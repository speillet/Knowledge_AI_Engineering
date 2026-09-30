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
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MOC = "00-moc-ai-engineering"
INDEXES = {MOC, "00-index"}

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

Card = collections.namedtuple("Card", "question answer line")


def fiche_files():
    return sorted(p for p in ROOT.glob("[0-9]*/*.md") if p.stem != MOC)


def parse_cards(text):
    """Découpe le corps d'une fiche (avant ## Connexions) en cartes question/réponse."""
    body = text.split("\n## Connexions")[0]
    cards, malformed = [], []
    offset = 0
    for block in body.split("\n---\n"):
        start = body.count("\n", 0, offset) + 1
        offset += len(block) + 5
        parts = re.split(r"^\?$", block, flags=re.M)
        line = start + parts[0].rstrip("\n").count("\n")
        if len(parts) == 1:
            continue
        if len(parts) > 2:
            malformed.append(line)
            continue
        q_lines = [l for l in parts[0].split("\n")
                   if l.strip() and not l.startswith(("#", "Tags:", "Vérifié le"))]
        cards.append(Card(" ".join(q_lines).strip(), parts[1].strip(), line))
    return cards, malformed


def words(answer):
    return len(re.sub(r"<!--SR:.*?-->", "", CODE_RE.sub("", answer)).split())


def list_items(answer):
    return len(re.findall(r"^(?:- |\d+\. )", CODE_RE.sub("", answer), flags=re.M))


def parse_date(text):
    m = VERIFIE_RE.search(text)
    if not m or m.group(2) not in MOIS:
        return None
    return datetime.date(int(m.group(3)), MOIS.index(m.group(2)) + 1, int(m.group(1)))


def lint(stale_months):
    errors, warnings = [], []
    files = fiche_files()
    all_md = [p for p in ROOT.glob("**/*.md") if not any(s.startswith(".") for s in p.relative_to(ROOT).parts)]
    names = collections.Counter(p.stem for p in all_md)
    for n, c in names.items():
        if c > 1:
            errors.append(f"nom de fichier en double dans le vault : {n}")

    moc_text = (ROOT / f"{MOC}.md").read_text()
    index_text = (ROOT / "70-containers-infra/00-index.md").read_text()
    readme = (ROOT / "README.md").read_text()
    inbound = collections.Counter()
    questions = collections.defaultdict(list)
    stats = []
    today = datetime.date.today()

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
            errors.append(f"{rel}:{line} bloc avec plusieurs lignes « ? » (séparateur --- manquant ?)")

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
            if target not in names:
                errors.append(f"{rel} lien mort : [[{target}]]")
            elif target != p.stem:
                inbound[target] += 1

        if p.stem not in INDEXES and f"[[{p.stem}" not in moc_text and f"[[{p.stem}" not in index_text:
            errors.append(f"{rel} absente du MOC (ou de l'index conteneurs)")
        if str(rel) not in readme:
            warnings.append(f"{rel} absente de la liste « Concepts couverts » du README")

        verified = parse_date(text)
        if "Vérifié le" in text and verified is None:
            errors.append(f"{rel} date « Vérifié le » illisible (format : 25 septembre 2026)")
        if verified and stale_months and (today - verified).days > stale_months * 30.5:
            warnings.append(f"{rel} vérifiée le {verified}, à reconfronter à la réalité")

        stats.append((str(rel), len(cards), len(situations),
                      sum(c.question.startswith("À ne pas confondre") for c in cards),
                      round(sum(words(c.answer) for c in cards) / max(1, len(cards)))))

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
    if args.update_readme:
        print("README :", update_readme(s))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
