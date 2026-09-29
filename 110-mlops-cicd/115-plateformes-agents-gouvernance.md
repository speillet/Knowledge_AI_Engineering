# Plateformes d'agents — Architecture & gouvernance — Flashcards
Tags: #flashcards #ai-engineering #agents #platform #gouvernance #llm
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.

Pourquoi construire une plateforme d'agents interne plutôt que laisser chaque équipe se débrouiller ?
?
Sans plateforme, chaque équipe réimplémente runtime, identité, accès aux outils, observabilité et contrôles, chacune à sa manière. L'équipe plateforme fournit un **chemin balisé** (paved road) : templates, outils approuvés, mémoire, authentification, traces et evals prêts à l'emploi. Les équipes produit se concentrent sur la logique métier.

L'enjeu est réel : Gartner prévoit que **plus de 40 % des projets agentiques seront annulés d'ici fin 2027**, pour trois raisons (coûts, valeur floue, contrôle des risques insuffisant) qu'une plateforme traite dès le départ.

---

À ne pas confondre : plan de contrôle et plan d'exécution d'une plateforme d'agents ?
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

Dans l'architecture de Claude Managed Agents, que sont le cerveau, les mains et la session ?
?
- **Cerveau** : le modèle et son harness, **sans état**
- **Mains** : sandboxes et outils, **provisionnés seulement quand un outil en a besoin**
- **Session** : un **journal d'événements en ajout seul**, stocké hors de la fenêtre de contexte

---

Que gagne-t-on à séparer le cerveau, les mains et la session d'un agent ?
?
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

Comment un agent délégué obtient-il ses droits sans compte de service ?
?
Par **échange de jetons** OAuth (RFC 8693) : le jeton de l'utilisateur est échangé contre un jeton **limité à ses droits**, qui porte **aussi l'identité de l'agent**. L'audit sait alors **qui a demandé** et **qui a agi**.

Un agent **autonome** a au contraire son propre compte (ex. les « autopilots » de Microsoft, avec un compte d'utilisateur Entra) et un humain propriétaire ([[38-plateformes-agents|délégué ou autonome]]).

---

Où vivent les jetons d'un agent ?
?
Dans un **coffre** géré par la plateforme, qui les **injecte au moment de l'appel d'outil**, **jamais dans le contexte du modèle ni dans la sandbox** : une injection de prompt ne peut pas exfiltrer ce que le modèle ne voit pas.

Les jetons sont **courts** (minutes) et **limités** au périmètre de la tâche, et révoqués au retrait de l'agent.

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

À quoi ressemble une politique Cedar pour un agent de support ?
?
```text
// Cedar : remboursement autorisé sous 100 €, sinon approbation
permit (
  principal in Group::"agents-support",
  action == Action::"rembourser",
  resource is Commande
) when { context.montant <= 100 && resource.owner == context.utilisateur };

forbid (principal, action == Action::"rembourser", resource)
unless { context.approbation_humaine == true } when { context.montant > 100 };
```
Le `permit` ouvre un cas précis, le `forbid` l'emporte toujours sur un `permit`. Le refus par défaut et la journalisation de chaque décision sont ce qui rend la politique **auditable**.

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

Top 10 OWASP agentique : que sont le détournement de l'objectif et les agents hors de contrôle ?
?
Deux des dix risques du Top 10 OWASP des applications agentiques (décembre 2025) :
- **Détournement de l'objectif** (ASI01) : une injection fait poursuivre à l'agent les buts de l'attaquant. Parade : Rule of Two, outils étroits, politiques appliquées hors du modèle ([[103-defenses-agents|architecture défensive]])
- **Agents hors de contrôle** (ASI10) : un agent compromis ou qui dérive continue d'agir sans qu'on s'en aperçoive. Parade : surveillance du comportement, recertification, **kill switch**

---

Top 10 OWASP agentique : que sont le mauvais usage des outils et l'exécution de code inattendue ?
?
- **Mauvais usage des outils** (ASI02) : l'agent utilise un outil légitime de façon dangereuse (suppression, envoi en masse). Parade : validation des arguments, quotas, approbation des actions à risque
- **Exécution de code inattendue** (ASI05) : l'agent génère et lance du code ou des commandes dangereuses. Parade : sandbox isolée, sans secrets, au réseau filtré

---

Top 10 OWASP agentique : que sont l'abus d'identité et la communication inter-agents non sécurisée ?
?
- **Abus d'identité et de privilèges** (ASI03) : l'agent utilise des jetons ou des droits hérités au-delà de son besoin. Parade : droits de l'utilisateur, jetons courts et limités, échange de jetons
- **Communication inter-agents non sécurisée** (ASI07) : messages entre agents usurpés, modifiés ou rejoués. Parade : authentification mutuelle, Agent Cards signées, sorties des autres agents traitées comme non fiables

---

Top 10 OWASP agentique : que sont la chaîne d'approvisionnement et l'empoisonnement du contexte ?
?
- **Chaîne d'approvisionnement** (ASI04) : outils, serveurs MCP, plugins ou skills malveillants ou compromis. Parade : registre interne, versions épinglées, analyse avant autorisation ([[104-securite-mcp-skills|MCP & skills]])
- **Empoisonnement du contexte et de la mémoire** (ASI06) : données récupérées ou mémorisées falsifiées, qui orientent les décisions suivantes. Parade : provenance, politique d'écriture, cloisonnement, purge

---

Top 10 OWASP agentique : que sont les défaillances en cascade et la confiance humain-agent abusée ?
?
- **Défaillances en cascade** (ASI08) : une erreur ou une donnée fausse se propage et s'amplifie d'un agent ou d'un système à l'autre. Parade : coupe-circuits, validation entre les étapes, rayon d'impact limité
- **Confiance humain-agent abusée** (ASI09) : l'agent pousse l'humain à approuver une action dangereuse, par persuasion ou description trompeuse. Parade : afficher les paramètres réels, approbations rares et ciblées

Voir [[102-menaces-agents|menaces & incidents]].

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

Quelles échéances de l'AI Act concernent une plateforme d'agents ?
?
- **Depuis le 2 août 2026** : obligations de **transparence**. Informer l'utilisateur qu'il échange avec une IA, marquer les contenus générés (délai jusqu'au 2 décembre 2026 pour le marquage des systèmes déjà sur le marché)
- **Systèmes à haut risque** (recrutement, crédit, etc.) : reportés au **2 décembre 2027** par le Digital Omnibus, entré en vigueur le 27 juillet 2026

Voir [[155-ai-act|AI Act]].

---

Que préparer pour l'AI Act sur une plateforme d'agents ?
?
- **Inventaire** et **classification du risque** de chaque agent : le registre de la plateforme sert de base
- **Supervision humaine** effective sur les actions à risque
- **Journaux** et **documentation** technique

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

---

Quelle architecture de plateforme d'agents est la plus fréquente ?
?
Une architecture **hybride** : services managés **modulaires** pour le runtime et les sandboxes, plan de contrôle (registre, politiques, observabilité) aligné sur des **standards ouverts** (MCP, A2A, OpenTelemetry). On profite du managé là où il fait gagner du temps, sans y enfermer ce qui coûte cher à migrer.

---

## Mises en situation

Mise en situation : ta direction veut « 50 agents en production d'ici un an ». Tu en as trois aujourd'hui, chacun construit à sa façon. Que proposes-tu ?
?
1. **Poser un chemin balisé** avant de multiplier : runtime, identité, gateway d'outils, traces et evals fournis par défaut
2. **Registre et cycle de vie** : propriétaire, objectif, droits, niveau de risque, recertification
3. **Contrôles par défaut** : moindre privilège, politiques hors du modèle, approbation des actions à risque
4. **Mesurer la valeur agent par agent** : coût par tâche réussie, taux d'escalade, gain réel
5. **Rappeler le risque** : plus de 40 % des projets agentiques sont annulés, faute de valeur claire ou de contrôle des risques

**Piège** : viser un nombre d'agents plutôt que des processus effectivement automatisés.

---

Mise en situation : un agent interne a supprimé des données dans un outil métier hier soir. Le directeur demande ce qui s'est passé et qui est responsable. Que dois-tu pouvoir produire ?
?
1. **La trace complète** : quel utilisateur, quel agent, quelles entrées, quelles actions, avec quelle version
2. **L'identité utilisée** : agent délégué avec les droits de l'utilisateur, ou identité propre de l'agent
3. **Les décisions de politique** : qu'est-ce qui a été autorisé, par quelle règle, avec ou sans approbation
4. **La fiche de l'agent** : propriétaire responsable, périmètre déclaré, niveau de risque
5. **Les mesures immédiates** : kill switch, révocation des jetons, correction des actions ([[105-devsecops-ia-agentique|réponse à incident]])

**Piège** : découvrir que les actions de l'agent sont journalisées sous un compte de service commun, sans lien avec l'utilisateur.

---

Mise en situation : le fournisseur de ta plateforme d'agents annonce l'arrêt d'un service dans six mois. Comment évalues-tu l'impact ?
?
1. **Inventorier** ce qui en dépend : agents, outils, mémoires, traces, jeux d'evals
2. **Séparer** ce qui est portable (logique d'agent en code, outils MCP, traces OpenTelemetry) de ce qui est propriétaire
3. **Vérifier l'export** des données : mémoire, journaux de session, datasets
4. **Chiffrer le coût de sortie** : réécriture, migration, revalidation par les evals
5. **En tirer une règle** : évaluer ce coût **avant** de choisir une plateforme, pas au moment de l'annonce

**Piège** : avoir construit la logique métier dans un builder visuel dont rien ne s'exporte.

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
- [[103-defenses-agents|Sécurité des agents — Architecture défensive]] — les contrôles de sécurité en détail
- [[105-devsecops-ia-agentique|DevSecOps pour l'IA agentique]] — détection et réponse aux incidents
- [[155-ai-act|AI Act]] — classification des risques et calendrier
- [[00-moc-ai-engineering|MOC AI Engineering]]
