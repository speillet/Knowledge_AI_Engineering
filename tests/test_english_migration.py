"""Compatibility checks for the French-to-English content migration."""

import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import export_anki as export
import lint_flashcards as lint


class EnglishMigrationTests(unittest.TestCase):
    def test_pretranslation_notes_keep_their_identity_and_deck(self):
        fixture = lint.ROOT / "tests/fixtures/english_migration_decks.json"
        historical = json.loads(fixture.read_text(encoding="utf-8"))
        decks, _, _ = export.build()
        current = {note.guid: (deck.deck_id, note.tags) for deck in decks for note in deck.notes}
        self.assertTrue(historical.keys() <= current.keys())
        for guid, deck_id in historical.items():
            with self.subTest(guid=guid):
                actual_id, tags = current[guid]
                if "retired" not in tags:
                    self.assertEqual(actual_id, deck_id)

    def test_model_identity_and_field_order_are_compatible(self):
        self.assertEqual(export.MODEL.model_id, 1718293041)
        self.assertEqual([field["name"] for field in export.MODEL.fields], ["Question", "Answer", "Topic", "Section"])
        self.assertEqual(len(export.MODEL.templates), 1)
        self.assertIn("{{Topic}}", export.MODEL.templates[0]["qfmt"])
        self.assertIn("{{Answer}}", export.MODEL.templates[0]["afmt"])

    def test_all_migration_guids_remain_active_or_explicitly_retired(self):
        fixture = lint.ROOT / "tests/fixtures/english_migration_guids.json"
        historical = set(json.loads(fixture.read_text(encoding="utf-8")))
        current = {
            card.guid for path in lint.topic_files() for card in lint.parse_cards(path.read_text(encoding="utf-8"))[0]
        }
        retired = {lint.decode_guid(entry["id"]) for entry in lint.retired_cards()}
        self.assertTrue(historical <= current | retired)


if __name__ == "__main__":
    unittest.main()
