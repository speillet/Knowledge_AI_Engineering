# Data observability, lineage & operations — Flashcards
Tags: #flashcards #ai-engineering #data #data-engineering
Verified on: 9 October 2026 — technical references and examples of this file.
<!-- summary: SLO of data, freshness, completeness by segment, reconciliation, test coverage, declared or executed lineage, catalog, impact, incidents and monitoring cost, monitoring of the presence of controls, misleading freshness, impact of incidents. -->


How to set a SLO of data useful to an AI product? <!--anki:6338353835303661393538373438626139353234656232346339623536373631-->
?
Set **consumer, population, measurement, threshold and observation period**. For example: 99% daily scores expected validated and available before 6 h, on 30 sliding days, or share feature readings fairly fresh for decision.

Also count missing partitions and failures, not just received outputs. Specify the status of periods without expected activity. A SLO must trigger a decision: waiting, last valid version, abstention or intervention. It does not replace other dimensions; point data may remain incomplete or false.

---

What timestamps distinguish to measure the freshness of data served to a model? <!--anki:3863343263326139346133623435633239363266633138663365646437353334-->
?
Separate **date of the event, arrival in the pipeline and availability to the consumer**. Depending on usage, the age of a reading value or the event-to-publication delay better expresses the constraint than the duration of the job.

A task can end in a minute after waiting two hours for its source export. Similarly, dbt's `freshness` control measures the age of the chosen `loaded_at_field`: a loading date measures the arrival, not the age of the events. For a stock, the last known value can be too old even if the queries are working. Measure distributions and segments, with the expected behavior when the goal is not met.

---

Why is the maximum timestamp of a table not enough to measure its completeness? <!--anki:3233643137343761356237363436396361383066633233353134363436396365-->
?
A single recent row can make the table appear **fresh** while a partition, client, or entire source is missing. A maximum describes one end, not the expected data coverage.

Compare manifests, keys and expected volumes per segment, starting from the expected list to see the absentees:
```sql
SELECT a.client_id FROM clients_attendus a
LEFT JOIN documents d ON d.client_id = a.client_id AND d.day = DATE '2026-10-21'
GROUP BY a.client_id HAVING count(d.id) = 0;
```
The usual volumes are a useful signal, but a real drop in activity can change them. Separate observation and cause: a successful freshness check does not prove that the whole batch is publishable.

---

Do not confuse: Testing the code of a transformation and controlling the data produced? <!--anki:3466636561343939656662663466313239323462646138623331393734366664-->
?
A **code test** verifies behavior on defined inputs; a **data control** examines a real execution or its result: uniqueness, references, intervals, null rate, or business consistency.

They complement each other. Example: a unit test checks that 1,250 cents become 12.50 €; it still passes the day the source delivers 30% zero amounts, which only a `not_null` control on the partition detects. Conversely, a satisfied constraint can pass a false formula.

---

Why can two tables with the same number of rows be out of sync? <!--anki:3930303233646438626133363430626362623232663032343536343634656238-->
?
A missing line and an additional line may **cancel in the counter**. The same identifiers may also have different versions or values. The number of lines is therefore a first check, not a proof of equivalence.

Compare keys, versions, business and footprints adapted, on a consistent time perimeter. A difference in both directions locates the deviations:
```sql
(SELECT id, version FROM source EXCEPT SELECT id, version FROM cible)
UNION ALL
(SELECT id, version FROM cible EXCEPT SELECT id, version FROM source);
```
Normalize types and nulls before comparison, and then repair only listed objects or partitions.

---

Do not confuse: declared and observed at run time? <!--anki:6466646566626237666663383432376462646164313961303464643832613738-->
?
**Declared Lineage** describes the dependencies expected in the models, requests, or configurations. **Observed Lineage** links an execution to its actually used inputs and outputs, with their available identities and versions.

From dynamic SQL, files read in a UDF or an external call can escape static analysis. Example: the dbt graph declares `ref('orders')`, but a hook also reads `read_parquet('s3://exports/remises/*.parquet')`; only the observed lineage sees this source. Conversely, incomplete instrumentation can miss events. Crossing the two and measuring the coverage. A nice but incomplete graph should not be interpreted as proof of absence.

---

What is Job, Run, and Dataset used for in the OpenLineage model? <!--anki:3430623966656261333037353432663238643936313635326665386434386431-->
?
A **Job** identifies a processing; a **Run** executes a **Dataset** an input or output. Events and facets add state, schema, code and context to read or write.
```json
{"eventType": "COMPLETE", "run": {"runId": "0192f3…"},
 "job": {"namespace": "prod-airflow", "name": "features.build_daily"},
 "inputs":  [{"namespace": "postgres://crm:5432", "name": "public.orders"}],
 "outputs": [{"namespace": "s3://features", "name": "daily"}]}
```
This separation makes it possible to link a code change to versions produced during specific runs. It does not automatically collect all metadata: integrations must send them correctly. Maintaining stable identities and a namespace avoids merging homonymous tables of two environments or assigning multiple identities to the same object.

---

When do you need a column or record line instead of a simple table graph? <!--anki:6638393861353738333037313438323939663761636638626234343136323865-->
?
The lineage of **Table** Helps find consumers from a source. The **Column** specifies the fields dependent on a transformation. Record-level **registration** You can find the documents, examples or decisions concerned with a particular object.

For example, to remove data from a client, the table graph indicates that the fine-tuning dataset depends on the support base; only a record lineage lists the 37 examples that derive from it. A RAG index often asks for a document-to-chunks match, not a copy of each document content in the traces.

---

What should a data catalog do for an AI Engineer? <!--anki:6134366561633630323963663433363462623930656632623363656239623462-->
?
For each dataset: **sense, grain, owner, access, freshness and limits of use**, with diagram, examples and useful versions. The catalog helps to choose a source rather than a table with a plausible but obsolete name: between `clients` and `clients_v2`, it indicates that the first is frozen since March and counts one line per customer and per country.

Distinguish between business responsibility, technical operations and consumers. A description does not prove that constraints are controlled; connect contracts to measurements and incidents. Also check the date of update of this documentation. A catalog without owner or correction process can become an inventory of outdated promises.

---

How to estimate the impact of a corrupted data partition on an AI system? <!--anki:3738353035646266616234383436636462633564373337646166623563656530-->
?
Follow **versions and dependencies** to derived tables, examples, trained models, indexes and caches built from this partition. Distinguish consumers who actually used it from those who could use it: a model whose training window stopped at the 1er March did not read the partition of the 3 March, even if it depends on the same table.

Define quarantine, repair, reconstruction and internal notification according to risk. A correct new version does not remove predictions already made. When lineage is incomplete, treat impact as uncertain and expand checks instead of concluding no damage.

---

How to monitor data without exposing its sensitive content or creating millions of series? <!--anki:6464393833643331623965643436333462303831653666313532633763373261-->
?
Publishing of **Aggregate measures and diagnostic references** Volumes, Delay, Nulls, violations by relevant source or segment. Avoid free values. Individual identifiers and documentary content in metric labels: `docs_en_retard{client_id=…}` on the 2 Millions of customers create 2 millions of series, `{segment=…}` Create twelve.

Limit raw data samples to authorized diagnostic tools, with appropriate retention and access. A fingerprint or identifier can remain correlated: it is not automatically anonymous. Choose aggregations that detect a broken segment without copying all the dataset into the monitoring logs.

---

Calculation: on 1,440 freshness observations all expected, seven are non-compliant. What compliance rate and does it meet a goal of 99.5%? <!--anki:3837636137316539386234643461316239363835353135373163303765383438-->
?
The denominator includes non-conforming observations:
```text
= (1,440 − 7) / 1,440 ≈ 99.514%
budget = 1 440 × 0,005 = 7,2 observations non conformes
```
With these discrete units, seven pass the threshold, eight do not pass it anymore. This does not mean seven minutes of unavailability if the observations do not represent equivalent minutes. Check coverage of the collection and definition of absences. A respected global objective can still hide a systematically degraded segment.

For an operating decision, keep the individual violations and their duration. Seven consecutive observations at the same time may require a different reaction of seven isolated deviations, despite an identical final percentage.

---

Calculation: a defect touches independently 1% Lines. On a random sample of 100 lines, What is the probability of not detecting any defects? <!--anki:3061353064323333353066333439303361613332333231643266333666373465-->
?
Under these assumptions:
```text
P(no defects) = (1 − 0.01)^100 ≈ 36.6%
P(at least one fault) ≈ 63.4%
```
Therefore, an error-free sample does not establish that the dataset is sound. Errors grouped by source or period invalidate the assumption of independence and motivate stratified or targeted sampling. Reserve exhaustive controls to invariants that require it and whose cost is acceptable; announce the actual coverage of validation.

To achieve 95% probability of detecting at least one fault at this independent rate, it takes about 299 lines: resolve `0,99^n ≤ 0,05`. A rarer error requires a larger sample.

---

How to prevent quality controls from costing more than the monitored pipeline? <!--anki:3438623363313839653536653464363439663561623333323438393339323463-->
?
Classify controls according to **criticality, frequency, and required volume**. Check essential invariants on modified partitions at each release; reserve some complete scans at a justified rate. Example: Uniqueness of keys on the partition of the day, 20 GB, at each release, and on the history of 8 TB once a week.

Reuse reliable statistics when they actually answer the question, and specify what sampling may be missing. Measure cost, time, and errors detected. A control optimization should not silently remove its warranty, for example, replace a comprehensive duplicate search with an estimate without changing the publishing contract.

---

Why should a freshness control also check that its own measurement is still coming? <!--anki:3830663439336238663338653432363038396330656436633833666432616339-->
?
A **last compliant value** may remain displayed after the pipeline or collector shuts down. Without control monitoring, the dashboard may appear healthy indefinitely.

Combine measurement and time of observation, define the expected frequency and treat absence as an explicit state. Compare freshness source, publication and availability to the consumer. Test interruption of the pipeline and then of the collector. A maximum timestamp in the data is not enough if no one regularly checks its progress and the presence of all expected partitions.

---

Why can a recently updated table contain old business data? <!--anki:3162356338623163613965393463636438643433343636303364663065353262-->
?
A job can rewrite **the same old events**, giving a recent technical timestamp without new information. Modification date and business freshness are not equivalent.

Track time of events, availability and coverage by segment, in addition to the latest pipeline success. Test a frozen source with always green jobs. A global freshness can also hide a partition that no longer receives data.

---

How does lineage help deal with an error discovered in a data source? <!--anki:6362613933663833326130663433383861313239376439653033633566633132-->
?
It allows to identify **The tables, Index, features and derived models** potentially affected. The analysis must also take into account the versions and windows concerned.

Prioritize active consumers, suspend risky posts and schedule recalculations. Check for actually executed lineage: an undeclared dependency may be missing in the catalog. Once corrected, reconcile results and confirm consumers updated.

---

## Scenarios

Scenario: all jobs are green and the maximum timestamp is recent, but a client’s documents have not been indexed for three days. What do you change? <!--anki:6530363436383061373463613432356361323335353835383266323662343162-->
?
1. **Measure coverage by client and partition**, with a reference to the expected documents.
2. **Track source-to-index** to locate the loss or quarantine.
3. **Defining an actionable alert** on freshness and completeness of the segment.
4. **Repair and reconcile derivatives**, then verify their effective visibility.
5. **Test a source-limited failure** before considering sufficient monitoring.

**Trap**: add only one alert on the time of the last overall success.

---

Scenario: An incorrect currency unit has powered three drives and two indexes. How do you conduct the repair? <!--anki:6632346262303864623862373436623639646665303035626265326231313430-->
?
1. **Block spread** and identify source, period, and affected versions.
2. **Use lineage** to inventory relevant models, datasets, indexes, and caches.
3. **Correct the conversion and its controls**, then rebuild the necessary derivatives.
4. **Reassess models and uses**, returning to a valid version if appropriate.
5. **Document results already issued** and impact inventory limits.

**Trap**: correct only the current table and report the incident completed.

---

Scenario: a volume alert is triggered every weekend while the drop is normal. How do you reduce the noise without masking a failure? <!--anki:3338333935363038373531343435316538343230383030636136323362363863-->
?
1. **Compare comparable periods**: same weekday, source and segment; treat holidays and calendar changes explicitly.
2. **Checking the delivery signal**: Zero sales declared by a manifest is not an absent file.
3. **Adapt the volume threshold** to a robust seasonal reference, with absolute minimum if relevant.
4. **Keeping the invariants** of schema, Keys and expected delivery. A small normal volume may still contain false data.
5. **Replay normal weekends and injected incidents**: no file, delay, abnormally low volume; measure false positives and missed defects before activation.

**Trap**: Remove all weekend alerts or automatically learn the new reference on an extended outage.

---

## Sources
- [OpenLineage — model Job, Run and Dataset](https://openlineage.io/docs/spec/object-model/)
- [dbt — data controls](https://docs.getdbt.com/docs/build/data-tests)
- [dbt — freshness criteria](https://docs.getdbt.com/reference/resource-configs/freshness)
- [TensorFlow Data Validation — schemas, anomalies and distributions](https://www.tensorflow.org/tfx/guide/tfdv)

## Connections
- [[157-data-contracts-quality|Contracts & quality]] — measure published warranties
- [[150-013-data-pipeline-orchestration|Orchestration data]] — link successful execution and availability of results
- [[111-mlops-llmops-fundamentals|MLOps]] — trace data to model versions
- [[116-ai-sre-incidents-capacity|SRE & incidents]] — react to warranty breaches and validate trade-ins
- [[150-017-ai-datasets-corpora|Building Datasets & Corpus IA]] — find sources and consumers affected
- [[00-moc-ai-engineering|MOC AI Engineering]]
