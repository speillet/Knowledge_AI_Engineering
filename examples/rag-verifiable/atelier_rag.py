#!/usr/bin/env python3
"""Atelier RAG déterministe : recherche lexicale, faits annotés et citations.

python3 examples/rag-verifiable/atelier_rag.py --questions
python3 examples/rag-verifiable/atelier_rag.py
python3 examples/rag-verifiable/atelier_rag.py --case courant --json /tmp/rag.json

Aucun appel réseau, embedding ni LLM. Les faits structurés remplacent l'extraction
et la génération pour isoler droits, versions, conflits et évaluation des preuves.
La baseline est volontairement incorrecte pour servir de contre-exemple.
"""

import argparse
from datetime import date
import hashlib
import json
from pathlib import Path
import re
import unicodedata

HERE = Path(__file__).resolve().parent
STOPWORDS = set("a au aux ce cette de des du en est et la le les mon pour quel quelle "
                "quelles quels un une a cette date par avec d l".split())


def load_fixture():
    corpus = json.loads((HERE / "corpus.json").read_text(encoding="utf-8"))
    cases = json.loads((HERE / "cases.json").read_text(encoding="utf-8"))
    return corpus, cases


def tokens(text):
    plain = "".join(char for char in unicodedata.normalize("NFD", text.lower())
                    if not unicodedata.combining(char))
    return set(re.findall(r"[a-z0-9]+", plain)) - STOPWORDS


def exclusion(document, principal, as_of):
    """Politique fictive : même tenant ET au moins un groupe autorisé.

    La date demandée détermine la validité métier ; elle ne rétablit pas des
    permissions passées et ne simule pas la disponibilité historique du corpus.
    """
    if (document["tenant"] != principal["tenant"]
            or not set(document["groups"]) & set(principal["groups"])):
        return "unauthorized"
    if document["state"] != "active":
        return "withdrawn"
    if date.fromisoformat(document["valid_from"]) > as_of:
        return "not_yet_valid"
    end = document["valid_until"]
    if end is not None and as_of >= date.fromisoformat(end):
        return "expired"
    return None


def retrieve(documents, query, k):
    """Classement exact par mots distincts communs ; égalités par chunk_id.

    Le score n'est ni BM25, ni une probabilité de pertinence. Les résultats
    de score nul sont exclus et la recherche peut renvoyer moins de k passages.
    """
    if k < 1:
        raise ValueError("k doit être strictement positif")
    query_tokens = tokens(query)
    ranked = [(len(query_tokens & tokens(doc["text"])), doc) for doc in documents]
    ranked = [(score, doc) for score, doc in ranked if score > 0]
    ranked.sort(key=lambda item: (-item[0], item[1]["chunk_id"]))
    return [doc for _, doc in ranked[:k]]


def answer(context, fields, resolve_conflicts=True):
    """Résout uniquement les faits récupérés, sans consulter les réponses de test.

    L'autorité est une annotation métier fictive, pas une sortie du modèle.
    Un conflit au niveau d'autorité maximal entraîne l'abstention sur le champ.
    """
    claims, missing = [], []
    for field in fields:
        evidence = [doc for doc in context if field in doc["facts"]]
        if not evidence:
            missing.append({"field": field, "reason": "no_evidence"})
            continue
        if resolve_conflicts:
            authority = max(doc["authority"] for doc in evidence)
            evidence = [doc for doc in evidence if doc["authority"] == authority]
            if len({doc["facts"][field] for doc in evidence}) > 1:
                missing.append({"field": field, "reason": "conflict"})
                continue
        else:
            evidence = evidence[:1]
        claims.append({"field": field, "value": evidence[0]["facts"][field],
                       "citations": [doc["chunk_id"] for doc in evidence]})
    status = "abstain" if not claims else "partial" if missing else "complete"
    return {"status": status, "claims": claims, "missing": missing}


def retrieval_metrics(context, relevant_chunks):
    ids = list(dict.fromkeys(doc["chunk_id"] for doc in context))
    relevant = set(relevant_chunks)
    hits = relevant & set(ids)
    first = next((rank for rank, chunk in enumerate(ids, 1) if chunk in relevant), None)
    return {
        "precision_returned": len(hits) / len(ids) if ids else None,
        "recall_at_k": len(hits) / len(relevant) if relevant else None,
        "reciprocal_rank": (1 / first if first else 0.0) if relevant else None,
    }


def audit_claims(response, context, documents, principal, as_of):
    """Contrôle chaque lien sur les annotations exactes, sans jugement sémantique.

    Une citation fidèle à une source admissible de faible autorité peut être
    soutenue tout en contredisant la réponse attendue selon la politique métier.
    """
    by_id = {doc["chunk_id"]: doc for doc in documents}
    context_ids = {doc["chunk_id"] for doc in context}
    rows = []
    for claim in response["claims"]:
        links = []
        for chunk_id in dict.fromkeys(claim["citations"]):
            doc = by_id.get(chunk_id)
            if doc is None:
                verdict = "unknown_source"
            else:
                verdict = exclusion(doc, principal, as_of)
                if verdict is None:
                    if chunk_id not in context_ids:
                        verdict = "outside_context"
                    elif doc["facts"].get(claim["field"]) != claim["value"]:
                        verdict = "unsupported"
                    else:
                        verdict = "supported"
            links.append({"chunk_id": chunk_id, "verdict": verdict})
        rows.append({"field": claim["field"], "value": claim["value"],
                     "supported": any(link["verdict"] == "supported" for link in links),
                     "links": links})
    return rows


def evaluate(corpus, case, mode, k=4):
    if mode not in {"baseline", "filtered"}:
        raise ValueError("mode inconnu")
    principal = corpus["principals"][case["principal"]]
    as_of = date.fromisoformat(case["as_of"])
    documents = corpus["documents"]
    candidates = documents if mode == "baseline" else [
        doc for doc in documents if exclusion(doc, principal, as_of) is None]
    context = retrieve(candidates, case["question"], k)
    response = answer(context, case["fields"], resolve_conflicts=mode == "filtered")
    audit = audit_claims(response, context, documents, principal, as_of)
    links = [link for row in audit for link in row["links"]]
    correct_supported = {row["field"] for row in audit if row["supported"]
                         and case["expected"].get(row["field"]) == row["value"]}
    violations = [{"chunk_id": doc["chunk_id"], "reason": reason}
                  for doc in context if (reason := exclusion(doc, principal, as_of))]
    actual = {claim["field"]: claim["value"] for claim in response["claims"]}
    metrics = retrieval_metrics(context, case["relevant_chunks"])
    metrics.update({
        "citation_support": (sum(link["verdict"] == "supported" for link in links)
                             / len(links)) if links else None,
        "claim_support": sum(row["supported"] for row in audit) / len(audit) if audit else None,
        "expected_coverage": (len(correct_supported) / len(case["expected"]))
                             if case["expected"] else None,
        "requested_coverage": len(correct_supported) / len(case["fields"]),
        "unexpected_claims": len(set(actual) - set(case["expected"])),
    })
    passed = (response["status"] == case["expected_status"]
              and actual == case["expected"] and not violations
              and all(row["supported"] for row in audit)
              and all(link["verdict"] == "supported" for link in links))
    return {"case_id": case["id"], "mode": mode,
            "principal": case["principal"], "tenant": principal["tenant"],
            "as_of": case["as_of"], "k": k,
            "context": [{"chunk_id": doc["chunk_id"], "document_id": doc["document_id"],
                         "version": doc["version"]} for doc in context],
            "response": response, "audit": audit, "violations": violations,
            "metrics": metrics, "passes_contract": passed}


def make_report(corpus, cases, k=4):
    rows = [evaluate(corpus, case, mode, k) for case in cases
            for mode in ("baseline", "filtered")]
    summary = {}
    for mode in ("baseline", "filtered"):
        selected = [row for row in rows if row["mode"] == mode]
        summary[mode] = {
            "cases": len(selected),
            "passed": sum(row["passes_contract"] for row in selected),
            "abstentions": sum(row["response"]["status"] == "abstain" for row in selected),
            "context_violations": sum(len(row["violations"]) for row in selected),
        }
    def fingerprint(value):
        payload = json.dumps(value, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    return {"snapshot": corpus["snapshot"],
            "fingerprints": {"corpus_sha256": fingerprint(corpus),
                             "cases_sha256": fingerprint(cases)},
            "retriever": "lexical_overlap_v1",
            "policy": "tenant_group_validity_authority_v1", "summary": summary,
            "results": rows}


def percent(value):
    return "n/a" if value is None else f"{value:.0%}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--questions", action="store_true", help="afficher seulement les énoncés")
    parser.add_argument("--case", help="identifiant d'un cas ; tous par défaut")
    parser.add_argument("--k", type=int, default=4, help="maximum de passages récupérés (défaut : 4)")
    parser.add_argument("--json", type=Path, help="écrire le rapport détaillé au chemin donné")
    args = parser.parse_args()
    if args.k < 1:
        parser.error("--k doit être strictement positif")
    if args.questions and args.json:
        parser.error("--questions et --json sont incompatibles")
    corpus, cases = load_fixture()
    if args.case:
        cases = [case for case in cases if case["id"] == args.case]
        if not cases:
            parser.error("cas inconnu ; consulter cases.json")
    print(f"Corpus fictif : {corpus['snapshot']} ; recherche lexicale ; aucun LLM.\n")
    if args.questions:
        for case in cases:
            principal = corpus["principals"][case["principal"]]
            print(f"{case['id']} — {case['principal']}, tenant {principal['tenant']}, "
                  f"groupes {', '.join(principal['groups'])}, date {case['as_of']}")
            print(f"  {case['question']} Champs demandés : {', '.join(case['fields'])}.")
        print("\nPrédire les preuves autorisées, les affirmations possibles et les abstentions.")
        return
    report = make_report(corpus, cases, args.k)
    for row in report["results"]:
        label = "OK" if row["passes_contract"] else "ÉCHEC"
        metrics = row["metrics"]
        print(f"{row['case_id']:18} {row['mode']:8} {row['response']['status']:8} {label:5} "
              f"rappel={percent(metrics['recall_at_k'])} "
              f"soutien={percent(metrics['citation_support'])} "
              f"couverture={percent(metrics['expected_coverage'])}")
        for claim in row["response"]["claims"]:
            print(f"  {claim['field']} = {claim['value']} [{', '.join(claim['citations'])}]")
        for missing in row["response"]["missing"]:
            print(f"  {missing['field']} : {missing['reason']}")
    print()
    for mode, summary in report["summary"].items():
        print(f"{mode} : {summary['passed']}/{summary['cases']} contrats respectés, "
              f"{summary['context_violations']} passages hors périmètre dans le contexte.")
    print("n/a : dénominateur nul ; une abstention sans citation n'a pas 100 % de soutien.")
    if args.json:
        try:
            args.json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                                 encoding="utf-8")
        except OSError as exc:
            parser.error(str(exc))
        print(f"Rapport : {args.json}")


if __name__ == "__main__":
    main()
