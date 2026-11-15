# Relevance Review — 11 October 2026

Valult remains relevant for an applied AI engineer, with a particularly developed coverage of LLMs, agents and their release into production. The two passes of this review reinforce the decision criteria, the limits of guarantees and the transition to exercises. They add 33 cards in total, to reach 2,043 cards.

## Perimeter and limits

Structural control covers the 137 format: format, Links, identifiers, reading by the plugin and pedagogical conventions. The first pass went from 2,010 cards; the second of 2,022 Cards, by keeping the previous changes. The detailed reading targets twelve cards: 31, 32, 51, 63, 95, 96, 143, 146, 161, 163, 172 and 173. The corrected passages are confronted with the primary sources indicated in the sheets; The numerical exercises are recalculated.

This review does not constitute an exhaustive factual validation of each response of the vault or an update of all product versions and regulatory texts. Existing verification dates remain unchanged: adding a reference or correcting a passage does not amount to rechecking an entire topic.

## First pass: quality of responses and evaluations

| Topic | Enrichissements | Pedagogical contribution |
|---|---|---|
| LLM-as-a-judge (95) | Injecting the judge, parsing errors and abstentions, bias in the selection of re-read cases, diagnosis of a suspicious gain | Distinguishing real improvement and artificial score increase |
| RAG Evals and Agents (96) | Validity, support and coverage of quotes; explicit calculation; counterfactual tests; case of valid but inconclusive links | Check affirmations rather than the mere presence of references |
| Hallucinations and grounding (143) | Low temperature limits, source conflicts, partial response, conflicting policy cases | Respond according to applicable evidence and explain what is missing |

Twelve added cards: eight concept cards, one calculation card and three scenarios. Two existing answers are nuanced: structured format and low temperature do not guarantee the news; a proof of judge must be short, controllable and evaluated, without systematically prescribing a long reasoning.

## Second pass: decision, agents, adaptation and multimodal

**35 existing cards are corrected or specified and 21 cards are added to nine cards.** Additions include seven calculations, three scenarios, one distinction, and ten other concept cards. The number of corrections counts one card only once, even when its front and back change.

| Topic | Corrected | Added | Enhanced competence |
| --- | ---: | ---: | --- |
| [Fundamental agents](../../30-agents/31-agent-fundamentals.md) | 4 | 0 | Distinguish ReAct, call format and controlled loop; justify autonomy |
| [Tool calling](../../30-agents/32-tool-calling.md) | 8 | 3 | MCP without LLM decision, conditional validation, timeouts, statuses and pagination |
| [Fine-tuning](../../50-fine-tuning/51-fine-tuning-adaptation.md) | 5 | 3 | Possible regress with LoRA, Adaptor Artifacts, Rank and Damping |
| [Guided generation](../../60-llm-inference/63-guided-generation.md) | 3 | 0 | Exit contract, abstention and diagnosis without assuming the cause |
| [Choice of models](../../140-system-design-product/146-model-selection.md) | 4 | 3 | Opening and hosting, OSI definition, comparable budgets and Pareto front |
| [Vision-langage](../../160-multimodal-edge/161-vision-language-models.md) | 5 | 4 | OCR without promise of accuracy, contact information, complete documents and scope of marking |
| [Real time voice](../../160-multimodal-edge/163-real-time-voice.md) | 5 | 3 | Measured latency, WER and business errors, interruption and action already performed |
| [Validation ML](../../170-classical-ml/172-ml-validation-metrics.md) | 0 | 1 | Effect of prevalence on accuracy at constant TPR/FPR |
| [Calibration and abstention](../../170-classical-ml/173-calibration-uncertainty-abstention.md) | 1 | 4 | Expected cost of three decisions, two directions of coverage, human errors |
| **Total** | **35** | **21** | |

Some decisive corrections:

- **MCP**: The old response excluded its use without native tool calling. The protocol also allows a resource reading or a call decided by code or an interface.
- **Strict arguments**: The presence of a schema does not guarantee its application; interrupted answers and business rules remain to be processed.
- **LoRA**: Freezing base weights does not prevent the active adaptor from degrading capabilities, nor does the number of customers suffice to size a serving multi-LoRA.
- **Open source AI**: The OSI 1.0 definition requires data information that allows a substantially equivalent system; it does not require bit-by-bit reproduction or always all raw data.
- **Multimodal**: OCR, transport choice or speech-to-speech are not enough to promise accuracy or latency. Guarantees must be measured on actual inputs.
- **Human Review**: its errors and delays are part of the result of the service. The front of the load calculation now announces the three minutes of review necessary to solve it.

New questions are understood alone and the calculations provide their hypotheses. The maps remain in the existing cards and their historical identifiers are kept.

## Executable workshop

The [AI Decision Workshop](../../examples/ai-decisions/README.md) uses the standard Python library, with separate statements of solutions, controlled results, and draft variants. It is linked from the README, MOC, and Learning Guide.

Its four exercises work precision according to prevalence, decision with review, choice under constraints and documentary quality. Two batches to 99% of correct fields have respectively 80% and 99% of fully correct documents: the distribution of errors counts. The independent calculation `0,99^20 ≈ 81,8 %` is another model, whose hypothesis must be explained.

The values are fictitious. No models are trained, no GPU benchmarks are executed, and no improvement in user learning is measured by this workshop.

## Primary sources and scope

- [Liu et al. — Evaluating Verifiability in Genetic Search Engines](https://arxiv.org/abs/2304.09848): distinguish between support for quotes and coverage of claims.
- [Niu et al. — RAGTruth](https://arxiv.org/abs/2401.00396): The retrieved context does not eliminate unsupported or conflicting claims.
- [JudgeDeceiver](https://arxiv.org/abs/2403.17710): The evaluated response may contain an injection aimed at the judge.

The proposed incident procedures, error handling and counterfactual tests are educational applications of these limits; these articles do not validate a particular production architecture on their own.

For the second pass, the references are added to the relevant topics:

- [Specification MCP 2025-11-25 — tools](https://modelcontextprotocol.io/specification/2025-11-25/server/tools) and [ressources](https://modelcontextprotocol.io/specification/2025-11-25/server/resources), [ReAct](https://arxiv.org/abs/2210.03629) and Anthropic documentation for tool contracts.
- [LoRA](https://arxiv.org/abs/2106.09685), [TRL SFT Trainer](https://huggingface.co/docs/trl/sft_trainer), [PEFT](https://huggingface.co/docs/peft/package_reference/lora) and [vLLM](https://docs.vllm.ai/en/stable/features/lora/) for adaptation and serving.
- [Open Source AI Definition 1.0](https://opensource.org/ai/open-source-ai-definition) for the freedoms and elements required, without assimilating weight opening and accommodation.
- [Qwen2.5-VL](https://arxiv.org/abs/2502.13923), [WER](https://huggingface.co/spaces/evaluate-metric/wer/blob/main/README.md) and [LiveKit](https://docs.livekit.io/testing/observability/data/) for multimodal capabilities and metrics.
- [European Commission — Article 50](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-50) to distinguishish scope of obligations, technical marking and information. This targeted correction does not renew the regulatory audit of the AI Act topic.
- Scikit-learn documentation and introduction to compliant prediction already present in 172 and 173 topics for metrics, calibration and coverages.

Choice policies and numbers are pedagogic derivations under explicit assumptions; these sources do not demonstrate that a particular model will be suitable for a given deployment.

## Further details are still useful

1. **Verifiable RAG workshop**: small versioned fictional corpus, unanswered questions and conflicting sources; deliverable composed of an affirmation/proof table, errors and a policy of abstention.
2. **Judge validation workshop**: independent human annotations, style variants and injections; deliverable consisting of a segmental confusion matrix, coverage and human review decisions.
3. **Workshop on tool effects**: fictitious service with partial result, timeout after write and pending operation; produce a state check that distinguishes stop, success and unknown result.
4. **Priority of the review**: measure the learner's errors to select the next cards to deepen. The number of cards alone does not measure the mastery; privilege the notions that fail in application.
5. **Targeted update**: continue the verification of product versions and regulatory texts by keeping a topic of the passages actually verified.

## Validation

- 137 cards, 2,043 cards, 323 situationalized and 164 confusion cards.
- Lint: zero error and zero warning.
- 40 successful repository tests on Python 3.13 with pinned dependencies; tests include parser, catalogs, and Anki export.
- The temporary copy used by the tests now includes the example Markdown files to control links to the README of the new workshop.
- Anki export generated and controlled: 2,043 active cards and 30 cards removed, suspended.
- All pre-existing card IDs retained; 33 new IDs assigned in two passes. Titles and assignments of existing packets unchanged.
- Four local exercises executed, including the mode that displays only statements; results of calculations and variants controlled.
- README and synchronized catalog; local links of documents and workshop checked.

The Python 3.9 system did not install all pinned dependencies, so validation used a temporary Python 3.13 environment, without changing the dependencies of the repository.
