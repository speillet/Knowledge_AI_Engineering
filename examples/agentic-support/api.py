"""API locale de démonstration : uvicorn api:create_app --factory --workers 1."""
from contextlib import asynccontextmanager
import os
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, ConfigDict, Field

from engine import Engine, Request
from storage import Conflict


class Decision(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    proposal_hash: str = Field(min_length=64, max_length=64)
    approved: bool


def identity(authorization: str = Header(default="")):
    # Comptes pédagogiques publics, PAS un mécanisme d'authentification de production.
    identities = {"Bearer alice-demo": "alice", "Bearer bob-demo": "bob"}
    if authorization not in identities:
        raise HTTPException(401, "Utiliser une identité de démonstration")
    return identities[authorization]


def create_app(directory=None):
    engine = Engine(directory or Path(os.environ.get("AGENTIC_LAB_DIR", ".lab-data")))

    @asynccontextmanager
    async def lifespan(app):
        yield
        engine.close()

    app = FastAPI(title="Atelier support agentique local", lifespan=lifespan)
    app.state.engine = engine

    @app.exception_handler(Conflict)
    async def conflict_handler(request, exc):
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(KeyError)
    async def missing_handler(request, exc):
        return JSONResponse(status_code=404, content={"detail": "Dossier introuvable"})

    @app.exception_handler(ValueError)
    async def value_handler(request, exc):
        return JSONResponse(status_code=422, content={"detail": "Entrée ou état incompatible"})

    @app.post("/runs")
    def submit(request: Request, tenant=Depends(identity), idempotency_key: str = Header(min_length=1, max_length=128)):
        run_id = engine.create(tenant, idempotency_key, request.model_dump())
        # Le modèle local est immédiat. En production : worker durable pour tâches longues.
        return engine.drive(tenant, run_id)

    @app.get("/runs/{run_id}")
    def inspect_run(run_id: str, tenant=Depends(identity)):
        return engine.view(tenant, run_id)

    @app.post("/runs/{run_id}/decision")
    def decide(run_id: str, decision: Decision, tenant=Depends(identity)):
        return engine.decide(tenant, run_id, decision.proposal_hash, decision.approved)

    @app.post("/runs/{run_id}/retry")
    def retry(run_id: str, tenant=Depends(identity)):
        # Réconciliation manuelle d'un échec ou d'un processus disparu.
        return engine.drive(tenant, run_id)

    @app.post("/runs/{run_id}/cancel")
    def cancel(run_id: str, tenant=Depends(identity)):
        return engine.cancel(tenant, run_id)

    @app.get("/runs/{run_id}/events")
    def events(run_id: str, tenant=Depends(identity), last_event_id: str = Header(default="0")):
        try:
            after = int(last_event_id)
            if after < 0:
                raise ValueError()
        except ValueError:
            raise HTTPException(400, "Curseur entier positif ou nul attendu")
        with engine.lock:
            rows = engine.store.events(run_id, tenant, after)
        # Rejeu fini du journal, PAS un abonnement temps réel ni un flux de tokens.
        frames = [f'id: {row["seq"]}\nevent: {row["kind"]}\ndata: {row["payload"]}\n\n' for row in rows]
        return StreamingResponse(iter(frames), media_type="text/event-stream",
                                 headers={"Cache-Control": "no-cache"})

    return app
