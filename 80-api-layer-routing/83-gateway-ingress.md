# Ingress & API gateway — Flashcards
Tags: #flashcards #ai-engineering #kubernetes #ingress #networking

Qu'est-ce qu'un Ingress dans Kubernetes ?
?
La **porte d'entrée HTTP(S) du cluster** : il route le trafic externe vers les Services selon l'hôte et le chemin.

---

Un Ingress fonctionne-t-il seul ?
?
**Non.** Il faut un **Ingress controller** (nginx, Traefik, HAProxy…) qui applique concrètement les règles.

---

Que gère typiquement un Ingress ?
?
- Routage **par hôte** (`api.example.com`) et **par chemin** (`/v1/...`)
- **Terminaison TLS** (HTTPS)

---

Qu'est-ce que la Gateway API ?
?
Le **successeur de l'Ingress** dans Kubernetes : API plus expressive (routes, classes, délégation par équipe).

---

Quelle différence entre Ingress et API gateway ?
?
L'**Ingress** fait du routage L7 ; une **API gateway** ajoute auth, rate limiting, quotas, transformation de requêtes.

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
Les réponses LLM sont **longues et streamées** : il faut des **timeouts allongés** et désactiver le buffering sur l'Ingress/proxy.

---

## Connexions
- [[04-kubernetes-kubelet-cri|Kubernetes]] — le socle
- [[64-metriques-slo-inference|Métriques & SLO]] — rate limiting et timeouts pilotés par le SLO
- [[12-kubernetes-gpu-inference|Kubernetes GPU]] — les Pods derrière l'Ingress
- [[81-litellm-api-layer|LiteLLM]] — la gateway applicative derrière l'Ingress
- [[00-moc-ai-engineering|MOC AI Engineering]]
