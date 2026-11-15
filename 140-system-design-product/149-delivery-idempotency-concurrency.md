# Delivery, idempotency & competition — Flashcards
Tags: #flashcards #ai-engineering #system-design #distributed #idempotency
<!-- summary: guarantees of delivery, limits of exactly once, ambiguous timeout, identity of operations, atomic deduplication, retention, ack, order by entity, optimistic concurrency, isolation and splitting tokens, atomicity of deduplication and effect, key and parameters, duration of deduplication. -->


Do not confuse: delivery at most once and at least once? <!--anki:6338323339363635373833343438333462316232386335666330386265396435-->
?
**At most once** avoids re-delivery but can lose a message. **At least once** allows re-delivery so as not to abandon an unconfirmed message; the consumer must support duplicates.

The choice depends on the cost of a loss: losing one telemetry point in a thousand is acceptable, losing an order is not. The second requires at least once and deduplication. A broker does not promise to try again forever. For an agent action, distinguish message received and business effect realized: two receptions can correspond to a single effect if the consumer is properly designed.

---

Why does a warranty exactly once have to specify its perimeter? <!--anki:3866373364386264623830343439393839643132626537386366336564633831-->
?
It may concern **an internal transaction to the engine**, without including an external payment or email. For example, Kafka transactions together validate the offset read and the messages written in an output topic; An e-mail sent during this processing can still leave twice.

Ask which records are atomic, how repeats are identified, and how long duplicates are recognized. A single business effect can be achieved with repeated deliveries, deduplication, and suitable destination. This chain of safeguards must be demonstrated instead of inferred from an option with the name "exactly-ounce".

---

Why doesn't a tool call timeout mean that the action failed? <!--anki:3762636139316533313363333433343661616431393837303766633965386439-->
?
The client only knows that he **did not receive a response within the time**. The request may not have arrived, may still be in progress, or may have succeeded with a lost response.

For an action with an external effect, record an "unknown result" state and look for its status with the transaction identifier. A retry is safe only if the protocol allows to recognize the same intent. Retrying with a new identifier can transform a simple loss of response into double payment or double booking.

---

Do not confuse: idempotency of an operation and determinism of its response? <!--anki:6333353633376632626632373464616362653235323461303964353765613762-->
?
**Idempotence** refers to the effect of repetitions: it remains equivalent to a single application. **Determinism** refers to the result obtained for the same inputs and conditions.

Example: "set the status closed" can be idempotent while returning first "modified", then "already closed". Conversely, two bitrates can produce exactly the same text "performed".

Define the business effect, key, scope, and shelf life; specify separately if the fetches fetch the first response. Test concurrent queries and parameters incompatible with the same key. The same seed or message in the model does not protect against a repeated effect.

---

How to build an idempotency key for an agent action? <!--anki:6334313330346166326230393438616639636331376164373165343539643165-->
?
Create a stable **identifier of the business intent**, before the external call, and reuse it every attempt of this same action. Attach it to the holder and the type of operation, for example `tenant-7:refund:dossier-123`; a new intent receives a new key.

Do not derive only the key from the generated text, which may vary, or only parameters, because two identical purchases may be legitimate. Also keep a fingerprint of the relevant parameters. The reuse of a key with another amount must cause an explicit conflict, not execute a new action silently.

---

Why is "check and insert" not enough to deduplicate two competing queries? <!--anki:3933616535306664383636303461313561616166333735336439626339326135-->
?
Two workers can both read **"missing operation"**, then each perform the action. A prior reading does not exclude the other writing.

For an effect entirely in a database, associate a uniqueness constraint on the identity of the operation and the business mutation in the same transaction.
```sql
INSERT INTO operations (op_id) VALUES (:op_id)
ON CONFLICT (op_id) DO NOTHING RETURNING op_id;   -- No line: already taken
```
If the effect is external, the local uniqueness does not cover the crash after its execution: the destination must cooperate or a reconciliation must resolve the uncertainty.

---

Which storage period to choose for Idempotence Keys? <!--anki:3833356231616533393838353431336161336236363963643661633861343836-->
?
The duration must cover **the real horizon of retry and replay**, including manual rework, Delayed incidents and tasks. After expiration, An old attempt can be considered new and reproduce its effect.

Document what the destination guarantees. Example: Stripe can purge an Idempotence key after 24 hours; a manual replay three days after an incident must rely on a persistent business identifier, such as the folder number. Also define the processing of current operations or unknown result: delete them by simple TTL can reopen a double execution window.

---

When to pay for a message consumed to avoid losses? <!--anki:6335373038626363656335643437643061396138323437626437366263346362-->
?
After the lasting **persistent effect and deduplication information**, when their perimeter allows it. Acquitting before may lose work after a breakdown. Acquitting after leaves a redelivery window if the worker crashes between commit and ack.

Example with RabbitMQ: in `auto_ack`, a worker who dies while processing loses the message; with `basic_ack` after commit, the message is re-delivered and an idempotent resume recognizes the duplicate. The execution order does not make atomic an ack and a mutation out of the same transaction. External calls also require a policy for the effect already performed but not yet locally registered.

---

Does a queue of messages guarantee the order of all operations? <!--anki:3637363639313263666164663464396162623837643966323337613735393661-->
?
**Not necessarily.** The order can be guaranteed only by partition or key, and several consumers can complete their treatments in a different order than the receptions.

Define the necessary order, usually by business entity. Example: Kafka places all `order-88` key messages in the same partition, but two consumer threads can still end them in a mess. A version number helps to refuse an obsolete state. But a delta, like "add an article", cannot always be ignored because a next operation has already arrived. The global order costs more and often remains useless.

---

How does optimistic concurrency avoid a lost update? <!--anki:3161666463306237633138323438643239363864366138383830393164323839-->
?
The mutation checks that the **version read is still current**, and then increments that version in the same conditional write. If another worker has changed the object, no lines are changed and the operation must be recalculated or denied.
```sql
UPDATE dossiers
SET status = 'valid', version = version + 1
WHERE id = :id AND version = :version_lue;
```
This example is conceptual parameterized SQL. Check the number of rows affected. Do not blindly replay a decision that has become outdated, especially if the price, rights, or approved parameters have changed.

---

Do not confuse: atomicity and isolation of a transaction? <!--anki:6530353664656438353531373430666239313232376537383430313638306438-->
?
The **Atomicity** ensures that the entries in a transaction are validated together or cancelled together. The **Insulation** defines what competing transactions can observe and what anomalies are still possible.

Two atomic transactions can still violate a global rule if they each read an incomplete state of each other's actions. For example, with a ceiling of 1,000 € already consumed in 800 €, Two expenses of 150 € Read each 800 €, They are allowed and bring the total to 1,100 €. Protect the invariant by constraints, appropriate locking or insulation, then manage the conflicts and recoveries that the storage may request.

---

Why is a distributed lock with expiration not always enough to protect a write? <!--anki:6330663731363636653062313462373339353161646266346433313333343064-->
?
A worker can be **suspended long enough to lose his lease**, then resume without knowing it. A second worker then has the lock, but the first can still send a late write.

An increasing token window, verified by the protected resource, makes it possible to refuse operations from a former holder. Example: A gets the 33 token, then a break of 40 s exceeds its lease of 30 s; B gets 34 and writes. Upon waking up to A, the storage refuses its writing bearing 33.

---

Calculation: with 10,000 unique operations and 200 redeliverys, how many business effects must produce an idempotent consumer? <!--anki:6639366265346662346162353466626461326365326139646264356530373339-->
?
Under the assumption that each operation is legitimate, ends up succeeding and that the deliveries keep the same identity, it must produce **10,000 effects**, despite 10,200 deliveries.

The number of attempts is therefore not the number of business successes. Measure unique operations, attempts, detected duplicates, unknown results and permanent failures separately. If some keys have expired or a retry recreates an identity, this property can break. The calculation defines an invariant to be checked in a failure test, not a guarantee offered by the queue alone.

---

Why should deduplication share the transaction with the effect it protects? <!--anki:3665613635623338613763623466643061636337343935323739356535333435-->
?
If the **marking as processed** and the business effect are two separate writes, a failure can produce an unmarked effect, or an unmarked mark, and the recovery will create a duplicate or lose the job.

When the data is in the same database, record operation identifier and business change in a transaction with uniqueness constraint. For an external service, use its identity contract and reconcile unknown statuses. Test the breaks between each step. A simple cache of identifiers already seen does not provide this atomicity.

---

What should a API do if the same idempotency key is reused with different parameters? <!--anki:6230353163353364626131383436303838353939363261363636343632666335-->
?
**Reject the conflict**, according to the intended contract, rather than silently executing a new action or returning an old misleading result. The key identifies a specific intent.

Associate the key with a canonical fingerprint of the relevant parameters and the identity perimeter. Atomically verify the reservation. Document the ignored fields and the shelf life to avoid logical collisions between separate operations.

---

## Scenarios

Scenario: two workers consume the same event and each debit a customer credit. How do you make this treatment safe? <!--anki:6333323763313939336238633437323939313639663864663431656265343862-->
?
1. **Give a stable identity** to the operation, separate from the attempt number.
2. **Impose the uniqueness** of this identity in the storage of the processing.
3. **Group deduplication and debit** in the same transaction if both are local.
4. **In case of remote effect**, use the destination idempotency and keep the result recoverable.
5. **Test race and crashes** before commit, after commit and before ack.

**Trap**: Place only one `if not exists` in the code of each worker.

---

Scenario: a booking tool responds by timeout; the agent offers to start again with a new key. What should the application do? <!--anki:3963616237306536633261633431313239383533356137653631643030643066-->
?
1. **Keep the original identity** and mark the result as unknown.
2. **Check the status** of the reservation at the supplier if his API allows it.
3. **Try again with the same key** only under the conditions guaranteed by this provider.
4. **Block additional action** as long as the uncertainty cannot be resolved without risk.
5. **Reconciliate or involve a human** if there is no technical guarantee to decide.

**Trap**: Ask the LLM to guess if the first call was successful.

---

Scenario: two agents modify the same commercial proposal and one overwrites the reduction of the other. What protection do you add? <!--anki:3864656164616134346438373437343562316433333263363937303766366237-->
?
1. **Version the shared object** and save the version on which each decision is based.
2. **Make the update conditional** to this version, rather than replacing the object without control.
3. **Detect the conflict** and review the current state before recalculating or requesting arbitration.
4. **Review approvals** if allowed settings have changed.
5. **Trac the decision chosen** and test two simultaneous entries.

**Trap**: Automatically restart the same write after the conflict and recreate the update loss.

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
