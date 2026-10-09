# Apprendre avec les cartes

Commencer par comprendre une fiche, puis répondre aux cartes **avant de révéler le verso**. Le verso sert à vérifier le raisonnement et ses limites ; il ne faut pas réciter ses phrases mot pour mot. Les expériences de Roediger et Karpicke montrent un bénéfice du rappel actif sur la rétention différée par rapport à la relecture dans les conditions étudiées. Elles ne démontrent pas qu'un score Anki mesure la compétence d'ingénieur. [Étude originale](https://psychnet.wustl.edu/memory/wp-content/uploads/2018/04/Roediger-Karpicke-2006_PsychSci.pdf).

## Commencer sans ouvrir tout le catalogue

Voici un ordre de travail proposé pour un parcours LLM appliqué. Ce sont des étapes à adapter aux acquis, pas un calendrier imposé. Lire les notions préalables avant les exercices, puis mélanger progressivement les cartes déjà comprises.

| Étape | Fiches de départ | Ce qu'il faut pouvoir faire sans le verso |
| --- | --- | --- |
| 1. Choisir une approche | [Choix du modèle](../170-ml-classique/171-choisir-modele-ml.md), [validation](../170-ml-classique/172-validation-metriques-ml.md) | Proposer une baseline et un test sans fuite de données |
| 2. Comprendre le modèle | [Tokenisation](../130-fondamentaux-llm/132-tokenisation.md), [Transformer](../130-fondamentaux-llm/131-transformer-architecture.md) | Expliquer prédiction du prochain token, masque causal et mémoire des poids |
| 3. Interpréter une sortie | [Probabilités et sampling](../60-inference-llm/65-probabilites-sampling.md), [prompts](../10-prompt-engineering/11-prompt-engineering-avance.md) | Appliquer une règle de sampling et distinguer accord, probabilité et exactitude |
| 4. Mesurer la qualité | [Méthodologie d'évaluation](../90-observabilite-evals/94-evals-methodologie.md), [juges](../90-observabilite-evals/95-llm-as-judge.md) | Définir réussite, référence, classe positive et limites d'une mesure |
| 5. Ajouter des connaissances | [Embeddings](../130-fondamentaux-llm/133-embeddings-representations.md), [RAG](../20-rag/21-rag-fondamentaux.md), [evals RAG](../90-observabilite-evals/96-evals-rag-agents.md) | Localiser un échec de retrieval ou de génération et calculer rappel/précision |
| 6. Faire agir un système | [Agents](../30-agents/31-agents-fondamentaux.md), [tool calling](../30-agents/32-tool-calling.md) | Séparer demande du modèle, validation, autorisation et exécution |
| 7. Servir sous contraintes | [Métriques et SLO](../60-inference-llm/64-metriques-slo-inference.md), [coûts](../120-couts-finops/121-couts-inference.md) | Distinguer latence, débit et coût par résultat utile |
| 8. Assembler et exploiter | [System design](../140-system-design-produit/141-system-design-llm.md), [SRE](../110-mlops-cicd/116-sre-incidents-capacite-ia.md) | Justifier une architecture, son évaluation et son comportement sous panne |

Si un calcul bloque, identifier le prérequis : unités et proportions, probabilités conditionnelles, ou incertitude statistique. Les [statistiques pour décider](../90-observabilite-evals/99-statistiques-decisions-experimentales.md) et la [reproductibilité](../110-mlops-cicd/114-reproductibilite-variance.md) aident ensuite à comparer des versions. Approfondir frameworks, HPC, RL et multi-agents selon le projet ; leur présence dans le catalogue ne leur donne pas tous la même priorité.

## Savoir ce que l'on évalue

Avant de retourner la carte, produire une réponse observable, à voix haute ou sur papier. La notion demandée détermine le niveau de détail attendu.

| Type de carte | Réponse à produire | Erreur qui compte |
| --- | --- | --- |
| Définition ou mécanisme | Idée centrale et relation de cause à effet pertinente | Reconnaître seulement le terme sans expliquer son fonctionnement |
| « À ne pas confondre » | Différence décisive et exemple qui sépare les deux notions | Inverser les notions ou donner un exemple valable pour les deux |
| Calcul | Formule, données, unités, résultat et interprétation demandée | Mauvais dénominateur, unités incompatibles ou résultat appris sans méthode |
| Mise en situation | Diagnostic, mesure discriminante, décision conditionnelle et vérification | Proposer une solution sans preuve, ou oublier une contrainte critique du cas |

Les compléments du verso aident à comprendre et à transférer. Omettre un exemple secondaire ne constitue pas automatiquement un échec. En revanche, oublier l'hypothèse qui rend la conclusion valide en est un : « pass^5 = p^5 » sans tenir compte des répétitions indépendantes et de la probabilité constante ne répond pas correctement à une question qui les examine.

Pour une mise en situation, plusieurs démarches peuvent être valides. Comparer les objectifs et les contrôles, pas l'ordre exact des mots. Si le recto ne permet pas de savoir ce qui est attendu, signaler la carte et proposer une question plus précise plutôt que s'attribuer un succès par défaut.

## Se noter dans Anki

| Bouton | Usage |
| --- | --- |
| Again | Réponse oubliée, fausse, ou lacune qui invalide le raisonnement demandé |
| Hard | Réponse correcte, retrouvée difficilement ou avec hésitation |
| Good | Réponse correcte avec l'effort habituel de rappel |
| Easy | Réponse correcte retrouvée sans effort |

**Hard ne signifie pas « oublié mais reconnu en lisant ».** Une formulation personnelle correcte est suffisante ; reconnaître la solution après l'avoir affichée ne l'est pas. En cas d'hésitation entre quatre boutons, Anki permet de se limiter à Again et Good. [Manuel Anki — Studying](https://docs.ankiweb.net/manual/studying).

Choisir un volume de nouvelles cartes compatible avec les révisions dues. Exemple de séance à adapter : révisions dues, lecture d'une notion, quelques nouvelles cartes, puis un calcul ou un cas pratique. Si le retard augmente, réduire l'introduction de nouveautés. Les exercices longs peuvent être travaillés sur papier dans une séance séparée ; la vitesse seule ne mesure pas la compréhension.

## Passer de la réponse connue au raisonnement

Pour un calcul déjà mémorisé, changer les données **sur un brouillon**, résoudre, puis vérifier. Ne pas modifier les identifiants des cartes existantes pour cette simple variation.

Exemple : cinq résultats récupérés contiennent trois passages pertinents, sur six pertinents annotés. On attend `precision@5 = 3/5 = 60 %` et `recall@5 = 3/6 = 50 %`. Pouvoir expliquer pourquoi les dénominateurs diffèrent est aussi important que le résultat. Le calcul suppose des résultats distincts et une référence fiable à la même unité.

Pour une règle, chercher un contre-exemple : une réponse fidèle à un document obsolète peut être fausse pour une question actuelle. Pour une décision, changer une contrainte : que devient la solution si le budget de latence est divisé par deux, si une dépendance tombe ou si l'on manque de labels ?

Tenir un petit journal d'erreurs : `notion | mon raisonnement erroné | correction | nouvel exemple résolu`. Exemple : `capacité KV | arrondir 25,94 à 26 | prendre le plancher | vérifier que 26 requêtes dépassent le budget`. Une erreur récurrente peut indiquer un prérequis manquant ou une carte trop chargée.

## Démontrer la maîtrise au-delà des cartes

Après un bloc, produire un livrable reproductible : notebook de métriques avec données annotées, diagnostic RAG, rapport de charge ou décision d'architecture. Consigner hypothèses, protocole, résultat et limites. Une simulation est utile si elle est annoncée comme telle ; elle ne remplace pas une mesure du service réel.

Le [parcours de mise en pratique senior](pertinence-parcours-senior-2026-10-07.md) et les [ateliers d'inférence](audit-inference-llm-2026-10-08.md) donnent des livrables et critères concrets. Les cartes entretiennent les connaissances nécessaires ; l'expérience de construction, de mesure, d'exploitation et de transmission complète cet apprentissage.

Pour les données, suivre le [parcours data engineering et ses cinq ateliers](audit-data-engineering-2026-10-09.md). L'[atelier SQL exécutable](../examples/data-engineering/atelier_sql.py) permet de prédire puis vérifier les effets des jointures, des valeurs nulles et de la disponibilité temporelle, sans service externe.
