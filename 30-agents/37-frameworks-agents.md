# Frameworks d'agents — Flashcards
Tags: #flashcards #ai-engineering #agents #frameworks #llm

À quoi sert un framework d'agents ?
?
À fournir des **briques prêtes** : abstraction des fournisseurs de modèles, déclaration d'outils, boucle d'agent, mémoire, persistance de l'état, streaming et intégrations d'observabilité.

---

Qu'est-ce que LangChain ?
?
Une bibliothèque de **composants LLM** (modèles, prompts, retrievers, outils) et d'**intégrations** avec des centaines de fournisseurs. Depuis la v1, elle fournit aussi un agent haut niveau, `create_agent`, extensible par **middlewares** et bâti sur LangGraph. Détails : [[42-langchain-fondamentaux|fondamentaux]] et [[43-langchain-agents|agents]].

---

Qu'est-ce que LangGraph ?
?
Un framework (écosystème LangChain) qui modélise l'agent comme un **graphe d'états** : nœuds (étapes), arêtes conditionnelles, **cycles**, **checkpoints** persistés. Il permet la reprise après erreur, le **human-in-the-loop** et le « time travel » dans l'exécution. Détails : [[44-langgraph-fondamentaux|fondamentaux]] et [[45-langgraph-production|production]].

---

Qu'est-ce que CrewAI ?
?
Un framework **multi-agents par rôles** : on définit des agents (rôle, objectif, backstory) et des **tâches**, qu'une « crew » exécute en séquence ou de façon hiérarchique. Très rapide à prototyper ; les **Flows** encadrent les crews en production. Détails : [[46-crewai-crews|crews]] et [[47-crewai-flows|flows]].

---

Qu'est-ce que Google ADK ?
?
L'**Agent Development Kit** de Google : framework open source (Python, Java…) pour construire des agents et des hiérarchies d'agents, optimisé pour Gemini et la Gemini Enterprise Agent Platform (ex-Vertex AI) mais multi-modèles, avec support de **[[33-mcp|MCP]]** et du protocole **A2A**.

---

Que proposent les SDK des fournisseurs de modèles ?
?
Des frameworks **légers** : **OpenAI Agents SDK** (agents, handoffs, guardrails, tracing) et **Claude Agent SDK** (le harness de Claude Code réutilisable : outils, sous-agents, hooks, MCP).

---

Citez d'autres frameworks courants.
?
- **LlamaIndex** : orienté données et RAG (ingestion, index, query engines)
- **Pydantic AI** : typage fort et sorties validées
- **Microsoft Agent Framework** (héritier d'AutoGen et Semantic Kernel)

---

Framework ou code maison ?
?
Une boucle d'agent tient en **quelques dizaines de lignes** : le code maison garde un **contrôle total** et un débogage simple. Un framework se justifie pour la **persistance, le multi-agent, le human-in-the-loop** ou quand l'équipe en maîtrise déjà un.

---

Quels critères pour choisir un framework ?
?
**Contrôle** du flux (graphe explicite ou boucle autonome), **persistance** et reprise, support **multi-modèles** et MCP, **observabilité** native, maturité et stabilité de l'API, langage de l'équipe.

---

Quel piège classique avec les frameworks ?
?
Les **abstractions opaques** : on ne voit plus le prompt réellement envoyé au modèle. Il faut toujours pouvoir **inspecter les appels bruts** (traces [[91-langfuse-observabilite|Langfuse]]).

---

## Connexions
- [[31-agents-fondamentaux|Agents]] — ce que les frameworks implémentent
- [[33-mcp|MCP]] — l'accès standardisé aux outils
- [[36-orchestration-agents|Orchestration multi-agents]] — patterns implémentés par les frameworks
- [[38-plateformes-agents|Plateformes d'agents]] — où les déployer
- [[42-langchain-fondamentaux|LangChain]], [[44-langgraph-fondamentaux|LangGraph]], [[46-crewai-crews|CrewAI]] — les fiches détaillées
- [[32-tool-calling|Tool calling]] — la boucle d'appel sur l'API brute, souvent suffisante sans framework
- [[00-moc-ai-engineering|MOC AI Engineering]]
