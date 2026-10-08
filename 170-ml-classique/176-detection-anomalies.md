# Détection d'anomalies — Flashcards
Tags: #flashcards #ai-engineering #ml-classique #anomalies #monitoring
Vérifié le : 8 octobre 2026
<!-- summary: rareté et erreur métier, outlier ou nouveauté, scores non probabilistes, baseline contextuelle, Isolation Forest, LOF, autoencodeurs, capacité de revue, prévalence, évaluation par incident, labels manquants et dérive. -->


Pourquoi une observation rare n'est-elle pas automatiquement une anomalie métier ? <!--anki:3262626534616237356331383432303561333862383131383336643362343139-->
?
Un détecteur repère un **écart à une référence**, qui peut correspondre à un incident, une nouveauté légitime ou une erreur de collecte. Un pic de commandes pendant une promotion est rare dans l'historique mais peut être attendu.

Définir l'action que doit déclencher l'alerte et le coût d'une fausse alarme. Conserver le contexte et une possibilité de revue. Supprimer automatiquement les observations atypiques peut effacer les cas les plus intéressants, ou transformer un changement réel d'activité en problème artificiel de qualité des données.

---

À ne pas confondre : détection d'outliers et détection de nouveauté ? <!--anki:3566633064316234396366303465626338396334643434303238326365346562-->
?
La **détection d'outliers** cherche des observations atypiques dans un jeu pouvant déjà en contenir. La **détection de nouveauté** apprend une référence supposée normale, puis juge de nouvelles observations par rapport à cette référence.

Cette distinction influence choix des données et méthode d'évaluation. Un historique contaminé peut faire apprendre un incident comme normal. Un nouveau comportement légitime peut être signalé à tort. Dans les deux cas, la pertinence métier exige des labels ou des investigations ; la géométrie des données ne définit pas seule l'incident.

---

Pourquoi un score d'anomalie de 0,95 n'est-il pas nécessairement un risque de 95 % ? <!--anki:6431623064323139323738383465656538323839316133323230316631636137-->
?
Un **score d'anomalie** ordonne souvent les observations selon isolement, densité ou erreur de reconstruction. Son échelle, et parfois son sens, dépendent de l'algorithme ; il n'est pas automatiquement calibré comme une probabilité d'incident.

Pour décider, choisir un seuil sur des observations représentatives et examiner les alertes obtenues. Le paramètre `contamination` de certains estimateurs règle un seuil à partir d'une proportion supposée ; il ne mesure pas la prévalence réelle et ne garantit pas le taux de fausses alertes futur.

---

Quelle baseline construire pour détecter une anomalie dans une série saisonnière ? <!--anki:3133393363653030656434313436393561643265306231313865386336376365-->
?
Comparer l'observation à une **référence adaptée au contexte** : heure, jour, catégorie ou prévision historique. Une médiane et une dispersion robuste sur des périodes comparables peuvent fournir un premier score d'écart.

Apprendre la référence sur le passé disponible et préciser ce qui arrive quand la dispersion est nulle ou les données absentes. Évaluer les résidus de prévision peut aider, sans garantir leur stabilité. Un seuil global sur les valeurs brutes signale souvent la saisonnalité normale plutôt que les incidents recherchés.

---

Comment Isolation Forest repère-t-il des observations atypiques ? <!--anki:6362353831653063623837373431313339366433396539346664613032613361-->
?
Il construit des arbres à **partitions aléatoires** des variables et mesure combien de séparations sont nécessaires pour isoler un point. Des observations isolées rapidement reçoivent un caractère plus atypique selon le score utilisé.

Le résultat dépend de la représentation, du sous-échantillonnage et de la structure des données. Ce mécanisme n'apprend pas directement une définition métier de fraude ou de panne. Tester plusieurs familles d'incidents et les fausses alertes ; une anomalie ressemblant géométriquement au fonctionnement normal peut rester difficile à détecter.

---

Quand une densité locale comme LOF est-elle utile pour détecter des anomalies ? <!--anki:6639663934643636316264303436363639626162376439653233396630336234-->
?
**Local Outlier Factor** compare la densité d'un point à celle de son voisinage. Il peut signaler un point inhabituel pour son groupe, même si une autre région du jeu possède une densité globale différente.

Distances, échelle des variables et nombre de voisins influencent fortement ce voisinage. Dans scikit-learn, le mode par défaut sert à analyser les données ajustées ; le mode `novelty=True` permet de scorer de nouvelles données, avec des précautions distinctes. Ne pas évaluer ce dernier sur ses propres observations d'entraînement comme s'il s'agissait de nouveaux cas.

---

Pourquoi un autoencodeur peut-il bien reconstruire une anomalie ? <!--anki:3661393162663335383138643466373662653762663933333730626335356363-->
?
L'autoencodeur apprend à **reconstruire ses entrées**, pas à reconnaître directement les incidents. Une capacité élevée, un entraînement contaminé ou une anomalie proche des motifs normaux peuvent produire une reconstruction très précise d'un cas problématique.

Inversement, un cas normal nouveau peut être mal reconstruit. Comparer à des baselines simples et valider l'erreur de reconstruction sur des incidents représentatifs. Réduire arbitrairement la taille latente ne garantit pas de séparer normal et anormal ; examiner les variables qui dominent la perte et leur normalisation.

---

Comment choisir un seuil d'anomalie avec une capacité humaine limitée ? <!--anki:3930393333353237366365633432326361616164306638343233663665663064-->
?
Relier le seuil au **volume d'alertes et aux incidents retrouvés**. Pour une équipe capable de traiter 30 dossiers par jour, mesurer précision parmi les 30 premiers, rappel des incidents critiques et délai avant investigation.

Un top-k borne la charge mais peut envoyer des alertes inutiles les jours calmes ou manquer un incident collectif. Prévoir seuil minimal, regroupement et traitement des urgences selon le contexte. Le seuil se règle sur validation ; sa capacité opérationnelle doit ensuite être vérifiée sur une période indépendante.

---

Calcul : sur 100 000 événements dont 100 incidents, combien d'alertes avec 90 % de rappel et 1 % de faux positifs ? <!--anki:6264363065303339333633643433333838646466353363656366623632653936-->
?
En prenant ces taux comme exacts pour cet exemple :
```text
Vrais positifs = 100 × 0,90 = 90
Faux positifs = 99 900 × 0,01 = 999
Alertes = 1 089 ; précision = 90 / 1 089 ≈ 8,3 %
```
Le taux de faux positifs porte sur les événements normaux, pas sur toutes les alertes. Malgré un bon rappel, la plupart des investigations seraient inutiles. Avec des taux estimés, ajouter leur incertitude et vérifier la prévalence de production avant de dimensionner l'équipe.

---

Pourquoi évaluer une détection temporelle par incident en plus des points individuels ? <!--anki:6439623633616130303133383432363238656239336361343264613864646162-->
?
Un même incident peut durer des centaines de points. Le compter point par point peut surpondérer sa durée ou récompenser une détection très tardive. Mesurer aussi **incidents retrouvés, délai de détection et fausses alertes par période**.

Définir fenêtres de tolérance, regroupement et règle d'association avant l'évaluation. Le point adjustment qui marque tout un intervalle détecté dès qu'un point l'est peut gonfler certains scores. Rapporter précisément le protocole et conserver une mesure reflétant le moment où l'opérateur aurait réellement pu intervenir.

---

Comment évaluer un détecteur d'anomalies quand les labels sont incomplets ? <!--anki:3863656264616537646261393438373439316164653138373635343665306531-->
?
Faire relire les alertes et un **échantillon de non-alertes**, avec une stratégie et des probabilités de sélection documentées. Examiner uniquement les alertes permet d'approcher leur précision, mais pas de compter les incidents manqués dans toute la population.

Utiliser, si nécessaire, des pondérations et une incertitude adaptées à l'échantillonnage. Des anomalies injectées testent certains mécanismes, sans représenter automatiquement les incidents réels. Séparer cas confirmés, inconnus et labels retardés ; l'absence de signalement ne constitue pas une preuve de normalité.

---

## Mises en situation

Mise en situation : ton détecteur déclenche des milliers d'alertes à chaque campagne commerciale. Comment réduis-tu le bruit ? <!--anki:6433633933363164373861643432663739303733633265616131366563633334-->
?
1. **Vérifier le changement réel** et éliminer une panne de collecte.
2. **Ajouter le contexte disponible** : campagne, jour, segment et volume attendu.
3. **Comparer une baseline contextuelle** au modèle actuel sur plusieurs périodes.
4. **Regrouper les alertes liées** et mesurer le délai de détection des vrais incidents.
5. **Fixer le seuil sur validation**, puis vérifier charge humaine et rappel critique.

**Piège** : désactiver toute détection pendant les campagnes, où de vrais incidents restent possibles.

---

Mise en situation : un autoencodeur obtient une faible erreur de reconstruction sur des pannes connues. Que vérifies-tu ? <!--anki:3638363535313663353533643437383639626632373261376433306335656464-->
?
1. **Chercher la contamination** des données d'entraînement par ces pannes ou leurs copies.
2. **Examiner la représentation** et les variables qui dominent la perte.
3. **Comparer à une baseline** de seuils contextuels ou d'isolement.
4. **Tester sur des périodes distinctes** et plusieurs familles d'incidents.
5. **Reformuler la tâche** en détection supervisée si suffisamment de labels fiables existent.

**Piège** : assimiler faible reconstruction et absence de risque métier.

---

Mise en situation : le taux d'alertes grimpe après un changement durable de fonctionnement, et l'équipe veut réentraîner immédiatement. Que décides-tu ? <!--anki:3262653861616635626166623464633638366134636534326334386233643835-->
?
1. **Distinguer changement légitime et incident**, avec le responsable du processus.
2. **Vérifier la collecte et les unités**, avant de conclure à une dérive du comportement.
3. **Isoler la période de transition** et confirmer quels exemples peuvent devenir la nouvelle référence.
4. **Réévaluer ancien et nouveau détecteur** sur normalité et incidents connus.
5. **Déployer progressivement** avec possibilité de repli et suivi des labels retardés.

**Piège** : réentraîner sur un incident en cours et apprendre à le considérer comme normal.

---

## Sources
- [scikit-learn — outliers, nouveauté et LOF](https://scikit-learn.org/stable/modules/outlier_detection.html)
- [scikit-learn — Isolation Forest et seuil](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html)
- [Kim et al. — Towards a Rigorous Evaluation of Time-series Anomaly Detection](https://arxiv.org/abs/2109.05257)
- [Bouman & Heskes — limites de la reconstruction pour détecter les anomalies](https://arxiv.org/abs/2501.13864)

## Connexions
- [[175-series-temporelles-prevision|Prévision temporelle]] — construire une référence contextuelle
- [[172-validation-metriques-ml|Validation ML]] — classes rares et coût des faux positifs
- [[113-monitoring-drift-feedback|Monitoring & drift]] — distinguer incident et évolution de la référence
- [[151-donnees-curation-annotation|Annotation]] — organiser la confirmation des incidents
- [[00-moc-ai-engineering|MOC AI Engineering]]
