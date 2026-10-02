# Optimisation automatique de prompts (DSPy) — Flashcards
Tags: #flashcards #ai-engineering #prompt-engineering #dspy #evals #llm
Vérifié le : 29 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.

Qu'est-ce que l'optimisation automatique de prompts ?
?
<!--anki:4e78672b25565b49213f-->
Traiter le prompt comme un **paramètre à optimiser** : un algorithme propose des variantes (instructions, exemples few-shot), les **évalue sur un jeu de données avec une métrique**, et garde les meilleures. L'humain écrit la **métrique et les données**, pas la formulation.

Prérequis non négociable : une **métrique automatique fiable** et quelques dizaines à centaines d'exemples ([[94-evals-methodologie|evals]]).

---

À ne pas confondre : meta-prompting et optimisation automatique ?
?
<!--anki:324e316873327b5041-->
- **Meta-prompting** : un LLM **réécrit** un prompt en une passe, d'après son jugement. Aucune garantie que la nouvelle version soit meilleure ([[11-prompt-engineering-avance|prompt engineering]])
- **Optimisation automatique** : une **boucle de recherche** pilotée par une **métrique** sur un jeu de données. On ne garde une variante que si elle **mesure mieux**

La première est une aide à la rédaction, la seconde une méthode d'ingénierie.

---

Qu'est-ce que DSPy ?
?
<!--anki:68263769686f2178694b-->
Un framework Python (Stanford) qui remplace les prompts écrits à la main par des **programmes** : on déclare **ce que** chaque étape doit faire (signature), on compose des **modules**, et un **optimiseur** génère les instructions et les exemples à partir d'une métrique.
```python
import dspy
dspy.configure(lm=dspy.LM("anthropic/claude-sonnet-4-5"))

class Classer(dspy.Signature):
    """Classe un ticket support."""
    ticket: str = dspy.InputField()
    categorie: str = dspy.OutputField(desc="facturation, technique ou compte")

classer = dspy.ChainOfThought(Classer)
```

---

Que sont les signatures et les modules de DSPy ?
?
<!--anki:41376d40793c6c616c4f-->
- **Signature** : le contrat d'une étape, `entrées -> sorties` typées et décrites (`"question, contexte -> reponse"`). Elle dit **quoi**, jamais **comment**
- **Module** : une stratégie d'appel autour d'une signature. `Predict` (appel simple), `ChainOfThought` (raisonnement puis réponse), `ReAct` (agent avec outils)

Un programme DSPy compose des modules comme un réseau de neurones compose des couches. Les prompts réels sont **générés** et peuvent être inspectés.

---

Comment un optimiseur DSPy améliore-t-il un programme ?
?
<!--anki:4a5525285d734955594c-->
On lui donne le programme, un **jeu d'entraînement** et une **métrique** (`def metrique(exemple, prediction) -> float`), puis on **compile** :
- **BootstrapFewShot** : exécute le programme, garde les traces qui **réussissent la métrique** et les injecte comme exemples few-shot
- **MIPROv2** : cherche conjointement **instructions et exemples** (optimisation bayésienne sur des candidats proposés par un LLM)
- **GEPA** : fait **réfléchir un LLM sur les échecs** (traces et retours textuels de la métrique) pour faire évoluer les instructions

Le résultat est un programme figé, sauvegardé et versionné comme un artefact.

---

Quels autres travaux ont fondé l'optimisation de prompts ?
?
<!--anki:42375e6b5e4274323c29-->
- **APE** (Automatic Prompt Engineer, 2022) : un LLM génère des instructions candidates, on garde la meilleure sur un jeu de validation
- **OPRO** (Google DeepMind, 2023) : le LLM joue l'**optimiseur**, en voyant l'historique des prompts et de leurs scores
- **TextGrad** (2024) : propager des **« gradients » textuels**, des critiques en langage naturel, à travers un pipeline de plusieurs appels

Idée commune : la recherche est **guidée par un score**, pas par l'intuition.

---

Quand l'optimisation automatique vaut-elle son coût ?
?
<!--anki:67365a516b212e525f33-->
- **Pipeline de plusieurs étapes**, où régler chaque prompt à la main devient ingérable
- **Métrique automatique fiable** : correspondance exacte, tests, juge calibré ([[95-llm-as-judge|LLM-as-a-judge]])
- **Changement de modèle** fréquent : on **recompile** pour le nouveau modèle au lieu de tout réécrire
- **Petit modèle** à faire performer : l'optimisation des exemples compense une partie de l'écart

Coût typique : quelques centaines à quelques milliers d'appels LLM par compilation.

---

Quand ne pas utiliser d'optimisation automatique ?
?
<!--anki:79246d48245a6a6b7e25-->
- **Pas de métrique automatique** : l'optimiseur maximiserait du bruit
- **Tâche simple** qu'un bon prompt et trois exemples règlent déjà
- **Moins de quelques dizaines d'exemples** : sur-apprentissage garanti
- **Contraintes de ton ou de conformité** difficiles à mesurer : l'optimiseur peut les sacrifier pour gagner des points

Dans ces cas, un prompt écrit à la main et testé reste plus lisible et plus sûr.

---

Pourquoi un prompt optimisé peut-il sur-apprendre ?
?
<!--anki:643868493d363a6a3b4d-->
L'optimiseur **maximise la métrique sur le jeu d'entraînement** : il peut choisir des exemples ou des formulations qui exploitent des particularités de ces données, ou les **failles de la métrique** (un juge qui préfère les réponses longues, par exemple).

Parades : séparer **entraînement, validation et test**, relire les prompts générés, et vérifier le gain sur un **jeu de test jamais vu** par l'optimiseur ([[151-donnees-curation-annotation|séparation des jeux]]).

---

Un prompt optimisé pour un modèle se transfère-t-il à un autre ?
?
<!--anki:4b547b706e6741336725-->
**Mal.** Les instructions et exemples retenus sont ceux qui marchaient **pour ce modèle** : changer de modèle ou même de version peut annuler le gain. C'est l'argument central de DSPy : on versionne le **programme, la métrique et les données**, et on **recompile** à chaque changement de modèle ([[146-choix-modeles|migration de modèle]]).

---

À ne pas confondre : optimisation de prompts et fine-tuning ?
?
<!--anki:657c2d797d3f60726269-->
- **Optimisation de prompts** : modifie le **texte** envoyé au modèle. Fonctionne avec un modèle **fermé en API**, se relit, se compile en minutes
- **Fine-tuning** : modifie les **poids**. Demande un modèle ouvert ou une API de fine-tuning, plus de données, et produit un modèle à servir ([[51-fine-tuning-adaptation|fine-tuning]])

Ils se combinent : DSPy peut aussi **distiller** un programme optimisé vers un petit modèle fine-tuné (`BootstrapFinetune`).

---

## Mises en situation

Mise en situation : ton pipeline d'extraction en trois étapes (classer, extraire, normaliser) plafonne à 81 % de champs corrects. Chaque retouche manuelle d'un prompt en dégrade un autre. Comment utilises-tu l'optimisation automatique ?
?
<!--anki:66336b21255779726a65-->
1. **Construire le jeu** : 200 documents annotés, séparés en entraînement, validation et test, jamais mélangés
2. **Écrire la métrique** : part des champs exactement corrects après normalisation, calculée par du code
3. **Réécrire le pipeline en modules** : une signature par étape, pour que l'optimiseur règle chaque étape en fonction du score **final**
4. **Compiler** avec BootstrapFewShot puis MIPROv2, en suivant le coût en appels
5. **Valider sur le test**, relire les prompts générés, puis versionner programme, métrique et données ensemble ([[91-langfuse-observabilite|prompt management]])

**Piège** : annoncer le score du jeu d'entraînement, que l'optimiseur a appris par cœur.

---

Mise en situation : ton équipe veut migrer vers un modèle deux fois moins cher, mais les prompts, réglés à la main depuis un an, perdent 6 points sur le nouveau modèle. Que proposes-tu ?
?
<!--anki:6e4d4f6e45767458594c-->
1. **Ne pas réécrire à l'aveugle** : partir du jeu d'eval existant et le compléter avec les cas durs de production ([[153-data-flywheel-versioning|flywheel]])
2. **Formaliser la métrique** que les prompts optimisaient implicitement
3. **Recompiler** les prompts pour le nouveau modèle (instructions et exemples), plutôt que porter ceux de l'ancien
4. **Comparer à coût égal** : score, latence et **coût par tâche réussie** sur le jeu de test ([[121-couts-inference|coûts]])
5. **Basculer progressivement** en canary, avec retour arrière ([[112-cicd-modeles|CI/CD]])

**Piège** : conclure que le nouveau modèle est moins bon alors que seuls les prompts étaient mal adaptés.

---

## Sources

- [DSPy — code et documentation des optimiseurs](https://github.com/stanfordnlp/dspy)

## Connexions
- [[11-prompt-engineering-avance|Prompt engineering avancé]] — les techniques manuelles que l'optimiseur automatise
- [[13-prompts-production|Prompts en production]] — versionner et maintenir le résultat
- [[94-evals-methodologie|Évaluation — méthodologie]] — la métrique est le vrai livrable
- [[95-llm-as-judge|LLM-as-a-judge]] — quand la métrique est un juge
- [[92-chainforge-evals-prompts|ChainForge]] — comparer des variantes à la main
- [[53-donnees-synthetiques-distillation|Distillation]] — du programme optimisé au petit modèle
- [[146-choix-modeles|Choix de modèles]] — recompiler à chaque migration
- [[00-moc-ai-engineering|MOC AI Engineering]]
