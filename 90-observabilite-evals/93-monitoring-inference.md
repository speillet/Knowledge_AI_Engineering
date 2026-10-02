# Monitoring de l'inférence & de l'usage — Flashcards
Tags: #flashcards #ai-engineering #observability #monitoring #inference #llm
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.
<!-- summary: monitoring ou observabilité, couches à monitorer, métriques vLLM et GPU (DCGM), usage par équipe, finish_reason, validations de chaque réponse, signaux de qualité sans vérité terrain, erreurs et disponibilité, traces OpenTelemetry GenAI, dashboard, alertes, contrôles avant mise en production, détection de régression, journalisation des prompts. -->

Quelles couches faut-il monitorer pour un service d'inférence ?
?
<!--anki:4f41512c3177716b6679-->
Quatre couches, chacune avec sa source :
- **GPU** : santé et saturation du matériel (DCGM exporter)
- **Serveur d'inférence** : file d'attente, KV cache, latences (endpoint `/metrics` de vLLM ou SGLang)
- **Requêtes et usage** : qui consomme quoi, tokens, coûts, erreurs ([[81-litellm-api-layer|gateway]])
- **Qualité** : réponses valides et utiles ([[91-langfuse-observabilite|traces]], evals)

Un problème se voit souvent dans une couche alors que sa cause est dans une autre.

---

Quelles métriques clés expose vLLM ?
?
<!--anki:715b2636234f51262b58-->
Au format Prometheus, sur `/metrics` :
- **Charge** : `vllm:num_requests_running`, `vllm:num_requests_waiting`
- **Mémoire** : `vllm:kv_cache_usage_perc`, `vllm:num_preemptions_total`
- **Latence** (histogrammes) : `vllm:time_to_first_token_seconds`, `vllm:inter_token_latency_seconds`, `vllm:e2e_request_latency_seconds`, `vllm:request_queue_time_seconds`
- **Volume** : `vllm:prompt_tokens_total`, `vllm:generation_tokens_total`, `vllm:request_success_total` (label `finished_reason`)

Les noms évoluent d'une version à l'autre : vérifier sur `/metrics`. Voir [[64-metriques-slo-inference|métriques & SLO]].
```promql
# TTFT p95 sur 5 minutes
histogram_quantile(0.95,
  sum(rate(vllm:time_to_first_token_seconds_bucket[5m])) by (le))

# requêtes en attente et occupation du cache
sum(vllm:num_requests_waiting)
avg(vllm:kv_cache_usage_perc)

# part de réponses tronquées
sum(rate(vllm:request_success_total{finished_reason="length"}[15m]))
  / sum(rate(vllm:request_success_total[15m]))
```

---

Quelles métriques GPU surveiller pour un service d'inférence ?
?
<!--anki:672e573d287b78522835-->
Avec le **DCGM exporter** de NVIDIA :
- `DCGM_FI_PROF_SM_ACTIVE` et `DCGM_FI_PROF_DRAM_ACTIVE` : charge réelle du calcul et de la **bande passante mémoire** (le goulot du decode)
- `DCGM_FI_DEV_POWER_USAGE`, `DCGM_FI_DEV_GPU_TEMP` : puissance, température, throttling
- `DCGM_FI_DEV_XID_ERRORS` : erreurs matérielles ou driver

---

Pourquoi l'utilisation GPU et la VRAM utilisée sont-elles des métriques trompeuses ?
?
<!--anki:4c64355e3f403432635f-->
`DCGM_FI_DEV_GPU_UTIL` dit seulement qu'un kernel tourne : il reste proche de 100 % même quand le GPU est sous-exploité. La **VRAM utilisée** (`DCGM_FI_DEV_FB_USED`) est aussi peu parlante, car vLLM **préalloue** la mémoire (`--gpu-memory-utilization`) : c'est le **taux d'occupation du KV cache** qu'il faut suivre.

---

Quelles métriques d'usage du modèle faut-il suivre ?
?
<!--anki:73494d5d7848655a2e6a-->
Par **équipe, application, clé et modèle** :
- **Requêtes** et **tokens d'entrée, de sortie et lus en cache**
- **Coût** et sa tendance ([[122-finops-llm|FinOps]])
- **Distribution des longueurs** de prompt et de réponse (p50, p95), qui dimensionne le KV cache
- **Concurrence de pointe** et répartition horaire
- **Top consommateurs** et usages inattendus

On les collecte à la **gateway**, qui voit toutes les requêtes et connaît l'appelant.

---

Que révèle la répartition des finish_reason ?
?
<!--anki:705253437b4d767a2b6e-->
La raison pour laquelle chaque génération s'est arrêtée :
- `stop` : fin normale
- `length` : **coupée par `max_tokens`**, avec des réponses tronquées ou un JSON invalide. Une hausse signale un `max_tokens` trop bas ou un modèle qui **boucle**
- `tool_calls` : appel d'outil
- `content_filter` : bloquée par un filtre
- `abort` (côté serveur) : client déconnecté ou timeout

On suit son **taux par route et par modèle**, pas seulement le total.

---

Quelles validations appliquer à chaque réponse en production ?
?
<!--anki:786c475440625e38524d-->
Des contrôles **déterministes et peu coûteux**, exécutés à chaque réponse :
- **Format** : JSON parsable et conforme au schéma ([[63-guided-generation|guided generation]])
- **Appels d'outils** : outil existant, arguments valides
- **Bornes** : longueur, langue attendue, réponse non vide
- **Contenu** : données personnelles, contenu interdit ([[101-securite-llm-guardrails|guardrails]])
- **RAG** : présence des citations attendues

Chaque échec est **compté comme une métrique** (taux d'échec de validation) et déclenche un retry, un fallback ou un message d'erreur propre.

---

Quels signaux automatiques révèlent une baisse de qualité sans vérité terrain ?
?
<!--anki:6955656e71496a394f63-->
- **Taux de refus** et de réponses vides
- **Boucles et répétitions** (n-grammes répétés)
- **Dérive de la longueur** des réponses
- **Confiance** : logprob moyenne ou entropie en baisse ([[65-probabilites-sampling|logprobs]])

---

Quels signaux humains ou jugés suivre pour la qualité, sans vérité terrain ?
?
<!--anki:73402f3540435a21636c-->
- **Feedback utilisateur** (pouce, reformulations, régénérations)
- **LLM-as-judge** sur un échantillon, segmenté par tâche et par langue

Ces signaux alimentent la détection de dérive ([[113-monitoring-drift-feedback|monitoring & drift]]).

---

Quelles erreurs et quelle disponibilité surveiller ?
?
<!--anki:6d796f7b3d3f3e262c4e-->
- **HTTP** : taux de 5xx, de **429** (rate limit, quota) et de timeouts
- **Serveur** : OOM, erreurs CUDA, **redémarrages de Pods**, préemptions de requêtes
- **Streaming** : flux interrompus avant la fin
- **Santé** : endpoint `/health` et readiness, qui ne passe au vert qu'une fois les poids chargés

La **disponibilité** se mesure du point de vue du client (requêtes réussies ÷ total), pas seulement par le fait que le Pod tourne.

---

Comment relier métriques et traces ?
?
<!--anki:77495f4f435b3625542b-->
Les métriques donnent l'**agrégat** (le p95 a doublé), les traces donnent l'**exemple** (quelle requête, quel prompt). Pour les relier :
- un **ID de requête** propagé de l'app à la gateway puis au serveur
- les **conventions OpenTelemetry GenAI** pour nommer les attributs : `gen_ai.request.model`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, `gen_ai.response.finish_reasons`
- des traces émises par le serveur lui-même (vLLM : `--otlp-traces-endpoint`)

---

Que contient un dashboard minimal d'inférence ?
?
<!--anki:4c4c2d5a2c6c683f564b-->
Les **golden signals** adaptés aux LLM :
- **Trafic** : requêtes/s, tokens/s en entrée et en sortie
- **Latence** : TTFT, TPOT et E2E en p50, p95 et p99
- **Erreurs** : 5xx, 429, échecs de validation, `finish_reason=length`
- **Saturation** : file d'attente, KV cache, préemptions

Plus deux vues : **usage et coût** par équipe, **qualité** (scores, feedback).

---

Quelles alertes configurer ?
?
<!--anki:6954683b7c7e24746059-->
Alerter sur les **symptômes vus par les utilisateurs**, pas sur chaque cause :
- **Consommation du budget d'erreur** du SLO (burn rate) sur TTFT, TPOT et disponibilité
- **File d'attente** qui reste haute plusieurs minutes, **KV cache** saturé avec des préemptions
- **Hausse brutale** du taux de 5xx, de `length` ou d'échecs de validation
- **Coût journalier** au-dessus du budget
- **Erreurs XID** ou throttling thermique d'un GPU

---

Quels contrôles avant d'envoyer du trafic à un nouveau déploiement ?
?
<!--anki:433a7965647929264862-->
1. **Readiness** : poids chargés, `/v1/models` renvoie le bon modèle et la **bonne révision**
2. **Smoke tests** : quelques prompts connus en greedy, avec le format de sortie attendu
3. **Benchmark de charge** à la concurrence cible : les SLO tiennent-ils ?
4. **Eval gate** : qualité au moins égale à la version en place ([[112-cicd-modeles|CI/CD des modèles]])
5. **Canary ou shadow** : une part du trafic réel, en comparant les mêmes métriques

---

Comment détecter une régression après un changement de modèle ou de configuration ?
?
<!--anki:6965217e3d6c7a2a2879-->
En étiquetant **toutes les métriques** avec le modèle, sa révision et la configuration de serving (quantization, speculative decoding, version du moteur). On compare alors la **nouvelle version et l'ancienne sur le même trafic** : latences, erreurs, taux de validation, `finish_reason`, scores de qualité. Côté evals, on compare **question par question** ([[114-reproductibilite-variance|comparaison appariée]]).

---

Quelles précautions pour journaliser les prompts et les réponses ?
?
<!--anki:45542b4d446e24716143-->
Ils contiennent souvent des **données personnelles ou confidentielles** :
- Journaliser les **métriques sans le contenu** par défaut, et le contenu seulement sur **échantillon** ou sur opt-in
- **Masquer** les données personnelles avant stockage
- Fixer une **durée de rétention** et restreindre l'accès aux logs
- Ne jamais mettre de contenu dans les **labels Prometheus** : cela exploserait la cardinalité et exposerait les données

---

À ne pas confondre : monitoring et observabilité ?
?
<!--anki:42447a46547b5f583055-->
- **Monitoring** : surveiller des **indicateurs connus à l'avance** (latence, taux d'erreur, coût) et alerter sur des seuils. Il répond à « est-ce que ça va ? »
- **Observabilité** : pouvoir **expliquer un comportement imprévu** à partir des traces, logs et métriques détaillés. Elle répond à « pourquoi ça ne va pas ? »

Pour un système LLM, le monitoring détecte une chute de qualité ; ce sont les **traces complètes** qui permettent d'en trouver la cause ([[98-debogage-agents|débogage]]).

---

## Mises en situation

Mise en situation : on te signale « l'assistant est lent ce matin ». Tu n'as que cette phrase. Dans quel ordre regardes-tu ?
?
<!--anki:7a24417a6c476d607978-->
1. **Confirmer et quantifier** : TTFT et TPOT en p95, sur la bonne route et la bonne période
2. **Saturation** : file d'attente, occupation du KV cache, préemptions. C'est la cause la plus fréquente
3. **Usage** : un client qui envoie des prompts beaucoup plus longs, ou un pic de trafic
4. **Infrastructure** : erreurs XID, throttling thermique, un réplica tombé, un nœud dégradé
5. **Changement récent** : déploiement, nouveau prompt, nouveau modèle, cache de préfixes cassé

**Piège** : regarder l'utilisation GPU, qui sera à 100 % dans tous les cas.

---

Mise en situation : ton service ne renvoie aucune erreur, mais le support reçoit des plaintes sur des réponses tronquées. Quelle métrique aurait dû t'alerter ?
?
<!--anki:4f53557e6f40256e5434-->
1. **La répartition des `finish_reason`** : une hausse de `length` signale des réponses coupées par `max_tokens`
2. **Vérifier la cause** : limite trop basse, prompts plus longs, ou modèle qui boucle
3. **Croiser** avec le taux d'échec de validation, notamment le JSON invalide dû à la troncature
4. **Corriger** : ajuster `max_tokens`, demander des réponses plus concises, découper la tâche
5. **Alerter** sur ce taux, pas seulement sur les codes d'erreur HTTP

**Piège** : considérer qu'une réponse renvoyée avec un code 200 est une réponse réussie.

---

Mise en situation : le responsable conformité demande si vous journalisez les conversations des utilisateurs. Que réponds-tu, et que vérifies-tu ?
?
<!--anki:4376464f387c74687054-->
1. **Distinguer** métriques (sans contenu) et traces (avec contenu), et dire ce qui est réellement conservé
2. **Par défaut** : métriques sans contenu, contenu seulement sur échantillon ou opt-in
3. **Masquer** les données personnelles avant stockage, et restreindre l'accès aux traces ([[152-pii-confidentialite|PII]])
4. **Rétention** définie et appliquée, y compris dans les sauvegardes ([[154-rgpd-llm|RGPD]])
5. **Vérifier les labels Prometheus** : jamais de contenu utilisateur, sous peine d'explosion de cardinalité et d'exposition

**Piège** : découvrir que des prompts complets sont partis dans les logs applicatifs, hors du dispositif de traces.

---

## Sources

- [vLLM — métriques de production](https://docs.vllm.ai/en/latest/usage/metrics/)
- [OpenTelemetry — conventions sémantiques GenAI](https://github.com/open-telemetry/semantic-conventions-genai)

## Connexions
- [[64-metriques-slo-inference|Métriques d'inférence & SLO]] — TTFT, TPOT, goodput, percentiles
- [[91-langfuse-observabilite|Langfuse & observabilité LLM]] — les traces applicatives
- [[113-monitoring-drift-feedback|Monitoring, drift & feedback]] — la qualité dans le temps
- [[81-litellm-api-layer|LiteLLM]] — la gateway qui voit tout l'usage
- [[122-finops-llm|FinOps LLM]] — attribuer et piloter les coûts
- [[112-cicd-modeles|CI/CD des modèles]] — eval gate, canary, rollback
- [[11-serveurs-inference-llm|Serveurs d'inférence]] — les endpoints `/metrics` et `/health`
- [[12-kubernetes-gpu-inference|Kubernetes GPU & inférence]] — autoscaling sur ces signaux
- [[68-quantization|Quantization]] — valider un modèle quantizé
- [[67-speculative-decoding|Speculative decoding]] — suivre le taux d'acceptation
- [[115-plateformes-agents-gouvernance|Plateformes d'agents — Architecture & gouvernance]] — audit et traces des agents
- [[38-plateformes-agents|Plateformes d'agents]] — l'observabilité fournie par la plateforme
- [[105-devsecops-ia-agentique|DevSecOps pour l'IA agentique]] — journaux de sécurité et détection
- [[97-evals-online-ab-testing|Evals online & A/B testing]] — qualité en production
- [[142-fiabilite-resilience-llm|Fiabilité & résilience]] — timeouts, retries, fallbacks et dégradation
- [[61-kv-cache-attention|KV cache]] — la mémoire qui limite la concurrence
- [[85-carte-protocoles-agentiques|Carte des protocoles]] — quel protocole à quelle frontière de l'agent
- [[95-llm-as-judge|LLM-as-a-judge]] — noter automatiquement, et valider le juge
- [[00-moc-ai-engineering|MOC AI Engineering]]
