# Inference Capacity & Scheduling LLM — Flashcards
Tags: #flashcards #ai-engineering #inference #capacity #scheduling #gpu
Verified on: 8 October 2026
<!-- summary: Sequence and tokens budgets, actual KV memory, GQA and sharding, preemption, admission, priorities, queues, replication and parallelisms, backup and cancellation capacity, KV reservation for outputs, stability margin, starvation risk. -->


Do not confuse: context limit, batch budget and KV capacity? <!--anki:3362373534643136313937303463623238346633646336363064366238343532-->
?
The **context limit** limits the length of a sequence; the **batch budget** limits the scheduled work for an iteration; the **KV capability** limits the in-memory resident states.

In vLLM, `max_model_len`, `max_num_batched_tokens` and `max_num_seqs` play different roles: length by sequence, planned tokens and number of sequences. None alone gives the total of tokens already stored. A batch can generate only 32 new tokens while retaining hundreds of thousands of tokens of context.

---

How to set max_num_seqs and max_num_batched_tokens together? <!--anki:6236383933626232323836333435393439313637633131646563633230363966-->
?
**`max_num_seqs`** limits the sequences processed together; **`max_num_batched_tokens`** limits the tokens work of an iteration. With chunked prefill, this budget is divided between prefill and decode.

Example: Allowing many sequences does not guarantee their admission if their KVs saturate the memory. Increasing only the budget of tokens can accelerate the prefill but lengthen the iterations and degrade the ITL.

Scan both parameters on a fixed mix, then on realistic spikes. Hold the best **goodput under SLO**, not the maximum of tokens/s. Follow TTFT, ITL, preemptions, refusal and memory; log the actual values and version.

---

How to calculate the KV memory of a set of active queries? <!--anki:3035346430336531636264653436306338323332653965663263373239653236-->
?
For a classic attention to explicit K/V:
```text
KV = 2 × layers × heads_KV × dimension_head × bytes_by_value
     × sum of resident lengths
```
Add rounding to blocks, metadata, and output growth; subtract blocks that are actually shared once. Queue queries without a calculated state do not consume this KV.

Do not apply this formula mechanically to MLA, hybrid, sliding window or recurrent state architectures: their storage differs. From the configuration and measured allocations, then check the budget **by GPU** after weights, activations and graphs.

---

Calculation: with 32 Layers, 8 Head KV of dimension 128 and BF16, without sharing or extra cost, How many sequences of 8,192 tokens The Dancers 40 GiB KV, If each of them has yet to generate 1,024 tokens ? <!--anki:3532326462613730363863393431666562613063613831666137623434363739-->
?
Assumptions: 32 layers, 8 heads KV, dimension 128, BF16, no sharing or extra cost.
```text
bytes/token = 2 × 32 × 8 × 128 × 2 = 131 072 = 128 KiB
KV/sequence = 8,192 × 128 KiB = 1 GiB
Ideal memory capacity = 40 GiB / 1 GiB = 40 sequences
```
The 8,192 tokens includes the already generated context. If each sequence still has to produce 1,024 tokens, count 1.125 GiB and at most 35 sequences, before margin. The capacity meeting the deadlines can be less than this memory ceiling.

The additional output reduces the maximum concurrency even if the input remains the same. For safe admission, take into account the envelope generated, the rounding in blocks and the engine allocations; the raw memory quotient does not define the SLO.

---

Why don't GQA and tensor parallelism always divide the KV as expected? <!--anki:6562633831303763333161303431626638326462383633366439346333303435-->
?
**GQA** uses fewer K/V heads than query heads; **MQA** uses only one. The KV size depends on the K/V heads and the attention scheme, not just the number of parameters.

The tensor parallelism divides these heads between GPU, but not below one head per row. Example: a model with 8 Head KV Served in TP=16 Retaliate each head in two rows. on the KV by GPU Don’t go further than TP.=8. Do not blindly divide the memory KV Total by the number of GPU : check the blocks available on each row. GQA is a property of the model, Not just a server button.

---

How can preemptions cause an overload spiral? <!--anki:6665383431303464626231633466626139646535336665333961356461393738-->
?
A lack of KV can interrupt sequences. If their state is dropped, the **recalculate** resume part of the prefix; other engines or configurations can move the state to slower memory.

Example: A sequence interrupted by 6,000 tokens the Context Pass 6,000 tokens through prefill in its recovery. This work delays the new prompts, the queue is getting longer and other sequences are missing KV in their turn. Follow preemptions and goodput distinguishing recalculation from new ones tokens user. Reduce admission or concurrency, or book more KV. An occasional pre-emption is not a breakdown; Their repetition calls for a targeted measure.

---

Why limit an inference queue in work and on time? <!--anki:6365313337636366326361353438663838353335336434326539313636613036-->
?
The number of queries hides their cost: a long prefill and a long generation weigh differently. Estimate tokens input not hidden, output budget and service time per class, without assuming an identical cost for all tokens.

Use queue size, age and deadline for admission. Example: with a response time of 10 s and 25 s of work estimated in front of it, an interactive request can no longer succeed; refuse it immediately or pass it deferred, according to an explicit product policy. The output lengths being uncertain, keep a margin. An unlimited queue transforms the overload into answers that have become useless.

---

How to prevent a scheduler from always favoring the same requests? <!--anki:3537336661643663313932623430623761363664313164626264373131653061-->
?
Prioritizing short tasks or hot prefixes can improve throughput and average, but make long requests or cold caches wait indefinitely.

Add quotas per client, service classes and **prioritization aging**; measure maximum wait, refusal and compliance per segment. Example: a client sends 5,000 batch requests at once; in FIFO, interactive users wait behind the entire burst. One quota per client or a weighted queue, two rounds for the interactive and one for the batch, limits this wait. Do not confuse a better average obtained by selection with an improvement for each category.

---

Do not confuse: replication, tensor parallelism and pipeline parallelism? <!--anki:3435316663353362616166613463613839656633323261313734616664306631-->
?
**replication** distributes requests between independent copies, each of which must be able to serve the model. **tensor parallelism** shares operations of a layer; **pipeline parallelism** distributes layers in stages.

The last two help to hold the model, with communications or pipeline bubbles. They do not guarantee a decrease in latency. Example: with 8 GPU of 80 GB and 60 GB of weight, Compare four TP replicas=2 and a TP instance=8. The first option isolates failures and multiplies caches; The second offers more KV by request, with collectives between 8 GPU. Measure Goodput and SLO on the real mix.

---

What does a MoE model add to inference sizing? <!--anki:6639623562343139636334643461616138666331393639373064336565316437-->
?
The parameters **active by token** influence the calculation, but the experts to keep or move also determine the memory and transfers. Two MoE with the same number of active parameters can have very different performance.

The expert parallelism splits the experts and introduces tokens exchanges between GPU. Example: if the router sends 30% of the tokens of a batch to two experts placed on the same GPU, this rank finishes last and all iteration awaits it. Track the load per expert and the dispersion between ranks, on the routes actually produced by the traffic.

---

Calculation: a replica supports 12 requests/s under SLO, with additive capacity and perfect balancing. How many requests/s does it take to serve 40 requests/s after losing a replica? <!--anki:3230353961333839616538333432343738386665633536663137383738373763-->
?
If each replica supports **12 requests/s under the same SLO and mix**, you need `(n − 1) × 12 ≥ 40`, so **n ≥ 5**. Four are arithmetically sufficient without failure, but only three would remain after loss, i.e. 36 requests/s.

It is a terminal under assumptions of balancing and additive capacity. Check cold caches, common dependencies, transfers and spikes; if the measured capacity does not include the necessary margin, add some. A node failure removing multiple replicas requires another scenario.

---

What to measure when scaling a LLM service? <!--anki:3832626163623039653034373461313162313735366162323034383239373339-->
?
In **scale-out**, measure time up to the first job actually served: available resources, loaded weights, compilation, warm-up and still cold cache. If this delay is 6 minutes, a peak of 3 minutes is only covered by an already hot reserve or a limited admission.

In **scale-in**, remove the replica from the routing, drain the requests and limit this phase according to their deadlines. Local KV states and session affinity can be lost. Stabilize autoscaling decisions to avoid an oscillation where instances disappear before cushioning their startup.

---

Why is cancellation part of capacity optimization? <!--anki:3134313338356131303230623462336362613862363032373266353534643463-->
?
After abandonment, timeout or choice of another response, an engine can continue to generate if the cancellation does not reach it. It then consumes calculation, KV and quota without producing any value.

Example: a user closes the tab after 2 s; without propagation, the engine still produces the 1,500 tokens expected, i.e. 30 s from a place of decode to 50 tokens/s. Spreading an excessive time budget and a cancellation signal through application, gateway and server, and then measuring the tokens products without output.

---

Why does booking only the entry tokens underestimate the KV capacity needed? <!--anki:3530333337623339643261663432313238653438316232343661303830626135-->
?
The **KV cache grows during generation**. Admitting sequences only according to their prompt can saturate the memory when they simultaneously produce their outputs.

Estimate an envelope input plus output, according to the observed lengths and contractual limits, and then keep a margin for the other allocations. Follow preemptions, long exits and distribution by request. A maximum reservation anywhere can be too conservative; choose a measured admission policy, with preemption or explicit refusal. Free memory at the beginning is not a guarantee of capacity until the end.

---

Calculation: A server terminates 20 requests/s while 23 requests/s are allowed for 30 seconds, without abandonments and with an initially empty queue. What additional backlog is formed? <!--anki:3665653138366239383766613439623061653639356139616431356563643337-->
?
The imbalance is **23 − 20 = 3 requests/s**, or **90 additional requests** in 30 seconds.

This calculation assumes a constant output rate and sufficient queue capacity. At a load that is permanently higher than the service, the queue does not stabilize. It is necessary to reduce the intake, increase the useful capacity or explicitly degrade the service; expanding the queue does not correct this imbalance.

---

## Scenarios

Scenario: Increasing concurrency lowers the useful throughput while there is still VRAM. What do you check? <!--anki:6231306139313863363538643466363462326464356634393062323236303362-->
?
1. **Distinguish allocated VRAM and busy KV**, then measure preemptions and memory by rank.
2. **Observe iterations**: More sequences can slow down decode and communications.
3. **Review the mix**: long contexts, missing prefixes, new formats or images.
4. **Scan Sequence and tokens budgets** with constant SLO.
5. **Keep the point useful** and a limited admission, instead of filling the memory at all costs.

**Trap**: Assimilate available memory capacity and service capacity on time.

---

Scenario: short prompts respect the SLO, but long documents wait indefinitely. How do you fix it? <!--anki:3030383438313232393336663431323239336637633565633937303062343563-->
?
1. **Segment** Waiting, Refusals and Goodput by Length and Client.
2. **Identify priority**: preference for short queries, decodes, or hot prefixes.
3. **Add a rule of fairness**: aging, quota or budget reserved for long prefills.
4. **Test compromise**: ITL of active streams, TTFT of new prompts and overall throughput.
5. **Separate the batch** if its deadline allows another pool or another queue.

**Trap**: Publish only the global P95 and make invisible the applications never admitted.

---

Scenario: Two GPUs have enough VRAM in total, but the server fails on a single card. How do you diagnose? <!--anki:6632353263653433623830623438323062353530386231303666303430323737-->
?
1. **Inspect each row**: weights, experts, KV, activations, graphs and other processes.
2. **Check for actual sharing**: replicated KV heads, layers, or unevenly distributed experts.
3. **Reproduce the peak** with identical lengths, modality and batch.
4. **Adapt placement or budgets**, then test quality and latency.
5. **Measure the margin per card** before increasing the load.

**Trap**: Split a memory total by two without checking what the runtime actually allocates.

---

## Sources

- [vLLM — Scheduler Setting and Preemptions](https://docs.vllm.ai/en/latest/configuration/optimization/)
- [vLLM — parallelism and scaling](https://docs.vllm.ai/en/latest/serving/parallelism_scaling/)
- [PagedAttention — memory management and sharing](https://arxiv.org/abs/2309.06180)
- [GQA — query heads and KV heads](https://arxiv.org/abs/2305.13245)
- [Orca — iteration order](https://www.usenix.org/conference/osdi22/presentation/yu)

## Connections
- [[61-kv-cache-attention|KV cache]] — calculate bytes before dimensioning
- [[60-010-inference-load-benchmarks|Load benchmarks]] — validate capacity and transitions
- [[66-prefix-caching-radix-attention|Prefix caching]] — balancing locality and expectation
- [[116-ai-sre-incidents-capacity|SRE AI Services]] — Reserve, Incidents and Admission Policies
- [[136-mixture-of-experts|Mixture of Experts]] — expert placement and communications
- [[60-012-inference-optimization-method|Optimization process]] — prioritize and verify gains under service constraints
- [[00-moc-ai-engineering|MOC AI Engineering]]
