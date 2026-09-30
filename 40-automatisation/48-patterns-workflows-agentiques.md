# Patterns de workflows agentiques — Flashcards
Tags: #flashcards #ai-engineering #agents #workflows #patterns #llm

Quels sont les patterns de base pour composer des appels LLM ?
?
La taxonomie popularisée par Anthropic (« Building effective agents », 2024), du plus simple au plus autonome :
1. **Prompt chaining** : une suite d'étapes fixes
2. **Routing** : un aiguillage vers une branche spécialisée
3. **Parallélisation** : plusieurs appels simultanés, puis agrégation
4. **Orchestrator-workers** : un LLM découpe dynamiquement et délègue ([[36-orchestration-agents|orchestration]])
5. **Evaluator-optimizer** : un appel produit, un autre critique, on itère

Au-delà, l'**agent** choisit lui-même ses étapes ([[31-agents-fondamentaux|agents]]).

---

Qu'est-ce que le prompt chaining ?
?
Découper une tâche en **étapes fixes**, chacune avec son prompt, la sortie de l'une nourrissant la suivante : extraire → traduire → résumer. Entre deux étapes, une **porte** (gate) en code peut vérifier le résultat : format, longueur, champ obligatoire.

Avantages : chaque étape est **testable** et plus simple, donc plus fiable. Coût : plus d'appels et de latence ([[11-prompt-engineering-avance|décomposition]]).

---

Qu'est-ce que le pattern routing ?
?
Un premier appel (ou un classifieur) **catégorise** l'entrée et l'envoie vers un **traitement spécialisé** : prompt, outils ou modèle propres à la catégorie. Exemple : remboursement, question technique et réclamation n'ont pas le même prompt.

Il évite un prompt fourre-tout qui dégrade toutes les catégories, et permet d'envoyer les cas simples vers un **petit modèle** ([[82-routing-llm|routing LLM]]).

---

Quelles sont les deux formes de parallélisation ?
?
- **Sectioning** : découper une tâche en **sous-tâches indépendantes** traitées en parallèle. Exemple : un appel répond, un autre vérifie en même temps les garde-fous
- **Voting** : lancer **la même tâche plusieurs fois** et agréger les réponses. Exemple : trois revues de sécurité d'un code, alerte si au moins une trouve un problème

Le premier réduit la **latence**, le second augmente la **fiabilité** ([[65-probabilites-sampling|self-consistency]]).

---

Qu'est-ce que le pattern evaluator-optimizer ?
?
Une **boucle** : un appel **génère**, un second **évalue** selon des critères explicites et renvoie une critique, le premier **corrige**, jusqu'à validation ou nombre maximal de tours.

Il marche quand deux conditions sont réunies : des **critères d'évaluation clairs**, et une critique qui **améliore réellement** la réponse (traduction, rédaction, code qui doit passer des tests). Sans critère vérifiable, la boucle tourne en rond ([[95-llm-as-judge|juge]]).

---

À ne pas confondre : plan-and-execute et ReAct ?
?
- **ReAct** : le modèle **décide une action à la fois**, observe, puis décide la suivante. Souple, mais chaque étape demande un appel au grand modèle
- **Plan-and-execute** : un planificateur produit d'abord **un plan complet**, que des exécutants (souvent plus petits) suivent, avec **replanification** si une étape échoue

Le second coûte moins cher et se relit avant exécution, mais s'adapte moins vite à l'imprévu ([[31-agents-fondamentaux|ReAct]]).

---

Qu'est-ce que la réflexion (Reflexion) ?
?
Après un **échec** (test raté, réponse jugée fausse), l'agent écrit une **critique en langage naturel** de ce qui a mal tourné, et la garde en mémoire pour la tentative suivante. Proposé par Shinn et al. (2023), il améliore les tâches à **retour vérifiable** : code avec tests, puzzles.

Sans signal d'échec fiable, le modèle « réfléchit » sur des erreurs imaginaires ([[39-memoire-agents|mémoire]]).

---

Calcul : quelle fiabilité pour une chaîne de 10 étapes réussies chacune à 95 % ?
?
Si les échecs sont indépendants et non rattrapés :
```text
0,95^10 ≈ 0,60   → 40 % des tâches échouent quelque part
0,99^10 ≈ 0,90
0,95^20 ≈ 0,36
```
D'où trois leviers : **moins d'étapes**, des **portes de vérification** qui rattrapent les erreurs, et des étapes plus fiables. C'est aussi pourquoi les agents longs sont difficiles à fiabiliser ([[114-reproductibilite-variance|pass^k]]).

---

Comment choisir entre workflow et agent ?
?
- **Étapes connues à l'avance** : workflow (chaining, routing). Prévisible, testable, moins cher
- **Nombre d'étapes imprévisible**, chemin qui dépend des résultats : agent
- **Erreur coûteuse** : workflow, ou agent avec approbation humaine

Règle d'Anthropic : commencer par **l'option la plus simple** qui marche, et n'ajouter de l'autonomie que si elle **mesure mieux** ([[94-evals-methodologie|evals]]).

---

Quand ne pas utiliser d'evaluator-optimizer ?
?
- **Pas de critère vérifiable** : le juge valide ou rejette au hasard, et la boucle ajoute du coût sans gain
- **Latence critique** : chaque tour double le temps de réponse
- **Première réponse déjà bonne** dans la grande majorité des cas : mieux vaut évaluer seulement les cas douteux
- **Même modèle, même contexte** pour générer et critiquer : il tend à **valider ses propres erreurs**

Mesurer le gain par tour : souvent, le deuxième tour apporte l'essentiel.

---

Comment implémenter ces patterns sans framework ?
?
Ce sont quelques **fonctions** : un appel LLM, du code Python entre les appels, `asyncio.gather` pour paralléliser.
```python
async def repondre(ticket):
    categorie = await classer(ticket)                    # routing
    brouillon, risque = await asyncio.gather(           # parallélisation
        rediger(ticket, categorie), verifier_risque(ticket))
    if risque.eleve:
        return escalader(ticket)                         # porte
    return await relire(brouillon)                       # chaining
```
Un framework devient utile pour la **persistance**, la reprise et la supervision humaine ([[44-langgraph-fondamentaux|LangGraph]]).

---

## Mises en situation

Mise en situation : ton équipe a construit un agent autonome pour traiter les demandes de remboursement. Il réussit 78 % des cas, coûte cher et ses erreurs sont imprévisibles. Or le processus métier a toujours les mêmes quatre étapes. Que proposes-tu ?
?
1. **Constater** que le chemin est connu : l'autonomie de l'agent n'apporte rien ici, elle ajoute de la variance
2. **Réécrire en workflow** : classer la demande, extraire les champs, vérifier l'éligibilité par des règles en code, rédiger la réponse
3. **Ajouter des portes** : champs obligatoires présents, montant cohérent, escalade humaine au-delà d'un seuil
4. **Garder un agent seulement** pour la branche « cas atypique », si elle existe
5. **Comparer** sur le même jeu d'eval : taux de réussite, coût par demande et variance ([[96-evals-rag-agents|evals d'agents]])

**Piège** : ajouter des consignes à l'agent pour qu'il suive les quatre étapes, au lieu de les coder.

---

Mise en situation : un générateur de descriptions produit a 20 % de rejets par l'équipe marketing (ton, longueur, mentions interdites). Tu envisages une boucle evaluator-optimizer. Comment la conçois-tu ?
?
1. **Écrire les critères** du marketing sous forme vérifiable : longueur, mentions interdites (en code), ton (juge)
2. **Vérifier d'abord en code** tout ce qui peut l'être, et réserver le juge au ton ([[95-llm-as-judge|juge]])
3. **Calibrer le juge** sur 100 descriptions déjà acceptées ou rejetées par le marketing
4. **Limiter à 2 ou 3 tours**, et escalader à un humain au-delà
5. **Mesurer** le taux de rejet et le coût par description avant et après

**Piège** : laisser le même prompt générer et s'auto-évaluer, puis s'étonner qu'il valide tout.

---

## Connexions
- [[31-agents-fondamentaux|Agents]] — workflow ou agent, ReAct
- [[36-orchestration-agents|Orchestration multi-agents]] — orchestrator-workers et sous-agents
- [[41-automatisation-code-nocode|Automatisation]] — les mêmes patterns en no-code
- [[44-langgraph-fondamentaux|LangGraph]] — implémenter ces graphes avec persistance
- [[82-routing-llm|Routing LLM]] — le routing côté modèles
- [[95-llm-as-judge|LLM-as-a-judge]] — l'évaluateur de la boucle
- [[98-debogage-agents|Débogage des agents]] — savoir quelle étape échoue
- [[00-moc-ai-engineering|MOC AI Engineering]]
