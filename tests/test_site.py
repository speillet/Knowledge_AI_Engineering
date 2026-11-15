"""The site must preserve card content, fold pages into collapsible blocks and turn links into Hugo references."""

from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import check_site
import lint_flashcards as lint
import prepare_site as site

TOPIC = (
    "# Demo — Flashcards\nTags: #flashcards #rag\n<!-- summary: one, two (a, b); three. -->\n\n\n"
    "What is RAG? <!--anki:616263-->\n?\nAnswer.\n```text\n?\n---\n```\n\n---\n\n"
    "Calculation: how many? <!--anki:646566-->\n?\nTwo.\n\n---\n\n"
    "## Scenarios\n\nScenario: a case. <!--anki:676869-->\n?\n1. Step.\n\n---\n\n"
    "## Sources\n\n- [Source](https://example.org)\n\n"
    "## Connections\n- [[31-agent-fundamentals|Agents]] — the loop\n- [[00-moc-ai-engineering|MOC AI Engineering]]\n"
)


class SiteTests(unittest.TestCase):
    def setUp(self):
        self.source = Path("20-rag/21-rag-fundamentals.md")
        self.target = Path("30-agents/31-agent-fundamentals.md")
        self.pages = {self.source, self.target, Path("README.md")}
        self.wikis = {self.target.stem: self.target}
        self.convert = site.link_converter(self.source, self.pages, self.wikis)

    def test_links_become_references_and_code_stays_intact(self):
        result = site.convert_block(
            "[[31-agent-fundamentals#Tool calls|Tools]]\n"
            "[Home](../README.md)\n[Script](../scripts/export_anki.py)\n"
            "`[[missing]]`\n```text\n[[missing]]\n?\n---\n```\n",
            self.convert,
        )
        self.assertIn('[Tools]({{< relref "/30-agents/31-agent-fundamentals.md#tool-calls" >}})', result)
        self.assertIn('[Home]({{< relref "/_index.md" >}})', result)
        self.assertIn("/blob/main/scripts/export_anki.py)", result)
        self.assertIn("`[[missing]]`", result)
        self.assertIn("```text\n[[missing]]\n?\n---\n```", result)

    def test_missing_wikilink_fails(self):
        with self.assertRaisesRegex(ValueError, "unknown wikilink"):
            self.convert("[[missing]]")

    def test_topic_cards_are_grouped_by_kind_under_headings(self):
        front, body, topic = site.topic_page(self.source, TOPIC, self.convert, self.wikis, 1)
        self.assertEqual(front["params"]["counts"], {"concept": 1, "confuse": 0, "calculation": 1, "scenario": 1})
        self.assertEqual(front["params"]["covers"], ["One", "Two (a, b)", "Three"])
        self.assertEqual((topic.title, topic.cards), ("Demo", 3))
        self.assertEqual(body.count('<details class="kv-card '), 3)
        self.assertLess(body.index("## Key concepts {#key-concepts}"), body.index("## Calculations {#calculations}"))
        self.assertLess(body.index("## Calculations"), body.index("## Scenarios {#scenarios}"))
        self.assertIn('<summary><span class="kv-q">How many?</span>', body)
        self.assertIn("```text\n?\n---\n```", body)
        self.assertNotIn("<!--anki:", body)
        self.assertIn('relref "/30-agents/31-agent-fundamentals.md"', body)
        self.assertNotIn("MOC AI Engineering", body)

    def test_every_active_card_has_one_panel(self):
        pages = {p.relative_to(lint.ROOT) for p in site.source_pages(lint.ROOT)}
        wikis = {p.stem: p for p in pages if p.name != "README.md"}
        for path in lint.topic_files():
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                cards, errors = lint.parse_cards(text)
                self.assertFalse(errors)
                source = path.relative_to(lint.ROOT)
                _, body, _ = site.topic_page(source, text, site.link_converter(source, pages, wikis), wikis, 1)
                self.assertEqual(body.count('<details class="kv-card '), len(cards))

    def test_subsections_fold_inside_their_sections(self):
        markdown = "Intro.\n\n## First\nA.\n### Inner\nB.\n## Second\nC.\n```text\n### not a heading\n```\n"
        body = site.fold_subsections(markdown, site.Ids())
        self.assertTrue(body.startswith("Intro."))
        self.assertIn("## First\nA.", body)
        self.assertIn('<details class="kv-fold" id="inner">', body)
        self.assertLess(body.index('id="inner"'), body.index("## Second"))
        self.assertIn("```text\n### not a heading\n```", body)

    def test_link_lists_become_card_grids(self):
        steps = "0. [A](https://a.example) — first\n1. [B](https://b.example) — second\n2. [C](https://c.example)\n"
        result = site.cardify_lists(steps)
        self.assertIn('<ol class="kv-grid kv-steps not-prose">', result)
        self.assertIn('<span class="kv-step-num">0</span>', result)
        mixed = "- [A](https://a.example)\n- plain text\n- [C](https://c.example)\n"
        self.assertEqual(site.cardify_lists(mixed), mixed.rstrip("\n"))

    def test_domain_route_and_catalog_follow_the_sections(self):
        first = site.Topic(Path("20-rag/21-a.md"), "First", "", ["X"], {"concept": 2}, 2)
        second = site.Topic(Path("20-rag/22-b.md"), "Second", "", [], {"concept": 1, "scenario": 1}, 2)
        prerequisite = site.Topic(Path("130-llm/133-c.md"), "Prerequisite", "", [], {"concept": 1}, 1)
        meta = {t.source: t for t in (first, second, prerequisite)}
        info = {
            "title": "RAG",
            "intro": "Retrieve.",
            "core": ["22-b.md", "21-a.md"],
            "prerequisites": ["130-llm/133-c.md"],
        }
        front, body = site.domain_page(Path("20-rag/README.md"), info, [first, second], meta)
        self.assertEqual((front["weight"], front["params"]["number"]), (20, "20"))
        self.assertLess(body.index("Second"), body.index("First"))
        first_step = (
            '<span class="kv-step-num">1</span>'
            '<a class="kv-tile-title" href="{{< relref "/20-rag/22-b.md" >}}">'
        )
        self.assertIn(first_step, body)
        self.assertIn('relref "/130-llm/133-c.md"', body)
        catalog = site.catalog_body("Intro.", {"20-rag": info}, {"20-rag": [first, second]})
        self.assertIn('<details class="kv-fold kv-domain" id="20-rag" open>', catalog)
        self.assertEqual(catalog.count('<li class="kv-tile">'), 2)

    def test_link_check_reports_missing_pages_and_anchors(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a").mkdir()
            (root / "a/index.html").write_text('<h2 id="x">X</h2><a href="#x">ok</a>', encoding="utf-8")
            page = '<a href="/a/#x">ok</a><a href="/a/#y">anchor</a><a href="/b/">page</a><a href="https://e.org/">ext</a>'
            (root / "index.html").write_text(page, encoding="utf-8")
            errors, count = check_site.check(root, "/")
        self.assertEqual(count, 2)
        self.assertEqual(errors, ["index.html: missing anchor /a/#y", "index.html: missing target /b/"])

    def test_directory_readmes_map_to_section_indexes(self):
        self.assertEqual(site.content_path(Path("docs/guides/README.md")), Path("docs/guides/_index.md"))
        self.assertEqual(site.content_path(Path("README.md")), Path("_index.md"))
        self.assertEqual(site.content_path(self.source), self.source)


if __name__ == "__main__":
    unittest.main()
