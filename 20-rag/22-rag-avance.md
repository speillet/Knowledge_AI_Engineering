# RAG — Avancé — Flashcards
Tags: #flashcards #ai-engineering #rag #retrieval #llm

Qu'est-ce que la recherche hybride ?
?
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
- **Rappel (recall@k)** : le bon passage est-il **présent** dans les k récupérés ? C'est le **plafond** du système : ce qui n'est pas remonté ne pourra jamais être utilisé
- **Précision** : quelle part des passages remontés est **utile** ? Elle joue sur le bruit, le coût et la dilution du contexte

Stratégie habituelle : **récupérer large** pour le rappel, puis **reranker** pour la précision ([[96-evals-rag-agents|evals de RAG]]).

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

## Mises en situation

Mise en situation : ton RAG juridique retrouve bien les documents pertinents (recall@20 de 0,95) mais les réponses restent moyennes. Que fais-tu ?
?
1. **Constater** : le retrieval fait son travail, le problème est en aval, dans le **classement** et le **contexte**
2. **Reranking** : un cross-encoder re-score les 20 passages pour n'en garder que 3 à 5 vraiment pertinents
3. **Ordre** : placer les meilleurs chunks **en début et en fin** de contexte, à cause du « lost in the middle »
4. **Grounding** : citations obligatoires et consigne d'abstention si le contexte ne suffit pas ([[143-hallucinations-grounding|hallucinations]])
5. **Mesurer** la triade : faithfulness, pertinence de la réponse, pertinence du contexte ([[96-evals-rag-agents|evals de RAG]])

**Piège** : augmenter le top-k pour « donner plus de contexte », ce qui dilue l'information utile.

---

Mise en situation : les utilisateurs posent des questions comme « quels fournisseurs des filiales de X ont eu un incident en 2025 ? », et ton RAG vectoriel échoue systématiquement. Que proposes-tu ?
?
1. **Reconnaître le type de question** : c'est du **multi-hop** avec agrégation, là où la similarité plate ne peut pas répondre ([[23-knowledge-graphs-ontologies|knowledge graphs]])
2. **Options** : requête sur une base structurée si les données existent déjà en base, ou **GraphRAG** si l'information est dans du texte
3. **Décomposer la question** en sous-questions (query rewriting) et laisser un **agent itérer** entre recherches ([[31-agents-fondamentaux|agentic RAG]])
4. **Comparer** les approches sur les mêmes evals avant d'investir dans un graphe, dont l'extraction coûte cher
5. **Attention aux droits** : le parcours de graphe doit respecter les ACL comme le retrieval

**Piège** : construire un knowledge graph complet alors que dix requêtes SQL bien faites suffisaient.

---

Mise en situation : après un changement de modèle d'embedding, la qualité du RAG s'effondre en production. Que s'est-il passé et comment gères-tu ?
?
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
- [[00-moc-ai-engineering|MOC AI Engineering]]
