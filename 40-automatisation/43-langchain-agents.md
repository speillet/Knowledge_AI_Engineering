# LangChain — Agents & middleware — Flashcards
Tags: #flashcards #ai-engineering #agents #langchain #llm

Qu'est-ce que `create_agent` ?
?
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
Sur **[[44-langgraph-fondamentaux|LangGraph]]** : l'agent est un graphe compilé. Il hérite donc de la **persistance**, du **human-in-the-loop**, du streaming et de la durable execution de LangGraph.

---

Comment donner une mémoire de conversation à l'agent ?
?
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
Avec `response_format=MonModelePydantic` : l'agent termine par une sortie validée, disponible dans **`result["structured_response"]`**.

---

Qu'est-ce qu'un middleware dans LangChain ?
?
Un composant qui **s'insère dans la boucle de l'agent** pour observer ou modifier son comportement (contexte, appels au modèle, appels d'outils) sans réécrire la boucle. C'est le principal point d'extension de la v1, comparable aux hooks d'un [[34-harness-plugins|harness]].

---

Quels hooks un middleware peut-il implémenter ?
?
- **Style nœud** : `before_agent`, `before_model`, `after_model`, `after_agent`
- **Style wrapper** : `wrap_model_call`, `wrap_tool_call` (pour retry, fallback, cache…)
Chaque hook existe aussi en **décorateur** (`@before_model`, `@wrap_tool_call`…), plus `@dynamic_prompt`.

---

À quoi ressemble un middleware personnalisé ?
?
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
- **HumanInTheLoopMiddleware** : approbation humaine avant certains outils
- **SummarizationMiddleware** : résume l'historique près de la limite ([[35-context-engineering|compaction]])
- **ModelFallbackMiddleware**, **ModelRetryMiddleware**, **ToolRetryMiddleware**
- **ModelCallLimitMiddleware**, **ToolCallLimitMiddleware** : plafonner les coûts
- **PIIMiddleware**, **ContextEditingMiddleware**, **TodoListMiddleware**

---

Comment fonctionne l'approbation humaine avec `create_agent` ?
?
Le **HumanInTheLoopMiddleware** interrompt l'agent avant les outils sensibles (ex. `send_email`) ; l'état est sauvegardé par le checkpointer. On reprend ensuite avec un **`Command(resume=...)`** qui contient la décision : approuver, modifier ou rejeter l'appel ([[45-langgraph-production|interrupts LangGraph]]).

---

Comment passer des données propres à l'exécution (utilisateur, tenant) ?
?
Par un **`context_schema`** : on passe `context=...` à `invoke`, et ces données sont accessibles dans les middlewares et les outils via le **runtime**, sans être mises dans les messages vus par le modèle.

---

Qu'est-ce que Deep Agents ?
?
Une surcouche « **batteries included** » bâtie sur les agents LangChain : **planification** (todo list), **système de fichiers virtuel**, **sous-agents** et **compression automatique du contexte**, pour les tâches longues.

---

Quand descendre de `create_agent` vers LangGraph ?
?
Quand le flux doit être **explicite** : étapes déterministes mêlées à des étapes agentiques, branches et boucles sur mesure, plusieurs agents coordonnés — c'est le domaine de [[44-langgraph-fondamentaux|LangGraph]].

---

## Connexions
- [[42-langchain-fondamentaux|LangChain — Fondamentaux]] — modèles, outils, messages
- [[44-langgraph-fondamentaux|LangGraph — Fondamentaux]] — le runtime sous-jacent
- [[45-langgraph-production|LangGraph — Production]] — persistance et interrupts
- [[34-harness-plugins|Harness & plugins]] — le middleware comme hook de harness
- [[35-context-engineering|Context engineering]] — résumé et édition du contexte
- [[00-moc-ai-engineering|MOC AI Engineering]]
