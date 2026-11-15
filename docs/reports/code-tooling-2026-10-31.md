# Python code tooling — 31 October 2026

Vault is mostly Markdown. but its reliability is based on code: the lint that protects the review, Anki export which keeps the history of the maps, the generation of summaries and executable workshops. This code was correct and well tested. On the other hand, it lacked the tools of a maintained project: no linter or typing, implicit encodings, a function of lint 145 lines, and two CI workflows that repeated the same steps.

## Perimeter

- `scripts/`: redesign of `lint_flashcards.py`, type annotations on the five modules, factorization of the reading of titles.
- `tests/`: explicit encoding, read and write helpers, two added tests (52 → 54).
- `examples/`: Ruff-only fixes (long lines, `raise … from None`, `zip(strict=True)`), without behavior change.
- Configuration : `pyproject.toml`, `requirements-dev.txt`, `Makefile`, `.editorconfig`, `.gitattributes`, `.github/dependabot.yml`, hook pre-commit.
- CI: `lint-flashcards.yml` and `anki-export.yml` workflows are merged into `flashcards.yml`. `agentic-workshop.yml` is unchanged.

The topics are not modified.

## Changements

### A single definition of verifications

`make check` links the files, the catalog synchronization, ruff, mypy, the tests and the two standard library workshops (SQL and decisions), which the CI did not run until now. The pre-commit hook, the CI and the README call the same targets: a check added to the Makefile applies everywhere.

### Encodage explicite

The 18 Readings and Writings `scripts/` They did not specify an encoding. Under a locale not UTF-8, like Windows by default, The accents on the topics would have been badly read. All of them now specify `encoding="utf-8"`, and rewritten files (README, MOC, topics) keep end of line LF. ruff does not detect this oversight on `Path.read_text`. `make lint` and `make catalog-check` Let the scripts run under `-X warn_default_encoding -W error::EncodingWarning` : a future forgetfulness makes the CI fail.

### Lint cut into controls

`lint()` keeps its signature, but delegates functions named after what they verify:

- `check_links`, `check_layout`, `check_parsing`, `check_sections` ;
- `check_cards`, `check_catalogs`, `check_dates` ;
- `check_retired`, `check_graph`.

Each file is read only once, against three previously for a file. The statistics become a named `FicheStats` instead of a tuple indexed by position. The title of a file is read by a single function, `fiche_title`, shared by the export and the summaries.

Two minor adjustments:

- The links were browsed in the order of a `set` Python, which varies from one process to another. They are now in their order of appearance.
- Two writes of the same link that differ only in spaces (`[[x]]` and `[[x ]]`) no longer count twice in the incoming links or in the connections without return.

### CI

- The `check` job runs on Python 3.10, the minimum version, and 3.12, the version that produces the package.
- The `publish` job only runs after a green `check`. Only it receives `contents: write`.
- Previously, a push on `main` launched two complete workflows, and the release did not depend on the verification workflow.
- Manual triggering from a branch other than `main` no longer releases the release.
- Dependabot offers a group PR for actions and one for Python dependencies every month. `examples/agentic-support` remains excluded: its versions are locked and checked by hand.

## Validations

- **Lint unchanged**: On the actual Vault, the output (with `--stats` and the summary) is the same before and after recast. Since the Vault does not produce any messages, the comparison was repeated on a voluntarily broken copy, which triggers each type of message: 40 errors, 26 warnings, and 81 with `--stale-months 1`.
- **Export unchanged**: The contents of `export_anki.build()` are identical: decks, GUID, fields and tags of 2,257 notes, i.e. 2,186 cards of the vault and 71 cards removed.
- `make check` is green under Python 3.10, and `actionlint` 1.7.12 does not report anything on workflows.
- The agentic workshop, installed since `requirements-lock.txt`, passes its 18 tests and demonstration.

## Outside perimeter

- `ruff format` is not applied: it would rewrite all files for a questionable readability gain on this already homogeneous code.
- GitHub actions remain referenced by major tag rather than SHA. Dependabot keeps them up to date.
- mypy only covers `scripts/`. Tests and workshops remain unannotated.
