# Containers — Overview — Flashcards
Tags: #flashcards #containers #review
<!-- summary: Transverse review cards (OCI, CRI and SIF, Kubernetes channels and image, GPU access, inference servers, weight storage), location of a failure in the launch chain, proof of portability, cold start diagnosis. -->


Do OCI, CRI and FIS refer to the same type of thing? <!--anki:6d445f2c347a236f5d4c-->
?
**Non.**

- OCI → open standards of containers
- CRI → interface Kubernetes ↔ container runtime
- SIF → format d'image Singularity/Apptainer

They concern three levels: OCI promotes interoperability, CRI links the kubelet to its runtime, SIF packs an image for Apptainer. For example, build with Docker and then run in Kubernetes concerns OCI and CRI; convert an image to an Apptainer file concerns SIF. Neither of these names replaces the other two.

---

Which Kubernetes chain should you rebuild? <!--anki:6f705f3e4421453a6f2d-->
?
```text
Kubernetes
    ↓
kubelet
    ↓
CRI
    ↓
containerd
    ↓
runc
    ↓
Linux Kernel
```

It is a **possible chain**, frequent: the kubelet requests execution via the CRI, containerd manages the lifecycle and delegates the creation of the process to an OCI runtime such as runc. The kernel provides isolation and control of resources. Other implementations can replace containerd or runc while respecting the expected interfaces.

To locate an error, ask which interface has completed its work: image drawn, process created, application ready. Model logs cannot explain a registry authentication that fails before it is launched.

---

Which string represents a classic image workflow? <!--anki:7232636a597439215430-->
?
```text
Dockerfile
    ↓
docker build
    ↓
Image OCI
    ↓
Registry
    ↓
pull
    ↓
Runtime
    ↓
Container
```

The Dockerfile describes the build; the image is the versioned artifact; the registry distributes it. The runtime then prepares an executable instance, the **container**, with process, network, and mounts. Multiple containers can start from the same image. Data written during runtime does not automatically become a new version of that image.

Rebuilding the same Dockerfile with unpinned dependencies can produce another image: the recipe alone does not guarantee reproducibility.

---

How to sum up Docker, Kubernetes, containerd and runc? <!--anki:4a54653c552f697c7a31-->
?
**Docker builds/manipulates the containers, Kubernetes orchestras them, containerd manages them and runc performs their low-level execution.**

These responsibilities complement each other: a developer builds an image with Docker, Kubernetes places Pods, then containerd and runc perform their execution on the node. This scheme helps diagnose: a pull error, a schedule error and a system call refusal are not at the same level.

---

How do I give access to the GPU according to the environment? <!--anki:434a6a212c3b70547052-->
?
- [[09-gpu-containers|Docker]]: `--gpus`, with Container Toolkit configured.
- [[13-apptainer-inference-hpc|Apptainer]]: `--nv`, in an allowed GPU allocation.
- [[12-kubernetes-gpu-inference|Kubernetes]]: resource `nvidia.com/gpu`, published by the device plugin.

Distinguish **allocation by the scheduler, visibility in the container and use by the framework**. Example: `nvidia-smi` successful, but the application uses a package CPU or place its tensors on CPU ; on the GPU remain unused.

Validate successively driver, allocation, exposure and small real inference. None of these settings add VRAM or guarantee memory isolation under sharing. In HPC, see a GPU does not give the right to use that of another job.

---

Which inference server for what purpose: GPU production, NVIDIA maximum performance, heterogeneous models, local workstation? <!--anki:3835303563363764303133313463393461306134623039613434386130383463-->
?
- **Production on GPU**, API compatible OpenAI: **vLLM** or **SGLang**
- **Maximum performance on GPU NVIDIA**: **TensorRT-LLM**, often served by **Triton**
- **Several types of models** (LLM, vision, classic models) behind the same server: **Triton**
- **Local post**: **Ollama** or llama.cpp

TGI is in maintenance mode ([[11-llm-inference-servers|Inference Servers]]).

These orientations do not replace a benchmark. Comparing on the same model, the same quantification and the same lengths; checking quality, p95 and cost per successful task. The fastest server on an isolated query may hold the target concurrency less well.

---

Where to store the weights of a model rather than in the image? <!--anki:7a6525313b45373b7221-->
?
In a **[[08-linux-primitives-docker-fundamentals|volume / bind mount]]** or a **External Storage** ; avoid "baker" the weights in the image. → [[10-images-models-weights|Images & poids]]

This makes it possible to update the server and weights separately, reuse a local cache and avoid republishing a huge image. Pinning a review or fingerprint and checking the integrity at loading. A download at startup without a cache can, however, greatly lengthen the cold start.

---

How to distinguish Apptainer, runtime, and SIF, image format? <!--anki:77763777364e6b7a5674-->
?
- **Apptainer**: the container runtime of **HPC** (ex-Singularity), without daemon and without root rights ([[06-apptainer-singularity|Apptainer]])
- **SIF**: Apptainer image format, a **unique** and immutable file

The runtime starts processes, while SIF transports their environment in a form that is easy to copy and verify. A SIF is usually used in read-only mode; outputs can go into external montages. Do not confuse read-only image with the inability to write to the host: the user's rights and montages remain decisive.

---

How to locate a container failure before accusing the inference server? <!--anki:3233383666316631666239633465346238326230353930666366396538653532-->
?
Follow the **launch string** until the last successful event: scheduler, kubelet, runtime, process creation, GPU initialization and then model loading.

A denied image download precedes any application code; a host OOM differs from a VRAM error; a false readiness differs from a stopped process. Keep events, exit codes, and timelines before restarting. This debugging reduces the assumptions to be tested and avoids modifying model settings for a registry or rights issue.

---

How can I demonstrate that an inference deployment is portable between two environments? <!--anki:3664306439363933373464333434383238373633613563663337643466313935-->
?
Replay **the same artifact manifest and query set** on both targets, with their documented hardware and configuration differences.

Compare boot, API functions, quality, memory and latency. An image accepted by two runtimes proves packaging compatibility, not identical performance or behavior. Include degraded modes and weight recovery to test the complete path.

---

Why break down the cold start of an inference container before optimizing it? <!--anki:6637366636363565626165353462616362656666346464313933626161316263-->
?
It can be dominated by **image uploading, weight uploading, or kernel initialization**. Reducing image size helps little if the cost comes from weights.

Timestamp each phase and compare cold and hot start. Then choose cache, preload or capacity already ready according to the prevailing cost. An effective local cache on an existing node can disappear when scale-out on a new node.

---

## Scenarios

Scenario: in maintenance, you are asked to describe what happens between `kubectl apply` and a container that runs on a GPU. What do you say? <!--anki:6936707d517d30363e60-->
?
1. **plane control side**: the API server saves the object, the scheduler chooses a node that satisfies the requested resources, including `nvidia.com/gpu`
2. **On the node**: the kubelet receives the Pod and calls the runtime by the **CRI**
3. **Runtime channel**: `containerd → runc → Linux kernel`, with namespaces and cgroups
4. **GPU**: NVIDIA Container Toolkit Injects Host Driver Devices and Libraries
5. **Applicative start**: image pull, loading of weights, probes that make the Pod ready

**Trap** : skip the CRI and talk about "Docker that launches the container" on a modern cluster.

---

Scenario: a newcomer confuses OCI, CRI and SIF in his architectural schemes. How do you clarify in three sentences? <!--anki:687a5b75263a75293542-->
?
- **OCI**: **standards** of containers (image, runtime, distribution)
- **CRI**: the **interface** between Kubernetes kubelet and container runtime
- **SIF**: the **Apptainer image format**, used in HPC

Useful marker: OCI says what an image looks like, CRI says how Kubernetes requests its execution, SIF is a competing format for another context.

**Trap**: Present CRI as an image format, while it is a API.

---

## Connections
- [[00-index|Index Containers (MOC)]] — full subject map
- [[01-oci|OCI]] — image, runtime and distribution standards
- [[04-kubernetes-kubelet-cri|Kubernetes & CRI]] — at the top of the execution chain
- [[00-moc-ai-engineering|MOC AI Engineering]]
