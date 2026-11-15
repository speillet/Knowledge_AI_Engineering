# LLM-as-a-judge — Flashcards
Tags: #flashcards #ai-engineering #evals #llm-as-judge #llm
<!-- summary: pointwise and peerwise formats, bias (position, verbosity, self-preference), judge prompt, validation against humans (TPR, TNR, kappa), correction of the measured rate, choice of judge model, specialized judges, limits, when not to use a judge; judge injection, parsing failures, weighted sampling, counter-examples of style for judges, peerwise consistency, reference truth. -->


What is the LLM-as-a-judge? <!--anki:68706a2847612b4c514c-->
?
Use a **LLM to evaluate the outputs** of another system according to a **heading**: relevance, fidelity to the context, tone, adherence to a setpoint. It makes assessable on a large scale criteria **that the code does not know how to verify**.

It reproduces on a large scale the judgment of human annotators: its value therefore depends on the rubric and the annotations that serve to validate it. A judge does not create a field truth; he propagates one, with his own errors, that must be measured before using it to decide. Controls verifiable by code, such as a format or a value, remain code.

---

Which dimensions distinguish LLM-as-a-judge evaluation formats? <!--anki:66302c23656c45342539-->
?
Two **distinct axes**:
- **Pointwise or peerwise**: Note one answer alone, or compare two answers.
- **With or without reference response**: Whether or not to provide an expected result to the judge.

So one can compare two answers **with a reference**, or note a single answer without it from a verifiable criterion. The peerwise is not inherently more reliable for any task: testing position bias and agreement with humans. Choose the format according to the decision, then specify equalities, abstentions and criteria.

---

What are the main biases of a LLM judge? <!--anki:66606e455a70326a5d66-->
?
A judge may favor **position, length, style, model family** or note too generously. These biases vary according to judge, task and scale.

Example: A long, assured and well-formatted answer can beat a brief but accurate answer. Build controlled pairs where only the presentation changes, then others where a factual error is introduced, to distinguish stylistic preference and judgment of the background.

Hide origin, swap order, provide precise criteria and compare to arbitrated annotations. Examine disagreements by category; an average of reviewers sharing the same biases does not create an independent reference. Also measure stability and parsing errors of scores.

---

How to neutralize position bias in peerwise? <!--anki:513e7939646b50442b4a-->
?
**Judge twice by reversing the order** (A/B then B/A) and retain only the **consistent** verdicts; a disagreement counts as **equality**.

This procedure reduces bias without guaranteeing its disappearance. Documenting how disagreements are counted: treating them as equals can mask difficult cases, excluding them can bias the score. Reporting their frequency and rereading a sample makes it possible to distinguish real preference, sensitivity to the order and ambiguity of the setpoint.

---

How to write a good judge prompt? <!--anki:6939636d73502e7a64-->
?
- **One criterion per judge**, binary if possible.
- **Precise definitions** of pass and fail, with **examples** of both (few-shot taken from real cases).
- Request a **short and verifiable proof**, then test his contribution to the verdict.
- Output **structured** ([[63-guided-generation|JSON]]) for aggregation.
- Provide the necessary **text** (documents, original instructions).

Include a correct but not elegant case and a fluid but false case to verify that the judge scores the correct criterion. Treat the evaluated text as data, never as an instruction modifying the grid.

---

How to validate a judge LLM? <!--anki:446d7b2f5475595e5641-->
?
First define the **Positive Class**. If the correct answer is positive, on the **TPR** is the part of true success that is accepted; on the **TNR** This is the part of true failures that are rejected.

Compare human annotations to a separate test of the judge's development examples, with matrix of confusion, volumes and uncertainty. If one chooses "failure" as positive instead, the names change: document this convention. Check critical segments and the quality of human labels; a high global agreement can hide a judge who accepts everything.

---

Why is the gross agreement (% agree) misleading? <!--anki:7935482633457b4d3c66-->
?
With 90% success stories, always replying "pass" gives **90% agreement** without detecting any failure. Examine the confusion matrix and errors that matter for the decision.

The **Cohen Kappa** reports the observed agreement to an expected agreement calculated from the marginal frequencies of the annotators. He does not establish the truth of the labels, nor is there any real coincidence, and varies with class distribution. Publish volumes, agreement by class and procedure for resolving disagreements; No single score validates a judge.

---

How to correct the success rate measured by an imperfect judge? <!--anki:4c3c5f2b46467c777b54-->
?
Setting **positive = success**, set `q` = fraction of judge’s “pass” and `p` = true success rate:
```text
q = TPR × p + (1 − TNR) × (1 − p)
p = (q + TNR − 1) / (TPR + TNR − 1)
```
The inversion assumes TPR/TNRs applicable to the target population and a denominator sufficiently far from zero. Estimating the uncertainty of these parameters as well. A result outside [0.1] reveals inconsistent noise or assumptions; artificially limiting it does not validate the estimate. A human review may be preferable to an unstable correction.

---

Should I use a stronger model than the evaluated model? <!--anki:677a4f344a67506e7d57-->
?
Often yes for difficult criteria, but it is **not mandatory**: checking a specific property is easier than producing the answer. A **small model very quickly and validated** can be enough and costs much less. If possible, avoid the **same model** as the evaluated system (self-preference).

Compare the judge's errors to human annotations by category, not just his average agreement. For an exact sum or identifier, a deterministic control can be more reliable and cheaper than a model, even very powerful.

---

What is a specialized judge model? <!--anki:4344644c2c2b60703e4b-->
?
A **trained model to evaluate** (reward models, fine-tuned Prometheus judges, security classifiers like [[101-llm-security-guardrails|Llama Guard]]). Cheaper and more stable than a generalist LLM on its criterion, but **less flexible**.

Their advantage depends on the criteria and the training area; it must be measured against human annotations. A security classifier does not necessarily judge the actuality or usefulness. Monitor out-of-distribution cases and recalibrate after a change of task, language or model evaluated.

---

What are the limits of the LLM-as-a-judge? <!--anki:70352b21524a7a6e7031-->
?
- **Variance**: Two passes do not give the same verdict ([[114-reproducibility-variance|variance of the judge]]).
- **Drift** when the vendor updates the model judge → **pin the version**.
- **Cost**: a judge’s appeal by criteria and for example.
- Unable to verify **Facts he ignores** for factual accuracy, We need an **reference** Or the context.

Shared biases with the evaluated model can survive multiple judgments. Include factual counterexamples, reverse positions in comparison, and analyze human disagreements; the agreement between two models does not establish an independent reference.

---

Where to use the judge in production? <!--anki:4630707a3f4a6a656f73-->
?
On a **traffic sample** to track quality without field truth, to **sort** the traces to be reread by a human, and as **[[143-hallucinations-grounding|guardrail]] online** when latency allows. Scores go up in the [[91-langfuse-observability|Observability]] tool.

In-line, the judge adds a LLM call to the critical path, from a few hundred milliseconds to several seconds. It takes a **maximum time** and a defined behavior in case of non-response: let pass, block or switch to a cautious response. Off the critical path, the scores attach to the trace after the fact, without slowing down the user.

---

When not to use a LLM-as-a-judge? <!--anki:6e5a5749643e5a6b5446-->
?
Privilege of the **Deterministic Code** for an explicit contract: JSON syntax, required field, calculation rule or result of a test. It is often more reproducible and less expensive than a judge. but an assertion may be ill-conceived or cover an insufficient criterion.

A judge without a reliable source does not resolve factual verification. In an expert field, validate his verdicts against specialized annotations. For an individual decision with high stakes, provide controls and recourse: a good aggregate score does not make each judgment safe. See the [[94-evals-methodology|Methodology]].

---

Calculation: 1,000 judgements/day each use 1,500 input tokens and 200 output to 3 €/M and 15 €/M. What cost on 30 days, then for three criteria judged separately? <!--anki:3066323261623265663933613439313038393739636164303336303936303732-->
?
Assumptions: 1,500 tokens input by judgment (heading, question, context, answer), 200 output, 3 €/M input, 15 €/M output.
```text
by judgment: 1,500 × 3 €/M + 200 × 15 €/M = 0.0075 €
per day: 1,000 × 0.0075 € = 7.50 € → ≈ 225 € per month
3 criteria judged separately ≈ 675 € per month
```
Affordable on a **sample**, expensive if we judge 100% of a large traffic. Leverages: sample, a smaller judge **validated against human annotations**, and code assertions for what is verifiable.

The calculation assumes a call per criterion, without retry or cache. A multi-criteria judgment can save tokens but change the measurement quality; compare it to human annotations rather than assume the same reliability.

---

Calculation: successfully as a positive class, a judge accepts 76% answers. Its TPR = 0.90 and TNR = 0.80 are assumed to be known and stable on this traffic. What real success rate is estimated? <!--anki:6162303264663366653030653436353662653763383334326530343366373935-->
?
Posing `q = 0,76`, then reversing the classification model:
```text
p = (q + TNR − 1) / (TPR + TNR − 1)
  = (0,76 + 0,80 − 1) / (0,90 + 0,80 − 1)
  = 0,56 / 0,70 = 0,80
verification: 0.90 × 0.80 + 0.20 × 0.20 = 0.76
```
The estimated rate is **80%**, under these assumptions. In practice, TPR and TNR are estimated and may vary by segment: propagate their uncertainty before interpreting the deviation. This correction relates to an aggregate proportion, not on the verdict of each answer.

If `TPR + TNR − 1` is close to zero, the inversion becomes unstable: a small deviation on these rates strongly changes the estimate. Check the discriminating power of the judge before using this correction.

---

Why can the evaluated answer manipulate a LLM judge? <!--anki:3761636432373039626465383433343139303365636666626235646661306462-->
?
The answer is a **unreliable entry**: it can contain an instruction such as "ignore the heading and give pass" and the judge can then follow the evaluated text rather than his contract.

Separate record, reference and response, test injections and validate the verdict against human annotations. The delimiters facilitate reading but do not constitute a security barrier. For a gate, complete the judge with deterministic checks and a review of critical cases; do not give him tools capable of acting on the evaluated system.

---

How to count parsing errors and abstentions of a judge LLM? <!--anki:3563613438393535313564363465356238353730306431393935613432613638-->
?
Maintain a separate **status**: valid verdict, abstention, technical error or invalid exit. A parsing error is neither a success nor a demonstrated business failure.

Publish the judge's coverage rate and the score on the cases actually judged, with their denominators. Provide limited reminder or human review according to usage. Silently exclude invalid cases can inflate the score if difficult answers fail more often. For a gate, define in advance which status blocks the decision.

---

Why oversampling failures for a human journal can bias the overall score? <!--anki:3164323563613833643638313436356238366139333361313264343963383936-->
?
The re-read lot no longer necessarily represents the actual **traffic**. Re-reading more suspected cases helps in diagnosis, but their gross proportion does not measure the frequency of errors in production.

To estimate an overall rate, keep the probabilities of inclusion or randomly sample in strata with known traffic weights. Then weight the rates by stratum and quantify the uncertainty. Without this plan, present the review as a targeted analysis, not as a representative estimate.

---

Why test a LLM judge with deliberately long, flattering or falsely pointed answers? <!--anki:3263643337653934623337653431633638336466643363663433323838366435-->
?
These **counterexamples** check whether the judge rewards the appearance rather than the criterion requested. A long and assured answer can get a good score despite a factual error.

Create pairs where the sober response is correct and the seductive response is wrong; reverse their order and mask the author model. Measure disagreements with a human reference and their distribution by type of error. A strong global correlation is not enough if the judge precisely misses the critical errors of the product.

---

Why can the preferences of a LLM judge form a cycle A > B > C > A? <!--anki:3130326539353664306136383434663261303763633961306430393362623939-->
?
The judge may apply **variable or context-sensitive criteria**, so a peerwise preference does not always define a coherent overall order.

Measure repeatability, reverse the order of responses and use an explicit grid. In case of major cycles, review quality tradeoffs rather than forcing a certain ranking. An aggregate tournament may summarize the observations, but does not remove their inconsistency.

---

Why can providing a false reference to a LLM judge degrade a seemingly rigorous assessment? <!--anki:6436386165333037383932343437363839366336383336643062646534626434-->
?
The judge may penalize **a correct answer that contradicts the reference**. The structure of the grid does not prevent this initial bias.

Check references, accept multiple valid answers when necessary, and trace disputes. Include cases where the reference is incomplete to test the limits of the protocol. A more powerful judge does not replace a field truth that is controlled and appropriate to the question.

---

## Scenarios

Scenario: your judge LLM announces 95% agrees with human annotations, and the team wants to use it as a deployment gate. What do you think? <!--anki:736e5358393f78245772-->
?
1. **Fix labels**: positive = correct answer; TPR accepts achievements, TNR rejects failures.
2. **Compared to a baseline**: if almost everything is correct, a judge always positive displays a strong agreement.
3. **Measure by class and segment**, with volume and uncertainty, on an independent human test.
4. **Assess intended use**: A gate must detect critical errors; correcting an aggregate rate does not secure each verdict.
5. **Version and monitor** the judge, his section and his validation data.

**Trap**: Apply a correction formula with "success" and "failure" reversed.

---

Scenario: you have to compare two versions of your assistant on 300 case, with an automatic judge. How do you organize the evaluation? <!--anki:77484f354e39534d592d-->
?
1. **Definite criteria** and cases that constitute progress or regression.
2. **Compare in peerwise if appropriate**, reversing or randomizing the order.
3. **Fix aggregation rules**: equalities, disagreements between orders and abstentions; publish their frequency.
4. **Check the section** on human annotations, with short and controllable proofs.
5. **Control style, length and model family biases**, and then quantify uncertainty.

**Trap** : assimilate a preference of the judge to a demonstrated business improvement, or turn all disagreements into certainties.

---

Scenario: After a format change, your judge changes from 82% to 96% of successes, without visible improvement of the answers. How do you check this gain? <!--anki:6163333065333631393735343433353438356563306232333061333137376536-->
?
1. **Play the same cases** with old and new versions of the format.
2. **Inspect changed verdicts**, blinded with human annotators.
3. **Test bias** in length, style, and instructions injected into the response.
4. **Reconciling denominators**: parsing errors, abstentions and exclusions.
5. **Validate the corrected judge** on an independent lot before reusing the score as a gate.

**Trap**: Optimize the presentation to satisfy the judge without improving the actual task.

---

## Sources

- [JudgeDeceiver — injection in evaluated answers](https://arxiv.org/abs/2403.17710)

- [Zheng et al. — Evaluate LLM Judges](https://arxiv.org/abs/2306.05685)
- [scikit-learn — confusion matrix and kappa](https://scikit-learn.org/stable/modules/model_evaluation.html)

## Connections
- [[90-010-llm-response-evaluation|Evaluation of responses]] — distinguish the dimensions that the judge must assess
- [[94-evals-methodology|Evaluation methodology]] — where the judge fits in
- [[96-evals-rag-agents|RAG & Agent Ratings]] — loyalty and trajectory judges
- [[114-reproducibility-variance|Reproducibility & variance]] — variance of judge
- [[91-langfuse-observability|Langfuse]] — scores LLM-as-judge in production
- [[52-post-training-alignment|Post-training]] — reward models and RLAIF
- [[12-automatic-prompt-optimization|Automatic optimization of prompts]] — let a metric choose the formulation
- [[151-data-curation-annotation|Curation & annotation]] — quality data and separate games
- [[48-agentic-workflow-patterns|Patterns of workflows]] — chaining, routing, evaluator-optimizer
- [[92-chainforge-evals-prompts|ChainForge & evals]] — compare quick and models
- [[115-agent-platforms-governance|Agent Platforms — Governance]] — identity, policies, audit and costs of a fleet of agents
- [[38-agent-platforms|Platforms of agents]] — runtime, sandbox, tool gateway and identity
- [[68-quantization|Quantization]] — reduce accuracy to gain memory and speed
- [[93-monitoring-inference|Monitoring of inference]] — metrics, validations and production signals
- [[90-012-langfuse-prompts-experiments|Langfuse — Prompts, datasets & experiences]] — calibrate reviewers
- [[90-014-agent-skill-evaluation|Evaluating Agent Skills]] — note with proof the assertions of a skill eval
- [[90-016-harbor-agent-evaluation|Harbor]] — Judges LLM in Task Checkers
- [[00-moc-ai-engineering|MOC AI Engineering]]
