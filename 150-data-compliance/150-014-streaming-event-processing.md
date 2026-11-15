# Streaming & event processing — Flashcards
Tags: #flashcards #ai-engineering #data #data-engineering
Verified on: 9 October 2026 — technical references and examples of this file.
<!-- summary: batch and micro-batch, partitions and order, consumer groups, windows, triggers, watermarks, flow joins, changelog, state, checkpoints, backpressure and recovery, high cardinality state size calculation, watermark and inactive partition, late state. -->


When to choose batch, micro-batch or continuous event processing? <!--anki:3032656162643734663865393465663462333830356134323166643563383435-->
?
Starting from the **useful time to the product**, the volume and the operating cost. The batch treats a limited set; the micro-batch treats frequent batches; the continuous reacts to the flow, with condition and guarantees specific to the engine.

Example: a fraud score must respond in less than one second during the payment, which justifies the continuous; recommendations refreshed every 15 minutes are content with a micro-batch. The continuous complicates delays, recoveries and provisional results. Measuring the source-to-consumer delay, not just the duration of an operator. "Real time" must correspond to an encrypted objective.

---

What does the order of a log partition guarantee, and what does it not guarantee? <!--anki:6338326166653738356564373431306239633834633264626662613233656530-->
?
A partitioned log can guarantee a **order inside a partition**, depending on its protocol. It does not automatically create a global order between partitions, nor a business order between events that are produced late.

Choose an entity key when its events need to stay together. Downstream asynchronous processing can still reverse effects if multiple queries end in a different order. Keep versions and identities, and then set allowed operations out of order. Changing partitioning requires a transition: switching from 12 to 24 partitions changes the result of `hash(key) mod n`, and new events in one command may precede old ones, left in the other partition.

---

Calculation: a Kafka topic has twelve partitions and a classic consumer group has twenty consumers. How many can receive partitions simultaneously? <!--anki:6532383739336361653033623437306362366538366338656566653239313336-->
?
In this assignment model, a partition is assigned to **only one consumer in the group at a time**: up to twelve consumers receive partitions, and at least eight remain without partition.

A consumer can receive more than one when they are fewer. Adding consumers over twelve does not increase this parallelism. This rule concerns the classic group and the assignment of partitions; other modes of consumption have different guarantees. Even with twelve active consumers, a hot partition can limit the total throughput.

---

How do fixed, sliding and session windows group a stream? <!--anki:3833623466353637333465303431623061363064646663626166653561633631-->
?
A **fixed window** divides time into adjacent intervals; a **slippery window** can make an event belong at several intervals; a **session** groups events separated by less than a defined idle time.

A late event can link two sessions: with 30 minutes of inactivity, clicks to 10 h 00, 10 h 20 and 11 h 05 form two sessions, that one click arrived late, time stamped 10 h 45, it does not indicate which events are merged.

---

Calculation: Ten-minute windows start every five minutes, with [start, end] terminals. To which windows belongs a timestamped event 12 h 07? <!--anki:6535616138623262613361353438366339613530623432373863356535326261-->
?
It belongs to the two windows whose terminals frame it:
```text
[12:00, 12:10)
[12:05, 12:15)
```
It does not belong to [11:55, 12:05) nor to [12:10, 12:20]. A sliding counter can therefore count the same event in several results, without it being a duplicate of delivery. Adding these results as if they were disjointed would be incorrect.

---

Do not confuse: window, watermark and trigger in a flow process? <!--anki:6333633636626131613736393438643661656432656664396638316332353835-->
?
The **window** determines the grouping of events; the **watermark** estimates the progression of the event time; the **trigger** determines when to send a result.

Example: fixed window of one hour, provisional result every minute, main result when the watermark exceeds the end of the hour, then corrections for ten minutes of allowed delay. Also define the accumulation mode: re-issuing a cumulative total does not have the same meaning as issuing only new items. Consumers must know how to replace, add or retract under this contract. No window name alone guarantees that a published result is definitive.

---

Why can an inactive input block the progress of a multi-stream treatment? <!--anki:3035626635653535376633663436623961303863376330656630623633346639-->
?
The engine can combine input progress in such a way that **Conservative**, for example with the minimum of active watermarks. If eleven partitions are 12 h 00 and a twelfth, Silently, Remains at 9 h 00, the global watermark is worth 9 h 00 and no subsequent window closes.

Configure inactivity detection according to engine guarantees, for example in Flink:
```java
WatermarkStrategy.forBoundedOutOfOrderness(Duration.ofSeconds(5))
                 .withIdleness(Duration.ofMinutes(1));
```
A silent entry is not necessarily definitively finished: when it resumes, its events may be late. Monitoring watermarks by entry, expected silence and corrected or rejected events. Force progress changes the compromise between delay and completeness.

---

Why does a join between two streams need time limits or a state policy? <!--anki:3232376662396132363561343434373438633837353838316139363563303139-->
?
To approximate future events, the processing must **retain unmatched events**. Without a cleanup limit or rule, this state can grow indefinitely on unbounded streams.

Set key, match interval, accepted delay, and exit objects that never find a partner. In Flink SQL, an interval join limits this state:
```sql
SELECT c.id, p.amount FROM orders c, payments p
WHERE c.id = p.order_id
  AND p.ts BETWEEN c.ts AND c.ts + INTERVAL '2' HOUR;
```
The interval is about timestamps; the purge depends on the temporal attributes and the progress of the watermarks, not two hours guaranteed. Removing too early loses associations; keeping without limit weighs checkpoints and resumes. Measure state size, restoration and non-matching.

---

Do not confuse: stream append-only, upsert and retraction? <!--anki:3661653836633737643534383434623862646332663462613139646337613366-->
?
**Append-only** adds facts; **upsert** replaces the status of a key; **retracts** takes the effect of a previous result.

Example: a window total changes from 10 to 12. An upsert publishes the new value **12**; differential logic can remove 10 and then add 12, or publish a delta **+2**. Adding both totals as independent events would result in 22 wrongly.

The contract specifies key, version, order, and message meaning. An older late upsert must not overwrite the recent state. On an append-only destination, keep a versioned log and rebuild the state; adding lines without this rule does not properly represent corrections.

---

What exactly does an end-to-end guarantee in a flow pipeline depend on? <!--anki:3366303631323961383065643464383062383064633464343138646561363135-->
?
It is necessary to coordinate **source positions, processing status and output release**, with replayable sources and compatible destinations. Engine checkpoints can restore a consistent state without preventing all repeated external calls.

A transactional write, deduplication, or an idempotent upsert may cover the destination. Example: In exactly-once mode, Flink's Kafka sink validates its transaction at the end of the checkpoint; a `read_committed` drive does not see the outputs of an abandoned checkpoint. An HTTP call to a system without an idempotency key is not necessarily covered automatically.

---

Which compromise creates a deduplication state retention period? <!--anki:6237356261333736383630393461316662643363313136663436343464663136-->
?
A **TTL** limits the retained identifiers and the memory cost, but a replay after their expiration may no longer be recognized. The right duration depends on delays, source retention and replay horizons.

Example: with a TTL of 24 h, replay seven days of the topic after an incident makes repeat six days of events as new. Distinguish TTL technical and business validity. For a lasting effect, persistent protection in the destination may be necessary. Document also what time pilot the expiration, because event time and processing time diverge during a failure. Test a replay beyond the TTL and really announce the guarantee.

---

What is backpressure in a streaming pipeline? <!--anki:6665393562616132383462663461613838303732396565386537313065636431-->
?
A downstream operator that is too slow **slows down its producers** or grows queues, depending on the regulatory mechanism. It is a signal of capacity imbalance, not necessarily a fault of the source.

Measure throughput, delay, queues, status, and wait time to locate the bottleneck. Example in Flink: The operator calling a API of embeddings displays `busyTimeMsPerSecond` close to 1,000, and all upstream ones are in backpressure; it is he who must be processed. Increasing buffers postpones saturation and can worsen memory or latency.

---

What to check before resizing a treatment with status? <!--anki:3266383737393736363035373433643839666335373665666334633266626265-->
?
Check **redistribution of keys, backed-up state compatibility, and recovery protocol**. The engine must regain the correct state of each key after changing parallelism; unstable operator identifiers or an incompatible schema may prevent recovery.

Example in Flink: the state is divided into groups of keys set by the maximum parallelism, at least 128 by default; resizing below this limit from a savepoint, but modifying it renders the state incompatible, and an operator without stable `uid()` may not regain its state.

---

Calculation: a processing retains two million keys, each with 160 bytes of useful state. Which gross volume, then with a factor two assumption for the additional costs? <!--anki:3230616635333332386330373438343662326364653463326336633233366261-->
?
In decimal units:
```text
= 2,000,000 × 160 = 320,000,000 bytes = 320 MB
with factor 2 = 640 MB
```
Factor two is educational, not a guaranteed feature of an engine. Adding buffers, serialization, indexes, checkpoints, and temporary restore state depending on the implementation. The size of the active keys, their lifetime, and unmatched events determine the evolution. A stable memory in normal operation is not enough to guarantee a recovery after several hours of delay.

---

Calculation: a stream receives 500 new/s keys and keeps each 2 hours. How many state entries should be expected without early expiration? <!--anki:6334616264306235323361353463623462333633343833323961323431373665-->
?
The retention is `2 × 3 600 = 7 200 s`. With **500 new keys per second**, the state reaches `500 × 7 200 = 3 600 000 inputs` under established regime, under these assumptions.

Then multiply by the actual size of an entry, including index, serialization, and replication. Late events, timers, and checkpoints add requirements. If keys are reused, the evolution differs; announce their creation rate rather than message throughput alone. A short logical window can still produce a large state with high cardinality.

---

Why can an inactive partition prevent the progress of a global watermark? <!--anki:3164663130616562346535373461663861623133383038316233333934316132-->
?
An operator can wait for **the minimum of the watermarks of its entries**. If a partition no longer produces data or progress, it can hold the closing of the windows.

Configure and test inactivity detection by engine, with a policy for events that return late. Declare an inactive partition too quickly can close windows prematurely. The choice depends on the acceptable delay, not just the observed throughput.

---

Why does purging the state of a streaming window impose a policy for late events? <!--anki:3961326237383934616162373462313238326635313336383236313563313937-->
?
After purging, The system no longer has to **data needed to correct the aggregate**. An ancient event can be rejected, sent somewhere else or trigger a recalculation.

Set retention time, allowable lateness, and correction mode. Publish versions or retractions if the result can change. A watermark is an operational estimate of progress, not proof that no old event will ever happen.

---

## Scenarios

Scenario: a sales aggregate is worth ten, then twelve after a late event; the dashboard displays twenty-two. Where are you looking for the error? <!--anki:3339623237376533666462643433313438653133366233376430313762376233-->
?
1. **Identify output semantics**: cumulative total, delta, or retraction.
2. **Check window key and version** in the consumer.
3. **Apply replacement or appropriate correction**, instead of systematic addition.
4. **Duplicate test, disorder and late correction** with expected results.
5. **Reconcile published aggregates** with a reference reconstruction.

**Trap**: Remove late events to hide an incorrect consumer contract.

---

Scenario: windows no longer close after a source partition is silent. How do you restore the processing? <!--anki:6337646366343165666334363435393961653163393231373838316561363933-->
?
1. **Watch the watermarks by entry** and locate the one that is blocking.
2. **Distinguish expected inactivity and collection outage**.
3. **Configure inactivity or repair source** according to contract and engine.
4. **Definite the fate of events on recovery**, potentially out of time.
5. **Check for completeness and corrections**, not just latency drop.

**Trap**: artificially advance the watermark without measuring the data that this can exclude.

---

Scenario: checkpoints succeed, but a job restart duplicates calls to a API enrichment. Why and what do you change? <!--anki:6132626662613634643666323433343362333361366639363239306232373638-->
?
1. **Delimit the checkpoint guarantee**: internal condition or external effects included.
2. **Identify calls accepted before failure** but not recorded locally.
3. **Use an idempotency key if available**, or a durable outcome and reconciliation protocol.
4. **Separate enrichment and publication**, with recovery and quotas controlled.
5. **Inject a failure at this border** and measure repeated effects and residual cost.

**Trap**: infer the uniqueness of the HTTP effects of an exact-ounce indicator from the engine.

---

## Sources
- [Apache Beam — Windows, Watermarks, Triggers and Status](https://beam.apache.org/documentation/programming-guide/)
- [Apache Kafka — partitions and consumer groups](https://kafka.apache.org/10/documentation/)
- [Apache Flink — status and fault tolerance](https://nightlies.apache.org/flink/flink-docs-stable/docs/learn-flink/fault_tolerance/)

- Supplement of the 14 November 2026 — Event time and watermarks: [Apache Flink — Timely Stream Processing](https://nightlies.apache.org/flink/flink-docs-stable/docs/concepts/time/).

- Supplement of the 14 November 2026 — Inactive sheet music and minimal watermark: [Apache Flink — Generating Watermarks](https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/datastream/event-time/generating_watermarks/).

## Connections
- [[159-temporal-data-features|Temporal data]] — respect event time, availability and delays
- [[158-ingestion-cdc-backfills|Ingestion & CDC]] — connect source positions and downstream effects
- [[149-delivery-idempotency-concurrency|Delivery & Idempotence]] — delineate end-to-end warranties
- [[150-013-data-pipeline-orchestration|Orchestration data]] — coordinate treatments and recoveries
- [[00-moc-ai-engineering|MOC AI Engineering]]
