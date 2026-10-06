# Guided generation (sorties structurées) — Flashcards
Tags: #flashcards #ai-engineering #inference #structured-output #llm
<!-- summary: masquage des logits, JSON Schema, regex et grammaires, XGrammar et Outlines, structured outputs des API, mode JSON ou structured outputs, validation métier. -->


Qu'est-ce que la guided generation ? <!--anki:574e547021574d687c-->
?
La **guided generation** restreint les tokens autorisés pendant le décodage pour respecter une grammaire ou un schéma supporté : JSON, valeurs d'énumération ou langage spécifique. Le modèle choisit parmi les continuations encore valides.

La garantie porte sur la **structure d'une sortie achevée dans les conditions prévues**. Refus, erreur, troncature et contraintes non supportées doivent être traités séparément. Une date bien formée ou un montant numérique peuvent rester faux : la validation métier reste nécessaire.

---

Comment la guided generation contraint-elle techniquement le décodage ? <!--anki:77513f6a2e546e395d69-->
?
À chaque pas de décodage, un **automate** (issu du schéma ou de la grammaire) calcule les tokens autorisés ; les autres sont **masqués dans les logits** (probabilité mise à zéro) avant l'échantillonnage.

```text
logits → masque(état de la grammaire) → échantillonnage → mise à jour de l'état
```

Par exemple, après une clé JSON attendue, le moteur n'autorise que les tokens compatibles avec sa valeur et la suite du schéma. Le masque est mis à jour à chaque token, lequel peut représenter plusieurs caractères. Le schéma doit rester satisfaisable et ses fonctionnalités être supportées par le moteur.

---

Demander du JSON dans le prompt ou le contraindre ? <!--anki:7352453c3f755a7a7363-->
?
Une consigne « réponds en JSON » **oriente** la génération, mais peut produire du texte autour de l'objet, des champs manquants ou une syntaxe invalide. Le décodage contraint restreint effectivement les continuations possibles.

Distinguer **JSON valide** et **conformité à un schéma** : un objet parsable peut avoir les mauvais champs. Même en mode strict, vérifier le statut de fin, les refus et les sorties tronquées avant de parser, puis appliquer les règles métier. Une contrainte de format ne remplace pas ces contrôles.

---

Quels types de contraintes peut-on appliquer au décodage d'un LLM ? <!--anki:694a55557556246d483b-->
?
- **Choix** : une valeur parmi une liste (classification)
- **Regex** : dates, identifiants
- **JSON Schema** : objets typés
- **Grammaire hors contexte (CFG)** : SQL, DSL, code

Choisir la contrainte minimale qui exprime le besoin. Une regex de date impose une forme mais peut accepter un jour inexistant ; une grammaire SQL n'impose pas les droits d'accès ni un coût de requête raisonnable. Tester les contraintes réellement prises en charge et compléter par une validation sémantique côté application.

---

Quel moteur de guided generation selon le serveur : vLLM ou SGLang, llama.cpp, ou une bibliothèque Python ? <!--anki:3533363362333633333436643465666461633639333739356631636532343066-->
?
- **vLLM et SGLang** : **XGrammar** par défaut, d'autres moteurs en option (llguidance, Outlines)
- **llama.cpp** : les grammaires **GBNF**
- **En bibliothèque Python**, autour de son propre code d'inférence : **Outlines**, lm-format-enforcer

Les API propriétaires n'exposent que le JSON Schema : leur moteur est caché.

---

Comment obtenir une sortie structurée garantie avec une API propriétaire ? <!--anki:6b4237606b477d4d3c74-->
?
Les fournisseurs proposent des **structured outputs** : on fournit un JSON Schema (ex. `response_format` de type `json_schema` en mode strict chez OpenAI, structured outputs chez Anthropic) et l'API garantit la conformité.

La garantie dépend du modèle, du mode choisi et du sous-ensemble de JSON Schema accepté. Prévoir une branche pour les refus et les réponses interrompues par la limite de sortie. Pour un flux streamé, attendre l'objet complet avant de le traiter comme un résultat valide ; des fragments seuls peuvent être impossibles à parser.

---

Une sortie valide syntaxiquement est-elle correcte ? <!--anki:49726331503b73342157-->
?
**Non.** La contrainte garantit la **forme**, pas le **fond** : les valeurs peuvent être fausses ou inventées. Il faut toujours une **validation métier** (ex. Pydantic, règles) et des [[92-chainforge-evals-prompts|evals]].

Par exemple, un objet JSON portant un montant de 120 est bien typé mais peut contredire une facture de 12 euros. Pydantic vérifie les contraintes déclarées ; seule une comparaison à la source ou une règle métier détectera certaines erreurs factuelles. Une action externe doit aussi vérifier l'autorisation, indépendamment de la validité du JSON.

---

La contrainte de format peut-elle dégrader la qualité d'une réponse LLM ? <!--anki:7669615e6153286a544d-->
?
**Oui.** Un schéma trop étroit peut forcer une réponse alors qu'il manque des informations, ou imposer un ordre de génération défavorable à la tâche. Prévoir des champs d'incertitude, une valeur nulle ou une catégorie « information absente » lorsque cela a du sens.

Comparer plusieurs schémas sur des exemples difficiles et séparer analyse et extraction si cela apporte un gain mesuré. Ajouter un champ `reasoning` n'est pas une recette universelle ; une courte justification ou des références vérifiables sont souvent plus utiles à l'application.

---

Quel coût en latence ajoute la guided generation ? <!--anki:4b3d5e5e4934672e2836-->
?
La contrainte peut ajouter une **préparation du schéma ou de la grammaire**, puis un calcul du masque pendant la génération. Certains moteurs mettent les structures préparées en cache et optimisent fortement ce travail.

Le surcoût dépend de la complexité du schéma, du moteur, du cache et du nombre de requêtes : il n'est pas toujours négligeable. Mesurer premier appel et appels suivants séparément, puis vérifier le débit sous charge avec les schémas réellement utilisés.

---

Quel lien entre guided generation et tool calling ? <!--anki:727c60472d7655416165-->
?
Le tool calling décrit un outil et ses arguments attendus, souvent par **JSON Schema**. Un mode strict de sortie structurée peut contraindre leur génération, mais **tout appel d'outil n'est pas automatiquement décodé sous contrainte** : cela dépend du fournisseur et de la configuration.

L'application doit donc valider nom, arguments, permissions et règles métier avant d'exécuter. Même des arguments parfaitement conformes peuvent viser le mauvais compte ou déclencher une action non autorisée ([[32-tool-calling|tool calling]]).

---

À ne pas confondre : mode JSON et structured outputs ? <!--anki:41673b782e4245765374-->
?
- **Mode JSON** : garantit une sortie en **JSON valide**, mais pas sa **forme** : champs manquants, noms inventés, types faux restent possibles
- **Structured outputs** (schéma strict) : la génération est **contrainte par un JSON Schema** précis, champs obligatoires et types compris

Pour un traitement automatique, préférer toujours le schéma strict ; la validation **métier** reste à faire dans tous les cas.

---

Que se passe-t-il si la génération atteint `max_tokens` au milieu d'un JSON contraint ? <!--anki:3731663364663939323734313431373261653832636436653336323231626565-->
?
La sortie est **tronquée** et le JSON est invalide, malgré la contrainte : la guided generation garantit que chaque token **respecte** la grammaire, pas que la génération **aille jusqu'au bout**.

La réponse l'indique (`finish_reason: "length"` ou `stop_reason: "max_tokens"`). Il faut **vérifier ce champ**, dimensionner `max_tokens` pour le pire cas, et borner la taille du schéma (listes de longueur maximale).

---

## Mises en situation

Mise en situation : depuis que tu contrains la sortie par un JSON Schema, le JSON est toujours valide mais les réponses sont devenues moins bonnes. Que corriges-tu ? <!--anki:4b54485521782c4c4a72-->
?
1. **Comprendre** : la contrainte force le modèle à produire la conclusion **immédiatement**, sans place pour raisonner
2. **Ordonner les champs** : un champ `raisonnement` **avant** le champ `reponse`, puisque le modèle génère dans l'ordre
3. **Ou séparer en deux temps** : réponse libre d'abord, extraction structurée ensuite
4. **Simplifier le schéma** : moins de champs obligatoires, énumérations claires, pas d'imbrication inutile
5. **Mesurer** : exactitude métier avant et après, pas seulement le taux de JSON valide ([[94-evals-methodologie|evals]])

**Piège** : conclure que « la génération contrainte dégrade le modèle », alors que c'est l'ordre des champs qui est en cause.

---

Mise en situation : ton extraction de factures renvoie toujours un JSON conforme, mais la comptabilité relève des montants faux. Comment sécurises-tu la chaîne ? <!--anki:4e243d382b5961484041-->
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
- [[132-tokenisation|Tokenisation]] — ce qu'est un token et ce qu'il coûte
- [[142-fiabilite-resilience-llm|Fiabilité & résilience]] — timeouts, retries, fallbacks et dégradation
- [[148-pipelines-batch-llm|Pipelines batch]] — traiter des millions d'items à moindre coût
- [[146-choix-modeles|Choix de modèles]] — critères, benchmarks et migration
- [[00-moc-ai-engineering|MOC AI Engineering]]
