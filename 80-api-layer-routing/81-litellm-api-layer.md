# LiteLLM (API layer) — Flashcards
Tags: #flashcards #ai-engineering #api-layer #litellm #llm
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.
<!-- summary: SDK ou proxy, virtual keys, budgets, rate limits, fallbacks, load balancing, callbacks d'observabilité, alternatives (gateways auto-hébergées, services des clouds, agrégateurs). -->


Qu'est-ce qu'une API layer (LLM gateway) ? <!--anki:79752c38462d5a6c3765-->
?
Une **couche unique entre les applications et tous les modèles** (API cloud et modèles auto-hébergés) : une seule interface, et des fonctions transverses centralisées (auth, budgets, fallbacks, logs).

Elle donne aux applications un point d'accès cohérent et centralise les politiques communes. Par exemple, une clé d'équipe peut accéder à certains modèles dans un budget donné. Cette couche devient aussi une dépendance du service : prévoir disponibilité, configuration versionnée et capacité à diagnostiquer une erreur de routage.

---

Qu'est-ce que LiteLLM ? <!--anki:496b6e43213c2b593774-->
?
Un projet open source qui expose **plus de 100 fournisseurs de LLM au format de l'API OpenAI**. Il existe sous deux formes : un **SDK Python** et un **proxy** (serveur gateway).

L'interface commune simplifie le code client, mais ne gomme pas toutes les différences des fournisseurs : paramètres, outils, schémas et erreurs peuvent varier. Vérifier les capacités du modèle et de l'intégration choisis. Tester le chemin exact de l'application avant de considérer deux backends comme interchangeables.

---

SDK ou proxy LiteLLM ? <!--anki:7531606c2c72556e5870-->
?
- **SDK** : bibliothèque dans le code (`litellm.completion(...)`), idéale pour un seul service
- **Proxy** : serveur **centralisé** pour toute l'organisation, avec clés, budgets et observabilité partagés

Le SDK évite un service réseau supplémentaire mais disperse la configuration si plusieurs applications l'utilisent séparément. Le proxy facilite les politiques communes, au prix d'un composant à héberger et superviser. Dans les deux cas, les permissions du fournisseur et les règles de traitement des données doivent correspondre à l'usage.

---

Comment configurer plusieurs déploiements derrière un alias du proxy LiteLLM ? <!--anki:75244e56214c4d524272-->
?
```yaml
model_list:
  - model_name: chat-default
    litellm_params:
      model: hosted_vllm/meta-llama/Llama-3.1-8B-Instruct
      api_base: http://vllm.inference.svc:8000/v1
  - model_name: chat-default
    litellm_params:
      model: anthropic/claude-sonnet-4-5
```
Deux déploiements sous le même nom : le proxy **répartit la charge** entre eux.

`model_name` est l'alias demandé par le client ; chaque entrée est un déploiement candidat. Ajouter les identifiants via des secrets et choisir la stratégie de routage. Ici les modèles diffèrent : la répartition peut changer la qualité des réponses ; pour une simple réplication, utiliser des backends fonctionnellement équivalents et tester les capacités requises.

---

Que sont les virtual keys de LiteLLM ? <!--anki:685b522c2437213a3750-->
?
Des **clés API émises par le proxy** (par équipe, projet ou utilisateur) : les vraies clés des fournisseurs restent **secrètes**, et chaque virtual key a ses **modèles autorisés, budget et limites**.

L'application utilise sa clé virtuelle et le proxy appelle le fournisseur avec le secret approprié. Cela facilite révocation et attribution de dépenses sans distribuer les clés maîtresses. Protéger néanmoins la clé virtuelle : elle autorise des appels facturables. Vérifier les permissions effectives, la rotation et la disponibilité du stockage de configuration.

---

Comment LiteLLM maîtrise-t-il les coûts ? <!--anki:462c433f457b28282c46-->
?
Par le **suivi des dépenses** par clé, équipe ou utilisateur, des **budgets** (plafond sur une période) et des **rate limits** en requêtes et tokens par minute (RPM/TPM).

Les budgets bornent la dépense sur une durée, tandis que les limites RPM/TPM contrôlent le rythme. Des requêtes concurrentes et une comptabilité différée peuvent produire un dépassement : tester les garanties de la configuration choisie. Prévoir alertes, marges et conduite en cas de quota atteint, sans retries qui aggraveraient la saturation.

---

Comment LiteLLM améliore-t-il la fiabilité ? <!--anki:6369583735646953616f-->
?
- **Retries** sur erreurs transitoires
- **Fallbacks** vers un autre modèle ou fournisseur si le premier échoue
- **Load balancing** entre déploiements, avec cooldown des déploiements en erreur

Limiter le nombre de tentatives et le temps total pour éviter une tempête de retries. Un fallback doit respecter les mêmes contraintes de données, de capacités et de qualité que le modèle initial. Après le début d'un streaming, remplacer silencieusement la réponse est délicat : définir le comportement de reprise côté client.

---

Comment relier LiteLLM à l'observabilité ? <!--anki:4e6e34374d5732535658-->
?
Par des **callbacks** : chaque appel est envoyé à [[91-langfuse-observabilite|Langfuse]] (ou OpenTelemetry, Prometheus) avec prompt, réponse, tokens, coût et latence — sans instrumenter chaque application.

La gateway voit les appels modèles, mais pas forcément toutes les étapes métier ou les outils externes ; propager un identifiant de trace et instrumenter ces étapes dans l'application. Filtrer les données sensibles avant export et définir rétention et accès. Une trace complète doit expliquer le résultat sans collecter inutilement des secrets.

---

Où se place LiteLLM dans la stack ? <!--anki:65484f7c36453a766272-->
?
```text
Client → Ingress (TLS) → LiteLLM (auth, quotas, routing) → vLLM / API cloud
```
L'[[83-gateway-ingress|Ingress]] gère le réseau ; LiteLLM gère la **logique propre aux LLM**.

Le client reçoit une interface commune tandis que la gateway choisit le backend et applique les politiques de coût. Chaque saut ajoute une possibilité d'erreur, de délai ou de buffering du stream. Aligner les timeouts, propager les identifiants de requête et vérifier l'authentification à chaque frontière exposée.

---

Quel type de gateway LLM choisir : auto-hébergée, service managé du cloud, ou agrégateur SaaS ? <!--anki:3236613063623236323539633436323039303964303466393931623061646136-->
?
- **Auto-hébergeable** (LiteLLM, Portkey, Kong AI Gateway, Envoy AI Gateway, agentgateway qui gère aussi MCP et A2A) : quand les **données ne doivent pas sortir**, ou pour garder la main sur le routage et les budgets
- **Service managé du cloud** (AWS, Azure, Google) : quand tout est déjà **chez un même cloud** et qu'on ne veut rien exploiter
- **Agrégateur SaaS** (OpenRouter) : pour accéder à **beaucoup de fournisseurs** sans infrastructure ni contrats séparés

Critères communs : fournisseurs couverts, budgets et virtual keys, observabilité, latence ajoutée.

---

Que se passe-t-il quand une virtual key LiteLLM atteint son budget ? <!--anki:3363626463666234653138353463303961396535356364323734336663613965-->
?
Le proxy **refuse** les requêtes suivantes avec une erreur explicite, jusqu'à la fin de la période (`budget_duration`) ou un relèvement du plafond.

Pour l'application, c'est une **panne** : il faut gérer cette erreur (message clair, mode dégradé), et **alerter avant** le plafond, par exemple à 80 % ([[122-finops-llm|FinOps]]).

---

## Mises en situation

Mise en situation : cinq équipes appellent directement les API de trois fournisseurs, avec des clés partagées par copier-coller. La facture mensuelle n'est attribuable à personne. Par quoi commences-tu ? <!--anki:6a6e56307e5b2b4c726f-->
?
1. **Mettre une gateway devant** : toutes les applications passent par le proxy, au format de l'API OpenAI
2. **Virtual keys** par équipe et par projet : les vraies clés des fournisseurs redeviennent secrètes
3. **Budgets et rate limits** par clé, avec alertes avant dépassement ([[122-finops-llm|FinOps]])
4. **Callbacks d'observabilité** : traces, coûts et latences centralisés sans instrumenter chaque application ([[91-langfuse-observabilite|Langfuse]])
5. **Migrer progressivement** : commencer par une équipe volontaire, puis fermer l'accès direct

**Piège** : faire de la gateway un point de défaillance unique sans réplicas ni supervision.

---

Mise en situation : ton fournisseur principal connaît une panne de 40 minutes en pleine journée. Comment ton architecture aurait-elle dû réagir ? <!--anki:67297e4a71396d5d5e4f-->
?
1. **Fallback configuré** vers un autre fournisseur ou un modèle auto-hébergé pour les routes critiques
2. **Retries** avec backoff sur les erreurs transitoires, et **cooldown** du déploiement en erreur
3. **Dégradation acceptable** : modèle moins bon mais disponible, ou réponse d'attente explicite ([[142-fiabilite-resilience-llm|fiabilité]])
4. **Vérifier la compatibilité** : le modèle de secours doit avoir été testé sur les mêmes evals
5. **Mesurer** : taux d'erreurs et bascules, pour savoir a posteriori ce qui s'est passé

**Piège** : déclarer un fallback jamais testé, qui échoue au moment où on en a besoin.

---

## Sources

- [LiteLLM — proxy et gateway](https://docs.litellm.ai/docs/simple_proxy)

## Connexions
- [[83-gateway-ingress|Ingress & API gateway]] — l'entrée réseau devant LiteLLM
- [[82-routing-llm|Routing LLM]] — choisir le bon modèle par requête
- [[91-langfuse-observabilite|Langfuse]] — les traces envoyées par callbacks
- [[64-metriques-slo-inference|Métriques & SLO]] — rate limits et timeouts
- [[11-serveurs-inference-llm|Serveurs d'inférence]] — les backends auto-hébergés
- [[122-finops-llm|FinOps LLM]] — budgets et attribution des coûts
- [[93-monitoring-inference|Monitoring de l'inférence]] — les métriques d'usage collectées à la gateway
- [[142-fiabilite-resilience-llm|Fiabilité & résilience]] — retries, fallbacks, circuit breakers
- [[84-streaming-integration-applicative|Streaming & intégration]] — relayer et annuler les flux
- [[101-securite-llm-guardrails|Sécurité LLM]] — injection, exfiltration et guardrails
- [[123-caching-agressif|Caching]] — prompt caching et caches de réponses
- [[141-system-design-llm|System design LLM]] — la méthode de conception
- [[33-mcp|MCP]] — le protocole standard entre agents et outils
- [[38-plateformes-agents|Plateformes d'agents]] — runtime, sandbox, gateway d'outils et identité
- [[41-automatisation-code-nocode|Automatisation code & no-code]] — workflows et outils no-code
- [[46-crewai-crews|CrewAI — Crews]] — équipes d'agents à rôles
- [[85-carte-protocoles-agentiques|Carte des protocoles]] — quel protocole à quelle frontière de l'agent
- [[00-moc-ai-engineering|MOC AI Engineering]]
