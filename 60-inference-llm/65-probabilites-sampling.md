# Probabilités & sampling — Flashcards
Tags: #flashcards #ai-engineering #inference #sampling #probabilites #llm

Que produit un LLM à chaque pas de génération ?
?
Un **vecteur de logits** (un score par token du vocabulaire), transformé en **distribution de probabilité** par un **softmax**. Le token suivant est **choisi** dans cette distribution, ajouté au contexte, et on recommence : c'est la génération **autorégressive**.
```text
contexte → logits → softmax → P(token) → choix → contexte + token → …
```

---

Pourquoi deux appels identiques donnent-ils des réponses différentes ?
?
Parce que le token est **échantillonné** (tiré au sort selon sa probabilité) et pas simplement pris comme le plus probable. Un écart sur un seul token change tout le contexte suivant : les différences **s'amplifient** au fil de la génération.

---

Quel est le rôle de la température ?
?
Elle **divise les logits avant le softmax** :
```text
P(i) = exp(zᵢ / T) / Σⱼ exp(zⱼ / T)
```
- **T < 1** : distribution plus **piquée**, sorties plus sûres et plus répétitives
- **T = 1** : la distribution apprise par le modèle
- **T > 1** : distribution plus **plate**, plus de diversité… et plus d'erreurs
- **T → 0** : on prend toujours le token le plus probable (**greedy**)

---

Qu'est-ce que le décodage greedy ?
?
Prendre **à chaque pas le token le plus probable** (température 0). Simple et stable, mais il peut **tourner en boucle** (répétitions) et ne donne **pas** forcément la séquence la plus probable dans son ensemble.

---

Qu'est-ce que le top-k ?
?
Ne garder que les **k tokens les plus probables**, **renormaliser** leurs probabilités, puis échantillonner. Limite : k est **fixe**, que le modèle soit sûr de lui (un seul bon candidat) ou qu'il hésite (des dizaines).

---

Qu'est-ce que le top-p (nucleus sampling) ?
?
Garder le **plus petit ensemble de tokens dont la probabilité cumulée atteint p** (ex. 0,9), renormaliser, échantillonner. L'ensemble **s'adapte** : étroit quand le modèle est sûr, large quand il hésite.

---

Qu'est-ce que le min-p ?
?
Garder les tokens dont la probabilité vaut au moins **min_p × celle du meilleur token** (ex. 0,05 × p_max). Le seuil suit la **confiance** du modèle, ce qui résiste mieux aux hautes températures que le top-p. Disponible dans vLLM, llama.cpp et Hugging Face transformers.

---

Quels réglages de sampling selon le cas d'usage ?
?
- **Extraction, classification, code, [[32-tool-calling|tool calling]]** : température **basse** (0 à 0,3)
- **Rédaction, brainstorming** : température **modérée** (0,7 à 1), top-p ≈ 0,9
- Recommandation courante : régler **la température ou le top-p, pas les deux**. Certains modèles de raisonnement ignorent ou fixent ces paramètres.

---

Que sont les logprobs et à quoi servent-ils ?
?
Les **log-probabilités** des tokens générés, souvent avec celles des meilleurs candidats alternatifs, renvoyées par certaines API et par les serveurs comme vLLM. Usages :
- **Score de confiance** d'une classification (probabilité de « oui » contre « non »)
- **Repérer l'incertitude** : des tokens clés peu probables signalent un risque d'hallucination
- Calculer la **perplexité**

---

Comment calcule-t-on la probabilité d'une séquence ?
?
C'est le **produit** des probabilités de chaque token sachant les précédents, donc la **somme des logprobs**. Elle baisse mécaniquement avec la longueur : pour comparer des séquences de longueurs différentes, on **normalise par le nombre de tokens**.

---

Qu'est-ce que la perplexité ?
?
```text
perplexité = exp( moyenne des −logprobs par token )
```
L'exponentielle de la **cross-entropy**, la loss minimisée à l'entraînement : elle mesure à quel point le modèle est « surpris » par un texte (≈ nombre de choix équiprobables entre lesquels il hésite à chaque token). Utile pour comparer des modèles de langage ou repérer du texte hors distribution, **pas** pour juger la qualité d'une réponse.

---

Les probabilités d'un LLM sont-elles fiables (calibration) ?
?
Un modèle **calibré** a raison environ 80 % du temps quand il annonce 80 %. Les modèles **de base** sont plutôt bien calibrés au niveau des tokens, mais le **post-training (RLHF)** dégrade souvent cette calibration, et la confiance **verbalisée** (« je suis sûr à 90 % ») est peu fiable. On mesure donc l'exactitude réelle sur un [[92-chainforge-evals-prompts|jeu d'évaluation]].

---

Le speculative decoding modifie-t-il la distribution des sorties ?
?
**Non.** L'étape de vérification par le grand modèle (acceptation ou rejet probabiliste de chaque token proposé) garantit **exactement la même distribution** que le grand modèle seul, et la même sortie en greedy. Seule la vitesse change ([[62-optimisations-inference|optimisations d'inférence]]).

---

## Connexions
- [[61-kv-cache-attention|KV cache & attention]] — la génération token par token
- [[62-optimisations-inference|Optimisations d'inférence]] — speculative decoding
- [[63-guided-generation|Guided generation]] — masquer des logits avant l'échantillonnage
- [[11-prompt-engineering-avance|Prompt engineering]] — self-consistency : plusieurs échantillons, vote majoritaire
- [[114-reproductibilite-variance|Reproductibilité & variance]] — pourquoi les sorties varient même à température 0
- [[92-chainforge-evals-prompts|Evals]] — mesurer l'effet des réglages
- [[67-speculative-decoding|Speculative decoding]] — la règle d'acceptation qui préserve la distribution
- [[00-moc-ai-engineering|MOC AI Engineering]]
