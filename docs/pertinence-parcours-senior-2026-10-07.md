# Pertinence du parcours ingénieur IA senior — 7 octobre 2026

## Diagnostic

Le vault est **pertinent pour un ingénieur IA appliquée orienté LLM, agents et production**. Ses points forts sont les évaluations, la sécurité, l'inférence, les données et la conception de systèmes. Les fondations ML et systèmes distribués ajoutées le 6 octobre améliorent son équilibre. Il ne constitue pas à lui seul un cursus complet de recherche ML, de vision ou de robotique, ni une preuve de séniorité.

La revue porte sur la cartographie des **117 fiches et 1 663 cartes initiales**, les questions et thèmes, puis une lecture approfondie ciblée des fiches liées aux lacunes et corrections ci-dessous. Le contrôle structurel est exhaustif ; la vérification factuelle est ciblée. Cette intervention ne prétend pas revérifier toutes les versions de produits et tous les textes réglementaires du vault.

Le principal déséquilibre est pédagogique : les outils et infrastructures sont très détaillés, alors que certaines compétences nécessaires pour justifier une décision n'étaient que mentionnées. Par exemple, la calibration apparaît dans plusieurs fiches, mais sans parcours complet de mesure et d'abstention ; l'accumulation de gradients apparaît dans le distribué, sans diagnostic de normalisation par token.

## Priorités de révision

Cette grille est une recommandation éditoriale pour ce vault, pas un barème universel de recrutement.

| Bloc existant | Pertinence pour le socle senior | Priorité proposée |
| --- | --- | --- |
| Choix ML, validation, contrats et temporalité des données | Essentiel pour éviter une solution inutile ou un score trompeur | À maîtriser avant de complexifier une architecture |
| Evals, analyse d'erreurs, sécurité, coûts et system design | Très forte : permet de décider et de livrer | Réviser avec des cas réels et des critères chiffrés |
| RAG, outils et workflows | Très forte pour les produits LLM | Comparer systématiquement à une baseline plus simple |
| Inférence, conteneurs et infrastructure | Socle utile ; profondeur selon le rôle | Approfondir GPU et Kubernetes pour un rôle plateforme ; HPC selon le contexte |
| Fiches centrées sur Cognee, ChainForge ou un framework | Utiles pour les projets concernés ; moins prioritaires que les mécanismes | Les lire avec un besoin concret, garder les principes transférables |
| Multi-agents, RL agentique, entraînement distribué avancé | Spécialisations à forte complexité | Les approfondir après les baselines, selon les responsabilités visées |
| Leadership technique | Nécessaire mais insuffisant à mémoriser | Démontrer décisions, transmission et responsabilité d'exploitation |

Aucune carte existante n'est supprimée : les fiches spécialisées gardent une utilité contextuelle et la progression de révision doit être préservée. L'ordre de travail change davantage que le périmètre du vault.

## Enrichissements réalisés

| Contenu | Ajout | Compétence travaillée |
| --- | ---: | --- |
| [Optimisation et diagnostic d'entraînement](../50-fine-tuning/56-optimisation-diagnostic-entrainement.md) | 14 cartes | Distinguer perte et valeur, diagnostiquer gradients, accumulation et précision numérique |
| [Calibration, incertitude et abstention](../170-ml-classique/173-calibration-incertitude-abstention.md) | 14 cartes | Valider une confiance, choisir une couverture et chiffrer la revue humaine |
| [Statistiques pour décider](../90-observabilite-evals/99-statistiques-decisions-experimentales.md) | 14 cartes | Interpréter un gain, contrôler la sélection et respecter l'unité indépendante |
| [SRE, incidents et capacité](../110-mlops-cicd/116-sre-incidents-capacite-ia.md) | 14 cartes | Exploiter les SLO, maîtriser les files et vérifier les reprises |
| [Leadership technique](../140-system-design-produit/147-leadership-technique-ia.md) | 4 cartes | Mentorat, revue de conception, dette et transfert d'exploitation |
| **Total** | **60 cartes** | **13 mises en situation et 9 distinctions incluses** |

Les sources primaires sont indiquées dans les fiches : documentation PyTorch, scikit-learn, SciPy, travaux sur calibration et prédiction conforme, NIST, ASA, Microsoft Research, Google SRE et AWS. Les exemples et démarches sont des applications pédagogiques aux systèmes IA, pas des résultats expérimentaux obtenus sur un déploiement particulier.

**Douze réponses existantes sont corrigées ou développées**, sans changer leurs questions ni identifiants :

- Taille du modèle et effort de raisonnement : un gain de qualité doit être mesuré, il n'est pas automatique.
- Calibration et hallucinations : distinguer probabilités de tokens, vérité des affirmations et signaux de détection.
- A/B testing : choisir l'unité de randomisation, distinguer proxy et résultat utile, ne pas supposer une durée universelle de nouveauté.
- Résilience : un repli sans RAG doit respecter le contrat produit ; les files et quotas doivent rester maîtrisés.
- QLoRA : distinguer poids bruts et mémoire totale au lieu de garantir qu'une taille de modèle tient sur un GPU donné.
- Séniorité : expliciter la responsabilité de bout en bout et l'autonomie de l'équipe.

## Ateliers avec preuves de maîtrise

Utiliser un fil rouge : **un service de tri et d'extraction de documents, avec revue humaine et assistant documentaire facultatif**. Travailler sur des données publiques ou synthétiques adaptées, avec des groupes et un test final réservés. Les seuils métier sont à fixer avant les essais ; les chiffres illustratifs des cartes ne sont pas des exigences universelles.

### 1. Justifier le choix du modèle

Comparer une règle, une baseline ML et une solution LLM si elle se justifie. Définir l'unité indépendante, les coûts d'erreur, la métrique principale et l'effet minimal utile. Produire un rapport avec différences appariées, incertitude, erreurs par segment, latence et coût total.

**Preuve attendue** : une autre personne peut reproduire le split et comprendre pourquoi le gain suffit, ne suffit pas ou demeure incertain. Aucun choix ne dépend d'essais répétés sur le test final.

### 2. Automatiser sans masquer les cas difficiles

Sur un classifieur, comparer probabilités brutes et calibrées avec jeux séparés. Mesurer courbe de fiabilité, Brier score, risque-couverture et charge de revue. Simuler un changement de population ou de prévalence et examiner les segments.

**Preuve attendue** : le seuil respecte les contraintes déclarées sur un jeu indépendant ; le rapport compte les abstentions, la capacité humaine et les erreurs restantes. Toute limite de validation est explicite.

### 3. Diagnostiquer l'apprentissage

Si l'adaptation fait partie du rôle visé, entraîner un petit modèle sur CPU ou un modèle adapté aux ressources disponibles. Vérifier qu'il mémorise un micro-lot, puis comparer train et validation. Introduire une erreur de masquage ou de normalisation et retrouver sa cause. Comparer accumulation et batch physique sur un cas contrôlé.

**Preuve attendue** : gradients et modifications de poids sont observés, la panne est isolée par une expérience et le correctif est vérifié. La seule baisse de loss ne constitue pas le résultat.

### 4. Exploiter le service sous panne

Servir le pipeline avec instrumentation et admission bornée. Injecter timeout, 429, indisponibilité du retrieval et saturation d'une dépendance. Mesurer délai, file, consommation du budget d'erreur et comportement du secours. Exécuter rollback et restauration avec des effets métier simulés.

**Preuve attendue** : chaque panne déclenche un comportement prévu ; aucun effet n'est dupliqué dans les scénarios testés ; RTO/RPO mesurés et limites de capacité sont documentés. Une réussite locale ne prouve pas les garanties d'un déploiement distribué réel.

### 5. Transmettre et défendre la décision

Écrire un ADR comparant les options et un runbook utilisable par un collègue. Faire exécuter une livraison ou un diagnostic sans instructions orales indispensables. Rédiger un postmortem de l'exercice et vérifier au moins une action corrective en rejouant la panne.

**Preuve attendue** : le collègue retrouve la décision, son motif et les conditions de réexamen ; les corrections réduisent un problème observé. C'est une preuve d'autonomie collective que la récitation seule ne fournit pas.

## Limites et suite du parcours

Pour un poste davantage centré sur l'entraînement ou la recherche, compléter selon le besoin les mathématiques de l'optimisation, l'algèbre linéaire, les architectures hors LLM et la lecture critique d'articles avec reproductions. Pour un poste plateforme, approfondir réseaux, stockage, profilage et exploitation GPU dans un environnement réel. La nouvelle fiche de statistiques introduit la causalité ; elle ne constitue pas un cours complet d'inférence causale.

## Validation

Le vault passe à **121 fiches, 1 723 cartes et 17 sections**, dont **269 mises en situation et 122 distinctions**. Les quatre fiches sont intégrées aux catalogues et reliées dans les deux sens. Le MOC propose un parcours pratique associé à ces ateliers.

- **Lint** : zéro erreur et zéro avertissement, avec lecture équivalente dans Obsidian et Anki.
- **Catalogues** : `sync_catalog.py --check` valide ; `git diff --check` sans anomalie.
- **Tests existants** : 40 réussis, avec les dépendances du dépôt disponibles dans `/tmp/knowledge-flashcards-deps`.
- **Conservation** : comparaison à `HEAD` ; les 1 663 anciens GUID et toutes leurs questions sont identiques. Douze réponses changent et 60 nouvelles cartes reçoivent un identifiant distinct.
- **Calculs** : batch effectif, Brier, précision, charge humaine, borne binomiale, comparaisons multiples, budget d'erreur, burn rate et croissance de file vérifiés en Python.
- **Anki** : `dist/ai-engineering.apkg` régénéré ; archive et intégrité SQLite valides, 1 723 cartes actives avec réponses et GUID correspondant au vault, 30 cartes retirées suspendues. Le paquet reste un artefact local exclu de Git.

Les ateliers ci-dessus sont proposés à l'apprenant ; ils n'ont pas été exécutés comme projets complets pendant cette revue. Aucun entraînement GPU ni exercice sur un fournisseur externe n'a été réalisé. La conservation des identifiants a été vérifiée dans le paquet ; aucune bibliothèque Anki personnelle n'a été ouverte ou modifiée.
