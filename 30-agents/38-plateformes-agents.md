# Plateformes d'agents — Flashcards
Tags: #flashcards #ai-engineering #agents #platform #llm
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.

À ne pas confondre : framework et plateforme d'agents ?
?
<!--anki:66657538313d7a42737a-->
Le **[[37-frameworks-agents|framework]]** sert à **écrire** l'agent (bibliothèque) ; la **plateforme** sert à l'**exécuter et le gouverner en production** : runtime managé, sandbox, mémoire, accès aux outils, identité, politiques d'accès, observabilité, evals. La suite senior de cette fiche : [[115-plateformes-agents-gouvernance|architecture & gouvernance]].

---

Quelles briques d'exécution fournit une plateforme d'agents ?
?
<!--anki:737d4d4e712a33605833-->
- **Runtime** : exécute les sessions d'agent, isolées et longues
- **Sandbox** : exécute le code et le navigateur de l'agent sans risque
- **Mémoire** : court terme (session) et long terme
- **Gateway d'outils** : expose les API comme outils [[33-mcp|MCP]]

---

Quelles briques de gouvernance fournit une plateforme d'agents ?
?
<!--anki:5262495061614f2a237c-->
- **Registre** : catalogue des agents, outils et skills
- **Identité et politiques d'accès** : qui l'agent représente, ce qu'il a le droit de faire
- **Observabilité, evals, coûts**

En 2026, AWS, Google et Microsoft proposent toutes ces briques, souvent **utilisables séparément**.

---

Quels niveaux d'abstraction proposent les plateformes ?
?
<!--anki:493c4c5225462a41395a-->
Du plus flexible au plus clé en main :
1. **API du modèle** : on écrit sa propre boucle d'agent ([[34-harness-plugins|harness]]) et on l'héberge soi-même
2. **Runtime managé** : on apporte son code d'agent, quel que soit le framework (LangGraph, ADK, CrewAI…), et la plateforme l'exécute (sessions, scaling, isolation)
3. **Harness managé** : on **déclare** seulement le modèle, le prompt, les outils et les skills, et la plateforme fournit la boucle elle-même (ex. **Claude Managed Agents**, **AgentCore Harness**)

---

Donnez des exemples de plateformes d'agents cloud.
?
<!--anki:6c2e232f513e5d4f3246-->
- **AWS** : **Bedrock AgentCore** (Harness, Runtime, Memory, Gateway, Identity, Code Interpreter, Browser, Observability, Evaluations, Policy, Registry)
- **Google** : **Gemini Enterprise Agent Platform**, nouveau nom de Vertex AI depuis avril 2026 (ADK, Agent Studio, runtime managé, Memory Bank, Agent Registry, Agent Identity, Agent Gateway)
- **Microsoft** : **Foundry Agent Service** (hosted agents, une identité Entra par agent), gouverné par **Agent 365**
- **Éditeurs de données et de SaaS** : Databricks, Snowflake, Salesforce Agentforce, ServiceNow

---

Que proposent les fournisseurs de modèles ?
?
<!--anki:4824477c257e78733d3a-->
- **OpenAI** : **Agents SDK** pour le code, **Frontier** (février 2026) pour gérer des agents en entreprise, y compris ceux d'autres éditeurs, et les **Workspace Agents** de ChatGPT pour les non-développeurs. Le builder visuel **Agent Builder** ferme le **30 novembre 2026**
- **Anthropic** : **Claude Agent SDK** pour le code, **Claude Managed Agents** (bêta depuis avril 2026) : un harness hébergé autour de 4 concepts, **agent**, **environment** (sandbox cloud ou auto-hébergée), **session** et **events**

---

Existe-t-il des plateformes open source ?
?
<!--anki:63642e78254937534137-->
**Oui**, à deux niveaux :
- **Builders visuels** auto-hébergeables : **Dify** (suite complète : workflows, base de connaissances, publication d'apps), **Langflow**, **Flowise**, **n8n** (automatisation avec des nœuds d'agent)
- **Briques d'infrastructure** : **kagent** (agents déclarés comme ressources Kubernetes et déployés en GitOps), **Agent Sandbox** (sandboxes sur Kubernetes), **agentgateway** (gateway pour MCP, A2A et LLM)

---

Qu'apporte un runtime d'agents par rapport à un déploiement web classique ?
?
<!--anki:423134626b627b623839-->
Un agent ne ressemble pas à une requête HTTP courte :
- **Sessions longues** : minutes, heures, voire jours (ex. jusqu'à 8 h par session sur AgentCore Runtime)
- **Isolation par session**, souvent une microVM par session
- **Exécution asynchrone** en arrière-plan, déclenchement par **cron** ou par événement
- **Reprise après panne** grâce à l'état sauvegardé ([[45-langgraph-production|checkpoints]])
- **Streaming**, **interruptions** pour le human-in-the-loop, gestion des messages concurrents

---

Qu'est-ce que le double texting ?
?
<!--anki:6d6275635935573e2957-->
L'utilisateur envoie un **nouveau message pendant que l'agent travaille** encore sur le précédent. Le runtime doit décider quoi faire du run en cours : le finir, l'interrompre ou l'annuler.

---

Quelles stratégies un runtime propose-t-il face au double texting ?
?
<!--anki:42397a604d446b253650-->
Quatre stratégies (vocabulaire de LangSmith Deployment) :
- **Enqueue** : finir le run en cours, puis traiter le nouveau message
- **Reject** : refuser le nouveau message
- **Interrupt** : arrêter le run en conservant son état, puis continuer avec le nouveau message
- **Rollback** : annuler le run en cours et repartir du nouveau message

---

Pourquoi une sandbox d'exécution ?
?
<!--anki:74725137757b39403351-->
Le code, les commandes et la navigation web générés par le modèle sont du **code non fiable**, potentiellement influencé par une injection de prompt. La sandbox les exécute dans un environnement **isolé et jetable** :
- **Isolation forte** : microVM (Firecracker), gVisor ou Kata, plutôt qu'un conteneur classique qui partage le noyau de l'hôte ([[03-containerd-runc|runtime]])
- **Réseau sortant filtré**, système de fichiers éphémère, limites CPU et mémoire
- **Aucun secret** accessible depuis la sandbox

---

Quels services de sandbox pour agents connaître ?
?
<!--anki:493231677a3150776559-->
- **Managés chez un cloud** : AgentCore Code Interpreter (AWS), Cloudflare Sandboxes
- **Spécialisés** : E2B, Daytona, Modal
- **Sur son cluster** : Agent Sandbox pour Kubernetes, avec un **pool de sandboxes préchauffées** pour masquer le temps de démarrage

Critères de choix : technologie d'isolation, **temps de démarrage**, persistance possible entre deux appels, filtrage réseau. Voir aussi [[34-harness-plugins|harness]].

---

Qu'est-ce qu'une gateway d'outils (ou gateway MCP) ?
?
<!--anki:677b3430255e3c483576-->
Le **point de passage unique entre les agents et les outils** :
- Elle **transforme des API existantes** (OpenAPI, fonctions serverless) en outils MCP
- Elle gère l'**authentification** vers chaque outil
- Elle filtre les outils **visibles par chaque agent**
- Elle applique **politiques d'accès, quotas et audit** à chaque appel

Exemples : AgentCore Gateway, Agent Gateway de Google, agentgateway en open source. À ne pas confondre avec la [[81-litellm-api-layer|gateway LLM]], qui se place entre l'application et les **modèles**.

---

Pourquoi un registre d'outils centralisé ?
?
<!--anki:6f2a595b353e4852725a-->
Pour **publier une fois** les agents, serveurs MCP, outils et skills de l'entreprise, avec un **circuit de revue et d'approbation**. Il sert à :
- **Découvrir** ce qui existe (recherche sémantique), plutôt que de réintégrer les mêmes API dans chaque équipe
- **Contrôler** qui peut utiliser quoi, et **épingler les versions** approuvées
- Tenir l'**inventaire** : propriétaire, usage, niveau de risque

Exemples : AgentCore Registry, Agent Registry de Google, registre d'Agent 365, registre officiel MCP pour les serveurs publics.

---

Pourquoi l'identité est-elle un sujet clé pour les agents ?
?
<!--anki:627564286c41662c6a68-->
Un agent **agit dans des systèmes réels** : il faut savoir **qui il est** et **au nom de qui** il agit, pour lui donner les bons droits et pour que l'audit sache qui a fait quoi.

Les plateformes donnent une identité à chaque agent (Entra Agent ID, AgentCore Identity, Agent Identity) et gardent les jetons **hors du code et du contexte de l'agent**. C'est le principe du **moindre privilège** ([[101-securite-llm-guardrails|sécurité LLM]]).

---

À ne pas confondre : agent délégué et agent autonome ?
?
<!--anki:41734f3c442839645429-->
- **Agent délégué** : il agit **au nom d'un utilisateur** et hérite de **ses droits** (OAuth, accès délégué), jamais d'un compte de service surpuissant
- **Agent autonome** : il agit **en son nom propre**, avec sa propre identité et ses propres droits, et un **humain propriétaire** responsable

Le mécanisme des jetons est détaillé dans la fiche senior ([[115-plateformes-agents-gouvernance|gouvernance]]).

---

Quelle mémoire fournit une plateforme d'agents ?
?
<!--anki:484a632f5562363b4a5d-->
- **Court terme** : l'historique de la session ou du thread, conservé côté serveur
- **Long terme** : faits, préférences et résumés **extraits automatiquement** des conversations et retrouvés dans les sessions suivantes (ex. AgentCore Memory, Memory Bank de Google)
- **Stores partagés** entre agents, **cloisonnés** par utilisateur ou par client

Voir [[39-memoire-agents|mémoire des agents]].

---

Quel rôle joue l'observabilité dans une plateforme ?
?
<!--anki:7751412e48372c7b3f42-->
**Tracer chaque étape** de l'agent (appels LLM, outils, décisions, approbations), mesurer coûts et latence, et rattacher des **scores de qualité**. Les plateformes émettent des traces **OpenTelemetry** (conventions GenAI), lisibles dans Langfuse, Datadog, CloudWatch… ([[91-langfuse-observabilite|Langfuse]], [[93-monitoring-inference|monitoring]]).

---

À quels moments évalue-t-on un agent sur une plateforme ?
?
<!--anki:4e706774217c234e5623-->
- **Avant déploiement** : datasets de tâches et **simulation** (utilisateurs synthétiques, outils virtualisés)
- **En continu** : **scoring d'un échantillon de traces** de production par des évaluateurs (souvent LLM-as-judge)

---

Que mesure-t-on quand on évalue un agent ?
?
<!--anki:514c36507e6b23627d33-->
- **Réussite de la tâche**
- **Trajectoire** : les bons outils, dans le bon ordre, avec des arguments corrects
- **Coût et nombre d'étapes**
- **Sécurité** et respect des règles

AgentCore Evaluations propose une dizaine d'évaluateurs prêts à l'emploi.

---

Quels protocoles rendent une plateforme interopérable ?
?
<!--anki:742e4e7131465e7c6163-->
- **MCP** : agent ↔ outils et données ([[33-mcp|MCP]]). Depuis la spec **2026-07-28**, il est **sans état** : il passe derrière un simple load balancer
- **A2A** : agent ↔ agent, entre éditeurs ([[36-orchestration-agents|orchestration]]). Version **1.0** en mars 2026 avec des **Agent Cards signées**
- **OpenTelemetry** : format commun des traces
- **AGENTS.md** : instructions pour les agents de code

MCP, A2A et AGENTS.md sont hébergés par l'**Agentic AI Foundation** (Linux Foundation), ce qui limite le verrouillage par un seul éditeur.

---

Build ou buy ?
?
<!--anki:68367e4b62543e7d4623-->
- **Buy** (plateforme cloud ou harness managé) : mise en production rapide, sécurité et scaling gérés, mais **lock-in** et produits qui changent vite
- **Build** (framework + Kubernetes + briques open source) : contrôle et portabilité, mais tout le run est à votre charge

En pratique, souvent **hybride** : acheter le runtime et les sandboxes, garder la **logique d'agent en code** et s'appuyer sur des **standards ouverts**. Critères détaillés : [[115-plateformes-agents-gouvernance|architecture & gouvernance]].

---

## Mises en situation

Mise en situation : ton prototype d'agent tourne dans un conteneur avec une API FastAPI. Il doit maintenant servir 200 utilisateurs, avec des tâches de 20 minutes. Qu'est-ce qui casse en premier ?
?
<!--anki:49552d657c4b4132623a-->
1. **Les requêtes longues** : une API HTTP classique ne tient pas des tâches de 20 minutes. Il faut de l'**exécution asynchrone** et un suivi de tâche
2. **L'état** : sans checkpoints, un redéploiement perd tout le travail en cours ([[45-langgraph-production|checkpoints]])
3. **L'isolation** : les sessions partagent le même processus, donc le code généré par l'une peut affecter les autres
4. **Les messages concurrents** : un utilisateur qui réécrit pendant le travail (double texting)
5. **La décision** : runtime managé, ou construire runtime, sandbox et reprise soi-même ([[115-plateformes-agents-gouvernance|architecture & gouvernance]])

**Piège** : mettre un simple autoscaling devant, alors que le problème est le modèle d'exécution.

---

Mise en situation : ta direction veut « une plateforme d'agents » en trois mois, et ton entreprise est déjà sur Microsoft 365. Par quoi commences-tu ?
?
<!--anki:69692f513c3f55756a61-->
1. **Suivre les données et l'identité** : avec Entra et Microsoft 365, la voie courte passe par Foundry pour construire et Agent 365 pour gouverner
2. **Commencer par un cas d'usage** mesurable, pas par la plateforme complète
3. **Poser les briques transverses** dès le premier agent : identité, registre, gateway d'outils, traces
4. **Garder la logique d'agent en code** versionné, pour rester portable ([[115-plateformes-agents-gouvernance|lock-in]])
5. **Prévoir la gouvernance** : propriétaire par agent, revue avant mise en production, budgets

**Piège** : lancer six agents en parallèle sans socle commun, et devoir tout reprendre au premier audit.

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
- [[103-defenses-agents|Défenses des agents]] — isolation, politiques et moindre privilège
- [[122-finops-llm|FinOps LLM]] — attribuer et piloter les dépenses IA
- [[165-computer-use-agents-navigateur|Computer use & agents navigateur]] — agents qui utilisent des interfaces
- [[44-langgraph-fondamentaux|LangGraph]] — graphes d'états pour agents et workflows
- [[49-agents-de-code|Agents de code]] — utiliser et intégrer les agents de code
- [[85-carte-protocoles-agentiques|Carte des protocoles]] — quel protocole à quelle frontière de l'agent
- [[95-llm-as-judge|LLM-as-a-judge]] — noter automatiquement, et valider le juge
- [[00-moc-ai-engineering|MOC AI Engineering]]
