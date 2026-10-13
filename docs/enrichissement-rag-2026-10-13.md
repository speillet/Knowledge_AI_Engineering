# Enrichissement du dépôt — 13 octobre 2026

Le dépôt couvre déjà largement les modèles, les agents, l'inférence, les données et leur exploitation. Le parcours d'apprentissage et les revues antérieures montrent surtout un besoin de **preuves pratiques reproductibles** : savoir réciter une règle ne suffit pas à diagnostiquer un résultat de pipeline.

Cette passe réalise l'atelier RAG proposé dans les [approfondissements de la revue du 11 octobre](revue-pertinence-2026-10-11.md). Elle ajoute une fiche spécialisée et relie l'exercice aux parcours existants.

## État de départ et périmètre

État observé : **138 fiches, 2 059 cartes**, 326 mises en situation et 166 cartes de confusion. Le lint et les catalogues étaient conformes. Des modifications locales étaient déjà présentes, notamment la fiche d'évaluation des réponses et le parcours plateforme : elles sont conservées.

La recherche des lacunes a porté sur l'organisation, les parcours, la revue de pertinence, les ateliers et les passages RAG relatifs aux droits, à la fraîcheur et aux évaluations. Cette passe ne constitue pas une revue factuelle exhaustive des 138 fiches préexistantes ni une mesure de l'apprentissage.

## Ajouts réalisés

| Ajout | Compétence travaillée | Preuve disponible |
| --- | --- | --- |
| [RAG : droits, versions et abstention](../20-rag/20-010-rag-droits-versions.md) | Identité authentifiée, filtres, dates d'effet, autorité des sources, citations, retraits et caches | 19 cartes, dont deux calculs, deux distinctions et trois mises en situation |
| [Atelier RAG vérifiable](../examples/rag-verifiable/README.md) | Diagnostiquer recherche, applicabilité des sources et réponse finale | Dix passages fictifs, dix cas annotés et rapport JSON affirmation/citation |
| [Tests de l'atelier](../tests/test_atelier_rag.py) | Détecter une fuite, une borne temporelle incorrecte ou une évaluation trompeuse | Régressions sur deux tenants, droits révoqués, preuves modifiées/retirées et conflit masqué |
| Intégration aux parcours | Passer des cartes à un livrable de validation | README, MOC, guide d'apprentissage, étape 5 du parcours plateforme et quatre liens réciproques |

Les fiches existantes reçoivent des liens ; leurs cartes et identifiants restent inchangés. Les dates de vérification antérieures restent conservées. La nouvelle fiche cite les sources primaires consultées pour cette passe.

La revue avant publication confirme que la fiche approfondit les règles de production évoquées dans le RAG avancé, tandis que l'atelier les rend observables sans dépendance à un modèle. Elle renforce la traçabilité : chaque rapport contient les empreintes SHA-256 du corpus et des cas exécutés. Les tests vérifient qu'une modification d'un fait ou d'une référence change l'empreinte correspondante, même si le nom du snapshot reste identique.

## Résultats pédagogiques et limites

Avec le corpus fourni et `k=4`, la politique filtrée respecte **10/10 contrats**, contre **0/10** pour la baseline volontairement incorrecte. Elle place zéro passage hors périmètre dans le contexte, contre 20 occurrences pour la baseline. Le contrat inclut l'admissibilité de tout le contexte, même lorsqu'un passage interdit n'est finalement pas cité.

Le cas contradictoire montre une réponse dont la citation est soutenue à 100 %, mais qui tranche à tort entre deux contrats de même autorité. Le cas partiel montre 100 % de couverture des éléments répondables et seulement 2/3 des éléments demandés. Les métriques sans dénominateur restent non définies ; elles ne deviennent pas automatiquement des succès.

L'atelier utilise un classement lexical exact et des faits structurés annotés manuellement. Il n'implémente ni authentification réelle, ni embeddings, ni LLM, ni cache ou purge physique. Les droits actuels sont simulés, et les dates représentent la validité métier plutôt que la disponibilité historique des données. Les résultats décrivent ces cas construits ; ils ne garantissent pas le comportement d'un service réel.

## Sources primaires et portée

- [PostgreSQL 18 — Row Security Policies](https://www.postgresql.org/docs/18/ddl-rowsecurity.html) : politiques de ligne et rôles qui peuvent les contourner.
- [pgvector 0.8.1 — Filtering](https://github.com/pgvector/pgvector/blob/v0.8.1/README.md#filtering) : filtrage après parcours d'un index approximatif, compromis de rappel et parcours itératifs.
- [Liu, Zhang et Liang — Evaluating Verifiability in Generative Search Engines](https://arxiv.org/abs/2304.09848) : distinguer soutien des citations et couverture des affirmations.

Les politiques de priorité, les intervalles métier et les démarches d'invalidation sont des choix pédagogiques explicités dans la fiche et l'atelier ; ces références ne valident pas à elles seules une architecture de production particulière.

## Prochaines priorités identifiées

| Priorité | Amélioration possible | Critère de réussite |
| --- | --- | --- |
| 1 | Atelier sur les effets d'outils et les reprises | Distinguer timeout avant/après écriture, résultat inconnu et reprise sans mutation dupliquée |
| 2 | Atelier de qualification d'un juge | Comparer annotations humaines, style, injections et erreurs par segment, avec couverture de la revue |
| 3 | Catalogue des ateliers et des livrables | Retrouver pour chaque parcours un exercice, ses prérequis, sa commande et un résultat vérifiable |

Ces priorités prolongent les sujets existants ; elles ne sont pas implémentées dans cette passe. L'ajout d'un backend réel au RAG devra conserver les cas contrôlés, puis étendre les annotations aux formulations libres et mesurer qualité, latence, coût et révocation.

## Validation

Résultats obtenus :

- **139 fiches, 2 078 cartes**, 329 mises en situation et 168 cartes de confusion ; zéro erreur et zéro avertissement au lint.
- **51 tests réussis** sous Python 3.12 avec les dépendances épinglées ; les 11 tests de l'atelier réussissent aussi avec le Python système 3.9 et sa seule bibliothèque standard.
- Catalogues conformes et **348 liens locaux contrôlés** dans le README, le MOC, les documents et le guide du nouvel atelier.
- Export Anki généré : **2 078 cartes actives et 30 cartes retirées suspendues**, base SQLite intègre.
- Les questions, réponses et identifiants des **2 059 cartes préexistantes sont conservés**, vérifiés contre une copie de l'état initial.

Les vérifications portent sur le format des cartes, leurs liens et identifiants, les catalogues, l'atelier et l'export Anki. Les commandes reproductibles sont :

```bash
python3 scripts/lint_flashcards.py --stale-months 0
python3 scripts/sync_catalog.py --check
python3 -m unittest discover -s tests -v
python3 scripts/export_anki.py
python3 examples/rag-verifiable/atelier_rag.py --questions
python3 examples/rag-verifiable/atelier_rag.py --json /tmp/rag-validation.json
```

La suite complète et l'export nécessitent les dépendances épinglées de `scripts/requirements.txt` ; l'atelier seul reste utilisable avec la bibliothèque standard.
