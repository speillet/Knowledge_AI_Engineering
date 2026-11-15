# Enrichment and relevance of — 12 topics November 2026

The 147 topics remain relevant for learning how to design, evaluate and operate AI systems. The foundation is not limited to the LLM: ML validation, temporality of data, transactions and exploitation explain a large part of the errors encountered in production. The topics on frameworks, protocols and specialized infrastructures are deepenings to choose according to the projects; learning them all before practicing is not a prerequisite.

This pass adds **147 cards**, one in each card, including **15 calculations**, and corrects or specifies **10 existing answers**. The value goes from **2,186 to 2,333 cards**, again in 17 sections. The added answers represent **12,493 words**; each contains between 74 and 95 words.

## Audit Methodology and Scope

The starting point is the remote version `2a0f84e`, which already contains the enrichments of early November. The inventory of 2,186 questions and answers was used to select the complements; the reading and the confrontation at the sources are targeted on the added notions, the close answers and the sensitive affirmations. It is not a reverification line by line of all the historical affirmations of the vault.

The additions favour an autonomous question, a direct answer, an explained mechanism and a limit of application. The numerical examples are pedagogic, with their hypotheses; they are neither current prices nor material benchmarks. A lexical comparison between additions and previous answers, followed by a review of the close results, led to reorient **11 proposals** to avoid redefining concepts already covered.

The existing **2,186 Anki IDs and related questions are retained**. The only new identities are those of the new 147 cards. The summaries of 146 cards are completed, then the catalog is regenerated; the container index retains its particular format. The global dates `Verified on` are not renewed by a simple targeted consultation: the new sources indicate the perimeter of this consultation.

## Coverage and interest in additions

| Section | Added cards | Additions to this pass |
| --- | ---: | --- |
| Prompt engineering | 3 | Metamorphic tests, critical optimization constraints, migration of the output contract. |
| RAG | 8 | Diagnostic with reference evidence, RRF, provenance, memory reversibility, overlap, SQL sampling, revocation and source independence. |
| Agents | 9 | Observable task completion, proposal and execution, MCP compatibility, negative tests, compaction, critical path, framework selection, quotas, and inferred memory. |
| Automation and frameworks | 12 | Deterministic replay, denial of authorization, effects after guardrail, webhooks, structured messages, budgets, approvals and independent tests. |
| Fine-tuning | 6 | Free generation, biased preferences, synthetic deduplication, parallel efficiency, isolation of episodes and comparability of losses. |
| Inference | 12 | Rafals, KV bookings, marginal cost, physical sharing, prefill equity, structured unknowns, full duration and cache isolation. |
| Containers and infrastructure | 14 | Real startup, OCI platforms, secrets, fault location, probes, permissions, VRAM, topology, atomic weights and drainage. |
| API and routing | 5 | Invoice reconciliation, cascade cost, timeouts, SSE reconnection and A2A cancellation. |
| Observability and assessments | 13 | Verifiable assertions, asynchronous traces, protected testing, fault injection, sampling, judge bias, external effects and sequential testing. |
| Security | 6 | False positives, trapped tool results, accurate approval, SSRF, attestations and test code rights. |
| MLOps | 7 | Release manifest, schema rollback, late labels, task stability, revocation, RTO/RPO and concurrent promotions. |
| Costs | 3 | Net cache economy, in-flight call booking and false semantic equivalents. |
| Fundamentals LLM | 8 | Attention and explanation, truncation, cosine/L2, ex æquo ANN, extrapolation, experts by batch, multiple proofs and reasoning performance. |
| System design and product | 11 | Outbox delay, uncertain submission, error cost, circuit breaker, applicable proof, local correction, human capacity and Pareto border. |
| Data and compliance | 17 | Weighted averages, deterministic SQL, pushdown, concurrent publishing, flow state, skew, data removal, and semantic contracts. |
| Multimodal and Edge | 5 | Resolution and proof, board units, audio interruption, thermal regime and modified screen before click. |
| ML Classic | 8 | Unknown Categories, Balanced Accuracy, CEE, Conditional Recall, MAPE, Alert Quotas, Explanation Stability, and Causal Interference. |

Container and HPC topics remain relevant for self-hosted inference. They are optional for a product that consumes only one API. On the contrary, classic ML topics and data forms a useful basis even when a LLM makes the final decision. Framework names help to locate the examples; their guarantees must remain verified on the version used.

## Corrected or clarified existing responses

| Topic | Correction |
| --- | --- |
| [MCP](../30-agents/33-mcp.md) | Example of an explicitly fictitious and host-specific configuration; removal of an example of a third-party package whose version is not established by the specification. |
| [containerd and runc](../70-containers-infra/03-containerd-runc.md) | crun is no longer presented as universally faster or as the guaranteed default of all quoted distributions. |
| [Linux primitives](../70-containers-infra/08-linux-primitives-docker-fundamentals.md) | Performance of storage-dependent volumes and layers; weight in the image presented as a possible compromise. |
| [Embeddings](../130-llm-fundamentals/133-embeddings-representations.md) | Cosine equivalency, scalar product and L2 conditioned to normalization; removal of a general speed superiority. |
| [Parsing of documents](../160-multimodal-edge/162-document-parsing.md) | Mixed PDF and scans already OCRized; a threshold of characters is not enough to decide on an OCR or to validate the text. |
| [Local LLM](../160-multimodal-edge/164-local-edge-llm.md) | Three revised answers: bandwidth quotient presented as a simplified terminal, GGUF not limited to quantified weights or a single file, `-ngl` offload and comparison of explicitly conditional machines. |
| [AI Act](../150-data-compliance/155-ai-act.md) | Aggregation of the results does not erase an inference of forbidden emotions upstream; another collection must be studied without reintroducing this function. |
| [Agentic protocols](../80-api-layer-routing/85-agentic-protocols-map.md) | Open governance distinguished from the guarantees of security, compatibility and durability of an implementation. |

## Points facing primary sources

- **MCP**: The [compatibility of review 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28/basic/versioning) distinguishes between modern queries and historical clients. The [Good Safety Practices](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices) covers SSRF and authorization. There is no need to replace this review with an old one simply because it is more familiar.
- **AI Act and GDPR** : [Calendar published by the Commission](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai) confirms the high-risk maturities already mentioned in the vault, of which December 2027 and August 2028. The qualification depends on the[article 6](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-6) ; the[article 5](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-5) The ban on inferring emotions at work. The purposes and legal bases remain to be examined according to the [RGPD](https://eur-lex.europa.eu/eli/reg/2016/679/oj/fra), Especially his articles 5 to 7 and 13.
- **Execution of agents**: the [Functional API of LangGraph](https://docs.langchain.com/oss/python/langgraph/functional-api) documents replay and non-deterministic operations; the [interruptions](https://docs.langchain.com/oss/python/langgraph/interrupts) requests a consistent order. The [CrewAI Task Guardrails](https://docs.crewai.com/en/concepts/tasks) is about output and retrievals; the separation of business effects is an architecture recommendation built from this behavior.
- **Serving**: vLLM documents the [KV Block Sharing](https://docs.vllm.ai/en/latest/design/prefix_caching/) and [secret cache salt by trusted perimeter](https://docs.vllm.ai/en/latest/usage/security/). The official [OpenAI on structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs) documentation distinguishes schema compliance, denial, and incomplete response. The [Specification A2A](https://a2a-protocol.org/latest/specification/) does not guarantee that a cancellation request will succeed.
- **Infrastructure** : [Kubernetes life cycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/) distinguishes the three probes. The[index OCI](https://github.com/opencontainers/image-spec/blob/main/image-index.md) Reference to separate platforms. Docker documentations explain the [Secrets of Build](https://docs.docker.com/build/building/secrets/) and the [Storage Drivers](https://docs.docker.com/engine/storage/drivers/). The performance of an [runtime such as crun](https://github.com/containers/crun) It remains to be measured on the target.
- **Documents and local**: PyMuPDF exposes a [Full or partial OCR](https://pymupdf.readthedocs.io/en/latest/ocr/index.html); the [llama.cpp server options](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md) renders the offload configurable. The details of this review are not measurements on a GPU or a physical device.
- **ML measurements**: [Scikit - Learn](https://scikit-learn.org/stable/modules/model_evaluation.html), [calibration](https://scikit-learn.org/stable/modules/calibration.html) and [Evaluation of forecasts](https://otexts.com/fpp3/toolbox.html) chapter support metric distinctions. Numerical examples are recalculated separately.

The added sources are identified checkpoints. They do not constitute a legal certification, a security audit of the code of the cited products or a validation of all their versions. The decision cards propose reasonings and experiments to conduct, not universal guarantees derived from a supplier.

## Validation

- Lint before modification: **147 cards, 2,186 cards, zero error and zero warning**.
- Lint after modification: **147 cards, 2,333 cards, zero error and zero warning**.
- Comparison by identifiers: **2,186 historical cards retained**, questions unchanged, **10 answers modified**, **147 cards added**; no cards removed.
- Recalculation of **15 new years**: assumptions, units and controlled results, including 8.78 s for 400 tokens, 18 € weighted average, 3.6 million state inputs and 60% final recall.
- `make check`: lint, catalog synchronization, ruff, mypy, **54 tests** and two successful local workshops with Python 3.13.
- `make export`: generating the Anki package and controlling its identifiers and number of notes.
- `git diff --check`: no spacing error.

Structure and export tests protect the use in Obsidian and Anki; they do not prove the accuracy of the content. Actual model calls, GPU loads, and business services are not executed in this document pass. CI checks on Python versions of the repository complete local validation before merging.

To review the add-ins, start with those that correspond to a problem encountered in a project, and then apply a calculation or diagnostic card on a real case. The [Learning Guide](learning-with-flashcards.md) remains the entry point to avoid confusing card volume and practical mastery.
