# Automatisation code & no-code — Flashcards
Tags: #flashcards #ai-engineering #automatisation #workflow #llm

Workflow ou agent : quelle différence ?
?
Un **workflow** enchaîne des étapes **définies à l'avance** (déterministe, prévisible, testable) ; un **[[31-agents-fondamentaux|agent]]** décide lui-même de ses étapes. Beaucoup de besoins « IA » sont en fait des **workflows avec un appel LLM au milieu**.

---

Qu'est-ce que n8n ?
?
Un outil d'**automatisation de workflows** visuel, **self-hostable** (licence fair-code) : des **nœuds** reliés (API, bases, LLM) déclenchés par des **triggers**, avec la possibilité d'insérer du code JavaScript ou Python.

---

Qu'est-ce qu'un trigger dans un outil de workflow ?
?
L'**événement qui lance le workflow** : webhook, planification (cron), nouveau mail, message Slack, ligne ajoutée dans une base…

---

Comment intègre-t-on un LLM dans un workflow n8n ?
?
Par des **nœuds IA** : appel de modèle, extraction structurée, classification, ou nœud **AI Agent** avec outils et mémoire — l'agent devient **une étape** d'un workflow maîtrisé.

---

n8n, Zapier ou Make ?
?
- **Zapier / Make** : SaaS, très simples, énormément de connecteurs, coût à l'exécution
- **n8n** : **self-hosting**, données chez soi, code possible, mieux adapté aux besoins techniques

---

Quand passer du no-code au code ?
?
Quand il faut **versionner, tester, faire de la revue de code**, gérer une logique complexe, de gros volumes ou des SLA stricts. Le no-code excelle pour **prototyper** et pour les intégrations simples.

---

Quels outils d'orchestration « code » utilise-t-on ?
?
- **Airflow** : DAG de pipelines batch planifiés (data)
- **Prefect** / **Dagster** : orchestration Python plus moderne
- **Temporal** : **durable execution**, workflows longs qui survivent aux pannes

---

Pourquoi la durable execution intéresse-t-elle les agents ?
?
Un agent long (minutes ou heures, avec validations humaines) doit **reprendre là où il s'est arrêté** après un crash ou une attente, sans rejouer les appels LLM et les actions déjà faites.

---

Quelles limites du no-code en production ?
?
**Versioning et diff** difficiles, **tests automatisés** limités, gestion des erreurs et des secrets à surveiller, et risque de **workflows « shadow IT »** que personne ne maintient.

---

## Connexions
- [[31-agents-fondamentaux|Agents]] — workflow vs agent
- [[36-orchestration-agents|Orchestration multi-agents]] — quand le workflow ne suffit plus
- [[32-tool-calling|Tool calling]] — un workflow peut servir d'outil à un agent
- [[44-langgraph-fondamentaux|LangGraph]] — workflows et agents en code, sous forme de graphe
- [[47-crewai-flows|CrewAI Flows]] — workflows événementiels qui orchestrent des crews
- [[81-litellm-api-layer|LiteLLM]] — point d'accès aux modèles
- [[91-langfuse-observabilite|Langfuse]] — les traces restent centralisées
- [[00-moc-ai-engineering|MOC AI Engineering]]
