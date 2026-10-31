#!/usr/bin/env python3
"""Vérifie les conventions des fiches de flashcards et calcule les statistiques du vault.

Usage :
    python3 scripts/lint_flashcards.py                  # vérifie, sortie non nulle en cas d'erreur
    python3 scripts/lint_flashcards.py --stats          # affiche aussi les stats par fiche
    python3 scripts/lint_flashcards.py --update-readme  # réécrit la ligne « État au … » du README
    python3 scripts/lint_flashcards.py --stale-months 6 # signale les « Vérifié le » plus vieux que 6 mois

Les erreurs cassent la révision ou la navigation (lien mort, carte mal formée…).
Les avertissements signalent un écart au guide de style (carte trop longue, fiche orpheline…).
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
CONTAINERS_INDEX = "70-containers-infra/00-index.md"
RETIRED = "scripts/retired_cards.json"

MAX_WORDS = 110          # carte standard, hors blocs de code
MAX_WORDS_SITUATION = 140
MIN_SITUATIONS = 2
MAX_ITEMS = 5            # au-delà, la liste se découpe en sous-cartes
MAX_STEPS = 6            # étapes d'une mise en situation

MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"]

LINK_RE = re.compile(r"\[\[([^\]|#]+)")
MD_LINK_RE = re.compile(r"(?<!!)\[[^\]\n]*\]\(([^)\s]+)\)")
URL_SCHEME_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9+.-]*:")
INLINE_CODE_RE = re.compile(r"`+[^`]*`+")
CODE_RE = re.compile(r"```.*?```", re.S)
FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
END_OF_CARDS_RE = re.compile(r"^## (Sources|Connexions)\s*$")
SOURCES_RE = re.compile(r"^## Sources\s*\n(.*?)(?=^## |\Z)", re.M | re.S)
HTTPS_LINK_RE = re.compile(r"\[[^\]]+\]\(https://[^)]+\)")
VERIFIE_RE = re.compile(r"^Vérifié le : (\d{1,2}) (\w+) (\d{4})", re.M)
# question qui ne se comprend qu'avec la carte précédente (« Et TGI ? », « Comment fonctionne-t-elle ? »)
HORS_CONTEXTE_RE = re.compile(r"^(Et\b|Comment \w+-t-(il|elle) ?\w* \?$|Que fait \w+ \?$)")
# liste de noms à réciter : préférer « Quel outil pour tel besoin ? »
LISTE_PRODUITS_RE = re.compile(
    r"^(Citez|Donnez des exemples|Quel(le)?s (outils|produits|alternatives|frameworks|serveurs|solutions|plateformes"
    r"|bibliothèques|benchmarks|services|offres)\b|.*\bconnaître \?$)")
# « Quelle différence entre X et Y ? » ou « X ou Y : quelle différence ? » : préférer « À ne pas confondre »
DIFFERENCE_RE = re.compile(r"^Quelles? (est la )?différences?|:\s*quelles? (est la )?différences?", re.I)

ID_RE = re.compile(r"<!--anki:([0-9a-f]+)-->")
META_RE = re.compile(r"<!--\s*(?:anki:|SR:|summary:).*?-->")
INLINE_META_RE = re.compile(r"\s*<!--\s*(?:anki:|SR:).*?-->")
NOT_CONTENT = ("#", "Tags:", "Vérifié le")

Line = tuple[int, str, bool]  # numéro, texte, dans un bloc de code


class Card(NamedTuple):
    question: str
    answer: str
    line: int  # ligne du séparateur ?
    guid: str | None = None


class FicheStats(NamedTuple):
    path: str
    cards: int
    situations: int
    confusions: int
    mean_words: int


@dataclass
class Report:
    """Erreurs (bloquantes) et avertissements accumulés par les contrôles."""
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class Vault:
    """Textes lus une seule fois, et registres partagés entre les contrôles des fiches."""
    files: list[Path]
    texts: dict[Path, str]
    stale_months: int
    today: datetime.date = field(default_factory=datetime.date.today)
    names: collections.Counter[str] = field(init=False)
    guids: dict[str, str] = field(default_factory=dict)
    questions: collections.defaultdict[str, list[str]] = field(
        default_factory=lambda: collections.defaultdict(list))
    inbound: collections.Counter[str] = field(default_factory=collections.Counter)

    def __post_init__(self) -> None:
        self.names = collections.Counter(p.stem for p in self.texts)

    def text(self, relative: str) -> str:
        return self.texts[ROOT / relative]


def markdown_lines(text: str) -> Iterator[Line]:
    """Lignes numérotées ; les fences et leur contenu ne sont pas structurels."""
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


def fiche_files() -> list[Path]:
    """Fiches des sections numérotées, index conteneurs compris, MOC exclu."""
    return sorted(p for p in ROOT.glob("[0-9]*/*.md") if p.stem != MOC)


def fiche_title(text: str) -> str:
    """Titre de la fiche (première ligne), sans « # » ni le suffixe « — Flashcards »."""
    return text.split("\n", 1)[0].strip().removeprefix("# ").removesuffix(" — Flashcards")


def connexions(text: str) -> str | None:
    """Contenu de la section ## Connexions, None si elle manque."""
    return text.split("\n## Connexions")[1] if "\n## Connexions" in text else None


def decode_guid(hexa: str) -> str:
    """Identifiant <!--anki:…--> (hexadécimal) → GUID Anki ; ValueError s'il est invalide."""
    try:
        guid = bytes.fromhex(hexa).decode("ascii")
    except UnicodeDecodeError as exc:
        raise ValueError("GUID non ASCII") from exc
    if not guid or any(ord(c) < 33 or ord(c) > 126 for c in guid):
        raise ValueError("GUID non imprimable")
    return guid


def retired_cards() -> list[Any]:
    """Cartes retirées du vault : l'export les republie avec le tag retired pour les supprimer d'Anki."""
    path = ROOT / RETIRED
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []


def _is_content(line: str, code: bool) -> bool:
    return code or bool(line.strip() and not line.startswith(NOT_CONTENT) and not META_RE.fullmatch(line.strip()))


def parse_cards(text: str) -> tuple[list[Card], list[int]]:
    """Lit les cartes hors code, avant Sources/Connexions, après un éventuel ## Cartes.

    Tout bloc de contenu doit être une carte. Les index utilisent ## Cartes
    pour distinguer explicitement leur introduction du contenu à réviser.
    Card.line est la ligne du séparateur ?. Les GUID sont encodés en hexadécimal ;
    l'identifiant se place en fin de question, et n'appartient pas à son texte.
    Renvoie les cartes et les lignes des cartes mal formées.
    """
    lines = list(markdown_lines(text))
    headers = [n for n, line, code in lines if not code and line == "## Cartes"]
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
                raise ValueError("identifiant mal formé ou multiple")
            if ids:
                guid = decode_guid(ids[0])
        except ValueError:
            malformed.append(block[sep][0])
            continue
        question = " ".join(line for _, line, code in block[:sep] if _is_content(line, code))
        question = INLINE_META_RE.sub("", question).strip()
        answer = "\n".join(line for _, line, code in block[sep + 1:]
                           if code or not META_RE.fullmatch(line.strip())).strip()
        cards.append(Card(question, answer, block[sep][0], guid))
    return cards, malformed


def plugin_differences(text: str, cards: list[Card]) -> list[tuple[int | None, str]]:
    """Cartes que le plugin Spaced Repetition lit autrement que l'export Anki (voir sr_plugin.py)."""
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
        seen.append((norm("\n".join(lines[:sep])), norm("\n".join(lines[sep + 1:]))))
    problems: list[tuple[int | None, str]] = []
    for index, card in enumerate(cards):
        expected = (norm(card.question), norm(card.answer))
        got = seen[index] if index < len(seen) else None
        if got != expected:
            if got is None:
                problems.append((card.line, "carte absente pour le plugin"))
            elif got[0] is None:
                problems.append((card.line, f"le plugin lit une carte d'un autre type : {got[1][:50]!r}"))
            elif got[0] != expected[0]:
                problems.append((card.line, f"question lue par le plugin : {got[0][:60]!r}"))
            else:
                problems.append((card.line, f"réponse lue par le plugin ({len(got[1].split())} mots "
                                            f"au lieu de {len(expected[1].split())})"))
            break  # la suite est décalée : seul le premier écart est utile
    if not problems and len(seen) > len(cards):
        problems.append((None, f"{len(seen) - len(cards)} carte(s) en trop pour le plugin : "
                               f"{str(seen[len(cards)][1])[:50]!r}"))
    return problems


def words(answer: str) -> int:
    """Nombre de mots de la réponse, hors blocs de code et métadonnées SR."""
    return len(re.sub(r"<!--SR:.*?-->", "", CODE_RE.sub("", answer)).split())


def list_items(answer: str) -> int:
    """Nombre d'éléments de liste de la réponse, hors blocs de code."""
    return len(re.findall(r"^(?:- |\d+\. )", CODE_RE.sub("", answer), flags=re.M))


def parse_date(text: str) -> datetime.date | None:
    """Date « Vérifié le : 25 septembre 2026 » ; None si absente ou invalide."""
    m = VERIFIE_RE.search(text)
    if not m or m.group(2) not in MOIS:
        return None
    try:
        return datetime.date(int(m.group(3)), MOIS.index(m.group(2)) + 1, int(m.group(1)))
    except ValueError:
        return None


def check_links(vault: Vault, report: Report) -> None:
    """Wikiliens et liens Markdown de toutes les pages, hors code."""
    for path, text in vault.texts.items():
        rel = path.relative_to(ROOT)
        visible = "\n".join(line for _, line, code in markdown_lines(text) if not code)
        visible = INLINE_CODE_RE.sub("", visible)
        for target in dict.fromkeys(LINK_RE.findall(visible)):
            if target.strip() not in vault.names:
                report.errors.append(f"{rel} lien mort : [[{target.strip()}]]")
        for target in MD_LINK_RE.findall(visible):
            if URL_SCHEME_RE.match(target) or target.startswith("#"):
                continue
            destination = unquote(target.split("#", 1)[0])
            if not (path.parent / destination).exists():
                report.errors.append(f"{rel} lien Markdown mort : {target}")


def check_layout(rel: Path, text: str, report: Report) -> None:
    """Titre en ligne 1, tags en ligne 2, pas de frontmatter."""
    lines = text.split("\n")
    if not lines[0].startswith("# "):
        report.errors.append(f"{rel}:1 titre manquant")
    if len(lines) < 2 or not lines[1].startswith("Tags:") or "#flashcards" not in lines[1]:
        report.errors.append(f"{rel}:2 la ligne 2 doit porter les tags, dont #flashcards")
    if text.startswith("---"):
        report.errors.append(f"{rel}:1 pas de frontmatter YAML")


def check_parsing(rel: Path, text: str, report: Report) -> list[Card]:
    """Cartes bien formées, et lues à l'identique par le plugin Spaced Repetition."""
    cards, malformed = parse_cards(text)
    for number in malformed:
        report.errors.append(f"{rel}:{number} carte mal formée : séparateur ? absent ou multiple, "
                             "ou identifiant invalide")
    if not cards:
        report.errors.append(f"{rel} aucune carte valide")
    elif not malformed:
        for line, problem in plugin_differences(text, cards):
            where = f"{rel}:{line}" if line else str(rel)
            report.errors.append(f"{where} {problem} (commentaire HTML en début de ligne, ou réglages du README ?)")
    return cards


def check_sections(path: Path, rel: Path, text: str, report: Report) -> None:
    """Mises en situation et Connexions présentes ; les Connexions finissent par le MOC."""
    if path.stem not in INDEXES and "\n## Mises en situation" not in text:
        report.errors.append(f"{rel} section « ## Mises en situation » manquante")
    section = connexions(text)
    if section is None:
        report.errors.append(f"{rel} section « ## Connexions » manquante")
        return
    links = [line for line in section.strip().split("\n") if line.strip()]
    if not links or f"[[{MOC}" not in links[-1]:
        report.errors.append(f"{rel} le dernier lien des Connexions doit renvoyer au MOC")


def check_cards(path: Path, rel: Path, cards: list[Card], vault: Vault, report: Report) -> list[Card]:
    """Identifiants, questions et réponses de chaque carte ; renvoie les mises en situation."""
    situations = [c for c in cards if c.question.startswith("Mise en situation :")]
    if path.stem not in INDEXES and len(situations) < MIN_SITUATIONS:
        report.warnings.append(f"{rel} {len(situations)} mise(s) en situation, {MIN_SITUATIONS} attendues")
    for c in cards:
        vault.questions[c.question.lower()].append(str(rel))
        if not c.question:
            report.errors.append(f"{rel}:{c.line} question vide")
        if not c.guid:
            report.errors.append(f"{rel}:{c.line} identifiant Anki absent (scripts/assign_card_ids.py)")
        elif c.guid in vault.guids:
            report.errors.append(f"{rel}:{c.line} identifiant Anki en double avec {vault.guids[c.guid]}")
        else:
            vault.guids[c.guid] = f"{rel}:{c.line}"
        if not c.answer:
            report.errors.append(f"{rel}:{c.line} réponse vide : {c.question[:60]}")
        situation = c in situations
        limit = MAX_WORDS_SITUATION if situation else MAX_WORDS
        if words(c.answer) > limit:
            report.warnings.append(f"{rel}:{c.line} réponse de {words(c.answer)} mots (> {limit}) : {c.question[:60]}")
        max_items = MAX_STEPS if situation else MAX_ITEMS
        if list_items(c.answer) > max_items:
            report.warnings.append(f"{rel}:{c.line} liste de {list_items(c.answer)} éléments (> {max_items}) : "
                                   f"{c.question[:60]}")
        if DIFFERENCE_RE.search(c.question):
            report.warnings.append(f"{rel}:{c.line} préférer « À ne pas confondre : X et Y ? » : {c.question[:60]}")
        if LISTE_PRODUITS_RE.match(c.question):
            report.warnings.append(f"{rel}:{c.line} liste de produits, préférer « Quel outil pour tel besoin ? » : "
                                   f"{c.question[:60]}")
        if HORS_CONTEXTE_RE.match(c.question):
            report.warnings.append(f"{rel}:{c.line} question incompréhensible hors de la fiche, nommer le sujet : "
                                   f"{c.question[:60]}")
    return situations


def check_catalogs(path: Path, rel: Path, vault: Vault, report: Report) -> None:
    """Fiche citée par le MOC (ou l'index conteneurs) et par le README."""
    moc, index = vault.text(f"{MOC}.md"), vault.text(CONTAINERS_INDEX)
    if path.stem not in INDEXES and f"[[{path.stem}" not in moc and f"[[{path.stem}" not in index:
        report.errors.append(f"{rel} absente du MOC (ou de l'index conteneurs)")
    if str(rel) not in vault.text(README):
        report.warnings.append(f"{rel} absente de la liste « Concepts couverts » du README")


def check_dates(rel: Path, text: str, vault: Vault, report: Report) -> None:
    """Date « Vérifié le » lisible, passée, sourcée, et pas trop ancienne."""
    verified = parse_date(text)
    if "Vérifié le" in text and verified is None:
        report.errors.append(f"{rel} date « Vérifié le » illisible (format : 25 septembre 2026)")
    if not verified:
        return
    sources = SOURCES_RE.search(text)
    if not sources or not HTTPS_LINK_RE.search(sources[1]):
        report.errors.append(f"{rel} fiche datée sans référence HTTPS dans « ## Sources »")
    if verified > vault.today:
        report.errors.append(f"{rel} date « Vérifié le » dans le futur")
    if vault.stale_months and (vault.today - verified).days > vault.stale_months * 30.5:
        report.warnings.append(f"{rel} vérifiée le {verified}, à reconfronter à la réalité")


def check_fiche(path: Path, vault: Vault, report: Report) -> FicheStats:
    """Tous les contrôles propres à une fiche ; renvoie ses statistiques."""
    rel = path.relative_to(ROOT)
    text = vault.texts[path]
    check_layout(rel, text, report)
    cards = check_parsing(rel, text, report)
    check_sections(path, rel, text, report)
    situations = check_cards(path, rel, cards, vault, report)
    for target in {target.strip() for target in LINK_RE.findall(text)}:
        if target in vault.names and target != path.stem:
            vault.inbound[target] += 1
    check_catalogs(path, rel, vault, report)
    check_dates(rel, text, vault, report)
    return FicheStats(str(rel), len(cards), len(situations),
                      sum(c.question.startswith("À ne pas confondre") for c in cards),
                      round(sum(words(c.answer) for c in cards) / max(1, len(cards))))


def check_retired(vault: Vault, report: Report) -> None:
    """Entrées de retired_cards.json valides, uniques et absentes du vault."""
    retired: set[str] = set()
    for entry in retired_cards():
        hexa = entry.get("id", "") if isinstance(entry, dict) else ""
        try:
            if not ID_RE.fullmatch(f"<!--anki:{hexa}-->") or not entry.get("question"):
                raise ValueError
            guid = decode_guid(hexa)
        except ValueError:
            report.errors.append(f"{RETIRED} entrée mal formée (id hexadécimal et question requis) : {entry}")
            continue
        if guid in retired:
            report.errors.append(f"{RETIRED} identifiant retiré en double : {hexa}")
        elif guid in vault.guids:
            report.errors.append(f"{vault.guids[guid]} identifiant retiré dans {RETIRED}, "
                                 "mais la carte est encore dans le vault")
        retired.add(guid)


def check_graph(vault: Vault, report: Report) -> None:
    """Questions en double, Connexions sans lien en retour et fiches peu reliées."""
    for question, where in vault.questions.items():
        if len(where) > 1:
            report.warnings.append(f"question en double ({', '.join(where)}) : {question[:60]}")
    by_stem = {p.stem: vault.texts[p] for p in vault.files}
    for stem, text in by_stem.items():
        section = connexions(text)
        if stem in INDEXES or section is None:
            continue
        for target in dict.fromkeys(target.strip() for target in LINK_RE.findall(section)):
            if target in by_stem and target not in INDEXES and f"[[{stem}" not in by_stem[target]:
                report.warnings.append(f"{stem} cite {target} dans ses Connexions, sans lien en retour")
    for p in vault.files:
        if vault.inbound[p.stem] < 2:
            report.warnings.append(f"{p.relative_to(ROOT)} peu reliée : "
                                   f"{vault.inbound[p.stem]} fiche(s) pointent vers elle")


def lint(stale_months: int) -> tuple[list[str], list[str], list[FicheStats]]:
    """Erreurs, avertissements et statistiques par fiche ; stale_months = 0 ignore l'ancienneté des dates."""
    files = fiche_files()
    pages = [*files, ROOT / f"{MOC}.md", ROOT / README]
    vault = Vault(files, {p: p.read_text(encoding="utf-8") for p in pages}, stale_months)
    report = Report()
    for name, count in vault.names.items():
        if count > 1:
            report.errors.append(f"nom de fichier en double dans le vault : {name}")
    check_links(vault, report)
    stats = [check_fiche(p, vault, report) for p in files]
    check_retired(vault, report)
    check_graph(vault, report)
    return report.errors, report.warnings, stats


def summary(stats: list[FicheStats]) -> dict[str, int]:
    """Totaux du vault affichés en fin de lint et dans le README."""
    return {
        "fiches": len(stats),
        "cartes": sum(s.cards for s in stats),
        "sections": len({s.path.split("/")[0] for s in stats}),
        "situations": sum(s.situations for s in stats),
        "confusions": sum(s.confusions for s in stats),
    }


def fr(n: int) -> str:
    """Nombre avec séparateur de milliers français : 2 186."""
    return f"{n:,}".replace(",", " ")


def update_readme(s: dict[str, int]) -> str:
    """Réécrit la ligne « État au … » du README ; renvoie la nouvelle ligne."""
    path = ROOT / README
    today = datetime.date.today()
    line = (f"**État au {today.day} {MOIS[today.month - 1]} {today.year}** : {s['fiches']} fiches et "
            f"{fr(s['cartes'])} cartes, réparties en {s['sections']} sections, dont {s['situations']} "
            f"mises en situation et {s['confusions']} cartes « à ne pas confondre ».")
    text, n = re.subn(r"^\*\*État au .*$", line, path.read_text(encoding="utf-8"), count=1, flags=re.M)
    if n:
        path.write_text(text, encoding="utf-8", newline="\n")
    return line


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stats", action="store_true", help="afficher les statistiques par fiche")
    ap.add_argument("--update-readme", action="store_true", help="mettre à jour la ligne d'état du README")
    ap.add_argument("--stale-months", type=int, default=6, help="ancienneté maximale d'un « Vérifié le » (0 : ignorer)")
    ap.add_argument("--quiet", action="store_true", help="n'afficher que les erreurs")
    args = ap.parse_args()

    errors, warnings, stats = lint(args.stale_months)
    if args.stats:
        print(f"{'fiche':60} cartes situations confusions mots/réponse")
        for row in stats:
            print(f"{row.path:60} {row.cards:6} {row.situations:10} {row.confusions:10} {row.mean_words:11}")
        print()
    for e in errors:
        print(f"ERREUR  {e}")
    if not args.quiet:
        for w in warnings:
            print(f"attention {w}")
    s = summary(stats)
    print(f"\n{s['fiches']} fiches, {s['cartes']} cartes, {s['situations']} mises en situation, "
          f"{s['confusions']} « à ne pas confondre » — {len(errors)} erreur(s), {len(warnings)} avertissement(s)")
    if args.update_readme and not errors:
        print("README :", update_readme(s))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
