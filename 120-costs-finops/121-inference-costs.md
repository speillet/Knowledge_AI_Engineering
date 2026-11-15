# Inference costs — Flashcards
Tags: #flashcards #ai-engineering #finops #costs #inference #llm
<!-- summary: cost structure of a call, calculation of the cost of an agent of 20 turns with and without cache, price input and output, prompt caching, cost of self-hosting, break-even API or self-host, batch API, technical levers, long context, unit economics, GPU idle, cost per compliant point-and-energy cache, cost per compliant point-and-energy. -->


How to structure the cost of a call LLM API ? <!--anki:4f444670265626663e6d-->
?
**Price per million tokens**, differentiated **input / output** (separate prices depending on the offer), with possible additional costs (reasoning, long context).
```text
cost = (tokens_in × price_in + tokens_out × price_out) / 1,000,000

Example (illustrative price: 3 €/M as input, 15 €/M as output)
  3,000 tokens input + 500 output
  = (3,000 × 3 + 500 × 15) / 1e6 = 0.009 + 0.0075 = 0.0165 €/request
  × 1 million requests per month ≈ 16,500 €
```
The contribution of each item depends on the product **volume × rate**. A first calculation helps to frame the project ([[141-system-design-llm|System Design]]).

Counting **calls actually executed**, including failed attempts and new attempts according to billing rules. Distinguish between regular entry, hidden entry and possible additional positions in usage data. The cost of a conversation is the sum of its calls; the same instruction returned at ten turns can be counted several times.

---

Do not confuse: price per token and cost per successful task? <!--anki:44393742637863294c-->
?
The **price per token** describes a rate. The **cost per successful task** reports all expenses to the acceptable tasks: tokens actually used, scrapes, escalations, tools and verification.

For example, one model at 0.007 € per attempt succeeding 70% of tasks costs `0,007 / 0,70 = 0,01 €` of success on this population. Another at 0.01 € with success 95% costs about 0.0105 €. An increase in the failure rate therefore does not mechanically cancel a discount of 30%.

---

Why do output tokens cost more than input? <!--anki:62606640475e324b5f71-->
?
Autoregressive generation advances sequentially, while the prefill further parallelizes the input tokens. This explains **different resource profiles**, without imposing a universal price ratio.

The tariff is a commercial policy: compare entries, exits, reasoning, cache and possible tiers of the chosen provider. Use dated rates in the calculation. A concise exit can save time and money, but a `max_tokens` too low leads to truncations and recoveries. Measure the cost per successful task rather than apply a fixed rule "exit three to five times more expensive".

---

What effect does prompt caching have on the bill? <!--anki:796c756e764b716c6232-->
?
Among the suppliers who offer it, the re-used entry **tokens** benefit from a specific rate, often reduced ([[35-context-engineering|prompt caching]]). Writing, storage or TTL can change the balance sheet.

Fictional example, excluding additional writing costs: 10,000 tokens to 2 €/million cost 0.02 €. If 8,000 are read at 0.50 €/million and 2,000 at the normal rate, the input costs **0.008 €**, i.e. 60% output separately.

Measure tokens effectively reused and billed, not just repeat the prompt. In self-hosting, the gain is a matter of avoided calculation and freed capacity, not necessarily a discount by token.

---

How is the cost of self-hosting calculated? <!--anki:455d7b3a6f6040737e3c-->
?
Use of **Coherent Units** :
```text
cost/token = total cost per hour / tokens useful per hour
          = hourly cost / (average throughput in tokens/s × 3,600)
Fateful example: 3.60 €/h and 100 tokens/s → 0.00001 €/token
```
Include GPU, CPU, storage, network, operation and idle periods. The retained throughput must match the actual load and the [[64-inference-metrics-slo|SLO]], not the theoretical peak. Then compare the cost per successful task, because an inexpensive token does not guarantee a useful response.

In the example, this corresponds to **10 € per million useful tokens**. If the machine only serves half of this average throughput while remaining charged, this unit cost doubles. Specify whether the counted tokens are outputs or an input/output mix, so as not to compare different units to a API rate.

---

API or self-host: where is the break-even? <!--anki:4f5871495e2e6540443a-->
?
- **Self-host** profitable at **high constant volume** and high usage GPU
- **API** gains at low volume or irregular load (no GPU idle, implicit scale-to-zero)

Compare to equivalent quality, latency, and availability, with operating cost and backup capacity included. Peaks sometimes require you to pay an unused reserve the rest of the time. The threshold is calculated on the load profile and actual rates; a hybrid model can absorb the base locally and spikes by API.

---

What is a API batch? <!--anki:434167563b555a475567-->
?
A **batch API** accepts a batch of requests for asynchronous processing, with a processing window, quotas and vendor-specific rates. It is suitable for evals, extractions and enrichments that support a delay.

A discount of 50% and a window of 24 hours are examples of offers, **not a universal guarantee of success of each line**. Some requests fail or expire. Associate an identifier with each entry, recover statuses and resume only the necessary lines ([[148-llm-batch-pipelines|pipelines batch]]).

---

Which technical levers reduce the inference cost of a LLM? <!--anki:4a616c7c46297d3f3e52-->
?
- **[[82-routing-llm|Routing]]** to a cheaper model for simple queries
- **Prompt caching** of the stable prefix ([[123-aggressive-caching|caching]])
- **Shorter prompts** and sorted context, `max_tokens` limited
- **Batch API** for non-interactive
- Self-hosted: **[[68-quantization|quantization]]** and GPU well-filled

Always measure the effect on quality: an economy that lowers the success rate increases the **cost per successful task**.

A fictitious example: switching from 0.04 € to 80% of success to 0.03 € to 50% increases the cost per success from 0.05 € to 0.06 €.

---

What does the long context really cost? <!--anki:70715578642e522529-->
?
Each context token costs **three times**: in money (billing), in latency (prefill) and in VRAM ([[61-kv-cache-attention|KV cache]]) — sort its context, it is saving.

These three dimensions do not necessarily translate into three invoice lines: VRAM is mostly a self-hosting capacity cost. The cache can reduce part of the prefill and the input price, but the context remains to be managed when decoding. Removing the noise helps; removing a necessary proof degrades the result.

---

What are the unit economics of a LLM feature? <!--anki:7135367b5678255e2b5b-->
?
The **cost per request / user / feature related to the value produced** — the metric that decides if an AI feature is viable.

For example, relate the total cost of a processed file to the time actually saved or the margin generated. Include recoveries, failures, human verification and external tools. An average per request can hide a small number of very expensive tasks; segment by use and also track percentiles.

Distinguish between marginal cost and full cost: A GPU already paid can make an additional call cheap, without making profitable a feature that immobilizes capacity all day long.

---

Why does an unused GPU cost as much as an active GPU? <!--anki:692b24734c473647792f-->
?
With an hourly rental, the cost of booking remains due during inactivity; energy and other charges may vary. At constant hourly cost, produce **five times less than useful tokens** multiplies their unit cost by five.

This reasoning does not follow from an indicator GPU to 20%: Kernel activity and useful production are not proportional. Adjust replicas, mutualization and schedules according to the measured load, retaining isolation and SLO. The scale-to-zero saves booking only if billing and resource lifecycle allow it.

---

Calculation: an agent made 20 Towers, with 5,000 tokens at the beginning, +2,000 tokens historical nets per turn and 300 exit by turn. To 3 €/M as input and 15 €/M out, what cost without cache then with prefixes read to 10% of the tariff, Without the additional cost of writing? <!--anki:43757a68396e6c7c3d49-->
?
Assumptions: 5,000 tokens at start, +2,000 tokens history net per turn (previous output and tools included), 300 tokens output per turn, 3 €/M input, 15 €/M output.
```text
cumulative input = 20 × 5,000 + 2,000 × (0 + 1 + ... + 19) = 480,000 tokens
without cache: 480 k × 3 €/M + 6 k × 15 €/M ≈ 1.53 €
with cache: ~43 k new tokens at full price
             ~437 k reread to 10% ≈ 0.35 €
```
Without a cache, the input volume has a **quadratic** term in terms of number of turns: 40 turns cost about 3.5 times more than 20. Hence the **compaction** and cache ([[123-aggressive-caching|caching]]). The additional cost of writing in cache is neglected here.

---

Calculation: 2,000 People are 10 requests per day on 22 days, each with 2,000 tokens Entry and 400 Exit. To 3 €/M as input and 15 €/M out, What monthly cost? <!--anki:6165653035666139373336363437383461383262393763386636316462633865-->
?
Assumptions: 10 requests per person and per working day, 22 days, 2,000 tokens Entry and 400 output by request, 3 €/M at the entrance, 15 €/M out.
```text
requests: 2,000 × 10 × 22 = 440,000 per month
entry: 440 k × 2,000 = 880 M tokens × 3 €/M ≈ 2,640 €
output   : 440 k ×   400 = 176 M tokens × 15 €/M ≈ 2 640 €
total ≈ 5,300 € per month, ≈ 2.60 € per person
```
Entering and exiting weigh as much, Because the exit costs 5 times more expensive token. A RAG who carries the entrance to 8,000 tokens by request would multiply the entry share by 4 ([[122-finops-llm|FinOps]]).

---

Calculation: GPU reserved 720 h to 2.50 €/h replaces a comparable API to 0.20 €/M of tokens. Excluding operation, what monthly volume and average throughput on 30 days equalize costs? <!--anki:3165666632316363393062643430633161363538303761346166313231356365-->
?
Fictional assumptions: an H100 leased 2.50 €/h, which serves a small open weights model; a API equivalent to 0.20 € per million tokens, entry and exit combined.
```text
GPU 24 h/24: 2.50 € × 720 h = 1,800 € per month
break-even: 1,800 € / 0.20 €/M = 9,000 M tokens per month
equivalently: 9e9 / (30 × 86 400 s)     ≈ 3 500 tokens/s, continuously
```
It takes a load **supported day and night** to beat a cheap API; if the realized volume remains below this threshold, the API is cheaper on this perimeter. And this calculation forgets the exploitation: engineers, supervision, updates ([[164-local-edge-llm|on-prem]]).

---

Calculation: A costs 12 €/h for 20 compliant responses/s; B, 8 €/h for 10, to the same mix and SLO. What cost per compliant response and which one is the cheapest at this charge? <!--anki:3933613530313832313337613439336538616165373939613865613434663562-->
?
A costs **12 €/h** and delivers 20 compliant responses/s; B costs **8 €/h** and delivers 10/s, on the same mix and with the same criteria.
```text
A: 12 / (20 × 3,600) ≈ 0.000167 €/compliant response
B: 8 / (10 × 3,600) ≈ 0.000222 €/compliant response
```
A is more expensive by the hour but cheaper by success at this charge. Include in the cost the failures and the reserve actually paid. Redo the calculation to the expected volume: an unused capacity does not automatically produce its maximum goodput.

---

Calculation: a server consumes on average 600 W during 60 s and delivers 120 compliant tasks. How many joules does it consume in total and per useful task? <!--anki:3764316232316465383563393465363338626662363766333136623261333262-->
?
On a window of 60 seconds, an average power of **600 W** represents `600 × 60 = 36 000 J`. If 120 compliant tasks are delivered, this gives **300 J per useful task**.

Specify the perimeter: GPU alone, server or complete installation; integrate all the energy of the perimeter, including failures and waiting. Instant watts are not enough to compare two variants. Measure quality and time at comparable load. Switching from joules to carbon requires in addition an electrical intensity located in time and space, with explicit assumptions.

---

Calculation: a Cache Passes 40% of 10,000 Requests for 0.01 € To 0.001 €, with 15 € of fixed costs. What net economy? <!--anki:3032306430336164656136323439346638616530636535313139306331643730-->
?
Without cache: `10 000 × 0,01 = 100 €`. With cache: `4 000 × 0,001 + 6 000 × 0,01 + 15 = 79 €`, i.e. **21 € saved**.

The hit rate must cover these comparable requests and the answers must remain valid. Add invalidation, storage or verification costs if not included. A high hit rate is not an economy in itself: it is necessary to compare the full costs and verify that the outdated errors or answers do not increase the business cost.

---

Calculation: 10,000 tasks cost 120 models €, 30 tools € and 50 human review €; 8,000 are solved correctly. What cost per task submitted and by useful success? <!--anki:3564303131643832663665333431363861303263623364343465366235643638-->
?
The total is **200 €**, i.e. **0.02 € per submitted task** and **0.025 € by useful success**.

The two indicators have different denominators. Reducing the cost of models by degrading the success rate can increase the second. Add fixed or recovery costs when they belong to the scope studied; do not compare two solutions with different accounting scopes.

---

Calculation: a cache costs 100 € per month and saves 0.005 € per hit, without any other effect. How many monthly hits does it take to cover its cost? <!--anki:3731646434623738646335313439326261663364616466613139303633373735-->
?
The breakeven is worth **100 / 0.005 = 20,000 hits per month**. Beyond that, the economy becomes positive according to these assumptions.

Counting hits that are actually reusable, after checking for freshness and entitlements. Storage, writes, mining, and cache errors can change this threshold. An excellent hit rate on tiny traffic may remain insufficient to cushion the infrastructure.

---

## Scenarios

Scenario: your management asks whether to switch from the API to self-hosted models to save money. How do you calculate? <!--anki:625447595134405e4423-->
?
1. **Measure actual volume**: tokens input and output per month, hourly profile, peaks
2. **Cost API**: price per million of tokens, taking into account cached tokens and deferred processing
3. **Self-host cost**: cost GPU amortized hourly ÷ actual throughput obtained on your charge, plus operation (on-call, updates)
4. **Compare in the right place**: the self-host gains at **high constant volume** and high usage, the API at low or irregular volume
5. **Don't forget about quality**: a lower self-hosted model can cost more in covers ([[146-model-selection|choice of model]])

**Pip**: Compare a GPU hourly price to a price per token without measuring actual throughput.

---

Scenario: the cost of your assistant is dominated by the input tokens, because of a long context sent to each turn. Which levers, in what order? <!--anki:6950405a5263647b3734-->
?
1. **Prompt caching**: A stable prefix makes most of the input much cheaper ([[123-aggressive-caching|caching]])
2. **Sort Context**: Fewer Recovered Documents, History Compaction ([[35-context-engineering|context engineering]])
3. **Router** simple queries to a cheaper model ([[82-routing-llm|routing]])
4. **Limit output**: `max_tokens` suitable, concise answers, since output costs more
5. **Deferred processing** for anything that is not interactive (evals, enrichment)

**Trap**: start by changing the model, while the context sent is the real cost item.

---

## Sources

- [NVIDIA DCGM — Power and Hardware Metrics](https://docs.nvidia.com/datacenter/dcgm/latest/learn/modules/profiling.html)

- [Anthropic — batch processing, failure and query expiration](https://platform.claude.com/docs/en/build-with-claude/batch-processing)

## Connections
- [[122-finops-llm|FinOps LLM]] — the governance of these costs
- [[64-inference-metrics-slo|Metrics & SLO]] — goodput ↔ cost per token
- [[62-inference-optimizations|Inference optimizations]] — technical levers
- [[35-context-engineering|Context engineering]] — the cost of context
- [[82-routing-llm|Routing LLM]] — pay the right model
- [[123-aggressive-caching|Caching agressif]] — maximize hit rate
- [[68-quantization|Quantization]] — less than GPU per replica
- [[132-tokenization|Tokenisation]] — cost according to language
- [[146-model-selection|Choice of model]] — cost per successful task
- [[164-local-edge-llm|Local LLM]] — on-prem and break-even
- [[148-llm-batch-pipelines|Pipelines batch]] — implement the batch API on a large scale
- [[136-mixture-of-experts|Mixture of Experts]] — total and active settings
- [[138-reasoning-models|Models of Reasoning]] — test-time compute and budget reflection
- [[60-012-inference-optimization-method|Optimization process]] — prioritize and verify gains under service constraints
- [[00-moc-ai-engineering|MOC AI Engineering]]
