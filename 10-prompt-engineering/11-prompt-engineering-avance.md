# Prompt engineering avancé — Flashcards
Tags: #flashcards #ai-engineering #prompt-engineering #llm

Quel est le rôle du system prompt par rapport au user prompt ?
?
Le **system prompt fixe le cadre** (rôle, règles, format, périmètre) et a priorité ; le **user prompt porte la tâche** du moment.

---

Qu'est-ce que le few-shot prompting ?
?
Fournir des **exemples entrée → sortie** dans le prompt : cela ancre format et style plus efficacement que des instructions abstraites. En pratique, **3 à 5 exemples** bien choisis suffisent, et les **cas limites** valent mieux que les cas évidents. Les exemples doivent être **cohérents** avec les consignes, sinon le modèle suit les exemples.

---

À ne pas confondre : few-shot et fine-tuning ?
?
- **Few-shot** : les exemples sont dans le **prompt**, donc **payés à chaque appel** et limités par le contexte. Changement instantané, aucune infrastructure
- **Fine-tuning** : les exemples sont **absorbés dans les poids**. Prompts plus courts, comportement plus constant, mais cycle d'entraînement, evals et versionnage ([[51-fine-tuning-adaptation|fine-tuning]])

Règle pratique : commencer en few-shot, passer au fine-tuning quand les exemples deviennent **trop nombreux ou trop coûteux** à renvoyer chaque fois.

---

Qu'est-ce que le chain-of-thought ?
?
Demander un **raisonnement étape par étape** avant la réponse : améliore les tâches complexes — les modèles de raisonnement récents l'internalisent.

---

Qu'est-ce que la self-consistency ?
?
Générer **plusieurs raisonnements indépendants** et retenir la réponse **majoritaire** : fiabilité accrue au prix du coût.

---

Pourquoi structurer les prompts avec des délimiteurs (XML, Markdown) ?
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

Instructions positives ou négatives ?
?
**Dire quoi faire** (« réponds en JSON ») fonctionne mieux que quoi ne pas faire (« pas de prose ») — les négations sont plus souvent ignorées.

---

Quand décomposer une tâche en plusieurs appels ?
?
Quand un **méga-prompt** cumule des objectifs : des étapes séparées (extraire → transformer → vérifier) sont plus fiables et testables unitairement.

---

Qu'est-ce que le meta-prompting ?
?
Utiliser un **LLM pour générer ou améliorer des prompts** (critique, variantes), validés ensuite par [[92-chainforge-evals-prompts|evals]].

---

Pourquoi traiter les prompts comme du code ?
?
Parce qu'ils **déterminent le comportement en production** : versioning, tests de régression (golden datasets), review et rollback ([[91-langfuse-observabilite|prompt management]]).

---

Quels anti-patterns courants ?
?
Prompt **fourre-tout**, exemples **contradictoires** avec les instructions, contexte non trié, redondances — et demander un format strict au lieu de le **[[63-guided-generation|contraindre]]**.

---

## Mises en situation

Mise en situation : un prompt de 400 lignes gère l'extraction, la traduction et le résumé de contrats. Il marche à 70 % et chaque correction en casse une autre partie. Comment reprends-tu le sujet ?
?
1. **Mesurer avant de toucher** : un golden dataset de contrats représentatifs et des evals par sous-tâche, pour savoir ce qui échoue vraiment ([[92-chainforge-evals-prompts|evals]])
2. **Décomposer** : extraire → traduire → résumer, en trois appels testables unitairement, plutôt qu'un méga-prompt
3. **Contraindre la sortie** de l'étape d'extraction par un schéma plutôt que par une consigne de format ([[63-guided-generation|guided generation]])
4. **Nettoyer** : délimiteurs entre instructions, données et exemples, instructions positives, exemples cohérents entre eux
5. **Versionner et tester** chaque changement comme du code, avec rollback possible ([[91-langfuse-observabilite|prompt management]])

**Piège** : réécrire le prompt d'un bloc sans jeu de test, et faire bouger la qualité au hasard.

---

Mise en situation : ton classifieur de tickets a 92 % d'exactitude mais l'équipe support veut 97 %. Tu peux augmenter le coût par ticket. Que testes-tu, et dans quel ordre ?
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
