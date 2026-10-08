# Explicabilité & diagnostic des modèles — Flashcards
Tags: #flashcards #ai-engineering #ml-classique #explicabilite #shap
Vérifié le : 8 octobre 2026
<!-- summary: explication locale ou globale, importance par permutation, variables corrélées, contributions SHAP, population de référence, log-odds, PDP et ICE, contrefactuels actionnables, justifications générées et fidélité de l'explication. -->


À ne pas confondre : explication locale et explication globale d'un modèle ? <!--anki:3236346461646234333634363465323038633662376664376335303433323061-->
?
Une explication **locale** décrit une prédiction particulière ; une explication **globale** résume le comportement du modèle sur une population. Les variables dominantes en moyenne peuvent ne pas expliquer un cas atypique.

Choisir l'échelle selon la question : diagnostiquer un ticket mal classé ou comprendre la politique générale de routage. Préciser modèle, sortie et population analysés. Agréger des explications locales peut masquer des effets opposés entre segments ; une importance globale ne suffit donc pas à justifier chaque décision individuelle.

---

Que mesure l'importance par permutation d'une variable ? <!--anki:3432346461383838626138373436326338373436336662383962353132656339-->
?
Elle mesure la **dégradation d'un score** quand on mélange une variable dans un jeu donné, en conservant le modèle entraîné. On teste ainsi sa dépendance prédictive à cette information pour la métrique retenue.

Utiliser un jeu tenu à l'écart et répéter les permutations pour mesurer la variabilité. Le résultat dépend du modèle, de la population et du score ; ce n'est pas une propriété absolue de la variable. Permuter peut créer des observations irréalistes, surtout lorsque les variables sont fortement dépendantes.

---

Calcul : quelle importance par permutation si une accuracy passe de 0,84 à 0,79 en moyenne ? <!--anki:6562656232353633336231383461343639653466363031323031336331313966-->
?
Pour un score dont **une valeur élevée est meilleure**, l'importance vaut **0,84 − 0,79 = 0,05**, soit cinq points d'accuracy. Répéter la permutation permet d'examiner sa variabilité.

Avec une perte dont une valeur faible est meilleure, interpréter l'augmentation de perte avec la convention appropriée. Le résultat n'indique pas que la variable cause 5 % des décisions. Il décrit une perturbation particulière du modèle ; une importance négative peut venir du bruit ou d'une dépendance défavorable à la généralisation.

---

Pourquoi deux variables corrélées peuvent-elles avoir une faible importance individuelle ? <!--anki:6166306366623936656532663437303362393761643035613561366131346262-->
?
Elles peuvent fournir une **information substituable** : quand l'une est mélangée, l'autre permet encore de bien prédire. Une faible importance individuelle ne prouve donc pas que le groupe de variables est inutile.

Examiner leurs dépendances, tester une permutation groupée ou comparer des modèles réentraînés sans le groupe. Ces expériences répondent à des questions différentes : dépendance du modèle actuel ou possibilité d'apprendre sans ces données. Elles doivent conserver le protocole de validation ; retirer une variable sur la seule base d'un classement d'importances peut tromper.

---

Que représente une contribution SHAP ? <!--anki:3335653430666264363334303434656138326437633235376333623661376131-->
?
Une contribution **SHAP** attribue à une variable une part de l'écart entre la sortie expliquée et une valeur de référence, dans un jeu de coalitions défini. Sous la propriété d'additivité, référence et contributions reconstituent cette sortie, à l'erreur d'approximation près.

Le résultat dépend de la manière de représenter l'absence d'une variable et des dépendances prises en compte. Il explique le modèle sous ces conventions, pas automatiquement les causes du phénomène réel. Vérifier quelle classe et quelle unité de sortie sont effectivement expliquées.

---

Pourquoi le choix de la population de référence change-t-il une explication SHAP ? <!--anki:3962326137306130336361383462306139643530626233343761613162363139-->
?
La référence précise **par rapport à quoi** la prédiction est expliquée. Comparer une demande au client moyen ou aux demandes du même service change la base et les attributions possibles, même si la prédiction reste identique.

Choisir un ensemble représentatif de la question posée, le versionner et documenter son échantillonnage. Les variables dépendantes demandent une attention particulière au mécanisme de masquage. Une évolution du graphique peut venir d'une nouvelle référence plutôt que d'un changement du modèle ; conserver les deux versions pour comparer.

---

Calcul : des contributions SHAP de +0,8 et +0,4 s'ajoutent à une base de −1 en log-odds ; quelle probabilité obtient-on ? <!--anki:6637363636646338303133393436346661613735356436396562386137613733-->
?
Les contributions s'additionnent d'abord dans **l'espace expliqué**, ici les log-odds :
```text
z = −1 + 0,8 + 0,4 = 0,2
p = 1 / (1 + exp(−0,2)) ≈ 0,5498
```
La probabilité finale est donc environ 55 %. On ne peut pas traiter +0,8 comme une hausse de 80 points de probabilité. Vérifier l'unité annoncée par l'explainer : certaines configurations expliquent une probabilité, d'autres une marge ou une autre transformation de sortie.

---

À ne pas confondre : PDP et courbes ICE ? <!--anki:3565633339626133663835313461366538306264313030633130303766336266-->
?
Un **PDP** moyenne les prédictions obtenues en faisant varier une caractéristique ; les **courbes ICE** montrent ces variations pour chaque observation. La moyenne peut masquer des interactions ou des comportements opposés entre groupes.

Les deux peuvent évaluer des combinaisons irréalistes lorsque les variables sont dépendantes. Examiner les zones où des données existent et compléter par des analyses conditionnelles adaptées. Une courbe montante décrit une réaction du modèle à ces entrées artificielles, pas la preuve qu'une intervention réelle sur la variable augmenterait la cible.

---

Qu'est-ce qui rend une explication contrefactuelle réellement actionnable ? <!--anki:6139353063643962643034313430663939383265333839313630653762626331-->
?
Elle propose un **changement réalisable** des entrées qui modifie la décision du modèle, en respectant variables immuables, dépendances et coût de l'action. Modifier fictivement une date de naissance ou une variable indisponible à l'utilisateur ne fournit pas un recours utile.

Vérifier que le point obtenu est plausible et que la recommandation résiste à de petites variations. Franchir la frontière d'un modèle ne prouve pas une amélioration de la situation réelle. Un conseil d'action demande des hypothèses causales supplémentaires et une validation de son effet.

---

Pourquoi une justification rédigée par un LLM n'est-elle pas une preuve du mécanisme de décision ? <!--anki:3461363763306332646438373433646162653337623239393239303135656663-->
?
Le texte généré est une **sortie supplémentaire**, pas un accès garanti au calcul qui a produit la décision. Un modèle peut donner une justification plausible tout en utilisant d'autres indices ; une explication reconstruite après coup peut aussi être inexacte.

Pour un pipeline, exposer les faits vérifiables : entrées utilisées, règles appliquées, sources et résultat des outils. Tester les affirmations de l'explication contre ces traces. La lisibilité facilite l'usage, mais ne remplace ni fidélité au système ni exactitude de la décision.

---

Comment vérifier qu'une explication de modèle est utile et fidèle ? <!--anki:3933333337656133383132613434643939616332313439343037383630613132-->
?
Tester la **fidélité à la sortie expliquée**, la stabilité dans le contexte pertinent et l'utilité pour la tâche humaine. Une décomposition additive correcte est un contrôle technique ; elle ne garantit ni causalité ni compréhension.

Comparer des perturbations plausibles, des références et des versions. Mesurer si l'explication aide réellement à détecter une erreur ou à choisir une action, plutôt que seulement à convaincre. Des prédictions proches peuvent avoir des raisons différentes ; juger la stabilité selon le comportement attendu, sans imposer une invariance aveugle.

---

## Mises en situation

Mise en situation : deux variables très corrélées ont une importance par permutation presque nulle, et l'équipe veut les supprimer. Que proposes-tu ? <!--anki:3837326264343461346663643466633238323939353534373932633863386536-->
?
1. **Vérifier la qualité du modèle** et le jeu sur lequel l'importance a été calculée.
2. **Examiner la corrélation** et les substitutions possibles entre variables.
3. **Permuter le groupe ensemble** pour mesurer la dépendance du modèle actuel.
4. **Réentraîner sans le groupe** avec validation séparée pour tester la décision de suppression.
5. **Comparer qualité, coût et segments**, puis documenter ce que chaque test montre.

**Piège** : interpréter faible importance individuelle comme absence d'information utile.

---

Mise en situation : le métier lit une contribution SHAP de +0,7 comme « 70 % de risque en plus ». Comment corriges-tu ? <!--anki:3431633238323565336661303438336461613865393037363437333965653834-->
?
1. **Identifier la sortie expliquée**, sa classe, son unité et sa valeur de référence.
2. **Reconstituer la prédiction** avec les contributions et vérifier l'additivité attendue.
3. **Montrer la transformation correcte**, par exemple la sigmoïde des log-odds.
4. **Adapter le libellé de l'interface** et fournir un exemple numérique vérifié.
5. **Rappeler la portée prédictive**, sans présenter la contribution comme un effet causal.

**Piège** : conserver un graphique séduisant dont l'unité est interprétée de travers.

---

Mise en situation : une explication affirme que contacter le support augmente le risque de résiliation, et le produit veut masquer ce bouton. Que réponds-tu ? <!--anki:3134376664316130383566393433636639346536366465383130633962396365-->
?
1. **Distinguer association et intervention** : une difficulté préalable peut causer contact et résiliation.
2. **Auditer la temporalité** des contacts et la population utilisée pour expliquer.
3. **Formuler la question causale** concernant l'accès au support et la rétention.
4. **Choisir un protocole adapté**, avec contraintes utilisateur et mesures de qualité.
5. **Évaluer l'effet réel** avant de transformer une importance prédictive en politique produit.

**Piège** : agir sur le symptôme appris par le modèle en aggravant le problème des utilisateurs.

---

## Sources
- [scikit-learn — importance par permutation et corrélations](https://scikit-learn.org/stable/modules/permutation_importance.html)
- [scikit-learn — PDP et ICE](https://scikit-learn.org/stable/modules/partial_dependence.html)
- [Lundberg & Lee — A Unified Approach to Interpreting Model Predictions](https://arxiv.org/abs/1705.07874)
- [SHAP — lire un waterfall plot et ses unités](https://shap.readthedocs.io/en/latest/example_notebooks/api_examples/plots/waterfall.html)
- [SHAP — limites des interprétations causales d'un modèle prédictif](https://shap.readthedocs.io/en/latest/example_notebooks/overviews/Be%20careful%20when%20interpreting%20predictive%20models%20in%20search%20of%20causal%20insights.html)
- [Karimi et al. — Model-Agnostic Counterfactual Explanations for Consequential Decisions](https://proceedings.mlr.press/v108/karimi20a.html)
- [Turpin et al. — limites de fidélité des justifications générées](https://arxiv.org/abs/2305.04388)

## Connexions
- [[171-choisir-modele-ml|Choisir un modèle]] — distinguer performance et compréhension du comportement
- [[156-ia-responsable|IA responsable]] — analyser les effets et les limites d'une explication
- [[178-inference-causale-decisions|Inférence causale]] — valider les effets des actions proposées
- [[00-moc-ai-engineering|MOC AI Engineering]]
