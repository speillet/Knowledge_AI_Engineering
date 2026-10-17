# Post-training & alignement — Flashcards
Tags: #flashcards #ai-engineering #fine-tuning #alignement #rlhf #llm
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.
<!-- summary: étapes du RLHF, pénalité KL, reward hacking, DPO et variantes, GRPO, RLVR, RLAIF et Constitutional AI, jeux de préférences, taxe d'alignement, reward model ou vérificateur, quand faire soi-même du DPO ou du RL. -->


Qu'est-ce que le post-training ? <!--anki:73335f71655f3f304837-->
?
Tout ce qui transforme un **modèle de base** (qui continue du texte) en **assistant** : **SFT** sur des démonstrations, puis **optimisation par préférences** et **RL** pour l'utilité, la sécurité, le raisonnement et l'usage d'outils. C'est là que se jouent le **comportement** et une grande part des différences entre modèles.

Le SFT montre des réponses souhaitées ; les méthodes par préférences ou récompenses orientent ensuite les comportements selon un critère. Ces étapes ne forment pas une recette obligatoire identique pour tous les modèles. Évaluer séparément suivi d'instructions, exactitude et refus : une réponse plus agréable peut être moins bien calibrée ou perdre certaines capacités spécialisées.

---

Quelles sont les étapes classiques du RLHF ? <!--anki:6e65685b71755b4e5f2c-->
?
1. **SFT** sur des réponses écrites par des humains.
2. **Collecte de préférences** : des annotateurs comparent plusieurs réponses à un même prompt.
3. **Reward model** entraîné à prédire la réponse préférée.
4. **Optimisation RL** (PPO) du modèle pour maximiser la récompense, avec une **pénalité KL** qui l'empêche de trop s'éloigner du modèle SFT.

---

Pourquoi une pénalité KL pendant le RL ? <!--anki:6f333c253e66767e7635-->
?
Sans elle, le modèle **exploite les failles du reward model** (reward hacking) : il produit des sorties qui obtiennent un score élevé sans être meilleures (flatterie, verbosité, formules types). La KL **l'ancre** à un comportement de référence raisonnable.

La divergence KL pénalise l'écart entre la **politique entraînée** et une politique de référence. Un coefficient trop fort freine l'apprentissage ; trop faible laisse le modèle s'éloigner rapidement. Suivre récompense, KL et qualité sur des évaluations indépendantes. Cette régularisation limite la dérive mais ne corrige pas un vérificateur ou un reward model mal conçu.

---

Qu'est-ce que le reward hacking ? <!--anki:5157706d245948426c43-->
?
Quand le modèle **maximise la récompense sans atteindre l'objectif réel** : réponses plus longues parce que le reward model aime la longueur, **tests modifiés** pour passer plutôt que code corrigé, **complaisance** (sycophancy) envers l'utilisateur. C'est la loi de Goodhart appliquée à l'entraînement.

Le problème vient de l'écart entre **mesure optimisée et résultat souhaité**. Un agent récompensé au nombre de tests réussis peut supprimer les tests difficiles si l'environnement le permet. Protéger les critères de validation, conserver des évaluations indépendantes et examiner les trajectoires inhabituelles. Une récompense qui monte alors que l'utilité baisse est un signal d'alerte.

---

Qu'apporte DPO par rapport au RLHF classique ? <!--anki:506a3b4d5e7d4e4b737a-->
?
**Direct Preference Optimization** optimise **directement** le modèle sur les paires (préférée, rejetée) avec une loss de classification, **sans reward model séparé ni boucle RL**. Souvent plus **simple et moins coûteux** à mettre en œuvre, c'est une option fréquente pour aligner un modèle open source sur ses préférences. Gain et stabilité restent à mesurer : des paires biaisées apprennent la longueur ou le style du gagnant. Variantes : IPO, KTO (préférences non appariées, simple pouce haut/bas), ORPO, SimPO.

---

Qu'est-ce que GRPO ? <!--anki:7a7b5346495648755428-->
?
**Group Relative Policy Optimization** : pour chaque prompt, on génère **un groupe de réponses**, on les note, et l'avantage de chaque réponse est calculé **par rapport à la moyenne du groupe**. Pas besoin de **value model** (critique) comme dans PPO → moins de mémoire. Popularisé par DeepSeek pour l'entraînement au **raisonnement** avec récompenses vérifiables ([[138-modeles-raisonnement|modèles de raisonnement]]).

---

Qu'est-ce que le RLVR ? <!--anki:4c412b4556294b474f37-->
?
Le **RL with Verifiable Rewards** utilise une récompense issue d'un vérificateur automatique : résultat numérique attendu, tests exécutés ou contraintes de format, plutôt qu'un jugement de préférence appris. Il est utile lorsque la réussite possède un critère contrôlable, notamment dans certains exercices de code et de mathématiques.

La qualité dépend du vérificateur : une suite de tests incomplète peut accepter du code incorrect, et un format valide ne garantit pas le fond. Protéger le vérificateur, varier les cas et évaluer sur des problèmes indépendants. Le RLVR réduit certains jugements subjectifs ; il n'élimine pas le **reward hacking**.

---

Qu'est-ce que le RLAIF et la Constitutional AI ? <!--anki:672962255f7837583554-->
?
- **RLAIF** : les préférences sont produites par **un modèle** plutôt que par des humains → beaucoup moins cher et plus rapide.
- **Constitutional AI** (Anthropic) : le modèle **critique et révise** ses propres réponses selon une **liste de principes écrits** (la constitution), et ces jugements servent de données de préférence.

---

Comment construire un bon jeu de préférences ? <!--anki:5161616669632121623d-->
?
- Prompts **représentatifs** de l'usage visé, y compris des cas difficiles.
- Réponses candidates **variées** (plusieurs modèles ou températures) pour que les comparaisons soient informatives.
- **Consignes d'annotation** précises, mesure de l'**accord inter-annotateurs**.
- Contrôle des biais (longueur, format) pour ne pas apprendre « plus long = mieux ».

Voir [[151-donnees-curation-annotation|annotation]].

---

Qu'est-ce que la « taxe d'alignement » ? <!--anki:45516e7073676e383561-->
?
La **perte de capacités** (créativité, précision sur certains benchmarks, calibration) que peut entraîner l'alignement. Elle se manifeste aussi par des **refus excessifs** (over-refusal) sur des demandes légitimes. On la mesure avec des evals de capacités **avant et après**, et des jeux de requêtes **légitimes mais sensibles**.

Ce compromis doit être établi sur des tâches comparables, avec les mêmes conditions de génération. Distinguer baisse réelle de compétence, changement de style et refus d'exécuter la tâche : leurs corrections diffèrent. L'alignement peut aussi améliorer certaines capacités ; la taxe n'est donc ni une constante ni une perte uniforme sur tous les usages.

---

Quand un AI Engineer fait-il lui-même du DPO ou du RL ? <!--anki:47504835327623642953-->
?
Rarement pour l'alignement général (déjà fait par le fournisseur). Mais c'est pertinent pour :
- aligner un **petit modèle** open source sur le **style ou la politique** de l'entreprise ;
- exploiter les **retours utilisateurs** (pouce haut/bas → KTO/DPO) ;
- entraîner un modèle spécialisé sur une tâche **vérifiable** (RLVR : SQL, extraction, code interne).

Outils : TRL, OpenRLHF, verl, Unsloth, ou les API de fine-tuning par préférences.

---

À ne pas confondre : reward model et vérificateur ? <!--anki:7948387d326c52594e29-->
?
- **Reward model** : un modèle **appris** sur des préférences humaines, qui estime une note. Il généralise à des tâches subjectives, mais peut être **exploité** (reward hacking)
- **Vérificateur** : un contrôle **programmatique** (résultat mathématique, tests unitaires, schéma). Fiable et difficile à tromper, mais limité aux tâches **vérifiables**

Le RLHF repose sur le premier, le RLVR sur le second ([[55-rl-agentique|RL agentique]]).

---

## Mises en situation

Mise en situation : tu as collecté 20 000 pouces haut/bas sur ton assistant. Comment les exploites-tu pour améliorer un petit modèle open source ? <!--anki:662b6070394656757737-->
?
1. **Format des données** : des retours non appariés se prêtent à **KTO** ; si tu peux régénérer une réponse alternative, tu obtiens des paires pour **DPO**
2. **Nettoyer** : retirer les votes incohérents, dédupliquer, vérifier les biais (longueur, format)
3. **Partir d'un SFT propre** avant d'optimiser les préférences
4. **Garder une ancre** : pénalité qui empêche de trop s'éloigner du modèle de départ, sinon le comportement dérive
5. **Mesurer la taxe d'alignement** : evals de capacités générales et jeu de requêtes légitimes mais sensibles, contre les refus excessifs

**Piège** : optimiser sur les pouces sans contrôle, et obtenir un modèle **complaisant** qui plaît sans aider.

---

Mise en situation : ton modèle entraîné à corriger du code obtient d'excellents scores, mais en production il modifie souvent les tests au lieu du code. Que s'est-il passé ? <!--anki:47402b3669547e5d3b2d-->
?
1. **Reward hacking** : la récompense était « les tests passent », le modèle a trouvé le raccourci
2. **Durcir le vérificateur** : tests en lecture seule, comparaison des tests avant et après, échec si le diff les touche
3. **Récompense composite** : tests qui passent **et** diff limité au code source, avec revue sur un échantillon
4. **Rappeler la loi de Goodhart** : toute métrique optimisée finit par être détournée
5. **Évaluer sur des cas non vus**, avec des tests cachés du modèle ([[94-evals-methodologie|evals]])

**Piège** : augmenter la récompense sans corriger sa définition.

---

## Sources

- [Rafailov et al. — Direct Preference Optimization (2023)](https://arxiv.org/abs/2305.18290)
- [Hugging Face — TRL, entraînement et alignement](https://huggingface.co/docs/trl/index)

## Connexions
- [[51-fine-tuning-adaptation|Fine-tuning & adaptation]] — SFT, LoRA, DPO en bref
- [[53-donnees-synthetiques-distillation|Données synthétiques & distillation]] — produire les données de post-training
- [[138-modeles-raisonnement|Modèles de raisonnement]] — RL avec récompenses vérifiables
- [[95-llm-as-judge|LLM-as-a-judge]] — juges et reward models
- [[156-ia-responsable|IA responsable]] — sécurité et biais du comportement
- [[135-pretraining-scaling-laws|Pré-entraînement]] — l'étape précédente
- [[55-rl-agentique|RL agentique]] — le RL sur des trajectoires d'outils
- [[65-probabilites-sampling|Probabilités & sampling]] — température, top-p et logprobs
- [[00-moc-ai-engineering|MOC AI Engineering]]
