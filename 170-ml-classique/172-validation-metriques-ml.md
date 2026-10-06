# ML classique : validation, fuites & métriques — Flashcards
Tags: #flashcards #ai-engineering #ml-classique #validation #metriques
<!-- summary: train-validation-test, fuite de données, validation croisée et imbriquée, groupes et temps, pipelines, précision et rappel, classes rares, ROC et PR, seuil métier, MAE et RMSE, suréchantillonnage et incertitude. -->


À ne pas confondre : entraînement, validation et test final en ML supervisé ? <!--anki:6663653365326138306266653464653739373832333133616230333730393964-->
?
Le **train** sert à apprendre les paramètres et transformations. La **validation** sert à choisir modèle, hyperparamètres et seuil. Le **test final**, tenu à l'écart de ces décisions, estime la qualité du système retenu.

Regarder le test après chaque essai en fait progressivement un jeu de validation. Documenter les décisions et réserver un test indépendant pour la conclusion. Après cette mesure, un éventuel réentraînement sur davantage de données crée un autre artefact : préciser ce qui a effectivement été évalué puis déployé.

---

Quelles formes de fuite de données peuvent rendre une évaluation ML trompeuse ? <!--anki:6539316435373633373665653463353461386435376536363636663864346434-->
?
Une fuite introduit de l'**information inaccessible dans les conditions réelles de prédiction**. Cela inclut une variable produite après l'issue, des copies d'un même exemple des deux côtés du split ou un prétraitement ajusté à partir du test.

Pour un score calculé à l'ouverture d'un ticket, son équipe finale et son délai de clôture sont suspects. Auditer la disponibilité de chaque variable, pas seulement son nom. Un score exceptionnel doit déclencher une vérification du protocole avant d'être présenté comme une avancée du modèle.

---

Quand utiliser une validation croisée plutôt qu'un unique split ? <!--anki:3336663630323466306532343465666262383761386433336663333663613365-->
?
Lorsque les données sont limitées et que plusieurs découpages plausibles aideraient à comparer les modèles. En **k-fold**, on entraîne sur k−1 parties et on évalue sur la partie restante, en répétant pour chaque partie.

Le découpage doit représenter le déploiement : des folds aléatoires ne conviennent pas automatiquement aux groupes ou au temps. Refaire prétraitement et sélection de variables dans chaque train de fold. Les scores des folds ne sont pas indépendants, car leurs ensembles d'entraînement se recouvrent ; leur dispersion n'est pas un intervalle de confiance universel.

---

Quand faut-il séparer les données par groupe plutôt que par ligne ? <!--anki:6165343635636164623837383434323638373165356565376534663736396237-->
?
Lorsque plusieurs lignes partagent une **entité ou une source** dont le modèle pourrait reconnaître les particularités : patient, client, document ou machine. Si l'objectif est de généraliser à de nouvelles entités, leurs lignes ne doivent pas être présentes simultanément dans le train et le test.

Définir le groupe selon le risque de dépendance réel. Si le service prédit le futur de clients déjà connus, un split temporel peut être plus approprié. La question est de reproduire le type de nouveauté rencontré en production, pas d'appliquer toujours le même split.

---

Comment valider un modèle qui prédit des événements futurs ? <!--anki:6339643833353038363830353461663938653632316366376632646465333565-->
?
Entraîner sur le **passé** et évaluer sur une période ultérieure, éventuellement avec plusieurs fenêtres successives. Respecter l'instant où les variables et les labels deviennent disponibles ; les labels d'un horizon futur ne doivent pas déborder artificiellement dans une simulation d'entraînement passée.

Un intervalle d'exclusion peut être nécessaire autour de la frontière si les fenêtres ou labels se chevauchent. Mesurer plusieurs périodes révèle saisonnalité et dérive. Mélanger aléatoirement des lignes temporelles peut donner au modèle des informations indirectes sur le futur qu'il n'aurait jamais possédées.

---

Pourquoi apprendre imputation et sélection de variables à l'intérieur de chaque fold ? <!--anki:3134653034613435396164373437323338386338363838616232656531313466-->
?
Ces opérations **apprennent elles aussi à partir des données**. Une sélection guidée par tous les labels transmet de l'information du fold de validation au modèle, même si son entraînement proprement dit n'utilise que le train.

Une pipeline regroupe les transformations et l'estimateur : chaque fold ajuste la chaîne sur son train, puis transforme sa validation avec les paramètres obtenus. Cette protection ne détecte pas une variable déjà contaminée en amont. L'audit de provenance et de disponibilité reste nécessaire, même avec une pipeline correctement construite.

---

Pourquoi une recherche massive d'hyperparamètres peut-elle surapprendre la validation ? <!--anki:6239363966616361353933333437303638366561666538666435666537313438-->
?
Choisir le meilleur parmi beaucoup d'essais sélectionne aussi des **fluctuations favorables du score**. Le résultat gagnant surestime alors sa qualité future, même sans fuite directe dans l'entraînement.

Limiter le budget, conserver un test final indépendant et documenter les essais. Une validation croisée imbriquée sépare sélection interne et estimation externe de la procédure de sélection. Elle coûte davantage de calcul et ne remplace pas un découpage pertinent par groupe ou période. Multiplier les essais sur un mauvais protocole ne rend pas sa conclusion fiable.

---

Calcul : quelle précision et quel rappel pour 80 vrais positifs, 120 faux positifs et 20 faux négatifs ? <!--anki:6235333335326366616131623438643662303137373036623638303532613364-->
?
La **précision** mesure la part des alertes qui sont correctes ; le **rappel** mesure la part des positifs réels retrouvés.
```text
précision = VP / (VP + FP) = 80 / 200 = 40 %
rappel   = VP / (VP + FN) = 80 / 100 = 80 %
```
Le système retrouve une grande partie des cas recherchés, mais impose 120 fausses alertes pour 80 utiles. Examiner la capacité de revue et le coût des erreurs. Sans vrais négatifs, on ne peut pas déduire l'accuracy ni le taux de faux positifs.

---

Pourquoi l'accuracy peut-elle masquer l'échec sur une classe rare ? <!--anki:3161643734653036343333333433356661633763636537323035373233376131-->
?
Si seulement **1 % des exemples sont positifs**, prédire toujours « négatif » donne 99 % d'accuracy et zéro rappel sur la classe utile. La moyenne récompense alors une solution inutilisable.

Examiner la matrice de confusion, précision et rappel de la classe cible, puis les volumes d'erreurs. En multiclasses, une moyenne macro donne un poids égal aux classes, tandis qu'une moyenne pondérée reflète leur fréquence. Aucun agrégat ne remplace les contraintes métier : dix erreurs critiques peuvent compter plus que mille erreurs bénignes.

---

À ne pas confondre : courbe ROC et courbe précision-rappel ? <!--anki:6430393537653937316432313433356239316434653837663131373039303064-->
?
La **ROC** relie rappel et taux de faux positifs ; la courbe **précision-rappel** relie rappel et qualité des alertes. Quand les positifs sont rares, une petite proportion de faux positifs peut représenter beaucoup d'alertes inutiles.

Examiner la zone de fonctionnement réellement acceptable plutôt qu'une aire globale seule. La précision dépend de la prévalence : comparer des jeux artificiellement rééquilibrés peut tromper. Préciser le résumé utilisé ; l'average precision et l'aire trapézoïdale sous la courbe PR ne sont pas exactement le même calcul.

---

Pourquoi le F1-score ne suffit-il pas toujours pour choisir un classifieur ? <!--anki:3831393033316131613166373435396438393533636563343037303032363961-->
?
Le **F1** est une moyenne harmonique de précision et rappel. Il favorise leur équilibre, mais ignore les vrais négatifs et ne représente pas directement un coût métier ou une limite de capacité opérationnelle.

Deux systèmes de même F1 peuvent générer des volumes d'alertes différents. Si une équipe ne peut traiter que 100 cas par jour, mesurer la précision et le rappel à cette capacité est plus concret. Pour un usage critique, ajouter des contraintes par segment plutôt que maximiser uniquement une moyenne.

---

Comment choisir le seuil d'un classifieur selon le coût des erreurs ? <!--anki:3135633064323666323465383439343139643933613735373831333336633537-->
?
Choisir le seuil sur **validation**, en tenant compte des faux positifs, faux négatifs et capacités de traitement. Sous l'hypothèse de probabilités calibrées, de coûts constants et d'un coût nul pour les décisions correctes :
```text
prédire positif si p > C_FP / (C_FP + C_FN)
```
Avec un faux positif à 5 unités et un faux négatif à 95, le seuil théorique est 0,05. Vérifier calibration et résultat métier, puis figer le seuil avant le test final. Un score de classement arbitraire n'est pas une probabilité.

---

À ne pas confondre : MAE et RMSE pour une régression ? <!--anki:6231663061663632383331383465633138663637316237303362306363666533-->
?
La **MAE** moyenne les valeurs absolues des erreurs ; la **RMSE** prend la racine de leur carré moyen et pénalise davantage les grandes erreurs. Toutes deux s'expriment dans l'unité de la cible.

Pour des erreurs de 0 et 10 jours, MAE = 5 jours et RMSE ≈ 7,07 jours. Choisir selon le coût des écarts et examiner leur distribution. Si sous-estimer coûte beaucoup plus que surestimer, une perte symétrique peut manquer l'objectif ; une approche quantile peut mieux représenter le besoin.

---

Où appliquer le suréchantillonnage d'une classe rare ? <!--anki:3831383037313138363733653465343361383962303662613939373334396234-->
?
Uniquement sur le **train de chaque split ou fold**, après sa séparation. Suréchantillonner avant le découpage peut placer des copies ou des exemples synthétiques très proches dans la validation et gonfler les scores.

Conserver une validation et un test représentatifs de l'usage réel pour évaluer les alertes. Comparer suréchantillonnage, pondération des classes et réglage du seuil : leurs effets diffèrent. Modifier les proportions à l'entraînement peut aussi affecter les probabilités ; leur calibration sur la distribution cible doit être vérifiée séparément.

---

Comment comparer deux modèles dont les scores sont très proches ? <!--anki:3064346565646231653831383461396362336438383638373362646530373662-->
?
Utiliser les **mêmes observations**, examiner les différences d'erreurs et quantifier l'incertitude avec une méthode adaptée au plan d'échantillonnage. Un bootstrap apparié peut rééchantillonner les mêmes unités pour les deux modèles ; si les observations sont groupées, rééchantillonner les groupes plutôt que prétendre que chaque ligne est indépendante.

Rapporter l'amplitude du gain, les segments et les coûts, pas seulement une significativité. Sur une série temporelle, préserver les dépendances demande un protocole spécifique. Un score supérieur de quelques centièmes ne constitue pas seul une preuve d'amélioration exploitable.

---

## Mises en situation

Mise en situation : ton classifieur de documents atteint 98 % sur un split aléatoire mais échoue chez de nouveaux clients. Que vérifies-tu ? <!--anki:6332393032336432653936623461356261323834363962633030343933643733-->
?
1. **Rechercher les dépendances** : modèles de documents, clients et versions presque identiques entre train et test.
2. **Définir la généralisation visée** : nouveaux clients, nouvelles périodes ou nouveaux formats.
3. **Reconstruire le split** par groupe approprié et dédupliquer avant de mesurer.
4. **Réapprendre le prétraitement** uniquement sur chaque train et comparer une baseline.
5. **Analyser les erreurs** par client et format avant de décider d'ajouter des données ou de changer de modèle.

**Piège** : augmenter la taille du modèle pour résoudre une fuite dans le protocole d'évaluation.

---

Mise en situation : un détecteur annonce 99 % d'accuracy, mais les opérateurs jugent presque toutes ses alertes inutiles. Comment évalues-tu le problème ? <!--anki:3531303639363534383862663433633762313637316364323531383261643236-->
?
1. **Mesurer la prévalence** et comparer au prédicteur toujours négatif.
2. **Compter VP, FP et FN**, sur une période avec labels suffisamment arrivés.
3. **Calculer précision et rappel** au seuil actuel, ainsi que le volume quotidien d'alertes.
4. **Tester d'autres seuils** sur validation selon capacité et coûts d'erreur.
5. **Vérifier les segments** et mesurer le seuil retenu sur un test indépendant.

**Piège** : rééquilibrer le test à 50/50 puis annoncer cette précision comme celle de production.

---

Mise en situation : après 200 essais, le meilleur modèle gagne un point sur validation mais perd sur le test final. Que conclus-tu ? <!--anki:3139666465653964633637643431623962666133316264333435376236346165-->
?
1. **Vérifier la comparabilité** des populations, périodes et traitements entre les jeux.
2. **Considérer le biais de sélection** : le gagnant peut avoir bénéficié du bruit de validation.
3. **Rapporter aussi le résultat négatif** au lieu de choisir un nouveau modèle grâce au test.
4. **Revoir la procédure** : budget d'essais, validation imbriquée si adaptée, nouvelles données indépendantes pour confirmer.
5. **Conserver une baseline robuste** tant que le gain n'est pas confirmé.

**Piège** : réutiliser le test jusqu'à ce qu'il confirme l'histoire attendue.

---

## Sources
- [scikit-learn — pièges et fuites de données](https://scikit-learn.org/stable/common_pitfalls.html)
- [scikit-learn — validation croisée](https://scikit-learn.org/stable/modules/cross_validation.html)
- [scikit-learn — métriques](https://scikit-learn.org/stable/modules/model_evaluation.html)
- [scikit-learn — choix du seuil de décision](https://scikit-learn.org/stable/modules/classification_threshold.html)

## Connexions
- [[171-choisir-modele-ml|Choisir un modèle ML]] — comparer les baselines et familles de modèles
- [[94-evals-methodologie|Méthodologie d'évaluation]] — prolonger les principes d'indépendance des jeux
- [[151-donnees-curation-annotation|Curation & annotation]] — qualité des labels et doublons
- [[00-moc-ai-engineering|MOC AI Engineering]]
