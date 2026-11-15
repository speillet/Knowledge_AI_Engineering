# Concrete anchoring of abstract maps — 22 October 2026

This pass continues the enrichment of the [17](relevance-review-2026-10-17.md) and [20 October](mlops-card-expansion-2026-10-20.md). It no longer aims at the length of the answers but their **anchoring**: the README requests "quantitative reference points and executable examples rather than abstract formulations", and the review of the 17 October reported recent cards "that answer with a checklist".

The following sections keep the historical record of the 22 October. These local changes were integrated and completed during the [Cross-country pass in November](#cross-sectional-supplement-of-november-2026) described at the end of the document; its figures should not be confused with those of the first pass.

## Perimeter

- **Start Measure**: A card is said to be abstract when its answer contains no numbers or codes, excluding situations. This was the case of 737 cards on 2,186, with a median of 82 words, above the median of the vault. Extending them was therefore not the right answer.
- **Files processed** All of which at least 60% definition cards were abstract, either 37 cards. They are concentrated in the most recent fact sheets: data (150), ML Classic170), System Design140), Observability (90), Inference (60-010 TB 60-012).
- **Excluding scope**: questions, scenarios and calculation cards have not been modified. The cards below the threshold of 60% have not been re-read.

This measure is a crude indicator: an example named without a number remains counted as abstract, and a comparison card can be useful without an example.

## Rule applied

Each addition **replaces a generic sentence** rather than adding to it, to remain below the limit of 110 words. It brings one of the following four elements, absent from the map and its neighbors:

| Contribution | Examples |
| --- | --- |
| Encrypted scenario | Coordinated omission on a blocked client 2 s, spending cap exceeded by two competing transactions, coverage of an interval at 90% measured at 83% |
| Code or request | outbox and inbox in SQL, conditional write `ON CONFLICT … WHERE`, reducer LangGraph that rejects conflicts, `merge_asof` point-in-time, salting PySpark |
| Concrete mechanism | long transaction lost by a polling on `updated_at`, swapping two `interrupt`, replication of KV heads beyond TP=8, prompt cache served during its refresh |
| Decision criteria | rule, supervised model or LLM as required, ETL or ELT, table or recording lineage, outliers or novelty |

Three controls complete this rule:

- **No answer given in advance**: before writing, the situation and calculation cards of the card have been reread. Five examples that used almost word for word a situation or a neighboring card have been replaced: relaunch of a reservation with a new key, variants of the same tutorial, exposure of the novelties, negation deleted by normalization, deletion of an SQS message.
- **A notion, a reference map**: an order of magnitude already established elsewhere is cited by a link. The multiplier of tokens of multi-agent systems thus remains in the 31 sheet; the 36 sheet illustrates rather the critical path by a calculation of delay.
- **Consistency with workshops** : the cards of the cards 90-013, 140-011 and 20-010 The real tests of `examples/agentic-support` and `examples/verifiable-rag`. A deviation has been corrected before publication: the counterfactual test of the workshop RAG Passing the deadline to 60 days, not to 45.

## Results

| Indicator | Before | After |
| --- | ---: | ---: |
| Cards | 2,186 | 2,186 |
| Modified cards | — | 316 |
| Abstract cards (neither number nor code) | 737 | 481 |
| Cards with a block of code | 214 | 262 |
| Average words by answer | 78.6 | 80.9 |
| Median words by answer | 80 | 82 |
| Maps under 50 words | 69 | 55 |

| Section | Sheets | Modified cards | Abstracts before → after |
| --- | ---: | ---: | ---: |
| 150 — Data & Compliance | 11 | 107 | 112 → 16 |
| 140 — System design & product | 5 | 47 | 51 → 19 |
| 90 — Observability & evals | 4 | 46 | 43 → 6 |
| 170 — ML Classic | 5 | 41 | 45 → 18 |
| 60 — Inference LLM | 4 | 30 | 32 → 3 |
| 20 — RAG | 2 | 14 | 18 → 5 |
| 40 — Automation | 2 | 14 | 17 → 7 |
| 50, 30, 160, 70 | 4 | 17 | 23 → 11 |

No question has changed: Anki IDs and review history are retained. No response exceeds the limit of lint.

## Verifications

- **API Cities facing library code**, installed in a temporary environment to the versions of the workshop when they are pinned: Langfuse 4.17.0 (`trace_context`, `completion_start_time`, `mask` and `mask_otel_spans`, `should_export_span`, lots of 512 Spans All 5 s, Cache of Prompts 60 served during its refreshment, Absent variable left as is by `compile`), LangGraph 1.2.14 Langgraph - Sdk 0.4.6 (`durability`, `Command(resume=…)` by identifier, `checkpointer=True` of a subgraph, `multitask_strategy`, default recursion limit of 10,007), TRL 1.14.2 (`DPOTrainer`, `beta` of 0.1), Hugging Face Datasets 5.1.0 (loss of mixing buffer on recovery, `split_dataset_by_node`), scikit-learn and statsmodels`TimeSeriesSplit`, `TargetEncoder`, `ExponentialSmoothing`, `ARIMA`), docling-core 2.103.1 (names of the chunkers).
- **Calculations** of quantified examples redone: ROI, robust MAD, exposure probability weighting, truncation, aggregated rates, point adjustment.
- **Vault**: lint without error or warning, 52 repository tests successful with `scripts/requirements.txt` dependencies, Anki export generated (2,186 cards, 71 removed), synchronized catalogs.

The other default values and syntaxes cited are from the tool documentation and have not been rechecked online during this pass: Spark (200 Shuffle topic music, the Broadcast Threshold 10 MB, `maxResultSize` of 1 GB), Flink (maximum parallelism of at least 128, `withIdleness`), Iceberg, dbt, Airflow, Kafka, pgvector 0.8, Stripe (clearable keys after 24 hours), Debezium and vLLM. The dates `Verified on` the topics have not changed, since only the added claims have been checked.

## Proposed action

- **Sheets under the threshold** : 481 Cards remain without numbers or codes. A part is legitimate (definitions, "not to be confused" cards already illustrated with names); Re-read the files between 50 and 60% (95, 96, 40-010, 40-012, 133, 161).
- **Duplicates between topics** revealed by this pass: 158 and 150-016 (source-destination reconciliation), 20-010 and 143 (Partial response, conflicting sources, 62 and 69 (disaggregation), 150-014 and 159 (watermark). Their merger is a review of relevance.
- **Dated review**: Compare the above-mentioned defaults with the documentation in the next review of 150-012 to 150-015 and 158.

## Cross-sectional supplement of November 2026

The first pass of November covered the **147 topics of the 17 sections**, including container indexes. Compared to the commit `218570f`, **536 responses on 2,186** were modified: the 316 responses of the initial local work, reread and corrected when necessary, and 220 additional responses in the other 110 topics.

Each file therefore contains an effective enrichment; this does not mean that its answers have all been rewritten. Additions target insufficiently explained mechanisms, decision criteria, counterexamples and concrete verifications. Length alone is not an objective.

| Thematic Lot | Sections | topics | Amended responses |
| --- | --- | ---: | ---: |
| Prompts, RAG, agents and workflows | 10, 20, 30, 40 | 32 | 85 |
| Models, training and inference | 50, 60, 130 | 26 | 78 |
| Infrastructure and API | 70, 80 | 19 | 37 |
| Evaluation, safety and operation | 90, 100, 110, 120 | 29 | 96 |
| Architecture, data and compliance | 140, 150 | 28 | 178 |
| Multimodal and classic ML | 160, 170 | 13 | 62 |
| **Total** | **17 sections** | **147** | **536** |

### Substantive corrections

- **Measurement and cost**: distinguish tuning and accuracy, observation and cause, quantiles by component and overall latency; convert FLOPs to seconds and then to GPU-hours; include failure costs.
- **Execution**: specify recovery limits, idempotency, cancellation and budget; do not make a trace assertion successful because no expected span has been produced.
- **Infrastructure**: distinguish OCI roles, Kubernetes Service types, readiness and liveness, VRAM application budget and hardware isolation.
- **Data**: Buckets do not limit the number of files; purging a time join depends on watermarks; a salt average should ignore null values like the reference aggregate.
- **ML**: `TimeSeriesSplit(test_size=28)` counts observations, not months; a multi-horizon seasonal baseline should not read future observations; a plausible explanation does not prove causality.
- **Compliance**: Pseudonymization does not guarantee the absence of personal data. The AI Act sanctions are specified from articles 99 and 101 consulted on the Commission's website, with distinction of plans.

### Validation scope

A card comparison with `218570f` checks **all questions, IDs and card order**, as well as the presence of at least one modified answer in each card. The number of cards, the 354 put in situation and the 182 confusion cards remain unchanged.

Readability controls keep the limits of 110 words per standard response and 140 per situation. The repository commands check format, links, plugin reading, catalogs, tests and Anki export; thematic PRs pass CI before merging.

Final Local Validation 6 November: `make check` successful, **54 Tests**, ruff and mypy without error, without warning, Synchronized catalogs and export of **2,186 active cards and 71 Withdrawn**. Additional targeted verifications cover FLOPs/GPU- hours, the cost per success, the probabilities, on the `LEFT JOIN`, the classification of deletions and the average with zero values.

This pass is a targeted re-reading of the rich answers, **not a comprehensive certification of the 2,186 cards or all the API cited**. The library checks reported in the historical balance sheet above have not all been repeated. The global dates `Verified on` are not advanced; the new ad hoc consultations are identified in the sources concerned. The local configurations MCP and VS Code remain out of publication.

## Second cross-pass — 6 November 2026

This continuation deepens **an answer in each of the 147 cards**, compared to `07df340`, starting point after the first six PRs. It includes **146 answers hitherto unchanged since `218570f`**, and a new complement to the single map of the container index, already enriched.

The accumulation is therefore modified **682 distinct answers**, and not 683: `536 + 146`. The 147 answers of this second pass include **141 standard cards and 6 situationalized**. No cards are added, deleted or moved; questions and identifiers remain the same.

### Educational contributions

- **Distinguish mechanism and warranty**: proposed or executed tool call, checkpoint and external effect, signature and trust, HTTP 200 and service actually rendered.
- **Making trade-offs measurable**: cost-per-success calculations, entry cost with cache, free/realized load, MAE/RMSE, SHAP log-odds, and multiple comparisons.
- **Specify technical assumptions**: total memory of a MoE, partitioned FSDP states, context actually used, cache metric units and order of sampling filters.
- **Strengthen production cases**: approval out of date, remote effect successful before local outage, tombstone expired before backfill, unmature labels and judge drift.
- **Correct misleading simplifications**: a Pod is not entirely immutable; an IFS can be distributed by OCI registry via ORAS without becoming a Docker image; GGUF imposes neither CPU nor single file; an SSE reconnection does not guarantee the resumption of the flow; the human agreement is not a universal evaluation ceiling.

| Lot | Sections | topics / answers |
| --- | --- | ---: |
| Prompts, RAG, agents and workflows | 10, 20, 30, 40 | 32 |
| Models, Execution, Infrastructure, Multimodal and ML | 50, 60, 70, 80, 130, 160, 170 | 58 |
| Quality, operation, product and data | 90, 100, 110, 120, 140, 150 | 57 |

### Verifications and Limitations

The comparison with `07df340` controls **exactly one modified answer per record**, all questions, IDs, order and total of **2,186 cards**. The comparison with `218570f` confirms the accumulation of 682 distinct answers. The 354 situationalized and 182 confusion cards remain present.

The lint does not report any errors or warnings: standard maps remain under 110 words and scenarios under 140. The added calculations have been verified in standard Python, including the retention of the distribution of the speculative sampling, probability conversions, costs, SLI and dependencies of a seven-day window.

The primary focus is on **Cognee routing, Kubernetes Pod updates, SIF publishing with Apptainer, article 22 of the GDPR and the scope of the AI Act**. The links and scope of the consultation are added to the relevant topics. This is not a re-verification of all versions, libraries or regulatory provisions of the Vault; the overall dates of the topics remain unchanged.

Final local validation: **`make check` passed, 54 tests**, ruff and mypy error-free, catalogs and workshops validated. **`make export` passed**; package database inspection: 2,257 notes, all active 2,186 identifiers present, and exactly 71 cards removed suspended.

Examples of calculation are illustrative, with fictitious rates when they relate to an invoice; the Examples ofAPI, of GPU Not all of them were executed in a real-world environment. Local configurations MCP/VS Code is not modified or published.
