#!/usr/bin/env python3
"""Génère les sommaires du README et du MOC depuis les fiches et sections.json.

python3 scripts/sync_catalog.py          # met à jour les deux blocs
python3 scripts/sync_catalog.py --check  # échoue si une mise à jour est nécessaire
"""
import argparse
import json
import re

from lint_flashcards import ROOT, MOC

BEGIN = "<!-- catalog:begin -->"
END = "<!-- catalog:end -->"


def fiche_order(path):
    """Compatibilité avec 31-… et extension 30-010-… sans renommer l'existant."""
    section = int(path.parent.name.split("-", 1)[0])
    parts = path.stem.split("-")
    if len(parts) > 2 and int(parts[0]) == section and parts[1].isdigit():
        number = int(parts[1])
    else:
        number = int(parts[0]) if section == 70 else int(parts[0]) - section
    return number, path.name


def render(root, moc=False):
    sections = json.loads((root / "scripts/sections.json").read_text())
    unknown = {p.name for p in root.glob("[0-9]*") if p.is_dir()} - sections.keys()
    if unknown:
        raise ValueError(f"sections absentes de scripts/sections.json : {sorted(unknown)}")
    output = []
    for directory, info in sorted(sections.items(), key=lambda item: int(item[0].split("-")[0])):
        files = sorted((root / directory).glob("*.md"), key=fiche_order)
        if not files:
            raise ValueError(f"section vide ou inexistante : {directory}")
        output += [f"{'##' if moc else '###'} {directory.split('-')[0]} — {info['title']}", ""]
        if not moc and info.get("intro"):
            output += [info["intro"], ""]
        for path in files:
            text = path.read_text()
            title = text.splitlines()[0].removeprefix("# ").removesuffix(" — Flashcards")
            match = re.search(r"^<!-- summary: (.+) -->$", text, re.M)
            if not match:
                raise ValueError(f"{path.name} : commentaire summary manquant")
            if moc:
                output.append(f"- [[{path.stem}|{title}]]")
            else:
                output.append(f"- [{title}]({path.relative_to(root).as_posix()}) : {match[1]}")
        output.append("")
    return "\n".join(output).rstrip()


def replace_block(text, body):
    if text.count(BEGIN) != 1 or text.count(END) != 1 or text.index(BEGIN) > text.index(END):
        raise ValueError("délimiteurs catalog absents, dupliqués ou inversés")
    before, rest = text.split(BEGIN)
    _, after = rest.split(END)
    return before + BEGIN + "\n\n" + body + "\n\n" + END + after


def sync(root=ROOT, check=False):
    updates = []
    for name, moc in (("README.md", False), (f"{MOC}.md", True)):
        path = root / name
        original = path.read_text()
        updated = replace_block(original, render(root, moc=moc))
        if updated != original:
            updates.append((path, updated))
    for path, updated in updates:
        if not check:
            path.write_text(updated)
        print(f"{path.name} : {'à régénérer' if check else 'mis à jour'}")
    return not updates if check else True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        return 0 if sync(check=args.check) else 1
    except (ValueError, OSError) as exc:
        parser.exit(1, f"ERREUR : {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
