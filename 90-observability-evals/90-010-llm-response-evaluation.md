# Evaluating LLM outputs & responses — Flashcards
Tags: #flashcards #ai-engineering #evals #responses #quality #llm
<!-- summary: grid by dimension, accuracy and completeness, relevance and guidance, multiple references, standardization, BLUE and RED, BERTScore, summaries, numerical responses, blocking criteria and aggregation by affirmation, validation of affirmations and style, numerical tolerance, weighted coverage, empty fields, extracted list, unparsable outputs. -->


How to define a grid for evaluating a LLM response? <!--anki:6631303738646665313965663463613262386165393030353031373061313738-->
?
From the **request and the task contract**, and then define observable criteria: exact result, elements requested present, instructions respected and limits of the evidence announced. For each criterion, specify the necessary data, the auditor and success or failure cases.

Keep dimensions separate: a clear answer may be wrong, an exact answer may be incomplete. Identify blocking criteria before noting the style. The [[94-evals-methodology|Methodology]] organizes the test set; a [[95-llm-as-judge|judge]] must be validated for the topic used.

---

Do not confuse: Accuracy of affirmations and completeness of a response? <!--anki:6266653465333165663233333465633538643032353065313035343032336362-->
?
The **Accuracy** examines whether the statements made are correct in the light of reliable references. The **Completeness** examines whether the response addresses the necessary elements of the request.

To "give status, confirmed cause and next point", answer only with the time of the next point can be accurate and incomplete. Define the elements expected before the evaluation; a lack of evidence must be able to be explicitly announced. Length does not measure completeness, and an empty answer does not become useful because it contains no factual errors.

---

Do not confuse: relevance and respect for the instructions of a response? <!--anki:3931316634333135373630353434646562383539613139656664383430353062-->
?
**Relevance** measures whether the response meets the expressed need. **Respect for instructions** checks for explicit constraints: language, length, structure or perimeter of authorized information.

A relevant answer of 500 words fails at a limit of 100 words. A French text of 80 words can meet these constraints while answering another question. Define a counting rule and anchor examples; do not give a mechanical property the meaning of a complete business success.

Publish the two criteria separately: Optimizing brevity should not remove a reserve essential to the decision.

---

Why can a single reference answer penalize correct answers? <!--anki:3266306332623938643062353464306338383233363036323065356538656431-->
?
A textual reference often illustrates **one formulation among several**. An exact raw match then rejects a correct paraphrase or other reasoning leading to the same result.

For an open question, annotate required facts, permissible formulations and prohibited contradictions, or use multiple reread references. For a truly unique target, such as an identifier, keep a strict comparison. A semantic judge can help but must be validated; multiplying references does not turn erroneous information into truth.

"0.5" and "50%" can be equivalent; two nearby client identifiers are not. Standardize according to the response type.

---

When to normalize an exit before an exact match? <!--anki:3631313133633933373165323436353362613163376334393534353436626236-->
?
Only if the **contract defines an equivalence**: non-significant spaces, JSON key order, or allowed decimal notation. Version this rule with the evaluation.

Example: `1,00 EUR` and `1 EUR` may be equivalent; `1 USD` is not. In a JSON structure, `true` and `1` are not interchangeable simply because a language compares them as equal.

Parse with strict validation, then compare types, units and values. Preserve order of lists when counting, negations, signs and relevant time zones. Also test outputs that **must remain different**: too permissive normalization turns real errors into success of exact match.

---

What do BLUE and RED measure, and when to use them? <!--anki:3939396430383565306332373439663238313263656535623739333735396635-->
?
**BLUE** combines modified precisions of n-grams with a brevity penalty, historically for translation. **RED** compares common units with reference summaries; RED-N uses n-grams and RED-L uses common subsequences.

These scores measure an overlap with references, not directly truth, security or business utility. Set variant, tokenization, references and aggregation; a corpus BLUE does not merge with an average of scores per sentence. Use them as complementary signals on a validated task, with control of facts and omissions.

---

Why is BERTScore not enough to verify the accuracy of an answer? <!--anki:3966386639396665323464303464633461386563666536613562666666386564-->
?
**BERTScore** compares candidate and reference by similarities between embeddings contextual tokens. It can recognize lexical variants that exact overlap penalizes.

A high similarity does not prove that dates, numbers or entities are correct. The original article presents a confusion between Monday and Tuesday that the metric detects wrong. Control these values against a reliable reference and validate the metric on the errors of the task. Set embeddings model, configuration and language; no universal threshold certifies a factual response.

---

How to evaluate verifiable instructions without confusing them with business quality? <!--anki:3463656462333761376565653439663139346162663361656131363962363433-->
?
Turn each explicit constraint into **documented checker**: number of words, presence of sections, schema or list allowed. **IFEval** illustrates this approach with automatically verifiable instructions.

Also test the checker on limit cases: titles, compound words or quotes can change the count. Publish respect by constraint and joint respect. A text that repeats a requested word can pass this control while being false or useless; semantic criteria require their own proof. A contradictory or impossible instruction must be treated according to an announced rule.

---

How to evaluate a summary produced by a LLM? <!--anki:3438623531356165643333393464623538346431643264353137373533393164-->
?
Verify separately **fact preservation**, cover essentials for use and presentation constraints. Annotate the necessary information before reading the summary, allowing multiple formulations.

Controlling numbers, dates, actors, causation and uncertainty: "suspected cause" does not become "confirmed cause". Look for unsupported additions and omissions that change a decision. A RED score may complete the comparison, but a repeat of the same words does not prove fidelity. Adapt the selection of information to the length and purpose of the summary.

---

What to check in a digital response of a LLM? <!--anki:3863663331626135333439343464623462633938633766623138613733623237-->
?
Compare **value, unit, sign, period and perimeter**, then check assumptions and rounding. For x values and a reference r, a possible rule is `|x-r| ≤ atol + rtol × |r|`, with tolerances set before the valuation.

Close to zero, the absolute component avoids an inappropriate relative tolerance. The rule chosen depends on the contract, not on a universal constant.

`100 g` and `0,1 kg` can be equivalent after authorized conversion; `100 kg` is false. For amounts, use decimal or whole currency units as needed, without erasing currency or sign.

---

Why can an average score hide an unacceptable response? <!--anki:3063346366393362343866303465366539343732383936383262626162383738-->
?
An average allows a **compensation between dimensions**: excellent style and structure can hide a false amount or revealed private data. Define blocking criteria before comparing variants.

Example: Nine exact assertions and one false critical deadline give 90% accuracy per assertion, but the answer remains inadmissible.

Publish profile by dimension, critical violations and fraction of responses meeting all required criteria. A weighted score can classify eligible responses without undoing a blocking failure. Also measure segments: a favorable average can hide an underserved population.

---

How to deal with an empty answer, a refusal and an unverifiable affirmation in an eval? <!--anki:6466313737363932633336363462313238376162393238306534316566386138-->
?
The verdict depends on the **task and available evidence**. An expected refusal on a prohibited request may succeed; an empty answer on a feasible request fails in utility or completeness.

An assertion without accessible evidence is not automatically false in the world. It can nevertheless violate a contract imposing a context-supported response. Distinguish between unsupported information, contradiction and impossible verification, and then define their treatment. Publish denominators and do not silently exclude difficult cases. See [[143-hallucinations-grounding|Grounding and Abstention]].

---

Calculation: A contains a sustained statement on one; B contains five out of nine. What scores are obtained with an average per response and then a grouping of all the statements, without weighting gravity? <!--anki:3731313532356461626432643465636139383333643434373066643234363165-->
?
The two aggregates answer different questions:
```text
Average response: (1/1 + 5/9) / 2 = 7/9 ≈ 77.8%
regroupement        : (1 + 5) / (1 + 9) = 6/10 = 60 %
```
The first gives the same weight to each answer; the second gives the same weight to each affirmation and more to long answers. Fix the granularity of cutting and processing of answers without affirmation. No score measures the expected information but omitted, nor makes acceptable a critical error. See [[96-evals-rag-agents|Assessment of evidence]].

---

Why evaluate the assertions of a response separately from its style? <!--anki:3564386539316363616131363436636262383339336265366162346539636461-->
?
A fluid **response** may contain a single false statement that is sufficient to make the decision dangerous. An overall style or utility score may mask this error.

Break down verifiable claims, associate each with proof, and distinguish between accuracy, coverage, and presentation. Weighting errors according to their consequence without hiding their number. For example, the date and amount of a refund require specific control. Keeping a full answer score: counting only the correct sentences can reward a very short answer that avoids all difficult parts.

---

How do you score an extracted field when the reference or the prediction is empty? <!--anki:3738393832353037623336323465613061303638356133373535343639613331-->
?
Distinguish **four cases**, which have neither the same meaning nor the same cost:
- empty reference, empty prediction: **correct abstention**;
- empty reference, predicted value: **invention**, often the most dangerous;
- reference value, empty prediction: **omission**, which sends the document to review;
- two different values: **value error**.

Count them separately, field by field. A single accuracy score that treats empty as an ordinary value rewards a model that abstains everywhere on often-empty fields. Document-level accuracy completes this tracking ([[161-vision-language-models|extraction by a VLM]]).

---

Calculation: an invoice has five reference lines. The model extracts four, three of which match a reference line. What are the precision, recall and F1 of the extracted list? <!--anki:6435326463366233373933653461326661333232386139643632383735336361-->
?
```text
precision = 3 / 4 = 75%
recall    = 3 / 5 = 60%
F1        = 2 × 0.75 × 0.60 / (0.75 + 0.60) ≈ 66.7%
```
Precision measures the share of extracted lines that are correct; recall, the share of invoice lines retrieved. The result depends on the **matching rule**: exact amount, normalized label, rounding tolerance. Set it before the eval, and match each reference line at most once; otherwise a line duplicated by the model counts twice as correct.

---

Calculation: out of 1,000 eval cases, 50 outputs fail to parse and 855 of the other 950 are correct. What score do you report? <!--anki:3133383766363664613432623463643561306365376632663835656136326634-->
?
```text
accuracy over all cases        = 855 / 1,000 = 85.5%
format validity                = 950 / 1,000 = 95%
accuracy among parsed outputs  = 855 / 950   = 90%
```
Report **85.5%** as the main score: an unreadable output is a system failure. The other two figures explain where the loss comes from. Removing the 50 cases from the denominator inflates the score and hides a format regression. Only an error unrelated to the model, such as a provider outage, justifies rerunning a case rather than counting it as wrong.

---

## Scenarios

Scenario: a new summary takes more of the words in the reference and gets a better RED, but reverses the due date. How do you decide if it is better? <!--anki:6366633431363630303137303434386362636462646433383031326337323335-->
?
1. **Check the date** against the trusted source, with the required time zone and perimeter.
2. **Classify the error** according to the contract: a false operational deadline can be blocking.
3. **Measure separately** Loyalty, essential information and presentation on the same cases.
4. **Compare regressions** and their severity, with suitable repetitions and uncertainty.
5. **Promote only** if the required criteria are met; the lexical gain remains a complementary signal.

**Trap**: Allowing an increase in the recovery score compensates for a critical factual error.

---

Scenario: an answer correctly gives the time of the next point, but the question also asked the status of the ticket and its confirmed cause. Your accuracy judge gives it pass. What do you complete? <!--anki:6539353432356461363838613464616439323662363431656566373636633333-->
?
1. **Decompose the application** in three expected elements, annotated before judgements.
2. **Evaluate completeness** separately from the accuracy of the statements made.
3. **Allow an explicit limit**: if the cause is unknown, "no confirmed cause" responds to this element without inventing.
4. **Validate the grid** on complete, partial, contradictory and empty answers.
5. **Replay independent testing** and publish both dimensions as well as joint compliance.

**Trap**: Make the accuracy judge more severe without giving him a criterion for omissions.

---

Scenario: the contract imposes an amount in euros. An exact match rejects "1 €" and "100 euro cents" against "1.00 EUR", while a normalization deleting currencies accepts "1.00 USD". How do you correct the appraiser? <!--anki:3731663835303930326565303465613661623131323165323236393238333435-->
?
1. **Definite the equivalences** allowed by the contract, without changing the rule after reading the scores.
2. **Extract value and currency**, with separate status in case of impossible parsing.
3. **Convert authorized units** with currency and digital representation.
4. **Positive and negative test**: valid paraphrases, wrong currency, reverse sign and wrong amount.
5. **Compare typed values**, then check other response criteria on an independent test.

**Trap**: Choose a normalization that maximizes the score by removing the information needed to detect an error.

---

## Sources

- [Papineni et al — BLEU](https://aclanthology.org/P02-1040.pdf)
- [Lin — ROUGE](https://aclanthology.org/W04-1013.pdf)
- [Zhang et al. — BERTScore and limits on factual errors](https://arxiv.org/abs/1904.09675)
- [Zhou et al. — IFEval and verifiable instructions](https://arxiv.org/abs/2311.07911)
- [Min et al. — FactScore and atomic precision](https://arxiv.org/abs/2305.14251)

## Connections
- [[94-evals-methodology|Evaluation methodology]] — games, criteria, references and decisions
- [[95-llm-as-judge|LLM-as-a-judge]] — validate grid semantic evaluators
- [[96-evals-rag-agents|RAG & Agent Ratings]] — proofs, quotes and business result
- [[92-chainforge-evals-prompts|Evaluation of prompts]] — assertions and output comparison
- [[63-guided-generation|Structured Outputs]] — separate format, schema and business values
- [[143-hallucinations-grounding|Grounding & abstention]] — limits of evidence and partial responses
- [[00-moc-ai-engineering|MOC AI Engineering]]
