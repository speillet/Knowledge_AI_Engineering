# Learning Review — 9 October 2026

The content remains relevant for an applied AI engineer, especially on the LLM, the agents and their putting into production. The priority of this review is the quality of the reminder: understand a notion, solve an exercise from its front and know if its answer is correct.

## Perimeter

Structural control covers the **129 cards and 1,856 initial cards**: syntax, identifiers, lengths, connections and identical questions after normalization. The in-depth pedagogical reading targets Transformer foundations, prompting, probabilities, RAG, evaluations and reproducibility, as well as the **68 existing calculation cards**. This perimeter does not constitute a new factual verification of each product, version or regulatory text.

Exact repetitions of questions were not the main problem. The defects observed were mainly necessary data missing from the front, too general conclusions and insufficient distinctions between the measurement and its interpretation. Similar notions can usefully come back in the form of definition, application and cases; this complementarity must be evaluated on reading, not only by a search for duplicates.

## Corrections made

**94 existing cards are corrected or specified in 36 cards**, including **44 calculation cards**. This represents 48 rectos and 63 versoes modified, with overlap between the two. Their credentials are retained and no cards are removed.

| Educational problem | Correction | Example of concept worked |
| --- | --- | --- |
| Data revealed only on the back | Place values, units, and assumptions in the question | Agent cost, Adam states, batch quotas, sample size |
| Empirical rule presented as a guarantee | Explain the mechanism and then the condition of validity | Low temperature ≠ accuracy; majority ≠ confidence calibrated |
| Generated explanation taken for proof | Separate controllable justification and internal mechanism | Chain-of-thought and verification of the result |
| Too strict boundaries between techniques | Specify the objectives and their recoveries | Few-shot/fine-tuning; pre-training/post-training |
| Mesures confondues | Define events, denominators and references | Likelihood/perplexity; fidelity/accuracy; pass@k/pass^k |
| Implicit positive class | Set “positive = success” and interpret TPR/TNR | Validation and correction of an imperfect judge |
| Test and evaluation presented as alternatives | Show their complementarity and limits | Deterministic contracts, quality criteria and non-regression |
| Approximation turned into promise | Separate theoretical ceiling and measured performance | Capacity KV, speed of decode, weight transfer |

Two concrete corrections: the KV budget of 68 GB divided by 2.62144 GB per request authorizes **25 complete requests**, not 26; the processing of 6.6 billion from tokens to 2 million / minute imposes **at least 55 hours** under the assumptions of the quota, without guaranteeing this actual duration.

The scenarios of the topics concerned are adjusted to remain consistent with the corrected answers: specify the requirements before designing the evals, diagnose the floors of the RAG, validate one judge per class and avoid transforming an average rate into an individual guarantee.

## Twelve cards to apply the notions

| Topic | Ajouts | Apport |
| --- | ---: | --- |
| [Transformer](../130-llm-fundamentals/131-transformer-architecture.md) | 3 | Weighted sum of attention, memory factor of GQA, parallelism in training and generation |
| [Probability and sampling](../60-llm-inference/65-probabilities-sampling.md) | 2 | Top-p with renormalization; probability of sequence and perplexity |
| [RAG Evals and Agents](../90-observability-evals/96-evals-rag-agents.md) | 4 | Accuracy/reminder, MRR, fidelity vs. accuracy, diagnostics by oracle context |
| [LLM-as-a-judge](../90-observability-evals/95-llm-as-judge.md) | 1 | Numerical correction of a proportion under explicit assumptions |
| [Reproducibility](../110-mlops-cicd/114-reproducibility-variance.md) | 1 | Average ^2 passes per task different from the average success square |
| [Prompting](../10-prompt-engineering/11-advanced-prompt-engineering.md) | 1 | Nine identical answers do not prove 90% accuracy |

These additions include **8 calculations, 2 distinctions and 2 diagnostic or interpretation cards**. They complete the definitions with an observable task. The Vault now contains **1,868 Cards**, of which **76 Calculations**, **293 put into situation** and **141 “Not to be confused” cards**.

## Method of review

The [Learning Guide](learning-with-flashcards.md) offers an initial route, a response criterion by card type, honest scoring in Anki and variants of draft exercises. It then connects this knowledge to existing workshops with deliverables. The README clarifies conventions to keep future questions autonomous and evaluable.

The distinction between recall and proofreading is supported by the [Study by Roediger and Karpicke](https://psychnet.wustl.edu/memory/wp-content/uploads/2018/04/Roediger-Karpicke-2006_PsychSci.pdf); the meaning of the notation buttons follows the [manuel Anki](https://docs.ankiweb.net/manual/studying). Primary technical sources are added to the relevant files: articles on Transformer, GQA, RoPE, reasoning, judges and RAG; Hugging Face and scikit-learn documentation; Stanford information search manual.

## Verifications

The checks focus on the consistency of the modified content and the proper functioning of the vault, not on a measured improvement in learning among users. The calculations are exercises; no GPU benchmark was executed for this review.

- Lint on all vault: no errors or warnings; playback compatible with Spaced Repetition parser.
- Synchronized summaries and absence of exactly repeated questions after normalization.
- 44 recalculated numerical results for new exercises, corrections and examples in the guide.
- 40 successful repository tests; Anki export generated and controlled.
- 1,868 active cards and 30 cards previously removed, still suspended in export.
- 1,856 pre-existing card identifiers retained, with their package assignments and stable package names. The control compares exported files; it does not simulate the import in a personal collection containing a review history.

The evolutions are divided into three commit themes: corrections of notions and statements, application exercises, then guide and pedagogical assessment.
