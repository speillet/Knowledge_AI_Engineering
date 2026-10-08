# Démarche d’optimisation de l’inférence LLM — Flashcards
Tags: #flashcards #ai-engineering #inference #performance #profiling #finops
Vérifié le : 8 octobre 2026
<!-- summary: objectif sous contraintes, profilage CPU/GPU, graphes CUDA et compilation, kernels, loi d’Amdahl, interactions entre optimisations, quotas API, retries, routage, raisonnement et multimodal. -->


Que signifie maximiser l’inférence d’un LLM dans un produit ? <!--anki:3766383238393464336537333434323438393562383237363466353762663831-->
?
Choisir une cible utile : **plus de tâches réussies par seconde ou par euro**, sous contraintes de qualité, délais, capacité et équité. Le maximum de tokens/s n'est pertinent que si ces tokens servent réellement la tâche.

Construire une frontière de compromis : conserver les configurations qu'aucune autre n'améliore sur tous les critères retenus. Certaines favorisent la latence individuelle, d'autres le traitement batch. Fixer d'abord les exigences incontournables, puis choisir dans les options admissibles. Inclure réserve et charge réelle ; une configuration optimale à saturation peut coûter trop cher en période creuse.

---

Comment passer d’un symptôme de lenteur à une hypothèse d’optimisation ? <!--anki:3536626435386262303236373461366638646339666264376663633731323337-->
?
Décomposer le parcours puis relier **temps perdu et ressource limitante** : file, tokenization, prefill, decode, communication, streaming, outils et validation. Comparer un cas lent à un cas comparable normal.

Écrire une hypothèse vérifiable : « si les collectives dominent, réduire le TP devrait diminuer leur part, avec mémoire et qualité inchangées ». Prévoir métrique attendue, contrôle et critère d'abandon. Un GPU actif ou un cache plein est un indice, pas une cause prouvée. Refaire la décomposition après le changement : le goulot peut se déplacer.

---

Comment utiliser un profileur sans fausser la mesure de performance ? <!--anki:3962356234336165633238313432626539303964643239613930386334616266-->
?
Capturer une **courte fenêtre représentative après échauffement**, avec événements CPU et GPU et, si nécessaire, allocations mémoire. Examiner les kernels, copies, lancements et synchronisations sur une chronologie commune.

PyTorch Profiler ou les outils du moteur aident à localiser le travail, mais collecte des formes, piles et traces détaillées peut perturber le temps mesuré. Comparer la performance finale sans instrumentation lourde. Mesurer plusieurs cas de charge : un profil à batch 1 n'explique pas nécessairement le goulot à forte concurrence. Ne pas confondre temps CPU d'envoi et exécution GPU asynchrone.

---

Que chercher quand le GPU attend alors que le service d’inférence est lent ? <!--anki:3130366432316562616136323462396439646538386239363733326132303266-->
?
Examiner **CPU, tokenization, traitement d'images, sérialisation, réseau, stockage et ordonnanceur**. Une limite de threads, un quota CPU, un placement NUMA défavorable ou une boucle événementielle bloquée peuvent empêcher d'alimenter le GPU.

Comparer temps avant moteur et temps GPU, files de chaque étape, copies et utilisation des cœurs. Tester une requête directement puis via le parcours complet avec les mêmes données. Augmenter les GPU ne corrige pas un frontend saturé. Après correction CPU ou I/O, refaire le test : le GPU peut devenir le nouveau facteur limitant.

---

À ne pas confondre : graphes CUDA, compilation et fusion de kernels ? <!--anki:3036643739623566646238333438663561383034363366616230326136666332-->
?
Les **graphes CUDA** rejouent une séquence d'opérations pour réduire les coûts de lancement. La **compilation** transforme et spécialise le programme. La **fusion** réunit des opérations pour diminuer lancements ou données intermédiaires.

Ces techniques se complètent, avec des contraintes de formes et de compatibilité. Capture, compilation, réserves mémoire et éventuelles variantes de formes ont un coût ; certains chemins restent en exécution classique. Mesurer démarrage, mémoire de pointe et régime établi. Un gain à forme fixe peut disparaître avec un trafic très variable ou une opération non prise en charge.

---

Comment choisir un backend d’attention ou un kernel plus rapide ? <!--anki:3066363861666266633336313461356462393264343536396338623637373066-->
?
Vérifier compatibilité avec GPU, dtype, dimensions, masque d'attention, contexte, quantification et mode de génération. Un kernel rapide dans un microbenchmark peut être rarement utilisé dans le service, ou provoquer des conversions coûteuses.

Comparer numériquement au backend de référence et valider les sorties sur les tâches critiques. Mesurer ensuite tout le parcours, aux longueurs et concurrences cibles. Inclure compilation et mémoire des espaces de travail si elles comptent pour le produit. Ne pas transposer un record de matrice isolée à une amélioration de TTFT ou de goodput.

---

Calcul : quel gain maximal si le decode représente 60 % du temps et devient deux fois plus rapide ? <!--anki:3663343736343064393438303434633938653934653930623361353134336639-->
?
À travail identique et sans interaction, la loi d'Amdahl donne :
```text
nouveau temps relatif = 0,40 + 0,60 / 2 = 0,70
accélération globale = 1 / 0,70 ≈ 1,43
```
Même un decode instantané limiterait le gain à `1 / 0,40 = 2,5`. Cette estimation aide à prioriser l'effort ; elle ne prédit pas directement un p95 ni un système en file d'attente. Sous charge, les changements de contention et de batching modifient les proportions. Vérifier le parcours complet après optimisation.

---

Pourquoi tester séparément puis ensemble les optimisations d’inférence ? <!--anki:6162343531366138386438373462636462303230396662623865356333616161-->
?
Une amélioration isolée peut disparaître ou s'inverser dans une combinaison : quantifier libère de la mémoire, un batch plus grand la remplit, puis la vérification spéculative accroît le calcul.

Commencer par des variantes attribuables à un changement, puis tester les combinaisons plausibles. Garder données, qualité et charge comparables, et relever effets sur CPU, KV et communications. Conserver la baseline et un rollback versionné. Éviter de multiplier tous les réglages sans hypothèse : un petit plan d'expérience ciblé explique mieux les gains et réduit le risque de choisir un résultat chanceux.

---

Calcul : quel débit maximal avec 600 RPM, 60 000 tokens d’entrée/min et 20 000 tokens de sortie/min ? <!--anki:3038643039393265373463333434353661616235366537383265306364373831-->
?
Supposons **1 000 tokens d'entrée et 500 de sortie par requête**, tous comptés dans ces quotas fictifs :
```text
requêtes : 600/min
entrée   : 60 000 / 1 000 = 60 requêtes/min
sortie   : 20 000 / 500   = 40 requêtes/min
plafond moyen = min(600, 60, 40) = 40 requêtes/min
```
La sortie limite ici, avant même latence et capacité du fournisseur. Vérifier fenêtres, bursts, quotas partagés, estimation/réservation et traitement du cache dans l'API réelle. Réduire les entrées ne lève pas ce goulot ; borner les sorties exige de préserver la qualité.

---

Pourquoi retries et hedging peuvent-ils réduire le débit utile d’un LLM ? <!--anki:3433656533303238313566313437666262363965353837363738393865303835-->
?
Un **retry** relance un appel ; le **hedging** lance une tentative concurrente pour réduire l'attente de la plus lente. Tous deux ajoutent du travail, parfois alors que l'appel initial continue.

Cent tâches avec 20 % de doubles tentatives imposent 120 appels, avant reprises supplémentaires. Fixer un budget global, backoff avec jitter et échéance propagée ; respecter les indications de quota. Annuler la tentative perdante et éviter les effets d'outils dupliqués. Mesurer amplification, coût et succès par tâche : une latence améliorée à faible charge peut devenir une tempête de retries en surcharge.

---

Comment optimiser une cascade de modèles sans déplacer le coût vers les reprises ? <!--anki:3531323830363532366339353436366162346233626465373364303738623563-->
?
Router vers un modèle plus petit lorsque les évaluations montrent qu'il suffit, et escalader selon des critères vérifiés. Mesurer coût et délai **de toute la cascade**, incluant contrôle et second appel.

Éviter les escalades systématiques après une première tentative inutile. Réduire contexte et verbosité en préservant les preuves et le format nécessaires. Un cache de réponse peut supprimer une génération, mais nécessite contrôle de fraîcheur, autorisations et clés pertinentes. Comparer succès par segment et coût par tâche, pas seulement le prix du modèle choisi en premier.

---

Comment maîtriser le budget de raisonnement et les branches parallèles d’un agent ? <!--anki:6162353566333163626434643433663461376134386465626464323132373831-->
?
Borner nombre d'appels, tokens, temps total et branches concurrentes, selon les mécanismes réellement exposés par le modèle et l'orchestrateur. Évaluer la **qualité gagnée par calcul supplémentaire**, notamment sur les tâches difficiles.

Un raisonnement plus long ou plusieurs candidats peuvent améliorer certains résultats et gaspiller des ressources sur d'autres. Compter tokens internes disponibles, appels d'outils, juge et tentatives annulées. La parallélisation peut réduire la latence murale tout en augmentant le coût et la pression sur les quotas. Ajuster le budget par catégorie de tâche, avec une règle d'arrêt explicite.

---

Pourquoi les tokens textuels ne suffisent-ils pas à dimensionner l’inférence multimodale ? <!--anki:3436373435326462393331643462303239363238323537353730313263326431-->
?
Image, audio et vidéo ajoutent décodage, redimensionnement, encodage et représentations dont le coût dépend de résolution, durée, fréquence d'images et architecture. Deux requêtes avec le même texte peuvent avoir des coûts très différents.

Mesurer taille des médias, unités du processeur, temps d'encodage, mémoire de pointe et transferts, en plus du prefill/decode textuel. Distinguer unités facturées et unités réellement traitées par le moteur. Segmenter les benchmarks par modalité et tester les combinaisons : un frontend média ou un encodeur peut saturer avant le décodeur LLM.

---

## Mises en situation

Mise en situation : tu dois doubler le nombre de réponses utiles sans augmenter le budget GPU. Quelle démarche proposes-tu ? <!--anki:6166356234316436373062623432656539666363386435646465653061323765-->
?
1. **Fixer le contrat** : tâches, qualité et délais, avec une baseline au trafic réel.
2. **Mesurer le gaspillage** : travail abandonné, reprises, contexte inutile, cache manquant et ressources inactives.
3. **Profiler le goulot**, puis choisir quelques leviers adaptés : scheduler, kernels, précision, modèle ou routage.
4. **Comparer seuls puis combinés** avec coût par réussite et marge en surcharge.
5. **Livrer le gain démontré** et les limites ; si doubler est impossible sous les contraintes, documenter l'arbitrage requis.

**Piège** : promettre un facteur deux avant d'avoir mesuré la part réellement optimisable.

---

Mise en situation : les kernels GPU accélèrent de 30 %, mais la latence utilisateur ne bouge pas. Que fais-tu ? <!--anki:6535636561303237643638353432323939316164306238636562323363303466-->
?
1. **Mesurer leur part initiale** dans le chemin critique, puis appliquer une borne d'Amdahl.
2. **Examiner l'amont et l'aval** : file, tokenization, médias, gateway, rendu et outils.
3. **Vérifier le chemin exécuté** : nouveau kernel réellement utilisé ou fallback sur certaines formes.
4. **Comparer sans profilage lourd**, avec cache, longueurs et charge identiques.
5. **Cibler le goulot restant** ou retenir seulement le bénéfice démontré, par exemple mémoire ou capacité.

**Piège** : annoncer un gain applicatif à partir d'un temps GPU isolé.

---

Mise en situation : augmenter la concurrence des appels API produit surtout des erreurs 429. Comment réagis-tu ? <!--anki:6562653731663163646363353465383862316436306334373338313137333138-->
?
1. **Identifier le quota** : requêtes, entrées, sorties, modèle, organisation ou rafale.
2. **Mesurer le rythme réel** et l'amplification due aux retries.
3. **Limiter l'admission** et lisser les envois avec une file bornée par échéance.
4. **Réduire le travail pertinent** ou différer les tâches compatibles ; demander davantage de quota si le besoin demeure.
5. **Valider le débit utile** après backoff et annulation des appels expirés.

**Piège** : compenser un quota dépassé par plus de parallélisme ou par des relances immédiates.

---

## Sources

- [PyTorch — profiler et activité CPU/GPU](https://docs.pytorch.org/tutorials/recipes/recipes/profiler_recipe.html)
- [vLLM — graphes CUDA](https://docs.vllm.ai/en/latest/design/cuda_graphs/)
- [vLLM — kernels et configuration de serving](https://docs.vllm.ai/en/latest/configuration/optimization/)
- [Anthropic — exemple de quotas RPM, ITPM et OTPM](https://platform.claude.com/docs/en/api/rate-limits)
- [AWS Builders’ Library — timeouts, retries et jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)

## Connexions
- [[62-optimisations-inference|Optimisations d’inférence]] — les mécanismes à tester selon le goulot
- [[60-010-benchmarks-charge-inference|Benchmarks de charge]] — comparaisons reproductibles
- [[60-011-capacite-ordonnancement-inference|Capacité & ordonnancement]] — budgets et admission
- [[121-couts-inference|Coûts d’inférence]] — coût et énergie par tâche utile
- [[138-modeles-raisonnement|Modèles de raisonnement]] — mesurer le rendement du calcul supplémentaire
- [[00-moc-ai-engineering|MOC AI Engineering]]
