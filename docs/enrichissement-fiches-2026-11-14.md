# Enrichissement des fiches existantes — 14 novembre 2026

Les **150 fiches existantes** sont enrichies, dans les 17 sections. Le vault passe de **2 440 à 2 711 cartes** : **271 ajouts**, dont **23 calculs**, et **18 réponses existantes approfondies ou corrigées**. Les 2 440 questions et identifiants antérieurs sont conservés ; aucune carte existante n'est retirée.

Le travail part de `main` au commit `a744073`, après récupération des neuf commits manquants. Il approfondit le contenu des fiches sans créer de nouvelle fiche thématique. Le README et les points d'entrée sont actualisés ; les parcours historiques gardent leurs bilans datés.

## Choix pédagogiques

Les ajouts portent sur des mécanismes, des hypothèses de calcul, des contre-exemples et des critères de diagnostic. Exemples : limites d'un reranker, monde ouvert d'un graphe, arguments d'outils streamés, fragmentation du KV cache, espérance des tokens spéculatifs, préconditions d'écriture, biais de sélection et temps de disponibilité des features.

La relecture a écarté **29 propositions qui recouvraient des cartes déjà présentes**. Les notions déjà bien expliquées ne sont pas redéfinies sous une nouvelle identité. Les fiches SQL et d'évaluation des réponses sont approfondies directement dans leurs cartes de référence ; d'autres reçoivent à la fois des ajouts et des précisions.

Les rectos de calcul indiquent données, unités et hypothèses. Les tarifs sont des hypothèses d'exercice, pas des prix fournisseurs actuels. Les réponses expliquent l'interprétation et les limites, en restant sous les seuils de longueur du dépôt. Une mise en situation supplémentaire complète l'index des conteneurs ; le vault compte désormais **364 mises en situation** et **201 cartes « à ne pas confondre »**.

## Répartition

| Section | Fiches | Cartes avant | Cartes après | Ajouts |
| --- | ---: | ---: | ---: | ---: |
| 10-prompt-engineering | 3 | 43 | 47 | +4 |
| 20-rag | 8 | 121 | 136 | +15 |
| 30-agents | 9 | 140 | 156 | +16 |
| 40-automatisation | 12 | 185 | 209 | +24 |
| 50-fine-tuning | 6 | 90 | 102 | +12 |
| 60-inference-llm | 13 | 249 | 273 | +24 |
| 70-containers-infra | 14 | 164 | 191 | +27 |
| 80-api-layer-routing | 5 | 67 | 77 | +10 |
| 90-observabilite-evals | 13 | 224 | 246 | +22 |
| 100-securite-guardrails | 6 | 120 | 132 | +12 |
| 110-mlops-cicd | 9 | 196 | 213 | +17 |
| 120-couts-finops | 3 | 49 | 55 | +6 |
| 130-fondamentaux-llm | 8 | 122 | 134 | +12 |
| 140-system-design-produit | 11 | 187 | 208 | +21 |
| 150-donnees-conformite | 17 | 279 | 307 | +28 |
| 160-multimodal-edge | 5 | 71 | 80 | +9 |
| 170-ml-classique | 8 | 133 | 145 | +12 |
| **Total** | **150** | **2 440** | **2 711** | **+271** |

## Corrections et approfondissements des réponses existantes

Le **reranking** n'est plus présenté comme une amélioration de précision garantie : l'exemple distingue sélection des candidats, reclassement et qualité finale. Le **caching** réutilise un travail encore valide et autorisé ; un changement dans le prompt peut laisser un préfixe partiellement réutilisable. Le cache ne supprime ni tout le prefill ni le calcul des suffixes. Les métriques de hit ne remplacent pas l'économie nette et la qualité.

Les exemples SQL précisent les ex æquo de ROWS/RANGE et montrent pourquoi `WHERE ... OR id IS NULL` ne remplace pas toujours un filtre dans `ON`. L'évaluation numérique explicite une combinaison possible de tolérances absolue et relative. Les autres réponses gagnent un exemple, une limite ou une vérification ciblée.

- [12-optimisation-automatique-prompts](../10-prompt-engineering/12-optimisation-automatique-prompts.md) — Pourquoi optimiser un prompt sur une moyenne peut-il dégrader un cas métier critique ?
- [123-caching-agressif](../120-couts-finops/123-caching-agressif.md) — Qu'est-ce que le caching agressif pour une application LLM ?
- [123-caching-agressif](../120-couts-finops/123-caching-agressif.md) — Pourquoi les agents profitent-ils autant du prompt caching ?
- [123-caching-agressif](../120-couts-finops/123-caching-agressif.md) — Qu'est-ce qui invalide silencieusement le cache de préfixe d'un LLM ?
- [132-tokenisation](../130-fondamentaux-llm/132-tokenisation.md) — Qu'est-ce qu'un token ?
- [138-modeles-raisonnement](../130-fondamentaux-llm/138-modeles-raisonnement.md) — Pourquoi augmenter le budget de raisonnement ne garantit-il pas une amélioration sur chaque tâche ?
- [150-011-sql-transformations-analytiques](../150-donnees-conformite/150-011-sql-transformations-analytiques.md) — Pourquoi un filtre WHERE sur la table droite peut-il changer le sens d’un LEFT JOIN ?
- [150-011-sql-transformations-analytiques](../150-donnees-conformite/150-011-sql-transformations-analytiques.md) — À ne pas confondre : cadre ROWS et cadre RANGE dans une fenêtre SQL ?
- [153-data-flywheel-versioning](../150-donnees-conformite/153-data-flywheel-versioning.md) — Comment prioriser les améliorations issues de la flywheel ?
- [163-voix-temps-reel](../160-multimodal-edge/163-voix-temps-reel.md) — Pourquoi le WER ne suffit-il pas pour évaluer la transcription d'un agent vocal ?
- [172-validation-metriques-ml](../170-ml-classique/172-validation-metriques-ml.md) — Pourquoi apprendre imputation et sélection de variables à l'intérieur de chaque fold ?
- [22-rag-avance](../20-rag/22-rag-avance.md) — Qu'est-ce que le reranking ?
- [39-memoire-agents](../30-agents/39-memoire-agents.md) — Pourquoi le silence d'un utilisateur ne doit-il pas devenir un fait permanent dans la mémoire d'un agent ?
- [60-013-prefill-decode-pas-a-pas](../60-inference-llm/60-013-prefill-decode-pas-a-pas.md) — D'où vient le tout premier token de sortie après le prefill ?
- [90-010-evaluation-reponses-llm](../90-observabilite-evals/90-010-evaluation-reponses-llm.md) — Que vérifier dans une réponse numérique d'un LLM ?
- [90-010-evaluation-reponses-llm](../90-observabilite-evals/90-010-evaluation-reponses-llm.md) — Pourquoi une moyenne de scores peut-elle cacher une réponse inacceptable ?
- [90-012-langfuse-prompts-experiences](../90-observabilite-evals/90-012-langfuse-prompts-experiences.md) — Pourquoi distinguer score nul, score absent et erreur d'évaluateur dans Langfuse ?
- [96-evals-rag-agents](../90-observabilite-evals/96-evals-rag-agents.md) — Comment tester qu'un RAG utilise réellement le contexte fourni ?

## Sources primaires consultées

**45 références** sont rattachées aux fiches avec la date et le sujet du complément. Les sources servent à vérifier les mécanismes indiqués ci-dessous ; les exemples chiffrés et procédures de diagnostic sont des constructions pédagogiques. Les implications de conception ne sont pas présentées comme des fonctionnalités garanties d'un framework.

| Fiches concernées | Point de contrôle | Référence |
| --- | --- | --- |
| 11-prompt-engineering-avance, 35-context-engineering, 137-long-contexte | Position et sélection du contexte | [Liu et al. — Lost in the Middle](https://arxiv.org/abs/2307.03172) |
| 22-rag-avance | Diversification par MMR | [Carbonell et Goldstein — MMR](https://www.cs.cmu.edu/~jgc/publication/The_Use_MMR_Diversity_Based_LTMIR_1998.pdf) |
| 23-knowledge-graphs-ontologies | Monde ouvert et assertions | [W3C — OWL 2 Primer](https://www.w3.org/TR/owl2-primer/) |
| 26-text-to-sql | Jointures, cardinalités et agrégations | [PostgreSQL 18 — expressions de table](https://www.postgresql.org/docs/18/queries-table-expressions.html) |
| 33-mcp, 104-securite-mcp-skills | Identité et frontières de confiance MCP | [MCP — pratiques de sécurité 2026-07-28](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices) |
| 42-langchain-fondamentaux | Fragments d’appels d’outils | [LangChain — modèles et streaming](https://docs.langchain.com/oss/python/langchain/models) |
| 44-langgraph-fondamentaux | État et reducers | [LangGraph — Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api) |
| 45-langgraph-production, 40-011-langgraph-reprise-concurrence | Checkpoints et mémoire persistée | [LangGraph — persistence](https://docs.langchain.com/oss/python/langgraph/persistence) |
| 46-crewai-crews | Contrats et contexte des tâches | [CrewAI — Tasks, v1.15.41](https://docs.crewai.com/v1.15.41/en/concepts/tasks) |
| 47-crewai-flows | État et routage des Flows | [CrewAI — Flows, v1.15.41](https://docs.crewai.com/v1.15.41/en/concepts/flows) |
| 51-fine-tuning-adaptation | Masquage des tokens supervisés | [Hugging Face TRL — SFT Trainer](https://huggingface.co/docs/trl/sft_trainer) |
| 52-post-training-alignement | Comparaisons conditionnelles DPO | [Rafailov et al. — DPO](https://arxiv.org/abs/2305.18290) |
| 54-entrainement-distribue | Synchronisation DDP | [PyTorch 2.15 — DDP](https://docs.pytorch.org/docs/2.15/notes/ddp.html) |
| 56-optimisation-diagnostic-entrainement | Unscale avant clipping | [PyTorch 2.15 — AMP examples](https://docs.pytorch.org/docs/2.15/notes/amp_examples.html) |
| 62-optimisations-inference | Mémoire intermédiaire et attention dense | [Dao et al. — FlashAttention](https://arxiv.org/abs/2205.14135) |
| 66-prefix-caching-radix-attention, 123-caching-agressif | Blocs complets, divergence et identité du cache | [vLLM — Automatic Prefix Caching](https://docs.vllm.ai/en/latest/design/prefix_caching/) |
| 67-speculative-decoding | Espérance de tokens validés par cycle | [Leviathan et al. — Speculative Decoding](https://arxiv.org/abs/2211.17192) |
| 69-roofline-prefill-decode | Plafonds de calcul et de bande passante | [NVIDIA — GPU Performance Background](https://docs.nvidia.com/deeplearning/performance/dl-performance-gpu-background/index.html) |
| 01-oci | Manifestes, configuration et couches | [OCI — Image Manifest](https://github.com/opencontainers/image-spec/blob/main/manifest.md) |
| 02-docker-images-registries | Invalidation du cache de build | [Docker — Build cache invalidation](https://docs.docker.com/build/cache/invalidation/) |
| 04-kubernetes-kubelet-cri | Terminaison des Pods | [Kubernetes — Pod Lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/) |
| 04-kubernetes-kubelet-cri | Éviction sous pression de ressources | [Kubernetes — Node-pressure Eviction](https://kubernetes.io/docs/concepts/scheduling-eviction/node-pressure-eviction/) |
| 06-apptainer-singularity | Montages et dépendances hôtes | [Apptainer — Bind Paths and Mounts](https://apptainer.org/docs/user/latest/bind_paths_and_mounts.html) |
| 09-gpu-conteneurs | Diagnostic du chemin GPU en conteneur | [NVIDIA — Container Toolkit troubleshooting](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/troubleshooting.html) |
| 142-fiabilite-resilience-llm | Sémantique des erreurs HTTP | [IETF — RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html) |
| 91-langfuse-observabilite | Échantillonnage des traces et limites de couverture | [Langfuse — Sampling](https://langfuse.com/docs/observability/features/sampling) |
| 93-monitoring-inference | Alertes et impact utilisateur | [Google SRE — Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/) |
| 103-defenses-agents | Contrôle des destinations réseau | [OWASP — SSRF](https://community.owasp.org/attacks/Server_Side_Request_Forgery) |
| 105-devsecops-ia-agentique | Provenance des artefacts | [SLSA v1.2 — Provenance](https://slsa.dev/spec/v1.2/provenance) |
| 118-artefacts-registre-releases-ml | Alias et versions de modèle | [MLflow — Model Registry Workflows](https://mlflow.org/docs/latest/ml/model-registry/workflow/) |
| 131-transformer-architecture | Attention et masque causal | [Vaswani et al. — Attention Is All You Need](https://arxiv.org/abs/1706.03762) |
| 136-mixture-of-experts | Routage et coûts des experts | [Fedus et al. — Switch Transformers](https://arxiv.org/abs/2101.03961) |
| 150-011-sql-transformations-analytiques | Cadres ROWS/RANGE et agrégations | [PostgreSQL 18 — Value Expressions](https://www.postgresql.org/docs/18/sql-expressions.html) |
| 150-012-stockage-colonnaire-lakehouse | Organisation physique Parquet | [Apache Parquet — File Format](https://parquet.apache.org/docs/file-format/) |
| 150-012-stockage-colonnaire-lakehouse | Snapshots et isolation des lectures | [Apache Iceberg — Reliability](https://iceberg.apache.org/docs/latest/reliability/) |
| 150-014-streaming-traitements-evenements | Temps événement et watermarks | [Apache Flink — Timely Stream Processing](https://nightlies.apache.org/flink/flink-docs-stable/docs/concepts/time/) |
| 159-donnees-temporelles-features | Rattachement temporel des features | [Feast — Point-in-time joins](https://docs.feast.dev/getting-started/concepts/point-in-time-joins) |
| 154-rgpd-llm | Finalités, conservation et droits ; les procédures de restauration sont des implications de conception | [CNIL — IA et RGPD](https://www.cnil.fr/fr/intelligence-artificielle/ia-comment-etre-en-conformite-avec-le-rgpd) |
| 155-ai-act | Changement de finalité et responsabilités | [Commission européenne — article 25](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-25) |
| 172-validation-metriques-ml | Prétraitement ajusté dans les folds | [scikit-learn — Common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html) |
| 172-validation-metriques-ml | Moyennes macro et micro | [scikit-learn — Metrics and scoring](https://scikit-learn.org/stable/modules/model_evaluation.html) |
| 173-calibration-incertitude-abstention | Calibration et populations de validation | [scikit-learn — Probability calibration](https://scikit-learn.org/stable/modules/calibration.html) |
| 173-calibration-incertitude-abstention | Portée marginale des garanties conformes | [Angelopoulos et Bates — Conformal Prediction](https://arxiv.org/abs/2107.07511) |
| 175-series-temporelles-prevision | Évaluation des prévisions et horizons | [Hyndman et Athanasopoulos — Forecasting, chapitre 5](https://otexts.com/fpp3/toolbox.html) |
| 150-014-streaming-traitements-evenements | Partitions inactives et watermark minimal | [Apache Flink — Generating Watermarks](https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/datastream/event-time/generating_watermarks/) |

Les dates globales `Vérifié le` restent **strictement identiques** à celles de la base : une vérification ciblée ne renouvelle pas toute une fiche. Cette passe ne certifie pas chaque affirmation historique, tous les benchmarks, prix, CVE ou calendriers réglementaires. Les références `latest` peuvent évoluer ; une implémentation doit utiliser la documentation de sa version. Aucun cluster GPU, service cloud, fournisseur LLM ou framework d'agents réel n'a été déployé pour valider ces ajouts.

## Vérifications de livraison

- `make check` dans un environnement Python 3.10 isolé avec les dépendances du dépôt : lint des fiches, catalogues, ruff, mypy, **54 tests** et les deux ateliers intégrés réussis.
- Lint : **0 erreur, 0 avertissement** ; aucune réponse nouvelle au-delà des limites de longueur.
- Comparaison avec `a744073` : **150 fiches modifiées**, **2 440 questions et identifiants conservés**, **18 réponses existantes changées**, **271 nouvelles cartes**, dates globales inchangées.
- **24 contrôles arithmétiques** et exécution du contre-exemple SQL de jointure : résultats conformes. Les hypothèses des autres exercices ont été relues.
- `make export`, puis inspection SQLite du paquet : **2 711 cartes actives** avec exactement les identifiants du vault, et **71 cartes retirées toujours suspendues**.
- `git diff --check` : aucune erreur d'espacement. Les configurations locales non suivies restent hors de la livraison.

La CI de la PR doit confirmer les contrôles sous Python 3.10 et 3.12 avant fusion. La publication du paquet Anki sur `main` reste assurée par le workflow existant. Les contrôles automatiques vérifient structure et cohérence technique ; ils ne démontrent pas à eux seuls la vérité de chaque explication.
