# Évaluation des RAG & des agents — Flashcards
Tags: #flashcards #ai-engineering #evals #rag #agents #llm
<!-- summary: retrieval et génération, recall@k, MRR, nDCG, triade RAG, faithfulness, jeux synthétiques, résultat final ou trajectoire, environnements d'eval (τ-bench, SWE-bench), pass^k, tool calling, multi-tours, efficacité. -->


Comment découper l'évaluation d'un RAG ? <!--anki:486239767d48454b594b-->
?
En deux étages :
1. **Retrieval** : les bons passages sont-ils remontés ? (recall@k, precision@k, MRR, nDCG)
2. **Génération** : la réponse est-elle **fidèle** aux passages et **répond-elle** à la question ?

Un mauvais score global ne dit pas lequel corriger ; les métriques par étage, si.

---

Que mesurent recall@k, MRR et nDCG ? <!--anki:4a7e6f715833634b5574-->
?
- **Recall@k** : part des passages pertinents présents dans les **k premiers** — la métrique clé, car le LLM ne voit que ceux-là.
- **MRR** (Mean Reciprocal Rank) : **1/rang** du premier résultat pertinent, moyenné.
- **nDCG** : qualité du **classement** avec pertinence graduée, pénalisant les bons résultats placés bas.

---

Quelle est la « triade RAG » ? <!--anki:6a653b4e2d6648756538-->
?
1. **Context relevance** : les passages récupérés sont-ils pertinents pour la question ?
2. **Faithfulness / groundedness** : chaque affirmation de la réponse est-elle **soutenue par le contexte** ?
3. **Answer relevance** : la réponse traite-t-elle **la question posée** ?

C'est la base de [[22-rag-avance|RAGAS]] et des évaluateurs équivalents.

---

Comment mesurer la faithfulness ? <!--anki:775151472b433d507b78-->
?
Décomposer la réponse en **affirmations atomiques**, puis faire vérifier par un [[95-llm-as-judge|juge]] (ou un modèle NLI) que chacune est **impliquée par le contexte**. Score = affirmations soutenues / total. Une réponse **vraie mais absente du contexte** compte comme non fidèle : elle révèle une connaissance paramétrique non vérifiée.

---

Comment construire un jeu d'eval de retrieval sans annotation manuelle massive ? <!--anki:492e45662f7739523f5b-->
?
**Génération synthétique** : pour chaque chunk, faire écrire par un LLM des **questions dont ce chunk est la réponse** → paires (question, chunk attendu). À compléter par des **questions réelles** annotées, car les questions synthétiques sont souvent **trop proches du texte** (recouvrement lexical) et surestiment le recall.

---

Qu'évalue-t-on dans un agent ? <!--anki:4c60365159432332473a-->
?
- **Résultat final** : la tâche est-elle accomplie ? (vérifiable par l'**état final** : fichier créé, ticket fermé, tests verts)
- **Trajectoire** : bons outils, bons arguments, pas d'étapes inutiles ni dangereuses.
- **Efficacité** : nombre d'étapes, tokens, coût, durée.
- **Sécurité** : actions interdites évitées, demandes de confirmation respectées.

---

Pourquoi préférer vérifier l'état final plutôt que la trajectoire exacte ? <!--anki:665d214731723872667a-->
?
Parce qu'il existe **plusieurs chemins valides** : imposer une séquence exacte d'appels pénalise des solutions correctes et rend l'eval **fragile**. On vérifie le **résultat** dans un environnement contrôlé, et on n'impose sur la trajectoire que des **contraintes** (outil interdit, étape obligatoire, budget max).

---

Qu'est-ce qu'un environnement d'eval pour agents ? <!--anki:77776f6c5d3a242e7325-->
?
Un **bac à sable reproductible** : faux services (API mockées, base de test, dépôt git figé), **utilisateur simulé** par un LLM pour les conversations multi-tours, et **vérificateur automatique** de l'état final. Exemples publics : **τ-bench** (support client), **SWE-bench** (correction de bugs), **WebArena**, **OSWorld**.

---

Pourquoi pass^k est-il crucial pour un agent en production ? <!--anki:4e5e397b574e687a6f79-->
?
**pass@k** = au moins un succès sur k essais (capacité) ; **pass^k** = **k succès sur k** (fiabilité). Un agent à 70 % de succès par essai n'a que **≈ 34 %** de pass^3. En production, l'utilisateur subit **chaque** essai : c'est pass^k qui compte ([[114-reproductibilite-variance|pass@k et pass^k]]).

---

Comment évaluer l'appel d'outils (tool calling) isolément ? <!--anki:4e634e67316076667936-->
?
Sur des cas unitaires : pour une requête donnée, vérifier **le choix de l'outil**, la **validité des arguments** (schéma, valeurs), les cas où **aucun outil** ne doit être appelé, et les **appels parallèles**. Évaluations **par règles**, rapides et déterministes → idéales en [[112-cicd-modeles|CI]].

---

Comment évaluer une conversation multi-tours ? <!--anki:6c46715556596074525d-->
?
Avec un **simulateur d'utilisateur** (LLM avec un persona et un objectif) qui dialogue avec le système jusqu'à la fin, puis un juge sur **l'objectif atteint**, la **cohérence** entre les tours et la **gestion des changements d'avis**. Il faut rejouer **plusieurs fois** : le simulateur ajoute sa propre variance.

---

Quelles métriques d'efficacité suivre en plus de la qualité ? <!--anki:515e3872755f6a3b5d67-->
?
**Tokens et coût par tâche réussie**, **nombre d'étapes**, **latence de bout en bout**, taux de **boucles** ou d'abandons. Un agent plus précis mais trois fois plus cher n'est pas forcément meilleur : on compare sur un **front qualité / coût** ([[122-finops-llm|FinOps]]).

---

Calcul : un agent réussit 90 % des tâches au premier essai. Quelle probabilité de réussir la même tâche 5 fois sur 5 (pass^5) ? <!--anki:6664613061633837663230343433353462663263393038633136326162303030-->
?
```text
pass^1 = 0,90
pass^5 = 0,90⁵ ≈ 0,59
pass^8 = 0,90⁸ ≈ 0,43
```
Avec des essais indépendants, un agent « à 90 % » ne réussit les cinq essais que **6 fois sur 10**. Pour un usage répété, c'est pass^k qui décrit l'expérience de l'utilisateur, pas pass@1 ([[114-reproductibilite-variance|variance]]).

---

## Mises en situation

Mise en situation : ton RAG affiche 62 % de réponses jugées correctes, et l'équipe veut changer de modèle de génération. Comment vérifies-tu que c'est le bon levier ? <!--anki:4f663b6b4b4a55712b34-->
?
1. **Découper la mesure** : recall@k du retrieval d'un côté, fidélité et pertinence de la génération de l'autre
2. **Si le recall est faible** : le problème est en amont (chunking, parsing, recherche hybride), changer de modèle n'y fera rien
3. **Si le recall est bon** : mesurer la **faithfulness** en décomposant les réponses en affirmations et en vérifiant chacune contre le contexte
4. **Distinguer** les réponses vraies mais **non soutenues** par le contexte, qui révèlent une connaissance non vérifiée
5. **Décider** avec les chiffres par étage, et prévoir le coût du changement ([[146-choix-modeles|choix de modèle]])

**Piège** : juger un RAG avec un seul score global, qui ne dit jamais quoi corriger.

---

Mise en situation : ton agent de support réussit 80 % des tâches en test, mais les utilisateurs le trouvent peu fiable. Comment expliques-tu l'écart ? <!--anki:6339702b49452f682876-->
?
1. **Différence entre capacité et fiabilité** : avec probabilité constante de 80 % et essais indépendants, trois réussites consécutives valent 0,8³ ≈ 51 % ; mesurer par tâche si ces hypothèses ne tiennent pas
2. **Mesurer pass^k**, puisque l'utilisateur subit **chaque** tentative, pas la meilleure
3. **Regarder la variance** : mêmes entrées rejouées plusieurs fois, pour repérer les tâches instables
4. **Stabiliser** : outils plus étroits, validations déterministes, étapes vérifiables plutôt que libres
5. **Prévoir l'échec** : escalade vers un humain plutôt qu'une réponse approximative ([[144-ux-ia-human-in-the-loop|UX]])

**Piège** : communiquer un taux de succès moyen comme s'il s'agissait d'une garantie par requête.

---

Mise en situation : tu dois évaluer un agent qui modifie des tickets et envoie des e-mails. Comment construis-tu l'environnement de test ? <!--anki:425a3d32585b2a4c7d41-->
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
- [[133-embeddings-representations|Embeddings]] — représenter le sens par des vecteurs
- [[143-hallucinations-grounding|Hallucinations & grounding]] — citations, abstention et vérification
- [[25-chunking-contextual-retrieval|Chunking avancé]] — rendre chaque chunk trouvable
- [[26-text-to-sql|Text-to-SQL]] — répondre aux questions chiffrées sur des tables
- [[49-agents-de-code|Agents de code]] — utiliser et intégrer les agents de code
- [[55-rl-agentique|RL agentique]] — entraîner un modèle sur des tâches d'agent
- [[174-recommandation-ranking|Recommandation & learning to rank]] — mesurer rappel et ordre des résultats
- [[00-moc-ai-engineering|MOC AI Engineering]]
