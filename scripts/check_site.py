#!/usr/bin/env python3
"""Check the links of the built site: every internal page, file and anchor must exist.

python3 scripts/check_site.py                  # site/, served at the Hugo baseURL
python3 scripts/check_site.py --site DIR --base http://127.0.0.1:1313/

Hugo already stops on a broken relref. This check also covers anchors, links written in
raw HTML or by the theme, absolute links to the site itself, and the URLs of the search
index. It uses the standard library.
"""

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urljoin, urlsplit

from lint_flashcards import ROOT

CONFIG = ROOT / "website/config/_default/hugo.toml"
EXTERNAL = re.compile(r"^(?:[a-zA-Z][a-zA-Z0-9+.-]*:|//)")
REFERENCES = {"a": "href", "link": "href", "script": "src", "img": "src"}


class Page(HTMLParser):
    """Anchors and outgoing references of one HTML page."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value for key, value in attrs if value is not None}
        if "id" in values:
            self.ids.add(values["id"])
        if tag == "a" and "name" in values:
            self.ids.add(values["name"])
        attribute = REFERENCES.get(tag)
        if attribute and values.get(attribute):
            self.links.append(values[attribute])


def site_url(config: Path = CONFIG) -> str:
    """Hugo baseURL: the address the site is served at."""
    match = re.search(r'^baseURL\s*=\s*"([^"]+)"', config.read_text(encoding="utf-8"), re.M)
    return match[1] if match else "/"


def served_file(site: Path, base: str, path: str) -> Path | None:
    """File that a static host serves for a URL path, or None outside the site or when absent."""
    if (path + "/") == base:
        path = base
    if not path.startswith(base):
        return None
    candidate = site / unquote(path[len(base) :])
    if candidate.is_dir():
        candidate = candidate / "index.html"
    return candidate if candidate.is_file() else None


def parse(path: Path) -> Page:
    page = Page()
    page.feed(path.read_text(encoding="utf-8"))
    return page


def check(site: Path, base: str, origin: str = "") -> tuple[list[str], int]:
    """Broken references of every page, and the number of pages checked.

    base is the URL path the site is served under; links starting with origin + base, such
    as https://host/base/page/, are checked like the internal links they are.
    """
    pages = {path: parse(path) for path in sorted(site.rglob("*.html"))}
    errors: list[str] = []
    for path, page in pages.items():
        url = base + path.relative_to(site).as_posix()
        for link in page.links:
            if origin and link.startswith(origin + base):
                link = link[len(origin) :]
            if EXTERNAL.match(link):
                continue
            parts = urlsplit(urljoin(url, link))
            target = served_file(site, base, parts.path)
            name = path.relative_to(site).as_posix()
            if target is None:
                errors.append(f"{name}: missing target {link}")
                continue
            fragment = unquote(parts.fragment)
            if fragment and target.suffix == ".html":
                ids = pages[target].ids if target in pages else parse(target).ids
                if fragment not in ids:
                    errors.append(f"{name}: missing anchor {link}")
    index = site / "index.json"
    if index.is_file():
        for entry in json.loads(index.read_text(encoding="utf-8")):
            if served_file(site, base, urlsplit(entry.get("permalink", "")).path) is None:
                errors.append(f"index.json: missing page {entry.get('permalink')}")
    return errors, len(pages)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--site", type=Path, default=ROOT / "site", help="built site directory (default: site/)")
    parser.add_argument("--base", help="URL or path the site is served at (default: the Hugo baseURL)")
    args = parser.parse_args()
    url = urlsplit(args.base or site_url())
    base = url.path if url.path.endswith("/") else url.path + "/"
    origin = f"{url.scheme}://{url.netloc}" if url.netloc else ""
    errors, count = check(args.site, base, origin)
    for error in errors[:200]:
        print(error)
    if len(errors) > 200:
        print(f"... and {len(errors) - 200} more")
    print(f"Checked the links of {count} pages: {len(errors)} broken")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
