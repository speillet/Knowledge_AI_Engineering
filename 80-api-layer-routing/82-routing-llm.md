# Routing LLM — Flashcards
Tags: #flashcards #ai-engineering #routing #api-layer #llm
<!-- summary: routage statique, par règles ou sémantique, RouteLLM, cascade, routage selon la charge, cache sémantique. -->

Pourquoi router les requêtes entre plusieurs modèles ?
?
<!--anki:6a5b33407a5a3140415e-->
Parce qu'**aucun modèle n'est optimal partout** : la majorité des requêtes sont simples et peuvent aller vers un **modèle petit, rapide et bon marché**, en réservant le **modèle puissant** aux cas difficiles. On optimise le triangle **coût / qualité / latence**.

---

Qu'est-ce que le routage statique ?
?
<!--anki:44773775513569557677-->
Un **modèle fixé par cas d'usage** (classification → petit modèle, rédaction juridique → gros modèle). Simple et prévisible, c'est le **point de départ** recommandé.

---

Qu'est-ce que le routage par règles ?
?
<!--anki:5162254473514a51595d-->
Des **heuristiques** sur la requête : longueur du prompt, langue, présence de code, client ou tenant, niveau d'abonnement. Déterministe et facile à auditer.

---

Qu'est-ce que le routage sémantique ?
?
<!--anki:416e31782d254b435577-->
On compare l'**embedding de la requête** à des exemples de référence pour chaque route (ex. « support », « code », « hors sujet ») et on choisit la route la plus proche. Rapide et sans appel LLM.

---

Qu'est-ce qu'un routeur appris (ex. RouteLLM) ?
?
<!--anki:733a60734a2a716f745b-->
Un **classifieur entraîné sur des données de préférence** qui prédit si le modèle faible suffira pour une requête donnée. Un **seuil** règle le compromis coût/qualité.

---

Qu'est-ce qu'une cascade de modèles ?
?
<!--anki:704a444b343c593f2c61-->
Envoyer d'abord la requête au **modèle bon marché**, **vérifier** la réponse (validation de format, score de confiance, juge) et **escalader** vers un modèle plus puissant seulement en cas d'échec.
```text
80 % des requêtes : petit modèle           → 1 × le coût
20 % escaladées   : petit + grand modèle   → 1 × + 12 × = 13 ×

coût moyen ≈ 0,8 × 1 + 0,2 × 13 ≈ 3,4   contre 12 en tout-grand-modèle
```
Le calcul ne tient que si la **vérification est fiable et bon marché** : sinon on paie deux fois pour un résultat incertain.

---

À ne pas confondre : routing et fallback ?
?
<!--anki:66313d487a55554a5a34-->
Le **routing** choisit le modèle **avant** l'appel (optimisation) ; le **fallback** bascule vers un autre modèle **après une erreur** (panne, rate limit, timeout) — c'est de la **fiabilité**, gérée par l'[[81-litellm-api-layer|API layer]].

---

Qu'est-ce que le routage selon la charge ?
?
<!--anki:47573371746971216e2e-->
Répartir entre **réplicas d'un même modèle** selon leur état : file d'attente, latence, occupation du [[61-kv-cache-attention|KV cache]], voire **affinité de préfixe** (envoyer la requête là où son préfixe est déjà en cache).

---

Sur quoi fonder une décision de routage ?
?
<!--anki:673d62522f6f49603563-->
Sur des **[[92-chainforge-evals-prompts|evals]] par segment de requêtes** (qualité de chaque modèle par type de tâche) et sur les **données de production** ([[91-langfuse-observabilite|Langfuse]] : coût, latence, feedback). Sans mesure, le routeur économise en dégradant la qualité sans le savoir.

---

Qu'est-ce qu'un cache sémantique ?
?
<!--anki:702925434b335a303e56-->
Renvoyer une **réponse déjà générée** pour une question **sémantiquement proche** d'une question passée. Gros gain de coût et de latence, mais risque de **mauvaise réponse** si le seuil de similarité est trop permissif.

---

À ne pas confondre : les quatre décisions autour du modèle ?
?
<!--anki:7265624f26605e34686c-->
```text
Routage   → AVANT l'appel, choisir le bon modèle          (optimisation)
Cascade   → APRÈS un échec de qualité, escalader          (optimisation)
Fallback  → APRÈS une erreur technique, basculer          (fiabilité)
Retry     → APRÈS une erreur transitoire, réessayer       (fiabilité)
```
Les deux premiers visent le **coût et la qualité**, les deux derniers la **disponibilité**. Ils vivent souvent dans le même composant, la [[81-litellm-api-layer|gateway]], mais répondent à des questions différentes ([[142-fiabilite-resilience-llm|fiabilité]]).

---

## Mises en situation

Mise en situation : ta direction demande de diviser par deux le coût de l'assistant, sans dégrader la qualité perçue. Comment procèdes-tu ?
?
<!--anki:702a4c60414f3b6c6136-->
1. **Segmenter le trafic** : quelles requêtes sont simples, lesquelles sont difficiles, dans quelles proportions
2. **Mesurer par segment** : qualité du petit modèle contre le gros, sur chaque segment ([[94-evals-methodologie|evals]])
3. **Commencer par du routage statique ou par règles**, prévisible et auditable, avant tout routeur appris
4. **Cascade** sur les segments incertains : petit modèle, vérification, escalade si échec
5. **Vérifier ensuite** : coût par requête, qualité par segment, taux d'escalade, feedback utilisateur

**Piège** : router sur la seule longueur du prompt, qui ne dit rien de la difficulté réelle.

---

Mise en situation : un collègue propose un cache sémantique pour les questions « proches » des précédentes, sur un assistant bancaire. Quelles réserves poses-tu ?
?
<!--anki:457145645a3a603e465f-->
1. **Le risque principal** : deux questions proches en apparence peuvent appeler des réponses opposées (« puis-je clôturer mon compte ? » selon le type de compte)
2. **Le seuil de similarité** devient un paramètre critique, à calibrer sur des cas réels
3. **Cloisonner** : jamais de cache partagé entre utilisateurs quand la réponse dépend de leurs données
4. **Limiter le périmètre** : réserver le cache aux questions **génériques**, factuelles et sans personnalisation
5. **Mesurer** : taux de hit, mais surtout taux de réponses inadaptées servies depuis le cache ([[123-caching-agressif|caching]])

**Piège** : mesurer le succès du cache à son taux de hit, sans contrôler la justesse des réponses servies.

---

## Connexions
- [[81-litellm-api-layer|LiteLLM]] — où le routage est implémenté
- [[91-langfuse-observabilite|Langfuse]] — décider grâce aux données observées
- [[92-chainforge-evals-prompts|Evals]] — mesurer la qualité par modèle
- [[64-metriques-slo-inference|Métriques & SLO]] — la contrainte de latence
- [[121-couts-inference|Coûts d'inférence]] — le levier de coût n°1
- [[66-prefix-caching-radix-attention|Prefix caching & RadixAttention]] — routage par affinité de préfixe
- [[123-caching-agressif|Caching agressif]] — tous les niveaux de cache
- [[146-choix-modeles|Choix de modèle]] — critères et benchmarks
- [[138-modeles-raisonnement|Modèles de raisonnement]] — router par difficulté
- [[122-finops-llm|FinOps LLM]] — attribuer et piloter les dépenses IA
- [[141-system-design-llm|System design LLM]] — la méthode de conception
- [[48-patterns-workflows-agentiques|Patterns de workflows]] — chaining, routing, evaluator-optimizer
- [[53-donnees-synthetiques-distillation|Données synthétiques & distillation]] — générer des données et transférer vers un petit modèle
- [[00-moc-ai-engineering|MOC AI Engineering]]
