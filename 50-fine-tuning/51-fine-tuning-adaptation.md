# Fine-tuning & adaptation de modèles — Flashcards
Tags: #flashcards #ai-engineering #fine-tuning #llm
<!-- summary: quand fine-tuner, SFT, full fine-tuning ou PEFT, LoRA, QLoRA, RLHF, DPO, distillation, multi-LoRA (exemple vLLM), catastrophic forgetting et parades. -->


Qu'est-ce que le fine-tuning ? <!--anki:71447a6c7b502c78475d-->
?
**Poursuivre l'entraînement d'un modèle pré-entraîné** sur des données spécifiques, pour adapter son **comportement**, son **format** ou son **domaine**. En pratique, pour une équipe produit : du **SFT** sur quelques centaines à quelques milliers d'exemples, le plus souvent avec **LoRA**.

Il sert à changer **comment** le modèle répond, bien plus qu'à lui apprendre des faits nouveaux, qui relèvent plutôt du [[21-rag-fondamentaux|RAG]].

---

Quand fine-tuner plutôt que prompter ou faire du RAG ? <!--anki:6758606d3f2a7e395547-->
?
Pour un **comportement constant** (format, ton, tâche spécialisée répétitive), la **distillation**, ou raccourcir les [[11-prompt-engineering-avance|prompts]] (latence/coût) — **pas** pour injecter des connaissances fraîches (→ [[21-rag-fondamentaux|RAG]]).

Commencer par une baseline avec prompt et exemples, puis vérifier qu'un jeu d'entraînement représentatif existe. Le fine-tuning devient intéressant quand le même comportement doit se répéter à grande échelle. Conserver un jeu de test indépendant pour mesurer les gains et les régressions, notamment sur les cas rares et hors domaine.

---

Qu'est-ce que le SFT ? <!--anki:6759363b4a296776615b-->
?
**Supervised Fine-Tuning** : entraînement sur des paires **instruction → réponse attendue** de qualité. Le format doit être **exactement celui de l'inférence**, chat template et outils compris ([[132-tokenisation|chat template]]).
```jsonl
{"messages": [
  {"role": "system", "content": "Tu extrais les champs d'une facture en JSON."},
  {"role": "user", "content": "Facture n°A-4471 du 12/03 : 1 240,50 € TTC…"},
  {"role": "assistant", "content": "{\"numero\":\"A-4471\",\"total\":1240.50}"}
]}
```
En entraînement **assistant-only**, on masque la perte sur les consignes pour apprendre les réponses. Ce masquage dépend du collator et de la configuration : le vérifier, car certains pipelines entraînent sur toute la séquence.

---

À ne pas confondre : full fine-tuning et PEFT ? <!--anki:666d6d6977395a684642-->
?
Le **full FT** met à jour tous les poids (coûteux en GPU et stockage) ; le **PEFT** (Parameter-Efficient FT) n'entraîne qu'une **petite fraction de paramètres**.

Le full fine-tuning conserve une grande flexibilité, mais doit stocker gradients et états d'optimiseur pour tous les paramètres entraînés. Une méthode PEFT comme LoRA réduit fortement ces états et permet plusieurs adaptations d'une même base. Le modèle de base reste nécessaire à l'inférence ; le petit adapter ne constitue pas un modèle autonome.

---

Qu'est-ce que LoRA ? <!--anki:634632767854463b7c5a-->
?
**LoRA** gèle une matrice de poids `W` et apprend une correction de bas rang `ΔW = B × A`. Pour une matrice `d × k`, cela entraîne environ `r × (d + k)` paramètres au lieu de `d × k`, avec un rang `r` bien plus petit que les dimensions.

L'adapter réduit mémoire d'entraînement et stockage des variantes, mais sa taille dépend du rang et des couches ciblées : elle peut dépasser quelques dizaines de Mo. Il faut la bonne version du modèle de base pour l'utiliser.

---

Qu'est-ce que QLoRA ? <!--anki:435021656c75503d585b-->
?
**LoRA sur un modèle quantizé en 4-bit** : fine-tuner un gros modèle sur un GPU modeste. Les poids de base restent figés en 4 bits (format NF4), seuls les adapters s'entraînent en précision plus haute ([[68-quantization|NF4]]).

---

De quelles hypothèses dépendent les ressources nécessaires à un fine-tuning ? <!--anki:457b75296778564c6056-->
?
Les ressources dépendent du **modèle, de la longueur des séquences, du batch, de l'optimiseur et des couches adaptées**.
```text
Full FT : poids + gradients + états d'optimiseur + activations
LoRA    : poids gelés + petits paramètres entraînés + activations
QLoRA   : base quantifiée + adapters entraînés + activations
```
À titre d'estimation, un 7B avec un budget de 16 octets par paramètre demande **112 Go hors activations**. Des configurations QLoRA rendent de grands modèles accessibles sur un GPU, sans garantir qu'un 70B tienne avec tout contexte. Mesurer la mémoire maximale et le temps sur un petit entraînement représentatif ; la qualité des exemples reste déterminante.

---

Qu'est-ce que le RLHF ? <!--anki:794a63615d3f7835663e-->
?
**Reinforcement Learning from Human Feedback** : un reward model entraîné sur des préférences humaines guide l'optimisation (PPO) du modèle — la base de l'alignement.

Dans le schéma classique, des humains comparent des réponses, un modèle de récompense apprend ces préférences, puis la politique est optimisée sous contrainte de rester proche d'une référence. La récompense est un proxy : le modèle peut apprendre à plaire au juge sans devenir plus exact. Évaluer les effets sur utilité, factualité et comportements indésirables.

---

Qu'est-ce que DPO ? <!--anki:492f54413476366b5246-->
?
**DPO** apprend à partir de paires de réponses préférée et rejetée pour un même prompt. Son objectif ajuste leurs probabilités relatives par rapport à un modèle de référence, **sans entraîner explicitement un modèle de récompense ni lancer une boucle de RL en ligne**.

Cela simplifie l'entraînement, mais ne garantit pas une meilleure qualité ou stabilité dans tous les cas. Les préférences doivent être cohérentes et représentatives ; des paires biaisées peuvent apprendre la longueur ou le style du gagnant plutôt que la qualité recherchée.

---

Comment obtenir un petit modèle aussi bon qu'un grand sur un domaine précis ? <!--anki:4a2c42346174694d706b-->
?
La **distillation** utilise un grand modèle comme enseignant pour produire des exemples, des distributions ou des signaux de supervision destinés à un plus petit modèle. Sur une tâche étroite, l'élève peut approcher la qualité utile de l'enseignant avec une inférence moins coûteuse.

Ce résultat n'est pas garanti : sélectionner des exemples divers, vérifier les sorties de l'enseignant et tester hors du jeu d'entraînement. Mesurer les cas difficiles et les régressions générales ; les erreurs de l'enseignant peuvent être transmises à l'élève ([[53-donnees-synthetiques-distillation|distillation en détail]]).

---

Comment servir plusieurs fine-tunings à moindre coût ? <!--anki:483c356d3755387d6c25-->
?
Par le **multi-LoRA** : le serveur charge **un seul modèle de base** et, par-dessus, **plusieurs adapters** légers (quelques dizaines à centaines de Mo chacun), choisis **requête par requête** ([[11-serveurs-inference-llm|vLLM]]).
```bash
vllm serve meta-llama/Llama-3.1-8B-Instruct --enable-lora \
  --lora-modules support=./lora-support juridique=./lora-juridique
```
Cent clients avec chacun leur fine-tuning tiennent ainsi sur quelques GPU, au lieu de cent modèles complets.

---

Quel est le principal risque du fine-tuning ? <!--anki:4a72233936695944475e-->
?
Le **catastrophic forgetting** : en s'adaptant à la tâche, le modèle **perd des capacités générales** (raisonnement, suivi d'instructions, refus appropriés, autres langues).

Parades :
- **LoRA** plutôt que full fine-tuning, et un taux d'apprentissage modéré
- **Mélanger** des données générales aux données de la tâche
- **Evals avant/après** sur la tâche **et** sur les capacités générales ([[92-chainforge-evals-prompts|evals]])

---

Calcul : pour une base 7B, comparer la mémoire brute des poids en LoRA avec BF16 et en QLoRA avec 4 bits. Pourquoi ces chiffres ne donnent-ils pas la mémoire totale du fine-tuning ? <!--anki:3337376463643866363135623439663561633937613466613932353937653533-->
?
La **mémoire des poids de base** fournit seulement un point de départ, en Go décimaux :
```text
LoRA, base BF16 : 7e9 × 2 octets = 14 Go
QLoRA, stockage brut 4 bits : 7e9 × 0,5 octet = 3,5 Go
```
Ajouter métadonnées de quantification, adapters, gradients et états d'optimiseur associés, activations et buffers temporaires. Leur coût dépend du rang, des couches ciblées, de la précision, du batch et des séquences. Un GPU de 16 ou 24 Go peut convenir à certaines recettes QLoRA 7B, sans garantie générale. Mesurer le pic mémoire d'un pas représentatif avant de dimensionner.

---

## Mises en situation

Mise en situation : le métier veut fine-tuner un modèle « pour qu'il connaisse nos procédures internes », qui changent chaque mois. Que réponds-tu ? <!--anki:6e332d72382e3d3f492e-->
?
1. **Séparer connaissances et comportement** : des procédures qui changent relèvent du **RAG**, pas du fine-tuning ([[21-rag-fondamentaux|RAG]])
2. **Rappeler le coût du cycle** : chaque mise à jour demanderait un nouvel entraînement, de nouvelles evals et un redéploiement
3. **Ce que le fine-tuning apporterait vraiment** : un format de réponse constant, un ton, une tâche répétitive, des prompts plus courts
4. **Proposer une étape intermédiaire** : prompt soigné plus RAG, mesuré sur un golden dataset
5. **Garder la porte ouverte** : si le format reste instable après optimisation, un fine-tuning léger (LoRA) se justifie

**Piège** : fine-tuner sur des documents internes et croire que le modèle « saura » les citer correctement.

---

Mise en situation : ton modèle fine-tuné est excellent sur l'extraction visée, mais les utilisateurs signalent qu'il répond n'importe quoi aux questions générales. Que s'est-il passé ? <!--anki:6961533e313a76446060-->
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
- [[111-mlops-llmops-fondamentaux|MLOps & LLMOps]] — cycle de vie et versioning des systèmes LLM
- [[114-reproductibilite-variance|Reproductibilité & variance]] — non-déterminisme et statistiques d'evals
- [[151-donnees-curation-annotation|Curation & annotation]] — données de qualité et jeux séparés
- [[55-rl-agentique|RL agentique]] — entraîner un modèle sur des tâches d'agent
- [[66-prefix-caching-radix-attention|Prefix caching]] — réutiliser le calcul des préfixes communs
- [[56-optimisation-diagnostic-entrainement|Optimisation & diagnostic d'entraînement]] — diagnostiquer une adaptation avant de la complexifier
- [[00-moc-ai-engineering|MOC AI Engineering]]
