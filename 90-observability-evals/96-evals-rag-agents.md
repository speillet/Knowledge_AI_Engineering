# Evaluation of RAG & agents — Flashcards
Tags: #flashcards #ai-engineering #evals #rag #agents #llm
<!-- summary: retrieval and generation, precision/recall calculations@k and MRR, nDCG, fidelity or accuracy, oracle context, synthetic games, result or trajectory, eval environments, pass^k and efficiency; citation coverage, support calculation, counterfactual tests, external effects verification, minimal evidence, context pollution. -->


How to cut the evaluation of a RAG? <!--anki:486239767d48454b594b-->
?
In two floors:
1. **Retrieval**: are the good passages up? (recall@k, precision@k, MRR, nDCG)
2. **Generation**: Is the answer **faithful** to the passages and **responds** to the question?

A bad overall score doesn’t say which one to correct; metrics by floor, yes.

Do an oracle test: provide the generator with the reference passages. If the failure persists, improving the retrieval alone is not enough. If the answer becomes correct, compare the actually recovered proofs and their versions to the oracle context.

---

What do call@k, MRR and nDCG measure? <!--anki:4a7e6f715833634b5574-->
?
The **recall@k** measures the fraction of the relevant annotated elements present in the k primes; the **MRR** averages the inverse of the rank of the first relevant, with zero if none is found in the retained perimeter. The **nDCG** evaluates the order, with relevance possibly graduated and normalized by an ideal ranking.

Specify unit — document, passage or proof —, cutoff and processing of requests without relevance. An incomplete reference may penalize another valid passage. These measures describe different aspects: finding a single proof is not always enough to answer a question that requires several.

---

What is the RAG triad? <!--anki:6a653b4e2d6648756538-->
?
1. **Relevance context**: Are the retrieved passages relevant to the question?
2. **Faithfulness/groundedness**: Is every statement in the answer **supported by context**?
3. **Answer note**: Does the answer address **the question asked**?

This is the basis of [[22-advanced-rag|RAGAS]] and equivalent evaluators.

A response can be faithful to a false or outdated context and remain incorrect. Add accuracy of business references, completeness and rights; the three dimensions of the triad isolate defects but do not cover all product warranties.

---

How to measure truthfulness? <!--anki:775151472b433d507b78-->
?
Break down the answer into verifiable assertions, then evaluate whether **the sources provided support them**. A possible score is the fraction of assertions supported, with explicit rules for contradictions, deductions and empty answers.

Validating the judge or annotators. A true but unsubstantiated statement may be held to be untrue; this does not prove that it comes from the memory of the model. Conversely, faithfully repeating an erroneous source does not make the statement true. Fidelity, accuracy and the answer to the question are complementary criteria.

---

How do I build a game without a massive manual annotation? <!--anki:492e45662f7739523f5b-->
?
**Synthetic generation**: for each chunk, have a LLM write **questions of which this chunk is the answer** → pairs (question, expected chunk). To be completed with **real questions** annotated, because the synthetic questions are often **too close to the text** (lexical overlap) and overestimate the call.

A generator chunk is not necessarily the only relevant passage. Annotate acceptable alternatives and add unanswered, ambiguous or multi-part questions; otherwise the game artificially favors the recovery of a single source text.

---

What is evaluated in an agent? <!--anki:4c60365159432332473a-->
?
- **Final result**: is the task completed? (verifiable by the **final state**: file created, ticket closed, green tests)
- **Trajectory**: good tools, good arguments, no unnecessary or dangerous steps.
- **Efficiency**: number of steps, tokens, cost, duration.
- **Security**: prohibited actions avoided, confirmation requests respected.

Defining the authorized effects and the expected state before the test and then controlling them in the target systems. A good final response obtained after a leak or a double payment is a failure, even if the formulation seems perfect.

---

Why would you prefer to check the final state rather than the exact trajectory? <!--anki:665d214731723872667a-->
?
There can be **several valid paths**. Requiring an exact call sequence penalizes correct solutions and makes evaluation **brittle**. Check the **result** in a controlled environment, and impose only necessary trajectory **constraints**, such as forbidden tools, mandatory steps and a maximum budget.

For “cancel order 42 and notify the customer,” verify that the order was canceled, exactly one email reached the correct recipient, and no other order changed. Whether the agent checked status first is incidental. However, a correct final state can conceal a dangerous path, such as deletion followed by recreation; explicit trajectory constraints address this limitation.

---

What is an agent eval environment? <!--anki:77776f6c5d3a242e7325-->
?
A **Reproducible sandbox** False Services (API Mockery, basis of testing, fixed git deposit), **Simulated User** by an LLM for multi-tour conversations, and **Automatic Checker** of the final state. Public examples: **τ-bench** (customer support), **SWE-bench** (fixing bugs), **WebArena**, **OSWorld**.

Reproducibility requires **resetting** the state before each test and freezing what varies: simulated date, data, responses from external APIs. Otherwise, a test that changed the next false basis and two runs no longer compare. The simulated user adds his own variance: repeat the tests rather than judge on a single pass.

---

How to evaluate tool calling in isolation? <!--anki:4e634e67316076667936-->
?
On unit cases: for a given query, check **the choice of tool**, the **validity of arguments** (scheme, values), the cases where **no tools** should be called, and the parallel **calls**. Evaluations **by rules**, fast and deterministic → ideal in [[112-model-cicd|CI]].

Case example: "Where's my 4212 command?" waits for the `order_status` tool with `{"id": "4212"}` and no other calls. Measure tool selection, argument validity, and toolless false calls separately. An agent who calls a tool at each message gets an excellent reminder, but poor accuracy.

---

How to evaluate a multi-turn conversation? <!--anki:6c46715556596074525d-->
?
Combine **scripted scenarios, authorized actual conversations and simulators**, and then evaluate objective achieved, consistency, changes of opinion and final business status.

Example: the user corrects his address in the third round; check that the final proposal and the tool use the new address, not only that the agent answers "understood".

A LLM simulator explores more variants but adds bias and variance; repeating tests and checking that it complies with the scenario. Keeping deterministic cases for invariants and an independent reference. The agreement of two agents on "mission accomplished" does not prove actual success.

---

Which efficiency metrics to follow in addition to quality? <!--anki:515e3872755f6a3b5d67-->
?
**Tokens and cost-per-task success**, **number of steps**, **end-to-end latency**, **loops** or abandonment rates. A more accurate agent but three times more expensive is not necessarily better: we compare on a **front quality / cost** ([[122-finops-llm|FinOps]]).

Example: Agent A passes 80% tasks to 0.05 € attempt, B 88% to 0.15 €. If each failure costs an escalation to 2 €, 100 tasks cost 45 € with A and 39 € with B: the cost of a failed part.

---

Calculation: on a given task, each independent test succeeds with constant probability 0.9. What is pass^5? <!--anki:6664613061633837663230343433353462663263393038633136326162303030-->
?
With a constant **probability of 0.9 for this task** and independent testing:
```text
P(5 successes on 5) = 0.9^5 = 0.59049 ≈ 59%
P(8 successes on 8) = 0.9^8 ≈ 43%
```
This is a repeated probability of success, not that of obtaining at least one correct answer. If the tests are dependent or the probabilities differ according to the tasks, these powers no longer directly describe the observed result. An overall rate of 90% is therefore not enough to apply the formula to each task.

---

Calculation: of four relevant passages annotated for a query, two appear in the three retrieved results, all distinct and judged. What are precision@3 and recall@3? <!--anki:3432393763326533356630363437366162653636643639393132396662633331-->
?
Denominators answer two different questions:
```text
precision@3 = relevant recovered / recovered = 2/3 ≈ 66.7%
recall@3 = relevant retrieved / relevant annotated = 2/4 = 50%
```
Accuracy measures the useful proportion in selection; recall, reference coverage. There are still two relevant passages missing, although the majority of the results are useful. These scores assume reliable judgments to the same — unit here the — passage and do not prove that the generator has exploited the evidence.

---

Calculation: for three queries, the first relevant pass appears in the ranks 1, 4, then remains absent from the five evaluated results. What is the MRR@5? <!--anki:6139653836306237353537633463613761323238653363363962613130336263-->
?
Each request contributes the inverse of the rank of the relevant first, or zero if it is absent from the top 5:
```text
MRR@5 = (1/1 + 1/4 + 0) / 3 = 5/12 ≈ 0,417
```
The denominator includes the **three requests**, including failure. Dividing only by the two successful requests would inflate the score. The MRR rewards the quick arrival of a useful first result; it ignores other relevant evidence. For a question that requires multiple documents, complete with a coverage measure.

---

Do not confuse: source fidelity and factual accuracy of a RAG response? <!--anki:3438653833316233663937323464373461653464616261383963323063313461-->
?
The **fidelity** verifies that the sources provided support the answer; the **accuracy** verifies that its content is correct according to a reliable reference adapted to the question.

A fictitious example: an old inventory indicates ten units, but the current stock is zero. For a question about the current stock, answer "ten" can be faithful to the document and false. Answer "zero" can be accurate without being supported by this document. Examine freshness and perimeter of sources, then evaluate both dimensions; a quote present is not enough.

---

How does an Oracle context help diagnose a RAG failure? <!--anki:6536643366363832613033393464306539373163383664653464353565323064-->
?
Replace the retrieved passages with a verified **context containing the necessary evidence**, while keeping question, generator and record comparable.

If the response improves, recovery or context preparation is a likely lever. If it fails again, consider understanding, instruction, conflict between sources and evaluation criteria. Controlling length, order and noise: a very short oracle context changes several factors. Using diagnostic cases separate from the final test; this intervention locates a problem, it does not prove that a better retriever will suffice in production.

---

Do not confuse: validity, support and coverage of RAG quotes? <!--anki:3339306365646439383137643466336639643336396363326662326262346235-->
?
The **validity** verifies that the reference exists and is accessible; the **support** verifies that the quoted passage supports the associated assertion; the **coverage** verifies that the assertions requiring proof have sufficient proof.

An answer can cite an actual document without it supporting its number. It can also correctly quote a single sentence and leave the rest without proof. Evaluate these three properties separately, with an explicit rule for statements that require a quote.

---

Calculation: one RAG response contains eight statements requiring proof; six are cited and four of these six are fully supported. What citation coverage and what proportion of supported statements is obtained? <!--anki:6431353064663736313966613438666661353363383938323830616436633336-->
?
With the units fixed on the front:
```text
citation cover = 6 / 8 = 75%
fraction of supported claims = 4 / 8 = 50 %
support among quoted claims = 4 / 6 ≈ 66.7%
```
The first score measures the presence of a citation, not its quality. The third is about the **claims cited**, not about each individual link: one should not rename it citation accuracy without defining this unit. The four unsupported assertions require verification, correction or withdrawal.

A citation covering two assertions must be checked for each. Preserve the decomposition of assertions and expected passages makes these denominators auditable; a single metric does not distinguish absence of reference and misleading reference.

---

How to test that a RAG actually uses the provided context? <!--anki:3063626439353131343730653432353762356538376433376630376438353436-->
?
Construct controlled counterfactual **tests**: change a fact in a fictitious document and verify that the response follows that change, and then remove the evidence to test abstention.

Keep question and configuration comparable; avoid transformations that make the document inconsistent. Add a variant with a contradictory source and an explicit priority rule. These tests reveal a dependence on context on the cases tested; they do not prove that all future answers will be faithful.

Also test a changed citation without changing the fact to distinguish semantic fidelity and reference copy.

---

Why should an agent evaluation check its external effects, even if its final answer is correct? <!--anki:3839373231623233343337383466363138343961656331653165313934303235-->
?
The final **answer** may announce the correct result while the agent has created a duplicate, accessed prohibited data, or omitted a write, so the evaluation must also inspect the external state.

Set initial state, expected and invariant effects to never violate. After the run, query the business source and check the permissions of the calls made. Include unknown failures and results. Correct text obtained at the price of a leak or an incorrect throughput does not constitute a successful task.

---

Why evaluate a RAG with plausible but irrelevant passages? <!--anki:6537383437663232363139643435346338613265626238343537623730303636-->
?
They test its ability to **ignore distractors**, which a context composed of only good evidence does not measure. lexically close passages may contain another date, entity or version.

Compare to the context without distractors and identify contaminated claims. A good recall can coexist with poor noise resistance. To vary the number and position of distractors without changing the necessary evidence.

---

## Scenarios

Scenario: your RAG displays 62% of answers deemed correct, and the team wants to change generation model. How do you check that it is the right lever? <!--anki:4f663b6b4b4a55712b34-->
?
1. **Separate floors**: recall of passages, fidelity and accuracy of the response.
2. **Examine retrieval failures**: missing, poorly parsed, poorly classified or filtered evidence.
3. **Test an oracle context** containing the right evidence, with the same generator and a comparable budget.
4. **Checking claims**: Source support and truth are two separate criteria.
5. **Choose the measured lever**, then compare quality, cost and latency ([[146-model-selection|choice of model]]).

**Trap**: infer the cause of a bad overall score without isolating retrieval and generation.

---

Scenario: your support agent passes 80% tasks in testing, but users find it unreliable. How do you explain the gap? <!--anki:6339702b49452f682876-->
?
1. **Difference between capacity and reliability**: with constant probability of 80% and independent tests, three consecutive successes are worth 0.8³ ≈ 51%; measure by task if these assumptions do not hold up
2. **Complete success on first try** by pass^k, severity of failures and results by segment
3. **Look at the variance**: same entries replayed several times, to identify unstable tasks
4. **Stabilize**: narrower tools, deterministic validations, verifiable steps rather than free
5. **Predicting failure** Climbing towards a human rather than an approximate response.[[144-ai-ux-human-in-the-loop|UX]])

**Trap**: Communicate an average success rate as if it were a guarantee per request.

---

Scenario: you need to evaluate an agent who edits tickets and sends emails. How do you build the test environment? <!--anki:425a3d32585b2a4c7d41-->
?
1. **Reproducible sandbox**: Simulated services, test base, fixed deposit, no actual action
2. **Check the final status**: is the ticket in the right status, does the email contain the right items?
3. **Do not set the exact path**: several paths are valid. We place constraints (forbidden tool, step budget)
4. **Simulated user** for multi-turn conversations, with multiple runs as it adds variance
5. **Follow efficiency**: steps, tokens and cost per successful task ([[122-finops-llm|FinOps]])

**Trap**: test in production “on real tickets, but with care”.

---

Scenario: your RAG still provides valid links, but still invents refund terms. How do you enrich the rating? <!--anki:6431323035623737626337343434343761393661353338343238333835373533-->
?
1. **Decompose responses** in verifiable conditions: deadline, amount, exclusions.
2. **Check the support** of each condition by the passages actually mentioned.
3. **Measure coverage** for conditions that require proof.
4. **Add difficult cases**: absent exception, old policy, contradiction and unanswered question.
5. **Review critical errors**, then compare variants on the same independent test.

**Trap**: confuse an existing URL with proof of affirmation.

---

## Sources

- [Liu et al. — citation support and coverage](https://arxiv.org/abs/2304.09848)
- [Niu et al. — RAGTruth, hallucinations despite a recovered context](https://arxiv.org/abs/2401.00396)

- [Es et al. — dimensions of the RAG assessment](https://arxiv.org/abs/2309.15217)
- [Yao et al. — τ-bench and repeated reliability](https://arxiv.org/abs/2406.12045)
- [Stanford — information search evaluation](https://nlp.stanford.edu/IR-book/html/htmledition/evaluation-of-ranked-retrieval-results-1.html)

## Connections
- [[20-010-rag-permissions-versions|RAG: rights & versions]] — test for applicable withdrawals, access restrictions and evidence
- [[90-010-llm-response-evaluation|Evaluation of responses]] — completeness, references and aggregation by affirmation
- [[94-evals-methodology|Evaluation methodology]] — General Frame
- [[95-llm-as-judge|LLM-as-a-judge]] — judges of truthfulness and trajectory
- [[21-rag-fundamentals|RAG — Fundamentals]] and [[22-advanced-rag|Advanced RAG]] —
- [[31-agent-fundamentals|Agents]] and [[32-tool-calling|tool calling]] —
- [[134-vector-search-ann|Vector search]] — ANN Index Reminder
- [[114-reproducibility-variance|Reproducibility & variance]] — pass@k, pass^k
- [[98-agent-debugging|Debugging agents]] — understand why a task fails
- [[27-search-agents-deep-research|Research agents]] — review coverage and quotes
- [[133-embeddings-representations|Embeddings]] — represent meaning by vectors
- [[143-hallucinations-grounding|Hallucinations & grounding]] — quotes, abstention and verification
- [[25-chunking-contextual-retrieval|Advanced Chunking]] — Make Every Chunk Found
- [[26-text-to-sql|Text-to-SQL]] — answer numerical questions on tables
- [[49-coding-agents|Code Agents]] — Use and Integrate Code Agents
- [[55-agentic-rl|Agentic RL]] — train a model on agent tasks
- [[174-recommendation-ranking|Recommandation & learning to rank]] — measure recall and result order
- [[90-013-agent-testing-recovery|Agents — Contracts, failures & recoveries testing]] — measure business results
- [[90-014-agent-skill-evaluation|Evaluating Agent Skills]] — evaluate an agent with and without a skill
- [[90-016-harbor-agent-evaluation|Harbor]] — run container agent evals
- [[00-moc-ai-engineering|MOC AI Engineering]]
