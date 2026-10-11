# Revue de pertinence — 11 octobre 2026

Le vault reste pertinent pour un ingénieur IA appliquée, avec une couverture particulièrement développée des LLM, des agents et de leur mise en production. Les deux passes de cette revue renforcent les critères de décision, les limites des garanties et le passage aux exercices. Elles ajoutent 33 cartes au total, pour atteindre 2 043 cartes.

## Périmètre et limites

Le contrôle structurel couvre les 137 fiches : format, liens, identifiants, lecture par le plugin et conventions pédagogiques. La première passe partait de 2 010 cartes ; la seconde de 2 022 cartes, en conservant les modifications précédentes. La lecture détaillée cible douze fiches : 31, 32, 51, 63, 95, 96, 143, 146, 161, 163, 172 et 173. Les passages corrigés sont confrontés aux sources primaires indiquées dans les fiches ; les exercices chiffrés sont recalculés.

Cette revue ne constitue pas une validation factuelle exhaustive de chaque réponse du vault ni une actualisation de toutes les versions de produits et de tous les textes réglementaires. Les dates de vérification existantes restent inchangées : ajouter une référence ou corriger un passage ne revient pas à revérifier une fiche entière.

## Première passe : qualité des réponses et des évaluations

| Fiche | Enrichissements | Apport pédagogique |
|---|---|---|
| LLM-as-a-judge (95) | Injection du juge, erreurs de parsing et abstentions, biais de sélection des cas relus, diagnostic d'un gain suspect | Distinguer amélioration réelle et hausse artificielle du score |
| Evals RAG et agents (96) | Validité, soutien et couverture des citations ; calcul explicite ; tests contrefactuels ; cas de liens valides mais non probants | Vérifier les affirmations plutôt que la simple présence de références |
| Hallucinations et grounding (143) | Limites de la température basse, conflits de sources, réponse partielle, cas de politiques contradictoires | Répondre selon des preuves applicables et expliciter ce qui manque |

Douze cartes ajoutées : huit cartes conceptuelles, une carte de calcul et trois mises en situation. Deux réponses existantes sont nuancées : format structuré et température basse ne garantissent pas la factualité ; un justificatif de juge doit être court, contrôlable et évalué, sans prescrire systématiquement un raisonnement long.

## Seconde passe : décision, agents, adaptation et multimodal

**35 cartes existantes sont corrigées ou précisées et 21 cartes ajoutées dans neuf fiches.** Les ajouts comprennent sept calculs, trois mises en situation, une distinction et dix autres cartes conceptuelles. Le nombre de corrections compte une carte une seule fois, même lorsque son recto et son verso changent.

| Fiche | Corrigées | Ajoutées | Compétence renforcée |
| --- | ---: | ---: | --- |
| [Agents fondamentaux](../30-agents/31-agents-fondamentaux.md) | 4 | 0 | Distinguer ReAct, format d'appel et boucle contrôlée ; justifier l'autonomie |
| [Tool calling](../30-agents/32-tool-calling.md) | 8 | 3 | MCP sans décision de LLM, validation conditionnelle, timeouts, statuts et pagination |
| [Fine-tuning](../50-fine-tuning/51-fine-tuning-adaptation.md) | 5 | 3 | Régressions possibles avec LoRA, artefacts d'un adapter, rang et amortissement |
| [Guided generation](../60-inference-llm/63-guided-generation.md) | 3 | 0 | Contrat de sortie, abstention et diagnostic sans présumer la cause |
| [Choix des modèles](../140-system-design-produit/146-choix-modeles.md) | 4 | 3 | Ouverture et hébergement, définition OSI, budgets comparables et front de Pareto |
| [Vision-langage](../160-multimodal-edge/161-modeles-vision-langage.md) | 5 | 4 | OCR sans promesse d'exactitude, coordonnées, documents complets et portée du marquage |
| [Voix temps réel](../160-multimodal-edge/163-voix-temps-reel.md) | 5 | 3 | Latence mesurée, WER et erreurs métier, interruption et action déjà effectuée |
| [Validation ML](../170-ml-classique/172-validation-metriques-ml.md) | 0 | 1 | Effet de la prévalence sur la précision à TPR/FPR constants |
| [Calibration et abstention](../170-ml-classique/173-calibration-incertitude-abstention.md) | 1 | 4 | Coût attendu des trois décisions, deux sens de couverture, erreurs humaines |
| **Total** | **35** | **21** | |

Quelques corrections décisives :

- **MCP** : l'ancienne réponse excluait son utilisation sans tool calling natif. Le protocole permet aussi une lecture de ressource ou un appel décidé par du code ou une interface.
- **Arguments stricts** : la présence d'un schéma ne garantit pas son application ; les réponses interrompues et les règles métier restent à traiter.
- **LoRA** : geler les poids de base n'empêche pas l'adapter actif de dégrader des capacités. Le nombre de clients ne suffit pas non plus à dimensionner un serving multi-LoRA.
- **Open source AI** : la définition OSI 1.0 demande des informations sur les données permettant un système substantiellement équivalent ; elle n'impose pas une reproduction bit à bit ni toujours toutes les données brutes.
- **Multimodal** : OCR, choix de transport ou speech-to-speech ne suffisent pas à promettre exactitude ou latence. Les garanties doivent être mesurées sur les entrées réelles.
- **Revue humaine** : ses erreurs et délais font partie du résultat du service. Le recto du calcul de charge annonce maintenant les trois minutes de revue nécessaires pour le résoudre.

Les questions nouvelles se comprennent seules et les calculs fournissent leurs hypothèses. Les cartes restent dans les fiches existantes et leurs identifiants historiques sont conservés.

## Atelier exécutable

L'[atelier de décision IA](../examples/decisions-ia/README.md) utilise la bibliothèque standard Python, avec énoncés séparés des solutions, résultats contrôlés et variantes sur brouillon. Il est relié depuis le README, le MOC et le guide d'apprentissage.

Ses quatre exercices travaillent précision selon la prévalence, décision avec revue, choix sous contraintes et qualité documentaire. Deux lots à 99 % de champs corrects ont respectivement 80 % et 99 % de documents entièrement corrects : la répartition des erreurs compte. Le calcul indépendant `0,99^20 ≈ 81,8 %` est un autre modèle, dont l'hypothèse doit être explicitée.

Les valeurs sont fictives. Aucun modèle n'est entraîné, aucun benchmark GPU n'est exécuté et aucune amélioration de l'apprentissage chez des utilisateurs n'est mesurée par cet atelier.

## Sources primaires et portée

- [Liu et al. — Evaluating Verifiability in Generative Search Engines](https://arxiv.org/abs/2304.09848) : distinguer soutien des citations et couverture des affirmations.
- [Niu et al. — RAGTruth](https://arxiv.org/abs/2401.00396) : le contexte récupéré n'élimine pas les affirmations non soutenues ou contradictoires.
- [JudgeDeceiver](https://arxiv.org/abs/2403.17710) : la réponse évaluée peut contenir une injection visant le juge.

Les démarches d'incident, le traitement des erreurs et les tests contrefactuels proposés sont des applications pédagogiques de ces limites ; ces articles ne valident pas à eux seuls une architecture de production particulière.

Pour la seconde passe, les références sont ajoutées aux fiches concernées :

- [Spécification MCP 2025-11-25 — outils](https://modelcontextprotocol.io/specification/2025-11-25/server/tools) et [ressources](https://modelcontextprotocol.io/specification/2025-11-25/server/resources), [ReAct](https://arxiv.org/abs/2210.03629) et documentation Anthropic pour les contrats d'outils.
- [LoRA](https://arxiv.org/abs/2106.09685), [TRL SFT Trainer](https://huggingface.co/docs/trl/sft_trainer), [PEFT](https://huggingface.co/docs/peft/package_reference/lora) et [vLLM](https://docs.vllm.ai/en/stable/features/lora/) pour l'adaptation et le serving.
- [Open Source AI Definition 1.0](https://opensource.org/ai/open-source-ai-definition) pour les libertés et les éléments requis, sans assimiler ouverture des poids et hébergement.
- [Qwen2.5-VL](https://arxiv.org/abs/2502.13923), [WER](https://huggingface.co/spaces/evaluate-metric/wer/blob/main/README.md) et [LiveKit](https://docs.livekit.io/testing/observability/data/) pour les capacités et les métriques multimodales.
- [Commission européenne — article 50](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-50) pour distinguer portée des obligations, marquage technique et information. Cette correction ciblée ne renouvelle pas l'audit réglementaire de la fiche AI Act.
- Documentation scikit-learn et introduction à la prédiction conforme déjà présentes dans les fiches 172 et 173 pour métriques, calibration et couvertures.

Les politiques de choix et les chiffres sont des dérivations pédagogiques sous hypothèses explicites ; ces sources ne démontrent pas qu'un modèle particulier sera adapté à un déploiement donné.

## Approfondissements encore utiles

1. **Atelier RAG vérifiable** : petit corpus fictif versionné, questions sans réponse et sources contradictoires ; livrable composé d'un tableau affirmation/preuve, des erreurs et d'une politique d'abstention.
2. **Atelier de validation du juge** : annotations humaines indépendantes, variantes de style et injections ; livrable composé d'une matrice de confusion par segment, de la couverture et des décisions de revue humaine.
3. **Atelier sur les effets d'outils** : service fictif avec résultat partiel, timeout après écriture et opération en attente ; produire une vérification d'état qui distingue arrêt, succès et résultat inconnu.
4. **Priorisation de la révision** : mesurer les erreurs de l'apprenant pour sélectionner les prochaines cartes à approfondir. Le nombre de cartes seul ne mesure pas la maîtrise ; privilégier les notions qui échouent en application.
5. **Actualisation ciblée** : poursuivre la vérification des fiches liées aux versions de produits et aux textes réglementaires en conservant une trace des passages réellement vérifiés.

## Validation

- 137 fiches, 2 043 cartes, 323 mises en situation et 164 cartes de confusion.
- Lint : zéro erreur et zéro avertissement.
- 40 tests du dépôt réussis sous Python 3.13 avec les dépendances épinglées ; les tests incluent le parseur, les catalogues et l'export Anki.
- La copie temporaire utilisée par les tests inclut maintenant les fichiers Markdown des exemples pour contrôler les liens vers le README du nouvel atelier.
- Export Anki généré et contrôlé : 2 043 cartes actives et 30 cartes retirées, suspendues.
- Tous les identifiants des cartes préexistantes conservés ; 33 nouveaux identifiants attribués en deux passes. Titres et affectations des paquets existants inchangés.
- Quatre exercices locaux exécutés, y compris le mode qui affiche seulement les énoncés ; résultats des calculs et variantes contrôlés.
- README et catalogue synchronisés ; liens locaux des documents et atelier vérifiés.

Le Python système 3.9 ne permettait pas d'installer toutes les dépendances épinglées. La validation a donc utilisé un environnement temporaire Python 3.13, sans modifier les dépendances du dépôt.
