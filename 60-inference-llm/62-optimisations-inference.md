# Optimisations d'inférence — Flashcards
Tags: #flashcards #ai-engineering #inference #optimisation #llm

Quelles sont les deux phases de l'inférence d'un LLM ?
?
- **Prefill** : traitement de **tout le prompt en parallèle** → produit le premier token et remplit le [[61-kv-cache-attention|KV cache]]
- **Decode** : génération **token par token**, chacun dépendant du précédent

---

Pourquoi prefill et decode ont-ils des goulots différents ?
?
Le **prefill** est **compute-bound** (beaucoup de calcul matriciel en parallèle) ; le **decode** est **memory-bandwidth-bound** (on relit tous les poids et le KV cache pour produire **un seul** token).

---

Qu'est-ce que le continuous batching ?
?
Un batching **au niveau de l'itération** : les requêtes **entrent et sortent du batch à chaque pas de décodage** au lieu d'attendre la plus longue. Le GPU reste plein et le débit est multiplié.

---

Qu'est-ce que la quantization ?
?
Réduire la **précision des poids** (et parfois des activations) : FP16 → **FP8, INT8, INT4**. Moins de VRAM et de bande passante, donc plus rapide, au prix d'une **légère perte de qualité**.

---

Quelles méthodes de quantization courantes ?
?
- **Weight-only** (poids seuls) : **AWQ, GPTQ** (INT4), GGUF pour llama.cpp
- **Poids + activations** : **FP8** (H100 et plus récents), W8A8 INT8
Le weight-only accélère surtout le **decode**, limité par la mémoire.

---

Qu'est-ce que le speculative decoding ?
?
Un **petit modèle « brouillon »** (ou des têtes dédiées, ex. EAGLE) propose plusieurs tokens, que le grand modèle **vérifie en une seule passe**. La sortie est **identique** à celle du grand modèle, mais plus rapide.

---

Qu'est-ce que FlashAttention ?
?
Une implémentation de l'attention **consciente de la hiérarchie mémoire du GPU** (calcul par tuiles en SRAM) : **résultat exact**, beaucoup moins d'accès à la HBM, donc plus rapide et moins gourmande en mémoire.

---

Tensor parallelism ou pipeline parallelism ?
?
- **Tensor parallelism** : chaque couche est **découpée entre plusieurs GPU** (demande un interconnect rapide type **NVLink**)
- **Pipeline parallelism** : les **couches sont réparties** par étages sur plusieurs GPU ou nœuds

---

Qu'est-ce que le chunked prefill ?
?
Découper un long prefill **en morceaux mélangés aux decodes** en cours : un gros prompt n'**interrompt plus** la génération des autres requêtes (latence inter-token plus stable).

---

Qu'est-ce que la désagrégation prefill/decode ?
?
Exécuter prefill et decode sur des **pools de GPU séparés**, avec transfert du KV cache entre eux : chaque pool est dimensionné pour son goulot et on optimise **TTFT et TPOT** indépendamment.

---

## Connexions
- [[61-kv-cache-attention|KV cache & attention]] — la mémoire que ces techniques gèrent
- [[64-metriques-slo-inference|Métriques & SLO]] — ce qu'on optimise (TTFT, TPOT, débit)
- [[11-serveurs-inference-llm|Serveurs d'inférence]] — où ces optimisations sont implémentées
- [[51-fine-tuning-adaptation|Fine-tuning]] — quantization et QLoRA
- [[12-kubernetes-gpu-inference|Kubernetes GPU]] — multi-GPU en cluster
- [[63-guided-generation|Guided generation]] — contraindre la sortie
- [[00-moc-ai-engineering|MOC AI Engineering]]
