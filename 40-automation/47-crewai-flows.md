# CrewAI — Flows — Flashcards
Tags: #flashcards #ai-engineering #agents #crewai #workflow #llm
Verified on: 25 September 2026 — This factsheet lists products, versions or regulatory texts that are evolving quickly.
<!-- summary: `@start`, `@listen`, `@router`, structured state, `@persist`, `@human_feedback`, memory, CLI, crew or flow, Flows or LangGraph, confidentiality of persistent states, state of branches, authorized transitions. -->


What is a Flow CrewAI? <!--anki:48705b4d433b4b7c7339-->
?
An event **workflow** written in Python: decorated methods that trigger one after the other, with a **shared state**. A Flow can call code, a simple LLM call, an agent, or an entire **crew**.

For example, a Flow validates a ticket, calls a crew for analysis and then passes the result to a deterministic control. The methods describe the route; the state transports the necessary data between steps. The presence of a shared state is not enough to guarantee recovery after failure or absence of runs between branches: these properties must be checked.

---

Why does CrewAI recommend Flows for production? <!--anki:493f4033257a2c434034-->
?
Because they give a **Deterministic Control** the process (steps, conditions, state) while maintaining the autonomy of the [[46-crewai-crews|crews]] Where it is useful — the " Principle " [[41-code-nocode-automation|workflow]] First, “Agent when necessary.”

Events and conditions make the execution paths visible, but the output of a crew remains probabilistic. Putting a validation between this output and a business action, for example before saving a command. Also provide recovery, idempotency and supervision: an explicit step graph is not enough to guarantee reliability.

---

Which decorators structure a Flow CrewAI? <!--anki:7a2571382c507c776739-->
?
- **`@start()`**: entry point (several possible, launched in parallel)
- **`@listen(methode)`**: Runs when `methode` terminates, and receives its output
- **`@router(methode)`**: returns a **label** that chooses the next branch
- **`or_()` / `and_()`**: listen to the end of **one** or **all** methods

Dependencies describe **when** a method becomes eligible, while state and outputs carry the data. With multiple branches, specify which ones can change the same field and how their results are joined. Also test a branch that fails or does not run, in order to understand the behavior of the expected junction.

---

How to write a Flow CrewAI that routes a ticket to a processing branch? <!--anki:6543357a5b677a2565-->
?
```python
from crewai.flow.flow import Flow, listen, router, start
from pydantic import BaseModel

class TicketState(BaseModel):
    message: str = ""
    category: str = ""

class SupportFlow(Flow[TicketState]):
    @start()
    def classer(self):
        self.state.category = classifier(self.state.message)

    @router(classer)
    def aiguiller(self):
        return "technical" if self.state.category == "bug" else "commercial"

    @listen("technique")
    def traiter_bug(self):
        return crew_support.kickoff(inputs={"message": self.state.message})

SupportFlow().kickoff(inputs={"message": "L'export PDF plante"})
```

`@start` starts the classification; `@router` issues a label; `@listen` executes the corresponding processing. `classifier` and `crew_support` are dependencies to be defined. This extract illustrates only the technical branch: adding a commercial listener and a management of unknown categories to cover all the paths of a real service.

To make the diagnosis reproducible, keep the resulting category and ticket ID in the status. Check each route with a simulated classifier before measuring the classification errors of a real model.

---

In a Flow CrewAI, structured or unstructured state? <!--anki:7a3c687e3b4823246c6c-->
?
- **Unstructured**: `self.state` is a fast — free dict to prototype
- **Structured**: a **Pydantic** model (`Flow[MonEtat]`) — typed and validated, recommended in production
In both cases, the state receives a unique **`id`**.

With a typed state, a category or amount has a contract that can be read by the following steps. However, the structure validation does not prove either business accuracy or authorization; some constraints require explicit validators. Also predict the evolution of the schema if persistent states must be reread after a deployment.

---

How to make a Flow repeatable after a stop? <!--anki:747a77217a394a3b7c6c-->
?
The decorator **`@persist`** saves the status of the Flow at the configured points, with SQLite by default. Reusing its identity allows to find this status; a fork can rehydrate a snapshot under a new identity.

Distinguish between **restore variables and restart execution**: check which methods are restarted. Checkpointing recent versions adds mechanisms of restart execution, with a separate contract. In any case, validate existence and owner of the folder, durability of the storage and idempotency of the effects. Test a stop between the business action and its backup.

---

How to integrate human validation into a Flow CrewAI? <!--anki:736663553e494c2a4138-->
?
With the decorator **`@human_feedback`** (CrewAI 1.8+): the Flow **pauses** to ask the opinion of a human, and the answer can **route** to different branches (approved, to be corrected...).

Present the result to be validated, the consequences and the options for refusal or correction. The mechanism of waiting and resumption depends on the integration used; check its persistence on restart. An approval must concern the effective action and arguments, without implicitly authorizing all the following actions.

If the amount goes from 30 to 300 euros after presentation, invalidate the previous agreement. Link the decision to a proposal version and the validator identity.

---

How does a Flow CrewAI use memory? <!--anki:4836683e74747c21725f-->
?
Unified memory exposes `self.remember(...)`, `self.recall(...)` and `self.extract_memories(...)` to record, retrieve and extract reusable information.

Example: "send invoices in French" can become a confirmed preference; "the customer tool has expired" is an incident, not proof that the customer does not exist. An automatic extraction produces **candidates to remember**, not certified facts.

Set user scope, provenance, date, retention, and deletion. Check for recall contradictions. This knowledge memory does not replace the transactional status of the Flow: remembering that an invoice was considered does not prove that it was issued.

---

How do I create and launch a Flow CrewAI project? <!--anki:6a725b613d5b23617567-->
?
```bash
crewai create flow mon_flow
cd mon_flow
crewai install
crewai run
```
The generated project contains the Flow and a `crews/` folder for the crews it orchestrates.

The generator provides a project structure, not a completed business workflow. Configure models and their identifiers, implement steps, and then test branches and errors before launching. Pin dependencies and keep secrets out of the repository to make the installation reproducible and shareable.

A first test can replace external tools with deterministic doubles. Check for success, refusal, and error before paying for actual calls; project startup does not validate its decisions.

---

Crew or Flow: when to use what? <!--anki:44575b3c377b7a313348-->
?
- **Crew**: a task **open** where several roles must collaborate independently (research, writing)
- **Flow**: a **business process** with steps, conditions, and a — state that calls for crews for open games

To process a claim, the Flow can impose identification, rights control and approval; a crew analyzes the parts and proposes a response. The result of this open part becomes an entry to validate before the business action. This composition locates the autonomy and facilitates the explanation of a failure from the step concerned.

---

Flows CrewAI or LangGraph? <!--anki:632943237e5a313c346d-->
?
Both orchestrate stateful steps. **Flows**: decorated, highly readable Python methods integrated into crews. **[[45-langgraph-production|LangGraph]]**: lower-level explicit graph, with a richer ecosystem of checkpointers, time travel and deployment tools.

Compare above all a real recovery case: interruption before writing, failure after writing and restart with the same state. Then examine the management of competing branches and the ease of inspection. The declaration style is not enough to decide; the necessary guarantees depend on the versions, storage and architecture around the framework.

---

Why does a Flow CrewAI need to be tested for persistence with sensitive data? <!--anki:3236656464376563623865393464396339303537643166643337313638303638-->
?
A **Persistent state** can keep entries, Outputs and intermediate data beyond the request. Storing this state without a dedicated policy extends the exposure of sensitive information.

Identify the fields that are really necessary for recovery, prefer protected references to raw secrets and control access, retention and deletion. Test that another tenant can not restore a state by his identifier alone. Check also backups and logs. The functional recovery of a Flow and the confidentiality of its storage are two guarantees to be validated separately.

---

Why should a Flow CrewAI distinguish an ignored branch from a failed branch? <!--anki:6535356363313562323563393438313862343635633535386261613934326638-->
?
These states have different **consequences for the sequence**: an unrequired branch may be normal, while a failed branch may render the publication invalid.

Explicitly represent the result, error, and reason for absence in the business state. Test the router conditions and expected completion before merging. An empty field does not tell if a task has not started, found nothing, or experienced a failure.

---

How to prevent an impossible business transition in a Flow CrewAI? <!--anki:3166326335366265373766373464376238356638316531346361643639663936-->
?
Set **authorized states and transitions**, then verify the transition before transfer. A refund must not go from "proposed" to "paid" without the expected validations.

The router chooses a branch, but the business service must also apply the invariants. Test invalid states injected during a recovery and events received in disorder. A typed schema checks the shape of the state; it does not prove the legality of its evolution.

---

## Scenarios

Scenario: you need to automate the processing of complaints: classify, investigate, propose a commercial gesture, then validate beyond 100 €. How do you structure the Flow? <!--anki:717a535a5a6058473b4e-->
?
1. **`@start`**: Receipt and classification of the claim, with a **Pydantic status** typed
2. **`@router`**: Switch according to category, simple cases passing through code without LLM
3. **Crew** for the open party only: the investigation, which intersects customer history and incidents
4. **`@human_feedback`** beyond the threshold, with routing as per decision (approved, to be corrected)
5. **`@persist`** to resume after a cut or long wait

**Trap**: entrusting the entire process to a stand-alone crew, while three out of four steps are deterministic.

---

Scenario: your Flow has been running for a month, but after each redeployment the current files start from scratch. What do you check? <!--anki:786e644b48736e4d7739-->
?
1. **`@persist`**: Without it, the state does not survive the process
2. **Status ID**: resume with the same `id` folder, not create a new one
3. **Storage**: Is the default SQLite suitable for production, or do you need shared storage between replicas?
4. **Idempotence**: steps already executed (e-mail, commercial gesture) must not be replayed
5. **Observability**: know at any time how many files are pending and at what stage ([[93-monitoring-inference|monitoring]])

**Trap**: Test the recovery only locally, where the status file still exists.

---

## Sources

- [CrewAI — flows](https://docs.crewai.com/en/concepts/flows)

- [CrewAI — Flows, documentation v1.15.23](https://docs.crewai.com/v1.15.23/en/concepts/flows)

- [CrewAI — checkpointing, documentation 1.15.26](https://docs.crewai.com/v1.15.26/en/concepts/checkpointing)

- 14 November 2026 — Flow Status and Routing: [CrewAI — Flows, v1.15.41](https://docs.crewai.com/v1.15.41/en/concepts/flows).

## Connections
- [[46-crewai-crews|CrewAI — Crews]] — teams of agents orchestrated by the Flow
- [[41-code-nocode-automation|Automation]] — workflow vs agent
- [[44-langgraph-fundamentals|LangGraph]] — the graph-based alternative
- [[36-agent-orchestration|Orchestration multi-agents]] — composition patterns
- [[31-agent-fundamentals|Agents]] — human-in-the-loop
- [[40-012-crewai-reliable-execution|CrewAI — Reliable Execution & Integration]] — recovery and application integration
- [[00-moc-ai-engineering|MOC AI Engineering]]
