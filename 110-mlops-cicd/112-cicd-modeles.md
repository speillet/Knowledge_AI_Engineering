# CI/CD des modèles — Flashcards
Tags: #flashcards #ai-engineering #mlops #cicd #llm
<!-- summary: evals statistiques et tests déterministes, eval gates (exemple de seuils), artefact déployé, blue/green et canary, shadow deployment, rollback, GitOps, tests d'une app LLM, prompts en CI, pipeline complet, rollback après migration de schéma. -->


Qu'apporte le CI/CD d'une app LLM en plus du CI/CD classique ? <!--anki:4a6b3758755748575f5d-->
?
Des **eval gates sur le comportement**, en plus des tests de code, contrats et intégration. L'opposition n'est pas « tests déterministes, evals statistiques » : les deux peuvent comporter de l'aléa, et un invariant métier peut être strict.

Exemple : bloquer toute action non autorisée, tout en comparant la qualité de résumé sur un échantillon avec intervalle d'incertitude. Un gain moyen ne compense pas la violation du premier critère.

Fixer jeux, versions, seuils et protocole de répétition avant les essais ([[114-reproductibilite-variance|variance]]). Évaluer les segments critiques et mesurer couverture/échecs de l'évaluateur ; une gate sans cas représentatifs peut laisser passer une régression.

---

Qu'est-ce qu'un eval gate ? <!--anki:6a4b402e5157293d4533-->
?
Un **seuil d'évaluation bloquant** dans la CI : si les scores régressent, le merge ou le déploiement est **refusé** ([[92-chainforge-evals-prompts|evals]]).
```yaml
eval_gate:
  dataset: golden-support@v14       # 400 cas
  criteres:
    exactitude:      { min: 0.90, regression_max: 0.02 }
    format_valide:   { min: 0.99 }
    cout_par_requete: { max_hausse: 0.15 }
```
On bloque sur la **régression** par rapport à la version en production, pas seulement sur un seuil absolu.

Comparer candidat et référence sur les mêmes cas, avec des critères définis avant l'essai. Une baisse minime peut venir du bruit ; une moyenne stable peut cacher une régression sur un segment critique. Prévoir seuils par segment, répétitions utiles et revue des cas limites. Le YAML représente ici une politique à implémenter, pas un outil universel.

---

Que contient l'artefact déployé d'une app LLM ? <!--anki:695e35574c713148795a-->
?
Quatre références distinctes, à tracer **ensemble** :
- L'**image conteneur** de l'application
- La **référence du modèle** (identifiant daté chez un fournisseur, ou poids et adapter dans un registry)
- Les **prompts et la config** de génération
- L'**index RAG** ou les données de retrieval, avec leur modèle d'embedding

Un manifeste de release qui les regroupe permet de redéployer ou d'annuler l'ensemble d'un coup.

Exemple : image v7, prompt v12, poids révision R et index I4 forment une combinaison testée. Déplacer seulement le label du modèle peut casser un schéma d'outil attendu par cette image. Vérifier la compatibilité du manifeste entier.

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
L'**état désiré** (version du modèle, config du serveur d'inférence, prompts) est déclaré **dans Git** ; un opérateur comme **Argo CD** ou **Flux** réconcilie le cluster en continu avec cet état.

Avantages : chaque changement passe par une **pull request** revue, l'historique Git sert d'audit, et le rollback est un `git revert` ([[12-kubernetes-gpu-inference|Kubernetes GPU]]).
```yaml
# InferenceService KServe versionné dans Git, appliqué par Argo CD
spec:
  predictor:
    model:
      modelFormat: { name: sklearn }
      storageUri: s3://modeles/fraude/v8   # passer de v7 à v8 = une pull request
```
Git décrit la configuration, pas les poids : l'URI doit désigner un artefact **immuable**. Si `v8` peut être réécrit dans le bucket, un même commit sert deux modèles et le `git revert` ne restaure rien. Avec `selfHeal` dans Argo CD, une modification manuelle du cluster est annulée : les correctifs d'urgence passent aussi par Git.

---

Quels types de tests pour une app LLM en CI ? <!--anki:507d662a4f776c345758-->
?
- **Unitaires** (parsing, outils)
- **Intégration** (LLM mocké)
- **Evals** (qualité sur golden dataset)
- **Contrats** : validité des schémas de [[63-guided-generation|sorties structurées]]

Les mocks rendent les tests rapides et reproductibles, mais ne vérifient pas le comportement du fournisseur réel. Prévoir aussi un petit ensemble d'intégrations réelles, borné en coût et en fréquence, et des evals sur cas difficiles. Les assertions doivent porter sur des contrats ou résultats utiles, pas seulement sur la présence d'un texte non vide.

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
- [[00-moc-ai-engineering|MOC AI Engineering]]
