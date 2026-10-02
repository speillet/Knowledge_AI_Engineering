# Carte des protocoles agentiques — Flashcards
Tags: #flashcards #ai-engineering #agents #protocoles #mcp #a2a
Vérifié le : 30 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.

Quels protocoles relient un agent à son environnement, et à quel niveau ?
?
<!--anki:43777b6e472d742a3e38-->
```text
            interface utilisateur
                    │  AG-UI
autres agents ── A2A ── AGENT ── MCP ── outils, données
                    │  API compatible OpenAI
                  modèles
      traces : OpenTelemetry · consignes : AGENTS.md, skills
```
Chaque protocole règle **une frontière**. Les confondre mène à tout faire passer par un seul, par exemple exposer un agent comme un simple outil MCP.

---

À ne pas confondre : MCP, A2A et AG-UI ?
?
<!--anki:517e403a342b5e76755a-->
- **MCP** : agent ↔ **outils et données**. L'agent appelle une capacité précise et garde le contrôle ([[33-mcp|MCP]])
- **A2A** : agent ↔ **autre agent**, souvent d'un autre éditeur. On délègue une **tâche**, que l'autre agent mène à sa façon ([[36-orchestration-agents|orchestration]])
- **AG-UI** : agent ↔ **interface utilisateur**. Un flux d'événements (texte, appels d'outils, état) vers le front ([[84-streaming-integration-applicative|streaming]])

Question à se poser : qui décide de la suite, l'appelant (MCP) ou l'appelé (A2A) ?

---

Que contient une Agent Card A2A ?
?
<!--anki:6d3f5351705879773044-->
Le document de **découverte** d'un agent, publié à une adresse connue :
- **Identité** et description, fournisseur, version
- **Compétences** (skills) : ce que l'agent sait faire, avec exemples
- **Endpoint** et modes d'échange supportés (streaming, notifications)
- **Authentification** attendue

Depuis A2A 1.0 (mars 2026), les cartes peuvent être **signées** : l'appelant vérifie qu'elles viennent bien de l'éditeur annoncé ([[102-menaces-agents|usurpation]]).

---

Comment se déroule une tâche A2A ?
?
<!--anki:4e733b7434655a54504e-->
1. Le client envoie un **message** qui crée une **tâche**
2. La tâche passe par des **états** : soumise, en cours, **en attente d'information** (l'agent distant demande une précision), terminée, échouée, annulée
3. Les résultats arrivent sous forme d'**artefacts** (documents, données structurées)
4. Le suivi se fait en **streaming SSE**, par interrogation ou par **notification push** (webhook) pour les tâches longues

C'est un modèle de **tâche longue et négociée**, pas d'appel de fonction.

---

Pourquoi l'API « compatible OpenAI » est-elle un standard de fait ?
?
<!--anki:6c527d66745e7243642d-->
Parce que presque tous les serveurs et passerelles l'exposent : vLLM, SGLang, Ollama, LiteLLM, beaucoup de fournisseurs. Changer de modèle revient souvent à changer une **URL et un nom de modèle** ([[81-litellm-api-layer|LiteLLM]]).

Limite : les fonctions **avancées divergent** (prompt caching, raisonnement, outils côté serveur, formats multimodaux). Un code qui en dépend n'est plus portable : on les isole derrière une couche d'abstraction ([[146-choix-modeles|lock-in]]).

---

Que standardisent les conventions OpenTelemetry GenAI ?
?
<!--anki:63383f544e615b586369-->
Les **noms d'attributs et de spans** des traces d'applications LLM et d'agents : modèle appelé, tokens d'entrée et de sortie, raison d'arrêt, spans d'appel d'outil et d'agent. Exemples : `gen_ai.request.model`, `gen_ai.usage.input_tokens`.

Intérêt : un même tableau de bord ou outil d'analyse lit les traces de **frameworks et plateformes différents**, sans adaptateur ([[93-monitoring-inference|monitoring]]).

---

À quoi servent `AGENTS.md` et les skills dans le paysage des standards ?
?
<!--anki:6c386c4d393f6e2f512f-->
Ils standardisent les **consignes données aux agents**, pas les échanges réseau :
- **`AGENTS.md`** : instructions de projet lues par les agents de code, quel que soit l'outil ([[49-agents-de-code|agents de code]])
- **Skills** : dossiers d'instructions et de scripts chargés **à la demande** (format `SKILL.md`), repris par plusieurs harness ([[34-harness-plugins|skills]])

Ce sont aussi des **entrées non fiables** quand elles viennent d'un dépôt ou d'un catalogue tiers ([[104-securite-mcp-skills|sécurité des skills]]).

---

Quels protocoles encadrent les paiements effectués par des agents ?
?
<!--anki:4f2c2c357e4d60472f7e-->
- **AP2** (Agent Payments Protocol, Google, 2025) : des **mandats signés** prouvent ce que l'utilisateur a autorisé (montant, marchand, conditions), pour qu'un paiement déclenché par un agent soit vérifiable et contestable
- **ACP** (Agentic Commerce Protocol, OpenAI et Stripe, 2025) : le parcours d'achat entre un agent conversationnel et un marchand

Principe commun : l'agent ne manipule jamais les moyens de paiement bruts, et **l'autorisation de l'humain est prouvée** cryptographiquement.

---

Qui gouverne ces standards, et pourquoi est-ce important ?
?
<!--anki:7a382370606173486134-->
MCP, A2A et `AGENTS.md` sont passés sous la gouvernance de la **Linux Foundation**, notamment via l'**Agentic AI Foundation** créée fin 2025. Un protocole contrôlé par un seul éditeur peut changer ou disparaître selon ses intérêts ; une fondation neutre rend l'investissement plus sûr.

Critère de choix : préférer un protocole **ouvert, multi-éditeurs et versionné**, et suivre son calendrier de dépréciation ([[115-plateformes-agents-gouvernance|verrouillage]]).

---

Quand ne pas exposer un agent en A2A ?
?
<!--anki:6c7a5b4c793579265f52-->
- **Agents dans la même application** : un appel de fonction ou un sous-agent suffit, sans réseau ni sérialisation ([[36-orchestration-agents|sous-agents]])
- **Capacité simple et déterministe** : c'est un **outil**, à exposer en MCP
- **Aucun consommateur externe** prévu : A2A ajoute authentification, découverte et surface d'attaque pour rien

A2A se justifie **entre équipes, entre éditeurs ou entre organisations**.

---

Quelle frontière de confiance chaque protocole introduit-il ?
?
<!--anki:7826376228252b703a2b-->
- **MCP** : les descriptions et résultats d'outils entrent dans le contexte, donc **injection** possible ([[104-securite-mcp-skills|sécurité MCP]])
- **A2A** : un agent distant peut être **usurpé** ou compromis, et ses réponses sont des données non fiables
- **AG-UI** : l'interface ne doit afficher ou exécuter que des événements **validés**
- **`AGENTS.md` et skills** : des instructions venues d'un dépôt ou d'un catalogue tiers

Chaque protocole ajouté est une **frontière à authentifier, journaliser et filtrer**.

---

## Mises en situation

Mise en situation : ton entreprise veut que son agent de voyages interne réserve via l'agent d'une agence partenaire, affiche sa progression dans l'application web, et consulte les politiques internes de déplacement. Quels protocoles utilises-tu, et où ?
?
<!--anki:74765a2e296f595d6542-->
1. **Politiques internes** : un serveur **MCP** en lecture seule sur la base documentaire, c'est un outil
2. **Agence partenaire** : **A2A**, car on délègue une tâche négociée (disponibilités, précisions) à un agent d'un autre éditeur, via son Agent Card signée
3. **Interface** : **AG-UI** ou un flux d'événements équivalent pour afficher étapes et demandes de confirmation ([[84-streaming-integration-applicative|streaming]])
4. **Traces** : OpenTelemetry sur toute la chaîne, pour relier une réservation à ses étapes
5. **Paiement** : confirmation humaine explicite, idéalement avec un mandat vérifiable plutôt qu'une carte confiée à l'agent

**Piège** : envelopper l'agent de l'agence dans un outil MCP synchrone, et perdre les échanges de précision et le suivi des tâches longues.

---

Mise en situation : trois équipes ont chacune construit des agents avec des frameworks différents, et la direction veut qu'ils collaborent sans tout réécrire. Que proposes-tu ?
?
<!--anki:6636733d7065247d4b31-->
1. **Inventorier** les capacités : lesquelles sont des outils, lesquelles des agents autonomes
2. **Exposer les outils partagés en MCP**, derrière une gateway commune ([[38-plateformes-agents|gateway d'outils]])
3. **Exposer en A2A** seulement les agents appelés par d'autres équipes, avec Agent Cards dans un registre interne
4. **Unifier l'observabilité** sur les conventions OpenTelemetry GenAI
5. **Garder les frameworks** : les protocoles rendent l'interopérabilité indépendante du code de chaque équipe

**Piège** : imposer un framework unique à tout le monde, alors que le besoin était un contrat d'échange.

---

## Sources

- [MCP — spécification 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28)
- [A2A — spécification du protocole](https://a2a-protocol.org/latest/specification/)
- [AG-UI — protocole d’interaction agent-interface](https://docs.ag-ui.com/introduction)
- [OpenTelemetry — conventions sémantiques GenAI](https://github.com/open-telemetry/semantic-conventions-genai)

## Connexions
- [[33-mcp|MCP]] — le protocole agent ↔ outils
- [[36-orchestration-agents|Orchestration multi-agents]] — A2A et délégation
- [[84-streaming-integration-applicative|Streaming & intégration]] — AG-UI et événements vers l'interface
- [[81-litellm-api-layer|LiteLLM]] — l'API compatible OpenAI comme contrat vers les modèles
- [[93-monitoring-inference|Monitoring]] — conventions OpenTelemetry GenAI
- [[104-securite-mcp-skills|Sécurité de MCP & des skills]] — chaque protocole est une frontière de confiance
- [[115-plateformes-agents-gouvernance|Plateformes d'agents — gouvernance]] — standards ouverts contre verrouillage
- [[11-serveurs-inference-llm|Serveurs d'inférence]] — vLLM, SGLang, TensorRT-LLM et leur réglage
- [[123-caching-agressif|Caching]] — prompt caching et caches de réponses
- [[103-defenses-agents|Défenses des agents]] — isolation, politiques et moindre privilège
- [[37-frameworks-agents|Frameworks d'agents]] — panorama des frameworks
- [[00-moc-ai-engineering|MOC AI Engineering]]
