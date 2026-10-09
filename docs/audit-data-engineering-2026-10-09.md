# Data engineering pour un AI Engineer — audit du 9 octobre 2026

## Diagnostic et périmètre

La couverture initiale était **solide sur la fiabilité de l'ingestion et la temporalité**, mais incomplète sur les mécanismes qui permettent de construire et d'exploiter les datasets. Les contrats, la CDC, les backfills et les jointures point-in-time étaient développés ; SQL, modélisation analytique, formats de stockage et calcul distribué étaient surtout évoqués à travers d'autres sujets.

La revue part des **129 fiches et 1 868 cartes** existantes. Elle cartographie les thèmes du vault et approfondit les fiches sur données, pipelines, automatisation, validation ML et sources documentaires. Elle ne revérifie pas tous les produits ou textes réglementaires des autres sections. Les dates de vérification des fiches historiques restent inchangées.

L'extension apporte **8 fiches, 142 cartes et un atelier SQL exécutable**. Le parcours couvre désormais les principaux mécanismes de data engineering utiles à un ingénieur IA appliquée : transformer correctement les données, les reconstruire, expliquer leurs limites, mesurer leur disponibilité et diagnostiquer leur coût. La maîtrise opérationnelle de chaque moteur reste à travailler sur des projets et des incidents réels.

## Matrice de couverture

« Développé » signifie ici définitions, mécanismes, limites et cas de raisonnement. Cela ne signifie pas certification pratique sur les outils cités.

| Compétence | Avant cette revue | Couverture et point d'entrée |
| --- | --- | --- |
| Grain, identités, faits/dimensions, cardinalités, SCD | Peu développés | [Modélisation analytique](../150-donnees-conformite/150-010-modelisation-donnees-analytiques.md) : éviter doubles comptes, mauvais labels et mélange d'entités |
| SQL de transformation | Text-to-SQL couvert ; fondations SQL insuffisantes | [SQL pour les datasets IA](../150-donnees-conformite/150-011-sql-transformations-analytiques.md) : jointures, NULL, fenêtres, anti-jointures, plans et tests |
| Fichiers, colonnes, partitions, tables transactionnelles | Versioning évoqué, stockage peu expliqué | [Stockage et lakehouse](../150-donnees-conformite/150-012-stockage-colonnaire-lakehouse.md) : Parquet/Arrow/Avro, pruning, petits fichiers, snapshots et maintenance |
| ETL/ELT et orchestration | Outils nommés, fonctionnement peu développé | [Orchestration data](../150-donnees-conformite/150-013-orchestration-pipelines-donnees.md) : intervalles, dépendances de partitions, publication, CI et ressources |
| Ingestion, API, CDC, reprises et suppressions | Déjà développé pour CDC et backfills | [Ingestion](../150-donnees-conformite/158-ingestion-cdc-backfills.md) conservée et complétée sur pagination des API évolutives |
| Temps métier, disponibilité, labels retardés et features | Déjà développé | [Variables temporelles](../150-donnees-conformite/159-donnees-temporelles-features.md) complétées sur chemins offline/online et matérialisation sûre |
| Traitements événementiels avec état | Watermarks présents, traitement distribué incomplet | [Streaming](../150-donnees-conformite/150-014-streaming-traitements-evenements.md) : fenêtres, triggers, ordre, jointures, corrections, état et backpressure |
| Passage à l'échelle et coût du calcul | Évoqué pour les lots LLM | [Performance data](../150-donnees-conformite/150-015-calcul-distribue-performance-donnees.md) : shuffle, skew, broadcast, mémoire, UDF, cache et coûts |
| Contrats et qualité des données | Déjà développé | [Contrats](../150-donnees-conformite/157-contrats-qualite-donnees.md) : structure, sens métier, migrations, quarantaine et publication cohérente |
| Observabilité, catalogue, lignage et incidents | Lignage et qualité présents, exploitation dispersée | [Observabilité data](../150-donnees-conformite/150-016-observabilite-lignage-donnees.md) : SLO, couverture, réconciliation, impact et coût des contrôles |
| Construction de corpus RAG, SFT et évaluation | Curation, parsing et versioning déjà présents | [Datasets et corpus IA](../150-donnees-conformite/150-017-datasets-corpus-ia.md) : manifestes, familles, shards, lecteurs, mélange, packing et reprise |
| Validation et prévention des fuites | Déjà développé | [Validation ML](../170-ml-classique/172-validation-metriques-ml.md), [curation](../150-donnees-conformite/151-donnees-curation-annotation.md) et nouveaux cas SQL/corpus |
| Confidentialité et gouvernance | Déjà développé | [Confidentialité](../150-donnees-conformite/152-pii-confidentialite.md), [RGPD](../150-donnees-conformite/154-rgpd-llm.md), [IA responsable](../150-donnees-conformite/156-ia-responsable.md) ; droits et copies dérivées rappelés dans les nouvelles fiches |
| Effets distribués et transactions | Déjà développé | [Idempotence](../140-system-design-produit/149-livraison-idempotence-concurrence.md), [outbox et sagas](../140-system-design-produit/140-010-transactions-outbox-sagas.md), reliés aux reprises de pipelines |

Le contenu met l'accent sur les décisions transférables entre moteurs. Par exemple, la garantie exactly-once exige de vérifier les sources et destinations couvertes ; elle ne s'étend pas automatiquement aux appels HTTP externes. Cette frontière est explicitée dans la [documentation Flink](https://nightlies.apache.org/flink/flink-docs-stable/docs/learn-flink/fault_tolerance/). De même, conserver une référence de snapshot ne préserve pas les données après expiration : voir la [maintenance Iceberg](https://iceberg.apache.org/docs/latest/maintenance/).

## Ajouts et corrections

| Nouvelle fiche | Cartes | Mises en situation incluses |
| --- | ---: | ---: |
| 150-010 — Modélisation analytique | 16 | 3 |
| 150-011 — SQL pour les pipelines et datasets IA | 18 | 3 |
| 150-012 — Stockage colonnaire, partitions et lakehouse | 19 | 3 |
| 150-013 — Transformations et orchestration | 17 | 3 |
| 150-014 — Streaming et traitements d'événements | 17 | 3 |
| 150-015 — Calcul distribué et performance | 17 | 3 |
| 150-016 — Observabilité, lignage et exploitation | 17 | 3 |
| 150-017 — Construction de datasets et corpus IA | 18 | 3 |
| **Total des nouvelles fiches** | **139** | **24** |

Trois autres cartes complètent les fiches existantes : pagination API dans 158, puis stockage offline/online et matérialisation des features dans 159. Les **142 ajouts** comprennent **13 calculs**, **21 distinctions**, **24 mises en situation** et **84 cartes de mécanisme, choix ou diagnostic**.

Quatre réponses historiques sont corrigées, avec leurs questions et identifiants conservés :

- Déduplication : une ressemblance sémantique ne suffit pas à fusionner des exemples ; chiffres, négations et variantes peuvent être décisifs.
- Versioning : une empreinte ne prouve pas les droits d'usage, et une version nommée doit rester physiquement accessible pour être reconstruite.
- Durable execution : un historique persistant ne garantit pas l'unicité de toutes les activités distantes.
- Orchestration data et durable execution : distinguer les objectifs et garanties sans présenter les catégories d'outils comme exclusives.

Chaque nouvelle fiche contient des sources primaires et des connexions réciproques. Les sources comprennent PostgreSQL, Kimball Group, Apache Parquet/Arrow/Avro/Iceberg/Spark/Beam/Flink/Kafka/Airflow, dbt, OpenLineage, Feast, PyTorch, Hugging Face et l'article des auteurs sur la déduplication. Les exemples chiffrés sont pédagogiques ; ils ne présentent pas des tarifs ou performances de production garantis.

## Parcours conseillé et niveau attendu

La priorité dépend du rôle. Cette répartition est une recommandation éditoriale pour le vault, pas une exigence universelle de recrutement.

| Niveau | Sujets | Preuve de maîtrise attendue |
| --- | --- | --- |
| Socle de tout AI Engineer appliqué | Grain et clés, SQL, contrats, temporalité, splits, provenance, formats et droits | Construire un dataset correct, expliquer chaque ligne et retrouver la source d'une erreur |
| Autonomie sur un produit en production | Incrémental, orchestration, stockage/versioning, corpus, qualité et SLO | Rejouer, publier, diagnostiquer une dégradation et réparer sans corrompre les consommateurs |
| Approfondissement selon le poste | Streaming avec état, tuning distribué, migrations d'état, plateformes lakehouse | Tester charge et pannes sur le moteur retenu, chiffrer les compromis et exploiter la solution |

Ordre de travail : **modélisation → SQL → contrats → ingestion et temporalité → stockage et orchestration → corpus et observabilité**. Étudier le streaming et le calcul distribué dès qu'un besoin de latence ou de volume les justifie. Les notions de shuffle, état et partitionnement doivent être comprises avant de régler une configuration de cluster.

Les spécialisations suivantes restent à approfondir selon le contexte : administration détaillée d'un warehouse ou d'un cluster Kafka/Flink, formats propriétaires, réseaux et IAM propres au cloud, moteurs géospatiaux, formats audio/vidéo spécialisés et optimisation des algorithmes de moteur. Les ajouter toutes au socle nuirait à sa lisibilité. Les fiches actuelles permettent de poser les bonnes questions et de consulter les références adaptées.

## Atelier 1 — SQL, grain et disponibilité temporelle

L'[atelier exécutable](../examples/data-engineering/atelier_sql.py) utilise uniquement la bibliothèque standard Python et SQLite en mémoire, avec des données synthétiques. Les fonctions de fenêtre nécessitent SQLite 3.25 ou plus récent.

Depuis la racine du dépôt :

```bash
python3 examples/data-engineering/atelier_sql.py
```

Prédire les résultats avant l'exécution, puis expliquer les divergences. L'atelier vérifie **7 cas et 14 résultats** : multiplication des jointures, filtres de LEFT JOIN, NULL et anti-jointures, déduplication ordonnée, cadres de fenêtres, jointure respectant la disponibilité, puis rejeu et tombstone versionné.

Modifier ensuite un cas : ajouter deux commandes de même montant, un client sans feature ou un événement ancien après suppression. Justifier les nouveaux résultats et la correction éventuelle. La jointure temporelle de l'atelier suppose des états complets, un ordre de version par entité et des timestamps UTC canoniques ; elle n'est pas une implémentation générique de toute dimension bitemporelle.

**Livrable** : requêtes, jeux de cas limites et explication du grain avant/après. Les résultats doivent rester corrects quand l'ordre d'insertion change. Le script teste les exemples SQL locaux ; il ne valide pas les performances d'un warehouse ni les pannes d'un système distribué.

## Atelier 2 — Ingestion, publication et reconstruction

Construire un petit pipeline de commandes et documents versionnés. Définir contrat, pagination ou journal de changements, manifestes d'entrée et sortie, destination de quarantaine et publication d'une version validée. Produire une table analytique et une correspondance document-vers-chunks.

Injecter doublon, suppression, événement désordonné, partition manquante et crash après écriture avant checkpoint. Effectuer un backfill avec la même logique puis avec une nouvelle version, en protégeant l'état courant. Prévoir aussi une source qui continue de changer pendant une extraction.

**Livrable** : rapport de réconciliation et procédure de reprise. Les sorties ne doivent pas ressusciter un document supprimé ni déclarer complet un lot amputé. Préciser ce qui est atomique, quelle durée de rejeu est possible et quelles données deviennent irrécupérables après expiration.

## Atelier 3 — Stockage et coût d'exécution

Sur un jeu public ou synthétique adapté aux ressources disponibles, comparer une disposition peu sélective à une version Parquet partitionnée ou triée. Exécuter les mêmes requêtes, puis modifier nombre de fichiers, colonnes projetées et distribution des clés.

Mesurer temps de planification, durée, octets lus, mémoire maximale et coût selon un tarif déclaré. Commencer sur une machine ; utiliser un moteur distribué seulement si le volume ou le poste visé le justifie. Comparer jointure classique et broadcast sur une référence de taille contrôlée, puis introduire une clé chaude.

**Livrable** : résultats identiques, plans et mesures comparables, avec état du cache documenté. Une amélioration annoncée doit venir des mesures, pas du nom de l'outil. Inclure compaction, réécritures, orchestration et réserve dans le coût retenu.

## Atelier 4 — Flux, features et état

Simuler des événements horodatés avec doublons, arrivées tardives et une entrée inactive. Publier un compteur glissant et des features courantes avec une politique explicite de correction, TTL et disponibilité.

Rejouer après checkpoint, puis faire arriver un événement au-delà de la durée de déduplication. Comparer reconstruction offline et valeurs effectivement disponibles en ligne. Pour un rôle plateforme, répéter avec un moteur de flux réel et un redimensionnement avec état ; une simulation locale doit rester présentée comme telle.

**Livrable** : chronologie des événements, valeurs publiées, taille d'état et rapport de reprise. Le consommateur doit interpréter correctement totaux, deltas et rétractions. Documenter les événements exclus et les effets externes qui échappent au protocole transactionnel.

## Atelier 5 — Corpus IA et incident de données

Préparer un corpus avec plusieurs formats et familles de documents. Produire textes extraits, exemples, splits et shards à partir d'un manifeste. Tester que deux configurations de workers lisent la couverture voulue, puis comparer le mélange en documents et en tokens.

Changer le parseur sur un sous-ensemble, introduire une perte de données d'un client et un recouvrement entre familles de train et test. Faire remonter ces incidents dans des contrôles de qualité et un graphe de dépendances, jusqu'aux index ou modèles concernés.

**Livrable** : manifeste reproductible, rapport de contamination et de filtrage par segment, contrôles de couverture et plan de reconstruction des dérivés affectés. La présence de documents de référence dans un RAG peut être attendue : distinguer cet accès prévu d'une fuite des réponses d'évaluation.

## Validation et conservation

Le vault passe à **137 fiches et 2 010 cartes**, sur les mêmes 17 sections, avec **89 calculs**, **317 mises en situation** et **162 distinctions**. Aucun titre de fiche ou de section existante n'est renommé ; les anciennes affectations aux paquets Anki doivent rester stables.

Vérifications de cette livraison :

- Lint global sans erreur ni avertissement, avec compatibilité de lecture Spaced Repetition.
- Catalogues README/MOC synchronisés et liens internes contrôlés.
- Calculs ajoutés recalculés ; atelier SQL exécuté avec ses 14 résultats attendus.
- 40 tests du dépôt réussis ; leur copie temporaire inclut désormais les exemples Python pour vérifier les nouveaux liens. Archive Anki et intégrité SQLite vérifiées.
- 1 868 identifiants actifs préexistants conservés ; quatre réponses modifiées et 142 nouvelles cartes identifiées.
- Export avec 2 010 cartes actives et les 30 cartes précédemment retirées toujours suspendues ; anciennes affectations aux paquets conservées.

Les contrôles d'export comparent les fichiers produits, sans simuler l'import dans la collection personnelle d'un utilisateur. Aucun cluster Spark/Flink, stockage cloud ou service de feature store n'a été déployé pour cette revue. Les ateliers 2 à 5 sont des exercices proposés, pas des expériences annoncées comme réalisées.

Les commits séparent modélisation/SQL, stockage/calcul, orchestration/streaming, corpus/observabilité, puis documentation et atelier exécutable.
