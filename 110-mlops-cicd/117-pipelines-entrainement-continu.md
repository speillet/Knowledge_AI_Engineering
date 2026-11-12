# Pipelines d'entraînement, registre & entraînement continu — Flashcards
Tags: #flashcards #ai-engineering #mlops #ml-classique #pipelines
Vérifié le : 20 octobre 2026 — date globale conservée ; revue ciblée du 13 novembre 2026 détaillée dans les Sources.
<!-- summary: niveaux de maturité MLOps, pipeline déployé plutôt que modèle, réentraînement planifié ou déclenché, validation des données et du modèle, suivi d'expériences MLflow, signature, alias champion et challenger, alias de registre ou de fournisseur, cache des étapes, fenêtre d'entraînement, scoring batch ou en ligne, labels censurés par le modèle, calcul de performance attendue sans labels, promotions concurrentes des modèles, regroupement des déclencheurs, calibrateur versionné, référence historique et cohorte récente, correction des labels. -->


Que distinguent les niveaux 0, 1 et 2 de maturité MLOps décrits par Google Cloud ? <!--anki:6539373632343731336431643433643839373035386566393038353034396538-->
?
- **Niveau 0** : étapes manuelles, souvent en notebook ; le modèle entraîné est transmis à l'équipe qui le sert. La validation peut exister sans automatisation ni suivi continu.
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
Contrôler **schéma, sémantique, volume, fraîcheur et disponibilité historique** des variables, ainsi que maturité, définition et couverture des labels. Comparer les règles de validation à l'usage prévu par le modèle.

Une catégorie nouvelle n'impose pas toujours l'arrêt : le contrat peut prévoir un traitement de l'inconnu testé, avec seuil d'alerte. Une unité changée ou une clé incohérente peut en revanche bloquer la publication. Classer les anomalies en erreur bloquante, quarantaine ou signal à examiner, avec responsable et règle explicite. Valider les mêmes données corrompues dans train et test peut donner un score rassurant ; conserver des invariants indépendants et des références métier.

---

Quels contrôles un modèle réentraîné doit-il passer avant de remplacer le modèle en production ? <!--anki:6639353939333063383366353465373861613231323564396266613433386230-->
?
Comparer **candidat et référence** sur des jeux indépendants de leur sélection, avec critères fixés avant l'essai : qualité utile, segments, calibration, contraintes métier, coût et service. Une marge de non-infériorité peut convenir à un candidat moins coûteux.

Tester chargement du paquet, prétraitement, signature et sorties dans l'image cible ; mesurer latence et mémoire au trafic visé. Associer référence historique et cohorte récente aux labels suffisamment mûrs. L'échec d'une gate conserve la version en place et ouvre une investigation. Le pipeline produit un candidat ; une fin d'entraînement sans erreur ne constitue ni approbation ni preuve que les réplicas servent la bonne version.

---

Que faut-il enregistrer dans un run de suivi d'expériences pour qu'un score soit comparable et reproductible ? <!--anki:3530323230313931666636393436326239373363626566646335356361653532-->
?
Relier **recette, données, environnement et résultats**, en distinguant entraînement, validation de sélection et test final. Conserver métriques par segment et artefact avec son prétraitement.
```python
# MLflow 3 ; pipeline déjà configuré, dont ses random_state.
import mlflow
import mlflow.sklearn
from mlflow.models import infer_signature
from sklearn.metrics import recall_score

with mlflow.start_run(run_name="retention-gbm"):
    mlflow.log_params({"seed": 42, "git_sha": sha,
                       "train_snapshot": "retention@s042"})
    pipeline.fit(X_train, y_train)
    pred = pipeline.predict(X_valid)
    mlflow.log_metric("rappel_validation", recall_score(y_valid, pred))
    signature = infer_signature(X_valid, pred)
    info = mlflow.sklearn.log_model(
        pipeline, name="model", signature=signature,
        input_example=X_valid.head(2),
    )
```
Journaliser une seed ne configure pas les générateurs. La capture automatique dépend de l'intégration et de sa configuration ; elle peut inclure certaines données sans remplacer leur provenance métier. Compléter snapshots, splits, définition du label et dépendances. Utiliser l'URI retournée par la journalisation plutôt que supposer un ancien emplacement de fichier.

---

À quoi sert la signature d'un modèle enregistré dans MLflow, et que ne vérifie-t-elle pas ? <!--anki:6239663931636263656563383439313061333262393861346664663238353164-->
?
La **signature MLflow** décrit un contrat de noms, types, formes et paramètres ; un exemple d'entrée aide à le documenter et à tester l'inférence. Le chemin de chargement ou de serving et le flavor déterminent les validations effectivement appliquées.

Cela ne démontre ni sens des unités, ni qualité, ni validité de toutes les sorties métier. Tester champs absents, valeurs nulles, catégories inconnues, ordre et types avec le paquet rechargé. L'inférence depuis un seul exemple peut manquer un cas important : une colonne entière devenue flottante à cause de valeurs manquantes mérite un choix de schéma réfléchi, pas un cast aveugle masquant l'erreur.

---

Comment promouvoir un modèle avec les alias du registre MLflow plutôt qu'avec les stages ? <!--anki:6237353965653432306163353464366462386232306536656232646136313965-->
?
Un **alias MLflow** est une référence mutable vers une version enregistrée ; les anciens stages sont dépréciés depuis MLflow 2.9. Après validation, une autorité contrôlée peut déplacer cet alias :
```python
from mlflow import MlflowClient
client = MlflowClient()
client.set_registered_model_alias("retention", "champion", "8")
```
L'opération modifie une référence, pas tous les processus qui ont déjà chargé un modèle. Résoudre la version, charger ou déployer explicitement puis vérifier les réplicas. Journaliser version et release effectives ; un tag d'approbation n'accorde pas de droits. Sérialiser les promotions concurrentes et conserver une preuve de validation indépendante de l'alias courant.

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
Le **cache d'exécution** peut réutiliser une sortie quand la clé calculée à partir des entrées et paramètres paraît inchangée. Dans Kubeflow Pipelines, il est activé par défaut mais configurable à la compilation, à l'exécution ou par tâche.

Un chemin mutable comme `s3://data/fraude/latest/` peut rester identique alors que son contenu change : une étape peut réutiliser un ancien dataset. Fournir snapshot ou manifeste immuable et expliciter les dépendances. Pour une tâche qui doit relire une source externe, désactiver son cache, par exemple `.set_caching_options(enable_caching=False)`. Vérifier aussi les overrides du run ; un réglage dans le code ne prouve pas le comportement de l'exécution effectivement lancée.

---

Comment choisir la fenêtre de données d'un réentraînement périodique ? <!--anki:3462653933633538646637613430653762333939313035373962633831633332-->
?
Comparer **fenêtre glissante, historique cumulatif et pondération décroissante** par [[172-validation-metriques-ml|backtest temporel]]. Le choix échange adaptation aux changements, couverture saisonnière et nombre d'événements rares.

Exemple : une fenêtre de trois mois réagit vite mais peut manquer les achats de fin d'année ; douze mois les couvrent, tout en conservant un ancien régime tarifaire. Aucune des deux ne gagne par principe.

Vérifier que les labels sont disponibles à chaque origine du backtest, pas seulement que les observations sont anciennes. Couvrir les régimes utiles dans la limite de conservation autorisée ; après rupture structurelle, pondérer ou exclure l'ancien régime peut être préférable à accumuler davantage de données.

---

À ne pas confondre : scoring batch et scoring en ligne d'un modèle tabulaire ? <!--anki:3835666466363632393961653434633861313331316236373735636166633733-->
?
- **Batch** : les scores sont précalculés périodiquement, par exemple chaque nuit pour deux millions de clients, puis écrits avec la version du modèle et l'heure de calcul. C'est simple et peu coûteux, mais le score reste figé jusqu'au lot suivant.
- **En ligne** : le score est calculé à la requête, avec des variables fraîches et un budget de latence, par exemple 50 ms au p99. Il faut une infrastructure de service et des variables disponibles en ligne ([[159-donnees-temporelles-features|features online]]).

Critère : la décision dépend-elle d'une information qui change entre deux lots, comme le montant d'une transaction en cours ? Si oui, le batch ne suffit pas.

---

Pourquoi un modèle anti-fraude qui bloque des transactions prive-t-il son successeur de labels fiables ? <!--anki:6331303431373561386338633430313738336436343962343634396137383666-->
?
Quand une décision détermine **quelles issues deviennent observables**, les labels sont sélectifs. Évaluer seulement les transactions acceptées décrit cette population filtrée ; cela ne révèle pas automatiquement le résultat qu'auraient eu les transactions bloquées.

Une revue indépendante peut fournir un autre label ou des indices utiles, sans être nécessairement l'issue contrefactuelle recherchée. Documenter la politique d'observation et les hypothèses d'une collecte ou analyse adaptée. Une pondération exige probabilités d'observation connues ou estimables et recouvrement : si certains cas n'ont aucune chance d'être observés, elle ne crée pas l'information absente. Conserver limites et populations couvertes avant de promouvoir un successeur.

---

Calcul : un modèle calibré évalue 100 000 transactions. La somme de toutes ses probabilités vaut 1 000 ; il en signale 2 000, de probabilité moyenne 0,35. Quelles précision et quel rappel attendre avant l'arrivée des labels ? <!--anki:6237633638313538633537333463346261373964633536353431323132653364-->
?
Si les probabilités restent fiables **dans les groupes considérés**, leurs sommes donnent des effectifs attendus :
```text
fraudes attendues signalées = 2 000 × 0,35 = 700
précision estimée = 700/2 000 = 35 %
ratio estimé pour le rappel = 700/1 000 = 70 %
```
Le dernier chiffre est un **ratio d'effectifs attendus**, pas une identité générale pour l'espérance du rappel observé. Ces estimations ne remplacent pas les labels. La calibration globale peut masquer des segments mal calibrés et ne survit pas automatiquement à une dérive d'entrées. Vérifier sélection, population et définition du label, puis confirmer sur des cohortes consolidées avec incertitude.

---

Pourquoi un pipeline de réentraînement doit-il empêcher deux candidats concurrents de se promouvoir simultanément ? <!--anki:3263663864393330636534653433386561653262663231393031643637376462-->
?
Deux **runs de promotion** peuvent tous deux comparer leur candidat au même ancien champion, puis remplacer l'alias dans un ordre arbitraire. Le dernier écrit n'est pas nécessairement le meilleur validé.

Sérialiser la promotion ou utiliser une mise à jour conditionnelle sur la version attendue du champion. Si celle-ci a changé, refaire la décision selon le protocole prévu. Conserver candidat, référence, critères et approbation dans un journal. L'alias du registre est un pointeur de déploiement ; sa simplicité ne fournit pas à elle seule un arbitrage entre expériences concurrentes.

---

Comment éviter qu'une rafale d'alertes lance trop de réentraînements simultanés ? <!--anki:3735376337636234366261643436336438666436383539303030636466363666-->
?
Un **déclencheur** peut recevoir plusieurs événements pour une même dérive ou fenêtre. Sans regroupement, il produit des entraînements concurrents, consomme le budget et multiplie les candidats difficiles à arbitrer.

Définir une identité logique de demande, une règle de regroupement, une période de stabilisation et une concurrence maximale. Vérifier maturité des données et coût avant lancement. Conserver les signaux regroupés pour l'enquête ; une temporisation ne doit pas cacher un incident critique. La protection du déclenchement complète, sans la remplacer, la sérialisation de la promotion : limiter les entraînements ne décide pas quel candidat sera servi.

---

Pourquoi le calibrateur doit-il être intégré à la recette et à la promotion d'un modèle ? <!--anki:3166353763353636393139323430393162396232366330393366643063363832-->
?
Un **calibrateur** appris sur les scores d'un modèle donné ne reste pas automatiquement valide après réentraînement des poids. Les probabilités et les décisions prises à partir d'elles peuvent changer même si le classement s'améliore.

Prévoir données d'ajustement distinctes selon le protocole, versionner modèle et calibrateur ensemble, puis évaluer la combinaison sur un jeu indépendant. Tester aussi le seuil et la capacité de revue résultante. Ne pas ajuster la calibration sur le test final pour réussir la gate. Une promotion doit identifier la chaîne réellement utilisée, pas seulement un modèle principal accompagné d'un fichier « calibrateur courant » mutable.

---

Pourquoi garder une référence historique et une cohorte récente dans la validation d'un réentraînement ? <!--anki:3838303336333435393930633465323138396133616264373736333963373363-->
?
La **référence historique** suit des régressions connues ; la **cohorte récente** renseigne sur la population actuelle, si ses labels sont suffisamment mûrs. L'une ne remplace pas l'autre.

Comparer candidat et champion sur les mêmes cas de chaque jeu, avec critères préspécifiés et incertitude. Un bon score historique peut manquer un nouveau régime ; une fenêtre récente seule peut partager un incident de collecte et oublier des situations saisonnières. Versionner composition et règles d'éligibilité. Lorsque la cible évolue, documenter la portée des comparaisons au lieu de présenter toute variation comme une amélioration du modèle à objectif constant.

---

Comment traiter une correction de labels après l'approbation d'un modèle ? <!--anki:3036313832353639623031303437323039663333303933303166366661643731-->
?
Une **correction de labels** modifie les preuves qui ont soutenu la décision. Conserver le rapport historique et créer une nouvelle version du dataset corrigé, avec provenance, date et périmètre des changements.

Recalculer les comparaisons nécessaires sur cette version et examiner si la promotion ou le seuil restent justifiés. Ne pas remplacer silencieusement les métriques de l'ancien run : l'audit doit retrouver ce qui était connu au moment de la décision. Si la correction révèle un défaut systématique, revoir collecte, annotation et futurs entraînements. Une nouvelle donnée peut déclencher une investigation sans imposer automatiquement le retrait du modèle.

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
1. **Définir la population cible** et l'issue réellement évaluée : détection d'un indice, impayé observé ou effet d'une décision.
2. **Identifier les labels manquants par construction**, notamment les cas systématiquement bloqués.
3. **Étudier une collecte ou un plan d'analyse adapté** avec ses hypothèses ; une revue humaine n'est pas automatiquement l'issue contrefactuelle.
4. **Utiliser le shadow pour les contrats et volumes**, sans lui attribuer des labels qu'il ne produit pas.
5. **Décider dans le périmètre étayé**, après contrôle de risques, délais de labels et métriques métier.

**Piège** : annoncer un gain généralisable de trois points sur une population filtrée, ou croire qu'une pondération répare une absence totale de recouvrement.

---

## Sources
- [Google Cloud — MLOps : livraison continue et pipelines d'automatisation en ML](https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning)
- [MLflow — workflow du Model Registry, alias et dépréciation des stages](https://mlflow.org/docs/latest/ml/model-registry/workflow/)
- [MLflow — signatures de modèles et validation des entrées](https://mlflow.org/docs/latest/ml/model/signatures/)
- [Kubeflow Pipelines — cache des exécutions](https://www.kubeflow.org/docs/components/pipelines/user-guides/core-functions/caching/)
- [Lakkaraju et al., The Selective Labels Problem, KDD 2017](https://pmc.ncbi.nlm.nih.gov/articles/PMC5958915)

- [MLflow — migration vers MLflow 3](https://mlflow.org/docs/latest/ml/mlflow-3/) — `name=` et URI du modèle retournée par la journalisation.
- [MLflow — API scikit-learn](https://mlflow.org/docs/latest/api_reference/python_api/mlflow.sklearn.html)

Revue ciblée du 13 novembre 2026 : affirmations précisées dans cette passe ; les autres contenus ne sont pas intégralement revérifiés.

- [Kubeflow — réglages et priorités du cache](https://www.kubeflow.org/docs/components/pipelines/user-guides/core-functions/caching/) — un paramètre à la soumission peut écraser le réglage par tâche.

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
- [[118-artefacts-registre-releases-ml|Artefacts, registre et releases ML]] — contrats et vérifications de production
- [[119-contrats-prediction-features-batch|Contrats de prédiction, features et batch]] — contrats et vérifications de production
- [[00-moc-ai-engineering|MOC AI Engineering]]
