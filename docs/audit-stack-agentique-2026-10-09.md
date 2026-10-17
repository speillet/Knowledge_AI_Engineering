# Approfondissement de la stack agentique — 9 octobre 2026

Le dépôt possédait 94 cartes dans sept fiches consacrées à LangChain, LangGraph, CrewAI et Langfuse, avec 15 mises en situation. Il contenait aussi 130 cartes dans la section Agents, ainsi que des fiches sur le streaming, MCP/A2A/AG-UI, les évaluations, la sécurité, l'idempotence et l'exploitation. Le besoin principal était d'approfondir l'assemblage et les garanties en production, en réutilisant ces fondations.

Cet enrichissement ajoute **124 cartes dans sept nouvelles fiches**, dont **21 mises en situation, 12 distinctions et 7 calculs**. Il corrige six réponses existantes en conservant leurs questions et identifiants Anki. Le vault passe de **137 fiches et 2 010 cartes** à **144 fiches et 2 134 cartes**, avec **338 mises en situation, 174 distinctions et 96 calculs**.

## Couverture et ordre de travail

| Thématique | Fiche ajoutée | Cartes | Preuve de compréhension attendue |
|---|---|---:|---|
| Contrats LangChain | [Outils & middleware](../40-automatisation/40-010-langchain-outils-middleware-production.md) | 17 | Expliquer identité injectée, contrat de sortie, ordre des middlewares et budget de retry |
| État LangGraph | [Reprise & concurrence](../40-automatisation/40-011-langgraph-reprise-concurrence.md) | 19 | Reprendre après panne sans dupliquer un effet ; traiter concurrence et anciens états |
| Exécution CrewAI | [Exécution fiable](../40-automatisation/40-012-crewai-execution-fiable.md) | 17 | Définir dépendances, guardrails bornés, budgets et granularité de reprise |
| Traces Langfuse | [Instrumentation en production](../90-observabilite-evals/90-011-langfuse-instrumentation-production.md) | 18 | Retrouver appels, outils, reprises et coûts sans parent perdu ni double comptage |
| Expériences Langfuse | [Prompts, datasets & expériences](../90-observabilite-evals/90-012-langfuse-prompts-experiences.md) | 17 | Promouvoir une version avec un jeu comparable, des scores interprétables et un rollback observable |
| Application complète | [Architecture & cycle de vie](../140-system-design-produit/140-011-architecture-applications-agentiques.md) | 19 | Définir les contrats API, décisions humaines, droits, événements et transitions de statut |
| Validation | [Tests de contrats, pannes & reprises](../90-observabilite-evals/90-013-tests-agents-reprises.md) | 17 | Distinguer tests techniques, invariants métier et évaluation de qualité d'un vrai modèle |

Après les fiches de base, commencer par l'architecture applicative, choisir le runtime adapté au besoin, puis travailler instrumentation et tests ensemble. LangChain et LangGraph peuvent se combiner ; CrewAI offre une autre organisation des tâches ; Langfuse observe et évalue. Connaître les quatre n'impose pas de les empiler dans chaque application.

## Ce qui a été approfondi

**LangChain.** Les nouvelles cartes traitent la séparation adaptateur/service métier, les schémas utiles au modèle, `ToolRuntime`, la cohérence `tool_calls`/`ToolMessage`, les stratégies de sortie structurée, la validation métier, les erreurs réparables, les limites de l'async, les interactions de middleware, les outils dynamiques, les fallbacks et les mises à niveau. Le but est de comprendre le chemin réel d'un appel et ses contrats.

**LangGraph.** La couverture inclut les modes `sync`/`async`/`exit`, les pending writes, les frontières transactionnelles, les interruptions multiples, les reprises après erreur, la concurrence entre invocations, la fusion d'état, les sous-graphes, les migrations et les rejeux de diagnostic. Chaque garantie est reliée au backend et au périmètre qui la fournit.

**CrewAI.** Les tâches sont abordées comme des contrats vérifiables avec des dépendances explicites. Les cartes distinguent correction par guardrail, retry technique, async et durabilité ; elles développent budgets, isolation, délégation et observabilité. La restauration d'état d'un Flow et le checkpointing d'exécution sont distingués. Les références CrewAI sont épinglées sur la documentation 1.15.26 consultée.

**Langfuse.** Deux fiches complètent les fondamentaux : une sur la qualité de l'instrumentation, une sur les décisions fondées sur les expériences. Les sujets incluent propagation distribuée, traces async, générations streamées, coûts incomplets, sampling, masquage, export et doublons ; puis labels, versions, cache du registre, fallback, jeux de régression, comparabilité, provenance des scores, valeurs manquantes et feedback authentifié.

**Architecture et tests.** Les fiches relient framework, service métier et interface : statut de run, admission durable, propriété des ressources, proposition immuable, expiration, préconditions revérifiées, annulation, journal d'événements, consommateurs lents et compatibilité de déploiement. Les tests vérifient les invariants aux fenêtres de panne et avec des états historiques, au-delà du simple retour `success` du moteur.

## Corrections des fiches existantes

| Fiche | Correction |
|---|---|
| [LangGraph — Fondamentaux](../40-automatisation/44-langgraph-fondamentaux.md) | Les super-steps ne rendent pas automatiquement l'état durable : checkpointer, mode et backend doivent être configurés. |
| [LangGraph — Production](../40-automatisation/45-langgraph-production.md) | Isoler un effet dans une tâche ne garantit pas son exécution unique ; un crash après acceptation distante peut conduire à le redemander. |
| [Langfuse — Fondamentaux](../90-observabilite-evals/91-langfuse-observabilite.md) | L'export OpenTelemetry doit être configuré ; les traces d'une gateway ne couvrent pas seules tout le workflow. |
| [CrewAI — Crews](../40-automatisation/46-crewai-crews.md) | Une URL accessible ne prouve pas qu'une affirmation est soutenue par la source. Les corrections sont bornées. |
| [CrewAI — Flows](../40-automatisation/47-crewai-flows.md) | Retrouver les variables persistées et reprendre le contrôle d'exécution sont deux garanties à vérifier séparément. |
| [Streaming applicatif](../80-api-layer-routing/84-streaming-integration-applicative.md) | Le premier contenu n'arrive pas toujours en quelques centaines de millisecondes ; le coût dépend aussi du travail consommé et de l'annulation effective. |

Les dates générales des anciennes fiches ne sont pas artificiellement renouvelées : cette revue cible ces réponses, elle ne prétend pas revalider toutes les API mentionnées sur toutes leurs cartes.

## Atelier exécutable et exercices complémentaires

L'[atelier support](../examples/agentic-support/README.md) fournit un vrai graphe LangGraph, des composants LangChain, le SDK Langfuse avec exporteur local et une API FastAPI. Son modèle est simulé ; ses données et sa politique métier sont synthétiques. Il ne demande aucune clé de modèle ni de service distant.

Trois scénarios s'exécutent avec `demo.py` : approbation, refus et panne après effet métier. Les tests vérifient aussi la persistance après reconstruction, la mort d'un processus entre COMMIT métier et checkpoint, l'isolation des clients, les doubles soumissions/décisions, les préconditions obsolètes, l'expiration et les événements SSE. Le registre métier et les checkpoints sont deux bases distinctes pour rendre visible la fenêtre de panne.

La reprise sans doublon est obtenue par une identité stable et une transaction métier contenant l'effet et sa déduplication. Ce choix pédagogique ne confère pas automatiquement la même garantie à une API distante.

| Exercice | Livrable | Critère de réussite |
|---|---|---|
| Reprise locale | Résultats des tests et explication de la fenêtre de panne | Un seul avoir malgré une panne après son enregistrement |
| Variante CrewAI | Flow/crew utilisant le même contrat métier | Refus, reprises et isolation conservent les mêmes invariants ; exercice à implémenter |
| Instance Langfuse | Trace complète, prompt versionné et score relié | Parenté correcte, données minimisées, aucun double comptage ; intégration distante à réaliser |
| Vrai modèle | Dataset figé, sorties, métriques et analyse d'erreurs | Résultat métier, coût et latence mesurés sur des essais comparables ; qualité non évaluée par le modèle simulé |
| Application distribuée | API d'admission, workers, reprise, migrations et scénario de charge | Garanties démontrées entre processus/réplicas ; au-delà du verrou local de l'atelier |

L'atelier n'implémente ni authentification de production, ni file distribuée, ni frontend, ni recherche vectorielle. Son SSE est un rejeu fini d'événements, pas un abonnement continu. La variante CrewAI est guidée, pas présentée comme exécutée. Cette distinction évite de confondre un exemple pédagogique vérifié avec une application prête à déployer.

## Méthode d'apprentissage

Pour chaque sujet, répondre à une carte de mécanisme, puis à une distinction et à une mise en situation. Écrire ensuite une prédiction vérifiable : quel état subsiste après crash, combien d'actions sont créées, quelles observations sont attendues ? Exécuter le test et expliquer un écart éventuel.

Une bonne réponse senior précise **qui fournit la garantie, ce qu'elle couvre et comment elle échoue**. « Le framework gère la reprise » est insuffisant sans dire quelles écritures sont persistées, quel code est rejoué et comment un effet externe est dédupliqué. Les fiches sont un support de rappel ; l'atelier et les exercices produisent les preuves.

## Validation

- Format, liens réciproques, catalogues et lecture compatible avec Obsidian Spaced Repetition.
- Conservation des 2 010 questions et identifiants préexistants ; aucune ancienne fiche renommée.
- Recalcul des sept nouveaux exemples numériques, avec données et hypothèses sur le recto.
- Tests du vault et export Anki ; contrôles de structure du paquet et unicité des identifiants.
- **40 tests du vault** et **18 tests de l’atelier** réussis ; trois dossiers de démonstration validés. Les sept cartes de calcul correspondent à onze résultats numériques recalculés.
- Atelier exécuté sous Python 3.10 avec les dépendances épinglées, séparées des paquets système ; CI dédiée ajoutée pour les changements de l’atelier. Une réussite locale ne préjuge pas de l’état des exécutions CI distantes.

Les documentations primaires sont citées dans chaque fiche. L'instrumentation Langfuse est validée avec son SDK et un exporteur en mémoire ; l'ingestion distante, les vrais modèles et une implémentation CrewAI du projet ne sont pas validés par ces tests locaux.
