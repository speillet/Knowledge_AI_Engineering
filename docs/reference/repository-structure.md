# Repository structure

```text
Knowledge_AI_Engineering/
├── README.md                    # learn, practice and review
├── START_HERE.md                # first learning session
├── CONTRIBUTING.md              # card conventions and maintenance
├── 00-moc-ai-engineering.md      # Obsidian navigation
├── docs/
│   ├── guides/                  # setup and learning method
│   ├── paths/                   # ordered learning routes
│   ├── reference/               # repository conventions
│   ├── reports/                 # dated reviews and audits
│   └── catalog.md               # generated topic summaries
├── 10-prompt-engineering/        # numbered topic domains
├── …
├── 170-classical-ml/
├── examples/                    # runnable workshops
├── scripts/                     # lint, catalogs, IDs and Anki export
├── tests/                       # tooling and compatibility checks
├── .github/workflows/           # checks and Anki publication
└── Makefile                     # maintenance commands
```

- Each **section** is a folder numbered by ten (`20-rag`, `30-agents`...).
- Each section's **`README.md`** lists prerequisites, an ordered foundation sequence and topics for deeper study. These pages are generated with `make catalog` from `scripts/sections.json` and are excluded from flashcard export. The historical container `00-index.md` still contains review cards.
- Each **topic** has a number derived from its section: `21-rag-fundamentals.md` and `22-advanced-rag.md` are in `20-rag/`.
- Exception: the container section keeps its own numbering, from `00-index.md` to `13-apptainer-inference-hpc.md`.
- Numeric prefixes remain stable. **A section may exceed nine topics**: after `39-agent-memory.md`, use `30-010-new-topic.md`, then `30-011-another-topic.md`, in `30-agents/`. The prefix designates the section, the second number its rank. The catalogs sort both numbering conventions together; choose the section according to the subject.
- The entry point is **MOC** (Map of Content), [00-moc-ai-engineering.md](../../00-moc-ai-engineering.md).
