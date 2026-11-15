# Model selection — Flashcards
Tags: #flashcards #ai-engineering #model-selection #benchmarks #llm
Verified on: 25 September 2026 — This factsheet lists products, versions or regulatory texts that are evolving quickly.
<!-- summary: criteria and constraints, benchmarks, hosting and weight opening, OSI definition, cost-per-success, comparable protocol, Pareto front, migration and lock-in, Pareto border, expected error cost, eligibility. -->


What are the technical criteria for choosing a model? <!--anki:4e76712b43634b3a5168-->
?
1. **Quality on his task** (eval house, not the leaderboard).
2. **Cost** per successful task (not just the price per token).
3. **Latency**: TTFT and throughput.
4. **Capacities**: useful context window, multimodality, tool calling, structured outputs.

Start with them **elimination thresholds**, Then compare the remaining models. For a streamed assistant, a TTFT of 2 can be prohibitive despite the best quality; for a night batch extraction, Only quality and cost count. Checking Capabilities in Real-World Conditions: An Advertised One Million Window tokens does not guarantee a good exploitation of this context.

---

What non-technical criteria weigh on the choice of a model? <!--anki:693e6d41763d4f6b3363-->
?
1. **Privacy**: where the data goes, retention, region.
2. **License** and conditions of use.
3. **Supplier reliability**: SLA, rate limits, announced depreciations.

Check these requirements on the exact offer: contract, region, and enabled features may change the terms. A license that allows for internal use does not necessarily allow for redistribution. Document playthroughs before benchmarks, and then schedule a migration if the provider removes the model or changes its terms.

---

Why is a benchmark ranking not enough to choose a model? <!--anki:6d6d6943634d763c4d30-->
?
A ranking measures **a protocol and a task population**, not necessarily the targeted product. [[135-pretraining-scaling-laws|Contamination]], style bias and uncertainty can limit its scope.

Example: The best model on general issues may fail to produce the expected schema in the customer's language, or exceed the service deadline.

Use benchmarks to pre-select and then compare on the same application cases: quality, formats, tools, costs and p95. Check versions, parameters and generation budgets; different conditions may explain the ranking. Also examine critical segments and contractual constraints, rather than an average deviation of a few points without interval.

---

Which public benchmark should you consult to pre-select a model in general knowledge, science, math or expert questions? <!--anki:6e2958374a2d3a4e4d34-->
?
- **MMLU / MMLU-Pro**: general knowledge in QCM (saturated for the best models).
- **GPQA**: scientific questions at PhD level.
- **Likes and other math benchmarks**: reasoning.
- **Humanity's Last Exam**: very difficult expert questions.

Useful reading: GPQA and Humanity's Last Exam indicate an expert reasoning ability, relevant for analysis or research. They provide little information on a support assistant, where respect for instructions and use of tools count more. These scores are used to eliminate candidates; the decision is made on a home evaluation.

---

Which public benchmark to consult to preselect a model in code, agent with tools, in compliance with instructions or in long context? <!--anki:515e6c40486e6f5e6030-->
?
- **SWE-bench (Verified)**: Resolution of real GitHub tickets.
- **τ-bench**: Support agents with tools and simulated user.
- **IFEval**: compliance with verifiable instructions.
- **RULER**: real exploitation of the long context.

They explore distinct capabilities; a good score on one does not predict the whole product. Examine version, protocol, authorized tools, and computational budget before comparing. The published results are used to preselect, and then a representative internal set must check for errors, latency, and cost on actual use.

---

Closed model (API) or open weights? <!--anki:772b5b4b677551327068-->
?
A **API** outsources the serving but imposes conditions for processing data, quotas and catalog changes. A **open weights** model allows you to manage the deployment yourself if its license and available resources allow it.

No choice guarantees the best level of quality or the lowest cost. Compare task, data requirements, hardware, volume, operation and migration capacity. The API can avoid an initial investment; self-hosting can bring control and economy to certain loads. Open weights models are also accessible in managed service: weight availability and hosting mode are two separate decisions.

---

Do not confuse: open weights and open source? <!--anki:45583454626869623129-->
?
**Open weights** indicates that the parameters are accessible; this does not in itself specify the freedoms of use or the published elements.

The OSI's definition **Open Source AI 1.0** requires the freedom to use, study, modify, and share, as well as parameters, code, and information that is sufficiently detailed about the data to build a substantially equivalent system. It does not necessarily require the publication of all raw data or a bit-by-bit reproduction. Check the available items and their conditions; do not deduct this qualification from the weight download alone.

---

How to compare the cost of two models correctly? <!--anki:4b3f394d40257e6f6577-->
?
On **the cost per successful task** : a cheaper model by token can consume **more than tokens** (tokenizer less effective, Longer answers, reasoning), **Fail more often** (withdrawals, climbs) or require a longer prompt. We measure them tokens **Real** on his eval ([[121-inference-costs|costs]]).

First set the quality and latency thresholds and then compare the eligible models. Also count tools, judge and human recovery. A lower average price obtained by abandoning difficult files is not an equivalent service economy.

---

Why not look for the “best model”? <!--anki:4c62553c676731324f2f-->
?
Subtasks can require different capabilities: classify, search, extract, or reason. Several models with [[82-routing-llm|routage]] can reduce the cost or improve a segment.

This architecture also adds components to be validated, thresholds, monitoring and folds. A single model can be enough and simplify operation. First compare this baseline, then introduce a specialist when a useful gain exceeds the cost of coordination. The diversity of needs suggests a comparison; it does not prescribe a universal multi-model architecture.

---

How to avoid lock-in supplier? <!--anki:6a3132365f365e506038-->
?
Isolate dependencies whose migration could block the product: call contracts, formats, hosted tools, identifiers and persistent data.

A **gateway** and versioned prompts make it easy to replace, but do not guarantee behavior compatibility. Keep evals, schemas, and data exportable; test another vendor on format, tools, security, quotas, and cost. Plan for unmatched features and qualification time. An untested fallback can move the outage rather than solve it.

---

How do I limit the risks when migrating to a new model? <!--anki:4d265f5f36683060794b-->
?
1. Rotate the **Game of Eval** complete (quality, format, cost, latency).
2. **Test existing prompts**, then adjust them if necessary: their portability is measured.
3. **Shadow** or **canary** on real traffic.
4. **A/B test** if the issue is important.
5. Keep the old model in **fallback** until stabilized ([[112-model-cicd|CI/CD models]]).

The shadow must not double the business effects: simulate the candidate's writing tools. Also check tokenizer, rejection, schemas and limits; a compatible API does not guarantee identical behavior.

---

How to track a market that changes every month? <!--anki:75334b5e4a6133343a3f-->
?
Keep an **Process** rather than a fixed opinion: a **eval automated house** that we relaunch at each exit of notable model, a **Decision grid** shared, and one **Quarterly Review** choice of models in terms of cost and quality ([[147-ai-technical-leadership|Technical Leadership]]).

Concretely: a few hundred representative cases, versioned, executable in one command on any model accessible via the gateway, with measured cost and latency. A migration is triggered on a gap higher than a threshold set in advance, for example 20% cost less at equal quality, not on an ad.

---

How to use a Pareto front to choose a LLM model? <!--anki:3265623433663661633161393463643061393366393734343638356539643931-->
?
First eliminate candidates who violate a **compulsory constraint**. Among the others, one candidate is dominated if another is at least as good on all the criteria selected and strictly better on one.

Non-dominated candidates form the **front of Pareto**: none wins everywhere. Differentiate according to product compromise, e.g. quality vs. cost and latency. Use comparable measurements and their uncertainty; a tiny and noisy difference does not demonstrate real domination. A weighted average should not hide an elimination constraint.

---

Why compare LLM models with the same protocol and explicit budgets? <!--anki:3965626364333538623730393432323461636332393333376565373831626436-->
?
Tools, context, prompts, number of essays and generation budget influence the result. A candidate authorized to search and try ten times is not directly comparable to a single answer without a tool.

Define whether the model’s **capacity** is compared to controlled resources or the **deployable** system under constraints produced. A prompt tailored to each model may be relevant if the optimization budget is documented. Report protocol and actual costs; equalize only `max_tokens` does not equalize time or calculation.

---

Calculation: on the same test, Has succeeded 94% To 0.010 €/request and p95 = 0.8 s; B, 95% To 0.008 € and 0.7 s; C, 97% To 0.012 € and 1.4 s. The requirements are successful ≥ 94% and p95 ≤ 1 s. By treating the measurements as accurate, Which one to remember? <!--anki:6338353134376464616165373434383961373639663166333263396561616539-->
?
**B** meets both constraints and dominates A: better success, lower cost and lower latency. C is excluded by the latency constraint despite its best success.
```text
A: cost per success = 0.010 / 0.94 ≈ 0.01064 €
B: cost per success = 0.008 / 0.95 ≈ 0.00842 €
```
These reports divide the total cost between successes; they do not model a withdrawal policy. In practice, check uncertainty, critical segments and load comparability before concluding. Thresholds and tariffs are fictitious.

---

Why compare models on a Pareto border rather than an arbitrary composite score? <!--anki:3934343434383434336531633462333962363364656662316538383934623238-->
?
A model is **dominated** if another is at least as good on all the criteria selected and better on one of them. Spreading these options simplifies the comparison without imposing an arbitrary weighting from the outset.

On the remaining boundary, decide according to quality, cost, latency and data constraints. Measure criteria under comparable conditions and take into account uncertainty. A single score may hide a delay overrun or a critical regression. The boundary makes arbitrage visible; it does not choose product priorities instead of the team.

---

Calculation: A costs 0.01 € per query with 4% errors; B costs 0.03 € with 1% errors. Each error costs on average 2 €, the same for both. What total cost expected per query? <!--anki:3064313966396237646533373431393861313737653736353561316532396534-->
?
For A: **0.01 + 0.04 × 2 = 0.09 €**. For B: **0.03 + 0.01 × 2 = 0.05 €**.

B is less expensive overall in these cases, despite its higher inference price. Verify that errors have comparable severity and that rates are representative. Time and confidentiality constraints remain separate criteria.

---

Why eliminate ineligible models before calculating a weighted choice score? <!--anki:3936333638653763376162663437363961323733376438663331323338636238-->
?
An excellent cost or benchmark should not compensate **a mandatory constraint not satisfied**, such as a necessary format or a hosting requirement.

First define the eligibility criteria, then compare the trade-offs between remaining candidates. Document evidence and uncertainties. An overall score may mask a crippling weakness if all criteria are treated as exchangeable.

---

## Scenarios

Scenario: a new model comes out, advertised better everywhere and 30% cheaper. Your team wants to migrate this week. What process do you impose? <!--anki:4b504f356c6a4d2e525f-->
?
1. **Replay the full home review**: quality, format, tool calling, real cost in tokens, latency
2. **Adjust prompts**: a prompt is not portable as is from one model to another
3. **Compare the cost per successful task**, not the price per token: a talkative model can cost more
4. **Shadow then canary** on real traffic, with the old model back down ([[112-model-cicd|CI/CD]])
5. **Document the decision** and what would go back

**Trap** : migrate on the basis of a press release and discover the regression on a segment in production.

---

Scenario: management requires that the data does not come out of the company, but the team wants the quality of a proprietary model. How do you handle the constraint? <!--anki:6d4d79474d392149404e-->
?
1. **Take constraint as a criterion of choice**, not as an obstacle to be circumvented
2. **Check options**: regional offerings, non-training and retention commitments, deployment to an existing cloud provider
3. **Evaluate open weights** on your task: the gap is sometimes small on a restricted perimeter ([[164-local-edge-llm|Local LLM]])
4. **Segmenter**: self-host for sensitive data, API for the rest, behind a gateway
5. **Encrypt** the total cost of the self-host, including operation ([[121-inference-costs|costs]])

**Trap** Choose a model first and expect compliance to follow.

---

## Sources

- [OSI — Open Source AI Definition 1.0](https://opensource.org/ai/open-source-ai-definition)

- [Hugging Face — Open LLM Leaderboard Methodology](https://huggingface.co/docs/leaderboards/open_llm_leaderboard/about)
- [NIST — AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)

## Connections
- [[94-evals-methodology|Evaluation methodology]] —
- [[82-routing-llm|Routing LLM]] — combine several models
- [[121-inference-costs|Inference costs]] — cost per task
- [[135-pretraining-scaling-laws|Pre-workout]] — contamination and cutoff
- [[164-local-edge-llm|Local LLM & Edge]] — options open weights
- [[155-ai-act|AI Act]] — general purpose model obligations
- [[13-production-prompts|Prompt in production]] — a prompt does not transfer from one model to another
- [[12-automatic-prompt-optimization|Automatic optimization of prompts]] — let a metric choose the formulation
- [[141-system-design-llm|System Design LLM]] — design method
- [[49-coding-agents|Code Agents]] — Use and Integrate Code Agents
- [[63-guided-generation|Guided generation]] — ensure valid structured outputs
- [[64-inference-metrics-slo|Metrics & SLO]] — TTFT, TPOT, flow rate and percentiles
- [[171-ml-model-selection|ML Classic]] — compare a LLM to predictive rules and models
- [[00-moc-ai-engineering|MOC AI Engineering]]
