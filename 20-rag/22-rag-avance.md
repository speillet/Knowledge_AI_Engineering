# RAG — Avancé — Flashcards
Tags: #flashcards #ai-engineering #rag #retrieval #llm
<!-- summary: recherche hybride (BM25, RRF), reranking, query rewriting, HyDE et ses limites, filtrage par métadonnées et ACL, GraphRAG, agentic RAG, « lost in the middle », problèmes de production (fraîcheur, droits, ré-indexation), fusion RRF et échelles de scores. -->


Qu'est-ce que la recherche hybride ? <!--anki:783b3a7d537e53723532-->
?
La combinaison **lexicale (BM25) + vectorielle**, fusionnée (ex. **RRF**) : robuste aux termes exacts (références, codes, noms) que le vectoriel seul rate.
```text
RRF : score(doc) = Σ  1 / (k + rang_dans_la_liste)      k ≈ 60

doc A : rang 1 en BM25, rang 5 en vectoriel → 1/61 + 1/65 = 0,0318
doc B : rang 3 en BM25, rang 2 en vectoriel → 1/63 + 1/62 = 0,0320  ← meilleur
```
L'intérêt du RRF : il ne travaille que sur les **rangs**, donc aucune calibration de scores hétérogènes n'est nécessaire.

Par exemple, une référence `AB-204` bénéficie du lexical, tandis qu'une reformulation du problème peut bénéficier des embeddings. RRF ne prouve pas qu'un document est pertinent : il combine les classements disponibles. Le paramètre `k` de sa formule est une constante de lissage, distincte du nombre de résultats finalement récupérés.

---

Qu'est-ce que le reranking ? <!--anki:72403c653b3e44335232-->
?
Un **cross-encoder re-score** les passages du retrieval initial (query et passage évalués **ensemble**) : précision nettement supérieure, au prix d'un peu de latence.
```text
retrieval large  : top 50 candidats  (hybride, ~20 ms)
reranking        : on garde les 5 meilleurs  (~50 à 200 ms)
génération       : 5 chunks dans le contexte au lieu de 50
```
Double bénéfice : **plus de précision** et **moins de tokens** envoyés au modèle ([[121-couts-inference|coûts]]).

Le reranker ne peut sélectionner qu'un passage **déjà présent parmi les candidats** : il ne corrige pas un document absent de l'index ou exclu par le premier retrieval. Les latences ci-dessus sont illustratives. Mesurer le gain de classement et la qualité finale, car un passage bien classé peut rester obsolète ou insuffisant pour répondre.

---

À ne pas confondre : rappel et précision dans un RAG ? <!--anki:506d6d49793b6532463c-->
?
- **Rappel (recall@k)** : le bon passage est-il **présent** dans les k récupérés ? C'est le **plafond** du système : ce qui n'est pas remonté ne pourra jamais être utilisé
- **Précision** : quelle part des passages remontés est **utile** ? Elle joue sur le bruit, le coût et la dilution du contexte

Stratégie habituelle : **récupérer large** pour le rappel, puis **reranker** pour la précision ([[96-evals-rag-agents|evals de RAG]]).

---

Qu'est-ce que le query rewriting ? <!--anki:76394545532971765776-->
?
**Reformuler ou décomposer la question** avant le retrieval, car la question de l'utilisateur est rarement la meilleure requête :
- **Multi-query** : plusieurs variantes, résultats fusionnés
- **Step-back** : une question plus générale, pour remonter le contexte utile
- **Décomposition** : sous-questions pour une question à plusieurs sauts
- **Contextualisation** : réécrire « et pour l'an dernier ? » en question autonome, à partir de l'historique de conversation

Exemple de décomposition : « notre politique de télétravail est-elle plus généreuse qu'en 2023 ? » devient deux recherches, politique actuelle et politique 2023, avant la comparaison. Coût : un appel LLM de plus avant la recherche.

---

Qu'est-ce que HyDE ? <!--anki:513c5b5f50533662435f-->
?
**Hypothetical Document Embeddings** : le LLM rédige une **réponse hypothétique** à la question, et on cherche les documents proches de cette réponse plutôt que de la question. Une réponse ressemble davantage aux passages recherchés qu'une question courte : « pourquoi mon pod redémarre-t-il en boucle ? » produit un passage hypothétique mentionnant `CrashLoopBackOff` et `OOMKilled`, termes de la documentation absents de la question.

Limites : un appel LLM en plus, et une réponse hypothétique **fausse** peut orienter la recherche vers de mauvais passages. Utile surtout quand questions et documents emploient des vocabulaires différents.

---

À quoi sert le metadata filtering ? <!--anki:70794c6a37282d7b332c-->
?
À combiner similarité et **filtres structurés** (date, source, tenant, **permissions/ACL**) — indispensable pour la sécurité : ne jamais retrouver ce que l'utilisateur n'a pas le droit de voir.

Les droits proviennent de l'identité authentifiée, jamais d'un tenant fourni librement par le modèle. Avec pgvector, par exemple :
```sql
SELECT id, texte FROM chunks
WHERE tenant_id = :tenant AND :groupe = ANY(groupes_autorises) AND date_effet <= current_date
ORDER BY embedding <=> :vecteur_question LIMIT 10;      -- distance cosinus
```
Propager la même isolation aux caches et citations. Tester notamment deux utilisateurs posant la même question avec des permissions différentes.

---

Qu'est-ce que GraphRAG ? <!--anki:654c65592a606b60292c-->
?
Un RAG appuyé sur un **knowledge graph** : utile pour les questions **multi-hop** ou globales (« quels liens entre X et Y ? ») où la similarité plate échoue.

Par exemple, relier une entreprise à ses filiales, puis aux contrats concernés, demande plusieurs relations explicites. Selon l'architecture, la recherche parcourt le graphe ou utilise des résumés de communautés. Le coût d'extraction, la résolution des entités et la maintenance du graphe doivent être justifiés par un gain mesuré face à un RAG plus simple.

---

Qu'est-ce que l'agentic RAG ? <!--anki:625d426536733d593a29-->
?
L'**agent décide quand et quoi chercher** : il itère (recherche → lecture → nouvelle requête) au lieu d'un retrieval unique en amont.

Une première source peut révéler une date ou une entité à vérifier par une deuxième recherche. Cette adaptation aide les questions complexes, mais ajoute des appels et des risques de boucle. Fixer un budget de recherches, conserver les preuves et arrêter avec une réponse partielle ou une abstention si les sources restent insuffisantes.

---

Quels problèmes de production spécifiques au RAG ? <!--anki:6a455549472f7c24745b-->
?
Le RAG doit maintenir la cohérence entre **sources, index, droits et caches** :
- Propager modifications, suppressions et révocations d'accès, pas seulement ajouter des documents.
- Versionner [[133-embeddings-representations|embeddings]] et chunking ; une migration peut nécessiter de réencoder le corpus.
- Détecter les pertes de contenu au [[162-document-parsing|parsing]].

Exemple : un document supprimé de la source reste exposé si ses anciens chunks ou une réponse en cache survivent. Suivre le délai de propagation et tester cette suppression de bout en bout. Un index techniquement disponible mais en retard sur les droits ne constitue pas un service correct.

---

Pourquoi l'ordre des chunks dans le contexte compte-t-il ? <!--anki:6e6c685336744b2e532a-->
?
Certains modèles exploitent moins bien une preuve située **au milieu d'un long contexte** : c'est l'effet « lost in the middle ». L'ordre des passages peut donc changer la réponse, même si les sources sont identiques.

Tester plusieurs ordres : rejouer 200 questions avec la preuve en position 1, 5 puis 10 sur 10 passages, et comparer l'exactitude. Placer ensuite les preuves importantes dans les positions bien exploitées par le modèle et supprimer les redondances. **Ce n'est pas une règle universelle début/fin** : l'effet dépend du modèle, de la tâche et de la longueur. Préserver aussi la cohérence des passages liés.

---

Pourquoi la fusion RRF résiste-t-elle aux échelles de scores différentes des moteurs de recherche ? <!--anki:6437333561303037353838643465623039383361623636653232656563323138-->
?
La **Reciprocal Rank Fusion** utilise les rangs plutôt que les scores bruts : un document reçoit une somme de termes `1 / (c + rang)`, avec une constante positive `c` fixée pour l'expérience.

Un score BM25 de 12 et une similarité vectorielle de 0,8 ne sont pas directement comparables ; leurs positions peuvent l'être. Dédupliquer par document ou passage avant d'interpréter le résultat. La fusion ne crée pas les preuves absentes des listes candidates et n'annule pas l'effet de leur profondeur. Mesurer ensuite rappel et qualité finale.

---

## Mises en situation

Mise en situation : ton RAG juridique retrouve bien les documents pertinents (recall@20 de 0,95) mais les réponses restent moyennes. Que fais-tu ? <!--anki:657e457c29693d3b524b-->
?
1. **Constater** : le retrieval fait son travail, le problème est en aval, dans le **classement** et le **contexte**
2. **Reranking** : un cross-encoder re-score les 20 passages pour n'en garder que 3 à 5 vraiment pertinents
3. **Ordre** : tester la position des meilleurs chunks, par exemple en début ou en fin de contexte, si le modèle est sensible au « lost in the middle »
4. **Grounding** : citations obligatoires et consigne d'abstention si le contexte ne suffit pas ([[143-hallucinations-grounding|hallucinations]])
5. **Mesurer** la triade : faithfulness, pertinence de la réponse, pertinence du contexte ([[96-evals-rag-agents|evals de RAG]])

**Piège** : augmenter le top-k pour « donner plus de contexte », ce qui dilue l'information utile.

---

Mise en situation : les utilisateurs posent des questions comme « quels fournisseurs des filiales de X ont eu un incident en 2025 ? », et ton RAG vectoriel échoue systématiquement. Que proposes-tu ? <!--anki:45777c3e74682b5f4b36-->
?
1. **Reconnaître le type de question** : c'est du **multi-hop** avec agrégation, là où la similarité plate ne peut pas répondre ([[23-knowledge-graphs-ontologies|knowledge graphs]])
2. **Options** : requête sur une base structurée si les données existent déjà en base, ou **GraphRAG** si l'information est dans du texte
3. **Décomposer la question** en sous-questions (query rewriting) et laisser un **agent itérer** entre recherches ([[31-agents-fondamentaux|agentic RAG]])
4. **Comparer** les approches sur les mêmes evals avant d'investir dans un graphe, dont l'extraction coûte cher
5. **Attention aux droits** : le parcours de graphe doit respecter les ACL comme le retrieval

**Piège** : construire un knowledge graph complet alors que dix requêtes SQL bien faites suffisaient.

---

Mise en situation : après un changement de modèle d'embedding, la qualité du RAG s'effondre en production. Que s'est-il passé et comment gères-tu ? <!--anki:4e6821404a43506d753e-->
?
1. **Cause probable** : l'index contient les anciens vecteurs, les requêtes sont encodées avec le nouveau modèle. Les deux espaces ne sont pas comparables
2. **Revenir** immédiatement à l'ancien modèle côté requête, le temps de corriger
3. **Réindexer** tout le corpus avec le nouveau modèle, dans un index séparé
4. **Basculer** par un test A/B ou un canary, avec comparaison du recall@k sur le golden dataset ([[112-cicd-modeles|CI/CD]])
5. **Prévenir** : versionner le modèle d'embedding avec l'index, et refuser une requête si les versions diffèrent

**Piège** : réindexer en place, ce qui laisse l'index dans un état mixte pendant des heures.

---

## Connexions
- [[20-010-rag-droits-versions|RAG : droits & versions]] — appliquer les permissions, dates d'effet et priorités de sources
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
