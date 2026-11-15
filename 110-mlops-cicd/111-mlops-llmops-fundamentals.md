# MLOps & LLMOps — Fundamentals — Flashcards
Tags: #flashcards #ai-engineering #mlops #llmops #llm
Verified on: 29 September 2026 — This factsheet lists products, versions or regulatory texts that are evolving quickly.
<!-- summary: DevOps or MLOps, specificities of the LLMOps, what to version (code and config, models and data), model registry, lineage, reproducibility, dev/staging/prod environments, role of the Lead, consistent release manifest, CI/CD/CT, recipe and run, technical, statistical and business validity, data dependency debt, model owner, label debt. -->


What is the MLOps? <!--anki:72493079506c593c216d-->
?
The **MLOps** organizes the construction, delivery and operation of ML systems: data, training, validation, prediction, monitoring and withdrawal. It combines automation, traceability and operational responsibilities to maintain a useful behavior over time.

For example, a new week of sales can produce a candidate with the same code but with other weights. You have to find his data, his recipe, his evaluations and the promotion decisions. The monitoring starts an investigation; it does not automatically command a retraining. Success is also measured by delivery time, stability, cost and ability to restore, beyond the score of a notebook.

---

Do not confuse: DevOps and MLOps? <!--anki:47765959597d7b3a6634-->
?
**DevOps** organizes the delivery and operation of software, including code, configuration and infrastructure. **MLOps** extends this approach to data, models and statistical evaluations, because a change in data can change behavior without changing the code.

An ML release must link code, data, training, and model versions to validation results, so rollback involves multiple artifacts, and code testing alone is not enough to detect a drop in predictive quality.

---

What is the LLMOps compared to the classic MLOps? <!--anki:4f587838485048773f3c-->
?
The **LLMOps** applies this discipline to a system whose behavior also depends on the prompts, contexts, indexes, tools and models that may be provided by API.

A change to the corpus or permission can change the results without changing the weights, so the release must identify the combination actually executed and its evaluation protocol. Monitor completed tasks, external effects, latency and cost, with vendor change management. Business invariants remain controlled by the application; the variability of the text does not justify a variability of rights or amounts.

---

What code and configuration artifacts do I need to version in a LLM system? <!--anki:723b4b462f6130794733-->
?
- The **application code** and pipelines
- **Prompts**, including tool descriptions
- The **Generation Configuration**: exact model and version, temperature, `max_tokens`, output scheme

Changing one of them changes the behavior: each response in production must be able to be related to the exact **combination** that produced it ([[13-production-prompts|Prompt in production]]).

A manifest can link `git_sha`, version of the prompt, model, and configuration imprint. Do not copy the secrets: keep their references and the necessary access rights, separate from the versioned artifacts.

---

What model and data artifacts do I need to version in a LLM system? <!--anki:364c47756e29552b3e-->
?
- The **fine-tuned weights or adaptors** ([[51-fine-tuning-adaptation|LoRA]]), with the data and recipe that produced them
- The **golden datasets** of eval, so that two scores are comparable
- The **Index RAG** source documents, Chunking and Modelembedding ([[153-data-flywheel-versioning|versioning]])

A test score without the version of the test game means nothing.

Two indexes using the same documents but different chunks or embeddingss are two separate artifacts; a "corpus-production" folder name is not enough to reproduce them.

---

What is a registry model? <!--anki:726f4b36424a7d697952-->
?
A **model registry** catalog of versions, their provenance and metadata relevant to their life cycle: owner, recipe, evaluations, status and artifact references. File storage can be provided by a separate service.

Do not confuse version number, mutable alias, and deployment authorization. A `champion` alias can designate an approved version without all replicas having loaded it. The promotion mechanisms vary; MLflow prefers aliases and tags rather than its old stages. Registering does not prove either quality or security of the file, nor compatibility with the serving environment.

---

What is the lineage of a model? <!--anki:4a724a21746435493b53-->
?
The **lineage** links a served version to the data, transformations, code, parameters, training execution and validations that produced it. Its coverage must be checked; a tool does not automatically discover all dependencies.
```yaml
release: retention-r17
image: registry.example.org/scoring@sha256:empreinte-a-remplacer
modele: models:/retention/17
features: client-30j@v4
train: retention-train@snapshot-042
evaluation: retention-validation@v9
```
This snippet is illustrative: replace references with recoverable objects and their actual footprints. To investigate, go back from a prediction to this release and its run. Names are not enough if the files have been rewritten or deleted. Keep the access and retention times necessary for the authorized reconstruction.

---

Do not confuse: version and pin? <!--anki:6c38252c232c417e7d21-->
?
- **Version**: keep the **history** of artifacts (code, prompts, weight, datasets) to be able to go back and compare
- **Pinch**: declare in the deployment an exact **version** (digest, dated identifier) instead of a moving alias like `latest`

We can very well version its prompts **and** call a model via an alias that changes under your feet: the versioning alone does not protect ([[142-llm-reliability-resilience|Pin the model]]).

---

Why is reproducibility difficult with LLM? <!--anki:6f574d3477383b5a6656-->
?
**Non-determinism** (sampling), **versions of API models that change**, GPU dependencies — from where: fix seeds/temperature, **pin versions** and plot configs.

Even with a seed, the order of parallel calculations, kernels, or batching can change some tokens choices. Reproducing the environment reduces variance without always removing any differences. To compare versions, repeat tests, and measure score distributions, also keeping tool inputs and results.

---

How to manage dev/staging/prod for a LLM app? <!--anki:69354f78696b443b7756-->
?
Promote a **consistent versioned set**: code, model, prompt, tool schemas, and configuration, with the same deployment mechanisms. Separate identities, secrets, data, and permissions from environments.

Example: a staging replays realistic requests but directs sending and payment tools to test duplicates; changing only the model is not enough to isolate it.

Combine properly depersonalized representative cases and synthetic cases covering the limits. Require [[112-model-cicd|eval gates]] before promotion and predict rollback. A mutable vendor alias also requires to trace the resolved version and detect changes undergone without application deployment.

---

What is the role of the Lead on the MLOps panel? <!--anki:7a3e4144593a524b4139-->
?
The Lead organizes **verifiable contracts and responsibilities**: who produces the data, validates the candidate, authorizes the promotion, operates the service and can stop a failed processing.

Define a nomenclature of releases, risk-based gateways, a system manager and tested recovery procedures. Provide for on-call transmission with dashboards, thresholds and diagnostics. A common registry facilitates inventory, but several tools can coexist if contracts remain consistent. Measure change delay, deployment failures and recovery time to verify that standards really help teams.

---

Why should an AI release manifest designate a coherent set of artifacts? <!--anki:3238613763396433623462303430633239386138326562306435343466343561-->
?
A **release** must link code, model, tokenizer, prompt, index or features and configuration by immutable versions. Their current aliases can evolve independently.

Publish this manifest after validation of the combination, then have the references solved once for the run. Keep its identifier in the results and traces. Test a redeployment from the manifest without implicit access to "latest". A collection of versioned artifacts is not enough if no one knows which combination actually served a decision.

---

Do not confuse: CI, CD and CT in an ML system? <!--anki:3635316166396234653463373430616639393564653836386162653462626165-->
?
**CI** checks for code and component changes; **CD** prepares and delivers validated artifacts to environments; **CT**, continuous training, runs the recipe on data to produce new candidates.

A change of code can change the recipe without immediately leading to a complete model. New data can trigger a training without changing this recipe. Separate identities, versions and pass criteria for both channels. “Continuous” does not mean uninterrupted calculation or promotion without control: frequency and automation depend on the need, cost and availability of reliable labels.

---

Do not confuse: pipeline recipe and drive execution? <!--anki:6165356234363933353831313433313539373466666136306362363563313131-->
?
The **recipe** is the code and configuration that defines the steps; an **execution** applies this recipe to specific entries, at a given time, with its own results and errors.

Two runs of the same recipe can produce different models because of random data, parameters, or operations. Each run must reference recipe, snapshots, environment, and artifacts. A resume must not overwrite the identity of the previous run or mix their outputs. To investigate, find the run actually deployed, rather than just the last commit of the repository or the last successful workout.

---

Why distinguish technical validity, predictive quality and business utility in an ML release? <!--anki:6262356431636266633963363437326638356265373965363737626165313065-->
?
A model can **load correctly**, predict with a good score and still be useless: too long a delay, excessive cost or decision that does not improve the targeted process.

Define three separate pieces of evidence: contracts and operations, relevant population metrics, and then business consequence with its assumptions. A more accurate forecast may not change the stock if the decision does not use it. Set the acceptance criterion and the person responsible for each level before promotion. A technical success does not replace statistical evaluation; an offline score alone does not demonstrate the effect produced under real conditions.

---

Why inventory dependencies and consumers of model data? <!--anki:3865333039316664303630653438386639323064336336343361376237666330-->
?
The **Hidden Dependencies** make changes risky: a column can come from another model, and a score in turn becomes a variable consumed elsewhere without explicit contract.

Document producers, transformations, purposes and consumers, with versions and responsible. Before modifying a definition or removing an output, examine these uses and plan a migration. The traceability of training is not enough to discover a consumer who directly reads a table of predictions. The MLOps therefore includes contracts around the model and chain effects, not just the follow-up of his own run.

---

Why assign an operational owner to each deployed model? <!--anki:3466306535656434323732623435323938396466616266343034313862323539-->
?
It takes someone to **interpret the alerts, decide on a suspension, and maintain the data and thresholds.** An ownerless model can continue to produce decisions after its original team disappears.

Document contacts, service contract, dependencies and withdrawal procedure. The business owner and operator may be different; explain their responsibilities. A model topic is only useful if it still matches the active deployment.

---

Why is the lack of reliable labels a MLOps debt? <!--anki:6232613363623536353139393465383438353034636364373861383336306234-->
?
Without observable results, it becomes difficult to **measure regressions and choose a retraining**. Adding technical monitoring does not replace this measurement.

Define how the label will be obtained, linked to the prediction and corrected, with time and cost. Provide sampling when exhaustive annotation is impossible. Confidence scores do not become a field truth because labels are missing.

---

## Scenarios

Scenario: a LLM application in production gives different answers from two months ago, and no one knows what has changed. What's missing, and how do you fix it? <!--anki:75382a6c5a6c4a356639-->
?
1. **Check**: without full versioning, we can neither explain nor go back
2. **Version all four bricks**: code, prompts and generation configuration, model or adapt, RAG index
3. **Pinch** the exact version of the model, including API side, which evolves without commit at home ([[113-monitoring-drift-feedback|Updates from the provider]])
4. **Trace** the version used in each query ([[91-langfuse-observability|traces]])
5. **Link** version and quality by evals replayed with each change ([[112-model-cicd|CI/CD]])

**Trap**: Version the code alone and consider the prompt as secondary configuration.

---

Scenario: three teams each deploy their models, with their conventions, and no one knows who is responsible for what in production. What do you put in place as a lead? <!--anki:782852524b5072625831-->
?
1. **A single registry** for models and adaptors, with metadata, steps and lineage
2. **Common versioning conventions**, applied by the IC rather than discipline
3. **An owner named** by model in production, responsible for its quality and its withdrawal
4. **Aligned environments**: same pipelines in dev, pre-production and production, data near the real
5. **Required evaluation gates** before each promotion

**Trap**: Impose a tool before you have responsibilities and agreements.

---

## Sources

- [Google Cloud — MLOps, Continuous Delivery and Pipelines](https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning)
- [Langfuse — traces, assessments and prompt management](https://langfuse.com/docs)

- [MLflow — versions, alias and registry governance](https://mlflow.org/docs/latest/ml/model-registry/workflow/)
- [Google Research — Hidden Technical Debt in Machine Learning Systems](https://research.google/pubs/hidden-technical-debt-in-machine-learning-systems/)

## Connections
- [[112-model-cicd|CI/CD models]] — the pipeline that applies these standards
- [[113-monitoring-drift-feedback|Monitoring & drift]] — Post-Deployment Loop
- [[10-images-models-weights|Images & poids]] — model registry vs container registry
- [[51-fine-tuning-adaptation|Fine-tuning]] — adapt them as artifacts
- [[91-langfuse-observability|Langfuse]] — Quick Versions
- [[114-reproducibility-variance|Reproducibility & variance]] — reproducibility in detail
- [[115-agent-platforms-governance|— Agent Platforms Architecture & Governance]] — agent registry and life cycle
- [[105-agentic-ai-devsecops|DevSecOps for Agentic AI]] — AI-BOM and Supply Chain Models
- [[153-data-flywheel-versioning|Data flywheel & versioning]] — versioner and loop on data
- [[147-ai-technical-leadership|Technical Leadership]] — role of senior
- [[150-016-data-observability-lineage|Observability, lineage & data exploitation]] — trace data to model versions
- [[117-continuous-training-pipelines|Training Pipelines & Register]] — alias champion, experience follow-up and continuous training
- [[118-ml-artifacts-registry-releases|Artifacts, registry and releases ML]] — production contracts and verifications
- [[00-moc-ai-engineering|MOC AI Engineering]]
