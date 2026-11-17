# LLM routing — Flashcards
Tags: #flashcards #ai-engineering #routing #api-layer #llm
<!-- summary: model routing versus workflow branches, static and rule-based routing, semantic and learned routers, eligibility before optimization, calibrated scores, cascades, fallback and retries, shared budgets, agent-state routing, selection bias and end-to-end evaluation. -->


## What the router chooses

Why route requests between multiple models? <!--anki:6a5b33407a5a3140415e-->
?
Routing chooses a model that meets the request's **quality and capability requirements** at an acceptable cost and latency. It is useful when candidates perform differently across the actual workload.

If 70% of requests can use a model costing one-tenth as much, model cost becomes `0.7 × 0.1 + 0.3 × 1 = 0.37` of an all-expensive baseline, before routing and verification costs.

That saving is only useful if quality remains acceptable on the diverted requests. Do not assume most traffic is easy or that the largest model always gives the best answer.

---

What is static model routing? <!--anki:44773775513569557677-->
?
A **fixed model assignment per use case**: for example, one tested model for structured extraction and another for document analysis.

The mapping comes from evaluation, not from labels such as “simple” or “advanced.” It is predictable and provides a useful baseline before adopting per-request routing.

Revisit the mapping when prompts, traffic, model versions or requirements change. Static routing simplifies the decision process; it does not eliminate the need to monitor quality and capability compatibility.

---

What is rule-based model routing? <!--anki:5162254473514a51595d-->
?
It chooses an eligible model using **explicit rules** about request properties or context, such as input size, language, required modality or service tier.

Define rule precedence and what happens when no eligible route remains. A context-length check must allow room for instructions, tool schemas and output, not just the user's message.

Hard requirements such as data location and tool support constrain the candidate set. A cheaper route must not override them. Log the rule that selected the route so boundary cases can be reproduced.

---

What is semantic routing, and what does similarity fail to establish? <!--anki:416e31782d254b435577-->
?
A semantic router compares a request's **meaning representation**, often an embedding, with route examples or descriptions. Similarity can help choose a topic-specific handler without a generative classification call.

Set thresholds and an ambiguous or out-of-scope route using labeled evaluation cases. A nearest neighbor always exists in a nonempty example set, even when none is appropriate.

Similarity is not proof of task difficulty, authorization or answerability. An embedding still has computation or API cost, and route examples must cover realistic phrasing and confusing neighboring categories.

---

What does a learned model router such as RouteLLM predict? <!--anki:733a60734a2a716f745b-->
?
A learned router estimates **when one candidate model offers useful quality over another**, using preferences or observed outcomes. A decision threshold controls the evaluated cost-quality tradeoff.

A short request can be difficult, while a long repetitive extraction can be easy for a specialized model. Learned routing can capture patterns that length rules miss, but it depends on its training distribution.

Validate on held-out traffic and compare with static and rule-based baselines. Changing the candidate models or their prompts may invalidate old scores and thresholds.

---

Why must a model router filter eligibility before optimizing cost or quality? <!--anki:6264333264666435353536613438343138313465616539636237653038363666-->
?
Some requirements are **hard constraints**, not preferences: required modalities, context capacity, tool protocol, data permissions or deployment location.

First remove candidates that cannot satisfy the request contract. Then optimize among the remaining candidates. If none qualify, return a defined unavailable or escalation outcome.

For example, a low-cost text-only backend cannot process an image merely because a router assigns it a high score. Apply the same checks to fallback paths; otherwise an outage can silently change the application's data or capability guarantees.

---

Can a router score of 0.9 be interpreted as a 90% chance of successful task completion? <!--anki:6363386563363934663334353434623061656562623361656138306464616263-->
?
Only if the score was **defined and calibrated for that specific event and population**. Cosine similarity, a route-class probability and a model's self-reported confidence are different quantities.

A classifier can be confident that a request concerns billing without knowing whether the billing handler will resolve it. Likewise, a preference score between two models does not directly measure absolute correctness.

Choose thresholds on held-out outcomes, inspect reliability by segment and revalidate after changes. An uncalibrated score should not become an automatic permission or completion criterion.

---

## Cascades, fallback and bounded recovery

What is a model cascade? <!--anki:704a444b343c593f2c61-->
?
A cascade tries one candidate, **checks its result**, and uses another candidate if the acceptance check fails and escalation can help.

With fictional costs of 1 unit for A and 12 for B, escalating 20% of requests costs `1 + 0.2 × 12 = 3.4` units on average, before verification. An all-B baseline costs 12 units.

Measure false acceptance, unnecessary escalation and sequential latency. A format-valid answer can still be wrong, so JSON validation alone is insufficient when the task also requires factual or business correctness.

---

Do not confuse: model routing and fallback? <!--anki:66313d487a55554a5a34-->
?
**Routing** selects a backend before a call. **Fallback** switches to another eligible backend after a technical failure, such as unavailability or a rate limit.

Escalating after an unacceptable answer is a quality-driven cascade, not the same failure mode. A retry repeats an attempt under a defined recovery policy.

Record the trigger and preserve the request contract across every switch. A fallback that lacks required tools or receives data it is not allowed to process is invalid, even if it returns an answer quickly.

---

Do not confuse: routing, cascade, fallback and retry? <!--anki:7265624f26605e34686c-->
?
```text
Routing  → select a backend before the attempt
Cascade  → try another candidate after a quality check fails
Fallback → switch eligible backends after a technical failure
Retry    → repeat a recoverable attempt within limits
```

These mechanisms can coexist, but each needs an explicit trigger and stopping rule. A failed quality check does not always mean a more capable model can solve the problem.

Track the entire attempt chain under one deadline and budget. Independent retry loops in the client, gateway and provider can otherwise multiply calls and delay the final outcome.

---

How should nested retries and model escalation share a stopping budget? <!--anki:3062653261333431353566353430366661366434303530376164656239343736-->
?
Use a **single task-level budget** alongside local limits. Count actual attempts, including retries, verification calls and fallbacks, rather than resetting the counter at each layer.

For example, a gateway allowing three attempts per call inside an agent allowing ten turns may permit thirty model attempts before tool retries are counted. Define whether the intended cap is ten turns or ten attempts.

Before admitting work, check remaining time and cost and retain a verification/reporting reserve. A new backend should not reset the clock or make an exhausted request eligible again.

---

When should a model cascade stop instead of escalating to another model? <!--anki:3762313434376663653134363435636561306137643237353333663638333038-->
?
Stop when the cause is **missing evidence, unresolved user intent, denied permission, incompatible capabilities or an exhausted budget**, rather than a model capability gap that another eligible candidate can plausibly close.

An inaccessible invoice does not become accessible by choosing a larger model. Resolve the missing evidence or authorization through an allowed path, or report the limitation.

Define a finite set of admissible attempts and preserve the best valid result where useful. “Try a stronger model” is not a substitute for classifying why the current attempt failed.

---

What is load-based routing between model replicas? <!--anki:47573371746971216e2e-->
?
It distributes requests among **compatible serving replicas** using recent signals such as queue length, expected latency, available capacity and prefix-cache affinity.

Sending a request to a replica that already holds its prompt prefix can save prefill work, but a busy cache-friendly replica may still be slower than an idle one.

Balance reuse against queueing and test with realistic traffic. This is a placement decision, distinct from choosing a different model for better task quality. Limit oscillation and handle stale load measurements.

---

When may an agent choose different models for different steps? <!--anki:3038343738306235333538323435333838313061376130383730353161323762-->
?
When the steps have **different capability requirements** and the system can preserve compatible state and tool contracts. A small model may classify a request while another handles a complex synthesis.

Route on the current step's purpose and constraints, not just the initial user message. Preserve accepted evidence, pending operations and output requirements when switching.

Validate the whole trajectory: a cheaper intermediate decision can send later work down the wrong path. Model switches must not lose operation IDs, change permissions or reset the global budget.

---

What is a semantic response cache? <!--anki:702925434b335a303e56-->
?
It reuses a stored answer for a **sufficiently similar request**, subject to compatibility rules. This can avoid generation, but semantic resemblance alone does not prove that the answer is reusable.

Two questions may differ by negation, date, account or document version. Include relevant identity, permissions and source freshness in cache eligibility, with invalidation when those facts change.

Use it where reuse can be evaluated and accepted. High cache-hit rate is not a quality measure if the system serves stale or inappropriate responses.

---

## Evaluation and accounting

What evidence should guide a model-routing policy? <!--anki:673d62522f6f49603563-->
?
Use **quality, latency and cost by request segment**, measured on representative tasks under comparable prompts, tools and inference budgets.

For example, synthetic results of 98% versus 99% success on order-status questions differ from 61% versus 88% on disputed refunds. Routing by segment may be useful, but these averages need uncertainty estimates and checks on important failure types.

Monitor whether production traffic still resembles the evaluation population. A shift toward difficult cases can erase expected savings or quality without changing the routing code.

---

How should a router with an abstention path be evaluated? <!--anki:6465396235666339623264363438373561643266356230326439316436373033-->
?
Report **coverage**—the share routed automatically—and quality on that subset, together with the outcomes and costs of abstained cases.

A router that handles only easy requests may have excellent conditional accuracy but poor overall completion. Measure end-to-end success, wrong-route severity, clarification or escalation rate, total cost and latency.

Evaluate ambiguous, multi-intent and out-of-scope requests explicitly. Choose thresholds using development data, then report results on a held-out set. Do not optimize a routing label metric while ignoring whether the selected handler actually solves the task.

---

Why is comparing models only on their routed traffic biased? <!--anki:3263313832643862306231643463323239323936326437353831666638656334-->
?
The router may send **harder cases to one model** and easier cases to another. Their observed success rates therefore reflect different populations as well as different capabilities.

Compare candidates on a common representative sample, or use a justified controlled evaluation that respects data and cost constraints. Preserve route scores and decision reasons.

A larger model's lower success rate on escalated requests does not prove it is worse. Those logs alone do not reveal how the smaller model would have performed on the same requests.

---

Calculation: every request uses model A at a fictional €0.002, and 25% also use B at €0.020. What is the mean model cost? <!--anki:3866303963663363386636343466323261316261666166396462353135303736-->
?
```text
mean cost = €0.002 + 0.25 × €0.020 = €0.007
cost for 1,000 requests = €7
```

The calculation assumes fixed per-attempt costs and at most one escalation. Add routing, verification, retries and tools to estimate the total.

Also measure the quality of requests accepted after A: a cascade can look inexpensive because its checker misses errors. Escalation rate alone establishes neither preserved quality nor net savings.

---

## Scenarios

Scenario: management asks to halve assistant costs while preserving quality. How do you evaluate model routing? <!--anki:702a4c60414f3b6c6136-->
?
1. **Define acceptable quality by segment**, including important error types.
2. **Compare candidate models on the same requests**, with all relevant capabilities enabled.
3. **Establish a static or rule-based baseline** before adding a learned router.
4. **Evaluate verification and escalation**, including false acceptance and extra latency.
5. **Measure total cost per acceptable outcome** and monitor distribution shifts after rollout.

**Trap**: selecting a router solely from its cheap-model usage rate.

---

Scenario: a banking assistant proposes reusing answers to semantically similar questions. What must be checked? <!--anki:457145645a3a603e465f-->
?
1. **Identify personalization and freshness dependencies**, including account, product and effective date.
2. **Enforce cache eligibility** before considering similarity.
3. **Test confusing pairs**, such as questions differing by negation or account type.
4. **Limit reuse to an evaluated scope** and invalidate entries when relevant facts change.
5. **Measure incorrect reuse**, not just hit rate and saved tokens.

**Trap**: sharing an answer between customers because their questions sound alike.

---

Scenario: the primary model times out, but the only available fallback lacks the required tool protocol. Should routing continue? <!--anki:3233313861353564633233633462633662353234646663643232323936376131-->
?
1. **Reject the incompatible fallback** under the capability contract.
2. **Check for another eligible backend** within the remaining deadline.
3. **Preserve pending tool operations and their IDs**; do not replay writes blindly.
4. **Return a recoverable unavailable or partial outcome** if no valid route remains.
5. **Test this path explicitly** so an outage does not silently degrade the contract.

**Trap**: treating any generated text as a valid substitute for the required tool-enabled operation.

---

## Sources

Review of 17 November 2026: routing decisions, compatibility gates, cascade stopping rules and evaluation. Costs and success rates in examples are synthetic, not provider prices or benchmark claims.

- [Ong et al. — RouteLLM](https://arxiv.org/abs/2406.18665).
- [Anthropic — workflow routing and composition](https://www.anthropic.com/research/building-effective-agents).
- [AWS Builders' Library — timeouts, retries and backoff with jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/).

## Connections
- [[81-litellm-api-layer|LiteLLM]] — where routing is implemented
- [[91-langfuse-observability|Langfuse]] — decide based on observed data
- [[92-chainforge-evals-prompts|Evals]] — measure quality by model
- [[64-inference-metrics-slo|Metrics & SLO]] — latency constraint
- [[121-inference-costs|Inference costs]] — cost lever n°1
- [[66-prefix-caching-radix-attention|Prefix caching & RadixAttention]] — Prefix affinity routing
- [[123-aggressive-caching|Caching]] — reuse at different layers
- [[146-model-selection|Choice of model]] — criteria and benchmarks
- [[138-reasoning-models|Reasoning models]] — task difficulty and inference budgets
- [[122-finops-llm|FinOps LLM]] — allocate and drive AI spend
- [[141-system-design-llm|System Design LLM]] — design method
- [[48-agentic-workflow-patterns|Workflow patterns]] — choosing a branch rather than a model
- [[53-synthetic-data-distillation|Synthetic Data & Distillation]] — generate data and transfer to a small model
- [[31-agent-fundamentals|Agent fundamentals]] — stopping conditions and bounded execution
- [[32-tool-calling|Tool calling]] — execution contracts that every backend must support
- [[00-moc-ai-engineering|MOC AI Engineering]]
