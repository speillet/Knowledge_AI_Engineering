# MCP — Model Context Protocol — Flashcards
Tags: #flashcards #ai-engineering #agents #mcp #llm

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
- **Client** : la connexion gérée par le host
- **Serveur MCP** : expose outils et données

---

Quelles sont les trois primitives exposées par un serveur MCP ?
?
- **Tools** : actions invocables par le modèle
- **Resources** : données/documents consultables
- **Prompts** : templates réutilisables

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

---

## Connexions
- [[32-tool-calling|Tool calling]] — le mécanisme sous-jacent
- [[34-harness-plugins|Harness & plugins]] — le host qui intègre MCP
- [[38-plateformes-agents|Plateformes d'agents]] — registre de serveurs MCP
- [[37-frameworks-agents|Frameworks d'agents]] — ADK & A2A côté interop
- [[115-plateformes-agents-gouvernance|Plateformes d'agents — Architecture & gouvernance]] — autorisation d'entreprise et gateway d'outils
- [[104-securite-mcp-skills|Sécurité de MCP & des skills]] — les attaques propres à MCP et les règles de la spec
- [[00-moc-ai-engineering|MOC AI Engineering]]
