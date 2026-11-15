# Charging benchmarks for inference LLM — Flashcards
Tags: #flashcards #ai-engineering #inference #benchmark #performance
Verified on: 8 October 2026
<!-- summary: Reproducible protocol, open or closed loop, coordinated omission, query mix, cold/hot cache, saturation, uncertainty, generator limits, SLO capability, burst testing, survivor bias, plateau duration. -->


Which contract to fix before a LLM inference benchmark? <!--anki:3464663735636264643633333437376238393536656231303262323632633333-->
?
Set **task, minimum quality, target load, latencies, and acceptable cost** before comparing engines. Example for a support wizard: 20 peak requests/s, 95% grid-compliant responses, first content under 1 s, and full response under 8 s at p95, at most 0.5 cents per response.

Specify tokens unit, customer/engine perimeter and treatment of rejects, retracts and cancellations. A synthetic generation benchmark measures a system; it does not demonstrate business quality. Keep the baseline as a point of comparison.

---

Do not confuse: open-loop and closed-loop benchmark? <!--anki:6465343464653161326536363437313362666232373039613261626466396631-->
?
In **open loop**, arrivals follow a calendar independent of responses. This allows to observe the growth of a queue when demand exceeds capacity.

In **closed loop**, a fixed number of clients wait for the end of a request before sending another one: a slow response slows down the arrivals. With 50 clients without reflection time, 2 s responses give 25 requests/s; at 10 s, the load drops to 5 requests/s, while an external request would continue to arrive with the dependency.

---

What is coordinated omission in a load test? <!--anki:6364633065373238373935613436396461356633323432336438343465343930-->
?
The generator stops or delays its shipments when the system slows down, then measures only the requests it actually sent. It thus omits the expectations that would have been experienced by independent arrivals: the latency queue seems better.

Example: a scheduled client every 100 ms is blocked 2 s on a response. The 19 scheduled shipments during this blocking would have waited from 0.1 to 1.9 s more; the histogram counts none. Compare the expected time and actual time of issue. A statistical fix does not recreate the work that the server never received.

---

How to build a representative query mix for a LLM? <!--anki:3639316435666364353065303466613362663961396536623961303035343365-->
?
Preserve the **joint distribution** of input and output lengths, arrival points, common prefixes, and turns of a conversation. Add the appropriate proportions of languages, tools, constrained formats, images, or reasoning.

Queries all to 1,000 tokens input and 500 output have the same averages as a mixture of abstracts (1,900 input, 100 output) and redactions (100 and 900); the second alternates prefill heavy and long decodes. Separate the critical segments and include the long-tails.

---

Why separate engine warm-up and prefix cache warm-up? <!--anki:6166663133613332363562343438633362656337383561303734613133346232-->
?
The engine can pay at boot loading, compilation, graph capture and kernel initialization. The prefix cache gets hot when reusing content; this is another phenomenon.

Measure start, set up with cold cache, then traffic with realistic reuse. Do the technical warm-up with separate data. Reset or control the cache between variants: with a common system prompt of 3,000 tokens, the variant tested second finds it cached and saves this prefill on each request, without being better. Also keep a scenario of restart or arrival of a new replica.

---

What to keep in the manifest of an inference benchmark? <!--anki:3565633531303463376362623436623561626632343630616339383137396339-->
?
Archive five sets of information:
- **Model**: review, tokenizer, template, precision and generation parameters.
- **Motor**: version, image, scheduler, budgets, caches and parallelisms.
- **Machine**: GPU, interconnect, CPU, memory, drivers and power limits.
- **Traffic**: versioned game, order, seeds, arrivals, actual lengths and initial state.
- **Measurement**: tool/version, perimeter, duration, timeouts, detailed results and quality criteria.

A model name and a number of GPUs are not enough: two runs of the same model on 8 GPU diverge if one ignores EOS and produces 512 tokens fixed, the other of the actual lengths.

---

How to find sustainable capacity in SLO? <!--anki:6336333434343034663135343435306361643434323563346234633134323165-->
?
Scan multiple arrival rates, then refine near the area where latencies or queues increase sharply. At each level, measure offered throughput, completed, useful, refusal, lengths and slope of the queue.

Example: up to 12 requests/s, each segment respects its SLO and the queue remains stable; at 14, it is constantly growing, even if the finished throughput seems constant. Refine between 12 and 14, repeat near the border, then retain a margin justified by variability, start and failure. The best point of a short test is not a production guarantee.

---

How do I count the start and end of a benchmark? <!--anki:3062313036336261633835373462306162616230393433333136343239303165-->
?
Set a measurement phase after warm-up, then a **empty** of queries still in flight. Distinguish throughput on a stable window and result of a cohort of arrivals followed until resolved.

Do not delete requests that exceed the end of the test: count their end, timeout or unfinished status. If the duration includes emptying, say so. Archive arrivals and departures to reconcile volumes. Example: A test of 10 minutes stops with 40 long answers still in flight; exclude them precisely removes the slower ones and favors the configuration that accumulates work.

---

How to measure the uncertainty of a LLM performance result? <!--anki:3033343963363063663664393461313161323332623430373933303530613265-->
?
Repeat the tests, alternate the order of the variants and compare the same traffic. Report dispersion, number of requests and number of repetitions, not just the best run.

Successive latencies can be correlated by queues or peaks: a block bootstrap or a run comparison is more careful than a blind independence hypothesis. A p99 on 100 requests is very unstable. Adapting time and accuracy to the decision; a tiny difference does not justify a costly migration without reproducible evidence.

---

How to check that the load generator does not limit the benchmark? <!--anki:3466323961336365353836653435636538653564613236623363656166633232-->
?
Monitor CPU, event loop, connections, bandwidth, and client issue delays. Verify that actual arrivals match the expected schedule and that tokens are counted with the expected tokenizer.

A client-side ceiling can leave the server under-loaded while giving the impression of saturation. Typical sign: two very different motors cap at the same rate, the core CPU of the generator is at 100% and the transmission delay increases. Then distribute the generation, without losing the temporal coherence. Also test the proxy and the streaming: grouping of chunks, TLS and network are part of the path when one announces a user-side performance.

---

How to interpret request-rate and max-concurrency in a vLLM benchmark? <!--anki:3364373366333239396338643431353561656131373639303232323963656238-->
?
**`--request-rate`** sets the requested speed; **`--max-concurrency`** limits simultaneous requests. An active limit may prevent the advertised load from being generated.

Example: With 20 flight requests to the maximum and an average duration of 2 seconds, the throughput achieved caps around **10 requests/s** in steady state, even if 50 were requested. The test is no longer an open unconstrained arrival; low latency may mask this limitation.

Check version and `vllm bench serve --help`. Publish requested/realized rhythm, emission delay, lengths, errors and percentile population; also document warm-up, cache and burstiness.

---

Calculation: at 100 offered requests/s, A completes 100 with 70 meeting the SLO; B completes 90 with 85 meeting it and rejects 10. Compare goodput and the fraction of offered demand satisfied. <!--anki:6237643931336361636437353463356362346235393334653930363830663633-->
?
On the same stable load of 100 requests/s, A terminates 100 requests/s of which **70 satisfy together** quality and lead times. B terminates 90 of which **85 are compliant**, and rejects the remaining 10.

A provides 70 useful achievements, B 85. B has a better goodput, but its rejection rate can make the option unacceptable according to the contract. Compare also cost and satisfaction rate on the **100 requests offered**, i.e. 70% and 85%. Maximizing goodput does not exempt from a minimum service requirement.

---

Do not confuse: synthetic benchmark and application replay? <!--anki:3136393261613361666439333431646162313531343664333132343731313532-->
?
The **Synthetic** Control lengths, Arrivals and parameters; It isolates an effect and reveals the limits of the engine. With `--ignore-eos`, Each request produces exactly its `max_tokens`, for example 256 tokens. Decode work becomes comparable between variants, But the task is no longer that of the product.

The **application replay** keeps more distributions, prefixes and dependencies, but must be secure and versioned. Re-evaluate quality if model or generation changes: the number of tokens actually produced may vary. Using both; neither forced-length throughput nor isolated replay alone proves the ability of a full agent.

---

Why should a LLM benchmark include gusts rather than just constant average throughput? <!--anki:3166643239346430383165613463623662663138323636363561653966396463-->
?
The **queue** depends on the variability of arrivals and work, not just their average. A burst may exceed the available capacity before autoscaling has loaded the model.

Compare multiple profiles maintaining the same volume: regular, bursts and time replay. Measure wait, rejects, timed out and recovery time, with the same mix of tokens. Avoid averaging window percentiles. A stable service at ten constant requests per second is not necessarily ready for one hundred requests arriving together every ten seconds.

---

Why exclude failed queries artificially embellishes an inference benchmark? <!--anki:6166363136636533363765373438646462653062333331636161356134613666-->
?
The slowest queries can disappear from the calculation after timeout. The p95 of the only successes then improves while **the service actually degrades**.

Publish error rates, time overruns and distribution of achievements with their denominators. Classify timeouts as violations of the contract without inventing their duration of completion. Keep the number of requests offered: a rejection policy must not transform a low coverage into an apparent perfect performance.

---

Why extend the load tray after the end of the LLM server warmup? <!--anki:6433383531343066356233633437303438313164346262653230623833346237-->
?
A short test may be missing **queue buildup, memory growth, or cache removal**. The system appears stable as long as its reserves absorb the imbalance.

Observe the slope of the backlog and the memory during a sufficiently long tray, then check the return to rest. The relevant time depends on the operating cycle studied. A queue that increases continuously indicates an unsustainable load, even if the output rate remains constant.

---

## Scenarios

Scenario: an engine advertises twice as many tokens/s, but the product is slower. How do you compare the results? <!--anki:3638653361393636633635373437643639353266306564373830653233333237-->
?
1. **Align task**: same game, tokenizer, actual length produced and minimum quality.
2. **Align Load**: Same arrivals and cache status, then measure on the client side.
3. **Decompose**: TTFT, TPOT/ITL, E2E, tools and file; check which tokens are counted.
4. **Compare goodput** and cost per successful task, with errors and rejections.
5. **Repeat** by alternating variants, then confirm in canary.

**Trap**: confuse aggregate throughput, individual speed, and complete experience.

---

Scenario: the p99 is excellent at 32 customers, but users experience a breakdown during a campaign. What is missing from the test? <!--anki:6163656233353161383966613464353038383339306336333532663433363266-->
?
1. **Review the arrival model**: 32 customers may be waiting for answers before returning work.
2. **Replay the campaign** with independent arrivals and representative gusts.
3. **Track queue and delays** on both the generator and server side.
4. **Include failures** and requests still in flight at the end of the test.
5. **Test intake and recovery** after peak, with actual autoscaling time.

**Trap**: Extrapolate production capacity from a fixed concurrency that automatically reduces overload demand.

---

Scenario: an optimization gains 4% throughput on a single test. Do you deploy it? <!--anki:3539343537343935323031613435353562393233313630356133346637666432-->
?
1. **Check manifest**: no unintentional cache changes, prompts, GPU or generation.
2. **Repeat and alternate** the tests around the target load.
3. **Quantify uncertainty** on goodput, latencies, and quality, by critical segment.
4. **Compare the gain to the cost** of complexity, memory, and operation.
5. **Deploy in canary** only if the win justifies the decision, with rollback criteria.

**Trap**: Turn a fluctuation or better heated cache into a demonstrated improvement.

---

## Sources

- [vLLM — bench serve settings](https://docs.vllm.ai/en/latest/cli/bench/serve/)
- [Grafana k6 — load models open and closed](https://grafana.com/docs/k6/latest/using-k6/scenarios/concepts/open-vs-closed/)
- [HdrHistogram — Coordinated Omission Correction](https://github.com/HdrHistogram/HdrHistogram/blob/master/src/main/java/org/HdrHistogram/AbstractHistogram.java)
- [NVIDIA — GenAI-Perf](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/perf_analyzer/genai-perf/README.html)

## Connections
- [[64-inference-metrics-slo|Metrics & SLO]] — define useful results before measuring
- [[93-monitoring-inference|Monitoring of Inference]] — compare customer and engine metrics
- [[99-statistics-experimental-decisions|Experimental statistics]] — uncertainty, matching and decisions
- [[60-011-inference-capacity-scheduling|Capacity & scheduling]] — connect memory, budgets and payload under load
- [[60-012-inference-optimization-method|Optimization process]] — prioritize and verify gains under service constraints
- [[00-moc-ai-engineering|MOC AI Engineering]]
