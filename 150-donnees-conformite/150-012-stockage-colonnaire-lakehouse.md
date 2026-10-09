# Stockage colonnaire, partitions & lakehouse — Flashcards
Tags: #flashcards #ai-engineering #donnees #data-engineering
Vérifié le : 9 octobre 2026 — références techniques et exemples de cette fiche.
<!-- summary: warehouse, lake et lakehouse, stockage objet, JSONL/Avro/Parquet/Arrow, row groups, pruning, partitions, petits fichiers, formats de table, transactions, snapshots et suppressions. -->


À ne pas confondre : data warehouse, data lake et lakehouse ? <!--anki:3030646666643563393464653462346261336265636638363463376338646433-->
?
Un **warehouse** organise des données pour les requêtes analytiques et leur exploitation gouvernée. Un **lake** conserve des fichiers de formats variés, souvent sur stockage objet. Une approche **lakehouse** ajoute notamment des métadonnées et garanties de table aux données du lake.

Ces architectures se recouvrent selon les plateformes. Le nom ne garantit ni qualité, ni faible coût, ni transactions couvrant tous les systèmes. Pour l'IA, examiner reproductibilité des datasets, scans, mises à jour, gouvernance et accès des moteurs. Un petit projet peut rester sur une base relationnelle et quelques fichiers versionnés.

---

Comment choisir un stockage selon le mode d’accès d’un système IA ? <!--anki:3663373738663333303333623439343739643862663930666330343933613363-->
?
Partir des **requêtes et garanties attendues**. Des lectures par clé à faible latence, des transactions métier, des scans de milliards de lignes et une recherche de voisins vectoriels demandent des structures différentes.

Une architecture peut combiner stockage objet des sources, tables analytiques des exemples et index spécialisés pour le serving. Définir lequel fait autorité et comment synchroniser les dérivés. Une base vectorielle n'est pas nécessairement le référentiel de documents ou de permissions. Mesurer fraîcheur, cohérence, latence et coût des mises à jour, pas seulement le débit de lecture.

---

Pourquoi un stockage objet ne doit-il pas être traité comme un répertoire transactionnel ? <!--anki:3630353762313535616662303433316362353863316539666438646637646335-->
?
Un stockage objet manipule des **objets identifiés par clé** ; des préfixes ressemblant à des dossiers ne garantissent ni renommage atomique d'un ensemble ni transaction entre fichiers. Ses garanties exactes dépendent du service et des opérations.

Pour publier un dataset cohérent, écrire des objets immuables puis un manifeste ou un commit de table avec une primitive adaptée. Une forte cohérence de lecture d'un objet ne crée pas une transaction multifichier. Garder empreintes, autorisations et stratégie de nettoyage ; des fichiers partiellement publiés ne doivent pas devenir visibles par simple listing.

---

Quand choisir JSONL, Avro ou Parquet pour transporter ou conserver des données ? <!--anki:3066323536333964353739333464356261316533366661653538363834353162-->
?
**JSONL** facilite inspection et échanges ligne par ligne, avec validation de schéma à organiser. **Avro** fournit une sérialisation avec schéma et règles de résolution lecteur/rédacteur, utile notamment aux événements. **Parquet** stocke les colonnes pour favoriser scans sélectifs et compression analytique.

Choisir selon lecteurs, évolution, types et accès. Aucun format ne fournit seul la qualité métier ou une publication transactionnelle de plusieurs fichiers. Des dates, décimaux et valeurs nulles peuvent changer de sens lors des conversions ; tester un aller-retour sur des cas représentatifs avant de généraliser.

---

À ne pas confondre : Apache Arrow et Parquet ? <!--anki:6539306639333663303634313464316662323232623664356536663438626362-->
?
**Arrow** définit notamment une représentation colonnaire en mémoire et des mécanismes d'échange ; **Parquet** est un format de fichiers colonnaires destiné au stockage. On peut lire Parquet dans des structures Arrow avant de transformer les données.

Le transfert sans copie est possible dans certaines conditions de représentation et de compatibilité, pas garanti sur toute la chaîne. Décompression, conversions de types ou passage vers des objets Python peuvent allouer davantage. Estimer la mémoire après décodage : un fichier compressé de 2 Go ne signifie pas un dataset de 2 Go en RAM.

---

Comment les row groups et statistiques Parquet réduisent-ils les lectures ? <!--anki:3031373261633839316630383435373662656333656466396161343637303136-->
?
Un fichier contient des **groupes de lignes**, eux-mêmes organisés en blocs par colonne. Le lecteur peut projeter les colonnes utiles et, lorsque les statistiques et filtres le permettent, éviter des groupes qui ne peuvent pas satisfaire la requête.

Des bornes min/max peu sélectives, des filtres non exploitables ou un lecteur incompatible réduisent ce gain. La taille des groupes échange granularité de filtrage, compression, parallélisme et mémoire. Vérifier les octets réellement lus et le plan ; ajouter un `WHERE` ne prouve pas que les données inutiles ont été évitées au stockage.

---

À ne pas confondre : partitionnement de table et clustering des données ? <!--anki:3662303934643933613532383461363562383262383334363637633031396364-->
?
Le **partitionnement** sépare logiquement les données selon une règle, par exemple le jour, pour écarter des ensembles entiers. Le **clustering** ou tri rapproche des valeurs à l'intérieur d'un ensemble et peut rendre les statistiques de fichiers plus sélectives.

Leur mise en œuvre varie selon le stockage et le moteur ; ils peuvent se compléter. Une requête filtrant les dates profite souvent d'une organisation temporelle, tandis que des filtres clients peuvent bénéficier d'un autre ordre. Choisir selon la charge réelle et le coût d'entretien, sans supposer qu'un index classique existe partout.

---

Pourquoi partitionner un lake par identifiant utilisateur peut-il être une mauvaise idée ? <!--anki:3563653662333435323461343435656438363565376131373636373639363161-->
?
Une clé de **très forte cardinalité** peut créer beaucoup de partitions minuscules et de fichiers, avec coûts de métadonnées, de planification et d'accès. Les utilisateurs peu actifs aggravent ce problème.

Évaluer une partition temporelle, un nombre borné de buckets ou du clustering selon les requêtes. Éviter aussi des partitions trop grosses qui rendent les filtres inutiles. Mesurer distribution des tailles, sélectivité et rythme d'écriture. Une partition est une décision physique ; elle ne remplace ni le filtre de tenant ni le contrôle d'autorisation.

---

Pourquoi les petits fichiers peuvent-ils ralentir un pipeline malgré un faible volume total ? <!--anki:3433366436636633346263343464353361393731326537356234313339623635-->
?
Chaque fichier entraîne des coûts fixes : **ouverture, métadonnées, requêtes au stockage et planification de tâches**. Des millions de petits objets peuvent saturer ces opérations avant de saturer la bande passante.

La compaction regroupe des fichiers pour réduire ce surcoût, en respectant visibilité atomique et lecteurs concurrents. Trop compacter peut diminuer parallélisme et sélectivité ou accroître la mémoire de traitement. Choisir une taille à partir des moteurs et de la charge, puis mesurer temps de planification, octets lus et coût de réécriture. La compaction ne doit pas changer le contenu logique.

---

À ne pas confondre : format de fichier Parquet et format de table Iceberg ? <!--anki:3934663237633862386161363466643438663962343434343237373965363565-->
?
**Parquet** décrit l'organisation d'un fichier. **Iceberg** décrit une table, ses fichiers, snapshots, schémas et métadonnées de partitionnement ; les fichiers de données peuvent être en Parquet.

Le format de table permet notamment une lecture cohérente et une évolution suivie des métadonnées avec un catalogue et des moteurs compatibles. Déposer plusieurs fichiers Parquet dans un dossier ne crée pas ces garanties. Vérifier la compatibilité des fonctionnalités utilisées, notamment suppressions et écritures concurrentes. Le catalogue qui publie l'état de la table fait partie du protocole, pas seulement de la documentation.

---

Quelle frontière vérifier derrière la promesse de transactions ACID d’un lakehouse ? <!--anki:3333393839643435393330613435613461653933393938343365653264303863-->
?
Identifier **l'unité transactionnelle réelle** : souvent une table et son commit, avec garanties définies par moteur, catalogue et opération. Une lecture de snapshot peut être cohérente alors que deux tables ont été mises à jour à des instants différents.

Relier une table d'exemples et une table de labels exige donc une version compatible ou un protocole de publication explicite. Des écritures concurrentes peuvent provoquer conflits et retries, pas seulement s'additionner. Les fichiers, index vectoriels et notifications externes ne deviennent pas automatiquement atomiques avec le commit de la table.

---

Que change une évolution du schéma ou du partitionnement d’une table Iceberg ? <!--anki:3934373662376233643038313435363939653136653763656238663766316266-->
?
Iceberg utilise notamment des **identifiants de champs** pour suivre le schéma, et peut faire coexister plusieurs spécifications de partitionnement. Changer le partitionnement concerne les nouvelles écritures sans réécrire automatiquement tous les anciens fichiers.

Cela facilite l'évolution physique, mais ne convertit pas implicitement le sens métier des valeurs. Renommer une unité sans conversion reste une erreur. Vérifier compatibilité des lecteurs, types autorisés et répartition des fichiers ; prévoir une réécriture si elle est nécessaire aux performances. L'évolution des métadonnées et la migration des contenus sont deux opérations distinctes.

---

Pourquoi le time travel ne garantit-il pas la reproductibilité indéfinie d’un dataset ? <!--anki:3234316635376566313530393462313339633664383431393039626630656532-->
?
Les requêtes historiques dépendent de la **conservation des snapshots et de leurs fichiers**. L'expiration ou un nettoyage peut rendre une ancienne version inaccessible ; une référence enregistrée dans un rapport ne préserve pas les octets.

Aligner rétention, sauvegardes et besoins de reproduction, avec les contraintes d'effacement applicables. Conserver les versions de transformations et des sources externes aussi. Une sauvegarde se valide par restauration, et un historique sur le même stockage ne couvre pas toutes ses pannes. Documenter la durée pendant laquelle chaque expérience reste effectivement reconstructible.

---

Comment une suppression logique diffère-t-elle de l’effacement physique dans une table analytique ? <!--anki:6265383661383361643162653461633039386537636361643636396331306632-->
?
Une suppression peut devenir invisible aux lecteurs via **réécriture de fichiers ou métadonnées de suppression**, selon format et moteur. Les anciennes copies peuvent rester dans des snapshots, caches, exports ou sauvegardes.

Vérifier le chemin de lecture et la maintenance qui retire les données devenues inutiles. Certains lecteurs doivent appliquer des fichiers de suppression ; contourner le format de table peut exposer des lignes retirées. Ne pas annoncer un effacement complet à partir d'un simple `DELETE` réussi. Inventorier les copies et appliquer la politique de conservation et d'accès prévue.

---

Calcul : une table de 900 Gio couvre 30 jours uniformes et 30 colonnes de taille égale. Quel volume idéal lire pour sept jours et trois colonnes, puis quel coût fictif à 5 €/Tio lu ? <!--anki:6133366430376232616236663464333062343230313637323538633533316336-->
?
En supposant élimination parfaite des partitions et projection proportionnelle des colonnes, hors métadonnées et surcoûts :
```text
volume = 900 × 7/30 × 3/30 = 21 Gio
coût = 21/1 024 × 5 ≈ 0,103 €
scan complet = 900/1 024 × 5 ≈ 4,39 €
```
Les colonnes réelles n'ont pas toutes la même taille et les filtres ne sont pas toujours exploitables. Les unités facturées peuvent différer des octets physiques lus. Ce calcul illustre la sélectivité ; vérifier plan, métrique de scan et tarification effective pour une décision réelle.

---

Calcul : 512 Gio sont écrits en fichiers de 1 Mio. Combien de fichiers cela représente-t-il, puis combien après regroupement idéal à 256 Mio, sans changement de volume ? <!--anki:6234616161353562636366313461336539396633666533663134323566393432-->
?
Avec les unités binaires et des fichiers uniformes :
```text
512 × 1 024 / 1 = 524 288 fichiers
512 × 1 024 / 256 = 2 048 fichiers
```
Le nombre de fichiers est divisé par **256**, pas le volume de données. Le gain de durée n'est pas forcément du même facteur : lecture, compression, réseau et écriture restent à payer. La taille de 256 Mio est une hypothèse pédagogique, pas une règle universelle. Conserver suffisamment de parallélisme et vérifier les résultats après publication du nouveau snapshot.

---

## Mises en situation

Mise en situation : une préparation de features de 80 Go met surtout du temps à démarrer et ouvre deux millions de fichiers. Quel diagnostic proposes-tu ? <!--anki:3330353764633634663539633439363661336132323938336534663831643435-->
?
1. **Séparer planification et exécution**, avec nombre et taille des fichiers.
2. **Mesurer les accès aux métadonnées** et la pression sur le stockage objet.
3. **Tester une compaction limitée** sur une partition avec le même contenu logique.
4. **Comparer durée, mémoire, octets lus et parallélisme**, sans supposer un gain proportionnel.
5. **Corriger le rythme d'écriture** pour ne pas recréer immédiatement les petits fichiers.

**Piège** : ajouter des workers alors que le goulot se situe dans la découverte des fichiers.

---

Mise en situation : un entraînement référence un snapshot vieux de trois mois, mais le nettoyage conserve seulement trente jours. Comment rends-tu la politique cohérente ? <!--anki:6263313164346630626434383432633761613635653839303039633762323062-->
?
1. **Inventorier les expériences à reproduire** et les données encore présentes.
2. **Définir un horizon explicite** avec propriétaires, coûts et contraintes de conservation.
3. **Protéger ou archiver les versions nécessaires** selon les capacités du stockage.
4. **Vérifier une reconstruction réelle** avec fichiers, code et dépendances.
5. **Déclarer les versions irrécupérables** et adapter la maintenance future.

**Piège** : conserver seulement un identifiant de snapshot en supposant qu'il protège automatiquement les fichiers.

---

Mise en situation : deux jobs publient chacun une table cohérente, mais le modèle lit des features nouvelles avec des labels anciens. Que manque-t-il ? <!--anki:3233323235343331316664383466343161633536626365653736376336336264-->
?
1. **Identifier les versions incompatibles** et les consommateurs concernés.
2. **Définir un ensemble de publication** qui référence les versions compatibles des deux tables.
3. **Valider cet ensemble avant visibilité**, avec contrôles de clés et de période.
4. **Faire lire les versions explicitement**, au lieu de deux états « latest » indépendants.
5. **Tester interruption et concurrence** pendant la publication.

**Piège** : déduire une transaction multitable de la seule présence d'un format de table transactionnel.

---

## Sources
- [Apache Parquet — structure de fichier](https://parquet.apache.org/docs/file-format/)
- [Apache Parquet — row groups, chunks et pages](https://parquet.apache.org/docs/concepts/)
- [Apache Avro — spécification et résolution des schémas](https://avro.apache.org/docs/1.12.0/specification/)
- [Apache Arrow — format colonnaire](https://arrow.apache.org/docs/format/Columnar.html)
- [Apache Iceberg — fiabilité et concurrence](https://iceberg.apache.org/docs/latest/reliability/)
- [Apache Iceberg — évolution](https://iceberg.apache.org/docs/latest/evolution/)
- [Apache Iceberg — maintenance et expiration](https://iceberg.apache.org/docs/latest/maintenance/)

## Connexions
- [[153-data-flywheel-versioning|Versioning des données]] — préserver les versions physiques nécessaires aux expériences
- [[157-contrats-qualite-donnees|Contrats & qualité]] — publier un état cohérent et lisible
- [[150-011-sql-transformations-analytiques|SQL analytique]] — relier filtres SQL et données réellement lues
- [[150-015-calcul-distribue-performance-donnees|Calcul distribué & performance des pipelines data]] — relier disposition des données et coût d’exécution
- [[00-moc-ai-engineering|MOC AI Engineering]]
