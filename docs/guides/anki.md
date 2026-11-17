# Review with Anki

Every push to `main` generates an Anki package and publishes it at a stable address:

[Download the Anki package](https://github.com/speillet/Knowledge_AI_Engineering/releases/download/anki/ai-engineering.apkg).

Each pull request merged into `main` also publishes a versioned release, tagged with the UTC date of the merge, `anki-vYYYY.MM.DD` (`.2`, `.3`… for later merges that day), with notes that list the merged changes: see the [releases](https://github.com/speillet/Knowledge_AI_Engineering/releases). Download one to keep a fixed reference; the stable link always serves the latest build of `main`.

1. Install **AnkiDroid** from the Play Store or F-Droid.
2. Download the package on your phone and open it with AnkiDroid. It imports into **AI Engineering**, organized by section and topic.
3. To update, download and import it again. Each note has a permanent `<!--anki:…-->` identifier, so rewording a question or renaming a file can update the existing note while retaining its review history.
   - Keep that identifier when editing a card.
   - A new question receives a new identifier through `scripts/assign_card_ids.py`.
   - Retired cards are re-exported suspended with the `retired` tag. Search for `tag:retired` in Anki to delete them.
4. Anki and Obsidian maintain separate review schedules; their progress is not synchronized.

The migration preserves note GUIDs, the model ID and the existing deck IDs. See the [migration report](../reports/english-migration-2026-11-15.md) for the compatibility checks.

To generate the package locally:

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r scripts/requirements.txt
python3 scripts/export_anki.py      # writes dist/ai-engineering.apkg
```
