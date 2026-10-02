#!/usr/bin/env python3
"""Exporte les fiches du vault en paquet Anki (.apkg), pour réviser sur téléphone avec AnkiDroid.

Usage :
    pip install -r scripts/requirements.txt
    python3 scripts/export_anki.py                        # écrit dist/ai-engineering.apkg
    python3 scripts/export_anki.py --output autre.apkg

Chaque note porte un identifiant permanent <!--anki:...--> : un réimport met à jour
les notes existantes même si leur question ou leur fichier change.
Les commentaires <!--SR:...--> du plugin Obsidian sont ignorés.
"""
import argparse
import hashlib
import re
import sys
from pathlib import Path

import genanki
from markdown_it import MarkdownIt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lint_flashcards import MOC, ROOT, fiche_files, lint, parse_cards  # noqa: E402

RACINE = "AI Engineering"
MODEL_ID = 1718293041  # fixe : changer cet identifiant dupliquerait toutes les notes

SR_RE = re.compile(r"<!--SR:.*?-->", re.S)
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|([^\]]+))?\]\]")
SECTION_RE = re.compile(r"^## (\d+) — (.+)$", re.M)

CSS = """
.card {
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  font-size: 18px; line-height: 1.45; text-align: left;
  color: #1d1d1f; background: #ffffff; padding: 0 4px;
}
.question { font-weight: 600; }
strong { color: #0b3d91; }
ul, ol { padding-left: 1.3em; }
li { margin: .2em 0; }
code {
  font-family: ui-monospace, "JetBrains Mono", Menlo, monospace; font-size: .88em;
  background: #f1f2f4; padding: 0 .25em; border-radius: 3px;
}
pre {
  overflow-x: auto; white-space: pre; font-size: .8em; line-height: 1.35;
  background: #f1f2f4; padding: .6em .7em; border-radius: 6px;
}
pre code { background: none; padding: 0; font-size: 1em; }
.lien { color: #1a5fb4; border-bottom: 1px dotted currentColor; }
.source { margin-top: 1.4em; font-size: .72em; color: #6b6b70; }
hr#answer { border: 0; border-top: 1px solid #d0d0d5; margin: 1em 0; }

.nightMode.card, .night_mode.card, .nightMode .card, .night_mode .card { color: #e7e7ea; background: #1e1e20; }
.nightMode strong, .night_mode strong { color: #9cc3ff; }
.nightMode code, .night_mode code, .nightMode pre, .night_mode pre { background: #2c2c30; }
.nightMode pre code, .night_mode pre code { background: none; }
.nightMode .lien, .night_mode .lien { color: #8ab4f8; }
.nightMode .source, .night_mode .source { color: #9a9aa0; }
.nightMode hr#answer, .night_mode hr#answer { border-top-color: #44444a; }
"""

MODEL = genanki.Model(
    MODEL_ID,
    "AI Engineering",
    fields=[{"name": "Question"}, {"name": "Réponse"}, {"name": "Fiche"}, {"name": "Section"}],
    templates=[{
        "name": "Question → Réponse",
        "qfmt": '<div class="question">{{Question}}</div>',
        "afmt": '{{FrontSide}}<hr id="answer">{{Réponse}}'
                '<div class="source">{{Section}} · {{Fiche}}</div>',
    }],
    css=CSS,
)

md = MarkdownIt("commonmark", {"html": False})


def titre(path):
    first = path.read_text().split("\n", 1)[0]
    return first.lstrip("# ").replace(" — Flashcards", "").strip()


def stable_id(text):
    return int(hashlib.sha1(text.encode()).hexdigest()[:8], 16) % (1 << 30) + (1 << 30)


def to_html(markdown, titres):
    html = md.render(SR_RE.sub("", markdown).strip())

    def lien(m):
        cible, alias = m.group(1).strip(), m.group(2)
        return f'<span class="lien">{alias or titres.get(cible, cible)}</span>'

    return WIKILINK_RE.sub(lien, html)


def type_tag(question):
    for prefix, tag in (("Mise en situation :", "situation"),
                        ("À ne pas confondre", "confusion"),
                        ("Calcul :", "calcul")):
        if question.startswith(prefix):
            return f"type::{tag}"
    return "type::question"


def build():
    moc = (ROOT / f"{MOC}.md").read_text()
    sections = {num: nom.strip() for num, nom in SECTION_RE.findall(moc)}
    files = fiche_files()
    titres = {p.stem: titre(p) for p in files + [ROOT / f"{MOC}.md"]}

    decks, guids, total = {}, set(), 0
    for p in files:
        num_section = p.parent.name.split("-", 1)[0]
        section = f"{int(num_section):03d} — {sections[num_section]}"  # 3 chiffres : Anki trie par ordre alphabétique
        fiche = titres[p.stem]
        num_fiche = re.match(r"\d+(?:-\d+)?", p.stem)[0]
        deck_name = f"{RACINE}::{section}::{num_fiche} {fiche}"
        deck = decks.setdefault(deck_name, genanki.Deck(stable_id(deck_name), deck_name))

        text = p.read_text()
        tags = [f"section::{p.parent.name}", f"fiche::{p.stem}"]
        if "\nVérifié le" in text:
            tags.append("verifie")

        cards, malformed = parse_cards(text)
        if malformed or not cards:
            raise ValueError(f"{p.name} : cartes mal formées ou absentes (lignes {malformed})")
        for c in cards:
            guid = c.guid
            if not guid or not c.question or not c.answer:
                raise ValueError(f"{p.name}:{c.line} : identifiant, question ou réponse manquant")
            if guid in guids:
                raise ValueError(f"identifiant en double dans {p.name} : {c.question[:60]}")
            guids.add(guid)
            deck.add_note(genanki.Note(
                model=MODEL,
                fields=[to_html(c.question, titres), to_html(c.answer, titres), fiche, section],
                tags=tags + [type_tag(c.question)],
                guid=guid,
            ))
            total += 1
    return list(decks.values()), total, len({d.split("::")[1] for d in decks})


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--output", default=str(ROOT / "dist" / "ai-engineering.apkg"), help="fichier .apkg à écrire")
    args = ap.parse_args()

    errors, _, _ = lint(stale_months=0)
    if errors:
        sys.exit("Export annulé :\n" + "\n".join(errors))
    decks, total, n_sections = build()
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    genanki.Package(decks).write_to_file(out)
    print(f"{total} cartes, {len(decks)} fiches, {n_sections} sections → {out}")


if __name__ == "__main__":
    main()
