# Docker & Kubernetes — Flashcards
Tags: #flashcards #docker #kubernetes
Verified on: 29 September 2026 — This factsheet lists products, versions or regulatory texts that are evolving quickly.
<!-- summary: Dockershim and its removal, current architecture, Docker images executed without Docker Engine, scream-dockerd, checks before removing Docker Engine, build of images without daemon (BuildKit rootless, Buildah), validation of Kubernetes execution conditions, UID and permissions, derives configurations. -->


Historically, how did Kubernetes communicate with Docker Engine? <!--anki:41645a73796a5a6f502a-->
?
By **dockershim**, an adapter built into the kubelet that translated the [[04-kubernetes-kubelet-cri|CRI]] to the API Docker Engine: `kubelet → dockershim → Docker Engine → containerd → runc`.

This adaptation was necessary because Docker Engine did not directly implement the CRI. Removing this built-in link does not mean removing the compatibility of images built with Docker: a compatible CRI runtime can use them.

Example: Migrating a node to containerd changes the run layer and its diagnostic tools, not necessarily the Dockerfiles of applications, but check for dependencies on the Docker socket, log paths, and runtime configuration.

---

Why did dockershim exist? <!--anki:746b7c73773064733f75-->
?
Because Docker Engine, prior to Kubernetes, does not expose the **CRI** interface. When the CRI appeared (to open Kubernetes to multiple runtimes), it was necessary to continue to run the existing clusters, all based on Docker.

Dockershim translated kubelet requests to Docker Engine. This adapter was about **runtime**, not image format. Its presence added a layer to maintain between Kubernetes and the underlying runtime.

---

Does Kubernetes still use dockershim natively? <!--anki:4d476c304a577c7d336d-->
?
**No**, it has been removed in the **1.24 version** (2022). Clusters now speak directly to a CRI-compatible runtime. What has disappeared is **shortcut to Docker Engine**, not compatibility with Docker images.

During a migration, look for dependencies on the Docker socket, log paths, and operating tools. A standard application image may remain the same, while an agent that mounts `/var/run/docker.sock` requires an adaptation.

---

Without dockershim, which execution string is common today on a Kubernetes node? <!--anki:464d5d4f407e2a234050-->
?
`kubelet → CRI → containerd (or CRI-O) → runc → Linux kernel`

Practical consequence: on a node, we debug with **`crictl`** and not `docker ps`, and there is **no Docker** daemon to query.

To find out what is actually running, `kubectl get nodes -o wide` displays in the `CONTAINER-RUNTIME` column the runtime of each node and its version, such as `containerd://…` or `cri-o://…`. Logs read with `crictl logs` or in `/var/log/pods/`, not with `docker logs`.

---

Do not confuse: “Kubernetes no longer supports Docker” and “Docker images no longer work”? <!--anki:6b3f563246555e212c79-->
?
- What has been removed: **dockershim**, so support for **Docker Engine as node runtime**
- What has never changed: the **images**, compliant with the [[01-oci|OCI]], run perfectly via containerd

This is the most common confusion on the subject: it is about the **runtime**, not the **image format**.

Check architecture, system and GPU access before promising that an image will work: format compatibility does not mean compatibility with any machine or configuration.

---

What is cri-dockerd? <!--anki:45314f337346634d2a34-->
?
**cri-dockerd** is an external adapter that translates CRI requests from Kubernetes to Docker Engine. It allows you to continue using this engine after removing the dockershim integrated in Kubernetes.

This option can respond to an existing dependency; it adds a component to configure and maintain. Compare with containerd or another CRI implementation based on support, exploitation and actual need. A tool that uses the Docker socket does not work automatically in all Kubernetes environments. The choice of runtime does not require reconstructing an OCI-compatible image, but platform constraints and external dependencies remain to be tested.

---

What to check before removing Docker Engine from cluster nodes? <!--anki:4c7424507a3764573976-->
?
Everything that depends **the Docker Demon** rather than Kubernetes:
- **`/var/run/docker.sock`** mounts: monitoring agents, log collectors, CI jobs that build images
- **Tools that read logs** in Docker's `json-file` format, while the CRI writes in its own format
- **Operating scripts** that call `docker ps` on nodes, to be replaced by `crictl`

The **images** do not change ([[03-containerd-runc|Containerd Tools]]).

---

How to build images in a cluster without Docker Engine? <!--anki:4a432a255d78575b7b42-->
?
With a manufacturer that **does not need the Docker daemon** nor the socket of the node:
- **BuildKit** in **rootless** mode, Pod mode or shared service
- **Buildah**, no demon, running in the Red Hat ecosystem

All of them produce standard **OCI** images, pushed into the registry as before ([[02-docker-images-registries|registries]]), thus avoiding mounting `docker.sock`, which in practice gives root access to the node.

---

Why is a local Docker test not enough to validate a Kubernetes deployment? <!--anki:3361376364343835653661643437306539636330343432366538643933663831-->
?
The **execution context** changes: identity, file system, network, resources, and life cycle. A local container launched with all privileges may fail in a restricted Pod.

Replay the expected conditions: non-privileged user, real volumes and rights, memory limits, injected secrets and graceful shutdown. Test download weights and access GPU on the target cluster. Finally check Service and progress. A common image facilitates the transfer, but does not automatically reproduce the contracts that Kubernetes imposes around the process.

---

Why can a container that runs as root locally fail under Kubernetes with an unprivileged user? <!--anki:3761323631653039303330313437393762356238336235616636373339643761-->
?
The application can try to write in **a directory belonging to root**, to access a device or use an unallocated ability.

Test the same UID, mounts, and restrictions before deployment. Explicitly prepare the necessary writable directories. Restoring root to “fix” startup may hide an avoidable dependency; correcting permissions at the useful perimeter.

---

Why keep Kubernetes manifests in addition to the Dockerfile to reproduce a service? <!--anki:3430373035333938303961353436376662353338623261323364346531336638-->
?
The Dockerfile does not describe **injected secrets, resources, mounts, probes, and network rules** of the deployment. These settings can change the behavior without changing the image.

Version configuration manifests and references, then check the actual state of the cluster. Keep sensitive values in a suitable mechanism rather than in Git. A difference between declared configuration and applied configuration must be detectable.

---

## Scenarios

Scenario: a developer says that you have to rewrite the images in "Kubernetes format", since Docker is no longer supported. What do you say? <!--anki:7454446b3b373b56544b-->
?
1. **Distinguish**: What was removed was **dockershim**, the layer that allowed the kubelet to drive Docker Engine
2. **Recall current architecture**: `kubelet → CRI → containerd → runc`
3. **Conclusion** The images remain **OCI Images**, built with Docker or something else, and run without Docker Engine
4. **What really changes**: Debug commands on nodes, and tools that spoke to the Docker daemon
5. **What to check**: no use of the Docker socket in Pods, convenient to ban anyway

**Trap**: confuse the image format and the runtime that runs it.

---

Scenario: a CI job builds images by mounting the node's Docker socket into a Pod. What risks and alternatives? <!--anki:456a383b786342397943-->
?
1. **Major risk**: access to the node socket returns root access to this node, for all containers that run on it
2. **Deprecated dependency**: Modern nodes often no longer have a Docker daemon
3. **Alternatives**: constructors without a daemon, in user space (Kaniko, Buildah, BuildKit in rootless mode)
4. **Isolate**: Build on dedicated nodes, with limited registry tokens
5. **Sign** the images produced and pin the digests ([[105-agentic-ai-devsecops|Supply Chain]])

**Trap**: Consider this edit as a simple implementation detail of the CI.

---

## Sources

- [Kubernetes — Official Dockershim Removal FAQ](https://kubernetes.io/blog/2022/02/17/dockershim-faq/)

## Connections
- [[04-kubernetes-kubelet-cri|Kubernetes, kubelet & CRI]] — CRI context
- [[03-containerd-runc|containerd & runc]] — the replacement of dockershim
- [[02-docker-images-registries|Docker & images]] — images OCI portables
- [[00-index|Index Containers]]
- [[00-moc-ai-engineering|MOC AI Engineering]]
