# Workshop: make decisions from AI metrics

Four exercises connect a calculation to a decision: precision under changing prevalence, human review, model selection under constraints and complete-document quality. They use synthetic data and the Python 3.10+ standard library, with no API key or GPU.

Read [validation and metrics](../../170-classical-ml/172-ml-validation-metrics.md) first. The [first learning session](../../START_HERE.md) guides you through model selection.

## Run

From the repository root, display the questions:

```bash
python3 examples/ai-decisions/decisions_workshop.py --questions
```

Solve on paper, stating formulas, units and assumptions. Then display the checked results:

```bash
python3 examples/ai-decisions/decisions_workshop.py
```

| Exercise | Result to explain | Related topic |
| --- | --- | --- |
| Prevalence | Precision drops from 94.7% to 15.4% when prevalence changes from 50% to 1%, assuming constant TPR and FPR | [ML validation](../../170-classical-ml/172-ml-validation-metrics.md) |
| Human review | For p = 0.02, 0.10, 0.60 and 0.99, the lowest expected-cost decisions are negative, review, review and positive | [Calibration and abstention](../../170-classical-ml/173-calibration-uncertainty-abstention.md) |
| Models | B dominates A; C fails the latency requirement. B costs approximately €0.00842 per success | [Model selection](../../140-system-design-product/146-model-selection.md) |
| Documents | Two batches with 99% field accuracy have 80% and 99% complete-document success | [Vision-language models](../../160-multimodal-edge/161-vision-language-models.md) |

## Change an assumption

1. **Prevalence**: replace 1% with 2%. With 180 true positives and 490 false positives, precision is about 26.9%. Explain why recall stays constant only under the exercise's assumptions.
2. **Review**: raise its cost to 5 units. Under the other assumptions, review is never cheapest: the best of the positive and negative decisions costs at most 3.6. If reviewers can make mistakes, include that expected error cost.
3. **Models**: raise the latency limit to 1.5 s. B and C are both undominated: C has higher success, while B is cheaper and faster. State a product criterion that would decide between them.
4. **Documents**: ten independent fields, each correct with probability 99%, give `0.99^10 ≈ 90.4%` complete success. Explain why independence does not describe the two deterministic batches in the workshop.

## Deliverable and limits

Write a short decision with the data, denominator, a crucial assumption and what you would measure on a real service. You should be able to explain why changing an assumption changes the decision.

The costs, probabilities and performance are synthetic. The workshop does not estimate uncertainty, validate calibration or measure human-review quality. Field accuracy alone does not establish complete-document success.

[All workshops](../README.md)
