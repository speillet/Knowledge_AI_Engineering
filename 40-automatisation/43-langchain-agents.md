# LangChain — Agents & middleware — Flashcards
Tags: #flashcards #ai-engineering #agents #langchain #llm
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.
<!-- summary: `create_agent`, mémoire par checkpointer et `thread_id`, `response_format`, hooks de middleware, middlewares fournis (human-in-the-loop, résumé, fallback, limites), runtime context, Deep Agents. -->


Qu'est-ce que `create_agent` ? <!--anki:7a4b2e797a59726e6d3e-->
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

Dans cet exemple, `get_weather` doit déjà être défini et l'intégration du modèle configurée. La fonction construit la boucle, mais il reste à borner les appels, valider les outils et gérer les échecs. La dernière réponse doit être vérifiée selon la tâche, même si l'exécution se termine normalement.

---

Sur quoi repose `create_agent` ? <!--anki:48725f6e587475697364-->
?
Sur **[[44-langgraph-fondamentaux|LangGraph]]** : l'agent est un graphe compilé. Il hérite donc de la **persistance**, du **human-in-the-loop**, du streaming et de la durable execution de LangGraph.

Ces capacités nécessitent une configuration appropriée : un checkpointer persistant pour survivre au redémarrage, des interruptions aux bons endroits et une gestion des effets externes. Construire un agent ne crée pas automatiquement une base de données, une interface d'approbation ou une garantie d'exécution unique des outils.

---

Comment donner une mémoire de conversation à l'agent ? <!--anki:412f743a4b36626b4447-->
?
En lui passant un **checkpointer** et en réutilisant le même **`thread_id`** d'un appel à l'autre : l'historique du thread est rechargé automatiquement.

```python
from langgraph.checkpoint.memory import InMemorySaver

agent = create_agent(model=..., tools=[...], checkpointer=InMemorySaver())
config = {"configurable": {"thread_id": "conv-42"}}
agent.invoke({"messages": [...]}, config=config)
```

`InMemorySaver` convient à une démonstration, mais perd l'historique à l'arrêt du processus. En production, choisir un backend durable et vérifier que l'utilisateur est autorisé à accéder au thread demandé. Réutiliser un identifiant partagé entre utilisateurs mélangerait leurs conversations et pourrait exposer leurs données.

---

Comment obtenir une réponse finale structurée avec create_agent de LangChain ? <!--anki:6e2d72285b7b3141633b-->
?
Avec `response_format=MonModelePydantic` : l'agent termine par une sortie validée, disponible dans **`result["structured_response"]`**.

Le modèle Pydantic décrit les champs, types et contraintes attendus, par exemple `categorie` et `priorite` pour un ticket. La stratégie utilisée dépend du support du fournisseur. Traiter explicitement validation impossible, refus et budget épuisé. Vérifier ensuite le contenu : une priorité autorisée par le schéma peut rester inadaptée au problème décrit.

---

Qu'est-ce qu'un middleware dans LangChain ? <!--anki:704e5b615d724d26394b-->
?
Un composant qui **s'insère dans la boucle de l'agent** pour observer ou modifier son comportement (contexte, appels au modèle, appels d'outils) sans réécrire la boucle. C'est le principal point d'extension de la v1, comparable aux hooks d'un [[34-harness-plugins|harness]].

---

Quels hooks un middleware d'agent LangChain peut-il implémenter ? <!--anki:623b496e31414c772f60-->
?
- **Style nœud** : `before_agent`, `before_model`, `after_model`, `after_agent`
- **Style wrapper** : `wrap_model_call`, `wrap_tool_call` (pour retry, fallback, cache…)
Chaque hook existe aussi en **décorateur** (`@before_model`, `@wrap_tool_call`…), plus `@dynamic_prompt`.

Choisir un hook selon l'endroit où agir : préparer le contexte avant le modèle, examiner sa sortie après, ou entourer un appel pour gérer les erreurs. L'ordre des middlewares influence le résultat. Éviter que plusieurs couches de retry multiplient silencieusement les tentatives et dépassent le budget global.

---

Comment écrire un middleware before_model personnalisé pour un agent LangChain ? <!--anki:62663d2665583f485161-->
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

Ce hook observe l'état sans le modifier. Pour router avec `jump_to`, déclarer les destinations permises via la configuration `can_jump_to` du middleware ; renvoyer une destination arbitraire ne suffit pas. Les logs doivent rester sobres : compter les messages peut être utile sans enregistrer leur contenu confidentiel.

---

Quels middlewares prêts à l'emploi LangChain fournit-il ? <!--anki:4a5532617776615f543e-->
?
- **HumanInTheLoopMiddleware** : approbation humaine avant certains outils
- **SummarizationMiddleware** : résume l'historique près de la limite ([[35-context-engineering|compaction]])
- **ModelFallbackMiddleware**, **ModelRetryMiddleware**, **ToolRetryMiddleware**
- **ModelCallLimitMiddleware**, **ToolCallLimitMiddleware** : plafonner les coûts
- **PIIMiddleware**, **ContextEditingMiddleware**, **TodoListMiddleware**

Choisir les middlewares en fonction du problème observé : boucle trop longue, contexte saturé, outil sensible ou erreur transitoire. Tester leur ordre et leur interaction sur un cas concret. Une limite d'appels doit couvrir toute l'exécution, tandis qu'une approbation humaine doit précéder l'effet externe qu'elle autorise.

---

Comment fonctionne l'approbation humaine avec `create_agent` ? <!--anki:494756303d597a3c6960-->
?
Le **HumanInTheLoopMiddleware** interrompt l'agent avant les outils sensibles (ex. `send_email`) ; l'état est sauvegardé par le checkpointer. On reprend ensuite avec un **`Command(resume=...)`** qui contient la décision : approuver, modifier ou rejeter l'appel ([[45-langgraph-production|interrupts LangGraph]]).

---

Comment passer l'utilisateur et le tenant au runtime d'un agent LangChain ? <!--anki:734e286f38437868654c-->
?
Par un **`context_schema`** : on passe `context=...` à `invoke`, et ces données sont accessibles dans les middlewares et les outils via le **runtime**, sans être mises dans les messages vus par le modèle.

L'application construit ce contexte à partir d'une identité authentifiée. Un outil peut ainsi filtrer une requête par tenant sans demander au LLM de choisir le tenant. Ne pas recopier ces valeurs dans une sortie d'outil non nécessaire, et appliquer les contrôles d'accès côté service : être invisible dans le prompt ne suffit pas à sécuriser une donnée.

---

Qu'est-ce que Deep Agents ? <!--anki:7670636152256a7e7468-->
?
Une surcouche « **batteries included** » bâtie sur les agents LangChain : **planification** (todo list), **système de fichiers virtuel**, **sous-agents** et **compression automatique du contexte**, pour les tâches longues.

Cette surcouche réduit l'assemblage initial pour une tâche qui planifie, lit et produit des artefacts. Vérifier quel backend stocke les fichiers et quelle isolation entoure les outils de code. Les sous-agents et la compression ajoutent des comportements à évaluer, notamment pertes d'information, consommation de tokens et propagation des permissions.

---

Quand descendre de `create_agent` vers LangGraph ? <!--anki:6c6473235e656b6e5743-->
?
Quand le flux doit être **explicite** : étapes déterministes mêlées à des étapes agentiques, branches et boucles sur mesure, plusieurs agents coordonnés — c'est le domaine de [[44-langgraph-fondamentaux|LangGraph]].

Exemple : récupérer des documents, demander une approbation, exécuter un traitement puis vérifier son résultat selon des branches prédéfinies. Un graphe rend les transitions et l'état inspectables. Garder `create_agent` dans les nœuds où une boucle autonome est utile ; il n'est pas nécessaire de réimplémenter chaque appel de modèle.

---

## Mises en situation

Mise en situation : ton agent LangChain doit demander une validation avant tout envoi d'e-mail, plafonner ses appels au modèle et résumer l'historique quand il s'allonge. Comment l'implémentes-tu ? <!--anki:51313d393b6e7032624a-->
?
1. **Ne pas réécrire la boucle** : ces besoins sont des **middlewares**, insérés dans l'agent existant
2. **HumanInTheLoopMiddleware** pour interrompre avant `send_email`, avec reprise par `Command(resume=...)`
3. **ModelCallLimitMiddleware** et **ToolCallLimitMiddleware** pour plafonner coût et boucles
4. **SummarizationMiddleware** pour la compaction près de la limite ([[35-context-engineering|context engineering]])
5. **Checkpointer** obligatoire : sans persistance, une interruption perd l'état de l'agent

**Piège** : mettre « demande toujours confirmation » dans le system prompt et croire que c'est un contrôle.

---

Mise en situation : tes outils ont besoin de l'identifiant du client et de son niveau d'abonnement, mais tu ne veux pas que le modèle puisse les modifier. Comment fais-tu ? <!--anki:63347e7a64404f595956-->
?
1. **Ne pas les mettre dans les messages** : tout ce que le modèle voit, il peut le reformuler ou l'inventer
2. **`context_schema`** : passer ces données via `context=...` à l'invocation
3. **Les lire dans le runtime**, côté outils et middlewares, au moment de l'exécution
4. **Vérifier les droits côté outil** à partir de ce contexte, jamais à partir d'un argument fourni par le modèle ([[103-defenses-agents|défenses]])
5. **Tracer** l'identité réelle utilisée pour chaque appel ([[93-monitoring-inference|traces]])

**Piège** : passer le `tenant_id` en paramètre d'outil. Une injection suffirait alors à changer de client.

---

## Sources

- [LangChain — middlewares personnalisés et routage](https://docs.langchain.com/oss/python/langchain/middleware/custom)

- [LangChain — agents et middleware](https://docs.langchain.com/oss/python/langchain/agents)

## Connexions
- [[42-langchain-fondamentaux|LangChain — Fondamentaux]] — modèles, outils, messages
- [[44-langgraph-fondamentaux|LangGraph — Fondamentaux]] — le runtime sous-jacent
- [[45-langgraph-production|LangGraph — Production]] — persistance et interrupts
- [[34-harness-plugins|Harness & plugins]] — le middleware comme hook de harness
- [[35-context-engineering|Context engineering]] — résumé et édition du contexte
- [[36-orchestration-agents|Orchestration multi-agents]] — sous-agents, handoffs et A2A
- [[00-moc-ai-engineering|MOC AI Engineering]]
