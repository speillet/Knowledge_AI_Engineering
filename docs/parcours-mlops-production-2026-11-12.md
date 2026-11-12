# Parcours MLOps : de l'expérience à une prédiction exploitable

Revue du 12 novembre 2026. Ce parcours accompagne les neuf fiches de `110-mlops-cicd`. Il suit un cas fictif de résiliation d'abonnement ; les noms de releases, données et seuils illustrent une démarche, sans constituer une configuration prête à déployer.

## 1. Définir ce que le modèle doit prédire

L'unité est **un abonnement actif à une date de référence**. La cible est sa résiliation dans les trente jours suivants. Un client possédant trois abonnements peut donc correspondre à trois observations. La définition précise les suspensions, renouvellements et corrections ; elle possède une version distincte du modèle.

Une prédiction de la semaine dernière ne reçoit pas immédiatement un label négatif parce qu'aucune résiliation n'est encore observée. L'horizon doit être écoulé, puis le délai de collecte respecté. Les métriques portent sur des cohortes suffisamment mûres, avec couverture du rapprochement et règle explicite pour les issues encore inconnues.

Le propriétaire métier définit usage et capacité de traitement ; les responsables données, modèle et exploitation définissent leurs engagements et les conditions de reprise. Le livrable initial est un contrat de prédiction, avant un choix de registre ou d'orchestrateur. Voir [les contrats de prédiction](../110-mlops-cicd/119-contrats-prediction-features-batch.md) et [les responsabilités MLOps](../110-mlops-cicd/111-mlops-llmops-fondamentaux.md).

## 2. Construire les données réellement disponibles à la décision

À chaque date de référence, reconstituer les informations alors accessibles : activité passée, ancienneté, offre et incidents connus. Un incident daté du lundi mais reçu le mercredi n'était pas disponible pour une décision prise mardi. Distinguer temps d'événement et disponibilité, et tester les arrivées tardives.

La documentation [Feast sur les jointures point-in-time](https://docs.feast.dev/getting-started/concepts/point-in-time-joins) décrit la recherche historique dans une fenêtre TTL. Cela ne dispense pas de vérifier séparément les règles de disponibilité, de déduplication et du backend. Une valeur disponible dans le stockage peut aussi être trop ancienne pour l'usage métier.

Le livrable est un snapshot identifié avec schéma, provenance, contrôles sémantiques, éligibilité et définition du label. Conserver les rejets et leur motif dans la limite prévue par la politique de données. Une source qui change les montants d'euros en centimes peut conserver ses types tout en invalidant le modèle. Voir [les données temporelles](../150-donnees-conformite/159-donnees-temporelles-features.md).

## 3. Séparer recette, exécution et candidat

La **recette** décrit les transformations, l'apprentissage et l'évaluation. Un **run** exécute cette recette avec données, paramètres et environnement précis. Le **candidat** est le paquet produit, avec ses résultats et ses limites.

Séparer chronologiquement les jeux lorsque l'usage le demande, en respectant disponibilité et maturité des labels. Ajuster imputation, encodage et normalisation sur les seules données autorisées par le protocole. Prévoir un ajustement de calibration et un choix de seuil sans réutiliser le test final comme levier de sélection. Une validation croisée correctement imbriquée peut organiser ces séparations ; quatre fichiers distincts ne sont pas une obligation universelle.

Tracer versions, splits, hyperparamètres, graines, environnement et résultats par segment. **Enregistrer une graine ne l'applique pas** aux différents générateurs. Les garanties de déterminisme dépendent des composants et plateformes. [PyTorch décrit ces limites](https://docs.pytorch.org/docs/stable/notes/randomness.html) ; les notions de seed et de preuve historique sont développées dans [la fiche reproductibilité](../110-mlops-cicd/114-reproductibilite-variance.md).

## 4. Publier un paquet qui sait réellement prédire

Le paquet contient les transformations apprises et le modèle, ainsi que le calibrateur lorsqu'il est utilisé. Une release référence aussi contrat des features, image, sorties et politique de décision. Un fichier de poids seul ne suffit pas si le service utilise un encodage ou un seuil indépendant et mutable.

Avec [MLflow 3](https://mlflow.org/docs/latest/ml/mlflow-3/), utiliser `name=` dans l'API de journalisation et conserver `info.model_uri`, retournée par `log_model`. Enregistrer ensuite cette URI et garder la version du registre obtenue. Ne pas reconstruire le chemin du modèle en supposant l'ancien emplacement dans les artefacts d'un run.

La signature décrit un contrat technique ; elle ne prouve pas que les unités ou l'horizon ont le sens attendu. Tester les probabilités avec leur ordre de classes et le mode d'inférence choisi. Un consommateur qui attend une probabilité ne doit pas recevoir silencieusement la classe produite par `predict`.

Dans une image propre, charger l'artefact publié, exécuter les cas connus et tester les erreurs. Vérifier provenance avant désérialisation : les formats fondés sur pickle peuvent exécuter du code. Une conversion ou une mise à jour de dépendance exige une validation adaptée ; [scikit-learn ne garantit pas la compatibilité de chargement entre versions](https://scikit-learn.org/stable/model_persistence.html). Voir [artefacts, registre et releases](../110-mlops-cicd/118-artefacts-registre-releases-ml.md).

## 5. Décider si le candidat mérite une promotion

Fixer les critères avant la comparaison : qualité utile, calibration, segments, coût, latence et capacité de traitement des décisions. Comparer candidat et champion sur les mêmes cas, avec incertitude. Une marge de non-infériorité peut convenir à un candidat moins coûteux ; un gain moyen ne doit pas masquer une régression sur un segment nécessaire à l'usage.

Conserver référence historique et cohorte récente suffisamment mûre : elles répondent à des questions différentes. Une source cassée peut produire une dérive, puis un modèle parfaitement adapté à cette erreur. Le déclencheur de réentraînement lance une investigation ou un pipeline ; il n'autorise pas la promotion. Cette séparation correspond à l'architecture décrite dans [le guide MLOps Google Cloud](https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning).

Le livrable est un rapport approuvé relié à une release immuable. Exemple conceptuel, avec références fictives :

```yaml
# Manifeste illustratif ; aucun schéma MLflow implicite.
release: retention-r17
recipe: recette-v6
model_uri: models:/retention/17
artifact_digest: empreinte-du-paquet-verifie
runtime_image: image-referencee-par-son-digest
features_contract: abonnement-v4
label_definition: resiliation-30j-v3
decision_policy: retention-v8
training_snapshot: retention-s042
validation_report: rapport-r17-approuve
rollback_release: retention-r16-revalidee
```

Le numéro 17 du registre et celui de la release coïncident ici par choix d'exemple ; ils n'ont pas besoin de coïncider. Une preuve d'approbation et les droits de promotion restent distincts d'un tag éditable. Voir [CI/CD](../110-mlops-cicd/112-cicd-modeles.md) et [pipelines continus](../110-mlops-cicd/117-pipelines-entrainement-continu.md).

## 6. Déployer la version approuvée et identifier celle qui répond

Résoudre l'alias en version explicite une seule fois, puis déployer cette version et journaliser son identité effective. Déplacer `champion` ne recharge pas les processus déjà démarrés. Les [alias du registre MLflow](https://mlflow.org/docs/latest/ml/model-registry/workflow/) désignent une version ; le déploiement doit organiser chargement, transition et vérification des réplicas.

```text
recette + snapshot → entraînement → candidat + rapport
                                         ↓ approbation
                                 release explicite
                                         ↓ déploiement
features → contrat → paquet chargé → score → politique → décision
                                         ↓
                         traces + labels mûrs → évaluation
```

Un canary surveille comportement, erreurs, ressources et qualité disponible. Avec une cible à trente jours, il ne prouve pas immédiatement la qualité finale. Un modèle en shadow n'influence pas la décision ; ses résultats ne prouvent pas à eux seuls l'effet de la politique qui serait appliquée. Les limites du canary sont décrites dans [Google SRE](https://sre.google/workbook/canarying-releases/).

Le rollback remet une **combinaison compatible** : modèle, transformation, contrat et politique. Tester qu'elle peut encore lire ses features et charger ses artefacts avant de compter sur elle.

## 7. Livrer des prédictions consommables en batch ou en ligne

En ligne, réserver un délai global pour attente, features, calcul et réponse. Prévoir le comportement si une source manque : secours validé, valeur encore admissible ou décision différée. Remplacer toute absence par zéro pour conserver un taux de réponses réussi peut cacher un incident de qualité.

En batch, définir une identité logique avec release, snapshot et partition ; chaque retry garde la même intention. Publier seulement après contrôle de couverture, unicité et sorties. Une publication partielle doit être prévue et visible. Les actions déclenchées en aval ont besoin de leur propre protection contre les doublons.

Pour douze millions de lignes en deux heures, le plancher moyen est d'environ **1 667 lignes utiles/s**, publication comprise. S'il ne reste que quatre-vingt-dix minutes pour le scoring, il faut environ **2 223 lignes/s** à cette étape. Mesurer sur les tailles réelles avec marge, reprises et déséquilibre des partitions.

Conserver instant de référence, date du calcul, validité et release. Un calcul récent sur un snapshot périmé ne constitue pas un score actualisé.

## 8. Mesurer la qualité sans confondre absence de preuve et succès

Surveiller disponibilité, latence, saturation, données, distribution des sorties et issues métier. Les dérives détectent des changements ; elles ne prouvent pas une baisse de qualité, et une stabilité des distributions ne prouve pas l'absence de régression.

Rapprocher les labels avec l'identité de prédiction et l'horizon, pas seulement le client. Rapporter maturation, couverture et corrections. Sur mille prédictions dont six cents ont un label exploitable et quatre cent quatre-vingts sont correctes, l'exactitude observée est **80 % sur la partie labellisée**, avec **60 % de couverture**. Cela ne démontre pas 80 % sur toute la population.

Quand les décisions déterminent quelles issues deviennent visibles, les labels sont sélectifs. Une revue humaine n'est pas nécessairement l'issue contrefactuelle. Une pondération ne recrée pas des labels pour des groupes qui n'ont aucune chance d'être observés ; voir [le travail original sur les selective labels](https://pmc.ncbi.nlm.nih.gov/articles/PMC5958915/). Le parcours de diagnostic figure dans [monitoring et feedback](../110-mlops-cicd/113-monitoring-drift-feedback.md).

## 9. Prouver la capacité de reprise

Une restauration du registre doit couvrir métadonnées et artefacts, qui sont [des composants de stockage distincts dans MLflow](https://mlflow.org/docs/latest/self-hosting/architecture/overview/). Tester en environnement isolé : retrouver la version approuvée, vérifier les octets, charger dans l'image compatible, récupérer les features nécessaires et produire les résultats de référence.

Mesurer RPO et RTO. Un registre accessible avec des artefacts absents ne rétablit pas le service. La fin de l'incident technique ne ferme pas l'analyse ML : identifier décisions affectées, résultats manquants, labels perturbés et éventuelle contamination des futurs entraînements. Voir [SRE, incidents et capacité](../110-mlops-cicd/116-sre-incidents-capacite-ia.md).

## Périmètre de l'enrichissement

Cette passe ajoute **68 cartes**, dont six mises en situation, et approfondit **33 réponses existantes**. La section passe de **7 fiches / 128 cartes à 9 fiches / 196 cartes**. Les deux nouvelles fiches séparent paquet et gouvernance de release, puis contrat des données et exploitation des prédictions. Les sept fiches existantes gagnent chacune quatre cartes ciblées.

Les corrections concernent notamment MLflow 3, résolution des alias, validation statistique, seed, labels sélectifs, estimation de rappel, indisponibilité du monitoring et prévisions Gartner. Les faits et APIs ajoutés ont été confrontés aux documentations primaires citées et aux références MLflow/Feast de Context7. Les procédures opérationnelles et calculs sont des exemples pédagogiques à adapter, pas des engagements des fournisseurs.

Les anciennes dates générales de vérification restent conservées : cette passe ne constitue pas une nouvelle vérification exhaustive des offres cloud, des textes réglementaires et de tous les exemples des anciennes fiches. Les snippets MLflow sont documentaires ; MLflow et Feast ne sont pas installés ni exécutés par les contrôles du dépôt.

Les **2 372 questions et identifiants Anki préexistants** sont conservés. Les nouvelles cartes reçoivent de nouveaux identifiants ; aucune carte n'est retirée. Les vérifications de contenu, de liens, des catalogues et de l'export Anki accompagnent la livraison.

Validation locale : `make check` réussit, dont **54 tests**, ruff, mypy et les deux ateliers. Le lint signale **zéro erreur et zéro avertissement**. L'inspection du paquet exporté retrouve **2 440 cartes actives** avec les identifiants attendus et les **71 anciennes cartes retirées toujours suspendues**. Les calculs ajoutés et la syntaxe des snippets Python ont également été contrôlés ; cela ne remplace pas un essai MLflow dans un environnement cible.

La [vérification d’actualité complémentaire](verification-actualite-2026-11-13.md) contrôle ensuite les annonces, modes d’hébergement, référentiels et transitions réglementaires encore cités dans ces fiches et leurs voisines.
