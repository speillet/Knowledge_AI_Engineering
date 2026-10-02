import contextlib
import io
import json
from pathlib import Path
import shutil
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import assign_card_ids as ids
import export_anki as export
import lint_flashcards as lint
import sync_catalog as catalog

ROOT = lint.ROOT


class ParserTests(unittest.TestCase):
    def test_missing_separator(self):
        cards, errors = lint.parse_cards("Question ?\nRéponse\n")
        self.assertEqual(cards, [])
        self.assertEqual(errors, [1])

    def test_empty_question_is_preserved_for_lint(self):
        cards, errors = lint.parse_cards("?\nRéponse\n")
        self.assertFalse(errors)
        self.assertEqual(cards[0].question, "")

    def test_code_is_not_structure(self):
        for fence in ("```", "~~~~"):
            with self.subTest(fence=fence):
                text = f"Question ?\n?\n{fence}text\n?\n---\n## Sources\n{fence}\n"
                cards, errors = lint.parse_cards(text)
                self.assertFalse(errors)
                self.assertEqual(len(cards), 1)
                self.assertIn("?\n---\n## Sources", cards[0].answer)

    def test_sources_and_connections_are_not_cards(self):
        for heading in ("Sources", "Connexions"):
            cards, errors = lint.parse_cards(f"Question ?\n?\nRéponse\n\n## {heading}\nTexte ?\n?\nAutre\n")
            self.assertFalse(errors)
            self.assertEqual(len(cards), 1)
            self.assertEqual(cards[0].answer, "Réponse")

    def test_index_preamble_is_excluded(self):
        cards, errors = lint.parse_cards("# Index\nIntroduction\n\n## Cartes\nQuestion ?\n?\nRéponse\n")
        self.assertFalse(errors)
        self.assertEqual(cards[0].question, "Question ?")

    def test_multiple_separators(self):
        cards, errors = lint.parse_cards("Question\n?\nRéponse\nQuestion 2\n?\nRéponse 2")
        self.assertFalse(cards)
        self.assertTrue(errors)

    def test_crlf_and_line_numbers(self):
        cards, errors = lint.parse_cards("# Titre\r\nTags: #flashcards\r\n\r\nQuestion ?\r\n?\r\nRéponse\r\n")
        self.assertFalse(errors)
        self.assertEqual(cards[0].line, 5)

    def test_metadata_hidden_and_guid_decoded(self):
        cards, errors = lint.parse_cards("Question ?\n?\n<!--anki:616263-->\nRéponse\n<!--SR:2026-10-02,1,250-->\n")
        self.assertFalse(errors)
        self.assertEqual(cards[0].guid, "abc")
        self.assertEqual(cards[0].answer, "Réponse")

    def test_summary_is_not_part_of_question(self):
        cards, errors = lint.parse_cards("# Titre\nTags: #flashcards\n<!-- summary: Résumé du catalogue. -->\nQuestion ?\n?\nRéponse\n")
        self.assertFalse(errors)
        self.assertEqual(cards[0].question, "Question ?")

    def test_bad_ids(self):
        for marker in ("<!--anki:xyz-->", "<!--anki:1-->", "<!--anki:ff-->", "<!--anki:00-->", "<!--anki:61-->\n<!--anki:62-->"):
            with self.subTest(marker=marker):
                cards, errors = lint.parse_cards(f"Q\n?\n{marker}\nA\n")
                self.assertFalse(cards)
                self.assertTrue(errors)

    def test_dates(self):
        for date in ("31 février 2026", "29 février 2025", "1 inconnu 2026", "0 janvier 2026"):
            self.assertIsNone(lint.parse_date("Vérifié le : " + date))
        self.assertEqual(str(lint.parse_date("Vérifié le : 29 février 2024")), "2024-02-29")

    def test_assign_is_idempotent_and_survives_rewording(self):
        text, count = ids.assign("Question ?\n?\nRéponse\n")
        self.assertEqual(count, 1)
        self.assertEqual(ids.assign(text), (text, 0))
        original = lint.parse_cards(text)[0][0].guid
        changed = lint.parse_cards(text.replace("Question ?", "Autre formulation ?"))[0][0].guid
        self.assertEqual(original, changed)

    def test_assign_rejects_invalid_cards(self):
        with self.assertRaises(ValueError):
            ids.assign("Question\nRéponse\n")


class VaultTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for source in lint.fiche_files() + [ROOT / "README.md", ROOT / f"{lint.MOC}.md", ROOT / "scripts/sections.json"]:
            target = self.root / source.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        self.patcher = patch.object(lint, "ROOT", self.root)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
        self.rag = self.root / "20-rag/21-rag-fondamentaux.md"

    def errors(self):
        return "\n".join(lint.lint(0)[0])

    def test_current_vault_is_clean(self):
        errors, warnings, stats = lint.lint(0)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])
        self.assertGreater(lint.summary(stats)["cartes"], 1500)

    def test_missing_separator_fails_lint(self):
        self.rag.write_text(self.rag.read_text().replace("\n?\n", "\n", 1))
        self.assertIn("carte mal formée", self.errors())

    def test_empty_question_fails_lint(self):
        self.rag.write_text(self.rag.read_text().replace("Qu'est-ce que le RAG ?", "", 1))
        self.assertIn("question vide", self.errors())

    def test_dead_link_in_moc_fails_lint(self):
        moc = self.root / f"{lint.MOC}.md"
        moc.write_text(moc.read_text() + "\n[[fiche-inexistante]]\n")
        self.assertIn("lien mort : [[fiche-inexistante]]", self.errors())

    def test_dead_markdown_link_in_readme_fails_lint(self):
        readme = self.root / "README.md"
        readme.write_text(readme.read_text() + "\n[Une fiche](fiche-inexistante.md)\n")
        self.assertIn("lien Markdown mort", self.errors())

    def test_invalid_date_fails_without_exception(self):
        self.rag.write_text(self.rag.read_text().replace("\n<!-- summary:", "\nVérifié le : 31 février 2026\n<!-- summary:", 1))
        self.assertIn("date « Vérifié le » illisible", self.errors())

    def test_dated_fiche_requires_sources(self):
        self.rag.write_text(self.rag.read_text().replace("\n<!-- summary:", "\nVérifié le : 1 janvier 2020\n<!-- summary:", 1))
        self.assertIn("sans référence HTTPS", self.errors())

    def test_duplicate_id_fails(self):
        text = self.rag.read_text()
        identifiers = lint.ID_RE.findall(text)
        self.rag.write_text(text.replace(identifiers[1], identifiers[0], 1))
        self.assertIn("identifiant Anki en double", self.errors())

    def test_missing_id_fails(self):
        self.rag.write_text(lint.ID_RE.sub("", self.rag.read_text(), count=1))
        self.assertIn("identifiant Anki absent", self.errors())

    def test_generated_catalog_drift(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertTrue(catalog.sync(self.root, check=True))
            self.rag.write_text(self.rag.read_text().replace("# RAG — Fondamentaux", "# RAG — Nouveau titre", 1))
            self.assertFalse(catalog.sync(self.root, check=True))
            catalog.sync(self.root)
            self.assertTrue(catalog.sync(self.root, check=True))

    def test_more_than_nine_fiches(self):
        directory = self.root / "30-agents"
        new = directory / "30-010-nouvelle-fiche.md"
        new.write_text("# Nouvelle fiche — Flashcards\nTags: #flashcards\n<!-- summary: Une dixième fiche. -->\n")
        names = [p.name for p in sorted(directory.glob("*.md"), key=catalog.fiche_order)]
        self.assertEqual(names[-1], new.name)
        self.assertIn(new.stem, catalog.render(self.root, moc=True))

    def test_export_rejects_invalid_cards(self):
        self.rag.write_text(self.rag.read_text().replace("\n?\n", "\n", 1))
        with patch.object(export, "ROOT", self.root), self.assertRaises(ValueError):
            export.build()

    def test_export_identity_survives_rename_and_rewording(self):
        card = lint.parse_cards(self.rag.read_text())[0][0]
        self.rag.write_text(self.rag.read_text().replace(card.question, "Nouvelle formulation du RAG ?", 1))
        self.rag.rename(self.rag.with_name("28-rag-renomme.md"))
        with patch.object(export, "ROOT", self.root):
            decks, _, _ = export.build()
        notes = [note for deck in decks for note in deck.notes if note.guid == card.guid]
        self.assertEqual(len(notes), 1)
        self.assertIn("Nouvelle formulation du RAG ?", notes[0].fields[0])


class ExportTests(unittest.TestCase):
    def test_legacy_guids_preserved(self):
        historical = set(json.loads((ROOT / "tests/fixtures/legacy_guids.json").read_text()))
        current = [c.guid for p in lint.fiche_files() for c in lint.parse_cards(p.read_text())[0]]
        self.assertEqual(len(current), len(set(current)))
        self.assertTrue(historical <= set(current), "Une carte historique a perdu son identifiant ; vérifier toute suppression intentionnelle.")

    def test_container_question_and_legacy_guid(self):
        card = lint.parse_cards((ROOT / "70-containers-infra/00-index.md").read_text())[0][0]
        self.assertEqual(card.question, "Pourquoi les conteneurs sont-ils devenus le standard pour servir des modèles ?")
        self.assertIsNotNone(card.guid)

    def test_runtimeclass_yaml_is_complete(self):
        cards, _ = lint.parse_cards((ROOT / "70-containers-infra/03-containerd-runc.md").read_text())
        card = next(c for c in cards if "déclarer un runtime alternatif" in c.question)
        self.assertIn("---\napiVersion: v1\nkind: Pod", card.answer)
        self.assertIn("runtimeClassName: gvisor", card.answer)

    def test_package_database(self):
        decks, total, sections = export.build()
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp) / "test.apkg"
            export.genanki.Package(decks).write_to_file(package)
            with zipfile.ZipFile(package) as archive:
                database = Path(tmp) / "collection.anki2"
                database.write_bytes(archive.read("collection.anki2"))
            with sqlite3.connect(database) as db:
                self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0], "ok")
                self.assertEqual(db.execute("SELECT count(*) FROM notes").fetchone()[0], total)
                self.assertEqual(db.execute("SELECT count(*) FROM cards").fetchone()[0], total)
                self.assertEqual(db.execute("SELECT count(DISTINCT guid) FROM notes").fetchone()[0], total)
                for fields, in db.execute("SELECT flds FROM notes"):
                    question, answer, _, _ = fields.split("\x1f")
                    self.assertTrue(question.strip())
                    self.assertTrue(answer.strip())
                    self.assertNotIn("&lt;!--anki:", fields)
                    self.assertNotIn("<!--anki:", fields)
                    self.assertNotIn("summary:", fields)
            self.assertEqual(sections, 16)


if __name__ == "__main__":
    unittest.main()
