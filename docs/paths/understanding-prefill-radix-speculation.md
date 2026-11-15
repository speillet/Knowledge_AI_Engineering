# Understanding the prefill, RadixAttention and Speculative Decoding

These three mechanisms occur in different locations of the same request. **prefill** calculates the state of the known prompt. **RadixAttention** avoids recalculating already available prefix states. **speculative decoding** tries to confirm multiple output tokens by checking the target. Understanding this timeline helps to choose an optimization and interpret its limits.

The flashcard path follows this order: [prefill and decode step by step](../../60-llm-inference/60-013-prefill-decode-step-by-step.md), [prefix caching and RadixAttention](../../60-llm-inference/66-prefix-caching-radix-attention.md), then [Special Decoding](../../60-llm-inference/67-speculative-decoding.md). The examples below use a classic Causal Transformer; a hybrid architecture may require other states.

## 1. The prefill calculates already known positions

Before the prefill, the model knows this sequence, but not yet its internal representations. At each layer, it calculates the projections of attention, the interactions allowed by the mask, then the other transformations, including the MLP. The weights remain fixed: it is inference, not training.

Positions can be calculated together in a layer because their inputs are known. However, the causal mask prohibits one position from looking at the future. For four tokens, the third position can look at the first three, never at the fourth. The next layer waits for the states of the previous one: "parallel" does not mean that the entire depth of the model disappears.

The keys and useful values are stored by layer. The last position of the prompt provides the logs that allow to choose the first token output. The emission of this token and the calculation of its state KV are two different moments:

```text
prompt connu : x1 x2 x3 x4

prefill processes x1 x2 x3 x4 → cache of 4 positions → chooses y1
decode 1 processes y1 → cache of 5 positions → chooses y2
decode 2 processes y2 → cache of 6 positions → chooses y3
```

If one stops after `y3`, it is not necessary to process the latter token to predict a non-existent `y4`. This is also why a response from `N` tokens, the first of which arrives after a TTFT, has `N−1` intervals up to the last token.

At each step of decode, the new token still crosses layers and looks at K/Vs from the past. The cache avoids recalculation of old representations; it does not remove weight reading, new projections, or attention to context. The [Founder of Transformer](https://arxiv.org/abs/1706.03762) describes projections and masking; current engines and architectures add their own mechanisms.

### What the chunked prefill changes

A long prompt can monopolize an iteration and interrupt the cadence of other requests. Cutting it into chunks allows the scheduler to insert prefill and decode. The chunks retain common positions and cache: treating them as independent documents would change the calculation.

With a fictitious budget of 2,048 positions per iteration, of which 48 occupied by decodes, there remain 2,000 positions for the prefill. A prompt of 6,000 tokens requires three ideal iterations if this distribution remains constant. This budget concerns the work of the iteration, not on the total length of the resident cache. A sequence processed at this iteration may already have thousands of positions.

The [vLLM documentation on the chunked prefill](https://docs.vllm.ai/en/latest/configuration/optimization/) explains scheduling priorities and their tradeoffs. Shrinking the size of tracks can protect streams while delaying the first release of the long prompt; measuring both populations.

## 2. RadixAttention returns a calculated state

Let's assume three compatible prompts, whose letters represent tokens identifiers:

```text
R1 = [S A B C]
R2 = [S A B D E]
R3 = [S A F]
```

Their cumulative length is worth twelve positions. A radix tree factorizes their beginning:

```text
racine
  └─ [S A]                 2 positions communes
       ├─ [B]              1 position shared by R1 and R2
       │    ├─ [C]         1 position unique to R1
       │    └─ [D E]       2 positions unique to R2
       └─ [F]              1 position unique to R3
```

Ideally, seven separate position states are retained, instead of twelve copies. Computation ignores rounding of pages, metadata, and subsequent output. Logical sharing is not a direct measure of the time or VRAM of an implementation.

### Research, bifurcation and service life

For `R2`, the engine finds `S,A,B`, then calculates `D,E`. To insert `R3`, it may have to split an existing edge after `S,A`: it reorganizes metadata and references, without having to recalculate these two common states.

Each active branch retains the references that its attention needs. When a query finishes, it releases them; states can remain cached for another request. Under memory pressure, states without a reader become candidates for eviction according to the policy. A shared prefix is often interesting to keep, but no rule promises that it will remain available forever.

RadixAttention does not replace the attention calculation with an approximate search. The tree recognizes exact prefixes and returns references to their state. The tensors remain managed by the memory pools and kernels of the engine. The [Article by SGLang](https://arxiv.org/html/2312.07104v2) explains the classic mechanism; the [Recent Unified Cache](https://www.sglang.io/blog/unified-radix-cache) adds the verification of the necessary states to the different components of a hybrid model.

### Why a resemblance is not enough

A key or value depends on the previous context. Finding the same tokens after a different start does not make their K/Vs interchangeable. Sharing conditions also include model, fit, positions, media, and isolation border relevant.

The new positions continue to consult the past. For `M` re-used positions and `S` News, the dense attention of the suffix `S×M + S×(S+1)/2` interactions. The prefill So avoiding it is not all the remaining attention. Finally, a Cache KV does not necessarily include final logs: a full hit may require a bit of recalculation to choose the next one token.

## 3. Speculation submits hypotheses to the target

A draft proposes an inexpensive sequence. The target can evaluate it as a batch because the proposed tokens are now known, like the positions of a small prefill. But their distributions are conditional: the distribution after a rejected proposal is no longer that of the text actually emitted.

```text
draft :         a   b   c   d
Verification: yes yes no
output :        a   b   x

c,d: abandoned proposals
x: correction to be integrated before the next
```

It is necessary to restore the cache lengths and references corresponding to the confirmed prefix. The hypothetical states of `c,d` cannot be reused as if they were describing `x` and its continuation. After accepting all the proposals, the standard scheme can produce an additional token of the target.

### Why Exact Sampling Requires Correction

Note `p` the target distribution and `q` the draft one with the same prefix. A `x` proposal from `q` is accepted with `min(1,p(x)/q(x))`. Example built on three tokens:

| Token | Cible p | Draft q | Probability of acceptance of the proposal |
| --- | ---: | ---: | ---: |
| A | 0.6 | 0.2 | 1 |
| B | 0.3 | 0.3 | 1 |
| C | 0.1 | 0.5 | 0.2 |

The mass produced by the accepted proposals is `(0,2; 0,3; 0,1)`, or 0.6 in total. It is missing 0.4 on `A`. After a rejection, the correction is therefore made in `max(p−q,0)` standardized: here `(1;0;0)`. We reconstitute `p` by adding the rejected mass redirected to `A`.

Simply shooting in `p` after rejection would add masses already present: in this example we would get `(0,44;0,42;0,14)`, which is not the target. This original calculation illustrates the need for the correction; the general demonstration and the sequential protocol are in the articles of [Leviathan et al.](https://proceedings.mlr.press/v202/leviathan23a.html) and [Chen et al.](https://arxiv.org/abs/2302.01318).

### Measuring the gain without confusing the meters

The accepted proposal ratio is not the number of tokens issued per pass. Correction and bonuses are useful outputs, without being accepted proposals. In the standard linear scheme, excluding early shutdown, the average issued length is `1 + accepted/verification passes`.

With four proposals and a constant conditional probability of acceptance of 0.8, the simplified expectation is `1+0,8+0,8²+0,8³+0,8⁴ = 3,3616`. If draft and verification together cost twice a normal step, the ideal gain is only `3,3616/2 ≈ 1,68`.

The distribution guarantee depends on the exact verification mechanism. The [documentation vLLM](https://docs.vllm.ai/en/latest/features/speculative_decoding/) distinguishes the standard rejection of released variants. A stable business result on a few examples does not demonstrate the general identity of the distributions; a different text for the same seed is also not a sufficient refutation.

## 4. Choose the experience that responds to the symptom

| Symptoms observed | Measure that separates the causes | Track to test |
| --- | --- | --- |
| First slow exit on long prompts | File, input calculation, effective reuse | Useful context, prefill, prefix cache |
| Streams interrupted during big prompts | ITL correlated to admissions | Chunked prefill and scheduler equity |
| First token Fast, Long Slow Response | decode time, weight readings and KV | Kernels, validated quantification, speculation |
| Hit high but TTFT still bad | Waiting and transfers, not just hits | Routing, admission, suffix cost |
| Isolated gain but reduced capacity at peak | Goodput and cost per task under several charges | k setting, draft memory, activation policy |

These tracks are hypotheses to be measured. The same change can move the bottleneck. The useful comparison preserves quality, length and load, includes errors and distinguishes an isolated request from a shared service.

## 12 November enrichment assessment 2026

This second pass starts from the commit `d37a212`, after the cross-sectional review. It develops the **110 answers initially between 45 and 60 words**, in 62 files, with specific additions on their subject: explanation, example, hypothesis or limit. After enrichment, these answers contain between **75 and 102 words out of code**. The threshold is used for the identification of the cards.

In total, **132 Existing responses are modified in 63 Sheets**, with **39 New Cards** : 22 in the new form prefill/decode, nine on the radix cache and eight on speculative decoding. The three inference sheets total **76 Cards**. The Vault now counts **148 cards and 2,372 Cards**, of which 357 put in situation and 184 “Not to be confused.”

**2,333 questions and historical identifiers are retained**. No maps are removed. Links, summaries and catalogs are updated, with a reciprocal link between the new sheet and its prerequisites. The verification dates of the 66 and 67 sheets are renewed after their review of mechanisms, examples, configurations and limits; other consultations remain reported as targeted in the sources.

The short answers also revealed corrected generalizations: anonymization and reasonable means of re-identification, analysis of personal data in a model according to the opinion of the EDPS, role of AWQ scales, permissions of agents and comparison of vector storages. The corresponding primary references are included in the topics concerned. This is not a reverification of all historical assertions of value.

### Verifications

- Lint: **Zero error and zero warning**, with Obsidian and Anki compatible playback.
- Catalogs: synchronization of README and MOC controlled.
- Identifiers: Comprehensive comparison before/after and retention of existing 2,333 identities.
- Calculations: timeline of the first token, logical sharing 12 → 7, probability correction, length expectancy, chunk budgets and transfer of 1 GiB recalculated separately.
- `make check`: ruff, mypy, 54 tests and two local workshops.
- `make export`: Anki packet generated, then controls active notes, suspended removed cards, and historical identifiers in its SQLite database.

Exercises and demonstrations do not constitute measurements on a GPU. Versions of serving and their variants must be tested with the hardware, load and constraints actually deployed. Repository tests protect the structure, navigation and export; the relevance of the content remains from the proofreading and cited sources.
