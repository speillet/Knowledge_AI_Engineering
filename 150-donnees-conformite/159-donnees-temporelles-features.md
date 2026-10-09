# Données temporelles & variables de production — Flashcards
Tags: #flashcards #ai-engineering #donnees #data-engineering #features
<!-- summary: temps événement et traitement, disponibilité historique, jointures point-in-time, corrections bitemporelles, fenêtres et watermarks, labels retardés, cohérence entraînement-serving, feature store et fraîcheur. -->


À ne pas confondre : temps de l'événement et temps de traitement ? <!--anki:6530353238343566646235653466306338396630383966326238633938343537-->
?
Le **temps de l'événement** décrit quand le fait s'est produit ; le **temps de traitement** décrit quand le système le traite. Une commande faite à 10 h et reçue à 10 h 20 appartient à la réalité de 10 h, mais n'était pas nécessairement connue du prédicteur à 10 h 05.

Conserver les deux permet de traiter les retards et de reconstruire ce que le système savait. Ajouter si nécessaire l'heure de publication effective de la variable : recevoir une donnée ne signifie pas qu'elle est déjà exploitable par le service.

---

Qu'est-ce qu'une jointure point-in-time pour construire un dataset ML ? <!--anki:3837343539316435383738383462666138346361386638383963376563376436-->
?
Pour chaque observation à prédire à l'instant **t**, récupérer les variables historiques valides à cet instant, sans prendre leurs versions futures. Une valeur peut aussi être exclue si elle est trop ancienne selon sa durée de validité.

La seule condition « date de l'événement ≤ t » ne suffit pas lorsque des données arrivent tard : vérifier leur disponibilité réelle à t. Un historique réécrit aujourd'hui peut autrement faire croire qu'une information était accessible hier. Définir précisément la garantie temporelle du stockage ou de l'outil utilisé.

---

Calcul : à 10 h 05, peut-on utiliser un achat effectué à 9 h 58 mais publié dans les variables à 10 h 12 ? <!--anki:3539643131366436633237333439313061336166363534386464363638613463-->
?
**Non**, pour simuler une prédiction réellement faite à 10 h 05. Le fait appartient au passé métier, mais sa disponibilité pour le modèle est postérieure à la décision.
```text
temps événement = 09:58 ≤ 10:05
disponible à    = 10:12 > 10:05 → exclure de la simulation
```
L'inclure dans l'entraînement ou l'évaluation historique créerait une fuite temporelle. Si un autre canal le rendait accessible plus tôt, il faudrait le démontrer et utiliser la définition de disponibilité correspondante, plutôt que supposer que le timestamp source suffit.

---

Pourquoi conserver plusieurs versions d'une valeur historique corrigée ? <!--anki:6432343334353963333866333435336561653031323436646466343834653339-->
?
Une correction peut changer ce que l'on considère vrai **pour une date passée**, sans changer ce que le système savait à l'époque. Une représentation bitemporelle distingue période de validité métier et période de connaissance ou d'enregistrement.

On peut ainsi répondre à deux questions différentes : « quelle est notre meilleure estimation actuelle du passé ? » et « quelles données pouvaient guider la décision passée ? ». Écraser l'ancienne valeur empêche le second usage. Définir la politique de conservation et les besoins d'audit avant de choisir ce niveau de détail.

---

Comment calculer une variable glissante sans regarder dans le futur ? <!--anki:6166353530373162666438323432646138313765653564383039383732333233-->
?
Définir explicitement **la fenêtre, ses bornes et la disponibilité des événements**. Pour un nombre d'achats sur les sept jours précédents à t, une convention possible est [t−7 jours, t), avec seuls les événements effectivement connus à t.

La borne ouverte évite de compter l'événement dont on cherche précisément à prédire l'issue. Utiliser les mêmes fuseaux et conventions en entraînement et serving. Tester frontières, arrivées tardives et corrections. Une agrégation « par jour » calculée après minuit peut révéler le futur d'une décision prise le matin.

---

Que signifie un watermark dans un traitement de flux ? <!--anki:3765613236353839333133623435363639306265623534303766343063626337-->
?
Un **watermark** représente une estimation de progression dans le temps des événements. Il aide à décider quand produire ou finaliser les résultats d'une fenêtre et comment traiter les données qui arrivent ensuite.

Ce n'est pas une preuve universelle que plus aucun événement ancien n'arrivera. Les garanties dépendent de la source et du moteur. Choisir une tolérance au retard, puis décider entre correction, résultat provisoire ou rejet documenté. Attendre davantage améliore parfois la complétude, mais augmente latence et état conservé.

---

Comment traiter un événement tardif après publication d'un agrégat ? <!--anki:3066343764656439633234653466613861336165636337363131306434616337-->
?
Choisir une **politique explicite de correction** : mettre à jour l'agrégat avec une nouvelle version, publier une rétraction suivie du résultat corrigé, ou le classer hors délai avec une mesure de perte de couverture.

La politique dépend des consommateurs : un tableau de bord peut être corrigé, une action externe déjà effectuée ne s'annule pas automatiquement. Si l'agrégat sert de variable ML, conserver aussi la valeur réellement vue lors de la prédiction. Remplacer tout l'historique par la valeur finale fausserait une simulation du fonctionnement passé.

---

Comment évaluer un modèle dont les labels arrivent plusieurs semaines plus tard ? <!--anki:3034663863316234326462623434653339323737376463343665343536346230-->
?
Définir une **période de maturation** cohérente avec la cible. Pour une résiliation dans les 30 jours, l'absence de résiliation après cinq jours ne constitue pas encore un négatif certain.

Évaluer des cohortes suffisamment anciennes ou employer une méthode adaptée aux observations censurées. Séparer les indicateurs rapides, encore provisoires, des métriques consolidées. Conserver date de prédiction, date d'observation et version du label. Une baisse apparente de positifs sur les dernières semaines peut provenir seulement de labels incomplets, pas d'une amélioration du modèle.

---

Qu'est-ce que le training-serving skew des variables ? <!--anki:6663663964393236376562653464623239343638613033613763356635393539-->
?
C'est un **écart entre les variables utilisées à l'entraînement et celles produites en service** : formule différente, arrondi, fuseau, source, fraîcheur ou gestion des absences. Même des poids identiques se comportent différemment si les entrées ont changé de sens.

Partager les définitions et versions réduit ce risque. Comparer les valeurs effectivement servies à un recalcul contrôlé sur les mêmes événements, en respectant leur disponibilité. Un historique finalisé peut légitimement différer d'un état provisoire ; cette différence doit être comprise plutôt que masquée dans la comparaison.

---

Quand un feature store est-il utile, et que ne garantit-il pas ? <!--anki:6331346435366635393235633430303461303230326362373566383935376235-->
?
Il peut centraliser **définitions, historiques et accès aux variables** pour plusieurs modèles, avec des chemins adaptés à l'entraînement et au service. Il devient intéressant lorsque les duplications de calcul et incohérences coûtent plus que sa propre complexité.

Il ne rend pas les variables exactes par magie et ne supprime pas les problèmes de disponibilité historique. Vérifier jointures temporelles, fraîcheur, corrections et responsabilités. Une petite application peut commencer avec une pipeline versionnée et un stockage simple, puis ajouter cette brique lorsque des besoins mesurés le justifient.

---

Quel comportement prévoir lorsqu'une variable de production est trop ancienne ? <!--anki:3030623161323236366138653430363562346665633465353835346631323562-->
?
Définir une **durée de validité propre à la variable et à l'usage**. Le pays d'un compte peut tolérer plus de retard qu'un solde ou un stock. Contrôler l'âge réel de la valeur, pas seulement l'état de santé du service qui la renvoie.

Prévoir attente bornée, modèle de secours, abstention ou décision humaine selon le risque. Une valeur absente et une valeur périmée peuvent exiger des traitements différents. Mesurer l'utilisation du mode dégradé pour éviter qu'il devienne silencieusement le fonctionnement normal.

---

## Mises en situation

Mise en situation : un modèle historique est excellent, mais ses performances chutent dès son lancement malgré les mêmes colonnes. Que recherches-tu ? <!--anki:6131633734393433356463633438363239396262626138313536326561376135-->
?
1. **Reconstituer l'instant de décision** et la disponibilité réelle de chaque variable.
2. **Identifier les corrections tardives** et agrégats calculés après les événements à prédire.
3. **Comparer des exemples servis** à la reconstruction historique de ce qui était alors connu.
4. **Corriger les jointures et splits** puis réentraîner et réévaluer sans données futures.
5. **Surveiller fraîcheur et écarts** entre pipelines d'entraînement et de production.

**Piège** : croire qu'avoir les mêmes noms de colonnes garantit les mêmes informations.

---

Mise en situation : un score d'activité est calculé par jour, mais des événements mobiles arrivent jusqu'à deux jours plus tard. Quelle politique proposes-tu ? <!--anki:3831353430663630303639323462373639613761623263326238366562643332-->
?
1. **Mesurer la distribution des retards** et préciser la latence acceptable pour le produit.
2. **Publier un résultat provisoire** si nécessaire, avec un statut et une version.
3. **Définir la fenêtre de correction** et le traitement des événements arrivant au-delà.
4. **Prévenir les consommateurs** de la possibilité de révisions et rendre leur application sûre.
5. **Conserver les valeurs vues** par les modèles pour reconstruire les décisions passées.

**Piège** : utiliser le score final corrigé pour évaluer une décision qui n'avait accès qu'au score provisoire.

---

Mise en situation : un modèle de churn semble s'améliorer fortement sur les sept derniers jours alors que sa cible est une résiliation sous 30 jours. Comment vérifies-tu ? <!--anki:3132613765363565353062613463356239346131386466356431656437366261-->
?
1. **Contrôler la maturité des labels** : la plupart des issues ne sont probablement pas encore observables.
2. **Distinguer absence d'événement et négatif confirmé**, sans convertir automatiquement les inconnus en zéros.
3. **Comparer des cohortes matures** avec le même horizon et les mêmes segments.
4. **Présenter séparément les signaux provisoires** et les mesures consolidées.
5. **Corriger les tableaux de bord** et les règles de sélection des données d'entraînement.

**Piège** : promouvoir un modèle sur une amélioration créée par le délai d'observation.

---

## Sources
- [Feast — jointures point-in-time](https://docs.feast.dev/getting-started/concepts/point-in-time-joins)
- [Apache Beam — temps des événements, watermarks et données tardives](https://beam.apache.org/documentation/programming-guide/#watermarks-and-late-data)
- [TensorFlow Data Validation — écarts entraînement et serving](https://www.tensorflow.org/tfx/guide/tfdv)

## Connexions
- [[157-contrats-qualite-donnees|Contrats & qualité]] — exprimer fraîcheur, unités et disponibilité
- [[158-ingestion-cdc-backfills|Ingestion & backfills]] — transporter et rejouer des changements temporels
- [[172-validation-metriques-ml|Validation ML]] — prévenir les fuites temporelles
- [[113-monitoring-drift-feedback|Drift & feedback]] — interpréter les labels et signaux de production
- [[175-series-temporelles-prevision|Prévision de séries temporelles]] — reconstruire les informations disponibles
- [[150-010-modelisation-donnees-analytiques|Modélisation des données analytiques]] — relier histoire métier et disponibilité pour le modèle
- [[150-011-sql-transformations-analytiques|SQL pour les pipelines et datasets IA]] — empêcher les jointures qui révèlent le futur
- [[00-moc-ai-engineering|MOC AI Engineering]]
