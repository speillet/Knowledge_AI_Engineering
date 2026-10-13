# Atelier local : RAG vérifiable

Cet atelier fait diagnostiquer un système documentaire avant d'ajouter un LLM. Un corpus fictif de dix passages et dix cas annotés permet de comparer une baseline volontairement incorrecte à une politique qui respecte tenant, groupes, dates d'effet, retrait et autorité des sources.

Il utilise seulement la bibliothèque standard de **Python 3.9 ou supérieur**, sans API, GPU ni installation. Le classement est lexical et déterministe ; les faits structurés, annotés à la main, remplacent extraction et génération. Les scores sont ceux de cette simulation, pas des performances mesurées sur un modèle.

## Exécuter depuis la racine du dépôt

```bash
# Prédire les résultats avant de lire les solutions.
python3 examples/rag-verifiable/atelier_rag.py --questions

# Comparer les deux politiques sur les dix cas.
python3 examples/rag-verifiable/atelier_rag.py

# Inspecter affirmation par affirmation, avec un rapport hors du dépôt.
python3 examples/rag-verifiable/atelier_rag.py --case courant --json /tmp/rag-courant.json

# Observer un budget de recherche qui masque une contradiction.
python3 examples/rag-verifiable/atelier_rag.py --case conflit --k 1

# Exécuter les tests de sécurité, de temporalité et les variations de preuves.
python3 -m unittest discover -s tests -p 'test_atelier_rag.py' -v
```

Les commandes fonctionnent aussi depuis un autre répertoire si le chemin du script est absolu : les données sont chargées à côté du script. Aucun fichier n'est écrit sans `--json` ; le répertoire de destination du rapport doit déjà exister.

## Données et politique

- [corpus.json](corpus.json) contient les identités simulées, les passages, leurs versions, dates d'effet, groupes et faits annotés. Une identité appartient à un tenant ; un document exige le même tenant **et au moins un groupe autorisé**.
- [cases.json](cases.json) fixe les champs demandés, les preuves pertinentes et les résultats attendus. Ces références servent seulement à l'évaluation ; le résolveur consulte uniquement les passages récupérés.
- [atelier_rag.py](atelier_rag.py) applique la politique et produit la trace : passages et versions, affirmations, citations, motifs d'abstention, violations et métriques.

Le rapport contient aussi les empreintes SHA-256 du contenu normalisé du corpus et des cas exécutés, annotations attendues comprises. Elles changent si un fait ou une référence change, même sans renommer le snapshot. Conserver les fichiers d'entrée avec le rapport : une empreinte permet de reconnaître le contenu, pas de le reconstruire.

La validité suit `[valid_from, valid_until)` : au 1er novembre, la version à 45 jours remplace celle à 30 jours. Les droits sont ceux de l'identité simulée au moment de l'accès, même pour une question historique. Les identifiants de chunks sont uniques dans le snapshot ; l'identité complète d'un document comprend aussi son tenant.

Dans ce domaine fictif, les contrats ont une autorité de 2 et la FAQ de 1. Pour chaque champ, le résolveur retient l'autorité maximale parmi les preuves récupérées. Deux valeurs incompatibles à cette autorité produisent `conflict`. L'absence de preuve produit `no_evidence`. La réponse est `complete`, `partial` ou `abstain` selon les champs résolus.

La baseline prend les premiers passages du classement global et la première valeur trouvée, sans filtre ni gestion des conflits. La variante `filtered` filtre le corpus avant classement et applique la priorité métier. Le score est le nombre de mots distincts communs après normalisation ; les égalités sont départagées par identifiant de chunk. Ce choix facilite la reproduction, sans simuler BM25 ou des embeddings.

## Cas à diagnostiquer

| Cas | Ce qu'il vérifie |
| --- | --- |
| `courant` | Ancienne version, FAQ contradictoire et contrat applicable |
| `historique` | Date métier passée avec les permissions actuelles |
| `frontiere-date` | Borne de fin exclue et nouvelle version effective |
| `finance-autorisee` / `finance-interdite` | Même question, permissions différentes |
| `autre-tenant` | Une question générique retrouve la preuve du tenant authentifié |
| `conflit` | Deux contrats applicables de même autorité se contredisent |
| `sans-preuve` | Aucune source ne contient le fait demandé |
| `partiel` | Deux champs résolus et un élément absent explicitement signalé |
| `source-retiree` | Un chunk encore présent dans le snapshot est bloqué après retrait |

Avec le corpus livré et `k=4`, `filtered` respecte **10 contrats sur 10**, avec zéro passage hors périmètre. La baseline respecte **0 sur 10** et expose 20 passages hors périmètre au total. Un contrat exige aussi que **tout le contexte** soit admissible : la baseline peut échouer même si sa réponse finale paraît correcte. Ces dix cas construits ne démontrent pas une garantie générale de sécurité.

## Lire les métriques sans confondre leurs dénominateurs

| Champ du rapport | Définition |
| --- | --- |
| `precision_returned` | Preuves pertinentes récupérées / passages distincts réellement renvoyés ; si moins de k résultats existent, le dénominateur n'est pas k |
| `recall_at_k` | Preuves pertinentes récupérées / preuves pertinentes annotées |
| `reciprocal_rank` | Inverse du rang de la première preuve pertinente, ou 0 si aucune n'est récupérée |
| `citation_support` | Liens qui soutiennent exactement le fait et sont admissibles / liens émis ; dédoublonnage au sein d'une affirmation |
| `claim_support` | Affirmations ayant au moins un lien soutenant / affirmations émises |
| `expected_coverage` | Éléments attendus correctement résolus et soutenus / éléments répondables attendus |
| `requested_coverage` | Éléments attendus correctement résolus et soutenus / tous les champs demandés |
| `unexpected_claims` | Nombre de champs affirmés qui ne figurent pas dans les éléments attendus |

Un dénominateur nul donne **`null` dans le JSON et `n/a` dans le terminal**. Une abstention sans citation n'obtient pas un soutien de 100 %. Les cas sans preuve ont un rappel non défini ; le cas contradictoire a deux passages pertinents même si aucune valeur unique n'est attendue. Le rapport ne moyenne pas arbitrairement ces populations.

Le cas `partiel` atteint 100 % de `expected_coverage` mais seulement **2/3 de `requested_coverage`** : l'élément sans preuve reste demandé. Dans le cas `conflit`, la baseline obtient 100 % de soutien de citations tout en répondant à tort « 4 heures » : le document cité contient cette valeur, mais une autre source de même autorité la contredit.

## Passer aux variations et produire un livrable

1. **Changer le fait courant** sur une copie du corpus : la réponse doit changer. Sans mise à jour de la référence, le contrat doit échouer ; cela révèle le changement au lieu de le masquer.
2. **Retirer toutes les preuves d'un champ** : la réponse devient partielle ou s'abstient. Retirer seulement le contrat peut laisser la FAQ comme preuve : décider si la politique métier doit encore l'accepter.
3. **Réduire `k` à 1 sur `conflit`** : la seconde preuve disparaît, le système affirme une valeur et échoue au contrat. Un résolveur ne peut détecter un conflit qu'il n'a pas récupéré.
4. **Retirer le groupe finance de Bruno** sur une copie : la recherche et l'accès aux citations doivent perdre la preuve privée. L'atelier simule une nouvelle requête ; ajouter un cache nécessiterait aussi d'en tester la révocation.
5. **Modifier une borne de validité** : vérifier les réponses juste avant, au moment et après le changement, puis contrôler les références devenues inapplicables.

Livrable : un rapport JSON, un tableau `question | affirmation | passage/version | verdict | cause | correction`, et une courte décision sur priorité des sources et abstention. Pour réussir, expliquer un échec de recherche, une réponse fidèle mais injustifiée et une différence entre couverture des éléments répondables et couverture de toute la demande.

## Limites et prolongement vers un vrai RAG

L'identité est une fixture de confiance, **pas une authentification réelle**. L'atelier ne modélise pas les permissions changeant pendant une requête, la purge physique, les caches, les flux de réponse, les formulations libres, la disponibilité historique des documents ou un moteur ANN. L'égalité exacte des faits annotés ne remplace pas une vérification sémantique sur des textes naturels.

Pour passer à un vrai pipeline, remplacer le retriever et le générateur tout en conservant les cas, les références et la trace. Annoter le soutien des affirmations libres, contrôler les preuves absentes, puis ajouter charge, coût et révocation pendant l'exécution. L'autorité numérique de cet exemple doit être remplacée par une règle métier adaptée au sujet.

L'effet des filtres sur un index approximatif doit être mesuré avec le moteur réel ; pgvector 0.8.1 documente le filtrage après parcours de l'index et les parcours itératifs. [Documentation pgvector 0.8.1](https://github.com/pgvector/pgvector/blob/v0.8.1/README.md#filtering).

Les indicateurs de soutien et de couverture sont une adaptation pédagogique de la distinction étudiée par Liu, Zhang et Liang ; ils ne reproduisent pas leur protocole d'annotation. [Evaluating Verifiability in Generative Search Engines](https://arxiv.org/abs/2304.09848).

À lire : [RAG et droits/versions](../../20-rag/20-010-rag-droits-versions.md), [évaluation RAG](../../90-observabilite-evals/96-evals-rag-agents.md), [construction de corpus](../../150-donnees-conformite/150-017-datasets-corpus-ia.md) et [guide d'apprentissage](../../docs/apprendre-avec-les-cartes.md).
