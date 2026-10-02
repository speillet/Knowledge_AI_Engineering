# LangChain — Fondamentaux — Flashcards
Tags: #flashcards #ai-engineering #agents #langchain #llm
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.

Qu'est-ce que LangChain aujourd'hui ?
?
<!--anki:6d5e30397b5f6e244140-->
Un framework open source (Python et JS) qui fournit des **composants LLM standardisés** (modèles, messages, outils, retrievers) et, depuis la **v1**, un **harness d'agent** minimal et configurable : `create_agent` ([[43-langchain-agents|LangChain agents]]).

---

Comment sont organisés les paquets LangChain ?
?
<!--anki:6a7e44294e70317a3d68-->
- **`langchain-core`** : abstractions de base (messages, Runnables, outils)
- **`langchain`** : agents et middlewares
- **Intégrations** : `langchain-openai`, `langchain-anthropic`… (un paquet par fournisseur)
- **`langchain-classic`** : les anciennes chains et fonctionnalités de la v0, pour la rétrocompatibilité

---

Comment instancier un modèle indépendamment du fournisseur ?
?
<!--anki:4e6c666e705f3a35383f-->
Avec `init_chat_model` et une chaîne `fournisseur:modèle` : on **change de fournisseur sans changer le code** applicatif.

```python
from langchain.chat_models import init_chat_model

model = init_chat_model("anthropic:claude-sonnet-4-5")
reponse = model.invoke("Explique le RAG en une phrase.")
```

---

Quels types de messages manipule LangChain ?
?
<!--anki:6e25772567323b58302f-->
`SystemMessage`, `HumanMessage`, `AIMessage` (qui peut contenir des `tool_calls`) et `ToolMessage` (résultat d'un outil) — ou de simples dicts `{"role": ..., "content": ...}`. La v1 ajoute des **content blocks standardisés** (texte, raisonnement, appels d'outils) communs à tous les fournisseurs.

---

Comment déclarer un outil ?
?
<!--anki:4e2668233f3b707b5663-->
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
<!--anki:6873426d3e2d217e434c-->
`model.bind_tools([get_weather])` attache les schémas des outils ; la réponse contient alors `response.tool_calls` (nom + arguments). **C'est à vous d'exécuter** l'outil et de renvoyer un `ToolMessage` — ce que `create_agent` automatise.

---

Comment obtenir une sortie structurée ?
?
<!--anki:79644644213972374439-->
`model.with_structured_output(MonModele)` avec un modèle **Pydantic** (ou un JSON Schema) : l'appel renvoie directement un objet validé, en s'appuyant sur les structured outputs ou le tool calling du fournisseur ([[63-guided-generation|guided generation]]).

---

Qu'est-ce que l'interface Runnable et LCEL ?
?
<!--anki:78337d302c763673295f-->
Tout composant expose les mêmes méthodes : **`invoke`, `batch`, `stream`** (et leurs versions async). **LCEL** les compose avec l'opérateur `|` :

```python
chain = prompt | model | StrOutputParser()
chain.invoke({"sujet": "le KV cache"})
```

Toujours disponible dans `langchain-core`, mais la v1 met l'accent sur les agents.

---

Quelles briques LangChain fournit-il pour le RAG ?
?
<!--anki:6d7c557541244b554728-->
**Document loaders** (PDF, web, bases), **text splitters** (ex. `RecursiveCharacterTextSplitter`), **embeddings**, **vector stores** et **retrievers** (`vector_store.as_retriever()`) — tout le pipeline du [[21-rag-fondamentaux|RAG]] avec des interfaces communes.

---

Quel est le rôle de LangSmith ?
?
<!--anki:47476469236b7933533b-->
La plateforme de l'éditeur pour **tracer, déboguer et évaluer** les applications LangChain/LangGraph (activée par variables d'environnement, ex. `LANGSMITH_TRACING=true`). Alternative open source : [[91-langfuse-observabilite|Langfuse]].

---

Quelle critique revient souvent sur LangChain ?
?
<!--anki:4f6a534f5b2a36356f23-->
Des **abstractions épaisses** qui masquent le prompt réellement envoyé et des **API qui ont beaucoup changé** entre versions. La v1 a répondu en **simplifiant** (un seul `create_agent`, anciennes chains déplacées dans `langchain-classic`).

---

## Mises en situation

Mise en situation : ta direction veut pouvoir changer de fournisseur de modèle en cas de hausse de prix, sans réécrire l'application. Comment structures-tu le code ?
?
<!--anki:6c2447527d2a5d675f62-->
1. **Abstraire l'accès au modèle** : `init_chat_model("fournisseur:modèle")`, le nom venant de la configuration et non du code
2. **S'en tenir aux interfaces communes** : messages standard, `@tool`, `with_structured_output`, pour éviter les particularités d'un fournisseur
3. **Passer par une gateway** pour les clés, les budgets et les bascules ([[81-litellm-api-layer|LiteLLM]])
4. **Tester la bascule** : rejouer les evals sur le modèle de secours, car les prompts ne se transposent pas toujours ([[114-reproductibilite-variance|comparaison appariée]])
5. **Surveiller** : qualité, latence et coût par modèle, pour décider avec des chiffres ([[82-routing-llm|routing]])

**Piège** : croire qu'un changement de modèle est neutre. Le code est portable, le comportement ne l'est pas.

---

Mise en situation : ton extraction de données renvoie parfois du JSON invalide, et tu enchaînes les `try/except` pour rattraper les cas. Que changes-tu ?
?
<!--anki:6f787361626c783c4351-->
1. **Arrêter de demander un format** : le **contraindre** avec `with_structured_output` et un modèle Pydantic ([[63-guided-generation|guided generation]])
2. **Valider le contenu**, pas seulement la syntaxe : bornes, énumérations, cohérence entre champs
3. **Prévoir l'échec** : un champ « non trouvé » explicite plutôt qu'une valeur inventée
4. **Tester** sur des documents réels, y compris malformés
5. **Mesurer** le taux de sorties valides comme métrique de production ([[93-monitoring-inference|validations]])

**Piège** : réparer le JSON avec des expressions régulières, ce qui masque les vraies erreurs d'extraction.

---

## Connexions
- [[43-langchain-agents|LangChain — Agents & middleware]] — `create_agent`
- [[44-langgraph-fondamentaux|LangGraph]] — le runtime sous les agents LangChain
- [[37-frameworks-agents|Frameworks d'agents]] — le panorama
- [[32-tool-calling|Tool calling]] — ce que `@tool` et `bind_tools` encapsulent
- [[21-rag-fondamentaux|RAG]] — les briques loaders, splitters, retrievers
- [[00-moc-ai-engineering|MOC AI Engineering]]
