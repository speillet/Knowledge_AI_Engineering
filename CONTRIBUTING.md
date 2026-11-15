# Contributing

Improve explanations and examples while preserving card identifiers and review history. For the folder layout and numbering rules, see the [repository structure](docs/reference/repository-structure.md).

## Format of a topic

```markdown
# Tool calling — Flashcards
Tags: #flashcards #ai-engineering #agents #tool-calling #llm
<!-- summary: Declaration, execution and validation of tool calls. -->


What is Tool Calling?
?
**Tool calling** allows the model to request an operation by producing a tool name and structured arguments. The application validates the request, executes the allowed function, and returns its result to the model to continue the task.

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
2. **Clarify descriptions**: give each tool a precise name, use case and limits.
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
- **Make success assessable**: specify what to explain, compare, calculate or decide. Do not present conditional rules as universal. Examples and limitations support understanding; they should not become an implicit recital. The [learning guide](docs/guides/learning-with-flashcards.md) explains how to assess each card type.
- **Avoid product lists to memorize**. “Which parsing tools should you know?” is hard to grade and ages quickly. Ask a decision question instead: “Which parsing tool fits high-volume scans, and which fits confidential data?”.
- **One idea per card**: split answers that combine two unrelated mechanisms, product lists or incidents.
- Prefer **numerical reference values and executable examples**—commands, configuration and code—to abstract claims.
- Add **`Verified on: …`** immediately after tags for topics citing products, versions or regulations. Put primary references in `## Sources` before `## Connections`: official documentation, a versioned specification, the author's paper or a regulatory text. Adding a reference alone does not justify changing the verification date.
- Add **`<!-- summary: … -->`** after tags and any verification date, **followed by two blank lines**. It supplies the topic catalog; topic titles supply both catalogs.
- Put a permanent **`<!--anki:…-->` identifier at the end of each question**, for example `What is RAG? <!--anki:…-->`, using the assignment script. It is invisible in the rendered text and excluded from the answer. Keep the identifier when rewording a card; a question with a different meaning gets a new one.
- **Do not begin a card line with an HTML comment**, except `<!--SR:`. The Spaced Repetition plugin also skips the following line. An identifier on its own line caused the answer to disappear; the same behavior explains the two blank lines after the summary. Lint replays the plugin parser in `scripts/sr_plugin.py` and detects differences from Anki export.
- **To retire a card**, remove its block and move its identifier, question and reason to `scripts/retired_cards.json`, for example `{"id": "…", "question": "…", "reason": "duplicate of 95-llm-as-judge"}`. Export includes it suspended with the `retired` tag.
- In an index with introductory text, place `---` and then **`## Cards`** before the first question. The parser excludes the introduction and catalog.

## Add a topic

1. Choose the section and the next free number, then name the file in kebab-case, for example `28-rag-multimodal.md`. To exceed nine topics, use the extended numbering described in [repository structure](docs/reference/repository-structure.md).
2. **The filename must be unique throughout the vault**, because Obsidian resolves `[[...]]` links by filename, not by path.
3. Write the cards in the format above, fill in the `summary` comment and the sources if the file is dated, and then launch `python3 scripts/assign_card_ids.py`.
4. Launch `python3 scripts/sync_catalog.py` to regenerate the MOC and topic catalog. For a new section, first fill in `scripts/sections.json`. The reading paths remain editorial. Update the figures with `python3 scripts/lint_flashcards.py --update-readme`.
5. Add links in both directions: the new file cites its neighbors, and the neighbors quote it in their section `Connections`. Also connect the files that **mention** the notion treated without binding. The lint indicates any link without return.
6. Launch `python3 scripts/lint_flashcards.py`: it indicates dead links, missing topics from the MOC or topic catalog, little connected topics and format deviations (see [Maintenance](#maintenance)).

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

- **Errors** block commits and CI: broken links, duplicate filenames, missing line-2 tags, missing or repeated `?` separators, empty questions or answers, disagreement between the plugin parser and Anki export, missing/invalid/duplicate Anki identifiers, active retired IDs, malformed retirement records, missing Scenarios or Connections, a final connection that does not return to the MOC, a topic absent from the MOC, invalid or future verification dates, and dated topics without sources. Navigation and guide links are checked too, outside code examples.
- **Warnings** flag answers longer than 110 words outside code (140 for scenarios), lists longer than 5 items (6 scenario steps), generic difference questions instead of “Do not confuse”, context-dependent questions, product lists to memorize, duplicate questions, one-way connections, fewer than 2 inbound topic links, topics absent from the catalog and stale verification dates.

Lint checks structure, links and conventions; it does not establish factual accuracy or teaching quality. During review, check that answers cover the question, explain necessary terms, state numerical assumptions and provide an example or limitation when useful. A short answer can suffice, and a long answer can remain vague. Record review scope and validation in `docs/`.

Pull requests run `make check` on Python 3.10 and 3.12 and build an Anki package as a CI artifact. Pushes to `main`, or manual workflow runs on `main`, publish the package only after these checks pass.

Python in `scripts/`, `tests/` and `examples/` follows ruff, configured in `pyproject.toml`. `scripts/` is type-checked with mypy. File reads and writes explicitly use `encoding="utf-8"`; lint rejects implicit encodings. The [code tooling report](docs/reports/code-tooling-2026-10-31.md) explains these choices and checks.

The [Anki package](docs/guides/anki.md) is rebuilt on each push to `main`. Preserve `MODEL_ID` in `scripts/export_anki.py` and the historical numeric deck mapping in `scripts/deck_ids.json`; changing these identities can disrupt updates to existing imports.

Enable the pre-commit hook once per clone with `git config core.hooksPath .githooks`. It runs `make pre-commit`: topic lint, catalog checks and ruff when installed.

Topics citing products, versions or regulations carry a `Verified on` date. The six-month threshold is a maintenance reminder, not a guarantee of currency. Recheck the cited sources, correct changes, then update the date. For APIs, models, prices and managed services, check changelogs and deprecations before deployment.

Targeted reviews state their dates and checked claims under Sources without artificially refreshing the overall date. Adding a source does not validate every historical claim.

`tests/fixtures/legacy_guids.json` and `tests/fixtures/english_migration_guids.json` protect historical note identities. A deliberate retirement belongs in `scripts/retired_cards.json`, which the identity checks recognize.
