# AI Engineering — Map of content
Tags: #moc #ai-engineering

Start with [your first learning session](START_HERE.md), then choose a [learning path](docs/paths/README.md). Use the [learning guide](docs/guides/learning-with-flashcards.md) to turn reading into recall and practical decisions.

Browse topics below, or open the [catalog with summaries](docs/catalog.md). Each topic includes scenarios and a Connections section linking related concepts. Search for `Scenario:` in Obsidian to focus on practical cases.

[Documentation](docs/README.md) · [Anki](docs/guides/anki.md) · [Obsidian](docs/guides/obsidian.md)

<!-- catalog:begin -->

## 10 — Prompt engineering

[Start this domain](./10-prompt-engineering/README.md)

- [[11-advanced-prompt-engineering|Advanced prompt engineering]]
- [[12-automatic-prompt-optimization|Automatic Prompt Optimization (DSPy)]]
- [[13-production-prompts|Prompts in production]]

## 20 — RAG

[Start this domain](./20-rag/README.md)

- [[21-rag-fundamentals|RAG — Fundamentals]]
- [[22-advanced-rag|Advanced RAG]]
- [[23-knowledge-graphs-ontologies|Knowledge graphs & ontologies]]
- [[24-cognee|Cognee]]
- [[25-chunking-contextual-retrieval|Advanced Chunking & Contextual Retrieval]]
- [[26-text-to-sql|Text-to-SQL & structured data]]
- [[27-search-agents-deep-research|Search agents (deep research)]]
- [[20-010-rag-permissions-versions|RAG in production: rights, versions & abstention]]

## 30 — Agents

[Start this domain](./30-agents/README.md)

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

[Start this domain](./40-automation/README.md)

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

[Start this domain](./50-fine-tuning/README.md)

- [[51-fine-tuning-adaptation|Fine-tuning & model adaptation]]
- [[52-post-training-alignment|Post-training & alignment]]
- [[53-synthetic-data-distillation|Synthetic data & distillation]]
- [[54-distributed-training|Distributed Training]]
- [[55-agentic-rl|Agentic RL & Training Environments]]
- [[56-training-optimization-diagnostics|Training optimization & diagnostics]]

## 60 — LLM inference

[Start this domain](./60-llm-inference/README.md)

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

[Start this domain](./70-containers-infra/README.md)

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

[Start this domain](./80-api-layer-routing/README.md)

- [[81-litellm-api-layer|LiteLLM (API layer)]]
- [[82-routing-llm|LLM routing]]
- [[83-gateway-ingress|Ingress & API gateway]]
- [[84-streaming-application-integration|Streaming & application integration]]
- [[85-agentic-protocols-map|Agentic protocol map]]

## 90 — Observability & evaluations

[Start this domain](./90-observability-evals/README.md)

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

[Start this domain](./100-security-guardrails/README.md)

- [[101-llm-security-guardrails|LLM security & guardrails]]
- [[102-agent-threats|Agent security — Threats & incidents]]
- [[103-agent-defenses|Agent security — Defensive architecture]]
- [[104-mcp-skills-security|MCP, tool & skill security]]
- [[105-agentic-ai-devsecops|DevSecOps for Agentic AI]]
- [[106-coding-agent-security|Coding agent security]]

## 110 — MLOps & CI/CD

[Start this domain](./110-mlops-cicd/README.md)

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

[Start this domain](./120-costs-finops/README.md)

- [[121-inference-costs|Inference costs]]
- [[122-finops-llm|LLM FinOps]]
- [[123-aggressive-caching|Aggressive caching]]

## 130 — LLM fundamentals

[Start this domain](./130-llm-fundamentals/README.md)

- [[131-transformer-architecture|Transformer architecture]]
- [[132-tokenization|Tokenisation]]
- [[133-embeddings-representations|Embeddings & representations]]
- [[134-vector-search-ann|Vector search & ANN indexes]]
- [[135-pretraining-scaling-laws|Pretraining & scaling laws]]
- [[136-mixture-of-experts|Mixture of Experts (MoE)]]
- [[137-long-context|Long context]]
- [[138-reasoning-models|Reasoning Models & Test-Time Compute]]

## 140 — System design & product

[Start this domain](./140-system-design-product/README.md)

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

[Start this domain](./150-data-compliance/README.md)

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

[Start this domain](./160-multimodal-edge/README.md)

- [[161-vision-language-models|Vision-Language Models (VLM)]]
- [[162-document-parsing|Document parsing (PDF, OCR, layout)]]
- [[163-real-time-voice|Voice & real-time agents]]
- [[164-local-edge-llm|Local, on-premises & edge LLMs]]
- [[165-computer-use-browser-agents|Computer use & browser agents]]

## 170 — Classical ML & validation

[Start this domain](./170-classical-ml/README.md)

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
