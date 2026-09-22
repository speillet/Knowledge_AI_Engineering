# MLOps & LLMOps — Fondamentaux — Flashcards
Tags: #flashcards #ai-engineering #mlops #llmops #llm

Qu'est-ce que le MLOps ?
?
L'application des pratiques **DevOps au cycle de vie ML** : données → entraînement → évaluation → déploiement → monitoring, avec **automatisation et reproductibilité**.

---

Quelle différence fondamentale entre DevOps et MLOps ?
?
DevOps versionne du **code** ; MLOps versionne **code + données + modèle + configuration** — le comportement d'un système ML vient des données, pas seulement du code.

---

Qu'est-ce que le LLMOps par rapport au MLOps classique ?
?
On entraîne rarement from scratch : le cycle est centré sur **prompts, RAG, fine-tuning, evals et coûts** ; les artefacts sont des prompts versionnés, des adapters et des index.

---

Que faut-il versionner dans un système LLM ?
?
- Le **code**
- Les **prompts**
- Les **poids/adapters** ([[51-fine-tuning-adaptation|LoRA]])
- Les **golden datasets** d'éval
- La **config de génération** (température, max_tokens)
- Les **index RAG**

---

Qu'est-ce qu'un model registry ?
?
Un service qui **stocke et versionne les modèles** avec métadonnées, stages (staging/prod) et lineage — ex. **MLflow, W&B, Hugging Face Hub**. Distinct du [[10-images-modeles-poids|container registry]].

---

Qu'est-ce que le lineage d'un modèle ?
?
La **traçabilité complète** : quelles données, quel code et quels hyperparamètres ont produit cette version du modèle.

---

Pourquoi la reproductibilité est-elle difficile avec les LLM ?
?
**Non-déterminisme** (sampling), **versions de modèles API qui changent**, dépendances GPU — d'où : fixer les seeds/température, **épingler les versions** et tracer les configs.

---

Comment gérer dev/staging/prod pour une app LLM ?
?
Mêmes pipelines partout, modèles et datasets **épinglés**, et **evals de non-régression** obligatoires avant chaque promotion d'environnement.

---

Quel est le rôle du Lead sur le volet MLOps ?
?
Imposer les **standards** : registry unique, conventions de versioning, [[112-cicd-modeles|gates d'éval]] et **ownership** clair de chaque modèle en production.

---

## Connexions
- [[112-cicd-modeles|CI/CD des modèles]] — le pipeline qui applique ces standards
- [[113-monitoring-drift-feedback|Monitoring & drift]] — la boucle post-déploiement
- [[10-images-modeles-poids|Images & poids]] — model registry vs container registry
- [[51-fine-tuning-adaptation|Fine-tuning]] — les adapters comme artefacts
- [[91-langfuse-observabilite|Langfuse]] — prompts versionnés
- [[114-reproductibilite-variance|Reproductibilité & variance]] — la reproductibilité en détail
- [[00-moc-ai-engineering|MOC AI Engineering]]
