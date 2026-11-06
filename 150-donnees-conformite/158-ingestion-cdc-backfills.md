# Ingestion incrémentale, CDC & backfills — Flashcards
Tags: #flashcards #ai-engineering #donnees #data-engineering #ingestion
<!-- summary: snapshot ou incrémental, CDC, cohérence snapshot-journal, checkpoints, identités et versions, suppressions, rejeu historique, capacité de rattrapage, quarantaine, réconciliation et index RAG, pagination API et cohérence des extractions. -->


Quand choisir une ingestion complète plutôt qu'incrémentale ? <!--anki:3366623837653530383437383462643961383764376337666362306263306237-->
?
Une **reconstruction complète** simplifie la logique lorsque le volume et le délai le permettent. Une ingestion **incrémentale** ne traite que les changements et réduit le travail, mais doit gérer créations, mises à jour, suppressions et reprises.

Décider à partir du volume, de la fraîcheur exigée et de la capacité de la source à exposer les changements. Exemple : 50 000 fiches produit rechargées chaque nuit en quelques minutes ne justifient pas une CDC ; 500 millions de lignes à rafraîchir toutes les 15 minutes l'exigent. Une optimisation qui économise du calcul mais perd les suppressions produit un index moins coûteux et pourtant incorrect.

---

À ne pas confondre : polling sur updated_at et capture de changements CDC ? <!--anki:6462396566393064356561363466356361666538656537623762333733633834-->
?
Le **polling** interroge périodiquement les lignes selon un champ ou un curseur. La **CDC** capture créations, modifications et suppressions, souvent via le journal transactionnel, avec une position de reprise.

Un polling naïf sur un timestamp peut manquer suppressions physiques et transactions longues. Exemple : une transaction écrit `updated_at = 09:59:58` mais ne valide qu'à 10:00:02 ; le poll de 10:00:00 ne la voit pas, le suivant filtre `updated_at > 10:00:00` et la perd. La CDC lit les validations dans l'ordre du journal, mais exige de gérer rétention, schéma, snapshots et doublons de livraison. Elle ne garantit pas à elle seule des effets aval exécutés exactement une fois.

---

Comment initialiser un pipeline CDC sans perdre les changements survenus pendant le snapshot ? <!--anki:3235363032383236336631303436323462363731326537383837356235313638-->
?
Coordonner le **snapshot initial et une position du journal** suivant le protocole du connecteur. Les changements concurrents doivent être raccordés à l'état initial, avec une stratégie pour les éventuels recouvrements.

Copier une table puis « commencer à écouter maintenant » laisse une fenêtre de perte. Lire le journal avant de copier sans gérer l'ordre peut aussi écraser une version récente par une ancienne. Exemple : le connecteur PostgreSQL de Debezium relève la position du journal dans la transaction du snapshot, copie les tables, puis diffuse le journal depuis cette position. Tester des écritures concurrentes pendant l'initialisation.

---

À quel moment enregistrer le checkpoint d'une ingestion ? <!--anki:3937643835363461623534333431353938363038666366666230333333643530-->
?
Après que les **résultats correspondants sont durables**, ou atomiquement avec leur écriture si le stockage le permet. Avancer le curseur avant la persistance peut perdre des événements après un crash ; le sauvegarder après peut conduire à les rejouer.

Le rejeu doit donc être sûr grâce à une identité stable et à des écritures idempotentes ou dédupliquées. Exemple avec Kafka : désactiver `enable.auto.commit`, écrire le lot dans la destination, puis valider l'offset ; un crash entre les deux rejoue au plus ce lot. Un checkpoint local ne prouve pas qu'un index distant a été mis à jour : définir « traitement terminé » pour chaque destination.

---

Pourquoi distinguer identifiant de document, identifiant d'événement et version ? <!--anki:3435656462653130323135653463373662643936613263613465353235666131-->
?
L'**identifiant de document** désigne l'objet métier ; l'**identifiant d'événement** distingue une modification de sa relivraison ; la **version** aide à ordonner les états de cet objet. Ils répondent à des questions différentes.

Exemple pour `contrat-42` : dédupliquer par document écarterait la version 8 après la 7. Dédupliquer par événement écarte bien la relivraison de `evt-91`, mais laisse la version 7, retardée, écraser la 8. Utiliser un ordre de version garanti par la source, ou une stratégie de résolution explicite : un timestamp mural n'offre pas toujours un ordre fiable entre producteurs.

---

Comment éviter qu'une ancienne mise à jour écrase une version plus récente ? <!--anki:3964333238396637636161363466663538346263616534373766353831613139-->
?
Appliquer une **écriture conditionnelle sur la version**, atomique dans la destination : accepter seulement une version ultérieure selon l'ordre défini. En PostgreSQL :
```sql
INSERT INTO docs (id, version, contenu) VALUES (:id, :version, :contenu)
ON CONFLICT (id) DO UPDATE SET version = EXCLUDED.version, contenu = EXCLUDED.contenu
WHERE docs.version < EXCLUDED.version;   -- une version plus ancienne ne change rien
```
Un upsert aveugle n'est pas suffisant si les livraisons sont désordonnées. Distinguer les événements portant un état complet des deltas : ignorer un ancien état peut être correct, ignorer un incrément nécessaire peut perdre une opération. Pour des deltas, il faut une séquence complète, une déduplication des opérations ou une réconciliation depuis la source.

---

Comment propager une suppression jusqu'à un index RAG ? <!--anki:6663643766393837323139303465393761323836393561653566636136653538-->
?
Conserver la **correspondance entre document source et objets dérivés** : chunks, vecteurs, caches et éventuelles copies. Un événement de suppression déclenche leur retrait ; un marqueur de suppression versionné peut empêcher qu'une ancienne mise à jour ressuscite le document.

Exemple : la suppression de `doc-17` retire ses 12 vecteurs et écrit un marqueur « supprimé en version 9 », qui fait rejeter une version 8 rejouée plus tard. Conserver ce marqueur aussi longtemps qu'un rejeu reste possible. Les changements de droits peuvent aussi exiger un retrait ou un filtrage immédiat. Un index rafraîchi uniquement par ajout finit par servir des documents supprimés ou devenus inaccessibles.

---

Comment organiser un backfill sans perturber l'ingestion courante ? <!--anki:6463613434353731396239313461323561366438326231356339333839393939-->
?
Un **backfill** recalcule un historique selon une version identifiée de la logique. Fixer plage, sources, destination, budget et critères de validation ; découper en partitions reprenables et contrôler la charge.

Exemple : recalculer 18 mois d'embeddings par partition mensuelle, dans un index `v2` séparé, avec au plus 20 % du quota d'appels ; basculer seulement après comparaison des volumes et d'un échantillon de recherches. Un rejeu de données ne doit pas relancer automatiquement des actions métier externes comme l'envoi de messages ou les paiements.

---

Calcul : combien de temps faut-il pour absorber 1,2 million d'événements de retard avec une capacité de 500/s et 300/s de nouvelles arrivées ? <!--anki:3637333265363631346166363463386638636437393863326131376137643531-->
?
Sous hypothèse de débits stables et d'une capacité réellement disponible pour ce flux, le **débit net de rattrapage** vaut 500 − 300 = 200 événements/s.
```text
durée = 1 200 000 / 200 = 6 000 s = 100 min
```
Diviser par 500 oublierait les nouvelles arrivées. Si la capacité est inférieure ou égale au débit entrant, le retard ne se résorbe pas durablement. Ajouter une marge pour retries, tailles variables et limites aval, puis vérifier l'estimation avec l'âge du plus ancien événement restant.

---

Que doit permettre une file de quarantaine pour les événements d'ingestion ? <!--anki:3134323539383962643133623465376261666338626332323930323866663633-->
?
Elle isole les **événements non traitables après la politique de reprise** sans perdre leur contenu ni leur provenance. Conserver identifiant, version, cause, tentatives et référence au schéma, avec des accès adaptés aux données transportées.

Prévoir alertes, propriétaire, correction et rejeu contrôlé. Déplacer un message ne résout pas son erreur et peut casser l'ordre d'une entité : si la version 3 de `commande-88` part en quarantaine, appliquer la 4 publie un état qui saute la 3. Décider si les suivants attendent. Un compteur de quarantaine qui augmente tandis que le pipeline reste vert doit apparaître comme une dégradation de couverture.

---

Pourquoi réconcilier périodiquement la source et la destination malgré la CDC ? <!--anki:6365626330393336663033353433653662393662616164333834623935303332-->
?
Pour détecter les **écarts silencieux** : événement perdu hors rétention, bug de transformation, suppression oubliée, écriture aval rejetée. Exemple : chaque nuit, comparer par jour de création le nombre de lignes et une empreinte agrégée des couples (identifiant, version) ; seule une partition divergente est examinée puis réparée.

Faire la comparaison sur des états compatibles dans le temps ; une source qui continue d'évoluer peut créer de faux écarts. Réparer les objets divergents ou reconstruire une version complète lorsque nécessaire. La réconciliation complète les garanties du flux : « le consommateur n'a plus de retard » ne prouve pas que la destination est correcte.

---

Comment paginer une extraction API qui continue d’évoluer pendant la lecture ? <!--anki:6633313464303738383631643464336538373334383734363432346132633336-->
?
Utiliser le **protocole documenté** : token de continuation, curseur stable ou export de snapshot lorsqu'il existe. Une pagination par offset sur une liste mutable peut répéter ou manquer des objets : si une insertion en tête survient entre `offset=0` et `offset=100`, l'ancien 100e objet revient en page 2 ; une suppression ferait sauter le 101e.

Conserver les paramètres de requête et le curseur après persistance, gérer expiration et relivraisons, puis réconcilier les identités. Une pagination par clé avec ordre total ne garantit pas à elle seule un snapshot cohérent. Ne pas reconstruire un token opaque ; une page courte ou vide n'indique pas la fin si une continuation est fournie.

---

## Mises en situation

Mise en situation : après un arrêt de trois jours, le journal source ne contient plus la position CDC sauvegardée. Comment reprends-tu ? <!--anki:3266343736653662663136633437326561653766643162373337393430326666-->
?
1. **Reconnaître la lacune** : repartir du dernier événement disponible perdrait silencieusement une période.
2. **Évaluer les sauvegardes et archives** pour déterminer si un rejeu complet reste possible.
3. **Sinon reconstruire un snapshot cohérent**, raccordé au journal selon le protocole prévu.
4. **Valider et réconcilier** la nouvelle destination, puis basculer les lecteurs.
5. **Adapter rétention et alertes** à la durée d'indisponibilité que l'équipe doit tolérer.

**Piège** : afficher un retard nul après avoir simplement déplacé le curseur au présent.

---

Mise en situation : un backfill a remis dans l'index des documents supprimés la veille. Quelle correction apportes-tu ? <!--anki:6165356537633730326435373439663062383533323366623565336332353466-->
?
1. **Suspendre l'exposition affectée**, identifier les objets réintroduits et les réponses éventuellement servies.
2. **Reconstituer la chronologie** : snapshot du backfill, positions CDC, versions et tombstones ; ne pas prendre l'heure d'ingestion pour une version métier.
3. **Refuser les écritures anciennes** : une suppression version 9 doit empêcher le rejeu d'un document version 8.
4. **Conserver la preuve de suppression** assez longtemps pour les replays autorisés, ou réconcilier avec une source faisant autorité avant publication.
5. **Réparer index et caches**, puis tester suppression, mise à jour et backfill concurrents, y compris après expiration des tombstones.

**Piège** : supprimer physiquement le document et son marqueur, puis accepter tout objet absent comme nouveau lors du prochain backfill.

---

Mise en situation : le job d'indexation réussit, mais certains documents récents ne sont pas retrouvables. Comment enquêtes-tu ? <!--anki:3432306134386337346531643462653539666434353662316534656662633663-->
?
1. **Suivre leurs identifiants** de la source jusqu'aux chunks et vecteurs publiés.
2. **Examiner les checkpoints**, rejets et accusés de réception aval.
3. **Distinguer écriture et visibilité** : l'index peut accepter une mise à jour avant de la rendre recherchable.
4. **Vérifier versions et filtres** de droits, ainsi que la configuration interrogée.
5. **Réconcilier puis rejouer** les seuls objets manquants, avec un contrôle de recherche après publication.

**Piège** : confondre succès du job, durabilité des données et disponibilité dans les résultats.

---

## Sources
- [Google AIP-158 — pagination et tokens de continuation](https://google.aip.dev/158)
- [Debezium — connecteur PostgreSQL, snapshots et journal de changements](https://debezium.io/documentation/reference/stable/connectors/postgresql.html)
- [Apache Kafka — garanties de livraison et traitement](https://kafka.apache.org/41/design/design/)

## Connexions
- [[157-contrats-qualite-donnees|Contrats & qualité]] — critères de validation et publication
- [[159-donnees-temporelles-features|Données temporelles]] — traiter événements tardifs et disponibilité historique
- [[153-data-flywheel-versioning|Versioning des données]] — versions d'index et sources à rejouer
- [[148-pipelines-batch-llm|Pipelines batch LLM]] — reprendre les traitements volumineux
- [[149-livraison-idempotence-concurrence|Garanties de livraison]] — protéger les reprises et écritures concurrentes
- [[150-013-orchestration-pipelines-donnees|Transformations & orchestration des pipelines data]] — coordonner reprises, partitions et publication
- [[150-014-streaming-traitements-evenements|Streaming & traitements d’événements]] — relier positions source et effets aval
- [[00-moc-ai-engineering|MOC AI Engineering]]
