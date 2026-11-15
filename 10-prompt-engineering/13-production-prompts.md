# Prompts in production — Flashcards
Tags: #flashcards #ai-engineering #prompt-engineering #production #llm
<!-- summary: Prompt bricks, placement of long documents, reasoned instructions, role limits, prompt a reasoning model, templates and user data, registry and versioning, prompt in the code or in a registry, portability between models, language, length control, migration of the output contract, effective rendering, missing data. -->


What are the bricks of a production prompt? <!--anki:775f2e70434e484c4021-->
?
1. **Role and perimeter**: who answers, for whom, what is off topic
2. **Context**: documents, user data, conversation status
3. **Task and success criteria**: what is a good answer
4. **Contracts**: tone, length, business rules, driving in case of doubt
5. **Output format**, ideally constrained ([[63-guided-generation|guided generation]])

**Examples** come in addition, when the expected format or judgment is difficult to describe.

---

Where to put long documents in a prompt? <!--anki:635d604a5d2428323726-->
?
**Test documents then question**, without making it a universal rule: the effect depends on the model, the task and the position of the proof ([[137-long-context|lost in the middle]]).

Compare the same questions with the proof at the beginning, middle and end, at a constant length. For the [[123-aggressive-caching|cache]], only a truly identical prefix is reusable: a document that changes with each call does not become hideable because it is placed in the lead.

---

Why explain the **why** of a deposit? <!--anki:443d7560577e47674929-->
?
Explaining the objective helps the model to **adapt the instruction to cases not explicitly listed**. For example, "the answer will be read by a speech synthesis" gives a reason to prefer simple sentences and avoid tables or symbols that are difficult to pronounce.

This motivation does not guarantee compliance with the format. Associate the why with observable constraints, such as the absence of a table, and then test representative entries. If a requirement is imperative, validate it in the application: the model can misinterpret a justification or favor another instruction.

---

Why is “You are an expert in...” not enough? <!--anki:70402569663046525a73-->
?
A **role** guides the **tone and the register**; it does not add verified data or guaranteed competence. Above all, provide the **context**, the **success criteria** and the **examples**.

"Credit Analyst" remains insufficient without a balance sheet, period and calculation rules. "Calculate the debt/income ratio with the values provided; report any missing data" gives verifiable behavior. Comparing results with and without role on the same files: the effect of a persona on accuracy depends on the model and the task, not the prestige of the title.

---

How to speed up a reasoning model? <!--anki:725b7449614f33655476-->
?
Describe **objective, constraints and verifiable criteria**; do not assume that a long procedure always improves a [[138-reasoning-models|Model of Reasoning]]. Keep the required business steps and consistent examples.

Example: to compare two offers, provide the expected volume, the budget cap and the format of the expected table; ask for useful assumptions and calculations, not a transcription of its internal reflection. The formula "considered step by step" is not a universal prerequisite. Adjust the **reflection budget** on a case set: measure quality gain, cost and delay before increasing it.

---

How do I limit risk by injecting user data into a template? <!--anki:63687347434c42302e68-->
?
- **Describe** the data (XML tags) and say that what they contain is **not a statement**
- **Escape** or refuse the closing tags in the data, so that a user does not get out of his block
- Never **contain** a user entry in the system prompt
- Keep the template **under application control**: do not compile the user text as a template; insert it as data

This limits accidental injection, without replacing the defenses against voluntary injection ([[101-llm-security-guardrails|Security]]).

---

How do I version and deploy a prompt? <!--anki:45322d48647e3977733d-->
?
- **Register of Prompts** : each version is immutable and numbered, with **Labels** Environment (`staging`, `production`) ([[91-langfuse-observability|Langfuse]])
- The version is **tracked** with each response, to link a regression to a change
- **Eval gate** before moving the `production` label ([[112-model-cicd|CI/CD]])
- **Backward** by moving the label, without redeploying the code

The prompt, the model and its parameters are versioned **together**: a prompt only makes sense for a given model.

---

Do not confuse: prompt in the code and prompt in a registry? <!--anki:634257615e2a3559405e-->
?
- **In code** (Git): code review, testing, and deployment with the app. Simple, but every change requires delivery
- **In a registry**: modifiable by non-developers and deployable in minutes. But the prompt can change **without commit**, so it takes an eval gate and traces

Current choice: **code** for prompts coupled to logic, **register** for those that the trade often adjusts.

---

Why does a prompt not transfer as is from one model to another? <!--anki:6f3d475e6263602d6e31-->
?
Each model family has been trained with its own conventions: sensitivity to **tags**, **few-shot**, **majuscules** and insistent instructions, verbosity by default. A useful "TOU DOIS" instruction on an old model makes **over-react** a newer model more obedient.

Any model migration is treated as a **code change**: the complete eval is replayed ([[146-model-selection|migration]], [[12-automatic-prompt-optimization|recompilation]]).

---

Do I need to write the prompt in English for a French-speaking application? <!--anki:46342128794b4e28727b-->
?
**Not necessarily.** Recent models follow a lot of instructions in French. What matters:
- Explicitly say the **response language** (that of the user, or always the French)
- Keep **examples in the target language**: the model imitates their language
- **Measure** on its eval game both versions, in cost too: the number of tokens depends on the tokenizer and the formulation, not just the language ([[132-tokenization|tokenization]])

---

How to control the length of the answers? <!--anki:477e60346d663b39685b-->
?
- Give a concrete **target** (“3 sentences”, “less than 120 words”) rather than “be concise”
- Show **Examples** of the right length
- Fix `max_tokens` as **crab**, not as a setting: a cut produces a truncated response
- Monitor the **average length in production**, which drifts with model changes and weighs on cost and latency ([[121-inference-costs|costs]])

---

How to change the contract of exit of a prompt without breaking its consumers? <!--anki:3066623561633963316236663465616561663838316432386563373536343930-->
?
Treating the **output schema** as a versioned interface. Adding a required field, renaming a category, or changing the unit by an amount can break a consumer even if the prompt text seems little changed.

Have the new version accepted by consumers before producing it; validate schema and business rules of both versions during the transition. Associate each result to its version of contract and test the historical cases. Plan the return to a compatible combination of prompt, model and parser.

---

Why log an imprint of the prompt actually made in production? <!--anki:3366343964336161313136313434356539663664376433623533336362393662-->
?
The version of the template does not determine the entry alone: **variables, retrieved examples, document order and serialization rules** also intervene. A rendering imprint helps to distinguish two executions announced under the same version.

Also keep the versions of these components and the parameters useful for reproduction. A hash does not allow to reconstruct the text; store the necessary data according to the rules of confidentiality. Avoid systematically logging all raw prompts.

---

How should an extraction prompt treat an absent value without confusing it with zero? <!--anki:6635313136333832333237323464633538336464623662343237643662383435-->
?
Explicitly set **value found, absent and unreadable**, with proof when available. An invoice with no readable tax amount does not justify `taxe: 0`: zero affirms a value, while `null` can signal the absence.

Provide this contract in the diagram and in the examples, then test incomplete and contradictory documents. The consumer then decides if he can continue, request a part or transmit to a human; the model must not invent the default value.

---

## Scenarios

Scenario: A quick “minor” change pushed on Friday caused 15%’s satisfaction to drop over the weekend, and no one knows which version was running. What do you put in place? <!--anki:693f694d2a3d5d354c25-->
?
1. **Register versioned**: immutable versions, `production` label, change history
2. **Traceability**: the version of the prompt and model attached to each trace ([[91-langfuse-observability|traces]])
3. **Eval gate**: no label changes without passing the non-regression game ([[112-model-cicd|CI/CD]])
4. **Progressive deployment**: canary on 5% traffic, with satisfaction metrics monitored ([[97-evals-online-ab-testing|evals online]])
5. **Back in one click**: Re-move label, without re-deploying

**Trap**: consider a prompt as an innocuous configuration, editable without review.

---

Scenario: your assistant, who summarizes reports of 80 pages, regularly forgets the decisions made at the end of the document and sometimes answers in English. How do you pick up the prompt? <!--anki:4854264e543b60743843-->
?
1. **Reorder**: document at the top, instructions and question at the end, with a brief reminder of the task ([[137-long-context|long context]])
2. **Structure output**: a mandatory “decisions” section in the schema, to force their search
3. **Fix the language** explicitly and give the example output in French
4. **Measure** on 30 annotated reviews: decisions found and correct language
5. **Cut if needed**: extract decisions by section, then synthesize

**Trap**: add "DO NOT OPEN DECISIONS" in capital letters without changing the prompt structure.

---

## Connections
- [[11-advanced-prompt-engineering|Advanced Prompt Engineering]] — basic techniques
- [[12-automatic-prompt-optimization|Automatic optimization]] — generate prompts rather than write them
- [[35-context-engineering|Context engineering]] — prompt in context budget
- [[91-langfuse-observability|Langfuse]] — register and traceability
- [[112-model-cicd|CI/CD models]] — eval gate before production
- [[137-long-context|Long context]] — document placement
- [[138-reasoning-models|Models of Reasoning]] — prompt the lens, not the steps
- [[101-llm-security-guardrails|LLM Security]] — user data in templates
- [[90-012-langfuse-prompts-experiments|Langfuse — Prompts, datasets & experiences]] — release and promote contracts
- [[00-moc-ai-engineering|MOC AI Engineering]]
