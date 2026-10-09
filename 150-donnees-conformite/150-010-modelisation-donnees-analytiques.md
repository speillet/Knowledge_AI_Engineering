# Modélisation des données analytiques — Flashcards
Tags: #flashcards #ai-engineering #donnees #data-engineering
Vérifié le : 9 octobre 2026 — références techniques et exemples de cette fiche.
<!-- summary: grain, OLTP et OLAP, faits et dimensions, clés, normalisation, cardinalités de jointure, mesures additives, SCD, identité métier et définitions de métriques. -->


Pourquoi définir le grain d’une table avant de construire des variables ML ? <!--anki:3062336464623832353838383439306261643964313533396439623630623261-->
?
Le **grain** précise ce que représente une ligne : événement, ligne de commande, client à une date, ou document dans une version. Il détermine les clés, les jointures et les agrégations valides.

« Une ligne par client » et « une ligne par client et par jour » ne sont pas interchangeables. Mélanger les deux peut répéter un label ou surpondérer les clients actifs. Écrire la règle d'unicité, la population couverte et la temporalité avant les colonnes ; vérifier ensuite ce contrat sur les données produites.

---

À ne pas confondre : stockage OLTP et OLAP pour une application IA ? <!--anki:6665636261656231373233373430313338343466633637346163383539333564-->
?
Un système **OLTP** sert des opérations transactionnelles courtes : créer une commande, lire un compte ou modifier un état avec des garanties de concurrence. Un système **OLAP** privilégie scans, jointures et agrégations sur beaucoup de lignes pour analyser ou préparer un dataset.

Ce sont des profils de charge, pas deux catégories absolument étanches. Une petite base relationnelle peut couvrir les deux. Isoler les extractions lourdes si elles dégradent le service ; une réplique ou une copie analytique introduit aussi du retard à mesurer. Choisir selon accès, cohérence et volume.

---

Comment un schéma en étoile organise-t-il les données analytiques ? <!--anki:6262656638663766353537633432333261353265353231666639326234376463-->
?
Une **table de faits** décrit des événements ou mesures à un grain précis ; les **dimensions** portent les attributs utilisés pour filtrer et regrouper. Une ligne de vente référence par exemple produit, client et date.

Cette organisation rend explicites les jointures et les définitions réutilisables. Elle peut alimenter un dataset ML ou un assistant SQL, sans imposer que toutes les données IA aient ce format. Les documents, graphes et événements imbriqués peuvent conserver d'autres représentations. Contrôler unicité des dimensions et intégrité des références avant d'agréger.

---

À ne pas confondre : clé métier, clé technique et identifiant d’exemple ML ? <!--anki:6537346233616663333137363461626361303231313861643239366132383238-->
?
La **clé métier** désigne une entité dans le domaine ; une **clé technique** identifie une ligne dans un stockage, éventuellement une version historique. L'**identifiant d'exemple** distingue une observation de modèle, par exemple `(client, instant_decision)`.

Un même client peut produire plusieurs exemples et plusieurs versions de dimension. Inclure le périmètre de la source ou du tenant lorsque les identifiants ne sont pas globaux. Un hash évite parfois des clés encombrantes, mais ne résout ni ambiguïté d'identité ni doublons métier. Documenter quelles clés servent au split, aux jointures et au rejeu.

---

Quand normaliser les tables, et quand dénormaliser pour un usage IA ? <!--anki:3566326338316564373061393434343361303637373961306430633437346266-->
?
La **normalisation** limite la duplication et les incohérences de mise à jour ; la **dénormalisation** rapproche des données pour simplifier ou accélérer un accès récurrent. Une table d'exemples ML est souvent dénormalisée à partir de sources plus structurées.

Conserver la provenance et la logique de construction pour pouvoir la reconstruire. Dupliquer une catégorie produit dans chaque exemple peut être utile, mais il faut préciser s'il s'agit de sa valeur historique ou actuelle. Mesurer le coût des jointures face au coût de stockage, de rafraîchissement et d'incohérence.

---

Pourquoi contrôler la cardinalité avant chaque jointure de données ? <!--anki:6139326230373030303334373439633938376338623437343138333730616530-->
?
Une jointure **un-à-plusieurs** peut multiplier les lignes et répéter les mesures du côté « un ». Deux tables contenant plusieurs lignes par clé produisent un produit des correspondances pour chaque clé.

Vérifier le grain des deux côtés, l'unicité attendue et le nombre de lignes avant/après. Pour enrichir une table d'exemples sans changer son grain, agréger ou sélectionner explicitement la bonne version de l'autre table. Un `DISTINCT` final peut cacher le symptôme tout en supprimant des observations valides ou en laissant les sommes déjà faussées.

---

Calcul : une commande de 120 € possède trois lignes et deux paiements. Combien de lignes produit la jointure des trois tables par commande, et que devient la somme du montant de commande ? <!--anki:3661643739323837326235653437323061623066663439363932656566313034-->
?
Avec toutes les correspondances entre lignes et paiements :
```text
lignes obtenues = 3 × 2 = 6
somme naïve du montant de commande = 6 × 120 € = 720 €
```
Le total métier reste **120 €**. Préagréger lignes et paiements au grain commande, ou calculer chaque mesure dans sa table de faits avant de rapprocher les résultats. `SUM(DISTINCT montant)` n'est pas une réparation générale : deux commandes différentes peuvent avoir le même montant. La bonne correction porte sur le grain et les clés, pas sur la valeur répétée.

---

À ne pas confondre : mesure additive, semi-additive et non additive ? <!--anki:3731353934613338643935643436633861386534336664343531373562663436-->
?
Une mesure **additive** se somme sur les dimensions prévues, comme des montants de ventes dans une même devise. Une mesure **semi-additive**, comme un stock instantané, se somme entre entrepôts mais généralement pas entre dates. Une mesure **non additive**, comme un taux, demande un calcul adapté.

Pour agréger des taux de succès, conserver numérateurs et dénominateurs puis les sommer ; une moyenne simple des taux de segments peut être trompeuse. Déclarer dimensions autorisées, unités et population. Même une somme de ventes devient incorrecte avec doubles comptes ou devises mélangées.

---

À ne pas confondre : dimensions à évolution lente SCD type 1 et type 2 ? <!--anki:3437633137353138666338343436623162633364653431633565646630336634-->
?
Le **type 1** remplace une valeur et conserve essentiellement l'état actuel. Le **type 2** ajoute une version de dimension, avec période de validité et identité permettant de rattacher les faits à cette version.

Le choix dépend de la question : analyser les clients selon leur segment actuel, ou selon celui associé à chaque vente. Le type 2 ne reconstitue pas automatiquement les changements jamais collectés. Il ne suffit pas non plus à garantir la disponibilité réelle d'une information lors d'une décision ML ; celle-ci nécessite une temporalité de connaissance explicite.

---

Pourquoi utiliser des intervalles de validité sans chevauchement dans une dimension historique ? <!--anki:3735313132333661323836363436356562336331366331383063663264376631-->
?
Des intervalles comme **[début, fin)** permettent de faire correspondre un instant à au plus une version, si les périodes d'une même entité ne se chevauchent pas. À la frontière, la nouvelle version commence quand l'ancienne cesse de s'appliquer.

Tester les chevauchements, les trous et le nombre de versions courantes. Un `is_current` ne suffit pas pour joindre une vente ancienne. Distinguer aussi validité métier et date de connaissance : corriger aujourd'hui une ancienne période n'autorise pas à utiliser cette correction pour simuler ce que le modèle savait hier.

---

Comment gérer une dimension qui arrive après le fait qui la référence ? <!--anki:3530373933313263316365363433363439386363313736396438663730383232-->
?
Conserver le fait avec un **statut de référence manquante** ou une ligne de dimension provisoire, selon le contrat, puis réconcilier lorsque la dimension arrive. Mesurer ces cas et définir les usages qui doivent attendre.

Une jointure interne supprimerait silencieusement les faits orphelins ; fabriquer une valeur métier arbitraire masquerait le manque. Lors de la réparation, choisir la version temporelle appropriée et recalculer les résultats dépendants. Un membre « inconnu » facilite la publication, mais ne transforme pas une information absente en information fiable pour l'entraînement.

---

Pourquoi l’entity resolution doit-elle être évaluée avant de fusionner des sources pour le ML ? <!--anki:6635636562646163333564653434383562633138643363613361656165333730-->
?
L'**entity resolution** décide si des enregistrements désignent la même entité malgré des identifiants différents. Une fusion abusive mélange des personnes ou produits ; une fusion manquée fragmente leur historique et peut répartir leurs données entre train et test.

Préférer des correspondances fiables lorsqu'elles existent, puis évaluer les rapprochements approximatifs sur des références annotées. Conserver méthode, score, version et possibilité de séparation. Un nom identique n'est pas une clé globale. Adapter les seuils aux conséquences métier et vérifier les erreurs par source et segment.

---

Que doit spécifier une métrique métier réutilisée par des modèles et un assistant SQL ? <!--anki:6263376435353863343934633463646462653461323563353837366338386530-->
?
Définir **population, grain, numérateur, dénominateur, période et exclusions**. « Client actif » peut signifier connexion, achat ou abonnement non résilié ; une requête SQL valide ne tranche pas cette ambiguïté.

Versionner la définition et ses dépendances, avec propriétaire et exemples attendus. Une couche sémantique centralise ces règles, mais doit encore respecter droits d'accès, fraîcheur et disponibilité des dimensions. Tester un petit jeu comprenant remboursements, inconnus et frontières temporelles aide à révéler les divergences avant qu'elles ne deviennent des labels ou des réponses utilisateur.

---

## Mises en situation

Mise en situation : après une jointure avec les tickets de support, les clients qui contactent souvent le support pèsent davantage dans l’entraînement. Comment corriges-tu le dataset ? <!--anki:3332373631356464323164393464633238636130313362353064343965343331-->
?
1. **Énoncer le grain attendu** : une observation par client et instant de décision.
2. **Mesurer la multiplication** des lignes par clé avant et après la jointure.
3. **Agréger les tickets disponibles** à cet instant en variables explicites.
4. **Vérifier l'unicité et les labels**, puis reconstruire les splits selon les entités et le temps.
5. **Comparer les segments** et les scores après correction, sans réutiliser le test pour ajuster la solution.

**Piège** : supprimer arbitrairement les doublons sans comprendre quelle information a été répétée.

---

Mise en situation : un rapport historique change dès qu’un client passe du segment PME au segment grand compte. Comment détermines-tu si c’est un bug ? <!--anki:6161316432656665316465323436313239393866653766623064626432663134-->
?
1. **Clarifier la question métier** : segmentation actuelle ou segmentation à la date des faits.
2. **Inspecter la stratégie de dimension** et l'historique réellement conservé.
3. **Choisir la jointure adaptée**, avec intervalles non chevauchants pour une lecture historique.
4. **Tester un client qui change de segment**, notamment à la frontière de validité.
5. **Versionner la définition du rapport** et annoncer toute rupture de série.

**Piège** : imposer le type 2 à tous les usages sans définir ce que le rapport doit représenter.

---

Mise en situation : deux sources utilisent toutes deux client_id = 42, mais pour des clients différents. Un modèle reçoit leurs historiques mélangés. Que changes-tu ? <!--anki:3433613438613730613334353433363039326464383964616531363231343631-->
?
1. **Contenir la fusion incorrecte** et identifier les datasets et prédictions touchés.
2. **Qualifier les clés** par source ou tenant avant toute jointure.
3. **Construire une table de correspondance** distincte pour les rapprochements intersources autorisés.
4. **Tester collisions et séparations**, puis reconstruire variables, labels et splits concernés.
5. **Ajouter un contrat d'identité** avec propriétaire, règles et contrôles de cardinalité.

**Piège** : changer seulement le type de la colonne ou hasher la valeur `42` sans son périmètre.

---

## Sources
- [Kimball Group — déclarer le grain](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/grain/)
- [Kimball Group — mesures additives et non additives](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/additive-semi-additive-non-additive-fact/)
- [Kimball Group — techniques SCD](https://www.kimballgroup.com/wp-content/uploads/2013/08/2013.09-Kimball-Dimensional-Modeling-Techniques11.pdf)
- [PostgreSQL — jointures et expressions de tables](https://www.postgresql.org/docs/current/queries-table-expressions.html)

## Connexions
- [[157-contrats-qualite-donnees|Contrats & qualité]] — définir grain, clés et sens des mesures
- [[159-donnees-temporelles-features|Données temporelles]] — relier histoire métier et disponibilité pour le modèle
- [[26-text-to-sql|Text-to-SQL]] — rendre explicites les jointures et métriques autorisées
- [[150-011-sql-transformations-analytiques|SQL pour les pipelines et datasets IA]] — préserver le grain et la cardinalité des transformations
- [[00-moc-ai-engineering|MOC AI Engineering]]
