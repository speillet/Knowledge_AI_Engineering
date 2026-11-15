# — Training Pipelines, Register & Continuous Training — Flashcards
Tags: #flashcards #ai-engineering #mlops #classical-ml #pipelines
Verified on: 20 October 2026 — global date preserved; targeted review of 13 November 2026 detailed in Sources.
<!-- summary: MLOps maturity levels, deployed pipeline rather than model, planned or triggered retraining, data and model validation, MLflow experience tracking, signature, champion and challenger alias, registry or vendor alias, milestone cache, training window, scoring batch or online, model censored labels, expected performance calculation without labels, concurrent model promotions, trigger grouping, benchmarking, benchmarking and benchmarking. -->


What distinguishes the levels 0, 1 and 2 Maturity MLOps Described by Google Cloud? <!--anki:6539373632343731336431643433643839373035386566393038353034396538-->
?
- **Level 0**: manual steps, often in a notebook; the trained model is transmitted to the team that serves it. Validation can exist without automation or continuous monitoring.
- **Level 1**: An automated **pipeline** retrains the model on new data (*continuous training*), with data and model validation and runtime metadata.
- **2 level**: a **CI/CD pipeline components** quickly tests and delivers their new versions.

These levels measure the automation, not the relevance of the model. Aim for the one that corresponds to the actual frequency of changes: a model reviewed twice a year does not justify the 2 level.

---

At the 1 Maturity MLOps, What are they doing, Why does this change matter? <!--anki:6239633566363762336266323431363162663234636131653537623737316334-->
?
We deploy the **training pipeline** itself, which runs on a recurring basis and produces the models served, and no longer a hand-trained model file.

The pipeline code becomes a production software: it is tested, versioned and reread. Each model produced must be linked to the execution that created it: version of the pipeline, snapshot of the data, parameters and validation results. If a model regresses, the pipeline or its data is corrected. A "fast" retrainment launched outside the pipeline recreates an artifact that no one knows how to reproduce ([[111-mlops-llmops-fundamentals|lineage]]).

---

When to prefer a planned retraining to a retraining triggered by an alert? <!--anki:3730363132663964323961313461646138663763373962333639643165643037-->
?
The **planned** is suitable when mature labels arrive regularly, training costs are low, and the pipeline is already validated. Example: a weekly demand forecast retrained on sales for the past week.

The **trigger** is suitable when training is expensive or labels are scarce: measured performance drop, confirmed drift, new category. In both cases, the trigger initiates the pipeline, not the deployment: the promotion depends on the candidate's control over the model in place. A drift alert can also reveal a data incident that a retraining would learn faithfully ([[113-monitoring-drift-feedback|when to retrain]]).

---

What does data validation check at the start of an automatic retraining pipeline? <!--anki:6439393237356164613533323463643762623336316662383761356533393561-->
?
Control **scheme, semantics, volume, freshness and historical availability** of variables, as well as maturity, definition and coverage of labels. Compare validation rules to the intended use of the model.

A new category does not always impose a stoppage: the contract may provide for processing of the unknown tested, with alert threshold. A changed unit or an inconsistent key may block the publication. Classify anomalies as blocking error, quarantine or signal to be examined, with responsibility and explicit rule. Validating the same corrupted data in train and test can give a reassuring score; keep independent invariants and business references.

---

What checks must a retrained model pass before replacing the model in production? <!--anki:6639353939333063383366353465373861613231323564396266613433386230-->
?
Compare **applicant and reference** on games independent of their selection, with criteria set before the test: useful quality, segments, calibration, business constraints, cost and service. A margin of non-inferiority may be suitable for a less expensive candidate.

Test packet loading, preprocessing, signing, and output in the target image; measure latency and memory to target traffic. Associate historical reference and recent cohort to sufficiently mature labels. The failure of a gate keeps the version in place and opens an investigation. The pipeline produces a candidate; an error-free end of training does not constitute approval or proof that replicas serve the correct version.

---

What should be recorded in an experiment tracking run for a score to be comparable and repeatable? <!--anki:3530323230313931666636393436326239373363626566646335356361653532-->
?
Link **recipe, data, environment and results**, distinguishing training, selection validation and final test. Keep metrics by segment and artifact with its preprocessing.
```python
# MLflow 3; pipeline already configured, including its random_state.
import mlflow
import mlflow.sklearn
from mlflow.models import infer_signature
from sklearn.metrics import recall_score

with mlflow.start_run(run_name="retention-gbm"):
    mlflow.log_params({"seed": 42, "git_sha": sha,
                       "train_snapshot": "retention@s042"})
    pipeline.fit(X_train, y_train)
    pred = pipeline.predict(X_valid)
    mlflow.log_metric("rappel_validation", recall_score(y_valid, pred))
    signature = infer_signature(X_valid, pred)
    info = mlflow.sklearn.log_model(
        pipeline, name="model", signature=signature,
        input_example=X_valid.head(2),
    )
```
Logging a seed does not configure generators. Automatic capture depends on the integration and its configuration; it can include some data without replacing their business origin. Complete snapshots, splits, label definition and dependencies. Use the URI returned by logging rather than assuming an old file location.

---

What is the purpose of signing a registered model in MLflow, and what does it not verify? <!--anki:6239663931636263656563383439313061333262393861346664663238353164-->
?
The **MLflow signature** describes a contract of names, types, shapes, and parameters; an input example helps to document it and test inference. The loading path or serving and the flavor determine the validations actually applied.

This does not demonstrate any sense of units, quality, or validity of all business outputs. Testing absent fields, null values, unknown categories, order, and types with the packet reloaded. Inference from a single example may miss an important case: an entire column that has become floating due to missing values deserves a thoughtful schema choice, not a blind cast masking the error.

---

How to promote a model with MLflow registry aliases rather than with internships? <!--anki:6237353965653432306163353464366462386232306536656232646136313965-->
?
An **alias MLflow** is a mutable reference to a registered version; old stages are deprecated from MLflow 2.9. After validation, a controlled authority can move this alias:
```python
from mlflow import MlflowClient
client = MlflowClient()
client.set_registered_model_alias("retention", "champion", "8")
```
The operation modifies a reference, not all processes that have already loaded a model. Resolve the version, load or deploy explicitly and then verify replicas. Log version and release effective; an approval tag does not grant rights. Serialize competing promotions and keep proof of validation independent of the current alias.

---

Do not confuse: `champion` alias of a model register and model alias of a API supplier? <!--anki:3665306137636438626664313435393061633835316532633665333930616563-->
?
Both are editable **references**. The difference is who moves them, and when.
- The **Registry alias** is moved by your pipeline, after your checks. The change is plotted, dated and reversible.
- The **alias of the supplier** can change targets at its discretion, without commit or validation at home ([[113-monitoring-drift-feedback|API model Updates]]).

The first is a promotion mechanism; the second is a dependency to pin. In both cases, record with each prediction the version actually used, otherwise a regression cannot be assigned.

---

Why can the steps cache of an ML pipeline result in a model on outdated data? <!--anki:3037633031353233366638363432623838343764343563303136666137613632-->
?
The **Execution cache** can reuse an output when the key calculated from the inputs and parameters appears unchanged. In Kubeflow Pipelines, it is enabled by default but configurable on compilation, execution or by task.

A mutable path like `s3://data/fraude/latest/` can remain the same while its contents change: a step can reuse an old dataset. Provide snapshot or immutable manifest and explain dependencies. For a task that needs to reread an external source, disable its cache, for example `.set_caching_options(enable_caching=False)`. Check also the overrides of the run; a setting in the code does not prove the behavior of the execution actually launched.

---

How to choose the data window of a periodic retraining? <!--anki:3462653933633538646637613430653762333939313035373962633831633332-->
?
Compare **Sliding Window, Cumulative History and Decreasing Weight** by [[172-ml-validation-metrics|backtest temporel]]. The choice swaps adaptation to changes, seasonal coverage and number of rare events.

Example: a three-month window reacts quickly but can miss year-end purchases; twelve months cover them, while maintaining an old tariff regime. Neither wins in principle.

Check that the labels are available at each origin of the backtest, not only that the observations are old. Cover the useful diets within the allowed retention limit; after structural breakage, weighting or excluding the old diet may be preferable to accumulating more data.

---

Do not confuse: scoring batch and online scoring of a tabular model? <!--anki:3835666466363632393961653434633861313331316236373735636166633733-->
?
- **Batch**: Scores are pre-calculated periodically, for example every night for two million customers, then written with the model version and the calculation time. It is simple and inexpensive, but the score remains frozen until the next batch.
- **Online**: Score is calculated on request, with fresh variables and a latency budget, for example 50 ms at p99. It requires a service infrastructure and variables available online ([[159-temporal-data-features|features online]]).

Criterion: Does the decision depend on information that changes between two lots, such as the amount of an ongoing transaction? If so, batching is not enough.

---

Why does an anti-fraud model that blocks transactions deprive its successor of reliable labels? <!--anki:6331303431373561386338633430313738336436343962343634396137383666-->
?
When a decision determines **which issues become observable**, the labels are selective. Evaluating only accepted transactions describes this filtered population; this does not automatically reveal the result that would have been the blocked transactions.

An independent journal can provide another label or useful clues, without necessarily being the counterfactual outcome sought. Document the observation policy and the assumptions of an adapted collection or analysis. A weighting requires known or estimable probabilities of observation and recovery: if some cases have no chance of being observed, it does not create the missing information. Keep limits and populations covered before promoting a successor.

---

Calculation: a calibrated model evaluates 100,000 transactions. The sum of all its probabilities is 1,000; it reports 2,000, medium probability 0.35. What precision and what reminder to wait before the arrival of labels? <!--anki:6237633638313538633537333463346261373964633536353431323132653364-->
?
If the probabilities remain reliable **in the groups considered**, their sums give expected numbers:
```text
expected frauds reported = 2,000 × 0.35 = 700
estimated accuracy = 700/2,000 = 35%
estimated recall ratio = 700/1,000 = 70%
```
The last figure is a **expected workforce ratio**, not a general identity for the expectation of the observed recall. These estimates do not replace the labels. The overall calibration can mask poorly calibrated segments and does not automatically survive a drift of entries. Check selection, population and definition of the label, and then confirm on consolidated cohorts with uncertainty.

---

Why should a retraining pipeline prevent two competing candidates from promoting themselves simultaneously? <!--anki:3263663864393330636534653433386561653262663231393031643637376462-->
?
Two **promotion runs** can both compare their candidate to the same former champion, then replace the alias in an arbitrary order. The last one written is not necessarily the best validated.

Serialize the promotion or use a conditional update on the expected version of the champion. If it has changed, redo the decision according to the planned protocol. Keep candidate, reference, criteria and approval in a journal. The registry alias is a deployment pointer; its simplicity does not alone provide an arbitration between competing experiences.

---

How to prevent a burst of alerts from launching too many simultaneous retrainings? <!--anki:3735376337636234366261643436336438666436383539303030636466363666-->
?
A **trigger** can receive multiple events for the same drift or window. Without grouping, it produces competing workouts, consumes the budget and multiplies the candidates difficult to arbitrate.

Define a logical request identity, a grouping rule, a stabilization period and maximum concurrency. Verify data maturity and cost before launch. Keep the grouped signals for the investigation; a delay must not hide a critical incident. The protection of the complete triggering, without replacing it, the serialization of the promotion: limiting training does not decide which candidate will be served.

---

Why should the calibrator be integrated into the recipe and promotion of a model? <!--anki:3166353763353636393139323430393162396232366330393366643063363832-->
?
A **calibrator** learned about the scores of a given model does not automatically remain valid after retraining weights. The probabilities and decisions made from them may change even if the ranking improves.

Provide separate fit data according to the protocol, version model and calibrator together, and then evaluate the combination on an independent set. Also test the resulting threshold and review capability. Do not adjust the calibration on the final test to pass the gate. A promotion must identify the chain actually used, not just a main model accompanied by a mutable "current calibrator" file.

---

Why keep a historical reference and a recent cohort in the validation of a retraining? <!--anki:3838303336333435393930633465323138396133616264373736333963373363-->
?
The **historical reference** follows known regressions; the **recent cohort** provides information on the current population, if its labels are sufficiently mature.

Compare candidate and champion on the same cases of each game, with pre-specified criteria and uncertainty. A good historical score may miss a new scheme; a recent window alone may share a collection incident and forget about seasonal situations. Version composition and eligibility rules. As the target evolves, document the scope of comparisons instead of presenting any variation as an improvement of the constant objective model.

---

How do I process a label correction after a model is approved? <!--anki:3036313832353639623031303437323039663333303933303166366661643731-->
?
A **label correction** changes the evidence that supported the decision. Keep the historical report and create a new version of the corrected dataset, with the source, date and scope of the changes.

Recalculate the necessary comparisons on this version and examine whether the promotion or threshold remains justified. Do not silently replace the metrics of the old run: the audit must find what was known at the time of the decision. If the correction reveals a systematic defect, review collection, annotation and future training. A new data can trigger an investigation without automatically imposing the removal of the model.

---

When to cancel a workout that has become obsolete during its execution? <!--anki:3334333934383032323661323463373861623566393337316538643036323537-->
?
When a **data correction or new constraint renders its result unusable**, continuing can waste the budget and risk an outdated promotion.

Mark run as obsolete with reason, stop resources when possible and prevent its promotion. Keep the metadata useful for diagnosis. Do not systematically cancel any old run: a reproducible candidate can remain useful as a reference if his contract remains valid.

---

Why does retraining on test set errors require changing the evaluation protocol? <!--anki:3633626438623034313736353432303562383961633935356237646365616261-->
?
These examples become **development or training data**. Their improvement no longer measures an independent generalization.

Keep cases for non-regression, but reserve a new separate and versioned confirmation set. Trace the examples used in each step. A continuous loop can accumulate a leak gradually, even without an explicit copy of the entire test in training.

---

## Scenarios

Scenario: a churn model is retrained every week by a hand-launched notebook, and no one knows how to reproduce the version in production. How do you pass it at the 1 level without rewriting everything? <!--anki:6136386535333361656532623434353639343966373363373966373433356132-->
?
1. **Measure the current version** on a frozen test set: it becomes the reference, even if its lineage is lost.
2. **Extract notebook steps** into components: data validation, features, training, evaluation, with an immutable snapshot as input.
3. **Trac each run**: experience tracking run, version registered in the registry, alias `champion` for the version served.
4. **Add promotion control**: comparison to the champion on cohorts with mature labels, by segment.
5. **Plan the pipeline** and keep manual promotion until controls are proven.

**Pip**: Automate deployment before having reliable data and model validation.

---

Scenario: a drift alert triggers an automatic retraining, the new model is promoted and the false positive rate doubles. What happened, and what do you change? <!--anki:6262336333663362303734653438666661643333663261333665326134373762-->
?
1. **Go back**: Replace the alias on the previous version and check that the services have reloaded it.
2. **Search for a data incident** behind the drift: unit, join, missing source ([[157-data-contracts-quality|drift or incident]]).
3. **Review promotion control**: A test from the same corrupted window validates a corrupted model.
4. **Strengthen the pipeline**: validation of blocking data, fixed reference set, thresholds by segment.
5. **Uncouple trigger and promotion**: go through a shadow comparison or a canary before the toggle.

**Trap**: Treat each drift alert as an order to retrain.

---

Scenario: an anti-fraud challenger earns 3 accuracy points in backtest, but it has been trained and evaluated only on the transactions accepted by the champion. Do you deploy it? <!--anki:3063653432316631653734323433623761303564353037653962653835336561-->
?
1. **Defining the target population** and the outcome actually assessed: detection of an index, observed unpaid or effect of a decision.
2. **Identify missing labels by construction**, including systematically blocked cases.
3. **Study a collection or an adapted analysis plan** with its hypotheses; a human review is not automatically the counterfactual outcome.
4. **Use the shadow for contracts and volumes**, without awarding it labels that it does not produce.
5. **Decide within the supported perimeter**, after risk control, label deadlines and business metrics.

**Trap**: announce a generalizable gain of three points on a filtered population, or believe that a weighting repairs a total lack of recovery.

---

## Sources
- [Google Cloud — MLOps: Continuous Delivery and Automation Pipelines in ML](https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning)
- [MLflow — Model Registry workflow, alias and internship depreciation](https://mlflow.org/docs/latest/ml/model-registry/workflow/)
- [MLflow — model signatures and input validation](https://mlflow.org/docs/latest/ml/model/signatures/)
- [Kubeflow Pipelines — Hides Executions](https://www.kubeflow.org/docs/components/pipelines/user-guides/core-functions/caching/)
- [Lakkaraju et al., The Selective Labels Problem, KDD 2017](https://pmc.ncbi.nlm.nih.gov/articles/PMC5958915)

- [MLflow — migration vers MLflow 3](https://mlflow.org/docs/latest/ml/mlflow-3/) — `name=` and Model URI returned by logging.
- [MLflow — API scikit-learn](https://mlflow.org/docs/latest/api_reference/python_api/mlflow.sklearn.html)

Targeted review of 13 November 2026: affirmations specified in this pass; other content is not fully verified.

- [Kubeflow — cache settings and priorities](https://www.kubeflow.org/docs/components/pipelines/user-guides/core-functions/caching/) — a submission parameter can override the per-task setting.

## Connections
- [[111-mlops-llmops-fundamentals|MLOps & LLMOps — Fundamentals]] — register, lineage and versioning applied here to the classic ML
- [[112-model-cicd|CI/CD models]] — shadow, canary and rollback of a pipeline-promoted model
- [[113-monitoring-drift-feedback|Monitoring, drift & feedback loop]] — the signals that trigger the pipeline
- [[157-data-contracts-quality|Contracts & data quality]] — distinguish real drift and incident before retraining
- [[159-temporal-data-features|Temporal data]] — online labels and variables maturity
- [[150-013-data-pipeline-orchestration|Orchestration data]] — immutable inputs, recoveries, and data intervals
- [[172-ml-validation-metrics|Validation ML]] — backtest and time validation of windows
- [[173-calibration-uncertainty-abstention|Calibration]] — performance rating condition without labels
- [[174-recommendation-ranking|Recommandation & ranking]] — exposure bias, cousin of selective labels
- [[99-statistics-experimental-decisions|Statistics to decide]] — significant gain against the champion
- [[118-ml-artifacts-registry-releases|Artifacts, registry and releases ML]] — production contracts and verifications
- [[119-prediction-contracts-features-batch|Prediction contracts, features and batch]] — production contracts and verifications
- [[00-moc-ai-engineering|MOC AI Engineering]]
