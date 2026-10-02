# LiteLLM (API layer) — Flashcards
Tags: #flashcards #ai-engineering #api-layer #litellm #llm
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.
<!-- summary: SDK ou proxy, virtual keys, budgets, rate limits, fallbacks, load balancing, callbacks d'observabilité, alternatives (gateways auto-hébergées, services des clouds, agrégateurs). -->

Qu'est-ce qu'une API layer (LLM gateway) ?
?
<!--anki:79752c38462d5a6c3765-->
Une **couche unique entre les applications et tous les modèles** (API cloud et modèles auto-hébergés) : une seule interface, et des fonctions transverses centralisées (auth, budgets, fallbacks, logs).

---

Qu'est-ce que LiteLLM ?
?
<!--anki:496b6e43213c2b593774-->
Un projet open source qui expose **plus de 100 fournisseurs de LLM au format de l'API OpenAI**. Il existe sous deux formes : un **SDK Python** et un **proxy** (serveur gateway).

---

SDK ou proxy LiteLLM ?
?
<!--anki:7531606c2c72556e5870-->
- **SDK** : bibliothèque dans le code (`litellm.completion(...)`), idéale pour un seul service
- **Proxy** : serveur **centralisé** pour toute l'organisation, avec clés, budgets et observabilité partagés

---

À quoi ressemble une configuration du proxy ?
?
<!--anki:75244e56214c4d524272-->
```yaml
model_list:
  - model_name: chat-default
    litellm_params:
      model: hosted_vllm/meta-llama/Llama-3.1-8B-Instruct
      api_base: http://vllm.inference.svc:8000/v1
  - model_name: chat-default
    litellm_params:
      model: anthropic/claude-sonnet-4-5
```
Deux déploiements sous le même nom : le proxy **répartit la charge** entre eux.

---

Que sont les virtual keys de LiteLLM ?
?
<!--anki:685b522c2437213a3750-->
Des **clés API émises par le proxy** (par équipe, projet ou utilisateur) : les vraies clés des fournisseurs restent **secrètes**, et chaque virtual key a ses **modèles autorisés, budget et limites**.

---

Comment LiteLLM maîtrise-t-il les coûts ?
?
<!--anki:462c433f457b28282c46-->
Par le **suivi des dépenses** par clé, équipe ou utilisateur, des **budgets** (plafond sur une période) et des **rate limits** en requêtes et tokens par minute (RPM/TPM).

---

Comment LiteLLM améliore-t-il la fiabilité ?
?
<!--anki:6369583735646953616f-->
- **Retries** sur erreurs transitoires
- **Fallbacks** vers un autre modèle ou fournisseur si le premier échoue
- **Load balancing** entre déploiements, avec cooldown des déploiements en erreur

---

Comment relier LiteLLM à l'observabilité ?
?
<!--anki:4e6e34374d5732535658-->
Par des **callbacks** : chaque appel est envoyé à [[91-langfuse-observabilite|Langfuse]] (ou OpenTelemetry, Prometheus) avec prompt, réponse, tokens, coût et latence — sans instrumenter chaque application.

---

Où se place LiteLLM dans la stack ?
?
<!--anki:65484f7c36453a766272-->
```text
Client → Ingress (TLS) → LiteLLM (auth, quotas, routing) → vLLM / API cloud
```
L'[[83-gateway-ingress|Ingress]] gère le réseau ; LiteLLM gère la **logique propre aux LLM**.

---

Quelles alternatives à LiteLLM ?
?
<!--anki:4a785a514860456e7223-->
- **Gateways auto-hébergées** : Portkey, Kong AI Gateway, Envoy AI Gateway, agentgateway (qui gère aussi MCP et A2A)
- **Services managés des clouds** : gateways IA intégrées aux offres AWS, Azure et Google
- **Agrégateurs SaaS** : OpenRouter, pour l'accès multi-fournisseurs sans infrastructure

Critères : fournisseurs couverts, budgets et virtual keys, observabilité, latence ajoutée, et possibilité d'auto-héberger si les données ne doivent pas sortir.

---

## Mises en situation

Mise en situation : cinq équipes appellent directement les API de trois fournisseurs, avec des clés partagées par copier-coller. La facture mensuelle n'est attribuable à personne. Par quoi commences-tu ?
?
<!--anki:6a6e56307e5b2b4c726f-->
1. **Mettre une gateway devant** : toutes les applications passent par le proxy, au format de l'API OpenAI
2. **Virtual keys** par équipe et par projet : les vraies clés des fournisseurs redeviennent secrètes
3. **Budgets et rate limits** par clé, avec alertes avant dépassement ([[122-finops-llm|FinOps]])
4. **Callbacks d'observabilité** : traces, coûts et latences centralisés sans instrumenter chaque application ([[91-langfuse-observabilite|Langfuse]])
5. **Migrer progressivement** : commencer par une équipe volontaire, puis fermer l'accès direct

**Piège** : faire de la gateway un point de défaillance unique sans réplicas ni supervision.

---

Mise en situation : ton fournisseur principal connaît une panne de 40 minutes en pleine journée. Comment ton architecture aurait-elle dû réagir ?
?
<!--anki:67297e4a71396d5d5e4f-->
1. **Fallback configuré** vers un autre fournisseur ou un modèle auto-hébergé pour les routes critiques
2. **Retries** avec backoff sur les erreurs transitoires, et **cooldown** du déploiement en erreur
3. **Dégradation acceptable** : modèle moins bon mais disponible, ou réponse d'attente explicite ([[142-fiabilite-resilience-llm|fiabilité]])
4. **Vérifier la compatibilité** : le modèle de secours doit avoir été testé sur les mêmes evals
5. **Mesurer** : taux d'erreurs et bascules, pour savoir a posteriori ce qui s'est passé

**Piège** : déclarer un fallback jamais testé, qui échoue au moment où on en a besoin.

---

## Sources

- [LiteLLM — proxy et gateway](https://docs.litellm.ai/docs/simple_proxy)

## Connexions
- [[83-gateway-ingress|Ingress & API gateway]] — l'entrée réseau devant LiteLLM
- [[82-routing-llm|Routing LLM]] — choisir le bon modèle par requête
- [[91-langfuse-observabilite|Langfuse]] — les traces envoyées par callbacks
- [[64-metriques-slo-inference|Métriques & SLO]] — rate limits et timeouts
- [[11-serveurs-inference-llm|Serveurs d'inférence]] — les backends auto-hébergés
- [[122-finops-llm|FinOps LLM]] — budgets et attribution des coûts
- [[93-monitoring-inference|Monitoring de l'inférence]] — les métriques d'usage collectées à la gateway
- [[142-fiabilite-resilience-llm|Fiabilité & résilience]] — retries, fallbacks, circuit breakers
- [[84-streaming-integration-applicative|Streaming & intégration]] — relayer et annuler les flux
- [[101-securite-llm-guardrails|Sécurité LLM]] — injection, exfiltration et guardrails
- [[123-caching-agressif|Caching]] — prompt caching et caches de réponses
- [[141-system-design-llm|System design LLM]] — la méthode de conception
- [[33-mcp|MCP]] — le protocole standard entre agents et outils
- [[38-plateformes-agents|Plateformes d'agents]] — runtime, sandbox, gateway d'outils et identité
- [[41-automatisation-code-nocode|Automatisation code & no-code]] — workflows et outils no-code
- [[46-crewai-crews|CrewAI — Crews]] — équipes d'agents à rôles
- [[85-carte-protocoles-agentiques|Carte des protocoles]] — quel protocole à quelle frontière de l'agent
- [[00-moc-ai-engineering|MOC AI Engineering]]
