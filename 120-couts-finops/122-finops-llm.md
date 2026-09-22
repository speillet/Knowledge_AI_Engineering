# FinOps LLM — Flashcards
Tags: #flashcards #ai-engineering #finops #gouvernance #llm

Qu'est-ce que le FinOps appliqué aux LLM ?
?
La discipline de **gestion des dépenses IA** (tokens + GPU) en quatre temps : **visibilité → attribution → optimisation → gouvernance**.

---

Quelle est la première étape FinOps d'une plateforme LLM ?
?
La **visibilité** : tracer le coût **par requête, équipe et feature** via la [[81-litellm-api-layer|gateway]] et les [[91-langfuse-observabilite|traces]] — on ne pilote pas ce qu'on ne voit pas.

---

Comment attribuer les coûts aux équipes ?
?
**Virtual keys et tags** par équipe/produit → **showback** (information) puis **chargeback** (refacturation interne).

---

Comment encadrer les dépenses ?
?
**Budgets et quotas par clé/équipe** dans la gateway, **alertes** avant dépassement, **kill switch** en cas d'emballement.

---

Quel est souvent le premier levier d'économie ?
?
Le **[[82-routing-llm|routing]]** : envoyer chaque requête au **modèle le moins cher qui suffit** (cascades) — souvent plusieurs dizaines de % de gain.

---

Quels caches actionner côté FinOps ?
?
**Cache de réponses** (requêtes identiques), **prompt caching** (préfixes), cache d'**embeddings** RAG.

---

Quelles pratiques FinOps côté GPU ?
?
**Droit-dimensionnement** (MIG), objectif d'utilisation, **spot/préemptible** pour le non-critique, **scale-to-zero**, réservations pour la charge de base ([[12-kubernetes-gpu-inference|K8s GPU]]).

---

Comment arbitrer coût, qualité et latence ?
?
C'est un **triangle** : les [[92-chainforge-evals-prompts|evals]] et les [[64-metriques-slo-inference|métriques/SLO]] rendent l'arbitrage **objectif** au lieu d'intuitif.

---

Quel est le rôle du Lead sur le FinOps ?
?
Suivre les **unit economics par produit**, imposer les **standards d'attribution**, tenir des **revues de coûts** régulières — le coût est une métrique de premier ordre, pas une surprise de fin de mois.

---

## Connexions
- [[121-couts-inference|Coûts d'inférence]] — la mécanique des coûts
- [[81-litellm-api-layer|LiteLLM]] — budgets, quotas, attribution
- [[91-langfuse-observabilite|Langfuse]] — cost tracking par trace
- [[82-routing-llm|Routing LLM]] — le levier n°1
- [[38-plateformes-agents|Plateformes d'agents]] — la gouvernance à l'échelle
- [[123-caching-agressif|Caching agressif]] — les caches en pratique
- [[93-monitoring-inference|Monitoring de l'inférence]] — les métriques d'usage par équipe
- [[115-plateformes-agents-gouvernance|Plateformes d'agents — Architecture & gouvernance]] — le coût d'une flotte d'agents
- [[00-moc-ai-engineering|MOC AI Engineering]]
