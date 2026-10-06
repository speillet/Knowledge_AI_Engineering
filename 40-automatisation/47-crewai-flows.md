# CrewAI — Flows — Flashcards
Tags: #flashcards #ai-engineering #agents #crewai #workflow #llm
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.
<!-- summary: `@start`, `@listen`, `@router`, état structuré, `@persist`, `@human_feedback`, mémoire, CLI, crew ou flow, Flows ou LangGraph. -->


Qu'est-ce qu'un Flow CrewAI ? <!--anki:48705b4d433b4b7c7339-->
?
Un **workflow événementiel** écrit en Python : des méthodes décorées qui se déclenchent les unes après les autres, avec un **état partagé**. Un Flow peut appeler du code, un simple appel LLM, un agent ou une **crew** entière.

---

Pourquoi CrewAI recommande-t-il les Flows pour la production ? <!--anki:493f4033257a2c434034-->
?
Parce qu'ils donnent un **contrôle déterministe** du déroulé (étapes, conditions, état) tout en gardant l'autonomie des [[46-crewai-crews|crews]] là où elle est utile — le principe « [[41-automatisation-code-nocode|workflow]] d'abord, agent quand nécessaire ».

Les événements et conditions rendent les chemins d'exécution visibles, mais la sortie d'une crew reste probabiliste. Mettre une validation entre cette sortie et une action métier, par exemple avant d'enregistrer une commande. Prévoir aussi reprise, idempotence et supervision : un graphe d'étapes explicite ne suffit pas à garantir la fiabilité.

---

Quels décorateurs structurent un Flow CrewAI ? <!--anki:7a2571382c507c776739-->
?
- **`@start()`** : point d'entrée (plusieurs possibles, lancés en parallèle)
- **`@listen(methode)`** : s'exécute quand `methode` se termine, et reçoit sa sortie
- **`@router(methode)`** : renvoie un **label** qui choisit la branche suivante
- **`or_()` / `and_()`** : écouter la fin de **l'une** ou de **toutes** les méthodes

---

Comment écrire un Flow CrewAI qui route un ticket vers une branche de traitement ? <!--anki:6543357a5b677a2565-->
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

`@start` lance la classification ; `@router` émet une étiquette ; `@listen` exécute le traitement correspondant. `classifier` et `crew_support` sont des dépendances à définir. Cet extrait illustre uniquement la branche technique : ajouter un listener commercial et une gestion des catégories inconnues pour couvrir tous les chemins d'un vrai service.

---

Dans un Flow CrewAI, état structuré ou non structuré ? <!--anki:7a3c687e3b4823246c6c-->
?
- **Non structuré** : `self.state` est un dict libre — rapide pour prototyper
- **Structuré** : un modèle **Pydantic** (`Flow[MonEtat]`) — typé et validé, recommandé en production
Dans les deux cas, l'état reçoit un **`id`** unique.

---

Comment rendre un Flow reprenable après un arrêt ? <!--anki:747a77217a394a3b7c6c-->
?
Avec le décorateur **`@persist`** (sur la classe ou sur des méthodes) : l'état est sauvegardé (SQLite par défaut) et le Flow peut **reprendre** avec le même `id` d'état, ou **repartir d'un instantané** avec un nouvel `id`.

---

Comment intégrer une validation humaine dans un Flow CrewAI ? <!--anki:736663553e494c2a4138-->
?
Avec le décorateur **`@human_feedback`** (CrewAI 1.8+) : le Flow **se met en pause** pour demander l'avis d'un humain, et la réponse peut **router** vers différentes branches (approuvé, à corriger…).

Présenter le résultat à valider, les conséquences et les options de refus ou correction. Le mécanisme d'attente et de reprise dépend de l'intégration utilisée ; vérifier sa persistance sur redémarrage. Une approbation doit porter sur l'action et les arguments effectifs, sans autoriser implicitement toutes les actions suivantes.

---

Comment un Flow CrewAI utilise-t-il la mémoire ? <!--anki:4836683e74747c21725f-->
?
Via la mémoire unifiée : `self.remember(...)` pour stocker, `self.recall(...)` pour retrouver, `self.extract_memories(...)` pour découper un texte en faits — ce qui permet d'**accumuler des connaissances d'une exécution à l'autre**.

Séparer les faits durables des observations temporaires : une préférence stable peut être mémorisée, une erreur d'outil ne doit pas devenir une vérité. Définir stockage, portée utilisateur, rétention et effacement. Lors d'un rappel, vérifier la provenance et la date, car une mémoire ancienne peut contredire une instruction ou une source plus récente.

---

Comment créer et lancer un projet Flow CrewAI ? <!--anki:6a725b613d5b23617567-->
?
```bash
crewai create flow mon_flow
cd mon_flow
crewai install
crewai run
```
Le projet généré contient le Flow et un dossier `crews/` pour les crews qu'il orchestre.

Le générateur fournit une structure de projet, pas un workflow métier achevé. Configurer les modèles et leurs identifiants, implémenter les étapes, puis tester les branches et les erreurs avant lancement. Épingler les dépendances et garder les secrets hors du dépôt pour rendre l'installation reproductible et partageable.

---

Crew ou Flow : quand utiliser quoi ? <!--anki:44575b3c377b7a313348-->
?
- **Crew** : une tâche **ouverte** où plusieurs rôles doivent collaborer de façon autonome (recherche, rédaction)
- **Flow** : un **processus métier** avec des étapes, des conditions et un état — qui appelle des crews pour les parties ouvertes

---

Flows CrewAI ou LangGraph ? <!--anki:632943237e5a313c346d-->
?
Les deux orchestrent des étapes avec état. **Flows** : méthodes Python décorées, très lisibles, intégrées aux crews. **[[45-langgraph-production|LangGraph]]** : graphe explicite plus bas niveau, avec un écosystème plus riche de checkpointers, time travel et outils de déploiement.

---

## Mises en situation

Mise en situation : tu dois automatiser le traitement des réclamations : classer, enquêter, proposer un geste commercial, puis faire valider au-delà de 100 €. Comment structures-tu le Flow ? <!--anki:717a535a5a6058473b4e-->
?
1. **`@start`** : réception et classification de la réclamation, avec un **état Pydantic** typé
2. **`@router`** : aiguiller selon la catégorie, les cas simples passant par du code sans LLM
3. **Crew** pour la seule partie ouverte : l'enquête, qui croise historique client et incidents
4. **`@human_feedback`** au-delà du seuil, avec routage selon la décision (approuvé, à corriger)
5. **`@persist`** pour reprendre après une coupure ou une attente longue

**Piège** : confier tout le processus à une crew autonome, alors que trois étapes sur quatre sont déterministes.

---

Mise en situation : ton Flow tourne depuis un mois, mais après chaque redéploiement les dossiers en cours repartent de zéro. Que vérifies-tu ? <!--anki:786e644b48736e4d7739-->
?
1. **`@persist`** : sans lui, l'état ne survit pas au processus
2. **Identifiant d'état** : reprendre avec le même `id` de dossier, et non en créer un nouveau
3. **Stockage** : le SQLite par défaut convient-il à la production, ou faut-il un stockage partagé entre réplicas ?
4. **Idempotence** : les étapes déjà exécutées (e-mail, geste commercial) ne doivent pas être rejouées
5. **Observabilité** : savoir à tout moment combien de dossiers sont en attente et à quelle étape ([[93-monitoring-inference|monitoring]])

**Piège** : tester la reprise uniquement en local, là où le fichier d'état existe toujours.

---

## Sources

- [CrewAI — flows](https://docs.crewai.com/en/concepts/flows)

- [CrewAI — Flows, documentation v1.15.23](https://docs.crewai.com/v1.15.23/en/concepts/flows)

## Connexions
- [[46-crewai-crews|CrewAI — Crews]] — les équipes d'agents orchestrées par le Flow
- [[41-automatisation-code-nocode|Automatisation]] — workflow vs agent
- [[44-langgraph-fondamentaux|LangGraph]] — l'alternative en graphe
- [[36-orchestration-agents|Orchestration multi-agents]] — patterns de composition
- [[31-agents-fondamentaux|Agents]] — human-in-the-loop
- [[00-moc-ai-engineering|MOC AI Engineering]]
