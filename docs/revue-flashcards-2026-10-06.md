# Revue des flashcards — 6 octobre 2026

Le contrôle structurel porte sur les **1 553 cartes de 110 fiches**. Toutes possèdent une question, une réponse et un identifiant permanent. La revue rédactionnelle a conduit à modifier **385 cartes dans 88 fiches** : **370 réponses** enrichies ou corrigées et **49 questions** reformulées, certaines cartes cumulant les deux changements.

## Profondeur des réponses

Les **330 réponses de moins de 35 mots hors code** ont toutes été relues et développées. Ce seuil a servi à repérer les réponses potentiellement trop succinctes, pas à juger automatiquement leur qualité. Les compléments expliquent le mécanisme, un exemple d'usage, les prérequis ou les limites propres à chaque sujet. Les réponses constituées uniquement d'un schéma ou d'un extrait de code ont désormais une explication.

La longueur moyenne passe de **55,7 à 66,9 mots hors code**. Les cartes déjà explicites ont généralement été conservées ; les réponses enrichies restent centrées sur leur question.

## Pertinence et corrections

Les questions ambiguës ont été rendues plus autonomes en précisant le sujet, notamment LangChain, LangGraph, CrewAI, l'inférence ou le prompt caching. Les descriptions de mécanismes remplacent les formulations trop télégraphiques. Les chiffres d'une étude, les hypothèses d'un calcul et les garanties conditionnelles sont distingués des règles générales.

Exemples de corrections :

- **RAG et agents** : citation à vérifier, séparation entre arrêt et succès, effet du parallélisme sur coût et délai.
- **Frameworks** : reprise d'un nœud LangGraph, limites de la persistance en RAM, responsabilités des middlewares et outils.
- **Inférence et infrastructure** : KV cache, fragmentation résiduelle, différence TPOT/ITL, mémoire des poids et mémoire totale, compatibilité d'une image avec l'hôte.
- **Coûts et évaluations** : unités du coût par token, incertitude d'un score et comparaison appariée, requêtes batch pouvant expirer, risques et coût du shadow testing.
- **Exemples techniques** : paramètre `system` dans l'API Anthropic, autorisation Cedar avec montant en centimes et contexte de confiance.
- **Conformité** : champ territorial et base légale du RGPD, qualification du haut risque, calendrier et transparence de l'AI Act confrontés aux sources institutionnelles.

Les références primaires consultées sont ajoutées dans les sections `Sources` des fiches concernées. Les dates globales de vérification n'ont pas été renouvelées automatiquement : cette intervention constitue une revue ciblée du fond, et non une nouvelle certification de chaque affirmation ou version de produit dans le vault.

## Conservation et validation

Aucune carte n'a été supprimée ou ajoutée. Les **1 553 identifiants Anki** sont identiques à ceux d'avant la revue, afin que la réimportation mette à jour les cartes existantes en conservant leur progression.

Résultats des contrôles :

- **Lint** : 0 erreur et 0 avertissement, avec équivalence de lecture Obsidian/Anki.
- **Catalogues** : README et MOC synchronisés.
- **Tests du dépôt** : 40 tests réussis, incluant le parseur, l'export et la préservation des identifiants historiques.
- **Comparaison avant/après** : les 1 553 identifiants actifs sont conservés.
- **Export Anki** : paquet généré et archive vérifiée ; 1 553 cartes actives avec réponses et 30 anciennes cartes retirées, republiées suspendues selon le fonctionnement existant.

Le paquet `dist/ai-engineering.apkg` est un artefact généré, exclu de Git. La CI le reconstruit et le publie dans la release `anki` après un push sur `main`.

Les exemples nécessitant des fournisseurs de modèles, des GPU ou des services externes n'ont pas été exécutés sur ces infrastructures.
