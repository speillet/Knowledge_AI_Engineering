# Patterns de workflows agentiques — Flashcards
Tags: #flashcards #ai-engineering #agents #workflows #patterns #llm
<!-- summary: prompt chaining, routing, parallélisation (sectioning, voting), evaluator-optimizer, plan-and-execute ou ReAct, Reflexion, calcul de fiabilité d'une chaîne, workflow ou agent, implémentation sans framework, conservation du meilleur candidat admissible, vote corrélé, arrêt des améliorations. -->


Quels sont les patterns de base pour composer des appels LLM ? <!--anki:794e6f356a4c61743f5b-->
?
La taxonomie popularisée par Anthropic (« Building effective agents », 2024), du plus simple au plus autonome :
1. **Prompt chaining** : une suite d'étapes fixes
2. **Routing** : un aiguillage vers une branche spécialisée
3. **Parallélisation** : plusieurs appels simultanés, puis agrégation
4. **Orchestrator-workers** : un LLM découpe dynamiquement et délègue ([[36-orchestration-agents|orchestration]])
5. **Evaluator-optimizer** : un appel produit, un autre critique, on itère

Au-delà, l'**agent** choisit lui-même ses étapes ([[31-agents-fondamentaux|agents]]).

---

Qu'est-ce que le prompt chaining ? <!--anki:63754e5a7b244d33377b-->
?
Découper une tâche en **étapes fixes**, chacune alimentant la suivante : extraire → traduire → résumer. Une **gate** en code peut bloquer une sortie invalide avant propagation ([[11-prompt-engineering-avance|décomposition]]).

Chaque étape devient plus ciblée et testable, mais la chaîne n'est pas automatiquement plus fiable. Exemple : si chaque étape réussit avec une probabilité de 98 % conditionnellement aux précédentes réussies, trois étapes réussissent ensemble à environ **94,1 %**.

Conserver les références aux données initiales pour repérer les déformations, tester aussi le résultat final et prévoir l'échec d'une gate. Le gain de contrôlabilité se paie en appels et latence.

---

Qu'est-ce que le pattern routing ? <!--anki:433c21753f315e2a483c-->
?
Un premier appel (ou un classifieur) **catégorise** l'entrée et l'envoie vers un **traitement spécialisé** : prompt, outils ou modèle propres à la catégorie. Exemple : remboursement, question technique et réclamation n'ont pas le même prompt.

Il évite un prompt fourre-tout qui dégrade toutes les catégories, et permet d'envoyer les cas simples vers un **petit modèle** ([[82-routing-llm|routing LLM]]).

Prévoir une branche « ambigu ou hors périmètre » : forcer chaque ticket dans une catégorie connue masque les erreurs du routeur. Mesurer la réussite de bout en bout, car un excellent spécialiste ne compense pas une mauvaise orientation.

---

Quelles sont les deux formes de parallélisation des appels LLM dans un workflow ? <!--anki:47335a5b4c435a6f5958-->
?
- **Sectioning** : découper une tâche en **sous-tâches indépendantes** traitées en parallèle. Exemple : un appel répond, un autre vérifie en même temps les garde-fous
- **Voting** : lancer **la même tâche plusieurs fois** et agréger les réponses. Exemple : trois revues de sécurité d'un code, alerte si au moins une trouve un problème

Le premier réduit la **latence**, le second augmente la **fiabilité** ([[65-probabilites-sampling|self-consistency]]).

---

Qu'est-ce que le pattern evaluator-optimizer ? <!--anki:6f513979335932596924-->
?
Une **boucle** : un appel **génère**, un second **évalue** selon des critères explicites et renvoie une critique, le premier **corrige**, jusqu'à validation ou nombre maximal de tours.

Il marche quand deux conditions sont réunies : des **critères d'évaluation clairs**, et une critique qui **améliore réellement** la réponse (traduction, rédaction, code qui doit passer des tests). Sans critère vérifiable, la boucle tourne en rond ([[95-llm-as-judge|juge]]).

---

À ne pas confondre : plan-and-execute et ReAct ? <!--anki:446b3f67597d5a3d334d-->
?
- **ReAct** : le modèle **décide une action à la fois**, observe, puis décide la suivante. Souple, mais chaque étape demande un appel au grand modèle
- **Plan-and-execute** : un planificateur produit d'abord **un plan complet**, que des exécutants (souvent plus petits) suivent, avec **replanification** si une étape échoue

Le second coûte moins cher et se relit avant exécution, mais s'adapte moins vite à l'imprévu ([[31-agents-fondamentaux|ReAct]]).

---

Qu'est-ce que le pattern Reflexion (Shinn et al.) ? <!--anki:43766a393a407a512d26-->
?
Après un **échec** (test raté, réponse jugée fausse), l'agent écrit une **critique en langage naturel** de ce qui a mal tourné, et la garde en mémoire pour la tentative suivante. Proposé par Shinn et al. (2023), il améliore les tâches à **retour vérifiable** : code avec tests, puzzles.

Sans signal d'échec fiable, le modèle « réfléchit » sur des erreurs imaginaires ([[39-memoire-agents|mémoire]]).

---

Calcul : quelle probabilité de réussite d’une chaîne de 10 étapes toutes nécessaires, chacune réussissant avec probabilité 0,95, sous indépendance et sans rattrapage ? <!--anki:51284f54214b6a7a7c36-->
?
Si les échecs sont indépendants et non rattrapés :
```text
0,95^10 ≈ 0,60   → 40 % des tâches échouent quelque part
0,99^10 ≈ 0,90
0,95^20 ≈ 0,36
```
D'où trois leviers : **moins d'étapes**, des **portes de vérification** qui rattrapent les erreurs, et des étapes plus fiables. C'est aussi pourquoi les agents longs sont difficiles à fiabiliser ([[114-reproductibilite-variance|pass^k]]).

Les étapes réelles peuvent partager une cause d'échec, comme un document erroné ; l'indépendance est donc une hypothèse de calcul, pas une propriété des agents. Un retry n'améliore la chaîne que s'il peut corriger l'erreur sans reproduire ses effets indésirables.

---

Comment choisir entre workflow et agent ? <!--anki:6f6678437a726b25366f-->
?
- **Étapes connues à l'avance** : workflow (chaining, routing). Prévisible, testable, moins cher
- **Nombre d'étapes imprévisible**, chemin qui dépend des résultats : agent
- **Erreur coûteuse** : workflow, ou agent avec approbation humaine

Règle d'Anthropic : commencer par **l'option la plus simple** qui marche, et n'ajouter de l'autonomie que si elle **mesure mieux** ([[94-evals-methodologie|evals]]).

Exemple hybride : workflow fixe pour vérifier une facture, agent borné pour retrouver une pièce manquante. L'autonomie porte sur la recherche, pas sur l'autorisation de paiement.

---

Quand ne pas utiliser d'evaluator-optimizer ? <!--anki:70363f3e4a7e4a215d56-->
?
- **Pas de critère vérifiable** : le juge valide ou rejette au hasard, et la boucle ajoute du coût sans gain
- **Latence critique** : chaque tour ajoute une génération et une évaluation sur le chemin critique
- **Première réponse déjà bonne** dans la grande majorité des cas : mieux vaut évaluer seulement les cas douteux
- **Même modèle, même contexte** pour générer et critiquer : il tend à **valider ses propres erreurs**

Mesurer le gain par tour : souvent, le deuxième tour apporte l'essentiel.

---

Comment implémenter chaining, routage et parallélisation LLM sans framework ? <!--anki:4867683c232863727074-->
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

Cet extrait suppose des fonctions déjà définies et un import d'`asyncio`. Les deux appels parallèles doivent être indépendants. Ajouter timeouts, annulation et gestion des exceptions ; `gather` ne constitue pas une politique de reprise. Enregistrer le résultat de chaque étape utile permet de diagnostiquer un échec sans relancer toute la tâche.

---

Quand une boucle evaluator-optimizer doit-elle conserver le meilleur candidat au lieu du dernier ? <!--anki:3064373864333466376237613435653438666364303263616337636134613833-->
?
Une **révision** peut améliorer un critère tout en dégradant une réponse déjà correcte. Le dernier candidat n'est donc pas nécessairement le meilleur.

Conserver chaque proposition avec son score, ses violations et son coût. N'accepter une révision que selon une règle définie : contraintes impératives satisfaites puis amélioration mesurable. Arrêter sur budget, stagnation ou réussite, et conserver le meilleur candidat admissible. Si l'évaluateur est bruité, confirmer les écarts utiles ; multiplier les révisions peut seulement suradapter le texte à son juge.

---

Calcul : trois classifieurs indépendants ont chacun 80 % de probabilité de réponse correcte sur une tâche binaire. Quelle fiabilité pour leur vote majoritaire sans abstention ? <!--anki:3062663931623331356234393437383562663763373630623534653039316233-->
?
La majorité réussit si exactement deux ou les trois réussissent : **3 × 0,8² × 0,2 + 0,8³ = 0,896**, soit **89,6 %**.

Le gain dépend fortement de l'indépendance supposée. Trois appels au même modèle partageant une fausse prémisse peuvent produire la même erreur ; leur vote ne suit alors pas ce calcul. Mesurer les erreurs conjointes et le coût avant de déployer une stratégie de vote.

---

Pourquoi fixer une amélioration minimale dans une boucle evaluator-optimizer ? <!--anki:3534353761626465623131653433613339383738626434636438336364623966-->
?
Sans seuil, la boucle peut poursuivre **des reformulations sans gain utile**, guidées par le bruit du juge. Définir un progrès minimal, un nombre maximal d'essais et une condition d'admissibilité.

Conserver le meilleur candidat admissible selon la grille, puis confirmer les gains sur des cas indépendants. Une hausse minime du score automatique ne justifie pas nécessairement le coût d'un nouvel appel. Une amélioration de style ne doit pas compenser une perte d'exactitude.

---

## Mises en situation

Mise en situation : ton équipe a construit un agent autonome pour traiter les demandes de remboursement. Il réussit 78 % des cas, coûte cher et ses erreurs sont imprévisibles. Or le processus métier a toujours les mêmes quatre étapes. Que proposes-tu ? <!--anki:6c42675b522672606b61-->
?
1. **Constater** que le chemin est connu : l'autonomie de l'agent n'apporte rien ici, elle ajoute de la variance
2. **Réécrire en workflow** : classer la demande, extraire les champs, vérifier l'éligibilité par des règles en code, rédiger la réponse
3. **Ajouter des portes** : champs obligatoires présents, montant cohérent, escalade humaine au-delà d'un seuil
4. **Garder un agent seulement** pour la branche « cas atypique », si elle existe
5. **Comparer** sur le même jeu d'eval : taux de réussite, coût par demande et variance ([[96-evals-rag-agents|evals d'agents]])

**Piège** : ajouter des consignes à l'agent pour qu'il suive les quatre étapes, au lieu de les coder.

---

Mise en situation : un générateur de descriptions produit a 20 % de rejets par l'équipe marketing (ton, longueur, mentions interdites). Tu envisages une boucle evaluator-optimizer. Comment la conçois-tu ? <!--anki:4c313c6c243e38355869-->
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
- [[49-agents-de-code|Agents de code]] — utiliser et intégrer les agents de code
- [[00-moc-ai-engineering|MOC AI Engineering]]
