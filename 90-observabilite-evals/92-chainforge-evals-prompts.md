# ChainForge & évaluation de prompts — Flashcards
Tags: #flashcards #ai-engineering #evals #prompts #llm
<!-- summary: comparer prompts et modèles, evals automatiques, tests de régression et cas qui basculent, evals comme prérequis au déploiement, ordre des variantes et biais d'expérience, contrôle des variables, cas discordants. -->


Qu'est-ce que ChainForge ? <!--anki:50782b535f40475d557e-->
?
Un **environnement visuel open source de comparaison** : relier entrées, prompts, modèles et évaluateurs pour inspecter les sorties côte à côte.

Exemple : deux prompts, deux modèles et trente cas donnent **120 combinaisons** avant répétitions. Cette grille aide à voir qu'une variante améliore les textes courts mais dégrade les documents longs ; un unique exemple flatteur ne le révèle pas.

Conserver paramètres, versions, jeux et résultats, puis confirmer sur des cas tenus à l'écart. L'exploration visuelle facilite l'analyse, pas la preuve statistique. Pour une gate CI reproductible, exporter ou transcrire le protocole dans un workflow automatisable, sans changer subrepticement les critères ([[94-evals-methodologie|méthodologie]]).

---

Pourquoi comparer des variantes de prompt sur une grille commune d'entrées et de modèles plutôt qu'au feeling ? <!--anki:6521623b3457727e2555-->
?
Parce qu'un jugement « au feeling » sur quelques exemples ne permet pas de comparer : une grille **N variantes × M modèles × K entrées**, comme dans ChainForge, montre les écarts en une passe.

La comparaison repose sur les mêmes entrées, des variantes identifiées et des critères d'évaluation explicites. Répéter les essais si les sorties varient et regarder les erreurs par catégorie. L'interface facilite l'expérience ; elle ne choisit pas automatiquement un jeu représentatif et ne transforme pas un score subjectif en mesure fiable.

---

Quels ordres de grandeur pour un jeu d'évaluation ? <!--anki:4346514f6f3c29256635-->
?
La taille dépend de la **précision voulue**, des cas rares et du protocole de comparaison. Quelques dizaines d'exemples peuvent détecter de gros défauts pendant l'itération. Pour un **score unique** proche de 80 %, sous hypothèse d'observations indépendantes :
```text
100 exemples → marge normale à 95 % d'environ ± 8 points
400 exemples → environ ± 4 points
```
Ce ne sont pas des seuils universels de différence détectable entre modèles. Une comparaison appariée dépend de leurs désaccords ; une décision de production demande aussi une couverture des erreurs coûteuses ([[114-reproductibilite-variance|incertitude statistique]]).

---

Quelles évaluations automatiques simples appliquer aux réponses d'un LLM ? <!--anki:767d70246e577d7b7829-->
?
**Exact match, regex, contains, validité JSON, tests de code** — rapides, gratuites et déterministes quand la tâche s'y prête.
```python
import json

def evaluer(sortie, attendu):
    d = json.loads(sortie)                       # syntaxe : erreur si JSON invalide
    assert isinstance(d, dict)                   # structure requise ici : un objet
    assert d["montant"] == attendu["montant"]    # fond
    assert d["devise"] == attendu["devise"]      # la bonne devise, pas seulement une devise autorisée
```
Un JSON parsable n'est pas forcément un objet ni un résultat correct. Ces assertions illustrent une comparaison à la référence ; les types, unités et règles d'arrondi se définissent selon le contrat. Règle : **le plus simple qui marche** ([[94-evals-methodologie|familles d'évaluateurs]]).

Ces contrôles restent aussi bons que leurs références : une valeur attendue fausse produit un test trompeur. Normaliser uniquement les différences sans effet métier, afin de ne pas effacer une erreur de signe, d'unité ou de devise.

---

Qu'est-ce qu'un test de régression de prompts ? <!--anki:632b5d52586e586c503e-->
?
Rejouer le **golden dataset à chaque modification** de prompt ou de modèle, souvent en [[112-cicd-modeles|CI]], et comparer les scores à la version en production.

On regarde les scores globaux **et** les cas qui **basculent** de réussi à échoué : un score stable peut masquer dix régressions compensées par dix améliorations.

Fixer des critères bloquants par risque : un gain rédactionnel ne compense pas une fuite entre clients. Rejouer les cas stochastiques si nécessaire, avec le même protocole pour les deux versions, et examiner les écarts appariés.

---

Pourquoi les evals sont-elles un prérequis au déploiement ? <!--anki:4d4f4667637553714c55-->
?
Sans mesure, impossible de **choisir un modèle**, de **[[82-routing-llm|router]]**, de valider un changement de prompt ou de savoir si une optimisation de coût a dégradé la qualité : on pilote à l'aveugle, sur des impressions tirées de quelques exemples.

Un jeu d'eval de quelques centaines de cas représentatifs est le premier livrable d'un projet LLM, avant le prompt définitif.

Ce volume est un point de départ, pas une preuve suffisante pour les événements rares. Compléter par des cas critiques ciblés et déclarer les limites : zéro erreur observée sur 100 essais ne démontre pas une fiabilité de 100 %.

---

Pourquoi une expérience ChainForge doit-elle mélanger l'ordre des variantes évaluées ? <!--anki:6236646337323261653233373463363638373461373934616261353138313063-->
?
Un **ordre fixe** peut confondre variante et conditions d'exécution : cache chaud, charge fournisseur, dérive temporelle ou fatigue de l'annotateur.

Apparier les entrées entre variantes, randomiser ou entrelacer leur ordre et enregistrer les conditions utiles. Pour un juge comparatif, inverser aussi la position des réponses et masquer leur origine. Refaire les essais nécessaires avec un protocole fixé. Une interface d'expérimentation organise les résultats ; elle ne supprime pas automatiquement les biais dus à la manière dont les appels et les jugements sont exécutés.

---

Pourquoi inspecter les cas où deux prompts donnent des résultats différents avant de choisir le meilleur ? <!--anki:3265333939333431366665383463643239363162383361666362336632383534-->
?
La différence de moyenne peut provenir **de quelques familles d'erreurs importantes**. Les cas discordants montrent ce que la nouvelle formulation gagne et perd.

Les annoter sans connaître la variante lorsque possible, puis vérifier leur poids dans le trafic réel. Une amélioration sur un groupe fréquent peut cacher une régression critique rare. Ajouter les contre-exemples au jeu de développement sans contaminer le test de confirmation indépendant.

---

Pourquoi enregistrer les paramètres effectifs d'une expérience de prompts, même si l'interface montre les valeurs par défaut ? <!--anki:3731353361316166396238663436366661303135613963383931663331343063-->
?
Les valeurs par défaut peuvent **changer avec le fournisseur ou la version**. Ne conserver que le texte du prompt rend alors la comparaison difficile à reproduire.

Exporter modèle résolu, sampling, limites, données et évaluateur, avec leurs versions. Vérifier les paramètres réellement acceptés, car une option ignorée n'est pas une option appliquée. Une capture d'écran ne remplace pas un manifeste exploitable de l'expérience.

---

## Mises en situation

Mise en situation : ton équipe doit choisir entre trois modèles pour une tâche d'extraction, et chacun a son avis. Comment tranches-tu en une journée ? <!--anki:4d6e266669303f537a7a-->
?
1. **Constituer un golden dataset** de 50 à 100 cas réels, avec réponses attendues, y compris des cas difficiles
2. **Définir les métriques** : exactitude par champ, validité du format, coût et latence
3. **Comparer en une passe** les trois modèles sur les mêmes entrées, avec le même prompt puis avec un prompt adapté à chacun
4. **Regarder les erreurs**, pas seulement les scores : le modèle le plus économique peut échouer sur les cas critiques
5. **Décider avec les trois dimensions** : qualité, coût, latence ([[146-choix-modeles|choix de modèle]])

**Piège** : comparer les modèles sur dix exemples choisis à la main, où l'écart observé n'est que du bruit ([[114-reproductibilite-variance|variance]]).

---

Mise en situation : une modification de prompt améliore visiblement les réponses en démonstration, mais tu ne sais pas si elle dégrade autre chose. Que fais-tu avant de la déployer ? <!--anki:726354326a61687c2d2f-->
?
1. **Rejouer le golden dataset** avant et après, sur les mêmes entrées
2. **Analyser en appariant** les résultats cas par cas, pour voir ce qui s'améliore et ce qui casse
3. **Automatiser** ce rejeu en CI, à chaque changement de prompt ou de modèle ([[112-cicd-modeles|eval gate]])
4. **Ajouter les nouveaux cas** découverts en production au dataset, surtout les échecs
5. **Déployer progressivement** et confirmer avec les signaux de production ([[91-langfuse-observabilite|traces]])

**Piège** : valider un prompt sur les exemples qui ont servi à l'écrire.

---

## Sources

- [NIST — test de McNemar pour observations binaires appariées](https://www.itl.nist.gov/div898/software/dataplot/refman1/auxillar/mcnemar.htm)

## Connexions
- [[90-010-evaluation-reponses-llm|Évaluation des réponses]] — choisir les critères et les équivalences admissibles
- [[91-langfuse-observabilite|Langfuse]] — evals en production (scores, datasets)
- [[11-prompt-engineering-avance|Prompt engineering avancé]] — ce qu'on évalue
- [[82-routing-llm|Routing LLM]] — décision fondée sur les evals
- [[63-guided-generation|Guided generation]] — sorties structurées plus faciles à évaluer
- [[21-rag-fondamentaux|RAG]] — évaluer le pipeline de retrieval
- [[112-cicd-modeles|CI/CD des modèles]] — les evals comme gates
- [[114-reproductibilite-variance|Reproductibilité & variance]] — intervalles de confiance, pass@k
- [[94-evals-methodologie|Méthodologie d'évaluation]] — le cadre complet
- [[95-llm-as-judge|LLM-as-a-judge]] — biais et calibration
- [[113-monitoring-drift-feedback|Monitoring & drift]] — qualité en production et boucle de feedback
- [[12-optimisation-automatique-prompts|Optimisation automatique de prompts]] — laisser une métrique choisir la formulation
- [[51-fine-tuning-adaptation|Fine-tuning]] — adapter un modèle, LoRA et QLoRA
- [[65-probabilites-sampling|Probabilités & sampling]] — température, top-p et logprobs
- [[00-moc-ai-engineering|MOC AI Engineering]]
