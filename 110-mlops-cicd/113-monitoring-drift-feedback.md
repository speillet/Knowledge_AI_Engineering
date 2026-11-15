# Monitoring, drift & feedback loop — Flashcards
Tags: #flashcards #ai-engineering #mlops #monitoring #drift #llm
<!-- summary: data drift and concept drift, PSI and calculation, KS test on large volumes, multivariate drift, score distribution, drift of a LLM app and a RAG, quality in production, feedback loop, when to re-train, regular annotation, updates of the API models, trend and segment alerts, through the late labels, fixed and sliding version references, definition. -->


Do not confuse: data drift and concept drift? <!--anki:693a4558422d7246257a-->
?
- **Data drift**: the distribution of **inputs** changes (new topics, jargon)
- **Concept drift**: the **relationship input → expected output** changes (the "good" behavior evolves)

Example of data drift: more requests in a new language. Example of a drift concept: a trade rule changes and an old correct response becomes false. A stable input distribution does not exclude a drop in quality. Measure the two separately and look for the cause before modifying or retraining the model.

---

How does the Population Stability Index (PSI) measure the drift of a variable? <!--anki:3839353839393939643139353462396362656138386437353365636534333832-->
?
The **PSI** compares the `e_i` and current `a_i` reference proportions in defined classes:
```text
PSI = Σ (a_i − e_i) × ln(a_i/e_i)
```
The 0.1 and 0.25 marks are conventions of certain uses, not universal statistical thresholds or proofs of quality.

A zero proportion requires an explicit rule: documented grouping or smoothing, with consistent normalization. The index depends on this choice and the breakdown. Inspect which classes change and their impact; the univariate PSI does not detect any drift of correlation or relationship between input and label.

---

Calculation: with PSI = Σ (a − e) × ln(a / e), which index for a variable whose three classes change from 50 / 30 / 20% to 40 / 30 / 30%? Is the population stable? <!--anki:3938656564616631313236303437343839646338666166616664333161326363-->
?
```text
(0,40 − 0,50) × ln(0,40 / 0,50) = −0,10 × −0,223 ≈ 0,022
(0,30 − 0,30) × ln(1)            = 0
(0,30 − 0,20) × ln(0,30 / 0,20) =  0,10 ×  0,405 ≈ 0,041
PSI ≈ 0.063
```
Under the mark of 0.1, we would speak of population **stable**. Yet the last class has gained half its weight, from 20 to 30%. If it groups the large amounts, where the model is the most mistaken, the business effect can be important.

A global index is thus completed by examining the classes that move and their share in the errors of the model.

---

Calculation: with 100,000 observations in each window, what deviation from Kolmogorov-Smirnov becomes significant at 5%, if D_write ≈ 1.36 × √((n + m) / (n × m))? What to conclude? <!--anki:3761623161306136393831653465323938323161346461613065613732366361-->
?
```text
D_crit ≈ 1,36 × √(200 000 / 10¹⁰) = 1,36 × 0,0045 ≈ 0,006
```
A maximum deviation of **0.6 point** between the two distribution functions is enough to reject the equality. On large volumes, almost each variable "drifts" in the sense of the test, even when the deviation has no effect.

Conversely, with 50 observations per window, the threshold goes up to 1.36 × √(100 / 2,500) ≈ 0.27: a significant drift goes unnoticed. The p-value tells if the distributions differ, not if the gap counts. Instead, follow an effect size, such as D, the PSI or the Wasser distance.

---

How to detect a multivariate drift that variable-by-variable controls do not see? <!--anki:3963393735306536386535613433613239383466366437643030343639303937-->
?
A **domain classifier** learns to distinguish between the reference period and the recent period. A good separation out of training indicates a detectable change with the chosen variables and model.

An AUC close to 0.5 does not prove the identity of the populations: low power or unsuitable model can hide a difference. Remove identifiers and dates that make the problem trivial; respect groups and temporal dependencies in the validation. Examine interactions and examples responsible for separation. The AUC measures the detectability of the difference, not its business cost or a certain decrease in accuracy; quality requires a complementary measure.

---

Why monitor the distribution of a model's scores in addition to its input variables? <!--anki:3731316566643535353330663439373962336264626566383836366234356634-->
?
The **score distribution** summarizes the drifts that count for this model: a little used variable can move without effect, while a shift of the scores directly affects the decisions. It is available immediately, without waiting for labels.

Follow in particular the **part above the decision threshold**: if it goes from 2 to 5%, the human review queue is multiplied by 2.5, even if the quality remains correct. Limit: stable scores do not exclude a drift of concept, where the same scores correspond to other issues. Only labels, even late, reveal it.

---

How does the drift manifest on a LLM app? <!--anki:4477547a5d582b2a403a-->
?
A LLM application can change **population of requests, context, or behavior** without technical errors: new topics, modified documents, removed rights, different tool, or vendor review.

Decompose the string before concluding that the model is degraded. Compare entries, passages retrieved, versions, tool decisions and results, by segment. A embeddings shift or a new refusal rate is a signal of investigation; it does not directly measure accuracy. Known probes and a representative annotation complete the automatic indicators. Neither stable scores nor intact availability prove that the answers remain useful and authorized.

---

How to monitor the quality of a LLM application in production? <!--anki:786d2e5876493b586624-->
?
Combine **Inexpensive Complete Controls** and **Annotated Samples**: Formats, Tool Errors, Citations, and Verifiable Effects on one side; Accuracy and Useful Satisfaction on the other; Link results to the version actually executed.

Announce population, sampling mode, coverage and uncertainty by segment. A judge may run out of references or fail; his or her lack of score is not a success. Separate rate observed on judged tracks and estimate of traffic. Cases targeted on incidents are used for diagnosis, without becoming automatically representative. Complete with probes and human returns, whose biases and delays remain to be measured.

---

What is the feedback loop of a LLM application? <!--anki:7568493c4c666036326e-->
?
```text
Traces Prod → curation → Golden Datasets
→ evals more loyal → prompts/fine-tuning improved
```
Production data **feeds** continuous improvement.

**curation** turns a raw signal into an actionable example: check for error, remove unnecessary data, produce a reference, and choose the right game. Keeping an independent test avoids optimizing only incidents that have already been seen. Measuring after deployment whether the correction actually improves usage without degrading other segments.

A negative thumb does not provide the right answer. Annotating the cause before training: factual error, excessive delay and user disagreement require different corrections.

---

When to retrain or tune a model again in production? <!--anki:69216450773565735339-->
?
**On signal**, or at a rate justified by the regular arrival of labels ([[117-continuous-training-pipelines|planned or triggered]]):
- Fall of scores on a segment
- Drift of entries detected
- New use cases or new categories
- New, more efficient base model

Before retraining, check that the problem is not solved more simply: prompt, retrieval or freshness of the index ([[51-fine-tuning-adaptation|fine-tuning]]).

Also check that the signal does not come from a data incident: retraining on a broken source causes the model to learn the error. Retraining produces a **candidate**; its commissioning remains subject to comparison with the version in place.

---

What is the drift equivalent for a RAG system? <!--anki:623f3a36415d4739725d-->
?
A RAG can be derived at several levels: **obsolete sources**, missynchronized index, question change, modified permissions, or loss of recall after changing embeddings.

Follow ingestion dates, deletions, question coverage, and quality of retrieved passages. If the right source exists but is no longer found, re-ingesting more is not enough: check index, filters, trimming and search pattern ([[22-advanced-rag|RAG in production]]).

---

Why are API model updates a risk? <!--anki:4a50656f363156493461-->
?
The provider **updates or depreciates** the models: the behavior changes without commit in you → **pin the versions** and re-play the evals with each change.

A stable alias can point to a different version, and a dated identifier can eventually be removed. Maintain a migration procedure: compare on the same set of evals, check formats and tools, deploy gradually and plan a fallback solution. Pinning reduces implicit changes without removing depreciations.

---

What role for humans in the production loop? <!--anki:695e2a5b4b652e41353c-->
?
Humans **note, referee, and review criteria**, but their labels may also be erroneous or ambiguous. Use a grid, verifiable sources, and a disagreement procedure ([[151-data-curation-annotation|annotation]]).

Example: Reserve part of the weekly 50 traces to a representative sample and another to rare incidents. The targeted cases reveal defects, but their error rate does not directly represent all the traffic.

Annotations are used to estimate the quality and calibrate the judges; keep an independent game instead of training and evaluating on the same corrections.

---

How to alert about a drop in the quality of a LLM application in production? <!--anki:724b5141763b4c37746b-->
?
As on availability: **thresholds** on quality scores, refusal and error rates, latencies, **by segment**, related to the [[64-inference-metrics-slo|SLO]].

Precautions: alert on a **trend** (slippery average over several hours) rather than on an isolated point, because the sample scores are noisy, and attach to the alert the **examples of traces** to diagnose quickly.

Include actual evaluated and coverage: A stable average calculated over half of the queries can mask a judge outage. Critical incidents, such as a confirmed data leak, require a reaction without waiting for a trend.

---

Why can the quality of a model seem to rise when its labels arrive late? <!--anki:3239653832366562656333633434616662636365653761303833633064313739-->
?
**early available labels** may be for easy cases, while disputed frauds or late terminations remain unsuccessful. Evaluating only already arrived labels then selects a favorable population.

Form cohorts according to the decision date and wait for a defined maturity for the final metric. Separately track arrival time and proportion of missing labels per segment. Early indicators remain useful, but need to be identified as such. An apparent improvement may reflect the change in label availability rather than a better model.

---

Why compare both a fixed reference and a sliding reference to monitor the drift? <!--anki:3635343665373535313233633435373362376662623331643838346536646130-->
?
A fixed **reference** retains a historical comparison point; a sliding **reference** further describes the recent regime. Each can hide a problem if used alone.

The fixed reference can alert to an expected seasonality; a sliding window can gradually absorb a degradation and make it invisible. Define populations, seasons and renewal rules, and then version the references. Keep also business metrics and data controls: the proximity to yesterday does not establish that the model remains useful. Modify the reference must be an explicit decision, not an automatic way to make alerts disappear.

---

Why version the label definition in ML monitoring? <!--anki:3861343533633232386536363433666538366139313866616231663766336262-->
?
A **label** depends on a rule: horizon of termination, definition of an incident or arbitration procedure. If this rule changes, the metrics can change even with the same predictions and without new default of the model.

For example, comparing churn to thirty days and churn to sixty days mixes two targets; an unripe file does not become a negative. Recalculating a historical series under a new definition requires a new measurement version. Keeping old reports to understand which promotion decision was based on which target.

---

Calculation: on 1,000 predictions, 600 labels are available and 480 of these predictions are correct. How accurate and what coverage can be announced? <!--anki:3839653031333039646534393465306138653939383964656161363736653766-->
?
The **accuracy observed on labeled cases** is `480/600 = 80 %`. The **label cover** is `600/1 000 = 60 %`.

80% cannot be reported directly on all traffic: 400 cases without a label can be more difficult, more recent or selected by the decision of the model. Reporting the two denominators and the maturity of the cohorts. Examining the rule of observation and uncertainty, then waiting or collecting appropriate information. Treating absences as successes, failures or negatives makes a field truth that has not been observed.

---

How to monitor a model when the evaluator or label collection fails? <!--anki:6231626434613731653764313430353038373839363464643631313564663063-->
?
Also monitor the **measurement chain**: number of predictions, expected and received labels, attempted and completed evaluations, age of latest observations and reconciliation errors.

Distinguish between healthy, non-compliant and unknown state. A fixed metric may reflect the stop of the calculation rather than a stability of quality. Provide an alert and an operating policy for this loss of visibility, depending on the criticality. Continue the available controls, such as formats and latency, without presenting them as proof of predictive performance. Test judge failure or label delay with probes whose expected result is known.

---

Why can an apparent drift come from the action of the model itself? <!--anki:3233303166356337336639323461326639393362393065343539386162653032-->
?
The model changes **decisions and therefore future data**. A retention offer can reduce terminations observed precisely among customers estimated to be at risk.

Linking prediction, action, and outcome, then distinguishing population change from policy effect. A decrease in termination rate is not automatically an improvement in calibration. Comparison groups or a collection designed for identification are required for some conclusions.

---

How to distinguish an expected seasonality from a worrying drift? <!--anki:3433653833363331333432623466613361366266626130363635386534326231-->
?
Compare to **comparable periods and segments**, for example same weekday or season, and then examine the effect on quality and decisions.

Keep a fixed reference to see background changes and a seasonal reference to avoid repetitive alerts. Do not normalize any variation to the point of hiding an incident. Thresholds should reflect volumes, uncertainty and business cost.

---

## Scenarios

Scenario: your HR assistant has been working well for six months. For three weeks, users have found it "next to the plate", without any deployment having taken place. What causes do you explore? <!--anki:433d3b33593952674f29-->
?
1. **Entries drift**: new subjects arrive (reform, new internal policy) and leave the covered area
2. **Fresh index**: documents have changed, but re-ingestion did not follow ([[22-advanced-rag|RAG in prod]])
3. **Update on the supplier side**: the model behind the alias has changed, without committing at home
4. **Measure**: sample scores, refusal rate, feedback, segmented by subject
5. **Correct and prevent**: pin versions, automate re-ingestion, alert on scores by segment

**Trap**: conclude a regression of the model without having looked at the freshness of the data.

---

Scenario: you want to turn production failures into continuous improvement, without spending your weeks there. How do you organize the loop? <!--anki:7732497b69286a71417d-->
?
1. **Capture**: negative feedback, validation failures, low confidence, escalations ([[93-monitoring-inference|Signals]])
2. **Sample** rather than process everything, prioritizing high-volume or high-risk segments
3. **Annotate** a regular batch with a business expert, which also calibrates automatic judges
4. **Verify** these cases to golden dataset, distinguishing non-regression and hard cases ([[94-evals-methodology|evals]])
5. **Trigger corrections on signal**, not on calendar: prompt, retrieve, or fine-tuning depending on the cause

**Trap** : collect feedback without ever doing anything, which discourages users from giving it away.

---

Scenario: your drift dashboard displays forty variables in red every Monday, and the team has stopped looking at it. How do you make it useful? <!--anki:3732316464366435656539343430386639376433366131613165306561653466-->
?
1. **Replace p-values** with effect sizes, with thresholds set according to business impact.
2. **Priority according to model**: important variables, distribution of scores, share above the decision threshold.
3. **Choose a comparable reference**: same day of the week or season, so as not to alert to a normal rhythm.
4. **Check the pipeline first**: diagram, volume, units, before concluding a real evolution ([[157-data-contracts-quality|drift or incident]]).
5. **Link each alert** to an owner, an impact estimate, and a planned action.

**Trap**: raise all the thresholds to silence, and miss the real drift.

---

## Sources

- [Rabanser et al. — Failing Loudly, NeurIPS 2019](https://papers.neurips.cc/paper_files/paper/2019/hash/846c260d715e5b854ffad5f70a516c88-Abstract.html) — detection of distribution changes and limits.
- [Taplin and Hunt — Population Stability Index Limits, 2019](https://www.econstor.eu/bitstream/10419/257891/1/risks-07-00053.pdf) — sensitivity to near-zero frequencies.
- [Google SRE — design measurement and alerts](https://sre.google/workbook/monitoring/)

## Connections
- [[91-langfuse-observability|Langfuse]] — traces, scores and datasets of prod
- [[92-chainforge-evals-prompts|Evals]] — Measuring Instruments
- [[112-model-cicd|CI/CD models]] — redeploy after fix
- [[51-fine-tuning-adaptation|Fine-tuning]] — response to behavioral drift
- [[22-advanced-rag|Advanced RAG]] — index freshness
- [[93-monitoring-inference|Monitoring of inference]] — validations and quality signals in production
- [[115-agent-platforms-governance|— Agent Platforms Architecture & Governance]] — SLO and agent metrics
- [[153-data-flywheel-versioning|Data flywheel]] — loop on failures
- [[97-evals-online-ab-testing|Evals online]] — production signals
- [[111-mlops-llmops-fundamentals|MLOps & LLMOps]] — life cycle and versioning of LLM systems
- [[114-reproducibility-variance|Reproducibility & variance]] — non-determinism and eval statistics
- [[157-data-contracts-quality|Operational quality]] — distinguish data incident and real drift
- [[159-temporal-data-features|Temporal data]] — interpret delays and incomplete labels
- [[173-calibration-uncertainty-abstention|Calibration, uncertainty & abstention]] — monitor the validity of probabilities
- [[176-anomaly-detection|Detection of anomalies]] — distinguish incident and reference evolution
- [[117-continuous-training-pipelines|Training Pipelines & Continuous Training]] — from drift signal to controlled redrive
- [[119-prediction-contracts-features-batch|Prediction contracts, features and batch]] — production contracts and verifications
- [[00-moc-ai-engineering|MOC AI Engineering]]
