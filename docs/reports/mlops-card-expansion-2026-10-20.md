# Enrichment of short cards and MLOps — 20 October 2026

This pass continues the enrichment proposed by the [Review of 17 October](relevance-review-2026-10-17.md) for sections 55 to 170. It had two objectives: no longer leave a card significantly shorter than the others, and give the MLOps a precise part on the classic ML, so far focused on applications LLM.

## Perimeter

- **Short cards**: All cards with a response of less than 45 words out of code, measured with the lint parser. They were 92, on a median of 78 words.
- **MLOps**: section 110, with a new plug and additions to the 112 and 113 plugs.
- **Online verification** of facts dated or specific to a product: stages and aliases of the MLflow registry, MLflow signatures, Kubeflow Pipelines cache, Google Cloud MLOps maturity levels, article on selective labels.

This pass does not reread cards with more than 45 words and does not recheck the other products cited by the cards.

## Short cards

89 cards have received a paragraph. In accordance with the rule of 17 October, each addition brings an element absent from the card and its neighbors:

| Contribution | Examples |
| --- | --- |
| Mechanism | copy-on-write of overlayfs, layer hidden by a `rm`, rollback of the KV cache after a rejection, states of a circuit breaker |
| Encrypted example | INT8 quantification of a weight, embedding and lm_head share in a 8B, total cost with escalations, TPOT gain according to output length |
| Decision criteria | weight in the image or separated, planned or triggered retraining, priority frequency × gravity |
| Diagnostic | `curl -N` through proxies, `OCI runtime create failed`, `kubectl get nodes -o wide` |

Neighbors were read before each addition to avoid redefining a notion. When a notion belongs to another card, the addition mobilizes it by a link, such as the sampling bias in the card on the active learning. The encrypted examples do not include the data of a neighboring computing card: the size of a 8B in Q4_K_M, an intermediate result of a calculation of the 164 card.

Three cards remain under 45 words: those that tell the story of dockershim in the card 05. The review of 17 October proposed to reduce them to the card "not to be confused"; would enrich them in the opposite direction. Their withdrawal remains to be decided.

## MLOps

The section covered the LLMOps version of the prompts, eval gates, drift of an application LLM. It lacked the life cycle of a retrained predictive model. The additions follow the convention "a notion, a reference card »: the training-serving Skew, the feature store and delayed labels remain in the file 159, the distinction drifts or incidents in the record 157.

### New 117 plug: drive pipelines, register and continuous drive

17 cards, including 3 situationalized and 1 calculation:

- 0, 1 and 2 levels of maturity MLOps, and pipeline deployed instead of model;
- planned or triggered retraining, data validation and model validation before promotion;
- MLflow experience tracking run, signature and its limitations, promotion by alias since the depreciation of internships in MLflow 2.9;
- registry alias or provider alias, caches immutable steps and entries, training window, scoring batch or online;
- Selective labels of a model that blocks transactions, and estimation of accuracy and recall before labels from calibrated probabilities.

### 113: measuring drift

Six added cards: PSI and its calculation, Kolmogorov-Smirnov threshold on 100,000 and on 50 observations, multivariate drift by domain classifier, distribution of scores and part above the threshold, and a situation on a drift dashboard ignored. The card “When to retrain” no longer asks to retrain “on signal, not on calendar”: a regular rhythm remains justified when the labels arrive.

### Data topics 112 and 113: details

GitOps shows a `InferenceService` KServe and the limit of a rewritable `storageUri`; the CI/CD pipeline separates CI from the pipeline and continuous drive; quality monitoring measures the sample by segment.

The MOC wins a five-stage **MLOps** course, from the 111 topic to the 116 topic.

## Results

| Indicator | Before | After |
| --- | ---: | ---: |
| topics | 146 | 147 |
| Cards | 2,163 | 2,186 |
| Maps under 45 words | 92 | 3 |
| Maps under 50 words | 158 | 69 |
| Average words by answer | 75.9 | 78.6 |
| Maps of the 110 section | 98 | 121 |

No response exceeds the limit of lint, 110 words off code and 140 for a situation.

## Verifications

- Lint on all the vault: no error, no warning.
- 52 successful repository tests, `scripts/requirements.txt` dependencies installed in a temporary environment.
- Anki IDs assigned to 23 new cards; README and MOC catalogs synchronized.
- Viewed sources: [Google Cloud — MLOps and Pipelines](https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning), [MLflow — Model Registry workflow](https://mlflow.org/docs/latest/ml/model-registry/workflow/), [MLflow — signatures](https://mlflow.org/docs/latest/ml/model/signatures/), [Kubeflow Pipelines — cache](https://www.kubeflow.org/docs/components/pipelines/user-guides/core-functions/caching/), [Lakkaraju et al., The Selective Labels Problem](https://pmc.ncbi.nlm.nih.gov/articles/PMC5958915).

The PSI benchmarks (0.1 and 0.25) are credit scoring conventions; the cards present them as such. The commands and metric names cited in the additions come from the tool documentation and must be rechecked at the next review of the relevant cards.

## Proposed action

- **Dockershim**: decide to remove the three historical cards from the 05 card.
- **Band from 45 to 50 words**: 66 cards, often definitions with a block of code; reread them with the same rule rather than systematically lengthening them.
- **MLOps**: A workshop executable in `examples/`, e.g. PSI, KS and performance estimation on synthetic data, would make the 113 cards verifiable by practice.
