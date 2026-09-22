# Monitoring de l'inférence & de l'usage — Flashcards
Tags: #flashcards #ai-engineering #observability #monitoring #inference #llm

Quelles couches faut-il monitorer pour un service d'inférence ?
?
Quatre couches, chacune avec sa source :
- **GPU** : santé et saturation du matériel (DCGM exporter)
- **Serveur d'inférence** : file d'attente, KV cache, latences (endpoint `/metrics` de vLLM ou SGLang)
- **Requêtes et usage** : qui consomme quoi, tokens, coûts, erreurs ([[81-litellm-api-layer|gateway]])
- **Qualité** : réponses valides et utiles ([[91-langfuse-observabilite|traces]], evals)

Un problème se voit souvent dans une couche alors que sa cause est dans une autre.

---

Quelles métriques clés expose vLLM ?
?
Au format Prometheus, sur `/metrics` :
- **Charge** : `vllm:num_requests_running`, `vllm:num_requests_waiting`
- **Mémoire** : `vllm:kv_cache_usage_perc`, `vllm:num_preemptions_total`
- **Latence** (histogrammes) : `vllm:time_to_first_token_seconds`, `vllm:inter_token_latency_seconds`, `vllm:e2e_request_latency_seconds`, `vllm:request_queue_time_seconds`
- **Volume** : `vllm:prompt_tokens_total`, `vllm:generation_tokens_total`, `vllm:request_success_total` (label `finished_reason`)

Les noms évoluent d'une version à l'autre : vérifier sur `/metrics`. Voir [[64-metriques-slo-inference|métriques & SLO]].

---

Quelles métriques GPU surveiller, et pourquoi l'utilisation GPU est-elle trompeuse ?
?
Avec le **DCGM exporter** de NVIDIA :
- `DCGM_FI_PROF_SM_ACTIVE` et `DCGM_FI_PROF_DRAM_ACTIVE` : charge réelle du calcul et de la **bande passante mémoire** (le goulot du decode)
- `DCGM_FI_DEV_POWER_USAGE`, `DCGM_FI_DEV_GPU_TEMP` : puissance, température, throttling
- `DCGM_FI_DEV_XID_ERRORS` : erreurs matérielles ou driver

`DCGM_FI_DEV_GPU_UTIL` dit seulement qu'un kernel tourne : il reste proche de 100 % même quand le GPU est sous-exploité. La **VRAM utilisée** (`DCGM_FI_DEV_FB_USED`) est aussi peu parlante, car vLLM **préalloue** la mémoire (`--gpu-memory-utilization`) : c'est le **taux d'occupation du KV cache** qu'il faut suivre.

---

Quelles métriques d'usage du modèle faut-il suivre ?
?
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
Des contrôles **déterministes et peu coûteux**, exécutés à chaque réponse :
- **Format** : JSON parsable et conforme au schéma ([[63-guided-generation|guided generation]])
- **Appels d'outils** : outil existant, arguments valides
- **Bornes** : longueur, langue attendue, réponse non vide
- **Contenu** : données personnelles, contenu interdit ([[101-securite-llm-guardrails|guardrails]])
- **RAG** : présence des citations attendues

Chaque échec est **compté comme une métrique** (taux d'échec de validation) et déclenche un retry, un fallback ou un message d'erreur propre.

---

Quels signaux de qualité suivre sans vérité terrain ?
?
- **Taux de refus** et de réponses vides
- **Boucles et répétitions** (n-grammes répétés)
- **Dérive de la longueur** des réponses
- **Confiance** : logprob moyenne ou entropie en baisse ([[65-probabilites-sampling|logprobs]])
- **Feedback utilisateur** (pouce, reformulations, régénérations)
- **LLM-as-judge** sur un échantillon, segmenté par tâche et par langue

Ces signaux alimentent la détection de dérive ([[113-monitoring-drift-feedback|monitoring & drift]]).

---

Quelles erreurs et quelle disponibilité surveiller ?
?
- **HTTP** : taux de 5xx, de **429** (rate limit, quota) et de timeouts
- **Serveur** : OOM, erreurs CUDA, **redémarrages de Pods**, préemptions de requêtes
- **Streaming** : flux interrompus avant la fin
- **Santé** : endpoint `/health` et readiness, qui ne passe au vert qu'une fois les poids chargés

La **disponibilité** se mesure du point de vue du client (requêtes réussies ÷ total), pas seulement par le fait que le Pod tourne.

---

Comment relier métriques et traces ?
?
Les métriques donnent l'**agrégat** (le p95 a doublé), les traces donnent l'**exemple** (quelle requête, quel prompt). Pour les relier :
- un **ID de requête** propagé de l'app à la gateway puis au serveur
- les **conventions OpenTelemetry GenAI** pour nommer les attributs : `gen_ai.request.model`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, `gen_ai.response.finish_reasons`
- des traces émises par le serveur lui-même (vLLM : `--otlp-traces-endpoint`)

---

Que contient un dashboard minimal d'inférence ?
?
Les **golden signals** adaptés aux LLM :
- **Trafic** : requêtes/s, tokens/s en entrée et en sortie
- **Latence** : TTFT, TPOT et E2E en p50, p95 et p99
- **Erreurs** : 5xx, 429, échecs de validation, `finish_reason=length`
- **Saturation** : file d'attente, KV cache, préemptions

Plus deux vues : **usage et coût** par équipe, **qualité** (scores, feedback).

---

Quelles alertes configurer ?
?
Alerter sur les **symptômes vus par les utilisateurs**, pas sur chaque cause :
- **Consommation du budget d'erreur** du SLO (burn rate) sur TTFT, TPOT et disponibilité
- **File d'attente** qui reste haute plusieurs minutes, **KV cache** saturé avec des préemptions
- **Hausse brutale** du taux de 5xx, de `length` ou d'échecs de validation
- **Coût journalier** au-dessus du budget
- **Erreurs XID** ou throttling thermique d'un GPU

---

Quels contrôles avant d'envoyer du trafic à un nouveau déploiement ?
?
1. **Readiness** : poids chargés, `/v1/models` renvoie le bon modèle et la **bonne révision**
2. **Smoke tests** : quelques prompts connus en greedy, avec le format de sortie attendu
3. **Benchmark de charge** à la concurrence cible : les SLO tiennent-ils ?
4. **Eval gate** : qualité au moins égale à la version en place ([[112-cicd-modeles|CI/CD des modèles]])
5. **Canary ou shadow** : une part du trafic réel, en comparant les mêmes métriques

---

Comment détecter une régression après un changement de modèle ou de configuration ?
?
En étiquetant **toutes les métriques** avec le modèle, sa révision et la configuration de serving (quantization, speculative decoding, version du moteur). On compare alors la **nouvelle version et l'ancienne sur le même trafic** : latences, erreurs, taux de validation, `finish_reason`, scores de qualité. Côté evals, on compare **question par question** ([[114-reproductibilite-variance|comparaison appariée]]).

---

Quelles précautions pour journaliser les prompts et les réponses ?
?
Ils contiennent souvent des **données personnelles ou confidentielles** :
- Journaliser les **métriques sans le contenu** par défaut, et le contenu seulement sur **échantillon** ou sur opt-in
- **Masquer** les données personnelles avant stockage
- Fixer une **durée de rétention** et restreindre l'accès aux logs
- Ne jamais mettre de contenu dans les **labels Prometheus** : cela exploserait la cardinalité et exposerait les données

---

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
- [[00-moc-ai-engineering|MOC AI Engineering]]
