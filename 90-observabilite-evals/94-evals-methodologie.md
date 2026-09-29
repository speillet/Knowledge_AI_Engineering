# Évaluation des systèmes LLM — Méthodologie — Flashcards
Tags: #flashcards #ai-engineering #evals #llm #qualite

Pourquoi l'évaluation est-elle la compétence centrale d'un AI Engineer senior ?
?
Parce qu'un système LLM est **non déterministe et sans spécification formelle** : sans evals, on ne peut **ni comparer deux versions, ni choisir un modèle, ni prouver qu'un changement améliore** quoi que ce soit. Les evals remplacent les tests unitaires comme **filet de sécurité du développement**.

---

À ne pas confondre : benchmark public et eval applicative ?
?
Un **benchmark public** (MMLU, GPQA, SWE-bench…) mesure une **capacité générale** du modèle. Une **eval applicative** mesure **ta tâche, sur tes données, avec tes critères**. Seule la seconde prédit la qualité en production ; les benchmarks servent au **pré-tri** des modèles ([[146-choix-modeles|choix de modèle]]).

---

Par quoi faut-il commencer pour construire des evals ?
?
Par l'**analyse d'erreurs** : lire **50 à 100 traces réelles**, noter ce qui ne va pas en texte libre (**open coding**), puis regrouper les problèmes en **catégories de défaillance** (axial coding). Les métriques viennent **après** : on mesure les défaillances observées, pas des critères génériques inventés a priori.

---

Qu'est-ce qu'un golden dataset et comment le constituer ?
?
Un **jeu d'entrées représentatives avec la réponse ou les critères attendus**. Sources :
- **traces de production** échantillonnées (le plus fidèle) ;
- cas **écrits par les experts métier** ;
- **cas limites et adversariaux** ;
- **données synthétiques** pour couvrir les trous (à relire).

Il doit être **versionné**, **stratifié** par type de requête et **enrichi à chaque bug** trouvé en production.

---

Combien d'exemples faut-il dans un jeu d'eval ?
?
Assez pour que **l'écart qu'on veut détecter dépasse le bruit**. Avec un taux de succès ~80 %, l'erreur standard sur 100 exemples est ≈ **4 points** ; sur 400, ≈ **2 points**. En pratique : **quelques dizaines** pour itérer vite, **plusieurs centaines** pour une décision de mise en production ([[114-reproductibilite-variance|intervalles de confiance]]).

---

Quelles sont les trois familles d'évaluateurs ?
?
1. **Code / règles** : exact match, regex, validité JSON, exécution de tests, appels d'outils attendus — **rapides, gratuits, fiables**.
2. **[[95-llm-as-judge|LLM-as-a-judge]]** : pour les critères subjectifs ou sémantiques — scalable mais **biaisé, à calibrer**.
3. **Humains** (experts, annotateurs) : la **référence**, chère et lente, qui sert à **valider les deux autres**.

Règle : utiliser le **plus simple qui marche** pour chaque critère.

---

Pourquoi préférer des critères binaires (pass/fail) aux notes de 1 à 10 ?
?
Les échelles de 1 à 10 sont **mal calibrées** (quelle différence entre 6 et 7 ?), **instables** d'un juge à l'autre et **difficiles à agir**. Un critère **binaire et précis** (« la réponse cite-t-elle une source du contexte ? ») est plus **reproductible**, plus facile à **aligner avec un humain** et dit directement **quoi corriger**.

---

À ne pas confondre : eval avec référence (reference-based) et eval sans référence (reference-free) ?
?
- **Avec référence** : on compare à une **réponse attendue** (exact match, similarité, juge qui compare). Fiable mais exige des réponses de référence.
- **Sans référence** : on vérifie des **propriétés** de la sortie (format, ton, fidélité au contexte, absence de PII). Applicable **en production**, où il n'y a pas de vérité terrain.

---

À ne pas confondre : évaluation offline et évaluation online ?
?
- **Offline** : sur un **jeu figé** avant déploiement — détecte les régressions, sert de [[112-cicd-modeles|gate CI]].
- **Online** : sur le **trafic réel** — évaluateurs sans référence sur un échantillon, feedback utilisateur, [[97-evals-online-ab-testing|A/B tests]].

Les deux se nourrissent : les échecs vus en ligne **alimentent le golden dataset**.

---

Pourquoi évaluer les composants **et** le système de bout en bout ?
?
Le bout en bout dit **si** ça marche ; les evals de composants disent **où** ça casse. Un [[96-evals-rag-agents|RAG]] se découpe en **retrieval** (le bon document est-il remonté ?) et **génération** (la réponse est-elle fidèle ?) ; un agent en **choix d'outil**, **arguments**, **trajectoire** et **résultat final**.

---

Qu'est-ce que l'« eval-driven development » ?
?
Écrire **l'eval avant le changement**, comme en TDD : définir le cas qui échoue, modifier prompt, retrieval ou modèle, puis vérifier que **le cas passe sans régresser ailleurs**. Chaque itération est **mesurée**, pas jugée « au feeling ».

---

Qu'est-ce que la saturation d'une eval et que faire ?
?
Quand le système atteint **~100 %** sur le jeu, l'eval **ne discrimine plus** : elle protège encore contre les régressions mais ne guide plus l'amélioration. Il faut **ajouter des cas plus durs** (échecs de prod, cas adversariaux) pour garder un **jeu de progrès** distinct du **jeu de non-régression**.

---

Quels sont les anti-patterns classiques en évaluation ?
?
- Adopter des **métriques génériques** (« helpfulness ») sans analyse d'erreurs.
- **Juge LLM non validé** contre des humains.
- **Jeu trop petit** et conclusions tirées d'un écart de 2 points.
- **Contamination** : optimiser les prompts sur le jeu de test lui-même (**overfitting** aux evals).
- Oublier les **coûts et la latence** dans la comparaison.

---

## Mises en situation

Mise en situation : tu reprends un assistant en production qui n'a aucune eval. Que fais-tu pendant la première semaine ?
?
1. **Lire 50 à 100 traces réelles** et noter en texte libre ce qui ne va pas, sans métrique préconçue
2. **Regrouper** ces observations en catégories de défaillance : source manquante, format cassé, ton, hors périmètre
3. **Constituer un golden dataset** à partir de ces cas, stratifié par type de requête et versionné
4. **Choisir l'évaluateur le plus simple** par catégorie : code d'abord, juge seulement pour le subjectif
5. **Brancher en CI** pour détecter les régressions dès le prochain changement ([[112-cicd-modeles|eval gate]])

**Piège** : commencer par des métriques génériques comme « utilité » ou « pertinence », qui ne disent jamais quoi corriger.

---

Mise en situation : un collègue annonce que son nouveau prompt fait passer le score de 78 % à 81 % sur 100 exemples. Quelle est ta réaction ?
?
1. **Calculer le bruit** : à 80 % de succès sur 100 exemples, l'erreur standard vaut environ 4 points. Un écart de 3 points ne prouve rien
2. **Comparer en apparié** : regarder les cas qui changent d'état, pas seulement les moyennes ([[114-reproductibilite-variance|comparaison appariée]])
3. **Agrandir le jeu** ou répéter les exécutions pour réduire l'incertitude
4. **Regarder ce qui casse** : un gain global peut cacher une régression sur un segment critique
5. **Vérifier la contamination** : le prompt a-t-il été écrit en regardant ces mêmes exemples ?

**Piège** : promouvoir un changement sur un écart inférieur à l'intervalle de confiance.

---

Mise en situation : ton eval principale affiche 99 % depuis trois mois, alors que les utilisateurs continuent de remonter des problèmes. Que se passe-t-il ?
?
1. **L'eval est saturée** : elle ne discrimine plus, même si elle protège encore des régressions
2. **Séparer les jeux** : un jeu de non-régression, et un jeu de progrès avec des cas nettement plus durs
3. **Alimenter** ce nouveau jeu avec les échecs réels remontés du terrain
4. **Vérifier la couverture** : les problèmes signalés appartiennent-ils à des catégories jamais mesurées ?
5. **Compléter par de l'online** : scores sur échantillon, feedback, A/B ([[97-evals-online-ab-testing|evals online]])

**Piège** : se rassurer avec un score élevé sur un jeu qui ne ressemble plus au trafic réel.

---

## Connexions
- [[95-llm-as-judge|LLM-as-a-judge]] — l'évaluateur automatique des critères subjectifs
- [[96-evals-rag-agents|Evals de RAG & d'agents]] — évaluer par composant
- [[97-evals-online-ab-testing|Evals online & A/B testing]] — mesurer en production
- [[92-chainforge-evals-prompts|ChainForge]] — outillage de comparaison de prompts
- [[91-langfuse-observabilite|Langfuse]] — traces, datasets et scores
- [[114-reproductibilite-variance|Reproductibilité & variance]] — statistiques des evals
- [[112-cicd-modeles|CI/CD des modèles]] — les evals comme gates
- [[151-donnees-curation-annotation|Données & annotation]] — produire des labels fiables
- [[12-optimisation-automatique-prompts|Optimisation automatique de prompts]] — la métrique comme moteur d'optimisation
- [[00-moc-ai-engineering|MOC AI Engineering]]
