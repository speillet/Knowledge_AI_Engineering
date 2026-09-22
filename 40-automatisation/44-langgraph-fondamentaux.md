# LangGraph — Fondamentaux — Flashcards
Tags: #flashcards #ai-engineering #agents #langgraph #llm

Qu'est-ce que LangGraph ?
?
Un framework **bas niveau d'orchestration et un runtime** pour des agents **longs et avec état**. Il permet de **mélanger étapes déterministes (code) et étapes agentiques (LLM)** dans un même graphe.

---

Quelle différence entre LangGraph et LangChain ?
?
**LangChain** fournit des composants et un agent haut niveau (`create_agent`) ; **LangGraph** est le **moteur d'orchestration** en dessous. On commence souvent avec [[43-langchain-agents|create_agent]] et on passe à LangGraph pour contrôler le flux.

---

Quels sont les trois éléments d'un graphe LangGraph ?
?
- **State** : l'état partagé (TypedDict ou Pydantic)
- **Nodes** : des fonctions qui reçoivent l'état et renvoient une **mise à jour partielle**
- **Edges** : les transitions entre nœuds (fixes ou conditionnelles)

---

Qu'est-ce qu'un reducer ?
?
La fonction qui dit **comment appliquer la mise à jour d'un nœud** à une clé de l'état. Par défaut la valeur est **remplacée** ; avec un reducer elle est **combinée** :

```python
from typing import Annotated
from operator import add
from typing_extensions import TypedDict

class State(TypedDict):
    notes: Annotated[list[str], add]  # les listes s'accumulent
```

---

Qu'est-ce que `MessagesState` ?
?
Un état prédéfini avec une clé **`messages`** et le reducer **`add_messages`**, qui **ajoute** les nouveaux messages (et met à jour ceux qui ont le même id) : la base de tout agent conversationnel.

---

Comment écrire une boucle d'agent ReAct avec LangGraph ?
?
```python
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition

def call_model(state: MessagesState):
    return {"messages": [model_with_tools.invoke(state["messages"])]}

builder = StateGraph(MessagesState)
builder.add_node("llm", call_model)
builder.add_node("tools", ToolNode([get_weather]))
builder.add_edge(START, "llm")
builder.add_conditional_edges("llm", tools_condition)  # → "tools" ou fin
builder.add_edge("tools", "llm")
graph = builder.compile()
```

---

Qu'est-ce qu'une edge conditionnelle ?
?
Une transition dont la destination est calculée par une **fonction de routage** qui lit l'état : `add_conditional_edges("noeud", route)`. C'est ce qui crée les **branches** et les **boucles** (cycles) du graphe.

---

Comment LangGraph exécute-t-il un graphe ?
?
Par **super-steps** (modèle Pregel) : tous les nœuds actifs d'une étape s'exécutent (**en parallèle** s'il y en a plusieurs), leurs mises à jour sont fusionnées via les reducers, puis l'état est **checkpointé** avant l'étape suivante.

---

À quoi sert l'API `Send` ?
?
Au **map-reduce dynamique** : quand le nombre de branches n'est connu qu'à l'exécution, une edge conditionnelle renvoie une liste de `Send`, un par élément à traiter.

```python
from langgraph.types import Send

def repartir(state):
    return [Send("resumer", {"doc": d}) for d in state["docs"]]
```

---

À quoi sert `Command` ?
?
À **mettre à jour l'état et choisir le nœud suivant** depuis un nœud, en une seule instruction : `return Command(update={"statut": "ok"}, goto="valider")`. Très utilisé pour les **handoffs** entre agents.

---

Comment éviter qu'un graphe boucle à l'infini ?
?
Avec la **`recursion_limit`** (nombre maximal de super-steps, passé dans la config) et des **conditions de sortie** explicites dans les fonctions de routage.

---

Existe-t-il une alternative au graphe explicite ?
?
**Oui** : la **Functional API** (décorateurs `@entrypoint` et `@task`) écrit le flux en **Python classique** (if, boucles) tout en profitant de la persistance et des interruptions de LangGraph.

---

## Connexions
- [[45-langgraph-production|LangGraph — Production]] — persistance, HITL, multi-agents
- [[43-langchain-agents|LangChain — Agents]] — l'agent haut niveau bâti sur LangGraph
- [[31-agents-fondamentaux|Agents]] — le pattern ReAct
- [[36-orchestration-agents|Orchestration multi-agents]] — les patterns à implémenter
- [[41-automatisation-code-nocode|Automatisation]] — workflow déterministe vs agent
- [[00-moc-ai-engineering|MOC AI Engineering]]
