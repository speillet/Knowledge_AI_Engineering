# Roofline, prefill/decode & disaggregation — Flashcards
Tags: #flashcards #ai-engineering #inference #gpu #performance #llm
Verified on: 29 September 2026 — This factsheet lists products, versions or regulatory texts that are evolving quickly.
<!-- summary: arithmetic intensity, model roofline, memory-bound or compute-bound, flow rate calculations of decode and duration of prefill, Batch decode, Limits of Use GPU, Interference prefill/decode, Chunked prefill or disaggregation, Disaggregated deployment (Dynamo, llm-d), When it disintegrates, cost and recovery of transfers KV, memory hierarchy and limits of the roofline, the tipping point, ceiling and measure. -->


What is Arithmetic Intensity? <!--anki:4e682e414f26342b616d-->
?
The number of **calculation operations per byte read in memory** (Flop/Byte). She says what limits a calculation:
- **Low**: GPU waits for data, calculation is limited by **memory bandwidth**
- **High**: the data is reused a lot, the calculation is limited by the **calculation power**

Compare to the hardware transition point: `compute throughput / bandwidth`, in FLOP/byte. A theoretical GPU at 100 TFLOP/s and 2 TB/s gives 50 FLOP/byte. This ideal terminal does not integrate small kernels, communications or costs CPU; check the actual profile.

---

What is the roofline model? <!--anki:734d2b432465463e4639-->
?
A graph that gives the maximum attainable **performance** according to the arithmetic intensity: a slope (bandwidth limit) then a ceiling (computation limit). The tipping point, the **ridge point**, is worth **computation power / bandwidth**.
```text
H100 SXM : ≈ 989 TFLOP/s (BF16 dense) / ≈ 3,35 TB/s ≈ 300 FLOP/byte
below ~300 FLOP/byte: memory-bound
Above: compute-bound
```

Read: performance attainable = min(computing limit, × bandwidth intensity). A core at 1 FLOP/byte on this H100 caps to 1 × 3.35 TB/s ≈ 3.35 TFLOP/s, i.e. about 0.3% of the peak of the calculation.

---

Do not confuse: memory-bound and compute-bound? <!--anki:6a6f7d6d386152727063-->
?
**Memory-bound**: memory transfers dominate; **compute-bound**: calculation dominates. The roofline model compares approximately `bytes / bandwidth` and `FLOPs / compute throughput`, with truly attainable bit rates.

Example: if both estimates are 8 ms and 2 ms, doubling the calculation reduces the second to 1 ms but leaves the memory floor to 8 ms.

Quantification, batching and precision can work on several terms. This simplified model does not include all the extra costs: communication, synchronization and small kernels can dominate. Check the regime with a profiler.

---

Why is the prefill compute-bound and the decode memory-bound? <!--anki:6d6f476d2f5178315951-->
?
In the linear layers of a dense model, the **prefill** reuses weights for many tokens; the **decode with small batch** reuses them much less. In BF16, the simplified model gives about `B FLOP/byte` for a batch of B tokens.

This explains a regime often limited by the calculation at the prefill and by the memory at the decode. Long attention, kernels, communications and MoE or hybrid architectures can move the neck. The ratio to the ridge point describes a theoretical intensity; it is not directly the percentage of FLOP actually used.

---

Calculation: to batch 1, a dense 70B FP8 relit 70 GB of weight per token, with a theoretical bandwidth of 3.35 TB/s. What ceiling of tokens/s due to weight readings only? <!--anki:6e584d7a536d48573540-->
?
Dense model, FP8 weight read once by token, batch 1 and theoretical bandwidth:
```text
weight ≈ 70 GB; bandwidth assumed ≈ 3.35 TB/s
ceiling due to weight readings only ≈ 3,350 / 70 ≈ 48 tokens/s
```
It is neither a measurement nor a guarantee that a complete deployment holds on the map. Add KV, scales, activations and reserves; attention, calculation, launches and transfers decrease the actual throughput. Without measurement, do not announce a fixed percentage of the ceiling. Quantization reduces bytes; speculation can dampen a reading on several validated tokens.

---

Calculation: under the approximation 2 FLOP per parameter and token, how long is the linear component of prefill from 10,000 tokens from a dense 8B to 5 × 10^14 FLOP/s useful? <!--anki:7326283a603b30342373-->
?
For linear layers of a dense model, use the `2 × parameters × tokens` approximation:
```text
2 × 8e9 × 10 000 = 1,6e14 FLOP
Useful flow assumption: 5e14 FLOP/s
estimated duration of this component = 0.32 s
```
The chosen useful flow rate is a **hypothesis**, not a guaranteed yield of the GPU. Add attention, engine fees, waiting and transport to get a TTFT. The dense attention grows quadratically at the prefill; the length at which it dominates depends on the architecture, batch and kernels, without universal threshold at 100,000 tokens.

---

Why can increasing the batch greatly improve the throughput of the decode? <!--anki:42785655476759424b2d-->
?
In a regime where the **Weight reading dominates**, Several sequences reuse these readings and increase the arithmetic intensity. Aggregate throughput can then grow much faster than the duration of an iteration.

The gain is not free: calculation, activations and KV readings also increase, especially in long context. Beyond a certain batch, calculation, memory or communications saturate and the TPOT degrades. Measure the load curve on the target workload; do not assume that an iteration to 64 sequences costs as much as a sequence.

---

Why do prefill and decode get stuck on the same GPU? <!--anki:4d7676625e503c7a2859-->
?
A large prefill **the Monopolise GPU** for hundreds of milliseconds: the sequences in decode from the same batch **Waiting**, from where the **Peaks of TPOT** visible to users during generation. Conversely, many decodes slow down the admission of new prompts and degrade the **TTFT**.

The two phases have different necks (calculation and memory) but share the same machine.

Compare the inter-token latencies with and without long bursts. If the pauses coincide, test the prefill cut-out and its budget of tokens before separating the GPU pools; check that the TTFT remains acceptable.

---

Do not confuse: chunked prefill and disaggregation prefill/decode? <!--anki:7a5e5671384259417430-->
?
- **Chunked prefill**: Cuts a long prefill into **pieces** interspersed with the decodes, **on the same GPU**. Smooths the TPOT, without additional infrastructure. Enabled by default when possible in vLLM V1
- **Disaggregation**: prefill and decode run on separate **pools of GPU**, and the KV cache is **transferred** from one to the other. Each pool is sized for its neck, at the price of a fast network and more complex orchestration

We start with the first; the second is justified on a large scale.

---

How does a disaggregated deployment work in practice? <!--anki:4d6b2467737e6a413962-->
?
1. A **router** sends the prompt to a worker of **prefill**, chosen according to the load and prefix cache ([[66-prefix-caching-radix-attention|routage cache-aware]])
2. The prefill calculates the KV cache and the **transfer** to a **decode** worker by NVLink or RDMA (libraries like NIXL)
3. The decode worker generates the following
4. The two pools **autoscale separately**: more prefill if prompts lengthen, more decode if answers lengthen

Implementations: NVIDIA Dynamo, llm-d on Kubernetes, vLLM and SGLang disaggregated modes ([[12-kubernetes-gpu-inference|Kubernetes GPU]]).

---

When is disaggregation worth its cost? <!--anki:446d467a673160625b32-->
?
When the separation prefill/decode Improves it sufficiently **Goodput SLO** to pay transfers KV, routing and reserved capacity in each pool. The long prompts mixed with streams sensitive to theITL This is a case to study.

Measure transferred volume, effective bandwidth, synchronization, files from both pools, and load imbalance. Compare to a well-tuned co-located configuration, especially with chunked prefill. Cluster size alone does not decide: a fast network may remain insufficient, and a separation may reduce usage if one pool waits for the other.

---

Calculation: what minimum cost to transfer 2 GiB KV on a link to 25 GiB/s? <!--anki:6236376139316165393166343439383339353764656438636464656336643633-->
?
Without overlap or contention, the transfer component is `2 / 25 = 0,08 s`, or **80 ms**. Add preparation, synchronization and waiting before comparing to a calculation gain.

If the separation saves only 50 ms on the critical path, an additional unmasked transfer of 80 ms cancels this gain. With overlap, measure the part actually exposed rather than blindly adding the durations. At several simultaneous requests, the bandwidth is shared: the time of an isolated request does not demonstrate the behavior under load.

---

Why does the roofline need to specify which memory provides the bandwidth used? <!--anki:3135363239353633323937393464313238633233663931653162653536323638-->
?
The **memory ceiling** depends on the level considered: HBM of the GPU, host memory or transfer between GPU. Using the HBM bandwidth for a partially offloaded model can greatly overestimate the throughput.

Identify the bytes moved on each link and the critical path; include KV cache and communications according to the workload. The calculation weight divided by bandwidth gives a simplified bound of decode at low batch, not a promise of performance. Measure the speeds actually supported and re-evaluate the neck when batch, context or parallelism change.

---

Calculation: GPU theoretically provides 120 TFLOP/s and 3 TB/s of memory bandwidth, in decimal units. At what arithmetic intensity do the two roofline ceilings intersect? <!--anki:3934646633393730663064383461663939633037326264643536333130633735-->
?
The toggle point is **120 × 10¹² / (3 × 10¹²) = 40 FLOP/byte**.

Below, the memory ceiling is the lowest; above, the calculation ceiling becomes limiting in this simplified model. Actual performance remains lower depending on access, kernels and communications. It is necessary to use the ceilings of the digital format and the hardware concerned, not mix an FP8 performance with a BF16 calculation.

---

Why is a kernel located far below the two roofline ceilings not necessarily memory-bound? <!--anki:6438653233386537663532663432353462336566376262383137333161613335-->
?
It can be limited by **launches, synchronizations, low occupancy, or inefficient access**. The roofline provides bollards, not an exhaustive diagnosis.

Profile time of kernels, transfers and periods of inactivity, then compare the actually processed shapes. For very small operations, fixed costs sometimes dominate. Changing from GPU or reducing accuracy does not necessarily correct a path mainly limited by the CPU orchestration.

---

## Scenarios

Scenario: your vLLM server displays 100% of GPU usage, but only one user gets 25 tokens/s on a 70B in BF16, on two H100 in tensor parallelism. Your manager requests two more GPU. What do you analyze? <!--anki:67466b7a5a43452e713c-->
?
1. **Calculate the ceiling** : 140 GB of weight read at each token on the 2 × 3.35 TB/s, either ≈ 48 tokens/s at best. 25 tokens/s is not abnormal
2. **Relativize the indicator**: 100% usage means that kernels are spinning, not that the calculation is saturated
3. **Strike the right bottleneck**: quantize in FP8 halves the bytes read ([[68-quantization|quantization]]), the specific decoding produces several tokens per read ([[67-speculative-decoding|Special Decoding]])
4. **Measurement at real load**: at 30 users, the total throughput rises sharply thanks to the batch ([[64-inference-metrics-slo|SLO]])
5. **Add GPU only if** the SLO is not held to the target load after these levers

**Trap**: Buy calculation for a memory bandwidth issue.

---

Scenario: on your RAG, the answers "stutter": the text stops half a second in full generation, especially during peak hours. The average TTFT is correct. What do you diagnose? <!--anki:6e51482c402857432865-->
?
1. **Link to metrics**: Peaks from ITL to p99 when the average is fine ([[64-inference-metrics-slo|percentiles]])
2. **Suspect interference**: Long RAG prompts (10,000 tokens and up) switch to prefill and block current decodes
3. **Enable or adjust the chunked prefill**: piece size, tokens budget share per step
4. **Reduce prompts**: fewer chunks, more selective ranking ([[25-chunking-contextual-retrieval|chunking]])
5. **On a large scale only**, consider disaggregation prefill/decode

**Trap**: Increase the batch size to absorb the tip, which further lengthens each step of decode.

---

## Sources

- [DistServe — separation and transfer cost](https://arxiv.org/abs/2401.09670)

- [NVIDIA — Dynamo, distributed inference](https://docs.nvidia.com/dynamo/latest/)

- 14 November 2026 — Compute and Bandwidth Ceilings: [NVIDIA — GPU Performance Background](https://docs.nvidia.com/deeplearning/performance/dl-performance-gpu-background/index.html).

## Connections
- [[62-inference-optimizations|Inference optimizations]] — levers by phase
- [[61-kv-cache-attention|KV cache & attention]] — what the decode rereads and transfers
- [[64-inference-metrics-slo|Metrics & SLO]] — TTFT, TPOT, percentiles
- [[68-quantization|Quantization]] — fewer bytes per token
- [[67-speculative-decoding|Speculative Decoding]] — several tokens per weight reading
- [[66-prefix-caching-radix-attention|Prefix caching]] — Routing in Disaggregated Deployment
- [[135-pretraining-scaling-laws|Pre-workout]] — MFU and 6ND
- [[12-kubernetes-gpu-inference|Kubernetes GPU & inference]] — llm-d and pool autoscaling
- [[11-llm-inference-servers|Inference Servers]] — vLLM, SGLang, TensorRT-LLM and their setting
- [[22-advanced-rag|RAG — Advanced]] — hybrid search, reranking and filters
- [[60-013-prefill-decode-step-by-step|Prefill & decode step by step]] — track calculated positions, cache and delays
- [[00-moc-ai-engineering|MOC AI Engineering]]
