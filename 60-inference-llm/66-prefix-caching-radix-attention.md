# Prefix caching & RadixAttention — Flashcards
Tags: #flashcards #ai-engineering #inference #kv-cache #caching #llm
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.

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

## Mises en situation

Mise en situation : ton assistant multi-tours affichait 70 % de hits sur le prefix cache. Après une mise à jour, le taux tombe à 5 % et le TTFT double. Que cherches-tu ?
?
1. **Un changement en tête de prompt** : horodatage, identifiant de session, ordre des outils devenu variable
2. **Vérifier la règle** : le prefix caching exige une correspondance **exacte depuis le premier token**
3. **Regarder le déploiement** : nouveaux réplicas aux caches froids, ou routage redevenu round-robin
4. **Corriger** : contenu stable en tête, variable en fin, et **routage par affinité de préfixe** ([[82-routing-llm|routing]])
5. **Surveiller** le taux de hit comme métrique de premier plan ([[123-caching-agressif|caching]])

**Piège** : une seule variable dynamique insérée au début du system prompt suffit à annuler tout le cache.

---

Mise en situation : tu passes de 1 à 4 réplicas vLLM derrière un load balancer classique, et le TTFT se dégrade alors que tu as plus de GPU. Pourquoi ?
?
1. **Cause** : chaque réplica a **son propre cache**. Un round-robin disperse les requêtes et fait chuter les hits
2. **Mesurer** : taux de hit par réplica, avant et après le passage à l'échelle
3. **Corriger** : routeur **cache-aware** (SGLang router, llm-d, Dynamo, vLLM production stack) qui envoie la requête là où son préfixe est chaud
4. **Équilibrer** : l'affinité ne doit pas créer de point chaud. Le routeur arbitre entre hit et charge
5. **Compléter** : offloading du KV cache, voire cache partagé entre instances (LMCache)

**Piège** : conclure que le passage à l'échelle « ne sert à rien » sans regarder le cache.

---

Mise en situation : ton service multi-clients partage un même modèle, et un client s'inquiète que ses prompts puissent fuiter via le cache. Que réponds-tu ?
?
1. **Le risque est réel** : le prefix caching crée un **canal auxiliaire temporel**. Un TTFT plus court révèle qu'un préfixe est déjà en cache
2. **Ce qui fuit** : pas le contenu directement, mais la possibilité de **deviner un prompt** morceau par morceau en mesurant les temps de réponse
3. **Parade principale** : isoler le cache par client (`cache_salt` dans vLLM), comme les fournisseurs d'API le font par organisation
4. **Coût** : moins de partage, donc moins de hits. C'est un arbitrage sécurité contre performance
5. **Vérifier** aussi l'isolation de la mémoire, des index et des journaux ([[115-plateformes-agents-gouvernance|isolation multi-tenant]])

**Piège** : partager le cache entre clients pour « améliorer les performances globales ».

---

## Connexions
- [[61-kv-cache-attention|KV cache & attention]] — PagedAttention et prefix caching
- [[62-optimisations-inference|Optimisations d'inférence]] — prefill et decode
- [[11-serveurs-inference-llm|Serveurs d'inférence]] — vLLM et SGLang
- [[82-routing-llm|Routing LLM]] — affinité de préfixe entre réplicas
- [[64-metriques-slo-inference|Métriques & SLO]] — TTFT et débit
- [[123-caching-agressif|Caching agressif]] — concevoir les prompts pour le cache
- [[00-moc-ai-engineering|MOC AI Engineering]]
