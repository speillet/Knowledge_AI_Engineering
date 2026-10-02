# Prompt engineering avancé — Flashcards
Tags: #flashcards #ai-engineering #prompt-engineering #llm
<!-- summary: system prompt et user prompt, few-shot, few-shot ou fine-tuning, chain-of-thought (coût, balises), self-consistency et ses limites, délimiteurs, décomposition en appels, meta-prompting, prompts versionnés comme du code, anti-patterns. -->


Quel est le rôle du system prompt par rapport au user prompt ? <!--anki:6876605d304e7d7c4d6f-->
?
Le **system prompt fixe le cadre** (rôle, règles, format, périmètre) et a priorité ; le **user prompt porte la tâche** du moment.

---

Qu'est-ce que le few-shot prompting ? <!--anki:64397243675666243d58-->
?
Fournir des **exemples entrée → sortie** dans le prompt : cela ancre format et style plus efficacement que des instructions abstraites. En pratique, **3 à 5 exemples** bien choisis suffisent, et les **cas limites** valent mieux que les cas évidents. Les exemples doivent être **cohérents** avec les consignes, sinon le modèle suit les exemples.

---

À ne pas confondre : few-shot et fine-tuning ? <!--anki:412f6970745161503d55-->
?
- **Few-shot** : les exemples sont dans le **prompt**, donc **payés à chaque appel** et limités par le contexte. Changement instantané, aucune infrastructure
- **Fine-tuning** : les exemples sont **absorbés dans les poids**. Prompts plus courts, comportement plus constant, mais cycle d'entraînement, evals et versionnage ([[51-fine-tuning-adaptation|fine-tuning]])

Règle pratique : commencer en few-shot, passer au fine-tuning quand les exemples deviennent **trop nombreux ou trop coûteux** à renvoyer chaque fois.

---

Qu'est-ce que le chain-of-thought ? <!--anki:787a345e6d216a737677-->
?
Demander un **raisonnement étape par étape** avant la réponse finale. Il améliore nettement les tâches à plusieurs étapes (calcul, logique, analyse), au prix de **plus de tokens de sortie**, donc de coût et de latence.

Pratique : faire raisonner dans une balise dédiée (`<reflexion>`), puis extraire la réponse d'une balise `<reponse>`. Avec un modèle de raisonnement, c'est **natif** et inutile à demander ([[138-modeles-raisonnement|modèles de raisonnement]]).

---

Qu'est-ce que la self-consistency ? <!--anki:627b5e3844466e393e54-->
?
Générer **plusieurs raisonnements indépendants** (température > 0, souvent 5 à 10) et retenir la réponse **majoritaire**. Les erreurs de raisonnement sont variées, les bonnes réponses convergent : le vote les fait ressortir.

Limites : coût multiplié par le nombre d'échantillons, et ne marche que pour des réponses **comparables** (classe, nombre, choix), pas pour un texte libre ([[65-probabilites-sampling|sampling]]).

---

Pourquoi structurer les prompts avec des délimiteurs (XML, Markdown) ? <!--anki:7264742c537b4b63536f-->
?
Pour **séparer sans ambiguïté** instructions, données et exemples : le modèle distingue la consigne du contenu, ce qui limite aussi l'injection accidentelle.
```xml
<role>Tu es analyste support. Réponds uniquement à partir des documents.</role>

<documents>
  <doc id="7">…</doc>
</documents>

<question>Le client peut-il être remboursé ?</question>

<format>JSON : { "reponse": str, "sources": [id], "certitude": "haute|basse" }</format>
```
Ordre utile : **stable d'abord** (rôle, format), **variable à la fin** (documents, question), pour profiter du [[123-caching-agressif|prompt caching]].

---

Dans un prompt, vaut-il mieux formuler les consignes positivement ou négativement ? <!--anki:42213a39796140435942-->
?
**Dire quoi faire** (« réponds en JSON ») fonctionne mieux que quoi ne pas faire (« pas de prose ») — les négations sont plus souvent ignorées.

---

Quand décomposer une tâche en plusieurs appels ? <!--anki:6b42553f48776d65447e-->
?
Quand un **méga-prompt** cumule des objectifs. Signes : chaque correction casse autre chose, les consignes se contredisent, on ne sait pas quelle partie échoue.

Des étapes séparées (extraire → transformer → vérifier) sont plus fiables, **testables unitairement**, et chaque étape peut utiliser le modèle adapté. Le coût : plus d'appels et de latence ([[48-patterns-workflows-agentiques|prompt chaining]]).

---

Qu'est-ce que le meta-prompting ? <!--anki:622b53787c656f4c5f41-->
?
Utiliser un **LLM pour générer ou améliorer des prompts** : critique d'un prompt existant, proposition de variantes, rédaction d'un premier jet à partir d'une description de la tâche.

Utile pour démarrer ou pour repérer des ambiguïtés, mais une variante n'est retenue que si elle **mesure mieux** sur le jeu d'eval ([[92-chainforge-evals-prompts|evals]]). Pour aller plus loin, l'optimisation automatique rend cette boucle systématique ([[12-optimisation-automatique-prompts|DSPy]]).

---

Pourquoi traiter les prompts comme du code ? <!--anki:736c4f6a3c5d3021267c-->
?
Parce qu'ils **déterminent le comportement en production** autant que le code, et qu'un changement d'un mot peut dégrader une catégorie de cas. Donc :
- **Versioning** et historique des changements
- **Tests de régression** sur un golden dataset avant chaque déploiement
- **Revue** par un pair
- **Rollback** rapide

Voir [[13-prompts-production|prompts en production]] et [[91-langfuse-observabilite|prompt management]].

---

Quels anti-patterns courants en écriture de prompts ? <!--anki:7621382e254d7e3f6163-->
?
Prompt **fourre-tout**, exemples **contradictoires** avec les instructions, contexte non trié, redondances — et demander un format strict au lieu de le **[[63-guided-generation|contraindre]]**.

---

## Mises en situation

Mise en situation : un prompt de 400 lignes gère l'extraction, la traduction et le résumé de contrats. Il marche à 70 % et chaque correction en casse une autre partie. Comment reprends-tu le sujet ? <!--anki:4e3842703a752847257c-->
?
1. **Mesurer avant de toucher** : un golden dataset de contrats représentatifs et des evals par sous-tâche, pour savoir ce qui échoue vraiment ([[92-chainforge-evals-prompts|evals]])
2. **Décomposer** : extraire → traduire → résumer, en trois appels testables unitairement, plutôt qu'un méga-prompt
3. **Contraindre la sortie** de l'étape d'extraction par un schéma plutôt que par une consigne de format ([[63-guided-generation|guided generation]])
4. **Nettoyer** : délimiteurs entre instructions, données et exemples, instructions positives, exemples cohérents entre eux
5. **Versionner et tester** chaque changement comme du code, avec rollback possible ([[91-langfuse-observabilite|prompt management]])

**Piège** : réécrire le prompt d'un bloc sans jeu de test, et faire bouger la qualité au hasard.

---

Mise en situation : ton classifieur de tickets a 92 % d'exactitude mais l'équipe support veut 97 %. Tu peux augmenter le coût par ticket. Que testes-tu, et dans quel ordre ? <!--anki:70302e6d375b4b3b7723-->
?
1. **Analyser les erreurs** : les 8 % ressemblent-ils à un problème de définition des classes, d'exemples manquants ou de tickets ambigus ?
2. **Few-shot ciblé** : ajouter des exemples des cas confondus, cohérents avec les consignes
3. **Self-consistency** : plusieurs raisonnements et vote majoritaire, ou un modèle plus fort sur les cas douteux ([[82-routing-llm|cascade]])
4. **Abstention** : renvoyer les cas à faible confiance à un humain plutôt que de forcer une classe ([[65-probabilites-sampling|logprobs]])
5. **Vérifier le plafond** : si deux annotateurs humains ne sont pas d'accord sur ces tickets, 97 % n'est peut-être pas atteignable

**Piège** : empiler les techniques sans mesurer l'apport de chacune sur le même jeu de test.

---

## Connexions
- [[92-chainforge-evals-prompts|ChainForge & evals]] — tester systématiquement
- [[35-context-engineering|Context engineering]] — le prompt dans son budget global
- [[63-guided-generation|Guided generation]] — garantir plutôt que demander
- [[91-langfuse-observabilite|Langfuse]] — prompts versionnés
- [[21-rag-fondamentaux|RAG]] — quand le prompt ne suffit plus
- [[65-probabilites-sampling|Probabilités & sampling]] — température, top-p et self-consistency
- [[138-modeles-raisonnement|Modèles de raisonnement]] — quand le chain-of-thought est natif
- [[143-hallucinations-grounding|Hallucinations & grounding]] — abstention et citations
- [[12-optimisation-automatique-prompts|Optimisation automatique de prompts]] — laisser une métrique choisir la formulation
- [[13-prompts-production|Prompts en production]] — structure, versioning et portabilité
- [[00-moc-ai-engineering|MOC AI Engineering]]
