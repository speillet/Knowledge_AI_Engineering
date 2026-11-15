# Architecture Transformer — Flashcards
Tags: #flashcards #ai-engineering #fundamentals #transformer #llm
<!-- summary: attention and weighted sum, causal mask, teacher forcing, multi-head, GQA/MQA and memory KV, MLP, residuals, normalization, RoPE, costs, weight of a 70B, basic model or assistant, explanatory limits of attention weights, softmax normalization, causal context. -->


What is a LLM, mechanically? <!--anki:7074663b5a51392c4f44-->
?
A **LLM** is a large language model. In the common case of a **Autoregressive Transformer decoder-only**, it estimates the distribution of the next token from the prefix. The generation chooses a token, adds it to the context and repeats the operation ([[65-probabilities-sampling|sampling]]).

This description explains the generative models studied here; it does not define all the architectures of language models. Encoder-decoder, hybrid models and other training objectives exist. The probabilities relate to the tokens, not directly to the truth of the claims.

---

What is the path of a token in a Transformer generative decoder-only? <!--anki:6f2477294b6c522a233e-->
?
1. **Tokenisation** → identifiant ([[132-tokenization|tokenizer]]).
2. **Embedding**: the id becomes a vector of dimension d (e.g. 4,096).
3. **N stacked Transformer** blocks (attention + MLP), which enrich this vector with context.
4. **Final standardization** then **projection** to the →**logits** vocabulary.
5. **Softmax** → probabilities of the next token.

At autoregressive inference, the final position predicts the next token; a decoding rule chooses it and then re-injects it. The model does not produce the entire response in a single pass. The intermediate representations are contextual, unlike the input embeddings table.

---

What does the attention mechanism do? <!--anki:4971286368426d485451-->
?
Attention uses a **Q** query to weigh **V** values, comparing Q to the **K** keys.
```text
Attention(Q, K, V) = softmax(Q·Kᵀ / √d_k + masque) · V
```
The softmax normalizes scores on allowed positions. The result is a weighted sum of their V vectors, not a necessarily unique selection. The weights depend on the learned representations; strong attention is not a proof that the passage is true, nor a complete causal explanation of the prediction.

In a causal decoder, the mask prohibits future tokens. Without it during training, the model could use the response it needs to predict.

---

What is Causal Attention? <!--anki:46472b6d792b493b2826-->
?
A **mask forbids viewing future positions**: the representation at position i uses the positions ≤ i to predict the next token. At training, the full text is available, but the mask preserves this constraint while calculating several positions in parallel.

Example: To learn how to complete "The Cat Sleeps", the "cat" position should not see "sleep" before predicting it. This causality describes the order of information in the sequence; it does not mean that the model identifies the causes of events.

---

Why multiple attention heads (multi-head)? <!--anki:70495d3d7d324e5e5848-->
?
Many heads build **Different weights of the same sequence** through their projections; their output is concatenated and then re-projected.

Example: in "Léa poses the file because it is heavy", one head can favor close links, another a relationship with "file". These are learned possibilities, not assigned linguistic roles or a guaranteed explanation of reasoning.

With a fixed total size, adding heads reduces their individual size: it is not a free gain of capacity. With GQA or MQA, the query heads remain multiple but share some K/V projections to reduce memory.

---

What is GQA and MQA, and why do they count in production? <!--anki:6a72557e65666e265368-->
?
**GQA** shares keyheads and values between groups of query heads; **MQA** uses a single K/V head for all queries. At fixed dimensions and accuracy, fewer KV heads means less cache memory and readings during the decode.

The quality compromise depends on the model and its drive. It is not an interchangeable setting without weight adjustment. Distinguish the number of Q heads from the number of KV heads in the calculations; other architectures, such as MLA, use another storage.

---

What is the role of the feed-forward block? <!--anki:6b6439385d5d4f3b3945-->
?
The **MLP** transforms the vector of each position with projections and non-linearity, while the attention exchanges information between positions. "Independently" means that the same transformation applies to each position, whose vector already contains context.

MLP blocks often represent a large part of the parameters and participate in the storage, but the knowledge does not reside exclusively in these blocks. In many [[136-mixture-of-experts|MoE]], some dense MLPs are replaced by experts selected by a router.

---

What are residual connections and standardization used for? <!--anki:7a416e26656a2b364877-->
?
Residual **connections** add a transformation to its input: `y = x + f(x)`. They provide a direct path for information and gradients, which facilitates deep training without guaranteeing the absence of unstable gradients.

The **normalization** controls the scale of representations, for example with LayerNorm or RMSNorm. Its placement before or after a subblock depends on the architecture. These are two complementary mechanisms: adding the input does not normalize values, and normalizing does not replace the residual connection.

---

How does the model know the position of the tokens? <!--anki:637e3955546a4c492f2d-->
?
Without positional information or mask depending on the position, attention alone does not distinguish the order of the elements in the desired way, so the model receives **positional** information, by embeddings, biases or transformations like RoPE.

**RoPE** applies rotations to queries and keys based on positions; their scalar product then encodes a relative position relation. The causal mask also provides an order structure, but does not replace all of these mechanisms. Extending supported positions does not guarantee proper use of longer contexts.

---

Why is attention expensive on long contexts? <!--anki:76402d59655d2e3c2977-->
?
The calculation of scores is **quadratic** in sequence length (n² pairs) during the **prefill**, and the **KV cache** grows **linearly** with context. FlashAttention reduces the cost **memory** and HBM accesses, not complexity ([[62-inference-optimizations|optimisations]]).

With dense **attention**, doubling the length approximately quadruples the work of the prefill's fixed-architecture attention pairs. This does not necessarily quadruple the total time, which includes other operations. During the decode, each new token consults the already stored context: the cost per step increases with its length.

---

Calculation: what gross storage for the weights of 70 billion parameters in BF16, FP8 and INT4, in decimal GB, then what additional costs should be expected? <!--anki:623b687d595d6121635b-->
?
**Number of × bytes per parameter**:
```text
70B to BF16 (2 bytes) ≈ 140 GB → two H100 80 GB at least
70B to FP8 (1 byte) ≈ 70 GB
70B to INT4 (~0.5 byte) ≈ 35-40 GB
```
It is necessary to add the **KV cache** and activations, often several tens of GB more in serving ([[68-quantization|quantization]], [[61-kv-cache-attention|KV cache]]).

The values are in **Gbdecimal** and are a budget for weights, not for the whole service. Quantification, scales and metadata add an extra cost. Two 80Gb cards are a minimum for this class of GPU and a compatible split; context and concurrency may impose more memory.

---

Do not confuse: decode-only, encode-only and encode-decoder? <!--anki:42425b217d782c423c4b-->
?
- **Decoder-only** (GPT, Llama, Claude): Causal attention, **generation** — standard LLM.
- **Encode-only** (BERT): Attention **bidirectional**, no — generation used for **classification**, **embeddings** and **rerankers**.
- **Encode-decoder** (T5): an encoder reads the input, a decoder generates — translation, summary.

The encoder produces representations that use both sides of the text; the causal decoder predicts a sequence without seeing the future tokens. In an encoder-decoder, the generation consults the representations of the input. "No generation" describes here the usual use of BERT as an encoder; it can nevertheless predict hidden tokens.

---

Why is a basic model not necessarily a good assistant? <!--anki:656e4e215b5455584f68-->
?
A **basic model** mainly learns to predict the sequence of texts; following an instruction is not always the explicit objective of this training. It can nevertheless respond to certain instructions thanks to the patterns learned.

**post-training**, including supervised training on exchanges and sometimes preferences, aims at a more adapted assistant behavior. Use the expected template and compare base and instruct on the task. Post-training can modify abilities and knowledge too: the separation "pre-training = knowledge, adaptation = behavior" is a benchmark, not an absolute border.

---

Calculation: A head of attention assigns weights 0.25 and 0.75 the V1 values = (2, 0) and V2 = (0, 4). What is its output before projection? <!--anki:6439356533656637316461373462393262346139653361386536616264316532-->
?
This is the **weighted sum** of the value vectors:
```text
0,25 × (2, 0) + 0,75 × (0, 4) = (0,5, 3)
```
The head therefore combines the two values; it does not only return V2 because its weight is the highest. These weights indicate the contribution to this combination, not a probability that each source is true. In a multi-head block, the outputs of the heads are then concatenated and projected; the statement stops before this projection.

---

Calculation: with identical context, layers, head size and accuracy, switching from 32 KV heads to 8 with GQA changes the memory of the KV cache by what factor? <!--anki:6164363761336462383365643431336262376439343561306239663130616464-->
?
The memory of the KV is **proportional to the number of KV** heads:
```text
new KV / old KV = 8 / 32 = 1/4
```
This is a division by four, a reduction of 75%, excluding additional costs. The number of query heads Q can remain at 32: four Q heads then share a K/V pair. This does not divide all the weights or the total latency by four. GQA is a property of the trained architecture; this number is not arbitrarily replaced when the server is launched.

---

Do not confuse: training parallelism and sequential dependence in autoregressive generation? <!--anki:3330303732316462376330383435636438323934343564646636666464316237-->
?
In training with **teacher forcing**, the reference tokens are already known. The model can calculate predictions of several parallel positions in a layer, while masking future positions: each target is predicted from the allowed prefix.

In classical autoregressive generation, the next token depends on the token actually chosen in the previous step, still unknown before its calculation. The KV cache avoids recalculating past states, but does not remove this dependency. The prefill of the known prompt remains parallelizable; several requests can also progress together.

---

Why are attention weights not automatically a true explanation of a LLM response? <!--anki:3566613130323866333934323435636438363664613433656433386232306363-->
?
The **Attention** is an internal calculation among several layers, heads and transformations. A high weight indicates a contribution to this local operation, No proof that the token is the sufficient cause of the final answer.

Distinguish between internal visualization and verified explanation. Test input interventions and compare behavior, not to mention that a change can change several factors at once. To justify a business response, provide verifiable external evidence. A convincing heat map does not validate either accuracy or causality.

---

Why does not subtract the maximum of logits before a softmax change the probabilities? <!--anki:6635363938373665386132623436626339363864326162303565313565643638-->
?
Multiplying all exponential terms by **the same factor** does not change their ratio. For a constant c, `exp(z_i-c) / Σexp(z_j-c)` equals the initial softmax.

Choosing c equals the maximum limits numerical exceedances. This transformation stabilizes the calculation; it does not modify the temperature or the relative preference between tokens. It also does not correct already unfinished logs.

---

Why should the causal mask be applied before normalization of attention scores? <!--anki:3238356361643932613437343431336639353136656466626562353063613736-->
?
Prohibited positions must be given **zero probability in the normalized distribution**. Hide them after softmax without renormalizing would leave a sum of less than one.

In practice, the calculation excludes these positions from normalization, often via a value assimilated to minus infinity. Check the conventions of the kernel. A mask error during training can leak the future tokens and produce an artificially low loss.

---

## Scenarios

Scenario: you are asked how many GPUs to plan to serve a 70B model with 16,000 tokens context and 50 concurrent users. How do you reason out loud? <!--anki:4c256b2c707933653264-->
?
1. **Weights first**: 70 billion parameters × 2 bytes in BF16 ≈ **140 GB**, so two GPU of 80 GB leave almost nothing
2. **The KV then hides**: proportional to the context, the number of layers and heads KV, and the **number of simultaneous requests** ([[61-kv-cache-attention|KV cache]])
3. **Study the levers**: quantification of weights and cache if supported; count real KV heads, especially with GQA
4. **Check by measurement**: a load benchmark, not just a calculation ([[64-inference-metrics-slo|SLO]])
5. **Announce a range** and the assumptions behind it

**Trap**: only size on weights, forgetting the cache, which decides the concurrency.

---

Scenario: In conversation, You’re asked why a basic model doesn’t answer questions when it has “read the whole internet.” What do you say? <!--anki:433e282a5721372b5575-->
?
1. **Training goal**: learns to **continue text**, not answer. It can extend a question with other questions
2. **What creates the assistant**: post-training, first supervised, then by preferences ([[52-post-training-alignment|post-training]])
3. **Practical consequence**: a "base" model on Hugging Face is not used as an "instruct" model
4. **Chat template**: educated models expect a precise format, without which the quality drops ([[132-tokenization|chat template]])
5. **Nuance**: different objectives, without strict boundaries; post-training can also modify knowledge and abilities

**Trap**: To conclude that a model is bad when using a basic variant or a bad conversation template.

---

## Sources

- [Vaswani et al. — architecture Transformer](https://arxiv.org/abs/1706.03762)
- [Ainslie et al. — GQA](https://arxiv.org/abs/2305.13245)
- [Su et al. — RoFormer and RoPE](https://arxiv.org/abs/2104.09864)

- Supplement of the 14 November 2026 — Attention and causal mask: [Vaswani et al. — Attention Is All You Need](https://arxiv.org/abs/1706.03762).

## Connections
- [[132-tokenization|Tokenisation]] — model input
- [[135-pretraining-scaling-laws|Pre-workout & scaling laws]] — how to train
- [[136-mixture-of-experts|Mixture of Experts]] — replace MLP with experts
- [[137-long-context|Long context]] — RoPE and its extensions
- [[61-kv-cache-attention|KV cache & attention]] — attention to inference
- [[65-probabilities-sampling|Probability & sampling]] — logs to token
- [[133-embeddings-representations|Embeddings]] — represent meaning by vectors
- [[161-vision-language-models|Vision-language models]] — input images and screens
- [[22-advanced-rag|RAG — Advanced]] — hybrid search, reranking and filters
- [[60-013-prefill-decode-step-by-step|Prefill & decode step by step]] — apply projections and causal mask to an actual query
- [[00-moc-ai-engineering|MOC AI Engineering]]
