#!/usr/bin/env python3
"""Stage the vault for MkDocs without modifying the Markdown source files."""

import os
from pathlib import Path
import re
import shutil
import unicodedata
from urllib.parse import quote, unquote

from lint_flashcards import MOC, ROOT, markdown_lines

REPOSITORY = "https://github.com/speillet/Knowledge_AI_Engineering"
WIKI = re.compile(r"\[\[([^\]|#]+)(?:#([^\]|]+))?(?:\|([^\]]+))?\]\]")
MARKDOWN_LINK = re.compile(r"(?<!!)\[([^\]\n]*)\]\(([^)\s]+)\)")
METADATA = re.compile(r"<!--\s*(?:anki:|SR:|summary:).*?-->")


def source_pages(root: Path) -> list[Path]:
    """Select public documentation only, excluding environment and private editor files."""
    return sorted(
        {
            *(root / name for name in ("README.md", "START_HERE.md", "CONTRIBUTING.md", f"{MOC}.md")),
            *root.glob("[0-9]*/*.md"),
            *(root / "docs").rglob("*.md"),
            root / "examples/README.md",
            *root.glob("examples/*/README.md"),
        }
    )


def site_path(path: Path) -> Path:
    """MkDocs uses index.md for directory landing pages."""
    return path.with_name("index.md") if path.name == "README.md" else path


def anchor(text: str) -> str:
    """Match Python-Markdown's default ASCII heading slugs."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[-\s]+", "-", re.sub(r"[^\w\s-]", "", text).strip().lower())


def render(text: str, source: Path, pages: set[Path], wikilinks: dict[str, Path]) -> str:
    """Convert links and review separators outside code; leave source prose intact."""
    destination = site_path(source)
    is_topic = bool(re.match(r"^\d", source.parts[0])) and len(source.parts) == 2 and source.name != "README.md"

    def relative(target: Path) -> str:
        return quote(Path(os.path.relpath(site_path(target), destination.parent)).as_posix(), safe="/#")

    def wiki(match: re.Match[str]) -> str:
        name, heading, label = match.groups()
        target = wikilinks.get(name.strip())
        if target is None:
            raise ValueError(f"{source}: unknown wikilink {name}")
        fragment = "#" + anchor(heading) if heading else ""
        return f"[{label or heading or name}]({relative(target)}{fragment})"

    def markdown_link(match: re.Match[str]) -> str:
        label, url = match.groups()
        if re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", url) or url.startswith(("#", "/")):
            return match[0]
        path, sep, fragment = url.partition("#")
        target = Path(os.path.normpath(source.parent / unquote(path)))
        if target in pages:
            return f"[{label}]({relative(target)}{sep}{fragment})"
        return f"[{label}]({REPOSITORY}/blob/main/{quote(target.as_posix())}{sep}{fragment})"

    output = []
    answer_open = False
    for _, line, code in markdown_lines(text):
        if code:
            output.append(line)
            continue
        if answer_open and (line.strip() == "---" or re.match(r"^## (Sources|Connections)\s*$", line)):
            output += ["", "</details>", ""]
            answer_open = False
        if is_topic and line.strip() == "?":
            output += ["", '<details markdown="1">', "<summary>Show answer</summary>", ""]
            answer_open = True
            continue
        if is_topic and line.startswith("Tags:"):
            continue
        parts = re.split(r"(`+[^`]*`+)", line)
        for i, part in enumerate(parts):
            if not part.startswith("`"):
                part = METADATA.sub("", part)
                parts[i] = WIKI.sub(wiki, MARKDOWN_LINK.sub(markdown_link, part))
        output.append("".join(parts).rstrip())
    if answer_open:
        output += ["", "</details>"]
    output += ["", "---", "", f"[View source on GitHub]({REPOSITORY}/blob/main/{quote(source.as_posix())})", ""]
    return "\n".join(output)


def prepare(root: Path = ROOT) -> Path:
    """Rebuild a disposable staging directory using only selected public pages."""
    sources = source_pages(root)
    pages = {p.relative_to(root) for p in sources}
    wikilinks = {p.stem: p for p in pages if p.name != "README.md"}
    output = root / "build/docs"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    for path in sources:
        relative = path.relative_to(root)
        target = output / site_path(relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render(path.read_text(encoding="utf-8"), relative, pages, wikilinks), encoding="utf-8")
    shutil.copytree(root / "docs/assets", output / "assets", dirs_exist_ok=True)
    print(f"Prepared {len(sources)} pages in {output.relative_to(root)}")
    return output


if __name__ == "__main__":
    prepare()
