# Mémoire des agents — Flashcards
Tags: #flashcards #ai-engineering #agents #memoire #llm

Pourquoi un agent a-t-il besoin d'une mémoire externe ?
?
Un LLM est **sans état** : il ne sait que ce qui est dans sa fenêtre de contexte, limitée et coûteuse. Pour retenir d'une session à l'autre (préférences, faits, leçons tirées d'erreurs), on **écrit hors du contexte** puis on **réinjecte sélectivement** ce qui sert à la tâche en cours ([[35-context-engineering|context engineering]]).

---

Quels types de mémoire distingue-t-on ?
?
- **De travail** : le contexte de la tâche en cours
- **Sémantique** : des **faits** (« l'utilisateur est végétarien »)
- **Épisodique** : des **expériences** passées (« la dernière fois, ce déploiement a échoué à cause du quota »)
- **Procédurale** : du **savoir-faire** (instructions, skills, prompt système mis à jour)

---

Mémoire de thread ou mémoire long terme ?
?
- **Thread** : l'historique d'**une** conversation, rechargé à chaque tour (ex. [[45-langgraph-production|checkpointer]] LangGraph)
- **Long terme** : partagée **entre conversations**, rangée par **namespace** (utilisateur, équipe, organisation) et retrouvée par recherche (ex. Store LangGraph)

---

Quand écrire en mémoire : pendant la conversation ou en arrière-plan ?
?
- **Pendant** (hot path) : l'agent appelle un outil « enregistrer un souvenir ». Disponible tout de suite, mais ajoute de la latence et détourne l'agent de sa tâche.
- **En arrière-plan** : un processus analyse la conversation **après coup** et en extrait les souvenirs. Aucune latence, mais un délai et moins de contrôle en direct.

---

Comment extraire et consolider les souvenirs ?
?
Un LLM extrait des **faits candidats**, puis compare chacun aux souvenirs proches déjà stockés et choisit : **ajouter**, **mettre à jour**, **supprimer** ou **ignorer** (les opérations ADD, UPDATE, DELETE, NOOP de Mem0). Sans cette consolidation, la mémoire accumule **doublons et contradictions**.

---

Comment choisir les souvenirs à rappeler ?
?
Par un **score combiné** (popularisé par les Generative Agents, 2023) :
- **Pertinence** : similarité avec la requête
- **Récence** : décroissance avec le temps
- **Importance** : notée à l'écriture

Plus des **filtres** (utilisateur, type de souvenir). Mieux vaut **peu de souvenirs bien choisis** que tout l'historique.

---

Qu'est-ce que la réflexion (reflection) ?
?
L'agent **synthétise périodiquement** ses souvenirs bruts en conclusions de plus haut niveau (« l'utilisateur préfère des réponses courtes avec du code »), ou tire des **leçons** de ses échecs. Il transforme ainsi l'épisodique en sémantique ou en procédural.

---

Comment gérer les faits qui changent dans le temps ?
?
**Invalider plutôt qu'écraser** : chaque fait porte une **fenêtre de validité** (depuis quand, jusqu'à quand) et l'historique est conservé. Les graphes temporels comme Graphiti le font automatiquement. Sans cela, l'agent mélange l'ancienne adresse et la nouvelle, ou perd la trace de ce qui était vrai à une date donnée.

---

Où stocker la mémoire ?
?
- **Base vectorielle** : souvenirs en texte + embeddings, recherche par similarité
- **[[23-knowledge-graphs-ontologies|Knowledge graph]]** : entités et relations, requêtes multi-hop, dimension temporelle
- **Profil structuré** (document clé-valeur) : préférences et attributs d'un utilisateur
- **Fichiers** : `CLAUDE.md`, ou le memory tool d'Anthropic qui lit et écrit dans un répertoire de mémoire

---

Comment fonctionne la mémoire de Letta (ex-MemGPT) ?
?
Une approche inspirée des **systèmes d'exploitation** : des **blocs de mémoire « core »** restent dans le contexte et l'agent les **modifie lui-même** avec des outils ; la mémoire d'**archives** (recherche vectorielle) et de **rappel** (historique) reste hors contexte et y est chargée à la demande, comme une pagination.

---

Quels outils de mémoire existent ?
?
- **Mem0** : couche mémoire (extraction et consolidation)
- **Letta** : agents avec mémoire auto-éditée
- **Zep / Graphiti** : graphe temporel
- **[[24-cognee|Cognee]]** : knowledge graph + ontologie
- **LangMem** pour LangGraph, et les mémoires intégrées aux frameworks ([[46-crewai-crews|CrewAI]], Store LangGraph)
- Côté fournisseur : le **memory tool** d'Anthropic (fichiers)

---

Quels risques pose une mémoire persistante ?
?
- **Empoisonnement** : une [[101-securite-llm-guardrails|injection de prompt]] enregistrée ressurgit à chaque session
- **Fuite entre utilisateurs** si les namespaces sont mal cloisonnés
- **Données personnelles** : RGPD, droit à l'oubli, donc suppression **réelle**
- **Souvenirs faux ou périmés**

Parades : valider ce qu'on écrit, TTL, et une interface pour **voir et effacer** ses souvenirs.

---

Comment évaluer la mémoire d'un agent ?
?
Des benchmarks de conversations longues (**LoCoMo**, **LongMemEval**) et des tests métiers :
- Rappeler un fait donné **plusieurs sessions** plus tôt
- Prendre en compte un fait **qui a changé**
- **S'abstenir** quand l'information n'a jamais été donnée

Mesurer aussi la **latence** et le **coût** ajoutés par l'écriture et la recherche.

---

## Connexions
- [[35-context-engineering|Context engineering]] — la mémoire comme composante du contexte
- [[45-langgraph-production|LangGraph en production]] — checkpointer et Store
- [[46-crewai-crews|CrewAI]] — mémoire unifiée
- [[23-knowledge-graphs-ontologies|Knowledge graphs & ontologies]] — la mémoire en graphe
- [[24-cognee|Cognee]] — une plateforme de mémoire en graphe
- [[34-harness-plugins|Harness & plugins]] — fichiers mémoire
- [[101-securite-llm-guardrails|Sécurité LLM]] — empoisonnement de la mémoire
- [[00-moc-ai-engineering|MOC AI Engineering]]
