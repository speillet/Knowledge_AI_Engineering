# Incremental Ingestion, CDC & backfills — Flashcards
Tags: #flashcards #ai-engineering #data #data-engineering #ingestion
<!-- summary: snapshot or incremental, CDC, snapshot-journal consistency, checkpoints, identities and versions, deletions, historical replay, catch-up capability, quarantine, reconciliation and RAG index, API pagination and consistency of extractions, tombstones and old events replayed, log retention, snapshot border. -->


When to choose a complete rather than incremental ingestion? <!--anki:3366623837653530383437383462643961383764376337666362306263306237-->
?
A **complete rebuild** simplifies logic when volume and delay allow. **incremental** ingestion only processes changes and reduces work, but must manage creation, updates, deletions and recovers.

Deciding on the volume, freshness, and ability of the source to expose changes. Example: 50,000 product topics recharged every night in minutes do not warrant a CDC; 500 million rows to refresh every 15 minutes require it. An optimization that saves computation but loses deletions produces a less expensive and yet incorrect index.

---

Do not confuse: polling on updated_at and capturing CDC changes? <!--anki:6462396566393064356561363466356361666538656537623762333733633834-->
?
**polling** periodically queries the lines according to a field or cursor. The **CDC** captures creations, changes and deletions, often via the transactional log, with a recovery position.

A naive polling on a timestamp may miss physical deletions and long transactions. Example: A transaction writes `updated_at = 09:59:58` but only validates to 10:00:02; the poll of 10:00:00 does not see it, the following filters `updated_at > 10:00:00` and loses it.

---

How to initialize a CDC pipeline without losing the changes that occurred during the snapshot? <!--anki:3235363032383236336631303436323462363731326537383837356235313638-->
?
Coordinate the initial **snapshot and a log position** according to the connector protocol. Competing changes must be connected to the initial state, with a strategy for possible overlaps.

Copying a table and then "start listening now" leaves a loss window. Reading the log before copying without managing the order can also overwrite a recent version by an old one. Example: The PostgreSQL connector in Debezium records the position of the log in the snapshot transaction, copies the tables, and then broadcasts the log from that position. Test concurrent writes during initialization.

---

When to checkpoint an ingestion? <!--anki:3937643835363461623534333431353938363038666366666230333333643530-->
?
After the corresponding **results are durable**, or atomically with their writing if storage allows. Moving the cursor before persistence may lose events after a crash; saving it afterwards may lead to replaying them.

The replay must therefore be secure thanks to a stable identity and to idempotent or deduplicated scripts. Example with Kafka: disable `enable.auto.commit`, write the batch in the destination, then validate the offset; a crash between the two replays at most this batch. A local checkpoint does not prove that a remote index has been updated: define "processing finished" for each destination.

---

Why distinguish document identifier, event identifier and version? <!--anki:3435656462653130323135653463373662643936613263613465353235666131-->
?
The **Document ID** means the business object; the **Event ID** distinguishes a modification from its redelivery; the **Version** helps to order the states of this object. They answer different questions.

Example for `contrat-42`: Deduplicating by document would discard the 8 version after the 7. Deduplicating by event effectively discards the redelivery of `evt-91`, but leaves the 7 version delayed, overwrites the 8. Using a source-guaranteed version order, or an explicit resolution policy: a wall-mounted timestamp does not always offer a reliable order.

---

How do I prevent an older update from overwriting a newer version? <!--anki:3964333238396637636161363466663538346263616534373766353831613139-->
?
Apply a **conditional write to the**, atomic version in the destination: accept only a later version in the order defined.
```sql
INSERT INTO docs (id, version, contenu) VALUES (:id, :version, :contenu)
ON CONFLICT (id) DO UPDATE SET version = EXCLUDED.version, contenu = EXCLUDED.contenu
WHERE docs.version < EXCLUDED.version;   -- An older version doesn’t change anything.
```
A blind upsert is not enough if deliveries are messed up. Distinguishing between events that carry a full state of deltas: ignoring an old state may be correct, ignoring a necessary increment may lose an operation. For deltas, it takes a full sequence, deduplication of operations, or reconciliation from the source.

---

How to propagate a deletion to a RAG index? <!--anki:6663643766393837323139303465393761323836393561653566636136653538-->
?
Keep the **match between source document and derived objects**: chunks, vectors, caches and any copies. A deletion event triggers their removal; a versioned deletion marker can prevent an old update from resurrecting the document.

For example, deleting `doc-17` removes its 12 vectors and writes a marker "deleted in 9 version", which causes a later replay of a 8 version to be rejected. Keep this marker for as long as a replay is possible. Rights changes may also require immediate removal or filtering. An index refreshed only as an addition ends up serving deleted or inaccessible documents.

---

How to organize a backfill without disrupting common ingestion? <!--anki:6463613434353731396239313461323561366438326231356339333839393939-->
?
A **backfill** recalculates a history according to an identified version of the logic. Set range, sources, destination, budget and validation criteria; split into replicable partitions and control the load.

Example: recalculate 18 months of embeddings by monthly partition, in a separate `v2` index, with at most 20% of the call quota; switch only after comparing volumes and a sample of searches. A re-set of data must not automatically restart external business actions such as sending messages or payments.

---

Calculation: How long does it take to absorb 1.2 million delay events with a capacity of 500/s and 300/s of new arrivals? <!--anki:3637333265363631346166363463386638636437393863326131376137643531-->
?
Under the assumption of stable flows and a capacity actually available for this flow, the **net catch-up flow** is 500 − 300 = 200 events/s.
```text
Duration = 1,200,000 / 200 = 6,000 s = 100 min
```
Divide by 500 would forget the new arrivals. If the capacity is less than or equal to the inflow, the delay does not resolve permanently. Add a margin for retrievings, variable sizes and downstream limits, and then check the estimate with the age of the oldest remaining event.

---

What should a quarantine line allow for ingestion events? <!--anki:3134323539383962643133623465376261666338626332323930323866663633-->
?
It isolates **non-treatable events after the recovery policy** without losing their content or their origin. Keep identifier, version, cause, attempts and reference to the schema, with access adapted to the data transported.

Allow alerts, owner, correction, and controlled replay. Moving a message does not resolve its error and can break an entity's order: if the 3 version of `order-88` goes into quarantine, apply the 4 publishes a state that skips the 3. Decide whether to wait. A quarantine counter that increases while the pipeline remains green must appear as a coverage degradation.

---

Why periodically reconcile source and destination despite CDC? <!--anki:6365626330393336663033353433653662393662616164333834623935303332-->
?
To detect **silent deviations**: event lost out of retention, transformation bug, deletion forgotten, downstream write rejected. Example: every night, compare the number of rows and an aggregate footprint of the pairs (identifier, version); only a divergent partition is examined and then repaired.

Comparing on compatible states over time; a source that continues to evolve can create false discrepancies. Repairing divergent objects or rebuilding a full version when necessary. Reconciliation completes the guarantees of the flow: "the consumer is no longer behind" does not prove that the destination is correct.

---

How to paginate a API extraction that continues to evolve during playback? <!--anki:6633313464303738383631643464336538373334383734363432346132633336-->
?
Use the **documented protocol**: token of continuation, stable cursor, or snapshot export when it exists. Offset pagination on a mutable list may repeat or miss objects: if a leading insertion occurs between `offset=0` and `offset=100`, the old 100e object returns to page 2; a deletion would skip the 101e.

Keep the query settings and cursor after persistence, manage expiration and redelivery, and then reconcile identities. Key pagination with total order does not guarantee a consistent snapshot on its own. Do not rebuild an opaque token; a short or empty page does not indicate the end if a continuation is provided.

---

Why should a removal tombstone resist the reappearance of an old CDC update? <!--anki:3435613532346230393762333464396362393565623130393434343061643937-->
?
A **delayed event** may occur after deleting the same object. If the destination has only cleared the line, it may accept this old event and resurrect the data.

Keep a deletion version or equivalent state according to the source contract, and then reject previous events. Set retention consistent with possible delays and replays. Test deletion, old update, and competitor backfill. A reconciliation may reveal the discrepancy, but the version rule must prevent its reintroduction on the next replay.

---

Why monitor CDC's delay in source log retention? <!--anki:3536313134376134313563393466303139383333323632666566363939643936-->
?
If the consumer is too late, **necessary events may disappear from the journal** before reading. Resuming after the last offset becomes impossible.

Alerting with a catch-up margin and documenting the resnapshot procedure. Measuring the available recovery speed. Increasing retention is not enough if the consumer remains sustainably slower than production.

---

## Scenarios

Scenario: after a three-day shutdown, the source log no longer contains the saved CDC position. How do you get started? <!--anki:3266343736653662663136633437326561653766643162373337393430326666-->
?
1. **Recognizing the gap**: Starting from the last available event would silently lose a period.
2. **Evaluate backups and archives** to determine if a full replay is still possible.
3. **Otherwise reconstruct a coherent snapshot**, connected to the log according to the intended protocol.
4. **Validate and reconcile** the new destination, then switch the drives.
5. **Adapt retention and alerts** to the amount of downtime the team must tolerate.

**Trap**: Display a zero delay after simply moving the cursor to the present.

---

Scenario: a backfill has put back in the index of documents deleted the day before. What correction do you make? <!--anki:6165356537633730326435373439663062383533323366623565336332353466-->
?
1. **Suspend the affected exposure**, identify reintroduced objects and any responses served.
2. **Reconstitute timeline**: Backfill snapshot, CDC positions, versions, and tombstones; do not take the ingestion time for a business version.
3. **Refuse old writes**: A 9 version deletion must prevent a 8 version document from being re-played.
4. **Keep proof of deletion** long enough for authorized replays, or reconcile with an authoritative source before publication.
5. **Repair indexes and caches**, then test competitor deletion, update, and backfill, including after tombstones expire.

**Trap**: physically delete the document and its marker, and then accept any missing object as new in the next backfill.

---

Scenario: the indexing job succeeds, but some recent documents cannot be found. How do you investigate? <!--anki:3432306134386337346531643462653539666434353662316534656662633663-->
?
1. **Track their identifiers** from source to published chunks and vectors.
2. **Review checkpoints**, rejections and acknowledgements of receipt.
3. **Distinguish writing and visibility**: The index can accept an update before making it searchable.
4. **Check versions and filters** of rights, as well as the queried configuration.
5. **Reconcile and then replay** the only missing objects, with a search control after publication.

**Trap**: confuse job success, data sustainability and availability in results.

---

## Sources
- [Google AIP-158 — pagination and continuation tokens](https://google.aip.dev/158)
- [Debezium — PostgreSQL connector, snapshots and change log](https://debezium.io/documentation/reference/stable/connectors/postgresql.html)
- [Apache Kafka — delivery and processing guarantees](https://kafka.apache.org/41/design/design/)

## Connections
- [[157-data-contracts-quality|Contracts & quality]] — validation and publication criteria
- [[159-temporal-data-features|Temporal data]] — process late events and historical availability
- [[153-data-flywheel-versioning|Versioning of data]] — index versions and sources to replay
- [[148-llm-batch-pipelines|Pipelines batch LLM]] — resume bulky treatments
- [[149-delivery-idempotency-concurrency|Delivery guarantees]] — Protects Concurrent Rework and Writes
- [[150-013-data-pipeline-orchestration|Transformations & orchestration of data pipelines]] — coordinate covers, partitions and publication
- [[150-014-streaming-event-processing|Streaming & event processing]] — connect source positions and downstream effects
- [[00-moc-ai-engineering|MOC AI Engineering]]
