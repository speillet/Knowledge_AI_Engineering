# CrewAI — Reliable Execution & Integration — Flashcards
Tags: #flashcards #ai-engineering #agents #production
Verified on: 9 October 2026 — API cited against official documentation; limits spelled out in maps.
<!-- summary: Task contracts, dependencies, bounded guardrails, budgets, async, persistence and checkpointing, delegation, isolation, instrumentation and testing, external effects after rejection of a guardrail, publication of results, isolation of files. -->


How do I split a CrewAI into verifiable tasks? <!--anki:3437303864316466363737393435623261313739336130656362623036353132-->
?
Give each task a **Identifiable Entry**, an expected result and a verifiable criterion. Separate collection of evidence, Proposition and validation helps to locate errors.

A breakdown into "researcher", "expert" and "director" is not enough if their responsibilities overlap. For a support file, ask the first agent for facts and a proposal in accordance with the policy to the second. Keep the execution of the commercial gesture in a controlled service.

---

How to explain dependencies between CrewAI tasks? <!--anki:6335633433623237333763653430313638363963656261363466393763616337-->
?
Use the task's **`context`** to select the necessary upstream outputs. Do not implicitly depend on the entire history or assume that two asynchronous tasks finish in the declaration order.

Draw the dependency graph and identify independent steps. A synthesis must wait for all required scans, or explicitly announce missing scans. Test a slow, failed, or ignored upstream task to verify actual behavior.

Example: `context=[analyse_financiere, analyse_legal]` makes these two expected outputs explicit. A task simply declared before synthesis is not proof that its data is available or valid.

---

Do not confuse: raw output, structured output and business proof in CrewAI? <!--anki:3039373438323265646230353465353738326632396164386438663139366333-->
?
A **raw** output is text; a **structured** output respects a model when it is actually available; a **business proof** establishes that its content is correct in the context of the task.

After a task configured with `output_pydantic`, verify the presence of the structured object in `TaskOutput` and its invariants. A list of valid URLs does not prove that the pages support the assertions. Keep source identifiers and check for relevant passages.

---

How to write a CrewAI guardrail that helps to correct a proposal? <!--anki:6530613565396335386363653439613762653839306236383435316232303537-->
?
Produce an explicit verdict and an actionable **reason**. A functional guardrail receives the task output and returns a `(success, result_or_error)` pair.

For example, check that all the references cited belong to the sources provided. In case of failure, specify the unknown references without exposing sensitive data. The guardrail must remain without business effect: it can be called several times and must not send an email or create a credit.

---

Why limit guardrail corrections and CrewAI technical covers separately? <!--anki:6136323939653263376461623462306239323264636633393330613530396237-->
?
A **content correction** prompts the agent again; a **technical retry** restarts a failed call. They respond to different causes and can stack up.

Set up `guardrail_max_retries`, and then predict a terminal state when no acceptable output is obtained. Keep a shared budget with the provider's retrievings. Do not automatically relax a validator because the agent fails to satisfy it: a task can actually be impossible.

---

What does max_iter, max_rpm, and max_execution_time measure in CrewAI? <!--anki:6134373630306433333862313434663762663430323161623437316437353737-->
?
These parameters limit **iterations**, **call throughput**, and **runtime**, respectively, according to their scope in the framework, and none of them is a financial ceiling for an entire workflow.

An iteration can handle a lot of tokens; a manager and delegated agents can add their own calls. Measure actual costs and impose the overall budget at the application/gateway level. Test the exhaustion of each limit and the result returned to the client.

---

Do not confuse: asynchronous launch of a crew and durable execution? <!--anki:3539376536343138363931613438623039343262396235386637343732636236-->
?
A **asynchronous** launch releases the caller for other tasks. A **durable** run retains enough information to recover after the process disappears.

For long processing, save the request, set the recovery policy, and use storage that is accessible to the next worker. Check the API async of the installed version and the behaviors of the synchronous tools, which can continue despite caller cancellation.

---

How do I prevent a batch CrewAI execution from overpowering vendors? <!--anki:3637643838666537316462343432313262376436346332343461663437383630-->
?
Limit the **number of active folders**, in addition to the limits per agent. A batch of 100 folders each containing several agents can brutally multiply calls.

Enforce quotas and fairness between clients with a shared queue and budget. Measure wait, concurrent calls, and withdrawals. For independent folders, isolate status, memory, and results; failure of an item must have its own status rather than making the entire batch opaque.

---

Do not confuse: persist of a Flow CrewAI and checkpoint execution? <!--anki:6239373931636131373734353438393338376638613662626431306632366438-->
?
**`@persist`** saves the status of the Flow to the configured points. **checkpointing** of recent versions can save execution information to resume or fork crews, flows and agents.

Rehydrating a state does not prove that all steps already completed will be skipped. Choose a mechanism based on its granularity, storage, and version used; test the process death between an external action and its backup. Both require idempotent business effects.

---

Why verify the existence of a state before a Flow CrewAI restart? <!--anki:6637386362613135363432643466346138666635643738336336386262303663-->
?
A recovery must find **the expected folder**, not just accept an identifier. In the versioned documentation consulted, an untraceable restore can return without the expected state.

Example: If the R42 folder is missing, its initial values could trigger a new statement while the user requested to continue with the old one. The service must verify existence, owner, version and status; if the state is missing, report the failure and offer an explicit recovery.

Distinguish between recovery and fork to a new identity. Test unknown identifier, bad owner and old schema. A local file lost on redeployment does not constitute a durable registry of folders.

---

How to limit the risks of a CrewAI delegation? <!--anki:3530323039346339356331323432366638613439323839616465613064313132-->
?
Define a **Bounded Mission**, authorized tools, a return format and a budget for the delegated agent. The manager must be able to distinguish failure, lack of evidence and success.

Avoid circular delegations by limiting depth and repetitions. Verify that delegation does not confer more rights than the caller. Compare to the same workflow without delegation: a collaboration that adds cost and ambiguity without improving success must be simplified.

---

How do I isolate two clients that use the same CrewAI configuration? <!--anki:3061373565343965346532613435656461636233663537316365346533366631-->
?
Separate their **states, memories, access to artifact sources and destinations**. Mutable objects and caches reused between requests require special attention.

Inject identities from the authenticated service and check the rights in the tools. A remembered preference for one client should not be recalled to another. Test two intercalated folders, with the same question wording, and then check results, storage and traces.

For example, use `tenant/run_id/rapport.json`, with a holder from the authenticated identity. A single name per execution avoids overwriting; permissions are still required to prevent cross-reading.

---

What should be used in a CrewAI application beyond kickoff? <!--anki:3132326134333863653331663430353738633639643334616166373739323934-->
?
Connecting **Flow, crew, tasks, model calls, and tools** to an application execution. Saving replays, guardrail fixes, delegations, and business results helps locate costs and failures.

Event listeners and observability integrations are used for this instrumentation; check that they cover async paths and error branches. An end callback does not replace a durable business log. Do not count a call captured by both the framework and the gateway twice.

---

Calculation: A crew uses 3 agents; each makes exactly 4 calls to 0.01 € per call, and the manager adds 3 at the same rate. What is the cost of a run, then 500 runs without retry? <!--anki:3164616533336461353932623430303338356136373764653632666138353933-->
?
**(3 × 4 + 3) × 0.01 = 0.15 €** per execution, then **500 × 0.15 = 75 €**.

This calculation shows the cost of coordination: the manager here adds 0.03 €, or 25% of the cost of agents alone. Actual calls vary with tokens, memory, corrections and delays; measure these positions before generalizing.

---

Why shouldn't a CrewAI guardrail implicitly undo effects already produced by a task? <!--anki:6366333137643237366565623432636338653464373831373437326333333465-->
?
An output **guardrail** judges the result of a task. Its rejection may cause a new attempt, but does not automatically restore the external systems modified by the tools.

Have a proposal produced before the action, then validate and execute with an idempotency key. If the effect has already occurred, check its status and apply explicit business compensation if necessary. Test the rejection after an effect and limit attempts. A guardrail that restarts a billing task can otherwise create multiple invoices.

---

Why publish the results of a crew only after validation of the expected batch? <!--anki:3664336664313863623130613435613062646639623232626533346136336165-->
?
A consumer can see **a mixture of complete and partial outputs** if each task writes directly to the final location. A missing task can then pass as a negative conclusion.

Write the results in a prep space, check for presence, schemas and references, then publish a validated batch manifest. Predict the status of partial failures. This application convention does not automatically result from the fact that `kickoff` has ended.

---

Why give each CrewAI run a separate file space? <!--anki:3832363763323333323039373438626561643235303363646661663030643762-->
?
Generic names like `rapport.md` create **collisions between tasks or clients**. A task can read a result of a previous execution and present it as new.

Build paths from controlled identifiers, limit access and assign each artifact to its execution. Clean according to a retention policy. Test two simultaneous crews with different entries and check the contents, not just their return codes.

---

## Scenarios

Scenario: a Crew CrewAI cites pages that are accessible but do not support its conclusions. What control do you add? <!--anki:3764323465323664373863393434656439306430393163616162623163623465-->
?
1. Retain recovered evidence with relevant identifiers and passages.
2. Verify that the references produced correspond to this evidence.
3. Evaluate the support of each important statement by its quoted passage.
4. Block corrections and allow abstention in the absence of evidence.

**Trap**: Assimilate HTTP 200 to a truth check.

For a critical statement, compare to the original passage and its date of validity; a well-formatted reference or a second agreement agent does not constitute additional evidence.

---

Scenario: after a redeployment, a Flow CrewAI finds its variables but starts a billing step again. How do you diagnose the problem? <!--anki:3034633234356663346161353435373038616332643537383230346561396235-->
?
1. Identify the mechanism used: state rehydration or checkpoint execution.
2. Verify folder identity, progress markers, and shared storage.
3. Protect billing with a stable business identity and atomic deduplication.
4. Repeat a stop after billing but before persistence.

**Trap**: Considering that finding the amount in the report means that the invoice has been recorded in the execution graph.

---

Scenario: a hierarchical crew produces better reports but regularly exceeds the budget. How do you decide to keep it? <!--anki:3035633832313862663335323466313939303231616262313934313939613838-->
?
1. Compare the same files sequentially, with evaluator and fixed criteria.
2. Measure cost per pass, latency, and pass rate, not just the average score.
3. Assign the additional cost to the delegations, the manager and the corrections.
4. Reserve the hierarchical mode in cases where the gain justifies its cost, with limited stop.

**Trap**: Consider the manager as free because he does not produce the final document.

---

## Sources
- [CrewAI — tasks, documentation 1.15.26](https://docs.crewai.com/v1.15.26/en/concepts/tasks)
- [CrewAI — agents and limits](https://docs.crewai.com/v1.15.26/en/concepts/agents)
- [CrewAI — Flows and Restoration](https://docs.crewai.com/v1.15.26/en/concepts/flows)
- [CrewAI — checkpointing](https://docs.crewai.com/v1.15.26/en/concepts/checkpointing)
- [CrewAI — production architecture](https://docs.crewai.com/v1.15.26/en/concepts/production-architecture)

- [CrewAI — tasks and exit guards](https://docs.crewai.com/en/concepts/tasks) — targeted deepening of the 12 November 2026; educational examples are built for this review.

## Connections
- [[46-crewai-crews|CrewAI — Crews]] — contracts and task execution
- [[47-crewai-flows|CrewAI — Flows]] — recovery and application integration
- [[36-agent-orchestration|Orchestration multi-agents]] — dependencies and delegation
- [[98-agent-debugging|Debugging agents]] — attributing errors to steps
- [[140-011-agentic-application-architecture|— Architecture & Life Cycle]] — place crews in the service
- [[90-013-agent-testing-recovery|Agents — Contracts, failures & recoveries testing]] — test jobs and resumes
- [[00-moc-ai-engineering|MOC AI Engineering]]
