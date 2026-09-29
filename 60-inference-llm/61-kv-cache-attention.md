# KV cache & attention — Flashcards
Tags: #flashcards #ai-engineering #inference #kv-cache #llm

Qu'est-ce que le KV cache ?
?
Le **stockage en VRAM des clés (K) et valeurs (V) d'attention** déjà calculées pour les tokens précédents.

---

Pourquoi le KV cache est-il indispensable ?
?
Sans lui, chaque nouveau token obligerait à **recalculer l'attention sur tout le contexte** ; avec lui, on ne calcule que le token courant.

---

De quoi dépend la taille du KV cache ?
?
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
- **KV cache** : le mécanisme **interne** à une génération. Sans lui, chaque token recalculerait tout le contexte
- **Prefix caching** : la **réutilisation entre requêtes** d'un KV cache déjà calculé pour un préfixe commun, côté serveur ([[66-prefix-caching-radix-attention|prefix caching]])
- **Prompt caching** : la même idée **facturée** par un fournisseur d'API, avec ses prix d'écriture et de lecture et son TTL ([[123-caching-agressif|caching]])

Le premier est indispensable, les deux autres sont des optimisations de coût et de TTFT.

---

Pourquoi le KV cache limite-t-il le nombre de requêtes simultanées ?
?
Parce que chaque requête occupe de la **VRAM proportionnelle à son contexte** : la mémoire GPU devient le goulot d'étranglement, pas le calcul.

---

Qu'est-ce que PagedAttention ?
?
La technique de [[11-serveurs-inference-llm|vLLM]] qui gère le KV cache en **blocs paginés non contigus** (comme la mémoire virtuelle d'un OS), éliminant la fragmentation.

---

Qu'est-ce que le prefix caching ?
?
La **réutilisation du KV cache d'un préfixe partagé** (ex. system prompt commun) entre plusieurs requêtes, évitant de le recalculer.

---

Peut-on quantizer le KV cache ?
?
**Oui** (ex. FP8) : on réduit la VRAM occupée par le cache au prix d'une légère perte de précision.

---

Quel lien entre KV cache et continuous batching ?
?
Le batching dynamique doit **allouer/libérer le KV cache par requête** ; une gestion efficace (PagedAttention) maximise le nombre de requêtes servies.

---

Quel lien entre KV cache et contexte long ?
?
Plus le contexte est long, plus le cache est gros : le **contexte long coûte de la VRAM et de la latence**, d'où l'intérêt de la [[35-context-engineering|gestion du contexte]].

---

Calcul : combien de requêtes de 8 000 tokens tiennent sur un H100 80 Go qui sert un modèle 8B en BF16 ?
?
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
1. **Cause** : le KV cache croît **linéairement avec le contexte**. À contexte multiplié par 16, chaque requête occupe 16 fois plus de VRAM
2. **Vérifier** : taux d'occupation du KV cache et préemptions, plutôt que l'utilisation GPU ([[93-monitoring-inference|monitoring]])
3. **Gagner de la place** : **quantizer le KV cache** en FP8, quantizer les poids pour libérer de la VRAM ([[68-quantization|quantization]])
4. **Réduire le contexte** : trier ce qu'on envoie, résumer, récupérer moins de chunks ([[35-context-engineering|context engineering]])
5. **Sinon, dimensionner** : plus de VRAM par GPU, ou plus de réplicas, avec le coût qui va avec ([[121-couts-inference|coûts]])

**Piège** : promettre un contexte de 128 000 tokens sans recalculer la concurrence possible.

---

Mise en situation : ton équipe veut activer la quantization FP8 du KV cache pour doubler la concurrence. Comment valides-tu la décision ?
?
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
- [[00-moc-ai-engineering|MOC AI Engineering]]
