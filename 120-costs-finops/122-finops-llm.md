# FinOps LLM — Flashcards
Tags: #flashcards #ai-engineering #finops #governance #llm
<!-- summary: four times of the FinOps, visibility of costs, allocation to teams, budgets and safeguards, routing as the first lever, caches, practices GPU, cost-quality-latency arbitration, role of the Lead, budget reservation of in-flight calls, shared costs, stable economic unit. -->


What is the FinOps applied to LLM? <!--anki:7438516d555137566925-->
?
The discipline of **AI Expense Management** (tokens D'AngeloAPI and GPU), in four stages:
1. **Visibility**: know what costs, up to the day
2. **Attribution**: what team, what product, what functionality
3. **Optimization**: caching, routing, batch, smaller models
4. **Governance**: budgets, alerts, arbitrations

The specificity of the LLM: a cost **variable** that depends on the behavior of users and agents, not a reserved capacity.

---

What is the first FinOps step of a LLM platform? <!--anki:6a5f702e5f54365e3c38-->
?
**Visibility**: plot the cost **by request, team and feature** via the [[81-litellm-api-layer|gateway]] and the [[91-langfuse-observability|traces]] — we do not drive what we do not see.

Spread request, hold, and feature identifiers to model and tool calls. Distinguish between measured, estimated, and shared costs, and then reconcile bill totals. Without reliable attribution, a local optimization can move expense to another step without reducing the full cost.

---

How to allocate costs to teams? <!--anki:74243d714f553e3e7e64-->
?
- **Virtual keys** per team or product in the gateway, and **tags** per feature ([[81-litellm-api-layer|LiteLLM]])
- **Showback** First: Each team sees its consumption
- **Chargeback** then: internal chargeback, once the figures are reliable

Without attribution, no one is responsible for a double cost, and optimizations remain wishful thinking.

Reconcile assigned usage and invoice, identifying shared costs and missing data. A request passing through three agents should not be charged three times to the parent in addition to his children; set the consolidation unit.

---

How to manage LLM team expenses? <!--anki:532b47722b306e7350-->
?
**Budgets and quotas per key/team** in the gateway, **alerts** before passing, **kill switch** in case of runaway.
```yaml
# example of virtual key safeguards (gateway LLM)
key: support-team
max_budget: 500          # € per month
budget_duration: 30d
rpm_limit: 600           # requests per minute
tpm_limit: 400000        # tokens per minute
models: [chat-petit, chat-fort]
```
Both limits count: **requests** against bursts, **tokens** against a single request to 200,000 tokens ([[81-litellm-api-layer|LiteLLM]]).

Associating these limits with an **attributable identity**: project, team and environment. An alert informs without necessarily blocking; a strict ceiling must be applied before the call, taking into account competing requests. The YAML is illustrative: currency, budget window and configuration keys must match the gateway actually deployed.

---

What gains can you expect from the main FinOps levers? <!--anki:73443a342f707e49655b-->
?
The gains are **measure on real traffic** ; No percentage is universal. A cheaper model may suffice for simple cases, a cover avoids repeated work, and the batch swaps a longer delay for different tariff conditions.

If an input expense represents 60% of the total and drops by half, the total savings are **30%**, not 50%. Count router cost, cache writes, and failures. Prioritize dominant endpoints, then re-evaluate the combined gains: they do not add up mechanically ([[121-inference-costs|Inference Costs]]).

---

What is often the first lever of savings on a LLM invoice? <!--anki:6a712b5f4f6e30675d6e-->
?
Start with the **Dominant Position Measured**. If many simple tasks use a large model, on the [[82-routing-llm|routing]] to a cheaper model is a good candidate. If the expense comes from repeated contexts or loops, cache, Context reduction or call limits can be more effective.

Compare cost per successful task and quality before and after, including router price and escalations. The best first lever depends on the load, not a universal order of optimizations.

---

What is FinOps practical on the GPU side? <!--anki:75432b70652f39746a70-->
?
- **Right-size**: the smallest GPU or the smallest **MIG** that holds the load
- **Usage target** tracked, for example above 60%
- **Spot or preemptible** for non-critical (batch, evals), with resume on interruption
- **Scale-to-zero** of little-known models
- **Reservations** for stable base load ([[12-kubernetes-gpu-inference|K8s GPU]])

The utilization rate alone is not a valuable target: a GPU busy recalculating KV after preemption can cost more without serving more tasks. Compare goodput, SLO and cost-per-success, keeping a margin for peaks.

---

How to arbitrate cost, quality and latency? <!--anki:69412d2547702d7c503f-->
?
Set **minimum quality, SLO latency, and mandatory constraints**, and then compare the total cost of eligible options with [[92-chainforge-evals-prompts|evals]] and [[64-inference-metrics-slo|Service Measures]].

Example: A costs 0.01 € per attempt and succeeds 80% of tasks; B costs 0.012 € and succeeds 98%. Out of recovery, their costs per success are worth about **0.0125 € and 0.01224 €**: B may be economically preferable.

Include cuts, human review and exploitation. There are trade-offs, but an improvement can also reduce cost and time while improving quality. Re-evaluate on measures, not on the assumption that prices always fall.

---

What is the role of the Lead on the FinOps? <!--anki:4d55412c6953465d317e-->
?
Follow them **unit economics by product**, impose them **Attribution standards**, hold of **Cost Reviews** Regular — the cost is a metric of first order, No surprise at the end of the month.

Setting budgets per usage and allowing arbitrations when they are exceeded: slowing down, batching or routing differently. Sharing cost and quality in the same review avoids rewarding a lower bill that deteriorates the service. Assign a manager and a result measure to each optimization.

---

Why does an agent budget cap have to reserve expenses for calls still in flight? <!--anki:6330623233643561396138313436373362346630323731633633323963373734-->
?
If multiple **parallel calls** read the same available balance, everyone can start before other expenses are accounted for, so a controlled budget only after response can be significantly exceeded.

Reserve an envelope before launch, cap the outputs and reconcile the actual use at the end. Release reserves only according to a rule that takes into account calls still potentially billable. Test concurrency and network shutdown. An invoice alert is useful for tracking, but does not constitute a synchronous control of the execution budget.

---

How to allocate the cost of a GPU shared between multiple teams? <!--anki:3731303730373965323563393462336638376332366433383330313861636262-->
?
Define a **measurable and explicit rule**: time reserved, work performed or capacity guaranteed, with a method for the inactive part.

No single key is universal. Sharing by request penalizes small requests if lengths vary greatly. Publish assumptions and reconcile the total allocated to the invoice. Teams must be able to explain their costs and act on the levers attributed to them.

---

Why monitor unit cost and total cost after a LLM optimization? <!--anki:6165313765396363666162393461373139653864633433373565363335626166-->
?
A lower cost per call can encourage **many more calls or branches**, increasing total spending, so the technical gain does not guarantee a lower budget.

Follow volume, cost per success and overall budget, with a baseline of comparable use. If the additional use creates value, the increase can be justified. The FinOps objective is an explicit arbitration, not an automatic decrease in any consumption.

---

## Scenarios

Scenario: the company's AI bill has tripled in a quarter and the finance department is asking for explanations that no one can give. Where do you start? <!--anki:78704d55386b76524b3d-->
?
1. **Visibility first**: without attribution, no decision is possible. Everything goes through the gateway, with keys per team and per project
2. **Attribute**: cost per team, app and feature, then showback before chargeback
3. **Identify large posts**: which routes, which models, which users concentrate the expense
4. **Pose safeguards**: budgets, quotas, alerts before overtaking, emergency cut
5. **Optimize next**: routing, caching, context, in this order ([[123-aggressive-caching|caching]])

**Trap**: Impose quotas before visibility, which blocks useful uses without addressing the cause.

---

Scenario: a team wants to move to the most powerful model for all its requests, on the grounds that "quality prevails". How do you frame the discussion? <!--anki:713930583e38726a4a71-->
?
1. **Getting out of opposition**: the subject is a cost, quality, latency triangle, not a binary choice
2. **Ask for measurements**: on which segments is the most powerful model really better? ([[94-evals-methodology|evals]])
3. **Encrypt**: cost per query and per successful task for each option
4. **Propose a waterfall**: small model with verification, climbing on difficult cases ([[82-routing-llm|routing]])
5. **Link to value**: unit economics of the feature, not just its invoice

**Trap**: decide on impressions, for lack of evals per segment.

---

## Connections
- [[121-inference-costs|Inference costs]] — Cost Mechanics
- [[81-litellm-api-layer|LiteLLM]] — budgets, quotas, attribution
- [[91-langfuse-observability|Langfuse]] — cost tracking by trace
- [[82-routing-llm|Routing LLM]] — the lever n°1
- [[38-agent-platforms|Platforms of agents]] — Governance at Scale
- [[123-aggressive-caching|Caching agressif]] — caches in practice
- [[93-monitoring-inference|Monitoring of inference]] — team usage metrics
- [[115-agent-platforms-governance|— Agent Platforms Architecture & Governance]] — the cost of a fleet of agents
- [[147-ai-technical-leadership|Technical Leadership]] — ROI of AI Features
- [[145-system-design-cases|Case of system design]] — of commented type architectures
- [[148-llm-batch-pipelines|Pipelines batch]] — process millions of items at a lower cost
- [[00-moc-ai-engineering|MOC AI Engineering]]
