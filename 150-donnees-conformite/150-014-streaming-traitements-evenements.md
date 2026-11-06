# Streaming & traitements d’événements — Flashcards
Tags: #flashcards #ai-engineering #donnees #data-engineering
Vérifié le : 9 octobre 2026 — références techniques et exemples de cette fiche.
<!-- summary: batch et micro-batch, partitions et ordre, groupes de consommateurs, fenêtres, triggers, watermarks, jointures de flux, changelog, état, checkpoints, backpressure et reprise. -->


Quand choisir batch, micro-batch ou traitement continu d’événements ? <!--anki:3032656162643734663865393465663462333830356134323166643563383435-->
?
Partir du **délai utile au produit**, du volume et du coût d'exploitation. Le batch traite un ensemble borné ; le micro-batch traite des lots fréquents ; le continu réagit au fil du flux, avec état et garanties propres au moteur.

Exemple : un score de fraude doit répondre en moins d'une seconde pendant le paiement, ce qui justifie le continu ; des recommandations rafraîchies toutes les 15 minutes se contentent d'un micro-batch. Le continu complexifie retards, reprises et résultats provisoires. Mesurer le délai source-à-consommateur, pas seulement la durée d'un opérateur. « Temps réel » doit correspondre à un objectif chiffré.

---

Que garantit l’ordre d’une partition de journal, et que ne garantit-il pas ? <!--anki:6338326166653738356564373431306239633834633264626662613233656530-->
?
Un journal partitionné peut garantir un **ordre à l'intérieur d'une partition**, selon son protocole. Il ne crée pas automatiquement d'ordre global entre partitions, ni d'ordre métier entre événements produits tardivement.

Choisir une clé d'entité lorsque ses événements doivent rester ensemble. Le traitement asynchrone aval peut encore inverser les effets si plusieurs requêtes terminent dans un autre ordre. Conserver versions et identités, puis définir les opérations autorisées hors ordre. Changer le partitionnement demande une transition : passer de 12 à 24 partitions change le résultat de `hash(clé) mod n`, et les nouveaux événements d'une commande peuvent précéder les anciens, restés dans l'autre partition.

---

Calcul : un topic Kafka possède douze partitions et un groupe de consommateurs classique compte vingt consommateurs. Combien peuvent recevoir des partitions simultanément ? <!--anki:6532383739336361653033623437306362366538366338656566653239313336-->
?
Dans ce modèle d'assignation, une partition est attribuée à **un seul consommateur du groupe à la fois** : au plus douze consommateurs reçoivent des partitions, et au moins huit restent sans partition.

Un consommateur peut en recevoir plusieurs lorsqu'ils sont moins nombreux. Ajouter des consommateurs au-delà de douze n'augmente donc pas ce parallélisme. Cette règle concerne le groupe classique et l'assignation des partitions ; d'autres modes de consommation ont des garanties différentes. Même avec douze consommateurs actifs, une partition chaude peut limiter le débit total.

---

Comment les fenêtres fixes, glissantes et de session regroupent-elles un flux ? <!--anki:3833623466353637333465303431623061363064646663626166653561633631-->
?
Une **fenêtre fixe** découpe le temps en intervalles adjacents ; une **fenêtre glissante** peut faire appartenir un événement à plusieurs intervalles ; une **session** regroupe des événements séparés par moins qu'un délai d'inactivité défini.

Choisir selon la question métier, les bornes et la clé de regroupement. Un événement tardif peut relier deux sessions : avec 30 minutes d'inactivité, des clics à 10 h 00, 10 h 20 et 11 h 05 forment deux sessions, qu'un clic arrivé en retard, horodaté 10 h 45, fusionne. La fenêtre indique quels événements sont regroupés ; elle ne suffit pas à définir quand le résultat est émis, corrigé ou considéré comme final.

---

Calcul : des fenêtres de dix minutes commencent toutes les cinq minutes, avec bornes [début, fin). À quelles fenêtres appartient un événement horodaté 12 h 07 ? <!--anki:6535616138623262613361353438366339613530623432373863356535326261-->
?
Il appartient aux deux fenêtres dont les bornes l'encadrent :
```text
[12:00, 12:10)
[12:05, 12:15)
```
Il n'appartient pas à [11:55, 12:05) ni à [12:10, 12:20). Un compteur glissant peut donc compter le même événement dans plusieurs résultats, sans qu'il s'agisse d'un doublon de livraison. Additionner ces résultats comme s'ils étaient disjoints serait incorrect. L'horodatage d'arrivée et le watermark influencent la publication et les corrections, pas ces appartenances définies par le temps événement.

---

À ne pas confondre : fenêtre, watermark et trigger dans un traitement de flux ? <!--anki:6333633636626131613736393438643661656432656664396638316332353835-->
?
La **fenêtre** détermine le regroupement des événements ; le **watermark** estime la progression du temps événement ; le **trigger** règle quand émettre un résultat. Un même regroupement peut produire un premier résultat rapide puis des corrections.

Exemple : fenêtre fixe d'une heure, résultat provisoire chaque minute, résultat principal quand le watermark dépasse la fin de l'heure, puis corrections pendant dix minutes de retard autorisé. Définir aussi le mode d'accumulation : réémettre un total cumulatif n'a pas la même signification qu'émettre seulement les nouveaux éléments. Les consommateurs doivent savoir remplacer, additionner ou rétracter selon ce contrat. Aucun nom de fenêtre ne garantit à lui seul qu'un résultat publié est définitif.

---

Pourquoi une entrée inactive peut-elle bloquer la progression d’un traitement multi-flux ? <!--anki:3035626635653535376633663436623961303863376330656630623633346639-->
?
Le moteur peut combiner les progrès des entrées de manière **conservatrice**, par exemple avec le minimum des watermarks actifs. Si onze partitions sont à 12 h 00 et qu'une douzième, silencieuse, reste à 9 h 00, le watermark global vaut 9 h 00 et aucune fenêtre postérieure ne se ferme.

Configurer la détection d'inactivité selon les garanties du moteur, par exemple dans Flink :
```java
WatermarkStrategy.forBoundedOutOfOrderness(Duration.ofSeconds(5))
                 .withIdleness(Duration.ofMinutes(1));
```
Une entrée silencieuse n'est pas forcément définitivement terminée : à sa reprise, ses événements peuvent être tardifs. Surveiller watermarks par entrée, silence attendu et événements corrigés ou rejetés. Forcer la progression change le compromis entre délai et complétude.

---

Pourquoi une jointure entre deux flux a-t-elle besoin de bornes temporelles ou d’une politique d’état ? <!--anki:3232376662396132363561343434373438633837353838316139363563303139-->
?
Pour rapprocher des événements futurs, le traitement doit **retenir les événements sans correspondance**. Sans borne ou règle de nettoyage, cet état peut croître indéfiniment sur des flux non bornés.

Définir clé, intervalle de correspondance, retard accepté et sort des objets qui ne trouvent jamais de partenaire. En Flink SQL, une jointure d'intervalle borne cet état :
```sql
SELECT c.id, p.montant FROM commandes c, paiements p
WHERE c.id = p.commande_id
  AND p.ts BETWEEN c.ts AND c.ts + INTERVAL '2' HOUR;
```
L'intervalle porte sur les timestamps ; la purge dépend des attributs temporels et de la progression des watermarks, pas de deux heures murales garanties. Supprimer trop tôt perd des associations ; conserver sans limite alourdit checkpoints et reprises. Mesurer taille d'état, restauration et non-correspondances.

---

À ne pas confondre : flux append-only, upsert et rétraction ? <!--anki:3661653836633737643534383434623862646332663462613139646337613366-->
?
**Append-only** ajoute des faits ; **upsert** remplace l'état d'une clé ; **rétraction** retire l'effet d'un résultat précédent.

Exemple : un total de fenêtre passe de 10 à 12. Un upsert publie la nouvelle valeur **12** ; une logique différentielle peut retirer 10 puis ajouter 12, ou publier un delta **+2**. Additionner les deux totaux comme des événements indépendants donnerait 22 à tort.

Le contrat précise clé, version, ordre et sens des messages. Un upsert tardif plus ancien ne doit pas écraser l'état récent. Sur une destination append-only, conserver un journal versionné et reconstruire l'état ; ajouter des lignes sans cette règle ne représente pas correctement les corrections.

---

De quoi dépend une garantie exactly-once de bout en bout dans un pipeline de flux ? <!--anki:3366303631323961383065643464383062383064633464343138646561363135-->
?
Il faut coordonner **positions source, état du traitement et publication des sorties**, avec sources rejouables et destinations compatibles. Les checkpoints du moteur peuvent restaurer un état cohérent sans empêcher tous les appels externes répétés.

Une écriture transactionnelle, une déduplication ou un upsert idempotent peut couvrir la destination. Exemple : en mode exactly-once, le sink Kafka de Flink valide sa transaction à la fin du checkpoint ; un lecteur en `read_committed` ne voit pas les sorties d'un checkpoint abandonné. Un appel HTTP à un système sans clé d'idempotence n'est pas couvert automatiquement. Exactly-once décrit un effet observable garanti dans un périmètre, pas nécessairement une unique exécution physique de chaque fonction.

---

Quel compromis crée une durée de conservation de l’état de déduplication ? <!--anki:6237356261333736383630393461316662643363313136663436343464663136-->
?
Une **TTL** borne les identifiants conservés et le coût mémoire, mais un doublon rejoué après leur expiration peut ne plus être reconnu. La bonne durée dépend des retards, de la rétention source et des horizons de rejeu.

Exemple : avec une TTL de 24 h, rejouer sept jours du topic après un incident fait repasser six jours d'événements comme nouveaux. Distinguer TTL technique et validité métier. Pour un effet durable, une protection persistante dans la destination peut être nécessaire. Documenter aussi quel temps pilote l'expiration, car temps événement et temps de traitement divergent pendant une panne. Tester un rejeu au-delà de la TTL et annoncer la garantie réellement obtenue.

---

Qu’est-ce que la backpressure dans un pipeline de streaming ? <!--anki:6665393562616132383462663461613838303732396565386537313065636431-->
?
Un opérateur aval trop lent **ralentit ses producteurs** ou fait croître des files, selon le mécanisme de régulation. C'est un signal de déséquilibre de capacité, pas nécessairement un défaut de la source.

Mesurer débit, retard, files, état et temps d'attente pour localiser le goulot. Exemple dans Flink : l'opérateur qui appelle une API d'embeddings affiche `busyTimeMsPerSecond` proche de 1 000, et tous ceux en amont sont en backpressure ; c'est lui qu'il faut traiter. Augmenter les buffers reporte la saturation et peut aggraver la mémoire ou la latence. Jeter des événements pour tenir la charge change la complétude et ne doit pas rester invisible.

---

Que vérifier avant de redimensionner un traitement avec état ? <!--anki:3266383737393736363035373433643839666335373665666334633266626265-->
?
Vérifier **redistribution des clés, compatibilité de l'état sauvegardé et protocole de reprise**. Le moteur doit retrouver l'état correct de chaque clé après changement de parallélisme ; des identifiants d'opérateurs instables ou un schéma incompatible peuvent empêcher la restauration.

Exemple dans Flink : l'état est réparti en groupes de clés fixés par le parallélisme maximal, au moins 128 par défaut ; on redimensionne sous cette limite depuis un savepoint, mais la modifier rend l'état incompatible, et un opérateur sans `uid()` stable peut ne pas retrouver le sien. Mesurer le temps de restauration et la capacité de rattrapage avant d'annoncer qu'un redimensionnement résout immédiatement la saturation.

---

Calcul : un traitement conserve deux millions de clés, chacune avec 160 octets d’état utile. Quel volume brut, puis avec une hypothèse de facteur deux pour les surcoûts ? <!--anki:3230616635333332386330373438343662326364653463326336633233366261-->
?
En unités décimales :
```text
état utile = 2 000 000 × 160 = 320 000 000 octets = 320 Mo
avec facteur 2 = 640 Mo
```
Le facteur deux est pédagogique, pas une caractéristique garantie d'un moteur. Ajouter buffers, sérialisation, index, checkpoints et état temporaire de restauration selon l'implémentation. La taille des clés actives, leur durée de vie et les événements sans correspondance déterminent l'évolution. Une mémoire stable en régime normal ne suffit pas à garantir une reprise après plusieurs heures de retard.

---

## Mises en situation

Mise en situation : un agrégat de ventes vaut dix, puis douze après un événement tardif ; le dashboard affiche vingt-deux. Où cherches-tu l’erreur ? <!--anki:3339623237376533666462643433313438653133366233376430313762376233-->
?
1. **Identifier la sémantique de sortie** : total cumulatif, delta ou rétraction.
2. **Vérifier clé de fenêtre et version** dans le consommateur.
3. **Appliquer remplacement ou correction appropriée**, au lieu d'une addition systématique.
4. **Tester doublon, désordre et correction tardive** avec résultats attendus.
5. **Réconcilier les agrégats publiés** avec une reconstruction de référence.

**Piège** : supprimer les événements tardifs pour cacher un contrat de consommation incorrect.

---

Mise en situation : les fenêtres ne se ferment plus depuis qu’une partition source est silencieuse. Comment rétablis-tu le traitement ? <!--anki:6337646366343165666334363435393961653163393231373838316561363933-->
?
1. **Observer les watermarks par entrée** et localiser celle qui bloque.
2. **Distinguer inactivité attendue et panne** de collecte.
3. **Configurer l'inactivité ou réparer la source** selon le contrat et le moteur.
4. **Définir le sort des événements à la reprise**, potentiellement hors délai.
5. **Vérifier complétude et corrections**, pas uniquement la baisse de latence.

**Piège** : avancer artificiellement le watermark sans mesurer les données que cela peut exclure.

---

Mise en situation : les checkpoints réussissent, mais un redémarrage du job duplique des appels à une API d’enrichissement. Pourquoi et que changes-tu ? <!--anki:6132626662613634643666323433343362333361366639363239306232373638-->
?
1. **Délimiter la garantie du checkpoint** : état interne ou effets externes inclus.
2. **Identifier les appels acceptés avant la panne** mais non enregistrés localement.
3. **Utiliser une clé d'idempotence si disponible**, ou un protocole de résultat durable et de réconciliation.
4. **Séparer enrichissement et publication**, avec reprise et quotas maîtrisés.
5. **Injecter une panne à cette frontière** et mesurer effets répétés et coût résiduel.

**Piège** : déduire l'unicité des effets HTTP d'un indicateur exactly-once du moteur.

---

## Sources
- [Apache Beam — fenêtres, watermarks, triggers et état](https://beam.apache.org/documentation/programming-guide/)
- [Apache Kafka — partitions et groupes de consommateurs](https://kafka.apache.org/10/documentation/)
- [Apache Flink — état et tolérance aux pannes](https://nightlies.apache.org/flink/flink-docs-stable/docs/learn-flink/fault_tolerance/)

## Connexions
- [[159-donnees-temporelles-features|Données temporelles]] — respecter temps événement, disponibilité et retards
- [[158-ingestion-cdc-backfills|Ingestion & CDC]] — relier positions source et effets aval
- [[149-livraison-idempotence-concurrence|Livraison & idempotence]] — délimiter les garanties de bout en bout
- [[150-013-orchestration-pipelines-donnees|Orchestration data]] — coordonner traitements et reprises
- [[00-moc-ai-engineering|MOC AI Engineering]]
