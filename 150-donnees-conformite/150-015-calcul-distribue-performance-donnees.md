# Calcul distribué & performance des pipelines data — Flashcards
Tags: #flashcards #ai-engineering #donnees #data-engineering
Vérifié le : 9 octobre 2026 — références techniques et exemples de cette fiche.
<!-- summary: choix local ou distribué, exécution paresseuse, partitions, shuffle, skew, broadcast, salting, mémoire driver, UDF, cache, agrégations, loi d’Amdahl et coût du traitement. -->


Quand distribuer un traitement de données plutôt que l’exécuter sur une machine ? <!--anki:6331663030656464613039623434643038353038613564656161386234653837-->
?
Lorsque **volume, temps de traitement, concurrence ou tolérance aux pannes** dépassent ce qu'une machine adaptée peut fournir à coût acceptable. Comparer d'abord une exécution locale vectorisée, éventuellement capable de déborder sur disque, à la solution distribuée.

Distribuer ajoute coordination, transferts et exploitation ; un petit job peut devenir plus lent. Un volume supérieur à la RAM n'impose pas toujours un cluster si le moteur peut traiter par blocs. Mesurer mémoire maximale, I/O, durée et coût sur une charge représentative, avec une réserve adaptée au pic.

---

À ne pas confondre : transformation paresseuse et action dans un moteur comme Spark ? <!--anki:3132643464323135323838343464623239623664623161333361643831376465-->
?
Une **transformation paresseuse** construit un plan sans nécessairement le calculer immédiatement. Une **action** demande un résultat et déclenche son exécution. Cette séparation permet à l'optimiseur de combiner des opérations et de réduire des lectures.

Définir une transformation sans lancer d'action ne mesure pas le temps réel du pipeline. Plusieurs actions peuvent aussi recalculer des étapes si elles ne sont pas réutilisées ou persistées. Inclure exécution, écriture et validation dans le benchmark, et comprendre si le résultat observé provient de données froides ou déjà en cache.

---

Qu’est-ce qu’un shuffle dans un calcul distribué ? <!--anki:6438396633363565343235363432656362393432333238363732343062643861-->
?
Un **shuffle** redistribue les données entre partitions, souvent entre machines, pour rapprocher celles nécessaires à une jointure, un tri ou une agrégation. Il peut coûter réseau, sérialisation, mémoire et disque.

Filtrer les lignes, projeter les colonnes et préagréger lorsque c'est valide peut réduire les octets échangés. Tous les opérateurs de même nom ne produisent pas le même plan : partitionnement existant et moteur comptent. Inspecter le plan physique et les métriques d'échange ; davantage de CPU ne répare pas forcément un réseau saturé.

---

Pourquoi le nombre de partitions de calcul est-il un compromis ? <!--anki:3066303161366332373137343463313538373462313766653030303234666436-->
?
Trop peu de partitions limitent le **parallélisme** et augmentent la mémoire par tâche ; trop de petites partitions accroissent les frais de planification et les petits fichiers produits. Leur taille peut être très inégale malgré un nombre apparemment correct.

Distinguer partitions de fichiers, partitions d'un shuffle et partitions métier de table. Choisir à partir des tailles observées, des ressources par tâche et de la concurrence, puis inspecter la distribution des durées. Un `repartition(1)` peut simplifier la sortie tout en créant un goulot et un risque mémoire.

---

Comment reconnaître un skew de clés dans une jointure ou une agrégation distribuée ? <!--anki:6433313061643333336430363438353861646661626632336536306139363332-->
?
Le **skew** apparaît lorsque certaines clés concentrent beaucoup plus de données ou de travail. Quelques tâches deviennent très longues ou débordent en mémoire tandis que les autres sont terminées.

Comparer tailles de partitions, durées et clés fréquentes, y compris les valeurs nulles ou par défaut. Les réponses possibles incluent préagrégation, traitement séparé des clés chaudes ou stratégies adaptatives du moteur. Ajouter des workers ne partage pas automatiquement une clé indivisible. Vérifier d'abord qu'une jointure erronée n'est pas la cause de la concentration.

---

Quand une jointure broadcast est-elle utile et quel risque mémoire introduit-elle ? <!--anki:6235666330343764313639633465373061336233346235333331376164386463-->
?
Elle diffuse une **petite relation** aux workers pour éviter de redistribuer la grande selon la clé de jointure. Elle convient si la petite relation et la structure nécessaire à la jointure tiennent dans la mémoire disponible des exécutants.

La taille compressée sur disque sous-estime souvent la taille décodée et la table de hachage. Tenir compte des tâches concurrentes et du coût de diffusion. Un seuil ou un hint ne prouve pas la faisabilité. Comparer plans, pic mémoire et durée ; vérifier la sémantique et le support du type de jointure.

---

Comment le salting peut-il répartir une clé chaude sans fausser une agrégation ? <!--anki:3164653834653139323534353461366639366239333763393434343664333237-->
?
Ajouter un **suffixe de répartition** à la clé chaude permet de produire plusieurs agrégats partiels, puis de les combiner en retirant ce suffixe. La fonction doit être combinable correctement.

Pour une moyenne, conserver somme et effectif ; moyenner les moyennes partielles sans poids est incorrect. Une jointure salée peut exiger de répliquer les correspondances de l'autre côté, ce qui augmente les données. Tester comptes et sommes après recombinaison. Le salting n'est pas une recette universelle : les fonctions non décomposables et les exigences d'ordre limitent son usage.

---

Pourquoi collecter un résultat distribué sur le driver peut-il provoquer une panne ? <!--anki:6566316130313838313136383437616362306331353639376239333963306631-->
?
Une opération comme **collect** rapatrie le résultat dans le processus coordinateur. La mémoire totale du cluster ne protège pas ce processus, qui peut devoir recevoir et matérialiser toutes les lignes.

Pour inspecter, prendre un échantillon ou une limite maîtrisée ; pour publier, écrire depuis les partitions vers un stockage adapté. Agréger avant de rapatrier seulement un petit résultat. Vérifier aussi les conversions en objets Python, souvent plus volumineuses que les données compactes. Augmenter la RAM du driver peut repousser la panne sans corriger une collecte sans borne.

---

Pourquoi préférer des expressions natives aux UDF ligne par ligne quand elles suffisent ? <!--anki:6231393762303136383337663438663338666464616135643564383035656235-->
?
Les expressions natives sont souvent **visibles de l'optimiseur** et exécutées de manière vectorisée. Une UDF opaque, notamment avec un passage entre runtimes, peut introduire sérialisation, allocations et perte d'optimisations.

Une UDF reste utile pour une logique non exprimable autrement ; la traiter par lots peut réduire les surcoûts. Comparer les résultats sur nulls, types et encodages, puis mesurer la performance. Des appels réseau ou LLM dans une UDF ajoutent aussi quotas, reprises et effets répétés : leur orchestration doit être explicite.

---

Quand persister un résultat intermédiaire de pipeline en mémoire ou sur disque ? <!--anki:3866616662333735663632353437373039646431366435386438636665396364-->
?
Lorsque sa **réutilisation** économise davantage que son coût de matérialisation, de stockage et de gestion. Un intermédiaire calculé une seule fois n'a pas automatiquement intérêt à être mis en cache.

Évaluer taille décodée, nombre de consommateurs, invalidation et pression mémoire. Libérer les résultats devenus inutiles et identifier la version source associée. Un cache peut accélérer un benchmark tout en masquant le coût d'un premier passage. Persister pour accélérer n'est pas la même chose que publier une version durable et auditée d'un dataset.

---

Comment choisir entre agrégat exact et agrégat approximatif sur de grands volumes ? <!--anki:6235623966633238616533353430343262313837623937393838613366646162-->
?
Un agrégat **approximatif** peut réduire mémoire et échanges pour estimer cardinalités ou quantiles, avec une erreur dépendant de l'algorithme et des paramètres. Il peut convenir au suivi exploratoire si sa précision suffit à la décision.

Pour un contrôle d'unicité, une facturation ou un seuil contractuel, vérifier si l'approximation est acceptable ; une estimation ne prouve pas l'absence de doublons. Documenter erreur, population et propriétés de fusion. Comparer à un résultat exact sur un périmètre maîtrisé, sans extrapoler une précision universelle à tous les jeux de données.

---

Comment distinguer un pipeline limité par le CPU, la mémoire ou les entrées-sorties ? <!--anki:6334336435313262616535313464346261666265646531303733323665633539-->
?
Relier les **temps d'étapes** à l'utilisation CPU, attente réseau/disque, débit lu, mémoire maximale et volumes de spill. Des workers peu occupés peuvent attendre des fichiers, un quota aval ou une tâche déséquilibrée.

Mesurer plusieurs couches avant de changer le nombre de workers. Réduire les lectures aide un goulot I/O ; filtrer avant un shuffle réduit les échanges ; borner les lots limite le pic mémoire. Comparer à résultat identique et inclure le coût de bout en bout. Un pourcentage CPU global peut cacher une tâche unique saturée.

---

Calcul : 20 % d’un pipeline reste strictement séquentiel, et 80 % se parallélise parfaitement. Quel gain maximal avec dix workers selon la loi d’Amdahl ? <!--anki:3633663438376530343532313466336661363232373538353763336265633334-->
?
Sous ces hypothèses idéales :
```text
accélération = 1 / (0,20 + 0,80/10) ≈ 3,57
limite avec une infinité de workers = 1 / 0,20 = 5
```
Dix workers ne donnent donc pas un gain de dix. Coordination, réseau et déséquilibre peuvent encore réduire ce résultat. Cette formule suppose une charge fixe et une fraction séquentielle inchangée ; elle ne décrit pas une augmentation simultanée du volume traité. Localiser la partie séquentielle peut être plus utile que multiplier les machines.

---

Calcul : A utilise deux workers à 0,80 €/h pendant 45 minutes ; B en utilise quatre au même tarif pendant 30 minutes. Quel coût par exécution, hors stockage et autres frais ? <!--anki:3934646165636233323435323432313562363964633731333233346165653930-->
?
Avec ces tarifs fictifs et une facturation proportionnelle au temps :
```text
A = 2 × 0,80 × 45/60 = 1,20 €
B = 4 × 0,80 × 30/60 = 1,60 €
```
B termine quinze minutes plus tôt mais coûte environ **33 % de plus**. Le choix dépend du délai requis, de la réserve et de la valeur du temps gagné. Ajouter orchestration, stockage, transferts et échecs pour le coût complet. Une durée plus courte ne suffit pas à annoncer un pipeline moins cher.

---

## Mises en situation

Mise en situation : 99 % des tâches Spark finissent en deux minutes, mais une seule dure quarante minutes. Que recherches-tu avant d’ajouter des machines ? <!--anki:6434616135663639306366333466626539663666313961316437626235313236-->
?
1. **Comparer la partition lente** aux autres : octets, lignes, clés et spill.
2. **Chercher une clé chaude ou une jointure multiplicative**, notamment sur les nulls.
3. **Vérifier le plan** et la possibilité de préagréger ou d'isoler cette clé.
4. **Tester une stratégie adaptée**, comme répartition supplémentaire ou traitement séparé.
5. **Comparer résultat, durée et coût**, avec un cas qui concentre volontairement les données.

**Piège** : augmenter les workers sans modifier le travail de la partition qui bloque.

---

Mise en situation : une table de référence fait 200 Mo sur disque mais son broadcast provoque des erreurs mémoire. Comment enquêtes-tu ? <!--anki:3364386530333735393135383465386339643765383032353533336131333766-->
?
1. **Mesurer la taille décodée** et la structure de jointure créée en mémoire.
2. **Compter les copies et tâches concurrentes** par exécutant.
3. **Projeter et filtrer la référence** avant la diffusion si le résultat reste équivalent.
4. **Comparer avec une autre stratégie de jointure** et des partitions adaptées.
5. **Vérifier les pics mémoire** sur la charge réelle avant de rétablir le broadcast.

**Piège** : utiliser la seule taille compressée pour garantir qu'une table tient en mémoire.

---

Mise en situation : un job d’embeddings distribué relance certaines partitions et la facture API double. Comment fiabilises-tu le traitement ? <!--anki:6330396139353930393939333465616361353466353363326433623236363664-->
?
1. **Identifier les appels répétés** avec clé d'objet, version et configuration d'embedding.
2. **Séparer calcul et publication**, en conservant les résultats durables réutilisables.
3. **Prévoir la reprise sans effet répété**, avec idempotence si l'API le permet et déduplication aval.
4. **Borner concurrence et quotas**, puis classer erreurs transitoires et permanentes.
5. **Tester une panne après réponse distante**, avant enregistrement local du résultat.

**Piège** : supposer qu'une tâche distribuée n'exécute sa fonction qu'une seule fois.

---

## Sources
- [Apache Spark — shuffle, persistance et actions](https://spark.apache.org/docs/latest/rdd-programming-guide.html)
- [Apache Spark — jointures, partitions, statistiques et skew](https://spark.apache.org/docs/latest/sql-performance-tuning.html)
- [DuckDB — optimisation et traitement au-delà de la mémoire](https://duckdb.org/docs/current/guides/performance/how_to_tune_workloads)

## Connexions
- [[150-012-stockage-colonnaire-lakehouse|Stockage analytique]] — relier disposition des données et coût d’exécution
- [[150-011-sql-transformations-analytiques|SQL analytique]] — examiner les plans et préserver le résultat
- [[148-pipelines-batch-llm|Pipelines batch LLM]] — borner les appels modèles et rendre les reprises sûres
- [[00-moc-ai-engineering|MOC AI Engineering]]
