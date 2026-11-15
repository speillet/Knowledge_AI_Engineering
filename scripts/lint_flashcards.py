#!/usr/bin/env python3
"""Checks the conventions of flashcard cards and calculates the statistics of the vault.

Usage :
    python3 scripts/lint_flashcards.py # check, non-zero output on error
    python3 scripts/lint_flashcards.py --stats # also displays the stats by file
    python3 scripts/lint_flashcards.py --update-readme # rewrites the README "State to..." line
    python3 scripts/lint_flashcards.py --stale-months 6 # reports "Verified on" older than 6 months

Errors break the revision or navigation (dead link, poorly formed map...).
Warnings indicate a deviation to the style guide (too long card, orphan card...).
"""

import argparse
import collections
from collections.abc import Iterator
from dataclasses import dataclass, field
import datetime
import json
from pathlib import Path
import re
import sys
from typing import Any, NamedTuple
from urllib.parse import unquote

import sr_plugin

ROOT = Path(__file__).resolve().parent.parent
MOC = "00-moc-ai-engineering"
INDEXES = {MOC, "00-index"}
README = "README.md"
CATALOG = "docs/catalog.md"
CONTAINERS_INDEX = "70-containers-infra/00-index.md"
RETIRED = "scripts/retired_cards.json"

MAX_WORDS = 110  # standard card, excluding code blocks
MAX_WORDS_SCENARIO = 140
MIN_SCENARIOS = 2
MAX_ITEMS = 5  # Beyond that, the list is divided into sub-maps
MAX_STEPS = 6  # Stages of a Situation

MONTHS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]

LINK_RE = re.compile(r"\[\[([^\]|#]+)")
MD_LINK_RE = re.compile(r"(?<!!)\[[^\]\n]*\]\(([^)\s]+)\)")
URL_SCHEME_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9+.-]*:")
INLINE_CODE_RE = re.compile(r"`+[^`]*`+")
CODE_RE = re.compile(r"```.*?```", re.S)
FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
END_OF_CARDS_RE = re.compile(r"^## (Sources|Connections)\s*$")
SOURCES_RE = re.compile(r"^## Sources\s*\n(.*?)(?=^## |\Z)", re.M | re.S)
HTTPS_LINK_RE = re.compile(r"\[[^\]]+\]\(https://[^)]+\)")
VERIFIED_RE = re.compile(r"^Verified on: (\d{1,2}) (\w+) (\d{4})", re.M)
# question that can only be understood with the previous card ("What about TGI?", "How does it work?")
OUT_OF_CONTEXT_RE = re.compile(r"^(And\b|What about\b|How does (it|this|that)\b|What does improve do\b)", re.I)
# list of names to recite: prefer “Which tool for such a need?”
PRODUCT_LIST_RE = re.compile(
    r"^(Name|List|Give examples|(?:Which|What) (?:\w+ )?(?:tools|products|alternatives|frameworks"
    r"|servers|solutions|platforms"
    r"|libraries|benchmarks|services)|.*\b(?:should (?:I|you) know|to know)\s*\?$)",
    re.I,
)
# “What is the difference between X and Y?” or “X or Y: what is the difference?”: preferring “Not to be confused”
DIFFERENCE_RE = re.compile(
    r"^What(?: is| are|'s)? (?:the )?differences?|:\s*what(?: is| are|'s)? (?:the )?differences?", re.I
)

ID_RE = re.compile(r"<!--anki:([0-9a-f]+)-->")
META_RE = re.compile(r"<!--\s*(?:anki:|SR:|summary:).*?-->")
INLINE_META_RE = re.compile(r"\s*<!--\s*(?:anki:|SR:).*?-->")
NOT_CONTENT = ("#", "Tags:", "Verified on")

Line = tuple[int, str, bool]  # number, text, in a code block


class Card(NamedTuple):
    question: str
    answer: str
    line: int  # The separator line?
    guid: str | None = None


class TopicStats(NamedTuple):
    path: str
    cards: int
    scenarios: int
    confusions: int
    mean_words: int


@dataclass
class Report:
    """Errors (blockers) and warnings accumulated by controls."""

    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class Vault:
    """Text read only once, and records shared between card controls."""

    files: list[Path]
    texts: dict[Path, str]
    stale_months: int
    today: datetime.date = field(default_factory=datetime.date.today)
    names: collections.Counter[str] = field(init=False)
    guids: dict[str, str] = field(default_factory=dict)
    questions: collections.defaultdict[str, list[str]] = field(default_factory=lambda: collections.defaultdict(list))
    inbound: collections.Counter[str] = field(default_factory=collections.Counter)

    def __post_init__(self) -> None:
        self.names = collections.Counter([*(p.stem for p in self.files), MOC])

    def text(self, relative: str) -> str:
        return self.texts[ROOT / relative]


def markdown_lines(text: str) -> Iterator[Line]:
    """Numbered lines; the fences and their contents are not structural."""
    fence = None
    for number, line in enumerate(text.splitlines(), 1):
        marker = FENCE_RE.match(line)
        code = fence is not None or marker is not None
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = None
        elif marker:
            fence = marker[1]
        yield number, line, code


def topic_files() -> list[Path]:
    """Sheets of numbered sections, including container indexes, MOC excluded."""
    return sorted(p for p in ROOT.glob("[0-9]*/*.md") if p.stem != MOC and p.name != README)


def topic_title(text: str) -> str:
    """File title (first line), without "#" or the suffix "— Flashcards"."""
    return text.split("\n", 1)[0].strip().removeprefix("# ").removesuffix(" — Flashcards")


def connections(text: str) -> str | None:
    """Content of section ## Connections, None if missing."""
    return text.split("\n## Connections")[1] if "\n## Connections" in text else None


def decode_guid(hexa: str) -> str:
    """<!--anki:…--> (hexadecimal) ID → GUID Anki; ValueError if invalid."""
    try:
        guid = bytes.fromhex(hexa).decode("ascii")
    except UnicodeDecodeError as exc:
        raise ValueError("GUID non ASCII") from exc
    if not guid or any(ord(c) < 33 or ord(c) > 126 for c in guid):
        raise ValueError("Non-printable GUID")
    return guid


def retired_cards() -> list[Any]:
    """Cards removed from the vault: export republishes them with the removed tag to remove them from Anki."""
    path = ROOT / RETIRED
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []


def _is_content(line: str, code: bool) -> bool:
    return code or bool(line.strip() and not line.startswith(NOT_CONTENT) and not META_RE.fullmatch(line.strip()))


def parse_cards(text: str) -> tuple[list[Card], list[int]]:
    """Reads cards off code, before Sources/Connections, after a possible ## cards.

    Any content block must be a card. Indexes use ## Cards
    to explicitly distinguish their introduction from the content to be revised.
    Card.line is the separator line?. GUIDs are encoded in hexadecimal;
    the identifier is placed at the end of the question, and does not belong to its text.
    Returns cards and lines of poorly formed cards.
    """
    lines = list(markdown_lines(text))
    headers = [n for n, line, code in lines if not code and line == "## Cards"]
    start = headers[0] if headers else 0
    blocks: list[list[Line]] = []
    block: list[Line] = []
    for number, line, code in lines:
        if number <= start:
            continue
        if not code and END_OF_CARDS_RE.match(line):
            break
        if not code and line.strip() == "---":
            blocks.append(block)
            block = []
        else:
            block.append((number, line, code))
    blocks.append(block)
    cards: list[Card] = []
    malformed: list[int] = []
    for block in blocks:
        separators = [i for i, (_, line, code) in enumerate(block) if not code and line.strip() == "?"]
        payload = [number for number, line, code in block if _is_content(line, code)]
        if not payload:
            if any(not code and "<!--anki:" in line for _, line, code in block):
                malformed.append(block[0][0])
            continue
        if len(separators) != 1:
            malformed.append(payload[0])
            continue
        sep = separators[0]
        metadata = "\n".join(line for _, line, code in block if not code)
        ids = ID_RE.findall(metadata)
        guid = None
        try:
            if metadata.count("<!--anki:") != len(ids) or len(ids) > 1:
                raise ValueError("ill-formed or multiple identifier")
            if ids:
                guid = decode_guid(ids[0])
        except ValueError:
            malformed.append(block[sep][0])
            continue
        question = " ".join(line for _, line, code in block[:sep] if _is_content(line, code))
        question = INLINE_META_RE.sub("", question).strip()
        answer = "\n".join(
            line for _, line, code in block[sep + 1 :] if code or not META_RE.fullmatch(line.strip())
        ).strip()
        cards.append(Card(question, answer, block[sep][0], guid))
    return cards, malformed


def plugin_differences(text: str, cards: list[Card]) -> list[tuple[int | None, str]]:
    """Maps that the Spaced Repetition plugin reads other than the Anki export (see sr_plugin.py)."""

    def norm(t: str) -> str:
        return re.sub(r"\s+", " ", re.sub(r"<!--.*?-->", "", t, flags=re.S)).strip()

    seen: list[tuple[str | None, str]] = []
    for kind, card_text in sr_plugin.parse(text):
        stripped = [line.strip() for line in card_text.split("\n")]
        if kind != "multiline" or "?" not in stripped:
            seen.append((None, card_text))
            continue
        lines = card_text.split("\n")
        sep = stripped.index("?")
        seen.append((norm("\n".join(lines[:sep])), norm("\n".join(lines[sep + 1 :]))))
    problems: list[tuple[int | None, str]] = []
    for index, card in enumerate(cards):
        expected = (norm(card.question), norm(card.answer))
        got = seen[index] if index < len(seen) else None
        if got != expected:
            if got is None:
                problems.append((card.line, "missing card for the plugin"))
            elif got[0] is None:
                problems.append((card.line, f"the plugin reads a map of another type: {got[1][:50]!r}"))
            elif got[0] != expected[0]:
                problems.append((card.line, f"Question read by the plugin: {got[0][:60]!r}"))
            else:
                problems.append(
                    (
                        card.line,
                        f"Answer read by the plugin ({len(got[1].split())} mots Instead of {len(expected[1].split())})",
                    )
                )
            break  # the sequence is offset: only the first deviation is useful
    if not problems and len(seen) > len(cards):
        problems.append(
            (None, f"{len(seen) - len(cards)} Overlay card(s) for the plugin: {str(seen[len(cards)][1])[:50]!r}")
        )
    return problems


def words(answer: str) -> int:
    """Number of words in the response, excluding SR code blocks and metadata."""
    return len(re.sub(r"<!--SR:.*?-->", "", CODE_RE.sub("", answer)).split())


def list_items(answer: str) -> int:
    """Number of response list items, excluding code blocks."""
    return len(re.findall(r"^(?:- |\d+\. )", CODE_RE.sub("", answer), flags=re.M))


def parse_date(text: str) -> datetime.date | None:
    """Date "Verified on: 25 September 2026"; None if absent or invalid."""
    m = VERIFIED_RE.search(text)
    if not m or m.group(2) not in MONTHS:
        return None
    try:
        return datetime.date(int(m.group(3)), MONTHS.index(m.group(2)) + 1, int(m.group(1)))
    except ValueError:
        return None


def check_links(vault: Vault, report: Report) -> None:
    """Wikilinks and Markdown links from all pages, off code."""
    for path, text in vault.texts.items():
        rel = path.relative_to(ROOT)
        visible = "\n".join(line for _, line, code in markdown_lines(text) if not code)
        visible = INLINE_CODE_RE.sub("", visible)
        for target in dict.fromkeys(LINK_RE.findall(visible)):
            if target.strip() not in vault.names:
                report.errors.append(f"{rel} broken link: [[{target.strip()}]]")
        for target in MD_LINK_RE.findall(visible):
            if URL_SCHEME_RE.match(target) or target.startswith("#"):
                continue
            destination = unquote(target.split("#", 1)[0])
            if not (path.parent / destination).exists():
                report.errors.append(f"{rel} broken Markdown link: {target}")


def check_layout(rel: Path, text: str, report: Report) -> None:
    """Title on line 1, tags on line 2, no frontmatter."""
    lines = text.split("\n")
    if not lines[0].startswith("# "):
        report.errors.append(f"{rel}:1 missing title")
    if len(lines) < 2 or not lines[1].startswith("Tags:") or "#flashcards" not in lines[1]:
        report.errors.append(f"{rel}:2 line 2 must carry tags, including #flashcards")
    if text.startswith("---"):
        report.errors.append(f"{rel}:1 no frontmatter YAML")


def check_parsing(rel: Path, text: str, report: Report) -> list[Card]:
    """Well-formed cards, and read identically by the Spaced Repetition plugin."""
    cards, malformed = parse_cards(text)
    for number in malformed:
        report.errors.append(f"{rel}:{number} malformed card: separator? absent or multiple, or invalid ID")
    if not cards:
        report.errors.append(f"{rel} no valid cards")
    elif not malformed:
        for line, problem in plugin_differences(text, cards):
            where = f"{rel}:{line}" if line else str(rel)
            report.errors.append(f"{where} {problem} (HTML comment at the beginning of the line, or README settings?)")
    return cards


def check_sections(path: Path, rel: Path, text: str, report: Report) -> None:
    """Set-up and Connections present; Connections end with the MOC."""
    if path.stem not in INDEXES and "\n## Scenarios" not in text:
        report.errors.append(f"{rel} missing section: ## Scenarios")
    section = connections(text)
    if section is None:
        report.errors.append(f"{rel} missing section: ## Connections")
        return
    links = [line for line in section.strip().split("\n") if line.strip()]
    if not links or f"[[{MOC}" not in links[-1]:
        report.errors.append(f"{rel} the last link of the Connections must refer to the MOC")


def check_cards(path: Path, rel: Path, cards: list[Card], vault: Vault, report: Report) -> list[Card]:
    """Identifiers, questions and answers of each card; returns the scenarios."""
    scenarios = [c for c in cards if c.question.startswith("Scenario:")]
    if path.stem not in INDEXES and len(scenarios) < MIN_SCENARIOS:
        report.warnings.append(f"{rel} {len(scenarios)} scenario(s), {MIN_SCENARIOS} expected")
    for c in cards:
        vault.questions[c.question.lower()].append(str(rel))
        if not c.question:
            report.errors.append(f"{rel}:{c.line} empty question")
        if not c.guid:
            report.errors.append(f"{rel}:{c.line} missing Anki ID (scripts/assign_card_ids.py)")
        elif c.guid in vault.guids:
            report.errors.append(f"{rel}:{c.line} duplicate Anki ID with {vault.guids[c.guid]}")
        else:
            vault.guids[c.guid] = f"{rel}:{c.line}"
        if not c.answer:
            report.errors.append(f"{rel}:{c.line} Empty answer: {c.question[:60]}")
        scenario = c in scenarios
        limit = MAX_WORDS_SCENARIO if scenario else MAX_WORDS
        if words(c.answer) > limit:
            report.warnings.append(f"{rel}:{c.line} Answer has {words(c.answer)} words (> {limit}) : {c.question[:60]}")
        max_items = MAX_STEPS if scenario else MAX_ITEMS
        if list_items(c.answer) > max_items:
            report.warnings.append(
                f"{rel}:{c.line} List of {list_items(c.answer)} elements (> {max_items}) : {c.question[:60]}"
            )
        if DIFFERENCE_RE.search(c.question):
            report.warnings.append(f"{rel}:{c.line} prefer “Do not confuse: X and Y?”: {c.question[:60]}")
        if PRODUCT_LIST_RE.match(c.question):
            report.warnings.append(
                f'{rel}:{c.line} list of products, prefer "What tool for such a need?": {c.question[:60]}'
            )
        if OUT_OF_CONTEXT_RE.match(c.question):
            report.warnings.append(
                f"{rel}:{c.line} question is unclear outside its topic; name the subject: {c.question[:60]}"
            )
    return scenarios


def check_catalogs(path: Path, rel: Path, vault: Vault, report: Report) -> None:
    """Topic listed in the MOC (or container index) and the generated catalog."""
    moc, index = vault.text(f"{MOC}.md"), vault.text(CONTAINERS_INDEX)
    if path.stem not in INDEXES and f"[[{path.stem}" not in moc and f"[[{path.stem}" not in index:
        report.errors.append(f"{rel} missing the MOC (or container index)")
    if rel.as_posix() not in vault.text(CATALOG):
        report.warnings.append(f"{rel} missing from the topic catalog")


def check_dates(rel: Path, text: str, vault: Vault, report: Report) -> None:
    """Date "Verified the" legible, past, sourced, and not too old."""
    verified = parse_date(text)
    if "Verified on" in text and verified is None:
        report.errors.append(f'{rel} invalid "Verified on" date (format: 25 September 2026)')
    if not verified:
        return
    sources = SOURCES_RE.search(text)
    if not sources or not HTTPS_LINK_RE.search(sources[1]):
        report.errors.append(f'{rel} dated topic without an HTTPS reference in "## Sources"')
    if verified > vault.today:
        report.errors.append(f"{rel} “Verified” date in the future")
    if vault.stale_months and (vault.today - verified).days > vault.stale_months * 30.5:
        report.warnings.append(f"{rel} verified the {verified}Reconfronting the reality")


def check_topic(path: Path, vault: Vault, report: Report) -> TopicStats:
    """All controls specific to a record; returns its statistics."""
    rel = path.relative_to(ROOT)
    text = vault.texts[path]
    check_layout(rel, text, report)
    cards = check_parsing(rel, text, report)
    check_sections(path, rel, text, report)
    scenarios = check_cards(path, rel, cards, vault, report)
    for target in {target.strip() for target in LINK_RE.findall(text)}:
        if target in vault.names and target != path.stem:
            vault.inbound[target] += 1
    check_catalogs(path, rel, vault, report)
    check_dates(rel, text, vault, report)
    return TopicStats(
        str(rel),
        len(cards),
        len(scenarios),
        sum(c.question.startswith("Do not confuse") for c in cards),
        round(sum(words(c.answer) for c in cards) / max(1, len(cards))),
    )


def check_retired(vault: Vault, report: Report) -> None:
    """Valid, unique, and missing entries from retired_cards.json."""
    retired: set[str] = set()
    for entry in retired_cards():
        hexa = entry.get("id", "") if isinstance(entry, dict) else ""
        try:
            if not ID_RE.fullmatch(f"<!--anki:{hexa}-->") or not entry.get("question"):
                raise ValueError
            guid = decode_guid(hexa)
        except ValueError:
            report.errors.append(f"{RETIRED} malformed entry (hexadecimal id and required question): {entry}")
            continue
        if guid in retired:
            report.errors.append(f"{RETIRED} ID removed in duplicate: {hexa}")
        elif guid in vault.guids:
            report.errors.append(f"{vault.guids[guid]} ID removed in {RETIRED}, but the card is still in the vault")
        retired.add(guid)


def check_graph(vault: Vault, report: Report) -> None:
    """Questions in duplicate, Connections without a link in return and little linked files."""
    for question, where in vault.questions.items():
        if len(where) > 1:
            report.warnings.append(f"duplicate question ({', '.join(where)}) : {question[:60]}")
    by_stem = {p.stem: vault.texts[p] for p in vault.files}
    for stem, text in by_stem.items():
        section = connections(text)
        if stem in INDEXES or section is None:
            continue
        for target in dict.fromkeys(target.strip() for target in LINK_RE.findall(section)):
            if target in by_stem and target not in INDEXES and f"[[{stem}" not in by_stem[target]:
                report.warnings.append(f"{stem} cite {target} in his Connections, without a link in return")
    for p in vault.files:
        if vault.inbound[p.stem] < 2:
            report.warnings.append(
                f"{p.relative_to(ROOT)} Little connected: {vault.inbound[p.stem]} File(s) point to it"
            )


def lint(stale_months: int) -> tuple[list[str], list[str], list[TopicStats]]:
    """Errors, warnings and statistics per record; stale_months = 0 ignores the age of the dates."""
    files = topic_files()
    pages = [*ROOT.glob("[0-9]*/*.md"), *ROOT.glob("*.md"), *(ROOT / "docs").rglob("*.md")]
    vault = Vault(files, {p: p.read_text(encoding="utf-8") for p in pages}, stale_months)
    report = Report()
    for name, count in vault.names.items():
        if count > 1:
            report.errors.append(f"Duplicate filename in the vault: {name}")
    check_links(vault, report)
    stats = [check_topic(p, vault, report) for p in files]
    check_retired(vault, report)
    check_graph(vault, report)
    return report.errors, report.warnings, stats


def summary(stats: list[TopicStats]) -> dict[str, int]:
    """Vault totals displayed at the end of lint and in README."""
    return {
        "topics": len(stats),
        "cards": sum(s.cards for s in stats),
        "sections": len({s.path.split("/")[0] for s in stats}),
        "scenarios": sum(s.scenarios for s in stats),
        "confusions": sum(s.confusions for s in stats),
    }


def format_number(n: int) -> str:
    """Format a count with an English thousands separator: 2,186."""
    return f"{n:,}"


def update_readme(s: dict[str, int]) -> str:
    """Refresh the README statistics line and return it."""
    path = ROOT / README
    today = datetime.date.today()
    line = (
        f"**As of {today.day} {MONTHS[today.month - 1]} {today.year}**: {s['topics']} topics and "
        f"{format_number(s['cards'])} cards across {s['sections']} sections, including {s['scenarios']} "
        f"scenarios and {s['confusions']} do-not-confuse cards."
    )
    text, count = re.subn(r"^\*\*As of .*$", line, path.read_text(encoding="utf-8"), count=1, flags=re.M)
    if count:
        path.write_text(text, encoding="utf-8", newline="\n")
    return line


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stats", action="store_true", help="view statistics by file")
    ap.add_argument("--update-readme", action="store_true", help="Update the README status line")
    ap.add_argument("--stale-months", type=int, default=6, help='Maximum age of a "Verified on" (0: ignore)')
    ap.add_argument("--quiet", action="store_true", help="Show only errors")
    args = ap.parse_args()

    errors, warnings, stats = lint(args.stale_months)
    if args.stats:
        print(f"{'topic':60} cards scenarios confusions words/answer")
        for row in stats:
            print(f"{row.path:60} {row.cards:6} {row.scenarios:10} {row.confusions:10} {row.mean_words:11}")
        print()
    for e in errors:
        print(f"ERROR   {e}")
    if not args.quiet:
        for w in warnings:
            print(f"warning {w}")
    s = summary(stats)
    print(
        f"\n{s['topics']} topics, {s['cards']} cards, {s['scenarios']} scenarios, "
        f"{s['confusions']} do-not-confuse — {len(errors)} error(s), {len(warnings)} warning(s)"
    )
    if args.update_readme and not errors:
        print("README :", update_readme(s))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
