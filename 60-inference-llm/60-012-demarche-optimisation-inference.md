# Démarche d’optimisation de l’inférence LLM — Flashcards
Tags: #flashcards #ai-engineering #inference #performance #profiling #finops
Vérifié le : 8 octobre 2026
<!-- summary: objectif sous contraintes, profilage CPU/GPU, graphes CUDA et compilation, kernels, loi d’Amdahl, interactions entre optimisations, quotas API, retries, routage, raisonnement et multimodal, coût marginal d'une optimisation. -->


Que signifie maximiser l’inférence d’un LLM dans un produit ? <!--anki:3766383238393464336537333434323438393562383237363466353762663831-->
?
Choisir une cible utile : **plus de tâches réussies par seconde ou par euro**, sous contraintes de qualité, délais, capacité et équité. Le maximum de tokens/s n'est pertinent que si ces tokens servent réellement la tâche.

Construire une frontière de compromis : conserver les configurations qu'aucune autre n'améliore sur tous les critères retenus. Exemple : A sert 40 tâches réussies/s avec un p95 de 1,2 s, B 55 avec 2,5 s, C 38 avec 1,4 s. C est dominée par A ; un SLO de 2 s élimine ensuite B. Fixer d'abord les exigences incontournables, puis choisir parmi les options admissibles, en incluant réserve et charge réelle.

---

Comment passer d’un symptôme de lenteur à une hypothèse d’optimisation ? <!--anki:3536626435386262303236373461366638646339666264376663633731323337-->
?
Décomposer le parcours : file, tokenization, prefill, decode, communication, outils et validation. Relier **temps perdu et ressource limitante** sur des cas comparables.

Exemple : avec 800 ms de file et 80 ms de prefill, diviser uniquement ce prefill par deux économise 40 ms, à file inchangée. L'attente dominante appelle une hypothèse de capacité ou d'admission, pas seulement un meilleur kernel.

Pour chaque hypothèse, définir changement isolé, métrique attendue, garde-fous qualité/mémoire et critère d'abandon. Rejouer la charge, car le changement peut modifier la file et déplacer le goulot. GPU actif et cache plein restent des indices, pas des causes prouvées.

---

Comment utiliser un profileur sans fausser la mesure de performance ? <!--anki:3962356234336165633238313432626539303964643239613930386334616266-->
?
Capturer une **courte fenêtre représentative après échauffement**, avec événements CPU et GPU et, si nécessaire, allocations mémoire. Examiner les kernels, copies, lancements et synchronisations sur une chronologie commune.

PyTorch Profiler ou les outils du moteur aident à localiser le travail, mais collecte des formes, piles et traces détaillées peut perturber le temps mesuré. Comparer la performance finale sans instrumentation lourde. Mesurer plusieurs cas de charge : un profil à batch 1 n'explique pas nécessairement le goulot à forte concurrence. Ne pas confondre temps CPU d'envoi et exécution GPU asynchrone.

---

Que chercher quand le GPU attend alors que le service d’inférence est lent ? <!--anki:3130366432316562616136323462396439646538386239363733326132303266-->
?
Examiner **CPU, tokenization, traitement d'images, sérialisation, réseau, stockage et ordonnanceur**. Une limite de threads, un quota CPU, un placement NUMA défavorable ou une boucle événementielle bloquée peuvent empêcher d'alimenter le GPU.

Comparer temps avant moteur et temps GPU, puis tester une requête directement et via le parcours complet. Exemple : un conteneur limité à 2 cœurs tokenise et diffuse 64 flux ; dans le `cpu.stat` de son cgroup, `nr_throttled` augmente pendant que le GPU reste à moitié inactif. Ajouter un GPU n'y change rien. Après correction, refaire le test : le GPU peut devenir le nouveau facteur limitant.

---

À ne pas confondre : graphes CUDA, compilation et fusion de kernels ? <!--anki:3036643739623566646238333438663561383034363366616230326136666332-->
?
Les **graphes CUDA** rejouent une séquence d'opérations pour réduire les coûts de lancement. La **compilation** transforme et spécialise le programme. La **fusion** réunit des opérations pour diminuer lancements ou données intermédiaires.

Ces techniques se complètent, avec des contraintes de formes. vLLM, par exemple, capture des graphes pour une liste de tailles de batch : un batch de 13 séquences est complété jusqu'à la taille capturée suivante, et au-delà de la plus grande l'exécution redevient classique. `--enforce-eager` désactive ces graphes pour mesurer leur apport. Capture et compilation coûtent du démarrage et de la mémoire.

---

Comment choisir un backend d’attention ou un kernel plus rapide ? <!--anki:3066363861666266633336313461356462393264343536396338623637373066-->
?
Vérifier compatibilité avec GPU, dtype, dimensions, masque d'attention, contexte, quantification et mode de génération. Un kernel rapide dans un microbenchmark peut être rarement utilisé dans le service, ou provoquer des conversions coûteuses.

Exemple : un backend gagne 25 % sur un microbenchmark en BF16, mais le service stocke son KV cache en FP8, format qu'il ne prend pas en charge ; le moteur reste sur l'ancien chemin et le gain réel est nul. Comparer numériquement au backend de référence, valider les sorties sur les tâches critiques, puis mesurer tout le parcours aux longueurs et concurrences cibles.

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

Calcul : chaque requête compte 1 000 tokens d’entrée et 500 de sortie. Quel plafond moyen avec les quotas fictifs 600 requêtes/min, 60 000 tokens d’entrée/min et 20 000 tokens de sortie/min ? <!--anki:3038643039393265373463333434353661616235366537383265306364373831-->
?
Supposons **1 000 tokens d'entrée et 500 de sortie par requête**, tous comptés dans ces quotas fictifs :
```text
requêtes : 600/min
entrée   : 60 000 / 1 000 = 60 requêtes/min
sortie   : 20 000 / 500   = 40 requêtes/min
plafond moyen = min(600, 60, 40) = 40 requêtes/min
```
La sortie limite ici, avant même latence et capacité du fournisseur. Vérifier fenêtres, bursts, quotas partagés, estimation/réservation et traitement du cache dans l'API réelle. Réduire les entrées ne lève pas ce goulot ; borner les sorties exige de préserver la qualité.

Le minimum de ces plafonds est nécessaire mais peut ne pas être soutenable : variations de longueur, rafales et fenêtres glissantes créent des rejets. Lisser les appels et mesurer les limites réellement appliquées par le service.

---

Pourquoi retries et hedging peuvent-ils réduire le débit utile d’un LLM ? <!--anki:3433656533303238313566313437666262363965353837363738393865303835-->
?
Un **retry** relance un appel ; le **hedging** lance une tentative concurrente pour réduire l'attente de la plus lente. Tous deux ajoutent du travail, parfois alors que l'appel initial continue.

Cent tâches avec 20 % de doubles tentatives imposent 120 appels, avant reprises supplémentaires. Fixer un budget global, backoff avec jitter et échéance propagée ; respecter les indications de quota. Annuler la tentative perdante et éviter les effets d'outils dupliqués. Mesurer amplification, coût et succès par tâche : une latence améliorée à faible charge peut devenir une tempête de retries en surcharge.

---

Comment optimiser une cascade de modèles sans déplacer le coût vers les reprises ? <!--anki:3531323830363532366339353436366162346233626465373364303738623563-->
?
Router vers un modèle plus petit lorsque les évaluations montrent qu'il suffit, et escalader selon des critères vérifiés. Mesurer coût et délai **de toute la cascade**, incluant contrôle et second appel.

Le contrôle décide du coût. Exemple : s'il rejette 60 % des réponses du petit modèle, dont la moitié étaient correctes, la majorité des tâches paie deux appels et attend deux fois. Mesurer ses faux rejets sur un jeu étiqueté et router d'emblée vers le grand modèle les segments qui escaladent presque toujours. Comparer succès par segment et coût par tâche, pas seulement le prix du modèle choisi en premier.

---

Comment maîtriser le budget de raisonnement et les branches parallèles d’un agent ? <!--anki:6162353566333163626434643433663461376134386465626464323132373831-->
?
Borner nombre d'appels, tokens, temps total et branches concurrentes, selon les mécanismes réellement exposés par le modèle et l'orchestrateur. Évaluer la **qualité gagnée par calcul supplémentaire**, notamment sur les tâches difficiles.

Un raisonnement plus long ou plusieurs candidats améliorent certains résultats et gaspillent des ressources sur d'autres. Exemple : quatre branches de 3 000 tokens coûtent 12 000 tokens pour une durée proche d'une seule ; si elles ne gagnent des points que sur les tâches difficiles, les réserver à cette catégorie. Compter aussi appels d'outils, juge et tentatives annulées. Fixer une règle d'arrêt explicite.

---

Pourquoi les tokens textuels ne suffisent-ils pas à dimensionner l’inférence multimodale ? <!--anki:3436373435326462393331643462303239363238323537353730313263326431-->
?
Image, audio et vidéo ajoutent décodage, redimensionnement, encodage et représentations dont le coût dépend de résolution, durée, fréquence d'images et architecture. Une question de dix mots sur une vidéo de 60 s échantillonnée à 2 images/s fait encoder 120 images.

Mesurer taille des médias, unités du processeur, temps d'encodage, mémoire de pointe et transferts, en plus du prefill/decode textuel. Distinguer unités facturées et unités réellement traitées par le moteur. Segmenter les benchmarks par modalité et tester les combinaisons : un frontend média ou un encodeur peut saturer avant le décodeur LLM.

---

Pourquoi mesurer le coût marginal d'une optimisation en plus de son gain de latence ? <!--anki:3933353536386638623666623438613239616663386637373939666533346635-->
?
Une **optimisation** peut réduire la latence en consommant davantage de GPU, de mémoire ou d'appels. Dupliquer une requête chez deux fournisseurs accélère parfois la première réponse tout en augmentant le coût et la charge.

Comparer au même volume offert et au même niveau de qualité : latence, goodput, ressources et coût par tâche utile. Inclure appels perdants et annulations tardives. Tester le régime saturé ; une technique rentable à faible charge peut réduire la capacité de toute la plateforme. Fixer l'objectif produit avant de choisir le meilleur chiffre.

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
