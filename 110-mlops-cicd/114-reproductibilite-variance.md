# Reproductibilité & variance — Flashcards
Tags: #flashcards #ai-engineering #mlops #reproductibilite #evals #llm
<!-- summary: non-déterminisme à température 0, invariance au batch, seed, appel rejouable, tests sur des sorties variables, erreur standard et intervalles de confiance, comparaison appariée, pass@k et pass^k, variance du LLM-as-judge, fine-tuning reproductible. -->


Une température à 0 garantit-elle des sorties identiques ? <!--anki:6354476e2a6372354e28-->
?
**Non.** Les calculs GPU en **virgule flottante** ne sont pas associatifs : (a + b) + c ≠ a + (b + c). Un infime écart sur les logits suffit à changer le token choisi quand deux candidats sont presque à égalité, et toute la suite de la réponse diverge.

---

D'où vient principalement le non-déterminisme d'un serveur d'inférence ? <!--anki:42575a626e2f243e7b46-->
?
Du **manque d'invariance au batch** : les kernels (matmul, normalisation, attention) changent leur **ordre de réduction** selon la taille du batch. Or, avec le [[62-optimisations-inference|continuous batching]], le batch dépend des **autres requêtes** présentes à cet instant : le résultat dépend de la charge du serveur. Des kernels **batch-invariants** (modes déterministes de SGLang ou vLLM) corrigent cela, au prix de performances.

---

Quels réglages du modèle peuvent changer sa sortie, à prompt identique ? <!--anki:7445534225614d64687a-->
?
- Paramètres de sampling et **seed**
- **Version exacte** du modèle, du tokenizer et du chat template
- **Quantization** (FP16, FP8, INT4…)

Tracer ces valeurs avec la requête et utiliser le même environnement pour comparer deux variantes. FP16 est ici une précision de référence, tandis que FP8 ou INT4 réduisent davantage la représentation numérique. Une seed identique n'assure une répétabilité que dans les conditions supportées par le moteur ; elle ne fige pas toutes les sources de variation.

---

Quels facteurs d'infrastructure et d'application peuvent changer la sortie d'un même modèle, à prompt identique ? <!--anki:4b5a6e72257228217c42-->
?
- **Moteur d'inférence** et sa version, type de **GPU**, degré de **tensor parallelism**
- **Charge du serveur** (taille des batchs)
- Côté application : prompt système, outils, **documents récupérés** par le RAG

Distinguer prompt utilisateur identique et **entrée complète du modèle identique** : un document récupéré différent change le problème posé. Enregistrer le contexte final permet de séparer cette variabilité applicative des effets numériques. Pour un diagnostic, figer d'abord les sources et les outils, puis comparer les configurations d'inférence.

---

À quoi sert le paramètre seed ? <!--anki:4b30415a706a76365a43-->
?
À **fixer le générateur aléatoire** du sampling pour rejouer le même tirage. vLLM l'accepte par requête ; côté API, c'est au mieux un **« best effort »** (OpenAI l'accompagne d'un `system_fingerprint` qui change quand le backend change). Le seed ne neutralise **ni les écarts numériques ni les changements de version**.

---

Comment rendre un appel LLM rejouable ? <!--anki:693e60316b3025562574-->
?
Journaliser **tout ce qui le détermine** : identifiant **daté** du modèle, prompt **rendu** (après templating) et sa version, paramètres de sampling, seed, schémas d'outils, **documents injectés**, et la **réponse obtenue**. Les [[91-langfuse-observabilite|traces]] servent de journal pour rejouer et déboguer.

---

Quand une comparaison exacte de la sortie LLM est-elle adaptée, et quand faut-il tester des propriétés ? <!--anki:656d592d3b347921397b-->
?
Pour une **réponse libre**, plusieurs formulations peuvent satisfaire la tâche : un exact match pénaliserait des variantes correctes. Vérifier les faits, champs, contraintes et références utiles.

Pour une classe, un identifiant ou une valeur canonique, l'égalité exacte peut au contraire être le bon test, après une normalisation explicitement admise. Tester séparément le code d'orchestration avec réponses simulées ou enregistrées, et le modèle sur des entrées représentatives. Un replay rend certains tests reproductibles ; il ne mesure pas à nouveau le comportement du modèle réel.

---

Pourquoi un écart de score entre deux prompts peut-il n'être que du bruit ? <!--anki:422b296b24785b465177-->
?
Un score calculé sur un échantillon a une **incertitude**. Pour une proportion de succès `p` sur `n` observations indépendantes :
```text
SE ≈ √(p × (1 − p) / n)
p = 0,8 ; n = 100 → SE ≈ 0,04
IC normal à 95 % ≈ 80 % ± 7,8 points
```
Cet intervalle concerne **un score**, pas directement l'écart entre deux prompts. Sur les mêmes exemples, utiliser une comparaison appariée : l'incertitude dépend des désaccords entre variantes. Répéter les générations si elles varient ; ne pas conclure à un gain robuste à partir de quelques points sans analyse.

---

Comment comparer rigoureusement deux variantes (prompt, modèle) ? <!--anki:74766263287b66405325-->
?
- **Même dataset** et analyse **appariée** (différence exemple par exemple) : bien moins de variance qu'en comparant deux moyennes
- **Plusieurs runs** par exemple, pour lisser le bruit du sampling
- Rapporter **moyenne ± intervalle de confiance**, et **agrandir le dataset** quand l'écart recherché est petit

---

À ne pas confondre : pass@k et pass^k ? <!--anki:4c352d733b676a657961-->
?
**pass@k** signifie au moins un succès parmi k essais ; **pass^k** signifie k succès. Pour une tâche de probabilité de succès constante p et des essais indépendants :
```text
pass@k = 1 − (1 − p)^k ; pass^k = p^k
p = 0,8 ; k = 3 → 99,2 % et 51,2 %
```
Le premier n'assure pas qu'on sait identifier la bonne réponse ; le second décrit la répétabilité selon ce protocole. Sur des tâches hétérogènes, calculer les résultats par tâche avant de moyenner. Publier aussi succès initial, coût et types d'échecs selon le service.

---

Comment estimer pass@k sans biais ? <!--anki:4467264a4f62364f6a33-->
?
Générer **n ≥ k** échantillons par problème, compter les **c** réussites, puis :
```text
pass@k = 1 − C(n − c, k) / C(n, k)
```
C'est l'estimateur du papier Codex (2021), plus stable que de ne tirer que k essais.

`C(a, b)` est le nombre de combinaisons ; si `n − c < k`, le terme d'échec vaut zéro. Calculer par problème puis moyenner. L'interprétation suppose des tirages selon un protocole comparable et un vérificateur fiable. Pass@k mesure la présence d'au moins une réussite, pas la capacité à identifier cette réussite sans oracle.

---

Pourquoi un LLM-as-judge ajoute-t-il de la variance ? <!--anki:6d765b41246831436431-->
?
Le juge est lui-même un LLM **non déterministe** et **biaisé** (ordre de présentation, longueur, style). On le fait tourner à **température basse**, on **permute l'ordre** des réponses comparées, on **moyenne plusieurs passes**, et on le calibre sur des annotations humaines.

---

Comment rendre un fine-tuning reproductible ? <!--anki:74213c39574676285476-->
?
- Fixer **toutes les seeds** (Python, NumPy, PyTorch/CUDA) et l'**ordre des données**
- Forcer les algorithmes déterministes : `torch.use_deterministic_algorithms(True)`, `CUBLAS_WORKSPACE_CONFIG=:4096:8`, `cudnn.benchmark = False`
- **Versionner** données, code, config, image et **type de GPU**

Changer de matériel ou de nombre de GPU modifie quand même les résultats au bit près : on vise des **métriques équivalentes**, pas des poids identiques.

---

Faut-il viser le déterminisme partout ? <!--anki:4e404d572d6036633c3c-->
?
**Non.** Il sert là où l'on compare ou enquête : **tests, audits, débogage, evals comparatives**. En production, on **conçoit pour la variabilité** : validation des sorties, [[63-guided-generation|sorties contraintes]], retries et evals sur plusieurs runs. Un système fiable ne dépend pas d'un tirage chanceux.

---

## Mises en situation

Mise en situation : un client exige par contrat que « le même document donne toujours la même extraction ». Que t'engages-tu à faire, et sur quoi refuses-tu de t'engager ? <!--anki:417a783d2b7d663c296b-->
?
1. **Expliquer honnêtement** : même à température 0, les calculs GPU ne garantissent pas une sortie identique au bit près
2. **Définir des critères testables** : schéma, exactitude des champs et gestion des erreurs ; ne pas promettre des valeurs identiques à chaque régénération
3. **Rendre l'appel rejouable** : journaliser modèle daté, prompt rendu, paramètres, documents et réponse
4. **Réduire la variance** : température basse, sortie contrainte, éventuellement un mode déterministe du moteur, au prix de performances
5. **Cacher les résultats** : pour un même document déjà traité, renvoyer la sortie enregistrée plutôt que régénérer

**Piège** : promettre le déterminisme parce que `temperature=0` figure dans la configuration.

---

Mise en situation : ton équipe teste un agent de correction de bugs. Il réussit 4 fois sur 5 en démonstration, et le produit veut annoncer « 80 % de réussite ». Que précises-tu ? <!--anki:6376583a3e3362543e7d-->
?
1. **Rapporter l'observation** : 4 succès sur 5 essais, soit 80 % sur cette petite démonstration ; l'estimation reste très incertaine.
2. **Définir le protocole** : cinq tâches différentes ou cinq répétitions d'une seule tâche ?
3. **Choisir les métriques** : succès au premier essai, pass@k si un vérificateur choisit une solution, pass^k pour la répétabilité.
4. **Élargir l'évaluation** à des cas représentatifs indépendants, avec répétitions si utiles.
5. **Rapporter incertitude et limites**, sans présenter le taux observé comme une garantie.

**Piège** : dire que cinq essais ne mesurent « rien », ou qu'ils suffisent à estimer précisément la production.

---

## Sources

- [NIST — test de McNemar pour observations binaires appariées](https://www.itl.nist.gov/div898/software/dataplot/refman1/auxillar/mcnemar.htm)

## Connexions
- [[65-probabilites-sampling|Probabilités & sampling]] — la source de la variabilité
- [[111-mlops-llmops-fondamentaux|MLOps fondamentaux]] — versioning et lineage
- [[112-cicd-modeles|CI/CD des modèles]] — tests et eval gates
- [[113-monitoring-drift-feedback|Monitoring & drift]] — les changements de version côté provider
- [[92-chainforge-evals-prompts|Evals]] — comparer des prompts sur un golden dataset
- [[91-langfuse-observabilite|Langfuse]] — les traces pour rejouer un appel
- [[62-optimisations-inference|Optimisations d'inférence]] — continuous batching et quantization
- [[51-fine-tuning-adaptation|Fine-tuning]] — des entraînements reproductibles
- [[94-evals-methodologie|Méthodologie d'évaluation]] — taille des jeux
- [[95-llm-as-judge|LLM-as-a-judge]] — corriger un juge imparfait
- [[11-serveurs-inference-llm|Serveurs d'inférence]] — vLLM, SGLang, TensorRT-LLM et leur réglage
- [[153-data-flywheel-versioning|Data flywheel & versioning]] — boucler sur les échecs, versionner les données
- [[54-entrainement-distribue|Entraînement distribué]] — mémoire et parallélismes d'entraînement
- [[67-speculative-decoding|Speculative decoding]] — générer plusieurs tokens par passage
- [[68-quantization|Quantization]] — réduire la précision pour gagner mémoire et vitesse
- [[96-evals-rag-agents|Évaluation des RAG & des agents]] — retrieval, trajectoires et pass^k
- [[97-evals-online-ab-testing|Evals online & A/B testing]] — mesurer en production
- [[98-debogage-agents|Débogage des agents]] — trouver la cause d'un échec dans une trace
- [[165-computer-use-agents-navigateur|Computer use & agents navigateur]] — agents qui utilisent des interfaces
- [[55-rl-agentique|RL agentique]] — entraîner un modèle sur des tâches d'agent
- [[00-moc-ai-engineering|MOC AI Engineering]]
