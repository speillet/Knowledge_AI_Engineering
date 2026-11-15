# Containers & infra — Index — Flashcards
Tags: #flashcards #moc #containers #docker #kubernetes #gpu
<!-- summary: Summary of 13 section cards, chains to remember, and maps on container interest to serve models, start test on the actual target, deployment responsibilities, configuration control. -->


Sub-map of the section **70 — Containers & Infra**: from container to GPU, to deploy models.

## List of series

### Fundamentals
- [[01-oci|01 — OCI]] — the standard for images and runtimes
- [[02-docker-images-registries|02 — Docker, images & registries]] — build and distribute
- [[08-linux-primitives-docker-fundamentals|08 — Linux primitives & Docker fundamentals]] — namespaces, cgroups, volumes

### Runtimes & orchestration
- [[03-containerd-runc|03 — containerd & runc]] — the execution chain
- [[04-kubernetes-kubelet-cri|04 — Kubernetes, kubelet & CRI]] — l'orchestration
- [[05-docker-kubernetes|05 — Docker & Kubernetes]] — history of dockershim

### Inference LLM
- [[09-gpu-containers|09 — GPU in container]] — give access to the GPU
- [[10-images-models-weights|10 — Model Images & Weights]] — packager models of several GB
- [[11-llm-inference-servers|11 — LLM Inference Servers]] — what we run (vLLM, TGI...)
- [[12-kubernetes-gpu-inference|12 — Kubernetes GPU & inference]] — allocate and share GPU

### HPC
- [[06-apptainer-singularity|06 — Apptainer & Singularity]] — HPC Containers
- [[13-apptainer-inference-hpc|13 — Apptainer & HPC Inference]] — serve models on a cluster

### Revision
- [[07-containers-overview|07 — Synthesis]]

## Chains to remember
```text
Kubernetes → kubelet → CRI → containerd → runc → Linux kernel
Dockerfile → build → image OCI → registry → pull → runtime → Container
```

GPU access: Docker `--gpus` · Apptainer `--nv` · Kubernetes `nvidia.com/gpu`

---

## Cards

Why have containers become the standard for serving models? <!--anki:45514a373c635d6d4a50-->
?
They bundle **server and application dependencies** into a versioned artifact, transportable between compatible and orchestral environments, especially on Kubernetes. They **do not freeze the whole machine**: kernel, driver GPU, hardware and volumes remain external.

Example: Returning the old image does not restore the old model if the mounted weights have changed. A reliable rollback must identify **image by digest, weight review, tokenizer and configuration**, and then verify their compatibility with the host.

Test a representative start and inference on the target; a successful build does not validate either access to the GPU or the required memory ([[09-gpu-containers|GPU in container]]).

---

What boot test distinguishes a valid container image from a usable inference service? <!--anki:6239363366343864343265383437316639613834316334373436653763656665-->
?
Make a **start on the actual target**, Then there is a representative inference. Check loading weights, Access GPU, tokenizer, Expected output and memory margin; A living process does not prove that the model is ready.

Measure separately download, initialize and first request, then test restart with cold cache. Keep versions of image, model and driver. This end-to-end test completes container compliance: a correct image may remain unusable due to lack of weight, capacity or hardware compatibility.

---

## Scenarios

Scenario: the same inference image gives two different behaviors in recipe and in production. How do you organize the diagnosis between teams? <!--anki:6165623633333832373235303465666639636633613166303333613962623238-->
?
1. **Compare actual manifests**: digest, weight, tokenizer, configuration and edits, not just the advertised tag.
2. **Replay an identical request** and locate the first divergence: serialized input, loading, calculation or network output.
3. **Assign verification to the right owner**: packaging, infrastructure or application, by sharing the identifiers of the execution.
4. **Confirm the fix** on the target and add the case to release control.

A running status does not prove that good artifacts are loaded or that their behavior is identical.

---

## Connections
- [[12-kubernetes-gpu-inference|Kubernetes GPU & inference]] — application topic
- [[83-gateway-ingress|Ingress & API gateway]] — Cluster Network Input
- [[00-moc-ai-engineering|MOC AI Engineering]]
