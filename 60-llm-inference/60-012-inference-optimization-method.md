# LLM inference optimization method — Flashcards
Tags: #flashcards #ai-engineering #inference #performance #profiling #finops
Verified on: 8 October 2026
<!-- summary: objective under constraints, CPU/GPU profiling, CUDA graphs and compilation, kernels, Amdahl law, interactions between optimizations, API quotas, retrievals, routing, reasoning and multimodal, marginal cost of an optimization, causal attribution of the gain, rollback cost. -->


What does it mean to maximize the inference of a LLM in a product? <!--anki:3766383238393464336537333434323438393562383237363466353762663831-->
?
Choose a useful target: **more successful tasks per second or per euro**, under constraints of quality, deadlines, capacity and fairness. The maximum of tokens/s is only relevant if these tokens actually serve the task.

Build a Compromise Boundary: Keep configurations that no one else improves on all the criteria selected. Example: A serves 40 Successful tasks with a P95 1.2 s, B 55 with 2.5 s, C 38 with 1.4 s. C is dominated by A; a SLO of 2 then removes B. First set the essential requirements, then choose from the eligible options, including reserve and actual charge.

---

How to go from a symptom of slowness to an optimization hypothesis? <!--anki:3536626435386262303236373461366638646339666264376663633731323337-->
?
Decompose the path: file, tokenization, prefill, decode, communication, tools and validation. Link **lost time and limiting resource** on comparable cases.

Example: with 800 ms queue and 80 ms of prefill, divide only this prefill by two saves 40 ms, unchanged queue. The dominant wait calls for a capacity or admission hypothesis, not just a better kernel.

For each hypothesis, define isolated change, expected metric, quality/memory safeguards and abandonment criterion. Replay the load, because the change can modify the queue and move the neck. GPU active and full cache remain clues, not proven causes.

---

How to use a profiler without distorting the performance measurement? <!--anki:3962356234336165633238313432626539303964643239613930386334616266-->
?
Capture a representative **short window after warm-up**, with CPU and GPU events and, if necessary, memory allocations. Examine kernels, copies, launches and synchronizations on a common timeline.

PyTorch Profiler or engine tools help locate work, but collecting detailed shapes, batteries, and traces can disrupt the measured time. Comparing final performance without heavy instrumentation. Measuring multiple load cases: A 1 batch profile does not necessarily explain the high-concurrency neck. Not to confuse CPU sending time with asynchronous GPU execution.

---

What to look for when the GPU waits while the inference service is slow? <!--anki:3130366432316562616136323462396439646538386239363733326132303266-->
?
Examine **CPU, tokenization, image processing, serialization, networking, storage, and scheduler**. A thread limit, CPU quota, unfavorable NUMA placement, or blocked event loop may prevent the GPU from being powered.

Compare time before engine and time GPU, and then test a query directly and via the full route. Example: a container limited to 2 Tokenized and diffused hearts 64 flow; in the `cpu.stat` from his cgroup, `nr_throttled` increases while the GPU Remains half inactive. Add a GPU Don't change it. After correction, Repeat the test: The GPU It can become the new limiting factor.

---

Do not confuse: CUDA graphs, compilation and merging of kernels? <!--anki:3036643739623566646238333438663561383034363366616230326136666332-->
?
**CUDA** graphs replay a sequence of operations to reduce launch costs. **Compilation** transforms and specializes the program. **Merger** combines operations to decrease launches or intermediate data.

These techniques complement each other, with shape constraints. vLLM, for example, captures graphs for a list of batch sizes: a batch of 13 sequences is completed up to the next captured size, and beyond the larger run becomes classic again. `--enforce-eager` disables these graphs to measure their input. Capture and compilation cost boot and memory.

---

How to choose a faster attention backend or kernel? <!--anki:3066363861666266633336313461356462393264343536396338623637373066-->
?
Check compatibility with GPU, dtype, dimensions, attention mask, context, quantization and generation mode. A fast kernel in a microbenchmark can be rarely used in the service, or cause expensive conversions.

Example: a backend gains 25% on a microbenchmark in BF16, but the service stores its KV cache in FP8, a format it does not support; the engine remains on the old path and the actual gain is zero. Comparing numerically to the reference backend, validating outputs on critical tasks, and then measuring the entire path at target lengths and competitors.

---

Calculation: What is the maximum gain if the decode represents 60% of time and becomes twice as fast? <!--anki:3663343736343064393438303434633938653934653930623361353134336639-->
?
For identical work and without interaction, Amdahl's law gives:
```text
new relative time = 0,40 + 0,60 / 2 = 0,70
global acceleration = 1 / 0.70 ≈ 1.43
```
Even an instant decode would limit the gain to `1 / 0,40 = 2,5`. This estimate helps prioritize the effort; it does not directly predict a p95 or a queued system. Under load, the contention and batching changes the proportions. Check the full course after optimization.

---

Why test inference optimizations separately and together? <!--anki:6162343531366138386438373462636462303230396662623865356333616161-->
?
An isolated improvement can disappear or reverse in a combination: quantifying frees up memory, a larger batch fills it, and then speculative verification increases the calculation.

Start with variations due to change, then test plausible combinations. Keep data, quality and load comparable, and see effects on CPU, KV and communications. Keep the baseline and a versioned rollback. Avoid multiplying all settings without hypothesis: a small targeted experience plan better explains the gains and reduces the risk of choosing a lucky result.

---

Calculation: Each request counts 1,000 tokens input and 500 output. What average ceiling with fictitious 600 requests/min, 60,000 tokens input/min and 20,000 tokens output/min quotas? <!--anki:3038643039393265373463333434353661616235366537383265306364373831-->
?
Suppose **1,000 tokens input and 500 output per request**, all counted in these fictitious quotas:
```text
requests: 600/min
entry: 60,000 / 1,000 = 60 requests/min
output: 20,000 / 500 = 40 requests/min
medium ceiling = min(600, 60, 40) = 40 requests/min
```
The output limits here, even before latency and vendor capacity. Checking windows, bursts, shared quotas, estimation/booking and cache processing in the actual API. Reducing the inputs does not remove this bottleneck; limiting the outputs requires preserving the quality.

The minimum of these ceilings is necessary but may not be sustainable: variations in length, gusts and slippery windows create discharges. Smooth calls and measure the limits actually applied by the service.

---

Why can retrieves and hedging reduce the throughput of a LLM? <!--anki:3433656533303238313566313437666262363965353837363738393865303835-->
?
A **retry** raises a call; the **hedging** launches a concurrent attempt to reduce the wait for the slower one. Both add work, sometimes while the initial call continues.

One hundred tasks with 20% double attempts require 120 calls, before additional retakes. Set a global budget, backoff with jitter and propagated deadline; follow quota indications. Undo the losing attempt and avoid the effects of duplicate tools. Measure amplification, cost and success per task: Increased latency at low load can become an overloaded outflow storm.

---

How to optimize a cascade of models without shifting the cost to the pick-ups? <!--anki:3531323830363532366339353436366162346233626465373364303738623563-->
?
Route to a smaller model when assessments show that it is sufficient, and scale according to verified criteria. Measure cost and delay **of the entire cascade**, including control and second call.

The control decides the cost. Example: If it rejects 60% of the answers of the small model, half of which were correct, the majority of the tasks pay two calls and waits twice. Measure its false rejections on a labeled game and immediately route to the large model the segments that almost always climb. Compare success by segment and cost per task, not just the price of the model chosen first.

---

How to master the reasoning budget and parallel branches of an agent? <!--anki:6162353566333163626434643433663461376134386465626464323132373831-->
?
To limit the number of calls, tokens, total time and competing branches, according to the mechanisms really exposed by the model and the orchestrator. To evaluate the **quality gained by additional calculation**, especially on difficult tasks.

Longer reasoning or multiple candidates improve some results and waste resources on others. Example: Four branches of 3,000 tokens cost 12,000 tokens for a duration close to one; if they only earn points on difficult tasks, reserve them to this category. Also count tool calls, judge and abort attempts. Set an explicit stop rule.

---

Why are textual tokens not enough to size multimodal inference? <!--anki:3436373435326462393331643462303239363238323537353730313263326431-->
?
Image, audio, and video add decoding, resizing, encoding, and representations whose cost depends on resolution, duration, frame rate, and architecture. A ten-word question about a 60 s video sampled at 2 frames/s causes 120 images to be encoded.

Measure media size, processor units, encoding time, peak memory, and transfers, in addition to the prefill/decode textual. Differentiate between charged units and units actually processed by the engine. Segment benchmarks by modality and test combinations: a media frontend or encoder can saturate before the LLM decoder.

---

Why measure the marginal cost of an optimization in addition to its latency gain? <!--anki:3933353536386638623666623438613239616663386637373939666533346635-->
?
A **optimization** can reduce latency by consuming more GPU, memory, or calls. Duplicating a request at two providers sometimes speeds up the first response while increasing cost and load.

Compare to the same volume offered and the same level of quality: latency, goodput, resources and cost per useful task. Include lost calls and late cancellations. Test the saturated diet; a cost-effective low-load technique can reduce the capacity of the entire platform. Set the product goal before choosing the best number.

---

How to avoid assigning a gain to the kernel from a change in output length? <!--anki:3464356562623239616664383439363738373838613436386130346537366638-->
?
Compare **work done and quality**, not just total life. A model that produces half as much tokens can finish faster without any acceleration of the calculation by token.

Keep the query mix, measure length, TTFT, ITL and business criteria, then isolate the effect of the kernel with a controlled protocol. If the change voluntarily changes the outputs, present the gain as a complete system change and check for omissions.

---

Why prepare a rollback before optimizing the serving LLM? <!--anki:3464356662656137646531663439353862616433323533393039656639653731-->
?
Optimization can fail on **a rare form, a long context, or a different hardware** despite an average gain. Keeping a known configuration, its artifacts, and the return procedure helps limit the incident.

Validate first on a representative sample and define the stop thresholds. A rollback can cause weights and cold cover to reload: include this cost in the plan. Reversibility must be tested under the expected capacity conditions.

---

## Scenarios

Scenario: you need to double the number of useful answers without increasing the GPU budget. What approach do you propose? <!--anki:6166356234316436373062623432656539666363386435646465653061323765-->
?
1. **Fix the contract**: tasks, quality and deadlines, with a baseline to the actual traffic.
2. **Measure waste**: Abandoned work, resumes, unnecessary context, missing cache and inactive resources.
3. **Profile the neck**, then choose a few suitable levers: scheduler, kernels, precision, model or routing.
4. **Compare alone and then combined** with cost-per-success and margin overcharge.
5. **Deliver demonstrated gain** and limits; if doubling is impossible under constraints, document the required arbitration.

**Trap**: Promise a factor of two before measuring the truly optimizeable share.

---

Scenario: GPU kernels are accelerating from 30%, but user latency is not moving. What are you doing? <!--anki:6535636561303237643638353432323939316164306238636562323363303466-->
?
1. **Measure their initial share** in the critical path, and then apply an Amdahl bound.
2. **Examine upstream and downstream**: file, tokenization, media, gateway, rendering and tools.
3. **Check the executed path**: new kernel actually used or fallback on some forms.
4. **Compare without heavy profiling**, with identical cover, lengths and load.
5. **Target remaining bottleneck** or retain only demonstrated benefit, e.g. memory or ability.

**Trap**: announce an application gain from an isolated GPU time.

---

Scenario: increase call concurrency API mostly produces 429 errors. How do you react? <!--anki:6562653731663163646363353465383862316436306334373338313137333138-->
?
1. **Identify quota**: requests, inputs, outputs, model, organization or burst.
2. **Measuring the actual rhythm** and the amplification due to the retries.
3. **Limit admission** and smooth shipments with a deadline-bound queue.
4. **Reduce relevant work** or defer compatible tasks; ask for more quota if the need remains.
5. **Validate the payload** after backoff and cancellation of expired calls.

**Trap**: compensate for a quota exceeded by more parallelism or by immediate raises.

---

## Sources

- [PyTorch — profiler and CPU/GPU activity](https://docs.pytorch.org/tutorials/recipes/recipes/profiler_recipe.html)
- [vLLM — graphes CUDA](https://docs.vllm.ai/en/latest/design/cuda_graphs/)
- [vLLM — kernels and serving configuration](https://docs.vllm.ai/en/latest/configuration/optimization/)
- [Anthropic — example of RPM, ITPM and OTPM quotas](https://platform.claude.com/docs/en/api/rate-limits)
- [AWS Builders’ Library — timesouts, retrieves, and jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)

## Connections
- [[62-inference-optimizations|Optimization of inference]] — the mechanisms to be tested according to the neck
- [[60-010-inference-load-benchmarks|Load benchmarks]] — comparaisons reproductibles
- [[60-011-inference-capacity-scheduling|Capacity & scheduling]] — budget and admission
- [[121-inference-costs|Costs of inference]] — cost and energy per useful task
- [[138-reasoning-models|Models of Reasoning]] — measure the performance of the additional calculation
- [[00-moc-ai-engineering|MOC AI Engineering]]
