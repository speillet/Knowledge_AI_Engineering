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
import datetime
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
MOC = "00-moc-ai-engineering"
INDEXES = {MOC, "00-index"}
RETIRED = "scripts/retired_cards.json"

MAX_WORDS = 110          # carte standard, hors blocs de code
MAX_WORDS_SITUATION = 140
MIN_SITUATIONS = 2
MAX_ITEMS = 5            # au-delà, la liste se découpe en sous-cartes
MAX_STEPS = 6            # étapes d'une mise en situation

MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"]

LINK_RE = re.compile(r"\[\[([^\]|#]+)")
CODE_RE = re.compile(r"```.*?```", re.S)
VERIFIE_RE = re.compile(r"^Vérifié le : (\d{1,2}) (\w+) (\d{4})", re.M)

Card = collections.namedtuple("Card", "question answer line guid", defaults=[None])
ID_RE = re.compile(r"<!--anki:([0-9a-f]+)-->")
META_RE = re.compile(r"<!--\s*(?:anki:|SR:|summary:).*?-->")


def markdown_lines(text):
    """Lignes numérotées ; les fences et leur contenu ne sont pas structurels."""
    fence = None
    for number, line in enumerate(text.splitlines(), 1):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        code = fence is not None or marker is not None
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = None
        elif marker:
            fence = marker[1]
        yield number, line, code


def fiche_files():
    return sorted(p for p in ROOT.glob("[0-9]*/*.md") if p.stem != MOC)


def decode_guid(hexa):
    """Identifiant <!--anki:…--> (hexadécimal) → GUID Anki ; ValueError s'il est invalide."""
    try:
        guid = bytes.fromhex(hexa).decode("ascii")
    except UnicodeDecodeError as exc:
        raise ValueError("GUID non ASCII") from exc
    if not guid or any(ord(c) < 33 or ord(c) > 126 for c in guid):
        raise ValueError("GUID non imprimable")
    return guid


def retired_cards():
    """Cartes retirées du vault : l'export les republie avec le tag retired pour les supprimer d'Anki."""
    path = ROOT / RETIRED
    return json.loads(path.read_text()) if path.exists() else []


def parse_cards(text):
    """Lit les cartes hors code, avant Sources/Connexions, après un éventuel ## Cartes.

    Tout bloc de contenu doit être une carte. Les index utilisent ## Cartes
    pour distinguer explicitement leur introduction du contenu à réviser.
    Card.line est la ligne du séparateur ?. Les GUID sont encodés en hexadécimal.
    """
    lines = list(markdown_lines(text))
    headers = [n for n, line, code in lines if not code and line == "## Cartes"]
    start = headers[0] if headers else 0
    blocks, block = [], []
    for number, line, code in lines:
        if number <= start:
            continue
        if not code and re.match(r"^## (Sources|Connexions)\s*$", line):
            break
        if not code and line.strip() == "---":
            blocks.append(block)
            block = []
        else:
            block.append((number, line, code))
    blocks.append(block)
    cards, malformed = [], []
    for block in blocks:
        separators = [i for i, (_, line, code) in enumerate(block) if not code and line.strip() == "?"]
        payload = [(n, line) for n, line, code in block
                   if code or (line.strip() and not line.startswith(("#", "Tags:", "Vérifié le"))
                               and not META_RE.fullmatch(line.strip()))]
        if not payload:
            if any(not code and "<!--anki:" in line for _, line, code in block):
                malformed.append(block[0][0])
            continue
        if len(separators) != 1:
            malformed.append(payload[0][0])
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
        question = " ".join(line for _, line, code in block[:sep]
                            if code or (line.strip() and not line.startswith(("#", "Tags:", "Vérifié le"))
                                        and not META_RE.fullmatch(line.strip()))).strip()
        answer = "\n".join(line for _, line, code in block[sep + 1:]
                           if code or not META_RE.fullmatch(line.strip())).strip()
        cards.append(Card(question, answer, block[sep][0], guid))
    return cards, malformed


def words(answer):
    return len(re.sub(r"<!--SR:.*?-->", "", CODE_RE.sub("", answer)).split())


def list_items(answer):
    return len(re.findall(r"^(?:- |\d+\. )", CODE_RE.sub("", answer), flags=re.M))


def parse_date(text):
    m = VERIFIE_RE.search(text)
    if not m or m.group(2) not in MOIS:
        return None
    try:
        return datetime.date(int(m.group(3)), MOIS.index(m.group(2)) + 1, int(m.group(1)))
    except ValueError:
        return None


def lint(stale_months):
    errors, warnings = [], []
    files = fiche_files()
    all_md = files + [ROOT / f"{MOC}.md", ROOT / "README.md"]
    names = collections.Counter(p.stem for p in all_md)
    for n, c in names.items():
        if c > 1:
            errors.append(f"nom de fichier en double dans le vault : {n}")

    moc_text = (ROOT / f"{MOC}.md").read_text()
    index_text = (ROOT / "70-containers-infra/00-index.md").read_text()
    readme = (ROOT / "README.md").read_text()
    inbound = collections.Counter()
    questions = collections.defaultdict(list)
    guids = {}
    stats = []
    today = datetime.date.today()

    for p in all_md:
        visible = "\n".join(line for _, line, code in markdown_lines(p.read_text()) if not code)
        visible = re.sub(r"`+[^`]*`+", "", visible)
        for target in set(LINK_RE.findall(visible)):
            if target.strip() not in names:
                errors.append(f"{p.relative_to(ROOT)} lien mort : [[{target.strip()}]]")
        for target in re.findall(r"(?<!!)\[[^\]\n]*\]\(([^)\s]+)\)", visible):
            if re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("#"):
                continue
            destination = unquote(target.split("#", 1)[0])
            if not (p.parent / destination).exists():
                errors.append(f"{p.relative_to(ROOT)} lien Markdown mort : {target}")

    for p in files:
        rel = p.relative_to(ROOT)
        text = p.read_text()
        lines = text.split("\n")
        if not lines[0].startswith("# "):
            errors.append(f"{rel}:1 titre manquant")
        if len(lines) < 2 or not lines[1].startswith("Tags:") or "#flashcards" not in lines[1]:
            errors.append(f"{rel}:2 la ligne 2 doit porter les tags, dont #flashcards")
        if text.startswith("---"):
            errors.append(f"{rel}:1 pas de frontmatter YAML")

        cards, malformed = parse_cards(text)
        for line in malformed:
            errors.append(f"{rel}:{line} carte mal formée : séparateur ? absent ou multiple, ou identifiant invalide")
        if not cards:
            errors.append(f"{rel} aucune carte valide")

        if p.stem not in INDEXES and "\n## Mises en situation" not in text:
            errors.append(f"{rel} section « ## Mises en situation » manquante")
        if "\n## Connexions" not in text:
            errors.append(f"{rel} section « ## Connexions » manquante")
        else:
            conn = [l for l in text.split("\n## Connexions")[1].strip().split("\n") if l.strip()]
            if not conn or f"[[{MOC}" not in conn[-1]:
                errors.append(f"{rel} le dernier lien des Connexions doit renvoyer au MOC")

        situations = [c for c in cards if c.question.startswith("Mise en situation :")]
        if p.stem not in INDEXES and len(situations) < MIN_SITUATIONS:
            warnings.append(f"{rel} {len(situations)} mise(s) en situation, {MIN_SITUATIONS} attendues")
        for c in cards:
            questions[c.question.lower()].append(str(rel))
            if not c.question:
                errors.append(f"{rel}:{c.line} question vide")
            if not c.guid:
                errors.append(f"{rel}:{c.line} identifiant Anki absent (scripts/assign_card_ids.py)")
            elif c.guid in guids:
                errors.append(f"{rel}:{c.line} identifiant Anki en double avec {guids[c.guid]}")
            else:
                guids[c.guid] = f"{rel}:{c.line}"
            if not c.answer:
                errors.append(f"{rel}:{c.line} réponse vide : {c.question[:60]}")
            limit = MAX_WORDS_SITUATION if c in situations else MAX_WORDS
            if words(c.answer) > limit:
                warnings.append(f"{rel}:{c.line} réponse de {words(c.answer)} mots (> {limit}) : {c.question[:60]}")
            max_items = MAX_STEPS if c in situations else MAX_ITEMS
            if list_items(c.answer) > max_items:
                warnings.append(f"{rel}:{c.line} liste de {list_items(c.answer)} éléments (> {max_items}) : {c.question[:60]}")
            if re.match(r"Quelles? (est la )?différences?", c.question):
                warnings.append(f"{rel}:{c.line} préférer « À ne pas confondre : X et Y ? » : {c.question[:60]}")

        for target in set(LINK_RE.findall(text)):
            target = target.strip()
            if target in names and target != p.stem:
                inbound[target] += 1

        if p.stem not in INDEXES and f"[[{p.stem}" not in moc_text and f"[[{p.stem}" not in index_text:
            errors.append(f"{rel} absente du MOC (ou de l'index conteneurs)")
        if str(rel) not in readme:
            warnings.append(f"{rel} absente de la liste « Concepts couverts » du README")

        verified = parse_date(text)
        if "Vérifié le" in text and verified is None:
            errors.append(f"{rel} date « Vérifié le » illisible (format : 25 septembre 2026)")
        if verified:
            source_section = re.search(r"^## Sources\s*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
            if not source_section or not re.search(r"\[[^\]]+\]\(https://[^)]+\)", source_section[1]):
                errors.append(f"{rel} fiche datée sans référence HTTPS dans « ## Sources »")
        if verified and verified > today:
            errors.append(f"{rel} date « Vérifié le » dans le futur")
        if verified and stale_months and (today - verified).days > stale_months * 30.5:
            warnings.append(f"{rel} vérifiée le {verified}, à reconfronter à la réalité")

        stats.append((str(rel), len(cards), len(situations),
                      sum(c.question.startswith("À ne pas confondre") for c in cards),
                      round(sum(words(c.answer) for c in cards) / max(1, len(cards)))))

    retired = set()
    for entry in retired_cards():
        hexa = entry.get("id", "") if isinstance(entry, dict) else ""
        try:
            if not ID_RE.fullmatch(f"<!--anki:{hexa}-->") or not entry.get("question"):
                raise ValueError
            guid = decode_guid(hexa)
        except ValueError:
            errors.append(f"{RETIRED} entrée mal formée (id hexadécimal et question requis) : {entry}")
            continue
        if guid in retired:
            errors.append(f"{RETIRED} identifiant retiré en double : {hexa}")
        elif guid in guids:
            errors.append(f"{guids[guid]} identifiant retiré dans {RETIRED}, mais la carte est encore dans le vault")
        retired.add(guid)

    for q, where in questions.items():
        if len(where) > 1:
            warnings.append(f"question en double ({', '.join(where)}) : {q[:60]}")
    texts = {p.stem: p.read_text() for p in files}
    for stem, text in texts.items():
        if stem in INDEXES or "\n## Connexions" not in text:
            continue
        for target in set(LINK_RE.findall(text.split("\n## Connexions")[1])):
            target = target.strip()
            if target in texts and target not in INDEXES and f"[[{stem}" not in texts[target]:
                warnings.append(f"{stem} cite {target} dans ses Connexions, sans lien en retour")
    for p in files:
        if inbound[p.stem] < 2:
            warnings.append(f"{p.relative_to(ROOT)} peu reliée : {inbound[p.stem]} fiche(s) pointent vers elle")
    return errors, warnings, stats


def summary(stats):
    sections = {s[0].split("/")[0] for s in stats}
    return {
        "fiches": len(stats),
        "cartes": sum(s[1] for s in stats),
        "sections": len(sections),
        "situations": sum(s[2] for s in stats),
        "confusions": sum(s[3] for s in stats),
    }


def fr(n):
    return f"{n:,}".replace(",", " ")


def update_readme(s):
    path = ROOT / "README.md"
    today = datetime.date.today()
    line = (f"**État au {today.day} {MOIS[today.month - 1]} {today.year}** : {s['fiches']} fiches et "
            f"{fr(s['cartes'])} cartes, réparties en {s['sections']} sections, dont {s['situations']} "
            f"mises en situation et {s['confusions']} cartes « à ne pas confondre ».")
    text, n = re.subn(r"^\*\*État au .*$", line, path.read_text(), count=1, flags=re.M)
    if n:
        path.write_text(text)
    return line


def main():
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
            print(f"{row[0]:60} {row[1]:6} {row[2]:10} {row[3]:10} {row[4]:11}")
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
