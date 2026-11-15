# Cognee — Flashcards
Tags: #flashcards #ai-engineering #rag #knowledge-graph #memory #cognee #llm
Verified on: 25 September 2026 — This factsheet lists products, versions or regulatory texts that are evolving quickly.
<!-- summary: Agent memory in knowledge graph, operations remember, recall, improve and forget, permanent or session memory, search policies, OWL ontology, integrations (plugin, MCP), limits, memory reversibility test, memory utility test, controlled reconstruction. -->


What is Cognee? <!--anki:7924302d43443778695b-->
?
A **open source** platform (Apache 2.0) with **agent memory**: it transforms documents, code and conversations into **knowledge graph** doubled by a **vector index**, which agents query from one session to the next. Ingestion can even turn **without LLM**, with local extraction models and embedding.

The advantage is to find both a similar passage and **relationships between entities**, for example linking a client to an incident already analyzed. This memory remains a data system: predicting origin, separation of users and deletion. An incorrect extraction can persist and be reused; the storage does not turn a hypothesis into a fact.

---

What are the four operations of Cognee 1.0? <!--anki:6568383b553a542a5065-->
?
- **`remember`**: store content in memory (permanent or session)
- **`recall`**: find context or a response
- **`improve`**: enrich the memory, apply feedback
- **`forget`**: delete an element or a dataset
```python
await cognee.remember("Marie Curie was born in Warsaw.", dataset_name="demo")
results = await cognee.recall("Where was Marie Curie born?", datasets=["demo"])
```

These operations describe a **lifecycle**, not four guarantees of quality. In the example, check that the dataset being queried is indeed the one being fed and examine the returned sources. After a modification or deletion, check the derived representations and future reminders; a response already copied in a history may remain elsewhere.

---

What does Cognee's operation remember in permanent memory? <!--anki:4a3726612a4444423334-->
?
The complete pipeline, in three phases:
1. **Ingestion** and normalization in a dataset
2. **Graph construction**: chunking, entity extraction and relationships, embeddings
3. **Automatic enrichment** (one pass `improve`)

It replaces the old `add` → `cognify` sequence, always available to control each step.

An ingestion therefore transforms several representations of the same document; its success is not limited to the presence of the file. On a small example, check the extracted entities, relationships and an expected reminder. Keep a source identifier to track updates and diagnose an extraction that distorts the content.

---

Permanent memory or session memory? <!--anki:6b6b4778485f7935575a-->
?
- **Permanent** (without `session_id`): the full, slower and more expensive pipeline, which produces graph and embeddings
- **Session** (with `session_id`): the **quick path**, written in a cache and available immediately for the session. It joins the permanent memory only by an explicit or automatic **transfer** (`improve`)

For example, a provisional meeting assumption must remain in session until it is validated. Testing expiration, restart, and transfer: "available now" does not mean "durable", and the transfer must not expand access rights.

---

How does Cognee's call operation choose its search strategy? <!--anki:636d76242e427a3c316e-->
?
By an **Router Rules**, Not by a choice LLM systematic: without explicit strategy, Permanent memory usually uses **`HYBRID_COMPLETION`**. The parameter `query_type` Allows you to force a mode.

The perimeter also counts: with `session_id` alone, Cognee can first search the session cache; specify `datasets` or `query_type` orients to the permanent memory. Examine the field **`source`** of the result to distinguish these paths.

Example: A response from `source="session"` does not show that the graph contains the fact. To diagnose an oversight, check scope, provenance, and index status before changing policy.

---

What does Cognee's operation improve? <!--anki:6e43464e492d4e46546f-->
?
- **Enriches** an existing graph without re-ingesting sources (derived structures, indexed triplets)
- Applies **feedback**: items used in a good answer gain weight, those of a bad one lose weight
- **Transfers session learning** (questions-answers, agent traces, lessons) into permanent memory

Positive feedback on a response does not necessarily validate **All the facts that fueled it**. Separate user feedback, factual verification and promotion rule in permanent memory. Compare reminders before and after enrichment on known issues, to identify a wrongly amplified preference or useful information that has become less accessible.

---

How does Cognee use an ontology? <!--anki:753478483f5845616f62-->
?
A **OWL** file (RDF/XML) is provided. The entities extracted by the LLM are **close** to the classes and individuals of the [[23-knowledge-graphs-ontologies|ontology]] and **renamed to the canonical term**.
- **annotate** (default): Non-ontology entities are retained
- **Strict**: they are removed

Strict mode is only appropriate if the ontology actually covers the domain: a new but valid entity might otherwise disappear. For example, a new type of contract that is missing from the schema deserves a review rather than a silent rejection. Measure the non-close items and keep their provenance to evolve the controlled vocabulary.

---

How to connect Cognee to an agent? <!--anki:4e43293673732c445132-->
?
- **Plugin** for Claude Code or Codex (memory captured by hooks)
- **[[33-mcp|MCP]] server** for Cursor, Cline and other MCP clients
- **SDK** Python and TypeScript, **API REST**

It can also import an existing memory from Mem0, Letta, Zep or Graphiti.

Choose integration based on where you control **identity, permissions, and lifecycle**. A memory that is accessible to multiple clients must be partitioned by user or project. Check what data hooks capture, how they are remembered, and how to delete a memory, before enabling automatic collection on real conversations.

---

What Cognee limits to keep in mind? <!--anki:4a404e6c463832774659-->
?
- The extraction by LLM has a **cost** and produces **noise**: the quality depends on the model and ontology
- A stack to operate: base graph, vector index, session cache
- A API **Young** Who is rapidly evolving: The 1.0 renamed the operations, Re-check before each update

On a sample corpus, measure correctly extracted facts, invented relationships, and actually supported responses. A denser graph is not automatically better. Include a de facto change and deletion in the upgrade test.

---

How to test the reversibility of a Cognee memory before entrusting it with a corpus? <!--anki:6530643134333066346436643433666561356237373835333963633362323662-->
?
Make a **Exit Test** on a small synthetic corpus: ingesting facts with their provenance, export accessible data and reconstruct useful responses in a blank environment.

Check separately documents, relationships, metadata, rights, and versions of transformations. An export of single texts can lose links or access rules. Also test deletion and re-ingestion of a document. This protocol evaluates the guarantees of the deployed version; it does not assume that a universal export command automatically preserves all memory.

---

How to measure whether a Cognee memory actually improves an agent's responses? <!--anki:6237333361666564626165633462306361353864366338336364343032313430-->
?
Compare **without memory, with relevant memory and with obsolete memory** on the same tasks. Measure recalled useful facts, respected corrections, latency and introduced errors.

Separate writing and testing conversations to avoid measuring a simple immediate repetition. Include requests where no memory should intervene. The number of nodes or memories stored does not measure usefulness: a larger memory can increase contradictions and reminders off topic.

---

What should be preserved to rebuild a Cognee memory after a embedding model change? <!--anki:3633643439363365346138353438356338306230386265373534326539666334-->
?
Preserving **authorized sources, identifiers, source, and versions of transformations**, rather than just vectors. A reconstruction can change extracted entities and relationships: it is not necessarily a semantically identical copy.

Build the new memory next to the old one, replay reference questions, and check for deletions and rights before toggling. Document data that is actually exportable in the deployed version; rebuild functions must be tested, not deduced from the name of the operations.

---

## Scenarios

Scenario: Your internal assistant must remember the decisions made in the meetings and answer questions that connect them. You are considering Cognee. How do you proceed? <!--anki:6751377b623156407d3d-->
?
1. **Check the need**: **Relational questions** (who decided what, what precedent) justify a graph; otherwise a vector RAG is enough ([[21-rag-fundamentals|RAG]])
2. **Restricted ontology** in OWL: meeting, decision, person, project, in `annotate` mode so as not to lose what comes out of the schema
3. **Memory session** during the meeting (quick path), then transfer to permanent memory by `improve`
4. **Skip agent** by MCP server or SDK ([[33-mcp|MCP]])
5. **Frame costs**: LLM extraction over the entire history is fast. Start with a reduced perimeter and measure

**Trap**: Ingest the entire history of the company before validating the quality of the answers on a control corpus.

---

Scenario: a user requests the deletion of all his data, which has been ingested in the agent's memory. What do you check? <!--anki:6776213679257c40792e-->
?
1. **Real Clearance**: `forget` on affected elements and datasets, not a simple masking
2. **Propagation**: The graph, vector index, session cache, and backups must all be processed ([[154-gdpr-llm|RGPD]])
3. **Derivatives**: Consolidated summaries, enrichments and memories that still contain these data
4. **Traceability**: retain proof of deletion, without retaining data
5. **Prevent**: partition by user upon ingestion and attach the provenance to each element

**Trap**: Forget the derived structures produced by `improve`, which survive the removal of the source.

---

## Sources

- [Cognee — project documentation](https://docs.cognee.ai/)
- [Cognee — call routing and session scope](https://docs.cognee.ai/core-concepts/main-operations/recall.md) — targeted consultation of the 6 November 2026; does not constitute a recheck of the entire topic.

## Connections
- [[23-knowledge-graphs-ontologies|Knowledge graphs & ontologies]] — the underlying concepts
- [[39-agent-memory|Memorandum of agents]] — the problem that Cognee solves
- [[22-advanced-rag|Advanced RAG]] — Hybrid
- [[33-mcp|MCP]] — Integration with Agent Customers
- [[34-harness-plugins|Harness & plugins]] — plugin and capture hooks
- [[00-moc-ai-engineering|MOC AI Engineering]]
