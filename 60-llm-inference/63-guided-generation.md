# Guided generation (structured outputs) — Flashcards
Tags: #flashcards #ai-engineering #inference #structured-output #llm
<!-- summary: masking of logs, JSON Schema, regex and grammars, XGrammar and Outlines, structured outputs of API, JSON mode or structured outputs, business validation, explicit representation of missing information, refusal and schema, cross-constraints. -->


What is guided generation? <!--anki:574e547021574d687c-->
?
The **guided generation** restricts the tokens allowed during decoding to adhere to a supported grammar or schema: JSON, enumeration values, or specific language. The model chooses from the continuations that are still valid.

The guarantee relates to the **structure of an output completed under the conditions provided**. Refusal, error, truncation and unsupported constraints must be treated separately. A well-formed date or a numerical amount may remain false: business validation remains necessary.

---

How does guided generation technically constrain decoding? <!--anki:77513f6a2e546e395d69-->
?
At each decoding step, a **automator** (from the schema or grammar) calculates the tokens allowed; the others are **masked in the logs** (probability zeroed) before sampling.

```text
logs → mask (grammar status) → sampling → status update
```

For example, after an expected JSON key, the engine only allows tokens that are compatible with its value and the rest of the schema. The mask is updated every token, which can represent several characters. The schema must remain satisfying and its features must be supported by the engine.

---

Requesting JSON in the prompt or constraining it? <!--anki:7352453c3f755a7a7363-->
?
A "Response to JSON" instruction **orients** the generation, but can produce text around the object, missing fields or invalid syntax. Constrained decoding effectively restricts possible continuations.

Distinguish between **JSON valid** and **comply with schema**: A parsable object may have the wrong fields. Even in strict mode, check end status, rejections, and truncated outputs before parsing, and then apply business rules. A format constraint does not replace these controls.

---

What types of constraints can be applied to decoding a LLM? <!--anki:694a55557556246d483b-->
?
- **Select**: a value from a list (classification)
- **Regex** : dates, identifiants
- **JSON Schema**: Typed objects
- **Out-of-Context (CFG)**: SQL, DSL, code

Choose the minimum constraint that expresses the need. A date regex imposes a form but can accept a non-existent day; a SQL grammar does not impose access rights or a reasonable query cost. Test the constraints actually supported and complete with semantic validation on the application side.

---

Which guided generation engine depending on the server: vLLM or SGLang, llama.cpp, or a Python library? <!--anki:3533363362333633333436643465666461633639333739356631636532343066-->
?
- **vLLM and SGLang**: **XGrammar** by default, other optional engines (llguidance, Outlines)
- **llama.cpp**: grammars **GBNF**
- **In Python library**, around its own inference code: **Outlines**, lm-format-enforcer

The API owners expose only the JSON Schema: their engine is hidden.

Check the supported schema subset on the deployed version: unions, terminals, and regular expressions are not universal. Test a real schema, truncated output, and denial; the engine name does not guarantee identical processing.

---

How to get a guaranteed structured output with a proprietary API? <!--anki:6b4237606b477d4d3c74-->
?
Suppliers offer **structured outputs**: a JSON Schema (e.g. `response_format` type `json_schema` in strict mode at OpenAI, structured outputs at Anthropic) is provided and the API guarantees compliance.

The guarantee depends on the model, the mode chosen and the subset of JSON Schema accepted. Provide a branch for refusals and responses interrupted by the output limit. For a streamed stream, wait for the complete object before treating it as a valid result; fragments alone may be impossible to parse.

---

Is a valid output syntactically correct? <!--anki:49726331503b73342157-->
?
**No.** The constraint guarantees the **form**, not the **fond**: the values can be false or invented. It always requires a **business validation** (e.g. Pydantic, rules) and [[92-chainforge-evals-prompts|evals]].

For example, a JSON object with an amount of 120 is well typed but can contradict an invoice of 12 euros. Pydantic checks the declared constraints; only a comparison at the source or a business rule will detect certain factual errors. An external action must also verify the authorization, regardless of the validity of the JSON.

---

Can format constraint degrade the quality of a LLM response? <!--anki:7669615e6153286a544d-->
?
**Yes.** A schema that is too narrow can force a response when information is missing, or impose an order of generation that is unfavourable to the task.

Comparing several schemas on difficult examples and separating analysis and extraction if it brings a measured gain. Adding a `reasoning` field is not a universal recipe; a short justification or verifiable references are often more useful to the application.

---

What latency cost does guided generation add? <!--anki:4b3d5e5e4934672e2836-->
?
The constraint can add a **preparation of the schema or grammar**, then a calculation of the mask during the generation. Some engines cache the prepared structures and greatly optimize this work.

The additional cost depends on the complexity of the schema, the engine, the cache and the number of requests: it is not always negligible. Measure first call and subsequent calls separately, then check the throughput under load with the schemas actually used.

---

What is the link between guided generation and tool calling? <!--anki:727c60472d7655416165-->
?
The [[32-tool-calling|tool calling]] expresses an operation request; the **guided generation** can constrain the form of its arguments, often described by JSON Schema. These are two distinct mechanisms: not all calls are decoded under constraint.

Example: a schema imposes a positive integer for `amount_cents`; the model can produce `25` with 25 euros in mind. The syntax is correct, the business amount is not.

Validate effectively supported schema, units, authorization and consistency with the request before execution. A generation interrupted or a refusal must also be processed explicitly, without assuming that a strict mode always produces a full call.

---

Do not confuse: JSON mode and structured outputs? <!--anki:41673b782e4245765374-->
?
The **JSON mode** targets a parsable JSON; **structured outputs** additionally impose a supported schema. An object can be valid while having the wrong fields, or contain a false value despite a correct schema.

Choose the schema when the processing contract requires it, then check end status, refusal and truncation before exploiting the object. The guarantees vary according to engine and configuration. An "absent information" branch avoids forcing an invented value; business validation remains essential.

---

What happens if the generation reaches `max_tokens` in the middle of a constrained JSON? <!--anki:3731663364663939323734313431373261653832636436653336323231626565-->
?
The output is **truncated** and the JSON is invalid, despite the constraint: the guided generation ensures that each token **respects** the grammar, not that the generation **goes to the end**.

The answer indicates this (`finish_reason: "length"` or `stop_reason: "max_tokens"`). You must **check this field**, size `max_tokens` for the worst case, and limit the size of the schema (lists of maximum length).

Do not simply add a brace to "fix": fields may be missing or a value may be cut. Reject the incomplete result and restart under budget, or explicitly expose the failure to the consumer.

---

How to represent missing information without forcing an invention into a structured output? <!--anki:3130346635353232626539313463353039653464373832316366393237326666-->
?
Provide in the **output contract** an explicit state: absent, not applicable, ambiguous or impossible extraction, depending on the need. A mandatory field without representation of the unknown can cause the model to fill a plausible value.

For example, distinguish `amount: null` by an amount equal to zero and associate a controlled reason. Validate rejection, incomplete output, and conforming result separately; schema guarantees have conditions. A valid structure does not prove that the document contains the information or that the extracted value is correct.

---

Why predict a rejection state in a constrained output scheme? <!--anki:3531326435383766363035323463653538663239306535303964386137663663-->
?
If the schema still requires an affirmative answer, the model may be **forced to fill in fields without proof**. Provide an explicit "unavailable" or "opt-out" variant, with appropriate reason.

The consumer must treat this variant as a planned outcome. Also check for refusals and errors specific to the API, which may follow a contract other than the requested output. An eligible scheme does not guarantee that the useful answer exists.

---

Why doesn't a JSON grammar guarantee that start_date precedes end_date? <!--anki:3437316165623139306465363464653239613762343766353733353866363535-->
?
Grammar constrains especially **the form of authorized outputs**. A business relationship between fields requires appropriate validation, even if each date is syntactically valid.

Control the relationship after parsing and return a targeted error or abstention. Avoid automatic correction that reverses dates without proof. Supported JSON Schema subsets vary; do not assume that a declared constraint is actually applied by the engine.

---

## Scenarios

Scenario: Since you forced the output by a JSON Schema, the JSON is still valid but the answers have become less good. What do you correct? <!--anki:4b54485521782c4c4a72-->
?
1. **Replay the same cases** with and without constraint to isolate the regression.
2. **Search for faulty constraints**: mandatory field without proof, incomplete enumeration, ambiguous schema or truncated output.
3. **Allow abstention** and simplify unnecessary fields.
4. **Testing schema variants** or separate extraction, also measuring latency and cost.
5. **Comparing business accuracy** on an independent test; a justification field is only useful if its contribution is demonstrated.

**Trap**: Declare that the field order is the cause before checking for errors.

---

Scenario: your invoice extraction always returns a compliant JSON, but the accounting amounts are false. How do you secure the chain? <!--anki:4e243d382b5961484041-->
?
1. **Compare values to proofs**: invoice, page and area associated with the field.
2. **Apply business rules**: consistent lines, taxes, currency and dates.
3. **Allow an absent value** when the document does not contain proof.
4. **Validate the sorting of doubtful cases** on labels: logprobs or agreement between extractions are signals, not guarantees of truth.
5. **Measure by field and document**, with errors, abstentions and review cost.

**Trap**: Write an object whose format has only been verified.

---

## Sources

- [OpenAI — structured outputs, rejections and limits](https://developers.openai.com/api/docs/guides/structured-outputs) — targeted deepening of the 12 November 2026; educational examples are built for this review.

## Connections
- [[90-010-llm-response-evaluation|Evaluation of responses]] — check content beyond format and schema
- [[11-advanced-prompt-engineering|Prompt engineering]] — guarantee rather than ask
- [[32-tool-calling|Tool calling]] — arguments constrained by schema
- [[92-chainforge-evals-prompts|Evals]] — structured outputs easier to evaluate
- [[62-inference-optimizations|Inference optimizations]] — impact on decoding
- [[11-llm-inference-servers|Inference Servers]] — XGrammar integrated with vLLM
- [[65-probabilities-sampling|Probability & sampling]] — The distribution that the mask modifies
- [[23-knowledge-graphs-ontologies|Knowledge graphs & ontologies]] — extract entities and relationships under schema
- [[132-tokenization|Tokenisation]] — what a token is and what it costs
- [[142-llm-reliability-resilience|Reliability & resilience]] — timeouts, recoveries, fallbacks and degradation
- [[148-llm-batch-pipelines|Pipelines batch]] — process millions of items at a lower cost
- [[146-model-selection|Choice of models]] — criteria, benchmarks and migration
- [[00-moc-ai-engineering|MOC AI Engineering]]
