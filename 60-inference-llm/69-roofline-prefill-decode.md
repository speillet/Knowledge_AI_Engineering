# Roofline, prefill/decode & désagrégation — Flashcards
Tags: #flashcards #ai-engineering #inference #gpu #performance #llm
Vérifié le : 29 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.

Qu'est-ce que l'intensité arithmétique ?
?
<!--anki:4e682e414f26342b616d-->
Le nombre d'**opérations de calcul par octet lu en mémoire** (FLOP/octet). Elle dit ce qui limite un calcul :
- **Faible** : le GPU attend les données, le calcul est limité par la **bande passante mémoire**
- **Élevée** : les données sont réutilisées beaucoup, le calcul est limité par la **puissance de calcul**

---

Qu'est-ce que le modèle roofline ?
?
<!--anki:734d2b432465463e4639-->
Un graphe qui donne la **performance maximale atteignable** selon l'intensité arithmétique : une pente (limite de bande passante) puis un plafond (limite de calcul). Le point de bascule, le **ridge point**, vaut **puissance de calcul / bande passante**.
```text
H100 SXM : ≈ 989 TFLOP/s (BF16 dense) / ≈ 3,35 To/s ≈ 300 FLOP/octet
en dessous de ~300 FLOP/octet : memory-bound
au-dessus                     : compute-bound
```

---

À ne pas confondre : memory-bound et compute-bound ?
?
<!--anki:6a6f7d6d386152727063-->
- **Memory-bound** : le temps est dicté par les **octets à lire**. On accélère en lisant moins (quantization, cache plus petit) ou en réutilisant chaque lecture (batch plus gros)
- **Compute-bound** : le temps est dicté par les **FLOP**. On accélère avec plus de calcul (GPU plus puissant, FP8 natif, parallélisme) ou moins d'opérations

Optimiser le mauvais côté ne sert à rien : quantizer les poids accélère peu un prefill compute-bound.

---

Pourquoi le prefill est-il compute-bound et le decode memory-bound ?
?
<!--anki:6d6f476d2f5178315951-->
- **Prefill** : tous les tokens du prompt passent **en parallèle**. Chaque poids lu sert à des **milliers de tokens**, donc l'intensité est élevée
- **Decode** : un **seul token** par séquence et par étape. Chaque poids lu ne sert qu'à **B tokens** (la taille du batch), donc l'intensité vaut à peu près **B FLOP/octet** en BF16

À batch 1, le decode est donc **~300 fois sous** le ridge point d'un H100 : le GPU passe son temps à lire des poids ([[62-optimisations-inference|optimisations]]).

---

Calcul : quelle vitesse maximale de decode pour un 70B en FP8 sur un H100, à batch 1 ?
?
<!--anki:6e584d7a536d48573540-->
Chaque token relit **tous les poids** :
```text
poids 70B en FP8                ≈ 70 Go
bande passante H100 SXM         ≈ 3,35 To/s
débit max ≈ 3 350 / 70          ≈ 48 tokens/s (plafond théorique)
```
En pratique 70 à 80 % de ce plafond. Même raisonnement pour un poste local ([[164-llm-local-edge|LLM locaux]]). Pour aller plus vite par séquence : moins d'octets ([[68-quantization|quantization]]) ou plusieurs tokens par lecture ([[67-speculative-decoding|speculative decoding]]).

---

Calcul : combien de temps prend le prefill de 10 000 tokens sur un modèle 8B ?
?
<!--anki:7326283a603b30342373-->
Un passage avant coûte **≈ 2 × N FLOP par token** :
```text
2 × 8e9 × 10 000       = 1,6e14 FLOP
H100 à ~50 % de MFU    ≈ 5e14 FLOP/s utiles
temps                  ≈ 0,3 s de TTFT (hors file d'attente)
```
Le coût de l'attention s'ajoute et croît avec le **carré** de la longueur : à 100 000 tokens, il devient dominant ([[137-long-contexte|long contexte]]).

---

Pourquoi augmenter le batch en decode est-il presque gratuit, jusqu'à un certain point ?
?
<!--anki:42785655476759424b2d-->
En decode, lire les poids coûte le même temps pour **1 ou 64 séquences** : chaque séquence ajoutée réutilise la même lecture. Le débit total monte presque **linéairement** avec le batch, tandis que le TPOT de chaque séquence bouge peu.

La limite arrive par la **mémoire du KV cache** (chaque séquence y occupe sa place) et parce que l'**attention**, elle, relit le cache propre à chaque séquence et reste memory-bound ([[61-kv-cache-attention|KV cache]]).

---

Pourquoi l'utilisation GPU de `nvidia-smi` est-elle trompeuse ?
?
<!--anki:48423f5d56613037636e-->
Elle mesure la **part du temps où un kernel tourne**, pas la part de la puissance utilisée. Un decode memory-bound affiche **100 %** d'utilisation en exploitant quelques pourcents des FLOP disponibles. Pour juger l'efficacité : **débit en tokens/s**, **MFU** (FLOP utiles / FLOP théoriques) ou bande passante atteinte, via DCGM ou un profileur ([[93-monitoring-inference|monitoring]]).

---

Pourquoi prefill et decode se gênent-ils sur le même GPU ?
?
<!--anki:4d7676625e503c7a2859-->
Un gros prefill **monopolise le GPU** pendant des centaines de millisecondes : les séquences en decode du même batch **attendent**, d'où des **pics de TPOT** visibles par les utilisateurs en cours de génération. Inversement, beaucoup de decodes ralentissent l'admission des nouveaux prompts et dégradent le **TTFT**.

Les deux phases ont des goulots différents (calcul et mémoire) mais partagent la même machine.

---

À ne pas confondre : chunked prefill et désagrégation prefill/decode ?
?
<!--anki:7a5e5671384259417430-->
- **Chunked prefill** : découpe un long prefill en **morceaux** intercalés avec les decodes, **sur le même GPU**. Lisse le TPOT, sans infrastructure supplémentaire. Activé par défaut dans vLLM
- **Désagrégation** : prefill et decode tournent sur des **pools de GPU séparés**, et le KV cache est **transféré** de l'un à l'autre. Chaque pool se dimensionne pour son goulot, au prix d'un réseau rapide et d'une orchestration plus complexe

On commence par le premier ; le second se justifie à grande échelle.

---

Comment fonctionne un déploiement désagrégé en pratique ?
?
<!--anki:4d6b2467737e6a413962-->
1. Un **routeur** envoie le prompt à un worker de **prefill**, choisi selon la charge et le cache de préfixes ([[66-prefix-caching-radix-attention|routage cache-aware]])
2. Le prefill calcule le KV cache et le **transfère** vers un worker de **decode** par NVLink ou RDMA (bibliothèques comme NIXL)
3. Le worker de decode génère la suite
4. Les deux pools **s'autoscalent séparément** : plus de prefill si les prompts s'allongent, plus de decode si les réponses s'allongent

Implémentations : NVIDIA Dynamo, llm-d sur Kubernetes, modes désagrégés de vLLM et SGLang ([[12-kubernetes-gpu-inference|Kubernetes GPU]]).

---

Quand la désagrégation vaut-elle son coût ?
?
<!--anki:446d467a673160625b32-->
- **Grande échelle** : plusieurs nœuds par modèle, où le gain d'utilisation compense la complexité
- **Prompts longs** (RAG, agents) avec des **SLO stricts à la fois** sur TTFT et TPOT
- **Réseau rapide** entre les GPU : sans RDMA ou NVLink, le transfert du KV cache mange le gain

Pour un ou deux GPU, chunked prefill et un bon réglage du batch suffisent ([[64-metriques-slo-inference|SLO]]).

---

## Mises en situation

Mise en situation : ton serveur vLLM affiche 100 % d'utilisation GPU, mais un seul utilisateur obtient 25 tokens/s sur un 70B en BF16, sur deux H100 en tensor parallelism. Ton responsable demande deux GPU de plus. Qu'analyses-tu ?
?
<!--anki:67466b7a5a43452e713c-->
1. **Calculer le plafond** : 140 Go de poids lus à chaque token sur 2 × 3,35 To/s, soit ≈ 48 tokens/s au mieux. 25 tokens/s n'a rien d'anormal
2. **Relativiser l'indicateur** : 100 % d'utilisation signifie que des kernels tournent, pas que le calcul est saturé
3. **Viser le bon goulot** : quantizer en FP8 divise par deux les octets lus ([[68-quantization|quantization]]), le speculative decoding produit plusieurs tokens par lecture ([[67-speculative-decoding|speculative decoding]])
4. **Mesurer à charge réelle** : à 30 utilisateurs, le débit total monte fortement grâce au batch ([[64-metriques-slo-inference|SLO]])
5. **Ajouter des GPU seulement si** le SLO n'est pas tenu à la charge cible après ces leviers

**Piège** : acheter du calcul pour un problème de bande passante mémoire.

---

Mise en situation : sur ton RAG, les réponses « bégaient » : le texte s'arrête une demi-seconde en pleine génération, surtout aux heures de pointe. Le TTFT moyen est correct. Que diagnostiques-tu ?
?
<!--anki:6e51482c402857432865-->
1. **Relier aux métriques** : des pics de TPOT au p99 alors que la moyenne va bien ([[64-metriques-slo-inference|percentiles]])
2. **Suspecter l'interférence** : les longs prompts RAG (10 000 tokens et plus) passent en prefill et bloquent les decodes en cours
3. **Activer ou régler le chunked prefill** : taille des morceaux, part du budget de tokens par étape
4. **Réduire les prompts** : moins de chunks, reranking plus sélectif ([[25-chunking-contextual-retrieval|chunking]])
5. **À grande échelle seulement**, envisager la désagrégation prefill/decode

**Piège** : augmenter la taille de batch pour absorber la pointe, ce qui allonge encore chaque étape de decode.

---

## Sources

- [NVIDIA — Dynamo, inférence distribuée](https://docs.nvidia.com/dynamo/latest/)

## Connexions
- [[62-optimisations-inference|Optimisations d'inférence]] — les leviers par phase
- [[61-kv-cache-attention|KV cache & attention]] — ce que le decode relit et transfère
- [[64-metriques-slo-inference|Métriques & SLO]] — TTFT, TPOT, percentiles
- [[68-quantization|Quantization]] — moins d'octets par token
- [[67-speculative-decoding|Speculative decoding]] — plusieurs tokens par lecture des poids
- [[66-prefix-caching-radix-attention|Prefix caching]] — le routage devant un déploiement désagrégé
- [[135-pretraining-scaling-laws|Pré-entraînement]] — MFU et loi 6ND
- [[12-kubernetes-gpu-inference|Kubernetes GPU & inférence]] — llm-d et l'autoscaling par pool
- [[11-serveurs-inference-llm|Serveurs d'inférence]] — vLLM, SGLang, TensorRT-LLM et leur réglage
- [[22-rag-avance|RAG — Avancé]] — recherche hybride, reranking et filtres
- [[00-moc-ai-engineering|MOC AI Engineering]]
