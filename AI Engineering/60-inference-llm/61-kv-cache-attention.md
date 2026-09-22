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

## Connexions
- [[62-optimisations-inference|Optimisations d'inférence]] — prefill/decode, batching
- [[64-metriques-slo-inference|Métriques & SLO]] — la concurrency plafonnée par la VRAM
- [[11-serveurs-inference-llm|Serveurs d'inférence]] — vLLM & PagedAttention
- [[09-gpu-conteneurs|GPU en conteneur]] — la VRAM sous-jacente
- [[35-context-engineering|Context engineering]] — maîtriser la taille du contexte
- [[00-moc-ai-engineering|MOC AI Engineering]]
