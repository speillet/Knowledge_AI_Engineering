# Knowledge Vault — AI Engineering

Un vault [Obsidian](https://obsidian.md) de **fiches de révision (flashcards) en français** qui couvre les compétences clés de l'**AI Engineering**. Le parcours va du choix entre règles, ML classique et LLM jusqu'à leur mise en production et leur sécurisation, avec les fondations en données et systèmes distribués nécessaires à leur fiabilité.

Chaque fiche traite **un concept** en 8 à 34 cartes question/réponse, une quinzaine en moyenne, et se termine par des **mises en situation** : des cas concrets à diagnostiquer, concevoir ou arbitrer. Les fiches sont reliées entre elles par des liens, pour qu'on puisse passer d'un sujet à ses voisins, et elles se révisent en **répétition espacée**.

**État au 9 octobre 2026** : 137 fiches et 2 010 cartes, réparties en 17 sections, dont 317 mises en situation et 162 cartes « à ne pas confondre ».

---

## Structure du repo

```text
Knowledge_AI_Engineering/
├── README.md
├── docs/                       # bilans de revue et documentation de maintenance
├── .obsidian/                   # configuration Obsidian
├── .claude/skills/              # skills Claude Code versionnés (grilling, grill-me)
├── scripts/lint_flashcards.py   # vérification des conventions + statistiques
├── scripts/export_anki.py       # export en paquet Anki (.apkg) pour AnkiDroid
├── scripts/assign_card_ids.py   # identifiants permanents des nouvelles cartes
├── scripts/sr_plugin.py         # lecture des fiches par le plugin Spaced Repetition, vérifiée par le lint
├── scripts/retired_cards.json   # cartes retirées du vault, à supprimer d'Anki
├── scripts/sync_catalog.py      # génération des sommaires README et MOC
├── scripts/sections.json        # titres et introductions des sections
├── tests/                       # tests du parseur, du lint, des sommaires et de l’export
├── scripts/requirements.txt     # dépendances de l'export Anki
├── .githooks/pre-commit         # lance le lint avant chaque commit
├── .github/workflows/           # lint en CI, et export Anki publié en release
├── 00-moc-ai-engineering.md     # carte racine : parcours de lecture, parcours agentique, sommaire
├── 10-prompt-engineering/        # techniques, optimisation automatique (DSPy), prompts en production
├── 20-rag/                      # RAG, graphes, chunking, text-to-SQL, agents de recherche
├── 30-agents/                   # boucle, outils, MCP, contexte, multi-agents, plateformes, mémoire
├── 40-automatisation/           # workflows, LangChain, LangGraph, CrewAI, patterns, agents de code
├── 50-fine-tuning/              # fine-tuning, alignement, distillation, distribué, RL, diagnostic
├── 60-inference-llm/            # KV cache, optimisations, sampling, quantization, roofline
├── 70-containers-infra/         # contient son propre index : 00-index.md
├── 80-api-layer-routing/        # gateway, routing, ingress, streaming, protocoles agentiques
├── 90-observabilite-evals/      # traces, monitoring, evals, juges, débogage, statistiques
├── 100-securite-guardrails/     # guardrails, menaces et défenses des agents, MCP, DevSecOps
├── 110-mlops-cicd/              # LLMOps, CI/CD, drift, variance, gouvernance, SRE et incidents
├── 120-couts-finops/            # coûts d'inférence, FinOps, caching
├── 130-fondamentaux-llm/         # Transformer, tokenisation, embeddings, MoE, raisonnement
├── 140-system-design-produit/    # system design, fiabilité, UX, batch, idempotence, transactions
├── 150-donnees-conformite/       # curation, conformité, contrats, ingestion, données temporelles
├── 160-multimodal-edge/          # VLM, parsing de documents, voix, LLM locaux, computer use
└── 170-ml-classique/            # validation, calibration, ranking, prévision, anomalies, explicabilité, causalité
```

- Chaque **section** est un dossier numéroté par dizaine (`20-rag`, `30-agents`…).
- Chaque **fiche** porte un numéro qui reprend celui de sa section : `21-rag-fondamentaux.md` et `22-rag-avance.md` sont dans `20-rag/`.
- Exception : la section conteneurs garde sa propre numérotation, de `00-index.md` à `13-apptainer-inference-hpc.md`.
- Les noms existants restent stables. **Une section peut dépasser neuf fiches** : après `39-memoire-agents.md`, utiliser `30-010-nouveau-sujet.md`, puis `30-011-autre-sujet.md`, dans `30-agents/`. Le préfixe désigne la section, le second nombre son rang. Les sommaires trient ensemble les deux conventions ; choisir la section selon le sujet.
- Le point d'entrée est le **MOC** (Map of Content), [00-moc-ai-engineering.md](00-moc-ai-engineering.md).

---

## Comment l'utiliser

### 1. Ouvrir le vault

1. Installer [Obsidian](https://obsidian.md).
2. Choisir **Open folder as vault** et sélectionner le dossier du dépôt (`Knowledge_AI_Engineering` après un `git clone`).
3. Ouvrir [00-moc-ai-engineering.md](00-moc-ai-engineering.md).

### 2. Lire et naviguer

- **Apprendre avant de multiplier les révisions** : le [guide d'apprentissage](docs/apprendre-avec-les-cartes.md) propose un démarrage progressif, des critères pour se noter et des exercices pour vérifier le transfert. Le [bilan du 9 octobre](docs/revue-apprentissage-2026-10-09.md) détaille les corrections pédagogiques et les nouvelles cartes d'application.
- **Suivre le parcours de lecture** du MOC, qui va dans cet ordre : ML classique et validation, fondamentaux LLM (prérequis), prompt engineering, RAG, agents, automatisation et frameworks d'agents, fine-tuning, inférence, conteneurs, API layer, observabilité, sécurité, MLOps & CI/CD, coûts & FinOps, données & conformité, multimodal & edge, puis system design & produit, qui assemble le tout. Le MOC propose aussi un **parcours AI Engineer agentique**, qui enchaîne en 8 étapes les fiches sur les agents réparties dans plusieurs sections.
- **Rebondir entre les concepts** : chaque fiche se termine par une section `Connexions` qui explique pourquoi les fiches liées sont liées. Ces liens sont **réciproques** : si A cite B, B cite A. Des liens apparaissent aussi dans les réponses elles-mêmes.
- **Compléter les fondations senior** : le parcours dédié du MOC relie choix et validation des modèles, contrats et ingestion des données, puis idempotence et transactions. Le [bilan des trois priorités](docs/fondations-senior-2026-10-06.md) détaille les sept fiches ajoutées et leur validation.
- **Mettre en pratique le niveau senior** : le [bilan de pertinence du 7 octobre](docs/pertinence-parcours-senior-2026-10-07.md) distingue socle commun et spécialisations, puis propose des ateliers avec livrables : décision expérimentale, calibration, diagnostic d’entraînement, incident et transmission. Le parcours correspondant figure dans le MOC.
- **Élargir les compétences prédictives** : le [bilan du 8 octobre](docs/nouvelles-competences-ia-2026-10-08.md) présente cinq nouvelles fiches sur la recommandation, la prévision temporelle, les anomalies, l’explicabilité et la causalité, avec des exercices ciblés.
- **Voir l'ensemble** : la **vue graphe** d'Obsidian montre comment les concepts s'articulent, et le panneau **Backlinks** liste les fiches qui citent la fiche ouverte.
- **Maîtriser les performances d’inférence** : l’[audit du 8 octobre](docs/audit-inference-llm-2026-10-08.md) relie métriques, benchmarks, capacité, optimisations et coût par tâche utile, avec une matrice de couverture et quatre ateliers.

### 3. Réviser en répétition espacée

Les fiches suivent la syntaxe du plugin communautaire **Spaced Repetition**. Il n'est pas installé par défaut :

1. **Settings → Community plugins** : activer les plugins communautaires, puis chercher et installer **Spaced Repetition**.
2. Le plugin retrouve automatiquement les fiches grâce au tag `#flashcards` qui figure en ligne 2 de chacune.
3. Dans les réglages du plugin :
   - **Separator for multiline flashcards** : garder `?` ;
   - **Characters denoting the end of clozes and multiline flashcards** : saisir `---`. **Indispensable** : sans ce réglage, chaque réponse s'arrête à sa première ligne vide ;
   - **Convert folders to decks and subdecks** : activer, pour obtenir un paquet par section ;
   - **Show context in cards** : activer, pour voir le titre de la fiche au-dessus de la question.
4. Lancer une révision avec l'icône du plugin dans la barre latérale, ou depuis la palette de commandes. La palette permet aussi de ne réviser que la note ouverte.

> Le plugin enregistre la planification des révisions **dans les fiches elles-mêmes**, sous forme de commentaires `<!--SR:...-->` placés après chaque carte. Si le vault est versionné avec git, ces commentaires apparaîtront dans les diffs.

### 4. Réviser sur Android avec Anki

À chaque push sur `main`, la CI génère un paquet Anki de toutes les fiches et le publie à une adresse fixe :

**https://github.com/speillet/Knowledge_AI_Engineering/releases/download/anki/ai-engineering.apkg**

1. Installer **AnkiDroid**, gratuit, depuis le Play Store ou F-Droid.
2. Ouvrir l'adresse ci-dessus sur le téléphone, puis ouvrir le fichier téléchargé avec AnkiDroid : il s'importe dans le paquet **AI Engineering**, rangé par section puis par fiche.
3. **Mettre à jour** : retélécharger le fichier et le réimporter. Chaque carte possède un identifiant permanent `<!--anki:…-->` : les cartes existantes sont mises à jour et gardent leur progression, même après reformulation de la question ou renommage du fichier.
   - Conserver ce commentaire lors d’une correction ou d’un déplacement. Pour créer une **nouvelle carte** par copie, retirer uniquement son identifiant, puis lancer `python3 scripts/assign_card_ids.py`.
   - Une carte supprimée du vault n'est pas supprimée d'Anki par le réimport. Elle est donc republiée **suspendue**, avec le tag `retired` : dans AnkiDroid, chercher `tag:retired`, tout sélectionner, puis **Supprimer**.
4. **Réviser un seul type de carte** avec un paquet filtré (menu **Créer un paquet filtré**) :
   - `tag:type::situation` : les mises en situation ;
   - `tag:type::confusion` : les cartes « à ne pas confondre » ;
   - `tag:type::calcul` : les ordres de grandeur ;
   - `tag:section::20-rag` : une seule section.
5. Pour retrouver la même progression sur ordinateur, synchroniser AnkiDroid avec un compte **AnkiWeb**.

> La progression Anki et celle du plugin Obsidian sont **indépendantes** : une carte révisée sur le téléphone ne l'est pas dans Obsidian, et inversement.

Pour générer le paquet en local :

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r scripts/requirements.txt
python3 scripts/export_anki.py      # écrit dist/ai-engineering.apkg
```

### Sans Obsidian

Les fiches sont du Markdown simple et se lisent dans n'importe quel éditeur. Seuls les liens au format `[[...]]` ne sont pas cliquables en dehors d'Obsidian.

---

## Format d'une fiche

```markdown
# Tool calling — Flashcards
Tags: #flashcards #ai-engineering #agents #tool-calling #llm
<!-- summary: Déclaration, exécution et validation des appels d’outils. -->


Qu'est-ce que le tool calling ?
?
Le **tool calling** permet au modèle de demander une opération en produisant un nom d'outil et des arguments structurés. L'application valide la demande, exécute la fonction autorisée et renvoie son résultat au modèle pour qu'il poursuive la tâche.

Par exemple, `statut_commande(id)` consulte une source métier avant la réponse au client. Un appel conforme au schéma ne garantit ni des arguments corrects ni une action autorisée : ces contrôles restent dans l'application.

---

Le modèle exécute-t-il lui-même les outils ?
?
**Non.** Le modèle produit une demande ; le [[34-harness-plugins|harness]] décide si elle est autorisée et lance l'outil. Il gère aussi les arguments invalides, les délais et les erreurs, puis transmet une observation au modèle.

Cette séparation permet de limiter les ressources accessibles et les effets possibles. Une instruction dans le prompt ne remplace pas un contrôle de permission au moment de l'exécution.

---

## Mises en situation

Mise en situation : ton agent dispose de 40 outils et se trompe souvent d'outil. Comment améliores-tu la situation ?
?
1. **Réduire le choix** : n'exposer que les outils utiles à la tâche en cours.
2. **Soigner les descriptions** : nom explicite, cas d'usage, ce que l'outil ne fait pas.
3. **Vérifier les arguments** : utiliser des schémas précis et des erreurs qui permettent de corriger l'appel.
4. **Mesurer le résultat** : rejouer des tâches représentatives et comparer choix d'outil, réussite et nombre d'appels.

**Piège** : ajouter un outil supplémentaire pour corriger les erreurs des précédents.

---

## Connexions
- [[31-agents-fondamentaux|Agents]] — la boucle qui consomme les outils
- [[00-moc-ai-engineering|MOC AI Engineering]]
```

Cet exemple montre une fiche avant attribution des identifiants permanents. Lancer `python3 scripts/assign_card_ids.py` après sa création ; conserver ensuite les identifiants lors des reformulations.

Les conventions à respecter :

- **Pas de frontmatter YAML.** Les tags sont écrits en texte sur la ligne 2.
- **Une carte** = la question, puis une ligne contenant seulement `?`, puis la réponse. Les cartes sont séparées par `---`.
- **Des réponses autonomes et suffisamment expliquées** : commencer par la réponse directe, puis expliquer le mécanisme, donner un exemple ou préciser les limites utiles. Mettre les termes clés en gras. Accompagner les commandes, calculs et schémas d'une explication de leurs hypothèses et de leur interprétation ; un bloc de code seul ne suffit pas.
- **Une section `## Mises en situation`** avant les connexions : 2 cartes (3 pour les fiches avancées) dont la question commence par `Mise en situation :`, tient en un seul paragraphe et décrit un cas concret. La réponse déroule une **démarche en 3 à 6 étapes** et peut finir par un **piège** à éviter.
- **Une section `## Connexions`** à la fin, dont le dernier lien renvoie toujours au MOC. Chaque lien a une raison courte, et il est **réciproque** : la fiche citée cite en retour.
- **Une question ciblée, une réponse développée** : conserver une notion principale par carte, sans imposer une réponse télégraphique. Au-delà de 5 éléments, une liste se découpe en sous-cartes thématiques dont la question donne un indice. La longueur est un repère de lisibilité, pas une mesure de qualité : éviter les ajouts qui ne font que répéter la question.
- **Des cartes « À ne pas confondre : X et Y ? »** pour les notions que l'on mélange (OCI et CRI, tag et digest, routing et fallback, rappel et précision, few-shot et fine-tuning…). On n'écrit pas « Quelle différence entre X et Y ? » : le format unique permet de toutes les retrouver par une recherche.
- **Des cartes de raisonnement** plutôt que des définitions seules : « Quand ne pas… ? », « Que se passe-t-il si… ? », et des cartes **« Calcul : … »** qui font poser un ordre de grandeur (VRAM, débit, coût, taille d'échantillon).
- **Une question qui se comprend seule** : en révision, les cartes sont mélangées. On nomme le sujet (« Qu'est-ce qu'un thread dans LangGraph ? », pas « Qu'est-ce qu'un thread ? ») et on évite « Et X ? » ou « Comment fonctionne-t-elle ? », qui supposent la carte précédente.
- **Un calcul résoluble avant de lire la réponse** : fournir dans le recto les données, unités, périmètre et hypothèses nécessaires, sauf si leur rappel est explicitement demandé. Annoncer les tarifs fictifs et les approximations. Le verso montre la formule, le résultat et ce qu'il permet réellement de conclure.
- **Un critère de réussite identifiable** : préciser ce qu'il faut expliquer, comparer, calculer ou décider. Éviter les questions qui présentent comme universelle une règle conditionnelle. Les exemples et limites du verso soutiennent la compréhension ; ils ne doivent pas devenir une liste implicite à réciter. Le [guide d'apprentissage](docs/apprendre-avec-les-cartes.md) précise comment évaluer chaque type de carte.
- **Pas de liste de produits à réciter** : « Quels outils de parsing connaître ? » se note mal et se périme vite. On pose plutôt un choix : « Quel outil de parsing pour des scans en volume, et lequel pour des données confidentielles ? ».
- **Une idée par carte** : si une réponse enchaîne deux sujets (un mécanisme puis une liste de produits, deux incidents), on la découpe. Une carte atomique se note honnêtement en révision.
- **Des repères chiffrés** et des **exemples exécutables** (commandes, configurations, extraits de code) plutôt que des formulations abstraites.
- **Une ligne `Vérifié le : …`** juste après les tags, sur les fiches qui citent des produits, des versions ou des textes réglementaires. Une section `## Sources`, placée avant `## Connexions`, doit contenir les références primaires utilisées : documentation officielle, spécification versionnée, article des auteurs ou texte réglementaire. Ajouter une référence ne justifie pas à lui seul de changer la date de vérification.
- **Un commentaire `<!-- summary: … -->`** après les tags et la date éventuelle, **suivi de deux lignes vides** : il alimente le catalogue du README. Les titres des fiches alimentent les deux sommaires.
- **Un identifiant `<!--anki:…-->` par carte, en fin de question** (`Qu'est-ce que le RAG ? <!--anki:…-->`), généré par le script dédié. Il est invisible à la lecture et exclu de l’export. Les identifiants historiques ont été conservés lors de la migration. Une reformulation garde l'identifiant ; une question qui change de sens en reçoit un nouveau.
- **Pas de commentaire HTML en début de ligne dans une fiche**, hors `<!--SR:` : le plugin Spaced Repetition saute la ligne qui suit un tel commentaire. Un identifiant placé seul sur sa ligne lui faisait perdre la réponse ; c'est pour cela que le résumé est suivi de deux lignes vides. Le lint rejoue la lecture du plugin (`scripts/sr_plugin.py`) et signale toute carte qu'il lirait autrement que l'export Anki.
- **Supprimer une carte** : retirer le bloc de la fiche et reporter son identifiant dans `scripts/retired_cards.json`, avec la question et la raison (`{"id": "…", "question": "…", "raison": "doublon de 95-llm-as-judge"}`). L'export la republie suspendue, avec le tag `retired`.
- Dans un index comportant une introduction, placer `---` puis `## Cartes` avant la première question ; le parseur ignore ainsi le sommaire et le texte introductif.

## Ajouter une fiche

1. Choisir la section et le prochain numéro libre, puis nommer le fichier en kebab-case, par exemple `28-rag-multimodal.md`. Pour dépasser neuf fiches, utiliser la numérotation étendue décrite dans [Structure du repo](#structure-du-repo).
2. **Le nom de fichier doit être unique dans tout le vault**, car Obsidian résout les liens `[[...]]` par nom de fichier, pas par chemin.
3. Rédiger les cartes au format ci-dessus, renseigner le commentaire `summary` et les sources si la fiche est datée, puis lancer `python3 scripts/assign_card_ids.py`.
4. Lancer `python3 scripts/sync_catalog.py` pour régénérer les catalogues du MOC et du README. Pour une nouvelle section, renseigner d’abord `scripts/sections.json`. Les parcours de lecture restent éditoriaux. Mettre à jour les chiffres avec `python3 scripts/lint_flashcards.py --update-readme`.
5. Ajouter des liens dans les deux sens : la nouvelle fiche cite ses voisines, et les voisines la citent dans leur section `Connexions`. Relier aussi les fiches qui **mentionnent** la notion traitée sans la lier. Le lint signale tout lien sans retour.
6. Lancer `python3 scripts/lint_flashcards.py` : il signale les liens morts, les fiches absentes du MOC ou du README, les fiches peu reliées et les écarts de format (voir [Maintenance](#maintenance)).

---

## Concepts couverts

La stack décrite par le vault, du haut vers le bas :

```text
App / Agent
    ↓
Plateforme d'agents (runtime, sandbox, gateway d'outils MCP, identité, politiques)
    ↓
Gateway LLM (Ingress → LiteLLM : auth, routing, budgets)
    ↓
Serveur d'inférence (vLLM/SGLang/TensorRT-LLM, KV cache, batching, quantization)
    ↓
Conteneur + GPU (Docker/K8s/Apptainer)
```

Trois sujets traversent toute la stack : l'**observabilité** (traces, métriques, evals), la **sécurité** (injection, moindre privilège, sandbox, DevSecOps) et les **coûts** (FinOps).

<!-- catalog:begin -->

### 10 — Prompt engineering

- [Prompt engineering avancé](10-prompt-engineering/11-prompt-engineering-avance.md) : system prompt et user prompt, few-shot, few-shot ou fine-tuning, chain-of-thought (coût, balises), self-consistency et ses limites, délimiteurs, décomposition en appels, meta-prompting, prompts versionnés comme du code, anti-patterns.
- [Optimisation automatique de prompts (DSPy)](10-prompt-engineering/12-optimisation-automatique-prompts.md) : meta-prompting ou optimisation guidée par une métrique, DSPy (signatures, modules, optimiseurs BootstrapFewShot, MIPROv2, GEPA), APE, OPRO, TextGrad, quand l'utiliser ou non, sur-apprentissage, transfert entre modèles, optimisation de prompts ou fine-tuning.
- [Prompts en production](10-prompt-engineering/13-prompts-production.md) : briques d'un prompt, placement des longs documents, consignes motivées, limites des rôles, prompter un modèle de raisonnement, templates et données utilisateur, registre et versioning, prompt dans le code ou dans un registre, portabilité entre modèles, langue, contrôle de la longueur.

### 20 — RAG

- [RAG — Fondamentaux](20-rag/21-rag-fondamentaux.md) : RAG ou fine-tuning, pipeline d'ingestion et de requête, stratégies de chunking, embeddings, bases vectorielles (HNSW, pgvector, Qdrant), top-k, grounding et citations, recall@k, quand ne pas faire de RAG.
- [RAG — Avancé](20-rag/22-rag-avance.md) : recherche hybride (BM25, RRF), reranking, query rewriting, HyDE et ses limites, filtrage par métadonnées et ACL, GraphRAG, agentic RAG, « lost in the middle », problèmes de production (fraîcheur, droits, ré-indexation).
- [Knowledge graphs & ontologies](20-rag/23-knowledge-graphs-ontologies.md) : triplets, RDF ou property graph (Cypher, GQL), ontologie et taxonomie, extraction par LLM sous schéma, résolution d'entités, graphe ou vecteurs, GraphRAG local et global, Text2Cypher, context graph, coûts.
- [Cognee](20-rag/24-cognee.md) : mémoire d'agent en knowledge graph, opérations remember, recall, improve et forget, mémoire permanente ou de session, stratégies de recherche, ontologie OWL, intégrations (plugin, MCP), limites.
- [Chunking avancé & contextual retrieval](20-rag/25-chunking-contextual-retrieval.md) : chunks sans contexte, contextual retrieval (gain, coût, prompt caching), late chunking, taille des chunks, small-to-big, chunking sémantique et par propositions, fil d'Ariane et métadonnées, comparaison de stratégies au recall@k.
- [Text-to-SQL & données structurées](20-rag/26-text-to-sql.md) : text-to-SQL ou RAG, contenu du prompt, schema linking, couche sémantique, sécurisation de l'exécution, boucle de correction, exact match ou execution accuracy, benchmarks (Spider, BIRD, Spider 2.0), questions ambiguës.
- [Agents de recherche (deep research)](20-rag/27-agents-recherche-deep-research.md) : RAG ou agent de recherche, boucle de recherche, sous-agents parallèles, outils de recherche, citations fiables, risques (sources, injection, biais), évaluation (couverture, BrowseComp), calcul du coût d'un rapport, quand ne pas l'utiliser.

### 30 — Agents

- [Fondamentaux des agents](30-agents/31-agents-fondamentaux.md) : workflow ou agent, pattern ReAct, composants d'un agent minimal, trois formes de human-in-the-loop, risques et parades, ordres de grandeur de coût, conditions d'arrêt.
- [Tool calling](30-agents/32-tool-calling.md) : déclaration par JSON Schema, exécution contrôlée par l'application, boucle d'appel, parallel tool calls, tool calling ou MCP, erreurs d'outil actionnables, bonne et mauvaise description d'outil, validité syntaxique et sémantique des arguments.
- [MCP — Model Context Protocol](30-agents/33-mcp.md) : problème M×N, host, client et serveur, tools, resources et prompts, transports stdio et HTTP, spec sans état 2026-07-28, serveur MCP ou API REST, risques.
- [Harness & plugins](30-agents/34-harness-plugins.md) : rôle du harness, plugins, skills, hooks, permissions, sandbox, fichiers mémoire.
- [Context engineering](30-agents/35-context-engineering.md) : le contexte comme budget, context rot, compaction, sous-agents, prompt caching, contexte chargé au besoin (just-in-time).
- [Orchestration multi-agents](30-agents/36-orchestration-agents.md) : orchestrator-workers, supervisor, handoffs, evaluator-optimizer, état partagé, coût du multi-agent, protocole A2A.
- [Frameworks d'agents](30-agents/37-frameworks-agents.md) : LangChain, LangGraph, CrewAI, Google ADK, OpenAI Agents SDK, Claude Agent SDK, LlamaIndex, framework ou code maison.
- [Plateformes d'agents](30-agents/38-plateformes-agents.md) : différence avec un framework, briques, niveaux d'abstraction (API, runtime, harness managé), offres cloud et des fournisseurs de modèles, open source, runtime et double texting, sandbox et services de sandbox, gateway d'outils, registre, identité, agent délégué ou autonome, mémoire, observabilité, evals, protocoles (MCP, A2A), build ou buy. La suite, niveau senior, est la fiche 115 de la section 110.
- [Mémoire des agents](30-agents/39-memoire-agents.md) : mémoire de travail, sémantique, épisodique et procédurale, thread ou long terme, écriture pendant ou après la conversation, consolidation, score de rappel, réflexion, faits qui changent, stockage, Letta, outils, risques, évaluation, mémoire d'agent ou RAG, quand ne pas donner de mémoire long terme.

### 40 — Automatisation & frameworks d'agents

Automatiser des processus, soit avec des outils de workflow, soit avec des agents écrits en code. Chaque framework a deux fiches : ses bases, puis son usage avancé ou en production.

- [Automatisation code & no-code](40-automatisation/41-automatisation-code-nocode.md) : n8n, triggers, Zapier et Make, Airflow, Prefect et Temporal, durable execution, limites du no-code.
- [LangChain — Fondamentaux](40-automatisation/42-langchain-fondamentaux.md) : paquets de la v1, `init_chat_model`, messages, outils `@tool` et `bind_tools`, sorties structurées, Runnables et LCEL, briques RAG, LangSmith.
- [LangChain — Agents & middleware](40-automatisation/43-langchain-agents.md) : `create_agent`, mémoire par checkpointer et `thread_id`, `response_format`, hooks de middleware, middlewares fournis (human-in-the-loop, résumé, fallback, limites), runtime context, Deep Agents.
- [LangGraph — Fondamentaux](40-automatisation/44-langgraph-fondamentaux.md) : `StateGraph`, state et reducers, `MessagesState`, nodes et edges conditionnelles, boucle ReAct en graphe, super-steps, `Send` (map-reduce), `Command`, Functional API.
- [LangGraph — Production (persistance, HITL, multi-agents)](40-automatisation/45-langgraph-production.md) : checkpointers, threads, `interrupt` et `Command(resume=...)`, time travel, Store long terme, durable execution, streaming, subgraphs, patterns multi-agents, déploiement.
- [CrewAI — Crews](40-automatisation/46-crewai-crews.md) : agents (role, goal, backstory), tâches, process séquentiel ou hiérarchique, délégation, sorties structurées, guardrails de tâche, LLM et outils, mémoire unifiée, structure d'un projet.
- [CrewAI — Flows](40-automatisation/47-crewai-flows.md) : `@start`, `@listen`, `@router`, état structuré, `@persist`, `@human_feedback`, mémoire, CLI, crew ou flow, Flows ou LangGraph.
- [Patterns de workflows agentiques](40-automatisation/48-patterns-workflows-agentiques.md) : prompt chaining, routing, parallélisation (sectioning, voting), evaluator-optimizer, plan-and-execute ou ReAct, Reflexion, calcul de fiabilité d'une chaîne, workflow ou agent, implémentation sans framework.
- [Agents de code : usage & intégration](40-automatisation/49-agents-de-code.md) : ACI (SWE-agent), boucle pilotée par les tests, `CLAUDE.md` et `AGENTS.md`, mode plan, worktrees et sous-agents, gestion du contexte, mode headless, SWE-bench et ses limites, tâches à déléguer, mesure de l'apport.

### 50 — Fine-tuning

- [Fine-tuning & adaptation de modèles](50-fine-tuning/51-fine-tuning-adaptation.md) : quand fine-tuner, SFT, full fine-tuning ou PEFT, LoRA, QLoRA, RLHF, DPO, distillation, multi-LoRA (exemple vLLM), catastrophic forgetting et parades.
- [Post-training & alignement](50-fine-tuning/52-post-training-alignement.md) : étapes du RLHF, pénalité KL, reward hacking, DPO et variantes, GRPO, RLVR, RLAIF et Constitutional AI, jeux de préférences, taxe d'alignement, reward model ou vérificateur, quand faire soi-même du DPO ou du RL.
- [Données synthétiques & distillation](50-fine-tuning/53-donnees-synthetiques-distillation.md) : génération variée, filtrage, model collapse, distillation sur les sorties ou sur les logits, distillation du raisonnement, contraintes juridiques, projet de distillation, jeux d'eval synthétiques.
- [Entraînement distribué](50-fine-tuning/54-entrainement-distribue.md) : calcul de la mémoire d'un fine-tuning 7B avec Adam, data ou model parallelism, DDP, ZeRO et FSDP, tensor et pipeline parallelism, parallélisme 3D, gradient checkpointing, accumulation de gradients, précision mixte BF16, réseau, pannes et checkpoints.
- [RL agentique & environnements d'entraînement](50-fine-tuning/55-rl-agentique.md) : RL sur trajectoires multi-tours, RLVR ou RL agentique, environnements d'entraînement, récompense de résultat ou de processus, reward hacking des agents, SFT sur trajectoires, GRPO, curriculum de tâches, outils (verl, OpenRLHF, TRL), quand une équipe produit doit s'y lancer.
- [Optimisation & diagnostic d'entraînement](50-fine-tuning/56-optimisation-diagnostic-entrainement.md) : perte et métrique métier, rétropropagation, learning rate, AdamW, courbes d'apprentissage, micro-lot de diagnostic, accumulation normalisée, clipping, précision mixte, modes PyTorch et masquage des labels.

### 60 — Inférence LLM

Comprendre les mécanismes du serving, mesurer qualité et SLO, tester la capacité sous charge et optimiser le débit utile, la mémoire et le coût.

- [KV cache & attention](60-inference-llm/61-kv-cache-attention.md) : rôle et taille du cache, KV cache, prefix caching et prompt caching, calcul de la concurrence sur un H100, PagedAttention et continuous batching, KV cache en FP8, coût des contextes longs.
- [Optimisations d'inférence](60-inference-llm/62-optimisations-inference.md) : prefill et decode, continuous batching, quantization (AWQ, GPTQ, FP8), FlashAttention, parallélisme tensor et pipeline, chunked prefill, désagrégation prefill/decode.
- [Guided generation (sorties structurées)](60-inference-llm/63-guided-generation.md) : masquage des logits, JSON Schema, regex et grammaires, XGrammar et Outlines, structured outputs des API, mode JSON ou structured outputs, validation métier.
- [Métriques d'inférence & SLO](60-inference-llm/64-metriques-slo-inference.md) : TTFT, TPOT et ITL, contenu utile et raisonnement, débits offert/admis/utile, SLO conjoints, timeouts, burn rate, loi de Little, autoscaling et benchmarks.
- [Probabilités & sampling](60-inference-llm/65-probabilites-sampling.md) : logits, température, greedy, top-k, top-p et min-p, probabilités conditionnelles, logprobs, perplexité, exercices de renormalisation, sampling et limites de la confiance.
- [Prefix caching & RadixAttention](60-inference-llm/66-prefix-caching-radix-attention.md) : prefix caching de vLLM, arbre radix de SGLang, éviction, ordonnancement et routage cache-aware, offloading du KV cache (LMCache), limites, canal auxiliaire temporel, métriques par requête et token, gain de TTFT réel, affinité et surcharge.
- [Speculative decoding](60-inference-llm/67-speculative-decoding.md) : brouillon et vérification en une passe, conditions d’amortissement des lectures, règle d'acceptation sans perte, gain selon le taux d'acceptation, choix de k, types de brouillons (petit modèle, n-grammes, EAGLE, Medusa, MTP), vérification en arbre, quand ça aide ou nuit, configuration vLLM, coûts, métriques d'acceptation, validation d'un déploiement.
- [Quantization](60-inference-llm/68-quantization.md) : intérêt en mémoire et en vitesse, quantization des poids, des activations ou du KV cache, formats (FP8, INT8, INT4, NVFP4, MXFP4), weight-only ou W8A8, granularité des échelles, outliers d'activation (SmoothQuant, rotations), PTQ ou QAT, GPTQ, AWQ, GGUF, NF4, choix de la méthode selon le matériel, calibration, mesure de la perte, divergence KL et flips, validation avant déploiement, suivi en production, outils (llm-compressor, Model Optimizer, vLLM).
- [Roofline, prefill/decode & désagrégation](60-inference-llm/69-roofline-prefill-decode.md) : intensité arithmétique, modèle roofline, memory-bound ou compute-bound, calculs de débit de decode et de durée de prefill, batch en decode, limites de l'utilisation GPU, interférence prefill/decode, chunked prefill ou désagrégation, déploiement désagrégé (Dynamo, llm-d), quand désagréger, coût et recouvrement des transferts KV.
- [Benchmarks de charge pour l’inférence LLM](60-inference-llm/60-010-benchmarks-charge-inference.md) : protocole reproductible, boucle ouverte ou fermée, omission coordonnée, mix de requêtes, cache froid/chaud, saturation, incertitude, limites du générateur, capacité sous SLO.
- [Capacité & ordonnancement de l’inférence LLM](60-inference-llm/60-011-capacite-ordonnancement-inference.md) : budgets de séquences et de tokens, mémoire KV réelle, GQA et sharding, préemption, admission, priorités, files, réplication et parallélismes, capacité de secours et annulation.
- [Démarche d’optimisation de l’inférence LLM](60-inference-llm/60-012-demarche-optimisation-inference.md) : objectif sous contraintes, profilage CPU/GPU, graphes CUDA et compilation, kernels, loi d’Amdahl, interactions entre optimisations, quotas API, retries, routage, raisonnement et multimodal.

### 70 — Conteneurs & Infra

- [Conteneurs & infra — Index](70-containers-infra/00-index.md) : sommaire des 13 fiches de la section, chaînes à retenir, et une carte sur l'intérêt des conteneurs pour servir des modèles.
- [OCI](70-containers-infra/01-oci.md) : rôle de l'Open Container Initiative, spécifications image, runtime et distribution.
- [Docker, images et registries](70-containers-infra/02-docker-images-registries.md) : rôle de Docker et différence avec OCI, image ou conteneur (instance, état, volumes), compatibilité « Docker/OCI », registries et workflow push/pull.
- [containerd & runc](70-containers-infra/03-containerd-runc.md) : rôle de containerd, rôle de runc, relation entre les deux, containerd ou CRI-O, crun, RuntimeClass, outils `ctr`, `nerdctl` et `crictl`, place du GPU dans la chaîne.
- [Kubernetes, kubelet & CRI](70-containers-infra/04-kubernetes-kubelet-cri.md) : Pod, Deployment, Service, control plane, kubelet, CRI (containerd, CRI-O), scheduler, requests et limits, probes.
- [Docker & Kubernetes](70-containers-infra/05-docker-kubernetes.md) : dockershim et sa suppression, architecture actuelle, images Docker exécutées sans Docker Engine, cri-dockerd, vérifications avant de retirer Docker Engine, construction d'images sans démon (BuildKit rootless, Buildah).
- [Apptainer & Singularity](70-containers-infra/06-apptainer-singularity.md) : usage en HPC, filiation Singularity → Apptainer, format SIF et conversion des images Docker, `--nv`.
- [Conteneurs — Synthèse](70-containers-infra/07-synthese-containers.md) : cartes de révision transverses (OCI, CRI et SIF, chaînes Kubernetes et image, accès GPU, serveurs d'inférence, stockage des poids).
- [Primitives Linux & fondamentaux Docker](70-containers-infra/08-linux-primitives-docker-fondamentaux.md) : namespaces et cgroups, conteneur ou VM, layers, ordre du Dockerfile et cache, volumes et bind mounts, port mapping.
- [GPU en conteneur](70-containers-infra/09-gpu-conteneurs.md) : NVIDIA Container Toolkit, driver et CUDA, images CUDA, GPU Operator, Apptainer `--nv`, ROCm.
- [Images & poids de modèles](70-containers-infra/10-images-modeles-poids.md) : calcul du temps de chargement des poids d'un 70B, poids dans l'image ou séparés, cold start, safetensors ou pickle, safetensors ou GGUF, modèles distribués comme artefacts OCI.
- [Serveurs d'inférence LLM](70-containers-infra/11-serveurs-inference-llm.md) : vLLM, API compatible OpenAI, multi-LoRA, SGLang, TensorRT-LLM et Triton, TGI, llama.cpp et Ollama.
- [Kubernetes GPU & inférence](70-containers-infra/12-kubernetes-gpu-inference.md) : device plugin, ressource `nvidia.com/gpu`, MIG, time-slicing, KServe, autoscaling (HPA, KEDA).
- [Apptainer & inférence HPC](70-containers-infra/13-apptainer-inference-hpc.md) : Apptainer ou Docker en HPC, modèle de sécurité, intégration Slurm, `--nv`, poids montés depuis le système de fichiers partagé, images SIF, fichier de définition, service multi-nœuds (Ray, InfiniBand, NCCL), exposition d'un serveur lancé dans un job.

### 80 — API Layer & Routing

- [LiteLLM (API layer)](80-api-layer-routing/81-litellm-api-layer.md) : SDK ou proxy, virtual keys, budgets, rate limits, fallbacks, load balancing, callbacks d'observabilité, alternatives (gateways auto-hébergées, services des clouds, agrégateurs).
- [Routing LLM](80-api-layer-routing/82-routing-llm.md) : routage statique, par règles ou sémantique, RouteLLM, cascade, routage selon la charge, cache sémantique.
- [Ingress & API gateway](80-api-layer-routing/83-gateway-ingress.md) : Ingress controller, Ingress ou API gateway, TLS, Gateway API, rate limiting, streaming SSE.
- [Streaming & intégration applicative](80-api-layer-routing/84-streaming-integration-applicative.md) : intérêt du streaming, SSE ou WebSocket, tampons des proxys, annulation côté serveur, JSON en streaming, événements d'un agent (AG-UI), tâches longues asynchrones, reprise d'un flux, clé d'idempotence, calcul des connexions ouvertes.
- [Carte des protocoles agentiques](80-api-layer-routing/85-carte-protocoles-agentiques.md) : protocoles par frontière, MCP, A2A et AG-UI, Agent Card, cycle d'une tâche A2A, API compatible OpenAI, conventions OpenTelemetry GenAI, `AGENTS.md` et skills, paiements par agents (AP2, ACP), gouvernance des standards, quand ne pas exposer un agent en A2A, frontières de confiance.

### 90 — Observabilité & Evals

- [Langfuse & observabilité LLM](90-observabilite-evals/91-langfuse-observabilite.md) : périmètre et alternatives (LangSmith, Phoenix, Braintrust), traces, spans et generations, sessions, prompt management, scores, LLM-as-judge, datasets.
- [ChainForge & évaluation de prompts](90-observabilite-evals/92-chainforge-evals-prompts.md) : comparer prompts et modèles, evals automatiques, tests de régression et cas qui basculent, evals comme prérequis au déploiement.
- [Monitoring de l'inférence & de l'usage](90-observabilite-evals/93-monitoring-inference.md) : monitoring ou observabilité, couches à monitorer, métriques vLLM et GPU (DCGM), usage par équipe, finish_reason, validations de chaque réponse, signaux de qualité sans vérité terrain, erreurs et disponibilité, traces OpenTelemetry GenAI, dashboard, alertes, contrôles avant mise en production, détection de régression, journalisation des prompts, agrégation des histogrammes, buckets SLO, périmètres de mesure, débit global et segmentation.
- [Évaluation des systèmes LLM — Méthodologie](90-observabilite-evals/94-evals-methodologie.md) : benchmark ou eval applicative, analyse d'erreurs, golden dataset, taille des jeux, familles d'évaluateurs, critères binaires, avec ou sans référence, offline et online, eval-driven development, saturation, anti-patterns.
- [LLM-as-a-judge](90-observabilite-evals/95-llm-as-judge.md) : formats pointwise et pairwise, biais (position, verbosité, auto-préférence), prompt de juge, validation contre des humains (TPR, TNR, kappa), correction du taux mesuré, choix du modèle juge, juges spécialisés, limites, quand ne pas utiliser de juge.
- [Évaluation des RAG & des agents](90-observabilite-evals/96-evals-rag-agents.md) : retrieval et génération, calculs precision/recall@k et MRR, nDCG, fidélité ou exactitude, contexte oracle, jeux synthétiques, résultat ou trajectoire, environnements d’eval, pass^k et efficacité.
- [Evals online & A/B testing](90-observabilite-evals/97-evals-online-ab-testing.md) : signaux explicites et implicites, A/B test, guardrail metrics, shadow testing, canary ou A/B, peeking, effet de nouveauté, métriques produit, boucle online-offline, confidentialité, calcul de la taille d'échantillon.
- [Débogage & analyse d'échecs des agents](90-observabilite-evals/98-debogage-agents.md) : error analysis (open et axial coding), symptôme ou cause, catégories d'échec, taxonomie MAST, détection des boucles, reproduction par rejeu, de l'échec au cas de non-régression, signaux de production, quand ne pas accuser le modèle.
- [Statistiques pour décider en IA](90-observabilite-evals/99-statistiques-decisions-experimentales.md) : effet utile et significativité, p-valeur, intervalle de confiance, comparaison appariée, unité indépendante, zéro échec, tests multiples, puissance, causalité, biais de sélection et sample ratio mismatch.

### 100 — Sécurité & guardrails

De la sécurité des LLM à celle des agents : les menaces et les incidents réels, l'architecture défensive, la chaîne d'approvisionnement des outils et des skills, le DevSecOps, et le cas des agents de code.

- [Sécurité LLM & guardrails](100-securite-guardrails/101-securite-llm-guardrails.md) : OWASP Top 10 LLM, injection directe ou indirecte, « lethal trifecta », exfiltration, excessive agency, guardrails (Llama Guard, NeMo Guardrails), red teaming.
- [Sécurité des agents — Menaces & incidents](100-securite-guardrails/102-menaces-agents.md) : nouveau modèle de menace, entrées non fiables, détournement d'agent, limites des défenses par détection, incidents (MCP GitHub, EchoLeak, Supabase, Replit), empoisonnement de la mémoire, injection invisible, risques multi-agents, denial of wallet, exécution de code, attaquants équipés d'agents.
- [Sécurité des agents — Architecture défensive](100-securite-guardrails/103-defenses-agents.md) : supposer la compromission, Agents Rule of Two, six design patterns, Dual LLM et CaMeL, moindre privilège, réseau sortant, secrets, validation des appels d'outils, approbation humaine fiable, guardrail de contenu ou politique d'autorisation, mémoire, échanges entre agents, défense en profondeur.
- [Sécurité de MCP, des outils & des skills](100-securite-guardrails/104-securite-mcp-skills.md) : surface d'attaque, tool poisoning, rug pull et tool shadowing (et leurs différences), postmark-mcp, ClawHub, ToxicSkills, règles d'autorisation de la spec, scopes minimaux, SSRF et URL piégées, serveurs locaux, évaluation avant autorisation, gateway MCP.
- [DevSecOps pour l'IA agentique](100-securite-guardrails/105-devsecops-ia-agentique.md) : threat modeling (MAESTRO, ATLAS), référentiels (OWASP, NIST, ISO 42001), AI-BOM, SBOM ou AI-BOM, supply chain des modèles, contrôles en CI, tests adversariaux (promptfoo, garak, PyRIT), red teaming, security eval gate, prompts comme du code, environnements, journalisation, détection, réponse à incident, vulnérabilités, responsabilités.
- [Sécurité des agents de code](100-securite-guardrails/106-securite-agents-code.md) : cible de choix, modes sans permission, isolation du poste, s1ngularity, Amazon Q, fichiers d'instructions piégés, PromptPwnd, agents en CI/CD, slopsquatting et typosquatting, qualité du code généré, revue des PR d'agents, secrets, politique d'entreprise.

### 110 — MLOps & CI/CD

- [MLOps & LLMOps — Fondamentaux](110-mlops-cicd/111-mlops-llmops-fondamentaux.md) : DevOps ou MLOps, spécificités du LLMOps, ce qu'il faut versionner (code et config, modèles et données), model registry, lineage, reproductibilité, environnements dev/staging/prod, rôle du Lead.
- [CI/CD des modèles](110-mlops-cicd/112-cicd-modeles.md) : evals statistiques et tests déterministes, eval gates (exemple de seuils), artefact déployé, blue/green et canary, shadow deployment, rollback, GitOps, tests d'une app LLM, prompts en CI, pipeline complet.
- [Monitoring, drift & boucle de feedback](110-mlops-cicd/113-monitoring-drift-feedback.md) : data drift et concept drift, drift d'une app LLM et d'un RAG, qualité en production, boucle de feedback, quand ré-entraîner, annotation régulière, mises à jour des modèles API, alertes sur tendance et par segment.
- [Reproductibilité & variance](110-mlops-cicd/114-reproductibilite-variance.md) : non-déterminisme à température 0, invariance au batch, seed, appel rejouable, tests sur des sorties variables, erreur standard et intervalles de confiance, comparaison appariée, pass@k et pass^k, variance du LLM-as-judge, fine-tuning reproductible.
- [Plateformes d'agents — Architecture & gouvernance](110-mlops-cicd/115-plateformes-agents-gouvernance.md) : plateforme interne (paved road), plan de contrôle et plan d'exécution, architecture de référence, séparation cerveau, mains et session, exécution durable, isolation multi-tenant, échange de jetons pour l'agent délégué, jetons hors du contexte, standards d'identité, moteur de politiques, human-in-the-loop, registre et cycle de vie, Top 10 OWASP agentique, rayon d'impact et kill switch, audit, SLO, evals continues, coûts, AI Act, lock-in, critères de choix.
- [SRE : incidents & capacité des services IA](110-mlops-cicd/116-sre-incidents-capacite-ia.md) : SLI utilisateur, budgets d'erreur, burn rate, alertes multi-fenêtres, files bornées, admission, capacité de secours, propagation des délais, gestion d'incident, rollback, RTO et RPO, postmortem et reprise.

### 120 — Coûts & FinOps

- [Coûts d'inférence](120-couts-finops/121-couts-inference.md) : structure du coût d'un appel, calcul du coût d'un agent de 20 tours avec et sans cache, prix input et output, prompt caching, coût du self-hosting, break-even API ou self-host, batch API, leviers techniques, contexte long, unit economics, GPU idle, coût par réponse conforme et énergie par tâche utile.
- [FinOps LLM](120-couts-finops/122-finops-llm.md) : quatre temps du FinOps, visibilité des coûts, attribution aux équipes, budgets et garde-fous, routage comme premier levier, caches, pratiques GPU, arbitrage coût-qualité-latence, rôle du Lead.
- [Caching agressif](120-couts-finops/123-caching-agressif.md) : prompt caching (TTL, prix d'écriture et de lecture), structure de prompt stable, ce qui casse le cache, contexte append-only, requêtes parallèles et pré-chauffage, caches de réponses, d'embeddings et d'outils, prompt caching, cache exact ou sémantique, invalidation, sécurité, pilotage.

### 130 — Fondamentaux LLM

Ce qu'il faut comprendre du modèle lui-même pour raisonner sur la qualité, le coût et le serving. À lire en prérequis.

- [Architecture Transformer](130-fondamentaux-llm/131-transformer-architecture.md) : attention et somme pondérée, masque causal, teacher forcing, multi-head, GQA/MQA et mémoire KV, MLP, résiduelles, normalisation, RoPE, coûts, poids d’un 70B, modèle de base ou assistant.
- [Tokenisation](130-fondamentaux-llm/132-tokenisation.md) : token ou mot, BPE, byte-level, taille de vocabulaire, surcoût du français, limites au niveau des caractères, tokens spéciaux, chat templates, frontières de tokens, comptage, sécurité.
- [Embeddings & représentations](130-fondamentaux-llm/133-embeddings-representations.md) : apprentissage contrastif, similarités, bi-encoder ou cross-encoder, ColBERT, Matryoshka, préfixes, choix (MTEB), fine-tuning d'embeddings, changement de modèle, SPLADE, limites.
- [Recherche vectorielle & index ANN](130-fondamentaux-llm/134-recherche-vectorielle-ann.md) : brute force ou ANN, rappel de l'index ou rappel du retrieval, calcul de la mémoire d'un index HNSW, HNSW et ses paramètres, IVF, Product Quantization, quantization scalaire et binaire, DiskANN, filtrage, recall de l'index, pgvector ou base dédiée, exploitation, dimensionnement.
- [Pré-entraînement & scaling laws](130-fondamentaux-llm/135-pretraining-scaling-laws.md) : étapes de fabrication, pré-entraînement ou post-training, données, scaling laws, Chinchilla, sur-entraînement pour l'inférence, 6ND, MFU, contamination, knowledge cutoff, capacités émergentes, mur des données.
- [Mixture of Experts (MoE)](130-fondamentaux-llm/136-mixture-of-experts.md) : paramètres totaux et actifs, routeur, load balancing, expert partagé, spécialisation réelle, coût mémoire, expert parallelism, MoE ou dense.
- [Long contexte](130-fondamentaux-llm/137-long-contexte.md) : extension de RoPE, lost in the middle, needle in a haystack et RULER, context rot, long contexte ou RAG, coût, techniques de serving, limite de sortie, test sur sa tâche.
- [Modèles de raisonnement & test-time compute](130-fondamentaux-llm/138-modeles-raisonnement.md) : modèle de raisonnement ou chain-of-thought par prompt, test-time compute, RLVR, budget de réflexion, facturation, quand ne pas les utiliser, prompting, fidélité de la chaîne de pensée, interleaved thinking, best-of-n.

### 140 — System design & produit

La partie qui assemble tout le reste : concevoir, fiabiliser et piloter une application LLM, niveau senior.

- [System design d'applications LLM — Méthode](140-system-design-produit/141-system-design-llm.md) : démarche, cadrage, échelle de complexité, triangle qualité-latence-coût, estimation de charge, composants, latence réelle ou perçue, synchrone ou asynchrone, multi-tenant, modes de défaillance, présentation des arbitrages.
- [Fiabilité & résilience des applications LLM](140-system-design-produit/142-fiabilite-resilience-llm.md) : timeouts, retries, fallbacks, circuit breaker, retry, fallback ou circuit breaker, retries multipliés entre couches, sorties mal formées, dégradation gracieuse, rate limits, tâches longues, épinglage de version, SLO, chaos testing.
- [Hallucinations, grounding & abstention](140-system-design-produit/143-hallucinations-grounding.md) : types d'hallucinations, leviers, citations vérifiées, abstention, arbitrage avec la couverture, détection, calibration, slopsquatting, communication de l'incertitude.
- [UX de l'IA & human-in-the-loop](140-system-design-produit/144-ux-ia-human-in-the-loop.md) : copilote ou autopilote, validation humaine efficace, streaming, visibilité des agents, feedback, attentes, chat ou interface dédiée, automation bias, erreurs et refus.
- [Cas de system design LLM](140-system-design-produit/145-cas-system-design.md) : support client, recherche documentaire, assistant de code, extraction à grande échelle, agent qui agit, chatbot grand public, assistant vocal, trame de réponse, erreurs d'entretien.
- [Choisir un modèle](140-system-design-produit/146-choix-modeles.md) : critères, limites des leaderboards, benchmarks, fermé ou open weights, licences, coût par tâche, architecture multi-modèles, lock-in, migration, veille.
- [Leadership technique en AI Engineering](140-system-design-produit/147-leadership-technique-ia.md) : ce qui fait un senior, choix des cas d'usage, ROI, échec des POC, RFC et ADR, build ou buy, go / no-go, standards d'équipe, mentorat, revue de conception, dette technique, communication et veille.
- [Pipelines batch à grande échelle](140-system-design-produit/148-pipelines-batch-llm.md) : batch ou en ligne, batch API (JSONL, `custom_id`, 24 h), batch API ou continuous batching, architecture reprenable, calculs de coût et de durée sous quota, classement des erreurs, contrôle qualité statistique, versions enregistrées avec chaque résultat, auto-hébergement hors ligne, quand ne pas utiliser de batch API.
- [Livraison, idempotence & concurrence](140-system-design-produit/149-livraison-idempotence-concurrence.md) : garanties de livraison, limites du exactement une fois, timeout ambigu, identité des opérations, déduplication atomique, rétention, ack, ordre par entité, concurrence optimiste, isolation et fencing tokens.
- [Transactions, outbox & sagas pour les agents](140-system-design-produit/140-010-transactions-outbox-sagas.md) : invariants métier, double écriture, outbox et inbox, périmètre transactionnel, sagas et compensation, isolation des workflows, états inconnus, checkpoints, validation humaine et tests de panne.

### 150 — Données & conformité

- [Données : curation & annotation](150-donnees-conformite/151-donnees-curation-annotation.md) : dimensions de qualité, déduplication, guide d'annotation, accord inter-annotateurs, qui annote, active learning, séparation dev et test, données de production, préparation d'un fine-tuning.
- [PII & confidentialité des données](150-donnees-conformite/152-pii-confidentialite.md) : où passent les données, détection, masquage, pseudonymisation et anonymisation, pseudonymiser avant l'appel, engagements des fournisseurs, logs, mémorisation, fuites entre utilisateurs, secrets, privacy by design.
- [Data flywheel & versioning des données](150-donnees-conformite/153-data-flywheel-versioning.md) : boucle d'amélioration, étapes, versioning des données, outils (DVC, lakeFS, Iceberg), lineage d'une eval, versioning d'un index, signaux implicites, pièges, priorisation.
- [RGPD appliqué aux LLM](150-donnees-conformite/154-rgpd-llm.md) : champ d'application, RGPD ou AI Act, principes, base légale de la réutilisation, responsable et sous-traitant, transferts hors UE, droit à l'effacement, AIPD, décisions automatisées, données dans le modèle, mesures concrètes.
- [AI Act (règlement européen sur l'IA)](150-donnees-conformite/155-ai-act.md) : approche par les risques, pratiques interdites, haut risque et obligations, fournisseur ou déployeur, transparence, modèles à usage général, calendrier, sanctions, plan d'action.
- [IA responsable : biais, équité & transparence](150-donnees-conformite/156-ia-responsable.md) : safety ou security, sources de biais, tests contrefactuels, métriques d'équité, model cards et system cards, datasheets, sycophancy, sécurité ou utilité, supervision humaine effective, référentiels (NIST AI RMF, ISO 42001).
- [Contrats, schémas & qualité des données](150-donnees-conformite/157-contrats-qualite-donnees.md) : contrat producteur-consommateur, contraintes de schéma et métier, fraîcheur et complétude, compatibilité, migrations, quarantaine, dérive ou incident, publication atomique et lignage opérationnel.
- [Ingestion incrémentale, CDC & backfills](150-donnees-conformite/158-ingestion-cdc-backfills.md) : snapshot ou incrémental, CDC, cohérence snapshot-journal, checkpoints, identités et versions, suppressions, rejeu historique, capacité de rattrapage, quarantaine, réconciliation et index RAG, pagination API et cohérence des extractions.
- [Données temporelles & variables de production](150-donnees-conformite/159-donnees-temporelles-features.md) : temps événement et traitement, disponibilité historique, jointures point-in-time, corrections bitemporelles, fenêtres et watermarks, labels retardés, cohérence entraînement-serving, feature store et fraîcheur, chemins offline/online et matérialisation sûre.
- [Modélisation des données analytiques](150-donnees-conformite/150-010-modelisation-donnees-analytiques.md) : grain, OLTP et OLAP, faits et dimensions, clés, normalisation, cardinalités de jointure, mesures additives, SCD, identité métier et définitions de métriques.
- [SQL pour les pipelines et datasets IA](150-donnees-conformite/150-011-sql-transformations-analytiques.md) : jointures et filtres, NULL, agrégations, fenêtres, déduplication déterministe, anti-jointures, CTE, SQL temporel, plans de requête et contrôles de transformations.
- [Stockage colonnaire, partitions & lakehouse](150-donnees-conformite/150-012-stockage-colonnaire-lakehouse.md) : warehouse, lake et lakehouse, stockage objet, JSONL/Avro/Parquet/Arrow, row groups, pruning, partitions, petits fichiers, formats de table, transactions, snapshots et suppressions.
- [Transformations & orchestration des pipelines data](150-donnees-conformite/150-013-orchestration-pipelines-donnees.md) : ETL/ELT, couches de données, tâches et assets, intervalles logiques, dépendances, incrémental, retries, publication, CI, ressources et chemin critique d’un DAG.
- [Streaming & traitements d’événements](150-donnees-conformite/150-014-streaming-traitements-evenements.md) : batch et micro-batch, partitions et ordre, groupes de consommateurs, fenêtres, triggers, watermarks, jointures de flux, changelog, état, checkpoints, backpressure et reprise.
- [Calcul distribué & performance des pipelines data](150-donnees-conformite/150-015-calcul-distribue-performance-donnees.md) : choix local ou distribué, exécution paresseuse, partitions, shuffle, skew, broadcast, salting, mémoire driver, UDF, cache, agrégations, loi d’Amdahl et coût du traitement.
- [Observabilité, lignage & exploitation des données](150-donnees-conformite/150-016-observabilite-lignage-donnees.md) : SLO de données, fraîcheur, complétude par segment, réconciliation, couverture des tests, lignage déclaré ou exécuté, catalogue, impact, incidents et coût de surveillance.
- [Construction de datasets & corpus IA](150-donnees-conformite/150-017-datasets-corpus-ia.md) : manifestes, identité documentaire, parsing, déduplication et splits, shards, streaming de datasets, shuffle, workers, mélange des sources, filtrage, packing et reprise d’entraînement.

### 160 — Multimodal & edge

- [Modèles vision-langage (VLM)](160-multimodal-edge/161-modeles-vision-langage.md) : encodeur visuel et projecteur, calcul du coût de 10 000 images, CLIP, faiblesses, injection visuelle, computer use, VLM ou OCR, évaluation, autres modalités.
- [Parsing de documents (PDF, OCR, layout)](160-multimodal-edge/162-document-parsing.md) : PDF natif ou scanné, analyse de layout, outils (Docling, Unstructured, services cloud, VLM), tableaux, figures, ColPali, chunking structurel, évaluation, exploitation.
- [Voix & agents temps réel](160-multimodal-edge/163-voix-temps-reel.md) : cascade ou speech-to-speech, budget de latence, réduction de latence, détection de fin de tour, barge-in, texte pour la voix, STT, évaluation, risques.
- [LLM locaux, on-prem & edge](160-multimodal-edge/164-llm-local-edge.md) : motivations, capacité ou bande passante mémoire, llama.cpp et GGUF, outils locaux, Ollama ou vLLM, Apple Silicon, small language models, hybride local et cloud, flotte d'appareils, rentabilité du on-prem.
- [Computer use & agents navigateur](160-multimodal-edge/165-computer-use-agents-navigateur.md) : image ou structure (DOM, arbre d'accessibilité), grounding visuel, benchmarks (OSWorld, WebArena), coût et latence, injection par le contenu web, isolation, quand ne pas l'utiliser, computer use ou RPA, outils.

### 170 — ML classique & validation

Choisir et valider les modèles prédictifs, calibrer leurs sorties, recommander, prévoir et détecter les anomalies ; distinguer explication du modèle et effet causal d’une action.

- [ML classique : choisir et comprendre les modèles](170-ml-classique/171-choisir-modele-ml.md) : règles ou ML ou LLM, formulation de la cible, baselines, régressions, régularisation, arbres, random forest et boosting, clustering, prétraitement, données manquantes et coût de possession.
- [ML classique : validation, fuites & métriques](170-ml-classique/172-validation-metriques-ml.md) : train-validation-test, fuite de données, validation croisée et imbriquée, groupes et temps, pipelines, précision et rappel, classes rares, ROC et PR, seuil métier, MAE et RMSE, suréchantillonnage et incertitude.
- [Calibration, incertitude & abstention](170-ml-classique/173-calibration-incertitude-abstention.md) : discrimination et calibration, courbes de fiabilité, Brier score, calibration séparée, temperature scaling, incertitude épistémique et aléatoire, risque-couverture, prédiction conforme, prévalence et coût de la revue.
- [Recommandation & learning to rank](170-ml-classique/174-recommandation-ranking.md) : objectif produit, génération de candidats et classement, filtrage collaboratif ou contenu, feedback implicite, modèles à deux tours, objectifs de ranking, négatifs, biais d'exposition, cold start, nDCG et diversité.
- [Prévision de séries temporelles](170-ml-classique/175-series-temporelles-prevision.md) : horizon et cadence, baseline saisonnière, ETS ou ARIMA ou ML, backtesting à origines glissantes, variables futures, prévisions directes ou récursives, lags, MAPE et MASE, quantiles, intervalles et cohérence hiérarchique.
- [Détection d'anomalies](170-ml-classique/176-detection-anomalies.md) : rareté et erreur métier, outlier ou nouveauté, scores non probabilistes, baseline contextuelle, Isolation Forest, LOF, autoencodeurs, capacité de revue, prévalence, évaluation par incident, labels manquants et dérive.
- [Explicabilité & diagnostic des modèles](170-ml-classique/177-explicabilite-modeles.md) : explication locale ou globale, importance par permutation, variables corrélées, contributions SHAP, population de référence, log-odds, PDP et ICE, contrefactuels actionnables, justifications générées et fidélité de l'explication.
- [Inférence causale & décisions produit](170-ml-classique/178-inference-causale-decisions.md) : prédiction ou intervention, ATE et CATE, graphe causal, confusion et collision, identification ou estimation, hypothèses, positivité, score de propension, différences de différences, uplift et analyses de sensibilité.

<!-- catalog:end -->

---

## Maintenance

La [revue du 6 octobre 2026](docs/revue-flashcards-2026-10-06.md) détaille les réponses enrichies, les corrections de fond et les contrôles effectués.

L'écosystème LLM change vite : noms de produits, versions et outils recommandés peuvent devenir obsolètes en quelques mois. Quand une réponse ne correspond plus à la réalité, on corrige la carte plutôt que d'en ajouter une nouvelle, pour que l'historique de révision de la carte soit conservé.

Le script `scripts/lint_flashcards.py` vérifie les conventions et calcule les statistiques :

```bash
python3 scripts/lint_flashcards.py                  # erreurs et avertissements
python3 scripts/lint_flashcards.py --stats          # statistiques par fiche
python3 scripts/lint_flashcards.py --update-readme  # met à jour la ligne « État au … »
python3 scripts/lint_flashcards.py --stale-months 6 # fiches à revérifier (défaut : 6 mois)
python3 scripts/assign_card_ids.py                 # identifiants des nouvelles cartes
python3 scripts/sync_catalog.py                    # régénérer les deux catalogues
python3 scripts/sync_catalog.py --check            # vérifier sans écrire
python3 -m unittest discover -s tests -v           # tests (dépendances Anki requises)
```

- **Erreurs** (bloquent le commit et la CI) : lien mort, nom de fichier en double, tags absents de la ligne 2, séparateur `?` absent ou multiple, question ou réponse vide, carte que le plugin Spaced Repetition lirait autrement que l'export Anki, identifiant Anki absent/invalide/dupliqué, identifiant retiré encore présent dans le vault ou entrée mal formée dans `retired_cards.json`, section `Mises en situation` ou `Connexions` manquante, dernier lien qui n'est pas le MOC, fiche absente du MOC, date `Vérifié le` illisible ou future, fiche datée sans source. Les liens sont contrôlés aussi dans le MOC et le README (hors exemples de code).
- **Avertissements** : réponse trop longue (110 mots hors code, 140 pour une mise en situation), liste de plus de 5 éléments (6 étapes pour une mise en situation), « Quelle différence… » au lieu de « À ne pas confondre », question qui suppose la carte précédente, liste de produits à réciter (« Citez… », « Quels outils… »), question en double, Connexion sans lien en retour, fiche citée par moins de 2 autres, fiche absente du README, `Vérifié le` trop ancien.

Le lint contrôle la structure, les liens et les conventions ; il ne juge pas l'exactitude ou la profondeur pédagogique. Lors d'une revue, vérifier que la réponse traite toute la question, explique les termes nécessaires, précise les hypothèses des chiffres et donne un exemple ou une limite lorsque cela aide à comprendre. Une réponse courte peut être suffisante ; une réponse longue peut rester vague. Consigner dans `docs/` le périmètre de la revue et les validations réalisées.

Les pull requests vérifient le lint, la synchronisation des catalogues, les tests et la génération d’un paquet Anki téléchargeable comme artefact CI. La publication en release reste réservée à `main` ou au déclenchement manuel.

Le paquet Anki se régénère seul à chaque push sur `main` (voir [Réviser sur Android avec Anki](#4-réviser-sur-android-avec-anki)). Changer `MODEL_ID` dans `scripts/export_anki.py` casserait la mise à jour des cartes déjà importées : ne pas y toucher.

Pour activer le hook pre-commit, une fois par clone : `git config core.hooksPath .githooks`.

Les fiches qui citent des produits, des versions ou des textes réglementaires portent une ligne `Vérifié le`. Le lint les signale au bout de 6 mois : on les relit, on corrige ce qui a changé, puis on met la date à jour.

Les références ajoutées aux fiches servent de points de contrôle pour leur prochaine revue ; elles ne remplacent pas une validation de chaque affirmation. Les dates existantes n’ont pas été renouvelées par le seul ajout de sources.

`tests/fixtures/legacy_guids.json` conserve les identifiants antérieurs à la migration : le test empêche leur perte accidentelle. Une suppression volontaire passe par `scripts/retired_cards.json`, que le test accepte.
