# Workshop: a support agent with approval and recovery

This workshop connects a LangChain tool, a simulated LangChain model, a persistent LangGraph graph, Langfuse instrumentation, and a FastAPI application to see the effects of an interruption, denial, and outage after a business transaction. All demo commands use synthetic data; no paid models or remote Langfuse services are called.

The associated path is described in the [agentic application audit](../../docs/reports/agentic-stack-audit-2026-10-09.md). The **18 tests** of the [workshop](test_workshop.py) are part of the workshop: read their invariants, predict the result, and then run them.

## Installation

Python 3.10 or newer. The workshop is tested on Linux. From this run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-lock.txt
python demo.py
python -m unittest -v test_workshop
```

The initial download of the packages requires the Internet. The demonstration and the tests then work locally. The [File of direct dependencies](requirements.txt) explains the bricks retained; the [Locked File](requirements-lock.txt) contains the 61 versions used during the validation. The dependencies of this workshop are independent of those of the Anki export.

`demo.py` builds three independent temporary environments: approval, refusal and failure injected after effect. It checks a credit, zero credit and a single credit respectively after recovery. Its output explicitly indicates `real_model_quality: not_evaluated`.

## Path of execution

```text
API: demonstration identity + submission key
    ↓
File registry in business.sqlite
    ↓
LangGraph : propose
    ├── LangChain tool: order lookup with injected tenant
    ├── exact recovery of a versioned synthetic policy
    └── Simulated Model → Pydantic validation + business controls
    ↓
LangGraph : approve → interrupt → checkpoint SQLite
    ↓ decision related to the proposal footprint
LangGraph : execute
    └── business transaction: preconditions + refund + deduplication
    ↓
result checkpoint and public statement completed
```

The order version, expiration and policy version are set by the server. A proposal does not change during approval. The business service rechecks the decision, balance and version before creating the credit.

Two files materialize two transactional borders: `business.sqlite` carries the files, decisions, assets and events; `checkpoints.sqlite` carries the LangGraph state. They are not validated atomically together. The key to the effect is the stable identifier of the file, and the business service records effect and deduplication in the same transaction. This contract allows to replay after a failure between the two bases.

## Handling the API

Run a single process, on the local interface:

```bash
uvicorn api:create_app --factory --host 127.0.0.1 --port 8000 --workers 1
```

Open `http://127.0.0.1:8000/docs` to explore the contract. Two fictitious identities exist: header `Authorization: Bearer alice-demo` or `Authorization: Bearer bob-demo`. They are public and serve only to demonstrate isolation; do not expose this application on the Internet.

Create a run:

```bash
curl -sS http://127.0.0.1:8000/runs \
  -H 'Authorization: Bearer alice-demo' \
  -H 'Idempotency-Key: example-1' \
  -H 'Content-Type: application/json' \
  -d '{"order_id":"order-1","amount_cents":2000}'
```

The response contains `id`, `status: waiting`, `proposal` and `proposal_hash`. Copy the values into the following command; the hash binds the decision to the specified proposal:

```bash
curl -sS http://127.0.0.1:8000/runs/RUN_ID/decision \
  -H 'Authorization: Bearer alice-demo' \
  -H 'Content-Type: application/json' \
  -d '{"proposal_hash":"PROPOSAL_HASH","approved":true}'
```

Also try `approved: false` on another run. A registered refusal is terminal. The repetition of the same decision is without additional effect; a contradictory decision is refused. The same submission key finds the same run for the same tenant and the same content; a different content returns HTTP 409.

| Operation | Route | What it demonstrates |
|---|---|---|
| Inspect | `GET /runs/{id}` | Ownership of the file and public projection of the state |
| Decide | `POST /runs/{id}/decision` | Persistence decision related to the footprint |
| Reuse | `POST /runs/{id}/retry` | Resume of the same thread, without new submission |
| Cancel | `POST /runs/{id}/cancel` | Cancellation before decision; refusal if effect is ambiguous or already executed |
| Read the events | `GET /runs/{id}/events` | Finished SSE replay, filtered by run |

To reread only the events following the number 3:

```bash
curl -N http://127.0.0.1:8000/runs/RUN_ID/events \
  -H 'Authorization: Bearer alice-demo' \
  -H 'Last-Event-ID: 3'
```

The log is persistent and the SSE response closes after the available events. It is not a live subscription or tokens streaming. The numbers are global at the base: holes between two events in the same run are normal. Disconnecting from this channel does not restart or cancel the run.

The default directory is `.lab-data`, ignored by Git. Set `AGENTIC_LAB_DIR` to use another location. Stop the server before changing data environment. Commands are recreated only if they do not already exist: a restart does not reset balances.

## Observe the traces

The real Langfuse SDK exports to `InMemorySpanExporter`, provided by OpenTelemetry. The observations are named `support-run`, `read-order`, `retrieve-policy`, `propose-refund` and `commit-refund`. The dedicated test checks their parent-child relationships. Each recovery produces a new trace related to the same `run_id`.

These observations are not sent to a Langfuse project. They disappear with the process; the business event log remains in SQLite. No token or fictitious cost is presented as an actual model measure. The SDK uses explicit dummy identifiers and LangSmith is disabled in the context of the graph execution.

For an integration exercise on an authorized Langfuse instance, replace the local exporter with the configuration of that instance, keep the synthetic data, and verify ingestion, masking, prompts, costs, and scores.

## Experiments to be carried out

1. **Persistence**: Submit a run, stop the server pending approval, restart it with the same files and then decide. It must keep the same proposal.
2. **Fault window**: read `test_process_exit_after_effect_is_recovered`. The child process stops with `os._exit(73)` after the business COMMIT, before the next checkpoint. The recovery must return a single credit.
3. **Business concurrency**: Prepare two runs on the same command, approve the first, then the second. The command version of the second is out of date: it must be blocked. The business version test reproduces this control.
4. **Observability**: Remove an observation or alter its parent in a working copy and see the regression of the trace test.
5. **Isolation**: Try the consultation and decision routes with the identity of the other client; no data from the file should be returned.

## Variant CrewAI to build

The form [CrewAI — Reliable Execution](../../40-automation/40-012-crewai-reliable-execution.md) describes the expected contract. This variant is a guided exercise, it is not implemented in the workshop:

- A Flow carries the run and calls a crew only to produce the proposal; a task defines its output schema and dependencies.
- A guardrail checks the proposal without making the refund. Corrections and delegations have a limited budget.
- The human decision remains associated with the exact content; execution calls the same `Store.refund` business service, with a stable operation identity.
- Explicitly choose state rehydration or checkpointing according to the chosen CrewAI version, and then rerun the rejection, failure and isolation scenarios.

Compare the guarantees observed and the maintenance cost of the two versions. No advantage of quality or performance of a framework is deduced from this simulated workshop.

## Limits to be addressed before a real application

The API runs the small local workflow synchronously until the break; it does not announce a distributed workers queue. A process lock serializes all commands and voluntarily limits concurrency. Concurrency tests demonstrate this perimeter only. Demo tokens do not handle expiration, roles, or revocation.

The scenario does not validate an actual LLM provider, vector search, remote Langfuse instance, PostgreSQL, network outage, or production authentication. The model is controlled and the retrieval consists of a synthetic policy selected directly, so the technical tests do not measure the quality of a standalone agent.

To industrialize: real authentication, revalued permissions, durable queues and workers, distributed admission, checkpoint/event retention, management of expired cursors, migrations, cancellation in effect and persistent observability. Define these guarantees before replacing local components: changing SQLite to PostgreSQL does not provide them automatically.

[All workshops](../README.md)
