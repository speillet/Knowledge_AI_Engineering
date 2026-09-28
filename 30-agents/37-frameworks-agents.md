# Frameworks d'agents — Flashcards
Tags: #flashcards #ai-engineering #agents #frameworks #llm
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.

À quoi sert un framework d'agents ?
?
À fournir des **briques prêtes** : abstraction des fournisseurs de modèles, déclaration d'outils, boucle d'agent, mémoire, persistance de l'état, streaming et intégrations d'observabilité.

---

Qu'est-ce que LangChain ?
?
Une bibliothèque de **composants LLM** (modèles, prompts, retrievers, outils) et d'**intégrations** avec des centaines de fournisseurs. Depuis la v1, elle fournit aussi un agent haut niveau, `create_agent`, extensible par **middlewares** et bâti sur LangGraph. Détails : [[42-langchain-fondamentaux|fondamentaux]] et [[43-langchain-agents|agents]].

---

Que propose LangGraph dans l'écosystème LangChain ?
?
Un framework qui modélise l'agent comme un **graphe d'états** : nœuds (étapes), arêtes conditionnelles, **cycles**, **checkpoints** persistés. Il permet la reprise après erreur, le **human-in-the-loop** et le « time travel » dans l'exécution. Détails : [[44-langgraph-fondamentaux|fondamentaux]] et [[45-langgraph-production|production]].

---

Qu'apporte CrewAI par rapport aux autres frameworks d'agents ?
?
Une approche **multi-agents par rôles** : on définit des agents (rôle, objectif, backstory) et des **tâches**, qu'une « crew » exécute en séquence ou de façon hiérarchique. Très rapide à prototyper ; les **Flows** encadrent les crews en production. Détails : [[46-crewai-crews|crews]] et [[47-crewai-flows|flows]].

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

À ne pas confondre : LangChain, LangGraph et LangSmith ?
?
```text
LangChain   → les composants : modèles, outils, retrievers, et create_agent
LangGraph   → le moteur d'orchestration et le runtime (graphe d'états,
              checkpoints, interruptions) sur lequel s'appuie create_agent
LangSmith   → la plateforme : traces, evals, datasets, et le déploiement
              (LangSmith Deployment, ex-LangGraph Platform)
```
Autrement dit : **avec quoi** on écrit, **quoi** exécute le flux, **où** on l'observe et le déploie. Les trois sont indépendants : on peut utiliser LangGraph sans LangChain, ou tracer une application maison dans LangSmith.

---

## Mises en situation

Mise en situation : tu démarres un assistant interne qui appelle trois outils et doit reprendre après une coupure. Framework ou code maison ?
?
1. **Cadrer le besoin réel** : la boucle d'appel tient en quelques dizaines de lignes ; ce qui coûte cher, c'est la **persistance** et la reprise
2. **Ce qui pousse vers un framework** : checkpoints, human-in-the-loop, multi-agents, streaming, reprise après crash ([[44-langgraph-fondamentaux|LangGraph]])
3. **Ce qui pousse vers le code maison** : peu d'étapes, besoin de contrôle total, équipe qui ne connaît aucun framework
4. **Compromis fréquent** : boucle maison sur l'API brute, plus une bibliothèque pour la persistance
5. **Condition non négociable** : pouvoir **inspecter les appels bruts** envoyés au modèle ([[91-langfuse-observabilite|traces]])

**Piège** : choisir un framework pour ses démos, puis se battre contre ses abstractions dès le premier cas particulier.

---

Mise en situation : ton équipe hésite entre CrewAI et LangGraph pour un processus d'analyse de documents en cinq étapes, avec validation humaine à l'étape 3. Comment tranches-tu ?
?
1. **Regarder la nature du flux** : cinq étapes connues, avec une interruption au milieu, c'est un **graphe explicite** plus qu'une équipe d'agents autonomes
2. **LangGraph** : état explicite, interruption et reprise, time travel, adapté au human-in-the-loop ([[45-langgraph-production|production]])
3. **CrewAI** : plus rapide à prototyper par rôles, avec ses **Flows** pour encadrer l'exécution ([[47-crewai-flows|flows]])
4. **Décider sur des critères** : contrôle du flux, persistance, observabilité, langage et compétences de l'équipe
5. **Prototyper** la même étape critique dans les deux, plutôt que de trancher sur la documentation

**Piège** : comparer les frameworks sur le temps du premier prototype, alors que le coût réel est en production.

---

## Connexions
- [[31-agents-fondamentaux|Agents]] — ce que les frameworks implémentent
- [[33-mcp|MCP]] — l'accès standardisé aux outils
- [[36-orchestration-agents|Orchestration multi-agents]] — patterns implémentés par les frameworks
- [[38-plateformes-agents|Plateformes d'agents]] — où les déployer
- [[42-langchain-fondamentaux|LangChain]], [[44-langgraph-fondamentaux|LangGraph]], [[46-crewai-crews|CrewAI]] — les fiches détaillées
- [[32-tool-calling|Tool calling]] — la boucle d'appel sur l'API brute, souvent suffisante sans framework
- [[00-moc-ai-engineering|MOC AI Engineering]]
