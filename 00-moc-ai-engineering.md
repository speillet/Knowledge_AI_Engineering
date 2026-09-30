# AI Engineering — MOC
Tags: #moc #ai-engineering

Carte racine du vault : les connaissances clés de l'**AI Engineering**, de l'usage des modèles à leur industrialisation.
Chaque domaine a ses notes de flashcards reliées entre elles via `## Connexions`.
Chaque fiche se termine par des **mises en situation** : pour ne réviser qu'elles, chercher `Mise en situation :` dans le vault.

## Parcours de lecture
Progression recommandée : **comprendre les modèles → les utiliser → construire des architectures → adapter → servir & déployer → industrialiser → gouverner → concevoir des systèmes.**
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
13. [[151-donnees-curation-annotation|Données & conformité]] — données, RGPD, AI Act
14. [[161-modeles-vision-langage|Multimodal & edge]] — images, documents, voix, local
15. [[141-system-design-llm|System design & produit]] — tout assembler (niveau senior)

## 10 — Prompt engineering
- [[11-prompt-engineering-avance|Prompt engineering avancé]]
- [[12-optimisation-automatique-prompts|Optimisation automatique de prompts (DSPy)]]
- [[13-prompts-production|Prompts en production (structure, versioning, portabilité)]]

## 20 — RAG
- [[21-rag-fondamentaux|RAG — Fondamentaux]]
- [[22-rag-avance|RAG — Avancé]]
- [[23-knowledge-graphs-ontologies|Knowledge graphs & ontologies (GraphRAG, context graph)]]
- [[24-cognee|Cognee (mémoire en knowledge graph)]]
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
- [[37-frameworks-agents|Frameworks d'agents (LangChain, LangGraph, CrewAI, ADK)]]
- [[38-plateformes-agents|Plateformes d'agents — Fondamentaux]] (suite senior : [[115-plateformes-agents-gouvernance|architecture & gouvernance]])
- [[39-memoire-agents|Mémoire des agents]]
- Agents d'interface : [[165-computer-use-agents-navigateur|computer use & agents navigateur]] (section 160, la section 30 étant pleine)
- Suites de la section 40 : [[48-patterns-workflows-agentiques|patterns de workflows agentiques]], [[49-agents-de-code|agents de code]] ; en section 20 : [[27-agents-recherche-deep-research|agents de recherche]] ; en section 90 : [[98-debogage-agents|débogage des agents]]

## 40 — Automatisation & frameworks d'agents
- [[41-automatisation-code-nocode|Automatisation code & no-code (n8n…)]]
- [[42-langchain-fondamentaux|LangChain — Fondamentaux]]
- [[43-langchain-agents|LangChain — Agents & middleware]]
- [[44-langgraph-fondamentaux|LangGraph — Fondamentaux]]
- [[45-langgraph-production|LangGraph — Production (persistance, HITL, multi-agents)]]
- [[46-crewai-crews|CrewAI — Crews]]
- [[47-crewai-flows|CrewAI — Flows]]
- [[48-patterns-workflows-agentiques|Patterns de workflows agentiques (chaining, routing, evaluator-optimizer, plan-and-execute)]]
- [[49-agents-de-code|Agents de code : usage & intégration]]

## 50 — Fine-tuning
- [[51-fine-tuning-adaptation|Fine-tuning & adaptation de modèles]]
- [[52-post-training-alignement|Post-training & alignement (RLHF, DPO, GRPO, RLVR)]]
- [[53-donnees-synthetiques-distillation|Données synthétiques & distillation]]
- [[54-entrainement-distribue|Entraînement distribué (DDP, FSDP/ZeRO, parallélismes)]]
- [[55-rl-agentique|RL agentique & environnements d'entraînement]]

## 60 — Inférence LLM
- [[61-kv-cache-attention|KV cache & attention]]
- [[62-optimisations-inference|Optimisations d'inférence]]
- [[63-guided-generation|Guided generation (sorties structurées)]]
- [[64-metriques-slo-inference|Métriques d'inférence & SLO]]
- [[65-probabilites-sampling|Probabilités & sampling (température, top-p, logprobs)]]
- [[66-prefix-caching-radix-attention|Prefix caching & RadixAttention]]
- [[67-speculative-decoding|Speculative decoding]]
- [[68-quantization|Quantization (FP8, INT4, AWQ, GPTQ, GGUF)]]
- [[69-roofline-prefill-decode|Roofline, prefill/decode & désagrégation]]

## 70 — Conteneurs & Infra
- [[00-index|Index Conteneurs]] — OCI, Docker, Kubernetes, GPU, Apptainer/HPC

## 80 — API Layer & Routing
- [[81-litellm-api-layer|LiteLLM (API layer)]]
- [[82-routing-llm|Routing LLM]]
- [[83-gateway-ingress|Ingress & API gateway]]
- [[84-streaming-integration-applicative|Streaming & intégration applicative (SSE, annulation, tâches longues)]]
- [[85-carte-protocoles-agentiques|Carte des protocoles agentiques (MCP, A2A, AG-UI, OpenTelemetry, AGENTS.md)]]

## 90 — Observabilité & Evals
- [[91-langfuse-observabilite|Langfuse & observabilité LLM]]
- [[92-chainforge-evals-prompts|ChainForge & évaluation de prompts]]
- [[93-monitoring-inference|Monitoring de l'inférence & de l'usage]]
- [[94-evals-methodologie|Évaluation des systèmes LLM — Méthodologie]]
- [[95-llm-as-judge|LLM-as-a-judge (biais, validation, correction)]]
- [[96-evals-rag-agents|Évaluation des RAG & des agents]]
- [[97-evals-online-ab-testing|Evals online & A/B testing]]
- [[98-debogage-agents|Débogage & analyse d'échecs des agents]]

## 100 — Sécurité & guardrails
- [[101-securite-llm-guardrails|Sécurité LLM & guardrails]]
- [[102-menaces-agents|Sécurité des agents — Menaces & incidents]]
- [[103-defenses-agents|Sécurité des agents — Architecture défensive]]
- [[104-securite-mcp-skills|Sécurité de MCP & des skills]]
- [[105-devsecops-ia-agentique|DevSecOps pour l'IA agentique]]
- [[106-securite-agents-code|Sécurité des agents de code]]

## 110 — MLOps & CI/CD
- [[111-mlops-llmops-fondamentaux|MLOps & LLMOps — Fondamentaux]]
- [[112-cicd-modeles|CI/CD des modèles]]
- [[113-monitoring-drift-feedback|Monitoring, drift & boucle de feedback]]
- [[114-reproductibilite-variance|Reproductibilité & variance (déterminisme, stats d'evals)]]
- [[115-plateformes-agents-gouvernance|Plateformes d'agents — Architecture & gouvernance]]

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
- [[142-fiabilite-resilience-llm|Fiabilité & résilience]]
- [[143-hallucinations-grounding|Hallucinations, grounding & abstention]]
- [[144-ux-ia-human-in-the-loop|UX de l'IA & human-in-the-loop]]
- [[145-cas-system-design|Cas de system design]]
- [[146-choix-modeles|Choisir un modèle]]
- [[147-leadership-technique-ia|Leadership technique en AI Engineering]]

## 150 — Données & conformité
- [[151-donnees-curation-annotation|Données : curation & annotation]]
- [[152-pii-confidentialite|PII & confidentialité]]
- [[153-data-flywheel-versioning|Data flywheel & versioning des données]]
- [[154-rgpd-llm|RGPD appliqué aux LLM]]
- [[155-ai-act|AI Act]]
- [[156-ia-responsable|IA responsable : biais, équité & transparence]]

## 160 — Multimodal & edge
- [[161-modeles-vision-langage|Modèles vision-langage (VLM)]]
- [[162-document-parsing|Parsing de documents (PDF, OCR, layout)]]
- [[163-voix-temps-reel|Voix & agents temps réel]]
- [[164-llm-local-edge|LLM locaux, on-prem & edge]]
- [[165-computer-use-agents-navigateur|Computer use & agents navigateur]]

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
