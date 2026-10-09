# LLM-as-a-judge — Flashcards
Tags: #flashcards #ai-engineering #evals #llm-as-judge #llm
<!-- summary: formats pointwise et pairwise, biais (position, verbosité, auto-préférence), prompt de juge, validation contre des humains (TPR, TNR, kappa), correction du taux mesuré, choix du modèle juge, juges spécialisés, limites, quand ne pas utiliser de juge. -->


Qu'est-ce que le LLM-as-a-judge ? <!--anki:68706a2847612b4c514c-->
?
Utiliser un **LLM pour évaluer les sorties** d'un autre système selon une **rubrique** : pertinence, fidélité au contexte, ton, respect d'une consigne. Il rend évaluables à grande échelle des critères **que le code ne sait pas vérifier**.

---

Quels axes distinguent les formats de jugement d’un LLM-as-a-judge ? <!--anki:66302c23656c45342539-->
?
Deux **axes distincts** :
- **Pointwise ou pairwise** : noter une réponse seule, ou comparer deux réponses.
- **Avec ou sans réponse de référence** : fournir ou non un résultat attendu au juge.

On peut donc comparer deux réponses **avec une référence**, ou noter une seule réponse sans elle à partir d'un critère vérifiable. Le pairwise n'est pas intrinsèquement plus fiable pour toute tâche : tester biais de position et accord avec les humains. Choisir le format selon la décision, puis préciser égalités, abstentions et critères.

---

Quels sont les principaux biais d'un juge LLM ? <!--anki:66606e455a70326a5d66-->
?
- **Biais de position** : préférer la réponse présentée en premier (ou en second).
- **Biais de verbosité** : préférer les réponses **longues**.
- **Auto-préférence** : favoriser les sorties de **son propre modèle** ou de sa famille.
- **Complaisance** : noter trop généreusement.
- **Sensibilité au format** (markdown, assurance du ton) plutôt qu'à l'exactitude.

---

Comment neutraliser le biais de position en pairwise ? <!--anki:513e7939646b50442b4a-->
?
**Juger deux fois en inversant l'ordre** (A/B puis B/A) et ne retenir que les verdicts **cohérents** ; un désaccord compte comme **égalité**. On peut aussi randomiser l'ordre sur l'ensemble du jeu.

Cette procédure réduit le biais sans garantir sa disparition. Documenter comment les désaccords sont comptés : les traiter comme égalités peut masquer des cas difficiles, les exclure peut biaiser le score. Rapporter leur fréquence et relire un échantillon permet de distinguer préférence réelle, sensibilité à l'ordre et ambiguïté de la consigne.

---

Comment rédiger un bon prompt de juge ? <!--anki:6939636d73502e7a64-->
?
- **Un critère par juge**, binaire si possible.
- **Définitions précises** de pass et fail, avec **exemples** des deux (few-shot tirés de vrais cas).
- Demander un **raisonnement avant le verdict** (critique puis décision).
- Sortie **structurée** ([[63-guided-generation|JSON]]) pour l'agrégation.
- Fournir le **contexte nécessaire** (documents, consigne originale).

---

Comment valider un juge LLM ? <!--anki:446d7b2f5475595e5641-->
?
Définir d'abord la **classe positive**. Si « réponse correcte » est positive, le **TPR** est la part des vraies réussites acceptées ; le **TNR** est la part des vrais échecs rejetés.

Comparer aux annotations humaines sur un test distinct des exemples de développement du juge, avec matrice de confusion, volumes et incertitude. Si l'on choisit plutôt « échec » comme positif, les appellations changent : documenter cette convention. Vérifier les segments critiques et la qualité des labels humains ; un accord global élevé peut cacher un juge qui accepte tout.

---

Pourquoi l'accord brut (% d'accord) est-il trompeur ? <!--anki:7935482633457b4d3c66-->
?
Avec 90 % de réussites, répondre toujours « pass » donne **90 % d'accord** sans détecter aucun échec. Examiner la matrice de confusion et les erreurs qui comptent pour la décision.

Le **kappa de Cohen** rapporte l'accord observé à un accord attendu calculé à partir des fréquences marginales des annotateurs. Il n'établit ni vérité des labels, ni équivalence au hasard réel, et varie avec la distribution des classes. Publier volumes, accord par classe et procédure de résolution des désaccords ; aucun score seul ne valide un juge.

---

Comment corriger le taux de succès mesuré par un juge imparfait ? <!--anki:4c3c5f2b46467c777b54-->
?
En définissant **positif = succès**, poser `q` = fraction de « pass » du juge et `p` = vrai taux de succès :
```text
q = TPR × p + (1 − TNR) × (1 − p)
p = (q + TNR − 1) / (TPR + TNR − 1)
```
L'inversion suppose des TPR/TNR applicables à la population visée et un dénominateur suffisamment éloigné de zéro. Estimer aussi l'incertitude de ces paramètres. Un résultat hors [0,1] révèle bruit ou hypothèses incompatibles ; le borner artificiellement ne valide pas l'estimation. Une revue humaine peut être préférable à une correction instable.

---

Faut-il utiliser un modèle plus fort que le modèle évalué ? <!--anki:677a4f344a67506e7d57-->
?
Souvent oui pour les critères difficiles, mais ce n'est **pas obligatoire** : vérifier une propriété précise est plus facile que produire la réponse. Un **petit modèle bien prompté et validé** peut suffire et coûte bien moins cher. On évite si possible le **même modèle** que le système évalué (auto-préférence).

---

Qu'est-ce qu'un modèle juge spécialisé ? <!--anki:4344644c2c2b60703e4b-->
?
Un modèle **entraîné pour évaluer** (reward models, juges fine-tunés type Prometheus, classifieurs de sécurité comme [[101-securite-llm-guardrails|Llama Guard]]). Moins cher et plus stable qu'un LLM généraliste sur son critère, mais **moins flexible**.

Leur avantage dépend du critère et du domaine d'entraînement ; il doit être mesuré face à des annotations humaines. Un classifieur de sécurité ne juge pas nécessairement la factualité ou l'utilité. Surveiller les cas hors distribution et recalibrer après un changement de tâche, de langue ou de modèle évalué.

---

Quelles sont les limites du LLM-as-a-judge ? <!--anki:70352b21524a7a6e7031-->
?
- **Variance** : deux passes ne donnent pas le même verdict ([[114-reproductibilite-variance|variance du juge]]).
- **Dérive** quand le fournisseur met à jour le modèle juge → **épingler la version**.
- **Coût** : un appel de juge par critère et par exemple.
- Incapable de vérifier des **faits qu'il ignore** : pour l'exactitude factuelle, il faut une **référence** ou le contexte.

---

Où utiliser le juge en production ? <!--anki:4630707a3f4a6a656f73-->
?
Sur un **échantillon du trafic** pour suivre la qualité sans vérité terrain, pour **trier** les traces à relire par un humain, et comme **[[143-hallucinations-grounding|guardrail]] en ligne** quand la latence le permet. Les scores remontent dans l'outil d'[[91-langfuse-observabilite|observabilité]].

---

Quand ne pas utiliser un LLM-as-a-judge ? <!--anki:6e5a5749643e5a6b5446-->
?
Privilégier du **code déterministe** pour un contrat explicite : syntaxe JSON, champ requis, règle de calcul ou résultat d'un test. C'est souvent plus reproductible et moins coûteux qu'un juge, mais une assertion peut être mal conçue ou couvrir un critère insuffisant.

Un juge sans source fiable ne résout pas la vérification factuelle. Dans un domaine expert, valider ses verdicts contre des annotations spécialisées. Pour une décision individuelle à fort enjeu, prévoir contrôles et recours : un bon score agrégé ne rend pas chaque jugement sûr. Voir la [[94-evals-methodologie|méthodologie]].

---

Calcul : 1 000 jugements/jour utilisent chacun 1 500 tokens d’entrée et 200 de sortie à 3 €/M et 15 €/M. Quel coût sur 30 jours, puis pour trois critères jugés séparément ? <!--anki:3066323261623265663933613439313038393739636164303336303936303732-->
?
Hypothèses : 1 500 tokens d'entrée par jugement (rubrique, question, contexte, réponse), 200 de sortie, 3 €/M en entrée, 15 €/M en sortie.
```text
par jugement : 1 500 × 3 €/M + 200 × 15 €/M = 0,0075 €
par jour     : 1 000 × 0,0075 €             = 7,50 € → ≈ 225 € par mois
3 critères jugés séparément                 ≈ 675 € par mois
```
Abordable sur un **échantillon**, cher si l'on juge 100 % d'un trafic important. Leviers : échantillonner, un juge plus petit **validé contre des annotations humaines**, et des assertions de code pour ce qui est vérifiable.

---

## Mises en situation

Mise en situation : ton juge LLM annonce 95 % d'accord avec les annotations humaines, et l'équipe veut s'en servir comme gate de déploiement. Qu'en penses-tu ? <!--anki:736e5358393f78245772-->
?
1. **Fixer les labels** : positif = réponse correcte ; TPR accepte les réussites, TNR rejette les échecs.
2. **Comparer à une baseline** : si presque tout est correct, un juge toujours positif affiche un fort accord.
3. **Mesurer par classe et segment**, avec volumes et incertitude, sur un test humain indépendant.
4. **Évaluer l'usage prévu** : une gate doit détecter les erreurs critiques ; corriger un taux agrégé ne sécurise pas chaque verdict.
5. **Versionner et surveiller** le juge, sa rubrique et ses données de validation.

**Piège** : appliquer une formule de correction avec « succès » et « échec » inversés.

---

Mise en situation : tu dois comparer deux versions de ton assistant sur 300 cas, avec un juge automatique. Comment organises-tu l'évaluation ? <!--anki:77484f354e39534d592d-->
?
1. **Définir le critère** et les cas qui constituent un progrès ou une régression.
2. **Comparer en pairwise si adapté**, en inversant ou randomisant l'ordre.
3. **Fixer les règles d'agrégation** : égalités, désaccords entre ordres et abstentions ; publier leur fréquence.
4. **Vérifier la rubrique** sur des annotations humaines, avec justificatifs courts et contrôlables.
5. **Contrôler les biais** de style, longueur et famille de modèle, puis quantifier l'incertitude.

**Piège** : assimiler une préférence du juge à une amélioration métier démontrée, ou transformer tous les désaccords en certitudes.

---

## Sources

- [Zheng et al. — évaluer les juges LLM](https://arxiv.org/abs/2306.05685)
- [scikit-learn — matrice de confusion et kappa](https://scikit-learn.org/stable/modules/model_evaluation.html)

## Connexions
- [[94-evals-methodologie|Méthodologie d'évaluation]] — où le juge s'insère
- [[96-evals-rag-agents|Evals de RAG & d'agents]] — juges de fidélité et de trajectoire
- [[114-reproductibilite-variance|Reproductibilité & variance]] — variance du juge
- [[91-langfuse-observabilite|Langfuse]] — scores LLM-as-judge en production
- [[52-post-training-alignement|Post-training]] — reward models et RLAIF
- [[12-optimisation-automatique-prompts|Optimisation automatique de prompts]] — laisser une métrique choisir la formulation
- [[151-donnees-curation-annotation|Curation & annotation]] — données de qualité et jeux séparés
- [[48-patterns-workflows-agentiques|Patterns de workflows]] — chaining, routing, evaluator-optimizer
- [[92-chainforge-evals-prompts|ChainForge & evals]] — comparer prompts et modèles
- [[115-plateformes-agents-gouvernance|Plateformes d'agents — gouvernance]] — identité, politiques, audit et coûts d'une flotte d'agents
- [[38-plateformes-agents|Plateformes d'agents]] — runtime, sandbox, gateway d'outils et identité
- [[68-quantization|Quantization]] — réduire la précision pour gagner mémoire et vitesse
- [[93-monitoring-inference|Monitoring de l'inférence]] — métriques, validations et signaux de production
- [[00-moc-ai-engineering|MOC AI Engineering]]
