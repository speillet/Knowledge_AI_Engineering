#!/usr/bin/env python3
"""Generates the README and MOC summaries from the sheets and sections.json.

python3 scripts/sync_catalog.py # updates both blocks
python3 scripts/sync_catalog.py --check # fails if an update is required
"""

import argparse
import json
from pathlib import Path
import re

from lint_flashcards import MOC, ROOT, topic_title

BEGIN = "<!-- catalog:begin -->"
END = "<!-- catalog:end -->"


def topic_order(path: Path) -> tuple[int, str]:
    """Compatibility with 31-... and extension 30-010-... without renaming the existing one."""
    section = int(path.parent.name.split("-", 1)[0])
    parts = path.stem.split("-")
    if len(parts) > 2 and int(parts[0]) == section and parts[1].isdigit():
        number = int(parts[1])
    else:
        number = int(parts[0]) if section == 70 else int(parts[0]) - section
    return number, path.name


def render(root: Path, moc: bool = False) -> str:
    """Summary of sections: wikilinks for the MOC, Markdown links and abstracts for the README."""
    sections = json.loads((root / "scripts/sections.json").read_text(encoding="utf-8"))
    unknown = {p.name for p in root.glob("[0-9]*") if p.is_dir()} - sections.keys()
    if unknown:
        raise ValueError(f"missing sections of scripts/sections.json: {sorted(unknown)}")
    output = []
    for directory, info in sorted(sections.items(), key=lambda item: int(item[0].split("-")[0])):
        files = sorted((root / directory).glob("*.md"), key=topic_order)
        if not files:
            raise ValueError(f"Empty or non-existent section: {directory}")
        output += [f"{'##' if moc else '###'} {directory.split('-')[0]} — {info['title']}", ""]
        if not moc and info.get("intro"):
            output += [info["intro"], ""]
        for path in files:
            text = path.read_text(encoding="utf-8")
            title = topic_title(text)
            match = re.search(r"^<!-- summary: (.+) -->$", text, re.M)
            if not match:
                raise ValueError(f"{path.name} : commentaire summary manquant")
            if moc:
                output.append(f"- [[{path.stem}|{title}]]")
            else:
                output.append(f"- [{title}]({path.relative_to(root).as_posix()}) : {match[1]}")
        output.append("")
    return "\n".join(output).rstrip()


def replace_block(text: str, body: str) -> str:
    """Replaces content between catalog delimiters."""
    if text.count(BEGIN) != 1 or text.count(END) != 1 or text.index(BEGIN) > text.index(END):
        raise ValueError("catalog delimiters absent, duplicated or reversed")
    before, rest = text.split(BEGIN)
    _, after = rest.split(END)
    return before + BEGIN + "\n\n" + body + "\n\n" + END + after


def sync(root: Path = ROOT, check: bool = False) -> bool:
    """Updates the two summaries; with check, returns False if they are to be regenerated, without writing."""
    updates: list[tuple[Path, str]] = []
    for name, moc in (("README.md", False), (f"{MOC}.md", True)):
        path = root / name
        original = path.read_text(encoding="utf-8")
        updated = replace_block(original, render(root, moc=moc))
        if updated != original:
            updates.append((path, updated))
    for path, updated in updates:
        if not check:
            path.write_text(updated, encoding="utf-8", newline="\n")
        print(f"{path.name} : {('needs regeneration' if check else 'updated')}")
    return not updates if check else True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        return 0 if sync(check=args.check) else 1
    except (ValueError, OSError) as exc:
        parser.exit(1, f"ERROR: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
