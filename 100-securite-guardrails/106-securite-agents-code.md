# Sécurité des agents de code — Flashcards
Tags: #flashcards #ai-engineering #securite #agents #coding-agents #llm

Pourquoi les agents de code sont-ils une cible de choix ?
?
Ils tournent **sur les postes des développeurs et dans la CI**, avec accès :
- au **code source** et aux **secrets** (`.env`, clés SSH, identifiants cloud)
- au **shell**, au **réseau**, aux gestionnaires de paquets et à `git push`

Ils lisent aussi beaucoup de **contenu non fiable** : issues, pull requests, README des dépendances, documentation web. Et leur production **part en production**.

---

Pourquoi les modes « sans permission » des agents de code sont-ils dangereux ?
?
Les options qui suppriment les demandes d'approbation (`--dangerously-skip-permissions`, `--yolo`…) laissent l'agent **exécuter n'importe quelle commande** qu'une injection lui suggère. On ne les utilise que dans un environnement **isolé et jetable** : conteneur ou VM, **sans secrets**, réseau limité.

Sinon, on travaille avec des **listes blanches** de commandes et des **règles de refus** sur les chemins sensibles ([[34-harness-plugins|permissions du harness]]).

---

Comment isoler un agent de code sur un poste de développement ?
?
- **Devcontainer ou VM** : le dossier personnel et les clés SSH ne sont pas montés
- **Jetons limités** : un jeton GitHub à grain fin pour **un seul dépôt**, un profil cloud **en lecture seule**
- **Réseau sortant** limité aux registres de paquets et aux API nécessaires
- **Sandbox intégrée** de l'outil activée (système de fichiers et réseau restreints)

---

Qu'a révélé l'attaque s1ngularity contre Nx (août 2025) ?
?
Des versions piégées du paquet npm **Nx** exécutaient à l'installation un script qui appelait les **agents de code installés** (Claude Code, Gemini CLI, Amazon Q) **avec leurs options de contournement des permissions**, pour chercher des secrets et des portefeuilles crypto. Le butin était publié dans des **dépôts GitHub publics**.

Les leçons :
- Un agent de code installé est **un outil de plus pour un malware**
- **Désactiver les scripts d'installation** des paquets (`ignore-scripts`)
- **Protéger les secrets** du poste

---

Que s'est-il passé avec l'extension Amazon Q pour VS Code (juillet 2025) ?
?
Une **pull request malveillante** a ajouté au prompt de l'extension une instruction demandant à l'agent d'**effacer les fichiers locaux et des ressources cloud**. Cette version a été **publiée officiellement** avant d'être retirée.

La leçon : les **prompts et configurations d'un outil IA sont du code**. Ils suivent les mêmes contrôles de revue et de chaîne d'approvisionnement que le reste.

---

Comment un dépôt peut-il piéger un agent de code ?
?
Par ses **fichiers d'instructions** : AGENTS.md, CLAUDE.md, fichiers de règles de l'éditeur, README. L'agent les lit comme des **consignes**.
- La technique **Rules File Backdoor** (Pillar Security, 2025) cache des instructions en **Unicode invisible** dans un fichier de règles, pour faire insérer une porte dérobée dans le code généré
- Un dépôt cloné ou une dépendance peuvent contenir de tels fichiers

Parades : **relire les changements** de ces fichiers comme du code, et **détecter les caractères invisibles** en CI.

---

Qu'est-ce que PromptPwnd (décembre 2025) ?
?
Une classe de failles découverte par Aikido dans des **workflows GitHub Actions et GitLab CI** qui passent du texte externe (titre et corps d'issue, de pull request, messages de commit) dans le **prompt d'un agent** (Gemini CLI, Claude Code, Codex) doté d'un **jeton privilégié**. Un attaquant ouvre une issue piégée, et l'agent exécute des commandes ou **publie des secrets**. Au moins cinq entreprises du Fortune 500 étaient touchées.

---

Comment sécuriser un agent qui tourne dans la CI/CD ?
?
- **Ne jamais** insérer du texte externe dans le prompt d'un agent qui a des outils privilégiés
- **Permissions minimales** pour le jeton du workflow (lecture seule par défaut)
- **Aucun secret** dans les jobs déclenchés par des contributeurs externes ; prudence avec `pull_request_target`, qui donne accès aux secrets
- **Approbation** avant d'exécuter les workflows des forks
- **Outils de l'agent restreints** au strict nécessaire

---

Qu'est-ce que le slopsquatting ?
?
Les modèles **inventent des noms de paquets** qui n'existent pas (environ **20 %** des paquets recommandés dans une étude de 2025 sur 576 000 échantillons de code), et souvent **les mêmes** d'une fois à l'autre. Des attaquants **enregistrent ces noms** avec un contenu malveillant. Parades :
- **Vérifier l'existence et la réputation** d'un paquet avant de l'ajouter
- **Proxy de paquets** interne avec liste blanche, blocage des paquets trop récents
- **Lockfiles** et analyse des dépendances (SCA)

---

Le code généré par IA est-il sûr par défaut ?
?
**Non.** Selon Veracode (2025), **45 %** des échantillons de code générés contenaient une vulnérabilité du Top 10 OWASP. Les défauts fréquents : **injections**, **contrôle d'accès manquant**, secrets en dur, configurations permissives, dépendances obsolètes. Il faut donc :
- La **même revue et le même SAST** que pour du code humain
- Des **consignes de sécurité** dans AGENTS.md et des templates sécurisés
- Une **revue assistée** par un agent si on veut, mais un **humain responsable**

---

Comment encadrer les pull requests produites par des agents ?
?
- **Petites PR**, faciles à relire
- **CODEOWNERS** humains sur les chemins sensibles : authentification, workflows CI, IaC, dépendances
- Un agent ne peut **ni approuver ni fusionner** ses propres PR (protection de branche)
- **Compte dédié** à l'agent (bot) pour tracer qui a écrit quoi
- Les **tests et scans de sécurité** passent obligatoirement avant fusion

---

Comment protéger les secrets face aux agents de code ?
?
L'agent lit les fichiers `.env` et les logs ; il peut **envoyer un secret au fournisseur** dans son contexte ou le **commiter**. Parades :
- **Gestionnaire de secrets** plutôt que des fichiers `.env` en clair
- **Règles de refus** sur les fichiers de secrets dans la configuration de l'agent
- **Détection de secrets** en pre-commit (gitleaks) et en CI
- **Masquage** dans la télémétrie, et **rotation** immédiate en cas d'exposition

---

Quelle politique d'entreprise pour les outils de code IA ?
?
- **Liste d'outils approuvés**, en offre entreprise (pas d'entraînement sur les données, rétention maîtrisée)
- **Paramètres gérés centralement** et non modifiables par l'utilisateur : règles de refus, sandbox, serveurs MCP autorisés
- **Serveurs MCP et skills** issus du registre interne uniquement ([[104-securite-mcp-skills|MCP & skills]])
- **Télémétrie** envoyée au SIEM, **formation** des développeurs, et **processus d'incident** connu

---

## Connexions
- [[34-harness-plugins|Harness & plugins]] — permissions, hooks et sandbox
- [[102-menaces-agents|Menaces & incidents]] — injection et exécution de code
- [[103-defenses-agents|Architecture défensive]] — moindre privilège et secrets
- [[104-securite-mcp-skills|Sécurité de MCP & des skills]] — serveurs et skills sur les postes
- [[105-devsecops-ia-agentique|DevSecOps pour l'IA agentique]] — contrôles en CI
- [[112-cicd-modeles|CI/CD des modèles]] — le pipeline
- [[00-moc-ai-engineering|MOC AI Engineering]]
