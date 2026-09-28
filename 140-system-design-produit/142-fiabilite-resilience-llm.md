# Fiabilité & résilience des applications LLM — Flashcards
Tags: #flashcards #ai-engineering #system-design #fiabilite #production #llm

Pourquoi une application LLM est-elle plus fragile qu'une application classique ?
?
Elle dépend d'un service **externe, lent, coûteux et non déterministe** : latences de plusieurs secondes à plusieurs minutes, **rate limits**, pannes du fournisseur, **sorties mal formées**, et changements de comportement lors des **mises à jour du modèle**. La résilience doit être **conçue**, pas ajoutée après coup.

---

Quels timeouts configurer ?
?
- **Timeout de connexion** court.
- **Timeout jusqu'au premier token** (TTFT) : détecte un modèle saturé.
- **Timeout entre tokens** en streaming : détecte un flux bloqué.
- **Timeout global** adapté à la tâche (un agent ≠ une autocomplétion).

Un seul timeout global de 60 s laisse l'utilisateur attendre **sans rien voir**.

---

Comment faire des retries correctement ?
?
- Seulement sur les erreurs **transitoires** (429, 5xx, timeouts), **jamais** sur les 400 (requête invalide).
- **Backoff exponentiel avec jitter**, en respectant l'en-tête **Retry-After**.
- **Nombre limité** de tentatives et **budget de retries** global pour ne pas amplifier une panne.
- Attention aux actions **non idempotentes** d'un agent (paiement, e-mail) : pas de retry aveugle.

---

Qu'est-ce qu'une chaîne de fallbacks ?
?
En cas d'échec du modèle principal : **même modèle chez un autre fournisseur/région** → **autre modèle** comparable → **modèle plus petit** → **réponse dégradée** (message d'attente, FAQ, humain). Chaque fallback doit être **évalué** : un prompt optimisé pour un modèle peut mal marcher sur un autre ([[81-litellm-api-layer|fallbacks LiteLLM]]).

---

Qu'est-ce qu'un circuit breaker et pourquoi l'utiliser ?
?
Un composant qui, après un **taux d'échec** élevé vers un fournisseur, **coupe** les appels vers lui pendant un moment et bascule directement sur le fallback. Il évite d'**attendre des timeouts** à chaque requête et de **surcharger** un service déjà en difficulté.

---

Comment gérer une sortie mal formée ?
?
1. **Prévenir** : [[63-guided-generation|structured outputs]] / décodage contraint.
2. **Valider** : schéma (Pydantic, JSON Schema) + règles métier.
3. **Réparer** : ré-appel avec **le message d'erreur** de validation (1 ou 2 fois max).
4. **Dégrader** : valeur par défaut ou erreur explicite, jamais une sortie invalide propagée en aval.

---

Qu'est-ce que la dégradation gracieuse ?
?
Continuer à rendre **un service réduit** plutôt que tomber : réponse sans RAG si l'index est indisponible (en le signalant), petit modèle si le gros sature, **désactivation** des fonctions non essentielles, **file d'attente** plutôt que refus. On définit à l'avance **quels niveaux de service** existent.

---

Comment gérer les rate limits d'un fournisseur ?
?
- Connaître ses quotas (**requêtes/min et tokens/min**) et les **répartir** entre applications.
- **File d'attente** avec priorités (interactif avant batch).
- **Limiteur côté client** (token bucket) pour ne pas envoyer des requêtes vouées au 429.
- Répartir sur **plusieurs clés, régions ou fournisseurs**, ou réserver du **débit provisionné**.

---

Comment rendre fiable une tâche d'agent de longue durée ?
?
- L'exécuter **hors de la requête HTTP** (file de tâches, workflow durable).
- **Checkpointer l'état** à chaque étape pour reprendre après une panne ([[45-langgraph-production|durable execution]], [[41-automatisation-code-nocode|Temporal]]).
- **Idempotence** des outils à effets de bord (clé d'idempotence).
- **Limites** : nombre d'étapes, budget de tokens, durée.

---

Pourquoi épingler la version du modèle ?
?
Un alias type « latest » peut **changer de modèle sans prévenir** → comportement, format ou coût modifiés en production. On épingle une **version datée**, on **teste** la nouvelle version sur les evals, puis on migre volontairement — et on surveille les **dates de dépréciation** des fournisseurs ([[113-monitoring-drift-feedback|mises à jour des modèles API]]).

---

Quels SLO définir pour une application LLM ?
?
- **Disponibilité** (taux de requêtes réussies, fallbacks compris).
- **Latence** : TTFT p95, durée totale p95 par type de tâche.
- **Qualité** : taux de sorties valides, score d'eval online au-dessus d'un seuil.
- **Coût** par requête sous un plafond.

Avec un **budget d'erreur** qui décide quand geler les changements ([[64-metriques-slo-inference|SLO d'inférence]]).

---

Comment tester la résilience ?
?
Par du **chaos testing** : injecter des 429, des timeouts, des flux coupés, des réponses invalides, un index vide, et vérifier que les fallbacks, circuit breakers et messages dégradés fonctionnent. Et des **tests de charge** avec des longueurs de prompt **réalistes** (la charge dépend des tokens, pas du nombre de requêtes).

---

## Mises en situation

Mise en situation : pendant un pic, ton application renvoie massivement des 429 et tes retries aggravent la situation. Que corriges-tu dans l'ordre ?
?
1. **Arrêter l'amplification** : backoff exponentiel avec jitter, respect de l'en-tête de reprise, budget global de retries
2. **Limiteur côté client** : ne pas envoyer des requêtes vouées au refus, avec des priorités (interactif avant batch)
3. **Circuit breaker** : couper vers le fournisseur en difficulté et basculer directement sur le fallback
4. **Répartir** : plusieurs clés, régions ou fournisseurs, ou débit réservé ([[81-litellm-api-layer|gateway]])
5. **Dégrader** : petit modèle, file d'attente, message explicite, plutôt qu'une page d'erreur

**Piège** : retenter aveuglément une action non idempotente, comme un envoi d'e-mail ou un paiement.

---

Mise en situation : ton équipe veut « tester la résilience » avant une mise en production critique. Que proposes-tu concrètement ?
?
1. **Injecter des pannes** : 429, timeouts, flux coupé en plein streaming, réponse invalide, index vide
2. **Vérifier chaque parade** : fallback réellement fonctionnel, circuit breaker qui s'ouvre, message dégradé affiché
3. **Tests de charge réalistes** : distribution des longueurs de prompts, pas seulement un nombre de requêtes
4. **Vérifier les timeouts** à tous les niveaux : connexion, premier token, entre tokens, global
5. **Vérifier les reprises** : une tâche d'agent interrompue doit repartir de son dernier point ([[45-langgraph-production|durable execution]])

**Piège** : tester un fallback qui n'a jamais été évalué, et découvrir qu'il produit des réponses inutilisables.

---

## Connexions
- [[141-system-design-llm|System design LLM]] — la méthode d'ensemble
- [[81-litellm-api-layer|LiteLLM]] — retries, fallbacks, load balancing
- [[63-guided-generation|Guided generation]] — sorties valides par construction
- [[45-langgraph-production|LangGraph production]] — durable execution
- [[64-metriques-slo-inference|Métriques & SLO]] — définir les objectifs
- [[93-monitoring-inference|Monitoring de l'inférence]] — détecter les défaillances
- [[00-moc-ai-engineering|MOC AI Engineering]]
