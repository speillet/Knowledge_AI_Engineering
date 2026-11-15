# Hallucinations, grounding & abstention — Flashcards
Tags: #flashcards #ai-engineering #hallucinations #grounding #quality #llm
<!-- summary: types of hallucinations, levers, verified citations, abstention, arbitrage with coverage, detection, reporting of uncertainty; temperature and news, source conflicts, partial responses, actual citation and applicable evidence, granularity of citations, facts and recommendations. -->


What is a hallucination? <!--anki:43342c5e784379766728-->
?
An output **plausible but false or unsupported**: fact invented, non-existent quote, imaginary API function, wrong number. It comes from the very nature of the model, which generates **what is likely**, not **what is true**, and from a training that often rewards **respond rather than abstain**.

Examples include quoting an "article 12.4" missing from the supplied contract, or calling `df.to_markdown_table()`, a method that does not exist in pandas.

---

Do not confuse: Intrinsic and extrinsic hallucination? <!--anki:68752d663634387a247b-->
?
- **Intrinsic**: the output **contradicts** the source provided (summary that reverses a digit).
- **Extrinsic** : the exit **Addition** an Information **Absent** from the source, True or False — It is unverifiable from context.

Example: the source indicates a return time of 30 days. Replying "14 days" is intrinsic; adding "free return costs", whose source says nothing, is extrinsic.

In RAG, both are failures of **faithfulness** ([[96-evals-rag-agents|Evaluation]]).

---

What levers reduce hallucinations before generation? <!--anki:68515d5d3f282d2d4d76-->
?
Prepare relevant, applicable and authorized **evidence** via [[21-rag-fundamentals|RAG]] or tools, specify the scope of response and define abstention or partial response when evidence is missing.

Example: a tool result gives "250" without a unit; asking for a monetary conclusion pushes to complete missing information. Provide unit, date and provenance, or have it clarified before generation.

Reduce ambiguities and separate data/instructions. Constrained format facilitates control, but JSON and low temperature do not guarantee accuracy. Even a faithful response may be wrong if its source is; evaluate recovery, support assertions, and business truth separately.

---

What levers reduce hallucinations after generation? <!--anki:7749336061702e3c4131-->
?
1. **Mandatory quotes**, then **verified** on the code side.
2. **Verification** of the answer: judge, NLI, or business rules on amounts, dates and references.
3. **Scale** to a human when verification fails, rather than an unsubstantiated response.

Example of a business rule: extract each amount from the answer and verify that it appears in a quoted passage; otherwise, the sentence is removed or the answer goes through. These controls cost one more calculation or one more call per answer: focus them on risky statements, such as amounts, dates, deadlines and commitments.

---

What is abstention and why is it difficult? <!--anki:6d23262a5e6d66256b7c-->
?
The ability to respond **"I don't know"** or **“It’s not in the documents.”**. Difficult because the models are biased towards **Answer** ; We need the **Require explicitly**, Supply of **Examples** abstention, and the **Evaluate** with questions **No answer** in the test set (otherwise we optimize a system that never abstains).

Example of instruction: "If the documents do not contain the answer, answer exactly: I do not find this information in the documents provided." A fixed formula is easily counted in the evaluation.

---

How to arbitrate between abstention and coverage? <!--anki:762f2b51314c5a4a552a-->
?
Too many abstentions = system **useless**; too few = **false answers**. We measure both (response rate, accuracy of answers given) and choose the point according to the **cost of an error**: a medical or legal assistant must abstain more than a brainstorming tool.

Example: With a confidence threshold of 0.5, the system answers 90% questions with 88% accuracy; at 0.8, it answers 70% with 97%. The trade chooses the point according to the cost of an error and that of a non-response.

---

How to detect hallucination after generation? <!--anki:423a236456252a5e4e45-->
?
**Check statements against a reference source**: retrieved passages, structured data or business rules. A judge or textual inference model can help, but it must be evaluated on reliable annotations. The latter classifies the pair (quoted passage, sentence) as implication, neutrality or contradiction: "neutral" signals an unsubstantiated statement.

The discrepancy between the generations and the logprobs serve as triage signals, not evidence: multiple responses may repeat the same error, and a probable continuation may be false. Measure false positives and false negatives of the detector. In case of uncertainty, trigger abstention or review depending on the risk.

---

How to communicate uncertainty to the user? <!--anki:783a747339575a7d7537-->
?
- Show **sources** and allow to open them.
- Distinguish **what comes from the documents** from what is **deducted**.
- Report answers **to check** (weak trust, no source).
- Do not overpromise in the interface ("verified response" only if true).

Example: “Return time: 30 days [Terms and Conditions, § 4.2]. Return costs: not specified in the documents.” See [[144-ai-ux-human-in-the-loop|UX of AI]].

---

Why does a low temperature not guarantee the news of a LLM? <!--anki:6436363963323235643535633431616538653434343230393137643133366330-->
?
The temperature changes the **Distribution of Selection tokens**, Not the truth of the facts available. A very likely false answer can be reproduced with confidence at low temperatures: a model that wrongly associates Sydney with the capital of Australia will repeat it with each call.

A structured output eventually ensures a compliant format, not an exact figure. Measuring news on reliable references; providing adequate evidence, checking calculations with code, and predicting abstention when the source is missing. Reducing variability can help some tasks, but its effect on accuracy needs to be evaluated.

---

How to respond when two recovered sources contradict each other? <!--anki:6535366534346465373464653433323461663564393234363562343264616666-->
?
Apply a documented **priority rule** as required: reference source, applicable version, effective date and scope. The most recent source is not necessarily the one that applies to the requested case.

If the conflict remains unresolved, make it explicit and refrain from the contentious point or ask for clarification. Quote the passages concerned. Do not merge two incompatible digits or let the model choose the most plausible wording. Keep the versions used to allow diagnosis.

---

When is a partial response preferable to a complete abstention in RAG? <!--anki:3762666538376539333832323464316138336132366665326439636237313864-->
?
When certain parts are **supported and useful independently** of the missing information. Respond to these parts by citing their evidence and identifying precisely what remains unknown.

Example: the procedure describes the return time, but not the costs; give the time without inventing the tariff. If the missing information conditions the whole decision, a partial answer can be misleading: ask for precision or climb. Evaluate separately the usefulness of the answer and respect the limits of the context.

---

Why can't an existing citation justify the statement that precedes it? <!--anki:3563393233643462643064633463376138666562376238376237373263663536-->
?
A **citation valid** can point to a real document that does not support the announced detail: other period, Another population or simple hypothesis transformed into fact.

Check the correspondence between affirmation and passage, then its conditions of application. For example, a refund policy for individuals does not justify the delay of a contract. Distinguish direct proof, explicit deduction and missing information. Test close but incompatible documents. Control of the URL or page number guarantees the location, not the logical implication.

---

Why can a single quote at the end of a long paragraph mask hallucinations? <!--anki:3035353038353234386463613436383461376561616230663231613638636562-->
?
The reader may believe that the source supports **all statements**, whereas it justifies only one. Visual proximity is not a proof of detail.

Cut out the assertions and attach each citation to the passage it supports. Check entity, date, and scope. A correct citation may accompany incorrect extrapolation; mark the deductions and their assumptions.

---

Why separate established facts and recommendation in an assistant response? <!--anki:3235616265616538383066653438303362613832333136656338316437383031-->
?
A recommendation combines **evidence, objectives and arbitrations**; it is not a fact directly present in a source. Presenting it as such prevents the reader from examining the assumptions.

Indicate the facts used, the constraints and the reasons for the choice. When information is missing, make the advice conditional. Accurate sources do not guarantee that a recommendation is suitable for all contexts.

---

## Scenarios

Scenario: your document assistant cites pages that do not exist, and users lose confidence. How do you handle the problem? <!--anki:437050683d4d6b72512b-->
?
1. **Change what you ask for**: cite **passage identifiers** provided in the context, not titles or URLs that the model can invent
2. **Check the code side** that each cited identifier actually exists in the context
3. **Check support**: Is the sentence really supported by the quoted passage (judge or NLI)?
4. **Refusing to respond** rather than producing a response without a valid citation
5. **Measure**: Valid citation rate and reliability on a test set ([[96-evals-rag-agents|RAG evals]])

**Pip**: Display unverified citations, which create false trust worse than lack of source.

---

Scenario: The job requires your assistant to always answer, never “I don’t know.” How do you react? <!--anki:4d562b243a672470396c-->
?
1. **Explaining arbitration**: removing abstention means accepting false answers on questions outside the scope
2. **Count the cost of an error** in this area: legal or medical advice, or simple brainstorming?
3. **Measuring both dimensions**: response rate and accuracy of answers given
4. **Test with unanswered questions** in context, otherwise we optimize a system that never abstains
5. **Propose a compromise** Answer with one **mention of uncertainty** and sources, Or a human being.[[144-ai-ux-human-in-the-loop|UX]])

**Trap**: Address the issue with prompt instructions, without ever measuring the rate of unsupported responses.

---

Scenario: two documents give return times of 14 and 30 days, and the wizard systematically chooses 30. How do you fix this behavior? <!--anki:3637613436353566316337353432316438653533326162303064343263633036-->
?
1. **Identify the scope** of each document: product, country, version and effective date.
2. **Definite the applicable source**, with the trade, instead of choosing the most favorable time frame.
3. **Transmit this metadata** and a resolution rule to the system.
4. **Provide clarification or abstention** if the evidence does not allow a decision to be made.
5. **Test both regimes and conflict**, with quotations and verification of assertions.

**Strap**: Automatically choose the most recent document without checking its scope.

---

## Sources

- [Liu et al. — citation support and coverage](https://arxiv.org/abs/2304.09848)
- [Niu et al. — RAGTruth, hallucinations despite a recovered context](https://arxiv.org/abs/2401.00396)
- [Geifman & El-Yaniv — risk and coverage with abstention](https://proceedings.neurips.cc/paper/2017/hash/4a8423d5e91fda00bb7e46540e2b0cf1-Abstract.html)

## Connections
- [[90-010-llm-response-evaluation|Evaluation of responses]] — Accuracy, completeness and processing of non-verifiable information
- [[21-rag-fundamentals|RAG — Fundamentals]] — grounding and quotes
- [[96-evals-rag-agents|Evals of RAG]] — measure factfulness
- [[95-llm-as-judge|LLM-as-a-judge]] — detect after blow
- [[65-probabilities-sampling|Probability & sampling]] — logprobs and calibration
- [[101-llm-security-guardrails|Guardrails]] — output controls
- [[144-ai-ux-human-in-the-loop|UX of AI]] — show uncertainty
- [[11-advanced-prompt-engineering|Advanced Prompt Engineering]] — the basic techniques of the prompt
- [[26-text-to-sql|Text-to-SQL]] — answer numerical questions on tables
- [[27-search-agents-deep-research|Research agents]] — multi-step search, with quotes
- [[49-coding-agents|Code Agents]] — Use and Integrate Code Agents
- [[173-calibration-uncertainty-abstention|Calibration, uncertainty & abstention]] — not to confuse trust and truthfulness
- [[00-moc-ai-engineering|MOC AI Engineering]]
