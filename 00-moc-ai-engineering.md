# AI Engineering — MOC
Tags: #moc #ai-engineering

Root Map of the Vault: Key Knowledge **AI Engineering**, from the use of models to their industrialization.
Each domain has its flashcard notes linked together via `## Connections`.
Each topic ends with **situation**: to review only them, look for `Scenario:` in the vault.

To get started, consult the [Learning Guide](docs/learning-with-flashcards.md): eight steps with prerequisites, response criteria, Anki notation and transition to practical exercises. The [Review of 9 October](docs/learning-review-2026-10-09.md) explains the background corrections and pedagogical additions.

To apply the metrics, the [Local AI Decision Workshop](examples/ai-decisions/README.md) links ML validation, calibration, model selection and document quality; the [Review of 11 October](docs/relevance-review-2026-10-11.md) specifies the enrichments and their perimeter.

To build verifiable evidence, the [atelier RAG local](examples/verifiable-rag/README.md) compares two policies out of ten fictitious cases: rights, effective dates, conflicts, withdrawal and abstention. Study [[22-advanced-rag|Advanced Search]], [[20-010-rag-permissions-versions|Rights and Versions]], then [[96-evals-rag-agents|the RAG Assessment]]; produce a statement/proof table and a reproducible report.

To understand how to execute a LLM query, the [prefill, RadixAttention and speculative decoding](docs/understanding-prefill-radix-speculation-2026-11-12.md) tracks the calculated states, shared branches, and verified tokens. It completes the topics with a continuous example and detailed calculations.

The [Transversal Review of November 12, 2026](docs/cross-topic-review-2026-11-12.md) presents the 147 in-depths, corrections, and limitations of source verification.

To industrialize a predictive model, the [MLOps route from end to end](docs/production-mlops-learning-path-2026-11-12.md) links data, training, inference package, promotion, scoring and recovery. It completes [[117-continuous-training-pipelines|The Pipelines]] with [[118-ml-artifacts-registry-releases|The releases]] and [[119-prediction-contracts-features-batch|the Prediction Contracts]].

The [Current affairs audit of 13 November 2026](docs/reference-currency-check-2026-11-13.md) distinguishes between confirmed references and corrections on managed services, MCP, OWASP and AI Act; it does not constitute a certification of all information of the vault.

The [Enrichment of November 14, 2026](docs/topic-expansion-2026-11-14.md) deepens the existing 150 cards: 271 new cards, 18 revised answers, encrypted examples and diagnostics, with retention of review IDs.

## Reading route
Recommended progression: **understand → models use → build → architectures adapt → serve & deploy → industrialize → govern → design systems.**
- **Predictive base**: [[171-ml-model-selection|ML Classic]] then [[172-ml-validation-metrics|validation and metrics]] — choose an approach before building a LLM chain

0. [[131-transformer-architecture|Fundamentals LLM]] — understand what we use (prerequisites)
1. [[11-advanced-prompt-engineering|Prompt engineering]] — talk to models
2. [[21-rag-fundamentals|RAG]] — increase them with knowledge
3. [[31-agent-fundamentals|Agents]] — give them hands
4. [[41-code-nocode-automation|Automation & frameworks d'agents]] — workflows, LangChain, LangGraph, CrewAI
5. [[51-fine-tuning-adaptation|Fine-tuning]] — adapt the model itself
6. [[61-kv-cache-attention|Inference]] — understand the serving
7. [[00-index|Containers & infra]] — deploy to GPU
8. [[81-litellm-api-layer|API layer & routing]] — industrialize access
9. [[91-langfuse-observability|Observability & evals]] — tout mesurer
10. [[101-llm-security-guardrails|Security]] — all protect
11. [[111-mlops-llmops-fundamentals|MLOps & CI/CD]] — continuous delivery
12. [[121-inference-costs|Costs & FinOps]] — master the economy
13. [[151-data-curation-annotation|Data & Compliance]] — data, GDPR, AI Act; then [[157-data-contracts-quality|contrats]], [[158-ingestion-cdc-backfills|ingestion]] and [[159-temporal-data-features|variables temporelles]]
14. [[161-vision-language-models|Multimodal & edge]] — images, documents, voice, local
15. [[141-system-design-llm|System design & product]] — all assemble (senior level)

### Course AI Agent Engineer
To focus on agents, through the sections:
1. [[31-agent-fundamentals|Agents]] then [[48-agentic-workflow-patterns|Patterns of workflows]] — workflow or agent
2. [[32-tool-calling|Tool calling]], [[33-mcp|MCP]] and [[85-agentic-protocols-map|Map of Protocols]] — connect agent to world
3. [[35-context-engineering|Context engineering]] and [[39-agent-memory|Memory]] — what the agent knows about each turn
4. [[36-agent-orchestration|Multi-agents]], [[27-search-agents-deep-research|Research Officers]] and [[49-coding-agents|Code Agents]] — large use cases
5. [[96-evals-rag-agents|Evaluate]] then [[98-agent-debugging|Debug]] an agent; measure its [[90-014-agent-skill-evaluation|skills]] and run it on [[90-016-harbor-agent-evaluation|Harbor]] tasks
6. [[102-agent-threats|Menaces]] and [[103-agent-defenses|Defenses]] — secure
7. [[84-streaming-application-integration|Application Integration]] and [[38-agent-platforms|Platforms]] — put into production
8. [[115-agent-platforms-governance|Governance]] and [[55-agentic-rl|Agentic RL]] — Senior

### Implement and validate an agent platform

Follow the [Complete practical guide](docs/platform-agents-inference-learning-path.md) on the same support agent. The steps are validated by deliverables and observable results:

1. **Set success** with [[141-system-design-llm|System design]] and [[94-evals-methodology|Evaluation methodology]]: task, baseline, constraints and acceptance criteria.
2. **Assign responsibilities** with [[38-agent-platforms|Platforms]] and [[115-agent-platforms-governance|Architecture and governance]]: API, runtime, status, LLM gateway and tools.
3. **Qualify API and Model** contracts with [[81-litellm-api-layer|Gateway LLM]], [[84-streaming-application-integration|Streaming]], and [[63-guided-generation|Structured Outputs]]: Real-world capabilities, errors, and backup.
4. **Make execution reliable** with [[32-tool-calling|Tool calling]], [[103-agent-defenses|Defensive Architecture]] and [[149-delivery-idempotency-concurrency|Idempotence]]: permissions, budgets, concurrency and trade-ins.
5. **Check answers and business result** with [[90-010-llm-response-evaluation|Evaluation of responses]], [[96-evals-rag-agents|Evaluation of Agents]] and [[114-reproducibility-variance|Reproducibility]]: grid, completeness, final state and variance.
6. **Observe end-to-end** with [[93-monitoring-inference|Monitoring]] and [[64-inference-metrics-slo|Metrics and SLO]]: traces, populations, deadlines and cost per compliant task.
7. **Measure and size** with [[60-010-inference-load-benchmarks|Benchmarks]], [[60-011-inference-capacity-scheduling|Capacity]] and [[60-012-inference-optimization-method|Optimisation]]: calls per task, actual load, queues and reserve.
8. **Deploy and resume** with [[60-014-inference-parity-validation|Inference parity]], [[142-llm-reliability-resilience|Resilience]], [[112-model-cicd|CI/CD]] and [[116-ai-sre-incidents-capacity|SRE]]: serving stack parity, crash tests, canary, rollback and runbook.

### Build and operate an agentic application

After the basics of the agentic path:
1. [[140-011-agentic-application-architecture|Defining the life cycle]] — API, identity, status, approvals and cancellation.
2. [[40-010-langchain-tools-middleware-production|Making contracts more reliable LangChain]] — tools, middleware, errors and budgets.
3. [[40-011-langgraph-recovery-concurrency|Approfondir LangGraph]] or [[40-012-crewai-reliable-execution|CrewAI]] — recovery, dependencies, concurrency and evolution.
4. [[90-011-langfuse-instrumentation-production|Instrumenting with Langfuse]] — business events, models, tools and propagation.
5. [[90-012-langfuse-prompts-experiments|Compare prompts and experiences]] — versions, games, scores and promotion.
6. [[90-013-agent-testing-recovery|Demonstrate Invariants]] — tool tests, crash, obsolete decisions and migrations.

The [Audit of Coverage](docs/agentic-stack-audit-2026-10-09.md) specifies inputs and limits. The [atelier support](examples/agentic-support/README.md) provides a local project with recovery tests; the CrewAI variant and remote integrations are complementary exercises.

### Senior Foundations Course
To link the three cross-cutting priorities to AI applications:
1. [[171-ml-model-selection|Choose an approach]] then [[172-ml-validation-metrics|Validate without leakage]] — rules, classic ML or LLM
2. [[157-data-contracts-quality|Defining contracts]], [[158-ingestion-cdc-backfills|reliability of ingestion]] then [[159-temporal-data-features|Rebuild the available data]] — quality and temporality
3. [[149-delivery-idempotency-concurrency|Controlling delivery and concurrency]] then [[140-010-transactions-outbox-sagas|orchestrate transactions]] — safe business effects despite outages

### Cross-links
- [[38-agent-platforms|Platforms]] → [[115-agent-platforms-governance|Architecture and Governance]]
- [[165-computer-use-browser-agents|Agents d’interface]]: multimodal supplement of the agentic journey.

### Data engineering journey for AI

1. **Define data** with [[150-010-analytical-data-modeling|Analytical modelling]], [[150-011-analytical-sql-transformations|SQL]] and [[157-data-contracts-quality|Contrats]]: grain, keys, joins, nulls and invariants.
2. **Collect and rebuild** with [[158-ingestion-cdc-backfills|Ingestion, CDC & backfills]] and [[159-temporal-data-features|Variables temporelles]]: pagination, versions, deletions and actual availability.
3. **Stocker and publish** with [[150-012-columnar-storage-lakehouse|Stockage & lakehouse]] and [[150-013-data-pipeline-orchestration|Orchestration data]]: files, snapshots, partitions, dependencies and recovery.
4. **Build corpus** with [[150-017-ai-datasets-corpora|Datasets & corpus IA]], [[151-data-curation-annotation|Curation]] and [[172-ml-validation-metrics|Validation ML]]: manifestos, families, splits, shards and readers.
5. **Operate and govern** with [[150-016-data-observability-lineage|Observability & lineage]], [[152-pii-privacy|Privacy]] and [[116-ai-sre-incidents-capacity|SRE]]: quality, SLO, impact and repair.
6. **Deepen as needed** with [[150-014-streaming-event-processing|Streaming]] and [[150-015-distributed-computing-data-performance|Distributed calculation]]: low latency, state, shuffle, skew and cost.

The [Cover audit and its five workshops](docs/data-engineering-audit-2026-10-09.md) specifies the expected level according to the role. Start with the [atelier SQL local](examples/data-engineering/sql_workshop.py), then demonstrate the resumption of a pipeline and the reconstruction of a dataset. The advanced topics are worked when the constraints of the project justify them.

### Senior practice path
After the foundations, work on these topics on the same project and produce proof for each step:
1. [[99-statistics-experimental-decisions|Deciding with statistics]] — protocol, matched comparison, useful gain interval and threshold
2. [[173-calibration-uncertainty-abstention|Calibrate and know how to abstain]] — reliability curve, cover risk and human load
3. [[56-training-optimization-diagnostics|Diagnosing training]] — micro-lot, train/validation curves, gradients and normalization; further if role includes model adaptation
4. [[116-ai-sre-incidents-capacity|Operate and resume after failure]] — SLO, bounded file, rocking exercise and postmortem
5. [[147-ai-technical-leadership|Make decisions and the team autonomous]] — ADR, Operation Transfer and Verified Correction

The [Relevance assessment and workshops](docs/senior-learning-path-relevance-2026-10-07.md) specifies priorities, deliverables and success criteria. The maps prepare the reasoning; mastery is also demonstrated by building, measuring and explaining the limits of a system.

### Predict, recommend and decide
After [[171-ml-model-selection|The choice of models]], [[172-ml-validation-metrics|Validation]] and [[173-calibration-uncertainty-abstention|Calibration]], choose the topic according to the problem:
- [[174-recommendation-ranking|Recommandation & ranking]] — propose and order elements, with exposure bias and cold start
- [[175-time-series-forecasting|Temporal forecast]] — predict useful horizons with the information actually available
- [[176-anomaly-detection|Detection of anomalies]] — turn atypical score into actionable alert
- [[177-model-explainability|Explainability]] — diagnose a prediction and check what its explanation means
- [[178-causal-inference-decisions|Causal inference]] — estimate what an action changes, with assumptions and limits

The [review of the five new topics](docs/new-ai-skills-2026-10-08.md) specifies their contributions and an exercise for each. These branches complete the course LLM and agents; they work according to the responsibilities of the position concerned.

### MLOps Journey: Train, Deliver and Monitor a Model

The [Threaded Case of Termination](docs/production-mlops-learning-path-2026-11-12.md) offers a deliverable and a passing criterion at each stage.

1. [[111-mlops-llmops-fundamentals|Version and trace]] — artifacts, registry, lineage and environments
2. [[117-continuous-training-pipelines|Automate the training]] — pipeline, data and model validation, aka champion and selective labels
3. [[114-reproducibility-variance|Compare without being wrong]] — variance, run selection, environment and historical evidence
4. [[118-ml-artifacts-registry-releases|Publish a loadable package]] — transformations, URI, output contract, integrity and restore
5. [[119-prediction-contracts-features-batch|Producing actionable predictions]] — features, time availability, freshness, batch idempotent and publication
6. [[112-model-cicd|Deliver gradually]] — eval gates, shadow, canary, GitOps and rollback
7. [[113-monitoring-drift-feedback|Monitor drift and measurement]] — PSI, multivariate drift, label cover and feedback loop
8. [[116-ai-sre-incidents-capacity|Exploit and resume]] then [[115-agent-platforms-governance|Governing the Agentic Systems]] — SLO, dependencies, incidents, liabilities and withdrawal

### Measuring and optimizing the LLM inference

1. **Set criteria** with [[64-inference-metrics-slo|Metrics & SLO]] and then [[93-monitoring-inference|Monitoring]]: Visible experience, joint compliance, errors and histograms.
2. **Measure capacity** with [[60-010-inference-load-benchmarks|Load benchmarks]]: arrivals, caches, saturation and uncertainty.
3. **Dimension** with [[61-kv-cache-attention|KV cache]] and [[60-011-inference-capacity-scheduling|Capacity & scheduling]]: memory, budgets, equity and reserve.
4. **Choose levers** with [[60-012-inference-optimization-method|Optimization process]], [[62-inference-optimizations|Optimizations]], [[67-speculative-decoding|Speculation]] and [[68-quantization|Quantification]].
5. **Validate the decision** with [[121-inference-costs|Costs]], [[112-model-cicd|CI/CD]] and [[116-ai-sre-incidents-capacity|SRE]]: quality, cost-per-success, canary and incidents.

The [Inference Audit of October 8](docs/llm-inference-audit-2026-10-08.md) maps the concepts covered and offers four workshops with deliverables. The gains are demonstrated on a representative load; the calculations of the maps remain pedagogical examples.

<!-- catalog:begin -->

## 10 — Prompt engineering

- [[11-advanced-prompt-engineering|Advanced prompt engineering]]
- [[12-automatic-prompt-optimization|Automatic Prompt Optimization (DSPy)]]
- [[13-production-prompts|Prompts in production]]

## 20 — RAG

- [[21-rag-fundamentals|RAG — Fundamentals]]
- [[22-advanced-rag|RAG Advanced]]
- [[23-knowledge-graphs-ontologies|Knowledge graphs & ontologies]]
- [[24-cognee|Cognee]]
- [[25-chunking-contextual-retrieval|Advanced Chunking & Contextual Retrieval]]
- [[26-text-to-sql|Text-to-SQL & structured data]]
- [[27-search-agents-deep-research|Search agents (deep research)]]
- [[20-010-rag-permissions-versions|RAG in production: rights, versions & abstention]]

## 30 — Agents

- [[31-agent-fundamentals|Basics of]]
- [[32-tool-calling|Tool calling]]
- [[33-mcp|MCP — Model Context Protocol]]
- [[34-harness-plugins|Harness & plugins]]
- [[35-context-engineering|Context engineering]]
- [[36-agent-orchestration|Orchestration multi-agents]]
- [[37-agent-frameworks|Frameworks d'agents]]
- [[38-agent-platforms|Agent Platforms]]
- [[39-agent-memory|Agent Memory]]

## 40 — Automation & agent frameworks

- [[41-code-nocode-automation|Automation code & no-code]]
- [[42-langchain-fundamentals|LangChain — Fundamentals]]
- [[43-langchain-agents|LangChain — Agents & middleware]]
- [[44-langgraph-fundamentals|LangGraph — Fundamentals]]
- [[45-langgraph-production|LangGraph — Production (persistance, HITL, multi-agents)]]
- [[46-crewai-crews|CrewAI — Crews]]
- [[47-crewai-flows|CrewAI — Flows]]
- [[48-agentic-workflow-patterns|Agentic Workflow Patterns]]
- [[49-coding-agents|Code Agents: Usage & Integration]]
- [[40-010-langchain-tools-middleware-production|LangChain — Contracts, tools & middleware in production]]
- [[40-011-langgraph-recovery-concurrency|LangGraph — Recovery, Concurrency & Evolution]]
- [[40-012-crewai-reliable-execution|CrewAI — Reliable Execution & Integration]]

## 50 — Fine-tuning

- [[51-fine-tuning-adaptation|Fine-tuning & adaptation of models]]
- [[52-post-training-alignment|Post-training & alignment]]
- [[53-synthetic-data-distillation|Synthetic data & distillation]]
- [[54-distributed-training|Distributed Training]]
- [[55-agentic-rl|Agentic RL & Training Environments]]
- [[56-training-optimization-diagnostics|Drive Optimization & Diagnostics]]

## 60 — LLM inference

- [[61-kv-cache-attention|KV cache & attention]]
- [[62-inference-optimizations|Inference optimizations]]
- [[63-guided-generation|Guided generation (structured outputs)]]
- [[64-inference-metrics-slo|Inference Metrics & SLO]]
- [[65-probabilities-sampling|Probability & sampling]]
- [[66-prefix-caching-radix-attention|Prefix caching & RadixAttention]]
- [[67-speculative-decoding|Speculative decoding]]
- [[68-quantization|Quantization]]
- [[69-roofline-prefill-decode|Roofline, prefill/decode & disaggregation]]
- [[60-010-inference-load-benchmarks|Charging benchmarks for inference LLM]]
- [[60-011-inference-capacity-scheduling|Inference Capacity & Scheduling LLM]]
- [[60-012-inference-optimization-method|Inference Optimization Approach LLM]]
- [[60-013-prefill-decode-step-by-step|Prefill & decode — Step by Step Execution]]
- [[60-014-inference-parity-validation|Validate an inference deployment: parity & non-regression]]

## 70 — Containers & infrastructure

- [[00-index|Containers & infra — Index]]
- [[01-oci|OCI]]
- [[02-docker-images-registries|Docker, images and registers]]
- [[03-containerd-runc|containerd & runc]]
- [[04-kubernetes-kubelet-cri|Kubernetes, kubelet & CRI]]
- [[05-docker-kubernetes|Docker & Kubernetes]]
- [[06-apptainer-singularity|Apptainer & Singularity]]
- [[07-containers-overview|Containers — Synthesis]]
- [[08-linux-primitives-docker-fundamentals|Primitive Linux & Docker fundamentals]]
- [[09-gpu-containers|GPU in container]]
- [[10-images-models-weights|Images & weights of]]
- [[11-llm-inference-servers|Inference Servers LLM]]
- [[12-kubernetes-gpu-inference|Kubernetes GPU & inference]]
- [[13-apptainer-inference-hpc|Apptainer & Inference HPC]]

## 80 — API layer & routing

- [[81-litellm-api-layer|LiteLLM (API layer)]]
- [[82-routing-llm|Routing LLM]]
- [[83-gateway-ingress|Ingress & API gateway]]
- [[84-streaming-application-integration|Streaming & application integration]]
- [[85-agentic-protocols-map|Map of]]

## 90 — Observability & evaluations

- [[91-langfuse-observability|Langfuse & observability LLM]]
- [[92-chainforge-evals-prompts|ChainForge & Prompt Review]]
- [[93-monitoring-inference|Inference & Usage Monitoring]]
- [[94-evals-methodology|System evaluation LLM — Methodology]]
- [[95-llm-as-judge|LLM-as-a-judge]]
- [[96-evals-rag-agents|Evaluation of RAG & agents]]
- [[97-evals-online-ab-testing|Evals online & A/B testing]]
- [[98-agent-debugging|Debugging & Failure Analysis of — Flashcards Agents]]
- [[99-statistics-experimental-decisions|Statistics for deciding in IA]]
- [[90-010-llm-response-evaluation|Output & Response Rating LLM]]
- [[90-011-langfuse-instrumentation-production|Langfuse — Instrumentation in production]]
- [[90-012-langfuse-prompts-experiments|Langfuse — Prompts, datasets & experiences]]
- [[90-013-agent-testing-recovery|Agents — Contracts, Faults & Repeats Testing]]
- [[90-014-agent-skill-evaluation|Evaluate agent skills]]
- [[90-015-agent-skills-format-skills-ref|Agent Skills: format & validation with skills-ref]]
- [[90-016-harbor-agent-evaluation|Harbor: Evaluating Agents in Containers]]

## 100 — Security & guardrails

- [[101-llm-security-guardrails|Security LLM & guardrails]]
- [[102-agent-threats|Security of agents — Threats & incidents]]
- [[103-agent-defenses|Security of agents — Defensive architecture]]
- [[104-mcp-skills-security|MCP Security, Tools & Skills]]
- [[105-agentic-ai-devsecops|DevSecOps for Agentic AI]]
- [[106-coding-agent-security|Security of code agents]]

## 110 — MLOps & CI/CD

- [[111-mlops-llmops-fundamentals|MLOps & LLMOps — Fundamentals]]
- [[112-model-cicd|CI/CD Models]]
- [[113-monitoring-drift-feedback|Monitoring, drift & feedback loop]]
- [[114-reproducibility-variance|Reproducibility & variance]]
- [[115-agent-platforms-governance|— Agent Platforms Architecture & Governance]]
- [[116-ai-sre-incidents-capacity|SRE: incidents & capacity of IA services]]
- [[117-continuous-training-pipelines|— Training Pipelines, Register & Continuous Training]]
- [[118-ml-artifacts-registry-releases|Artefacts, registry & releases ML]]
- [[119-prediction-contracts-features-batch|Prediction contracts, features & scoring batch]]

## 120 — Costs & FinOps

- [[121-inference-costs|Inference costs]]
- [[122-finops-llm|FinOps LLM]]
- [[123-aggressive-caching|Caching agressif]]

## 130 — LLM fundamentals

- [[131-transformer-architecture|Architecture Transformer]]
- [[132-tokenization|Tokenisation]]
- [[133-embeddings-representations|Embeddings & representations]]
- [[134-vector-search-ann|Vector Search & Index ANN]]
- [[135-pretraining-scaling-laws|Pre-workout & scaling laws]]
- [[136-mixture-of-experts|Mixture of Experts (MoE)]]
- [[137-long-context|Long context]]
- [[138-reasoning-models|Reasoning Models & Test-Time Compute]]

## 140 — System design & product

- [[141-system-design-llm|LLM application system design]]
- [[142-llm-reliability-resilience|Reliability & resilience of LLM — Flashcards applications]]
- [[143-hallucinations-grounding|Hallucinations, grounding & abstention]]
- [[144-ai-ux-human-in-the-loop|AI UX & human-in-the-loop]]
- [[145-system-design-cases|LLM system design cases]]
- [[146-model-selection|Choose model]]
- [[147-ai-technical-leadership|Technical Leadership in AI Engineering]]
- [[148-llm-batch-pipelines|Large Scale Batch Pipelines]]
- [[149-delivery-idempotency-concurrency|Delivery, idempotency & concurrency]]
- [[140-010-transactions-outbox-sagas|Transactions, outbox & sagas for agents]]
- [[140-011-agentic-application-architecture|Applications — Architecture & Life Cycle]]

## 150 — Data & compliance

- [[151-data-curation-annotation|Data: curation & annotation]]
- [[152-pii-privacy|PII & Data Privacy]]
- [[153-data-flywheel-versioning|Data flywheel & data versioning]]
- [[154-gdpr-llm|GDPR applied to LLM]]
- [[155-ai-act|AI Act (European AI Regulation)]]
- [[156-responsible-ai|Responsible AI: bias, fairness & transparency]]
- [[157-data-contracts-quality|Contracts, Schematics & Data Quality]]
- [[158-ingestion-cdc-backfills|Incremental Ingestion, CDC & backfills]]
- [[159-temporal-data-features|Temporal data & production features]]
- [[150-010-analytical-data-modeling|Analytic Data Modeling]]
- [[150-011-analytical-sql-transformations|SQL for IA pipelines and datasets]]
- [[150-012-columnar-storage-lakehouse|Columnar storage, partitions & lakehouse]]
- [[150-013-data-pipeline-orchestration|Transforming & orchestrating data pipelines]]
- [[150-014-streaming-event-processing|Streaming & event processing]]
- [[150-015-distributed-computing-data-performance|Distributed Computing & Data Pipeline Performance]]
- [[150-016-data-observability-lineage|Observability, lineage & data exploitation]]
- [[150-017-ai-datasets-corpora|Dataset building & corpus IA]]

## 160 — Multimodal & edge

- [[161-vision-language-models|Vision-Language Models (VLM)]]
- [[162-document-parsing|Parsing documents (PDF, OCR, layout)]]
- [[163-real-time-voice|Voice & real-time agents]]
- [[164-local-edge-llm|LLM local, on-prem & edge]]
- [[165-computer-use-browser-agents|Computer use & browser agents]]

## 170 — Classical ML & validation

- [[171-ml-model-selection|Classic ML: choose and understand the]]
- [[172-ml-validation-metrics|Classic ML: Validation, Leaks & Metrics]]
- [[173-calibration-uncertainty-abstention|Calibration, uncertainty & abstention]]
- [[174-recommendation-ranking|Recommandation & learning to rank]]
- [[175-time-series-forecasting|Time Series Forecast]]
- [[176-anomaly-detection|Detection of anomalies]]
- [[177-model-explainability|Explainability & diagnostics of]]
- [[178-causal-inference-decisions|Causal Inference & Product Decisions]]

<!-- catalog:end -->

## The stack in one chain
```text
App / Agent
    ↓
Agent platform (runtime, sandbox, MCP tool gateway, identity, policies)
    ↓
Gateway LLM (Ingress → LiteLLM : auth, routing, budgets)
    ↓
Inference server (vLLM/SGLang/TensorRT-LLM, KV cache, batching, quantization)
    ↓
Container + GPU (Docker/K8s/Apptainer)
```
Transverses: **observability** (traces, metrics, evals), **security** (injection, lesser privilege, sandbox, DevSecOps), **costs** (FinOps) and **data & compliance** (PII, GDPR, AI Act).
