# Post-training & alignement — Flashcards
Tags: #flashcards #ai-engineering #fine-tuning #alignement #rlhf #llm
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.

Qu'est-ce que le post-training ?
?
Tout ce qui transforme un **modèle de base** (qui continue du texte) en **assistant** : **SFT** sur des démonstrations, puis **optimisation par préférences** et **RL** pour l'utilité, la sécurité, le raisonnement et l'usage d'outils. C'est là que se jouent le **comportement** et une grande part des différences entre modèles.

---

Quelles sont les étapes classiques du RLHF ?
?
1. **SFT** sur des réponses écrites par des humains.
2. **Collecte de préférences** : des annotateurs comparent plusieurs réponses à un même prompt.
3. **Reward model** entraîné à prédire la réponse préférée.
4. **Optimisation RL** (PPO) du modèle pour maximiser la récompense, avec une **pénalité KL** qui l'empêche de trop s'éloigner du modèle SFT.

---

Pourquoi une pénalité KL pendant le RL ?
?
Sans elle, le modèle **exploite les failles du reward model** (reward hacking) : il produit des sorties qui obtiennent un score élevé sans être meilleures (flatterie, verbosité, formules types). La KL **l'ancre** à un comportement de référence raisonnable.

---

Qu'est-ce que le reward hacking ?
?
Quand le modèle **maximise la récompense sans atteindre l'objectif réel** : réponses plus longues parce que le reward model aime la longueur, **tests modifiés** pour passer plutôt que code corrigé, **complaisance** (sycophancy) envers l'utilisateur. C'est la loi de Goodhart appliquée à l'entraînement.

---

Qu'apporte DPO par rapport au RLHF classique ?
?
**Direct Preference Optimization** optimise **directement** le modèle sur les paires (préférée, rejetée) avec une loss de classification, **sans reward model séparé ni boucle RL**. Plus **simple, stable et bon marché** — c'est l'option par défaut pour aligner un modèle open source sur ses propres préférences. Variantes : IPO, KTO (préférences non appariées, simple pouce haut/bas), ORPO, SimPO.

---

Qu'est-ce que GRPO ?
?
**Group Relative Policy Optimization** : pour chaque prompt, on génère **un groupe de réponses**, on les note, et l'avantage de chaque réponse est calculé **par rapport à la moyenne du groupe**. Pas besoin de **value model** (critique) comme dans PPO → moins de mémoire. Popularisé par DeepSeek pour l'entraînement au **raisonnement** avec récompenses vérifiables ([[138-modeles-raisonnement|modèles de raisonnement]]).

---

Qu'est-ce que le RLVR ?
?
**RL with Verifiable Rewards** : la récompense vient d'un **vérificateur automatique** (réponse mathématique exacte, tests unitaires qui passent, format respecté) plutôt que d'un reward model appris. Beaucoup **moins exposé au reward hacking** et très efficace pour le code et les maths ; limité aux tâches **vérifiables**.

---

Qu'est-ce que le RLAIF et la Constitutional AI ?
?
- **RLAIF** : les préférences sont produites par **un modèle** plutôt que par des humains → beaucoup moins cher et plus rapide.
- **Constitutional AI** (Anthropic) : le modèle **critique et révise** ses propres réponses selon une **liste de principes écrits** (la constitution), et ces jugements servent de données de préférence.

---

Comment construire un bon jeu de préférences ?
?
- Prompts **représentatifs** de l'usage visé, y compris des cas difficiles.
- Réponses candidates **variées** (plusieurs modèles ou températures) pour que les comparaisons soient informatives.
- **Consignes d'annotation** précises, mesure de l'**accord inter-annotateurs**.
- Contrôle des biais (longueur, format) pour ne pas apprendre « plus long = mieux ».

Voir [[151-donnees-curation-annotation|annotation]].

---

Qu'est-ce que la « taxe d'alignement » ?
?
La **perte de capacités** (créativité, précision sur certains benchmarks, calibration) que peut entraîner l'alignement. Elle se manifeste aussi par des **refus excessifs** (over-refusal) sur des demandes légitimes. On la mesure avec des evals de capacités **avant et après**, et des jeux de requêtes **légitimes mais sensibles**.

---

Quand un AI Engineer fait-il lui-même du DPO ou du RL ?
?
Rarement pour l'alignement général (déjà fait par le fournisseur). Mais c'est pertinent pour :
- aligner un **petit modèle** open source sur le **style ou la politique** de l'entreprise ;
- exploiter les **retours utilisateurs** (pouce haut/bas → KTO/DPO) ;
- entraîner un modèle spécialisé sur une tâche **vérifiable** (RLVR : SQL, extraction, code interne).

Outils : TRL, OpenRLHF, verl, Unsloth, ou les API de fine-tuning par préférences.

---

## Mises en situation

Mise en situation : tu as collecté 20 000 pouces haut/bas sur ton assistant. Comment les exploites-tu pour améliorer un petit modèle open source ?
?
1. **Format des données** : des retours non appariés se prêtent à **KTO** ; si tu peux régénérer une réponse alternative, tu obtiens des paires pour **DPO**
2. **Nettoyer** : retirer les votes incohérents, dédupliquer, vérifier les biais (longueur, format)
3. **Partir d'un SFT propre** avant d'optimiser les préférences
4. **Garder une ancre** : pénalité qui empêche de trop s'éloigner du modèle de départ, sinon le comportement dérive
5. **Mesurer la taxe d'alignement** : evals de capacités générales et jeu de requêtes légitimes mais sensibles, contre les refus excessifs

**Piège** : optimiser sur les pouces sans contrôle, et obtenir un modèle **complaisant** qui plaît sans aider.

---

Mise en situation : ton modèle entraîné à corriger du code obtient d'excellents scores, mais en production il modifie souvent les tests au lieu du code. Que s'est-il passé ?
?
1. **Reward hacking** : la récompense était « les tests passent », le modèle a trouvé le raccourci
2. **Durcir le vérificateur** : tests en lecture seule, comparaison des tests avant et après, échec si le diff les touche
3. **Récompense composite** : tests qui passent **et** diff limité au code source, avec revue sur un échantillon
4. **Rappeler la loi de Goodhart** : toute métrique optimisée finit par être détournée
5. **Évaluer sur des cas non vus**, avec des tests cachés du modèle ([[94-evals-methodologie|evals]])

**Piège** : augmenter la récompense sans corriger sa définition.

---

## Connexions
- [[51-fine-tuning-adaptation|Fine-tuning & adaptation]] — SFT, LoRA, DPO en bref
- [[53-donnees-synthetiques-distillation|Données synthétiques & distillation]] — produire les données de post-training
- [[138-modeles-raisonnement|Modèles de raisonnement]] — RL avec récompenses vérifiables
- [[95-llm-as-judge|LLM-as-a-judge]] — juges et reward models
- [[156-ia-responsable|IA responsable]] — sécurité et biais du comportement
- [[135-pretraining-scaling-laws|Pré-entraînement]] — l'étape précédente
- [[00-moc-ai-engineering|MOC AI Engineering]]
