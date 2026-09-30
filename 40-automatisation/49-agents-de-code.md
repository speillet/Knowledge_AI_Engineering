# Agents de code : usage & intégration — Flashcards
Tags: #flashcards #ai-engineering #agents #agents-de-code #developpement #llm
Vérifié le : 30 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.

Qu'est-ce qu'un agent de code ?
?
Un agent qui **lit le dépôt, édite des fichiers, lance des commandes** (tests, build, linter) et itère sur les résultats jusqu'à atteindre l'objectif. La différence avec l'autocomplétion : il **agit sur plusieurs fichiers** et **vérifie son travail** en exécutant du code.

Exemples de harness : Claude Code, Codex CLI, Cursor, Aider ([[34-harness-plugins|harness]]).

---

Qu'est-ce que l'ACI (Agent-Computer Interface) ?
?
L'idée, introduite par **SWE-agent** (Princeton, 2024), que les outils d'un agent doivent être **conçus pour un modèle**, comme une interface l'est pour un humain :
- Commandes **simples** et peu nombreuses
- Sorties **courtes et informatives** (un résumé plutôt que 5 000 lignes de log)
- **Garde-fous** : un éditeur qui refuse une modification qui casse la syntaxe

Même modèle, meilleure ACI : nettement plus de tâches résolues ([[32-tool-calling|conception d'outils]]).

---

Pourquoi les tests sont-ils le meilleur allié d'un agent de code ?
?
Ils donnent un **signal de réussite vérifiable** : l'agent peut boucler « modifier → lancer les tests → corriger » sans humain. Sans tests, il ne sait pas s'il a fini, et le reviewer doit tout vérifier à la main.

Pratique efficace : faire **écrire le test d'abord** (qui échoue), puis le code. Attention à l'agent qui **modifie ou supprime le test** pour le faire passer : relire les diffs de tests.

---

À quoi sert un fichier `CLAUDE.md` ou `AGENTS.md` ?
?
C'est la **mémoire de projet** chargée à chaque session : commandes de build et de test, conventions, architecture, pièges connus. `AGENTS.md` est le format **commun à plusieurs outils**, confié à l'Agentic AI Foundation.

Le garder **court et factuel** : il consomme du contexte à chaque tour. Les procédures longues vont dans des **skills** chargées à la demande ([[34-harness-plugins|mémoire et skills]]).

---

Pourquoi demander un plan avant l'implémentation ?
?
Sur une tâche non triviale, un agent qui code tout de suite part souvent dans une **mauvaise direction** et produit un gros diff à jeter. Un **mode plan** (lecture seule) lui fait explorer le code et proposer une approche que l'humain **corrige en quelques lignes**, avant tout changement.

C'est le pattern plan-and-execute appliqué au code ([[48-patterns-workflows-agentiques|patterns]]).

---

Comment faire travailler plusieurs agents de code en parallèle ?
?
- **Un worktree Git par agent** (`git worktree add`) : chaque agent a sa copie de travail et sa branche, sans se marcher dessus
- **Sous-agents** pour l'exploration : ils lisent beaucoup de code et ne renvoient qu'un résumé, ce qui protège le contexte principal ([[36-orchestration-agents|sous-agents]])
- **Tâches indépendantes** seulement : deux agents sur le même module produisent des conflits

Le goulot devient la **revue humaine**, pas la génération.

---

Comment un agent de code gère-t-il son contexte sur une longue session ?
?
- **Chercher plutôt que tout lire** : `grep`, lecture de passages ciblés
- **Compaction** : résumer l'historique quand le contexte se remplit ([[35-context-engineering|context engineering]])
- **Sessions courtes et ciblées** : une tâche par session, un nouveau contexte pour la suivante
- **Notes persistantes** : un fichier de progression que l'agent met à jour, pour reprendre après une coupure

Un contexte saturé de logs anciens fait baisser la qualité bien avant la limite.

---

Comment utiliser un agent de code en mode headless ?
?
Sans interface, depuis un script ou la CI : `claude -p "…"`, `codex exec "…"`. Usages : corriger un lint, mettre à jour des dépendances, trier des issues, proposer une PR à partir d'un ticket.

Règles : permissions **explicites et minimales**, sortie **structurée** (JSON) pour le script appelant, **budget** de tours et de coût, et jamais de données non fiables (titre d'issue) traitées comme instructions ([[106-securite-agents-code|sécurité des agents de code]]).

---

Que mesure SWE-bench et quelles sont ses limites ?
?
**SWE-bench** : résoudre de vraies issues GitHub de projets Python, jugé par les tests du dépôt. **SWE-bench Verified** (2024) en garde 500, validées par des humains.

Limites : Python seulement, dépôts populaires sans doute vus à l'entraînement (**contamination**), tâches plutôt courtes. Des variantes plus dures (SWE-bench Pro, multilingues) existent. Sur **son propre dépôt**, rien ne remplace un essai sur des tickets réels ([[146-choix-modeles|benchmarks]]).

---

Quelles tâches déléguer à un agent de code ?
?
- **Bien adaptées** : tâches **bien spécifiées et vérifiables** (bug avec reproduction, migration mécanique, tests à écrire, refactoring couvert par des tests)
- **À accompagner** : nouvelle fonctionnalité, avec plan validé et revue attentive
- **À garder** : choix d'architecture, code de sécurité sensible, zones sans tests où l'erreur est silencieuse

Critère simple : **pourrai-je vérifier le résultat plus vite que l'écrire ?**

---

Comment mesurer l'apport des agents de code dans une équipe ?
?
- **Débit** : PR fusionnées, délai entre ticket et mise en production
- **Qualité** : taux de retour arrière, bugs en production, part des PR d'agents rejetées en revue
- **Coût** : tokens par PR fusionnée, temps de revue humain
- **Perception** : enquêtes, mais à croiser avec les chiffres, car le gain ressenti peut différer du gain mesuré

Comparer sur des **tâches comparables**, avant et après, plutôt que sur des impressions.

---

## Mises en situation

Mise en situation : ton équipe adopte un agent de code, mais les PR produites sont énormes, mélangent plusieurs sujets et les reviewers les approuvent sans les lire. Que mets-tu en place ?
?
1. **Découper à la source** : une tâche par session, un plan validé avant l'implémentation
2. **Limiter la taille** : règle de PR courte, l'agent propose une série de PR plutôt qu'une seule
3. **Exiger la vérification** : tests ajoutés ou modifiés, CI verte, description de ce qui a été testé
4. **Relire en priorité** les diffs de tests et les zones sensibles, signalées par des règles de revue ([[106-securite-agents-code|PR d'agents]])
5. **Suivre** le taux de retours arrière des PR d'agents par rapport aux autres

**Piège** : juger l'outil sur le nombre de lignes produites.

---

Mise en situation : tu veux que l'agent de code mette à jour chaque semaine les dépendances d'une vingtaine de dépôts, sans intervention sauf en cas de problème. Comment l'organises-tu ?
?
1. **Job planifié en CI**, agent en mode headless, un dépôt et une branche par exécution
2. **Permissions minimales** : lecture du dépôt, écriture sur une branche dédiée, pas de secrets de production
3. **Critère de réussite** : build et tests verts, sinon l'agent tente une correction limitée à quelques tours
4. **PR systématique** avec le résumé des changements et des notes de version lues, jamais de fusion automatique des mises à jour majeures
5. **Rapport** : dépôts à jour, PR ouvertes, échecs à traiter par un humain

**Piège** : laisser l'agent fusionner seul, ou installer des paquets qu'il a « supposés » exister ([[106-securite-agents-code|slopsquatting]]).

---

## Connexions
- [[34-harness-plugins|Harness & plugins]] — l'outil qui exécute la boucle
- [[106-securite-agents-code|Sécurité des agents de code]] — les risques et leurs parades
- [[35-context-engineering|Context engineering]] — gérer une longue session
- [[36-orchestration-agents|Orchestration]] — sous-agents et parallélisme
- [[48-patterns-workflows-agentiques|Patterns de workflows]] — plan-and-execute appliqué au code
- [[96-evals-rag-agents|Évaluation des agents]] — environnements et pass^k
- [[147-leadership-technique-ia|Leadership technique]] — standards d'équipe pour les outils IA
- [[55-rl-agentique|RL agentique]] — comment les modèles apprennent à coder en agent
- [[00-moc-ai-engineering|MOC AI Engineering]]
