# Plateformes d'agents — Architecture & gouvernance — Flashcards
Tags: #flashcards #ai-engineering #agents #platform #gouvernance #llm
Vérifié le : 25 septembre 2026 — date globale conservée ; revue ciblée du 13 novembre 2026 détaillée dans les Sources.
<!-- summary: plateforme interne (paved road), plan de contrôle et plan d'exécution, architecture de référence, séparation cerveau, mains et session, exécution durable, isolation multi-tenant, échange de jetons pour l'agent délégué, jetons hors du contexte, standards d'identité, moteur de politiques, human-in-the-loop, registre et cycle de vie, Top 10 OWASP agentique, rayon d'impact et kill switch, audit, SLO, evals continues, coûts, AI Act, lock-in, critères de choix, révocation d'une délégation active, politiques versionnées, retrait vérifié, responsabilités métier et exploitation, dérogations temporaires, révocation de cache, accès exceptionnel. -->


Pourquoi construire une plateforme d'agents interne plutôt que laisser chaque équipe se débrouiller ? <!--anki:736971307067364a5850-->
?
Sans plateforme, chaque équipe réimplémente runtime, identité, accès aux outils, observabilité et contrôles, chacune à sa manière. L'équipe plateforme fournit un **chemin balisé** (paved road) : templates, outils approuvés, mémoire, authentification, traces et evals prêts à l'emploi. Les équipes produit se concentrent sur la logique métier.

La plateforme est utile si elle réduit réellement le délai de livraison et les erreurs répétées. Commencer par les besoins communs observés, avec contrats et responsabilités clairs, puis mesurer adoption, incidents et coût d'exploitation. Un socle trop rigide peut pousser les équipes à le contourner ; prévoir une procédure d'extension et des exceptions tracées.

---

Pour quelles raisons Gartner prévoit-il l'annulation de nombreux projets agentiques d'ici fin 2027, et qu'en retenir ? <!--anki:6233353432366564333864353439316662376461306137396636323031326531-->
?
**Plus de 40 %**, pour trois raisons : des **coûts** qui dérapent, une **valeur métier** floue et un **contrôle des risques** insuffisant. Ce sont les sujets qu'une plateforme interne traite dès le départ.

C'est une **prévision publiée**, pas une mesure d'échecs déjà observés ni une probabilité applicable à chaque projet. Le point à retenir est d'exiger une valeur mesurable, un coût par tâche réussie et un responsable des risques. Une plateforme peut aider ces contrôles, mais sa seule présence ne garantit pas la réussite d'un projet.

---

À ne pas confondre : plan de contrôle et plan d'exécution d'une plateforme d'agents ? <!--anki:4b303c326a415821624f-->
?
Le **plan de contrôle** gère inventaire, identités, politiques, versions et décisions de déploiement ; le **plan d'exécution** traite les sessions, appels de modèles et outils, mémoire et traces.

Il s'agit de responsabilités, pas nécessairement de deux produits : une offre peut couvrir les deux. Chez Microsoft, Foundry Agent Service fournit l'exécution et Agent 365 la gouvernance organisationnelle des agents intégrés ou découverts. Agent 365 est disponible commercialement depuis le 1er mai 2026, avec conditions de licence et d'intégration. Ne pas en déduire une visibilité ou un contrôle automatique sur tout agent inconnu du système ; tester découverte, droits et couverture réelle.

---

À quoi ressemble l'architecture de référence d'une plateforme d'agents ? <!--anki:6a53783776536d3a607e-->
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

Les composants peuvent être regroupés dans un petit système, mais leurs responsabilités doivent rester explicites. L'identité accompagne les appels jusqu'aux outils et à la mémoire. Par exemple, une autorisation de conversation ne vaut pas autorisation de remboursement : le contrôle effectif se fait aussi à la frontière de l'action métier.

---

Dans l'architecture de Claude Managed Agents, que sont le cerveau, les mains et la session ? <!--anki:4b67397543574d597878-->
?
- **Cerveau** : le modèle et son harness, **sans état**
- **Mains** : sandboxes et outils, **provisionnés seulement quand un outil en a besoin**
- **Session** : un **journal d'événements en ajout seul**, stocké hors de la fenêtre de contexte

Cette séparation permet de recréer un processus de calcul à partir d'un historique durable, et de n'allouer un environnement d'exécution qu'au moment utile. Elle ne rend pas les effets externes réversibles. Si une écriture métier réussit avant une panne, la reprise doit consulter une preuve de cette écriture ou utiliser une clé d'idempotence.

---

Que gagne-t-on à séparer le cerveau, les mains et la session d'un agent ? <!--anki:422e7d317c6e3e4b662d-->
?
Séparer **calcul, environnement d'outils et historique durable** permet d'allouer et restaurer ces composants selon des cycles différents. Un worker peut repartir d'un état conservé ; une sandbox peut être renouvelée sans perdre tout le dossier.

Les bénéfices de latence et de coût dépendent de ce qui est effectivement préchauffé, transféré ou reconstruit. La séparation peut faciliter l'isolement des secrets, mais leur inaccessibilité n'est pas automatique : vérifier montages, proxy et droits des outils. Une panne après effet externe exige toujours idempotence ou réconciliation. Les gains mesurés par un fournisseur ne constituent pas une borne applicable à toute architecture qui reprend ces noms.

---

Comment rendre fiable un agent qui tourne pendant des heures ? <!--anki:6c415f6f4a3457375e3a-->
?
Avec l'**exécution durable** ([[41-automatisation-code-nocode|durable execution]]) :
- **Checkpoint à chaque étape**, reprise au dernier point après un crash ([[45-langgraph-production|LangGraph]], Temporal)
- **Idempotence** des appels d'outils (clé d'idempotence), pour qu'un rejeu ne paie pas deux fois
- **Timeouts et retries** avec backoff
- **Compensation** (pattern saga) pour défaire une action quand une étape suivante échoue
- **Opérations longues asynchrones**, suivies par polling (extension **Tasks** de MCP)

---

Comment isoler les clients et les équipes sur une plateforme partagée ? <!--anki:42344a3b424b56677953-->
?
- **Calcul** : une **microVM par session** (Firecracker) ou gVisor ou Kata, plutôt que des conteneurs qui partagent le noyau
- **Données** : mémoire, fichiers et index **cloisonnés** par client et par utilisateur
- **Caches** : pas de partage du prefix cache entre clients ([[66-prefix-caching-radix-attention|canal auxiliaire]])
- **Secrets** propres à chaque client, **réseau sortant** limité à une liste blanche
- **Quotas** par client contre l'effet voisin bruyant

---

Comment un agent délégué obtient-il ses droits sans compte de service ? <!--anki:7859473c4b2c3479314d-->
?
Un mécanisme d'**échange de jetons**, comme OAuth Token Exchange, peut permettre d'obtenir un jeton pour une audience et un périmètre précis à partir d'une identité existante. La représentation du sujet et de l'acteur dépend du profil et du serveur d'autorisation.

Le protocole n'accorde pas automatiquement tous les droits de l'utilisateur, ni une réduction correcte par simple présence de deux identités. Définir audience, scopes, durée et règles de délégation ; contrôler ensuite chaque action et conserver le lien demandeur/agent dans l'audit. Un agent autonome utilise une identité de service encadrée, avec un responsable, sans mandat utilisateur implicite.

---

Où vivent les jetons d'un agent ? <!--anki:4630305e382b7b6f4121-->
?
Une architecture privilégiée conserve les **credentials dans un coffre ou un proxy d'outils**, qui authentifie l'action et injecte le secret au dernier moment. Le modèle reçoit un résultat métier plutôt que le jeton brut.

Utiliser des droits minimaux, une durée limitée et une révocation adaptée. Ne pas exposer le secret dans contexte, logs ou fichiers accessibles à l'agent lorsque l'architecture l'évite. Cela empêche certaines lectures directes, mais pas l'abus d'un outil autorisé : une injection peut encore demander une consultation ou un envoi indu. Le proxy doit vérifier identité, arguments et destination.

---

Quels standards émergent pour l'identité des agents ? <!--anki:6c754254776647366b4d-->
?
Distinguer **protocole, extension, projet de standard et produit** :
- **MCP Enterprise-Managed Authorization** : extension stable, activée explicitement ; l'IdP centralise les politiques via ID-JAG. Le support des participants reste nécessaire.
- **Client ID Metadata Documents**, recommandés dans MCP 2026-07-28 ; l'enregistrement dynamique est déprécié mais conservé pour compatibilité, avec pré-enregistrement possible.
- **SPIFFE** : identité de workload ; **AIMS/WIMSE**, notamment `draft-ietf-wimse-aims-01`, reste un Internet-Draft, pas un RFC final.
- **Entra Agent ID** : identités d'agents et cycle de vie dans l'annuaire.

Identifier révision, support et politique effective. Une identité attestée n'autorise pas, seule, une action métier ni une délégation utilisateur.

---

Pourquoi un moteur de politiques déterministe en plus des instructions du prompt ? <!--anki:72532c345f666b242154-->
?
Un prompt **n'est pas une barrière** : une injection peut le contourner. Les politiques sont évaluées **hors du modèle**, par la gateway, **avant chaque appel d'outil** : quel outil, quels paramètres, sous quelles conditions (montant maximal, rôle de l'utilisateur, horaires), avec ou sans approbation humaine. On part d'un **refus par défaut** et **chaque décision est journalisée**.

Langages : **Cedar** (AgentCore Policy, disponible depuis mars 2026) ou **OPA/Rego**. Complète les guardrails de contenu ([[101-securite-llm-guardrails|sécurité LLM]]).

---

À quoi ressemble une politique Cedar pour un agent de support ? <!--anki:4b7c5f4a345a5a6a366a-->
?
Exemple avec **montant entier en centimes**, identité et approbation fournies par un contexte de confiance :
```text
permit (
  principal in Group::"agents-support",
  action == Action::"rembourser",
  resource is Commande
) when {
  resource.owner == context.utilisateur &&
  context.montant_centimes >= 0 &&
  (context.montant_centimes <= 10000 ||
   context.approbation_humaine == true)
};
```
Sans `permit` applicable, Cedar refuse ; un `forbid` applicable prime sur les autorisations. Le schéma doit définir ces entités et attributs. Valider aussi le solde remboursable et l'idempotence dans le service métier. **L'agent ne renseigne pas lui-même son approbation** : la politique serait sinon contournable.

---

Comment organiser le human-in-the-loop à grande échelle ? <!--anki:65425e237c397e475a58-->
?
Classer les actions selon **conséquences, données et réversibilité réelle**, puis choisir automatisation, contrôle déterministe et approbation. Une lecture de secret peut être sensible ; une écriture réversible peut déjà avoir divulgué une information.

Pour une approbation, montrer arguments et destination exacts, identité, portée et expiration. Lier l'accord à la proposition versionnée puis revérifier droits et préconditions avant l'effet. Mesurer charge et erreurs de revue : multiplier les demandes peut réduire l'attention. Certaines actions ne deviennent pas acceptables par un clic humain ; les interdictions et limites métier restent appliquées par le système, indépendamment du choix du modèle.

---

Que contient le registre des agents et quel est leur cycle de vie ? <!--anki:4a405e614e7c51417737-->
?
**Fiche d'un agent** : propriétaire, objectif, modèles, outils et droits, données accessibles, **niveau de risque**, version, statut.

**Cycle de vie** : proposition → revue sécurité et risque → publication → surveillance → **recertification périodique** → retrait (identité désactivée, jetons révoqués).

On inventorie aussi les **agents fantômes**, créés hors du circuit, et on **épingle les versions** des serveurs MCP et des skills approuvés, car ils font partie de la chaîne d'approvisionnement.

---

Top 10 OWASP agentique : que sont le détournement de l'objectif et les agents hors de contrôle ? <!--anki:4826364a4d7941746038-->
?
Deux risques de l'édition **Top 10 for Agentic Applications 2026**, publiée le 9 décembre 2025 :
- **Détournement de l'objectif** (ASI01) : une injection fait poursuivre les buts de l'attaquant. Réduire les privilèges et appliquer les politiques hors du modèle.
- **Agents hors de contrôle** (ASI10) : un agent compromis ou déviant continue d'agir. Surveiller comportement, identités, tâches admises et moyens d'arrêt.

Ne pas confondre ce référentiel **ASI** avec le Top 10 des applications LLM, dont l'édition 2026 possède d'autres identifiants. Associer la version du référentiel aux scénarios et contrôles testés ; ni sa publication ni une checklist remplie ne démontrent la sécurité du produit.

---

Top 10 OWASP agentique : que sont le mauvais usage des outils et l'exécution de code inattendue ? <!--anki:36517a694450415267-->
?
- **Mauvais usage des outils** (ASI02) : l'agent utilise un outil légitime de façon dangereuse (suppression, envoi en masse). Parade : validation des arguments, quotas, approbation des actions à risque
- **Exécution de code inattendue** (ASI05) : l'agent génère et lance du code ou des commandes dangereuses. Parade : sandbox isolée, sans secrets, au réseau filtré

La séparation aide au diagnostic : une API autorisée appelée sur la mauvaise ressource relève de l'autorisation métier ; un processus lancé hors confinement relève du contrôle d'exécution. Tester les deux frontières, car une sandbox ne valide pas les arguments d'une API distante.

---

Top 10 OWASP agentique : que sont l'abus d'identité et la communication inter-agents non sécurisée ? <!--anki:773b325725532a2d5d67-->
?
- **Abus d'identité et de privilèges** (ASI03) : l'agent utilise des jetons ou des droits hérités au-delà de son besoin. Parade : droits de l'utilisateur, jetons courts et limités, échange de jetons
- **Communication inter-agents non sécurisée** (ASI07) : messages entre agents usurpés, modifiés ou rejoués. Parade : authentification mutuelle, Agent Cards signées, sorties des autres agents traitées comme non fiables

---

Top 10 OWASP agentique : que sont la chaîne d'approvisionnement et l'empoisonnement du contexte ? <!--anki:44333b24796c634c6648-->
?
- **Chaîne d'approvisionnement** (ASI04) : outils, serveurs MCP, plugins ou skills malveillants ou compromis. Parade : registre interne, versions épinglées, analyse avant autorisation ([[104-securite-mcp-skills|MCP & skills]])
- **Empoisonnement du contexte et de la mémoire** (ASI06) : données récupérées ou mémorisées falsifiées, qui orientent les décisions suivantes. Parade : provenance, politique d'écriture, cloisonnement, purge

Une version épinglée garantit une identité d'artefact, pas son innocuité. Prévoir retrait du registre, révocation des accès et recherche des exécutions ayant consommé une version compromise ; la traçabilité rend cette réponse possible.

---

Top 10 OWASP agentique : que sont les défaillances en cascade et la confiance humain-agent abusée ? <!--anki:704d472e495a65307153-->
?
- **Défaillances en cascade** (ASI08) : une erreur ou une donnée fausse se propage et s'amplifie d'un agent ou d'un système à l'autre. Parade : coupe-circuits, validation entre les étapes, rayon d'impact limité
- **Confiance humain-agent abusée** (ASI09) : l'agent pousse l'humain à approuver une action dangereuse, par persuasion ou description trompeuse. Parade : afficher les paramètres réels, approbations rares et ciblées

Voir [[102-menaces-agents|menaces & incidents]].

---

Comment limiter le rayon d'impact d'un agent qui déraille ? <!--anki:482d267241512f7a7832-->
?
Limiter **droits, destinations et travail admis**, avec plafonds d'appels, durée, coût et concurrence. Un outil étroit et une politique externe au modèle bornent les actions même si les instructions sont détournées.

Prévoir l'arrêt de nouvelles demandes, la révocation adaptée des credentials et le blocage d'une route ou d'un outil. Un kill switch ne retire pas automatiquement un message envoyé ni une opération déjà acceptée ailleurs. Tester délais de propagation, tâches en vol et réconciliation après arrêt. Les compteurs et anomalies aident au déclenchement ; la réduction du rayon d'impact doit reposer aussi sur les permissions effectives et les frontières techniques.

---

Quelles traces et quel audit pour la conformité ? <!--anki:74515d325a734c793226-->
?
Distinguer **trace de diagnostic** et **preuve d'audit** : relier identité, tâche, versions, décisions de politique, approbation, action et résultat, sans recopier inutilement les données sensibles ([[93-monitoring-inference|monitoring]]).

Exemple : un span dit « outil appelé », mais le journal d'audit doit permettre de retrouver la proposition approuvée et l'identifiant de l'opération externe. Les deux se relient par corrélation.

Protéger le journal contre les modifications non autorisées, vérifier sa couverture et définir rétention/effacement compatibles avec les obligations. « Immuable » ne signifie pas conserver toutes les données pour toujours. Tester la panne du collecteur et prévoir tampon durable ou refus explicite selon la criticité.

---

Quelles métriques et quels SLO pour un agent ? <!--anki:4b6c28432b555a68485f-->
?
- **Taux de réussite des tâches**, et **pass^k** : réussir les k essais, une mesure de fiabilité ([[114-reproductibilite-variance|reproductibilité]])
- **Étapes et durée** par tâche
- **Coût par tâche réussie**
- **Taux d'escalade** vers un humain
- **Refus de politique** et **erreurs d'outils**

Le SLO porte sur la **tâche de bout en bout** (réussite et durée), pas seulement sur le TTFT ([[64-metriques-slo-inference|métriques & SLO]]).

---

Comment évaluer et améliorer un agent en continu ? <!--anki:71255944386074307b6c-->
?
Organiser une **boucle de changement contrôlée** :
- Avant déploiement : cas représentatifs, outils simulés, régressions et critères de promotion versionnés.
- En production : traces, échantillons évalués, couverture, retours et issues métier suffisamment mûres.
- Optimisation : analyser les causes, proposer prompt ou description d'outil, puis valider la variante indépendamment.

AgentCore documente recommandations, bundles et A/B tests ; Google présente Agent Optimizer pour suggérer des améliorations à partir des échecs. Vérifier disponibilité, région et prérequis de chaque fonction, plutôt que déduire son statut de celui de toute la plateforme. Une recommandation automatique n'est ni une preuve de gain, ni une autorisation de promotion.

---

Comment maîtriser le coût d'une flotte d'agents ? <!--anki:4a5a787e4c6044325e53-->
?
Quatre leviers :
- **Attribuer** le coût par agent, tâche et équipe, grâce à l'identité et aux tags ([[122-finops-llm|FinOps]])
- **Budgets par run**
- **Préfixe stable** pour le cache ([[123-caching-agressif|caching]]) et **compaction** du contexte
- **Petits modèles** pour les sous-étapes ([[82-routing-llm|routing]])

La métrique qui décide : le **coût par tâche réussie**, comparé au coût du processus actuel.

Inclure les tentatives échouées et les appels encore en vol dans l'enveloppe budgétaire. Segmenter les coûts par résultat : une baisse du prix par appel peut cacher davantage de tours ou de reprises.

---

Que préparer pour l'AI Act sur une plateforme d'agents ? <!--anki:764d316c7c5548246a50-->
?
- **Inventaire** et **classification du risque** de chaque agent : le registre de la plateforme sert de base
- **Supervision humaine** effective sur les actions à risque
- **Journaux** et **documentation** technique

Cadre de management utile : **ISO/IEC 42001** ; calendrier et obligations dans la [[155-ai-act|fiche AI Act]].

La qualification dépend de la **finalité du système et du rôle de l'organisation**, pas du seul usage d'un agent. Relier chaque cas d'usage aux responsables, aux preuves disponibles et aux obligations effectivement applicables. Un registre ou une certification de management ne démontre pas à lui seul la conformité de chaque application ; faire valider le périmètre et les échéances.

---

Comment limiter le verrouillage par un fournisseur ? <!--anki:754262562e752d547735-->
?
Identifier dès le choix d'une plateforme **ce qui coûte à déplacer** : logique, état, politiques, événements, données, observabilité et comportement des outils. Un protocole ouvert facilite une interface sans rendre portables tous les checkpoints ou formats internes.

Versionner les contrats et garder une voie d'export documentée. Faire un essai sur un dossier représentatif : reconstruire son état utile et reprendre le parcours sur une autre implémentation. Mesurer travail, données perdues et revalidation nécessaire. Prévoir les dépréciations et la rétention des preuves. Une gateway seule n'efface pas les différences de modèles, d'authentification ou de fonctions propres à un service.

---

Quels critères pour choisir sa plateforme d'agents ? <!--anki:7a642525262b4e577b43-->
?
Examiner **écosystème, données, compatibilité et exploitation** :
- Intégration aux données, identités et outils existants.
- Localisation et rétention des sessions, traces, fichiers et appels de modèles.
- Agents et protocoles effectivement pris en charge.
- Capacité de l'équipe à exploiter et reprendre le service.
- Coût par tâche utile et coût de sortie testé.

Exemple : le **Managed Agents hébergé par Anthropic** n'est pas éligible au ZDR, même avec sandboxes auto-hébergées. Dans le service entièrement auto-hébergé, accessible sur demande, l'organisation conserve les sessions ; les appels de modèles suivent leur contrat fournisseur. Auto-héberger la sandbox, le service ou le modèle représente trois périmètres différents.

---

Quelle architecture de plateforme d'agents est la plus fréquente ? <!--anki:7a6664363e28693c4c29-->
?
Sans **population et mesure de référence**, on ne peut pas établir ici une architecture la plus fréquente. Une combinaison de services managés et de contrôles internes constitue une option à évaluer, pas une statistique d'adoption.

On peut confier calcul ou sandboxes à un service tout en gardant identité, politiques et métadonnées sous des contrats maîtrisés. Tester échanges d'événements, export d'état, reprise et retrait avant de considérer cette combinaison comme portable. Comparer au besoin réel : autonomie des équipes, contraintes de données, capacité opérationnelle et coût de sortie. La popularité supposée n'est ni une preuve de compatibilité ni un critère suffisant de choix.

---

Pourquoi une plateforme d'agents doit-elle prévoir la révocation d'une délégation pendant un run actif ? <!--anki:3535646463323738376438373436303061363636343138396164646562666265-->
?
Un **run long** peut conserver un droit qui n'est plus valide : utilisateur désactivé, mandat retiré ou politique modifiée. Vérifier seulement au lancement laisse une fenêtre d'action indue.

Associer chaque effet à une identité et un mandat, utiliser des credentials à durée limitée et revérifier les autorisations aux frontières sensibles. Prévoir suspension ou arrêt des runs concernés et invalidation des jetons selon le mécanisme d'identité. Tester une révocation entre deux étapes. Un kill switch du worker ne supprime pas les opérations déjà confiées à un service externe.

---

Pourquoi associer la version de politique aux preuves d'une release agentique ? <!--anki:3064616336353863643238663463323439656438646134643839386565396461-->
?
Une **politique d'autorisation** ou un plafond peut changer le comportement sans modifier modèle ni prompt. Une évaluation faite avec des outils libres ne valide pas automatiquement la même tâche avec approbation ou refus supplémentaires.

Associer politique, identité d'exécution et environnement aux rapports de test. Vérifier les actions permises comme interdites, puis mesurer leur effet sur réussite et délai. Une approbation d'ancienne version peut devoir être renouvelée selon le changement. La politique reste vérifiée au moment de l'action ; la tracer n'autorise pas à conserver indéfiniment des droits qui ont été révoqués depuis l'évaluation.

---

Comment vérifier qu'un agent retiré ne peut plus accepter de travail ? <!--anki:3662353336306432303361333466643038663431383833386461393832656233-->
?
Le **retrait** comprend admission, identités, tâches en cours et ressources dérivées. Désactiver seulement sa page dans un catalogue peut laisser un endpoint, un cron ou une file active.

Inventorier ces chemins, arrêter les nouvelles soumissions, appliquer les révocations et décider du sort des runs existants. Tester un appel direct et une reprise avec les anciens identifiants. Vérifier effets externes encore incertains, puis conservation ou effacement des données selon leur contrat. Garder les preuves nécessaires à l'audit sans garder les privilèges. La fin administrative du projet n'est pas la preuve technique de son arrêt effectif.

---

Pourquoi distinguer propriétaire métier et responsable d'exploitation d'un système IA ? <!--anki:6336316664393635303835303435633038346437386638363966303863376666-->
?
Le **propriétaire métier** fixe l'objectif et les conséquences acceptables ; le **responsable d'exploitation** maintient le service et coordonne la réponse opérationnelle. Les mêmes personnes peuvent cumuler les rôles, mais leurs obligations doivent rester explicites.

Définir qui décide d'une dégradation, autorise une promotion, finance la fiabilité et répond à une alerte de qualité. Prévoir un remplaçant et l'accès aux preuves nécessaires. Un nom dans le registre ne suffit pas si personne n'a capacité d'arrêter l'effet dangereux ou d'arbitrer le retour au service. Tester cette organisation lors d'un exercice d'incident représentatif.

---

Comment encadrer une exception temporaire aux standards de la plateforme IA ? <!--anki:3539363066646263363437393432623139636438656564663530313131613430-->
?
Une **exception** doit identifier besoin, périmètre, propriétaire, contrôles compensatoires, échéance et condition de sortie. Elle permet une dérogation visible plutôt qu'un service parallèle oublié.

Relier la décision à la release et tester les garanties réellement conservées : droits, données, traces et reprise. À expiration, réexaminer explicitement ou retirer l'usage selon la politique ; ne pas transformer le silence en prolongation. Mesurer les exceptions récurrentes : elles peuvent révéler un socle inadapté et motiver une évolution commune. L'automatisation peut signaler ou appliquer les limites prévues, sans inventer une autorisation que les responsables n'ont pas donnée.

---

Pourquoi les caches de décision d'autorisation doivent-ils faire partie du plan de révocation d'une plateforme d'agents ? <!--anki:3837613630353336616237353432666561323838643962653331376138643235-->
?
Une décision « autorisé » conservée trop longtemps peut **survivre au retrait d'un droit**. Les workers et gateways peuvent continuer à accepter des actions sur cette base.

Définir portée, durée et invalidation du cache selon le risque. Pour une écriture sensible, vérifier les conditions courantes au service métier. Tester un retrait pendant une tâche longue. La politique centrale correcte ne suffit pas si ses copies restent périmées.

---

## Mises en situation

Mise en situation : ta direction veut « 50 agents en production d'ici un an ». Tu en as trois aujourd'hui, chacun construit à sa façon. Que proposes-tu ? <!--anki:48635f77536c646d5f48-->
?
1. **Clarifier les résultats métier** attendus et mesurer la baseline, au-delà du nombre d'agents.
2. **Établir un chemin balisé** pour identité, outils, exécution, traces et évaluations, à partir des besoins déjà observés.
3. **Nommer les responsables** du comportement, de l'exploitation et des décisions de risque.
4. **Livrer progressivement** avec coûts par tâche, contrôles d'effets et reprise testée.
5. **Réexaminer la valeur** avant chaque extension ; une prévision sectorielle ne remplace pas les preuves du projet.

**Piège** : présenter la prévision Gartner d'annulations d'ici 2027 comme un taux déjà observé ou une probabilité attachée à chaque agent, puis choisir une plateforme sur ce seul chiffre.

---

Mise en situation : un agent interne a supprimé des données dans un outil métier hier soir. Le directeur demande ce qui s'est passé et qui est responsable. Que dois-tu pouvoir produire ? <!--anki:71514c53763e61336077-->
?
1. **La trace complète** : quel utilisateur, quel agent, quelles entrées, quelles actions, avec quelle version
2. **L'identité utilisée** : agent délégué avec les droits de l'utilisateur, ou identité propre de l'agent
3. **Les décisions de politique** : qu'est-ce qui a été autorisé, par quelle règle, avec ou sans approbation
4. **La fiche de l'agent** : propriétaire responsable, périmètre déclaré, niveau de risque
5. **Les mesures immédiates** : kill switch, révocation des jetons, correction des actions ([[105-devsecops-ia-agentique|réponse à incident]])

**Piège** : découvrir que les actions de l'agent sont journalisées sous un compte de service commun, sans lien avec l'utilisateur.

---

Mise en situation : le fournisseur de ta plateforme d'agents annonce l'arrêt d'un service dans six mois. Comment évalues-tu l'impact ? <!--anki:432b3b67705d31754a72-->
?
1. **Inventorier** ce qui en dépend : agents, outils, mémoires, traces, jeux d'evals
2. **Séparer** ce qui est portable (logique d'agent en code, outils MCP, traces OpenTelemetry) de ce qui est propriétaire
3. **Vérifier l'export** des données : mémoire, journaux de session, datasets
4. **Chiffrer le coût de sortie** : réécriture, migration, revalidation par les evals
5. **En tirer une règle** : évaluer ce coût **avant** de choisir une plateforme, pas au moment de l'annonce

**Piège** : avoir construit la logique métier dans un builder visuel dont rien ne s'exporte.

---

## Sources

- [Cedar — syntaxe des politiques](https://docs.cedarpolicy.com/policies/syntax-policy.html)

- [Anthropic — consommation observée dans son système de recherche multi-agents](https://www.anthropic.com/engineering/multi-agent-research-system)

- [AWS — composants de Bedrock AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html)
- [NIST — AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)

- [RFC 8693 — OAuth 2.0 Token Exchange](https://www.rfc-editor.org/rfc/rfc8693.html) — sujet, acteur et politique d’émission des jetons.
- [Gartner, 25 juin 2025 — prévision d’annulations pour fin 2027](https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027) — prévision, pas taux déjà observé.

Revue ciblée du 13 novembre 2026 : produits, identité, rétention et référentiels.

- [Microsoft Learn — Agent 365, disponibilité et prérequis](https://learn.microsoft.com/en-us/microsoft-agent-365/overview)
- [MCP 2026-07-28 — enregistrement des clients](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/client-registration) — mécanisme dynamique déprécié, conservé pour compatibilité.
- [MCP — extension Enterprise-Managed Authorization](https://modelcontextprotocol.io/extensions/auth/enterprise-managed-authorization) — support explicite et flux ID-JAG.
- [IETF — AIMS, draft-ietf-wimse-aims-01 du 2 novembre 2026](https://datatracker.ietf.org/doc/html/draft-ietf-wimse-aims-01) — document de travail, pas RFC final.
- [Microsoft Learn — identités Entra Agent ID](https://learn.microsoft.com/en-us/entra/agent-id/agent-identities)
- [Anthropic — séparation du cerveau, des outils et de la session](https://www.anthropic.com/research/managed-agents)
- [Claude Platform — Managed Agents hébergé et rétention](https://platform.claude.com/docs/en/managed-agents/overview)
- [Claude Platform — données et accès du service entièrement auto-hébergé](https://platform.claude.com/docs/en/managed-agents/self-hosted-data-and-access) — accès sur demande ; distinct des seules sandboxes auto-hébergées.
- [AWS — notes de version AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/release-notes.html) — disponibilité des fonctions, à distinguer des annonces de preview historiques.
- [AWS — recommandations, bundles et A/B tests](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/optimization.html)
- [Google Cloud — Agent Platform et Agent Optimizer](https://cloud.google.com/blog/products/ai-machine-learning/introducing-gemini-enterprise-agent-platform/)
- [OWASP — Top 10 agentique 2026, publication du 9 décembre 2025](https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/)

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
- [[85-carte-protocoles-agentiques|Carte des protocoles]] — les standards ouverts d'une plateforme
- [[147-leadership-technique-ia|Leadership technique]] — standards d'équipe et décisions
- [[35-context-engineering|Context engineering]] — ce que l'agent a sous les yeux à chaque tour
- [[44-langgraph-fondamentaux|LangGraph]] — graphes d'états pour agents et workflows
- [[84-streaming-integration-applicative|Streaming & intégration]] — SSE, annulation et tâches longues
- [[95-llm-as-judge|LLM-as-a-judge]] — noter automatiquement, et valider le juge
- [[140-010-transactions-outbox-sagas|Transactions, outbox & sagas]] — implémenter compensation et validation des actions
- [[00-moc-ai-engineering|MOC AI Engineering]]
