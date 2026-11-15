# OCI — Flashcards
Tags: #flashcards #containers #oci
<!-- summary: Open Container Initiative role, image specifications, runtime and distribution, cross-platform OCI index, integrity and authenticity, manifests and layers. -->


What does OCI mean? <!--anki:6f362a5b606568722d5a-->
?
**Open Container Initiative**: a project of the **Linux Foundation**, launched in 2015 at the initiative of Docker, to prevent each publisher from imposing its own container format.

The initiative separates interoperability contracts from the products that implement them. It describes how to package, distribute and run containers. For a deployment, remember that the manufacturer of an image and the engine that launches it may be different, subject to platform compatibility and the functions used.

---

Is OCI a software? <!--anki:633b584966716644446b-->
?
**No**, It is a **Standardization Body** He publishes **Specifications**, In other words, documents. The software **Implementing** : [[03-containerd-runc|runc]] for runtime (given by Docker as a reference implementation), containerd, Podman, CRI-O.

By analogy, a format specification describes what a valid file should contain; a program can then read or produce it. This distinction allows you to change tools without necessarily changing images. Compliance with a standard does not replace compatibility tests on the target environment.

---

What are the three major OCI specifications? <!--anki:4d426b496f495d577c37-->
?
- **Image Specification**: image structure, layers, configuration, and manifests.
- **Runtime Specification**: Configuration and lifecycle of a container from a bundle.
- **Distribution Specification**: Exchanges to publish and retrieve content in a registry.

These contracts cover distinct steps: an image is produced and distributed, and then prepared to be executed. They do not impose any particular orchestrator or single build tool. It is this separation that makes possible strings mixing several implementations.

---

What is the OCI Image Specification? <!--anki:492d3f33555e7c406e54-->
?
To standardize the **format and the structure of images**. In concrete terms, an image is a set of files linked by imprints **sha256**:
```text
manifest → lists layers and points to the config
config      → entrypoint, env variables, architecture, OS
→ compressed tar file system archives
```
Each element is identified by its **digest**, making the image **verifiable** and **deduplicable** ([[08-linux-primitives-docker-fundamentals|layers]]).

Above the manifest, a **image index** can point to a manifest per platform, for example `linux/amd64` and `linux/arm64` : the customer chooses the one of his machine. An image published only for amd64 therefore fails on an ARM node with `exec format error`, Even if the tag exists. Building and publishing the variants together avoids this trap.

---

What is the OCI Runtime Specification? <!--anki:74435b21594f332f3126-->
?
To define how a container is **Created and executed** by an [[03-containerd-runc|runtime OCI]] As **Runc** A: **Bundle** (file system extracted + file `config.json`) and one **life cycle** Standardized (`create`, `start`, `kill`, `delete`). The `config.json` Describes them **Namespaces**, on the **cgroups**, the assemblies and capabilities to be applied ([[08-linux-primitives-docker-fundamentals|primitives Linux]]).

It does not define the construction of the image or the download from a registry. To diagnose a failure, distinguish recovered image, prepared bundle and started process: these steps belong to different components.

---

What is the OCI Distribution Specification? <!--anki:4e5b376774414d56514e-->
?
To standardize the **distribution of images**: a API HTTP (`/v2/…`) to push and retrieve manifests and layers, by **tag** or by **digest**. It is this that makes the [[02-docker-images-registries|registries]] interchangeable, and today it serves to distribute much more than images: Helm charts, policies, and even **model weights** as OCI artifacts ([[10-images-models-weights|Weight of models]]).

A successful download proves the artifact's availability, not its CPU/GPU compatibility or trust. Verifying digest, provenance and platform before execution; authentication to the registry does not automatically allow all of its repositories.

---

Do not confuse: Dockerfile and OCI image? <!--anki:74493137785359437339-->
?
The **Dockerfile** is a build recipe; the **OCI image** is a standardized artifact containing manifest, configuration, and layers. OCI does not prescribe the recipe used.

Example: Two builds of the same Dockerfile can produce different digests if `FROM` or unpinned dependencies have changed, so keeping the recipe is not enough to find the tested artifact.

Tools like Buildpacks, Bazel, or Nix can produce an OCI image without a Dockerfile. However, an Apptainer build typically produces an SIF, another format. OCI normalization does not guarantee execution everywhere: architecture, system, and runtime capabilities must be compatible.

---

Why doesn't a cross-platform OCI index make the same binary compatible with all processors? <!--anki:6136343765393966366536623466356339393539373435366166343332346539-->
?
A **OCI Index** can refer to several manifests corresponding to different platforms. The runtime selects a suitable image; It does not automatically convert an x86 binary to an ARM binary.

Build and test each variant with its native dependencies. Log platform and manifest effectively resolved to replicate the deployment. Emulation can help some builds or uses, but does not guarantee compatibility of GPU extensions or performance. A cross-platform tag is therefore a mechanism for distributing variants, not a universal compilation of the same program.

---

Do not confuse: OCI digest and proof of origin of an image? <!--anki:3239616261323537623133393462613038633763336131666432363035353565-->
?
The digest identifies **a content by its imprint** and makes it possible to detect its modification. It does not say by itself who produced it or whether the producer is trustworthy.

A signature or attestation must be verified according to a policy of authorized identities. A malicious image also has a valid digest. Combine integrity, provenance and analysis of the content; none of these verifications replaces the others.

---

Why is copying only layers not enough to reproduce an OCI image? <!--anki:3331623530313466326136623437623462363162306533366135386332336664-->
?
The manifest and configuration describe **the assembly and parameters of the image**. The layers alone do not necessarily give their order, the process to be launched or the required metadata.

Keep the graph of referenced objects with its digests and check the target platform. A registry distributes structured artifacts, not just an archive of files. A copy must be validated by recovery and execution on the intended target.

---

## Scenarios

Scenario: a client imposes Podman, while your inference server images are built with Docker. Should we do it all over again? <!--anki:4f616e4634712154307d-->
?
1. **No** The image conforms to the **OCI Image Specification** runs on Docker, Podman, Containerd or Kubernetes
2. **Check the distribution** : the registry has to talk **OCI Distribution Specification**, What is the case with current registrations
3. **Check the runtime** : Podman uses a runtime conforming to the **OCI Runtime Specification** (crun or runc)
4. **Tester anyway**: Docker-specific options in scripts, rootless mode, GPU access ([[09-gpu-containers|GPU]])
5. **Keep construction reproducible**: same image digests, no `latest`

**Pip**: confuse **format** (standardized) and **tooling** (specific), and believe that an image is related to Docker.

---

Scenario: An audit requires you to prove that your production containers are based on open standards and not on a single supplier. What are you doing? <!--anki:426032727a68504e5149-->
?
1. **The three OCI specifications**: image, runtime, distribution, and what each covers
2. **Real string**: registry compliant, containerd via CRI, runc compliant to spec runtime
3. **Proof of portability**: the same image executed on another runtime, in test
4. **Artifacts**: pinned digests, signatures, provenance ([[105-agentic-ai-devsecops|Supply Chain]])
5. **The honest limit**: the standard is for containers, not orchestrators or managed services

**Trap**: Present OCI as software, whereas it is a set of specifications.

---

## Sources

- 14 November Add-in 2026 — Manifestes, configuration and layers: [OCI — Image Manifest](https://github.com/opencontainers/image-spec/blob/main/manifest.md).

## Connections
- [[02-docker-images-registries|Docker, images & registries]] — concrete implementation of standards
- [[03-containerd-runc|containerd & runc]] — runc applies the OCI Runtime Spec
- [[08-linux-primitives-docker-fundamentals|Linux primitives]] — what the runtime configures (namespaces, cgroups)
- [[07-containers-overview|Container Synthesis]] — chains to rebuild
- [[04-kubernetes-kubelet-cri|Kubernetes, kubelet & CRI]] — orchestration and its interface with runtime
- [[00-index|Index Containers]]
- [[00-moc-ai-engineering|MOC AI Engineering]]
