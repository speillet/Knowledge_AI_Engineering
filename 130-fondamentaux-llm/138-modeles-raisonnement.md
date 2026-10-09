# Modèles de raisonnement & test-time compute — Flashcards
Tags: #flashcards #ai-engineering #fondamentaux #reasoning #llm
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.
<!-- summary: modèle de raisonnement ou chain-of-thought par prompt, test-time compute, RLVR, budget de réflexion, facturation, quand ne pas les utiliser, prompting, fidélité de la chaîne de pensée, interleaved thinking, best-of-n. -->


Qu'est-ce qu'un modèle de raisonnement ? <!--anki:44457a7a766655556330-->
?
Un LLM entraîné à **produire une longue réflexion interne** (chaîne de pensée : exploration, vérification, retours en arrière) **avant sa réponse finale**. Il est nettement meilleur en **maths, code, planification et problèmes à plusieurs étapes**, au prix de **plus de tokens et de latence**.

---

Qu'est-ce que le test-time compute ? <!--anki:68657a773f6c3b31424f-->
?
Dépenser **plus de calcul au moment de l'inférence** pour améliorer la réponse, au lieu (ou en plus) d'un plus gros modèle. Deux formes :
- **séquentielle** : raisonner plus longtemps (plus de tokens de réflexion) ;
- **parallèle** : générer **plusieurs réponses** et choisir (vote majoritaire, vérificateur, best-of-n).

---

Comment entraîne-t-on un modèle à raisonner ? <!--anki:452d33327c713c6e6424-->
?
Par **RL avec récompenses vérifiables** (RLVR) : on pose des problèmes dont la réponse est **vérifiable automatiquement** (résultat mathématique, tests unitaires), on récompense les réponses **correctes**, et le modèle apprend **de lui-même** des stratégies (vérifier, reprendre, décomposer). Algorithmes typiques : **PPO**, **GRPO** ([[52-post-training-alignement|post-training]]).

---

Qu'est-ce qu'un budget de réflexion (thinking budget / reasoning effort) ? <!--anki:765438515a4753303f29-->
?
Un paramètre d'API qui borne ou oriente **la quantité de tokens de raisonnement** (niveau faible/moyen/élevé, ou nombre max de tokens). C'est le **curseur qualité / latence / coût** : un effort élevé pour un problème difficile, faible pour une tâche simple ou interactive.

---

Comment les tokens de raisonnement sont-ils facturés ? <!--anki:75577c53737b3a2f4b71-->
?
Comme des **tokens de sortie**, même s'ils ne sont pas tous visibles (certains fournisseurs n'en renvoient qu'un **résumé**). Une réponse courte peut donc coûter **des milliers de tokens**. À suivre dans les métriques d'usage et dans le calcul du **coût par tâche** ([[121-couts-inference|coûts]]).

---

Quand ne pas utiliser un modèle de raisonnement ? <!--anki:51502558695d4271762f-->
?
- Tâches **simples** (classification, extraction, reformulation) : aucun gain, coût et latence multipliés.
- Interfaces **temps réel** (voix, autocomplétion) où le TTFT prime.
- Tâches de **style ou de créativité**, où réfléchir plus n'aide pas.

Le [[82-routing-llm|routage]] par difficulté est la réponse naturelle.

---

Faut-il encore écrire « réfléchis étape par étape » ? <!--anki:4c503b7432776c5b584d-->
?
Pour un modèle de raisonnement, **non** : il raisonne déjà, et imposer une méthode détaillée peut **nuire**. Mieux vaut décrire **clairement l'objectif, les contraintes et le format** de sortie, et laisser le modèle organiser sa réflexion. Le chain-of-thought explicite reste utile pour les modèles **sans raisonnement natif** ([[11-prompt-engineering-avance|prompt engineering]]).

---

Peut-on faire confiance à la chaîne de pensée affichée ? <!--anki:4339773d41252f6d6749-->
?
**Pas entièrement.** Des travaux montrent que la réflexion affichée n'est **pas toujours fidèle** au processus réel : le modèle peut utiliser un indice sans le mentionner. Elle est utile pour **déboguer** et **surveiller**, mais ce n'est pas une **explication garantie** ni une preuve de correction.

---

Qu'est-ce que le interleaved thinking dans un agent ? <!--anki:482670287673403f334a-->
?
Le modèle **raisonne entre deux appels d'outils** : il analyse le résultat d'un outil avant de décider du suivant. Cela améliore la qualité des **trajectoires d'agent** ; il faut en général **renvoyer les blocs de raisonnement** précédents dans l'historique pour garder la cohérence ([[31-agents-fondamentaux|agents]]).

---

Qu'est-ce que le best-of-n avec vérificateur ? <!--anki:674758746a32554c483a-->
?
Générer **n réponses** puis choisir la meilleure grâce à un **vérificateur** : tests unitaires (code), vérification formelle, [[95-llm-as-judge|juge]] ou reward model. Le gain dépend surtout de la **qualité du vérificateur** : un vérificateur exécutable (tests) est bien plus fiable qu'un juge LLM.

---

À ne pas confondre : modèle de raisonnement et chain-of-thought par prompt ? <!--anki:44797d3846553d526763-->
?
- **Chain-of-thought par prompt** : on **demande** à un modèle classique d'écrire ses étapes. Le gain dépend de la formulation et reste limité ([[11-prompt-engineering-avance|prompt engineering]])
- **Modèle de raisonnement** : le modèle a été **entraîné par RL** à produire une longue réflexion, à se vérifier et à revenir en arrière. La réflexion est **native**, souvent réglable par un budget, et parfois masquée

Conséquence : avec un modèle de raisonnement, on décrit **l'objectif et les critères** plutôt que les étapes, et on paie les tokens de réflexion.

---

Calcul : 100 000 requêtes/jour utilisent chacune 1 000 tokens d’entrée et 300 de sortie visible. À 3 €/M en entrée et 15 €/M en sortie, quel coût supplémentaire et total si chacune ajoute 4 000 tokens de raisonnement facturés en sortie ? <!--anki:6261636664353832363133613430613738386335656266613266306232393465-->
?
Hypothèses : 1 000 tokens d'entrée, 300 tokens de réponse visible, 4 000 tokens de raisonnement facturés comme de la sortie ; 3 €/M en entrée, 15 €/M en sortie.
```text
sans raisonnement : 1 000 × 3 €/M + 300 × 15 €/M = 0,0075 € par requête
raisonnement      : 4 000 × 15 €/M               = 0,060 € de plus
avec raisonnement :                                0,0675 € (× 9)
par jour          : 750 € → 6 750 €
```
La réponse visible est la même, mais le coût est multiplié par 9 et la latence s'allonge : on règle l'**effort de raisonnement** par type de requête, et on route les questions simples vers un mode sans raisonnement ([[82-routing-llm|routing]]).

---

## Mises en situation

Mise en situation : ton équipe passe tout le trafic sur un modèle de raisonnement « puisqu'il est meilleur ». Le coût triple et les utilisateurs trouvent l'assistant lent. Que proposes-tu ? <!--anki:4c38422a7861506f2f53-->
?
1. **Segmenter** : classification, extraction et reformulation ne tirent aucun bénéfice du raisonnement
2. **Router par difficulté** : raisonnement réservé aux problèmes à plusieurs étapes ([[82-routing-llm|routing]])
3. **Régler l'effort** : le budget de réflexion est un curseur qualité, latence et coût
4. **Mesurer le coût réel** : les tokens de réflexion sont facturés comme des tokens de sortie, même invisibles
5. **Vérifier le gain** par segment, sur tes evals, avant de généraliser ([[94-evals-methodologie|evals]])

**Piège** : comparer les modèles sur les cas difficiles seulement, puis appliquer la conclusion à tout le trafic.

---

Mise en situation : un auditeur veut utiliser la chaîne de pensée affichée par le modèle comme justification des décisions prises par ton système. Qu'en dis-tu ? <!--anki:734e60406e7636373164-->
?
1. **Avertir** : la réflexion affichée n'est pas toujours fidèle au processus réel du modèle
2. **Ce à quoi elle sert** : déboguer, surveiller, repérer des trajectoires aberrantes
3. **Ce qu'elle ne fournit pas** : une explication garantie ni une preuve de correction
4. **Ce qui fait foi** : les données consultées, les outils appelés, les règles appliquées et les validations ([[115-plateformes-agents-gouvernance|audit]])
5. **Pour les usages sensibles** : décision vérifiable par du code ou validée par un humain ([[144-ux-ia-human-in-the-loop|human-in-the-loop]])

**Piège** : présenter la chaîne de pensée comme une justification opposable, notamment dans un cadre réglementé.

---

## Sources

- [DeepSeek-AI — DeepSeek-R1 (2025)](https://arxiv.org/abs/2501.12948)

## Connexions
- [[52-post-training-alignement|Post-training & alignement]] — RL avec récompenses vérifiables
- [[11-prompt-engineering-avance|Prompt engineering]] — chain-of-thought et self-consistency
- [[82-routing-llm|Routing LLM]] — réserver le raisonnement aux requêtes difficiles
- [[121-couts-inference|Coûts d'inférence]] — tokens de réflexion
- [[64-metriques-slo-inference|Métriques & SLO]] — latence des réponses longues
- [[135-pretraining-scaling-laws|Pré-entraînement & scaling laws]] — du calcul d'entraînement au calcul d'inférence
- [[55-rl-agentique|RL agentique]] — du raisonnement à l'usage d'outils
- [[13-prompts-production|Prompts en production]] — structure, versioning et portabilité des prompts
- [[60-012-demarche-optimisation-inference|Démarche d’optimisation]] — prioriser et vérifier les gains sous contraintes de service
- [[00-moc-ai-engineering|MOC AI Engineering]]
