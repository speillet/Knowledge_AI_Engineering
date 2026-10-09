"""Vrai graphe LangGraph, modèle LangChain simulé et traces Langfuse locales."""
import json
import os
import sqlite3
import threading
import time
import uuid
from pathlib import Path
from typing_extensions import TypedDict

from langchain.tools import tool
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import HumanMessage
from langfuse import Langfuse
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt
from langsmith import tracing_context
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from pydantic import BaseModel, ConfigDict, Field

from storage import Conflict, Store, fingerprint


class Request(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    order_id: str = Field(min_length=1, max_length=80)
    amount_cents: int = Field(gt=0, le=10000)


class Proposal(Request):
    order_version: int = Field(ge=1)
    expires_at: float
    policy_version: str


class State(TypedDict, total=False):
    run_id: str
    tenant: str
    request: dict
    proposal: dict
    approved: bool
    status: str
    receipt: str


class Engine:
    def __init__(self, directory, fault=None):
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        self.store = Store(directory / "business.sqlite")
        self.checkpoints = sqlite3.connect(str(directory / "checkpoints.sqlite"), check_same_thread=False)
        # Tous les runs sont sérialisés : atelier UN processus, pas un verrou distribué.
        self.lock = threading.RLock()
        self.fault = fault  # injecté par les tests, jamais exposé dans l'API
        self.exporter = InMemorySpanExporter()
        # Export local uniquement. Aucune clé réelle, aucun envoi à Langfuse Cloud.
        self.telemetry = Langfuse(public_key="pk-lab-" + str(uuid.uuid4()), secret_key="sk-local-only",
                                 span_exporter=self.exporter, environment="local-lab")
        builder = StateGraph(State)
        builder.add_node("propose", self.propose)
        builder.add_node("approve", self.approve)
        builder.add_node("execute", self.execute)
        builder.add_edge(START, "propose")
        builder.add_edge("propose", "approve")
        builder.add_conditional_edges("approve", lambda s: "execute" if s["approved"] else END)
        builder.add_edge("execute", END)
        self.graph = builder.compile(checkpointer=SqliteSaver(self.checkpoints))

    def close(self):
        self.telemetry.flush()
        self.telemetry.shutdown()
        self.checkpoints.close()
        self.store.close()

    @staticmethod
    def config(run_id):
        return {"configurable": {"thread_id": run_id}}

    def propose(self, state):
        # Le tenant est injecté par le service, jamais par le schéma d'outil.
        @tool
        def read_order(order_id: str) -> dict:
            """Lire le solde et la version d'une commande du client authentifié."""
            return self.store.order(state["tenant"], order_id)

        with self.telemetry.start_as_current_observation(name="read-order", as_type="tool",
                                                        input={"order_id": state["request"]["order_id"]}) as span:
            order = read_order.invoke({"order_id": state["request"]["order_id"]})
            span.update(output=order)
        with self.telemetry.start_as_current_observation(name="retrieve-policy", as_type="retriever",
                                                        input={"policy_id": "support-v1"}) as span:
            # Retrieval exact sur une source synthétique versionnée, sans moteur vectoriel.
            policy = {"version": "support-v1", "text": "Toute création d'avoir exige une approbation humaine et un solde suffisant."}
            span.update(output=policy)
        # Réponse contrôlée : teste l'intégration, pas la qualité d'un fournisseur.
        model = GenericFakeChatModel(messages=iter([json.dumps(state["request"])]))
        prompt = policy["text"] + " Demande : " + json.dumps(state["request"])
        with self.telemetry.start_as_current_observation(name="propose-refund", as_type="generation",
                                                        input=[{"role": "user", "content": prompt}],
                                                        model="simulated-local", metadata={"simulated": True}) as span:
            response = model.invoke([HumanMessage(content=prompt)])
            span.update(output=response.content)
        draft = Request.model_validate_json(response.content).model_dump()
        # Version métier, expiration et politique sont fixées côté serveur.
        proposal = Proposal(**draft, order_version=order["version"],
                            expires_at=time.time() + 3600.0,
                            policy_version=policy["version"]).model_dump()
        # Validation indépendante de la réponse du modèle.
        if proposal["order_id"] != state["request"]["order_id"] or proposal["amount_cents"] != state["request"]["amount_cents"]:
            raise Conflict("Le modèle a changé la demande")
        if proposal["amount_cents"] > order["remaining"]:
            raise Conflict("Solde insuffisant")
        return {"proposal": proposal, "status": "waiting"}

    def approve(self, state):
        digest = fingerprint(state["proposal"])
        decision = interrupt({"proposal": state["proposal"], "proposal_hash": digest})
        if decision.get("proposal_hash") != digest or type(decision.get("approved")) is not bool:
            raise Conflict("Décision incompatible avec la proposition")
        return {"approved": decision["approved"], "status": "approved" if decision["approved"] else "rejected"}

    def execute(self, state):
        with self.telemetry.start_as_current_observation(name="commit-refund", as_type="tool",
                                                        input={"proposal_hash": fingerprint(state["proposal"])}) as span:
            receipt = self.store.refund(state["run_id"], state["tenant"], state["proposal"])
            span.update(output={"receipt": receipt})
        # La transaction métier est déjà validée ; le checkpoint suivant ne l'est pas.
        if self.fault == "exit_after_effect":
            os._exit(73)
        if self.fault == "raise_after_effect":
            self.fault = None
            raise RuntimeError("Panne injectée après effet, avant checkpoint")
        return {"receipt": receipt, "status": "completed"}

    def create(self, tenant, key, request):
        request = Request.model_validate(request).model_dump()
        if not 1 <= len(key) <= 128:
            raise ValueError("Clé de soumission invalide")
        with self.lock:
            return self.store.create(tenant, key, request)

    def view(self, tenant, run_id):
        with self.lock:
            row = self.store.owned(run_id, tenant)
            state = self.graph.get_state(self.config(run_id)).values
            result = {"id": run_id, "status": row["status"]}
            if "proposal" in state:
                result.update(proposal=state["proposal"], proposal_hash=fingerprint(state["proposal"]))
            if "receipt" in state:
                result["receipt"] = state["receipt"]
            return result

    def drive(self, tenant, run_id):
        with self.lock, tracing_context(enabled=False):
            row = self.store.owned(run_id, tenant)
            if row["status"] in ("completed", "rejected", "cancelled"):
                return self.view(tenant, run_id)
            snapshot = self.graph.get_state(self.config(run_id))
            if snapshot.interrupts:
                if row["decision"] is None:
                    self.store.status(run_id, "waiting")
                    return self.view(tenant, run_id)
                data = Command(resume={"approved": bool(row["decision"]), "proposal_hash": row["proposal_hash"]})
            elif snapshot.values:
                data = None
            else:
                data = {"run_id": run_id, "tenant": tenant, "request": json.loads(row["request"])}
            self.store.status(run_id, "running")
            try:
                with self.telemetry.start_as_current_observation(name="support-run", as_type="agent",
                                                                input=json.loads(row["request"]),
                                                                metadata={"run_id": run_id}) as span:
                    self.graph.invoke(data, self.config(run_id), durability="sync")
                    current = self.graph.get_state(self.config(run_id))
                    status = "waiting" if current.interrupts else current.values["status"]
                    span.update(output={"status": status, "receipt": current.values.get("receipt")})
                self.store.status(run_id, status)
            except Exception:
                # failed signifie traitement interrompu, pas preuve d'absence d'effet.
                self.store.status(run_id, "failed")
                raise
            finally:
                self.telemetry.flush()
            return self.view(tenant, run_id)

    def decide(self, tenant, run_id, digest, approved):
        if type(approved) is not bool:
            raise ValueError("Décision booléenne attendue")
        with self.lock:
            view = self.view(tenant, run_id)
            if digest != view.get("proposal_hash"):
                raise Conflict("Proposition obsolète ou inconnue")
            self.store.decide(run_id, tenant, digest, approved)
            return self.drive(tenant, run_id)

    def cancel(self, tenant, run_id):
        with self.lock:
            row = self.store.owned(run_id, tenant)
            if row["status"] == "cancelled":
                return self.view(tenant, run_id)
            # Une décision déjà persistée peut avoir été exécutée malgré un crash.
            if row["status"] not in ("queued", "waiting") or row["decision"] is not None:
                raise Conflict("Annulation sûre impossible dans cet état ; vérifier les effets")
            self.store.status(run_id, "cancelled")
            return self.view(tenant, run_id)
