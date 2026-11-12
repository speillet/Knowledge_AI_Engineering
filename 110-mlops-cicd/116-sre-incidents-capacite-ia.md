# SRE : incidents & capacité des services IA — Flashcards
Tags: #flashcards #ai-engineering #mlops #sre #incidents #capacite
<!-- summary: SLI utilisateur, budgets d'erreur, burn rate, alertes multi-fenêtres, files bornées, admission, capacité de secours, propagation des délais, gestion d'incident, rollback, RTO et RPO, postmortem et reprise, calcul du respect des RTO et RPO, dépendance au registre au démarrage, isolation entraînement-service, calcul de résorption du backlog, impact ML après restauration. -->


Pourquoi un statut HTTP 200 ne suffit-il pas comme SLI d'un service IA ? <!--anki:3635323732333063663032383435633261333464373137376137633665346238-->
?
HTTP 200 indique un succès protocolaire, pas nécessairement une **réponse utile et conforme au délai**. Définir événements éligibles, succès et fenêtre au niveau utilisateur.

Exemple : sur 1 000 demandes éligibles, 990 arrivent en HTTP 200, mais 40 de ces réponses sont vides ou hors délai ; le succès de ce contrat est **950/1 000 = 95 %**, pas 99 %. Les catégories doivent être sans double comptage.

Séparer ce SLI de la qualité estimée sur un échantillon annoté, avec couverture et incertitude. Un fallback ne compte comme succès que s'il respecte le contrat produit ; une réponse d'attente n'est pas automatiquement une résolution.

---

Calcul : combien d'échecs autorise un SLO de 99,9 % sur un million de requêtes éligibles ? <!--anki:6230353962613665323066613437376261666466363162653333363966316365-->
?
Le budget vaut **1 000 000 × (1 − 0,999) = 1 000 requêtes en échec**. Avec 700 échecs déjà comptés dans cette fenêtre, il reste 300 événements dans le budget.

Ce SLO repose sur des requêtes, pas directement sur des minutes d'arrêt. Une panne pendant un pic consomme davantage qu'une panne pendant une période creuse. Le trafic futur et le glissement de la fenêtre changent le budget ; une politique doit préciser comment ces évolutions influencent les décisions de livraison.

---

Calcul : quel burn rate pour 2 % d'échecs avec un SLO de 99,9 % ? <!--anki:6335613061333137663963313432633662356334633964353839656338343339-->
?
Le **burn rate** compare le taux d'échec observé au taux autorisé : **0,02 / 0,001 = 20**. À ce rythme constant, avec trafic uniforme et un budget initial complet sur 30 jours, il serait consommé en **30 / 20 = 1,5 jour**.

Ce délai est une projection, pas une prédiction de panne. Il change avec le trafic, les erreurs déjà comptées et la fenêtre retenue. Relier l'alerte à la consommation du budget évite un seuil arbitraire identique pour tous les services.

---

Pourquoi combiner une fenêtre courte et une fenêtre longue dans une alerte de burn rate ? <!--anki:3838633662346539353238363437356562356630306362623561646335666439-->
?
La **fenêtre longue** confirme une consommation significative du budget ; la **fenêtre courte** vérifie que le problème est toujours actif. Exiger les deux peut éviter de réveiller l'astreinte pour un incident déjà terminé.

Des règles complémentaires détectent une panne rapide et une dégradation lente. Adapter les seuils au trafic et au délai d'intervention, puis tester leur comportement sur des incidents connus. Un faible nombre de requêtes rend les ratios instables : le service peut nécessiter des sondes et une stratégie d'alerte spécifique.

---

À ne pas confondre : backpressure et load shedding ? <!--anki:6361656431366339653033393432613262616164643439326638363131303230-->
?
La **backpressure** ralentit ou limite la production de travail en amont lorsque l'aval sature. Le **load shedding** refuse ou abandonne explicitement une partie de la charge pour protéger le service restant.

Une file sans limite ne résout ni l'un ni l'autre : elle peut accumuler des tâches déjà inutiles. Pour un service IA, utiliser des files bornées, quotas de tokens, échéances et priorités. Communiquer les refus et compter leur impact utilisateur ; les masquer dans les statistiques donnerait un SLO artificiellement favorable.

---

Calcul : une file reçoit 30 tâches par seconde et n'en traite que 20 ; combien s'accumulent en deux minutes ? <!--anki:3831313332343830373134633435306538333532623036316236313938393830-->
?
Sous débits constants et sans abandon, la file augmente de **(30 − 20) × 120 = 1 200 tâches**. Si les arrivées s'arrêtent, le serveur mettra encore **60 secondes** à traiter ce stock au même débit.

Si les arrivées restent à 30 par seconde, la file continue de grandir. Ajouter du stockage ne résout pas le déficit de capacité. Il faut augmenter le service, réduire l'admission ou diminuer le travail par tâche, avec des priorités et une limite de délai acceptée par le produit.

---

Pourquoi un fournisseur de secours doit-il être testé sous la charge de bascule ? <!--anki:6531346435636635326466663433376339363634623839333639643936336631-->
?
Un **secours** doit supporter la charge transférée avec les mêmes contrats utiles : identité, formats, outils, délais et données autorisées. Une réponse correcte à un seul appel ne prouve pas cette capacité.

Exercer la bascule avec trafic représentatif, quotas disponibles, cache froid et dépendances communes. Vérifier ce qui reste si DNS, gateway, registre ou système d'identité tombe aussi ; deux fournisseurs ne sont pas indépendants de toute l'application. Prévoir admission et mode dégradé si la capacité de secours est moindre. Après retour, réconcilier les opérations incertaines et observer les signaux utilisateur, sans compter toute réponse de secours comme une réussite.

---

Pourquoi propager une échéance globale aux étapes d'un agent ? <!--anki:3530653465313534336237653439306262633736383030316637353661646634-->
?
Une **échéance de bout en bout** borne le délai encore utile pour l'utilisateur. Chaque étape et retry consomme le reste, au lieu de recevoir à nouveau son timeout maximal.

Si trois étapes ont chacune droit à trente secondes, la tâche peut durer bien plus que le budget produit. Propager le temps restant aux files, outils et fournisseurs qui le permettent ; avant une nouvelle tentative, vérifier qu'elle peut encore servir la décision. Annuler ou réconcilier les travaux en vol selon leurs effets. L'expiration côté client n'arrête pas automatiquement une écriture distante, et une tâche expirée ne doit pas rester facturable sans suivi.

---

Que faire en premier pendant un incident IA affectant les utilisateurs ? <!--anki:6439643935393961326330323463653061346263646630613233663730373239-->
?
**Réduire l'impact et coordonner la réponse** : qualifier la portée, nommer un responsable d'incident, appliquer une mitigation vérifiable et tenir un journal horodaté. Répartir diagnostic technique et communication pour éviter les actions concurrentes incohérentes.

Un rollback, un arrêt des outils d'écriture ou un mode dégradé peut être préférable à une recherche immédiate de la cause complète. Conserver les preuves nécessaires sans diffuser de données sensibles. Le retour à la normale se constate par des signaux utilisateur, pas seulement par un redémarrage réussi.

---

Pourquoi un rollback du modèle ne restaure-t-il pas forcément le service IA ? <!--anki:3764316166643039643232653431386461316636633031323562616331323933-->
?
Le comportement dépend aussi du **prompt, tokenizer, index, schéma d'outil, configuration et données**. Revenir aux seuls poids précédents peut laisser un index incompatible ou une migration irréversible en place.

Versionner l'ensemble utile, documenter les compatibilités et répéter la procédure de retour. Les effets externes déjà réalisés exigent réconciliation ou compensation ; les annuler n'est pas une propriété du rollback logiciel. Vérifier après bascule la qualité, les files en attente et le traitement des tâches démarrées sous l'ancienne configuration.

Exemple : des embeddings de même dimension mais issus d'un autre modèle restent incompatibles. Revenir aux seuls poids du générateur ne répare pas cet index.

---

À ne pas confondre : RTO et RPO pour une application IA ? <!--anki:3439663163353563633762653465313839343835313836623039336634646539-->
?
Le **RTO** est l'objectif de délai de reprise après interruption ; le **RPO** représente la perte de données tolérable exprimée en durée. Reprendre en une heure ne signifie pas retrouver tous les événements jusqu'à la panne.

Définir les objectifs par état : corpus, index reconstructible, checkpoints d'agents et journal d'effets métier. Une sauvegarde n'est utile que si restauration, clés, permissions et dépendances fonctionnent ensemble. Mesurer la reprise réelle lors d'un exercice et documenter les écarts aux objectifs.

Exemple : un RPO de 15 minutes peut autoriser la perte de récents checkpoints, pas nécessairement celle de paiements déjà acceptés. Ces états exigent des objectifs distincts.

---

Calcul : une panne détruit les données des 12 dernières minutes et le service revient après 45 minutes. Respecte-t-on RPO 5 min et RTO 1 h ? <!--anki:6363373462356533313736353436373662663433343535376638356534363561-->
?
Le **RTO** est respecté : le rétablissement prend 45 minutes, sous l'objectif d'une heure. Le **RPO** ne l'est pas : 12 minutes de données perdues dépassent les cinq minutes acceptées.

Préciser quelles données et fonctions sont couvertes : état des agents, opérations métier, preuves et index peuvent avoir des objectifs différents. Un service de nouveau accessible peut encore être incapable de réconcilier ses actions. Tester restauration et cohérence métier, pas seulement redémarrage des processus.

---

Pourquoi une inférence déjà chargée et un démarrage à froid n'ont-ils pas les mêmes dépendances au registre ? <!--anki:3238626562356633316432383463323362396666343938393030333433326133-->
?
Un service ayant **chargé son modèle** peut continuer à prédire pendant une panne du registre, si son contrat ne requiert pas de résolution distante à chaque appel. Un nouveau réplica peut rester bloqué faute de métadonnées ou d'artefacts.

Tester ces deux états : service stable, redémarrage, scale-out et restauration. Prévoir références épinglées, cache contrôlé et règles de validité ; ne pas contourner une révocation ou servir un artefact non vérifié pour gagner en disponibilité. Une API de prédiction saine ne prouve pas que la capacité peut être reconstruite après la perte des processus déjà chauds.

---

Pourquoi isoler les ressources d'entraînement et d'inférence même si elles utilisent le même modèle ? <!--anki:3831376531326636343762373432333039306333316461353432343866626331-->
?
L'**entraînement** peut saturer GPU, CPU, réseau et stockage pendant des heures ; l'inférence doit respecter un délai utilisateur. Partager sans quota peut faire d'un réentraînement normal un incident de production.

Définir pools, priorités ou enveloppes de ressources, puis tester les pics simultanés. Inclure téléchargement des données, checkpoints et lecture des poids, qui sollicitent parfois des dépendances communes malgré des GPU séparés. Le partage peut rester rentable avec admission et préemption adaptées, mais le modèle identique ne rend pas leurs profils de charge interchangeables. Relier planification du réentraînement, SLO et coût de la capacité de réserve.

---

Calcul : après une panne, 9 000 tâches attendent ; 20 nouvelles arrivent par seconde et le service en termine 30/s. Quel temps idéal pour résorber la file ? <!--anki:6530633837383164306337393462383161353736396132373165616466376537-->
?
La **capacité nette de rattrapage** vaut `30 − 20 = 10 tâches/s`. Le retard demande donc `9 000/10 = 900 s`, soit **15 minutes**, sous ces hypothèses.

Diviser par 30 oublierait les nouvelles arrivées. Si service et arrivées s'égalisent, le retard ne diminue pas ; si les arrivées dominent, il grossit. Le calcul suppose tâches comparables, débits constants et aucune expiration ni reprise. Examiner aussi âge des éléments, délais utiles et classes de priorité : retrouver un débit normal ne signifie pas que toutes les demandes anciennes peuvent encore produire un résultat valable.

---

À ne pas confondre : rétablissement technique et fin d'analyse d'impact d'un incident ML ? <!--anki:3437366430366262333834333433356362326232336537386465653239343336-->
?
Le **rétablissement technique** remet le service dans son contrat opérationnel. L'**analyse d'impact** identifie les décisions, personnes et systèmes affectés pendant la dégradation, puis les corrections nécessaires.

Un modèle de nouveau disponible peut avoir laissé des scores faux dans une table batch ou des actions déjà exécutées. Utiliser versions, périodes, identifiants de décisions et journaux pour délimiter ce périmètre. Prévoir recalcul, réconciliation ou traitement métier approprié, avec responsables distincts si nécessaire. Clore l'alerte de disponibilité ne clôt pas automatiquement ces actions ; conserver le suivi et vérifier qu'une remise en service ne propage pas de nouveau les résultats corrompus.

---

## Mises en situation

Mise en situation : le GPU semble peu chargé, mais les utilisateurs attendent 45 secondes et la file grossit. Comment réagis-tu ? <!--anki:3661656463396430323033363436623439663335636166393363623563623464-->
?
1. **Décomposer la latence** : attente, retrieval, fournisseur, génération et outils.
2. **Comparer arrivées et service**, avec âge des tâches et distribution des tokens.
3. **Borner l'admission** et retirer les tâches expirées selon leur contrat métier.
4. **Isoler le goulot** : quota externe, CPU, réseau ou blocage applicatif.
5. **Vérifier la récupération** au niveau utilisateur et la vidange de la file.

**Piège** : ajouter des GPU alors que le débit est limité ailleurs.

---

Mise en situation : après une panne, le modèle de secours répond, mais exécute mal les appels d'outils. Que fais-tu ? <!--anki:3834643766356132383231313433653839643334663333356137613434323434-->
?
1. **Suspendre les effets risqués** et proposer un service dégradé explicite.
2. **Identifier les tâches touchées** grâce aux versions et journaux d'exécution.
3. **Vérifier les actions déjà engagées**, avant toute relance.
4. **Revenir à une configuration validée** ou limiter le secours à la lecture.
5. **Ajouter une eval de compatibilité** des outils et un exercice de bascule avant réactivation.

**Piège** : compter HTTP 200 comme rétablissement alors que le résultat métier est incorrect.

---

Mise en situation : le même incident de saturation revient chaque mois malgré des postmortems. Que changes-tu ? <!--anki:3032663335626632636236343436366139303663653862643334393962353663-->
?
1. **Revoir les facteurs techniques et organisationnels**, sans réduire l'analyse à une erreur humaine.
2. **Choisir des actions vérifiables** : admission bornée, alerte ou suppression d'une dépendance fragile.
3. **Attribuer responsable et échéance** à chaque action prioritaire.
4. **Rejouer le scénario de panne** pour vérifier que l'action réduit l'impact.
5. **Suivre l'exécution du plan** et arbitrer le travail de fiabilité avec le produit.

**Piège** : clore le postmortem dès que le document est écrit, sans vérifier les corrections.

---

## Sources
- [Google SRE — définir et mettre en œuvre les SLO](https://sre.google/workbook/implementing-slos/)
- [Google SRE — alertes fondées sur les SLO](https://sre.google/workbook/alerting-on-slos/)
- [Google SRE — politique de budget d'erreur](https://sre.google/workbook/error-budget-policy/)
- [Google SRE — gérer la surcharge](https://sre.google/sre-book/handling-overload/)
- [Google SRE — gérer les incidents](https://sre.google/sre-book/managing-incidents/)
- [Google SRE — postmortems et actions correctives](https://sre.google/sre-book/postmortem-culture/)

- [AWS Well-Architected — objectifs et tests de reprise](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/plan-for-disaster-recovery-dr.html)

- [MLflow — métadonnées, artefacts et serveur de tracking](https://mlflow.org/docs/latest/self-hosting/architecture/overview/) — distinguer dépendance de démarrage et service déjà chargé.

## Connexions
- [[142-fiabilite-resilience-llm|Fiabilité & résilience]] — passer des mécanismes à leur exploitation
- [[64-metriques-slo-inference|Métriques & SLO]] — relier capacité et expérience utilisateur
- [[112-cicd-modeles|CI/CD des modèles]] — rollback et compatibilité des artefacts
- [[147-leadership-technique-ia|Leadership technique]] — responsabilités et suivi des corrections
- [[60-011-capacite-ordonnancement-inference|Capacité & ordonnancement]] — relier mémoire, budgets et débit utile sous charge
- [[150-016-observabilite-lignage-donnees|Observabilité, lignage & exploitation des données]] — réagir aux ruptures de garanties et valider les reprises
- [[118-artefacts-registre-releases-ml|Artefacts, registre et releases ML]] — contrats et vérifications de production
- [[119-contrats-prediction-features-batch|Contrats de prédiction, features et batch]] — contrats et vérifications de production
- [[00-moc-ai-engineering|MOC AI Engineering]]
