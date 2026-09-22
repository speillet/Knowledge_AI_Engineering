# LangChain — Fondamentaux — Flashcards
Tags: #flashcards #ai-engineering #agents #langchain #llm

Qu'est-ce que LangChain aujourd'hui ?
?
Un framework open source (Python et JS) qui fournit des **composants LLM standardisés** (modèles, messages, outils, retrievers) et, depuis la **v1**, un **harness d'agent** minimal et configurable : `create_agent` ([[43-langchain-agents|LangChain agents]]).

---

Comment sont organisés les paquets LangChain ?
?
- **`langchain-core`** : abstractions de base (messages, Runnables, outils)
- **`langchain`** : agents et middlewares
- **Intégrations** : `langchain-openai`, `langchain-anthropic`… (un paquet par fournisseur)
- **`langchain-classic`** : les anciennes chains et fonctionnalités de la v0, pour la rétrocompatibilité

---

Comment instancier un modèle indépendamment du fournisseur ?
?
Avec `init_chat_model` et une chaîne `fournisseur:modèle` : on **change de fournisseur sans changer le code** applicatif.

```python
from langchain.chat_models import init_chat_model

model = init_chat_model("anthropic:claude-sonnet-4-5")
reponse = model.invoke("Explique le RAG en une phrase.")
```

---

Quels types de messages manipule LangChain ?
?
`SystemMessage`, `HumanMessage`, `AIMessage` (qui peut contenir des `tool_calls`) et `ToolMessage` (résultat d'un outil) — ou de simples dicts `{"role": ..., "content": ...}`. La v1 ajoute des **content blocks standardisés** (texte, raisonnement, appels d'outils) communs à tous les fournisseurs.

---

Comment déclarer un outil ?
?
Avec le décorateur `@tool` : le **nom de la fonction**, la **docstring** et les **type hints** deviennent le nom, la description et le JSON Schema de l'[[32-tool-calling|outil]].

```python
from langchain.tools import tool

@tool
def get_weather(city: str) -> str:
    """Donne la météo actuelle d'une ville."""
    return f"Il fait beau à {city}"
```

---

Comment un modèle utilise-t-il des outils hors agent ?
?
`model.bind_tools([get_weather])` attache les schémas des outils ; la réponse contient alors `response.tool_calls` (nom + arguments). **C'est à vous d'exécuter** l'outil et de renvoyer un `ToolMessage` — ce que `create_agent` automatise.

---

Comment obtenir une sortie structurée ?
?
`model.with_structured_output(MonModele)` avec un modèle **Pydantic** (ou un JSON Schema) : l'appel renvoie directement un objet validé, en s'appuyant sur les structured outputs ou le tool calling du fournisseur ([[63-guided-generation|guided generation]]).

---

Qu'est-ce que l'interface Runnable et LCEL ?
?
Tout composant expose les mêmes méthodes : **`invoke`, `batch`, `stream`** (et leurs versions async). **LCEL** les compose avec l'opérateur `|` :

```python
chain = prompt | model | StrOutputParser()
chain.invoke({"sujet": "le KV cache"})
```

Toujours disponible dans `langchain-core`, mais la v1 met l'accent sur les agents.

---

Quelles briques LangChain fournit-il pour le RAG ?
?
**Document loaders** (PDF, web, bases), **text splitters** (ex. `RecursiveCharacterTextSplitter`), **embeddings**, **vector stores** et **retrievers** (`vector_store.as_retriever()`) — tout le pipeline du [[21-rag-fondamentaux|RAG]] avec des interfaces communes.

---

Quel est le rôle de LangSmith ?
?
La plateforme de l'éditeur pour **tracer, déboguer et évaluer** les applications LangChain/LangGraph (activée par variables d'environnement, ex. `LANGSMITH_TRACING=true`). Alternative open source : [[91-langfuse-observabilite|Langfuse]].

---

Quelle critique revient souvent sur LangChain ?
?
Des **abstractions épaisses** qui masquent le prompt réellement envoyé et des **API qui ont beaucoup changé** entre versions. La v1 a répondu en **simplifiant** (un seul `create_agent`, anciennes chains déplacées dans `langchain-classic`).

---

## Connexions
- [[43-langchain-agents|LangChain — Agents & middleware]] — `create_agent`
- [[44-langgraph-fondamentaux|LangGraph]] — le runtime sous les agents LangChain
- [[37-frameworks-agents|Frameworks d'agents]] — le panorama
- [[32-tool-calling|Tool calling]] — ce que `@tool` et `bind_tools` encapsulent
- [[21-rag-fondamentaux|RAG]] — les briques loaders, splitters, retrievers
- [[00-moc-ai-engineering|MOC AI Engineering]]
