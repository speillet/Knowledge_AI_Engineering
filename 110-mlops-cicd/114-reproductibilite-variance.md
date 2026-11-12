# Reproductibilité & variance — Flashcards
Tags: #flashcards #ai-engineering #mlops #reproductibilite #evals #llm
<!-- summary: non-déterminisme à température 0, invariance au batch, seed, appel rejouable, tests sur des sorties variables, erreur standard et intervalles de confiance, comparaison appariée, pass@k et pass^k, variance du LLM-as-judge, fine-tuning reproductible, stabilité par tâche répétée, sélection des seeds, checkpoint ou artefact d’inférence, changement de dépendance isolé, audit sans replay possible. -->


Une température à 0 garantit-elle des sorties identiques ? <!--anki:6354476e2a6372354e28-->
?
**Non.** Les calculs GPU en **virgule flottante** ne sont pas associatifs : (a + b) + c ≠ a + (b + c). Un infime écart sur les logits suffit à changer le token choisi quand deux candidats sont presque à égalité, et toute la suite de la réponse diverge.

Le batching, les kernels ou une révision du backend peuvent changer l'ordre des calculs. Pour un test, distinguer invariants métier stables et égalité textuelle exacte ; répéter les essais sensibles et archiver la configuration effective.

---

D'où vient principalement le non-déterminisme d'un serveur d'inférence ? <!--anki:42575a626e2f243e7b46-->
?
Une source importante est la **non-invariance au batch** : les kernels peuvent modifier leur ordre de réduction selon la forme du calcul. Les arrondis changent alors légèrement les logits ; deux tokens proches peuvent échanger leur rang.

Avec le continuous batching, la forme dépend aussi des requêtes concurrentes. Une graine ne fixe donc pas tout l'environnement numérique. Des kernels ou modes déterministes réduisent certaines variations, avec des conditions et coûts propres au moteur. Vérifier également sampling, matériel, versions et opérations parallèles ; il n'existe pas une unique cause dominante pour tous les déploiements.

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
La **graine** initialise un générateur pseudo-aléatoire dans le périmètre pris en charge par la bibliothèque ou le moteur. Elle aide à répéter certains tirages dans une pile fixée ; elle ne fige ni toutes les opérations ni tout le système.

Plusieurs générateurs peuvent intervenir : préparation des données, sampler, modèle, workers ou GPU. Documenter ceux contrôlés et les versions utilisées, puis tester la répétabilité annoncée par l'environnement. En comparaison, répéter sur plusieurs graines prévues à l'avance et garder leurs résultats, y compris défavorables. Choisir après coup la meilleure graine revient à sélectionner une expérience, avec un risque de surapprentissage de l'évaluation.

---

Comment rendre un appel LLM rejouable ? <!--anki:693e60316b3025562574-->
?
Conserver, selon les droits et la rétention autorisés, **l'entrée effective, les versions et le résultat observé** : prompt rendu, contexte, paramètres, contrats d'outils et observations externes. Des références protégées peuvent remplacer certaines copies sensibles.

Distinguer replay d'observations enregistrées et nouvel appel aux services réels. Le premier isole l'orchestration ; le second peut rencontrer données, outils ou backend différents. Une référence inaccessible ou un modèle retiré empêche parfois la régénération. Pour une preuve historique, le résultat enregistré et son contexte restent donc distincts d'une promesse de recalcul identique. Tester régulièrement l'accès aux pièces nécessaires au diagnostic.

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

L'appariement permet de voir quelles tâches gagnent ou perdent, au lieu de masquer les compensations dans la moyenne. Si plusieurs runs viennent du même exemple, tenir compte de cette dépendance dans l'incertitude. Garder un test final séparé : sélectionner le meilleur prompt après de nombreux essais sur le même jeu finit par exploiter son bruit.

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

Répéter le jugement réduit une partie de l'aléa, mais **pas un biais systématique** : un juge qui préfère toujours les réponses longues peut rester très stable et se tromper. Mesurer l'accord avec des références humaines par type de cas, conserver la version du juge et inspecter les désaccords avant d'utiliser son score comme décision de déploiement.

---

Comment rendre un fine-tuning reproductible ? <!--anki:74213c39574676285476-->
?
Figer **données, ordre d'échantillonnage, seeds, base, code, bibliothèques, matériel et configuration distribuée**. Activer les options déterministes appropriées, par exemple `torch.use_deterministic_algorithms(True)`, en respectant leurs préconditions.

Exemple : reprendre un entraînement exige aussi états d'optimiseur, scheduler, générateurs aléatoires et position du sampler. Recharger seulement les poids avec la même seed ne reprend pas le même calcul.

Le déterminisme peut ralentir ou refuser une opération sans implémentation adaptée. Des changements de matériel ou de réduction distribuée peuvent modifier les résultats. Distinguer reproduction bit à bit dans une pile fixée et **reproductibilité des conclusions**, évaluée par plusieurs runs et des métriques comparables.

---

Faut-il viser le déterminisme partout ? <!--anki:4e404d572d6036633c3c-->
?
**Non.** Il sert là où l'on compare ou enquête : **tests, audits, débogage, evals comparatives**. En production, on **conçoit pour la variabilité** : validation des sorties, [[63-guided-generation|sorties contraintes]], retries et evals sur plusieurs runs. Un système fiable ne dépend pas d'un tirage chanceux.

Rendre déterministes les règles métier, l'autorisation et les calculs quand c'est possible, puis mesurer la variabilité des parties génératives. Pour une même demande, plusieurs formulations peuvent être acceptables alors qu'un montant doit rester exact. Définir des invariants de résultat et d'effet externe permet d'être fiable sans imposer un texte identique à chaque exécution.

---

Calcul : deux tâches équipondérées réussissent avec probabilités constantes 1 et 0,5. Les répétitions sont indépendantes pour chacune. Quel est leur pass^2 moyen, comparé au carré du succès moyen ? <!--anki:3237306434396163383139313463656161383761666134346137363531323363-->
?
Calculer d'abord la réussite répétée **par tâche**, puis moyenner :
```text
moyenne des pass^2 = (1² + 0,5²)/2 = 0,625
succès moyen = (1 + 0,5)/2 = 0,75
carré du succès moyen = 0,75² = 0,5625
```
Les valeurs diffèrent car les difficultés diffèrent. Pour ce protocole, deux essais répètent la même tâche ; ils ne rééchantillonnent pas une tâche du mélange à chaque tentative. Un succès global moyen de 75 % ne suffit donc pas à déterminer le pass^2 moyen. Préciser tâches, répétitions et pondération avant d'agréger.

---

Pourquoi répéter plusieurs fois chaque tâche avant de comparer la stabilité de deux agents ? <!--anki:3232383735333832656138383437646639376330653431323964366130323633-->
?
Un **score moyen** mélange difficulté des tâches et variance des exécutions. Un agent peut réussir toujours les mêmes cas, tandis qu'un autre réussit chaque cas de façon intermittente avec la même moyenne globale.

Répéter chaque tâche avec état initial contrôlé, puis rapporter succès moyen et distribution de fiabilité par tâche. Garder les répétitions groupées dans l'analyse de l'incertitude. Choisir la métrique selon le besoin : une automatisation sans supervision exige une régularité différente d'une génération où l'utilisateur sélectionne un candidat. Des appels répétés sur des tâches différentes ne mesurent pas cette stabilité.

---

Pourquoi conserver les graines défavorables dans une comparaison d'entraînements ? <!--anki:6664346537356230386264333462633938613036663063633866326266373665-->
?
Sélectionner seulement la **meilleure graine** transforme une répétition destinée à mesurer la variance en recherche de candidat. Le résultat rapporté devient favorablement sélectionné.

Définir avant l'essai nombre de runs, métrique et règle d'agrégation ; conserver scores et échecs de chaque run. Si une sélection est assumée, compter son coût et confirmer le candidat sur des données non utilisées pour la choisir. Une variance importante peut indiquer un entraînement instable ou un jeu trop petit. La dispersion des résultats est une information opérationnelle : elle influence le risque de la prochaine exécution automatique, pas seulement la qualité d'une publication.

---

À ne pas confondre : checkpoint d'entraînement et modèle exporté pour l'inférence ? <!--anki:3063626564653532306165333462376562656131386565653235303237353961-->
?
Un **checkpoint d'entraînement** peut inclure poids, optimiseur, scheduler, états aléatoires et position de lecture nécessaires à la reprise. Un **artefact d'inférence** contient ce que le service doit charger pour prédire, avec son contrat et ses dépendances.

Exporter les seuls poids n'assure pas une reprise fidèle du calcul ; garder tout l'état d'entraînement n'assure pas un paquet léger ou sûr pour le serving. Définir deux contrats et politiques de rétention, puis tester reprise et chargement séparément. Le format exact dépend du framework ; un fichier nommé `checkpoint` ne prouve pas à lui seul quels états il contient.

---

Pourquoi tester séparément une nouvelle dépendance et de nouveaux poids ? <!--anki:3831393435343162333339393463313962636361376334616639656532313664-->
?
Changer simultanément **bibliothèques et modèle** empêche d'attribuer facilement un écart. Une différence peut venir de la sérialisation, d'un calcul numérique, d'un prétraitement ou de l'apprentissage.

Comparer, lorsque les combinaisons sont compatibles, ancien modèle/ancienne pile, ancien modèle/nouvelle pile et nouveau modèle/nouvelle pile sur les mêmes cas. Mesurer types, valeurs, décisions et coûts avec des tolérances explicites. Une pile ancienne peut ne pas charger le nouveau format : documenter cette limite plutôt que fabriquer un résultat comparable. Ce protocole ne supprime pas toute interaction, mais réduit l'enquête et donne un chemin de migration plus facile à valider.

---

Comment expliquer une décision historique si le modèle fournisseur utilisé a été retiré ? <!--anki:6365646334323839653266313462613362353134396131373965343638393331-->
?
Distinguer **preuve de ce qui s'est passé** et **capacité à le régénérer**. Sans accès au modèle d'origine, une nouvelle exécution identique peut être impossible, même avec prompt et paramètres conservés.

S'appuyer sur résultat enregistré, contexte autorisé, référence fournisseur, version applicative et preuves d'actions externes, selon la politique de rétention. Une autre version peut servir à analyser le comportement, mais son résultat ne remplace pas celui observé historiquement. Prévoir cette limite avant le choix du service et tester la récupération des pièces d'audit. Archiver des données sensibles sans finalité ni contrôle n'est pas une solution universelle.

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

- [PyTorch — reproductibilité et sources d’aléa](https://docs.pytorch.org/docs/stable/notes/randomness.html)
- [scikit-learn — persistance et compatibilité des environnements](https://scikit-learn.org/stable/model_persistence.html)

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
- [[118-artefacts-registre-releases-ml|Artefacts, registre et releases ML]] — contrats et vérifications de production
- [[00-moc-ai-engineering|MOC AI Engineering]]
