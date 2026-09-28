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

À ne pas confondre : les leviers qui agissent sur le TTFT et ceux qui agissent sur le TPOT ?
?
```text
TTFT (prefill)          prefix caching, chunked prefill, contexte plus court,
                        désagrégation, plus de calcul
TPOT (decode)           quantization, speculative decoding, GQA, moins de
                        bande passante mémoire consommée
Débit total             continuous batching, batch plus gros, parallélisme
```
Un même changement peut **améliorer l'un et dégrader l'autre** : un gros batch augmente le débit mais allonge le TPOT ([[64-metriques-slo-inference|SLO]]).

---

Qu'est-ce que le continuous batching ?
?
Un batching **au niveau de l'itération** : les requêtes **entrent et sortent du batch à chaque pas de décodage** au lieu d'attendre la plus longue. Le GPU reste plein et le débit est multiplié.
```text
Batch statique : ████████████░░░░░░  4 requêtes, on attend la plus longue
                 ████░░░░░░░░░░░░░░  les GPU tournent à vide (░)
                 ██████████░░░░░░░░

Continuous     : ████████████  → une requête finit, une autre entre aussitôt
                 ████▶▶▶▶▶▶▶▶     le batch est recomposé à chaque token
                 ██████████▶▶
```
C'est la raison principale de l'écart de débit **d'un ordre de grandeur** entre un script Transformers et un serveur comme vLLM ([[11-serveurs-inference-llm|serveurs d'inférence]]).

---

Qu'est-ce que la quantization ?
?
Réduire la **précision des poids** (et parfois des activations) : FP16 → **FP8, INT8, INT4**. Moins de VRAM et de bande passante, donc plus rapide, au prix d'une **légère perte de qualité** ([[68-quantization|quantization]]).

---

Quelles méthodes de quantization courantes ?
?
- **Weight-only** (poids seuls) : **AWQ, GPTQ** (INT4), GGUF pour llama.cpp
- **Poids + activations** : **FP8** (H100 et plus récents), W8A8 INT8
Le weight-only accélère surtout le **decode**, limité par la mémoire.

---

Qu'est-ce que le speculative decoding ?
?
Un **petit modèle « brouillon »** (ou des têtes dédiées, ex. EAGLE) propose plusieurs tokens, que le grand modèle **vérifie en une seule passe**. La sortie suit **la même distribution** que le grand modèle seul (identique en greedy), mais plus vite ([[67-speculative-decoding|speculative decoding]]).

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

## Mises en situation

Mise en situation : ton service d'inférence tient le SLO de latence à faible charge, mais aux heures de pointe le TTFT explose alors que le débit stagne. Quels leviers actionnes-tu ?
?
1. **Diagnostiquer** : file d'attente longue et préemptions pointent vers un manque de capacité KV cache, pas de calcul ([[93-monitoring-inference|métriques]])
2. **Chunked prefill** : les longs prompts n'interrompent plus les décodages en cours, ce qui stabilise la latence inter-token
3. **Quantization** en FP8 : moins de VRAM, donc plus de requêtes simultanées et plus de débit ([[68-quantization|quantization]])
4. **Prefix caching** si les prompts partagent un long préfixe ([[66-prefix-caching-radix-attention|prefix caching]])
5. **Si la charge est structurellement trop forte** : plus de réplicas, ou désagrégation prefill/decode pour régler TTFT et TPOT séparément

**Piège** : augmenter la taille de batch maximale pour « améliorer le débit », et dégrader encore le TTFT.

---

Mise en situation : on te propose de passer de 2 GPU à 4 GPU en tensor parallelism pour accélérer un modèle 70B. Que vérifies-tu avant ?
?
1. **L'interconnect** : le tensor parallelism échange beaucoup entre GPU. Sans NVLink, le gain s'effondre
2. **Ce qu'on cherche** : plus de débit, ou moins de latence ? Le TP réduit la latence, mais au prix d'une efficacité par GPU plus faible
3. **L'alternative** : deux réplicas de 2 GPU donnent souvent plus de débit total qu'un seul réplica de 4
4. **La mémoire** : plus de GPU libère de la VRAM pour le KV cache, donc plus de concurrence
5. **Mesurer** : benchmark de charge sur les deux configurations, à la même distribution de trafic ([[64-metriques-slo-inference|SLO]])

**Piège** : raisonner en FLOPS disponibles et oublier le coût des communications entre GPU.

---

## Connexions
- [[61-kv-cache-attention|KV cache & attention]] — la mémoire que ces techniques gèrent
- [[64-metriques-slo-inference|Métriques & SLO]] — ce qu'on optimise (TTFT, TPOT, débit)
- [[11-serveurs-inference-llm|Serveurs d'inférence]] — où ces optimisations sont implémentées
- [[51-fine-tuning-adaptation|Fine-tuning]] — quantization et QLoRA
- [[12-kubernetes-gpu-inference|Kubernetes GPU]] — multi-GPU en cluster
- [[63-guided-generation|Guided generation]] — contraindre la sortie
- [[65-probabilites-sampling|Probabilités & sampling]] — speculative decoding : même distribution de sortie
- [[114-reproductibilite-variance|Reproductibilité & variance]] — le batching comme source de non-déterminisme
- [[67-speculative-decoding|Speculative decoding]] — la technique en détail
- [[68-quantization|Quantization]] — formats et méthodes en détail
- [[136-mixture-of-experts|Mixture of Experts]] — expert parallelism
- [[54-entrainement-distribue|Entraînement distribué]] — les mêmes parallélismes à l'entraînement
- [[00-moc-ai-engineering|MOC AI Engineering]]
