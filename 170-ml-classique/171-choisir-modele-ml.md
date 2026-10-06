# ML classique : choisir et comprendre les modèles — Flashcards
Tags: #flashcards #ai-engineering #ml-classique #modeles #baseline
<!-- summary: règles ou ML ou LLM, formulation de la cible, baselines, régressions, régularisation, arbres, random forest et boosting, clustering, prétraitement, données manquantes et coût de possession. -->


Comment choisir entre règles, ML classique et LLM pour un besoin métier ? <!--anki:6661353466646534356365313436373439663763316530386363633734333530-->
?
Partir de la **décision attendue**, des données disponibles et du coût des erreurs. Des règles conviennent à une politique explicite et stable ; un modèle supervisé apprend une relation à partir d'exemples labellisés ; un LLM apporte surtout des capacités de traitement du langage et de génération.

Comparer ces approches sur les mêmes cas et contraintes. Une extraction par LLM suivie d'un modèle tabulaire peut être pertinente. La complexité supplémentaire doit apporter un gain mesurable de qualité ou de maintenance, pas seulement une démonstration plus impressionnante.

---

Comment définir une cible supervisée avant de choisir un algorithme ? <!--anki:6361663033653337336436613433356639386630636230633635373037396664-->
?
Préciser **l'unité prédite, l'instant de décision, l'horizon et le label**. « Prédire le churn » est incomplet ; « pour chaque abonnement actif au premier du mois, prédire sa résiliation dans les 30 jours » définit une tâche testable.

Les variables doivent être disponibles au moment de la décision. Les labels exigent d'attendre la fin de l'horizon : un abonnement observé depuis cinq jours ne peut pas encore être considéré comme un négatif à 30 jours. Cette définition conditionne le découpage temporel et la collecte.

---

À ne pas confondre : classification, régression et clustering ? <!--anki:3636313061303366326164643436656161633537306134646361623337323035-->
?
La **classification** prédit une catégorie connue, par exemple le type d'un ticket. La **régression** prédit une quantité, comme son délai de résolution. Le **clustering** regroupe des observations selon une représentation et une notion de proximité, sans labels de classes imposés.

Un groupe découvert ne constitue pas automatiquement une catégorie métier utile. Il faut examiner les exemples, la stabilité des groupes et leur usage. Choisir la tâche selon la décision à prendre : créer dix groupes n'aide pas nécessairement à router vers les cinq équipes existantes.

---

Quelle baseline construire avant un modèle prédictif complexe ? <!--anki:6536376232316439373065333461623239383837346531333266383635376438-->
?
Mesurer une **référence simple et exploitable** : classe majoritaire pour une classification, moyenne ou médiane pour une régression selon la perte, règle métier existante, ou modèle linéaire. Pour prévoir une série, une valeur récente ou saisonnière peut être plus pertinente qu'une constante.

Évaluer cette référence avec exactement les mêmes observations et métriques que le candidat. Une baseline révèle parfois une cible mal définie ou un jeu facile. Conserver aussi le coût et la latence : un faible gain de score peut ne pas justifier une chaîne plus fragile.

---

Que suppose une régression linéaire et quand est-elle utile ? <!--anki:3230383030383231623732663437363261626131623636656633613031396534-->
?
Elle représente la prédiction par une **somme pondérée des variables**, avec un intercept. C'est une référence rapide lorsque des effets additifs constituent une approximation raisonnable. Des interactions ou transformations peuvent enrichir les variables tout en conservant une relation linéaire dans les coefficients.

Inspecter les erreurs selon les segments et les valeurs prédites. Une extrapolation hors des données observées peut devenir absurde. Un coefficient décrit une association conditionnelle dans ce modèle ; il ne démontre pas qu'une intervention sur la variable aurait cet effet causal.

---

Pourquoi la régression logistique sert-elle à classifier ? <!--anki:6136336230616464363032353437353638366637663036626532376138633466-->
?
Dans le cas binaire, elle transforme un score linéaire par une **sigmoïde** pour produire une probabilité estimée de la classe positive. Un seuil convertit ensuite cette probabilité en décision ; malgré son nom, la tâche finale est une classification.

Elle fournit une baseline compacte et rapide, notamment avec des variables textuelles ou tabulaires. La qualité des probabilités doit être vérifiée sur des observations indépendantes. Le seuil de 0,5 n'est pas une obligation : il dépend des erreurs acceptables et du coût des décisions.

---

Comment la régularisation limite-t-elle le surapprentissage ? <!--anki:6538633264316533643265343433613061303939626533343330306465356237-->
?
Elle pénalise certaines solutions complexes lors de l'entraînement. Pour un modèle linéaire, **L2** réduit les coefficients ; **L1** peut en annuler certains. On accepte éventuellement un ajustement moins précis du train pour mieux généraliser.

L'intensité se choisit sur validation, avec une échelle des variables adaptée. Une pénalité trop forte produit du sous-apprentissage. Elle ne corrige ni des labels faux ni une fuite de données ; un modèle fortement régularisé peut encore exploiter une information qui n'existera pas en production.

---

Comment un arbre de décision apprend-il des interactions ? <!--anki:6538323032383132316466343433376262336232346537663863653066336433-->
?
Il partitionne les observations par une succession de **tests sur les variables**. Une branche peut traiter différemment les clients récents selon leur activité : l'effet d'une variable dépend alors des décisions précédentes. Les feuilles portent une prédiction calculée à partir des exemples d'entraînement qui y arrivent.

Un arbre profond peut mémoriser des particularités du train et changer fortement après une petite variation des données. Limiter profondeur et taille minimale des feuilles. Une règle lisible dans l'arbre n'est pas forcément stable ou causale.

---

À ne pas confondre : random forest et gradient boosting ? <!--anki:3162346437366331633737343461333839316135333262373366323730313763-->
?
Une **random forest** agrège des arbres diversifiés par échantillonnage des observations et des variables ; leur combinaison réduit notamment la variance. Le **gradient boosting** ajoute progressivement des arbres pour améliorer une fonction de perte, en suivant le signal laissé par l'ensemble courant.

Le boosting est un candidat important sur des données tabulaires, mais ne gagne pas systématiquement. Comparer les deux avec un budget de réglage explicite. Profondeur, nombre d'arbres et, pour le boosting, taux d'apprentissage influencent généralisation, latence et mémoire.

---

Quand préférer un modèle tabulaire à un LLM ? <!--anki:3365336236643265343633653435366362646136643839623961633036336339-->
?
Lorsqu'on dispose de **variables structurées et de labels** pour une cible stable, un modèle tabulaire offre souvent une solution compacte à tester : score de risque opérationnel, délai, probabilité d'abandon. Il évite de sérialiser chaque nombre dans un prompt et peut servir à faible latence.

Comparer sur un test réaliste plutôt que supposer sa supériorité. Du texte libre peut justifier des embeddings ou une extraction en amont. Inclure coût de préparation des variables, fréquence de réentraînement et disponibilité des données en production.

---

Pourquoi le prétraitement fait-il partie du modèle déployé ? <!--anki:6666613662313664393338303434633039663034653636393630303565646361-->
?
Le modèle apprend sur une **représentation précise** : ordre des colonnes, imputation, normalisation, encodage des catégories. Il faut enregistrer et réutiliser ces transformations avec les poids. Réapprendre la normalisation sur chaque requête ou changer l'ordre des colonnes modifie le sens des entrées.

Apprendre les transformations sur le train, puis les appliquer aux autres jeux. Définir aussi le comportement pour une catégorie inconnue ou une colonne manquante. Une chaîne de transformation versionnée évite que notebook et service reconstruisent différemment les mêmes variables.

---

Comment traiter les variables numériques et catégorielles sans créer de fausse structure ? <!--anki:3533373434353664643636353432376138646464323234366439323236356333-->
?
Adapter l'encodage à la méthode. Une **standardisation** aide de nombreux modèles linéaires régularisés et méthodes de distance ; les arbres fondés sur des seuils en ont généralement moins besoin. Un encodage indicateur évite d'inventer un ordre entre des villes.

Des catégories très nombreuses demandent une stratégie de mémoire et de généralisation. Un encodage utilisant la cible doit être appris sans révéler le label de l'observation encodée. Prévoir les catégories nouvelles au lieu de les laisser provoquer des erreurs imprévues.

---

Une valeur manquante doit-elle toujours être remplacée par zéro ? <!--anki:3936623264623266636266373466646339336663393234666161383333616139-->
?
**Non : zéro porte souvent un sens métier différent de l'absence.** Un revenu inconnu n'est pas un revenu nul. Choisir une imputation adaptée, apprise sur le train, et éventuellement une variable indiquant l'absence ; certains modèles la traitent directement.

Examiner pourquoi l'information manque. Un champ rempli seulement après investigation peut révéler indirectement la cible ou un processus indisponible à la prédiction. Surveiller les taux d'absence en production : une panne de collecte ne doit pas être silencieusement transformée en changement de profil client.

---

Quand le clustering apporte-t-il une valeur concrète ? <!--anki:6561653439636339666238353439343761643964646366393263323339303934-->
?
Pour **explorer des populations**, organiser des exemples à annoter ou découvrir des familles d'erreurs. Le résultat dépend des variables, de leur échelle, de la distance et de l'algorithme. Par exemple, k-means favorise des groupes compacts autour de centroïdes et exige de choisir leur nombre.

Vérifier des exemples, la stabilité et l'utilité pour une action métier. Un bon indice géométrique ne prouve pas que les groupes correspondent à des besoins réels. Des points atypiques peuvent être importants plutôt que simplement du bruit à supprimer.

---

Pourquoi une variable importante pour un modèle n'est-elle pas forcément une cause ? <!--anki:6334663162333634336263313462653362396264366536313130396661323865-->
?
Le modèle exploite des **associations prédictives**, qui peuvent provenir d'un facteur commun, d'une fuite ou d'une variable substitutive. Une importance élevée du nombre de contacts au support ne prouve pas qu'empêcher ces contacts réduirait les résiliations.

Les importances dépendent aussi des variables corrélées et de la méthode de calcul. Les mesurer sur des données tenues à l'écart et examiner les erreurs aide à comprendre le comportement. Pour estimer l'effet d'une intervention, il faut un protocole causal approprié, pas seulement expliquer la prédiction.

---

## Mises en situation

Mise en situation : on te demande un agent LLM pour prédire le délai de livraison à partir de vingt colonnes et de deux ans d'historique. Que proposes-tu ? <!--anki:3364313230656333323766333463396362303563626536393361346335383130-->
?
1. **Définir la cible** : délai à partir de quel instant, avec quelles informations disponibles à cet instant.
2. **Construire des références** : délai habituel par trajet, modèle linéaire et arbres, évalués sur une période future.
3. **Mesurer les erreurs utiles** : écarts par région, retards extrêmes, coût des sous-estimations.
4. **Comparer le coût complet** : collecte des variables, serving, maintenance et éventuel LLM.
5. **Réserver le langage** aux données textuelles ou explications si leur valeur est démontrée.

**Piège** : intégrer la date réelle d'expédition quand la prédiction doit être faite avant sa connaissance.

---

Mise en situation : un arbre obtient 99 % de réussite sur le train et 68 % sur validation. Comment diagnostiques-tu le problème ? <!--anki:6534366630633362326131663436666162306338316336623062643237356230-->
?
1. **Vérifier le découpage et les labels** : doublons, groupes, dates et même définition de la cible.
2. **Comparer une baseline** pour savoir si 68 % constitue un progrès.
3. **Limiter la complexité** : profondeur, nombre minimal d'exemples par feuille, variables suspectes.
4. **Examiner des courbes d'apprentissage** et les segments d'erreur pour distinguer manque de données et inadéquation des variables.
5. **Retester sur validation**, en gardant le test final indépendant.

**Piège** : chercher exclusivement un algorithme plus puissant alors que l'arbre mémorise déjà le train.

---

Mise en situation : un modèle complexe gagne 0,3 point de qualité mais multiplie la latence par dix. Comment décides-tu de le déployer ? <!--anki:6666386330363161663838353430386438333736373564333237313661386639-->
?
1. **Mesurer l'incertitude** du gain sur les mêmes exemples et vérifier les segments importants.
2. **Traduire le gain** en décisions réellement améliorées et en coût d'erreur évité.
3. **Vérifier les contraintes** de latence, débit, mémoire et disponibilité des variables.
4. **Chiffrer l'exploitation** : surveillance, réentraînement, dépendances et possibilité de retour arrière.
5. **Choisir selon la valeur nette**, éventuellement avec un routage vers le modèle complexe pour les seuls cas difficiles.

**Piège** : choisir le meilleur score moyen sans vérifier qu'il apporte une amélioration utilisable.

---

## Sources
- [scikit-learn — modèles linéaires](https://scikit-learn.org/stable/modules/linear_model.html)
- [scikit-learn — ensembles d'arbres](https://scikit-learn.org/stable/modules/ensemble.html)
- [scikit-learn — prétraitement](https://scikit-learn.org/stable/modules/preprocessing.html)
- [scikit-learn — clustering](https://scikit-learn.org/stable/modules/clustering.html)

## Connexions
- [[172-validation-metriques-ml|Validation & métriques ML]] — comparer les méthodes sans biaiser l'évaluation
- [[146-choix-modeles|Choix des modèles LLM]] — situer un LLM parmi les options techniques
- [[147-leadership-technique-ia|Leadership technique]] — relier complexité et valeur métier
- [[151-donnees-curation-annotation|Curation & annotation]] — construire les exemples supervisés
- [[00-moc-ai-engineering|MOC AI Engineering]]
