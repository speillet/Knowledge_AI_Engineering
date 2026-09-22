# Guided generation (sorties structurées) — Flashcards
Tags: #flashcards #ai-engineering #inference #structured-output #llm

Qu'est-ce que la guided generation ?
?
**Contraindre le décodage** pour que la sortie respecte **à coup sûr** un format : JSON Schema, regex, liste de choix ou grammaire. On parle aussi de **constrained decoding** ou de **structured outputs**.

---

Comment fonctionne-t-elle techniquement ?
?
À chaque pas de décodage, un **automate** (issu du schéma ou de la grammaire) calcule les tokens autorisés ; les autres sont **masqués dans les logits** (probabilité mise à zéro) avant l'échantillonnage.

```text
logits → masque(état de la grammaire) → échantillonnage → mise à jour de l'état
```

---

Demander du JSON dans le prompt ou le contraindre ?
?
Le **[[11-prompt-engineering-avance|prompt]]** (« réponds en JSON ») donne un résultat **probable** : champ manquant, virgule en trop, texte autour. La **contrainte** donne une **garantie syntaxique** : la sortie est toujours parsable.

---

Quels types de contraintes peut-on appliquer ?
?
- **Choix** : une valeur parmi une liste (classification)
- **Regex** : dates, identifiants
- **JSON Schema** : objets typés
- **Grammaire hors contexte (CFG)** : SQL, DSL, code

---

Quels outils implémentent la guided generation ?
?
**XGrammar** (moteur par défaut de vLLM et SGLang), **Outlines**, **llguidance**, **lm-format-enforcer**, et les grammaires **GBNF** de llama.cpp.

---

Et côté API propriétaires ?
?
Les fournisseurs proposent des **structured outputs** : on fournit un JSON Schema (ex. `response_format` de type `json_schema` en mode strict chez OpenAI, structured outputs chez Anthropic) et l'API garantit la conformité.

---

Une sortie valide syntaxiquement est-elle correcte ?
?
**Non.** La contrainte garantit la **forme**, pas le **fond** : les valeurs peuvent être fausses ou inventées. Il faut toujours une **validation métier** (ex. Pydantic, règles) et des [[92-chainforge-evals-prompts|evals]].

---

La contrainte peut-elle dégrader la qualité ?
?
**Oui**, si elle force le modèle trop tôt : on laisse de la place au raisonnement (champ `reasoning` **avant** le champ `answer`, ou raisonnement libre puis extraction structurée). **L'ordre des champs compte.**

---

Quel coût en latence ?
?
Une **compilation de la grammaire** au premier usage (mise en cache ensuite) et un calcul de masque à chaque token, devenu **négligeable** avec les moteurs récents comme XGrammar.

---

Quel lien avec le tool calling ?
?
Les **arguments d'un [[32-tool-calling|appel d'outil]]** sont générés sous contrainte du JSON Schema de l'outil : c'est ce qui rend le tool calling **fiable syntaxiquement**.

---

## Connexions
- [[11-prompt-engineering-avance|Prompt engineering]] — garantir plutôt que demander
- [[32-tool-calling|Tool calling]] — arguments contraints par le schéma
- [[92-chainforge-evals-prompts|Evals]] — des sorties structurées plus faciles à évaluer
- [[62-optimisations-inference|Optimisations d'inférence]] — impact sur le décodage
- [[11-serveurs-inference-llm|Serveurs d'inférence]] — XGrammar intégré à vLLM
- [[00-moc-ai-engineering|MOC AI Engineering]]
