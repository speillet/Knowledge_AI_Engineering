# Audit of the LLM — 8 October 2026

The course already had the central mechanisms: prefill/decode, KV cache, batching, quantification, speculation, routing, SLO and costs. The audit revealed above all a lack of depth on **the validity of the measurements, the experiences of charging and the transition from a diagnosis to a decision of capacity**. Some formulations also promised too systematic gains.

This review adds **63 cards**, including **12 calculation cards**, to three new cards and five existing cards. It corrects or specifies **47 old cards**, without deleting their Anki IDs. The three new cards each include 16 cards, including three situationalized cards. The five ML cards previously added, namely 70 cards, are kept in a separate commit.

The result is to maximize the **useful tasks performed under constraints of quality, time and cost**. The gross throughput of tokens, full VRAM or an active GPU is not enough to choose a configuration.

## Verified coverage

“Existing” means that the notion already had a dedicated topic; “deepened” means that its limits, metrics or decision criteria have been completed. This matrix covers the engineering foundation of the inference, not each variant of kernel, hardware or architecture published.

| Problematic | Audit status and expected depth | Reference forms |
|---|---|---|
| TTFT, TPOT, ITL and full life | In-depth: formulas, granularity of chunks, weights and outputs of less than two tokens | [64 — Metric](../60-llm-inference/64-inference-metrics-slo.md), [93 — Monitoring](../90-observability-evals/93-monitoring-inference.md) |
| Reasoning and Visible Experience | Addition: first event, first useful content, tokens visible or internal | [64](../60-llm-inference/64-inference-metrics-slo.md), [138 — Reasoning](../130-llm-fundamentals/138-reasoning-models.md) |
| Flow rates and success criteria | Extended: offered, admitted, completed, useful; criteria intersected by query | [64](../60-llm-inference/64-inference-metrics-slo.md) |
| Percentiles and histograms | Addition: quantile aggregation, buckets at SLO thresholds, size, segmentation and cardinality | [93](../90-observability-evals/93-monitoring-inference.md) |
| Errors and missing observations | Added: timeouts, rejections, cancellations and unfinished requests; avoid metrics on success only | [64](../60-llm-inference/64-inference-metrics-slo.md), [60-010 — Benchmarks](../60-llm-inference/60-010-inference-load-benchmarks.md) |
| SLO and Error Budgets | Fixed: burn rate of a fraction of non-compliant events; not a percentile | [64](../60-llm-inference/64-inference-metrics-slo.md), [116 — SRE](../110-mlops-cicd/116-ai-sre-incidents-capacity.md) |
| Customer measurement, gateway and engine | Add: milestones, clocks, buffering, tasks, calls and attempts | [93](../90-observability-evals/93-monitoring-inference.md), [84 — Streaming](../80-api-layer-routing/84-streaming-application-integration.md) |
| Charging protocol | New plug: open/closed loops, coordinated omission, saturated generator and actually emitted load | [60-010](../60-llm-inference/60-010-inference-load-benchmarks.md) |
| Realism and reproducibility | Addition: joint input/output distribution, prefixes, bursts, manifest, heating and draining | [60-010](../60-llm-inference/60-010-inference-load-benchmarks.md) |
| Uncertainty of results | Addition: repetitions, trial order, time dependencies and stability of p99 | [60-010](../60-llm-inference/60-010-inference-load-benchmarks.md), [99 — Statistics](../90-observability-evals/99-statistics-experimental-decisions.md) |
| Little's ability and law | Fixed: flight requests ≠ sequences GPU; mid-range ≠ | [64](../60-llm-inference/64-inference-metrics-slo.md), [60-011 — Capacity](../60-llm-inference/60-011-inference-capacity-scheduling.md) |
| Memory KV | Deep: bytes/token, Gio/Kio, growth, sharing, margin by GPU, GQA/MQA and replication | [61 — KV](../60-llm-inference/61-kv-cache-attention.md), [60-011](../60-llm-inference/60-011-inference-capacity-scheduling.md) |
| Non-classical architectures | Explicit limits: Do not transpose the classic KV formula to MLA, sliding windows and recurring states | [60-011](../60-llm-inference/60-011-inference-capacity-scheduling.md) |
| Ordonnancement | New topic: sequences, tokens by iteration, maximum context, preemption and recalculated work | [60-011](../60-llm-inference/60-011-inference-capacity-scheduling.md) |
| Admission, Priorities and Equity | Addition: queue bounded by delay and work, aging, customers and long prompts | [60-011](../60-llm-inference/60-011-inference-capacity-scheduling.md) |
| Replication and multi-GPU | In-depth: DP/TP/PP, fault domain, communications, MoE and expert placement | [60-011](../60-llm-inference/60-011-inference-capacity-scheduling.md), [136 — MoE](../130-llm-fundamentals/136-mixture-of-experts.md) |
| Autoscaling and Reserve | Deepened: real readiness, cold cover, drainage, oscillation, breakdown and queue growth | [64](../60-llm-inference/64-inference-metrics-slo.md), [60-011](../60-llm-inference/60-011-inference-capacity-scheduling.md) |
| Prefix caching | Deepened: hit per request/token, real E2E gain, affinity against overload; isolation already processed | [66 — Prefix caching](../60-llm-inference/66-prefix-caching-radix-attention.md) |
| Batching and interference between phases | Fixed: conditional gains; compromise batch, chunked prefill, TTFT and streaming pauses | [62 — Optimizations](../60-llm-inference/62-inference-optimizations.md), [69 — Roofline](../60-llm-inference/69-roofline-prefill-decode.md) |
| Roofline and disintegration | In-depth: theoretical ceiling ≠ measured flow rate, assumptions of prefill, transfer KV and recovery | [69](../60-llm-inference/69-roofline-prefill-decode.md) |
| Speculative Decoding | Fixed: conditionally preserved distribution, verification cost, acceptance ≠ speedup | [67 — Speculation](../60-llm-inference/67-speculative-decoding.md) |
| Quantification | Fixed: independent weight/activations/KV, kernels and quality per segment; no universally lossless format | [68 — Quantification](../60-llm-inference/68-quantization.md) |
| Profiling and Critical Path | New listing: CPU/GPU, tokenization, media, network, NUMA, chronology and cost of instrumentation | [60-012 — Approach](../60-llm-inference/60-012-inference-optimization-method.md) |
| Graphs, compilation and kernels | Addition: distinct mechanisms, shapes, memory, start and digital validation | [60-012](../60-llm-inference/60-012-inference-optimization-method.md) |
| Prioritization of optimizations | Addition: Amdahl, rebuttable hypothesis, interactions and quality/cost/time limit compromise | [60-012](../60-llm-inference/60-012-inference-optimization-method.md) |
| API and charge amplification | Addition: RPM, I/O tokens, bursts, fetches, hedging and cancellation | [60-012](../60-llm-inference/60-012-inference-optimization-method.md) |
| Reduction of application work | Existing and related: context, model, cascade, response cache, reasoning and agent branches | [60-012](../60-llm-inference/60-012-inference-optimization-method.md), [82 — Routage](../80-api-layer-routing/82-routing-llm.md) |
| Quality and output control | Existing and integrated with criteria: evals, JSON, truncations, sampling, canary and rollback | [63 — Structured outputs](../60-llm-inference/63-guided-generation.md), [65 — Sampling](../60-llm-inference/65-probabilities-sampling.md), [112 — CI/CD](../110-mlops-cicd/112-model-cicd.md) |
| Cost, energy and batch | In-depth: cost per compliant response, booking, calculation API, J/task; asynchronous batch already processed | [121 — Costs](../120-costs-finops/121-inference-costs.md), [148 — Batch](../140-system-design-product/148-llm-batch-pipelines.md) |
| Multimodal | Addition: Resolution/Duration, Encoder, Processor and Billing Units, Advanced Memory | [60-012](../60-llm-inference/60-012-inference-optimization-method.md) |

## Proposed working approach

1. **Definite useful result**: task, minimum quality, compliance proportions and cost budget; separate interaction in streaming and deferred processing.
2. **Measuring the right perimeter**: client and engine, errors included, reconciled volumes, histograms and relevant segments.
3. **Establish capacity**: load curves, steady or increasing queue, cold/hot caches, bursts, cancellations and loss of capacity.
4. **Choose a targeted hypothesis**: KV memory, calculation, bandwidth, communications, CPU, quota or superfluous application work.
5. **Compare and deploy**: repeat tests, quality per segment, goodput and cost to expected traffic, then canary with rollback criteria.

## Workshops to demonstrate mastery

### Measurement and SLO

Produce a small set of events including success, rejection, timeouts, short answers, chunks containing multiple tokens, and resumes. Calculate TPOT separately per request, chunk intervals, goodput, and joint compliance rate. Build two replicas with different volumes to show why their p95s do not average.

**Livable**: definition of populations, units and denominators, with manual verification of a few lines. Errors before first token remain in the eligible events of the contract, even if they do not appear in the histogram TTFT.

### Capacity under load

On an available test server, compare multiple loads with the same data, version, tokenizer, and generation settings. Keep expected/actual arrivals, results, lengths, latencies, and cache status. Separate technical warm-up and content reuse. Include emptying, errors, and abandoned requests.

**Livable**: goodput curves, latencies, refusal and queue growth; manifests of each run and capacity retained with justified margin. Add a spike and a replica loss. A queue simulation can prepare the exercise but does not demonstrate an actual GPU capacity.

### Targeted optimization

Identify the dominant bottleneck and then compare a baseline, a lever and a justified combination: scheduler, prefixes, kernels, precision or speculation. Compare on identical tasks and on the lengths actually produced, taking into account interrupted outputs.

**Deliverable**: hypothesis, measure that could refute it, quality control by segment, representative profile and results without heavy profiling. Explain a case where optimization becomes unfavourable. Quality is measured on a set separate from the eventual calibration.

### Cost and quotas

Build a spreadsheet or a script with hourly volume, success rates, resumes, quotas, backup replicas and fictitious prices clearly identified. Compare a service more expensive by the hour but better in goodput to a service cheaper and less productive.

**Deliverable**: cost per compliant task and demand coverage, low load and target load. If energy is measured, specify GPU/server/installation and integrate joules on the same window. Do not convert a GPU activity to cost or carbon by an unvalidated proportionality rule.

## References and Limitations

The primary references are kept in the files: vLLM documentation for the metrics, Budgets and kernels. NVIDIA for DCGM and GenAI-Perf Prometheus for histograms and instrumentation; Google SRE for Error Budgets Orca works, PagedAttention, GQA, DistServe and speculative decoding for mechanisms. Examples of quotas are fictitious. the concrete rules depend on theAPI. Financial examples are not current rates.

The base now deals with measurement, sizing, optimization, quality and operation. A specialization will still require a practice on the target hardware: writing kernels, precise adjustments of collectives, internal mechanisms of each architecture or energy optimization of a site. The list of options and names of metrics must be confronted with the version actually deployed.

## Validation carried out

- **Content**: 63 new cards and 47 old cards specified; 34 numerical results recalculated in Python, covering in particular the 12 new calculation cards.
- **Navigation**: three new topics integrated into the MOC and the catalog, reciprocal connections, updated summaries; linted without error or warning.
- **Compatibility**: 1,793 active card identifiers present before this audit are retained; titles of existing subpackages unchanged.
- **Tests**: Existing 40 tests pass; Synchronized catalogs and `git diff --check` own.
- **Export**: 1,856 cards active in 129 cards and 17 sections; 293 situationalized and 139 distinctions. Anki archive and SQLite database verified, old GUID and subpackage assignments retained, 30 cards removed always suspended.

No GPU benchmark or paid call to a API was executed for this audit. The card numbers are pedagogical calculations under explicit assumptions, not measured production gains. The local export `dist/ai-engineering.apkg` has been regenerated; this artifact remains excluded from Git.
