# Caching agressif — Flashcards
Tags: #flashcards #ai-engineering #finops #caching #couts #llm

Qu'est-ce que le caching agressif pour une application LLM ?
?
**Ne jamais payer deux fois le même travail** : réutiliser à chaque niveau ce qui a déjà été calculé (KV cache des préfixes, réponses, embeddings, résultats d'outils et de retrieval), et **concevoir prompts et architecture** pour maximiser le taux de hit. Pour un agent en production, le taux de hit du KV cache est souvent la métrique qui pilote le plus le coût et la latence.

---

Pourquoi les agents en profitent-ils autant ?
?
Leur ratio **entrée / sortie** est énorme : à chaque tour, tout l'historique est renvoyé pour quelques centaines de tokens générés. Avec un préfixe stable, **presque tout l'input** est lu depuis le cache, facturé une fraction du prix normal et sans prefill.

---

Comment fonctionne le prompt caching chez Anthropic ?
?
- Points de cache `cache_control` (**4 maximum**) ou cache automatique
- **TTL de 5 minutes** par défaut, rafraîchi à chaque lecture ; **1 heure** en option
- Écriture : **1,25×** le prix d'entrée (TTL 5 min) ou **2×** (1 h) ; lecture : **≈ 0,1×**
- Rentable **dès la 2e requête** avec le TTL de 5 minutes

D'autres fournisseurs cachent automatiquement les longs préfixes (ex. OpenAI).

---

Comment structurer un prompt pour le cache ?
?
- **Stable d'abord, variable à la fin** : outils → system → historique → question
- **Aucun élément dynamique en tête** : ni date du jour, ni identifiant de requête
- **Sérialisation déterministe** : clés JSON triées, outils toujours dans le même ordre
- Le point de cache à la **fin de la partie partagée**, pas à la fin du prompt entier

---

Qu'est-ce qui casse silencieusement le cache ?
?
- **Un seul octet modifié** dans le préfixe (horodatage, UUID, JSON non trié)
- Ajouter, retirer ou **réordonner un outil**
- **Changer de modèle** : les caches sont propres à chaque modèle
- **Réécrire l'historique** (supprimer ou résumer des messages passés)
- Changer certains paramètres en cours de route (thinking, effort)

Symptôme : les tokens **lus en cache tombent à zéro** dans les champs `usage`, sans aucune erreur.

---

Pourquoi le contexte d'un agent doit-il être append-only ?
?
Toute modification d'un message passé **invalide le cache de tout ce qui suit**. On **ajoute** au lieu de réécrire. Pour restreindre les outils disponibles, on les **masque au décodage** plutôt que de retirer leur définition, ou on passe le « mode » dans un message.

---

Quel piège avec les requêtes parallèles ?
?
Une entrée de cache n'est lisible qu'**une fois que la première réponse commence à streamer**. N requêtes lancées au même instant avec le même préfixe paient donc **toutes l'écriture**. Parade : **pré-chauffer** le cache (chez Anthropic, un appel avec `max_tokens: 0`), ou lancer une requête avant les autres.

---

Quand choisir un TTL d'une heure ?
?
Quand l'écart entre deux requêtes qui partagent le préfixe est **entre 5 et 60 minutes** (un utilisateur qui répond après 20 minutes). En dessous de 5 minutes, chaque lecture rafraîchit le TTL de 5 minutes : il reste chaud tout seul et coûte moins cher à écrire.

---

Que peut-on cacher en dehors du modèle ?
?
- **Réponses exactes** : clé = hash du prompt normalisé + modèle + paramètres
- **Cache sémantique** pour les questions proches ([[82-routing-llm|routing]])
- **Embeddings** : hash du chunk + version du modèle d'embedding, pour ne jamais ré-embedder
- **Résultats d'outils, d'API et de retrieval**, avec un TTL adapté à leur fraîcheur

---

Comment éviter de servir une réponse périmée ou fausse depuis le cache ?
?
- Une **clé complète** : modèle, version du prompt, paramètres, tenant, version de l'index RAG
- Un **TTL** adapté à la fraîcheur des données, et une **invalidation** à chaque changement de prompt ou de données
- **Ne pas cacher** les réponses personnalisées ou volontairement variées
- Un **seuil strict** pour le cache sémantique

---

Quels risques de sécurité et de confidentialité ?
?
- **Fuite entre utilisateurs** si la clé de cache n'inclut pas le tenant
- **Canal auxiliaire temporel** sur un [[66-prefix-caching-radix-attention|prefix cache]] partagé
- **Données sensibles** stockées dans le cache : chiffrement, durée de rétention, droit à l'oubli

---

Comment piloter le caching ?
?
- Suivre le **taux de hit** (tokens lus en cache / tokens d'entrée) et le **coût par tâche**
- **Alerter** sur une chute du taux de hit : c'est typiquement une régression silencieuse après un changement du prompt
- Un **test d'intégration** : une 2e requête identique doit montrer des tokens lus en cache

---

## Connexions
- [[121-couts-inference|Coûts d'inférence]] — ce que le cache fait économiser
- [[122-finops-llm|FinOps LLM]] — les caches comme levier FinOps
- [[66-prefix-caching-radix-attention|Prefix caching & RadixAttention]] — le mécanisme côté serveur
- [[35-context-engineering|Context engineering]] — le préfixe stable
- [[82-routing-llm|Routing LLM]] — cache sémantique et affinité de préfixe
- [[81-litellm-api-layer|LiteLLM]] — cache de réponses dans la gateway
- [[00-moc-ai-engineering|MOC AI Engineering]]
