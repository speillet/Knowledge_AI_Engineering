# Prediction contracts, features & scoring batch — Flashcards
Tags: #flashcards #ai-engineering #mlops #classical-ml #features #batch
Verified on: 12 November 2026 — feature store behaviors depend on version and backend.
<!-- summary: grain and contract of a prediction, semantic validation, drive-service parity, uptime, TTL and freshness, missing values, named schemas, feature migrations, deadlines, batch independence, idempotency, full publication, temporal validity of scores, feature removal, label reconciliation, latency budget and batch capability, column order, decision and score. -->


What should the contract of a prediction specify before designing its endpoint? <!--anki:3532653337623538353362313436646661646637323462333234613839343437-->
?
Set **predicted unit, eligible population, reference time, horizon, and exit direction**. Add entity keys, input units, freshness rules, missing values, errors, and contract version.

Example: risk of termination at thirty days for an active subscription at the moment of decision, from the information available at that moment. "One score per customer" remains ambiguous if a customer has several subscriptions. The contract links API, batch, training and collection of labels. Without this definition, two technically compatible services can compare scores on different populations or horizons.

---

How to separate syntactic validation and semantic validation of model entries? <!--anki:6661626262646665353533643436623161626230313663356339393763656439-->
?
The validation **syntactic** controls presence, type and form; the validation **semantic** controls meaning and coherence: unity, plausible range, keys, temporality and field combinations.

A sum in cents can be a valid float but a hundred times too large for a model driven in euros. Providing explicit rejection, quarantine or processing of the unknown according to the contract, with counters by cause. Do not silently convert any malformed value to missing value. Test the controls with preprocessing and the model reloaded. A successful HTTP response only demonstrates that the software path has run, not that its data had the expected meaning.

---

How to check the parity between training features and features served? <!--anki:3132333966666236363337623430626261396162323538643765666661393630-->
?
Compare the values obtained for the **same entities at the same reference times**, Respecting what was actually available. Controlling windows, spindles, joins, units, categories, missing and rounded values.

Sharing the code of the transformations reduces divergences without removing those of the sources or their availability. Keep reference cases and, where allowed, observations representative of the features actually served; compare with tolerances and expected explanations. A historical table recalculated with subsequent corrections may be cleaner than the data seen online. Its apparent agreement therefore does not prove the fidelity of the reconstruction at the time of the decision.

---

Why can an event time join still create a time leak? <!--anki:3965653963343633363736663435613561393432623831333332613562356137-->
?
An event can be **dated before the prediction but received after**. A join based solely on its business date can include it in the historical training when the service could not know it.

Keep, if necessary, event time and actual availability time, and then restore the accessible state at the moment of decision. In a feature store, check the guarantees of the historic join, deduplication and backend used; the label "point-in-time" does not exempt from studying late arrivals. A technical creation timestamp is only useful for this purpose if it represents the correct availability sought.

---

Do not confuse: Historical TTL, expiration of storage and business freshness of a feature? <!--anki:3739346534373432663232373434356339356638336261313135636664363233-->
?
A historical **TTL** can limit the age of the values sought before a reference moment; in Feast, it limits the search window of the historical join. A **storage expiration** determines how long an object remains accessible. The **business freshness** tells if a value still suits a given decision.

These mechanisms are not automatically equivalent. Check the rules of the backend and control the age from the relevant timestamp. A present value may be too old for use, while an absent value may simply never have existed. Document the limits separately to train and serve with compatible assumptions.

---

How to treat an absent or outdated feature without inventing an observation? <!--anki:3566366566636662643261373461333362386438353733636261343232333461-->
?
An absence is not necessarily **zero**, and an old value is not necessarily usable. Distinguish between normal absence, source incident and allowed timeout.

Apply only a planned and tested treatment: learned imputation, absence indicator, validated backup model or deferred decision. If the contract requires the feature, return an explicit state rather than a misleading ordinary score. Measure frequency and affected segments; check that the degraded mode remains in its validated domain. An imputation that passed on a few missing values in training does not guarantee quality when an entire source disappears in production.

---

Why are the named columns not enough to guarantee the entry contract? <!--anki:6266643639386132663265353432336138303963343662353761373065643563-->
?
Names reduce positional errors but do not set **types, units, meanings, and behavior of additional fields**. A layer can convert a named array to a positional matrix before the estimator.

Test reordering, missing or unexpected columns, type changes, and category variants with the published package. Explicitly choose whether an additional field is accepted or denied. Verify that the column selection follows the expected pattern until the last preprocessing. A test that calls only the model in memory with an already correct matrix ignores the transformations and serializations through which the queries will actually pass.

---

How to migrate a feature without making the current model or rollback unusable? <!--anki:3165303039323837373438333438363862646364663732353163666464353831-->
?
Treat migration as a **compatibility between producers and consumers**. Publish the new definition with a separate identity, prepare its history and its food, then check coverage and values before linking a candidate.

Make the necessary versions coexist during the transition and the rollback window. The model manifest references the expected definition; replacing a feature behind an unchanged name can change all consumers at once. Delivery coordinates data, model and contract without assuming a global atomic transaction. Remove the old definition after identifying consumers and validating recovery conditions, not from the first successful deployment.

---

How do I integrate feature recovery into the latency budget of a prediction? <!--anki:3231356265633531666137373434386162306464373064303330346631623235-->
?
Reserve a **global deadline** covering the queue, recovery of features, pre-treatment, model and serialization. Spread the remaining time to calls; A retry should not reset the budget.

Parallel independent sources when appropriate, with limits of concurrency and behavior expected for a partial response. Check for freshness and identity of backup values. Measure end-to-end latency distributions under load; adding p99 components does not automatically give the service p99. A two millisecond inference may miss its SLO if the majority of the time is spent waiting for a feature or a pool of connections.

---

Why test that an individual prediction remains stable when the batch composition changes? <!--anki:6365623139383633623861633435396439346261353462623662353137313037-->
?
For a model **point by point**, The other lines should not determine the transformation of an observation at the time of prediction. A scaler adjusted on each batch or an involuntary aggregation can vary the score according to its neighbors.

Compare the same line alone, with ordinary and then extreme cases; check outputs and decisions with a tolerance adapted to the runtime. Do not call `fit` or `fit_transform` on the inference data to "prepare" each batch. Some models voluntarily use a collective context; their contract must then identify this group and its construction. The test depends on the announced independence, not a universal property of any model.

---

How to make a scoring batch idempotent despite the setbacks? <!--anki:6334353238343961333435343464316261353732636135613562363531333937-->
?
Set a **logical identity** from release, input snapshot, partition, and calculation contract. Distinguish this identity from execution attempts; a retry retains the intent of the same calculation.

Write first in a temporary location, then publish in a controlled manner with uniqueness or deduplication suitable for storage. Check cardinality and content before publication. A key built with the time of each attempt turns each retry into a new result. The idempotency must also cover consumers: recalculating scores without duplicates is not enough if each notification restarts a business action. Preserve provenance and status of attempts to explain a resumption.

---

When can a batch of predictions be declared publishable? <!--anki:3063393139363630303633633435333262363636306630393539323932356663-->
?
After checking its **completeness according to the contract**, not only after the end of the process. Compare eligible population and results: unique keys, expected partitions, accepted lines, rejected and absent, valid outputs and effective release.

A contract may allow partial publication, provided that it makes it explicit to consumers. Using a manifest or storage-compatible transactional publication to prevent a reader from consuming a batch that is still in progress. Keeping counters and rejection causes. A green job that has ignored an empty partition or an absorbed error may produce a clean table that appears to be unusable for the intended decision.

---

What time stamps should be kept with a pre-calculated score? <!--anki:3966666437393630616634633465646638303636363232393639376364643332-->
?
Keep **reference time of the information**, time of calculation and period of authorized use, with definition of the horizon. These times answer different questions: what was known, when was calculated, until when is the result suitable?

Add prediction identity, entity, release and snapshot or adapted provenance. A recalculation this morning from an old snapshot does not update the information. The consumer checks the validity for his decision and predicts a behavior if the score is absent or too old. A table present and a successful job do not prove that the score still describes the target population today.

---

Why should the removal of a feature follow the real consumers? <!--anki:6631383235633961303130393433376662646330303561613534616438376138-->
?
A feature can be used by **current model, rescue release, scoring batch and historical survey**. Removing its source as soon as a new model no longer consumes it can make rollback or recovery impossible.

Inventory declared dependencies and observed access, notify owners according to the planned process and set a withdrawal date. Check the alternative and retention or deletion requirements. An incomplete line graph may be missing from indirect consumers; access logs complete without always proving their absence. The withdrawal must be an explicit decision with verified conditions, not the side effect of an optimization of storage.

---

Why bring labels closer to a prediction identity rather than just the customer ID? <!--anki:3036353063623539623731363464646638663266313838386561303833356232-->
?
A customer can receive **several predictions at different dates and time horizons**. A join only on his ID can associate a future termination with all his old predictions or duplicate the lines.

Keep prediction identity, unit, reference time, horizon, eligibility rule and label version. Set maturation and corrections of issues, then measure rapprochement rate and delay. Verify that a label describes the expected target, not just an operator action. Good apparent quality on the only close-up lines can hide difficult cases or populations whose labels arrive later. Report coverage with metrics.

---

Calculation: Three independent readings 25, 40 and 70 ms, Then the model 12 ms and serialization 5 MS. What gain does their ideal parallelization bring? <!--anki:6231333261323935663964633432633939393765643530613063306539386533-->
?
For these **fixed durations**, without waiting or coordination cost:
```text
= 25 + 40 + 70 + 12 + 5 = 152 ms
Parallel = max(25, 40, 70) + 12 + 5 = 87 ms
gain = 65 ms; margin under 100 ms = 13 ms
```
This calculation does not add up percentiles and does not predict the actual p99. Files, connections, CPU and concurrency can absorb the margin. Measure under load the full path; verify that the reads are indeed independent and that their parallelization does not exhaust a shared resource. A global timeout must also cover these costs. Keep source latency and total time to diagnose actual expectations.

---

Calculation: it is necessary to score 12 million lines in two hours. What average useful rate should be supported? <!--anki:6466316166633531663961383435646139333631363239663162343865333263-->
?
Two hours represents **7,200 seconds**:
```text
12 000 000/7 200 ≈ 1 667 line_items/s
```
It is a flow floor **useful from end to end**, After reading, Preparation, calculation, Writing and validation. If thirty minutes are reserved for these stages excluding scoring, on the 5,400 remaining seconds impose approximately **2,223 line/s** for scoring alone.

Provide margin for unbalanced covers and scores, then measure with actual sizes. Multiply a bit rate on a small sample by the number of workers often ignores storage, memory and contention. Specify whether the delay relates to the last calculation or to the validated publication of the consumable batch.

---

Why can two tables with the same columns in a different order produce incorrect predictions? <!--anki:3962623262643264313365613465343838396362643439663438386562646635-->
?
A pipeline that converts inputs into **Positional Matrix** can associate each value with the wrong feature. The types are plausible, So the model can answer without error.

Explicitly align names and validate order, type, and unit before conversion. Test a permutation of columns. Named schemas only help if all steps meet them; their loss in an intermediate array must be controlled.

---

Why version the decision policy separately from the predictive score? <!--anki:6363633038306532663630313462366461393830633837373365323633353666-->
?
The same score can trigger **a different action depending on the threshold, quotas or business rules**. Modifying these rules changes the product without changing the weights.

Maintain model version, raw score, policy, and effective decision for audit and rollback. Assess the impacts of capacity, cost, and equity. A good predictive metric does not prove that the policy that turns score into action is appropriate.

---

## Scenarios

Scenario: scores change significantly after a source migration, but the schema and types are the same. What do you check? <!--anki:3830633832373562333731393432363261313862633962636262353234366632-->
?
1. **Compare values with the same entity and time**: unit, currency, time zone, window and category, not just columns.
2. **Examine availability and freshness**: Data recalculated or received late may have changed the historical reconstruction.
3. **Control preprocessing and contract** of the actually loaded model, then replay known cases with both sources.
4. **Suspend or revert to a validated combination** according to the runbook; avoid training immediately on the new source.
5. **Verify the corrected definition** and add independent semantic controls.

**Trap**: to conclude a natural drift because a type test passes; an amount in cents can silently replace euros.

---

Scenario: a batch restarted after timeout doubles the score lines and campaigns sent. How to fix it? <!--anki:3732313435396561323961373432323839383462303636353039353634373065-->
?
1. **Stop consumption** and identify the attempts, partitions and actions already produced.
2. **Reconstitute logical batch** with identical release and snapshot; distinguish published results from temporary writes.
3. **Reconcile scores** according to a correct business key, with uniqueness and coverage control; do not arbitrarily delete all old lines.
4. **Also deduplicate business effects** with a stable action identity; a table fix does not cancel a send.
5. **Test an interrupted restart** and publish only a validated result with its manifest.

**Trap**: add a unique attempt key and call it Idempotence: it allows precisely a new duplicate on each raise.

---

Scenario: a feature source becomes unavailable, but the service continues to respond with null values. What do you decide? <!--anki:3733633232343866333061373433613861616537356161616664326662303963-->
?
1. **Measure the perimeter**: source, seniority, segments, absence rate and release version.
2. **Check the validated contract**: normal one-time absence or global outage outside the tested domain?
3. **Apply expected mode**: retained values still valid, backup model evaluated, or deferred decision with explicit status.
4. **Monitor charge and quality available** without presenting the absence of immediate labels as proof of safety.
5. **Restore source and check values** before progressive return; retain identities of affected decisions.

**Trap**: Replace everything with zero to maintain the rate of successful HTTP responses, and then hide the degradation of the service rendered.

---

## Sources

- [scikit-learn — consistent pre-processing and data leakage](https://scikit-learn.org/stable/common_pitfalls.html) — separate adjustment and transformation; test the complete package.
- [Feast — jointures point-in-time](https://docs.feast.dev/getting-started/concepts/point-in-time-joins) — search history and TTL; check backend availability and behavior separately.
- [Google Research — Hidden Technical Debt in Machine Learning Systems](https://research.google/pubs/hidden-technical-debt-in-machine-learning-systems/) — undeclared data dependencies and consumers.
- [Google SRE — monitoring](https://sre.google/workbook/monitoring/) — observe the service and its symptoms; the contracts and calculations presented are design examples.

## Connections

- [[112-model-cicd|CI/CD models]] — check the actual service path
- [[113-monitoring-drift-feedback|Monitoring and feedback]] — label coverage and maturity
- [[116-ai-sre-incidents-capacity|SRE of AI Systems]] — Delays, Dependencies and Degraded Modes
- [[117-continuous-training-pipelines|Training pipelines]] — compatibility between data and model
- [[118-ml-artifacts-registry-releases|Artifacts and releases ML]] — describe the delivered chain
- [[157-data-contracts-quality|Data contracts]] — invariants and semantic validation
- [[159-temporal-data-features|Temporal data and features]] — historical availability and feature stores
- [[149-delivery-idempotency-concurrency|Idempotence and concurrency]] — business entries and effects
- [[00-moc-ai-engineering|MOC AI Engineering]]
