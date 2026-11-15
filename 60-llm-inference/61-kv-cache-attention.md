# KV cache & attention — Flashcards
Tags: #flashcards #ai-engineering #inference #kv-cache #llm
<!-- summary: cache role and size, KV cache, prefix caching and prompt caching, concurrency calculation on an H100, PagedAttention and continuous batching, KV cache in FP8, cost of long contexts, physical blocks and shared prefixes, fragmentation by blocks, residence time. -->


What is the KV cache? <!--anki:4b502378625b2b7e6f5e-->
?
The **KV caches** the keys and values of the positions already processed, at each attention layer. At the decode, we calculate the new K/V and we consult the old ones without redoing all the passage before on the prefix.

For dense attention, the reading of the past remains proportional to the length of the context at each stage; the cumulative cost of generation can therefore grow quadratically. To say that the cache “removes all quadratic cost” confuses avoided recalculation and attention still necessary.

---

What is the size of the KV cache? <!--anki:772d3f6b3d4e527d4575-->
?
It grows **linearly** with: context length × number of layers × heads KV × dimension × accuracy (dtype) × batch size.
```text
bytes per token = 2 (K and V) × layers × heads_KV × dim_head × bytes

Llama 3.1 8B  : 2 × 32 × 8 × 128 × 2 bytes ≈ 128 KiB / token
                → 8,000 tokens ≈ 1 GB context for ONE query
70B (GQA)     : 2 × 80 × 8 × 128 × 2 bytes ≈ 320 KiB / token
                → 8,000 tokens ≈ 2.5 GB per request
```
Hence the importance of **GQA** (few KV heads) and the [[68-quantization|Quantification of the cache]]: they are the ones that determine the concurrency held by GPU.

The length includes prompt and tokens already generated. For queries of different sizes, sum their lengths rather than multiply by an optimistic average. The formula assumes that all layers retain the positions considered; sliding windows, prefix sharing and block allocation change the actual occupation.

---

Do not confuse: KV cache, prefix caching and prompt caching? <!--anki:42435b332d6730765774-->
?
- **KV Cache** : the mechanism **Internal** to a generation. Without him, each token would recalculate the entire context
- **Prefix caching**: the **reuse between requests** of a KV cache already calculated for a common prefix, server-side ([[66-prefix-caching-radix-attention|prefix caching]])
- **Prompt caching**: the same idea **charged** by a API provider, with its writing and reading prices and its TTL ([[123-aggressive-caching|caching]])

The first is indispensable, the other two are cost and TTFT optimizations.

---

Why does the KV cache limit the number of simultaneous requests? <!--anki:3d415a7e614c5e375e-->
?
Because each query takes up **VRAM proportional to its context**: the GPU memory becomes the bottleneck, not the computation.

The remaining budget after weights and other allowances must cover all active tokens, input and output. A long query can take the place of several short ones. Memory is not always the only bottleneck: calculation, bandwidth and SLO can impose a concurrency below the maximum that holds in VRAM. A limit of concurrency and a bounded queue avoid accepting a job impossible to complete within the deadline.

---

What is PagedAttention? <!--anki:6b4d433358527e784d24-->
?
**PagedAttention** organizes the KV cache into non-contiguous physical blocks, associated with the logical positions of a sequence. The server allocates the blocks as it grows, without reserving a large contiguous space for its maximum length.

This organization **greatly reduces waste and fragmentation**; it can remain a partially filled block per sequence and metadata. It also facilitates some block shares. It does not reduce the amount of K/V needed for separate tokens ([[11-llm-inference-servers|vLLM]]).

---

Can we quantify the KV cache? <!--anki:765860436e5b7274564e-->
?
A **FP8** cache uses about half as many bytes for values as a BF16 cache, excluding scales and metadata. This may allow for more tokens residents, subject to hardware support and the engine.
```bash
vllm serve my-model --kv-cache-dtype fp8
```
Check the required formats and scaling factors for the model and version. Measure quality, including long-context, and then load goodput. Half bytes does not guarantee unchanged quality or doubled throughput: kernels, bandwidth, and scheduler limits also count.

---

What is the connection between KV cache and continuous batching? <!--anki:7536444f685b6a7a327a-->
?
Continuous batching causes **batch requests to enter and exit** at each step, so **allocate and release** the KV cache of each request continuously, without fragmenting the memory.

This is what **PagedAttention** allows: the cache is cut into **blocks** of fixed size, like the virtual memory of an operating system, which maximizes the number of requests served ([[62-inference-optimizations|continuous batching]]).

A completed query releases its blocks for the next one; the long sequences continue to grow, so the scheduler must reserve capacity for their decode, not just verify that the new prompts are holding on to the admission.

---

What is the connection between KV cache and long context? <!--anki:793936344b2c75354c44-->
?
The longer the context, the bigger the cache: the **long context costs VRAM and latency**, hence the interest of the [[35-context-engineering|context management]].

For dense attention, each new token consults more K/V as the history grows, so reducing the context can improve both concurrency and decoding time. Quantifying the cache or sharing prefixes helps memory, but does not replace a selection of relevant sources and an output length limit.

---

Calculation: for a 8B BF16 on 80GB, VRAM 90% are usable, weights take 16GB and other 3GB allocations. With 128 KB of KV/token, how many queries of 8,000 tokens in total hold, off margin? <!--anki:6a4724747a7e6e796170-->
?
```text
VRAM utilisable (gpu_memory_utilization 0.9)   ≈ 72 GB
weight 8B in BF16 ≈ 16 GB
activations, graphes CUDA                      ≈  3 GB
remains for the KV cache ≈ 53 GB
KV by token (Llama 3.1 8B) ≈ 128 KiB → 8,000 tokens ≈ 1 GB
→ about 50 full context simultaneous queries
```
Beyond that, requests **wait in queue** or are **preempted** (recalculated or swap), and p99 latency explodes. In FP8, the KV cache can increase memory capacity ([[64-inference-metrics-slo|Competition]]).

These are approximate memory capacities, with decimal Go and a cache of about 128 KiB per token. Also reserve the tokens that will be generated and the engine margins. **Twice as many bytes per K/V does not guarantee twice as many requests in the SLO**: check bandwidth and latency in load.

---

Calculation: Two GPUs of 80GB have 90% of usable memory, 70GB of FP8 weight and 6GB of other allowances in total. With 320 KB of KV/token and a perfect distribution, how many requests of 8,000 tokens hold, out of margin? <!--anki:6137666465353731643634663436353938383237353137393038343239396564-->
?
The total KV budget is `2 × 80 × 0,9 − 70 − 6 = 68 GB`.
```text
KV/query = 8,000 × 320 × 1,024 bytes = 2.62144 GB
68 / 2.62144 ≈ 25.94 → at most 25 complete queries
```
Rounding up to 26 overestimates the capacity under these assumptions. It is an ideal memory cap, not a concurrency under SLO. Include output growth and reserves, then check each GPU: a sufficient total does not guarantee a compatible distribution. Quantifying the KV can increase this cap without doubling the useful throughput.

---

What happens if you double `max_model_len` on a vLLM server? <!--anki:3066363230336533336366653437396238396664636166383237643436363065-->
?
We **allow longer sequences**, without automatically doubling the KV of each request. With paginated allocation, the occupation mainly follows the tokens actually preserved.

For a dense attention keeping all the context, double the length actually used approximately doubles the KV per request; at budget KV fixed, less long requests hold together. Other allocations and mixtures of lengths make it impossible to deduce a concurrency exactly divided by two.

The new limit can also exceed the verified capacity at startup, depending on version and configuration.Size on the actual need, and then measure memory, preemptions and latency with requests reaching this limit.

---

Why shouldn't prefix sharing count the same KV memory twice? <!--anki:3739386333386638663161633437653661656437336639386432393534653266-->
?
**Sequences sharing a prefix** can reference the same physical KV blocks. Add naively all their logical tokens then overestimates the memory actually allocated.

Separate shared blocks, clean suffixes, partially filled blocks and engine reserves. Conversely, an estimate assuming perfect sharing becomes too optimistic when prefixes diverge or are discarded. Check engine metrics with a representative workload. The number of tokens in the context remains a logical magnitude; the capacity depends on the physical blocks and their reuse policy.

---

Calculation: a KV cache allocates blocks of 16 tokens. Three independent sequences each use 17 tokens, without sharing. How many seats are reserved and what fraction is unused? <!--anki:3831316637326334646661663432336439333232666237363163333331613339-->
?
Each sequence requires two blocks, so **3 × 2 × 16 = 96 seats** for 51 tokens useful. There is **45 seats**, or **46.875%** of the reservation.

This is an illustration of internal fragmentation, not including metadata or other allocations. Smaller blocks reduce this waste, but can increase management costs. The sizing must take into account actual lengths and eventual sharing.

---

Why can a slow client increase the memory occupancy of the inference service? <!--anki:6665366135303961616362323466663262313639343235326639323864616262-->
?
If the system keeps the query active during sending, the **residence time of its states and buffers** increases. This can reduce the available concurrency even when the GPU calculates fast.

Examine the coupling between generation, buffering and network. Block buffers, manage delays and propagate cancellations. The KV can be released before the end of the transfer in some architectures: measure the actual behavior rather than infer it from the duration of the client flow alone.

---

## Scenarios

Scenario: your vLLM service holds 60 simultaneous queries with prompts from 2,000 tokens, but more than 8 when you switch to 32,000 tokens context. Why, and what do you do? <!--anki:793e766f644d6c763c68-->
?
1. **Cause**: the KV cache grows **linearly with context**. With context multiplied by 16, each query takes up 16 times more VRAM
2. **Check**: KV cache and preemption occupancy rate, rather than using GPU ([[93-monitoring-inference|monitoring]])
3. **Save space**: **Quantify the KV cache** in FP8, quantify weights to release VRAM ([[68-quantization|quantization]])
4. **Reduce context**: sort what you send, summarize, retrieve less chunks ([[35-context-engineering|context engineering]])
5. **Otherwise, size**: more VRAM per GPU, or more replicas, with the cost that goes with it ([[121-inference-costs|costs]])

**Trap**: Promising a 128,000 tokens context without recalculating the possible concurrency.

---

Scenario: your team wants to activate the FP8 quantization of the KV cache to double the concurrency. How do you validate the decision? <!--anki:677257392a29685b5b40-->
?
1. **Understand the gain**: cache values are about twice as small; check the extra costs and the SLO before promising more queries
2. **Measure loss**: compare answers with and without, on your own evals, paying attention to long contexts ([[68-quantization|validation]])
3. **Tester in charge**: throughput, TPOT and pre-emptions to the target concurrency ([[64-inference-metrics-slo|SLO]])
4. **Deploy gradually**: canary, with quality monitoring in production
5. **Document**: this is a setting that changes the outputs, so it must appear in the versioned configuration

**Trap**: Enable cache quantization and weight quantization at the same time, without being able to assign degradation.

---

## Sources

- [PagedAttention — memory and attention](https://arxiv.org/abs/2309.06180)
- [vLLM — quantified KV cache](https://docs.vllm.ai/en/latest/features/quantization/quantized_kvcache/)

- [vLLM — KV blocks and prefix cache](https://docs.vllm.ai/en/latest/design/prefix_caching/) — targeted deepening of the 12 November 2026; educational examples are built for this review.

## Connections
- [[62-inference-optimizations|Inference optimizations]] — prefill/decode, batching
- [[64-inference-metrics-slo|Metrics & SLO]] — the concurrency capped by the VRAM
- [[11-llm-inference-servers|Inference Servers]] — vLLM & PagedAttention
- [[09-gpu-containers|GPU in container]] — the underlying VRAM
- [[35-context-engineering|Context engineering]] — control the context size
- [[66-prefix-caching-radix-attention|Prefix caching & RadixAttention]] — re-use cache in detail
- [[68-quantization|Quantization]] — Quantify Weight and Cache
- [[131-transformer-architecture|Architecture Transformer]] — attention, GQA, RoPE
- [[137-long-context|Long context]] — cost of long contexts
- [[65-probabilities-sampling|Probability & sampling]] — temperature, top-p and logprobs
- [[69-roofline-prefill-decode|Roofline & Disaggregation]] — which limits each phase of the inference
- [[12-kubernetes-gpu-inference|Kubernetes GPU & inference]] — serve models on a GPU cluster
- [[164-local-edge-llm|Local LLM & Edge]] — run a model locally
- [[67-speculative-decoding|Speculative Decoding]] — generate multiple tokens per pass
- [[84-streaming-application-integration|Streaming & integration]] — SSE, cancellation and long tasks
- [[60-011-inference-capacity-scheduling|Capacity & scheduling]] — connect memory, budgets and payload under load
- [[60-013-prefill-decode-step-by-step|Prefill & decode step by step]] — track calculated positions, cache and delays
- [[00-moc-ai-engineering|MOC AI Engineering]]
