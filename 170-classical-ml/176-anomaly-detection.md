# Detection of anomalies — Flashcards
Tags: #flashcards #ai-engineering #classical-ml #anomalies #monitoring
Verified on: 8 October 2026
<!-- summary: rarity and business error, outlier or novelty, non-probability scores, contextual baseline, Isolation Forest, LOF, self-encoders, review capacity, prevalence, assessment by incident, missing and drifting labels, limits of a fixed quota of alerts, duration of incidents, contextual threshold. -->


Why is a rare sighting not automatically a business anomaly? <!--anki:3262626534616237356331383432303561333862383131383336643362343139-->
?
A detector detects a **deviation from a reference**, which may correspond to an incident, a legitimate novelty or a collection error. A peak of orders during a promotion is rare in the history but can be expected.

Define the action that the alert should trigger and the cost of a false alarm. Keep the context and a possibility of review. Automatically delete the atypical observations can erase the most interesting cases, or turn a real change of activity into an artificial problem of data quality.

---

Do not confuse: Outlier detection and novelty detection? <!--anki:3566633064316234396366303465626338396334643434303238326365346562-->
?
The **outlier detection** looks for atypical observations in a game that can already contain them. The **newness detection** learns a supposedly normal reference, and then judges new observations with respect to this reference.

For example, cleaning up a year of payments that already contains fraud is an outlier; learning about a verified month without an incident, and then judging each new transaction, is a novelty. A contaminated history can make an incident learn as normal. A new legitimate behavior can be reported wrongly. In both cases, business relevance requires labels or investigations; the geometry of the data does not alone define the incident.

---

Why is an abnormality score of 0.95 not necessarily a risk of 95%? <!--anki:6431623064323139323738383465656538323839316133323230316631636137-->
?
A **Anomaly score** often measured in isolation, low density or a reconstruction error. Its scale and meaning depend on the algorithm: 0.95 This is not automatically a probability.

Example: select the most atypical 1% of 10,000 product observations 100 alerts, **not necessarily 100 incidents** or 1% false positives. Estimate accuracy and recall with reliable labels, then choose the threshold according to cost of errors and ability to review.

`contamination` can set this threshold from an assumed proportion; it does not discover the actual prevalence. Monitor the drift of scores and business results.

---

Which baseline to build to detect an anomaly in a seasonal series? <!--anki:3133393363653030656434313436393561643265306231313865386336376365-->
?
Compare the observation to a **contextual reference**: time, day, category, or historical forecast. A median and a robust dispersion over comparable periods can provide a first gap score.
```text
= score |x − median | / (1.4826 × MAD) on the 8 previous Mondays at 14 h
1,250 controls, median 900, MAD 60 → 350 / 89 ≈ 3.9
```

Learning the reference to the available past and specifying what happens when the dispersion is zero or the data is missing. Assessing forecast residues can help, but not guarantee their stability. An overall threshold on raw values often signals normal seasonality rather than the incidents sought.

---

How does Forest Insulation detect atypical observations? <!--anki:6362353831653063623837373431313339366433396539346664613032613361-->
?
It constructs trees with **random partitions** of variables and measures how many separations are needed to isolate a point. Quickly isolated observations receive a more atypical character depending on the score used. In scikit-learn, each `IsolationForest` tree uses by default `min(256, n_samples)` observations; `score_samples` is all the lower the point is atypical.

The result depends on the representation, sub-sampling and structure of the data. This mechanism does not directly learn a business definition of fraud or failure. Testing multiple families of incidents and false alerts; an anomaly geometrically resembling normal operation may remain difficult to detect.

---

When is a local density like LOF useful for detecting anomalies? <!--anki:6639663934643636316264303436363639626162376439653233396630336234-->
?
**Local Outlier Factor** compares the density of a point to that of its vicinity. It can signal an unusual point for its group, even if another region of the game has a different overall density.

Distances, scale of variables and number of neighbors strongly influence this neighborhood. In scikit-learn, the default mode is used to analyze the adjusted data; the `novelty=True` mode allows to score new data, with separate precautions. Do not evaluate the latter on its own training observations as if they were new cases.

---

Why can an autoencoder reconstruct an anomaly? <!--anki:3661393162663335383138643466373662653762663933333730626335356363-->
?
The autoencoder learns to **rebuild its inputs**, not directly recognize incidents. High capacity, contaminated training or an anomaly close to normal patterns can produce a very accurate reconstruction of a problematic case.

Conversely, a new normal case can be badly reconstructed. Compare to simple baselines and validate the reconstruction error on representative incidents. Arbitrarily reducing the latent size does not guarantee to separate normal and abnormal. Examine the variables that dominate the loss: without normalization, a temperature of 0 to 1,000 overwrites a vibration of 0 to 0.1, the anomaly of which goes unnoticed.

---

How to choose an anomaly threshold with limited human capacity? <!--anki:3930393333353237366365633432326361616164306638343233663665663064-->
?
Connecting the Threshold to **volume of alerts and incidents found**. For a team that can handle 30 files per day, measuring accuracy among the 30 first, Identify critical incidents and delay before investigation.

A top-k limits the load but can send unnecessary alerts on quiet days or miss a collective incident. Provide minimum threshold, grouping and treatment of emergencies according to the context. The threshold is set on validation; its operational capacity must then be verified over an independent period.

---

Calculation: on 100,000 events including 100 incidents, how many alerts with 90% reminder and 1% false positives? <!--anki:6264363065303339333633643433333838646466353363656366623632653936-->
?
Taking these rates as accurate for this example:
```text
True positives = 100 × 0,90 = 90
False positives = 99 900 × 0,01 = 999
= 1,089 alerts; precision = 90 / 1,089 ≈ 8.3%
```
The false positive rate refers to normal events, not all alerts. Despite a good reminder, most investigations would be useless. With estimated rates, add their uncertainty and check the prevalence of production before sizing the team.

If each alert costs ten minutes of investigation, it represents about 181.5 hours of review, so a low accuracy becomes a concrete capacity constraint; grouping the alerts of the same incident can change this cost.

---

Why evaluate time detection per incident in addition to individual points? <!--anki:6439623633616130303133383432363238656239336361343264613864646162-->
?
The same incident can last hundreds of points. Counting point by point can overweight its duration or reward a very late detection. Also measure **recovered incidents, detection time and false alerts per period**.

Set tolerance windows, grouping and association rule before evaluation. The adjustment point, which marks an entire interval detected as soon as a point is detected, can inflate the scores: an incident of 180 minutes spotted at the 170e counts 11 points detected, or 180 after adjustment, for a delay of 170 minutes.

---

How to evaluate an anomaly detector when labels are incomplete? <!--anki:3863656264616537646261393438373439316164653138373635343665306531-->
?
Review alerts and a **sample of non-alerts**, with documented strategy and probability of selection. Examining only alerts allows to approach their accuracy, but not to count missed incidents in the entire population.

Example: if 3 non-alerts on 300, randomly drawn from among 50,000, are incidents, it is estimated that about 500 missed incidents, with a wide interval; each reread case weighs here 50,000 / 300. Injected anomalies test certain mechanisms, without automatically representing the actual incidents. Separate confirmed cases, unknown and delayed labels; the absence of a report does not constitute normal.

---

Why can a fixed quota of daily alerts hide a real anomaly crisis? <!--anki:3830383530663263393566323466653439313635386661313663313631376637-->
?
A daily **top-k** guarantees a maximum load but artificially fixes the number of alerts. If the actual incidents multiply, many remain invisible; in quiet periods, the quota can push normal cases.

Combine investigative capacity, severity thresholds and volume monitoring above stable thresholds. Consolidate points per incident and predict escalation during a major increase. Measure incident recall and detection delay. A triage policy controls human work; it should not lead to the belief that business risk has remained constant.

---

Why can a single anomaly threshold saturate the journal on certain segments? <!--anki:3331653661616237303235343437626562633265313031343930663563383561-->
?
The scores can have **different distributions depending on the context**, even without incident. An overall threshold then produces very unequal volumes of false positives.

Examine rates and costs by segment, and then calibrate a tailored policy without masking true incidents. An identical quota per group does not guarantee comparable quality. Validate changes over independent periods and track human load.

---

## Scenarios

Scenario: your detector triggers thousands of alerts every commercial campaign. How do you reduce noise? <!--anki:6433633933363164373861643432663739303733633265616131366563633334-->
?
1. **Check for actual change** and eliminate a collection failure.
2. **Add available context**: campaign, day, segment and expected volume.
3. **Compare a contextual baseline** to the current model over multiple periods.
4. **Group related alerts** and measure the time to detect real incidents.
5. **Fix the threshold on validation**, then check human load and critical recall.

**Trap**: Disable detection during campaigns, where real incidents remain possible.

---

Scenario: an autoencoder gets a small reconstruction error on known failures. What do you check? <!--anki:3638363535313663353533643437383639626632373261376433306335656464-->
?
1. **Seek contamination** of training data by these failures or their copies.
2. **Examine the representation** and the variables that dominate the loss.
3. **Compare contextual or isolation thresholds to a baseline**.
4. **Test for separate periods** and multiple incident families.
5. **Reform the task** to supervised detection if enough reliable labels exist.

**Trap**: assimilate weak reconstruction and lack of business risk.

---

Scenario: the alert rate climbs after a lasting change in operation, and the team wants to retrain immediately. What do you decide? <!--anki:3262653861616635626166623464633638366134636534326334386233643835-->
?
1. **Distinguish legitimate change and incident**, with the process manager.
2. **Check collection and units**, before concluding a drift in behavior.
3. **Isolate the transition period** and confirm which examples may become the new reference.
4. **Reassess old and new detector** on normality and known incidents.
5. **Deploy gradually** with the possibility of folding and tracking delayed labels.

**Trap** : retrain on an ongoing incident and learn to consider it as normal.

---

## Sources
- [scikit-learn — outliers, novelty and LOF](https://scikit-learn.org/stable/modules/outlier_detection.html)
- [scikit-learn — Forest Insulation and Threshold](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html)
- [Kim et al. — Towards a Rigorous Evaluation of Time-series Anomaly Detection](https://arxiv.org/abs/2109.05257)
- [Bouman & Heskes — limits reconstruction to detect anomalies](https://arxiv.org/abs/2501.13864)

## Connections
- [[175-time-series-forecasting|Temporal forecast]] — build contextual reference
- [[172-ml-validation-metrics|Validation ML]] — rare classes and cost of false positives
- [[113-monitoring-drift-feedback|Monitoring & drift]] — distinguish incident and reference evolution
- [[151-data-curation-annotation|Annotation]] — organize the confirmation of incidents
- [[00-moc-ai-engineering|MOC AI Engineering]]
