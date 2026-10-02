# KV cache & attention — Flashcards
Tags: #flashcards #ai-engineering #inference #kv-cache #llm
<!-- summary: rôle et taille du cache, KV cache, prefix caching et prompt caching, calcul de la concurrence sur un H100, PagedAttention et continuous batching, KV cache en FP8, coût des contextes longs. -->

Qu'est-ce que le KV cache ?
?
<!--anki:4b502378625b2b7e6f5e-->
Le **stockage en VRAM des clés (K) et valeurs (V) d'attention** déjà calculées pour les tokens précédents. À chaque nouveau token, le modèle n'a qu'à calculer K et V **pour ce token** et à relire le reste.

Sans lui, chaque token généré recalculerait l'attention sur toute la séquence : le coût de génération deviendrait **quadratique**. Le prix à payer : une mémoire qui grandit avec le contexte et le nombre de requêtes.

---

Pourquoi le KV cache est-il indispensable ?
?
<!--anki:426d336e30672d4b5324-->
Sans lui, chaque nouveau token obligerait à **recalculer l'attention sur tout le contexte** ; avec lui, on ne calcule que le token courant.

---

De quoi dépend la taille du KV cache ?
?
<!--anki:772d3f6b3d4e527d4575-->
Elle croît **linéairement** avec : longueur du contexte × nombre de couches × têtes KV × dimension × précision (dtype) × taille du batch.
```text
octets par token = 2 (K et V) × couches × têtes_KV × dim_tête × octets

Llama 3.1 8B  : 2 × 32 × 8 × 128 × 2 octets ≈ 128 Ko / token
                → 8 000 tokens de contexte ≈ 1 Go pour UNE requête
70B (GQA)     : 2 × 80 × 8 × 128 × 2 octets ≈ 320 Ko / token
                → 8 000 tokens ≈ 2,5 Go par requête
```
D'où l'importance de **GQA** (peu de têtes KV) et de la [[68-quantization|quantization du cache]] : ce sont eux qui déterminent la concurrence tenue par GPU.

---

À ne pas confondre : KV cache, prefix caching et prompt caching ?
?
<!--anki:42435b332d6730765774-->
- **KV cache** : le mécanisme **interne** à une génération. Sans lui, chaque token recalculerait tout le contexte
- **Prefix caching** : la **réutilisation entre requêtes** d'un KV cache déjà calculé pour un préfixe commun, côté serveur ([[66-prefix-caching-radix-attention|prefix caching]])
- **Prompt caching** : la même idée **facturée** par un fournisseur d'API, avec ses prix d'écriture et de lecture et son TTL ([[123-caching-agressif|caching]])

Le premier est indispensable, les deux autres sont des optimisations de coût et de TTFT.

---

Pourquoi le KV cache limite-t-il le nombre de requêtes simultanées ?
?
<!--anki:3d415a7e614c5e375e-->
Parce que chaque requête occupe de la **VRAM proportionnelle à son contexte** : la mémoire GPU devient le goulot d'étranglement, pas le calcul.

---

Qu'est-ce que PagedAttention ?
?
<!--anki:6b4d433358527e784d24-->
La technique de [[11-serveurs-inference-llm|vLLM]] qui gère le KV cache en **blocs paginés non contigus** (comme la mémoire virtuelle d'un OS), éliminant la fragmentation.

---

Qu'est-ce que le prefix caching ?
?
<!--anki:43725f666b753b3d2d2e-->
La **réutilisation du KV cache d'un préfixe partagé** entre plusieurs requêtes : system prompt commun, documents identiques, historique d'une conversation. Le prefill de ce préfixe n'est calculé **qu'une fois**, d'où un TTFT et un coût bien plus faibles pour les requêtes suivantes.

Condition : le préfixe doit être **identique au token près**, donc placé en tête et stable ([[66-prefix-caching-radix-attention|prefix caching & RadixAttention]]).

---

Peut-on quantizer le KV cache ?
?
<!--anki:765860436e5b7274564e-->
**Oui**, typiquement en **FP8** : le cache occupe **deux fois moins** de VRAM, donc on sert environ deux fois plus de requêtes ou des contextes deux fois plus longs.
```bash
vllm serve mon-modele --kv-cache-dtype fp8
```
Contrepartie : une légère perte de précision, à mesurer sur ses evals, surtout pour les contextes longs ([[68-quantization|quantization]]).

---

Quel lien entre KV cache et continuous batching ?
?
<!--anki:7536444f685b6a7a327a-->
Le continuous batching fait **entrer et sortir** les requêtes du batch à chaque étape. Il faut donc **allouer et libérer** le KV cache de chaque requête en continu, sans fragmenter la mémoire.

C'est ce que permet **PagedAttention** : le cache est découpé en **blocs** de taille fixe, comme la mémoire virtuelle d'un système d'exploitation, ce qui maximise le nombre de requêtes servies ([[62-optimisations-inference|continuous batching]]).

---

Quel lien entre KV cache et contexte long ?
?
<!--anki:793936344b2c75354c44-->
Plus le contexte est long, plus le cache est gros : le **contexte long coûte de la VRAM et de la latence**, d'où l'intérêt de la [[35-context-engineering|gestion du contexte]].

---

Calcul : combien de requêtes de 8 000 tokens tiennent sur un H100 80 Go qui sert un modèle 8B en BF16 ?
?
<!--anki:6a4724747a7e6e796170-->
```text
VRAM utilisable (gpu_memory_utilization 0,9)   ≈ 72 Go
poids 8B en BF16                              ≈ 16 Go
activations, graphes CUDA                      ≈  3 Go
reste pour le KV cache                         ≈ 53 Go
KV par token (Llama 3.1 8B)                    ≈ 128 Ko → 8 000 tokens ≈ 1 Go
→ environ 50 requêtes simultanées à contexte plein
```
Au-delà, les requêtes **attendent en file** ou sont **préemptées** (recalcul ou swap), et la latence p99 explose. En FP8, le KV cache double la concurrence ([[64-metriques-slo-inference|concurrence]]).

---

## Mises en situation

Mise en situation : ton service vLLM tient 60 requêtes simultanées avec des prompts de 2 000 tokens, mais plus que 8 quand tu passes à 32 000 tokens de contexte. Pourquoi, et que fais-tu ?
?
<!--anki:793e766f644d6c763c68-->
1. **Cause** : le KV cache croît **linéairement avec le contexte**. À contexte multiplié par 16, chaque requête occupe 16 fois plus de VRAM
2. **Vérifier** : taux d'occupation du KV cache et préemptions, plutôt que l'utilisation GPU ([[93-monitoring-inference|monitoring]])
3. **Gagner de la place** : **quantizer le KV cache** en FP8, quantizer les poids pour libérer de la VRAM ([[68-quantization|quantization]])
4. **Réduire le contexte** : trier ce qu'on envoie, résumer, récupérer moins de chunks ([[35-context-engineering|context engineering]])
5. **Sinon, dimensionner** : plus de VRAM par GPU, ou plus de réplicas, avec le coût qui va avec ([[121-couts-inference|coûts]])

**Piège** : promettre un contexte de 128 000 tokens sans recalculer la concurrence possible.

---

Mise en situation : ton équipe veut activer la quantization FP8 du KV cache pour doubler la concurrence. Comment valides-tu la décision ?
?
<!--anki:677257392a29685b5b40-->
1. **Comprendre le gain** : le cache divisé par deux, donc environ deux fois plus de requêtes simultanées à VRAM égale
2. **Mesurer la perte** : comparer les réponses avec et sans, sur tes propres evals, en portant attention aux contextes longs ([[68-quantization|validation]])
3. **Tester en charge** : débit, TPOT et préemptions à la concurrence cible ([[64-metriques-slo-inference|SLO]])
4. **Déployer progressivement** : canary, avec suivi de la qualité en production
5. **Documenter** : c'est un réglage qui change les sorties, donc il doit apparaître dans la configuration versionnée

**Piège** : activer la quantization du cache et celle des poids en même temps, sans pouvoir attribuer la dégradation.

---

## Connexions
- [[62-optimisations-inference|Optimisations d'inférence]] — prefill/decode, batching
- [[64-metriques-slo-inference|Métriques & SLO]] — la concurrency plafonnée par la VRAM
- [[11-serveurs-inference-llm|Serveurs d'inférence]] — vLLM & PagedAttention
- [[09-gpu-conteneurs|GPU en conteneur]] — la VRAM sous-jacente
- [[35-context-engineering|Context engineering]] — maîtriser la taille du contexte
- [[66-prefix-caching-radix-attention|Prefix caching & RadixAttention]] — la réutilisation du cache en détail
- [[68-quantization|Quantization]] — quantizer les poids et le cache
- [[131-transformer-architecture|Architecture Transformer]] — attention, GQA, RoPE
- [[137-long-contexte|Long contexte]] — coût des contextes longs
- [[65-probabilites-sampling|Probabilités & sampling]] — température, top-p et logprobs
- [[69-roofline-prefill-decode|Roofline & désagrégation]] — ce qui limite chaque phase de l'inférence
- [[12-kubernetes-gpu-inference|Kubernetes GPU & inférence]] — servir des modèles sur un cluster GPU
- [[164-llm-local-edge|LLM locaux & edge]] — faire tourner un modèle en local
- [[67-speculative-decoding|Speculative decoding]] — générer plusieurs tokens par passage
- [[84-streaming-integration-applicative|Streaming & intégration]] — SSE, annulation et tâches longues
- [[00-moc-ai-engineering|MOC AI Engineering]]
