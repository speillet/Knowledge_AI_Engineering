# Fine-tuning & adaptation of models — Flashcards
Tags: #flashcards #ai-engineering #fine-tuning #llm
<!-- summary: when to adapt, SFT, PEFT, LoRA and QLoRA, resources, distillation, multi-LoRA, regressions, rank and damping calculation, versions of an adaptor, teacher forcing and free generation, supervision masking, fusion LoRA. -->


What is the fine-tuning? <!--anki:71447a6c7b502c78475d-->
?
**Continue training a pre-trained model** to adapt its outputs to a goal: behavior, format, task or domain. The SFT on annotated examples and PEFT methods like LoRA are common options.

The volume required depends on the diversity of the cases and the initial level; a few hundred examples do not constitute a universal recipe. Adaptation can learn from knowledge, but their restitution, updating and deletion are not guaranteed. For changing facts to cite, compare first a search to execution like the [[21-rag-fundamentals|RAG]].

---

When do you tune rather than prompt or do RAG? <!--anki:6758606d3f2a7e395547-->
?
When a repeated adaptation of the **behaviour or task** brings measurable gain: specialized extraction, expected style, distillation or reduction of the required context.

Compare the [[11-advanced-prompt-engineering|prompt]] with examples and the [[21-rag-fundamentals|RAG]] if the difficulty comes from the access to the facts. Verify that a representative and authorized game exists, with an independent test. Measure gains, rare cases and regressions. For frequently updated knowledge, the search generally facilitates updating and traceability; this does not make the methods mutually exclusive.

---

What is SFT? <!--anki:6759363b4a296776615b-->
?
**Supervised Fine-Tuning**: Training on quality pairs **→ expected response**. The format must be **exactly that of the inference**, including chat template and tools ([[132-tokenization|chat template]]).
```jsonl
{"messages": [
  {"role": "system", "content": "Extract invoice fields as JSON."},
  {"role": "user", "content": "Invoice n°A-4471 of the 12/03: 1,240, 50 € TTC..."},
  {"role": "assistant", "content": "{\"numero\":\"A-4471\",\"total\":1240.50}"}
]}
```
In training **assistant-only**, we hide the loss on the instructions to learn the answers. This masking depends on the collator and the configuration: check it, because some pipelines drive on the whole sequence.

Inspect a tokenized example with its labels: ignored positions should not contribute to the loss, while the response and its termination should remain learned. A loss that drops does not prove that the mask is correct.

---

Do not confuse: full fine-tuning and PEFT? <!--anki:666d6d6977395a684642-->
?
The **full fine-tuning** updates all weights; the **PEFT** causes a subset or added parameters, such as LoRA matrices, by freezing most of the base.

Example: sharing a base between three business adaptations avoids storing three complete copies of the driven weights. However, each adaptation must find **the correct basic review**, the targeted modules and the compatible tokenizer; it is not autonomous.

PEFT mainly reduces gradients and driveable optimizer states, not all memory: basics and activations are still required. Compare quality and resources on the task; fewer trained parameters do not guarantee the same result.

---

What is LoRA? <!--anki:634632767854463b7c5a-->
?
**LoRA** freezes a `W` weight matrix and learns a `ΔW = B × A` low-rank correction. For a `d × k` matrix, this results in about `r × (d + k)` parameters instead of `d × k`, with a much smaller `r` rank than the dimensions.

Adapting it reduces training memory and variant storage, but its size depends on the rank and targeted layers: it can exceed a few tens of MB. It takes the right version of the basic model to use.

---

What is QLoRA? <!--anki:435021656c75503d585b-->
?
**LoRA on a quantized model in 4-bit**: fine tune a large model on a modest GPU. The basic weights remain fixed in 4 bits (NF4 format), only the adaptors train in higher precision ([[68-quantization|NF4]]).

During the calculation, the quantified weights are exploited with a suitable calculation accuracy; "4 bits" describes their storage, not all operations. It still requires memory for the activations, the adaptors and their optimizer. The gain makes some training possible, without guaranteeing that a long context or a large batch fits on the same GPU.

---

Which assumptions depend on the resources required for a fine-tuning? <!--anki:457b75296778564c6056-->
?
Resources depend on **model, sequence length, batch, optimizer, and appropriate layers**.
```text
Full FT: weight + gradients + optimizer states + activations
LoRA: frozen weight + small parameters trained + activations
QLoRA: quantified base + trained adaptors + activations
```
As an estimate, a 7B with a budget of 16 bytes per parameter requests **112 GB excluding activations**. QLoRA configurations make large models accessible on a GPU, without guaranteeing that a 70B holds with any context. Measuring maximum memory and time on a small representative drive; the quality of the examples remains decisive.

---

How to get a small model as good as a large on a specific domain? <!--anki:4a2c42346174694d706b-->
?
**Distillation** uses a large model as a teacher to produce examples, distributions, or supervision signals for a smaller model. On a narrow task, the student can approach the useful quality of the teacher with a less expensive inference.

This result is not guaranteed: select various examples, check the teacher's outputs and test out of the training set. Measure difficult cases and general regressions; the teacher's errors can be transmitted to the student ([[53-synthetic-data-distillation|Distillation in detail]]).

---

How to serve several fine tunings at a lower cost? <!--anki:483c356d3755387d6c25-->
?
The **multi-LoRA** shares a base model between several adapters, selected according to the request. This avoids duplicating all the weights for each adaptation.
```bash
vllm serve meta-llama/Llama-3.1-8B-Instruct --enable-lora \
  --lora-modules support=./lora-support legal=./lora-legal
```
This example assumes a compatible server and architecture. Check basic versions, targeted ranks and modules, then measure memory, adapter loads and throughput under concurrency. The number of clients is not enough to size the GPU: simultaneous adapters, active sequences and KV cache also count.

The identity of the client must determine the authorized adaptors. A legal adaptor is not a border of confidentiality and must not be freely selectable by another tenant.

---

What is the main risk of fine-tuning? <!--anki:4a72233936695944475e-->
?
A major risk is the **regression of useful abilities** during the specialization: followed by instructions, other languages or general tasks. A biased game can also learn errors without the loss revealing it.

Freezing the database with **LoRA** does not guarantee the absence of regression when adapting it is active. Comparing the database and adaptation on the target task and the capabilities to be preserved; selecting learning rate, duration and possible mixing of data according to these measures. Removing the adaptation allows to find the database, but does not correct the behavior of the specialized version.

---

Calculation: for a 7B base, compare the raw weight memory in LoRA with BF16 and in QLoRA with 4 bits. Why don't these numbers give the total memory of the fine-tuning? <!--anki:3337376463643866363135623439663561633937613466613932353937653533-->
?
**Basic weight memory** provides only a starting point, in decimal GB:
```text
LoRA, base BF16 : 7e9 × 2 bytes = 14 GB
QLoRA, storage brut 4 bits : 7e9 × 0,5 byte = 3,5 GB
```
Add quantization metadata, adapters, gradients, and associated optimizer states, activations, and temporary buffers. Their cost depends on rank, targeted layers, accuracy, batch, and sequences. A GPU of 16 or 24 GB may be suitable for certain QLoRA 7B recipes, without general warranty.

---

Calculation: LoRA adapts a matrix of 4,096 × 4,096 with a 16 rank, without bias or other induced parameters. How many parameters are learned and what fraction of the complete matrix does this represent? <!--anki:6362383461646433373665393461356362623838643937616435383465623236-->
?
Both correction matrices contain `r × (d + k)` parameters:
```text
LoRA : 16 × (4 096 + 4 096) = 131 072
complete matrix: 4,096² = 16,777,216
fraction : 131 072 / 16 777 216 = 0,0078125 ≈ 0,78 %
```
This reduction relates to the parameters driven from **this matrix**. It does not divide all the memory or the calculation time by the same factor: base, activations and other modules remain present. The rank is a choice to validate on the task.

Adapting multiple projections in multiple layers multiplies the LoRA total. Counting the matrices actually targeted and any additional driven modules; the percentage of a single matrix does not automatically describe the entire model.

---

What does it take to faithfully redeploy a LoRA adapter? <!--anki:3161663637373437313135313434343738373861323137353861636533393538-->
?
The exact **review of the database**, the weights and configuration to adapt it, the tokenizer, the conversation template and the settings of serving.

The rank and target modules must match the loaded architecture. A model name alone is not enough if its files have changed. Also keep data references and eval results to understand the adaptation. Test the load and some cases of non-regression in the target environment; an adaptor is a system component, not a stand-alone model.

---

Calculation: an adaptation costs 1,200 € initially and saves 0.004 € per request of comparable quality, with no additional recurring cost. At 50,000 requests per month, what volume and delay amortize this investment? <!--anki:6539343261343363333263323438643339643432396335363361366535306637-->
?
With the fictitious costs and assumptions of the front:
```text
damping volume = 1,200 / 0.004 = 300,000 requests
Monthly Savings = 50,000 × 0.004 = 200 €
lead time = 1,200 / 200 = 6 months
```
This calculation is only valid if quality, volume and economy remain comparable. Add re-drives, validation, operation and regressions to the actual scenario. If the monthly gains do not exceed the recurring costs, there is no finite amortization time in this model.

At 25,000 monthly queries, the same investment would take twelve months, all things equal. This sensitivity to volume helps decide whether to adapt now or wait for a more stable demand.

---

Why doesn't a small teacher forcing loss replace free generation evaluation after SFT? <!--anki:3731356531646565346666643466623661633664633865663533633131653436-->
?
In **teacher forcing**, each prediction receives the previous tokens of the reference response. In free generation, the model continues from its own outputs, including their errors.

A small gap can therefore change the entire suite, tool calls or termination. Evaluate complete answers with the format and budgets of the serving, and then measure business success and errors by segment. Keep the loss as a learning diagnosis, without assimilating it to the rate of successful tasks. The comparison must use examples independent of the training.

---

Why hide user tokens in some fine-tuning conversations? <!--anki:3265383336656438663736333438666262646666363563636532386139636133-->
?
If the goal is to learn **helper answers**, calculating the loss on all tokens also results in the reproduction of the questions and documents provided. This changes the purpose and relative weight of the long examples.

Check the mask actually produced by the template and collator, including tool calls. Masking does not remove tokens from the context; it removes their direct contribution to the loss.

---

Why not merge a LoRA adapter into the weights? <!--anki:3436376631646333626161383437373462346531323039396136333035306266-->
?
Merger materializes **W + ΔW** in a given representation. Rounded, quantized, scaled or bad base can make the model served different from the one evaluated with separate fit.

Verify database identity, merge parameters and tokenizer, then compare outputs and metrics after export. Merging can simplify the serving of a single adapter, but removes the flexibility to switch between multiple adapters on a shared basis.

---

## Scenarios

Scenario: the trade wants to fine tune a model "so that he knows our internal procedures", which change every month. What do you answer? <!--anki:6e332d72382e3d3f492e-->
?
1. **Separate knowledge and behavior**: procedures that change fall under **RAG**, not fine-tuning ([[21-rag-fundamentals|RAG]])
2. **Recall cycle cost**: each update would require a new training, new evals and redeployment
3. **What the fine-tuning would really bring**: a constant response format, a tone, a repetitive task, shorter prompts
4. **Propose an intermediate step**: prompt care plus RAG, measured on a golden dataset
5. **Keep the door open**: if the format remains unstable after optimization, a light fine-tuning (LoRA) is justified

**Trap**: fine tune on internal documents and believe that the model “will” quote them correctly.

---

Scenario: your fine-tuned model is excellent on the intended extraction, but users report that it answers anything to the general questions. What happened? <!--anki:6961533e313a76446060-->
?
1. **Reproduce errors** on the same cases with the appropriate base and version.
2. **Check the string**: tokenizer, template, build configuration and adapt loaded.
3. **Measuring off-task regressions** and data biases, before concluding that abilities are being forgotten.
4. **Compare less aggressive** adaptations and a mix of general data; LoRA alone does not guarantee anything.
5. **Limit the perimeter** or route to a validated base, then re-evaluate the whole.

**Trap**: Attribute any regression to training without checking the model actually served.

---

## Sources

- [vLLM — multi-LoRA serving and configuration constraints](https://docs.vllm.ai/en/stable/features/lora/)

- [Hu et al. — LoRA and low-rank settings](https://arxiv.org/abs/2106.09685)
- [Hugging Face TRL — masking, truncation and SFT](https://huggingface.co/docs/trl/sft_trainer)
- [Hugging Face PEFT — configuration and loading LoRA](https://huggingface.co/docs/peft/package_reference/lora)

- 14 November 2026 — Masking supervised tokens: [Hugging Face TRL — SFT Trainer](https://huggingface.co/docs/trl/sft_trainer).

## Connections
- [[21-rag-fundamentals|RAG]] — knowledge vs behavior
- [[11-advanced-prompt-engineering|Prompt engineering]] — light alternative
- [[11-llm-inference-servers|Inference Servers]] — multi-LoRA serving
- [[62-inference-optimizations|Optimizations]] — quantization (QLoRA)
- [[92-chainforge-evals-prompts|Evals]] — measure before/after
- [[113-monitoring-drift-feedback|Monitoring & drift]] — when retraining
- [[68-quantization|Quantization]] — NF4 and serving formats
- [[52-post-training-alignment|Post-training & Alignment]] — RLHF, DPO, GRPO in detail
- [[53-synthetic-data-distillation|Synthetic Data & Distillation]] — generate and distill
- [[54-distributed-training|Distributed training]] — FSDP, ZeRO, parallelism
- [[111-mlops-llmops-fundamentals|MLOps & LLMOps]] — life cycle and versioning of LLM systems
- [[114-reproducibility-variance|Reproducibility & variance]] — non-determinism and eval statistics
- [[151-data-curation-annotation|Curation & annotation]] — quality data and separate games
- [[55-agentic-rl|Agentic RL]] — train a model on agent tasks
- [[66-prefix-caching-radix-attention|Prefix caching]] — Reuse the calculation of common prefixes
- [[56-training-optimization-diagnostics|Training Optimization & Diagnosis]] — diagnose an adaptation before making it more complex
- [[60-014-inference-parity-validation|Inference parity]] — teacher forcing to compare two inference stacks
- [[00-moc-ai-engineering|MOC AI Engineering]]
