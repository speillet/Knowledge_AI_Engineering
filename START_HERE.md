# Your first learning session

Start with one decision: **which model would you ship, and why?** This session connects three topics to a small local exercise. Allow roughly 30–45 minutes; the duration is a suggestion, not a prerequisite.

You need basic arithmetic, a terminal and Python 3.10 or newer. The exercise uses the standard library and synthetic data; no API key or GPU is required. Run commands from the repository root.

## 1. Read three topics

Read the explanations before reviewing the cards. Focus on these questions:

1. [Model selection](170-classical-ml/171-ml-model-selection.md): when would rules or classical ML be sufficient?
2. [Validation and metrics](170-classical-ml/172-ml-validation-metrics.md): what population and denominator does a metric describe?
3. [Choosing models for a product](140-system-design-product/146-model-selection.md): which constraints must a candidate meet before cost decides?

Close each topic and explain one decision in your own words. Reopen it to check assumptions you missed.

## 2. Make a decision before running the solution

Display the workshop questions:

```bash
python3 examples/ai-decisions/decisions_workshop.py --questions
```

Start with **exercise 3: models**. Candidates A, B and C were measured on the same test and load:

| Candidate | Success rate | Cost per request | p95 latency |
| --- | --- | --- | --- |
| A | 94% | €0.010 | 0.8 s |
| B | 95% | €0.008 | 0.7 s |
| C | 97% | €0.012 | 1.4 s |

The requirements are at least **94% success** and **p95 latency at most 1 s**. Treat these measurements as exact for this exercise.

Write down which candidates qualify, which one you would choose, and its cost per successful request. State what the calculation assumes. Then run the checked solutions:

```bash
python3 examples/ai-decisions/decisions_workshop.py
```

The program prints all four exercises and their results. For exercise 3, A and B qualify, B dominates A, and its cost per success is approximately **€0.00842** (`0.008 / 0.95`). C fails the latency requirement. This allocates total cost across successes; it does not model retries.

## 3. Change one constraint

Raise the latency limit to **1.5 s** and reconsider the choice on paper. B and C now trade cost and latency against success rate. Explain what additional product criterion would let you choose between them.

Before using this reasoning on a real service, specify what you would measure again: workload, uncertainty in the success rate, latency under load and total operating cost.

## 4. Check that you can move on

You are ready for the next step when you can:

- Reject a candidate that fails a requirement, even if its success rate is highest.
- Calculate cost per success with units and an explicit denominator.
- Explain why a relaxed requirement can change the set of reasonable choices.
- Name at least one limitation of the synthetic measurements.

Keep your short decision as the session's deliverable. Review a few cards from the three topics using [Anki](docs/anki.md) or [Obsidian](docs/obsidian.md); use the [learning guide](docs/learning-with-flashcards.md) to rate your answers.

## Where to go next

Continue with the other [AI decision exercises](examples/ai-decisions/README.md), choose a [learning path](00-moc-ai-engineering.md#reading-path), or browse the [topic catalog](docs/catalog.md). You do not need to read every section before practicing.
