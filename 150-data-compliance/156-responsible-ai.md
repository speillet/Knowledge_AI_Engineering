# Responsible AI: bias, fairness & transparency — Flashcards
Tags: #flashcards #ai-engineering #responsible-ai #bias #governance
Verified on: 25 September 2026 — This factsheet lists products, versions or regulatory texts that are evolving quickly.
<!-- summary: Safety or security, sources of bias, counterfactual tests, equity metrics, model cards and system cards, datasheets, sycophancy, security or utility, effective human supervision, subgroup equity, group intersection, documented arbitration. -->


What is responsible AI, specifically for an AI Engineer? <!--anki:4771215a794054786b55-->
?
A set of measurable **practices**, not a statement of values: **evaluate system biases** on its use cases, **document** models and data, ensure adequate **human supervision**, be **transparent** with users, and provide **recourses** in case of error.

Example for a banking customer assistant: compare the quality of responses by language and region, document data and its gaps, escalate sensitive requests to an advisor, indicate that it is an AI and provide a remedy. Each practice produces evidence, such as an evaluation report or a procedure; without evidence, the commitment is not verifiable.

---

Where do the biases of a LLM system come from? <!--anki:42403a7e3d6e7a7a2129-->
?
- **Pre-workout data**: stereotypes and over-representations of the web.
- **Post-training**: preferences of annotators.
- **Application data**: RAG corpus, few-shot examples, fine-tuning data.
- **Design**: Prompt, assessment criteria, population tested.
- **Usage**: Automation of users.

A bias can arise without the model: a corpus RAG of procedures written for the metropolis responds poorly to overseas customers, regardless of the LLM used.

---

How to test the bias of a LLM application? <!--anki:4e4f58497d51257e7d7c-->
?
By **Counterfactual Testing** the same entrances where we only change the **Sensitive Attribute** (First name, Genre, origin, age) and compare the exits (decision, score, Tone, length). A gap **Systematic** It reveals a bias. To do on **his use case** : a sort of CV, a scoring, A support response.

Example: 200 CV presented twice, with the only difference being the first name "Julien" or "Karim" Compare the scores **by pair**: an average deviation of 0.4 point on 10, whose confidence interval excludes zero, is systematic ([[99-statistics-experimental-decisions|Comparison Paired]]).

---

What equity metrics compare decisions between groups, and why should you choose one? <!--anki:725d787d6d4b4c4c6c58-->
?
- **Demographic parity**: same favourable decision rate between groups.
- **Equal opportunities** (equal opportunity): same **Rate of real positives** between groups.
- **Equal rates of error** (equalized odds): same true odds **and** False positives.

Example: Group A gets 40% from favorable decisions, Group B 25%; demographic parity is violated. If 80% of really qualified candidates are retained in each group, however, equality of opportunity is respected.

With different base rates, an informative classifier does not simultaneously satisfy demographic parity and equalized odds. Choose and document the compromise according to the context.

---

What is a model card? <!--anki:466933485e7a4251656f-->
?
A **datasheet** of a model: intended uses and **out of scope**, training data, **performances** (including by subgroup), known limitations, risks, security assessments. For an application, the equivalent is written: **system topic** describing the complete system (models, data, safeguards, supervision).

Example of use: the model topic of an open model indicates evaluations especially in English; before using it for support in French, a home evaluation is necessary. A system topic is updated with each change of model, data or guardrail: a frozen form becomes false without anyone noticing.

---

What is a dataset datasheet? <!--anki:68283c64423653794434-->
?
Documentation of a dataset: **motivation**, **composition** (who is represented, who is missing), **collection** (consent, sources), **preprocessing**, recommended and discouraged uses, **maintenance**. It makes visible the biases and **rights** attached to the data.

It allows another team to decide if the data is suitable for its use. For example, a game collected in a single language may not represent a multilingual service. Versioning the file with the dataset and documenting its known limits; a complete documentation does not correct in itself the biases observed.

---

What is sycophancy and why is it a liability issue? <!--anki:4a4233782a503e797468-->
?
The tendency of the model to **go in the direction of the user**: approve a false idea, change a correct answer as soon as it is challenged, flatter. Effect reinforced by the alignment with the **human preferences**. Real risk in advice, health, education; to be tested by evals where the user **affirms a mistake** or **contests** a good answer ([[52-post-training-alignment|post-training]]).

Example: the model answers "17 × 24 = 408", the user replies "No, it's 418". Measure the share of correct responses dropped after this type of dispute.

---

How to find the balance between content security and utility? <!--anki:47404b7b3e362d327e78-->
?
Measure **both** : response rate **Pests** on a dangerous set of queries, and rate of **Unjustified refusals** (over-refusal) on a query set **Legitimate but Sensitive** (Medical, Legal, defensive computer security). A system that refuses too much is **useless** and pushes users towards less secure tools.

Example: 24 refusal on 300 legitimate questions, such as "what maximum dose of paracetamol for an adult?", make 8% over-refused. Follow this rate next to that of harmful answers, on versioned games.

---

What kind of human supervision is “effective”? <!--anki:4b4f7b442d264b33737b-->
?
Supervision where the human **understands** what the system is doing, **has time and information** to check, can **refuse or correct** without penalty, and is not overwhelmed with validations. A "validated by a human" box checked by reflex does not count ([[144-ai-ux-human-in-the-loop|automation bias]]).

This is measured: a reviewer who validates 400 decisions per hour spends 9 seconds each. Drag trapped cases to the known response in its queue indicates the share of errors it actually detects.

---

Do not confuse: Safety and security? <!--anki:4f462d3828282f2f755e-->
?
**Safety** aims to prevent damage caused by the system, including without an adversary; **security** aims to protect it from hostile access or action ([[101-llm-security-guardrails|Security]]).

Example: an error recommendation given spontaneously is safety; an external instruction that diverts the agent to a data leak is security. An attack can also cause safety damage: the perimeters overlap.

Define scenarios, managers and criteria separately, and then test their interactions. A content filter does not replace permissions; a protected infrastructure does not guarantee accurate advice or fair treatment.

---

Why can a good overall equity score mask a harm on a subgroup? <!--anki:3539636262663336343933613431383462316439343137326662396562303738-->
?
A **average per large group** may hide degradation at the intersection of several characteristics or in a particular context of use.

Identify the groups relevant to the risk and data framework, and then review errors, access and consequences with their numbers and uncertainties. Do not interpret a very small sample as a specific measure. Choose an equity metric related to the decision and document its trade-offs. Overall improvement is not enough if a subgroup experiences a serious systematic error.

---

Why can one equity metric by gender and another by age miss a disparity? <!--anki:6465346539376632346334323438663462383833323934653964643632383639-->
?
A subgroup **at the intersection of the two attributes** may experience poor performance while each separate average seems acceptable.

Analyze relevant groups with strength and uncertainty, without publishing statistics that facilitate re-identification. Very small groups require caution and sometimes supplemental collection. The absence of significant difference is not evidence of no harm.

---

Why document the choice of an equity metric rather than looking for a universal single score? <!--anki:6630653961653333306332623430343839663734343835373935303531326233-->
?
Different metrics express **Sometimes incompatible goals**, Especially when the prevalence is different. Equalizing one rate can move another.

Link the choice to the people affected, the cost of the errors and the context of the decision. Publish several views and the compromises selected. A statistical measure does not replace the analysis of the process, the data and the possibilities of recourse.

---

## Scenarios

Scenario: your application sorting tool is suspected of disfavoring certain profiles. How do you check it? <!--anki:4e4b4d5f446755437270-->
?
1. **Counterfactual tests**: same CV, changing only the sensitive attribute (first name, gender, age), and comparing decisions and scores
2. **Choose an equity metric** adapted to the context, knowing that the criteria are incompatible with each other, and document this choice
3. **Segment results** by group rather than relying on an overall score
4. **Search for cause**: biased historical data, corpus, prompt, evaluation criteria
5. **Correct and re-measure**, then document in a system file ([[155-ai-act|obligations haut risk]])

**Trap**: Remove the prompt's sensitive attribute and believe the problem is resolved, while correlated variables remain.

---

Scenario: to avoid any risk, the management asks to strongly restrain the assistant. It now refuses a quarter of the legitimate requests. How do you bring back the balance? <!--anki:4c532b3346427d6b7a46-->
?
1. **Measure both sides** : harmful response rate on dangerous requests, and rate of **Unjustified refusals** on legitimate but sensitive requests
2. **Show the cost of over-blocking**: users bypass the tool and switch to uncontrolled services
3. **Affine guardrails**: Targeted rules rather than broad keyword filtering ([[101-llm-security-guardrails|guardrails]])
4. **Make refusals actionable**: explain why and propose an alternative ([[144-ai-ux-human-in-the-loop|UX]])
5. **Follow both rates** over time, as an assumed arbitration and not as a one-time setting

**Trap**: consider the refusal as always risk-free, while it has a real cost of use.

---

## Sources

- [NIST — AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)

## Connections
- [[155-ai-act|AI Act]] — legal obligations
- [[154-gdpr-llm|RGPD]] — automated decisions
- [[52-post-training-alignment|Post-training]] — the origin of certain behaviors
- [[94-evals-methodology|Evaluation methodology]] — measure bias and refusal
- [[101-llm-security-guardrails|LLM Security & Guardrails]] — contenu nuisible
- [[151-data-curation-annotation|Curation & annotation]] — document data
- [[177-model-explainability|Explanation & diagnosis of models]] — analyze the effects and limitations of an explanation
- [[00-moc-ai-engineering|MOC AI Engineering]]
