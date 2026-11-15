# Knowledge Vault — AI Engineering

An [Obsidian](https://obsidian.md) vault of **English flashcards** covering the core skills of **AI engineering**. The learning paths run from choosing between rules, classical ML and LLMs to deploying and securing them, with the data and distributed systems foundations needed for reliable applications.

Each topic covers **one concept** in 11–38 question-and-answer cards, about eighteen on average, and ends with **scenarios**: practical cases to diagnose, design or make tradeoffs about. Links connect related topics, and the cards support **spaced repetition**.

**As of 15 November 2026**: 153 topics and 2,775 cards across 17 sections, including 372 scenarios and 208 do-not-confuse cards.

---

## Repository structure

```text
Knowledge_AI_Engineering/
├── README.md
├── docs/                       # practical courses, review and maintenance
├── examples/data-engineering/  # local SQL workshop with synthetic data
├── examples/ai-decisions/      # metric, human review and model choice in Python
├── examples/verifiable-rag/    # proofs, rights, versions and abstention without LLM
├── examples/agentic-support/    # LangChain, LangGraph, Langfuse, API and recovery tests
├── .obsidian/                   # configuration Obsidian
├── .claude/skills/ # versioned Claude Code skills (grilling, grill-me)
├── scripts/lint_flashcards.py   # verification of conventions + statistics
├── scripts/export_anki.py       # export package Anki (.apkg) for AnkiDroid
├── scripts/assign_card_ids.py   # permanent identifiers of new cards
├── scripts/sr_plugin.py         # reading of the topics by the Spaced Repetition plugin, verified by the lint
├── scripts/retired_cards.json   # cards removed from the vault, to be removed from Anki
├── scripts/sync_catalog.py      # generation of README and MOC summaries
├── scripts/sections.json        # Titles and introductions of the sections
├── tests/                       # tests of parser, lint, summaries and export
├── scripts/requirements.txt     # Anki Export Dependencies
├── requirements-dev.txt # development dependencies: export Anki, ruff, mypy
├── Makefile                     # orders of the vault: make check reproduces the CI
├── pyproject.toml               # configuration of ruff and mypy
├── .githooks/pre-commit         # runs make pre-commit before each commit
├── .github/workflows/           # check in CI, then Anki package released in release
├── .github/dependabot.yml       # monthly updates of Python actions and dependencies
├── 00-moc-ai-engineering.md     # root map: reading route, agentic route, summary
├── 10-prompt-engineering/        # techniques, automatic optimization (DSPy), production prompts
├── 20-rag/                      # RAG, graphs, chunking, text-to-SQL, search agents
├── 30-agents/                   # loop, tools, MCP, context, multi-agent, platforms, memory
├── 40-automation/           # workflows, LangChain, LangGraph, CrewAI, patterns, code agents
├── 50-fine-tuning/              # fine-tuning, alignment, distillation, distributed, RL, diagnostic
├── 60-llm-inference/            # KV cache, optimisations, sampling, quantization, roofline
├── 70-containers-infra/         # contains its own index: 00-index.md
├── 80-api-layer-routing/        # gateway, routing, ingress, streaming, protocols agentic
├── 90-observability-evals/      # traces, monitoring, evals, judges, debugging, statistics
├── 100-security-guardrails/     # Guardrails, threats and agent defenses, MCP, DevSecOps
├── 110-mlops-cicd/              # MLOps, LLMOps, CI/CD, training, releases, features, batch, monitoring, SRE
├── 120-costs-finops/            # inference costs, FinOps, caching
├── 130-llm-fundamentals/         # Transformer, tokenization, embeddings, MoE, reasoning
├── 140-system-design-product/    # system design, reliability, UX, batch, idempotency, transactions
├── 150-data-compliance/       # SQL, modeling, storage, pipelines, corpus, quality and compliance
├── 160-multimodal-edge/          # VLM, document parsing, voice, local LLM, computer use
└── 170-classical-ml/            # validation, calibration, ranking, forecast, anomalies, explicability, causality
```

- Each **section** is a folder numbered by ten (`20-rag`, `30-agents`...).
- Each **topic** has a number derived from its section: `21-rag-fundamentals.md` and `22-advanced-rag.md` are in `20-rag/`.
- Exception: the container section keeps its own numbering, from `00-index.md` to `13-apptainer-inference-hpc.md`.
- Numeric prefixes remain stable. **A section may exceed nine topics**: after `39-agent-memory.md`, use `30-010-new-topic.md`, then `30-011-another-topic.md`, in `30-agents/`. The prefix designates the section, the second number its rank. The catalogs sort both numbering conventions together; choose the section according to the subject.
- The entry point is **MOC** (Map of Content), [00-moc-ai-engineering.md](00-moc-ai-engineering.md).

---

## How to use it

### 1. Open vault

1. Install [Obsidian](https://obsidian.md).
2. Choose **Open folder as vault** and select the repository folder (`Knowledge_AI_Engineering` after a `git clone`).
3. Open [00-moc-ai-engineering.md](00-moc-ai-engineering.md).

### 2. Read and navigate

- **Deepen all existing cards**: The [Review of 14 November](docs/topic-expansion-2026-11-14.md) details the new 271 cards, including 23 calculations, 18 in-depth or corrected answers, sources and verifications. The 150 cards now cover 2,711 cards.
- **Implement and validate an agent platform**: the [eight-step route](docs/platform-agents-inference-learning-path.md) tracks a support agent, from the architecture and API contracts to the quality, load and recovery tests. Each step connects the relevant topics to a deliverable and a passing criterion.
- **Assess agent skills**: Three topics separate controls. The [Methodological topic](90-observability-evals/90-014-agent-skill-evaluation.md) handles trigger, paired executions with and without skills, assertions, and skillsbench results. The [File Format](90-observability-evals/90-015-agent-skills-format-skills-ref.md) covers the Agent Skills and `skills-ref` specification. The [Harbor topic](90-observability-evals/90-016-harbor-agent-evaluation.md) explains container tasks, checkers, skill injection, and reward hacking.
- **Assess outputs and responses**: The [Dedicated topic](90-observability-evals/90-010-llm-response-evaluation.md) gathers accuracy, completeness, instructions, references and metrics according to the task. The 5 stage of the platform path applies a grid to complete, partial and false support responses.
- **Apply metrics to decisions**: the [atelier Python local](examples/ai-decisions/README.md) offers four corrected exercises on prevalence, human review, model choice and full document quality, without API or GPU.
- **Build a verifiable RAG**: the [Local workshop in ten cases](examples/verifiable-rag/README.md) compares naive and filtered research, with versioned corpus, access rights, contradictions, quotes and partial answers. The [rights topic and versions](20-rag/20-010-rag-permissions-versions.md) brings the rules of production; the [Review of 13 October](docs/rag-expansion-2026-10-13.md) specifies the additions and the next priorities.
- **Check references**: The [Audit of November 13](docs/reference-currency-check-2026-11-13.md) distinguishes between confirmations and corrections targeted at MLOps, MCP, hosting, OWASP and AI Act. It specifies the limits of the control and keeps the overall dates when only part of the topic has been reviewed.
- **Check out the relevant reviews**: the [Review of 11 October](docs/relevance-review-2026-10-11.md) specifies the corrections and the 33 cards added in two passes, as well as the verification perimeter. The [17 octobre](docs/relevance-review-2026-10-17.md) reviews the duplicates removed and the corrected dated facts. The [Review of 20 October](docs/mlops-card-expansion-2026-10-20.md) enriches the shortest cards and adds a MLOps part on the drive pipelines and drift measurement.
- **Learn before multiplying revisions**: The [Learning Guide](docs/learning-with-flashcards.md) offers a progressive start, scoring criteria and exercises to check the transfer. The [Review of 9 October](docs/learning-review-2026-10-09.md) details the pedagogical corrections and the new application cards.
- **Industrialize an ML model**: the [MLOps Complete Course](docs/production-mlops-learning-path-2026-11-12.md) follows a termination score, from available data at the right time to release, scoring, monitoring and recovery. The section has nine cards and 196 cards; this pass adds 68 cards and deepens 33 answers.
- **Understand prefill, RadixAttention and speculative decoding**: the [Detailed route](docs/understanding-prefill-radix-speculation-2026-11-12.md) connects prompt calculation, prefix sharing and draft verification, with trees, timeline and probabilistic correction. The three cards total 76 cards; this pass also develops the shortest 110 answers.
- **Deepen decisions and verify limits**: the [Review of November 12](docs/cross-topic-review-2026-11-12.md) enriches the 147 cards with new 147 cards, including 15 calculations, and specifies 10 existing answers. It details the corrections, the primary sources consulted and the verification scope.
- **Expand existing answers**: the [Transversal Enrichment in November](docs/practical-card-expansion-2026-10-22.md#cross-sectional-supplement-of-november-2026) covers the 147 files, with 682 separate answers enriched with examples, limits and decision criteria after two passes. Anki questions and identifiers remain unchanged; the balance sheet distinguishes the integrated local work and complements, not to mention twice an answer taken again.
- **Follow the reading route** of the MOC, which goes in this order: classic ML and validation, Basic LLM (prerequisites), Fast engineering, RAG, Agents, automation and agent frameworks, fine-tuning, Inference, containers, API Layer, Observability, security, MLOps & CI/CD, Cost & FinOps, data & compliance, multimodal & edge, then system design & product, who assembles everything. The MOC also offers a **AI Agent Engineer**, Who follows in 8 step topics on the agents distributed in several sections.
- **Bounce between concepts**: Each topic ends with a `Connections` section that explains why linked topics are linked. These links are **reciprocal**: if A cites B, B cites A. Links also appear in the answers themselves.
- **Complete the senior foundations**: the dedicated MOC path links selection and validation of models, contracts and data ingestion, then idempotency and transactions. The [Review of the three priorities](docs/senior-foundations-2026-10-06.md) details the seven added files and their validation.
- **Practice the senior level**: the [Relevance report for October 7](docs/senior-learning-path-relevance-2026-10-07.md) distinguishes common ground and specializations, then offers workshops with deliverables: experimental decision, calibration, training diagnosis, incident and transmission. The corresponding course is included in the MOC.
- **Expanding predictive skills** : [Review of 8 October](docs/new-ai-skills-2026-10-08.md) submits five new factsheets on the recommendation, the temporal forecast, the anomalies, Explainability and causality, with targeted exercises.
- **See the set**: Obsidian's **graph view** shows how the concepts fit together, and the **Backlinks** panel lists the topics that quote the open topic.
- **Control inference performance**: the [Audit of October 8](docs/llm-inference-audit-2026-10-08.md) connects metrics, benchmarks, capacity, optimizations and cost per useful task, with a coverage matrix and four workshops.
- **Master the data that powers AI**: the [audit data engineering](docs/data-engineering-audit-2026-10-09.md) connects the eight new topics to contracts, the CDC and existing features. It distinguishes base and deepening, with five workshops, including a [Executable SQL Workshop](examples/data-engineering/sql_workshop.py). The MOC offers the corresponding path.

### 3. Review with spaced repetition

The files follow the syntax of the community plugin **Spaced Repetition**, which is not installed by default:

1. In **Settings → Community plugins**, enable community plugins, then find and install **Spaced Repetition**.
2. The plugin discovers topics through the `#flashcards` tag on line 2 of each file.
3. Configure the plugin:
   - **Separator for multiline flashcards**: keep `?`.
   - **Characters denoting the end of clozes and multiline flashcards**: enter `---`. This is essential: otherwise, each answer stops at its first blank line.
   - **Convert folders to decks and subdecks**: enable it to get a deck per section.
   - **Show context in cards**: enable it to display the topic title above each question.
4. Start a review from the sidebar icon or command palette. The palette also lets you review only the open note.

> The plugin stores scheduling **in the cards themselves**, as `<!--SR:...-->` comments after each card. These comments appear in Git diffs when you version the vault.

### 4. Review on Android with Anki

Every push to `main` generates an Anki package and publishes it at a stable address:

[Download the Anki package](https://github.com/speillet/Knowledge_AI_Engineering/releases/download/anki/ai-engineering.apkg).

1. Install **AnkiDroid** from the Play Store or F-Droid.
2. Download the package on your phone and open it with AnkiDroid. It imports into **AI Engineering**, organized by section and topic.
3. To update, download and import it again. Each note has a permanent `<!--anki:…-->` identifier, so rewording a question or renaming a file can update the existing note while retaining its review history.
   - Keep that identifier when editing a card.
   - A new question receives a new identifier through `scripts/assign_card_ids.py`.
   - Retired cards are re-exported suspended with the `retired` tag. Search for `tag:retired` in Anki to delete them.
4. Anki and Obsidian maintain separate review schedules; their progress is not synchronized.

The English migration preserves note GUIDs, the model ID and the existing deck IDs. See the [migration report](docs/english-migration-2026-11-15.md) for the compatibility checks.

To generate the package locally:

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r scripts/requirements.txt
python3 scripts/export_anki.py      # writes dist/ai-engineering.apkg
```

### Without Obsidian

The files are simple Markdown and can be read in any editor. Only links in `[[...]]` format are not clickable outside Obsidian.

---

## Format of a topic

```markdown
# Tool calling — Flashcards
Tags: #flashcards #ai-engineering #agents #tool-calling #llm
<!-- summary: Declaration, execution and validation of tool calls. -->


What is Tool Calling?
?
The **tool calling** allows the model to request an operation by producing a tool name and structured arguments. The application validates the request, executes the allowed function, and returns its result to the model to continue the task.

For example, `order_status(id)` consults a business source before responding to the client. A call in accordance with the schema does not guarantee correct arguments or an authorized action: these controls remain in the application.

---

Does the model run the tools itself?
?
**No.** The model produces a request; the [[34-harness-plugins|harness]] decides if it is allowed and launches the tool. It also handles invalid arguments, delays, and errors, and then forwards an observation to the model.

This separation limits accessible resources and possible effects. A prompt statement does not replace a permission check at runtime.

---

## Scenarios

Scenario: your agent has 40 tools and often gets the wrong tool. How do you improve the situation?
?
1. **Reduce choice**: expose only useful tools to the current task.
2. **Care for descriptions**: Explicit name, use case, which the tool does not do.
3. **Check arguments**: Use accurate schemas and errors to correct the call.
4. **Measure the result**: replay representative tasks and compare tool selection, success and number of calls.

**Trap**: Add an additional tool to fix previous errors.

---

## Connections
- [[31-agent-fundamentals|Agents]] — the loop that consumes the tools
- [[00-moc-ai-engineering|MOC AI Engineering]]
```

This example shows a topic before the permanent identifiers are assigned. Launch `python3 scripts/assign_card_ids.py` after it is created; then keep the identifiers during reformulations.

Conventions:

- **No YAML frontmatter.** Write tags as plain text on line 2.
- **One card** consists of a question, a line containing only `?`, and an answer. Separate cards with `---`.
- **Self-contained, sufficiently explained answers**: lead with the direct answer, then explain the mechanism, give an example or state useful limitations. Bold key terms. Explain the assumptions and interpretation of commands, calculations and diagrams; code alone is insufficient.
- Include **`## Scenarios`** before Connections, with at least 2 cards (3 for advanced topics). Each question starts with `Scenario:` and describes a concrete case in one paragraph. Answers follow 3–6 steps and may end with a pitfall to avoid.
- End with **`## Connections`**, whose last link returns to the MOC. Give each link a short rationale and make links reciprocal.
- **One focused question, a developed answer**: keep one main concept per card. Split lists longer than 5 items into themed cards whose questions provide a useful cue. Length is a readability signal, not a quality measure; avoid repeating the question.
- Use **“Do not confuse: X and Y?”** for commonly confused concepts: OCI and CRI, tag and digest, routing and fallback, recall and precision, few-shot and fine-tuning.
- Include **reasoning cards**, not only definitions: “When should you avoid…?”, “What happens if…?”, and **“Calculation:…”** questions about VRAM, throughput, cost or sample size.
- **Questions must make sense alone**, because review mixes cards. Name the subject: “What is a thread in LangGraph?”, rather than “What is a thread?”. Avoid “And X?” or “How does it work?”, which depend on the previous card.
- **Calculations must be solvable before reading the answer**. Supply the data, units, scope and assumptions unless recalling them is explicitly part of the task. Identify fictional prices and approximations. Show the formula, result and justified conclusion on the back; neighboring cards should not give away the result.
- **One concept, one reference card**: define a concept in its dedicated card. Other cards link to it, apply it or use it in a scenario. Search the vault before adding another definition.
- **Make success assessable**: specify what to explain, compare, calculate or decide. Do not present conditional rules as universal. Examples and limitations support understanding; they should not become an implicit recital. The [learning guide](docs/learning-with-flashcards.md) explains how to assess each card type.
- **Avoid product lists to memorize**. “Which parsing tools should you know?” is hard to grade and ages quickly. Ask a decision question instead: “Which parsing tool fits high-volume scans, and which fits confidential data?”.
- **One idea per card**: split answers that combine two unrelated mechanisms, product lists or incidents.
- Prefer **numerical reference values and executable examples**—commands, configuration and code—to abstract claims.
- Add **`Verified on: …`** immediately after tags for topics citing products, versions or regulations. Put primary references in `## Sources` before `## Connections`: official documentation, a versioned specification, the author's paper or a regulatory text. Adding a reference alone does not justify changing the verification date.
- Add **`<!-- summary: … -->`** after tags and any verification date, **followed by two blank lines**. It supplies the README catalog; topic titles supply both catalogs.
- Put a permanent **`<!--anki:…-->` identifier at the end of each question**, for example `What is RAG? <!--anki:…-->`, using the assignment script. It is invisible in the rendered text and excluded from the answer. Keep the identifier when rewording a card; a question with a different meaning gets a new one.
- **Do not begin a card line with an HTML comment**, except `<!--SR:`. The Spaced Repetition plugin also skips the following line. An identifier on its own line caused the answer to disappear; the same behavior explains the two blank lines after the summary. Lint replays the plugin parser in `scripts/sr_plugin.py` and detects differences from Anki export.
- **To retire a card**, remove its block and move its identifier, question and reason to `scripts/retired_cards.json`, for example `{"id": "…", "question": "…", "reason": "duplicate of 95-llm-as-judge"}`. Export includes it suspended with the `retired` tag.
- In an index with introductory text, place `---` and then **`## Cards`** before the first question. The parser excludes the introduction and catalog.

## Add a topic

1. Choose the section and the next free number, then name the file in kebab-case, for example `28-rag-multimodal.md`. To exceed nine topics, use the extended numbering described in [Structure of the Repo](#repository-structure).
2. **The filename must be unique throughout the vault**, because Obsidian resolves `[[...]]` links by filename, not by path.
3. Write the cards in the format above, fill in the `summary` comment and the sources if the file is dated, and then launch `python3 scripts/assign_card_ids.py`.
4. Launch `python3 scripts/sync_catalog.py` to regenerate the MOC and README catalogs. For a new section, first fill in `scripts/sections.json`. The reading paths remain editorial. Update the figures with `python3 scripts/lint_flashcards.py --update-readme`.
5. Add links in both directions: the new file cites its neighbors, and the neighbors quote it in their section `Connections`. Also connect the files that **mention** the notion treated without binding. The lint indicates any link without return.
6. Launch `python3 scripts/lint_flashcards.py`: it indicates dead links, missing topics from the MOC or README, little connected topics and format deviations (see [Maintenance](#maintenance)).

---

## Explore agentic applications

The [Agentic path of production](docs/agentic-stack-audit-2026-10-09.md) connects LangChain contracts, LangGraph resume, CrewAI execution, Langfuse instrumentation, experiments and application architecture. It adds diagnostic maps and scenarios to the basic sheets.

The [Executable Support Workshop](examples/agentic-support/README.md) allows you to test approval, refusal, isolation, events and breakdown after business effect. It uses a simulated model and a local Langfuse export: no API key is required. The documentation distinguishes technical tests from evaluations to be carried out with real models and services.

---

## Concepts covered

The stack described by the vault, from top to bottom:

```text
App / Agent
    ↓
Agent platform (runtime, sandbox, MCP tool gateway, identity, policies)
    ↓
Gateway LLM (Ingress → LiteLLM : auth, routing, budgets)
    ↓
Inference server (vLLM/SGLang/TensorRT-LLM, KV cache, batching, quantization)
    ↓
Container + GPU (Docker/K8s/Apptainer)
```

Three topics cross the stack: **observability** (traces, metrics, evals), **safety** (injection, lesser privilege, sandbox, DevSecOps) and **costs** (FinOps).

<!-- catalog:begin -->

### 10 — Prompt engineering

- [Advanced prompt engineering](10-prompt-engineering/11-advanced-prompt-engineering.md) : system prompt and user prompt, few-shot, few-shot or fine-tuning, chain-of-thought (cost, tags), self-consistency and its limits, delimiters, decomposition into calls, meta-prompting, prompt versions as code, anti-patterns, metamorphic tests, removal of instructions, limit examples.
- [Automatic Prompt Optimization (DSPy)](10-prompt-engineering/12-automatic-prompt-optimization.md) : meta-prompting or metric-guided optimization, DSpy (signatures, modules, BootstrapFewShot optimizers, MIPROv2, GEPA), APE, OPRO, TextGrad, when to use it or not, over-learning, transfer between models, prompt optimization or fine-tuning, critical optimization constraints, constrained goal, research budget.
- [Prompts in production](10-prompt-engineering/13-production-prompts.md) : Prompt bricks, placement of long documents, reasoned instructions, role limits, prompt a reasoning model, templates and user data, registry and versioning, prompt in the code or in a registry, portability between models, language, length control, migration of the output contract, effective rendering, missing data.

### 20 — RAG

- [RAG — Fundamentals](20-rag/21-rag-fundamentals.md) : RAG or fine-tuning, ingestion and query pipeline, chunking strategies, embeddings, vector bases (HNSW, pgvector, Qdrant), top-k, grounding and citations, recall@k, when not to do RAG, diagnostic with reference context, evidence budget, sub-question coverage.
- [RAG Advanced](20-rag/22-advanced-rag.md) : hybrid search (BM25, RRF), ranking, query rewriting, HyDE and its limits, filtering by metadata and ACL, GraphRAG, agentic RAG, "lost in the middle", production problems (fresher, rights, re-indexing), RRF fusion and score scales, diversity of results, ceiling of the ranking.
- [Knowledge graphs & ontologies](20-rag/23-knowledge-graphs-ontologies.md) : triplets, RDF or property graph (Cypher, GQL), ontology and taxonomy, extraction by LLM under schema, entity resolution, graph or vectors, local and global GraphRAG, Text2Cypher, context graph, costs, source of relations, open world, negation of relations.
- [Cognee](20-rag/24-cognee.md) : Agent memory in knowledge graph, operations remember, recall, improve and forget, permanent or session memory, search policies, OWL ontology, integrations (plugin, MCP), limits, memory reversibility test, memory utility test, controlled reconstruction.
- [Advanced Chunking & Contextual Retrieval](20-rag/25-chunking-contextual-retrieval.md) : chunks without context, contextual retrieval (gain, cost, prompt caching), late chunking, chunk size, small-to-big, semantic and propositional chunking, breadcrumb and metadata, policy comparison to call@k, calculation of overlap overcost, tables and units, parent-child under budget.
- [Text-to-SQL & structured data](20-rag/26-text-to-sql.md) : text-to-SQL or RAG, prompt content, schema linking, semantic layer, execution security, correction loop, exact match or execution compliance, benchmarks (Spider, BIRD, Spider 2.0), ambiguous questions, limits of SQL validation on sample, join fan-out, NULL values.
- [Search agents (deep research)](20-rag/27-search-agents-deep-research.md) : RAG or search agent, search loop, parallel subagents, search tools, reliable citations, risks (sources, injection, bias), evaluation (coverage, BrowseComp), calculation of the cost of a report, when not to use it, independence of web evidence, coverage of assertions, search stop criterion.
- [RAG in production: rights, versions & abstention](20-rag/20-010-rag-permissions-versions.md) : identity and permissions, pre-exposure filtering, recall under filters, time validity, source priority, deletions and caches, versioned citations, abstention and regression tests, revocation of rights during generation, proof of absence, consistency of snapshots.

### 30 — Agents

- [Basics of](30-agents/31-agent-fundamentals.md) : workflow or agent, ReAct pattern, minimal agent components, three forms of human-in-the-loop, risks and parades, cost orders of magnitude, stop conditions, end-of-task proof, environmental observableness, success and trajectory.
- [Tool calling](30-agents/32-tool-calling.md) : tool definition, controlled parallel calls, tool calling or MCP, validation of arguments, errors and timeouts, operation statuses, pagination and cost of schemas, separation proposal and execution, voluminous results, writing preconditions.
- [MCP — Model Context Protocol](30-agents/33-mcp.md) : M×N problem, host, client and server, tools, resources and prompts, stdio and HTTP transport, 2026-07-28 stateless spec, MCP or API REST server, risks, interoperability and historical compatibility tests, protocol and business errors, server identity.
- [Harness & plugins](30-agents/34-harness-plugins.md) : Harness role, plugins, skills, hooks, permissions, sandbox, memory files, negative policy tests, working directory, ability tests.
- [Context engineering](30-agents/35-context-engineering.md) : context as budget, context rot, compaction, sub-agents, prompt caching, context loaded as needed (just-in-time), compaction invariants, context selection, reserve budget.
- [Orchestration multi-agents](30-agents/36-agent-orchestration.md) : orchestrator-workers, supervisor, handoffs, evaluator-optimizer, shared state, multi-agent cost, A2A protocol, parallel critical path calculation, branch cancellation, delegation contract.
- [Frameworks d'agents](30-agents/37-agent-frameworks.md) : LangChain, LangGraph, CrewAI, Google ADK, OpenAI Agents SDK, Claude Agent SDK, LlamaIndex, framework or house code, comparative prototype with failures, state portability, business border.
- [Agent Platforms](30-agents/38-agent-platforms.md) : Different from a framework, bricks, levels of abstraction (API, runtime, Harness managed, cloud offerings and model providers, open source, runtime and double texting, sandbox and sandbox services, gateway of tools, register, identity, Delegated or autonomous agent, memory, Observability, evals, ProtocolsMCP, A2A), Build or buy. The rest, Senior level, is the topic 115 of the Section 110, work quotas and equity between supporters, control plan unavailable, Isolation of quotas.
- [Agent Memory](30-agents/39-agent-memory.md) : Working memory, semantics, episodic and procedural, thread or long-term, writing during or after the conversation, consolidation, recall score, reflection, changing facts, storage, Letta, tools, risks, evaluation, agent memory or RAG, when not to give long-term memory, distinction between inferred facts and preferences, correction and logical deletion, provenance of memories.

### 40 — Automation & agent frameworks

Build workflows and agents with LangChain, LangGraph and CrewAI: fundamentals, tool contracts, takeover, competition, budgets and integration in production.

- [Automation code & no-code](40-automation/41-code-nocode-automation.md) : n8n, triggers, Zapier and Make, Airflow, Prefect and Temporal, durable execution, no-code limits, duplicates and webhooks mess, time zones, queue failure.
- [LangChain — Fundamentals](40-automation/42-langchain-fundamentals.md) : v1, `init_chat_model` packets, messages, `@tool` and `bind_tools` tools, structured outputs, Runnables and LCEL, RAG bricks, LangSmith, structured message retention, argument streaming, call concurrency.
- [LangChain — Agents & middleware](40-automation/43-langchain-agents.md) : `create_agent`, memory by checkpointer and `thread_id`, `response_format`, middleware hooks, middleware provided (human-in-the-loop, summary, fallback, limits), runtime context, Deep Agents, multiple entries between layers, restore budgets, filter results.
- [LangGraph — Fundamentals](40-automation/44-langgraph-fundamentals.md) : `StateGraph`, state and reducers, `MessagesState`, nodes and conditional edges, ReAct loop in graph, super-steps, `Send` (map-reduce), `Command`, Functional API, explicit order of parallel aggregations, reducers and duplicates, minimal state.
- [LangGraph — Production (persistance, HITL, multi-agents)](40-automation/45-langgraph-production.md) : checkpointers, threads, `interrupt` and `Command(resume=...)`, time travel, Store long-term, durable execution, streaming, subgraphs, multi-agent patterns, deployment, valid take-back approvals, concurrent approval, take-back and secrets.
- [CrewAI — Crews](40-automation/46-crewai-crews.md) : agents (role, goal, backstory), tasks, sequential or hierarchical process, delegation, structured outputs, task guards, LLM and tools, unified memory, project structure, independence of validations between agents, task criteria, context contamination.
- [CrewAI — Flows](40-automation/47-crewai-flows.md) : `@start`, `@listen`, `@router`, structured state, `@persist`, `@human_feedback`, memory, CLI, crew or flow, Flows or LangGraph, confidentiality of persistent states, state of branches, authorized transitions.
- [Agentic Workflow Patterns](40-automation/48-agentic-workflow-patterns.md) : Prompt chaining, routing, parallelization (sectioning, voting), valuator-optimizer, plan-and-execute or ReAct, Reflexion, chain reliability calculation, workflow or agent, implementation without framework, retention of the best eligible candidate, correlated voting, stop improvements.
- [Code Agents: Usage & Integration](40-automation/49-coding-agents.md) : ACI (SWE-agent), test-driven loop, `CLAUDE.md` and `AGENTS.md`, plan mode, worktrees and subagents, context management, headless mode, SWE-bench and its limits, tasks to delegate, provision measurement, patch independent testing, change location, patch proof.
- [LangChain — Contracts, tools & middleware in production](40-automation/40-010-langchain-tools-middleware-production.md) : business contracts, ToolRuntime, ToolMessage, structured outputs, errors, async, middleware, budgets, isolation, testing and upgrades, denial of authorization and fallback, propagated delays, error typing.
- [LangGraph — Recovery, Concurrency & Evolution](40-automation/40-011-langgraph-recovery-concurrency.md) : durability sync/async/exit, pending writes, external effects, interruptions, thread concurrency, reducers, subgraphs, migrations and recovery diagnostics, determinism of decisions during replay, leases and fending, retention of checkpoints.
- [CrewAI — Reliable Execution & Integration](40-automation/40-012-crewai-reliable-execution.md) : Task contracts, dependencies, bounded guardrails, budgets, async, persistence and checkpointing, delegation, isolation, instrumentation and testing, external effects after rejection of a guardrail, publication of results, isolation of files.

### 50 — Fine-tuning

- [Fine-tuning & adaptation of models](50-fine-tuning/51-fine-tuning-adaptation.md) : when to adapt, SFT, PEFT, LoRA and QLoRA, resources, distillation, multi-LoRA, regressions, rank and damping calculation, versions of an adaptor, teacher forcing and free generation, supervision masking, fusion LoRA.
- [Post-training & alignment](50-fine-tuning/52-post-training-alignment.md) : RLHF steps, KL penalty, reward hacking, DPO and variants, GRPO, RLVR, RLAIF and Constitutional AI, sets of preferences, alignment fee, reward model or checker, when to do DPO or RL yourself, bias preference pairs, DPO signal, reward and length.
- [Synthetic data & distillation](50-fine-tuning/53-synthetic-data-distillation.md) : varied generation, filtering, model collapse, distillation on outputs or on logs, distillation of reasoning, legal constraints, distillation project, synthetic eval games, deduplication after generation, coverage of modes, filtering efficiency.
- [Distributed Training](50-fine-tuning/54-distributed-training.md) : fine-tuning 7B memory calculation with Adam, data or model parallelism, DDP, ZeRO and FSDP, tensor and pipeline parallelism, 3D parallelism, gradient checkpointing, gradient accumulation, mixed precision BF16, network, outages and checkpoints, parallel efficiency calculation, stragglers and microbatches.
- [Agentic RL & Training Environments](50-fine-tuning/55-agentic-rl.md) : RL on multi-turn trajectories, RLVR or agentic RL, training environments, result or process reward, agent reward hacking, SFT on trajectories, GRPO, task curriculum, tools (verl, OpenRLHF, TRL), when a product team needs to get started, isolation of RL episodes, terminal reward, policy lag.
- [Drive Optimization & Diagnostics](50-fine-tuning/56-training-optimization-diagnostics.md) : loss and business metric, backpropagation, learning rate, AdamW, learning curves, diagnostic micro-lot, normalized accumulation, clipping, mixed precision, PyTorch modes and label masking, train loss comparability and validation, supervised tokens, order of transformations.

### 60 — LLM inference

Understand the mechanisms of the serving, measure quality and SLO, test capacity under load and optimize payload, memory and cost.

- [KV cache & attention](60-llm-inference/61-kv-cache-attention.md) : cache role and size, KV cache, prefix caching and prompt caching, concurrency calculation on an H100, PagedAttention and continuous batching, KV cache in FP8, cost of long contexts, physical blocks and shared prefixes, fragmentation by blocks, residence time.
- [Inference optimizations](60-llm-inference/62-inference-optimizations.md) : prefill and decode, continuous batching, quantization (AWQ, GPTQ, FP8), FlashAttention, parallelism tensor and pipeline, chunked prefill, disaggregation prefill/decode, equity of chunked prefill, FlashAttention and complexity, useful batch.
- [Guided generation (structured outputs)](60-llm-inference/63-guided-generation.md) : masking of logs, JSON Schema, regex and grammars, XGrammar and Outlines, structured outputs of API, JSON mode or structured outputs, business validation, explicit representation of missing information, refusal and schema, cross-constraints.
- [Inference Metrics & SLO](60-llm-inference/64-inference-metrics-slo.md) : TTFT, TPOT and ITL, useful content and reasoning, offered/admitted/useful bitrates, SLO spouses, timeouts, burn rate, Little's law, autoscaling and benchmarks, calculation of duration up to the last token, percentile aggregation, latency budget.
- [Probability & sampling](60-llm-inference/65-probabilities-sampling.md) : logits, temperature, greedy, top-k, top-p and min-p, conditional probabilities, logprobs, perplexity, renormalization exercises, sampling and confidence limits, class scores at several tokens, entropy, order of filters.
- [Prefix caching & RadixAttention](60-llm-inference/66-prefix-caching-radix-attention.md) : vLLM prefix caching, SGLang radix tree, eviction, scheduling and cache-aware routing, offloading of the KV cache (LMCache), limits, time auxiliary channel, query metrics and token, real TTFT gain, affinity and overload, cache_salt isolation, step-by-step compressed tree, references and branch separation, sharing computation.
- [Speculative decoding](60-llm-inference/67-speculative-decoding.md) : draft and one-pass verification, read damping conditions, lossless acceptance rule, gain according to acceptance rate, choice of k, types of drafts (small model, n-grams, EAGLE, Medusa, MTP), tree verification, when it helps or night, vLLM configuration, costs, acceptance metrics, validation of a deployment, calculation of speculation damping, causation.
- [Quantization](60-llm-inference/68-quantization.md) : Calibration and speed, quantization of weights, activations or KV cache, formats (FP8, INT8, INT4, NVFP4, MXFP4), weight-only or W8A8, granularity of scales, outliers of activation (SmoothQuant, rotations), PTQ or QAT, GPTQ, AWQ, GGUF, NF4.
- [Roofline, prefill/decode & disaggregation](60-llm-inference/69-roofline-prefill-decode.md) : arithmetic intensity, model roofline, memory-bound or compute-bound, flow rate calculations of decode and duration of prefill, Batch decode, Limits of Use GPU, Interference prefill/decode, Chunked prefill or disaggregation, Disaggregated deployment (Dynamo, llm-d), When it disintegrates, cost and recovery of transfers KV, memory hierarchy and limits of the roofline, the tipping point, ceiling and measure.
- [Charging benchmarks for inference LLM](60-llm-inference/60-010-inference-load-benchmarks.md) : Reproducible protocol, open or closed loop, coordinated omission, query mix, cold/hot cache, saturation, uncertainty, generator limits, SLO capability, burst testing, survivor bias, plateau duration.
- [Inference Capacity & Scheduling LLM](60-llm-inference/60-011-inference-capacity-scheduling.md) : Sequence and tokens budgets, actual KV memory, GQA and sharding, preemption, admission, priorities, queues, replication and parallelisms, backup and cancellation capacity, KV reservation for outputs, stability margin, starvation risk.
- [Inference Optimization Approach LLM](60-llm-inference/60-012-inference-optimization-method.md) : objective under constraints, CPU/GPU profiling, CUDA graphs and compilation, kernels, Amdahl law, interactions between optimizations, API quotas, retrievals, routing, reasoning and multimodal, marginal cost of an optimization, causal attribution of the gain, rollback cost.
- [Prefill & decode — Step by Step Execution](60-llm-inference/60-013-prefill-decode-step-by-step.md) : Known positions and causal mask, Q/K/V projections, first token, cache timeline, attention cost, partial prefill, temporary memory, batching, chunked prefill, KV transfer and latency diagnosis, logs of the next token, padding masking.

### 70 — Containers & infrastructure

- [Containers & infra — Index](70-containers-infra/00-index.md) : Summary of 13 section cards, chains to remember, and maps on container interest to serve models, start test on the actual target, deployment responsibilities, configuration control.
- [OCI](70-containers-infra/01-oci.md) : Open Container Initiative role, image specifications, runtime and distribution, cross-platform OCI index, integrity and authenticity, manifests and layers.
- [Docker, images and registers](70-containers-infra/02-docker-images-registries.md) : Docker role and difference with OCI, image or container (instance, state, volumes), Docker/OCI compatibility, records and push/pull workflow, secrets in image layers, build cache, reproducible dependencies.
- [containerd & runc](70-containers-infra/03-containerd-runc.md) : role of containerd, runc role, relationship between the two, containerd or CRI-O, crun, RuntimeClass, tools `ctr`, `nerdctl` and `crictl`, place of the GPU in the chain, distinction between shim failure and application failure, logs by layer, snapshots disk.
- [Kubernetes, kubelet & CRI](70-containers-infra/04-kubernetes-kubelet-cri.md) : Pod, Deployment, Service, control plane, kubelet, CRI (containerd, CRI-O), schedule, requests and limits, probes, startup, readiness and liveness, graceful shutdown, eviction and OOM.
- [Docker & Kubernetes](70-containers-infra/05-docker-kubernetes.md) : Dockershim and its removal, current architecture, Docker images executed without Docker Engine, scream-dockerd, checks before removing Docker Engine, build of images without daemon (BuildKit rootless, Buildah), validation of Kubernetes execution conditions, UID and permissions, derives configurations.
- [Apptainer & Singularity](70-containers-infra/06-apptainer-singularity.md) : Singularity → Apptainer, SIF format and Docker image conversion, `--nv`, bind mount permissions, host environment, immutable image.
- [Containers — Synthesis](70-containers-infra/07-containers-overview.md) : Transverse review cards (OCI, CRI and SIF, Kubernetes channels and image, GPU access, inference servers, weight storage), location of a failure in the launch chain, proof of portability, cold start diagnosis.
- [Primitive Linux & Docker fundamentals](70-containers-infra/08-linux-primitives-docker-fundamentals.md) : namespaces and cgroups, container or VM, layers, Dockerfile and cache order, volumes and bind mounts, port mapping, distinction between RAM and VRAM, PID 1 and signals, disk and inodes.
- [GPU in container](70-containers-infra/09-gpu-containers.md) : NVIDIA Container Toolkit, driver and CUDA, CUDA images, GPU Operator, Apptainer `--nv`, ROCm, topology and communications between GPU, visibility and allocation, real CUDA test.
- [Images & weights of](70-containers-infra/10-images-models-weights.md) : calculation of the loading time of the weights of a 70B, weight in the image or separated, cold start, safetensors or pickle, safetensors or GGUF, distributed models as OCI artifacts, atomic publication of a weight cache, integrity of shards, download cache.
- [Inference Servers LLM](70-containers-infra/11-llm-inference-servers.md) : vLLM, API compatible OpenAI, multi-LoRA, SGLang, TensorRT-LLM and Triton, TGI, llama.cpp and Ollama, boundary tests of a compatible API, effective tokenizer, termination tests.
- [Kubernetes GPU & inference](70-containers-infra/12-kubernetes-gpu-inference.md) : device plugin, `nvidia.com/gpu` resource, MIG, time-slicing, KServe, autoscaling (HPA, KEDA), scale-out pressure on storage, rollout capacity, careful scale-down.
- [Apptainer & Inference HPC](70-containers-infra/13-apptainer-inference-hpc.md) : Apptainer or Docker in HPC, security model, Slurm integration, `--nv`, weights mounted from the shared file system, SIF images, definition file, multi-node service (Ray, InfiniBand, NCCL), exposure of a server launched in a job, drainage before walltime, Slurm allocation, local caches.

### 80 — API layer & routing

- [LiteLLM (API layer)](80-api-layer-routing/81-litellm-api-layer.md) : SDK or proxy, virtual keys, budgets, rate limits, fallbacks, load balancing, observability callbacks, alternatives (self-hosted gateways, cloud services, aggregators), reconciliation with provider billing, streaming and fallback, competing budget.
- [Routing LLM](80-api-layer-routing/82-routing-llm.md) : static, rule-based or semantic routing, RouteLLM, cascade, load-based routing, semantic cache, calculation of the average cost of a cascade, router bias, counterfactual decision.
- [Ingress & API gateway](80-api-layer-routing/83-gateway-ingress.md) : Ingress controller, ingress-nginx removal, Ingress, API gateway and gateway LLM, TLS, Gateway API, rate limiting, SSE streaming, controller migration, total timeout and idle timeout, client disconnect, body size.
- [Streaming & application integration](80-api-layer-routing/84-streaming-application-integration.md) : streaming interest, SSE or WebSocket, proxy buffers, server-side cancellation, streaming JSON, agent events (AG-UI), long asynchronous tasks, resuming a stream, idempotency key, calculation of open connections, deduplication to SSE reconnection, backpressure, end of stream.
- [Map of](80-api-layer-routing/85-agentic-protocols-map.md) : protocols by border, MCP, A2A and AG-UI, Agent Card, A2A task cycle, OpenAI compatible API, OpenTelemetry GenAI conventions, `AGENTS.md` and skills, payments by agents (AP2, ACP), governance of standards, when not to expose an agent in A2A, trust borders, job cancellation and business clearing, negotiation of capabilities, contract evolution.

### 90 — Observability & evaluations

Instrument applications, link tracks and metrics, manage prompts and experiences, assess quality and test contracts, breakdowns and reps of agents.

- [Langfuse & observability LLM](90-observability-evals/91-langfuse-observability.md) : perimeter and alternatives (LangSmith, Phoenix, Braintrust), traces, spans and generations, sessions, prompt management, scores, LLM-as-judge, datasets, trace sampling bias, traces and audit, metadata cardinality.
- [ChainForge & Prompt Review](90-observability-evals/92-chainforge-evals-prompts.md) : compare prompts and models, automatic evals, regression tests and tipping cases, evals as a prerequisite for deployment, order of variants and experience biases, variable control, discordant cases.
- [Inference & Usage Monitoring](90-observability-evals/93-monitoring-inference.md) : monitoring or observability, layers to monitor, vLLM and GPU (DCGM), Use by team, finish_reason, validation of each response, quality signals without field truth, errors and availability, OpenTelemetry GenAI traces, Dashboard, Alerts, Controls before production, detection of regression, Logging of the prompts, aggregation of histograms, Buckets SLO, perimeters of measurement, global throughput and segmentation, missing measurements and telemetry failure, Metrics of queue, Actionable Alerts.
- [System evaluation LLM — Methodology](90-observability-evals/94-evals-methodology.md) : benchmark or eval application, error analysis, golden dataset, game size, evaluation families, binary criteria, with or without reference, offline and online, eval-driven development, saturation, anti-patterns, representative cases and adversarial cases, annotation disagreement, test maintenance.
- [LLM-as-a-judge](90-observability-evals/95-llm-as-judge.md) : pointwise and peerwise formats, bias (position, verbosity, self-preference), judge prompt, validation against humans (TPR, TNR, kappa), correction of the measured rate, choice of judge model, specialized judges, limits, when not to use a judge; judge injection, parsing failures, weighted sampling, counter-examples of style for judges, peerwise consistency, reference truth.
- [Evaluation of RAG & agents](90-observability-evals/96-evals-rag-agents.md) : retrieval and generation, precision/recall calculations@k and MRR, nDCG, fidelity or accuracy, oracle context, synthetic games, result or trajectory, eval environments, pass^k and efficiency; citation coverage, support calculation, counterfactual tests, external effects verification, minimal evidence, context pollution.
- [Evals online & A/B testing](90-observability-evals/97-evals-online-ab-testing.md) : Explicit and implicit signals, A/B test, guardrail metrics, shadow testing, canary or A/B, peeking, novelty effect, product metrics, online-offline loop, confidentiality, sample size calculation, intent to process and exposure bias, randomization unit, delayed metrics.
- [Debugging & Failure Analysis of — Flashcards Agents](90-observability-evals/98-agent-debugging.md) : error analysis (open and axial coding), symptom or cause, failure categories, MAST taxonomy, loop detection, replay reproduction, failure in case of non-regression, production signals, when not to blame the model, controlled ablation, first divergence, debugging without effects.
- [Statistics for deciding in IA](90-observability-evals/99-statistics-experimental-decisions.md) : Useful effect and significance, p-value, confidence interval, matched comparison, independent unit, zero failure, multiple tests, power, causality, selection bias and sample mismatch ratio, opportunistic stop and sequential tests, Simpson's paradox, observation dependency.
- [Output & Response Rating LLM](90-observability-evals/90-010-llm-response-evaluation.md) : grid by dimension, accuracy and completeness, relevance and guidance, multiple references, standardization, BLUE and RED, BERTScore, summaries, numerical responses, blocking criteria and aggregation by affirmation, validation of affirmations and style, numerical tolerance, weighted coverage.
- [Langfuse — Instrumentation in production](90-observability-evals/90-011-langfuse-instrumentation-production.md) : Complete application traces, observations, distributed correlation, async, tokens and costs, streaming, sampling, masking, export, duplicates and diagnostics, spread of traces between workers, failed export, distributed clocks.
- [Langfuse — Prompts, datasets & experiences](90-observability-evals/90-012-langfuse-prompts-experiments.md) : labels and versions, prompt cache, fallback, promotion, evaluation games, comparable runs, missing scores, costs per achievement and feedback, confirmation game independence, absent scores, version cache.
- [Agents — Contracts, Faults & Repeats Testing](90-observability-evals/90-013-agent-testing-recovery.md) : pyramid of tests, simulated models, business invariants, fault windows, double orders, concurrency, migrations, traces, evaluations and release qualification, fault injection after business effect, property test, status readout failure.
- [Evaluate agent skills](90-observability-evals/90-014-agent-skill-evaluation.md) : Compliance, triggering and utility, role of description, overly simple requests, trigger set and near-misses, trace detection, three-test noise, training and validation, paired executions, reference without skill or older version, assertions and evidence, cost-per-success, SkillsBench (cured, self-generated skills, size, normalized gain), solution leak, skill invoked or useful.
- [Agent Skills: format & validation with skills-ref](90-observability-evals/90-015-agent-skills-format-skills-ref.md) : Open specification Agent Skills, non-imposed location, mandatory and optional fields, name and description rules, progressive disclosure budget, skills-ref (validate, read-properties, to-prompt), structure and field controls, validator blind spots, unknown fields, Unicode names, catalog and cost in tokens, allowed-tools, CI integration.
- [Harbor: Evaluate Container Agents](90-observability-evals/90-016-harbor-agent-evaluation.md) : Harbor role, task components, checker and reward files, trial or job, oracle and nop agents, shared or separate checker, run command and its options, job or task skills, skill provenance, comparison with and without skill, reward aggregation, mis-trials, calculation of invalid rewards, pass@k, reward hacking, lint, check-and-anal.

### 100 — Security & guardrails

From the security of the LLM to that of the agents: the real threats and incidents, the defensive architecture, the supply chain of tools and skills, the DevSecOps, and the case of code agents.

- [Security LLM & guardrails](100-security-guardrails/101-llm-security-guardrails.md) : OWASP Top 10 LLM 2026, exposure of the hidden context and change of identifiers, direct or indirect injection, “lethal trifecta”, exfiltration, excessive agency, guardrails (Llama Guard, NeMo Guardrails), red teaming, false positive injection detectors, fail-open, cost of false positives.
- [Security of agents — Threats & incidents](100-security-guardrails/102-agent-threats.md) : new threat model, unreliable entries, agent hijacking, detection defense limits, incidents (MCP GitHub, EchoLeak, Supabase, Replit), memory poisoning, invisible injection, multi-agent risks, denial of wallet, code execution, attackers equipped with agents, injection into a valid tool result, secondary channels, privilege amplification.
- [Security of agents — Defensive architecture](100-security-guardrails/103-agent-defenses.md) : Assume Compromise, Agents Rule of Two, Six Design Patterns, Dual LLM and CaMeL, Lower Privilege, Outbound Network, Secrets, Tool Call Validation, Trusted Human Approval, Content Guardrail or Authorization Policy, Memory, Agent Exchanges, Defense in Depth, Argument-Related Approval, Destination Validation, Flight Revocation.
- [MCP Security, Tools & Skills](100-security-guardrails/104-mcp-skills-security.md) : attack surface, tool poisoning, rug pull and tool shadowing (and their differences), postmark-mcp, ClawHub, ToxicSkills, spec permission rules, minimal scopes, SSRF and URL traps, local servers, pre-authorization evaluation, gateway MCP, SSRF upon discovery, dependency lock, update scope.
- [DevSecOps for Agentic AI](100-security-guardrails/105-agentic-ai-devsecops.md) : proof modeling (MAESTRO, ATLAS), repositories (OWASP, NIST, ISO 42001), AI-BOM, SBOM or AI-BOM, supply chain models, CI controls, adversarial tests (promptfoo, garak, PyRIT), red teaming, security eval gate, prompts as code, environments, logging, detection, response to incident
- [Security of code agents](100-security-guardrails/106-coding-agent-security.md) : choice target, permissionless modes, job isolation, s1ngularity, Amazon Q, trapped instruction files, PromptPwnd, agents in CI/CD, slopsquatting and typing, generated code quality, agent PR review, secrets, corporate policy, test code accessible secrets, test commands, proven dependencies.

### 110 — MLOps & CI/CD

Industrialize the life cycle of LLM models and applications: data, drive, artifacts, registry, releases, prediction contracts, CI/CD, monitoring, governance and disaster recovery.

- [MLOps & LLMOps — Fundamentals](110-mlops-cicd/111-mlops-llmops-fundamentals.md) : DevOps or MLOps, specificities of the LLMOps, what to version (code and config, models and data), model registry, lineage, reproducibility, dev/staging/prod environments, role of the Lead, consistent release manifest, CI/CD/CT, recipe and run, technical, statistical and business validity, data dependency debt, model owner, label debt.
- [CI/CD Models](110-mlops-cicd/112-model-cicd.md) : evals statistics and deterministic tests, eval gates (threshold example), deployed artifact, blue/green and canary, shadow deployment, rollback, GitOps, tests of a LLM app, CI prompts, complete pipeline, rollback after schema migration, continuous delivery or deployment, smoke training, same promoted artifact, canary with late label.
- [Monitoring, drift & feedback loop](110-mlops-cicd/113-monitoring-drift-feedback.md) : data drift and concept drift, PSI and calculation, KS test on large volumes, multivariate drift, score distribution, drift of a LLM app and a RAG, quality in production, feedback loop, when to re-train, regular annotation, updates of the API models, trend and segment alerts, through the late labels, fixed and sliding version references, definition.
- [Reproducibility & variance](110-mlops-cicd/114-reproducibility-variance.md) : non-temperature determinism 0, invariance to batch, seed, A rejoicing call, tests on variable outputs, standard error and confidence intervals, Matching comparison, Pass@K and Pass^k, variance of LLM-as-judge, fine-tuning reproducible, stability per repeated task, selection of seeds, checkpoint or inference artifact, change of dependence isolated, audit without replay possible, order of data, variance between runs.
- [— Agent Platforms Architecture & Governance](110-mlops-cicd/115-agent-platforms-governance.md) : internal platform (paved road), control plan and implementation plan, reference architecture, separation of the brain, hands and session, sustainable execution, multi-tenant insulation, exchange of tokens for the delegated agent, throws out of context, standards of identity, engine of policies, human-in-the-loop, register and life cycle, Top 10 OWASP agentic, impact radius and kill switch, Audit, SLO, continuous evals, costs, AI Act, lock-in, criteria of choice, revocation of an active delegation, political versions, verified withdrawal, business and operational responsibilities, Temporary derogations, Revocation of cache, exceptional access.
- [SRE: incidents & capacity of IA services](110-mlops-cicd/116-ai-sre-incidents-capacity.md) : SLI user, error budgets, burn rate, multi-window alerts, bounded queues, admission, backup capability, time propagation, incident management, rollback, RTO and RPO, postmortem and recovery, RTO and RPO compliance calculation, boot-up dependency, drive-service isolation, backlog resorption calculation, ML impact after restoration, recovery load, recovery exercises.
- [— Training Pipelines, Register & Continuous Training](110-mlops-cicd/117-continuous-training-pipelines.md) : MLOps maturity levels, deployed pipeline rather than model, planned or triggered retraining, data and model validation, MLflow experience tracking, signature, champion and challenger alias, registry or vendor alias, milestone cache, training window, scoring batch or online, model censored labels, expected performance calculation without labels, concurrent model promotions, trigger grouping, benchmarking, benchmarking and benchmarking.
- [Artefacts, registry & releases ML](110-mlops-cicd/118-ml-artifacts-registry-releases.md) : run, logged model and registered version, full inference package, MLflow 3 URI, alias resolution, integrity and provenance, secure serialization, clean environment loading, output contract, predict_proba, approval, registry backup, retention, conversion, release thresholds and rollback, immutable resolution, network dependency on loading.
- [Prediction contracts, features & scoring batch](110-mlops-cicd/119-prediction-contracts-features-batch.md) : grain and contract of a prediction, semantic validation, drive-service parity, uptime, TTL and freshness, missing values, named schemas, feature migrations, deadlines, batch independence, idempotency, full publication, temporal validity of scores, feature removal, label reconciliation, latency budget and batch capability, column order, decision and score.

### 120 — Costs & FinOps

- [Inference costs](120-costs-finops/121-inference-costs.md) : cost structure of a call, calculation of the cost of an agent of 20 turns with and without cache, price input and output, prompt caching, cost of self-hosting, break-even API or self-host, batch API, technical levers, long context, unit economics, GPU idle, cost per compliant point-and-energy cache, cost per compliant point-and-energy.
- [FinOps LLM](120-costs-finops/122-finops-llm.md) : four times of the FinOps, visibility of costs, allocation to teams, budgets and safeguards, routing as the first lever, caches, practices GPU, cost-quality-latency arbitration, role of the Lead, budget reservation of in-flight calls, shared costs, stable economic unit.
- [Caching agressif](120-costs-finops/123-aggressive-caching.md) : prompt caching (TTL, write and read prices), stable prompt structure, which breaks the cache, append-only context, parallel requests and pre-heating, response caches, embeddings and tool caches, prompt caching, exact or semantic cache, invalidation, security, steering, false semantic cache equivalents, stampede, verified freshness.

### 130 — LLM fundamentals

What you need to understand about the model itself in order to reason about quality, cost and the serving.

- [Architecture Transformer](130-llm-fundamentals/131-transformer-architecture.md) : attention and weighted sum, causal mask, teacher forcing, multi-head, GQA/MQA and memory KV, MLP, residuals, normalization, RoPE, costs, weight of a 70B, basic model or assistant, explanatory limits of attention weights, softmax normalization, causal context.
- [Tokenisation](130-llm-fundamentals/132-tokenization.md) : token or word, BPE, byte-level, vocabulary size, extra cost of French, character limits, special tokens, chat templates, tokens borders, counting, security, structured truncation and budget of tokens, Unicode and standardization, special tokens.
- [Embeddings & representations](130-llm-fundamentals/133-embeddings-representations.md) : Contrastive learning, similarities, bi-encoder or cross-encoder, ColBERT, Matryoshka, prefixes, choice (MTEB), fine-tuning of embeddings, model change, SPLADE, limits, calculation of the link between cosine and distance L2, standard vectors, difficult negatives.
- [Vector Search & Index ANN](130-llm-fundamentals/134-vector-search-ann.md) : brute force or ANN, index recall or retrieval recall, calculation of the memory of an HNSW index, HNSW and its parameters, IVF, Product Quantization, scalar and binary quantization, DiskANN, filtering, index recall, pgvector or dedicated base, exploitation, sizing, processing of ex æquo in an ANN benchmark, recall under filtering.
- [Pre-workout & scaling laws](130-llm-fundamentals/135-pretraining-scaling-laws.md) : manufacturing steps, pre-workout or post-workout, data, scaling laws, Chinchilla, over-workout for inference, 6ND, MFU, contamination, knowledge cutoff, emerging capabilities, data wall, scaling laws extrapolation limits, lifecycle cost, tokens quality.
- [Mixture of Experts (MoE)](130-llm-fundamentals/136-mixture-of-experts.md) : total and active parameters, router, load balancing, shared expert, real specialization, memory cost, expert parallelism, MoE or dense, calculation of separate experts active in a batch, all-to-all communication, router imbalance.
- [Long context](130-llm-fundamentals/137-long-context.md) : RoPE extension, lost in the middle, needle in a haystack and RULER, context rot, long context or RAG, cost, serving techniques, output limit, task test, proof reconciliation assessment, evidence position, useful length.
- [Reasoning Models & Test-Time Compute](130-llm-fundamentals/138-reasoning-models.md) : Reasoning model or chain-of-thought per prompt, test-time compute, RLVR, budget reflection, billing, when not to use them, prompting, chain of thought fidelity, interleaved thinking, best-of-n, budget reasoning performance, budget and auditor, intermediate result.

### 140 — System design & product

The part that assembles everything else: design, reliability and control an application LLM, senior level.

- [LLM application system design](140-system-design-product/141-system-design-llm.md) : approach, framing, complexity scale, quality-latency-cost triangle, load estimation, components, real or perceived latency, synchronous or asynchronous, multi-tenant, failure modes, arbitration presentation, cost of business errors, amplification of calls, degraded mode.
- [Reliability & resilience of LLM — Flashcards applications](140-system-design-product/142-llm-reliability-resilience.md) : timeouts, recoveries, fallbacks, circuit breaker, retry, fallback or circuit breaker, recoveries multiplied between layers, poorly formed outputs, graceful degradation, spleen limits, long tasks, version pinning, SLO, chaos testing, classification of errors of a circuit breaker, jitter, recovery after 429.
- [Hallucinations, grounding & abstention](140-system-design-product/143-hallucinations-grounding.md) : types of hallucinations, levers, verified citations, abstention, arbitrage with coverage, detection, reporting of uncertainty; temperature and news, source conflicts, partial responses, actual citation and applicable evidence, granularity of citations, facts and recommendations.
- [AI UX & human-in-the-loop](140-system-design-product/144-ai-ux-human-in-the-loop.md) : copilot or autopilot, effective human validation, streaming, agent visibility, feedback, expectations, chat or dedicated interface, automation bias, errors and refusal, local correction of results, review capacity, before-after comparison.
- [LLM system design cases](140-system-design-product/145-system-design-cases.md) : customer support, document research, code assistant, natural language data analysis, large-scale extraction, acting agent, consumer chatbot, voice assistant, response frame, maintenance errors, human review capacity calculation, storage estimation, hypothesis validation.
- [Choose model](140-system-design-product/146-model-selection.md) : criteria and constraints, benchmarks, hosting and weight opening, OSI definition, cost-per-success, comparable protocol, Pareto front, migration and lock-in, Pareto border, expected error cost, eligibility.
- [Technical Leadership in AI Engineering](140-system-design-product/147-ai-technical-leadership.md) : what makes a senior, choice of use cases, ROI, POC failure, RFC and ADR, build or buy, go/no-go, team standards, mentoring, design review, technical debt, communication and monitoring, conditions for reviewing an architectural decision, stopping a POC, transfer criteria.
- [Large Scale Batch Pipelines](140-system-design-product/148-llm-batch-pipelines.md) : batch or online, batch API (JSONL, `custom_id`, 24 h), batch API or continuous batching, replicable architecture, quota cost and duration calculations, error classification, statistical quality control, versions saved with each result, offline self-hosting, when not using batch API, independent identifiers of the order of the results, relaunch.
- [Delivery, idempotency & competition](140-system-design-product/149-delivery-idempotency-concurrency.md) : guarantees of delivery, limits of exactly once, ambiguous timeout, identity of operations, atomic deduplication, retention, ack, order by entity, optimistic concurrency, isolation and splitting tokens, atomicity of deduplication and effect, key and parameters, duration of deduplication.
- [Transactions, outbox & sagas for agents](140-system-design-product/140-010-transactions-outbox-sagas.md) : business invariants, double write, outbox and inbox, transactional perimeter, sagas and compensation, isolation of workflows, unknown states, checkpoints, human validation and fault tests, age of events blocked in the outbox, reservation and compensation, publication order.
- [Applications — Architecture & Life Cycle](140-system-design-product/140-011-agentic-application-architecture.md) : choice of bricks, execution contracts, API and workers, admission, identity, versioned approvals, cancellation, events, deployment and capacity, retrieval of a submission after network shutdown, task and session, resource cleaning.

### 150 — Data & compliance

Building AI systems data: modeling and SQL, contracts and ingestion, temporality and features, storage, orchestration, streaming, distributed computing, corpus, lineage and compliance.

- [Data: curation & annotation](150-data-compliance/151-data-curation-annotation.md) : quality dimensions, deduplication, annotation guide, inter-annotators agreement, which annotates, active learning, dev and test separation, production data, preparation of a fine-tuning, review of the guide after disagreements, auction, label uncertainty.
- [PII & Data Privacy](150-data-compliance/152-pii-privacy.md) : where data pass, detection, masking, pseudonymization and anonymization, pseudonymization before the call, commitments of providers, logs, memorization, leaks between users, secrets, privacy by design, reidentification by indirect attributes, hash and pseudonym, trace minimization.
- [Data flywheel & data versioning](150-data-compliance/153-data-flywheel-versioning.md) : improvement loop, steps, data versioning, tools (DVC, lakeFS, Iceberg), eval lineup, index versioning, implicit signals, traps, prioritization, production feedback representativeness, feedback and policy, example priority.
- [GDPR applied to LLM](150-data-compliance/154-gdpr-llm.md) : scope, GDPR or AI Act, principles, legal basis for re-use, controller and processor, transfers outside the EU, right to erasure, AIPD, automated decisions, data in the model, concrete measures, separate purposes between service and training, retention by purpose, proof of erasure.
- [AI Act (European AI Regulation)](150-data-compliance/155-ai-act.md) : risk-based approach, prohibited practices, high risk and obligations, supplier or deployer, transparency, general purpose models, calendar, sanctions, action plan, limits of human validation for qualification, change of purpose, proof of role.
- [Responsible AI: bias, fairness & transparency](150-data-compliance/156-responsible-ai.md) : Safety or security, sources of bias, counterfactual tests, equity metrics, model cards and system cards, datasheets, sycophancy, security or utility, effective human supervision, subgroup equity, group intersection, documented arbitration.
- [Contracts, Schematics & Data Quality](150-data-compliance/157-data-contracts-quality.md) : producer-consumer contract, schema and business constraints, freshness and completeness, compatibility, migrations, quarantine, drift or incident, atomic publication and operational lineage, semantic contracts and units, compatibility of values, quarantine and population.
- [Incremental Ingestion, CDC & backfills](150-data-compliance/158-ingestion-cdc-backfills.md) : snapshot or incremental, CDC, snapshot-journal consistency, checkpoints, identities and versions, deletions, historical replay, catch-up capability, quarantine, reconciliation and RAG index, API pagination and consistency of extractions, tombstones and old events replayed, log retention, snapshot border.
- [Temporal data & production features](150-data-compliance/159-temporal-data-features.md) : event time and processing, historical availability, point-in-time joins, bi-temporal corrections, windows and watermarks, delayed labels, drive-serving consistency, feature store and freshness, offline/online paths and secure materialization, date of effect and date of knowledge, leakage by aggregate, delay in availability.
- [Analytic Data Modeling](150-data-compliance/150-010-analytical-data-modeling.md) : grain, OLTP and OLAP, facts and dimensions, keys, standardization, join cardinalities, additive measurements, SCD, business identity and metric definitions, weighted global average calculation, semi-additive measurements, historical dimensions.
- [SQL for IA pipelines and datasets](150-data-compliance/150-011-analytical-sql-transformations.md) : joins and filters, null, aggregations, windows, deterministic deduplication, anti-joins, CTE, time SQL, query plans and transformation controls, deterministic deduplication and equalities, ROWS and RANGE windows, join filter.
- [Columnar storage, partitions & lakehouse](150-data-compliance/150-012-columnar-storage-lakehouse.md) : warehouse, lake and lakehouse, object storage, JSONL/Avro/Parquet/Arrow, row groups, pluming, partitions, small files, table formats, transactions, snapshots and deletions, predictive pushdown and bytes actually read, min-max and sort, compaction and snapshots.
- [Transforming & orchestrating data pipelines](150-data-compliance/150-013-data-pipeline-orchestration.md) : ETL/ELT, data layers, tasks and assets, logical intervals, dependencies, incremental, retrievals, publication, CI, resources and critical path of a DAG, concurrent publication of the same interval, available data, successful task without publication.
- [Streaming & event processing](150-data-compliance/150-014-streaming-event-processing.md) : batch and micro-batch, partitions and order, consumer groups, windows, triggers, watermarks, flow joins, changelog, state, checkpoints, backpressure and recovery, high cardinality state size calculation, watermark and inactive partition, late state.
- [Distributed Computing & Data Pipeline Performance](150-data-compliance/150-015-distributed-computing-data-performance.md) : Local or distributed choice, lazy execution, partitions, shuffle, skew, broadcast, salting, driver memory, UDF, cache, aggregations, Amdahl’s law and processing cost, unbalanced partition and hot key, preventable shuffle, partial aggregation.
- [Observability, lineage & data exploitation](150-data-compliance/150-016-data-observability-lineage.md) : SLO of data, freshness, completeness by segment, reconciliation, test coverage, declared or executed lineage, catalog, impact, incidents and monitoring cost, monitoring of the presence of controls, misleading freshness, impact of incidents.
- [Dataset building & corpus IA](150-data-compliance/150-017-ai-datasets-corpora.md) : manifests, document identity, parsing, deduplication and splits, shards, streaming datasets, shuffles, workers, mixing sources, filtering, packing and resuming training, spreading withdrawals to training caches, splitting by source, packing and leaking.

### 160 — Multimodal & edge

- [Vision-Language Models (VLM)](160-multimodal-edge/161-vision-language-models.md) : Generative or contrastive VLM, visual encoder, cost of images, CLIP, limits, visual injection, OCR, coordinates after transformation, quality per field and complete document, image resolution and preservation of evidence, cropping and coverage, small writing.
- [Parsing documents (PDF, OCR, layout)](160-multimodal-edge/162-document-parsing.md) : Native or scanned PDF, layout analysis, tools (Docling, Unstructured, cloud services, VLM), tables, figures, ColPali, structural chunking, evaluation, exploitation, units and table headers, reading order, global quality calculation.
- [Voice & real-time agents](160-multimodal-edge/163-real-time-voice.md) : cascade or speech-to-speech, latency and critical path, end of turn, barge-in, STT and WER limits, interruptions and business effects, evaluation and risks, audio interruption and business cancellation, provisional transcription, critical words.
- [LLM local, on-prem & edge](160-multimodal-edge/164-local-edge-llm.md) : motivations, capacity or memory bandwidth, llama.cpp and GGUF, local tools, Ollama or vLLM, Apple Silicon, small language models, hybrid local and cloud, fleet of devices, profitability of on-prem, measurement in sustained thermal regime, energy autonomy, offline mode.
- [Computer use & browser agents](160-multimodal-edge/165-computer-use-browser-agents.md) : image or structure (DOM, accessibility tree), grounding visual, benchmarks (OSWorld, WebArena), cost and latency, web content injection, isolation, when not to use it, computer use or RPA, tools, screen reverification before a sensitive click, condition wait, success after click.

### 170 — Classical ML & validation

Select and validate predictive models, calibrate their outputs, recommend, predict and detect anomalies; distinguish model explanation and causal effect of an action.

- [Classic ML: choose and understand the](170-classical-ml/171-ml-model-selection.md) : rules or ML or LLM, target formulation, baselines, regressions, regularization, trees, random forest and boosting, clustering, preprocessing, missing data and cost of ownership, unknown categories in production, business baseline, capacity and data.
- [Classic ML: Validation, Leaks & Metrics](170-classical-ml/172-ml-validation-metrics.md) : Train-validation-test, leaks, cross-validation, groups and times, pipelines, rare classes, ROC and PR, precision calculation according to prevalence, thresholds and uncertainty, balanced-accuracy calculation, macro and micro, pretreatment in folds.
- [Calibration, uncertainty & abstention](170-classical-ml/173-calibration-uncertainty-abstention.md) : discrimination and calibration, Brier score, separate calibrator, temperature scaling, uncertainties, risk-coverage, compliant prediction, cost of decision with review and human errors, limits of an aggregated CDE, calibration after selection, conditional coverage.
- [Recommandation & learning to rank](170-classical-ml/174-recommendation-ranking.md) : Product objective, candidate generation and ranking, collaborative filtering or content, implicit feedback, two-turn models, ranking objectives, negatives, exposure bias, cold start, nDCG and diversity, recall calculation between candidates and ranking, non-exposed negatives, catalog diversity.
- [Time Series Forecast](170-classical-ml/175-time-series-forecasting.md) : horizon and cadence, seasonal baseline, ETS or ARIMA or ML, backtesting with slippery origins, future variables, direct or recursive forecasts, lags, MAPE and MASE, quantiles, intervals and hierarchical coherence, MAPE limits with zero sales, horizon and leakage, interval validation.
- [Detection of anomalies](170-classical-ml/176-anomaly-detection.md) : rarity and business error, outlier or novelty, non-probability scores, contextual baseline, Isolation Forest, LOF, self-encoders, review capacity, prevalence, assessment by incident, missing and drifting labels, limits of a fixed quota of alerts, duration of incidents, contextual threshold.
- [Explainability & diagnostics of](170-classical-ml/177-model-explainability.md) : Local or global explanation, significance by permutation, correlated variables, SHAP contributions, reference population, log-odds, PDP and ICE, actionable counterfactuals, generated justifications and explanation fidelity, stability of explanations, importance and causality, explanation of transformations.
- [Causal Inference & Product Decisions](170-classical-ml/178-causal-inference-decisions.md) : prediction or intervention, ATE and CATE, causal graph, confusion and collision, identification or estimation, hypotheses, positivity, propensity score, differences in differences, uplift and sensitivity analyses, interference between treated units, post-processing adjustment, transport of effects.

<!-- catalog:end -->

---

## Maintenance

Edit and improve existing cards while retaining their identifiers, so revisions preserve the review history.

```bash
make install   # install development dependencies
make check     # topics, catalogs, ruff, mypy, tests and workshops
make lint      # topic errors and warnings
make stats     # topic statistics and verification dates to review
make readme    # refresh the “As of …” statistics line
make ids       # assign identifiers to new cards
make catalog   # regenerate both catalogs
make export    # build dist/ai-engineering.apkg
make help      # list all targets
```

Each target calls a script in `scripts/`. Run a script directly for additional options, such as `python3 scripts/lint_flashcards.py --help` or `--stale-months 12`.

- **Errors** block commits and CI: broken links, duplicate filenames, missing line-2 tags, missing or repeated `?` separators, empty questions or answers, disagreement between the plugin parser and Anki export, missing/invalid/duplicate Anki identifiers, active retired IDs, malformed retirement records, missing Scenarios or Connections, a final connection that does not return to the MOC, a topic absent from the MOC, invalid or future verification dates, and dated topics without sources. README and MOC links are checked too, outside code examples.
- **Warnings** flag answers longer than 110 words outside code (140 for scenarios), lists longer than 5 items (6 scenario steps), generic difference questions instead of “Do not confuse”, context-dependent questions, product lists to memorize, duplicate questions, one-way connections, fewer than 2 inbound topic links, topics absent from the README and stale verification dates.

Lint checks structure, links and conventions; it does not establish factual accuracy or teaching quality. During review, check that answers cover the question, explain necessary terms, state numerical assumptions and provide an example or limitation when useful. A short answer can suffice, and a long answer can remain vague. Record review scope and validation in `docs/`.

Pull requests run `make check` on Python 3.10 and 3.12 and build an Anki package as a CI artifact. Pushes to `main`, or manual workflow runs on `main`, publish the package only after these checks pass.

Python in `scripts/`, `tests/` and `examples/` follows ruff, configured in `pyproject.toml`. `scripts/` is type-checked with mypy. File reads and writes explicitly use `encoding="utf-8"`; lint rejects implicit encodings. The [code tooling report](docs/code-tooling-2026-10-31.md) explains these choices and checks.

The [Anki package](#4-review-on-android-with-anki) is rebuilt on each push to `main`. Preserve `MODEL_ID` in `scripts/export_anki.py` and the historical numeric deck mapping in `scripts/deck_ids.json`; changing these identities can disrupt updates to existing imports.

Enable the pre-commit hook once per clone with `git config core.hooksPath .githooks`. It runs `make pre-commit`: topic lint, catalog checks and ruff when installed.

Topics citing products, versions or regulations carry a `Verified on` date. The six-month threshold is a maintenance reminder, not a guarantee of currency. Recheck the cited sources, correct changes, then update the date. For APIs, models, prices and managed services, check changelogs and deprecations before deployment.

Targeted reviews state their dates and checked claims under Sources without artificially refreshing the overall date. Adding a source does not validate every historical claim.

`tests/fixtures/legacy_guids.json` and `tests/fixtures/english_migration_guids.json` protect historical note identities. A deliberate retirement belongs in `scripts/retired_cards.json`, which the identity checks recognize.
