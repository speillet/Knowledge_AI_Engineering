# Readable flashcard diagrams — 21 November 2026

Ten existing answers now illustrate mechanisms where ordering, branching or memory
placement is easier to understand visually. Questions, permanent identifiers, model
identity and deck identities are preserved; the vault still contains 2,870 active cards.

## Selection and references

The diagrams are original, simplified drawings informed by the primary references
below, consulted on 21 November 2026. They are not downloaded screenshots. Sources
are also linked beside each image in the answer. This review checks the illustrated
mechanisms; it does not refresh every claim or verification date in the topic.

| Card topic | What the diagram explains | Primary reference |
| --- | --- | --- |
| [Hybrid search](../../20-rag/22-advanced-rag.md) | Lexical/vector retrieval, fusion by rank, then optional reranking | [Elastic: RRF](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion) |
| [ReAct](../../30-agents/31-agent-fundamentals.md) | Model request, harness controls, execution, observation and stopping | [Anthropic: agents diagram](https://www.anthropic.com/research/building-effective-agents) |
| [LoRA](../../50-fine-tuning/51-fine-tuning-adaptation.md) | Frozen weights and the trainable low-rank branch share the input | [Hu et al., Figure 1](https://arxiv.org/abs/2106.09685) |
| [DPO](../../50-fine-tuning/52-post-training-alignment.md) | Direct preference loss versus reward fitting and online RL | [Rafailov et al., Figure 1](https://arxiv.org/abs/2305.18290) |
| [ZeRO](../../50-fine-tuning/54-distributed-training.md) | The model states sharded at each stage, illustrated with four GPUs | [DeepSpeed: ZeRO stages](https://www.deepspeed.ai/tutorials/zero/) |
| [PagedAttention](../../60-llm-inference/61-kv-cache-attention.md) | Logical KV blocks map to non-contiguous physical blocks | [vLLM: PagedAttention diagrams](https://vllm-project.github.io/2023/06/20/vllm.html) |
| [Prefill/decode](../../60-llm-inference/60-013-prefill-decode-step-by-step.md) | Selecting a token precedes processing it and caching its K/V | [Vaswani et al., decoder and attention](https://arxiv.org/abs/1706.03762) |
| [Speculative decoding](../../60-llm-inference/67-speculative-decoding.md) | Accepted prefix, first rejection, discarded suffix and correction | [Leviathan et al., Figure 1 and Algorithm 1](https://arxiv.org/abs/2211.17192) |
| [Causal attention](../../130-llm-fundamentals/131-transformer-architecture.md) | Rows query columns; future positions are blocked | [Vaswani et al., §3.2](https://arxiv.org/abs/1706.03762) |
| [MoE routing](../../130-llm-fundamentals/136-mixture-of-experts.md) | Per-token top-2 selection and the weighted sum of expert outputs | [Jiang et al., §2](https://arxiv.org/abs/2401.04088) |

The ReAct drawing shows the authorized tool path; denied requests must also return
controlled feedback. The ZeRO quarters describe persistent model states, not the
whole memory peak. The MoE drawing uses three experts for legibility; it does not
describe Mixtral's expert count. The speculative example illustrates a rejection;
the answer and reference retain the distinction between greedy and exact sampling.

## Assets and rendering

- Editable SVGs and committed PNGs live together in `assets/diagrams/`.
- Each diagram uses a 480-unit-wide canvas, labels of at least 24 units and a
  white background. Layout and text supplement color to identify branches and states.
- PNGs are rendered at twice the SVG dimensions. Anki limits display width to
  480 pixels or the available card width, preserving the aspect ratio.
- The answer keeps its explanation, descriptive alternative text and source link.
- The exporter parses Markdown image tokens, resolves images relative to the
  topic, references basenames in HTML and embeds the files in the `.apkg` media
  manifest. Missing files, external image URLs and filename collisions fail export.
- Site preparation copies the PNGs to static assets and generates URLs that honor
  the deployment subpath. Code examples containing image syntax remain unchanged.

Regeneration instructions are in the [Anki guide](../guides/anki.md). The optional
browser dependency is needed only to edit assets; exports use the committed PNGs.

## Validation

- `make check`: 75 tests pass, including historical note/deck identity checks;
  topic lint reports zero errors and warnings, and ruff/mypy pass.
- `make export`: 2,870 active cards, 155 topics, 17 sections, 71 retired cards
  and ten embedded images. Package tests compare every media payload with its
  source and check that every image referenced by a note is present.
- `make site`: 217 HTML pages checked with zero broken references, including
  the ten diagram URLs under the project's deployment subpath.
- Browser checks cover all ten exported answers and all ten site cards at
  widths of 320, 360, 480 and 1,024 pixels, in light and dark themes: 160 cases.
  Images load without clipping, keep their proportions and display at no more
  than 480 pixels wide. The smallest diagram labels on the 320-pixel site are
  approximately 14.3 pixels tall. A narrow code example cannot force the card's
  grid column wider than the screen.
- Visual inspection of phone previews checked contrast, text bounds, arrow
  placement and layout. The white image background remains legible in dark mode;
  the reference links also have an explicit dark-mode color.

Browser previews use the fields and styling extracted from the built `.apkg`;
they do not replace an import on a physical AnkiDroid device.

[All review reports](README.md)
