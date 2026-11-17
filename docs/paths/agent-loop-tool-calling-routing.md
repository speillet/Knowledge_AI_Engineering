# Agent loops, tool calling and routing

Use this path to explain how an agent chooses work, obtains observations and decides whether it has actually finished. The example and state labels below are illustrative application contracts, not a framework API.

## Read in this order

1. [Agent fundamentals](../../30-agents/31-agent-fundamentals.md) — the loop, ReAct, state and stopping decisions.
2. [Tool calling](../../30-agents/32-tool-calling.md) — contracts, dispatch, results and recovery.
3. [Workflow patterns](../../40-automation/48-agentic-workflow-patterns.md) — branches, handoffs, planning and revision loops.
4. [LLM routing](../../80-api-layer-routing/82-routing-llm.md) — eligible models, cascades, fallback and shared budgets.

After each topic, explain one successful trace and one trace that stops without completing its business goal. Use the [learning guide](../guides/learning-with-flashcards.md) to assess the explanation.

## Separate the decisions

| Decision | Question it answers | Example | What it does not establish |
| --- | --- | --- | --- |
| Workflow routing | Which processing branch owns this request? | Send an invoice export request to billing. | That the request is already resolved. |
| Model routing | Which eligible backend should perform this model call? | Choose a model compatible with the tool and data contract. | Permission to execute a proposed action. |
| Tool selection | Which operation is useful now? | Select `list_unpaid_invoices`. | That the operation ran. |
| Tool dispatch | Which implementation runs the validated request? | Resolve an allowed name through a runtime registry. | That the returned data are complete or sufficient. |
| Stopping decision | Has the task succeeded, or why must execution stop? | Accept a verified export or report a pending operation at the deadline. | That every stopped run succeeded. |

### ReAct connects decisions to observations

ReAct interleaves reasoning about the task, actions and observations. The next decision uses the actual observation rather than assuming the expected result occurred. The model proposes; the runtime checks and executes; the environment supplies the outcome.

This does not require RL training. It also does not require an application to display private internal reasoning. For review, record the task state, decision, executed action, observation and supporting evidence. An invented tool result is not an observation.

### Plans and branches can contain a loop

A workflow may first choose billing, then run a bounded agent inside that branch. A plan may establish milestones, while a ReAct-style loop decides which lookup to perform next. These patterns can coexist.

The parent task owns its overall acceptance criteria and budget. A specialist finishing one subtask, or handing the conversation to another specialist, does not automatically finish the original request.

## Follow one complete task

The user asks: **“Export all unpaid invoices for customer C42 to a CSV and tell me where the file is.”** The customer is within the authenticated user's permitted scope.

Before executing, define completion: the selected customer and unpaid filter are correct; the source result is complete; export processing has completed; the CSV is readable with the required columns and expected records; and the returned file reference is accessible to the user. Zero invoices is a valid result only if the complete filtered query confirms zero.

### Successful trace

| Step | Decision or operation | Actual observation | Consequence |
| --- | --- | --- | --- |
| 1 | Route to billing; choose an eligible model. | The branch has the necessary read and export capabilities. | Continue with the same task identity and budget. |
| 2 | Request `list_unpaid_invoices(customer_id="C42")`. | Two invoices, source snapshot `s17`, `complete=true`. | Record the two invoice IDs and the snapshot. |
| 3 | Request an export of those records from `s17`. | `status=pending`, `operation_id=op-42`. | Save the operation ID; the file is not yet verified. |
| 4 | Check `export_status(operation_id="op-42")` within the polling policy. | `status=completed`, file reference `file-9`. | Inspect the finished artifact. |
| 5 | Validate `file-9`. | Required columns, two matching invoice records, readable file and valid user access. | Acceptance criteria are satisfied. |
| 6 | Return the file reference and a concise description. | The task record contains supporting evidence. | Mark the task as succeeded. |

The fictional export service supports a source snapshot and explicit invoice IDs. If the real service does not, define how consistency is established instead of assuming two independent reads refer to the same data. Correlate each tool result with its call ID; persist any business idempotency key separately.

### Change one observation and the correct next action changes

| Changed observation | Appropriate response |
| --- | --- |
| The invoice result includes a continuation cursor. | Use a complete filtered query or continue pagination within budget. Do not infer that the first page contains all unpaid invoices. |
| Customer identity is ambiguous. | Resolve it from trusted context or ask a targeted clarification question before exporting. |
| The export request times out. | Treat execution as unknown; reconcile its status before resubmitting. A new model or a new call ID does not prevent duplicate exports. |
| Export remains pending at the deadline. | Stop active polling, preserve `op-42` and report the pending state. Do not claim the file is ready. |
| The user cancels after export submission. | Stop new work and request cancellation where supported. Record whether the export already completed or remains unresolved. |
| The model says “done” before artifact verification. | Check the missing acceptance condition. Continue only if an admissible action and budget remain; otherwise return the actual incomplete outcome. |

## Make stopping conditions explicit

### Completion and other exits

| Outcome | Evidence or trigger | What to preserve and report |
| --- | --- | --- |
| Succeeded | Every required acceptance condition is verified. | The result and its evidence references. |
| Waiting | Specific input, authorization or external event is needed. | The exact dependency and resumable state. |
| Failed | An execution error has no admissible recovery. | The failure, completed effects and relevant diagnostics. |
| Limited | Time, cost, calls, revisions or useful-progress allowance is exhausted. | The best usable partial result and unmet requirements. |
| Cancelled | The user or controlling system stops execution. | Known effects and any pending or unknown external operations. |

These outcomes describe application state. A provider's `end_turn`, token-limit or tool-use signal describes a model response. Interpret the protocol first, then apply the business contract. State names can differ; the distinctions must remain clear.

### Enforce budgets outside the prompt

The runtime checks cancellation, permissions, deadlines and admission limits before new work. It also monitors in-flight calls. Counters cover retries, verification, parallel tools and handoffs under the same task; changing models or branches does not reset them.

Reserve time for verification and a final report. With 40 seconds left, an 8-second reserve and 12 seconds per bounded round, at most two further rounds fit. This calculation requires a worst-case bound that includes scheduling, calls and retries; average latency is insufficient.

Stopping the controller is not a rollback mechanism. A remote operation can complete after a local timeout or cancellation. Record unresolved effects and reconcile them under the application's recovery policy.

### Define useful progress

Use progress toward the required outcome: a missing fact found, a previously invalid argument resolved, an operation moving to a new state, or a required check passing. More text, another tool name or a higher uncalibrated confidence score is insufficient.

Repeated polling can be legitimate when an operation is still progressing, with backoff and a deadline. Repeating identical searches with unchanged evidence needs a bounded strategy change or an explicit stop. A stagnation stop still does not establish success.

## Practice the distinctions

For each case, identify the decision owner, the next allowed action and the stopping outcome:

| Case | Expected reasoning |
| --- | --- |
| A correct tracking answer is followed by endless tracking calls. | Inspect required-tool settings and the completion path, then enforce repetition and budget limits. |
| A router is 95% accurate but mishandles every mixed billing-and-delivery request. | Evaluate multi-intent coverage and end-to-end completion; a single label may discard part of the task. |
| A high-scoring revision contains a prohibited claim. | It fails eligibility. Keep an eligible candidate and continue only within the revision policy. |
| A fallback model is available but lacks the required tool protocol. | Exclude it; use another eligible route or return an unavailable/incomplete outcome. |
| A branch completes cancellation but notification fails. | Preserve the cancellation effect and report partial completion; do not replay cancellation merely to retry notification. |

For implementation exercises, continue with the [support-agent workshop](../../examples/agentic-support/README.md) and [agent testing and recovery](../../90-observability-evals/90-013-agent-testing-recovery.md). This path provides contracts and worked reasoning; it is not a deployable runtime.

Definitions and primary sources are recorded in the four linked topics. The [dated review](../reports/agent-loop-tool-calling-routing-2026-11-17.md) describes the changes and validation.

[All learning paths](README.md)
