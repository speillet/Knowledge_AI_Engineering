# Observabilité, lignage & exploitation des données — Flashcards
Tags: #flashcards #ai-engineering #donnees #data-engineering
Vérifié le : 9 octobre 2026 — références techniques et exemples de cette fiche.
<!-- summary: SLO de données, fraîcheur, complétude par segment, réconciliation, couverture des tests, lignage déclaré ou exécuté, catalogue, impact, incidents et coût de surveillance. -->


Comment définir un SLO de données utile à un produit IA ? <!--anki:6338353835303661393538373438626139353234656232346339623536373631-->
?
Définir **consommateur, population, mesure, seuil et période d'observation**. Par exemple : part des partitions quotidiennes attendues, validées et disponibles avant une heure donnée, ou part des lectures de features assez fraîches pour la décision.

Compter aussi les partitions absentes et les échecs, pas seulement les sorties reçues. Préciser le statut des périodes sans activité attendue. Un SLO doit déclencher une décision : attente, dernière version valide, abstention ou intervention. Il ne remplace pas les autres dimensions ; des données ponctuelles peuvent rester incomplètes ou fausses.

---

Quels horodatages distinguer pour mesurer la fraîcheur de données servies à un modèle ? <!--anki:3863343263326139346133623435633239363266633138663365646437353334-->
?
Séparer **date de l'événement, arrivée dans le pipeline et disponibilité chez le consommateur**. Selon l'usage, l'âge d'une valeur à la lecture ou le délai événement-à-publication exprime mieux la contrainte que la durée du job.

Une tâche peut finir en une minute après avoir attendu deux heures son export source. Documenter horloges, fuseaux et événements sans timestamp fiable. Pour un stock, la dernière valeur connue peut être trop ancienne même si les requêtes fonctionnent. Mesurer distributions et segments, avec le comportement prévu lorsque l'objectif n'est pas respecté.

---

Pourquoi le timestamp maximal d’une table ne suffit-il pas à mesurer sa complétude ? <!--anki:3233643137343761356237363436396361383066633233353134363436396365-->
?
Une seule ligne récente peut faire paraître la table **fraîche** alors qu'une partition, un client ou une source entière manque. Un maximum décrit une extrémité, pas la couverture des données attendues.

Comparer manifestes, clés et volumes attendus par segment ; compléter par âge des éléments en retard et statut des partitions. Les volumes habituels sont un signal utile, mais une vraie baisse d'activité peut les modifier. Séparer constat et cause : un contrôle de fraîcheur réussi ne prouve pas que l'ensemble du lot est publiable.

---

À ne pas confondre : test du code d’une transformation et contrôle des données produites ? <!--anki:3466636561343939656662663466313239323462646138623331393734366664-->
?
Un **test de code** vérifie le comportement sur des entrées définies ; un **contrôle de données** examine une exécution réelle ou son résultat : unicité, références, intervalles, taux de nulls ou cohérence métier.

Ils se complètent. Un transformateur correct peut recevoir une source incomplète, et une contrainte satisfaite peut laisser passer une formule fausse. Classer les contrôles en bloquants, dégradants ou informatifs, avec propriétaire. Prévoir des exemples qui doivent échouer et mesurer la couverture des contrôles, au lieu de compter seulement le nombre de tests verts.

---

Pourquoi deux tables ayant le même nombre de lignes peuvent-elles être désynchronisées ? <!--anki:3930303233646438626133363430626362623232663032343536343634656238-->
?
Une ligne manquante et une ligne supplémentaire peuvent **s'annuler dans le compteur**. Les mêmes identifiants peuvent aussi porter des versions ou valeurs différentes. Le nombre de lignes est donc un premier contrôle, pas une preuve d'équivalence.

Comparer clés, versions, sommes métier et empreintes adaptées, sur un périmètre temporel cohérent. Normaliser types et nulls avant comparaison ; un hash nécessite une sérialisation canonique et conserve un risque de collision. Les différences doivent être localisables pour réparer seulement les partitions ou objets concernés lorsque c'est possible.

---

À ne pas confondre : lignage déclaré et lignage observé à l’exécution ? <!--anki:6466646566626237666663383432376462646164313961303464643832613738-->
?
Le **lignage déclaré** décrit les dépendances prévues dans les modèles, requêtes ou configurations. Le **lignage observé** relie une exécution à ses entrées et sorties effectivement utilisées, avec leurs identités et versions disponibles.

Du SQL dynamique, des fichiers lus dans une UDF ou un appel externe peuvent échapper à l'analyse statique. Inversement, une instrumentation incomplète peut manquer des événements. Croiser les deux et mesurer la couverture. Un graphe joli mais incomplet ne doit pas être interprété comme une preuve d'absence d'impact sur les consommateurs non représentés.

---

À quoi servent Job, Run et Dataset dans le modèle OpenLineage ? <!--anki:3430623966656261333037353432663238643936313635326665386434386431-->
?
Un **Job** identifie un traitement ; un **Run** une de ses exécutions ; un **Dataset** une entrée ou une sortie. Des événements et facettes ajoutent notamment état, schéma, code et contexte de lecture ou d'écriture.

Cette séparation permet de relier une modification de code à des versions produites lors d'exécutions précises. Elle ne collecte pas automatiquement toutes les métadonnées : les intégrations doivent les émettre correctement. Conserver des identités stables et un namespace évite de fusionner des tables homonymes de deux environnements ou d'attribuer plusieurs identités au même objet.

---

Quand faut-il un lignage de colonne ou d’enregistrement plutôt qu’un simple graphe de tables ? <!--anki:6638393861353738333037313438323939663761636638626234343136323865-->
?
Le lignage de **table** aide à trouver les consommateurs d'une source. Celui de **colonne** précise les champs dépendants d'une transformation. Celui d'**enregistrement** peut retrouver les documents, exemples ou décisions concernés par un objet particulier.

Choisir la granularité selon le diagnostic et les obligations opérationnelles, avec coût et confidentialité. Un index RAG demande souvent une correspondance document-vers-chunks, pas une copie de chaque contenu dans les traces. Le lignage d'une jointure dynamique peut être plus difficile à obtenir ; documenter ses zones d'incertitude.

---

Que doit rendre trouvable un catalogue de données pour un AI Engineer ? <!--anki:6134366561633630323963663433363462623930656632623363656239623462-->
?
Pour chaque dataset : **sens, grain, propriétaire, accès, fraîcheur et limites d'usage**, avec schéma, exemples et versions utiles. Le catalogue aide à choisir une source plutôt qu'une table au nom plausible mais obsolète.

Distinguer responsabilité métier, exploitation technique et consommateurs. Une description ne prouve pas que les contraintes sont contrôlées ; relier les contrats aux mesures et incidents. Vérifier aussi la date de mise à jour de cette documentation. Un catalogue sans propriétaire ni processus de correction peut devenir un inventaire de promesses périmées.

---

Comment estimer l’impact d’une partition de données corrompue sur un système IA ? <!--anki:3738353035646266616234383436636462633564373337646166623563656530-->
?
Suivre **versions et dépendances** vers les tables dérivées, exemples, modèles entraînés, index et caches construits à partir de cette partition. Distinguer les consommateurs qui l'ont réellement utilisée de ceux qui pourraient l'utiliser.

Définir mise en quarantaine, réparation, reconstruction et notification interne selon le risque. Une nouvelle version correcte ne retire pas les prédictions déjà émises. Conserver les références nécessaires aux investigations, avec accès limité. Lorsque le lignage est incomplet, traiter l'impact comme incertain et élargir les vérifications au lieu de conclure à l'absence de dommage.

---

Comment surveiller les données sans exposer leur contenu sensible ni créer des millions de séries ? <!--anki:6464393833643331623965643436333462303831653666313532633763373261-->
?
Publier des **mesures agrégées et des références de diagnostic** : volumes, retard, nulls, violations par source ou segment pertinent. Éviter valeurs libres, identifiants individuels et contenu documentaire dans les labels des métriques.

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

---

Calcul : un défaut touche indépendamment 1 % des lignes. Sur un échantillon aléatoire de 100 lignes, quelle probabilité de ne détecter aucun défaut ? <!--anki:3061353064323333353066333439303361613332333231643266333666373465-->
?
Sous ces hypothèses :
```text
P(aucun défaut) = (1 − 0,01)^100 ≈ 36,6 %
P(au moins un défaut) ≈ 63,4 %
```
Un échantillon sans erreur n'établit donc pas que le dataset est sain. Des erreurs regroupées par source ou période invalident l'hypothèse d'indépendance et motivent un échantillonnage stratifié ou ciblé. Réserver les contrôles exhaustifs aux invariants qui l'exigent et dont le coût est acceptable ; annoncer la couverture réelle de la validation.

---

Comment éviter que les contrôles de qualité coûtent plus cher que le pipeline surveillé ? <!--anki:3438623363313839653536653464363439663561623333323438393339323463-->
?
Classer les contrôles selon **criticité, fréquence et volume nécessaire**. Vérifier à chaque publication les invariants essentiels sur les partitions modifiées ; réserver certains scans complets ou comparaisons lourdes à une cadence justifiée.

Réutiliser des statistiques fiables lorsqu'elles répondent réellement à la question, et préciser ce que l'échantillonnage peut manquer. Mesurer coût, durée et erreurs détectées. Une optimisation de contrôle ne doit pas supprimer silencieusement sa garantie, par exemple remplacer une recherche exhaustive de doublons par une estimation sans changer le contrat de publication.

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
1. **Comparer la saisonnalité attendue** par source et segment.
2. **Séparer absence légitime et livraison manquante**, grâce aux manifestes ou calendriers.
3. **Ajuster la référence de volume** avec périodes comparables et seuils utiles.
4. **Conserver les contrôles invariants**, notamment clés, contrats et fraîcheur requise.
5. **Rejouer des incidents connus** pour vérifier qu'ils restent détectés.

**Piège** : désactiver les alertes du week-end sans prévoir les traitements réellement attendus.

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
