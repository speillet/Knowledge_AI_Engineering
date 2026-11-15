# Automatic Prompt Optimization (DSPy) — Flashcards
Tags: #flashcards #ai-engineering #prompt-engineering #dspy #evals #llm
Verified on: 29 September 2026 — This factsheet lists products, versions or regulatory texts that are evolving quickly.
<!-- summary: meta-prompting or metric-guided optimization, DSpy (signatures, modules, BootstrapFewShot optimizers, MIPROv2, GEPA), APE, OPRO, TextGrad, when to use it or not, over-learning, transfer between models, prompt optimization or fine-tuning, critical optimization constraints, constrained goal, research budget. -->


What is automatic prompt optimization? <!--anki:4e78672b25565b49213f-->
?
Treating the Prompt as One **parameter to optimize** : an algorithm proposes variants (instructions, Examples few-shot), on the **evaluates on a dataset with a metric**, and keep the best. The human writes the **Metrics and Data**, Not the formulation.

Prerequisites: a sufficiently reliable **assessment** and representative examples ([[94-evals-methodology|evals]]). Optimizing only the valid JSON can select a prompt that always returns empty fields. Also measure accuracy and coverage; book a final test independent of testing. The volume required depends on the diversity and rarity of errors, not a universal threshold.

---

Do not confuse: Meta-prompting and automatic optimization? <!--anki:324e316873327b5041-->
?
- **Meta-prompting**: Ask a LLM to write or improve a prompt. A more convincing formulation does not prove a gain ([[11-advanced-prompt-engineering|prompt engineering]]).
- **Automatic optimization**: Search for variants and compare them with a measured **metric** on examples.

Meta-prompting can generate the candidates of an optimization loop: the two are not excluded. Example: produce ten extraction variants, classify them on a validation set, then check the winner on a test that remained out of the way. Without this separation, choosing the best score can especially select an overlearning of the examples.

---

What is DSPy? <!--anki:68263769686f2178694b-->
?
A Python framework (Stanford) that replaces handwritten prompts with **programs**: we declare **what** each step should do (signature), we compose **modules**, and an **optimizer** generates instructions and examples from a metric.
```python
import dspy
dspy.configure(lm=dspy.LM("anthropic/claude-sonnet-4-5"))

class Classify(dspy.Signature):
    """Get a support ticket."""
    ticket: str = dspy.InputField()
    category: str = dspy.OutputField(desc="billing, technical or account")

classer = dspy.ChainOfThought(Classify)
```

The signature describes the **input and output contract**; the module chooses a way to solve the task. This extract does not yet initiate any optimization: it is necessary to provide examples, metric and budget to an optimizer. Then evaluate the compiled program on separate cases to detect an overlearning of the prompt.

---

What are DSPy signatures and modules? <!--anki:41376d40793c6c616c4f-->
?
- **Signature**: one-step contract, `inputs -> outputs` typed and described (`"question, context -> reponse"`). She says **what**, never **how**
- **Module**: a call strategy around a signature. `Predict` (single call), `ChainOfThought` (reasoning then response), `ReAct` (agent with tools)

A DSpy program composes modules as a neural network composes layers. Actual prompts are **generated** and can be inspected.

---

How does a DSPy optimizer improve a program? <!--anki:4a5525285d734955594c-->
?
We give him the program, a **training dataset** and a **metric** (`def metric(example, prediction) -> float`), then we **compile**:
- **BootstrapFewShot**: Runs the program, keeps traces that **pass the metric** and injects them as examples few-shot
- **MIPROv2**: jointly searching **instructions and examples** (bayesian optimization on candidates proposed by a LLM)
- **GEPA**: Makes **reflect a LLM on the failures** (traces and textual returns of the metric) to change the instructions

The result is a program that is frozen, saved, and versioned as an artifact.

---

How do APE, OPRO and TextGrad each guide the search for a better prompt? <!--anki:42375e6b5e4274323c29-->
?
- **APE** (Automatic Prompt Engineer, 2022): a LLM generates candidate instructions, we keep the best on a validation game
- **OPRO** (Google DeepMind, 2023): the LLM plays the **optimizer**, seeing the history of the prompts and their scores
- **TextGrad** (2024): Spread textual **gradients**, natural language reviews, through a pipeline of multiple calls

Common idea: research is **guided by a score**, not intuition.

---

When is automatic optimization worth its cost? <!--anki:67365a516b212e525f33-->
?
- **Pipeline of several steps**, where setting each prompt by hand becomes unmanageable
- **Reliable Automatic Metric**: exact match, tests, calibrated judge ([[95-llm-as-judge|LLM-as-a-judge]])
- **Model change** frequent: we **recompile** for the new model instead of rewriting everything
- **Small model** to perform: the optimization of the examples compensates part of the gap

Typical cost: a few hundred to a few thousand LLM calls per compilation.

---

When not to use automatic optimization? <!--anki:79246d48245a6a6b7e25-->
?
- **No automatic metric**: the optimizer would maximize noise
- **Simple task** that a good prompt and three examples already solve
- **Less than a few dozen examples**: high risk of over-learning and unclear validation
- **Constraints of tone or conformity** difficult to measure: the optimizer can sacrifice them to earn points

In these cases, a hand-written and tested prompt remains more readable and safer.

---

Why can an optimized prompt over-learn? <!--anki:643868493d363a6a3b4d-->
?
The optimizer **maximizes the metric on the training set**: it can choose examples or formulations that exploit peculiarities of this data, or the **failures of the metric** (a judge who prefers long answers, for example).

Parades: separate **training, validation and test**, replay generated prompts, and check the gain on a **test game never seen** by the optimizer ([[151-data-curation-annotation|Separation of Games]]).

---

Does one speed optimized for one model transfer to another? <!--anki:4b547b706e6741336725-->
?
**Not necessarily.** The selected instructions and examples are those that worked **for the evaluated model**; changing versions can void the gain. Version the **program, metric, and data**, and then compare the existing prompt to a new optimization on the target model ([[146-model-selection|Model Migration]]).

For example, a formulation that reduces omissions in A can increase false positives in B. Measuring both on the same cases and maintaining an independent test. Recompiling with DSPy is an option to be evaluated, not evidence that a direct transfer will fail.

---

Do not confuse: optimization of prompts and fine-tuning? <!--anki:657c2d797d3f60726269-->
?
- **Prompt optimization**: changes the **text** sent to the model. Works with a **model closed in API**, rereads, compiles in minutes
- **Fine-tuning**: Changes the **weights**. Request an open model or API from fine-tuning, more data, and produce a model to serve ([[51-fine-tuning-adaptation|fine-tuning]])

They combine: DSpy can also **distill** an optimized program to a small fine-tuned model (`BootstrapFinetune`).

---

Why can optimizing a prompt on an average degrade a critical business case? <!--anki:6365663032613936633638383436633362333636373262666539396166366561-->
?
An average **metric** makes it possible to compensate for a rare regression by many small gains. An extractor can thus improve the addresses while degrading the amounts, however decisive.

Define a selection metric and **constraints per segment**: exact amount, rare language, refusal required. Evaluate each candidate on these constraints before comparing his average. Keep independent validation and an explicit test budget. An optimizer improves the objective provided; it does not automatically discover the business cost of errors.

A zero observed on a few critical cases does not guarantee a zero real rate: specify actuality and uncertainty.

---

Calculation: an optimizer tests 24 prompts on 80 inputs with 2 prints, to 0.003 € per generation and 0.001 € by judgment. What evaluation budget to expect, excluding generation of prompts? <!--anki:6365366138663130386563653431666462336530643362656231313532396239-->
?
It takes **24 × 80 × 2 = 3,840 ratings**. Each generation/judgment pair costs 0.004 €, or **15.36 €**.

This amount does not cover either the optimizer's proposals, the covers, or the final test. The number of draws improves the estimation of the variability, but multiplying the candidates also increases the risk of selecting a lucky variant. Reserve a share of the budget to an independent confirmation.

---

## Scenarios

Scenario: your three-step extraction pipeline (classify, extract, normalize) fills 81% with correct fields. Each manual touch-up of one prompt degrades another. How do you use automatic optimization? <!--anki:66336b21255779726a65-->
?
1. **Build the game**: 200 annotated documents, separated in training, validation and testing, never mixed
2. **Write metric**: share of fields exactly correct after normalization, calculated by code
3. **Rewrite the pipeline in modules**: one signature per step, so that the optimizer sets each step according to the score **final**
4. **Compile** with BootstrapFewShot and then MIPROv2, following the cost in calls
5. **Validate on the test**, re-read the generated prompts, then version program, metric and data together ([[91-langfuse-observability|prompt management]])

**Trap**: announce the score of the training dataset, which the optimizer has learned by heart.

---

Scenario: your team wants to migrate to a model that is half as expensive, but the swift ones, hand-settled for a year, Losing 6 points to the new model. What are you proposing? <!--anki:6e4d4f6e45767458594c-->
?
1. **Do not rewrite blindly**: start from the existing eval game and complete it with production hard cases ([[153-data-flywheel-versioning|flywheel]])
2. **Formalize metric** that prompts implicitly optimized
3. **Recompile** prompts for the new model (instructions and examples), rather than carry those of the old model
4. **Compare at equal cost**: score, latency, and **cost per successful task** on the test set ([[121-inference-costs|costs]])
5. **Gradually switch** to canary, with backwards ([[112-model-cicd|CI/CD]])

**Trap**: conclude that the new model is less good while only the prompts were poorly adapted.

---

## Sources

- [DSPy — code and documentation of optimizers](https://github.com/stanfordnlp/dspy)

## Connections
- [[11-advanced-prompt-engineering|Advanced Prompt Engineering]] — manual techniques that the optimizer automates
- [[13-production-prompts|Prompt in production]] — version and maintain the result
- [[94-evals-methodology|Evaluation — methodology]] — the metric is the real deliverable
- [[95-llm-as-judge|LLM-as-a-judge]] — when the metric is a judge
- [[92-chainforge-evals-prompts|ChainForge]] — compare variants by hand
- [[53-synthetic-data-distillation|Distillation]] — from program optimized to small model
- [[146-model-selection|Choice of models]] — recompile with each migration
- [[90-014-agent-skill-evaluation|Evaluating Agent Skills]] — optimize the description of a skill without over-adjustment
- [[00-moc-ai-engineering|MOC AI Engineering]]
