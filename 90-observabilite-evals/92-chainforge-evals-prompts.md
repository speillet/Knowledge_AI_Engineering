# ChainForge & évaluation de prompts — Flashcards
Tags: #flashcards #ai-engineering #evals #prompts #llm

Qu'est-ce que ChainForge ?
?
Un **environnement visuel open source** pour **comparer systématiquement prompts et modèles** côte à côte : on relie des nœuds d'entrées, de prompts, de modèles et d'évaluateurs, et on visualise les résultats en grille.

Utile en **phase d'exploration** : choisir un modèle, tester des variantes de prompt sur quelques dizaines de cas. Pour les evals en CI et en production, on passe à des outils scriptables ([[94-evals-methodologie|méthodologie]]).

---

Quel problème ChainForge adresse-t-il ?
?
Le prompt engineering « au feeling » : il permet de **tester un prompt sur N variantes × M modèles × K inputs** en une passe.

---

Qu'est-ce qu'un golden dataset ?
?
Un **jeu d'exemples avec réponses ou critères attendus**, qui sert de référence pour comparer prompts et modèles. Il est **versionné**, **stratifié** par type de requête, et **enrichi à chaque bug** trouvé en production ([[94-evals-methodologie|construction]]).

---

Quels ordres de grandeur pour un jeu d'évaluation ?
?
```text
20 à 50 exemples    itérer vite sur un prompt, détecter les gros écarts
100 exemples        écart mesurable ≈ 8 points (à 80 % de réussite)
400 exemples        écart mesurable ≈ 4 points
1 000 et plus       décision de mise en production, comparaison fine
```
La règle : la taille dépend de **l'écart qu'on veut détecter**. Sur 100 exemples, un gain de 3 points ne prouve rien ([[114-reproductibilite-variance|intervalles de confiance]]).

---

Qu'est-ce que le LLM-as-judge ?
?
Utiliser un **LLM pour noter les réponses** d'un autre (pertinence, style, exactitude par rapport à une référence) : c'est ce qui permet d'évaluer des milliers de réponses en texte libre.

Il a des **biais** (position, longueur, auto-préférence) et doit être **validé contre des annotations humaines** avant qu'on se fie à ses scores. Détails dans [[95-llm-as-judge|LLM-as-a-judge]].

---

Quelles évaluations automatiques simples existent ?
?
**Exact match, regex, contains, validité JSON, tests de code** — rapides, gratuites et déterministes quand la tâche s'y prête.
```python
def evaluer(sortie, attendu):
    assert json.loads(sortie)                    # forme
    d = json.loads(sortie)
    assert d["montant"] == attendu["montant"]    # fond
    assert d["devise"] in {"EUR", "USD"}         # domaine
```
Règle : **le plus simple qui marche**. On ne sort le juge LLM que pour ce que le code ne sait pas vérifier ([[94-evals-methodologie|familles d'évaluateurs]]).

---

Qu'est-ce qu'un test de régression de prompts ?
?
Rejouer le **golden dataset à chaque modification** de prompt ou de modèle, souvent en [[112-cicd-modeles|CI]], et comparer les scores à la version en production.

On regarde les scores globaux **et** les cas qui **basculent** de réussi à échoué : un score stable peut masquer dix régressions compensées par dix améliorations.

---

Pourquoi les evals sont-elles un prérequis au déploiement ?
?
Sans mesure, impossible de **choisir un modèle**, de **[[82-routing-llm|router]]**, de valider un changement de prompt ou de savoir si une optimisation de coût a dégradé la qualité : on pilote à l'aveugle, sur des impressions tirées de quelques exemples.

Un jeu d'eval de quelques centaines de cas représentatifs est le premier livrable d'un projet LLM, avant le prompt définitif.

---

## Mises en situation

Mise en situation : ton équipe doit choisir entre trois modèles pour une tâche d'extraction, et chacun a son avis. Comment tranches-tu en une journée ?
?
1. **Constituer un golden dataset** de 50 à 100 cas réels, avec réponses attendues, y compris des cas difficiles
2. **Définir les métriques** : exactitude par champ, validité du format, coût et latence
3. **Comparer en une passe** les trois modèles sur les mêmes entrées, avec le même prompt puis avec un prompt adapté à chacun
4. **Regarder les erreurs**, pas seulement les scores : le modèle le plus économique peut échouer sur les cas critiques
5. **Décider avec les trois dimensions** : qualité, coût, latence ([[146-choix-modeles|choix de modèle]])

**Piège** : comparer les modèles sur dix exemples choisis à la main, où l'écart observé n'est que du bruit ([[114-reproductibilite-variance|variance]]).

---

Mise en situation : une modification de prompt améliore visiblement les réponses en démonstration, mais tu ne sais pas si elle dégrade autre chose. Que fais-tu avant de la déployer ?
?
1. **Rejouer le golden dataset** avant et après, sur les mêmes entrées
2. **Analyser en appariant** les résultats cas par cas, pour voir ce qui s'améliore et ce qui casse
3. **Automatiser** ce rejeu en CI, à chaque changement de prompt ou de modèle ([[112-cicd-modeles|eval gate]])
4. **Ajouter les nouveaux cas** découverts en production au dataset, surtout les échecs
5. **Déployer progressivement** et confirmer avec les signaux de production ([[91-langfuse-observabilite|traces]])

**Piège** : valider un prompt sur les exemples qui ont servi à l'écrire.

---

## Connexions
- [[91-langfuse-observabilite|Langfuse]] — evals en production (scores, datasets)
- [[11-prompt-engineering-avance|Prompt engineering avancé]] — ce qu'on évalue
- [[82-routing-llm|Routing LLM]] — décision fondée sur les evals
- [[63-guided-generation|Guided generation]] — sorties structurées plus faciles à évaluer
- [[21-rag-fondamentaux|RAG]] — évaluer le pipeline de retrieval
- [[112-cicd-modeles|CI/CD des modèles]] — les evals comme gates
- [[114-reproductibilite-variance|Reproductibilité & variance]] — intervalles de confiance, pass@k
- [[94-evals-methodologie|Méthodologie d'évaluation]] — le cadre complet
- [[95-llm-as-judge|LLM-as-a-judge]] — biais et calibration
- [[00-moc-ai-engineering|MOC AI Engineering]]
