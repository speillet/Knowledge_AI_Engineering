# Automatisation code & no-code — Flashcards
Tags: #flashcards #ai-engineering #automatisation #workflow #llm
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.

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
```python
# le moteur enregistre le résultat de chaque étape : au redémarrage,
# il rejoue le code mais renvoie les résultats déjà connus
async def traiter_dossier(id):
    donnees   = await etape(extraire, id)         # déjà fait → résultat rejoué
    analyse   = await etape(analyser_llm, donnees) # déjà fait → résultat rejoué
    decision  = await attendre_humain(analyse)     # reprend ici, 2 jours plus tard
    await etape(notifier, decision)                # exécuté une seule fois
```
Condition indispensable : des étapes **idempotentes**, sinon la reprise renvoie deux fois le même e-mail ([[45-langgraph-production|checkpoints]]).

---

À ne pas confondre : orchestrateur de données et durable execution ?
?
- **Airflow, Dagster, Prefect** : pensés pour des **pipelines planifiés** (batch nocturne, ETL). Granularité : la tâche, l'exécution périodique
- **Temporal, Restate, DBOS** : pensés pour des **processus longs et événementiels**, avec état, attentes humaines et reprise **à l'instruction près**

Un agent qui attend une validation pendant deux jours relève du second, pas du premier.

---

Quelles limites du no-code en production ?
?
**Versioning et diff** difficiles, **tests automatisés** limités, gestion des erreurs et des secrets à surveiller, et risque de **workflows « shadow IT »** que personne ne maintient.

---

## Mises en situation

Mise en situation : le service marketing a monté seul un workflow n8n qui envoie des e-mails clients avec un LLM, et il tourne déjà en production. Que fais-tu ?
?
1. **Ne pas l'interdire sèchement** : il répond à un vrai besoin et il tourne. Le supprimer pousserait le sujet dans l'ombre
2. **Inventorier** : que fait-il, quelles données touche-t-il, quels secrets utilise-t-il, qui le maintient
3. **Sécuriser l'essentiel** : clés passées par la [[81-litellm-api-layer|gateway]], budgets, pas de données sensibles en clair, traces centralisées
4. **Encadrer** : validation humaine avant envoi, gestion des erreurs, propriétaire identifié
5. **Décider ensuite** : le garder en no-code s'il reste simple, ou le passer en code s'il devient critique (versioning, tests, revue)

**Piège** : laisser vivre un workflow « shadow IT » sans propriétaire, jusqu'au jour où il envoie mille e-mails erronés.

---

Mise en situation : ton processus d'onboarding client dure trois jours, avec deux validations humaines et un appel LLM par étape. Quel outillage choisis-tu ?
?
1. **Reconnaître le besoin** : un processus long, avec attentes humaines, doit **survivre aux redémarrages**
2. **Durable execution** : Temporal ou un framework à checkpoints, pour reprendre sans rejouer les appels déjà faits ([[45-langgraph-production|LangGraph en production]])
3. **Idempotence** de chaque étape qui écrit ou envoie quelque chose
4. **Attentes humaines** modélisées comme des états, avec délais d'expiration et relances
5. **Observabilité** : où en est chaque dossier, quelles étapes ont échoué ([[93-monitoring-inference|monitoring]])

**Piège** : un script cron qui relance tout depuis le début après un incident, et qui renvoie les e-mails déjà partis.

---

## Connexions
- [[31-agents-fondamentaux|Agents]] — workflow vs agent
- [[36-orchestration-agents|Orchestration multi-agents]] — quand le workflow ne suffit plus
- [[32-tool-calling|Tool calling]] — un workflow peut servir d'outil à un agent
- [[44-langgraph-fondamentaux|LangGraph]] — workflows et agents en code, sous forme de graphe
- [[47-crewai-flows|CrewAI Flows]] — workflows événementiels qui orchestrent des crews
- [[81-litellm-api-layer|LiteLLM]] — point d'accès aux modèles
- [[91-langfuse-observabilite|Langfuse]] — les traces restent centralisées
- [[48-patterns-workflows-agentiques|Patterns de workflows]] — les patterns derrière les workflows
- [[00-moc-ai-engineering|MOC AI Engineering]]
