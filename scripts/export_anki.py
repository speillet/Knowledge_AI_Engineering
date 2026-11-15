#!/usr/bin/env python3
"""Exports the cards of the vault in Anki package (.apkg), to revise on the phone with AnkiDroid.

Usage :
    pip install -r scripts/requirements.txt
    python3 scripts/export_anki.py # writes dist/ai-engineering.apkg
    python3 scripts/export_anki.py --output autre.apkg

Each note carries a permanent <!--anki:...--> identifier: a reimport updates
existing notes even if their question or file changes.
The scripts/retired_cards.json cards are republished suspended, with the tag removed:
A tag:retired search in Anki allows you to delete them.
<!--SR:...--> comments from the Obsidian plugin are ignored.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

import genanki
from markdown_it import MarkdownIt

from lint_flashcards import MOC, ROOT, decode_guid, lint, parse_cards, retired_cards, topic_files, topic_title

ROOT_DECK = "AI Engineering"
RETIRED_DECK = "999 — Cards removed"
DECK_IDS = json.loads((ROOT / "scripts/deck_ids.json").read_text(encoding="utf-8"))
MODEL_ID = 1718293041  # fixed: changing this identifier would duplicate all notes

SR_RE = re.compile(r"<!--SR:.*?-->", re.S)
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|([^\]]+))?\]\]")
SECTION_RE = re.compile(r"^## (\d+) — (.+)$", re.M)
TOPIC_NUMBER_RE = re.compile(r"\d+(?:-\d+)?")  # 21-rag… → 21, 30-010-… → 30-010

CSS = """
.card {
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  font-size: 18px; line-height: 1.45; text-align: left;
  color: #1d1d1f; background: #ffffff; padding: 0 4px;
}
.context { margin-bottom: .5em; font-size: .72em; color: #6b6b70; }
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
.link { color: #1a5fb4; border-bottom: 1px dotted currentColor; }
.source { margin-top: 1.4em; font-size: .72em; color: #6b6b70; }
hr#answer { border: 0; border-top: 1px solid #d0d0d5; margin: 1em 0; }

.nightMode.card, .night_mode.card, .nightMode .card, .night_mode .card { color: #e7e7ea; background: #1e1e20; }
.nightMode strong, .night_mode strong { color: #9cc3ff; }
.nightMode code, .night_mode code, .nightMode pre, .night_mode pre { background: #2c2c30; }
.nightMode pre code, .night_mode pre code { background: none; }
.nightMode .link, .night_mode .link { color: #8ab4f8; }
.nightMode .source, .night_mode .source,
.nightMode .context, .night_mode .context { color: #9a9aa0; }
.nightMode hr#answer, .night_mode hr#answer { border-top-color: #44444a; }
"""

MODEL = genanki.Model(
    MODEL_ID,
    "AI Engineering",
    fields=[{"name": "Question"}, {"name": "Answer"}, {"name": "Topic"}, {"name": "Section"}],
    templates=[
        {
            "name": "Question → Answer",
            "qfmt": '<div class="context">{{Topic}}</div><div class="question">{{Question}}</div>',
            "afmt": '{{FrontSide}}<hr id="answer">{{Answer}}<div class="source">{{Section}}</div>',
        }
    ],
    css=CSS,
)

md = MarkdownIt("commonmark", {"html": False})


def stable_id(text: str) -> int:
    """Stable deck identifier from one export to another, derived from its name."""
    return int(hashlib.sha1(text.encode()).hexdigest()[:8], 16) % (1 << 30) + (1 << 30)


def to_html(markdown: str, titles: dict[str, str]) -> str:
    """Markdown → HTML Anki; wikilinks become the title of the cited file."""
    html = md.render(SR_RE.sub("", markdown).strip())

    def link(m: re.Match[str]) -> str:
        target, alias = m.group(1).strip(), m.group(2)
        return f'<span class="link">{alias or titles.get(target, target)}</span>'

    return WIKILINK_RE.sub(link, html)


def type_tag(question: str) -> str:
    """Anki tag of the card type, deduced from the question prefix."""
    for prefix, tag in (("Scenario:", "scenario"), ("Do not confuse", "confusion"), ("Calculation:", "calculation")):
        if question.startswith(prefix):
            return f"type::{tag}"
    return "type::question"


def build() -> tuple[list[genanki.Deck], int, int]:
    """Decks per card, number of vault cards and number of sections."""
    moc = (ROOT / f"{MOC}.md").read_text(encoding="utf-8")
    sections = {num: name.strip() for num, name in SECTION_RE.findall(moc)}
    files = topic_files()
    texts = {p: p.read_text(encoding="utf-8") for p in files}
    titles = {p.stem: topic_title(text) for p, text in texts.items()} | {MOC: topic_title(moc)}

    decks: dict[str, genanki.Deck] = {}
    guids: set[str] = set()
    total = 0
    for p in files:
        section_number = p.parent.name.split("-", 1)[0]
        section = f"{int(section_number):03d} — {sections[section_number]}"  # 3 digits: Anki sort alphabetically
        topic = titles[p.stem]
        topic_number = TOPIC_NUMBER_RE.match(p.stem)
        if not topic_number:
            raise ValueError(f"{p.name} : name of file without number")
        deck_name = f"{ROOT_DECK}::{section}::{topic_number[0]} {topic}"
        deck = decks.setdefault(
            deck_name,
            genanki.Deck(DECK_IDS.get(f"{section_number}/{topic_number[0]}", stable_id(deck_name)), deck_name),
        )

        text = texts[p]
        tags = [f"section::{p.parent.name}", f"topic::{p.stem}"]
        if "\nVerified on" in text:
            tags.append("verified")

        cards, malformed = parse_cards(text)
        if malformed or not cards:
            raise ValueError(f"{p.name} : poorly formed or absent cards (lines) {malformed})")
        for c in cards:
            guid = c.guid
            if not guid or not c.question or not c.answer:
                raise ValueError(f"{p.name}:{c.line} : identifier, Missing question or answer")
            if guid in guids:
                raise ValueError(f"Identifier in duplicate {p.name} : {c.question[:60]}")
            guids.add(guid)
            deck.add_note(
                genanki.Note(
                    model=MODEL,
                    fields=[to_html(c.question, titles), to_html(c.answer, titles), topic, section],
                    tags=[*tags, type_tag(c.question)],
                    guid=guid,
                )
            )
            total += 1
    n_sections = len({d.split("::")[1] for d in decks})

    retired = retired_cards()
    if retired:
        deck_name = f"{ROOT_DECK}::{RETIRED_DECK}"
        deck = decks.setdefault(deck_name, genanki.Deck(DECK_IDS["retired"], deck_name))
        for entry in retired:
            guid = decode_guid(entry["id"])
            if guid in guids:
                raise ValueError(f"Removed identifier still present in the vault: {entry['question'][:60]}")
            guids.add(guid)
            reason = f" ({entry['reason']})" if entry.get("reason") else ""
            note = genanki.Note(
                model=MODEL,
                fields=[
                    to_html(entry["question"], titles),
                    f"<p>Card retired from the vault{reason}. To delete it, search for <code>tag:retired</code>.</p>",
                    "Retired cards",
                    RETIRED_DECK,
                ],
                tags=["retired"],
                guid=guid,
            )
            for card in note.cards:
                card.suspend = True  # a new import does not offer them for review
            deck.add_note(note)
    return list(decks.values()), total, n_sections


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--output", default=str(ROOT / "dist" / "ai-engineering.apkg"), help=".apkg file to write")
    args = ap.parse_args()

    errors, _, _ = lint(stale_months=0)
    if errors:
        sys.exit("Export cancelled:\n" + "\n".join(errors))
    decks, total, n_sections = build()
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    genanki.Package(decks).write_to_file(out)
    topics = sum(not d.name.endswith(RETIRED_DECK) for d in decks)
    print(f"{total} cards, {topics} topics, {n_sections} sections, {len(retired_cards())} retired card(s) → {out}")


if __name__ == "__main__":
    main()
