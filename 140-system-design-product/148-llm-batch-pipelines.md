# Large Scale Batch Pipelines — Flashcards
Tags: #flashcards #ai-engineering #batch #system-design #costs #llm
Verified on: 30 September 2026 — This factsheet lists products, versions or regulatory texts that are evolving quickly.
<!-- summary: batch or online, batch API (JSONL, `custom_id`, 24 h), batch API or continuous batching, replicable architecture, quota cost and duration calculations, error classification, statistical quality control, versions saved with each result, offline self-hosting, when not using batch API, independent identifiers of the order of the results, relaunch. -->


When to process data by LLM in batch rather than online? <!--anki:73254754575550477a61-->
?
When the result can be **differed**: document extraction, history classification, embeddings or massive evaluations. Discounts of API batches and the best filling GPU can reduce the cost, depending on the supply and load ([[121-inference-costs|costs]]).

The batch keeps a **deadline**: a report available at 9 h fails if the processing ends at noon. Sizing useful throughput, withdrawals and margin before this deadline; plan to resume by item rather than relaunch the whole batch. Declare separately acceptance of the job and success of each of its results.

---

How does a API supplier batch work? <!--anki:6f605b3045597429645b-->
?
1. Prepare a **JSONL** file, one query per line, each with a **`custom_id`**
2. Submit lot, processed asynchronously within **24 hours**
3. Retrieve a result file, **out of order**, brought together by `custom_id`
4. Remove lines **in error**

Reduced price by about **50%**, and separate quotas of online traffic. The `custom_id` must be the **business** identifier of the item, not a line number.

---

Do not confuse: API batch and inference server batching? <!--anki:4c374d2b252d29546352-->
?
- **Batch API**: a **mode of invoicing and delivery** of the supplier. Submit a lot, results under 24 h, reduced price
- **Batching the server** (continuous batching): one **Technique of execution** of the GPU, which gathers the current requests to share the weight reading. It is constantly running, Online and offline ([[62-inference-optimizations|continuous batching]])

The first is chosen, the second is automatic in vLLM or SGLang.

---

What architecture for a multi-million-item pipeline batch? <!--anki:4d3f24336e7d3844763e-->
?
```text
source → item splitting (stable id) → work file
       → workers: prompt + model call + validation
       → results (with status, versions) → quality control
       ↘ errors → file (dead letter) → resume
```
Each item has a **status** (to do, done, wrong) that persists: you can interrupt, resume and restart only what failed. Orchestration: Airflow, Dagster, Prefect, or Ray Data and Spark for the large volume.

The number of workers is set to the **quota of the provider**, not the size of the cluster. Beyond that, workers receive 429s and their withdrawals waste quota. A shared rate limiter, in tokens per minute, protects the pipeline and other applications that use the same key.

---

Calculation: 2 million documents each request 3,000 tokens input and 300 output, to 3 €/M and 15 €/M. What cost, then what cost with a fictitious batch discount of 50% on both stations? <!--anki:797842345d605833776e-->
?
Convert volumes first to millions of tokens, because rates are expressed in this unit:
```text
= 2,000,000 × 3,000 = 6,000 M tokens → 18,000 €
output = 2 000 000 ×   300 =   600 M tokens →  9 000 €
total standard = 27 000 €
fictional 50% batch discount on both → 13,500 € stations
```
Common instructions are included in the 3,000 tokens, without additional cache delivery in this statement. Do not implicitly stack cache, batch, and model change. Add retrievals, parsing, and storage to the operational budget, and then verify that batch deadlines and quotas are appropriate. The calculation gives a cost under assumptions, not a current vendor rate.

---

Calculation: how long at least to process 6.6 billion tokens with an overall quota of 2 million tokens/minute, supposed fully usable and without any other bottleneck? <!--anki:694f677b2d714b26386d-->
?
The quota imposes an **Lower Terminal**, If they 6.6 billions of tokens are all counted in the same quota:
```text
6,6e9 / 2e6 = 3 300 minutes = 55 hours
```
The actual duration can be longer: call latency, concurrency, query quota, resumes, pauses and provider throughput are added. Some APIs separate input and output quotas; the above quotient does not apply as is. Measure the bottleneck before requesting more quota or increasing workers.

---

How to make a pipeline batch repreenable? <!--anki:6c4c614f3d3267766f48-->
?
- **Stable identifier** per item, and result write **idempotent** (rewrite the same item does not create duplicates)
- **Persistent** status per item, updated after each achievement
- **Recovery**: Restart only treats items that are not made or in error
- **Medium-sized lots**, so that a breakdown costs only one lot

On GPU **preemptible** (spot), this is what makes the economy possible: an interruption loses almost nothing.

---

How to handle the errors of a batch pipeline? <!--anki:75475e6c31627a623d5a-->
?
**Classify them**, because they do not treat each other the same:
- **Transitional** (network, quota): retry with backoff
- **Invalid output** (broken JSON, missing field): new test, with schema constraint or stronger model ([[63-guided-generation|guided generation]])
- **Problematic content** (unreadable document, too long, refusal of the model): queue of releases for separate treatment

Track **error rate by category**: A peak often signals a change in the format of the source.

---

How to control the quality of millions of outputs? <!--anki:50582f6b425974584d35-->
?
1. **Pilote** on 1% of items, rated on an annotated game, before throwing everything ([[94-evals-methodology|evals]])
2. **Automatic validation** of each output: schema, business rules, plausible values
3. **Random sampling** reviewed by a human or calibrated judge, **per batch**
4. **Distribution Monitoring**: Proportion of each class, empty fields. Brutal drift betrays a problem

It is impossible to reread everything: we control by **statistics**, not by exhaustiveness.

---

Why save versions with each result? <!--anki:45596b32693846726f53-->
?
Each release must bear the **model, version of the prompt, and date** that produced it; otherwise, it is impossible to know what items **retreat** when a prompt is corrected or a model is deprecated, or to explain a result six months later.

This is the **line** of the generated data, as useful in auditing as in maintenance ([[153-data-flywheel-versioning|versioning]]).

Add input ID, schema version, and validation status. To reprocess errors in the v3 prompt, select these results precisely; a simple file name or run date does not distinguish different configurations of the same batch.

---

When to self-host batch processing rather than using a API? <!--anki:69234355312640396e2f-->
?
When **predictable volume, adapted model and data constraints** justify the total cost of operation. A GPU occupied at 100% is not a proof of profitability: measure valid results per euro, lead times, recoveries and engineering time.

Example: a large monthly fee may leave the equipment idle for the rest of the month; a API batch or a temporary rental may cost less.

The offline mode, for example `LLM.generate`, allows batching and [[66-prefix-caching-radix-attention|Reuse of Prefixes]], without guaranteeing an automatic optimum. Test the actual batch and predict sustainable results per element. Self-hosting facilitates some constraints of [[152-pii-privacy|Privacy]], but still requires control of access and network flows.

---

When not to use a API batch? <!--anki:4b552b3350372d2f6a78-->
?
- **Results required in less than a few hours**: a processing window of 24 h, depending on the offer, does not guarantee a faster end or success of each line
- **Dependent steps**: an agent or chain where each call depends on the previous one does not submit in a batch
- **Quick iterations** on the prompt: during the focus, the online call on a sample is more convenient
- **Very small volumes**: lot management costs more than saving money

---

Why should a LLM batch process identify each element regardless of its position in the output file? <!--anki:3336353463383632316264373435326638383439666431323739323631616361-->
?
The **order of restitution** may differ from that of the entries, and some elements may fail. Reconciling by line number can associate a response to the wrong folder.

Assign a stable identifier to each request and attach the results to that key, with duplicates and missing items checked. Resume only unconfirmed units according to their status, retaining business identity. Test mixed and partial output. A batch declared complete does not guarantee that all its requests have been successful or that their effects have been published.

---

Why restart only failed elements of a LLM batch? <!--anki:6439366632316538386238383435303861373831343337666634616431303135-->
?
Restarting the entire batch can **repay achievements, produce variants, and repeat downstream effects**. Each item must have a stable identifier and exploitable status.

Reconcile unknown results first, then create a batch of controlled recovery. Keep pattern, prompt and data of the attempt or explain their migration. A new submission may receive a new technical identifier while representing the same business work.

---

Why fix an input snapshot for a long LLM pipeline batch? <!--anki:6339366339303664373865663437353939656630333633353231653538306636-->
?
If the documents change during processing, the final result can **mix several states of the corpus**. A recovery will no longer know what content has been analyzed.

Keep identifiers, versions and fingerprints, and then link each result to its entry. Set the management of documents removed or corrected before publication. The snapshot makes the calculation consistent; the distribution permissions still need to be checked at the appropriate time.

---

## Scenarios

Scenario: you are asked to extract 15 fields from 3 million scanned contracts, for a migration in six weeks, with a budget of 20,000 €. How do you organize the project? <!--anki:6b69527d595330333274-->
?
1. **Pilote**: 2,000 annotated contracts, comparison of three models in quality and cost per contract ([[162-document-parsing|parsing]])
2. **Encrypt**: tokens per contract, API batch or self-hosted cost, duration according to quotas
3. **Build repeatable pipeline**: Identifier by contract, persistent status, queue of releases, registered versions
4. **Control**: validation of schema and business rules, sample read by batch, monitoring of distributions
5. **Plan a margin** to reprocess releases and a possible second pass

**Trap** : launch them 3 million at a time without a pilot, and discover a defect of prompt after spending the budget.

---

Scenario: your classification pipeline has been running for three days. You discover that an ambiguous instruction has misclassified a category on 30% of the items already processed. What do you do? <!--anki:466c77294a6c3f742445-->
?
1. **Stop** treatment to not make the problem worse
2. **Correct the prompt** and validate it on an annotated sample, especially on the offending category
3. **Identify the items to be reprocessed** thanks to the version of the prompt recorded with each result
4. **Retreat only** affected items, not all stock, if the correction only affects one category
5. **Add a control** on the distribution of classes, which would have detected the anomaly from the first batch

**Trap**: not to have recorded the version of the prompt, and having to retire everything for lack of knowing what.

---

## Sources

- [Anthropic — batch processing, results and expiration](https://platform.claude.com/docs/en/build-with-claude/batch-processing)

## Connections
- [[145-system-design-cases|Case of system design]] — massive document extraction
- [[121-inference-costs|Inference costs]] — batch API and unit economics
- [[62-inference-optimizations|Inference optimizations]] — continuous batching and throughput
- [[153-data-flywheel-versioning|Data flywheel & versioning]] — output lineage
- [[94-evals-methodology|Evaluation — methodology]] — driver and sampling
- [[63-guided-generation|Guided generation]] — large-scale valid outputs
- [[162-document-parsing|Parsing of documents]] — the first step in document pipelines
- [[11-llm-inference-servers|Inference Servers]] — vLLM, SGLang, TensorRT-LLM and their setting
- [[122-finops-llm|FinOps LLM]] — allocate and drive AI spend
- [[141-system-design-llm|System Design LLM]] — design method
- [[158-ingestion-cdc-backfills|Ingestion & backfills]] — manage recoveries, deletions and catch-ups
- [[150-015-distributed-computing-data-performance|Distributed Computing & Data Pipeline Performance]] — limit model calls and make repeats safe
- [[00-moc-ai-engineering|MOC AI Engineering]]
