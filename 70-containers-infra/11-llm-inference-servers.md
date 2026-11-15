# LLM inference servers — Flashcards
Tags: #flashcards #ai-engineering #inference #serving #llm
Verified on: 25 September 2026 — This factsheet lists products, versions or regulatory texts that are evolving quickly.
<!-- summary: vLLM, API compatible OpenAI, multi-LoRA, SGLang, TensorRT-LLM and Triton, TGI, llama.cpp and Ollama, boundary tests of a compatible API, effective tokenizer, termination tests. -->


What is a LLM Inference Server? <!--anki:495d704d38615143496f-->
?
To **load the model on the GPU** and serve it effectively to many users: batching, [[61-kv-cache-attention|KV cache]] management, streaming, **API HTTP** and metrics.

It orders requests to share hardware, manages active sequence memory, and exposes the state of the service. A API around a simple `generate` call does not necessarily provide these mechanisms. Sizing the server from input and output lengths, concurrency, and the expected SLO.

---

Do not confuse: inference server and gateway LLM? <!--anki:4441306c4a2b54426b3d-->
?
The **inference server** loads the weights and calculates the outputs on its hardware; the **gateway** ([[81-litellm-api-layer|LiteLLM]]) applies policies and routes calls to the backends. It performs processing, but normally does not infer the target model.

Example: A 429 HTTP response may come from the gateway quota while the GPU are free; adding a server does not correct this policy.

Frequent channel: `client → ingress → gateway → server → accelerator`. External APIs sometimes replace the self-hosted server. Trace each layer: an OpenAI-compatible API does not say which layer responds or where the neck is located.

---

Why not serve a model with a simple Transformers script? <!--anki:7371754d53625342432e-->
?
A naive script that processes requests one by one often leaves the GPU underutilized and does not handle queue, cache and concurrency well. A specialized server brings scheduling, continuous batching, limits and metrics.

The gain is not **not a fixed factor of 10 or 20** : it depends on the model, of the starting implementation and the load. A script may be sufficient for local use or a small batch. compare options on a representative benchmark before making the deployment more complex.

---

What is vLLM? <!--anki:6a7a656152266d58602f-->
?
The reference open source inference server: **PagedAttention**, **continuous batching**, prefix caching, quantization, tensor parallelism, [[63-guided-generation|guided generation]] and **API OpenAI compatible**.

```bash
vllm serve meta-llama/Llama-3.1-8B-Instruct --max-model-len 8192
```

The command limits the accepted total length to 8,192 tokens depending on the configuration of the model. Check availability of weights, hardware compatibility and memory, then protect the endpoint and test its support before exposure.

A loaded model does not prove that there is enough KV left for the intended concurrency. Test prompts long and long outputs together, following rejections and preemptions.

---

What is the multi-LoRA in serving? <!--anki:46362e6e346d5f39534d-->
?
Load **several [[51-fine-tuning-adaptation|LoRA]]** adapters above a **only base model** in VRAM: each request chooses its adaptor, and dozens of fine-tuned variants are used for the price of a model.

The economy comes from sharing large base weights; adapters still have a memory and management cost. They must match the right architecture and the right basic review. Measure latency during loads and transitions, and prevent a request from accessing an adapter from another tenant.

---

What is SGLang? <!--anki:483f5936213a34336e4e-->
?
A high-performance vLLM concurrent server with **RadixAttention** (cached shared prefix tree): especially effective for **agentic** and multi-call workloads that reuse long prefixes.

Sharing helps when queries actually have common prefixes and the cache can keep them. It does not guarantee the best performance on any load. Compare model support, stability, latency, and throughput with the same hardware and inputs, distinguishing between cold cache and hot cache.

---

What is TensorRT-LLM and Triton? <!--anki:703f3e3e306448765b68-->
?
**TensorRT-LLM** provides inference components and engines optimized for NVIDIA GPUs; its backends and preparation modes depend on version and model. **Triton Inference Server** exposes and orchestrates models via multiple backends, with API, metrics and scheduling.

They can be combined: TensorRT-LLM performs the LLM calculation and Triton provides a service layer. Checking the supported integration path and measuring gains; "optimized" does not always mean better on any workload.

---

What is TGI (Text Generation Inference) from Hugging Face? <!--anki:62455d30213b665d742b-->
?
**Text Generation Inference** (Hugging Face): Historically widely used server, today **in maintenance mode**; Hugging Face is oriented towards vLLM and SGLang.

Maintenance mode means that it is not necessary to assume a functional evolution at the same rate as the preferred engines for new projects. For an existing service, consider necessary patches, supported models and migration cost. A migration is decided on these needs and comparative tests, not on the server name alone.

---

Which server to use for local LLM inference? <!--anki:6f484e484e652c34492a-->
?
**llama.cpp** and **Ollama**: Quantized **GGUF**, CPU, Mac (Apple Silicon) or GPU consumer models. Suitable for local development and deployments; their capacity under concurrency must be measured.
```bash
ollama run llama3.1:8b                       # Local, a user
vllm serve meta-llama/Llama-3.1-8B-Instruct \
  --max-model-len 8192 --gpu-memory-utilization 0.9   # server, multi-user
```
The toggle depends on the hardware and the SLO, not a universal threshold of users. Test the [[164-local-edge-llm|service local]] to the expected concurrency: if it respects quality and timeliness, changing engine is not mandatory. Compare useful throughput, memory and operating cost before migration.

---

What criteria to use when choosing a LLM inference server? <!--anki:645063305f2e3f68515b-->
?
**Model support** and equipment, throughput and latency measured on **your** Charge ([[64-inference-metrics-slo|benchmark]]), Functions (LoRA, guided generation, prefix caching), exposed metrics, maturity and ease of operation on Kubernetes.

Also test start-up, build-up, request cancellation, disaster recovery, and updates. An advertised feature may only be available for certain model and GPU combinations. Withhold a specific version and publish benchmark assumptions to make the decision repeatable.

---

Why does an OpenAI-compatible API not guarantee the same behavior between inference servers? <!--anki:3333356436343833623934393438616561613761653137316437343461323465-->
?
The **Compatibility ofAPI** can carry on paths and fields without covering all functions: tools, Diagrams, Stop tokens, errors, cancellation or usage metrics.

Define the functionalities used by the application and test their limit cases on each engine. Compare in particular an incomplete output, a refusal and a streaming tool call. Fix model, tokenizer and chat template before assigning a difference to the server. A simple request that responds with HTTP 200 does not demonstrate the interchangeability of the complete application contract.

---

Why check the chat template when replacing an inference server? <!--anki:3465343563336131366662373437643061383466343266333736373631353232-->
?
The template turns messages into **tokens of roles, separators, and markers expected by the template**. An HTTP-compatible server can serialize the same messages differently.

Compare the actual rendering and special tokens, then test responses, tool calls and stop conditions. A degradation may come from the template rather than weights or the kernel. Keep its version with the tokenizer in the release.

---

How to test the end conditions of a LLM inference server? <!--anki:3235393432653462633963653439393361656635373435376339666562386363-->
?
Cover **EOS, stop sequence, tokens limit, cancellation and error**. Check returned text, end pattern and resource release for each case.

A truncated response should not be presented as complete. Testing stop markers that cross multiple stream fragments and processing special tokens. Correct responses on short prompts do not validate these boundaries.

---

## Scenarios

Scenario: a team serves a 8B model with a Transformers script behind FastAPI. At 30 users, everything collapses. What do you offer, and what gains do you advertise? <!--anki:6c3f6a2157402575507b-->
?
1. **Diagnose**: request-by-query processing, GPU underutilized, no KV cache management
2. **Go to an inference server**: vLLM or SGLang, with continuous batching and PagedAttention
3. **Announce a hypothesis**, not a promise: the flow gain can reach an order of magnitude, but depends on the starting script and the load; measure it before committing
4. **Keep the OpenAI compatible API**, so as not to touch the customer code ([[81-litellm-api-layer|gateway]])
5. **Measure before and after**: TTFT, TPOT, throughput and concurrency held ([[64-inference-metrics-slo|SLO]])

**Trap**: Add replicas of the existing script, which multiplies the cost without fixing the problem.

---

Scenario: your company has 15 fine-tuned variants of the same model 8B, one per customer. Does 15 need deployments? <!--anki:6f3158764657234e4e3a-->
?
1. **No, if they are LoRA**: the **multi-LoRA** loads multiple adapters over a single base model in VRAM
2. **Each query chooses its adaptor**, which allows you to serve dozens of variants for the price of a model
3. **Watch out for VRAM**: adapters are small, but their number and the KV cache remain to be monitored
4. **Closure**: check that a request from one client cannot be adapted by another
5. **If the variants are complete fine-tunings**: there, it is necessary to separate deployments ([[51-fine-tuning-adaptation|fine-tuning]])

**Trap**: Merge the adapters into the basic weights “to simplify”, and lose the benefit of sharing.

---

## Sources

- [Hugging Face — TGI in maintenance mode](https://huggingface.co/docs/text-generation-inference/main/en/index)

- [SGLang — server documentation and optimizations](https://docs.sglang.io/)
- [vLLM — production metrics](https://docs.vllm.ai/en/latest/usage/metrics/)

## Connections
- [[61-kv-cache-attention|KV cache & attention]] — PagedAttention
- [[62-inference-optimizations|Inference optimizations]] — what the server implements
- [[51-fine-tuning-adaptation|Fine-tuning]] — multi-LoRA serving
- [[12-kubernetes-gpu-inference|Kubernetes GPU & inference]] —
- [[09-gpu-containers|GPU in container]] — access to the GPU
- [[10-images-models-weights|Images & poids]] — loading weights
- [[13-apptainer-inference-hpc|Apptainer & HPC]] — serving on an HPC cluster
- [[00-index|Index Containers]]
- [[66-prefix-caching-radix-attention|Prefix caching & RadixAttention]] — RadixAttention from SGLang
- [[67-speculative-decoding|Speculative Decoding]] — enable and adjust in vLLM or SGLang
- [[68-quantization|Quantization]] — serve FP8, AWQ, GPTQ or GGUF models
- [[93-monitoring-inference|Monitoring of inference]] — operate `/metrics` and `/health`
- [[164-local-edge-llm|Local LLM & Edge]] — Ollama, llama.cpp, MLX
- [[132-tokenization|Tokenisation]] — chat templates
- [[04-kubernetes-kubelet-cri|Kubernetes, kubelet & CRI]] — orchestration and its interface with runtime
- [[114-reproducibility-variance|Reproducibility & variance]] — non-determinism and eval statistics
- [[148-llm-batch-pipelines|Pipelines batch]] — process millions of items at a lower cost
- [[65-probabilities-sampling|Probability & sampling]] — temperature, top-p and logprobs
- [[69-roofline-prefill-decode|Roofline & Disaggregation]] — which limits each phase of the inference
- [[83-gateway-ingress|Ingress & API gateway]] — network input stack
- [[85-agentic-protocols-map|Map of protocols]] — which protocol to which agent boundary
- [[00-moc-ai-engineering|MOC AI Engineering]]
