# Harness & plugins — Flashcards
Tags: #flashcards #ai-engineering #agents #harness #llm

Qu'est-ce que le harness (harnais) d'un agent ?
?
Le **programme qui entoure le modèle** : il fait tourner la boucle, **exécute les outils**, gère le contexte, applique les permissions et affiche le résultat. Le modèle propose, **le harness dispose**.

---

Quelles sont les responsabilités d'un harness ?
?
- **Boucle** d'agent et conditions d'arrêt
- **Exécution** des [[32-tool-calling|appels d'outils]] et renvoi des résultats
- **Gestion du contexte** : system prompt, historique, compaction
- **Permissions**, sandboxing, approbations
- **Intégrations** : [[33-mcp|MCP]], plugins, hooks

---

Pourquoi dit-on que le harness compte autant que le modèle ?
?
À modèle égal, la **qualité des outils, du contexte fourni et de la boucle** change radicalement les résultats : un agent de code dépend autant de ses outils de recherche et d'édition que du LLM.

---

Donnez des exemples de harness.
?
**Claude Code, Cursor, Codex CLI, Aider** pour le code ; les SDK (**Claude Agent SDK**, OpenAI Agents SDK) permettent de construire son propre harness.

---

Qu'est-ce qu'un plugin dans un harness ?
?
Un **paquet d'extensions** qu'on installe dans le host : **commandes** (slash commands), **skills**, **sous-agents**, **hooks** et **serveurs MCP**, distribués ensemble.

---

Qu'est-ce qu'une skill ?
?
Un **dossier d'instructions et de ressources** (ex. `SKILL.md` + scripts) que l'agent **charge à la demande** quand la tâche s'y prête : seule une courte description reste en permanence dans le contexte (**progressive disclosure**).

---

Qu'est-ce qu'un hook ?
?
Un **script exécuté par le harness** à un moment précis du cycle (avant/après un appel d'outil, fin de tour…) : **déterministe**, il peut bloquer une action, formater du code ou journaliser, sans dépendre du bon vouloir du modèle.

---

Comment un harness gère-t-il les permissions ?
?
Par des **modes et des règles** : lecture seule, approbation à chaque action, allowlist de commandes, ou autonomie complète — avec **demande de confirmation humaine** pour les actions sensibles.

---

Pourquoi exécuter un agent dans une sandbox ?
?
Pour **limiter le rayon d'impact** d'une erreur ou d'une [[101-securite-llm-guardrails|prompt injection]] : système de fichiers restreint, réseau filtré, conteneur ou VM jetable.

---

Quelle différence entre fichier mémoire (ex. `CLAUDE.md`) et skill ?
?
Le **fichier mémoire** est chargé **à chaque session** (conventions du projet) ; la **skill** n'est chargée **que quand elle est utile** — on y met les procédures longues et spécialisées.

---

## Connexions
- [[31-agents-fondamentaux|Agents]] — la boucle que le harness exécute
- [[32-tool-calling|Tool calling]] — le harness exécute les appels
- [[33-mcp|MCP]] — le harness est le host MCP
- [[35-context-engineering|Context engineering]] — ce que le harness met dans le contexte
- [[101-securite-llm-guardrails|Sécurité LLM]] — permissions et sandbox
- [[38-plateformes-agents|Plateformes d'agents]] — harness à l'échelle d'une organisation
- [[00-moc-ai-engineering|MOC AI Engineering]]
