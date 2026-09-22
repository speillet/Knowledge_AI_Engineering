# Coûts d'inférence — Flashcards
Tags: #flashcards #ai-engineering #finops #couts #inference #llm

Comment se structure le coût d'un appel LLM API ?
?
**Prix par million de tokens**, différencié **input / output** (l'output est plus cher), avec surcoûts éventuels (raisonnement, contexte long).

---

Pourquoi les tokens d'output coûtent-ils plus cher que l'input ?
?
Parce que le **decode est séquentiel** (un passage par token généré) alors que le **prefill est parallèle** ([[62-optimisations-inference|optimisations]]).

---

Quel effet du prompt caching sur la facture ?
?
Les **tokens de préfixe déjà en cache sont facturés à prix réduit** : gros gains sur les system prompts et définitions d'outils répétés ([[35-context-engineering|prompt caching]]).

---

Comment se calcule le coût du self-hosting ?
?
**Coût par token = coût GPU (par heure ou amorti) ÷ débit (tokens/s)** : maximiser l'utilisation et le [[64-metriques-slo-inference|goodput]] fait mécaniquement baisser le coût unitaire.

---

API ou self-host : où est le break-even ?
?
- **Self-host** rentable à **fort volume constant** et forte utilisation GPU
- **API** gagne à faible volume ou charge irrégulière (pas de GPU idle, scale-to-zero implicite)

---

Qu'est-ce qu'une batch API ?
?
Un traitement **différé** (fenêtre de plusieurs heures) à **~-50 %** : idéal pour le non-interactif (evals massives, ingestion, enrichissement).

---

Quels leviers techniques réduisent le coût ?
?
- [[82-routing-llm|Routing]] vers un modèle moins cher
- [[62-optimisations-inference|Quantization]]
- **Caching** de réponses ([[81-litellm-api-layer|gateway]])
- Prompts plus courts, `max_tokens` limité

---

Que coûte réellement le contexte long ?
?
Chaque token de contexte coûte **trois fois** : en argent (facturation), en latence (prefill) et en VRAM ([[61-kv-cache-attention|KV cache]]) — trier son contexte, c'est économiser.

---

Qu'est-ce que les unit economics d'une feature LLM ?
?
Le **coût par requête / utilisateur / feature rapporté à la valeur produite** — la métrique qui décide si une feature IA est viable.

---

Pourquoi un GPU inutilisé coûte-t-il autant qu'un GPU actif ?
?
Un GPU **alloué facture pareil, utilisé ou non** : consolidation, MIG/time-slicing, autoscaling et scale-to-zero ([[12-kubernetes-gpu-inference|K8s GPU]]).

---

## Connexions
- [[122-finops-llm|FinOps LLM]] — la gouvernance de ces coûts
- [[64-metriques-slo-inference|Métriques & SLO]] — goodput ↔ coût par token
- [[62-optimisations-inference|Optimisations d'inférence]] — les leviers techniques
- [[35-context-engineering|Context engineering]] — le coût du contexte
- [[82-routing-llm|Routing LLM]] — payer le juste modèle
- [[00-moc-ai-engineering|MOC AI Engineering]]
