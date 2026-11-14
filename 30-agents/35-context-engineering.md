# Context engineering — Flashcards
Tags: #flashcards #ai-engineering #agents #context-engineering #llm
<!-- summary: le contexte comme budget, context rot, compaction, sous-agents, prompt caching, contexte chargé au besoin (just-in-time), invariants de compaction, sélection de contexte, budget de réserve. -->


Qu'est-ce que le context engineering ? <!--anki:6d7964697b53773a6a7e-->
?
L'art de **choisir, à chaque appel, l'ensemble minimal de tokens le plus utile** dans la fenêtre de contexte : instructions, outils, historique, mémoire, documents récupérés.

Il faut conserver ce qui permet la prochaine décision : objectif, contraintes, preuves et état d'avancement. Par exemple, remplacer un long journal d'exécution par un résumé des résultats avec des liens vers les détails. Le but n'est pas de réduire aveuglément les tokens : retirer une exception importante peut coûter plus qu'un contexte légèrement plus long.

---

À ne pas confondre : context engineering et prompt engineering ? <!--anki:267e45776566756838-->
?
Le **[[11-prompt-engineering-avance|prompt engineering]]** optimise la **formulation** d'une instruction ; le **context engineering** gère **tout ce qui entre dans le contexte**, sur la durée d'une session ou d'un agent.

Réécrire « résume ce contrat » en consignes précises relève du prompt engineering. Sélectionner la bonne version du contrat, charger ses annexes, conserver les contraintes utilisateur et résumer les tours précédents relève du context engineering. Une instruction excellente ne compense pas une source manquante ou périmée : il faut travailler sur les deux niveaux.

---

Pourquoi traiter la fenêtre de contexte comme un budget ? <!--anki:6565374d7c3f655b753c-->
?
Chaque token **coûte** (prix, latence, VRAM du [[61-kv-cache-attention|KV cache]]) et **dilue l'attention** : plus le contexte grossit, moins le modèle exploite bien chaque information.
```text
Budget d'un tour d'agent (exemple) :
  system prompt              600 tokens   stable → mis en cache
  définitions de 12 outils  2 400 tokens  stable → mis en cache
  mémoire et préférences      300 tokens
  documents récupérés       3 000 tokens  variable
  historique (8 tours)      4 500 tokens  croît sans cesse ← à compacter
  question                    120 tokens
                           ──────────────
                          ~10 900 tokens par appel, dont 70 % réutilisables
```
Le poste qui grossit tout seul est l'**historique** : c'est lui qu'on compacte en premier.

Réserver aussi de la place pour la **réponse et les prochains résultats d'outils**. La part effectivement cachée dépend d'un préfixe compatible avec le mécanisme du fournisseur : « réutilisable » n'implique pas « cache hit ». Compacter l'historique en conservant décisions, contraintes et références ; perdre une autorisation ou un résultat critique peut coûter plus qu'économiser quelques tokens.

---

Qu'est-ce que le context rot ? <!--anki:493a7c686b5f307c324d-->
?
La **dégradation des performances quand le contexte s'allonge** : informations anciennes contradictoires, bruit accumulé, effet [[22-rag-avance|« lost in the middle »]]. Une grande fenêtre n'est pas un contexte bien utilisé.

Repérer les symptômes : oubli d'une contrainte, répétition d'une recherche ou utilisation d'une ancienne valeur. Réduire les résultats d'outils redondants, garder un état explicite et recharger la source si nécessaire. Comparer la réussite avant et après compaction, car un résumé trop agressif peut lui aussi supprimer une information décisive.

---

Quelles sont les composantes du contexte d'un agent ? <!--anki:6b38662a4c5f6b385871-->
?
- **Instructions** (system prompt)
- **Définitions d'outils**
- **Historique** de la conversation et des résultats d'outils
- **Mémoire** (faits persistés)
- **Connaissances récupérées** ([[21-rag-fondamentaux|RAG]])

Chaque composante a une fonction : définir la tâche, rendre les actions possibles, conserver l'avancement ou apporter des faits. Les documents et résultats d'outils restent des **données à examiner**, pas des instructions de confiance. Réserver aussi assez de place pour la sortie du modèle et pour les observations du prochain tour.

---

Qu'est-ce que la compaction du contexte d'un agent ? <!--anki:6e5f505d713a4b7b5677-->
?
**Résumer l'historique** quand on approche de la limite, pour repartir avec un contexte plus court qui garde décisions, état et tâches en cours. Variante légère : **effacer les vieux résultats d'outils**.

Deux effets de bord : elle **invalide le cache à partir du premier token modifié** et **perd des détails**. Le préfixe antérieur inchangé peut rester réutilisable. Conserver les faits critiques hors contexte ([[39-memoire-agents|mémoire]]).

Exemple de résumé utile : objectif, décisions validées, références des preuves, travail restant et erreurs non résolues. Vérifier qu'une hypothèse n'est pas devenue un fait au passage.

---

À ne pas confondre : compaction, troncature et mémoire ? <!--anki:7229785e5a41372d3b28-->
?
- **Troncature** : on **coupe** les messages les plus anciens. Gratuit, mais on perd tout ce qui est coupé, y compris les décisions prises
- **Compaction** : on **résume** l'historique. Coûte un appel LLM, conserve l'essentiel, mais perd les détails et invalide le cache
- **Mémoire** : on **écrit hors du contexte** les faits durables, et on les relit à la demande. Seule solution qui survit à la session

Les trois se combinent : mémoire pour ce qui doit durer, compaction pour tenir la session, troncature en dernier recours.

---

Comment les sous-agents aident-ils à gérer le contexte ? <!--anki:4f7d3b7869655a2c734e-->
?
Un [[36-orchestration-agents|sous-agent]] explore dans **son propre contexte** et renvoie un résultat ciblé : le principal n'ingère pas toutes ses recherches.

Exemple : déléguer l'identification des limites d'une API avec un retour « limite, condition, référence, incertitude », plutôt qu'un résumé général du fournisseur. Le principal conserve les éléments nécessaires à la décision et peut rouvrir la source d'une affirmation critique.

La séparation réduit l'encombrement du contexte principal, **pas nécessairement les tokens totaux ni le délai**. Éviter les missions redondantes et les délégations qui exigent de retransmettre tout l'historique ; borner question, outils et format de retour.

---

Pourquoi garder un préfixe de prompt stable ? <!--anki:4e48317c44305d665b56-->
?
Pour profiter du **prompt caching** : le fournisseur réutilise le calcul (KV cache) d'un **préfixe identique**. On met le contenu stable (instructions, outils) **au début** et le contenu variable **à la fin**.

Un horodatage ou identifiant variable placé avant les instructions peut empêcher leur réutilisation. Mesurer les tokens réellement lus en cache, car les seuils, durées de conservation et tarifs dépendent du fournisseur. Le cache accélère une partie du calcul d'entrée ; il ne dispense pas de générer la nouvelle réponse ni de vérifier sa qualité.

---

Qu'est-ce que le just-in-time context ? <!--anki:6a6c3e4a7c636c713068-->
?
Ne pas tout charger d'avance : donner à l'agent des **références légères** (chemins de fichiers, requêtes, outils de recherche) et le laisser **récupérer l'information au moment où il en a besoin**.

Par exemple, fournir l'index d'un dépôt puis lire seulement les fichiers concernés. Cela économise du contexte et évite de travailler sur des copies anciennes, à condition que les outils permettent une recherche fiable. Garder les références exactes et les versions consultées ; sinon l'agent peut chercher longtemps ou relire une source qui a changé.

---

Que se passe-t-il si le contexte d'un agent dépasse la fenêtre du modèle ? <!--anki:6435353066396565386132663436363262613562303131313639303632356336-->
?
Selon l'API et sa configuration, la requête est **rejetée ou tronquée**. Ne pas dépendre d'une suppression implicite qui pourrait retirer consignes ou preuves.

Le harness doit **réserver la sortie et compacter avant la limite**. Exemple fictif : une fenêtre totale de 32 000 tokens, avec 4 000 réservés à la génération, laisse au plus 28 000 pour toutes les entrées, outils compris. Ajouter une marge et mesurer le comptage réel. La qualité peut se dégrader avant la saturation : conserver objectif, décisions et sources utiles, pas seulement faire tenir le texte ([[137-long-contexte|long contexte]]).

---

Comment vérifier qu'une compaction conserve les informations indispensables à un agent ? <!--anki:6666353138343263643833373438366638616236346465316337373135373131-->
?
Définir des **invariants à préserver** : objectif courant, contraintes, décisions validées, références de preuves et opérations encore incertaines. Comparer ces éléments avant et après compaction sur des sessions longues.

Tester une reprise qui exige un fait ancien, un refus utilisateur et l'identifiant d'une opération déjà exécutée. Garder les règles d'autorisation dans le contrôle applicatif et les faits durables dans un stockage adapté. Une bonne reformulation du résumé ne suffit pas : mesurer réussite et absence de répétition d'effets après reprise.

---

Pourquoi charger tous les résultats d'outils dans le contexte peut-il réduire la fiabilité d'un agent ? <!--anki:3561363434313836306434663432613262653062303131313334386239633239-->
?
Chaque résultat consomme du budget et peut **diluer les preuves utiles** ou introduire des instructions non fiables. La présence d'une information dans la fenêtre ne garantit pas son utilisation correcte.

Conserver un résumé fidèle avec références, puis charger les détails à la demande. Ne pas résumer les nombres ou contraintes dont l'exactitude est nécessaire sans accès à l'original. Évaluer les réponses après cette sélection, notamment les cas où une exception rare change la décision.

---

Calcul : un agent dispose d'une fenêtre de 32 000 tokens, de 6 000 tokens fixes, de 14 000 d'historique et réserve 4 000 pour la sortie. Quelle place reste-t-il pour les résultats d'outils ? <!--anki:6365636234373061643263313435613062356436623936653764386635363161-->
?
Il reste **32 000 − 6 000 − 14 000 − 4 000 = 8 000 tokens** dans cette convention de comptage.

Un résultat de 12 000 tokens exige donc pagination, sélection ou compaction avant le prochain appel. Prévoir une marge pour les nouveaux messages et les schémas éventuels. Le calcul suppose que la sortie partage ce plafond ; les limites d'entrée et de sortie peuvent être distinctes selon le modèle et l'API.

---

## Mises en situation

Mise en situation : ton agent de support donne de bonnes réponses au début des conversations, puis se dégrade et se contredit au bout d'une heure. Que fais-tu ? <!--anki:463a55674e31642c4634-->
?
1. **Reconnaître le context rot** : le contexte a gonflé, les informations anciennes et contradictoires s'accumulent
2. **Compacter** : résumer l'historique en gardant décisions, état et tâches en cours ; supprimer les vieux résultats d'outils
3. **Sortir les faits durables** vers une mémoire relue à la demande ([[39-memoire-agents|mémoire]])
4. **Just-in-time** : donner des références et laisser l'agent récupérer ce dont il a besoin, plutôt que tout précharger
5. **Mesurer** : longueur de contexte, qualité et coût par tour au fil de la conversation ([[93-monitoring-inference|monitoring]])

**Piège** : passer à un modèle à très grande fenêtre sans rien changer. Le problème est la **qualité** du contexte, pas sa taille.

---

Mise en situation : ton assistant coûte deux fois plus cher que prévu, alors que le system prompt et les définitions d'outils sont identiques à chaque appel. Quelle piste ? <!--anki:6a563d5e6c7b32533143-->
?
1. **Vérifier le prompt caching** : le préfixe est-il réellement stable, ou y insères-tu la date, l'ID de session ou des outils réordonnés ?
2. **Réorganiser** : contenu stable (instructions, outils) au début, contenu variable à la fin ([[123-caching-agressif|caching]])
3. **Mesurer** le taux de tokens lus en cache dans les traces, avant et après
4. **Réduire** ce qui est envoyé à chaque tour : outils inutiles, documents récupérés trop nombreux
5. **Surveiller** le coût par conversation, pas seulement par appel ([[122-finops-llm|FinOps]])

**Piège** : ajouter l'historique complet en tête de prompt, ce qui invalide le cache à chaque tour.

---

Mise en situation : ton agent doit analyser 300 pages de documentation technique pour répondre à une question précise. Comment organises-tu son contexte ? <!--anki:6b6b564f527c422b5958-->
?
1. **Ne pas tout charger** : 300 pages saturent le contexte, coûtent cher et diluent l'attention
2. **Recherche d'abord** : RAG ou outil de recherche pour ne récupérer que les passages utiles ([[21-rag-fondamentaux|RAG]])
3. **Sous-agents** : si plusieurs sections doivent être explorées, chacun travaille dans son contexte et ne remonte qu'un résumé ([[36-orchestration-agents|sous-agents]])
4. **Références plutôt que contenu** : donner la table des matières et des outils de lecture ciblée
5. **Citer** les passages utilisés, pour vérifier la réponse

**Piège** : découper mécaniquement en 10 appels sans mémoire entre eux, et perdre le fil du raisonnement.

---

## Sources

- [Anthropic — gestion du contexte et compaction des agents](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents) — approfondissement ciblé du 12 novembre 2026 ; les exemples pédagogiques sont construits pour cette revue.

- Complément du 14 novembre 2026 — Position et sélection du contexte : [Liu et al. — Lost in the Middle](https://arxiv.org/abs/2307.03172).

## Connexions
- [[11-prompt-engineering-avance|Prompt engineering]] — le prompt dans son budget global
- [[22-rag-avance|RAG avancé]] — placement des chunks
- [[31-agents-fondamentaux|Agents]] — la mémoire de travail de l'agent
- [[61-kv-cache-attention|KV cache]] — le coût mémoire du contexte
- [[36-orchestration-agents|Orchestration multi-agents]] — isoler les contextes
- [[34-harness-plugins|Harness]] — qui assemble le contexte
- [[39-memoire-agents|Mémoire des agents]] — la mémoire long terme en détail
- [[123-caching-agressif|Caching agressif]] — concevoir le contexte pour le cache
- [[137-long-contexte|Long contexte]] — lost in the middle, longueur effective
- [[121-couts-inference|Coûts d'inférence]] — structure du coût et unit economics
- [[13-prompts-production|Prompts en production]] — structure, versioning et portabilité des prompts
- [[132-tokenisation|Tokenisation]] — ce qu'est un token et ce qu'il coûte
- [[43-langchain-agents|LangChain — Agents]] — agents et middleware LangChain
- [[45-langgraph-production|LangGraph — Production]] — persistance, reprise et supervision humaine
- [[49-agents-de-code|Agents de code]] — utiliser et intégrer les agents de code
- [[115-plateformes-agents-gouvernance|Plateformes d'agents — gouvernance]] — identité, politiques, audit et coûts d'une flotte d'agents
- [[00-moc-ai-engineering|MOC AI Engineering]]
