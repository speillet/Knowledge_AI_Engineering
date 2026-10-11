# Calibration, incertitude & abstention — Flashcards
Tags: #flashcards #ai-engineering #ml-classique #calibration #incertitude
<!-- summary: discrimination et calibration, Brier score, calibrateur séparé, temperature scaling, incertitudes, risque-couverture, prédiction conforme, coût de décision avec revue et erreurs humaines. -->


À ne pas confondre : discrimination et calibration d'un classifieur ? <!--anki:6337616261653836306433623432636261323934336534393832663635306633-->
?
La **discrimination** est la capacité à classer les positifs devant les négatifs. La **calibration** relie les probabilités annoncées aux fréquences observées : parmi les cas annoncés à 80 %, environ 80 % devraient être positifs.

Un score peut très bien ordonner les cas tout en étant trop confiant. Pour choisir un seuil selon un coût attendu, contrôler les probabilités en plus du classement. Une bonne calibration globale ne garantit pas celle de chaque population ni un classement utile.

---

Comment lire une courbe de fiabilité sans se laisser tromper ? <!--anki:6537616439316332303635323462366138313632616134393832356135363733-->
?
Regrouper les prédictions par plage de probabilité et comparer, dans chaque groupe, la probabilité moyenne à la fréquence des positifs. Afficher aussi les **effectifs** : un groupe de cinq cas ne permet pas la même conclusion qu'un groupe de cinq mille.

Les résultats dépendent du découpage des plages. Examiner les segments importants et l'incertitude plutôt qu'un unique écart agrégé. Une courbe proche de la diagonale sur le jeu utilisé pour ajuster le calibrateur ne constitue pas une validation indépendante.

---

Calcul : quel Brier score pour les probabilités 0,9 et 0,6 avec les labels 1 et 0 ? <!--anki:3539313833653139336136323465656139663462653436333530346338333634-->
?
Pour une classification binaire, le **Brier score** est la moyenne des erreurs quadratiques entre probabilités et labels :
```text
Brier = ((0,9 − 1)² + (0,6 − 0)²) / 2 = 0,185
```
Plus bas est meilleur. Cette définition binaire compte une seule probabilité par observation ; d'autres conventions somment les classes. Le score reflète plusieurs propriétés, dont discrimination et calibration : une baisse ne prouve pas à elle seule que la calibration s'améliore. Deux observations ne permettent pas d'estimer la fiabilité réelle du modèle.

---

Pourquoi séparer les données d'ajustement du modèle et du calibrateur ? <!--anki:6537646631316564303466373464363762396166376665316463393361386363-->
?
Les prédictions sur les données d'entraînement sont souvent trop optimistes. Ajuster le **calibrateur** sur ces mêmes prédictions lui apprend une relation qui ne représentera pas les nouveaux cas.

Utiliser des prédictions sur un jeu tenu à l'écart ou des prédictions obtenues hors fold, en respectant groupes et temps. Réserver encore des données indépendantes pour évaluer la chaîne finale et son seuil. Le calibrateur fait partie du système appris : il possède une version, une population cible et un risque de surapprentissage.

---

Que change le temperature scaling d'un classifieur ? <!--anki:6233346231373066623439613461613038643839633764366364383064326636-->
?
Il ajuste un paramètre positif **T** sur des données de calibration, puis calcule `softmax(logits / T)`. Pour T supérieur à 1, la distribution s'aplatit ; pour T inférieur à 1, elle devient plus concentrée.

L'ordre des classes d'un exemple reste inchangé, donc sa classe prédite par argmax aussi. La calibration peut s'améliorer sans modifier l'accuracy. Cette température apprise poursuit un objectif de calibration ; elle ne garantit pas que la température de sampling d'un LLM mesure la véracité d'une réponse.

---

À ne pas confondre : incertitude aléatoire et incertitude épistémique ? <!--anki:6133313136323161663935363433316239626639383238343136373838313864-->
?
L'**incertitude aléatoire** vient de la variabilité de la cible à information donnée ; l'**incertitude épistémique** vient de ce que le modèle connaît mal. Un texte ambigu et une langue absente de l'entraînement illustrent deux causes différentes d'erreur.

Des données informatives supplémentaires peuvent réduire la seconde. La première peut diminuer si de nouvelles variables rendent la situation moins ambiguë, mais pas par la seule répétition du même entraînement. Les séparer empiriquement reste difficile : un score de confiance ne dit pas automatiquement quelle cause domine.

---

Pourquoi une forte probabilité de token ne garantit-elle pas une réponse factuelle correcte ? <!--anki:3237303265336532363264333437326561313234613763326434303661663438-->
?
La probabilité d'un **token** est conditionnelle au contexte et aux tokens précédents. Elle mesure la préférence du modèle pour une continuation, pas directement la véracité d'une proposition complète. Une phrase fausse mais habituelle peut avoir une forte probabilité.

Définir l'événement à prédire, par exemple « le montant extrait est correct », puis valider un score sur des exemples labellisés de cette tâche. Une transformation des logprobs ne devient pas une probabilité de correction sans cette validation et un suivi de la distribution.

---

Comment lire une courbe risque-couverture pour un système qui s'abstient ? <!--anki:3032646536383561303331333462323539333834623334623533346631633639-->
?
La **couverture** est la fraction des cas traités automatiquement ; le **risque sélectif** mesure les erreurs parmi ces cas acceptés. Faire varier le seuil révèle le coût en couverture d'une réduction du risque.

Comparer les systèmes à couverture comparable et examiner qui est exclu : un bon résultat global peut cacher l'abandon d'une langue ou d'un client. Suivre aussi les erreurs et délais de la revue humaine. Un système qui s'abstient toujours ne rend pas le service attendu, même si aucune réponse automatique n'est fausse.

---

Calcul : sur 1 000 demandes, 600 réponses automatiques contiennent 18 erreurs ; les 400 abstentions sont revues en trois minutes chacune. Quelle précision automatique et quelle charge humaine ? <!--anki:6339663738303634353834323431646561343636323238396335626639653264-->
?
La **couverture automatique** vaut 600 / 1 000 = 60 %. La précision parmi les réponses vaut 582 / 600 = **97 %**. Si toutes les abstentions sont revues, 400 demandes arrivent aux humains.

Avec trois minutes par revue, cela représente **20 heures** de travail, hors reprise des erreurs automatiques. Rapporter ensemble qualité, volume et capacité. Les 1,8 % d'erreurs automatiques sur l'ensemble des demandes ne signifient pas 98,2 % de résolution correcte : le résultat des 400 revues reste à mesurer.

---

Que garantit la prédiction conforme dans son cadre standard ? <!--anki:3537356636366530336566643464363561623933396432343630333338666361-->
?
Elle construit des **ensembles de classes ou intervalles** à partir d'un modèle et de scores sur un jeu de calibration. Sous les hypothèses requises, notamment l'échangeabilité des exemples de calibration et du nouveau cas, elle vise une couverture marginale d'au moins **1 − α**.

Une couverture de 90 % ne signifie ni 90 % de certitude pour chaque cas ni 90 % dans chaque sous-groupe. Mesurer aussi la taille des ensembles : inclure presque toutes les réponses peut assurer la couverture sans permettre une décision utile.

---

Pourquoi la calibration peut-elle se dégrader quand la prévalence change ? <!--anki:3961643434323038303063653434346338303235643261636133653336323066-->
?
Une probabilité apprise reflète la **population d'origine**. Si la fréquence des positifs change, la relation entre score et fréquence réelle peut changer aussi, même avec un classement encore utile.

Contrôler les fréquences et erreurs dès que les labels arrivent, par segment. Une correction de prior suppose notamment une forme de stabilité des distributions conditionnelles par classe ; elle ne corrige pas toute dérive. Une dégradation doit donc déclencher un diagnostic avant une recalibration automatique, puis une évaluation indépendante sur la population cible.

---

Comment choisir entre prédiction positive, négative et revue humaine à partir d'une probabilité calibrée ? <!--anki:3133323763373130306434663437333761326135323634653538303663323932-->
?
Comparer les **coûts attendus** des trois décisions. Avec probabilité positive `p`, coûts constants des erreurs et décisions correctes gratuites :
```text
positif : (1 − p) × C_FP
négatif : p × C_FN
revue : C_revue + coût attendu des erreurs restantes
```
Choisir le minimum sous les contraintes de qualité et capacité. Si la revue est supposée parfaite, son coût se réduit à `C_revue` ; c'est une hypothèse à vérifier. Des délais, capacités limitées et coûts variables peuvent changer la politique. Une probabilité mal calibrée fausse l'arbitrage.

---

Calcul : p = 0,10 est supposé calibré ; un faux positif coûte 4 unités, un faux négatif 36, et une revue parfaite coûte 1. Les décisions correctes sont gratuites et la capacité de revue est suffisante. Quelle décision minimise le coût attendu ? <!--anki:3236303436626565656462313461663461656439663431366335393530666363-->
?
Comparer les trois coûts :
```text
prédire positif : (1 − 0,10) × 4 = 3,6
prédire négatif : 0,10 × 36 = 3,6
revue parfaite : 1
```
**Revoir** minimise le coût attendu sous ces hypothèses. Sans revue, positif et négatif sont à égalité ; le seuil binaire vaut 4/(4+36) = 0,10. Ajouter le coût des erreurs humaines et du délai avant d'appliquer cette règle au réel. Le meilleur choix individuel peut devenir impossible si la file de revue sature.

---

À ne pas confondre : couverture conforme et couverture d'automatisation ? <!--anki:6230396632636661386366613437323438656166333638343762346139643533-->
?
La **couverture conforme** mesure la fréquence à laquelle un ensemble ou intervalle prédictif contient la vraie cible, sous le cadre considéré. La **couverture d'automatisation** mesure la fraction des demandes traitées sans abstention.

Un ensemble conforme contenant plusieurs classes peut couvrir la cible sans permettre une décision automatique. À l'inverse, un système répondant à toutes les demandes a 100 % d'automatisation, même s'il se trompe souvent. Rapporter ensemble couverture prédictive, taille des ensembles, risque des décisions et charge humaine : le même mot « couverture » désigne ici des événements différents.

---

Pourquoi une revue humaine ne permet-elle pas de supposer toutes les abstentions correctement résolues ? <!--anki:3762363637393136663064613465623562303431663333626136663139326237-->
?
La revue est **une étape du système**, avec ses propres erreurs, délais et abandons. Son lot est souvent plus difficile que les cas automatisés ; une accuracy humaine mesurée sur un autre lot ne s'y transfère pas automatiquement.

Sur un même ensemble de demandes, compter séparément erreurs automatiques, erreurs après revue et demandes non résolues. Définir une échéance et mesurer le délai de résolution. Une baisse des erreurs automatiques peut coïncider avec une hausse des erreurs globales si la revue est saturée. Valider le parcours complet, pas seulement le modèle.

---

## Mises en situation

Mise en situation : un classifieur annonce 95 % de confiance mais se trompe sur un cas sur quatre dans cette tranche. Que changes-tu ? <!--anki:6234383262333736643935613465303538336135323536366232333930313163-->
?
1. **Vérifier l'événement prédit** et la qualité des labels de cette tranche.
2. **Mesurer les effectifs** et l'écart par population, avec son incertitude.
3. **Ajuster un calibrateur** sur des prédictions indépendantes de l'entraînement du modèle.
4. **Rechoisir le seuil** selon coûts et capacité de revue, sur validation.
5. **Évaluer la chaîne figée** sur un test indépendant avant d'afficher une nouvelle confiance.

**Piège** : remplacer 95 % par un score visuel sans changer la décision ni mesurer sa fiabilité.

---

Mise en situation : l'abstention réduit les erreurs à 1 %, mais triple la file de revue humaine. Comment arbitres-tu ? <!--anki:3164386166303834373161633434613239386365313230666339653835363563-->
?
1. **Préciser le dénominateur** du 1 % : cas acceptés ou demandes totales.
2. **Tracer risque et couverture**, avec volumes par segment.
3. **Mesurer la capacité humaine**, le délai et les erreurs de revue.
4. **Comparer plusieurs seuils** selon coût total et contraintes de qualité.
5. **Tester le parcours complet**, y compris ce qui arrive aux demandes en attente.

**Piège** : présenter l'amélioration du seul sous-ensemble automatique comme celle du service entier.

---

Mise en situation : un intervalle conforme calibré sur les clients historiques couvre mal les nouveaux clients. Que conclus-tu ? <!--anki:6238643963653161346665663466376362663939313331303536306531343437-->
?
1. **Vérifier la mesure** : taille du groupe et définition de la couverture.
2. **Examiner le changement de distribution** et la dépendance entre observations d'un client.
3. **Rappeler la garantie marginale**, qui ne promet pas une couverture par client.
4. **Collecter une calibration représentative** ou étudier une méthode adaptée aux hypothèses réelles.
5. **Prévoir un repli** pour les groupes insuffisamment validés, puis mesurer largeur et couverture.

**Piège** : invoquer le mot « conforme » comme une garantie universelle malgré un changement de population.

---

## Sources
- [scikit-learn — calibration des probabilités](https://scikit-learn.org/stable/modules/calibration.html)
- [Guo et al. — On Calibration of Modern Neural Networks](https://proceedings.mlr.press/v70/guo17a.html)
- [Geifman & El-Yaniv — Selective Classification for Deep Neural Networks](https://proceedings.neurips.cc/paper/2017/hash/4a8423d5e91fda00bb7e46540e2b0cf1-Abstract.html)
- [Angelopoulos & Bates — introduction à la prédiction conforme](https://arxiv.org/abs/2107.07511)

- [Kendall & Gal — incertitudes aléatoire et épistémique](https://arxiv.org/abs/1703.04977)
- [Lipton et al. — hypothèses et correction du label shift](https://proceedings.mlr.press/v80/lipton18a.html)

## Connexions
- [[172-validation-metriques-ml|Validation ML]] — probabilités et seuils métier
- [[143-hallucinations-grounding|Hallucinations & abstention]] — ne pas confondre confiance et véracité
- [[113-monitoring-drift-feedback|Monitoring & drift]] — surveiller la validité des probabilités
- [[00-moc-ai-engineering|MOC AI Engineering]]
