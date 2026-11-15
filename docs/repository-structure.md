# Repository structure

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
├── scripts/sync_catalog.py      # generation of topic catalog and MOC
├── scripts/sections.json        # Titles and introductions of the sections
├── tests/                       # tests of parser, lint, summaries and export
├── scripts/requirements.txt     # Anki Export Dependencies
├── requirements-dev.txt # development dependencies: export Anki, ruff, mypy
├── Makefile                     # maintenance commands: make check reproduces the CI
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
- The entry point is **MOC** (Map of Content), [00-moc-ai-engineering.md](../00-moc-ai-engineering.md).
