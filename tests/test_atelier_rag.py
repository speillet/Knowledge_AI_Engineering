"""Régressions sur les preuves, les permissions et les dénominateurs de l'atelier."""

from copy import deepcopy
from datetime import date
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "examples/rag-verifiable/atelier_rag.py"
spec = importlib.util.spec_from_file_location("atelier_rag", SCRIPT)
rag = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rag)


class RagWorkshopTests(unittest.TestCase):
    def setUp(self):
        self.corpus, cases = rag.load_fixture()
        self.cases = {case["id"]: case for case in cases}
        self.docs = {doc["chunk_id"]: doc for doc in self.corpus["documents"]}
        self.alice = self.corpus["principals"]["alice"]
        self.today = date(2026, 10, 13)

    def test_supplied_cases_and_trace_respect_the_contract(self):
        self.assertEqual(len(self.cases), 10)
        self.assertEqual(len(self.docs), len(self.corpus["documents"]))
        report = rag.make_report(self.corpus, list(self.cases.values()))
        for row in report["results"]:
            with self.subTest(case=row["case_id"], mode=row["mode"]):
                self.assertEqual(row["passes_contract"], row["mode"] == "filtered")
                for ref in row["context"]:
                    self.assertEqual(ref["version"], self.docs[ref["chunk_id"]]["version"])
        self.assertEqual(report["summary"]["filtered"]["context_violations"], 0)
        self.assertEqual(report["summary"]["baseline"]["context_violations"], 20)

    def test_tenant_and_group_are_both_required(self):
        finance = self.docs["e-remise-finance"]
        orion = self.docs["f-orion-remboursement"]
        bruno = self.corpus["principals"]["bruno"]
        self.assertEqual(rag.exclusion(finance, self.alice, self.today), "unauthorized")
        self.assertIsNone(rag.exclusion(finance, bruno, self.today))
        self.assertEqual(rag.exclusion(orion, bruno, self.today), "unauthorized")
        revoked = deepcopy(bruno)
        revoked["groups"] = ["support"]
        self.assertEqual(rag.exclusion(finance, revoked, self.today), "unauthorized")
        # Une question historique ne rétablit pas le groupe finance révoqué.
        self.assertEqual(rag.exclusion(finance, revoked, date(2026, 9, 15)), "unauthorized")

    def test_effective_date_boundaries_and_withdrawal(self):
        old = self.docs["a-remboursement-v1"]
        current = self.docs["c-remboursement-v2"]
        future = self.docs["d-remboursement-v3"]
        for day, expected_old, expected_current, expected_future in (
            (date(2026, 9, 30), None, "not_yet_valid", "not_yet_valid"),
            (date(2026, 10, 1), "expired", None, "not_yet_valid"),
            (date(2026, 11, 1), "expired", "expired", None),
        ):
            with self.subTest(day=day):
                self.assertEqual(rag.exclusion(old, self.alice, day), expected_old)
                self.assertEqual(rag.exclusion(current, self.alice, day), expected_current)
                self.assertEqual(rag.exclusion(future, self.alice, day), expected_future)
        self.assertEqual(rag.exclusion(self.docs["i-promotion-retiree"], self.alice,
                                       self.today), "withdrawn")

    def test_filtering_after_global_top_k_loses_an_authorized_proof(self):
        # Les trois candidats interdits ont un meilleur score lexical.
        denied = []
        for index in range(3):
            doc = deepcopy(self.docs["e-remise-finance"])
            doc.update(chunk_id=f"denied-{index}", text="remboursement delai procedure")
            denied.append(doc)
        allowed = deepcopy(self.docs["c-remboursement-v2"])
        allowed["text"] = "remboursement"
        documents = denied + [allowed]
        query = "remboursement delai procedure"
        post_filtered = [doc for doc in rag.retrieve(documents, query, 3)
                         if rag.exclusion(doc, self.alice, self.today) is None]
        pre_filtered = rag.retrieve([doc for doc in documents
                                    if rag.exclusion(doc, self.alice, self.today) is None],
                                    query, 3)
        self.assertEqual(post_filtered, [])
        self.assertEqual([doc["chunk_id"] for doc in pre_filtered], [allowed["chunk_id"]])

    def test_changed_fact_changes_answer_and_fails_the_old_reference(self):
        before = rag.make_report(self.corpus, [self.cases["courant"]])
        self.docs["c-remboursement-v2"]["facts"]["refund_days"] = "60 jours"
        self.docs["c-remboursement-v2"]["text"] = self.docs["c-remboursement-v2"]["text"].replace(
            "30 jours", "60 jours")
        result = rag.evaluate(self.corpus, self.cases["courant"], "filtered")
        values = {claim["field"]: claim["value"] for claim in result["response"]["claims"]}
        self.assertEqual(values["refund_days"], "60 jours")
        self.assertFalse(result["passes_contract"])
        self.assertEqual(result["metrics"]["claim_support"], 1)
        self.assertEqual(result["metrics"]["expected_coverage"], 0.5)
        after = rag.make_report(self.corpus, [self.cases["courant"]])
        self.assertEqual(before["snapshot"], after["snapshot"])
        self.assertNotEqual(before["fingerprints"]["corpus_sha256"],
                            after["fingerprints"]["corpus_sha256"])
        self.assertEqual(before["fingerprints"]["cases_sha256"],
                         after["fingerprints"]["cases_sha256"])
        changed_cases = [deepcopy(self.cases["courant"])]
        changed_cases[0]["expected"]["refund_days"] = "60 jours"
        revised = rag.make_report(self.corpus, changed_cases)
        self.assertNotEqual(after["fingerprints"]["cases_sha256"],
                            revised["fingerprints"]["cases_sha256"])
        self.assertTrue(revised["results"][1]["passes_contract"])

    def test_removing_a_fact_causes_partial_answer_instead_of_invention(self):
        for doc in self.corpus["documents"]:
            doc["facts"].pop("refund_days", None)
        result = rag.evaluate(self.corpus, self.cases["courant"], "filtered")
        self.assertEqual(result["response"]["status"], "partial")
        self.assertEqual(result["response"]["missing"],
                         [{"field": "refund_days", "reason": "no_evidence"}])
        self.assertEqual([claim["field"] for claim in result["response"]["claims"]],
                         ["refund_method"])
        self.assertFalse(result["passes_contract"])

    def test_hidden_conflict_fails_despite_a_supported_citation(self):
        complete = rag.evaluate(self.corpus, self.cases["conflit"], "filtered", k=4)
        truncated = rag.evaluate(self.corpus, self.cases["conflit"], "filtered", k=1)
        self.assertEqual(complete["response"]["status"], "abstain")
        self.assertTrue(complete["passes_contract"])
        self.assertEqual(truncated["response"]["status"], "complete")
        self.assertEqual(truncated["metrics"]["citation_support"], 1)
        self.assertEqual(truncated["metrics"]["recall_at_k"], 0.5)
        self.assertFalse(truncated["passes_contract"])

    def test_faithfulness_to_faq_does_not_establish_business_correctness(self):
        faq = self.docs["b-faq-remboursement"]
        current = self.docs["c-remboursement-v2"]
        response = rag.answer([faq], ["refund_days"])
        audited = rag.audit_claims(response, [faq], self.corpus["documents"],
                                   self.alice, self.today)
        self.assertTrue(audited[0]["supported"])
        self.assertEqual(response["claims"][0]["value"], "14 jours")
        self.assertEqual(rag.answer([faq, current], ["refund_days"])["claims"][0]["value"],
                         "30 jours")

    def test_citation_audit_rejects_fabrication_wrong_fact_and_inaccessible_sources(self):
        context = [self.docs["c-remboursement-v2"]]
        for chunk, value, expected in (
            ("missing", "30 jours", "unknown_source"),
            ("c-remboursement-v2", "99 jours", "unsupported"),
            ("e-remise-finance", "45 %", "unauthorized"),
            ("a-remboursement-v1", "14 jours", "expired"),
            ("d-remboursement-v3", "45 jours", "not_yet_valid"),
            ("i-promotion-retiree", "50 %", "withdrawn"),
            ("b-faq-remboursement", "14 jours", "outside_context"),
            ("c-remboursement-v2", "30 jours", "supported"),
        ):
            with self.subTest(chunk=chunk, value=value):
                response = {"claims": [{"field": "refund_days", "value": value,
                                        "citations": [chunk, chunk]}]}
                audited = rag.audit_claims(response, context, self.corpus["documents"],
                                           self.alice, self.today)
                self.assertEqual(audited[0]["links"], [{"chunk_id": chunk, "verdict": expected}])
        uncited = rag.audit_claims({"claims": [{"field": "refund_days", "value": "30 jours",
                                                "citations": []}]}, context,
                                  self.corpus["documents"], self.alice, self.today)
        self.assertFalse(uncited[0]["supported"])

    def test_undefined_metrics_and_partial_coverage_have_distinct_denominators(self):
        empty = rag.retrieval_metrics([], [])
        self.assertTrue(all(value is None for value in empty.values()))
        missed = rag.retrieval_metrics([], ["c-remboursement-v2"])
        self.assertIsNone(missed["precision_returned"])
        self.assertEqual(missed["recall_at_k"], 0)
        self.assertEqual(missed["reciprocal_rank"], 0)
        no_proof = rag.evaluate(self.corpus, self.cases["sans-preuve"], "filtered")
        self.assertIsNone(no_proof["metrics"]["claim_support"])
        self.assertIsNone(no_proof["metrics"]["citation_support"])
        partial = rag.evaluate(self.corpus, self.cases["partiel"], "filtered")
        self.assertEqual(partial["metrics"]["expected_coverage"], 1)
        self.assertAlmostEqual(partial["metrics"]["requested_coverage"], 2 / 3)
        context = [self.docs["b-faq-remboursement"], self.docs["c-remboursement-v2"]]
        metrics = rag.retrieval_metrics(context + context, ["c-remboursement-v2"])
        self.assertEqual(metrics["precision_returned"], 0.5)
        self.assertEqual(metrics["reciprocal_rank"], 0.5)

    def test_cli_runs_outside_repo_hides_solutions_and_exports_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            def run(*args):
                return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=tmp,
                                      capture_output=True, text=True)
            questions = run("--questions")
            self.assertEqual(questions.returncode, 0, questions.stderr)
            self.assertNotIn("30 jours", questions.stdout)
            self.assertNotIn("contrats respectés", questions.stdout)
            path = Path(tmp) / "report.json"
            execution = run("--case", "courant", "--json", str(path))
            self.assertEqual(execution.returncode, 0, execution.stderr)
            report = json.loads(path.read_text())
            self.assertEqual(report["snapshot"], self.corpus["snapshot"])
            self.assertEqual(report["summary"]["filtered"]["passed"], 1)
            for arguments in (("--k", "0"), ("--case", "inconnu"),
                              ("--questions", "--json", str(path))):
                with self.subTest(arguments=arguments):
                    self.assertEqual(run(*arguments).returncode, 2)


if __name__ == "__main__":
    unittest.main()
