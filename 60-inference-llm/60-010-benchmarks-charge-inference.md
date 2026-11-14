# Benchmarks de charge pour l’inférence LLM — Flashcards
Tags: #flashcards #ai-engineering #inference #benchmark #performance
Vérifié le : 8 octobre 2026
<!-- summary: protocole reproductible, boucle ouverte ou fermée, omission coordonnée, mix de requêtes, cache froid/chaud, saturation, incertitude, limites du générateur, capacité sous SLO, tests de rafales, biais de survivants, durée du plateau. -->


Quel contrat fixer avant un benchmark d’inférence LLM ? <!--anki:3464663735636264643633333437376238393536656231303262323632633333-->
?
Fixer **tâche, qualité minimale, charge cible, latences et coût acceptable** avant de comparer les moteurs. Exemple pour un assistant de support : 20 demandes/s en pointe, 95 % de réponses conformes à la grille, premier contenu sous 1 s et réponse complète sous 8 s au p95, au plus 0,5 centime par réponse.

Préciser unité des tokens, périmètre client/moteur et traitement des rejets, retries et annulations. Un benchmark de génération synthétique mesure un système ; il ne démontre pas la qualité métier. Conserver la baseline comme point de comparaison.

---

À ne pas confondre : benchmark en boucle ouverte et en boucle fermée ? <!--anki:6465343464653161326536363437313362666232373039613261626466396631-->
?
En **boucle ouverte**, les arrivées suivent un calendrier indépendant des réponses. Cela permet d'observer la croissance d'une file lorsque la demande dépasse la capacité.

En **boucle fermée**, un nombre fixé de clients attend la fin d'une requête avant d'en envoyer une autre : une réponse lente ralentit les arrivées. Avec 50 clients sans temps de réflexion, des réponses de 2 s donnent 25 demandes/s ; à 10 s, la charge tombe à 5 demandes/s, alors qu'une demande extérieure continuerait d'arriver. Ce modèle convient aux sessions avec cette dépendance. Déclarer le modèle d'arrivée, les temps de réflexion et toute limite de concurrence.

---

Qu’est-ce que l’omission coordonnée dans un test de charge ? <!--anki:6364633065373238373935613436396461356633323432336438343465343930-->
?
Le générateur cesse ou retarde ses envois quand le système ralentit, puis mesure seulement les demandes qu'il a effectivement envoyées. Il omet ainsi des attentes qu'auraient subies des arrivées indépendantes : la queue de latence paraît meilleure.

Exemple : un client prévu toutes les 100 ms reste bloqué 2 s sur une réponse. Les 19 envois prévus pendant ce blocage auraient attendu de 0,1 à 1,9 s de plus ; l'histogramme n'en compte aucun. Comparer heure prévue et heure réelle d'émission. Une correction statistique ne recrée pas le travail que le serveur n'a jamais reçu.

---

Comment construire un mix de requêtes représentatif pour un LLM ? <!--anki:3639316435666364353065303466613362663961396536623961303035343365-->
?
Préserver la **distribution conjointe** des longueurs d'entrée et de sortie, les pointes d'arrivée, les préfixes communs et les tours d'une conversation. Ajouter les proportions de langues, outils, formats contraints, images ou raisonnement pertinentes.

Des requêtes toutes à 1 000 tokens d'entrée et 500 de sortie ont les mêmes moyennes qu'un mélange de résumés (1 900 en entrée, 100 en sortie) et de rédactions (100 et 900) ; le second alterne prefill lourd et longs decodes. Séparer les segments critiques et inclure les longues traînes. Des prompts aléatoires ne reproduisent pas la structure réelle du cache.

---

Pourquoi séparer échauffement du moteur et échauffement du cache de préfixes ? <!--anki:6166663133613332363562343438633362656337383561303734613133346232-->
?
Le moteur peut payer au démarrage chargement, compilation, capture de graphes et initialisation des kernels. Le cache de préfixes devient chaud en réutilisant du contenu ; c'est un autre phénomène.

Mesurer démarrage, régime établi avec cache froid, puis trafic avec réutilisation réaliste. Faire l'échauffement technique avec des données distinctes. Réinitialiser ou contrôler le cache entre variantes : avec un system prompt commun de 3 000 tokens, la variante testée en second le trouve en cache et économise ce prefill sur chaque requête, sans être meilleure. Conserver aussi un scénario de redémarrage ou d'arrivée d'un nouveau réplica.

---

Que conserver dans le manifeste d’un benchmark d’inférence ? <!--anki:3565633531303463376362623436623561626632343630616339383137396339-->
?
Archiver cinq ensembles :
- **Modèle** : révision, tokenizer, template, précision et paramètres de génération.
- **Moteur** : version, image, scheduler, budgets, caches et parallélismes.
- **Machine** : GPU, interconnexion, CPU, mémoire, pilotes et limites de puissance.
- **Trafic** : jeu versionné, ordre, graines, arrivées, longueurs réelles et état initial.
- **Mesure** : outil/version, périmètre, durée, timeouts, résultats détaillés et critères de qualité.

Un nom de modèle et un nombre de GPU ne suffisent pas : deux runs du même modèle sur 8 GPU divergent si l'un ignore EOS et produit 512 tokens fixes, l'autre des longueurs réelles. Conserver les commandes exactes et les écarts au protocole.

---

Comment trouver la capacité soutenable sous SLO ? <!--anki:6336333434343034663135343435306361643434323563346234633134323165-->
?
Balayer plusieurs taux d'arrivée, puis raffiner près de la zone où latences ou files augmentent fortement. À chaque palier, mesurer débit offert, terminé, utile, refus, longueurs et pente de la file.

Exemple : jusqu'à 12 demandes/s, chaque segment respecte son SLO et la file reste stable ; à 14, elle croît sans cesse, même si le débit terminé semble constant. Raffiner entre 12 et 14, répéter près de la frontière, puis retenir une marge justifiée par variabilité, démarrage et panne. Le meilleur point d'un essai court n'est pas une garantie de production.

---

Comment comptabiliser le début et la fin d’un benchmark ? <!--anki:3062313036336261633835373462306162616230393433333136343239303165-->
?
Définir une phase de mesure après échauffement, puis une **vidange** des requêtes encore en vol. Distinguer débit sur une fenêtre stable et résultat d'une cohorte d'arrivées suivie jusqu'à résolution.

Ne pas supprimer les demandes qui débordent la fin du test : comptabiliser leur fin, timeout ou statut inachevé. Si la durée inclut la vidange, le dire. Archiver arrivées et départs pour réconcilier les volumes. Exemple : un test de 10 minutes s'arrête avec 40 réponses longues encore en vol ; les exclure retire précisément les plus lentes et favorise la configuration qui accumule du travail.

---

Comment mesurer l’incertitude d’un résultat de performance LLM ? <!--anki:3033343963363063663664393461313161323332623430373933303530613265-->
?
Répéter les essais, alterner l'ordre des variantes et comparer le même trafic. Rapporter dispersion, nombre de requêtes et nombre de répétitions, pas seulement le meilleur run.

Les latences successives peuvent être corrélées par les files ou les pics : un bootstrap par blocs ou une comparaison entre runs est plus prudent qu'une hypothèse d'indépendance aveugle. Un p99 sur 100 demandes est très instable. Adapter durée et précision à la décision ; une différence minuscule ne justifie pas une migration coûteuse sans preuve reproductible.

---

Comment vérifier que le générateur de charge ne limite pas le benchmark ? <!--anki:3466323961336365353836653435636538653564613236623363656166633232-->
?
Surveiller CPU, boucle événementielle, connexions, bande passante et retards d'émission du client. Vérifier que les arrivées réelles correspondent au calendrier prévu et que les tokens sont comptés avec le tokenizer attendu.

Un plafond côté client peut laisser le serveur sous-chargé tout en donnant l'impression d'une saturation. Signe typique : deux moteurs très différents plafonnent au même débit, le cœur CPU du générateur est à 100 % et le retard d'émission croît. Répartir alors la génération, sans perdre la cohérence temporelle. Tester également le proxy et le streaming : regroupement des chunks, TLS et réseau font partie du parcours lorsqu'on annonce une performance côté utilisateur.

---

Comment interpréter request-rate et max-concurrency dans un benchmark vLLM ? <!--anki:3364373366333239396338643431353561656131373639303232323963656238-->
?
**`--request-rate`** fixe le rythme demandé ; **`--max-concurrency`** limite les requêtes simultanées. Une limite active peut empêcher de produire la charge annoncée.

Exemple : avec 20 requêtes en vol au maximum et une durée moyenne de 2 secondes, le débit réalisé plafonne autour de **10 requêtes/s** en régime stable, même si 50 étaient demandées. Le test n'est plus une arrivée ouverte non contrainte ; une faible latence peut masquer cette limitation.

Vérifier version et `vllm bench serve --help`. Publier rythme demandé/réalisé, retard d'émission, longueurs, erreurs et population des percentiles ; documenter aussi échauffement, cache et burstiness.

---

Calcul : à 100 demandes/s offertes, A en termine 100 dont 70 conformes au SLO ; B en termine 90 dont 85 conformes et rejette 10. Comparer goodput et taux de satisfaction de la demande ? <!--anki:6237643931336361636437353463356362346235393334653930363830663633-->
?
Sur une même charge stable de 100 demandes/s, A termine 100 demandes/s dont **70 satisfont ensemble** qualité et délais. B en termine 90 dont **85 sont conformes**, et rejette les 10 restantes.

A fournit 70 réussites utiles/s, B 85. B a un meilleur goodput, mais son taux de rejet peut rendre l'option inacceptable selon le contrat. Comparer aussi coût et taux de satisfaction sur les **100 demandes offertes**, soit 70 % et 85 %. Maximiser le goodput ne dispense pas d'une exigence minimale de service.

---

À ne pas confondre : benchmark synthétique et replay applicatif ? <!--anki:3136393261613361666439333431646162313531343664333132343731313532-->
?
Le **synthétique** contrôle longueurs, arrivées et paramètres ; il isole un effet et révèle les limites du moteur. Avec `--ignore-eos`, chaque requête produit exactement son `max_tokens`, par exemple 256 : le decode devient comparable entre variantes, mais la tâche n'est plus celle du produit.

Le **replay applicatif** garde davantage de distributions, préfixes et dépendances, mais doit être sécurisé et versionné. Réévaluer la qualité si modèle ou génération changent : le nombre de tokens réellement produits peut varier. Utiliser les deux ; ni débit à longueur forcée ni replay isolé ne prouvent à eux seuls la capacité d'un agent complet.

---

Pourquoi un benchmark LLM doit-il inclure les rafales plutôt que seulement un débit moyen constant ? <!--anki:3166643239346430383165613463623662663138323636363561653966396463-->
?
La **file d'attente** dépend de la variabilité des arrivées et du travail, pas seulement de leur moyenne. Une rafale peut dépasser la capacité disponible avant que l'autoscaling n'ait chargé le modèle.

Comparer plusieurs profils conservant le même volume : régulier, rafales et replay temporel. Mesurer attente, rejets, délais dépassés et temps de récupération, avec le même mix de tokens. Éviter de moyenner les percentiles de fenêtres. Un service stable à dix requêtes par seconde constantes n'est pas nécessairement prêt pour cent requêtes arrivant ensemble toutes les dix secondes.

---

Pourquoi exclure les requêtes échouées embellit-il artificiellement un benchmark d'inférence ? <!--anki:6166363136636533363765373438646462653062333331636161356134613666-->
?
Les requêtes les plus lentes peuvent disparaître du calcul après timeout. Le p95 des seules réussites s'améliore alors pendant que **le service se dégrade réellement**.

Publier taux d'erreur, dépassements de délai et distribution des réussites avec leurs dénominateurs. Classer les timeouts comme violations du contrat sans inventer leur durée de complétion. Conserver le nombre de demandes offertes : une politique de rejet ne doit pas transformer une faible couverture en apparente performance parfaite.

---

Pourquoi prolonger le plateau de charge après la fin du warmup d'un serveur LLM ? <!--anki:6433383531343066356233633437303438313164346262653230623833346237-->
?
Un court test peut manquer **l'accumulation de file, la croissance mémoire ou l'éviction du cache**. Le système paraît stable tant que ses réserves absorbent le déséquilibre.

Observer la pente du backlog et de la mémoire pendant un plateau suffisamment long, puis vérifier le retour au repos. La durée pertinente dépend du cycle d'exploitation étudié. Une file qui augmente continûment indique une charge non soutenable, même si le débit de sortie reste constant.

---

## Mises en situation

Mise en situation : un moteur annonce deux fois plus de tokens/s, mais le produit est plus lent. Comment compares-tu les résultats ? <!--anki:3638653361393636633635373437643639353266306564373830653233333237-->
?
1. **Aligner la tâche** : même jeu, tokenizer, longueur réellement produite et qualité minimale.
2. **Aligner la charge** : mêmes arrivées et état du cache, puis mesurer côté client.
3. **Décomposer** : TTFT, TPOT/ITL, E2E, outils et file ; vérifier quels tokens sont comptés.
4. **Comparer le goodput** et le coût par tâche réussie, avec erreurs et rejets.
5. **Répéter** en alternant les variantes, puis confirmer en canary.

**Piège** : confondre débit agrégé, vitesse individuelle et expérience complète.

---

Mise en situation : le p99 est excellent à 32 clients, mais les utilisateurs subissent une panne lors d’une campagne. Que manque-t-il au test ? <!--anki:6163656233353161383966613464353038383339306336333532663433363266-->
?
1. **Examiner le modèle d'arrivée** : les 32 clients attendent peut-être les réponses avant de renvoyer du travail.
2. **Rejouer la campagne** avec arrivées indépendantes et rafales représentatives.
3. **Suivre la file et les retards** côté générateur autant que serveur.
4. **Inclure les échecs** et demandes encore en vol à la fin du test.
5. **Tester l'admission et la reprise** après le pic, avec le délai réel d'autoscaling.

**Piège** : extrapoler une capacité de production depuis une concurrence fixe qui réduit automatiquement la demande en surcharge.

---

Mise en situation : une optimisation gagne 4 % de débit sur un seul essai. La déploies-tu ? <!--anki:3539343537343935323031613435353562393233313630356133346637666432-->
?
1. **Vérifier le manifeste** : pas de changement involontaire de cache, prompts, GPU ou génération.
2. **Répéter et alterner** les essais autour de la charge cible.
3. **Quantifier l'incertitude** sur goodput, latences et qualité, par segment critique.
4. **Comparer le gain au coût** de complexité, de mémoire et d'exploitation.
5. **Déployer en canary** seulement si le gain justifie la décision, avec critères de rollback.

**Piège** : transformer une fluctuation ou un cache mieux échauffé en amélioration démontrée.

---

## Sources

- [vLLM — paramètres de bench serve](https://docs.vllm.ai/en/latest/cli/bench/serve/)
- [Grafana k6 — modèles de charge ouverts et fermés](https://grafana.com/docs/k6/latest/using-k6/scenarios/concepts/open-vs-closed/)
- [HdrHistogram — correction de l’omission coordonnée](https://github.com/HdrHistogram/HdrHistogram/blob/master/src/main/java/org/HdrHistogram/AbstractHistogram.java)
- [NVIDIA — GenAI-Perf](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/perf_analyzer/genai-perf/README.html)

## Connexions
- [[64-metriques-slo-inference|Métriques & SLO]] — définir les résultats utiles avant de mesurer
- [[93-monitoring-inference|Monitoring de l’inférence]] — comparer métriques client et moteur
- [[99-statistiques-decisions-experimentales|Statistiques expérimentales]] — incertitude, appariement et décisions
- [[60-011-capacite-ordonnancement-inference|Capacité & ordonnancement]] — relier mémoire, budgets et débit utile sous charge
- [[60-012-demarche-optimisation-inference|Démarche d’optimisation]] — prioriser et vérifier les gains sous contraintes de service
- [[00-moc-ai-engineering|MOC AI Engineering]]
