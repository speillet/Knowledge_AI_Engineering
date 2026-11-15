# Delivery, idempotency & concurrency — Flashcards
Tags: #flashcards #ai-engineering #system-design #distributed #idempotency
<!-- summary: guarantees of delivery, limits of exactly once, ambiguous timeout, identity of operations, atomic deduplication, retention, ack, order by entity, optimistic concurrency, isolation and splitting tokens, atomicity of deduplication and effect, key and parameters, duration of deduplication. -->


Do not confuse: at-most-once and at-least-once delivery? <!--anki:6338323339363635373833343438333462316232386335666330386265396435-->
?
**At-most-once** avoids redelivery but can lose a message. **At-least-once** allows redelivery so an unconfirmed message is not abandoned; the consumer must tolerate duplicates.

The choice depends on the cost of loss: losing one telemetry point in a thousand may be acceptable; losing an order is not. The latter needs at-least-once delivery and deduplication. A broker does not necessarily promise to retry forever. For an agent action, distinguish receipt of a message from completion of its business effect: two deliveries can produce one effect if the consumer is designed correctly.

---

Why must an exactly-once guarantee specify its scope? <!--anki:3866373364386264623830343439393839643132626537386366336564633831-->
?
It may cover **an internal transaction within the engine** without covering an external payment or email. For example, Kafka transactions commit the consumed offset and messages written to an output topic together; an email sent during that processing can still be sent twice.

Ask which writes are atomic, how retries are identified and how long duplicates remain recognizable. Repeated deliveries can produce a single business effect through deduplication and a suitable destination. Demonstrate that chain of guarantees instead of inferring it from an option named "exactly-once".

---

Why doesn't a tool call timeout mean that the action failed? <!--anki:3762636139316533313363333433343661616431393837303766633965386439-->
?
The client only knows that it **did not receive a response before the deadline**. The request may never have arrived, may still be running, or may have succeeded with a lost response.

For an action with an external effect, record an "unknown outcome" state and look up its status using the operation identifier. Retrying is safe only if the protocol recognizes the same intent. Retrying with a new identifier can turn a lost response into a duplicate payment or reservation.

---

Do not confuse: idempotency of an operation and determinism of its response? <!--anki:6333353633376632626632373464616362653235323461303964353765613762-->
?
**Idempotency** concerns the effect of repetition: it remains equivalent to applying the operation once. **Determinism** concerns obtaining the same result from the same inputs and conditions.

For example, "set status to closed" can be idempotent while returning "updated" first and "already closed" on a retry. Conversely, two charges can return exactly the same text, "completed".

Define the business effect, key, scope and retention period; separately specify whether retries return the original response. Test concurrent requests and incompatible parameters using the same key. The same seed or model response does not prevent a repeated effect.

---

How do you build an idempotency key for an agent action? <!--anki:6334313330346166326230393438616639636331376164373165343539643165-->
?
Create a **stable identifier for the business intent** before the external call and reuse it on every attempt at that action. Bind it to the tenant and operation type, for example `tenant-7:refund:case-123`; a new intent receives a new key.

Do not derive the key solely from generated text, which can vary, or solely from parameters, because two identical purchases can be legitimate. Also store a fingerprint of the relevant parameters. Reusing a key with a different amount must cause an explicit conflict, rather than silently executing a new action.

---

Why is "check then insert" insufficient to deduplicate concurrent requests? <!--anki:3933616535306664383636303461313561616166333735336439626339326135-->
?
Two workers can both read **"operation absent"** and then each perform the action. A preliminary read does not exclude the other write.

For an effect contained entirely in one database, combine a uniqueness constraint on the operation identity with the business mutation in the same transaction.
```sql
INSERT INTO operations (op_id) VALUES (:op_id)
ON CONFLICT (op_id) DO NOTHING RETURNING op_id;   -- no row: already claimed
```
The second attempt must wait or detect the conflict and retrieve the result. For an external effect, local uniqueness does not cover a crash after execution: the destination must cooperate, or reconciliation must resolve the uncertainty.

---

How long should idempotency keys be retained? <!--anki:3833356231616533393838353431336161336236363963643661633861343836-->
?
Retention must cover **the actual retry and replay window**, including manual recovery, incidents and delayed tasks. After expiration, an old attempt can be treated as new and repeat its effect.

Document the destination's guarantees. For example, Stripe may purge an idempotency key after 24 hours; a manual replay three days after an incident must rely on a persistent business identifier such as a case number. Also define how to handle operations still in progress or with unknown outcomes: deleting them through a simple TTL can reopen a duplicate-execution window.

---

When should a consumed message be acknowledged to avoid loss? <!--anki:6335373038626363656335643437643061396138323437626437366263346362-->
?
After **durably persisting the effect and deduplication information**, when their scope permits it. Acknowledging first can lose work after a failure. Acknowledging afterward leaves a redelivery window if the worker crashes between commit and ack.

For example, with RabbitMQ's `auto_ack`, a worker dying during processing loses the message. With `basic_ack` after commit, the message is redelivered and an idempotent recovery recognizes the duplicate. Execution order alone does not make an acknowledgment and a mutation atomic if they are outside the same transaction. External calls also need a strategy for an effect already performed but not yet recorded locally.

---

Does a message queue guarantee the order of all operations? <!--anki:3637363639313263666164663464396162623837643966323337613735393661-->
?
**Not necessarily.** Ordering may apply only within a partition or key, and multiple consumers can finish processing in a different order from receipt.

Define the required order, usually per business entity. Kafka places all messages with key `order-88` in the same partition, but two consumer threads can still finish them out of order. A version number helps reject stale state. However, a delta such as "add an item" cannot always be discarded just because a later operation has already arrived. Global ordering costs more and is often unnecessary.

---

How does optimistic concurrency avoid a lost update? <!--anki:3161666463306237633138323438643239363864366138383830393164323839-->
?
The mutation checks that **the version previously read is still current**, then increments it in the same conditional write. If another worker changed the object, no rows are updated and the operation must be recomputed or rejected.
```sql
UPDATE cases
SET status = 'valid', version = version + 1
WHERE id = :id AND version = :read_version;
```
This is conceptual parameterized SQL. Check the affected-row count. Do not blindly replay a decision that has become stale, especially if the price, permissions or approved parameters changed.

---

Do not confuse: atomicity and isolation of a transaction? <!--anki:6530353664656438353531373430666239313232376537383430313638306438-->
?
**Atomicity** guarantees that a transaction's writes are committed together or rolled back together. **Isolation** defines what concurrent transactions can observe and which anomalies remain possible.

Two atomic transactions can still violate a global rule if each reads an incomplete view of the other's actions. For example, with a €1,000 limit and €800 already spent, two €150 expenses can each read €800, consider themselves authorized and bring the total to €1,100. Protect the invariant with constraints, locking or appropriate isolation, then handle conflicts and retries requested by the storage system.

---

Why is a distributed lock with expiration not always enough to protect a write? <!--anki:6330663731363636653062313462373339353161646266346433313333343064-->
?
A worker can be **paused long enough to lose its lease**, then resume without realizing it. A second worker now holds the lock, but the first can still send a late write.

A monotonically increasing **fencing token**, checked by the protected resource, allows it to reject operations from a former holder. For example, A receives token 33, then pauses for 40 s, exceeding its 30 s lease. B receives token 34 and writes. When A resumes, storage rejects its write carrying token 33. A conditional version check may also fit the requirement. Test pauses, network partitions and expiration, not just concurrency during normal operation.

---

Calculation: with 10,000 unique operations and 200 redeliveries, how many business effects should an idempotent consumer produce? <!--anki:6639366265346662346162353466626461326365326139646264356530373339-->
?
Assuming each operation is legitimate, eventually succeeds and retains the same identity on redelivery, it should produce **10,000 effects** despite 10,200 deliveries.

The attempt count therefore differs from the business-success count. Measure unique operations, attempts, detected duplicates, unknown outcomes and permanent failures separately. If some keys expire or a retry creates a new identity, this property can fail. The calculation defines an invariant to verify in a failure test, not a guarantee provided by the queue alone.

---

Why should deduplication share the transaction with the effect it protects? <!--anki:3665613635623338613763623466643061636337343935323739356535333435-->
?
If the **processed marker** and business effect are separate writes, a failure can leave an effect without a marker or a marker without an effect. Recovery then creates a duplicate or loses the work.

When the data is in the same database, record the operation identifier and business change in one transaction with a uniqueness constraint. For an external service, use its idempotency contract and reconcile unknown outcomes. Test failures between each step. A simple cache of previously seen identifiers does not provide this atomicity.

---

What should an API do if the same idempotency key is reused with different parameters? <!--anki:6230353163353364626131383436303838353939363261363636343632666335-->
?
**Reject the conflict** according to the documented contract, rather than silently executing a new action or returning a misleading old result. The key identifies a specific intent.

Bind the key to a canonical fingerprint of relevant parameters and its identity scope. Verify the reservation atomically. Document ignored fields and the retention period to avoid logical collisions between distinct operations.

---

## Scenarios

Scenario: two workers consume the same event and each debit a customer credit. How do you make processing safe? <!--anki:6333323763313939336238633437323939313639663864663431656265343862-->
?
1. **Give the operation a stable identity**, separate from the attempt number.
2. **Enforce uniqueness** of that identity in persistent storage.
3. **Combine deduplication and the debit** in the same transaction if both are local.
4. **For a remote effect**, use the destination's idempotency support and keep the result retrievable.
5. **Test races and crashes** before commit, after commit and before acknowledgment.

**Trap**: merely adding `if not exists` to each worker's code.

---

Scenario: a booking tool times out, and the agent proposes retrying with a new key. What should the application do? <!--anki:3963616237306536633261633431313239383533356137653631643030643066-->
?
1. **Keep the original identity** and mark the outcome as unknown.
2. **Look up the booking status** at the provider if its API supports it.
3. **Retry with the same key** only under the conditions guaranteed by the provider.
4. **Block an additional action** while uncertainty cannot be resolved safely.
5. **Reconcile or involve a human** if technical guarantees cannot establish the outcome.

**Trap**: asking the LLM to guess whether the first call succeeded.

---

Scenario: two agents edit the same sales proposal, and one overwrites the other's discount. What protection do you add? <!--anki:3864656164616134346438373437343562316433333263363937303766366237-->
?
1. **Version the shared object** and record the version on which each decision is based.
2. **Make the update conditional** on that version instead of replacing the object unconditionally.
3. **Detect the conflict** and reread the current state before recomputing or requesting a decision.
4. **Revalidate approvals** if authorized parameters changed.
5. **Record the chosen decision** and test simultaneous writes.

**Trap**: automatically retrying the same write after a conflict and recreating the lost update.

---

## Sources
- [Apache Kafka — Scope of Delivery Guarantees](https://kafka.apache.org/41/design/design/)
- [AWS Builders' Library — retries and idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)
- [PostgreSQL — contraintes](https://www.postgresql.org/docs/current/ddl-constraints.html)
- [PostgreSQL — transaction isolation](https://www.postgresql.org/docs/current/transaction-iso.html)
- [Hazelcast — leases and fending tokens](https://docs.hazelcast.com/hazelcast/5.5/data-structures/fencedlock)

- [PostgreSQL — isolation and competing transactions](https://www.postgresql.org/docs/current/transaction-iso.html) — targeted deepening of the 12 November 2026; educational examples are built for this review.

## Connections
- [[140-010-transactions-outbox-sagas|Transactions, outbox & sagas]] — assemble these guarantees in a workflow
- [[142-llm-reliability-resilience|Reliability & resilience]] — make rework safe
- [[84-streaming-application-integration|Application Integration]] — track operations regardless of connection
- [[158-ingestion-cdc-backfills|Ingestion & backfills]] — apply deduplication, versions and checkpoints
- [[150-014-streaming-event-processing|Streaming & event processing]] — delineate end-to-end warranties
- [[40-011-langgraph-recovery-concurrency|LangGraph — Recovery, Concurrency & Evolution]] — external effects and concurrent runs
- [[140-011-agentic-application-architecture|— Architecture & Life Cycle]] — submissions and business effects
- [[119-prediction-contracts-features-batch|Prediction contracts, features and batch]] — production contracts and verifications
- [[00-moc-ai-engineering|MOC AI Engineering]]
