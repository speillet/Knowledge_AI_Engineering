# Enrichment of existing plugs — 14 November 2026

The existing **150 cards** are enriched, in the 17 sections. The value changes from **2,440 to 2,711 cards**: **271 additions**, of which **23 calculations**, and **18 in-depth or corrected existing answers**. The previous 2,440 questions and IDs are retained; no existing cards are removed.

The work starts from `main` to commit `a744073`, after recovering the nine missing commits. It deepens the content of the topics without creating a new thematic topic. The README and the entry points are updated; the historical tracks keep their balance topics dated.

## Educational choices

Additions include mechanisms, computational assumptions, counter-examples, and diagnostic criteria. Examples include the limits of a reranker, the open world of a graph, streamed tool arguments, KV cache fragmentation, speculative tokens expectation, write preconditions, selection bias, and feature availability time.

The review ruled out **29 proposals that covered maps already present**. The notions already well explained are not redefined under a new identity. SQL and response evaluation cards are deepened directly in their reference maps; others receive both additions and clarifications.

The calculation rectos indicate data, units and assumptions. The rates are assumptions of exercise, not current supplier prices. The answers explain the interpretation and the limits, remaining below the thresholds of the deposit. An additional situationalization completes the index of the containers; the value now counts **364 situationalization** and **201 cards "not to be confused"**.

## Distribution

| Section | Sheets | Cards before | Cards after | Ajouts |
| --- | ---: | ---: | ---: | ---: |
| 10-prompt-engineering | 3 | 43 | 47 | +4 |
| 20-rag | 8 | 121 | 136 | +15 |
| 30-agents | 9 | 140 | 156 | +16 |
| 40-automation | 12 | 185 | 209 | +24 |
| 50-fine-tuning | 6 | 90 | 102 | +12 |
| 60-llm-inference | 13 | 249 | 273 | +24 |
| 70-containers-infra | 14 | 164 | 191 | +27 |
| 80-api-layer-routing | 5 | 67 | 77 | +10 |
| 90-observability-evals | 13 | 224 | 246 | +22 |
| 100-security-guardrails | 6 | 120 | 132 | +12 |
| 110-mlops-cicd | 9 | 196 | 213 | +17 |
| 120-costs-finops | 3 | 49 | 55 | +6 |
| 130-llm-fundamentals | 8 | 122 | 134 | +12 |
| 140-system-design-product | 11 | 187 | 208 | +21 |
| 150-data-compliance | 17 | 279 | 307 | +28 |
| 160-multimodal-edge | 5 | 71 | 80 | +9 |
| 170-classical-ml | 8 | 133 | 145 | +12 |
| **Total** | **150** | **2,440** | **2,711** | **+271** |

## Corrections and deepening of existing responses

**reranking** is no longer presented as a guaranteed improvement in accuracy: the example distinguishes candidate selection, reclassification and final quality. **caching** reuses still valid and authorized work; a change in the prompt can leave a partially reusable prefix. The cache does not remove all the prefill nor the suffix calculation. Hit metrics do not replace net economy and quality.

The SQL examples specify the ex-æquo of ROWS/RANGE and show why `WHERE ... OR id IS NULL` does not always replace a filter in `ON`. Numerical evaluation explains a possible combination of absolute and relative tolerances. The other answers gain an example, a limit or a targeted check.

- [12-automatic-prompt-optimization](../10-prompt-engineering/12-automatic-prompt-optimization.md) — Why can optimizing a quick on average degrade a critical business case?
- [123-aggressive-caching](../120-costs-finops/123-aggressive-caching.md) — What is aggressive caching for a LLM application?
- [123-aggressive-caching](../120-costs-finops/123-aggressive-caching.md) — Why do agents benefit so much from prompt caching?
- [123-aggressive-caching](../120-costs-finops/123-aggressive-caching.md) — What silently invalidates the prefix cache of a LLM?
- [132-tokenization](../130-llm-fundamentals/132-tokenization.md) — What is a token?
- [138-reasoning-models](../130-llm-fundamentals/138-reasoning-models.md) — Why does not increasing the reasoning budget guarantee an improvement on each task?
- [150-011-analytical-sql-transformations](../150-data-compliance/150-011-analytical-sql-transformations.md) — Why can a WHERE filter on the right table change the direction of a LEFT JOIN?
- [150-011-analytical-sql-transformations](../150-data-compliance/150-011-analytical-sql-transformations.md) — Not to be confused: ROWS frame and RANGE frame in an SQL window?
- [153-data-flywheel-versioning](../150-data-compliance/153-data-flywheel-versioning.md) — How to prioritize improvements from flywheel?
- [163-real-time-voice](../160-multimodal-edge/163-real-time-voice.md) — Why is WER not enough to evaluate the transcription of a voice agent?
- [172-ml-validation-metrics](../170-classical-ml/172-ml-validation-metrics.md) — Why learn imputation and variable selection inside each fold?
- [22-advanced-rag](../20-rag/22-advanced-rag.md) — What is reranking?
- [39-agent-memory](../30-agents/39-agent-memory.md) — Why shouldn't a user's silence become a permanent fact in an agent's memory?
- [60-013-prefill-decode-step-by-step](../60-llm-inference/60-013-prefill-decode-step-by-step.md) — Where does the very first token output come from after the prefill?
- [90-010-llm-response-evaluation](../90-observability-evals/90-010-llm-response-evaluation.md) — What to check in a digital response of a LLM?
- [90-010-llm-response-evaluation](../90-observability-evals/90-010-llm-response-evaluation.md) — Why can an average score hide an unacceptable response?
- [90-012-langfuse-prompts-experiments](../90-observability-evals/90-012-langfuse-prompts-experiments.md) — Why distinguish zero score, absent score and reviewer error in Langfuse?
- [96-evals-rag-agents](../90-observability-evals/96-evals-rag-agents.md) — How to test that a RAG actually uses the provided context?

## Primary sources consulted

**45 references** are attached to the files with the date and the subject of the add-in. The sources are used to verify the mechanisms indicated below; the encrypted examples and diagnostic procedures are pedagogical constructs. The design implications are not presented as guaranteed functionalities of a framework.

| Files concerned | Checkpoint | Reference |
| --- | --- | --- |
| 11-advanced-prompt-engineering, 35-context-engineering, 137-long-context | Position and context selection | [Liu et al. — Lost in the Middle](https://arxiv.org/abs/2307.03172) |
| 22-advanced-rag | Diversification by MMR | [Carbonell and Goldstein — MMR](https://www.cs.cmu.edu/~jgc/publication/The_Use_MMR_Diversity_Based_LTMIR_1998.pdf) |
| 23-knowledge-graphs-ontologies | Open world and assertions | [W3C — OWL 2 Primer](https://www.w3.org/TR/owl2-primer/) |
| 26-text-to-sql | Joints, cardinalities and aggregations | [PostgreSQL 18 — table expressions](https://www.postgresql.org/docs/18/queries-table-expressions.html) |
| 33-mcp, 104-mcp-skills-security | Identity and borders of trust MCP | [MCP — Security Practices 2026-07-28](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices) |
| 42-langchain-fundamentals | Fragments of tool calls | [LangChain — models and streaming](https://docs.langchain.com/oss/python/langchain/models) |
| 44-langgraph-fundamentals | State and Reducers | [LangGraph — Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api) |
| 45-langgraph-production, 40-011-langgraph-recovery-concurrency | Checkpoints and Persistent Memory | [LangGraph — persistence](https://docs.langchain.com/oss/python/langgraph/persistence) |
| 46-crewai-crews | Contracts and context of tasks | [CrewAI — Tasks, v1.15.41](https://docs.crewai.com/v1.15.41/en/concepts/tasks) |
| 47-crewai-flows | Flow Status and Routing | [CrewAI — Flows, v1.15.41](https://docs.crewai.com/v1.15.41/en/concepts/flows) |
| 51-fine-tuning-adaptation | Masking supervised tokens | [Hugging Face TRL — SFT Trainer](https://huggingface.co/docs/trl/sft_trainer) |
| 52-post-training-alignment | DPO Conditional Comparisons | [Rafailov et al. — DPO](https://arxiv.org/abs/2305.18290) |
| 54-distributed-training | Synchronisation DDP | [PyTorch 2.15 — DDP](https://docs.pytorch.org/docs/2.15/notes/ddp.html) |
| 56-training-optimization-diagnostics | Unscale before clipping | [PyTorch 2.15 — AMP examples](https://docs.pytorch.org/docs/2.15/notes/amp_examples.html) |
| 62-inference-optimizations | Intermediate memory and dense attention | [Dao et al. — FlashAttention](https://arxiv.org/abs/2205.14135) |
| 66-prefix-caching-radix-attention, 123-aggressive-caching | Complete blocks, divergence and cache identity | [vLLM — Automatic Prefix Caching](https://docs.vllm.ai/en/latest/design/prefix_caching/) |
| 67-speculative-decoding | tokens validated per cycle | [Leviathan et al — Speculative Decoding](https://arxiv.org/abs/2211.17192) |
| 69-roofline-prefill-decode | Calculation and bandwidth limits | [NVIDIA — GPU Performance Background](https://docs.nvidia.com/deeplearning/performance/dl-performance-gpu-background/index.html) |
| 01-oci | Manifests, configuration and layers | [OCI — Image Manifest](https://github.com/opencontainers/image-spec/blob/main/manifest.md) |
| 02-docker-images-registries | Invalidation of the build cache | [Docker — Build cache invalidation](https://docs.docker.com/build/cache/invalidation/) |
| 04-kubernetes-kubelet-cri | End of Pods | [Kubernetes — Pod Lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/) |
| 04-kubernetes-kubelet-cri | Eviction under pressure of resources | [Kubernetes — Node-pressure Eviction](https://kubernetes.io/docs/concepts/scheduling-eviction/node-pressure-eviction/) |
| 06-apptainer-singularity | Host mounts and dependencies | [Apptainer — Bind Paths and Mounts](https://apptainer.org/docs/user/latest/bind_paths_and_mounts.html) |
| 09-gpu-containers | Diagnostic of GPU path in container | [NVIDIA — Container Toolkit troubleshooting](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/troubleshooting.html) |
| 142-llm-reliability-resilience | Semantics of HTTP errors | [IETF — RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html) |
| 91-langfuse-observability | Trace sampling and coverage limits | [Langfuse — Sampling](https://langfuse.com/docs/observability/features/sampling) |
| 93-monitoring-inference | Alerts and user impact | [Google SRE — Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/) |
| 103-agent-defenses | Control of network destinations | [OWASP — SSRF](https://community.owasp.org/attacks/Server_Side_Request_Forgery) |
| 105-agentic-ai-devsecops | Origin of Artifacts | [SLSA v1.2 — Provenance](https://slsa.dev/spec/v1.2/provenance) |
| 118-ml-artifacts-registry-releases | Alias and model versions | [MLflow — Model Registry Workflows](https://mlflow.org/docs/latest/ml/model-registry/workflow/) |
| 131-transformer-architecture | Attention and Causal Mask | [Vaswani et al. — Attention Is All You Need](https://arxiv.org/abs/1706.03762) |
| 136-mixture-of-experts | Routing and costs of experts | [Fedus et al — Switch Transformers](https://arxiv.org/abs/2101.03961) |
| 150-011-analytical-sql-transformations | ROWS/RANGE frameworks and aggregations | [PostgreSQL 18 — Value Expressions](https://www.postgresql.org/docs/18/sql-expressions.html) |
| 150-012-columnar-storage-lakehouse | Physical Organization Parquet | [Apache Parquet — File Format](https://parquet.apache.org/docs/file-format/) |
| 150-012-columnar-storage-lakehouse | Snapshots and isolation of readings | [Apache Iceberg — Reliability](https://iceberg.apache.org/docs/latest/reliability/) |
| 150-014-streaming-event-processing | Event time and watermarks | [Apache Flink — Timely Stream Processing](https://nightlies.apache.org/flink/flink-docs-stable/docs/concepts/time/) |
| 159-temporal-data-features | Temporal attachment of features | [Feast — Point-in-time joins](https://docs.feast.dev/getting-started/concepts/point-in-time-joins) |
| 154-gdpr-llm | Purposes, conservation and rights; restoration procedures are design implications | [CNIL — AI and GDPR](https://www.cnil.fr/fr/intelligence-artificielle/ia-comment-etre-en-conformite-avec-le-rgpd) |
| 155-ai-act | Change of purpose and responsibilities | [European Commission — Article 25](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-25) |
| 172-ml-validation-metrics | Adjusted pretreatment in folds | [scikit-learn — Common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html) |
| 172-ml-validation-metrics | Macro and micro averages | [scikit-learn — Metrics and scoring](https://scikit-learn.org/stable/modules/model_evaluation.html) |
| 173-calibration-uncertainty-abstention | Calibration and validation populations | [scikit-learn — Probability calibration](https://scikit-learn.org/stable/modules/calibration.html) |
| 173-calibration-uncertainty-abstention | Marginal scope of guarantees | [Angelopoulos and Bates — Conformal Prediction](https://arxiv.org/abs/2107.07511) |
| 175-time-series-forecasting | Evaluation of forecasts and horizons | [Hyndman and Athanasopoulos — Forecasting, Chapter 5](https://otexts.com/fpp3/toolbox.html) |
| 150-014-streaming-event-processing | Inactive sheet music and minimal watermark | [Apache Flink — Generating Watermarks](https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/datastream/event-time/generating_watermarks/) |

The `Verified on` global dates remain **strictly identical** to those of the database: a targeted check does not renew an entire topic. This pass does not certify each historical statement, all benchmarks, prices, CVE or regulatory calendars. The `latest` references can evolve; an implementation must use the documentation of its version. No GPU cluster, cloud service, LLM provider or real agent framework has been validated.

## Delivery verifications

- `make check` in a Python 3.10 environment isolated with the dependencies of the repository: lint of files, catalogs, ruff, mypy, **54 tests** and the two integrated successful workshops.
- Lint: **0 error, 0 warning**; no new response beyond length limits.
- Comparison with `a744073`: **150 modified cards**, **2,440 questions and retained identifiers**, **18 existing answers changed**, **271 new cards**, global dates unchanged.
- **24 arithmetic controls** and execution of the SQL join counter-example: compliant results. Assumptions from other exercises have been reread.
- `make export`, then SQLite inspection of the package: **2,711 active cards** with exactly the Vault IDs, and **71 removed cards still suspended**.
- `git diff --check`: no spacing error. Untracked local configurations remain out of delivery.

The PR CI must confirm the controls in Python 3.10 and 3.12 before merging. Publishing the Anki package to `main` remains ensured by the existing workflow. The automatic controls verify structure and technical consistency; they do not alone demonstrate the truth of each explanation.
