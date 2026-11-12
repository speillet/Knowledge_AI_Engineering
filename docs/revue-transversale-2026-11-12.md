# Enrichissement et pertinence des fiches — 12 novembre 2026

Les 147 fiches restent pertinentes pour apprendre à concevoir, évaluer et exploiter des systèmes IA. Le socle ne se limite pas aux LLM : validation ML, temporalité des données, transactions et exploitation expliquent une grande partie des erreurs rencontrées en production. Les fiches sur les frameworks, protocoles et infrastructures spécialisées sont des approfondissements à choisir selon les projets ; les apprendre toutes avant de pratiquer n'est pas un prérequis.

Cette passe ajoute **147 cartes**, une dans chaque fiche, dont **15 calculs**, et corrige ou précise **10 réponses existantes**. Le vault passe de **2 186 à 2 333 cartes**, toujours dans 17 sections. Les réponses ajoutées représentent **12 493 mots** ; chacune contient entre 74 et 95 mots. Ces chiffres décrivent le périmètre, pas une mesure d'efficacité pédagogique.

## Méthode et portée de la vérification

Le point de départ est la version distante `2a0f84e`, qui contient déjà les enrichissements de début novembre. L'inventaire des 2 186 questions et réponses a servi à sélectionner les compléments ; la lecture et la confrontation aux sources sont ciblées sur les notions ajoutées, les réponses proches et les affirmations sensibles. Il ne s'agit pas d'une revérification ligne par ligne de toutes les affirmations historiques du vault.

Les ajouts privilégient une question autonome, une réponse directe, un mécanisme expliqué et une limite d'application. Les exemples chiffrés sont pédagogiques, avec leurs hypothèses ; ce ne sont ni des prix actuels ni des benchmarks matériels. Une comparaison lexicale entre ajouts et réponses antérieures, suivie d'une revue des résultats proches, a conduit à réorienter **11 propositions** pour éviter de redéfinir des notions déjà couvertes. Un calcul d'application peut compléter une définition sans constituer une nouvelle définition à réciter.

Les **2 186 identifiants Anki existants et les questions correspondantes sont conservés**. Les seules nouvelles identités sont celles des 147 nouvelles cartes. Les résumés de 146 fiches sont complétés, puis le catalogue est régénéré ; l'index conteneurs conserve son format particulier. Les dates globales `Vérifié le` ne sont pas renouvelées par une simple consultation ciblée : les nouvelles sources indiquent le périmètre de cette consultation.

## Couverture et intérêt des ajouts

| Section | Cartes ajoutées | Compléments de cette passe |
| --- | ---: | --- |
| Prompt engineering | 3 | Tests métamorphiques, contraintes critiques d'optimisation, migration du contrat de sortie. |
| RAG | 8 | Diagnostic avec preuves de référence, RRF, provenance, réversibilité de mémoire, overlap, échantillonnage SQL, révocation et indépendance des sources. |
| Agents | 9 | Fin de tâche observable, proposition et exécution, compatibilité MCP, tests négatifs, compaction, chemin critique, choix de framework, quotas et mémoire inférée. |
| Automatisation et frameworks | 12 | Rejeu déterministe, refus d'autorisation, effets après guardrail, webhooks, messages structurés, budgets, approbations et tests indépendants. |
| Fine-tuning | 6 | Génération libre, préférences biaisées, déduplication synthétique, efficacité parallèle, isolation des épisodes et comparabilité des pertes. |
| Inférence | 12 | Rafales, réservations KV, coût marginal, partage physique, équité du prefill, inconnus structurés, durée complète et isolation du cache. |
| Conteneurs et infrastructure | 14 | Démarrage réel, plateformes OCI, secrets, localisation des pannes, probes, permissions, VRAM, topologie, poids atomiques et drainage. |
| API et routage | 5 | Réconciliation de facture, coût d'une cascade, timeouts, reconnexion SSE et annulation A2A. |
| Observabilité et évaluations | 13 | Affirmations vérifiables, traces asynchrones, test protégé, injection de panne, échantillonnage, biais des juges, effets externes et tests séquentiels. |
| Sécurité | 6 | Faux positifs, résultats d'outils piégés, approbation exacte, SSRF, attestations et droits du code de test. |
| MLOps | 7 | Manifeste de release, rollback de schéma, labels tardifs, stabilité par tâche, révocation, RTO/RPO et promotions concurrentes. |
| Coûts | 3 | Économie nette du cache, réservation des appels en vol et faux équivalents sémantiques. |
| Fondamentaux LLM | 8 | Attention et explication, troncature, cosinus/L2, ex æquo ANN, extrapolation, experts par batch, preuves multiples et rendement du raisonnement. |
| System design et produit | 11 | Retard d'outbox, soumission incertaine, coût d'erreur, circuit breaker, preuve applicable, correction locale, capacité humaine et frontière de Pareto. |
| Données et conformité | 17 | Moyennes pondérées, SQL déterministe, pushdown, publication concurrente, état de flux, skew, retrait des données et contrats sémantiques. |
| Multimodal et edge | 5 | Résolution et preuve, unités des tableaux, interruption audio, régime thermique et écran modifié avant clic. |
| ML classique | 8 | Catégories inconnues, balanced accuracy, ECE, rappel conditionnel, MAPE, quotas d'alertes, stabilité des explications et interférence causale. |

Les fiches conteneurs et HPC gardent leur pertinence pour l'inférence auto-hébergée. Elles sont optionnelles pour un produit consommant uniquement une API. Les fiches ML classique et données forment au contraire un socle utile même lorsqu'un LLM prend la décision finale. Les noms de frameworks aident à situer les exemples ; leurs garanties doivent rester vérifiées sur la version utilisée.

## Réponses existantes corrigées ou précisées

| Fiche | Correction |
| --- | --- |
| [MCP](../30-agents/33-mcp.md) | Exemple de configuration explicitement fictif et propre au host ; retrait d'un exemple de paquet tiers dont la version n'est pas établie par la spécification. |
| [containerd et runc](../70-containers-infra/03-containerd-runc.md) | crun n'est plus présenté comme universellement plus rapide ni comme le défaut garanti de toutes les distributions citées. |
| [Primitives Linux](../70-containers-infra/08-linux-primitives-docker-fondamentaux.md) | Performances des volumes et couches dépendantes du stockage ; poids dans l'image présentés comme un compromis possible. |
| [Embeddings](../130-fondamentaux-llm/133-embeddings-representations.md) | Équivalence cosinus, produit scalaire et L2 conditionnée à la normalisation ; retrait d'une supériorité de vitesse générale. |
| [Parsing de documents](../160-multimodal-edge/162-document-parsing.md) | PDF mixtes et scans déjà OCRisés ; un seuil de caractères ne suffit pas à décider d'un OCR ni à valider le texte. |
| [LLM locaux](../160-multimodal-edge/164-llm-local-edge.md) | Trois réponses revues : quotient de bande passante présenté comme une borne simplifiée, GGUF non limité aux poids quantifiés ni à un fichier unique, offload `-ngl` et comparaison des machines explicitement conditionnels. |
| [AI Act](../150-donnees-conformite/155-ai-act.md) | Une agrégation des résultats n'efface pas une inférence d'émotions interdite en amont ; une autre collecte doit être étudiée sans réintroduire cette fonction. |
| [Protocoles agentiques](../80-api-layer-routing/85-carte-protocoles-agentiques.md) | Gouvernance ouverte distinguée des garanties de sécurité, de compatibilité et de pérennité d'une implémentation. |

## Points confrontés aux sources primaires

- **MCP** : la [compatibilité de la révision 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28/basic/versioning) distingue requêtes modernes et clients historiques. Les [bonnes pratiques de sécurité](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices) couvrent notamment SSRF et autorisation. Il n'y a pas lieu de remplacer cette révision par une ancienne au seul motif qu'elle est plus familière.
- **AI Act et RGPD** : le [calendrier publié par la Commission](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai) confirme les échéances de haut risque déjà citées dans le vault, dont décembre 2027 et août 2028. La qualification dépend de l'[article 6](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-6) ; l'[article 5](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-5) encadre l'interdiction d'inférer les émotions au travail. Les finalités et bases légales restent à examiner selon le [RGPD](https://eur-lex.europa.eu/eli/reg/2016/679/oj/fra), notamment ses articles 5 à 7 et 13.
- **Exécution des agents** : la [Functional API de LangGraph](https://docs.langchain.com/oss/python/langgraph/functional-api) documente le rejeu et les opérations non déterministes ; les [interruptions](https://docs.langchain.com/oss/python/langgraph/interrupts) demandent un ordre cohérent. Les [guardrails de tâches CrewAI](https://docs.crewai.com/en/concepts/tasks) portent sur la sortie et les retries ; la séparation des effets métier est une recommandation d'architecture construite à partir de ce comportement.
- **Serving** : vLLM documente le [partage de blocs KV](https://docs.vllm.ai/en/latest/design/prefix_caching/) et le [sel de cache secret par périmètre de confiance](https://docs.vllm.ai/en/latest/usage/security/). La documentation officielle [OpenAI sur les sorties structurées](https://developers.openai.com/api/docs/guides/structured-outputs) distingue conformité de schéma, refus et réponse incomplète. La [spécification A2A](https://a2a-protocol.org/latest/specification/) ne garantit pas qu'une demande d'annulation réussira.
- **Infrastructure** : le [cycle de vie Kubernetes](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/) distingue les trois sondes. L'[index OCI](https://github.com/opencontainers/image-spec/blob/main/image-index.md) référence des plateformes distinctes. Les documentations Docker expliquent les [secrets de build](https://docs.docker.com/build/building/secrets/) et les [drivers de stockage](https://docs.docker.com/engine/storage/drivers/). Les performances d'un [runtime comme crun](https://github.com/containers/crun) restent à mesurer sur la cible.
- **Documents et local** : PyMuPDF expose un [OCR complet ou partiel](https://pymupdf.readthedocs.io/en/latest/ocr/index.html) ; les [options du serveur llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md) rendent l'offload configurable. Les précisions de cette revue ne sont pas des mesures sur un GPU ou un appareil physique.
- **Mesures ML** : les [métriques scikit-learn](https://scikit-learn.org/stable/modules/model_evaluation.html), la [calibration](https://scikit-learn.org/stable/modules/calibration.html) et le chapitre d'[évaluation des prévisions](https://otexts.com/fpp3/toolbox.html) soutiennent les distinctions de métriques. Les exemples numériques sont recalculés séparément.

Les sources ajoutées sont des points de contrôle identifiés. Elles ne constituent pas une certification juridique, un audit de sécurité du code des produits cités ni une validation de toutes leurs versions. Les cartes de décision proposent des raisonnements et expériences à conduire, pas des garanties universelles dérivées d'un fournisseur.

## Validation

- Lint avant modification : **147 fiches, 2 186 cartes, zéro erreur et zéro avertissement**.
- Lint après modification : **147 fiches, 2 333 cartes, zéro erreur et zéro avertissement**.
- Comparaison par identifiants : **2 186 cartes historiques conservées**, questions inchangées, **10 réponses modifiées**, **147 cartes ajoutées** ; aucune carte retirée.
- Recalcul des **15 nouveaux exercices** : hypothèses, unités et résultats contrôlés, dont 8,78 s pour 400 tokens, 18 € de moyenne pondérée, 3,6 millions d'entrées d'état et 60 % de rappel final.
- `make check` : lint, synchronisation du catalogue, ruff, mypy, **54 tests** et deux ateliers locaux réussis avec Python 3.13.
- `make export` : génération du paquet Anki et contrôle de ses identifiants et de son nombre de notes.
- `git diff --check` : absence d'erreur d'espacement.

Les tests de structure et d'export protègent l'utilisation dans Obsidian et Anki ; ils ne prouvent pas l'exactitude du contenu. Les appels réels aux modèles, charges GPU et services métier ne sont pas exécutés dans cette passe documentaire. Les vérifications CI sur les versions Python du dépôt complètent la validation locale avant fusion.

Pour réviser les compléments, commencer par ceux qui correspondent à un problème rencontré dans un projet, puis appliquer une carte de calcul ou de diagnostic sur un cas réel. Le [guide d'apprentissage](apprendre-avec-les-cartes.md) reste le point d'entrée pour éviter de confondre volume de cartes et maîtrise pratique.
