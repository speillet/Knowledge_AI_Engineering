# Documentation website

The [website](https://speillet.github.io/Knowledge_AI_Engineering/) provides domain navigation, full-text search and expandable answers. Markdown files in the repository remain the source for the website, Obsidian and Anki.

## Build or preview

Use a Python 3.10+ virtual environment from the repository root:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-docs.txt
make site
make site-serve
```

The preview address is printed in the terminal. Stop it with Ctrl+C. After editing source Markdown, rerun `make site-serve` to regenerate the staged pages.

`make site` writes static HTML to `site/` and fails on documentation build warnings. Serve that directory over HTTP to test navigation and search; opening files directly with `file://` does not support the search requests.

## What is generated

[scripts/prepare_site.py](../../scripts/prepare_site.py) stages the public learning pages in `build/docs/`. It converts Obsidian wikilinks to relative Markdown links, maps each `README.md` to `index.md`, and turns flashcard separators into expandable answers. Fenced and inline code remain unchanged. Links to scripts and data point to their GitHub source.

The staging list includes topics, domain indexes, guides, learning paths, references, review reports and workshop READMEs. Editor settings, local environments and working databases are excluded. Neither `build/` nor `site/` is committed.

Navigation, search, the theme and strict link validation are configured in [mkdocs.yml](../../mkdocs.yml). Dependencies are pinned in [requirements-docs.txt](../../requirements-docs.txt). When adding a domain, add its navigation entry to the configuration after updating `scripts/sections.json`.

## Publication

The Documentation site workflow builds every pull request and uploads a `documentation-site` preview artifact. Only `main` deploys to GitHub Pages, after a successful strict build. GitHub Pages must use **GitHub Actions** as its publishing source in the repository settings.

The Flashcards workflow separately checks the source and exports Anki. Website generation does not change card identifiers or review schedules.

See the official [MkDocs configuration guide](https://www.mkdocs.org/user-guide/configuration/) and [GitHub Pages workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

[Reference](README.md) · [Contributing](../../CONTRIBUTING.md)
