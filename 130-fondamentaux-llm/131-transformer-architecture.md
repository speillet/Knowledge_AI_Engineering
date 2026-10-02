# Architecture Transformer — Flashcards
Tags: #flashcards #ai-engineering #fondamentaux #transformer #llm
<!-- summary: chemin d'un token, attention, attention causale, multi-head, GQA et MQA, bloc MLP, résiduelles et normalisation, RoPE, coût quadratique, calcul de la mémoire des poids d'un 70B, decoder-only ou encoder, modèle de base ou assistant. -->


Qu'est-ce qu'un LLM, mécaniquement ? <!--anki:7074663b5a51392c4f44-->
?
Un réseau **Transformer decoder-only** entraîné à **prédire le token suivant**. À chaque pas, il produit une **distribution de probabilités** sur le vocabulaire ; la génération consiste à **échantillonner** un token, l'ajouter à l'entrée et recommencer ([[65-probabilites-sampling|sampling]]).

---

Quel est le chemin d'un token dans le modèle ? <!--anki:6f2477294b6c522a233e-->
?
1. **Tokenisation** → identifiant ([[132-tokenisation|tokenizer]]).
2. **Embedding** : l'id devient un vecteur de dimension d (ex. 4 096).
3. **N blocs Transformer** empilés (attention + MLP), qui enrichissent ce vecteur avec le contexte.
4. **Normalisation finale** puis **projection** vers le vocabulaire → **logits**.
5. **Softmax** → probabilités du token suivant.

---

Que fait le mécanisme d'attention ? <!--anki:4971286368426d485451-->
?
Chaque token calcule une **query (Q)**, une **key (K)** et une **value (V)**. Le score entre deux tokens est **Q·K / √d** ; après softmax, ces scores pondèrent les **V**. Chaque token **agrège ainsi l'information des tokens pertinents** du contexte :
```text
Attention(Q, K, V) = softmax(Q·Kᵀ / √d_k) · V
```

---

Qu'est-ce que l'attention causale ? <!--anki:46472b6d792b493b2826-->
?
Un **masque** qui empêche chaque token de voir les **tokens futurs** : le token i n'attend qu'aux positions ≤ i. C'est ce qui permet d'entraîner la prédiction du token suivant **sur toutes les positions en parallèle**, et de réutiliser les K/V passés à l'inférence ([[61-kv-cache-attention|KV cache]]).

---

Pourquoi plusieurs têtes d'attention (multi-head) ? <!--anki:70495d3d7d324e5e5848-->
?
Chaque tête a ses propres projections Q/K/V et peut se spécialiser dans **un type de relation** (syntaxe, coréférence, position proche…). Les sorties des têtes sont **concaténées** puis reprojetées.

---

Qu'est-ce que GQA et MQA, et pourquoi comptent-ils en production ? <!--anki:6a72557e65666e265368-->
?
- **MQA** (Multi-Query Attention) : toutes les têtes de query **partagent une seule paire K/V**.
- **GQA** (Grouped-Query Attention) : les têtes sont groupées, **un K/V par groupe**.

Ils divisent la **taille du KV cache** (donc la mémoire par requête) avec une perte de qualité faible → plus de requêtes en parallèle. La plupart des modèles récents utilisent GQA ; d'autres compressent le cache autrement (MLA chez DeepSeek).

---

Quel est le rôle du bloc MLP (feed-forward) ? <!--anki:6b6439385d5d4f3b3945-->
?
Après l'attention (qui **mélange l'information entre tokens**), le MLP **transforme chaque token indépendamment**. Il contient **la majorité des paramètres** et on considère qu'il stocke une grande part des **connaissances factuelles**. C'est lui qu'on remplace par des experts dans un [[136-mixture-of-experts|MoE]].

---

À quoi servent les connexions résiduelles et la normalisation ? <!--anki:7a416e26656a2b364877-->
?
- **Résiduelles** : chaque bloc **ajoute** sa sortie à son entrée (x + f(x)) — le gradient traverse des dizaines de couches sans s'éteindre.
- **Normalisation** (RMSNorm, en **pre-norm** avant chaque sous-bloc) : stabilise l'entraînement.

---

Comment le modèle connaît-il la position des tokens ? <!--anki:637e3955546a4c492f2d-->
?
L'attention seule est **insensible à l'ordre**. On injecte la position, aujourd'hui surtout par **RoPE** (Rotary Position Embedding) : Q et K sont **tournés d'un angle dépendant de la position**, si bien que le score dépend de la **distance relative**. RoPE est au cœur des techniques d'[[137-long-contexte|extension de contexte]].

---

Pourquoi l'attention coûte-t-elle cher sur les contextes longs ? <!--anki:76402d59655d2e3c2977-->
?
Le calcul des scores est **quadratique** en longueur de séquence (n² paires) pendant le **prefill**, et le **KV cache** grandit **linéairement** avec le contexte. FlashAttention réduit le coût **mémoire** et les accès HBM, pas la complexité ([[62-optimisations-inference|optimisations]]).

---

Calcul : quelle mémoire pour les poids d'un modèle 70B ? <!--anki:623b687d595d6121635b-->
?
**Nombre de paramètres × octets par paramètre** :
```text
70B en BF16 (2 octets)   ≈ 140 Go → deux H100 80 Go au minimum
70B en FP8  (1 octet)    ≈  70 Go
70B en INT4 (~0,5 octet) ≈  35-40 Go
```
Il faut ajouter le **KV cache** et les activations, souvent plusieurs dizaines de Go de plus en serving ([[68-quantization|quantization]], [[61-kv-cache-attention|KV cache]]).

---

À ne pas confondre : decoder-only, encoder-only et encoder-decoder ? <!--anki:42425b217d782c423c4b-->
?
- **Decoder-only** (GPT, Llama, Claude) : attention causale, **génération** — le standard des LLM.
- **Encoder-only** (BERT) : attention **bidirectionnelle**, pas de génération — utilisé pour la **classification**, les **embeddings** et les **rerankers**.
- **Encoder-decoder** (T5) : un encodeur lit l'entrée, un décodeur génère — traduction, résumé.

---

Pourquoi un modèle de base ne suit-il pas les instructions ? <!--anki:656e4e215b5455584f68-->
?
Le pré-entraînement lui apprend à **continuer du texte**, pas à **répondre** : face à une question, il peut la prolonger par d'autres questions. Le suivi d'instructions vient du **post-training** (SFT, puis alignement par préférences) — voir [[52-post-training-alignement|post-training]].

---

## Mises en situation

Mise en situation : on te demande combien de GPU prévoir pour servir un modèle 70B avec 16 000 tokens de contexte et 50 utilisateurs simultanés. Comment raisonnes-tu à voix haute ? <!--anki:4c256b2c707933653264-->
?
1. **Les poids d'abord** : 70 milliards de paramètres × 2 octets en BF16 ≈ **140 Go**, donc deux GPU de 80 Go ne laissent presque rien
2. **Le KV cache ensuite** : proportionnel au contexte, au nombre de couches et de têtes KV, et au **nombre de requêtes simultanées** ([[61-kv-cache-attention|KV cache]])
3. **Réduire** : quantization FP8 ou INT4 des poids, cache en FP8, GQA déjà présent dans la plupart des modèles récents
4. **Vérifier par la mesure** : un benchmark de charge, pas seulement un calcul ([[64-metriques-slo-inference|SLO]])
5. **Annoncer une fourchette** et les hypothèses qui la sous-tendent

**Piège** : ne dimensionner que sur la taille des poids, en oubliant le cache, qui décide de la concurrence.

---

Mise en situation : en entretien, on te demande pourquoi un modèle de base répond mal aux questions alors qu'il a « lu tout internet ». Que réponds-tu ? <!--anki:433e282a5721372b5575-->
?
1. **Objectif d'entraînement** : il apprend à **continuer du texte**, pas à répondre. Il peut prolonger une question par d'autres questions
2. **Ce qui crée l'assistant** : le post-training, d'abord supervisé, puis par préférences ([[52-post-training-alignement|post-training]])
3. **Conséquence pratique** : un modèle « base » sur Hugging Face ne s'utilise pas comme un modèle « instruct »
4. **Chat template** : les modèles instruits attendent un format précis, sans lequel la qualité chute ([[132-tokenisation|chat template]])
5. **Nuance** : le pré-entraînement détermine les connaissances et les capacités, le post-training le comportement

**Piège** : conclure qu'un modèle est mauvais alors qu'on utilise une variante de base ou un mauvais gabarit de conversation.

---

## Connexions
- [[132-tokenisation|Tokenisation]] — l'entrée du modèle
- [[135-pretraining-scaling-laws|Pré-entraînement & scaling laws]] — comment on l'entraîne
- [[136-mixture-of-experts|Mixture of Experts]] — remplacer le MLP par des experts
- [[137-long-contexte|Long contexte]] — RoPE et ses extensions
- [[61-kv-cache-attention|KV cache & attention]] — l'attention à l'inférence
- [[65-probabilites-sampling|Probabilités & sampling]] — des logits au token
- [[133-embeddings-representations|Embeddings]] — représenter le sens par des vecteurs
- [[161-modeles-vision-langage|Modèles vision-langage]] — images et écrans en entrée
- [[22-rag-avance|RAG — Avancé]] — recherche hybride, reranking et filtres
- [[00-moc-ai-engineering|MOC AI Engineering]]
