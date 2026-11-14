# Contrats de prédiction, features & scoring batch — Flashcards
Tags: #flashcards #ai-engineering #mlops #ml-classique #features #batch
Vérifié le : 12 novembre 2026 — les comportements de feature store dépendent de la version et du backend.
<!-- summary: grain et contrat d'une prédiction, validation sémantique, parité entraînement-service, temps de disponibilité, TTL et fraîcheur, valeurs manquantes, schémas nommés, migrations des features, deadlines, indépendance au batch, idempotence, publication complète, validité temporelle des scores, retrait des features, rapprochement des labels, budget de latence et capacité batch, ordre des colonnes, décision et score. -->


Que doit préciser le contrat d'une prédiction avant de concevoir son endpoint ? <!--anki:3532653337623538353362313436646661646637323462333234613839343437-->
?
Définir **unité prédite, population éligible, instant de référence, horizon et sens de la sortie**. Ajouter clés d'entité, unités des entrées, règles de fraîcheur, valeurs manquantes, erreurs et version du contrat.

Exemple : risque de résiliation à trente jours pour un abonnement actif à l'instant de décision, à partir des informations disponibles à cet instant. « Un score par client » reste ambigu si un client possède plusieurs abonnements. Le contrat relie API, batch, entraînement et collecte des labels. Sans cette définition, deux services techniquement compatibles peuvent comparer des scores portant sur des populations ou des horizons différents.

---

Comment séparer validation syntaxique et validation sémantique des entrées d'un modèle ? <!--anki:6661626262646665353533643436623161626230313663356339393763656439-->
?
La validation **syntaxique** contrôle présence, type et forme ; la validation **sémantique** contrôle signification et cohérence : unité, plage plausible, clés, temporalité et combinaisons de champs.

Une somme en centimes peut être un flottant valide mais cent fois trop grande pour un modèle entraîné en euros. Prévoir rejet explicite, quarantaine ou traitement de l'inconnu conformément au contrat, avec compteurs par cause. Ne pas convertir silencieusement toute valeur malformée en valeur manquante. Tester les contrôles avec le prétraitement et le modèle rechargés. Une réponse HTTP réussie démontre seulement que le chemin logiciel s'est exécuté, pas que ses données avaient le sens attendu.

---

Comment vérifier la parité entre features d'entraînement et features servies ? <!--anki:3132333966666236363337623430626261396162323538643765666661393630-->
?
Comparer les valeurs obtenues pour les **mêmes entités aux mêmes instants de référence**, en respectant ce qui était réellement disponible. Contrôler fenêtres, fuseaux, jointures, unités, catégories, valeurs manquantes et arrondis.

Partager le code des transformations réduit les divergences sans supprimer celles des sources ou de leur disponibilité. Conserver des cas de référence et, lorsque permis, des observations représentatives des features effectivement servies ; comparer avec tolérances et explications attendues. Une table historique recalculée avec des corrections ultérieures peut être plus propre que les données vues en ligne. Son accord apparent ne prouve donc pas la fidélité de la reconstitution au moment de la décision.

---

Pourquoi une jointure sur le temps de l'événement peut-elle encore créer une fuite temporelle ? <!--anki:3965653963343633363736663435613561393432623831333332613562356137-->
?
Un événement peut être **daté d'avant la prédiction mais reçu après**. Une jointure fondée seulement sur sa date métier peut l'inclure dans l'entraînement historique alors que le service ne pouvait pas le connaître.

Conserver, si nécessaire, temps d'événement et temps de disponibilité réelle, puis reconstituer l'état accessible à l'instant de décision. Dans un feature store, vérifier les garanties de la jointure historique, de la déduplication et du backend utilisé ; l'étiquette « point-in-time » ne dispense pas d'étudier les arrivées tardives. Un horodatage de création technique n'est utile à cette fin que s'il représente correctement la disponibilité recherchée.

---

À ne pas confondre : TTL historique, expiration du stockage et fraîcheur métier d'une feature ? <!--anki:3739346534373432663232373434356339356638336261313135636664363233-->
?
Un **TTL historique** peut borner l'ancienneté des valeurs recherchées avant un instant de référence ; dans Feast, il limite la fenêtre de recherche de la jointure historique. Une **expiration de stockage** détermine combien de temps un objet demeure accessible. La **fraîcheur métier** dit si une valeur convient encore à une décision donnée.

Ces mécanismes ne sont pas automatiquement équivalents. Vérifier les règles du backend et contrôler l'âge depuis l'horodatage pertinent. Une valeur présente peut être trop ancienne pour l'usage, tandis qu'une valeur absente peut simplement n'avoir jamais existé. Documenter les limites séparément pour entraîner et servir avec des hypothèses compatibles.

---

Comment traiter une feature absente ou périmée sans inventer une observation ? <!--anki:3566366566636662643261373461333362386438353733636261343232333461-->
?
Une absence n'est pas nécessairement **zéro**, et une valeur ancienne n'est pas nécessairement utilisable. Distinguer absence normale, incident de source et dépassement du délai admis.

Appliquer seulement un traitement prévu et testé : imputation apprise, indicateur d'absence, modèle de secours validé ou décision différée. Si le contrat exige la feature, retourner un état explicite plutôt qu'un score ordinaire trompeur. Mesurer fréquence et segments concernés ; vérifier que le mode dégradé reste dans son domaine validé. Une imputation qui passait sur quelques valeurs manquantes à l'entraînement ne garantit pas la qualité lorsque toute une source disparaît en production.

---

Pourquoi les colonnes nommées ne suffisent-elles pas à garantir le contrat d'entrée ? <!--anki:6266643639386132663265353432336138303963343662353761373065643563-->
?
Les noms réduisent les erreurs de position mais ne fixent pas **types, unités, sens et comportement des champs supplémentaires**. Une couche peut convertir un tableau nommé en matrice positionnelle avant l'estimateur.

Tester réordonnancement, colonnes manquantes ou inattendues, changements de type et variantes de catégories avec le paquet publié. Choisir explicitement si un champ supplémentaire est accepté ou refusé. Vérifier que la sélection des colonnes suit le schéma attendu jusqu'au dernier prétraitement. Un test qui appelle seulement le modèle en mémoire avec une matrice déjà correcte ignore les transformations et sérialisations par lesquelles passeront réellement les requêtes.

---

Comment migrer une feature sans rendre le modèle courant ou le rollback inutilisable ? <!--anki:3165303039323837373438333438363862646364663732353163666464353831-->
?
Traiter la migration comme une **compatibilité entre producteurs et consommateurs**. Publier la nouvelle définition avec une identité distincte, préparer son historique et son alimentation, puis vérifier couverture et valeurs avant d'y relier un candidat.

Faire coexister les versions nécessaires pendant la transition et la fenêtre de rollback. Le manifeste du modèle référence la définition attendue ; remplacer une feature derrière un nom inchangé peut modifier tous les consommateurs d'un coup. La livraison coordonne données, modèle et contrat sans supposer une transaction atomique globale. Retirer l'ancienne définition après identification des consommateurs et validation des conditions de reprise, pas dès le premier déploiement réussi.

---

Comment intégrer la récupération des features dans le budget de latence d'une prédiction ? <!--anki:3231356265633531666137373434386162306464373064303330346631623235-->
?
Réserver un **délai global** couvrant file d'attente, récupération des features, prétraitement, modèle et sérialisation. Propager le temps restant aux appels ; un retry ne doit pas réinitialiser le budget.

Paralléliser les sources indépendantes lorsque cela convient, avec bornes de concurrence et comportement prévu pour une réponse partielle. Vérifier fraîcheur et identité des valeurs de secours. Mesurer les distributions de latence de bout en bout sous charge ; additionner des p99 de composants ne donne pas automatiquement le p99 du service. Une inférence de deux millisecondes peut manquer son SLO si la majorité du temps est passée à attendre une feature ou un pool de connexions.

---

Pourquoi tester qu'une prédiction individuelle reste stable quand la composition du batch change ? <!--anki:6365623139383633623861633435396439346261353462623662353137313037-->
?
Pour un modèle **point par point**, les autres lignes ne doivent pas déterminer la transformation d'une observation au moment de prédire. Un scaler réajusté sur chaque batch ou une agrégation involontaire peut faire varier le score selon ses voisins.

Comparer la même ligne seule, avec des cas ordinaires puis extrêmes ; vérifier sorties et décisions avec une tolérance adaptée au runtime. Ne pas appeler `fit` ou `fit_transform` sur les données d'inférence pour « préparer » chaque lot. Certains modèles utilisent volontairement un contexte collectif ; leur contrat doit alors identifier ce groupe et sa construction. Le test dépend de l'indépendance annoncée, pas d'une propriété universelle de tout modèle.

---

Comment rendre un scoring batch idempotent malgré les retries ? <!--anki:6334353238343961333435343464316261353732636135613562363531333937-->
?
Définir une **identité logique** à partir de release, snapshot d'entrée, partition et contrat de calcul. Distinguer cette identité des tentatives d'exécution ; un retry conserve l'intention du même calcul.

Écrire d'abord dans un emplacement temporaire, puis publier de façon contrôlée avec unicité ou déduplication adaptées au stockage. Vérifier cardinalité et contenu avant publication. Une clé construite avec l'heure de chaque tentative transforme chaque retry en nouveau résultat. L'idempotence doit aussi couvrir les consommateurs : recalculer les scores sans doublons ne suffit pas si chaque notification relance une action métier. Préserver provenance et statut des tentatives pour expliquer une reprise.

---

Quand un lot de prédictions peut-il être déclaré publiable ? <!--anki:3063393139363630303633633435333262363636306630393539323932356663-->
?
Après vérification de sa **complétude selon le contrat**, pas seulement après la fin du processus. Comparer population éligible et résultats : clés uniques, partitions attendues, lignes acceptées, rejetées et absentes, sorties valides et release effective.

Un contrat peut autoriser une publication partielle, à condition d'en rendre couverture et limites explicites aux consommateurs. Utiliser un manifeste ou une publication transactionnelle compatible avec le stockage pour éviter qu'un lecteur consomme un lot encore en cours. Conserver compteurs et causes de rejet. Un job vert ayant ignoré une partition vide ou une erreur absorbée peut produire une table propre en apparence mais inutilisable pour la décision prévue.

---

Quels horodatages faut-il conserver avec un score précalculé ? <!--anki:3966666437393630616634633465646638303636363232393639376364643332-->
?
Conserver **instant de référence des informations**, moment du calcul et période d'utilisation autorisée, avec définition de l'horizon. Ces temps répondent à des questions différentes : que savait-on, quand a-t-on calculé, jusqu'à quand le résultat convient-il ?

Ajouter identité de prédiction, entité, release et snapshot ou provenance adaptée. Un recalcul ce matin à partir d'un snapshot ancien n'actualise pas les informations. Le consommateur vérifie la validité pour sa décision et prévoit un comportement si le score est absent ou trop ancien. Une table présente et un job réussi ne prouvent pas que le score décrit encore la population visée aujourd'hui.

---

Pourquoi le retrait d'une feature doit-il suivre les consommateurs réels ? <!--anki:6631383235633961303130393433376662646330303561613534616438376138-->
?
Une feature peut être utilisée par **modèle courant, release de secours, scoring batch et enquête historique**. Supprimer sa source dès qu'un nouveau modèle ne la consomme plus peut rendre le rollback ou une reprise impossible.

Inventorier dépendances déclarées et accès observés, notifier les propriétaires selon le processus prévu et fixer une date de retrait. Vérifier l'alternative et les exigences de conservation ou d'effacement. Un graphe de lineage incomplet peut manquer des consommateurs indirects ; les journaux d'accès complètent sans toujours prouver leur absence. Le retrait doit être une décision explicite avec conditions vérifiées, et non l'effet secondaire d'une optimisation du stockage.

---

Pourquoi rapprocher les labels avec une identité de prédiction plutôt qu'avec le seul identifiant client ? <!--anki:3036353063623539623731363464646638663266313838386561303833356232-->
?
Un client peut recevoir **plusieurs prédictions à des dates et horizons différents**. Une jointure uniquement sur son identifiant peut associer une résiliation future à toutes ses anciennes prédictions ou dupliquer les lignes.

Conserver identité de prédiction, unité, instant de référence, horizon, règle d'éligibilité et version du label. Définir maturation et corrections des issues, puis mesurer taux de rapprochement et délai. Vérifier qu'un label décrit la cible attendue, pas seulement une action opérateur. Une bonne qualité apparente sur les seules lignes rapprochées peut masquer les cas difficiles ou les populations dont les labels arrivent plus tard. Rapporter la couverture avec les métriques.

---

Calcul : trois lectures indépendantes durent 25, 40 et 70 ms, puis le modèle 12 ms et la sérialisation 5 ms. Quel gain apporte leur parallélisation idéale ? <!--anki:6231333261323935663964633432633939393765643530613063306539386533-->
?
Pour ces **durées fixes**, sans attente ni coût de coordination :
```text
séquentiel = 25 + 40 + 70 + 12 + 5 = 152 ms
parallèle  = max(25, 40, 70) + 12 + 5 = 87 ms
gain       = 65 ms ; marge sous 100 ms = 13 ms
```
Ce calcul n'additionne pas des percentiles et ne prédit pas le p99 réel. Files, connexions, CPU et concurrence peuvent absorber la marge. Mesurer sous charge le chemin complet ; vérifier que les lectures sont effectivement indépendantes et que leur parallélisation n'épuise pas une ressource partagée. Un timeout global doit aussi couvrir ces frais. Conserver latence des sources et délai total pour diagnostiquer les attentes réelles.

---

Calcul : il faut scorer 12 millions de lignes en deux heures. Quel débit utile moyen faut-il soutenir ? <!--anki:6466316166633531663961383435646139333631363239663162343865333263-->
?
Deux heures représentent **7 200 secondes** :
```text
12 000 000/7 200 ≈ 1 667 lignes/s
```
C'est un plancher de débit **utile de bout en bout**, après lecture, préparation, calcul, écriture et validation. Si trente minutes sont réservées à ces étapes hors scoring, les 5 400 secondes restantes imposent environ **2 223 lignes/s** pour le scoring seul.

Prévoir marge pour reprises et partitions déséquilibrées, puis mesurer avec les tailles réelles. Multiplier un débit sur petit échantillon par le nombre de workers ignore souvent stockage, mémoire et contention. Préciser si le délai porte sur le dernier calcul ou sur la publication validée du lot consommable.

---

Pourquoi deux tables ayant les mêmes colonnes dans un ordre différent peuvent-elles produire des prédictions incorrectes ? <!--anki:3962623262643264313365613465343838396362643439663438386562646635-->
?
Un pipeline qui convertit les entrées en **matrice positionnelle** peut associer chaque valeur à la mauvaise feature. Les types restent plausibles, donc le modèle peut répondre sans erreur.

Aligner explicitement les noms et valider ordre, type et unité avant conversion. Tester une permutation des colonnes. Les schémas nommés aident seulement si toutes les étapes les respectent ; leur perte dans un tableau intermédiaire doit être contrôlée.

---

Pourquoi versionner la politique de décision séparément du score prédictif ? <!--anki:6363633038306532663630313462366461393830633837373365323633353666-->
?
Un même score peut déclencher **une action différente selon le seuil, les quotas ou les règles métier**. Modifier ces règles change le produit sans modifier les poids.

Conserver version du modèle, score brut, politique et décision effective pour l'audit et le rollback. Évaluer les impacts de capacité, coût et équité. Une bonne métrique prédictive ne prouve pas que la politique qui transforme le score en action est adaptée.

---

## Mises en situation

Mise en situation : les scores changent fortement après une migration de source, mais le schéma et les types sont identiques. Que vérifies-tu ? <!--anki:3830633832373562333731393432363261313862633962636262353234366632-->
?
1. **Comparer les valeurs à entité et instant identiques** : unité, devise, fuseau, fenêtre et catégorie, pas seulement colonnes.
2. **Examiner disponibilité et fraîcheur** : une donnée recalculée ou reçue tard peut avoir changé la reconstitution historique.
3. **Contrôler prétraitement et contrat** du modèle réellement chargé, puis rejouer des cas connus avec les deux sources.
4. **Suspendre ou revenir à une combinaison validée** selon le runbook ; éviter d'entraîner immédiatement sur la nouvelle source.
5. **Versionner la définition corrigée** et ajouter des contrôles sémantiques indépendants.

**Piège** : conclure à une dérive naturelle parce qu'un test de types passe ; un montant en centimes peut remplacer silencieusement des euros.

---

Mise en situation : un batch relancé après timeout double les lignes de scores et les campagnes envoyées. Comment le réparer ? <!--anki:3732313435396561323961373432323839383462303636353039353634373065-->
?
1. **Stopper la consommation** et identifier les tentatives, partitions et actions déjà produites.
2. **Reconstituer le lot logique** avec release et snapshot identiques ; distinguer résultats publiés et écritures temporaires.
3. **Réconcilier les scores** selon une clé métier correcte, avec unicité et contrôle de couverture ; ne pas supprimer arbitrairement toutes les anciennes lignes.
4. **Dédupliquer aussi les effets métier** avec une identité stable d'action ; une correction de table n'annule pas un envoi.
5. **Tester une reprise interrompue** et publier seulement un résultat validé avec son manifeste.

**Piège** : ajouter une clé de tentative unique et appeler cela de l'idempotence : elle autorise précisément un nouveau doublon à chaque relance.

---

Mise en situation : une source de features devient indisponible, mais le service continue à répondre avec des valeurs nulles. Que décides-tu ? <!--anki:3733633232343866333061373433613861616537356161616664326662303963-->
?
1. **Mesurer le périmètre** : source, ancienneté, segments, taux d'absence et version de release.
2. **Vérifier le contrat validé** : absence ponctuelle normale ou panne globale hors du domaine testé ?
3. **Appliquer le mode prévu** : valeurs conservées encore valides, modèle de secours évalué ou décision différée avec statut explicite.
4. **Surveiller charge et qualité disponible** sans présenter l'absence de labels immédiats comme preuve de sûreté.
5. **Rétablir la source et vérifier les valeurs** avant retour progressif ; conserver les identités des décisions affectées.

**Piège** : remplacer tout par zéro pour maintenir le taux de réponses HTTP réussies, puis masquer la dégradation du service rendu.

---

## Sources

- [scikit-learn — prétraitement cohérent et fuite de données](https://scikit-learn.org/stable/common_pitfalls.html) — séparer ajustement et transformation ; tester le paquet complet.
- [Feast — jointures point-in-time](https://docs.feast.dev/getting-started/concepts/point-in-time-joins) — recherche historique et TTL ; vérifier séparément disponibilité et comportement du backend.
- [Google Research — Hidden Technical Debt in Machine Learning Systems](https://research.google/pubs/hidden-technical-debt-in-machine-learning-systems/) — dépendances de données et consommateurs non déclarés.
- [Google SRE — monitoring](https://sre.google/workbook/monitoring/) — observer le service et ses symptômes ; les contrats et calculs présentés sont des exemples de conception.

## Connexions

- [[112-cicd-modeles|CI/CD des modèles]] — vérifier le chemin réel de service
- [[113-monitoring-drift-feedback|Monitoring et feedback]] — couverture et maturité des labels
- [[116-sre-incidents-capacite-ia|SRE des systèmes IA]] — délais, dépendances et modes dégradés
- [[117-pipelines-entrainement-continu|Pipelines d'entraînement]] — compatibilité entre données et modèle
- [[118-artefacts-registre-releases-ml|Artefacts et releases ML]] — décrire la chaîne livrée
- [[157-contrats-qualite-donnees|Contrats de données]] — invariants et validation sémantique
- [[159-donnees-temporelles-features|Données temporelles et features]] — disponibilité historique et feature stores
- [[149-livraison-idempotence-concurrence|Idempotence et concurrence]] — retries et effets métier
- [[00-moc-ai-engineering|MOC AI Engineering]]
