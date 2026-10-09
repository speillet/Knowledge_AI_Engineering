# Atelier : un dossier support avec approbation et reprise

Cet atelier relie un outil LangChain, un modèle LangChain simulé, un graphe LangGraph persistant, l'instrumentation Langfuse et une API FastAPI. Il permet de constater les effets d'une interruption, d'un refus et d'une panne après écriture métier. Toutes les commandes de démonstration utilisent des données synthétiques ; aucun modèle payant ni service Langfuse distant n'est appelé.

Le parcours associé est décrit dans l'[audit agentique](../../docs/audit-stack-agentique-2026-10-09.md). Les **18 tests** de l’[atelier](test_atelier.py) font partie de l'atelier : lire leurs invariants, prédire le résultat, puis les exécuter.

## Installation

Python 3.10 ou plus récent ; ensemble vérifié sous Python 3.10 et Linux. Depuis ce dossier :

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-lock.txt
python demo.py
python -m unittest -v test_atelier
```

Le téléchargement initial des paquets nécessite Internet. La démonstration et les tests fonctionnent ensuite localement. Le [fichier des dépendances directes](requirements.txt) explique les briques retenues ; le [fichier verrouillé](requirements-lock.txt) contient les 61 versions utilisées lors de la validation. Les dépendances de cet atelier sont indépendantes de celles de l'export Anki.

`demo.py` construit trois environnements temporaires indépendants : approbation, refus et panne injectée après effet. Il vérifie respectivement un avoir, zéro avoir et un seul avoir après reprise. Sa sortie indique explicitement `real_model_quality: not_evaluated`.

## Chemin d'exécution

```text
API : identité de démonstration + clé de soumission
    ↓
registre du dossier dans business.sqlite
    ↓
LangGraph : propose
    ├── outil LangChain : lecture de commande avec tenant injecté
    ├── récupération exacte d'une politique synthétique versionnée
    └── modèle simulé → validation Pydantic + contrôles métier
    ↓
LangGraph : approve → interrupt → checkpoint SQLite
    ↓ décision liée à l'empreinte de la proposition
LangGraph : execute
    └── transaction métier : préconditions + avoir + déduplication
    ↓
checkpoint du résultat et état public completed
```

La version de commande, l'expiration et la version de politique sont fixées par le serveur. Une proposition ne change pas pendant l'approbation. Le service métier revérifie la décision, le solde et la version avant de créer l'avoir.

Deux fichiers matérialisent deux frontières transactionnelles : `business.sqlite` porte les dossiers, décisions, avoirs et événements ; `checkpoints.sqlite` porte l'état LangGraph. Ils ne sont pas validés atomiquement ensemble. La clé de l'effet est l'identifiant stable du dossier, et le service métier enregistre effet et déduplication dans la même transaction. Ce contrat permet de rejouer après une panne entre les deux bases. Pour un remboursement distant réel, cette garantie doit être assurée par le service distant ou par un protocole de réconciliation adapté.

## Manipuler l'API

Lancer un seul processus, sur l'interface locale :

```bash
uvicorn api:create_app --factory --host 127.0.0.1 --port 8000 --workers 1
```

Ouvrir `http://127.0.0.1:8000/docs` pour explorer le contrat. Deux identités fictives existent : en-tête `Authorization: Bearer alice-demo` ou `Authorization: Bearer bob-demo`. Elles sont publiques et servent uniquement à démontrer l'isolation ; ne pas exposer cette application sur Internet.

Créer un dossier :

```bash
curl -sS http://127.0.0.1:8000/runs \
  -H 'Authorization: Bearer alice-demo' \
  -H 'Idempotency-Key: exemple-1' \
  -H 'Content-Type: application/json' \
  -d '{"order_id":"commande-1","amount_cents":2000}'
```

La réponse contient `id`, `status: waiting`, `proposal` et `proposal_hash`. Copier les valeurs dans la commande suivante ; le hash lie la décision à la proposition précise :

```bash
curl -sS http://127.0.0.1:8000/runs/REMPLACER_ID/decision \
  -H 'Authorization: Bearer alice-demo' \
  -H 'Content-Type: application/json' \
  -d '{"proposal_hash":"REMPLACER_HASH","approved":true}'
```

Essayer aussi `approved: false` sur un autre dossier. Un refus enregistré est terminal. La répétition de la même décision est sans effet supplémentaire ; une décision contradictoire est refusée. La même clé de soumission retrouve le même dossier pour le même tenant et le même contenu ; un contenu différent renvoie HTTP 409.

| Opération | Route | Ce qu'elle démontre |
|---|---|---|
| Consulter | `GET /runs/{id}` | Propriété du dossier et projection publique de l'état |
| Décider | `POST /runs/{id}/decision` | Décision persistée liée à l'empreinte |
| Reprendre | `POST /runs/{id}/retry` | Reprise du même thread, sans nouvelle soumission |
| Annuler | `POST /runs/{id}/cancel` | Annulation avant décision ; refus si l'effet est ambigu ou déjà exécuté |
| Lire les événements | `GET /runs/{id}/events` | Rejeu SSE fini, filtré par dossier |

Pour relire seulement les événements suivant le numéro 3 :

```bash
curl -N http://127.0.0.1:8000/runs/REMPLACER_ID/events \
  -H 'Authorization: Bearer alice-demo' \
  -H 'Last-Event-ID: 3'
```

Le journal est persistant et la réponse SSE se ferme après les événements disponibles. Ce n'est pas un abonnement en direct ni du streaming de tokens. Les numéros sont globaux à la base : des trous entre deux événements d'un même dossier sont normaux. La déconnexion de ce canal ne relance ni n'annule le dossier.

Le répertoire par défaut est `.lab-data`, ignoré par Git. Définir `AGENTIC_LAB_DIR` pour utiliser un autre emplacement. Arrêter le serveur avant de changer d'environnement de données. Les commandes sont recréées uniquement si elles n'existent pas déjà : un redémarrage ne réinitialise pas les soldes.

## Observer les traces

Le vrai SDK Langfuse exporte vers `InMemorySpanExporter`, fourni par OpenTelemetry. Les observations sont nommées `support-run`, `read-order`, `retrieve-policy`, `propose-refund` et `commit-refund`. Le test dédié vérifie leurs relations parent-enfant. Chaque reprise produit une nouvelle trace liée au même `run_id`.

Ces observations ne sont pas envoyées vers un projet Langfuse. Elles disparaissent avec le processus ; le journal des événements métier, lui, reste dans SQLite. Aucun token ni coût fictif n'est présenté comme une mesure de modèle réel. Le SDK utilise des identifiants factices explicites et LangSmith est désactivé dans le contexte d'exécution du graphe.

Pour un exercice d'intégration sur une instance Langfuse autorisée, remplacer l'exporteur local par la configuration de cette instance, garder les données synthétiques et vérifier ingestion, masquage, prompts, coûts et scores. Cette étape n'a pas été exécutée dans la validation locale.

## Expériences à réaliser

1. **Persistance** : soumettre un dossier, arrêter le serveur en attente d'approbation, le relancer avec les mêmes fichiers puis décider. Il doit conserver la même proposition.
2. **Fenêtre de panne** : lire `test_process_exit_after_effect_is_recovered`. Le processus fils s'arrête avec `os._exit(73)` après le COMMIT métier, avant le checkpoint suivant. La reprise doit rendre un seul avoir.
3. **Course métier** : préparer deux dossiers sur la même commande, approuver le premier, puis le second. La version de commande du second est périmée : il doit être bloqué. Le test de version métier reproduit ce contrôle.
4. **Observabilité** : retirer une observation ou altérer son parent dans une copie de travail et constater la régression du test de traces.
5. **Isolation** : essayer les routes de consultation et de décision avec l'identité de l'autre client ; aucune donnée du dossier ne doit être renvoyée.

## Variante CrewAI à construire

La fiche [CrewAI — Exécution fiable](../../40-automatisation/40-012-crewai-execution-fiable.md) décrit le contrat attendu. Cette variante est un exercice guidé, elle n'est pas implémentée dans l'atelier :

- Un Flow porte le dossier et appelle une crew uniquement pour produire la proposition ; une tâche définit son schéma de sortie et ses dépendances.
- Un guardrail vérifie la proposition sans effectuer le remboursement. Les corrections et les délégations ont un budget borné.
- La décision humaine reste associée au contenu exact ; l'exécution appelle le même service métier `Store.refund`, avec une identité d'opération stable.
- Choisir explicitement réhydratation d'état ou checkpointing selon la version CrewAI retenue, puis réexécuter les scénarios de refus, de panne et d'isolation.

Comparer les garanties observées et le coût de maintenance des deux versions. Aucun avantage de qualité ou de performance d'un framework n'est déduit de cet atelier simulé.

## Limites à traiter avant une application réelle

L'API exécute le petit workflow local de façon synchrone jusqu'à la pause ; elle n'annonce pas une file de workers distribués. Un verrou de processus sérialise toutes les commandes et limite volontairement la concurrence. Les tests concurrents démontrent ce périmètre uniquement. Les jetons de démonstration ne gèrent ni expiration, ni rôles, ni révocation.

Le scénario ne valide pas de fournisseur LLM réel, de recherche vectorielle, d'instance Langfuse distante, de PostgreSQL, de panne réseau ou d'authentification de production. Le modèle est contrôlé et le retrieval consiste en une politique synthétique sélectionnée directement. Les tests techniques ne mesurent donc pas la qualité d'un agent autonome.

Pour industrialiser : authentification réelle, autorisations réévaluées, file et workers durables, admission distribuée, rétention des checkpoints/événements, gestion des curseurs expirés, migrations, annulation en cours d'effet et observabilité persistante. Définir ces garanties avant de remplacer les composants locaux : changer SQLite pour PostgreSQL ne les fournit pas automatiquement.
