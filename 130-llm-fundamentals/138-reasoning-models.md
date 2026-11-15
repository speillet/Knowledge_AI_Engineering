# Reasoning Models & Test-Time Compute — Flashcards
Tags: #flashcards #ai-engineering #fundamentals #reasoning #llm
Verified on: 25 September 2026 — This factsheet lists products, versions or regulatory texts that are evolving quickly.
<!-- summary: Reasoning model or chain-of-thought per prompt, test-time compute, RLVR, budget reflection, billing, when not to use them, prompting, chain of thought fidelity, interleaved thinking, best-of-n, budget reasoning performance, budget and auditor, intermediate result. -->


What is a Reasoning Model? <!--anki:44457a7a766655556330-->
?
A LLM trained to **produce a long internal reflection** (chain of thought: exploration, verification, backtracking)**before its final answer**. It is significantly better in **maths, code, planning and multi-step problems**, at the price of **more tokens and latency**.

The advantage is to allocate more calculation before the answer, especially to explore or check tracks. The gain depends on the task and the model: a long reflection can remain false or useless. Evaluate the final answer and verifiable results, then compare cost and latency to a baseline with less effort.

---

What is the test-time calculator? <!--anki:68657a773f6c3b31424f-->
?
Spend **more computing at the time of inference** to improve the response, instead of (or in addition to) a larger model.
- **sequential**: reason longer (more than tokens of reflection);
- **parallel**: generate **several responses** and choose (majority vote, checker, best-of-n).

The extra calculation only helps if the crawl brings in new leads and the **selection** recognizes the best ones. Generating ten variants of the same wrong reasoning does not create ten independent proofs. Comparing equally budgeted strategies and examining success rate, persistent errors and time before a usable answer.

---

How do you train a model to be reasoned? <!--anki:452d33327c713c6e6424-->
?
By **RL with verifiable rewards** (RLVR): problems arise that are **automatically verifiable** (mathematical result, unit tests), reward responses **correct**, and the model learns **from itself** strategies (check, resume, break down). Typical algorithms: **PPO**, **GRPO** ([[52-post-training-alignment|post-training]]).

The RLVR is an important pathway, often combined with demonstrations, distillation or other post-training steps. The checker must distinguish a correct solution from a score bypass. Testing then on new problems and varied difficulties; learning to succeed in training exercises does not prove an unlimited generalization of reasoning.

---

What is a reflection budget (thinking budget / reasoning effort)? <!--anki:765438515a4753303f29-->
?
A API parameter that limits or orients **the amount of tokens reasoning** (low/medium/high level, or max number of tokens). This is the **quality/latency/cost** cursor: a high effort for a difficult problem, low effort for a simple or interactive task.

An effort level is often a **orientation**, not an exact amount or a guarantee of accuracy. The reflection can share the output limit: a budget consumed before the answer can leave it truncated. Compare several levels on the same tasks, by difficulty; retain the marginal gain of success compatible with the user delay.

---

How are reasoning tokens billed? <!--anki:75577c53737b3a2f4b71-->
?
Like **tokens output**, even if they are not all visible (some providers return only a **summary**). A short answer can therefore cost **thousands of tokens**. To be followed in the usage metrics and in the calculation of **cost per task** ([[121-inference-costs|costs]]).

Read the service usage counters rather than estimate the bill from the displayed text. Check if the output total **already includes** the reasoning tokens, so as not to count them twice. The rules vary according to the offer; also follow the abandoned attempts and report the cost to the number of tasks correctly completed.

---

When not to use a reasoning model? <!--anki:51502558695d4271762f-->
?
When the **gain measured does not justify the cost and the delay**, or when a deterministic processing is sufficient. Extracting an identifier already structured does not necessarily require a model; classifying an ambiguous text may, however, benefit from reasoning.

Fateful example: switching from 99.0% to 99.1% of valid results by adding two seconds may be unfavorable for instant interaction, but acceptable for an expensive folder to fix.

Compare on the same cases, with statistical uncertainty and cost of errors. Test several budgets, not just two models, and plan an escalation on verifiable criteria.

---

Can we trust the displayed thought chain? <!--anki:4339773d41252f6d6749-->
?
**Not entirely.** Some work shows that the reflection displayed is **not always true** to the actual process: the model can use an index without mentioning it. It is useful for **debugging** and **monitoring**, but it is not a **guaranteed explanation** or proof of correction.

For a numerical answer, redo the calculation; for code, run the tests; for a fact, consult the source. A convincing explanation can rationalize a wrong conclusion, and the absence of a clue in the text does not prove that it did not influence the model. Treat reflection as a signal among others, never as a certification.

---

What is interleaved thinking in an agent? <!--anki:482670287673403f334a-->
?
The model **reasons between two tool calls**: it analyzes the result of a tool before deciding on the next one. This improves the quality of agent **paths**; in general **return the previous reasoning blocks** in the history to keep consistency ([[31-agent-fundamentals|agents]]).

Example: the agent searches for a command, receives "3 results, including 2 canceled", and reasons that it must ask which one is affected instead of acting on the first. Cost: each turn adds tokens of invoiced reasoning and latency, which accumulate on 20 tool calls. The reflection budget is settled according to the issue of the decisions.

---

What is the best-of-n with checker? <!--anki:674758746a32554c483a-->
?
Generate **n answers** and then choose the best through a **verify**: unit tests (code), formal verification, [[95-llm-as-judge|juge]] or reward model. The gain depends mainly on the **quality of the verify**: an executable verify (tests) is much more reliable than a judge LLM.

The cost increases linearly with n, the gain much less: the first additional tests often help clearly, the following ones less and less. With an imperfect judge, increase can even degrade the result: the more candidates there are, the more likely the judge is to prefer a forgery that exploits its biases.

---

Do not confuse: reasoning model and chain-of-thought per prompt? <!--anki:44797d3846553d526763-->
?
- **Chain-of-thought by prompt** A: On **Request** to a classical model to write its steps. The gain depends on the formulation and remains limited ([[11-advanced-prompt-engineering|prompt engineering]])
- **Model of reasoning** : The model was **Trained by RL** to produce a long reflection, Check yourself out and go back. The reflection is **Native**, often adjustable by a budget, and sometimes masked

Consequence: with a reasoning model, we describe **the objective and criteria** rather than the steps, and we pay the tokens of reflection.

In both cases, check the result by calculation, source or independent test: a long convincing justification can remain false.

---

Calculation: 100,000 requests/day use each 1,000 tokens Entry and 300 visible exit. To 3 €/M as input and 15 €/M out, what additional and total cost if each adds 4,000 tokens Reasoning charged at the exit? <!--anki:6261636664353832363133613430613738386335656266613266306232393465-->
?
Assumptions: 1,000 tokens input, 300 tokens visible response, 4,000 tokens reasoning billed as output; 3 €/M input, 15 €/M output.
```text
without reasoning: 1,000 × 3 €/M + 300 × 15 €/M = 0.0075 € per request
Reasoning: 4,000 × 15 €/M = 0.060 € more
with reasoning: 0.0675 € (× 9)
per day: 750 € → 6,750 €
```
The visible answer is the same, but the cost is multiplied by 9 and the latency increases: we adjust the **reasoning effort** by type of request, and we route the simple questions to a mode without reasoning ([[82-routing-llm|routing]]).

---

Why does not increasing the budget of reasoning guarantee an improvement on each task? <!--anki:3065383566393065633661383465373162643766643663623739336164353863-->
?
Additional **calculation** can help to explore or verify, but also repeat a bad hypothesis or exceed the useful time. The gain depends on the task, model and control mechanism.

Compare multiple budgets on the same cases, with quality, cost and latency; identify segments where the gain stabilizes or reverses. Reserve the extra effort for requests that benefit according to an evaluated rule. A long justification is not a proof of correct result: use a checker or an external source when possible.

A stoppage triggered by a verified result must remain separate from a stoppage imposed by budget depletion.

---

Why can a reliable checker be more useful than more candidates in a best-of-n? <!--anki:6363666432646462306663313464383161366363656438393461316539386633-->
?
Producing more answers only helps if the system knows **Select a good answer among them.**. A bad auditor can favor a convincing but false solution.

Measure separately the presence of a good solution in the batch and the quality of the selection. For code or calculations, executable controls can provide targeted proof. They must cover real requirements, not just easy cases.

---

## Scenarios

Scenario: your team spends all the traffic on a reasoning model "since it is better". The triple cost and users find the assistant slow. What do you propose? <!--anki:4c38422a7861506f2f53-->
?
1. **Segmenter**: classification, extraction and reformulation do not benefit from reasoning
2. **Router by difficulty**: reasoning reserved for multi-step problems ([[82-routing-llm|routing]])
3. **Setting effort**: the reflection budget is a slider of quality, latency and cost
4. **Measure the real cost**: reflection tokens are billed as output tokens, even invisible
5. **Check the gain** by segment, on your evals, before generalizing ([[94-evals-methodology|evals]])

**Trap**: Compare models on difficult cases only, then apply the conclusion to all traffic.

---

Scenario: an auditor wants to use the thought chain displayed by the model as justification for the decisions made by your system. What do you say? <!--anki:734e60406e7636373164-->
?
1. **Warn**: the reflection displayed is not always faithful to the actual process of the model
2. **What it is used for**: debug, monitor, spot outliers
3. **What it does not provide**: a guaranteed explanation or proof of correction
4. **What is authentic**: the data consulted, the tools called, the rules applied and the validations ([[115-agent-platforms-governance|audit]])
5. **For sensitive uses**: decision verifiable by code or validated by a human ([[144-ai-ux-human-in-the-loop|human-in-the-loop]])

**Trap**: Present the chain of thought as an opposable justification, especially in a regulated framework.

---

## Sources

- [DeepSeek-AI — DeepSeek-R1 (2025)](https://arxiv.org/abs/2501.12948)

## Connections
- [[52-post-training-alignment|Post-training & Alignment]] — RL with verifiable rewards
- [[11-advanced-prompt-engineering|Prompt engineering]] — chain-of-thought and self-consistency
- [[82-routing-llm|Routing LLM]] — reserve reasoning for difficult queries
- [[121-inference-costs|Inference costs]] — tokens Reflection
- [[64-inference-metrics-slo|Metrics & SLO]] — long response latency
- [[135-pretraining-scaling-laws|Pre-workout & scaling laws]] — of Inference Calculation Training
- [[55-agentic-rl|Agentic RL]] — from reasoning to tools
- [[13-production-prompts|Prompt in production]] — structure, versioning and portability of prompts
- [[60-012-inference-optimization-method|Optimization process]] — prioritize and verify gains under service constraints
- [[00-moc-ai-engineering|MOC AI Engineering]]
