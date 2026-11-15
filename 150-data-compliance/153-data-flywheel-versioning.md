# Data flywheel & data versioning — Flashcards
Tags: #flashcards #ai-engineering #data #flywheel #versioning #mlops
<!-- summary: improvement loop, steps, data versioning, tools (DVC, lakeFS, Iceberg), eval lineup, index versioning, implicit signals, traps, prioritization, production feedback representativeness, feedback and policy, example priority. -->


What is a data flywheel? <!--anki:452f4c54795042304253-->
?
A **continuous improvement loop**: the product is used → on collecting **tracks and feedback** → on **analysis** failures → on improving (prompts, retrieval, evals, fine-tuning) → the product is better → more usage and data. The lasting competitive advantage comes from this loop, not from the model.

The loop only improves if feedback is relevant, allowed, and transformed into evaluated changes. An increase in mislabeled or biased data can amplify errors; keep an independent test to confirm the gain.

---

How does a data flywheel start? <!--anki:4f4d77716748323a2d5f-->
?
1. **Collect** traces and feedback, explicit as implicit.
2. **Priority sampling** of failures and uncertain cases.
3. **Analyse** and categorize errors.

Failures reveal improvement needs, but oversampling changes the observed distribution. Also keep a representative sample to measure overall quality. Separate model error, missing source, failed tool and misunderstood wait before producing new training examples.

---

How does a data flywheel end? <!--anki:4f217724235b63464567-->
?
4. **Labell** and add to the golden dataset.
5. **Fix**, starting with the least expensive lever: prompt, then retrieve, then fine-tuning.
6. **Validate** offline, **deploy** in canary, **measure** online.

Choose the lever according to the **cause**: an absent document is not corrected by a longer prompt, and a tool bug is code. Separate the examples used to adjust the system from an independent test. Keep the version of the correction, measure the effects by segment and predict the return.

---

Why version the data? <!--anki:695e49255e7a682b623f-->
?
To identify **actually used data**, compare experiences and find the origin of a result. A version must designate stable content, with manifest or snapshot, transformations and source metadata.

The name of a version is not enough if its files disappear or change. Set retention, access and restore as needed; a hash allows to verify a content identity, not to prove alone its origin or rights of use. A partially reproducible experience must explain what is missing rather than treat its score as devoid of any information.

---

Which tool to version what data: files next to code, data lake, analytical tables, eval games? <!--anki:6663323763343033366262303439636539643836643838366461613930353662-->
?
- **Files next to the code**: **DVC** (pointers in git, content on an object storage)
- **Data lake entire**, with git-like branches and commits: **lakeFS**
- **Analytic tables**: **Delta Lake** or **Iceberg Apache**, with their history (time travel)
- **Eval Games**: Versioned datasets from the eval platform ([[91-langfuse-observability|Langfuse]]) or the Hugging Face Hub

Regardless of the tool, check restore, versions of transformations and shelf life. A Git pointer with no accessible object, or an expired snapshot, does not allow to rebuild the dataset actually used.

---

How to version a RAG index? <!--anki:5b24386779354f4f48-->
?
Keep an **Reproducible Manifest** documents/versions, Parseur, Chunking, embeddings and indexing parameters, with journal of additions, updates and deletions.

Example: Changing the embedding model requires an index that is consistent with the query vectors; toggling the alias before the end of construction exposes an incompatible mixture.

Also test back. Restoring an old index should not resurrect deleted documents or old access rights: apply current policies and reconcile deletions before exposure. A build date alone does not allow this reproduction.

---

Which production signals power the flywheel without human annotation? <!--anki:7a4a7a5b6b2153607d79-->
?
- **Reformulations** of the same question (first answer failed).
- **Scales** to a human and their resolution.
- **Changes** made by the user to the output (the final version is a fix).
- **Acceptance** or rejection of suggestions.
- **Verifiable** results (tests that pass, ticket resolved).

These signals are clues, not all labels: a reformulation can specify a need, and a modification can add a preference without correcting an error. Validate a sample and keep the provenance before using them to train.

---

What traps threaten a data flywheel? <!--anki:4d62452a5442293c4656-->
?
- **Selection Bias**: Only some users give feedback.
- **Self-reinforcing loop**: we only improve what we already measure.
- **Derivation of labels** if the annotation guide changes without re-labeling.
- **Consent** and **purpose**: Reusing conversations to engage requires a legal basis ([[154-gdpr-llm|RGPD]]).

Compare populations with and without feedback. If only expert users correct the outputs, training only on their corrections can improve their segment while degrading the beginners. Reserve a representative independent game to measure this displacement.

---

How to prioritize improvements from flywheel? <!--anki:7649423b5a6439217743-->
?
Compare **frequency, severity and correction cost** per family of failures. A rare but costly error can come before a frequent style defect. Keep a table of failure modes.

Example: Inappropriate tone in 8% responses, severity 1; wrong amount in 0.5%, severity 50. Illustrative scores frequency × gravity give 8 against 25: amounts pass first, although sixteen times less frequent.

Fix the weights with the trade and specify the uncertainty. A prohibited hazard remains blocking despite a low score. Keep a representative sample to measure the effects of corrections.

---

Why should a data flywheel keep examples of ordinary successes in addition to reported failures? <!--anki:6536303434346466643734383439326239353966313838356338346539303765-->
?
**signals** often over-represent active users, visible errors and irritating situations. Training only on these returns can move the model to the detriment of common uses.

Keep, with a suitable data policy, a representative sample of requests and a targeted set of difficult cases. Trace the collection rule and corrections made. Evaluate separately improvement of failures and regressions on ordinary traffic. A useful feedback loop increases the available information; it should not confuse frequency of complaints and frequency of real situations.

---

Why is positive feedback not always a proof of accuracy? <!--anki:6162366339623162656337343464636161353938633831343865643534636332-->
?
The user can appreciate **style, speed or an answer that confirms his opinion**, without checking the facts. A click or an inch measures a behavior, not directly the truth.

Link this signal to the task and complete it with evidence or annotations. Examine the false positives of feedback before using it to train. A poorly defined improvement loop can reinforce complacency rather than utility.

---

## Scenarios

Scenario: a competitor uses the same model as you, with the same public prompts. Where is your advantage built? <!--anki:642928604c4d28683850-->
?
1. **Not in the model**: it is buyable by everyone
2. **In the data**: traces, feedback, user corrections, evaluative games specific to your job
3. **In the loop**: capture failures, analyze them, correct and measure, turn after turn
4. **Integration**: access to internal systems, rights, business context
5. **Condition**: collect from the first day, with complete traces and common identifiers ([[151-data-curation-annotation|collecte]])

**Pip**: Throw without instrumentation, then discover six months later that we have nothing to improve.

---

Scenario: an eval score obtained three months ago is impossible to reproduce today. What hasn't been versioned? <!--anki:413f6b777e754d7a2d72-->
?
1. **The dataset** itself, which has been enriched since
2. **Prompt**, **Model** (Dated ID) and **Generation Configuration**
3. **The RAG** index and the **embedding** model used at the time
4. **The code of the evaluators** and the **prompt of the judge**
5. **The consequence**: a score without version of the game and the string does not make sense ([[114-reproducibility-variance|Reproducibility]])

**Strap**: Release the code and prompts, but let the eval game evolve continuously without a version label.

---

## Sources
- [Apache Iceberg — snapshot expiration and file retention](https://iceberg.apache.org/docs/latest/maintenance/)

## Connections
- [[97-evals-online-ab-testing|Evals online]] — collection in production
- [[113-monitoring-drift-feedback|Monitoring, drift & feedback]] — feedback loop
- [[151-data-curation-annotation|Curation & annotation]] — label chess
- [[111-mlops-llmops-fundamentals|MLOps & LLMOps]] — lineage and versioning
- [[114-reproducibility-variance|Reproducibility]] — replay an eval
- [[148-llm-batch-pipelines|Pipelines batch]] — line of generated outputs
- [[98-agent-debugging|Debugging agents]] — find the cause of a failure in a trace
- [[157-data-contracts-quality|Contrats & publication]] — make versions consistent and controllable
- [[158-ingestion-cdc-backfills|Ingestion & backfills]] — synchronize changes and rebuild indexes
- [[150-012-columnar-storage-lakehouse|Columnar storage, partitions & lakehouse]] — preserve physical versions needed for experiments
- [[150-017-ai-datasets-corpora|Building Datasets & Corpus IA]] — fix content, transformations and preservation
- [[00-moc-ai-engineering|MOC AI Engineering]]
