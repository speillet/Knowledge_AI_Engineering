# Roofline, prefill/decode & désagrégation — Flashcards
Tags: #flashcards #ai-engineering #inference #gpu #performance #llm
Vérifié le : 29 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.
<!-- summary: intensité arithmétique, modèle roofline, memory-bound ou compute-bound, calculs de débit de decode et de durée de prefill, batch en decode, limites de l'utilisation GPU, interférence prefill/decode, chunked prefill ou désagrégation, déploiement désagrégé (Dynamo, llm-d), quand désagréger, coût et recouvrement des transferts KV. -->


Qu'est-ce que l'intensité arithmétique ? <!--anki:4e682e414f26342b616d-->
?
Le nombre d'**opérations de calcul par octet lu en mémoire** (FLOP/octet). Elle dit ce qui limite un calcul :
- **Faible** : le GPU attend les données, le calcul est limité par la **bande passante mémoire**
- **Élevée** : les données sont réutilisées beaucoup, le calcul est limité par la **puissance de calcul**

---

Qu'est-ce que le modèle roofline ? <!--anki:734d2b432465463e4639-->
?
Un graphe qui donne la **performance maximale atteignable** selon l'intensité arithmétique : une pente (limite de bande passante) puis un plafond (limite de calcul). Le point de bascule, le **ridge point**, vaut **puissance de calcul / bande passante**.
```text
H100 SXM : ≈ 989 TFLOP/s (BF16 dense) / ≈ 3,35 To/s ≈ 300 FLOP/octet
en dessous de ~300 FLOP/octet : memory-bound
au-dessus                     : compute-bound
```

---

À ne pas confondre : memory-bound et compute-bound ? <!--anki:6a6f7d6d386152727063-->
?
- **Memory-bound** : le temps est dicté par les **octets à lire**. On accélère en lisant moins (quantization, cache plus petit) ou en réutilisant chaque lecture (batch plus gros)
- **Compute-bound** : le temps est dicté par les **FLOP**. On accélère avec plus de calcul (GPU plus puissant, FP8 natif, parallélisme) ou moins d'opérations

Optimiser le mauvais côté ne sert à rien : quantizer les poids accélère peu un prefill compute-bound.

---

Pourquoi le prefill est-il compute-bound et le decode memory-bound ? <!--anki:6d6f476d2f5178315951-->
?
Dans les couches linéaires d'un modèle dense, le **prefill** réutilise les poids pour de nombreux tokens ; le **decode à petit batch** les réutilise beaucoup moins. En BF16, le modèle simplifié donne environ `B FLOP/octet` pour un batch de B tokens.

Cela explique un régime souvent limité par le calcul au prefill et par la mémoire au decode. L'attention longue, les kernels, les communications et les architectures MoE ou hybrides peuvent déplacer le goulot. Le rapport au ridge point décrit une intensité théorique ; ce n'est pas directement le pourcentage de FLOP réellement utilisé.

---

Calcul : quelle vitesse maximale de decode pour un 70B en FP8 sur un H100, à batch 1 ? <!--anki:6e584d7a536d48573540-->
?
Modèle dense, poids FP8 lus une fois par token, batch 1 et bande passante théorique :
```text
poids ≈ 70 Go ; bande passante supposée ≈ 3,35 To/s
plafond dû aux seules lectures de poids ≈ 3 350 / 70 ≈ 48 tokens/s
```
Ce n'est ni une mesure ni une garantie qu'un déploiement complet tient sur la carte. Ajouter KV, échelles, activations et réserves ; attention, calcul, lancements et transferts diminuent le débit réel. Sans mesure, ne pas annoncer un pourcentage fixe du plafond. La quantification réduit les octets ; la spéculation peut amortir une lecture sur plusieurs tokens validés.

---

Calcul : combien de temps prend le prefill de 10 000 tokens sur un modèle 8B ? <!--anki:7326283a603b30342373-->
?
Pour les couches linéaires d'un modèle dense, utiliser l'approximation `2 × paramètres × tokens` :
```text
2 × 8e9 × 10 000 = 1,6e14 FLOP
hypothèse de débit utile : 5e14 FLOP/s
durée estimée de cette composante = 0,32 s
```
Le débit utile choisi est une **hypothèse**, pas un rendement garanti du GPU. Ajouter attention, frais du moteur, attente et transport pour obtenir un TTFT. L'attention dense croît quadratiquement au prefill ; la longueur à laquelle elle domine dépend de l'architecture, du batch et des kernels, sans seuil universel à 100 000 tokens.

---

Pourquoi augmenter le batch peut-il améliorer fortement le débit du decode ? <!--anki:42785655476759424b2d-->
?
Dans un régime où la **lecture des poids domine**, plusieurs séquences réutilisent ces lectures et augmentent l'intensité arithmétique. Le débit agrégé peut alors progresser beaucoup plus vite que la durée d'une itération.

Le gain n'est pas gratuit : calcul, activations et lectures KV augmentent aussi, surtout à long contexte. Au-delà d'un certain batch, calcul, mémoire ou communications saturent et le TPOT se dégrade. Mesurer la courbe de charge sur le workload visé ; ne pas supposer qu'une itération à 64 séquences coûte autant qu'à une séquence.

---

Pourquoi l'utilisation GPU de `nvidia-smi` est-elle trompeuse ? <!--anki:48423f5d56613037636e-->
?
Elle mesure la **part du temps où un kernel tourne**, pas la part de la puissance utilisée. Un decode memory-bound affiche **100 %** d'utilisation en exploitant quelques pourcents des FLOP disponibles. Pour juger l'efficacité : **débit en tokens/s**, **MFU** (FLOP utiles / FLOP théoriques) ou bande passante atteinte, via DCGM ou un profileur ([[93-monitoring-inference|monitoring]]).

---

Pourquoi prefill et decode se gênent-ils sur le même GPU ? <!--anki:4d7676625e503c7a2859-->
?
Un gros prefill **monopolise le GPU** pendant des centaines de millisecondes : les séquences en decode du même batch **attendent**, d'où des **pics de TPOT** visibles par les utilisateurs en cours de génération. Inversement, beaucoup de decodes ralentissent l'admission des nouveaux prompts et dégradent le **TTFT**.

Les deux phases ont des goulots différents (calcul et mémoire) mais partagent la même machine.

---

À ne pas confondre : chunked prefill et désagrégation prefill/decode ? <!--anki:7a5e5671384259417430-->
?
- **Chunked prefill** : découpe un long prefill en **morceaux** intercalés avec les decodes, **sur le même GPU**. Lisse le TPOT, sans infrastructure supplémentaire. Activé par défaut quand possible dans vLLM V1
- **Désagrégation** : prefill et decode tournent sur des **pools de GPU séparés**, et le KV cache est **transféré** de l'un à l'autre. Chaque pool se dimensionne pour son goulot, au prix d'un réseau rapide et d'une orchestration plus complexe

On commence par le premier ; le second se justifie à grande échelle.

---

Comment fonctionne un déploiement désagrégé en pratique ? <!--anki:4d6b2467737e6a413962-->
?
1. Un **routeur** envoie le prompt à un worker de **prefill**, choisi selon la charge et le cache de préfixes ([[66-prefix-caching-radix-attention|routage cache-aware]])
2. Le prefill calcule le KV cache et le **transfère** vers un worker de **decode** par NVLink ou RDMA (bibliothèques comme NIXL)
3. Le worker de decode génère la suite
4. Les deux pools **s'autoscalent séparément** : plus de prefill si les prompts s'allongent, plus de decode si les réponses s'allongent

Implémentations : NVIDIA Dynamo, llm-d sur Kubernetes, modes désagrégés de vLLM et SGLang ([[12-kubernetes-gpu-inference|Kubernetes GPU]]).

---

Quand la désagrégation vaut-elle son coût ? <!--anki:446d467a673160625b32-->
?
Quand la séparation prefill/decode améliore suffisamment le **goodput sous SLO** pour payer transferts KV, routage et capacité réservée dans chaque pool. Les longs prompts mélangés aux streams sensibles à l'ITL sont un cas à étudier.

Mesurer volume transféré, bande passante effective, synchronisation, files des deux pools et déséquilibre de charge. Comparer à une configuration colocalisée bien réglée, notamment avec chunked prefill. La taille du cluster seule ne décide pas : un réseau rapide peut rester insuffisant, et une séparation peut réduire l'utilisation si un pool attend l'autre.

---

Calcul : quel coût minimal pour transférer 2 Gio de KV sur un lien à 25 Gio/s ? <!--anki:6236376139316165393166343439383339353764656438636464656336643633-->
?
Sans recouvrement ni contention, la composante de transfert vaut `2 / 25 = 0,08 s`, soit **80 ms**. Ajouter préparation, synchronisation et attente avant de comparer à un gain de calcul.

Si la séparation économise seulement 50 ms sur le chemin critique, un transfert supplémentaire non masqué de 80 ms annule ce gain. Avec recouvrement, mesurer la partie réellement exposée plutôt qu'additionner aveuglément les durées. À plusieurs requêtes simultanées, la bande passante est partagée : le temps d'une requête isolée ne démontre pas le comportement sous charge.

---

## Mises en situation

Mise en situation : ton serveur vLLM affiche 100 % d'utilisation GPU, mais un seul utilisateur obtient 25 tokens/s sur un 70B en BF16, sur deux H100 en tensor parallelism. Ton responsable demande deux GPU de plus. Qu'analyses-tu ? <!--anki:67466b7a5a43452e713c-->
?
1. **Calculer le plafond** : 140 Go de poids lus à chaque token sur 2 × 3,35 To/s, soit ≈ 48 tokens/s au mieux. 25 tokens/s n'a rien d'anormal
2. **Relativiser l'indicateur** : 100 % d'utilisation signifie que des kernels tournent, pas que le calcul est saturé
3. **Viser le bon goulot** : quantizer en FP8 divise par deux les octets lus ([[68-quantization|quantization]]), le speculative decoding produit plusieurs tokens par lecture ([[67-speculative-decoding|speculative decoding]])
4. **Mesurer à charge réelle** : à 30 utilisateurs, le débit total monte fortement grâce au batch ([[64-metriques-slo-inference|SLO]])
5. **Ajouter des GPU seulement si** le SLO n'est pas tenu à la charge cible après ces leviers

**Piège** : acheter du calcul pour un problème de bande passante mémoire.

---

Mise en situation : sur ton RAG, les réponses « bégaient » : le texte s'arrête une demi-seconde en pleine génération, surtout aux heures de pointe. Le TTFT moyen est correct. Que diagnostiques-tu ? <!--anki:6e51482c402857432865-->
?
1. **Relier aux métriques** : des pics d’ITL au p99 alors que la moyenne va bien ([[64-metriques-slo-inference|percentiles]])
2. **Suspecter l'interférence** : les longs prompts RAG (10 000 tokens et plus) passent en prefill et bloquent les decodes en cours
3. **Activer ou régler le chunked prefill** : taille des morceaux, part du budget de tokens par étape
4. **Réduire les prompts** : moins de chunks, reranking plus sélectif ([[25-chunking-contextual-retrieval|chunking]])
5. **À grande échelle seulement**, envisager la désagrégation prefill/decode

**Piège** : augmenter la taille de batch pour absorber la pointe, ce qui allonge encore chaque étape de decode.

---

## Sources

- [DistServe — séparation et coût des transferts](https://arxiv.org/abs/2401.09670)


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
