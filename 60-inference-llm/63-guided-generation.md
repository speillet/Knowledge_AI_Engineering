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

À ne pas confondre : mode JSON et structured outputs ?
?
- **Mode JSON** : garantit une sortie en **JSON valide**, mais pas sa **forme** : champs manquants, noms inventés, types faux restent possibles
- **Structured outputs** (schéma strict) : la génération est **contrainte par un JSON Schema** précis, champs obligatoires et types compris

Pour un traitement automatique, préférer toujours le schéma strict ; la validation **métier** reste à faire dans tous les cas.

---

## Mises en situation

Mise en situation : depuis que tu contrains la sortie par un JSON Schema, le JSON est toujours valide mais les réponses sont devenues moins bonnes. Que corriges-tu ?
?
1. **Comprendre** : la contrainte force le modèle à produire la conclusion **immédiatement**, sans place pour raisonner
2. **Ordonner les champs** : un champ `raisonnement` **avant** le champ `reponse`, puisque le modèle génère dans l'ordre
3. **Ou séparer en deux temps** : réponse libre d'abord, extraction structurée ensuite
4. **Simplifier le schéma** : moins de champs obligatoires, énumérations claires, pas d'imbrication inutile
5. **Mesurer** : exactitude métier avant et après, pas seulement le taux de JSON valide ([[94-evals-methodologie|evals]])

**Piège** : conclure que « la génération contrainte dégrade le modèle », alors que c'est l'ordre des champs qui est en cause.

---

Mise en situation : ton extraction de factures renvoie toujours un JSON conforme, mais la comptabilité relève des montants faux. Comment sécurises-tu la chaîne ?
?
1. **Rappeler la limite** : la contrainte garantit la **forme**, jamais le **fond**
2. **Validation métier** : montants cohérents avec les lignes, TVA recalculée, dates plausibles, fournisseur connu
3. **Champ d'abstention** : permettre « non trouvé » plutôt que d'obliger le modèle à inventer une valeur
4. **Confiance** : logprobs ou double extraction pour repérer les cas douteux et les envoyer à un humain ([[144-ux-ia-human-in-the-loop|human-in-the-loop]])
5. **Mesurer en production** : taux d'échec de validation par champ ([[93-monitoring-inference|validations]])

**Piège** : traiter un JSON valide comme une donnée vérifiée, et l'écrire directement en comptabilité.

---

## Connexions
- [[11-prompt-engineering-avance|Prompt engineering]] — garantir plutôt que demander
- [[32-tool-calling|Tool calling]] — arguments contraints par le schéma
- [[92-chainforge-evals-prompts|Evals]] — des sorties structurées plus faciles à évaluer
- [[62-optimisations-inference|Optimisations d'inférence]] — impact sur le décodage
- [[11-serveurs-inference-llm|Serveurs d'inférence]] — XGrammar intégré à vLLM
- [[65-probabilites-sampling|Probabilités & sampling]] — la distribution que le masque modifie
- [[23-knowledge-graphs-ontologies|Knowledge graphs & ontologies]] — extraire entités et relations sous schéma
- [[00-moc-ai-engineering|MOC AI Engineering]]
