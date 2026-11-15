"""Three synthetic files, including recovery after already validated effect."""

import json
import tempfile

from engine import Engine


def run_case(name, approved, inject_failure=False):
    with tempfile.TemporaryDirectory() as directory:
        engine = Engine(directory, fault="raise_after_effect" if inject_failure else None)
        try:
            run_id = engine.create("alice", name, {"order_id": "order-1", "amount_cents": 2000})
            pending = engine.drive("alice", run_id)
            before = engine.store.db.execute("SELECT count(*) FROM refunds").fetchone()[0]
            if before != 0 or pending["status"] != "waiting":
                raise AssertionError("Effect before approval or interruption absent")
            try:
                result = engine.decide("alice", run_id, pending["proposal_hash"], approved)
            except RuntimeError:
                if not inject_failure:
                    raise
                engine.close()
                engine = Engine(directory)
                result = engine.drive("alice", run_id)
            effects = engine.store.db.execute("SELECT count(*) FROM refunds").fetchone()[0]
            expected = "completed" if approved else "rejected"
            if result["status"] != expected or effects != int(approved):
                raise AssertionError("Incorrect business result")
            return {
                "case": name,
                "status": result["status"],
                "effects": effects,
                "business_invariants": "passed",
                "real_model_quality": "not_evaluated",
            }
        finally:
            engine.close()


if __name__ == "__main__":
    print(
        json.dumps(
            [run_case("approval", True), run_case("declined", False), run_case("crash_after_side_effect", True, True)],
            ensure_ascii=False,
            indent=2,
        )
    )
