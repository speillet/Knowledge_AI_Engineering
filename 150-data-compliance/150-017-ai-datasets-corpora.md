# Building AI datasets & corpora — Flashcards
Tags: #flashcards #ai-engineering #data #data-engineering
Verified on: 9 October 2026 — technical references and examples of this file.
<!-- summary: manifests, document identity, parsing, deduplication and splits, shards, streaming datasets, shuffles, workers, mixing sources, filtering, packing and resuming training, spreading withdrawals to training caches, splitting by source, packing and leaking. -->


What should the manifest of a training or evaluation dataset identify? <!--anki:6435646437656139346162653431616139653838636163636131313631653832-->
?
A **precise set of data**, with files or snapshots, footprints, schema, volumes and selection rules. Also link transformation code, source versions, split and parameters that change the examples produced.
```yaml
dataset: support-sft
version: 2026-10-05
shards:
  - {path: s3://corpus/support/v3/part-0000.parquet, sha256: 9f2c…, line_items: 48211}
transformation: git 3f9a1c2        # cleaning, deduplication, split
split: {unit: document_family, seed: 17}
```
The manifest is used to verify that an experience reads the right content and that all the expected shards are available. It does not keep the files itself: organize access and retention. The usage rights and provenance must be documented separately from the only fingerprints, which prove a content identity, not a permission to use it.

---

Why distinguish source document, extracted text and tokenized example? <!--anki:6136333861303865396161393463636561623935383238636630643032326438-->
?
These are **three distinct artifacts**, linked by versioned transformations. An unchanged source can produce different text after parser change, and then other tokens after tokenizer or template change.

Example: A PDF contains a correct array, but the parser assigns a value to the wrong column. The PDF hash proves its identity, not the fidelity of the extracted text.

Keep identifiers and versions at each step, with structure checks and references to pages. In training, trace also labels, loss masks and truncation. An error must be able to be located and then corrected without confusing source, extraction and example actually consumed.

---

How to identify the chunks of a corpus without confusing document and processing version? <!--anki:3564316662663534643534643437653362663362633035383030363934613738-->
?
Connect **business identity of the document, source version and parsing/chunking version** to its derived objects. A chunk identifier can integrate these references and its position or content according to a stable convention.

Example: `contrat-42@v7/parse-3/0012` refers to the 12e chunk of the 7 version of the contract, broken by the 3 version of the parser; a new parser produces other identifiers and embeddings to be recalculated. A document-to-chunks table allows replacement, deletion and auditing. Access rights must follow the current document; an older version not even technically available to be used.

---

Why control the families of documents before building the splits of an AI corpus? <!--anki:6166373530383964623062383437373139396162353034613032663861386566-->
?
Copies, revisions, translations, and fragments from the same source can form a **correlated family**. Randomly distributing them between train and test can measure the recognition of previously seen content rather than the generalization sought.

Example: a contract exists in French, in English and in three revisions; randomly distributed, the English version falls in train and the French one in test. Define the unit of separation according to the deployment, family, client or period, and then pass it as a group to `GroupShuffleSplit` of scikit-learn. A high similarity does not always impose a merger: negations and business variants can be important. Document the false approximations and the effect of the policy.

---

Do not confuse: exact deduplication and approximation of quasi-duplicates in a corpus? <!--anki:3361646632396135306334313431343061613131366437383637626435336134-->
?
The deduplication **exact** compares a canonical representation, often via hash; **quasi-doubles** require a measure of similarity, with threshold and validation. Example: MinHash estimates the similarity of Jaccard between sets of 5-grams; two pages that differ only by a dated footer exceed a threshold of 0.8.

Too strong a normalization can make it "allowed" and "unauthorized" if it removes decisive elements. Measure errors of fusion and separation on an annotated sample and keep the provenance of the variants. The policy depends on the purpose: save the calculation, prevent leaks or keep legitimate repetitions.

---

Why build different views for training, evaluation and serving from the same sources? <!--anki:3433643538346237343231643466353338386565643065303062376463653464-->
?
Their **contracts differ**: training with authorized examples and available labels, protected evaluation with verified references, serving with freshness and current permissions. A common source does not make the three views interchangeable.

Sharing identities and transformations when relevant, but versioning selection, timing, and access to each view. Example: The 2025 pricing grid remains in the dated training set, exits the evaluation because it has been corrected, and is no longer served by the RAG. A useful example of debugging may be in development and no longer be an independent test.

---

Why distribute a large corpus in shards? <!--anki:3864393532646138383963363439383161633837393465613830333830623564-->
?
**shards** are identifiable pieces of the dataset that workers can read and process separately. They facilitate parallelism, recovery and completeness control.

Too many small shards increase apertures and metadata; too few large shards limit distribution and make some replays expensive. Example: 2 TB shards of 500 MB give 4,000 files, enough to occupy 64 workers and replay an offending shard alone. Balancing by bytes, tokens or cost of parsing them.

---

Do not confuse: streaming a training dataset and processing an event flow? <!--anki:6163333033326639383231633435356161326438333864333464346634316166-->
?
**dataset streaming** gradually reads examples without downloading or loading into memory; the dataset can be bounded and frozen. A **event stream** describes data that arrives over time, with delay, status and update policies.

Thus, `load_dataset("parquet", data_files=..., streaming=True)` returns an iterator on a frozen corpus, read shard by shard, without watermark or late event. The streaming mainly changes random access, shuffle and recovery of the player. Define if the list of objects is frozen during an era, otherwise two executions can traverse different populations.

---

Why is a shuffle with a limited buffer not a uniform permutation of the entire corpus? <!--anki:6333363564353838383264323439363139393737336166333538383134356634-->
?
The player chooses from a **bounded buffer**, fed over the course of the playback. With a small buffer, the close examples in the files can remain correlated; the overall mixture also depends on the order of the shards.

Example: with `ds.shuffle(seed=42, buffer_size=10_000)` on files sorted by language, one million examples per language, hundreds of consecutive batches remain monolingual. A fixed seed makes these decisions reproducible, without guaranteeing a uniform mixture. Examine languages, sources and lengths as the batches progress. Adapt buffer size and reading order to the memory budget and the risk of homogeneous sequences during training.

---

How to avoid duplicate examples with multiple workers reading an iterable dataset? <!--anki:3830393964353066316135353465633961306461643261313462343164666335-->
?
Explicitly distribute **shards or examples between rows and workers**, depending on the framework. Copies of the same iterator can otherwise browse the same data. In PyTorch, a `IterableDataset` replicated between workers must be configured to avoid these duplicates.
```python
info = torch.utils.data.get_worker_info()
mes_shards = shards[info.id::info.num_workers] if info else shards
```
Between rows, Hugging Face Datasets' `split_dataset_by_node` plays this role. Test read identifiers, coverage and recoveries on a small corpus before mounting support. Control also the latest uneven partitions, number of steps and behavior in case of a failed worker. Some samplers complete or truncate data to balance the rows; this behavior must be chosen and measured.

---

What reading state should be considered to faithfully resume training? <!--anki:3533353633613665303635303465366462383365303936616664623361303730-->
?
Beyond the model and optimizer, consider **dataset version, sampler progress or shards, seeds, and mix state**. Buffers and preloads can advance playback beyond the last batch actually consumed.

The exact recovery depends on the drive: `IterableDataset.state_dict()` from Hugging Face Datasets saves shard and position, but the examples present in the mixing buffer are lost on recovery. Set whether a few repeated or skipped examples are acceptable, then test the protocol with example identifiers. Changing the number of workers, file order or transformation code can change the sequence, even with the same restored weights.

---

Why define the mix of a corpus in tokens or in weight, not just in number of documents? <!--anki:3232343231323664636232393461613961373837633435306161613264303231-->
?
Documents of different lengths contribute very differently to the **number of tokens and to the calculation of loss**. A minority source of documents can dominate the training if its texts are long or if it is resampled.

Define mixing unit, weighting, repeat management, and budget by source. Example: 60% of tokens for web, 30% for code, 10% for mathematics, with no more than four passages on the rare source. A mix chosen to improve a capacity does not automatically represent evaluation traffic; maintain a separate measure on the target population and analyze regressions.

---

Calculation: a corpus contains 1,000 documents A of 100 tokens and 1,000 documents B of 900 tokens, each read once without truncation. How much of the documents and tokens comes from B? <!--anki:6462356638376464316534313436393162623638383963353337323839313762-->
?
The two denominators give different answers:
```text
Part of documents B = 1,000 / 2,000 = 50%
tokens A = 100 000 ; tokens B = 900 000
Share of tokens B = 900,000 / 1,000,000 = 90%
```
With a loss averaged evenly over these unmasked tokens, B contributes much more than document counting suggests. Masking, packing, truncating, or weighting changes this contribution. Fix the targeted unit before announcing that a corpus is balanced.

To aim for 50% of the tokens of each group at unchanged lengths, it would be necessary to adjust the sampling frequencies or weights. Reading each short text nine times in total equalizes the volume without creating nine times more information.

---

How to check that a quality filter does not excessively impoverish a corpus? <!--anki:6337653966306332613463373464356339353162396138333063666135316135-->
?
Measure **what is removed and retained by segment**: languages, sources, lengths, formats and difficult cases. A filter trained on a dominant style can eliminate valid texts more often elsewhere: remove 15% from English encyclopedic pages, but 45% from French technical forums useful to the product.

Annotate a sample of rejections and acceptances, version the rules and compare the model on the capabilities sought. A high rejection rate is not proof of quality. Keep the counters and grounds necessary for diagnosis, with a policy adapted for rejected content; keep everything indefinitely is not required to trace the filtering.

---

Why are packaging and truncation part of the training data contract? <!--anki:3331313130373163333037393436333738333337353664353334383661653766-->
?
The **packing** groups several examples in a sequence; the **trunk** removes tokens beyond a limit. They modify boundaries, proportions and sometimes target actually learned.

Check separators, Loss masks and attention according to the goal. With no planned isolation, One example can use the context of another. A truncation to 2,048 tokens Withdraw 252 of the 400 tokens of an example whose question counts 1,900 : The model learns a cut-off response. Measure tokens useful, truncated examples and affected segments. A better occupation GPU does not guarantee an equivalent dataset: compare learning and evaluation after change of preparation.

---

Why does keeping a deleted dataset in a drive cache invalidate corpus traceability? <!--anki:6564663938306139626230623464333338323732346261393465373838323565-->
?
A **Derived cache** may continue to provide examples removed from sources or excluded from a new release. The dataset actually read no longer corresponds to the announced manifesto.

Include version of the corpus, transformations, and filtering rules in the cache keys. Spreading withdrawals to affected shards, tokenized data, and artifacts according to a verifiable policy. Trying with a deleted sentinel example, and then inspecting what the dataloader actually consumes. Recalculating the manifest without invalidating the derivatives does not prove their update.

---

Why distribute documents by source before producing their training and test chunks? <!--anki:3434343932633965343139653433646662343938346632336437366538323931-->
?
Chunks of the same document can **share formulations and facts**, even if they are not identical. A random distribution after splitting creates a leak between games.

First assign the relevant groups, and then transform and verify the quasi-duplicates. The group can be document, author, client or period depending on usage. Keep the split manifest so that subsequent reconstructions do not silently move the examples.

---

## Scenarios

Scenario: doubling workers almost doubles the examples read per era, while the manifesto does not change. What do you check? <!--anki:3662643934313736323438393439643638393361356364336135356562396335-->
?
1. **Collect read** identifiers on a small controlled corpus.
2. **Examine split between ranks and workers**, especially for replicated iterators.
3. **Check padding, repetition and end of period criteria** of the sampler.
4. **Correct distribution** and measure coverage and intersection of readings.
5. **Recalculate tokens** budget and affected training results.

**Trap**: Consider the number of batches as proof of the number of separate examples.

---

Scenario: a new version of the parser improves the tables but drops the answers on the scanned contracts. How do you evaluate it? <!--anki:6462623731663332343139613434663761313937643937616133373962396434-->
?
1. **Compare versions on identical documents**, with extraction references.
2. **Segment by document type**, language and scan quality.
3. **Examine lost structure or text**, then derived chunks and tokens.
4. **Rebuild a versioned candidate corpus** and replay the downstream assessments.
5. **Post after validation**, with possibility to return to the previous version.

**Trap**: Replace the parser globally based on a single average score.

---

Scenario: the evaluation score increases sharply after ingestion of new documentation almost identical to the test questions. How do you react? <!--anki:3266613563346337306432363434623261373062366564376532636164343530-->
?
1. **Search for overlaps and common families** between sources, training and testing.
2. **Distinguish allowed access to the RAG corpus and response leak**, depending on what the test measures.
3. **Isolate contaminated data** and document the separation rule.
4. **Recalculate scores on an independent test adapted** to the intended deployment.
5. **Verify the incident and prevent recurrence** by checking for provenance and similarity.

**Trap**: Declare any presence of a document in the RAG as a leak, or any gain as a generalization enhancement.

---

## Sources
- [Hugging Face Datasets — streaming, shards, mixing and recovery](https://huggingface.co/docs/datasets/stream)
- [PyTorch — loading and iterable datasets](https://docs.pytorch.org/docs/2.14/data.html)
- [Lee et al. — deduplication of training data](https://arxiv.org/abs/2107.06499)
- [Apache Arrow — columnar representation and exchanges](https://arrow.apache.org/docs/format/Columnar.html)

## Connections
- [[20-010-rag-permissions-versions|RAG: rights & versions]] — Apply the Corpus Life Cycle to Evidence Served
- [[151-data-curation-annotation|Curation & annotation]] — linking editorial quality and corpus construction
- [[153-data-flywheel-versioning|Versioning of data]] — fix content, transformations and preservation
- [[162-document-parsing|Parsing Documentary]] — control derived representations
- [[150-012-columnar-storage-lakehouse|Analytical storage]] — organize and read shards efficiently
- [[150-016-data-observability-lineage|Data lineage]] — find sources and consumers affected
- [[172-ml-validation-metrics|Validation ML]] — protect splits and measure generalization
- [[00-moc-ai-engineering|MOC AI Engineering]]
