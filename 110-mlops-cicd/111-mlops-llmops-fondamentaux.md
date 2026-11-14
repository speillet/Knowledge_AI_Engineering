# MLOps & LLMOps — Fondamentaux — Flashcards
Tags: #flashcards #ai-engineering #mlops #llmops #llm
Vérifié le : 29 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.
<!-- summary: DevOps ou MLOps, spécificités du LLMOps, ce qu'il faut versionner (code et config, modèles et données), model registry, lineage, reproductibilité, environnements dev/staging/prod, rôle du Lead, manifeste cohérent de release, CI/CD/CT, recette et run, validité technique, statistique et métier, dette de dépendances de données, propriétaire du modèle, dette de labels. -->


Qu'est-ce que le MLOps ? <!--anki:72493079506c593c216d-->
?
Le **MLOps** organise la construction, la livraison et l'exploitation de systèmes ML : données, entraînement, validation, prédiction, surveillance et retrait. Il associe automatisation, traçabilité et responsabilités opérationnelles pour maintenir un comportement utile dans la durée.

Par exemple, une nouvelle semaine de ventes peut produire un candidat avec le même code mais d'autres poids. Il faut retrouver ses données, sa recette, ses évaluations et les décisions de promotion. Le monitoring lance une investigation ; il ne commande pas automatiquement un réentraînement. Le succès se mesure aussi par délai de livraison, stabilité, coût et capacité de restauration, au-delà du score d'un notebook.

---

À ne pas confondre : DevOps et MLOps ? <!--anki:47765959597d7b3a6634-->
?
**DevOps** organise la livraison et l'exploitation du logiciel, y compris code, configuration et infrastructure. **MLOps** étend cette démarche aux données, modèles et évaluations statistiques, car une modification des données peut changer le comportement sans modifier le code.

Une release ML doit relier les versions de code, données, entraînement et modèle aux résultats de validation. Le rollback concerne donc plusieurs artefacts, et les tests de code seuls ne suffisent pas à détecter une baisse de qualité prédictive.

---

Qu'est-ce que le LLMOps par rapport au MLOps classique ? <!--anki:4f587838485048773f3c-->
?
Le **LLMOps** applique cette discipline à un système dont le comportement dépend aussi des prompts, contextes, index, outils et modèles éventuellement fournis par API. L'équipe peut exploiter un modèle sans gérer son entraînement initial.

Une modification du corpus ou d'une permission peut changer les résultats sans changer les poids. La release doit donc identifier la combinaison réellement exécutée et son protocole d'évaluation. Surveiller tâches accomplies, effets externes, latence et coût, avec gestion des changements fournisseur. Les invariants métier restent contrôlés par l'application ; la variabilité du texte ne justifie pas une variabilité des droits ou des montants.

---

Quels artefacts de code et de configuration faut-il versionner dans un système LLM ? <!--anki:723b4b462f6130794733-->
?
- Le **code** applicatif et les pipelines
- Les **prompts**, y compris les descriptions d'outils
- La **config de génération** : modèle et version exacte, température, `max_tokens`, schéma de sortie

Changer l'un d'eux change le comportement : chaque réponse en production doit pouvoir être reliée à la **combinaison exacte** qui l'a produite ([[13-prompts-production|prompts en production]]).

Un manifeste peut relier `git_sha`, version du prompt, modèle et empreinte de configuration. Ne pas y copier les secrets : conserver leurs références et les droits d'accès nécessaires, séparément des artefacts versionnés.

---

Quels artefacts de modèle et de données faut-il versionner dans un système LLM ? <!--anki:364c47756e29552b3e-->
?
- Les **poids ou adapters** fine-tunés ([[51-fine-tuning-adaptation|LoRA]]), avec les données et la recette qui les ont produits
- Les **golden datasets** d'éval, pour que deux scores soient comparables
- Les **index RAG** : documents sources, chunking et modèle d'embedding ([[153-data-flywheel-versioning|versioning]])

Un score d'eval sans la version du jeu de test ne veut rien dire.

Conserver aussi le split, les annotations et la politique de filtrage. Deux index utilisant les mêmes documents mais des chunks ou embeddings différents sont deux artefacts distincts ; un nom de dossier « corpus-production » ne suffit pas à les reproduire.

---

Qu'est-ce qu'un model registry ? <!--anki:726f4b36424a7d697952-->
?
Un **registre de modèles** catalogue des versions, leur provenance et les métadonnées utiles à leur cycle de vie : propriétaire, recette, évaluations, statut et références d'artefacts. Le stockage des fichiers peut être assuré par un service distinct.

Ne pas confondre numéro de version, alias mutable et autorisation de déploiement. Un alias `champion` peut désigner une version approuvée sans que tous les réplicas l'aient chargée. Les mécanismes de promotion varient ; MLflow privilégie les alias et tags plutôt que ses anciens stages. L'inscription au registre ne prouve ni qualité, ni sûreté du fichier, ni compatibilité avec l'environnement de serving.

---

Qu'est-ce que le lineage d'un modèle ? <!--anki:4a724a21746435493b53-->
?
Le **lineage** relie une version servie aux données, transformations, code, paramètres, exécution d'entraînement et validations qui l'ont produite. Sa couverture doit être vérifiée ; un outil ne découvre pas automatiquement toutes les dépendances.
```yaml
release: retention-r17
image: registry.example.org/scoring@sha256:empreinte-a-remplacer
modele: models:/retention/17
features: client-30j@v4
train: retention-train@snapshot-042
evaluation: retention-validation@v9
```
Cet extrait est illustratif : remplacer les références par des objets récupérables et leurs empreintes réelles. Pour enquêter, remonter d'une prédiction à cette release puis à son run. Les noms ne suffisent pas si les fichiers ont été réécrits ou supprimés. Conserver les accès et durées de rétention nécessaires à la reconstruction autorisée.

---

À ne pas confondre : versionner et épingler ? <!--anki:6c38252c232c417e7d21-->
?
- **Versionner** : conserver l'**historique** des artefacts (code, prompts, poids, datasets) pour pouvoir revenir en arrière et comparer
- **Épingler** : déclarer dans le déploiement une **version exacte** (digest, identifiant daté) au lieu d'un alias mouvant comme `latest`

On peut très bien versionner ses prompts **et** appeler un modèle via un alias qui change sous vos pieds : le versionnage seul ne protège pas ([[142-fiabilite-resilience-llm|épingler le modèle]]).

---

Pourquoi la reproductibilité est-elle difficile avec les LLM ? <!--anki:6f574d3477383b5a6656-->
?
**Non-déterminisme** (sampling), **versions de modèles API qui changent**, dépendances GPU — d'où : fixer les seeds/température, **épingler les versions** et tracer les configs.

Même avec une seed, l'ordre des calculs parallèles, les kernels ou le batching peuvent modifier certains choix de tokens. Reproduire l'environnement réduit la variance sans toujours supprimer toute différence. Pour comparer des versions, répéter les essais et mesurer les distributions de scores, en conservant aussi les entrées et résultats d'outils.

---

Comment gérer dev/staging/prod pour une app LLM ? <!--anki:69354f78696b443b7756-->
?
Promouvoir un **ensemble versionné cohérent** : code, modèle, prompt, schémas d'outils et configuration, avec les mêmes mécanismes de déploiement. Séparer identités, secrets, données et permissions des environnements.

Exemple : un staging rejoue des demandes réalistes mais dirige les outils d'envoi et de paiement vers des doubles de test ; changer seulement le modèle ne suffit pas à l'isoler.

Associer cas représentatifs correctement dépersonnalisés et cas synthétiques couvrant les limites. Exiger des [[112-cicd-modeles|eval gates]] avant promotion et prévoir rollback. Un alias fournisseur mutable exige aussi de tracer la version résolue et détecter les changements subis sans déploiement applicatif.

---

Quel est le rôle du Lead sur le volet MLOps ? <!--anki:7a3e4144593a524b4139-->
?
Le Lead organise des **contrats et responsabilités vérifiables** : qui produit les données, valide le candidat, autorise la promotion, exploite le service et peut arrêter un traitement défaillant.

Définir une nomenclature de releases, des gates fondées sur le risque, un responsable par système et des procédures de reprise testées. Prévoir la transmission à l'astreinte avec tableaux de bord, seuils et moyens de diagnostic. Un registre commun facilite l'inventaire, mais plusieurs outils peuvent coexister si les contrats restent cohérents. Mesurer délai de changement, échecs de déploiement et temps de rétablissement pour vérifier que les standards aident réellement les équipes.

---

Pourquoi un manifeste de release IA doit-il désigner un ensemble cohérent d'artefacts ? <!--anki:3238613763396433623462303430633239386138326562306435343466343561-->
?
Une **release** doit relier code, modèle, tokenizer, prompt, index ou features et configuration par des versions immuables. Leurs alias courants peuvent évoluer indépendamment.

Publier ce manifeste après validation de la combinaison, puis faire résoudre les références une seule fois pour le run. Conserver son identifiant dans les résultats et traces. Tester un redéploiement à partir du manifeste sans accès implicite à « latest ». Une collection d'artefacts versionnés ne suffit pas si personne ne sait quelle combinaison a réellement servi une décision.

---

À ne pas confondre : CI, CD et CT dans un système ML ? <!--anki:3635316166396234653463373430616639393564653836386162653462626165-->
?
La **CI** vérifie les changements de code et de composants ; la **CD** prépare et livre des artefacts validés vers les environnements ; la **CT**, entraînement continu, exécute la recette sur des données pour produire de nouveaux candidats.

Un changement de code peut modifier la recette sans entraîner immédiatement un modèle complet. De nouvelles données peuvent déclencher un entraînement sans changer cette recette. Séparer identités, versions et critères de passage pour les deux chaînes. « Continu » ne signifie ni calcul ininterrompu ni promotion sans contrôle : fréquence et automatisation dépendent du besoin, du coût et de la disponibilité de labels fiables.

---

À ne pas confondre : recette de pipeline et exécution d'entraînement ? <!--anki:6165356234363933353831313433313539373466666136306362363563313131-->
?
La **recette** est le code et la configuration qui définissent les étapes ; une **exécution** applique cette recette à des entrées précises, à un moment donné, avec ses propres résultats et erreurs.

Deux runs de la même recette peuvent produire des modèles différents à cause des données, paramètres ou opérations aléatoires. Chaque run doit référencer recette, snapshots, environnement et artefacts. Une reprise ne doit pas écraser l'identité de l'exécution précédente ni mélanger leurs sorties. Pour enquêter, retrouver le run effectivement déployé, plutôt que seulement le dernier commit du dépôt ou le dernier entraînement réussi.

---

Pourquoi distinguer validité technique, qualité prédictive et utilité métier dans une release ML ? <!--anki:6262356431636266633963363437326638356265373965363737626165313065-->
?
Un modèle peut **charger correctement**, prédire avec un bon score et néanmoins être inutile : délai trop long, coût excessif ou décision qui n'améliore pas le processus visé.

Définir trois preuves séparées : contrats et fonctionnement, métriques sur population pertinente, puis conséquence métier avec ses hypothèses. Une prévision plus précise peut ne pas changer le stock si la décision ne l'utilise pas. Fixer le critère d'acceptation et le responsable de chaque niveau avant la promotion. Une réussite technique ne remplace pas l'évaluation statistique ; un score offline ne démontre pas à lui seul l'effet produit en conditions réelles.

---

Pourquoi inventorier les dépendances et consommateurs des données d'un modèle ? <!--anki:3865333039316664303630653438386639323064336336343361376237666330-->
?
Les **dépendances cachées** rendent les changements risqués : une colonne peut provenir d'un autre modèle, et un score devenir à son tour une variable consommée ailleurs sans contrat explicite.

Documenter producteurs, transformations, finalités et consommateurs, avec versions et responsables. Avant de modifier une définition ou retirer une sortie, examiner ces usages et prévoir une migration. La traçabilité d'entraînement ne suffit pas à découvrir un consommateur qui lit directement une table de prédictions. Le MLOps inclut donc les contrats autour du modèle et les effets de chaîne, pas seulement le suivi de son propre run.

---

Pourquoi attribuer un propriétaire opérationnel à chaque modèle déployé ? <!--anki:3466306535656434323732623435323938396466616266343034313862323539-->
?
Il faut quelqu'un pour **interpréter les alertes, décider d'une suspension et maintenir les données et seuils**. Un modèle sans propriétaire peut continuer à produire des décisions après disparition de son équipe d'origine.

Documenter contacts, contrat de service, dépendances et procédure de retrait. Le propriétaire métier et l'exploitant peuvent être différents ; expliciter leurs responsabilités. Une fiche de modèle n'est utile que si elle correspond encore au déploiement actif.

---

Pourquoi l'absence de labels fiables constitue-t-elle une dette MLOps ? <!--anki:6232613363623536353139393465383438353034636364373861383336306234-->
?
Sans résultats observables, il devient difficile de **mesurer les régressions et choisir un réentraînement**. Ajouter du monitoring technique ne remplace pas cette mesure.

Définir dès la conception comment le label sera obtenu, relié à la prédiction et corrigé, avec délai et coût. Prévoir un échantillonnage lorsque l'annotation exhaustive est impossible. Les scores de confiance ne deviennent pas une vérité terrain parce que les labels manquent.

---

## Mises en situation

Mise en situation : une application LLM en production donne des réponses différentes d'il y a deux mois, et personne ne sait ce qui a changé. Que manque-t-il, et comment le corriges-tu ? <!--anki:75382a6c5a6c4a356639-->
?
1. **Constater** : sans versionnage complet, on ne peut ni expliquer ni revenir en arrière
2. **Versionner les quatre briques** : code, prompts et configuration de génération, modèle ou adapter, index RAG
3. **Épingler** la version exacte du modèle, y compris côté API, qui évolue sans commit chez toi ([[113-monitoring-drift-feedback|mises à jour du provider]])
4. **Tracer** la version utilisée dans chaque requête ([[91-langfuse-observabilite|traces]])
5. **Relier** version et qualité par des evals rejouées à chaque changement ([[112-cicd-modeles|CI/CD]])

**Piège** : versionner le code seul et considérer le prompt comme de la configuration secondaire.

---

Mise en situation : trois équipes déploient chacune leurs modèles, avec leurs conventions, et personne ne sait qui est responsable de quoi en production. Que mets-tu en place comme lead ? <!--anki:782852524b5072625831-->
?
1. **Un registre unique** pour les modèles et adapters, avec métadonnées, étapes et lineage
2. **Des conventions de versionnage** communes, appliquées par la CI plutôt que par la discipline
3. **Un propriétaire nommé** par modèle en production, responsable de sa qualité et de son retrait
4. **Des environnements alignés** : mêmes pipelines en dev, préproduction et production, données près du réel
5. **Des gates d'évaluation** obligatoires avant chaque promotion

**Piège** : imposer un outil avant d'avoir posé les responsabilités et les conventions.

---

## Sources

- [Google Cloud — MLOps, livraison et pipelines continus](https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning)
- [Langfuse — traces, évaluations et gestion des prompts](https://langfuse.com/docs)

- [MLflow — versions, alias et gouvernance du registre](https://mlflow.org/docs/latest/ml/model-registry/workflow/)
- [Google Research — Hidden Technical Debt in Machine Learning Systems](https://research.google/pubs/hidden-technical-debt-in-machine-learning-systems/)

## Connexions
- [[112-cicd-modeles|CI/CD des modèles]] — le pipeline qui applique ces standards
- [[113-monitoring-drift-feedback|Monitoring & drift]] — la boucle post-déploiement
- [[10-images-modeles-poids|Images & poids]] — model registry vs container registry
- [[51-fine-tuning-adaptation|Fine-tuning]] — les adapters comme artefacts
- [[91-langfuse-observabilite|Langfuse]] — prompts versionnés
- [[114-reproductibilite-variance|Reproductibilité & variance]] — la reproductibilité en détail
- [[115-plateformes-agents-gouvernance|Plateformes d'agents — Architecture & gouvernance]] — registre et cycle de vie des agents
- [[105-devsecops-ia-agentique|DevSecOps pour l'IA agentique]] — AI-BOM et chaîne d'approvisionnement des modèles
- [[153-data-flywheel-versioning|Data flywheel & versioning]] — versionner et boucler sur les données
- [[147-leadership-technique-ia|Leadership technique]] — rôle du senior
- [[150-016-observabilite-lignage-donnees|Observabilité, lignage & exploitation des données]] — tracer les données jusqu’aux versions de modèles
- [[117-pipelines-entrainement-continu|Pipelines d'entraînement & registre]] — alias champion, suivi d'expériences et entraînement continu
- [[118-artefacts-registre-releases-ml|Artefacts, registre et releases ML]] — contrats et vérifications de production
- [[00-moc-ai-engineering|MOC AI Engineering]]
