# Langfuse & observability LLM — Flashcards
Tags: #flashcards #ai-engineering #observability #langfuse #llm
Verified on: 25 September 2026 — This factsheet lists products, versions or regulatory texts that are evolving quickly.
<!-- summary: perimeter and alternatives (LangSmith, Phoenix, Braintrust), traces, spans and generations, sessions, prompt management, scores, LLM-as-judge, datasets, trace sampling bias, traces and audit, metadata cardinality. -->


What is Langfuse? <!--anki:66646977482431392c37-->
?
A self-hosted or SaaS-based **open source of LLM** observability that covers:
- **Traces** of LLM calls, agent tools and steps
- **Costs and Latencies** by Trace, User or Feature
- **Prompt management** versioned
- **Evaluations**: automatic scores, human annotations, datasets

Alternatives: LangSmith, Arize Phoenix, Braintrust, or OpenTelemetry traces in an existing observability tool ([[93-monitoring-inference|monitoring]]).

A trace is not an evaluation: it shows what happened, not if the decision was correct. Add scores related to explicit criteria and control the coverage of the instrumented steps.

---

Why is the LLM observability different from the conventional APM? <!--anki:6678545e5a4b5374595b-->
?
Because the outputs are **non-deterministic** and the cost is **per token**: you have to track prompts, responses, tokens and quality, not just latency/errors.

A successful HTTP request can produce a false response or an unsuitable tool call. Linking the technical trace to the business result and an evaluation helps to distinguish failure, excessive cost and quality defect. Capture content only when necessary, with proper masking and access rights.

---

What is a trace in Langfuse? <!--anki:7741552c30265d676839-->
?
The **complete record of a request**: a tree of **spans** (steps) and **generations** (LLM calls), with inputs, outputs, latency, tokens and cost.
```text
trace: "support question #4212"         1.8 s    €0.004
├─ span       retrieval (hybrid + rerank) 240 ms 12 chunks
├─ generation intent classification      180 ms 310 → 8 tokens
├─ span       order-status tool           90 ms
└─ generation final answer (streaming)    1.2 s 3,400 → 180 tokens
```
This granularity shows **where** time and money are spent and supports replaying a case ([[93-monitoring-inference|aggregate metrics]]).

The final generation takes 1.2 of the 1.8 seconds; its 3,400 input tokens contribute to cost. Reducing retrieved passages affects both. Add prompt version, environment and a pseudonymous user identifier so a slow request can be attributed to the configuration that produced it.

---

What does session and user tracking allow? <!--anki:63492c7126682c43374f-->
?
**Group traces by conversation or user**: follow an end-to-end journey, find the history of a case reported to the support, identify users who constantly reformulate (failure signal) and assign costs per customer or team ([[122-finops-llm|FinOps]]).

Warning: a user identifier is a **personal data**. We prefer a **pseudonym** identifier ([[152-pii-privacy|PII]]).

Pseudonymization does not make data anonymous if the link remains possible. Separate business identifier, session and trace, limit access and retention. Two conversations from the same user should not be merged into a single execution.

---

What is prompt management of Langfuse? <!--anki:466a4f293328754834-->
?
A registry of versioned **prompts**, recoverable by the application via version or label, such as `production`. It allows to promote or restore a prompt without necessarily redeploying the code ([[13-production-prompts|Prompt in production]]).

Moving `production` from v12 to v13 is not enough to prove that each worker uses v13: some may still have v12 cached. Trace the **version actually resolved**, not just the label requested.

Submit promotion and rollback to evals, permissions, and changelogs. Set behavior in case of unavailable registry and cache propagation delay. The prompt must remain compatible with deployed tools, variables, and model.

---

How does Langfuse rate the quality of responses? <!--anki:755f48612d6276607357-->
?
Via **scores attached to the tracks**, from three origins:
- **User**: thumb up or down, note, comment, returned by the application
- **Automatic**: rules or code (JSON valid, citations present, length)
- **[[95-llm-as-judge|LLM-as-judge]]**: an evaluator running on a traffic sample

A score has a **name**, a **value** and possibly a **comment**, which allows to filter the failed tracks and track the quality over time ([[113-monitoring-drift-feedback|drift]]).

---

What are datasets for in Langfuse? <!--anki:7162585f2c4d7240345a-->
?
To build **test games from the actual traces**: we add an interesting trace (especially a failure) to the dataset in one click, with its entry and the expected output. We **replay** then this dataset with each change of prompt or model, and we compare the scores between executions.

This is the bridge between production and evals: the observed failures become **non-regression tests** ([[94-evals-methodology|golden dataset]], [[153-data-flywheel-versioning|flywheel]]).

---

How do I use an app with Langfuse? <!--anki:6b713c4c794f4b26255a-->
?
Combine **SDK**, framework integration and, if necessary, OpenTelemetry propagation:
```python
from langfuse import observe

@observe()
def respond(question: str):
    ...
```
LangChain callbacks or gateway integration capture their own calls; check the coverage obtained. OpenTelemetry observations must be configured and exported to the intended destination: they do not automatically trace back by their existence alone.

Link research, tools, models and validations in an application trace. A gateway alone does not see all these steps. Test kinship of observations, masking and absence of double counting of tokens.

---

Do not confuse: trace, metric and eval? <!--anki:752431622a3e7d525a51-->
?
- **Trace**: a **specific case**, with all its context. Serves to **investigate**
- **Metric**: one **aggregate** (p95 latency, cost per day, error rate). Serves to **alert**
- **Eval**: a **quality judgment** on an output, attached to a trace or a dataset. Serves to **decide** ([[94-evals-methodology|Methodology]])

All three are necessary: a metric says there is a problem, a trace says which, an eval says if a change has corrected it.

---

Why can sampling Langfuse traces bias quality and cost statistics? <!--anki:3065343561616434623566633434343738353633313464353239386633626230-->
?
A **sample of traces** that promote errors or delays is useful for diagnosis but is not representative of traffic. Its average can overestimate cost and latency, or exclude certain segments.

Document the sampling rule and keep complete counters for volumes and expenses. Use a representative sample or a justified weighting for overall estimates. Distinguish rate on observed traces and rate on eligible requests. Queries whose telemetry fails should not disappear from the denominator without analysis.

---

Do not confuse: Diagnostic trace and business audit log? <!--anki:3833623237623636373862383465373839353631343234613930653234633365-->
?
A trace makes it easier **understanding of an execution** and can be sampled. An audit journal must meet the requirements of completeness, defined integrity and retention for important decisions.

Linking them by identifiers makes it possible to explain an action without confusing their guarantees. Checking who can modify or delete events. The presence of a trace interface does not prove that all approvals and actions are permanently registered.

---

Why carefully choose the metadata used to aggregate LLM traces? <!--anki:6536626139353632653430303433643562626661343334656563363263666561-->
?
Almost unique values, such as each prompt text, create **very high cardinality** and complicate queries, costs and data protection.

Use stable dimensions: task type, version, length class, or status. Keep detailed identifiers where they are useful in case-finding. A clustering dimension should allow for operational decision, not just reproduce the entire raw context.

---

## Scenarios

Scenario: a user reports "a wrong answer yesterday afternoon". You only have the classic application logs. What do you miss, and what do you put in place? <!--anki:7375784c423966706d21-->
?
1. **What's missing**: the actual prompt sent, recovered documents, tool calls, prompt and model version
2. **Tracing** each query as a span and generation tree, with inputs, outputs, tokens and cost
3. **Identify**: session and user, to find the full conversation
4. **Version prompts** out of code, so you know which one was running at the time ([[111-mlops-llmops-fundamentals|MLOps]])
5. **Attention to personal data**: masking and retention defined from the start ([[152-pii-privacy|PII]])

**Trap** : only log the final answer, This makes any investigation impossible.

---

Scenario: your team wants to pass impressions ("it works pretty well") to a measure of quality in production. How do you do it? <!--anki:4d7a4b59692846604b-->
?
1. **Collect signal**: thumb up or down, reformulations, abandonments, escalations to a human
2. **Scoring a sample** of traces with an automatic judge, calibrated on human annotations ([[95-llm-as-judge|LLM-as-a-judge]])
3. **Build datasets** from real traces, especially failures
4. **Replay** these datasets with each prompt or model change ([[112-model-cicd|CI/CD]])
5. **Track over time** and segment by task, language and customer ([[113-monitoring-drift-feedback|drift]])

**Trap**: judge the quality on the only cases raised by the support, very biased.

---

## Sources

- [Langfuse — traces, assessments and prompt management](https://langfuse.com/docs)

- [Langfuse — trace structure and instrumentation](https://langfuse.com/docs/observability/best-practices)

- Supplement to the 14 November 2026 — Trace sampling and coverage limits: [Langfuse — Sampling](https://langfuse.com/docs/observability/features/sampling).

## Connections
- [[92-chainforge-evals-prompts|ChainForge & evals]] — evaluation out of production
- [[64-inference-metrics-slo|Metrics & SLO]] — from system to application
- [[81-litellm-api-layer|LiteLLM]] — natural trace source
- [[82-routing-llm|Routing LLM]] — decide based on observed data
- [[38-agent-platforms|Platforms of agents]] — brick observability
- [[113-monitoring-drift-feedback|Monitoring & drift]] — feedback loop prod
- [[122-finops-llm|FinOps LLM]] — the cost tracking
- [[93-monitoring-inference|Monitoring of inference]] — server metrics, GPU and usage
- [[94-evals-methodology|Evaluation methodology]] — golden dataset, error analysis
- [[95-llm-as-judge|LLM-as-a-judge]] — judge's bias and validation
- [[13-production-prompts|Prompt in production]] — register, labels and back
- [[98-agent-debugging|Debugging agents]] — read traces with method
- [[101-llm-security-guardrails|LLM Security]] — injection, exfiltration and guardrails
- [[11-advanced-prompt-engineering|Advanced Prompt Engineering]] — the basic techniques of the prompt
- [[114-reproducibility-variance|Reproducibility & variance]] — non-determinism and eval statistics
- [[41-code-nocode-automation|Automation code & no-code]] — workflows and no-code tools
- [[45-langgraph-production|LangGraph — Production]] — persistence, recovery and human supervision
- [[90-011-langfuse-instrumentation-production|Langfuse — Production instrumentation]] — trace instrumentation
- [[90-012-langfuse-prompts-experiments|Langfuse — Prompts, datasets & experiences]] — connect prompts, traces and scores
- [[00-moc-ai-engineering|MOC AI Engineering]]
