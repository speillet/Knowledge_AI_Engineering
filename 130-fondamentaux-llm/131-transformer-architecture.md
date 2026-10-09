# Architecture Transformer — Flashcards
Tags: #flashcards #ai-engineering #fondamentaux #transformer #llm
<!-- summary: chemin d'un token, attention, attention causale, multi-head, GQA et MQA, bloc MLP, résiduelles et normalisation, RoPE, coût quadratique, calcul de la mémoire des poids d'un 70B, decoder-only ou encoder, modèle de base ou assistant. -->


Qu'est-ce qu'un LLM, mécaniquement ? <!--anki:7074663b5a51392c4f44-->
?
Un **LLM** est un modèle de langage de grande taille. Dans le cas courant d'un **Transformer autorégressif decoder-only**, il estime la distribution du prochain token à partir du préfixe. La génération choisit un token, l'ajoute au contexte et répète l'opération ([[65-probabilites-sampling|sampling]]).

Cette description explique les modèles génératifs étudiés ici ; elle ne définit pas toutes les architectures de modèles de langage. Encoder-decoder, modèles hybrides et autres objectifs d'entraînement existent. Les probabilités portent sur les tokens, pas directement sur la vérité des affirmations.

---

Quel est le chemin d'un token dans un Transformer génératif decoder-only ? <!--anki:6f2477294b6c522a233e-->
?
1. **Tokenisation** → identifiant ([[132-tokenisation|tokenizer]]).
2. **Embedding** : l'id devient un vecteur de dimension d (ex. 4 096).
3. **N blocs Transformer** empilés (attention + MLP), qui enrichissent ce vecteur avec le contexte.
4. **Normalisation finale** puis **projection** vers le vocabulaire → **logits**.
5. **Softmax** → probabilités du token suivant.

---

Que fait le mécanisme d'attention ? <!--anki:4971286368426d485451-->
?
L'attention utilise une **requête Q** pour pondérer des **valeurs V**, en comparant Q aux **clés K**. Dans l'attention à produit scalaire :
```text
Attention(Q, K, V) = softmax(Q·Kᵀ / √d_k + masque) · V
```
Le softmax normalise les scores sur les positions autorisées. Le résultat est une somme pondérée de leurs vecteurs V, pas une sélection nécessairement unique. Les poids dépendent des représentations apprises ; une forte attention n'est pas une preuve que le passage est vrai, ni une explication causale complète de la prédiction.

---

Qu'est-ce que l'attention causale ? <!--anki:46472b6d792b493b2826-->
?
Un **masque interdit de consulter les positions futures** : la représentation à la position i utilise les positions ≤ i pour prédire le token suivant. À l'entraînement, le texte complet est disponible, mais le masque préserve cette contrainte tout en calculant plusieurs positions en parallèle.

Exemple : pour apprendre à compléter « Le chat dort », la position « chat » ne doit pas voir « dort » avant de le prédire. Cette causalité décrit l'ordre d'information dans la séquence ; elle ne signifie pas que le modèle identifie les causes des événements.

---

Pourquoi plusieurs têtes d'attention (multi-head) ? <!--anki:70495d3d7d324e5e5848-->
?
Chaque tête a ses propres projections Q/K/V et peut se spécialiser dans **un type de relation** (syntaxe, coréférence, position proche…). Les sorties des têtes sont **concaténées** puis reprojetées.

Elles donnent plusieurs façons de combiner l'information d'une même séquence, au lieu d'une unique pondération. La spécialisation n'est pas imposée tête par tête ni forcément interprétable. Avec GQA ou MQA, plusieurs têtes de requête partagent des K/V pour économiser de la mémoire ; le principe de vues multiples demeure.

---

Qu'est-ce que GQA et MQA, et pourquoi comptent-ils en production ? <!--anki:6a72557e65666e265368-->
?
**GQA** partage les têtes de clés et valeurs entre groupes de têtes de requête ; **MQA** utilise une seule tête K/V pour toutes les requêtes. À dimensions et précision fixées, moins de têtes KV signifie moins de mémoire cache et de lectures pendant le decode.

Le compromis de qualité dépend du modèle et de son entraînement. Ce n'est pas un réglage interchangeable sans adaptation des poids. Distinguer le nombre de têtes Q du nombre de têtes KV dans les calculs ; d'autres architectures, comme MLA, utilisent un autre stockage.

---

Quel est le rôle du bloc MLP (feed-forward) ? <!--anki:6b6439385d5d4f3b3945-->
?
Le **MLP** transforme le vecteur de chaque position avec des projections et une non-linéarité, tandis que l'attention échange des informations entre positions. « Indépendamment » signifie que la même transformation s'applique à chaque position, dont le vecteur contient déjà du contexte.

Les blocs MLP représentent souvent une grande part des paramètres et participent à la mémorisation, mais les connaissances ne résident pas exclusivement dans ces blocs. Dans de nombreux [[136-mixture-of-experts|MoE]], on remplace certains MLP denses par des experts sélectionnés par un routeur.

---

À quoi servent les connexions résiduelles et la normalisation ? <!--anki:7a416e26656a2b364877-->
?
Les **connexions résiduelles** ajoutent une transformation à son entrée : `y = x + f(x)`. Elles offrent un chemin direct pour l'information et les gradients, ce qui facilite l'entraînement profond sans garantir l'absence de gradients instables.

La **normalisation** contrôle l'échelle des représentations, par exemple avec LayerNorm ou RMSNorm. Son placement avant ou après un sous-bloc dépend de l'architecture. Ce sont deux mécanismes complémentaires : ajouter l'entrée ne normalise pas les valeurs, et normaliser ne remplace pas la connexion résiduelle.

---

Comment le modèle connaît-il la position des tokens ? <!--anki:637e3955546a4c492f2d-->
?
Sans information de position ni masque dépendant de la position, l'attention seule ne distingue pas l'ordre des éléments de la façon voulue. Le modèle reçoit donc une information **positionnelle**, par embeddings, biais ou transformations comme RoPE.

**RoPE** applique des rotations aux requêtes et clés en fonction des positions ; leur produit scalaire encode alors une relation de position relative. Le masque causal fournit également une structure d'ordre, mais ne remplace pas tous ces mécanismes. Étendre les positions supportées ne garantit pas une bonne utilisation des contextes plus longs.

---

Pourquoi l'attention coûte-t-elle cher sur les contextes longs ? <!--anki:76402d59655d2e3c2977-->
?
Le calcul des scores est **quadratique** en longueur de séquence (n² paires) pendant le **prefill**, et le **KV cache** grandit **linéairement** avec le contexte. FlashAttention réduit le coût **mémoire** et les accès HBM, pas la complexité ([[62-optimisations-inference|optimisations]]).

---

Calcul : quel stockage brut pour les poids de 70 milliards de paramètres en BF16, FP8 et INT4, en Go décimaux, puis quels surcoûts faut-il prévoir ? <!--anki:623b687d595d6121635b-->
?
**Nombre de paramètres × octets par paramètre** :
```text
70B en BF16 (2 octets)   ≈ 140 Go → deux H100 80 Go au minimum
70B en FP8  (1 octet)    ≈  70 Go
70B en INT4 (~0,5 octet) ≈  35-40 Go
```
Il faut ajouter le **KV cache** et les activations, souvent plusieurs dizaines de Go de plus en serving ([[68-quantization|quantization]], [[61-kv-cache-attention|KV cache]]).

Les valeurs sont en **Go décimaux** et constituent un budget pour les poids, pas pour tout le service. En quantification, échelles et métadonnées ajoutent un surcoût. Deux cartes de 80 Go ne constituent un minimum que pour cette classe de GPU et une répartition compatible ; contexte et concurrence peuvent imposer davantage de mémoire.

---

À ne pas confondre : decoder-only, encoder-only et encoder-decoder ? <!--anki:42425b217d782c423c4b-->
?
- **Decoder-only** (GPT, Llama, Claude) : attention causale, **génération** — le standard des LLM.
- **Encoder-only** (BERT) : attention **bidirectionnelle**, pas de génération — utilisé pour la **classification**, les **embeddings** et les **rerankers**.
- **Encoder-decoder** (T5) : un encodeur lit l'entrée, un décodeur génère — traduction, résumé.

---

Pourquoi un modèle de base n'est-il pas nécessairement un bon assistant ? <!--anki:656e4e215b5455584f68-->
?
Un **modèle de base** apprend principalement à prédire la suite de textes ; suivre une instruction n'est pas systématiquement l'objectif explicite de cet entraînement. Il peut néanmoins répondre à certaines consignes grâce aux motifs appris.

Le **post-training**, notamment l'entraînement supervisé sur des échanges et parfois les préférences, vise un comportement d'assistant plus adapté. Employer le template attendu et comparer base et instruct sur la tâche. Le post-training peut modifier capacités et connaissances aussi : la séparation « pré-entraînement = savoir, adaptation = comportement » est un repère, pas une frontière absolue.

---

## Mises en situation

Mise en situation : on te demande combien de GPU prévoir pour servir un modèle 70B avec 16 000 tokens de contexte et 50 utilisateurs simultanés. Comment raisonnes-tu à voix haute ? <!--anki:4c256b2c707933653264-->
?
1. **Les poids d'abord** : 70 milliards de paramètres × 2 octets en BF16 ≈ **140 Go**, donc deux GPU de 80 Go ne laissent presque rien
2. **Le KV cache ensuite** : proportionnel au contexte, au nombre de couches et de têtes KV, et au **nombre de requêtes simultanées** ([[61-kv-cache-attention|KV cache]])
3. **Étudier les leviers** : quantification des poids et du cache si supportée ; compter les têtes KV réelles, notamment avec GQA
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
5. **Nuance** : objectifs différents, sans frontière stricte ; le post-training peut aussi modifier connaissances et capacités

**Piège** : conclure qu'un modèle est mauvais alors qu'on utilise une variante de base ou un mauvais gabarit de conversation.

---

## Sources

- [Vaswani et al. — architecture Transformer](https://arxiv.org/abs/1706.03762)
- [Ainslie et al. — GQA](https://arxiv.org/abs/2305.13245)
- [Su et al. — RoFormer et RoPE](https://arxiv.org/abs/2104.09864)

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
