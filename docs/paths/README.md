# Learning paths

Choose a path for your goal. Start with [your first learning session](../../START_HERE.md) if you are new to the vault, and use the [learning guide](../guides/learning-with-flashcards.md) to assess progress.

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

For a concrete trace linking the concepts, start with [agent loops, tool calling and routing](agent-loop-tool-calling-routing.md): distinguish the decisions, follow an export task and explain every stopping outcome.

1. [[31-agent-fundamentals|Agent fundamentals]], then [[48-agentic-workflow-patterns|workflow patterns]] — choose between a workflow and an agent.
2. [[32-tool-calling|Tool calling]], [[33-mcp|MCP]] and the [[85-agentic-protocols-map|protocol map]] — connect agents to external systems.
3. [[35-context-engineering|Context engineering]] and [[39-agent-memory|memory]] — manage what an agent knows at each turn.
4. [[36-agent-orchestration|Multi-agent systems]], [[27-search-agents-deep-research|research agents]] and [[49-coding-agents|coding agents]] — explore major use cases.
5. [[96-evals-rag-agents|Evaluate]] and [[98-agent-debugging|debug]] agents; measure their [[90-014-agent-skill-evaluation|skills]] and run them on [[90-016-harbor-agent-evaluation|Harbor]] tasks.
6. [[102-agent-threats|Threats]] and [[103-agent-defenses|defenses]] — secure agentic systems.
7. [[84-streaming-application-integration|Application integration]] and [[38-agent-platforms|platforms]] — move into production.
8. [[115-agent-platforms-governance|Governance]] and [[55-agentic-rl|agentic RL]] — explore advanced topics.

### Implement and validate an agent platform

Follow the [practical guide](platform-agents-inference-learning-path.md) using the same support agent throughout. Validate each step through deliverables and observable results:

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

The [coverage audit](../reports/agentic-stack-audit-2026-10-09.md) describes the contributions and limits. The [support-agent workshop](../../examples/agentic-support/README.md) provides a local project with recovery tests; the CrewAI variant and remote integrations are additional exercises.

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

The [coverage audit and its five workshops](../reports/data-engineering-audit-2026-10-09.md) describe expectations for different roles. Start with the [local SQL workshop](../../examples/data-engineering/sql_workshop.py), then demonstrate pipeline recovery and dataset reconstruction. Study advanced topics when your project's constraints call for them.

### Senior practice path

After the foundations, work through these topics on one project and produce evidence for each step:

1. [[99-statistics-experimental-decisions|Make decisions with statistics]] — protocol, paired comparisons, intervals and thresholds for meaningful gains.
2. [[173-calibration-uncertainty-abstention|Calibrate and know when to abstain]] — reliability curves, risk–coverage tradeoffs and human-review workload.
3. [[56-training-optimization-diagnostics|Diagnose training]] — micro-batches, training and validation curves, gradients and normalization; go deeper if your role includes model adaptation.
4. [[116-ai-sre-incidents-capacity|Operate and recover from failures]] — SLOs, bounded queues, failover exercises and postmortems.
5. [[147-ai-technical-leadership|Help teams make and own decisions]] — architecture decision records, operational handover and verified fixes.

The [review and workshops](../reports/senior-learning-path-relevance-2026-10-07.md) set out priorities, deliverables and success criteria. Flashcards prepare your reasoning; demonstrate mastery by building systems, measuring them and explaining their limits.

### Predict, recommend and decide

After [[171-ml-model-selection|model selection]], [[172-ml-validation-metrics|validation]] and [[173-calibration-uncertainty-abstention|calibration]], choose a topic to match the problem:

- [[174-recommendation-ranking|Recommendation and ranking]] — select and order items while accounting for exposure bias and cold starts.
- [[175-time-series-forecasting|Time series forecasting]] — predict useful horizons using information actually available at prediction time.
- [[176-anomaly-detection|Anomaly detection]] — turn anomaly scores into actionable alerts.
- [[177-model-explainability|Explainability]] — diagnose predictions and understand what their explanations mean.
- [[178-causal-inference-decisions|Causal inference]] — estimate the effects of an action, with explicit assumptions and limits.

The [review of these five topics](../reports/new-ai-skills-2026-10-08.md) explains their contributions and provides an exercise for each. They extend the LLM and agent paths; select them according to the responsibilities of your target role.

### MLOps: train, deliver and monitor a model

The [churn-prediction case study](production-mlops-learning-path.md) provides a deliverable and completion criteria at each stage.

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

The [inference audit of 8 October](../reports/llm-inference-audit-2026-10-08.md) maps the covered concepts and provides four workshops with deliverables. Demonstrate gains under a representative workload; calculations in the cards are teaching examples.

