# AI Engineering — MOC
Tags: #moc #ai-engineering

Carte racine du vault : les connaissances clés de l'**AI Engineering**, de l'usage des modèles à leur industrialisation.
Chaque domaine a ses notes de flashcards reliées entre elles via `## Connexions`.
Chaque fiche se termine par des **mises en situation** : pour ne réviser qu'elles, chercher `Mise en situation :` dans le vault.

## Parcours de lecture
Progression recommandée : **comprendre les modèles → les utiliser → construire des architectures → adapter → servir & déployer → industrialiser → gouverner → concevoir des systèmes.**
- **Socle prédictif** : [[171-choisir-modele-ml|ML classique]] puis [[172-validation-metriques-ml|validation et métriques]] — choisir une approche avant de construire une chaîne LLM

0. [[131-transformer-architecture|Fondamentaux LLM]] — comprendre ce qu'on utilise (prérequis)
1. [[11-prompt-engineering-avance|Prompt engineering]] — parler aux modèles
2. [[21-rag-fondamentaux|RAG]] — les augmenter avec des connaissances
3. [[31-agents-fondamentaux|Agents]] — leur donner des mains
4. [[41-automatisation-code-nocode|Automatisation & frameworks d'agents]] — workflows, LangChain, LangGraph, CrewAI
5. [[51-fine-tuning-adaptation|Fine-tuning]] — adapter le modèle lui-même
6. [[61-kv-cache-attention|Inférence]] — comprendre le serving
7. [[00-index|Conteneurs & infra]] — déployer sur GPU
8. [[81-litellm-api-layer|API layer & routing]] — industrialiser l'accès
9. [[91-langfuse-observabilite|Observabilité & evals]] — tout mesurer
10. [[101-securite-llm-guardrails|Sécurité]] — tout protéger
11. [[111-mlops-llmops-fondamentaux|MLOps & CI/CD]] — livrer en continu
12. [[121-couts-inference|Coûts & FinOps]] — maîtriser l'économie
13. [[151-donnees-curation-annotation|Données & conformité]] — données, RGPD, AI Act ; puis [[157-contrats-qualite-donnees|contrats]], [[158-ingestion-cdc-backfills|ingestion]] et [[159-donnees-temporelles-features|variables temporelles]]
14. [[161-modeles-vision-langage|Multimodal & edge]] — images, documents, voix, local
15. [[141-system-design-llm|System design & produit]] — tout assembler (niveau senior)

### Parcours AI Engineer agentique
Pour se concentrer sur les agents, à travers les sections :
1. [[31-agents-fondamentaux|Agents]] puis [[48-patterns-workflows-agentiques|patterns de workflows]] — workflow ou agent
2. [[32-tool-calling|Tool calling]], [[33-mcp|MCP]] et [[85-carte-protocoles-agentiques|carte des protocoles]] — relier l'agent au monde
3. [[35-context-engineering|Context engineering]] et [[39-memoire-agents|mémoire]] — ce que l'agent sait à chaque tour
4. [[36-orchestration-agents|Multi-agents]], [[27-agents-recherche-deep-research|agents de recherche]] et [[49-agents-de-code|agents de code]] — les grands cas d'usage
5. [[96-evals-rag-agents|Évaluer]] puis [[98-debogage-agents|déboguer]] un agent
6. [[102-menaces-agents|Menaces]] et [[103-defenses-agents|défenses]] — sécuriser
7. [[84-streaming-integration-applicative|Intégration applicative]] et [[38-plateformes-agents|plateformes]] — mettre en production
8. [[115-plateformes-agents-gouvernance|Gouvernance]] et [[55-rl-agentique|RL agentique]] — niveau senior

### Parcours fondations senior
Pour relier les trois priorités transversales aux applications IA :
1. [[171-choisir-modele-ml|Choisir une approche]] puis [[172-validation-metriques-ml|valider sans fuite]] — règles, ML classique ou LLM
2. [[157-contrats-qualite-donnees|Définir les contrats]], [[158-ingestion-cdc-backfills|fiabiliser l’ingestion]] puis [[159-donnees-temporelles-features|reconstruire les données disponibles]] — qualité et temporalité
3. [[149-livraison-idempotence-concurrence|Maîtriser livraison et concurrence]] puis [[140-010-transactions-outbox-sagas|orchestrer les transactions]] — effets métier sûrs malgré les pannes

### Liens transversaux
- [[38-plateformes-agents|Plateformes]] → [[115-plateformes-agents-gouvernance|architecture et gouvernance]]
- [[165-computer-use-agents-navigateur|Agents d’interface]] : complément multimodal du parcours agentique.

### Parcours de mise en pratique senior
Après les fondations, travailler ces sujets sur un même projet et produire une preuve pour chaque étape :
1. [[99-statistiques-decisions-experimentales|Décider avec des statistiques]] — protocole, comparaison appariée, intervalle et seuil de gain utile
2. [[173-calibration-incertitude-abstention|Calibrer et savoir s'abstenir]] — courbe de fiabilité, risque-couverture et charge humaine
3. [[56-optimisation-diagnostic-entrainement|Diagnostiquer l'entraînement]] — micro-lot, courbes train/validation, gradients et normalisation ; approfondir si le rôle inclut l'adaptation des modèles
4. [[116-sre-incidents-capacite-ia|Exploiter et reprendre après panne]] — SLO, file bornée, exercice de bascule et postmortem
5. [[147-leadership-technique-ia|Rendre les décisions et l'équipe autonomes]] — ADR, transfert d'exploitation et correction vérifiée

Le [bilan de pertinence et les ateliers](docs/pertinence-parcours-senior-2026-10-07.md) précisent priorités, livrables et critères de réussite. Les cartes préparent le raisonnement ; la maîtrise se démontre aussi en construisant, mesurant et expliquant les limites d'un système.

### Parcours prédire, recommander et décider
Après [[171-choisir-modele-ml|le choix des modèles]], [[172-validation-metriques-ml|la validation]] et [[173-calibration-incertitude-abstention|la calibration]], choisir le sujet selon le problème :
- [[174-recommandation-ranking|Recommandation & ranking]] — proposer et ordonner des éléments, avec biais d'exposition et cold start
- [[175-series-temporelles-prevision|Prévision temporelle]] — prévoir aux horizons utiles avec les informations réellement disponibles
- [[176-detection-anomalies|Détection d'anomalies]] — transformer un score atypique en alerte exploitable
- [[177-explicabilite-modeles|Explicabilité]] — diagnostiquer une prédiction et vérifier ce que son explication signifie
- [[178-inference-causale-decisions|Inférence causale]] — estimer ce qu'une action change, avec hypothèses et limites

Le [bilan des cinq nouveaux sujets](docs/nouvelles-competences-ia-2026-10-08.md) précise leurs apports et un exercice pour chacun. Ces branches complètent le parcours LLM et agents ; elles se travaillent selon les responsabilités du poste visé.

<!-- catalog:begin -->

## 10 — Prompt engineering

- [[11-prompt-engineering-avance|Prompt engineering avancé]]
- [[12-optimisation-automatique-prompts|Optimisation automatique de prompts (DSPy)]]
- [[13-prompts-production|Prompts en production]]

## 20 — RAG

- [[21-rag-fondamentaux|RAG — Fondamentaux]]
- [[22-rag-avance|RAG — Avancé]]
- [[23-knowledge-graphs-ontologies|Knowledge graphs & ontologies]]
- [[24-cognee|Cognee]]
- [[25-chunking-contextual-retrieval|Chunking avancé & contextual retrieval]]
- [[26-text-to-sql|Text-to-SQL & données structurées]]
- [[27-agents-recherche-deep-research|Agents de recherche (deep research)]]

## 30 — Agents

- [[31-agents-fondamentaux|Fondamentaux des agents]]
- [[32-tool-calling|Tool calling]]
- [[33-mcp|MCP — Model Context Protocol]]
- [[34-harness-plugins|Harness & plugins]]
- [[35-context-engineering|Context engineering]]
- [[36-orchestration-agents|Orchestration multi-agents]]
- [[37-frameworks-agents|Frameworks d'agents]]
- [[38-plateformes-agents|Plateformes d'agents]]
- [[39-memoire-agents|Mémoire des agents]]

## 40 — Automatisation & frameworks d'agents

- [[41-automatisation-code-nocode|Automatisation code & no-code]]
- [[42-langchain-fondamentaux|LangChain — Fondamentaux]]
- [[43-langchain-agents|LangChain — Agents & middleware]]
- [[44-langgraph-fondamentaux|LangGraph — Fondamentaux]]
- [[45-langgraph-production|LangGraph — Production (persistance, HITL, multi-agents)]]
- [[46-crewai-crews|CrewAI — Crews]]
- [[47-crewai-flows|CrewAI — Flows]]
- [[48-patterns-workflows-agentiques|Patterns de workflows agentiques]]
- [[49-agents-de-code|Agents de code : usage & intégration]]

## 50 — Fine-tuning

- [[51-fine-tuning-adaptation|Fine-tuning & adaptation de modèles]]
- [[52-post-training-alignement|Post-training & alignement]]
- [[53-donnees-synthetiques-distillation|Données synthétiques & distillation]]
- [[54-entrainement-distribue|Entraînement distribué]]
- [[55-rl-agentique|RL agentique & environnements d'entraînement]]
- [[56-optimisation-diagnostic-entrainement|Optimisation & diagnostic d'entraînement]]

## 60 — Inférence LLM

- [[61-kv-cache-attention|KV cache & attention]]
- [[62-optimisations-inference|Optimisations d'inférence]]
- [[63-guided-generation|Guided generation (sorties structurées)]]
- [[64-metriques-slo-inference|Métriques d'inférence & SLO]]
- [[65-probabilites-sampling|Probabilités & sampling]]
- [[66-prefix-caching-radix-attention|Prefix caching & RadixAttention]]
- [[67-speculative-decoding|Speculative decoding]]
- [[68-quantization|Quantization]]
- [[69-roofline-prefill-decode|Roofline, prefill/decode & désagrégation]]

## 70 — Conteneurs & Infra

- [[00-index|Conteneurs & infra — Index]]
- [[01-oci|OCI]]
- [[02-docker-images-registries|Docker, images et registries]]
- [[03-containerd-runc|containerd & runc]]
- [[04-kubernetes-kubelet-cri|Kubernetes, kubelet & CRI]]
- [[05-docker-kubernetes|Docker & Kubernetes]]
- [[06-apptainer-singularity|Apptainer & Singularity]]
- [[07-synthese-containers|Conteneurs — Synthèse]]
- [[08-linux-primitives-docker-fondamentaux|Primitives Linux & fondamentaux Docker]]
- [[09-gpu-conteneurs|GPU en conteneur]]
- [[10-images-modeles-poids|Images & poids de modèles]]
- [[11-serveurs-inference-llm|Serveurs d'inférence LLM]]
- [[12-kubernetes-gpu-inference|Kubernetes GPU & inférence]]
- [[13-apptainer-inference-hpc|Apptainer & inférence HPC]]

## 80 — API Layer & Routing

- [[81-litellm-api-layer|LiteLLM (API layer)]]
- [[82-routing-llm|Routing LLM]]
- [[83-gateway-ingress|Ingress & API gateway]]
- [[84-streaming-integration-applicative|Streaming & intégration applicative]]
- [[85-carte-protocoles-agentiques|Carte des protocoles agentiques]]

## 90 — Observabilité & Evals

- [[91-langfuse-observabilite|Langfuse & observabilité LLM]]
- [[92-chainforge-evals-prompts|ChainForge & évaluation de prompts]]
- [[93-monitoring-inference|Monitoring de l'inférence & de l'usage]]
- [[94-evals-methodologie|Évaluation des systèmes LLM — Méthodologie]]
- [[95-llm-as-judge|LLM-as-a-judge]]
- [[96-evals-rag-agents|Évaluation des RAG & des agents]]
- [[97-evals-online-ab-testing|Evals online & A/B testing]]
- [[98-debogage-agents|Débogage & analyse d'échecs des agents]]
- [[99-statistiques-decisions-experimentales|Statistiques pour décider en IA]]

## 100 — Sécurité & guardrails

- [[101-securite-llm-guardrails|Sécurité LLM & guardrails]]
- [[102-menaces-agents|Sécurité des agents — Menaces & incidents]]
- [[103-defenses-agents|Sécurité des agents — Architecture défensive]]
- [[104-securite-mcp-skills|Sécurité de MCP, des outils & des skills]]
- [[105-devsecops-ia-agentique|DevSecOps pour l'IA agentique]]
- [[106-securite-agents-code|Sécurité des agents de code]]

## 110 — MLOps & CI/CD

- [[111-mlops-llmops-fondamentaux|MLOps & LLMOps — Fondamentaux]]
- [[112-cicd-modeles|CI/CD des modèles]]
- [[113-monitoring-drift-feedback|Monitoring, drift & boucle de feedback]]
- [[114-reproductibilite-variance|Reproductibilité & variance]]
- [[115-plateformes-agents-gouvernance|Plateformes d'agents — Architecture & gouvernance]]
- [[116-sre-incidents-capacite-ia|SRE : incidents & capacité des services IA]]

## 120 — Coûts & FinOps

- [[121-couts-inference|Coûts d'inférence]]
- [[122-finops-llm|FinOps LLM]]
- [[123-caching-agressif|Caching agressif]]

## 130 — Fondamentaux LLM

- [[131-transformer-architecture|Architecture Transformer]]
- [[132-tokenisation|Tokenisation]]
- [[133-embeddings-representations|Embeddings & représentations]]
- [[134-recherche-vectorielle-ann|Recherche vectorielle & index ANN]]
- [[135-pretraining-scaling-laws|Pré-entraînement & scaling laws]]
- [[136-mixture-of-experts|Mixture of Experts (MoE)]]
- [[137-long-contexte|Long contexte]]
- [[138-modeles-raisonnement|Modèles de raisonnement & test-time compute]]

## 140 — System design & produit

- [[141-system-design-llm|System design d'applications LLM — Méthode]]
- [[142-fiabilite-resilience-llm|Fiabilité & résilience des applications LLM]]
- [[143-hallucinations-grounding|Hallucinations, grounding & abstention]]
- [[144-ux-ia-human-in-the-loop|UX de l'IA & human-in-the-loop]]
- [[145-cas-system-design|Cas de system design LLM]]
- [[146-choix-modeles|Choisir un modèle]]
- [[147-leadership-technique-ia|Leadership technique en AI Engineering]]
- [[148-pipelines-batch-llm|Pipelines batch à grande échelle]]
- [[149-livraison-idempotence-concurrence|Livraison, idempotence & concurrence]]
- [[140-010-transactions-outbox-sagas|Transactions, outbox & sagas pour les agents]]

## 150 — Données & conformité

- [[151-donnees-curation-annotation|Données : curation & annotation]]
- [[152-pii-confidentialite|PII & confidentialité des données]]
- [[153-data-flywheel-versioning|Data flywheel & versioning des données]]
- [[154-rgpd-llm|RGPD appliqué aux LLM]]
- [[155-ai-act|AI Act (règlement européen sur l'IA)]]
- [[156-ia-responsable|IA responsable : biais, équité & transparence]]
- [[157-contrats-qualite-donnees|Contrats, schémas & qualité des données]]
- [[158-ingestion-cdc-backfills|Ingestion incrémentale, CDC & backfills]]
- [[159-donnees-temporelles-features|Données temporelles & variables de production]]

## 160 — Multimodal & edge

- [[161-modeles-vision-langage|Modèles vision-langage (VLM)]]
- [[162-document-parsing|Parsing de documents (PDF, OCR, layout)]]
- [[163-voix-temps-reel|Voix & agents temps réel]]
- [[164-llm-local-edge|LLM locaux, on-prem & edge]]
- [[165-computer-use-agents-navigateur|Computer use & agents navigateur]]

## 170 — ML classique & validation

- [[171-choisir-modele-ml|ML classique : choisir et comprendre les modèles]]
- [[172-validation-metriques-ml|ML classique : validation, fuites & métriques]]
- [[173-calibration-incertitude-abstention|Calibration, incertitude & abstention]]
- [[174-recommandation-ranking|Recommandation & learning to rank]]
- [[175-series-temporelles-prevision|Prévision de séries temporelles]]
- [[176-detection-anomalies|Détection d'anomalies]]
- [[177-explicabilite-modeles|Explicabilité & diagnostic des modèles]]
- [[178-inference-causale-decisions|Inférence causale & décisions produit]]

<!-- catalog:end -->

## La stack en une chaîne
```text
App / Agent
    ↓
Plateforme d'agents (runtime, sandbox, gateway d'outils MCP, identité, politiques)
    ↓
Gateway LLM (Ingress → LiteLLM : auth, routing, budgets)
    ↓
Serveur d'inférence (vLLM/SGLang/TensorRT-LLM, KV cache, batching, quantization)
    ↓
Conteneur + GPU (Docker/K8s/Apptainer)
```
Transverses : **observabilité** (traces, métriques, evals), **sécurité** (injection, moindre privilège, sandbox, DevSecOps), **coûts** (FinOps) et **données & conformité** (PII, RGPD, AI Act).
