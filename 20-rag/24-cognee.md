# Cognee — Flashcards
Tags: #flashcards #ai-engineering #rag #knowledge-graph #memoire #cognee #llm
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.
<!-- summary: mémoire d'agent en knowledge graph, opérations remember, recall, improve et forget, mémoire permanente ou de session, stratégies de recherche, ontologie OWL, intégrations (plugin, MCP), limites. -->


Qu'est-ce que Cognee ? <!--anki:7924302d43443778695b-->
?
Une plateforme **open source** (Apache 2.0) de **mémoire pour agents** : elle transforme documents, code et conversations en **knowledge graph** doublé d'un **index vectoriel**, auto-hébergeable, que les agents interrogent d'une session à l'autre. L'ingestion peut même tourner **sans LLM**, avec des modèles d'extraction et d'embedding locaux.

L'intérêt est de retrouver à la fois un passage similaire et des **relations entre entités**, par exemple relier un client à un incident déjà analysé. Cette mémoire reste un système de données : prévoir provenance, séparation des utilisateurs et suppression. Une extraction incorrecte peut persister et être réutilisée ; le stockage ne transforme pas une hypothèse en fait.

---

Quelles sont les quatre opérations de Cognee 1.0 ? <!--anki:6568383b553a542a5065-->
?
- **`remember`** : stocker du contenu en mémoire (permanente ou de session)
- **`recall`** : retrouver du contexte ou une réponse
- **`improve`** : enrichir la mémoire, appliquer du feedback
- **`forget`** : supprimer un élément ou un dataset
```python
await cognee.remember("Marie Curie est née à Varsovie.", dataset_name="demo")
results = await cognee.recall("Où est née Marie Curie ?", datasets=["demo"])
```

Ces opérations décrivent un **cycle de vie**, pas quatre garanties de qualité. Dans l'exemple, contrôler que le dataset interrogé est bien celui alimenté et examiner les sources retournées. Après une modification ou une suppression, vérifier les représentations dérivées et les futurs rappels ; une réponse déjà copiée dans un historique peut subsister ailleurs.

---

Que fait l'opération remember de Cognee en mémoire permanente ? <!--anki:4a3726612a4444423334-->
?
Le pipeline complet, en trois phases :
1. **Ingestion** et normalisation dans un dataset
2. **Construction du graphe** : chunking, extraction des entités et relations, embeddings
3. **Enrichissement** automatique (une passe `improve`)

Il remplace l'ancienne séquence `add` → `cognify`, toujours disponible pour contrôler chaque étape.

Une ingestion transforme donc plusieurs représentations du même document ; son succès ne se résume pas à la présence du fichier. Sur un petit exemple, vérifier les entités extraites, les relations et un rappel attendu. Conserver un identifiant de source pour suivre les mises à jour et diagnostiquer une extraction qui déforme le contenu.

---

Mémoire permanente ou mémoire de session ? <!--anki:6b6b4778485f7935575a-->
?
- **Permanente** (sans `session_id`) : le pipeline complet, plus lent et plus coûteux, qui produit graphe et embeddings
- **Session** (avec `session_id`) : le **chemin rapide**, écrit dans un cache et disponible aussitôt pour la session. Elle ne rejoint la mémoire permanente que par un **transfert** explicite ou automatique (`improve`)

---

Comment l'opération recall de Cognee choisit-elle sa stratégie de recherche ? <!--anki:636d76242e427a3c316e-->
?
Par **routage automatique** : des règles repèrent les citations exactes ou les demandes de règles de code, sinon il utilise **HYBRID_COMPLETION** (chunks, résumés et voisinage des entités en un seul appel LLM). On peut forcer une stratégie : `GRAPH_COMPLETION`, `RAG_COMPLETION`, `CHUNKS`, `CHUNKS_LEXICAL` (BM25), `SUMMARIES`, `TEMPORAL`, `CYPHER`… C'est une **récupération par graphe**, pas une simple similarité d'embeddings.

---

Que fait l'opération improve de Cognee ? <!--anki:6e43464e492d4e46546f-->
?
- **Enrichit** un graphe existant sans ré-ingérer les sources (structures dérivées, triplets indexés)
- Applique le **feedback** : les éléments utilisés dans une bonne réponse gagnent du poids, ceux d'une mauvaise en perdent
- **Transfère les apprentissages de session** (questions-réponses, traces d'agent, leçons) dans la mémoire permanente

Un retour positif sur une réponse ne valide pas nécessairement **tous les faits qui l'ont alimentée**. Séparer feedback utilisateur, vérification factuelle et règle de promotion en mémoire permanente. Comparer les rappels avant et après enrichissement sur des questions connues, afin de repérer une préférence amplifiée à tort ou une information utile devenue moins accessible.

---

Comment Cognee utilise-t-il une ontologie ? <!--anki:753478483f5845616f62-->
?
On fournit un fichier **OWL** (RDF/XML). Les entités extraites par le LLM sont **rapprochées** des classes et individus de l'[[23-knowledge-graphs-ontologies|ontologie]] et **renommées au terme canonique**. Deux modes :
- **annotate** (par défaut) : les entités hors ontologie sont conservées
- **strict** : elles sont supprimées

Le mode strict convient seulement si l'ontologie couvre réellement le domaine : une entité nouvelle mais valide pourrait sinon disparaître. Par exemple, un nouveau type de contrat absent du schéma mérite une revue plutôt qu'un rejet silencieux. Mesurer les éléments non rapprochés et conserver leur provenance pour faire évoluer le vocabulaire contrôlé.

---

Comment brancher Cognee à un agent ? <!--anki:4e43293673732c445132-->
?
- **Plugin** pour Claude Code ou Codex (mémoire capturée par des hooks)
- **Serveur [[33-mcp|MCP]]** pour Cursor, Cline et les autres clients MCP
- **SDK** Python et TypeScript, **API REST**

Il sait aussi importer une mémoire existante depuis Mem0, Letta, Zep ou Graphiti.

Choisir l'intégration selon l'endroit où l'on contrôle **identité, permissions et cycle de vie**. Une mémoire accessible à plusieurs clients doit rester cloisonnée par utilisateur ou projet. Vérifier quelles données les hooks capturent, comment elles sont rappelées et comment supprimer un souvenir, avant d'activer la collecte automatique sur des conversations réelles.

---

Quelles limites de Cognee garder en tête ? <!--anki:4a404e6c463832774659-->
?
- L'extraction par LLM a un **coût** et produit du **bruit** : la qualité dépend du modèle et de l'ontologie
- Une stack à opérer : base graphe, index vectoriel, cache de session
- Une API **jeune** qui évolue vite : la 1.0 a renommé les opérations, à revérifier avant chaque mise à jour

---

## Mises en situation

Mise en situation : ton assistant interne doit se souvenir des décisions prises dans les réunions et répondre à des questions qui les relient entre elles. Tu envisages Cognee. Comment procèdes-tu ? <!--anki:6751377b623156407d3d-->
?
1. **Vérifier le besoin** : des questions **relationnelles** (qui a décidé quoi, quel précédent) justifient un graphe ; sinon un RAG vectoriel suffit ([[21-rag-fondamentaux|RAG]])
2. **Ontologie restreinte** en OWL : réunion, décision, personne, projet, en mode `annotate` pour ne pas perdre ce qui sort du schéma
3. **Mémoire de session** pendant la réunion (chemin rapide), puis transfert vers la mémoire permanente par `improve`
4. **Brancher l'agent** par le serveur MCP ou le SDK ([[33-mcp|MCP]])
5. **Cadrer les coûts** : l'extraction par LLM sur tout l'historique se chiffre vite. Commencer par un périmètre réduit et mesurer

**Piège** : ingérer tout l'historique de l'entreprise avant d'avoir validé la qualité des réponses sur un corpus témoin.

---

Mise en situation : un utilisateur demande la suppression de toutes ses données, qui ont été ingérées dans la mémoire de l'agent. Que vérifies-tu ? <!--anki:6776213679257c40792e-->
?
1. **Effacement réel** : `forget` sur les éléments et datasets concernés, et non un simple masquage
2. **Propagation** : le graphe, l'index vectoriel, le cache de session et les sauvegardes doivent tous être traités ([[154-rgpd-llm|RGPD]])
3. **Dérivés** : les résumés, enrichissements et souvenirs consolidés qui contiennent encore ces données
4. **Traçabilité** : conserver la preuve de la suppression, sans conserver les données
5. **Prévenir** : cloisonner par utilisateur dès l'ingestion et attacher la provenance à chaque élément

**Piège** : oublier les structures dérivées produites par `improve`, qui survivent à la suppression de la source.

---

## Sources

- [Cognee — documentation du projet](https://docs.cognee.ai/)

## Connexions
- [[23-knowledge-graphs-ontologies|Knowledge graphs & ontologies]] — les concepts sous-jacents
- [[39-memoire-agents|Mémoire des agents]] — le problème que Cognee résout
- [[22-rag-avance|RAG avancé]] — la recherche hybride
- [[33-mcp|MCP]] — l'intégration aux clients agents
- [[34-harness-plugins|Harness & plugins]] — plugin et hooks de capture
- [[00-moc-ai-engineering|MOC AI Engineering]]
