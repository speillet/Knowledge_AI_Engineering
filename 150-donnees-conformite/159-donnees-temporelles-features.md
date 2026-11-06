# Données temporelles & variables de production — Flashcards
Tags: #flashcards #ai-engineering #donnees #data-engineering #features
<!-- summary: temps événement et traitement, disponibilité historique, jointures point-in-time, corrections bitemporelles, fenêtres et watermarks, labels retardés, cohérence entraînement-serving, feature store et fraîcheur, chemins offline/online et matérialisation sûre. -->


À ne pas confondre : temps de l'événement et temps de traitement ? <!--anki:6530353238343566646235653466306338396630383966326238633938343537-->
?
Le **temps de l'événement** décrit quand le fait s'est produit ; le **temps de traitement** décrit quand le système le traite. Une commande faite à 10 h et reçue à 10 h 20 appartient à la réalité de 10 h, mais n'était pas nécessairement connue du prédicteur à 10 h 05.

Conserver les deux permet de traiter les retards et de reconstruire ce que le système savait. Ajouter si nécessaire l'heure de publication effective de la variable : recevoir une donnée ne signifie pas qu'elle est déjà exploitable par le service.

---

Qu'est-ce qu'une jointure point-in-time pour construire un dataset ML ? <!--anki:3837343539316435383738383462666138346361386638383963376563376436-->
?
Pour chaque observation à prédire à l'instant **t**, récupérer les variables historiques valides à cet instant, sans prendre leurs versions futures. Une valeur peut aussi être exclue si elle est trop ancienne selon sa durée de validité.

La seule condition « date de l'événement ≤ t » ne suffit pas lorsque des données arrivent tard : joindre sur leur disponibilité réelle à t.
```python
pd.merge_asof(obs.sort_values("t"), feats.sort_values("disponible_a"),
              left_on="t", right_on="disponible_a", by="client_id",
              direction="backward", tolerance=pd.Timedelta("7D"))  # dernière valeur connue, d'au plus 7 jours
```
Un historique réécrit aujourd'hui peut autrement faire croire qu'une information était accessible hier.

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

On peut ainsi distinguer la meilleure estimation actuelle du passé et les données qui guidaient la décision passée. Exemple : le revenu de janvier d'un client, enregistré à 3 000 € le 3 janvier, est corrigé à 3 400 € le 15 mars. Une décision du 10 février a vu 3 000 € ; écraser l'ancienne valeur rend ce fait irreconstituable. Choisir ce niveau de détail selon les besoins d'audit.

---

Comment calculer une variable glissante sans regarder dans le futur ? <!--anki:6166353530373162666438323432646138313765653564383039383732333233-->
?
Définir explicitement **la fenêtre, ses bornes et la disponibilité des événements**. Pour un nombre d'achats sur les sept jours précédents à t, une convention possible est [t−7 jours, t), avec seuls les événements effectivement connus à t.

La borne ouverte évite de compter l'événement dont on cherche précisément à prédire l'issue. Utiliser les mêmes fuseaux et conventions en entraînement et serving. Tester frontières, arrivées tardives et corrections. Une agrégation « par jour » calculée après minuit peut révéler le futur d'une décision prise le matin.

---

Que signifie un watermark dans un traitement de flux ? <!--anki:3765613236353839333133623435363639306265623534303766343063626337-->
?
Un **watermark** représente une estimation de progression dans le temps des événements. Il aide à décider quand produire ou finaliser les résultats d'une fenêtre et comment traiter les données qui arrivent ensuite.

Ce n'est pas une preuve universelle que plus aucun événement ancien n'arrivera. Exemple : avec un watermark égal à « horodatage maximal vu − 10 minutes », 12 h 30 observé déclare la fenêtre 12 h 00–12 h 15 complète ; un événement de 12 h 10 reçu ensuite est tardif. Choisir une tolérance au retard, puis décider entre correction, résultat provisoire ou rejet documenté. Attendre davantage améliore parfois la complétude, mais augmente latence et état conservé.

---

Comment traiter un événement tardif après publication d'un agrégat ? <!--anki:3066343764656439633234653466613861336165636337363131306434616337-->
?
Choisir une **politique explicite de correction** : mettre à jour l'agrégat avec une nouvelle version, publier une rétraction suivie du résultat corrigé, ou le classer hors délai avec une mesure de perte de couverture.

La politique dépend des consommateurs : un tableau de bord peut être corrigé, une action externe déjà effectuée ne s'annule pas automatiquement. Exemple : les ventes du 20 octobre, publiées à 10 000 €, passent à 10 450 € en version 2 ; la décision prise le 21 garde la trace des 10 000 € qu'elle a réellement vus. Remplacer tout l'historique par la valeur finale fausserait une simulation du fonctionnement passé.

---

Comment évaluer un modèle dont les labels arrivent plusieurs semaines plus tard ? <!--anki:3034663863316234326462623434653339323737376463343665343536346230-->
?
Définir une **période de maturation** cohérente avec la cible. Pour une résiliation dans les 30 jours, l'absence de résiliation après cinq jours ne constitue pas encore un négatif certain.

Évaluer des cohortes suffisamment anciennes ou employer une méthode adaptée aux observations censurées. Séparer les indicateurs rapides, encore provisoires, des métriques consolidées. Conserver date de prédiction, date d'observation et version du label. Une baisse apparente de positifs sur les dernières semaines peut provenir seulement de labels incomplets, pas d'une amélioration du modèle.

---

Qu'est-ce que le training-serving skew des variables ? <!--anki:6663663964393236376562653464623239343638613033613763356635393539-->
?
C'est un **écart entre les variables utilisées à l'entraînement et celles produites en service** : formule différente, arrondi, fuseau, source, fraîcheur ou gestion des absences. Même des poids identiques se comportent différemment si les entrées ont changé de sens. Exemple : `anciennete_jours` est calculée en UTC à minuit pour l'entraînement, en heure de Paris à l'instant de la requête en service ; certains clients gagnent un jour.

Partager les définitions et versions réduit ce risque. Comparer les valeurs effectivement servies à un recalcul contrôlé sur les mêmes événements, en respectant leur disponibilité. Un historique finalisé peut légitimement différer d'un état provisoire : comprendre cet écart plutôt que le masquer.

---

Quand un feature store est-il utile, et que ne garantit-il pas ? <!--anki:6331346435366635393235633430303461303230326362373566383935376235-->
?
Il peut centraliser **définitions, historiques et accès aux variables** pour plusieurs modèles, avec des chemins adaptés à l'entraînement et au service. Il devient intéressant lorsque les duplications de calcul et incohérences coûtent plus que sa propre complexité : trois modèles qui recalculent chacun « achats sur 30 jours » avec des fenêtres différentes, par exemple.

Il ne rend pas les variables exactes par magie et ne supprime pas les problèmes de disponibilité historique. Vérifier jointures temporelles, fraîcheur, corrections et responsabilités. Une petite application peut commencer avec une pipeline versionnée et un stockage simple, puis ajouter cette brique lorsque des besoins mesurés le justifient.

---

Quel comportement prévoir lorsqu'une variable de production est trop ancienne ? <!--anki:3030623161323236366138653430363562346665633465353835346631323562-->
?
Définir une **durée de validité propre à la variable et à l'usage**. Contrôler l'âge réel de la valeur, pas seulement l'état de santé du service qui la renvoie.

Prévoir attente bornée, modèle de secours, abstention ou décision humaine selon le risque. Exemple : un stock vaut 5 minutes, le pays du compte 30 jours ; un stock vieux de deux heures bascule vers un modèle de secours qui n'utilise pas cette variable. Une valeur absente et une valeur périmée peuvent exiger des traitements différents. Mesurer l'utilisation du mode dégradé pour éviter qu'il devienne silencieusement le fonctionnement normal.

---

À ne pas confondre : stockage offline et online des features ? <!--anki:3737623337316630626462303433383962333335366533636535343039646365-->
?
Le **stockage offline** sert notamment à reconstruire des historiques et lots d'entraînement. Le **stockage online** vise la récupération des variables utiles à une requête avec la latence attendue, souvent par clé d'entité.

Une valeur courante rapide à lire ne fournit pas automatiquement son historique ; un historique complet n'offre pas nécessairement un accès interactif rapide. Feast expose ainsi deux appels pour la même définition :
```python
store.get_historical_features(entity_df=obs, features=["client:achats_30j"])   # offline, point-in-time
store.get_online_features(features=["client:achats_30j"], entity_rows=[{"client_id": 42}])
```
Vérifier types, valeurs manquantes, fraîcheur et version des transformations dans les deux chemins.

---

Comment matérialiser des features en ligne sans écraser une valeur récente par un backfill ancien ? <!--anki:6566643833666364333636303431363762653937316363366536636330323934-->
?
Associer **clé d'entité, version de feature et ordre temporel pertinent**, puis écrire selon une politique qui refuse ou isole les mises à jour obsolètes. Les garanties du stockage et de son connecteur doivent être vérifiées.

Séparer reconstruction offline et publication online lorsque leurs objectifs diffèrent. Un backfill historique ne doit pas remplacer la valeur courante simplement parce qu'il termine plus tard : recalculée pour le 1er mars et écrite le 10 octobre, `achats_30j` écraserait sinon la valeur du jour. Tester événement tardif, correction valide, suppression et rejeu. La règle « plus grand timestamp gagne » n'est correcte que si ce timestamp exprime réellement l'ordre métier attendu.

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
- [Feast — architecture et chemins de features](https://docs.feast.dev/getting-started/architecture/overview)
- [Feast — stockage online](https://docs.feast.dev/getting-started/components/online-store)
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
- [[150-014-streaming-traitements-evenements|Streaming & traitements d’événements]] — respecter temps événement, disponibilité et retards
- [[117-pipelines-entrainement-continu|Pipelines d'entraînement]] — maturité des labels avant réentraînement
- [[00-moc-ai-engineering|MOC AI Engineering]]
