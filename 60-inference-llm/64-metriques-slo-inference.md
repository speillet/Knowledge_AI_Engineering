# Métriques d'inférence & SLO — Flashcards
Tags: #flashcards #ai-engineering #inference #slo #llm

Qu'est-ce que le TTFT ?
?
<!--anki:68355e7b7b31743d5d46-->
**Time To First Token** : délai entre l'envoi de la requête et le **premier token reçu**. Il dépend de la file d'attente et du **prefill** (longueur du prompt). C'est la réactivité perçue en streaming.

---

Qu'est-ce que le TPOT (ou ITL) ?
?
<!--anki:68424b38777e6e2a472f-->
**Time Per Output Token** / **Inter-Token Latency** : le temps entre deux tokens générés pendant le **decode**. Il fixe la **vitesse de lecture** du streaming (ex. 30 ms/token ≈ 33 tokens/s).

---

Quels repères de latence viser selon l'usage ?
?
<!--anki:6f5537494a4a4244263c-->
```text
Autocomplétion de code      TTFT < 200 à 300 ms   (sinon inutilisable)
Assistant vocal             réponse < 1 s de bout en bout
Chat en streaming           TTFT < 800 ms, TPOT 20 à 50 ms
Agent en arrière-plan        minutes acceptables, montrer la progression
Batch et extraction          la latence n'a pas d'importance, le coût oui
```
Repère de lecture : **20 tokens par seconde** suffit à suivre un texte qui défile, soit un TPOT de 50 ms ([[144-ux-ia-human-in-the-loop|UX]]).

---

Comment se décompose la latence end-to-end ?
?
<!--anki:797160634d527b2e5e4d-->
```text
latence E2E ≈ TTFT + TPOT × (nb tokens de sortie − 1)
```
Une réponse longue est donc dominée par le TPOT, une réponse courte sur un long prompt par le TTFT.

---

Qu'est-ce que le throughput ?
?
<!--anki:49216f726b2d6a6f292d-->
Le **débit** du service : **tokens de sortie par seconde** (tous utilisateurs confondus) ou **requêtes par seconde**. C'est lui qui détermine le **coût par token**.

---

Quel compromis entre latence et débit ?
?
<!--anki:7a332c303b47545233-->
Un **batch plus gros** augmente le débit (GPU mieux rempli) mais **dégrade le TPOT** de chaque requête. On règle la **concurrence maximale** pour tenir le SLO de latence.

---

Qu'est-ce que le goodput ?
?
<!--anki:4b7157417d2d3c3f7e39-->
Le débit **des seules requêtes qui respectent le SLO** (TTFT et TPOT sous les seuils). Plus honnête que le throughput brut : servir vite des requêtes hors SLO ne compte pas.

---

Pourquoi raisonner en percentiles ?
?
<!--anki:4b306636786f4b446d71-->
Parce que la moyenne cache la **queue de distribution** : on fixe les SLO sur **p95/p99**. Un p50 excellent avec un p99 de 20 s reste une mauvaise expérience pour 1 % des utilisateurs.

---

À quoi ressemble un SLO d'inférence ?
?
<!--anki:6b77706546525e735472-->
Un objectif chiffré sur une fenêtre de temps, par exemple :
```text
p95 TTFT < 800 ms, p95 TPOT < 50 ms, disponibilité ≥ 99,5 % sur 30 jours
```
Il pilote le dimensionnement, les [[83-gateway-ingress|timeouts et le rate limiting]].

---

Qu'est-ce qui limite la concurrence d'un serveur ?
?
<!--anki:4e7d7c3d6a4c3c4f5f3b-->
Surtout la **VRAM disponible pour le [[61-kv-cache-attention|KV cache]]** : chaque requête active y occupe une place proportionnelle à son contexte. Quand le cache est plein, les requêtes **attendent en file** ou sont préemptées.

---

Quels signaux utiliser pour l'autoscaling ?
?
<!--anki:6e46644e3e766a2e4a7d-->
La **longueur de la file d'attente** (requêtes en attente) et le **taux d'occupation du KV cache**, exposés en métriques Prometheus par le serveur ([[11-serveurs-inference-llm|vLLM]]). **Pas l'utilisation GPU**, souvent proche de 100 % et peu discriminante.

---

Comment mesurer les performances d'un déploiement ?
?
<!--anki:505e777663703b53257c-->
Par des **benchmarks de charge** réalistes (distribution des longueurs de prompt/sortie, taux d'arrivée) : `vllm bench serve`, **GuideLLM**, **genai-perf** (NVIDIA). On trace la **courbe latence vs débit**.

---

Calcul : combien de requêtes simultanées faut-il servir pour 10 requêtes/s qui durent 8 secondes ?
?
<!--anki:44597b556d555a6b6b32-->
**Loi de Little** : concurrence = débit × durée.
```text
L = λ × W = 10 req/s × 8 s = 80 requêtes en vol en moyenne
```
Avec 8 000 tokens de contexte par requête sur un 8B, c'est **≈ 80 Go de KV cache** : plus d'un H100 ([[61-kv-cache-attention|calcul du KV cache]]). Réduire la **durée** (moins de tokens de sortie, decode plus rapide) réduit la concurrence nécessaire autant qu'ajouter des GPU.

---

## Mises en situation

Mise en situation : le produit demande « une réponse en moins de 2 secondes » pour un assistant qui streame des réponses de 400 tokens. Comment traduis-tu ce besoin en SLO ?
?
<!--anki:772b352d2f4c5b694141-->
1. **Décomposer** : en streaming, l'utilisateur perçoit d'abord le **TTFT**, puis la vitesse de lecture (**TPOT**)
2. **Poser des cibles** : par exemple p95 TTFT < 800 ms et p95 TPOT < 50 ms, soit environ 20 tokens par seconde
3. **Vérifier la cohérence** : 400 tokens à 50 ms font 20 s au total. Si le besoin est « tout en 2 s », il faut raccourcir la réponse, pas accélérer le GPU
4. **Choisir les percentiles** et la fenêtre (p95 sur 30 jours), pas la moyenne
5. **Valider par un benchmark** de charge réaliste avant de s'engager ([[93-monitoring-inference|monitoring]])

**Piège** : s'engager sur une latence totale sans fixer la longueur des réponses.

---

Mise en situation : ton dashboard affiche 100 % d'utilisation GPU et l'équipe conclut qu'il faut acheter des GPU. Comment vérifies-tu ?
?
<!--anki:4a3363746c6836453d3b-->
1. **Se méfier de cette métrique** : elle indique qu'un kernel tourne, pas que le GPU est bien exploité
2. **Regarder les vraies causes** : file d'attente, occupation du KV cache, préemptions ([[93-monitoring-inference|métriques vLLM]])
3. **Tracer la courbe latence-débit** : à quel niveau de charge le SLO casse-t-il vraiment ?
4. **Mesurer le goodput** : le débit des seules requêtes qui respectent le SLO
5. **Chercher les gains gratuits** avant d'acheter : quantization, prefix caching, chunked prefill, limitation du contexte

**Piège** : dimensionner sur le pic absolu plutôt que sur le p95 du trafic réel.

---

Mise en situation : ton autoscaling se déclenche trop tard, et des requêtes attendent plusieurs secondes avant d'être traitées. Sur quoi le règles-tu ?
?
<!--anki:6c6759312a4c4c493574-->
1. **Pas sur l'utilisation GPU**, presque toujours proche de 100 %
2. **Signaux utiles** : longueur de la file d'attente et taux d'occupation du KV cache, exposés en métriques par le serveur
3. **Anticiper le temps de démarrage** : un réplica LLM met plusieurs minutes à charger ses poids ([[10-images-modeles-poids|cold start]])
4. **Garder un coussin** : réplicas chauds ou pool préchauffé pour absorber les pics
5. **Alerter sur le SLO** plutôt que sur la cause : burn rate du TTFT p95

**Piège** : un scale-to-zero agressif qui fait payer un cold start de plusieurs minutes au premier utilisateur.

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
- [[69-roofline-prefill-decode|Roofline & désagrégation]] — l'interférence prefill/decode derrière les pics de TPOT
- [[163-voix-temps-reel|Voix & agents temps réel]] — le TTFT dans un budget de latence conversationnel
- [[112-cicd-modeles|CI/CD des modèles]] — eval gates, canary et rollback
- [[138-modeles-raisonnement|Modèles de raisonnement]] — test-time compute et budget de réflexion
- [[142-fiabilite-resilience-llm|Fiabilité & résilience]] — timeouts, retries, fallbacks et dégradation
- [[66-prefix-caching-radix-attention|Prefix caching]] — réutiliser le calcul des préfixes communs
- [[81-litellm-api-layer|LiteLLM]] — la gateway entre applications et modèles
- [[82-routing-llm|Routing LLM]] — choisir le modèle par requête, fallbacks et cache sémantique
- [[84-streaming-integration-applicative|Streaming & intégration]] — SSE, annulation et tâches longues
- [[137-long-contexte|Long contexte]] — limites et coût des longues fenêtres
- [[146-choix-modeles|Choix de modèles]] — critères, benchmarks et migration
- [[00-moc-ai-engineering|MOC AI Engineering]]
