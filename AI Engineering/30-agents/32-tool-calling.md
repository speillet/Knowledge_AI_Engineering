# Tool calling — Flashcards
Tags: #flashcards #ai-engineering #agents #tool-calling #llm

Qu'est-ce que le tool calling (function calling) ?
?
Le mécanisme par lequel un LLM **émet un appel structuré** (nom d'outil + arguments JSON) que **l'application exécute** avant de renvoyer le résultat au modèle.

---

Le modèle exécute-t-il lui-même les outils ?
?
**Non.** Le modèle ne fait que **générer l'intention d'appel** ; c'est l'application (le harnais) qui exécute et renvoie le résultat.

---

Comment déclare-t-on un outil au modèle ?
?
Par un **JSON Schema** : nom, description et paramètres typés.

---

À quoi ressemble la boucle de tool calling ?
?
```text
prompt → le modèle émet tool_call(name, args)
→ l'app exécute → résultat renvoyé au modèle
→ nouveau tool_call ou réponse finale
```

---

Que sont les parallel tool calls ?
?
L'émission de **plusieurs appels d'outils indépendants en une seule réponse**, exécutables simultanément.

---

Que faire quand un outil échoue ?
?
**Renvoyer l'erreur au modèle** comme résultat : il peut corriger ses arguments, réessayer ou changer d'approche.

---

Pourquoi la description des outils est-elle critique ?
?
C'est du **prompt engineering** : le modèle choisit ses outils d'après leurs descriptions — noms clairs, paramètres documentés, cas d'usage explicites.

---

Sur quoi repose la fiabilité syntaxique des arguments ?
?
Sur la **[[63-guided-generation|guided generation]]** : les arguments sont contraints par le JSON Schema de l'outil.

---

## Connexions
- [[31-agents-fondamentaux|Agents]] — la boucle qui consomme les outils
- [[63-guided-generation|Guided generation]] — la garantie syntaxique
- [[33-mcp|MCP]] — standardiser l'accès aux outils
- [[34-harness-plugins|Harness]] — qui exécute réellement
- [[101-securite-llm-guardrails|Sécurité LLM]] — valider avant d'exécuter
- [[00-moc-ai-engineering|MOC AI Engineering]]
