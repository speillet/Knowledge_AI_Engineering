# Inférence causale & décisions produit — Flashcards
Tags: #flashcards #ai-engineering #ml-classique #causalite #experimentation
<!-- summary: prédiction ou intervention, ATE et CATE, graphe causal, confusion et collision, identification ou estimation, hypothèses, positivité, score de propension, différences de différences, uplift et analyses de sensibilité. -->


Pourquoi prédire qui résiliera ne suffit-il pas à choisir qui aider ? <!--anki:3631623936393761336133623439396662323464393830633136303130383630-->
?
Un score de résiliation prédit une **issue sous les conditions observées**. Pour décider d'une action, il faut aussi savoir qui changera de comportement grâce à cette action. Un utilisateur à très haut risque peut partir même après intervention ; un autre peut rester sans aide.

Définir l'intervention, son coût et l'issue recherchée. Un modèle d'effet hétérogène cherche une variation due à l'action, sous des hypothèses causales explicites. Le meilleur classement du risque n'est donc pas nécessairement le meilleur classement des bénéfices d'une politique d'aide.

---

À ne pas confondre : ATE et CATE en inférence causale ? <!--anki:3139653434363639333361313439363562343430393065346665336635306263-->
?
L'**ATE** est l'effet moyen d'un traitement sur une population définie : `E[Y(1) − Y(0)]`. Le **CATE** conditionne cet effet à des caractéristiques : `E[Y(1) − Y(0) | X=x]`.

Pour une même personne, on n'observe généralement qu'une des deux issues potentielles. Le CATE n'est donc pas une mesure directe de son effet individuel. Préciser population, intervention et horizon ; un effet moyen positif peut masquer des segments peu aidés ou lésés. Leur estimation nécessite données suffisantes et validation indépendante.

---

À quoi sert un graphe causal avant de choisir les variables d'ajustement ? <!--anki:6464643931623734623766393434666262653865396366616331336531366238-->
?
Un **graphe orienté acyclique** explicite les hypothèses sur les causes et leur ordre. Un facteur commun peut influencer à la fois intervention et résultat : la difficulté d'un dossier influence l'attribution d'une aide et sa durée de traitement.

Chercher un ajustement qui bloque les chemins de confusion pertinents selon ce graphe. Ajouter toutes les variables n'est pas une règle valide : contrôler un médiateur peut retirer une partie de l'effet total recherché. Le graphe formalise des hypothèses métier ; il n'est pas une vérité déduite automatiquement des corrélations.

---

Qu'est-ce qu'un biais de collision dans une analyse causale ? <!--anki:6364376432626132653264663464316462643930333164613238613738663961-->
?
Un **collider** est un effet commun de deux variables, par exemple `usage_assistant → ticket_ouvert ← difficulté`. Conditionner sur cette variable peut créer une association artificielle entre ses causes, même si elles étaient indépendantes initialement.

Analyser seulement les tickets ouverts peut ainsi comparer des difficultés différentes selon l'usage de l'assistant. Identifier les filtres de sélection dans le graphe avant d'ajuster. La correction dépend du mécanisme causal et de l'effet recherché ; un filtre pratique de tableau de bord peut changer la validité de toute l'analyse.

---

À ne pas confondre : identification et estimation d'un effet causal ? <!--anki:6131313437353335303130313461373461323539373639666261656435386331-->
?
L'**identification** détermine si l'effet recherché peut s'exprimer à partir des observations sous les hypothèses retenues. L'**estimation** calcule ensuite une valeur et son incertitude avec des données finies et une méthode statistique.

Un modèle prédictif très flexible peut améliorer certaines estimations, mais ne corrige pas l'absence d'identification. Si un facteur commun non mesuré biaise la comparaison, davantage de lignes ne suffit pas forcément. Documenter d'abord les hypothèses permettant l'effet, puis le protocole de calcul, les diagnostics et les limites de l'estimation.

---

Quelles hypothèses rendent interprétable un ajustement causal sur des données observationnelles ? <!--anki:3037616464303166666237313434356138633630393063363766346539666563-->
?
Pour un ajustement standard, préciser notamment **échangeabilité conditionnelle**, **positivité** et **cohérence du traitement** : pas de confusion non mesurée après ajustement, alternatives possibles dans les groupes comparés, et intervention suffisamment définie pour relier issue observée et issue potentielle.

Le cadre habituel demande aussi de traiter l'interférence entre unités : aider un membre peut modifier le résultat de son équipe. Ces hypothèses ne sont pas garanties par une bibliothèque. Les connaissances métier, le plan de collecte et les analyses de sensibilité déterminent la crédibilité de la conclusion.

---

Pourquoi l'absence de recouvrement empêche-t-elle certaines comparaisons causales ? <!--anki:6563306633353161373337633466383361393564633737663738636461646438-->
?
Si tous les dossiers difficiles reçoivent l'aide et aucun dossier comparable ne reste sans aide, il manque une **alternative observée dans ce segment**. Une régression peut extrapoler une différence, sans que les données seules la rendent crédible.

Examiner les distributions de caractéristiques et de propension. Restreindre la population à une zone de recouvrement peut être utile, mais change l'effet ciblé. Sinon, une collecte ou une expérimentation adaptée est nécessaire. Des poids extrêmes sont un symptôme à diagnostiquer, pas seulement un problème numérique à cacher.

---

Que représente un score de propension et à quoi sert-il ? <!--anki:3435656636636334343831343462363138626630333161643064393130313165-->
?
Le **score de propension** est la probabilité de recevoir le traitement conditionnellement aux variables retenues : `e(X)=P(T=1|X)`. Il décrit l'attribution de l'action, pas le risque de l'issue.

Appariement ou pondération peuvent l'utiliser pour équilibrer des caractéristiques observées. Pour une pondération ATE classique, les traités reçoivent `1/e(X)` et les non-traités `1/(1−e(X))`. Contrôler équilibre et poids extrêmes. Un bon prédicteur d'attribution ne prouve ni l'absence de confusion non mesurée ni la validité de l'effet causal.

---

Calcul : quel effet en différences de différences si le groupe équipé passe de 50 à 65 et le contrôle de 40 à 48 ? <!--anki:6230303962663832613734353464656439333832383665333266626163616262-->
?
L'estimation est **(65 − 50) − (48 − 40) = 7 unités**. Elle retire à l'évolution du groupe équipé celle observée chez le contrôle.

L'interprétation causale demande notamment que, sans traitement, les tendances auraient été parallèles, avec absence d'anticipation et de choc différentiel pertinent. Des tendances préalables compatibles soutiennent cette hypothèse sans la prouver. Plusieurs dates d'adoption ou des effets hétérogènes demandent une méthode adaptée ; ce calcul simple ne valide pas tout déploiement progressif.

---

Calcul : quel gain net attendu pour une aide coûtant 2 unités et augmentant de 3 points une issue valant 100 unités ? <!--anki:6533313463343133666164653437633239646339383732626163623137396132-->
?
Sous un effet causal correctement estimé et une valeur linéaire, le gain net attendu par personne aidée est **0,03 × 100 − 2 = 1 unité**. La décision doit intégrer l'incertitude de cet effet et les autres contraintes.

Si un autre segment ne gagne qu'un point, le gain attendu devient −1 unité. Une politique d'**uplift** cible l'effet incrémental utile, pas uniquement la probabilité brute de succès. Évaluer la politique complète sur des données indépendantes avec support suffisant et contrôle des effets indésirables.

---

Pourquoi des tests de réfutation réussis ne prouvent-ils pas une conclusion causale ? <!--anki:6563653334313566386630303430643862663861356166666438623762363364-->
?
Placebos, contrôles négatifs ou analyses de sensibilité peuvent révéler une **fragilité** du protocole. Leur réussite montre seulement que les vérifications retenues n'ont pas détecté de problème ; une hypothèse non testable peut rester fausse.

Choisir des contrôles ayant un sens dans le domaine et mesurer l'ampleur d'une confusion non observée nécessaire pour inverser la décision. Rapporter estimations, incertitude et hypothèses résiduelles. Une petite p-valeur ou une série de diagnostics verts ne transforme pas une observation en expérience randomisée.

---

## Mises en situation

Mise en situation : les utilisateurs de l'assistant ferment leurs tickets plus vite, mais ce sont surtout les équipes expérimentées. Comment évalues-tu l'effet ? <!--anki:6532626231303561636330303466323062393935396463616166366533343361-->
?
1. **Définir l'intervention et l'issue**, avec population et délai de mesure.
2. **Représenter les causes plausibles**, dont expérience et difficulté des tickets.
3. **Privilégier une assignation randomisée adaptée** si elle est réalisable.
4. **Sinon, expliciter l'identification**, vérifier recouvrement et variables antérieures à l'usage.
5. **Rapporter sensibilité et limites**, sans attribuer tout l'écart observé à l'assistant.

**Piège** : ajuster avec la satisfaction mesurée après usage sans définir quel effet cela permet d'estimer.

---

Mise en situation : tous les dossiers complexes reçoivent automatiquement une aide et aucun autre dossier ne la reçoit. Peut-on estimer son effet partout ? <!--anki:3933666339646137653866353463383961363934343165336631393432663233-->
?
1. **Vérifier la règle d'attribution** et le support réel dans chaque segment.
2. **Signaler la violation de positivité** pour une comparaison par ajustement standard.
3. **Identifier une population comparable** si elle existe et préciser la nouvelle cible.
4. **Étudier un plan de collecte ou un autre design**, avec hypothèses explicites.
5. **Distinguer extrapolation et preuve**, en limitant la portée des recommandations.

**Piège** : ajouter un modèle plus complexe pour fabriquer l'information manquante.

---

Mise en situation : une différence de différences attribue un gain à un assistant lancé en même temps qu'une formation réservée au groupe équipé. Que conclus-tu ? <!--anki:6164373062623661376537393466623439623961643230346463383730306363-->
?
1. **Identifier le changement conjoint** et sa plausibilité comme cause du gain.
2. **Revoir l'effet ciblé** : assistant seul ou programme assistant plus formation.
3. **Chercher un groupe ou un calendrier informatif** permettant une séparation crédible.
4. **Examiner tendances, composition et chocs**, avec l'incertitude appropriée.
5. **Rapporter ce qui est identifiable**, ou concevoir une nouvelle expérience pour isoler l'assistant.

**Piège** : nommer « effet du modèle » l'effet d'un ensemble de changements indissociables.

---

## Sources
- [Hernán & Robins — Causal Inference: What If, hypothèses et graphes](https://miguelhernan.org/whatifbook)
- [PyWhy — modéliser, identifier et estimer un effet](https://www.pywhy.org/dowhy/v0.13/user_guide/causal_tasks/estimating_causal_effects/index.html)
- [PyWhy — limites et réfutation des estimations](https://www.pywhy.org/dowhy/v0.13/user_guide/refuting_causal_estimates/index.html)
- [SHAP — distinguer prédiction et décision causale](https://shap.readthedocs.io/en/latest/example_notebooks/overviews/Be%20careful%20when%20interpreting%20predictive%20models%20in%20search%20of%20causal%20insights.html)
- [Callaway & Sant’Anna — différences de différences et adoptions multiples](https://arxiv.org/abs/1803.09015)

## Connexions
- [[99-statistiques-decisions-experimentales|Statistiques expérimentales]] — distinguer estimation précise et conclusion valide
- [[97-evals-online-ab-testing|A/B testing]] — concevoir une intervention randomisée
- [[177-explicabilite-modeles|Explicabilité]] — ne pas transformer une attribution en causalité
- [[174-recommandation-ranking|Recommandation]] — tenir compte de l'exposition dans les journaux
- [[00-moc-ai-engineering|MOC AI Engineering]]
