#!/usr/bin/env python3
"""Attribue un identifiant permanent aux nouvelles cartes, sans modifier les anciens.

Usage : python3 scripts/assign_card_ids.py
Ne jamais retirer un identifiant pour reformuler ou déplacer une carte existante.
"""
import sys
import uuid

from lint_flashcards import fiche_files, parse_cards


def assign(text):
    cards, malformed = parse_cards(text)
    if malformed or any(not c.question or not c.answer for c in cards):
        raise ValueError(f"cartes mal formées ou vides (lignes {malformed})")
    lines = text.splitlines(keepends=True)
    missing = [c for c in cards if not c.guid]
    for card in reversed(missing):
        guid = uuid.uuid4().hex
        lines.insert(card.line, f"<!--anki:{guid.encode('ascii').hex()}-->\n")
    return "".join(lines), len(missing)


def main():
    # Préparer toutes les modifications avant d'écrire : aucun fichier partiellement migré.
    updates = []
    for path in fiche_files():
        try:
            text, count = assign(path.read_text())
        except ValueError as exc:
            sys.exit(f"{path.name} : {exc}")
        if count:
            updates.append((path, text, count))
    for path, text, _ in updates:
        path.write_text(text)
    print(f"{sum(count for _, _, count in updates)} identifiant(s) ajouté(s).")


if __name__ == "__main__":
    main()
