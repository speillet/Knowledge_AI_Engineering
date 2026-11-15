# Model CI/CD — Flashcards
Tags: #flashcards #ai-engineering #mlops #cicd #llm
<!-- summary: evals statistics and deterministic tests, eval gates (threshold example), deployed artifact, blue/green and canary, shadow deployment, rollback, GitOps, tests of a LLM app, CI prompts, complete pipeline, rollback after schema migration, continuous delivery or deployment, smoke training, same promoted artifact, canary with late label. -->


What does the CI/CD of a LLM app bring in addition to the classic CI/CD? <!--anki:4a6b3758755748575f5d-->
?
**eval gates on behavior**, in addition to code tests, contracts and integration. The opposition is not "deterministic tests, statistical tests": both can include hazard, and a business invariant can be strict.

Example: Block any unauthorized action, while comparing the summary quality on a sample with uncertainty interval. An average gain does not compensate for the violation of the first criterion.

Set games, versions, thresholds, and repeat protocol before testing ([[114-reproducibility-variance|variance]]). Evaluate critical segments and measure reviewer coverage/failures; a gate without representative cases can pass a regression.

---

What is an eval gate? <!--anki:6a4b402e5157293d4533-->
?
A **eval gate** decides whether a candidate can take a step, according to criteria defined before the test. It eventually combines absolute constraints, comparison to the reference and cost or latency budgets.
```yaml
# Illustrative policy, to implement and to version.
gate:
  dataset: support-validation@v14
  reference: release-r16
  exactitude_min: 0.90
  perte_max_points: 0.02
  action_non_autorisee_observee: 0
```
Compare on the same cases and examine uncertainty, segments and coverage. An economy may justify a pre-specified margin of non-inferiority; any version does not have to improve each score. Zero observed violation blocks some critical cases without demonstrating zero risk. Keep report, assessor and decision with release.

---

What is the deployed artifact of a LLM app? <!--anki:695e35574c713148795a-->
?
The release unit links **application, model, configuration and data dependencies**: image by digest, weight or supplier reference, tokenizer and adaption, possible prompt, tool contracts and indexes or compatible features.

For a tabular model, include preprocessing, input order and semantics, calibrator, classes, and decision policy. A weight-only version does not identify this service. Have the combination tested and then promote the same objects. A manifest describes these links; it does not replace their availability, access controls, or a necessary migration. Check the result actually served after loading, not just the published manifest.

---

Do not confuse: blue/green and canary for a model? <!--anki:4c433e55363b3a3f6e2a-->
?
- **Blue/green**: two environments; traffic switches from old to new after validation. The return is fast if the old remains available and compatible.
- **Canary**: some traffic uses the new version; it is increased if quality, errors, cost and [[64-inference-metrics-slo|SLO]] remain acceptable.

The first facilitates a global toggle, the second limits the initial exposure. None guarantees an instantaneous rollback of data or external actions. Provide compatibility of diagrams, stop criteria and observation time.

---

What is shadow deployment? <!--anki:644e744c303250597258-->
?
In **shadow deployment**, a new version receives a copy of the traffic but its output is not presented to users. This allows to compare quality, latency and formats on real entries.

Disable or simulate external effects and verify rights, privacy and capacity: the absence of display does not remove any risk. The additional cost depends on the traffic copied and the models; it does not necessarily double the invoice. This method does not observe the effect of the new response on user behavior ([[97-evals-online-ab-testing|shadow testing]]).

---

How does the rollback of a model work? <!--anki:7a484c43315e344e4931-->
?
We go back to the **previous version** of the model, to adapt it or to prompt, for example by relocating a label in the registry.

Requirements: Strict versioning, old version **still available** (a API model may have been removed), and compatible **output schemes**, otherwise downstream systems break. A rollback is **tested** before it is needed.

After toggling, trace the version actually served: caches and replicas can keep the old target of the label. Checking a known business case and current queues; changing a reference in the registry is not proof of recovery.

---

What is GitOps applied to models? <!--anki:423a6e24507a51415361-->
?
The **GitOps** declares in Git a desired state, then a controller compares it to the executed state and applies the allowed changes. Version of the service, model references and configuration can thus go through review.

References must designate controlled and immutable artifacts; a rewritten path behind the same name breaks reproducibility. A `git revert` creates a new return intent, but does not guarantee schema compatibility, data restoration, or business effects cancellation. Define the handling of emergency responses and discrepancies. Test convergence and version actually loaded; the presence of an operator does not prove successful deployment.

---

What types of tests for a LLM app in CI? <!--anki:507d662a4f776c345758-->
?
Combine **unit tests**, contracts, integrations and behavior assessments. The first ones isolate parsing, transformations and authorizations; integrations check boundaries; evals measure the task on representative cases.

For the tabular ML, test also preprocessing and model reloaded from the package intended for the serving. The mocks reduce cost and variance but do not verify the actual provider or the dependencies of the final image. Provide some limited real integrations when necessary, negative cases and resume tests. An assertion "exit not empty" or "HTTP 200" does not validate nor amount, nor proof.

---

What steps make up a CI/CD pipeline of LLM application? <!--anki:633b61656533535d3e3f-->
?
```text
PR → tests + evals → build image → push registry
→ deploy canary → metric/SLO OK → promotion
```

Each passage must have a criterion: valid deterministic tests, thresholds of evals reached, artifact identified, then observation of the canary. Keep the manifest linking code, model, prompt and data to this validation. A regression of quality or SLO blocks the promotion and can trigger the rollback; a simple HTTP response 200 is not enough.

For a regularly retrained model, we separate two chains: the **CI of the pipeline**, which tests the transformations and launches a smoke drive on a few thousand lines, and the **continuous drive**, which produces the candidates ([[117-continuous-training-pipelines|Drive Pipelines]]).

---

Why test an AI rollback after a schema migration rather than assume that it will be enough to restore the image? <!--anki:6663393966663531373731653432323139326231386566643565363066333062-->
?
The **Old Application** can no longer understand the state, the categories or data produced by the new version. Restoring your image can make the incident worse.

Deploy compatible drives first, migrate gradually and then change producers according to an expansion and removal strategy. Keep a compatibility window or a documented restore path. Test rollback with runs created after migration. Include model, prompt, index and parser: their consistency counts as much as that of the code.

---

Do not confuse: Continuous delivery and continuous model deployment? <!--anki:3562653164393336616537353436616162323764373235623536663761363134-->
?
**Continuous Delivery** maintains a version ready to be deployed after the planned checks, possibly with a final human decision. The **Continuous Deployment** also automates this last transition when its conditions are met.

Both require identified artifacts, proof of validation and return procedure. For a model with sensitive effects or late labels, manual promotion can be a mastering choice, without giving up testing or preparation automation. Clearly describe where the automaton stops: the phrase "CI/CD pipeline" does not specify who authorizes commissioning or under what evidence.

---

What does a smoke drive in the IC of an ML pipeline check? <!--anki:3666383335663963356230343435363939616638333339373930356438363764-->
?
A **smoke training** quickly executes the complete path on a small controlled game: ingestion, transformations, fit, prediction and publication of a test artifact. It reveals in particular broken imports, incompatible types and missing outputs.

Its small size does not make it possible to assert a generalization quality or a production capacity. Use cases covering categories, missing values and expected errors, then reserve other tests for performance and statistical validation. Check that the test data does not reach the production register. A fast CI validates the operation of the recipe; the complete candidate passes his own gates.

---

Why promote the same tested artifact rather than retrain to each environment? <!--anki:6536393566663039346134383433343338373761393062333930316163376632-->
?
Retraining in staging and then in production can produce **two different models**, even with the same code. The evidence obtained on the former no longer automatically applies to the latter.

Build an identified candidate, validate its packet, and then promote these same objects with a controlled environment configuration. Separate secrets without silently changing preprocessing or business parameters. If an adaptation requires a new calculation, create a new version and validate it. Save fingerprints and version actually loaded; a common release name or an identical recipe does not demonstrate the identity of the weights and dependencies delivered.

---

Why doesn't a technically sound canary still validate the quality of a late-label model? <!--anki:3135363933376136353963343430656639383631363035303637623639356631-->
?
The **canary** quickly gives service signals: errors, latency, formats, volumes and cost. If the target is a thirty-day exit, these first minutes do not yet tell if the predictions are correct.

Define immediate safeguards and a separate criterion based on mature cohorts. Keep assignment, version and decisions to reconcile future results. A partial promotion may remain under observation depending on the risk; do not replace the exit with a proxy without verifying its scope. Successful transport and the absence of visible incidents do not prove calibration or sustainable business gain.

---

Why neutralize the business effects of a model shadow deployment? <!--anki:3039386261623230326530373465626362373232353531646665663633353561-->
?
The shadow must allow **comparison on actual traffic without doubling the executed decisions**. A second refund or a second notification would turn the test into a production action.

Send entries to an evaluation path with controlled destinations, then compare results and latency. Check quotas, sensitive data and added load. A "shadow" label in the configuration is not enough if the tools retain their write accesses.

---

How to prevent an old evaluation result from allowing a modified release since? <!--anki:6438363066366237643932363431313462336133643131353534393436363636-->
?
Link the approval to **the exact footprint of the evaluated manifest**: model, code, reference data, thresholds and configuration. Any relevant changes invalid or renews this validation.

Check this link at the time of promotion, not just in the initial CI. A green badge associated with a mutable branch does not prove that the deployed artifact has passed the tests. Keep the proof and its limits with the release.

---

## Scenarios

Scenario: a modification of a line of the system prompt goes into production without review, and the quality drops for two days before we notice. What do you put in place? <!--anki:6e6a4676534d666b7c3f-->
?
1. **Treat the prompt as code**: versioned in Git, replayed in pull request
2. **Eval gate**: replay of the golden dataset with each modification, blocking if regression ([[94-evals-methodology|evals]])
3. **Traceability**: the version of the prompt appears in the tracks, to know what was running ([[91-langfuse-observability|traces]])
4. **Progressive Deployment**: canary with comparison of metrics before promotion
5. **Fast Rollback**: Go back to the previous version without redeploying the entire application

**Pip**: change the prompts in a production interface, without history or review.

---

Scenario: you need to deploy a new model version on a critical service, without a maintenance window. What strategy do you choose? <!--anki:6f55366b2969522d7352-->
?
1. **Validate offline**: non-regression checks and contract tests on structured outputs
2. **Shadow** first if budget allows: real traffic duplicated, no response shown to user
3. **Canary** then: small percentage, monitoring of SLO, errors and quality scores
4. **Advancely defined promotion and rollback criteria**, not decided in an emergency
5. **Full versioned artifact**: image, model reference, prompts and configuration

**Strap**: an instant blue/green on a model whose latency and output format have not been verified under real-world conditions.

---

## Sources

- [Google SRE — canary and release control](https://sre.google/workbook/canarying-releases/)
- [Google Cloud — CI/CD/CT and validation of ML pipelines](https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning)

## Connections
- [[111-mlops-llmops-fundamentals|Basic MLOps]] — versioning & registry
- [[92-chainforge-evals-prompts|Evals]] — the content of the gates
- [[64-inference-metrics-slo|Metrics & SLO]] — the judge of the canary
- [[83-gateway-ingress|Ingress & gateway]] — traffic splitting
- [[12-kubernetes-gpu-inference|Kubernetes GPU]] — Deployment Target
- [[114-reproducibility-variance|Reproducibility & variance]] — test variable outputs
- [[93-monitoring-inference|Monitoring of inference]] — controls before sending traffic
- [[115-agent-platforms-governance|— Agent Platforms Architecture & Governance]] — evals and agent optimization loop
- [[105-agentic-ai-devsecops|DevSecOps for Agentic AI]] — security checks and security eval gate
- [[94-evals-methodology|Evaluation methodology]] — build gates
- [[97-evals-online-ab-testing|Evals online & A/B testing]] — canary vs A/B
- [[106-coding-agent-security|Security of Code Agents]] — risks specific to code agents
- [[113-monitoring-drift-feedback|Monitoring & drift]] — quality in production and feedback loop
- [[13-production-prompts|Prompt in production]] — structure, versioning and portability of prompts
- [[116-ai-sre-incidents-capacity|SRE: incidents & capacity of AI services]] — rollback and artifact compatibility
- [[117-continuous-training-pipelines|Training Pipelines & Continuous Training]] — pipeline that produces candidates to promote
- [[118-ml-artifacts-registry-releases|Artifacts, registry and releases ML]] — production contracts and verifications
- [[119-prediction-contracts-features-batch|Prediction contracts, features and batch]] — production contracts and verifications
- [[00-moc-ai-engineering|MOC AI Engineering]]
