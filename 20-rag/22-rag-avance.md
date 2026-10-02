# RAG — Avancé — Flashcards
Tags: #flashcards #ai-engineering #rag #retrieval #llm

Qu'est-ce que la recherche hybride ?
?
<!--anki:783b3a7d537e53723532-->
La combinaison **lexicale (BM25) + vectorielle**, fusionnée (ex. **RRF**) : robuste aux termes exacts (références, codes, noms) que le vectoriel seul rate.
```text
RRF : score(doc) = Σ  1 / (k + rang_dans_la_liste)      k ≈ 60

doc A : rang 1 en BM25, rang 5 en vectoriel → 1/61 + 1/65 = 0,0318
doc B : rang 3 en BM25, rang 2 en vectoriel → 1/63 + 1/62 = 0,0320  ← meilleur
```
L'intérêt du RRF : il ne travaille que sur les **rangs**, donc aucune calibration de scores hétérogènes n'est nécessaire.

---

Qu'est-ce que le reranking ?
?
<!--anki:72403c653b3e44335232-->
Un **cross-encoder re-score** les passages du retrieval initial (query et passage évalués **ensemble**) : précision nettement supérieure, au prix d'un peu de latence.
```text
retrieval large  : top 50 candidats  (hybride, ~20 ms)
reranking        : on garde les 5 meilleurs  (~50 à 200 ms)
génération       : 5 chunks dans le contexte au lieu de 50
```
Double bénéfice : **plus de précision** et **moins de tokens** envoyés au modèle ([[121-couts-inference|coûts]]).

---

À ne pas confondre : rappel et précision dans un RAG ?
?
<!--anki:506d6d49793b6532463c-->
- **Rappel (recall@k)** : le bon passage est-il **présent** dans les k récupérés ? C'est le **plafond** du système : ce qui n'est pas remonté ne pourra jamais être utilisé
- **Précision** : quelle part des passages remontés est **utile** ? Elle joue sur le bruit, le coût et la dilution du contexte

Stratégie habituelle : **récupérer large** pour le rappel, puis **reranker** pour la précision ([[96-evals-rag-agents|evals de RAG]]).

---

Qu'est-ce que le query rewriting ?
?
<!--anki:76394545532971765776-->
**Reformuler ou décomposer la question** avant le retrieval, car la question de l'utilisateur est rarement la meilleure requête :
- **Multi-query** : plusieurs variantes, résultats fusionnés
- **Step-back** : une question plus générale, pour remonter le contexte utile
- **Décomposition** : sous-questions pour une question à plusieurs sauts
- **Contextualisation** : réécrire « et pour l'an dernier ? » en question autonome, à partir de l'historique de conversation

Coût : un appel LLM de plus avant la recherche.

---

Qu'est-ce que HyDE ?
?
<!--anki:513c5b5f50533662435f-->
**Hypothetical Document Embeddings** : le LLM rédige une **réponse hypothétique** à la question, et on cherche les documents proches de cette réponse plutôt que de la question. Une réponse ressemble davantage aux passages recherchés qu'une question courte.

Limites : un appel LLM en plus, et une réponse hypothétique **fausse** peut orienter la recherche vers de mauvais passages. Utile surtout quand questions et documents emploient des vocabulaires différents.

---

À quoi sert le metadata filtering ?
?
<!--anki:70794c6a37282d7b332c-->
À combiner similarité et **filtres structurés** (date, source, tenant, **permissions/ACL**) — indispensable pour la sécurité : ne jamais retrouver ce que l'utilisateur n'a pas le droit de voir.

---

Qu'est-ce que GraphRAG ?
?
<!--anki:654c65592a606b60292c-->
Un RAG appuyé sur un **knowledge graph** : utile pour les questions **multi-hop** ou globales (« quels liens entre X et Y ? ») où la similarité plate échoue.

---

Qu'est-ce que l'agentic RAG ?
?
<!--anki:625d426536733d593a29-->
L'**agent décide quand et quoi chercher** : il itère (recherche → lecture → nouvelle requête) au lieu d'un retrieval unique en amont.

---

Quelle est la triade d'évaluation RAG ?
?
<!--anki:71536079417d5f583732-->
- **Faithfulness** : la réponse est fidèle au contexte fourni
- **Answer relevance** : elle répond à la question
- **Context relevance** : les chunks récupérés sont pertinents

(frameworks type **RAGAS**)

---

Quels problèmes de production spécifiques au RAG ?
?
<!--anki:6a455549472f7c24745b-->
- **Fraîcheur de l'index** : ré-ingestion incrémentale des documents modifiés ou supprimés
- **Propagation des droits d'accès** : un utilisateur ne doit jamais recevoir un passage qu'il n'a pas le droit de lire
- **Coût des embeddings** à l'échelle, et ré-indexation complète si l'on change de modèle ([[133-embeddings-representations|embeddings]])
- **Dérive du chunking** entre versions du pipeline
- **Qualité du parsing** des documents sources ([[162-document-parsing|parsing]])

---

Pourquoi l'ordre des chunks dans le contexte compte-t-il ?
?
<!--anki:6e6c685336744b2e532a-->
Effet **« lost in the middle »** : l'information au milieu du contexte est moins bien exploitée → placer les chunks clés **en début/fin**.

---

## Mises en situation

Mise en situation : ton RAG juridique retrouve bien les documents pertinents (recall@20 de 0,95) mais les réponses restent moyennes. Que fais-tu ?
?
<!--anki:657e457c29693d3b524b-->
1. **Constater** : le retrieval fait son travail, le problème est en aval, dans le **classement** et le **contexte**
2. **Reranking** : un cross-encoder re-score les 20 passages pour n'en garder que 3 à 5 vraiment pertinents
3. **Ordre** : placer les meilleurs chunks **en début et en fin** de contexte, à cause du « lost in the middle »
4. **Grounding** : citations obligatoires et consigne d'abstention si le contexte ne suffit pas ([[143-hallucinations-grounding|hallucinations]])
5. **Mesurer** la triade : faithfulness, pertinence de la réponse, pertinence du contexte ([[96-evals-rag-agents|evals de RAG]])

**Piège** : augmenter le top-k pour « donner plus de contexte », ce qui dilue l'information utile.

---

Mise en situation : les utilisateurs posent des questions comme « quels fournisseurs des filiales de X ont eu un incident en 2025 ? », et ton RAG vectoriel échoue systématiquement. Que proposes-tu ?
?
<!--anki:45777c3e74682b5f4b36-->
1. **Reconnaître le type de question** : c'est du **multi-hop** avec agrégation, là où la similarité plate ne peut pas répondre ([[23-knowledge-graphs-ontologies|knowledge graphs]])
2. **Options** : requête sur une base structurée si les données existent déjà en base, ou **GraphRAG** si l'information est dans du texte
3. **Décomposer la question** en sous-questions (query rewriting) et laisser un **agent itérer** entre recherches ([[31-agents-fondamentaux|agentic RAG]])
4. **Comparer** les approches sur les mêmes evals avant d'investir dans un graphe, dont l'extraction coûte cher
5. **Attention aux droits** : le parcours de graphe doit respecter les ACL comme le retrieval

**Piège** : construire un knowledge graph complet alors que dix requêtes SQL bien faites suffisaient.

---

Mise en situation : après un changement de modèle d'embedding, la qualité du RAG s'effondre en production. Que s'est-il passé et comment gères-tu ?
?
<!--anki:4e6821404a43506d753e-->
1. **Cause probable** : l'index contient les anciens vecteurs, les requêtes sont encodées avec le nouveau modèle. Les deux espaces ne sont pas comparables
2. **Revenir** immédiatement à l'ancien modèle côté requête, le temps de corriger
3. **Réindexer** tout le corpus avec le nouveau modèle, dans un index séparé
4. **Basculer** par un test A/B ou un canary, avec comparaison du recall@k sur le golden dataset ([[112-cicd-modeles|CI/CD]])
5. **Prévenir** : versionner le modèle d'embedding avec l'index, et refuser une requête si les versions diffèrent

**Piège** : réindexer en place, ce qui laisse l'index dans un état mixte pendant des heures.

---

## Connexions
- [[21-rag-fondamentaux|RAG fondamentaux]] — le socle
- [[35-context-engineering|Context engineering]] — placement et budget
- [[101-securite-llm-guardrails|Sécurité LLM]] — injection via documents, ACL
- [[31-agents-fondamentaux|Agents]] — l'agentic RAG
- [[32-tool-calling|Tool calling]] — l'agentic RAG appelle des outils
- [[23-knowledge-graphs-ontologies|Knowledge graphs & ontologies]] — GraphRAG en détail
- [[134-recherche-vectorielle-ann|Recherche vectorielle & index ANN]] — HNSW, IVF, PQ, filtrage
- [[96-evals-rag-agents|Evals de RAG]] — mesurer chaque étage
- [[25-chunking-contextual-retrieval|Chunking avancé & contextual retrieval]] — agir sur ce qu'on indexe
- [[27-agents-recherche-deep-research|Agents de recherche]] — quand une recherche ne suffit plus
- [[113-monitoring-drift-feedback|Monitoring & drift]] — qualité en production et boucle de feedback
- [[145-cas-system-design|Cas de system design]] — des architectures types commentées
- [[24-cognee|Cognee]] — une mémoire d'agent en knowledge graph
- [[131-transformer-architecture|Architecture Transformer]] — le fonctionnement interne du modèle
- [[141-system-design-llm|System design LLM]] — la méthode de conception
- [[69-roofline-prefill-decode|Roofline & désagrégation]] — ce qui limite chaque phase de l'inférence
- [[00-moc-ai-engineering|MOC AI Engineering]]
