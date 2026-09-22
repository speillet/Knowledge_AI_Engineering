# Reproductibilité & variance — Flashcards
Tags: #flashcards #ai-engineering #mlops #reproductibilite #evals #llm

Une température à 0 garantit-elle des sorties identiques ?
?
**Non.** Les calculs GPU en **virgule flottante** ne sont pas associatifs : (a + b) + c ≠ a + (b + c). Un infime écart sur les logits suffit à changer le token choisi quand deux candidats sont presque à égalité, et toute la suite de la réponse diverge.

---

D'où vient principalement le non-déterminisme d'un serveur d'inférence ?
?
Du **manque d'invariance au batch** : les kernels (matmul, normalisation, attention) changent leur **ordre de réduction** selon la taille du batch. Or, avec le [[62-optimisations-inference|continuous batching]], le batch dépend des **autres requêtes** présentes à cet instant : le résultat dépend de la charge du serveur. Des kernels **batch-invariants** (modes déterministes de SGLang ou vLLM) corrigent cela, au prix de performances.

---

Qu'est-ce qui peut changer la sortie d'un même modèle, à prompt identique ?
?
- Paramètres de sampling et **seed**
- **Version exacte** du modèle, du tokenizer et du chat template
- **Quantization** (FP16, FP8, INT4…)
- **Moteur d'inférence** et sa version, type de **GPU**, degré de **tensor parallelism**
- **Charge du serveur** (taille des batchs)
- Côté application : prompt système, outils, **documents récupérés** par le RAG

---

À quoi sert le paramètre seed ?
?
À **fixer le générateur aléatoire** du sampling pour rejouer le même tirage. vLLM l'accepte par requête ; côté API, c'est au mieux un **« best effort »** (OpenAI l'accompagne d'un `system_fingerprint` qui change quand le backend change). Le seed ne neutralise **ni les écarts numériques ni les changements de version**.

---

Comment rendre un appel LLM rejouable ?
?
Journaliser **tout ce qui le détermine** : identifiant **daté** du modèle, prompt **rendu** (après templating) et sa version, paramètres de sampling, seed, schémas d'outils, **documents injectés**, et la **réponse obtenue**. Les [[91-langfuse-observabilite|traces]] servent de journal pour rejouer et déboguer.

---

Pourquoi ne pas comparer la sortie d'un LLM à une chaîne attendue ?
?
Parce qu'elle **varie** d'un appel à l'autre sans être fausse. On vérifie des **propriétés** (JSON valide, bonne entité extraite, aucune donnée interdite) ou on note contre un **seuil** (métrique, juge). Pour tester le code autour du LLM, on **enregistre puis rejoue** les réponses (record/replay) : tests déterministes et gratuits.

---

Pourquoi un écart de score entre deux prompts peut-il n'être que du bruit ?
?
Un score mesuré sur **n exemples** est incertain. Pour une exactitude p :
```text
erreur standard  SE = √( p (1 − p) / n )    ex. p = 0,8 et n = 100 → SE = 0,04
IC à 95 %        ≈ p ± 1,96 × SE           → 80 % ± 8 points
```
Sur 100 exemples, un écart de 3 points **ne prouve rien**.

---

Comment comparer rigoureusement deux variantes (prompt, modèle) ?
?
- **Même dataset** et analyse **appariée** (différence exemple par exemple) : bien moins de variance qu'en comparant deux moyennes
- **Plusieurs runs** par exemple, pour lisser le bruit du sampling
- Rapporter **moyenne ± intervalle de confiance**, et **agrandir le dataset** quand l'écart recherché est petit

---

Quelle différence entre pass@k et pass^k ?
?
- **pass@k** : probabilité qu'**au moins une** des k tentatives réussisse → le **potentiel** (utile quand on peut vérifier puis relancer, ex. du code avec des tests)
- **pass^k** : probabilité que **les k tentatives** réussissent → la **fiabilité** vécue par l'utilisateur qui repose la même question

Avec 80 % de succès par tentative (tentatives indépendantes) : pass@3 ≈ 99 %, pass^3 ≈ 51 %.

---

Comment estimer pass@k sans biais ?
?
Générer **n ≥ k** échantillons par problème, compter les **c** réussites, puis :
```text
pass@k = 1 − C(n − c, k) / C(n, k)
```
C'est l'estimateur du papier Codex (2021), plus stable que de ne tirer que k essais.

---

Pourquoi un LLM-as-judge ajoute-t-il de la variance ?
?
Le juge est lui-même un LLM **non déterministe** et **biaisé** (ordre de présentation, longueur, style). On le fait tourner à **température basse**, on **permute l'ordre** des réponses comparées, on **moyenne plusieurs passes**, et on le calibre sur des annotations humaines.

---

Comment rendre un fine-tuning reproductible ?
?
- Fixer **toutes les seeds** (Python, NumPy, PyTorch/CUDA) et l'**ordre des données**
- Forcer les algorithmes déterministes : `torch.use_deterministic_algorithms(True)`, `CUBLAS_WORKSPACE_CONFIG=:4096:8`, `cudnn.benchmark = False`
- **Versionner** données, code, config, image et **type de GPU**

Changer de matériel ou de nombre de GPU modifie quand même les résultats au bit près : on vise des **métriques équivalentes**, pas des poids identiques.

---

Faut-il viser le déterminisme partout ?
?
**Non.** Il sert là où l'on compare ou enquête : **tests, audits, débogage, evals comparatives**. En production, on **conçoit pour la variabilité** : validation des sorties, [[63-guided-generation|sorties contraintes]], retries et evals sur plusieurs runs. Un système fiable ne dépend pas d'un tirage chanceux.

---

## Connexions
- [[65-probabilites-sampling|Probabilités & sampling]] — la source de la variabilité
- [[111-mlops-llmops-fondamentaux|MLOps fondamentaux]] — versioning et lineage
- [[112-cicd-modeles|CI/CD des modèles]] — tests et eval gates
- [[113-monitoring-drift-feedback|Monitoring & drift]] — les changements de version côté provider
- [[92-chainforge-evals-prompts|Evals]] — comparer des prompts sur un golden dataset
- [[91-langfuse-observabilite|Langfuse]] — les traces pour rejouer un appel
- [[62-optimisations-inference|Optimisations d'inférence]] — continuous batching et quantization
- [[51-fine-tuning-adaptation|Fine-tuning]] — des entraînements reproductibles
- [[00-moc-ai-engineering|MOC AI Engineering]]
