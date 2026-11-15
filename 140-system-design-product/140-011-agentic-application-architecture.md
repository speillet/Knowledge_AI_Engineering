# Agentic applications — Architecture & lifecycle — Flashcards
Tags: #flashcards #ai-engineering #agents #production
Verified on: 9 October 2026 — API cited against official documentation; limits spelled out in maps.
<!-- summary: choice of bricks, execution contracts, API and workers, admission, identity, versioned approvals, cancellation, events, deployment and capacity, retrieval of a submission after network shutdown, task and session, resource cleaning. -->


How to choose the necessary bricks for an agentic application? <!--anki:6264333961356665313630323462663361383062303936656332656432666539-->
?
Starting from the **business process**: steps, tools, status, end criteria and operating constraints. LangChain provides abstractions and an agent loop; LangGraph allows to control a graph; CrewAI organizes tasks and roles; Langfuse observes and evaluates.

These roles do not make it mandatory to fully assemble them. Retaining components that resolve a verified need, with a clear boundary between them. Example: classifying 5,000 emails per day into eight categories requires a structured call and validation; a refund whose approval can wait two days justifies a persistent graph.

---

What is the contract between the API and an agent's engine? <!--anki:3861623432653065393030613435363161393439643862633131643463336433-->
?
A **business execution** contract: validated entry, authorized identity, status, result and structured error. Provide separate operations to submit, view, approve and cancel, as in the `examples/agentic-support` workshop:
```text
POST/runs submit, with Idempotency-Key
GET /runs/{id} view public health
POST /runs/{id}/decision approve or deny a specific proposal
POST /runs/{id}/cancel      demander l'annulation
GET /runs/{id}/events track public events
```
Keeping the internal classes of the framework behind an adapter makes it easier to test and migrate. The client should not have to understand all the fields in the graph or send an arbitrary `Command`. Version public events and visible states, because an interface can remain open during a deployment.

---

Why doesn't a 202 HTTP status prove that an agent will complete its task? <!--anki:3432643964376361316164653430386238323966323839376264353135303734-->
?
It means that the request has been **accepted for processing**, with no guaranteed end result. Before issuing it, make the request recoverable in a durable storage or clarify a lower guarantee.

Return an identifier and a tracking URL, for example `202 Accepted` with `Location: /runs/r-81f2` and a `{"id": "r-81f2", "status": "accepted"}` body. The contract must explain failure, expiration and cancellation. A client that receives 202 must still be able to view a state after restarting the server; a simple task in memory may disappear in the meantime.

---

Why does a FastAPI background task not replace a durable queue for an agent? <!--anki:6333353032356330366636623464326562356133633331623235376136376135-->
?
It can execute a work after the response in the **application process**, without providing alone durable storage, taken over by another worker and distributed coordination.

Example: `background_tasks.add_task(executer_agent, run_id)` runs in the responding pod; if a redeployment stops 30s later, the job disappears while the response is gone. To survive a crash, persist request and status, then organize consumption and resumes. The "background" character describes the time of execution, not a guarantee of delivery or persistence.

---

Which public states to expose to track an agent run? <!--anki:3836303230303530343036323433313738626533613866323630636164643265-->
?
Define a **Explicit State Machine** : accepted, In progress, waiting for approval, Then finished, failed or cancelled depending on the transitions allowed. Also keep the causes and possible possibility of recovery.

A technical failure can leave an external action in an unknown state; then expose a verification phase rather than announce a failure without effect. Distinguish between "received cancellation request" and "work actually stopped". Test Allowed and Prohibited Transitions: `waiting_approval → cancelled` is allowed, `completed → running` is not.

---

How do I treat a repeated submission with the same idempotency key? <!--anki:3466386264396533643734363439383662343236636236343335633839616635-->
?
Link the key to an authenticated **perimeter** and an input fingerprint. Same key and same content find the operation; same key and different content produce an explicit conflict. In the support workshop, return `Idempotency-Key: example-1` with `amount_cents` passed from 2000 to 2500 gives HTTP 409.

The key reservation must be atomic with the creation of the folder. Set retention time and behavior for an operation still in progress. This protection at the input is not enough for the tools: each business effect must also have a stable identity when restarting.

---

Why check the rights at each consultation and takeover of an agent? <!--anki:3562336635343335663739313437353939393666346533613336646231653566-->
?
A run or thread ID refers to a **resource**, not its owner. Verify rights to read, events, upload, approve, and cancel.

Rebuild identity from authentication; do not trust a tenant provided in the state by the client. Rights may change during a human wait: if Alice creates a folder and then leaves the finance team, her approval three days later must fail, even if she remains the owner of the folder.

---

What should be included in a proposed action submitted for human approval? <!--anki:3935333239373430343839623439373038336333663934343065363566373031-->
?
A **precise and versioned action**: type, target, effective arguments, consequences and expiration. Associate the decision with its identifier or imprint, the identity of the decision maker and time.
```json
{"action": "refund", "order": "C-881", "order_version": 7,
 "amount_cents": 4500, "expires_at": "2026-10-23T10:00:00Z"}
```
The decision bears the SHA-256 imprint of this canonical JSON.

If the amount or recipient changes, the previous approval should no longer apply. Display these items in the interface and check their server-side correspondence. The model can prepare the proposal; it should not be able to fabricate proof of its approval.

---

How do I prevent a valid approval from becoming unsafe while waiting? <!--anki:3431653135316132386233393437396439376364616535633434353639653938-->
?
Link the approval to an exact **proposal and versioned**, and then recheck rights, expiration, and preconditions at runtime.

Example: The validator approves the modification of a contract in version 7; in the meantime, an operator publishes version 8. The service running must refuse the writing conditioned to version 7 and request reconciliation or new approval.

A read "everything is still valid" followed by an unprotected write leaves a time-travel. Apply the control with the operation, by transaction, expected version or equivalent mechanism. Neither the checkpoint nor the past approval freeze the resource; do not silently reinterpret the agreement for a different proposal.

---

Do not confuse: disconnection from the interface and cancellation of the agentic run? <!--anki:3565643836393762386136363439626462306136303531333830313763366461-->
?
The **logout** stops a tracking channel; the **cancellation** requests that the work stop. A long task can continue when the browser closes, and then be viewed later.

Set this policy by task type: Closing the tab can be considered cancellation for a chat response, not for an audit of 20 minutes that the user will come to consult. A cancellation must be authenticated, persisted and propagated to components capable of applying it. If an external action has already been validated, announce its actual state and provide business compensation if necessary. Closing a stream does not go back time.

---

How to publish agent events without exposing its full internal state? <!--anki:3166333235316633336561343439303939623930623466353266663937363030-->
?
Turn internal updates into **filtered public events**: step, progress, approval request, result, or allowable error. Define a schema and verify rights before issue.

The report may contain secrets, internal instructions, or the results of tools belonging to another perimeter, so a simple serialization of `state` is a bad interface contract; instead, publish `{"id": 42, "type": "approval_requested", "amount_cents": 4500}`. Do not display internal reasonings as proof of truth; favor actions performed and useful sources.

---

What to do when the resume cursor of an agent stream has expired? <!--anki:6665663637613136623531653438633239386364343436623866353039343263-->
?
Detecting that old events are not **more available**, then propose a current public snapshot and a new recovery point. Do not invent missing events or automatically restart the work.

Example: The client reconnects with `Last-Event-ID: 1200`, but the log keeps only one hour of events; the server sends a `snapshot` event with the current public state, and then resumes at the 1,857 event. Document event log retention separately from that of results and checkpoints. Test reconnection after expiration, duplicates, and events arriving during snapshot recovery.

---

How to manage a slow client that consumes the events of an agent? <!--anki:3931363834636564346563383437326339303533666135626233383565393332-->
?
Block **buffers per connection** and choose a policy: aggregate the progress, cut the channel with possibility of recovery, or slow down the producer when it is acceptable. Example: beyond 256 pending events, merge text fragments; after 30 s of full queue, close the connection with a recovery cursor.

A slow client should not exhaust worker memory or block all other folders. Keep essential business events in an appropriate journal; intermediate text fragments may have a different policy. Measure buffer size, consumer delay, and reconnections.

---

How do I deploy a new version of an agent when runs are active? <!--anki:6637623834303762656266353438323162316432633161323937363139663965-->
?
Maintain **code, state, and contract compatibility** for running runs. Depending on the system, drain older workers, route resumes to their version, or explicitly migrate states.

Example: Each run carries `workflow_version=1`, and a worker v1 remains active until the 37 v1 folders awaiting approval are completed. A container rollback is not enough if the storage has already been transformed inconsistently. Trace the version of the workflow and keep the artifacts needed to diagnose rework.

---

Calculation: an application receives on average 2 new agent files per second; each file waits for 10 min an approval, with a stable regime. How many files wait on average? <!--anki:3134653638656362386132353463366339663161336135613561643033373162-->
?
By Little's law, **2 × 600 = 1,200 files** wait on average. The stability hypothesis means in particular that approvals follow this throughput over time.

This does not mean that it takes 1,200 LLM calls or active HTTP connections: a durable pause must free up unnecessary compute resources. If decisions arrive less quickly than folders, the queue grows.

---

How to choose a success indicator for an agentic application? <!--anki:3530663737643839636232373437323561626434303939636262366435663638-->
?
Measure the **verified business result**, with cost and time on the same perimeter. For a support agent: properly resolved file, without prohibited action, within the expected time.

A technically completed run may have returned an unusable response; a justified escalation may instead be the expected result. Set categories, denominators, and segments before launch. Link traces and business states to explain failures without confusing HTTP success with user success.

---

Why does the customer need to be able to track down an agent run after losing the response to their submission? <!--anki:3563613333373337636438313465376662346365616233363435316561363536-->
?
A **network shutdown** can occur after the run has been permanently created but before the client receives his/her ID. The client does not know if his/her request has been accepted.

Provide a stable submission key and a consultation or resubmission mechanism that finds the same run. Verify identity, content footprint, and public status before restarting. Test out the outage right after registration. Creating a new run at each timeout can double the effects and invoice, even if each worker is working properly.

---

Do not confuse: user session and business task of an agent application? <!--anki:3565643339653865386561663462343638663532373031363039396164633831-->
?
A session contains **interactions**, while a task has a verifiable goal, state, and end. The same session can contain multiple tasks, and a task can survive its disconnection.

Use separate identifiers and link approvals, budget and effects to the right task. Closing the tab should not implicitly mean success or cancellation. Define the expected behavior for background jobs.

---

Why set a temporary file life cycle for an agent? <!--anki:6366346264363263336165323431393539326531373634326564346364633434-->
?
Sandboxes and artifacts can **survive execution**, consume resources, and keep data private, but deleting them too early can prevent a recovery.

Assign ownership, status, and expiration to resources, and then clean up according to the actual end of tasks. Plan for abandoned tasks and worker failures. Test that an expired resource produces an explicit error, without accidental reuse by another task.

---

## Scenarios

Scenario: a user approves a refund of 20 €, but the model then changes the proposal to 80 €. What control should prevent execution? <!--anki:3731316438363064336638353463663839366236373134356265633036303964-->
?
1. Make the approved proposal immutable and identifiable by version or imprint.
2. Verify that the action to be performed corresponds exactly to this proposal.
3. Refuse the obsolete decision and request a new validation if the content changes.
4. Re-check business requirements at the time of writing.

**Trap**: store only `approved=True` in a freely modifiable state.

Also test a change in the recipient, currency and identity of the applicant. The agreement references the significant parameters and expires according to a defined rule; an unchanged amount is not enough to prove equivalence.

---

Scenario: API returns 202, then the server restarts and the folder disappears. How do you make the actual acceptance guarantee? <!--anki:3062336239386663313035623463643338353637616334373362363466323865-->
?
1. Persist the file and its key of idempotency before the accused of acceptance.
2. Make its processing recoverable, for example with an outbox or a worker that reads pending files.
3. Explain a searchable status and a recovery policy.
4. Test the crash before and after each storage validation.

**Trap**: Add only an asynchronous task to the process that has just been answered.

---

Scenario: after an SSE reconnection, the customer receives the "proposal ready" event again. How do you avoid a second refund? <!--anki:6530336362643662643162393431343361663536656531386338636139636531-->
?
1. Treat the event as display information, never as an order to execute.
2. Deduplicate the display by event ID.
3. Require an authenticated approval command related to the proposal.
4. Also deduplicate the business operation, regardless of SSE transport.

**Trap**: Trigger an irreversible effect each time a progress event is received.

Test a cut after the effect, before the acknowledgment: the restarted run must find the existing refund. The business server keeps the operation key with its result; only deduplicating the display does not protect the money.

---

## Sources
- [FastAPI — background scope of tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- [LangGraph — persistence and recovery](https://docs.langchain.com/oss/python/langgraph/checkpointers)
- [CrewAI — production architecture](https://docs.crewai.com/v1.15.26/en/concepts/production-architecture)
- [MDN — SSE events and reconnection](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events)

## Connections
- [[141-system-design-llm|System Design LLM]] — assemble components
- [[84-streaming-application-integration|Streaming]] — public contract and reconnections
- [[144-ai-ux-human-in-the-loop|UX & approbations]] — decisions related to proposals
- [[149-delivery-idempotency-concurrency|Delivery & Idempotence]] — submissions and business effects
- [[40-011-langgraph-recovery-concurrency|LangGraph — Recovery]] — exploit persistent states
- [[40-012-crewai-reliable-execution|CrewAI — Production]] — place crews in the service
- [[90-013-agent-testing-recovery|Agents — Contracts, failures & recoveries testing]] — validate the life cycle
- [[00-moc-ai-engineering|MOC AI Engineering]]
