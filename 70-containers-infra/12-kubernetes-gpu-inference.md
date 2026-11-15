# Kubernetes, GPUs & inference — Flashcards
Tags: #flashcards #kubernetes #gpu #llm #inference
Verified on: 25 September 2026 — This factsheet lists products, versions or regulatory texts that are evolving quickly.
<!-- summary: device plugin, `nvidia.com/gpu` resource, MIG, time-slicing, KServe, autoscaling (HPA, KEDA), scale-out pressure on storage, rollout capacity, careful scale-down. -->


How does [[04-kubernetes-kubelet-cri|Kubernetes]] allocate GPU to Pods? <!--anki:782d706f674268736979-->
?
Via the **NVIDIA device plugin**, deployed in **Daemon Set** : he discovers them GPU of each node, on the **Announcement at Kubelet** as a resource `nvidia.com/gpu`, and provides the runtime with devices to inject when a Pod requests it. Then the scheduler does nothing but **Whole Arithmetic** on this resource.

In practice, it is installed via the **GPU Operator**, which also supports driver, toolkit, DCGM metrics and MIG configuration ([[09-gpu-containers|GPU in container]]).

---

How do I request a GPU for a container in Kubernetes? <!--anki:6f716621355b686f6048-->
?
By declaring the resource **`nvidia.com/gpu`** in the `resources.limits`.

```yaml
resources:
  limits:
    nvidia.com/gpu: 1
```

The node must announce this resource via a configured device plugin. For an extended GPU resource, the limit serves as a request if it is omitted; if both are set, they must be equal. Without an eligible ability, the Pod remains Pending. The request allocates an advertised unit, whose meaning depends on the configured share.

---

Can a GPU be shared between multiple Pods by default? <!--anki:4f2d4d2f21696245696b-->
?
**No.** The `nvidia.com/gpu` resource is **entire and exclusive**: you cannot ask for "0.5 GPU". A Pod that gets the GPU keeps it for itself, even if it only uses it at 10%.

Three ways to share:
- **MIG**: partitions **materially isolated** (dedicated memory and calculation)
- **Time-slicing**: several Pods take turns on the GPU, **without memory isolation**
- **MPS**: concurrent execution of kernels, for trusted loads

---

What is MIG (Multi-Instance GPU)? <!--anki:6e4870724d693d6c2b2a-->
?
An NVIDIA technology that physically **partitions** a GPU (A100, H100, H200, B200) into **isolated instances**, each with its memory and computing units. Each instance appears as a separate GPU and is therefore assignable to a different Pod.
```text
A100 80 GB → up to 7 instances (1g.10gb, 2g.20gb, 3g.40gb...)
```
Interest: serve several **small models** or test environments without them bothering. Limit: profiles are **set in advance** and reconfigure it requires emptying the node.

---

Do not confuse: MIG and time-slicing? <!--anki:6b3b5f755d694f4f6851-->
?
- **MIG**: isolation **hardware**. Dedicated memory, predictable performance, number of instances limited by profiles
- **Time-slicing**: simple **time-sharing**. No memory isolation, one Pod can saturate VRAM and knock others down, but sharing is flexible and without reconfiguration

Rule: **MIG for multi-tenant production**, time-slicing for development or tolerant loads.

Check that the MIG profile really holds weight and KV of the model; a partition too small remains unusable despite its isolation. Time-slicing increases the admitted consumers, not the available VRAM nor the physical power.

---

What are node selectors, tints, and tolerations for the GPU? <!--anki:786472704640764f4057-->
?
To **target and reserve GPU** nodes:
- **Node selector or affinity**: "place me on a node that has H100s." It's the Pod that **chooses**
- **Taint on the node**: "No one comes here without being invited." This is the node that **repeats**
- **Toleration on the Pod**: the pass that allows you to ignore the stain

Without tincture, Charges without GPU come to occupy the memory and CPU machines worth tens of thousands of euros. The GPU Operator of the **Labels** (Model of GPU, MIG profile) directly operable by the selectors.

---

What are KServe and Kubeflow? <!--anki:63503c706e2e62445352-->
?
**KServe** provides a layer of serving Kubernetes, especially with `InferenceService`; **Kubeflow** bundles larger MLOps components: notebooks, pipelines, drive and tuning.

Autoscaling, canary, and scale-to-zero depend on the deployment mode and configured components: these are not automatic warranties.

Example: returning from zero replicas requires recovering the weights and initializing the engine; an interactive SLO may require hot replicas despite a scale-to-zero option.

Comparing the need for standardization to the cost of operation. A vLLM deployment with suitable routing may be enough; the platform does not choose a good [[66-prefix-caching-radix-attention|routage cache-aware]] alone.

---

How do I manage the variable load of an inference service on Kubernetes? <!--anki:4b5451773748245e6355-->
?
By the **Autoscaling** decode work **HPA** on custom metrics, or **KEDA** to connect directly to Prometheus. We scale on the **queue** and the **occupation of KV Cache**, not on the use GPU ([[93-monitoring-inference|Metric]]).
```yaml
resources:
  limits:
    nvidia.com/gpu: 1        # unit announced by the device plugin
nodeSelector:
  nvidia.com/gpu.product: NVIDIA-H100-80GB-HBM3
tolerations:
  - key: nvidia.com/gpu
    operator: Exists
```
The **scale-to-zero** is only valid if you accept a **cold start** of several minutes ([[10-images-models-weights|cold start]]).

The requested resource only guarantees physical exclusivity without sharing configured. The YAML places a Pod; it does not define the HPA. Also size a hot reserve to cover the time of arrival of a new replica.

---

Why is GPU management so important in inference on Kubernetes? <!--anki:697851257b26396e486d-->
?
Because the **GPU is a rare and expensive resource**: its allocation and sharing condition the cost and density of the service.

A too large allocation immobilizes the capacity; poorly controlled sharing degrades the memory and latency of neighbors. Choose GPU integer, hardware partition or time sharing according to the need for isolation. Follow usage, memory, queue and useful throughput to verify that the density obtained complies with the SLO.

---

What happens if a Pod requests a GPU when no node has one? <!--anki:3663623037653831613230613465336462336361666463326631393961353562-->
?
The Pod remains **Pending** (`Insufficient nvidia.com/gpu` event). If a cluster autoscaler is configured, it adds a GPU node, but it takes **several minutes**: VM startup, driver, image pull, load weights ([[10-images-models-weights|cold start]]).

During this time, requests wait or fail. Parades: a **margin** of capacity, an anticipated load on the queue, and GPU reserved for critical services.

---

Why can adding a GPU replica increase the pressure on shared storage first? <!--anki:3633656237613561353231363462316561643930626139386334333439633130-->
?
A **new replica** often has to read the same large weights before serving. Several simultaneous starts compete for network and storage, which can lengthen the load of all Pods.

Measure cold start under concurrency, provide a local cache or controlled preparation and adjust the scale-out speed. The readiness must reflect the actual load. Include this duration in the sizing: a theoretical capacity available after ten minutes does not resolve a burst that lasts thirty seconds.

---

Calculation: a service uses 4 Pods of one GPU each and the deployment imposes an additional temporary Pod without unavailability. The cluster only has 4 GPU free for this service. Why can rollout remain blocked? <!--anki:6331613832353565366464613461383561393434666231363761373638653064-->
?
It is temporary **5 GPU**, while only 4 is available. The new Pod remains Pending as long as no resources are released.

Provide surge capacity, other compatible pool, or policy that accepts controlled downtime. Also check for placement constraints. The total number of GPUs in the cluster is not enough if some nodes are not eligible for the image or model.

---

Why stabilize the scale-down decisions of a GPU service? <!--anki:3365313336376433393832613461343261663964386364666162656163393866-->
?
A temporary drop can result in **deletion and then costly** recreation of Pods, with loading weights and warming caches. This back and forth degrades latency and cost.

Use a stabilization window, a justified minimum capacity, and active query drainage. Measure the cost of unoccupied GPU against the cost of restarts and violations of SLO. The correct policy depends on the traffic profile, not a universal CPU threshold.

---

## Scenarios

Scenario: your inference service runs on 4 GPU A100 permanently reserved, but the traffic is focused on the office hours. How do you reduce the bill without breaking the service? <!--anki:474124573d3839286841-->
?
1. **Measure real profile**: traffic per hour, top concurrency, SLO to hold ([[64-inference-metrics-slo|SLO]])
2. **Autoscaling** on the queue and occupation of the KV cache, not on the use GPU
3. **Anticipate the cold start**: several minutes to load the weights, so keep a base of hot replicas ([[10-images-models-weights|cold start]])
4. **Scale-to-zero** only for non-critical environments (preproduction, batch)
5. **Densifier**: MIG for small models, quantization to fit on less than GPU ([[68-quantization|quantization]])

**Trap**: a scale-to-zero in production that charges several minutes of waiting time to the first user in the morning.

---

Scenario: Several teams want to deploy their models on the same GPU cluster, and compete for resources. How do you organize sharing? <!--anki:76356329543d292b5349-->
?
1. **Reserve GPU** nodes to affected loads with tints and tolerations
2. **Quotas per namespace**: number of GPUs per team, rather than a first-come race
3. **Fine sharing**: MIG to isolate instances, time-slicing only for tolerant loads
4. **Priorities**: priority classes and pre-emption for critical loads
5. **Visibility**: consumption and cost per team, otherwise nothing changes ([[122-finops-llm|FinOps]])

**Hip**: Let each team request “1 GPU” for inactive services half the time.

---

## Sources

- [Kubernetes — GPU Planning](https://kubernetes.io/docs/tasks/manage-gpus/scheduling-gpus/)

## Connections
- [[04-kubernetes-kubelet-cri|Kubernetes, kubelet & CRI]] — base d'orchestration
- [[09-gpu-containers|GPU in container]] — GPU
- [[11-llm-inference-servers|Inference Servers]] —
- [[10-images-models-weights|Images & poids]] — pull time big pictures
- [[83-gateway-ingress|Ingress & API gateway]] — network input of the serving
- [[64-inference-metrics-slo|Metrics & SLO]] — autoscaling signals
- [[122-finops-llm|FinOps LLM]] — the cost of the GPU idle
- [[00-index|Index Containers]]
- [[93-monitoring-inference|Monitoring of inference]] — metric GPU (DCGM) and autoscaling signals
- [[69-roofline-prefill-decode|Disaggregation prefill/decode]] — two pools to be autoscaled separately
- [[112-model-cicd|CI/CD models]] — eval gates, canary and rollback
- [[13-apptainer-inference-hpc|Apptainer & HPC Inference]] — serve a model on a Slurm cluster
- [[136-mixture-of-experts|Mixture of Experts]] — total and active settings
- [[61-kv-cache-attention|KV cache]] — memory that limits concurrency
- [[62-inference-optimizations|Inference optimizations]] — latency and throughput levers
- [[00-moc-ai-engineering|MOC AI Engineering]]
