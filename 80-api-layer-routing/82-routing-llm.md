# Routing LLM — Flashcards
Tags: #flashcards #ai-engineering #routing #api-layer #llm

Pourquoi router les requêtes entre plusieurs modèles ?
?
Parce qu'**aucun modèle n'est optimal partout** : la majorité des requêtes sont simples et peuvent aller vers un **modèle petit, rapide et bon marché**, en réservant le **modèle puissant** aux cas difficiles. On optimise le triangle **coût / qualité / latence**.

---

Qu'est-ce que le routage statique ?
?
Un **modèle fixé par cas d'usage** (classification → petit modèle, rédaction juridique → gros modèle). Simple et prévisible, c'est le **point de départ** recommandé.

---

Qu'est-ce que le routage par règles ?
?
Des **heuristiques** sur la requête : longueur du prompt, langue, présence de code, client ou tenant, niveau d'abonnement. Déterministe et facile à auditer.

---

Qu'est-ce que le routage sémantique ?
?
On compare l'**embedding de la requête** à des exemples de référence pour chaque route (ex. « support », « code », « hors sujet ») et on choisit la route la plus proche. Rapide et sans appel LLM.

---

Qu'est-ce qu'un routeur appris (ex. RouteLLM) ?
?
Un **classifieur entraîné sur des données de préférence** qui prédit si le modèle faible suffira pour une requête donnée. Un **seuil** règle le compromis coût/qualité.

---

Qu'est-ce qu'une cascade ?
?
Envoyer d'abord la requête au **modèle bon marché**, **vérifier** la réponse (validation de format, score de confiance, juge) et **escalader** vers un modèle plus puissant seulement en cas d'échec.

---

Quelle différence entre routing et fallback ?
?
Le **routing** choisit le modèle **avant** l'appel (optimisation) ; le **fallback** bascule vers un autre modèle **après une erreur** (panne, rate limit, timeout) — c'est de la **fiabilité**, gérée par l'[[81-litellm-api-layer|API layer]].

---

Qu'est-ce que le routage selon la charge ?
?
Répartir entre **réplicas d'un même modèle** selon leur état : file d'attente, latence, occupation du [[61-kv-cache-attention|KV cache]], voire **affinité de préfixe** (envoyer la requête là où son préfixe est déjà en cache).

---

Sur quoi fonder une décision de routage ?
?
Sur des **[[92-chainforge-evals-prompts|evals]] par segment de requêtes** (qualité de chaque modèle par type de tâche) et sur les **données de production** ([[91-langfuse-observabilite|Langfuse]] : coût, latence, feedback). Sans mesure, le routeur économise en dégradant la qualité sans le savoir.

---

Qu'est-ce qu'un cache sémantique ?
?
Renvoyer une **réponse déjà générée** pour une question **sémantiquement proche** d'une question passée. Gros gain de coût et de latence, mais risque de **mauvaise réponse** si le seuil de similarité est trop permissif.

---

## Connexions
- [[81-litellm-api-layer|LiteLLM]] — où le routage est implémenté
- [[91-langfuse-observabilite|Langfuse]] — décider grâce aux données observées
- [[92-chainforge-evals-prompts|Evals]] — mesurer la qualité par modèle
- [[64-metriques-slo-inference|Métriques & SLO]] — la contrainte de latence
- [[121-couts-inference|Coûts d'inférence]] — le levier de coût n°1
- [[00-moc-ai-engineering|MOC AI Engineering]]
