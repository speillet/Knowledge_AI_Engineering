# Images & weights of — Flashcards
Tags: #flashcards #containers #models #storage #infra
<!-- summary: calculation of the loading time of the weights of a 70B, weight in the image or separated, cold start, safetensors or pickle, safetensors or GGUF, distributed models as OCI artifacts, atomic publication of a weight cache, integrity of shards, download cache. -->


Calculation: what minimum network transfer time for 140 GB of weight BF16 of a 70B, at 1 then 10 Gbit/s constant, excluding storage, deserialization and engine initialization? <!--anki:4e2e2a7a3e49745e523f-->
?
Convert bytes to bits before dividing by bitrate:
```text
140 GB × 8 = 1 120 Gbit
at 1 Gbit/s: 1,120 s ≈ 18 min 40 s
at 10 Gbit/s: 112 s ≈ 1 min 52 s
```
These durations only cover constant-rate transfer. RAM/VRAM loading, storage playback, deserialization, compilation, and warm-up can still delay the readiness. A local cache avoids this remote transfer, but its duration should be measured rather than universally assumed by a few seconds.

If four replicas read the same weight on a common saturated source, the individual time may increase; test this concurrent startup before scaling the autoscaling.

---

Should we put the weights in the container image? <!--anki:707d512f4d7270214938-->
?
- **In the image**: artifact **autonomous and immutable**, but huge image, slow pull and rebuild to each model version
- **Separated** (recommended for larger models): light image with runtime, loaded weights from storage

Criterion: size and rate of change. A 300 MB classifier that evolves with the code wins to be in the image, versioned with it. A LLM of several tens of gigabytes, which changes independently of the server, loads from storage. Pin a review or digest of the weights, to keep the immutability that the image brought.

---

Where to store weights when separated from the image? <!--anki:6d5d53393124313f7072-->
?
- **Shared volume** (PVC, NFS) mounted in Pods
- **Object storage** (S3, GCS) downloaded at startup
- **Hugging Face Hub** (or internal mirror), with persistent **cache** (`HF_HOME`)
- **Local cache** on the node disk
```yaml
env:
  - { name: HF_HOME, value: /cache/hf }      # cache shared between Pods
  - { name: HF_HUB_OFFLINE, value: "1" }     # Prohibits any surprise download
volumeMounts:
  - { name: model-cache, mountPath: /cache/hf }
```
The **local cache on the node** is the fastest, the **shared volume** the easiest to pool.

Offline mode assumes the files already present, including tokenizer and configuration. Preload a complete review and check its fingerprint; a partial cache must explicitly fail the startup, not trigger an unexpected download.

---

Do not confuse: container registry and model registry? <!--anki:666631384e6473424e60-->
?
- **Container registry** (Docker Hub, Harbor, ECR): stores **OCI images**, addressed by tag or digest
- **Model registry** (MLflow, W&B, Hugging Face): stores **model versions** with their **metadata**: metrics, lineage, stage (staging, production), author

The two complement each other: the image contains the **runtime**, the registry model says **what weights** to deploy ([[111-mlops-llmops-fundamentals|MLOps]]). The trend of OCI artifacts blurs the border, but the metadata remains the contribution of the registry model.

---

What is the cold start of a model server? <!--anki:655d3c2f5b7a6d6e494b-->
?
The time before the first response: **pull of the image + upload of the weights + loading in VRAM** (+ possible compilation). It can reach **several minutes**, which penalizes the scale-from-zero.
```text
pull image (10 GB) 30 s to 3 min depending on network and cache
weight 8B from S3 1 to 3 min
weight 8B from node 10 to 30 s
loading in VRAM 10 s to 1 min
compilation (TensorRT) several minutes, to be done once
```
These figures are illustrative, not a SLO. If the peak lasts two minutes and the start takes four, the reactive autoscaling arrives too late: anticipate hot capacity, anticipation or queue compatible with the product delay ([[12-kubernetes-gpu-inference|autoscaling GPU]]).

---

How to reduce the cold start of an inference pod? <!--anki:643a67575b6d6a61735d-->
?
**Pre-pull images** on GPU nodes (DaemonSet), keep weights in **local cache**, download via a **init container**, stream weights directly to the GPU, keep a minimum of hot replicas.

Measure node wait, image pull, weight transfer, GPU loading, and warm-up separately. An init container orders the download but does not make it faster on its own. Keeping a hot replica reduces latency at the cost of idle resources; choose according to the SLO and traffic variability.

---

Why prefer the safetensors format? <!--anki:6a617730764d4a24792f-->
?
Because it contains **only tensors**: no code executed at loading, unlike the **pickle** PyTorch files (`.bin`, `.pt`) which can **execute arbitrary code**. It is also faster to load (mmap).

**mmap** projects the file into memory without an intermediate copy: the processes of the same node share the pages already read, and a tensor is only read at its first access. Limit: safetensors deletes the code when loading the weights, not that of the repository. A `trust_remote_code=True` always executes the Python supplied with the model.

---

Do not confuse: safetensors and GGUF? <!--anki:3636316535383632616663663462353961326137313766323332643535323562-->
?
**safetensors** stores tensors without executing Python code on deserialization; configuration and tokenizer are usually separated. **GGUF** groups tensors and metadata for runtimes like llama.cpp, with several possible details.

GGUF is not reserved for the CPU and can be divided into several files; safetensors does not in itself guarantee the security of all the code of the repository.

Example: renaming a checkpoint does not convert its format. Choose a conversion and a [[68-quantization|quantification]] supported by the runtime, then control tokenizer, quality and memory ([[164-local-edge-llm|Local Inference]]).

---

How to keep a reasonable inference server image? <!--anki:483132742f7d464d5863-->
?
**Multi-stage build** (compile in a `devel` image, deliver on `runtime`), minimal dependencies, layers ordered to **maximize the cache**, and especially **no weight** in the image.

Measure compressed size, deployed size, and boot time. Avoid unnecessary download caches and build tools in the final image. Weight separation is a common choice for independent updates; if a standalone artifact includes them, document the compromise and explicitly version those weights.

---

How to ensure traceability of deployed models? <!--anki:722b4e75573023266877-->
?
By **versioning the weights** (review/commit Hugging Face, digest, model register) and by **pinning them** in the deployment configuration, as one pins the digest of an image.

Trace also tokenizer, chat template, adapt, quantize and configure the server. Two deployments with the same weights can behave differently if these elements change. A deployment manifest connects these versions to the evaluation results and makes it possible to rebuild or restore the variant actually validated.

---

What trend is emerging to distribute model weights with container tooling? <!--anki:426c59524537246c475d-->
?
Distribute weights as **OCI artifacts** in a registry, then mount them as volumes (Kubernetes image volumes, KitOps): same tooling as images (versioning, cache, signature).

This separates the model artifact from the application image while reusing the registry and delivery controls. Check the features available in the Kubernetes version and the chosen runtime. The OCI packaging does not solve by itself the download times, the weight format or their compatibility with the inference engine.

---

Why should a shared weight cache publish models atomically? <!--anki:3635323430383338333738343462613261383363343139393730333133643561-->
?
Two **workers** can read the same path during a download or update. If files appear gradually, they may load a mix of versions or incomplete weights.

Download in a temporary location, check manifest and checksums, and then publish a reference to a full, immutable version. Make the service ready only after loading validated. Clean versions with a policy that takes into account active drives. A present file or a plausible size does not guarantee the integrity of all shards.

---

Why check all shards and their index before publishing a downloaded model? <!--anki:3233356430306434663233383438623762393633613333333230353636333962-->
?
A partially filled directory can have **the right name and a plausible size** while lacking tensors. The index associates the weights with their shards; their consistency must be checked.

Upload to a temporary space, check the manifest and the available footprints, and then make the set visible atomically. Test an interrupted download. A "ready" marker file is only reliable if it is written after these controls.

---

How to prevent multiple Pods from simultaneously downloading the same weights into a shared cache? <!--anki:3361343565623936333138353465626562636635363733666262306162373338-->
?
Use **one coordination mechanism per version of artifact**, then let readers use only a full version. Provide owner timeout and recovery after failure.

Write to separate temporary files and publish without overwriting an active download. The lock protects coordination; integrity checks protect content. Also monitor playback throughput once the download is complete: the cache may become the next bottleneck.

---

## Scenarios

Scenario: autoscaling adds a replica to the peak load, but the new Pod takes 7 minutes to serve its first request. How do you reduce this delay? <!--anki:664c5d31717646235664-->
?
1. **Decompose the cold start**: image pull, weight download, VRAM loading, possible compilation
2. **Pre-pull** image on GPU nodes, with a DaemonSet
3. **Cache weights locally** on the node, or serve them from a fast shared volume
4. **Download in init container**, or stream weights directly to the GPU
5. **Keep a warm base**: autoscaling must anticipate, not react ([[12-kubernetes-gpu-inference|K8s GPU]])

**Strap**: Sizing autoscaling on application metrics without considering startup time.

---

Scenario: a colleague downloads a model from a public repository and wants to deploy it in production tomorrow. What controls do you impose? <!--anki:464963526d393250565e-->
?
1. **Format**: privilege **safesensors**. A pickle file can execute code on loading
2. **Provenance**: official editor, review pinned by imprint, verified signature if available ([[105-agentic-ai-devsecops|Supply Chain]])
3. **License**: commercial use allowed, conditions on derivative models
4. **Evals**: quality on your own cases, not just the advertised scores
5. **Traceability**: version registered in the model registry and pinned in the deployment ([[111-mlops-llmops-fundamentals|MLOps]])

**Trap**: Load pickle weights from an unknown repository directly to a production server.

---

## Connections
- [[00-index|Index Containers]] — OCI images and layers
- [[09-gpu-containers|GPU in container]] — images CUDA
- [[12-kubernetes-gpu-inference|Kubernetes GPU & inference]] — pull time and scaling
- [[11-llm-inference-servers|Inference Servers]] — which loads the weights
- [[02-docker-images-registries|Registries & images]] — storage & distribution
- [[08-linux-primitives-docker-fundamentals|Volumes & bind mounts]] — lift weights
- [[111-mlops-llmops-fundamentals|MLOps]] — the in-depth registry model
- [[68-quantization|Quantization]] — reduce weight size
- [[105-agentic-ai-devsecops|DevSecOps for Agentic AI]] — Signature Models and AI-BOM
- [[164-local-edge-llm|Local LLM & Edge]] — run a model locally
- [[00-moc-ai-engineering|MOC AI Engineering]]
