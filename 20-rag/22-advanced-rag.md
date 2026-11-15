# Advanced RAG — Flashcards
Tags: #flashcards #ai-engineering #rag #retrieval #llm
<!-- summary: hybrid search (BM25, RRF), ranking, query rewriting, HyDE and its limits, filtering by metadata and ACL, GraphRAG, agentic RAG, "lost in the middle", production problems (fresher, rights, re-indexing), RRF fusion and score scales, diversity of results, ceiling of the ranking. -->


What is hybrid search? <!--anki:783b3a7d537e53723532-->
?
The combination **lexical (BM25) + vector**, merged (e.g. **RRF**): robust to the exact terms (references, codes, names) that the vector only misses.
```text
RRF : score(doc) = Σ  1 / (k + rank_in_list)      k ≈ 60

doc A : rank 1 in BM25, rank 5 in vector search → 1/61 + 1/65 = 0,0318
doc B : rank 3 in BM25, rank 2 in vector search → 1/63 + 1/62 = 0,0320  ← better
```
The interest of the RRF: it only works on **ranges**, so no calibration of heterogeneous scores is necessary.

For example, a `AB-204` reference benefits from the lexical, while a reformulation of the problem can benefit from the embeddings. RRF does not prove that a document is relevant: it combines the available rankings. The parameter `k` of its formula is a smoothing constant, distinct from the number of results finally recovered.

---

What is reranking? <!--anki:72403c653b3e44335232-->
?
The **reranking reclassifies candidates** from the initial retrieving with a more expensive model, often a cross-encoder that examines question and pass together. It can improve their relevance and reduce the context transmitted.
```text
retrieval: 50 candidates → ranking: 5 passes → generation
```
This illustrative choice is based on the data and the latency budget. The gain is not guaranteed: check recall of candidates, ranking and then final quality.

A proof missing from the lot cannot be found by simple reclassification. Adding it to the lot allows you to test this ceiling. A good classification does not validate either freshness or rights ([[121-inference-costs|costs]]).

---

Do not confuse: recall and precision in a RAG? <!--anki:506d6d49793b6532463c-->
?
- **Reminder (recall@k)**: is the correct passageway **present** in the recovered k? It is the **ceiling** of the system: what is not reassembled can never be used
- **Precision**: how much of the reassembled passages is **useful**? It plays on the noise, cost and dilution of the context

Regular policy: **recover wide** for recall, then **reranker** for accuracy ([[96-evals-rag-agents|RAG evals]]).

---

What is query rewriting? <!--anki:76394545532971765776-->
?
**Reform or break down the question** before retrieving, as the user question is rarely the best query:
- **Multi-query**: multiple variants, merged results
- **Step-back**: a more general question, to go back to the useful context
- **Decomposition**: sub-questions for a multi-hop question
- **Contextualization**: rewrite "and for the last year?" in autonomous question, from the conversation history

Example of decomposition: "Is our telecommuting policy more generous than in 2023?" becomes two searches, current policy and 2023 policy, before the comparison. Cost: one more LLM call before the search.

---

What is HyDE? <!--anki:513c5b5f50533662435f-->
?
**Hypothetical Document Embeddings**: the LLM writes a hypothetical **answer** to the question, and we look for documents close to this answer rather than the question. An answer looks more like the passages sought rather than a short question: "why does my pod reboot in a loop?" produces a hypothetical passage mentioning `CrashLoopBackOff` and `OOMKilled`, terms of the documentation missing from the question.

Limitations: an additional LLM call, and a hypothetical **false** answer can direct the search to bad passages. Useful especially when questions and documents use different vocabularies.

---

What is metadata filtering? <!--anki:70794c6a37282d7b332c-->
?
To combine similarity and **structured filters** (date, source, holding, **permissions/ACL**) — essential for security: never find what the user does not have the right to see.

The rights come from the authenticated identity, never from a holder freely provided by the model. With pgvector, for example:
```sql
SELECT id, text FROM chunks
WHERE tenant_id = :tenant AND :group = ANY(allowed_groups) AND effective_date <= current_date
ORDER BY embedding <=> :question_vector LIMIT 10;      -- cosine distance
```
Spread the same isolation to caches and quotes. Test two users asking the same question with different permissions.

---

What is GraphRAG? <!--anki:654c65592a606b60292c-->
?
A RAG supported on a **knowledge graph**: useful for **multi-hop** or global questions (“what links between X and Y?”) where flat similarity fails.

For example, linking a company to its subsidiaries and then to the relevant contracts requires several explicit relationships. Depending on the architecture, the search runs through the graph or uses community summaries. The cost of extracting, resolving entities, and maintaining the graph must be justified by a measured gain against a simpler RAG.

---

What is agentic RAG? <!--anki:625d426536733d593a29-->
?
The **agent decides when and what to look for** He iterates (research) → Reading → new request) instead of a single upstream retrieval.

A first source can reveal a date or entity to be verified by a second search. This adaptation helps with complex questions, but adds calls and loop risks. Set a search budget, retain evidence, and stop with a partial response or abstention if the sources remain insufficient.

---

What production problems are specific to the RAG? <!--anki:6a455549472f7c24745b-->
?
The RAG must maintain consistency between **sources, indexes, rights, and caches**:
- Propagate changes, deletions, and access revocations, not just add documents.
- Version [[133-embeddings-representations|embeddings]] and chunking; a migration may require re-encoding the corpus.
- Detect loss of content at [[162-document-parsing|parsing]].

Example: A document deleted from the source remains exposed if its old chunks or a cached response survive. Follow the propagation delay and test this removal end-to-end. An index that is technically available but late on the rights is not a correct service.

---

Why does the order of chunks in context count? <!--anki:6e6c685336744b2e532a-->
?
Some models make less use of located evidence **in the middle of a long context** This is the "Lost in the Middle" effect. The order of the passages can therefore change the answer, Even if the sources are the same.

Test several orders: replay 200 questions with proof in position 1, 5 then 10 on 10 passes, and compare accuracy. Then place important proofs in positions well exploited by the model and remove redundancies. **This is not a universal rule start/end**: the effect also depends on the model, the task and the length of the related passes.

---

Why does the RRF merge stand up to different search engine scoring scales? <!--anki:6437333561303037353838643465623039383361623636653232656563323138-->
?
The **Reciprocal Rank Fusion** uses ranks rather than raw scores: a document receives a sum of `1 / (c + rang)` terms, with a positive constant `c` set for the experiment.

A BM25 score of 12 and a vector similarity of 0.8 are not directly comparable; their positions may be. Deduplicate by document or pass before interpreting the result. Merging does not create missing evidence from candidate lists and does not negate the effect of their depth. Then measure recall and final quality.

---

Why diversify the results after a hybrid search? <!--anki:6538326237613333316433333434383561623565663830613562353562643066-->
?
Several engines can find copies of the same passage. The **diversity** looks for complementary evidence rather than a ranking filled with almost identical variants.

A method like MMR combines relevance to the question and penalty of similarity with the passages already selected. Set this compromise on multi-aspect questions: too diversified brings documents out of subject. The exact deduplication and the constraints of rights must remain independent of this score.

---

## Scenarios

Scenario: your legal RAG can find the relevant documents (recall@20 of 0.95) but the answers remain average. What do you do? <!--anki:657e457c29693d3b524b-->
?
1. **Check**: the retrieval is doing its job, the problem is downstream, in the **classification** and the **context**
2. **Reranking**: a cross-encoder re-scores the 20 passages to keep only 3 to 5 really relevant
3. **Order**: test the position of the best chunks, for example at the beginning or at the end of the context, if the model is sensitive to "lost in the middle"
4. **Grounding**: mandatory quotes and abstention instructions if the context is not sufficient ([[143-hallucinations-grounding|hallucinations]])
5. **Measure** the triad: truthfulness, relevance of the response, relevance of the context ([[96-evals-rag-agents|RAG evals]])

**Trap**: Increase the top-k to “give more context,” which dilutes useful information.

---

Scenario: users ask questions such as "which suppliers of X's subsidiaries had an incident in 2025?", and your RAG vector always fails. What do you suggest? <!--anki:45777c3e74682b5f4b36-->
?
1. **Recognise question type**: this is **multi-hop** with aggregation, where flat similarity cannot answer ([[23-knowledge-graphs-ontologies|knowledge graphs]])
2. **Options**: query on a structured basis if the data already exists in the database, or **GraphRAG** if the information is in text
3. **Breaking down the question** in sub-questions (query rewriting) and leave a **Agent Iterer** between researches ([[31-agent-fundamentals|agentic RAG]])
4. **Compare** approaches on the same evals before investing in a graph, which extraction is expensive
5. **Attention to rights**: the graph path must respect the ACLs as the restrieval

**Trap**: Building a complete knowledge graph when ten well-made SQL queries were enough.

---

Scenario: After a embedding model change, the quality of the RAG collapses into production. What happened and how do you handle it? <!--anki:4e6821404a43506d753e-->
?
1. **Probable cause**: the index contains old vectors, queries are encoded with the new model. The two spaces are not comparable
2. **Return** immediately to the old model on the request side, time to correct
3. **Reindex** the entire corpus with the new model, in a separate index
4. **Toggle** by A/B test or canary, with comparison of the call@k on the golden dataset ([[112-model-cicd|CI/CD]])
5. **Prevent**: Version the embedding model with the index, and refuse a request if the versions differ

**Trap**: Re-index in place, which leaves the index in a mixed state for hours.

---

## Sources

- Supplement of the 14 November 2026 — Diversification by MMR: [Carbonell and Goldstein — MMR](https://www.cs.cmu.edu/~jgc/publication/The_Use_MMR_Diversity_Based_LTMIR_1998.pdf).

## Connections
- [[20-010-rag-permissions-versions|RAG: rights & versions]] — apply permissions, effective dates and source priorities
- [[21-rag-fundamentals|Basic RAG]] — Base
- [[35-context-engineering|Context engineering]] — placement and budget
- [[101-llm-security-guardrails|LLM Security]] — injection via documents, ACL
- [[31-agent-fundamentals|Agents]] — l'agentic RAG
- [[32-tool-calling|Tool calling]] — agentic RAG calls tools
- [[23-knowledge-graphs-ontologies|Knowledge graphs & ontologies]] — GraphRAG in detail
- [[134-vector-search-ann|Vector Search & Index ANN]] — HNSW, IVF, PQ, filtrage
- [[96-evals-rag-agents|Evals of RAG]] — measure each floor
- [[25-chunking-contextual-retrieval|Advanced Chunking & Contextual Retrieval]] — act on what is indexed
- [[27-search-agents-deep-research|Research agents]] — when a search is no longer enough
- [[113-monitoring-drift-feedback|Monitoring & drift]] — quality in production and feedback loop
- [[145-system-design-cases|Case of system design]] — of commented type architectures
- [[24-cognee|Cognee]] — an agent memory in knowledge graph
- [[131-transformer-architecture|Architecture Transformer]] — model internal operation
- [[141-system-design-llm|System Design LLM]] — design method
- [[69-roofline-prefill-decode|Roofline & Disaggregation]] — which limits each phase of the inference
- [[00-moc-ai-engineering|MOC AI Engineering]]
