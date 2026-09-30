# Fine-tuning & adaptation de modèles — Flashcards
Tags: #flashcards #ai-engineering #fine-tuning #llm

Qu'est-ce que le fine-tuning ?
?
**Poursuivre l'entraînement d'un modèle pré-entraîné** sur des données spécifiques, pour adapter son **comportement**, son **format** ou son **domaine**. En pratique, pour une équipe produit : du **SFT** sur quelques centaines à quelques milliers d'exemples, le plus souvent avec **LoRA**.

Il sert à changer **comment** le modèle répond, bien plus qu'à lui apprendre des faits nouveaux, qui relèvent plutôt du [[21-rag-fondamentaux|RAG]].

---

Quand fine-tuner plutôt que prompter ou faire du RAG ?
?
Pour un **comportement constant** (format, ton, tâche spécialisée répétitive), la **distillation**, ou raccourcir les [[11-prompt-engineering-avance|prompts]] (latence/coût) — **pas** pour injecter des connaissances fraîches (→ [[21-rag-fondamentaux|RAG]]).

---

Qu'est-ce que le SFT ?
?
**Supervised Fine-Tuning** : entraînement sur des paires **instruction → réponse attendue** de qualité. Le format doit être **exactement celui de l'inférence**, chat template et outils compris ([[132-tokenisation|chat template]]).
```jsonl
{"messages": [
  {"role": "system", "content": "Tu extrais les champs d'une facture en JSON."},
  {"role": "user", "content": "Facture n°A-4471 du 12/03 : 1 240,50 € TTC…"},
  {"role": "assistant", "content": "{\"numero\":\"A-4471\",\"total\":1240.50}"}
]}
```
La perte n'est calculée que sur la **réponse de l'assistant**, pas sur la consigne.

---

À ne pas confondre : full fine-tuning et PEFT ?
?
Le **full FT** met à jour tous les poids (coûteux en GPU et stockage) ; le **PEFT** (Parameter-Efficient FT) n'entraîne qu'une **petite fraction de paramètres**.

---

Qu'est-ce que LoRA ?
?
**Low-Rank Adaptation** : on gèle les poids et on entraîne de **petites matrices de bas rang** ajoutées aux couches — l'adapter ne pèse que quelques Mo.

---

Qu'est-ce que QLoRA ?
?
**LoRA sur un modèle quantizé en 4-bit** : fine-tuner un gros modèle sur un GPU modeste. Les poids de base restent figés en 4 bits (format NF4), seuls les adapters s'entraînent en précision plus haute ([[68-quantization|NF4]]).

---

Quels ordres de grandeur pour un fine-tuning ?
?
```text
Exemples nécessaires (SFT)   quelques centaines à quelques milliers de bons exemples
Taille d'un adapter LoRA     quelques Mo à quelques dizaines de Mo
Mémoire, full FT d'un 7B     ~112 Go → plusieurs GPU
Mémoire, LoRA d'un 8B        tient sur 1 GPU de 24 à 48 Go
Mémoire, QLoRA d'un 70B      tient sur 1 GPU de 48 à 80 Go
Durée d'un LoRA              minutes à quelques heures
```
Retenir : la **qualité des données** compte plus que leur volume, et **LoRA change l'ordre de grandeur matériel** ([[54-entrainement-distribue|entraînement distribué]]).

---

Qu'est-ce que le RLHF ?
?
**Reinforcement Learning from Human Feedback** : un reward model entraîné sur des préférences humaines guide l'optimisation (PPO) du modèle — la base de l'alignement.

---

Qu'est-ce que DPO ?
?
**Direct Preference Optimization** : aligner directement sur des **paires réponse préférée / rejetée**, sans reward model ni RL — plus simple et stable que RLHF.

---

Comment obtenir un petit modèle aussi bon qu'un grand sur un domaine précis ?
?
Par la **distillation** : entraîner un **petit modèle sur les sorties d'un grand**. Qualité proche sur le domaine ciblé, coût d'inférence fortement réduit ([[53-donnees-synthetiques-distillation|distillation en détail]]).

---

Comment servir plusieurs fine-tunings à moindre coût ?
?
Par le **multi-LoRA** : le serveur charge **un seul modèle de base** et, par-dessus, **plusieurs adapters** légers (quelques dizaines à centaines de Mo chacun), choisis **requête par requête** ([[11-serveurs-inference-llm|vLLM]]).
```bash
vllm serve meta-llama/Llama-3.1-8B-Instruct --enable-lora \
  --lora-modules support=./lora-support juridique=./lora-juridique
```
Cent clients avec chacun leur fine-tuning tiennent ainsi sur quelques GPU, au lieu de cent modèles complets.

---

Quel est le principal risque du fine-tuning ?
?
Le **catastrophic forgetting** : en s'adaptant à la tâche, le modèle **perd des capacités générales** (raisonnement, suivi d'instructions, refus appropriés, autres langues).

Parades :
- **LoRA** plutôt que full fine-tuning, et un taux d'apprentissage modéré
- **Mélanger** des données générales aux données de la tâche
- **Evals avant/après** sur la tâche **et** sur les capacités générales ([[92-chainforge-evals-prompts|evals]])

---

## Mises en situation

Mise en situation : le métier veut fine-tuner un modèle « pour qu'il connaisse nos procédures internes », qui changent chaque mois. Que réponds-tu ?
?
1. **Séparer connaissances et comportement** : des procédures qui changent relèvent du **RAG**, pas du fine-tuning ([[21-rag-fondamentaux|RAG]])
2. **Rappeler le coût du cycle** : chaque mise à jour demanderait un nouvel entraînement, de nouvelles evals et un redéploiement
3. **Ce que le fine-tuning apporterait vraiment** : un format de réponse constant, un ton, une tâche répétitive, des prompts plus courts
4. **Proposer une étape intermédiaire** : prompt soigné plus RAG, mesuré sur un golden dataset
5. **Garder la porte ouverte** : si le format reste instable après optimisation, un fine-tuning léger (LoRA) se justifie

**Piège** : fine-tuner sur des documents internes et croire que le modèle « saura » les citer correctement.

---

Mise en situation : ton modèle fine-tuné est excellent sur l'extraction visée, mais les utilisateurs signalent qu'il répond n'importe quoi aux questions générales. Que s'est-il passé ?
?
1. **Catastrophic forgetting** : l'entraînement spécialisé a dégradé les capacités générales
2. **Mesurer** : evals générales avant et après, pas seulement la tâche cible ([[94-evals-methodologie|méthodologie d'évaluation]])
3. **Réduire l'impact** : préférer **LoRA** au full fine-tuning, moins d'époques, taux d'apprentissage plus bas
4. **Mélanger les données** : ajouter des exemples généraux au jeu d'entraînement
5. **Router** : réserver le modèle spécialisé à sa tâche et envoyer le reste au modèle généraliste ([[82-routing-llm|routing]])

**Piège** : juger un fine-tuning sur sa seule métrique cible.

---

## Connexions
- [[21-rag-fondamentaux|RAG]] — connaissances vs comportement
- [[11-prompt-engineering-avance|Prompt engineering]] — l'alternative légère
- [[11-serveurs-inference-llm|Serveurs d'inférence]] — multi-LoRA en serving
- [[62-optimisations-inference|Optimisations]] — quantization (QLoRA)
- [[92-chainforge-evals-prompts|Evals]] — mesurer avant/après
- [[113-monitoring-drift-feedback|Monitoring & drift]] — quand ré-entraîner
- [[68-quantization|Quantization]] — NF4 et les formats de serving
- [[52-post-training-alignement|Post-training & alignement]] — RLHF, DPO, GRPO en détail
- [[53-donnees-synthetiques-distillation|Données synthétiques & distillation]] — générer et distiller
- [[54-entrainement-distribue|Entraînement distribué]] — FSDP, ZeRO, parallélismes
- [[00-moc-ai-engineering|MOC AI Engineering]]
