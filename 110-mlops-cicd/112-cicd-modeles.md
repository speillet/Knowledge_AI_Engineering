# CI/CD des modèles — Flashcards
Tags: #flashcards #ai-engineering #mlops #cicd #llm

Qu'apporte le CI/CD d'une app LLM en plus du CI/CD classique ?
?
Des **eval gates** : la qualité du modèle/prompt est testée automatiquement **comme du code**, en plus des tests logiciels habituels.

---

Qu'est-ce qu'un eval gate ?
?
Un **seuil d'évaluation bloquant** (golden dataset, LLM-as-judge) : si les scores régressent, le merge ou le déploiement est **refusé** ([[92-chainforge-evals-prompts|evals]]).

---

Que contient l'artefact déployé d'une app LLM ?
?
L'**image conteneur** + la **référence versionnée du modèle/adapter** + les **prompts/config** — trois versions distinctes à tracer ensemble.

---

Quelle différence entre blue/green et canary pour un modèle ?
?
- **Blue/green** : bascule totale, rollback instantané
- **Canary** : % de trafic progressif, comparaison des **[[64-metriques-slo-inference|métriques/SLO]]** et scores avant promotion

---

Qu'est-ce que le shadow deployment ?
?
Le nouveau modèle reçoit une **copie du trafic réel sans répondre aux utilisateurs** : comparaison en conditions réelles, **sans risque**.

---

Comment fonctionne le rollback d'un modèle ?
?
Revenir à la **version précédente du registry/adapter** : exige un versioning strict et des schémas de sortie compatibles.

---

Qu'est-ce que le GitOps appliqué aux modèles ?
?
L'**état désiré** (version du modèle, config, prompts) est déclaré **dans Git** ; un opérateur (ArgoCD) réconcilie le cluster en continu.

---

Quels types de tests pour une app LLM en CI ?
?
- **Unitaires** (parsing, outils)
- **Intégration** (LLM mocké)
- **Evals** (qualité sur golden dataset)
- **Contrats** : validité des schémas de [[63-guided-generation|sorties structurées]]

---

Pourquoi les prompts passent-ils par la CI ?
?
Un prompt modifié **change le comportement en production** : chaque modification déclenche les **tests de régression** ([[92-chainforge-evals-prompts|golden datasets]]).

---

À quoi ressemble un pipeline complet ?
?
```text
PR → tests + evals → build image → push registry
→ deploy canary → métriques/SLO OK → promotion
```

---

## Connexions
- [[111-mlops-llmops-fondamentaux|MLOps fondamentaux]] — versioning & registry
- [[92-chainforge-evals-prompts|Evals]] — le contenu des gates
- [[64-metriques-slo-inference|Métriques & SLO]] — le juge du canary
- [[83-gateway-ingress|Ingress & gateway]] — le découpage du trafic
- [[12-kubernetes-gpu-inference|Kubernetes GPU]] — la cible de déploiement
- [[114-reproductibilite-variance|Reproductibilité & variance]] — tester des sorties variables
- [[93-monitoring-inference|Monitoring de l'inférence]] — les contrôles avant d'envoyer du trafic
- [[115-plateformes-agents-gouvernance|Plateformes d'agents — Architecture & gouvernance]] — evals et boucle d'optimisation des agents
- [[00-moc-ai-engineering|MOC AI Engineering]]
