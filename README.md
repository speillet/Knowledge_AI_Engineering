# Knowledge Vault — AI Engineering

Un vault [Obsidian](https://obsidian.md) de **fiches de révision (flashcards) en français** qui couvre les compétences clés de l'**AI Engineering**. Le parcours va de l'utilisation des modèles jusqu'à leur mise en production et leur sécurisation.

Chaque fiche traite **un concept** en 5 à 22 cartes question/réponse, une dizaine en moyenne. Les fiches sont reliées entre elles par des liens, pour qu'on puisse passer d'un sujet à ses voisins, et elles se révisent en **répétition espacée**.

**État au 22 septembre 2026** : 64 fiches et 678 cartes, réparties en 12 sections.

---

## Structure du repo

```text
Knowledge_AI_Engineering/
├── README.md
├── .obsidian/                   # configuration Obsidian
├── .claude/skills/              # skills Claude Code versionnés (grilling, grill-me)
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
- Une section compte **au plus 9 fiches** (de `x1` à `x9`). Quand elle est pleine, la fiche va dans la section la plus proche de son sujet et le MOC la signale à côté de sa fiche d'origine. C'est le cas de `115-plateformes-agents-gouvernance.md` (section 110), la suite senior de `38-plateformes-agents.md`, car la section 30 est pleine.
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

1. Choisir la section et le prochain numéro libre, puis nommer le fichier en kebab-case, par exemple `25-rag-multimodal.md`. Si la section est pleine, appliquer la règle décrite dans [Structure du repo](#structure-du-repo).
2. **Le nom de fichier doit être unique dans tout le vault**, car Obsidian résout les liens `[[...]]` par nom de fichier, pas par chemin.
3. Rédiger les cartes au format ci-dessus.
4. Ajouter la fiche dans le sommaire du MOC, dans la section qui lui correspond, et dans la liste [Concepts couverts](#concepts-couverts) de ce README. Mettre à jour le nombre de fiches et de cartes en haut du README (voir [Maintenance](#maintenance)).
5. Ajouter des liens dans les deux sens : la nouvelle fiche cite ses voisines, et les voisines la citent dans leur section `Connexions`.
6. Vérifier qu'aucun lien ne pointe vers une fiche absente. Dans la vue graphe, désactiver le filtre **Existing files only** : les fiches citées mais inexistantes apparaissent alors comme des nœuds fantômes.

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

---

## Maintenance

L'écosystème LLM change vite : noms de produits, versions et outils recommandés peuvent devenir obsolètes en quelques mois. Quand une réponse ne correspond plus à la réalité, on corrige la carte plutôt que d'en ajouter une nouvelle, pour que l'historique de révision de la carte soit conservé.

Pour recompter les fiches et les cartes après un ajout :

```bash
grep -rl --include='*.md' '#flashcards' [0-9]*/ | wc -l      # fiches
find [0-9]*/ -name '*.md' -exec awk '$0=="?"' {} + | wc -l  # cartes
```
