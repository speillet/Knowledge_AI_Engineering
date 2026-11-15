# Local workshop — Decide from IA metrics

Four exercises on fictitious data to go from the recall of a formula to its consequence: prevalence, decision with review, choice of model under constraints and quality of the complete document. The workshop uses only the standard library of Python 3.9 or newer, without API or GPU.

## Procedure

From the repository root, view the statements:

```bash
python3 examples/ai-decisions/decisions_workshop.py --questions
```

Solve on paper by giving formula, units and assumptions. Display then the controlled results:

```bash
python3 examples/ai-decisions/decisions_workshop.py
```

| Exercice | Result to explain | Related files |
| --- | --- | --- |
| Prevalence | 94.7% accuracy drops to 15.4% when positives change from 50% to 1%, with TPR and FPR assumed constant | [Validation ML](../../170-classical-ml/172-ml-validation-metrics.md) |
| Revue humaine | For p = 0.02; 0.10; 0.60; 0.99, the lower cost decisions are negative, reviewed, reviewed, positive | [Calibration and abstention](../../170-classical-ml/173-calibration-uncertainty-abstention.md) |
| Models | B dominates A; C is eliminated by latency. The cost of B is about 0.00842 € by success | [Choice of models](../../140-system-design-product/146-model-selection.md) |
| Documents | Two batches at 99% accuracy per field have 80% and 99% correct complete documents respectively | [Vision-langage](../../160-multimodal-edge/161-vision-language-models.md) |

## Variants to check the transfer

1. **Prevalence**: Replace 1% with 2%. The 180 true positives and 490 false positives give about 26.9% accuracy. Explain why the recall remains constant only in the exercise model.
2. **Review**: If it costs 5 units, with the other assumptions unchanged, it is never the lower cost decision: the best cost between positive and negative does not exceed 3.6. If it can be wrong, add its expected error cost before deciding.
3. **Models**: Release the latency cap to 1.5 s. B and C become undominated: C gains in success, B in cost and latency. Additional product arbitrage is required.
4. **Documents**: Asking only ten correct independent fields each to 99% gives `0,99^10 ≈ 90,4 %` complete success. Explain why this calculation does not necessarily describe the two deterministic batches of the workshop.

**Proof of control**: produce a short decision with the data used, the denominator, an assumption on which the conclusion depends and what should be measured on a real service.

## Limites

The costs, probabilities and performance are fictitious and the checks are based on these examples. The workshop does not estimate uncertainty, does not validate the calibration of a model and does not measure the quality of the human review. The two documentary batches show precisely why a score per field is not enough to infer complete success.
