# Évaluation des RAG & des agents — Flashcards
Tags: #flashcards #ai-engineering #evals #rag #agents #llm

Comment découper l'évaluation d'un RAG ?
?
En deux étages :
1. **Retrieval** : les bons passages sont-ils remontés ? (recall@k, precision@k, MRR, nDCG)
2. **Génération** : la réponse est-elle **fidèle** aux passages et **répond-elle** à la question ?

Un mauvais score global ne dit pas lequel corriger ; les métriques par étage, si.

---

Que mesurent recall@k, MRR et nDCG ?
?
- **Recall@k** : part des passages pertinents présents dans les **k premiers** — la métrique clé, car le LLM ne voit que ceux-là.
- **MRR** (Mean Reciprocal Rank) : **1/rang** du premier résultat pertinent, moyenné.
- **nDCG** : qualité du **classement** avec pertinence graduée, pénalisant les bons résultats placés bas.

---

Quelle est la « triade RAG » ?
?
1. **Context relevance** : les passages récupérés sont-ils pertinents pour la question ?
2. **Faithfulness / groundedness** : chaque affirmation de la réponse est-elle **soutenue par le contexte** ?
3. **Answer relevance** : la réponse traite-t-elle **la question posée** ?

C'est la base de [[22-rag-avance|RAGAS]] et des évaluateurs équivalents.

---

Comment mesurer la faithfulness ?
?
Décomposer la réponse en **affirmations atomiques**, puis faire vérifier par un [[95-llm-as-judge|juge]] (ou un modèle NLI) que chacune est **impliquée par le contexte**. Score = affirmations soutenues / total. Une réponse **vraie mais absente du contexte** compte comme non fidèle : elle révèle une connaissance paramétrique non vérifiée.

---

Comment construire un jeu d'eval de retrieval sans annotation manuelle massive ?
?
**Génération synthétique** : pour chaque chunk, faire écrire par un LLM des **questions dont ce chunk est la réponse** → paires (question, chunk attendu). À compléter par des **questions réelles** annotées, car les questions synthétiques sont souvent **trop proches du texte** (recouvrement lexical) et surestiment le recall.

---

Qu'évalue-t-on dans un agent ?
?
- **Résultat final** : la tâche est-elle accomplie ? (vérifiable par l'**état final** : fichier créé, ticket fermé, tests verts)
- **Trajectoire** : bons outils, bons arguments, pas d'étapes inutiles ni dangereuses.
- **Efficacité** : nombre d'étapes, tokens, coût, durée.
- **Sécurité** : actions interdites évitées, demandes de confirmation respectées.

---

Pourquoi préférer vérifier l'état final plutôt que la trajectoire exacte ?
?
Parce qu'il existe **plusieurs chemins valides** : imposer une séquence exacte d'appels pénalise des solutions correctes et rend l'eval **fragile**. On vérifie le **résultat** dans un environnement contrôlé, et on n'impose sur la trajectoire que des **contraintes** (outil interdit, étape obligatoire, budget max).

---

Qu'est-ce qu'un environnement d'eval pour agents ?
?
Un **bac à sable reproductible** : faux services (API mockées, base de test, dépôt git figé), **utilisateur simulé** par un LLM pour les conversations multi-tours, et **vérificateur automatique** de l'état final. Exemples publics : **τ-bench** (support client), **SWE-bench** (correction de bugs), **WebArena**, **OSWorld**.

---

Pourquoi pass^k est-il crucial pour un agent en production ?
?
**pass@k** = au moins un succès sur k essais (capacité) ; **pass^k** = **k succès sur k** (fiabilité). Un agent à 70 % de succès par essai n'a que **≈ 34 %** de pass^3. En production, l'utilisateur subit **chaque** essai : c'est pass^k qui compte ([[114-reproductibilite-variance|pass@k et pass^k]]).

---

Comment évaluer l'appel d'outils (tool calling) isolément ?
?
Sur des cas unitaires : pour une requête donnée, vérifier **le choix de l'outil**, la **validité des arguments** (schéma, valeurs), les cas où **aucun outil** ne doit être appelé, et les **appels parallèles**. Évaluations **par règles**, rapides et déterministes → idéales en [[112-cicd-modeles|CI]].

---

Comment évaluer une conversation multi-tours ?
?
Avec un **simulateur d'utilisateur** (LLM avec un persona et un objectif) qui dialogue avec le système jusqu'à la fin, puis un juge sur **l'objectif atteint**, la **cohérence** entre les tours et la **gestion des changements d'avis**. Il faut rejouer **plusieurs fois** : le simulateur ajoute sa propre variance.

---

Quelles métriques d'efficacité suivre en plus de la qualité ?
?
**Tokens et coût par tâche réussie**, **nombre d'étapes**, **latence de bout en bout**, taux de **boucles** ou d'abandons. Un agent plus précis mais trois fois plus cher n'est pas forcément meilleur : on compare sur un **front qualité / coût** ([[122-finops-llm|FinOps]]).

---

## Mises en situation

Mise en situation : ton RAG affiche 62 % de réponses jugées correctes, et l'équipe veut changer de modèle de génération. Comment vérifies-tu que c'est le bon levier ?
?
1. **Découper la mesure** : recall@k du retrieval d'un côté, fidélité et pertinence de la génération de l'autre
2. **Si le recall est faible** : le problème est en amont (chunking, parsing, recherche hybride), changer de modèle n'y fera rien
3. **Si le recall est bon** : mesurer la **faithfulness** en décomposant les réponses en affirmations et en vérifiant chacune contre le contexte
4. **Distinguer** les réponses vraies mais **non soutenues** par le contexte, qui révèlent une connaissance non vérifiée
5. **Décider** avec les chiffres par étage, et prévoir le coût du changement ([[146-choix-modeles|choix de modèle]])

**Piège** : juger un RAG avec un seul score global, qui ne dit jamais quoi corriger.

---

Mise en situation : ton agent de support réussit 80 % des tâches en test, mais les utilisateurs le trouvent peu fiable. Comment expliques-tu l'écart ?
?
1. **Différence entre capacité et fiabilité** : 80 % par essai donne environ 51 % de réussite sur trois essais consécutifs (pass^3)
2. **Mesurer pass^k**, puisque l'utilisateur subit **chaque** tentative, pas la meilleure
3. **Regarder la variance** : mêmes entrées rejouées plusieurs fois, pour repérer les tâches instables
4. **Stabiliser** : outils plus étroits, validations déterministes, étapes vérifiables plutôt que libres
5. **Prévoir l'échec** : escalade vers un humain plutôt qu'une réponse approximative ([[144-ux-ia-human-in-the-loop|UX]])

**Piège** : communiquer un taux de succès moyen comme s'il s'agissait d'une garantie par requête.

---

Mise en situation : tu dois évaluer un agent qui modifie des tickets et envoie des e-mails. Comment construis-tu l'environnement de test ?
?
1. **Bac à sable reproductible** : services simulés, base de test, dépôt figé, aucune action réelle
2. **Vérifier l'état final** : le ticket est-il dans le bon statut, l'e-mail contient-il les bons éléments ?
3. **Ne pas imposer la trajectoire exacte** : plusieurs chemins sont valides. On pose des contraintes (outil interdit, budget d'étapes)
4. **Utilisateur simulé** pour les conversations multi-tours, avec plusieurs exécutions car il ajoute de la variance
5. **Suivre l'efficacité** : étapes, tokens et coût par tâche réussie ([[122-finops-llm|FinOps]])

**Piège** : tester en production « sur de vrais tickets, mais en faisant attention ».

---

## Connexions
- [[94-evals-methodologie|Méthodologie d'évaluation]] — le cadre général
- [[95-llm-as-judge|LLM-as-a-judge]] — les juges de faithfulness et de trajectoire
- [[21-rag-fondamentaux|RAG — Fondamentaux]] et [[22-rag-avance|RAG avancé]] — ce qu'on évalue
- [[31-agents-fondamentaux|Agents]] et [[32-tool-calling|tool calling]] — ce qu'on évalue
- [[134-recherche-vectorielle-ann|Recherche vectorielle]] — rappel de l'index ANN
- [[114-reproductibilite-variance|Reproductibilité & variance]] — pass@k, pass^k
- [[98-debogage-agents|Débogage des agents]] — comprendre pourquoi une tâche échoue
- [[27-agents-recherche-deep-research|Agents de recherche]] — évaluer couverture et citations
- [[00-moc-ai-engineering|MOC AI Engineering]]
