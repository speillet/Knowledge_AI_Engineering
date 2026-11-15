#!/usr/bin/env python3
"""Assigns a permanent ID to new cards, without changing old ones.

Usage : python3 scripts/assign_card_ids.py
Never remove an identifier to reformulate or move an existing card.
"""

from pathlib import Path
import sys
import uuid

from lint_flashcards import parse_cards, topic_files


def assign(text: str) -> tuple[str, int]:
    """Adds the identifier at the end of the question: on its own line, the plugin
    Spaced Repetition would also skip the next line (see sr_plugin.py).
    Returns the text and the number of identifiers added."""
    cards, malformed = parse_cards(text)
    if malformed or any(not c.question or not c.answer for c in cards):
        raise ValueError(f"poorly formed or empty cards (lines) {malformed})")
    lines = text.splitlines(keepends=True)
    missing = [c for c in cards if not c.guid]
    for card in missing:
        index = card.line - 2  # The line before the separator?
        while not lines[index].strip():
            index -= 1
        content = lines[index].rstrip("\r\n")
        ending = lines[index][len(content) :]
        guid = uuid.uuid4().hex
        lines[index] = f"{content.rstrip()} <!--anki:{guid.encode('ascii').hex()}-->{ending}"
    return "".join(lines), len(missing)


def main() -> None:
    # Prepare all changes before writing: no partially migrated files.
    updates: list[tuple[Path, str, int]] = []
    for path in topic_files():
        try:
            text, count = assign(path.read_text(encoding="utf-8"))
        except ValueError as exc:
            sys.exit(f"{path.name} : {exc}")
        if count:
            updates.append((path, text, count))
    for path, text, _ in updates:
        path.write_text(text, encoding="utf-8", newline="\n")
    print(f"{sum(count for (_, _, count) in updates)} ID(s) added.")


if __name__ == "__main__":
    main()
