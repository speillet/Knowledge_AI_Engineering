# Temporal data & production features — Flashcards
Tags: #flashcards #ai-engineering #data #data-engineering #features
<!-- summary: event time and processing, historical availability, point-in-time joins, bi-temporal corrections, windows and watermarks, delayed labels, drive-serving consistency, feature store and freshness, offline/online paths and secure materialization, date of effect and date of knowledge, leakage by aggregate, delay in availability. -->


Do not confuse: event time and processing time? <!--anki:6530353238343566646235653466306338396630383966326238633938343537-->
?
The **time of the event** describes when the fact occurred; the **time of processing** describes when the system processes it. An order made at 10 h and received at 10 h 20 belongs to the reality of 10 h, but was not necessarily known to the predictor at 10 h 05.

Retaining both allows you to process delays and rebuild what the system knew. Add if necessary the actual time of publication of the variable: receiving data does not mean that it is already exploitable by the service.

---

What is a point-in-time join to build an ML dataset? <!--anki:3837343539316435383738383462666138346361386638383963376563376436-->
?
For each observation to be predicted at the time **t**, retrieve the historical variables valid at that time, without taking their future versions. A value can also be excluded if it is too old according to its validity period.

The only condition "event date ≤ t" is not enough when data arrives late: attach on their actual availability to t.
```python
pd.merge_asof(obs.sort_values("t"), feats.sort_values("disponible_a"),
              left_on="t", right_on="disponible_a", by="client_id",
              direction="backward", tolerance=pd.Timedelta("7D"))  # last known value, not more than 7 days
```
A rewritten history today may otherwise make one believe that information was accessible yesterday.

---

Calculation: to 10 h 05, can we use a purchase made to 9 h 58 but published in variables to 10 h 12? <!--anki:3539643131366436633237333439313061336166363534386464363638613463-->
?
**No**, to simulate a prediction actually made at 10 h 05. The fact belongs to the business past, but its availability for the model is post-decision.
```text
event time = 09:58 ≤ 10:05
available at = 10:12 > 10:05 → exclude from simulation
```
Including it in training or historical evaluation would create a temporal leak; if another channel made it available earlier, it would have to be demonstrated and use the corresponding availability definition, rather than assuming that the source timestamp is sufficient.

---

Why keep multiple versions of a corrected historical value? <!--anki:6432343334353963333866333435336561653031323436646466343834653339-->
?
A correction can change what is considered true **for a past date**, without changing what the system knew at the time. A bitemporal representation distinguishes period of business validity from period of knowledge or recording.

We can thus distinguish the current best estimate of the past and the data that guided the past decision. Example: a customer's January income, recorded at 3,000 € on 3 January, is corrected at 3,400 € on 15 March. A decision of the 10 February saw 3,000 €; overwrite this level makes it irresolvable.

---

How to calculate a sliding variable without looking into the future? <!--anki:6166353530373162666438323432646138313765653564383039383732333233-->
?
Define explicitly **the window, its limits and the availability of events**. For a number of purchases over the previous seven days at t, a possible convention is [t−7 days, (t), with only the events actually known to t.

Using the same time zones and conventions in training and serving. Testing boundaries, late arrivals and corrections. A daily aggregation calculated after midnight can reveal the future of a decision made in the morning.

---

What does a watermark mean in a flow treatment? <!--anki:3765613236353839333133623435363639306265623534303766343063626337-->
?
A **watermark** represents an estimate of the progress over time of events. It helps to decide when to produce or finalize the results of a window and how to process the data that comes next.

It is not a universal proof that no more ancient events will happen. Example: with a watermark equal to "maximum timestamp seen" − 10 minutes," 12 h 30 observed declares the window 12 h 00–12 h 15 complete; an Event of 12 h 10 Then it is late. Choose a tolerance for delay, then decide between correction, provisional outcome or documented rejection. Waiting more sometimes improves the completeness, but increases latency and retained state.

---

How to process a late event after publishing an aggregate? <!--anki:3066343764656439633234653466613861336165636337363131306434616337-->
?
Choose an explicit **correction policy**: update the aggregate with a new version, publish a retraction followed by the corrected result, or classify it out of time with a loss of coverage measure.

The policy depends on consumers: a dashboard can be corrected, an external action already performed does not cancel automatically. Example: sales of the 20 October, published to 10,000 €, switch to 10,450 € in version 2; the decision made the 21 keeps track of the 10,000 € that it would actually replace.

---

How to evaluate a model whose labels arrive several weeks later? <!--anki:3034663863316234326462623434653339323737376463343665343536346230-->
?
Waiting for **maturing of the target and its collection**, or using a method suitable for censorship. An absence of observed event is not always a negative label.

Example: for a termination in 30 days, a file aged five days is not mature. If events arrive seven days late, even the day 30 may be too early to consolidate the labels.

Keep prediction date, target window, observation date and label version. Publish provisional and consolidated metrics separately, with coverage rate. A recent drop in positives may reflect their unavailability rather than actual improvement.

---

What is training-serving skew variables? <!--anki:6663663964393236376562653464623239343638613033613763356635393539-->
?
This is a **variable between the variables used in training and those produced in service**: different formula, rounded, spindle, source, freshness or absence management. Even identical weights behave differently if the inputs have changed direction. Example: `anciennete_jours` is calculated in UTC at midnight for training, in Paris time at the time of the request in service; some customers win a day.

Sharing definitions and versions reduces this risk. Comparing the values actually used to a controlled recalculation on the same events, respecting their availability. A finalized history may legitimately differ from a provisional state: understand this deviation rather than hide it.

---

When is a feature store useful, and what does it not guarantee? <!--anki:6331346435366635393235633430303461303230326362373566383935376235-->
?
It can centralize **definitions, history, and variable access** for multiple models, with paths adapted to training and service. It becomes interesting when computational duplications and inconsistencies cost more than its own complexity: three models that each recalculate "purchases on 30 days" with different windows, for example.

It does not magically make variables exact and does not remove historical availability issues. Check time joins, freshness, corrections, and responsibilities. A small application can start with a versioned pipeline and simple storage, and then add this brick when measured needs warrant.

---

What to expect when a production variable is too old? <!--anki:3030623161323236366138653430363562346665633465353835346631323562-->
?
Define a **validity period specific to the variable and use**. Control the actual age of the value, not just the state of health of the service that returns it.

For example: a stock is 5 minutes, the account country 30 days; a two-hour old stock switches to a backup model that does not use this variable. An absent value and an expired value may require different processing. Measure the use of degraded mode to prevent it from becoming silently normal operation.

---

Do not confuse: offline and online storage of features? <!--anki:3737623337316630626462303433383962333335366533636535343039646365-->
?
**offline storage** is used in particular to reconstruct training histories and batches. **online storage** aims to recover variables useful for a query with expected latency, often by entity key.

A current fast-to-read value does not automatically provide its history; a full history does not necessarily provide quick interactive access. Feast thus exposes two calls for the same definition:
```python
store.get_historical_features(entity_df=obs, features=["client:achats_30j"])   # offline, point-in-time
store.get_online_features(features=["client:achats_30j"], entity_rows=[{"client_id": 42}])
```
Check types, missing values, freshness, and version of transformations in both paths.

---

How to materialize features online without overwriting a recent value by an old backfill? <!--anki:6566643833666364333636303431363762653937316363366536636330323934-->
?
Associate **entity key, feature version and relevant time order**, then write according to a policy that rejects or isolates outdated updates. The guarantees of the storage and its connector must be verified.

Separate offline reconstruction and online publication when their objectives differ. A historical backfill should not replace the current value simply because it terminates later: recalculated for the 1er March and written on the 10 October, `achats_30j` would overwrite otherwise the value of the day. Test late event, valid correction, deletion and replay. The rule "greatest timestamp actually wins" is not the correct order.

---

Why does a point-in-time join sometimes have to take into account the availability date in addition to the effective date? <!--anki:6130613030393865366465373431653962616330383236343836393738343262-->
?
A **corrected historical value** can have an old business effect while only being known later. Attaching it only on its effective date gives the model information inaccessible during the past decision.

Keep validity time and knowledge time, and then rebuild the view available at the predicted time. For example, a fix published on Friday should not artificially improve a prediction made on Monday. Tester late arrivals and revisions. A realistic assessment uses what the system could actually know, not just the best historical version known today.

---

Why can a monthly average calculated after the end of the month leak the future into a daily model? <!--anki:6333383864393733643534313461623162646662653361376665313939643664-->
?
For a prediction of 10, it can integrate **events from 11 to 31**, unavailable at the time of the decision. The date associated with the feature does not make this calculation causally available.

Build the aggregates with a correct time limit and take into account the release time. Test the pipeline by simulating the known data at each moment. A time split alone does not correct an already contaminated feature.

---

Calculation: an event takes place at 09 h 00, arrives at 09 h 20 and is available to feature service at 09 h 25. Can it be used to reconstruct a prediction made at 09 h 10 without leaking? <!--anki:6633656661626137633734323431663238383963363332353333306536613734-->
?
**No**, if the prediction service could not know it before 09 h 25. Its pre-09 h 10 event time is not enough.

The reconstruction must respect the availability time relevant to the actual system. Keeping corrections and deadlines makes it possible to distinguish what was true in the world from what was actually known at the time of the decision.

---

## Scenarios

Scenario: a historical model is excellent, but its performance drops as soon as it launches despite the same columns. What are you looking for? <!--anki:6131633734393433356463633438363239396262626138313536326561376135-->
?
1. **Reconstitute the decision time** and the actual availability of each variable.
2. **Identify late corrections** and aggregates calculated after events to be predicted.
3. **Compare examples used** for the historical reconstruction of what was then known.
4. **Correct joins and splits** and then retrain and re-evaluate without future data.
5. **Monitoring coolness and gaps** between drive and production pipelines.

**Trap**: Believing that having the same column names guarantees the same information.

---

Scenario: an activity score is calculated per day, but mobile events arrive up to two days later. What policy do you propose? <!--anki:3831353430663630303639323462373639613761623263326238366562643332-->
?
1. **Measuring the distribution of delays** and specifying acceptable latency for the product.
2. **Publish a provisional result** if necessary, with a status and version.
3. **Definite the correction window** and the processing of events beyond that.
4. **Warn consumers** of the possibility of revisions and make their application safe.
5. **Keep values seen** by models to reconstruct past decisions.

**Field**: Use the corrected final score to evaluate a decision that only had access to the provisional score.

---

Scenario: a churn model seems to improve strongly over the last seven days while its target is a termination under 30 days. How do you check? <!--anki:3132613765363565353062613463356239346131386466356431656437366261-->
?
1. **Check the maturity of labels**: most issues are probably not yet observable.
2. **Distinguish event absence and confirmed negative**, without automatically converting unknowns to zeros.
3. **Compare mature cohorts** with the same horizon and segments.
4. **Submit interim signals** and consolidated measures separately.
5. **Correct dashboards** and training data selection rules.

**Trap**: Promote a model on an improvement created by the observation time.

---

## Sources
- [— architecture and feature paths](https://docs.feast.dev/getting-started/architecture/overview)
- [Feast — storage online](https://docs.feast.dev/getting-started/components/online-store)
- [Feast — jointures point-in-time](https://docs.feast.dev/getting-started/concepts/point-in-time-joins)
- [Apache Beam — event time, watermarks and late data](https://beam.apache.org/documentation/programming-guide/#watermarks-and-late-data)
- [TensorFlow Data Validation — gaps training and serving](https://www.tensorflow.org/tfx/guide/tfdv)

- 14 November 2026 — Feature Time Attachment: [Feast — Point-in-time joins](https://docs.feast.dev/getting-started/concepts/point-in-time-joins).

## Connections
- [[157-data-contracts-quality|Contracts & quality]] — express freshness, units and availability
- [[158-ingestion-cdc-backfills|Ingestion & backfills]] — transport and replay temporal changes
- [[172-ml-validation-metrics|Validation ML]] — prevent time leakage
- [[113-monitoring-drift-feedback|Drift & feedback]] — interpret labels and production signals
- [[175-time-series-forecasting|Prediction of time series]] — rebuild available information
- [[150-010-analytical-data-modeling|Modeling of analytical data]] — connect business history and availability for the model
- [[150-011-analytical-sql-transformations|SQL for AI Pipelines and Datasets]] — prevents joints that reveal the future
- [[150-014-streaming-event-processing|Streaming & event processing]] — respect event time, availability and delays
- [[117-continuous-training-pipelines|Training pipelines]] — maturing labels before retraining
- [[119-prediction-contracts-features-batch|Prediction contracts, features and batch]] — production contracts and verifications
- [[00-moc-ai-engineering|MOC AI Engineering]]
