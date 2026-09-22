# Plateformes d'agents — Flashcards
Tags: #flashcards #ai-engineering #agents #platform #llm

Quelle différence entre un framework et une plateforme d'agents ?
?
Le **[[37-frameworks-agents|framework]]** sert à **écrire** l'agent (bibliothèque) ; la **plateforme** sert à l'**exécuter et le gouverner en production** (runtime managé, identité, mémoire, observabilité).

---

Quelles briques fournit une plateforme d'agents ?
?
- **Runtime** managé et scalable (sessions longues, isolation)
- **Registre d'outils** et de serveurs [[33-mcp|MCP]]
- **Mémoire** persistante
- **Identité et permissions** (IAM, accès délégué)
- **Observabilité**, evals, gestion des coûts

---

Donnez des exemples de plateformes d'agents cloud.
?
- **Google** : Vertex AI Agent Builder / Agent Engine
- **AWS** : Bedrock AgentCore (runtime, gateway, memory, identity)
- **Microsoft** : Azure AI Foundry Agent Service

---

Existe-t-il des plateformes open source ?
?
**Oui** : **Dify**, **Langflow**, **Flowise** proposent des builders visuels, des connecteurs et le déploiement d'agents ou d'apps LLM, en **self-hosting**.

---

Pourquoi un registre d'outils centralisé ?
?
Pour **publier une fois** les outils et serveurs MCP de l'entreprise, contrôler **qui y accède**, et éviter que chaque équipe réintègre les mêmes API.

---

Pourquoi l'identité est-elle un sujet clé pour les agents ?
?
Un agent agit **au nom d'un utilisateur** : il doit hériter de **ses droits** (OAuth, accès délégué) et pas d'un compte de service surpuissant. C'est le principe du **moindre privilège** ([[101-securite-llm-guardrails|sécurité LLM]]).

---

Quel rôle joue l'observabilité dans une plateforme ?
?
**Tracer chaque étape** de l'agent (appels LLM, outils, décisions), mesurer coûts et latence, et rattacher des **scores de qualité** — comme le fait [[91-langfuse-observabilite|Langfuse]].

---

Build ou buy ?
?
**Buy** (plateforme cloud) : time-to-market, sécurité et scaling managés, mais **lock-in**. **Build** (framework + Kubernetes + outils open source) : contrôle et portabilité, mais tout le run est à votre charge.

---

## Connexions
- [[33-mcp|MCP]] — le registre de serveurs MCP
- [[37-frameworks-agents|Frameworks d'agents]] — le code qu'on y déploie
- [[36-orchestration-agents|Orchestration multi-agents]] — ce que le runtime doit supporter
- [[91-langfuse-observabilite|Langfuse]] — la brique observabilité
- [[101-securite-llm-guardrails|Sécurité LLM]] — identité et permissions
- [[81-litellm-api-layer|LiteLLM]] — la gateway
- [[83-gateway-ingress|Ingress]] — l'entrée réseau
- [[00-moc-ai-engineering|MOC AI Engineering]]
