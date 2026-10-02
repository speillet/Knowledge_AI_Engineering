# Text-to-SQL & données structurées — Flashcards
Tags: #flashcards #ai-engineering #rag #text-to-sql #donnees #llm
Vérifié le : 29 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.

Qu'est-ce que le text-to-SQL ?
?
<!--anki:797b6930743e52773076-->
Un LLM **traduit une question en langage naturel en requête SQL**, qu'on exécute sur la base ; le résultat est ensuite présenté ou résumé. C'est le moyen de répondre aux questions **chiffrées et agrégées** (« combien », « quelle évolution », « top 10 ») sur des données tabulaires.

---

À ne pas confondre : text-to-SQL et RAG ?
?
<!--anki:49415b3c493c4d7148-->
- **RAG** : retrouve des **passages de texte** pertinents et laisse le LLM en tirer la réponse. Bon pour « que dit la politique de remboursement ? »
- **Text-to-SQL** : fait **calculer** la base. Bon pour « combien de remboursements en mars, par région ? »

Un RAG ne sait pas **compter** : il remonte k chunks, jamais l'ensemble des lignes. Les assistants d'entreprise combinent souvent les deux, avec un **routage** selon la question ([[21-rag-fondamentaux|quand ne pas faire de RAG]]).

---

Que met-on dans le prompt d'un système text-to-SQL ?
?
<!--anki:7145587c263171674831-->
- Le **schéma** : tables, colonnes, types, clés, avec des **descriptions métier** (« `statut = 3` signifie annulé »)
- Quelques **valeurs d'exemple** par colonne catégorielle, pour écrire les bons filtres
- Des **exemples question → SQL** validés, proches de la question (sélectionnés par similarité)
- Le **dialecte** (PostgreSQL, BigQuery, Snowflake) et les règles : lecture seule, `LIMIT`, fuseau horaire

Le schéma brut sans descriptions est la cause d'erreur la plus fréquente.

---

Comment faire avec un schéma de 500 tables ?
?
<!--anki:744e306277797e296e65-->
Par **schema linking** : une première étape sélectionne les **tables et colonnes utiles** à la question (recherche sur les descriptions, ou LLM), puis on ne met que ce sous-schéma dans le prompt de génération. Sans cela, le schéma sature le contexte et le modèle **confond des colonnes homonymes**.

Mieux encore : exposer des **vues métier** préparées plutôt que les tables brutes.

---

Qu'est-ce qu'une couche sémantique et pourquoi aide-t-elle ?
?
<!--anki:4a75536f372969675526-->
Une couche qui définit **une fois** les **métriques et dimensions** de l'entreprise (« chiffre d'affaires net », « client actif ») avec leur calcul officiel (dbt Semantic Layer, Cube, LookML). Le LLM choisit **quelle métrique et quels filtres**, au lieu d'écrire la jointure et la formule.

Gain : les chiffres **correspondent à ceux des tableaux de bord**, et le LLM ne peut pas inventer sa propre définition du CA.

---

Comment sécuriser l'exécution des requêtes générées ?
?
<!--anki:503f54667a6e2f616d4d-->
- Compte de base en **lecture seule**, sur une **réplique**, avec seulement les schémas autorisés
- **Sécurité au niveau des lignes** (row-level security) : l'utilisateur ne voit que ses données, quelle que soit la requête
- **Analyse de la requête** avant exécution : une seule instruction `SELECT`, tables autorisées
- **Timeouts**, `LIMIT` et budget : estimation préalable du coût (`EXPLAIN`, dry run BigQuery)

La requête générée est une **entrée non fiable**, influençable par injection ([[101-securite-llm-guardrails|sécurité]]).

---

Comment un système text-to-SQL corrige-t-il ses erreurs ?
?
<!--anki:493c403f785f2c3e4b37-->
Par une **boucle d'exécution** : on exécute (ou `EXPLAIN`), et en cas d'erreur on renvoie le **message d'erreur** au modèle pour qu'il corrige, avec un nombre limité de tentatives. Un résultat **vide ou aberrant** (0 ligne, montant négatif) peut aussi déclencher une vérification.

Cela corrige la syntaxe et les noms de colonnes, **pas** les erreurs de sens : une requête qui s'exécute peut répondre à une autre question.

---

À ne pas confondre : exact match et execution accuracy ?
?
<!--anki:4a5e2b332a234d433067-->
- **Exact match** : la requête générée est-elle **identique** à la requête de référence ? Trop strict, car il existe plusieurs SQL corrects
- **Execution accuracy** : les deux requêtes donnent-elles le **même résultat** sur la base ? C'est la métrique standard

Limite de la seconde : deux requêtes peuvent coïncider sur les données de test par hasard. On teste sur une base **réaliste** et on vérifie les cas limites.

---

Quels benchmarks de text-to-SQL connaître ?
?
<!--anki:6976465b5b7c3160683e-->
- **Spider** (2018) : bases variées mais simples, aujourd'hui saturé
- **BIRD** (2023) : bases plus grandes et **sales**, connaissances métier nécessaires
- **Spider 2.0** (2024) : workflows d'entreprise réels (BigQuery, Snowflake), schémas de centaines de colonnes ; les taux de réussite y restent bien plus bas

L'écart entre ces benchmarks rappelle qu'un score public ne prédit pas le résultat **sur sa propre base** ([[146-choix-modeles|choix de modèle]]).

---

Comment gérer une question ambiguë ?
?
<!--anki:62717d725e7e684b387b-->
« Les ventes de mars » : quelle année, quel périmètre, CA brut ou net ? Options :
- **Demander une précision** quand l'ambiguïté change fortement le résultat
- **Appliquer une convention documentée** (dernière année complète, CA net) et **l'afficher** dans la réponse
- **Montrer la requête** ou sa traduction en langage naturel, pour que l'utilisateur vérifie ce qui a été calculé

Un chiffre faux présenté avec assurance est pire qu'une question de clarification ([[143-hallucinations-grounding|abstention]]).

---

## Mises en situation

Mise en situation : le directeur commercial veut « poser ses questions à l'entrepôt de données en langage naturel ». L'entrepôt compte 300 tables mal documentées. Comment cadres-tu le projet ?
?
<!--anki:48286c646f7b7a5a404e-->
1. **Réduire le périmètre** : un domaine (ventes), une dizaine de vues métier documentées, pas les 300 tables
2. **S'appuyer sur la couche sémantique** si elle existe, pour que les chiffres collent aux tableaux de bord
3. **Construire le jeu d'eval** : 100 questions réelles du métier avec leur résultat attendu, en execution accuracy
4. **Sécuriser** : lecture seule, réplique, row-level security, timeouts et budget par requête
5. **Rendre vérifiable** : afficher la requête, les filtres appliqués et les conventions choisies

**Piège** : brancher le LLM sur tout l'entrepôt et laisser le métier découvrir des chiffres faux en comité.

---

Mise en situation : ton assistant text-to-SQL a 85 % d'execution accuracy en test, mais les utilisateurs se plaignent de chiffres « qui ne collent pas ». Que cherches-tu ?
?
<!--anki:76553f3b417169662447-->
1. **Collecter les cas signalés** avec la question, la requête et le chiffre attendu par l'utilisateur
2. **Classer les écarts** : mauvaise définition métier (CA brut ou net), filtre implicite oublié (clients test, annulations), période ambiguë, vraie erreur SQL
3. **Corriger à la source** : descriptions de colonnes, exemples question → SQL, métriques dans la couche sémantique
4. **Ajouter ces cas au jeu d'eval**, qui ne reflétait pas les vraies questions ([[153-data-flywheel-versioning|flywheel]])
5. **Afficher les conventions** appliquées dans chaque réponse

**Piège** : changer de modèle alors que l'erreur vient de définitions métier absentes du prompt.

---

## Connexions
- [[21-rag-fondamentaux|RAG — Fondamentaux]] — le texte, quand le SQL ne convient pas
- [[23-knowledge-graphs-ontologies|Knowledge graphs]] — Text2Cypher, le même problème sur un graphe
- [[32-tool-calling|Tool calling]] — exposer l'exécution SQL comme un outil
- [[101-securite-llm-guardrails|Sécurité LLM]] — la requête générée est une entrée non fiable
- [[96-evals-rag-agents|Évaluation des RAG & des agents]] — mesurer sur ses propres questions
- [[143-hallucinations-grounding|Hallucinations & grounding]] — clarifier plutôt qu'inventer
- [[00-moc-ai-engineering|MOC AI Engineering]]
