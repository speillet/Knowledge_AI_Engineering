# Knowledge Vault — AI Engineering

Un vault [Obsidian](https://obsidian.md) de **fiches de révision (flashcards) en français** qui couvre les compétences clés de l'**AI Engineering**. Le parcours va de l'utilisation des modèles jusqu'à leur mise en production et leur sécurisation.

Chaque fiche traite **un concept** en une dizaine de cartes question/réponse. Les fiches sont reliées entre elles par des liens, pour qu'on puisse passer d'un sujet à ses voisins, et elles se révisent en **répétition espacée**.

**État au 22 septembre 2026** : 58 fiches et 580 cartes, réparties en 12 sections.

---

## Structure du repo

```text
Knowledge_AI_Engineering/
├── README.md
├── .obsidian/                   # configuration Obsidian
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
└── 120-couts-finops/
```

- Chaque **section** est un dossier numéroté par dizaine (`20-rag`, `30-agents`…).
- Chaque **fiche** porte un numéro qui reprend celui de sa section : `21-rag-fondamentaux.md` et `22-rag-avance.md` sont dans `20-rag/`.
- Exception : la section conteneurs garde sa propre numérotation, de `00-index.md` à `13-apptainer-inference-hpc.md`.
- Le point d'entrée est le **MOC** (Map of Content), [00-moc-ai-engineering.md](00-moc-ai-engineering.md).

---

## Comment l'utiliser

### 1. Ouvrir le vault

1. Installer [Obsidian](https://obsidian.md).
2. Choisir **Open folder as vault** et sélectionner le dossier du dépôt (`Knowledge_AI_Engineering` après un `git clone`).
3. Ouvrir [00-moc-ai-engineering.md](00-moc-ai-engineering.md).

### 2. Lire et naviguer

- **Suivre le parcours de lecture** du MOC, qui va dans cet ordre : prompt engineering, RAG, agents, automatisation et frameworks d'agents, fine-tuning, inférence, conteneurs, API layer, observabilité, sécurité, MLOps & CI/CD, coûts & FinOps.
- **Rebondir entre les concepts** : chaque fiche se termine par une section `Connexions` qui explique pourquoi les fiches liées sont liées. Des liens apparaissent aussi dans les réponses elles-mêmes.
- **Voir l'ensemble** : la **vue graphe** d'Obsidian montre comment les concepts s'articulent, et le panneau **Backlinks** liste les fiches qui citent la fiche ouverte.

### 3. Réviser en répétition espacée

Les fiches suivent la syntaxe du plugin communautaire **Spaced Repetition**. Il n'est pas installé par défaut :

1. **Settings → Community plugins** : activer les plugins communautaires, puis chercher et installer **Spaced Repetition**.
2. Le plugin retrouve automatiquement les fiches grâce au tag `#flashcards` qui figure en ligne 2 de chacune.
3. Dans les réglages du plugin, garder `?` comme séparateur des cartes multilignes. Choisir aussi `---` comme marqueur de fin de carte, car certaines réponses contiennent des lignes vides.
4. Lancer une révision avec l'icône du plugin dans la barre latérale, ou depuis la palette de commandes. La palette permet aussi de ne réviser que la note ouverte.

> Le plugin enregistre la planification des révisions **dans les fiches elles-mêmes**, sous forme de commentaires `<!--SR:...-->` placés après chaque carte. Si le vault est versionné avec git, ces commentaires apparaîtront dans les diffs.

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

## Connexions
- [[31-agents-fondamentaux|Agents]] — la boucle qui consomme les outils
- [[00-moc-ai-engineering|MOC AI Engineering]]
```

Les conventions à respecter :

- **Pas de frontmatter YAML.** Les tags sont écrits en texte sur la ligne 2.
- **Une carte** = la question, puis une ligne contenant seulement `?`, puis la réponse. Les cartes sont séparées par `---`.
- **Des réponses courtes**, avec les termes clés en gras, et un bloc de code quand c'est utile.
- **Une section `## Connexions`** à la fin, dont le dernier lien renvoie toujours au MOC.

## Ajouter une fiche

1. Choisir la section et le prochain numéro libre, puis nommer le fichier en kebab-case, par exemple `25-rag-multimodal.md`.
2. **Le nom de fichier doit être unique dans tout le vault**, car Obsidian résout les liens `[[...]]` par nom de fichier, pas par chemin.
3. Rédiger les cartes au format ci-dessus.
4. Ajouter la fiche dans le sommaire du MOC, dans la section qui lui correspond.
5. Ajouter des liens dans les deux sens : la nouvelle fiche cite ses voisines, et les voisines la citent dans leur section `Connexions`.
6. Vérifier qu'aucun lien ne pointe vers une fiche absente. Dans la vue graphe, désactiver le filtre **Existing files only** : les fiches citées mais inexistantes apparaissent alors comme des nœuds fantômes.

---

## Concepts couverts

La stack décrite par le vault, du haut vers le bas :

```text
App / Agent
    ↓
Gateway (Ingress → LiteLLM : auth, routing, budgets)
    ↓
Serveur d'inférence (vLLM/Triton/SGLang, KV cache, batching)
    ↓
Conteneur + GPU (Docker/K8s/Apptainer)
```

Deux sujets traversent toute la stack : l'**observabilité** (traces, coûts, evals) et la **sécurité** (injection, permissions, guardrails).

### 10 — Prompt engineering

- [Prompt engineering avancé](10-prompt-engineering/11-prompt-engineering-avance.md) : system prompt et user prompt, few-shot, chain-of-thought, self-consistency, délimiteurs, meta-prompting, prompts versionnés comme du code, anti-patterns.

### 20 — RAG

- [RAG — Fondamentaux](20-rag/21-rag-fondamentaux.md) : RAG ou fine-tuning, pipeline d'ingestion et de requête, stratégies de chunking, embeddings, bases vectorielles (HNSW, pgvector, Qdrant), top-k, grounding et citations, recall@k.
- [RAG — Avancé](20-rag/22-rag-avance.md) : recherche hybride (BM25, RRF), reranking, query rewriting, HyDE, filtrage par métadonnées et ACL, GraphRAG, agentic RAG, triade d'évaluation (RAGAS), « lost in the middle ».
- [Knowledge graphs & ontologies](20-rag/23-knowledge-graphs-ontologies.md) : triplets, RDF ou property graph (Cypher, GQL), ontologie et taxonomie, extraction par LLM sous schéma, résolution d'entités, graphe ou vecteurs, GraphRAG local et global, Text2Cypher, context graph, coûts.
- [Cognee](20-rag/24-cognee.md) : mémoire d'agent en knowledge graph, opérations remember, recall, improve et forget, mémoire permanente ou de session, stratégies de recherche, ontologie OWL, intégrations (plugin, MCP), limites.

### 30 — Agents

- [Fondamentaux des agents](30-agents/31-agents-fondamentaux.md) : workflow ou agent, pattern ReAct, composants d'un agent, human-in-the-loop, risques, conditions d'arrêt.
- [Tool calling](30-agents/32-tool-calling.md) : déclaration par JSON Schema, boucle d'appel, parallel tool calls, gestion des erreurs, rédaction des descriptions d'outils.
- [MCP — Model Context Protocol](30-agents/33-mcp.md) : problème M×N, host, client et serveur, tools, resources et prompts, transports stdio et HTTP, risques.
- [Harness & plugins](30-agents/34-harness-plugins.md) : rôle du harness, plugins, skills, hooks, permissions, sandbox, fichiers mémoire.
- [Context engineering](30-agents/35-context-engineering.md) : le contexte comme budget, context rot, compaction, mémoire court et long terme, sous-agents, prompt caching, contexte chargé au besoin (just-in-time).
- [Orchestration multi-agents](30-agents/36-orchestration-agents.md) : orchestrator-workers, supervisor, handoffs, evaluator-optimizer, état partagé, coût du multi-agent, protocole A2A.
- [Frameworks d'agents](30-agents/37-frameworks-agents.md) : LangChain, LangGraph, CrewAI, Google ADK, OpenAI Agents SDK, Claude Agent SDK, LlamaIndex, framework ou code maison.
- [Plateformes d'agents](30-agents/38-plateformes-agents.md) : différence avec un framework, runtime managé, registre MCP, identité des agents, offres cloud et open source, build ou buy.
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

### 50 — Fine-tuning

- [Fine-tuning & adaptation](50-fine-tuning/51-fine-tuning-adaptation.md) : quand fine-tuner, SFT, full fine-tuning ou PEFT, LoRA, QLoRA, RLHF, DPO, distillation, multi-LoRA, catastrophic forgetting.

### 60 — Inférence LLM

- [KV cache & attention](60-inference-llm/61-kv-cache-attention.md) : taille du cache, PagedAttention, prefix caching, quantization du cache, coût des contextes longs.
- [Optimisations d'inférence](60-inference-llm/62-optimisations-inference.md) : prefill et decode, continuous batching, quantization (AWQ, GPTQ, FP8), speculative decoding, FlashAttention, parallélisme tensor et pipeline, chunked prefill, désagrégation prefill/decode.
- [Guided generation](60-inference-llm/63-guided-generation.md) : masquage des logits, JSON Schema, regex et grammaires, XGrammar et Outlines, structured outputs des API, validation métier.
- [Métriques d'inférence & SLO](60-inference-llm/64-metriques-slo-inference.md) : TTFT, TPOT, throughput, goodput, percentiles, définition d'un SLO, signaux d'autoscaling, benchmarks.
- [Probabilités & sampling](60-inference-llm/65-probabilites-sampling.md) : logits et softmax, température, greedy, top-k, top-p, min-p, réglages par cas d'usage, logprobs, probabilité d'une séquence, perplexité, calibration, speculative decoding et distribution.
- [Prefix caching & RadixAttention](60-inference-llm/66-prefix-caching-radix-attention.md) : prefix caching de vLLM, arbre radix de SGLang, éviction, ordonnancement et routage cache-aware, offloading du KV cache (LMCache), limites, canal auxiliaire temporel, métriques.
- [Speculative decoding](60-inference-llm/67-speculative-decoding.md) : brouillon et vérification en une passe, pourquoi c'est presque gratuit, règle d'acceptation sans perte, gain selon le taux d'acceptation, choix de k, types de brouillons (petit modèle, n-grammes, EAGLE, Medusa, MTP), vérification en arbre, quand ça aide ou nuit, configuration vLLM, coûts, métriques d'acceptation, validation d'un déploiement.
- [Quantization](60-inference-llm/68-quantization.md) : intérêt en mémoire et en vitesse, formats (FP8, INT8, INT4, NVFP4, MXFP4), weight-only ou W8A8, granularité des échelles, outliers d'activation (SmoothQuant, rotations), PTQ ou QAT, GPTQ, AWQ, GGUF, NF4, choix de la méthode selon le matériel, calibration, mesure de la perte, divergence KL et flips, validation avant déploiement, suivi en production, outils (llm-compressor, Model Optimizer, vLLM).

### 70 — Conteneurs & infra

- [Index Conteneurs](70-containers-infra/00-index.md) : sommaire des 13 fiches de la section, chaînes à retenir, et une carte sur l'intérêt des conteneurs pour servir des modèles.
- [OCI](70-containers-infra/01-oci.md) : rôle de l'Open Container Initiative, spécifications image, runtime et distribution.
- [Docker, images & registries](70-containers-infra/02-docker-images-registries.md) : rôle de Docker et différence avec OCI, image ou conteneur, compatibilité « Docker/OCI », registries et workflow push/pull.
- [containerd & runc](70-containers-infra/03-containerd-runc.md) : rôle de containerd, rôle de runc, relation entre les deux.
- [Kubernetes, kubelet & CRI](70-containers-infra/04-kubernetes-kubelet-cri.md) : Pod, Deployment, Service, control plane, kubelet, CRI (containerd, CRI-O), scheduler, requests et limits, probes.
- [Docker & Kubernetes](70-containers-infra/05-docker-kubernetes.md) : dockershim et sa suppression, architecture actuelle, images Docker exécutées sans Docker Engine.
- [Apptainer & Singularity](70-containers-infra/06-apptainer-singularity.md) : usage en HPC, filiation Singularity → Apptainer, format SIF, import d'images Docker, `--nv`.
- [Synthèse conteneurs](70-containers-infra/07-synthese-containers.md) : cartes de révision transverses (OCI, CRI et SIF, chaînes Kubernetes et image, accès GPU, serveurs d'inférence, stockage des poids).
- [Primitives Linux & fondamentaux Docker](70-containers-infra/08-linux-primitives-docker-fondamentaux.md) : namespaces et cgroups, conteneur ou VM, layers, ordre du Dockerfile et cache, volumes et bind mounts, port mapping.
- [GPU en conteneur](70-containers-infra/09-gpu-conteneurs.md) : NVIDIA Container Toolkit, driver et CUDA, images CUDA, GPU Operator, Apptainer `--nv`, ROCm.
- [Images & poids de modèles](70-containers-infra/10-images-modeles-poids.md) : poids dans l'image ou séparés, cold start, safetensors ou pickle, GGUF, modèles distribués comme artefacts OCI.
- [Serveurs d'inférence LLM](70-containers-infra/11-serveurs-inference-llm.md) : vLLM, API compatible OpenAI, multi-LoRA, SGLang, TensorRT-LLM et Triton, TGI, llama.cpp et Ollama.
- [Kubernetes GPU & inférence](70-containers-infra/12-kubernetes-gpu-inference.md) : device plugin, ressource `nvidia.com/gpu`, MIG, time-slicing, KServe, autoscaling (HPA, KEDA).
- [Apptainer & inférence HPC](70-containers-infra/13-apptainer-inference-hpc.md) : Apptainer ou Docker en HPC, modèle de sécurité, intégration Slurm, `--nv`, poids montés depuis le système de fichiers partagé, images SIF.

### 80 — API layer & routing

- [LiteLLM (API layer)](80-api-layer-routing/81-litellm-api-layer.md) : SDK ou proxy, virtual keys, budgets, rate limits, fallbacks, load balancing, callbacks d'observabilité.
- [Routing LLM](80-api-layer-routing/82-routing-llm.md) : routage statique, par règles ou sémantique, RouteLLM, cascade, routage selon la charge, cache sémantique.
- [Ingress & API gateway](80-api-layer-routing/83-gateway-ingress.md) : Ingress controller, TLS, Gateway API, rate limiting, streaming SSE.

### 90 — Observabilité & evals

- [Langfuse & observabilité LLM](90-observabilite-evals/91-langfuse-observabilite.md) : traces, spans et generations, sessions, prompt management, scores, LLM-as-judge, datasets.
- [ChainForge & évaluation de prompts](90-observabilite-evals/92-chainforge-evals-prompts.md) : comparer prompts et modèles, golden dataset, evals automatiques, tests de régression.
- [Monitoring de l'inférence & de l'usage](90-observabilite-evals/93-monitoring-inference.md) : couches à monitorer, métriques vLLM et GPU (DCGM), usage par équipe, finish_reason, validations de chaque réponse, signaux de qualité sans vérité terrain, erreurs et disponibilité, traces OpenTelemetry GenAI, dashboard, alertes, contrôles avant mise en production, détection de régression, journalisation des prompts.

### 100 — Sécurité & guardrails

- [Sécurité LLM & guardrails](100-securite-guardrails/101-securite-llm-guardrails.md) : OWASP Top 10 LLM, prompt injection directe et indirecte, « lethal trifecta », exfiltration, excessive agency, guardrails (Llama Guard, NeMo Guardrails), red teaming.

### 110 — MLOps & CI/CD

- [MLOps & LLMOps — Fondamentaux](110-mlops-cicd/111-mlops-llmops-fondamentaux.md) : DevOps ou MLOps, spécificités du LLMOps, ce qu'il faut versionner, model registry, lineage, reproductibilité, environnements dev/staging/prod, rôle du Lead.
- [CI/CD des modèles](110-mlops-cicd/112-cicd-modeles.md) : eval gates, artefact déployé, blue/green et canary, shadow deployment, rollback, GitOps, tests d'une app LLM, prompts en CI, pipeline complet.
- [Monitoring, drift & boucle de feedback](110-mlops-cicd/113-monitoring-drift-feedback.md) : data drift et concept drift, drift d'une app LLM et d'un RAG, qualité en production, boucle de feedback, quand ré-entraîner, mises à jour des modèles API, alertes.
- [Reproductibilité & variance](110-mlops-cicd/114-reproductibilite-variance.md) : non-déterminisme à température 0, invariance au batch, seed, appel rejouable, tests sur des sorties variables, erreur standard et intervalles de confiance, comparaison appariée, pass@k et pass^k, variance du LLM-as-judge, fine-tuning reproductible.

### 120 — Coûts & FinOps

- [Coûts d'inférence](120-couts-finops/121-couts-inference.md) : structure du coût d'un appel, prix input et output, prompt caching, coût du self-hosting, break-even API ou self-host, batch API, leviers techniques, contexte long, unit economics, GPU idle.
- [FinOps LLM](120-couts-finops/122-finops-llm.md) : visibilité des coûts, attribution aux équipes, budgets et garde-fous, routage comme premier levier, caches, pratiques GPU, arbitrage coût-qualité-latence, rôle du Lead.
- [Caching agressif](120-couts-finops/123-caching-agressif.md) : prompt caching (TTL, prix d'écriture et de lecture), structure de prompt stable, ce qui casse le cache, contexte append-only, requêtes parallèles et pré-chauffage, caches de réponses, d'embeddings et d'outils, invalidation, sécurité, pilotage.

---

## Maintenance

L'écosystème LLM change vite : noms de produits, versions et outils recommandés peuvent devenir obsolètes en quelques mois. Quand une réponse ne correspond plus à la réalité, on corrige la carte plutôt que d'en ajouter une nouvelle, pour que l'historique de révision de la carte soit conservé.
