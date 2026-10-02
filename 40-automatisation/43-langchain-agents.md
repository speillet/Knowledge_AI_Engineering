# LangChain — Agents & middleware — Flashcards
Tags: #flashcards #ai-engineering #agents #langchain #llm
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.

Qu'est-ce que `create_agent` ?
?
<!--anki:7a4b2e797a59726e6d3e-->
La fonction de LangChain v1 qui construit un **agent prêt à l'emploi** : un modèle, des outils, un system prompt, et la **boucle** modèle → outils → modèle jusqu'à la réponse finale ([[31-agents-fondamentaux|ReAct]]).

```python
from langchain.agents import create_agent

agent = create_agent(
    model="anthropic:claude-sonnet-4-5",
    tools=[get_weather],
    system_prompt="Tu es un assistant météo concis.",
)
result = agent.invoke({"messages": [{"role": "user", "content": "Météo à Lyon ?"}]})
print(result["messages"][-1].content)
```

---

Sur quoi repose `create_agent` ?
?
<!--anki:48725f6e587475697364-->
Sur **[[44-langgraph-fondamentaux|LangGraph]]** : l'agent est un graphe compilé. Il hérite donc de la **persistance**, du **human-in-the-loop**, du streaming et de la durable execution de LangGraph.

---

Comment donner une mémoire de conversation à l'agent ?
?
<!--anki:412f743a4b36626b4447-->
En lui passant un **checkpointer** et en réutilisant le même **`thread_id`** d'un appel à l'autre : l'historique du thread est rechargé automatiquement.

```python
from langgraph.checkpoint.memory import InMemorySaver

agent = create_agent(model=..., tools=[...], checkpointer=InMemorySaver())
config = {"configurable": {"thread_id": "conv-42"}}
agent.invoke({"messages": [...]}, config=config)
```

---

Comment obtenir une réponse finale structurée ?
?
<!--anki:6e2d72285b7b3141633b-->
Avec `response_format=MonModelePydantic` : l'agent termine par une sortie validée, disponible dans **`result["structured_response"]`**.

---

Qu'est-ce qu'un middleware dans LangChain ?
?
<!--anki:704e5b615d724d26394b-->
Un composant qui **s'insère dans la boucle de l'agent** pour observer ou modifier son comportement (contexte, appels au modèle, appels d'outils) sans réécrire la boucle. C'est le principal point d'extension de la v1, comparable aux hooks d'un [[34-harness-plugins|harness]].

---

Quels hooks un middleware peut-il implémenter ?
?
<!--anki:623b496e31414c772f60-->
- **Style nœud** : `before_agent`, `before_model`, `after_model`, `after_agent`
- **Style wrapper** : `wrap_model_call`, `wrap_tool_call` (pour retry, fallback, cache…)
Chaque hook existe aussi en **décorateur** (`@before_model`, `@wrap_tool_call`…), plus `@dynamic_prompt`.

---

À quoi ressemble un middleware personnalisé ?
?
<!--anki:62663d2665583f485161-->
```python
from langchain.agents.middleware import before_model, AgentState
from langgraph.runtime import Runtime

@before_model
def log_before_model(state: AgentState, runtime: Runtime):
    print(f"{len(state['messages'])} messages envoyés au modèle")
    return None  # ou un dict de mise à jour de l'état
```
Un hook peut aussi renvoyer **`jump_to`** (`"end"`, `"tools"`, `"model"`) pour court-circuiter la boucle.

---

Citez des middlewares fournis par LangChain.
?
<!--anki:4a5532617776615f543e-->
- **HumanInTheLoopMiddleware** : approbation humaine avant certains outils
- **SummarizationMiddleware** : résume l'historique près de la limite ([[35-context-engineering|compaction]])
- **ModelFallbackMiddleware**, **ModelRetryMiddleware**, **ToolRetryMiddleware**
- **ModelCallLimitMiddleware**, **ToolCallLimitMiddleware** : plafonner les coûts
- **PIIMiddleware**, **ContextEditingMiddleware**, **TodoListMiddleware**

---

Comment fonctionne l'approbation humaine avec `create_agent` ?
?
<!--anki:494756303d597a3c6960-->
Le **HumanInTheLoopMiddleware** interrompt l'agent avant les outils sensibles (ex. `send_email`) ; l'état est sauvegardé par le checkpointer. On reprend ensuite avec un **`Command(resume=...)`** qui contient la décision : approuver, modifier ou rejeter l'appel ([[45-langgraph-production|interrupts LangGraph]]).

---

Comment passer des données propres à l'exécution (utilisateur, tenant) ?
?
<!--anki:734e286f38437868654c-->
Par un **`context_schema`** : on passe `context=...` à `invoke`, et ces données sont accessibles dans les middlewares et les outils via le **runtime**, sans être mises dans les messages vus par le modèle.

---

Qu'est-ce que Deep Agents ?
?
<!--anki:7670636152256a7e7468-->
Une surcouche « **batteries included** » bâtie sur les agents LangChain : **planification** (todo list), **système de fichiers virtuel**, **sous-agents** et **compression automatique du contexte**, pour les tâches longues.

---

Quand descendre de `create_agent` vers LangGraph ?
?
<!--anki:6c6473235e656b6e5743-->
Quand le flux doit être **explicite** : étapes déterministes mêlées à des étapes agentiques, branches et boucles sur mesure, plusieurs agents coordonnés — c'est le domaine de [[44-langgraph-fondamentaux|LangGraph]].

---

## Mises en situation

Mise en situation : ton agent LangChain doit demander une validation avant tout envoi d'e-mail, plafonner ses appels au modèle et résumer l'historique quand il s'allonge. Comment l'implémentes-tu ?
?
<!--anki:51313d393b6e7032624a-->
1. **Ne pas réécrire la boucle** : ces besoins sont des **middlewares**, insérés dans l'agent existant
2. **HumanInTheLoopMiddleware** pour interrompre avant `send_email`, avec reprise par `Command(resume=...)`
3. **ModelCallLimitMiddleware** et **ToolCallLimitMiddleware** pour plafonner coût et boucles
4. **SummarizationMiddleware** pour la compaction près de la limite ([[35-context-engineering|context engineering]])
5. **Checkpointer** obligatoire : sans persistance, une interruption perd l'état de l'agent

**Piège** : mettre « demande toujours confirmation » dans le system prompt et croire que c'est un contrôle.

---

Mise en situation : tes outils ont besoin de l'identifiant du client et de son niveau d'abonnement, mais tu ne veux pas que le modèle puisse les modifier. Comment fais-tu ?
?
<!--anki:63347e7a64404f595956-->
1. **Ne pas les mettre dans les messages** : tout ce que le modèle voit, il peut le reformuler ou l'inventer
2. **`context_schema`** : passer ces données via `context=...` à l'invocation
3. **Les lire dans le runtime**, côté outils et middlewares, au moment de l'exécution
4. **Vérifier les droits côté outil** à partir de ce contexte, jamais à partir d'un argument fourni par le modèle ([[103-defenses-agents|défenses]])
5. **Tracer** l'identité réelle utilisée pour chaque appel ([[93-monitoring-inference|traces]])

**Piège** : passer le `tenant_id` en paramètre d'outil. Une injection suffirait alors à changer de client.

---

## Connexions
- [[42-langchain-fondamentaux|LangChain — Fondamentaux]] — modèles, outils, messages
- [[44-langgraph-fondamentaux|LangGraph — Fondamentaux]] — le runtime sous-jacent
- [[45-langgraph-production|LangGraph — Production]] — persistance et interrupts
- [[34-harness-plugins|Harness & plugins]] — le middleware comme hook de harness
- [[35-context-engineering|Context engineering]] — résumé et édition du contexte
- [[36-orchestration-agents|Orchestration multi-agents]] — sous-agents, handoffs et A2A
- [[00-moc-ai-engineering|MOC AI Engineering]]
