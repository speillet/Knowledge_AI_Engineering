# Harness & plugins — Flashcards
Tags: #flashcards #ai-engineering #agents #harness #llm
<!-- summary: rôle du harness, plugins, skills, hooks, permissions, sandbox, fichiers mémoire. -->

Qu'est-ce que le harness (harnais) d'un agent ?
?
<!--anki:7976774a57665d6f6958-->
Le **programme qui entoure le modèle** : il fait tourner la boucle, **exécute les outils**, gère le contexte, applique les permissions et affiche le résultat. Le modèle propose, **le harness dispose**.

---

Quelles sont les responsabilités d'un harness ?
?
<!--anki:73483b4938322d2e4366-->
- **Boucle** d'agent et conditions d'arrêt
- **Exécution** des [[32-tool-calling|appels d'outils]] et renvoi des résultats
- **Gestion du contexte** : system prompt, historique, compaction
- **Permissions**, sandboxing, approbations
- **Intégrations** : [[33-mcp|MCP]], plugins, hooks

---

Pourquoi dit-on que le harness compte autant que le modèle ?
?
<!--anki:4976284543642a78436b-->
À modèle égal, la **qualité des outils, du contexte fourni et de la boucle** change radicalement les résultats : un agent de code dépend autant de ses outils de recherche et d'édition que du LLM.

---

Donnez des exemples de harness.
?
<!--anki:67254c614036287a593d-->
**Claude Code, Cursor, Codex CLI, Aider** pour le code ; les SDK (**Claude Agent SDK**, OpenAI Agents SDK) permettent de construire son propre harness.

---

Qu'est-ce qu'un plugin dans un harness ?
?
<!--anki:21632f592e76504753-->
Un **paquet d'extensions** qu'on installe dans le host : **commandes** (slash commands), **skills**, **sous-agents**, **hooks** et **serveurs MCP**, distribués ensemble.

---

Qu'est-ce qu'une skill ?
?
<!--anki:6f3f3e3a684076505951-->
Un **dossier d'instructions et de ressources** (ex. `SKILL.md` + scripts) que l'agent **charge à la demande** quand la tâche s'y prête : seule une courte description reste en permanence dans le contexte (**progressive disclosure**).

---

Qu'est-ce qu'un hook ?
?
<!--anki:4c427a57297048423e58-->
Un **script exécuté par le harness** à un moment précis du cycle (avant ou après un appel d'outil, fin de tour…) : **déterministe**, il peut bloquer une action, formater du code ou journaliser, sans dépendre du bon vouloir du modèle.
```json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "Bash",
        "hooks": [{ "type": "command", "command": "./scripts/verifie-commande.sh" }] }
    ],
    "PostToolUse": [
      { "matcher": "Edit|Write",
        "hooks": [{ "type": "command", "command": "ruff format" }] }
    ]
  }
}
```
Un code de sortie non nul **bloque** l'action : c'est la différence entre une consigne et un contrôle ([[106-securite-agents-code|agents de code]]).

---

Comment un harness gère-t-il les permissions ?
?
<!--anki:723e704a553f6c796757-->
Par des **modes et des règles** : lecture seule, approbation à chaque action, allowlist de commandes, ou autonomie complète — avec **demande de confirmation humaine** pour les actions sensibles.

---

Pourquoi exécuter un agent dans une sandbox ?
?
<!--anki:497a51314634782d6450-->
Pour **limiter le rayon d'impact** d'une erreur ou d'une [[101-securite-llm-guardrails|prompt injection]] : système de fichiers restreint, réseau filtré, conteneur ou VM jetable.

---

À ne pas confondre : fichier mémoire (ex. `CLAUDE.md`) et skill ?
?
<!--anki:77702e78736c33755528-->
Le **fichier mémoire** est chargé **à chaque session** (conventions du projet) ; la **skill** n'est chargée **que quand elle est utile** — on y met les procédures longues et spécialisées.

---

À ne pas confondre : harness, framework et plateforme d'agents ?
?
<!--anki:785e4a4b2b72266e5651-->
- **Harness** : le **programme qui exécute** la boucle chez vous (Claude Code, Cursor, ou le vôtre). Il tient les outils, le contexte et les permissions
- **Framework** : la **bibliothèque** avec laquelle vous écrivez cette boucle (LangGraph, CrewAI) ([[37-frameworks-agents|frameworks]])
- **Plateforme** : le **service managé** qui l'héberge et la gouverne en production ([[38-plateformes-agents|plateformes]])

Un harness peut être écrit sans framework, et déployé sans plateforme. Les trois répondent à des questions différentes : **qui exécute**, **avec quoi on l'écrit**, **où ça tourne**.

---

## Mises en situation

Mise en situation : deux équipes utilisent le même modèle pour le même agent de code, mais l'une obtient de bien meilleurs résultats. Où cherches-tu la différence ?
?
<!--anki:7142566f2e2663332b4c-->
1. **Dans le harness, pas dans le modèle** : à modèle égal, ce sont les outils, le contexte et la boucle qui font la différence
2. **Outils** : qualité de la recherche dans le code, de l'édition, de l'exécution des tests ; descriptions et retours d'erreur
3. **Contexte** : fichier de conventions du projet, skills disponibles, compaction bien réglée ([[35-context-engineering|context engineering]])
4. **Boucle** : conditions d'arrêt, vérification automatique (tests, lint) après chaque modification
5. **Comparer** en faisant tourner les deux configurations sur les mêmes tâches ([[96-evals-rag-agents|evals d'agents]])

**Piège** : conclure trop vite que « l'autre équipe a un meilleur modèle ».

---

Mise en situation : tu veux garantir qu'aucun agent de ton équipe ne puisse lancer `terraform apply` sans relecture, quelle que soit la consigne donnée au modèle. Comment t'y prends-tu ?
?
<!--anki:4c7879576f32706a6e53-->
1. **Ne pas compter sur le prompt** : une consigne se contourne, un contrôle non
2. **Hook** exécuté par le harness avant chaque appel d'outil : il inspecte la commande et **bloque** celles qui correspondent à un motif interdit
3. **Permissions** : liste blanche de commandes, mode approbation pour tout le reste
4. **Paramétrage géré centralement**, non modifiable par l'utilisateur ([[106-securite-agents-code|agents de code]])
5. **Journaliser** chaque blocage, pour ajuster les règles et détecter les contournements

**Piège** : mettre la règle dans le fichier de conventions du projet, que le modèle peut ignorer.

---

## Connexions
- [[31-agents-fondamentaux|Agents]] — la boucle que le harness exécute
- [[32-tool-calling|Tool calling]] — le harness exécute les appels
- [[33-mcp|MCP]] — le harness est le host MCP
- [[35-context-engineering|Context engineering]] — ce que le harness met dans le contexte
- [[101-securite-llm-guardrails|Sécurité LLM]] — permissions et sandbox
- [[38-plateformes-agents|Plateformes d'agents]] — harness à l'échelle d'une organisation
- [[106-securite-agents-code|Sécurité des agents de code]] — modes de permission et isolation des agents de code
- [[49-agents-de-code|Agents de code]] — l'usage quotidien d'un harness de code
- [[103-defenses-agents|Défenses des agents]] — isolation, politiques et moindre privilège
- [[104-securite-mcp-skills|Sécurité de MCP & des skills]] — outils et skills comme chaîne d'approvisionnement
- [[24-cognee|Cognee]] — une mémoire d'agent en knowledge graph
- [[36-orchestration-agents|Orchestration multi-agents]] — sous-agents, handoffs et A2A
- [[39-memoire-agents|Mémoire des agents]] — ce que l'agent retient d'une session à l'autre
- [[43-langchain-agents|LangChain — Agents]] — agents et middleware LangChain
- [[44-langgraph-fondamentaux|LangGraph]] — graphes d'états pour agents et workflows
- [[00-moc-ai-engineering|MOC AI Engineering]]
