# Orchestration multi-agents — Flashcards
Tags: #flashcards #ai-engineering #agents #multi-agent #llm
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.

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
```text
                 ┌── worker : sources FR ──┐
orchestrateur ───┼── worker : sources EN ──┼──→ synthèse
                 └── worker : brevets ─────┘
```
Chaque worker travaille dans **son propre contexte** et ne remonte qu'un **résultat structuré**. C'est ce qui protège le contexte de l'orchestrateur, mais aussi ce qui multiplie les tokens ([[35-context-engineering|context engineering]]).

---

Qu'est-ce que le pattern supervisor (hiérarchique) ?
?
Un agent **superviseur** choisit à chaque étape **quel agent spécialisé** doit agir, et peut empiler plusieurs niveaux (superviseurs de superviseurs).

---

Qu'est-ce qu'un handoff ?
?
Le **transfert du contrôle de la conversation** d'un agent à un autre (ex. triage → agent facturation), avec le contexte nécessaire pour continuer. Techniquement, c'est souvent un **appel d'outil** particulier, qui passe la main au lieu de renvoyer un résultat.

---

À ne pas confondre : sous-agent et handoff ?
?
- **Sous-agent** : l'agent principal **garde le contrôle**. Il appelle le sous-agent comme un outil, reçoit un **résumé** et continue. Le contexte reste cloisonné
- **Handoff** : l'agent **cède le contrôle** et ne reprend pas la main. C'est le suivant qui parle à l'utilisateur

Choix pratique : sous-agent pour **explorer** ou paralléliser, handoff pour **router** vers une spécialité (triage vers facturation).

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
**Agent2Agent** (initié par Google) : un standard pour que des agents **de fournisseurs différents** se découvrent (**Agent Card**) et se délèguent des tâches — là où [[33-mcp|MCP]] relie un agent à ses **outils**. Version **1.0** en mars 2026 (Agent Cards signées), hébergé depuis août 2026 par l'**Agentic AI Foundation**, comme MCP.

---

Quel est l'intérêt principal des sous-agents ?
?
L'**isolation du contexte** : chaque sous-agent explore dans son propre contexte et ne remonte que l'essentiel ([[35-context-engineering|context engineering]]).

---

## Mises en situation

Mise en situation : une équipe propose une architecture à sept agents (recherche, rédaction, relecture, SEO, traduction, publication, supervision) pour produire des articles. Qu'en penses-tu ?
?
1. **Questionner le besoin** : ces étapes sont **séquentielles et prévisibles**, donc un workflow avec quelques appels LLM suffit souvent ([[41-automatisation-code-nocode|automatisation]])
2. **Rappeler le coût** : chaque agent a son contexte. Un système multi-agents consomme beaucoup plus de tokens et cumule les latences
3. **Garder le multi-agent** là où il apporte quelque chose : la recherche, parallélisable sur plusieurs sources
4. **Simplifier** : un agent principal, des sous-agents de recherche, et du code pour l'enchaînement
5. **Comparer** les deux versions sur la même tâche : qualité, coût, latence, facilité de débogage

**Piège** : un superviseur qui coordonne six agents et devient le vrai goulot, impossible à déboguer.

---

Mise en situation : dans ton système orchestrateur-workers, un worker renvoie une donnée fausse que l'orchestrateur reprend telle quelle dans sa synthèse. Comment évites-tu la propagation ?
?
1. **Traiter la sortie d'un worker comme non fiable**, même s'il est interne ([[103-defenses-agents|défenses]])
2. **Formats structurés** : le worker renvoie des champs validés par schéma, avec ses **sources**, pas un texte libre
3. **Vérification** : recoupement entre workers, ou contrôle déterministe quand c'est possible
4. **Coupe-circuit** : au-delà d'un taux d'erreurs, on arrête la chaîne plutôt que de publier
5. **Tracer** chaque étape, pour retrouver l'agent à l'origine de l'erreur ([[93-monitoring-inference|traces]])

**Piège** : juger la qualité seulement sur le résultat final, sans jamais regarder les étapes intermédiaires.

---

Mise en situation : un partenaire veut que ton agent de réservation dialogue avec le sien, développé avec un autre framework. Comment procèdes-tu ?
?
1. **A2A** : exposer une **Agent Card** décrivant les compétences, l'endpoint et l'authentification, et consommer la sienne
2. **Vérifier l'identité** : Agent Cards signées, authentification mutuelle, périmètre d'actions autorisé
3. **Cadrer les échanges** : tâches typées, formats structurés, délais et reprise sur erreur
4. **Se protéger** : ce que renvoie l'agent partenaire est une **entrée non fiable**, à valider avant toute action
5. **Observer** : traces et métriques de bout en bout, et un coupe-circuit si le partenaire se dégrade

**Piège** : donner au partenaire un accès direct à tes outils au lieu de passer par une interface d'agent contrôlée.

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
- [[103-defenses-agents|Sécurité des agents — Architecture défensive]] — sécuriser les échanges entre agents
- [[48-patterns-workflows-agentiques|Patterns de workflows]] — chaining, routing, evaluator-optimizer
- [[27-agents-recherche-deep-research|Agents de recherche]] — le cas d'école de l'orchestrateur et des sous-agents
- [[98-debogage-agents|Débogage des agents]] — les échecs de coordination (MAST)
- [[00-moc-ai-engineering|MOC AI Engineering]]
