# Enrichissement des cartes courtes et du MLOps — 20 octobre 2026

Cette passe poursuit l'enrichissement proposé par la [revue du 17 octobre](revue-pertinence-2026-10-17.md) pour les sections 55 à 170. Elle avait deux objectifs : ne plus laisser de carte nettement plus courte que les autres, et donner au MLOps une partie précise sur le ML classique, jusqu'ici centré sur les applications LLM.

## Périmètre

- **Cartes courtes** : toutes les cartes dont la réponse comptait moins de 45 mots hors code, mesurés avec le parseur du lint. Elles étaient 92, sur une médiane de 78 mots.
- **MLOps** : section 110, avec une nouvelle fiche et des ajouts aux fiches 112 et 113.
- **Vérification en ligne** des faits datés ou propres à un produit : stages et alias du registre MLflow, signatures MLflow, cache de Kubeflow Pipelines, niveaux de maturité MLOps de Google Cloud, article sur les labels sélectifs.

Cette passe ne relit pas les cartes de plus de 45 mots et ne revérifie pas les autres produits cités par les fiches.

## Cartes courtes

89 cartes ont reçu un paragraphe. Conformément à la règle du 17 octobre, chaque ajout apporte un élément absent de la carte et de ses voisines :

| Apport | Exemples |
| --- | --- |
| Mécanisme | copy-on-write d'overlayfs, couche masquée par un `rm`, rollback du KV cache après un rejet, états d'un circuit breaker |
| Exemple chiffré | quantification INT8 d'un poids, part d'embedding et lm_head dans un 8B, coût total avec escalades, gain de TPOT selon la longueur de sortie |
| Critère de décision | poids dans l'image ou séparés, réentraînement planifié ou déclenché, priorité fréquence × gravité |
| Diagnostic | `curl -N` à travers les proxys, `OCI runtime create failed`, `kubectl get nodes -o wide` |

Les voisines ont été lues avant chaque ajout pour éviter de redéfinir une notion. Quand une notion appartient à une autre fiche, l'ajout la mobilise par un lien, comme le biais d'échantillonnage dans la carte sur l'active learning. Les exemples chiffrés ne reprennent pas les données d'une carte de calcul voisine : la taille d'un 8B en Q4_K_M, résultat intermédiaire d'un calcul de la fiche 164, a ainsi été écartée.

Trois cartes restent sous 45 mots : celles qui racontent l'histoire de dockershim dans la fiche 05. La revue du 17 octobre proposait de les réduire à la carte « à ne pas confondre » ; les enrichir irait dans le sens inverse. Leur retrait reste à décider.

## MLOps

La section couvrait bien le LLMOps : versionnage des prompts, eval gates, drift d'une application LLM. Il lui manquait le cycle de vie d'un modèle prédictif réentraîné. Les ajouts suivent la convention « une notion, une carte de référence » : le training-serving skew, le feature store et les labels retardés restent dans la fiche 159, la distinction dérive ou incident dans la fiche 157.

### Nouvelle fiche 117 : pipelines d'entraînement, registre et entraînement continu

17 cartes, dont 3 mises en situation et 1 calcul :

- niveaux 0, 1 et 2 de maturité MLOps, et pipeline déployé à la place du modèle ;
- réentraînement planifié ou déclenché, validation des données et validation du modèle avant promotion ;
- run de suivi d'expériences MLflow, signature et ses limites, promotion par alias depuis la dépréciation des stages dans MLflow 2.9 ;
- alias de registre ou alias de fournisseur, cache des étapes et entrées immuables, fenêtre d'entraînement, scoring batch ou en ligne ;
- labels sélectifs d'un modèle qui bloque des transactions, et estimation de précision et de rappel avant les labels à partir de probabilités calibrées.

### Fiche 113 : mesurer la dérive

Six cartes ajoutées : PSI et son calcul, seuil de Kolmogorov-Smirnov sur 100 000 et sur 50 observations, dérive multivariée par classifieur de domaine, distribution des scores et part au-dessus du seuil, et une mise en situation sur un tableau de bord de dérive ignoré. La carte « Quand réentraîner » ne demande plus de réentraîner « sur signal, pas sur calendrier » : un rythme régulier reste justifié quand les labels arrivent régulièrement.

### Fiches 112 et 113 : précisions

Le GitOps montre un `InferenceService` KServe et la limite d'un `storageUri` réinscriptible ; le pipeline CI/CD sépare CI du pipeline et entraînement continu ; le monitoring de qualité dimensionne l'échantillon par segment.

Le MOC gagne un **parcours MLOps** en cinq étapes, de la fiche 111 à la fiche 116.

## Résultats

| Indicateur | Avant | Après |
| --- | ---: | ---: |
| Fiches | 146 | 147 |
| Cartes | 2 163 | 2 186 |
| Cartes sous 45 mots | 92 | 3 |
| Cartes sous 50 mots | 158 | 69 |
| Mots moyens par réponse | 75,9 | 78,6 |
| Cartes de la section 110 | 98 | 121 |

Aucune réponse ne dépasse la limite du lint, 110 mots hors code et 140 pour une mise en situation.

## Vérifications

- Lint sur tout le vault : aucune erreur, aucun avertissement.
- 52 tests du dépôt réussis, dépendances de `scripts/requirements.txt` installées dans un environnement temporaire.
- Identifiants Anki attribués aux 23 nouvelles cartes ; catalogues du README et du MOC synchronisés.
- Sources consultées : [Google Cloud — MLOps et pipelines](https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning), [MLflow — workflow du Model Registry](https://mlflow.org/docs/latest/ml/model-registry/workflow/), [MLflow — signatures](https://mlflow.org/docs/latest/ml/model/signatures/), [Kubeflow Pipelines — cache](https://www.kubeflow.org/docs/components/pipelines/user-guides/core-functions/caching/), [Lakkaraju et al., The Selective Labels Problem](https://pmc.ncbi.nlm.nih.gov/articles/PMC5958915).

Les repères du PSI (0,1 et 0,25) sont des conventions issues du scoring crédit ; les cartes les présentent comme telles. Les commandes et noms de métriques cités dans les ajouts proviennent des documentations des outils et doivent être revérifiés à la prochaine revue des fiches concernées.

## Suite proposée

- **Dockershim** : décider du retrait des trois cartes historiques de la fiche 05.
- **Bande de 45 à 50 mots** : 66 cartes, souvent des définitions avec un bloc de code ; les relire avec la même règle plutôt que de les allonger systématiquement.
- **MLOps** : un atelier exécutable dans `examples/`, par exemple PSI, KS et estimation de performance sur des données synthétiques, rendrait les cartes de la fiche 113 vérifiables par la pratique.
