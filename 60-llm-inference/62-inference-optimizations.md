# Inference optimizations — Flashcards
Tags: #flashcards #ai-engineering #inference #optimization #llm
<!-- summary: prefill and decode, continuous batching, quantization (AWQ, GPTQ, FP8), FlashAttention, parallelism tensor and pipeline, chunked prefill, disaggregation prefill/decode, equity of chunked prefill, FlashAttention and complexity, useful batch. -->


What are the two phases of inference of a LLM? <!--anki:482678244d584c28753b-->
?
The **prefill** processes the positions of the prompt, with parallelism between positions under causal mask, and builds the [[61-kv-cache-attention|KV cache]]. Its output allows to sample the first token. The **decode** continues the autoregressive generation by reusing this cache.

Example: Summarizing a long document in one sentence mainly requires input; writing several pages from a short instruction mainly requires the steps of output. Batching, cache and concurrency can modify the actual neck.

The TTFT also includes queue and transport: it is not a stopwatch of the only prefill. Measure separately waiting, first token and generation intervals.

---

Do not confuse: the levers that act on the TTFT and those that act on the TPOT? <!--anki:477c572b3f2d422a736d-->
?
```text
TTFT (prefill) prefix caching, chunked prefill, shorter context,
                        Disaggregation, more calculation
TPOT (decode) quantization, speculative decoding, GQA, less than
                        memory bandwidth consumed
Total flow continuous batching, bigger batch, parallelism
```
The same change can **improve one and degrade the other**: a big batch can increase throughput and lengthen the TPOT ([[64-inference-metrics-slo|SLO]]).

The TTFT also includes queue waiting and transport; speeding up only the prefill does not solve a service saturation. The chunked prefill especially protects requests already in decode and can delay the end of a new prefill. Compare percentiles at the same load to avoid confusing better throughput and better experience.

---

What is continuous batching? <!--anki:6f76727c477c5a746c4d-->
?
The **continuous batching** order to the granularity of an iteration: a completed sequence frees its place, and new sequences can join the following without waiting for the end of an entire batch.

Example: In a static batch, a response from 20 tokens keeps its place until the end of the longest, 500 iterations later; here, a new request takes it back as soon as the 21e. This does not guarantee a full GPU: request, limit KV, CPU or communications may restrict the server's throughput; the gap between a script and

---

What are the common quantization methods? <!--anki:796f767d2a297674625a-->
?
Distinguish **what is quantified** and **method**: AWQ and GPTQ include weight quantification, often in 4 bits; W8A8 describes weights and activations on 8 bits. FP8 refers to a family of digital formats whose support depends on GPU and kernels.

**GGUF is a file format**, which can contain different types of quantization for engines like llama.cpp. Compare complete configurations, not just these names: accuracy, calibration, kernels and workload determine quality and speed.

---

What is FlashAttention? <!--anki:4b232642746c452f422f-->
?
An implementation of the attention **conscious memory hierarchy of the GPU** (calculated by tiles in SRAM): **exact result**, much less access to the HBM, so faster and less memory-intensive.

The algorithm avoids materializing the entire attention matrix in external memory: for 32,000 tokens, he would be counting 32,000² values, either approximately 2 GB in BF16 per head and per sequence. "Exact" here means that it calculates the same operation, to the nearest numerical rounding, This is contrary to an approximation of attention. For dense attention, the number of operations remains quadratic with the length at prefill ; The gains are mainly related to memory access and execution.

---

Tensor parallelism or pipeline parallelism? <!--anki:514f686c4c5338235550-->
?
- **Tensor parallelism**: each layer is **cut between several GPU** (requests a fast interconnect type **NVLink**)
- **Pipeline parallelism**: **layers are distributed** by stages over several GPU or nodes

The tensor parallelism exchanges intermediate results frequently and suffers from a slow network. The pipeline parallelism transmits activations between stages and can leave GPU Inactive if the pipeline is not properly filled. Hence a common configuration with vLLM: `--tensor-parallel-size 8` inside a node connected by NVLink, and `--pipeline-parallel-size 2` between two knots. Add GPU does not automatically speed up an isolated request.

---

What is the chunked prefill? <!--anki:674f44515326767c7e37-->
?
Cut a long prefill **in pieces mixed with the decodes** in progress: a big prompt n'**Interrupts more** generation of other requests (inter-token more stable).

The scheduler allocates a budget of tokens The prefill and then intercalate the other works: with `--max-num-batched-tokens 2048`, decodes included, a Prompt of 16,000 tokens At least eight iterations. This limits long streaming breaks, without removing the total cost of the prompt. Pieces that are too small add scheduling fees; Too big can still penalize decodes. Measure TTFT and inter-token together.

---

What is prefill/decode disaggregation? <!--anki:51242a2437253078482b-->
?
Run prefill and decode on separate **pools of GPU**, with KV cache transfer between them: each pool is sized for its neck and optimized **TTFT and TPOT** independently.

This separation reduces some interference between large prompts and current generations: summaries of long documents occupy the pool of prefill, dimensioned in computation, while long generations remain on the pool of decode, dimensioned in memory and bandwidth. Its cost is the transfer of the cache and the coordination of the pools, which can cancel the gain if the network is insufficient.

---

Why can the chunked prefill improve interactivity without accelerating each single prompt? <!--anki:3136393361393564306336303464623661303538643765393034303230653665-->
?
Cutting the **prefill long** allows the scheduler to interlace it with the decode of already active queries, thus limiting the pauses imposed on these users by a new large document.

This equity can improve the ITL at the price of a more fragmented prefill and a different TTFT for the long-timer. Measuring both populations together and the useful throughput. The setting depends on the budget of tokens per batch and hardware; no universal chunk simultaneously minimizes all latencies.

---

Why can FlashAttention reduce memory without making the attention calculation linear? <!--anki:3561383533396666363164363435633738393035333434333362663330363065-->
?
It avoids materializing the entire **score matrix in external GPU memory**, by organizing the calculation by blocks and by exploiting the fast memory.

Interactions between positions remain quadratic for a complete dense attention: the drop in transfers and intermediate memory does not remove these operations. Distinguish arithmetic complexity, auxiliary memory and observed performance. The gain depends on the shapes, the hardware and the backend actually used.

---

Why can a larger batch lower goodput despite higher gross throughput? <!--anki:3865636463613365356435303435313462393362386665343535336266356433-->
?
It can improve the use of the GPU but **lengthen the wait or intervals between tokens**. More queries finish, but some exceed the SLO.

Compare useful throughput under latency constraints and rejection rate, to the same traffic offered. Segment by length and priority. Look for the operating point that meets the product contract, rather than the maximum batch that holds in memory or the best number of tokens/s isolated.

---

## Scenarios

Scenario: your inference service holds the SLO latency at low load, but at peak times the TTFT explodes while the flow stagnates. What levers do you operate? <!--anki:6932733f3f45586b4746-->
?
1. **Decompose the TTFT**: wait, prompt processing and transport; correlate with input length.
2. **Distinguish saturation**: preemptions and full KV point to memory; a single queue is not enough.
3. **Reduce targeted work**: stable prefixes, relevant context, validated quantification on hardware.
4. **Set the scheduler** Batch and Chunked prefill, by monitoring as well ITL and equity.
5. **Adapt capacity** if necessary, with bounded admission, replicas or disaggregation evaluated.

**Trap**: Activate multiple levers simultaneously and then assign the gain to the wrong mechanism.

---

Scenario: we offer you to go from 2 GPU to 4 GPU in tensor parallelism to accelerate a model 70B. What do you check before? <!--anki:63652b765a21517a6169-->
?
1. **Measure topology**: bandwidth and latency of collectives, intra-node links and network.
2. **Set Objective**: Model that must be stored in memory, individual latency, or useful throughput.
3. **Compare with the same budget**: one TP4 instance against two TP2 instances, if all of them hold in memory.
4. **Examine each GPU**: weight, KV distributed or replicated, activations and imbalance.
5. **Test under load**: goodput, lead times, errors, quality and cost.

**Tip**: Assuming that tensor parallelism necessarily reduces latency, or that NVLink is sufficient to guarantee gain.

---

## Sources

- [Orca — continuous batching](https://www.usenix.org/conference/osdi22/presentation/yu)
- [vLLM — optimization and compromise](https://docs.vllm.ai/en/latest/configuration/optimization/)

- Supplement to the 14 November 2026 — Intermediate memory and dense attention: [Dao et al. — FlashAttention](https://arxiv.org/abs/2205.14135).

## Connections
- [[61-kv-cache-attention|KV cache & attention]] — the memory these techniques handle
- [[64-inference-metrics-slo|Metrics & SLO]] — what we optimize (TTFT, TPOT, throughput)
- [[11-llm-inference-servers|Inference Servers]] — where these optimizations are implemented
- [[51-fine-tuning-adaptation|Fine-tuning]] — quantization and QLoRA
- [[12-kubernetes-gpu-inference|Kubernetes GPU]] — multi-GPU clustered
- [[63-guided-generation|Guided generation]] — constrain output
- [[65-probabilities-sampling|Probability & sampling]] — special decoding: same output distribution
- [[114-reproducibility-variance|Reproducibility & variance]] — batching as a source of non-determinism
- [[67-speculative-decoding|Speculative Decoding]] — technology in detail
- [[68-quantization|Quantization]] — formats and methods in detail
- [[136-mixture-of-experts|Mixture of Experts]] — expert parallelism
- [[54-distributed-training|Distributed training]] — the same parallelisms in training
- [[69-roofline-prefill-decode|Roofline & Disaggregation]] — Why Every Phase Has Its Neck
- [[121-inference-costs|Inference costs]] — cost structure and unit economics
- [[148-llm-batch-pipelines|Pipelines batch]] — process millions of items at a lower cost
- [[60-012-inference-optimization-method|Optimization process]] — prioritize and verify gains under service constraints
- [[66-prefix-caching-radix-attention|Prefix caching]] — reduce prefill according to actual reuse
- [[60-013-prefill-decode-step-by-step|Prefill & decode step by step]] — track calculated positions, cache and delays
- [[00-moc-ai-engineering|MOC AI Engineering]]
