# SQL pour les pipelines et datasets IA — Flashcards
Tags: #flashcards #ai-engineering #donnees #data-engineering
Vérifié le : 9 octobre 2026 — références techniques et exemples de cette fiche.
<!-- summary: jointures et filtres, NULL, agrégations, fenêtres, déduplication déterministe, anti-jointures, CTE, SQL temporel, plans de requête et contrôles de transformations. -->


Dans quel ordre logique raisonner sur une requête SQL analytique ? <!--anki:3638393465633964663639633434613639363865613739346437383030623434-->
?
Raisonner sur **FROM et JOIN**, puis `WHERE`, agrégations et `HAVING`, puis fenêtres et projection, enfin tri et limitation. Cet ordre conceptuel explique quelles lignes et colonnes sont disponibles à chaque étape ; l'optimiseur peut employer un autre ordre physique équivalent.

Un filtre `WHERE` retire des lignes avant une moyenne ; `HAVING` filtre des groupes après agrégation. Une fonction de fenêtre ne voit donc pas les lignes déjà exclues. Décomposer la requête en étapes aide à comprendre pourquoi un dataset perd des observations ou change de dénominateur.

---

Pourquoi un filtre WHERE sur la table droite peut-il changer le sens d’un LEFT JOIN ? <!--anki:3264633139653733613066663461666639323533666230303465336132353434-->
?
Les lignes sans correspondance reçoivent des `NULL` à droite. Un filtre comme `WHERE t.statut = 'ouvert'` les exclut, car cette comparaison n'est pas vraie pour `NULL`.
```sql
SELECT c.id, t.id AS ticket_id
FROM clients c
LEFT JOIN tickets t
  ON t.client_id = c.id AND t.statut = 'ouvert';
```
Placer ce critère dans `ON` conserve ici les clients sans ticket ouvert. Cela ne garantit pas une ligne par client : plusieurs tickets ouverts créent plusieurs correspondances. Choisir ensuite une agrégation ou une sélection cohérente avec le grain souhaité.

---

Pourquoi comparer une colonne SQL à NULL avec = ne teste-t-il pas son absence ? <!--anki:3032646563643533396361643461633238393565326466343464363936373637-->
?
SQL utilise une **logique à trois valeurs** : vrai, faux et inconnu. Une comparaison ordinaire avec `NULL` produit généralement inconnu ; `WHERE` ne garde que les lignes dont la condition est vraie. Utiliser `IS NULL` ou `IS NOT NULL` pour tester l'absence.

`COALESCE(x, 0)` remplace une absence par zéro, mais change le sens des données. Le faire uniquement si le contrat l'autorise. Pour des comparaisons qui doivent traiter deux valeurs nulles comme égales, vérifier les opérateurs disponibles dans le dialecte et la sémantique métier recherchée.

---

Calcul : une colonne SQL contient 10, 20 et NULL. Que donnent COUNT(*), COUNT(valeur), SUM(valeur) et AVG(valeur) ? <!--anki:3363646132636532666232373465326362393333613866303132323732306530-->
?
Les agrégats usuels ignorent les valeurs nulles, tandis que `COUNT(*)` compte les lignes :
```text
COUNT(*) = 3 ; COUNT(valeur) = 2
SUM(valeur) = 30 ; AVG(valeur) = 30 / 2 = 15
```
Après remplacement de `NULL` par zéro, la moyenne devient **10** : la population du dénominateur a changé. Sur un ensemble vide, `COUNT` vaut zéro mais `SUM` et `AVG` valent généralement `NULL`. Publier taux de valeurs manquantes et convention de calcul évite de confondre amélioration métier et disparition de données.

---

À ne pas confondre : GROUP BY et fonction de fenêtre SQL ? <!--anki:6564333466356132356539313430306161646332356562363132346532646539-->
?
`GROUP BY` produit une ligne par groupe. Une fonction avec **OVER** calcule sur un ensemble de lignes apparentées tout en conservant les lignes d'entrée de cette étape.

Pour attacher à chaque vente le total de son client, une somme fenêtrée peut convenir ; pour construire une ligne par client, une agrégation est adaptée. Conserver les lignes ne signifie pas conserver leur grain d'origine si une jointure les a déjà multipliées. Vérifier partition, tri et cadre de fenêtre avant d'utiliser le résultat comme variable ML.

---

Comment sélectionner une version par identifiant avec ROW_NUMBER de façon déterministe ? <!--anki:6466356164643736363133303434343562306131343137363238326537643033-->
?
Définir un **ordre total** cohérent avec les versions source, puis filtrer après la fenêtre. Ici `version` est non nulle et `event_id` départage les égalités de façon stable :
```sql
WITH ranked AS (
  SELECT id, valeur, ROW_NUMBER() OVER (
    PARTITION BY id ORDER BY version DESC, event_id DESC
  ) AS rn
  FROM changements
)
SELECT id, valeur FROM ranked WHERE rn = 1;
```
Un timestamp seul peut laisser des ex æquo. Un départage stable garantit la reproductibilité, pas la vérité métier : des événements contradictoires à la même version doivent aussi être détectés.

---

À ne pas confondre : cadre ROWS et cadre RANGE dans une fenêtre SQL ? <!--anki:3931653737313039383438393439353861626639663739373237303066636532-->
?
**ROWS** délimite le cadre par positions dans l'ordre des lignes ; **RANGE** le définit selon les valeurs de tri et inclut les pairs selon ses bornes. Des timestamps égaux peuvent donc recevoir le même cumul avec RANGE, mais des cumuls successifs avec ROWS.

Déclarer le cadre et un ordre suffisamment précis lorsque cela compte. `ROWS BETWEEN 6 PRECEDING AND CURRENT ROW` désigne jusqu'à sept lignes, pas sept jours. Les syntaxes d'intervalles et valeurs par défaut varient selon le moteur ; tester doublons de dates et jours absents.

---

Comment rechercher les objets absents d’une destination sans le piège de NOT IN avec NULL ? <!--anki:6539303461613535613864663437373861316433346263623961373630393133-->
?
Une **anti-jointure avec NOT EXISTS** exprime directement l'absence de correspondance. Pour des identifiants non nuls :
```sql
SELECT s.id
FROM source s
WHERE NOT EXISTS (
  SELECT 1 FROM destination d WHERE d.id = s.id
);
```
Avec `NOT IN`, un `NULL` parmi les valeurs comparées peut rendre la condition inconnue pour des objets pourtant absents. `NOT EXISTS` ne règle pas l'identité des clés nulles : décider si elles sont invalides ou comparables. Réconcilier aussi versions et contenus, car la présence d'un identifiant ne prouve pas sa fraîcheur.

---

Pourquoi UNION ALL et UNION ne sont-ils pas interchangeables dans un pipeline de données ? <!--anki:6338343164646530636638343432336361376461353464393761323263343665-->
?
**UNION ALL** conserve toutes les lignes ; **UNION** élimine les doublons sur l'ensemble des colonnes projetées. Deux événements métier distincts peuvent avoir les mêmes valeurs visibles et être fusionnés à tort par UNION.

À l'inverse, UNION ALL conserve aussi les relivraisons si aucune déduplication explicite ne suit. Choisir une identité d'événement et une règle de version plutôt qu'une suppression implicite fondée sur les colonnes affichées. La déduplication peut en outre demander tri ou échange réseau : son coût et son effet sémantique doivent être voulus.

---

Pourquoi un CTE SQL améliore-t-il la lecture sans garantir une matérialisation ? <!--anki:3965643134643065383139653461313762626137623263633262383039376162-->
?
Un **CTE**, introduit par `WITH`, nomme une sous-requête et rend visibles les étapes d'une transformation. Selon le moteur et la requête, il peut être intégré au plan ou matérialisé ; le mot-clé seul ne garantit ni cache ni calcul unique.

Employer des CTE pour isoler grain, filtrage et agrégation, puis inspecter le plan pour les performances. Si une étape doit être persistée, réutilisée ou auditée comme un dataset, choisir une matérialisation explicite et sa politique de rafraîchissement. La lisibilité et le coût d'exécution sont deux critères distincts.

---

Comment vérifier une jointure temporelle SQL avant de produire des exemples ML ? <!--anki:6462373436646230616163613433653262306563336562643761666466623861-->
?
Pour chaque décision, filtrer les versions **valides et effectivement disponibles** à cet instant, puis sélectionner celle que le service aurait utilisée. Une condition portant seulement sur la date métier ne suffit pas si les informations arrivent tard.

Construire un petit jeu où une correction ancienne arrive après la décision, où deux versions se touchent et où aucune valeur n'est disponible. Vérifier au plus une ligne par exemple et une politique explicite de valeur périmée. Comparer aux données réellement servies lorsque possible ; un `MAX(timestamp)` global n'exprime pas cette jointure.

---

Que vérifier avant un MERGE ou un upsert dans une transformation incrémentale ? <!--anki:6539303464363062376436653432653162386532623539663739396166613936-->
?
Définir **clé de correspondance, unicité, ordre des versions et traitement des suppressions**. Plusieurs lignes source pour une même cible peuvent provoquer erreur ou résultat dépendant du moteur ; les clés nulles et événements désordonnés demandent une politique explicite.

Préparer la source au grain attendu, puis appliquer une écriture cohérente avec la version. Tester création, mise à jour, doublon, ancien événement et suppression. Une opération nommée MERGE ne garantit pas l'idempotence de toute la chaîne, notamment si une extraction a déjà omis des changements ou si des effets externes suivent.

---

Quel risque crée l’expansion d’un tableau JSON en lignes dans un dataset IA ? <!--anki:3837303763376465313036343436663561613030633130636664373139336163-->
?
Une opération d'**expansion**, souvent appelée `UNNEST` ou `explode`, change le grain : un document avec cinq éléments peut produire cinq lignes. Les attributs du document sont alors répétés, ce qui peut multiplier labels, montants ou poids d'échantillonnage.

Définir l'identité de chaque élément, l'ordre éventuel et le traitement des listes vides ou nulles. Certains modes les suppriment, d'autres conservent une ligne vide. Valider les comptes avant/après et agréger au grain voulu. La syntaxe et la sémantique exacte dépendent du dialecte ; ne pas les déduire du seul nom de fonction.

---

Comment utiliser EXPLAIN pour diagnostiquer une requête de préparation de données lente ? <!--anki:3339643564313965373735383430666438316432393735633133313665383736-->
?
Examiner **lectures, cardinalités estimées, filtres, stratégies de jointure et tris**, puis confronter le plan aux mesures d'exécution. Une mauvaise estimation peut entraîner un choix inadapté ; une jointure multiplicative peut expliquer coût et données erronées.

Vérifier statistiques, colonnes réellement lues et possibilité d'éliminer des partitions. Dans PostgreSQL, `EXPLAIN ANALYZE` exécute la requête : utiliser un contexte de test adapté, surtout pour une mutation. Un coût estimé n'est pas une durée en millisecondes. Optimiser après avoir confirmé l'équivalence des résultats, pas seulement la vitesse.

---

Pourquoi tester une transformation SQL avec des données adverses de petite taille ? <!--anki:6164393634373131383134653463396238373663613033336165333632366462-->
?
Un petit jeu explicite rend les **erreurs sémantiques observables** : doublons de clés, valeurs nulles, absence de correspondance, égalité de timestamps, suppression et frontière temporelle. Fixer les lignes attendues, pas seulement le nombre total.

Compléter par des invariants sur un volume représentatif : unicité, références, sommes de contrôle métier et stabilité au rejeu. Une requête qui compile peut produire des labels faux ou perdre un segment. Un test unitaire ne mesure toutefois ni la performance à grande échelle ni la qualité réelle de la source.

---

## Mises en situation

Mise en situation : une table de clients perd 30 % de ses lignes après un LEFT JOIN avec leurs achats. Comment recherches-tu l’erreur ? <!--anki:6134623064373962646333373461323062643661393038633437616330643033-->
?
1. **Comparer les identifiants avant/après** pour identifier les clients disparus.
2. **Inspecter les filtres WHERE** portant sur les colonnes d'achat, notamment dates et statuts.
3. **Clarifier la population attendue** : tous les clients ou seulement ceux ayant acheté.
4. **Déplacer les critères dans ON si adapté**, puis vérifier le grain et les sommes.
5. **Ajouter des cas sans achat, avec achat exclu et avec plusieurs achats** au test de transformation.

**Piège** : remplacer la jointure par une autre sans définir ce que représente une ligne.

---

Mise en situation : relancer une requête choisit parfois une autre version du même document, sans changement de données. Que vérifies-tu ? <!--anki:6565353134626666613133363464653139323636366439626632323131643863-->
?
1. **Chercher les ex æquo** dans l'ordre de la fenêtre ou de la sélection.
2. **Vérifier les versions source** et les éventuels événements contradictoires.
3. **Définir un ordre total stable**, compatible avec la règle métier.
4. **Tester permutations d'entrée et égalités**, puis comparer les sorties.
5. **Tracer la version choisie** pour les embeddings et exemples dérivés.

**Piège** : supposer que l'ordre physique des fichiers départage les lignes de manière contractuelle.

---

Mise en situation : une moyenne de satisfaction augmente après une migration SQL, mais les utilisateurs ne voient aucun progrès. Comment enquêtes-tu ? <!--anki:6666643433616663663263343461346162663066643236386139303964666339-->
?
1. **Fixer la population et la période** pour comparer les deux versions.
2. **Comparer les dénominateurs**, les nulls et les exclusions par segment.
3. **Inspecter COALESCE, jointures et agrégations** susceptibles de modifier les poids.
4. **Rejouer sur des cas simples** dont les valeurs attendues sont connues.
5. **Corriger puis republier** les mesures concernées, avec une définition versionnée.

**Piège** : réentraîner le modèle alors que la métrique a changé de sens.

---

## Sources
- [PostgreSQL — jointures, WHERE et agrégations](https://www.postgresql.org/docs/current/queries-table-expressions.html)
- [PostgreSQL — fonctions de fenêtre](https://www.postgresql.org/docs/current/tutorial-window.html)
- [PostgreSQL — IN, NOT IN et valeurs nulles](https://www.postgresql.org/docs/current/functions-comparisons.html)
- [PostgreSQL — lecture des plans EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html)
- [dbt — modèles incrémentaux et clés](https://docs.getdbt.com/docs/build/incremental-models)

## Connexions
- [[150-010-modelisation-donnees-analytiques|Modélisation analytique]] — préserver le grain et la cardinalité des transformations
- [[26-text-to-sql|Text-to-SQL]] — valider le sens et les résultats du SQL
- [[159-donnees-temporelles-features|Variables temporelles]] — empêcher les jointures qui révèlent le futur
- [[00-moc-ai-engineering|MOC AI Engineering]]
