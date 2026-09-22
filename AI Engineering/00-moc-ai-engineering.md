# AI Engineering — MOC
Tags: #moc #ai-engineering

Carte racine du vault : les connaissances pour devenir **Senior / Lead AI Engineer**.
Chaque domaine a ses notes de flashcards reliées entre elles via `## Connexions`.

## Parcours de lecture
Progression recommandée : **utiliser les modèles → construire des architectures → adapter → servir & déployer → industrialiser → gouverner.**
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

## 10 — Prompt engineering
- [[11-prompt-engineering-avance|Prompt engineering avancé]]

## 20 — RAG
- [[21-rag-fondamentaux|RAG — Fondamentaux]]
- [[22-rag-avance|RAG — Avancé]]

## 30 — Agents
- [[31-agents-fondamentaux|Fondamentaux des agents]]
- [[32-tool-calling|Tool calling]]
- [[33-mcp|MCP — Model Context Protocol]]
- [[34-harness-plugins|Harness & plugins]]
- [[35-context-engineering|Context engineering]]
- [[36-orchestration-agents|Orchestration multi-agents]]
- [[37-frameworks-agents|Frameworks d'agents (LangChain, LangGraph, CrewAI, ADK)]]
- [[38-plateformes-agents|Plateformes d'agents]]

## 40 — Automatisation & frameworks d'agents
- [[41-automatisation-code-nocode|Automatisation code & no-code (n8n…)]]
- [[42-langchain-fondamentaux|LangChain — Fondamentaux]]
- [[43-langchain-agents|LangChain — Agents & middleware]]
- [[44-langgraph-fondamentaux|LangGraph — Fondamentaux]]
- [[45-langgraph-production|LangGraph — Production (persistance, HITL, multi-agents)]]
- [[46-crewai-crews|CrewAI — Crews]]
- [[47-crewai-flows|CrewAI — Flows]]

## 50 — Fine-tuning
- [[51-fine-tuning-adaptation|Fine-tuning & adaptation de modèles]]

## 60 — Inférence LLM
- [[61-kv-cache-attention|KV cache & attention]]
- [[62-optimisations-inference|Optimisations d'inférence]]
- [[63-guided-generation|Guided generation (sorties structurées)]]
- [[64-metriques-slo-inference|Métriques d'inférence & SLO]]

## 70 — Conteneurs & Infra
- [[00-index|Index Conteneurs]] — OCI, Docker, Kubernetes, GPU, Apptainer/HPC

## 80 — API Layer & Routing
- [[81-litellm-api-layer|LiteLLM (API layer)]]
- [[82-routing-llm|Routing LLM]]
- [[83-gateway-ingress|Ingress & API gateway]]

## 90 — Observabilité & Evals
- [[91-langfuse-observabilite|Langfuse & observabilité LLM]]
- [[92-chainforge-evals-prompts|ChainForge & évaluation de prompts]]

## 100 — Sécurité & guardrails
- [[101-securite-llm-guardrails|Sécurité LLM & guardrails]]

## 110 — MLOps & CI/CD
- [[111-mlops-llmops-fondamentaux|MLOps & LLMOps — Fondamentaux]]
- [[112-cicd-modeles|CI/CD des modèles]]
- [[113-monitoring-drift-feedback|Monitoring, drift & boucle de feedback]]

## 120 — Coûts & FinOps
- [[121-couts-inference|Coûts d'inférence]]
- [[122-finops-llm|FinOps LLM]]

## La stack en une chaîne
```text
App / Agent
    ↓
Gateway (Ingress → LiteLLM : auth, routing, budgets)
    ↓
Serveur d'inférence (vLLM/Triton/TGI, KV cache, batching)
    ↓
Conteneur + GPU (Docker/K8s/Apptainer)
```
Observabilité transverse : Langfuse (traces, coûts, evals).
