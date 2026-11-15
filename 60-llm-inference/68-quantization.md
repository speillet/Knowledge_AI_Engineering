# Quantization — Flashcards
Tags: #flashcards #ai-engineering #inference #quantization #llm
Verified on: 25 September 2026 — This factsheet lists products, versions or regulatory texts that are evolving quickly.
<!-- summary: Calibration and speed, quantization of weights, activations or KV cache, formats (FP8, INT8, INT4, NVFP4, MXFP4), weight-only or W8A8, granularity of scales, outliers of activation (SmoothQuant, rotations), PTQ or QAT, GPTQ, AWQ, GGUF, NF4. -->


What is the quantization of a LLM? <!--anki:723d7149494058234777-->
?
Represent model numbers with **fewer bits**: each value is plotted on a small grid, with a **scale factor** to find the original order of magnitude.
```text
x ≈ scale × (q − z) q on 8 or 4 bits (integer or small floating)
                         z = zero-point, zero in symmetric quantization
```
We can quantify the **weight**, the **activations** and the [[61-kv-cache-attention|KV cache]].

Example in symmetric INT8: if the largest weight of a group is 0.8, scale = 0.8 / 127 ≈ 0.0063. The weight 0.5 becomes q = round(0.5 / 0.0063) = 79, Reread 79 × 0.0063 ≈ 0.498. The error is limited by a half-step; but one extreme value expands the walk for the whole group, Hence the importance of granularity.

---

Why quantify a LLM? <!--anki:703678237b5b54653950-->
?
Reduce the footprint of **weights**, **activations**, or **KV cache**, depending on the method. Less bulky weights can free up KV, reduce memory readings, and allow less GPU per instance.
```text
70 billion values: BF16 ≈ 140 GB; 8 bits ≈ 70 GB; 4 bits ≈ 35 GB
```
Add scales, metadata, and tensors retained in higher accuracy. Speed gain depends on kernels and load: dequantization or conversions can cancel it. Measure quality per task, peak memory, latency, and cost per success before retaining the variant.

---

What digital formats do we encounter in quantization of LLM? <!--anki:4b245f5862716c2a7e75-->
?
- **BF16/FP16**: 16 bit formats, often used as references; they also round up the values.
- **FP8**: formats like E4M3 and E5M2, with range/precision compromise.
- **INT8**: Quantified integer values, with scales adapted to tensors.
- **INT4**: current for weights only, with calculation often in a higher precision.
- **FP4**: block formats and schemas like MXFP4 and NVFP4.

The format name does not guarantee kernel support, accumulation accuracy, or quality. Check the model, hardware, engine, and method combination.

---

What is quantization granularity? <!--anki:715b716529555e2f695a-->
?
The number of values that **share the same scale factor**:
- **Per tensor**: a scale for the whole matrix, simple but sensitive to extreme values
- **Per channel**: one scale per row or per column
- **Per group or per block**: one scale every **16 to 128 weight** (e.g. groups of 128 in INT4, blocks of 16 in NVFP4)

The more it ends, More is **Precise**, but the scales occupy space: one INT4 per group of 128 Actually costs **≈ 4.1 TB 4.25 bits by weight**.

---

Why are activations more difficult to quantify than weights? <!--anki:4b4355607366724d7b2a-->
?
Because of the **outliers**: in the LLM, some **activation channels** take values **much larger** than the others. A common scale then overwrites all small values.
- **SmoothQuant**: transfer the difficulty of activations to weights, by a mathematically equivalent channel scaling
- **Rotations** (QuaRot, SpinQuant): multiply by an orthogonal matrix (Hadamard) that **spreads outliers** on all channels
- Keep these channels in **higher accuracy** (LLM.int8())

---

PTQ or QAT? <!--anki:4d4276533f3f3c26692e-->
?
- **PTQ** (post-training quantization): we quantify a model **already trained**, without data or with a small set of **calibration**. Fast (a few minutes to a few hours): GPTQ and AWQ are methods of PTQ; FP8 is a format usable in different schemes
- **QAT** (quantization-aware training): we **Simulate quantization during training** so that the model adapts to it. More expensive, but can better preserve the quality at very low precisions

Models are now **published quantized natively**, by QAT or post-training in low precision: gpt-oss (MXFP4), Kimi K2 Thinking (INT4).

---

How does GPTQ work? <!--anki:4f366a575e4973377544-->
?
A **Post-workout quantification of weights**, layer by layer, which seeks to preserve the outputs on calibration activations. It gradually quantizes columns and adjusts the remaining weights using a second-order approximation.

Example: Rounding a weight creates an error; GPTQ tries to compensate for some of it with unquantified weights, rather than rounding each weight independently.

Number of bits and size of groups are settings, not universal constants. A limited calibration of dialogues may not preserve the code. Evaluate tasks held apart and check the target kernel: a smaller file is not automatically faster.

---

How does AWQ work? <!--anki:6f356c62755260316047-->
?
**AWQ** uses the activation statistics of a calibration corpus to identify channels whose quantization errors strongly affect the outputs. A resizing of the channels, compensated on the activations, reduces the error when quantifying weights.

The idea is not to systematically keep 1% weights in full precision: the benchmark comes from the observations of the article, not from a universal rule. The search for scales is done without retraining the model by backpropagation. Check corpus, product format and kernels compatible, then measure quality by segment and speed; the name AWQ does not guarantee any fixed gain or absence of regression.

---

When is FP8 a good candidate for production inference? <!--anki:505f6a2158383c2f3164-->
?
FP8 is a **candidate** when hardware and kernels support it effectively: values take up less memory than in BF16 and some operations can be accelerated.

This is not a universal flaw. Checking scale scheme, checkpoint, possible calibration, attention and runtime compatibility. Quantifying weights does not automatically enable quantization of the KV cache, which adjusts and evaluates separately. Compare to a baseline on critical tasks, and then measure goodput and peak memory; a small average loss may hide a significant regression on a segment.

---

What are NVFP4 and MXFP4? <!--anki:6d213f642a5d7670466f-->
?
Two formats **floating 4 bits** (E2M1) with **scales in small blocks**, natively executed by the GPU **Blackwell** (≈ 2 times the throughput of the FP8):
- **MXFP4** (OCP standard): blocks of **32** values, power scale of two.
- **NVFP4** (NVIDIA): blocks of **16** values, scale FP8 plus one global scale per tensor, so **more accurate** than MXFP4

They target the **W4A4**, weights and activations in 4 bits, where the classic INT4 is limited to weights.

---

What is the llama.cpp GGUF quantization? <!--anki:4279436741614c7e3e4f-->
?
The [[10-images-models-weights|llama.cpp and Ollama]] format offers levels named after their number of bits:
- **Q8_0**: almost without loss
- **Q5_K_M, Q4_K_M**: the current compromise (Q4_K_M ≈ 4.8 bits per weight)
- **IQ2, IQ3**: highly compressed, with a clear loss in quality

The **K-quants** keep some tensors in higher precision, and a **matrix importance** (imatrix), calculated on calibration data, improves the low levels. GGUF targets the **CPU, the Mac and the local**, not the serving with high concurrency.

---

What is NF4 and when to use it? <!--anki:79393c4d63614f3a6148-->
?
**NormalFloat 4 bits**, used by **bitsandbytes**, places its 16 levels to efficiently represent approximately normal weights. **QLoRA** retains the quantified base and causes adaptors ([[51-fine-tuning-adaptation|fine-tuning]]).

Four bits describe the storage, not necessarily the dtype of the multiplications: the weights are dequantized for the calculation. Add memory scales, activations and adapt to the budget. For the serving, compare to the formats supported by the target hardware kernels, including FP8, AWQ or GPTQ; no format is always the fastest.

---

Which quantization method to choose according to the context? <!--anki:66505d4d5421646f257b-->
?
- **GPU Hopper or Blackwell in production**: **FP8** (W8A8) to be evaluated; **NVFP4** on Blackwell if the evals hold
- **GPU Ampere (A100) or consumer, tight memory**: **INT4 weight-only** (AWQ or GPTQ, with Marlin cores); **INT8 W8A8** (SmoothQuant) for throughput
- **CPU, Mac, Local Post** : **GGUF from Q4_K_M to Q8_0**, or MLX on Apple Silicon
- **Fine tuning on a small GPU**: **NF4** with QLoRA
- **Model published already quantized** (QAT): keep its **native format**

---

What is usually kept in high precision? <!--anki:652a504b395d47797b63-->
?
Small but sensitive components: **embeddings**, **lm_head** (the output layer), **normalization**, the **MoE router**, and often attention. Quantize **linear layers** first, especially **MoE experts**, which account for most weights.

These components are not always small. For an 8B model with a 128,000-token vocabulary and dimension 4,096, embeddings and lm_head contain approximately 2 × 128,000 × 4,096 ≈ 1 billion parameters, or 13% of the model. Keeping them in BF16 therefore consumes substantial memory for a small model. lm_head is sensitive because its errors shift the logits of every generated token.

---

Why does the calibration dataset count? <!--anki:486856647e3f6424266b-->
?
GPTQ, AWQ, SmoothQuant or the static FP8 set their scales from **a few hundred examples**. If they do not look like real traffic (other language, code, long context, chat format), the quality drops **specifically on this traffic**. It takes examples **representatives of the domain**, formatted with the **chat template** of the model.

Separate calibration and final test. Include rare but important languages and lengths, then measure their errors individually: a stable average can hide a strong degradation of code or numbers.

---

How to measure the quality loss of a quantized model? <!--anki:64773d654d3b283f5942-->
?
Compare to the **reference variant** on a separate business set of calibration data, with matched evaluations. Measure format, accuracy, tools, languages, reasoning and long contexts by segment.

Defining acceptable loss in advance and reporting uncertainty; similar perplexity or a stable overall score is not enough. Also observe wrong answers, corrections and length changes. There is no universal loss from "1 to 3%" in INT4, nor is there a guarantee of near-equivalence in FP8: model, data and kernels determine the result.

---

Which metrics directly compare a quantized model to its BF16 version? <!--anki:782d547b304c23294b65-->
?
We run the two models on the same **texts** and compare their outputs token by token:
- **Medium divergence KL** between the two probability distributions (0 = identical): the most sensitive measurement
- **Top-1 Agreement**: Share of positions where both models choose the same token
- **Δ perplexity**: the perplexity gap, useful but coarse
- **Flips**: eval responses that go from right to wrong (or vice versa), while the overall score may remain the same

llama.cpp calculates the KL divergence and the top-1 agreement with `llama-perplexity --kl-divergence`.

---

How do I validate a quantized model before deploying it? <!--anki:4e602c2f2d606e6e4977-->
?
With a **eval gate**, comparing to the BF16 model ([[112-model-cicd|CI/CD models]]):
1. **Business assessments** question by question, with a threshold set in advance (e.g. ≥ 99% of the BF16 score on each critical task)
2. **Format tests**: validity of JSON and tool calls, long context
3. **Benchmark load** on target hardware: is the gain in TPOT, throughput or number of GPU real?
4. **Canary or shadow** on real traffic before full toggle

---

What to watch in production after quantization? <!--anki:48663f2b752d297e6f7d-->
?
- **Performance**, to confirm the gain: TPOT, TTFT, throughput, KV cache occupancy and concurrency reached
- **Quality**, to identify a loss that the evals have not seen: validation failure rate (JSON, tools), `finish_reason=length` rate (loops), refusal rate, response length, feedback and scores LLM-as-judge **per segment** (language, task)

Each metric is labeled with the **model variant** to compare to the BF16 version ([[93-monitoring-inference|monitoring of inference]]).

---

With equal memory, is it better a large quantized model or a small model in full precision? <!--anki:78244434472d6f667748-->
?
Compare the two options **on the task and under the same service constraint**. A larger quantified model can respond better, but sometimes retains more computation, KV or communication; it may lose its advantage in latency or concurrency.

A small recent or specialized model may be preferable. Measure quality by segment, length of responses, peak memory, goodput and cost per successful task. The number of bits and parameters alone does not allow to designate the winner. Include a common reference and a reproducible load protocol.

---

With which tool to produce a quantitative checkpoint for vLLM, for TensorRT-LLM or for llama.cpp? <!--anki:3433393265393632646633333430666638643537616161333766356464343137-->
?
- **vLLM or SGLang**: **llm-compressor** (vLLM project: GPTQ, AWQ, SmoothQuant, FP8, NVFP4, in *compressed-tensors* format)
- **TensorRT-LLM**: **NVIDIA Model Optimizer** (FP8, NVFP4, INT4 AWQ), whose checkpoints are also used for vLLM and SGLang
- **llama.cpp and Ollama**: `llama-quantize` to GGUF
- **Often nothing to do**: already quantized checkpoints exist on Hugging Face (`-FP8`, `-AWQ`, `-GPTQ-Int4`, `-GGUF`)

Other: GPTQModel, bitsandbytes. AutoAWQ and AutoGPTQ are no longer maintained.

---

How to serve a quantized checkpoint with vLLM? <!--anki:3836366337646562333134363438346162663163383366663563393835353332-->
?
vLLM **reads the method in the checkpoint configuration**, and also knows how to quantize in FP8 **on the fly** ([[11-llm-inference-servers|Inference Servers]]):
```bash
vllm serve org/model-AWQ                     # Automatically detected method
vllm serve org/model --quantization fp8 \
           --kv-cache-dtype fp8               # FP8 weight on the fly + KV FP8 cache
```

Check compatibility between checkpoint, GPU and kernels before launch. The FP8 on the fly may require loading a larger base at startup; holding after conversion does not guarantee to pass this peak. Evaluate separately the quality of quantified weights and cache KV and then measure the gain under load.

---

Do not confuse: Quantification of weights, activations and cache KV? <!--anki:472f61333a5d544d7225-->
?
- **Weight** (W4A16, W8): Reduces **model memory** and can speed up **decode** memory-bound
- **Activations** (W8A8, FP8): allows low-precision calculations on dedicated units, and can also accelerate the **prefill** compute-bound
- **KV cache** (FP8): reduces the memory **per request**, therefore increases the **concurrency** and the servable context length ([[61-kv-cache-attention|KV cache]])

Three independent settings, to be validated separately: no schema name guarantees acceleration without hardware-specific kernels ([[69-roofline-prefill-decode|roofline]]).

---

Why should a quantization calibration cover difficult entries rather than just a sample of short texts? <!--anki:3735386235616339656430373466393838633835336137626335636231623064-->
?
The **distribution of activations** depends on languages, lengths, structures and tasks. A calibration limited to short texts may not represent the extreme values encountered in code or long documents.

Choose a separate corpus from the final test, covering production segments and sensitive cases. Comparing quality and errors by segment before and after quantization, with the same protocol. Versioning corpus and calibration parameters. A good overall score may hide a degradation on rare amounts or minority languages; increasing the corpus without diversifying its cases may not correct anything.

---

Calculation: a group of 128 weight uses 4 bits per weight and an FP16 scale of 2 bytes, without zero-point or padding. What average cost in bits per weight? <!--anki:6662386633313363343637303462326439316630633734343037393665663939-->
?
Weights occupy **64 bytes**, the 2 scale, or 66 bytes. The average cost is **66 × 8 / 128 = 4.125 bits per weight**.

Actual storage can still include index, alignment, zero-points, and unquantized layers, so announcing "4 bits" often describes the main representation, not the total size of the checkpoint or the runtime memory.

---

Why monitor the saturation of activations after quantization? <!--anki:3438646266653833663238333435353562646339366130353134643965343038-->
?
An out-of-range value can be **capped**, which destroys part of the signal. If the actual traffic differs from the calibration, rare activations can saturate more.

Examine distributions and errors by input type, then adjust scales, granularity, or sensitive layer accuracy. A small average error can hide a few critical cases. Comparing final quality and costs: better digital reconstruction alone does not ensure a better business outcome.

---

## Scenarios

Scenario: you must serve a 70B model on GPU A100s of 80 GB, with a budget of two GPU. What quantization do you choose? <!--anki:786c3b6c673a2d742b6b-->
?
1. **Budgeter**: about 140 GB of BF16 weight on 160 GB nominal leave a narrow margin; check reserves, activations and KV by GPU, without declaring this impossible in principle.
2. **Check for kernels**: A100s do not have a native Tensor Core FP8 calculation.
3. **Compare supported candidates**: INT4 weight-only, INT8 or BF16 if the budget is sufficient.
4. **Test the workload**: long prompts, resident context, concurrency and expected deadlines.
5. **Validate quality and goodput** before selecting the format.

**Trap**: Choose a quantization only from file size or a theoretical gain.

---

Scenario: after the changeover to INT4, your global evals only lose 1%, but the support reports false answers in German and on long documents. What do you do? <!--anki:733a714d6e3255376136-->
?
1. **Do not rely on the average**: losses are focused on specific segments
2. **Assess by segment**: language, context length, task type, tool calls
3. **Measure finely**: KL divergence and top-1 agreement against the BF16 model on these cases
4. **Correct**: finer granularity, representative calibration (German, long documents), or transition to FP8
5. **Router**: keep the model unquantized for sensitive segments, time to correct ([[82-routing-llm|routing]])

**Strap**: Calibrate on a generic English corpus for multilingual service.

---

Scenario: your supplier publishes the same model in BF16, FP8 and GGUF Q4_K_M. Three teams ask you which one to take: production GPU, developer position, offline demonstration. What do you answer? <!--anki:4645564758673a5d7750-->
?
1. **Production GPU recent**: **FP8 to evaluate**, with compatible kernels and separate measurement of quality and memory
2. **Developer position**: **GGUF Q4_K_M** with llama.cpp or Ollama, running on CPU or Mac
3. **Offline demonstration**: GGUF too, giving priority to Q5_K_M or Q8_0 if the machine allows it
4. **Reminder** that these variants do not give the same outputs: the evals must be redone by variant
5. **Trace** the variant served in the metrics and traces ([[93-monitoring-inference|monitoring]])

**Trap**: validate the quality on the developer’s job in GGUF, then deploy another variant in production.

---

## Sources

- [vLLM — Quantification and Compatible Hardware](https://docs.vllm.ai/en/latest/features/quantization/)
- [llama.cpp — formats, quantification and local inference](https://github.com/ggml-org/llama.cpp)

- [— AWQ](https://arxiv.org/abs/2306.00978) — targeted review of 12 November 2026: activation statistics and channel resizing.

## Connections
- [[62-inference-optimizations|Inference optimizations]] — prefill, decode and memory bandwidth
- [[61-kv-cache-attention|KV cache & attention]] — Quantify Cache
- [[64-inference-metrics-slo|Metrics & SLO]] — effect on TTFT, TPOT and throughput
- [[10-images-models-weights|Images & weights of models]] — Weight Size, GGUF Format
- [[11-llm-inference-servers|Inference Servers]] — vLLM, TensorRT-LLM, llama.cpp
- [[51-fine-tuning-adaptation|Fine-tuning]] — QLoRA and NF4
- [[121-inference-costs|Inference costs]] — less than GPU per replica
- [[114-reproducibility-variance|Reproducibility & variance]] — compare before and after quantification
- [[67-speculative-decoding|Speculative Decoding]] — the other lever to accelerate the decode
- [[93-monitoring-inference|Monitoring of inference]] — follow quantity model in production
- [[164-local-edge-llm|Local LLM & Edge]] — GGUF and small devices
- [[69-roofline-prefill-decode|Roofline]] — why quantization accelerates the decode
- [[134-vector-search-ann|Vector search]] — index ANN, HNSW and vector quantization
- [[136-mixture-of-experts|Mixture of Experts]] — total and active settings
- [[95-llm-as-judge|LLM-as-a-judge]] — note automatically, and validate the judge
- [[133-embeddings-representations|Embeddings]] — represent meaning by vectors
- [[137-long-context|Long context]] — limits and cost of long windows
- [[60-014-inference-parity-validation|Inference parity]] — the same comparison method for any stack change
- [[00-moc-ai-engineering|MOC AI Engineering]]
