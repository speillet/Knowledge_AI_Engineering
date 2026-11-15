# Prefix caching & RadixAttention — Flashcards
Tags: #flashcards #ai-engineering #inference #kv-cache #caching #llm
Verified on: 12 November 2026 — mechanisms and limits against cited articles and documentation; performance to be measured on the target.
<!-- summary: vLLM prefix caching, SGLang radix tree, eviction, scheduling and cache-aware routing, offloading of the KV cache (LMCache), limits, time auxiliary channel, query metrics and token, real TTFT gain, affinity and overload, cache_salt isolation, step-by-step compressed tree, references and branch separation, sharing computation. -->


What is server-side prefix caching? <!--anki:703830706b2926403428-->
?
The **prefix caching** reuses the keys and values already calculated for the exact start of a sequence, with the same model and a compatible state. It avoids recalculating the representations of these positions during the prefill of another request.

If the initial 3,000 tokens of a 3,200 prompt is reusable, the new 200 must still traverse the model and view the past. The cache does not provide a final answer or semantic search. The gain depends on the work avoided, the transfers and the queue; the decode continues to read the context and calculate the following tokens.

---

How does vLLM implement automatic prefix caching? <!--anki:4e4853344a45633c4345-->
?
vLLM **Blocks KV Physical** to the tokens of logical sequences. To recognize a prefix block, His identity depends in particular on tokens, the parent block and compatibility information such as adapt, Multimodal content or cache salt.

Two blocks with identical text but preceded by different contexts are therefore not interchangeable. A table makes it possible to find the reusable blocks; the management of references and the eviction control their lifetime. Granularity and behavior depend on the version: distinguish common logical prefix and tokens actually reused. PagedAttention organizes the memory; the prefix cache decides its reuse.

---

What is RadixAttention? <!--anki:71516b533b7348404c3e-->
?
**RadixAttention** organizes the reuse of the KV cache in SGLang by means of a **radix tree**, a prefix tree whose paths without bifurcation are compressed into sequences of tokens.

The search engine searches for the longest prefix already calculated and compatible, retrieves its KV references, and then calculates the sequence and inserts it into the tree. The tree contains search metadata; tensors live in the memory pools of the engine. The word "attention" does not designate a new formula of softmax: optimization avoids repeated calculations between queries, conversations or branches sharing exactly their beginning.

---

How does SGLang flush out the entrances to the radix tree? <!--anki:746d6a686e7c2f454321-->
?
In the classic mechanism described by RadixAttention, The eviction chooses **Reusable sheets according to their age**, by protecting by references the paths used by active queries. Releasing a sheet can make its parent a candidate himself.

The little used suffixes often disappear before a shared prefix. This is not a guarantee of conservation: if an entire subtree becomes inactive, it may eventually be removed. Recent versions offer several hybrid policies and caches; check the configuration. Never discard a block still necessary for an active calculation to artificially improve the hit rate.

---

What is cache-aware scheduling? <!--anki:736e6973636b5e717b7b-->
?
A **Scheduler sensitive to cache** uses possible re-use to order requests, Instead of just considering their arrival. The longest-prefix-match policy favors those who find a long compatible prefix.

This can dampen the processing of a shared document before it is discarded. It is not always the best user delay: a query without a hit can wait indefinitely if new hot requests arrive. Combine age, deadline, load and equity; compare the work saved to the time spent in queue. At low load, the choice of order often counts less than the cost of the prompt and speed of the model.

---

Which workloads benefit the most from prefix caching? <!--anki:4c337b29762e50327361-->
?
- **Multi-tour agents**: History grows but its beginning does not change
- Long **prompt system and shared tool definitions**
- **Few-shot**, **self-consistency**, reasoning trees: same prefix, multiple branches
- **RAG** repeated on the same documents
- Many users on a **same assistant**

The gain depends on the tokens actually reused, not just the number of hits. A query with 100 tokens shared on 10,000 takes little advantage of the cache. Measure length of the reused prefix and TTFT, with planned access isolation.

---

Why should the routing between replicas take cache into account? <!--anki:723d5362493f5e2c4929-->
?
When caches reside **locally on replicas**, blindly distributing requests scatters hot prefixes. A router may prefer the instance that already has the compatible prefix, subject to rights and its load.

Compare queue delay, prefill remaining, and possible transfers; a hit on an overloaded instance may be less useful than a new calculation elsewhere. A hierarchical or shared cache changes this trade-off, without removing the KV's travel costs. Repeat the reused tokens and actual latency, rather than assuming that any affinity improves service.

---

What is KV cache offloading? <!--anki:482b3a513b2b5b7e2545-->
?
**offloading** moves or saves K/Vs out of GPU memory, for example in host RAM or on hierarchical storage. It increases the conserveable volume, but reuse requires a transfer to the place of calculation.

Compare recovery cost, avoided calculation and contention on links. A long prefix can be profitable to reload; some tokens can be cheaper to recalculate. When transfers are recoverable with the calculation, part of the delay can be hidden, without disappearing from the bandwidth budget. Include allocations, synchronization and isolation of data in the evaluation.

---

What are the limits of prefix caching? <!--anki:7a28604f3a4f7871363e-->
?
- Match **exact from the beginning**: a different token in mind, and nothing is reused
- **Granularity per block** (vLLM only hides full blocks)
- Cache **limited** by memory and removed under heavy load
- Accelerates only the **prefill**, not the generation (decode)

A timestamp placed before stable statements can invalidate the entire prefix at each call. Move variable data after this prefix if semantics allow, and then verify the gain under the same load and routing.

---

What security risk does a shared prefix cache pose? <!--anki:6b45506d623c422f4b4a-->
?
A **Time Channel** can reveal that a guessed prefix is already cached: its reuse reduces part of the prefill. The attacker observes times, not directly the tensors or the neighbor's text.

Repeated testing and prior knowledge can make this index actionable in spite of noise. Define an authorized sharing boundary, and then impose server-side appropriate separation, such as a secret cache salt per trusted group when the engine allows it. Check the precise offer and functionality: no universal rules of isolation of all providers should be assumed.

---

How to measure the effectiveness of the prefix cache? <!--anki:79677d5a467a362a2129-->
?
Measure **tokens re-used**, TTFT and cost, not just queries with a hit. Check the exact unit of the engine or vendor metrics ([[123-aggressive-caching|caching agressif]]).

Simplified example: one query of 100 tokens fully reused and another of 9,900 tokens without hit give **50% queries with hit**, but only **1% of tokens reused**.

Compare cold/hot cache at the same load and lengths, including evictions and occupied memory. A drop can come from an unstable prefix, but also from a change in traffic, routing or memory pressure. A high hit does not ensure a drop in the TTFT if the wait dominates.

---

Calculation: for a prompt of 10,000 tokens including 9,000 reused, suppose a prefill going from 300 to 30 ms and 200 ms fixed waiting/transport. What gain of TTFT, excluding additional cache costs? <!--anki:6365333934613162646331393439376661353639326434613561303631636664-->
?
Suppose a prefill of 300 ms without cache, reduced to 30 ms for unhidden work, and **200 ms fixed** waiting and transport:
```text
TTFT without cache = 200 + 300 = 500 ms
TTFT with cache = 200 + 30 = 230 ms, before additional costs
Acceleration = 500 / 230 ≈ 2.17, not 10
```
New tokens still see the K/Vs of the prefix; loading and searching the cache may add time. The factor ten on the simplified prefill does not translate to full latency or decode.

---

Calculation: nine 100 tokens prompts are fully reusable in cache and one 9,100 tokens prompt is not. What hit rates per request and per token do we get? <!--anki:3364316439313634633036333430353638346561626463623734633461366439-->
?
Nine 100 tokens prompts are fully reusable, but one 9,100 tokens prompt is not. The request rate with hit reaches **90%**, while the share of reusable tokens is only worth `900 / 10 000 = 9 %`.

Set the unit of the counter: request with partial hit, block or token; check the one of the engine. Calculate the ratios from the sums, not the average ratios of the replicas. Even the rate per token does not directly measure the saved milliseconds: length, file and transfers intervene.

---

When should cache affinity be waived when routing? <!--anki:3661383866353637343861373430323761343465633631363938343461373764-->
?
When the time saved by the local prefix becomes less than the additional wait of the hot replica. Compare **expected time of queue + remaining prefill + transfers** to alternatives, then check the prediction in load.

A purely hit rate policy can focus traffic on a few instances and degrade the p99. Provide a load gap threshold, cross-client fairness, and privacy boundaries. The cache mostly improves input work; it does not make it free to read context in decode or tokens output.

---

How to isolate the prefix cache vLLM between holders without losing any sharing inside a holder? <!--anki:3431366139336134386564663464613639396632653131333339366263386235-->
?
The documented version of vLLM allows a **`cache_salt`** per request: it participates in the hash of the first block, which separates the reuse between different values.

Have the gateway assign a stable secret value for each trust group and then pass it on to all of its calls. Do not let one client choose another's salt. A random salt on each request would also delete the desired share. Test hits and actual separation; this mechanism does not replace permissions on data and other caches.

---

Do not confuse: RadixAttention, PagedAttention and FlashAttention? <!--anki:3638343633313466366663623439303138376531383064356131386566353362-->
?
**RadixAttention** identifies prefixes already calculated to reuse their state. **PagedAttention** organizes the KV into physical blocks addressed by logical sequences. **FlashAttention** optimizes the calculation of attention and its memory transfers without materializing the entire score matrix.

These roles are complementary: find a prefix, manage its pages, and calculate new positions efficiently. None of them transform a text that looks like a reusable cache. Their combination and the available kernels depend on the engine; measure the work avoided and the calculation remaining instead of multiplying acceleration factors announced separately.

---

How does a radix tree represent two prompts that diverge after three tokens? <!--anki:3066383534356432373639383465393061316435346433326565666362326235-->
?
Suppose the tokens symbolic `[S,A,B,C]` then `[S,A,B,D,E]`. The common prefix of length three remains unique; the suffixes separate:
```text
racine
  └─ [S A B]  → shared KV references
       ├─ [C]   → suffix of request 1
       └─ [D E] → suffix of request 2
```
An edge carries several tokens, unlike a naive sorting with a node by token. The second query reuses the states of `S,A,B`, then calculates `D,E` by consulting this past. These letters are pedagogical tokens identifiers, not characters supposed to correspond to the tokens of a real tokenizer.

---

What happens if a new prompt diverges in the middle of an existing radix edge? <!--anki:3664383234653336326238643466616662353233396564326536333038333131-->
?
The engine **the Edge Split** border of the common prefix. If the tree contains `[S,A,B]` and receives `[S,A,F]`, he creates a knot after `[S,A]`, Then two paths `[B]` and `[F]`.

The already calculated KV states of `S,A` remain reusable; splitting the metadata does not mean recalculating these tokens. References must nevertheless respect the page constraints of the allocator. This splitting makes possible shorter future shares and several branches. A divergence of the third token does not invalidate the first two, if model, positions and cache perimeter correspond.

---

Why aren’t identical tokens in the middle of two prompts enough to share their KV cache? <!--anki:3161633764316361323036363437333839626532646334623131633237366235-->
?
In a **Causal Transformer**, the state of an token It depends on its predecessors through the layers. The word “Paris” after two different contexts can therefore produce different keys and values, even with the same ID of token.

Secure sharing is about an identical start in a compatible state, not about a substring found elsewhere. Positions, model, adapt, and multimodal inputs also count. RadixAttention looks for this prefix identity; it does not approximate paraphrases. A semantic cache of answers answers answers answers another question and requests further validations.

---

How do references protect a shared prefix during a decode? <!--anki:6237343037376338656364363432313138393961666466383365363037653336-->
?
An active query **retains references** to blocks that its attention still needs. A second query can retain the same prefix blocks, while allocating its own suffixes.

When a request ends, it releases its references; blocks should not be recycled as long as another drive uses them. Without an active drive, they can remain cached, and then be discarded according to policy. Sharing blocks does not give the right to write arbitrarily: a divergence requires separate states, with a copy if a partially shared block needs to be modified.

---

Calculation: how many separate tokens KV for prompts [S,A,B,C], [S,A,B,D,E] and [S,A,F] with ideal sharing? <!--anki:3435306465323963653338383466303862623737613262323966303436353764-->
?
Without sharing, the lengths total `4 + 5 + 3 = 12` positions. The ideal shaft retains:
```text
[S A]: 2 positions shared by the three prompts
[B]: 1 shared by the first two
[C]   : 1 ; [D E] : 2 ; [F] : 1
total = 7 positions KV distinctes
= 5 / 12 ≈ 41.7%
```
The calculation assumes compatibility and exact sharing, outside partially filled pages, metadata and new outputs. It measures the avoided logical storage, not an identical decrease in the total time: suffixes still calculate their attention on the prefix and the answers remain to be generated.

---

Why doesn't changing the temperature necessarily make a KV prefix unusable? <!--anki:3463383939633963313663333462356638353665323263663561643365383238-->
?
The **Sampling Temperature** acts on the logs used to choose an output; it does not change the representations of a fixed prefix when the model and its calculation remain the same.

So two queries can share the same prefix and then generate different suites. However, these new suites only share their cache as long as their tokens exactly coincide. Modifying weight, adapt, positions or entries potentially changes states and requires appropriate separation. The sharing decision also depends on the keys and rules of the engine; do not confuse mathematical eligibility with actually configured behavior.

---

Why isn't a long match of tokens always enough with a recent hybrid cache? <!--anki:3239343937633630313830633432663039353766333038316331356132366262-->
?
A hybrid engine can retain **several state types**: full attention, sliding window, or recurring state. The presence of a tokens path does not prove that each component still has the necessary state at this boundary.

The SGLang Unified Cache looks for a reuse boundary that is accepted by all required components. An out-of-place or non-checkpoint component can shorten that boundary. Simple radix tree schemes therefore describe the classic case, not all guarantees of a hybrid model. Check the architecture and the actual reuse counters before converting a common length into expected gain.

---

Why can a full prefix cache hit still require a bit of calculation? <!--anki:3561343831646530616437323465633862333831653032383932363830303534-->
?
A **Cache KV** keeps keys and values, not necessarily the final logs or the distribution of the next token. Even if all the prompts correspond, the engine may have to replay its last position or use another stored state to obtain this distribution.

Cache search, compatibility checks, allocation and possible forwarding also add delay. “All tokens were already known” does not mean TTFT null. Check what counts the engine as hit and as recalculated token; distinguish reuse of representations, availability of logs and issue of the first token.

---

Calculation: One cache only shares complete blocks of 16 tokens. Two prompts share exactly their first 30 tokens then diverge. How many tokens can they reuse according to this rule? <!--anki:3161306464643963313063623438326561303738653264613238313339313939-->
?
A single complete block belongs to the common prefix: **16 tokens**. The following 14 do not constitute an entirely identical second block.

This calculation describes a given alignment rule, not all radix engines or hybrid caches, so the text prefix can overestimate the reusable work. Measure the tokens actually served from the cache and distinguish logical match, physical allocation and avoided calculation.

---

Why should I invalidate or separate the prefix cache when changing weight or adjusting? <!--anki:3365366634333865316139353433306362386365323563643562386563303538-->
?
The K/V depends **calculation of the model**, not just identifiers of tokens. The same prompt treated with different weights usually does not produce the same states.

The key and the perimeter of the cache must distinguish between configurations that change these states, including the applicable adaption. Testing a model toggle with hot cache. Sharing prefixes between incompatible variants can produce erroneous outputs without visible format errors.

---

## Scenarios

Scenario: your multi-turn assistant displayed 70% hits on the prefix cache. After an update, the rate drops to 5% and the TTFT doubles. What are you looking for? <!--anki:7964774643443c5a3328-->
?
1. **Compare tokenized** entries before and after update: prompt start, template, tools, variables, and document order.
2. **Check cache compatibility**: model, adapt, positions, salt, and share perimeter.
3. **Examine exploitation**: cold replicas, routing, evictions and pressure of active sequences.
4. **Restore a stable prefix if meaning allows**, then replay the same traffic with and without reuse.
5. **Measure tokens reused and delays**, distinguishing file and suffix calculation.

**Trap**: Move data into the prompt to maximize the hit without checking for quality or privacy effects.

---

Scenario: you go from 1 to 4 replicas vLLM behind a classic load balancer, and the TTFT degrades while you have more than GPU. Why? <!--anki:6e67712c2325372c714e-->
?
1. **Test the dispersion hypothesis**: local caches heat up separately and traffic may lose its affinity.
2. **Compare replicas**: repurposed lengths, queues, ejections and starting weights.
3. **Evaluate cache-sensitive routing**, which arbitrates prefill gain and wait time.
4. **Testing fairness and sharing boundaries**, without focusing on a saturated instance.
5. **Study a hierarchical or shared cache** only if transfers and coordination are amortized.

**Trap**: Attribute any degradation to the cache without eliminating saturated storage, limited load generator, or changing the query mix.

---

Scenario: your multi-client service shares the same model, and a client is worried that its prompts may leak through the cache. What do you answer? <!--anki:7542547e2e756e342652-->
?
1. **Describe risk**: A response time can provide a clue to a guessed prefix already present, without directly reading the cache.
2. **Definite the group authorized to share**: user, holding or other justified trust boundary.
3. **Impose server-side separation**, with appropriate cache keys or separate instances; a client does not choose the perimeter of a neighbor.
4. **Test other shared states**: media, index, memory, and logs.
5. **Measure the compromise** between confidentiality, hits and capacity, with the mechanisms of the deployed version.

**Trap**: generalize the commitments of a commercial API to all its products, or assume that a hash of tokens constitutes an authorization.

---

## Sources

- [vLLM — automatic prefix caching and limits](https://docs.vllm.ai/en/latest/features/automatic_prefix_caching/)
- [SGLang — server documentation and optimizations](https://docs.sglang.io/)

- [vLLM — cache isolation and security](https://docs.vllm.ai/en/latest/usage/security/) — targeted deepening of the 12 November 2026; educational examples are built for this review.

- [Zheng et al. — RadixAttention, classic mechanism and references](https://arxiv.org/html/2312.07104v2) — targeted review of 12 November 2026: compressed tree, sharing, eviction and scheduling.

- [SGLang — policies for removing the radix cache](https://github.com/sgl-project/sglang/blob/main/docs/docs/advanced_features/radix_eviction_policy.mdx) — targeted review of 12 November 2026: current policies, to be distinguished from the classical mechanism.

- [SGLang — unified radix cache](https://www.sglang.io/blog/unified-radix-cache) — targeted review of 12 November 2026: common reuse boundary for hybrid model components.

- 14 November 2026 — Complete blocks, divergence and cache identity: [vLLM — Automatic Prefix Caching](https://docs.vllm.ai/en/latest/design/prefix_caching/).

## Connections
- [[61-kv-cache-attention|KV cache & attention]] — PagedAttention and prefix caching
- [[62-inference-optimizations|Inference optimizations]] — prefill and decode
- [[11-llm-inference-servers|Inference Servers]] — vLLM and SGLang
- [[82-routing-llm|Routing LLM]] — Prefix affinity between replicas
- [[64-inference-metrics-slo|Metrics & SLO]] — TTFT and flow
- [[123-aggressive-caching|Caching agressif]] — design prompts for cache
- [[137-long-context|Long context]] — limits and cost of long windows
- [[51-fine-tuning-adaptation|Fine-tuning]] — adapt a model, LoRA and QLoRA
- [[69-roofline-prefill-decode|Roofline & Disaggregation]] — which limits each phase of the inference
- [[60-011-inference-capacity-scheduling|Capacity & scheduling]] — connect memory, budgets and payload under load
- [[60-013-prefill-decode-step-by-step|Prefill & decode step by step]] — track calculated positions, cache and delays
- [[00-moc-ai-engineering|MOC AI Engineering]]
