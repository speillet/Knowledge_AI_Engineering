# New skills IA — 8 October 2026

## Perimeter

This extension adds **five cards of 14 cards**, or **70 cards**, with **15 scenarios, 10 distinctions and 8 calculations**. It complements the existing 1,723 cards with useful prediction and decision skills depending on the AI engineer position targeted.

The review of the themes and related topics made it possible to distinguish what was missing from what was already introduced: the temporal validation, the metrics of retrieval and the absence of causality of the importances were mentioned; the approaches specific to the five fields below did not have a dedicated topic.

## Contributions and priorities

| Topic | Contribution in relation to existing content | When to work |
| --- | --- | --- |
| [174 — Recommandation & learning to rank](../../170-classical-ml/174-recommendation-ranking.md) | Product objective, candidates, implicit labels, negatives, exposure, new users and diversity; extends embeddings and RAG metrics | Custom search, suggestions, catalog, content or products |
| [175 — Time forecast](../../170-classical-ml/175-time-series-forecasting.md) | Horizons, backtesting, seasonal baseline, ETS/ARIMA, recursive forecasts, future variables, MASE, quantiles and reconciliation; extends the temporal availability of data | Demand, capacity, volumes or deadlines to anticipate |
| [176 — Detection of anomalies](../../170-classical-ml/176-anomaly-detection.md) | Detection without complete labels, methods, operational thresholds, review load and measurement by incident; extends rare class monitoring and metrics | Incidents, quality, unusual changes or investigation |
| [177 — Explainability](../../170-classical-ml/177-model-explainability.md) | Permutations, correlations, SHAP and its units, PDP/ICE, feasible actions and justifications fidelity; develops the limits of predictive importance | Diagnosing, reviewing a model or explaining it to its users |
| [178 — Causal Inference](../../170-classical-ml/178-causal-inference-decisions.md) | Targeted effects, graphs, selection, identification, overlap, propensity, differences in differences and uplift; extends A/B tests | Choose an action and measure what it really changes |

Start with the 171 to 173 files on choice, validation and calibration. Then choose a branch according to the problem encountered. The five domains do not constitute a list of tools to know uniformly: a research, platform and forecasting station does not require the same depth.

## Associated exercises

### Recommandation

Build a contextualized popularity baseline and a content search on a catalogue of articles. Reserve an evaluation period and freeze eligible candidates. Compare candidate recall, nDCG, redundancy and results on new items.

**Livable**: a table distinguishing search failure from poor ranking, and then a diversity test. If the data does not contain exposure logs, report it; do not present unclicked items as certain rejections. A simulation does not demonstrate the actual gain from users.

### Temporal forecast

Provide a daily volume of one day and four weeks with a seasonal baseline and a candidate model. Simulate multiple decision dates, using only the variables then available. Report DFA, baseline comparison and coverage of intervals by horizon.

**Livable**: a reproducible backtest, with a hand-reconstructed historical line and an analysis of a break period. Demonstrate that true intermediate values are not used in a recursive prediction.

### Detection of anomalies

Compare a contextual rule and a detector on annotated events or a simulation with known incidents. Change the threshold with a daily limit of treatable records. Measure incidents found, delay and false alarms; distinguish injected cases from actual incidents.

**Livable**: a curve linking threshold, load and utility. If the labels are incomplete, provide a review of non-alerts and explain what remains impossible to estimate. Also check the behavior after a legitimate change of reference.

### Explainability

On a tabular model, introduce two highly correlated variables. Compare individual permutation, group permutation, and retraining without the group. Produce a local explanation with explicit reference and unity.

**Deliverable**: a note explaining why the results differ, with numerical reconstruction of the prediction. Check that no attribution is presented as proof of the effect of an actual action.

### Causality

Simulate an aid whose allocation depends on the difficulty of the files, with a known effect in the generator. Compare gross difference and adjustment on observed factors. Add an unobserved common factor or remove the recovery to expose the limits.

**Livable**: graph, target population, assumptions, estimation and sensitivity analysis. A method that finds the effect in a simulation does not prove that the assumptions will be true in real data.

## Sources and Scope

The primary references are in each file: Google and Microsoft Research for the recommendation, the authors of *Forecasting: Principles and Practice*, scikit-learn and SHAP documentation, scientific work on anomalies and explanations, Hernán & Robins and PyWhy for causality. The calculations and scenarios are educational; they are not the results of an deployed system.

The 170 section expands to prediction and decision. Its historical title is retained to keep existing Anki subpackages stable. The README and MOC present the new topics; a path allows to choose the branch according to the task. This extension does not replace a complete course of optimization, causality or advanced forecasting. It provides benchmarks to design an experiment, detect a trap and choose a useful deepening.

## Validation

The Vault changes from **121 cards and 1,723 cards** to **126 cards and 1,793 cards**, in 17 sections. It now has **284 situationalized and 132 cards of distinction**.

- **Conservation**: Comparison to the `61d13ad` commit; the old 1,723 questions, answers and identifiers are strictly identical. Only links are added to existing topics.
- **Structure and navigation**: lint without error or warning, Obsidian/Anki equivalent reading, reciprocal connections, synchronized catalogs and local links of the balance sheet valid.
- **Tests**: Existing 40 tests pass; `git diff --check` reports no anomalies.
- **Calculations**: The eight digital maps are verified in Python, with their assumptions: nDCG, MASE, pinball, alerts, permutation, log-odds, differences in differences and incremental gain.
- **Export**: `dist/ai-engineering.apkg` regenerated; valid archive and SQLite database, 1,793 active cards with fields entered, 30 cards removed suspended. Old GUIDs and subpacket IDs are retained. The artifact remains excluded from Git.

The proposed exercises have not been executed as complete projects. The verification covers the added content, its calculations and its integration into the vault; no personal Anki library or production infrastructure has been modified.
