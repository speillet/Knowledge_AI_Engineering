# Transactions, outbox & sagas for agents — Flashcards
Tags: #flashcards #ai-engineering #system-design #distributed #transactions
<!-- summary: business invariants, double write, outbox and inbox, transactional perimeter, sagas and compensation, isolation of workflows, unknown states, checkpoints, human validation and fault tests, age of events blocked in the outbox, reservation and compensation, publication order. -->


Why start an agent workflow with its business invariants? <!--anki:6130323438373235613561633435303762363666336239313661613163346336-->
?
**invariants** describe what should remain true despite errors and concurrency: an order should not be debited twice, a stock should not become negative, a sensitive action should match the approved parameters.

They guide the storage, transitions, and controls. A prompt asking to "be careful" does not impose anything on the writes; `CHECK (stock >= 0)` or `UNIQUE (order_id)` on the charges table causes the faulty write to fail, regardless of the model text. For each invariant, identify where it is checked, which concurrent operations may threaten it, and what happens if the process crashes there.

---

What problem does a dual write between a business database and a broker create? <!--anki:3335356335363537623034643434623138366330643232363266666135376536-->
?
If one **validates in base and then publishes an event**, a crash between the two leaves a change without notification. If one publishes first, the event can announce a change eventually canceled in base.

Changing the order moves the problem without solving it. It requires proper transactional coordination or long-term recording of the publishing intent with the business mutation. Retries require to know what remains to publish. Example: `commit()` succeeds, then the pod is killed for memory overflow before `send()`; the command exists, but no preparation service learns it, and no `try/except` has run.

---

How does the transactional outbox pattern solve the dual-write problem? <!--anki:3738363031656632333061323438653162666433346538613039663263616231-->
?
Write **the business mutation and the event to be published in the same local transaction**. A relay then reads the validated entries of the outbox and transmits them to the broker, with recovery on error.
```sql
BEGIN;
INSERT INTO orders (id, status) VALUES ('c-17', 'creee');
INSERT INTO outbox (event_id, type, payload)
  VALUES ('e-901', 'CommandeCreee', '{"order":"c-17"}');
COMMIT;   -- the two line_items exist, or none
```
If the transaction fails, neither mutation nor event is validated. If the relay stops, the event remains recoverable. This pairs the intent of publishing to the business state, without making the sending distant atomic. Monitor the age of unpublished events and predict their retention as well as a safe cleaning policy.

---

Why can the relay of an outbox publish the same event twice? <!--anki:3635346334356362356136373464663161633463323539336438313261396566-->
?
It can **publish successfully and then crash before saving this success**. Example: the broker accepts `e-901`, then the relay restarts before `UPDATE outbox SET publie = true`; the next cycle, `e-901` leaves. Marking it as sent before publication would instead create a loss window.

Keep an event ID stable and make consumers tolerant to redelivery. For an order by entity, also carry a sequence and organize relays accordingly. The outbox does not guarantee any global order or unique effect in each recipient by its presence alone.

---

How does a transactional inbox protect a consumer? <!--anki:3430383365313537643539643430323939376562363230306266356365326535-->
?
The consumer stores **the identifier of the processed event and its local mutation in the same transaction**. A single constraint prevents a redelivery from repeating this mutation. After commit, he can acquit the message; a failure before ack becomes a recognizable replay.
```sql
BEGIN;
INSERT INTO inbox (event_id) VALUES ('e-901');   -- primary key: fails if already processed
UPDATE stocks SET reserve = reserve + 1 WHERE sku = 'A12';
COMMIT;
```

The scope is important: an email or payment executed outside of this transaction is not protected by the inbox alone. For these effects, use a durable intent and an idempotent destination, or a reconciliation procedure when the result remains unknown.

---

Do not confuse: Distributed transaction and saga? <!--anki:3466646234613861393631613461663261396532626634643835326633633262-->
?
A **distributed transaction** coordinates participants capable of taking part in a common validation protocol, for example in two phases. A **saga** chain of local transactions and provides business actions to compensate for the steps already carried out in case of failure.

A saga makes intermediate states visible and does not automatically provide isolation of a global transaction. Example: book a hotel, debit the card, issue a ticket; none of these APIs participate in a commit in two phases. If the debit fails, the saga cancels the hotel reservation by a new operation. Calling these APIs from a local transaction block does not include them.

---

Do not confuse: technical rollback and business compensation? <!--anki:3837656434633238643236653433316162336534356533616634623533376262-->
?
A **rollback** cancels an unvalidated transaction within its scope. A **compensation** is a new operation that corrects the consequences of an action already validated: refund, release of a reservation, corrective message.

It does not always restore exactly the past: an email sent could have been read, a refund can lead to fees, it can fail and must be followed. Define these limits with the job before automating the workflow; an "undo" statement does not make an action reversible.

---

How to design a compensation that can itself be replayed? <!--anki:3331396262346265623232323436363539633138626639386561336330633333-->
?
Assign to the compensation a **stable identity related to the original action**, with parameters and state persisted. To enforce its uniqueness and its preconditions by the service performing, not by a simple prior reading.

Example: a compensatory refund succeeds, then the orchestrator falls before saving the response. On recovery, reuse the same identity and find the remote result, rather than create a second refund.

Provide unknown states, bounded entries and reconciliation. A partial compensation must specify amount and perimeter; the same identifier with other parameters must be rejected. The order depends on the trade, not always on the exact inverse of the steps.

---

Why does a saga need to manage interactions with other workflows? <!--anki:3331663431383966636536333430336538353934333936616530343433336638-->
?
Its steps validate visible states **before the end of the set**, so another workflow can make a decision on a tentative booking or pending payment.

Use explicit business statements, reservations, constraints, and version controls to protect invariants. For example, distinguish available, reserved, and sold stock rather than letting each step infer its own availability. Late compensation should not override a legitimate change made in the meantime. Test these interactions as much as the failure of an isolated step.

---

Which states to keep for an external action whose response can be lost? <!--anki:3630666665336530626530633466313961653133376664316562333136306631-->
?
Distinguish between at least **registered intent, current action, confirmed success, confirmed failure, and unknown result**. Example: A transfer expires after 30 s; it changes to "unknown", not "failed", and a key-based lookup reveals that it was executed five minutes later.

Keep operation key, allowed settings, vendor references, and attempt history. Transitions must be controlled: a late return must not overwrite an already reconciled state without verification. Exposing a recoverable status allows the client and operator to track the action even after an agent disconnects or restarts.

---

Why is an agent checkpoint not enough to secure external effects? <!--anki:3333323166376239613861633432613862333037376561316162666230633934-->
?
A checkpoint describes **the saved workflow state**, but is not necessarily atomic with an action performed by a remote tool. If the action succeeds and saving the checkpoint fails, recovery can return to just before that action.

Record the action's identity before the call and reuse it during recovery. For example, LangGraph reruns the `pay` node from the last checkpoint; the stable key `run-42:pay`, passed to the provider, lets it recognize the original charge. Framework persistence makes computation resumable; unique effects require additional guarantees from tools and their destinations.

---

How do you test distributed workflow guarantees beyond the happy path? <!--anki:3632653736656631316438653439633738323635343439386630376137396362-->
?
Inject failures **at the boundaries between effect, persistence and acknowledgment**. Replay the same event, lose a response, stop a worker after commit, reorder messages and run two simultaneous attempts.

Check business invariants and the ability to reach a terminal state or an explicit unknown-outcome state. For example, injecting `os._exit(1)` immediately after commit simulates a shutdown that no `finally` block can intercept; a proxy such as Toxiproxy cuts off the broker's response after receipt. Testing only the HTTP response misses duplicate effects, and a perfect mock can hide the provider's real limitations.

---

Why monitor the age of the oldest unpublished event in an outbox? <!--anki:3636643839336264316663613435313338653061666336363664653033633631-->
?
A **small number of pending events** can hide an event that has been blocked for hours. The volume alone does not reveal either the business delay or a line that fails on each attempt.

Track age, publishing rate, and errors by category. Provide bounded recovery, inspectable quarantine, and reconciliation with expected effects. Test an invalid event in the middle of a healthy stream: it must not disappear or silently block all subsequent ones. The outbox transaction guarantees joint recording; it does not guarantee on its own that the relay will publish on time.

---

Do not confuse: reserve a resource and compensate for an action already performed? <!--anki:6166383563616165386539653430333661356665353132663739613463643463-->
?
**Booking** temporarily retains an action option; **compensation** attempts to repair an effect already produced. A stock booking may expire, while a package shipped does not return instantly by cancelling a line.

Choose according to business constraints, with explicit duration and ownership. A saga does not make each effect reversible. Predict the states requiring human intervention when the compensation fails or remains partial.

---

Why should outbox events be ordered per entity when updates do not commute? <!--anki:3738353130306332626330613431373438386330356135636362626534396639-->
?
Posting "closed" before "open" can make **regress state to a consumer** if events are applied in their order of arrival.

Associating version or sequence by entity and defining the treatment of delays and duplicates. An expensive global order is not always necessary. The consumer must check the compatible transitions; an outbox guarantees the transactional link with the source writing, not all delivery orders.

---

## Scenarios

Scenario: an agent debited a client, then the server stopped before its checkpoint. How do you resume without debiting again? <!--anki:3964366538356535333233633464376439643866666266383932363933616635-->
?
1. **Find the persistent intent** and its initial idempotency key.
2. **Question the supplier** to obtain status or replay the same key as part of its warranty.
3. **Save the confirmed result** and then resume the workflow from this state.
4. **Keep uncertainty** and trigger a reconciliation if the provider does not allow to conclude.
5. **Test this fault window** and check the uniqueness of the flow in the external register.

**Trap**: rely on the only checkpoint that still says "payment to be made".

---

Scenario: creating an order succeeds, but its processing event sometimes never reaches the queue. How do you fix the architecture? <!--anki:3135376531326265343464643465353761393966323438333730396331656366-->
?
1. **Identify double-write** and the window between commit base and publish.
2. **Save order and event** in an outbox transaction.
3. **Add a repeatable relay**, maintaining identity and order policy per order.
4. **Deduplicate at the consumer**, because the relay can publish several times.
5. **Monitor and reconcile** late events, then test crashes before and after release.

**Trap**: Add retries to memory while the intent to send disappears with the process.

---

Scenario: a stock reservation succeeds, the payment fails and the release of the stock also fails. What state should the system expose? <!--anki:3436323335393733623033393463653638316363373766633465393737653534-->
?
1. **Keep the payment failure** and the separate compensation status to complete.
2. **Sustainably record the release**, with an identity allowing it to be replayed.
3. **Check the status of the reservation** before each recovery in order to manage expiration or compensation already made.
4. **Alert after the scheduled time** and provide the operator with the necessary references.
5. **Close only after confirmation** or documented business resolution.

**Trap**: announce "all canceled" while a resource remains blocked.

---

## Sources
- [AWS — transactional outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)
- [AWS — sagas orchestration](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/saga-orchestration.html)
- [Stripe — Contract for Idempotent Requests](https://docs.stripe.com/api/idempotent_requests)
- [PostgreSQL — isolation and competing transactions](https://www.postgresql.org/docs/current/transaction-iso.html)

## Connections
- [[149-delivery-idempotency-concurrency|Delivery, Idempotency & Concurrency]] — guarantees provided by workflow components
- [[45-langgraph-production|LangGraph in production]] — distinguish checkpoint and business effect
- [[115-agent-platforms-governance|Governance of agents]] — permissions, approvals, and compensation
- [[144-ai-ux-human-in-the-loop|UX & validation humaine]] — approve an exact request and track its result
- [[40-011-langgraph-recovery-concurrency|LangGraph — Recovery, Concurrency & Evolution]] — transactional borders
- [[00-moc-ai-engineering|MOC AI Engineering]]
