# Construction de datasets & corpus IA — Flashcards
Tags: #flashcards #ai-engineering #donnees #data-engineering
Vérifié le : 9 octobre 2026 — références techniques et exemples de cette fiche.
<!-- summary: manifestes, identité documentaire, parsing, déduplication et splits, shards, streaming de datasets, shuffle, workers, mélange des sources, filtrage, packing et reprise d’entraînement. -->


Que doit identifier le manifeste d’un dataset d’entraînement ou d’évaluation ? <!--anki:6435646437656139346162653431616139653838636163636131313631653832-->
?
Un **ensemble précis de données**, avec fichiers ou snapshots, empreintes, schéma, volumes et règles de sélection. Relier également code de transformation, versions des sources, split et paramètres qui changent les exemples produits.

Le manifeste permet de vérifier qu'une expérience relit le bon contenu et que tous les shards attendus sont disponibles. Il ne conserve pas lui-même les fichiers : organiser accès et rétention. Les droits d'usage et la provenance doivent être documentés séparément des seules empreintes, qui prouvent une identité de contenu, pas une autorisation de l'utiliser.

---

Pourquoi distinguer document source, texte extrait et exemple tokenisé ? <!--anki:6136333861303865396161393463636561623935383238636630643032326438-->
?
Ce sont des **représentations successives**, chacune susceptible de changer. Le parseur peut perdre un tableau, une normalisation peut supprimer une négation, et le tokenizer ou le template peuvent modifier longueur et structure des exemples.

Conserver les références source et versions de transformations, avec contrôles à chaque frontière. Pour un RAG, garder si utile page ou emplacement pour vérifier les citations ; pour un entraînement, tracer les éléments utilisés pour calculer la loss. Reproduire seulement les fichiers bruts ne garantit pas de reproduire les mêmes tokens ni les mêmes labels.

---

Comment identifier les chunks d’un corpus sans confondre document et version de traitement ? <!--anki:3564316662663534643534643437653362663362633035383030363934613738-->
?
Relier **identité métier du document, version source et version de parsing/chunking** à ses objets dérivés. Un identifiant de chunk peut intégrer ces références et sa position ou son contenu selon une convention stable.

Ne pas confondre une nouvelle version avec une relivraison, ni réutiliser aveuglément des embeddings après changement de texte. Une table document-vers-chunks permet remplacement, suppression et audit. Les droits d'accès doivent suivre le document courant ; une ancienne version techniquement disponible n'est pas automatiquement autorisée à être servie au même utilisateur.

---

Pourquoi contrôler les familles de documents avant de construire les splits d’un corpus IA ? <!--anki:6166373530383964623062383437373139396162353034613032663861386566-->
?
Copies, révisions, traductions et fragments d'une même source peuvent former une **famille corrélée**. Les répartir aléatoirement entre train et test peut mesurer la reconnaissance d'un contenu déjà vu plutôt que la généralisation recherchée.

Définir l'unité de séparation selon le déploiement : famille, client, document ou période. Détecter les recouvrements, décider d'une règle stable et garder le test protégé. Une similarité élevée n'impose pas toujours une fusion : négations et variantes métier peuvent être importantes. Documenter les faux rapprochements et l'effet de la politique sur la couverture.

---

À ne pas confondre : déduplication exacte et rapprochement de quasi-doublons dans un corpus ? <!--anki:3361646632396135306334313431343061613131366437383637626435336134-->
?
La déduplication **exacte** compare une représentation canonique, souvent via hash ; les **quasi-doublons** demandent une mesure de ressemblance, par exemple sur fragments textuels, avec seuil et validation.

Une normalisation trop forte peut rendre identiques « autorisé » et « non autorisé » si elle supprime des éléments décisifs. Une proximité sémantique n'est pas une identité documentaire. Mesurer les erreurs de fusion et de séparation sur un échantillon annoté, puis garder la provenance du représentant et de ses variantes. La politique dépend du but : économiser le calcul, empêcher les fuites ou conserver des répétitions légitimes.

---

Pourquoi construire des vues différentes pour entraînement, évaluation et serving à partir des mêmes sources ? <!--anki:3433643538346237343231643466353338386565643065303062376463653464-->
?
Leurs **contrats diffèrent** : entraînement avec exemples autorisés et labels disponibles, évaluation protégée avec références vérifiées, serving avec fraîcheur et permissions actuelles. Une source commune ne rend pas les trois vues interchangeables.

Partager identités et transformations lorsque pertinent, mais versionner sélection, temporalité et accès de chaque vue. Un exemple utile au débogage peut appartenir au développement et ne plus constituer un test indépendant. Des documents retirés du serving peuvent aussi rester référencés dans des historiques soumis à une politique de conservation distincte, à expliciter.

---

Pourquoi répartir un gros corpus en shards ? <!--anki:3864393532646138383963363439383161633837393465613830333830623564-->
?
Des **shards** sont des morceaux identifiables du dataset que des workers peuvent lire et traiter séparément. Ils facilitent parallélisme, reprise et contrôle de complétude.

Trop de petits shards augmentent les ouvertures et métadonnées ; trop peu de gros shards limitent la répartition et rendent certains rejeux coûteux. Équilibrer selon octets, tokens ou coût de parsing, pas seulement nombre de documents. Un manifeste fixe leur liste et leurs empreintes. Le partitionnement des lecteurs doit empêcher qu'un même shard soit oublié ou consommé involontairement plusieurs fois.

---

À ne pas confondre : streaming d’un dataset d’entraînement et traitement d’un flux événementiel ? <!--anki:6163333033326639383231633435356161326438333864333464346634316166-->
?
Le **streaming de dataset** lit progressivement des exemples sans tout télécharger ou charger en mémoire ; le dataset peut être borné et figé. Un **flux événementiel** décrit des données qui arrivent au fil du temps, avec politiques de retard, état et mise à jour.

Lire un corpus en streaming ne lui donne donc pas automatiquement des watermarks ou une garantie de fraîcheur. Cela change surtout accès aléatoire, shuffle et reprise du lecteur. Définir si la liste d'objets est figée pendant une époque, faute de quoi deux exécutions peuvent parcourir des populations différentes.

---

Pourquoi un shuffle avec buffer limité n’est-il pas une permutation uniforme de tout le corpus ? <!--anki:6333363564353838383264323439363139393737336166333538383134356634-->
?
Le lecteur choisit parmi un **tampon borné**, alimenté au fil de la lecture. Avec un petit buffer, les exemples proches dans les fichiers peuvent rester corrélés ; le mélange global dépend aussi de l'ordre des shards.

Une graine fixe rend certaines décisions reproductibles dans une configuration donnée, sans garantir un mélange uniforme ni une reprise identique après changement de workers. Examiner langues, sources et longueurs au fil des batches. Adapter taille du tampon et ordre de lecture au budget mémoire et au risque de séquences homogènes pendant l'entraînement.

---

Comment éviter les exemples dupliqués avec plusieurs workers lisant un dataset itérable ? <!--anki:3830393964353066316135353465633961306461643261313462343164666335-->
?
Répartir explicitement **shards ou exemples entre rangs et workers**, selon le framework. Des copies du même itérateur peuvent sinon parcourir les mêmes données. Dans PyTorch, un `IterableDataset` répliqué entre workers doit être configuré pour éviter ces doublons.

Tester identifiants lus, couverture et recouvrements sur un petit corpus avant de monter en charge. Contrôler aussi dernières partitions inégales, nombre d'étapes et comportement en cas de worker défaillant. Certains samplers complètent ou tronquent des données pour équilibrer les rangs ; ce comportement doit être choisi et mesuré.

---

Quel état de lecture faut-il envisager pour reprendre fidèlement un entraînement ? <!--anki:3533353633613665303635303465366462383365303936616664623361303730-->
?
Au-delà du modèle et de l'optimiseur, considérer **version du dataset, progression du sampler ou des shards, graines et état du mélange**. Des buffers et préchargements peuvent avancer la lecture au-delà du dernier batch effectivement consommé.

La reprise exacte dépend des possibilités du lecteur et du framework ; conserver une graine seule ne suffit pas toujours. Définir si quelques exemples répétés ou sautés sont acceptables, puis tester le protocole avec identifiants d'exemples. Changer nombre de workers, ordre des fichiers ou code de transformation peut modifier la séquence, même avec les mêmes poids restaurés.

---

Pourquoi définir le mélange d’un corpus en tokens ou en poids, pas seulement en nombre de documents ? <!--anki:3232343231323664636232393461613961373837633435306161613264303231-->
?
Des documents de longueurs différentes contribuent très différemment au **nombre de tokens et au calcul de loss**. Une source minoritaire en documents peut dominer l'entraînement si ses textes sont longs ou si elle est rééchantillonnée.

Définir l'unité de mélange, la pondération, la gestion des répétitions et le budget par source. Vérifier aussi les segments importants mais rares. Un mélange choisi pour améliorer une capacité ne représente pas automatiquement le trafic d'évaluation ; conserver une mesure distincte sur la population visée et analyser les régressions.

---

Calcul : un corpus contient 1 000 documents A de 100 tokens et 1 000 documents B de 900 tokens, chacun lu une fois sans troncature. Quelle part des documents et des tokens vient de B ? <!--anki:6462356638376464316534313436393162623638383963353337323839313762-->
?
Les deux dénominateurs donnent des réponses différentes :
```text
part des documents B = 1 000 / 2 000 = 50 %
tokens A = 100 000 ; tokens B = 900 000
part des tokens B = 900 000 / 1 000 000 = 90 %
```
Avec une loss moyennée uniformément sur ces tokens non masqués, B contribue beaucoup plus que ne le suggère le comptage des documents. Masquage, packing, troncature ou pondération changent cette contribution. Fixer l'unité visée avant d'annoncer qu'un corpus est équilibré.

---

Comment contrôler qu’un filtrage de qualité n’appauvrit pas excessivement un corpus ? <!--anki:6337653966306332613463373464356339353162396138333063666135316135-->
?
Mesurer **ce qui est retiré et conservé par segment** : langues, sources, longueurs, formats et cas difficiles. Un filtre entraîné sur un style dominant peut éliminer des textes valides plus souvent dans d'autres groupes.

Annoter un échantillon de rejets et d'acceptations, versionner les règles et comparer le modèle sur les capacités recherchées. Un taux de rejet élevé n'est pas une preuve de qualité. Conserver les compteurs et motifs nécessaires au diagnostic, avec une politique adaptée pour les contenus rejetés ; tout conserver indéfiniment n'est pas requis pour tracer le filtrage.

---

Pourquoi packing et troncature font-ils partie du contrat de données d’entraînement ? <!--anki:3331313130373163333037393436333738333337353664353334383661653766-->
?
Le **packing** regroupe plusieurs exemples dans une séquence ; la **troncature** retire des tokens au-delà d'une limite. Ils modifient frontières, proportions et parfois cible réellement apprise.

Vérifier séparateurs, masques de loss et d'attention selon l'objectif. Sans isolation prévue, un exemple peut utiliser le contexte d'un autre ; une troncature peut retirer la réponse tout en conservant la question. Mesurer tokens utiles, exemples tronqués et segments touchés. Une meilleure occupation GPU ne garantit pas un dataset équivalent : comparer apprentissage et évaluation après changement de préparation.

---

## Mises en situation

Mise en situation : doubler les workers double presque les exemples lus par époque, alors que le manifeste ne change pas. Que vérifies-tu ? <!--anki:3662643934313736323438393439643638393361356364336135356562396335-->
?
1. **Collecter les identifiants lus** sur un petit corpus contrôlé.
2. **Examiner le partage entre rangs et workers**, surtout pour les itérateurs répliqués.
3. **Vérifier padding, répétition et critères de fin d'époque** du sampler.
4. **Corriger la répartition** puis mesurer couverture et intersection des lectures.
5. **Recalculer le budget de tokens** et les résultats d'entraînement affectés.

**Piège** : considérer le nombre de batches comme une preuve du nombre d'exemples distincts.

---

Mise en situation : une nouvelle version du parseur améliore les tableaux mais fait chuter les réponses sur les contrats scannés. Comment l’évalues-tu ? <!--anki:6462623731663332343139613434663761313937643937616133373962396434-->
?
1. **Comparer les versions sur des documents identiques**, avec références d'extraction.
2. **Segmenter par type de document**, langue et qualité de scan.
3. **Examiner les pertes de structure ou de texte**, puis les chunks et tokens dérivés.
4. **Reconstruire un corpus candidat versionné** et rejouer les évaluations aval.
5. **Publier après validation**, avec possibilité de retour à la version précédente.

**Piège** : remplacer le parseur globalement sur la base d'un seul score moyen.

---

Mise en situation : le score d’évaluation augmente fortement après ingestion de nouvelles documentations presque identiques aux questions de test. Comment réagis-tu ? <!--anki:3266613563346337306432363434623261373062366564376532636164343530-->
?
1. **Rechercher les recouvrements et familles communes** entre sources, entraînement et test.
2. **Distinguer accès autorisé au corpus RAG et fuite de réponses**, selon ce que le test mesure.
3. **Isoler les données contaminées** et documenter la règle de séparation.
4. **Recalculer les scores sur un test indépendant adapté** au déploiement visé.
5. **Versionner l'incident et prévenir la récidive** par contrôles de provenance et de similitude.

**Piège** : déclarer toute présence d'un document dans le RAG comme une fuite, ou tout gain comme une amélioration de généralisation.

---

## Sources
- [Hugging Face Datasets — streaming, shards, mélange et reprise](https://huggingface.co/docs/datasets/stream)
- [PyTorch — chargement et datasets itérables](https://docs.pytorch.org/docs/2.14/data.html)
- [Lee et al. — déduplication des données d’entraînement](https://arxiv.org/abs/2107.06499)
- [Apache Arrow — représentation colonnaire et échanges](https://arrow.apache.org/docs/format/Columnar.html)

## Connexions
- [[151-donnees-curation-annotation|Curation & annotation]] — relier qualité éditoriale et construction du corpus
- [[153-data-flywheel-versioning|Versioning des données]] — fixer contenu, transformations et conservation
- [[162-document-parsing|Parsing documentaire]] — contrôler les représentations dérivées
- [[150-012-stockage-colonnaire-lakehouse|Stockage analytique]] — organiser et lire les shards efficacement
- [[150-016-observabilite-lignage-donnees|Lignage des données]] — retrouver les sources et consommateurs affectés
- [[172-validation-metriques-ml|Validation ML]] — protéger les splits et mesurer la généralisation
- [[00-moc-ai-engineering|MOC AI Engineering]]
