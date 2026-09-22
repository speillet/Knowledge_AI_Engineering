# RAG — Avancé — Flashcards
Tags: #flashcards #ai-engineering #rag #retrieval #llm

Qu'est-ce que la recherche hybride ?
?
La combinaison **lexicale (BM25) + vectorielle**, fusionnée (ex. **RRF**) : robuste aux termes exacts (références, codes, noms) que le vectoriel seul rate.

---

Qu'est-ce que le reranking ?
?
Un **cross-encoder re-score** les passages du retrieval initial (query + passage évalués ensemble) : précision nettement supérieure, au prix d'un peu de latence.

---

Qu'est-ce que le query rewriting ?
?
**Reformuler ou décomposer la question** avant le retrieval : multi-query (variantes), step-back (question plus générale), décomposition en sous-questions.

---

Qu'est-ce que HyDE ?
?
**Hypothetical Document Embeddings** : générer une **réponse hypothétique** puis chercher les documents similaires à cette réponse plutôt qu'à la question.

---

À quoi sert le metadata filtering ?
?
À combiner similarité et **filtres structurés** (date, source, tenant, **permissions/ACL**) — indispensable pour la sécurité : ne jamais retrouver ce que l'utilisateur n'a pas le droit de voir.

---

Qu'est-ce que GraphRAG ?
?
Un RAG appuyé sur un **knowledge graph** : utile pour les questions **multi-hop** ou globales (« quels liens entre X et Y ? ») où la similarité plate échoue.

---

Qu'est-ce que l'agentic RAG ?
?
L'**agent décide quand et quoi chercher** : il itère (recherche → lecture → nouvelle requête) au lieu d'un retrieval unique en amont.

---

Quelle est la triade d'évaluation RAG ?
?
- **Faithfulness** : la réponse est fidèle au contexte fourni
- **Answer relevance** : elle répond à la question
- **Context relevance** : les chunks récupérés sont pertinents

(frameworks type **RAGAS**)

---

Quels problèmes de production spécifiques au RAG ?
?
**Fraîcheur de l'index** (ré-ingestion), propagation des **ACL**, coût des embeddings à l'échelle, dérive du chunking entre versions.

---

Pourquoi l'ordre des chunks dans le contexte compte-t-il ?
?
Effet **« lost in the middle »** : l'information au milieu du contexte est moins bien exploitée → placer les chunks clés **en début/fin**.

---

## Connexions
- [[21-rag-fondamentaux|RAG fondamentaux]] — le socle
- [[35-context-engineering|Context engineering]] — placement et budget
- [[101-securite-llm-guardrails|Sécurité LLM]] — injection via documents, ACL
- [[31-agents-fondamentaux|Agents]] — l'agentic RAG
- [[32-tool-calling|Tool calling]] — l'agentic RAG appelle des outils
- [[23-knowledge-graphs-ontologies|Knowledge graphs & ontologies]] — GraphRAG en détail
- [[00-moc-ai-engineering|MOC AI Engineering]]
