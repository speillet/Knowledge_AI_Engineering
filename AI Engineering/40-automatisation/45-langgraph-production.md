# LangGraph — Production (persistance, HITL, multi-agents) — Flashcards
Tags: #flashcards #ai-engineering #agents #langgraph #llm

Qu'est-ce qu'un checkpointer ?
?
Le composant qui **sauvegarde l'état du graphe après chaque super-step**. Il apporte la mémoire de conversation, la reprise après erreur, le human-in-the-loop et le time travel.

```python
graph = builder.compile(checkpointer=checkpointer)
```

---

Quels checkpointers existent ?
?
- **`InMemorySaver`** : en mémoire, perdu au redémarrage (tests)
- **`SqliteSaver`** : fichier local (développement)
- **`PostgresSaver`** / `AsyncPostgresSaver` : **production**

---

Qu'est-ce qu'un thread ?
?
Une **suite de checkpoints** identifiée par un **`thread_id`**, passé dans la config (`{"configurable": {"thread_id": "..."}}`). Même `thread_id` = on reprend l'état ; nouveau `thread_id` = on repart de zéro.

---

Comment mettre un humain dans la boucle ?
?
Un nœud appelle **`interrupt(payload)`** : l'état est sauvegardé et l'exécution **s'arrête** en renvoyant le payload. On reprend avec **`Command(resume=valeur)`** sur le même thread ; `valeur` devient le retour de `interrupt()`.

```python
from langgraph.types import interrupt, Command

def approbation(state):
    ok = interrupt("Valider l'envoi de ce mail ?")
    return {"approuve": ok}

graph.invoke(Command(resume=True), config=config)
```

---

Pourquoi un checkpointer est-il obligatoire pour `interrupt` ?
?
Parce que la reprise peut arriver **des minutes ou des jours plus tard**, dans un autre processus : l'état doit être **persisté** pour que le graphe reparte exactement du point d'arrêt.

---

Qu'est-ce que le time travel ?
?
Parcourir l'**historique des checkpoints** d'un thread (`get_state_history`), **rejouer** depuis un checkpoint passé ou le **modifier** (`update_state`) pour explorer une autre branche — très utile pour déboguer un agent.

---

Checkpointer ou Store : quelle différence ?
?
- **Checkpointer** : mémoire **court terme**, propre à **un thread**
- **Store** (ex. `InMemoryStore`) : mémoire **long terme, partagée entre threads**, organisée en **namespaces** (ex. `("user-123", "preferences")`), avec recherche sémantique possible

---

Qu'est-ce que la durable execution ?
?
La capacité d'un workflow à **reprendre après une panne** ou une longue pause **depuis le dernier checkpoint**, sans refaire le travail déjà fait. Les **effets de bord** (appels d'API, écritures) doivent être isolés dans des tâches pour ne pas être rejoués.

---

Que peut-on streamer depuis un graphe ?
?
L'**état complet** après chaque étape (`values`), les **mises à jour** de chaque nœud (`updates`), les **tokens** du LLM (`messages`) ou des **événements personnalisés** (`custom`). Les versions récentes ajoutent aussi `stream_events(..., version="v3")`.

---

Qu'est-ce qu'un subgraph ?
?
Un **graphe compilé utilisé comme nœud** d'un autre graphe. On découpe ainsi un système complexe en modules, souvent **un subgraph par agent**.

---

Quels patterns multi-agents LangChain/LangGraph documentent-ils ?
?
- **Subagents** : un agent principal appelle des sous-agents **comme des outils**
- **Handoffs** : un agent **passe la main** à un autre via un appel d'outil
- **Router** : une étape classe la requête et l'envoie au bon agent
- **Skills** : un seul agent charge du contexte spécialisé à la demande
- **Custom workflow** : un graphe sur mesure qui combine les précédents

---

Comment déployer et déboguer un graphe LangGraph ?
?
- **LangSmith Deployment** (ex-LangGraph Platform) : un **Agent Server** qui expose le graphe en API, avec persistance, files de tâches et streaming gérés
- **Studio** : IDE visuel pour exécuter pas à pas et inspecter l'état
- **Auto-hébergé** : le graphe dans son propre service (FastAPI, conteneur) avec un `PostgresSaver`

---

## Connexions
- [[44-langgraph-fondamentaux|LangGraph — Fondamentaux]] — state, nodes, edges
- [[43-langchain-agents|LangChain — Agents]] — HITL et mémoire via middleware
- [[36-orchestration-agents|Orchestration multi-agents]] — les patterns
- [[35-context-engineering|Context engineering]] — mémoire court et long terme
- [[41-automatisation-code-nocode|Automatisation]] — durable execution (Temporal)
- [[91-langfuse-observabilite|Langfuse]] — tracer les exécutions
- [[00-moc-ai-engineering|MOC AI Engineering]]
