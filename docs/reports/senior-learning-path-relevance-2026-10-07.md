# Relevance of the course engineer IA senior — 7 October 2026

## Diagnostic

Valult is **relevant for a LLM-oriented applied AI engineer, agents and production**. Its strengths are assessments, security, inference, data and system design. The ML foundations and distributed systems added on the 6 October improve its balance. It does not in itself constitute a complete course of ML research, vision or robotics, nor a proof of seniority.

The review covers the mapping of **117 cards and 1,663 initial cards**, questions and themes, then a focused in-depth reading of the cards related to the shortcomings and corrections below. The structural control is exhaustive; the factual verification is targeted. This intervention does not pretend to recheck all product versions and all regulatory texts of the vault.

The main imbalance is educational: the tools and infrastructures are very detailed, while some skills necessary to justify a decision were only mentioned. For example, calibration appears in several topics, but without complete measurement and abstention; the accumulation of gradients appears in the distributed, without diagnosis of normalization by token.

## Priorities for review

This grid is an editorial recommendation for this vault, not a universal recruitment scale.

| Bloc existant | Relevance to the Senior Base | Proposed priority |
| --- | --- | --- |
| ML choice, validation, contracts and temporality of data | Essential to avoid an unnecessary solution or a misleading score | To be mastered before complexifying an architecture |
| Evals, error analysis, security, costs and system design | Very strong: allows you to decide and deliver | Review with real cases and quantified criteria |
| RAG, tools and workflows | Very strong for LLM products | Compare systematically to a simpler baseline |
| Inference, containers and infrastructure | Useful base; depth according to the role | Deepen GPU and Kubernetes for a platform role; HPC according to context |
| topics centered on Cognee, ChainForge or a framework | Useful for the projects concerned; less priority than the mechanisms | Read them with a concrete need, keep the principles transferable |
| Multi-agent, Agentic RL, Advanced Distributed Training | High Complexity Specializations | Deepen them after the baselines, according to the responsibilities targeted |
| Technical Leadership | Necessary but insufficient to remember | Demonstrate decisions, transmission and operating responsibility |

No existing cards are removed: the specialized cards remain contextually useful and review progress must be preserved. The work order changes more than the scope of the vault.

## Enrichments achieved

| Contenu | Ajout | Competence worked |
| --- | ---: | --- |
| [Training Optimization and Diagnostics](../../50-fine-tuning/56-training-optimization-diagnostics.md) | 14 cards | Distinguish loss and value, diagnose gradients, accumulation and numerical accuracy |
| [Calibration, uncertainty and abstention](../../170-classical-ml/173-calibration-uncertainty-abstention.md) | 14 cards | Validate a trust, choose a cover and encrypt the human review |
| [Statistics to decide](../../90-observability-evals/99-statistics-experimental-decisions.md) | 14 cards | Interpret a gain, control the selection and respect the independent unit |
| [SRE, Incidents and Capacity](../../110-mlops-cicd/116-ai-sre-incidents-capacity.md) | 14 cards | Exploit the SLO, master the queues and check the replays |
| [Technical Leadership](../../140-system-design-product/147-ai-technical-leadership.md) | 4 cards | Mentoring, design review, debt and transfer of operations |
| **Total** | **60 cards** | **13 scenarios and 9 distinctions included** |

Primary sources are listed in the topics: PyTorch documentation, scikit-learn, SciPy, calibration work and compliant prediction, NIST, ASA, Microsoft Research, Google SRE and AWS. The examples and steps are educational applications to AI systems, not experimental results obtained on a particular deployment.

**Twelve existing answers are corrected or expanded**, without changing their questions or identifiers:

- Model size and reasoning effort: a quality gain must be measured, it is not automatic.
- Calibration and hallucinations: distinguish probabilities from tokens, truth from assertions and detection signals.
- A/B testing: choose the randomization unit, distinguish proxy and useful result, do not assume a universal duration of novelty.
- Resilience: a withdrawal without RAG must respect the product contract; queues and quotas must remain under control.
- QLoRA: Distinguish between gross weight and total memory instead of guaranteeing that a model size fits on a given GPU.
- Seniority: Explicit end-to-end responsibility and team autonomy.

## Workshops with evidence of mastery

Use a red thread: **a document sorting and retrieval service, with human review and optional documentary assistant**. Work on suitable public or synthetic data, with groups and a final test reserved. The business thresholds are to be set before testing; illustrative figures of the maps are not universal requirements.

### 1. Justify the choice of the model

Compare a rule, ML baseline, and LLM solution if warranted. Define independent unit, error costs, master metric, and minimal useful effect. Produce a report with matched differences, uncertainty, errors by segment, latency, and total cost.

**Expected proof**: another person can reproduce the split and understand why the gain is enough, not enough or remains uncertain. No choice depends on repeated tests on the final test.

### 2. Automate difficult cases without masking

On a classifier, compare raw and calibrated probabilities with separate sets. Measure reliability curve, Brier score, risk-coverage and review load. Simulate a change in population or prevalence and examine segments.

**Expected proof**: the threshold meets the stated constraints on an independent game; the report counts abstentions, human capacity and remaining errors. Any validation limit is explicit.

### 3. Diagnose learning

If the adaptation is part of the intended role, train a small model on CPU or a model adapted to the available resources. Verify that it memorizes a microlot, then compare train and validation. Introduce a masking or normalization error and find its cause. Compare accumulation and physical batch on a controlled case.

**Expected proof**: Gradients and weight changes are observed, the failure is isolated by an experiment and the fix is checked. The only loss is not the result.

### 4. Operate a service during an outage

Serve the pipeline with limited instrumentation and input. Inject timeout, 429, unavailability of retrieval, and dependency saturation. Measure delay, queue, error budget consumption, and rescue behavior. Run rollback and restore with simulated business effects.

**Expected Proof**: Each failure triggers a predicted behavior; no effect is duplicated in the tested scenarios; measured RTO/RPO and capacity limits are documented. A local success does not prove guarantees of a real distributed deployment.

### 5. Submit and defend the decision

Write an ADR comparing the options and a runbook usable by a colleague. Run a delivery or diagnosis without much oral instructions. Write a postmortem of the exercise and verify at least one corrective action by replaying the failure.

**Expected proof**: the co-worker finds the decision, its reason and the conditions for reconsideration; the corrections reduce an observed problem. This is a proof of collective autonomy that recitation alone does not provide.

## Limits and continuation of the course

For a more training or research-oriented position, complete optimization mathematics, linear algebra, non-LLM architectures and critical reading of articles with reproductions as needed. For a platform position, deepen networking, storage, profiling and exploitation GPU in a real environment. The new statistics topic introduces causality; it does not constitute a full course of causal inference.

## Validation

The value increases to **121 cards, 1,723 cards and 17 sections**, of which **269 sets the scene and 122 distinctions**. The four cards are integrated into the catalogues and connected in both directions. The MOC offers a practical path associated with these workshops.

- **Lint**: zero error and zero warning, with equivalent reading in Obsidian and Anki.
- **Catalogs**: `sync_catalog.py --check` valid; `git diff --check` without anomaly.
- **Existing Tests**: Successful 40, with repository dependencies available in `/tmp/knowledge-flashcards-deps`.
- **Conservation**: Compared to `HEAD`; the old 1,663 GUID and all their questions are the same. Twelve answers change and 60 new cards receive a separate ID.
- **Calculations**: effective batch, Brier, accuracy, human load, binomial bound, multiple comparisons, error budget, burn rate, and queue growth checked in Python.
- **Anki**: `dist/ai-engineering.apkg` regenerated; SQLite archive and integrity valid, 1,723 active cards with answers and GUID matching the vault, 30 removed cards suspended. The package remains a local artifact excluded from Git.

The above workshops are offered to the learner; they were not executed as complete projects during this review. No GPU training or exercise on an external provider was performed. The retention of credentials was checked in the package; no personal Anki libraries were opened or modified.
