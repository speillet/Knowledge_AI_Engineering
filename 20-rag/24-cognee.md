# Cognee — Flashcards
Tags: #flashcards #ai-engineering #rag #knowledge-graph #memoire #cognee #llm

Qu'est-ce que Cognee ?
?
Une plateforme **open source** (Apache 2.0) de **mémoire pour agents** : elle transforme documents, code et conversations en **knowledge graph** doublé d'un **index vectoriel**, auto-hébergeable, que les agents interrogent d'une session à l'autre. L'ingestion peut même tourner **sans LLM**, avec des modèles d'extraction et d'embedding locaux.

---

Quelles sont les quatre opérations de Cognee 1.0 ?
?
- **`remember`** : stocker du contenu en mémoire (permanente ou de session)
- **`recall`** : retrouver du contexte ou une réponse
- **`improve`** : enrichir la mémoire, appliquer du feedback
- **`forget`** : supprimer un élément ou un dataset
```python
await cognee.remember("Marie Curie est née à Varsovie.", dataset_name="demo")
results = await cognee.recall("Où est née Marie Curie ?", datasets=["demo"])
```

---

Que fait remember en mémoire permanente ?
?
Le pipeline complet, en trois phases :
1. **Ingestion** et normalisation dans un dataset
2. **Construction du graphe** : chunking, extraction des entités et relations, embeddings
3. **Enrichissement** automatique (une passe `improve`)

Il remplace l'ancienne séquence `add` → `cognify`, toujours disponible pour contrôler chaque étape.

---

Mémoire permanente ou mémoire de session ?
?
- **Permanente** (sans `session_id`) : le pipeline complet, plus lent et plus coûteux, qui produit graphe et embeddings
- **Session** (avec `session_id`) : le **chemin rapide**, écrit dans un cache et disponible aussitôt pour la session. Elle ne rejoint la mémoire permanente que par un **transfert** explicite ou automatique (`improve`)

---

Comment recall choisit-il sa stratégie ?
?
Par **routage automatique** : des règles repèrent les citations exactes ou les demandes de règles de code, sinon il utilise **HYBRID_COMPLETION** (chunks, résumés et voisinage des entités en un seul appel LLM). On peut forcer une stratégie : `GRAPH_COMPLETION`, `RAG_COMPLETION`, `CHUNKS`, `CHUNKS_LEXICAL` (BM25), `SUMMARIES`, `TEMPORAL`, `CYPHER`… C'est une **récupération par graphe**, pas une simple similarité d'embeddings.

---

Que fait improve ?
?
- **Enrichit** un graphe existant sans ré-ingérer les sources (structures dérivées, triplets indexés)
- Applique le **feedback** : les éléments utilisés dans une bonne réponse gagnent du poids, ceux d'une mauvaise en perdent
- **Transfère les apprentissages de session** (questions-réponses, traces d'agent, leçons) dans la mémoire permanente

---

Comment Cognee utilise-t-il une ontologie ?
?
On fournit un fichier **OWL** (RDF/XML). Les entités extraites par le LLM sont **rapprochées** des classes et individus de l'[[23-knowledge-graphs-ontologies|ontologie]] et **renommées au terme canonique**. Deux modes :
- **annotate** (par défaut) : les entités hors ontologie sont conservées
- **strict** : elles sont supprimées

---

Comment brancher Cognee à un agent ?
?
- **Plugin** pour Claude Code ou Codex (mémoire capturée par des hooks)
- **Serveur [[33-mcp|MCP]]** pour Cursor, Cline et les autres clients MCP
- **SDK** Python et TypeScript, **API REST**

Il sait aussi importer une mémoire existante depuis Mem0, Letta, Zep ou Graphiti.

---

Quelles limites garder en tête ?
?
- L'extraction par LLM a un **coût** et produit du **bruit** : la qualité dépend du modèle et de l'ontologie
- Une stack à opérer : base graphe, index vectoriel, cache de session
- Une API **jeune** qui évolue vite : la 1.0 a renommé les opérations, à revérifier avant chaque mise à jour

---

## Connexions
- [[23-knowledge-graphs-ontologies|Knowledge graphs & ontologies]] — les concepts sous-jacents
- [[39-memoire-agents|Mémoire des agents]] — le problème que Cognee résout
- [[22-rag-avance|RAG avancé]] — la recherche hybride
- [[33-mcp|MCP]] — l'intégration aux clients agents
- [[34-harness-plugins|Harness & plugins]] — plugin et hooks de capture
- [[00-moc-ai-engineering|MOC AI Engineering]]
