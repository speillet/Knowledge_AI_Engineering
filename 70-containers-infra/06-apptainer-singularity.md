# Apptainer & Singularity — Flashcards
Tags: #flashcards #containers #apptainer #singularity #hpc
<!-- summary: Singularity → Apptainer, SIF format and Docker image conversion, `--nv`, bind mount permissions, host environment, immutable image. -->


In which Apptainer environment is it particularly used? <!--anki:755e35286742334e2d28-->
?
In environments **HPC**, scientific computing, shared clusters (Slurm, MPI) and GPU workloads: no root daemon, the container runs **with the user identity** (details in [[13-apptainer-inference-hpc|Apptainer & HPC Inference]]).

This integration makes it easier to access shared directories and the resources allocated by the scheduler. It does not grant additional rights to these data. The isolation level and privilege mechanisms depend on the installation; examine the cluster configuration before considering the container as an untrusted code sandbox.

---

What is the relationship between Singularity and Apptainer? <!--anki:75255f5a4e5e676b2342-->
?
**Apptainer is a continuation of the Singularity project**: the project was renamed to 2021 by joining the **Linux Foundation**, while the name Singularity was retained by a commercial offer. Practical consequence: documentation and scripts still circulate with the `singularity` command, which often remains available as an alias.

The name alone is not enough to identify the software: SingularityCE and commercial offers also have their trajectory. Check binary, version and corresponding documentation before transposing an option or editing behavior.

---

What is the historically native image format of Apptainer/Singularity? <!--anki:4e496b6d7331432b713f-->
?
**SIF — Singularity Image Format**: a **single file**, unlike the stacked layers of an OCI image. It can be **signed** and run directly, making it easy to copy, archive and share on a cluster file system.

An SIF is mounted **read-only**: to write, we mount a host directory with `--bind` or a temporary layer with `--writable-tmpfs`. On a parallel file system like Lustre, reading a single large file is much cheaper than opening thousands of small layer files: this is a decisive asset in HPC.

---

Is an SIF image simply an OCI image? <!--anki:4d7c436a753d627a6e3c-->
?
**No.** A [[01-oci|OCI]] image describes configuration and layers; a **SIF** groups objects into a file, usually including a read-only compressed file system.

Apptainer can convert an image retrieved via `docker://` to SIF. This SIF can also be published in a compatible OCI registry via **`oras://`**, as an artifact: this does not transform it into an image directly executable by Docker.

Example: Sharing `modele.sif` per registry avoids manual transfer on each cluster, but consumers need to understand the SIF format. Distinguish between **execution format and distribution channel**, and then verify provenance and conversion compatibility.

---

Do not confuse: Apptainer and Docker in terms of security? <!--anki:6e52296f4e61242e4541-->
?
- **Docker in rootful mode**: Access to the socket of the daemon gives equivalent powers to root. The **rootless mode** changes this model.
- **Apply**: no permanent daemon, usually running with user identity and rights, suitable for [[13-apptainer-inference-hpc|HPC]] policies.

This does not make an image harmless: it can read or edit mounted files that are accessible to the user. Check mounts, network, and local configuration; admission to a cluster depends on its policy, not just the product.

---

How do I execute a command in an Apptainer image? <!--anki:785338455e3a71633e63-->
?
```bash
apptainer exec image.sif python train.py     # an Order
apptainer shell image.sif                    # an Interactive Shell
apptainer run image.sif                      # The runscript of the image
```
By default, on the **current directory and personal folder are mounted** and environment variables are inherited, so a script can work at home and fail elsewhere. To isolate, we use `--cleanenv` and `--no-home`.

No daemons keep containers active: each `exec` starts a container for the duration of the command. For a durable service, such as an inference server, `apptainer instance start image.sif nom` starts a background instance, which is stopped with `apptainer instance stop nom`.

---

What is `--nv` with Apptainer? <!--anki:78416b386d2b283c4c2f-->
?
To provide the container with the necessary access to the host machine environment **[[09-gpu-containers|NVIDIA/GPU]]**.

```bash
apptainer exec --nv model.sif python inference.py
```

The option makes available the necessary NVIDIA devices and libraries, while the kernel module remains the host's. It does not install a missing driver and does not reserve a GPU in Slurm. It requires a valid allocation, CUDA/driver compatibility and application dependencies in the image.

Testing a small calculation with the framework of the model and then a representative inference. See the GPU with a system tool does not prove that all the necessary kernels are working or that there is enough VRAM left for the intended context.

---

Why should a bind mount Apptainer be reviewed as a host data access permission? <!--anki:6663353433363966343166303438636461383836343031343864373330346366-->
?
A **bind mount** renders a path of the host visible in the container with the applicable effective rights, so the SIF image is not enough to describe the data accessible during the job.

Inspect explicit and automatic edits, limit paths, and use read-only when writing is not required. Test with job identity and actual shared file system. Overly large edits can expose results of other experiences or personal directory secrets. Immutability of the image does not protect a scripted host directory.

---

Why can an identical SIF image produce different results on two machines? <!--anki:3938383534356265633737633432303239393435333238653530333532393636-->
?
Runtime also depends on **kernel, exposed libraries, environment, and mounted files**. The image does not freeze the entire host.

Document the required dependencies and verify the actual variables and mounts. For the GPU, test compatibility on each target. Reproducibility requires a runtime manifest; keeping only the SIF file is not enough to reproduce all numerical results and data access.

---

Why separate the outputs of an Apptainer calculation from the immutable content of the SIF image? <!--anki:3137663866346338343435643437373039326464663731313666353061323330-->
?
The results and caches are **execution data**, while the image describes the environment. Using explicitly mounted output directories facilitates traceability, permissions, and retention.

Assign one space per job to avoid collisions. Check the user's actual rights and automatic edits. A read-only image does not make the host directories mounted to write harmless.

---

## Scenarios

Scenario: your experiments run in a Docker image, but your lab's compute cluster only allows Apptainer. How do you do it? <!--anki:714676425960586c7734-->
?
1. **Convert**: `apptainer pull mon.sif docker://mon-image:tag`, which produces a unique SIF file
2. **Understand the model**: no root daemon, the container is running **with your identity**, which explains the permission
3. **GPU Access**: Add `--nv` to expose the host machine's NVIDIA driver
4. **Data and weight**: mounted from the shared file system, never embedded in the image
5. **Check**: CUDA version compatible with cluster driver ([[13-apptainer-inference-hpc|Apptainer & HPC]])

**Trap**: Assume that the paths and users of the Docker image exist as is in the Apptainer container.

---

Scenario: a colleague wants to store the weights of a model of 40 GB in the SIF file "so that everything is reproducible". What do you think? <!--anki:755257727d5f58674535-->
?
1. **Real advantage**: a unique and immutable file, easy to copy and archive
2. **Disadvantages**: Huge image, full reconstruction with each model version, duplicated storage on the cluster
3. **Current practice** : image with runtime, weight on the **Shared File System**, mounted at the execution
4. **Reproducibility otherwise**: version of weights pinned and checked by imprint ([[10-images-models-weights|images & poids]])
5. **Where FIS wins**: Nodes without network access, or need a self-supporting artifact

**Trap**: confuse immutability and reproducibility, which is also obtained by versioning.

---

## Sources

- [Apptainer — access to GPU devices and libraries](https://apptainer.org/docs/user/main/gpu.html)
- [Apptain — publishing SIF with push and ORAS](https://apptainer.org/docs/user/latest/cli/apptainer_push.html) — targeted consultation of 6 November 2026.

- Complement of the 14 November 2026 — Host mounts and dependencies: [Apptainer — Bind Paths and Mounts](https://apptainer.org/docs/user/latest/bind_paths_and_mounts.html).

## Connections
- [[13-apptainer-inference-hpc|Apptainer & HPC Inference]] — advanced use for serving LLM
- [[09-gpu-containers|GPU in container]] — equivalent `--gpus` / `--nv`
- [[02-docker-images-registries|Docker & images]] — Interoperability `docker://`
- [[00-index|Index Containers]]
- [[00-moc-ai-engineering|MOC AI Engineering]]
