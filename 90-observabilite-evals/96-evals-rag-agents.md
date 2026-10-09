# Évaluation des RAG & des agents — Flashcards
Tags: #flashcards #ai-engineering #evals #rag #agents #llm
<!-- summary: retrieval et génération, calculs precision/recall@k et MRR, nDCG, fidélité ou exactitude, contexte oracle, jeux synthétiques, résultat ou trajectoire, environnements d’eval, pass^k et efficacité. -->


Comment découper l'évaluation d'un RAG ? <!--anki:486239767d48454b594b-->
?
En deux étages :
1. **Retrieval** : les bons passages sont-ils remontés ? (recall@k, precision@k, MRR, nDCG)
2. **Génération** : la réponse est-elle **fidèle** aux passages et **répond-elle** à la question ?

Un mauvais score global ne dit pas lequel corriger ; les métriques par étage, si.

---

Que mesurent recall@k, MRR et nDCG ? <!--anki:4a7e6f715833634b5574-->
?
Le **recall@k** mesure la fraction des éléments pertinents annotés présents dans les k premiers ; la **MRR** moyenne l'inverse du rang du premier pertinent, avec zéro si aucun n'est retrouvé dans le périmètre retenu. Le **nDCG** évalue l'ordre, avec pertinence éventuellement graduée et normalisation par un classement idéal.

Préciser unité — document, passage ou preuve —, cutoff et traitement des requêtes sans pertinent. Une référence incomplète peut pénaliser un autre passage valable. Ces mesures décrivent des aspects différents : retrouver une preuve unique ne suffit pas toujours à répondre à une question qui en demande plusieurs.

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
Décomposer la réponse en affirmations vérifiables, puis évaluer si **les sources fournies les soutiennent**. Un score possible est la fraction d'affirmations soutenues, avec règles explicites pour contradictions, déductions et réponses vides.

Valider le juge ou les annotateurs. Une affirmation vraie mais non étayée peut être jugée non fidèle ; cela ne prouve pas qu'elle vient de la mémoire du modèle. À l'inverse, répéter fidèlement une source erronée ne rend pas l'affirmation vraie. La fidélité, l'exactitude et la réponse à la question sont des critères complémentaires.

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

Qu’apporte pass^k à l’évaluation de la fiabilité d’un agent ? <!--anki:4e5e397b574e687a6f79-->
?
**pass@k** mesure la présence d'au moins une réussite parmi k essais ; **pass^k** mesure la réussite de tous les essais, selon le protocole de répétition. À probabilité constante de 0,7 et avec essais indépendants, pass^3 vaut `0,7³ = 34,3 %`.

Ces métriques répondent à des questions différentes. Un service en un appel doit aussi publier succès au premier essai, gravité des échecs et abstention. Le taux moyen sur des tâches de difficulté variable ne s'élève pas simplement à la puissance k. Mesurer par tâche et agréger selon l'usage.

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

Calcul : sur une tâche donnée, chaque essai indépendant réussit avec probabilité constante 0,9. Quel est pass^5 ? <!--anki:6664613061633837663230343433353462663263393038633136326162303030-->
?
Avec une **probabilité constante de 0,9 pour cette tâche** et des essais indépendants :
```text
P(5 réussites sur 5) = 0,9^5 = 0,59049 ≈ 59 %
P(8 réussites sur 8) = 0,9^8 ≈ 43 %
```
C'est une probabilité de réussite répétée, pas celle d'obtenir au moins une bonne réponse. Si les essais sont dépendants ou les probabilités diffèrent selon les tâches, ces puissances ne décrivent plus directement le résultat observé. Un taux global de 90 % ne suffit donc pas à appliquer la formule à chaque tâche.

---

Calcul : parmi quatre passages pertinents annotés pour une requête, deux figurent dans les trois résultats récupérés, tous distincts et jugés. Quels sont precision@3 et recall@3 ? <!--anki:3432393763326533356630363437366162653636643639393132396662633331-->
?
Les dénominateurs répondent à deux questions différentes :
```text
precision@3 = pertinents récupérés / récupérés = 2/3 ≈ 66,7 %
recall@3 = pertinents récupérés / pertinents annotés = 2/4 = 50 %
```
La précision mesure la proportion utile dans la sélection ; le rappel, la couverture de la référence. Il manque encore deux passages pertinents, même si la majorité des résultats est utile. Ces scores supposent des jugements fiables à la même unité — ici le passage — et ne prouvent pas que le générateur a exploité les preuves.

---

Calcul : pour trois requêtes, le premier passage pertinent apparaît aux rangs 1, 4, puis reste absent des cinq résultats évalués. Quelle est la MRR@5 ? <!--anki:6139653836306237353537633463613761323238653363363962613130336263-->
?
Chaque requête contribue l'inverse du rang du premier pertinent, ou zéro s'il est absent du top 5 :
```text
MRR@5 = (1/1 + 1/4 + 0) / 3 = 5/12 ≈ 0,417
```
Le dénominateur inclut les **trois requêtes**, y compris l'échec. Diviser seulement par les deux requêtes réussies gonflerait le score. La MRR récompense l'arrivée rapide d'un premier résultat utile ; elle ignore les autres preuves pertinentes. Pour une question qui exige plusieurs documents, compléter notamment par une mesure de couverture.

---

À ne pas confondre : fidélité aux sources et exactitude factuelle d’une réponse RAG ? <!--anki:3438653833316233663937323464373461653464616261383963323063313461-->
?
La **fidélité** vérifie que les sources fournies soutiennent la réponse ; l'**exactitude** vérifie que son contenu est correct selon une référence fiable adaptée à la question.

Exemple fictif : un ancien inventaire indique dix unités, mais le stock courant vaut zéro. Pour une question sur le stock actuel, répondre « dix » peut être fidèle au document et faux. Répondre « zéro » peut être exact sans être soutenu par ce document. Examiner fraîcheur et périmètre des sources, puis évaluer les deux dimensions ; une citation présente ne suffit pas.

---

Comment un contexte oracle aide-t-il à diagnostiquer un échec RAG ? <!--anki:6536643366363832613033393464306539373163383664653464353565323064-->
?
Remplacer les passages récupérés par un **contexte vérifié contenant les preuves nécessaires**, tout en gardant question, générateur et consigne comparables.

Si la réponse s'améliore, la récupération ou la préparation du contexte constitue un levier probable. Si elle échoue encore, examiner compréhension, consigne, conflit entre sources et critère d'évaluation. Contrôler longueur, ordre et bruit : un contexte oracle très court change plusieurs facteurs. Utiliser des cas de diagnostic séparés du test final ; cette intervention localise un problème, elle ne prouve pas qu'un meilleur retriever suffira en production.

---

## Mises en situation

Mise en situation : ton RAG affiche 62 % de réponses jugées correctes, et l'équipe veut changer de modèle de génération. Comment vérifies-tu que c'est le bon levier ? <!--anki:4f663b6b4b4a55712b34-->
?
1. **Séparer les étages** : rappel des passages, fidélité et exactitude de la réponse.
2. **Examiner les échecs de retrieval** : preuve absente, mal parsée, mal classée ou filtrée.
3. **Tester un contexte oracle** contenant les bonnes preuves, avec le même générateur et un budget comparable.
4. **Vérifier les affirmations** : soutien par les sources et vérité sont deux critères distincts.
5. **Choisir le levier mesuré**, puis comparer qualité, coût et latence ([[146-choix-modeles|choix de modèle]]).

**Piège** : déduire la cause d'un mauvais score global sans isoler retrieval et génération.

---

Mise en situation : ton agent de support réussit 80 % des tâches en test, mais les utilisateurs le trouvent peu fiable. Comment expliques-tu l'écart ? <!--anki:6339702b49452f682876-->
?
1. **Différence entre capacité et fiabilité** : avec probabilité constante de 80 % et essais indépendants, trois réussites consécutives valent 0,8³ ≈ 51 % ; mesurer par tâche si ces hypothèses ne tiennent pas
2. **Compléter le succès au premier essai** par pass^k, gravité des échecs et résultats par segment
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

## Sources

- [Es et al. — dimensions de l’évaluation RAG](https://arxiv.org/abs/2309.15217)
- [Yao et al. — τ-bench et fiabilité répétée](https://arxiv.org/abs/2406.12045)
- [Stanford — évaluation en recherche d’information](https://nlp.stanford.edu/IR-book/html/htmledition/evaluation-of-ranked-retrieval-results-1.html)

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
