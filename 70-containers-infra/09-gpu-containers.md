# GPU in container — Flashcards
Tags: #flashcards #containers #gpu #cuda #infra
<!-- summary: NVIDIA Container Toolkit, driver and CUDA, CUDA images, GPU Operator, Apptainer `--nv`, ROCm, topology and communications between GPU, visibility and allocation, real CUDA test. -->


Does a container see the GPU of the default host? <!--anki:7278436c2c57552b3c74-->
?
**No.** Explicitly expose the **GPU** (`/dev/nvidia*`) devices and the **driver libraries** in the container.

The engine must be configured to transmit this access, for example via the NVIDIA Container Toolkit. The kernel driver runs on the host; the image provides the compatible application environment. Check the GPU on the host side first, and then in the container, to distinguish a driver problem from an exposure problem.

`nvidia-smi` function confirms the visibility, not the correct execution of the kernels of the model. Add a small calculation GPU with the library actually used to verify the actual compatibility.

---

What is the NVIDIA Container Toolkit? <!--anki:464b64547e593d74596f-->
?
The integration stack that exposes the **NVIDIA devices and host driver libraries** the containers, Especially with runtime. Hooks or **CDI**, according to the configuration.

Example: CUDA in the image provides user components, but not the kernel module of the driver. The Toolkit makes available the necessary host elements; it does not replace either the driver installation or the compatibility check.

Without configured exposure, a CUDA image does not automatically receive the GPU. CDI can be used for compatible rootless runtimes, but permissions and host configuration are still required. Test an inference, not just the presence of `/dev/nvidia*`.

---

How to launch a container with GPU under Docker? <!--anki:6826774e63433865767d-->
?
```bash
docker run --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
```
`--gpus all` (or `--gpus '"device=0,1"'`); `nvidia-smi` in container checks access.

This command assumes a compatible host driver and the NVIDIA Container Toolkit configured for Docker. The CUDA tag is a versioned example. `nvidia-smi` validates visibility and access to the driver, but not the entire compute stack; then run a small calculation with the framework used to verify CUDA and the necessary kernels.

---

Where is the driver and CUDA? <!--anki:5136266a643a60475856-->
?
- **NVIDIA driver** (core module): **on the host**, never in the image
- **CUDA toolkit / runtime** and libraries (cuDNN, NCCL): **in the image**

The container uses the host's kernel and NVIDIA module, and makes driver user libraries accessible. The application image provides the libraries it needs, not necessarily the full toolkit. Choosing compatible versions: Installing CUDA in the image cannot repair an absent host driver.

---

What is the compatibility constraint between driver and CUDA? <!--anki:6f476a253b514c4a3043-->
?
The **driver of the host must be fairly recent** for the CUDA version of the image. A CUDA 12.x image on a host with too old driver fails at startup: CUDA versions of the images are aligned to the driver park.

Baseline: `CUDA Version` line of `nvidia-smi` indicates the **maximum** version that the driver supports, not a CUDA installation. On Linux, 12 CUDA images require at least the 525 driver branch; some functions, such as the recent PTX JIT compilation, require a newer driver. On GPU datacenter, the `cuda-compat` package allows a more CXQ0005 to run.

---

What NVIDIA base images exist? <!--anki:4c6f73773453635d4e79-->
?
- **base**: the minimum CUDA
- **runtime**: + CUDA libraries to run
- **devel**: + compilers and headers for **compile**
Good reflex: compile in `devel`, deliver on `runtime` (**multi-stage build**).

A `devel` image helps build a CUDA extension, but embedding compilers and headers increases the size and maintenance area. Copy only the necessary artifacts in the final step and check the required dynamic libraries. Some applications compile at startup: test this behavior before removing the compilation tools.

---

Can I limit the VRAM of a container like RAM? <!--anki:4743213f66743c323749-->
?
**Not with regular cgroup RAM limits.** Shared access to the GPU does not create a hardware quota of VRAM. **MIG**, on compatible GPU, provides partitions; **time-slicing does not isolate memory** ([[12-kubernetes-gpu-inference|Kubernetes GPU]]).

A parameter like `--gpu-memory-utilization` guides the engine budget, without preventing another process from allocating the remaining VRAM. Two servers each configured for 90% can conflict. Sizing weight, KV and buffers together; using proper isolation rather than presenting an application setting as a guarantee between tenants.

---

What VRAM capacities do common GPUs provide? <!--anki:6c37477e77387b442667-->
?
```text
RTX 4090 / 5090 24 to 32 GB workstation
L4 24 GB economical inference
L40S 48 GB inference, no NVLink
A100 40 or 80 GB previous generation, no FP8
H100               80 GB       FP8 natif, NVLink
H200 141 GB ideal for long contexts
B200              ~180 GB      Blackwell, FP4 natif
B300 ~288 GB Blackwell Ultra, increased HBM3e memory
```
These capabilities are benchmarks of material variants; check the exact file of GPU. Compare **Weight + KV cache + engine allocations** to the really usable memory, with coherent units. The only weight of one 70B in BF16 represents approximately 140 GB: This does not guarantee a serving Operate on an H200 141 GB, lack of sufficient margin according to the configuration.

---

What is the NVIDIA GPU Operator? <!--anki:6a3f28646d4a55596924-->
?
A Kubernetes operator that **installs and manages the entire GPU** stack on nodes: driver, Container Toolkit, **device plugin**, export metrics **DCGM**, MIG configuration.

It automates the deployment and maintenance of compatible components, some of which may already be provided by the administrator. Its installation is not enough to set a sharing, quota or placement policy. Check the health of the components, the resources announced and the policy chosen for the different types of nodes.

---

How to give access to a GPU AMD to a container? <!--anki:507e28233f496e5a7523-->
?
With **ROCm**: expose the `/dev/kfd` and `/dev/dri` devices to the container and use ROCm images. vLLM and PyTorch support ROCm.

Check the support matrix for the GPU, the system and the ROCm version, as well as device permissions. Framework support does not mean that all CUDA model architectures or optimizations are available. Test a basic calculation and then the target model before comparing performance.

---

Calculation: estimate the VRAM for a 8B with 30 active sequences of 4,000 tokens each, 16 GB of weight BF16, 128 KB of KV/token and 3 GB of other allocations, before margin? <!--anki:6131653231643037393661613436643938623330323430663339666230626637-->
?
```text
weight 8B in BF16 ≈ 16 GB
KV : 30 × 4,000 tokens × 128 Ko  ≈ 15.7 GB
activations, graphes CUDA        ≈  3 GB
total ≈ 35 GB → 48 GB (L40S) or 80 GB; 24 GB is not enough
in FP8 (weight and KV cache) ≈ 19 GB → nominal budget compatible with 24 GB, to be checked
```
We dimension on the **concurrency** and the **context length**, not just on the model size ([[61-kv-cache-attention|KV cache]]).

The 128 KBs are about **128 KBs**, for precise architecture and BF16 cache; not all 8Bs have this cache size. Add the output tokens and margins. The total FP8 of 19GB suggests memory feasibility, but does not guarantee peak loading or compliance with target latency.

---

Why doesn't having two GPUs guarantee a quick link between them for inference? <!--anki:6635636635313233633834643434323339666663326664646563363864366161-->
?
The **Material Topology** Determine the path between GPU : dedicated interconnection, PCIe, Passing through the CPU or network between nodes. Adding their VRAM does not describe these exchanges.

Check for links that are actually accessible to the container and measure the communications of the chosen parallelism. Compare a model on multiple GPUs with independent replicas when it fits on a map. Include placement and affinity in the benchmark manifest. An inference limited by transfers can slow down despite more GPU and sufficient total memory.

---

Why is a successful nvidia-smi in a container not enough to validate a CUDA application? <!--anki:6664393534663837353430623431656462653964653662323831306165623163-->
?
It mainly confirms **access to the management interface of the GPU**. Loading libraries, the kernels used and the application memory requirements may still fail.

Run a minimal calculation with the actual framework, then a representative query. Check compatible versions, accuracy and GPU architecture. Do not turn this smoke test into proof of capacity under load: this one requires a separate benchmark.

---

Why does the visibility of a GPU not guarantee its exclusivity for a container? <!--anki:3364663537306632326666623435326538646135336136613132633839616665-->
?
Make a device visible determines **what the process can address**, Not always who else uses it. Several processes can share compute and memory depending on the configuration.

Check allocation by orchestrator, sharing policy and competing processes. Measure effects on latency and memory. A visibility variable is not, in itself, an isolation boundary or capacity reservation.

---

## Scenarios

Scenario: your inference container starts but `nvidia-smi` does not respond to it, while the GPU is clearly visible on the host. How do you proceed? <!--anki:4f613c7a75292524322a-->
?
1. **Check for exposure**: Was the container launched with `--gpus` (or the GPU resource under Kubernetes)?
2. **Check Toolkit**: Without NVIDIA Container Toolkit, neither devices nor driver libraries are injected
3. **Verify versions**: A CUDA image that is more recent than the host driver fails. The driver remains **on the host**, CUDA **in the image**
4. **On Kubernetes**: device plugin present, node correctly tagged, resource GPU requested ([[12-kubernetes-gpu-inference|K8s GPU]])
5. **Simplify test**: Launch a basic CUDA image with `nvidia-smi`, before debugging the application

**Trap**: Install the NVIDIA driver in the image, which conflicts with the host's.

---

Scenario: two teams share a GPU for their inference services, and one regularly saturates the VRAM, knocking down the other. What do you offer? <!--anki:6c7a70385b75254f5d2d-->
?
1. **Explain limit**: cgroups do not limit VRAM. A container with access to the GPU can consume it entirely
2. **MIG**: partition the GPU into **isolated** instances, with dedicated memory, on the GPU that support it
3. **Time-slicing**: sharing possible, but without memory isolation, so the problem would remain
4. **Or dedicate**: one GPU per service, if the load justifies it
5. **Monitor**: VRAM and errors by GPU, with export DCGM ([[93-monitoring-inference|monitoring]])

**Trap**: Believe that a container memory limit protects the memory of the GPU.

---

## Sources

- [NVIDIA — memory capacities of HGX H100, H200 and B200 systems](https://docs.nvidia.com/enterprise-reference-architectures/hgx-ai-factory-h100-h200-b200/latest/components.html)
- [NVIDIA — GB300 NVL72 and Blackwell Ultra GPU Memory](https://www.nvidia.com/en-us/data-center/gb300-nvl72/)

- [Apptainer — access to GPU devices and libraries](https://apptainer.org/docs/user/main/gpu.html)

- 14 November 2026 — Diagnostic of GPU path in container: [NVIDIA — Container Toolkit troubleshooting](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/troubleshooting.html).

## Connections
- [[00-index|Index Containers]] — container bases
- [[12-kubernetes-gpu-inference|Kubernetes GPU & inference]] — allocate and share GPU
- [[61-kv-cache-attention|KV cache]] — what consumes VRAM
- [[11-llm-inference-servers|Inference Servers]] — what runs on the GPU
- [[08-linux-primitives-docker-fundamentals|Linux primitives]] — cgroup devices
- [[10-images-models-weights|Images & poids]] — images CUDA volumineuses
- [[13-apptainer-inference-hpc|Apptainer & HPC]] — `--nv` in HPC
- [[03-containerd-runc|containerd & runc]] — where the toolkit fits into the string
- [[04-kubernetes-kubelet-cri|Kubernetes, kubelet & CRI]] — orchestration and its interface with runtime
- [[06-apptainer-singularity|Apptainer & Singularity]] — the world's HPC containers
- [[54-distributed-training|Distributed training]] — memory and drive parallelisms
- [[00-moc-ai-engineering|MOC AI Engineering]]
