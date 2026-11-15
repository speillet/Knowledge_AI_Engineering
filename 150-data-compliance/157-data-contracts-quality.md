# Contracts, Schematics & Data Quality — Flashcards
Tags: #flashcards #ai-engineering #data #data-engineering #quality
<!-- summary: producer-consumer contract, schema and business constraints, freshness and completeness, compatibility, migrations, quarantine, drift or incident, atomic publication and operational lineage, semantic contracts and units, compatibility of values, quarantine and population. -->


What should a data contract guarantee for an AI system? <!--anki:6465333362376365616461653439353861633730323038363164306534316230-->
?
A **Explicit agreement between producer and consumer** on the meaning, the format and conditions of delivery of the data. It specifies units, Keys, Accepted values, freshness, responsibility and change process.

For a `amount` field, knowing its numerical type is not enough: currency, taxes and monetary unit change its interpretation. The contract must be verifiable by controls and accompanied by a reaction to violations. It does not automatically guarantee business veracity; data that perfectly conforms to the scheme can remain false.

---

Do not confuse: Schema validation and business data validation? <!--anki:6138383865616161643339643433346561333131653265316532313630383136-->
?
**Scheme** describes the structure: types, required fields, formats and nullability. **Business validation** verifies relationships and invariants: a closing date follows the opening, a sum of rows corresponds to the total, a key references an existing entity.

Both complement each other. A positive integer can represent a misconverted amount of cents to euros. Some controls are local to a row; others require a reference table or multiple events. Define their cost and when they block publication.

---

Why are freshness, completeness and accuracy three distinct dimensions? <!--anki:3031626665393639653539653439356162396231393561646139346162343262-->
?
The **fresher** measures the delay in relation to the need; the **complete** checks that the expected items are present; the **accuracy** concerns their conformity to reality. A recent batch may forget one customer in two, while a complete batch may contain old values.

Follow separately the time of the last success, age of the data, expected volumes and verified samples. A green job only proves that it has finished according to its rules. Without manifests, source counters or other reference, a lack of data can pass for an absence of activity.

---

How to distinguish between no data and zero business value? <!--anki:6230396462373461656333613439363361623231343539313330326430653438-->
?
Give an explicit **semantic** to the missing values: unknown, not applicable, not yet received or true zero. A zero-command counter must not be identical to a counter impossible to calculate because a partition is missing.

Maintain an availability indicator or calculation status and define consumer behavior: wait, abstain, or use a backup value. Silent imputation can hide a collection incident and cause the model to use examples that have changed in meaning.

---

Do not confuse: backward and forward compatibility of a schema? <!--anki:3133663165663634643834393432643362653636396334656238636433326630-->
?
**backward** compatibility allows the new player to read old data. **forward** compatibility allows the old player to read new data. The behavior depends on the format and default values: adding a field is not always harmless.

With Avro, adding this field remains backward, because the new drive completes old messages with the default value; without `default`, it can no longer read them.
```json
{"name": "canal", "type": "string", "default": "web"}
```
Test the combinations of versions that will coexist: the only previous version does not represent the entire history. Renaming a business field also requires to preserve its meaning, not just to satisfy the registry.

---

How to migrate a data field without breaking all its consumers? <!--anki:6335316261383337393062343465383938393436346631616438333937623233-->
?
Follow **add → migrate → remove**: publish the new representation, adapt consumers, observe their toggle and then remove the old one according to an agreed deadline.

For example, switching from whole cents to decimal amounts requires exact conversion, a currency, and a rounding rule. Producing the two fields from the same canonical value and checking their consistency, rather than writing them independently.

Replay historical events with their version: `1250` should not be read as 1,250 euros if it represented 12.50 euros. Checking for late customers, features and existing models; providing rollback. Schema and semantic compatibility are two separate validations.

---

When to quarantine invalid data instead of blocking the entire pipeline? <!--anki:6136653135653135613963633434316239643432643337643832613335623462-->
?
When to isolate the errors allows to publish a result again **consistent and acceptable**. Keep the raw record, the reason for the rejection, its origin and a procedure of correction and replay.

The policy depends on the criticality: excluding from a 30 index product files on 50,000 to poorly formed HTML remains acceptable, publishing an exchange rate table without the euro is not. Measuring and announcing the published coverage. Setting a stop threshold, e.g. 0.5% rejections or any rejections on a critical key, and alerting; silently throwing invalid rows can create a systematic bias.

---

How to distinguish a real drift from a pipeline incident? <!--anki:3164633539376233396434623437643362343339326231636562646233353530-->
?
A drift may reflect a **population evolution**, while an incident alters its representation: modified unit, broken join, missing source. Check diagrams, volumes, null rates, versions and upstream deployments first.

Compare affected segments to known changes and raw data. Example: the share of tickets in English changes from 10% to 35% in one night, only for the web form redeployed the day before; a poorly filled language field is more likely than a customer change. Repair the collection before retraining. A statistical distance signals a change, not its cause or impact on predictive quality.

---

Why publish a dataset via a validated version rather than overwriting the files in place? <!--anki:6434356532326163356364613438613739386331646336616333326136393261-->
?
A consumer could read a **mix of versions** while writing. Building a snapshot, checking its contents and then atomically flipping a pointer or manifest makes a coherent set visible.

The warranty depends on the storage: on S3, each object is written atomically, but not an entire prefix. Write `dataset/v42/`, validate it, and then replace the `_LATEST` object that contains `v42` provides this toggle. Keeping the previous version makes it easier to go back. Manifests must designate immutable or fingerprinted objects so that the same version does not change under the drives.

---

What lineage to keep to diagnose a bad data in a prediction? <!--anki:6264366563326330353664343466303638643639326162316338643630643833-->
?
Link **source and version, transformations and configuration, published dataset and consumer**. For a prediction, save the useful references to the variables or documents actually used, with the time and version of the model.

Example: each decision records `modele=fraude-v12` and `features=snapshot-2026-10-20T06` ; a Corrupt Lot 20 October then designates exactly the decisions concerned, to play alone again. A simple “current” table name is not enough if its content has changed. Adapt the granularity of the lineage to the necessary diagnosis and confidentiality, without duplicating all the sensitive data in the logs.

---

Calculation: 9,800 documents are published on 10,000 expected. Can we announce a reliable pipeline to 98%? <!--anki:3761646434663031373663633438303138333331376636383665306564313336-->
?
A **complete 98% can be announced for this lot**, if the denominator is established and the identifiers are unique. This number does not measure freshness, accuracy or availability of the service.

Absent 200s may belong to the same client and render its experience unusable. Examine their distribution and criticality of documents, and then decide whether partial publication is acceptable. Counting only the received documents would have hidden the absent ones; one needs a reference to the expected objects, not just the processed successes.

---

Why should a data contract specify the unity and semantics of a field, beyond its type? <!--anki:6239376566623337313135623433366261316261346337393161366465653632-->
?
A **valid numeric field** can change direction without breaking the pattern: euros become cents, amount TTC became HT or local timestamp became UTC.

Documenting unit, time convention, nullity rules and business domain; adding controls on known examples and distribution changes. Versioning semantic changes and notifying consumers before publication. A `float` or `timestamp` validation will not detect these breaks. The contract must make observable what users assume, and designate the responsible for an ambiguity or a migration.

---

Why can adding a new value to an enum break a consumer without changing the physical scheme? <!--anki:3064666331323964336435633437373062633434353033363261333536643330-->
?
The consumer may assume **a closed set of categories** and not know how to process the news. The columns and types remain the same, but the semantic contract changes.

Define unknown management, compatibility and migration before publication. Test critical consumers with the new value. Validation of the `string` type is not enough to guarantee business acceptance.

---

Why can quarantining invalid rows bias a published dataset? <!--anki:6234353435333338383539363463613538626564363238396535306566323134-->
?
Errors can focus **on a source, country, or client type**. Removing these lines improves technical compliance but changes the population.

Measure rejection rate and coverage by segment, then decide if the batch remains publishable. Keep causes for correction and recovery. A dataset without an invalid line is not necessarily complete or representative.

---

## Scenarios

Scenario: all amount predictions are multiplied by one hundred after a data delivery, but no type has changed. How do you react? <!--anki:3138663766646436623263653462613839303930316363366363353533326132-->
?
1. **Suspend the affected usage** or revert to a validated version based on business risk.
2. **Compare raw data** and upstream changes: currency, unit, taxes, conversion.
3. **Correct the contract** with an explicit unit and reference examples.
4. **Add consistency and distribution controls** that can detect this change.
5. **Identify the results concerned** by the lineage and organize their recalculation.

**Trap**: Retrain to absorb an incorrect conversion and perpetuate the incident.

---

Scenario: your ingestion rejects 2% documents and stays green, but all come from the same customer. What do you change? <!--anki:3266396664343830323135643462646539356334383530326634613536336536-->
?
1. **Measure coverage per customer**, not just the overall success rate.
2. **Inspect retained releases** to determine if the problem is with the format or collection.
3. **Set a threshold per segment** and an explicit partial release status.
4. **Correct and replay** documents without duplicating those already published.
5. **Check for product impact**, including responses built without missing documents.

**Trap**: Lower the alert threshold to improve the dashboard without repairing the cover.

---

Scenario: a producer wants to delete a column that several models use tomorrow. How do you organize the migration? <!--anki:3532383236393165306433653436666361323931643638666530343663653264-->
?
1. **Censor consumers** with lineage, including historical workouts and rarely performed jobs.
2. **Define the target representation** and the conversion or replacement rules.
3. **Introduce a compatible period** and test old and new reading on real data.
4. **Version pipelines and models** and validate their behavior before switching.
5. **Remove the old field** after confirmation of the migrations and the possibility of replay.

**Trap**: only check that the services start, without testing the values produced.

---

## Sources
- [TensorFlow Data Validation — Data Controls, Schema and Distribution Differences](https://www.tensorflow.org/tfx/guide/tfdv)
- [Confluent — Evolution and Schema Compatibility](https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html)

## Connections
- [[158-ingestion-cdc-backfills|Ingestion & repeats]] — enforce the contract during collection
- [[159-temporal-data-features|Temporal data]] — define availability and freshness of variables
- [[151-data-curation-annotation|Curation & annotation]] — complements editorial quality with operational guarantees
- [[153-data-flywheel-versioning|Versioning of data]] — publish and trace consistent versions
- [[113-monitoring-drift-feedback|Drift & feedback]] — distinguish population change and collection failure
- [[150-010-analytical-data-modeling|Modeling of analytical data]] — define grain, keys and sense of measurement
- [[150-012-columnar-storage-lakehouse|Columnar storage, partitions & lakehouse]] — publish a consistent and readable report
- [[150-016-data-observability-lineage|Observability, lineage & data exploitation]] — measure published warranties
- [[117-continuous-training-pipelines|Training pipelines]] — stop retraining on invalid data
- [[119-prediction-contracts-features-batch|Prediction contracts, features and batch]] — production contracts and verifications
- [[00-moc-ai-engineering|MOC AI Engineering]]
