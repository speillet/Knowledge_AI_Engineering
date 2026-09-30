# LangGraph — Fondamentaux — Flashcards
Tags: #flashcards #ai-engineering #agents #langgraph #llm
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.

Qu'est-ce que LangGraph ?
?
Un framework **bas niveau d'orchestration et un runtime** pour des agents **longs et avec état**. Il permet de **mélanger étapes déterministes (code) et étapes agentiques (LLM)** dans un même graphe.

---

À ne pas confondre : LangGraph et LangChain ?
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

## Mises en situation

Mise en situation : ton graphe doit résumer un nombre variable de documents (parfois 3, parfois 200) puis produire une synthèse. Comment le construis-tu ?
?
1. **Map-reduce dynamique** : une edge conditionnelle renvoie une liste de `Send`, un par document, car le nombre n'est connu qu'à l'exécution
2. **Reducer d'accumulation** sur la clé qui collecte les résumés, sinon chaque branche écrase la précédente
3. **Limiter le parallélisme** pour ne pas saturer les quotas du fournisseur ([[81-litellm-api-layer|gateway]])
4. **Gérer les échecs partiels** : un document qui échoue ne doit pas faire tomber toute la synthèse
5. **Surveiller le coût** : 200 documents, c'est 200 appels ([[122-finops-llm|FinOps]])

**Piège** : oublier le reducer et ne retrouver qu'un seul résumé sur 200 dans l'état final.

---

Mise en situation : ton équipe hésite entre le graphe explicite et la Functional API pour un processus avec deux branches et une boucle. Comment choisis-tu ?
?
1. **Graphe explicite** : le flux est visible, inspectable dans Studio, et se prête aux branches nombreuses et aux subgraphs
2. **Functional API** : le flux s'écrit en Python classique (if, boucles), plus naturel quand la logique est surtout séquentielle
3. **Point commun** : les deux profitent de la persistance, des interruptions et de la reprise
4. **Critère pratique** : qui va maintenir ? Une équipe non familière des graphes lira plus vite du Python
5. **Garde-fou commun** : `recursion_limit` et conditions de sortie explicites, pour éviter les boucles infinies

**Piège** : modéliser en graphe un enchaînement purement linéaire, ce qui ajoute de la cérémonie sans bénéfice.

---

## Connexions
- [[45-langgraph-production|LangGraph — Production]] — persistance, HITL, multi-agents
- [[43-langchain-agents|LangChain — Agents]] — l'agent haut niveau bâti sur LangGraph
- [[31-agents-fondamentaux|Agents]] — le pattern ReAct
- [[36-orchestration-agents|Orchestration multi-agents]] — les patterns à implémenter
- [[41-automatisation-code-nocode|Automatisation]] — workflow déterministe vs agent
- [[48-patterns-workflows-agentiques|Patterns de workflows]] — les patterns à implémenter en graphe
- [[37-frameworks-agents|Frameworks d'agents]] — panorama des frameworks
- [[42-langchain-fondamentaux|LangChain]] — les briques de base du framework
- [[47-crewai-flows|CrewAI — Flows]] — workflows pilotés par événements
- [[115-plateformes-agents-gouvernance|Plateformes d'agents — gouvernance]] — identité, politiques, audit et coûts d'une flotte d'agents
- [[34-harness-plugins|Harness & plugins]] — le programme qui exécute l'agent
- [[38-plateformes-agents|Plateformes d'agents]] — runtime, sandbox, gateway d'outils et identité
- [[39-memoire-agents|Mémoire des agents]] — ce que l'agent retient d'une session à l'autre
- [[00-moc-ai-engineering|MOC AI Engineering]]
