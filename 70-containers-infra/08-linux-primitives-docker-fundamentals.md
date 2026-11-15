# Linux primitives & Docker fundamentals — Flashcards
Tags: #flashcards #containers #linux #docker
<!-- summary: namespaces and cgroups, container or VM, layers, Dockerfile and cache order, volumes and bind mounts, port mapping, distinction between RAM and VRAM, PID 1 and signals, disk and inodes. -->


What Linux kernel primitives do containers rest on? <!--anki:6c342463685269653428-->
?
**namespaces** and **cgroups**, supplemented by security mechanisms: **capabilities**, **seccomp** (system call filtering), **AppArmor or SELinux**, and a **overlay** file system for layers.

A container is not **not an object of the kernel** : it is an **Ordinary Process** assembled from these bricks by a runtime like [[03-containerd-runc|runc]].

It shares the host's kernel: packaging an Ubuntu user space does not provide a separate Ubuntu kernel, so a kernel feature or flaw remains a host subject, unlike a Python dependency contained in the image.

---

What are namespaces for? <!--anki:6a65563352482663542e-->
?
To **isolate what a process sees**, each type covering a resource:
```text
pid → process tree (the container sees its own PID 1)
net → interfaces, ports, routing table
mnt → mount points, so the file tree
the → Hostname
ipc → shared memory, message queues
user → UID mapping (rootless mode database)
cgroup → view of cgroups
```
That's why two containers can listen to the conflict-free **port 8000**.

The absence of conflict implies **separate network namespaces**. With a shared network, especially between containers of the same Pod, Ports may be in conflict. Namespaces do not constitute complete virtualization: processes share the host kernel and isolation depends on the spaces actually configured.

---

What are cgroups used for? <!--anki:4a2c613b3d4068604965-->
?
To **Limiting and allocating resources** that a process consumes (CPU, memory, I/O, access to devices such as the [[09-gpu-containers|GPU]]).

A CPU limit can cause throttling; a memory limit can lead to a shutdown for lack of memory. Device access control does not automatically partition VRAM or the GPU calculation: this sharing requires specific mechanisms.

---

Which sentence can remember the namespaces / cgroups difference? <!--anki:4351766a67394b416049-->
?
**Namespaces isolate (what you see); cgroups limit (what you consume).**

Example: A PID namespace hides the processes of other groups, while a memory cgroup limits the usable quantity. A container can therefore have an isolated view without a strict memory limit, or a limit without an isolated network. Both mechanisms complement each other with permissions, capabilities and system call filtering.

A process can see few neighbors while consuming all of the allowed RAM. For an OOM, look at the limit of the cgroup and its usage, not just the free memory displayed on the host.

---

Is a container a virtual machine? <!--anki:46582f686d7b712e5b5b-->
?
**No.** A container **shares the host's kernel** and isolates only processes; it does not emulate hardware or a complete operating system, and starts in seconds. A **VM** embeds **its own kernel** on a hypervisor: stronger but heavier isolation.

Shared Kernel Consequences: A Linux container does not run natively on Windows or macOS, where Docker Desktop starts a Linux VM. A kernel flaw affects all containers on the host. And a kernel module, like the GPU driver, is on the host: you can't embed a different version of it per container.

---

What is an image layer? <!--anki:735f7a393c5b29347d70-->
?
A **read-only layer**; layers are stacked via a **union/overlay filesystem** to form the final image. The image is described by a **manifest** and identified by a **digest** (hash); layers common to multiple images are **shared and cached**.

Each `RUN`, `COPY` or `ADD` statement creates a layer. Delete a file in a subsequent layer the **mask** without reducing the image: a `RUN wget model.bin` followed by a `RUN rm model.bin` leaves the file in the previous layer, uploaded to each pull. Clean in the same `RUN` statement, or copy only the final result.

---

Why does the order of a Dockerfile's instructions influence the build? <!--anki:48487e3d602d24354b28-->
?
The builder reuses the results of steps whose instructions and dependencies have not changed. A change invalidates the relevant step and the steps that depend on it. The **RUN, COPY, or ADD** statements may change the file system; not all instructions create a file layer.

First copy the dependency file, install, and then copy the code avoids reinstalling each application change. Also pin the versions: an effective cache is not a guarantee of reproducibility.

---

Do not confuse: volume and bind mount? <!--anki:794d3870536e79555836-->
?
Both **continue data out of the container lifecycle**; a **volume** is managed by the runtime (location, backup, drivers); a **bind mount** mounts a specific path of the host.

A volume simplifies the management of storage by the engine; a bind mount is suitable for a specific local path, but couples the container to the host. The data is not saved automatically just because it is in a volume. For non-modifiable model weights, prefer a read-only mount.

---

Do not confuse: writeable layer and volume? <!--anki:4c2e7958784f645d4a5a-->
?
The **writable layer** belongs to the container's life cycle; its data is lost when it is deleted. A **volume or bind mount** keeps data out of that layer, subject to its own deletion policy.

Additional costs depend on the driver and access: copy-on-write can penalize certain writes, while a network volume can itself be slow. Measure actual storage. For shared bulky weights and persistent caches, prefer suitable external storage; embedding immutable weights in the image remains a possible choice with distribution tradeoffs ([[10-images-models-weights|Weight of models]]).

---

What is a Dockerfile? <!--anki:6641264b537b71293034-->
?
An image-building **recipe**: `FROM` chooses the base, `COPY` adds files, `RUN` executes a build step, `CMD` provides a default command on startup.

Example: install the dependencies with `RUN` entered them in the image; start the server with `CMD` starts it when creating the container, not during the build. `CMD` can be replaced at launch.

Pin base and dependencies, and limit the context of build. Copying a secret and then deleting it in a subsequent layer does not erase it from the image history; use the build's secret mechanisms rather than `COPY`.

---

What is port mapping (`-p`)? <!--anki:7366346b4c3365405e54-->
?
To **expose a port of the container on the host**, for example to make a [[11-llm-inference-servers|Endpoint of Inference]] accessible.

```bash
docker run -p 8000:8000 my-inference-server
```

The first number is the host port, the second is the container port. The application must listen on a reachable address in the container. Without explicit address, the port can be published on all interfaces; for local use, use `-p 127.0.0.1:8000:8000` and keep authentication suitable for the service.

---

Why does a container memory limit not automatically store GPU memory? <!--anki:3032646263336463396331373433393038333039336564353430376462666535-->
?
The usual **memory limits of the container** relate to the memory managed by the host system. The VRAM and its allocation depend on the GPU, the runtime and the mechanisms of sharing retained.

A process can meet its RAM limit while failing in VRAM, or vice versa while loading weights. Monitor RAM, pinned memory, and VRAM separately. Set GPU limits and isolation with the appropriate components, and then test multiple competing workloads. The only memory field in the container does not constitute a VRAM quota.

---

Why should the 1 PID process of a container handle child signals and processes? <!--anki:3936306633333238653437373432333838636536373861303462626437633234-->
?
It plays a special role in **stopping and recovering completed children**. A wrapper shell that does not transmit signals can prevent the server from draining its requests.

Use a launch chain that transmits signals correctly, with shell replacement or suitable init. Test SIGTERM and end of grace period. A container that stops only by SIGKILL has not demonstrated a clean application shutdown.

---

Why can a container receive "no space left on device" when there are still free gigabytes? <!--anki:3437363633656433316261643465626361353738613764333135623132353538-->
?
The file system may be missing **inodes**, needed to represent the files, or another partition may be full.

Examine space and inodes of the relevant mount, including writable layers and volumes. Identifying the file producer before cleaning. Adding RAM or expanding another partition does not correct this saturation.

---

## Scenarios

Scenario: Each `docker build` of your inference image takes 12 minutes, even when you change only one line of Python code. What do you fix? <!--anki:4a296074577b5d2d6763-->
?
1. **Understanding the cache**: Each statement creates a **layer**, and anything following a modified statement is reconstructed
2. **Reorder**: installation of dependencies (rarely modified) **before** copy of code
3. **Copy finely**: First the dependency file, then the rest of the code
4. **Multi-stage**: compile into a heavy image, deliver on a light run image
5. **Check** what goes into the build context (exclusion file), often the real cause of slowness

**Trap**: A copy instruction of the entire directory placed at the top, which invalidates the entire cache with each change.

---

Scenario: a security manager asks to execute the code generated by an agent "in a container, therefore isolated". What do you specify? <!--anki:513a6d74406e3c434175-->
?
1. **Remind reality**: a container **shares the kernel** of the host. Namespaces isolate the view, cgroups limit consumption
2. **What's missing**: A kernel flaw allows for escape, while a VM embeds its own kernel
3. **Strengthen**: gVisor or Kata for untrusted code, with an isolated kernel ([[103-agent-defenses|Defenses]])
4. **Complete**: no secrets in the environment, filtered outgoing network, ephemeral file system
5. **Limit consumption**: cgroups on CPU, memory and device access

**Trap**: Treat "containerized" as synonymous with "safe to run any code".

---

## Sources

- [Kubernetes — Container Resource Management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/) — targeted deepening of the 12 November 2026; educational examples are built for this review.

- [Docker — storage, writeable layers and drivers](https://docs.docker.com/engine/storage/drivers/) — targeted verification of 12 November 2026, without renewal of the global date of the topic.

## Connections
- [[03-containerd-runc|runc]] — configure namespaces & cgroups
- [[09-gpu-containers|GPU in container]] — cgroup devices for GPU
- [[10-images-models-weights|Images & poids]] — volumes for lifting weights
- [[02-docker-images-registries|Docker & images]] — layers & Dockerfile
- [[07-containers-overview|Container Synthesis]] — definitions in one sentence
- [[01-oci|OCI]] — image, runtime and distribution standards
- [[00-index|Index Containers]]
- [[00-moc-ai-engineering|MOC AI Engineering]]
