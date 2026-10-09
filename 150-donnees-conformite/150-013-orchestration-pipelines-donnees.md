# Transformations & orchestration des pipelines data — Flashcards
Tags: #flashcards #ai-engineering #donnees #data-engineering
Vérifié le : 9 octobre 2026 — références techniques et exemples de cette fiche.
<!-- summary: ETL/ELT, couches de données, tâches et assets, intervalles logiques, dépendances, incrémental, retries, publication, CI, ressources et chemin critique d’un DAG. -->


À ne pas confondre : ETL et ELT dans un pipeline de données IA ? <!--anki:3335323665353333336238353433396662366239393935376130313139346330-->
?
**ETL** transforme avant de charger dans la destination analytique ; **ELT** charge d'abord, puis transforme avec les ressources de cette destination. Une chaîne réelle peut combiner les deux.

Conserver les sources facilite certains rejeux, mais ne justifie pas de copier sans limite toutes les données sensibles. Choisir où filtrer, pseudonymiser et valider selon les accès et usages autorisés. Comparer coûts de transfert, ressources et traçabilité. L'ordre des lettres ne garantit ni qualité ni reproductibilité : celles-ci demandent contrats, versions et règles de publication.

---

Quel intérêt ont des couches brute, préparée et métier dans un pipeline IA ? <!--anki:3361363930643062353730623430316262613066646566383034613335383837-->
?
Elles séparent **fidélité à la source, transformations communes et produits consommables**. La couche brute aide à expliquer et rejouer ; la couche préparée normalise identités et types ; la couche métier expose des datasets au grain et aux garanties explicites.

Les appellations bronze, silver et gold sont des conventions, pas des niveaux de qualité automatiques. Chaque couche doit avoir contrat, propriétaire, rétention et accès. Éviter de multiplier les copies sans besoin ; un petit pipeline peut matérialiser seulement les frontières utiles à la reprise, au partage ou à la validation.

---

À ne pas confondre : orchestrateur et moteur de traitement de données ? <!--anki:6130323930663631383436303431366639666666666233323366323134373033-->
?
L'**orchestrateur** décide quelles tâches lancer, avec quelles dépendances, paramètres et reprises. Le **moteur de traitement** exécute les transformations : requêtes SQL, calcul distribué, parsing ou inférence par lots.

Un DAG peut soumettre un job distant sans traiter lui-même son volume de données. Il doit suivre sa vraie fin et récupérer ses références de sortie, pas seulement constater qu'une soumission a réussi. Cette séparation aide à dimensionner chaque couche, mais impose de gérer annulation, timeout et reprise lorsqu'un job continue après la perte de connexion à l'orchestrateur.

---

À ne pas confondre : tâche de pipeline et asset de données ? <!--anki:3065313931373331623363363435363761306339333634383337353461343831-->
?
Une **tâche** représente une opération exécutée ; un **asset** représente un résultat de données identifiable, comme une table de features ou une partition de corpus. Une même tâche peut produire plusieurs assets, et un asset peut être reconstruit lors de plusieurs exécutions.

Suivre seulement les tâches ne dit pas forcément quelle version les consommateurs peuvent lire. Définir dépendances, partitions et critères de disponibilité du résultat. Une orchestration orientée assets facilite ce raisonnement, mais n'élimine ni les contrôles de contenu ni les problèmes de cohérence entre plusieurs sorties.

---

Pourquoi paramétrer un job par intervalle de données plutôt que par l’heure courante ? <!--anki:3963323130643034643937613433363438643838663230313734346162646533-->
?
L'**intervalle logique** précise les données à traiter, indépendamment de l'heure réelle de lancement. Un job du lundi peut être exécuté mardi après une panne tout en reconstruisant exactement la période du lundi.

Utiliser des bornes explicites, par exemple [début, fin), avec fuseau défini. Un filtre fondé sur `now()` change de périmètre lors d'un retry et rend un backfill ambigu. Dans Airflow, l'intervalle associé au run et sa date logique ne désignent pas nécessairement l'heure d'exécution. Tester frontières et changements d'heure pour les calendriers locaux.

---

Comment définir les dépendances de données d’une partition aval ? <!--anki:3436626265303765326638343431653262666638663338373665326264376633-->
?
Identifier **les partitions et versions amont nécessaires**, pas seulement les tâches qui doivent être vertes. Une variable glissante sur sept jours peut dépendre de sept partitions alors qu'un export quotidien n'en utilise qu'une.

Lors d'une correction amont, recalculer les partitions aval dont la fenêtre inclut cette donnée. Définir quand les entrées sont suffisamment complètes et si un résultat provisoire est acceptable. Un graphe de tâches sans correspondance entre partitions peut laisser un dataset déclaré prêt avec des entrées anciennes, manquantes ou incompatibles.

---

Pourquoi transmettre des références de datasets entre tâches plutôt que leur contenu complet ? <!--anki:3133383036323433646564313462663738323635393731343564353136303961-->
?
Les métadonnées d'orchestration conviennent à des **identifiants, chemins, versions et manifestes**, pas nécessairement à des millions de lignes ou à des poids de modèles. Transmettre le contenu peut saturer la base de l'orchestrateur et dupliquer des données sensibles.

Écrire les résultats dans un stockage adapté, puis passer une référence stable avec contrôles d'accès et durée de conservation. La tâche suivante vérifie la version et le statut de publication. Un chemin `latest` mutable n'offre pas la même garantie qu'un manifeste immuable ; une référence expirée doit être détectée clairement.

---

Comment rendre une tâche de transformation sûre à relancer ? <!--anki:6566366433353762383064623432353761613363316166613737643433326133-->
?
Définir un résultat identifié par **entrées, période et version de logique**, puis publier de manière idempotente ou remplacer une partition complète selon un protocole sûr. Écrire provisoirement avant validation peut éviter qu'un lecteur voie une sortie partielle.

Tester un crash avant écriture, après écriture et avant confirmation à l'orchestrateur. Les appels externes peuvent être répétés malgré une sortie aval dédupliquée : prévoir identifiants et garanties adaptées. Une tâche qui reprend ne doit pas choisir de nouvelles entrées implicites ou relancer un effet métier sans contrôle.

---

Comment distinguer une erreur à réessayer d’une erreur à corriger dans un pipeline ? <!--anki:3666613337666338343033323436343761363536616465326665363333636231-->
?
Une erreur **transitoire**, comme une indisponibilité brève ou un quota temporaire, peut justifier des retries bornés avec attente croissante et dispersion. Une violation de schéma ou une donnée invalide exige souvent correction ou quarantaine.

Classer les erreurs, fixer un budget et préserver les preuves nécessaires au diagnostic. Réessayer immédiatement à l'infini peut saturer la dépendance et bloquer les autres partitions. Ne pas absorber l'erreur puis déclarer le dataset complet ; rendre visibles couverture partielle, nombre de tentatives et actions attendues du propriétaire.

---

Pourquoi une transformation incrémentale ne se réduit-elle pas à filtrer les lignes les plus récentes ? <!--anki:3265616161316137383066363465366662653036333665646236343738636464-->
?
Elle doit traiter **créations, modifications, suppressions et corrections tardives** selon le résultat attendu. Un filtre sur la date métier maximale peut manquer une ligne ancienne arrivée aujourd'hui.

Définir curseur fiable, éventuelle fenêtre de reprise et méthode d'écriture. Une fenêtre de trois jours n'attrape pas une correction reçue après une semaine : prévoir réconciliation ou reconstruction ciblée. Dans dbt, `unique_key` aide certaines stratégies à rapprocher les lignes ; ce paramètre n'impose pas à lui seul unicité, absence de nulls ou capture des suppressions.

---

Que vérifier en CI pour une transformation de données avant sa publication ? <!--anki:3865383533663130663166633466303139653131653239306538663330633062-->
?
Combiner **tests de logique sur petits exemples**, contrôles de schéma et de contrats, puis comparaison d'un résultat sur un périmètre représentatif. Tester les clés, limites temporelles, suppressions et rejeux, pas seulement la compilation.

Exécuter dans une destination isolée avec droits et coûts bornés. Les tests sur données doivent préciser s'ils bloquent la publication ou signalent une dégradation. Une requête de test qui retourne zéro ligne peut valider un invariant formulé incorrectement ; relire aussi la définition et prévoir un exemple qui doit effectivement échouer.

---

Pourquoi un déclenchement à heure fixe ne prouve-t-il pas que les données amont sont prêtes ? <!--anki:6635343033653666346536363463356439386162383961393764383266396333-->
?
Un horaire prévoit une **exécution**, pas la complétude d'une source. Un export peut arriver tard, partiellement ou sous un nouveau schéma alors que le cron aval démarre normalement.

Attendre un signal de publication fiable, vérifier manifeste et contrat, puis appliquer timeout et politique de données manquantes. Un déclenchement par événement réduit certains délais, mais un événement « fichier créé » peut lui aussi arriver avant une publication complète. Séparer arrivée, validation et disponibilité pour consommation, avec un état explicite à chaque frontière.

---

Comment éviter qu’un backfill monopolise les ressources des pipelines courants ? <!--anki:6362313636623664393431343438653061666633346632363535303230626162-->
?
Réserver **concurrence et quotas** par classe de travail, limiter les runs actifs et découper le backfill en unités reprenables. Tenir compte des limites de la source, du warehouse et des API modèles, pas seulement des workers.

Mesurer retard du trafic courant et progression du rejeu, puis ajuster la priorité. Des tâches individuellement légères peuvent produire une pointe importante lorsqu'elles démarrent ensemble. Prévoir pause, annulation et nettoyage ; un job distant peut continuer à consommer après un timeout de l'orchestrateur.

---

Calcul : un DAG a une ingestion de 2 minutes, deux branches indépendantes de 10 et 4 minutes, puis une publication de 3 minutes attendant les deux. Quelle durée idéale et quel travail cumulé ? <!--anki:3166623462333236336535623431383962383636633864643239383130303666-->
?
Sans attente ni contention :
```text
durée critique = 2 + max(10, 4) + 3 = 15 minutes
travail cumulé = 2 + 10 + 4 + 3 = 19 minutes de tâche
```
Réduire la branche de quatre minutes n'accélère pas ce chemin critique tant qu'elle reste plus courte que l'autre. Le parallélisme consomme cependant des ressources simultanées. Inclure files, démarrage, transferts et validation pour prévoir la durée réelle. Ces minutes de tâche ne sont pas directement des minutes facturées si les tâches utilisent des ressources différentes.

---

## Mises en situation

Mise en situation : un backfill de janvier écrit dans la partition du jour parce que le script utilise la date système. Comment le corriges-tu ? <!--anki:3264313131623362323035653432356161386437646333366339646566646363-->
?
1. **Identifier les sorties touchées** et suspendre leur publication si nécessaire.
2. **Passer l'intervalle logique explicitement** aux lectures et écritures.
3. **Épingler entrées et version de code** pour rendre chaque partition reproductible.
4. **Tester deux relances à des dates différentes**, avec mêmes paramètres et résultats attendus.
5. **Réparer les partitions affectées** puis valider les consommateurs dépendants.

**Piège** : changer seulement le nom du fichier de sortie sans corriger le filtre d'entrée.

---

Mise en situation : une tâche soumet un job distant, perd la connexion puis le soumet une seconde fois au retry. Quelle stratégie proposes-tu ? <!--anki:6234623531333764653665643433306339363265396331623034386165393065-->
?
1. **Donner une identité stable à la soumission** lorsque le service distant le permet.
2. **Conserver l'identifiant du job** et rechercher son état avant de recréer du travail.
3. **Définir la politique d'annulation** et le traitement d'un état inconnu.
4. **Rendre la publication aval idempotente**, même si le calcul a été exécuté deux fois.
5. **Tester la perte de connexion après acceptation** et observer le coût résiduel.

**Piège** : croire qu'un timeout local prouve que le traitement distant n'a pas commencé.

---

Mise en situation : un DAG est vert, mais le dataset publié contient seulement neuf partitions sur dix attendues. Que modifies-tu ? <!--anki:6563343534396332373137623436346162643931616663333738646238303564-->
?
1. **Définir un manifeste des partitions attendues** pour cet intervalle.
2. **Vérifier les règles de succès** et les erreurs absorbées ou tâches sautées.
3. **Ajouter une validation avant publication**, avec volumes et cohérence des versions.
4. **Publier un statut partiel uniquement si le contrat l'autorise**, sinon maintenir la dernière version valide.
5. **Rejouer la partition manquante** et tester ce scénario de panne.

**Piège** : confondre succès de l'orchestration et conformité du produit de données.

---

## Sources
- [Apache Airflow — bonnes pratiques de tâches et données](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)
- [Apache Airflow — runs et intervalles de données](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dag-run.html)
- [Apache Airflow — contrôle des backfills](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/backfill.html)
- [dbt — incrémental et limites des clés](https://docs.getdbt.com/docs/build/incremental-models)
- [dbt — tests de données](https://docs.getdbt.com/docs/build/data-tests)

## Connexions
- [[158-ingestion-cdc-backfills|Ingestion & backfills]] — coordonner reprises, partitions et publication
- [[150-011-sql-transformations-analytiques|SQL analytique]] — valider les transformations avant publication
- [[41-automatisation-code-nocode|Automatisation]] — séparer orchestration et exécution des traitements
- [[150-015-calcul-distribue-performance-donnees|Calcul distribué]] — dimensionner les ressources et le chemin critique
- [[150-014-streaming-traitements-evenements|Streaming & traitements d’événements]] — coordonner traitements et reprises
- [[150-016-observabilite-lignage-donnees|Observabilité, lignage & exploitation des données]] — relier exécution réussie et disponibilité des résultats
- [[00-moc-ai-engineering|MOC AI Engineering]]
