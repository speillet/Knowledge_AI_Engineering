# Fiabilité & résilience des applications LLM — Flashcards
Tags: #flashcards #ai-engineering #system-design #fiabilite #production #llm
<!-- summary: timeouts, retries, fallbacks, circuit breaker, retry, fallback ou circuit breaker, retries multipliés entre couches, sorties mal formées, dégradation gracieuse, rate limits, tâches longues, épinglage de version, SLO, chaos testing. -->


Pourquoi une application LLM est-elle plus fragile qu'une application classique ? <!--anki:47364949697173294a73-->
?
Elle dépend d'un service **externe, lent, coûteux et non déterministe** : latences de plusieurs secondes à plusieurs minutes, **rate limits**, pannes du fournisseur, **sorties mal formées**, et changements de comportement lors des **mises à jour du modèle**. La résilience doit être **conçue**, pas ajoutée après coup.

---

Quels timeouts configurer sur les appels à un LLM ? <!--anki:455f43415a692f2c7b6f-->
?
- **Timeout de connexion** court.
- **Timeout jusqu'au premier token** (TTFT) : détecte un modèle saturé.
- **Timeout entre tokens** en streaming : détecte un flux bloqué.
- **Timeout global** adapté à la tâche (un agent ≠ une autocomplétion).

Un seul timeout global de 60 s laisse l'utilisateur attendre **sans rien voir**.

---

Comment faire des retries correctement sur une API LLM ? <!--anki:47233729762a372f7c5f-->
?
- Seulement sur les erreurs **transitoires** (429, 5xx, timeouts), **jamais** sur les 400 (requête invalide).
- **Backoff exponentiel avec jitter**, en respectant l'en-tête **Retry-After**.
- **Nombre limité** de tentatives et **budget de retries** global pour ne pas amplifier une panne.
- Attention aux actions **non idempotentes** d'un agent (paiement, e-mail) : pas de retry aveugle.

---

Qu'est-ce qu'une chaîne de fallbacks ? <!--anki:4b612e3c3921336d733a-->
?
En cas d'échec du modèle principal : **même modèle chez un autre fournisseur/région** → **autre modèle** comparable → **modèle plus petit** → **réponse dégradée** (message d'attente, FAQ, humain). Chaque fallback doit être **évalué** : un prompt optimisé pour un modèle peut mal marcher sur un autre ([[81-litellm-api-layer|fallbacks LiteLLM]]).

---

Qu'est-ce qu'un circuit breaker et pourquoi l'utiliser ? <!--anki:424258362c2624254676-->
?
Un composant qui, après un **taux d'échec** élevé vers un fournisseur, **coupe** les appels vers lui pendant un moment et bascule directement sur le fallback. Il évite d'**attendre des timeouts** à chaque requête et de **surcharger** un service déjà en difficulté.

---

Comment gérer une sortie mal formée ? <!--anki:507e476873755e536655-->
?
1. **Prévenir** : [[63-guided-generation|structured outputs]] / décodage contraint.
2. **Valider** : schéma (Pydantic, JSON Schema) + règles métier.
3. **Réparer** : ré-appel avec **le message d'erreur** de validation (1 ou 2 fois max).
4. **Dégrader** : valeur par défaut ou erreur explicite, jamais une sortie invalide propagée en aval.

---

Qu'est-ce que la dégradation gracieuse ? <!--anki:706e317761743a564431-->
?
Continuer à rendre **un service réduit** plutôt que tomber : réponse sans RAG si l'index est indisponible (en le signalant), petit modèle si le gros sature, **désactivation** des fonctions non essentielles, **file d'attente** plutôt que refus. On définit à l'avance **quels niveaux de service** existent.

---

Comment gérer les rate limits d'un fournisseur ? <!--anki:71434b7834454773454e-->
?
- Connaître ses quotas (**requêtes/min et tokens/min**) et les **répartir** entre applications.
- **File d'attente** avec priorités (interactif avant batch).
- **Limiteur côté client** (token bucket) pour ne pas envoyer des requêtes vouées au 429.
- Répartir sur **plusieurs clés, régions ou fournisseurs**, ou réserver du **débit provisionné**.

---

Comment rendre fiable une tâche d'agent de longue durée ? <!--anki:6432522c7d30417a6769-->
?
- L'exécuter **hors de la requête HTTP** (file de tâches, workflow durable).
- **Checkpointer l'état** à chaque étape pour reprendre après une panne ([[45-langgraph-production|durable execution]], [[41-automatisation-code-nocode|Temporal]]).
- **Idempotence** des outils à effets de bord (clé d'idempotence).
- **Limites** : nombre d'étapes, budget de tokens, durée.

---

Pourquoi épingler la version du modèle ? <!--anki:5043614c313623677e64-->
?
Un alias type « latest » peut **changer de modèle sans prévenir** → comportement, format ou coût modifiés en production. On épingle une **version datée**, on **teste** la nouvelle version sur les evals, puis on migre volontairement — et on surveille les **dates de dépréciation** des fournisseurs ([[113-monitoring-drift-feedback|mises à jour des modèles API]]).

---

Quels SLO définir pour une application LLM ? <!--anki:6c773648497256297b71-->
?
- **Disponibilité** (taux de requêtes réussies, fallbacks compris).
- **Latence** : TTFT p95, durée totale p95 par type de tâche.
- **Qualité** : taux de sorties valides, score d'eval online au-dessus d'un seuil.
- **Coût** par requête sous un plafond.

Avec un **budget d'erreur** qui décide quand geler les changements ([[64-metriques-slo-inference|SLO d'inférence]]).

---

Comment tester la résilience d'une application LLM ? <!--anki:68407a3a592331445669-->
?
Par du **chaos testing** : injecter des 429, des timeouts, des flux coupés, des réponses invalides, un index vide, et vérifier que les fallbacks, circuit breakers et messages dégradés fonctionnent. Et des **tests de charge** avec des longueurs de prompt **réalistes** (la charge dépend des tokens, pas du nombre de requêtes).

---

À ne pas confondre : retry, fallback et circuit breaker ? <!--anki:712c79247c783766604f-->
?
- **Retry** : **rejouer la même requête** sur le même fournisseur, pour une erreur transitoire
- **Fallback** : envoyer la requête **ailleurs** (autre modèle, autre fournisseur, réponse dégradée) quand le premier choix échoue
- **Circuit breaker** : **arrêter d'appeler** un fournisseur défaillant pendant un temps, pour ne pas empiler les timeouts

Ils s'enchaînent : quelques retries, puis fallback, et le disjoncteur évite de payer ces retries quand la panne est franche ([[82-routing-llm|routing]]).

---

Que se passe-t-il si chaque couche d'un système réessaie trois fois ? <!--anki:64766361467b4e364763-->
?
Les retries se **multiplient** : front, orchestrateur et client LLM à 3 tentatives chacun donnent jusqu'à **3³ = 27 appels** au fournisseur pour une requête utilisateur. Pendant une panne partielle, c'est une **tempête de retries** qui empêche le service de récupérer, et qui coûte en tokens.

Parades : réessayer à **une seule couche**, **budget de retries** global (ex. 10 % du trafic), **jitter** pour désynchroniser les clients, et **circuit breaker** ([[82-routing-llm|fallbacks]]).

---

Calcul : quelle disponibilité pour une chaîne de 3 services à 99,5 %, et avec un fallback ? <!--anki:3430313231643964333833343465356439306135343731396564333462393436-->
?
```text
3 services en série             : 0,995³ ≈ 0,985     → ≈ 11 h d'indisponibilité par mois
fournisseur à 99,5 %
+ fallback indépendant à 99,5 % : 1 − 0,005² ≈ 0,99998 → ≈ 1 min par mois
```
Les dépendances en série **multiplient** les indisponibilités ; un fallback indépendant les fait presque disparaître, à condition que les pannes **ne soient pas corrélées** : même cloud, même région, même modèle ([[82-routing-llm|fallbacks]]).

---

## Mises en situation

Mise en situation : pendant un pic, ton application renvoie massivement des 429 et tes retries aggravent la situation. Que corriges-tu dans l'ordre ? <!--anki:64417942635e45495449-->
?
1. **Arrêter l'amplification** : backoff exponentiel avec jitter, respect de l'en-tête de reprise, budget global de retries
2. **Limiteur côté client** : ne pas envoyer des requêtes vouées au refus, avec des priorités (interactif avant batch)
3. **Circuit breaker** : couper vers le fournisseur en difficulté et basculer directement sur le fallback
4. **Répartir** : plusieurs clés, régions ou fournisseurs, ou débit réservé ([[81-litellm-api-layer|gateway]])
5. **Dégrader** : petit modèle, file d'attente, message explicite, plutôt qu'une page d'erreur

**Piège** : retenter aveuglément une action non idempotente, comme un envoi d'e-mail ou un paiement.

---

Mise en situation : ton équipe veut « tester la résilience » avant une mise en production critique. Que proposes-tu concrètement ? <!--anki:427533363e3e53507373-->
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
- [[84-streaming-integration-applicative|Streaming & intégration]] — idempotence et tâches longues
- [[145-cas-system-design|Cas de system design]] — des architectures types commentées
- [[00-moc-ai-engineering|MOC AI Engineering]]
