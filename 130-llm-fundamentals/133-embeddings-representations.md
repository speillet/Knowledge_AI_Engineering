# Embeddings & representations — Flashcards
Tags: #flashcards #ai-engineering #fundamentals #embeddings #rag
<!-- summary: Contrastive learning, similarities, bi-encoder or cross-encoder, ColBERT, Matryoshka, prefixes, choice (MTEB), fine-tuning of embeddings, model change, SPLADE, limits, calculation of the link between cosine and distance L2, standard vectors, difficult negatives. -->


What is a embedding model? <!--anki:6b565249636a404c3878-->
?
A model (often a BERT-type **encoder**, or an adapted LLM) that transforms a text into a dense **vector of fixed size** (384 to 4,096 dimensions) such that texts **semantically close** have vectors **close**. This is the basis of semantic search, [[21-rag-fundamentals|RAG]], clustering and deduplication.

These dimensions are examples, not universal limits. Two models each producing 1,024 dimensions do not necessarily have a compatible space: after migration, reencode documents and queries with the expected torque, and then measure the recall.

---

How is a embedding model driven? <!--anki:756445307677664a4864-->
?
By **Contrastive Learning** Bringing the pairs closer together **Positive** (question ↔ passage that answers it, paraphrases) and we move them away **negative**, other examples of batching (**In-Batch Negatives**) more of **Hard Negatives** (Near but false passages). The typical loss is **InfoNCE**.

A good negative is plausible but does not answer the question, such as a procedure for another product. A really relevant passage treated as negative sends a contradictory signal. Treating pairs and false negatives; optimizing only the training loss is not enough to guarantee a better retrieval on new questions.

---

What similarity measures to use between embeddings? <!--anki:716c647e42323e3f283e-->
?
The **cosinus** compares directions, the **scalar product** also depends on the standards, and the **euclidean distance** measures the geometric deviation. Use the recommended measurement and standardization for the model and check their support by the index.

For vectors of standard 1, scalar product and cosine coincide; the distance L2 gives the same classification by the relation `L2² = 2 − 2 × cosinus`. Without normalization, this equivalence disappears. The calculation cost depends on the engine and data: no measurement is universally the fastest nor a business confidence score.

---

Do not confuse: bi-encoder and cross-encoder? <!--anki:4c4b5539596c715d5251-->
?
- **Bi-encoder**: encode query and document **separately** → documents are indexed in advance, the search is fast. This is the model of embedding.
- **Cross-encoder**: read **request and document together** → much more precise but a passage in pairs, so reserved for the **reranking** of a few dozen candidates ([[22-advanced-rag|reranking]]).

The cross-encoder cannot find any missing proof of the candidates: if the correct document never enters the top-50, improving only the ranker will not correct this failure.

---

What is Late Interaction (ColBERT)? <!--anki:4b736c5829233b5b7e76-->
?
A compromise: we keep **a vector per token** of the document, and the score is the sum, for each token of the query, of its **maximum similarity** with a token of the document (**MaxSim**). More precise than a single vector, pre-calculateable, but **much heavier** to store.

This preserves several clues to a document instead of condensing everything into a single vector. For example, two specific words in a question may correspond to two distinct places in the passage. Document vectors are calculated in advance, but their aggregation depends on the query; predict the cost of storing and searching for multiple representations.

---

What is embeddings Matryoshka? <!--anki:4a757a636a5735704d36-->
?
embeddings trained so that **the first dimensions** carry most of the information: you can **truncate** the vector (e.g. 3,072 → 256 dimensions) with low loss. Useful to **reduce storage** and do a **two-step search** (small vector to preselect, large to reclassify).

The property must be **learned by the model**: arbitrarily cutting an ordinary embedding does not offer the same guarantee. After truncation, apply the expected normalization and measure the recall to each candidate dimension. A too short preselection may lose the right document before reclassification, even if the complete vector would be able to find it.

---

Why do some models require a prefix (instruction)? <!--anki:753d3929536a2937733e-->
?
The **asymmetric** models distinguish between **request** and **document** (e.g., prefixes "query:" and "pass:", or a task instruction). Forgetting the prefix, or putting the wrong one, **clearly degrades the recall**: the model documentation is authoritative.

The prefix indicates to the model the **role of the text to be encoded**, according to its training. For example, a short question and the paragraph that answers it do not have the same form, but must become close. Version this preparation with the index and avoid comparing a new request prefix to a corpus encoded according to an incompatible convention.

---

How to choose a embedding model? <!--anki:4f7c267c5168495d2b74-->
?
- The leaderboard **MTEB** for a pre-sorting, **filtered on his language and his task** (retrieval, not classification).
- **Test on his own game** (recall@k), the only reliable criterion.
- **Max input length**, **dimension** (storage cost), **multilingual**, **license**, **API or self-hosted**, latency.

Keep corpus, questions, and comparable indexing methods to isolate the effect of the model. Also examine difficult segments: exact references, short queries, and long documents. A good average score can hide a recurring business failure. The final choice combines relevance and operating constraints; gaining a recall point can cost a lot of memory or latency.

---

When to fine tune a embedding model? <!--anki:4a67347976475d723761-->
?
When the domain has a specific **vocabulary** (legal, medical, internal code) and the generic models miss obvious matches for an expert. With **a few thousand pairs** (question, passage), often **generated synthetically** then filtered, and hard negatives, the recall gains are frequently **several points**.

Before training, check parsing, chunking, prefixes and quality of labels: a defect of ingestion is not necessarily corrected in the weights. Separate training and test by families of documents to avoid the quasi-doubles. The necessary volume and the gain are not guaranteed; compare to the initial model and monitor regressions outside the specialized field.

---

What happens when you change the model of embedding? <!--anki:467e29694e6252774e30-->
?
The vectors of two models **are not comparable**: it is necessary **to re-encode the whole corpus** and reconstruct the index. Hence the interest of **version** the model of embedding with the index, and to provide the **re-indexation** (cost, time, double index during the toggle).

Two vectors of the same size can represent different **spaces**; the same size is not enough to mix them. During the migration, route each request to the encoder corresponding to its index, test the callback and keep a backlash. Also include preprocessing, prefixes and normalization in the version, because they influence the representations.

---

What is embeddings sparse (SPLADE)? <!--anki:6d6f7272495a6b473372-->
?
Representations **Hollows** on the vocabulary, learned by a model: each dimension corresponds to a **term**, with expansion to neighboring terms. They combine **lexical accuracy** BM25 (names proper, codes, references) with a part of **Semantic**, and combine well with the embeddings Dense in **Hybrid Research**.

The representation assigns weights to a small number of lexical dimensions and can activate terms absent from the original text. It is exploited with an adapted inverted index. This expansion brings some reformulations closer together, but can introduce noise; measure the effect on rare references and business vocabulary instead of equating any expansion with an improvement.

---

What are the limits of dense embeddings? <!--anki:4741334661243f797b34-->
?
A dense vector compresses the text: it can lose details, constraints or rare distinctions. The **semantic proximity is neither equality nor proof**.

Example: `AB-120` and `AB-102` may seem close together while designating two incompatible parts; “allowed” and “unauthorized” also share a lot of context. Combine lexical search, exact filters and ranking depending on the task.

A long document sometimes dilutes a local fact: use the [[21-rag-fundamentals|chunking]]. Test negations, identifiers and business vocabulary on its data; a good general score does not guarantee recall in a different domain.

---

Calculation: for two standardized cosine vectors 0.8, what Euclidean distance is obtained and why can the classification be equivalent? <!--anki:6465313239333534643634613465343862643836633239383463356235386337-->
?
For two 1 standard vectors, `||u − v||² = 2 − 2 × cos(u,v)`. With a cosine of 0.8, the distance is `√0,4 ≈ 0,632`.

Minimizing this distance is therefore equivalent to maximizing the cosine **if all vectors are effectively normalized**. Without this assumption, standards influence the scalar product and distance, and rankings may change. Check normalization at indexing and query; a similarity threshold is not directly a relevance probability threshold.

---

Why can the scalar product classify two embeddingss differently than the cosine? <!--anki:6264303934396465653338323464663439623030613138333932616361373766-->
?
The scalar product depends **on the angle and standards**; the cosine only keeps the angle. A high standard vector can get a high score without being the closest in the direction.

When all vectors are normalized to standard one, the two rankings coincide. Check what the model and index are waiting for before normalizing: the standard can carry information in some workouts.

---

Why are false negatives dangerous in embeddings contrast training? <!--anki:3263333165656165343837643466623462383164623438393332303235326337-->
?
A negative-labeled passage may be **another relevant response**. The objective then causes the model to move away from elements that should stay close.

Controlling difficult negatives, deduplicating and accepting multiple positives when the task allows. Random negatives are sometimes too easy; close negatives require more validation. Measure the retrieval on questions and sources independent of the pair construction.

---

## Scenarios

Scenario: your legal RAG misses matches that a lawyer finds obvious, despite a well-ranked embedding model. What do you do? <!--anki:4144587d52417c345f3f-->
?
1. **Check the ranking**: a good score on a general leaderboard does not say anything about your domain or language
2. **Measure on your data**: recall@k on a set of real questions, the only criterion that matters
3. **Check for prefixes**: Some models wait for a different statement for the query and for the document
4. **Add lexical**: hybrid search retrieves references and articles of law ([[22-advanced-rag|hybride]])
5. **Consider a fine-tuning**: a few thousand question-passage pairs of the domain, with difficult negatives

**Strap**: Choose a embedding model from its overall score, without filtering by language and task.

---

Scenario: Ton corpus of 20 million chunks is expensive in vector storage, and the search slows down. What options before buying servers? <!--anki:7878497b7b7e37685a4e-->
?
1. **Reduce dimension**: a Matryoshka model can truncate vectors with low loss
2. **Compress**: scalar quantization in int8, even binary with re-scoring of the best candidates ([[134-vector-search-ann|index ANN]])
3. **Two-step search**: small vector to preselect, complete vector or ranking to rank
4. **Review the chunking**: too small chunks unnecessarily multiply the number of vectors
5. **Measuring the impact** on the recall at each step, not just the storage gain

**Trap**: Compress vectors without ever checking what the callback becomes.

---

## Connections
- [[134-vector-search-ann|Vector Search & Index ANN]] — store and search vectors
- [[21-rag-fundamentals|RAG — Fundamentals]] — l'usage principal
- [[22-advanced-rag|Advanced RAG]] — hybrid search and ranking
- [[131-transformer-architecture|Architecture Transformer]] — encoders and decoders
- [[96-evals-rag-agents|Evals of RAG]] — measure recall
- [[123-aggressive-caching|Caching agressif]] — cache d'embeddings
- [[161-vision-language-models|Vision-language models]] — input images and screens
- [[162-document-parsing|Parsing of documents]] — transform PDF and scans into structured text
- [[25-chunking-contextual-retrieval|Advanced Chunking]] — Make Every Chunk Found
- [[68-quantization|Quantization]] — reduce accuracy to gain memory and speed
- [[174-recommendation-ranking|Recommandation & learning to rank]] — representations to search for candidates
- [[00-moc-ai-engineering|MOC AI Engineering]]
