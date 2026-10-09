# Évaluation des systèmes LLM — Méthodologie — Flashcards
Tags: #flashcards #ai-engineering #evals #llm #qualite
<!-- summary: benchmark ou eval applicative, analyse d'erreurs, golden dataset, taille des jeux, familles d'évaluateurs, critères binaires, avec ou sans référence, offline et online, eval-driven development, saturation, anti-patterns. -->


Pourquoi l'évaluation est-elle la compétence centrale d'un AI Engineer senior ? <!--anki:672b7a264c7763732b24-->
?
Les **evals** permettent de comparer les comportements d'un système IA sur des tâches, populations et critères définis. Elles quantifient qualité, limites et régressions, au-delà d'une démonstration réussie.

Elles **complètent les tests logiciels** : tests unitaires pour le code, contrats et intégration pour les interfaces, evals pour les comportements du modèle et du système complet. Des propriétés formelles restent possibles, comme un schéma de sortie ou une permission. Une bonne eval fournit une preuve limitée à son protocole, pas une garantie de toutes les réponses futures.

---

À ne pas confondre : benchmark public et eval applicative ? <!--anki:7a433e69633c7d2f2c32-->
?
Un **benchmark public** mesure les tâches et conditions définies par ses auteurs ; une **eval applicative** représente les usages et critères de ton service. Le premier aide au pré-tri ; la seconde aide à choisir et contrôler une solution pour ce besoin.

Ni l'un ni l'autre ne prédit automatiquement la production. Vérifier contamination, représentativité, versions et protocole, puis confronter les résultats au trafic réel. Un modèle bien classé sur du code peut mal extraire les champs de tes documents. Comparer des variantes sur les mêmes cas et budgets.

---

Par quoi faut-il commencer pour construire des evals ? <!--anki:45287263614956357d47-->
?
Définir la **tâche et ses exigences**, puis examiner des exemples et erreurs réels ou simulés : sources manquantes, mauvais montant, action interdite, format invalide. Regrouper les défaillances pour choisir des critères qui guident une correction.

Un premier échantillon aide à découvrir les problèmes, sans prétendre estimer leur fréquence réelle. Ajouter les cas limites importants même s'ils ne sont pas encore observés. Les contrats déjà connus, comme droits d'accès ou exactitude d'un calcul, n'attendent pas un incident pour devenir des critères d'évaluation.

---

Qu'est-ce qu'un golden dataset et comment le constituer ? <!--anki:686a7c383d56593b4855-->
?
Un **jeu de référence versionné** contient entrées, contexte nécessaire et réponses ou critères attendus. Combiner trafic représentatif, cas métier, régressions connues et cas limites relus.

Distinguer leurs usages : les bugs ajoutés nourrissent la non-régression ; un test final indépendant sert à estimer la qualité sans guider les réglages. Un jeu volontairement enrichi en cas difficiles ne représente plus directement la fréquence du trafic. Documenter provenance, segments, droits et qualité des annotations. « Golden » ne signifie pas que chaque référence est infaillible ou immuable.

---

Combien d'exemples faut-il dans un jeu d'eval ? <!--anki:4a7c3664572c6c572a38-->
?
Assez pour que **l'écart qu'on veut détecter dépasse le bruit**. Avec un taux de succès ~80 %, l'erreur standard sur 100 exemples est ≈ **4 points** ; sur 400, ≈ **2 points**. En pratique : **quelques dizaines** pour itérer vite, **plusieurs centaines** pour une décision de mise en production ([[114-reproductibilite-variance|intervalles de confiance]]).

---

Quelles sont les trois familles d'évaluateurs ? <!--anki:7a46426d355b3c3e386b-->
?
Le **code** contrôle des propriétés explicites : schéma, valeur attendue ou tests d'exécution. Un **juge LLM** apprécie des critères sémantiques définis. Les **humains** établissent et discutent des références, notamment pour les cas ambigus.

Chacun peut se tromper : assertion mal conçue, juge biaisé, annotation incohérente. Choisir le moyen le plus simple qui mesure réellement le critère, puis le valider. Le code a un coût et sa détermination ne garantit pas la pertinence du test. Une sortie JSON valide ne prouve pas que son montant est correct.

---

Pourquoi préférer des critères binaires (pass/fail) aux notes de 1 à 10 ? <!--anki:796e4c44435b4b7e4e43-->
?
Un **critère binaire explicite** facilite une décision de conformité : « toutes les affirmations chiffrées sont-elles étayées ? ». Il rend l'erreur localisable et se compare à une annotation de référence.

Ce n'est pas toujours supérieur à une échelle : la qualité stylistique ou une pertinence graduée peuvent nécessiter plusieurs niveaux, décrits par des exemples d'ancrage. Une question binaire vague reste vague. Mesurer accord et erreurs des évaluateurs, et ne pas réduire plusieurs dimensions à un oui/non qui masque les régressions.

---

À ne pas confondre : eval avec référence (reference-based) et eval sans référence (reference-free) ? <!--anki:4d5563343c4437657732-->
?
Une eval **avec référence** utilise une réponse, des faits ou un résultat attendu pour comparer la sortie. Une eval **sans réponse de référence** vérifie un critère à partir des données disponibles : format, consigne ou soutien par les documents.

« Sans référence » ne veut pas dire sans information fiable : juger la fidélité exige le contexte source. Une référence peut aussi contenir des erreurs ou n'illustrer qu'une formulation valable. Choisir les informations et le vérificateur selon le critère ; les expressions *reference-based* et *reference-free* doivent être définies dans le protocole.

---

À ne pas confondre : évaluation offline et évaluation online ? <!--anki:454b247c583369367a35-->
?
- **Offline** : sur un **jeu figé** avant déploiement — détecte les régressions, sert de [[112-cicd-modeles|gate CI]].
- **Online** : sur le **trafic réel** — évaluateurs sans référence sur un échantillon, feedback utilisateur, [[97-evals-online-ab-testing|A/B tests]].

Les deux se nourrissent : les échecs vus en ligne **alimentent le golden dataset**.

---

Pourquoi évaluer les composants **et** le système de bout en bout ? <!--anki:4529237523433a3c5f4b-->
?
Le bout en bout dit **si** ça marche ; les evals de composants disent **où** ça casse. Un [[96-evals-rag-agents|RAG]] se découpe en **retrieval** (le bon document est-il remonté ?) et **génération** (la réponse est-elle fidèle ?) ; un agent en **choix d'outil**, **arguments**, **trajectoire** et **résultat final**.

---

Qu'est-ce que l'« eval-driven development » ? <!--anki:774521632879232f4d3b-->
?
Écrire **l'eval avant le changement**, comme en TDD : définir le cas qui échoue, modifier prompt, retrieval ou modèle, puis vérifier que **le cas passe sans régresser ailleurs**. Chaque itération est **mesurée**, pas jugée « au feeling ».

---

Qu'est-ce que la saturation d'une eval et que faire ? <!--anki:4730412c2d44506c2d2f-->
?
Quand le système atteint **~100 %** sur le jeu, l'eval **ne discrimine plus** : elle protège encore contre les régressions mais ne guide plus l'amélioration. Il faut **ajouter des cas plus durs** (échecs de prod, cas adversariaux) pour garder un **jeu de progrès** distinct du **jeu de non-régression**.

---

Quels sont les anti-patterns classiques en évaluation ? <!--anki:7a58572a706e4a592975-->
?
- Adopter des **métriques génériques** (« helpfulness ») sans analyse d'erreurs.
- **Juge LLM non validé** contre des humains.
- **Jeu trop petit** et conclusions tirées d'un écart de 2 points.
- **Contamination** : optimiser les prompts sur le jeu de test lui-même (**overfitting** aux evals).
- Oublier les **coûts et la latence** dans la comparaison.

---

Calcul : pour une proportion de succès proche de 70 %, combien d’observations de Bernoulli indépendantes faut-il environ pour une marge de ±3 points à 95 %, avec l’approximation normale ? <!--anki:3763333165623463643835383436323462346134626564643634653863326439-->
?
On inverse la formule de l'intervalle de confiance à 95 % ([[114-reproductibilite-variance|variance]]) :
```text
n ≈ 1,96² × p(1 − p) / marge²
± 3 points  : 3,84 × 0,7 × 0,3 / 0,03² ≈ 900 cas
± 5 points  : 3,84 × 0,21 / 0,05²      ≈ 320 cas
± 10 points :                           ≈  80 cas
```
Diviser la marge par 2 demande 4 fois plus de cas. Pour départager deux versions à 2 ou 3 points d'écart, une comparaison **appariée** sur les mêmes cas est plus sensible.

---

## Mises en situation

Mise en situation : tu reprends un assistant en production qui n'a aucune eval. Que fais-tu pendant la première semaine ? <!--anki:484b26356c43544e5055-->
?
1. **Clarifier les exigences** : tâches attendues, contraintes et erreurs critiques déjà connues.
2. **Lire des traces variées** et regrouper les défaillances observées, sans se limiter aux incidents signalés.
3. **Séparer développement et test**, avec références vérifiées ; garder aussi un corpus de non-régression ciblé.
4. **Choisir des critères observables** : assertions pour les contrats, juge validé ou humain pour le reste.
5. **Brancher une évaluation en CI**, puis suivre les segments et la production ([[112-cicd-modeles|eval gate]]).

**Piège** : prendre le taux d'erreur d'un corpus composé de bugs pour celui du trafic réel.

---

Mise en situation : un collègue annonce que son nouveau prompt fait passer le score de 78 % à 81 % sur 100 exemples. Quelle est ta réaction ? <!--anki:63427c294379574b6125-->
?
1. **Vérifier le protocole** : mêmes 100 exemples, références correctes et conditions comparables ?
2. **Comparer en apparié** : compter les cas gagnés et perdus ; la différence des moyennes ne donne pas son incertitude ([[114-reproductibilite-variance|comparaison appariée]]).
3. **Quantifier l'incertitude** avec une méthode adaptée aux observations, puis répéter les générations si elles varient.
4. **Examiner les régressions** par segment, surtout les erreurs coûteuses.
5. **Vérifier l'indépendance du test**, puis augmenter l'échantillon si la décision reste incertaine.

**Piège** : assimiler la marge d'erreur d'un score individuel à celle de la différence appariée, ou promouvoir trois réussites supplémentaires sans analyser les cas.

---

Mise en situation : ton eval principale affiche 99 % depuis trois mois, alors que les utilisateurs continuent de remonter des problèmes. Que se passe-t-il ? <!--anki:457660597676656d2e26-->
?
1. **L'eval est saturée** : elle ne discrimine plus, même si elle protège encore des régressions
2. **Séparer les jeux** : un jeu de non-régression, et un jeu de progrès avec des cas nettement plus durs
3. **Alimenter** ce nouveau jeu avec les échecs réels remontés du terrain
4. **Vérifier la couverture** : les problèmes signalés appartiennent-ils à des catégories jamais mesurées ?
5. **Compléter par de l'online** : scores sur échantillon, feedback, A/B ([[97-evals-online-ab-testing|evals online]])

**Piège** : se rassurer avec un score élevé sur un jeu qui ne ressemble plus au trafic réel.

---

## Sources

- [Sculley et al. — test et dette des systèmes ML](https://papers.nips.cc/paper/5656-hidden-technical-debt-in-machine-learning-systems)
- [Zheng et al. — juges, critères et biais](https://arxiv.org/abs/2306.05685)

- [NIST — test de McNemar pour observations binaires appariées](https://www.itl.nist.gov/div898/software/dataplot/refman1/auxillar/mcnemar.htm)

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
- [[98-debogage-agents|Débogage des agents]] — l'analyse d'erreurs avant les métriques
- [[147-leadership-technique-ia|Leadership technique]] — standards d'équipe et décisions
- [[148-pipelines-batch-llm|Pipelines batch]] — traiter des millions d'items à moindre coût
- [[156-ia-responsable|IA responsable]] — biais, équité et transparence
- [[49-agents-de-code|Agents de code]] — utiliser et intégrer les agents de code
- [[53-donnees-synthetiques-distillation|Données synthétiques & distillation]] — générer des données et transférer vers un petit modèle
- [[172-validation-metriques-ml|Validation & métriques ML]] — splits, classes rares et comparaison des prédicteurs
- [[99-statistiques-decisions-experimentales|Statistiques pour décider en IA]] — passer d'un score à une décision justifiée
- [[146-choix-modeles|Choix de modèles]] — départager les candidats sur la tâche
- [[00-moc-ai-engineering|MOC AI Engineering]]
