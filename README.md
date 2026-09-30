# Knowledge Vault — AI Engineering

Un vault [Obsidian](https://obsidian.md) de **fiches de révision (flashcards) en français** qui couvre les compétences clés de l'**AI Engineering**. Le parcours va de l'utilisation des modèles jusqu'à leur mise en production et leur sécurisation.

Chaque fiche traite **un concept** en 10 à 32 cartes question/réponse, une quinzaine en moyenne, et se termine par des **mises en situation** : des cas concrets à diagnostiquer, concevoir ou arbitrer. Les fiches sont reliées entre elles par des liens, pour qu'on puisse passer d'un sujet à ses voisins, et elles se révisent en **répétition espacée**.

**État au 29 septembre 2026** : 102 fiches et 1 420 cartes, réparties en 16 sections, dont 219 mises en situation et 78 cartes « à ne pas confondre ».

---

## Structure du repo

```text
Knowledge_AI_Engineering/
├── README.md
├── .obsidian/                   # configuration Obsidian
├── .claude/skills/              # skills Claude Code versionnés (grilling, grill-me)
├── scripts/lint_flashcards.py   # vérification des conventions + statistiques
├── scripts/export_anki.py       # export en paquet Anki (.apkg) pour AnkiDroid
├── scripts/requirements.txt     # dépendances de l'export Anki
├── .githooks/pre-commit         # lance le lint avant chaque commit
├── .github/workflows/           # lint en CI, et export Anki publié en release
├── 00-moc-ai-engineering.md     # carte racine : parcours de lecture + sommaire
├── 10-prompt-engineering/
├── 20-rag/
├── 30-agents/
├── 40-automatisation/           # workflows + LangChain, LangGraph, CrewAI
├── 50-fine-tuning/
├── 60-inference-llm/
├── 70-containers-infra/         # contient son propre index : 00-index.md
├── 80-api-layer-routing/
├── 90-observabilite-evals/
├── 100-securite-guardrails/
├── 110-mlops-cicd/
├── 120-couts-finops/
├── 130-fondamentaux-llm/         # Transformer, tokenisation, embeddings, MoE, raisonnement
├── 140-system-design-produit/    # system design, fiabilité, UX, choix de modèle, leadership
├── 150-donnees-conformite/       # curation, PII, flywheel, RGPD, AI Act, IA responsable
└── 160-multimodal-edge/          # VLM, parsing de documents, voix, LLM locaux
```

- Chaque **section** est un dossier numéroté par dizaine (`20-rag`, `30-agents`…).
- Chaque **fiche** porte un numéro qui reprend celui de sa section : `21-rag-fondamentaux.md` et `22-rag-avance.md` sont dans `20-rag/`.
- Exception : la section conteneurs garde sa propre numérotation, de `00-index.md` à `13-apptainer-inference-hpc.md`.
- Une section compte **au plus 9 fiches** (de `x1` à `x9`). Quand elle est pleine, la fiche va dans la section la plus proche de son sujet et le MOC la signale à côté de sa fiche d'origine. C'est le cas de `115-plateformes-agents-gouvernance.md` (section 110), la suite senior de `38-plateformes-agents.md`, car la section 30 est pleine. De même, `165-computer-use-agents-navigateur.md` rejoint la section 160 (multimodal), à côté des modèles vision-langage.
- Le point d'entrée est le **MOC** (Map of Content), [00-moc-ai-engineering.md](00-moc-ai-engineering.md).

---

## Comment l'utiliser

### 1. Ouvrir le vault

1. Installer [Obsidian](https://obsidian.md).
2. Choisir **Open folder as vault** et sélectionner le dossier du dépôt (`Knowledge_AI_Engineering` après un `git clone`).
3. Ouvrir [00-moc-ai-engineering.md](00-moc-ai-engineering.md).

### 2. Lire et naviguer

- **Suivre le parcours de lecture** du MOC, qui va dans cet ordre : fondamentaux LLM (prérequis), prompt engineering, RAG, agents, automatisation et frameworks d'agents, fine-tuning, inférence, conteneurs, API layer, observabilité, sécurité, MLOps & CI/CD, coûts & FinOps, données & conformité, multimodal & edge, puis system design & produit, qui assemble le tout.
- **Rebondir entre les concepts** : chaque fiche se termine par une section `Connexions` qui explique pourquoi les fiches liées sont liées. Des liens apparaissent aussi dans les réponses elles-mêmes.
- **Voir l'ensemble** : la **vue graphe** d'Obsidian montre comment les concepts s'articulent, et le panneau **Backlinks** liste les fiches qui citent la fiche ouverte.

### 3. Réviser en répétition espacée

Les fiches suivent la syntaxe du plugin communautaire **Spaced Repetition**. Il n'est pas installé par défaut :

1. **Settings → Community plugins** : activer les plugins communautaires, puis chercher et installer **Spaced Repetition**.
2. Le plugin retrouve automatiquement les fiches grâce au tag `#flashcards` qui figure en ligne 2 de chacune.
3. Dans les réglages du plugin, garder `?` comme séparateur des cartes multilignes. Choisir aussi `---` comme marqueur de fin de carte, car certaines réponses contiennent des lignes vides.
4. Lancer une révision avec l'icône du plugin dans la barre latérale, ou depuis la palette de commandes. La palette permet aussi de ne réviser que la note ouverte.

> Le plugin enregistre la planification des révisions **dans les fiches elles-mêmes**, sous forme de commentaires `<!--SR:...-->` placés après chaque carte. Si le vault est versionné avec git, ces commentaires apparaîtront dans les diffs.

### 4. Réviser sur Android avec Anki

À chaque push sur `main`, la CI génère un paquet Anki de toutes les fiches et le publie à une adresse fixe :

**https://github.com/speillet/Knowledge_AI_Engineering/releases/download/anki/ai-engineering.apkg**

1. Installer **AnkiDroid**, gratuit, depuis le Play Store ou F-Droid.
2. Ouvrir l'adresse ci-dessus sur le téléphone, puis ouvrir le fichier téléchargé avec AnkiDroid : il s'importe dans le paquet **AI Engineering**, rangé par section puis par fiche.
3. **Mettre à jour** : retélécharger le fichier et le réimporter. Chaque carte est identifiée par sa fiche et sa question : les cartes existantes sont mises à jour et gardent leur progression.
   - Reformuler une question crée une **nouvelle carte**, et l'ancienne reste dans Anki.
   - Une carte supprimée du vault n'est pas supprimée d'Anki : la retirer à la main, par exemple en cherchant son texte.
4. **Réviser un seul type de carte** avec un paquet filtré (menu **Créer un paquet filtré**) :
   - `tag:type::situation` : les mises en situation ;
   - `tag:type::confusion` : les cartes « à ne pas confondre » ;
   - `tag:type::calcul` : les ordres de grandeur ;
   - `tag:section::20-rag` : une seule section.
5. Pour retrouver la même progression sur ordinateur, synchroniser AnkiDroid avec un compte **AnkiWeb**.

> La progression Anki et celle du plugin Obsidian sont **indépendantes** : une carte révisée sur le téléphone ne l'est pas dans Obsidian, et inversement.

Pour générer le paquet en local :

```bash
pip install -r scripts/requirements.txt
python3 scripts/export_anki.py      # écrit dist/ai-engineering.apkg
```

### Sans Obsidian

Les fiches sont du Markdown simple et se lisent dans n'importe quel éditeur. Seuls les liens au format `[[...]]` ne sont pas cliquables en dehors d'Obsidian.

---

## Format d'une fiche

```markdown
# Tool calling — Flashcards
Tags: #flashcards #ai-engineering #agents #tool-calling #llm

Qu'est-ce que le tool calling ?
?
Le mécanisme par lequel un LLM **émet un appel structuré** que **l'application exécute**.

---

Le modèle exécute-t-il lui-même les outils ?
?
**Non.** Il génère l'intention d'appel ; c'est le [[34-harness-plugins|harness]] qui exécute.

---

## Mises en situation

Mise en situation : ton agent dispose de 40 outils et se trompe souvent d'outil. Comment améliores-tu la situation ?
?
1. **Réduire le choix** : n'exposer que les outils utiles à la tâche en cours.
2. **Soigner les descriptions** : nom explicite, cas d'usage, ce que l'outil ne fait pas.
3. …

**Piège** : ajouter un outil supplémentaire pour corriger les erreurs des précédents.

---

## Connexions
- [[31-agents-fondamentaux|Agents]] — la boucle qui consomme les outils
- [[00-moc-ai-engineering|MOC AI Engineering]]
```

Les conventions à respecter :

- **Pas de frontmatter YAML.** Les tags sont écrits en texte sur la ligne 2.
- **Une carte** = la question, puis une ligne contenant seulement `?`, puis la réponse. Les cartes sont séparées par `---`.
- **Des réponses courtes**, avec les termes clés en gras, et un bloc de code quand c'est utile.
- **Une section `## Mises en situation`** avant les connexions : 2 cartes (3 pour les fiches avancées) dont la question commence par `Mise en situation :`, tient en un seul paragraphe et décrit un cas concret. La réponse déroule une **démarche en 3 à 6 étapes** et peut finir par un **piège** à éviter.
- **Une section `## Connexions`** à la fin, dont le dernier lien renvoie toujours au MOC.
- **Des cartes courtes** : au-delà de 5 éléments, une liste se découpe en sous-cartes thématiques dont la question donne un indice.
- **Des cartes « À ne pas confondre : X et Y ? »** pour les notions que l'on mélange (OCI et CRI, tag et digest, routing et fallback, rappel et précision, few-shot et fine-tuning…). On n'écrit pas « Quelle différence entre X et Y ? » : le format unique permet de toutes les retrouver par une recherche.
- **Des cartes de raisonnement** plutôt que des définitions seules : « Quand ne pas… ? », « Que se passe-t-il si… ? », et des cartes **« Calcul : … »** qui font poser un ordre de grandeur (VRAM, débit, coût, taille d'échantillon).
- **Une idée par carte** : si une réponse enchaîne deux sujets (un mécanisme puis une liste de produits, deux incidents), on la découpe. Une carte atomique se note honnêtement en révision.
- **Des repères chiffrés** et des **exemples exécutables** (commandes, configurations, extraits de code) plutôt que des formulations abstraites.
- **Une ligne `Vérifié le : …`** juste après les tags, sur les fiches qui citent des produits, des versions ou des textes réglementaires. Elle dit quand le contenu a été confronté à la réalité.

## Ajouter une fiche

1. Choisir la section et le prochain numéro libre, puis nommer le fichier en kebab-case, par exemple `27-rag-multimodal.md`. Si la section est pleine, appliquer la règle décrite dans [Structure du repo](#structure-du-repo).
2. **Le nom de fichier doit être unique dans tout le vault**, car Obsidian résout les liens `[[...]]` par nom de fichier, pas par chemin.
3. Rédiger les cartes au format ci-dessus.
4. Ajouter la fiche dans le sommaire du MOC, dans la section qui lui correspond, et dans la liste [Concepts couverts](#concepts-couverts) de ce README. Mettre à jour les chiffres en haut du README avec `python3 scripts/lint_flashcards.py --update-readme`.
5. Ajouter des liens dans les deux sens : la nouvelle fiche cite ses voisines, et les voisines la citent dans leur section `Connexions`.
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

### 10 — Prompt engineering

- [Prompt engineering avancé](10-prompt-engineering/11-prompt-engineering-avance.md) : system prompt et user prompt, few-shot, chain-of-thought, self-consistency, délimiteurs, meta-prompting, prompts versionnés comme du code, anti-patterns.
- [Optimisation automatique de prompts](10-prompt-engineering/12-optimisation-automatique-prompts.md) : meta-prompting ou optimisation guidée par une métrique, DSPy (signatures, modules, optimiseurs BootstrapFewShot, MIPROv2, GEPA), APE, OPRO, TextGrad, quand l'utiliser ou non, sur-apprentissage, transfert entre modèles, optimisation de prompts ou fine-tuning.
- [Prompts en production](10-prompt-engineering/13-prompts-production.md) : briques d'un prompt, placement des longs documents, consignes motivées, limites des rôles, prompter un modèle de raisonnement, templates et données utilisateur, registre et versioning, prompt dans le code ou dans un registre, portabilité entre modèles, langue, contrôle de la longueur.

### 20 — RAG

- [RAG — Fondamentaux](20-rag/21-rag-fondamentaux.md) : RAG ou fine-tuning, pipeline d'ingestion et de requête, stratégies de chunking, embeddings, bases vectorielles (HNSW, pgvector, Qdrant), top-k, grounding et citations, recall@k.
- [RAG — Avancé](20-rag/22-rag-avance.md) : recherche hybride (BM25, RRF), reranking, query rewriting, HyDE, filtrage par métadonnées et ACL, GraphRAG, agentic RAG, triade d'évaluation (RAGAS), « lost in the middle ».
- [Knowledge graphs & ontologies](20-rag/23-knowledge-graphs-ontologies.md) : triplets, RDF ou property graph (Cypher, GQL), ontologie et taxonomie, extraction par LLM sous schéma, résolution d'entités, graphe ou vecteurs, GraphRAG local et global, Text2Cypher, context graph, coûts.
- [Cognee](20-rag/24-cognee.md) : mémoire d'agent en knowledge graph, opérations remember, recall, improve et forget, mémoire permanente ou de session, stratégies de recherche, ontologie OWL, intégrations (plugin, MCP), limites.
- [Chunking avancé & contextual retrieval](20-rag/25-chunking-contextual-retrieval.md) : chunks sans contexte, contextual retrieval (gain, coût, prompt caching), late chunking, taille des chunks, small-to-big, chunking sémantique et par propositions, fil d'Ariane et métadonnées, comparaison de stratégies au recall@k.
- [Text-to-SQL & données structurées](20-rag/26-text-to-sql.md) : text-to-SQL ou RAG, contenu du prompt, schema linking, couche sémantique, sécurisation de l'exécution, boucle de correction, exact match ou execution accuracy, benchmarks (Spider, BIRD, Spider 2.0), questions ambiguës.
- [Agents de recherche (deep research)](20-rag/27-agents-recherche-deep-research.md) : RAG ou agent de recherche, boucle de recherche, sous-agents parallèles, outils de recherche, citations fiables, risques (sources, injection, biais), évaluation (couverture, BrowseComp), calcul du coût d'un rapport, quand ne pas l'utiliser.

### 30 — Agents

- [Fondamentaux des agents](30-agents/31-agents-fondamentaux.md) : workflow ou agent, pattern ReAct, composants d'un agent, human-in-the-loop, risques, conditions d'arrêt.
- [Tool calling](30-agents/32-tool-calling.md) : déclaration par JSON Schema, boucle d'appel, parallel tool calls, gestion des erreurs, rédaction des descriptions d'outils.
- [MCP — Model Context Protocol](30-agents/33-mcp.md) : problème M×N, host, client et serveur, tools, resources et prompts, transports stdio et HTTP, risques.
- [Harness & plugins](30-agents/34-harness-plugins.md) : rôle du harness, plugins, skills, hooks, permissions, sandbox, fichiers mémoire.
- [Context engineering](30-agents/35-context-engineering.md) : le contexte comme budget, context rot, compaction, mémoire court et long terme, sous-agents, prompt caching, contexte chargé au besoin (just-in-time).
- [Orchestration multi-agents](30-agents/36-orchestration-agents.md) : orchestrator-workers, supervisor, handoffs, evaluator-optimizer, état partagé, coût du multi-agent, protocole A2A.
- [Frameworks d'agents](30-agents/37-frameworks-agents.md) : LangChain, LangGraph, CrewAI, Google ADK, OpenAI Agents SDK, Claude Agent SDK, LlamaIndex, framework ou code maison.
- [Plateformes d'agents — Fondamentaux](30-agents/38-plateformes-agents.md) : différence avec un framework, briques, niveaux d'abstraction (API, runtime, harness managé), offres cloud et des fournisseurs de modèles, open source, runtime et double texting, sandbox, gateway d'outils, registre, identité, mémoire, observabilité, evals, protocoles (MCP, A2A), build ou buy. La suite, niveau senior, est la fiche 115 de la section 110.
- [Mémoire des agents](30-agents/39-memoire-agents.md) : mémoire de travail, sémantique, épisodique et procédurale, thread ou long terme, écriture pendant ou après la conversation, consolidation, score de rappel, réflexion, faits qui changent, stockage, Letta, outils, risques, évaluation.

### 40 — Automatisation & frameworks d'agents

Automatiser des processus, soit avec des outils de workflow, soit avec des agents écrits en code. Chaque framework a deux fiches : ses bases, puis son usage avancé ou en production.

- [Automatisation code & no-code](40-automatisation/41-automatisation-code-nocode.md) : n8n, triggers, Zapier et Make, Airflow, Prefect et Temporal, durable execution, limites du no-code.
- [LangChain — Fondamentaux](40-automatisation/42-langchain-fondamentaux.md) : paquets de la v1, `init_chat_model`, messages, outils `@tool` et `bind_tools`, sorties structurées, Runnables et LCEL, briques RAG, LangSmith.
- [LangChain — Agents & middleware](40-automatisation/43-langchain-agents.md) : `create_agent`, mémoire par checkpointer et `thread_id`, `response_format`, hooks de middleware, middlewares fournis (human-in-the-loop, résumé, fallback, limites), runtime context, Deep Agents.
- [LangGraph — Fondamentaux](40-automatisation/44-langgraph-fondamentaux.md) : `StateGraph`, state et reducers, `MessagesState`, nodes et edges conditionnelles, boucle ReAct en graphe, super-steps, `Send` (map-reduce), `Command`, Functional API.
- [LangGraph — Production](40-automatisation/45-langgraph-production.md) : checkpointers, threads, `interrupt` et `Command(resume=...)`, time travel, Store long terme, durable execution, streaming, subgraphs, patterns multi-agents, déploiement.
- [CrewAI — Crews](40-automatisation/46-crewai-crews.md) : agents (role, goal, backstory), tâches, process séquentiel ou hiérarchique, délégation, sorties structurées, guardrails de tâche, LLM et outils, mémoire unifiée, structure d'un projet.
- [CrewAI — Flows](40-automatisation/47-crewai-flows.md) : `@start`, `@listen`, `@router`, état structuré, `@persist`, `@human_feedback`, mémoire, CLI, crew ou flow, Flows ou LangGraph.
- [Patterns de workflows agentiques](40-automatisation/48-patterns-workflows-agentiques.md) : prompt chaining, routing, parallélisation (sectioning, voting), evaluator-optimizer, plan-and-execute ou ReAct, Reflexion, calcul de fiabilité d'une chaîne, workflow ou agent, implémentation sans framework.
- [Agents de code : usage & intégration](40-automatisation/49-agents-de-code.md) : ACI (SWE-agent), boucle pilotée par les tests, `CLAUDE.md` et `AGENTS.md`, mode plan, worktrees et sous-agents, gestion du contexte, mode headless, SWE-bench et ses limites, tâches à déléguer, mesure de l'apport.

### 50 — Fine-tuning

- [Fine-tuning & adaptation](50-fine-tuning/51-fine-tuning-adaptation.md) : quand fine-tuner, SFT, full fine-tuning ou PEFT, LoRA, QLoRA, RLHF, DPO, distillation, multi-LoRA, catastrophic forgetting.
- [Post-training & alignement](50-fine-tuning/52-post-training-alignement.md) : étapes du RLHF, pénalité KL, reward hacking, DPO et variantes, GRPO, RLVR, RLAIF et Constitutional AI, jeux de préférences, taxe d'alignement, quand faire soi-même du DPO ou du RL.
- [Données synthétiques & distillation](50-fine-tuning/53-donnees-synthetiques-distillation.md) : génération variée, filtrage, model collapse, distillation sur les sorties ou sur les logits, distillation du raisonnement, contraintes juridiques, projet de distillation, jeux d'eval synthétiques.
- [Entraînement distribué](50-fine-tuning/54-entrainement-distribue.md) : mémoire d'entraînement, DDP, ZeRO et FSDP, tensor et pipeline parallelism, parallélisme 3D, gradient checkpointing, accumulation de gradients, précision mixte BF16, réseau, pannes et checkpoints.

### 60 — Inférence LLM

- [KV cache & attention](60-inference-llm/61-kv-cache-attention.md) : taille du cache, PagedAttention, prefix caching, quantization du cache, coût des contextes longs.
- [Optimisations d'inférence](60-inference-llm/62-optimisations-inference.md) : prefill et decode, continuous batching, quantization (AWQ, GPTQ, FP8), speculative decoding, FlashAttention, parallélisme tensor et pipeline, chunked prefill, désagrégation prefill/decode.
- [Guided generation](60-inference-llm/63-guided-generation.md) : masquage des logits, JSON Schema, regex et grammaires, XGrammar et Outlines, structured outputs des API, validation métier.
- [Métriques d'inférence & SLO](60-inference-llm/64-metriques-slo-inference.md) : TTFT, TPOT, throughput, goodput, percentiles, définition d'un SLO, signaux d'autoscaling, benchmarks.
- [Probabilités & sampling](60-inference-llm/65-probabilites-sampling.md) : logits et softmax, température, greedy, top-k, top-p, min-p, réglages par cas d'usage, logprobs, probabilité d'une séquence, perplexité, calibration, speculative decoding et distribution.
- [Prefix caching & RadixAttention](60-inference-llm/66-prefix-caching-radix-attention.md) : prefix caching de vLLM, arbre radix de SGLang, éviction, ordonnancement et routage cache-aware, offloading du KV cache (LMCache), limites, canal auxiliaire temporel, métriques.
- [Speculative decoding](60-inference-llm/67-speculative-decoding.md) : brouillon et vérification en une passe, pourquoi c'est presque gratuit, règle d'acceptation sans perte, gain selon le taux d'acceptation, choix de k, types de brouillons (petit modèle, n-grammes, EAGLE, Medusa, MTP), vérification en arbre, quand ça aide ou nuit, configuration vLLM, coûts, métriques d'acceptation, validation d'un déploiement.
- [Quantization](60-inference-llm/68-quantization.md) : intérêt en mémoire et en vitesse, formats (FP8, INT8, INT4, NVFP4, MXFP4), weight-only ou W8A8, granularité des échelles, outliers d'activation (SmoothQuant, rotations), PTQ ou QAT, GPTQ, AWQ, GGUF, NF4, choix de la méthode selon le matériel, calibration, mesure de la perte, divergence KL et flips, validation avant déploiement, suivi en production, outils (llm-compressor, Model Optimizer, vLLM).
- [Roofline, prefill/decode & désagrégation](60-inference-llm/69-roofline-prefill-decode.md) : intensité arithmétique, modèle roofline, memory-bound ou compute-bound, calculs de débit de decode et de durée de prefill, batch en decode, limites de l'utilisation GPU, interférence prefill/decode, chunked prefill ou désagrégation, déploiement désagrégé (Dynamo, llm-d), quand désagréger.

### 70 — Conteneurs & infra

- [Index Conteneurs](70-containers-infra/00-index.md) : sommaire des 13 fiches de la section, chaînes à retenir, et une carte sur l'intérêt des conteneurs pour servir des modèles.
- [OCI](70-containers-infra/01-oci.md) : rôle de l'Open Container Initiative, spécifications image, runtime et distribution.
- [Docker, images & registries](70-containers-infra/02-docker-images-registries.md) : rôle de Docker et différence avec OCI, image ou conteneur, compatibilité « Docker/OCI », registries et workflow push/pull.
- [containerd & runc](70-containers-infra/03-containerd-runc.md) : rôle de containerd, rôle de runc, relation entre les deux, containerd ou CRI-O, crun, RuntimeClass, outils `ctr`, `nerdctl` et `crictl`, place du GPU dans la chaîne.
- [Kubernetes, kubelet & CRI](70-containers-infra/04-kubernetes-kubelet-cri.md) : Pod, Deployment, Service, control plane, kubelet, CRI (containerd, CRI-O), scheduler, requests et limits, probes.
- [Docker & Kubernetes](70-containers-infra/05-docker-kubernetes.md) : dockershim et sa suppression, architecture actuelle, images Docker exécutées sans Docker Engine, cri-dockerd, vérifications avant de retirer Docker Engine, construction d'images sans démon (BuildKit rootless, Buildah).
- [Apptainer & Singularity](70-containers-infra/06-apptainer-singularity.md) : usage en HPC, filiation Singularity → Apptainer, format SIF, import d'images Docker, `--nv`.
- [Synthèse conteneurs](70-containers-infra/07-synthese-containers.md) : cartes de révision transverses (OCI, CRI et SIF, chaînes Kubernetes et image, accès GPU, serveurs d'inférence, stockage des poids).
- [Primitives Linux & fondamentaux Docker](70-containers-infra/08-linux-primitives-docker-fondamentaux.md) : namespaces et cgroups, conteneur ou VM, layers, ordre du Dockerfile et cache, volumes et bind mounts, port mapping.
- [GPU en conteneur](70-containers-infra/09-gpu-conteneurs.md) : NVIDIA Container Toolkit, driver et CUDA, images CUDA, GPU Operator, Apptainer `--nv`, ROCm.
- [Images & poids de modèles](70-containers-infra/10-images-modeles-poids.md) : poids dans l'image ou séparés, cold start, safetensors ou pickle, GGUF, modèles distribués comme artefacts OCI.
- [Serveurs d'inférence LLM](70-containers-infra/11-serveurs-inference-llm.md) : vLLM, API compatible OpenAI, multi-LoRA, SGLang, TensorRT-LLM et Triton, TGI, llama.cpp et Ollama.
- [Kubernetes GPU & inférence](70-containers-infra/12-kubernetes-gpu-inference.md) : device plugin, ressource `nvidia.com/gpu`, MIG, time-slicing, KServe, autoscaling (HPA, KEDA).
- [Apptainer & inférence HPC](70-containers-infra/13-apptainer-inference-hpc.md) : Apptainer ou Docker en HPC, modèle de sécurité, intégration Slurm, `--nv`, poids montés depuis le système de fichiers partagé, images SIF, fichier de définition, service multi-nœuds (Ray, InfiniBand, NCCL), exposition d'un serveur lancé dans un job.

### 80 — API layer & routing

- [LiteLLM (API layer)](80-api-layer-routing/81-litellm-api-layer.md) : SDK ou proxy, virtual keys, budgets, rate limits, fallbacks, load balancing, callbacks d'observabilité.
- [Routing LLM](80-api-layer-routing/82-routing-llm.md) : routage statique, par règles ou sémantique, RouteLLM, cascade, routage selon la charge, cache sémantique.
- [Ingress & API gateway](80-api-layer-routing/83-gateway-ingress.md) : Ingress controller, TLS, Gateway API, rate limiting, streaming SSE.
- [Streaming & intégration applicative](80-api-layer-routing/84-streaming-integration-applicative.md) : intérêt du streaming, SSE ou WebSocket, tampons des proxys, annulation côté serveur, JSON en streaming, événements d'un agent (AG-UI), tâches longues asynchrones, reprise d'un flux, clé d'idempotence, calcul des connexions ouvertes.

### 90 — Observabilité & evals

- [Langfuse & observabilité LLM](90-observabilite-evals/91-langfuse-observabilite.md) : traces, spans et generations, sessions, prompt management, scores, LLM-as-judge, datasets.
- [ChainForge & évaluation de prompts](90-observabilite-evals/92-chainforge-evals-prompts.md) : comparer prompts et modèles, golden dataset, evals automatiques, tests de régression.
- [Monitoring de l'inférence & de l'usage](90-observabilite-evals/93-monitoring-inference.md) : couches à monitorer, métriques vLLM et GPU (DCGM), usage par équipe, finish_reason, validations de chaque réponse, signaux de qualité sans vérité terrain, erreurs et disponibilité, traces OpenTelemetry GenAI, dashboard, alertes, contrôles avant mise en production, détection de régression, journalisation des prompts.
- [Évaluation des systèmes LLM — Méthodologie](90-observabilite-evals/94-evals-methodologie.md) : benchmark ou eval applicative, analyse d'erreurs, golden dataset, taille des jeux, familles d'évaluateurs, critères binaires, avec ou sans référence, offline et online, eval-driven development, saturation, anti-patterns.
- [LLM-as-a-judge](90-observabilite-evals/95-llm-as-judge.md) : formats pointwise et pairwise, biais (position, verbosité, auto-préférence), prompt de juge, validation contre des humains (TPR, TNR, kappa), correction du taux mesuré, choix du modèle juge, juges spécialisés, limites.
- [Évaluation des RAG & des agents](90-observabilite-evals/96-evals-rag-agents.md) : retrieval et génération, recall@k, MRR, nDCG, triade RAG, faithfulness, jeux synthétiques, résultat final ou trajectoire, environnements d'eval (τ-bench, SWE-bench), pass^k, tool calling, multi-tours, efficacité.
- [Evals online & A/B testing](90-observabilite-evals/97-evals-online-ab-testing.md) : signaux explicites et implicites, A/B test, guardrail metrics, shadow testing, canary ou A/B, peeking, effet de nouveauté, métriques produit, boucle online-offline, confidentialité.
- [Débogage & analyse d'échecs des agents](90-observabilite-evals/98-debogage-agents.md) : error analysis (open et axial coding), symptôme ou cause, catégories d'échec, taxonomie MAST, détection des boucles, reproduction par rejeu, de l'échec au cas de non-régression, signaux de production, quand ne pas accuser le modèle.

### 100 — Sécurité & guardrails

De la sécurité des LLM à celle des agents : les menaces et les incidents réels, l'architecture défensive, la chaîne d'approvisionnement des outils et des skills, le DevSecOps, et le cas des agents de code.

- [Sécurité LLM & guardrails](100-securite-guardrails/101-securite-llm-guardrails.md) : OWASP Top 10 LLM, prompt injection directe et indirecte, « lethal trifecta », exfiltration, excessive agency, guardrails (Llama Guard, NeMo Guardrails), red teaming.
- [Sécurité des agents — Menaces & incidents](100-securite-guardrails/102-menaces-agents.md) : nouveau modèle de menace, entrées non fiables, détournement d'agent, limites des défenses par détection, incidents (MCP GitHub, EchoLeak, Supabase, Replit), empoisonnement de la mémoire, injection invisible, risques multi-agents, denial of wallet, exécution de code, attaquants équipés d'agents.
- [Sécurité des agents — Architecture défensive](100-securite-guardrails/103-defenses-agents.md) : supposer la compromission, Agents Rule of Two, six design patterns, Dual LLM et CaMeL, moindre privilège, réseau sortant, secrets, validation des appels d'outils, approbation humaine fiable, rôle des guardrails, mémoire, échanges entre agents, défense en profondeur.
- [Sécurité de MCP, des outils & des skills](100-securite-guardrails/104-securite-mcp-skills.md) : surface d'attaque, tool poisoning, rug pull, tool shadowing, postmark-mcp, ClawHub et ToxicSkills, règles d'autorisation de la spec, scopes minimaux, SSRF et URL piégées, serveurs locaux, évaluation avant autorisation, gateway MCP.
- [DevSecOps pour l'IA agentique](100-securite-guardrails/105-devsecops-ia-agentique.md) : threat modeling (MAESTRO, ATLAS), référentiels (OWASP, NIST, ISO 42001), AI-BOM, supply chain des modèles, contrôles en CI, tests adversariaux (promptfoo, garak, PyRIT), red teaming, security eval gate, prompts comme du code, environnements, journalisation, détection, réponse à incident, vulnérabilités, responsabilités.
- [Sécurité des agents de code](100-securite-guardrails/106-securite-agents-code.md) : cible de choix, modes sans permission, isolation du poste, s1ngularity, Amazon Q, fichiers d'instructions piégés, PromptPwnd, agents en CI/CD, slopsquatting, qualité du code généré, revue des PR d'agents, secrets, politique d'entreprise.

### 110 — MLOps & CI/CD

- [MLOps & LLMOps — Fondamentaux](110-mlops-cicd/111-mlops-llmops-fondamentaux.md) : DevOps ou MLOps, spécificités du LLMOps, ce qu'il faut versionner, model registry, lineage, reproductibilité, environnements dev/staging/prod, rôle du Lead.
- [CI/CD des modèles](110-mlops-cicd/112-cicd-modeles.md) : eval gates, artefact déployé, blue/green et canary, shadow deployment, rollback, GitOps, tests d'une app LLM, prompts en CI, pipeline complet.
- [Monitoring, drift & boucle de feedback](110-mlops-cicd/113-monitoring-drift-feedback.md) : data drift et concept drift, drift d'une app LLM et d'un RAG, qualité en production, boucle de feedback, quand ré-entraîner, mises à jour des modèles API, alertes.
- [Reproductibilité & variance](110-mlops-cicd/114-reproductibilite-variance.md) : non-déterminisme à température 0, invariance au batch, seed, appel rejouable, tests sur des sorties variables, erreur standard et intervalles de confiance, comparaison appariée, pass@k et pass^k, variance du LLM-as-judge, fine-tuning reproductible.
- [Plateformes d'agents — Architecture & gouvernance](110-mlops-cicd/115-plateformes-agents-gouvernance.md) : plateforme interne (paved road), plan de contrôle et plan d'exécution, architecture de référence, séparation cerveau, mains et session, exécution durable, isolation multi-tenant, identité déléguée ou autonome, standards d'identité, moteur de politiques, human-in-the-loop, registre et cycle de vie, Top 10 OWASP agentique, rayon d'impact et kill switch, audit, SLO, evals continues, coûts, AI Act, lock-in, critères de choix.

### 120 — Coûts & FinOps

- [Coûts d'inférence](120-couts-finops/121-couts-inference.md) : structure du coût d'un appel, prix input et output, prompt caching, coût du self-hosting, break-even API ou self-host, batch API, leviers techniques, contexte long, unit economics, GPU idle.
- [FinOps LLM](120-couts-finops/122-finops-llm.md) : visibilité des coûts, attribution aux équipes, budgets et garde-fous, routage comme premier levier, caches, pratiques GPU, arbitrage coût-qualité-latence, rôle du Lead.
- [Caching agressif](120-couts-finops/123-caching-agressif.md) : prompt caching (TTL, prix d'écriture et de lecture), structure de prompt stable, ce qui casse le cache, contexte append-only, requêtes parallèles et pré-chauffage, caches de réponses, d'embeddings et d'outils, invalidation, sécurité, pilotage.

### 130 — Fondamentaux LLM

Ce qu'il faut comprendre du modèle lui-même pour raisonner sur la qualité, le coût et le serving. À lire en prérequis.

- [Architecture Transformer](130-fondamentaux-llm/131-transformer-architecture.md) : chemin d'un token, attention, attention causale, multi-head, GQA et MQA, bloc MLP, résiduelles et normalisation, RoPE, coût quadratique, mémoire des poids, decoder-only ou encoder, modèle de base ou assistant.
- [Tokenisation](130-fondamentaux-llm/132-tokenisation.md) : BPE, byte-level, taille de vocabulaire, surcoût du français, limites au niveau des caractères, tokens spéciaux, chat templates, frontières de tokens, comptage, sécurité.
- [Embeddings & représentations](130-fondamentaux-llm/133-embeddings-representations.md) : apprentissage contrastif, similarités, bi-encoder ou cross-encoder, ColBERT, Matryoshka, préfixes, choix (MTEB), fine-tuning d'embeddings, changement de modèle, SPLADE, limites.
- [Recherche vectorielle & index ANN](130-fondamentaux-llm/134-recherche-vectorielle-ann.md) : brute force ou ANN, HNSW et ses paramètres, IVF, Product Quantization, quantization scalaire et binaire, DiskANN, filtrage, recall de l'index, pgvector ou base dédiée, exploitation, dimensionnement.
- [Pré-entraînement & scaling laws](130-fondamentaux-llm/135-pretraining-scaling-laws.md) : étapes de fabrication, données, scaling laws, Chinchilla, sur-entraînement pour l'inférence, 6ND, MFU, contamination, knowledge cutoff, capacités émergentes, mur des données.
- [Mixture of Experts](130-fondamentaux-llm/136-mixture-of-experts.md) : paramètres totaux et actifs, routeur, load balancing, expert partagé, spécialisation réelle, coût mémoire, expert parallelism, MoE ou dense.
- [Long contexte](130-fondamentaux-llm/137-long-contexte.md) : extension de RoPE, lost in the middle, needle in a haystack et RULER, context rot, long contexte ou RAG, coût, techniques de serving, limite de sortie, test sur sa tâche.
- [Modèles de raisonnement](130-fondamentaux-llm/138-modeles-raisonnement.md) : test-time compute, RLVR, budget de réflexion, facturation, quand ne pas les utiliser, prompting, fidélité de la chaîne de pensée, interleaved thinking, best-of-n.

### 140 — System design & produit

La partie qui assemble tout le reste : concevoir, fiabiliser et piloter une application LLM, niveau senior.

- [System design LLM — Méthode](140-system-design-produit/141-system-design-llm.md) : démarche, cadrage, échelle de complexité, triangle qualité-latence-coût, estimation de charge, composants, latence perçue, synchrone ou asynchrone, multi-tenant, modes de défaillance, présentation des arbitrages.
- [Fiabilité & résilience](140-system-design-produit/142-fiabilite-resilience-llm.md) : timeouts, retries, fallbacks, circuit breaker, sorties mal formées, dégradation gracieuse, rate limits, tâches longues, épinglage de version, SLO, chaos testing.
- [Hallucinations, grounding & abstention](140-system-design-produit/143-hallucinations-grounding.md) : types d'hallucinations, leviers, citations vérifiées, abstention, arbitrage avec la couverture, détection, calibration, slopsquatting, communication de l'incertitude.
- [UX de l'IA & human-in-the-loop](140-system-design-produit/144-ux-ia-human-in-the-loop.md) : copilote ou autopilote, validation humaine efficace, streaming, visibilité des agents, feedback, attentes, chat ou interface dédiée, automation bias, erreurs et refus.
- [Cas de system design](140-system-design-produit/145-cas-system-design.md) : support client, recherche documentaire, assistant de code, extraction à grande échelle, agent qui agit, chatbot grand public, assistant vocal, trame de réponse, erreurs d'entretien.
- [Choisir un modèle](140-system-design-produit/146-choix-modeles.md) : critères, limites des leaderboards, benchmarks, fermé ou open weights, licences, coût par tâche, architecture multi-modèles, lock-in, migration, veille.
- [Leadership technique](140-system-design-produit/147-leadership-technique-ia.md) : ce qui fait un senior, choix des cas d'usage, ROI, échec des POC, RFC et ADR, build ou buy, go / no-go, standards d'équipe, communication avec les décideurs, veille.

### 150 — Données & conformité

- [Données : curation & annotation](150-donnees-conformite/151-donnees-curation-annotation.md) : dimensions de qualité, déduplication, guide d'annotation, accord inter-annotateurs, qui annote, active learning, séparation dev et test, données de production, préparation d'un fine-tuning.
- [PII & confidentialité](150-donnees-conformite/152-pii-confidentialite.md) : où passent les données, détection, masquage, pseudonymisation et anonymisation, pseudonymiser avant l'appel, engagements des fournisseurs, logs, mémorisation, fuites entre utilisateurs, secrets, privacy by design.
- [Data flywheel & versioning](150-donnees-conformite/153-data-flywheel-versioning.md) : boucle d'amélioration, étapes, versioning des données, outils (DVC, lakeFS, Iceberg), lineage d'une eval, versioning d'un index, signaux implicites, pièges, priorisation.
- [RGPD appliqué aux LLM](150-donnees-conformite/154-rgpd-llm.md) : champ d'application, principes, base légale de la réutilisation, responsable et sous-traitant, transferts hors UE, droit à l'effacement, AIPD, décisions automatisées, données dans le modèle, mesures concrètes.
- [AI Act](150-donnees-conformite/155-ai-act.md) : approche par les risques, pratiques interdites, haut risque et obligations, fournisseur ou déployeur, transparence, modèles à usage général, calendrier, sanctions, plan d'action.
- [IA responsable](150-donnees-conformite/156-ia-responsable.md) : sources de biais, tests contrefactuels, métriques d'équité, model cards et system cards, datasheets, sycophancy, sécurité ou utilité, supervision humaine effective, référentiels (NIST AI RMF, ISO 42001).

### 160 — Multimodal & edge

- [Modèles vision-langage](160-multimodal-edge/161-modeles-vision-langage.md) : encodeur visuel et projecteur, coût en tokens, CLIP, faiblesses, injection visuelle, computer use, VLM ou OCR, évaluation, autres modalités.
- [Parsing de documents](160-multimodal-edge/162-document-parsing.md) : PDF natif ou scanné, analyse de layout, outils (Docling, Unstructured, services cloud, VLM), tableaux, figures, ColPali, chunking structurel, évaluation, exploitation.
- [Voix & agents temps réel](160-multimodal-edge/163-voix-temps-reel.md) : cascade ou speech-to-speech, budget de latence, réduction de latence, détection de fin de tour, barge-in, texte pour la voix, STT, évaluation, risques.
- [LLM locaux, on-prem & edge](160-multimodal-edge/164-llm-local-edge.md) : motivations, bande passante mémoire, llama.cpp et GGUF, outils locaux, Ollama ou vLLM, Apple Silicon, small language models, hybride local et cloud, flotte d'appareils, rentabilité du on-prem.
- [Computer use & agents navigateur](160-multimodal-edge/165-computer-use-agents-navigateur.md) : image ou structure (DOM, arbre d'accessibilité), grounding visuel, benchmarks (OSWorld, WebArena), coût et latence, injection par le contenu web, isolation, quand ne pas l'utiliser, computer use ou RPA, outils. Placée en section 160, la section 30 étant pleine.

---

## Maintenance

L'écosystème LLM change vite : noms de produits, versions et outils recommandés peuvent devenir obsolètes en quelques mois. Quand une réponse ne correspond plus à la réalité, on corrige la carte plutôt que d'en ajouter une nouvelle, pour que l'historique de révision de la carte soit conservé.

Le script `scripts/lint_flashcards.py` vérifie les conventions et calcule les statistiques :

```bash
python3 scripts/lint_flashcards.py                  # erreurs et avertissements
python3 scripts/lint_flashcards.py --stats          # statistiques par fiche
python3 scripts/lint_flashcards.py --update-readme  # met à jour la ligne « État au … »
python3 scripts/lint_flashcards.py --stale-months 6 # fiches à revérifier (défaut : 6 mois)
```

- **Erreurs** (bloquent le commit et la CI) : lien mort, nom de fichier en double, tags absents de la ligne 2, bloc avec deux lignes `?`, réponse vide, section `Mises en situation` ou `Connexions` manquante, dernier lien qui n'est pas le MOC, fiche absente du MOC, date `Vérifié le` illisible.
- **Avertissements** : réponse trop longue (110 mots hors code, 140 pour une mise en situation), liste de plus de 5 éléments (6 étapes pour une mise en situation), « Quelle différence… » au lieu de « À ne pas confondre », question en double, fiche citée par moins de 2 autres, fiche absente du README, `Vérifié le` trop ancien.

Le paquet Anki se régénère seul à chaque push (voir [Réviser sur Android avec Anki](#4-réviser-sur-android-avec-anki)). Changer `MODEL_ID` dans `scripts/export_anki.py` casserait la mise à jour des cartes déjà importées : ne pas y toucher.

Pour activer le hook pre-commit, une fois par clone : `git config core.hooksPath .githooks`.

Les fiches qui citent des produits, des versions ou des textes réglementaires portent une ligne `Vérifié le`. Le lint les signale au bout de 6 mois : on les relit, on corrige ce qui a changé, puis on met la date à jour.
