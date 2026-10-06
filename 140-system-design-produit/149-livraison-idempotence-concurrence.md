# Livraison, idempotence & concurrence — Flashcards
Tags: #flashcards #ai-engineering #system-design #distribue #idempotence
<!-- summary: garanties de livraison, limites du exactement une fois, timeout ambigu, identité des opérations, déduplication atomique, rétention, ack, ordre par entité, concurrence optimiste, isolation et fencing tokens. -->


À ne pas confondre : livraison au plus une fois et au moins une fois ? <!--anki:6338323339363635373833343438333462316232386335666330386265396435-->
?
**Au plus une fois** évite les relivraisons mais peut perdre un message. **Au moins une fois** permet des relivraisons pour ne pas abandonner un message non confirmé ; le consommateur doit supporter les doublons.

Préciser les conditions de durabilité, de rétention et de disponibilité qui bornent ces garanties. Un broker ne promet pas nécessairement de réessayer éternellement. Pour une action d'agent, distinguer message reçu et effet métier réalisé : deux réceptions peuvent correspondre à un seul effet si le consommateur est correctement conçu.

---

Pourquoi une garantie exactement une fois doit-elle préciser son périmètre ? <!--anki:3866373364386264623830343439393839643132626537386366336564633831-->
?
Elle peut concerner **une transaction interne au moteur**, sans inclure un paiement ou un e-mail externe. Par exemple, consommer un événement et produire un résultat dans un même système transactionnel n'englobe pas automatiquement les effets d'une API distante.

Demander quelles écritures sont atomiques, comment les reprises sont identifiées et combien de temps les doublons sont reconnus. On peut obtenir un effet métier unique avec livraisons répétées, déduplication et destination adaptée. Il faut démontrer cette chaîne de garanties au lieu de l'inférer d'une option portant le nom « exactly-once ».

---

Pourquoi un timeout d'appel d'outil ne signifie-t-il pas que l'action a échoué ? <!--anki:3762636139316533313363333433343661616431393837303766633965386439-->
?
Le client sait seulement qu'il **n'a pas reçu de réponse dans le délai**. La requête peut ne pas être arrivée, être encore en cours, ou avoir réussi avec une réponse perdue.

Pour une action à effet externe, enregistrer un état « résultat inconnu » et rechercher son statut avec l'identifiant de l'opération. Un retry est sûr seulement si le protocole permet de reconnaître la même intention. Réessayer avec un nouvel identifiant peut transformer une simple perte de réponse en double paiement ou double réservation.

---

À ne pas confondre : idempotence d'une opération et déterminisme de sa réponse ? <!--anki:6333353633376632626632373464616362653235323461303964353765613762-->
?
L'**idempotence** signifie que répéter la même opération conserve l'effet attendu d'une seule application. Le **déterminisme** signifie obtenir le même résultat pour les mêmes entrées dans les conditions définies.

Un service peut retourner une réponse textuelle différente tout en n'effectuant qu'un débit. Inversement, un agent peut répondre exactement la même phrase tout en déclenchant deux débits. Définir l'idempotence sur l'état métier observable, avec son périmètre et sa durée, puis préciser séparément si la réponse initiale est conservée et renvoyée aux retries.

---

Comment construire une clé d'idempotence pour une action d'agent ? <!--anki:6334313330346166326230393438616639636331376164373165343539643165-->
?
Créer un **identifiant stable de l'intention métier**, avant l'appel externe, et le réutiliser à chaque tentative de cette même action. Le rattacher au tenant et au type d'opération ; une nouvelle intention reçoit une nouvelle clé.

Ne pas dériver uniquement la clé du texte généré, qui peut varier, ni uniquement des paramètres, car deux achats identiques peuvent être légitimes. Conserver aussi une empreinte des paramètres pertinents. La réutilisation d'une clé avec un autre montant doit provoquer un conflit explicite, pas exécuter une nouvelle action silencieusement.

---

Pourquoi « vérifier puis insérer » ne suffit-il pas à dédupliquer deux requêtes concurrentes ? <!--anki:3933616535306664383636303461313561616166333735336439626339326135-->
?
Deux workers peuvent tous deux lire **« opération absente »**, puis effectuer chacun l'action. Une lecture préalable n'exclut pas l'autre écriture.

Pour un effet entièrement dans une base, associer une contrainte d'unicité sur l'identité de l'opération et la mutation métier dans la même transaction. La seconde tentative doit attendre ou constater le conflit et retrouver le résultat. Si l'effet est externe, l'unicité locale ne couvre pas le crash après son exécution : la destination doit coopérer ou une réconciliation doit résoudre l'incertitude.

---

Quelle durée de conservation choisir pour les clés d'idempotence ? <!--anki:3833356231616533393838353431336161336236363963643661633861343836-->
?
La durée doit couvrir **l'horizon réel de retry et de rejeu**, y compris reprises manuelles, incidents et tâches retardées. Après expiration, une ancienne tentative peut être considérée comme nouvelle et reproduire son effet.

Documenter ce que garantit la destination et ne pas supposer une déduplication éternelle. Pour une opération durablement unique, un identifiant métier persistant peut être nécessaire au-delà d'un cache de clés. Définir aussi le traitement des opérations en cours ou au résultat inconnu : les supprimer par simple TTL peut rouvrir une fenêtre de double exécution.

---

Quand acquitter un message consommé pour éviter les pertes ? <!--anki:6335373038626363656335643437643061396138323437626437366263346362-->
?
Après la **persistance durable de l'effet et des informations de déduplication**, lorsque leur périmètre le permet. Acquitter avant peut perdre le travail après une panne. Acquitter après laisse une fenêtre de relivraison si le worker plante entre commit et ack.

Cette dernière fenêtre se traite par une reprise idempotente. Si l'ack et la mutation ne partagent pas de transaction, ne prétendre pas les rendre atomiques avec leur seul ordre d'exécution. Les appels externes exigent en plus une stratégie pour l'effet déjà réalisé mais encore non enregistré localement.

---

Une file de messages garantit-elle l'ordre de toutes les opérations ? <!--anki:3637363639313263666164663464396162623837643966323337613735393661-->
?
**Pas nécessairement.** L'ordre peut être garanti seulement par partition ou clé, et plusieurs consommateurs peuvent terminer leurs traitements dans un ordre différent de celui des réceptions.

Définir l'ordre nécessaire, généralement par entité métier, puis choisir partitionnement, séquence et politique de reprise. Un numéro de version aide à refuser un état obsolète. Mais un delta, comme « ajouter un article », ne peut pas toujours être ignoré parce qu'une opération suivante est déjà arrivée. L'ordre global coûte davantage et reste souvent inutile.

---

Comment la concurrence optimiste évite-t-elle une mise à jour perdue ? <!--anki:3161666463306237633138323438643239363864366138383830393164323839-->
?
La mutation vérifie que la **version lue est toujours courante**, puis incrémente cette version dans la même écriture conditionnelle. Si un autre worker a changé l'objet, aucune ligne n'est modifiée et l'opération doit être recalculée ou refusée.
```sql
UPDATE dossiers
SET statut = 'valide', version = version + 1
WHERE id = :id AND version = :version_lue;
```
Cet exemple est du SQL paramétré conceptuel. Vérifier le nombre de lignes touchées. Ne pas rejouer aveuglément une décision devenue périmée, surtout si le prix, les droits ou les paramètres approuvés ont changé.

---

À ne pas confondre : atomicité et isolation d'une transaction ? <!--anki:6530353664656438353531373430666239313232376537383430313638306438-->
?
L'**atomicité** garantit que les écritures d'une transaction sont validées ensemble ou annulées ensemble. L'**isolation** définit ce que des transactions concurrentes peuvent observer et les anomalies encore possibles.

Deux transactions atomiques peuvent tout de même violer une règle globale si elles lisent chacune un état incomplet des actions de l'autre. Par exemple, deux dépenses peuvent chacune sembler compatibles avec un plafond partagé. Protéger l'invariant par contraintes, verrouillage ou isolation appropriée, puis gérer les conflits et reprises que le stockage peut demander.

---

Pourquoi un verrou distribué avec expiration ne suffit-il pas toujours à protéger une écriture ? <!--anki:6330663731363636653062313462373339353161646266346433313333343064-->
?
Un worker peut être **suspendu assez longtemps pour perdre son bail**, puis reprendre sans le savoir. Un second worker possède alors le verrou, mais le premier peut encore envoyer une écriture tardive.

Un fencing token croissant, vérifié par la ressource protégée, permet de refuser les opérations provenant d'un ancien détenteur. Sans cette vérification au point d'écriture, le numéro ne protège rien. Une écriture conditionnelle sur version peut aussi convenir selon le besoin. Tester pauses, partitions réseau et expiration, pas seulement la concurrence en fonctionnement normal.

---

Calcul : avec 10 000 opérations uniques et 200 relivraisons, combien d'effets métier doit produire un consommateur idempotent ? <!--anki:6639366265346662346162353466626461326365326139646264356530373339-->
?
Sous hypothèse que chaque opération est légitime, finit par réussir et que les relivraisons gardent la même identité, il doit produire **10 000 effets**, malgré 10 200 livraisons.

Le nombre de tentatives n'est donc pas le nombre de succès métier. Mesurer séparément opérations uniques, tentatives, doublons détectés, résultats inconnus et échecs définitifs. Si certaines clés ont expiré ou si un retry recrée une identité, cette propriété peut casser. Le calcul définit un invariant à vérifier dans un test de panne, pas une garantie offerte par la file seule.

---

## Mises en situation

Mise en situation : deux workers consomment le même événement et débitent chacun un crédit client. Comment rends-tu ce traitement sûr ? <!--anki:6333323763313939336238633437323939313639663864663431656265343862-->
?
1. **Donner une identité stable** à l'opération, distincte du numéro de tentative.
2. **Imposer l'unicité** de cette identité dans le stockage du traitement.
3. **Regrouper déduplication et débit** dans la même transaction si les deux sont locaux.
4. **En cas d'effet distant**, utiliser l'idempotence de la destination et conserver le résultat récupérable.
5. **Tester la course et les crashes** avant commit, après commit et avant ack.

**Piège** : placer seulement un `if not exists` dans le code de chaque worker.

---

Mise en situation : un outil de réservation répond par timeout ; l'agent propose de recommencer avec une nouvelle clé. Que doit faire l'application ? <!--anki:3963616237306536633261633431313239383533356137653631643030643066-->
?
1. **Conserver l'identité initiale** et marquer le résultat comme inconnu.
2. **Consulter le statut** de la réservation chez le fournisseur si son API le permet.
3. **Réessayer avec la même clé** seulement dans les conditions garanties par ce fournisseur.
4. **Bloquer une action supplémentaire** tant que l'incertitude ne peut pas être résolue sans risque.
5. **Réconcilier ou faire intervenir un humain** si aucune garantie technique ne permet de trancher.

**Piège** : demander au LLM de deviner si le premier appel a réussi.

---

Mise en situation : deux agents modifient la même proposition commerciale et l'un écrase la réduction de l'autre. Quelle protection ajoutes-tu ? <!--anki:3864656164616134346438373437343562316433333263363937303766366237-->
?
1. **Versionner l'objet partagé** et enregistrer la version sur laquelle chaque décision repose.
2. **Rendre la mise à jour conditionnelle** à cette version, plutôt que remplacer l'objet sans contrôle.
3. **Détecter le conflit** et relire l'état courant avant de recalculer ou demander un arbitrage.
4. **Revalider les approbations** si les paramètres autorisés ont changé.
5. **Tracer la décision retenue** et tester deux écritures simultanées.

**Piège** : recommencer automatiquement la même écriture après le conflit et recréer la perte de mise à jour.

---

## Sources
- [Apache Kafka — périmètre des garanties de livraison](https://kafka.apache.org/41/design/design/)
- [AWS Builders' Library — retries et APIs idempotentes](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)
- [PostgreSQL — contraintes](https://www.postgresql.org/docs/current/ddl-constraints.html)
- [PostgreSQL — isolation des transactions](https://www.postgresql.org/docs/current/transaction-iso.html)
- [Hazelcast — baux et fencing tokens](https://docs.hazelcast.com/hazelcast/5.5/data-structures/fencedlock)

## Connexions
- [[140-010-transactions-outbox-sagas|Transactions, outbox & sagas]] — assembler ces garanties dans un workflow
- [[142-fiabilite-resilience-llm|Fiabilité & résilience]] — rendre les reprises sûres
- [[84-streaming-integration-applicative|Intégration applicative]] — suivre les opérations indépendamment de la connexion
- [[158-ingestion-cdc-backfills|Ingestion & backfills]] — appliquer déduplication, versions et checkpoints
- [[00-moc-ai-engineering|MOC AI Engineering]]
