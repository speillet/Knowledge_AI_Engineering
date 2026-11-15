# Agents — Contracts, Faults & Repeats Testing — Flashcards
Tags: #flashcards #ai-engineering #agents #production
Verified on: 9 October 2026 — API cited against official documentation; limits spelled out in maps.
<!-- summary: pyramid of tests, simulated models, business invariants, fault windows, double orders, concurrency, migrations, traces, evaluations and release qualification, fault injection after business effect, property test, status readout failure. -->


How to distribute the tests of an agentic application? <!--anki:3039663565653632366637393463383639616232376264373038636630623864-->
?
Test **isolated services and tools**, orchestration with controlled model, then integrations and quality with the real models. Each level answers a different question.

A business test checks permissions and calculations; a graph test checks transitions and resumes; an evaluation measures success on representative requests. Example: The `examples/agentic-support` workshop runs 18 tests without a API key, then explicitly declares the quality of the real `not_evaluated` model.

---

Do not confuse: simulated model and model actually evaluated? <!--anki:6333313165376134663731323430366639383963666132346563633333643665-->
?
A simulated **model** returns controlled responses to cause a specific path. It checks the code that processes these responses, without proving that a real model would be able to produce them.

Use invalid responses, multiple tool calls, and denials to test the orchestration. Example: A LangChain `GenericFakeChatModel` returns `{"amount_cents": -1}`; the test verifies that validation stops this amount before any approval. Measure quality separately with an actual vendor and a frozen case set. A API workshop without a key can demonstrate recovery and isolation, not language performance.

---

Which invariants to check after an agentic execution with business effect? <!--anki:3365396438386664653865613434336662393664613465353366633136633130-->
?
Check **the status of the system concerned**: authorized operation, good target, good amount and no duplicates. The agent's messages do not constitute proof of execution.

For example, after a restart, `SELECT count(*) FROM refunds` must be 1 for this folder, and the balance of the command will drop by the only approved amount. Also test the negative invariant: no effect before approval or after refusal. Set the expected proof before writing the scenarios to avoid assertions that repeat only the code.

---

Where to inject outages to test an agent's recovery? <!--anki:6239323236346462363766303439636262373332343361653835623831633433-->
?
At **validation borders**: before the effect, after its acceptance but before receiving the response, then after the response but before the checkpoint. Add the restart during a human wait.

For a refund, each window has its expected result: failure before the call, zero have; after acceptance but before the answer, an unknown state to reconcile; after the answer but before the checkpoint, a have that the resume must not duplicate. Counting the effects persisted with the same operation identity. A test that only crashes before any external call does not cover the most dangerous window.

---

Why close and then reopen the storage in a LangGraph recovery test? <!--anki:3032386561303835356234353435333938393030303139626134386465626130-->
?
To verify that the recovery depends on the **Persisted data**, and not objects that have been left in memory. Rebuilding graph, connections before continuing the same thread.

An even stronger test initiates a new process. In the support workshop, a child process leaves with the code 73 just after the business COMMIT; the test rebuilds the engine from the SQLite files and requires a single credit. Document what the test demonstrates: reopening SQLite does not validate a PostgreSQL network failure.

---

How to test the authentication and isolation of an agent run? <!--anki:3164303962656361306130663465313762613036393930393963613032393630-->
?
Create two identities and attempt **read, resume, approve, cancel, and access artifacts** from the other's folder. Check for refusal and no leak: With Bob's token, `GET /runs/{id}` on an Alice's folder returns the same 404 response as a non-existent identifier.

Add a case where a right is revoked between creation and approval. Also test tools directly: the API must not be the only place of control if the engine has another path. Use only test data and identities.

---

How do I test two competing approvals for the same agent action? <!--anki:3736633738653664386331653438356161623564653863346136303033623862-->
?
Leave the requests together with a **synchronization barrier**, then observe answers and final business effect. Repeat with two identical decisions and two contradictory decisions.
```python
barrier = threading.Barrier(2)
def approve():
    barrier.wait(timeout=5)          # The two threads go together.
    return engine.decide("alice", run_id, digest, True)
```
The application must apply its explicit rule: a single accepted transition, or safe reuse of the already set result. Check the absence of duplicates in the business register. A sequential double-click test does not cover the race between reading the status and writing the decision.

---

How to test an approval that has become obsolete? <!--anki:3537653732653766363161353462663462316431633632343737383939373631-->
?
Create a proposal, keep its reference, then modify a **business precondition** or submit a new proposal before submitting the old decision.

The execution must refuse the action that has become incompatible or request a new validation, according to the rule defined. Example: the decision bears the imprint of the proposal calculated on the 3 version of the command; if the command changes to 4 before execution, no credit must be written. Test also expiration and change of rights. A simple "yes/no" test does not validate that the approval is for the correct version.

---

How to test the cancellation without hiding an external effect already achieved? <!--anki:6135323765636262353536383462636138636563386239626163646439316633-->
?
Inject the cancellation request **before**, **during** and **after** the effect. Check what the customer learns and whether reconciliation or compensation is required.

An engine can interrupt future steps without cancelling an accepted payment. Example: Cancellation arrives 200 ms after the provider has accepted the refund; the final status must indicate "reimbursement, cancellation too late", not "cancelled". In testing, use a simulated service that distinguishes reception, validation and response in order to expose the time travel.

---

How to test a consumer of agentic events? <!--anki:3335363230613162623535373465616639356336323735326436326166646337-->
?
Provide him with events **duplicated, delayed, interrupted and resumed** according to the contract of transport. Check that its display converges to the current public snapshot.

Example: The consumer receives 41, 42, 42, 44 and then 43 events, ignores the duplicate, fills the hole before displaying 44 or reloads the snapshot, and never sends a second email. Testing an expired cursor and an unknown event pattern after deployment. The order guarantees must be those of the system being used, not an implicit assumption.

---

Why keep historical checkpoints as migration fixtures? <!--anki:3838363065336566346163643435643361643663323865643337383238373139-->
?
They represent the **states actually taken back** after an update: missing fields, old node name, pending proposal, and partial errors.

Example: a checkpoint in v1, pending approval, does not contain the `policy_version` field added in v2. Repeated by the candidate, it must obtain an explicit value or a clear refusal, not a `KeyError` in production. Clean sensitive data and also test the planned rollback. A fix made only according to the new scheme can precisely hide the incompatibility that one seeks to detect.

---

How to automatically check the traces of an agent workshop without remote service? <!--anki:3430393663363633303339633434613461376435393833343935343432306638-->
?
Plug a local **exporter into memory** on the SDK or test collector, and then check names, parents, attributes, and absence of synthetic secrets.
```python
spans = exporter.get_finished_spans()     # InMemorySpanExporter from OpenTelemetry
roots = {s.context.span_id for s in spans if s.name == "support-run"}
commits = [s for s in spans if s.name == "commit-refund"]
assert roots and commits
assert all(s.parent is not None and s.parent.span_id in roots for s in commits)
```
This validates the exported instrumentation and payloads. This does not validate the authentication, ingestion, or display of a remote instance. Add a separate integration test to the target environment when it is available, with an allowed dataset and a defined retention.

---

How to organize an agent evaluation that changes its environment? <!--anki:6233313030633133643334643464666338643638623132306166366336396364-->
?
Reset an independent **fix per try**: database, files, memory, and tools. Check the final result from a source independent of the agent statements.

Otherwise, the 2 test finds the command already refunded by the 1 test and responds "already processed": an apparent success for the wrong reason. Copying a reference base to a temporary directory before each test avoids this bias. Also keep scenarios explicitly dedicated to multi-turn continuity. A realistic but uncontrolled environment makes comparisons difficult to interpret.

---

Calculation: 60 files are each evaluated 4 times for two agent versions. Each trial costs fictitiously 0.03 €, excluding judge. How many trials and what minimum budget to plan? <!--anki:3431366134363630623562353439363661383231373633316432643330333363-->
?
**60 × 4 × 2 = 480 trials**, i.e. **480 × 0.03 = 14.40 €**. Add separately the cost of judges, environment and additional attempts.

Repeats inform variability, but do not create 480 independent folders. To compare versions, keep the results grouped by folder and use an analysis adapted to this dependency. Provide a budget cap and a policy for interrupted trials.

---

How can a fault injection test verify the true idempotency of an agent? <!--anki:6433373732643039336232633436346562316133313332623731636161396437-->
?
Place a **checked out immediately after the business effect**, before its acquittal or checkpoint, and then resume the same operation with the same logical identity.

Check the end state in the target system: a single effect, recoverable result and consistent status. Repeat before the effect and after the acknowledgement to cover the borders. Also test two concurrent times. Counting only the tool calls is not enough: several calls can correctly find the same effect, while a single call can produce several if the downstream service is poorly designed.

---

Why test the invariants of an agent on several orders of events? <!--anki:3231613933653839656164333433333339366334303961646134303865333565-->
?
The reprises, duplicates and human responses can happen **in different orders of the nominal demonstration**. A single suite of clicks does not cover these combinations.

Generate bounded sequences and check the invariants after each transition: no payment without valid approval, no double effect, consistent terminal state. Keep a minimum sequence for each failure. The test must observe the business service, not just the internal state of the graph.

---

How do I test an agent when the action succeeds but its status reading fails? <!--anki:3533663932393364653236323466346462313265363435653465366631663739-->
?
Voluntarily create **an external success followed by unavailability of tracking**. The agent must maintain the indeterminate status and identifier of the operation, without finding a certain failure.

Restoring tracking and verifying reconciliation without further non-idempotent action. This scenario distinguishes between transport failure tolerance and business reliability. A simple exception simulation before the effect does not cover this window.

---

## Scenarios

Scenario: all tests of an agent pass with a simulated model, but the real model calls the wrong tool. What level of testing is missing? <!--anki:6333663431633539646266663462666338313739643237643138626238343339-->
?
1. Keep controlled tests that prove the correct processing of requests.
2. Add tool selection assessments with the real model on representative tasks.
3. Measure arguments, permissions, end result and costs, with multiple trials if necessary.
4. Turn observed errors into new regression cases.

**Trap**: Replace all local tests with expensive model calls, without isolating the cause.

---

Scenario: the resumption of an agent goes to test, but a stop of the worker produces duplicates in production. How do you strengthen the proof? <!--anki:3534396162363766366566633464313339646666343936653631336266346432-->
?
1. Check where the test injects the failure relative to the effect and checkpoint.
2. Cause a stop after business validation, before saving the result.
3. Rebuild the engine from storage and then resume the same operation.
4. Control the business register independently of the text rendered by the agent.

**Trap**: only check that the graph ends up returning `success`.

Destroy the worker instance, then rebuild it as in production, with the same storage and operation key. A test that keeps the variables in memory can hide precisely the window where duplicates are born.

---

Scenario: a new agent version improves the average quality but fails the "no effect before approval" test. Can it be promoted? <!--anki:6165633863326538636231313465336539633436316263376365613762663839-->
?
1. **Block promotion**: “No effect before approval” is a critical invariant, not a compensable component of the average.
2. **Confirm the effect actually observed** with the business register or a duplicate tool recording operations; do not rely on the text of the agent.
3. **Localize the wrong path**: tool, middleware, recovery, delegation or concurrency.
4. **Correct at the point of execution**, then test rejection, no approval, expiration and modified proposal; check zero effect in each prohibited case.
5. **Replay controls and evals** on the corrected version, as the fix can change quality, cost, and time.

**Trap**: Raise the overall quality score to hide an authorization regression.

---

## Sources
- [LangGraph — tests nodes and graphs](https://docs.langchain.com/oss/python/langgraph/test)
- [LangChain — test strategy](https://docs.langchain.com/oss/python/langchain/test)
- [Anthropic — agent reviews](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [LangGraph — interruptions and recovery](https://docs.langchain.com/oss/python/langgraph/interrupts)

## Connections
- [[96-evals-rag-agents|RAG Assessments & Agents]] — measure business results
- [[94-evals-methodology|Evaluation methodology]] — games and success criteria
- [[40-010-langchain-tools-middleware-production|LangChain — Production]] — test tools and contracts
- [[40-011-langgraph-recovery-concurrency|LangGraph — Recovery]] — inject failures
- [[40-012-crewai-reliable-execution|CrewAI — Production]] — test jobs and resumes
- [[140-011-agentic-application-architecture|Agentic Architecture]] — validate the life cycle
- [[00-moc-ai-engineering|MOC AI Engineering]]
