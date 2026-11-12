# CI/CD des modèles — Flashcards
Tags: #flashcards #ai-engineering #mlops #cicd #llm
<!-- summary: evals statistiques et tests déterministes, eval gates (exemple de seuils), artefact déployé, blue/green et canary, shadow deployment, rollback, GitOps, tests d'une app LLM, prompts en CI, pipeline complet, rollback après migration de schéma, livraison ou déploiement continus, smoke training, même artefact promu, canary avec labels tardifs. -->


Qu'apporte le CI/CD d'une app LLM en plus du CI/CD classique ? <!--anki:4a6b3758755748575f5d-->
?
Des **eval gates sur le comportement**, en plus des tests de code, contrats et intégration. L'opposition n'est pas « tests déterministes, evals statistiques » : les deux peuvent comporter de l'aléa, et un invariant métier peut être strict.

Exemple : bloquer toute action non autorisée, tout en comparant la qualité de résumé sur un échantillon avec intervalle d'incertitude. Un gain moyen ne compense pas la violation du premier critère.

Fixer jeux, versions, seuils et protocole de répétition avant les essais ([[114-reproductibilite-variance|variance]]). Évaluer les segments critiques et mesurer couverture/échecs de l'évaluateur ; une gate sans cas représentatifs peut laisser passer une régression.

---

Qu'est-ce qu'un eval gate ? <!--anki:6a4b402e5157293d4533-->
?
Une **eval gate** décide si un candidat peut franchir une étape, selon des critères définis avant l'essai. Elle combine éventuellement contraintes absolues, comparaison à la référence et budgets de coût ou de latence.
```yaml
# Politique illustrative, à implémenter et à versionner.
gate:
  jeu: support-validation@v14
  reference: release-r16
  exactitude_min: 0.90
  perte_max_points: 0.02
  action_non_autorisee_observee: 0
```
Comparer sur les mêmes cas et examiner incertitude, segments et couverture. Une économie peut justifier une marge de non-infériorité préspécifiée ; toute version n'a pas à améliorer chaque score. Zéro violation observée bloque certains cas critiques sans démontrer un risque nul. Conserver rapport, évaluateur et décision avec la release.

---

Que contient l'artefact déployé d'une app LLM ? <!--anki:695e35574c713148795a-->
?
L'unité de release relie **application, modèle, configuration et dépendances de données** : image par digest, poids ou référence fournisseur, tokenizer et adapter éventuels, prompt, contrats d'outils et index ou features compatibles.

Pour un modèle tabulaire, inclure prétraitement, ordre et sémantique des entrées, calibrateur, classes et politique de décision. Une version de poids seule n'identifie pas ce service. Faire tester la combinaison puis promouvoir les mêmes objets. Un manifeste décrit ces liens ; il ne remplace pas leur disponibilité, les contrôles d'accès ni une migration nécessaire. Vérifier le résultat effectivement servi après chargement, pas seulement le manifeste publié.

---

À ne pas confondre : blue/green et canary pour un modèle ? <!--anki:4c433e55363b3a3f6e2a-->
?
- **Blue/green** : deux environnements ; le trafic bascule de l'ancien vers le nouveau après validation. Le retour est rapide si l'ancien reste disponible et compatible.
- **Canary** : une part du trafic utilise la nouvelle version ; on l'augmente si qualité, erreurs, coût et [[64-metriques-slo-inference|SLO]] restent acceptables.

Le premier facilite une bascule globale, le second limite l'exposition initiale. Aucun ne garantit un rollback instantané des données ou des actions externes. Prévoir compatibilité des schémas, critères d'arrêt et durée d'observation.

---

Qu'est-ce que le shadow deployment ? <!--anki:644e744c303250597258-->
?
En **shadow deployment**, une nouvelle version reçoit une copie du trafic mais sa sortie n'est pas présentée aux utilisateurs. Cela permet de comparer qualité, latence et formats sur des entrées réelles.

Désactiver ou simuler les effets externes et vérifier droits, confidentialité et capacité : l'absence d'affichage ne supprime pas tout risque. Le surcoût dépend du trafic copié et des modèles ; il ne double pas nécessairement la facture. Cette méthode n'observe pas l'effet de la nouvelle réponse sur le comportement des utilisateurs ([[97-evals-online-ab-testing|shadow testing]]).

---

Comment fonctionne le rollback d'un modèle ? <!--anki:7a484c43315e344e4931-->
?
On revient à la **version précédente** du modèle, de l'adapter ou du prompt, par exemple en redéplaçant une étiquette dans le registry.

Conditions : un versioning strict, l'ancienne version **encore disponible** (un modèle d'API peut avoir été retiré), et des **schémas de sortie compatibles**, sinon les systèmes en aval cassent. Un rollback se **teste** avant d'en avoir besoin.

Après bascule, tracer la version réellement servie : caches et réplicas peuvent conserver l'ancienne cible du label. Vérifier un cas métier connu et les files en cours ; modifier une référence dans le registre n'est pas la preuve du rétablissement.

---

Qu'est-ce que le GitOps appliqué aux modèles ? <!--anki:423a6e24507a51415361-->
?
Le **GitOps** déclare dans Git un état désiré, puis un contrôleur le compare à l'état exécuté et applique les changements autorisés. Version du service, références de modèles et configuration peuvent ainsi passer par revue.

Les références doivent désigner des artefacts contrôlés et immuables ; un chemin réécrit derrière le même nom casse la reproductibilité. Un `git revert` crée une nouvelle intention de retour, mais ne garantit pas compatibilité des schémas, restauration de données ou annulation d'effets métier. Définir le traitement des interventions d'urgence et des divergences. Tester convergence et version réellement chargée ; la présence d'un opérateur ne prouve pas la réussite du déploiement.

---

Quels types de tests pour une app LLM en CI ? <!--anki:507d662a4f776c345758-->
?
Combiner **tests unitaires**, contrats, intégrations et évaluations de comportement. Les premiers isolent parsing, transformations et autorisations ; les intégrations vérifient les frontières ; les evals mesurent la tâche sur des cas représentatifs.

Pour le ML tabulaire, tester aussi prétraitement et modèle rechargés depuis le paquet destiné au serving. Les mocks réduisent coût et variance mais ne vérifient pas le fournisseur réel ni les dépendances de l'image finale. Prévoir quelques intégrations réelles bornées lorsque nécessaires, des cas négatifs et des essais de reprise. Une assertion « sortie non vide » ou « HTTP 200 » ne valide ni montant, ni preuve, ni absence de double effet.

---

Quelles étapes composent un pipeline CI/CD d'application LLM ? <!--anki:633b61656533535d3e3f-->
?
```text
PR → tests + evals → build image → push registry
→ deploy canary → métriques/SLO OK → promotion
```

Chaque passage doit avoir un critère : tests déterministes valides, seuils d'evals atteints, artefact identifié, puis observation du canary. Conserver le manifeste reliant code, modèle, prompt et données à cette validation. Une régression de qualité ou de SLO bloque la promotion et peut déclencher le rollback ; une simple réponse HTTP 200 ne suffit pas.

Pour un modèle réentraîné régulièrement, on sépare deux chaînes : la **CI du pipeline**, qui teste les transformations et lance un entraînement de fumée sur quelques milliers de lignes, et l'**entraînement continu**, qui produit les candidats ([[117-pipelines-entrainement-continu|pipelines d'entraînement]]).

---

Pourquoi tester un rollback IA après une migration de schéma plutôt que supposer qu'il suffira de restaurer l'image ? <!--anki:6663393966663531373731653432323139326231386566643565363066333062-->
?
L'**ancienne application** peut ne plus comprendre l'état, les catégories ou les données produits par la nouvelle version. Restaurer son image peut donc aggraver l'incident.

Déployer d'abord des lecteurs compatibles, migrer progressivement puis changer les producteurs selon une stratégie d'expansion et de retrait. Garder une fenêtre de compatibilité ou un chemin de restauration documenté. Tester le rollback avec des runs créés après migration. Inclure modèle, prompt, index et parseur : leur cohérence compte autant que celle du code.

---

À ne pas confondre : livraison continue et déploiement continu de modèles ? <!--anki:3562653164393336616537353436616162323764373235623536663761363134-->
?
La **livraison continue** maintient une version prête à être déployée après les contrôles prévus, avec éventuellement une décision humaine finale. Le **déploiement continu** automatise aussi cette dernière transition lorsque ses conditions sont satisfaites.

Les deux exigent artefacts identifiés, preuves de validation et procédure de retour. Pour un modèle dont les effets sont sensibles ou les labels tardifs, une promotion manuelle peut être un choix de maîtrise, sans renoncer aux tests ni à l'automatisation de préparation. Décrire clairement où s'arrête l'automate : l'expression « pipeline CI/CD » ne précise pas qui autorise la mise en service ni sous quelles preuves.

---

Que vérifie un entraînement de fumée dans la CI d'un pipeline ML ? <!--anki:3666383335663963356230343435363939616638333339373930356438363764-->
?
Un **entraînement de fumée** exécute rapidement le chemin complet sur un petit jeu contrôlé : ingestion, transformations, fit, prédiction et publication d'un artefact test. Il révèle notamment imports cassés, types incompatibles et sorties manquantes.

Sa petite taille ne permet pas d'affirmer une qualité de généralisation ou une capacité de production. Employer des cas couvrant catégories, valeurs manquantes et erreurs attendues, puis réserver d'autres tests aux performances et à la validation statistique. Vérifier que les données de test n'atteignent pas le registre de production. Une CI rapide valide le fonctionnement de la recette ; le candidat complet passe ses propres gates.

---

Pourquoi promouvoir le même artefact testé plutôt que réentraîner à chaque environnement ? <!--anki:6536393566663039346134383433343338373761393062333930316163376632-->
?
Réentraîner en staging puis en production peut produire **deux modèles différents**, même avec le même code. Les preuves obtenues sur le premier ne s'appliquent plus automatiquement au second.

Construire un candidat identifié, valider son paquet, puis promouvoir ces mêmes objets avec une configuration d'environnement contrôlée. Séparer les secrets sans changer silencieusement prétraitement ou paramètres métier. Si une adaptation impose un nouveau calcul, créer une nouvelle version et la valider. Enregistrer empreintes et version effectivement chargée ; un nom de release commun ou une recette identique ne démontre pas l'identité des poids et dépendances livrés.

---

Pourquoi un canary techniquement sain ne valide-t-il pas encore la qualité d'un modèle aux labels tardifs ? <!--anki:3135363933376136353963343430656639383631363035303637623639356631-->
?
Le **canary** donne rapidement des signaux de service : erreurs, latence, formats, volumes et coût. Si la cible est une issue à trente jours, ces premières minutes ne disent pas encore si les prédictions sont justes.

Définir des garde-fous immédiats et un critère distinct fondé sur cohortes mûres. Conserver assignation, version et décisions pour rapprocher les résultats futurs. Une promotion partielle peut rester sous observation selon le risque ; ne pas remplacer l'issue par un proxy sans vérifier sa portée. La réussite du transport et l'absence d'incident visible ne prouvent ni calibration ni gain métier durable.

---

## Mises en situation

Mise en situation : une modification d'une ligne du system prompt part en production sans revue, et la qualité chute pendant deux jours avant qu'on s'en aperçoive. Que mets-tu en place ? <!--anki:6e6a4676534d666b7c3f-->
?
1. **Traiter le prompt comme du code** : versionné dans Git, relu en pull request
2. **Eval gate** : rejeu du golden dataset à chaque modification, blocage si régression ([[94-evals-methodologie|evals]])
3. **Traçabilité** : la version du prompt apparaît dans les traces, pour savoir ce qui tournait ([[91-langfuse-observabilite|traces]])
4. **Déploiement progressif** : canary avec comparaison des métriques avant promotion
5. **Rollback rapide** : revenir à la version précédente sans redéployer toute l'application

**Piège** : modifier les prompts dans une interface de production, sans historique ni revue.

---

Mise en situation : tu dois déployer une nouvelle version de modèle sur un service critique, sans fenêtre de maintenance. Quelle stratégie choisis-tu ? <!--anki:6f55366b2969522d7352-->
?
1. **Valider offline** : evals de non-régression et tests de contrat sur les sorties structurées
2. **Shadow** d'abord si le budget le permet : trafic réel dupliqué, sans réponse montrée à l'utilisateur
3. **Canary** ensuite : petit pourcentage, surveillance des SLO, des erreurs et des scores de qualité
4. **Critères de promotion et de rollback définis à l'avance**, pas décidés dans l'urgence
5. **Artefact complet versionné** : image, référence du modèle, prompts et configuration

**Piège** : un blue/green instantané sur un modèle dont la latence et le format de sortie n'ont pas été vérifiés en conditions réelles.

---

## Sources

- [Google SRE — canary et contrôle des releases](https://sre.google/workbook/canarying-releases/)
- [Google Cloud — CI/CD/CT et validation des pipelines ML](https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning)

## Connexions
- [[111-mlops-llmops-fondamentaux|MLOps fondamentaux]] — versioning & registry
- [[92-chainforge-evals-prompts|Evals]] — le contenu des gates
- [[64-metriques-slo-inference|Métriques & SLO]] — le juge du canary
- [[83-gateway-ingress|Ingress & gateway]] — le découpage du trafic
- [[12-kubernetes-gpu-inference|Kubernetes GPU]] — la cible de déploiement
- [[114-reproductibilite-variance|Reproductibilité & variance]] — tester des sorties variables
- [[93-monitoring-inference|Monitoring de l'inférence]] — les contrôles avant d'envoyer du trafic
- [[115-plateformes-agents-gouvernance|Plateformes d'agents — Architecture & gouvernance]] — evals et boucle d'optimisation des agents
- [[105-devsecops-ia-agentique|DevSecOps pour l'IA agentique]] — contrôles de sécurité et security eval gate
- [[94-evals-methodologie|Méthodologie d'évaluation]] — construire les gates
- [[97-evals-online-ab-testing|Evals online & A/B testing]] — canary vs A/B
- [[106-securite-agents-code|Sécurité des agents de code]] — risques propres aux agents de code
- [[113-monitoring-drift-feedback|Monitoring & drift]] — qualité en production et boucle de feedback
- [[13-prompts-production|Prompts en production]] — structure, versioning et portabilité des prompts
- [[116-sre-incidents-capacite-ia|SRE : incidents & capacité des services IA]] — rollback et compatibilité des artefacts
- [[117-pipelines-entrainement-continu|Pipelines d'entraînement & entraînement continu]] — le pipeline qui produit les candidats à promouvoir
- [[118-artefacts-registre-releases-ml|Artefacts, registre et releases ML]] — contrats et vérifications de production
- [[119-contrats-prediction-features-batch|Contrats de prédiction, features et batch]] — contrats et vérifications de production
- [[00-moc-ai-engineering|MOC AI Engineering]]
