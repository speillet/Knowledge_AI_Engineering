# LLM-as-a-judge — Flashcards
Tags: #flashcards #ai-engineering #evals #llm-as-judge #llm
<!-- summary: formats pointwise et pairwise, biais (position, verbosité, auto-préférence), prompt de juge, validation contre des humains (TPR, TNR, kappa), correction du taux mesuré, choix du modèle juge, juges spécialisés, limites, quand ne pas utiliser de juge. -->


Qu'est-ce que le LLM-as-a-judge ? <!--anki:68706a2847612b4c514c-->
?
Utiliser un **LLM pour évaluer les sorties** d'un autre système selon une **rubrique** : pertinence, fidélité au contexte, ton, respect d'une consigne. Il rend évaluables à grande échelle des critères **que le code ne sait pas vérifier**.

---

Quels sont les trois formats de jugement ? <!--anki:66302c23656c45342539-->
?
1. **Pointwise** : noter une réponse seule (pass/fail ou échelle).
2. **Pairwise** : choisir la meilleure de **deux réponses** — plus fiable pour comparer deux versions.
3. **Avec référence** : comparer la réponse à une **réponse attendue**.

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
En le **comparant à des labels humains** sur un échantillon (quelques centaines de cas) :
- mesurer **TPR et TNR** (le juge détecte-t-il les vrais échecs ? laisse-t-il passer les vrais succès ?) plutôt qu'un simple accord global ;
- découper en **jeu de développement** (itérer le prompt du juge) et **jeu de test** (mesure finale) pour ne pas sur-ajuster.

---

Pourquoi l'accord brut (% d'accord) est-il trompeur ? <!--anki:7935482633457b4d3c66-->
?
Sur un jeu **déséquilibré** (90 % de succès), un juge qui dit toujours « pass » a **90 % d'accord** sans rien détecter. On regarde le **rappel sur les échecs**, la **précision**, ou le **kappa de Cohen**, qui corrige l'accord dû au hasard.

---

Comment corriger le taux de succès mesuré par un juge imparfait ? <!--anki:4c3c5f2b46467c777b54-->
?
Avec le TPR et le TNR du juge : taux réel ≈ **(taux observé + TNR − 1) / (TPR + TNR − 1)**. On peut aussi donner un **intervalle de confiance** par bootstrap sur les labels humains. Sans cette correction, un juge biaisé **fausse la décision**.

---

Faut-il utiliser un modèle plus fort que le modèle évalué ? <!--anki:677a4f344a67506e7d57-->
?
Souvent oui pour les critères difficiles, mais ce n'est **pas obligatoire** : vérifier une propriété précise est plus facile que produire la réponse. Un **petit modèle bien prompté et validé** peut suffire et coûte bien moins cher. On évite si possible le **même modèle** que le système évalué (auto-préférence).

---

Qu'est-ce qu'un modèle juge spécialisé ? <!--anki:4344644c2c2b60703e4b-->
?
Un modèle **entraîné pour évaluer** (reward models, juges fine-tunés type Prometheus, classifieurs de sécurité comme [[101-securite-llm-guardrails|Llama Guard]]). Moins cher et plus stable qu'un LLM généraliste sur son critère, mais **moins flexible**.

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
- **Critère vérifiable par du code** : JSON valide, champ attendu, tests unitaires qui passent, regex, correspondance exacte. Une **assertion déterministe** est gratuite, instantanée et sans variance
- **Exactitude factuelle sans référence** : le juge ne vérifie pas ce qu'il ignore
- **Domaine expert** (médical, juridique) tant que le juge n'est pas **calibré sur des annotations d'experts**
- **Décision unitaire à fort enjeu** (bloquer un utilisateur, valider un paiement) : le juge sert à mesurer des taux, pas à trancher seul un cas

Règle : **code d'abord**, juge pour ce que le code ne sait pas mesurer ([[94-evals-methodologie|méthodologie]]).

---

Calcul : combien coûte un LLM-as-a-judge qui note 1 000 réponses par jour ? <!--anki:3066323261623265663933613439313038393739636164303336303936303732-->
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
1. **Se méfier de l'accord brut** : si 90 % des cas sont des succès, un juge qui dit toujours « pass » atteint 90 % sans rien détecter
2. **Mesurer ce qui compte** : rappel sur les **échecs** (TPR), spécificité (TNR), ou kappa
3. **Séparer les jeux** : un pour itérer sur le prompt du juge, un autre pour la mesure finale
4. **Corriger le taux observé** à partir du TPR et du TNR, pour estimer le taux réel
5. **Épingler la version** du modèle juge, sinon une mise à jour fera bouger tous tes scores

**Piège** : faire du juge une gate sans jamais avoir mesuré sa capacité à détecter les vrais échecs.

---

Mise en situation : tu dois comparer deux versions de ton assistant sur 300 cas, avec un juge automatique. Comment organises-tu l'évaluation ? <!--anki:77484f354e39534d592d-->
?
1. **Format pairwise** : demander au juge de choisir la meilleure des deux réponses, plus fiable qu'une note absolue
2. **Neutraliser la position** : juger dans les deux ordres et ne garder que les verdicts cohérents, les désaccords comptant comme égalité
3. **Un critère à la fois**, binaire, avec définitions précises et exemples
4. **Raisonnement avant verdict**, et sortie structurée pour agréger ([[63-guided-generation|guided generation]])
5. **Contrôler la verbosité** : vérifier que le juge ne préfère pas simplement la réponse la plus longue

**Piège** : utiliser comme juge le modèle qui a produit l'une des deux réponses.

---

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
