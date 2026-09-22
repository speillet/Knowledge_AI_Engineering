# Orchestration multi-agents — Flashcards
Tags: #flashcards #ai-engineering #agents #multi-agent #llm

Qu'est-ce qu'un système multi-agents ?
?
Plusieurs **agents LLM spécialisés** (rôle, outils et contexte propres) qui **coopèrent** sur une tâche, coordonnés par un orchestrateur ou par des règles de passage de main.

---

Quand passer au multi-agent ?
?
Quand la tâche est **parallélisable**, qu'elle **dépasse la fenêtre de contexte** d'un seul agent, ou qu'elle demande des **outils ou expertises très différents**. Sinon, **un seul agent** reste plus simple et moins cher.

---

Qu'est-ce que le pattern orchestrator-workers ?
?
Un **orchestrateur** découpe la tâche, **délègue** des sous-tâches à des workers (souvent en parallèle), puis **synthétise** leurs résultats.

---

Qu'est-ce que le pattern supervisor (hiérarchique) ?
?
Un agent **superviseur** choisit à chaque étape **quel agent spécialisé** doit agir, et peut empiler plusieurs niveaux (superviseurs de superviseurs).

---

Qu'est-ce qu'un handoff ?
?
Le **transfert du contrôle de la conversation** d'un agent à un autre (ex. triage → agent facturation), avec le contexte nécessaire pour continuer.

---

Quels autres patterns de composition existent ?
?
- **Séquentiel** (pipeline) : la sortie de l'un est l'entrée du suivant
- **Parallèle** : sections indépendantes ou votes
- **Evaluator-optimizer** : un agent produit, un autre critique, on itère

---

Quel est le coût du multi-agent ?
?
**Beaucoup plus de tokens** (chaque agent a son contexte), une **latence** qui s'additionne et un **débogage plus difficile** : les erreurs se propagent d'un agent à l'autre.

---

Comment les agents partagent-ils l'information ?
?
Par des **messages** (résumés renvoyés à l'orchestrateur), un **état partagé** (graphe d'état, tableau blanc) ou des **artefacts externes** (fichiers, base) — ce qui évite de tout faire passer par le contexte.

---

Qu'est-ce que le protocole A2A ?
?
**Agent2Agent** (initié par Google) : un standard pour que des agents **de fournisseurs différents** se découvrent (**Agent Card**) et se délèguent des tâches — là où [[33-mcp|MCP]] relie un agent à ses **outils**.

---

Quel est l'intérêt principal des sous-agents ?
?
L'**isolation du contexte** : chaque sous-agent explore dans son propre contexte et ne remonte que l'essentiel ([[35-context-engineering|context engineering]]).

---

## Connexions
- [[31-agents-fondamentaux|Agents]] — l'agent unique avant le multi-agent
- [[35-context-engineering|Context engineering]] — isoler les contextes
- [[37-frameworks-agents|Frameworks d'agents]] — LangGraph, CrewAI, ADK
- [[38-plateformes-agents|Plateformes d'agents]] — exécuter en production
- [[41-automatisation-code-nocode|Automatisation]] — quand un workflow suffit
- [[45-langgraph-production|LangGraph en production]] — subagents, handoffs, router en pratique
- [[46-crewai-crews|CrewAI]] — process séquentiel ou hiérarchique
- [[115-plateformes-agents-gouvernance|Plateformes d'agents — Architecture & gouvernance]] — gouverner une flotte d'agents
- [[00-moc-ai-engineering|MOC AI Engineering]]
