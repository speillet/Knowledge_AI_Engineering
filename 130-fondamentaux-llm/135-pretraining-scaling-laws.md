# Pré-entraînement & scaling laws — Flashcards
Tags: #flashcards #ai-engineering #fondamentaux #pretraining #scaling #llm

Quelles sont les grandes étapes de fabrication d'un LLM ?
?
1. **Pré-entraînement** : prédiction du token suivant sur des **milliers de milliards de tokens** → modèle de base (connaissances, langue, raisonnement latent).
2. **Mid-training** (optionnel) : données plus ciblées (code, maths, long contexte).
3. **Post-training** : SFT puis alignement par préférences et **RL** → modèle qui suit les instructions, utilise des outils et raisonne ([[52-post-training-alignement|post-training]]).

---

Sur quelles données pré-entraîne-t-on un LLM ?
?
Du **web filtré** (Common Crawl nettoyé), du **code**, des **livres**, des articles scientifiques, des données multilingues et, de plus en plus, des **données synthétiques**. La qualité prime : **déduplication**, filtres de qualité (souvent par classifieur), retrait des contenus toxiques et des PII, **décontamination** des benchmarks ([[151-donnees-curation-annotation|curation]]).

---

Que disent les scaling laws ?
?
La **loss** du modèle diminue de façon **prévisible (loi de puissance)** avec la **taille du modèle (N)**, la **quantité de données (D)** et le **calcul (C ≈ 6·N·D FLOPs)**. On peut donc **prédire la performance** d'un gros entraînement à partir de petits essais, et choisir comment répartir un budget de calcul.

---

Qu'a montré Chinchilla ?
?
Qu'à **budget de calcul fixe**, l'optimum est d'augmenter **paramètres et tokens à parts égales**, soit environ **20 tokens par paramètre**. Beaucoup de modèles antérieurs étaient **trop gros et sous-entraînés**.

---

Pourquoi les modèles actuels sont-ils entraînés bien au-delà de Chinchilla ?
?
Chinchilla optimise le **coût d'entraînement**, pas le **coût total**. Un modèle plus **petit** entraîné sur **beaucoup plus de tokens** (des centaines, voire des milliers de tokens par paramètre) coûte plus à entraîner mais est **moins cher à servir** — et l'inférence domine le coût sur la durée de vie d'un modèle déployé.

---

Qu'est-ce que la loi « 6ND » et à quoi sert-elle ?
?
Le calcul d'entraînement d'un Transformer dense ≈ **6 × paramètres × tokens** FLOPs (2 pour la passe avant, 4 pour la passe arrière). Exemple : 8 B paramètres sur 15 T tokens ≈ **7,2·10²³ FLOPs**. Divisé par le débit réel du cluster (FLOPs/s × **MFU**), on obtient les **GPU-heures** nécessaires.

---

Qu'est-ce que le MFU ?
?
**Model FLOPs Utilization** : la part de la puissance de calcul **théorique** des GPU réellement utilisée pour l'entraînement. Typiquement **30 à 50 %** sur de gros clusters ; le reste est perdu en communications, attentes mémoire et pannes ([[54-entrainement-distribue|entraînement distribué]]).

---

Qu'est-ce que la contamination des benchmarks ?
?
La présence des **questions (et réponses) d'un benchmark dans les données d'entraînement**. Le modèle les a « vues » : son score **surestime** sa capacité réelle. D'où les benchmarks **récents ou privés**, les tests sur des variantes reformulées, et la prudence face aux leaderboards ([[146-choix-modeles|choix de modèle]]).

---

Qu'est-ce que la date de coupure (knowledge cutoff) ?
?
La date après laquelle **aucune donnée** n'a été vue en entraînement. Le modèle ignore les événements, versions d'API ou bibliothèques postérieurs, et peut **affirmer avec assurance** des informations périmées → [[21-rag-fondamentaux|RAG]] ou outils de recherche pour tout ce qui change.

---

Qu'appelle-t-on capacités émergentes, et pourquoi sont-elles débattues ?
?
Des capacités qui semblent **apparaître brusquement** au-delà d'une certaine taille. Une partie de cet effet vient du **choix de la métrique** (exact match, tout ou rien) : avec une métrique continue, le progrès est souvent **graduel**. Moralité : **mesurer sur sa tâche** plutôt que supposer un seuil.

---

Pourquoi parle-t-on de « mur des données » ?
?
Le stock de **texte humain de qualité** disponible sur le web est fini et en voie d'épuisement au rythme actuel. Les réponses : **données synthétiques**, **multimodal**, entraînement sur **plusieurs époques** des meilleures données, et déplacement du calcul vers le **post-training par RL** et le **test-time compute** ([[138-modeles-raisonnement|modèles de raisonnement]]).

---

À ne pas confondre : pré-entraînement et post-training ?
?
- **Pré-entraînement** : prédire le token suivant sur des **milliers de milliards de tokens** de texte brut. Il apporte les **connaissances** et les capacités générales, et coûte l'essentiel du calcul
- **Post-training** : SFT puis préférences ou RL (RLHF, DPO, RLVR) sur des jeux **beaucoup plus petits**. Il apporte le **comportement** : suivre les instructions, le format, le refus, le raisonnement ([[52-post-training-alignement|post-training]])

Conséquence pratique : un fine-tuning d'entreprise est du post-training. Il change la **forme** des réponses bien plus facilement qu'il n'ajoute des **connaissances** ([[51-fine-tuning-adaptation|fine-tuning]]).

---

## Mises en situation

Mise en situation : un modèle affiche 92 % sur un benchmark public de raisonnement, mais s'effondre sur tes cas métier. Quelles explications envisages-tu ?
?
1. **Contamination** : les questions du benchmark, ou leurs variantes, étaient peut-être dans les données d'entraînement
2. **Écart de distribution** : le benchmark ne ressemble pas à ton trafic, ni en langue, ni en format, ni en difficulté
3. **Métrique** : un score global peut masquer l'échec sur le segment qui t'intéresse
4. **La bonne réponse** : évaluer sur **tes** données, les benchmarks ne servant qu'au pré-tri ([[146-choix-modeles|choix de modèle]])
5. **Vérifier la date de coupure** si tes cas portent sur des informations récentes

**Piège** : arbitrer entre deux modèles sur la foi d'un classement public.

---

Mise en situation : ta direction demande combien coûterait le pré-entraînement d'un modèle « maison » de 8 milliards de paramètres. Comment réponds-tu ?
?
1. **Estimer le calcul** : environ 6 × paramètres × tokens. Pour 8 milliards sur 15 000 milliards de tokens, l'ordre de grandeur est colossal
2. **Convertir en GPU-heures** : diviser par le débit réel du cluster, sachant que l'utilisation effective des GPU tourne souvent autour de 30 à 50 %
3. **Ajouter le reste** : collecte et curation des données, essais ratés, post-training, evals
4. **Poser la vraie question** : quel besoin ne serait pas couvert par un modèle existant, fine-tuné ou distillé ?
5. **Proposer l'alternative** : fine-tuning ou distillation, pour une fraction du coût ([[53-donnees-synthetiques-distillation|distillation]])

**Piège** : comparer un coût d'entraînement à un coût d'API sans regarder la durée de vie et le coût d'inférence.

---

## Connexions
- [[131-transformer-architecture|Architecture Transformer]] — ce qu'on entraîne
- [[52-post-training-alignement|Post-training & alignement]] — l'étape suivante
- [[53-donnees-synthetiques-distillation|Données synthétiques & distillation]] — au-delà du mur des données
- [[54-entrainement-distribue|Entraînement distribué]] — comment on parallélise
- [[136-mixture-of-experts|Mixture of Experts]] — plus de paramètres sans plus de calcul
- [[146-choix-modeles|Choix de modèle]] — lire les benchmarks
- [[55-rl-agentique|RL agentique]] — entraîner un modèle sur des tâches d'agent
- [[69-roofline-prefill-decode|Roofline & désagrégation]] — ce qui limite chaque phase de l'inférence
- [[00-moc-ai-engineering|MOC AI Engineering]]
