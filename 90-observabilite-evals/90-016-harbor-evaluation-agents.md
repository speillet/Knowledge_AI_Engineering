# Harbor : évaluer des agents en conteneurs — Flashcards
Tags: #flashcards #ai-engineering #evals #agents #benchmarks #containers
Vérifié le : 14 novembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.
<!-- summary: rôle de Harbor, composants d'une tâche, vérificateur et fichiers de récompense, trial ou job, agents oracle et nop, vérificateur partagé ou séparé, commande run et ses options, skills de job ou de tâche, provenance des skills, comparaison avec et sans skill, agrégation des récompenses, trials en erreur, calcul des récompenses invalides, pass@k, reward hacking, lint, check et analyze, réseau restreint, versions et re-vérification. -->


Qu'est-ce que Harbor ? <!--anki:6239333066353262363737633431323738373066316330666434613364326133-->
?
Un framework open source, sous licence Apache 2.0, créé par l'équipe de **Terminal-Bench** pour **évaluer et optimiser des agents et des modèles** dans des conteneurs. Il exécute des agents existants, comme Claude Code, Codex CLI ou OpenHands, ou un agent maison, sur des tâches isolées dont un vérificateur calcule la récompense.

C'est le harness officiel de Terminal-Bench 2.0 ; il intègre des benchmarks tiers comme SWE-bench et produit des trajectoires réutilisables en [[55-rl-agentique|RL agentique]]. Les essais tournent en local avec Docker, ou en parallèle chez des fournisseurs de sandboxes comme Daytona ou Modal.

---

Quels sont les composants d'une tâche Harbor ? <!--anki:6531363938333430363665383438303938616565346534643432343862363438-->
?
Un dossier autonome :
- **`instruction.md`** : la consigne donnée à l'agent ;
- **`task.toml`** : métadonnées, délais, ressources, réseau, mode du vérificateur ;
- **`environment/`** : la définition du sandbox, souvent un `Dockerfile` ;
- **`tests/test.sh`** : le vérificateur, qui écrit la récompense ;
- **`solution/solve.sh`**, facultatif : une solution de référence.

Une tâche ne dépend pas du framework : c'est un paquet versionné qu'un autre outil compatible peut exécuter. La traiter comme du logiciel — revue, tests, versions — évite qu'un défaut de tâche passe pour un échec d'agent.

---

Comment un vérificateur Harbor produit-il la récompense d'un essai ? <!--anki:3866306466343931396562353462636461626635366566343235656532666566-->
?
`tests/test.sh` s'exécute après l'agent et écrit un nombre dans **`/logs/verifier/reward.txt`**, ou des métriques nommées dans **`/logs/verifier/reward.json`**, prioritaire si les deux existent :

```bash
#!/bin/bash
set -euo pipefail
if pytest /tests/test_outputs.py; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
```

Utiliser des chemins absolus. Harbor efface ces fichiers au début de la vérification : un agent ne peut pas y déposer sa propre récompense. Le script peut aussi appeler un [[95-llm-as-judge|juge LLM]], par exemple avec le paquet `harbor-rewardkit`.

---

À ne pas confondre : trial et job dans Harbor ? <!--anki:6464323531366133323364643461353861373831363864656430376666653135-->
?
Un **trial** est **une tentative d'un agent sur une tâche** : démarrage du sandbox, exécution de l'agent, vérification, récompense et trajectoire. Un **job** est un **ensemble de trials** lancé par `harbor run` : il combine datasets, tâches, agents et modèles, et exécute les trials en parallèle.

Avec 30 tâches, deux agents et 5 tentatives par tâche, un job compte 300 trials. Les statistiques, comme la moyenne ou pass@k, se calculent dans le job, par agent, modèle et dataset. La **trajectoire** de chaque trial, au format ATIF, sert au débogage.

---

À quoi servent les agents oracle et nop dans Harbor ? <!--anki:3961323633656464376264363463623262306430376239363734313535383663-->
?
À **tester la tâche avant de tester un agent**. **`oracle`** exécute `solution/solve.sh` : il doit obtenir 1, sinon la tâche est insoluble ou le vérificateur rejette une bonne solution. **`nop`** ne fait rien : il doit obtenir 0, sinon le vérificateur accepte l'état de départ.

```bash
harbor run -p taches/ma-tache -a oracle
harbor run -p taches/ma-tache -a nop
```

Une tâche peut fournir plusieurs solutions de référence, choisies par une variable passée avec `--ae`. Un vérificateur qui n'accepte qu'une implémentation est **sur-ajusté** et pénalisera des agents corrects.

---

À ne pas confondre : vérificateur partagé et vérificateur séparé dans Harbor ? <!--anki:6663336334633962353863663432663739663937633135623836323136666233-->
?
**Partagé** (`environment_mode = "shared"`) : les tests tournent dans le conteneur de l'agent, qui a pu les lire ou modifier ce qu'ils inspectent. **Séparé** : un sandbox neuf, où Harbor copie seulement les **artefacts** déclarés dans `task.toml`.

```toml
artifacts = ["/app/output"]

[verifier]
environment_mode = "separate"
```

`harbor init` crée des tâches séparées par défaut. Limite : ce qui doit être vérifié doit exister sous forme de **fichiers** ; un processus en cours ou un état en mémoire doit être matérialisé, sinon le mode partagé reste nécessaire. Le mode séparé permet aussi de re-vérifier des trials existants.

---

Comment lancer un job d'évaluation avec Harbor ? <!--anki:3833616631323034643530323438363538313230633335343839376438336361-->
?
```bash
harbor run -d terminal-bench@2.0 -a claude-code \
  -m anthropic/claude-opus-5-5 -n 8 -k 5 -r 2
```
- `-d` : dataset du registre, `-p` pour un dossier local, `-t` pour une tâche ;
- `-a` et `-m` : agent et modèle ;
- `-n` : trials concurrents, 4 par défaut ;
- `-k` : tentatives par tâche, 1 par défaut ;
- `-r` : reprises après erreur, 0 par défaut.

`--env daytona` déplace les sandboxes chez un fournisseur pour monter en parallélisme. `--print-config` affiche la configuration : la versionner rend le job rejouable.

---

Comment Harbor fournit-il des skills à l'agent pendant un essai ? <!--anki:6637373038613239323238343433393562323438613530373237303066376230-->
?
Avec l'option répétable `--skill`, qui accepte un dossier local, `org/repo@ref` ou une URL GitHub en `/tree/<ref>/<chemin>` :

```bash
harbor run -p taches/ -a codex -m openai/<modele> \
  --skill ./skills/analyse-csv --skill mon-org/skills@v1.4
```

Pour chaque trial, Harbor copie chaque skill dans `/runtime/skills/<nom>` du sandbox, après le contrôle de santé et avant l'installation de l'agent. L'intégration l'enregistre ensuite à l'endroit natif : `$HOME/.agents/skills` pour Codex, `$CLAUDE_CONFIG_DIR/skills` pour Claude Code. Si deux skills portent le même nom de dossier, **la dernière gagne**.

---

À ne pas confondre : skills de tâche et skills de job dans Harbor ? <!--anki:3936326531326430653566323430653438646334303034376639323438363734-->
?
Les **skills de tâche** sont intégrées à l'image, par exemple `COPY skills/ /skills/` dans le `Dockerfile`, et déclarées par `environment.skills_dir` : tous les agents reçoivent les mêmes. Les **skills de job** viennent de `--skill` au lancement : on change de skill sans reconstruire la tâche.

Les skills de job sont copiées dans le `skills_dir` de la tâche, et une skill de job **remplace** la skill de tâche du même nom pour ce trial. Pour comparer avec et sans skill, ne pas mélanger les deux : une skill restée dans l'image contamine la condition « sans skill ».

---

Comment Harbor rend-il traçable la version d'une skill utilisée dans un job ? <!--anki:3665666433613337383539383465313939633862393836663061353166386537-->
?
Le **fichier de verrouillage du job** enregistre, pour chaque skill, son nom, sa source, un **digest SHA-256** de tous ses fichiers et, pour une skill Git, l'URL du dépôt et le **commit résolu**. Les skills Git sont mises en cache par commit dans `~/.cache/harbor/skills/`.

Une branche peut avancer après le job : le commit et le digest disent exactement quel contenu a produit les résultats. Comparer les digests de deux jobs avant d'attribuer un écart à « la skill » : si le contenu diffère, on compare peut-être deux versions sans le savoir.

---

Comment comparer un agent avec et sans skill dans Harbor ? <!--anki:3030323739396665306531353435336661663932393430393663313263313731-->
?
Deux jobs identiques, à la skill près :

```bash
harbor run -p taches/ -a claude-code -m anthropic/claude-opus-5-5 \
  -k 5 --job-name sans-skill
harbor run -p taches/ -a claude-code -m anthropic/claude-opus-5-5 \
  -k 5 --job-name avec-skill --skill ./skills/migration-schema
```

Garder tâches, agent, modèle, tentatives et environnement ; vérifier qu'aucune skill n'est déjà dans les images. Comparer **par tâche**, puis la moyenne, les récompenses valides et les tokens. `harbor view` montre dans les trajectoires si la skill a été chargée : non-déclenchement et skill inefficace ne se corrigent pas de la même façon ([[90-014-evaluation-skills-agents|évaluation des skills]]).

---

Comment Harbor agrège-t-il les récompenses d'un job ? <!--anki:3737663261373437636231373464396538643235363135303232366338366132-->
?
Par défaut, il fait la **moyenne** des récompenses ; pour un `reward.json` à plusieurs dimensions, une moyenne **par dimension**, où une dimension absente compte 0. Un `metric.py` placé dans le dataset remplace ce calcul : il lit un fichier JSONL de récompenses (`-i`) et écrit un objet JSON de métriques (`-o`).

La moyenne globale mélange des tâches de difficultés très différentes. Pour comparer deux conditions, regarder aussi les résultats **par tâche** et par domaine, ainsi que le nombre de récompenses valides de chaque côté ([[94-evals-methodologie|méthodologie des evals]]).

---

Que fait Harbor d'un trial qui se termine en erreur ? <!--anki:6332353832386265663962393434346261643139393166306464373131613136-->
?
Chaque type d'erreur a sa politique : reprendre ou non, vérifier ou non, compter ou non la récompense.
- **Délai de l'agent ou contexte dépassé** : vérifié, récompense **valide** ; c'est un échec de l'agent.
- **Sandbox qui ne démarre pas** : reprise, pas de vérification, récompense invalide.
- **Erreur d'API ou limite de débit** : reprise et vérification, mais récompense **invalide**.

Une récompense invalide sort du **numérateur et du dénominateur** de la moyenne. Les reprises se règlent avec `-r`, et `override_error_policy` modifie la politique d'un type d'erreur.

---

Calcul : un job compte 20 trials : 10 réussites et 6 échecs valides, plus 4 trials en erreur d'API à récompense invalide. Quelle moyenne Harbor rapporte-t-il, et quel serait le taux si ces 4 trials comptaient comme échecs ? <!--anki:3533313230643162643433613463393161356161393264313232386166623538-->
?
```text
Harbor : 10 / (10 + 6) = 0,625
erreurs comptées en échec : 10 / 20 = 0,50
```
Harbor rapporte **62,5 %**. L'exclusion est juste si les erreurs frappent au hasard. Si elles touchent surtout les tâches longues, qui font plus d'appels et rencontrent plus de limites de débit, elles retirent des tâches difficiles et gonflent le score. Avant de comparer deux conditions, vérifier qu'elles ont autant de récompenses valides et relancer les trials en erreur.

---

Quand Harbor calcule-t-il pass@k, et pour quelles valeurs de k ? <!--anki:3938313632666236356435363438623239653733323665666530313566393936-->
?
Seulement si chaque récompense est **binaire**, 0 ou 1, et à une seule dimension. Harbor applique par tâche l'estimateur sans biais de [[114-reproductibilite-variance|pass@k]], puis fait la moyenne sur les tâches.

Les valeurs de k sont les puissances de 2 à partir de 2 et les multiples de 5, jusqu'au **plus petit nombre d'essais valides** d'une tâche. Avec `-k 5` et aucune erreur : k ∈ {2, 4, 5}. Si une tâche n'a que 3 récompenses valides, seul pass@2 reste. Une récompense continue, comme 0,7, supprime pass@k.

---

Quels sont les trois types de reward hacking distingués par Harbor ? <!--anki:6362363631623462633662303432633362353062393038386462396430336530-->
?
- **Altération** (*tampering*) : l'agent perturbe la notation, par exemple en modifiant le vérificateur ou en pointant un lien symbolique vers la solution.
- **Triche** (*cheating*) : il obtient la réponse d'une source interdite, comme la solution du benchmark publiée en ligne.
- **Faille** (*loophole*) : il satisfait les tests sans résoudre le problème, par exemple en codant en dur les cas vérifiés.

Chaque type appelle sa parade : isoler le vérificateur, restreindre le réseau, renforcer les tests. Le même risque existe à l'entraînement ([[55-rl-agentique|reward hacking en RL]]).

---

À ne pas confondre : harbor lint, harbor check et harbor analyze ? <!--anki:6163373736353735656531333432376261353733323438386338383065653030-->
?
**`harbor lint`** contrôle statiquement la configuration d'une tâche : solution ou tests copiés dans l'image de l'agent, vérificateur partagé, image non épinglée par digest, conteneur privilégié.

**`harbor check`** confie à un agent la revue des sources de la tâche selon une grille, par défaut 11 critères inspirés de Terminal-Bench.

**`harbor analyze`** intervient **après** le job : un agent lit la tâche, les journaux et la trajectoire de chaque trial, puis signale les récompenses obtenues en trompant le vérificateur et les consignes trop floues. Les deux premiers précèdent les essais ; le troisième audite les résultats.

---

Comment Harbor limite-t-il la triche par accès réseau ? <!--anki:6236613738303436396239643463646138326461623637353861353431646539-->
?
Par `network_mode` dans `task.toml` : `public`, `allowlist` avec `allowed_hosts`, ou `no-network`, réglable séparément pour l'agent et le vérificateur.

```toml
[environment]
network_mode = "allowlist"
allowed_hosts = ["pypi.org"]
```

Quand le réseau est restreint, Harbor autorise automatiquement le point d'inférence déclaré par l'agent, ou le `base_url` configuré, et **désactive la recherche web intégrée** des agents qui en ont une. Pour limiter la conscience d'être évalué, chemins et variables visibles par l'agent portent des noms neutres.

---

Que se passe-t-il quand on change la version d'une tâche dans un dataset Harbor ? <!--anki:3135623836653661393034393438303461313634643336396264643061346331-->
?
Harbor applique le **versionnage sémantique** aux tâches :
- **correctif** : les trials existants sont réutilisés ;
- **mineure** : ils sont **re-vérifiés** avec le nouveau vérificateur ;
- **majeure** : ils sont **relancés**.

`harbor run -d <dataset>@<nouvelle-version> -a <agent> --diff <ancien-job>` applique ces règles. Corriger un vérificateur trop permissif coûte ainsi une re-vérification, pas un nouveau passage des agents, à condition d'utiliser un vérificateur séparé et des artefacts conservés.

---

## Mises en situation

Mise en situation : ton équipe veut savoir si sa skill interne de migration de schéma améliore vraiment Claude Code avant de la déployer à 200 développeurs. Comment organises-tu la mesure avec Harbor ? <!--anki:6130353530316336613139653434393762333465643432373764353434623537-->
?
1. **Construire 15 à 30 tâches** réalistes, cas limites compris, avec vérificateur séparé et solution de référence.
2. **Valider les tâches** : `harbor lint`, `oracle` à 1, `nop` à 0, et aucune fuite de la solution dans la skill.
3. **Lancer deux jobs appariés**, avec et sans `--skill`, 5 tentatives par tâche.
4. **Comparer par tâche** : réussite, récompenses valides, tokens, régressions.
5. **Lire les trajectoires** : skill chargée ou non, instructions suivies ou ignorées.
6. **Décider** selon un seuil fixé avant, en conservant le digest de la skill mesurée.

**Piège** : mesurer sur les tâches qui ont servi à écrire la skill.

---

Mise en situation : sur ton dataset Harbor interne, un nouvel agent passe de 55 % à 94 % de réussite en une version. Avant de célébrer, que vérifies-tu ? <!--anki:6362666337626132363061343439613962613933383538373665626230636439-->
?
1. **Lire des trajectoires réussies** avec `harbor view` : l'agent résout-il la tâche ou contourne-t-il les tests ?
2. **Lancer `harbor analyze`** sur le job pour signaler altérations, triches et failles.
3. **Auditer les tâches** avec `harbor lint` : vérificateur partagé, tests dans l'image, réseau ouvert.
4. **Durcir** : vérificateur séparé, agent non root, liste blanche réseau, plusieurs solutions de référence.
5. **Corriger et versionner** les tâches, puis re-vérifier avec `--diff`.

**Piège** : publier le score avant d'avoir lu une seule trajectoire.

---

Mise en situation : tu découvres que le vérificateur d'une tâche acceptait un fichier de sortie vide, alors que 2 000 trials ont déjà été notés sur ce dataset. Comment corriges-tu sans tout relancer ? <!--anki:3637613938643835316637363433306539623232323262316438313863666433-->
?
1. **Reproduire** le défaut : un fichier de sortie vide doit obtenir 0 avec le vérificateur corrigé.
2. **Corriger** `tests/` et ajouter un test du vérificateur, exclu du sandbox par `.harborignore`.
3. **Monter la version mineure** de la tâche : les trials existants seront re-vérifiés, pas relancés.
4. **Re-vérifier** avec `--diff` sur l'ancien job, ce qui suppose un vérificateur séparé et des artefacts conservés.
5. **Publier** l'écart avant et après correction, et signaler les classements concernés.

**Piège** : corriger sans changer de version, ce qui mélange anciennes et nouvelles notes.

---

## Sources

- [Harbor — dépôt et README, version 0.26.0](https://github.com/harbor-framework/harbor)
- [Harbor — concepts](https://docs.harborframework.com/core-concepts)
- [Harbor — format des tâches](https://docs.harborframework.com/tasks/overview), [vérificateur](https://docs.harborframework.com/tasks/verifier) et [solution](https://docs.harborframework.com/tasks/solution)
- [Harbor — lancer un job](https://docs.harborframework.com/jobs/run-a-job), [skills](https://docs.harborframework.com/jobs/skills) et [skills de tâche](https://docs.harborframework.com/tasks/skills)
- [Harbor — classification des erreurs](https://docs.harborframework.com/jobs/error-classification) et [métriques](https://docs.harborframework.com/datasets/metrics)
- [Harbor — Cracking down on reward hacking, 28 octobre 2026](https://docs.harborframework.com/news/reward-hacking)

## Connexions
- [[90-014-evaluation-skills-agents|Évaluer des skills d'agent]] — le protocole avec et sans skill que Harbor exécute
- [[90-015-agent-skills-format-skills-ref|Agent Skills & skills-ref]] — valider le format avant d'injecter une skill
- [[96-evals-rag-agents|Évaluation des RAG & des agents]] — environnements d'eval et vérification de l'état final
- [[114-reproductibilite-variance|Reproductibilité & variance]] — pass@k et essais répétés
- [[55-rl-agentique|RL agentique]] — environnements d'entraînement et reward hacking
- [[49-agents-de-code|Agents de code]] — benchmarks d'agents de code et leurs limites
- [[95-llm-as-judge|LLM-as-a-judge]] — les vérificateurs qui notent avec un modèle
- [[00-moc-ai-engineering|MOC AI Engineering]]
