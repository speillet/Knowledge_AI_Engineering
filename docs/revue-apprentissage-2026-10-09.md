# Revue de l'apprentissage — 9 octobre 2026

Le contenu reste pertinent pour un ingénieur IA appliquée, particulièrement sur les LLM, les agents et leur mise en production. La priorité de cette revue est la qualité du rappel : comprendre une notion, résoudre un exercice à partir de son recto et savoir si sa réponse est correcte.

## Périmètre

Le contrôle structurel couvre les **129 fiches et 1 856 cartes initiales** : syntaxe, identifiants, longueurs, connexions et questions identiques après normalisation. La lecture pédagogique approfondie cible les fondations Transformer, le prompting, les probabilités, le RAG, les évaluations et la reproductibilité, ainsi que les **68 cartes de calcul existantes**. Ce périmètre ne constitue pas une nouvelle vérification factuelle de chaque produit, version ou texte réglementaire du vault ; leurs dates de vérification restent inchangées.

Les répétitions exactes de questions n'étaient pas le principal problème. Les défauts observés étaient surtout des données nécessaires absentes du recto, des conclusions trop générales et des distinctions insuffisantes entre la mesure et son interprétation. Des notions voisines peuvent utilement revenir sous forme de définition, d'application et de cas ; cette complémentarité doit être évaluée à la lecture, pas uniquement par une recherche de doublons.

## Corrections apportées

**94 cartes existantes sont corrigées ou précisées dans 36 fiches**, dont **44 cartes de calcul**. Cela représente 48 rectos et 63 versos modifiés, avec chevauchement entre les deux. Leurs identifiants sont conservés et aucune carte n'est retirée.

| Problème pédagogique | Correction | Exemple de notion travaillée |
| --- | --- | --- |
| Données révélées seulement au verso | Placer valeurs, unités et hypothèses dans la question | Coût d'un agent, états Adam, quotas batch, taille d'échantillon |
| Règle empirique présentée comme garantie | Expliquer le mécanisme puis la condition de validité | Basse température ≠ exactitude ; majorité ≠ confiance calibrée |
| Explication générée prise pour une preuve | Séparer justification contrôlable et mécanisme interne | Chain-of-thought et vérification du résultat |
| Frontières trop strictes entre techniques | Préciser les objectifs et leurs recouvrements | Few-shot/fine-tuning ; pré-entraînement/post-training |
| Mesures confondues | Définir événements, dénominateurs et références | Vraisemblance/perplexité ; fidélité/exactitude ; pass@k/pass^k |
| Classe positive implicite | Fixer « positif = succès » et interpréter TPR/TNR | Validation et correction d'un juge imparfait |
| Test et évaluation présentés comme alternatives | Montrer leur complémentarité et leurs limites | Contrats déterministes, critères de qualité et non-régression |
| Approximation transformée en promesse | Séparer plafond théorique et performance mesurée | Capacité KV, vitesse de decode, transfert des poids |

Deux corrections concrètes : le budget KV de 68 Go divisé par 2,62144 Go par requête autorise **25 requêtes complètes**, pas 26 ; le traitement de 6,6 milliards de tokens à 2 millions/minute impose **au moins 55 heures** sous les hypothèses du quota, sans garantir cette durée réelle. Les calculs utilisent des hypothèses pédagogiques, pas des devis ni des benchmarks matériels.

Les mises en situation des fiches concernées sont ajustées pour rester cohérentes avec les réponses corrigées : préciser les exigences avant de concevoir les evals, diagnostiquer les étages du RAG, valider un juge par classe et éviter de transformer un taux moyen en garantie individuelle.

## Douze cartes pour appliquer les notions

| Fiche | Ajouts | Apport |
| --- | ---: | --- |
| [Transformer](../130-fondamentaux-llm/131-transformer-architecture.md) | 3 | Somme pondérée d'attention, facteur mémoire de GQA, parallélisme à l'entraînement et génération |
| [Probabilités et sampling](../60-inference-llm/65-probabilites-sampling.md) | 2 | Top-p avec renormalisation ; probabilité de séquence et perplexité |
| [Evals RAG et agents](../90-observabilite-evals/96-evals-rag-agents.md) | 4 | Précision/rappel, MRR, fidélité contre exactitude, diagnostic par contexte oracle |
| [LLM-as-a-judge](../90-observabilite-evals/95-llm-as-judge.md) | 1 | Correction numérique d'une proportion sous hypothèses explicites |
| [Reproductibilité](../110-mlops-cicd/114-reproductibilite-variance.md) | 1 | Moyenne des pass^2 par tâche différente du carré du succès moyen |
| [Prompting](../10-prompt-engineering/11-prompt-engineering-avance.md) | 1 | Neuf réponses identiques ne prouvent pas 90 % d'exactitude |

Ces ajouts comprennent **8 calculs, 2 distinctions et 2 cartes de diagnostic ou d'interprétation**. Ils complètent les définitions par une tâche observable. Le vault contient désormais **1 868 cartes**, dont **76 calculs**, **293 mises en situation** et **141 cartes « À ne pas confondre »**.

## Méthode de révision

Le [guide d'apprentissage](apprendre-avec-les-cartes.md) propose un parcours initial, un critère de réponse par type de carte, une notation honnête dans Anki et des variantes d'exercices sur brouillon. Il relie ensuite ces connaissances aux ateliers existants avec livrables. Le README explicite les conventions pour garder les futures questions autonomes et évaluables.

L'ordre de progression est une recommandation éditoriale adaptée à ce vault. La distinction entre rappel et relecture est étayée par l'[étude de Roediger et Karpicke](https://psychnet.wustl.edu/memory/wp-content/uploads/2018/04/Roediger-Karpicke-2006_PsychSci.pdf) ; le sens des boutons de notation suit le [manuel Anki](https://docs.ankiweb.net/manual/studying). Les sources techniques primaires sont ajoutées aux fiches concernées : articles sur Transformer, GQA, RoPE, raisonnement, juges et RAG ; documentation Hugging Face et scikit-learn ; manuel de recherche d'information de Stanford.

## Vérifications

Les vérifications portent sur la cohérence des contenus modifiés et le bon fonctionnement du vault, pas sur une amélioration mesurée de l'apprentissage chez des utilisateurs. Les calculs sont des exercices ; aucun benchmark GPU n'a été exécuté pour cette revue.

- Lint sur tout le vault : aucune erreur ni avertissement ; lecture compatible avec le parseur Spaced Repetition.
- Sommaires synchronisés et absence de questions exactement répétées après normalisation.
- 44 résultats numériques recalculés pour les nouveaux exercices, les corrections et les exemples du guide.
- 40 tests du dépôt réussis ; export Anki généré et contrôlé.
- 1 868 cartes actives et 30 cartes précédemment retirées, toujours suspendues dans l'export.
- Identifiants des 1 856 cartes préexistantes conservés, avec leurs affectations aux paquets et les noms de paquets stables. Le contrôle compare les fichiers exportés ; il ne simule pas l'import dans une collection personnelle contenant un historique de révision.

Les évolutions sont réparties en trois thèmes de commit : corrections des notions et des énoncés, exercices d'application, puis guide et bilan pédagogique.
