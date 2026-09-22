# Prompt engineering avancé — Flashcards
Tags: #flashcards #ai-engineering #prompt-engineering #llm

Quel est le rôle du system prompt par rapport au user prompt ?
?
Le **system prompt fixe le cadre** (rôle, règles, format, périmètre) et a priorité ; le **user prompt porte la tâche** du moment.

---

Qu'est-ce que le few-shot prompting ?
?
Fournir des **exemples entrée → sortie** dans le prompt : ancre le format et le style plus efficacement que des instructions abstraites.

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
Pour **séparer sans ambiguïté** instructions, données et exemples : le modèle distingue la consigne du contenu — ce qui limite aussi l'injection accidentelle.

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

## Connexions
- [[92-chainforge-evals-prompts|ChainForge & evals]] — tester systématiquement
- [[35-context-engineering|Context engineering]] — le prompt dans son budget global
- [[63-guided-generation|Guided generation]] — garantir plutôt que demander
- [[91-langfuse-observabilite|Langfuse]] — prompts versionnés
- [[21-rag-fondamentaux|RAG]] — quand le prompt ne suffit plus
- [[00-moc-ai-engineering|MOC AI Engineering]]
