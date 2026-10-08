# Prévision de séries temporelles — Flashcards
Tags: #flashcards #ai-engineering #ml-classique #forecasting #series-temporelles
<!-- summary: horizon et cadence, baseline saisonnière, ETS ou ARIMA ou ML, backtesting à origines glissantes, variables futures, prévisions directes ou récursives, lags, MAPE et MASE, quantiles, intervalles et cohérence hiérarchique. -->


Que faut-il définir avant de prévoir une série temporelle ? <!--anki:3832313262386130373438663432643761663164383138343564303065376431-->
?
Préciser **la cible, l'horizon, la cadence et l'instant de décision**. Prévoir chaque matin la demande du lendemain diffère d'une prévision hebdomadaire des quatre prochaines semaines. L'information disponible et le coût des erreurs ne sont pas les mêmes.

Définir aussi la granularité : article, magasin ou total. Distinguer demande réelle et ventes observées lorsque des ruptures limitent les ventes. Le backtest doit reproduire ces décisions et cette disponibilité historique, pas seulement prédire une colonne décalée dans un tableau complet.

---

Pourquoi une prévision saisonnière naïve constitue-t-elle une baseline importante ? <!--anki:6633316437616161323365343434356538646532396431633935303033333461-->
?
Elle reprend la **dernière valeur observée de la même saison** : pour une série quotidienne à cycle hebdomadaire, le lundi précédent sert à prévoir le lundi suivant. Elle capture un motif récurrent avec très peu de paramètres.

Comparer le modèle candidat à cette référence sur les mêmes horizons et dates. Une baseline naïve simple reprend seulement la dernière valeur. Fêtes, promotions ou ruptures structurelles peuvent invalider la répétition saisonnière ; leur présence motive une amélioration mesurée, sans supprimer l'intérêt de la comparaison.

---

À ne pas confondre : modèles ETS, ARIMA et régression avec variables retardées ? <!--anki:6265353436636335316332363465653839303034383762643230656439326230-->
?
**ETS** représente niveau, tendance et saisonnalité via lissage exponentiel. **ARIMA** décrit des dépendances temporelles et peut utiliser des différences pour traiter certaines non-stationnarités. Une **régression avec retards** apprend une relation à partir de lags et d'autres variables disponibles.

Le choix dépend de la structure, du volume de séries et des informations externes. Un modèle global peut partager l'apprentissage entre séries. Comparer au même protocole multi-horizon ; davantage de paramètres ou un modèle pré-entraîné ne garantit pas un gain sur la population visée.

---

Comment construire un backtest à origines glissantes ? <!--anki:6134643739613434633563343463323562633266383333656563646135366564-->
?
Choisir plusieurs **dates de décision**. À chacune, reconstruire les données disponibles, entraîner ou réutiliser le modèle selon la cadence prévue, puis prévoir les horizons réellement demandés. Avancer la date et répéter sans inclure les observations futures dans l'entraînement.

Rapporter les erreurs par horizon et période, avec une agrégation explicite entre séries. Des fenêtres qui se chevauchent produisent des erreurs dépendantes. Régler les hyperparamètres sur des fenêtres de validation distinctes et réserver une période finale indépendante pour la conclusion.

---

Pourquoi distinguer variables futures connues et variables futures à prévoir ? <!--anki:6439613435346139376561313434386261633631363235643238623938333563-->
?
Un **calendrier** ou une promotion déjà planifiée peut être disponible pour l'horizon visé. La météo effectivement observée ce jour-là ne l'est pas : seules ses prévisions disponibles à la date de décision peuvent servir.

Archiver les versions historiques de ces informations pour un backtest réaliste. Utiliser une variable future inconnue impose de la prévoir ou d'étudier des scénarios ; cette incertitude influence le résultat final. Un intervalle conditionnel à une météo supposée exacte ne couvre pas automatiquement l'erreur de la prévision météo.

---

À ne pas confondre : prévision récursive et prévision directe à plusieurs horizons ? <!--anki:3565636464326634363862303463333138313963633531373465646264623232-->
?
La méthode **récursive** prédit un pas puis réutilise cette prédiction pour avancer. Elle peut accumuler ses erreurs. Une méthode **directe** apprend une cible pour chaque horizon, éventuellement avec un modèle commun produisant plusieurs sorties.

La seconde évite certaines rétroactions mais peut demander plus de données ou produire des horizons peu cohérents entre eux. Le backtest doit reproduire la stratégie réelle : alimenter une prévision récursive avec les vraies valeurs intermédiaires futures donnerait un résultat trop optimiste.

---

Comment éviter une fuite de cible dans des moyennes mobiles utilisées pour prévoir ? <!--anki:6162386661656532323330613437376461343133663735326131383838623564-->
?
Construire chaque agrégat uniquement avec des **observations disponibles avant la décision**. Pour prévoir la valeur du jour avant son observation, une moyenne incluant cette valeur fuit la cible ; une fenêtre centrée peut aussi incorporer le futur.

Dans un tableau supervisé, décaler la cible avant de calculer la fenêtre est une protection fréquente, à adapter à l'horizon et au délai de collecte. Traiter chaque série séparément. Vérifier quelques lignes à la main, y compris début de série, trous et changements de fréquence.

---

Calcul : quel MASE pour une MAE de test de 12 et une erreur saisonnière naïve moyenne de 20 sur le train ? <!--anki:3561323334396265623030333435336162663932656365306662343464343838-->
?
Le **MASE** rapporte l'erreur absolue de test à une échelle calculée sur les différences naïves du train : **12 / 20 = 0,6**. Le dénominateur doit utiliser la saisonnalité retenue et uniquement le train.

Ce score facilite certaines comparaisons entre séries d'échelles différentes. Il ne prouve pas que le modèle bat la baseline sur cette période de test : il faut aussi y évaluer la baseline. Si le train est constant, le dénominateur peut être nul. La MAPE, elle, pose problème avec des valeurs réelles nulles ou proches de zéro.

---

Calcul : quelle perte pinball au quantile 0,9 pour une cible de 100 et des prévisions de 80 puis 120 ? <!--anki:3663373637343666656130653437386561373266386264313839303930613365-->
?
Pour `u = cible − prévision`, la perte vaut `max(αu, (α−1)u)` :
```text
Sous-prévision de 20 : 0,9 × 20 = 18
Sur-prévision de 20  : 0,1 × 20 = 2
```
Le quantile élevé pénalise davantage la sous-prévision. Choisir α selon la décision et le coût asymétrique, puis vérifier les fréquences de dépassement. Une prévision au quantile 0,9 n'est pas une moyenne augmentée arbitrairement de 10 % et ne garantit pas une couverture identique dans chaque segment.

---

Comment évaluer un intervalle de prévision à 90 % ? <!--anki:3338646162346561396133623437363039336565343761306533316638636330-->
?
Mesurer sa **couverture empirique** et sa **largeur**, par horizon et segment. Un intervalle immense peut couvrir presque toutes les observations sans aider à planifier ; un intervalle trop étroit masque l'incertitude.

Comparer sur des périodes successives avec assez d'observations, en tenant compte de leur dépendance. Examiner les ruptures de régime et les hypothèses sur les variables futures. L'intervalle vise les futures observations, pas seulement l'incertitude sur une moyenne estimée. Un taux global de 90 % ne garantit pas la couverture de chaque magasin.

---

Pourquoi réconcilier les prévisions d'une hiérarchie de séries ? <!--anki:6431303330386462666633343464353861633332363433653861363165306631-->
?
Des prévisions séparées par magasin et au niveau national peuvent donner des **totaux incompatibles**. La réconciliation impose une cohérence avec la structure d'agrégation, en tenant compte de la méthode et, selon l'approche, des erreurs historiques.

Vérifier les contraintes métier, notamment non-négativité et changements de périmètre. La cohérence ne garantit pas une meilleure précision à tous les niveaux. Les quantiles ne s'additionnent généralement pas : le quantile 90 % du total dépend aussi de la dépendance entre les composantes.

---

## Mises en situation

Mise en situation : ton modèle prédit très bien à un jour, mais échoue pour le planning à quatre semaines. Que changes-tu ? <!--anki:6635623432376633633662643431663362353630316232346361666163333738-->
?
1. **Redéfinir la cible opérationnelle** : horizons et agrégation utilisés par le planning.
2. **Rejouer un backtest multi-horizon** aux dates où les décisions étaient prises.
3. **Vérifier les variables futures**, en distinguant prévisions disponibles et observations réalisées.
4. **Comparer direct et récursif** à une baseline saisonnière aux mêmes horizons.
5. **Rapporter erreurs et intervalles** par horizon, puis le coût des décisions obtenues.

**Piège** : présenter la métrique à un jour comme preuve de qualité à un mois.

---

Mise en situation : une prévision utilise les ventes du jour pour calculer sa moyenne mobile, alors qu'elle doit être produite à 8 h. Que vérifies-tu ? <!--anki:3965323464633135383833623438306538663536326537376133656331616332-->
?
1. **Tracer l'heure réelle de disponibilité** de chaque variable et correction.
2. **Recalculer les agrégats** en excluant les ventes encore inconnues à 8 h.
3. **Reconstruire le backtest historique** avec les données alors disponibles.
4. **Comparer la baisse de score** et revoir les conclusions de l'expérience précédente.
5. **Ajouter un contrôle temporel** sur les variables servies en production.

**Piège** : garder le score historique obtenu grâce à la fuite pour annoncer la performance attendue.

---

Mise en situation : la demande devient très intermittente et la MAPE explose malgré de faibles erreurs en unités. Comment évalues-tu ? <!--anki:3562613738616666343763363461386238393462313232393534653830386263-->
?
1. **Examiner les zéros**, ruptures de stock et mécanismes de collecte.
2. **Choisir des métriques définies** sur ces cas, avec MAE et coût métier.
3. **Vérifier le dénominateur du MASE** si cette métrique est utilisée.
4. **Comparer des références adaptées** à l'intermittence et à l'horizon de décision.
5. **Évaluer agrégats et quantiles** selon les besoins de réapprovisionnement.

**Piège** : retirer les périodes à zéro du test puis annoncer un gain global.

---

## Sources
- [Hyndman & Athanasopoulos — prévisions simples](https://otexts.com/fpp3/simple-methods.html)
- [Hyndman & Athanasopoulos — validation temporelle](https://otexts.com/fpp3/tscv.html)
- [Hyndman & Athanasopoulos — métriques et MASE](https://otexts.com/fpp3/accuracy.html)
- [Hyndman & Athanasopoulos — variables futures](https://otexts.com/fpp3/forecasting-regression.html)
- [Hyndman & Athanasopoulos — ARIMA et ETS](https://otexts.com/fpp3/arima-ets.html)
- [Hyndman & Athanasopoulos — intervalles de prévision](https://otexts.com/fpp3/prediction-intervals.html)
- [Hyndman & Athanasopoulos — réconciliation](https://otexts.com/fpp3/reconciliation.html)
- [scikit-learn — variables retardées et validation](https://scikit-learn.org/stable/auto_examples/applications/plot_time_series_lagged_features.html)
- [scikit-learn — perte pinball](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.mean_pinball_loss.html)

## Connexions
- [[171-choisir-modele-ml|Choisir un modèle]] — construire les baselines prédictives
- [[172-validation-metriques-ml|Validation ML]] — comparer sans utiliser le futur
- [[159-donnees-temporelles-features|Données temporelles]] — reconstruire les informations disponibles
- [[176-detection-anomalies|Détection d'anomalies]] — détecter les écarts à une dynamique attendue
- [[00-moc-ai-engineering|MOC AI Engineering]]
