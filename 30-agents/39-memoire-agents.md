# Mémoire des agents — Flashcards
Tags: #flashcards #ai-engineering #agents #memoire #llm
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.
<!-- summary: mémoire de travail, sémantique, épisodique et procédurale, thread ou long terme, écriture pendant ou après la conversation, consolidation, score de rappel, réflexion, faits qui changent, stockage, Letta, outils, risques, évaluation, mémoire d'agent ou RAG, quand ne pas donner de mémoire long terme. -->


Pourquoi un agent a-t-il besoin d'une mémoire externe ? <!--anki:4771475b312e6378352c-->
?
Un LLM est **sans état** : il ne sait que ce qui est dans sa fenêtre de contexte, limitée et coûteuse. Pour retenir d'une session à l'autre (préférences, faits, leçons tirées d'erreurs), on **écrit hors du contexte** puis on **réinjecte sélectivement** ce qui sert à la tâche en cours ([[35-context-engineering|context engineering]]).

---

Quels types de mémoire distingue-t-on pour un agent ? <!--anki:234b3f24393a6b7661-->
?
- **De travail** : le contexte de la tâche en cours
- **Sémantique** : des **faits** (« l'utilisateur est végétarien »)
- **Épisodique** : des **expériences** passées (« la dernière fois, ce déploiement a échoué à cause du quota »)
- **Procédurale** : du **savoir-faire** (instructions, skills, prompt système mis à jour)

---

Mémoire de thread ou mémoire long terme ? <!--anki:4f61472d505b28496777-->
?
- **Thread** : l'historique d'**une** conversation, rechargé à chaque tour (ex. [[45-langgraph-production|checkpointer]] LangGraph)
- **Long terme** : partagée **entre conversations**, rangée par **namespace** (utilisateur, équipe, organisation) et retrouvée par recherche (ex. Store LangGraph)

L'état de thread permet de reprendre un dossier en cours ; une préférence durable peut être réutilisée dans un nouveau dossier. Un namespace organise les données mais ne constitue pas à lui seul une autorisation. Définir droits de lecture, durée de conservation et effacement, notamment pour éviter qu'une information d'un utilisateur soit rappelée à un autre.

---

Quand écrire en mémoire : pendant la conversation ou en arrière-plan ? <!--anki:514f75377d7373513a29-->
?
- **Pendant** (hot path) : l'agent appelle un outil « enregistrer un souvenir ». Disponible tout de suite, mais ajoute de la latence et détourne l'agent de sa tâche.
- **En arrière-plan** : un processus analyse la conversation **après coup** et en extrait les souvenirs. Aucune latence, mais un délai et moins de contrôle en direct.

---

Comment extraire et consolider les souvenirs ? <!--anki:6f2351266f6a21365b2a-->
?
Un LLM extrait des **faits candidats**, puis compare chacun aux souvenirs proches déjà stockés et choisit : **ajouter**, **mettre à jour**, **supprimer** ou **ignorer** (les opérations ADD, UPDATE, DELETE, NOOP de Mem0). Sans cette consolidation, la mémoire accumule **doublons et contradictions**.

---

Comment choisir les souvenirs à rappeler ? <!--anki:6f7862213e5e592d556b-->
?
Par un **score combiné** (popularisé par les Generative Agents, 2023) :
- **Pertinence** : similarité avec la requête
- **Récence** : décroissance avec le temps
- **Importance** : notée à l'écriture

Plus des **filtres** (utilisateur, type de souvenir). Mieux vaut **peu de souvenirs bien choisis** que tout l'historique.

---

En mémoire d'agent, qu'est-ce que la réflexion (reflection) ? <!--anki:747d5b5b70284a2c677b-->
?
L'agent **synthétise périodiquement** ses souvenirs bruts en conclusions de plus haut niveau (« l'utilisateur préfère des réponses courtes avec du code »), ou tire des **leçons** de ses échecs. Il transforme ainsi l'épisodique en sémantique ou en procédural.

---

Comment gérer les faits qui changent dans le temps ? <!--anki:4e5d6777774e4f2e3b52-->
?
**Invalider plutôt qu'écraser** : chaque fait porte une **fenêtre de validité** (depuis quand, jusqu'à quand) et l'historique est conservé. Les graphes temporels comme Graphiti le font automatiquement. Sans cela, l'agent mélange l'ancienne adresse et la nouvelle, ou perd la trace de ce qui était vrai à une date donnée.

---

Où stocker la mémoire long terme d'un agent ? <!--anki:474e52572d285e445668-->
?
- **Base vectorielle** : souvenirs en texte + embeddings, recherche par similarité
- **[[23-knowledge-graphs-ontologies|Knowledge graph]]** : entités et relations, requêtes multi-hop, dimension temporelle
- **Profil structuré** (document clé-valeur) : préférences et attributs d'un utilisateur
- **Fichiers** : `CLAUDE.md`, ou le memory tool d'Anthropic qui lit et écrit dans un répertoire de mémoire

---

Comment fonctionne la mémoire de Letta (ex-MemGPT) ? <!--anki:65302b6a764f7b402e40-->
?
Une approche inspirée des **systèmes d'exploitation** : des **blocs de mémoire « core »** restent dans le contexte et l'agent les **modifie lui-même** avec des outils ; la mémoire d'**archives** (recherche vectorielle) et de **rappel** (historique) reste hors contexte et y est chargée à la demande, comme une pagination.

---

Quelle bibliothèque de mémoire d'agent pour une couche d'extraction simple, une mémoire auto-éditée, des faits qui changent, un graphe avec ontologie ? <!--anki:3931613663613465373863633435633661313165373434653566323234346263-->
?
- **Couche mémoire** qui extrait et consolide les faits des conversations : **Mem0**
- **Mémoire auto-éditée** par l'agent lui-même : **Letta**
- **Faits qui changent dans le temps** (validité, historique) : **Zep / Graphiti**, un graphe temporel
- **Knowledge graph structuré par une ontologie** : **[[24-cognee|Cognee]]**

---

Quelles mémoires sont intégrées aux frameworks, aux fournisseurs et aux plateformes ? <!--anki:6473553378783f6d733a-->
?
- **Frameworks** : **LangMem** et le **Store** de LangGraph, la mémoire de [[46-crewai-crews|CrewAI]]
- **Fournisseurs de modèles** : le **memory tool** d'Anthropic (fichiers)
- **Plateformes d'agents** : AgentCore Memory, Memory Bank de Google ([[38-plateformes-agents|plateformes]])

Distinguer le stockage brut des mécanismes qui extraient, sélectionnent et mettent à jour les souvenirs. Une intégration prête à l'emploi ne garantit ni pertinence ni confidentialité. Vérifier l'isolation par utilisateur, les opérations d'effacement, la provenance et la gestion des contradictions avant de laisser l'agent écrire automatiquement en mémoire.

---

Quels risques pose une mémoire persistante ? <!--anki:7623374a3f4c6c633932-->
?
- **Empoisonnement** : une [[101-securite-llm-guardrails|injection de prompt]] enregistrée ressurgit à chaque session
- **Fuite entre utilisateurs** si les namespaces sont mal cloisonnés
- **Données personnelles** : RGPD, droit à l'oubli, donc suppression **réelle**
- **Souvenirs faux ou périmés**

Parades : valider ce qu'on écrit, TTL, et une interface pour **voir et effacer** ses souvenirs.

---

Comment évaluer la mémoire d'un agent ? <!--anki:6a323337576173662f2e-->
?
Des benchmarks de conversations longues (**LoCoMo**, **LongMemEval**) et des tests métiers :
- Rappeler un fait donné **plusieurs sessions** plus tôt
- Prendre en compte un fait **qui a changé**
- **S'abstenir** quand l'information n'a jamais été donnée

Mesurer aussi la **latence** et le **coût** ajoutés par l'écriture et la recherche.

---

Quand ne pas donner de mémoire long terme à un agent ? <!--anki:49407272774774375d5d-->
?
- **Tâches ponctuelles** sans continuité (extraction, classification, one-shot)
- **Un profil structuré suffit** : préférences et faits stables vivent mieux dans une table ou un CRM, lus par un outil
- **Données sensibles** : chaque souvenir est une donnée personnelle à justifier, sécuriser et savoir **effacer** ([[154-rgpd-llm|RGPD]])
- **Pas de moyen de l'évaluer ni de la purger** : une mémoire fausse ou empoisonnée persiste et contamine les sessions suivantes ([[102-menaces-agents|menaces]])

La mémoire long terme se justifie par un **gain mesuré**, pas par principe.

---

À ne pas confondre : mémoire d'agent et RAG ? <!--anki:4a74332155403f4b7574-->
?
- **RAG** : recherche dans un **corpus existant** (documentation, base de connaissances), le même pour tous les utilisateurs, alimenté par un pipeline d'ingestion
- **Mémoire d'agent** : des informations **écrites par l'agent lui-même** au fil des interactions (préférences, faits, décisions), souvent **propres à un utilisateur**, qui évoluent et se contredisent

Techniquement, la mémoire utilise souvent un retrieval ; la difficulté propre est **quoi écrire, quand mettre à jour et quoi oublier** ([[21-rag-fondamentaux|RAG]]).

---

## Mises en situation

Mise en situation : les utilisateurs se plaignent que ton assistant « oublie tout » d'une session à l'autre, mais aussi qu'il ressort parfois des informations périmées. Comment conçois-tu sa mémoire ? <!--anki:69632a4d35613b2e6023-->
?
1. **Séparer les niveaux** : historique de thread pour la conversation en cours, mémoire long terme pour les faits durables
2. **Choisir quoi écrire** : préférences et faits stables, pas tout l'historique, avec extraction puis **consolidation** (ajouter, mettre à jour, supprimer)
3. **Gérer le temps** : chaque fait porte une fenêtre de validité, on **invalide** au lieu d'écraser
4. **Rappeler peu, mais bien** : score combinant pertinence, récence et importance, avec filtres par utilisateur
5. **Donner la main à l'utilisateur** : voir et effacer ses souvenirs ([[154-rgpd-llm|RGPD]])

**Piège** : tout mémoriser « au cas où », ce qui produit doublons, contradictions et fuites potentielles.

---

Mise en situation : ton agent partage une mémoire entre tous les utilisateurs d'une même entreprise cliente. Quels garde-fous poses-tu avant la mise en production ? <!--anki:495a2d323c4446493275-->
?
1. **Cloisonnement** : namespace par client et par utilisateur, vérifié à l'écriture comme à la lecture
2. **Contrôle de ce qui entre** : pas de contenu externe brut, pas d'instructions, analyse d'injection à l'écriture ([[103-defenses-agents|défenses]])
3. **Provenance** attachée à chaque souvenir, pour pouvoir purger par source
4. **Rétention** : durée de vie, suppression réelle, traitement des données personnelles
5. **Tests** : rappel d'un fait ancien, prise en compte d'un fait changé, abstention si l'information n'a jamais été donnée

**Piège** : un souvenir écrit par un utilisateur qui remonte dans la session d'un autre.

---

## Sources

- [Letta — agents avec état et mémoire](https://docs.letta.com/v1-sdk/concepts/stateful-agents)
- [LangGraph — persistance et threads](https://docs.langchain.com/oss/python/langgraph/persistence)

## Connexions
- [[35-context-engineering|Context engineering]] — la mémoire comme composante du contexte
- [[45-langgraph-production|LangGraph en production]] — checkpointer et Store
- [[46-crewai-crews|CrewAI]] — mémoire unifiée
- [[23-knowledge-graphs-ontologies|Knowledge graphs & ontologies]] — la mémoire en graphe
- [[24-cognee|Cognee]] — une plateforme de mémoire en graphe
- [[34-harness-plugins|Harness & plugins]] — fichiers mémoire
- [[101-securite-llm-guardrails|Sécurité LLM]] — empoisonnement de la mémoire
- [[38-plateformes-agents|Plateformes d'agents]] — la mémoire managée des plateformes
- [[103-defenses-agents|Sécurité des agents — Architecture défensive]] — protéger la mémoire contre l'empoisonnement
- [[154-rgpd-llm|RGPD appliqué aux LLM]] — effacement et rétention
- [[44-langgraph-fondamentaux|LangGraph]] — graphes d'états pour agents et workflows
- [[00-moc-ai-engineering|MOC AI Engineering]]
