# Vault commands: `make check` reproduces the CI, `make help` lists the targets.
PYTHON ?= python3
# Dependency-free scripts fail on any read or write without explicit encoding.
STRICT_ENCODING = -X warn_default_encoding -W error::EncodingWarning

.DEFAULT_GOAL := help
.PHONY: help install check lint catalog-check ruff typecheck test workshops pre-commit \
	ids catalog stats readme export

help: ## List of targets
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "} {printf "  %-14s %s\n", $$1, $$2}'

install: ## Installs development dependencies
	$(PYTHON) -m pip install -r requirements-dev.txt

check: lint catalog-check ruff typecheck test workshops ## All CI checks

lint: ## Card Conventions: Errors and Warnings
	$(PYTHON) $(STRICT_ENCODING) scripts/lint_flashcards.py --stale-months 0

catalog-check: ## Verify README and MOC catalogs are current
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

catalog: ## Regenerates the README and MOC summaries
	$(PYTHON) scripts/sync_catalog.py

stats: ## Statistics by topic and dates to be rechecked
	$(PYTHON) scripts/lint_flashcards.py --stats

readme: ## Update the README As of statistics line
	$(PYTHON) scripts/lint_flashcards.py --update-readme

export: ## Anki package in dist/ai-engineering.apkg
	$(PYTHON) scripts/export_anki.py
