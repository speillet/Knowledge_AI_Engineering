# LangGraph — Fondamentaux — Flashcards
Tags: #flashcards #ai-engineering #agents #langgraph #llm
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.
<!-- summary: `StateGraph`, state et reducers, `MessagesState`, nodes et edges conditionnelles, boucle ReAct en graphe, super-steps, `Send` (map-reduce), `Command`, Functional API. -->


Qu'est-ce que LangGraph ? <!--anki:6c283f532b7b414f4e78-->
?
Un framework **bas niveau d'orchestration et un runtime** pour des agents **longs et avec état**. Il permet de **mélanger étapes déterministes (code) et étapes agentiques (LLM)** dans un même graphe.

L'état transporte les informations entre étapes et les transitions déterminent la suite du travail. Exemple : rechercher, analyser, demander une validation, puis agir. Le graphe rend le contrôle explicite ; la fiabilité dépend encore des fonctions exécutées, du stockage de checkpoints et du traitement des effets externes.

---

Quels sont les trois éléments d'un graphe LangGraph ? <!--anki:2571304a364929733c-->
?
- **State** : l'état partagé (TypedDict ou Pydantic)
- **Nodes** : des fonctions qui reçoivent l'état et renvoient une **mise à jour partielle**
- **Edges** : les transitions entre nœuds (fixes ou conditionnelles)

Par exemple, l'état contient un ticket, un nœud calcule sa catégorie et une transition choisit le traitement correspondant. Définir des clés et contrats clairs évite que les étapes dépendent implicitement de l'historique. Pour les écritures concurrentes, préciser comment fusionner les mises à jour au moyen de reducers adaptés.

---

Qu'est-ce qu'un reducer dans LangGraph ? <!--anki:66312c767534457c4079-->
?
La fonction qui dit **comment appliquer la mise à jour d'un nœud** à une clé de l'état. Par défaut la valeur est **remplacée** ; avec un reducer elle est **combinée** :

```python
from typing import Annotated
from operator import add
from typing_extensions import TypedDict

class State(TypedDict):
    notes: Annotated[list[str], add]  # les listes s'accumulent
```

Avec cet exemple, deux sorties `['a']` et `['b']` s'accumulent au lieu que la seconde écrase la première. Le choix doit respecter le sens métier : concaténer peut créer des doublons lors d'une reprise. Pour des objets identifiés, une fusion par identifiant est parfois préférable à une addition aveugle.

---

Qu'est-ce que `MessagesState` ? <!--anki:516c586a45296d392342-->
?
Un état prédéfini avec une clé **`messages`** et le reducer **`add_messages`**, qui **ajoute** les nouveaux messages (et met à jour ceux qui ont le même id) : la base de tout agent conversationnel.

Le reducer traite donc l'historique comme des messages identifiés, et non comme une simple liste à concaténer. Préserver les liens entre appels d'outils et réponses reste essentiel. Ce type d'état n'ajoute pas, à lui seul, de stockage durable ni de mémoire commune à toutes les conversations.

---

Comment écrire une boucle d'agent ReAct avec LangGraph ? <!--anki:6e7d42476361234b54-->
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

Le nœud `llm` ajoute la réponse du modèle ; `tools_condition` termine si aucun outil n'est demandé, sinon `ToolNode` exécute puis rend la main au modèle. `get_weather` et `model_with_tools` sont des prérequis : le modèle doit être lié aux mêmes outils. Ajouter limites d'itérations, permissions et gestion des erreurs avant un usage réel.

---

Qu'est-ce qu'une edge conditionnelle dans LangGraph ? <!--anki:4335732e4d703f5b4531-->
?
Une transition dont la destination est calculée par une **fonction de routage** qui lit l'état : `add_conditional_edges("noeud", route)`. C'est ce qui crée les **branches** et les **boucles** (cycles) du graphe.

Par exemple, router vers une correction si la validation échoue, sinon vers la fin. Tester toutes les valeurs de retour et assurer une condition de sortie pour chaque cycle. Une transition peut être déterministe même si l'information utilisée pour la choisir provient d'un LLM incertain.

---

Comment LangGraph exécute-t-il un graphe ? <!--anki:50592646755542376a7c-->
?
Par **super-steps** (modèle Pregel) : tous les nœuds actifs d'une étape s'exécutent (**en parallèle** s'il y en a plusieurs), leurs mises à jour sont fusionnées via les reducers, puis l'état est **checkpointé** avant l'étape suivante.

---

À quoi sert l'API `Send` de LangGraph ? <!--anki:6d3b50523a447c7d7e4a-->
?
Au **map-reduce dynamique** : quand le nombre de branches n'est connu qu'à l'exécution, une edge conditionnelle renvoie une liste de `Send`, un par élément à traiter.

```python
from langgraph.types import Send

def repartir(state):
    return [Send("resumer", {"doc": d}) for d in state["docs"]]
```

Chaque branche reçoit un état adapté à un document, puis ses résultats doivent être réunis avec un reducer. Borner le nombre de tâches simultanées pour respecter les quotas du modèle. Définir aussi le comportement lorsqu'un document échoue : retry limité, résultat partiel ou arrêt de l'ensemble.

---

À quoi sert `Command` dans LangGraph ? <!--anki:756a654c29346c544574-->
?
À **mettre à jour l'état et choisir le nœud suivant** depuis un nœud, en une seule instruction : `return Command(update={"statut": "ok"}, goto="valider")`. Très utilisé pour les **handoffs** entre agents.

`update` décrit les changements d'état et `goto` la destination choisie. C'est utile lorsqu'une décision produit à la fois une information et un transfert de contrôle. Vérifier les autres edges du nœud : une edge statique peut encore déclencher son chemin, même si `Command` demande une autre destination.

---

Comment éviter qu'un graphe LangGraph boucle à l'infini ? <!--anki:4341417b4c627b246c37-->
?
Avec la **`recursion_limit`** (nombre maximal de super-steps, passé dans la config) et des **conditions de sortie** explicites dans les fonctions de routage.

Cette limite compte les étapes du graphe, pas directement les tokens ni la durée. Ajouter un délai global, un budget d'appels et une détection des actions répétées sans progrès. Intercepter l'erreur de limite et restituer l'état partiel ; augmenter le plafond sans diagnostic peut seulement rendre l'échec plus coûteux.

---

Existe-t-il dans LangGraph une alternative au graphe explicite ? <!--anki:4d6557676c3834252436-->
?
**Oui** : la **Functional API** (décorateurs `@entrypoint` et `@task`) écrit le flux en **Python classique** (if, boucles) tout en profitant de la persistance et des interruptions de LangGraph.

Elle convient lorsque le flux existant est déjà lisible en Python et qu'on veut lui ajouter des points de persistance. Encapsuler les opérations concernées dans des tâches facilite la reprise. Il faut toujours réfléchir aux actions qui peuvent être rejouées : une syntaxe impérative ne fournit pas automatiquement une exécution exactement une fois.

---

## Mises en situation

Mise en situation : ton graphe doit résumer un nombre variable de documents (parfois 3, parfois 200) puis produire une synthèse. Comment le construis-tu ? <!--anki:6772416528637b63416b-->
?
1. **Map-reduce dynamique** : une edge conditionnelle renvoie une liste de `Send`, un par document, car le nombre n'est connu qu'à l'exécution
2. **Reducer d'accumulation** sur la clé qui collecte les résumés, sinon chaque branche écrase la précédente
3. **Limiter le parallélisme** pour ne pas saturer les quotas du fournisseur ([[81-litellm-api-layer|gateway]])
4. **Gérer les échecs partiels** : un document qui échoue ne doit pas faire tomber toute la synthèse
5. **Surveiller le coût** : 200 documents, c'est 200 appels ([[122-finops-llm|FinOps]])

**Piège** : oublier le reducer et ne retrouver qu'un seul résumé sur 200 dans l'état final.

---

Mise en situation : ton équipe hésite entre le graphe explicite et la Functional API pour un processus avec deux branches et une boucle. Comment choisis-tu ? <!--anki:6c30363260537e4c5e57-->
?
1. **Graphe explicite** : le flux est visible, inspectable dans Studio, et se prête aux branches nombreuses et aux subgraphs
2. **Functional API** : le flux s'écrit en Python classique (if, boucles), plus naturel quand la logique est surtout séquentielle
3. **Point commun** : les deux profitent de la persistance, des interruptions et de la reprise
4. **Critère pratique** : qui va maintenir ? Une équipe non familière des graphes lira plus vite du Python
5. **Garde-fou commun** : `recursion_limit` et conditions de sortie explicites, pour éviter les boucles infinies

**Piège** : modéliser en graphe un enchaînement purement linéaire, ce qui ajoute de la cérémonie sans bénéfice.

---

## Sources

- [LangGraph — état, reducers, transitions et Command](https://docs.langchain.com/oss/python/langgraph/graph-api)

- [LangGraph — concepts et architecture](https://docs.langchain.com/oss/python/langgraph/overview)

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
