# Apptainer & Inference HPC — Flashcards
Tags: #flashcards #containers #apptainer #hpc #llm #inference
Verified on: 29 September 2026 — This factsheet lists products, versions or regulatory texts that are evolving quickly.
<!-- summary: Apptainer or Docker in HPC, security model, Slurm integration, `--nv`, weights mounted from the shared file system, SIF images, definition file, multi-node service (Ray, InfiniBand, NCCL), exposure of a server launched in a job, drainage before walltime, Slurm allocation, local caches. -->


Why do we prefer Apptainer over Docker in HPC environment? <!--anki:632d364048502c312858-->
?
Apptainer integrates with **Unix identities, shared file systems, and HPC schedulers**, with no central daemon comparable to Docker Engine. A Slurm job can launch an SIF image with user rights.

Example: The container reads the allowed data from the account and uses the GPU allocated to the job; it must not bypass the cluster quotas.

Nuancer security: Apptainer can be installed with a setuid component depending on configuration; Docker also exists as rootless. It is the access to the socket of a **rootful** Docker that confers equivalent powers to root. Respect the installation choices and policies of the administrators.

---

How does Apptainer integrate with Slurm? <!--anki:4e31232b53236e642f30-->
?
The Apptainer command is **launched inside a Slurm** job, inheriting allocated resources (GPU, CPU, memory): there is **nothing to install on the scheduling side**, since there is no demon.
```bash
#!/bin/bash
#SBATCH --gres=gpu:1 --cpus-per-task=8 --mem=64G --time=02:00:00
apptainer exec --nv \
  --bind /scratch/models:/models \
  vllm.sif python -m vllm.entrypoints.openai.api_server --model /models/llama-8b
```
The variables `SLURM_*` and `CUDA_VISIBLE_DEVICES` are **inherited** by the container.

The container also inherits **limits** from the job. If the cluster applies the Slurm cgroups, a load that exceeds the requested 64 GB is killed for lack of memory, even on a 512 GB node. Similarly, `--cpus-per-task` limits loading and tokenization threads: sizing the request on the boot peak, not just on the established scheme.

---

How do I provide model weights to an Apptainer container? <!--anki:4a423c78424443567254-->
?
By **mounting the shared file system** with `--bind`.

```bash
apptainer exec --nv --bind /data/models:/models model.sif python serve.py
```

The left path indicates the storage visible on the host, the right path indicates its location in the container. Use accurate weight review and read-only editing if no changes are required. Verify rights, shared storage throughput, and presence of all expected files before launching the server.

The form `--bind /data/models:/models:ro` makes read-only explicit. Keep caches and results on another writable path; otherwise a library attempting to write near weights may fail at startup.

---

How to recover a Docker image in Apptainer format? <!--anki:4626266d35774b253342-->
?
With `apptainer pull` and the prefix `docker://` (see [[06-apptainer-singularity|Apptainer & Singularity]]).

```bash
apptainer pull vllm.sif docker://vllm/vllm-openai:latest
```

Apptainer downloads the registry image and converts it to SIF; Docker Engine does not need to rotate on the node. `latest` is convenient to illustrate the command but is not reproducible. In production, use an immutable reference or a controlled tag, keep the SIF fingerprint and check the compatibility of the entry point.

Building or retrieving the SIF before the GPU job avoids paying an allocation while downloading, and then testing the image on a representative compute node, not just the connection node.

---

How to build an Apptainer image from a definition file? <!--anki:77425d60757078702d63-->
?
A `.def` file starts from an existing image and completes it:
```text
Bootstrap: docker
From: vllm/vllm-openai:v0.10.1

%environment
    export HF_HUB_OFFLINE=1

%runscript
    exec vllm serve "$@"
```
```bash
apptainer build vllm.sif vllm.def      # often possible without root (--fakeroot)
apptainer run --nv --bind /data/models:/models vllm.sif /models/llama-70b
```
The `.def` file is **version** in Git, and the produced SIF is an immutable artifact.

The offline mode assumes that weight, tokenizer and necessary configurations already exist in the timeline. The given tag is illustrative: choose a version compatible with the model and the drivers of the cluster. The possibilities of build without root depend on the user namespaces and the administrator configuration; check these prerequisites before planning the job.

---

How do I serve a multi-node model with Slurm and Apptainer? <!--anki:4a3d3177612d7c5e5a56-->
?
- **Tensor parallelism in node** (NVLink), **pipeline parallelism between nodes**, because the internode network is slower ([[54-distributed-training|Parallelisms]])
- A Slurm allocation of N nodes, where `srun` starts a container per node and a **cluster Ray** that connects vLLM workers
- The container must see the fast network: **InfiniBand** and associated libraries, which `--nv` does not provide, so that **NCCL** does not fall back on Ethernet

Check the NCCL flow rate before accusing the model of being slow.

---

How to expose an inference server launched in a Slurm job? <!--anki:72645e2f7e58367a5647-->
?
The server listens to a **calculation node** whose name changes with each job:
- The job **publishes its address** (shared file, discovery service) or a **reverse proxy** on an access node route to it
- For personal use: **SSH tunnel** via the login node
- The **walltime** limits the duration: provide an automatic resubmission and a **health check** on the client side

These bypasses show the HPC limit for a permanent service ([[12-kubernetes-gpu-inference|Kubernetes GPU]]).

---

Why should a Slurm job that arrives at its walltime stop accepting new requests before stopping? <!--anki:3063353234626533643164613434616438313935303361346466393731653531-->
?
The **walltime** imposes a deadline independent of the duration of the requests. Continuing to accept work until the last second increases the interrupted answers.

Schedule a drainage phase: remove the instance from the discovery, refuse new requests, and let the remaining requests finish within the remaining time. Make long jobs repeatable or explicitly announce their interruption. Test the shutdown with active clients. An automatic resubmission eventually restores the capacity, but does not guarantee the continuity of the flow or the retention of requests in memory.

---

Why should a server running a Slurm job use only the allocated resources? <!--anki:6132383733303833396236383437646262643863643366383465313163363838-->
?
The node can be **shared with other jobs**. Detect all GPUs on the machine and then use them ignores the allocation and can cause conflicts or policy violation.

Respect the scheduler's exposure mechanisms and constraints, and then check rows, GPU, and ports actually used. Do not run heavy compute on a connection node. Test multi-process launch in the configuration allowed by the center.

---

When to copy the weights to the local storage of an HPC node before inference? <!--anki:6437383938313230643938333461646539666538353739623765666236383430-->
?
When multiple reads on shared storage become **a measured bottleneck** and the job has enough space and time, the copy adds an upfront cost that needs to be amortized.

Verify integrity, isolate caches by version, and manage their lifetime. One copy per row can unnecessarily multiply transfers; coordinate at node level. Take into account local data cleansing and privacy.

---

## Scenarios

Scenario: you must serve a 70B model on an HPC cluster in Slurm, without root rights and without Internet access from the compute nodes. How do you organize? <!--anki:6d3e37556e6351317430-->
?
1. **Prepare image elsewhere**: `apptainer pull` from a node that has the network, then copy the SIF to the shared file system
2. **Except weight**: downloaded once and mounted by `--bind`, never embedded in the image
3. **Job Slurm**: reserve GPU, CPU and memory, then launch `apptainer exec --nv` in the job
4. **Check CUDA and driver**: the image must be compatible with the node driver ([[09-gpu-containers|GPU in container]])
5. **Expose service**: port accessible from the connection node, or batch processing rather than permanent service

**Field**: Launch a permanent inference server on a cluster whose jobs have a maximum duration.

---

Scenario: your laboratory hesitates between an HPC cluster in Slurm and a Kubernetes cluster to serve models. What criteria do you propose? <!--anki:513e6d4b3132634e4077-->
?
1. **Load nature**: batch and scheduled calculation for HPC, permanent service and continuous traffic for Kubernetes
2. **Security model**: Apptainer is rootless and demon-free, designed for multi-user clusters
3. **What's missing in HPC**: autoscaling, ingress, automatic restart, progressive deployments ([[12-kubernetes-gpu-inference|K8s GPU]])
4. **What already exists**: equipment, team, scheduler and skills in place often weigh more than technique
5. **Frequent mixed solution**: HPC training and batch, online service on Kubernetes

**Pip**: turn an HPC cluster into an online service platform, with jobs relaunched in a loop.

---

## Sources

- [Apptainer — access to GPU devices and libraries](https://apptainer.org/docs/user/main/gpu.html)

- [Apptainer — GPU support, user guide 1.5](https://apptainer.org/docs/user/1.5/gpu.html)

## Connections
- [[06-apptainer-singularity|Apptainer & Singularity]] — bases & format SIF
- [[09-gpu-containers|GPU in container]] — `--nv` vs `--gpus`
- [[11-llm-inference-servers|Inference Servers]] — what we run
- [[12-kubernetes-gpu-inference|Kubernetes GPU]] — alternative cloud/cluster
- [[00-index|Index Containers]]
- [[00-moc-ai-engineering|MOC AI Engineering]]
