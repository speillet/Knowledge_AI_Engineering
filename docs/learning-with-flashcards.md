# Learning with flashcards

First understand the topic, then answer its cards **before revealing the back**. Use the answer to check your reasoning and its limits; you do not need to recite it word for word. Roediger and Karpicke's experiments found that active recall improved delayed retention compared with rereading under the conditions studied. They do not show that an Anki score measures engineering competence. [Original study](https://psychnet.wustl.edu/memory/wp-content/uploads/2018/04/Roediger-Karpicke-2006_PsychSci.pdf).

## Start without browsing the entire catalog

The following sequence is a suggested learning path for applied LLM engineering. Adapt it to what you already know. Study the prerequisites before attempting exercises, then gradually mix cards from topics you understand.

| Step | Topics to start with | What you should be able to do without revealing the answer |
| --- | --- | --- |
| 1. Choose an approach | [Model selection](../170-classical-ml/171-ml-model-selection.md), [validation](../170-classical-ml/172-ml-validation-metrics.md) | Propose a baseline and an evaluation without data leakage |
| 2. Understand the model | [Tokenization](../130-llm-fundamentals/132-tokenization.md), [Transformer architecture](../130-llm-fundamentals/131-transformer-architecture.md) | Explain next-token prediction, causal masking and the memory required for model weights |
| 3. Interpret model output | [Probabilities and sampling](../60-llm-inference/65-probabilities-sampling.md), [prompts](../10-prompt-engineering/11-advanced-prompt-engineering.md) | Apply a sampling rule and distinguish agreement, probability and correctness |
| 4. Measure quality | [Evaluation methodology](../90-observability-evals/94-evals-methodology.md), [LLM judges](../90-observability-evals/95-llm-as-judge.md) | Define success, a reference, the positive class and the limits of a metric |
| 5. Add knowledge | [Embeddings](../130-llm-fundamentals/133-embeddings-representations.md), [RAG](../20-rag/21-rag-fundamentals.md), [RAG evaluation](../90-observability-evals/96-evals-rag-agents.md) | Identify a retrieval or generation failure and calculate recall and precision |
| 6. Enable a system to act | [Agents](../30-agents/31-agent-fundamentals.md), [tool calling](../30-agents/32-tool-calling.md) | Distinguish a model's request from validation, authorization and execution |
| 7. Serve under constraints | [Metrics and SLOs](../60-llm-inference/64-inference-metrics-slo.md), [costs](../120-costs-finops/121-inference-costs.md) | Distinguish latency, throughput and cost per useful result |
| 8. Assemble and operate | [System design](../140-system-design-product/141-system-design-llm.md), [SRE](../110-mlops-cicd/116-ai-sre-incidents-capacity.md) | Justify an architecture, its evaluation and its behavior during failures |

If a calculation blocks your progress, identify the missing prerequisite: units and proportions, conditional probability or statistical uncertainty. [Statistics for decision-making](../90-observability-evals/99-statistics-experimental-decisions.md) and [reproducibility](../110-mlops-cicd/114-reproducibility-variance.md) then help you compare versions. Explore frameworks, HPC, RL and multi-agent systems as your project requires; their presence in the catalog does not give them equal priority.

## Know what you are assessing

Before revealing an answer, explain it aloud or write it down. The question determines the level of detail required.

| Card type | What your answer should contain | Errors that matter |
| --- | --- | --- |
| Definition or mechanism | The central idea and a relevant cause-and-effect relationship | Recognizing a term without explaining how it works |
| Do not confuse | The decisive difference and an example that distinguishes the concepts | Reversing the concepts or giving an example that fits both |
| Calculation | The formula, inputs, units, result and requested interpretation | Using the wrong denominator, mixing incompatible units or memorizing a result without the method |
| Scenario | A diagnosis, a measurement that distinguishes possible causes, a decision based on the conditions and a way to verify it | Proposing a solution without evidence or overlooking a critical constraint |

The additional explanations on the back support understanding and applying the concept elsewhere. Omitting a secondary example does not automatically mean failure. Omitting an assumption that makes the conclusion valid does: stating `pass^5 = p^5` without accounting for independent trials and constant success probability does not correctly answer a question about those assumptions.

Several approaches may be valid for a scenario. Compare objectives and checks rather than the exact wording or order of the answer. If the question does not make the expectations clear, flag the card and propose a more precise question instead of marking it correct by default.

## Rate your answers in Anki

| Button | When to use it |
| --- | --- |
| Again | You forgot the answer, answered incorrectly or missed something that invalidates the required reasoning |
| Hard | You answered correctly, but recall was difficult or hesitant |
| Good | You answered correctly with your usual recall effort |
| Easy | You recalled the correct answer effortlessly |

**Hard does not mean “I forgot, but recognized the answer after reading it.”** A correct answer in your own words is sufficient; recognizing the solution after revealing it is not. If choosing among four buttons is difficult, you can use only Again and Good. [Anki manual — Studying](https://docs.ankiweb.net/manual/studying).

Choose a number of new cards that you can manage alongside reviews already due. One possible session is: complete due reviews, read about a concept, study a few new cards, then solve a calculation or practical case. If your review backlog grows, introduce fewer new cards. Work through longer exercises on paper in a separate session when needed; speed alone does not measure understanding.

## Move from a memorized answer to reasoning

For a calculation you have memorized, change the inputs **on scratch paper**, solve it again and check the result. Keep the existing card identifiers when trying these variations.

Example: five retrieved results include three relevant passages, and the annotated reference contains six relevant passages in total. The expected results are `precision@5 = 3/5 = 60%` and `recall@5 = 3/6 = 50%`. Explaining why the denominators differ is as important as obtaining the numbers. This calculation assumes distinct results and a reliable reference defined at the same unit of retrieval.

For a rule, look for a counterexample: an answer faithful to an outdated document may be wrong for a current question. For a decision, change a constraint: what happens if the latency budget is halved, a dependency fails or labels are unavailable?

Keep a short error log: `concept | my incorrect reasoning | correction | new worked example`. For example: `KV cache capacity | round 25.94 up to 26 | take the floor | check that 26 requests exceed the budget`. A recurring error may reveal a missing prerequisite or an overloaded card.

## Demonstrate mastery beyond flashcards

After a group of topics, produce a reproducible deliverable: a metrics notebook with annotated data, a RAG diagnostic, a load-test report or an architecture decision. Record assumptions, protocol, results and limits. Label simulations clearly; their results do not replace measurements of the real service.

To build a platform, follow [Implement and validate an agent platform](platform-agents-inference-learning-path.md): eight steps using a support agent, covering architecture, API contracts, quality, observability, capacity and recovery. Each step identifies the topics to study, a deliverable and criteria for moving on. Practical evidence complements card reviews.

The [senior practice path](senior-learning-path-relevance-2026-10-07.md) and [inference workshops](llm-inference-audit-2026-10-08.md) provide concrete deliverables and success criteria. Flashcards maintain the necessary knowledge; building, measuring, operating systems and sharing that knowledge develop practical competence.

For data engineering, follow the [learning path and its five workshops](data-engineering-audit-2026-10-09.md). The [executable SQL workshop](../examples/data-engineering/sql_workshop.py) lets you predict and then verify the effects of joins, null values and data availability over time, without an external service.

For AI decisions, the [local Python workshop](../examples/ai-decisions/README.md) presents exercises before their solutions, followed by variations to solve on paper. Compare expected costs and human-review strategies, distinguish precision from prevalence, make choices under constraints and evaluate complete documents. The data are synthetic; explaining assumptions matters as much as reproducing the numbers.

For RAG, the [verifiable RAG workshop](../examples/verifiable-rag/README.md) asks you to predict which evidence and answers are permitted before comparing two policies. Then change a fact, remove a piece of evidence or reduce the retrieval budget: the result should reflect the changed data or expose a limitation. The deliverable links each claim to a versioned passage and explains any abstentions. These simulation metrics are not an LLM benchmark.

For agentic systems, follow the [production path](agentic-stack-audit-2026-10-09.md), then run the [support-agent workshop](../examples/agentic-support/README.md). Predict the effects of a failure before reading the test: recovery guarantees and business controls should be verifiable independently of the model's generated text.
