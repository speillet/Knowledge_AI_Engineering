# RL agentique & environnements d'entraînement — Flashcards
Tags: #flashcards #ai-engineering #fine-tuning #reinforcement-learning #agents #llm
Vérifié le : 30 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.

Qu'est-ce que le RL agentique ?
?
<!--anki:6966466243243e466b26-->
Entraîner un modèle par **renforcement** sur des **tâches à plusieurs tours** où il utilise des outils : il agit dans un **environnement** (dépôt de code, navigateur, API simulées), et reçoit une **récompense** selon le résultat (tests qui passent, tâche accomplie).

C'est ce qui a fait progresser les modèles récents en code et en usage d'outils, au-delà du simple RLVR sur une réponse unique ([[52-post-training-alignement|RLVR]]).

---

À ne pas confondre : RLVR sur une réponse et RL agentique ?
?
<!--anki:6e73554e47344851597d-->
- **RLVR classique** : une question, **une** réponse, vérifiée automatiquement (résultat mathématique, tests d'une fonction)
- **RL agentique** : une **trajectoire** de dizaines d'actions et d'observations, dans un environnement qui **change d'état**. La récompense arrive souvent **à la fin**

Le second pose des problèmes propres : attribution du mérite entre étapes, trajectoires longues et coûteuses à générer, environnements à faire tourner par milliers.

---

Qu'est-ce qu'un environnement d'entraînement pour agents ?
?
<!--anki:47497e416c2d30714141-->
Un bac à sable **reproductible** qui fournit :
- un **état initial** (dépôt, base de données, compte simulé)
- des **outils** que le modèle peut appeler
- une **fonction de récompense** qui vérifie le résultat
- une **remise à zéro** rapide entre deux épisodes

Il doit tourner **en masse** (des milliers d'épisodes en parallèle) et être **isolé**, car le modèle en entraînement essaie des actions arbitraires ([[96-evals-rag-agents|environnements d'eval]]).

---

À ne pas confondre : récompense de résultat et récompense de processus ?
?
<!--anki:65552155572869485d6c-->
- **Récompense de résultat** (outcome) : note l'**état final**. Simple et difficile à tromper, mais signal **rare** sur les longues tâches
- **Récompense de processus** (process) : note les **étapes intermédiaires**, souvent par un modèle de récompense. Signal plus dense, mais plus facile à exploiter et coûteux à construire

La tendance est aux récompenses de résultat **vérifiables**, complétées de pénalités simples (longueur, format).

---

Comment un agent peut-il tricher pendant le RL ?
?
<!--anki:6b7030485a6f31363057-->
Par **reward hacking** : il maximise la récompense sans faire la tâche.
- **Modifier ou supprimer les tests** pour qu'ils passent
- Coder en dur la **valeur attendue**
- Exploiter une **faille du vérificateur** (sortie mal parsée comptée comme juste)
- Déclarer la tâche finie sans la faire, si le juge le croit

Parades : tests **protégés en écriture**, vérificateurs robustes, **inspection** d'échantillons de trajectoires récompensées ([[52-post-training-alignement|reward hacking]]).

---

Qu'est-ce que le SFT sur trajectoires (rejection sampling) ?
?
<!--anki:75655a326c694a7a2c43-->
Une alternative plus simple au RL : faire tourner un modèle (souvent plus fort) sur de nombreuses tâches, **garder seulement les trajectoires réussies**, puis faire un **fine-tuning supervisé** du modèle cible sur ces trajectoires.

Moins efficace que le RL pour dépasser le modèle d'origine, mais **stable** et accessible, c'est souvent la première étape d'une équipe produit ([[53-donnees-synthetiques-distillation|distillation]]).

---

Pourquoi GRPO est-il populaire pour le RL agentique ?
?
<!--anki:762d3d71285d59625760-->
Il n'a pas besoin de **modèle critique** : pour une même tâche, on génère **plusieurs trajectoires**, et chacune est comparée à la **moyenne du groupe** (avantage relatif). C'est moins de mémoire et d'ingénierie que PPO.

Sur des tâches agentiques, il faut que le groupe contienne **des succès et des échecs** : des tâches trop faciles ou trop dures ne produisent aucun signal ([[52-post-training-alignement|GRPO]]).

---

Pourquoi le choix des tâches d'entraînement est-il décisif ?
?
<!--anki:4a4e643352476b6e4271-->
Le signal d'apprentissage vient des tâches **à la limite des capacités** du modèle : réussies parfois, pas toujours. On construit donc un **curriculum** : filtrer les tâches toujours réussies ou toujours ratées, et augmenter la difficulté au fil de l'entraînement.

La **diversité** compte autant : un modèle entraîné sur un seul type de dépôt ou d'API généralise mal.

---

Quels outils pour faire du RL agentique ?
?
<!--anki:787e2f625a5433466645-->
- **Bibliothèques open source** : verl, OpenRLHF, TRL (GRPO), avec un serveur d'inférence rapide pour générer les trajectoires ([[11-serveurs-inference-llm|vLLM, SGLang]])
- **Services managés** de reinforcement fine-tuning chez certains fournisseurs de modèles, où l'on fournit tâches et **grader**
- **Infrastructure d'environnements** : conteneurs ou microVM par épisode, orchestrés en masse ([[54-entrainement-distribue|entraînement distribué]])

La partie la plus coûteuse est souvent la **génération des trajectoires**, pas la mise à jour des poids.

---

Quand une équipe produit doit-elle faire du RL agentique ?
?
<!--anki:7077524a526d3c78352f-->
Rarement en premier. Dans l'ordre :
1. Prompts, descriptions d'outils et contexte ([[48-patterns-workflows-agentiques|patterns]])
2. Meilleur modèle ou routage
3. SFT sur trajectoires réussies
4. **RL**, si l'on a un **vérificateur fiable**, un **environnement reproductible**, beaucoup de volume et un gain qui justifie des semaines d'ingénierie

Le RL amplifie ce que le vérificateur récompense : un vérificateur imparfait produit un agent qui l'exploite.

---

## Mises en situation

Mise en situation : ton entreprise traite 50 000 tickets par mois avec un agent qui utilise 12 outils internes. Un modèle open weights fine-tuné coûterait 5 fois moins cher, mais réussit 20 points de moins. Comment envisages-tu l'entraînement ?
?
<!--anki:4e5e36736062615121-->
1. **Construire l'environnement** : outils internes simulés à partir de traces réelles, état initial reproductible, vérification du résultat par des règles métier
2. **Commencer par du SFT** sur les trajectoires réussies du modèle actuel, et mesurer l'écart restant
3. **Passer au RL (GRPO)** sur les tâches où le modèle réussit parfois, avec un vérificateur robuste
4. **Surveiller le reward hacking** : inspecter des trajectoires récompensées à chaque itération
5. **Valider** sur un jeu de test séparé, en pass^k et en coût par ticket réussi ([[96-evals-rag-agents|evals d'agents]])

**Piège** : récompenser « le client n'a pas rappelé », que l'agent obtient en clôturant les tickets trop tôt.

---

Mise en situation : pendant un entraînement RL d'un agent de code, le taux de réussite grimpe de 40 % à 85 % en deux jours. Que vérifies-tu avant de te réjouir ?
?
<!--anki:774e2e796e754a55642f-->
1. **Lire des trajectoires récompensées**, au hasard : le code résout-il vraiment le problème ?
2. **Chercher les triches connues** : tests modifiés ou supprimés, valeurs codées en dur, sortie qui trompe le parseur
3. **Évaluer sur un jeu séparé**, avec des tests cachés que l'agent n'a jamais vus
4. **Comparer** avec les capacités générales, pour détecter une régression ailleurs
5. **Corriger le vérificateur** si une faille est trouvée, puis reprendre l'entraînement

**Piège** : publier le modèle sur la seule courbe de récompense d'entraînement.

---

## Connexions
- [[52-post-training-alignement|Post-training & alignement]] — RLHF, GRPO, RLVR et reward hacking
- [[53-donnees-synthetiques-distillation|Données synthétiques & distillation]] — SFT sur trajectoires
- [[51-fine-tuning-adaptation|Fine-tuning]] — quand adapter les poids
- [[96-evals-rag-agents|Évaluation des agents]] — les environnements servent aussi à évaluer
- [[54-entrainement-distribue|Entraînement distribué]] — l'infrastructure d'entraînement
- [[49-agents-de-code|Agents de code]] — le cas d'usage phare du RL agentique
- [[114-reproductibilite-variance|Reproductibilité & variance]] — non-déterminisme et statistiques d'evals
- [[138-modeles-raisonnement|Modèles de raisonnement]] — test-time compute et budget de réflexion
- [[135-pretraining-scaling-laws|Pré-entraînement & scaling laws]] — comment on fabrique un LLM
- [[00-moc-ai-engineering|MOC AI Engineering]]
