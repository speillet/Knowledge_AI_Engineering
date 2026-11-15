# Learning with Cards

Start by understanding a card, Then answer the cards. **before revealing the verso**. The back serves to check the reasoning and its limits; Do not recite your sentences word for word. Roediger and Karpicke’s experiments show a benefit of active recall over delayed retention compared to replay under the conditions studied. They do not demonstrate that an Anki score measures the skill of an engineer. [Original study](https://psychnet.wustl.edu/memory/wp-content/uploads/2018/04/Roediger-Karpicke-2006_PsychSci.pdf).

## Start without opening the entire catalog

Here is an order of work proposed for an applied LLM course. These are steps to adapt to the acquired, not a imposed schedule. Read the previous notions before the exercises, then gradually mix the cards already understood.

| Step | Start topics | What you can do without the back |
| --- | --- | --- |
| 1. Choose an approach | [Choice of model](../170-classical-ml/171-ml-model-selection.md), [validation](../170-classical-ml/172-ml-validation-metrics.md) | Propose a database and a test without data leakage |
| 2. Understanding the model | [Tokenisation](../130-llm-fundamentals/132-tokenization.md), [Transformer](../130-llm-fundamentals/131-transformer-architecture.md) | Explain prediction of the next token, causal mask and weight memory |
| 3. Interpret output | [Probability and sampling](../60-llm-inference/65-probabilities-sampling.md), [prompts](../10-prompt-engineering/11-advanced-prompt-engineering.md) | Apply a sampling rule and distinguish agreement, probability and accuracy |
| 4. Measure quality | [Evaluation methodology](../90-observability-evals/94-evals-methodology.md), [juges](../90-observability-evals/95-llm-as-judge.md) | Define success, reference, positive class and limits of a measure |
| 5. Add knowledge | [Embeddings](../130-llm-fundamentals/133-embeddings-representations.md), [RAG](../20-rag/21-rag-fundamentals.md), [evals RAG](../90-observability-evals/96-evals-rag-agents.md) | Locate a retrieval or generation failure and calculate recall/accuracy |
| 6. Making a system work | [Agents](../30-agents/31-agent-fundamentals.md), [tool calling](../30-agents/32-tool-calling.md) | Separate model request, validation, authorization, and execution |
| 7. Serve under constraints | [Metrics and SLO](../60-llm-inference/64-inference-metrics-slo.md), [costs](../120-costs-finops/121-inference-costs.md) | Distinguish latency, throughput and cost per useful result |
| 8. Assemble and operate | [System design](../140-system-design-product/141-system-design-llm.md), [SRE](../110-mlops-cicd/116-ai-sre-incidents-capacity.md) | Justify an architecture, its evaluation and its behavior down |

If a calculation blocks, identify the prerequisite: units and proportions, conditional probabilities, or statistical uncertainty. The [statistics to decide](../90-observability-evals/99-statistics-experimental-decisions.md) and the [Reproducibility](../110-mlops-cicd/114-reproducibility-variance.md) then help to compare versions. Deepening frameworks, HPC, RL and multi-agents according to the project; their presence in the catalog does not give them all the same priority.

## Know what is being evaluated

Before returning the map, produce an observable response, either out loud or on paper. The requested notion determines the level of detail expected.

| Type of card | Response to produce | Mistake that matters |
| --- | --- | --- |
| Definition or mechanism | Central idea and relevant cause and effect relationship | Recognize only the term without explaining how it works |
| "Not to be confused" | Decisive difference and example that separates the two notions | Reverse the notions or give a valid example for both |
| Calcul | Formula, data, units, result and interpretation requested | Bad denominator, incompatible units or result learned without method |
| Setting the scene | Diagnosis, Discriminant Measure, Conditional Decision and Verification | Propose a solution without proof, or forget a critical constraint of the case |

The backside complements help to understand and transfer. Omitting a secondary example does not automatically constitute a failure. By contrast, To forget the hypothesis that makes the conclusion valid is one: "pass^5 = p^5 without taking into account the independent repetitions and the constant probability does not correctly answer a question that examines them.

For a situation, several steps can be valid. Compare objectives and controls, not the exact order of the words. If the front does not know what is expected, report the card and propose a more precise question rather than a success by default.

## Showing posts in Anki

| Bouton | Usage |
| --- | --- |
| Again | Forgotten, false, or missing answer that invalidates the requested reasoning |
| Hard | Correct answer, found with difficulty or hesitation |
| Good | Correct response with usual recall effort |
| Easy | Correct answer found without effort |

**Hard does not mean “forgotten but recognized by reading.”** A correct personal formulation is sufficient. Recognizing the solution after posting it is not. In case of hesitation between four buttons, Anki allows you to limit yourself to Again and Good. [Manuel Anki — Studying](https://docs.ankiweb.net/manual/studying).

Choose a volume of new cards that is compatible with the revisions due. Example of a session to be adapted: revisions due, reading a notion, a few new cards, then a calculation or a practical case. If the delay increases, reduce the introduction of novelties. Long exercises can be worked on paper in a separate session; speed alone does not measure understanding.

## Moving from the known answer to reasoning

For a calculation already stored, change the data **on a draft**, solve, and then check. Do not modify the identifiers of existing maps for this simple variation.

Example: Five retrieved results contain three relevant passages, out of six relevant ones annotated. We expect `precision@5 = 3/5 = 60 %` and `recall@5 = 3/6 = 50 %`. Being able to explain why denominators differ is as important as the result. The calculation assumes separate results and a reliable reference to the same unit.

For a rule, look for a counterexample: a faithful answer to an obsolete document may be wrong for a current question. For a decision, change a constraint: what becomes of the solution if the latency budget is halved, if a dependency falls or if there are no labels?

Keep a small log of errors: `concept | my incorrect reasoning | correction | new worked example`. Example: `KV capacity | round 25.94 up to 26 | take the floor | check that 26 requests exceed the budget`. A recurring error can indicate a missing prerequisite or a card that is too loaded.

## Demonstrate mastery beyond the cards

After a block, produce a reproducible deliverable: metric notebook with annotated data, RAG diagnostic, load report or architecture decision. Record assumptions, protocol, result and limits. A simulation is useful if it is announced as such; it does not replace a measurement of the actual service.

To assemble a platform, follow the [Implement and validate an agent platform](platform-agents-inference-learning-path.md): eight steps on a support agent, with architecture, contracts API, quality, observability, capacity and recovery. Each step indicates the cards to be studied, a deliverable and a criterion of passage; the practical evidence completes the revisions.

The [Senior practice path](senior-learning-path-relevance-2026-10-07.md) and the [Inference Workshops](llm-inference-audit-2026-10-08.md) give concrete deliverables and criteria. The maps maintain the necessary knowledge; the experience of construction, measurement, operation and transmission completes this learning.

For data, follow the [data engineering course and its five workshops](data-engineering-audit-2026-10-09.md). The [Executable SQL Workshop](../examples/data-engineering/sql_workshop.py) predicts and then verifies the effects of joins, null values and time availability, without external service.

For AI decisions, the [atelier Python local](../examples/ai-decisions/README.md) offers statements before displaying solutions, then variants on draft. It compares expected and revised cost, distinguish precision and prevalence, choose under constraints and measure complete documents. The data are fictitious; explaining the assumptions counts as much as finding the figures.

For the RAG, the [Verifiable Workshop](../examples/verifiable-rag/README.md) predicts the authorized evidence and answers before comparing two policies. Then modify a fact, remove a proof and reduce the research budget: the result must follow the data or reveal the limit met. The expected deliverable links each claim to a versioned passage and explains the abstentions; the metrics of this simulation do not constitute a benchmark of LLM.

For the agent stack, follow the [Production path](agentic-stack-audit-2026-10-09.md) and then run the [atelier support](../examples/agentic-support/README.md). Predict the effects of a failure before reading the test: the guarantees of resumption and the business controls must be able to be verified independently of the text produced by the model.
