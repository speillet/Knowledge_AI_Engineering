# RAG — Fundamentals — Flashcards
Tags: #flashcards #ai-engineering #rag #retrieval #llm
<!-- summary: RAG or fine-tuning, ingestion and query pipeline, chunking strategies, embeddings, vector bases (HNSW, pgvector, Qdrant), top-k, grounding and citations, recall@k, when not to do RAG, diagnostic with reference context, evidence budget, sub-question coverage. -->


What is the RAG? <!--anki:45677223625926775b30-->
?
**Retrieval-Augmented Generation**: we **recover relevant passages** in a knowledge base and we **inject them in the context** of the LLM before it generates its response.

For example, an assistant retrieves the refund procedure before replying by quoting the passage. The documents are consulted at runtime: **The weight of the model does not change**. The quality depends on both the search and the use of sources; a RAG does not automatically prevent hallucinations.

---

What problem does the RAG solve? <!--anki:6d5e59414b626f25585e-->
?
The **RAG** makes it accessible to the execution of selected sources, including internal or updates, without having to retrain the model for each modification.

It responds to a need for access and traceability, not to a guarantee of truth. A document can be out of date, inaccessible to that user, poorly retrieved or misinterpreted. The model can also already know some facts of the corpus. Check freshness, rights, relevance and support of assertions; the existence of a documentary database is not enough to make all answers reliable.

---

RAG or fine-tuning to bring knowledge? <!--anki:4c7d4823364c5e317e31-->
?
Choose the **RAG for up-to-date and traceable knowledge**, the **[[51-fine-tuning-adaptation|fine-tuning]] for learning behavior** (format, tone, task). This is not an absolute boundary: the training can memorize facts, without guaranteeing their restitution or erasure.

Example: for a catalog whose prices change every day, recover the current rate rather than retrain daily. A fine-tuning can then improve the extraction or the response structure. If the right information is already provided but poorly exploited, work the behavior; if it is missing or is out of date, first correct the source and its recovery.

---

What are the steps in a RAG pipeline? <!--anki:416b4c68676631527378-->
?
```text
Ingestion : documents → parsing → chunking → embeddings → vector store
Request: question → embedding → retrieval top-k → prompt increased → LLM → answer
```

The **ingestion** prepares the passages and their metadata; It comes back when the sources change. At each **Query**, the search selects the authorized passages, possibly reclassified, Then the model builds a sourced response. Keeping document identifiers and versions helps diagnose an error. The search can also be lexical or hybrid: a vector base is not mandatory.

Useful control: keep the passages recovered for a test case. Absent evidence of context: examine ingestion and research; present but misused evidence: examine generation.

---

What is chunking and why is it critical? <!--anki:4165744b3d31647a653d-->
?
The **cutting of documents into indexable** passages. Too big: noise and wasted context. Too small: we lose meaning. It is often **the first lever of quality** of the RAG.

Preserve units of meaning: a title with its paragraph, an array with its headings, a rule with its exceptions. Evaluate several cuts on real questions and check if the passage recovered is enough to answer. Overlap limits cuts but increases storage and duplicates.

---

What chunking strategies exist? <!--anki:5062235d2c4f48603f28-->
?
- **Fixed Size** (tokens) with **overlap** (overlap)
- **Recursive / structural**: titles, paragraphs, sections Markdown
- **Semantic**: cut where subject changes
- **Parent-child**: index small chunks, return the parent block

The choice depends on the **Unity of meaning to be found**. Cutting a procedure between a condition and its exception can make the passage misleading. Overlap preserves context but adds duplicates; the parent-child gives more explanations but consumes more tokens. Compare strategies on annotated questions, in a comparable context.

---

What are the starting settings for a RAG? <!--anki:755f707256696747215b-->
?
```text
Size from chunk 300 to 800 tokens (structural preferably)
Overlap 10 to 20% the size of the chunk
top-k recovered 20 to 50 before reranking
top-k final 3 to 8 chunks in context
Context added document title + section path
```
These are **starting points to measure**, not truths: the right setting depends on the documents and is valid at call@k ([[96-evals-rag-agents|RAG evals]]).

Change one parameter at a time on a fixed set of questions. Also measure the accuracy of the passages, the fidelity of the response, the latency and the number of tokens transmitted. A better reminder is not enough if the additional passages drown the information or exceed the context budget.

---

What is a embedding? <!--anki:714a71323d3b2f513621-->
?
A **embedding** is a digital vector learned to represent a text in a space where a proximity measurement helps to find relevant content. Cosine similarity is common, but depends on the training of the model.

Queries and documents must use compatible **encoders in the same space**, sometimes with separate prefixes or encoders provided by the model. High proximity is neither a proof of identity nor a probability of truth. Changing models usually requires recalculating vectors ([[133-embeddings-representations|embeddings in detail]]).

---

Do not confuse: semantic similarity and relevance? <!--anki:724f3423233a34542d60-->
?
Vector search ranks by **near sense**, which is not the same as **answering the question**:
- "flu symptoms" and "flu treatment" are very close, and one does not respond to the other
- a negation changes the meaning without moving the vector a lot

Hence the **reranking** (which evaluates the question-passage pair) and the **hybrid search** for the exact terms ([[22-advanced-rag|Advanced RAG]]).

A passage on the right product but its previous version can remain very similar. Relevance also requires checking the constraints of version, date and perimeter of the question.

---

What is a vector base? <!--anki:77764970652b4b3d5857-->
?
A **vector database** stores vectors, their identifiers, and metadata, and then finds elements close to a query in a metric. An approximate index, such as **HNSW**, exchanges a little reminder for less computation; an exact search remains possible on small corpora.

Jointly evaluate recall, latency, memory, updates and access filters. The number of vectors alone does not guarantee a response in milliseconds: dimension, filters and hardware also count.

---

How to choose the top-k of a RAG? <!--anki:6b342c707e4867592653-->
?
It is a compromise: **k too small** → missing information (**recall** low); **k too large** → noise, cost and dilution of the context. We often recover large, then filter or on [[22-advanced-rag|re-classe]].

Distinguish the number of **candidates retrieved** from those actually sent to the model. On an annotated game, increase the first until a satisfactory reminder, then limit the second according to the accuracy and budget of tokens. Deduplicating the passages avoids spending this budget several times for the same proof.

---

What is the main limit for vector-only retrieval? <!--anki:4d2f444e6238555b4c3b-->
?
Vector proximity can be difficult to distinguish between **exact references**, numbers, acronyms or rare names. This risk depends on the model, data and query; not all product codes are necessarily missed.

Compare lexical, vector and hybrid search on annotated cases. A lexical branch helps preserve matches like `AB-123`, while the vector finds paraphrases. Merging and ranking can improve the result, without automatic guarantee. Measure recall of candidates and quality of the passages finally transmitted to the model.

---

How to make a RAG response verifiable? <!--anki:737874235b314a4a3373-->
?
By asking the model to **quote its sources** (chunk identifiers) and **respond "I don't know"** if the context doesn't contain the information: this is the **grounding**.

The application must verify that each cited identifier exists and refers to an accessible passage. Then, check that the passage **actually supports the assertion**: a valid citation may be off topic. Presenting the source and its date helps the user to verify; a citation instruction alone does not guarantee fidelity.

---

How to evaluate a RAG? <!--anki:79282e50452d245d4c69-->
?
Separately: the **retrieval** (**recall@k**, MRR: has the correct passage been recovered?) and the **generation** (**faithfulness**, relevance of the answer), on a [[92-chainforge-evals-prompts|golden dataset]] of questions.

Add unanswered questions to the corpus to test abstention and cases with access restrictions. If evidence is missing in retrieved passages, correct the search; if present but misused, correct the generation. Also measure latency and cost in order to compare deployable variants.

---

When not to make RAG? <!--anki:495f6e2451306c4a7269-->
?
Avoid adding research if it does not add anything as needed:
- **Corpus that really fits in the useful budget**: compare the direct injection, possibly with cache, to the retrieval.
- **Format or behavior**: study first prompt, constraints or adaptation.
- **Structured aggregation**: Use a query or tool that has schema, filters, and result validated.
- **Task without the need for external sources**: Measure a baseline without a trace.

A long advertised window does not guarantee that all the evidence will be used properly. Even an SQL query can be false; validate the system retained on its errors.

---

Calculation: 50,000 documents from 10 pages contain 500 tokens/page. Without overlap, with chunks from 500 tokens, embeddings to 0.02 €/M and float32 vectors of dimension 1,024, what cost of embedding and raw storage? <!--anki:3339373433333537663864353435373962653930323631643639396438623461-->
?
Without overlap, each token is encoded once:
```text
tokens : 50 000 × 10 × 500 = 250 millions
embedding : 250 × 0,02 € = 5 €
vectors : 250 millions / 500 = 500 000
values : 500 000 × 1 024 × 4 = 2 048 000 000 bytes = 2,048 GB
```
The rate is fictitious; it is not the total cost of indexing. Add parsing, metadata, index structure, storage, exploitation and possible reindexing. Overlap repeats tokens and increases these volumes; poorly extracted documents remain unusable despite inexpensive embeddings.

The 2.048 GB only covers float32 vector values. The number of vectors and their dimensions are used to size this component; the index and metadata can significantly change the actual occupation of the service.

---

How does a reference context experience help diagnose a RAG? <!--anki:3335616337333837333331363434633339343062323136336363653033613664-->
?
Provide the generator with the **annotated reference passes**, instead of the search result, and then compare with the entire pipeline on the same questions.

If the answer remains wrong with these passages, examine generation, contradictions, format and evaluation criteria. If it becomes correct, look instead in ingestion, search, filtering or ranking. Verify that the passages are indeed sufficient to answer. This experiment isolates a component under controlled conditions; it does not measure the actual performance of the retrieval and does not replace an end-to-end evaluation.

---

Why is counting relevant documents not enough to answer a compound RAG question? <!--anki:3632303937383862646565363461633562313937343666343865303661316162-->
?
A question may require **multiple additional evidence**: amount, effective date and exception. Ten passages on the amount do not cover the other two items.

Break down the expected response into verifiable assertions, and then check for evidence for each. Measure this coverage in addition to the documentary recall. If evidence is missing, specifically seek or produce an explicit partial response; increasing top-k indiscriminately can especially add repetitions.

---

Calculation: a context RAG accepts 8,000 tokens; instructions and question take 1,000, the reserved output 2.000. Each pass with its metadata makes 500 tokens. How many passes can we provide at most? <!--anki:3431366164306331356236643432656462356135346161633139353062613033-->
?
The documentary budget is **8,000 − 1,000 − 2,000 = 5,000 tokens**, so **10 passages** in these assumptions.

This is a ceiling, not an optimal top-k. Deduplicating and selecting additional evidence may be better than filling the entire window. Counting separators and other messages if not included in the starting data; check the counting rules of the API used.

---

## Scenarios

Scenario: your RAG on the internal documentation answers "I can't find" on questions that you know exist. How do you diagnose? <!--anki:44667c316e40784c526c-->
?
1. **Isolate the faulty layer**: is the right passage in the top-k? If so, the problem comes from the **generation**; if not, from the **retrieval** ([[96-evals-rag-agents|RAG evals]])
2. **Look at chunks**: cutting that cuts tables or titles, parsing that loses the PDF structure ([[162-document-parsing|parsing]])
3. **Test the exact terms**: if the questions contain references or acronyms, the vector only the spleen → **hybrid search** ([[22-advanced-rag|Advanced RAG]])
4. **Check k and filters**: top-k too small, metadata filter too strict, documents not reindexed
5. **Measure**: call@k on a golden dataset before and after each correction

**Pip**: Change model of embedding first, while chunking and parsing explain most cases.

---

Scenario: the trade asks you for a RAG on 200,000 documents, including HR notes reserved for certain services. What decisions do you make before indexing? <!--anki:6e6c53594f5f666e487c-->
?
1. **Access rights first**: Each chunk carries its permission metadata, and filtering is done **at retrieval**, never after ([[101-llm-security-guardrails|Security]])
2. **Perimeter**: start with a useful and well-controlled corpus rather than ingesting everything
3. **Fresh**: re-ingestion pipeline and removal, otherwise the index drifts ([[113-monitoring-drift-feedback|drift]])
4. **Chunking** adapted to actual documents (structure, tables) and **compulsory quotations** in responses
5. **Cost and volumetry**: index size, cost of embeddings, vector base adapted

**Trap**: index first and process the rights "later". Everything will have to be reindexed.

---

## Connections
- [[22-advanced-rag|Advanced RAG]] — hybride, reranking, query rewriting
- [[11-advanced-prompt-engineering|Prompt engineering]] — when the prompt is no longer enough
- [[35-context-engineering|Context engineering]] — place chunks in context budget
- [[51-fine-tuning-adaptation|Fine-tuning]] — knowledge vs behavior
- [[92-chainforge-evals-prompts|Evals]] — Evaluate the Retrieval Pipeline
- [[133-embeddings-representations|Embeddings & Representations]] — models of embedding in detail
- [[162-document-parsing|Parsing of documents]] — ingestion quality
- [[96-evals-rag-agents|Evals of RAG]] — recall@k, faithfulness
- [[25-chunking-contextual-retrieval|Advanced Chunking & Contextual Retrieval]] — Make Every Chunk Found
- [[26-text-to-sql|Text-to-SQL]] — encrypted questions that the RAG does not know how to handle
- [[123-aggressive-caching|Caching]] — prompt caching and response caches
- [[134-vector-search-ann|Vector search]] — index ANN, HNSW and vector quantization
- [[141-system-design-llm|System Design LLM]] — design method
- [[143-hallucinations-grounding|Hallucinations & grounding]] — quotes, abstention and verification
- [[23-knowledge-graphs-ontologies|Knowledge graphs]] — GraphRAG and related data
- [[27-search-agents-deep-research|Research agents]] — multi-step search, with quotes
- [[42-langchain-fundamentals|LangChain]] — the basic building blocks of the framework
- [[137-long-context|Long context]] — compare search and complete context
- [[20-011-retrieval-quality-metrics|Retrieval quality metrics]] — AP/MAP, RR/MRR, relevance judgments and evidence coverage
- [[00-moc-ai-engineering|MOC AI Engineering]]
