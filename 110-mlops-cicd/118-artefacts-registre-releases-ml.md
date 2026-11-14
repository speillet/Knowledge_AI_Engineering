# Artefacts, registre & releases ML — Flashcards
Tags: #flashcards #ai-engineering #mlops #ml-classique #registre #deploiement
Vérifié le : 12 novembre 2026 — les exemples MLflow ciblent l'API 3 et restent à adapter à la version installée.
<!-- summary: run, modèle journalisé et version enregistrée, paquet d'inférence complet, URI MLflow 3, résolution des alias, intégrité et provenance, sérialisation sûre, chargement en environnement propre, contrat des sorties, predict_proba, approbation, sauvegarde du registre, rétention, conversion, seuils et rollback de release, résolution immuable, dépendance réseau au chargement. -->


À ne pas confondre : run d'expérience, modèle journalisé et version de registre ? <!--anki:6166313136613661653031633431336539323137646439633965333963323364-->
?
Un **run** décrit une exécution : paramètres, données référencées, métriques et artefacts. Un **modèle journalisé** est un objet d'inférence produit ou capturé ; MLflow 3 permet aussi de le journaliser hors d'un run actif. Une **version enregistrée** appartient à un nom de modèle dans le registre et référence un modèle à gouverner.

Un run peut produire plusieurs modèles. Deux versions enregistrées peuvent référencer des contenus identiques ; leur numéro n'est pas une empreinte des poids. Relier ces identités aux rapports et à la release effectivement servie. Aucun numéro de version ne prouve, seul, qualité ou approbation.

---

Que doit contenir une release ML pour reproduire une décision en production ? <!--anki:3735643135303136343033653430333339333963643735633836396461376563-->
?
Le paquet d'inférence doit embarquer ou référencer de façon immuable **prétraitement appris, estimateur, calibrateur et contrat des sorties**. La release ajoute image d'exécution, dépendances, contrat des features, règle de décision et preuves d'approbation.
```text
release → paquet d'inférence + image + features + politique
paquet  → transformations apprises + modèle + calibration
preuves → données + recette + évaluations + approbation
```
Ce schéma est conceptuel, pas un format MLflow imposé. Un scaler « courant » ou un seuil mutable hors manifeste peut changer les décisions sans changement des poids. Le rollback doit retrouver la combinaison compatible, ainsi que ses dépendances encore disponibles et leurs contrôles d'accès.

---

Pourquoi utiliser l'URI retournée par log_model dans MLflow 3 ? <!--anki:3333313239666133343230663465306339623833393732623231666135636566-->
?
MLflow 3 donne aux modèles journalisés leur propre identité. Ne pas déduire leur emplacement à partir d'un ancien chemin d'artefact de run ; utiliser le résultat de la journalisation.
```python
# pipeline ajusté ; signature et exemple préparés en amont
info = mlflow.sklearn.log_model(
    pipeline, name="model", signature=signature,
    input_example=X_example,
)
version = mlflow.register_model(info.model_uri, "retention")
```
L'argument actuel est `name=` ; `artifact_path=` est déprécié pour cette API. Conserver durablement URI du modèle journalisé et version retournée par l'enregistrement. Vérifier ensuite le chargement depuis l'environnement cible : un enregistrement réussi n'exécute pas tous les tests de service et ne constitue pas une promotion.

---

Comment charger un alias de registre sans perdre la version réellement résolue ? <!--anki:6231353339383630633731643436653639616132383565383337336633633732-->
?
Résoudre l'alias **une fois**, puis charger la version explicite obtenue et l'inscrire dans le manifeste de déploiement.
```python
from mlflow import MlflowClient
import mlflow.pyfunc

client = MlflowClient()
mv = client.get_model_version_by_alias("retention", "champion")
uri = f"models:/retention/{mv.version}"
model = mlflow.pyfunc.load_model(uri)
```
Relire l'alias pour journaliser sa cible après avoir chargé via l'alias peut attribuer la mauvaise version si une promotion intervient entre les deux opérations. Ce code réduit cette course ; il ne rend pas le déploiement atomique. Vérifier artefact, image et version effective de chaque réplica, puis définir la politique de transition entre versions et le traitement des requêtes en vol.

---

Pourquoi une empreinte SHA-256 ne suffit-elle pas à autoriser un modèle ? <!--anki:3730663735336135393862613465643439336336643732373965393932353361-->
?
Une **empreinte** permet de vérifier que les octets correspondent à une valeur attendue. Elle ne prouve pas que cette valeur provient d'un producteur autorisé, ni que le modèle a passé les contrôles nécessaires.

Obtenir l'empreinte attendue depuis un manifeste dont la provenance est vérifiée et dont la modification est contrôlée ; relier identité du producteur, recette, dépendances et rapport approuvé. Vérifier les octets chargés, pas seulement un nom de fichier. Un attaquant qui remplace simultanément le fichier et son empreinte dans le même emplacement non protégé conserve une apparence de cohérence. L'intégrité complète une chaîne de confiance, elle ne la crée pas.

---

Quel risque présente le chargement d'un modèle sérialisé avec pickle ou joblib ? <!--anki:6130356338346162393331343438663439383139333566633865306230386230-->
?
Le chargement peut **exécuter du code** : un fichier de modèle n'est pas nécessairement une simple matrice de nombres. Avec les formats fondés sur pickle, ne charger que des artefacts dont la provenance et l'intégrité sont établies, dans un environnement aux droits limités.

Une analyse de fichier ou une extension `.pkl` attendue ne garantit pas l'innocuité. D'autres formats peuvent réduire certains risques, avec des limites propres : types autorisés à examiner, opérateurs supportés, runtime et ressources à contrôler. Le choix du format doit aussi préserver le comportement utile. Un artefact sûr à stocker n'est pas automatiquement sûr à désérialiser.

---

Que doit vérifier un test de chargement dans un environnement propre ? <!--anki:6234346234666338663334323464303161353633336333386137636539313639-->
?
Partir de l'**image cible**, sans état caché du notebook : charger l'artefact publié, importer les transformations personnalisées, puis prédire sur des cas représentatifs et des entrées invalides.

Vérifier versions des bibliothèques, ressources, fichiers externes et dépendances système réellement requises. Comparer sorties et décisions aux références avec tolérances justifiées. Un fichier de dépendances Python ne capture pas nécessairement pilotes, bibliothèques natives et configuration du runtime. scikit-learn ne garantit pas le chargement entre versions différentes. Refaire ce test après une mise à jour de dépendance, même lorsque les poids restent identiques, et conserver l'image ayant passé la vérification.

---

Pourquoi le contrat des sorties doit-il identifier l'ordre des classes et les unités ? <!--anki:3538373461366533333139333464353561333935616338626365623134663931-->
?
Une matrice de probabilités possède un **ordre de colonnes**, pas une signification universelle. Pour un classifieur scikit-learn, relier les colonnes à `classes_` et à une définition versionnée des labels ; ne pas supposer que la deuxième colonne signifie toujours « événement défavorable ».

Documenter aussi unité, horizon, forme, valeurs invalides et transformation inverse éventuelle. Une prévision de logarithme du chiffre d'affaires ne devient pas spontanément une prévision en euros. Tester le contrat avec des cas dont le sens est connu. Une sortie de forme correcte peut être consommée à l'envers sans erreur technique, puis déclencher de mauvaises décisions à grande échelle.

---

Comment éviter de servir des classes quand les consommateurs attendent des probabilités ? <!--anki:3734383833623439346666323439393461616136613066633864336638346464-->
?
Définir explicitement le **mode d'inférence** du paquet et tester ses sorties après rechargement. `predict` et `predict_proba` n'offrent pas le même contrat ; la signature seule ne choisit pas l'intention métier.

Pour le flavor scikit-learn de MLflow, `pyfunc_predict_fn="predict_proba"` permet de choisir cette méthode pour l'interface pyfunc, si l'estimateur la propose. Construire alors la signature depuis ces probabilités, conserver l'ordre des classes et tester l'appel via pyfunc. Cette option n'est pas une propriété universelle de tous les flavors. Modifier seulement le consommateur pour interpréter une classe comme un score crée une erreur silencieuse de décision.

---

À ne pas confondre : version READY, modèle approuvé et service prêt ? <!--anki:3438623433646233636135393465646261616335343232303832353734396437-->
?
Le statut **READY** du registre MLflow indique que la création de la version a abouti. Une **approbation** est une décision de gouvernance fondée sur des preuves et une politique. Un **service prêt** a chargé la release attendue et peut répondre selon ses contrôles opérationnels.

Ces états relèvent de mécanismes différents. Ne pas brancher automatiquement l'exposition au trafic sur la seule fin de l'enregistrement. Vérifier rapport, autorité de promotion, chargement, dépendances et capacité ; exposer l'identité effective dans les diagnostics. Un registre disponible peut contenir un modèle refusé, et une version approuvée peut échouer au démarrage d'un réplica.

---

Que doit prouver un tag d'approbation dans le registre, et comment éviter de le surinterpréter ? <!--anki:3832386564303830383661633434346639383166396433363639643762653837-->
?
Un tag peut **référencer** rapport, décision, responsable et politique appliquée. Sa valeur n'est pas, par elle-même, une preuve infalsifiable ni une règle de contrôle d'accès.

Restreindre qui peut modifier l'approbation et déplacer les alias ; conserver un historique vérifiable relié à la version et aux artefacts exacts. Le processus de déploiement vérifie ces éléments selon sa politique. Un tag copié depuis un ancien candidat ne doit pas approuver de nouveaux octets. Quand une dérogation existe, enregistrer périmètre, expiration et mesure compensatoire. L'approbation doit rester explicable après un incident, même si les tags courants ont changé.

---

Pourquoi sauvegarder la base du registre ne suffit-il pas à restaurer le système ML ? <!--anki:3535323065356363386239613463353738623662373633663435356239636464-->
?
Les **métadonnées** et les **artefacts** peuvent vivre dans des stockages différents : la base décrit runs et versions, tandis que le stockage d'objets contient notamment les fichiers du modèle. Restaurer seulement la base peut laisser des références vers des objets absents.

Définir des sauvegardes compatibles avec la cohérence attendue ; préserver aussi manifests, images, configuration et accès nécessaires, selon des procédures adaptées aux secrets. Tester une restauration isolée : résoudre une version, télécharger ses octets, vérifier leur empreinte, charger puis prédire. L'objectif est de mesurer la capacité de reprise, avec RPO et RTO, pas seulement d'obtenir un écran de registre fonctionnel.

---

Comment définir la rétention des artefacts sans casser un rollback ? <!--anki:3131383336316539306133333436383961333062346132393166636132386566-->
?
Construire la rétention à partir des **références encore nécessaires** : releases servies, retour arrière approuvé, enquêtes et obligations de conservation. Une version ancienne peut rester critique même si aucun alias courant ne la désigne.

Avant suppression, inventorier consommateurs et dépendances ; vérifier qu'images, features et configuration compatibles restent disponibles pour les versions conservées. Prévoir un délai de récupération et tester la restauration. La conservation doit aussi respecter les restrictions applicables aux données embarquées : « tout garder » n'est pas une politique universelle. Supprimer un run ou déplacer un alias n'est pas une démonstration que tous les octets associés peuvent être détruits.

---

Calcul : 30 artefacts de 400 Mio chacun sont référencés depuis trois environnements. Quel stockage faut-il prévoir ? <!--anki:3266393734343236656437633436613338623761333766643339326665373566-->
?
Si les trois environnements **référencent les mêmes objets conservés une seule fois**, le contenu total représente :
```text
30 × 400 = 12 000 Mio
12 000/1 024 = 11,71875 Gio
```
Avec trois copies physiques intégrales indépendantes, il faut **36 000 Mio**, soit **35,15625 Gio**. Ces chiffres excluent versions supplémentaires, sauvegardes, métadonnées, réplication interne et images.

Un alias ou une URI ne démontre pas la déduplication du stockage. Vérifier le comportement réel du registre et de la procédure de promotion ; séparer octets logiques, octets facturés et coût des transferts. Une copie entre environnements peut être volontaire pour isoler accès et disponibilité.

---

Pourquoi une conversion de modèle vers un autre format exige-t-elle une nouvelle validation ? <!--anki:6132333033643138633461663432323562386266613066333235663463336334-->
?
Une conversion peut modifier **précision numérique, opérateurs, prétraitement ou contrat de sortie**. Tous les modèles et opérateurs ne sont pas supportés par tous les formats et runtimes.

Comparer original et converti sur cas usuels, extrêmes, catégories inconnues et valeurs proches du seuil. Fixer des tolérances numériques, puis vérifier les décisions : un petit écart de probabilité peut franchir un seuil métier. Mesurer aussi latence et mémoire dans l'environnement cible. Conserver origine, outil de conversion, version et rapport avec le nouvel artefact. Une conversion réussie sur un exemple ne prouve ni équivalence globale, ni maintien de la qualité en production.

---

Pourquoi deux releases peuvent-elles produire des décisions différentes avec les mêmes poids ? <!--anki:3133613534356663393731323430613238333962366534303739373134373965-->
?
Les décisions dépendent de **toute la chaîne** : données disponibles, transformations, calibration, ordre des classes, seuil, règle métier et configuration d'exécution. Changer l'un de ces éléments peut conserver les poids tout en modifiant le résultat.

Identifier séparément artefact et release complète, et comparer les manifests lors d'une régression. Un numéro de version de registre ne remplace pas cette description ; inversement, réenregistrer des poids identiques ne garantit pas une nouvelle capacité. Tester la combinaison effectivement livrée, puis attribuer les effets à ses changements. Le diagnostic doit pouvoir expliquer pourquoi un même client a reçu une décision différente à deux dates.

---

Pourquoi un changement de seuil doit-il suivre une procédure de promotion ? <!--anki:6164626332643133363239643465616138643934313536336466353738393730-->
?
Le **seuil** transforme des scores en décisions et modifie précision, rappel, volume traité et charge des équipes. Un meilleur classement n'implique pas que le seuil précédent reste adapté ; changer le seuil sans changer les poids peut suffire à saturer une revue humaine.

Versionner la politique, documenter objectif et contraintes, puis évaluer les décisions sur des données indépendantes de son ajustement. Vérifier calibration et capacité, prévoir déploiement progressif et retour arrière. Conserver modèle, calibrateur et seuil effectifs avec chaque décision. Une procédure proportionnée peut être légère, mais elle doit laisser une preuve de ce qui a été autorisé et pourquoi.

---

Pourquoi résoudre un alias de modèle une seule fois au début d'un job batch ? <!--anki:3933383431353437663936393435646362316166633635386532396265303438-->
?
Un alias peut changer pendant le job et conduire à **un lot mélangeant plusieurs versions**. Résoudre une version immuable et l'enregistrer avec les résultats rend le traitement cohérent.

Pour une reprise, conserver cette version sauf migration explicite. Un changement d'alias ne doit pas altérer silencieusement les éléments restants. Si le modèle initial est retiré pour sécurité, interrompre et appliquer une politique de retrait documentée.

---

Pourquoi tester le chargement d'un artefact ML sans accès réseau non déclaré ? <!--anki:3430346264306631653964663437303539363666346261343464363839666134-->
?
Un paquet peut télécharger **un tokenizer, du code ou des poids supplémentaires** au chargement. Il n'est alors pas autonome et sa reproduction dépend d'une source mutable.

Déclarer et embarquer les dépendances nécessaires, ou documenter précisément leur récupération contrôlée. Tester en environnement propre avec réseau limité. Une réussite sur la machine d'entraînement peut provenir de caches locaux absents en production.

---

## Mises en situation

Mise en situation : le modèle fonctionne dans le notebook mais l'image de production ne trouve pas une classe de prétraitement. Que changes-tu ? <!--anki:3234383065626134626138333430636239643563393566386537336332353334-->
?
1. **Bloquer la promotion** et conserver la release en place ; l'entraînement réussi ne valide pas le paquet.
2. **Reproduire dans une image propre** avec le seul artefact publié : identifier module local, import ou fichier implicite manquant.
3. **Distribuer le composant** de façon versionnée et déclarer ses dépendances ; éviter la copie manuelle depuis le poste d'un auteur.
4. **Recharger et tester la chaîne** sur références, entrées invalides et contrat de sortie ; vérifier environnement et ressources cibles.
5. **Publier une nouvelle release** avec le rapport et l'empreinte du paquet vérifié.

**Piège** : ajouter un chemin local au notebook puis conclure que le déploiement est réparé.

---

Mise en situation : champion pointe vers la version 18, mais des réponses proviennent encore de la version 17. Comment enquêter ? <!--anki:3961613463663662373736663432626661613835666637666535373565356463-->
?
1. **Lire l'identité effective** des réplicas et des réponses ; séparer cible de l'alias et paquet réellement chargé.
2. **Examiner la procédure** : déplacement de l'alias, démarrage des processus, caches et éventuels chargements échoués.
3. **Résoudre une version explicite** et déployer le manifeste correspondant, avec contrôles de chargement et transition maîtrisée.
4. **Vérifier le trafic** et la distribution des versions jusqu'au terme du déploiement ; une coexistence peut être volontaire pendant un canary.
5. **Corriger l'attribution** des métriques si elles étaient étiquetées avec l'alias courant.

**Piège** : considérer le déplacement de l'alias comme une diffusion automatique et simultanée aux services.

---

Mise en situation : après restauration, le registre affiche le champion mais son chargement retourne un objet introuvable. Comment reprendre ? <!--anki:3964613865643464336131653433666162316237343165303565626633323265-->
?
1. **Identifier la référence absente** : URI, objet, version de stockage et droits ; distinguer absence et refus d'accès.
2. **Retrouver une sauvegarde cohérente** des artefacts et métadonnées, sans déplacer arbitrairement l'alias vers un fichier disponible.
3. **Vérifier provenance et empreinte**, puis charger dans l'image attendue et exécuter les cas de référence.
4. **Rétablir une release approuvée** ou appliquer le mode dégradé prévu ; ne pas improviser un modèle sans preuves.
5. **Compléter l'exercice de reprise** pour couvrir artefacts, images et accès, puis mesurer RPO et RTO réels.

**Piège** : confondre interface de registre accessible et capacité de produire une prédiction correcte.

---

## Sources

- [MLflow — registre, versions et alias](https://mlflow.org/docs/latest/ml/model-registry/workflow/) — distinctions d'identité et résolution des alias.
- [MLflow — migration vers MLflow 3](https://mlflow.org/docs/latest/ml/mlflow-3/) — modèles journalisés et URI retournée.
- [MLflow — API scikit-learn](https://mlflow.org/docs/latest/api_reference/python_api/mlflow.sklearn.html) — `name`, `pyfunc_predict_fn` et résultat de `log_model`.
- [MLflow — architecture du stockage](https://mlflow.org/docs/latest/self-hosting/architecture/overview/) — séparation métadonnées et artefacts ; la procédure de restauration proposée en découle.
- [scikit-learn — persistance des modèles](https://scikit-learn.org/stable/model_persistence.html) — sécurité, dépendances, compatibilité et conversion.
- [scikit-learn — API du classifieur RandomForestClassifier](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html) — relation entre `classes_` et colonnes de probabilités.

- Complément du 14 novembre 2026 — Alias et versions de modèle : [MLflow — Model Registry Workflows](https://mlflow.org/docs/latest/ml/model-registry/workflow/).

## Connexions

- [[111-mlops-llmops-fondamentaux|MLOps et LLMOps]] — identités, responsabilités et lineage
- [[112-cicd-modeles|CI/CD des modèles]] — tests et promotion d'une release
- [[114-reproductibilite-variance|Reproductibilité]] — environnement et preuves historiques
- [[116-sre-incidents-capacite-ia|SRE des systèmes IA]] — reprise et identité effective
- [[117-pipelines-entrainement-continu|Pipelines d'entraînement]] — produire et sélectionner les candidats
- [[119-contrats-prediction-features-batch|Contrats de prédiction]] — entrées, features et publication des résultats
- [[00-moc-ai-engineering|MOC AI Engineering]]
