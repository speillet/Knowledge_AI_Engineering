# — 6 October Flashcard Review 2026

The structural control concerns the **1,553 cards of 110 cards**. All of them have a question, an answer and a permanent identifier. The editorial review led to the modification of **385 cards in 88 cards**: **370 answers** enriched or corrected and **49 questions** reformulated, some cards cumulating the two changes.

## Depth of answers

The **330 responses of less than 35 words out of code** have all been reread and developed. This threshold was used to identify potentially too succinct responses, not to automatically judge their quality. The add-ins explain the mechanism, an example of use, the prerequisites or the limits specific to each subject. The answers consisting only of a schema or a code snippet now have an explanation.

The average length goes from **55.7 to 66.9 words out of code**. Cards already explicit have generally been retained; enriched answers remain focused on their question.

## Relevance and corrections

Ambiguous questions have been made more self-reliant by clarifying the topic, including LangChain, LangGraph, CrewAI, inference, or prompt caching. Descriptions of mechanisms replace overly telegraphic formulations. Figures from a study, assumptions from a calculation, and conditional guarantees are distinguished from general rules.

Examples of corrections:

- **RAG and agents**: quotation to check, separation between stop and success, effect of parallelism on cost and delay.
- **Frameworks**: LangGraph node recovery, RAM persistence limits, middleware responsibilities, and tools.
- **Inference and infrastructure**: KV cache, residual fragmentation, difference TPOT/ITL, weight memory and total memory, image compatibility with host.
- **Costs and Ratings**: Cost units per token, score uncertainty and matched comparison, batch queries that may expire, risks and cost of shadow testing.
- **Technical examples**: `system` parameter in the API Anthropic, Cedar authorization with cents amount and trusted context.
- **Compliance**: territorial scope and legal basis of the GDPR, qualification of high risk, timing and transparency of the AI Act facing institutional sources.

The primary references consulted are added in the `Sources` sections of the relevant topics. The overall verification dates have not been renewed automatically: this intervention constitutes a targeted review of the content, and not a new certification of each claim or version of product in the vault.

## Conservation and validation

No cards have been removed or added. The **1,553 Anki identifiers** are identical to those before the review, so that the reimport updates the existing cards while maintaining their progress.

Results of controls:

- **Lint**: 0 error and 0 warning, with Obsidian/Anki playback equivalence.
- **Catalogs**: README and MOC synchronized.
- **Repository Tests**: 40 successful tests, including parser, export and preservation of historical identifiers.
- **Before/after comparison**: Active 1,553 identifiers are retained.
- **Anki export**: generated package and checked archive; 1,553 active cards with replies and 30 old cards removed, republished suspended according to existing operation.

The `dist/ai-engineering.apkg` package is a generated artifact, excluded from Git. The CI rebuilds it and publishes it in the `anki` release after a push on `main`.

Examples requiring model providers, GPUs, or external services have not been run on these infrastructures.
