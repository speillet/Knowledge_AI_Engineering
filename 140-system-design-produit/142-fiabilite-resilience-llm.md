# Fiabilité & résilience des applications LLM — Flashcards
Tags: #flashcards #ai-engineering #system-design #fiabilite #production #llm
<!-- summary: timeouts, retries, fallbacks, circuit breaker, retry, fallback ou circuit breaker, retries multipliés entre couches, sorties mal formées, dégradation gracieuse, rate limits, tâches longues, épinglage de version, SLO, chaos testing, classification des erreurs d'un circuit breaker. -->


Pourquoi une application LLM est-elle plus fragile qu'une application classique ? <!--anki:47364949697173294a73-->
?
Elle dépend d'un service **externe, lent, coûteux et non déterministe** : latences de plusieurs secondes à plusieurs minutes, **rate limits**, pannes du fournisseur, **sorties mal formées**, et changements de comportement lors des **mises à jour du modèle**. La résilience doit être **conçue**, pas ajoutée après coup.

Même auto-hébergé, un modèle conserve des sorties à valider et des ressources limitées. Distinguer succès technique et succès métier : HTTP 200 peut transporter une réponse inutilisable. Prévoir timeouts, validation, budget de reprise et mode dégradé explicite.

---

Quels timeouts configurer sur les appels à un LLM ? <!--anki:455f43415a692f2c7b6f-->
?
Distinguer **connexion**, attente de la première réponse utile, **inactivité du flux** et **durée totale**. Ces délais protègent contre des problèmes différents : réseau inaccessible, attente excessive, stream bloqué ou tâche qui s'éternise.

Un long TTFT peut venir de la file, du prefill, du raisonnement ou du transport ; il ne prouve pas à lui seul une saturation. Propager une échéance globale aux outils et retries, puis annuler le travail aval si elle expire. Tester les heartbeats : des octets réguliers peuvent maintenir un flux vivant sans fournir de contenu utile à l'utilisateur.

---

Comment faire des retries correctement sur une API LLM ? <!--anki:47233729762a372f7c5f-->
?
- Seulement sur les erreurs **transitoires** (429, 5xx, timeouts), **jamais** sur les 400 (requête invalide).
- **Backoff exponentiel avec jitter**, en respectant l'en-tête **Retry-After**.
- **Nombre limité** de tentatives et **budget de retries** global pour ne pas amplifier une panne.
- Attention aux actions **non idempotentes** d'un agent (paiement, e-mail) : pas de retry aveugle.

Chaque tentative consomme le délai restant et peut déjà être facturée. Sur timeout d'une écriture, rechercher son résultat par identifiant avant de rejouer ; distinguer réponse perdue et opération certainement non exécutée.

---

Qu'est-ce qu'une chaîne de fallbacks ? <!--anki:4b612e3c3921336d733a-->
?
Une **suite bornée de solutions de repli**, choisies selon l'erreur et le contrat : autre backend compatible, autre modèle évalué, ou dégradation explicitement annoncée ([[81-litellm-api-layer|fallbacks LiteLLM]]).

Exemple : après indisponibilité d'une région, une seconde région autorisée peut convenir ; après arguments invalides, changer de région ne corrige probablement rien. Un autre modèle peut aussi manquer le schéma ou la fenêtre de contexte requis.

Conserver délai et budget globaux, éviter les pannes communes aux backends et ne pas rejouer un effet déjà exécuté. Arrêter la chaîne quand aucune option admissible ne reste. Une FAQ statique peut informer, sans être comptée comme résolution complète de toute demande.

---

Qu'est-ce qu'un circuit breaker et pourquoi l'utiliser ? <!--anki:424258362c2624254676-->
?
Un composant qui, après un **taux d'échec** élevé vers un fournisseur, **coupe** les appels vers lui pendant un moment et bascule directement sur le fallback. Il évite d'**attendre des timeouts** à chaque requête et de **surcharger** un service déjà en difficulté.

Il a trois états : **fermé**, les appels passent ; **ouvert**, ils sont coupés pendant une durée, par exemple 30 s ; **semi-ouvert**, quelques requêtes test passent et le circuit se referme si elles réussissent. Le seuil se calcule sur une fenêtre glissante avec un minimum d'appels, par exemple 50 % d'échecs sur au moins 20 requêtes, pour ne pas couper sur deux erreurs isolées.

---

Comment gérer une sortie LLM mal formée dans une application ? <!--anki:507e476873755e536655-->
?
1. **Prévenir** : [[63-guided-generation|structured outputs]] / décodage contraint.
2. **Valider** : schéma (Pydantic, JSON Schema) + règles métier.
3. **Réparer** : ré-appel avec **le message d'erreur** de validation (1 ou 2 fois max).
4. **Dégrader** : valeur par défaut ou erreur explicite, jamais une sortie invalide propagée en aval.

Une valeur par défaut doit être explicitement admissible et signalée comme telle. Pour une facture, remplacer un montant illisible par zéro peut être syntaxiquement valide mais dangereux ; préférer un statut incomplet et une revue.

---

Qu'est-ce que la dégradation gracieuse d'un service LLM ? <!--anki:706e317761743a564431-->
?
Continuer à rendre un **service réduit mais conforme à un contrat explicite** : modèle de secours évalué, fonctions non essentielles désactivées, délai supplémentaire borné ou transfert humain. Chaque mode définit ce qu'il peut encore promettre et comment revenir à la normale.

Répondre sans RAG n'est acceptable que si la tâche autorise une réponse non documentaire ; pour une procédure interne, mieux vaut souvent s'abstenir. Une file doit avoir capacité et échéance limitées. Tester aussi permissions, qualité et messages utilisateur dans chaque mode dégradé.

---

Comment gérer les rate limits d'un fournisseur ? <!--anki:71434b7834454773454e-->
?
Respecter les **quotas autorisés** de requêtes, tokens et concurrence, qui peuvent être partagés par organisation, projet, modèle ou région. Un limiteur en amont et des files bornées évitent d'envoyer une charge déjà vouée au refus.

Prioriser l'interactif, tenir compte de Retry-After et borner les retries. Demander davantage de capacité ou répartir vers des déploiements autorisés et validés si nécessaire. Multiplier les clés ne crée pas forcément du quota et ne doit pas servir à contourner une limite commune. Tester la capacité du secours avant une panne.

---

Comment rendre fiable une tâche d'agent de longue durée ? <!--anki:6432522c7d30417a6769-->
?
- L'exécuter **hors de la requête HTTP** (file de tâches, workflow durable).
- **Checkpointer l'état** à chaque étape pour reprendre après une panne ([[45-langgraph-production|durable execution]], [[41-automatisation-code-nocode|Temporal]]).
- **Idempotence** des outils à effets de bord (clé d'idempotence).
- **Limites** : nombre d'étapes, budget de tokens, durée.

Tester un crash après l'effet métier mais avant son checkpoint. À la reprise, consulter l'opération persistée avec la même identité au lieu de supposer qu'elle n'a pas eu lieu. Un statut « inconnu, vérification en cours » vaut mieux qu'un faux échec suivi d'un doublon.

---

Pourquoi épingler la version du modèle ? <!--anki:5043614c313623677e64-->
?
Un alias type « latest » peut **changer de modèle sans prévenir** → comportement, format ou coût modifiés en production. On épingle une **version datée**, on **teste** la nouvelle version sur les evals, puis on migre volontairement — et on surveille les **dates de dépréciation** des fournisseurs ([[113-monitoring-drift-feedback|mises à jour des modèles API]]).

Épingler n'empêche ni dépréciation ni changement d'infrastructure autour du modèle. Conserver la combinaison prompt, outils et paramètres validés, puis tester un remplacement avant l'échéance ; prévoir une date de revue et une route de secours compatible.

---

Quels SLO définir pour une application LLM ? <!--anki:6c773648497256297b71-->
?
- **Disponibilité** (taux de requêtes réussies, fallbacks compris).
- **Latence** : TTFT p95, durée totale p95 par type de tâche.
- **Qualité** : taux de sorties valides, score d'eval online au-dessus d'un seuil.
- **Coût** par requête sous un plafond.

Avec un **budget d'erreur** qui décide quand geler les changements ([[64-metriques-slo-inference|SLO d'inférence]]).

Définir pour chaque indicateur population, fenêtre et traitement des refus, timeouts et annulations. Un HTTP 200 avec un montant faux ne compte pas comme réussite métier ; séparer validité de forme et exactitude utile.

---

Comment tester la résilience d'une application LLM ? <!--anki:68407a3a592331445669-->
?
Par du **chaos testing** : injecter des 429, des timeouts, des flux coupés, des réponses invalides, un index vide, et vérifier que les fallbacks, circuit breakers et messages dégradés fonctionnent. Et des **tests de charge** avec des longueurs de prompt **réalistes** (la charge dépend des tokens, pas du nombre de requêtes).

Fixer avant l'essai le comportement attendu et les invariants métier. Couper après un effet externe puis reprendre vérifie davantage qu'un timeout simulé avant tout appel ; contrôler aussi absence de doublon et annulation effective.

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

Calcul : avec des disponibilités indépendantes de 99,5 % et une bascule parfaite, comparer trois services obligatoires en série à deux fournisseurs redondants. Quels temps d’indisponibilité moyens sur 30 jours ? <!--anki:3430313231643964333833343465356439306135343731396564333462393436-->
?
Sous hypothèse d'**indépendance** et de bascule parfaite :
```text
3 services obligatoires en série : 0,995³ ≈ 0,985075
→ environ 10,75 h indisponibles sur 30 jours
2 fournisseurs redondants : 1 − (1 − 0,995)² = 0,999975
→ environ 1,08 min indisponible sur 30 jours
```
En série, ce sont les **disponibilités qui se multiplient**. En redondance, on multiplie les probabilités d'indisponibilité simultanée. Le fallback ne protège pas une gateway commune en panne ; corrélation, délais de détection, capacité de secours et échecs de bascule dégradent le résultat réel ([[82-routing-llm|fallbacks]]).

Ces temps représentent une traduction théorique des probabilités en durée attendue. Ils ne décrivent pas la fréquence ni la durée de chaque incident : une même disponibilité peut correspondre à une longue panne ou de nombreuses microcoupures.

---

Pourquoi un circuit breaker doit-il distinguer panne fournisseur et erreur propre à une requête ? <!--anki:3632643539613639346636623436333061363833336131333665313131373836-->
?
Un **circuit breaker** suspend temporairement les appels vers une dépendance défaillante. S'il compte une entrée invalide ou un refus métier comme panne globale, quelques requêtes peuvent bloquer le service pour tous.

Classer erreurs récupérables, erreurs de contrat et décisions métier ; choisir la portée du circuit par dépendance ou route pertinente. Tester la réouverture avec un trafic limité et un budget partagé avec les retries. Une bascule doit préserver droits, format et contraintes de données. Le circuit protège la capacité ; il ne corrige pas une demande incorrecte.

---

## Mises en situation

Mise en situation : pendant un pic, ton application renvoie massivement des 429 et tes retries aggravent la situation. Que corriges-tu dans l'ordre ? <!--anki:64417942635e45495449-->
?
1. **Arrêter l'amplification** : backoff exponentiel avec jitter, respect de l'en-tête de reprise, budget global de retries
2. **Limiteur côté client** : ne pas envoyer des requêtes vouées au refus, avec des priorités (interactif avant batch)
3. **Circuit breaker** : couper vers le fournisseur en difficulté et basculer directement sur le fallback
4. **Répartir dans les limites autorisées** : régions ou fournisseurs validés, débit réservé ou quota supplémentaire demandé ([[81-litellm-api-layer|gateway]])
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

## Sources
- [Google SRE — surcharge et admission](https://sre.google/sre-book/handling-overload/)

## Connexions
- [[141-system-design-llm|System design LLM]] — la méthode d'ensemble
- [[81-litellm-api-layer|LiteLLM]] — retries, fallbacks, load balancing
- [[63-guided-generation|Guided generation]] — sorties valides par construction
- [[45-langgraph-production|LangGraph production]] — durable execution
- [[64-metriques-slo-inference|Métriques & SLO]] — définir les objectifs
- [[93-monitoring-inference|Monitoring de l'inférence]] — détecter les défaillances
- [[84-streaming-integration-applicative|Streaming & intégration]] — idempotence et tâches longues
- [[145-cas-system-design|Cas de system design]] — des architectures types commentées
- [[149-livraison-idempotence-concurrence|Idempotence & concurrence]] — sécuriser les retries et gérer les résultats inconnus
- [[116-sre-incidents-capacite-ia|SRE : incidents & capacité des services IA]] — passer des mécanismes à leur exploitation
- [[00-moc-ai-engineering|MOC AI Engineering]]
