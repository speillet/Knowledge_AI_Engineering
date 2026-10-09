"""Trois dossiers synthétiques, y compris reprise après effet déjà validé."""
import json
import tempfile

from engine import Engine


def run_case(name, approved, inject_failure=False):
    with tempfile.TemporaryDirectory() as directory:
        engine = Engine(directory, fault="raise_after_effect" if inject_failure else None)
        try:
            run_id = engine.create("alice", name, {"order_id": "commande-1", "amount_cents": 2000})
            pending = engine.drive("alice", run_id)
            before = engine.store.db.execute("SELECT count(*) FROM refunds").fetchone()[0]
            if before != 0 or pending["status"] != "waiting":
                raise AssertionError("Effet avant approbation ou interruption absente")
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
                raise AssertionError("Résultat métier incorrect")
            return {"case": name, "status": result["status"], "effects": effects,
                    "business_invariants": "passed", "real_model_quality": "not_evaluated"}
        finally:
            engine.close()


if __name__ == "__main__":
    print(json.dumps([run_case("approbation", True), run_case("refus", False),
                      run_case("panne_apres_effet", True, True)], ensure_ascii=False, indent=2))
