#!/usr/bin/env python3
"""RAG deterministic workshop: lexical research, annotated facts and quotations.

python3 examples/verifiable-rag/rag_workshop.py --questions
python3 examples/verifiable-rag/rag_workshop.py
python3 examples/verifiable-rag/rag_workshop.py --case current --json /tmp/rag.json

No network calls, embedding or LLM. Structured facts replace extraction
and generation to isolate rights, versions, conflicts and evaluation of evidence.
The baseline is intentionally incorrect to serve as a counterexample.
"""

import argparse
from datetime import date
import hashlib
import json
from pathlib import Path
import re
import unicodedata

HERE = Path(__file__).resolve().parent
STOPWORDS = set(
    "a an and are as at be by for from in is it my of on or that the their this to was what when which with".split()
)


def load_fixture():
    corpus = json.loads((HERE / "corpus.json").read_text(encoding="utf-8"))
    cases = json.loads((HERE / "cases.json").read_text(encoding="utf-8"))
    return corpus, cases


def tokens(text):
    plain = "".join(char for char in unicodedata.normalize("NFD", text.lower()) if not unicodedata.combining(char))
    return set(re.findall(r"[a-z0-9]+", plain)) - STOPWORDS


def exclusion(document, principal, as_of):
    """Fictional politics: even holding AND at least one authorized group.

    The requested date determines the business validity; it does not restore
    past permissions and does not simulate the historical availability of the corpus.
    """
    if document["tenant"] != principal["tenant"] or not set(document["groups"]) & set(principal["groups"]):
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
    """Exact ranking by common distinct words; equalities by chunk_id.

    The score is neither BM25 nor a probability of relevance. Results
    of zero scores are excluded and the search may return fewer k passes.
    """
    if k < 1:
        raise ValueError("k must be strictly positive")
    query_tokens = tokens(query)
    ranked = [(len(query_tokens & tokens(doc["text"])), doc) for doc in documents]
    ranked = [(score, doc) for score, doc in ranked if score > 0]
    ranked.sort(key=lambda item: (-item[0], item[1]["chunk_id"]))
    return [doc for _, doc in ranked[:k]]


def answer(context, fields, resolve_conflicts=True):
    """Resolves only the recovered facts, without consulting the test answers.

    Authority is a fictitious business annotation, not an output of the model.
    A conflict at the maximum level of authority leads to abstention on the spot.
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
        claims.append(
            {"field": field, "value": evidence[0]["facts"][field], "citations": [doc["chunk_id"] for doc in evidence]}
        )
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
    """Controls each link on the exact annotations, without semantic judgment.

    A quote true to an allowable source of low authority can be
    supported while contradicting the expected response according to business policy.
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
        rows.append(
            {
                "field": claim["field"],
                "value": claim["value"],
                "supported": any(link["verdict"] == "supported" for link in links),
                "links": links,
            }
        )
    return rows


def evaluate(corpus, case, mode, k=4):
    if mode not in {"baseline", "filtered"}:
        raise ValueError("unknown mode")
    principal = corpus["principals"][case["principal"]]
    as_of = date.fromisoformat(case["as_of"])
    documents = corpus["documents"]
    candidates = (
        documents if mode == "baseline" else [doc for doc in documents if exclusion(doc, principal, as_of) is None]
    )
    context = retrieve(candidates, case["question"], k)
    response = answer(context, case["fields"], resolve_conflicts=mode == "filtered")
    audit = audit_claims(response, context, documents, principal, as_of)
    links = [link for row in audit for link in row["links"]]
    correct_supported = {
        row["field"] for row in audit if row["supported"] and case["expected"].get(row["field"]) == row["value"]
    }
    violations = [
        {"chunk_id": doc["chunk_id"], "reason": reason}
        for doc in context
        if (reason := exclusion(doc, principal, as_of))
    ]
    actual = {claim["field"]: claim["value"] for claim in response["claims"]}
    metrics = retrieval_metrics(context, case["relevant_chunks"])
    metrics.update(
        {
            "citation_support": (sum(link["verdict"] == "supported" for link in links) / len(links)) if links else None,
            "claim_support": sum(row["supported"] for row in audit) / len(audit) if audit else None,
            "expected_coverage": (len(correct_supported) / len(case["expected"])) if case["expected"] else None,
            "requested_coverage": len(correct_supported) / len(case["fields"]),
            "unexpected_claims": len(set(actual) - set(case["expected"])),
        }
    )
    passed = (
        response["status"] == case["expected_status"]
        and actual == case["expected"]
        and not violations
        and all(row["supported"] for row in audit)
        and all(link["verdict"] == "supported" for link in links)
    )
    return {
        "case_id": case["id"],
        "mode": mode,
        "principal": case["principal"],
        "tenant": principal["tenant"],
        "as_of": case["as_of"],
        "k": k,
        "context": [
            {"chunk_id": doc["chunk_id"], "document_id": doc["document_id"], "version": doc["version"]}
            for doc in context
        ],
        "response": response,
        "audit": audit,
        "violations": violations,
        "metrics": metrics,
        "passes_contract": passed,
    }


def make_report(corpus, cases, k=4):
    rows = [evaluate(corpus, case, mode, k) for case in cases for mode in ("baseline", "filtered")]
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
        payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    return {
        "snapshot": corpus["snapshot"],
        "fingerprints": {"corpus_sha256": fingerprint(corpus), "cases_sha256": fingerprint(cases)},
        "retriever": "lexical_overlap_v1",
        "policy": "tenant_group_validity_authority_v1",
        "summary": summary,
        "results": rows,
    }


def percent(value):
    return "n/a" if value is None else f"{value:.0%}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--questions", action="store_true", help="Show only the statements")
    parser.add_argument("--case", help="case identifier; all by default")
    parser.add_argument("--k", type=int, default=4, help="maximum number of passages recovered (default: 4)")
    parser.add_argument("--json", type=Path, help="Write the detailed report to the given path")
    args = parser.parse_args()
    if args.k < 1:
        parser.error("--k must be strictly positive")
    if args.questions and args.json:
        parser.error("--questions and --json incompatible")
    corpus, cases = load_fixture()
    if args.case:
        cases = [case for case in cases if case["id"] == args.case]
        if not cases:
            parser.error("unknown; see cases.json")
    print(f"Synthetic corpus: {corpus['snapshot']} ; lexical retrieval; no LLM.\n")
    if args.questions:
        for case in cases:
            principal = corpus["principals"][case["principal"]]
            print(
                f"{case['id']} — {case['principal']}, tenant {principal['tenant']}, "
                f"groups {', '.join(principal['groups'])}, date {case['as_of']}"
            )
            print(f"  {case['question']} Fields requested: {', '.join(case['fields'])}.")
        print("\nPredict permitted evidence, possible assertions, and abstentions.")
        return
    report = make_report(corpus, cases, args.k)
    for row in report["results"]:
        label = "OK" if row["passes_contract"] else "Failed"
        metrics = row["metrics"]
        print(
            f"{row['case_id']:18} {row['mode']:8} {row['response']['status']:8} {label:5} "
            f"recall={percent(metrics['recall_at_k'])} "
            f"support={percent(metrics['citation_support'])} "
            f"coverage={percent(metrics['expected_coverage'])}"
        )
        for claim in row["response"]["claims"]:
            print(f"  {claim['field']} = {claim['value']} [{', '.join(claim['citations'])}]")
        for missing in row["response"]["missing"]:
            print(f"  {missing['field']} : {missing['reason']}")
    print()
    for mode, summary in report["summary"].items():
        print(
            f"{mode} : {summary['passed']}/{summary['cases']} contracts respected, "
            f"{summary['context_violations']} Out of scope in context."
        )
    print("n/a: zero denominator; an abstention without quotation has no 100% support.")
    if args.json:
        try:
            args.json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        except OSError as exc:
            parser.error(str(exc))
        print(f"Report: {args.json}")


if __name__ == "__main__":
    main()
