# Documentation website

The [website](https://speillet.github.io/Knowledge_AI_Engineering/) offers domain navigation, full-text search and collapsible answers. Markdown files in the repository remain the source for the website, Obsidian and Anki.

## Build or preview

The site uses [Hugo](https://gohugo.io/installation/) **extended** edition, version 0.166.0 to 0.169.0, as required by the pinned release of the [Blowfish](https://blowfish.page/) theme. Then run from the repository root:

```bash
make site          # writes the static site to site/
make site-serve    # preview at http://127.0.0.1:1313/, rendered in memory
```

Both targets first fetch the theme submodule if it is missing (`git submodule update --init --depth 1 website/themes/blowfish`). `make site` stages the content, builds with Hugo, then runs [scripts/check_site.py](../../scripts/check_site.py). It checks every internal link and anchor of the built pages, including absolute links to the site itself, and the URLs of the search index. It fails on any Hugo warning, broken page reference, link or anchor. The preview leaves `site/` untouched. After editing source Markdown, rerun `make site-serve` to regenerate the staged pages. Staging needs only Python 3.10+ and its standard library.

## How pages are built

[scripts/prepare_site.py](../../scripts/prepare_site.py) stages the public pages in `website/content/` without modifying the sources:

- **Topics** keep one section per card kind: key concepts, do-not-confuse, calculations and scenarios. Each answer folds under its question; card counts, the "What this topic covers" list, sources and connections frame the cards. The theme adds the table of contents, breadcrumbs and previous/next topics.
- **Other pages** keep their `##` sections and fold each `###` subsection. Lists made only of links become card grids; numbered lists keep their step numbers.
- **Domain pages** show the prerequisites, the ordered fundamentals and the practice task from `scripts/sections.json`, then every topic of the domain as theme cards. The **topic catalog** folds one block per domain.
- **Links**: wikilinks and relative links become Hugo `relref` references, so a broken link fails the build. Links to scripts and data point to their GitHub source. Card anchors derive from Anki identifiers, so a link to a card survives a rewording. Heading anchors use the same slugs as wikilinks to headings and as the previous site, so old links keep working.

Neither `website/content/` nor `site/` is committed.

## Theme

[Blowfish](https://github.com/nunocoracao/blowfish) is a git submodule in `website/themes/blowfish`, pinned to a release. The site configuration is in `website/config/_default/`. It sets the colour scheme, the appearance (dark by default, light with the footer switch), a fixed header with blur, search, breadcrumbs and tables of contents. The `obsidian` colour scheme is specific to the site, in `website/assets/css/schemes/obsidian.css`: violet-tinted greys, a violet primary in the spirit of Obsidian's accent and a coral accent like the red line of index cards, with shades chosen for WCAG AA text contrast in both appearances. Cards look like index cards: a header line in the colour of their kind, Q and A tabs, and the edge of the deck beneath them. Titles use [Fraunces](https://github.com/undercasetype/Fraunces), served from `website/static/fonts/` with its SIL Open Font License; the file keeps only the Latin letters, the soft style and the two weights the site uses (30 KB).

The site overrides only what the vault needs, in `website/layouts/` and `website/assets/`:

- the home page (`partials/home/custom.html`): a deck of three real flashcards over a faceted obsidian surface (`img/facets.svg`). `scripts/prepare_site.py` takes them from the first core topic of the domains listed in `HOME_DECK`. The top card turns over to show its answer and links to it; it pauses on hover, while off screen or with the button of the hero, and stays still when the reader prefers reduced motion;
- the search index (`_default/index.json`): the full text of each page, where topics give their summary, questions, answers and sources without the labels of the page controls;
- the edit link to the vault source, and the logo: an original crystal over index cards, which nods to Obsidian without using its trademarked logo;
- the tab and home-screen icons (`partials/favicons.html`): the SVG in `assets/icons/` gets a fingerprinted URL and the other icons a version derived from every icon file, so browsers replace a cached icon when one changes. The ICO, PNG and manifest files in `website/static/` replace the Blowfish defaults of the same names. After changing the SVG, `make icons` renders them again; it needs cairosvg and Pillow, which the other scripts do not;
- the 404 page (`404.html`, wording in `i18n/en.yaml`), without the random film quotes of the theme;
- the alias template, which keeps the query of old `search.html?q=` links so that the search opens with their term;
- the styles and script of the collapsible cards (`css/custom.css`, `js/kv.js`). These styles use the colour variables of the scheme, so they follow the palette and the appearance.

To upgrade the theme, check the Hugo versions it supports (`[module.hugoVersion]` in its `config.toml`), then:

```bash
git -C website/themes/blowfish fetch --depth 1 origin tag <tag>
git -C website/themes/blowfish checkout <tag>
git add website/themes/blowfish
```

Update `HUGO_VERSION` and `HUGO_SHA256` in the workflow if the supported range changes. In Obsidian, `.obsidian/app.json` excludes `website/`, so the theme's own Markdown and the pages staged by `make site` stay out of the vault.

## Publication

The Documentation site workflow checks out the theme submodule, installs a pinned Hugo extended release after checking its SHA-256, builds every pull request and uploads a `documentation-site` preview artifact. The artifact is built for the `/Knowledge_AI_Engineering/` path: to browse it, extract it into a folder named `Knowledge_AI_Engineering`, run `python3 -m http.server` from the parent folder and open `http://localhost:8000/Knowledge_AI_Engineering/`. Only `main` deploys to GitHub Pages, which must use **GitHub Actions** as its publishing source in the repository settings.

The Flashcards workflow separately checks the source and exports Anki. Website generation does not change card identifiers or review schedules.

See the official [Hugo documentation](https://gohugo.io/documentation/), the [Blowfish documentation](https://blowfish.page/docs/) and the [GitHub Pages workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

[Reference](README.md) · [Contributing](../../CONTRIBUTING.md)
