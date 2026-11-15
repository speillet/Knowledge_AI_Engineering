# LLM local, on-prem & edge — Flashcards
Tags: #flashcards #ai-engineering #edge #local #self-hosting #llm
Verified on: 25 September 2026 — This factsheet lists products, versions or regulatory texts that are evolving quickly.
<!-- summary: motivations, capacity or memory bandwidth, llama.cpp and GGUF, local tools, Ollama or vLLM, Apple Silicon, small language models, hybrid local and cloud, fleet of devices, profitability of on-prem, measurement in sustained thermal regime, energy autonomy, offline mode. -->


Why run a LLM locally or on site? <!--anki:68767b39524b69526735-->
?
- **Privacy/sovereignty**: possibility to keep data on site.
- **Off-line** or constrained network (factory, terrain, embedded).
- **Latency** without network round-trip.
- **Potentially low marginal cost** on already paid hardware.
- **Control**: fixed version, no depreciation imposed.

These benefits require controls: disabling or mastering telemetry, remote tools, and downloads. Energy, wear, and occupied capacity remain costs. Testing the network service cut-off: a local model may still depend on authentication or an external search.

---

What is the limiting factor on a workstation or device? <!--anki:67755876354173497641-->
?
The **memory capacity** determines whether weight, KV and allocations hold; the **bandwidth** can then limit the decode, especially at low batch. Calculation, offload and temperature can also become dominant.

Simplified example: a dense occupying model 5 GB of weight and reread entirely by token, with 100 GB/s really available for these readings, has a ceiling related to the weights of **20 tokens/s**. This is not a prediction of measured flow: KV, De-quantification, Kernels and shared memory add costs. A MoE, A batch or multiple levels of memory require a suitable performance model.

---

What is llama.cpp and the GGUF format? <!--anki:647e555f4a2a7a723579-->
?
**llama.cpp** is a portable C/C++ inference engine, with different CPU and GPU backends. **GGUF** describes a weight and metadata container; weights can be quantified or floating precision, and the model can be split into shards.

The tokenizer and the chat template must match the template; check the metadata present. Example: `llama-server -m model.gguf -c 8192 -ngl 99`. `-ngl 99` requests the offload of a number of layers; the result depends on the template, the backend and the memory. Check logs instead of assuming that the entire template runs on GPU.

---

What tool to serve a LLM locally: developer alone, Mac, GUI, team? <!--anki:3462633762323030326236333435653361303765663234343061626430623137-->
?
- **Developer only**: **Ollama** (model management and local API, above llama.cpp), or directly server **llama.cpp**, OpenAI compatible
- **Mac Apple Silicon**: **MLX**, optimized for unified memory
- **Graphic interface**: **LM Studio**
- **Team, concurrent users**: **vLLM** or **SGLang** on an on-prem GPU server ([[11-llm-inference-servers|Inference Servers]])

These choices are starting points, not a universal ranking. Check supported model, structured outputs, concurrency, and deployment conditions; test the actual path before choosing on ease of installation alone.

---

Why are Apple Silicon Macs popular for local LLM? <!--anki:797c71366d393945402f-->
?
The **Unified Memory** Donate to CPU and the GPU access to a common memory space, This can make it easier to load larger models on some Apple Silicon configurations.

The announced memory is not fully available to the model: system, other applications, KV and buffers also consume it. Flow of decode and duration of prefill depend on the model, quantification, backend and hardware compared; no universal hierarchy against GPU servers derives from the brand. Measure a supported workload on the target machine, including temperature and bandwidth sharing.

---

Which models to aim for the edge? <!--anki:79514e2a284664622c76-->
?
Depart from **Material and Task Constraints**, and test small models, possibly quantified or [[53-synthetic-data-distillation|Distilled]]. The beach 1–8 billion parameters is a benchmark, Not a definition of edge.

Example: 3 billion in weight to 4 bits represent about **1.5 GB raw decimals**, plus metadata, activations, runtime and KV cache. This does not guarantee to fit comfortably in 2 GB.

Measure quality, response time, energy and thermal slowdown on the target device. A specialized model can beat a bigger one on its task; fine-tuning and distillation do not automatically compensate for all its limitations.

---

What is a hybrid local/cloud architecture? <!--anki:6c64257577297726536d-->
?
Process **locally** which is simple, frequent or sensitive (PII, classification, pre-filtering), and **climb difficult requests to the cloud**, after **pseudonymization** if necessary. The router decides according to **difficulty**, **sensitivity** and **connectivity** ([[82-routing-llm|routing]]).

Example: A desktop email assistant classifies and summarizes locally with a small model. To write a complex response, it sends text to the cloud where names and addresses are replaced with tokens, and then reinserts the values locally. Provide offline mode: Without a network, the cloud function explicitly degrades instead of failing.

---

What are the challenges of operating a local model fleet? <!--anki:255a2e4b704c7e2b6a-->
?
- **Distribution and update** of models (several GB) on many devices.
- **Heterogeneity** → hardware multiple quantized variants.
- **Observability** limited (no centralized logs by default).
- **Safety**: Weights are **extractable** from the device, and the local model remains exposed to prompt injection.
- **Evals** to be redone for each quantization.

Schedule a progressive update, integrity check, and rollback compatible with local data. Test a device offline during migration; then control which version is actually active, not just which one is downloaded.

---

When does the on-prem GPU become profitable compared to the API? <!--anki:63522c7c41676e3e78-->
?
When the **Use** of the GPU is **High and Regular**, the Open Weights Model **Quality** required, and that the team knows **Exploit**. The calculation must include material, energy, accommodation, Engineers, and the **occupancy rate** Real — a GPU Unoccupied at night costs so much ([[121-inference-costs|break-even API vs self-host]]).

Compare several volume scenarios and a breakdown reserve, not just the theoretical maximum load. Fixed costs continue during inactivity, even if energy decreases. A cheaper local model but often scaled towards a API can cancel the expected savings.

---

Do not confuse: memory capacity and memory bandwidth? <!--anki:782f576c373a7e467939-->
?
The **capacity** limits the volume of weight, KV cache and other allowances that may reside in a memory. The **bandwidth** limits the speed of transfers; it contributes to the throughput when these transfers are the neck.

Compare the two on the target workload. A large memory allows you to load a larger model without guaranteeing a faster generation; a high bandwidth is not enough if the model imposes an expensive offload. Calculation, batch, context, quantization and links between memories modify the compromise. The only GB announced do not allow to classify the machines.

---

Calculation: to batch 1, a dense 8B occupies on average 4.8 bits per weight in Q4_K_M. What ceiling of decode related to weight readings alone, with 400 GB/s and a full reading by token? <!--anki:6662653665313639616561363434653162323664663362306565646566613361-->
?
Under the reading assumptions given:
```text
poids = 8e9 × 4,8 / 8 = 4,8 GB
weight ceiling = 400 / 4.8 ≈ 83 tokens/s
```
The measured flow rate may be lower because of the KV, activations, of the kernels, dequantization and bandwidth sharing with the rest of the system. This quotient does not guarantee or 50–60 tokens/s in practice or a bottleneck always memory. Also check that the complete model fits in the available memory and measure the actual workload.

---

Why does a local LLM benchmark have to last long enough to reveal thermal limits? <!--anki:3434363562623530373734633439313261313463646438326364653463326538-->
?
A **short test** can benefit from a high frequency that the device does not maintain under continuous load. Temperature, power supply and concurrent tasks can reduce the flow rate after a few minutes.

Measure start-up, sustained speed, memory and consumption on the target device, with comparable context and quality. Test on battery if this use is expected. Check latency after several long requests and in the presence of the usual applications. A maximum throughput obtained cold machine is not enough to size a daily local experience.

---

Calculation: a device consumes additional 18 W for a generation of 20 seconds. What marginal energy per task, then for 1,000 tasks, excluding other costs? <!--anki:6330383966326132613062373437306361643934613863616438323632343864-->
?
A task consumes **18 × 20 = 360 joules**, or **0.1 Wh**. A thousand tasks represent **100 Wh**, or **0.1 kWh**.

It is a marginal energy in fixed conditions, without monitoring, cooling or other components. Also measure heating and sustained flow: a decrease in frequency can increase the duration and modify this estimate over long sessions.

---

Why test a local LLM application with the network effectively shut down? <!--anki:3536646538376337393335363461313939346362373037326130383232626165-->
?
It may still depend on **a tokenizer download, a license, a blocking telemetry, or a remote service**.

Prepare artifacts, launch from a clean environment, and test startup, useful tasks, and errors. Document functions unavailable offline. Also check for updates and temporary file management.

---

## Scenarios

Scenario: a team has put Ollama in production for 50 users and complains that "local models are slow. What do you diagnose? <!--anki:43257c3f2b6670734c3b-->
?
1. **Bad tool for use**: llama.cpp and Ollama handle few simultaneous requests
2. **Go to an inference server**: vLLM or SGLang, with continuous batching and PagedAttention ([[11-llm-inference-servers|Servers]])
3. **Checking hardware**: The throughput depends mainly on the **memory bandwidth**, not just the number of cores
4. **Dimensioner**: Measure actual throughput to target concurrency before closing ([[64-inference-metrics-slo|SLO]])
5. **Keep Ollama** for what he does well: development and prototyping positions

**Trap**: conclude that self-hosting does not work, while it is the server that is not suitable.

---

Scenario: an industrial customer wants an assistant that works without the Internet, on workshop workstations. How do you design the solution? <!--anki:5073454f71744f5d4025-->
?
1. **Set the task**: a small model (1 to 8 billion parameters) successfully completes a **targeted** task, not a general culture
2. **Quantizer in 4 bits** and check that the model fits in the memory of the workstations ([[68-quantization|quantization]])
3. **Specialize**: fine-tuning or distillation on task, to compensate for size ([[53-synthetic-data-distillation|distillation]])
4. **Provide exploitation**: distribution and update of several gigabytes, variants according to the hardware, evals redone by variant
5. **Safety**: weights are extricable from the station, and prompt injection remains possible

**Trap**: Promising the capabilities of a large cloud model on a device that has no memory or bandwidth.

---

## Sources

- [llama.cpp — formats, quantification and local inference](https://github.com/ggml-org/llama.cpp)
- [vLLM — Quantification and Compatible Hardware](https://docs.vllm.ai/en/latest/features/quantization/)

- [llama.cpp — Server Options and Offload Layers](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md) — targeted verification of 12 November 2026, without renewal of the global date of the topic.

## Connections
- [[68-quantization|Quantization]] — fit model
- [[11-llm-inference-servers|LLM Inference Servers]] — vLLM, llama.cpp, Ollama
- [[10-images-models-weights|Images & weights of models]] — GGUF and distribution
- [[146-model-selection|Choice of model]] — open weights vs API
- [[121-inference-costs|Inference costs]] — break-even
- [[53-synthetic-data-distillation|Distillation]] — small specialized models
- [[101-llm-security-guardrails|LLM Security]] — injection, exfiltration and guardrails
- [[61-kv-cache-attention|KV cache]] — memory that limits concurrency
- [[60-014-inference-parity-validation|Inference parity]] — checking the pre-tokenizer during GGUF conversion
- [[00-moc-ai-engineering|MOC AI Engineering]]
