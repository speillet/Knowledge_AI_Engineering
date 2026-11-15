# Columnar storage, partitions & lakehouse — Flashcards
Tags: #flashcards #ai-engineering #data #data-engineering
Verified on: 9 October 2026 — technical references and examples of this file.
<!-- summary: warehouse, lake and lakehouse, object storage, JSONL/Avro/Parquet/Arrow, row groups, pluming, partitions, small files, table formats, transactions, snapshots and deletions, predictive pushdown and bytes actually read, min-max and sort, compaction and snapshots. -->


Do not confuse: data warehouse, data lake and lakehouse? <!--anki:3030646666643563393464653462346261336265636638363463376338646433-->
?
A **warehouse** organizes data for analytical queries and their governed exploitation. A **lake** keeps files of various formats, often on object storage. A **lakehouse** approach adds metadata and table guarantees to the lake data.

Example: Cleaned sales in an SQL warehouse; raw PDF and JSONL annotations on S3; Iceberg tables on S3 readable by Spark, Trino and DuckDB. These architectures overlap; the name does not guarantee quality, low cost, or transactions covering all systems. For AI, review reproducibility, scans, updates and governance. A small project can remain on a relational basis and a few versions.

---

How to choose a storage according to the access mode of an AI system? <!--anki:3663373738663333303333623439343739643862663930666330343933613363-->
?
Starting with **requests and expected guarantees**. Low-latency key readings, business transactions, scans of billions of lines, and a search for vector neighbors require different structures.

Example: the balance of a client read by key in milliseconds in PostgreSQL, two billion training examples scanned in Parquet, 50 million vectors in a neighbor index. Define which is authoritative and how to synchronize derivatives. A vector base is not necessarily the repository of documents or permissions. Measure freshness, consistency, latency and cost of updates, not just the read rate.

---

Why should object storage not be treated as a transactional directory? <!--anki:3630353762313535616662303433316362353863316539666438646637646335-->
?
Object storage handles **key-identified objects**; folder-like prefixes do not guarantee atomic renaming of a set or transaction between files. Thus, `aws s3 mv` of a "folder" copies and then deletes each object: a drive that lists during the operation sees part of the files at each path.

To publish a consistent dataset, write immutable objects and then a manifest or table commit with a suitable primitive. A strong reading consistency of an object does not create a multi-file transaction. Keep fingerprints, permissions and cleanup policy; partially published files must not become visible by simple listing.

---

When to choose JSONL, Avro or Parquet to transport or store data? <!--anki:3066323536333964353739333464356261316533366661653538363834353162-->
?
**JSONL** facilitates line-by-line inspection and exchange, with schema validation to be organized. **Avro** provides serialization with schema and rules for reader/editor resolution, useful especially for events. **Parquet** stores columns to promote selective scans and analytical compression.

Example: JSONL for 500 manually read evaluation cases, Avro for Kafka events with schema registry, Parquet for 300 GB of features read per column. No single format provides the business quality or transactional publication of multiple files. Dates, decimals, and null values can change direction during conversions; test a round trip on representative cases before generalizing.

---

Do not confuse: Apache Arrow and Parquet? <!--anki:6539306639333663303634313464316662323232623664356536663438626362-->
?
**Arrow** defines in particular a columnary representation in memory and exchange mechanisms; **Parquet** is a format of columnary files intended for storage. One can read Parquet in Arrow structures before transforming the data.

Copyless transfer is possible under certain performance and compatibility conditions, not guaranteed across the entire string. Decompression, type conversions, or switching to Python objects may allocate more. Estimate memory after decoding: A compressed 2GB file does not mean a 2GB dataset in RAM.

---

How do row groups and Parquet statistics reduce readings? <!--anki:3031373261633839316630383435373662656333656466396161343637303136-->
?
Parquet groups rows into **row groups**, with data organized by column. The reader can read only the projected columns and eliminate groups incompatible with the filter thanks to the statistics.

Example: if the min/max dates of a group are in January, a search limited to February can avoid it. If each group mixes all year, these terminals become little selective despite the same `WHERE`.

Tri/clustering, group size, and drive support determine the gain. Statistics can prove the absence of a match, not necessarily its presence. Check the plan and bytes actually read; fewer rows returned does not mean less data browsed.

---

Do not confuse: Table partitioning and data clustering? <!--anki:3662303934643933613532383461363562383262383334363637633031396364-->
?
**partitioning** logically separates data according to a rule, e.g. day, to discard entire sets. **clustering** or sorting approximates values within a set and can make file statistics more selective.

Their implementation varies depending on the storage and engine; they can complement each other. With Iceberg:
```sql
CREATE TABLE events (...) USING iceberg PARTITIONED BY (days(ts));
ALTER TABLE events WRITE ORDERED BY client_id;   -- sorting in each partition
```
A filter on the dates spreads out entire days; a customer filter takes advantage of the min/max terminals tightened by the sorting. Choose according to the actual load and the maintenance cost, without assuming that a classic index exists everywhere.

---

Why partitioning a lake by user ID might be a bad idea? <!--anki:3563653662333435323461343435656438363565376131373636373639363161-->
?
A key to **Very strong cardinality** can create many tiny partitions and files, with metadata costs, planning and access. Low-active users make this problem worse.

Example: partitioning per user can create five million tiny partitions; `bucket(64, user_id)` limits to 64 buckets per combination of other keys, **not to 64 files**. Multiple writes still produce multiple files per bucket. Evaluate time partition, buckets or clustering according to requests. Measure sizes, selectivity and write rate. A physical partition does not replace either the holding filter or the authorization.

---

Why can small files slow down a pipeline despite a low total volume? <!--anki:3433366436636633346263343464353361393731326537356234313339623635-->
?
Each file incurs fixed costs: **opening, metadata, storage requests, and task scheduling**. Millions of small objects can saturate these operations before saturating bandwidth.

Compaction brings together files to reduce this additional cost, while respecting atomic visibility and competing drives: in Iceberg, `CALL catalog.system.rewrite_data_files(table => 'db.events')` publishes the files grouped in a new snapshot. Over compacting can decrease parallelism and selectivity or increase processing memory. Choose a size from engines and load, then measure scheduling time, bytes read and rewrite cost. Compaction must not change the logical content.

---

Do not confuse: Parquet file format and Iceberg table format? <!--anki:3934663237633862386161363466643438663962343434343237373965363565-->
?
**Parquet** describes the organization of a file. **Iceberg** describes a table, its files, snapshots, schemas, and partitioning metadata; the data files can be in Parquet.

The table format allows consistent reading and evolution of metadata. Dropping multiple Parquet files into a folder does not create these guarantees: a drive that lists the folder while writing 40 files can see 17, while with Iceberg it follows the snapshot of the catalog and sees 0 or 40 files. Check the compatibility of the engines with the features used; the catalog that publishes the state.

---

Which border to check behind a lakehouse’s ACID transaction promise? <!--anki:3333393839643435393330613435613461653933393938343365653264303863-->
?
Identify **the actual transactional unit**: often a table and its commit, with guarantees defined by engine, catalog and operation. A snapshot reading can be consistent while two tables have been updated at different times.

Linking examples and labels requires compatible versions or explicit publishing protocol. Two `MERGE`s from the same snapshot can conflict depending on the affected data and isolation; sharing this snapshot does not guarantee failure. After conflict, re-evaluate the operation on the new state before recovery. Vector indexes and external notifications do not become atomic with the table commit.

---

What does an Iceberg table schema or partition change? <!--anki:3934373662376233643038313435363939653136653763656238663766316266-->
?
Iceberg uses **field identifiers** to follow the pattern, and can make several partitioning specifications coexist. Changing partitioning concerns new writes without automatically rewriting all old files: `days(ts)` To `hours(ts)` on 1 October, September is cut by day.

This facilitates physical evolution, but does not implicitly convert the business sense of the values. Renaming a unit without conversion remains an error. Check compatibility of drives, allowed types and file distribution; provide for rewriting if it is necessary for performance. Metadata evolution and content migration are two separate operations.

---

Why does time travel not guarantee the indefinite reproducibility of a dataset? <!--anki:3234316635376566313530393462313339633664383431393039626630656532-->
?
Historical queries depend on **keeping snapshots and their files**. `SELECT … FROM t VERSION AS OF 8231` only works as long as `expire_snapshots` has not removed this snapshot: expiration can make an older version inaccessible; a reference saved in a report does not preserve bytes.

Align retention, backups, and reproduction needs, with applicable deletion constraints. Keep transformation versions and external sources as well. A backup is valid by restore, and a history on the same storage does not cover all its failures. Document how long each experience remains effectively rebuildable.

---

How does a logical deletion differ from the physical deletion in an analytical table? <!--anki:6265383661383361643162653461633039386537636361643636396331306632-->
?
A deletion can become invisible to drives via **rewrite files or delete metadata**, depending on format and engine. Older copies can remain in snapshots, caches, exports, or backups.

Example: With the Iceberg delete files, a `DELETE` saves the removed rows; their bytes remain in the data files until they are rewritten, and then the snapshots that reference them expire. A drive that bypasses the table format can still see them. Do not announce a complete delete from a simple successful `DELETE`.

---

Calculation: a table of 900 GiB covers 30 uniform days and 30 columns of equal size. What ideal volume read for seven days and three columns, then what fictitious cost to 5 €/Tio read? <!--anki:6133366430376232616236663464333062343230313637323538633533316336-->
?
Assuming perfect removal of partitions and proportional projection of columns, excluding metadata and additional costs:
```text
volume = 900 × 7/30 × 3/30 = 21 GiB
cost = 21/1,024 × 5 ≈ 0.103 €
scan complet = 900/1 024 × 5 ≈ 4,39 €
```
Actual columns are not all the same size and filters are not always actionable. Units billed may differ from the physical bytes read. This calculation illustrates selectivity; check plan, scan metric and effective pricing for an actual decision.

Different physical compression between columns would invalidate the simple 3/30 ratio. To check the economy, compare the scans with the same engine, the same table version and the same expected result.

---

Calculation: 512 GiB are written as 1 MiB files. How many files does this represent, then how many after ideal grouping to 256 MiB, without volume change? <!--anki:6234616161353562636366313461336539396633666533663134323566393432-->
?
With binary units and uniform files:
```text
512 × 1 024 / 1 = 524 288 fichiers
512 × 1 024 / 256 = 2 048 fichiers
```
The number of files is divided by **256**, not the volume of data. The time saving is not necessarily the same factor: reading, compression, network and writing remain to be paid. The size of 256 MiB is a pedagogical hypothesis, not a universal rule. Keep enough parallelism and check the results after publication of the new snapshot.

---

Why doesn’t a logical filter on a Parquet table guarantee that the engine will avoid reading unnecessary blocks? <!--anki:3265386435343263333261653439353938353237386165356538383439383134-->
?
The **predicate pushdown** depends on the statistics available and the shape of the filter understood by the engine. An opaque conversion or function applied to a column can prevent the early elimination of files or row groups.

Examine the plan and bytes actually read with the target engine. Compare an equivalent expression that can be used by statistics, without changing the time zone, type or processing zero values. Filtering the result can be correct even if almost everything has been scanned. Test the performance on the actual physical organization of the data.

---

Why can sorting data improve the pruning of a Parquet file? <!--anki:3235353262366532626430343465666638333236396333303334633231353636-->
?
Row groups containing **tighter ranges** allow min/max statistics to exclude more groups for some filters.

Without organization, each group can cover almost the entire range and remain a candidate. The profit depends on the filtered columns and the cost of sorting. Measure the bytes actually read; the number of rows returned is not enough to estimate the work avoided.

---

Why shouldn't a compaction lakehouse immediately delete old files that are still referenced? <!--anki:3764313336613332376531623437656461366566373833643064383130636466-->
?
Readers or snapshots can **use the old version** while the new one becomes visible. Delete too early breaks their readings and the possibilities of historical return.

Publish the new version through the transactional mechanism of the table format, then apply a drive-compatible retention. Also check for orphan files. Object storage alone does not know these logical dependencies.

---

## Scenarios

Scenario: a feature preparation of 80 GB mostly takes time to start and opens two million files. What diagnosis do you propose? <!--anki:3330353764633634663539633439363661336132323938336534663831643435-->
?
1. **Separate planning and execution**, with number and size of files.
2. **Measure metadata access** and pressure on object storage.
3. **Test limited compaction** on a partition with the same logical content.
4. **Compare duration, memory, read bytes and parallelism**, without assuming a proportional gain.
5. **Correct the write rate** so that you don't immediately recreate small files.

**Pip**: Add workers while the bottleneck is in file discovery.

---

Scenario: a three-month old snapshot, but the cleaning only keeps it for thirty days. How do you make the policy consistent? <!--anki:6263313164346630626434383432633761613635653839303039633762323062-->
?
1. **Inventory of the experiments to be reproduced** and the data still present.
2. **Defining an explicit horizon** with owners, costs and conservation constraints.
3. **Protect or archive the necessary versions** according to the storage capacity.
4. **Check for actual reconstruction** with files, code, and dependencies.
5. **Declare irrecoverable versions** and adapt future maintenance.

**Trap**: Keep only a snapshot ID assuming it automatically protects files.

---

Scenario: two jobs each publish a coherent table, but the model reads new features with old labels. What's missing? <!--anki:3233323235343331316664383466343161633536626365653736376336336264-->
?
1. **Identify incompatible versions** and affected consumers.
2. **Define a publication set** that references compatible versions of both tables.
3. **Validate this set before visibility**, with key and period controls.
4. **Read versions explicitly**, instead of two independent “latest” states.
5. **Test interruption and concurrency** during publication.

**Trap**: Deduct a multitable transaction from the mere presence of a transactional table format.

---

## Sources
- [Apache Parquet — file structure](https://parquet.apache.org/docs/file-format/)
- [Apache Parquet — row groups, chunks and pages](https://parquet.apache.org/docs/concepts/)
- [Apache Avro — Schema Specification and Resolution](https://avro.apache.org/docs/1.12.0/specification/)
- [Apache Arrow — columnar format](https://arrow.apache.org/docs/format/Columnar.html)
- [Apache Iceberg — reliability and concurrency](https://iceberg.apache.org/docs/latest/reliability/)
- [Apache Iceberg — Evolution](https://iceberg.apache.org/docs/latest/evolution/)
- [Apache Iceberg — maintenance and expiration](https://iceberg.apache.org/docs/latest/maintenance/)

- Supplement of the 14 November 2026 — Physical Organization Parquet: [Apache Parquet — File Format](https://parquet.apache.org/docs/file-format/).

- 14 November 2026 — Snapshots and Reading Insulation: [Apache Iceberg — Reliability](https://iceberg.apache.org/docs/latest/reliability/).

## Connections
- [[153-data-flywheel-versioning|Versioning of data]] — preserve physical versions needed for experiments
- [[157-data-contracts-quality|Contracts & quality]] — publish a consistent and readable report
- [[150-011-analytical-sql-transformations|Analytical SQL]] — link SQL filters and data actually read
- [[150-015-distributed-computing-data-performance|Distributed Computing & Data Pipeline Performance]] — connect data layout and execution cost
- [[150-017-ai-datasets-corpora|Building Datasets & Corpus IA]] — organize and read shards efficiently
- [[00-moc-ai-engineering|MOC AI Engineering]]
