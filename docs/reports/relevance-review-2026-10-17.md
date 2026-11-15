# Card Relevance Review — 17 October 2026

The value remains relevant for an AI Engineer: the cards are accurate in their vast majority, up-to-date on the agent stack and rich in case of application. The main flaw was not the error but the **redundancy**: the same notion was defined in two, three or four cards, which causes the same answer to be revised several times.

## Perimeter

- **Complete reading** of 144 topics from the local copy at 17 October, including an then-uncommitted enrichment pass that adds about 175 paragraphs to 46 topics from sections 10 to 54.
- **Automatic analysis**: TF-IDF similarity between cards, catalog questions, short questions that do not name their subject, formulations proscribed by README.
- **Online verification** of four dated facts: Claude Code hooks, ingress-nginx removal, GPU B300 memory, Anthropic prompt caching.
- **Integration**: The remote repository contained seven commits from the 11 to the 13 October, missing from the reread copy. They bring the [Relevance Review of October 11](relevance-review-2026-10-11.md), two new cards and changes in 25 cards. The changes in this review were replayed on this state, card by card.

This review does not recheck every product, version or regulatory text. Facts after June 2026 And they are called by the signs. as the specification MCP 2026-07-28, A2A 1.0 Or the omnibus. have not been re-checked. Only three dates `Verified on` change, on the topics whose claims have actually been confronted to the sources: 34, 83 and 123. The two topics arrived with the remote deposit, on rights and versions in RAG and on the evaluation of responses, have not been re-read; Only the lintel covers them.

## Constats

### Redundancy between topics

The lexical similarity only identifies about ten duplicates, because the repeated cards are reformulated. The reading has found about forty. Examples:

| Notion | Where it was defined |
| --- | --- |
| Option `--nv` d'Apptainer | 06, 09 and 13 |
| KV cache | two almost identical cards in 61 |
| Prefix caching | 61 and 66 |
| Ollama or vLLM | 11 and three 164 cards |
| Use of misleading GPU | 64, 69 and 93 |
| pass@k and pass^k | 96 and 114 |
| RLHF and DPO | 51 and 52 |
| Shadow deployment | 97 and 112 |
| Schedule of the AI Act | 115 and 155 |

A duplicate card costs time to review without increasing understanding, and it can also diverge: the AI Act calendar spoke of "Digital Omnibus" in one card and "AI Omnibus" in the other.

### Dated or inaccurate facts

- **Hooks of Claude Code**: the card claimed that a non-zero exit code blocks the action. Only the code 2 blocks; a code 1 allows the call to be made.
- **ingress-nginx**: The Ingress plug presented it as a reference controller and used its annotations, while its maintenance was to stop in March 2026.
- **Prompt caching**: Caching is cheaper than 0.1× on some recent models.
- **VRAM benchmarks**: The B300, about 288GB, was missing.

### Inconsistencies between cards

- **Size of chunks**: 512 to 1,024 tokens in 21, 300 to 800 in 25, which considers "too big" beyond 1.000.
- **Lost in the middle**: a scenario imposed the best passages at the beginning and at the end, the neighboring card refuses to make it a universal rule.
- **Rate limits**: a situationalization advised to multiply the keys, the card of the same card warns against this circumvention.
- **Expanded artifact**: three versions to trace in the 112 topic, four in the 111 topic, which adds the RAG index.
- **Examples that give the answer**: the cards "gradient accumulation" and "6ND law" accurately quoted the data and the result of a nearby calculation card.

### Difficult questions to note

- **Catalogs**: “What text-to-SQL benchmarks do you know?”, “What agent sandbox services do you know?” or lists of cloud components fail and age quickly.
- **Absent topic**: “What does the speed gain depend on?” or “When not to blame the pattern?” do not understand each other once the cards have been shuffled.
- **Forbidden wording**: three cards used "X or Y: what's the difference?", which the lint did not detect.

### Enrichment Pass

The added paragraphs are correct and often provide a useful nuance: idempotency after resumption, verified permissions for execution, action before decision, but they follow the same cautionary template.

| Indicator | Before the Pass | After the Pass and the Review |
| --- | ---: | ---: |
| Average words by answer | 71.9 | 75.9 |
| Answers with an imperative "Check, Measure, Test, Compare..." | 18% | 21% |

Four additions posed a concrete problem: two revealed the answer of a calculation card, Two repeated the next card. They have been lightened. Two others took up a nuance that the remote repository had published in the meantime, on the tool schema cache and the serving multi-LoRA. They were removed on integration. To continue this passage on the sections 55 TB 170, add a paragraph only if it provides a mechanism, a counter-example or a decision criterion absent from the card and its neighbors.

## Modifications

| Type | Count | Examples |
| --- | ---: | --- |
| Retired cards | 41 | duplicates above, two catalogs without response criteria |
| Reformulated questions | 29 | benchmarks set as a choice, subject named, “Not to be confused” |
| Added cards | 2 | migration out of ingress-nginx, case of a data analysis wizard |
| Other replacements in the topics | 49 | dated facts, inconsistencies, shells, lightened additions, summaries and sources |

The IDs of the reformulated cards are kept: their review history follows. Each card removed appears in `scripts/retired_cards.json` with its reason, and the export republishes it suspended with the tag `retired`. In AnkiDroid, search for `tag:retired`, select everything and then delete. The preserved card keeps its own history.

Two removals are replaced to maintain coverage: the situation setting "answers cut to 60 seconds" of the 83 form, duplicate of the 84 form, becomes a migration out of ingress-nginx, and the "Cas 4" of the 145 form, duplicate of its own situation setting, becomes a natural language data analysis assistant.

Five planned replacements were already made by the review of the 11 October or no longer had an object. The card of the card 32 no longer claims that MCP requires tool calling. The situation of the card 63 no longer imputes the regression to the order of the fields. The summary of the card 161 no longer cites the other modalities.

## Tools and Conventions

- **Lint**: it now indicates "X or Y: what's the difference?" and catalog questions in "Which benchmarks...", "Which services...", "Which offers..." or "...know?".
- **README**: two conventions added. A notion is defined in its dedicated card and is mobilized elsewhere by a link or an application card. A neighbor card must not give as an example the result of a calculation card.

## Verifications

- Lint on all the vault: no errors, no warnings, even with extended rules.
- 52 successful repository tests under Python 3.10, pinned dependencies, including those of the RAG workshop; Anki export generated with 2,163 active cards and 71 suspended removed cards.
- Synchronized README and MOC catalogs; update status line.
- Viewed sources: [Documentation of Claude Code's Hooks](https://code.claude.com/docs/en/hooks), [Announcement of the withdrawal of Ingress NGINX](https://kubernetes.io/blog/2025/11/11/ingress-nginx-retirement/), [Anthropic prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching), [GB300 NVL72 from NVIDIA](https://www.nvidia.com/en-us/data-center/gb300-nvl72/).

These controls focus on the consistency and proper functioning of the vault. They do not measure a learning gain in users.

## Proposed action

- **Files arrived with the remote repository**: reread 20-010 and 90-010 with the same redundancy and formulation criteria.
- **Files to be rechecked in priority**: 38 and 115, which cite many cloud offers and announcement dates; 33, 36 and 85 for MCP and A2A.
- **Container section**: the 05 sheet devotes three cards to the history of dockershim, removed in 2022. They could be reduced to the "not to be confused" card.
- **Very abstract recent cards**: Several cards from 60-010 to 60-012 respond with a checklist. Completing them with an encrypted example would make it easier to review ratings.
