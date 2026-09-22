# Métriques d'inférence & SLO — Flashcards
Tags: #flashcards #ai-engineering #inference #slo #llm

Qu'est-ce que le TTFT ?
?
**Time To First Token** : délai entre l'envoi de la requête et le **premier token reçu**. Il dépend de la file d'attente et du **prefill** (longueur du prompt). C'est la réactivité perçue en streaming.

---

Qu'est-ce que le TPOT (ou ITL) ?
?
**Time Per Output Token** / **Inter-Token Latency** : le temps entre deux tokens générés pendant le **decode**. Il fixe la **vitesse de lecture** du streaming (ex. 30 ms/token ≈ 33 tokens/s).

---

Comment se décompose la latence end-to-end ?
?
```text
latence E2E ≈ TTFT + TPOT × (nb tokens de sortie − 1)
```
Une réponse longue est donc dominée par le TPOT, une réponse courte sur un long prompt par le TTFT.

---

Qu'est-ce que le throughput ?
?
Le **débit** du service : **tokens de sortie par seconde** (tous utilisateurs confondus) ou **requêtes par seconde**. C'est lui qui détermine le **coût par token**.

---

Quel compromis entre latence et débit ?
?
Un **batch plus gros** augmente le débit (GPU mieux rempli) mais **dégrade le TPOT** de chaque requête. On règle la **concurrence maximale** pour tenir le SLO de latence.

---

Qu'est-ce que le goodput ?
?
Le débit **des seules requêtes qui respectent le SLO** (TTFT et TPOT sous les seuils). Plus honnête que le throughput brut : servir vite des requêtes hors SLO ne compte pas.

---

Pourquoi raisonner en percentiles ?
?
Parce que la moyenne cache la **queue de distribution** : on fixe les SLO sur **p95/p99**. Un p50 excellent avec un p99 de 20 s reste une mauvaise expérience pour 1 % des utilisateurs.

---

À quoi ressemble un SLO d'inférence ?
?
Un objectif chiffré sur une fenêtre de temps, par exemple :
```text
p95 TTFT < 800 ms, p95 TPOT < 50 ms, disponibilité ≥ 99,5 % sur 30 jours
```
Il pilote le dimensionnement, les [[83-gateway-ingress|timeouts et le rate limiting]].

---

Qu'est-ce qui limite la concurrence d'un serveur ?
?
Surtout la **VRAM disponible pour le [[61-kv-cache-attention|KV cache]]** : chaque requête active y occupe une place proportionnelle à son contexte. Quand le cache est plein, les requêtes **attendent en file** ou sont préemptées.

---

Quels signaux utiliser pour l'autoscaling ?
?
La **longueur de la file d'attente** (requêtes en attente) et le **taux d'occupation du KV cache**, exposés en métriques Prometheus par le serveur ([[11-serveurs-inference-llm|vLLM]]). **Pas l'utilisation GPU**, souvent proche de 100 % et peu discriminante.

---

Comment mesurer les performances d'un déploiement ?
?
Par des **benchmarks de charge** réalistes (distribution des longueurs de prompt/sortie, taux d'arrivée) : `vllm bench serve`, **GuideLLM**, **genai-perf** (NVIDIA). On trace la **courbe latence vs débit**.

---

## Connexions
- [[61-kv-cache-attention|KV cache]] — la concurrence plafonnée par la VRAM
- [[62-optimisations-inference|Optimisations d'inférence]] — les leviers sur TTFT et TPOT
- [[12-kubernetes-gpu-inference|Kubernetes GPU]] — autoscaling piloté par ces signaux
- [[83-gateway-ingress|Ingress & API gateway]] — rate limiting et timeouts
- [[91-langfuse-observabilite|Langfuse]] — du système à l'application
- [[121-couts-inference|Coûts d'inférence]] — goodput ↔ coût par token
- [[67-speculative-decoding|Speculative decoding]] — réduire le TPOT
- [[68-quantization|Quantization]] — plus de débit et de concurrence par GPU
- [[93-monitoring-inference|Monitoring de l'inférence]] — les métriques concrètes (vLLM, GPU, usage)
- [[00-moc-ai-engineering|MOC AI Engineering]]
