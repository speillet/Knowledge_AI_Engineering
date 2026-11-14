# Transformations & orchestration des pipelines data — Flashcards
Tags: #flashcards #ai-engineering #donnees #data-engineering
Vérifié le : 9 octobre 2026 — références techniques et exemples de cette fiche.
<!-- summary: ETL/ELT, couches de données, tâches et assets, intervalles logiques, dépendances, incrémental, retries, publication, CI, ressources et chemin critique d’un DAG, publication concurrente d'un même intervalle, données disponibles, tâche réussie sans publication. -->


À ne pas confondre : ETL et ELT dans un pipeline de données IA ? <!--anki:3335323665353333336238353433396662366239393935376130313139346330-->
?
**ETL** transforme avant de charger dans la destination analytique ; **ELT** charge d'abord, puis transforme avec les ressources de cette destination. Une chaîne réelle combine souvent les deux : pseudonymiser les e-mails clients avant l'entrepôt partagé, puis transformer les journaux chargés bruts avec dbt.

Conserver les sources facilite certains rejeux, mais ne justifie pas de copier sans limite toutes les données sensibles. Choisir où filtrer, pseudonymiser et valider selon les accès et usages autorisés. Comparer coûts de transfert, ressources et traçabilité. L'ordre des lettres ne garantit ni qualité ni reproductibilité : celles-ci demandent contrats, versions et règles de publication.

---

Quel intérêt ont des couches brute, préparée et métier dans un pipeline IA ? <!--anki:3361363930643062353730623430316262613066646566383034613335383837-->
?
Elles séparent **fidélité à la source, transformations communes et produits consommables**. Exemple : `brut.tickets` garde le JSON reçu pour expliquer et rejouer ; `prep.tickets` type les dates et dédoublonne ; `metier.tickets_resolus_jour` expose une ligne par ticket résolu et par jour, avec ses garanties.

Les appellations bronze, silver et gold sont des conventions, pas des niveaux de qualité automatiques. Chaque couche doit avoir contrat, propriétaire, rétention et accès. Éviter de multiplier les copies sans besoin ; un petit pipeline peut matérialiser seulement les frontières utiles à la reprise, au partage ou à la validation.

---

À ne pas confondre : orchestrateur et moteur de traitement de données ? <!--anki:6130323930663631383436303431366639666666666233323366323134373033-->
?
L'**orchestrateur** décide quelles tâches lancer, avec quelles dépendances, paramètres et reprises. Le **moteur de traitement** exécute les transformations : requêtes SQL, calcul distribué, parsing ou inférence par lots.

Exemple : une tâche Airflow lance une requête BigQuery de 40 minutes ; le calcul s'exécute chez BigQuery, et la tâche doit suivre l'identifiant du job. Le DAG doit connaître sa vraie fin et récupérer ses références de sortie, pas seulement constater qu'une soumission a réussi. Cette séparation aide à dimensionner chaque couche, mais impose de gérer annulation, timeout et reprise lorsqu'un job continue après la perte de connexion à l'orchestrateur.

---

À ne pas confondre : tâche de pipeline et asset de données ? <!--anki:3065313931373331623363363435363761306339333634383337353461343831-->
?
Une **tâche** représente une opération exécutée ; un **asset** représente un résultat de données identifiable, comme une table de features ou une partition de corpus. Une même tâche peut produire plusieurs assets, et un asset peut être reconstruit lors de plusieurs exécutions.

Suivre seulement les tâches ne dit pas forcément quelle version les consommateurs peuvent lire. Avec Dagster, l'asset déclare lui-même dépendances et partitions :
```python
@asset(partitions_def=DailyPartitionsDefinition(start_date="2026-01-01"))
def features_clients(commandes):      # dépend de l'asset « commandes »
    ...
```
Une orchestration orientée assets facilite ce raisonnement, mais n'élimine ni les contrôles de contenu ni les problèmes de cohérence entre plusieurs sorties.

---

Pourquoi paramétrer un job par intervalle de données plutôt que par l’heure courante ? <!--anki:3963323130643034643937613433363438643838663230313734346162646533-->
?
L'**intervalle logique** précise les données à traiter, indépendamment de l'heure réelle de lancement. Un job du lundi peut être exécuté mardi après une panne tout en reconstruisant exactement la période du lundi.

Utiliser des bornes explicites, par exemple [début, fin), avec fuseau défini. Un filtre fondé sur `now()` change de périmètre lors d'un retry et rend un backfill ambigu. Dans Airflow, l'intervalle associé au run et sa date logique ne désignent pas nécessairement l'heure d'exécution. Tester frontières et changements d'heure pour les calendriers locaux.

---

Comment définir les dépendances de données d’une partition aval ? <!--anki:3436626265303765326638343431653262666638663338373665326264376633-->
?
Décrire **quelles partitions et versions amont alimentent chaque partition aval**, avec règle de complétude, pas seulement ordre des tâches.

Exemple : une feature quotidienne sur les sept jours `J−6` à `J` dépend de ces sept entrées. Corriger la source du jour `J` invalide aussi les sorties déjà produites pour `J+1` à `J+6`, pas seulement celle de `J`.

Enregistrer ce lien pour cibler le recalcul et éviter un backfill intégral inutile. Distinguer entrée absente, vide valide et provisoire ; publier avec un indicateur de complétude si le métier l'accepte. Une tâche verte ne prouve pas que ses dépendances correspondent aux bonnes versions.

---

Pourquoi transmettre des références de datasets entre tâches plutôt que leur contenu complet ? <!--anki:3133383036323433646564313462663738323635393731343564353136303961-->
?
Les métadonnées d'orchestration conviennent à des **identifiants, chemins, versions et manifestes**, pas à des millions de lignes ou à des poids de modèles. Exemple : un DataFrame de 2 millions de lignes poussé en XCom remplit la base de métadonnées d'Airflow ; `s3://features/v42/_manifest.json` suffit.

Écrire les résultats dans un stockage adapté, puis passer une référence stable avec contrôles d'accès et durée de conservation. La tâche suivante vérifie la version et le statut de publication. Un chemin `latest` mutable n'offre pas la même garantie qu'un manifeste immuable ; une référence expirée doit être détectée clairement.

---

Comment rendre une tâche de transformation sûre à relancer ? <!--anki:6566366433353762383064623432353761613363316166613737643433326133-->
?
Définir un résultat identifié par **entrées, période et version de logique**, puis publier de manière idempotente ou remplacer une partition complète selon un protocole sûr.
```sql
BEGIN;
DELETE FROM ventes_jour WHERE jour = DATE '2026-10-21';
INSERT INTO ventes_jour SELECT ... WHERE jour = DATE '2026-10-21';
COMMIT;   -- relancer redonne la même partition, sans doublons
```

Tester un crash avant écriture, après écriture et avant confirmation à l'orchestrateur. Les appels externes peuvent être répétés malgré une sortie aval dédupliquée : prévoir identifiants et garanties adaptées. Une tâche qui reprend ne doit pas choisir de nouvelles entrées implicites ou relancer un effet métier sans contrôle.

---

Comment distinguer une erreur à réessayer d’une erreur à corriger dans un pipeline ? <!--anki:3666613337666338343033323436343761363536616465326665363333636231-->
?
Une erreur **transitoire**, comme une indisponibilité brève ou un quota temporaire, peut justifier des retries bornés avec attente croissante et dispersion. Une violation de schéma ou une donnée invalide exige souvent correction ou quarantaine.

Exemple : HTTP 429 ou 503, retry après 1, 2 puis 4 s avec dispersion, cinq fois au plus ; colonne `montant` absente, quarantaine et alerte au propriétaire, sans retry. Réessayer immédiatement à l'infini peut saturer la dépendance et bloquer les autres partitions. Ne pas absorber l'erreur puis déclarer le dataset complet ; rendre visibles couverture partielle, nombre de tentatives et actions attendues du propriétaire.

---

Pourquoi une transformation incrémentale ne se réduit-elle pas à filtrer les lignes les plus récentes ? <!--anki:3265616161316137383066363465366662653036333665646236343738636464-->
?
Elle doit traiter **créations, modifications, suppressions et corrections tardives** selon le résultat attendu. Un filtre sur la date métier maximale peut manquer une ligne ancienne arrivée aujourd'hui.

Définir curseur fiable, éventuelle fenêtre de reprise et méthode d'écriture. Une fenêtre de trois jours n'attrape pas une correction reçue après une semaine : prévoir réconciliation ou reconstruction ciblée. Dans dbt, `unique_key` aide certaines stratégies à rapprocher les lignes ; ce paramètre n'impose pas à lui seul unicité, absence de nulls ou capture des suppressions.

---

Que vérifier en CI pour une transformation de données avant sa publication ? <!--anki:3865383533663130663166633466303139653131653239306538663330633062-->
?
Combiner **tests de logique sur petits exemples**, contrôles de schéma et de contrats, puis comparaison d'un résultat sur un périmètre représentatif. Tester les clés, limites temporelles, suppressions et rejeux, pas seulement la compilation.

Exécuter dans une destination isolée avec droits et coûts bornés, par exemple `dbt build --select state:modified+ --defer --state prod/` pour les seuls modèles modifiés et leurs dépendants. Un test dbt passe quand sa requête renvoie zéro ligne : `WHERE montant < 0` sur une colonne toujours nulle passe toujours. Prévoir un exemple qui doit échouer.

---

Pourquoi un déclenchement à heure fixe ne prouve-t-il pas que les données amont sont prêtes ? <!--anki:6635343033653666346536363463356439386162383961393764383266396333-->
?
Un horaire prévoit une **exécution**, pas la complétude d'une source. Un export peut arriver tard, partiellement ou sous un nouveau schéma alors que le cron aval démarre normalement.

Attendre un signal de publication fiable, vérifier manifeste et contrat, puis appliquer timeout et politique de données manquantes. Un déclenchement par événement réduit certains délais, mais un événement « fichier créé » peut lui aussi arriver avant une publication complète : un export écrit en 25 minutes est lu tronqué, sauf si l'on attend un marqueur `_SUCCESS` ou un manifeste. Séparer arrivée, validation et disponibilité pour consommation, avec un état explicite à chaque frontière.

---

Comment éviter qu’un backfill monopolise les ressources des pipelines courants ? <!--anki:6362313636623664393431343438653061666633346632363535303230626162-->
?
Réserver **concurrence et quotas** par classe de travail, limiter les runs actifs et découper le backfill en unités reprenables. Dans Airflow, par exemple, `max_active_runs=2` sur le DAG de backfill et un pool `backfill` de deux emplacements, distinct de celui du trafic courant. Tenir compte des limites de la source, du warehouse et des API modèles, pas seulement des workers.

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

Si les deux branches partagent une ressource saturée, elles ne sont plus indépendantes en temps d'exécution. Mesurer leurs durées simultanées plutôt que réutiliser leurs temps isolés pour promettre les quinze minutes.

---

Pourquoi deux orchestrations du même intervalle de données doivent-elles publier un résultat cohérent ? <!--anki:6534393565393834363234353437613639393530393536613330666130653565-->
?
Un **retry, backfill ou lancement manuel** peut recalculer le même intervalle en parallèle. Si chaque run écrit directement dans la destination finale, les lecteurs peuvent voir des résultats mélangés.

Définir une identité de partition logique, écrire dans une version isolée, valider puis publier avec un contrôle de concurrence. Décider si une seconde exécution retrouve le résultat existant ou le remplace selon une règle explicite. Tester deux runs simultanés. Le succès de toutes les tâches d'un DAG ne garantit pas que leur publication concurrente respecte le contrat de données.

---

Pourquoi une dépendance de données est-elle plus précise qu'une simple attente entre horaires de jobs ? <!--anki:6433643662623338386465643436636438323861623565626433306563623563-->
?
Un job lancé à 03 h peut dépendre d'un producteur de 02 h **qui a échoué ou n'a publié qu'une partie des données**. L'heure ne prouve pas la disponibilité.

Déclencher selon un état de publication validé pour l'intervalle attendu, avec fraîcheur et complétude. Prévoir timeout et politique de retard. Un succès du scheduler ne doit pas être confondu avec une donnée prête pour ses consommateurs.

---

Que signifie la réussite d'une tâche de pipeline si ses résultats ne sont pas encore publiés ? <!--anki:6165666362383962613963343433376339336630383063383666363730346161-->
?
Elle peut signifier seulement **que le calcul s'est terminé**. Les consommateurs ont besoin d'une publication complète et cohérente, éventuellement distincte.

Séparer états calculé, validé et publié, puis définir quel état débloque l'aval. Tester une panne entre ces étapes. Une reprise doit pouvoir vérifier les artefacts déjà produits sans créer un lot partiellement visible ou écraser une version publiée.

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
- [[117-pipelines-entrainement-continu|Pipelines d'entraînement ML]] — cache des étapes et snapshots immuables
- [[00-moc-ai-engineering|MOC AI Engineering]]
