# MCP — Model Context Protocol — Flashcards
Tags: #flashcards #ai-engineering #agents #mcp #llm
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.
<!-- summary: problème M×N, host, client et serveur, tools, resources et prompts, transports stdio et HTTP, spec sans état 2026-07-28, serveur MCP ou API REST, risques, tests d'interopérabilité et compatibilité historique, erreurs de protocole et métier, identité du serveur. -->


Qu'est-ce que MCP ? <!--anki:516d532139606b765240-->
?
Le **Model Context Protocol** : un **standard ouvert** (initié par Anthropic, hébergé depuis décembre 2025 par l'**Agentic AI Foundation** de la Linux Foundation) pour connecter les applications IA à des outils et sources de données via une architecture client-serveur.

Par exemple, plusieurs assistants peuvent utiliser le même serveur documentaire sans chacun réimplémenter son API métier. MCP normalise les échanges et la découverte des capacités ; le **host** conserve la décision d'exposer et d'appeler ces capacités. La compatibilité protocolaire ne garantit ni la fiabilité du serveur ni l'autorisation d'accéder à toutes ses données.

---

Quel problème MCP résout-il ? <!--anki:6c3b47315f4c6e566d3b-->
?
Le problème **M×N** : sans standard, chaque app doit intégrer chaque outil ; avec MCP, une app parle à **tout serveur MCP** — d'où l'image du « **USB-C des apps IA** ».

Le protocole standardise notamment la découverte et l'invocation de capacités, ce qui réduit les adaptateurs spécifiques. L'interopérabilité reste conditionnée aux transports, versions et fonctionnalités supportés des deux côtés. Il faut encore configurer l'authentification, les permissions et la sémantique des outils : une connexion réussie ne rend pas tous les serveurs interchangeables.

---

Quelle est l'architecture de MCP ? <!--anki:505935676943515d3e6b-->
?
- **Host** : l'application IA (IDE, chat, agent)
- **Client** : la connexion gérée par le host, **une par serveur**
- **Serveur MCP** : expose outils et données
```text
Host (Claude Code, Cursor, ton agent)
 ├─ client ──→ serveur MCP GitHub      (outils : issues, PR)
 ├─ client ──→ serveur MCP Postgres    (outils : requêtes en lecture)
 └─ client ──→ serveur MCP interne     (outils : CRM maison)
```
Le **modèle ne parle jamais directement** à un serveur : c'est le host qui liste les outils, les présente au modèle, exécute l'appel et renvoie le résultat ([[32-tool-calling|tool calling]]).

Le host reste responsable de l'accord utilisateur et du périmètre des connexions. Brancher deux serveurs n'autorise pas implicitement à transférer les données de l'un vers l'autre.

---

Quelles sont les trois primitives exposées par un serveur MCP ? <!--anki:7334672d62745828472a-->
?
- **Tools** : actions invocables **par le modèle** (il décide)
- **Resources** : données ou documents consultables, choisis **par l'application ou l'utilisateur**
- **Prompts** : templates réutilisables, déclenchés **par l'utilisateur** (souvent des commandes)

La distinction porte sur **qui décide** de l'utiliser : le modèle, l'application, ou l'humain. Les extensions récentes ajoutent les **Tasks** (opérations longues suivies par polling) et les **Apps** (interface HTML rendue dans une sandbox).

Exemple : un guide interne est une ressource, « analyser un incident » un template de prompt, et consulter son ticket un outil. Cette distinction ne remplace jamais l'autorisation côté serveur.

---

Quels transports MCP existent ? <!--anki:683c4f6b67296425664d-->
?
- **stdio** : serveur local lancé en sous-processus
- **HTTP streamable** : serveur distant

Depuis la spec **2026-07-28**, le protocole est **sans état** (plus de session ni de handshake) : un serveur distant passe derrière un simple load balancer. L'ancien transport HTTP+SSE est déprécié.

Le transport détermine surtout **où tourne le serveur et comment l'atteindre**. Avec stdio, maîtriser le binaire lancé, son environnement et ses accès locaux ; avec HTTP, gérer identité, réseau et délais. Fixer la version du protocole et vérifier sa compatibilité côté client et serveur : les garanties de session ne se déduisent pas du seul mot HTTP.

---

À ne pas confondre : serveur MCP et API REST ? <!--anki:6a476f7b5b3434754e73-->
?
- **API REST** : un contrat pensé pour des **développeurs**, qui lisent la doc et écrivent le code d'appel
- **Serveur MCP** : un contrat pensé pour un **modèle**, qui **découvre** à l'exécution outils, ressources et prompts, décrits en langage naturel avec leur JSON Schema

Un serveur MCP **enveloppe** souvent une API REST : il choisit quelles opérations exposer, les renomme et les décrit pour le modèle. Exposer tels quels 200 endpoints REST donne un mauvais serveur MCP. Le lien avec le modèle reste le **[[32-tool-calling|tool calling]]**.

---

Un serveur MCP est-il lié à un modèle particulier ? <!--anki:6b6f7e2628343e304b4f-->
?
**Non.** Le serveur expose des capacités via MCP ; le host les rend accessibles au modèle et organise les échanges. Changer de modèle ne nécessite donc pas, en principe, de réécrire le connecteur.

Mais **compatibilité protocolaire et qualité d'usage sont distinctes**. Exemple : deux hosts accèdent au même outil de tickets ; l'un exploite ses ressources associées, l'autre seulement ses outils. Transport, authentification et capacités prises en charge doivent aussi correspondre. Tester découverte, appel et traitement des erreurs avec chaque host ; un serveur joignable ne garantit ni toutes ses fonctionnalités ni un bon choix d'outil par le modèle.

---

Quels risques de sécurité MCP introduit-il ? <!--anki:6b5735663b3e5b48284d-->
?
**Serveurs tiers non audités, [[101-securite-llm-guardrails|prompt injection]] via les résultats et les descriptions d'outils, permissions trop larges** — d'où sandboxing et validation humaine des actions sensibles. Détail des attaques (tool poisoning, rug pull…) : [[104-securite-mcp-skills|sécurité de MCP & des skills]].

Une description d'outil peut prétendre qu'il faut envoyer un secret pour terminer la tâche ; elle reste une donnée tierce, pas une autorisation. Limiter les jetons et sorties réseau, filtrer l'accès par utilisateur et journaliser les actions. La validation humaine doit montrer la destination et les arguments réels pour permettre un contrôle utile.

---

Comment un host MCP déclare-t-il un serveur local et un serveur distant ? <!--anki:3861633963323633363765663437353461356231323532633438386235333338-->
?
Un serveur **local** est un processus lancé par le host ; un serveur **distant** est joint par son URL et son mécanisme d'authentification. Exemple illustratif pour un host acceptant cette convention :
```json
{
  "mcpServers": {
    "crm-local": { "command": "/opt/mcp/crm/1.4.0/bin/mcp-crm", "args": ["--stdio"] },
    "crm-distant": { "url": "https://mcp.example.org/crm" }
  }
}
```
Le chemin est fictif et versionné ; adapter le format au host et fournir les secrets par son mécanisme sécurisé. MCP n'impose pas universellement ces clés de configuration. Vérifier origine du binaire, droits locaux, transport et version supportée avant connexion ; épingler un composant n'atteste pas sa sûreté.

---

Pourquoi déclarer une capacité MCP ne suffit-il pas à prouver son interopérabilité ? <!--anki:3566646134346631633966373436396262326430383834633532326234373666-->
?
Une **capacité annoncée** décrit ce qu'un participant prétend prendre en charge. Il faut encore vérifier version, transport, authentification et comportement réel avec le host retenu.

Construire un test de contrat : découverte, appel valide, erreur métier, résultat volumineux et refus d'accès. Tester aussi une capacité absente pour vérifier la dégradation prévue. Dans la révision 2026-07-28, version et capacités accompagnent les requêtes ; les clients historiques peuvent nécessiter une adaptation. Fixer la révision testée au lieu de déduire la compatibilité du seul nom MCP.

---

À ne pas confondre : erreur de protocole MCP et échec métier d'un outil ? <!--anki:6336323733623162363238613435343161353064646531613531363534333030-->
?
Une **erreur de protocole** indique que l'échange lui-même est invalide ou impossible ; un **échec métier** peut être une réponse correctement reçue indiquant que l'opération a été refusée ou n'a pas abouti.

Le host doit préserver cette distinction dans ce qu'il montre au modèle et dans ses métriques. Un transport réussi ne prouve pas le succès de l'action. Définir les reprises selon la nature de l'erreur et vérifier le contrat exact de la version MCP utilisée.

---

Pourquoi deux serveurs MCP exposant un outil de même nom ne sont-ils pas interchangeables ? <!--anki:3161383261393963646661373463656161373837353732636534386138353233-->
?
Le nom ne détermine ni **l'identité de l'opérateur, les autorisations, ni la sémantique** de l'action. Deux outils `search` peuvent explorer des corpus et des tenants différents.

Lier la sélection à un serveur authentifié, sa configuration approuvée et son contrat. Tester les résultats et les effets lors d'un remplacement. Une description d'outil récupérée dynamiquement est une donnée à examiner ; elle ne doit pas accorder de nouvelles permissions au serveur qui la fournit.

---

## Mises en situation

Mise en situation : chaque équipe intègre à sa façon les API internes dans ses agents, et le même connecteur Jira existe en quatre versions. Que proposes-tu ? <!--anki:436d2a2b63586a323e77-->
?
1. **Un serveur MCP par système** : publié une fois, réutilisable par tous les hosts, quel que soit le modèle
2. **Registre interne** : découverte, propriétaire, version épinglée, circuit d'approbation ([[38-plateformes-agents|plateformes]])
3. **Gateway MCP** devant les serveurs : authentification, liste blanche d'outils par agent, quotas, audit
4. **Conventions** : nommage des outils, descriptions rédigées avec soin, schémas stricts
5. **Sécurité** : revue avant publication, versions épinglées, surveillance des changements de description ([[104-securite-mcp-skills|sécurité MCP]])

**Piège** : laisser chaque poste de développeur configurer ses propres serveurs MCP, sans inventaire ni contrôle.

---

Mise en situation : ton serveur MCP interne, écrit avant la spec 2026-07-28, garde l'état des requêtes en mémoire par session. Le passage à trois réplicas casse tout. Que fais-tu ? <!--anki:7a3f694b376861363352-->
?
1. **Comprendre** : la spec récente rend le protocole **sans état**, justement pour permettre plusieurs réplicas derrière un load balancer
2. **Sortir l'état de la mémoire du processus** : le serveur émet un **handle opaque** que le client renvoie comme argument, et l'état vit dans un stockage partagé
3. **Lier le handle à l'utilisateur** authentifié côté serveur : le détenir ne doit pas suffire à y accéder ([[104-securite-mcp-skills|sécurité MCP]])
4. **Migrer le transport** : abandonner l'ancien HTTP+SSE, déprécié
5. **Tester** avec plusieurs réplicas et un load balancer simple, sans affinité de session

**Piège** : contourner le problème par des sessions collantes, qui repoussent la dette et cassent au prochain redémarrage.

---

## Sources

- [MCP — spécification 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28)
- [MCP — bonnes pratiques de sécurité, édition 2026-07-28](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices)

- [MCP 2026-07-28 — version et compatibilité](https://modelcontextprotocol.io/specification/2026-07-28/basic/versioning) — approfondissement ciblé du 12 novembre 2026 ; les exemples pédagogiques sont construits pour cette revue.

- Complément du 14 novembre 2026 — Identité et frontières de confiance MCP : [MCP — pratiques de sécurité 2026-07-28](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices).

## Connexions
- [[32-tool-calling|Tool calling]] — le mécanisme sous-jacent
- [[34-harness-plugins|Harness & plugins]] — le host qui intègre MCP
- [[38-plateformes-agents|Plateformes d'agents]] — registre de serveurs MCP
- [[37-frameworks-agents|Frameworks d'agents]] — ADK & A2A côté interop
- [[115-plateformes-agents-gouvernance|Plateformes d'agents — Architecture & gouvernance]] — autorisation d'entreprise et gateway d'outils
- [[104-securite-mcp-skills|Sécurité de MCP & des skills]] — les attaques propres à MCP et les règles de la spec
- [[85-carte-protocoles-agentiques|Carte des protocoles]] — MCP parmi A2A, AG-UI et les autres
- [[103-defenses-agents|Défenses des agents]] — isolation, politiques et moindre privilège
- [[165-computer-use-agents-navigateur|Computer use & agents navigateur]] — agents qui utilisent des interfaces
- [[24-cognee|Cognee]] — une mémoire d'agent en knowledge graph
- [[84-streaming-integration-applicative|Streaming & intégration]] — SSE, annulation et tâches longues
- [[102-menaces-agents|Menaces sur les agents]] — attaques et incidents réels
- [[105-devsecops-ia-agentique|DevSecOps IA]] — contrôles de sécurité dans le cycle de livraison
- [[106-securite-agents-code|Sécurité des agents de code]] — risques propres aux agents de code
- [[81-litellm-api-layer|LiteLLM]] — la gateway entre applications et modèles
- [[00-moc-ai-engineering|MOC AI Engineering]]
