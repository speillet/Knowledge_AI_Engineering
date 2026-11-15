# Artefacts, registry & releases ML — Flashcards
Tags: #flashcards #ai-engineering #mlops #classical-ml #registry #deployment
Verified on: 12 November 2026 — MLflow examples target the API 3 and remain to be adapted to the installed version.
<!-- summary: run, logged model and registered version, full inference package, MLflow 3 URI, alias resolution, integrity and provenance, secure serialization, clean environment loading, output contract, predict_proba, approval, registry backup, retention, conversion, release thresholds and rollback, immutable resolution, network dependency on loading. -->


Do not confuse: Experience run, journaled model and registry version? <!--anki:6166313136613661653031633431336539323137646439633965333963323364-->
?
A **run** describes an execution: parameters, referenced data, metrics, and artifacts. A **journalized model** is a produced or captured inference object; MLflow 3 also allows it to be logged out of an active run. A **registered version** belongs to a model name in the registry and references a model to govern.

A run can produce multiple models. Two registered versions can reference identical content; their number is not a weight footprint. Link these identities to reports and the actual release served. No version number proves, alone, quality or approval.

---

What must an ML release contain to reproduce a decision in production? <!--anki:3735643135303136343033653430333339333963643735633836396461376563-->
?
The inference package must immutably embed or reference **learned preprocessing, estimator, calibrator, and output contract**. The release adds runtime image, dependencies, feature contract, decision rule, and approval proofs.
```text
release → inference package + image + features + policy
→ package learned transformations + model + calibration
evidence → data + recipe + evaluations + approval
```
This schema is conceptual, not an imposed MLflow format. A "current" scaler or an out-of-manifest mutable threshold can change decisions without changing weights. The rollback must find the compatible combination, as well as its dependencies still available and their access controls.

---

Why use the URI returned by log_model in MLflow 3? <!--anki:3333313239666133343230663465306339623833393732623231666135636566-->
?
MLflow 3 gives logged models their own identity. Do not infer their location from an old run artifact path; use the result of logging.
```python
# adjusted pipeline; pre-prepared signature and example
info = mlflow.sklearn.log_model(
    pipeline, name="model", signature=signature,
    input_example=X_example,
)
version = mlflow.register_model(info.model_uri, "retention")
```
The current argument is `name=`; `artifact_path=` is deprecated for this API. Sustainably keep URI of the model logged and version returned by the record. Then check the load from the target environment: a successful record does not run all service tests and does not constitute a promotion.

---

How to load a registry alias without losing the version that was actually resolved? <!--anki:6231353339383630633731643436653639616132383565383337336633633732-->
?
Solve the alias **once**, then load the resulting explicit version and enter it in the deployment manifest.
```python
from mlflow import MlflowClient
import mlflow.pyfunc

client = MlflowClient()
mv = client.get_model_version_by_alias("retention", "champion")
uri = f"models:/retention/{mv.version}"
model = mlflow.pyfunc.load_model(uri)
```
Re-reading the alias to log its target after loading via the alias can assign the wrong version if a promotion occurs between the two operations. This code reduces this run; it does not make the deployment atomic. Check the artifact, image and effective version of each replica, and then define the policy of transition between versions and the processing of in-flight requests.

---

Why is a SHA-256 footprint not enough to allow a model? <!--anki:3730663735336135393862613465643439336336643732373965393932353361-->
?
A **fingerprint** is used to verify that the bytes match an expected value. It does not prove that this value is from an authorized producer, nor that the model has passed the necessary controls.

Get the expected fingerprint from a provenance-controlled manifest; link producer identity, recipe, dependencies, and trusted report. Check for loaded bytes, not just a file name. An attacker who simultaneously replaces the file and its fingerprint in the same unprotected location retains an appearance of consistency. Integrity completes a trust chain, it does not create it.

---

What is the risk of loading a serialized model with pickle or joblib? <!--anki:6130356338346162393331343438663439383139333566633865306230386230-->
?
Loading can **execute code**: a model file is not necessarily a simple matrix of numbers. With pickle-based formats, loading only artifacts with provenance and integrity is established, in an environment with limited rights.

A file scan or expected `.pkl` extension does not guarantee safety. Other formats may reduce some risks, with specific limits: types allowed to examine, operators supported, runtime and resources to control. The choice of format must also preserve the useful behavior. A safe artifact to store is not automatically safe to deserialize.

---

What should a load test do in a clean environment? <!--anki:6234346234666338663334323464303161353633336333386137636539313639-->
?
Starting from the **target image**, with no hidden state of the notebook: load the published artifact, import custom transformations, and then predict on representative cases and invalid entries.

Verify versions of libraries, resources, external files, and system dependencies that are actually required. Compare outputs and decisions to references with justified tolerances. A Python dependency file does not necessarily capture drivers, native libraries, and runtime configuration. scikit-learn does not guarantee loading between different versions. Retry this test after a dependency update, even when the weights remain the same, and keep the image that passed the check.

---

Why does the output contract need to identify the order of classes and units? <!--anki:3538373461366533333139333464353561333935616338626365623134663931-->
?
A probability matrix has a **column order**, not a universal meaning. For a scikit-learn classifier, connect the columns to `classes_` and a versioned definition of labels; do not assume that the second column always means "adverse event".

Documenting also unity, horizon, form, invalid values and possible reverse transformation. A forecast of turnover logarithm does not spontaneously become a forecast in euros. Test the contract with cases whose meaning is known. A correct form output can be consumed upside down without technical error, and then trigger bad decisions on a large scale.

---

How to avoid serving classes when consumers expect probabilities? <!--anki:3734383833623439346666323439393461616136613066633864336638346464-->
?
Explicitly set the **inference mode** of the packet and test its outputs after reloading. `predict` and `predict_proba` do not offer the same contract; the signature alone does not choose the business intent.

For the scikit-learn flavor of MLflow, `pyfunc_predict_fn="predict_proba"` allows to choose this method for the pyfunc interface, if the estimator proposes it. Building the signature from these probabilities, keeping the order of the classes and testing the call via pyfunc. This option is not a universal property of all flavors. Changing only the consumer to interpret a class as a score creates a silent error.

---

Do not confuse: READY version, approved model and ready service? <!--anki:3438623433646233636135393465646261616335343232303832353734396437-->
?
The status **READY** of the MLflow registry indicates that the creation of the version has been successful. An **approval** is an evidence-based governance decision and policy. A **ready service** has loaded the expected release and can respond according to its operational controls.

These reports fall under different mechanisms. Do not automatically connect traffic exposure to the end of the record alone. Check report, promotion authority, load, dependencies, and capacity; expose the actual identity in diagnostics. An available registry may contain a rejected model, and a trusted version may fail when starting a replica.

---

What should an approval tag prove in the registry, and how to avoid overinterpreting it? <!--anki:3832386564303830383661633434346639383166396433363639643762653837-->
?
A tag can **reference** report, decision, responsible and applied policy. Its value is not, by itself, an unfalsifiable proof nor a rule of access control.

Restrict who can edit the approval and move aliases; keep a verifiable history related to the exact version and artifacts. The deployment process checks for these items according to its policy. A tag copied from an old candidate must not approve new bytes. When a waiver exists, save scope, expiration, and countervailing action. The approval must remain explainable after an incident, even if the current tags have changed.

---

Why is backing up the registry database not enough to restore the ML system? <!--anki:3535323065356363386239613463353738623662373633663435356239636464-->
?
**metadata** and **artifacts** can live in different storages: the database describes runs and versions, while the object storage contains the model files. Restoring only the database can leave references to objects missing.

Set backups consistent with the expected consistency; also preserve necessary manifests, images, configuration and access, according to procedures adapted to the secrets. Test an isolated restore: solve a version, download its bytes, check their fingerprint, load and then predict. The goal is to measure the ability to recover, with RPO and RTO, not just to get a functional registry screen.

---

How to set the retention of artifacts without breaking a rollback? <!--anki:3131383336316539306133333436383961333062346132393166636132386566-->
?
Build retention from the still-needed **references**: releases served, trusted backtracking, surveys, and retention obligations. An older version can remain critical even if no common aliases designate it.

Before deletion, inventory consumers and dependencies; verify that compatible images, features and configuration remain available for the retained versions. Allow recovery time and test recovery. Retention must also respect the restrictions applicable to embedded data: "keep everything" is not a universal policy. Deleting a run or moving an alias is not a demonstration that all associated bytes can be destroyed.

---

Calculation: 30 artifacts of 400 MiB each are referenced from three environments. What storage should be expected? <!--anki:3266393734343236656437633436613338623761333766643339326665373566-->
?
If all three environments **reference the same objects stored once**, the total content represents:
```text
30 × 400 = 12 000 MiB
12 000/1 024 = 11,71875 GiB
```
With three independent full physical copies, you need **36,000 MiB**, or **35.15625 GiB**. These numbers exclude additional versions, backups, metadata, internal replication, and images.

An alias or URI does not demonstrate deduplication of storage. Check the actual behavior of the registry and the promotion procedure; separate logical bytes, billed bytes, and transfer costs. A copy between environments may be voluntary to isolate access and availability.

---

Why does a model conversion to another format require a new validation? <!--anki:6132333033643138633461663432323562386266613066333235663463336334-->
?
A conversion can modify **digital accuracy, operators, preprocessing, or output contract**. Not all models and operators are supported by all formats and runtimes.

Compare original and converted to common cases, extremes, unknown categories and values close to the threshold. Set numerical tolerances, then check decisions: a small probability gap can cross a business threshold. Also measure latency and memory in the target environment. Keep origin, conversion tool, version and relationship with the new artifact. A successful conversion on an example proves neither global equivalence nor maintenance of quality in production.

---

Why can two releases produce different decisions with the same weight? <!--anki:3133613534356663393731323430613238333962366534303739373134373965-->
?
Decisions depend on **the entire chain**: available data, transformations, calibration, class order, threshold, business rule, and execution configuration. Changing one of these elements can keep weights while changing the result.

Separately identify artifact and complete release, and compare manifests during regression. A registry version number does not replace this description; conversely, re-registering identical weights does not guarantee a new capacity. Test the combination actually delivered, and then assign the effects to its changes. The diagnosis must be able to explain why the same client received a different decision on two dates.

---

Why does a threshold change have to follow a promotion procedure? <!--anki:6164626332643133363239643465616138643934313536336466353738393730-->
?
The **threshold** transforms scores into decisions and changes the accuracy, recall, volume processed and load of the teams. A better ranking does not imply that the previous threshold remains adapted; changing the threshold without changing the weights can be enough to saturate a human review.

Version the policy, document objective and constraints, and then evaluate decisions on data independent of its adjustment. Check calibration and capacity, schedule gradual deployment and backtracking. Keep model, calibrator and effective threshold with each decision. A proportionate procedure may be light, but it must leave evidence of what has been authorized and why.

---

Why solve a model alias only once at the start of a job batch? <!--anki:3933383431353437663936393435646362316166633635386532396265303438-->
?
An alias can change during the job and lead to **a batch mixing multiple versions**. Solving an immutable version and saving it with the results makes processing consistent.

For a recovery, keep this version unless explicitly migrated. A change of aliases should not silently alter the remaining elements. If the initial model is removed for security, interrupt and apply a documented removal policy.

---

Why test the loading of an ML artifact without undeclared network access? <!--anki:3430346264306631653964663437303539363666346261343464363839666134-->
?
A package can download **a tokenizer, code, or additional weights** at loading, so it is not self-contained and its reproduction depends on a mutable source.

Declare and embed the necessary dependencies, or accurately document their controlled recovery. Test in clean environment with limited network. A success on the training machine can come from local caches absent in production.

---

## Scenarios

Scenario: the model works in the notebook but the production image does not find a preprocessing class. What do you change? <!--anki:3234383065626134626138333430636239643563393566386537336332353334-->
?
1. **Block promotion** and keep release in place; successful training does not validate the package.
2. **Reproduce in a clean image** with the only published artifact: identify local module, import or missing implicit file.
3. **Distribute the component** in a versioned way and declare its dependencies; avoid manual copying from an author's workstation.
4. **Reload and test the channel** on references, invalid entries and output contract; check target environment and resources.
5. **Publish a new release** with the report and footprint of the verified package.

**Pip**: Add a local path to the notebook and then conclude that the deployment is repaired.

---

Scenario: champion points to the 18 version, but answers still come from the 17 version. How to investigate? <!--anki:3961613463663662373736663432626661613835666637666535373565356463-->
?
1. **Read the actual identity** of replicas and replies; separate target from alias and packet actually loaded.
2. **Review the procedure**: Move the alias, start processes, caches, and any failed loads.
3. **Resolve an explicit version** and deploy the corresponding manifest, with loading controls and controlled transition.
4. **Check traffic** and distribution of versions until the end of the deployment; coexistence may be voluntary during a canary.
5. **Correct assignment** of metrics if they were tagged with the current alias.

**Trap**: consider the alias move as an automatic and simultaneous broadcast to the services.

---

Scenario: after restoration, the registry displays the champion but its load returns an object not found. How to resume? <!--anki:3964613865643464336131653433666162316237343165303565626633323265-->
?
1. **Identify missing reference**: URI, object, storage version and rights; distinguish absence and denial of access.
2. **Find a consistent backup** of artifacts and metadata, without arbitrarily moving the alias to an available file.
3. **Check provenance and fingerprint**, then load into the expected image and run the reference cases.
4. **Restore an approved release** or apply the intended gradient mode; do not improvise a model without proof.
5. **Complete the recovery exercise** to cover artifacts, images and access, and then measure actual RPO and RTO.

**trap**: confuse accessible registry interface and ability to produce correct prediction.

---

## Sources

- [MLflow — registry, versions and alias](https://mlflow.org/docs/latest/ml/model-registry/workflow/) — identity distinctions and alias resolution.
- [MLflow — migration vers MLflow 3](https://mlflow.org/docs/latest/ml/mlflow-3/) — journaled models and URI returned.
- [MLflow — API scikit-learn](https://mlflow.org/docs/latest/api_reference/python_api/mlflow.sklearn.html) — `name`, `pyfunc_predict_fn` and result of `log_model`.
- [MLflow — storage architecture](https://mlflow.org/docs/latest/self-hosting/architecture/overview/) — separation metadata and artifacts; the proposed restore procedure follows from this.
- [scikit-learn — persistence of models](https://scikit-learn.org/stable/model_persistence.html) — security, dependencies, compatibility and conversion.
- [scikit-learn — Classifier API RandomForestClassifier](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html) — relationship between `classes_` and probability columns.

- 14 November supplement 2026 — Alias and model versions: [MLflow — Model Registry Workflows](https://mlflow.org/docs/latest/ml/model-registry/workflow/).

## Connections

- [[111-mlops-llmops-fundamentals|MLOps and LLMOps]] — identities, responsibilities and lineage
- [[112-model-cicd|CI/CD models]] — tests and promotes a release
- [[114-reproducibility-variance|Reproducibility]] — environment and historical evidence
- [[116-ai-sre-incidents-capacity|SRE of AI Systems]] — recovery and effective identity
- [[117-continuous-training-pipelines|Training pipelines]] — produce and select candidates
- [[119-prediction-contracts-features-batch|Prediction contracts]] — entries, features and results publication
- [[00-moc-ai-engineering|MOC AI Engineering]]
