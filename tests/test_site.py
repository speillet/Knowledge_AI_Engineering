"""The site must preserve card content and turn source links into usable web links."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import lint_flashcards as lint
import prepare_site as site


class SiteTests(unittest.TestCase):
    def setUp(self):
        self.source = Path("20-rag/21-rag-fundamentals.md")
        self.target = Path("30-agents/31-agent-fundamentals.md")
        self.pages = {self.source, self.target, Path("README.md")}
        self.wikis = {self.target.stem: self.target}

    def render(self, text):
        return site.render(text, self.source, self.pages, self.wikis)

    def test_links_and_code(self):
        result = self.render(
            "[[31-agent-fundamentals#Tool calls|Tools]]\n"
            "[Home](../README.md)\n[Script](../scripts/export_anki.py)\n"
            "`[[missing]]`\n```text\n[[missing]]\n?\n---\n```\n"
        )
        self.assertIn("[Tools](../30-agents/31-agent-fundamentals.md#tool-calls)", result)
        self.assertIn("[Home](../index.md)", result)
        self.assertIn("/blob/main/scripts/export_anki.py)", result)
        self.assertIn("`[[missing]]`", result)
        self.assertIn("```text\n[[missing]]\n?\n---\n```", result)

    def test_missing_wikilink_fails(self):
        with self.assertRaisesRegex(ValueError, "unknown wikilink"):
            self.render("[[missing]]")

    def test_answers_close_before_sources_and_code_stays_intact(self):
        result = self.render("Question? <!--anki:616263-->\n?\nAnswer.\n```text\n?\n---\n```\n## Sources\nSource.\n")
        self.assertEqual(result.count('<details markdown="1">'), 1)
        self.assertEqual(result.count("</details>"), 1)
        self.assertNotIn("<!--anki:", result)
        self.assertLess(result.index("</details>"), result.index("## Sources"))
        self.assertIn("```text\n?\n---\n```", result)

    def test_every_active_card_has_one_answer_panel(self):
        pages = {p.relative_to(lint.ROOT) for p in site.source_pages(lint.ROOT)}
        wikis = {p.stem: p for p in pages if p.name != "README.md"}
        for path in lint.topic_files():
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                cards, errors = lint.parse_cards(text)
                self.assertFalse(errors)
                rendered = site.render(text, path.relative_to(lint.ROOT), pages, wikis)
                self.assertEqual(rendered.count('<details markdown="1">'), len(cards))
                self.assertEqual(rendered.count("</details>"), len(cards))

    def test_directory_readmes_map_to_landing_pages(self):
        self.assertEqual(site.site_path(Path("docs/guides/README.md")), Path("docs/guides/index.md"))
        self.assertEqual(site.site_path(self.source), self.source)


if __name__ == "__main__":
    unittest.main()
