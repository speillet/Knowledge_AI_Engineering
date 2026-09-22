# Langfuse & observabilité LLM — Flashcards
Tags: #flashcards #ai-engineering #observability #langfuse #llm

Qu'est-ce que Langfuse ?
?
Une plateforme **open source d'observabilité LLM** (self-hostable) : traces, coûts, prompt management et évaluation.

---

Pourquoi l'observabilité LLM diffère-t-elle de l'APM classique ?
?
Parce que les sorties sont **non déterministes** et le coût est **par token** : il faut tracer prompts, réponses, tokens et qualité, pas seulement latence/erreurs.

---

Qu'est-ce qu'une trace dans Langfuse ?
?
L'**enregistrement complet d'une requête** : arbre de **spans** (étapes) et **generations** (appels LLM), avec entrées/sorties, latence, tokens et coût.

---

Que permet le suivi des sessions et des users ?
?
De **regrouper les traces par conversation ou par utilisateur** pour analyser les parcours et retrouver les échecs.

---

Qu'est-ce que le prompt management de Langfuse ?
?
Des **prompts versionnés et déployés hors du code** : rollback, A/B et itération sans redéploiement applicatif.

---

Comment Langfuse évalue-t-il la qualité des réponses ?
?
Via des **scores** : feedback utilisateur, règles automatiques ou **LLM-as-judge** attachés aux traces.

---

À quoi servent les datasets dans Langfuse ?
?
À constituer des **jeux de test** depuis les traces réelles pour rejouer et comparer prompts/modèles.

---

Comment instrumenter une app avec Langfuse ?
?
Par **SDK (decorators), intégrations natives** (LangChain, [[81-litellm-api-layer|LiteLLM]] callbacks) ou OpenTelemetry.

---

## Connexions
- [[92-chainforge-evals-prompts|ChainForge & evals]] — l'évaluation hors production
- [[64-metriques-slo-inference|Métriques & SLO]] — du système à l'application
- [[81-litellm-api-layer|LiteLLM]] — source naturelle des traces
- [[82-routing-llm|Routing LLM]] — décider grâce aux données observées
- [[38-plateformes-agents|Plateformes d'agents]] — brique observabilité
- [[113-monitoring-drift-feedback|Monitoring & drift]] — la boucle de feedback prod
- [[122-finops-llm|FinOps LLM]] — le cost tracking
- [[00-moc-ai-engineering|MOC AI Engineering]]
