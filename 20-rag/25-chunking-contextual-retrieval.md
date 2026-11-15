# Advanced Chunking & Contextual Retrieval — Flashcards
Tags: #flashcards #ai-engineering #rag #chunking #retrieval #llm
Verified on: 29 September 2026 — This factsheet lists products, versions or regulatory texts that are evolving quickly.
<!-- summary: chunks without context, contextual retrieval (gain, cost, prompt caching), late chunking, chunk size, small-to-big, semantic and propositional chunking, breadcrumb and metadata, policy comparison to call@k, calculation of overlap overcost, tables and units, parent-child under budget. -->


Why is an isolated chunk often not found? <!--anki:7a544f517c5831297e3c-->
?
Because it has **lost its context** by being split. "Revenue increased by 3%" does not say either **which company** or **what quarter**: neither its embedding nor its keywords correspond to the question "ACME's turnover in Q2 2025". The problem is not the index, it is **what has been indexed**.

Check this information in the source: inventing the missing context would make the passage easier to find, but less reliable.

---

What is contextual retrieval? <!--anki:5052216e2d52403b2b54-->
?
A technique published by Anthropic (2024): before indexing, a LLM writes for **each chunk** a short context sentence (50 to 100 tokens) from the **entire document**, which is **prefixed to the chunk**. We then calculate the embedding **and** index BM25 on this enriched text.
```text
[Background: excerpt from ACME quarterly report, T2 2025,
Financial results section.]
Sales increased by 3% compared to the previous quarter.
```

The prefix makes an isolated passage understandable: "3%" does not specify any company or period. Keep the original chunk and its source, however, because the added context is **generated** and may contain an error. Evaluate the recovery and fidelity of these prefixes, as well as the cost of their production during updates.

---

What is the gain and cost for the contextual retrieval? <!--anki:727b7357643b706e5729-->
?
**Gain** measured by Anthropic: **−49% of retrieval failures** (embeddings and BM25 contextualized), **−67%** by adding a reranker.

**Cost**: one LLM call per chunk, for ingestion only. The entire document is sent to each call, so the **[[123-aggressive-caching|prompt caching]]** is essential: the document is cached once, only the chunk and the response change. Re-ingesting a modified document repaints this cost.

---

What is Late Chunking? <!--anki:52446439345e515e6d-->
?
Invert the usual order: pass **the entire document** (or a large window) in a model of embedding to **long context**, then cut **the vectors of tokens** into chunks and average them (pooling). Each vector of chunk has "seen" the rest of the document, **without calling LLM**. Suggested by Jina AI (2024).

Limit: A embedding model is required that exposes vectors by token and accepts long documents ([[133-embeddings-representations|embeddings]]).

---

Do not confuse: Contextual Retrieval and Late Chunking? <!--anki:483b40683c78345a3126-->
?
- **Contextual retrieval**: adds context **in text**, written by a LLM. Also benefits **BM25**, remains readable and verifiable, but costs a LLM call per chunk
- **Late chunking**: adds context **in the vector**, by the encoder. No LLM call, but no effect on the lexical search and depends on the embedding model

The first is more expensive and more robust, the second more economical.

---

What are the effects of a chunk size that is too small or too large? <!--anki:436e5231376f26446864-->
?
- **Too small** (less than 100 tokens): accurate but **without context**, and the answer is broken between several chunks
- **Too big** (more than 1,000 tokens): the embedding **averages several subjects** and becomes blurred, and each reassembled chunk is expensive in context

Current starting point: **300 to 800 tokens** with 10 to 20% overlap, then **measure** multiple sizes on its own questions ([[21-rag-fundamentals|Start Settings]]).

---

What is the small-to-big (parent-child) pattern? <!--anki:6f4d265d7a2f3e534a41-->
?
**Look for small, Send back big** The index of **Small Chunks** (Phrase, paragraphs) for a specific search, and we return to LLM their **Parent Block** (Section, page) so that it has context. Variant **sentence window** : return the sentence found with the N neighboring sentences.

It decouples two conflicting needs: the **precision** of the research and the **completeness** of the context.

Deduplicate parents if multiple small chunks point to the same section, and cap the context returned. Preserve parent rights and versions; a relevant child does not justify exposing a larger unauthorized block.

---

Is semantic chunking worth its cost? <!--anki:67377e70797147715e59-->
?
**Not always.** Cutting where the embeddings of consecutive sentences diverge seems smarter, but published ratings (2024) show **no constant gain** on a well-tuned recursive cutting, for a higher cost of ingestion. **Document structure** (headings, sections) is often a better signal than similarity ([[162-document-parsing|chunking structurel]]).

Compare to similar context budget, not just equal number of chunks. Check for questions that require two neighboring sentences: a semantic break can separate a rule from its exception.

---

What is Chunking by Propositions? <!--anki:79456d2e71752a256331-->
?
Rewrite the text in **Atomic and autonomous proposals**, indexed separately. Example: "ACME provides 12 M€ from CA to T2 2025 » must retain **Plan**, the company, the period and the unit; ACME has achieved 12 M€ “Changes the meaning.

This granularity can improve factual research, but lose conditions, negations, or relationships between propositions. The LLM extraction adds cost and possible errors. Keep a link to the original passage, verify that it actually involves the proposition, and render its context if necessary. A proposition is a research object, not an authoritative new source.

---

Why enrich chunks with metadata? <!--anki:433a363b4023495b3046-->
?
- **Ariane's son** prefixed to the text (title of the document > section > subsection): from the context **free**, without appeal LLM
- **filterable fields** (date, source, language, access rights): filter **before** vector search ([[22-advanced-rag|Filtering and ACL]])
- **Stable identifiers** (document, page, position): incremental citations and updates

This is the first improvement to try: inexpensive, often effective.

---

How to compare two chunking strategies? <!--anki:6d51784b656f656e423a-->
?
1. A game of **real questions** with, for each, the **expected passes**
2. Re-index the **The same corpus** with each strategy
3. Compare the **recall@k** and **MRR** of the retrieval, then the quality of the final answers ([[96-evals-rag-agents|evals RAG]])
4. Also compare the **cost of ingestion** and the **number of tokens** injected per response

As the chunks change between strategies, we judge "expected passage found" by **text recovery**, not by chunk identifier.

---

Calculation: 10,000 Documents of 8,000 tokens They are cut in 16 Chunks 500 tokens. Each call receives document + chunk + 100 tokens set-off and product 75 tokens, To 1 €/M as input and 5 €/M out. What cost without cache then with the document written once to 1.25× and reread 15 Time to 0.1× ? <!--anki:6336316138626364306238353434323662316364643334376639656430306536-->
?
With the **hypothetical rates** and the 160,000 calls of the statement:
```text
cacheless entry: 160,000 × 8,600 / 1e6 × 1 = 1,376 €
entry with cache: 80 × (1.25 + 15 × 0.1) + 96 = 316 €
output unchanged: 160,000 × 75 / 1e6 × 5 = 60 €
total without cache: 1,436 €; with cache: 376 €
```
The 80 M tokens represents the documents; the remaining 96 M, chunks and instructions. The gain assumes the fifteen proofreadings actually served from the cache. Expiration, different prefixes and additional attempts change the invoice. It is a cost of ingestion, to be reevaluated during the modifications.

Unhidden instructions and chunks still cost 96 € entry in this scenario. The cache here is about the document placed in a reusable prefix; it does not make the other parts of each call free.

---

Calculation: how much does an overlap of 100 tokens create for chunks of 500 tokens on a long document? <!--anki:3966666139393564316138613438393938636261386464333563666635393730-->
?
The **chunk stride** is `500 − 100 = 400` tokens. For a very long document, the total indexed volume is approximately multiplied by `500 / 400 = 1,25`, either **25% of tokens Additional**.

The cost of embedding and the number of vectors increase in this ratio if the other settings remain fixed. The document edges and the structural slicing change the exact result. Deduplicating the neighboring passages to the evaluation: finding several almost identical chunks does not mean covering more evidence.

---

Why can a table cut by tokens number produce misleading RAG evidence? <!--anki:3030656130313936623438653432646338343636623266383061336363353564-->
?
The value can be separated from **its header, unit or period**. "12.5" without knowing if it is millions of euros or a percentage is not actionable proof.

Preserve the line/column structure and replicate the useful headers in the pieces, with provenance. For a multipage table, check the repeated headers and notes. Test the reconstruction of a cell with its full meaning, not just the presence of the number in the index.

---

How to limit context when multiple small chunks point to the same parent? <!--anki:6336393762333634343536653463656139346339613366386364366661333266-->
?
**Deduplicate parents before expansion**, then limit the total volume. Five relevant children of the same chapter should not lead to injecting five times this chapter.

If the parent is too large, select windows around the passages with the necessary titles and references. Measure the coverage of evidence after expansion: a reminder gain at the child level can be canceled by truncation of the final context. Keep fine locations for quotes.

---

## Scenarios

Scenario: your RAG on 3,000 financial reports often answers "information not found" while the number is in the corpus. The chunks do 400 tokens. How do you proceed? <!--anki:7126512e53305a26792c-->
?
1. **Diagnose**: on 50 missed questions, is the right passage in the top 20? If not, it's the retrieval
2. **Read the chunks**: they often say "turnover" without a company name or period
3. **Add the breadcrumb thread** (company, year, section) to each chunk, at no cost LLM
4. **Test contextual retrieval** with prompt caching, then add a **reranker** ([[22-advanced-rag|reranking]])
5. **Measure** call@k before and after, and total ingestion cost

**Trap** : increase the top-k to "bring everything back", which drowns the model without making the chunks more findable.

---

Scenario: You are asked to pass the entire corpus in semantic chunking "because it is the state of the art". The corpus is well-structured technical documentation in Markdown. What do you say? <!--anki:7a253f545f55776c6c67-->
?
1. **Remind the goal**: the chunking is judged at call@k on our questions, not fashionable
2. **Finding the corpus asset**: Markdown titles already give reliable boundaries of meaning
3. **Propose a comparison**: cutting by sections with Ariadne thread, against semantic chunking, on the same set of questions
4. **Rate** the cost of ingestion and re-ingestion of each option
5. **Decide on measures**, and document the choice in an ADR ([[147-ai-technical-leadership|ADR]])

**Trap**: Change your chunking strategy without an eval game, and discover regression by users.

---

## Sources

- [Anthropic — Contextual Retrieval (2024)](https://www.anthropic.com/engineering/contextual-retrieval)

## Connections
- [[21-rag-fundamentals|RAG — Fundamentals]] — basic chunking strategies
- [[22-advanced-rag|RAG — Advanced]] — hybride, reranking, filtres
- [[162-document-parsing|Parsing of documents]] — structure before cutting
- [[133-embeddings-representations|Embeddings]] — models with long context and late interaction
- [[123-aggressive-caching|Caching]] — make contextual retrieval affordable
- [[96-evals-rag-agents|Evaluation of GARs]] — judge a strategy to call@k
- [[00-moc-ai-engineering|MOC AI Engineering]]
