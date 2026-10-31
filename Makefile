# Commandes du vault : `make check` reproduit la CI, `make help` liste les cibles.
PYTHON ?= python3
# Les scripts sans dépendance échouent sur toute lecture ou écriture sans encodage explicite.
STRICT_ENCODING = -X warn_default_encoding -W error::EncodingWarning

.DEFAULT_GOAL := help
.PHONY: help install check lint catalog-check ruff typecheck test ateliers pre-commit \
	ids catalog stats readme export

help: ## Liste les cibles
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "} {printf "  %-14s %s\n", $$1, $$2}'

install: ## Installe les dépendances de développement
	$(PYTHON) -m pip install -r requirements-dev.txt

check: lint catalog-check ruff typecheck test ateliers ## Toutes les vérifications de la CI

lint: ## Conventions des fiches : erreurs et avertissements
	$(PYTHON) $(STRICT_ENCODING) scripts/lint_flashcards.py --stale-months 0

catalog-check: ## Sommaires du README et du MOC à jour
	$(PYTHON) $(STRICT_ENCODING) scripts/sync_catalog.py --check

ruff: ## Style et erreurs probables du code Python
	$(PYTHON) -m ruff check .

typecheck: ## Annotations de type de scripts/
	$(PYTHON) -m mypy

test: ## Tests du parseur, du lint, des sommaires, de l'export et de l'atelier RAG
	$(PYTHON) -m unittest discover -s tests

ateliers: ## Ateliers autovérifiés en bibliothèque standard
	$(PYTHON) examples/data-engineering/atelier_sql.py > /dev/null
	$(PYTHON) examples/decisions-ia/atelier_decisions.py > /dev/null

pre-commit: ## Vérifications rapides lancées par .githooks/pre-commit
	$(PYTHON) $(STRICT_ENCODING) scripts/lint_flashcards.py --quiet
	$(PYTHON) $(STRICT_ENCODING) scripts/sync_catalog.py --check
	@if $(PYTHON) -m ruff --version > /dev/null 2>&1; then $(PYTHON) -m ruff check --quiet .; \
	else echo "ruff absent : lancer make install pour vérifier aussi le code Python"; fi

ids: ## Identifiants Anki des nouvelles cartes
	$(PYTHON) scripts/assign_card_ids.py

catalog: ## Régénère les sommaires du README et du MOC
	$(PYTHON) scripts/sync_catalog.py

stats: ## Statistiques par fiche et dates à revérifier
	$(PYTHON) scripts/lint_flashcards.py --stats

readme: ## Met à jour la ligne « État au … » du README
	$(PYTHON) scripts/lint_flashcards.py --update-readme

export: ## Paquet Anki dans dist/ai-engineering.apkg
	$(PYTHON) scripts/export_anki.py
