# Retrieval metrics and RL alignment review — 17 November 2026

The review checked coverage of retrieval quality, AP@k/MAP@k, reciprocal rank, MRR and alignment through reinforcement learning. Existing material covered precision, recall, MRR and introductory alignment; AP/MAP lacked a dedicated treatment, and the optimization mechanisms needed more depth.

## Coverage and changes

| Topic | Before | After | Scope |
| --- | ---: | ---: | --- |
| [Retrieval quality metrics](../../20-rag/20-011-retrieval-quality-metrics.md) | 0 | 25 cards | Evaluation contracts, qrels, eligible evidence, empty relevance sets, RR/MRR, AP/MAP conventions, graded nDCG, missing judgments, duplicates, evidence coverage, ANN recall and stage-by-stage diagnosis |
| [Post-training and RL alignment](../../50-fine-tuning/52-post-training-alignment.md) | 17 | 35 cards | RLHF, RLAIF, verifiable rewards, policy gradients, reward models and critics, advantages, PPO, reference KL, action masks, GRPO, DPO, preference data and realignment after adaptation |
| [Agentic RL](../../50-fine-tuning/55-agentic-rl.md) | 15 | 15 cards | Revised explanations and scenarios: environments, reward design, accepted trajectories, curricula, episode isolation, sparse feedback, policy lag and independent evaluation |

The update adds **43 cards** without retiring any. The repository now contains **155 topics and 2,870 active cards**, including **382 scenarios** and **215 do-not-confuse cards**. Existing note identifiers, the Anki model identifier and historical deck identifiers are preserved.

Both retrieval metrics and post-training alignment are included in their domain's core reading sequence. Reciprocal topic links connect the new material to RAG, evaluation, ranking, permissions and vector search. Generated indexes and repository statistics are refreshed.

## Corrections and assumptions

- AP@k examples explicitly divide by the total number of relevant items, R. A separate card contrasts this with the `min(R, k)` convention. Queries with relevant evidence but no retrieved hits remain in macro averages; genuinely empty relevance sets require a declared policy.
- RR measures the first relevant rank; it does not establish evidence completeness. Reciprocal rank fusion combines result lists and is a separate concept. ANN recall against exact vector neighbors is distinguished from recall against relevance judgments.
- PPO clipping limits parts of the optimization incentive; it is not a hard policy-distance bound. The collection policy and reference policy serve different purposes. A sampled log-ratio may be negative although the exact KL expectation is nonnegative.
- GRPO's zero centered reward advantage does not imply every configured gradient is zero. Reward normalization and variance conventions are stated explicitly. DPO is distinguished from an online RL loop and a separately learned reward model.
- Verifiable rewards describe the feedback source, while agentic interaction describes the trajectory. They can coexist. Neither outcome rewards nor automated verifiers are inherently resistant to exploitation.
- Later fine-tuning can regress previously learned behavior. Independent regression checks are needed throughout adaptation; an alignment pass is not a universal repair guarantee.

Worked examples cover AP, MAP, conflicting RR/AP rankings, nDCG, PPO clipping, KL penalties, GRPO normalization and DPO margins. They use synthetic inputs and do not claim measured improvements from training or retrieval experiments.

## Sources and review limits

Primary sources are linked in each topic. The review checked the [NIST cutoff AP implementation](https://github.com/usnistgov/trec_eval/blob/main/m_map_cut.c), [Spark's alternative cutoff normalizer](https://github.com/apache/spark/blob/master/mllib/src/main/scala/org/apache/spark/mllib/evaluation/RankingMetrics.scala), the original [PPO](https://arxiv.org/abs/1707.06347), [DPO](https://arxiv.org/abs/2305.18290) and [DeepSeekMath](https://arxiv.org/abs/2402.03300) papers, and [TRL's documented GRPO variations](https://huggingface.co/docs/trl/main/en/grpo_trainer).

The alignment topic's verification date covers this conceptual and mathematical review. The agentic RL topic retains its previous overall date and records a targeted review; no fresh claim about every framework or managed service is implied. No model training or retrieval benchmark was run.

## Validation

- Flashcard structure, links, reciprocal connections and generated catalogs: no errors or warnings.
- Python lint, type checking, 72 unit tests and both executable workshops pass.
- Numerical examples independently recalculated; all existing active card identifiers retained.
- Anki export contains 2,870 active cards and 71 suspended retired cards, for 2,941 notes.
- Hugo extended 0.169.0 builds the documentation with warnings treated as errors; generated-site link validation passes.

[Review reports](README.md) · [Learning guide](../guides/learning-with-flashcards.md)
