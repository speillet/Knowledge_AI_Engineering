# Calibration, uncertainty & abstention — Flashcards
Tags: #flashcards #ai-engineering #classical-ml #calibration #uncertainty
<!-- summary: discrimination and calibration, Brier score, separate calibrator, temperature scaling, uncertainties, risk-coverage, compliant prediction, cost of decision with review and human errors, limits of an aggregated CDE, calibration after selection, conditional coverage. -->


Do not confuse: discrimination and calibration of a classifier? <!--anki:6337616261653836306433623432636261323934336534393832663635306633-->
?
**Discrimination** is the ability to rank positives in front of negatives. **Calibration** relates the reported probabilities to observed frequencies: among the reported cases at 80%, approximately 80% should be positive.

A score can very well order cases while being too confident. To choose a threshold according to an expected cost, control the probabilities in addition to the ranking. A good overall calibration does not guarantee that of each population nor a useful ranking.

Predicting prevalence everywhere can be calibrated without discriminating any case. Examine jointly reliability curve, ranking metric and decision performance.

---

How to read a reliability curve without being fooled? <!--anki:6537616439316332303635323462366138313632616134393832356135363733-->
?
By probability range, compare **average prediction and observed frequency**, with numbers and uncertainty.

Example: ten files predicted around 0.8 of which six positives give a point close to `(0,8 ; 0,6)`, but little statistical precision. A thousand files provide more information; they do not correct a biased sample.

Changing the boundaries of the ranges can change the curve. Examine business segments and areas where decisions are made, not just the aggregate gap. Evaluate on a set separate from the one that adjusted the calibrator. A good diagonal is not enough: predicting prevalence for all can be calibrated without discriminating the cases.

---

Calculation: which Brier score for probability 0.9 and 0.6 with labels 1 and 0? <!--anki:3539313833653139336136323465656139663462653436333530346338333634-->
?
For a binary classification, the **Brier score** is the average of quadratic errors between probabilities and labels:
```text
Brier = ((0,9 − 1)² + (0,6 − 0)²) / 2 = 0,185
```
Lower is better. This binary definition has only one probability per observation; other conventions sum up the classes. The score reflects several properties, including discrimination and calibration: a decrease does not by itself prove that the calibration improves. Two observations do not allow to estimate the real reliability of the model.

---

Why separate model and calibrator adjustment data? <!--anki:6537646631316564303466373464363762396166376665316463393361386363-->
?
Predictions about training data are often too optimistic. Adjusting the **calibrator** to these same predictions teaches him a relationship that will not represent the new cases.

Use predictions about a sidelined game or predictions obtained outside of fold, respecting groups and time. Reserve independent data to evaluate the final string and its threshold. The calibrator is part of the learned system: it has a version, a target population and a risk of overlearning.

---

What does the temperature scaling of a classifier change? <!--anki:6233346231373066623439613461613038643839633764366364383064326636-->
?
It adjusts a positive parameter **T** on calibration data, then calculates `softmax(logits / T)`. For T greater than 1, the distribution flattens; for T less than 1, it becomes more concentrated.

The order of the classes in an example remains unchanged, so so does its class predicted by argmax. Calibration can improve without changing the accuracy. This learned temperature pursues a calibration goal; it does not guarantee that the sampling temperature of a LLM measures the veracity of a response.

---

Do not confuse: Random Uncertainty and Epistemic Uncertainty? <!--anki:6133313136323161663935363433316239626639383238343136373838313864-->
?
The **Uncertainty** comes from the variability of the given information target; the **Epistemic uncertainty** It comes from what the model doesn’t know. An ambiguous text and a language missing from the training illustrate two different causes of error.

Additional information can reduce the second. The first can decrease if new variables make the situation less ambiguous, but not by the repetition of the same training. To separate empirically remains difficult: a confidence score does not automatically say which cause dominates.

---

Why does a high probability of token not guarantee a correct factual response? <!--anki:3237303265336532363264333437326561313234613763326434303661663438-->
?
The probability of a **token** is conditional on the context and previous tokens. It measures the preference of the model for a continuation, not directly the veracity of a complete proposition. A false but usual sentence can have a high probability.

Define the event to be predicted, for example "the amount extracted is correct", then validate a score on labeled examples of this task. A transformation of the logprobs does not become a probability of correction without this validation and monitoring of the distribution.

---

How to read a risk-coverage curve for a system that abstains? <!--anki:3032646536383561303331333462323539333834623334623533346631633639-->
?
The **coverage** is the fraction of the cases processed automatically; the **selective risk** measures the errors among these accepted cases. Varying the threshold reveals the cost of hedging a risk reduction.

Comparing systems with comparable coverage and examining who is excluded: a good overall result can hide the abandonment of a language or a client. Also track human review errors and delays. A system that always abstains does not render the expected service, even if no automatic response is wrong.

---

Calculation: on 1,000 requests, 600 automatic answers contain 18 errors; the 400 abstentions are reviewed in three minutes each. What automatic accuracy and what human load? <!--anki:6339663738303634353834323431646561343636323238396335626639653264-->
?
The **automatic cover** is worth 600/1,000 = 60%. The accuracy among the answers is worth 582/600 = **97%**. If all the abstentions are reviewed, 400 requests come to humans.

With three minutes per review, this represents **20 hours** of work, excluding automatic errors. Reporting quality, volume and capacity together. The 1.8% of automatic errors on all requests does not mean 98.2% of correct resolution: the result of the 400 reviews remains to be measured.

---

What does the standard prediction guarantee? <!--anki:3537356636366530336566643464363561623933396432343630333338666361-->
?
It constructs **class or interval sets** from a model and scores on a calibration set. Under the required assumptions, including the exchangeability of calibration examples and the new case, it aims for marginal coverage of at least **1 − α**.

A 90% cover does not mean either 90% of certainty for each case or 90% in each subgroup. Also measure the size of the sets: including almost all answers can ensure coverage without allowing a useful decision.

---

Why can calibration deteriorate when prevalence changes? <!--anki:3961643434323038303063653434346338303235643261636133653336323066-->
?
A learned probability reflects the **original population**. If the frequency of positives changes, the relationship between score and actual frequency may also change, even with a still useful ranking.

Controlling frequencies and errors as soon as labels arrive, by segment. A prior correction assumes a form of stability of conditional distributions by class; it does not correct any drift. A degradation must therefore trigger a diagnosis before an automatic recalibration, then an independent evaluation on the target population.

---

How to choose between positive prediction, negative and human review from a calibrated probability? <!--anki:3133323763373130306434663437333761326135323634653538303663323932-->
?
Compare the **expected** costs of the three decisions. With positive probability `p`, constant costs of errors and free correct decisions:
```text
positive : (1 − p) × C_FP
negative: p × C_FN
review: C_review + expected cost of remaining errors
```
Choose the minimum under the constraints of quality and capacity. If the review is supposed to be perfect, its cost is reduced to `C_revue`; this is an assumption to be checked. Delays, limited capacities and variable costs can change the policy. A poorly calibrated probability distorts the arbitration.

Add the queue delay to the review cost if a late decision loses its value. Test the probabilities close to the decision boundaries, where a small calibration error changes the chosen action.

---

Calculation: p = 0.10 is assumed calibrated; a false positive costs 4 units, a false negative 36, and a perfect review costs 1. The correct decisions are free and the ability to review is sufficient. What decision minimizes the expected cost? <!--anki:3236303436626565656462313461663461656439663431366335393530666363-->
?
Compare the three costs:
```text
predict positive: (1 − 0.10) × 4 = 3.6
predict negative: 0.10 × 36 = 3.6
review parfaite : 1
```
**Review** minimizes the expected cost under these assumptions. Without review, positive and negative are equal; the binary threshold is 4/(4+36) = 0.10. Add the cost of human errors and delay before applying this rule to the real. The best individual choice may become impossible if the review queue saturates.

The equality of binary costs at the threshold does not automatically divide the files to be reviewed. With a limited capacity, prioritize the expected benefit of the review taking into account human errors and constraints of the service.

---

Do not confuse: Compliant coverage and automation coverage? <!--anki:6230396632636661386366613437323438656166333638343762346139643533-->
?
**Compliant coverage** measures the frequency with which a predictive set or interval contains the true target, under the relevant frame. **Automation coverage** measures the fraction of requests processed without abstention.

A compliant set containing multiple classes can cover the target without allowing an automatic decision. Conversely, a system meeting all requests has 100% automation, even if it is often wrong. Reporting together predictive coverage, set size, risk of decisions and human burden: the same word "coverage" here refers to different events.

---

Why can't a human review assume all the abstentions correctly resolved? <!--anki:3762363637393136663064613465623562303431663333626136663139326237-->
?
The review is **a stage of the system**, with its own errors, delays and abandonments. Its lot is often more difficult than automated cases; a human accuracy measured on another lot does not transfer automatically.

On the same set of requests, count automatic errors separately, errors after review and unresolved requests. Set a deadline and measure the resolution time. A decrease in automatic errors may coincide with an increase in global errors if the review is saturated. Validate the entire journey, not just the model.

---

Why does a weak ECE not prove that a classifier is well calibrated on each population? <!--anki:3266616136613230636533393436656138393832393936663930646635336233-->
?
The **Expected Calibration Error** summarizes the differences between average confidence and frequency observed in groups of scores. Its result depends in particular on the cutting and can hide internal deviations or groups little represented.

Examine the reliability, effectiveness, and uncertainty curve, and then the segments that are useful to the decision. Also compare a probabilistic metric like Brier or log loss depending on the goal. A favorable calibration average does not imply good discrimination or conditional calibration everywhere. Avoid choosing the number of bins only to improve the score displayed.

---

Why check the calibration after filtering of cases subject to automatic decision? <!--anki:3835316234393231653264363461353862626534336662383135626539626234-->
?
The selection can remember **a different population** than the one used to calibrate. A reliable score overall can be miscalibrated on this subset or on some groups.

Measure observed frequencies, effectiveness and risk among the decisions actually made. Keep an independent game to adjust threshold and calibrator. A drop in coverage can improve average accuracy while focusing errors on a particular category.

---

Why does a 90% marginal compliant coverage not guarantee 90% for each subgroup? <!--anki:6636373231373238366261313462303861336265653032313561626239303130-->
?
The guarantee generally covers **the overall population under the required assumptions**, including exchangeability for the standard framework. Groups may have different coverages.

Measure large groups and sizes of sets or intervals, and then consider an appropriate method if a more targeted guarantee is needed. A distribution drift may also invalidate assumptions. Do not interpret coverage as an exact individual probability for each prediction.

---

## Scenarios

Scenario: a trusted 95% classifier but is wrong on one case out of four in this range. What do you change? <!--anki:6234383262333736643935613465303538336135323536366232333930313163-->
?
1. **Check the predicted event** and the quality of the labels in this slice.
2. **Measure the numbers** and the difference by population, with its uncertainty.
3. **Adjust a calibrator** to predictions independent of model training.
4. **Choose the threshold** according to costs and review capacity, upon validation.
5. **Evaluate the frozen string** on an independent test before displaying a new confidence.

**Strap**: Replace 95% with a visual score without changing the decision or measuring its reliability.

---

Scenario: Abstention reduces errors to 1%, but triples the human review queue. How do you arbiter? <!--anki:3164386166303834373161633434613239386365313230666339653835363563-->
?
1. **Specify 1% denominator**: Accepted cases or total requests.
2. **Tracing risk and coverage**, with volumes per segment.
3. **Measuring human capacity**, timeliness and review errors.
4. **Compare multiple thresholds** according to total cost and quality constraints.
5. **Test the full route**, including what happens to pending requests.

**Trap**: Present the improvement of the only automatic subset as that of the entire service.

---

Scenario: a calibrated compliant interval on historical customers poorly covers new customers. What do you conclude? <!--anki:6238643963653161346665663466376362663939313331303536306531343437-->
?
1. **Check the measurement**: group size and definition of coverage.
2. **Examine the change in distribution** and the dependence between customer observations.
3. **Recall the marginal warranty**, which does not promise coverage per customer.
4. **Collect a representative calibration** or study a method adapted to the actual assumptions.
5. **Provide a fold** for undervalidated groups, then measure width and coverage.

**Trap**: invoke the word “conforming” as a universal guarantee despite a change in population.

---

## Sources
- [scikit-learn — probability calibration](https://scikit-learn.org/stable/modules/calibration.html)
- [— On Calibration of Modern Neural Networks](https://proceedings.mlr.press/v70/guo17a.html)
- [Geifman & El-Yaniv — Selective Classification for Deep Neural Networks](https://proceedings.neurips.cc/paper/2017/hash/4a8423d5e91fda00bb7e46540e2b0cf1-Abstract.html)
- [Angelopoulos & Bates — introduction to compliant prediction](https://arxiv.org/abs/2107.07511)

- [Kendall & Gal — Random and Epistemic Uncertainties](https://arxiv.org/abs/1703.04977)
- [Lipton et al. — assumptions and label shift correction](https://proceedings.mlr.press/v80/lipton18a.html)

- [scikit-learn — calibration and reliability diagrams](https://scikit-learn.org/stable/modules/calibration.html) — targeted deepening of the 12 November 2026; educational examples are built for this review.

- Supplement of 14 November 2026 — Calibration and validation populations: [scikit-learn — Probability calibration](https://scikit-learn.org/stable/modules/calibration.html).

- Supplement to the 14 November 2026 — Marginal scope of the compliant warranties: [Angelopoulos and Bates — Conformal Prediction](https://arxiv.org/abs/2107.07511).

## Connections
- [[172-ml-validation-metrics|Validation ML]] — Probabilities and Business Thresholds
- [[143-hallucinations-grounding|Hallucinations & abstention]] — not to confuse trust and truthfulness
- [[113-monitoring-drift-feedback|Monitoring & drift]] — monitor the validity of probabilities
- [[117-continuous-training-pipelines|Training pipelines]] — estimate accuracy and recall before labels
- [[00-moc-ai-engineering|MOC AI Engineering]]
