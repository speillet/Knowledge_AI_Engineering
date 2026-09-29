# Données synthétiques & distillation — Flashcards
Tags: #flashcards #ai-engineering #fine-tuning #synthetic-data #distillation #llm
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.

Qu'est-ce que les données synthétiques en AI Engineering ?
?
Des données **générées par un LLM** (questions, réponses, conversations, cas de test, préférences) plutôt que collectées ou écrites par des humains. Usages : **fine-tuning**, **distillation**, **jeux d'eval** ([[94-evals-methodologie|golden dataset]]), **tests adversariaux**, entraînement de **modèles d'embedding**.

---

Comment générer des données synthétiques variées ?
?
Éviter « génère 100 exemples » (sorties répétitives). À la place :
- définir des **dimensions** (persona, intention, difficulté, longueur, langue) et **croiser** leurs valeurs ;
- partir de **graines réelles** (documents, requêtes de prod) ;
- générer en **deux temps** : d'abord les entrées, ensuite les réponses ;
- faire varier les modèles et la température.

---

Pourquoi le filtrage est-il l'étape la plus importante ?
?
Un LLM génère avec aplomb des exemples **faux, triviaux ou dupliqués**. On filtre par : **validation automatique** (exécution du code, schéma, réponse vérifiable), **juge** de qualité, **déduplication** (exacte et sémantique), et **relecture humaine** d'un échantillon. Mieux vaut **1 000 bons exemples que 50 000 médiocres**.

---

Qu'est-ce que le model collapse ?
?
La **dégradation** d'un modèle entraîné de façon répétée sur les **sorties de modèles** : la diversité s'effondre, les **queues de distribution** (cas rares) disparaissent et les erreurs s'amplifient. Parade : **mélanger avec des données réelles**, conserver les données humaines d'origine, filtrer fortement.

---

Qu'est-ce que la distillation ?
?
Entraîner un **modèle élève** (petit) à reproduire le comportement d'un **modèle enseignant** (grand). Objectif : garder l'essentiel de la qualité **sur un périmètre ciblé** avec un modèle **bien moins cher et plus rapide** à servir ([[121-couts-inference|coûts]]).

---

À ne pas confondre : distillation « sur les sorties » et « sur les logits » ?
?
- **Sur les sorties** (sequence-level) : l'élève est fine-tuné (SFT) sur les **textes générés** par l'enseignant — possible même avec un modèle fermé via API.
- **Sur les logits** (soft labels) : l'élève apprend à reproduire la **distribution de probabilités** complète de l'enseignant (loss KL) — plus riche en information, mais exige l'accès aux logits et un **tokenizer compatible**.

---

Qu'est-ce que la distillation du raisonnement ?
?
Fine-tuner un petit modèle sur les **traces de raisonnement** d'un modèle de raisonnement (problème → réflexion → réponse vérifiée). Des modèles de quelques milliards de paramètres gagnent ainsi fortement en maths et en code ; c'est souvent **plus efficace que de faire du RL** directement sur un petit modèle ([[138-modeles-raisonnement|raisonnement]]).

---

Quelles contraintes juridiques pèsent sur la distillation ?
?
Les **conditions d'utilisation** de nombreux fournisseurs interdisent d'utiliser leurs sorties pour **entraîner un modèle concurrent**. Il faut vérifier la **licence** de l'enseignant (y compris des modèles open weights, dont certaines licences imposent des conditions sur les modèles dérivés) et tracer la **provenance** des données ([[155-ai-act|AI Act]], [[105-devsecops-ia-agentique|AI-BOM]]).

---

Comment mener un projet de distillation en pratique ?
?
1. **Eval** de référence sur la tâche avec l'enseignant (plafond) et l'élève de base (plancher).
2. Collecter des **entrées réelles** (logs de production) et les faire traiter par l'enseignant.
3. **Filtrer** (juge, validation, humains).
4. **Fine-tuner** l'élève (souvent [[51-fine-tuning-adaptation|LoRA]]).
5. Comparer sur l'eval, puis déployer derrière un [[82-routing-llm|routeur]] avec l'enseignant en **fallback**.

---

Comment générer des données synthétiques pour les evals sans biaiser le résultat ?
?
- Utiliser un **modèle différent** de celui qu'on évalue.
- Faire **relire** les cas par un expert, et garder une part de **données réelles**.
- Surveiller le **recouvrement lexical** (questions trop proches des documents, trop faciles).
- Ne jamais **ré-entraîner** sur le jeu d'eval lui-même (contamination).

---

## Mises en situation

Mise en situation : ta classification de documents coûte 8 000 € par mois avec un grand modèle. Comment mènes-tu un projet de distillation ?
?
1. **Fixer les bornes** : eval de référence avec l'enseignant (plafond) et avec le petit modèle non entraîné (plancher)
2. **Collecter des entrées réelles** issues des logs, pas des exemples inventés, et les faire traiter par l'enseignant
3. **Filtrer** : validation automatique, juge, déduplication, relecture d'un échantillon. Mille bons exemples valent mieux que cinquante mille médiocres
4. **Entraîner l'élève** en LoRA, puis comparer sur la même eval
5. **Déployer prudemment** : routeur avec l'enseignant en repli sur les cas à faible confiance ([[82-routing-llm|routing]])

**Piège** : vérifier les conditions d'utilisation de l'enseignant trop tard, alors que beaucoup interdisent l'entraînement d'un modèle concurrent.

---

Mise en situation : pour gagner du temps, un collègue propose de générer 50 000 exemples synthétiques avec le même modèle que celui qu'on évalue. Quels risques signales-tu ?
?
1. **Contamination** : évaluer un modèle sur des données qu'il a produites gonfle artificiellement les scores
2. **Model collapse** : entraîner en boucle sur des sorties de modèles appauvrit la diversité et efface les cas rares
3. **Manque de variété** : « génère 50 000 exemples » produit des sorties répétitives. Il faut croiser des dimensions et partir de graines réelles
4. **Bonnes pratiques** : générer avec un **autre modèle**, faire relire par un expert, garder une part de données réelles
5. **Surveiller** : recouvrement lexical, doublons sémantiques, difficulté réelle des cas

**Piège** : juger la qualité d'un jeu synthétique à son volume.

---

## Connexions
- [[51-fine-tuning-adaptation|Fine-tuning & adaptation]] — SFT et LoRA
- [[52-post-training-alignement|Post-training & alignement]] — données de préférences
- [[151-donnees-curation-annotation|Curation & annotation]] — qualité des données
- [[94-evals-methodologie|Méthodologie d'évaluation]] — jeux synthétiques
- [[82-routing-llm|Routing LLM]] — servir l'élève et l'enseignant ensemble
- [[135-pretraining-scaling-laws|Pré-entraînement]] — le mur des données
- [[00-moc-ai-engineering|MOC AI Engineering]]
