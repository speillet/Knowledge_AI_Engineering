# MCP — Model Context Protocol — Flashcards
Tags: #flashcards #ai-engineering #agents #mcp #llm
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.

Qu'est-ce que MCP ?
?
Le **Model Context Protocol** : un **standard ouvert** (initié par Anthropic, hébergé depuis décembre 2025 par l'**Agentic AI Foundation** de la Linux Foundation) pour connecter les applications IA à des outils et sources de données via une architecture client-serveur.

---

Quel problème MCP résout-il ?
?
Le problème **M×N** : sans standard, chaque app doit intégrer chaque outil ; avec MCP, une app parle à **tout serveur MCP** — d'où l'image du « **USB-C des apps IA** ».

---

Quelle est l'architecture de MCP ?
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

---

Quelles sont les trois primitives exposées par un serveur MCP ?
?
- **Tools** : actions invocables **par le modèle** (il décide)
- **Resources** : données ou documents consultables, choisis **par l'application ou l'utilisateur**
- **Prompts** : templates réutilisables, déclenchés **par l'utilisateur** (souvent des commandes)

La distinction porte sur **qui décide** de l'utiliser : le modèle, l'application, ou l'humain. Les extensions récentes ajoutent les **Tasks** (opérations longues suivies par polling) et les **Apps** (interface HTML rendue dans une sandbox).

---

Quels transports MCP existent ?
?
- **stdio** : serveur local lancé en sous-processus
- **HTTP streamable** : serveur distant

Depuis la spec **2026-07-28**, le protocole est **sans état** (plus de session ni de handshake) : un serveur distant passe derrière un simple load balancer. L'ancien transport HTTP+SSE est déprécié.

---

Quelle différence entre MCP et le tool calling ?
?
Le **[[32-tool-calling|tool calling]]** est le mécanisme du modèle pour émettre un appel ; **MCP** standardise la **découverte et l'accès** aux outils côté application.

---

Un serveur MCP est-il lié à un modèle particulier ?
?
**Non.** C'est l'intérêt : le même serveur (GitHub, base de données, navigateur…) sert n'importe quel host compatible MCP.

---

Quels risques de sécurité MCP introduit-il ?
?
**Serveurs tiers non audités, [[101-securite-llm-guardrails|prompt injection]] via les résultats et les descriptions d'outils, permissions trop larges** — d'où sandboxing et validation humaine des actions sensibles. Détail des attaques (tool poisoning, rug pull…) : [[104-securite-mcp-skills|sécurité de MCP & des skills]].

---

Donnez des exemples de serveurs MCP courants.
?
**GitHub, systèmes de fichiers, bases de données (Postgres), navigateur, Slack** — plus tout serveur interne maison.
```json
// configuration côté host : un serveur local et un serveur distant
{
  "mcpServers": {
    "github":   { "command": "npx", "args": ["-y", "@modelcontextprotocol/server-github@1.4.0"] },
    "crm-interne": { "url": "https://mcp.interne/crm", "headers": { "Authorization": "Bearer …" } }
  }
}
```
Bonne pratique : **version épinglée** plutôt que `@latest`, et serveurs internes derrière une gateway ([[104-securite-mcp-skills|sécurité MCP]]).

---

## Mises en situation

Mise en situation : chaque équipe intègre à sa façon les API internes dans ses agents, et le même connecteur Jira existe en quatre versions. Que proposes-tu ?
?
1. **Un serveur MCP par système** : publié une fois, réutilisable par tous les hosts, quel que soit le modèle
2. **Registre interne** : découverte, propriétaire, version épinglée, circuit d'approbation ([[38-plateformes-agents|plateformes]])
3. **Gateway MCP** devant les serveurs : authentification, liste blanche d'outils par agent, quotas, audit
4. **Conventions** : nommage des outils, descriptions rédigées avec soin, schémas stricts
5. **Sécurité** : revue avant publication, versions épinglées, surveillance des changements de description ([[104-securite-mcp-skills|sécurité MCP]])

**Piège** : laisser chaque poste de développeur configurer ses propres serveurs MCP, sans inventaire ni contrôle.

---

Mise en situation : ton serveur MCP interne, écrit avant la spec 2026-07-28, garde l'état des requêtes en mémoire par session. Le passage à trois réplicas casse tout. Que fais-tu ?
?
1. **Comprendre** : la spec récente rend le protocole **sans état**, justement pour permettre plusieurs réplicas derrière un load balancer
2. **Sortir l'état de la mémoire du processus** : le serveur émet un **handle opaque** que le client renvoie comme argument, et l'état vit dans un stockage partagé
3. **Lier le handle à l'utilisateur** authentifié côté serveur : le détenir ne doit pas suffire à y accéder ([[104-securite-mcp-skills|sécurité MCP]])
4. **Migrer le transport** : abandonner l'ancien HTTP+SSE, déprécié
5. **Tester** avec plusieurs réplicas et un load balancer simple, sans affinité de session

**Piège** : contourner le problème par des sessions collantes, qui repoussent la dette et cassent au prochain redémarrage.

---

## Connexions
- [[32-tool-calling|Tool calling]] — le mécanisme sous-jacent
- [[34-harness-plugins|Harness & plugins]] — le host qui intègre MCP
- [[38-plateformes-agents|Plateformes d'agents]] — registre de serveurs MCP
- [[37-frameworks-agents|Frameworks d'agents]] — ADK & A2A côté interop
- [[115-plateformes-agents-gouvernance|Plateformes d'agents — Architecture & gouvernance]] — autorisation d'entreprise et gateway d'outils
- [[104-securite-mcp-skills|Sécurité de MCP & des skills]] — les attaques propres à MCP et les règles de la spec
- [[00-moc-ai-engineering|MOC AI Engineering]]
