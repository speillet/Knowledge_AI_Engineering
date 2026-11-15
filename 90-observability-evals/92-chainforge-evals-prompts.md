# ChainForge & prompt evaluation — Flashcards
Tags: #flashcards #ai-engineering #evals #prompts #llm
<!-- summary: compare prompts and models, automatic evals, regression tests and tipping cases, evals as a prerequisite for deployment, order of variants and experience biases, variable control, discordant cases. -->


What is ChainForge? <!--anki:50782b535f40475d557e-->
?
A **open source comparison visual environment** to connect the inputs, Prompt, models and assessors to inspect the exits side by side.

Example: Two prompts, two models, and thirty cases give **120 combinations** before repetitions. This grid helps to see that a variant improves short texts but degrades long documents; a single flattering example does not reveal it.

Keep parameters, versions, games, and results, and then confirm on cases kept out of the way. Visual exploration makes it easier to analyze, not statistical proof. For a repeatable CI gate, export or transcribe the protocol into a automatable workflow, without surreptitiously changing the criteria ([[94-evals-methodology|Methodology]]).

---

Why compare variants of prompt on a common grid of inputs and models rather than the feeling? <!--anki:6521623b3457727e2555-->
?
Because a "feeling" judgment on some examples does not allow to compare: a grid **N variants × M models × K inputs**, as in ChainForge, shows the deviations in one pass.

The comparison is based on the same entries, identified variants and explicit evaluation criteria. Repeat the tests if the outputs vary and look at the errors by category. The interface facilitates the experience; it does not automatically choose a representative game and does not transform a subjective score into a reliable measure.

---

What are the orders of magnitude for an evaluation game? <!--anki:4346514f6f3c29256635-->
?
The size depends on the desired **precision**, the rare cases and the comparison protocol. A few dozen examples can detect large defects during the iteration. For a **single score** close to 80%, under the assumption of independent observations:
```text
100 examples → normal margin to 95% about ± 8 points
400 examples → environ ± 4 points
```
These are not universal thresholds of detectable difference between models. A matched comparison depends on their disagreements; a production decision also requires coverage of costly errors ([[114-reproducibility-variance|Statistical uncertainty]]).

---

What simple automatic evaluations apply to the answers of a LLM? <!--anki:767d70246e577d7b7829-->
?
**Exact match, regex, contents, JSON validity, code testing** — fast, free and deterministic when the task is suitable.
```python
import json

def evaluer(output, expected):
    d = json.loads(output)                       # syntax: error if JSON invalid
    assert isinstance(d, dict)                   # structure required here: an object
    assert d["amount"] == expected["amount"]    # content
    assert d["devise"] == expected["devise"]      # the right currency, not just an authorized currency
```
A parsable JSON is not necessarily an object or a correct result. These assertions illustrate a comparison to the reference; the types, units and rounding rules are defined according to the contract. Rule: **the simplest that works** ([[94-evals-methodology|Families of Evaluators]]).

These controls remain as good as their references: a false expected value produces a misleading test. Normalize only differences without business effect, so as not to erase a sign, unit or currency error.

---

What is a Prompt Regression Test? <!--anki:632b5d52586e586c503e-->
?
Replay the **golden dataset with each prompt or model edit**, often in [[112-model-cicd|CI]], and compare the scores to the version in production.

Look at the overall scores. **and** The cases that **Rocker** A stable score can hide ten regressions offset by ten improvements.

Set blocking criteria by risk: an editorial gain does not compensate for a leak between customers. Replay stochastic cases if necessary, with the same protocol for both versions, and examine the paired deviations.

---

Why are evals a prerequisite for deployment? <!--anki:4d4f4667637553714c55-->
?
Without measurement, it is impossible to **choose a model**, **[[82-routing-llm|router]]**, to validate a prompt change or to know if a cost optimization has degraded the quality: we drive blind, on impressions taken from a few examples.

A review of a few hundred representative cases is the first deliverable of a LLM project, before the final prompt.

This volume is a starting point, not sufficient evidence for rare events.Completing with targeted critical cases and declaring the limits: zero error observed on 100 tests does not demonstrate reliability of 100%.

---

Why should a ChainForge experiment mix the order of the evaluated variants? <!--anki:6236646337323261653233373463363638373461373934616261353138313063-->
?
A **fixed order** can confuse variant and execution conditions: hot cache, supplier load, time drift or annotator fatigue.

Pairing entries between variants, randomizing or interlacing their order and saving useful conditions. For a comparative judge, also reverse the position of the answers and hide their origin. Repeat the necessary tests with a fixed protocol. An experiment interface organizes the results; it does not automatically remove biases due to the way calls and judgments are executed.

---

Why inspect cases where two prompts give different results before choosing the best? <!--anki:3265333939333431366665383463643239363162383361666362336632383534-->
?
The average difference can come from **A Few Important Mistakes**. Discordant cases show what the new formulation wins and loses.

Annotate them without knowing the variant when possible, and then check their weight in real traffic. An improvement on a frequent group can hide a rare critical regression. Add counterexamples to the development set without contaminating the independent confirmation test.

---

Why save the actual parameters of a prompt experience, even if the interface shows the default values? <!--anki:3731353361316166396238663436366661303135613963383931663331343063-->
?
The default values can **change with the vendor or version**, so keeping only the prompt text makes the comparison difficult to replicate.

Export resolved model, sampling, limits, data, and evaluator, along with their versions. Check for actually accepted settings, because an ignored option is not an applied option. A screenshot does not replace an exploitable manifest of the experience.

---

## Scenarios

Scenario: your team must choose between three models for an extraction task, and each one has its opinion. How do you slice in a day? <!--anki:4d6e266669303f537a7a-->
?
1. **Build a golden dataset** from 50 to 100 real cases, with expected answers, including difficult cases
2. **Set metrics**: accuracy by field, format validity, cost and latency
3. **Compare in one pass** the three models on the same inputs, with the same prompt then with a prompt adapted to each
4. **Watching errors**, not just scores: the most economical model may fail on critical cases
5. **Decide with three dimensions**: quality, cost, latency ([[146-model-selection|choice of model]])

**Pip**: compare models on ten hand-selected examples, where the observed deviation is only noise ([[114-reproducibility-variance|variance]]).

---

Scenario: a prompt change obviously improves the demo responses, but you don't know if it degrades anything else. What do you do before deploying it? <!--anki:726354326a61687c2d2f-->
?
1. **Replay the golden dataset** before and after, on the same entries
2. **Analyse by matching** the results case by case, to see what improves and what breaks
3. **Automate** this replay in CI, with each change of prompt or model ([[112-model-cicd|eval gate]])
4. **Add new cases** discovered in production to the dataset, especially failures
5. **Deploy gradually** and confirm with production signals ([[91-langfuse-observability|traces]])

**Pip**: validate a prompt on the examples that were used to write it.

---

## Sources

- [NIST — McNemar test for paired binary observations](https://www.itl.nist.gov/div898/software/dataplot/refman1/auxillar/mcnemar.htm)

## Connections
- [[90-010-llm-response-evaluation|Evaluation of responses]] — select eligible criteria and equivalences
- [[91-langfuse-observability|Langfuse]] — evals in production (scores, datasets)
- [[11-advanced-prompt-engineering|Advanced Prompt Engineering]] — what we're evaluating
- [[82-routing-llm|Routing LLM]] — decision based on evals
- [[63-guided-generation|Guided generation]] — structured outputs easier to evaluate
- [[21-rag-fundamentals|RAG]] — Evaluate the Retrieval Pipeline
- [[112-model-cicd|CI/CD models]] — evals as gates
- [[114-reproducibility-variance|Reproducibility & variance]] — confidence intervals, pass@k
- [[94-evals-methodology|Evaluation methodology]] — Full Frame
- [[95-llm-as-judge|LLM-as-a-judge]] — bias and calibration
- [[113-monitoring-drift-feedback|Monitoring & drift]] — quality in production and feedback loop
- [[12-automatic-prompt-optimization|Automatic optimization of prompts]] — let a metric choose the formulation
- [[51-fine-tuning-adaptation|Fine-tuning]] — adapt a model, LoRA and QLoRA
- [[65-probabilities-sampling|Probability & sampling]] — temperature, top-p and logprobs
- [[00-moc-ai-engineering|MOC AI Engineering]]
