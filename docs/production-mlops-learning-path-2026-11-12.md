# MLOps journey: from experience to actionable prediction

Review of the 12 November 2026. This course accompanies the nine topics of `110-mlops-cicd`. It follows a fictitious case of subscription termination; the names of releases, data and thresholds illustrate an approach, without constituting a ready-to-deploy configuration.

## 1. Define what the model should predict

The unit is **an active subscription at a reference date**. The target is its termination within the next thirty days. A customer with three subscriptions can therefore correspond to three observations. The definition specifies suspensions, renewals and corrections; it has a separate version of the model.

A prediction from last week does not immediately receive a negative label because no termination is yet observed. The horizon must be elapsed, then the collection time respected. The metrics relate to sufficiently mature cohorts, with coverage of the reconciliation and explicit rule for issues still unknown.

The business owner defines usage and processing capacity; data, model and operations managers define their commitments and take-back conditions. The initial deliverable is a prediction contract, before a choice of registry or orchestrator. See [the Prediction Contracts](../110-mlops-cicd/119-prediction-contracts-features-batch.md) and [the MLOps Responsibilities](../110-mlops-cicd/111-mlops-llmops-fundamentals.md).

## 2. Build the data that is actually available for decision

At each reference date, reconstitute the information then available: past activity, seniority, offer and known incidents. An incident dated Monday but received on Wednesday was not available for a decision made Tuesday. Distinguish event time and availability, and test late arrivals.

The [Feast on point-in-time joins](https://docs.feast.dev/getting-started/concepts/point-in-time-joins) documentation describes the history search in a TTL window. This does not exempt you from checking the availability, deduplication and backend rules separately. A value available in the storage may also be too old for business use.

The deliverable is an identified snapshot with schema, provenance, semantic controls, eligibility and label definition. Keep rejections and their reason within the limit provided by the data policy. A source that changes amounts from euros to cents can keep its types while invalidating the model. See [the Time Data](../150-data-compliance/159-temporal-data-features.md).

## 3. Separate recipe, execution and candidate

The **recipe** describes transformations, learning, and evaluation. A **run** executes this recipe with accurate data, parameters, and environment. The **candidate** is the product package, with its results and limitations.

Timely separation of sets when required, respecting availability and label maturity. Adjusting imputation, encoding, and normalization to only data allowed by the protocol. Allow for calibration adjustment and threshold selection without reusing the final test as a selection lever. Properly nested cross-validation can organize these separations; four separate files are not a universal obligation.

Tracer versions, splits, hyperparameters, seeds, environment and results per segment. **Save a seed does not apply** to different generators. The determinism guarantees depend on the components and platforms. [PyTorch describes these limits](https://docs.pytorch.org/docs/stable/notes/randomness.html); the notions of seed and historical proof are developed in [the Reproducibility topic](../110-mlops-cicd/114-reproducibility-variance.md).

## 4. Publish a package that can actually predict

The package contains the learned transformations and model, as well as the calibrator when used. A release also references feature contract, image, output, and decision policy. A weight-only file is not enough if the service uses an independent and mutable encoding or threshold.

With [MLflow 3](https://mlflow.org/docs/latest/ml/mlflow-3/), use `name=` in the API logging and keep `info.model_uri`, returned by `log_model`. Then save this URI and keep the resulting registry version. Do not rebuild the model path assuming the old location in the artifacts of a run.

The signature describes a technical contract; it does not prove that the units or the horizon have the expected meaning. Test the probabilities with their order of classes and the mode of inference chosen. A consumer who expects a probability should not silently receive the class produced by `predict`.

In a clean image, load the published artifact, run known cases, and test for errors. Checking provenance before deserialization: Pickle-based formats can run code. A conversion or dependency update requires proper validation; [scikit-learn does not guarantee load compatibility between versions](https://scikit-learn.org/stable/model_persistence.html). See [artifacts, registry and releases](../110-mlops-cicd/118-ml-artifacts-registry-releases.md).

## 5. Decide if the candidate deserves a promotion

Set criteria before comparison: useful quality, calibration, segments, cost, latency, and decision processing capacity. Compare candidate and champion on the same cases, with uncertainty. A margin of non-inferiority may be suitable for a less expensive candidate; an average gain should not hide a regression on a segment necessary for use.

Keep historical reference and recent cohort mature enough: they answer different questions. A broken source can produce a drift, then a model perfectly adapted to this error. The rework trigger initiates an investigation or pipeline; it does not allow promotion. This separation corresponds to the architecture described in [the Google Cloud MLOps Guide](https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning).

The deliverable is an approved report related to an immutable release. Conceptual example, with fictitious references:

```yaml
# Illustrative manifesto; no implicit MLflow scheme.
release: retention-r17
recipe: recette-v6
model_uri: models:/retention/17
artifact_digest: verified-package-digest
runtime_image: image-referencee-par-son-digest
features_contract: subscription-v4
label_definition: churn-30d-v3
decision_policy: retention-v8
training_snapshot: retention-s042
validation_report: approved-report-r17
rollback_release: retention-r16-revalidee
```

The number 17 the registry and the release coincide here by choice of example; They don’t need to coincide. Proof of approval and promotion rights remain separate from an editable tag. See [CI/CD](../110-mlops-cicd/112-model-cicd.md) and [pipelines continus](../110-mlops-cicd/117-continuous-training-pipelines.md).

## 6. Deploy the approved version and identify the one that responds

Solve the explicit version alias only once, and then deploy that version and log its actual identity. Moving `champion` does not reload processes that have already started. [MLflow Registry alias](https://mlflow.org/docs/latest/ml/model-registry/workflow/) refers to a version; the deployment must organize loading, transitioning, and checking replicas.

```text
recipe + snapshot → training → candidate + report
                                         ↓ approbation
                                 release explicite
                                         ↓ Deployment
features → contract → loaded package → score → policy → decision
                                         ↓
                         traces + mature labels → evaluation
```

A canary monitors behavior, errors, resources, and available quality. With a target at thirty days, it does not immediately prove the final quality. A shadow model does not influence the decision; its results alone do not prove the effect of the policy that would be applied. The limits of the canary are described in [Google SRE](https://sre.google/workbook/canarying-releases/).

The rollback gives a **compatible combination**: model, transformation, contract and policy. Test that it can still read its features and load its artifacts before relying on it.

## 7. Deliver consumable predictions in batch or online

Online, reserve a global timeout for waiting, features, calculation, and response. Predicting behavior if a source is missing: Validated rescue, still allowable value, or delayed decision. Replacing any absence with zero to maintain a successful response rate can hide a quality incident.

In batch, define a logical identity with release, snapshot and partition; each retry keeps the same intent. Publish only after coverage control, uniqueness and outputs. A partial release must be planned and visible. Actions triggered downstream need their own protection against duplicates.

For twelve million lines in two hours, the average floor is about **1,667 useful lines/s**, publication included. If there are only ninety minutes left for scoring, it takes about **2,223 lines/s** at this stage. Measure on actual sizes with margin, covers and imbalance of partitions.

Keep reference time, calculation date, validity and release. A recent calculation on an expired snapshot does not constitute an updated score.

## 8. Measure quality without confusing lack of evidence with success

Monitoring availability, latency, saturation, data, output distribution and business output. The drifts detect changes; they do not prove a drop in quality, and a stable distribution does not prove the absence of regression.

Bring labels closer to the prediction identity and the horizon, not just the client. Report maturation, coverage and corrections. Out of a thousand predictions of which six hundred have an exploitable label and four hundred eighty are correct, the observed accuracy is **80% on the labeled part**, with **60% of coverage**. This does not demonstrate 80% on the entire population.

When decisions determine which outcomes become visible, labels are selective. A human review is not necessarily the counterfactual outcome. A weighting does not recreate labels for groups that have no chance of being observed; see [Original work on selective labels](https://pmc.ncbi.nlm.nih.gov/articles/PMC5958915/). The diagnostic path is in [monitoring and feedback](../110-mlops-cicd/113-monitoring-drift-feedback.md).

## 9. Prove recovery capability

A registry restore must cover metadata and artifacts, which are [separate storage components in MLflow](https://mlflow.org/docs/latest/self-hosting/architecture/overview/). Test in isolated environment: find the approved version, check bytes, load into the compatible image, retrieve the necessary features and produce the reference results.

Measuring RPO and RTO. An accessible record with missing artifacts does not restore service. The end of the technical incident does not close the ML analysis: identify affected decisions, missing results, disrupted labels and possible contamination of future drives. See [SRE, Incidents and Capacity](../110-mlops-cicd/116-ai-sre-incidents-capacity.md).

## Perimeter of enrichment

This pass adds **68 maps**, including six situational maps, and deepens **33 existing answers**. The section goes from **7 cards / 128 cards to 9 cards / 196 cards**. The two new cards separate package and release governance, then contract data and exploit predictions. The seven existing cards each earn four targeted cards.

The corrections include MLflow 3, alias resolution, statistical validation, seed, selective labels, recall estimation, unavailability of monitoring and Gartner forecasts. The added facts and APIs were confronted with the primary documentation cited and the MLflow/Fast references of Context7.

The old general verification dates remain: this pass does not constitute a new exhaustive verification of the cloud offers, the regulatory texts and all the examples of the old files. The MLflow snippets are documentary; MLflow and Feast are not installed or executed by the deposit controls.

The pre-existing **2,372 questions and Anki IDs** are retained. New cards receive new IDs; no cards are removed. Anki content, link, catalog, and export checks accompany delivery.

Local Validation: `make check` succeeds, including **54 tests**, ruff, mypy and both workshops. Lint reports **zero error and zero warning**. Inspection of exported package finds **2,440 active cards** with expected IDs and **71 old cards removed still suspended**. Added calculations and syntax of Python snippets have also not been checked for an Mnippets test;

The [Additional topicality check](reference-currency-check-2026-11-13.md) then controls the announcements, hosting methods, repositories and regulatory transitions still mentioned in these topics and their neighbors.
