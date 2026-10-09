"""Invariants métier et pannes réelles ; aucun appel de modèle ni export distant."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage
from pydantic import ValidationError

from api import create_app
from engine import Engine
from storage import Conflict


REQUEST = {"order_id": "commande-1", "amount_cents": 2000}


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.engine = Engine(self.directory.name)

    def tearDown(self):
        self.engine.close()
        self.directory.cleanup()

    def pending(self, tenant="alice", key="requete-1"):
        run_id = self.engine.create(tenant, key, REQUEST)
        result = self.engine.drive(tenant, run_id)
        self.assertEqual(result["status"], "waiting")
        self.assertEqual(self.count_effects(), 0)
        return run_id, result["proposal_hash"]

    def count_effects(self):
        return self.engine.store.db.execute("SELECT count(*) FROM refunds").fetchone()[0]

    def reopen(self, fault=None):
        self.engine.close()
        self.engine = Engine(self.directory.name, fault=fault)

    def test_approval_survives_reconstruction_and_repetition(self):
        run_id, digest = self.pending()
        self.reopen()
        result = self.engine.decide("alice", run_id, digest, True)
        repeated = self.engine.decide("alice", run_id, digest, True)
        self.assertEqual(result, repeated)
        self.assertEqual(result["status"], "completed")
        self.assertEqual(self.count_effects(), 1)
        self.assertEqual(self.engine.store.order("alice", "commande-1")["remaining"], 8000)

    def test_refusal_has_no_effect_and_cannot_be_reversed(self):
        run_id, digest = self.pending()
        self.assertEqual(self.engine.decide("alice", run_id, digest, False)["status"], "rejected")
        with self.assertRaises(Conflict):
            self.engine.decide("alice", run_id, digest, True)
        self.assertEqual(self.count_effects(), 0)

    def test_idempotency_is_scoped_and_checks_content(self):
        run_id = self.engine.create("alice", "key", REQUEST)
        self.assertEqual(run_id, self.engine.create("alice", "key", REQUEST))
        self.assertNotEqual(run_id, self.engine.create("bob", "key", REQUEST))
        with self.assertRaises(Conflict):
            self.engine.create("alice", "key", {**REQUEST, "amount_cents": 3000})

    def test_other_tenant_cannot_read_resume_approve_cancel_or_read_events(self):
        run_id, digest = self.pending()
        actions = [lambda: self.engine.view("bob", run_id),
                   lambda: self.engine.drive("bob", run_id),
                   lambda: self.engine.decide("bob", run_id, digest, True),
                   lambda: self.engine.cancel("bob", run_id),
                   lambda: self.engine.store.events(run_id, "bob")]
        for action in actions:
            with self.subTest(action=action), self.assertRaises(KeyError):
                action()
        self.assertEqual(self.count_effects(), 0)

    def test_changed_proposal_hash_is_rejected(self):
        run_id, digest = self.pending()
        with self.assertRaises(Conflict):
            self.engine.decide("alice", run_id, "0" * 64, True)
        self.assertEqual(self.count_effects(), 0)

    def test_changed_business_version_blocks_effect(self):
        run_id, digest = self.pending()
        with self.engine.store.db:
            self.engine.store.db.execute("UPDATE orders SET version=version+1 WHERE tenant='alice'")
        with self.assertRaises(Conflict):
            self.engine.decide("alice", run_id, digest, True)
        self.assertEqual(self.count_effects(), 0)

    def test_expiration_blocks_effect(self):
        run_id, digest = self.pending()
        with patch("storage.time.time", return_value=10**12), self.assertRaises(Conflict):
            self.engine.decide("alice", run_id, digest, True)
        self.assertEqual(self.count_effects(), 0)

    def test_cancel_before_approval_blocks_effect(self):
        run_id, digest = self.pending()
        self.assertEqual(self.engine.cancel("alice", run_id)["status"], "cancelled")
        with self.assertRaises(Conflict):
            self.engine.decide("alice", run_id, digest, True)
        self.assertEqual(self.engine.drive("alice", run_id)["status"], "cancelled")
        self.assertEqual(self.count_effects(), 0)

    def test_exception_after_effect_does_not_duplicate_on_retry(self):
        run_id, digest = self.pending()
        self.engine.fault = "raise_after_effect"
        with self.assertRaises(RuntimeError):
            self.engine.decide("alice", run_id, digest, True)
        self.assertEqual(self.count_effects(), 1)
        with self.assertRaises(Conflict):
            self.engine.cancel("alice", run_id)
        self.reopen()
        self.assertEqual(self.engine.drive("alice", run_id)["status"], "completed")
        self.assertEqual(self.count_effects(), 1)

    def test_process_exit_after_effect_is_recovered(self):
        run_id, digest = self.pending()
        self.engine.close()
        # Le processus fils meurt après COMMIT métier et avant checkpoint.
        code = "from engine import Engine; import sys; e=Engine(sys.argv[1],fault='exit_after_effect'); e.decide('alice',sys.argv[2],sys.argv[3],True)"
        result = subprocess.run([sys.executable, "-c", code, self.directory.name, run_id, digest],
                                cwd=Path(__file__).parent, capture_output=True, text=True, timeout=30)
        self.engine = Engine(self.directory.name)
        self.assertEqual(result.returncode, 73, result.stderr)
        self.assertEqual(self.count_effects(), 1)
        self.assertEqual(self.engine.drive("alice", run_id)["status"], "completed")
        self.assertEqual(self.count_effects(), 1)

    def test_two_concurrent_identical_approvals_have_one_effect(self):
        run_id, digest = self.pending()
        barrier = threading.Barrier(2)
        def approve():
            barrier.wait(timeout=5)
            return self.engine.decide("alice", run_id, digest, True)
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(approve) for _ in range(2)]
            results = [f.result(timeout=15) for f in futures]
        self.assertEqual(results[0], results[1])
        self.assertEqual(self.count_effects(), 1)

    def test_business_service_rejects_unapproved_direct_call(self):
        run_id, digest = self.pending()
        proposal = self.engine.view("alice", run_id)["proposal"]
        with self.assertRaises(Conflict):
            self.engine.store.refund(run_id, "alice", proposal)
        self.assertEqual(self.count_effects(), 0)

    def test_invalid_model_output_never_reaches_approval_or_effect(self):
        run_id = self.engine.create("alice", "invalid-output", REQUEST)
        with patch("engine.GenericFakeChatModel.invoke", return_value=AIMessage(content='{"amount_cents": -1}')):
            with self.assertRaises(ValidationError):
                self.engine.drive("alice", run_id)
        self.assertEqual(self.engine.view("alice", run_id)["status"], "failed")
        self.assertEqual(self.count_effects(), 0)
        self.assertNotIn("proposal", self.engine.view("alice", run_id))

    def test_persisted_decision_survives_crash_before_resume(self):
        run_id, digest = self.pending()
        # État exact après COMMIT de la décision, avant Command(resume=...).
        self.engine.store.decide(run_id, "alice", digest, True)
        self.reopen()
        self.assertEqual(self.engine.drive("alice", run_id)["status"], "completed")
        self.assertEqual(self.count_effects(), 1)

    def test_contradictory_concurrent_decisions_have_one_winner(self):
        run_id, digest = self.pending()
        barrier = threading.Barrier(2)
        def decide(approved):
            barrier.wait(timeout=5)
            try:
                return self.engine.decide("alice", run_id, digest, approved)["status"]
            except Conflict:
                return "conflict"
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(decide, decision) for decision in (True, False)]
            results = [future.result(timeout=15) for future in futures]
        self.assertEqual(results.count("conflict"), 1)
        self.assertEqual(self.count_effects(), int("completed" in results))

    def test_local_langfuse_spans_have_expected_parentage(self):
        run_id, digest = self.pending()
        self.engine.decide("alice", run_id, digest, True)
        spans = self.engine.exporter.get_finished_spans()
        roots = [span for span in spans if span.name == "support-run"]
        self.assertEqual(len(roots), 2)
        root_ids = {span.context.span_id for span in roots}
        children = [span for span in spans if span.name != "support-run"]
        self.assertEqual({s.name for s in children}, {"read-order", "retrieve-policy", "propose-refund", "commit-refund"})
        self.assertTrue(all(s.parent and s.parent.span_id in root_ids for s in children))
        self.assertTrue(all(s.attributes.get("langfuse.observation.metadata.run_id") == run_id for s in roots))


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.app = create_app(self.directory.name)
        self.client = TestClient(self.app)
        self.client.__enter__()
        self.headers = {"Authorization": "Bearer alice-demo", "Idempotency-Key": "api-1"}

    def tearDown(self):
        self.client.__exit__(None, None, None)
        self.directory.cleanup()

    def test_end_to_end_api_and_event_replay(self):
        response = self.client.post("/runs", json=REQUEST, headers=self.headers)
        self.assertEqual(response.status_code, 200, response.text)
        run = response.json()
        self.assertEqual(run["status"], "waiting")
        prefix = f'/runs/{run["id"]}'
        first = self.client.get(prefix + "/events", headers=self.headers)
        self.assertEqual(first.status_code, 200)
        cursor = max(int(line[4:]) for line in first.text.splitlines() if line.startswith("id: "))
        decision = {"proposal_hash": run["proposal_hash"], "approved": True}
        self.assertEqual(self.client.post(prefix + "/decision", json=decision, headers=self.headers).json()["status"], "completed")
        second = self.client.get(prefix + "/events", headers={**self.headers, "Last-Event-ID": str(cursor)})
        self.assertIn("effect_committed", second.text)
        self.assertTrue(all(int(line[4:]) > cursor for line in second.text.splitlines() if line.startswith("id: ")))
        self.assertEqual(self.client.get(prefix, headers={"Authorization": "Bearer bob-demo"}).status_code, 404)
        self.assertEqual(self.client.post(prefix + "/decision", json=decision, headers=self.headers).status_code, 200)

    def test_api_rejects_missing_identity_bad_input_and_key_conflict(self):
        self.assertEqual(self.client.post("/runs", json=REQUEST).status_code, 401)
        self.assertEqual(self.client.post("/runs", json={**REQUEST, "tenant": "bob"}, headers=self.headers).status_code, 422)
        self.assertEqual(self.client.post("/runs", json={**REQUEST, "amount_cents": True}, headers=self.headers).status_code, 422)
        self.assertEqual(self.client.post("/runs", json=REQUEST, headers=self.headers).status_code, 200)
        self.assertEqual(self.client.post("/runs", json={**REQUEST, "amount_cents": 3000}, headers=self.headers).status_code, 409)


if __name__ == "__main__":
    unittest.main(verbosity=2)
