# Prefix caching & RadixAttention — Flashcards
Tags: #flashcards #ai-engineering #inference #kv-cache #caching #llm

Qu'est-ce que le prefix caching côté serveur ?
?
La **réutilisation du [[61-kv-cache-attention|KV cache]]** d'un préfixe déjà calculé par une requête précédente : le serveur saute le prefill de ces tokens. Résultat : **TTFT plus court** et **débit plus élevé**. Il faut une correspondance **exacte, token par token, depuis le début** du prompt.

---

Comment vLLM implémente-t-il l'automatic prefix caching ?
?
Le KV cache est découpé en **blocs** ([[61-kv-cache-attention|PagedAttention]]). Chaque bloc plein est identifié par un **hash** (hash du bloc parent + tokens du bloc + clés éventuelles : adaptateur LoRA, image, sel). Une table hash → bloc permet de retrouver les préfixes ; les blocs libres sont évincés en **LRU**. Activé par défaut dans vLLM V1.

---

Qu'est-ce que RadixAttention ?
?
La technique de **SGLang** qui range les préfixes en cache dans un **arbre radix** : chaque arête porte une séquence de tokens, chaque nœud pointe vers ses pages de KV cache. Une requête **descend l'arbre** jusqu'au plus long préfixe commun, réutilise son KV cache et ajoute une branche pour la suite. Le partage est **automatique** entre requêtes, tours de conversation et branches parallèles.

---

Comment l'arbre radix est-il évincé ?
?
En **LRU sur les feuilles** : on retire d'abord les branches les moins récemment utilisées. Un **compteur de références** protège les nœuds utilisés par des requêtes en cours, et la mémoire libérée retourne au pool commun.

---

Qu'est-ce que l'ordonnancement cache-aware ?
?
Servir en priorité les requêtes dont le **préfixe en cache est le plus long** : cela maximise les hits avant que ces préfixes soient évincés. Le risque est de **faire attendre** les autres requêtes : on l'équilibre avec une règle d'équité.

---

Quels workloads en profitent le plus ?
?
- **Agents multi-tours** : l'historique grossit mais son début ne change pas
- Longs **system prompts et définitions d'outils** partagés
- **Few-shot**, **self-consistency**, arbres de raisonnement : un même préfixe, plusieurs branches
- **RAG** répété sur les mêmes documents
- Beaucoup d'utilisateurs sur un **même assistant**

---

Pourquoi le routage entre réplicas doit-il tenir compte du cache ?
?
Chaque réplica a **son propre cache** : un load balancer round-robin disperse les préfixes et le taux de hit s'effondre. Un routage par **affinité de préfixe** envoie la requête là où son préfixe est déjà chaud, tout en équilibrant la charge : SGLang router, llm-d, NVIDIA Dynamo, vLLM production stack ([[82-routing-llm|routage LLM]]).

---

Qu'est-ce que l'offloading du KV cache ?
?
Étendre le cache **au-delà de la VRAM** : RAM CPU, SSD, stockage distant, voire un cache **partagé entre instances** (LMCache, gestionnaire de blocs de Dynamo). On conserve ainsi beaucoup plus de préfixes, et pour un long préfixe, **recharger** coûte moins cher que **recalculer**.

---

Quelles sont les limites du prefix caching ?
?
- Correspondance **exacte depuis le début** : un token différent en tête, et rien n'est réutilisé
- **Granularité par bloc** (vLLM ne cache que les blocs pleins)
- Cache **borné** par la mémoire et évincé sous forte charge
- N'accélère que le **prefill**, pas la génération (decode)

---

Quel risque de sécurité en multi-tenant ?
?
Un **canal auxiliaire temporel** : un TTFT plus court révèle qu'un préfixe est déjà en cache, ce qui permet de deviner le prompt d'un autre utilisateur morceau par morceau. Parades : **isoler le cache par tenant** (ex. `cache_salt` dans vLLM) ; les fournisseurs d'API isolent le cache par organisation ou par workspace.

---

Comment mesurer l'efficacité du prefix cache ?
?
- **Taux de hit** du prefix cache (métriques Prometheus de vLLM et SGLang)
- **TTFT** par percentile, avant et après
- Côté API : part des tokens d'entrée **lus depuis le cache**

Une chute brutale du taux de hit signale souvent un préfixe devenu instable ([[123-caching-agressif|caching agressif]]).

---

## Connexions
- [[61-kv-cache-attention|KV cache & attention]] — PagedAttention et prefix caching
- [[62-optimisations-inference|Optimisations d'inférence]] — prefill et decode
- [[11-serveurs-inference-llm|Serveurs d'inférence]] — vLLM et SGLang
- [[82-routing-llm|Routing LLM]] — affinité de préfixe entre réplicas
- [[64-metriques-slo-inference|Métriques & SLO]] — TTFT et débit
- [[123-caching-agressif|Caching agressif]] — concevoir les prompts pour le cache
- [[00-moc-ai-engineering|MOC AI Engineering]]
