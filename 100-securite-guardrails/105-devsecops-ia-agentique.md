# DevSecOps pour l'IA agentique — Flashcards
Tags: #flashcards #ai-engineering #securite #devsecops #agents #llm

Qu'est-ce que le DevSecOps appliqué à l'IA agentique ?
?
Intégrer la sécurité **à chaque étape du cycle de vie** d'un agent (conception, code, build, tests, déploiement, exploitation) plutôt qu'en audit final. Ce qui change par rapport à une application classique :
- **Nouveaux actifs** à protéger et versionner : prompts, configurations d'outils, serveurs MCP, skills, modèles, datasets, mémoire, jeux d'evals
- **Nouvelle surface d'attaque** : toute entrée en langage naturel
- **Comportement non déterministe**, qui se teste statistiquement ([[114-reproductibilite-variance|reproductibilité]])

---

Comment faire le threat modeling d'un agent ?
?
1. **Cartographier** : actifs, données, outils et droits, flux, frontières de confiance, sorties réseau
2. **Lister les entrées non fiables** ([[102-menaces-agents|menaces]]) et vérifier la **Rule of Two** pour chaque flux
3. **Énumérer les menaces** avec STRIDE, le Top 10 OWASP agentique, **MAESTRO** (Cloud Security Alliance, modèle en 7 couches pour l'IA agentique) ou **MITRE ATLAS**
4. En déduire des **contrôles** et des **tests adversariaux**

À refaire dès qu'on ajoute un **outil, une source de données ou un niveau d'autonomie**.

---

Quels référentiels de sécurité IA faut-il connaître ?
?
- **OWASP** : Top 10 LLM (2025), Top 10 des applications agentiques (décembre 2025), AI Exchange
- **MITRE ATLAS** : tactiques et techniques d'attaque contre l'IA, sur le modèle d'ATT&CK
- **NIST** : AI RMF et son profil IA générative (AI 600-1) ; **AI Agent Standards Initiative** du CAISI (février 2026), qui prépare des overlays SP 800-53 dédiés aux agents
- **ISO/IEC 42001** : système de management de l'IA
- **CSA MAESTRO**, **Google SAIF**
- **AI Act** européen ([[115-plateformes-agents-gouvernance|gouvernance]])

---

Qu'est-ce qu'un AI-BOM ?
?
Un **inventaire des composants IA** d'un système, sur le modèle du SBOM : modèles (version, source, licence), datasets, prompts, outils et serveurs MCP, skills, dépendances. Formats : **CycloneDX ML-BOM** et **profil IA de SPDX 3**.

Il sert à **répondre vite à un incident** (« quels agents utilisent le serveur X compromis ? »), à l'audit et à la conformité. Il devient une **exigence d'achat** dans certains marchés publics.

---

Comment sécuriser la chaîne d'approvisionnement des modèles ?
?
- **Sources officielles** et miroir interne, révision **épinglée** par empreinte
- Format **safetensors** plutôt que pickle, qui peut exécuter du code ([[10-images-modeles-poids|poids de modèles]]) ; analyser les pickles restants (ModelScan, picklescan)
- **Vérifier les signatures** : OpenSSF **Model Signing** (v1.0 en 2025, basé sur Sigstore)
- Se méfier des **fine-tunes tiers**, qui peuvent contenir des **portes dérobées** activées par un déclencheur
- Vérifier la **licence**

---

Quels contrôles de sécurité mettre dans la CI d'un agent ?
?
- **Classiques** : SAST, analyse des dépendances (SCA) et lockfiles, détection de secrets, scan des images et de l'IaC
- **Spécifiques à l'IA** :
  - scan des **configurations MCP et des skills** (ex. mcp-scan)
  - lint des prompts et configurations : **pas de secrets**, listes blanches d'outils respectées
  - **suite de tests adversariaux** utilisée comme gate
  - génération de l'**AI-BOM** et **signature** des artefacts

Voir [[112-cicd-modeles|CI/CD des modèles]].

---

Comment automatiser les tests adversariaux d'un agent ?
?
- **Outils** : **promptfoo** (open source, racheté par OpenAI en mars 2026), **garak** (NVIDIA), **PyRIT** (Microsoft)
- **Benchmarks** : AgentDojo, InjecAgent
- **Cas de test** : une injection **par source d'entrée non fiable**, tentatives d'exfiltration, escalade de privilèges, jailbreaks, actions destructrices
- **Métrique** : le **taux de réussite des attaques** (ASR) par catégorie

Chaque attaque réussie devient un **test de régression**. Les attaques adaptatives restent plus fortes que ces suites : on complète par du red teaming humain.

---

Comment mener le red teaming d'un système agentique ?
?
- Tester **le système entier**, pas seulement le modèle : outils, mémoire, RAG, rendu de l'interface, échanges entre agents
- Partir des **scénarios du threat model** : vol de données, action non autorisée, dépassement de coût
- Mobiliser la **créativité humaine** : face aux humains, toutes les défenses testées sont tombées ([[102-menaces-agents|« The Attacker Moves Second »]])
- **Quand** : avant le lancement, à chaque changement majeur, et en continu (bug bounty)

---

Qu'est-ce qu'un security eval gate pour un agent ?
?
Un **seuil de sécurité qui bloque le déploiement**, comme l'[[112-cicd-modeles|eval gate]] qualité :
- Un **ASR maximal** par catégorie d'attaque
- **Tolérance zéro** pour les scénarios critiques (fuite de secrets, action destructrice)

Il est rejoué à **chaque changement de modèle, de prompt, d'outil ou de skill** : une simple montée de version du modèle peut changer sa robustesse.

---

Comment gérer les prompts et configurations d'agents de manière sécurisée ?
?
**Comme du code** :
- **Versionnés** dans Git et **relus** en pull request
- **CODEOWNERS** sécurité sur les listes d'outils, les politiques et les droits
- **Aucun secret**, releases signées
- **Détection des écarts** entre la configuration déclarée et celle qui tourne (registre, [[115-plateformes-agents-gouvernance|gouvernance]])

Une ligne de prompt qui ajoute un outil, c'est **un changement de droits**.

---

Quelles règles pour les environnements de dev et de test des agents ?
?
- **Données synthétiques ou anonymisées** en dev et en préproduction
- **Identifiants séparés** : aucun jeton de production accessible à un agent de dev
- **Outils simulés** ou sandboxés pour les tests, surtout ceux qui écrivent ou envoient
- **Mêmes politiques et mêmes guardrails** qu'en production, pour tester ce qui sera réellement déployé

---

Que journaliser pour la sécurité d'un agent ?
?
Pour chaque action :
- **Qui** : l'utilisateur et l'agent
- **Quel outil**, avec quels arguments (secrets masqués)
- **Décision de politique**, approbation éventuelle, résultat
- **ID de corrélation** vers la trace complète

On envoie ces journaux au **SIEM**. Comme ils contiennent des données sensibles, on les **protège** (accès restreint, rétention définie). Voir [[93-monitoring-inference|monitoring]].

---

Comment détecter un agent compromis à l'exécution ?
?
Des signaux à surveiller :
- **Nouveaux outils ou domaines** contactés, **pics** d'appels, boucles
- **Refus de politique** en hausse
- **Données sensibles** dans les sorties (DLP)
- **Changement de description** d'un outil
- Activité à des **horaires inhabituels**

On peut aussi placer des **honeytokens** : de fausses données sensibles dont toute utilisation trahit une exfiltration. Les plateformes proposent de la détection d'anomalies dédiée aux agents.

---

Comment réagir à un incident impliquant un agent ?
?
1. **Contenir** : kill switch (désactiver l'agent, bloquer l'outil à la gateway), **révoquer les jetons**, faire la rotation des secrets
2. **Enquêter** grâce aux traces et au journal de session : quelle entrée, quelles actions, quelles données
3. **Nettoyer** : purger la mémoire ou l'index empoisonnés, corriger les actions (compensation)
4. **Notifier** selon les obligations
5. **Post-mortem** : nouveau contrôle et **nouveau test de régression**

Le playbook s'**exerce à l'avance**, comme pour tout incident de sécurité.

---

Comment gérer les vulnérabilités d'un système agentique ?
?
- Maintenir l'**inventaire** (AI-BOM) pour savoir ce qui est exposé
- **Suivre les avis de sécurité** des frameworks, SDK MCP, serveurs et outils d'agents : ils ont déjà eu des failles critiques (ex. CVE-2025-49596 dans MCP Inspector, CVE-2025-6514 dans mcp-remote)
- Des **délais de correction** selon la criticité, comme pour toute dépendance
- Surveiller aussi les **dépréciations de modèles et d'API**, qui forcent des changements

---

Qui est responsable de la sécurité des agents ?
?
Une **responsabilité partagée** :
- **Équipe plateforme** : contrôles fournis par défaut (gateway, sandbox, identité, traces)
- **Équipe produit** : threat model, outils au moindre privilège, tests adversariaux
- **Équipe sécurité** : standards, red teaming, détection, réponse aux incidents
- **Propriétaire de chaque agent** : responsable de son comportement et de ses droits

Des **security champions** dans les équipes, et la formation des développeurs aux risques propres aux agents.

---

## Connexions
- [[102-menaces-agents|Menaces & incidents]] — ce que le threat model doit couvrir
- [[103-defenses-agents|Architecture défensive]] — les contrôles à vérifier
- [[104-securite-mcp-skills|Sécurité de MCP & des skills]] — scanner les outils et les skills
- [[106-securite-agents-code|Sécurité des agents de code]] — les agents dans la CI/CD
- [[112-cicd-modeles|CI/CD des modèles]] — eval gate et pipeline
- [[111-mlops-llmops-fondamentaux|MLOps & LLMOps]] — versionner les artefacts
- [[115-plateformes-agents-gouvernance|Plateformes d'agents — Architecture & gouvernance]] — audit, kill switch, AI Act
- [[93-monitoring-inference|Monitoring de l'inférence]] — journaux et alertes
- [[10-images-modeles-poids|Images & poids de modèles]] — safetensors ou pickle
- [[101-securite-llm-guardrails|Sécurité LLM & guardrails]] — OWASP LLM et red teaming
- [[00-moc-ai-engineering|MOC AI Engineering]]
