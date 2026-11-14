# Observabilité, lignage & exploitation des données — Flashcards
Tags: #flashcards #ai-engineering #donnees #data-engineering
Vérifié le : 9 octobre 2026 — références techniques et exemples de cette fiche.
<!-- summary: SLO de données, fraîcheur, complétude par segment, réconciliation, couverture des tests, lignage déclaré ou exécuté, catalogue, impact, incidents et coût de surveillance, surveillance de la présence des contrôles, fraîcheur trompeuse, impact des incidents. -->


Comment définir un SLO de données utile à un produit IA ? <!--anki:6338353835303661393538373438626139353234656232346339623536373631-->
?
Définir **consommateur, population, mesure, seuil et période d'observation**. Par exemple : 99 % des partitions quotidiennes attendues validées et disponibles avant 6 h, sur 30 jours glissants, ou part des lectures de features assez fraîches pour la décision.

Compter aussi les partitions absentes et les échecs, pas seulement les sorties reçues. Préciser le statut des périodes sans activité attendue. Un SLO doit déclencher une décision : attente, dernière version valide, abstention ou intervention. Il ne remplace pas les autres dimensions ; des données ponctuelles peuvent rester incomplètes ou fausses.

---

Quels horodatages distinguer pour mesurer la fraîcheur de données servies à un modèle ? <!--anki:3863343263326139346133623435633239363266633138663365646437353334-->
?
Séparer **date de l'événement, arrivée dans le pipeline et disponibilité chez le consommateur**. Selon l'usage, l'âge d'une valeur à la lecture ou le délai événement-à-publication exprime mieux la contrainte que la durée du job.

Une tâche peut finir en une minute après avoir attendu deux heures son export source. De même, le contrôle `freshness` de dbt mesure l'âge du `loaded_at_field` choisi : une date de chargement mesure l'arrivée, pas l'âge des événements. Pour un stock, la dernière valeur connue peut être trop ancienne même si les requêtes fonctionnent. Mesurer distributions et segments, avec le comportement prévu lorsque l'objectif n'est pas respecté.

---

Pourquoi le timestamp maximal d’une table ne suffit-il pas à mesurer sa complétude ? <!--anki:3233643137343761356237363436396361383066633233353134363436396365-->
?
Une seule ligne récente peut faire paraître la table **fraîche** alors qu'une partition, un client ou une source entière manque. Un maximum décrit une extrémité, pas la couverture des données attendues.

Comparer manifestes, clés et volumes attendus par segment, en partant de la liste attendue pour voir les absents :
```sql
SELECT a.client_id FROM clients_attendus a
LEFT JOIN documents d ON d.client_id = a.client_id AND d.jour = DATE '2026-10-21'
GROUP BY a.client_id HAVING count(d.id) = 0;
```
Les volumes habituels sont un signal utile, mais une vraie baisse d'activité peut les modifier. Séparer constat et cause : un contrôle de fraîcheur réussi ne prouve pas que l'ensemble du lot est publiable.

---

À ne pas confondre : test du code d’une transformation et contrôle des données produites ? <!--anki:3466636561343939656662663466313239323462646138623331393734366664-->
?
Un **test de code** vérifie le comportement sur des entrées définies ; un **contrôle de données** examine une exécution réelle ou son résultat : unicité, références, intervalles, taux de nulls ou cohérence métier.

Ils se complètent. Exemple : un test unitaire vérifie que 1 250 centimes deviennent 12,50 € ; il passe encore le jour où la source livre 30 % de montants nuls, que seul un contrôle `not_null` sur la partition détecte. À l'inverse, une contrainte satisfaite peut laisser passer une formule fausse. Classer les contrôles en bloquants, dégradants ou informatifs, avec propriétaire, et mesurer leur couverture plutôt que le nombre de tests verts.

---

Pourquoi deux tables ayant le même nombre de lignes peuvent-elles être désynchronisées ? <!--anki:3930303233646438626133363430626362623232663032343536343634656238-->
?
Une ligne manquante et une ligne supplémentaire peuvent **s'annuler dans le compteur**. Les mêmes identifiants peuvent aussi porter des versions ou valeurs différentes. Le nombre de lignes est donc un premier contrôle, pas une preuve d'équivalence.

Comparer clés, versions, sommes métier et empreintes adaptées, sur un périmètre temporel cohérent. Une différence dans les deux sens localise les écarts :
```sql
(SELECT id, version FROM source EXCEPT SELECT id, version FROM cible)
UNION ALL
(SELECT id, version FROM cible EXCEPT SELECT id, version FROM source);
```
Normaliser types et nulls avant comparaison, puis réparer seulement les objets ou partitions listés.

---

À ne pas confondre : lignage déclaré et lignage observé à l’exécution ? <!--anki:6466646566626237666663383432376462646164313961303464643832613738-->
?
Le **lignage déclaré** décrit les dépendances prévues dans les modèles, requêtes ou configurations. Le **lignage observé** relie une exécution à ses entrées et sorties effectivement utilisées, avec leurs identités et versions disponibles.

Du SQL dynamique, des fichiers lus dans une UDF ou un appel externe peuvent échapper à l'analyse statique. Exemple : le graphe dbt déclare `ref('commandes')`, mais un hook lit aussi `read_parquet('s3://exports/remises/*.parquet')` ; seul le lignage observé voit cette source. Inversement, une instrumentation incomplète peut manquer des événements. Croiser les deux et mesurer la couverture. Un graphe joli mais incomplet ne doit pas être interprété comme une preuve d'absence d'impact sur les consommateurs non représentés.

---

À quoi servent Job, Run et Dataset dans le modèle OpenLineage ? <!--anki:3430623966656261333037353432663238643936313635326665386434386431-->
?
Un **Job** identifie un traitement ; un **Run** une de ses exécutions ; un **Dataset** une entrée ou une sortie. Des événements et facettes ajoutent notamment état, schéma, code et contexte de lecture ou d'écriture.
```json
{"eventType": "COMPLETE", "run": {"runId": "0192f3…"},
 "job": {"namespace": "prod-airflow", "name": "features.build_daily"},
 "inputs":  [{"namespace": "postgres://crm:5432", "name": "public.commandes"}],
 "outputs": [{"namespace": "s3://features", "name": "daily"}]}
```
Cette séparation permet de relier une modification de code à des versions produites lors d'exécutions précises. Elle ne collecte pas automatiquement toutes les métadonnées : les intégrations doivent les émettre correctement. Conserver des identités stables et un namespace évite de fusionner des tables homonymes de deux environnements ou d'attribuer plusieurs identités au même objet.

---

Quand faut-il un lignage de colonne ou d’enregistrement plutôt qu’un simple graphe de tables ? <!--anki:6638393861353738333037313438323939663761636638626234343136323865-->
?
Le lignage de **table** aide à trouver les consommateurs d'une source. Celui de **colonne** précise les champs dépendants d'une transformation. Celui d'**enregistrement** peut retrouver les documents, exemples ou décisions concernés par un objet particulier.

Choisir la granularité selon le diagnostic et les obligations, avec coût et confidentialité. Exemple : pour retirer les données d'un client, le graphe de tables indique que le dataset de fine-tuning dépend de la base support ; seul un lignage d'enregistrement liste les 37 exemples qui en dérivent. Un index RAG demande souvent une correspondance document-vers-chunks, pas une copie de chaque contenu dans les traces. Documenter les zones d'incertitude, comme les jointures dynamiques.

---

Que doit rendre trouvable un catalogue de données pour un AI Engineer ? <!--anki:6134366561633630323963663433363462623930656632623363656239623462-->
?
Pour chaque dataset : **sens, grain, propriétaire, accès, fraîcheur et limites d'usage**, avec schéma, exemples et versions utiles. Le catalogue aide à choisir une source plutôt qu'une table au nom plausible mais obsolète : entre `clients` et `clients_v2`, il indique que la première est figée depuis mars et compte une ligne par client et par pays.

Distinguer responsabilité métier, exploitation technique et consommateurs. Une description ne prouve pas que les contraintes sont contrôlées ; relier les contrats aux mesures et incidents. Vérifier aussi la date de mise à jour de cette documentation. Un catalogue sans propriétaire ni processus de correction peut devenir un inventaire de promesses périmées.

---

Comment estimer l’impact d’une partition de données corrompue sur un système IA ? <!--anki:3738353035646266616234383436636462633564373337646166623563656530-->
?
Suivre **versions et dépendances** vers les tables dérivées, exemples, modèles entraînés, index et caches construits à partir de cette partition. Distinguer les consommateurs qui l'ont réellement utilisée de ceux qui pourraient l'utiliser : un modèle dont la fenêtre d'entraînement s'arrêtait au 1er mars n'a pas lu la partition du 3 mars, même s'il dépend de la même table.

Définir mise en quarantaine, réparation, reconstruction et notification interne selon le risque. Une nouvelle version correcte ne retire pas les prédictions déjà émises. Lorsque le lignage est incomplet, traiter l'impact comme incertain et élargir les vérifications au lieu de conclure à l'absence de dommage.

---

Comment surveiller les données sans exposer leur contenu sensible ni créer des millions de séries ? <!--anki:6464393833643331623965643436333462303831653666313532633763373261-->
?
Publier des **mesures agrégées et des références de diagnostic** : volumes, retard, nulls, violations par source ou segment pertinent. Éviter valeurs libres, identifiants individuels et contenu documentaire dans les labels des métriques : `docs_en_retard{client_id=…}` sur 2 millions de clients crée 2 millions de séries, `{segment=…}` en crée douze.

Limiter les échantillons de données brutes aux outils de diagnostic autorisés, avec rétention et accès appropriés. Une empreinte ou un identifiant peut rester corrélable : il n'est pas automatiquement anonyme. Choisir des agrégations qui permettent de détecter un segment en panne sans recopier tout le dataset dans les logs de monitoring.

---

Calcul : sur 1 440 observations de fraîcheur toutes attendues, sept sont non conformes. Quel taux de conformité et respecte-t-il un objectif de 99,5 % ? <!--anki:3837636137316539386234643461316239363835353135373163303765383438-->
?
Le dénominateur inclut les observations non conformes :
```text
conformité = (1 440 − 7) / 1 440 ≈ 99,514 %
budget = 1 440 × 0,005 = 7,2 observations non conformes
```
Avec ces unités discrètes, sept passent le seuil, huit ne le passent plus. Cela ne signifie pas sept minutes d'indisponibilité si les observations ne représentent pas des minutes équivalentes. Vérifier couverture de la collecte et définition des absences. Un objectif global respecté peut encore cacher un segment systématiquement dégradé.

Pour une décision d'exploitation, conserver les violations individuelles et leur durée. Sept observations consécutives au même moment peuvent demander une réaction différente de sept écarts isolés, malgré un pourcentage final identique.

---

Calcul : un défaut touche indépendamment 1 % des lignes. Sur un échantillon aléatoire de 100 lignes, quelle probabilité de ne détecter aucun défaut ? <!--anki:3061353064323333353066333439303361613332333231643266333666373465-->
?
Sous ces hypothèses :
```text
P(aucun défaut) = (1 − 0,01)^100 ≈ 36,6 %
P(au moins un défaut) ≈ 63,4 %
```
Un échantillon sans erreur n'établit donc pas que le dataset est sain. Des erreurs regroupées par source ou période invalident l'hypothèse d'indépendance et motivent un échantillonnage stratifié ou ciblé. Réserver les contrôles exhaustifs aux invariants qui l'exigent et dont le coût est acceptable ; annoncer la couverture réelle de la validation.

Pour atteindre 95 % de probabilité de détecter au moins un défaut à ce taux indépendant, il faut environ 299 lignes : résoudre `0,99^n ≤ 0,05`. Une erreur plus rare demande un échantillon plus grand.

---

Comment éviter que les contrôles de qualité coûtent plus cher que le pipeline surveillé ? <!--anki:3438623363313839653536653464363439663561623333323438393339323463-->
?
Classer les contrôles selon **criticité, fréquence et volume nécessaire**. Vérifier à chaque publication les invariants essentiels sur les partitions modifiées ; réserver certains scans complets à une cadence justifiée. Exemple : unicité des clés sur la partition du jour, 20 Go, à chaque publication, et sur l'historique de 8 To une fois par semaine.

Réutiliser des statistiques fiables lorsqu'elles répondent réellement à la question, et préciser ce que l'échantillonnage peut manquer. Mesurer coût, durée et erreurs détectées. Une optimisation de contrôle ne doit pas supprimer silencieusement sa garantie, par exemple remplacer une recherche exhaustive de doublons par une estimation sans changer le contrat de publication.

---

Pourquoi un contrôle de fraîcheur doit-il vérifier aussi que sa propre mesure arrive encore ? <!--anki:3830663439336238663338653432363038396330656436633833666432616339-->
?
Une **dernière valeur conforme** peut rester affichée après l'arrêt du pipeline ou du collecteur. Sans surveillance du contrôle, le dashboard peut sembler sain indéfiniment.

Associer mesure et heure d'observation, définir la fréquence attendue et traiter l'absence comme un état explicite. Comparer fraîcheur source, publication et disponibilité au consommateur. Tester interruption du pipeline puis du collecteur. Un timestamp maximal dans les données ne suffit pas si personne ne vérifie régulièrement sa progression et la présence de toutes les partitions attendues.

---

Pourquoi une table mise à jour récemment peut-elle contenir des données métier anciennes ? <!--anki:3162356338623163613965393463636438643433343636303364663065353262-->
?
Un job peut réécrire **les mêmes événements anciens**, donnant un timestamp technique récent sans nouvelle information. Date de modification et fraîcheur métier ne sont pas équivalentes.

Suivre temps des événements, disponibilité et couverture par segment, en plus du dernier succès du pipeline. Tester une source figée avec jobs toujours verts. Une fraîcheur globale peut aussi masquer une partition qui ne reçoit plus de données.

---

Comment le lignage aide-t-il à traiter une erreur découverte dans une source de données ? <!--anki:6362613933663833326130663433383861313239376439653033633566633132-->
?
Il permet d'identifier **les tables, index, features et modèles dérivés** potentiellement touchés. L'analyse doit aussi tenir compte des versions et fenêtres concernées.

Prioriser les consommateurs actifs, suspendre les publications risquées et planifier les recalculs. Vérifier le lignage réellement exécuté : une dépendance non déclarée peut manquer dans le catalogue. Une fois corrigé, réconcilier les résultats et confirmer les consommateurs remis à jour.

---

## Mises en situation

Mise en situation : tous les jobs sont verts et le timestamp maximal est récent, mais les documents d’un client ne sont plus indexés depuis trois jours. Que changes-tu ? <!--anki:6530363436383061373463613432356361323335353835383266323662343162-->
?
1. **Mesurer la couverture par client et partition**, avec une référence des documents attendus.
2. **Tracer le chemin source-à-index** pour localiser la perte ou la quarantaine.
3. **Définir une alerte exploitable** sur fraîcheur et complétude du segment.
4. **Réparer et réconcilier les dérivés**, puis vérifier leur visibilité effective.
5. **Tester une panne limitée à une source** avant de considérer le monitoring suffisant.

**Piège** : ajouter seulement une alerte sur l'heure du dernier succès global.

---

Mise en situation : une unité monétaire incorrecte a alimenté trois entraînements et deux index. Comment conduis-tu la réparation ? <!--anki:6632346262303864623862373436623639646665303035626265326231313430-->
?
1. **Bloquer la propagation** et identifier source, période et versions affectées.
2. **Utiliser le lignage** pour inventorier modèles, datasets, index et caches concernés.
3. **Corriger la conversion et ses contrôles**, puis reconstruire les dérivés nécessaires.
4. **Réévaluer les modèles et les usages**, avec retour à une version valide si adapté.
5. **Documenter les résultats déjà émis** et les limites de l'inventaire d'impact.

**Piège** : corriger seulement la table courante et déclarer l'incident terminé.

---

Mise en situation : une alerte de volume se déclenche chaque week-end alors que la baisse est normale. Comment réduis-tu le bruit sans masquer une panne ? <!--anki:3338333935363038373531343435316538343230383030636136323362363863-->
?
1. **Comparer les périodes comparables** : même jour de semaine, source et segment ; traiter jours fériés et changements de calendrier explicitement.
2. **Vérifier le signal de livraison** : zéro vente déclaré par un manifeste n'est pas un fichier absent.
3. **Adapter le seuil de volume** à une référence saisonnière robuste, avec minimum absolu si pertinent.
4. **Garder les invariants** de schéma, clés et livraison attendue. Un petit volume normal peut encore contenir des données fausses.
5. **Rejouer week-ends normaux et incidents injectés** : absence de fichier, retard, volume anormalement faible ; mesurer faux positifs et défauts manqués avant activation.

**Piège** : supprimer toutes les alertes du week-end ou apprendre automatiquement la nouvelle référence sur une panne prolongée.

---

## Sources
- [OpenLineage — modèle Job, Run et Dataset](https://openlineage.io/docs/spec/object-model/)
- [dbt — contrôles de données](https://docs.getdbt.com/docs/build/data-tests)
- [dbt — critères de fraîcheur](https://docs.getdbt.com/reference/resource-configs/freshness)
- [TensorFlow Data Validation — schémas, anomalies et distributions](https://www.tensorflow.org/tfx/guide/tfdv)

## Connexions
- [[157-contrats-qualite-donnees|Contrats & qualité]] — mesurer les garanties publiées
- [[150-013-orchestration-pipelines-donnees|Orchestration data]] — relier exécution réussie et disponibilité des résultats
- [[111-mlops-llmops-fondamentaux|MLOps]] — tracer les données jusqu’aux versions de modèles
- [[116-sre-incidents-capacite-ia|SRE & incidents]] — réagir aux ruptures de garanties et valider les reprises
- [[150-017-datasets-corpus-ia|Construction de datasets & corpus IA]] — retrouver les sources et consommateurs affectés
- [[00-moc-ai-engineering|MOC AI Engineering]]
