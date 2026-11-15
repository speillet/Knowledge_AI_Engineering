# Knowledge graphs & ontologies — Flashcards
Tags: #flashcards #ai-engineering #rag #knowledge-graph #ontology #llm
Verified on: 29 September 2026 — This factsheet lists products, versions or regulatory texts that are evolving quickly.
<!-- summary: triplets, RDF or property graph (Cypher, GQL), ontology and taxonomy, extraction by LLM under schema, entity resolution, graph or vectors, local and global GraphRAG, Text2Cypher, context graph, costs, source of relations, open world, negation of relations. -->


What is a knowledge graph? <!--anki:75794e4c4c3a65215f7b-->
?
A representation of knowledge in the form of a **graph**: **entities** (nodes: people, products, contracts...) linked by **typed relationships** (edges), each of which can carry properties. The basic unit is the **triplet**:
```text
(Marie Curie) — [NEA_To]→ (Warsaw)
   Subject Predicate Object
```

The interest is to be able to follow the relationships: find the people related to an organization, then the contracts concerned. Keep the source and, if necessary, the validity period of the facts. A graph represents what has been recorded; it does not guarantee that each relationship extracted is true.

---

RDF or property graph? <!--anki:6f6a784b296a54416f74-->
?
- **RDF** (W3C standard): everything is triplet, identified by URIs, interrogated in **SPARQL**, described by **OWL** ontologies. Strong for interoperability and reasoning.
- **Property graph** (Neo4j, FalkorDB, Amazon Neptune...): nodes and edges directly carry properties, queried in **Cypher** or **GQL** (ISO standard since 2024). More convenient for applications, it is the common choice of LLM stacks.

---

What is an ontology? <!--anki:473f21414c2b645b3135-->
?
The **formal scheme of a domain**: the **classes** (Person, Company), their **hierarchy** (a Provider *is an* Company), the **types of relations** allowed between classes and their constraints. It allows to validate the data and **infer** facts.
- **Taxonomy**: only the class hierarchy
- **Ontology**: the complete schema, with relationships and rules
- **Knowledge graph**: **Instances** (data) conform to this schema

---

Why an ontology when a LLM builds the graph? <!--anki:66354d4240287b307542-->
?
Without a schema, extraction **drifts**: duplicate entities ("Paris", "City of Paris"), synonymous relationships (WORKS_FOR, EMPLOYED_BY) and invented types make the graph difficult to query. An ontology **constrains extraction** to allowed entity and relationship types, using [[63-guided-generation|structured output]], and normalizes entities to **canonical terms**.

For example, imposing a `EMPLOYE_PAR` relationship avoids three names for the same link, but this does not prove that the job exists or that two people with the same name are the same. Keep the source of each relationship and control separately **schema validity, identity resolution, and factual accuracy**.

---

How to build a knowledge graph with a LLM? <!--anki:7645732d313e6c377d63-->
?
```text
documents → passages → entity extraction and schema relationships
→ entity resolution → validation → graph storage
```
The extractor must associate each fact with a source passage; the **entity resolution** then merges the mentions designating the same object without confusing homonyms.

Check constraints, duplicates, and questionable relationships before loading. embeddingss can make searching easier, but are not mandatory. Tools like [[24-cognee|Cognee]] automate a portion of the pipeline; they do not replace fact validation.

---

What is Entity Resolution? <!--anki:70586539675d5f58613a-->
?
Recognize that several mentions designate **the same real entity** and **merge**: normalization, similarity of embeddings, business rules (same SIREN), then a LLM to decide ambiguous cases. Too shy, the graph is **fragmented**; too aggressive, it **mistakenly merges** separate entities.

Two institutions with the same name should not be merged on text-only likeness. Prefer a stable identifier where it exists, keep mentions and provenance, and then provide for a review of uncertain cases. An erroneous merge spreads attributes and relationships to the wrong entity; it should be able to be undone.

---

When does a graph beat vector search? <!--anki:696f362a64337e444e58-->
?
- Questions **multi-hop** (“Which suppliers from X’s subsidiaries are late?”)
- **Explicit relationships** and paths between entities
- **Aggregations** and counts (“how many contracts per customer?”)
- **Provenance** and explicability: we show the path traveled

The vector search remains better for the **closeness of meaning** in unstructured text: we often combine the two.

---

How to combine graph and vectors? <!--anki:5268263e733e2e3f7d6a-->
?
1. **Vector search** to find relevant chunks or input nodes
2. **Path of the Graph** to k jumps around these nodes (neighbors, Relationships)
3. Assembly of the **subgraph and chunks** in the context of the LLM

This is the principle of GraphRAG "local", useful when the answer is distributed among several linked documents.

Example: find a component by its description, then follow the links to its suppliers. Bound depth and number of neighbors: a highly connected node can fill the context of unnecessary relationships. Keep the provenance of relationships to check the answer.

---

How does GraphRAG work from Microsoft? <!--anki:7a516429687c6a513b6d-->
?
At indexing: extraction of entities and relationships, detection of **communities** (Leiden algorithm), then **hierarchical summaries** of each community.
- **Local search**: from the entities of the question and their neighborhood
- **Global search**: map-reduce on community summaries, for questions on **the whole corpus** (“what are the main themes?”)

Indexing is **expensive**; LazyGraphRAG pushes back the LLM job at the time of the query to greatly reduce it.

---

What is Text2Cypher and what are its risks? <!--anki:4450547e3f4856545139-->
?
The LLM **translates the question into a Cypher request**, with the diagram of the graph in the prompt. Risks: false request, invented labels, expensive request or **destructive** (injection). Parades: basic user **read-only**, request validation, timeouts and result limits, requests **set** for frequent cases.

A syntactically valid query can cross the wrong type of relationship. Test on a small graph whose answer is known, and then control the execution plan. A `LIMIT` limits the returned lines, not necessarily the work done before this return.

---

What is a context graph? <!--anki:7256243e362425497749-->
?
A recent term, **not standardized**, with two meanings:
- **Decision marks** (Foundation Capital, end 2025): a graph that links business entities to **decisions made** (rule applied, exception granted, who validated, what precedent), so that agents can find the precedents and audit their choices.
- **Time Graph** (Graphiti, Zep): a knowledge graph where each fact has a **window of validity** and goes back to the **episodes** (raw data) that produced it.

---

What are the costs and pitfalls of a knowledge graph? <!--anki:64642c3535557229767e-->
?
The cost includes **extraction, maintenance and evaluation**, not just graph storage. An erroneous relationship can contaminate multiple multi-hop responses.

For example, turning "supplier envisaged" into "authorised supplier" creates a plausible but false edge. Keeping the supporting passage, type and period of validity of the relationship allows you to control it and remove it when the source changes.

Start with a **restricted ontology**; measure the quality of entities, relationships and responses. Compare the gain to a [[21-rag-fundamentals|Vector RAG]] on the same [[92-chainforge-evals-prompts|evals]], integrating the human correction cost.

---

Why keep the provenance of each relationship extracted in a knowledge graph? <!--anki:3866343838343766326361623433336262323237373366623366393334363032-->
?
An extracted **relationship** remains an affirmation from a source, sometimes uncertain. Keep document, passage, validity date and extractor version allows to verify, correct or withdraw this affirmation.

If two reports assign different leaders to a company, keeping their periods and evidence avoids arbitrarily overwriting one of the relationships. A deletion must be able to find the relationships derived from the document. The graph gains in traceability; it does not become true by construction. Distinguish observed relationship, inferred relationship and validated fact.

---

Do not confuse: absence of relationship in a graph and proof that the relationship is false? <!--anki:6665303530386666656164313464313162653766626631376135653063313662-->
?
In a semantics of **Open World**, Not knowing a relationship does not mean its negation. An unrelated graph between a company and a subsidiary may simply be incomplete.

A closed world rule is defensible only for a declared complete perimeter, with date and provenance. An agent must therefore distinguish confirmed, refuted and unknown relationship. The convention of the query engine does not transform the incompleteness of the sources into business certainty.

---

How to avoid turning a hypothetical relationship extracted by LLM into a knowledge graph? <!--anki:3934356638626430663463313466363138326637623836653834353263613063-->
?
Retaining **modality, negation, and attribution**: "considers redeeming" does not mean "owns." Model the assertion with its source, date, and status before deriving an exploitable relationship.

Validate promotion rules on negative and conditional examples. Two repeated mentions of the same rumor do not constitute two independent confirmations. A relationship without these qualifications can make multi-hop courses coherent in appearance but factually false.

---

## Scenarios

Scenario: your graph extracted by LLM contains "Societe Generale", "Societe Generale" and "SG" as three separate entities, and multi-hop queries fail. How do you fix it? <!--anki:6670413d484e4a557b4d-->
?
1. **Cause** : extraction without ontology or resolution of entities, So a graph **Fragment**
2. **Restricted Ontology**: Allowed types of entities and relationships, structured output extraction ([[63-guided-generation|guided generation]])
3. **Entity resolution**: normalization, similarity of embeddings, business rules (same SIREN), LLM in arbiter on doubtful cases
4. **Merge the existing** rather than re-extract everything, if the corpus is expensive to reprocess
5. **Measure**: Known test queries, and monitor the number of entities per concept

**Trap** too aggressive resolution that merges a subsidiary and its parent company.

---

Scenario: a project manager wants to expose Text2Cypher to business users, so that they query the graph in natural language. What conditions do you pose? <!--anki:4a3b4c694f233a516228-->
?
1. **Read-only basic user**: No request can modify or delete the graph
2. **Validation of query generated** before execution, with labels and relationships checked against the schema
3. **Timeouts and result limits**, against queries that scan the entire graph
4. **Setting requests** for frequently asked questions, the LLM only filling in the parameters
5. **Show the query and the path** traveled, so that the user can judge the answer ([[102-agent-threats|threats]])

**Trap**: Give the generator an administration account "test time".

---

## Sources

- [Microsoft — GraphRAG, indexing and search](https://microsoft.github.io/graphrag/)

- [W3C — PROV provenance model](https://www.w3.org/TR/prov-overview/) — targeted deepening of the 12 November 2026; educational examples are built for this review.

- Supplement of the 14 November 2026 — Open world and assertions: [W3C — OWL 2 Primer](https://www.w3.org/TR/owl2-primer/).

## Connections
- [[21-rag-fundamentals|RAG — Fundamentals]] — Basic Vector Search
- [[22-advanced-rag|Advanced RAG]] — hybrid and agentic search RAG
- [[24-cognee|Cognee]] — an agent memory built on a graph and an ontology
- [[39-agent-memory|Memorandum of agents]] — Time Graphs to Remember
- [[63-guided-generation|Guided generation]] — extract as schema
- [[101-llm-security-guardrails|LLM Security]] — injection in generated queries
- [[26-text-to-sql|Text-to-SQL]] — the same problem as Text2Cypher, on a relational basis
- [[00-moc-ai-engineering|MOC AI Engineering]]
