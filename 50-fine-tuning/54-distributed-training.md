# Distributed Training — Flashcards
Tags: #flashcards #ai-engineering #fine-tuning #distributed-training #gpu
<!-- summary: fine-tuning 7B memory calculation with Adam, data or model parallelism, DDP, ZeRO and FSDP, tensor and pipeline parallelism, 3D parallelism, gradient checkpointing, gradient accumulation, mixed precision BF16, network, outages and checkpoints, parallel efficiency calculation, stragglers and microbatches. -->


What should be stored in GPU memory during training? <!--anki:4b3540475374235a42-->
?
1. **Weight** of the model.
2. **Gradients** (same size as weights).
3. **Optimizer states**: Adam keeps **two moments** per parameter, often in FP32, plus one FP32 copy of the weights.
4. **Activations** retained for the — rear pass they grow with the **batch size and sequence length**.

Add temporary buffers, communications, and fragmentation. Gradients have the same shape as driveable parameters, not necessarily the same dtype; in LoRA, frozen weights do not all have gradients. Measure the peak after a complete step, because some optimizer states are allocated late.

---

Calculation: a complete fine-tuning 7B uses weights and gradients BF16, a FP32 master copy and two Adam FP32 moments. What memory for these states, excluding activations and buffers? <!--anki:4f713b3f5d38403a325b-->
?
In mixed precision, about **16 bytes per parameter** before activations:
```text
poids BF16                         2 bytes
gradients BF16                     2 bytes
FP32 copy + two Adam moments  12 bytes
total ≈ 16 bytes × 7e9          ≈ 112 GB (+ activations)
```
This envelope exceeds a 80GB card; a larger card, several GPU with sharding or a light adaptation are options. The only weights of inference occupy about 14GB. Hence the interest of [[51-fine-tuning-adaptation|LoRA / QLoRA]] or ZeRO/FSDP sharding.

The 112 GB are decimal and concern the listed states, not each optimizer configuration. Specify the distribution between GPU and the copies actually present; the batch and the checkpointing modify especially the activations, absent here.

---

What is data parallelism (DDP)? <!--anki:7a643e4b316b7a3a7526-->
?
Each GPU has a full **copy of the model** and processes **part of the batch**; gradients are **averaged between GPU** (all-reduce) before each update. Simple and efficient, but the model must **hold fully** on a GPU.

It is also necessary to distribute the **data**: DDP synchronizes the gradients but does not guarantee separate examples on each rank. With four GPU and eight examples per GPU, one step normally covers 32 examples. The model, its gradients and optimizer states remain replicated in the classic DDP, which limits the memory gain.

---

What is ZeRO and FSDP? <!--anki:45643a7d4866595d5b4e-->
?
Techniques for **partitioning states** between workers:
- **ZeRO-1** distributes optimizer states.
- **ZeRO-2** also distributes gradients.
- **ZeRO-3**, as FSDP in full sharding, also distributes the parameters, temporarily collected for the calculation.

Example: On four GPUs, a uniformly partitioned state occupies about a quarter by GPU, **not the entire drive**. Activations, communication buffers and momentarily collected parameters are added to this share.

More sharding saves persistent memory but increases communications. Measuring the actual peak and throughput; too coarse cutting can cause an OOM during a rally despite low occupancy at rest.

---

What is tensor parallelism? <!--anki:755a7e2d324d60357763-->
?
The **tensor parallelism** distributes the operations of certain layers, including their matrices, over several GPU. Each calculates part of the result; communications gather the necessary contributions following the network. This allows to distribute weights and calculations too large for a single GPU.

As exchanges are frequent, a fast interconnection, often inside a node, is particularly useful. Multinode remains possible depending on the hardware and implementation. Increasing the degree of parallelism reduces local work, but can increase the share of time spent on communications.

---

What is pipeline parallelism? <!--anki:68393a736c62713e4645-->
?
Distribute **the Layers** between GPU (Layers 1-20 on the GPU 1, 21-40 on the GPU 2…). The batch is cut into **Micro-Batch** who advance in a chain to limit the **Bubbles** (GPU inactive in waiting). Moderated Communications → Usable **Between Nodes**.

While a GPU processes a micro-batch, the next one can work on a previous micro-batch. There are still filling and emptying phases, as well as imbalances if one step is slower. Cut according to the **measured cost of the layers**, not just their number, and measure memory activations and time lost in bubbles.

---

What is parallelism 3D? <!--anki:62293e267d6e7d3a7a4d-->
?
The **combination** of the three: tensor parallelism **in the node**, pipeline parallelism **between nodes**, data parallelism (FSDP/ZeRO)**over**, plus sometimes the **context** parallelism (long sequences) and the **expert** parallelism ([[136-mixture-of-experts|MoE]]).

For example, 8 GPU in tensor parallelism, 4 pipeline stages and 2 Data Replicas Mobilize **8 × 4 × 2 = 64 GPU**, in this decomposition. Each axis meets a different limit: the size of a layer, depth of the model or flow rate. Their combination must respect memory, Network topology and global batch size.

---

What is gradient checkpointing? <!--anki:4b623d76394a25253056-->
?
Keep only **some of the activations** during the front pass and **recalculate** during the back pass. We exchange about **30% more calculation** for a **strong memory reduction** of — activations essential for long sequences.

The exact extra cost depends on the recalculated segments; 30% is a marker, not a constant. This technique especially reduces the **saved activations**, not the weights or all the states of the optimizer. If these already saturate the memory, it is necessary to act on another position. Measure the compromise between saved memory and time by steps.

---

What is gradient accumulation? <!--anki:4132692b52472140715d-->
?
Add the gradients of **Several small batches** before making an update: we simulate a **large effective batch** without the corresponding memory. Effective Batch = Micro-Batch × No accumulation × Number of GPU.

The GPU multiplier is for replica data, not tensor parallelism GPU. Normalize the loss correctly and only advance the optimizer at the expected time; the equivalence with a large batch also depends on the operations of the model.

---

What is mixed precision and why BF16 rather than FP16? <!--anki:665a7a642e456235383a-->
?
Combine calculations in **16 bits** and operations or sensitive states in **FP32**, depending on the framework. **BF16** shares the 8 exponent bits of FP32: comparable range, but less accuracy; overflows are less frequent than in FP16 and **loss scaling** is generally unnecessary.

This does not remove NaNs due to data or excessive learning rate. Compare loss and gradients over a few steps to an FP32 reference. Check hardware support: an available dtype does not involve fast kernels. A FP32 master copy depends on the optimizer and configuration.

---

Why does the network count so much in distributed drive? <!--anki:443d775a5e4440455875-->
?
Each step requires **all-reduce/all-gather** of gigabytes between GPU. Without **NVLink** in the node and **InfiniBand/RoCE** between nodes, the GPU **wait** and the [[135-pretraining-scaling-laws|MFU]] collapses. The cluster topology conditions the choice of parallelism.

The volume exchanged depends on the strategy: DDP aggregates gradients, while FSDP must also gather parameters. Examining effective bandwidth, collective latency and overlap with the calculation. Adding GPU does not necessarily accelerate the step if communications or a slow link become the new limit.

---

What operating problems does a drive pose on many GPU? <!--anki:6545723a4169537c663f-->
?
- **Outbreaks** Frequently (GPU, knots, Network) → **Checkpoints** Regular and automatic recovery.
- **Loss spikes** (loss spikes) → monitoring and return to previous checkpoint.
- **Stragglers**: A slow GPU slows down all others.
- **Scheduling** of the cluster (Slurm, Kubernetes with Kueue/Volcano) — see [[13-apptainer-inference-hpc|HPC & Slurm]].

An exploitable checkpoint also retains the optimizer, scheduler, and data read state required. Test its restore before a long workout and choose the frequency according to the write cost and the acceptable lost work. For a slowdown, distinguish GPU failing, saturated network and insufficient data supply before restarting the whole job.

---

Do not confuse: data parallelism and model parallelism? <!--anki:643b6f29754f79465e4b-->
?
- **Data parallelism** (DDP, FSDP): each GPU processes **different data** with a copy (or fragment) of the model, and gradients are averaged
- **Model parallelism**: the **model itself** is split between GPU, in layers (**pipeline**) or inside layers (**tensor**)

The first accelerates the training of a model that already holds in memory; the second becomes necessary when it **does not hold anymore**.

---

Calculation: under C ≈ 6ND, how many GPU-useful hours for an era of fine-tuning dense 7B on 100 million tokens, to 4 × 10^14 FLOP/s useful by GPU? <!--anki:6264366332636363363433613463316539343266666164623039333564333938-->
?
```text
C ≈ 6 × N × D = 6 × 7e9 × 1e8   = 4,2e18 FLOP
H100 to 40% from MFU ≈ 4e14 FLOP/s
4.2e18 / 4e14 ≈ 10,500 s ≈ 3 GPU-hours per time
```
The calculation of a fine-tuning is in **GPU-hours**, not in GPU-years. The constraint is the **memory** (≈ 112GB for a 7B with Adam), which may require sharding or [[51-fine-tuning-adaptation|LoRA]].

This is a useful calculation estimate, not a promised delay: transfers, checkpoints, padding and real efficiency are added. With several GPU, the ideal duration decreases but the GPU-hours do not disappear. The 112 GB excludes activations and assumes a precise diagram of precision and Adam states.

---

What happens if a GPU fails in the middle of a distributed drive? <!--anki:3236353836376335663738323437393161333434323538316365383736326463-->
?
The training is **synchronous**: each step waits for the gradients of all GPU, so **the whole job stops**. We relaunch it since the last **checkpoint**, and everything that has been calculated since is lost.

At the scale of thousands of GPU, failures occur **several times a day**: we save often (asynchronous checkpoints, not to block the calculation), we automatically restart, and we keep spare nodes.

---

Calculation: what rate of acceleration and what efficiency if a drive goes from 8 hours on a GPU to 1.5 hours on eight GPU? <!--anki:3864636563343965616636333434366561396131656435613438323065633239-->
?
The **speedup** is `8 / 1,5 ≈ 5,33`. The **parallel efficiency** is `5,33 / 8 ≈ 66,7 %`, for the same work and the same stop criterion.

The elapsed time decreases, but the consumption goes from **8 to 12 GPU-hours**. Communications, imbalance and sequential portions can explain the gap to the ideal. Check also data rate and convergence: changing the global batch can change the number of steps needed. A measurement of tokens/s alone does not guarantee a better cost to reach the target quality.

---

Why can the slowest worker limit synchronous DDP training? <!--anki:3133663064333432323037663439313961343661346363323462306130313465-->
?
Replicas must participate in **gradient collectives in a compatible order**. A worker slowed down by his data, his network or longer sequences delays the others.

Compare loading time, calculation and communication by rank. Balancing the actual work rather than just the number of examples. An average GPU usage masks these expectations. Increasing the number of GPU without correcting the slow worker can worsen the efficiency and cost.

---

Why does not accumulating gradients automatically remove all DDP communications? <!--anki:6561386466336266636463613465383762666463383237363964626335653661-->
?
Without the proper mechanism, **each backward can trigger synchronizations**. Accumulation increases the effective batch, but therefore does not guarantee the reduction of network traffic.

Check the synchronization configuration and normalization of losses, then profile the collectives. All ranks must follow a compatible sequence. An optimization that avoids intermediate synchronizations must retain the necessary synchronization before updating the parameters.

---

## Scenarios

Scenario: your 7 billion parameter model runs smoothly in inference on a GPU from 80GB, but the full fine-tuning fails in memory. Explains and offers a solution. <!--anki:4b2b71595771393f3e60-->
?
1. **Understanding the Gap**: Drive stores weight, gradients, optimizer states, and activations, approximately 16 bytes per parameter before activations
2. **Calculate**: about 112 GB for 7 billion parameters, so several GPU
3. **The simplest answer**: **LoRA** or **QLoRA**, which result in only a small fraction of the parameters ([[51-fine-tuning-adaptation|LoRA]])
4. **Otherwise, reduce memory**: gradient checkpointing, gradient accumulation, mixed precision BF16
5. **As a last resort, distribute**: FSDP or ZeRO-3 to distribute reports between GPU

**Strap**: Sizing a workout from the memory needed for inference.

---

Scenario: your training on 32 GPU uses only 20% of their theoretical power. Where are you looking? <!--anki:6c2e39332b675d795755-->
?
1. **Network First**: Without NVLink in the node and fast interconnection between nodes, GPUs wait for communications
2. **Parallelism strategy**: the tensor parallelism must remain **in** a node, the pipeline between nodes
3. **The pipeline bubbles**: micro-batchs too few leave GPU inactive
4. **Stragglers**: a slow or degraded node slows down the entire collective
5. **The profile**: measure the time spent in calculation and communication before changing anything

**Strap**: Increase the batch size to "occupy GPU", and bump into activation memory.

---

## Sources

- 14 November 2026 — DDP Synchronization: [PyTorch 2.15 — DDP](https://docs.pytorch.org/docs/2.15/notes/ddp.html).

## Connections
- [[51-fine-tuning-adaptation|Fine-tuning & adaptation]] — LoRA to avoid distribution
- [[135-pretraining-scaling-laws|Pre-workout & scaling laws]] — MFU, calculation budget
- [[136-mixture-of-experts|Mixture of Experts]] — expert parallelism
- [[62-inference-optimizations|Inference optimizations]] — parallelism in serving
- [[09-gpu-containers|GPU in container]] and [[13-apptainer-inference-hpc|Apptainer & HPC]] —
- [[114-reproducibility-variance|Reproducibility]] — fine-tuning reproductible
- [[55-agentic-rl|Agentic RL]] — train a model on agent tasks
- [[56-training-optimization-diagnostics|Training Optimization & Diagnosis]] — effective batch and gradient reduction
- [[00-moc-ai-engineering|MOC AI Engineering]]
