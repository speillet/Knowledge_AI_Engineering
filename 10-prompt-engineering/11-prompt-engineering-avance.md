# Prompt engineering avancé — Flashcards
Tags: #flashcards #ai-engineering #prompt-engineering #llm
<!-- summary: system prompt et user prompt, few-shot, few-shot ou fine-tuning, chain-of-thought (coût, balises), self-consistency et ses limites, délimiteurs, décomposition en appels, meta-prompting, prompts versionnés comme du code, anti-patterns. -->


Quel est le rôle du system prompt par rapport au user prompt ? <!--anki:6876605d304e7d7c4d6f-->
?
Le **system prompt fixe le cadre** (rôle, règles, format, périmètre) et a priorité ; le **user prompt porte la tâche** du moment.

Par exemple, le système définit un assistant de support qui cite sa documentation ; l'utilisateur demande comment réinitialiser son compte. Le cadre doit préciser quoi faire si l'information manque. **Une instruction de priorité supérieure n'est pas une barrière de sécurité** : les permissions et validations des actions restent appliquées par le code.

---

Qu'est-ce que le few-shot prompting ? <!--anki:64397243675666243d58-->
?
Le **few-shot prompting** fournit des exemples entrée → sortie dans le contexte, sans modifier les poids. Les exemples montrent le format et les distinctions attendues, notamment les cas faciles à confondre.

Choisir des exemples cohérents avec la consigne, diversifiés et distincts du test final. Leur nombre, ordre et proximité avec la requête peuvent changer le résultat : comparer au zero-shot puis mesurer le gain et le coût. « Trois à cinq exemples suffisent » n'est pas une règle universelle. Des exemples contradictoires créent une ambiguïté, sans garantir lequel le modèle suivra.

---

À ne pas confondre : few-shot et fine-tuning ? <!--anki:412f6970745161503d55-->
?
Le **few-shot** fournit les exemples à l'exécution dans le prompt ; le **fine-tuning** utilise des exemples d'entraînement pour modifier les paramètres, parfois seulement des adaptateurs.

Le premier permet une itération rapide mais consomme du contexte ; le second demande données, entraînement et validation. Il ne garantit pas, à lui seul, un comportement plus constant ou une mémorisation fiable des faits. Commencer par une baseline simple, puis comparer à qualité et coût de service équivalents. Le nombre d'exemples à renvoyer est un motif d'étude du fine-tuning, pas un critère suffisant pour basculer.

---

Qu'est-ce que le chain-of-thought ? <!--anki:787a345e6d216a737677-->
?
Le **chain-of-thought prompting** donne ou sollicite des étapes intermédiaires avant une réponse. Il peut aider certaines tâches de raisonnement, avec davantage de tokens et sans garantie d'exactitude.

Les étapes écrites ne prouvent ni la validité du résultat ni la fidélité au calcul interne. Selon le modèle, son raisonnement peut rester interne : suivre le mode d'usage prévu et comparer des résultats vérifiables plutôt qu'exiger une trace détaillée. Pour une application, demander les preuves, calculs ou justifications utiles à la validation ; des balises ne rendent pas une conclusion correcte.

---

Qu'est-ce que la self-consistency ? <!--anki:627b5e3844466e393e54-->
?
Échantillonner plusieurs solutions, **extraire des réponses finales comparables**, puis les agréger, souvent par vote. Des chemins différents peuvent aboutir à une même réponse ; le coût augmente avec les tentatives.

La majorité peut répéter une erreur commune au modèle ou au prompt. Des tirages indépendants conditionnellement au prompt n'impliquent pas des erreurs indépendantes face au monde réel. Pour du texte libre, définir d'abord une normalisation ou une comparaison fiable ; le vote textuel brut ne suffit pas. Mesurer le gain sur validation et prévoir le traitement des égalités et abstentions.

---

Pourquoi structurer les prompts avec des délimiteurs (XML, Markdown) ? <!--anki:7264742c537b4b63536f-->
?
Les **délimiteurs** rendent les rôles des blocs plus lisibles : instruction, document, exemple ou question. Ils aident à concevoir un prompt vérifiable, mais ne créent pas une frontière de sécurité.
```xml
<documents><doc id="7">Données à analyser…</doc></documents>
<question>Le document autorise-t-il ce remboursement ?</question>
```
Un document peut lui-même contenir des instructions hostiles ou des balises. Utiliser les rôles structurés disponibles et contrôler les actions dans l'application. Placer le préfixe stable avant les données variables peut aider le cache, à condition de préserver la clarté et de mesurer la qualité.

---

Dans un prompt, vaut-il mieux formuler les consignes positivement ou négativement ? <!--anki:42213a39796140435942-->
?
Privilégier une **action attendue explicite**, accompagnée d'un exemple : « Retourne un objet JSON avec `statut` et `motif` » est plus opérationnel que « N'écris pas de prose ». Une interdiction reste utile pour nommer une limite, mais il faut indiquer la conduite de remplacement : « Si la source manque, indique que tu ne sais pas ».

Ce n'est pas une loi sur les négations : comparer les formulations sur des cas représentatifs. Pour un format strict, utiliser aussi un schéma et une validation applicative.

---

Quand décomposer une tâche en plusieurs appels ? <!--anki:6b42553f48776d65447e-->
?
Décomposer quand des sous-tâches ont des **entrées, sorties et critères vérifiables distincts** : extraction, traduction, puis synthèse, par exemple. Cela facilite le diagnostic et permet d'adapter les modèles à chaque étape.

La décomposition n'améliore pas automatiquement la fiabilité : une erreur d'extraction peut contaminer toutes les étapes suivantes. Prévoir validation des interfaces, traitement d'échec et budget global. Comparer à une baseline en un appel sur les mêmes tâches, avec coût et latence. Conserver plusieurs appels seulement si leur contrôle ou leur gain mesuré justifie la complexité.

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

Ils rendent la tâche ambiguë : le modèle doit arbitrer entre des objectifs incompatibles ou chercher l'information utile dans du bruit. **Séparer objectif, données et format attendu**, harmoniser les exemples, puis tester les cas limites. Un prompt long n'est pas mauvais en soi ; chaque partie doit contribuer à un comportement vérifiable.

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

## Sources

- [Wei et al. — chain-of-thought prompting](https://arxiv.org/abs/2201.11903)
- [Wang et al. — self-consistency](https://arxiv.org/abs/2203.11171)
- [Turpin et al. — limites de fidélité des explications](https://arxiv.org/abs/2305.04388)

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
- [[51-fine-tuning-adaptation|Fine-tuning]] — distinguer exemples dans le prompt et adaptation des poids
- [[00-moc-ai-engineering|MOC AI Engineering]]
