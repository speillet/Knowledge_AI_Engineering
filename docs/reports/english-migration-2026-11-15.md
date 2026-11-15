# English repository migration — 15 November 2026

The migration covers all 153 published topics and 2,775 active cards, the README and map of content, learning paths and historical review reports, source labels, tags, illustrative code, workshops and fixtures, Python documentation and diagnostics, CI descriptions, and repository maintenance instructions. French filenames and directories have English names, with references updated together.

The 71 retired cards remain suspended in Anki exports. Existing factual verification dates are retained: translation is not a new verification of every historical claim.

## Anki compatibility

Permanent note GUIDs and model ID `1718293041` are unchanged. The four fields retain their ordinal positions and are now named Question, Answer, Topic and Section. The single question-and-answer template is retained.

Deck IDs previously depended on French names. `scripts/deck_ids.json` now preserves the 154 existing IDs by stable numeric section/topic prefixes, including the retired deck. New topics continue to receive a deterministic ID. The migration fixtures record the original GUIDs and note-to-deck associations, so tests can detect accidental identity changes independently of translated wording.

Anki imports should be made into a backed-up collection using the same update procedure described in the README. Package-level identity checks do not constitute a test of every Anki client version or a synchronization mechanism between Anki and Obsidian.

## Translation and review

Bulk prose was translated locally with [OPUS-MT French–English](https://huggingface.co/Helsinki-NLP/opus-mt-tc-big-fr-en), with protected identifiers, links, code and numerical expressions. Subsequent passes corrected terminology, formatting, English labels, examples and parser conventions. The source model is distributed under CC BY 4.0; see its model card for authorship and the OPUS-MT research references.

Reviews specifically addressed concurrency, model versus template, calculation units and thousands separators, code examples, English retrieval vocabulary, and false positives in language-dependent lint rules. The RAG workshop uses consistent English terms in questions and documents while retaining its original outcomes: all ten filtered cases pass; the baseline fails all ten and produces twenty context violations.

A further review corrected substitution damage in three words, restored Harbor's `verifier` paths and configuration section, and refined the skills, distributed-systems and document-parsing translations against their French originals. Technical terms such as acknowledgment, isolation, fencing tokens, control plane and durable execution use their established English forms. These targeted reviews do not amount to a sentence-by-sentence human review of the entire vault.

Historical reports retain their original scope, counts and verification limits. Source URLs and historical Git commit identifiers remain references to their original targets. Third-party names, licensed skill text already in English, and deliberate Unicode examples are retained where their exact spelling matters.

## Validation

The repository's normal checks cover topic structure and links, generated catalogs, ruff, mypy, parser/export tests, and deterministic SQL and decision workshops. Additional migration tests check historical GUID coverage, note-to-deck associations, and model field order. The Anki package is built and inspected before publication. Local validation passed: 57 repository tests, ruff, mypy, catalog checks and both standard-library workshops, plus all 18 agentic workshop tests and its demo. The exported SQLite collection passed its integrity check with 2,846 distinct notes: 2,775 active cards and 71 suspended retired cards. Source URL comparison and repository-wide Markdown link checks also passed.

GitHub metadata is translated alongside the content: repository description, the Anki release, and user-authored pull request titles and bodies. The comment inventory was empty, including issue, review, commit and review-summary comments. Existing Git history and third-party English pull requests are retained.
