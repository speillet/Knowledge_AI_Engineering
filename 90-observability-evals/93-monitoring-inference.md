# Inference & Usage Monitoring — Flashcards
Tags: #flashcards #ai-engineering #observability #monitoring #inference #llm
Verified on: 8 October 2026 — This page lists products, versions or regulatory texts that are evolving quickly.
<!-- summary: monitoring or observability, layers to monitor, vLLM and GPU (DCGM), Use by team, finish_reason, validation of each response, quality signals without field truth, errors and availability, OpenTelemetry GenAI traces, Dashboard, Alerts, Controls before production, detection of regression, Logging of the prompts, aggregation of histograms, Buckets SLO, perimeters of measurement, global throughput and segmentation, missing measurements and telemetry failure, Metrics of queue, Actionable Alerts. -->


What layers should be monitored for an inference service? <!--anki:4f41512c3177716b6679-->
?
Four layers, each with its source:
- **GPU**: health and equipment saturation (DCGM export)
- **Inference server**: queue, KV cache, latencies (vLLM or SGLang `/metrics` endpoint)
- **Requests and usage**: who consumes what, tokens, costs, errors ([[81-litellm-api-layer|gateway]])
- **Quality**: valid and useful answers ([[91-langfuse-observability|traces]], evals)

A problem is often seen in one layer while its cause is in another.

---

What key metrics does vLLM exhibit? <!--anki:715b2636234f51262b58-->
?
In Prometheus format, on `/metrics`:
- **Charge** : `vllm:num_requests_running`, `vllm:num_requests_waiting`
- **Memory**: `vllm:kv_cache_usage_perc`, `vllm:num_preemptions_total`
- **Latence** (histogrammes) : `vllm:time_to_first_token_seconds`, `vllm:inter_token_latency_seconds`, `vllm:request_time_per_output_token_seconds`, `vllm:e2e_request_latency_seconds`, `vllm:request_queue_time_seconds`
- **Volume** : `vllm:prompt_tokens_total`, `vllm:generation_tokens_total`, `vllm:request_success_total` (label `finished_reason`)

Names change from one version to another: check on `/metrics`. See [[64-inference-metrics-slo|Metric & SLO]].

These aggregates can hide a saturated replica: also break down by instance and model. An average of KV to 50% can hide a full GPU and another empty one; it does not describe the available capacity for each query.
```promql
# TTFT p95 on 5 minutes
histogram_quantile(0.95,
  sum(rate(vllm:time_to_first_token_seconds_bucket[5m])) by (le))

# pending requests and cache occupancy
sum(vllm:num_requests_waiting)
avg(vllm:kv_cache_usage_perc)

# Share of truncated answers
sum(rate(vllm:request_success_total{finished_reason="length"}[15m]))
  / sum(rate(vllm:request_success_total[15m]))
```

---

Which GPU metrics to monitor for an inference service? <!--anki:672e573d287b78522835-->
?
With **DCGM**, follow several families:
- **Activity** of SM and DRAM: `DCGM_FI_PROF_SM_ACTIVE`, `DCGM_FI_PROF_DRAM_ACTIVE`.
- **Transfers** PCIe/NVLink, to be brought closer to multi-GPU collectives.
- **Power and health**: `DCGM_FI_DEV_POWER_USAGE`, temperature, frequencies, throttling and XID errors.

A fraction of active cycles do not directly yield either useful FLOP/s or transferred GB/s. Correlate these signals to throughput, kernel times, and queues before concluding at the neck. Available counters depend on GPU, rights, and configuration; some profiles multiplex measurements.

---

Why are GPU usage and the VRAM used misleading metrics? <!--anki:4c64355e3f403432635f-->
?
`DCGM_FI_DEV_GPU_UTIL` only says that a kernel is running: it remains close to 100% even when the GPU is underexploited. The **VRAM used** (`DCGM_FI_DEV_FB_USED`) is also unspeakable, because vLLM **preallocates** the memory (`--gpu-memory-utilization`): this is the **occupancy rate of the KV cache** that must be followed.

Thus, 95% of VRAM occupied at startup, without any query, is normal. These two metrics are used to detect an inactive GPU, absent or occupied by another process; they do not measure a capacity margin. To find out if you can add load, look at the queue and latency under SLO ([[60-010-inference-load-benchmarks|load benchmarks]]).

---

Which usage metrics of the model should be followed? <!--anki:73494d5d7848655a2e6a-->
?
Track requests, input/output/cache tokens, costs, lengths and concurrency by **model, route and bounded usage group**. The gateway allows attribution to the caller; traces or analytical storage carry the detail per user.

Do not create a Prometheus series for each API key, query, or conversation. Labels multiply cardinality and can expose sensitive identifiers. Billed totals may differ from the visible tokens: retain their origin and explicitly process reasoning, cache, fetches, and interrupted generations.

---

What does the distribution of finish_reason reveal? <!--anki:705253437b4d767a2b6e-->
?
The reason each generation stopped:
- `stop` : fin normale
- `length`: **Cut to `max_tokens`**, with truncated answers or invalid JSON. A raise signals a `max_tokens` too low or a pattern that **loop**
- `tool_calls` : appel d'tool
- `content_filter`: blocked by a filter
- `abort` (server side): disconnected client or timeout

We follow his **rate by road and by model**, not just the total.

---

What validations apply to each response in production? <!--anki:786c475440625e38524d-->
?
Inexpensive **deterministic** checks, performed with each response:
- **Format**: JSON parsable and conforming to the scheme ([[63-guided-generation|guided generation]])
- **Tool calls**: existing tool, valid arguments
- **Bornes**: length, expected language, non-empty response
- **Content**: personal data, prohibited content ([[101-llm-security-guardrails|guardrails]])
- **RAG**: presence of expected quotes

Every failure is **counted as a metric** (validation failure rate) and triggers a retry, a fallback or clean error message.

---

Which automatic signals reveal a drop in quality without field truth? <!--anki:6955656e71496a394f63-->
?
Monitor **empty responses, unexpected refusals, loops, repetitions, and length changes**, segmenting by task and language. These variations signal a behavior to be examined, without alone proving a loss of quality.

Logprobs and entropy describe the distribution of the model: low entropy may correspond to a predictable, correct or false response. **No sense of variation is universally good or bad.** Compare to a baseline and confirm on a reread or evaluated sample ([[65-probabilities-sampling|logprobs]]).

---

Which human signals or judged to follow for quality, without field truth? <!--anki:73402f3540435a21636c-->
?
- **User feedback** (inch, reformulations, regenerations)
- **LLM-as-judge** on a sample, segmented by task and language

These signals feed drift detection ([[113-monitoring-drift-feedback|monitoring & drift]]).

Explicit feedback is often rare and biased towards disgruntled or highly engaged users. A reformulation can signal a failure, but also a new request. Cross several signals, calibrate the judge on a human proofreading and check the segments concerned before launching a global correction.

---

What errors and what availability to monitor? <!--anki:6d796f7b3d3f3e262c4e-->
?
- **HTTP**: rate of 5xx, of **429** (rate limit, quota) and timeouts
- **Server**: OOM, CUDA errors, **Pods restarts**, request preemptions
- **Streaming**: Streams interrupted before the end
- **Health**: `/health` and readiness endpoint, which only goes green once the weights are loaded

**Availability** is measured from the customer's point of view (successful ÷ total requests), not just by the fact that the Pod runs.

---

How to connect metrics and traces? <!--anki:77495f4f435b3625542b-->
?
The metrics give the **Aggregate** (p95 has doubled), the Traces Give **Example** (What a request, What a quick one). To connect them:
- a **query ID** propagated from the app to the gateway and then to the server
- on the **OpenTelemetry GenAI Conventions** to name the attributes: `gen_ai.request.model`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, `gen_ai.response.finish_reasons`
- traces emitted by the server itself (vLLM: `--otlp-traces-endpoint`)

Avoiding a query identifier as a label for each metric: This creates a strong cardinality. Use correlation or exemplars when available, and apply the same privacy policy to trace attributes as to business data.

---

What does a minimal inference dashboard contain? <!--anki:4c4c2d5a2c6c683f564b-->
?
The **golden signals** adapted to the LLM:
- Traffic offered and realized, input/output tokens.
- TTFT, generation intervals and total duration per percentile.
- Refusal, timeouts, 5xx, failed validations and unplanned truncations.
- File, KV occupation and preemptions.

Add cost per team and quality with measurement coverage. `finish_reason=length` is a signal to be interpreted according to the contract, not always a business error.

Example: a minority of very long prompts can suffer despite an acceptable global p95. Break down by length classes, backend and version, without user identifiers as labels with high cardinality. Link a degraded signal to the corresponding diagnostic traces.

---

What alerts to set up on an inference server? <!--anki:6954683b7c7e24746059-->
?
Alert about **symptoms seen by users**, not about each cause:
- **Error budget consumption** of SLO (burn rate) on TTFT, TPOT and availability
- **Waiting file** that stays high for several minutes, **KV cache** saturated with preemptions
- **Sudden rate increase** of 5xx, `length` or validation failures
- **Daily cost** above budget
- **XID errors** or thermal throttling of a GPU

---

What are the controls before sending traffic to a new deployment? <!--anki:433a7965647929264862-->
?
1. **Readiness**: loaded weights, `/v1/models` returns the right model and **good overhaul**
2. **Smoke tests**: some known prompts in Greedy, with the expected output format
3. **Benchmark charging** to target concurrency: do SLOs hold up?
4. **Eval gate**: quality at least equal to the version in place ([[112-model-cicd|CI/CD models]])
5. **Canary or shadow**: a share of real traffic, comparing the same metrics

---

How to detect regression after a model or configuration change? <!--anki:6965217e3d6c7a2a2879-->
?
By labeling **all metrics** with the model, its review and configuration of serving (quantization, speculative decoding, engine version), we compare the **new version and the old one on the same traffic**: latencies, errors, validation rate, `finish_reason`, quality scores. evals side, we compare **question by question** ([[114-reproducibility-variance|Comparison Paired]]).

Keep labels with limited cardinality: a request identifier belongs to the traces, not to the Prometheus series. Also control the mix of lengths and clients; a latency increase may come from traffic rather than release.

---

What are the precautions for logging prompts and responses? <!--anki:45542b4d446e24716143-->
?
They often contain **personal or confidential data**:
- Log **Metrics without default** content, and content only on **sample** or opt-in
- **Hide** personal data before storage
- Set a **retention time** and restrict access to logs
- Never put content in them. **Prometheus Labels** It would explode cardinality and expose the data.

---

Do not confuse: Monitoring and observability? <!--anki:42447a46547b5f583055-->
?
- **Monitoring**: monitor **indicators known in advance** (latency, error rate, cost) and alert on thresholds. It responds to "Are you okay?"
- **Observability**: Being able to **explain unexpected behavior** from traces, logs, and detailed metrics. She replies to “Why is it wrong?”

For a LLM system, the monitoring detects a drop in quality; it is the **complete traces** that make it possible to find the cause ([[98-agent-debugging|Debugging]]).

---

Why not average the p95 of the inference replicas? <!--anki:3834613263323836633032643462303239323335663839613065333938303433-->
?
One percentile is not additive. One replica serving 10 requests and another 10,000 do not contribute in the same way; even a weighted average of their p95 does not replenish the overall percentile.

Aggregate histograms **compatible**, then calculate the quantile. For classical histograms:
```promql
histogram_quantile(0.95,
  sum by (le, model_name) (
    rate(vllm:time_to_first_token_seconds_bucket[5m])
  )
)
```
Filter first service and environment; check actual labels. Keep models separate and compare homogeneous populations. Quantiles pre-calculated in summaries do not aggregate like this.

---

How to choose the buckets of a LLM latency histogram? <!--anki:3661326262363665393537363466663062313764333030633262316165663338-->
?
Place bounds around thresholds that trigger a decision, for example **0.8 seconds** for the TTFT. With conventional buckets, the fraction under an explicit bound is calculated without interpolating a percentile.

Too large buckets make a p95 close to the threshold imprecise. Check units, volume of observations and compatibility between replicas. The counter of a TTFT histogram does not necessarily contain the errors that occurred before the first token: it does not replace the total of requests eligible for the SLO.

---

How to reconcile the metrics of the gateway and those of the LLM engine? <!--anki:6166333166666534353761633463366139626534633135383032353536356339-->
?
Milestones: arrival, admission, start of the prefill, first token engine, first customer content, last token and final validation. Meters must specify layer, population and unit.

One task can trigger multiple calls, and a call for several attempts. Connect these levels with traces; do not add their counters as if they were independent. Measure durations on a local monotonous clock; subtracting timestamps from different machines requires known timing and uncertainty. Network, buffering and tools often explain the client–engine gap.

---

Calculation: two queries start together and each produce 100 tokens, A in 1 s and B in 9 s. Compare the average of individual bitrates to the overall bitrate on the 9 s? <!--anki:3961323930326463383764623432363861333465306430333062356639376239-->
?
Two **simultaneous** queries each produce 100 tokens: A in 1 seconds, B in 9 seconds. Their average bitrates are `(100 + 11,1) / 2 ≈ 55,6 tokens/s`.

On the common window of 9 seconds, the service produces `200 / 9 ≈ 22,2 tokens/s`. The denominators differ; none of these numbers substitutes for the other. For the aggregated rate, use the tokens actually emitted during a common wall window. Specify if we count all tokens or only those of the compliant answers.

---

How to prevent a dashboard from masking the degradation of a query category? <!--anki:6665326135633731613237323438333338356662333064646137303162643061-->
?
Maintain a global view and stable segments: model, route, length class, modality, and service level. An increase in easy requests can improve the overall p95 while each difficult task slows down.

Compare distributions and volumes of segments before assigning a gain to an optimization. Bound categories; keep fine identifiers in the tracks. Also publish refusals and deadlines per segment to detect an admission policy that systematically benefits short queries or a particular client.

---

Why monitor missing metric rate on an inference service? <!--anki:3833393266373365613931313430646439373662323962356531316233333337-->
?
A **telemetry failure** can cause the slowest or most interrupted requests to disappear. The dashboard improves while the service degrades.

Compare input counters, completed queries, and duration observations; alert to unexplained deviations. Distinguish between zero value, no measurement, and no traffic. Test a restart of the collector and a cut-off response before final use. Use input layer logs or metrics as a close-up point, without assuming that each system loses the same events.

---

Why measure the age of the oldest queue request in addition to the queue length? <!--anki:3839653062623265336561393466396138653932623033373739656465363766-->
?
A small queue may contain **a request that has beas a batchked for a long time**, while a large queue may resolve quickly. Length describes a volume; age reveals a risk of delay or starvation.

Track also arrivals, departures and distribution of waiting by priority. An alert must specify the perimeter and the action expected. Do not reset the age on a recovery if the user is still waiting for the same task.

---

How to distinguish a useful alert from a simple indicator of interest for inference? <!--anki:3338653035626532626437653432663639363965356535633935373963323163-->
?
A useful alert signals **a concrete impact or risk requiring action**, with owner and procedure. “GPU to 90%” may be normal; “timeout and queue growing” describes a user problem.

Keep other signals in dashboards for diagnosis. Test the alert, its routing and its return to normal state. Too many alerts without action increases noise and delays the detection of important incidents.

---

## Scenarios

Scenario: "The assistant is slow this morning." You only have this sentence. In what order do you look? <!--anki:7a24417a6c476d607978-->
?
1. **Confirm and quantify**: TTFT and TPOT in p95, on the right track and in the right period
2. **Saturation**: queue, KV cache occupancy, preemptions. This is the most common cause
3. **Usage**: a client that sends much longer prompts, or a spike in traffic
4. **Infrastructure**: XID errors, thermal throttling, a fallen replica, a degraded node
5. **Recent change**: deployment, new prompt, new model, broken prefix cache

**Trap**: conclude the saturation of the calculation from the use of GPU alone; correlate it to the queue, flow rate and time per phase.

---

Scenario: your service does not return any errors, but the support receives complaints about truncated answers. What metric should have alerted you? <!--anki:4f53557e6f40256e5434-->
?
1. **The distribution of `finish_reason`**: an increase of `length` signals responses cut by `max_tokens`
2. **Check cause**: limit too low, prompt longer, or model that loops
3. **Cross** with validation failure rate, including invalid JSON due to truncation
4. **Fix**: adjust `max_tokens`, ask for more concise answers, cut out the task
5. **Alert** on this rate, not just on HTTP error codes

**Trap**: Consider a response returned with a 200 code to be a successful response.

---

Scenario: the compliance manager asks if you are logging user conversations. What do you answer, and what do you check? <!--anki:4376464f387c74687054-->
?
1. **Distinguish** metrics (without content) and traces (with content), and say what is actually preserved
2. **Default**: Metrics without content, content only on sample or opt-in
3. **Hide** personal data before storage, and restrict access to traces ([[152-pii-privacy|PII]])
4. **Retention** set and applied, including in backups ([[154-gdpr-llm|RGPD]])
5. **Check Prometheus labels**: never user content, under penalty of explosion of cardinality and exposure

**Trap**: discover that complete prompts have left in the application logs, outside the trace system.

---

## Sources

- [Prometheus — histograms and aggregation](https://prometheus.io/docs/practices/histograms/)
- [Prometheus — instrumentation and cardinality](https://prometheus.io/docs/practices/instrumentation/)
- [NVIDIA DCGM — interpretation of profiling counters](https://docs.nvidia.com/datacenter/dcgm/latest/learn/modules/profiling.html)

- [vLLM — production metrics](https://docs.vllm.ai/en/latest/usage/metrics/)
- [OpenTelemetry — semantic conventions GenAI](https://github.com/open-telemetry/semantic-conventions-genai)

- 14 November supplement 2026 — Alerts and user impact: [Google SRE — Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/).

## Connections
- [[64-inference-metrics-slo|Inference Metrics & SLO]] — TTFT, TPOT, goodput, percentiles
- [[91-langfuse-observability|Langfuse & LLM observability]] — application traces
- [[113-monitoring-drift-feedback|Monitoring, drift & feedback]] — quality in time
- [[81-litellm-api-layer|LiteLLM]] — the gateway that sees all the use
- [[122-finops-llm|FinOps LLM]] — allocate and manage costs
- [[112-model-cicd|CI/CD models]] — eval gate, canary, rollback
- [[11-llm-inference-servers|Inference Servers]] — `/metrics` and `/health` endpoints
- [[12-kubernetes-gpu-inference|Kubernetes GPU & inference]] — autoscaling on these signals
- [[68-quantization|Quantization]] — validate a quantized model
- [[67-speculative-decoding|Speculative Decoding]] — follow the acceptance rate
- [[115-agent-platforms-governance|— Agent Platforms Architecture & Governance]] — audit and trace agents
- [[38-agent-platforms|Platforms of agents]] — observability provided by the platform
- [[105-agentic-ai-devsecops|DevSecOps for Agentic AI]] — security logs and detection
- [[97-evals-online-ab-testing|Evals online & A/B testing]] — Quality in production
- [[142-llm-reliability-resilience|Reliability & resilience]] — timeouts, recoveries, fallbacks and degradation
- [[61-kv-cache-attention|KV cache]] — memory that limits concurrency
- [[85-agentic-protocols-map|Map of protocols]] — which protocol to which agent boundary
- [[95-llm-as-judge|LLM-as-a-judge]] — note automatically, and validate the judge
- [[60-010-inference-load-benchmarks|LLM Load Benchmarks]] — measure capacity without hiding files and failures
- [[90-011-langfuse-instrumentation-production|Langfuse — Production instrumentation]] — connect traces and aggregate measurements
- [[00-moc-ai-engineering|MOC AI Engineering]]
