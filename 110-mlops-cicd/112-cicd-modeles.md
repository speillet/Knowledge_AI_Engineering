# CI/CD des modèles — Flashcards
Tags: #flashcards #ai-engineering #mlops #cicd #llm
<!-- summary: evals statistiques et tests déterministes, eval gates (exemple de seuils), artefact déployé, blue/green et canary, shadow deployment, rollback, GitOps, tests d'une app LLM, prompts en CI, pipeline complet. -->


Qu'apporte le CI/CD d'une app LLM en plus du CI/CD classique ? <!--anki:4a6b3758755748575f5d-->
?
Des **eval gates** : la qualité du modèle ou du prompt est testée automatiquement **comme du code**, en plus des tests logiciels habituels.

La différence de fond : les tests classiques sont **déterministes** (réussi ou échoué), les evals sont **statistiques** (un score sur un jeu de cas, avec de la variance). Il faut donc des seuils, des marges et assez d'exemples pour qu'un écart soit significatif ([[114-reproductibilite-variance|variance]]).

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

---

Que contient l'artefact déployé d'une app LLM ? <!--anki:695e35574c713148795a-->
?
Trois versions distinctes, à tracer **ensemble** :
- L'**image conteneur** de l'application
- La **référence du modèle** (identifiant daté chez un fournisseur, ou poids et adapter dans un registry)
- Les **prompts et la config** de génération

Un manifeste de release qui les regroupe permet de redéployer ou d'annuler l'ensemble d'un coup.

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

---

Qu'est-ce que le GitOps appliqué aux modèles ? <!--anki:423a6e24507a51415361-->
?
L'**état désiré** (version du modèle, config du serveur d'inférence, prompts) est déclaré **dans Git** ; un opérateur comme **Argo CD** ou **Flux** réconcilie le cluster en continu avec cet état.

Avantages : chaque changement passe par une **pull request** revue, l'historique Git sert d'audit, et le rollback est un `git revert` ([[12-kubernetes-gpu-inference|Kubernetes GPU]]).

---

Quels types de tests pour une app LLM en CI ? <!--anki:507d662a4f776c345758-->
?
- **Unitaires** (parsing, outils)
- **Intégration** (LLM mocké)
- **Evals** (qualité sur golden dataset)
- **Contrats** : validité des schémas de [[63-guided-generation|sorties structurées]]

Les mocks rendent les tests rapides et reproductibles, mais ne vérifient pas le comportement du fournisseur réel. Prévoir aussi un petit ensemble d'intégrations réelles, borné en coût et en fréquence, et des evals sur cas difficiles. Les assertions doivent porter sur des contrats ou résultats utiles, pas seulement sur la présence d'un texte non vide.

---

Pourquoi les prompts passent-ils par la CI ? <!--anki:6e4f4a30597944562b70-->
?
Un prompt modifié **change le comportement en production** autant qu'un changement de code, et souvent de façon moins prévisible : une consigne ajoutée pour un cas peut en dégrader dix autres.

Chaque modification déclenche donc les **tests de régression** sur le golden dataset ([[92-chainforge-evals-prompts|golden datasets]]), et le diff du prompt est relu comme du code.

---

Quelles étapes composent un pipeline CI/CD d'application LLM ? <!--anki:633b61656533535d3e3f-->
?
```text
PR → tests + evals → build image → push registry
→ deploy canary → métriques/SLO OK → promotion
```

Chaque passage doit avoir un critère : tests déterministes valides, seuils d'evals atteints, artefact identifié, puis observation du canary. Conserver le manifeste reliant code, modèle, prompt et données à cette validation. Une régression de qualité ou de SLO bloque la promotion et peut déclencher le rollback ; une simple réponse HTTP 200 ne suffit pas.

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
- [[00-moc-ai-engineering|MOC AI Engineering]]
