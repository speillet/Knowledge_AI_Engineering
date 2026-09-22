# Plateformes d'agents — Architecture & gouvernance — Flashcards
Tags: #flashcards #ai-engineering #agents #platform #gouvernance #llm

Pourquoi construire une plateforme d'agents interne plutôt que laisser chaque équipe se débrouiller ?
?
Sans plateforme, chaque équipe réimplémente runtime, identité, accès aux outils, observabilité et contrôles, chacune à sa manière. L'équipe plateforme fournit un **chemin balisé** (paved road) : templates, outils approuvés, mémoire, authentification, traces et evals prêts à l'emploi. Les équipes produit se concentrent sur la logique métier.

L'enjeu est réel : Gartner prévoit que **plus de 40 % des projets agentiques seront annulés d'ici fin 2027**, pour trois raisons (coûts, valeur floue, contrôle des risques insuffisant) qu'une plateforme traite dès le départ.

---

Quelle différence entre plan de contrôle et plan d'exécution d'une plateforme d'agents ?
?
- **Plan de contrôle** : ce qui **décide** : registre des agents, identités, politiques d'accès, versions et configurations, budgets, approbations
- **Plan d'exécution** : ce qui **fait tourner** : runtime, sandboxes, gateways LLM et outils, mémoire, émission des traces

Les séparer permet de **gouverner des agents construits n'importe où**, y compris chez d'autres éditeurs. Exemple : chez Microsoft, **Foundry** construit et exécute les agents, et **Agent 365** (disponible depuis mai 2026) sert de plan de contrôle pour tous les agents de l'entreprise, y compris les agents « fantômes » découverts dans le tenant.

---

À quoi ressemble l'architecture de référence d'une plateforme d'agents ?
?
```text
Utilisateurs, apps, autres agents (A2A)
        ↓
Gateway d'agents : authentification, routage, quotas
        ↓
Runtime : sessions isolées, harness (boucle d'agent)
   ├─ Gateway LLM ──────→ modèles (routing, budgets)
   ├─ Gateway d'outils ─→ outils MCP, API   ← moteur de politiques
   ├─ Sandbox ──────────→ code, navigateur
   └─ Mémoire ──────────→ session, long terme
Transverse : identité, registre, observabilité (OTel), evals
```
Chaque flèche est un **point de contrôle** : c'est là qu'on authentifie, filtre, trace et limite.

---

Pourquoi séparer le cerveau, les mains et la session d'un agent ?
?
C'est l'architecture de **Claude Managed Agents** :
- **Cerveau** : le modèle et son harness, **sans état**
- **Mains** : sandboxes et outils, **provisionnés seulement quand un outil en a besoin**
- **Session** : un **journal d'événements en ajout seul**, stocké hors de la fenêtre de contexte

Ce qu'on y gagne :
- **Reprise** : un harness qui plante est relancé et reconstruit l'état depuis le journal ; une sandbox qui plante devient une simple erreur d'outil
- **Sécurité** : les jetons ne sont **jamais accessibles depuis la sandbox** où tourne le code généré
- **Latence** : plus de conteneur démarré à chaque session. Anthropic mesure un TTFT p50 réduit d'environ **60 %** et un p95 de plus de **90 %**

---

Comment rendre fiable un agent qui tourne pendant des heures ?
?
Avec l'**exécution durable** ([[41-automatisation-code-nocode|durable execution]]) :
- **Checkpoint à chaque étape**, reprise au dernier point après un crash ([[45-langgraph-production|LangGraph]], Temporal)
- **Idempotence** des appels d'outils (clé d'idempotence), pour qu'un rejeu ne paie pas deux fois
- **Timeouts et retries** avec backoff
- **Compensation** (pattern saga) pour défaire une action quand une étape suivante échoue
- **Opérations longues asynchrones**, suivies par polling (extension **Tasks** de MCP)

---

Comment isoler les clients et les équipes sur une plateforme partagée ?
?
- **Calcul** : une **microVM par session** (Firecracker) ou gVisor ou Kata, plutôt que des conteneurs qui partagent le noyau
- **Données** : mémoire, fichiers et index **cloisonnés** par client et par utilisateur
- **Caches** : pas de partage du prefix cache entre clients ([[66-prefix-caching-radix-attention|canal auxiliaire]])
- **Secrets** propres à chaque client, **réseau sortant** limité à une liste blanche
- **Quotas** par client contre l'effet voisin bruyant

---

Agent délégué ou agent autonome : comment gérer son identité ?
?
- **Délégué** : il agit **pour un utilisateur**. Par **échange de jetons** OAuth (RFC 8693), il obtient un jeton limité aux **droits de l'utilisateur** et qui porte aussi l'identité de l'agent : l'audit sait qui a demandé et qui a agi
- **Autonome** : il agit **en son nom propre**, avec sa propre identité et ses propres droits (ex. les « autopilots » de Microsoft, qui ont un compte d'utilisateur Entra), et un **humain propriétaire** responsable

Dans les deux cas : jetons **courts et limités**, stockés dans un **coffre**, injectés par la plateforme, **jamais dans le contexte ni dans la sandbox**.

---

Quels standards émergent pour l'identité des agents ?
?
- **Enterprise-Managed Authorization** de MCP (stable depuis juin 2026) : l'**IdP de l'entreprise** décide quels clients MCP accèdent à quels serveurs pour quels utilisateurs, sans écran de consentement par utilisateur (mécanisme ID-JAG, dit **Cross-App Access**)
- **Client ID Metadata Documents** : remplacent l'enregistrement dynamique des clients dans la spec MCP 2026-07-28
- **SPIFFE / WIMSE** : identités de workload attestées, proposées pour les agents par un brouillon de l'IETF (2026)
- **Identités d'agents** dans les annuaires (**Entra Agent ID**), avec revues d'accès et **attestation par le propriétaire**

---

Pourquoi un moteur de politiques déterministe en plus des instructions du prompt ?
?
Un prompt **n'est pas une barrière** : une injection peut le contourner. Les politiques sont évaluées **hors du modèle**, par la gateway, **avant chaque appel d'outil** : quel outil, quels paramètres, sous quelles conditions (montant maximal, rôle de l'utilisateur, horaires), avec ou sans approbation humaine. On part d'un **refus par défaut** et **chaque décision est journalisée**.

Langages : **Cedar** (AgentCore Policy, disponible depuis mars 2026) ou **OPA/Rego**. Complète les guardrails de contenu ([[101-securite-llm-guardrails|sécurité LLM]]).

---

Comment organiser le human-in-the-loop à grande échelle ?
?
On classe les actions par **niveau de risque** :
- **Lecture** : automatique
- **Écriture réversible** : automatique, avec audit
- **Action irréversible, financière ou communication externe** : **approbation humaine**

L'approbation est **asynchrone** (notification, délai d'expiration) et montre **exactement ce qui va se passer** (diff, montant, destinataire). Trop d'approbations produit de la **fatigue** et des validations à l'aveugle, un risque classé par l'OWASP (confiance humain-agent abusée).

---

Que contient le registre des agents et quel est leur cycle de vie ?
?
**Fiche d'un agent** : propriétaire, objectif, modèles, outils et droits, données accessibles, **niveau de risque**, version, statut.

**Cycle de vie** : proposition → revue sécurité et risque → publication → surveillance → **recertification périodique** → retrait (identité désactivée, jetons révoqués).

On inventorie aussi les **agents fantômes**, créés hors du circuit, et on **épingle les versions** des serveurs MCP et des skills approuvés, car ils font partie de la chaîne d'approvisionnement.

---

Quelles sont les menaces du Top 10 OWASP pour les applications agentiques ?
?
Publié en décembre 2025 :
1. **Détournement de l'objectif** de l'agent
2. **Mauvais usage des outils**
3. **Abus d'identité et de privilèges**
4. **Chaîne d'approvisionnement** : outils, serveurs MCP, plugins
5. **Exécution de code inattendue**
6. **Empoisonnement du contexte et de la mémoire**
7. **Communication inter-agents non sécurisée**
8. **Défaillances en cascade**
9. **Confiance humain-agent abusée**
10. **Agents hors de contrôle** (rogue agents)

Voir [[101-securite-llm-guardrails|sécurité LLM]].

---

Comment limiter le rayon d'impact d'un agent qui déraille ?
?
- **Plafonds par run et par jour** : tokens, coût, nombre d'étapes, nombre d'appels d'outils
- **Quotas par outil** et droits minimaux
- **Détection d'anomalies** : boucles, pics d'appels, comportements inhabituels
- **Coupe-circuits** entre agents, contre les défaillances en cascade
- **Kill switch** : désactiver un agent, révoquer son identité ou bloquer un outil **à la gateway**, immédiatement et sans redéployer

---

Quelles traces et quel audit pour la conformité ?
?
Une **trace complète par tâche** (OpenTelemetry, spans d'agent, de modèle et d'outil) qui répond à : **qui** (utilisateur et agent), **a fait quoi**, **sur quelles données**, **avec quelle approbation**, **avec quelle version** de l'agent. Les décisions de politique et les approbations vont dans un **journal d'audit immuable**, avec une durée de rétention définie. Voir [[93-monitoring-inference|monitoring de l'inférence]].

---

Quelles métriques et quels SLO pour un agent ?
?
- **Taux de réussite des tâches**, et **pass^k** : réussir les k essais, une mesure de fiabilité ([[114-reproductibilite-variance|reproductibilité]])
- **Étapes et durée** par tâche
- **Coût par tâche réussie**
- **Taux d'escalade** vers un humain
- **Refus de politique** et **erreurs d'outils**

Le SLO porte sur la **tâche de bout en bout** (réussite et durée), pas seulement sur le TTFT ([[64-metriques-slo-inference|métriques & SLO]]).

---

Comment évaluer et améliorer un agent en continu ?
?
- **Avant déploiement** : simulation avec des utilisateurs synthétiques et des outils virtualisés, datasets de régression issus des traces de production, **eval gate** ([[112-cicd-modeles|CI/CD]])
- **En production** : scoring d'un échantillon de traces (LLM-as-judge), feedback, dérive ([[113-monitoring-drift-feedback|monitoring & drift]])
- **Boucle d'optimisation** : regrouper les échecs par cause, proposer des changements de prompt ou de description d'outil, les valider par **A/B test**

AWS (AgentCore Optimization) et Google (Agent Optimizer) proposent cette boucle en service managé.

---

Comment maîtriser le coût d'une flotte d'agents ?
?
Un agent consomme beaucoup plus qu'un chat : selon Anthropic, **environ 4 fois plus de tokens**, et **environ 15 fois plus** pour un système multi-agents. Les leviers :
- **Attribuer** le coût par agent, tâche et équipe, grâce à l'identité et aux tags ([[122-finops-llm|FinOps]])
- **Budgets par run**
- **Préfixe stable** pour le cache ([[123-caching-agressif|caching]]) et **compaction** du contexte
- **Petits modèles** pour les sous-étapes ([[82-routing-llm|routing]])

La métrique qui décide : le **coût par tâche réussie**, comparé au coût du processus actuel.

---

Que change l'AI Act européen pour une plateforme d'agents ?
?
- **Depuis le 2 août 2026** : obligations de **transparence**. Informer l'utilisateur qu'il échange avec une IA, marquer les contenus générés (délai jusqu'au 2 décembre 2026 pour le marquage des systèmes déjà sur le marché)
- **Systèmes à haut risque** (recrutement, crédit, etc.) : reportés au **2 décembre 2027** par le Digital Omnibus, entré en vigueur le 27 juillet 2026
- **À préparer** : inventaire et **classification du risque** de chaque agent, supervision humaine, journaux, documentation. Le registre de la plateforme sert de base

Cadre de management utile : **ISO/IEC 42001**.

---

Comment limiter le verrouillage par un fournisseur ?
?
Le cas d'école : l'**Agent Builder** d'OpenAI, lancé en octobre 2025, est déprécié en juin 2026 et **ferme le 30 novembre 2026**. Les parades :
- **Logique d'agent en code**, versionnée dans Git, plutôt que dans un builder propriétaire
- **Standards ouverts** : outils en MCP, agents exposés en A2A, traces en OpenTelemetry
- **Modèles derrière une gateway** ([[81-litellm-api-layer|LiteLLM]])
- **Données exportables** : mémoire, traces, datasets d'evals
- **Coût de sortie** évalué dès le choix de la plateforme

---

Quels critères pour choisir sa plateforme d'agents ?
?
- **Écosystème existant** : où sont déjà les données et l'identité (AWS → AgentCore, Microsoft 365 et Entra → Foundry et Agent 365, GCP → Gemini Enterprise Agent Platform)
- **Souveraineté et rétention** : les harness managés **stockent l'état** des sessions (ex. Claude Managed Agents n'est pas éligible au zero data retention)
- **Agents multi-éditeurs** à gouverner, ou un seul
- **Maturité de l'équipe** et volume
- **Coût de sortie**

Le choix fréquent est **hybride** : services managés **modulaires** pour le runtime et les sandboxes, plan de contrôle (registre, politiques, observabilité) aligné sur des standards ouverts.

---

## Connexions
- [[38-plateformes-agents|Plateformes d'agents — Fondamentaux]] — les briques et les offres
- [[36-orchestration-agents|Orchestration multi-agents]] — A2A et coût du multi-agent
- [[33-mcp|MCP]] — autorisation, gateway et registre d'outils
- [[101-securite-llm-guardrails|Sécurité LLM & guardrails]] — injection, excessive agency, guardrails
- [[112-cicd-modeles|CI/CD des modèles]] — eval gate, canary, rollback
- [[113-monitoring-drift-feedback|Monitoring, drift & feedback]] — qualité en production
- [[93-monitoring-inference|Monitoring de l'inférence]] — métriques, traces et alertes
- [[122-finops-llm|FinOps LLM]] — attribution et budgets
- [[45-langgraph-production|LangGraph — Production]] — exécution durable et interruptions
- [[111-mlops-llmops-fondamentaux|MLOps & LLMOps]] — registre, lineage, environnements
- [[00-moc-ai-engineering|MOC AI Engineering]]
