# Docker, images and registers — Flashcards
Tags: #flashcards #containers #docker
<!-- summary: Docker role and difference with OCI, image or container (instance, state, volumes), Docker/OCI compatibility, records and push/pull workflow, secrets in image layers, build cache, reproducible dependencies. -->


Are Docker and OCI the same? <!--anki:473c39416b3845714e37-->
?
**No.** Docker is a containerization ecosystem/tooling, the reference tool in development: it **builds** images (`Dockerfile`, `docker build`), **distributes** (push/pull to a registry) and **executes** (via [[03-containerd-runc|containerd and runc]]). [[01-oci|OCI]] sets open standards.

On the format side, two types of manifest coexist: `application/vnd.docker.distribution.manifest.v2+json` and `application/vnd.oci.image.manifest.v1+json`. They are almost equivalent, and the current registries and runtimes accept both. Docker is therefore **an implementation**, whose historical format served as the basis for the specification; OCI is **the contract**.

---

Can an image built with Docker be used without Docker Engine? <!--anki:4c543262645e38635a65-->
?
**Yes.** An OCI compatible image may be used by other compatible technologies.

Docker is a build and run tool, not a built-in dependency on any image it produces. For example, Kubernetes can entrust the image to containerd. Check architecture, operating system, and external dependencies, however; an x86_64 image with precise GPU needs does not run on any host.

---

What does “Docker/OIC compatible” mean? <!--anki:494f576456637d502555-->
?
Whether it complies with the **OCI formats or protocols relevant to its role**: image, distribution, or runtime ([[01-oci|OCI]]). A registry does not need to run a container to be compatible with the OCI distribution.

This interoperability makes it possible to replace components, not to remove platform constraints. An ARM64 Linux image does not become native on an AMD64 host; check architecture, system and functionality required. “Compatible OCI” must therefore specify which specification and perimeter have been tested.

---

What orders of magnitude for the size of the images? <!--anki:482a30374c4f77287a3f-->
?
```text
alpine                  ~  8 MB
debian-slim             ~ 75 MB
python:3.x-slim         ~130 MB
image CUDA runtime ~2 to 3 GB
LLM ~8 to 12 GB Inference Server
weight of a model 8B ~16 GB ← to keep out of the picture
```
Hold the order of magnitude: an application image is counted in **hundreds of MB**, a GPU image in **GB**, and **weights** must not enter it ([[10-images-models-weights|Weight of models]]).

These sizes vary with version, dependencies, and compression; distinguishing between downloaded size and uncompressed space on the node. Separating weights is often convenient, but integrating them can be an explicit choice for a stand-alone artifact. Measuring especially pull time, disk space, and update frequency.

---

Do not confuse: image and container? <!--anki:676649472e342573532b-->
?
- **Image** A: **immutable model**, in layers, which contains the application and its environment. It is stored and shared in a registry
- **Container**: a **running instance** of an image, with its own editable state, processes, and network

An image gives as many containers as you want, like a class gives objects. What a written container disappears with it, except in a **volume**.

---

Can a single image create multiple containers? <!--anki:654344583059492e3349-->
?
**Yeah.**, As much as we want. The layers of the image are in **Read Only and Shared** ; Each container adds only one **Inscriptible Layer** on top. Ten containers of the same image do not duplicate physically its layers on the disc, and start in a few hundred milliseconds.

Sharing is based on overlayfs **copy-on-write**: editing a file from the image first copies it entirely into the container layer. Opening a 10GB file embedded in the 10GB mirror image for each container, so the data that changes goes into a volume, not into the image.

---

What is a registry container? <!--anki:4b706936536a6b482f4e-->
?
A service that **stores and distributes images**, according to the API of the [[01-oci|OCI Distribution Specification]]: it keeps the **manifests** and the **layers**, addressed by digest, and serves them on pull. Examples: Docker Hub, GitHub Container Registry, Harbor, Amazon ECR, Google Artifact Registry.

A `pull` first downloads the manifest, then only the missing layers of the node: two images built on the same CUDA base transfer it only once. The `push` works the same, sending only the unknown layers of the registry. Sharing heavy and stable base layers therefore reduces both storage and deployment time.

---

What role does the registry play in business, and what happens if it falls? <!--anki:3334393664346233353761633438343761346139383366633838393265663966-->
?
It supports **access control**,**vulnerability analysis**,**signature** and image retention.

This is a critical component: if it is unavailable, no Pod will start on an image that is not already present on the node.

Parades: a replicated registry or a pull-through **cache** near the cluster, digest pinned images with `imagePullPolicy: IfNotPresent`, and pre-loading critical images on nodes. Test the scenario by draining a node during a simulated registry failure: we see which services are not leaving.

---

Which workflow typically uses a registry? <!--anki:42337a5b48555930447d-->
?
`build → image → push → registry → pull → runtime`
```bash
docker build -t registry.interne/app:1.2.0 .
docker push registry.interne/app:1.2.0
docker pull registry.interne/app@sha256:9f2c…   # by digest: immutable
```
In production, we deploy by **digest** and not by tag ([[112-model-cicd|CI/CD]]).

The build makes the artifact, the push publishes it and the pull picks it up before execution. The digest designates the precise content, while a tag can be moved. The digest abbreviated above is illustrative: use its full value. Add provenance and signature if the delivery chain must verify the origin of the image.

---

Is Docker Hub a runtime? <!--anki:715d2f71583467563355-->
?
**No**, this is a **registry**: it stores and distributes images, it does not execute any. Execution goes back to [[03-containerd-runc|containerd and runc]].

In practice, two consequences: Docker Hub applies **pull limits** to anonymous accounts, and its public images are not audited. Hence the use of an internal **registry** or a mirror in CI and on nodes.

A `ImagePullBackOff` can come from identifiers, quota or an absent tag, before any process starts. Consult the pull event rather than look for logs of an application that has never started.

---

Do not confuse: Tag and digest? <!--anki:72692e4142293e5a457b-->
?
A **tag** is a moveable name, except for the registry's immutability policy; a **digest** identifies specific content.

Example: `app:1.2.0` can be republished after a patch. Two machines pulling this tag at different dates can run different contents; a digest avoids this ambiguity.

A digest can identify a single-platform manifest or a cross-platform index: also record the platform and the image actually resolved. **Integrity is not trusted**: the hash does not certify neither author nor absence of vulnerability. Also pin configuration and external weights to reproduce the service, not just the image.

---

Why is it not enough to delete a secret in a subsequent Dockerfile statement? <!--anki:6165643235633165666534333464373161616533643535326134616162353564-->
?
The previous **layers** may still contain the file or the sensitive value. A deletion in a new layer hides the path in the final view without rewriting the image history.

Provide build secrets by dedicated mechanisms, avoid copying them and also check logs and artifacts produced. If a secret has been published, revoke it and rebuild without it; delete only the last tag does not repair copies already distributed. A secret montage protects its passage to the build, but the executed program can still copy it.

---

Why doesn't a successful Docker build with cache prove that the image is rebuildable? <!--anki:3732663139326236383830383431316338613639636332623234326166626438-->
?
The cache can hide **a removed dependency or a now defective step**. A rebuild on a new machine will actually perform this step.

Periodically test a clean build with locked dependencies and available sources. A mutable base tag can produce another image even with the same Dockerfile. Comparing artifacts and retaining their provenance; content reproducibility and functional success are two separate controls.

---

Why distinguish downloaded image from approved image in a registry? <!--anki:3835656663643731313731613464333862353939656363333462626634303563-->
?
The presence in the registry only proves **the availability of the artifact**. It does not prove review, testing or compliance with the deployment policy.

Promote a digest after validation and apply this selection to the deployment. If a tag is moved, check which digest each instance has actually loaded. Publish permissions should be separated from promotion permissions when they carry different responsibilities.

---

## Scenarios

Scenario: Deploying your inference server takes 20 minutes, including 18 image pull, because the model weights are in the image. What do you change? <!--anki:794e496a3e5e64635b5a-->
?
1. **Output image weights**: light image with runtime, weight mounted from volume or object storage ([[10-images-models-weights|images & poids]])
2. **Pre-pull** image on GPU nodes, with a DaemonSet
3. **Optimize layers**: stable dependencies at the bottom, application code at the top, to maximize cache
4. **Register close**: internal mirror or regional cache, rather than a pullover from the outside
5. **Pinch by digest** rather than moving tag

**Trap**: Rebuild the entire image with each model version change.

---

Scenario: a team pushes its images on Docker Hub with the tag `latest`, and the production sometimes restarts with an unexpected version. What do you put in place? <!--anki:76772d7e25723a7b5829-->
?
1. **Prohibit `latest`** in production: each deployment references a **digest** or an immutable version
2. **Internal registry**: access control, retention, vulnerability analysis
3. **Traceability**: Which image rotates, built from which commit
4. **Signature** of images and verification at admission
5. **Cleaning**: retention policy, otherwise the registry becomes unmanageable

**Trap** I believe a tag is immutable. It can be rewritten at any time.

---

## Sources

- [Docker — build secrets and ARG/ENV limits](https://docs.docker.com/build/building/secrets/) — targeted deepening of the 12 November 2026; educational examples are built for this review.

- 14 November 2026 — Build cache invalidation: [Docker — Build cache invalidation](https://docs.docker.com/build/cache/invalidation/).

## Connections
- [[01-oci|OCI]] — standards behind Docker
- [[03-containerd-runc|containerd & runc]] — which executes the images
- [[08-linux-primitives-docker-fundamentals|Primitive & fundamental]] — layers, volumes, Dockerfile
- [[10-images-models-weights|Images & weights of models]] — case of large models LLM
- [[05-docker-kubernetes|Docker & Kubernetes]] — Why Kubernetes No Longer Needs Docker Engine
- [[06-apptainer-singularity|Apptainer & Singularity]] — the world's HPC containers
- [[00-index|Index Containers]]
- [[00-moc-ai-engineering|MOC AI Engineering]]
