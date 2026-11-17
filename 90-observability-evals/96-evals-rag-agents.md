# Evaluation of RAG & agents — Flashcards
Tags: #flashcards #ai-engineering #evals #rag #agents #llm
<!-- summary: retrieval and generation, precision@k, recall@k and MRR calculations, nDCG, faithfulness or accuracy, oracle context, synthetic datasets, result or trajectory, eval environments, pass^k and efficiency; citation coverage, support calculation, counterfactual tests, external effects verification, minimal evidence, context pollution, annotations required per metric, RAGAS definitions (rank-weighted context precision, context recall against the reference, context relevance, answer relevancy, answer correctness), hit@k or recall@k, NaN scores, agreement with human annotators. -->


How do you split the evaluation of a RAG? <!--anki:486239767d48454b594b-->
?
Into two stages:
1. **Retrieval**: are the right passages retrieved? (recall@k, precision@k, MRR, nDCG)
2. **Generation**: is the answer **faithful** to the passages, and does it **address** the question?

A bad overall score does not say which stage to fix; per-stage metrics do.

Run an oracle test: give the generator the reference passages. If the failure persists, improving retrieval alone is not enough. If the answer becomes correct, compare the evidence actually retrieved, and its versions, with the oracle context.

---

What do recall@k, MRR and nDCG measure? <!--anki:4a7e6f715833634b5574-->
?
**Recall@k** measures the fraction of the annotated relevant items present in the top k; **MRR** averages the inverse rank of the first relevant item, counting zero when none is found within the cutoff. **nDCG** evaluates the order, with optionally graded relevance, normalized by an ideal ranking.

For AP@k, MAP@k and normalization conventions, see [[20-011-retrieval-quality-metrics|retrieval quality metrics]]. Specify the unit — document, passage or piece of evidence —, the cutoff and the handling of queries without any relevant item. An incomplete reference may penalize another valid passage. These measures describe different aspects: finding a single piece of evidence is not always enough to answer a question that requires several.

---

What is the RAG triad? <!--anki:6a653b4e2d6648756538-->
?
1. **Context relevance**: are the retrieved passages relevant to the question?
2. **Faithfulness / groundedness**: is every statement in the answer **supported by the context**?
3. **Answer relevance**: does the answer address **the question asked**?

This is the basis of [[22-advanced-rag|RAGAS]] and equivalent evaluators.

A response can be faithful to a false or outdated context and remain incorrect. Add accuracy of business references, completeness and rights; the three dimensions of the triad isolate defects but do not cover all product guarantees.

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
Precision measures the useful proportion in selection; recall, reference coverage. There are still two relevant passages missing, although the majority of the results are useful. These scores assume reliable judgments to the same — unit here the — passage and do not prove that the generator has exploited the evidence.

---

Calculation: for three queries, the first relevant passage appears at ranks 1, 4, then remains absent from the five evaluated results. What is the MRR@5? <!--anki:6139653836306237353537633463613761323238653363363962613130336263-->
?
Each request contributes the inverse of the rank of the relevant first, or zero if it is absent from the top 5:
```text
MRR@5 = (1/1 + 1/4 + 0) / 3 = 5/12 ≈ 0.417
```
The denominator includes the **three requests**, including failure. Dividing only by the two successful requests would inflate the score. The MRR rewards the quick arrival of a useful first result; it ignores other relevant evidence. For a question that requires multiple documents, complete with a coverage measure.

---

Do not confuse: faithfulness to the sources and factual accuracy of a RAG answer? <!--anki:3438653833316233663937323464373461653464616261383963323063313461-->
?
**Faithfulness** checks that the sources provided support the answer; **accuracy** checks that its content is correct according to a reliable reference suited to the question.

A fictitious example: an old inventory indicates ten units, but the current stock is zero. For a question about the current stock, answering "ten" can be faithful to the document and false; answering "zero" can be accurate without being supported by this document. Examine the freshness and scope of the sources, then evaluate both dimensions; the presence of a citation is not enough.

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

Also test a changed citation without changing the fact to distinguish semantic faithfulness from copying the reference.

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

What annotations do common RAG evaluation metrics require? <!--anki:3235386564336461613334313437633062366264353763653330346463346536-->
?
- **No reference**: faithfulness, answer relevancy, context relevance, `ContextUtilization` in RAGAS. Logging question, context and answer is enough: these metrics can score a sample of production traffic.
- **A reference answer**: context precision and context recall in RAGAS, answer correctness.
- **Annotated relevant passages**: hit@k, precision@k, recall@k, MRR, nDCG.
- **Human judgment**: usefulness, completeness, tone and business risks; it also validates the automated judges.

"Reference-free" does not mean judge-free: these scores depend on an LLM, its prompt and its version ([[94-evals-methodology|eval with or without reference]]).

---

Do not confuse: Context Relevance and Context Precision of a RAG? <!--anki:3339643539663439303231633462366662666334343632646562313730356139-->
?
**Context Relevance** judges whether the retrieved context relates to the **question**, without reference or rank. In RAGAS 0.4, two judge prompts rate all the chunks together from 0 to 2; the average score is scaled to between 0 and 1.

**Context Precision** in RAGAS judges each chunk: does it help produce the **reference answer**? It takes the **rank** of the useful chunks into account.

A passage can cover the right topic without containing the evidence: relevant to the question, it is still useless for the answer. High relevance therefore does not guarantee good precision ([[22-advanced-rag|reranking]]).

---

Calculation: a retriever returns four chunks, only one of which is useful for answering. What precision@4 and RAGAS Context Precision do you get if that chunk comes at rank 1, then at rank 4? <!--anki:6539643365666564363737363465396462393630623565613838643261326462-->
?
```text
precision@4 = 1/4 = 0.25 in both cases
RAGAS, useful chunk at rank 1: (1/1) / 1 = 1.0
RAGAS, useful chunk at rank 4: (1/4) / 1 = 0.25
```
RAGAS averages precision@k only at the ranks of the useful chunks: it measures whether they come **first**. Useless chunks placed after the last useful one cost nothing, although they fill the generator's context. The denominator only counts the useful chunks **retrieved**: missing ones are a matter of recall.

An LLM judges the usefulness of each chunk, one call per chunk, against the reference (`ContextPrecision`) or the generated answer (`ContextUtilization`). The "relevant / retrieved" formula is precision@k: check each tool's definition before comparing scores.

---

Do not confuse: Context Recall in RAGAS and the recall@k of a retriever? <!--anki:3133376162313462616364613463333239366234316434636432623764366436-->
?
**Recall@k** counts the annotated relevant passages found in the top k. **Context Recall** in RAGAS splits the **reference answer** into claims; an LLM then judges whether each one can be attributed to the retrieved context:
```text
Context Recall = attributed claims / claims in the reference
```
The reference thus replaces the annotation of passages, which takes longer to produce.

An incomplete reference overestimates recall. The score names neither the missing chunk nor its rank, and it depends on the judge. For a recall@k on passage IDs, RAGAS offers `IDBasedContextRecall`.

---

Do not confuse: hit@k and the recall@k of a retriever? <!--anki:6635616164333739616635303465613838363333623065623736623036663232-->
?
**Hit@k**, or success@k, is 1 if at least one relevant item appears in the top k, 0 otherwise; it is averaged over queries. **Recall@k** measures the share of relevant items retrieved. The two coincide when each query has a single relevant item.

Example: four relevant passages, only one in the top 5: hit@5 = 1, recall@5 = 0.25. MRR@k never exceeds hit@k: each successful query contributes 1/rank, at most 1.

Names vary: ir_measures notes that some call its success@k "recall@k", and the "granular" hit rate of LlamaIndex is a recall. Check the formula ([[174-recommendation-ranking|ranking]]).

---

How does RAGAS measure Answer Relevancy, and which good answer does it score 0? <!--anki:3565393234343832356537363436656561336564643637386166323266663339-->
?
An LLM generates three questions from the answer by default (`strictness`). RAGAS then averages the cosine between their embeddings and the embedding of the question asked. An incomplete answer, or one loaded with unnecessary details, produces more distant questions; correctness is not measured.

The same LLM flags an evasive answer, such as "I don't know"; if every generation flags it, the score is **0**. A **correct abstention**, on a question with no answer in the corpus, then counts as a failure. Evaluate these questions separately, with abstention as the expected behavior ([[143-hallucinations-grounding|abstention]]).

---

Calculation: RAGAS Answer Correctness weights by default the F1 of the claims at 0.75 and the embedding similarity with the reference at 0.25. Answer A has TP = 3, FP = 1, FN = 1 and a similarity of 0.92. Answer B inverts the key figure: TP = 0, FP = 2, FN = 2, similarity of 0.95. What scores? <!--anki:6536623431616135303366313462376562333731643632663733343031376430-->
?
```text
F1 = TP / (TP + (FP + FN) / 2)
A: F1 = 3 / (3 + 1) = 0.75   score = 0.75 × 0.75 + 0.25 × 0.92 ≈ 0.79
B: F1 = 0                    score = 0.75 × 0    + 0.25 × 0.95 ≈ 0.24
```
TP counts the claims of the answer supported by the reference, FP those that are not, FN the claims of the reference missing from the answer.

B is **wrong** yet scores 0.24: similarity gives a floor to an answer phrased like the reference. To decide pass or fail, read the F1, or set the weights to `[1.0, 0.0]` ([[90-010-llm-response-evaluation|correctness]]).

---

Why count the NaN scores of a RAGAS evaluation before reading its averages? <!--anki:6239346264373365613232653465323438356230336566316563386132323631-->
?
Because the average displayed by `evaluate()` **ignores `NaN` values**. Faithfulness returns `NaN` when the LLM extracts no claim from the answer, for lack of verifiable content: these cases drop out of the overall score, and each metric may cover a different subset. Other metrics handle the same edge case with a **default score** instead: test each metric on an empty answer and on a refusal before trusting its average.

Count the `NaN` values and the claim-less cases per metric, report the number of cases actually scored, and evaluate refusals and empty answers as explicit outcomes ([[90-010-llm-response-evaluation|empty answers]]).

---

What does the agreement of RAGAS with human annotators in the original paper show, and what is its limit? <!--anki:3935356535316639306633323434636462613865333734346233373535646338-->
?
On WikiEval, 50 questions drawn from Wikipedia, two annotators picked the better of two answers or two contexts. RAGAS matched their choice in 95% of pairs for faithfulness, but only 70% for context relevance, the hardest dimension to judge, especially on long contexts.

This validates the ranking of **contrasted pairs**, in English, with gpt-3.5-turbo and the 2023 formulas, not a threshold on absolute scores. Before trusting a RAGAS score on your data, annotate a sample from your domain and measure the agreement metric by metric ([[95-llm-as-judge|validating a judge]]).

---

## Scenarios

Scenario: your RAG displays 62% of answers deemed correct, and the team wants to change generation model. How do you check that it is the right lever? <!--anki:4f663b6b4b4a55712b34-->
?
1. **Separate the stages**: passage recall, faithfulness and accuracy of the answer.
2. **Examine retrieval failures**: missing, poorly parsed, poorly classified or filtered evidence.
3. **Test an oracle context** containing the right evidence, with the same generator and a comparable budget.
4. **Check the claims**: source support and truth are two separate criteria.
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

Scenario: your RAGAS dashboard shows a Context Precision of 0.94 and a Faithfulness of 0.96, but users find the answers incomplete. What do you check? <!--anki:3564626262653263643237333465333362656563633864323330346133646364-->
?
1. **Reread the definitions**: Context Precision judges the order of the retrieved chunks, not the missing ones.
2. **Measure recall**: recall@k on annotated passages, or Context Recall with complete references.
3. **Measure completeness**: the reference claims missing from the answer, i.e. the FN of Answer Correctness.
4. **Count the excluded cases**: `NaN` values and claim-less answers, absent from the averages.
5. **Have humans review** a sample of complaints and successes, to recalibrate the metrics on human judgment ([[94-evals-methodology|annotator agreement]]).

**Trap**: concluding that retrieval is good because Context Precision is high. An answer faithful to a partial context is still incomplete.

---

## Sources

- [Liu et al. — citation support and coverage](https://arxiv.org/abs/2304.09848)
- [Niu et al. — RAGTruth, hallucinations despite a recovered context](https://arxiv.org/abs/2401.00396)

- [Es et al. — dimensions of the RAG assessment](https://arxiv.org/abs/2309.15217)
- [Yao et al. — τ-bench and repeated reliability](https://arxiv.org/abs/2406.12045)
- [Stanford — information search evaluation](https://nlp.stanford.edu/IR-book/html/htmledition/evaluation-of-ranked-retrieval-results-1.html)
- Supplement of 15 November 2026 — RAGAS 0.4.4: [context precision](https://github.com/vibrantlabsai/ragas/blob/8c63f10d500c44efbf24fdb9e2920de2104c321c/docs/concepts/metrics/available_metrics/context_precision.md), [context recall](https://github.com/vibrantlabsai/ragas/blob/8c63f10d500c44efbf24fdb9e2920de2104c321c/docs/concepts/metrics/available_metrics/context_recall.md), [context relevance](https://github.com/vibrantlabsai/ragas/blob/8c63f10d500c44efbf24fdb9e2920de2104c321c/docs/concepts/metrics/available_metrics/nvidia_metrics.md), [answer relevancy](https://github.com/vibrantlabsai/ragas/blob/8c63f10d500c44efbf24fdb9e2920de2104c321c/docs/concepts/metrics/available_metrics/answer_relevance.md), [answer correctness](https://github.com/vibrantlabsai/ragas/blob/8c63f10d500c44efbf24fdb9e2920de2104c321c/docs/concepts/metrics/available_metrics/answer_correctness.md) and [its code](https://github.com/vibrantlabsai/ragas/blob/8c63f10d500c44efbf24fdb9e2920de2104c321c/src/ragas/metrics/collections/answer_correctness/metric.py), [faithfulness without claims](https://github.com/vibrantlabsai/ragas/blob/8c63f10d500c44efbf24fdb9e2920de2104c321c/src/ragas/metrics/collections/faithfulness/metric.py), [average that ignores `NaN` values](https://github.com/vibrantlabsai/ragas/blob/8c63f10d500c44efbf24fdb9e2920de2104c321c/src/ragas/utils.py)
- [Es et al. — RAGAs, EACL 2024: WikiEval and agreement with annotators](https://aclanthology.org/2024.eacl-demo.16/)
- [ir_measures — success@k and the TREC convention for recall@k](https://github.com/terrierteam/ir_measures/blob/cbd73f5dd8013f30deb41581e2c66596cd0db84f/ir_measures/measures/success.py)
- [LlamaIndex — hit rate and MRR, granular variants](https://github.com/run-llama/llama_index/blob/99d7433f6f71888951379ccca9294e272442c832/llama-index-core/llama_index/core/evaluation/retrieval/metrics.py)

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
- [[20-011-retrieval-quality-metrics|Retrieval quality metrics]] — AP/MAP, RR/MRR, relevance judgments and evidence coverage
- [[00-moc-ai-engineering|MOC AI Engineering]]
