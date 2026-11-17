# Agent fundamentals — Flashcards
Tags: #flashcards #ai-engineering #agents #llm
<!-- summary: workflow versus agent, ReAct and observations, execution state, model versus runtime responsibilities, success evidence, stop reasons, bounded retries and budgets, stagnation, cancellation, clarification and incomplete outcomes. -->


## The agent loop and ReAct

What is an LLM agent? <!--anki:502c4c3f7a7c7b624a33-->
?
An **LLM agent** uses a model to choose its next action from the current task and observations, within an execution loop controlled by software.

For an order inquiry, it might look up an order, inspect shipment tracking and then answer. The runtime checks each proposed operation, executes allowed tools and returns observations.

The distinguishing feature is adaptive control of the next step, not the number of tools. Available actions, permissions and budgets constrain that autonomy; the model cannot grant itself additional authority.

---

Do not confuse: workflow and agent? <!--anki:712b5a28436a7b683047-->
?
A **workflow** follows developer-defined control flow, which can include branches and LLM calls. An **agent** lets a model choose more of the next actions as observations arrive.

An invoice workflow can extract fields, apply eligibility rules and route exceptions without becoming an autonomous agent. An investigation agent may choose different searches for each case.

They can be combined: a fixed workflow delegates one bounded investigation to an agent, then validates its result. Choose the amount of autonomy needed by the task rather than treating these categories as competing products.

---

What is the ReAct pattern? <!--anki:4e773142733d352f7878-->
?
**ReAct** interleaves reasoning about the task, actions and observations. New evidence informs the next decision instead of following an unchanged plan.

```text
Need: establish an order's delivery status
Action: order_status(order_id="ORD-42")
Observation: shipped; tracking_id="TRK-8"
Next action: tracking_status(tracking_id="TRK-8")
Observation: delivered, with timestamp
Next decision: answer using the observed status
```

This is an illustrative decision trace. A statement that a lookup should succeed is not an observation: the runtime must obtain the actual result. ReAct does not itself implement tool execution, permissions or stopping rules.

---

What happens during one complete iteration of an agent loop? <!--anki:3638363533663564366338323430383561663530346534356563393030353331-->
?
The runtime builds context from the request and recorded state, asks the model for a decision, validates that decision, executes any admitted actions and records their observations.

```text
state → model decision → validation → execution → observation → updated state
```

The next iteration uses the updated state. If the decision proposes a final answer, the runtime checks the task's completion conditions instead of executing a tool.

Errors, requests for clarification and budget limits are explicit transitions too. A loop that handles only successful calls will behave unpredictably when the environment refuses or delays an action.

---

Do not confuse: ReAct and reasoning without external actions? <!--anki:3937383639363238356335653430633539666136323634333434613435323762-->
?
**ReAct** updates decisions using observations obtained through actions. Reasoning within a model call can organize a solution without interacting with the environment.

For a shipment question, internally guessing a delivery date cannot replace reading the tracking service. Conversely, an arithmetic question may need no external action at all.

The original ReAct work used interleaved textual reasoning traces. An application can record decisions, actions and evidence without requiring private internal reasoning to be exposed. A plausible rationale is not proof that a tool ran or that its result supports the answer.

---

Do not confuse: ReAct and reinforcement learning? <!--anki:6165653062653637613662623430623139383233356565653365616562396332-->
?
**ReAct is an inference-time interaction pattern**. **Reinforcement learning is a training approach** that changes a policy using rewards.

A pretrained model can follow a ReAct-style loop through prompting and tool orchestration without additional RL training. Conversely, an RL-trained model can answer a question in one response without invoking a tool.

The two can coexist: RL may train a policy on multi-step trajectories, and the deployed agent may alternate actions and observations. The presence of a loop does not establish how the model was trained.

---

What are the minimal components of an agent system? <!--anki:43784f552a2f34552f69-->
?
An agent needs a **decision policy**, an **action interface**, an **execution controller**, **task state** and **stopping conditions**.

The model proposes actions; tool contracts describe them; the controller validates and runs them; state records observations and progress; stop rules bound the task.

For a report-writing agent, state includes source references and the remaining questions, while completion requires a usable report with sufficient evidence. A short prototype can implement these roles, but production use also needs recovery from errors, cancellation and uncertain external effects.

---

What state should an agent retain between iterations? <!--anki:3631636435663266363333373438626539623833626238306535313036346635-->
?
Retain the **goal and acceptance criteria**, relevant observations with provenance, completed and pending operations, and the remaining budget.

For an export task, record the export operation ID and status separately from the model's claim that the file is ready. Store authoritative operation records outside a lossy conversation summary.

Context passed to the model is a selected view of this state, not necessarily the entire history. Summarization must preserve unresolved questions, failures and important constraints; otherwise the agent may repeat work or act as though a failed step succeeded.

---

When should you avoid building an autonomous agent? <!--anki:7330797b4f57247a213f-->
?
Prefer an explicit workflow when the necessary steps and branches are **known and stable**. Add adaptive decision-making only where it improves measured outcomes.

For leave requests, a model can extract dates while code checks balances and routing rules. Exceptions can go to a person or a bounded investigation step.

Compare task success, latency, cost and recovery behavior against this baseline. A variable input format alone does not require an autonomous loop, and adding tools does not automatically make the system more useful.

---

## Success, limits and stopping decisions

How should an agent decide when to stop? <!--anki:653272545f6866677138-->
?
Define **success evidence and non-success exit conditions before execution**. The model may propose that it is finished, but the runtime applies the stopping policy.

Successful completion requires the requested outcome to be verified. Other exits include missing information or authorization, unrecoverable failure, exhausted budget, cancellation and lack of useful progress.

For a CSV export, a tool acknowledgment is insufficient: check the completed operation, file and required schema. When stopping without success, preserve progress and explain what is missing. Reaching a turn limit is a reason to stop, not a reason to report completion.

---

Why is a model response without tool calls not sufficient proof of task completion? <!--anki:3835303365393663613136323462373838613133383239666662623435316664-->
?
It indicates that the model **did not request another tool in that response**. It may be answering, asking a question, refusing or failing to continue correctly.

The runtime must also inspect the protocol status: token truncation or an incomplete response is different from a normal turn ending. Then compare the proposed answer with the task's acceptance criteria.

For a pure explanation, a suitable final response may satisfy the task. For creating an invoice, verify the business record. Never infer an external effect solely from text saying that it happened.

---

Which outcomes should an agent runtime distinguish when execution stops? <!--anki:3661386632343134643634363431643061396264653532396133656138633966-->
?
Use explicit outcomes rather than a single `done` flag. One possible application vocabulary is:

- **Succeeded**: acceptance criteria are verified.
- **Waiting**: a particular input, authorization or external event is needed.
- **Failed**: no admissible recovery remains for an execution error.
- **Limited**: the task exhausted its budget or made no useful progress.
- **Cancelled**: execution was interrupted by the user or controlling system.

These labels are illustrative, not a universal API standard. Waiting may be resumable. Record partial results and uncertain external effects separately from the lifecycle outcome.

---

What evidence should an agent require before announcing business-task completion? <!--anki:6236373266383337663938303463393462303462663030323039656461663066-->
?
Define an **observable acceptance condition in the authoritative system**: the requested document exists with the right content, the payment has the required status, or the relevant tests pass.

Associate evidence with the specific object, operation ID and version. An accepted asynchronous request means work has started; it does not establish completion.

Verification should match the user's scope. “Order cancelled” does not satisfy “cancel the order and send a confirmation” unless both outcomes are checked. Record unresolved effects as unknown instead of silently converting them into success or failure.

---

Where should an agent enforce step, time and cost limits? <!--anki:6431613437326136633837643464643261303863623430313436643538636138-->
?
Enforce them **in runtime code**, before admitting new work and while monitoring in-flight operations. Prompt instructions alone cannot impose a reliable resource ceiling.

Define what a step counts: a model turn, tool call, retry or delegated run. Multiple parallel tools can consume one model turn but several operations and substantial cost.

Share a total budget across nested loops and reserve capacity for verification and reporting. Timeouts and cancellation requests do not guarantee that a remote write stopped; preserve its operation ID and reconcile the outcome.

---

How can an agent detect lack of progress without blocking legitimate repeated observations? <!--anki:3931646531333235363433313430373261656334656261316133313634336165-->
?
Compare **task-relevant state changes**, not just repeated text. Track unresolved requirements, new evidence and operation status across a bounded window.

Repeated identical searches yielding the same evidence may justify stopping or changing strategy. Polling the same asynchronous operation can be legitimate if the contract permits it, with backoff and a deadline.

A new query string is not automatically progress, and a repeated tool name is not automatically a loop. Use task-specific progress signals and explicit retry budgets; report the unresolved requirement when the policy stops further attempts.

---

Calculation: an agent has 40 seconds left and reserves 8 seconds for verification and reporting. Each new round has a worst-case duration of 12 seconds. How many rounds may it admit? <!--anki:6461333537323536393466343439383939333830303639343465373039393966-->
?
The available exploration time is **40 − 8 = 32 seconds**:

```text
maximum new rounds = floor(32 / 12) = 2
```

Three rounds could require 36 seconds and leave too little time for the reserved work. This assumes the 12-second bound includes the model call, tools, retries and scheduling overhead.

Recheck remaining time before each round and honor any tighter cost or call limit. Average latency is not a worst-case bound, and the reporting reserve must not be consumed by unbounded retries.

---

What is human-in-the-loop in an agent system? <!--anki:6e254c244e5b5d6d4e5d-->
?
It means placing human input at **specific decision points**:

- **Clarification** supplies missing information, such as which account to modify.
- **Approval** authorizes a concrete action when the task or application policy requires it.
- **Review** assesses outcomes, possibly after execution.

These are different contracts. A clarification answer is not automatically approval for a payment. An approval should identify the actual action and parameters; changed parameters may require revalidation.

Pause the relevant work while required input is pending. Use existing authorization where it applies instead of asking again at every harmless step.

---

What should an agent do when cancellation arrives during a tool operation? <!--anki:3132663037393564623566323464636239323362616466363363363636613734-->
?
Stop admitting new work, request cancellation of in-flight operations where supported, and preserve their identifiers and known effects.

Cancellation of the agent loop **does not imply rollback** of a remote action. A refund may have completed just before the cancellation request. Reconcile its state and report confirmed, pending or unknown effects.

Any compensation is a separate authorized action, not an automatic consequence of stopping. A resumed run should use the saved operation state rather than blindly replaying the last write.

---

Why must an agent sometimes observe the environment again before acting? <!--anki:3965376432336139613537373436316138636330643939343863623164313430-->
?
Its recorded state may be **stale or incomplete**. Another transaction can consume stock or change an invoice after the agent reads it.

Refresh important observations and enforce business preconditions atomically when applying a change. If an update expects version 7 but finds version 8, return a conflict and reconsider the action using the current record.

Correct reasoning from an old observation does not guarantee a valid action now. Re-observation should resolve a specific uncertainty; repeating reads indefinitely without a decision is not a recovery strategy.

---

## Reliability and evaluation

What are the main failure modes of an agent loop? <!--anki:6c23424a5e3f5e732375-->
?
Common failures include **repeating actions without progress**, drifting from the task, producing unintended effects, exhausting resources and declaring unsupported success.

Match controls to the failure: progress checks and budgets bound repetition; explicit task state limits drift; server-side checks control effects; operation records support verification.

For example, a support agent may repeatedly close an unresolved ticket because the reward or prompt treats closure as success. Evaluate actual resolution and allowed actions. Adding a larger turn budget or a more confident final response does not fix a faulty completion criterion.

---

What token-cost multipliers have been reported for research agents, and why are they not universal estimates? <!--anki:743745713e294b57476e-->
?
Anthropic reported approximately **4 times the tokens for agents** and **15 times for multi-agent systems**, compared with chats, in its research-system data. These are workload-specific observations, not universal bill multipliers.

Estimate actual costs from model calls, input and output tokens, caching, tools and retries. Different models and token types have different prices; latency is a separate measure.

Compare **cost per task meeting its acceptance criteria**, accounting for failed and unresolved runs. Spending less per run by stopping prematurely can increase cost per successful task.

---

Why evaluate an agent trajectory as well as its final response? <!--anki:3962636638383665376237303433306439633864616433656136373234383330-->
?
A correct final answer can conceal **unauthorized actions, excessive spending or unverified intermediate effects**. Check executed calls and state transitions, not just the wording of the response.

Evaluate permissions, budgets, recovery, stopping reasons and the evidence supporting completion. Allow multiple valid action sequences unless a particular order is required by the task.

An agent that correctly reports missing access can satisfy its behavioral contract even when it cannot complete the business objective. Record those two outcomes separately instead of rewarding a system that bypasses the restriction.

---

## Scenarios

Scenario: leave requests follow fixed rules, but the business asks for an autonomous agent. What do you propose? <!--anki:6f2d7b747a3e764a7673-->
?
1. **Map the process** and identify whether any step requires adaptive investigation.
2. **Use a workflow baseline** for extraction, balance checks and routing.
3. **Define completion** as a correctly recorded decision with required notifications.
4. **Handle exceptions explicitly**, using clarification or a bounded investigation when useful.
5. **Compare outcomes**, including errors, processing cost and time to resolution.

**Trap**: adding autonomy before demonstrating a benefit over the known process.

---

Scenario: an analysis agent takes 40 steps and still produces no useful answer. How do you revise its stopping policy? <!--anki:42587c246536282e3159-->
?
1. **Define success evidence** and the specific questions the analysis must resolve.
2. **Set runtime budgets** for turns, tools, time and cost, including verification reserves.
3. **Inspect progress**, looking for repeated evidence, unchanged blockers and looping retries.
4. **Permit a bounded strategy change** only when it addresses an identified cause.
5. **Stop with an honest partial result** or a concrete clarification request when progress remains impossible.

**Trap**: raising the step limit without diagnosing why additional work does not help.

---

Scenario: an agent requests a report export, receives status pending and says the report is ready. What is wrong? <!--anki:6366616666633663653836353438653938383763323965306162326666663433-->
?
1. **Separate acceptance from completion**: the export request was accepted, but the report is not verified.
2. **Keep the operation ID** and use its documented status interface.
3. **Poll within a deadline**, with backoff; do not create a new export on every attempt.
4. **Verify the finished artifact** against the requested format and scope.
5. **Return pending or unknown status** if the deadline expires before confirmation.

**Trap**: treating a successful HTTP request as proof of a completed business operation.

---

Scenario: the model gives a final answer, but one of three required facts lacks evidence. Should the runtime accept it? <!--anki:3163353661636135653737363430373362626230303864333364323937643235-->
?
1. **Check the completion contract**: identify the missing fact and whether it is necessary.
2. **Inspect existing evidence** before spending another call.
3. **Continue only if an allowed action can close the gap** within the remaining budget.
4. **Ask for specific missing input or report a partial result** if the gap cannot be resolved.
5. **Record the actual outcome** instead of marking an unsupported answer as successful.

**Trap**: forcing repeated “try harder” prompts without new evidence or a reachable stopping condition.

---

## Sources

Review of 17 November 2026: agent-loop concepts, ReAct, completion evidence and runtime stopping policies. State labels, budgets and traces are illustrative application contracts.

- [Yao et al. — ReAct](https://arxiv.org/abs/2210.03629).
- [Anthropic — token consumption observed in its research system](https://www.anthropic.com/research/multi-agent-research-system).
- [Anthropic — Building effective agents](https://www.anthropic.com/research/building-effective-agents).
- [Claude documentation — protocol stop reasons](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons). A protocol stop reason is distinct from an application's business outcome.
- [Claude documentation — handling tool calls and results](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls).

## Connections
- [[32-tool-calling|Tool calling]] — the hands of the agent
- [[34-harness-plugins|Harness]] — Execution Framework
- [[35-context-engineering|Context engineering]] — Working Memory
- [[36-agent-orchestration|Orchestration multi-agents]] — Scale
- [[41-code-nocode-automation|Automation]] — workflow vs agent
- [[96-evals-rag-agents|Agent evaluation]] — trajectory, final state and repeated-run reliability
- [[141-system-design-llm|System Design LLM]] — workflow or agent
- [[165-computer-use-browser-agents|Computer use & browser agents]] — when the tool is a GUI
- [[48-agentic-workflow-patterns|Workflow patterns]] — routing, planning and bounded revision
- [[22-advanced-rag|RAG — Advanced]] — hybrid search, reranking and filters
- [[37-agent-frameworks|Agent frameworks]] — implementation options
- [[44-langgraph-fundamentals|LangGraph]] — state graphs for agents and workflows
- [[47-crewai-flows|CrewAI — Flows]] — event-driven workflows
- [[144-ai-ux-human-in-the-loop|Human-in-the-loop UX]] — clarification, approval and review
- [[82-routing-llm|LLM routing]] — model choices and shared attempt budgets
- [[00-moc-ai-engineering|MOC AI Engineering]]
