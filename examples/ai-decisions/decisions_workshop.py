#!/usr/bin/env python3
"""Four AI decision exercises, with fictitious data and standard library.

python3 examples/ai-decisions/decisions_workshop.py --questions
python3 examples/ai-decisions/decisions_workshop.py

The assertions check the stated educational results. No model is trained
and no production measurements are made.
"""

import argparse
import math

QUESTIONS = """1. Prevalence: on 10,000 cases, TPR = 90% and FPR = 5%, assumed constant.
Calculate true positives (TP), false positives (FP) and precision with 50% then 1% of positives.

2. Decision: calibrated probabilities p = 0.02; 0.10; 0.60; 0.99.
A false positive costs 4 units, a false negative 36, the correct decisions
are free. A perfect review costs 1 unit, with sufficient capacity.
For each p, choose positive, negative or reviewed according to the expected cost.

3. Models: same test and load, measurements treated as accurate.
A: success 94%, 0.010 €/request, p95 0.8 s.
B: success 95%, 0.008 €/request, p95 0.7 s.
C: success 97%, 0.012 €/request, p95 1.4 s.
Requirements: success >= 94% and p95 <= 1 s.
Choose among eligible candidates, then calculate the cost per success.

4. Documents: 100 documents with 20 fields each, with exactly 20 errors.
Dispersed batch: one mistake in each of the first twenty documents.
Concentrated batch: twenty errors in the first document only.
Calculate field accuracy and document success in each batch.
Compare to the hypothesis of twenty independent fields, each correct to 99%.
"""


def precision_by_prevalence():
    for prevalence, expected in ((0.50, (4500, 250)), (0.01, (90, 495))):
        true_positive = 10_000 * prevalence * 0.90
        false_positive = 10_000 * (1 - prevalence) * 0.05
        assert (true_positive, false_positive) == expected
        precision = true_positive / (true_positive + false_positive)
        print(
            f"  Prevalence {prevalence:.0%}: TP={true_positive:.0f}, "
            f"FP={false_positive:.0f}, precision={precision:.2%}"
        )
    print("  Recall remains 90% under these assumptions; precision changes.")


def decisions_with_review():
    expected = ("negative", "review", "review", "positive")
    for p, expected_decision in zip((0.02, 0.10, 0.60, 0.99), expected, strict=True):
        costs = {"positive": (1 - p) * 4, "negative": p * 36, "review": 1.0}
        decision = min(costs, key=costs.get)
        assert decision == expected_decision
        print(f"  p={p:.2f} : {decision}, expected cost={costs[decision]:.2f}")
    print("  These decisions assume calibrated probabilities and perfect review.")


def constrained_selection():
    # name, success rate, euros per request, p95 in seconds
    candidates = (
        ("A", 0.94, 0.010, 0.8),
        ("B", 0.95, 0.008, 0.7),
        ("C", 0.97, 0.012, 1.4),
    )
    eligible = [m for m in candidates if m[1] >= 0.94 and m[3] <= 1.0]

    def dominates(a, b):
        weakly_better = a[1] >= b[1] and a[2] <= b[2] and a[3] <= b[3]
        strictly_better = a[1] > b[1] or a[2] < b[2] or a[3] < b[3]
        return weakly_better and strictly_better

    frontier = [m for m in eligible if not any(dominates(other, m) for other in eligible)]
    assert [m[0] for m in eligible] == ["A", "B"]
    assert [m[0] for m in frontier] == ["B"]
    winner = frontier[0]
    cost_per_success = winner[2] / winner[1]
    assert math.isclose(cost_per_success, 0.008421052631578947)
    print(f"  eligible: A, B; Pareto front: {winner[0]}")
    print(f"  B : {cost_per_success:.5f} € per success, against {candidates[0][2] / candidates[0][1]:.5f} € for A")
    print("  The report divides the total cost between successes; it does not simulate retries.")


def document_quality():
    dispersed = [[True] * 20 for _ in range(100)]
    concentrated = [[True] * 20 for _ in range(100)]
    for document in dispersed[:20]:
        document[0] = False
    concentrated[0] = [False] * 20
    for name, documents, expected_success in (
        ("Dispersed", dispersed, 0.80),
        ("concentrated", concentrated, 0.99),
    ):
        field_accuracy = sum(sum(doc) for doc in documents) / 2000
        document_success = sum(all(doc) for doc in documents) / len(documents)
        assert math.isclose(field_accuracy, 0.99)
        assert math.isclose(document_success, expected_success)
        print(f"  batch {name} : fields={field_accuracy:.1%}, complete documents={document_success:.1%}")
    independent_success = 0.99**20
    assert math.isclose(independent_success, 0.8179069375972308)
    print(f"  Independent hypothesis: {independent_success:.1%} Complete Documents")
    print("  The same accuracy per field can hide different complete-document success rates.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--questions", action="store_true", help="display statements without results")
    args = parser.parse_args()
    print(QUESTIONS)
    if args.questions:
        return
    for title, exercise in (
        ("1. Precision and prevalence", precision_by_prevalence),
        ("2. Decision with review", decisions_with_review),
        ("3. Choice under constraints", constrained_selection),
        ("4. Quality of the complete document", document_quality),
    ):
        print(title)
        exercise()
        print()
    print("Four verified exercises. Change an assumption to check your understanding.")


if __name__ == "__main__":
    main()
