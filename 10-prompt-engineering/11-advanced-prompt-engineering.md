# Advanced prompt engineering — Flashcards
Tags: #flashcards #ai-engineering #prompt-engineering #llm
<!-- summary: system prompt and user prompt, few-shot, few-shot or fine-tuning, chain-of-thought (cost, tags), self-consistency and its limits, delimiters, decomposition into calls, meta-prompting, prompt versions as code, anti-patterns, metamorphic tests, removal of instructions, limit examples. -->


What is the system prompt compared to the user prompt? <!--anki:6876605d304e7d7c4d6f-->
?
The **system prompt sets the frame** (role, rules, format, perimeter); the **user prompt carries the task** of the moment. In the hierarchy provided by the API, the frame prevails over an incompatible user request.

Example: The system requires a sourced response; the user requests to invent a reference. The wizard must report the lack of evidence, not fabricate a citation. Separating the stable instructions from the request data facilitates testing of this conflict. **Priority is not a security barrier**: permissions and validations of actions remain applied by the code.

---

What is few-shot prompting? <!--anki:64397243675666243d58-->
?
The **few-shot prompting** provides examples of input → output in context, without changing weights. The examples show the format and expected distinctions, including cases that are easy to confuse.

Choosing examples that are consistent with the setpoint, diversified and distinct from the final test. Their number, order and proximity to the query can change the result: compare to the zero-shot and then measure the gain and cost. "Three to five examples are enough" is not a universal rule. Conflicting examples create ambiguity, without guaranteeing which model will follow.

---

Do not confuse: few-shot and fine-tuning? <!--anki:412f6970745161503d55-->
?
The **few-shot** provides examples to run in the prompt; the **fine-tuning** uses training examples to change settings, sometimes only adapters.

The first allows for fast iteration but consumes context; the second requests data, training and validation. It does not, on its own, guarantee a more constant behavior or a reliable memorization of the facts. Start with a simple baseline, then compare to equivalent quality and cost of service. The number of examples to be returned is a reason for studying the fine-tuning, not a sufficient criterion to tip over.

---

What is the chain-of-thought? <!--anki:787a345e6d216a737677-->
?
The **chain-of-thought prompting** gives or solicits intermediate steps before a response. It can help some reasoning tasks, with more than tokens and without guarantee of accuracy.

The written steps do not prove the validity of the result or the fidelity to the internal calculation. Depending on the model, its reasoning can remain internal: follow the intended mode of use and compare verifiable results rather than requiring a detailed trace. For an application, ask for the proofs, calculations or justifications useful for validation; tags do not make a correct conclusion.

---

What is the self-consistency? <!--anki:627b5e3844466e393e54-->
?
Sample several solutions, **extract comparable final answers**, And then add them up. Often by voting. Different paths can lead to the same answer. The cost increases with attempts.

The majority can repeat an error common to the model or the prompt. Draws that are conditionally independent given the prompt do not imply independent errors about the real world. For free text, define first a normalization or a reliable comparison; the raw text vote is not enough. Measure the gain on validation and provide for the treatment of equalities and abstentions.

---

Why structure prompts with delimiters (XML, Markdown)? <!--anki:7264742c537b4b63536f-->
?
The **delimiters** make the roles of blocks more readable: instruction, document, example, or question. They help design a verifiable prompt, but do not create a security boundary.
```xml
<documents><doc id="7">Data to analyze...</doc></documents>
<question>Does the document authorize this reimbursement?</question>
```
A document can itself contain hostile instructions or tags. Using the available structured roles and controlling actions in the application. Placing the stable prefix before the variable data can help the cache, provided you maintain clarity and measure quality.

---

In a prompt, is it better to formulate the instructions positively or negatively? <!--anki:42213a39796140435942-->
?
Preferring an explicit **expected action**, accompanied by an example: "Returns a JSON object with `status` and `reason`" is more operational than "Do not write prose". A prohibition remains useful to name a limit, but you must indicate the replacement conduct: "If the source is missing, indicate that you do not know".

It is not a law on negations: compare the formulations on representative cases. For a strict format, also use a schema and an application validation.

---

When to break down a task into multiple calls? <!--anki:6b42553f48776d65447e-->
?
Break down when subtasks have separate **inputs, outputs and verifiable criteria**: extraction, translation, then synthesis, for example. This facilitates diagnosis and allows models to be adapted at each stage.

Decomposition does not automatically improve reliability: an extraction error can contaminate all the following steps. Provide validation of interfaces, failure processing and overall budget. Compare to a baseline in one call on the same tasks, with cost and latency. Keep several calls only if their control or measured gain justifies the complexity.

---

What is meta-prompting? <!--anki:622b53787c656f4c5f41-->
?
Use a **LLM to generate or improve prompts**: review an existing prompt, propose variants, write a first draft from a job description.

Useful to start or to detect ambiguities, but a variant is only retained if it **measures better** on the eval set ([[92-chainforge-evals-prompts|evals]]). To go further, automatic optimization makes this loop systematic ([[12-automatic-prompt-optimization|DSPy]]).

Example: ask for three rephrases of an extraction instruction, then compare the fields actually extracted. The self-assessment "this prompt is clearer" does not replace this test.

---

Why treat prompts like code? <!--anki:736c4f6a3c5d3021267c-->
?
Because they **determine the behavior in production** as much as the code, and a change in a word can degrade a case category.
- **Versioning** and history of changes
- **Regression tests** on a golden dataset before each deployment
- **Review** by a peer
- **Rollback** rapide

For example, a "respond briefly" command can remove much-needed reservations; associating each result with the prompt version and the model isolates this regression rather than assigning it to chance.

See [[13-production-prompts|Prompt in production]] and [[91-langfuse-observability|prompt management]].

---

Which common anti-patterns for writing prompts? <!--anki:7621382e254d7e3f6163-->
?
Prompt **fur-all**, examples **contradictory** with instructions, unsorted context, — redundancies and request a strict format instead of the **[[63-guided-generation|contraindre]]**.

They make the task ambiguous: the model must arbitrate between incompatible objectives or seek useful information in noise. **Separate objective, data and expected format**, harmonize examples, then test limit cases. A long prompt is not bad in itself; each party must contribute to verifiable behavior.

---

Why don’t nine identical answers out of ten prints of a LLM demonstrate an accuracy of 90%? <!--anki:6663336562623738313739613466386438376435343663663461626362633761-->
?
The number here measures one **Agreement Between Draws**, without the truth ground. A prompt containing a false premise or common flaw in the model can produce the same error nine times.

Majority voting can improve a task when errors compensate, but its gain is verified on annotated cases independent of the setting. Control the normalization of responses, the cost of ten generations and cases where the vote is mistaken with confidence. To announce a probability of correction, it is necessary to validate the calibration of the agreement score.

---

How to use metamorphic tests to check the robustness of a prompt? <!--anki:6433386631383831653636363437633062363537653538643563393234336639-->
?
A metamorphic **test** transforms an input while knowing the expected relationship between outputs. For example, changing the order of two invoices must swap the corresponding extractions without changing their amounts.

Test paraphrases, spaces, order of examples and addition of unrelated information. Define the property before the test and verify that the transformation retains the meaning. A negation or a change of currency should not keep the answer. These tests reveal weaknesses without being in themselves a proof of accuracy.

---

How does an ablation tell which prompt instructions are useful? <!--anki:6662663636333839346136663434613761333235366238633838326231373266-->
?
A **removal removes a single component**: role, example, rule or document block. Comparing outputs on the same inputs, with multiple prints if necessary, allows to estimate its contribution.

If removing the role does not change anything but removing an example degrades ambiguous cases, keep this example as a priority. The absence of an average gain is not enough: controlling critical errors. The interactions between components then require retesting the complete simplified prompt.

---

## Scenarios

Scenario: A prompt of 400 lines handles the extraction, translation and summary of contracts. It works at 70% and each correction breaks another part. How do you resume the subject? <!--anki:4e3842703a752847257c-->
?
1. **Measure before touch**: a golden dataset of representative contracts and subtask valuations, to find out what really fails ([[92-chainforge-evals-prompts|evals]])
2. **Remove**: Extract → translate → summarize, into three unit testable calls, rather than one mega-prompt
3. **Constrict the output** of the extraction step by a schema rather than by a format setpoint ([[63-guided-generation|guided generation]])
4. **Clean**: delimiters between instructions, data and examples, positive instructions, examples that are consistent with each other
5. **Version and test** each change as code, with rollback possible ([[91-langfuse-observability|prompt management]])

**Trap**: Rewrite the prompt of a block without a test set, and randomly move the quality.

---

Scenario: your ticket classifier has 92% accuracy but the support team wants 97%. You can increase the cost per ticket. What are you testing, and in what order? <!--anki:70302e6d375b4b3b7723-->
?
1. **Analyse errors**: Do 8%s look like class definition problems, missing examples, or ambiguous tickets?
2. **Few-shot targeted**: add examples of cases confused, consistent with the instructions
3. **Self-consistency**: several reasonings and majority vote, or a stronger model on doubtful cases ([[82-routing-llm|cascade]])
4. **Abstention**: Return low-trust cases to a human rather than forcing a class ([[65-probabilities-sampling|logprobs]])
5. **Check the ceiling**: If two human annotators disagree on these tickets, 97% may not be reachable

**Strap**: Stack techniques without measuring the input of each on the same test set.

---

## Sources

- [Wei et al. — chain-of-thought prompting](https://arxiv.org/abs/2201.11903)
- [Wang et al — self-consistency](https://arxiv.org/abs/2203.11171)
- [Turpin et al. — explanation fidelity limits](https://arxiv.org/abs/2305.04388)

- 14 November 2026 — Position and context selection: [Liu et al. — Lost in the Middle](https://arxiv.org/abs/2307.03172).

## Connections
- [[92-chainforge-evals-prompts|ChainForge & evals]] — test systematically
- [[35-context-engineering|Context engineering]] — the prompt in its global budget
- [[63-guided-generation|Guided generation]] — guarantee rather than ask
- [[91-langfuse-observability|Langfuse]] — Quick Versions
- [[21-rag-fundamentals|RAG]] — when the prompt is no longer enough
- [[65-probabilities-sampling|Probability & sampling]] — temperature, top-p and self-consistency
- [[138-reasoning-models|Models of Reasoning]] — when the chain-of-thought is native
- [[143-hallucinations-grounding|Hallucinations & grounding]] — abstention and quotes
- [[12-automatic-prompt-optimization|Automatic optimization of prompts]] — let a metric choose the formulation
- [[13-production-prompts|Prompt in production]] — structure, versioning and portability
- [[51-fine-tuning-adaptation|Fine-tuning]] — distinguish examples in prompt and weight adjustment
- [[00-moc-ai-engineering|MOC AI Engineering]]
