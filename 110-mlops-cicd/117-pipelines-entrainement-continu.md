# Pipelines d'entraînement, registre & entraînement continu — Flashcards
Tags: #flashcards #ai-engineering #mlops #ml-classique #pipelines
Vérifié le : 20 octobre 2026 — cette fiche cite des produits et versions qui évoluent vite.
<!-- summary: niveaux de maturité MLOps, pipeline déployé plutôt que modèle, réentraînement planifié ou déclenché, validation des données et du modèle, suivi d'expériences MLflow, signature, alias champion et challenger, alias de registre ou de fournisseur, cache des étapes, fenêtre d'entraînement, scoring batch ou en ligne, labels censurés par le modèle, calcul de performance attendue sans labels. -->


Que distinguent les niveaux 0, 1 et 2 de maturité MLOps décrits par Google Cloud ? <!--anki:6539373632343731336431643433643839373035386566393038353034396538-->
?
- **Niveau 0** : étapes manuelles, souvent en notebook ; le modèle entraîné est remis à l'équipe qui le sert. Releases rares, sans CI/CD ni suivi de la qualité.
- **Niveau 1** : un **pipeline automatisé** réentraîne le modèle sur de nouvelles données (*continuous training*), avec validation des données et du modèle et métadonnées d'exécution.
- **Niveau 2** : une **CI/CD des composants du pipeline** teste et livre rapidement leurs nouvelles versions.

Ces niveaux mesurent l'automatisation, pas la pertinence du modèle. Viser celui qui correspond à la fréquence réelle des changements : un modèle revu deux fois par an ne justifie pas le niveau 2.

---

Au niveau 1 de maturité MLOps, que déploie-t-on, et pourquoi ce changement compte-t-il ? <!--anki:6239633566363762336266323431363162663234636131653537623737316334-->
?
On déploie le **pipeline d'entraînement** lui-même, qui s'exécute de façon récurrente et produit les modèles servis, et non plus un fichier de modèle entraîné à la main.

Le code du pipeline devient alors un logiciel de production : il se teste, se versionne et se relit. Chaque modèle produit doit être relié à l'exécution qui l'a créé : version du pipeline, snapshot des données, paramètres et résultats de validation. Si un modèle régresse, on corrige le pipeline ou ses données. Un réentraînement « rapide » lancé hors du pipeline recrée un artefact que personne ne sait reproduire ([[111-mlops-llmops-fondamentaux|lineage]]).

---

Quand préférer un réentraînement planifié à un réentraînement déclenché par une alerte ? <!--anki:3730363132663964323961313461646138663763373962333639643165643037-->
?
Le **planifié** convient quand des labels mûrs arrivent régulièrement, que l'entraînement coûte peu et que le pipeline est déjà validé. Exemple : une prévision de demande réentraînée chaque semaine sur les ventes de la semaine écoulée.

Le **déclenché** convient quand l'entraînement est coûteux ou que les labels sont rares : baisse de performance mesurée, dérive confirmée, nouvelle catégorie. Dans les deux cas, le déclencheur lance le pipeline, pas le déploiement : la promotion dépend d'un contrôle du candidat face au modèle en place. Une alerte de dérive peut aussi révéler un incident de données qu'un réentraînement apprendrait fidèlement ([[113-monitoring-drift-feedback|quand réentraîner]]).

---

Que vérifie la validation des données au début d'un pipeline de réentraînement automatique ? <!--anki:6439393237356164613533323463643762623336316662383761356533393561-->
?
- **Écarts de schéma** : colonne absente, type changé, catégorie inconnue. Ce sont des anomalies d'entrée : le pipeline s'arrête.
- **Écarts de valeurs** : distributions qui bougent, à signaler et à confronter aux changements connus.
- **Volume, valeurs manquantes et fraîcheur** de chaque source.
- **Maturité des labels** : une période trop récente contient de faux négatifs ([[159-donnees-temporelles-features|labels retardés]]).

Sans cette étape, un pipeline automatique apprend un incident comme une nouvelle norme. Si une source passe des euros aux centimes, le modèle réentraîné intègre ce facteur 100 et la validation du modèle, calculée sur les mêmes données, peut ne rien voir ([[157-contrats-qualite-donnees|contrats de données]]).

---

Quels contrôles un modèle réentraîné doit-il passer avant de remplacer le modèle en production ? <!--anki:6639353939333063383366353465373861613231323564396266613433386230-->
?
- **Métrique principale** sur le même jeu de test que le modèle en place, avec un gain supérieur au bruit ([[99-statistiques-decisions-experimentales|comparaison appariée]])
- **Segments critiques** : aucune régression au-delà d'une tolérance fixée à l'avance
- **Calibration**, si les probabilités servent à décider ([[173-calibration-incertitude-abstention|calibration]])
- **Compatibilité de service** : signature, latence p95, mémoire, chargement réel dans l'image de serving

Si un contrôle échoue, le modèle en place reste servi et le pipeline alerte. Ce découplage protège d'un réentraînement automatique sur des données dégradées. Garder aussi un jeu de test de référence figé : un test tiré de la même fenêtre que l'entraînement partage ses défauts.

---

Que faut-il enregistrer dans un run de suivi d'expériences pour qu'un score soit comparable et reproductible ? <!--anki:3530323230313931666636393436326239373363626566646335356361653532-->
?
```python
with mlflow.start_run(run_name="gbm-fraude"):
    mlflow.log_params({"max_depth": 6, "seed": 42, "git_sha": sha,
                       "train_snapshot": "fraude@2026-10-01"})
    pipeline.fit(X_train, y_train)
    mlflow.log_metrics({"auc_pr_valid": auc_pr, "rappel_gros_montants": rappel_gm})
    mlflow.sklearn.log_model(pipeline, "model", signature=signature)
```
Le run doit relier le score à ce qui l'a produit : **hyperparamètres et graine**, **commit du code**, **identifiant du snapshot** d'entraînement et de validation, **métriques par segment**, et le modèle avec son prétraitement.

`mlflow.autolog()` capture les paramètres et métriques du framework, mais ni la version des données ni les segments métier : il faut les ajouter. Deux runs sans snapshot identifié ne se comparent pas, même avec un code identique.

---

À quoi sert la signature d'un modèle enregistré dans MLflow, et que ne vérifie-t-elle pas ? <!--anki:6239663931636263656563383439313061333262393861346664663238353164-->
?
La **signature** décrit les entrées, les sorties et les paramètres d'inférence attendus : noms, types et formes. Elle se calcule avec `infer_signature(X_valid, pipeline.predict(X_valid))`, ou à partir d'un `input_example`. Au chargement en pyfunc ou en service REST, MLflow valide les entrées : une colonne requise absente fait échouer l'appel, un `int` peut devenir `double`, mais une chaîne n'est pas convertie en entier.

Elle contrôle la forme, pas le sens. Un montant envoyé en centimes au lieu d'euros passe la validation. Piège classique : une colonne entière qui contient des valeurs manquantes devient flottante et ne respecte plus la signature ; la déclarer `double` dès l'entraînement.

---

Comment promouvoir un modèle avec les alias du registre MLflow plutôt qu'avec les stages ? <!--anki:6237353965653432306163353464366462386232306536656232646136313965-->
?
Depuis MLflow 2.9, les **stages** (`Staging`, `Production`, `Archived`) sont dépréciés. Un **alias** est une référence nommée et modifiable vers une version : le service charge `models:/fraude@champion`, et la promotion consiste à déplacer l'alias.
```python
client = MlflowClient()
client.set_registered_model_alias("fraude", "champion", 8)
modele = mlflow.pyfunc.load_model("models:/fraude@champion")
```
Le rollback replace l'alias sur la version 7. Un service qui a chargé le modèle au démarrage garde cependant l'ancienne version jusqu'à son rechargement : prévoir ce rechargement et journaliser la **version résolue**, pas l'alias. Des tags comme `validation_status=approved` consignent les décisions.

---

À ne pas confondre : alias `champion` d'un registre de modèles et alias de modèle chez un fournisseur d'API ? <!--anki:3665306137636438626664313435393061633835316532633665333930616563-->
?
Les deux sont des **références modifiables**. La différence tient à qui les déplace, et quand.
- L'**alias de registre** est déplacé par ton pipeline, après tes contrôles. Le changement est tracé, daté et réversible.
- L'**alias du fournisseur** peut changer de cible à sa discrétion, sans commit ni validation chez toi ([[113-monitoring-drift-feedback|mises à jour des modèles API]]).

Le premier est un mécanisme de promotion ; le second est une dépendance à épingler. Dans les deux cas, enregistrer avec chaque prédiction la version effectivement utilisée, sans quoi une régression ne peut pas être attribuée.

---

Pourquoi le cache des étapes d'un pipeline ML peut-il entraîner un modèle sur des données périmées ? <!--anki:3037633031353233366638363432623838343764343563303136666137613632-->
?
Des orchestrateurs comme Kubeflow Pipelines **réutilisent la sortie d'une étape** déjà exécutée avec les mêmes entrées et paramètres ; ce cache y est activé par défaut. Si l'étape reçoit le chemin `s3://data/fraude/latest/`, ce paramètre ne change pas quand le contenu change : l'étape est sautée et l'ancien dataset est réutilisé.

Passer en entrée un **identifiant immuable** : partition datée, version de table ou empreinte du manifeste ([[150-013-orchestration-pipelines-donnees|références de datasets]]). Désactiver le cache des étapes qui lisent une source externe, avec `.set_caching_options(enable_caching=False)` dans KFP. Le cache reste utile pour les étapes déterministes et coûteuses.

---

Comment choisir la fenêtre de données d'un réentraînement périodique ? <!--anki:3462653933633538646637613430653762333939313035373962633831633332-->
?
- **Fenêtre glissante**, par exemple les 12 derniers mois : suit les changements, mais oublie les régimes anciens.
- **Fenêtre cumulative** : plus d'exemples, mais conserve des comportements périmés.
- **Pondération décroissante** des anciens exemples : compromis entre les deux.

Couvrir au moins un cycle saisonnier complet si la cible en dépend. Comparer les fenêtres candidates par backtest sur plusieurs origines successives ([[172-validation-metriques-ml|validation temporelle]]). Une fenêtre courte réagit vite mais peut contenir trop peu de positifs rares, comme les fraudes. La durée de conservation autorisée des données personnelles peut aussi plafonner l'historique.

---

À ne pas confondre : scoring batch et scoring en ligne d'un modèle tabulaire ? <!--anki:3835666466363632393961653434633861313331316236373735636166633733-->
?
- **Batch** : les scores sont précalculés périodiquement, par exemple chaque nuit pour deux millions de clients, puis écrits avec la version du modèle et l'heure de calcul. C'est simple et peu coûteux, mais le score reste figé jusqu'au lot suivant.
- **En ligne** : le score est calculé à la requête, avec des variables fraîches et un budget de latence, par exemple 50 ms au p99. Il faut une infrastructure de service et des variables disponibles en ligne ([[159-donnees-temporelles-features|features online]]).

Critère : la décision dépend-elle d'une information qui change entre deux lots, comme le montant d'une transaction en cours ? Si oui, le batch ne suffit pas.

---

Pourquoi un modèle anti-fraude qui bloque des transactions prive-t-il son successeur de labels fiables ? <!--anki:6331303431373561386338633430313738336436343962343634396137383666-->
?
Une transaction bloquée ne produit jamais d'issue observable : on ne saura pas si elle aurait donné lieu à un impayé. Seules les transactions acceptées reçoivent un label. C'est le problème des **labels sélectifs** : le modèle en place décide quelles données d'évaluation existeront.

Un successeur entraîné et évalué sur ces seules données apprend une population filtrée, et son rappel sur les cas bloqués reste inconnu. Parades : faire revoir par des enquêteurs un échantillon aléatoire des blocages, conserver scores et décisions avec la version du modèle, et pondérer par la probabilité d'acceptation. Les journaux d'un recommender posent le même problème ([[174-recommandation-ranking|biais d'exposition]]).

---

Calcul : un modèle calibré évalue 100 000 transactions. La somme de toutes ses probabilités vaut 1 000 ; il en signale 2 000, de probabilité moyenne 0,35. Quelles précision et quel rappel attendre avant l'arrivée des labels ? <!--anki:6237633638313538633537333463346261373964633536353431323132653364-->
?
Si les probabilités restent calibrées, le nombre attendu de fraudes parmi les signalements est la somme de leurs probabilités : 2 000 × 0,35 = **700**.
- Précision attendue : 700 / 2 000 = **35 %**.
- Rappel attendu : 700 / 1 000 = **70 %**, car 1 000 est le nombre attendu de fraudes sur l'ensemble.

Hypothèse : la relation entre variables et fraude n'a pas changé. L'estimation tient sous une dérive des entrées, pas sous une dérive de concept : un nouveau mode de fraude, mal noté, ferait chuter le rappel réel sans changer l'estimation. C'est une alerte précoce, à confirmer avec les labels consolidés.

---

## Mises en situation

Mise en situation : un modèle de churn est réentraîné chaque semaine par un notebook lancé à la main, et personne ne sait reproduire la version en production. Comment le passes-tu au niveau 1 sans tout réécrire ? <!--anki:6136386535333361656532623434353639343966373363373966373433356132-->
?
1. **Mesurer la version actuelle** sur un jeu de test figé : elle devient la référence, même si son lineage est perdu.
2. **Extraire les étapes du notebook** en composants : validation des données, features, entraînement, évaluation, avec un snapshot immuable en entrée.
3. **Tracer chaque exécution** : run de suivi d'expériences, version enregistrée dans le registre, alias `champion` pour la version servie.
4. **Ajouter le contrôle de promotion** : comparaison au champion sur des cohortes aux labels mûrs, par segment.
5. **Planifier le pipeline** et garder la promotion manuelle tant que les contrôles n'ont pas fait leurs preuves.

**Piège** : automatiser le déploiement avant d'avoir une validation des données et du modèle fiable.

---

Mise en situation : une alerte de dérive déclenche un réentraînement automatique, le nouveau modèle est promu et le taux de faux positifs double. Que s'est-il passé, et que changes-tu ? <!--anki:6262336333663362303734653438666661643333663261333665326134373762-->
?
1. **Revenir en arrière** : replacer l'alias sur la version précédente et vérifier que les services l'ont rechargée.
2. **Chercher un incident de données** derrière la dérive : unité, jointure, source manquante ([[157-contrats-qualite-donnees|dérive ou incident]]).
3. **Examiner le contrôle de promotion** : un test tiré de la même fenêtre corrompue valide un modèle corrompu.
4. **Renforcer le pipeline** : validation des données bloquante, jeu de référence figé, seuils par segment.
5. **Découpler déclenchement et promotion** : passer par une comparaison en shadow ou un canary avant la bascule.

**Piège** : traiter chaque alerte de dérive comme un ordre de réentraîner.

---

Mise en situation : un challenger anti-fraude gagne 3 points de précision en backtest, mais il a été entraîné et évalué uniquement sur les transactions acceptées par le champion. Le déploies-tu ? <!--anki:3063653432316631653734323433623761303564353037653962653835336561-->
?
1. **Reconnaître les labels sélectifs** : le backtest ignore les transactions que le champion a bloquées.
2. **Évaluer sur un échantillon non filtré** : blocages revus par des enquêteurs, tirés au hasard.
3. **Scorer en shadow** sur le trafic réel : recouvrement des signalements, volume d'alertes face à la capacité d'enquête.
4. **Lancer un canary limité** avec des métriques garde-fous : impayés, plaintes clients, file d'enquête ([[112-cicd-modeles|déploiement progressif]]).
5. **Décider après la fenêtre de maturation** des impayés, sur des cohortes comparables.

**Piège** : comparer deux modèles sur des labels produits par l'un d'eux.

---

## Sources
- [Google Cloud — MLOps : livraison continue et pipelines d'automatisation en ML](https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning)
- [MLflow — workflow du Model Registry, alias et dépréciation des stages](https://mlflow.org/docs/latest/ml/model-registry/workflow/)
- [MLflow — signatures de modèles et validation des entrées](https://mlflow.org/docs/latest/ml/model/signatures/)
- [Kubeflow Pipelines — cache des exécutions](https://www.kubeflow.org/docs/components/pipelines/user-guides/core-functions/caching/)
- [Lakkaraju et al., The Selective Labels Problem, KDD 2017](https://pmc.ncbi.nlm.nih.gov/articles/PMC5958915)

## Connexions
- [[111-mlops-llmops-fondamentaux|MLOps & LLMOps — Fondamentaux]] — registre, lineage et versionnage appliqués ici au ML classique
- [[112-cicd-modeles|CI/CD des modèles]] — shadow, canary et rollback d'un modèle promu par le pipeline
- [[113-monitoring-drift-feedback|Monitoring, drift & boucle de feedback]] — les signaux qui déclenchent le pipeline
- [[157-contrats-qualite-donnees|Contrats & qualité des données]] — distinguer dérive réelle et incident avant de réentraîner
- [[159-donnees-temporelles-features|Données temporelles]] — maturité des labels et variables en ligne
- [[150-013-orchestration-pipelines-donnees|Orchestration data]] — entrées immuables, reprises et intervalles de données
- [[172-validation-metriques-ml|Validation ML]] — backtest et validation temporelle des fenêtres
- [[173-calibration-incertitude-abstention|Calibration]] — condition de l'estimation de performance sans labels
- [[174-recommandation-ranking|Recommandation & ranking]] — biais d'exposition, cousin des labels sélectifs
- [[99-statistiques-decisions-experimentales|Statistiques pour décider]] — gain significatif face au champion
- [[00-moc-ai-engineering|MOC AI Engineering]]
