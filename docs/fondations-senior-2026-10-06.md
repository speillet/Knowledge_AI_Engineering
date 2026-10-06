# Fondations senior : trois priorités — 6 octobre 2026

Cette extension complète le parcours LLM et agents par trois fondations transversales : choisir et valider un modèle prédictif, construire des pipelines de données fiables, et garantir les effets métier malgré les pannes et la concurrence.

## Contenu ajouté

| Bloc | Fiches | Cartes | Mises en situation |
| --- | --- | ---: | ---: |
| ML classique et validation | [Choisir un modèle](../170-ml-classique/171-choisir-modele-ml.md), [validation et métriques](../170-ml-classique/172-validation-metriques-ml.md) | 36 | 6 |
| Ingénierie des données | [Contrats et qualité](../150-donnees-conformite/157-contrats-qualite-donnees.md), [ingestion et backfills](../150-donnees-conformite/158-ingestion-cdc-backfills.md), [temporalité et variables](../150-donnees-conformite/159-donnees-temporelles-features.md) | 42 | 9 |
| Systèmes distribués | [Livraison, idempotence et concurrence](../140-system-design-produit/149-livraison-idempotence-concurrence.md), [transactions, outbox et sagas](../140-system-design-produit/140-010-transactions-outbox-sagas.md) | 32 | 6 |
| **Total** | **7 fiches** | **110** | **21** |

La nouvelle section `170-ml-classique` traite les modèles prédictifs, leur comparaison et les fuites de données. Les cinq autres fiches prolongent les sections données et system design existantes. La fiche `140-010` applique la numérotation étendue prévue par le dépôt, sans renommer les fiches historiques.

Le [MOC](../00-moc-ai-engineering.md) propose un parcours « fondations senior ». Les catalogues, statistiques, structure et parcours du README sont mis à jour. Les nouvelles fiches et leurs voisines sont reliées dans les deux sens.

## Choix pédagogiques

Chaque carte commence par une réponse directe, puis précise mécanisme, exemple ou limite. Les 110 nouvelles réponses contiennent entre **62 et 94 mots hors code**, avec une moyenne de **82,4 mots**. Cette mesure vérifie leur consistance rédactionnelle ; elle ne remplace pas la revue du fond.

Les cas pratiques couvrent notamment le choix d'une baseline, une validation trompeuse, une modification d'unité, la disparition d'une position CDC, la résurrection de documents supprimés, les labels retardés, les écritures concurrentes et un paiement réalisé avant un crash. Les cartes de calcul explicitent leurs hypothèses.

Les distinctions suivantes structurent les réponses :

- **Qualité du score et validité de l'expérience** : groupes, temps, prétraitements appris sur le train et indépendance du test final.
- **Date métier et disponibilité réelle** : une donnée ancienne mais reçue après la décision ne doit pas fuiter dans son évaluation historique.
- **Checkpoint et effet externe** : la persistance du workflow ne garantit pas l'unicité d'un paiement.
- **Garantie locale et garantie de bout en bout** : outbox, inbox et transactions ne couvrent que les ressources effectivement incluses dans leur protocole.
- **Rollback et compensation** : une correction métier n'efface pas nécessairement toutes les conséquences d'une action déjà effectuée.

Les références primaires consultées figurent dans chaque fiche : scikit-learn, TensorFlow, Feast, Apache Beam et Kafka, Debezium, Confluent, PostgreSQL, AWS, Stripe et Hazelcast. Les exemples d'architecture et de diagnostic sont pédagogiques ; ils ne constituent pas une validation d'un déploiement particulier.

## Validation et conservation

Le vault passe de **110 fiches / 1 553 cartes / 16 sections** à **117 fiches / 1 663 cartes / 17 sections**. Il contient désormais **256 mises en situation** et **113 cartes de distinction**.

Contrôles effectués :

- **Lint** : 0 erreur et 0 avertissement, y compris l'équivalence de lecture entre Obsidian et Anki.
- **Catalogues** : `sync_catalog.py --check` valide ; `git diff --check` sans anomalie.
- **Tests du dépôt** : 40 tests réussis. Deux assertions de comptage utilisent désormais `scripts/sections.json` au lieu du nombre fixe de 16 sections.
- **Conservation** : comparaison avec le commit `4b54331` ; les 1 553 anciennes questions, réponses et GUID sont strictement identiques. Seules des connexions sont ajoutées aux fiches existantes.
- **Exemples** : calculs numériques vérifiés ; écriture conditionnelle SQL exécutée dans SQLite, avec refus de la seconde écriture portant une version obsolète. Ce contrôle ne simule pas un système distribué complet.
- **Export Anki** : archive et intégrité SQLite vérifiées ; 1 663 cartes actives avec question et réponse, GUID uniques, et 30 cartes retirées suspendues.

Le paquet `dist/ai-engineering.apkg` est généré et reste exclu de Git. La CI le reconstruit et le publie après le push sur `main`. Les scénarios de panne distribuée décrits dans les cartes n'ont pas été exécutés contre des services externes.
