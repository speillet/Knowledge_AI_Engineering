# CrewAI — Flows — Flashcards
Tags: #flashcards #ai-engineering #agents #crewai #workflow #llm

Qu'est-ce qu'un Flow CrewAI ?
?
Un **workflow événementiel** écrit en Python : des méthodes décorées qui se déclenchent les unes après les autres, avec un **état partagé**. Un Flow peut appeler du code, un simple appel LLM, un agent ou une **crew** entière.

---

Pourquoi CrewAI recommande-t-il les Flows pour la production ?
?
Parce qu'ils donnent un **contrôle déterministe** du déroulé (étapes, conditions, état) tout en gardant l'autonomie des [[46-crewai-crews|crews]] là où elle est utile — le principe « [[41-automatisation-code-nocode|workflow]] d'abord, agent quand nécessaire ».

---

Quels décorateurs structurent un Flow ?
?
- **`@start()`** : point d'entrée (plusieurs possibles, lancés en parallèle)
- **`@listen(methode)`** : s'exécute quand `methode` se termine, et reçoit sa sortie
- **`@router(methode)`** : renvoie un **label** qui choisit la branche suivante
- **`or_()` / `and_()`** : écouter la fin de **l'une** ou de **toutes** les méthodes

---

À quoi ressemble un Flow avec routage ?
?
```python
from crewai.flow.flow import Flow, listen, router, start
from pydantic import BaseModel

class TicketState(BaseModel):
    message: str = ""
    categorie: str = ""

class SupportFlow(Flow[TicketState]):
    @start()
    def classer(self):
        self.state.categorie = classifier(self.state.message)

    @router(classer)
    def aiguiller(self):
        return "technique" if self.state.categorie == "bug" else "commercial"

    @listen("technique")
    def traiter_bug(self):
        return crew_support.kickoff(inputs={"message": self.state.message})

SupportFlow().kickoff(inputs={"message": "L'export PDF plante"})
```

---

État structuré ou non structuré ?
?
- **Non structuré** : `self.state` est un dict libre — rapide pour prototyper
- **Structuré** : un modèle **Pydantic** (`Flow[MonEtat]`) — typé et validé, recommandé en production
Dans les deux cas, l'état reçoit un **`id`** unique.

---

Comment rendre un Flow reprenable après un arrêt ?
?
Avec le décorateur **`@persist`** (sur la classe ou sur des méthodes) : l'état est sauvegardé (SQLite par défaut) et le Flow peut **reprendre** avec le même `id` d'état, ou **repartir d'un instantané** avec un nouvel `id`.

---

Comment intégrer une validation humaine dans un Flow ?
?
Avec le décorateur **`@human_feedback`** (CrewAI 1.8+) : le Flow **se met en pause** pour demander l'avis d'un humain, et la réponse peut **router** vers différentes branches (approuvé, à corriger…).

---

Comment un Flow utilise-t-il la mémoire ?
?
Via la mémoire unifiée : `self.remember(...)` pour stocker, `self.recall(...)` pour retrouver, `self.extract_memories(...)` pour découper un texte en faits — ce qui permet d'**accumuler des connaissances d'une exécution à l'autre**.

---

Comment créer et lancer un projet Flow ?
?
```bash
crewai create flow mon_flow
cd mon_flow
crewai install
crewai run
```
Le projet généré contient le Flow et un dossier `crews/` pour les crews qu'il orchestre.

---

Crew ou Flow : quand utiliser quoi ?
?
- **Crew** : une tâche **ouverte** où plusieurs rôles doivent collaborer de façon autonome (recherche, rédaction)
- **Flow** : un **processus métier** avec des étapes, des conditions et un état — qui appelle des crews pour les parties ouvertes

---

Flows CrewAI ou LangGraph ?
?
Les deux orchestrent des étapes avec état. **Flows** : méthodes Python décorées, très lisibles, intégrées aux crews. **[[45-langgraph-production|LangGraph]]** : graphe explicite plus bas niveau, avec un écosystème plus riche de checkpointers, time travel et outils de déploiement.

---

## Connexions
- [[46-crewai-crews|CrewAI — Crews]] — les équipes d'agents orchestrées par le Flow
- [[41-automatisation-code-nocode|Automatisation]] — workflow vs agent
- [[44-langgraph-fondamentaux|LangGraph]] — l'alternative en graphe
- [[36-orchestration-agents|Orchestration multi-agents]] — patterns de composition
- [[31-agents-fondamentaux|Agents]] — human-in-the-loop
- [[00-moc-ai-engineering|MOC AI Engineering]]
