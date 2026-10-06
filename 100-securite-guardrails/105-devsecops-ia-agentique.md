# DevSecOps pour l'IA agentique — Flashcards
Tags: #flashcards #ai-engineering #securite #devsecops #agents #llm
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.
<!-- summary: threat modeling (MAESTRO, ATLAS), référentiels (OWASP, NIST, ISO 42001), AI-BOM, SBOM ou AI-BOM, supply chain des modèles, contrôles en CI, tests adversariaux (promptfoo, garak, PyRIT), red teaming, security eval gate, prompts comme du code, environnements, journalisation, détection, réponse à incident, vulnérabilités, responsabilités. -->


Qu'est-ce que le DevSecOps appliqué à l'IA agentique ? <!--anki:44494a704c554b4f3d6c-->
?
Intégrer la sécurité **à chaque étape du cycle de vie** d'un agent (conception, code, build, tests, déploiement, exploitation) plutôt qu'en audit final. Ce qui change par rapport à une application classique :
- **Nouveaux actifs** à protéger et versionner : prompts, configurations d'outils, serveurs MCP, skills, modèles, datasets, mémoire, jeux d'evals
- **Nouvelle surface d'attaque** : toute entrée en langage naturel
- **Comportement non déterministe**, qui se teste statistiquement ([[114-reproductibilite-variance|reproductibilité]])

---

Comment faire le threat modeling d'un agent ? <!--anki:5f6043506c24217b64-->
?
1. **Cartographier** : actifs, données, outils et droits, flux, frontières de confiance, sorties réseau
2. **Lister les entrées non fiables** ([[102-menaces-agents|menaces]]) et vérifier la **Rule of Two** pour chaque flux
3. **Énumérer les menaces** avec STRIDE, le Top 10 OWASP agentique, **MAESTRO** (Cloud Security Alliance, modèle en 7 couches pour l'IA agentique) ou **MITRE ATLAS**
4. En déduire des **contrôles** et des **tests adversariaux**

À refaire dès qu'on ajoute un **outil, une source de données ou un niveau d'autonomie**.

---

Quels référentiels décrivent les attaques contre l'IA et les agents ? <!--anki:414b466a5e572f687153-->
?
- **OWASP** : Top 10 LLM (2025), Top 10 des applications agentiques (décembre 2025), AI Exchange
- **MITRE ATLAS** : tactiques et techniques d'attaque contre l'IA, sur le modèle d'ATT&CK

Ces référentiels servent de vocabulaire et de point de départ pour les scénarios de menace, pas de preuve de sécurité. Relier chaque menace pertinente à un composant réel, une mesure et un test. Conserver la version du référentiel utilisée afin de pouvoir expliquer la couverture et les évolutions de l'analyse.

---

Que propose le NIST pour la sécurité de l'IA et des agents ? <!--anki:705724283e7326467450-->
?
- **AI RMF** : le cadre de gestion des risques de l'IA, avec son **profil IA générative** (AI 600-1)
- **AI Agent Standards Initiative** du CAISI (février 2026) : interopérabilité et sécurité des agents. Elle prépare des **overlays SP 800-53** dédiés aux agents : moindre privilège des outils, confinement des actions, journalisation

---

Quels cadres de management et de conformité s'appliquent à l'IA agentique ? <!--anki:4c565e4f416e3d577049-->
?
- **ISO/IEC 42001** : système de management de l'IA, certifiable
- **CSA MAESTRO** (threat modeling agentique) et **Google SAIF** (cadre de sécurité de l'IA)
- **AI Act** européen ([[115-plateformes-agents-gouvernance|gouvernance]])

Ils n'ont pas le même statut : norme de management, méthode d'analyse, cadre de sécurité et règlement imposent des démarches différentes. Choisir les exigences selon le rôle de l'organisation et l'usage du système. Une certification de management ne prouve pas qu'un agent particulier résiste aux injections ou satisfait toutes ses obligations légales.

---

Qu'est-ce qu'un AI-BOM ? <!--anki:4d585b443b5e6e4c3825-->
?
Un **inventaire des composants IA** d'un système, sur le modèle du SBOM : modèles (version, source, licence), datasets, prompts, outils et serveurs MCP, skills, dépendances. Formats : **CycloneDX ML-BOM** et **profil IA de SPDX 3**.

Il sert à **répondre vite à un incident** (« quels agents utilisent le serveur X compromis ? »), à l'audit et à la conformité. Il devient une **exigence d'achat** dans certains marchés publics.

---

Comment sécuriser la chaîne d'approvisionnement des modèles ? <!--anki:32397d2c3454654279-->
?
- **Sources officielles** et miroir interne, révision **épinglée** par empreinte
- Format **safetensors** plutôt que pickle, qui peut exécuter du code ([[10-images-modeles-poids|poids de modèles]]) ; analyser les pickles restants (ModelScan, picklescan)
- **Vérifier les signatures** : OpenSSF **Model Signing** (v1.0 en 2025, basé sur Sigstore)
- Se méfier des **fine-tunes tiers**, qui peuvent contenir des **portes dérobées** activées par un déclencheur
- Vérifier la **licence**

---

Quels contrôles de sécurité classiques restent indispensables dans la CI d'un agent ? <!--anki:635f446973612436423e-->
?
Les mêmes que pour toute application :
- **SAST** sur le code de l'agent
- **Analyse des dépendances** (SCA) et lockfiles
- **Détection de secrets**
- **Scan des images et de l'IaC**

Ils détectent des failles du logiciel qui entoure le modèle : dépendance vulnérable, secret commité ou permissions d'infrastructure excessives. Les compléter par des tests des outils et des attaques sur le contexte. Réussir les scans classiques ne démontre pas qu'une instruction malveillante récupérée dans un document sera correctement contenue.

---

Quels contrôles de sécurité propres à l'IA ajouter dans la CI d'un agent ? <!--anki:6b4e737433567a426026-->
?
- Scan des **configurations MCP et des skills** (ex. mcp-scan)
- Lint des prompts et configurations : **pas de secrets**, listes blanches d'outils respectées
- **Suite de tests adversariaux** utilisée comme gate
- Génération de l'**AI-BOM** et **signature** des artefacts
```yaml
jobs:
  securite-ia:
    steps:
      - run: mcp-scan scan .mcp.json                  # outils et skills
      - run: python -m lint_prompts prompts/          # secrets, outils autorisés
      - run: promptfoo redteam run --config redteam.yaml
      - run: python -m ai_bom generate > aibom.json
      - run: python -m check_asr --max-injection 0.05 --max-exfiltration 0
```
Voir [[112-cicd-modeles|CI/CD des modèles]].

---

Comment automatiser les tests adversariaux d'un agent ? <!--anki:516a3b58562466217c52-->
?
- **Outils** : **promptfoo** (open source, racheté par OpenAI en mars 2026), **garak** (NVIDIA), **PyRIT** (Microsoft)
- **Benchmarks** : AgentDojo, InjecAgent
- **Cas de test** : une injection **par source d'entrée non fiable**, tentatives d'exfiltration, escalade de privilèges, jailbreaks, actions destructrices
- **Métrique** : le **taux de réussite des attaques** (ASR) par catégorie

Chaque attaque réussie devient un **test de régression**. Les attaques adaptatives restent plus fortes que ces suites : on complète par du red teaming humain.

---

Comment mener le red teaming d'un système agentique ? <!--anki:792541572a57546c3a6b-->
?
- Tester **le système entier**, pas seulement le modèle : outils, mémoire, RAG, rendu de l'interface, échanges entre agents
- Partir des **scénarios du threat model** : vol de données, action non autorisée, dépassement de coût
- Mobiliser la **créativité humaine** : face aux humains, toutes les défenses testées sont tombées ([[102-menaces-agents|« The Attacker Moves Second »]])
- **Quand** : avant le lancement, à chaque changement majeur, et en continu (bug bounty)

---

Qu'est-ce qu'un security eval gate pour un agent ? <!--anki:737e5d52593c53394d46-->
?
Un **seuil de sécurité qui bloque le déploiement**, comme l'[[112-cicd-modeles|eval gate]] qualité :
- Un **ASR maximal** par catégorie d'attaque
- **Tolérance zéro** pour les scénarios critiques (fuite de secrets, action destructrice)

Il est rejoué à **chaque changement de modèle, de prompt, d'outil ou de skill** : une simple montée de version du modèle peut changer sa robustesse.

---

Comment gérer les prompts et configurations d'agents de manière sécurisée ? <!--anki:497c4871785959714777-->
?
**Comme du code** :
- **Versionnés** dans Git et **relus** en pull request
- **CODEOWNERS** sécurité sur les listes d'outils, les politiques et les droits
- **Aucun secret**, releases signées
- **Détection des écarts** entre la configuration déclarée et celle qui tourne (registre, [[115-plateformes-agents-gouvernance|gouvernance]])

Une ligne de prompt qui ajoute un outil, c'est **un changement de droits**.

---

Quelles règles pour les environnements de dev et de test des agents ? <!--anki:50442e70333969307a7b-->
?
- **Données synthétiques ou anonymisées** en dev et en préproduction
- **Identifiants séparés** : aucun jeton de production accessible à un agent de dev
- **Outils simulés** ou sandboxés pour les tests, surtout ceux qui écrivent ou envoient
- **Mêmes politiques et mêmes guardrails** qu'en production, pour tester ce qui sera réellement déployé

---

Que journaliser pour la sécurité d'un agent ? <!--anki:755e792c39652e345530-->
?
Pour chaque action :
- **Qui** : l'utilisateur et l'agent
- **Quel outil**, avec quels arguments (secrets masqués)
- **Décision de politique**, approbation éventuelle, résultat
- **ID de corrélation** vers la trace complète

On envoie ces journaux au **SIEM**. Comme ils contiennent des données sensibles, on les **protège** (accès restreint, rétention définie). Voir [[93-monitoring-inference|monitoring]].

---

Comment détecter un agent compromis à l'exécution ? <!--anki:6c7162372875413e5d40-->
?
Des signaux à surveiller :
- **Nouveaux outils ou domaines** contactés, **pics** d'appels, boucles
- **Refus de politique** en hausse
- **Données sensibles** dans les sorties (DLP)
- **Changement de description** d'un outil
- Activité à des **horaires inhabituels**

On peut aussi placer des **honeytokens** : de fausses données sensibles dont toute utilisation trahit une exfiltration. Les plateformes proposent de la détection d'anomalies dédiée aux agents.

---

Comment réagir à un incident impliquant un agent ? <!--anki:6d2e6a44283a755e6b31-->
?
1. **Contenir** : kill switch (désactiver l'agent, bloquer l'outil à la gateway), **révoquer les jetons**, faire la rotation des secrets
2. **Enquêter** grâce aux traces et au journal de session : quelle entrée, quelles actions, quelles données
3. **Nettoyer** : purger la mémoire ou l'index empoisonnés, corriger les actions (compensation)
4. **Notifier** selon les obligations
5. **Post-mortem** : nouveau contrôle et **nouveau test de régression**

Le playbook s'**exerce à l'avance**, comme pour tout incident de sécurité.

---

Comment gérer les vulnérabilités d'un système agentique ? <!--anki:48216c502f3d38795f7e-->
?
- Maintenir l'**inventaire** (AI-BOM) pour savoir ce qui est exposé
- **Suivre les avis de sécurité** des frameworks, SDK MCP, serveurs et outils d'agents : ils ont déjà eu des failles critiques (ex. CVE-2025-49596 dans MCP Inspector, CVE-2025-6514 dans mcp-remote)
- Des **délais de correction** selon la criticité, comme pour toute dépendance
- Surveiller aussi les **dépréciations de modèles et d'API**, qui forcent des changements

---

Qui est responsable de la sécurité des agents ? <!--anki:4b507379584d596b234b-->
?
Une **responsabilité partagée** :
- **Équipe plateforme** : contrôles fournis par défaut (gateway, sandbox, identité, traces)
- **Équipe produit** : threat model, outils au moindre privilège, tests adversariaux
- **Équipe sécurité** : standards, red teaming, détection, réponse aux incidents
- **Propriétaire de chaque agent** : responsable de son comportement et de ses droits

Des **security champions** dans les équipes, et la formation des développeurs aux risques propres aux agents.

---

À ne pas confondre : SBOM et AI-BOM ? <!--anki:723559332f417224645b-->
?
- **SBOM** : l'inventaire des **composants logiciels** d'une application (bibliothèques, versions, licences), pour savoir qui est touché par une vulnérabilité
- **AI-BOM** : étend l'inventaire aux **composants IA** : modèles et leurs versions, jeux de données, prompts, serveurs MCP, skills, agents et leurs outils

L'AI-BOM répond à la question « quels agents utilisent ce serveur MCP compromis ? » que le SBOM ne couvre pas.

---

## Mises en situation

Mise en situation : tu dois mettre en place la CI/CD d'un nouvel agent qui lit le CRM et envoie des e-mails aux clients. Que mets-tu dans le pipeline ? <!--anki:715f364056525f595273-->
?
1. **Contrôles classiques** : SAST, SCA, détection de secrets, scan d'image et d'IaC
2. **Contrôles IA** : scan des configurations MCP et des skills, lint des prompts (pas de secrets, outils autorisés), génération de l'AI-BOM
3. **Evals qualité** et **tests adversariaux** : injections dans les e-mails et les fiches CRM, tentatives d'exfiltration, envoi à des destinataires non autorisés
4. **Security eval gate** : tolérance zéro pour l'exfiltration et l'envoi non autorisé, seuil d'ASR pour le reste
5. **Déploiement progressif** : canary surveillé, rollback prêt ([[112-cicd-modeles|CI/CD]])

**Piège** : ne lancer les tests adversariaux qu'au premier déploiement, et pas à chaque changement de modèle, de prompt ou d'outil.

---

Mise en situation : une alerte signale l'utilisation d'un honeytoken, une fausse clé d'API placée dans la base documentaire de ton agent RH. Déroule ta réponse à incident. <!--anki:4d344f4e3765742d4069-->
?
1. **Contenir** : désactiver l'agent ou ses outils sortants, révoquer ses jetons ([[115-plateformes-agents-gouvernance|kill switch]])
2. **Tracer** : quelle session a lu le document piégé, quelle entrée a déclenché la fuite, par quel canal la clé est sortie
3. **Évaluer** : quelles vraies données ont pu sortir par le même chemin ; faire tourner les secrets concernés
4. **Nettoyer** : retirer le contenu malveillant de l'index ou de la mémoire
5. **Notifier** selon les obligations, surtout pour des données personnelles
6. **Post-mortem** : fermer le canal (réseau sortant, rendu des URL) et ajouter un test de régression

**Piège** : supprimer le document piégé avant d'avoir sauvegardé les traces.

---

Mise en situation : ton fournisseur annonce que le modèle utilisé par tes agents passe à une nouvelle version le mois prochain. Que prévois-tu côté sécurité ? <!--anki:653e3f45697d4c752f34-->
?
1. **Inventaire** : l'AI-BOM indique quels agents utilisent ce modèle
2. **Rejouer** la suite adversariale et les evals sur la nouvelle version : la robustesse aux injections peut changer d'une version à l'autre
3. **Comparer** l'ASR par catégorie avec la version actuelle, sur les mêmes cas ([[114-reproductibilite-variance|comparaison appariée]])
4. **Bloquer** si le security eval gate n'est pas atteint : renforcer les contrôles d'architecture ou rester sur l'ancienne version tant qu'elle est disponible
5. **Déployer progressivement** en surveillant les refus de politique et les anomalies

**Piège** : utiliser un alias de modèle qui bascule tout seul vers la nouvelle version.

---

## Sources

- [NIST — AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- [MITRE ATLAS — techniques d’attaque contre les systèmes IA](https://atlas.mitre.org/)

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
- [[155-ai-act|AI Act]] — obligations réglementaires
- [[33-mcp|MCP]] — le protocole standard entre agents et outils
- [[00-moc-ai-engineering|MOC AI Engineering]]
