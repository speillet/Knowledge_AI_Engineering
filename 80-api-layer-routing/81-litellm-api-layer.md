# LiteLLM (API layer) — Flashcards
Tags: #flashcards #ai-engineering #api-layer #litellm #llm

Qu'est-ce qu'une API layer (LLM gateway) ?
?
Une **couche unique entre les applications et tous les modèles** (API cloud et modèles auto-hébergés) : une seule interface, et des fonctions transverses centralisées (auth, budgets, fallbacks, logs).

---

Qu'est-ce que LiteLLM ?
?
Un projet open source qui expose **plus de 100 fournisseurs de LLM au format de l'API OpenAI**. Il existe sous deux formes : un **SDK Python** et un **proxy** (serveur gateway).

---

SDK ou proxy LiteLLM ?
?
- **SDK** : bibliothèque dans le code (`litellm.completion(...)`), idéale pour un seul service
- **Proxy** : serveur **centralisé** pour toute l'organisation, avec clés, budgets et observabilité partagés

---

À quoi ressemble une configuration du proxy ?
?
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

Que sont les virtual keys ?
?
Des **clés API émises par le proxy** (par équipe, projet ou utilisateur) : les vraies clés des fournisseurs restent **secrètes**, et chaque virtual key a ses **modèles autorisés, budget et limites**.

---

Comment LiteLLM maîtrise-t-il les coûts ?
?
Par le **suivi des dépenses** par clé, équipe ou utilisateur, des **budgets** (plafond sur une période) et des **rate limits** en requêtes et tokens par minute (RPM/TPM).

---

Comment LiteLLM améliore-t-il la fiabilité ?
?
- **Retries** sur erreurs transitoires
- **Fallbacks** vers un autre modèle ou fournisseur si le premier échoue
- **Load balancing** entre déploiements, avec cooldown des déploiements en erreur

---

Comment relier LiteLLM à l'observabilité ?
?
Par des **callbacks** : chaque appel est envoyé à [[91-langfuse-observabilite|Langfuse]] (ou OpenTelemetry, Prometheus) avec prompt, réponse, tokens, coût et latence — sans instrumenter chaque application.

---

Où se place LiteLLM dans la stack ?
?
```text
Client → Ingress (TLS) → LiteLLM (auth, quotas, routing) → vLLM / API cloud
```
L'[[83-gateway-ingress|Ingress]] gère le réseau ; LiteLLM gère la **logique propre aux LLM**.

---

Quelles alternatives à LiteLLM ?
?
**Portkey**, **Kong AI Gateway**, **Envoy AI Gateway** (auto-hébergés ou managés), ou un service SaaS comme **OpenRouter** pour l'accès multi-fournisseurs.

---

## Connexions
- [[83-gateway-ingress|Ingress & API gateway]] — l'entrée réseau devant LiteLLM
- [[82-routing-llm|Routing LLM]] — choisir le bon modèle par requête
- [[91-langfuse-observabilite|Langfuse]] — les traces envoyées par callbacks
- [[64-metriques-slo-inference|Métriques & SLO]] — rate limits et timeouts
- [[11-serveurs-inference-llm|Serveurs d'inférence]] — les backends auto-hébergés
- [[122-finops-llm|FinOps LLM]] — budgets et attribution des coûts
- [[00-moc-ai-engineering|MOC AI Engineering]]
