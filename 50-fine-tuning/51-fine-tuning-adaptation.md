# Fine-tuning & adaptation de modèles — Flashcards
Tags: #flashcards #ai-engineering #fine-tuning #llm

Qu'est-ce que le fine-tuning ?
?
**Poursuivre l'entraînement d'un modèle pré-entraîné** sur des données spécifiques pour adapter son comportement, son style ou son domaine.

---

Quand fine-tuner plutôt que prompter ou faire du RAG ?
?
Pour un **comportement constant** (format, ton, tâche spécialisée répétitive), la **distillation**, ou raccourcir les [[11-prompt-engineering-avance|prompts]] (latence/coût) — **pas** pour injecter des connaissances fraîches (→ [[21-rag-fondamentaux|RAG]]).

---

Qu'est-ce que le SFT ?
?
**Supervised Fine-Tuning** : entraînement sur des paires **instruction → réponse attendue** de qualité.

---

Quelle différence entre full fine-tuning et PEFT ?
?
Le **full FT** met à jour tous les poids (coûteux en GPU et stockage) ; le **PEFT** (Parameter-Efficient FT) n'entraîne qu'une **petite fraction de paramètres**.

---

Qu'est-ce que LoRA ?
?
**Low-Rank Adaptation** : on gèle les poids et on entraîne de **petites matrices de bas rang** ajoutées aux couches — l'adapter ne pèse que quelques Mo.

---

Qu'est-ce que QLoRA ?
?
**LoRA sur un modèle quantizé en 4-bit** : fine-tuner un gros modèle sur un GPU modeste.

---

Qu'est-ce que le RLHF ?
?
**Reinforcement Learning from Human Feedback** : un reward model entraîné sur des préférences humaines guide l'optimisation (PPO) du modèle — la base de l'alignement.

---

Qu'est-ce que DPO ?
?
**Direct Preference Optimization** : aligner directement sur des **paires réponse préférée / rejetée**, sans reward model ni RL — plus simple et stable que RLHF.

---

Qu'est-ce que la distillation ?
?
Entraîner un **petit modèle sur les sorties d'un grand** : qualité proche sur le domaine ciblé, coût d'inférence fortement réduit.

---

Comment servir plusieurs fine-tunings à moindre coût ?
?
Par le **multi-LoRA** : le serveur ([[11-serveurs-inference-llm|vLLM]]) charge **plusieurs adapters** au-dessus d'un même modèle de base partagé.

---

Quel est le principal risque du fine-tuning ?
?
Le **catastrophic forgetting** et la régression sur les capacités générales → [[92-chainforge-evals-prompts|evals]] avant/après obligatoires.

---

## Connexions
- [[21-rag-fondamentaux|RAG]] — connaissances vs comportement
- [[11-prompt-engineering-avance|Prompt engineering]] — l'alternative légère
- [[11-serveurs-inference-llm|Serveurs d'inférence]] — multi-LoRA en serving
- [[62-optimisations-inference|Optimisations]] — quantization (QLoRA)
- [[92-chainforge-evals-prompts|Evals]] — mesurer avant/après
- [[113-monitoring-drift-feedback|Monitoring & drift]] — quand ré-entraîner
- [[68-quantization|Quantization]] — NF4 et les formats de serving
- [[00-moc-ai-engineering|MOC AI Engineering]]
