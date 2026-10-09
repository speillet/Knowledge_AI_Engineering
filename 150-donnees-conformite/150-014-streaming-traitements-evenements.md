# Streaming & traitements d’événements — Flashcards
Tags: #flashcards #ai-engineering #donnees #data-engineering
Vérifié le : 9 octobre 2026 — références techniques et exemples de cette fiche.
<!-- summary: batch et micro-batch, partitions et ordre, groupes de consommateurs, fenêtres, triggers, watermarks, jointures de flux, changelog, état, checkpoints, backpressure et reprise. -->


Quand choisir batch, micro-batch ou traitement continu d’événements ? <!--anki:3032656162643734663865393465663462333830356134323166643563383435-->
?
Partir du **délai utile au produit**, du volume et du coût d'exploitation. Le batch traite un ensemble borné ; le micro-batch traite des lots fréquents ; le continu réagit au fil du flux, avec état et garanties propres au moteur.

Une fraîcheur de quinze minutes peut être satisfaite sans traitement événement par événement. Un besoin de réaction rapide peut le justifier, mais complexifie retards, reprises et résultats provisoires. Mesurer le délai source-à-consommateur, pas seulement la durée d'un opérateur. « Temps réel » doit correspondre à un objectif chiffré.

---

Que garantit l’ordre d’une partition de journal, et que ne garantit-il pas ? <!--anki:6338326166653738356564373431306239633834633264626662613233656530-->
?
Un journal partitionné peut garantir un **ordre à l'intérieur d'une partition**, selon son protocole. Il ne crée pas automatiquement d'ordre global entre partitions, ni d'ordre métier entre événements produits tardivement.

Choisir une clé d'entité lorsque ses événements doivent rester ensemble. Le traitement asynchrone aval peut encore inverser les effets si plusieurs requêtes terminent dans un autre ordre. Conserver versions et identités, puis définir les opérations autorisées hors ordre. Changer le partitionnement ou le routage des clés demande également une stratégie de transition.

---

Calcul : un topic Kafka possède douze partitions et un groupe de consommateurs classique compte vingt consommateurs. Combien peuvent recevoir des partitions simultanément ? <!--anki:6532383739336361653033623437306362366538366338656566653239313336-->
?
Dans ce modèle d'assignation, une partition est attribuée à **un seul consommateur du groupe à la fois** : au plus douze consommateurs reçoivent des partitions, et au moins huit restent sans partition.

Un consommateur peut en recevoir plusieurs lorsqu'ils sont moins nombreux. Ajouter des consommateurs au-delà de douze n'augmente donc pas ce parallélisme. Cette règle concerne le groupe classique et l'assignation des partitions ; d'autres modes de consommation ont des garanties différentes. Même avec douze consommateurs actifs, une partition chaude peut limiter le débit total.

---

Comment les fenêtres fixes, glissantes et de session regroupent-elles un flux ? <!--anki:3833623466353637333465303431623061363064646663626166653561633631-->
?
Une **fenêtre fixe** découpe le temps en intervalles adjacents ; une **fenêtre glissante** peut faire appartenir un événement à plusieurs intervalles ; une **session** regroupe des événements séparés par moins qu'un délai d'inactivité défini.

Choisir selon la question métier, les bornes et la clé de regroupement. Un événement tardif peut modifier une session ou relier deux sessions auparavant séparées, selon la politique retenue. La fenêtre indique quels événements sont regroupés ; elle ne suffit pas à définir quand le résultat est émis, corrigé ou considéré comme final.

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

Définir aussi retard autorisé et mode d'accumulation. Réémettre un total cumulatif n'a pas la même signification qu'émettre seulement les nouveaux éléments. Les consommateurs doivent savoir remplacer, additionner ou rétracter selon ce contrat. Aucun nom de fenêtre ne garantit à lui seul qu'un résultat publié est définitif.

---

Pourquoi une entrée inactive peut-elle bloquer la progression d’un traitement multi-flux ? <!--anki:3035626635653535376633663436623961303863376330656630623633346639-->
?
Le moteur peut combiner les progrès des entrées de manière **conservatrice**, par exemple avec le minimum des watermarks actifs. Une partition qui n'émet plus peut empêcher de finaliser des fenêtres même si les autres avancent.

Configurer la détection d'inactivité selon les garanties du moteur et la nature des sources. Une entrée silencieuse n'est pas forcément définitivement terminée : à sa reprise, ses événements peuvent être tardifs. Surveiller watermarks par entrée, silence attendu et événements corrigés ou rejetés. Forcer la progression change le compromis entre délai et complétude.

---

Pourquoi une jointure entre deux flux a-t-elle besoin de bornes temporelles ou d’une politique d’état ? <!--anki:3232376662396132363561343434373438633837353838316139363563303139-->
?
Pour rapprocher des événements futurs, le traitement doit **retenir les événements sans correspondance**. Sans borne ou règle de nettoyage, cet état peut croître indéfiniment sur des flux non bornés.

Définir clé, intervalle de correspondance, retard accepté et sort des objets qui ne trouvent jamais de partenaire. Une commande et son paiement peuvent demander des heures de conservation. Supprimer l'état trop tôt perd des associations ; le garder sans limite peut rendre les checkpoints et reprises impraticables. Mesurer taille, durée de restauration et taux de non-correspondance.

---

À ne pas confondre : flux append-only, upsert et rétraction ? <!--anki:3661653836633737643534383434623862646332663462613139646337613366-->
?
Un flux **append-only** ajoute de nouveaux faits. Un **upsert** remplace l'état associé à une clé selon une règle de version. Une **rétraction** retire l'effet d'un résultat antérieur, éventuellement avant sa correction.

Un agrégat de fenêtre réémis avec un total de douze après dix ne doit pas toujours être additionné comme un delta de douze. Le consommateur doit connaître clé, version et sémantique des messages. Une destination acceptant seulement des ajouts peut nécessiter un journal de versions et une vue de reconstruction pour représenter les corrections.

---

De quoi dépend une garantie exactly-once de bout en bout dans un pipeline de flux ? <!--anki:3366303631323961383065643464383062383064633464343138646561363135-->
?
Il faut coordonner **positions source, état du traitement et publication des sorties**, avec sources rejouables et destinations compatibles. Les checkpoints du moteur peuvent restaurer un état cohérent sans empêcher tous les appels externes répétés.

Une écriture transactionnelle, une déduplication ou un upsert idempotent peut couvrir la destination selon le protocole. Préciser cette frontière et tester les pannes avant/après commit. Un appel HTTP à un système sans clé d'idempotence n'est pas couvert automatiquement. Exactly-once décrit un effet observable garanti dans un périmètre, pas nécessairement une unique exécution physique de chaque fonction.

---

Quel compromis crée une durée de conservation de l’état de déduplication ? <!--anki:6237356261333736383630393461316662643363313136663436343464663136-->
?
Une **TTL** borne les identifiants conservés et le coût mémoire, mais un doublon rejoué après leur expiration peut ne plus être reconnu. La bonne durée dépend des retards, de la rétention source et des horizons de rejeu.

Distinguer TTL technique et validité métier. Pour un effet durable, une protection persistante dans la destination peut être nécessaire. Documenter aussi quel temps pilote l'expiration, car temps événement et temps de traitement divergent pendant une panne. Tester un rejeu au-delà de la TTL et annoncer la garantie réellement obtenue.

---

Qu’est-ce que la backpressure dans un pipeline de streaming ? <!--anki:6665393562616132383462663461613838303732396565386537313065636431-->
?
Un opérateur aval trop lent **ralentit ses producteurs** ou fait croître des files, selon le mécanisme de régulation. C'est un signal de déséquilibre de capacité, pas nécessairement un défaut de la source.

Mesurer débit, retard, files, état et temps d'attente pour localiser le premier goulot. Augmenter les buffers reporte la saturation et peut aggraver la mémoire ou la latence. Borne de file, admission, ressources et politique de dégradation doivent respecter les garanties métier : jeter des événements change la complétude et ne doit pas rester invisible.

---

Que vérifier avant de redimensionner un traitement avec état ? <!--anki:3266383737393736363035373433643839666335373665666334633266626265-->
?
Vérifier **redistribution des clés, compatibilité de l'état sauvegardé et protocole de reprise**. Le moteur doit retrouver l'état correct de chaque clé après changement de parallélisme ; des identifiants d'opérateurs instables ou un schéma incompatible peuvent empêcher la restauration.

Tester un checkpoint ou savepoint adapté au moteur, le rejeu et la continuité des sorties. Une sauvegarde d'état n'inclut pas nécessairement toutes les dépendances externes. Mesurer le temps de restauration et la capacité de rattrapage avant d'annoncer qu'un redimensionnement résout immédiatement la saturation.

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
