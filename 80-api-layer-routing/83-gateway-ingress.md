# Ingress & API gateway — Flashcards
Tags: #flashcards #ai-engineering #kubernetes #ingress #networking

Qu'est-ce qu'un Ingress dans Kubernetes ?
?
La **porte d'entrée HTTP(S) du cluster** : il route le trafic externe vers les Services selon l'hôte et le chemin.

---

Un Ingress fonctionne-t-il seul ?
?
**Non.** L'objet Ingress n'est qu'une **déclaration** ; il faut un **Ingress controller** (ingress-nginx, Traefik, HAProxy, Envoy Gateway) qui l'observe et configure réellement un proxy. Sans controller installé, l'objet est accepté par l'API et **rien ne se passe** : c'est une cause classique de « mon Ingress ne répond pas ».

---

Que gère typiquement un Ingress ?
?
- Routage **par hôte** (`api.example.com`) et **par chemin** (`/v1/...`)
- **Terminaison TLS** (HTTPS)

---

Qu'est-ce que la Gateway API ?
?
Le **successeur de l'Ingress** dans Kubernetes, avec des rôles séparés :
```text
GatewayClass → l'implémentation (choisie par la plateforme)
Gateway      → le point d'entrée : ports, TLS (équipe infra)
HTTPRoute    → le routage vers les Services (équipe applicative)
```
Apports : **délégation par équipe** sans annotations propriétaires, découpage du trafic **par poids** (canary), et prise en charge d'autres protocoles (gRPC, TCP). Les projets de gateway pour agents s'appuient dessus ([[38-plateformes-agents|agentgateway]]).

---

À ne pas confondre : Ingress et API gateway ?
?
- **Ingress** : du **routage HTTP** (L7) vers les Services du cluster, par hôte et par chemin, avec terminaison TLS
- **API gateway** : ajoute la **logique d'API** : authentification, rate limiting, quotas, transformation de requêtes, analytics

Pour une stack LLM, on ajoute souvent une **gateway LLM** (LiteLLM) derrière, qui connaît les modèles, les tokens et les budgets ([[81-litellm-api-layer|LiteLLM]]).

---

À ne pas confondre : Ingress, API gateway et gateway LLM ?
?
```text
Ingress        → entrée réseau : TLS, hôte, chemin
API gateway    → authentification, quotas, transformation, WAF
Gateway LLM    → clés virtuelles, budgets par équipe, routage entre modèles,
                 fallbacks, comptage des tokens, traces
```
Les trois se cumulent, dans cet ordre. Une API gateway sait compter les **requêtes**, pas les **tokens** : c'est précisément ce qu'apporte la couche LLM ([[81-litellm-api-layer|LiteLLM]]).

---

Pourquoi rate-limiter un endpoint LLM ?
?
Parce que chaque requête consomme du **GPU coûteux** : sans limite, un client peut saturer le service et faire exploser les coûts.

---

À quoi ressemble la chaîne réseau d'une stack LLM sur Kubernetes ?
?
```text
Client → Ingress (TLS, routage) → gateway/LiteLLM (auth, quotas) → Service vLLM → Pods GPU
```

---

Pourquoi le streaming (SSE) impose-t-il des réglages particuliers ?
?
Les réponses LLM sont **longues et streamées** : il faut des **timeouts allongés** et désactiver le **buffering**, sinon le proxy garde la réponse et l'utilisateur attend tout le texte d'un coup.
```yaml
annotations:                       # ingress-nginx
  nginx.ingress.kubernetes.io/proxy-buffering: "off"
  nginx.ingress.kubernetes.io/proxy-read-timeout: "600"
  nginx.ingress.kubernetes.io/proxy-send-timeout: "600"
```
Penser aussi aux **load balancers cloud** en amont, avec leur propre délai d'inactivité, et à la **compression**, à désactiver sur ces routes.

---

Quels repères de configuration pour un endpoint LLM ?
?
```text
timeout de lecture      300 à 900 s selon la longueur des réponses
buffering               désactivé sur les routes de streaming
taille max de requête   10 à 50 Mo  (documents, images, audio)
rate limit              en requêtes ET en tokens par minute
keep-alive              supérieur au timeout du client
```
Un défaut à 60 secondes coupe les réponses longues : c'est le symptôme le plus courant en mise en production ([[142-fiabilite-resilience-llm|fiabilité]]).

---

## Mises en situation

Mise en situation : en production, les réponses longues de ton assistant sont coupées au bout de 60 secondes, alors qu'elles fonctionnent en local. Que vérifies-tu ?
?
1. **Les timeouts de l'Ingress** et de tout proxy intermédiaire, souvent à 60 s par défaut
2. **Le buffering** : un proxy qui met la réponse en tampon casse le streaming, à désactiver pour ces routes
3. **La chaîne complète** : load balancer cloud, Ingress, gateway applicative, serveur d'inférence, chacun avec ses délais
4. **Les timeouts côté client** et les reconnexions automatiques
5. **Réduire le besoin** : limiter `max_tokens`, streamer dès le premier token pour que l'utilisateur voie la réponse arriver

**Piège** : augmenter seulement le timeout du serveur d'inférence, alors que la coupure vient du proxy.

---

Mise en situation : un client unique sature ton service d'inférence en lançant des milliers de requêtes en parallèle. Où poses-tu les limites ?
?
1. **À l'entrée** : rate limiting par clé ou par IP sur l'Ingress ou l'API gateway
2. **Dans la gateway LLM** : limites en requêtes et en **tokens** par minute, plus un budget ([[81-litellm-api-layer|LiteLLM]])
3. **Dans le serveur d'inférence** : concurrence maximale, pour préserver le SLO des autres utilisateurs
4. **Répondre proprement** : code 429 avec en-tête de reprise, plutôt qu'un timeout
5. **Surveiller** : taux de 429 par client, pour distinguer un abus d'une limite trop basse ([[93-monitoring-inference|monitoring]])

**Piège** : limiter uniquement le nombre de requêtes, alors qu'une seule requête à 100 000 tokens coûte bien plus cher.

---

## Connexions
- [[04-kubernetes-kubelet-cri|Kubernetes]] — le socle
- [[64-metriques-slo-inference|Métriques & SLO]] — rate limiting et timeouts pilotés par le SLO
- [[12-kubernetes-gpu-inference|Kubernetes GPU]] — les Pods derrière l'Ingress
- [[81-litellm-api-layer|LiteLLM]] — la gateway applicative derrière l'Ingress
- [[84-streaming-integration-applicative|Streaming & intégration]] — tampons et timeouts sur les flux SSE
- [[11-serveurs-inference-llm|Serveurs d'inférence]] — vLLM, SGLang, TensorRT-LLM et leur réglage
- [[112-cicd-modeles|CI/CD des modèles]] — eval gates, canary et rollback
- [[144-ux-ia-human-in-the-loop|UX & human-in-the-loop]] — ce que voit et valide l'utilisateur
- [[00-moc-ai-engineering|MOC AI Engineering]]
