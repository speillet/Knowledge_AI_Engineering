# Data engineering for an AI Engineer — audit of the 9 October 2026

## Diagnosis and scope

Initial coverage was **solid on ingestion reliability and temporality**, but incomplete on the mechanisms that allow to build and exploit datasets. Contracts, CDC, backfills and point-in-time joins were developed; SQL, analytical modeling, storage formats and distributed computing were mostly discussed through other topics.

The review starts with the existing **129 cards and 1,868 cards**. It maps the themes of the vault and deepens the cards on data, pipelines, automation, ML validation and documentary sources. It does not recheck all products or regulatory texts of the other sections. The dates of verification of the historical cards remain unchanged.

The extension brings **8 cards, 142 cards and an executable SQL workshop**. The course now covers the main data engineering mechanisms useful to an applied AI engineer: correctly transform data, reconstruct it, explain its limits, measure its availability and diagnose its cost. The operational control of each engine remains to work on real projects and incidents.

## Cover Matrix

"Developed" here means definitions, mechanisms, limits and cases of reasoning. This does not mean practical certification on the tools cited.

| Competence | Before this review | Coverage and entry point |
| --- | --- | --- |
| Grain, identities, facts/dimensions, cardinalities, SCD | Little developed | [Analytical modelling](../150-data-compliance/150-010-analytical-data-modeling.md): avoid duplicate accounts, bad labels and entity mixing |
| SQL Transformation | Text-to-SQL covered; insufficient SQL foundations | [SQL for AI datasets](../150-data-compliance/150-011-analytical-sql-transformations.md): joins, NULL, windows, anti-joins, plans and tests |
| Files, columns, partitions, transactional tables | Versioning evoked, storage little explained | [Storage and Lakehouse](../150-data-compliance/150-012-columnar-storage-lakehouse.md): Parquet/Arrow/Avro, pluming, small files, snapshots and maintenance |
| ETL/ELT and orchestration | Appointed tools, poorly developed operation | [Orchestration data](../150-data-compliance/150-013-data-pipeline-orchestration.md): intervals, partition dependencies, publishing, CI, and resources |
| Ingestion, API, CDC, recoveries and deletions | Already developed for CDC and backfills | [Ingestion](../150-data-compliance/158-ingestion-cdc-backfills.md) preserved and completed on pagination of scalable API |
| Business time, availability, delayed labels and features | Already developed | [Variables temporelles](../150-data-compliance/159-temporal-data-features.md) completed on offline/online paths and secure materialization |
| Event Treatments with Status | Watermarks present, incomplete distributed treatment | [Streaming](../150-data-compliance/150-014-streaming-event-processing.md): Windows, triggers, order, joins, corrections, status and backpressure |
| Scale and cost of calculation | Mentioned for lots LLM | [Performance data](../150-data-compliance/150-015-distributed-computing-data-performance.md): shuffle, skew, broadcast, memory, UDF, cache and costs |
| Contracts and data quality | Already developed | [Contrats](../150-data-compliance/157-data-contracts-quality.md): consistent structure, business sense, migration, quarantine and publication |
| Observability, catalog, lineage and incidents | Lineage and quality present, dispersed operation | [Observability data](../150-data-compliance/150-016-data-observability-lineage.md): SLO, coverage, reconciliation, impact and cost of controls |
| Corpus construction RAG, SFT and evaluation | Curation, parsing and versioning already present | [Datasets and corpus AI](../150-data-compliance/150-017-ai-datasets-corpora.md): manifestos, families, shards, readers, mixing, packaging and cover |
| Leak validation and prevention | Already developed | [Validation ML](../170-classical-ml/172-ml-validation-metrics.md), [curation](../150-data-compliance/151-data-curation-annotation.md) and new SQL/corpus cases |
| Confidentiality and governance | Already developed | [Privacy](../150-data-compliance/152-pii-privacy.md), [RGPD](../150-data-compliance/154-gdpr-llm.md), [IA responsable](../150-data-compliance/156-responsible-ai.md); rights and derivative copies recalled in new files |
| Distributed effects and transactions | Already developed | [Idempotence](../140-system-design-product/149-delivery-idempotency-concurrency.md), [Outbox and Sagas](../140-system-design-product/140-010-transactions-outbox-sagas.md), linked to pipeline takeovers |

The content focuses on transferable decisions between engines. For example, the exact-once guarantee requires checking for sources and destinations covered; it does not automatically extend to external HTTP calls. This boundary is explained in the [documentation Flink](https://nightlies.apache.org/flink/flink-docs-stable/docs/learn-flink/fault_tolerance/). Similarly, keeping a snapshot reference does not preserve data after expiration: see the [maintenance Iceberg](https://iceberg.apache.org/docs/latest/maintenance/).

## Additions and corrections

| New form | Cards | Situations included |
| --- | ---: | ---: |
| 150-010 — Analytical modeling | 16 | 3 |
| 150-011 — SQL for AI Pipelines and Datasets | 18 | 3 |
| 150-012 — Column storage, partitions and lakehouse | 19 | 3 |
| 150-013 — Transformations and Orchestration | 17 | 3 |
| 150-014 — Streaming and Event Processing | 17 | 3 |
| 150-015 — Distributed Computing and Performance | 17 | 3 |
| 150-016 — Observability, lineage and operation | 17 | 3 |
| 150-017 — Building Datasets and Corpus AI | 18 | 3 |
| **Total new listings** | **139** | **24** |

Three other cards complete the existing cards: pagination API in 158, then offline/online storage and feature materialization in 159. The **142 additions** include **13 calculations**, **21 distinctions**, **24 set-up** and **84 mechanism, choice or diagnostic cards**.

Four historical answers are corrected, with their questions and identifiers retained:

- Deduplication: a semantic likeness is not enough to merge examples; numbers, negations and variants can be decisive.
- Versioning: A fingerprint does not prove usage rights, and a named version must remain physically accessible to be rebuilt.
- Durable execution: a persistent history does not guarantee the uniqueness of all remote activities.
- Orchestration data and durable execution: distinguish objectives and guarantees without presenting the categories of tools as exclusive.

Each new listing contains primary sources and reciprocal connections. Sources include PostgreSQL, Kimball Group, Apache Parquet/Arrow/Avro/Iceberg/Spark/Beam/Flink/Kafka/Airflow, dbt, OpenLineage, Feast, PyTorch, Hugging Face, and the authors' article on deduplication.

## Recommended route and expected level

This distribution is an editorial recommendation for the vault, not a universal requirement for recruitment.

| Level | Subjects | Proof of expected mastery |
| --- | --- | --- |
| Base of any applied AI Engineer | Grain and keys, SQL, contracts, temporality, splits, provenance, formats and rights | Build a correct dataset, explain each line and find the source of an error |
| Autonomy on a product in production | Incremental, orchestration, storage/versioning, corpus, quality and SLO | Replay, publish, diagnose degradation and repair without corrupting consumers |
| Deepening according to the position | Streaming with state, distributed tuning, state migrations, lakehouse platforms | Test load and failures on the retained engine, encrypt compromises and exploit the solution |

Order of work: **→ SQL Modelling → contracts → ingestion and temporality → storage and orchestration → corpus and observability** Study streaming and distributed computing whenever a need for latency or volume warrants. The notions of shuffle, state and partitioning must be understood before setting a cluster configuration.

The following specializations are still to be explored depending on the context: detailed administration of a Kafka/Flink warehouse or cluster, proprietary formats, networks and IAMs specific to the cloud, geospatial engines, specialized audio/video formats and optimization of engine algorithms. Adding them all to the base would impair its readability. The current topics allow you to ask the right questions and consult the appropriate references.

## Workshop 1 — SQL, grain and time availability

The [Executable Workshop](../examples/data-engineering/sql_workshop.py) uses only the standard Python and SQLite library in memory, with synthetic data. Window functions require SQLite 3.25 or newer.

From the root of the repository:

```bash
python3 examples/data-engineering/sql_workshop.py
```

Predict the results before execution, then explain the discrepancies. The workshop checks **7 cases and 14 results**: multiple joins, LEFT JOIN filters, NULL and anti-joins, ordered deduplication, window frames, join respecting availability, then replay and tombstone versioned.

Then modify a case: add two commands of the same amount, a client with no feature or an old event after deletion. Justify new results and possible correction. The time join of the workshop assumes complete states, a version order per entity and canonical UTC timestamps; it is not a generic implementation of any bitemporal dimension.

**Deliverable**: Queries, limit case sets, and before/after grain explanation. The results must remain correct when the insertion order changes. The script tests local SQL examples; it does not validate the performance of a warehouse or the failures of a distributed system.

## Workshop 2 — Ingestion, publication and reconstruction

Build a small pipeline of orders and versioned documents. Define contract, pagination, or change log, input and output manifests, quarantine destination, and release of a validated version. Produce an analytical table and document-to-chunk correspondence.

Inject duplicate, delete, messy event, missing partition and crash after writing before checkpoint. Perform a backfill with the same logic and then with a new version, protecting the current state. Also provide a source that continues to change during an extraction.

**Deliverable**: reconciliation report and recovery procedure. Outputs must not resurrect a deleted document or declare an amputated batch complete. Specify what is atomic, how long replay is possible, and what data becomes unrecoverable after expiration.

## Workshop 3 — Storage and Cost of Execution

On a public or synthetic game adapted to the available resources, compare an unselective layout to a partitioned or sorted Parquet version. Execute the same requests, then modify the number of files, projected columns and key distribution.

Measure scheduling time, duration, read bytes, maximum memory, and cost at a stated rate. Start on a machine; use a distributed engine only if the volume or target station warrants it. Compare conventional join and broadcast on a controlled size reference, and then introduce a hot key.

**Deliverable**: Same results, plans and comparable measures, with documented cache status. An advertised improvement must come from the measures, not the name of the tool. Include compaction, rewrites, orchestration and reserve in the retained cost.

## Workshop 4 — Flows, Features and Status

Simulate time-stamped events with duplicates, late arrivals and inactive input. Publish a rolling counter and common features with an explicit correction, TTL and availability policy.

Replay after checkpoint, then make an event happen beyond the deduplication time. Compare offline reconstruction and values actually available online. For a platform role, repeat with a real flow engine and a state resizing; a local simulation must remain presented as such.

**Livable**: chronology of events, published values, status size, and recovery report. The consumer must correctly interpret totals, deltas, and retractions. Document excluded events and external effects that escape the transactional protocol.

## 5 — Corpus AI Workshop and Data Incident

Prepare a corpus with multiple formats and families of documents. Produce extracted texts, examples, splits and shards from a manifest. Test that two configurations of workers read the desired coverage, and then compare the mixture into documents and tokens.

Change the parser to a subset, introduce a loss of client data and overlap between train and test families, and trace these incidents through quality checks and dependency graphs to the relevant indexes or models.

**Deliverable**: reproducible manifest, contamination and filtering report by segment, coverage checks and reconstruction plan of affected derivatives. The presence of reference documents in a RAG can be expected: distinguish this expected access from a leak of the evaluation answers.

## Validation and conservation

The value increases to **137 cards and 2,010 cards**, on the same 17 sections, with **89 calculations**, **317 situationalized** and **162 distinctions**. No existing card or section titles are renamed; old assignments to Anki packages must remain stable.

Verifications of this delivery:

- Global lint without error or warning, with Spaced Repetition playback compatibility.
- Synchronized README/MOC catalogs and controlled internal links.
- Added calculations recalculated; SQL workshop executed with its 14 expected results.
- 40 successful repository tests; their temporary copy now includes Python examples to check for new links. Archive Anki and SQLite integrity checked.
- 1,868 pre-existing active identifiers retained; four modified responses and 142 new cards identified.
- Export with 2,010 active cards and previously removed 30 cards still suspended; old assignments to preserved packets.

Export controls compare product files, without simulating import into a user's personal collection. No Spark/Flink clusters, cloud storage, or feature store service were deployed for this review. The 2 to 5 workshops are exercises offered, not experiments advertised as performed.

Commits separate modeling/SQL, storage/computing, orchestration/streaming, corpus/observability, then documentation and executable workshop.
