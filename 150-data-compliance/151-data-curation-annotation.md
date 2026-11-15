# Data: curation & annotation — Flashcards
Tags: #flashcards #ai-engineering #data #annotation #quality
<!-- summary: quality dimensions, deduplication, annotation guide, inter-annotators agreement, which annotates, active learning, dev and test separation, production data, preparation of a fine-tuning, review of the guide after disagreements, auction, label uncertainty. -->


Why do data remain decisive in the era of pre-trained LLMs? <!--anki:7a61323b38504268346f-->
?
Because the **Differentiation** of an application comes from its data: documents of RAG, **eval games**, Examples few-shot, Data from **fine-tuning**, User feedback. A state-of-the-art model on poorly distributed documents or poorly labeled evals gives a **Bad system**.

Example: if the tables of the contracts are flattened to parsing, no model will find the right amount; changing the model will do nothing, repair the parsing if. Before accusing the model, check on some failures if the right information appeared, legible, in what it received.

---

What dimensions of content to check on a dataset? <!--anki:473b29623d24767e4a36-->
?
- **Exactness** of labels or responses.
- **Cover**: all use cases, languages, difficulty levels.
- **Representative** to actual traffic.

Check a sample by segment rather than just a global average. An exact but easy-to-request corpus does not learn or measure exceptions properly. Write an annotation guide, examine disagreements, and keep difficult examples; the reference itself may be ambiguous or erroneous.

---

What dimensions of hygiene and compliance should you check on a dataset? <!--anki:427675662e7457574a7c-->
?
- **No duplicates** and leaks between training and testing.
- **Freshness** of the data.
- **Compliance**: user rights, PII, consent.

Also deduplicate paraphrases and documents from the same source before separating training and testing. Trace provenance, license, purpose and applicable legal basis; consent is not the only possible basis. Define updates and deletion, because a game conforms and relevant to its creation can cease to be.

---

Why and how to deduplicate a training or eval dataset? <!--anki:733b53586434355f6835-->
?
Duplicates can **overweight some sources**, waste computation or create a leak between train and test. Start with source identity and standardized content footprints; then detect near-duplicates with a validated method and threshold.

Do not automatically assimilate semantic proximity and identity: negations, numbers and versions sometimes change the correct answer. Keep the provenance of groups and define the appropriate split unit. Some repetitions are legitimate; decide what you want to correct, then measure the effect on coverage and evaluation rather than indiscriminately delete everything that looks alike.

---

What is a good annotation guide? <!--anki:716b3a504a62423d5e4b-->
?
- **Precise** definitions of each label, with **positive and negative examples**.
- Treatment of **Case Limits** to **Uncertainty** (label “uncertain” rather than forcing a choice).
- **Iterated**: we annotate a pilot, we measure the disagreement, we specify the guide, we start again.

A frequent disagreement often reveals a **Poorly defined criteria**, Not a bad annotator.

Annotate the same examples without consultation before arbitration. Versioning the rules and noting the reasons for disagreement makes it possible to distinguish evolution of the guide, real ambiguity and individual error.

---

How to measure the inter-annotator agreement? <!--anki:416b7945232c3f326648-->
?
Annotate **independently the same sample**, then measure raw chord, disagreements by class and adapted coefficient: Cohen kappa for two annotators, Krippendorff alpha for more general configurations.

For example, if a class represents 95% of cases, a strong raw agreement may mostly reflect this prevalence. Corrected coefficients use an expected agreement model, but remain sensitive to distribution and protocol.

A weak chord signals ambiguity, difficulty, or insufficient formation; it is not a **universal mathematical ceiling** for a [[95-llm-as-judge|juge LLM]]. Build an arbitrated reference and document uncertainty rather than automatically declare an infallible annotator.

---

Who should annotate the data of a LLM project? <!--anki:655759474a3971454429-->
?
- **Business experts** for criteria that require skill (medical, legal, code) expensive but indispensable — on the reference eval set.
- **Trained annotators** (internal or service providers) for volumes.
- **LLM** pre-annotating, **validating humans**: strongly accelerates but introduces the bias of the model (humans tend to accept the proposal).

A blind check of the initial proposal, on a sample, helps to reveal the anchoring bias introduced by the automatic pre-annotation.

---

What is active learning applied to LLM? <!--anki:797d785a307d35426a60-->
?
Prioritize the examples **the most informative** Those where the system is **Uncertain**, Where the judges **Divergent**, where the user has given a **Negative feedback**, or who are **Underrepresented**. We get more value per hour of annotation than with a random sample.

For one LLM, Uncertainty is identified by the disagreement between several generations, weak logprobs on the extracted fields or a judge who hesitates. Limit: a game built in this way overrepresents difficult cases; it serves to improve the system, not to estimate its average quality ([[95-llm-as-judge|sampling bias]]). Reserve a portion of the hours, for example 30%, to a random draw.

---

Why should development and testing games be strictly separated? <!--anki:622f5d2e6a734231353e-->
?
If one adjusts prompt, few-shot or fine-tuning by looking at the test set, it becomes a **disguised training set**: the scores **overestimate** the actual performance. We iterate on a **dev set**, we consult the **test set** only for the final decisions, and we **renew** periodically.

Separate also by documentary family, client or period according to use: a translation of the same contract in train and test remains a leak. The renewal does not retroactively repair a score already contaminated; keep its status and its history.

---

What production data should be collected at launch? <!--anki:77423d7b6a6a503e387d-->
?
The **Complete Traces** (Entries, context recovered, calls of tools, exits, Prompt and model versions), on the **Feedback** and the **corrections**, with **Trace ID** Common — in respect of the [[152-pii-privacy|Privacy]]. Without them, impossible to build the evals and the [[153-data-flywheel-versioning|flywheel]].

Fix from the start **retention period and access rights**, and check the legal basis that allows to reuse these traces to improve the system ([[154-gdpr-llm|RGPD]]). Catching these decisions after the fact often requires to purge months of data, therefore to lose the material of future evals.

---

How to prepare data for a fine-tuning? <!--anki:46607e4c3f4754636c5a-->
?
- Format **conversational** identical to that of the inference (same [[132-tokenization|chat template]], same tools).
- **Quality > quantity**: a few hundred to a few thousand excellent examples are often enough in SFT.
- **Diversity** of cases, including desired refusals and abstentions.
- Withdrawal of **PII**, deduplication, **validation game** separated.

Inspecting a sample after tokenization, not just the source JSON: truncated response, poorly serialized tools, and masked labels can undo the quality of the curation.

---

Calculation: 2,000 examples require 3 minutes each to 80 €/h, and 20% are annotated a second time at the same cost. What budget out of preparation and arbitration? <!--anki:3334646132633937623364663461373839383536306436313733656235646261-->
?
Assumptions: 3 minutes for example, expert at 80 €/h, double annotation of 20% examples to measure the chord.
```text
annotation    : 2 000 × 3 min = 100 h × 80 €/h = 8 000 €
double (20 %) :   400 × 3 min =  20 h × 80 €/h = 1 600 €
total ≈ 9,600 €, plus annotation guide
```
This is the price of a reliable reference eval set: we reserve the experts in cases where expertise counts, and we go through trained annotators or a pre-annotating LLM for volume ([[94-evals-methodology|golden dataset]]).

The double marking is used to observe disagreements; it does not guarantee the accuracy of the labels. Provide pilot, arbitration of ambiguous cases and revisions of the guide; these activities add time to the arithmetic cost calculated.

---

Why does the arbitration of annotation disagreements sometimes have to modify the guide rather than just choose a winning annotator? <!--anki:3163383032333537306164623436333138396332626664353630666139336637-->
?
A **recurring disagreement** can reveal an ambiguous definition of the target, not a poor performance of the annotators. Slice each case without reviewing the rule reproduces the problem.

Group disagreements by cause, clarify criteria, and add limit examples to the guide. Re-annotate an affected sample with the new version and measure the agreement obtained. Keep the origin of the labels and distinguish actual ambiguity from error. A test reference may admit several justified answers; forcing an artificial consensus masks the uncertainty that the model will have to handle.

---

What is the purpose of an auction after an annotation disagreement? <!--anki:6430313830346563616130333437323039303735373031383831356332313431-->
?
It seeks **a reasoned decision according to the guide**, or identifies an ambiguity to be retained. It is not just about getting more people to vote.

Examine the evidence, clarify the rule, and re-annotate the examples if necessary. Trace the change in the guide. Some data remains undecidable; imposing a certain label on it can teach the model an artificial rule.

---

Why keep the annotators' reasons for abstention? <!--anki:6264346537346235393236633438306439663461663932653463323364366162-->
?
They distinguish between **missing evidence, ambiguous instructions and out-of-scope cases**. These causes require different actions on the corpus or the product.

A simple "unannotated" field hides this information. Measure the frequency by source and segment, then improve collection or guide. Do not systematically remove these cases from the test: the production system may encounter them and will have to abstain correctly.

---

## Scenarios

Scenario: two annotators disagree on a third of the cases of your eval game. What do you do? <!--anki:7868723a7777786f4966-->
?
1. **Do not blame annotators**: frequent disagreement reveals above all an ill-defined **criterion**
2. **Measure** the agreement with a metric that corrects chance (kappa), rather than a gross percentage
3. **Resume guide**: definitions, positive and negative examples, treatment of borderline cases, option "uncertain"
4. **Re-annotate a driver** and check that the agreement is up
5. **Pulling a marker**: an automatic judge can do no better than human agreement ([[95-llm-as-judge|juge]])

**Trap**: decide the disagreements yourself and freeze an eval game whose criteria remain unclear.

---

Scenario: you have 40 business expert hours to annotate. How do you best use them? <!--anki:6b4b4c7930443c425326-->
?
1. **Do not shoot at random**: give preference to the most informative examples
2. **Target** cases where system is uncertain, judges differ, users have reported a problem
3. **Cover under-represented segments**, to avoid an eval game that ignores portions of traffic
4. **Pre-annotate with a LLM** and validate, knowing that it biases towards acceptance
5. **Protect test set**: iterate on a dev set, only check the test for final decisions

**Trap**: expend expertise on easy cases that the system already handles well.

---

## Connections
- [[94-evals-methodology|Evaluation methodology]] — the golden dataset
- [[53-synthetic-data-distillation|Synthetic data]] — complete the actual data
- [[152-pii-privacy|PII & Privacy]] — protect data
- [[153-data-flywheel-versioning|Data flywheel & versioning]] — bring data to life
- [[51-fine-tuning-adaptation|Fine-tuning]] — training use
- [[95-llm-as-judge|LLM-as-a-judge]] — automatic labels to validate
- [[156-responsible-ai|IA responsable]] — bias, fairness and transparency
- [[171-ml-model-selection|ML Classic]] — define a supervised target and its variables
- [[172-ml-validation-metrics|Validation ML]] — avoid leaks and choose data cutting
- [[157-data-contracts-quality|Contracts & data quality]] — validate schema, business sense and batch coverage
- [[176-anomaly-detection|Detection of anomalies]] — organize the confirmation of incidents
- [[150-017-ai-datasets-corpora|Building Datasets & Corpus IA]] — linking editorial quality and corpus construction
- [[00-moc-ai-engineering|MOC AI Engineering]]
