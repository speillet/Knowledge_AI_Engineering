# Routing LLM — Flashcards
Tags: #flashcards #ai-engineering #routing #api-layer #llm
<!-- summary: static, rule-based or semantic routing, RouteLLM, cascade, load-based routing, semantic cache, calculation of the average cost of a cascade, router bias, counterfactual decision. -->


Why route queries between multiple models? <!--anki:6a5b33407a5a3140415e-->
?
Because **no model is optimal everywhere**: the majority of queries are simple and can go towards a **small, fast and cheap model**, reserving the **powerful model** for difficult cases. We optimize the triangle **cost / quality / latency**.

Order of magnitude: if 70% requests go to a model ten times cheaper, the average cost becomes 0.7 × 0.1 + 0.3 × 1 = 0.37 the initial cost, either −63%, As long as the quality is on these 70%. The router also costs: a few milliseconds for rules or a embedding, a full call if it uses a LLM.

---

What is Static Routing? <!--anki:44773775513569557677-->
?
A **model set by use case** (→ classification small model, legal writing → large model). Simple and predictable, this is the recommended **starting point**.

The choice comes from reviews of the use case, not just the "simple" or "complex" label. A small model can be excellent for a specialized format, and a large model can still fail. This stable baseline is used to measure whether a more dynamic routing brings enough gain to justify its complexity.

---

What is rule-based routing? <!--anki:5162254473514a51595d-->
?
**heuristics** on the request: prompt length, language, code presence, client or tenant, subscription level. Deterministic and easy to audit.

Example: Send too long an entry to a model with sufficient context. Set priorities if multiple rules apply and an explicit default route. Confidentiality or region requirements are hard constraints; they should not be bypassed by a cost rule.

Test Boundaries: A query just above the threshold should keep enough room for output and tools. Journaling the winning rule helps explain an unexpected route.

---

What is Semantic Routing? <!--anki:416e31782d254b435577-->
?
The **embedding of the query** is compared to reference examples for each route (e.g. "support", "code", "off topic") and the closest route is chosen. Fast and no-call LLM.

In practice: a few dozen example sentences per route, and a **similarity threshold** under which the request goes to a default route. The threshold is set on a game labeled: too high, everything falls into the default route; too low, off-topic requests are captured. Limit: proximity captures the subject, not the difficulty.

---

What is a learned router (e.g. RouteLLM)? <!--anki:733a60734a2a716f745b-->
?
A model learns, from comparisons or results, **when a more expensive backend brings a useful gain**. A threshold sets the cost/quality trade-off for the models and the traffic evaluated.

Example: A short sentence containing a legal exception can be difficult; length alone is not enough to route. Evaluate orientation errors by task type and severity, with climbing capability.

Compare to a static rule by including router cost and latency. After changing candidate models, recheck labels, calibration and threshold: a router trained for one pair does not automatically predict the behavior of another.

---

What is a model cascade? <!--anki:704a444b343c593f2c61-->
?
First send the request to the **cheap model**, **check** the response (format validation, trust score, judge) and **climb** to a more powerful model only in case of failure.
```text
80% queries: small model → 1 × the cost
20% scaled: small + large model → 1 × + 12 × = 13 ×

Average cost ≈ 0.8 × 1 + 0.2 × 13 ≈ 3.4 vs 12 in all-size
```
The calculation only holds if the **verification is reliable and cheap**: otherwise we pay twice for an uncertain result.

Add its cost to each request, then measure false chords and false rejections. A false chord lets pass an erroneous response; a false rejection reduces the economy. The scaled cases also undergo the two sequential latencies.

---

Do not confuse: routing and fallback? <!--anki:66313d487a55554a5a34-->
?
The **Routing** choose the model **before** the call (optimization); on the **Fallback** Switching to another model **After an error** (blows, rate limit, timeout) — it's the **Reliability**, Run by the[[81-litellm-api-layer|API layer]].

A fallback must be admissible for the same contract: access to data, context length, tools and output format. A poor quality response can trigger a cascade, which is another mechanism. Trace the reason for the choice or the toggle makes it possible to distinguish quality problem and technical incident.

---

What is load-based routing? <!--anki:47573371746971216e2e-->
?
Split between **replicas of the same model** according to their state: queue, latency, [[61-kv-cache-attention|KV cache]] occupancy, or even **prefix affinity** (send the request where its prefix is already cached).

A cache affinity saves prefill but can overload a popular replica; the decision must balance reuse and queue wait. Use recent signals and limit oscillations. Test with realistic prompt sequences, because random queries without shared prefixes do not reveal this compromise.

---

On what to base a routing decision? <!--anki:673d62522f6f49603563-->
?
On **[[92-chainforge-evals-prompts|evals]] per request segment** (quality of each model by type of task) and on **production data** ([[91-langfuse-observability|Langfuse]]: cost, latency, feedback). Without measurement, the router saves by degrading quality without knowing it.

Example: the eval shows that the small model equals the big one on status issues, 98% against 99%, but falls on litigation, 61% against 88%. We drive by category, then we check in production that the actual distribution resembles that of the eval: a slide towards litigation degrades the quality without any alert.

---

What is a semantic cache? <!--anki:702925434b335a303e56-->
?
Return an already generated **answer** for a question **semantically close** to a past question. Big gain in cost and latency, but risk of **bad answer** if the similarity threshold is too permissive.

Two related questions may differ by negation, date, or user. Include holding, permissions, and source versions in cache access conditions, and then provide invalidation and control of hits. Reserve this technique for tasks where a re-used response is acceptable and measurable, not for data changing with each request.

---

Do not confuse: the four decisions around the model? <!--anki:7265624f26605e34686c-->
?
```text
Routing → BEFORE the call, choose the right model (optimization)
Cascade → AFTER a quality failure, climb (optimization)
Fallback → AFTER technical error, toggle (reliability)
Retry → AFTER transient error, try again (reliability)
```
The first two are aimed at **cost and quality**, The last two la **Availability**. They often live in the same component, the [[81-litellm-api-layer|gateway]], but answer different questions ([[142-llm-reliability-resilience|Reliability]]).

For example, route an extraction to a small model, scale if quality control fails, switch if the provider is unavailable, and try again briefly on a transient error. Share an overall budget between these mechanisms: their composition can otherwise multiply calls and exceed the user delay.

---

Calculation: a waterfall uses A to 0.002 € then B to 0.020 € for 25% requests. What average cost before other times? <!--anki:3866303963663363386636343466323261316261666166396462353135303736-->
?
A is called for all requests and B for a quarter: `0,002 + 0,25 × 0,020 = 0,007 €`, or **7 € for 1,000 requests**.

The calculation assumes constant costs and a single escalation. Add the cost of the router, checks and retrievals if they exist. Also measure the quality of the requests that remain on A: a cheap cascade can under-detect difficult cases. The escalation rate alone shows neither preserved quality nor net economy.

---

Why evaluate only queries sent to the large model biases the comparison with the small one? <!--anki:3263313832643862306231643463323239323936326437353831666638656334-->
?
The router can reserve **the most difficult cases**. A lower average quality of the large model on this subset does not mean that it is less capable.

Compare the two on a common representative sample or organize a controlled exploration, with costs and data rules respected. Keep the routing decision and its criteria. The results observed after selection are not enough to estimate what the other model would have done.

---

When should a waterfall abstain instead of climbing to a more powerful model? <!--anki:3762313434376663653134363435636561306137643237353333663638333038-->
?
When the problem comes from **absent evidence, denied permission, or user ambiguity**, not a lack of capacity of the first model.

Climbing can increase the cost without solving the cause. Classify the reasons for failure and provide additional research, clarification or human review. Measure the resolution rate by reason: a useful cascade improves the end result, not just the number of responses produced.

---

## Scenarios

Scenario: your management asks to halve the cost of the assistant, without degrading the perceived quality. How do you proceed? <!--anki:702a4c60414f3b6c6136-->
?
1. **Segment traffic**: which queries are simple, which are difficult, in what proportions
2. **Measure by segment**: quality of the small model against the big one, on each segment ([[94-evals-methodology|evals]])
3. **Start with static routing or rules**, predictable and auditable, before any router learned
4. **Cascade** on uncertain segments: small model, check, escalation if failure
5. **Check next**: cost per request, quality per segment, escalation rate, user feedback

**Trap** : route on the only length of the prompt, who says nothing about the real difficulty.

---

Scenario: a colleague offers a semantic cache for questions “close” to the previous ones, about a banking assistant. What reservations do you pose? <!--anki:457145645a3a603e465f-->
?
1. **The main risk**: Two seemingly close questions can be answered oppositely (“can I close my account?” depending on the type of account)
2. **The similarity threshold** becomes a critical parameter, to be calibrated on real cases
3. **Closure**: never cache shared between users when the answer depends on their data
4. **Limit the perimeter**: reserve the cache to questions **generic**, factual and without customization
5. **Measure**: hit rate, but especially inappropriate response rate served from cache ([[123-aggressive-caching|caching]])

**Trap**: Measure the success of the cache at its hit rate, without checking the correctness of the answers served.

---

## Connections
- [[81-litellm-api-layer|LiteLLM]] — where routing is implemented
- [[91-langfuse-observability|Langfuse]] — decide based on observed data
- [[92-chainforge-evals-prompts|Evals]] — measure quality by model
- [[64-inference-metrics-slo|Metrics & SLO]] — latency constraint
- [[121-inference-costs|Inference costs]] — cost lever n°1
- [[66-prefix-caching-radix-attention|Prefix caching & RadixAttention]] — Prefix affinity routing
- [[123-aggressive-caching|Caching agressif]] — all cache levels
- [[146-model-selection|Choice of model]] — criteria and benchmarks
- [[138-reasoning-models|Models of Reasoning]] — router by difficulty
- [[122-finops-llm|FinOps LLM]] — allocate and drive AI spend
- [[141-system-design-llm|System Design LLM]] — design method
- [[48-agentic-workflow-patterns|Patterns of workflows]] — chaining, routing, evaluator-optimizer
- [[53-synthetic-data-distillation|Synthetic Data & Distillation]] — generate data and transfer to a small model
- [[00-moc-ai-engineering|MOC AI Engineering]]
