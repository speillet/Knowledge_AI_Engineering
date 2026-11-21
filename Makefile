# Vault commands: `make check` reproduces the CI, `make help` lists the targets.
PYTHON ?= python3
HUGO ?= hugo
# Dependency-free scripts fail on any read or write without explicit encoding.
STRICT_ENCODING = -X warn_default_encoding -W error::EncodingWarning

.DEFAULT_GOAL := help
.PHONY: help install check lint catalog-check ruff typecheck test workshops pre-commit \
	ids catalog stats readme export site site-serve icons diagrams

help: ## List of targets
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "} {printf "  %-14s %s\n", $$1, $$2}'

install: ## Installs development dependencies
	$(PYTHON) -m pip install -r requirements-dev.txt

check: lint catalog-check ruff typecheck test workshops ## All CI checks

lint: ## Card Conventions: Errors and Warnings
	$(PYTHON) $(STRICT_ENCODING) scripts/lint_flashcards.py --stale-months 0

catalog-check: ## Verify the topic catalog, MOC and domain indexes are current
	$(PYTHON) $(STRICT_ENCODING) scripts/sync_catalog.py --check

ruff: ## Style and Probable Python Code Errors
	$(PYTHON) -m ruff check .

typecheck: ## Script Type Annotations
	$(PYTHON) -m mypy

test: ## Parser, lint, catalog, export and RAG workshop tests
	$(PYTHON) -m unittest discover -s tests

workshops: ## Self-checked workshops in standard library
	$(PYTHON) examples/data-engineering/sql_workshop.py > /dev/null
	$(PYTHON) examples/ai-decisions/decisions_workshop.py > /dev/null

pre-commit: ## Quick Checks Launched by .githooks/pre-commit
	$(PYTHON) $(STRICT_ENCODING) scripts/lint_flashcards.py --quiet
	$(PYTHON) $(STRICT_ENCODING) scripts/sync_catalog.py --check
	@if $(PYTHON) -m ruff --version > /dev/null 2>&1; then $(PYTHON) -m ruff check --quiet .; \
	else echo "ruff is missing: run make install to check Python code too"; fi

ids: ## Anki New Card Identifiers
	$(PYTHON) scripts/assign_card_ids.py

catalog: ## Regenerate the topic catalog, MOC and domain indexes
	$(PYTHON) scripts/sync_catalog.py

stats: ## Statistics by topic and dates to be rechecked
	$(PYTHON) scripts/lint_flashcards.py --stats

readme: ## Update the README As of statistics line
	$(PYTHON) scripts/lint_flashcards.py --update-readme

export: ## Anki package in dist/ai-engineering.apkg
	$(PYTHON) scripts/export_anki.py

THEME = website/themes/blowfish/theme.toml

$(THEME):
	git submodule update --init --depth 1 website/themes/blowfish

site: $(THEME) ## Build the site with Hugo extended into site/; fails on any warning or broken link
	$(PYTHON) $(STRICT_ENCODING) scripts/prepare_site.py
	$(HUGO) --source website --minify --cleanDestinationDir --panicOnWarning
	$(PYTHON) $(STRICT_ENCODING) scripts/check_site.py

site-serve: $(THEME) ## Preview the site at http://127.0.0.1:1313/; rerun after changing source files
	$(PYTHON) $(STRICT_ENCODING) scripts/prepare_site.py
	$(HUGO) server --source website --bind 127.0.0.1 --baseURL http://127.0.0.1:1313/ --renderToMemory

icons: ## Render the website icons from their SVG (needs cairosvg and Pillow)
	$(PYTHON) scripts/build_icons.py

diagrams: ## Render flashcard SVGs to PNGs (needs Playwright and Chromium; see Anki guide)
	$(PYTHON) scripts/build_diagrams.py
