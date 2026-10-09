# Contrats, schémas & qualité des données — Flashcards
Tags: #flashcards #ai-engineering #donnees #data-engineering #qualite
<!-- summary: contrat producteur-consommateur, contraintes de schéma et métier, fraîcheur et complétude, compatibilité, migrations, quarantaine, dérive ou incident, publication atomique et lignage opérationnel. -->


Que doit garantir un contrat de données pour un système IA ? <!--anki:6465333362376365616461653439353861633730323038363164306534316230-->
?
Un **accord explicite entre producteur et consommateurs** sur le sens, le format et les conditions de livraison des données. Il précise unités, clés, valeurs admises, fraîcheur, responsabilité et procédure de changement.

Pour un champ `montant`, connaître son type numérique ne suffit pas : devise, taxes et unité monétaire changent son interprétation. Le contrat doit être vérifiable par des contrôles et assorti d'une réaction aux violations. Il ne garantit pas automatiquement la véracité métier ; des données parfaitement conformes au schéma peuvent rester fausses.

---

À ne pas confondre : validation de schéma et validation métier des données ? <!--anki:6138383865616161643339643433346561333131653265316532313630383136-->
?
Le **schéma** décrit la structure : types, champs requis, formats et nullabilité. La **validation métier** vérifie des relations et invariants : une date de clôture suit l'ouverture, une somme de lignes correspond au total, une clé référence une entité existante.

Les deux se complètent. Un entier positif peut représenter un montant mal converti de centimes en euros. Certains contrôles sont locaux à une ligne ; d'autres exigent une table de référence ou plusieurs événements. Définir leur coût et le moment où ils bloquent la publication.

---

Pourquoi fraîcheur, complétude et exactitude sont-elles trois dimensions distinctes ? <!--anki:3031626665393639653539653439356162396231393561646139346162343262-->
?
La **fraîcheur** mesure le retard par rapport au besoin ; la **complétude** vérifie que les éléments attendus sont présents ; l'**exactitude** concerne leur conformité à la réalité. Un lot récent peut oublier un client sur deux, tandis qu'un lot complet peut contenir des valeurs anciennes.

Suivre séparément heure du dernier succès, âge des données, volumes attendus et échantillons vérifiés. Un job vert prouve seulement qu'il a terminé selon ses règles. Sans manifestes, compteurs source ou autre référence, une absence de données peut passer pour une absence d'activité.

---

Comment distinguer absence de données et valeur métier nulle ? <!--anki:6230396462373461656333613439363361623231343539313330326430653438-->
?
Donner une **sémantique explicite** aux valeurs manquantes : inconnu, non applicable, pas encore reçu ou véritable zéro. Un compteur de zéro commandes ne doit pas être identique à un compteur impossible à calculer parce qu'une partition manque.

Conserver un indicateur de disponibilité ou un statut de calcul et définir le comportement du consommateur : attendre, s'abstenir ou utiliser une valeur de secours. Une imputation silencieuse peut masquer un incident de collecte et entraîner le modèle sur des exemples dont le sens a changé.

---

À ne pas confondre : compatibilité backward et forward d'un schéma ? <!--anki:3133663165663634643834393432643362653636396334656238636433326630-->
?
La compatibilité **backward** permet au nouveau lecteur de lire les anciennes données. La compatibilité **forward** permet à l'ancien lecteur de lire les nouvelles. Le comportement dépend du format, des valeurs par défaut et des règles de résolution ; ajouter un champ n'est donc pas toujours inoffensif.

Lister les versions de producteurs et consommateurs qui vont coexister et tester leurs combinaisons. Une vérification contre la seule version précédente ne garantit pas la compatibilité avec tout l'historique. Renommer un champ métier nécessite aussi de préserver son sens, pas seulement de satisfaire le registre.

---

Comment migrer un champ de données sans casser tous ses consommateurs ? <!--anki:6335316261383337393062343465383938393436346631616438333937623233-->
?
Utiliser une migration **ajouter, migrer, retirer** : introduire la nouvelle représentation, rendre les consommateurs capables de la lire, vérifier leur bascule, puis retirer l'ancienne après la période convenue.

Par exemple, conserver temporairement `montant_centimes` et `montant_decimal` avec une règle de conversion explicite. Éviter une double écriture indépendante qui laisse les deux valeurs diverger. Contrôler les anciens clients, les historiques rejoués et les modèles entraînés avec l'ancien format avant suppression. Un schéma compatible ne rend pas automatiquement compatibles les calculs métier.

---

Quand mettre les données invalides en quarantaine plutôt que bloquer tout le pipeline ? <!--anki:6136653135653135613963633434316239643432643337643832613335623462-->
?
Quand isoler les erreurs permet de publier un résultat encore **cohérent et acceptable**. Conserver l'enregistrement brut, la raison du rejet, sa provenance et une procédure de correction puis de rejeu.

La politique dépend de la criticité : quelques descriptions mal formées peuvent être exclues d'un index, mais une table incomplète peut rendre un calcul global faux. Mesurer et annoncer la couverture publiée. Fixer un seuil d'arrêt et alerter ; jeter silencieusement les lignes invalides peut créer un biais systématique sur certains clients ou formats.

---

Comment distinguer une dérive réelle des données d'un incident de pipeline ? <!--anki:3164633539376233396434623437643362343339326231636562646233353530-->
?
Une dérive peut refléter une **évolution de la population**, alors qu'un incident altère sa représentation : unité modifiée, jointure cassée, source manquante. Vérifier d'abord schémas, volumes, taux de nulls, versions et déploiements amont.

Comparer les segments touchés aux changements connus et aux données brutes. Si seule une source bascule soudainement, réparer la collecte avant de réentraîner. Une distance statistique signale un changement, pas sa cause ni son impact métier. Confirmer ensuite si la qualité prédictive est réellement affectée.

---

Pourquoi publier un dataset via une version validée plutôt qu'écraser les fichiers en place ? <!--anki:6434356532326163356364613438613739386331646336616333326136393261-->
?
Un consommateur pourrait lire un **mélange de versions** pendant l'écriture. Construire un snapshot, vérifier son contenu puis basculer atomiquement un pointeur ou un manifeste permet de rendre visible un ensemble cohérent.

La garantie dépend du stockage : il faut une primitive de publication adaptée, pas supposer qu'un répertoire est transactionnel. Conserver la version précédente facilite le retour arrière. Les manifestes doivent désigner des objets immuables ou identifiés par empreinte pour qu'une même version ne change pas sous les lecteurs.

---

Quel lignage conserver pour diagnostiquer une mauvaise donnée dans une prédiction ? <!--anki:6264366563326330353664343466303638643639326162316338643630643833-->
?
Relier **source et version, transformations et configuration, dataset publié et consommateur**. Pour une prédiction, enregistrer les références utiles vers les variables ou documents effectivement utilisés, avec l'heure et la version du modèle.

Cela permet de retrouver les résultats affectés par un lot corrompu et de rejouer seulement les traitements concernés. Un simple nom de table « courante » ne suffit pas si son contenu a changé. Adapter la granularité du lignage au diagnostic nécessaire et à la confidentialité, sans dupliquer toutes les données sensibles dans les logs.

---

Calcul : 9 800 documents sont publiés sur 10 000 attendus. Peut-on annoncer un pipeline fiable à 98 % ? <!--anki:3761646434663031373663633438303138333331376636383665306564313336-->
?
On peut annoncer une **complétude de 98 % pour ce lot**, si le dénominateur est établi et si les identifiants sont uniques. Ce chiffre ne mesure ni fraîcheur, ni exactitude, ni disponibilité du service.

Les 200 absents peuvent appartenir au même client et rendre son expérience inutilisable. Examiner leur répartition et la criticité des documents, puis décider si la publication partielle est acceptable. Compter uniquement les documents reçus aurait caché les absents ; il faut une référence des objets attendus, pas seulement des succès traités.

---

## Mises en situation

Mise en situation : toutes les prédictions de montant sont multipliées par cent après une livraison de données, mais aucun type n'a changé. Comment réagis-tu ? <!--anki:3138663766646436623263653462613839303930316363366363353533326132-->
?
1. **Suspendre l'usage affecté** ou revenir à une version validée selon le risque métier.
2. **Comparer les données brutes** et les changements amont : devise, unité, taxes, conversion.
3. **Corriger le contrat** avec une unité explicite et des exemples de référence.
4. **Ajouter des contrôles** de cohérence et de distribution capables de détecter ce changement.
5. **Identifier les résultats concernés** par le lignage et organiser leur recalcul.

**Piège** : réentraîner pour absorber une conversion incorrecte et pérenniser l'incident.

---

Mise en situation : ton ingestion rejette 2 % des documents et reste verte, mais tous viennent du même client. Que changes-tu ? <!--anki:3266396664343830323135643462646539356334383530326634613536336536-->
?
1. **Mesurer la couverture par client**, pas seulement le taux global de succès.
2. **Inspecter les rejets conservés** pour déterminer si le problème vient du format ou de la collecte.
3. **Définir un seuil par segment** et un statut explicite de publication partielle.
4. **Corriger puis rejouer** les documents sans dupliquer ceux déjà publiés.
5. **Vérifier l'impact produit**, notamment les réponses construites sans les documents manquants.

**Piège** : abaisser le seuil d'alerte pour améliorer le dashboard sans réparer la couverture.

---

Mise en situation : un producteur veut supprimer demain une colonne que plusieurs modèles utilisent. Comment organises-tu la migration ? <!--anki:3532383236393165306433653436666361323931643638666530343663653264-->
?
1. **Recenser les consommateurs** avec le lignage, y compris entraînements historiques et jobs rarement exécutés.
2. **Définir la représentation cible** et les règles de conversion ou de remplacement.
3. **Introduire une période compatible** et tester ancienne et nouvelle lecture sur des données réelles.
4. **Versionner les pipelines et modèles** puis valider leur comportement avant bascule.
5. **Retirer l'ancien champ** après confirmation des migrations et de la possibilité de rejeu.

**Piège** : vérifier seulement que les services démarrent, sans tester les valeurs produites.

---

## Sources
- [TensorFlow Data Validation — contrôles de données, schémas et différences de distribution](https://www.tensorflow.org/tfx/guide/tfdv)
- [Confluent — évolution et compatibilité des schémas](https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html)

## Connexions
- [[158-ingestion-cdc-backfills|Ingestion & reprises]] — faire respecter le contrat pendant la collecte
- [[159-donnees-temporelles-features|Données temporelles]] — définir disponibilité et fraîcheur des variables
- [[151-donnees-curation-annotation|Curation & annotation]] — compléter la qualité éditoriale par des garanties opérationnelles
- [[153-data-flywheel-versioning|Versioning des données]] — publier et tracer des versions cohérentes
- [[113-monitoring-drift-feedback|Drift & feedback]] — distinguer changement de population et défaut de collecte
- [[150-010-modelisation-donnees-analytiques|Modélisation des données analytiques]] — définir grain, clés et sens des mesures
- [[150-012-stockage-colonnaire-lakehouse|Stockage colonnaire, partitions & lakehouse]] — publier un état cohérent et lisible
- [[150-016-observabilite-lignage-donnees|Observabilité, lignage & exploitation des données]] — mesurer les garanties publiées
- [[00-moc-ai-engineering|MOC AI Engineering]]
