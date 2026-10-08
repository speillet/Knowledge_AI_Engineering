# KV cache & attention — Flashcards
Tags: #flashcards #ai-engineering #inference #kv-cache #llm
<!-- summary: rôle et taille du cache, KV cache, prefix caching et prompt caching, calcul de la concurrence sur un H100, PagedAttention et continuous batching, KV cache en FP8, coût des contextes longs. -->


Qu'est-ce que le KV cache ? <!--anki:4b502378625b2b7e6f5e-->
?
Le **KV cache** conserve les clés et valeurs des positions déjà traitées, à chaque couche d'attention. Au decode, on calcule les nouvelles K/V et on consulte les anciennes sans refaire tout le passage avant sur le préfixe.

Il échange du calcul contre une mémoire croissante. Pour une attention dense, la lecture du passé reste proportionnelle à la longueur du contexte à chaque étape ; le coût cumulé de génération peut donc encore croître quadratiquement. Dire que le cache « supprime tout coût quadratique » confond recalcul évité et attention encore nécessaire.

---

Pourquoi le KV cache est-il indispensable ? <!--anki:426d336e30672d4b5324-->
?
Le KV cache conserve les **clés et valeurs des tokens déjà traités** à chaque couche. Pour le prochain token, on calcule ses nouvelles représentations puis son attention sur les K/V passés, sans recalculer ceux-ci à chaque tour.

Le passé n'est donc pas gratuit : le nouveau token doit encore consulter le cache, ce qui consomme de la bande passante. Sans cache, une implémentation autorégressive répète beaucoup de calculs sur le préfixe ; avec cache, elle échange ce calcul contre de la mémoire.

---

De quoi dépend la taille du KV cache ? <!--anki:772d3f6b3d4e527d4575-->
?
Elle croît **linéairement** avec : longueur du contexte × nombre de couches × têtes KV × dimension × précision (dtype) × taille du batch.
```text
octets par token = 2 (K et V) × couches × têtes_KV × dim_tête × octets

Llama 3.1 8B  : 2 × 32 × 8 × 128 × 2 octets ≈ 128 Kio / token
                → 8 000 tokens de contexte ≈ 1 Go pour UNE requête
70B (GQA)     : 2 × 80 × 8 × 128 × 2 octets ≈ 320 Kio / token
                → 8 000 tokens ≈ 2,5 Go par requête
```
D'où l'importance de **GQA** (peu de têtes KV) et de la [[68-quantization|quantization du cache]] : ce sont eux qui déterminent la concurrence tenue par GPU.

---

À ne pas confondre : KV cache, prefix caching et prompt caching ? <!--anki:42435b332d6730765774-->
?
- **KV cache** : le mécanisme **interne** à une génération. Sans lui, chaque token recalculerait tout le contexte
- **Prefix caching** : la **réutilisation entre requêtes** d'un KV cache déjà calculé pour un préfixe commun, côté serveur ([[66-prefix-caching-radix-attention|prefix caching]])
- **Prompt caching** : la même idée **facturée** par un fournisseur d'API, avec ses prix d'écriture et de lecture et son TTL ([[123-caching-agressif|caching]])

Le premier est indispensable, les deux autres sont des optimisations de coût et de TTFT.

---

Pourquoi le KV cache limite-t-il le nombre de requêtes simultanées ? <!--anki:3d415a7e614c5e375e-->
?
Parce que chaque requête occupe de la **VRAM proportionnelle à son contexte** : la mémoire GPU devient le goulot d'étranglement, pas le calcul.

Le budget restant après les poids et les autres allocations doit couvrir tous les tokens actifs, entrée et sortie. Une requête longue peut prendre la place de plusieurs courtes. La mémoire n'est pas toujours le seul goulot : calcul, bande passante et SLO peuvent imposer une concurrence inférieure au maximum qui tient en VRAM.

---

Qu'est-ce que PagedAttention ? <!--anki:6b4d433358527e784d24-->
?
**PagedAttention** organise le KV cache en blocs physiques qui peuvent être non contigus, associés aux positions logiques d'une séquence. Le serveur alloue les blocs à mesure que celle-ci grandit, sans réserver un grand espace contigu pour sa longueur maximale.

Cette organisation **réduit fortement le gaspillage et la fragmentation** ; il peut rester un bloc partiellement rempli par séquence et des métadonnées. Elle facilite aussi certains partages de blocs. Elle ne réduit pas la quantité de K/V nécessaire pour des tokens distincts ([[11-serveurs-inference-llm|vLLM]]).

---

Qu'est-ce que le prefix caching ? <!--anki:43725f666b753b3d2d2e-->
?
La **réutilisation du KV cache d'un préfixe partagé** entre plusieurs requêtes : system prompt commun, documents identiques, historique d'une conversation. Le prefill de ce préfixe n'est calculé **qu'une fois**, d'où un TTFT et un coût bien plus faibles pour les requêtes suivantes.

Condition : le préfixe doit être **identique au token près**, donc placé en tête et stable ([[66-prefix-caching-radix-attention|prefix caching & RadixAttention]]).

---

Peut-on quantizer le KV cache ? <!--anki:765860436e5b7274564e-->
?
Un cache **FP8** utilise environ deux fois moins d'octets pour les valeurs qu'un cache BF16, hors échelles et métadonnées. Cela peut permettre davantage de tokens résidents, sous réserve du support matériel et du moteur.
```bash
vllm serve mon-modele --kv-cache-dtype fp8
```
Vérifier les formats et facteurs d'échelle requis pour le modèle et la version. Mesurer la qualité, notamment à long contexte, puis le goodput sous charge. Moitié moins d'octets ne garantit ni qualité inchangée, ni débit doublé : kernels, bande passante et limites du scheduler comptent aussi.

---

Quel lien entre KV cache et continuous batching ? <!--anki:7536444f685b6a7a327a-->
?
Le continuous batching fait **entrer et sortir** les requêtes du batch à chaque étape. Il faut donc **allouer et libérer** le KV cache de chaque requête en continu, sans fragmenter la mémoire.

C'est ce que permet **PagedAttention** : le cache est découpé en **blocs** de taille fixe, comme la mémoire virtuelle d'un système d'exploitation, ce qui maximise le nombre de requêtes servies ([[62-optimisations-inference|continuous batching]]).

---

Quel lien entre KV cache et contexte long ? <!--anki:793936344b2c75354c44-->
?
Plus le contexte est long, plus le cache est gros : le **contexte long coûte de la VRAM et de la latence**, d'où l'intérêt de la [[35-context-engineering|gestion du contexte]].

Pour une attention dense, chaque nouveau token consulte davantage de K/V lorsque l'historique grandit. Réduire le contexte peut donc améliorer à la fois concurrence et temps de décodage. Quantifier le cache ou partager des préfixes aide la mémoire, mais ne remplace pas une sélection de sources pertinentes et une limite de longueur de sortie.

---

Calcul : combien de requêtes de 8 000 tokens tiennent sur un H100 80 Go qui sert un modèle 8B en BF16 ? <!--anki:6a4724747a7e6e796170-->
?
```text
VRAM utilisable (gpu_memory_utilization 0,9)   ≈ 72 Go
poids 8B en BF16                              ≈ 16 Go
activations, graphes CUDA                      ≈  3 Go
reste pour le KV cache                         ≈ 53 Go
KV par token (Llama 3.1 8B)                    ≈ 128 Kio → 8 000 tokens ≈ 1 Go
→ environ 50 requêtes simultanées à contexte plein
```
Au-delà, les requêtes **attendent en file** ou sont **préemptées** (recalcul ou swap), et la latence p99 explose. En FP8, le KV cache peut augmenter la capacité mémoire ([[64-metriques-slo-inference|concurrence]]).

Ce sont des capacités mémoire approximatives, avec Go décimaux et un cache d'environ 128 Kio par token. Réserver aussi les tokens qui seront générés et les marges du moteur. **Deux fois moins d'octets par K/V ne garantit pas deux fois plus de requêtes dans le SLO** : vérifier bande passante et latence en charge.

---

Calcul : combien de requêtes de 8 000 tokens tiennent sur 2 H100 qui servent un 70B en FP8 ? <!--anki:6137666465353731643634663436353938383237353137393038343239396564-->
?
```text
VRAM utilisable : 2 × 80 Go × 0,9                 ≈ 144 Go
poids 70B en FP8                                  ≈  70 Go
activations, graphes CUDA                         ≈   6 Go
reste pour le KV cache                            ≈  68 Go
KV par token (Llama 3.1 70B : 80 couches, 8 têtes KV de 128, BF16)
  2 × 80 × 8 × 128 × 2 octets                     ≈ 320 Kio → 8 000 tokens ≈ 2,6 Go
→ environ 26 requêtes simultanées à contexte plein
```
Le 70B coûte 2,5 fois plus de KV par token que le 8B (320 Kio contre 128 Kio) : sa concurrence chute vite. Un KV cache en FP8 réduit l’empreinte des valeurs ([[68-quantization|quantization]]).

L'estimation suppose que les poids et le cache se répartissent correctement entre GPU ; tenir au total ne garantit pas de tenir sur chaque carte. Inclure les sorties futures et les allocations du moteur. Le FP8 peut approximativement doubler la capacité mémoire du cache, mais pas nécessairement le débit utile sous contrainte de latence.

---

Que se passe-t-il si on double `max_model_len` sur un serveur vLLM ? <!--anki:3066363230336533336366653437396238396664636166383237643436363065-->
?
Les requêtes longues peuvent occuper **deux fois plus de KV cache** : quand elles arrivent, la concurrence baisse d'autant. Les requêtes courtes ne paient rien de plus, car le cache est alloué par blocs à la demande (**PagedAttention**).

Au démarrage, vLLM vérifie qu'au moins une requête de longueur maximale tient dans le cache, et **refuse de démarrer** sinon. On fixe donc `max_model_len` au besoin réel, pas au maximum du modèle.

---

## Mises en situation

Mise en situation : ton service vLLM tient 60 requêtes simultanées avec des prompts de 2 000 tokens, mais plus que 8 quand tu passes à 32 000 tokens de contexte. Pourquoi, et que fais-tu ? <!--anki:793e766f644d6c763c68-->
?
1. **Cause** : le KV cache croît **linéairement avec le contexte**. À contexte multiplié par 16, chaque requête occupe 16 fois plus de VRAM
2. **Vérifier** : taux d'occupation du KV cache et préemptions, plutôt que l'utilisation GPU ([[93-monitoring-inference|monitoring]])
3. **Gagner de la place** : **quantizer le KV cache** en FP8, quantizer les poids pour libérer de la VRAM ([[68-quantization|quantization]])
4. **Réduire le contexte** : trier ce qu'on envoie, résumer, récupérer moins de chunks ([[35-context-engineering|context engineering]])
5. **Sinon, dimensionner** : plus de VRAM par GPU, ou plus de réplicas, avec le coût qui va avec ([[121-couts-inference|coûts]])

**Piège** : promettre un contexte de 128 000 tokens sans recalculer la concurrence possible.

---

Mise en situation : ton équipe veut activer la quantization FP8 du KV cache pour doubler la concurrence. Comment valides-tu la décision ? <!--anki:677257392a29685b5b40-->
?
1. **Comprendre le gain** : le valeurs du cache environ deux fois plus petites ; vérifier les surcoûts et le SLO avant de promettre davantage de requêtes
2. **Mesurer la perte** : comparer les réponses avec et sans, sur tes propres evals, en portant attention aux contextes longs ([[68-quantization|validation]])
3. **Tester en charge** : débit, TPOT et préemptions à la concurrence cible ([[64-metriques-slo-inference|SLO]])
4. **Déployer progressivement** : canary, avec suivi de la qualité en production
5. **Documenter** : c'est un réglage qui change les sorties, donc il doit apparaître dans la configuration versionnée

**Piège** : activer la quantization du cache et celle des poids en même temps, sans pouvoir attribuer la dégradation.

---

## Sources

- [PagedAttention — mémoire et attention](https://arxiv.org/abs/2309.06180)
- [vLLM — cache KV quantifié](https://docs.vllm.ai/en/latest/features/quantization/quantized_kvcache/)

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
- [[60-011-capacite-ordonnancement-inference|Capacité & ordonnancement]] — relier mémoire, budgets et débit utile sous charge
- [[00-moc-ai-engineering|MOC AI Engineering]]
