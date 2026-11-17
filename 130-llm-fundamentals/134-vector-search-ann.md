# Vector search & ANN indexes — Flashcards
Tags: #flashcards #ai-engineering #fundamentals #vector-search #rag
<!-- summary: brute force or ANN, index recall or retrieval recall, calculation of the memory of an HNSW index, HNSW and its parameters, IVF, Product Quantization, scalar and binary quantization, DiskANN, filtering, index recall, pgvector or dedicated base, exploitation, sizing, processing of ex æquo in an ANN benchmark, recall under filtering. -->


Why not do an exact search (raw force) of the nearest neighbors? <!--anki:434b37366f67544e55-->
?
The exact search compares the query to **all eligible vectors**: linear cost in number and size, and provides a useful reference for measuring the recall of a **ANN** index, which exchanges accuracy for less work.

There is no universal size threshold: GPU, batch, size, filters and target throughput count. A huge global corpus can become small after a selective filter. Compare time and memory to the SLO, then measure `recall@k` of the ANN against this exact reference, with the same filters.

---

How does HNSW work? <!--anki:4a582545506f752e5a6e-->
?
**Hierarchical Navigable Small World**: a **multi-level graph** where each vector is connected to its close neighbors. The upper, sparse levels serve as **highways**; the search goes down from level to level following **glow** the nearest neighbor. High recall and low latency, but **gourmand in memory** (vectors + graph in RAM).

At the finer level, expanding the number of candidates explored usually increases recall and latency.Measuring the curve rather than looking for a magic value; a poorly constructed index does not always correct itself with a larger search budget.

---

Which HNSW parameters solve the recall/cost trade-off? <!--anki:76525d40386e2f777647-->
?
- **M** controls graph connectivity: More links cost more memory.
- **ef_construction** expands research to construction: best potential graph, more expensive indexing.
- **ef_search** expands the exploration to the query: runtime lever of the recall/latency compromise.

Example: Set `k=10`, then compare multiple values of `ef_search` to the ten neighbors of an exact search on a sample. Report @10 and p95 latency with the same filters.

Increasing these parameters does not guarantee a useful gain; the effects depend on the data and implementation. `ef_search` is not the number of results returned.

---

How does an IVF index work? <!--anki:72553a316c3773444028-->
?
**Inverted File**: partition the space into **k clusters** (k-means). At request, we only look for the nearest **nprobe clusters**. Less memory than HNSW and fast build; reminder set by **nprobe**, which drops if a neighbor falls into an unvisited cluster.

Increasing **nprobe** explores more lists: recall can go up, but so can the research work. If the data changes significantly, the learned centroids may misrepresent the new space. Compare the found neighbors to an exact search on a sample and measure latency and recall together, with the same business filters.

---

What is Product Quantization (PQ)? <!--anki:484430554d377855643f-->
?
Compression: Each vector is divided into **m subvectors**, each replaced by the nearest **centroid index** in a small dictionary. A vector of 768 floats (3 KB) can hold in **a few tens of bytes**. The distances become **approximate** → is often combined with a **re-scoring** on the full vectors.

With 96 subvectors and 256 centroids per dictionary, each index holds on a byte: the code occupies 96 bytes, excluding dictionaries. Centroids are learned on a representative corpus; their quality conditions the degradation of the recall.

---

What other vector compression techniques exist? <!--anki:7328294347582a3e372a-->
?
- **Scalar quantization** : float32 → **int8** (÷4), perte minime.
- **Binary quantization**: 1 bit by dimension (÷32), search by **Hamming distance** very fast, then **re-scoring** the best candidates in full accuracy.
- **Troncature** of the embeddings [[133-embeddings-representations|Matryoshka]].

The reduction factors relate to the **values of the vectors**, not the metadata, the graph or a copy retained for reclassification. The quality loss depends on the model and the data; it is not always minimal. Evaluate each compression with an exact reference and check the cost of re-scoring the candidates.

---

What is DiskANN and when to use it? <!--anki:242e5d653b58264e72-->
?
A graph index (family **Vamana**) designed to live **on SSD**, with only vectors compressed into RAM. It allows to serve **billion vectors** on a machine at reasonable cost, where HNSW would require a huge RAM.

The compromise shifts some of the RAM constraint to SSD **reads and their latency**. It still requires memory for hot structures and a cache policy. Test a cold load and then compete: a good result on a few queries does not guarantee the same p99 when a lot of searches request the disk.

---

Why is metadata filtering difficult with an ANN index? <!--anki:726234383c2e6259602a-->
?
- **Post-filtering** (look for top-k and then filter): if the filter is **Selective**, he/she/it may not stay **no result**.
- **Pre-filtering** (restrict and search): breaks the navigation of the HNSW graph and can fall back into brute force.

The modern bases do **integrated filtering** at the crossing; to be tested with filters **very selective** (ACL, holding) which are the critical case ([[22-advanced-rag|Filtering and ACL]]).

---

How to measure the quality of an ANN index? <!--anki:632f2b3f4d4d244e3332-->
?
By the **recall@k of the index** in relation to the exact **search** on a sample of queries (what share of the real k nearest neighbors is found), set against the **latence p95** and the **QPS**.

Procedure: draw a few hundred to thousands of actual queries, calculate their k real neighbors by brute force offline, then compare each candidate setting. Remeasure when the corpus grows or after a reconstruction: at constant setting, the recall of a graph index can decrease with size. Measure also under the metadata filters used in production.

---

Dedicated vector base or extension of an existing one? <!--anki:68674461647c78563b3c-->
?
Compare a **extension of an already-operated system** and a **specialized database** on the same need: recall, rights filters, freshness, latency, availability, and cost of operation.

An extension can simplify transactions, joins and backups. A specialized database can offer more suitable search or distribution mechanisms, without automatic superiority. The threshold depends on the dimensions, index and load, not just the number of vectors. Replay representative traffic with filters and updates, then test restoration and revocation; starting with the existing one is a baseline to be measured, not an obligation.

---

What operating topics does a vector base pose? <!--anki:75695a595f4272337c3e-->
?
- **Updates and deletions** (HNSW graphs mishandle massive → reconstruction deletions).
- **Re-indexing** on a embedding model change.
- **Multi-tenant**: one collection per customer or one hold filter.
- **Backup**, replication, **memory** (RAM sizing), and **right to erasure** ([[154-gdpr-llm|RGPD]]).

Check for **observable freshness** after inserting, updating, and deleting, including in replicas and caches. A backup must be able to restore compatible indexes and metadata. Deletion policies vary by implementation; test accumulation of deletions and rebuild instead of assuming that a functional index will remain performing without maintenance.

---

Calculation: estimate the memory of 10 million vectors to 768 dimensions float32 and a simplified HNSW graph of 32 links of 4 bytes per vector. How much does it vary if the vectors pass into int8? <!--anki:4b382a2f6a796f4b7621-->
?
With the simplified assumptions of the statement, in **Go decimal**:
```text
vectors float32 = 10 000 000 × 768 × 4 = 30,72 GB
graphe = 10 000 000 × 32 × 4 = 1,28 GB
total simplified float32 = 32.00 GB
vectors int8 = 10 000 000 × 768 × 1 = 7,68 GB
total simplified int8 = 7.68 + 1.28 = 8.96 GB
```
Only the share of vectors is divided by four: the total decreases by about **3.57 times**. Add metadata, allocation structures, graph levels, buffers and possibly full-precision copy. This calculation gives a pedagogical floor, not the exact RAM of an HNSW implementation.

For a real budget, also measure index construction and maintenance. A compression that holds in memory can move the cost to distance calculations or re-scoring; check reminder and latency together.

---

Do not confuse: the recall of an ANN index and the recall of the retrieval? <!--anki:4e435f743a47466c2161-->
?
- **ANN Index Reminder**: the share of **nearest real neighbors** (in the sense of the exact search) that the index finds. It measures **approximation** of the index
- **Retrieval reminder** (recall@k of a RAG): the share of **relevant documents** for the question that have been reassembled. It measures **end-to-end quality**: chunking, embedding model, query and index

An index to 99% ANN reminder can give a bad RAG if the **embedding** does not bring the good passages closer. We set `ef_search` with the first, we judge the system with the second ([[96-evals-rag-agents|evals RAG]]).

---

Why can two different exact top-k be equally valid for evaluating an ANN index? <!--anki:6666643537386462326234643432363439366238303062393637343430636562-->
?
The **Ex Distances æQuo** at the border of the top-k can admit several exact lists. Comparing their unique identifiers to a single reference list can penalize a geometrically equivalent result.

Define the treatment of equalities before the benchmark: deterministic separation or distance equivalence rule with justified tolerance. Keep identical normalization, precision and filters. Inspect vector duplicates and numerical sensitivity. This convention concerns index recall; it does not prove that all equidistant documents are equally relevant to the user.

---

Why measure ANN recall with the same filters as production? <!--anki:3036616333353232343233303430663239366537653930333632333766373733-->
?
Filters can **significantly reduce the allowable set and change the path of the index**. A good reminder without a filter does not guarantee that of a less represented stand.

Compare to an exact search on the authorized subset, with the same metric and even k. Varying the selectivity and the size of the segments. Also measure latency: increasing the search effort to restore the recall can change the useful capacity.

---

Calculation: an exact search returns 10 neighbors; the ANN index finds 8 in its 10 results, without ex æquo. What call@10 of the index and what does it not measure? <!--anki:6165303139393730663630393431636462636562633332383237663365633538-->
?
The recall is **8 / 10 = 0.8**. It measures accuracy to the exact search with this representation and metric.

It does not say whether the ten exact neighbors are relevant to the user. A perfect index can serve as a bad model of embedding. Evaluate separately index approximation, retrieval quality and final response, and then aggregate on representative queries.

---

## Scenarios

Scenario: your RAG multi-tenant sometimes returns zero results for a client, while its documents exist in the index. What cause do you suspect? <!--anki:4b34572d3f6c5d796e43-->
?
1. **Metadata filtering** combined with the ANN index: in post-filtering, the top-k may not contain any client documents
2. **Test with very selective filters**, which are the critical case in multi-tenant
3. **Choose the right strategy**: filtering integrated in the crossing, or collection by client
4. **Never release the filter** to “get results”: this would be a leak between customers ([[22-advanced-rag|ACL]])
5. **Monitor** the rate of queries without result, per customer

**Trap** : increase the top-k to compensate, which hides the problem without correcting it.

---

Scenario: your team hesitates between pgvector in the existing PostgreSQL database and a dedicated vector base. How do you slice? <!--anki:41243453456f7523645d-->
?
1. **Estimate volumetry**: up to a few tens of millions of vectors, the extension often suffices
2. **Counting the benefits of the existing**: a single base to operate, transactions, joins, ACL and lexical search already available
3. **Look at advanced needs**: quantization, powerful filtering, large-scale multi-tenant, massive updates
4. **Test on your corpus**: index against exact search, p95 and QPS latency
5. **Do not forget the exploitation**: backups, re-indexing, memory, data deletion

**Strap**: Choose a dedicated base for 200,000 vectors, and add a component to operate without profit.

---

## Connections
- [[133-embeddings-representations|Embeddings & Representations]] — What we index
- [[21-rag-fundamentals|RAG — Fundamentals]] — ingestion and query pipeline
- [[22-advanced-rag|Advanced RAG]] — hybride, filtres, ACL
- [[96-evals-rag-agents|Evals of RAG]] — recall
- [[68-quantization|Quantization]] — the same ideas applied to weights
- [[20-011-retrieval-quality-metrics|Retrieval quality metrics]] — AP/MAP, RR/MRR, relevance judgments and evidence coverage
- [[00-moc-ai-engineering|MOC AI Engineering]]
