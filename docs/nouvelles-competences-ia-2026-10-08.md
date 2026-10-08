# Nouvelles compétences IA — 8 octobre 2026

## Périmètre

Cette extension ajoute **cinq fiches de 14 cartes**, soit **70 cartes**, avec **15 mises en situation, 10 distinctions et 8 calculs**. Elle complète les 1 723 cartes existantes par des compétences de prédiction et de décision utiles selon le poste d'ingénieur IA visé.

La revue des thèmes et des fiches voisines a permis de distinguer ce qui manquait de ce qui était déjà introduit : la validation temporelle, les métriques de retrieval et l'absence de causalité des importances étaient mentionnées ; les démarches propres aux cinq domaines ci-dessous n'avaient pas de fiche dédiée. Les fiches existantes reçoivent des connexions, sans reformulation de leurs questions ou réponses.

## Apports et priorités

| Fiche | Apport par rapport au contenu existant | Quand la travailler |
| --- | --- | --- |
| [174 — Recommandation & learning to rank](../170-ml-classique/174-recommandation-ranking.md) | Objectif produit, candidats, labels implicites, négatifs, exposition, nouveaux utilisateurs et diversité ; prolonge les embeddings et métriques du RAG | Recherche personnalisée, suggestions, catalogue, contenu ou produits |
| [175 — Prévision temporelle](../170-ml-classique/175-series-temporelles-prevision.md) | Horizons, backtesting, baseline saisonnière, ETS/ARIMA, prévisions récursives, variables futures, MASE, quantiles et réconciliation ; prolonge la disponibilité temporelle des données | Demande, capacité, volumes ou délais à anticiper |
| [176 — Détection d'anomalies](../170-ml-classique/176-detection-anomalies.md) | Détection sans labels complets, méthodes, seuils opérationnels, charge de revue et mesure par incident ; prolonge le monitoring et les métriques de classes rares | Incidents, qualité, changements inhabituels ou investigation |
| [177 — Explicabilité](../170-ml-classique/177-explicabilite-modeles.md) | Permutations, corrélations, SHAP et ses unités, PDP/ICE, actions réalisables et fidélité des justifications ; développe les limites des importances prédictives | Diagnostic, revue d'un modèle ou explication à ses utilisateurs |
| [178 — Inférence causale](../170-ml-classique/178-inference-causale-decisions.md) | Effets ciblés, graphes, sélection, identification, recouvrement, propension, différences de différences et uplift ; prolonge les A/B tests | Choisir une action et mesurer ce qu'elle change réellement |

Commencer par les fiches 171 à 173 sur choix, validation et calibration. Ensuite, choisir une branche selon le problème rencontré. Les cinq domaines ne constituent pas une liste d'outils à connaître uniformément : un poste de recherche documentaire, de plateforme et de prévision n'exige pas la même profondeur.

## Exercices associés

### Recommandation

Construire une baseline de popularité contextualisée et une recherche par contenu sur un catalogue d'articles. Réserver une période d'évaluation et figer les candidats éligibles. Comparer rappel des candidats, nDCG, redondance et résultats sur les nouveaux éléments.

**Livrable** : un tableau distinguant échec de recherche et mauvais classement, puis un test de diversité. Si les données ne contiennent pas de journaux d'exposition, le signaler ; ne pas présenter les éléments non cliqués comme des rejets certains. Une simulation ne démontre pas le gain réel auprès d'utilisateurs.

### Prévision temporelle

Prévoir un volume quotidien à un jour et à quatre semaines avec une baseline saisonnière et un modèle candidat. Simuler plusieurs dates de décision, en utilisant uniquement les variables alors disponibles. Rapporter MAE, comparaison à la baseline et couverture des intervalles par horizon.

**Livrable** : un backtest reproductible, avec une ligne historique reconstituée à la main et une analyse d'une période de rupture. Démontrer que les vraies valeurs intermédiaires ne sont pas utilisées dans une prévision récursive.

### Détection d'anomalies

Comparer une règle contextuelle et un détecteur sur des événements annotés ou une simulation avec incidents connus. Faire varier le seuil avec une limite de dossiers traitables par jour. Mesurer incidents retrouvés, délai et fausses alertes ; distinguer les cas injectés des incidents réels.

**Livrable** : une courbe reliant seuil, charge et utilité. Si les labels sont incomplets, prévoir une revue de non-alertes et expliquer ce qui reste impossible à estimer. Vérifier aussi le comportement après un changement légitime de référence.

### Explicabilité

Sur un modèle tabulaire, introduire deux variables fortement corrélées. Comparer permutation individuelle, permutation groupée et réentraînement sans le groupe. Produire une explication locale avec référence et unité explicites.

**Livrable** : une note expliquant pourquoi les résultats diffèrent, avec reconstitution numérique de la prédiction. Vérifier qu'aucune attribution n'est présentée comme preuve de l'effet d'une action réelle.

### Causalité

Simuler une aide dont l'attribution dépend de la difficulté des dossiers, avec un effet connu dans le générateur. Comparer différence brute et ajustement sur les facteurs observés. Ajouter un facteur commun non observé ou supprimer le recouvrement pour exposer les limites.

**Livrable** : graphe, population cible, hypothèses, estimation et analyse de sensibilité. Une méthode qui retrouve l'effet dans une simulation ne prouve pas que les hypothèses seront vraies dans des données réelles.

## Sources et portée

Les références primaires figurent dans chaque fiche : Google et Microsoft Research pour la recommandation, les auteurs de *Forecasting: Principles and Practice*, documentation scikit-learn et SHAP, travaux scientifiques sur anomalies et explications, Hernán & Robins et PyWhy pour la causalité. Les calculs et scénarios sont pédagogiques ; ils ne sont pas des résultats d'un système déployé.

La section 170 s’élargit à la prédiction et à la décision. Son titre historique est conservé pour garder les sous-paquets Anki existants stables. Le README et le MOC présentent les nouvelles fiches ; un parcours permet de choisir la branche selon la tâche. Cette extension ne remplace pas un cours complet d'optimisation, de causalité ou de prévision avancée. Elle fournit des repères pour concevoir une expérience, détecter un piège et choisir un approfondissement utile.

## Validation

Le vault passe de **121 fiches et 1 723 cartes** à **126 fiches et 1 793 cartes**, dans 17 sections. Il compte désormais **284 mises en situation et 132 cartes de distinction**.

- **Conservation** : comparaison au commit `61d13ad` ; les 1 723 anciennes questions, réponses et identifiants sont strictement identiques. Seuls des liens sont ajoutés aux fiches existantes.
- **Structure et navigation** : lint sans erreur ni avertissement, lecture Obsidian/Anki équivalente, connexions réciproques, catalogues synchronisés et liens locaux du bilan valides.
- **Tests** : les 40 tests existants réussissent ; `git diff --check` ne signale aucune anomalie.
- **Calculs** : les huit cartes numériques sont vérifiées en Python, avec leurs hypothèses : nDCG, MASE, pinball, alertes, permutation, log-odds, différences de différences et gain incrémental.
- **Export** : `dist/ai-engineering.apkg` régénéré ; archive et base SQLite valides, 1 793 cartes actives avec champs renseignés, 30 cartes retirées suspendues. Les anciens GUID et identifiants de sous-paquets sont conservés. L'artefact reste exclu de Git.

Les exercices proposés n'ont pas été exécutés comme projets complets. La vérification porte sur les contenus ajoutés, leurs calculs et leur intégration au vault ; aucune bibliothèque Anki personnelle ni infrastructure de production n'a été modifiée.
