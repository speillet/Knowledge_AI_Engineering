# MLOps & LLMOps — Fondamentaux — Flashcards
Tags: #flashcards #ai-engineering #mlops #llmops #llm
Vérifié le : 29 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.

Qu'est-ce que le MLOps ?
?
L'application des pratiques **DevOps au cycle de vie ML** : données → entraînement → évaluation → déploiement → monitoring, avec **automatisation et reproductibilité**.

---

À ne pas confondre : DevOps et MLOps ?
?
DevOps versionne du **code** ; MLOps versionne **code + données + modèle + configuration** — le comportement d'un système ML vient des données, pas seulement du code.

---

Qu'est-ce que le LLMOps par rapport au MLOps classique ?
?
On entraîne rarement from scratch : le cycle est centré sur **prompts, RAG, fine-tuning, evals et coûts** ; les artefacts sont des prompts versionnés, des adapters et des index.

---

Quels artefacts de code et de configuration faut-il versionner dans un système LLM ?
?
- Le **code** applicatif et les pipelines
- Les **prompts**, y compris les descriptions d'outils
- La **config de génération** : modèle et version exacte, température, `max_tokens`, schéma de sortie

Changer l'un d'eux change le comportement : chaque réponse en production doit pouvoir être reliée à la **combinaison exacte** qui l'a produite ([[13-prompts-production|prompts en production]]).

---

Quels artefacts de modèle et de données faut-il versionner dans un système LLM ?
?
- Les **poids ou adapters** fine-tunés ([[51-fine-tuning-adaptation|LoRA]]), avec les données et la recette qui les ont produits
- Les **golden datasets** d'éval, pour que deux scores soient comparables
- Les **index RAG** : documents sources, chunking et modèle d'embedding ([[153-data-flywheel-versioning|versioning]])

Un score d'eval sans la version du jeu de test ne veut rien dire.

---

Qu'est-ce qu'un model registry ?
?
Un service qui **stocke et versionne les modèles** avec métadonnées, stages (staging/prod) et lineage — ex. **MLflow, W&B, Hugging Face Hub**. Distinct du [[10-images-modeles-poids|container registry]].

---

Qu'est-ce que le lineage d'un modèle ?
?
La **traçabilité complète** : quelles données, quel code et quels hyperparamètres ont produit cette version du modèle.
```yaml
# manifeste d'un artefact déployé : les 4 versions à tracer ensemble
image:        registry.interne/assistant@sha256:9f2c…
modele:       claude-sonnet-4-5-20250929     # identifiant daté, pas un alias
prompts:      prompts/support@v14
index_rag:    support-fr-2026-09-20 (embedding: e5-large@v2)
```
Sans ce manifeste, une régression en production devient une enquête sans pièces à conviction ([[114-reproductibilite-variance|reproductibilité]]).

---

À ne pas confondre : versionner et épingler ?
?
- **Versionner** : conserver l'**historique** des artefacts (code, prompts, poids, datasets) pour pouvoir revenir en arrière et comparer
- **Épingler** : déclarer dans le déploiement une **version exacte** (digest, identifiant daté) au lieu d'un alias mouvant comme `latest`

On peut très bien versionner ses prompts **et** appeler un modèle via un alias qui change sous vos pieds : le versionnage seul ne protège pas ([[142-fiabilite-resilience-llm|épingler le modèle]]).

---

Pourquoi la reproductibilité est-elle difficile avec les LLM ?
?
**Non-déterminisme** (sampling), **versions de modèles API qui changent**, dépendances GPU — d'où : fixer les seeds/température, **épingler les versions** et tracer les configs.

---

Comment gérer dev/staging/prod pour une app LLM ?
?
- **Mêmes pipelines** de déploiement partout, seules les valeurs changent
- Modèles, prompts et datasets **épinglés** par environnement
- **Evals de non-régression** obligatoires avant chaque promotion ([[112-cicd-modeles|eval gate]])
- **Staging alimenté par des cas réels**, anonymisés, plutôt que par des exemples inventés

Piège fréquent : un alias de modèle (`latest`) en production, qui change sans que personne n'ait rien déployé.

---

Quel est le rôle du Lead sur le volet MLOps ?
?
Imposer les **standards** plutôt que tout faire lui-même :
- **Registry unique** et conventions de versioning
- **Gates d'éval** obligatoires ([[112-cicd-modeles|CI/CD]])
- **Ownership** : chaque modèle, prompt et index en production a un responsable nommé
- **Runbooks** : que faire si la qualité chute ou si un fournisseur tombe

Le but : qu'un changement risqué ne puisse pas partir en production **par accident**.

---

## Mises en situation

Mise en situation : une application LLM en production donne des réponses différentes d'il y a deux mois, et personne ne sait ce qui a changé. Que manque-t-il, et comment le corriges-tu ?
?
1. **Constater** : sans versionnage complet, on ne peut ni expliquer ni revenir en arrière
2. **Versionner les quatre briques** : code, prompts et configuration de génération, modèle ou adapter, index RAG
3. **Épingler** la version exacte du modèle, y compris côté API, qui évolue sans commit chez toi ([[113-monitoring-drift-feedback|mises à jour du provider]])
4. **Tracer** la version utilisée dans chaque requête ([[91-langfuse-observabilite|traces]])
5. **Relier** version et qualité par des evals rejouées à chaque changement ([[112-cicd-modeles|CI/CD]])

**Piège** : versionner le code seul et considérer le prompt comme de la configuration secondaire.

---

Mise en situation : trois équipes déploient chacune leurs modèles, avec leurs conventions, et personne ne sait qui est responsable de quoi en production. Que mets-tu en place comme lead ?
?
1. **Un registre unique** pour les modèles et adapters, avec métadonnées, étapes et lineage
2. **Des conventions de versionnage** communes, appliquées par la CI plutôt que par la discipline
3. **Un propriétaire nommé** par modèle en production, responsable de sa qualité et de son retrait
4. **Des environnements alignés** : mêmes pipelines en dev, préproduction et production, données près du réel
5. **Des gates d'évaluation** obligatoires avant chaque promotion

**Piège** : imposer un outil avant d'avoir posé les responsabilités et les conventions.

---

## Connexions
- [[112-cicd-modeles|CI/CD des modèles]] — le pipeline qui applique ces standards
- [[113-monitoring-drift-feedback|Monitoring & drift]] — la boucle post-déploiement
- [[10-images-modeles-poids|Images & poids]] — model registry vs container registry
- [[51-fine-tuning-adaptation|Fine-tuning]] — les adapters comme artefacts
- [[91-langfuse-observabilite|Langfuse]] — prompts versionnés
- [[114-reproductibilite-variance|Reproductibilité & variance]] — la reproductibilité en détail
- [[115-plateformes-agents-gouvernance|Plateformes d'agents — Architecture & gouvernance]] — registre et cycle de vie des agents
- [[105-devsecops-ia-agentique|DevSecOps pour l'IA agentique]] — AI-BOM et chaîne d'approvisionnement des modèles
- [[153-data-flywheel-versioning|Data flywheel & versioning]] — versionner et boucler sur les données
- [[147-leadership-technique-ia|Leadership technique]] — rôle du senior
- [[00-moc-ai-engineering|MOC AI Engineering]]
