# Streaming & intégration applicative — Flashcards
Tags: #flashcards #ai-engineering #api #streaming #agents #llm
Vérifié le : 30 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.
<!-- summary: intérêt du streaming, SSE ou WebSocket, tampons des proxys, annulation côté serveur, JSON en streaming, événements d'un agent (AG-UI), tâches longues asynchrones, reprise d'un flux, clé d'idempotence, calcul des connexions ouvertes. -->


Pourquoi streamer les réponses d'un LLM ? <!--anki:6536416a5043402c2f28-->
?
Parce que la génération est **séquentielle** : une réponse de 500 tokens à 50 tokens/s prend 10 secondes. En streaming, l'utilisateur lit dès le **premier token** (TTFT de quelques centaines de millisecondes), et la latence **perçue** s'effondre ([[64-metriques-slo-inference|TTFT]]).

Le coût total ne change pas ; seule l'expérience change ([[144-ux-ia-human-in-the-loop|UX]]).

---

À ne pas confondre : SSE et WebSocket ? <!--anki:4c7763604f434577474d-->
?
- **SSE** (Server-Sent Events) : flux **serveur → client** sur une réponse HTTP ordinaire (`text/event-stream`). Simple, passe les proxys, **reconnexion** intégrée. Format des API de LLM
- **WebSocket** : canal **bidirectionnel** permanent. Utile quand le client envoie aussi en continu : voix, interruption en temps réel, collaboration ([[163-voix-temps-reel|voix]])

Pour un chat ou un agent textuel, SSE suffit dans la grande majorité des cas.

---

Pourquoi un streaming SSE arrive-t-il parfois d'un seul bloc ? <!--anki:4e6e354453327c605246-->
?
Un intermédiaire **met la réponse en tampon** (buffering) : reverse proxy, compression, CDN ou framework. Le client reçoit tout à la fin.
```nginx
location /api/chat {
    proxy_pass http://backend;
    proxy_buffering off;          # ou en-tête X-Accel-Buffering: no
    proxy_read_timeout 300s;      # les réponses longues dépassent 60 s
    gzip off;
}
```
Vérifier aussi les **timeouts d'inactivité** des load balancers : envoyer un commentaire SSE régulier (`: ping`) les évite ([[83-gateway-ingress|gateway]]).

---

Pourquoi gérer l'annulation côté serveur ? <!--anki:4c74432f2e24316a6b77-->
?
Quand l'utilisateur ferme l'onglet ou clique sur « Arrêter », le serveur doit **interrompre l'appel au modèle** : sinon la génération continue, **consomme des tokens facturés** et occupe le KV cache du serveur d'inférence pour rien.

En pratique : détecter la déconnexion du client, puis annuler la requête en cours (annulation de la tâche asynchrone, fermeture du flux vers le fournisseur) ([[121-couts-inference|coûts]]).

---

Comment streamer une sortie structurée (JSON) ? <!--anki:4f736b3c676762595649-->
?
Un JSON partiel n'est pas valide tant qu'il n'est pas fini. Deux approches :
- **Parseur de JSON partiel** côté client, qui affiche les champs au fur et à mesure qu'ils se complètent
- **Streamer seulement le texte libre**, et envoyer les champs structurés dans un événement final

Les API de structured outputs streament des fragments, validés contre le schéma **à la fin** seulement ([[63-guided-generation|guided generation]]).

---

Comment streamer une réponse d'agent qui appelle des outils ? <!--anki:732a6b6543373a467370-->
?
Le flux contient plusieurs **types d'événements**, pas seulement du texte : début et fin d'étape, appel d'outil avec ses arguments, résultat, texte de la réponse, erreur, fin. Le client affiche ainsi **ce que l'agent fait** (« recherche dans la base… »), ce qui rend l'attente acceptable.

C'est l'objet de protocoles comme **AG-UI**, qui standardise ces événements entre un agent et son interface ([[144-ux-ia-human-in-the-loop|rendre visible le travail]]).

---

Comment exposer une tâche d'agent qui dure plusieurs minutes ? <!--anki:6a352641682c7b69602d-->
?
Pas en requête HTTP synchrone : les connexions se coupent et on perd tout. On passe en **asynchrone** :
1. `POST /taches` renvoie tout de suite un **identifiant**
2. L'agent tourne dans un **worker**, son état est persisté
3. Le client suit la progression par **SSE**, par interrogation périodique, ou reçoit un **webhook** à la fin

Si le worker redémarre, la tâche reprend grâce à l'**exécution durable** ([[115-plateformes-agents-gouvernance|exécution durable]]).

---

Comment reprendre un flux coupé sans tout perdre ? <!--anki:686c3f7c614c49506d52-->
?
- Numéroter les événements : SSE renvoie l'en-tête **`Last-Event-ID`** à la reconnexion
- **Conserver le flux** côté serveur (Redis, base) quelques minutes, indépendamment de la connexion
- Au retour, renvoyer les événements **manqués**, puis continuer en direct

Condition : que la génération **continue** côté serveur même sans client connecté, ce qui s'oppose à l'annulation automatique. On choisit selon l'usage : chat court (annuler) ou tâche longue (continuer).

---

Qu'est-ce qu'une clé d'idempotence et pourquoi en mettre sur une API LLM ? <!--anki:413e3131404d6351465b-->
?
Un identifiant unique fourni par le client (`Idempotency-Key`) : si la même requête arrive deux fois (double clic, retry réseau), le serveur renvoie le **même résultat** au lieu de relancer. Sans elle, un retry relance l'agent, **double le coût** et peut **répéter une action** (ticket créé deux fois) ([[142-fiabilite-resilience-llm|retries]]).

---

Calcul : combien de connexions ouvertes pour 50 utilisateurs qui démarrent une conversation par seconde, streamée pendant 12 secondes ? <!--anki:725e21745a3f6a415179-->
?
**Loi de Little** : connexions simultanées = arrivées × durée.
```text
50 req/s × 12 s = 600 flux SSE ouverts en moyenne
pic ×3          ≈ 1 800
```
Chaque flux tient une connexion et souvent une tâche asynchrone : il faut un serveur **asynchrone** (pas un thread par requête) et vérifier les **limites de connexions** du proxy et du fournisseur ([[64-metriques-slo-inference|concurrence]]).

---

## Mises en situation

Mise en situation : ton assistant stream bien en local, mais en production la réponse apparaît d'un coup après 15 secondes, et certaines réponses longues sont coupées à 60 secondes. Que vérifies-tu ? <!--anki:4651427b395e7d5061-->
?
1. **Tracer le chemin** : navigateur, CDN, load balancer, ingress, application, fournisseur
2. **Chercher le tampon** : `proxy_buffering`, compression, middleware qui lit toute la réponse ([[83-gateway-ingress|ingress]])
3. **Chercher le timeout de 60 s** : délai d'inactivité du load balancer ou `proxy_read_timeout`
4. **Corriger** : désactiver le tampon sur cette route, allonger les délais, envoyer des `: ping` réguliers
5. **Tester** avec `curl -N` à chaque couche pour voir où le flux se bloque

**Piège** : augmenter les ressources du backend, alors que le problème est dans le proxy.

---

Mise en situation : un agent d'analyse met 3 à 8 minutes à produire un rapport. Aujourd'hui l'interface attend la réponse HTTP, et 20 % des analyses sont perdues. Comment reconçois-tu l'intégration ? <!--anki:76523976517d40646353-->
?
1. **Passer en asynchrone** : création de tâche avec identifiant, clé d'idempotence contre les doubles soumissions
2. **Exécuter dans un worker** avec exécution durable, pour survivre aux redémarrages ([[115-plateformes-agents-gouvernance|exécution durable]])
3. **Publier la progression** en événements (étapes, sources lues), consultables par SSE avec reprise via `Last-Event-ID`
4. **Notifier la fin** par webhook ou notification, pour que l'utilisateur puisse fermer l'onglet
5. **Mesurer** : taux de tâches terminées, durée, abandons

**Piège** : augmenter les timeouts partout jusqu'à 10 minutes, et garder une architecture fragile.

---

## Sources

- [MDN — utilisation des Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events)
- [AG-UI — protocole d’interaction agent-interface](https://docs.ag-ui.com/introduction)

## Connexions
- [[81-litellm-api-layer|LiteLLM]] — la gateway qui relaie le flux
- [[83-gateway-ingress|Ingress & API gateway]] — tampons et timeouts
- [[64-metriques-slo-inference|Métriques & SLO]] — TTFT et concurrence
- [[144-ux-ia-human-in-the-loop|UX & human-in-the-loop]] — ce que le streaming change pour l'utilisateur
- [[142-fiabilite-resilience-llm|Fiabilité & résilience]] — idempotence et retries
- [[115-plateformes-agents-gouvernance|Plateformes d'agents]] — exécution durable des tâches longues
- [[163-voix-temps-reel|Voix & temps réel]] — quand il faut du bidirectionnel
- [[85-carte-protocoles-agentiques|Carte des protocoles]] — où se place AG-UI
- [[141-system-design-llm|System design LLM]] — la méthode de conception
- [[61-kv-cache-attention|KV cache]] — la mémoire qui limite la concurrence
- [[33-mcp|MCP]] — le protocole standard entre agents et outils
- [[00-moc-ai-engineering|MOC AI Engineering]]
