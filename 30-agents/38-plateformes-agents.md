# Plateformes d'agents — Flashcards
Tags: #flashcards #ai-engineering #agents #platform #llm

Quelle différence entre un framework et une plateforme d'agents ?
?
Le **[[37-frameworks-agents|framework]]** sert à **écrire** l'agent (bibliothèque) ; la **plateforme** sert à l'**exécuter et le gouverner en production** : runtime managé, sandbox, mémoire, accès aux outils, identité, politiques d'accès, observabilité, evals. La suite senior de cette fiche : [[115-plateformes-agents-gouvernance|architecture & gouvernance]].

---

Quelles briques fournit une plateforme d'agents ?
?
- **Runtime** : exécute les sessions d'agent, isolées et longues
- **Sandbox** : exécute le code et le navigateur de l'agent sans risque
- **Mémoire** : court terme (session) et long terme
- **Gateway d'outils** : expose les API comme outils [[33-mcp|MCP]]
- **Registre** : catalogue des agents, outils et skills
- **Identité et politiques d'accès** : qui l'agent représente, ce qu'il a le droit de faire
- **Observabilité, evals, coûts**

En 2026, AWS, Google et Microsoft proposent tous ces briques, souvent **utilisables séparément**.

---

Quels niveaux d'abstraction proposent les plateformes ?
?
Du plus flexible au plus clé en main :
1. **API du modèle** : on écrit sa propre boucle d'agent ([[34-harness-plugins|harness]]) et on l'héberge soi-même
2. **Runtime managé** : on apporte son code d'agent, quel que soit le framework (LangGraph, ADK, CrewAI…), et la plateforme l'exécute (sessions, scaling, isolation)
3. **Harness managé** : on **déclare** seulement le modèle, le prompt, les outils et les skills, et la plateforme fournit la boucle elle-même (ex. **Claude Managed Agents**, **AgentCore Harness**)

---

Donnez des exemples de plateformes d'agents cloud.
?
- **AWS** : **Bedrock AgentCore** (Harness, Runtime, Memory, Gateway, Identity, Code Interpreter, Browser, Observability, Evaluations, Policy, Registry)
- **Google** : **Gemini Enterprise Agent Platform**, nouveau nom de Vertex AI depuis avril 2026 (ADK, Agent Studio, runtime managé, Memory Bank, Agent Registry, Agent Identity, Agent Gateway)
- **Microsoft** : **Foundry Agent Service** (hosted agents, une identité Entra par agent), gouverné par **Agent 365**
- **Éditeurs de données et de SaaS** : Databricks, Snowflake, Salesforce Agentforce, ServiceNow

---

Que proposent les fournisseurs de modèles ?
?
- **OpenAI** : **Agents SDK** pour le code, **Frontier** (février 2026) pour gérer des agents en entreprise, y compris ceux d'autres éditeurs, et les **Workspace Agents** de ChatGPT pour les non-développeurs. Le builder visuel **Agent Builder** ferme le **30 novembre 2026**
- **Anthropic** : **Claude Agent SDK** pour le code, **Claude Managed Agents** (bêta depuis avril 2026) : un harness hébergé autour de 4 concepts, **agent**, **environment** (sandbox cloud ou auto-hébergée), **session** et **events**

---

Existe-t-il des plateformes open source ?
?
**Oui**, à deux niveaux :
- **Builders visuels** auto-hébergeables : **Dify** (suite complète : workflows, base de connaissances, publication d'apps), **Langflow**, **Flowise**, **n8n** (automatisation avec des nœuds d'agent)
- **Briques d'infrastructure** : **kagent** (agents déclarés comme ressources Kubernetes et déployés en GitOps), **Agent Sandbox** (sandboxes sur Kubernetes), **agentgateway** (gateway pour MCP, A2A et LLM)

---

Qu'apporte un runtime d'agents par rapport à un déploiement web classique ?
?
Un agent ne ressemble pas à une requête HTTP courte :
- **Sessions longues** : minutes, heures, voire jours (ex. jusqu'à 8 h par session sur AgentCore Runtime)
- **Isolation par session**, souvent une microVM par session
- **Exécution asynchrone** en arrière-plan, déclenchement par **cron** ou par événement
- **Reprise après panne** grâce à l'état sauvegardé ([[45-langgraph-production|checkpoints]])
- **Streaming**, **interruptions** pour le human-in-the-loop, gestion des messages concurrents

---

Qu'est-ce que le double texting et comment le gère-t-on ?
?
L'utilisateur envoie un **nouveau message pendant que l'agent travaille** encore sur le précédent. Le runtime doit choisir une stratégie (vocabulaire de LangSmith Deployment) :
- **Enqueue** : finir le run en cours, puis traiter le nouveau message
- **Reject** : refuser le nouveau message
- **Interrupt** : arrêter le run en conservant son état, puis continuer avec le nouveau message
- **Rollback** : annuler le run en cours et repartir du nouveau message

---

Pourquoi une sandbox d'exécution ?
?
Le code, les commandes et la navigation web générés par le modèle sont du **code non fiable**, potentiellement influencé par une injection de prompt. La sandbox les exécute dans un environnement **isolé et jetable** :
- **Isolation forte** : microVM (Firecracker), gVisor ou Kata, plutôt qu'un conteneur classique qui partage le noyau de l'hôte
- **Réseau sortant filtré**, système de fichiers éphémère, limites CPU et mémoire
- **Aucun secret** accessible depuis la sandbox

Exemples : AgentCore Code Interpreter, E2B, Daytona, Modal, Cloudflare Sandboxes, Agent Sandbox pour Kubernetes (avec un pool de sandboxes préchauffées). Voir aussi [[34-harness-plugins|harness]].

---

Qu'est-ce qu'une gateway d'outils (ou gateway MCP) ?
?
Le **point de passage unique entre les agents et les outils** :
- Elle **transforme des API existantes** (OpenAPI, fonctions serverless) en outils MCP
- Elle gère l'**authentification** vers chaque outil
- Elle filtre les outils **visibles par chaque agent**
- Elle applique **politiques d'accès, quotas et audit** à chaque appel

Exemples : AgentCore Gateway, Agent Gateway de Google, agentgateway en open source. À ne pas confondre avec la [[81-litellm-api-layer|gateway LLM]], qui se place entre l'application et les **modèles**.

---

Pourquoi un registre d'outils centralisé ?
?
Pour **publier une fois** les agents, serveurs MCP, outils et skills de l'entreprise, avec un **circuit de revue et d'approbation**. Il sert à :
- **Découvrir** ce qui existe (recherche sémantique), plutôt que de réintégrer les mêmes API dans chaque équipe
- **Contrôler** qui peut utiliser quoi, et **épingler les versions** approuvées
- Tenir l'**inventaire** : propriétaire, usage, niveau de risque

Exemples : AgentCore Registry, Agent Registry de Google, registre d'Agent 365, registre officiel MCP pour les serveurs publics.

---

Pourquoi l'identité est-elle un sujet clé pour les agents ?
?
Un agent **agit dans des systèmes réels** : il faut savoir **qui il est** et **au nom de qui** il agit. Deux cas :
- **Agent délégué** : il agit **au nom d'un utilisateur** et hérite de **ses droits** (OAuth, accès délégué), jamais d'un compte de service surpuissant
- **Agent autonome** : il a **sa propre identité** et ses propres droits, avec un humain responsable

Les plateformes donnent une identité à chaque agent (Entra Agent ID, AgentCore Identity, Agent Identity) et gardent les jetons **hors du code et du contexte de l'agent**. C'est le principe du **moindre privilège** ([[101-securite-llm-guardrails|sécurité LLM]]).

---

Quelle mémoire fournit une plateforme d'agents ?
?
- **Court terme** : l'historique de la session ou du thread, conservé côté serveur
- **Long terme** : faits, préférences et résumés **extraits automatiquement** des conversations et retrouvés dans les sessions suivantes (ex. AgentCore Memory, Memory Bank de Google)
- **Stores partagés** entre agents, **cloisonnés** par utilisateur ou par client

Voir [[39-memoire-agents|mémoire des agents]].

---

Quel rôle joue l'observabilité dans une plateforme ?
?
**Tracer chaque étape** de l'agent (appels LLM, outils, décisions, approbations), mesurer coûts et latence, et rattacher des **scores de qualité**. Les plateformes émettent des traces **OpenTelemetry** (conventions GenAI), lisibles dans Langfuse, Datadog, CloudWatch… ([[91-langfuse-observabilite|Langfuse]], [[93-monitoring-inference|monitoring]]).

---

Comment évalue-t-on un agent sur une plateforme ?
?
À deux moments :
- **Avant déploiement** : datasets de tâches et **simulation** (utilisateurs synthétiques, outils virtualisés)
- **En continu** : **scoring d'un échantillon de traces** de production par des évaluateurs (souvent LLM-as-judge)

Ce qu'on mesure :
- **Réussite de la tâche**
- **Trajectoire** : les bons outils, dans le bon ordre, avec des arguments corrects
- **Coût et nombre d'étapes**
- **Sécurité** et respect des règles

AgentCore Evaluations propose une dizaine d'évaluateurs prêts à l'emploi.

---

Quels protocoles rendent une plateforme interopérable ?
?
- **MCP** : agent ↔ outils et données ([[33-mcp|MCP]]). Depuis la spec **2026-07-28**, il est **sans état** : il passe derrière un simple load balancer
- **A2A** : agent ↔ agent, entre éditeurs ([[36-orchestration-agents|orchestration]]). Version **1.0** en mars 2026 avec des **Agent Cards signées**
- **OpenTelemetry** : format commun des traces
- **AGENTS.md** : instructions pour les agents de code

MCP, A2A et AGENTS.md sont hébergés par l'**Agentic AI Foundation** (Linux Foundation), ce qui limite le verrouillage par un seul éditeur.

---

Build ou buy ?
?
- **Buy** (plateforme cloud ou harness managé) : mise en production rapide, sécurité et scaling gérés, mais **lock-in** et produits qui changent vite
- **Build** (framework + Kubernetes + briques open source) : contrôle et portabilité, mais tout le run est à votre charge

En pratique, souvent **hybride** : acheter le runtime et les sandboxes, garder la **logique d'agent en code** et s'appuyer sur des **standards ouverts**. Critères détaillés : [[115-plateformes-agents-gouvernance|architecture & gouvernance]].

---

## Connexions
- [[37-frameworks-agents|Frameworks d'agents]] — le code qu'on y déploie
- [[115-plateformes-agents-gouvernance|Plateformes d'agents — Architecture & gouvernance]] — la suite, niveau senior
- [[34-harness-plugins|Harness & plugins]] — la boucle d'agent et la sandbox
- [[33-mcp|MCP]] — le protocole des outils et le registre de serveurs
- [[36-orchestration-agents|Orchestration multi-agents]] — ce que le runtime doit supporter, protocole A2A
- [[39-memoire-agents|Mémoire des agents]] — la brique mémoire
- [[45-langgraph-production|LangGraph — Production]] — checkpoints, interruptions, déploiement
- [[91-langfuse-observabilite|Langfuse]] — la brique observabilité
- [[93-monitoring-inference|Monitoring de l'inférence]] — métriques et alertes en production
- [[101-securite-llm-guardrails|Sécurité LLM]] — identité et permissions
- [[81-litellm-api-layer|LiteLLM]] — la gateway LLM
- [[83-gateway-ingress|Ingress]] — l'entrée réseau
- [[104-securite-mcp-skills|Sécurité de MCP & des skills]] — pourquoi une gateway et un registre d'outils
- [[00-moc-ai-engineering|MOC AI Engineering]]
