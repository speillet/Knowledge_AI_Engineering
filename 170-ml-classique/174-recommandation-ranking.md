# Recommandation & learning to rank — Flashcards
Tags: #flashcards #ai-engineering #ml-classique #recommandation #ranking
<!-- summary: objectif produit, génération de candidats et classement, filtrage collaboratif ou contenu, feedback implicite, modèles à deux tours, objectifs de ranking, négatifs, biais d'exposition, cold start, nDCG et diversité. -->


Pourquoi définir l'objectif produit avant d'entraîner un système de recommandation ? <!--anki:3961363434643038363137653430666262613063613338656334323464636161-->
?
Le modèle doit optimiser un **résultat utile**, pas seulement reproduire les clics historiques. Pour recommander des articles techniques, un clic, une lecture complète et une résolution de problème représentent des objectifs différents.

Définir l'événement, son horizon et les contraintes de qualité, de fraîcheur et de latence. Comparer une baseline de popularité ou de règles contextualisées. Un meilleur taux de clic peut provenir de titres trompeurs ; mesurer aussi satisfaction, couverture du catalogue et effets indésirables avant de conclure à une amélioration.

---

À ne pas confondre : génération de candidats et classement en recommandation ? <!--anki:6337313536363663346235333430386438653762623733373534623339323536-->
?
La **génération de candidats** réduit un grand catalogue à un sous-ensemble plausible, avec un budget de latence serré. Le **classement** ordonne ensuite ces candidats avec des caractéristiques et un calcul éventuellement plus coûteux.

Un excellent ranker ne récupère pas un article absent des candidats. Mesurer séparément le rappel des candidats et la qualité du classement, puis le parcours complet après filtres métier. Comparer les rankers sur un ensemble contrôlé aide au diagnostic ; mesurer seulement ce sous-ensemble ne décrit pas tout le système.

---

À ne pas confondre : filtrage collaboratif et recommandation fondée sur le contenu ? <!--anki:3437343438613636656665303462393562326563333639616465316539643433-->
?
Le **filtrage collaboratif** apprend à partir des interactions entre utilisateurs et éléments. La recommandation **par contenu** utilise leurs caractéristiques : thème, texte, catégorie ou attributs du contexte.

Le collaboratif peut retrouver des proximités absentes des descriptions, mais dépend de l'historique disponible. Le contenu aide notamment pour les nouveaux éléments correctement décrits. Une approche hybride combine ces signaux ; elle ne supprime pas les biais de collecte. Comparer selon l'ancienneté des utilisateurs et des éléments plutôt que sur une moyenne dominée par les plus populaires.

---

Pourquoi une absence de clic n'est-elle pas toujours un exemple négatif fiable ? <!--anki:3132393934613263633334663434663738366430396465633432666162643838-->
?
L'utilisateur n'a peut-être **jamais vu l'élément**, ou ne l'a pas remarqué à sa position. Le feedback implicite mélange préférence, exposition et contexte. L'absence d'interaction sur tout le catalogue ne signifie donc pas rejet explicite.

Journaliser les impressions réellement affichées, positions, candidats et versions. Définir un délai cohérent pour attribuer une interaction. Même une impression sans clic peut être ambiguë : onglet inactif, recommandation déjà connue ou objectif ne nécessitant pas d'ouverture. Le choix des labels modifie la tâche apprise.

---

Pourquoi un modèle à deux tours facilite-t-il la recherche de recommandations à grande échelle ? <!--anki:3065383238373765333138613466613738373362366637323932623433353634-->
?
Une tour encode le **contexte utilisateur**, l'autre l'**élément** ; une fonction simple, souvent un produit scalaire, compare leurs représentations. Les vecteurs des éléments peuvent être calculés à l'avance et indexés pour chercher rapidement des candidats.

Cette séparation limite les interactions fines entre contexte et élément pendant la recherche. Un ranker plus riche peut les exploiter ensuite. Versionner ensemble encodeurs et index, et réencoder les éléments lorsque nécessaire : mélanger des espaces incompatibles peut dégrader le rappel sans provoquer d'erreur technique.

---

À ne pas confondre : objectifs pointwise, pairwise et listwise en ranking ? <!--anki:6530643030626634366232363461313338303064346635633162353631656635-->
?
Un objectif **pointwise** apprend un score par élément ; **pairwise** apprend des préférences entre paires ; **listwise** optimise une propriété d'une liste. Ils diffèrent par le signal utilisé, le coût et leur lien avec la métrique finale.

Un classifieur de clic peut fournir une baseline pointwise, mais son accuracy ne mesure pas directement l'ordre du top-k. Former les paires ou listes à l'intérieur d'un contexte comparable. Choisir l'objectif selon les labels disponibles, puis vérifier le résultat sur le classement réellement affiché.

---

Comment le choix des exemples négatifs influence-t-il un recommender ? <!--anki:6565303930643130653632323461646539363931636330666365636534363966-->
?
Des négatifs **aléatoires** rendent souvent la séparation facile ; des négatifs difficiles apprennent des distinctions plus fines mais peuvent être de faux négatifs. Un article voisin non consulté peut réellement intéresser l'utilisateur.

Documenter la distribution d'échantillonnage et comparer les résultats sur des candidats représentatifs du service. Les scores appris avec des classes artificiellement rééquilibrées ne sont pas automatiquement des probabilités de clic calibrées. Conserver les exclusions métier et la temporalité : un élément indisponible au moment historique ne doit pas devenir un candidat plausible de ce moment.

---

Pourquoi les journaux d'un ancien recommender biaisent-ils l'évaluation du suivant ? <!--anki:3737323531313730663962313430373662653664373437316163366533326162-->
?
L'ancien système a choisi **ce qui était visible et à quelle position**. Les interactions observées reflètent cette politique, en plus des préférences. Un nouveau système proposant d'autres éléments rencontre des zones où les journaux apportent peu d'information.

Des pondérations par probabilité d'exposition peuvent aider sous hypothèses explicites, avec risque de forte variance et besoin de support. Elles ne créent pas d'observations pour une action jamais proposée. Une exploration contrôlée ou un test randomisé fournit des preuves complémentaires, selon le risque du produit.

---

Comment gérer le cold start d'un utilisateur ou d'un élément ? <!--anki:6262373936326638313331343465633862653739303832303765613138346431-->
?
Prévoir un **chemin sans historique** : popularité contextualisée, attributs de l'élément, intention de la session ou préférences explicitement fournies. Pour un élément nouveau, la description peut permettre une première représentation avant les interactions.

Mesurer ce segment séparément et définir la transition vers la personnalisation. Solliciter des préférences coûte un effort utilisateur ; une popularité globale peut mal servir des usages rares. Évaluer aussi le temps nécessaire pour exposer un nouvel élément pertinent, pas seulement les performances sur les utilisateurs déjà très actifs.

---

Calcul : quel nDCG@3 pour les pertinences binaires [0, 1, 1], avec deux éléments pertinents dans le jeu évalué ? <!--anki:3666363231343362656138353430363339303034336237356235313266343833-->
?
Avec un gain binaire et une décote logarithmique par position :
```text
DCG@3  = 0/log2(2) + 1/log2(3) + 1/log2(4) ≈ 1,1309
IDCG@3 = 1/log2(2) + 1/log2(3) + 0/log2(4) ≈ 1,6309
nDCG@3 = DCG/IDCG ≈ 0,6934
```
L'ordre idéal place les deux éléments pertinents en tête. Préciser pertinences, gain et univers de candidats pour comparer des scores. Le résultat évalue ce classement annoté ; il ne mesure ni exposition équitable ni satisfaction durable des utilisateurs.

---

Pourquoi ajouter diversité et contraintes métier après le score de pertinence ? <!--anki:3736356165376333353332633438366561353530353966616166313831636462-->
?
Les meilleurs scores individuels peuvent produire une **liste redondante**, indisponible ou mal adaptée à la session. Le reclassement applique exclusions, plafonds par catégorie, diversité ou fraîcheur selon un contrat explicite.

Mesurer le compromis entre pertinence et utilité de la liste, ainsi que les violations de contraintes. Les droits d'accès et exclusions impératives doivent être garantis par l'application. Une contrainte de diversité ne doit pas être présentée comme une amélioration universelle : sa valeur dépend de la tâche et de ce que l'utilisateur cherche à accomplir.

---

## Mises en situation

Mise en situation : ton nouveau ranker gagne en nDCG offline, mais le taux de résolution baisse en production. Que vérifies-tu ? <!--anki:6636323239656663353334623438376261623161383538353862366439313237-->
?
1. **Comparer les objectifs** : pertinence annotée, clic et résolution effective.
2. **Auditer les candidats et filtres**, avec leur disponibilité au moment historique.
3. **Examiner les biais d'exposition**, les positions et les changements de population.
4. **Découper les résultats** par cold start, thème et ancienneté.
5. **Tester une hypothèse à la fois** avec garde-fous produit et protocole online adapté.

**Piège** : conclure que toute progression d'une métrique de ranking améliore nécessairement l'expérience.

---

Mise en situation : les nouveaux documents pertinents ne sont jamais recommandés, malgré des descriptions complètes. Comment diagnostiques-tu ? <!--anki:3330623837396361663832663432653739666635613235343461306532376433-->
?
1. **Vérifier ingestion et éligibilité**, puis présence effective dans l'index.
2. **Mesurer leur rappel parmi les candidats**, avant le classement final.
3. **Examiner la dépendance à la popularité** et à l'historique d'interactions.
4. **Tester un chemin par contenu** ou une exposition contrôlée des nouveautés.
5. **Mesurer délai de découverte et satisfaction**, sans sacrifier les contraintes de qualité.

**Piège** : modifier le ranker alors que les documents n'atteignent jamais son entrée.

---

Mise en situation : un recommender propose dix variantes presque identiques du même tutoriel. Quelle correction testes-tu ? <!--anki:6230363266323731313036643465376262343161366438636161383463336231-->
?
1. **Identifier les doublons** et définir la diversité utile : source, difficulté ou sujet.
2. **Conserver la baseline** et mesurer sa pertinence ainsi que sa redondance.
3. **Appliquer un reclassement borné**, avec plafond par famille et exclusions explicites.
4. **Vérifier les segments** où plusieurs variantes restent réellement utiles.
5. **Évaluer la liste complète** sur réussite de tâche, qualité et latence.

**Piège** : maximiser la diversité en proposant des éléments hors sujet.

---

## Sources
- [Google — architecture des systèmes de recommandation](https://developers.google.com/machine-learning/recommendation/overview/types)
- [Google — filtrage collaboratif et feedback](https://developers.google.com/machine-learning/recommendation/collaborative/basics)
- [Covington et al. — Deep Neural Networks for YouTube Recommendations](https://research.google/pubs/deep-neural-networks-for-youtube-recommendations/)
- [Google — reclassement, fraîcheur et diversité](https://developers.google.com/machine-learning/recommendation/dnn/re-ranking)
- [Schnabel et al. — biais de sélection dans la recommandation](https://proceedings.mlr.press/v48/schnabel16.html)
- [Burges — From RankNet to LambdaRank to LambdaMART](https://www.microsoft.com/en-us/research/publication/from-ranknet-to-lambdarank-to-lambdamart-an-overview/)

## Connexions
- [[133-embeddings-representations|Embeddings]] — représentations pour rechercher les candidats
- [[96-evals-rag-agents|Évaluation du retrieval]] — mesurer rappel et ordre des résultats
- [[97-evals-online-ab-testing|A/B testing]] — vérifier la valeur de la liste exposée
- [[178-inference-causale-decisions|Inférence causale]] — distinguer exposition et effet de la recommandation
- [[00-moc-ai-engineering|MOC AI Engineering]]
