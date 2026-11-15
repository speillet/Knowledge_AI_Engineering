# Kubernetes, kubelet & CRI — Flashcards
Tags: #flashcards #kubernetes #containers #infra
<!-- summary: Pod, Deployment, Service, control plane, kubelet, CRI (containerd, CRI-O), schedule, requests and limits, probes, startup, readiness and liveness, graceful shutdown, eviction and OOM. -->


What is Kubernetes? <!--anki:727e3f4d405d3b296743-->
?
A **container orchestrator** the State of the **Desired state** (What applications, How many replicas, what resources) and controllers **Continuously maintain** (Restarting, placement, Scaling).

If a Pod disappears, the controllers try to restore the requested number; the scheduler chooses a node and the kubelet launches the containers. Kubernetes automates this reconciliation, but does not guarantee that a replicated application is correct. Readiness, resources, storage and business logic remain to be configured.

---

What is a Pod? <!--anki:7850754b2339264c582f-->
?
The **Kubernetes Smaller Deployable Unit** : containers co-located on a node, share the network and can mount common volumes. Their root file systems are not automatically shared.

Example: an init container downloads the [[10-images-models-weights|poids]] into a volume that the server then mounts; a sidecar can join this server via `localhost`.

The Pod is ephemeral, but **not entirely immutable**: some fields can be changed. A deployment template change usually replaces the Pods. A recreated Pod has a new identity; keep the necessary data in suitable storage, not just in its local file system.

---

What is the role of a Deployment? <!--anki:62577b514a5248636034-->
?
Manage a set of identical **Pods** (via a ReplicaSet): number of replicas, **rolling updates** and rollback.

In a new version, the Deployment adjusts the ReplicaSets to gradually replace the Pods according to the chosen policy. It is suitable for services whose instances are interchangeable. A rollback restores a previous configuration; it does not automatically restore a database or the effects already produced by the new application.

---

What is a Kubernetes Service? <!--anki:4c2d5e652833592c4a4e-->
?
To provide a stable **address** (virtual IP and DNS name) in front of ephemeral Pods, with **load allocation** between them.

A Service selects endpoints corresponding to the expected Pods and hides their address changes. In the current case `ClusterIP`, the address is internal to the cluster; the external exposure requires an additional mechanism. A Headless Service is a different case, without a virtual IP. The readiness helps to exclude unready instances.

---

What is in the Kubernetes plane control? <!--anki:484723506a4126657e57-->
?
- **kube-apiserver**: entry point for all operations
- **etcd**: key-value base of the cluster state
- **kube-scheduler**: choose the node of each Pod
- **controller-manager**: reconciliation loops

The scheduler decides the placement; the controllers reconcile the desired state; the kubelet executes the execution on the node. The API server centralizes exchanges and permissions. A failure of the control plane can prevent new decisions without immediately stopping all containers already running.

---

What is the role of kubelet? <!--anki:526151232c463e387774-->
?
The **agent present on each node** : it receives the assigned Pods, ask the runtime **Launch the Containers**, monitor their health (probes) and **Resurrect their state** At theAPI server.

The kubelet does not usually choose which node to place the Pod on: this decision comes from the scheduler. It locally translates the PodSpec into runtime operations, mounts the necessary resources and applies the procedures. To diagnose a failed launch, consult Pod events, node state and runtime messages.

---

What is CRI? <!--anki:792f3230294d735a244f-->
?
The **Container Runtime Interface**: the API (gRPC) by which the kubelet drives **any compatible runtime**, such as **containerd** or **CRI-O**. Direct Docker support (dockershim) has been removed in v1.24.

It separates Kubernetes from the concrete implementations of the runtime: the kubelet requires for example the preparation of a sandbox or the launch of a container. An image built with Docker remains usable after the removal of dockershim. Do not confuse CRI with OCI, which describes in particular the format of the images and the low-level execution.

---

How does the scheduler choose a node? <!--anki:6f6d4e346d365b51612c-->
?
It **filters** the nodes capable of hosting the Pod (requested resources, node selectors, tints/tolerations, affinities), then **notes** the remaining candidates and takes the best.

In particular, it uses declared **requests**, not just the instant consumption of existing Pods. If no node satisfies the constraints, the Pod remains Pending. Check schedule events before adding resources: incompatible affinity or lack of toleration may be the real cause.

---

Do not confuse: requests and limits? <!--anki:6257312a413972352b79-->
?
- **Requests**: resources **reserved**, used by the scheduler to place the Pod
- **Limits**: **Usage ceiling**; memory overrun → **OOMKilled**, overrun CPU → idle (throttling)

For CPU and memory, requests are used for placement and relative guarantees; the container can consume more if available and allowed. A memory limit is not an additional reservation. The GPU exposed as extended resources follow other rules: they are usually requested in integer units and their requests and limits must coincide.

---

What is a DaemonSet? <!--anki:647c2c386d5138336533-->
?
A controller that launches **a Pod on each node** (or each selected node): log agents, monitoring, or the **NVIDIA device plugin** ([[12-kubernetes-gpu-inference|GPU]]).

When an eligible node joins the cluster, the controller creates the corresponding Pod. This is suitable for the services attached to the machine, not for an arbitrary number of application replicas. Selectors, stains and tolerations remain important to deploy a GPU agent only on the nodes concerned.

---

Why are processes important for a LLM server? <!--anki:622e723e7a6d7d574d23-->
?
An inference server takes **several minutes to load weights**: a **startupProbe** prevents it from being killed during loading, and the **readinessProbe** only sends traffic to it once it is ready.
```yaml
startupProbe:                 # tolerates 10 min loading
  httpGet: { path: /health, port: 8000 }
  failureThreshold: 60
  periodSeconds: 10
readinessProbe:               # sends traffic only when the model is loaded
  httpGet: { path: /health, port: 8000 }
```
Without startupProbe, a **livenessProbe that is too impatient** can restart the container in a loop. Verify that `/health` not only declares the process alive: the readiness must reflect the ability to serve the model. A transient overload is not necessarily a reason for restarting.

---

Do not confuse: Service and Ingress? <!--anki:4e357775664e4c37644a-->
?
- **Service** A stable address **Inside** cluster (virtual IP and DNS name) in front of ephemeral Pods, with load distribution
- **Ingress** The entrance **from the outside** in HTTP(S), which leads to Services according to the host and the path ([[83-gateway-ingress|Ingress]])

A **ClusterIP** service does not directly expose the Internet; **NodePort** or **LoadBalancer** types can provide external access depending on the network. An Ingress requires a controller to enforce its rules.

To diagnose a failure, first test the Pod, then the Service, and then the external entry: a DNS or TLS error does not have the same fix as an unready backend.

---

Why distinguish startup, dreaminess and liveness for a long model to load on Kubernetes? <!--anki:3538313238666534653361363464643138313138343637633839656364613939-->
?
The **startup probe** protects the startup phase; the **readiness probe** determines whether the Pod can receive Service traffic; the **liveness probe** triggers a restart when its failure exceeds the configured threshold.

A model may need several minutes to accept a request. Using too aggressive liveness during this phase can cause a loop of restarts. After startup, test a readiness related to the ability to serve and prevent a momentarily slow dependency from causing cascading restarts.

---

Why remove a Pod from traffic before completing its inference process? <!--anki:6530303638363661663865613465623661643933623130613335306465306562-->
?
It is necessary to **stop admitting new requests and then drain the current ones**. Otherwise, accepted streams just before the stop are cut.

Coordinating readiness, network propagation, and termination time with the server. A grace period does not guarantee that the program is properly managing SIGTERM. Testing active streams during a deployment, including forced termination when the timeout is exhausted.

---

Do not confuse: OOMKilled of a container and eviction of a Pod under pressure from the node? <!--anki:6632346365653637626161623465383162316534383439323034313962633561-->
?
A **OOM kill** is a memory-related kill; a **eviction** is a decision of the kubelet in the face of resource pressure, such as memory or disk.

Examine the node's reason, events, and metrics to distinguish the causes. Increasing the container's memory limit does not resolve a saturated disk or necessarily a global pressure. Automatic restarting may mask the repetition of the problem without correcting it.

---

## Scenarios

Scenario: your Pod vLLM is killed and restarted in a loop at startup, even before you have responded to a request. What do you check? <!--anki:46422c54432f78477a62-->
?
1. **Probes**: Without **startupProbe**, the livenessProbe kills the container while loading the weights, which takes several minutes
2. **The rearinessProbe**: it should only go green once the model is loaded, so as not to receive traffic too early
3. **Memory**: a `OOMKilled` indicates a memory limit that is too low, not a problem of probe
4. **Resources**: consistent requests and limits, well-requested GPU ([[12-kubernetes-gpu-inference|K8s GPU]])
5. **Logs and events** of the Pod, to distinguish startup failure and health failure

**Trap**: Extend the timeline of the livenessProbe instead of using a startupProbe.

---

Scenario: one team asks why its GPU Pods remain on hold while the cluster “has free GPUs.” How do you explain the placement? <!--anki:495e636128334b48256a-->
?
1. **The scheduler filters and then notes**: it only retains nodes that can accommodate the Pod
2. **Resources requested**: A GPU explicitly requests itself as a resource, and it is not shareable by default
3. **Taints and tolerations**: GPU nodes are often tinted to accommodate only the loads concerned
4. **Requests too high**: memory or CPU requested beyond what a node can offer
5. **Check** for Pod events, which indicate the exact reason for rejection per node

**trap**: Watch the actual use of nodes rather than their resources **reserved**.

---

## Sources
- [Kubernetes — Pods, updates and replacements](https://kubernetes.io/docs/concepts/workloads/pods/) — targeted consultation of 6 November 2026.

- [Kubernetes — Pod life cycle and probes](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/) — targeted deepening of the 12 November 2026; educational examples are built for this review.

- 14 November 2026 — Pod completion: [Kubernetes — Pod Lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/).

- 14 November Supplement 2026 — Resource Pressure Eviction: [Kubernetes — Node-pressure Eviction](https://kubernetes.io/docs/concepts/scheduling-eviction/node-pressure-eviction/).

## Connections
- [[00-index|Index Containers]] — containers, OCI, Docker
- [[09-gpu-containers|GPU in container]] — what the runtime should expose
- [[12-kubernetes-gpu-inference|Kubernetes GPU & inference]] — the application to LLM
- [[83-gateway-ingress|Ingress & API gateway]] — expose the Services
- [[01-oci|OCI]] — not to be confused with CRI
- [[03-containerd-runc|containerd & runc]] — the runtime behind CRI
- [[05-docker-kubernetes|Docker & Kubernetes]] — history of dockershim
- [[07-containers-overview|Container Synthesis]] — from `kubectl apply` to process
- [[11-llm-inference-servers|Inference Servers]] — vLLM, SGLang, TensorRT-LLM and their setting
- [[00-moc-ai-engineering|MOC AI Engineering]]
