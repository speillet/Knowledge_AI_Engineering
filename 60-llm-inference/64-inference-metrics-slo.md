# Inference Metrics & SLO — Flashcards
Tags: #flashcards #ai-engineering #inference #slo #llm
<!-- summary: TTFT, TPOT and ITL, useful content and reasoning, offered/admitted/useful bitrates, SLO spouses, timeouts, burn rate, Little's law, autoscaling and benchmarks, calculation of duration up to the last token, percentile aggregation, latency budget. -->


What is the TTFT? <!--anki:68355e7b7b31743d5d46-->
?
**Time to First Token** : time between sending the request and the **First token received**. It depends on the queue and the **prefill** (Length of Prompt). This is the reactivity perceived in streaming.

Specify the measuring point: the TTFT client side includes network and intermediaries, The engine can exclude them. The first event of the protocol is not necessarily a token Displayable. A TTFT high may come from a saturated queue, a missing cache or input calculation; separate these components to diagnose.

---

Do not confuse: TPOT and ITL? <!--anki:68424b38777e6e2a472f-->
?
The **TPOT** is the average time per token after the first: `(duration − TTFT) / (output tokens − 1)`, for at least two tokens. The **ITL** describes the intervals between successive emissions; its granularity depends on the instrumentation.

A TPOT of 30 ms can hide a long pause. The percentile of TPOT per request differs from the percentile of all intervals, to which long responses contribute more. A network chunk can contain multiple tokens. Exclude or distinguish outputs from zero or one token, and document the tool convention.

---

What latency targets are appropriate for each use case? <!--anki:6f5537494a4a4244263c-->
?
Targets depend on the experience expected; Here are **examples of budgets to validate with users** :
```text
autocomplete a few hundred milliseconds
Interactive voice aim for quick speaking, around a second
streaming chat first text in less than a second if possible
asynchronous agent visible progress and announced end time
batch processing deadline, debit and priority cost
```
Measure on the client side, under load and in percentiles. The reading speed varies according to language and content. Even in batch, the latency counts if the processing must end before a time limit ([[144-ai-ux-human-in-the-loop|UX]]).

Specify what counts as the first useful content: a quick heartbeat or “I think” does not necessarily respect the promise of the product.

---

How does end-to-end latency break down? <!--anki:797160634d527b2e5e4d-->
?
```text
E2E ≈ TTFT + TPOT × (nb tokens output − 1)
```
A long answer is therefore dominated by the TPOT, a short answer on a long prompt by the TTFT.

With a TTFT of 0.5 s, 101 tokens and an average TPOT of 0.03 s, the generation lasts about **3.5 s**. This formula assumes a consistent measurement from the first to the last token; tools, rendering and post-generation processing are added to measure the entire application experience.

Do not add p95 of the TTFT and p95 of the TPOT to obtain a global p95: these quantiles can concern different requests. First calculate the duration of each request.

---

What is the throughput of an inference service? <!--anki:49216f726b2d6a6f292d-->
?
The **rate** of the service: **tokens output per second** (all users combined) or **requests per second**. It determines the **cost per token**.

Specify which tokens are counted: input, output or both. Two services with the same number of requests per second can have very different loads if the answers are not the same length. The unit cost also depends on the price of the infrastructure, its use and the part of the answers actually exploitable.

---

What tradeoff exists between latency and throughput? <!--anki:7a332c303b47545233-->
?
A larger batch can increase the **aggregate throughput** by reusing the weights, but each iteration ends up costing more and expectations can get longer. The effect on the TPOT is neither constant nor always monotonous: it depends on the memory/calculation regime, lengths and scheduler.

Scan batch loads and budgets. Hold maximum throughput that meets latency and quality objectives, with a margin for traffic variations. Include queue; a fast engine behind a saturated queue remains slow for the user.

---

What is goodput? <!--anki:4b7157417d2d3c3f7e39-->
?
The bitrate **of the only requests that meet the SLO** (TTFT and TPOT below the thresholds). More honest than raw throughput: serving requests outside SLO quickly does not count.

Precisely define the unit: successful requests per second, or tokens associated with these requests, with all applicable criteria. If 100 requests/s are served but only 70 meet quality and time requirements, the payload speed is 70 requests/s according to this definition. Compare variants with the same thresholds.

---

Why use percentiles for inference latency? <!--anki:4b306636786f4b446d71-->
?
Because the average hides the **distribution tail**: we set the SLO to **p95/p99**. An excellent p50 with a p99 of 20 s remains a bad experience for 1% users.

The p95 indicates that about 95% of observations are below this value, not that any query will have this delay. Set window and traffic segment, and then verify that there are enough observations to estimate the queue. Separating prompts short and long helps to prevent a mix change from masking a regression.

---

What does an inference SLO look like? <!--anki:6b77706546525e735472-->
?
An encrypted goal on a time window, for example:
```text
p95 TTFT < 800 ms, p95 TPOT < 50 ms, availability ≥ 99.5% on 30 days
```
It drives the sizing, the [[83-gateway-ingress|Timeouts and Rate Limiting]].

Specify which queries are included in the calculation, how to handle errors and cancellations, and where times are measured. Also define the error budget and alerts that trigger an action. The values above are an example of a product contract; they do not constitute a valid standard for all uses.

---

What signals to use for autoscaling a LLM inference server? <!--anki:6e46644e3e766a2e4a7d-->
?
Combine **waiting for the oldest job**, queue size, tokens remaining to be processed, KV occupancy, preemptions and SLO compliance. Ten long prompts do not represent the same load as ten short messages.

The GPU activity completes the diagnosis; alone, it does not distinguish the necks. Calibrate the thresholds by model and traffic mix, anticipate loading weights and warm-up, then check the actual readiness. Keep a reserve adapted to the peaks and drain the requests before reducing the number of replicas. Test also the loss of a replica.

---

How to measure the performance of a LLM inference deployment? <!--anki:505e777663703b53257c-->
?
Build a **→ free load curve, errors, and goodput**, with representative lengths and arrivals. Tools like `vllm bench serve`, GuideLLM, or genai-perf help run it.

Example: Two servers have the same p95 on completed responses, but one rejects 20% requests. They do not offer the same service: include denials, timeouts, and results consistent with SLO in the balance sheet.

Fix model, quality, input/output distribution, warm-up and cache status. Swipe through to saturation, then test spikes. A peak of tokens/s on short prompts does not certify production capacity or latency on long documents.

---

Calculation: in steady state, with 10 requests/s completed and 8 s of average file duration included, how many requests are in flight on average according to Little's law? <!--anki:44597b556d555a6b6b32-->
?
**Little's Law** in stable operation, with flow and duration measured at the same perimeter:
```text
L = λ × W = 10 req/s × 8 s = 80 flight requests on average
```
If the 8 seconds include waiting, these 80 queries include **file and execution**. This does not mean 80 active sequences in GPU, nor a KV reservation determined.

Separately sizing the memory of the actual resident tokens, their growth and shared blocks. This relationship covers averages; it provides neither concurrency p99, nor capacity margin, nor guarantee of lead time overload.

---

Do not confuse: free, admitted, finished and useful? <!--anki:3666356538323836666565633432333239346636646538626530383234313834-->
?
The **debit offered** counts the requests arriving at the chosen perimeter; the **admitted**, those accepted; the **completed**, those having reached a final state; the **goodput**, the successes meeting the criteria set.

Also track refusals, abandonments and changes in the number of in-flight requests. A server can display excellent latency after rejecting half of the requests. Counting technical attempts and user tasks separately: three entries do not create three successful tasks. Keep the same perimeter and the same window to compare configurations.

---

Calculation: Do two criteria each met by 95% queries guarantee 95% joint compliance? <!--anki:3766323866373230643236353432626339323037616335643366326434643963-->
?
No. On 1,000 requests, 50 may miss the TTFT and **50 others** the TPOT: only 900 respects both, i.e. **90%**. If the two chess groups coincide, the result is 95%.

Measure the intersection **per request**, with technical success and quality when the latter is observable. If these 1,000 requests arrive in 100 seconds in steady state, and 900 are compliant, the goodput is worth 9 requests/s. Marginal histograms are not enough to reconstruct this intersection.

---

How long does it take for a model to reason before responding? <!--anki:3465373330633361393930363435363139323162313330633838623137333461-->
?
Distinguish between **first event**, first token generated or received, **first visible useful content**, and completed response. Explicitly name the delay to the first useful content, for example TTFU in the local contract: this acronym is not a universal convention.

A metadata event or hidden reasoning does not necessarily satisfy the user's expectation. Separately follow tokens visible, tokens reasoning exposed in use and tokens charged; conventions vary. A short response to the screen can consume a lot of computation and arrive late.

---

How do I count timeouts and cancellations in latency metrics? <!--anki:3038353239383363653338613432633638363964326533626637666331363136-->
?
A timeout is a **Unfinished result**, not a pass latency equal to the threshold. Publish its observed frequency and time separately; The length of time required for a complete response is unknown.

Keep these requests in the SLO denominator according to the contract. Distinguish between voluntary abandonment, timeout, rejection and disconnection after error. The percentiles of the successes alone can improve when the slower requests fail. Also check that the cancellation actually releases calculation and KV, otherwise the load continues despite the disappearance of the client.

---

Calculation: what burn rate for 4% violations with a SLO to 99%? <!--anki:3832346261303930623339333434316638626232646663323934326266663865-->
?
The authorized budget is **1%** of non-compliant events. An observed rate of 4% gives `4 / 1 = 4`: consumption four times faster than the pace compatible with the objective, with comparable traffic and perimeter.

This calculation uses eligible events, including contract errors, not the p95 value. Combining short and long windows to distinguish between fast incident and persistent degradation. The time until exhaustion depends on the remaining budget and future traffic; it is not deducted from the ratio alone.

---

Calculation: The first of 400 tokens Comes after 0.8 second, Then each interval between tokens Hard 20 MS. How long until the last token ? <!--anki:6231653834363131386530393437303338363562623430383161366235353138-->
?
There are **399 intervals** remaining after the arrival of the first token. The total duration is `0,8 + 399 × 0,020 = 8,78 secondes`, excluding additional processing after the last token.

A TTFT less than one second does not mean a complete response in one second. The calculation assumes constant intervals and a token emitted per observed event. In practice, the transport can group tokens; measure the reception on the client side and distinguish token, network chunk and useful content. The average rate does not alone describe the pauses felt.

---

Calculation: a service satisfies its SLO on 990 requests on 1,000 in the morning and 50 on 100 in the evening. What overall rate does one get, and what would hide the average of the two percentages? <!--anki:3766383130653632316132383438306339313731636661303061353934643562-->
?
The overall rate is approximately **(990 + 50) / (1,000 + 100) = 94.55%**. The unweighted average of 99% and 50% gives 74.5%, which does not represent the fraction of compliant queries.

The overall rate also hides the strong degradation of the evening. Publish volume and compliance by window in addition to the aggregate. Define whether the SLO relates to requests or to time windows: the denominators correspond to different contracts.

---

Calculation: a TTFT budget of 1,000 ms reserves 120 ms to the network, 80 ms to the controls and 300 ms to the prefill. What maximum wait is left, assuming these sequential steps and these fixed durations? <!--anki:3765303163383935336466343436356238343661333635663661393235666463-->
?
The queue budget is worth **1,000 − 120 − 80 − 300 = 500 ms**.

This is a design budget under fixed assumptions. Adding the p95 of each component does not usually give the p95 end-to-end. Measure the correlated durations per request and check the complete SLO, especially in the presence of covers and cold cache.

---

## Scenarios

Scenario: the product asks "a response in less than 2 seconds" for an assistant that streams answers from 400 tokens. How do you translate this need into SLO? <!--anki:772b352d2f4c5b694141-->
?
1. **Clarify deadline**: first useful text or fully available response, user-side.
2. **Calculate budget**: with 800 ms of TTFT and 400 tokens, finishing in 2 s requires an average TPOT at most equal to `(2 − 0,8) / 399 ≈ 3 ms`.
3. **Evaluate levers**: more concise output, faster model, specific decoding or infrastructure; validate quality and cost.
4. **Definite contract**: Proportion of requests that meet thresholds, window, errors and segments together.
5. **Test under load** before promising these deadlines.

**Trap**: Add percentiles as if they were describing the same request.

---

Scenario: your dashboard displays 100% of GPU usage and the team concludes that you need to buy GPU. How do you check? <!--anki:4a3363746c6836453d3b-->
?
1. **Interpreting activity**: A running kernel does not mean that compute or memory is reaching their maximum throughput.
2. **Localize the bottleneck**: files, KV, preemptions, time-by-phase, memory activity and communications.
3. **Trac the load curve** with latencies, errors, and goodput to the same query mix.
4. **Test a targeted leverage**: batch, cache, quantization or context; measure its counterparties.
5. **Dimension the reserve** according to expected peaks, startup, outage and admission policy.

**Pip**: Buy calculation based on GPU usage, which measures kernel occupancy and not computational or memory saturation.

---

Scenario: your autoscaling is triggered too late, and requests wait several seconds before being processed. On what do you rule? <!--anki:6c6759312a4c4c493574-->
?
1. **Anticipate** with queue age, work in tokens, occupation KV and load trend.
2. **Measure the actual start**: loading, compilation, warm-up, then readiness.
3. **Keep a reserve** consistent with this time frame and the spikes to be absorbed.
4. **Born the queue** and apply a scheduled downgrade if queries can no longer meet their deadline.
5. **Burn rate alert**: fraction of requests violating the SLO divided by the allowed error budget.

**Trap**: Calculate a burn rate of p95. A percentile is not a fraction of failed events.

---

## Sources

- [Google SRE — error alerts and budgets](https://sre.google/workbook/alerting-on-slos/)
- [vLLM — metric definitions](https://docs.vllm.ai/en/latest/design/metrics/)
- [DistServe — goodput and SLO spouses](https://arxiv.org/abs/2401.09670)

## Connections
- [[61-kv-cache-attention|KV cache]] — concurrency capped by VRAM
- [[62-inference-optimizations|Inference optimizations]] — levers on TTFT and TPOT
- [[12-kubernetes-gpu-inference|Kubernetes GPU]] — autoscaling driven by these signals
- [[83-gateway-ingress|Ingress & API gateway]] — rate limiting and timeouts
- [[91-langfuse-observability|Langfuse]] — from system to application
- [[121-inference-costs|Inference costs]] — goodput ↔ cost per token
- [[67-speculative-decoding|Speculative Decoding]] — reduce the TPOT
- [[68-quantization|Quantization]] — more throughput and concurrency by GPU
- [[93-monitoring-inference|Monitoring of inference]] — concrete metrics (vLLM, GPU, usage)
- [[69-roofline-prefill-decode|Roofline & Disaggregation]] — interference prefill/decode behind TPOT peaks
- [[163-real-time-voice|Voice & Real-Time Agents]] — the TTFT in a conversational latency budget
- [[112-model-cicd|CI/CD models]] — eval gates, canary and rollback
- [[138-reasoning-models|Models of Reasoning]] — test-time compute and budget reflection
- [[142-llm-reliability-resilience|Reliability & resilience]] — timeouts, recoveries, fallbacks and degradation
- [[66-prefix-caching-radix-attention|Prefix caching]] — Reuse the calculation of common prefixes
- [[81-litellm-api-layer|LiteLLM]] — the gateway between applications and models
- [[82-routing-llm|Routing LLM]] — choose model by query, fallbacks and semantic cache
- [[84-streaming-application-integration|Streaming & integration]] — SSE, cancellation and long tasks
- [[137-long-context|Long context]] — limits and cost of long windows
- [[146-model-selection|Choice of models]] — criteria, benchmarks and migration
- [[116-ai-sre-incidents-capacity|SRE: incidents & capacity of AI services]] — connect capacity and user experience
- [[60-010-inference-load-benchmarks|LLM Load Benchmarks]] — measure capacity without hiding files and failures
- [[60-013-prefill-decode-step-by-step|Prefill & decode step by step]] — track calculated positions, cache and delays
- [[00-moc-ai-engineering|MOC AI Engineering]]
