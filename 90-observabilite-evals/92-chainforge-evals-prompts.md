# ChainForge & évaluation de prompts — Flashcards
Tags: #flashcards #ai-engineering #evals #prompts #llm

Qu'est-ce que ChainForge ?
?
Un **environnement visuel open source** pour **comparer systématiquement prompts et modèles** côte à côte (nodes de prompts, d'inputs et d'évaluation).

---

Quel problème ChainForge adresse-t-il ?
?
Le prompt engineering « au feeling » : il permet de **tester un prompt sur N variantes × M modèles × K inputs** en une passe.

---

Qu'est-ce qu'un golden dataset ?
?
Un **jeu d'exemples avec réponses attendues**, servant de référence pour mesurer objectivement un prompt/modèle.

---

Qu'est-ce que le LLM-as-judge ?
?
Utiliser un **LLM pour noter les réponses** d'un autre (pertinence, style, exactitude) — scalable mais à calibrer contre du jugement humain.

---

Quelles évaluations automatiques simples existent ?
?
**Exact match, regex, contains, validité JSON, tests de code** — rapides et objectives quand la tâche s'y prête.

---

Qu'est-ce qu'un test de régression de prompts ?
?
Rejouer le **golden dataset à chaque modification** de prompt/modèle (souvent en [[112-cicd-modeles|CI]]) pour détecter les dégradations.

---

Pourquoi les evals sont-elles un prérequis au déploiement ?
?
Sans mesure, impossible de **choisir un modèle, [[82-routing-llm|router]] ou valider un changement de prompt** : on pilote à l'aveugle.

---

## Connexions
- [[91-langfuse-observabilite|Langfuse]] — evals en production (scores, datasets)
- [[11-prompt-engineering-avance|Prompt engineering avancé]] — ce qu'on évalue
- [[82-routing-llm|Routing LLM]] — décision fondée sur les evals
- [[63-guided-generation|Guided generation]] — sorties structurées plus faciles à évaluer
- [[21-rag-fondamentaux|RAG]] — évaluer le pipeline de retrieval
- [[112-cicd-modeles|CI/CD des modèles]] — les evals comme gates
- [[114-reproductibilite-variance|Reproductibilité & variance]] — intervalles de confiance, pass@k
- [[00-moc-ai-engineering|MOC AI Engineering]]
