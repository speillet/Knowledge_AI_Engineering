# LangGraph — Production (persistance, HITL, multi-agents) — Flashcards
Tags: #flashcards #ai-engineering #agents #langgraph #llm
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.
<!-- summary: checkpointers, threads, `interrupt` et `Command(resume=...)`, time travel, Store long terme, durable execution, streaming, subgraphs, patterns multi-agents, déploiement. -->

Qu'est-ce qu'un checkpointer ?
?
<!--anki:73715178653d54644d38-->
Le composant qui **sauvegarde l'état du graphe après chaque super-step**. Il apporte la mémoire de conversation, la reprise après erreur, le human-in-the-loop et le time travel.

```python
graph = builder.compile(checkpointer=checkpointer)
```

---

Quels checkpointers existent ?
?
<!--anki:4a23792655613437387d-->
- **`InMemorySaver`** : en mémoire, perdu au redémarrage (tests)
- **`SqliteSaver`** : fichier local (développement)
- **`PostgresSaver`** / `AsyncPostgresSaver` : **production**

---

Qu'est-ce qu'un thread ?
?
<!--anki:65266e7a71676c416a5b-->
Une **suite de checkpoints** identifiée par un **`thread_id`**, passé dans la config (`{"configurable": {"thread_id": "..."}}`). Même `thread_id` = on reprend l'état ; nouveau `thread_id` = on repart de zéro.

---

Comment mettre un humain dans la boucle ?
?
<!--anki:4e2d79524e626742322d-->
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
<!--anki:52647e3824313c325d47-->
Parce que la reprise peut arriver **des minutes ou des jours plus tard**, dans un autre processus : l'état doit être **persisté** pour que le graphe reparte exactement du point d'arrêt.

---

Qu'est-ce que le time travel ?
?
<!--anki:43524756212128393c4d-->
Parcourir l'**historique des checkpoints** d'un thread (`get_state_history`), **rejouer** depuis un checkpoint passé ou le **modifier** (`update_state`) pour explorer une autre branche — très utile pour déboguer un agent.

---

Checkpointer ou Store : quelle différence ?
?
<!--anki:4b5042685f574b50716d-->
- **Checkpointer** : mémoire **court terme**, propre à **un thread**
- **Store** (ex. `InMemoryStore`) : mémoire **long terme, partagée entre threads**, organisée en **namespaces** (ex. `("user-123", "preferences")`), avec recherche sémantique possible

---

Qu'est-ce que la durable execution ?
?
<!--anki:6e5a3837745771543752-->
La capacité d'un workflow à **reprendre après une panne** ou une longue pause **depuis le dernier checkpoint**, sans refaire le travail déjà fait. Les **effets de bord** (appels d'API, écritures) doivent être isolés dans des tâches pour ne pas être rejoués.

---

Que peut-on streamer depuis un graphe ?
?
<!--anki:445e71583c4f4f626c26-->
L'**état complet** après chaque étape (`values`), les **mises à jour** de chaque nœud (`updates`), les **tokens** du LLM (`messages`) ou des **événements personnalisés** (`custom`). Les versions récentes ajoutent aussi `stream_events(..., version="v3")`.

---

Qu'est-ce qu'un subgraph ?
?
<!--anki:447762797072732f477e-->
Un **graphe compilé utilisé comme nœud** d'un autre graphe. On découpe ainsi un système complexe en modules, souvent **un subgraph par agent**.

---

Quels patterns multi-agents LangChain/LangGraph documentent-ils ?
?
<!--anki:78287e6656626f715b77-->
- **Subagents** : un agent principal appelle des sous-agents **comme des outils**
- **Handoffs** : un agent **passe la main** à un autre via un appel d'outil
- **Router** : une étape classe la requête et l'envoie au bon agent
- **Skills** : un seul agent charge du contexte spécialisé à la demande
- **Custom workflow** : un graphe sur mesure qui combine les précédents

---

Comment déployer et déboguer un graphe LangGraph ?
?
<!--anki:6c6747322662447d7252-->
- **LangSmith Deployment** (ex-LangGraph Platform) : un **Agent Server** qui expose le graphe en API, avec persistance, files de tâches et streaming gérés
- **Studio** : IDE visuel pour exécuter pas à pas et inspecter l'état
- **Auto-hébergé** : le graphe dans son propre service (FastAPI, conteneur) avec un `PostgresSaver`

---

## Mises en situation

Mise en situation : ton agent de traitement de commandes s'arrête pour une validation humaine qui arrive parfois deux jours plus tard. Il tourne aujourd'hui avec `InMemorySaver`. Que changes-tu ?
?
<!--anki:4d2f6936553058693334-->
1. **Checkpointer persistant** : `PostgresSaver` en production, sinon un redémarrage perd tous les dossiers en attente
2. **Thread par dossier** : `thread_id` stable, pour reprendre exactement au point d'arrêt
3. **Reprise** par `Command(resume=...)` avec la décision, depuis un autre processus que celui qui a interrompu
4. **Délais et relances** : un dossier en attente depuis trop longtemps doit alerter ou expirer
5. **Effets de bord isolés** : les écritures et envois ne doivent pas être rejoués après une reprise

**Piège** : garder les interruptions en mémoire et perdre les validations en cours au premier déploiement.

---

Mise en situation : un agent a produit une réponse aberrante hier à 14 h, et l'utilisateur veut comprendre pourquoi. Comment enquêtes-tu ?
?
<!--anki:432a625f5e245f5a3577-->
1. **Retrouver le thread** à partir de l'identifiant de conversation, puis son historique de checkpoints
2. **Time travel** : rejouer depuis le checkpoint qui précède l'erreur pour voir l'état exact d'alors
3. **Isoler l'étape fautive** : outil qui a renvoyé une donnée fausse, routage inattendu, contexte tronqué
4. **Tester une correction** en modifiant l'état à ce point (`update_state`) et en rejouant
5. **Fixer le cas** en test de non-régression, puis corriger le code ou le prompt ([[112-cicd-modeles|CI/CD]])

**Piège** : rejouer la requête aujourd'hui, avec un autre contexte et une autre version du modèle, et conclure que le problème n'existe pas.

---

Mise en situation : ton système à quatre agents devient impossible à déboguer, chaque agent ayant ses propres outils et son état. Comment le restructures-tu ?
?
<!--anki:4b4347547d6645526b3f-->
1. **Un subgraph par agent** : chacun devient un module compilé, testable seul
2. **Choisir un pattern explicite** : router en entrée, handoffs entre pairs, ou sous-agents appelés comme outils ([[36-orchestration-agents|orchestration]])
3. **État partagé minimal** : ce qui circule entre agents est structuré et limité, le reste reste local
4. **Streaming des mises à jour** par nœud, pour voir qui fait quoi en direct
5. **Se demander si quatre agents sont nécessaires** : souvent deux suffisent, avec du code entre eux

**Piège** : un état global où chaque agent écrit ce qu'il veut, et que plus personne ne comprend.

---

## Sources

- [LangGraph — persistance et threads](https://docs.langchain.com/oss/python/langgraph/persistence)

## Connexions
- [[44-langgraph-fondamentaux|LangGraph — Fondamentaux]] — state, nodes, edges
- [[43-langchain-agents|LangChain — Agents]] — HITL et mémoire via middleware
- [[36-orchestration-agents|Orchestration multi-agents]] — les patterns
- [[35-context-engineering|Context engineering]] — mémoire court et long terme
- [[41-automatisation-code-nocode|Automatisation]] — durable execution (Temporal)
- [[91-langfuse-observabilite|Langfuse]] — tracer les exécutions
- [[39-memoire-agents|Mémoire des agents]] — types de mémoire, écriture et rappel
- [[38-plateformes-agents|Plateformes d'agents]] — runtimes managés, double texting
- [[115-plateformes-agents-gouvernance|Plateformes d'agents — gouvernance]] — identité, politiques, audit et coûts d'une flotte d'agents
- [[142-fiabilite-resilience-llm|Fiabilité & résilience]] — timeouts, retries, fallbacks et dégradation
- [[00-moc-ai-engineering|MOC AI Engineering]]
