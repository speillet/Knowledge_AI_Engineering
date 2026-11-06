# Ancrage concret des cartes abstraites — 22 octobre 2026

Cette passe poursuit l'enrichissement des [17](revue-pertinence-2026-10-17.md) et [20 octobre](enrichissement-cartes-mlops-2026-10-20.md). Elle ne vise plus la longueur des réponses mais leur **ancrage** : le README demande « des repères chiffrés et des exemples exécutables plutôt que des formulations abstraites », et la revue du 17 octobre signalait des cartes récentes « qui répondent par une liste de vérifications ».

Les sections suivantes conservent le bilan historique du 22 octobre. Ces modifications locales ont été intégrées et complétées lors de la [passe transversale de novembre](#complément-transversal-de-novembre-2026) décrite en fin de document ; ses chiffres ne doivent pas être confondus avec ceux de la première passe.

## Périmètre

- **Mesure de départ** : une carte est dite abstraite lorsque sa réponse ne contient ni chiffre ni code, mises en situation exclues. C'était le cas de 737 cartes sur 2 186, avec une médiane de 82 mots, au-dessus de la médiane du vault. Les allonger n'était donc pas la bonne réponse.
- **Fiches traitées** : toutes celles dont au moins 60 % des cartes de définition étaient abstraites, soit 37 fiches. Elles se concentrent dans les fiches les plus récentes : données (150), ML classique (170), system design (140), observabilité (90), inférence (60-010 à 60-012).
- **Hors périmètre** : les questions, les mises en situation et les cartes de calcul n'ont pas été modifiées. Les fiches sous le seuil de 60 % n'ont pas été relues.

Cette mesure est un indicateur grossier : un exemple nommé sans chiffre reste compté comme abstrait, et une carte de comparaison peut être utile sans exemple.

## Règle appliquée

Chaque ajout **remplace une phrase générique** plutôt qu'il ne s'ajoute à elle, pour rester sous la limite du lint de 110 mots. Il apporte un des quatre éléments suivants, absent de la carte et de ses voisines :

| Apport | Exemples |
| --- | --- |
| Scénario chiffré | omission coordonnée sur un client bloqué 2 s, plafond de dépense dépassé par deux transactions concurrentes, couverture d'un intervalle à 90 % mesurée à 83 % |
| Code ou requête | outbox et inbox en SQL, écriture conditionnelle `ON CONFLICT … WHERE`, reducer LangGraph qui refuse les conflits, `merge_asof` point-in-time, salting PySpark |
| Mécanisme concret | transaction longue perdue par un polling sur `updated_at`, permutation de deux `interrupt`, réplication des têtes KV au-delà de TP=8, cache de prompts servi pendant son rafraîchissement |
| Critère de décision | règle, modèle supervisé ou LLM selon le besoin, ETL ou ELT, lignage de table ou d'enregistrement, outliers ou nouveauté |

Trois contrôles complètent cette règle :

- **Pas de réponse donnée d'avance** : avant d'écrire, les mises en situation et les cartes de calcul de la fiche ont été relues. Cinq exemples qui reprenaient presque mot pour mot une mise en situation ou une carte voisine ont été remplacés : relance d'une réservation avec une nouvelle clé, variantes d'un même tutoriel, exposition des nouveautés, négation supprimée par la normalisation, suppression d'un message SQS.
- **Une notion, une carte de référence** : un ordre de grandeur déjà établi ailleurs est cité par un lien. Le multiplicateur de tokens des systèmes multi-agents reste ainsi dans la fiche 31 ; la fiche 36 illustre plutôt le chemin critique par un calcul de délai.
- **Cohérence avec les ateliers** : les cartes des fiches 90-013, 140-011 et 20-010 citent les tests réels de `examples/agentic-support` et `examples/rag-verifiable`. Un écart a été corrigé avant publication : le test contrefactuel de l'atelier RAG fait passer le délai à 60 jours, pas à 45.

## Résultats

| Indicateur | Avant | Après |
| --- | ---: | ---: |
| Cartes | 2 186 | 2 186 |
| Cartes modifiées | — | 316 |
| Cartes abstraites (ni chiffre ni code) | 737 | 481 |
| Cartes avec un bloc de code | 214 | 262 |
| Mots moyens par réponse | 78,6 | 80,9 |
| Médiane des mots par réponse | 80 | 82 |
| Cartes sous 50 mots | 69 | 55 |

| Section | Fiches | Cartes modifiées | Abstraites avant → après |
| --- | ---: | ---: | ---: |
| 150 — Données & conformité | 11 | 107 | 112 → 16 |
| 140 — System design & produit | 5 | 47 | 51 → 19 |
| 90 — Observabilité & evals | 4 | 46 | 43 → 6 |
| 170 — ML classique | 5 | 41 | 45 → 18 |
| 60 — Inférence LLM | 4 | 30 | 32 → 3 |
| 20 — RAG | 2 | 14 | 18 → 5 |
| 40 — Automatisation | 2 | 14 | 17 → 7 |
| 50, 30, 160, 70 | 4 | 17 | 23 → 11 |

Aucune question n'a changé : les identifiants Anki et l'historique de révision sont conservés. Aucune réponse ne dépasse la limite du lint.

## Vérifications

- **API citées confrontées au code des bibliothèques**, installées dans un environnement temporaire aux versions de l'atelier quand elles y sont épinglées : Langfuse 4.17.0 (`trace_context`, `completion_start_time`, `mask` et `mask_otel_spans`, `should_export_span`, lots de 512 spans toutes les 5 s, cache de prompts de 60 s servi pendant son rafraîchissement, variable absente laissée telle quelle par `compile`), LangGraph 1.2.14 et langgraph-sdk 0.4.6 (`durability`, `Command(resume=…)` par identifiant, `checkpointer=True` d'un sous-graphe, `multitask_strategy`, limite de récursion par défaut de 10 007), TRL 1.14.2 (`DPOTrainer`, `beta` de 0,1), Hugging Face Datasets 5.1.0 (perte du tampon de mélange à la reprise, `split_dataset_by_node`), scikit-learn et statsmodels (`TimeSeriesSplit`, `TargetEncoder`, `ExponentialSmoothing`, `ARIMA`), docling-core 2.103.1 (noms des chunkers).
- **Calculs** des exemples chiffrés refaits : ROI, MAD robuste, pondération par probabilité d'exposition, troncature, taux agrégés, point adjustment.
- **Vault** : lint sans erreur ni avertissement, 52 tests du dépôt réussis avec les dépendances de `scripts/requirements.txt`, export Anki généré (2 186 cartes, 71 retirées), catalogues synchronisés.

Les autres valeurs par défaut et syntaxes citées viennent des documentations des outils et n'ont pas été revérifiées en ligne pendant cette passe : Spark (200 partitions de shuffle, seuil de broadcast de 10 Mo, `maxResultSize` de 1 Go), Flink (parallélisme maximal d'au moins 128, `withIdleness`), Iceberg, dbt, Airflow, Kafka, pgvector 0.8, Stripe (clés purgeables après 24 heures), Debezium et vLLM. Les dates `Vérifié le` des fiches n'ont pas changé, puisque seules les affirmations ajoutées ont été contrôlées.

## Suite proposée

- **Fiches sous le seuil** : 481 cartes restent sans chiffre ni code. Une partie est légitime (définitions, cartes « à ne pas confondre » déjà illustrées par des noms) ; relire en priorité les fiches entre 50 et 60 % (95, 96, 40-010, 40-012, 133, 161).
- **Doublons entre fiches** révélés par cette passe : 158 et 150-016 (réconciliation source-destination), 20-010 et 143 (réponse partielle, sources contradictoires), 62 et 69 (désagrégation), 150-014 et 159 (watermark). Leur fusion relève d'une revue de pertinence.
- **Revérification datée** : confronter aux documentations les valeurs par défaut citées ci-dessus lors de la prochaine revue des fiches 150-012 à 150-015 et 158.

## Complément transversal de novembre 2026

La première passe de novembre a couvert les **147 fiches des 17 sections**, index conteneurs compris. Par rapport au commit `218570f`, **536 réponses sur 2 186** étaient modifiées : les 316 réponses du travail local initial, relues et corrigées lorsque nécessaire, et 220 réponses supplémentaires dans les 110 autres fiches.

Chaque fiche contient donc un enrichissement effectif ; cela ne signifie pas que ses réponses ont toutes été réécrites. Les ajouts ciblent les mécanismes insuffisamment expliqués, les critères de décision, les contre-exemples et les vérifications concrètes. La longueur seule n'est pas un objectif.

| Lot thématique | Sections | Fiches | Réponses modifiées |
| --- | --- | ---: | ---: |
| Prompts, RAG, agents et workflows | 10, 20, 30, 40 | 32 | 85 |
| Modèles, entraînement et inférence | 50, 60, 130 | 26 | 78 |
| Infrastructure et API | 70, 80 | 19 | 37 |
| Évaluation, sécurité et exploitation | 90, 100, 110, 120 | 29 | 96 |
| Architecture, données et conformité | 140, 150 | 28 | 178 |
| Multimodal et ML classique | 160, 170 | 13 | 62 |
| **Total** | **17 sections** | **147** | **536** |

### Corrections de fond

- **Mesure et coût** : distinguer accord et exactitude, observation et cause, quantiles par composant et latence globale ; convertir les FLOPs en secondes puis en GPU-heures ; inclure les coûts des échecs.
- **Exécution** : préciser limites de reprise, idempotence, annulation et budget ; ne pas faire réussir une assertion de traçage parce qu'aucun span attendu n'a été produit.
- **Infrastructure** : distinguer rôles OCI, types de Service Kubernetes, readiness et liveness, budget applicatif de VRAM et isolation matérielle.
- **Données** : les buckets ne bornent pas le nombre de fichiers ; la purge d'une jointure temporelle dépend des watermarks ; une moyenne salée doit ignorer les valeurs nulles comme l'agrégat de référence.
- **ML** : `TimeSeriesSplit(test_size=28)` compte des observations, pas des mois ; une baseline saisonnière multi-horizon ne doit pas lire les observations futures ; une explication plausible ne prouve pas la causalité.
- **Conformité** : la pseudonymisation ne garantit pas l'absence de données personnelles. Les sanctions AI Act sont précisées à partir des articles 99 et 101 consultés sur le site de la Commission, avec distinction des régimes.

### Périmètre de validation

Une comparaison par fiche avec `218570f` vérifie **toutes les questions, tous les identifiants et l'ordre des cartes**, ainsi que la présence d'au moins une réponse modifiée dans chaque fiche. Le nombre de cartes, les 354 mises en situation et les 182 cartes de confusion restent inchangés.

Les contrôles de lisibilité conservent les limites de 110 mots par réponse standard et 140 par mise en situation. Les commandes du dépôt vérifient format, liens, lecture par le plugin, catalogues, tests et export Anki ; les PR thématiques passent la CI avant fusion.

Validation locale finale du 6 novembre : `make check` réussi, **54 tests**, ruff et mypy sans erreur, lint sans avertissement, catalogues synchronisés et export de **2 186 cartes actives et 71 retirées**. Des vérifications ciblées supplémentaires couvrent les conversions FLOPs/GPU-heures, le coût par réussite, les probabilités, le `LEFT JOIN`, le classement des suppressions et la moyenne avec valeurs nulles.

Cette passe est une relecture ciblée des réponses enrichies, **pas une certification exhaustive des 2 186 cartes ni de toutes les API citées**. Les vérifications de bibliothèques rapportées dans le bilan historique ci-dessus n'ont pas toutes été répétées. Les dates globales `Vérifié le` ne sont pas avancées ; les consultations ponctuelles nouvelles sont identifiées dans les sources concernées. Les configurations locales MCP et VS Code restent hors publication.

## Seconde passe transversale — 6 novembre 2026

Cette continuation approfondit **une réponse dans chacune des 147 fiches**, par rapport à `07df340`, point de départ après les six premières PR. Elle comprend **146 réponses jusque-là inchangées depuis `218570f`**, et un nouveau complément à l'unique carte de l'index conteneurs, déjà enrichie.

Le cumul est donc de **682 réponses distinctes modifiées**, et non 683 : `536 + 146`. Les 147 réponses de cette seconde passe comprennent **141 cartes standard et 6 mises en situation**. Aucune carte n'est ajoutée, supprimée ou déplacée ; questions et identifiants restent identiques.

### Apports pédagogiques

- **Distinguer mécanisme et garantie** : appel d'outil proposé ou exécuté, checkpoint et effet externe, signature et confiance, HTTP 200 et service réellement rendu.
- **Rendre les compromis mesurables** : calculs de coût par réussite, coût d'entrée avec cache, charge offerte/réalisée, MAE/RMSE, log-odds SHAP et comparaisons multiples.
- **Préciser les hypothèses techniques** : mémoire totale d'un MoE, états partitionnés de FSDP, contexte réellement utilisé, unités des métriques de cache et ordre des filtres d'échantillonnage.
- **Renforcer les cas de production** : approbation devenue périmée, effet distant réussi avant panne locale, tombstone expiré avant backfill, labels non mûrs et dérive d'un juge.
- **Corriger les simplifications trompeuses** : un Pod n'est pas intégralement immuable ; un SIF peut être distribué par registre OCI via ORAS sans devenir une image Docker ; GGUF n'impose ni CPU ni fichier unique ; une reconnexion SSE ne garantit pas la reprise du flux ; l'accord humain n'est pas un plafond universel d'évaluation.

| Lot | Sections | Fiches / réponses |
| --- | --- | ---: |
| Prompts, RAG, agents et workflows | 10, 20, 30, 40 | 32 |
| Modèles, exécution, infrastructure, multimodal et ML | 50, 60, 70, 80, 130, 160, 170 | 58 |
| Qualité, exploitation, produit et données | 90, 100, 110, 120, 140, 150 | 57 |

### Vérifications et limites

La comparaison avec `07df340` contrôle **exactement une réponse modifiée par fiche**, toutes les questions, les identifiants, l'ordre et le total de **2 186 cartes**. La comparaison avec `218570f` confirme le cumul de 682 réponses distinctes. Les 354 mises en situation et 182 cartes de confusion restent présentes.

Le lint ne signale aucune erreur ni avertissement : les cartes standard restent sous 110 mots et les mises en situation sous 140. Les calculs ajoutés ont été vérifiés en Python standard, notamment la conservation de la distribution du speculative sampling, les conversions de probabilités, les coûts, le SLI et les dépendances d'une fenêtre de sept jours.

Les consultations primaires ciblées concernent **le routage Cognee, les mises à jour des Pods Kubernetes, la publication SIF avec Apptainer, l'article 22 du RGPD et le champ d'application de l'AI Act**. Les liens et la portée de consultation sont ajoutés aux fiches concernées. Il ne s'agit pas d'une revérification de toutes les versions, bibliothèques ou dispositions réglementaires du vault ; les dates globales des fiches restent inchangées.

Validation locale finale : **`make check` réussi, 54 tests**, ruff et mypy sans erreur, catalogues et ateliers validés. **`make export` réussi** ; inspection de la base du paquet : 2 257 notes, tous les 2 186 identifiants actifs présents, et exactement 71 cartes retirées suspendues. Les lots passent également les contrôles CI avant leur fusion.

Les exemples de calcul sont illustratifs, avec tarifs fictifs lorsqu'ils portent sur une facture ; les exemples d'API, de GPU et d'infrastructure n'ont pas tous été exécutés dans un environnement réel. Les configurations locales MCP/VS Code ne sont ni modifiées ni publiées.
