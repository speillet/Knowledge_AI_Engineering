# Modèles de raisonnement & test-time compute — Flashcards
Tags: #flashcards #ai-engineering #fondamentaux #reasoning #llm
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.

Qu'est-ce qu'un modèle de raisonnement ?
?
Un LLM entraîné à **produire une longue réflexion interne** (chaîne de pensée : exploration, vérification, retours en arrière) **avant sa réponse finale**. Il est nettement meilleur en **maths, code, planification et problèmes à plusieurs étapes**, au prix de **plus de tokens et de latence**.

---

Qu'est-ce que le test-time compute ?
?
Dépenser **plus de calcul au moment de l'inférence** pour améliorer la réponse, au lieu (ou en plus) d'un plus gros modèle. Deux formes :
- **séquentielle** : raisonner plus longtemps (plus de tokens de réflexion) ;
- **parallèle** : générer **plusieurs réponses** et choisir (vote majoritaire, vérificateur, best-of-n).

---

Comment entraîne-t-on un modèle à raisonner ?
?
Par **RL avec récompenses vérifiables** (RLVR) : on pose des problèmes dont la réponse est **vérifiable automatiquement** (résultat mathématique, tests unitaires), on récompense les réponses **correctes**, et le modèle apprend **de lui-même** des stratégies (vérifier, reprendre, décomposer). Algorithmes typiques : **PPO**, **GRPO** ([[52-post-training-alignement|post-training]]).

---

Qu'est-ce qu'un budget de réflexion (thinking budget / reasoning effort) ?
?
Un paramètre d'API qui borne ou oriente **la quantité de tokens de raisonnement** (niveau faible/moyen/élevé, ou nombre max de tokens). C'est le **curseur qualité / latence / coût** : un effort élevé pour un problème difficile, faible pour une tâche simple ou interactive.

---

Comment les tokens de raisonnement sont-ils facturés ?
?
Comme des **tokens de sortie**, même s'ils ne sont pas tous visibles (certains fournisseurs n'en renvoient qu'un **résumé**). Une réponse courte peut donc coûter **des milliers de tokens**. À suivre dans les métriques d'usage et dans le calcul du **coût par tâche** ([[121-couts-inference|coûts]]).

---

Quand ne pas utiliser un modèle de raisonnement ?
?
- Tâches **simples** (classification, extraction, reformulation) : aucun gain, coût et latence multipliés.
- Interfaces **temps réel** (voix, autocomplétion) où le TTFT prime.
- Tâches de **style ou de créativité**, où réfléchir plus n'aide pas.

Le [[82-routing-llm|routage]] par difficulté est la réponse naturelle.

---

Faut-il encore écrire « réfléchis étape par étape » ?
?
Pour un modèle de raisonnement, **non** : il raisonne déjà, et imposer une méthode détaillée peut **nuire**. Mieux vaut décrire **clairement l'objectif, les contraintes et le format** de sortie, et laisser le modèle organiser sa réflexion. Le chain-of-thought explicite reste utile pour les modèles **sans raisonnement natif** ([[11-prompt-engineering-avance|prompt engineering]]).

---

Peut-on faire confiance à la chaîne de pensée affichée ?
?
**Pas entièrement.** Des travaux montrent que la réflexion affichée n'est **pas toujours fidèle** au processus réel : le modèle peut utiliser un indice sans le mentionner. Elle est utile pour **déboguer** et **surveiller**, mais ce n'est pas une **explication garantie** ni une preuve de correction.

---

Qu'est-ce que le interleaved thinking dans un agent ?
?
Le modèle **raisonne entre deux appels d'outils** : il analyse le résultat d'un outil avant de décider du suivant. Cela améliore la qualité des **trajectoires d'agent** ; il faut en général **renvoyer les blocs de raisonnement** précédents dans l'historique pour garder la cohérence ([[31-agents-fondamentaux|agents]]).

---

Qu'est-ce que le best-of-n avec vérificateur ?
?
Générer **n réponses** puis choisir la meilleure grâce à un **vérificateur** : tests unitaires (code), vérification formelle, [[95-llm-as-judge|juge]] ou reward model. Le gain dépend surtout de la **qualité du vérificateur** : un vérificateur exécutable (tests) est bien plus fiable qu'un juge LLM.

---

## Mises en situation

Mise en situation : ton équipe passe tout le trafic sur un modèle de raisonnement « puisqu'il est meilleur ». Le coût triple et les utilisateurs trouvent l'assistant lent. Que proposes-tu ?
?
1. **Segmenter** : classification, extraction et reformulation ne tirent aucun bénéfice du raisonnement
2. **Router par difficulté** : raisonnement réservé aux problèmes à plusieurs étapes ([[82-routing-llm|routing]])
3. **Régler l'effort** : le budget de réflexion est un curseur qualité, latence et coût
4. **Mesurer le coût réel** : les tokens de réflexion sont facturés comme des tokens de sortie, même invisibles
5. **Vérifier le gain** par segment, sur tes evals, avant de généraliser ([[94-evals-methodologie|evals]])

**Piège** : comparer les modèles sur les cas difficiles seulement, puis appliquer la conclusion à tout le trafic.

---

Mise en situation : un auditeur veut utiliser la chaîne de pensée affichée par le modèle comme justification des décisions prises par ton système. Qu'en dis-tu ?
?
1. **Avertir** : la réflexion affichée n'est pas toujours fidèle au processus réel du modèle
2. **Ce à quoi elle sert** : déboguer, surveiller, repérer des trajectoires aberrantes
3. **Ce qu'elle ne fournit pas** : une explication garantie ni une preuve de correction
4. **Ce qui fait foi** : les données consultées, les outils appelés, les règles appliquées et les validations ([[115-plateformes-agents-gouvernance|audit]])
5. **Pour les usages sensibles** : décision vérifiable par du code ou validée par un humain ([[144-ux-ia-human-in-the-loop|human-in-the-loop]])

**Piège** : présenter la chaîne de pensée comme une justification opposable, notamment dans un cadre réglementé.

---

## Connexions
- [[52-post-training-alignement|Post-training & alignement]] — RL avec récompenses vérifiables
- [[11-prompt-engineering-avance|Prompt engineering]] — chain-of-thought et self-consistency
- [[82-routing-llm|Routing LLM]] — réserver le raisonnement aux requêtes difficiles
- [[121-couts-inference|Coûts d'inférence]] — tokens de réflexion
- [[64-metriques-slo-inference|Métriques & SLO]] — latence des réponses longues
- [[135-pretraining-scaling-laws|Pré-entraînement & scaling laws]] — du calcul d'entraînement au calcul d'inférence
- [[00-moc-ai-engineering|MOC AI Engineering]]
