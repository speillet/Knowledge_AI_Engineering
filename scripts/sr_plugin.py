"""Lecture des fiches telle que la fait le plugin Obsidian Spaced Repetition (version 1.15.4).

Transcription fidèle de la fonction parse() de src/parser.ts, défauts compris, pour que le lint
vérifie que le plugin voit exactement les mêmes cartes que l'export Anki. Deux comportements
du plugin dictent la mise en page des fiches :
- une ligne qui commence par <!-- (hors <!--SR:) est sautée, et la ligne suivante aussi ;
- sans marqueur de fin, une carte s'arrête à la première ligne vide : le README impose `---`.
"""
import re

OPTIONS = {
    "single": "::",
    "single_reversed": ":::",
    "multiline": "?",
    "multiline_reversed": "??",
    "end_marker": "---",  # réglage « Characters denoting the end of clozes and multiline flashcards »
}
SR_METADATA_CALLOUT = "> [!sr|card-metadata]"
CLOZE_RE = re.compile(r"==.+?==")  # motif de cloze par défaut ==answer== (surlignage)


def _inside_code(text, marker, index):
    before = text[:index].count("`")
    after = text[index + len(marker):].count("`")
    return before % 2 == 1 and after % 2 == 1


def _has_inline_marker(text, marker):
    index = text.find(marker) if marker else -1
    return index != -1 and not _inside_code(text, marker, index)


def parse(text, options=OPTIONS):
    """Liste de (type, texte) : type vaut single, single_reversed, multiline, multiline_reversed ou cloze."""
    separators = sorted([(options["single"], "single"), (options["single_reversed"], "single_reversed")],
                        key=lambda s: -len(s[0]))
    cards, card_text, card_type = [], "", None
    lines = text.replace("\r\n", "\n").split("\n")
    i = 0
    while i < len(lines):
        line, trimmed = lines[i], lines[i].strip()
        if line.startswith("<!--") and not line.startswith("<!--SR:"):
            while i + 1 < len(lines) and "-->" not in line:
                i += 1
            i += 2  # défaut du plugin : la ligne qui suit le commentaire est perdue
            continue
        empty = not trimmed
        end_marker = options["end_marker"] and trimmed == options["end_marker"]
        if (empty and not options["end_marker"]) or (empty and card_type is None) or end_marker:
            if card_type:
                cards.append((card_type, card_text.rstrip()))
                card_type = None
            card_text = ""
            i += 1
            continue
        if card_text:
            card_text += "\n"
        card_text += line.rstrip()
        for separator, kind in separators:
            if _has_inline_marker(line, separator):
                card_type = kind
                break
        if card_type in ("single", "single_reversed"):
            card_text = line
            if i + 1 < len(lines) and lines[i + 1].startswith("<!--SR:"):
                card_text += "\n" + lines[i + 1]
                i += 1
            elif i + 1 < len(lines) and lines[i + 1].startswith(SR_METADATA_CALLOUT):
                for j in range(i + 1, len(lines)):
                    card_text += "\n" + lines[j]
                    i += 1
                    if "<!--SR:" in lines[j]:
                        break
            cards.append((card_type, card_text))
            card_type, card_text = None, ""
        elif trimmed == options["multiline"]:
            if len(card_text) > 1:
                card_type = "multiline"
        elif trimmed == options["multiline_reversed"]:
            if len(card_text) > 1:
                card_type = "multiline_reversed"
        elif line.startswith("```") or line.startswith("~~~"):
            fence = re.search(r"`+|~+", line)[0]
            while i + 1 < len(lines) and not lines[i + 1].startswith(fence):
                i += 1
                card_text += "\n" + lines[i]
            card_text += "\n" + fence
            i += 1
        elif card_type is None and CLOZE_RE.search(line):
            card_type = "cloze"
        i += 1
    if card_type and card_text:
        cards.append((card_type, card_text.rstrip()))
    return cards
