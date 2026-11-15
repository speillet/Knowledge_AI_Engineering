# System evaluation LLM — Methodology — Flashcards
Tags: #flashcards #ai-engineering #evals #llm #quality
<!-- summary: benchmark or eval application, error analysis, golden dataset, game size, evaluation families, binary criteria, with or without reference, offline and online, eval-driven development, saturation, anti-patterns, representative cases and adversarial cases, annotation disagreement, test maintenance. -->


Why is assessment the core competency of a senior AI Engineer? <!--anki:672b7a264c7763732b24-->
?
They turn an impression into a **verifiable decision**: compare variants, identify failures and limit regressions on representative tasks.

Example: a prompt increases the average score but forgets more about contractual exceptions. A segmented eval reveals it and allows to block the promotion despite a better overall score.

Link each criterion to the expected service, keep the cases and versions, and then associate software tests, strict invariants and behavioral measures with uncertainty. The evaluation must also focus on its own judges and its coverage. A demonstration is not enough; neither is a non-representative evaluation. The evidence remains limited to the protocol and must be supplemented by monitoring in production.

---

Do not confuse: benchmark public et eval applicative? <!--anki:7a433e69633c7d2f2c32-->
?
A public **benchmark** measures the tasks and conditions defined by its authors; an application **eval** represents the uses and criteria of your service. The first helps with pre-sorting; the second helps to choose and control a solution for this need.

Neither of them automatically predicts production. Check for contamination, representativeness, versions and protocol, and then compare the results to actual traffic. A well-ranked model on code can incorrectly extract the fields of your documents. Compare variants on the same cases and budgets.

---

What do you need to start building evals? <!--anki:45287263614956357d47-->
?
Define the **task and its requirements**, then examine real or simulated examples and errors: missing sources, wrong amount, forbidden action, invalid format. Group the failures to choose criteria that guide a correction: on 100 replayed conversations, for example 31 missing sources, 12 false amounts and 4 forbidden actions ([[98-agent-debugging|Analysis of Errors]]).

A first sample helps to discover problems, without claiming to estimate their actual frequency. Add important limit cases even if they are not yet observed. Contracts already known, such as access rights or accuracy of a calculation, do not wait for an incident to become evaluation criteria.

---

What is a golden dataset and how do I build it? <!--anki:686a7c383d56593b4855-->
?
A **Reference game versioned** contains entries, necessary context and expected answers or criteria. Combining representative traffic, business case, known regressions and re-read limit cases: for example 300 requests drawn at random from traffic, 60 cases written with the support and 40 regressions.

Differentiate their usage: added bugs feed non-regression; an independent final test is used to estimate quality without guiding settings. A game voluntarily enriched in difficult cases no longer directly represents the frequency of traffic. Documenting the origin, segments, rights and quality of annotations. “Golden” does not mean that each reference is infallible or immutable.

---

What are the three families of assessors? <!--anki:7a46426d355b3c3e386b-->
?
The **code** controls explicit properties: schema, expected value or execution tests. A **LLM** judge appreciates defined semantic criteria. The **humans** establish and discuss references, especially for ambiguous cases.

Example for an invoice extraction: the code checks `total == somme(line_items)`, a judge checks that a reformulated wording keeps its meaning, a human decides ambiguous invoices. Everyone can be wrong: choose the simplest way that actually measures the criterion, then validate it. The code has a cost and its determination does not guarantee the relevance of the test. A valid JSON output does not prove that its amount is correct.

---

Why prefer binary criteria (pass/fail) to 1 to 10? <!--anki:796e4c44435b4b7e4e43-->
?
A **Explicit Binary Criteria** facilitates a compliance decision: “Are all quantified statements supported? ». It makes the error localizable and compares to a reference annotation: two annotators that note the same answer 6 and 8 on the 10 They both say “no” to this. by pointing to the same amount.

This is not always superior to a scale: stylistic quality or graded relevance may require several levels, described by anchor examples. A vague binary question remains vague. Measure evaluators' agreement and errors, and do not reduce several dimensions to a yes/no that hides regressions.

---

Do not confuse: eval with reference-based and eval without reference-free? <!--anki:4d5563343c4437657732-->
?
An eval **with reference** uses a response, facts, or expected result to compare the output. An eval **without reference** verifies a criterion from the available data: format, record, or document support.

Example: "Amount extracted = €1,240.00" compares to the annotated value; "the answer contains only facts present in the passages" is judged without reference answer. "Without reference" does not mean without reliable information: judging fidelity requires the source context. A reference may also contain errors or illustrate only a valid formulation among others.

---

Do not confuse: offline evaluation and online evaluation? <!--anki:454b247c583369367a35-->
?
- **Offline**: On a **frozen** game before deployment — detects regressions, serves as [[112-model-cicd|gate CI]].
- **Online** on the **Real Traffic** — without reference on a sample, user feedback, [[97-evals-online-ab-testing|A/B tests]].

Example: in offline, 400 frozen cases block a PR if accuracy drops; in online, a validated judge notes every day 2% real conversations about fidelity to sources.

Both feed off: chess seen online **feeds the golden dataset**.

---

Why evaluate the components **and** the end-to-end system? <!--anki:4529237523433a3c5f4b-->
?
The end-to-end says **if** it works; the component evals say **where** it breaks. A [[96-evals-rag-agents|RAG]] is divided into **retrieval** (is the good document reassembled?) and **generation** (is the answer true?); an agent in **tool selection**, **arguments**, **trajectory** and **final result**.

Example: Success changes from 82% to 74%; recall@5 remains stable but fidelity decreases. Examine generation and effective context: An identical recall may hide other distractors or a different order. Replay with set context before assigning the gap to the prompt.

---

What is eval-driven development? <!--anki:774521632879232f4d3b-->
?
Write **the eval before the change**, as in TDD: set the case that fails, change prompt, retrieve or model, then check that **the case passes without regressing elsewhere**. Each iteration is **measured**, not judged "on feeling".

Example: a user reports that the assistant invents a repayment period. First, we add this case to the game, found in check, with a binary criterion: "quotes the policy in force or abstains". Then we modify the prompt and we replay the whole game; the case then remains in non-regression. Limit: constantly optimizing the added cases overlearns the game.

---

What is the saturation of an eval and what to do? <!--anki:4730412c2d44506c2d2f-->
?
When the system reaches **~100%** on the game, The Eval **no longer discriminates** : it still protects against regressions but no longer guides improvement. Two very different models get 98% and 99% on the 200 case; The difference is due to two questions. We must **Add Harder Cases** (Failure of Prod. adversarial cases) to keep a **Game of Progress** separate from the **Game of Non-Regression**.

---

What are the classic anti-patterns in evaluation? <!--anki:7a58572a706e4a592975-->
?
- Adopt generic **metrics** (“helpfulness”) without error analysis.
- **Judge LLM not validated** against humans.
- **Game too small** and conclusions drawn from a gap of 2 points.
- **Contamination**: Optimize prompts on the test set itself (**overfitting** at evals).
- Forget the **costs and latency** in the comparison.

Example of overfitting: fifteen iterations of prompt set on the 100 test cases raise the score from 72% to 86%, then it falls back to 74% on 100 never seen cases.

---

Calculation: for a success rate close to 70%, how many independent Bernoulli observations does it take about for a margin of ±3 points to 95%, with the normal approximation? <!--anki:3763333165623463643835383436323462346134626564643634653863326439-->
?
We reverse the formula of the confidence interval to 95% ([[114-reproducibility-variance|variance]]):
```text
n ≈ 1,96² × p(1 − p) / margin²
± 3 points: 3.84 × 0.7 × 0.3 / 0.03² ≈ 900 case
± 5 points: 3.84 × 0.21 / 0.05² ≈ 320 cases
± 10 points: ≈ 80 cases
```
Divide the margin by 2 requests 4 times more cases. To divide two versions to 2 or 3 points of difference, a **paired** comparison on the same cases is more sensitive.

The formula assumes **independent** cases. 900 questions from 60 conversations of the same client are not worth 900 observations: the answers of the same conversation are similar, and the actual uncertainty is wider than the calculated margin.

---

Why book a set of representative cases and a set of separate adversarial cases in the evals? <!--anki:6532653739316565393430643436316139653663346234666366386132313364-->
?
The **Representative Cases** assess the behaviour of the intended use; on the **Adversarial Cases** Look for limits and failures. Mixing their scores without explicit weighting makes the result difficult to interpret.

Separately report current performance, risk coverage, and critical violations. Set blocking criteria before comparing variants. A deliberately difficult adversarial set does not measure the natural frequency of incidents; a current sample may ignore a rare attack. Both are used to decide, with roles and denominators announced.

---

Why measure annotator agreement before finely comparing two models? <!--anki:6339316436623763363333613432373762353239333065366336613533373861-->
?
If the evaluation instruction is ambiguous, **the noise of the labels can exceed the difference between models**. Different notes do not necessarily reveal a difference in quality.

Annotate a common subset, analyze disagreements and clarify criteria. Keep irreducible ambiguities with an explicit policy. High agreement does not guarantee the truth: annotators can share the same bias or a bad reference.

---

When to renew an evaluation game that has become too familiar to the team? <!--anki:6430343661666538316263613464333962646666306635386164346166306437-->
?
When successive decisions have **overmatched the system to the same examples**, or actual usages change. Keep a history to measure regressions and add a recent independent game.

Do not clear difficult cases to beautify the score. Version composition, annotations and criteria to explain a variation. A new score is only comparable to the old one if the change in population and protocol is taken into account.

---

## Scenarios

Scenario: you take over a production assistant who has no evaluation. What do you do during the first week? <!--anki:484b26356c43544e5055-->
?
1. **Clarify requirements**: expected tasks, constraints and critical errors already known.
2. **Read various traces** and group observed failures, not limited to reported incidents.
3. **Separate development and testing**, with verified references; also keep a focused non-regression corpus.
4. **Choose observable criteria**: assertions for contracts, validated judge or humane for the rest.
5. **Finish a CI rating**, then track segments and production ([[112-model-cicd|eval gate]]).

**Trap**: take the error rate of a corpus made up of bugs for that of real traffic.

---

Scenario: a colleague announces that his new prompt raises the score from 78% to 81% on 100 examples. What is your reaction? <!--anki:63427c294379574b6125-->
?
1. **Check protocol**: same 100 examples, correct references and comparable conditions?
2. **Compare in pairing**: count the cases won and lost; the difference of the averages does not give its uncertainty ([[114-reproducibility-variance|Comparison Paired]]).
3. **Quantify uncertainty** with a method adapted to the observations, then repeat the generations if they vary.
4. **Examine regressions** by segment, especially costly errors.
5. **Check the independence of the test**, then increase the sample if the decision remains uncertain.

**Trap**: Assimilate the margin of error of an individual score to that of the matched difference, or promote three additional achievements without analyzing the cases.

---

Scenario: your main eval has been displaying 99% for three months, while users continue to experience problems. What happens? <!--anki:457660597676656d2e26-->
?
1. **Eval is saturated**: it no longer discriminates, even if it still protects against regressions
2. **Separate games**: a game of non-regression, and a game of progress with significantly harder cases
3. **Feed** this new game with real failures coming back from the field
4. **Check coverage**: Do reported problems fall into categories that have never been measured?
5. **Complete with online**: sample scores, feedback, A/B ([[97-evals-online-ab-testing|evals online]])

**Trap**: Reassure yourself with a high score on a game that no longer looks like real traffic.

---

## Sources

- [Sculley et al. — testing and debt of ML systems](https://papers.nips.cc/paper/5656-hidden-technical-debt-in-machine-learning-systems)
- [Zheng et al. — judges, criteria and bias](https://arxiv.org/abs/2306.05685)

- [NIST — McNemar test for paired binary observations](https://www.itl.nist.gov/div898/software/dataplot/refman1/auxillar/mcnemar.htm)

## Connections
- [[90-010-llm-response-evaluation|Evaluation of responses]] — grid, completeness and metrics according to the task
- [[95-llm-as-judge|LLM-as-a-judge]] — the automatic evaluator of subjective criteria
- [[96-evals-rag-agents|RAG & Agent Ratings]] — evaluate by component
- [[97-evals-online-ab-testing|Evals online & A/B testing]] — measure in production
- [[92-chainforge-evals-prompts|ChainForge]] — quick comparison tooling
- [[91-langfuse-observability|Langfuse]] — tracks, datasets and scores
- [[114-reproducibility-variance|Reproducibility & variance]] — eval statistics
- [[112-model-cicd|CI/CD models]] — evals as gates
- [[151-data-curation-annotation|Data & annotation]] — produce reliable labels
- [[12-automatic-prompt-optimization|Automatic optimization of prompts]] — metric as optimization engine
- [[98-agent-debugging|Debugging agents]] — error analysis before metrics
- [[147-ai-technical-leadership|Technical Leadership]] — team standards and decisions
- [[148-llm-batch-pipelines|Pipelines batch]] — process millions of items at a lower cost
- [[156-responsible-ai|IA responsable]] — bias, fairness and transparency
- [[49-coding-agents|Code Agents]] — Use and Integrate Code Agents
- [[53-synthetic-data-distillation|Synthetic Data & Distillation]] — generate data and transfer to a small model
- [[172-ml-validation-metrics|Validation & ML metrics]] — splits, rare classes and predictor comparison
- [[99-statistics-experimental-decisions|Statistics to decide in AI]] — moving from a score to a justified decision
- [[146-model-selection|Choice of models]] — split candidates on task
- [[90-013-agent-testing-recovery|Agents — Contracts, failures & recoveries testing]] — games and success criteria
- [[90-014-agent-skill-evaluation|Evaluating Agent Skills]] — a matched eval applied to agent skills
- [[00-moc-ai-engineering|MOC AI Engineering]]
