# Classic ML: Validation, Leaks & Metrics — Flashcards
Tags: #flashcards #ai-engineering #classical-ml #validation #metrics
<!-- summary: Train-validation-test, leaks, cross-validation, groups and times, pipelines, rare classes, ROC and PR, precision calculation according to prevalence, thresholds and uncertainty, balanced-accuracy calculation, macro and micro, pretreatment in folds. -->


Do not confuse: Supervised ML training, validation and final testing? <!--anki:6663653365326138306266653464653739373832333133616230333730393964-->
?
The **train** is used to learn parameters and transformations. The **validation** is used to choose model, hyperparameters and threshold. The **final test**, kept away from these decisions, estimates the quality of the chosen system.

Watching the test after each test makes it progressively a validation game. Documenting decisions and reserving an independent test for conclusion. After this measurement, a possible retraining on more data creates another artifact: specify what has actually been evaluated and then deployed.

Imputation and normalization are also learned on the train: calculating them on all data before the split introduces a leak even without using the labels.

---

What forms of data leakage can make an ML assessment misleading? <!--anki:6539316435373633373665653463353461386435376536363636663864346434-->
?
A leak introduced from the **Inaccessible information in real prediction conditions**. This includes a variable produced after the exit, copies of the same example on both sides of the split or pre-treatment adjusted from the test.

For a score calculated at the opening of a ticket, its final team and closing time are suspect. Audit the availability of each variable, not just its name. An exceptional score must trigger a protocol check before being presented as an advance of the model.

---

When to use cross-validation instead of a single split? <!--anki:3336663630323466306532343465666262383761386433336663333663613365-->
?
When the data are limited and several plausible splits would help to compare the models. In **k-fold**, we drive on k−1 parts and we evaluate on the remaining part, repeating for each part.

Splitting must represent deployment: random folds do not automatically suit groups or time. Re-process and select variables in each fold train. Fold scores are not independent, as their training sets overlap; their dispersion is not a universal confidence interval.

---

When should data be separated by group rather than line? <!--anki:6165343635636164623837383434323638373165356565376534663736396237-->
?
When several lines share a **entity or a source** whose model could recognize the particularities: patient, client, document or machine. If the goal is to generalize to new entities, their lines must not be present simultaneously in the train and the test.

Define the group according to the actual dependency risk. If the service predicts the future of already known customers, a time split may be more appropriate. The question is to reproduce the type of novelty encountered in production, not to always apply the same split.

---

How do I validate a model that predicts future events? <!--anki:6339643833353038363830353461663938653632316366376632646465333565-->
?
Train on the **past** and evaluate on a later period, possibly with several successive windows. Respect the moment when variables and labels become available; labels of a future horizon must not artificially overflow in a past training simulation.

An exclusion interval may be required around the border if the windows or labels overlap. Measuring multiple periods reveals seasonality and drifts. Randomly mixing timelines can give the model indirect information about the future that it would never have possessed.

---

Why learn imputation and variable selection inside each fold? <!--anki:3134653034613435396164373437323338386338363838616232656531313466-->
?
These operations **They also learn from data.**. A selection guided by all labels transmits information from the validation fold to the model, even if his training itself uses only the train.

A pipeline combines the transformations and the estimator: each fold adjusts the chain on its train, then transforms its validation with the parameters obtained. This protection does not detect a variable already contaminated upstream. The audit of origin and availability remains necessary, even with a properly constructed pipeline.

Even a median calculated without labels uses the validation distribution if it is adjusted over the entire dataset.

---

Why can a massive search for hyperparameters overlearn validation? <!--anki:6239363966616361353933333437303638366561666538666435666537313438-->
?
Choosing the best from many trials also selects favorable **score fluctuations**. The winning result then overestimates its future quality, even without a direct leak in training.

Limiting the budget, maintaining an independent final test and documenting the trials. A nested cross-validation separates internal selection and external estimation of the selection procedure. It costs more calculation and does not replace a relevant breakdown by group or period. Multiplying the trials on a bad protocol does not make its conclusion reliable.

---

Calculation: what accuracy and recall for 80 true positives, 120 false positives and 20 false negatives? <!--anki:6235333335326366616131623438643662303137373036623638303532613364-->
?
The **precision** measures the share of alerts that are correct; the **reminder** measures the share of actual positives found.
```text
Precision = TP/(TP+FP) = 80/200 = 40%
recall   = TP / (TP + FN) = 80 / 100 = 80 %
```
The system finds a large part of the sought-after cases, but imposes 120 false alarms for 80 useful. Examine the ability to review and the cost of errors. Without true negatives, we can not deduce the accuracy or the false positive rate.

---

Why can Accuracy hide failure on a rare class? <!--anki:3161643734653036343333333433356661633763636537323035373233376131-->
?
If only **1% of examples are positive**, always predict "negative" gives 99% of accuracy and zero reminder on the useful class. The average then rewards an unusable solution.

Examine the matrix of confusion, accuracy, and recall of the target class, then the error volumes. In multiclasses, a macro average gives a weight equal to the classes, while a weighted average reflects their frequency. No aggregate replaces the business constraints: ten critical errors can count more than a thousand benign errors.

---

Do not confuse: ROC curve and precision-recall curve? <!--anki:6430393537653937316432313433356239316434653837663131373039303064-->
?
**ROC** links recall and false positive rate; **accuracy-reminder** curve links recall and quality of alerts. When positives are rare, a small proportion of false positives can represent a lot of unnecessary alerts.

Examine the truly acceptable area of operation rather than an overall area alone. Accuracy depends on prevalence: comparing artificially rebalanced games may mislead. Specify the summary used; the precision averaging and trapezoidal area under the PR curve are not exactly the same calculation.

---

Why is the F1-score not always enough to choose a classifier? <!--anki:3831393033316131613166373435396438393533636563343037303032363961-->
?
The **F1** is a harmonic mean of precision and recall. It promotes their balance, but ignores the real negatives and does not directly represent a business cost or operational capacity limit.

Two systems of the same F1 can generate different alert volumes. If a team can only process 100 cases per day, measuring accuracy and recall to this capability is more concrete. For critical use, adding constraints per segment rather than maximizing only an average.

---

How to choose the threshold of a classifier according to the cost of errors? <!--anki:3135633064323666323465383439343139643933613735373831333336633537-->
?
Choose the threshold on **validation**, taking into account false positives, false negatives and processing capabilities. Under the assumption of calibrated probabilities, constant costs and zero cost for correct decisions:
```text
predict positive if p > C_FP / (C_FP + C_FN)
```
With a false positive at 5 units and a false negative at 95, the theoretical threshold is 0.05. Check calibration and business result, then freeze the threshold before the final test. An arbitrary ranking score is not a probability.

If this threshold triggers 2,000 alerts for 200 review places, the capacity constraint imposes another policy; do not ignore over-alerts in the review.

---

Do not confuse: MAE and RMSE for regression? <!--anki:6231663061663632383331383465633138663637316237303362306363666533-->
?
**MAE = average(|error|)**;**RMSE = root(mean(error2))**. Both have target unit, but RMSE gives more weight to large deviations.

Example: 0 and 10 days errors → MAE 5, RMSE approximately 7.07 days. 5 and 5 days errors → MAE and RMSE of 5 days. Same MAE, but different dispersion: the RMSE here prefers less concentrated errors.

Choose according to the business cost, not the numerically smallest score. These symmetrical metrics do not distinguish delay and advance; examine the signs or an asymmetrical loss if their consequences differ.

---

Where to apply oversampling of a rare class? <!--anki:3831383037313138363733653465343361383962303662613939373334396234-->
?
Only on the **train of each split or fold**, after its separation. Oversampling before cutting can place copies or synthetic examples very close in the validation and inflate the scores.

Keep validation and testing representative of actual use to evaluate alerts. Compare oversampling, class weighting and threshold setting: their effects differ. Changing the proportions in training can also affect the probabilities; their calibration on the target distribution must be checked separately.

---

How to compare two models with very similar scores? <!--anki:3064346565646231653831383461396362336438383638373362646530373662-->
?
Using **same observations**, examining differences in errors, and quantifying uncertainty with a method adapted to the sampling plan. A paired bootstrap can resample the same units for both models; if the observations are grouped, resample the groups rather than pretending that each line is independent.

Reporting the magnitude of the gain, the segments and the costs, not just a meaningfulness. On a time series, preserving dependencies requires a specific protocol. A score higher than a few hundredths is not alone a proof of exploitable improvement.

---

Calculation: on 10,000 cases, a classifier has TPR = 90% and FPR = 5%. Assuming these stable rates, what accuracy for prevalences of 50% then 1%? <!--anki:3061393332623339323864383434306661356339343337376466626131366431-->
?
Accuracy depends on the number of true and false positives:
```text
Prevalence 50%: TP = 5,000 × 0.90 = 4,500
                 FP = 5 000 × 0,05 = 250
Precision = 4,500 / 4,750 ≈ 94.7%
Prevalence 1%: TP = 100 × 0.90 = 90
                FP = 9 900 × 0,05 = 495
Precision = 90 / 585 ≈ 15.4%
```
The recall remains 90% in this hypothesis. The accuracy of a rebalanced test is not that of the real traffic. A drift can also change TPR and FPR: measure them instead of assuming their stability.

At low prevalence, even a low RPF applies to many negatives. To improve accuracy, compare thresholds on the target population, controlling for recall decline and review capacity.

---

Calculation: on 900 negatives and 100 positives, a model always predicts negative. What accuracy and what balanced accuracy? <!--anki:3735383766303134313734613432326439613833376139313931656163613638-->
?
The **accuracy** is `900 / 1 000 = 90 %`. The **balanced accuracy**, the average of the reminders of each class, is `(100 % + 0 %) / 2 = 50 %`.

The second metric gives a weight equal to the two classes and reveals the complete failure on the positives. It does not automatically represent the business cost: the severity of the false negatives and the ability to investigate remain to be specified. Report the confusion matrix and choose the metric before selecting the model, rather than choosing the one with the best number.

---

Do not confuse: macro and micro averages for a multiclass classification? <!--anki:3537323966636332636235363430366239643735383739393137326637386431-->
?
The **macro** calculates the metric by class and then gives the same weight to each class. The **micro** aggregates accounts before calculation and gives more weight to frequent classes.

A good micrometric can hide a rare class that is not properly processed. Choose by use and publish the numbers by class. For a single label multiclass classification, the micro-F1 coincides with accuracy if all classes are included.

---

## Scenarios

Scenario: your document classifier reaches 98% on a random split but fails in new clients. What do you check? <!--anki:6332393032336432653936623461356261323834363962633030343933643733-->
?
1. **Find dependencies**: Document models, clients, and almost identical versions between train and test.
2. **Definite targeted generalization**: new clients, new periods or new formats.
3. **Rebuild the split** by appropriate group and deduplicate before measuring.
4. **Relearn pre-treatment** only on each train and compare a baseline.
5. **Analyse errors** by client and format before deciding whether to add data or change models.

**Trap**: Increase model size to resolve a leak in the evaluation protocol.

---

Scenario: A 99% detector advertises Accuracy, but operators consider almost all of its alerts unnecessary. How do you rate the problem? <!--anki:3531303639363534383862663433633762313637316364323531383261643236-->
?
1. **Measure prevalence** and compare to always negative predictor.
2. **Count TP, FP and FN**, over a period with sufficiently arrived labels.
3. **Calculate accuracy and recall** to the current threshold, as well as the daily volume of alerts.
4. **Test other thresholds** on validation according to capacity and error costs.
5. **Check the segments** and measure the threshold on an independent test.

**Trap**: rebalance the test to 50/50 and then announce this precision as the production one.

---

Scenario: after 200 tests, the best model wins one point on validation but loses on the final test. What do you conclude? <!--anki:3139666465653964633637643431623962666133316264333435376236346165-->
?
1. **Check the comparability** of populations, periods and treatments between games.
2. **Consider selection bias**: The winner may have benefited from the validation noise.
3. **Also report the negative result** instead of choosing a new model through the test.
4. **Review the procedure**: test budget, nested validation if adapted, new independent data to confirm.
5. **Keep a strong baseline** until the gain is confirmed.

**Trap**: Re-use the test until it confirms the expected story.

---

## Sources
- [scikit-learn — traps and data leaks](https://scikit-learn.org/stable/common_pitfalls.html)
- [scikit-learn — cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html)
- [Scikit - Learn — Metric](https://scikit-learn.org/stable/modules/model_evaluation.html)
- [scikit-learn — decision threshold selection](https://scikit-learn.org/stable/modules/classification_threshold.html)

- [scikit-learn — metric and balanced accuracy](https://scikit-learn.org/stable/modules/model_evaluation.html) — targeted deepening of the 12 November 2026; educational examples are built for this review.

- 14 November supplement 2026 — Pretreatment adjusted in folds: [scikit-learn — Common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html).

- Supplement of the 14 November 2026 — Macro and micro averages: [scikit-learn — Metrics and scoring](https://scikit-learn.org/stable/modules/model_evaluation.html).

## Connections
- [[171-ml-model-selection|Choose a model ML]] — compare baselines and model families
- [[94-evals-methodology|Evaluation methodology]] — Extend Game Independence Principles
- [[151-data-curation-annotation|Curation & annotation]] — quality labels and duplicates
- [[159-temporal-data-features|Temporal data]] — rebuild variables actually available during prediction
- [[56-training-optimization-diagnostics|Training Optimization & Diagnosis]] — separate selection and final estimate
- [[173-calibration-uncertainty-abstention|Calibration, uncertainty & abstention]] — Probabilities and Business Thresholds
- [[99-statistics-experimental-decisions|Statistics to decide in AI]] — compare models without selection bias
- [[175-time-series-forecasting|Prediction of time series]] — compare without using future
- [[176-anomaly-detection|Detection of anomalies]] — rare classes and cost of false positives
- [[150-017-ai-datasets-corpora|Building Datasets & Corpus IA]] — protect splits and measure generalization
- [[117-continuous-training-pipelines|Training pipelines]] — retraining windows and promotion control
- [[00-moc-ai-engineering|MOC AI Engineering]]
