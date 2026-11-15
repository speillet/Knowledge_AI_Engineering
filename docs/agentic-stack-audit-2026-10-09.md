# Deepening of the — 9 October 2026

The repository had 94 cards in seven cards dedicated to LangChain, LangGraph, CrewAI and Langfuse, with 15 put in situation. It also contained 130 cards in the Agents section, as well as cards on streaming, MCP/A2A/AG-UI, assessments, security, idempotency and operation. The main need was to deepen the assembly and use.

This enrichment adds **124 cards in seven new cards**, of which **21 put in a situation, 12 distinctions and 7 Calculations**. It corrects six existing answers by keeping their Anki questions and identifiers. The Vault Passes **137 cards and 2,010 Cards** To **144 cards and 2,134 Cards**, with **338 put in a situation, 174 distinctions and 96 Calculations**.

## Coverage and work order

| Theme | Sheet added | Cards | Proof of expected understanding |
|---|---|---:|---|
| Contrats LangChain | [Tools & middleware](../40-automation/40-010-langchain-tools-middleware-production.md) | 17 | Explain injected identity, exit contract, middleware order and retry budget |
| LangGraph State | [Recovery & competition](../40-automation/40-011-langgraph-recovery-concurrency.md) | 19 | Resume after failure without duplicating an effect; treat concurrency and old states |
| Execution CrewAI | [Reliable execution](../40-automation/40-012-crewai-reliable-execution.md) | 17 | Define dependencies, bounded guardrails, budgets and granularity of recovery |
| Traces Langfuse | [Instrumentation in production](../90-observability-evals/90-011-langfuse-instrumentation-production.md) | 18 | Find calls, tools, pick-ups and costs without lost parent or double counting |
| Experiences Langfuse | [Prompts, datasets & experiences](../90-observability-evals/90-012-langfuse-prompts-experiments.md) | 17 | Promote a version with a comparable game, interpretable scores and observable rollback |
| Full application | [Architecture & life cycle](../140-system-design-product/140-011-agentic-application-architecture.md) | 19 | Define API contracts, human decisions, rights, events and status transitions |
| Validation | [Tests of contracts, breakdowns & recoveries](../90-observability-evals/90-013-agent-testing-recovery.md) | 17 | Distinguishing technical tests, business invariants and quality evaluation of a real model |

After the basic topics, start with the application architecture, choose the right runtime as needed, then work instrumentation and tests together. LangChain and LangGraph can combine; CrewAI offers another organization of tasks; Langfuse observes and evaluates. Knowing the four does not require stacking them in each application.

## What has been deepened

**LangChain.** The new cards deal with adapter/business service separation, schemas useful to the model, `ToolRuntime`, `tool_calls`/`ToolMessage` consistency, structured output policies, business validation, repairable errors, async limits, middleware interactions, dynamic tools, fallbacks, and upgrades. The goal is to understand the real path of a call.

**LangGraph.** Coverage includes `sync`/`async`/`exit` modes, pending writes, transactional borders, multiple interruptions, error recovery, invocation concurrency, state merge, subgraphs, migrations, and diagnostic replays. Each warranty is tied to the backend and the perimeter that provides it.

**CrewAI.** Tasks are treated as verifiable contracts with explicit dependencies. Cards distinguish between correction by guardrail, technical retry, async and durability; they develop budgets, isolation, delegation and observability. Flow state restoration and execution checkpointing are distinguished. CrewAI references are pinned to the 1.15.26e documentation consulted.

**Langfuse.** Two topics complete the fundamentals: one on the quality of instrumentation, one on experience-based decisions. Topics include distributed spread, async traces, streamed generations, incomplete costs, sampling, masking, export and duplicates; then labels, versions, registry cache, fallback, regression sets, comparability, origin of scores, missing values and authenticated feedback.

**Architecture and testing.** The topics link framework, business service and interface: run status, durable admission, asset ownership, immutable proposal, expiration, rechecked preconditions, cancellation, event log, slow consumers and deployment compatibility. The tests check for invariants at fault windows and with historical states, beyond the simple `success` return of the engine.

## Corrections to existing topics

| Topic | Correction |
|---|---|
| [LangGraph — Fundamentals](../40-automation/44-langgraph-fundamentals.md) | Super-steps do not automatically make the state durable: checkpointer, mode and backend must be configured. |
| [LangGraph — Production](../40-automation/45-langgraph-production.md) | Isolating an effect in a task does not guarantee its unique execution; a crash after remote acceptance may lead to a request for it again. |
| [Langfuse — Fundamentals](../90-observability-evals/91-langfuse-observability.md) | The OpenTelemetry export must be configured; the traces of a gateway do not cover the entire workflow alone. |
| [CrewAI — Crews](../40-automation/46-crewai-crews.md) | An accessible URL does not prove that an assertion is supported by the source. Corrections are limited. |
| [CrewAI — Flows](../40-automation/47-crewai-flows.md) | Finding the persistent variables and taking back the execution control are two guarantees to check separately. |
| [Streaming applicatif](../80-api-layer-routing/84-streaming-application-integration.md) | The first content does not always arrive in a few hundred milliseconds; the cost also depends on the work consumed and the actual cancellation. |

The general dates of the old cards are not artificially renewed: this review targets these answers, it does not claim to revalidate all the API mentioned on all their cards.

## Executable workshop and complementary exercises

The [atelier support](../examples/agentic-support/README.md) provides a true LangGraph graph, LangChain components, Langfuse SDK with local exporter, and a API FastAPI. Its model is simulated; its data and business policy are synthetic. It does not require any remote model or service keys.

Three scenarios run with `demo.py`: approval, denial and failure after business effect. The tests also check for persistence after reconstruction, the death of a process between business COMMIT and checkpoint, client isolation, double submissions/decisions, obsolete preconditions, expiration and SSE events. The business registry and checkpoints are two separate bases for making the failure window visible.

Duplicate recovery is achieved by a stable identity and a business transaction containing the effect and its deduplication. This pedagogical choice does not automatically confer the same guarantee to a remote API.

| Exercice | Livrable | Criteria for success |
|---|---|---|
| Local takeover | Test results and explanation of the failure window | Only one to have despite a breakdown after its registration |
| Variante CrewAI | Flow/crew using the same business contract | Refusal, repetitions and isolation retain the same invariants; exercise to implement |
| Instance Langfuse | Complete trace, prompt versioned and score bound | Correct parenting, minimized data, no double counting; remote integration to be performed |
| True Model | Fixed dataset, outputs, metrics and error analysis | Business result, cost and latency measured on comparable tests; quality not assessed by simulated model |
| Distributed application | API admission, workers, recovery, migration and load scenario | Demonstrated guarantees between processes/replicas; beyond the local lock of the workshop |

The workshop does not implement production authentication, distributed file, frontend, or vector search. Its SSE is a finite replay of events, not a continuous subscription. The CrewAI variant is guided, not presented as executed. This distinction avoids confusing a verified educational example with a ready-to-deploy application.

## Method of learning

For each subject, respond to a mechanism map, then to a distinction and a situation. Write then a verifiable prediction: what state remains after crash, how many actions are created, what observations are expected? Run the test and explain a possible deviation.

A good, accurate senior response **that provides the guarantee, what it covers, and how it fails**. "The framework handles recovery" is insufficient without saying which writes are persisted, which code is replayed, and how an external effect is deduplicated. The topics are a reminder medium; the workshop and the exercises produce the evidence.

## Validation

- Format, reciprocal links, catalogs and playback compatible with Obsidian Spaced Repetition.
- Retention of 2,010 pre-existing questions and identifiers; no old renamed topics.
- Recalculation of the seven new numerical examples, with data and assumptions on the front.
- Vault testing and Anki export; package structure checks and uniqueness of identifiers.
- **40 vault tests** and **18 workshop tests** passed; three demonstration files validated. The seven calculation cards correspond to eleven recalculated numerical results.
- Workshop run under Python 3.10 with pinned dependencies, separate from system packets; dedicated CI added for workshop changes. A local success does not prejudge the state of remote CI runs.

The Langfuse instrumentation is validated with its SDK and an in-memory exporter; remote ingestion, real models, and a CrewAI implementation of the project are not validated by these local tests.
