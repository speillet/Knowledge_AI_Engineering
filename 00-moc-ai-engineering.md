# AI Engineering — MOC
Tags: #moc #ai-engineering

The vault's main map of content covers the core knowledge of **AI engineering**, from using models to operating production systems.
Each domain contains flashcard topics linked through their `## Connections` sections.
Each topic also includes **scenarios**. Search for `Scenario:` in the vault to focus on those cards.

New to the vault? Start with [your first learning session](START_HERE.md).

Use the [learning guide](docs/learning-with-flashcards.md): eight steps covering prerequisites, answer criteria, Anki ratings and practical exercises. The [9 October review](docs/learning-review-2026-10-09.md) explains the content corrections and teaching improvements.

To apply evaluation metrics, use the [local AI decision workshop](examples/ai-decisions/README.md), which connects ML validation, calibration, model selection and document quality. The [11 October review](docs/relevance-review-2026-10-11.md) describes the additions and their scope.

To build verifiable evidence, use the [local RAG workshop](examples/verifiable-rag/README.md). It compares two policies across ten synthetic cases involving permissions, effective dates, conflicts, withdrawn documents and abstention. Study [[22-advanced-rag|advanced retrieval]], [[20-010-rag-permissions-versions|permissions and versions]], then [[96-evals-rag-agents|RAG evaluation]]. Produce a claim-to-evidence table and a reproducible report.

To understand how an LLM request is executed, follow the [prefill, RadixAttention and speculative decoding walkthrough](docs/understanding-prefill-radix-speculation-2026-11-12.md). It traces computed states, shared branches and verified tokens through a continuous example with detailed calculations.

The [cross-topic review of 12 November 2026](docs/cross-topic-review-2026-11-12.md) documents 147 topic expansions, corrections and the limits of source verification.

To take a predictive model into production, follow the [end-to-end MLOps path](docs/production-mlops-learning-path-2026-11-12.md), connecting data, training, inference packaging, promotion, scoring and recovery. It links [[117-continuous-training-pipelines|training pipelines]] to [[118-ml-artifacts-registry-releases|releases]] and [[119-prediction-contracts-features-batch|prediction contracts]].

The [reference review of 13 November 2026](docs/reference-currency-check-2026-11-13.md) distinguishes confirmed references from corrections concerning managed services, MCP, OWASP and the AI Act. It does not certify every claim in the vault.

The [14 November 2026 expansion](docs/topic-expansion-2026-11-14.md) developed the 150 topics available at that time: 271 new cards, 18 revised answers, numerical examples and diagnostics, with review identifiers preserved.

## Reading path

Suggested progression: **understand models → use them → build architectures → adapt models → serve and deploy → operate in production → govern → design systems.**

- **Predictive foundations**: [[171-ml-model-selection|classical ML]], then [[172-ml-validation-metrics|validation and metrics]] — choose an approach before building an LLM pipeline.

0. [[131-transformer-architecture|LLM fundamentals]] — understand how the models you use work.
1. [[11-advanced-prompt-engineering|Prompt engineering]] — communicate tasks and constraints to models.
2. [[21-rag-fundamentals|RAG]] — supply models with external knowledge.
3. [[31-agent-fundamentals|Agents]] — enable systems to act through tools.
4. [[41-code-nocode-automation|Automation and agent frameworks]] — workflows, LangChain, LangGraph and CrewAI.
5. [[51-fine-tuning-adaptation|Fine-tuning]] — adapt the model itself.
6. [[61-kv-cache-attention|Inference]] — understand model serving.
7. [[00-index|Containers and infrastructure]] — deploy on GPUs.
8. [[81-litellm-api-layer|API layer and routing]] — provide reliable access to models.
9. [[91-langfuse-observability|Observability and evaluation]] — measure system behavior and quality.
10. [[101-llm-security-guardrails|Security]] — protect the system and its users.
11. [[111-mlops-llmops-fundamentals|MLOps and CI/CD]] — deliver changes continuously.
12. [[121-inference-costs|Costs and FinOps]] — understand and control costs.
13. [[151-data-curation-annotation|Data and compliance]] — data, GDPR and the AI Act; then [[157-data-contracts-quality|contracts]], [[158-ingestion-cdc-backfills|ingestion]] and [[159-temporal-data-features|time-aware features]].
14. [[161-vision-language-models|Multimodal and edge]] — images, documents, voice and local inference.
15. [[141-system-design-llm|System design and product]] — bring the components together at a senior level.

### Agent engineering path

Focus on agents through topics from several sections:

1. [[31-agent-fundamentals|Agent fundamentals]], then [[48-agentic-workflow-patterns|workflow patterns]] — choose between a workflow and an agent.
2. [[32-tool-calling|Tool calling]], [[33-mcp|MCP]] and the [[85-agentic-protocols-map|protocol map]] — connect agents to external systems.
3. [[35-context-engineering|Context engineering]] and [[39-agent-memory|memory]] — manage what an agent knows at each turn.
4. [[36-agent-orchestration|Multi-agent systems]], [[27-search-agents-deep-research|research agents]] and [[49-coding-agents|coding agents]] — explore major use cases.
5. [[96-evals-rag-agents|Evaluate]] and [[98-agent-debugging|debug]] agents; measure their [[90-014-agent-skill-evaluation|skills]] and run them on [[90-016-harbor-agent-evaluation|Harbor]] tasks.
6. [[102-agent-threats|Threats]] and [[103-agent-defenses|defenses]] — secure agentic systems.
7. [[84-streaming-application-integration|Application integration]] and [[38-agent-platforms|platforms]] — move into production.
8. [[115-agent-platforms-governance|Governance]] and [[55-agentic-rl|agentic RL]] — explore advanced topics.

### Implement and validate an agent platform

Follow the [practical guide](docs/platform-agents-inference-learning-path.md) using the same support agent throughout. Validate each step through deliverables and observable results:

1. **Define success** with [[141-system-design-llm|system design]] and [[94-evals-methodology|evaluation methodology]]: task, baseline, constraints and acceptance criteria.
2. **Assign responsibilities** with [[38-agent-platforms|platforms]] and [[115-agent-platforms-governance|architecture and governance]]: API, runtime, state, LLM gateway and tools.
3. **Verify API and model contracts** with [[81-litellm-api-layer|LLM gateways]], [[84-streaming-application-integration|streaming]] and [[63-guided-generation|structured outputs]]: actual capabilities, errors and fallbacks.
4. **Make execution reliable** with [[32-tool-calling|tool calling]], [[103-agent-defenses|defensive architecture]] and [[149-delivery-idempotency-concurrency|idempotency]]: permissions, budgets, concurrency and recovery.
5. **Check responses and business outcomes** with [[90-010-llm-response-evaluation|response evaluation]], [[96-evals-rag-agents|agent evaluation]] and [[114-reproducibility-variance|reproducibility]]: rubrics, completeness, final state and variance.
6. **Observe the full system** with [[93-monitoring-inference|monitoring]] and [[64-inference-metrics-slo|metrics and SLOs]]: traces, request populations, deadlines and cost per task meeting its requirements.
7. **Measure and size capacity** with [[60-010-inference-load-benchmarks|benchmarks]], [[60-011-inference-capacity-scheduling|capacity planning]] and [[60-012-inference-optimization-method|optimization]]: calls per task, actual load, queues and headroom.
8. **Deploy and recover** with [[60-014-inference-parity-validation|inference parity]], [[142-llm-reliability-resilience|resilience]], [[112-model-cicd|CI/CD]] and [[116-ai-sre-incidents-capacity|SRE]]: serving-stack parity, failure tests, canary deployments, rollback and runbooks.

### Build and operate an agentic application

After the agent engineering foundations:

1. [[140-011-agentic-application-architecture|Define the lifecycle]] — API, identity, states, approvals and cancellation.
2. [[40-010-langchain-tools-middleware-production|Strengthen LangChain contracts]] — tools, middleware, errors and budgets.
3. Explore [[40-011-langgraph-recovery-concurrency|LangGraph]] or [[40-012-crewai-reliable-execution|CrewAI]] in depth — recovery, dependencies, concurrency and evolution.
4. [[90-011-langfuse-instrumentation-production|Instrument with Langfuse]] — business events, model calls, tools and trace propagation.
5. [[90-012-langfuse-prompts-experiments|Compare prompts and experiments]] — versions, datasets, scores and promotion.
6. [[90-013-agent-testing-recovery|Verify invariants]] — tool tests, crashes, stale decisions and migrations.

The [coverage audit](docs/agentic-stack-audit-2026-10-09.md) describes the contributions and limits. The [support-agent workshop](examples/agentic-support/README.md) provides a local project with recovery tests; the CrewAI variant and remote integrations are additional exercises.

### Senior foundations path

Connect three cross-cutting priorities to AI applications:

1. [[171-ml-model-selection|Choose an approach]], then [[172-ml-validation-metrics|validate without leakage]] — rules, classical ML or LLMs.
2. [[157-data-contracts-quality|Define contracts]], [[158-ingestion-cdc-backfills|make ingestion reliable]], then [[159-temporal-data-features|reconstruct the data available at a given time]] — quality and temporal correctness.
3. [[149-delivery-idempotency-concurrency|Control delivery and concurrency]], then [[140-010-transactions-outbox-sagas|coordinate transactions]] — preserve business guarantees despite failures.

### Cross-links

- [[38-agent-platforms|Platforms]] → [[115-agent-platforms-governance|architecture and governance]].
- [[165-computer-use-browser-agents|Computer-use agents]] — a multimodal extension of the agent engineering path.

### Data engineering for AI

1. **Define the data** with [[150-010-analytical-data-modeling|analytical modeling]], [[150-011-analytical-sql-transformations|SQL]] and [[157-data-contracts-quality|contracts]]: grain, keys, joins, nulls and invariants.
2. **Collect and reconstruct** with [[158-ingestion-cdc-backfills|ingestion, CDC and backfills]] and [[159-temporal-data-features|time-aware features]]: pagination, versions, deletions and actual availability.
3. **Store and publish** with [[150-012-columnar-storage-lakehouse|storage and lakehouse]] and [[150-013-data-pipeline-orchestration|data orchestration]]: files, snapshots, partitions, dependencies and recovery.
4. **Build corpora** with [[150-017-ai-datasets-corpora|AI datasets and corpora]], [[151-data-curation-annotation|curation]] and [[172-ml-validation-metrics|ML validation]]: manifests, data families, splits, shards and readers.
5. **Operate and govern** with [[150-016-data-observability-lineage|observability and lineage]], [[152-pii-privacy|privacy]] and [[116-ai-sre-incidents-capacity|SRE]]: quality, SLOs, impact and repair.
6. **Explore further as needed** with [[150-014-streaming-event-processing|streaming]] and [[150-015-distributed-computing-data-performance|distributed computing]]: low latency, state, shuffle, skew and cost.

The [coverage audit and its five workshops](docs/data-engineering-audit-2026-10-09.md) describe expectations for different roles. Start with the [local SQL workshop](examples/data-engineering/sql_workshop.py), then demonstrate pipeline recovery and dataset reconstruction. Study advanced topics when your project's constraints call for them.

### Senior practice path

After the foundations, work through these topics on one project and produce evidence for each step:

1. [[99-statistics-experimental-decisions|Make decisions with statistics]] — protocol, paired comparisons, intervals and thresholds for meaningful gains.
2. [[173-calibration-uncertainty-abstention|Calibrate and know when to abstain]] — reliability curves, risk–coverage tradeoffs and human-review workload.
3. [[56-training-optimization-diagnostics|Diagnose training]] — micro-batches, training and validation curves, gradients and normalization; go deeper if your role includes model adaptation.
4. [[116-ai-sre-incidents-capacity|Operate and recover from failures]] — SLOs, bounded queues, failover exercises and postmortems.
5. [[147-ai-technical-leadership|Help teams make and own decisions]] — architecture decision records, operational handover and verified fixes.

The [review and workshops](docs/senior-learning-path-relevance-2026-10-07.md) set out priorities, deliverables and success criteria. Flashcards prepare your reasoning; demonstrate mastery by building systems, measuring them and explaining their limits.

### Predict, recommend and decide

After [[171-ml-model-selection|model selection]], [[172-ml-validation-metrics|validation]] and [[173-calibration-uncertainty-abstention|calibration]], choose a topic to match the problem:

- [[174-recommendation-ranking|Recommendation and ranking]] — select and order items while accounting for exposure bias and cold starts.
- [[175-time-series-forecasting|Time series forecasting]] — predict useful horizons using information actually available at prediction time.
- [[176-anomaly-detection|Anomaly detection]] — turn anomaly scores into actionable alerts.
- [[177-model-explainability|Explainability]] — diagnose predictions and understand what their explanations mean.
- [[178-causal-inference-decisions|Causal inference]] — estimate the effects of an action, with explicit assumptions and limits.

The [review of these five topics](docs/new-ai-skills-2026-10-08.md) explains their contributions and provides an exercise for each. They extend the LLM and agent paths; select them according to the responsibilities of your target role.

### MLOps: train, deliver and monitor a model

The [churn-prediction case study](docs/production-mlops-learning-path-2026-11-12.md) provides a deliverable and completion criteria at each stage.

1. [[111-mlops-llmops-fundamentals|Version and trace]] — artifacts, registry, lineage and environments.
2. [[117-continuous-training-pipelines|Automate training]] — pipelines, data and model validation, the champion alias and selective labels.
3. [[114-reproducibility-variance|Compare models reliably]] — variance, run selection, environments and historical evidence.
4. [[118-ml-artifacts-registry-releases|Publish a loadable package]] — transformations, URIs, output contracts, integrity and restoration.
5. [[119-prediction-contracts-features-batch|Produce usable predictions]] — features, availability at prediction time, freshness, idempotent batch processing and publication.
6. [[112-model-cicd|Deploy gradually]] — evaluation gates, shadow deployments, canaries, GitOps and rollback.
7. [[113-monitoring-drift-feedback|Monitor drift and measurement quality]] — PSI, multivariate drift, label coverage and feedback loops.
8. [[116-ai-sre-incidents-capacity|Operate and recover]], then [[115-agent-platforms-governance|govern agentic systems]] — SLOs, dependencies, incidents, responsibilities and retirement.

### Measure and optimize LLM inference

1. **Define criteria** with [[64-inference-metrics-slo|metrics and SLOs]], then [[93-monitoring-inference|monitoring]]: user-visible experience, joint SLO compliance, errors and histograms.
2. **Measure capacity** with [[60-010-inference-load-benchmarks|load benchmarks]]: arrivals, caches, saturation and uncertainty.
3. **Plan capacity** with [[61-kv-cache-attention|KV cache]] and [[60-011-inference-capacity-scheduling|capacity and scheduling]]: memory, budgets, fairness and headroom.
4. **Choose optimizations** with the [[60-012-inference-optimization-method|optimization method]], [[62-inference-optimizations|inference optimizations]], [[67-speculative-decoding|speculative decoding]] and [[68-quantization|quantization]].
5. **Validate the decision** with [[121-inference-costs|costs]], [[112-model-cicd|CI/CD]] and [[116-ai-sre-incidents-capacity|SRE]]: quality, cost per successful task, canary deployments and incidents.

The [inference audit of 8 October](docs/llm-inference-audit-2026-10-08.md) maps the covered concepts and provides four workshops with deliverables. Demonstrate gains under a representative workload; calculations in the cards are teaching examples.

<!-- catalog:begin -->

## 10 — Prompt engineering

- [[11-advanced-prompt-engineering|Advanced prompt engineering]]
- [[12-automatic-prompt-optimization|Automatic Prompt Optimization (DSPy)]]
- [[13-production-prompts|Prompts in production]]

## 20 — RAG

- [[21-rag-fundamentals|RAG — Fundamentals]]
- [[22-advanced-rag|Advanced RAG]]
- [[23-knowledge-graphs-ontologies|Knowledge graphs & ontologies]]
- [[24-cognee|Cognee]]
- [[25-chunking-contextual-retrieval|Advanced Chunking & Contextual Retrieval]]
- [[26-text-to-sql|Text-to-SQL & structured data]]
- [[27-search-agents-deep-research|Search agents (deep research)]]
- [[20-010-rag-permissions-versions|RAG in production: rights, versions & abstention]]

## 30 — Agents

- [[31-agent-fundamentals|Agent fundamentals]]
- [[32-tool-calling|Tool calling]]
- [[33-mcp|MCP — Model Context Protocol]]
- [[34-harness-plugins|Harness & plugins]]
- [[35-context-engineering|Context engineering]]
- [[36-agent-orchestration|Multi-agent orchestration]]
- [[37-agent-frameworks|Agent frameworks]]
- [[38-agent-platforms|Agent Platforms]]
- [[39-agent-memory|Agent Memory]]

## 40 — Automation & agent frameworks

- [[41-code-nocode-automation|Code and no-code automation]]
- [[42-langchain-fundamentals|LangChain — Fundamentals]]
- [[43-langchain-agents|LangChain — Agents & middleware]]
- [[44-langgraph-fundamentals|LangGraph — Fundamentals]]
- [[45-langgraph-production|LangGraph — Production (persistence, HITL, multi-agent systems)]]
- [[46-crewai-crews|CrewAI — Crews]]
- [[47-crewai-flows|CrewAI — Flows]]
- [[48-agentic-workflow-patterns|Agentic Workflow Patterns]]
- [[49-coding-agents|Coding agents: usage & integration]]
- [[40-010-langchain-tools-middleware-production|LangChain — Contracts, tools & middleware in production]]
- [[40-011-langgraph-recovery-concurrency|LangGraph — Recovery, Concurrency & Evolution]]
- [[40-012-crewai-reliable-execution|CrewAI — Reliable Execution & Integration]]

## 50 — Fine-tuning

- [[51-fine-tuning-adaptation|Fine-tuning & model adaptation]]
- [[52-post-training-alignment|Post-training & alignment]]
- [[53-synthetic-data-distillation|Synthetic data & distillation]]
- [[54-distributed-training|Distributed Training]]
- [[55-agentic-rl|Agentic RL & Training Environments]]
- [[56-training-optimization-diagnostics|Training optimization & diagnostics]]

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
- [[60-010-inference-load-benchmarks|Load benchmarking for LLM inference]]
- [[60-011-inference-capacity-scheduling|LLM inference capacity & scheduling]]
- [[60-012-inference-optimization-method|LLM inference optimization method]]
- [[60-013-prefill-decode-step-by-step|Prefill & decode — Step by Step Execution]]
- [[60-014-inference-parity-validation|Validate an inference deployment: parity & non-regression]]

## 70 — Containers & infrastructure

- [[00-index|Containers & infra — Index]]
- [[01-oci|OCI]]
- [[02-docker-images-registries|Docker, images & registries]]
- [[03-containerd-runc|containerd & runc]]
- [[04-kubernetes-kubelet-cri|Kubernetes, kubelet & CRI]]
- [[05-docker-kubernetes|Docker & Kubernetes]]
- [[06-apptainer-singularity|Apptainer & Singularity]]
- [[07-containers-overview|Containers — Overview]]
- [[08-linux-primitives-docker-fundamentals|Linux primitives & Docker fundamentals]]
- [[09-gpu-containers|GPUs in containers]]
- [[10-images-models-weights|Container images & model weights]]
- [[11-llm-inference-servers|LLM inference servers]]
- [[12-kubernetes-gpu-inference|Kubernetes, GPUs & inference]]
- [[13-apptainer-inference-hpc|Apptainer & HPC inference]]

## 80 — API layer & routing

- [[81-litellm-api-layer|LiteLLM (API layer)]]
- [[82-routing-llm|LLM routing]]
- [[83-gateway-ingress|Ingress & API gateway]]
- [[84-streaming-application-integration|Streaming & application integration]]
- [[85-agentic-protocols-map|Agentic protocol map]]

## 90 — Observability & evaluations

- [[91-langfuse-observability|Langfuse & LLM observability]]
- [[92-chainforge-evals-prompts|ChainForge & prompt evaluation]]
- [[93-monitoring-inference|Inference & Usage Monitoring]]
- [[94-evals-methodology|LLM system evaluation — Methodology]]
- [[95-llm-as-judge|LLM-as-a-judge]]
- [[96-evals-rag-agents|Evaluation of RAG & agents]]
- [[97-evals-online-ab-testing|Online evaluation & A/B testing]]
- [[98-agent-debugging|Agent debugging & failure analysis]]
- [[99-statistics-experimental-decisions|Statistics for AI decisions]]
- [[90-010-llm-response-evaluation|Evaluating LLM outputs & responses]]
- [[90-011-langfuse-instrumentation-production|Langfuse — Instrumentation in production]]
- [[90-012-langfuse-prompts-experiments|Langfuse — Prompts, datasets & experiments]]
- [[90-013-agent-testing-recovery|Agent testing — Contracts, failures & recovery]]
- [[90-014-agent-skill-evaluation|Evaluating agent skills]]
- [[90-015-agent-skills-format-skills-ref|Agent Skills: format & validation with skills-ref]]
- [[90-016-harbor-agent-evaluation|Harbor: Evaluating Agents in Containers]]

## 100 — Security & guardrails

- [[101-llm-security-guardrails|LLM security & guardrails]]
- [[102-agent-threats|Agent security — Threats & incidents]]
- [[103-agent-defenses|Agent security — Defensive architecture]]
- [[104-mcp-skills-security|MCP, tool & skill security]]
- [[105-agentic-ai-devsecops|DevSecOps for Agentic AI]]
- [[106-coding-agent-security|Coding agent security]]

## 110 — MLOps & CI/CD

- [[111-mlops-llmops-fundamentals|MLOps & LLMOps — Fundamentals]]
- [[112-model-cicd|Model CI/CD]]
- [[113-monitoring-drift-feedback|Monitoring, drift & feedback loop]]
- [[114-reproducibility-variance|Reproducibility & variance]]
- [[115-agent-platforms-governance|Agent platforms — Architecture & governance]]
- [[116-ai-sre-incidents-capacity|SRE — Incidents & capacity for AI services]]
- [[117-continuous-training-pipelines|Training pipelines, registry & continuous training]]
- [[118-ml-artifacts-registry-releases|ML artifacts, registry & releases]]
- [[119-prediction-contracts-features-batch|Prediction contracts, features & batch scoring]]

## 120 — Costs & FinOps

- [[121-inference-costs|Inference costs]]
- [[122-finops-llm|LLM FinOps]]
- [[123-aggressive-caching|Aggressive caching]]

## 130 — LLM fundamentals

- [[131-transformer-architecture|Transformer architecture]]
- [[132-tokenization|Tokenisation]]
- [[133-embeddings-representations|Embeddings & representations]]
- [[134-vector-search-ann|Vector search & ANN indexes]]
- [[135-pretraining-scaling-laws|Pretraining & scaling laws]]
- [[136-mixture-of-experts|Mixture of Experts (MoE)]]
- [[137-long-context|Long context]]
- [[138-reasoning-models|Reasoning Models & Test-Time Compute]]

## 140 — System design & product

- [[141-system-design-llm|LLM application system design]]
- [[142-llm-reliability-resilience|LLM application reliability & resilience]]
- [[143-hallucinations-grounding|Hallucinations, grounding & abstention]]
- [[144-ai-ux-human-in-the-loop|AI UX & human-in-the-loop]]
- [[145-system-design-cases|LLM system design cases]]
- [[146-model-selection|Model selection]]
- [[147-ai-technical-leadership|Technical Leadership in AI Engineering]]
- [[148-llm-batch-pipelines|Large Scale Batch Pipelines]]
- [[149-delivery-idempotency-concurrency|Delivery, idempotency & concurrency]]
- [[140-010-transactions-outbox-sagas|Transactions, outbox & sagas for agents]]
- [[140-011-agentic-application-architecture|Agentic applications — Architecture & lifecycle]]

## 150 — Data & compliance

- [[151-data-curation-annotation|Data: curation & annotation]]
- [[152-pii-privacy|PII & Data Privacy]]
- [[153-data-flywheel-versioning|Data flywheel & data versioning]]
- [[154-gdpr-llm|GDPR for LLMs]]
- [[155-ai-act|AI Act (European AI Regulation)]]
- [[156-responsible-ai|Responsible AI: bias, fairness & transparency]]
- [[157-data-contracts-quality|Data contracts, schemas & quality]]
- [[158-ingestion-cdc-backfills|Incremental Ingestion, CDC & backfills]]
- [[159-temporal-data-features|Temporal data & production features]]
- [[150-010-analytical-data-modeling|Analytical data modeling]]
- [[150-011-analytical-sql-transformations|SQL for AI pipelines & datasets]]
- [[150-012-columnar-storage-lakehouse|Columnar storage, partitions & lakehouse]]
- [[150-013-data-pipeline-orchestration|Transforming & orchestrating data pipelines]]
- [[150-014-streaming-event-processing|Streaming & event processing]]
- [[150-015-distributed-computing-data-performance|Distributed Computing & Data Pipeline Performance]]
- [[150-016-data-observability-lineage|Data observability, lineage & operations]]
- [[150-017-ai-datasets-corpora|Building AI datasets & corpora]]

## 160 — Multimodal & edge

- [[161-vision-language-models|Vision-Language Models (VLM)]]
- [[162-document-parsing|Document parsing (PDF, OCR, layout)]]
- [[163-real-time-voice|Voice & real-time agents]]
- [[164-local-edge-llm|Local, on-premises & edge LLMs]]
- [[165-computer-use-browser-agents|Computer use & browser agents]]

## 170 — Classical ML & validation

- [[171-ml-model-selection|Classical ML: model selection & fundamentals]]
- [[172-ml-validation-metrics|Classical ML: validation, leakage & metrics]]
- [[173-calibration-uncertainty-abstention|Calibration, uncertainty & abstention]]
- [[174-recommendation-ranking|Recommendation & learning to rank]]
- [[175-time-series-forecasting|Time series forecasting]]
- [[176-anomaly-detection|Anomaly detection]]
- [[177-model-explainability|Model explainability & diagnostics]]
- [[178-causal-inference-decisions|Causal Inference & Product Decisions]]

<!-- catalog:end -->

## How the stack fits together

```text
App / Agent
    ↓
Agent platform (runtime, sandbox, MCP tool gateway, identity, policies)
    ↓
LLM gateway (Ingress → LiteLLM: authentication, routing, budgets)
    ↓
Inference server (vLLM/SGLang/TensorRT-LLM, KV cache, batching, quantization)
    ↓
Container + GPU (Docker/K8s/Apptainer)
```

Cross-cutting concerns: **observability** (traces, metrics, evaluations), **security** (prompt injection, least privilege, sandboxing, DevSecOps), **costs** (FinOps) and **data and compliance** (PII, GDPR, AI Act).
