# Fondamentaux des agents — Flashcards
Tags: #flashcards #ai-engineering #agents #llm

Qu'est-ce qu'un agent LLM ?
?
Un **LLM doté d'outils et d'une boucle d'exécution** (percevoir → raisonner → agir) qui poursuit un **objectif** en décidant lui-même de ses étapes.

---

Quelle est la différence entre un workflow et un agent ?
?
Un **workflow** suit des étapes prédéfinies par le développeur ; un **agent** décide dynamiquement de ses actions — distinction popularisée par Anthropic (« Building effective agents »).

---

Qu'est-ce que le pattern ReAct ?
?
Une boucle **Reasoning + Acting** : le modèle alterne raisonnement, appel d'outil et observation du résultat jusqu'à la réponse finale.

---

De quoi est composé un agent minimal ?
?
- Un **modèle**
- Des **[[32-tool-calling|outils]]**
- Une **boucle** de contrôle
- Un **[[35-context-engineering|contexte]]** (instructions, historique, mémoire)

---

Quand ne faut-il PAS construire un agent ?
?
Quand la tâche est **prévisible** : un workflow fixe est plus fiable, moins cher et plus simple à déboguer. **L'agent se justifie quand le chemin est inconnu à l'avance.**

---

Qu'est-ce que le human-in-the-loop ?
?
Des **points de validation humaine** insérés dans la boucle de l'agent (actions sensibles, irréversibles ou coûteuses).

---

Quels sont les principaux risques d'un agent ?
?
**Boucles infinies, dérive d'objectif, actions destructives, coût** — d'où limites d'itérations, garde-fous et permissions.

---

Comment un agent sait-il quand s'arrêter ?
?
Quand le modèle **répond sans appeler d'outil** (ou émet un signal de fin), ou quand le harnais atteint une **limite** (itérations, budget).

---

## Connexions
- [[32-tool-calling|Tool calling]] — les mains de l'agent
- [[34-harness-plugins|Harness]] — le cadre d'exécution
- [[35-context-engineering|Context engineering]] — la mémoire de travail
- [[36-orchestration-agents|Orchestration multi-agents]] — passage à l'échelle
- [[41-automatisation-code-nocode|Automatisation]] — workflow vs agent
- [[00-moc-ai-engineering|MOC AI Engineering]]
