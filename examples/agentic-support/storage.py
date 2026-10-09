"""Registre métier pédagogique. Toutes les écritures critiques sont locales à SQLite."""
import hashlib
import json
import sqlite3
import time
import uuid


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def fingerprint(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


class Conflict(ValueError):
    pass


class Store:
    def __init__(self, path):
        self.db = sqlite3.connect(str(path), check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS orders (
                tenant TEXT, id TEXT, remaining INTEGER NOT NULL, version INTEGER NOT NULL,
                PRIMARY KEY (tenant, id));
            CREATE TABLE IF NOT EXISTS runs (
                id TEXT PRIMARY KEY, tenant TEXT NOT NULL, request_key TEXT NOT NULL,
                request TEXT NOT NULL, status TEXT NOT NULL,
                decision INTEGER, proposal_hash TEXT,
                UNIQUE (tenant, request_key));
            CREATE TABLE IF NOT EXISTS refunds (
                operation_id TEXT PRIMARY KEY, tenant TEXT NOT NULL,
                proposal TEXT NOT NULL, receipt TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS events (
                seq INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL,
                kind TEXT NOT NULL, payload TEXT NOT NULL);
        """)
        # Données fictives ; pas de réinitialisation d'une commande déjà traitée.
        with self.db:
            for tenant in ("alice", "bob"):
                self.db.execute("INSERT OR IGNORE INTO orders VALUES (?, 'commande-1', 10000, 1)", (tenant,))

    def close(self):
        self.db.close()

    def owned(self, run_id, tenant):
        row = self.db.execute("SELECT * FROM runs WHERE id=? AND tenant=?", (run_id, tenant)).fetchone()
        if row is None:
            raise KeyError("Dossier introuvable")
        return dict(row)

    def event(self, run_id, kind, payload):
        self.db.execute("INSERT INTO events(run_id,kind,payload) VALUES (?,?,?)", (run_id, kind, canonical(payload)))

    def create(self, tenant, key, request):
        encoded = canonical(request)
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            previous = self.db.execute("SELECT * FROM runs WHERE tenant=? AND request_key=?", (tenant, key)).fetchone()
            if previous:
                if previous["request"] != encoded:
                    raise Conflict("Même clé avec un contenu différent")
                return previous["id"]
            run_id = str(uuid.uuid4())
            self.db.execute("INSERT INTO runs(id,tenant,request_key,request,status) VALUES (?,?,?,?,?)", (run_id, tenant, key, encoded, "queued"))
            self.event(run_id, "accepted", {"status": "queued"})
            return run_id

    def status(self, run_id, status):
        with self.db:
            row = self.db.execute("SELECT status FROM runs WHERE id=?", (run_id,)).fetchone()
            if row["status"] != status:
                self.db.execute("UPDATE runs SET status=? WHERE id=?", (status, run_id))
                self.event(run_id, "status", {"status": status})

    def decide(self, run_id, tenant, digest, approved):
        self.owned(run_id, tenant)
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            row = self.db.execute("SELECT * FROM runs WHERE id=?", (run_id,)).fetchone()
            if row["decision"] is not None:
                if row["decision"] != int(approved) or row["proposal_hash"] != digest:
                    raise Conflict("Une décision différente est déjà enregistrée")
                return
            if row["status"] != "waiting":
                raise Conflict("Le dossier n'attend pas de décision")
            self.db.execute("UPDATE runs SET decision=?,proposal_hash=? WHERE id=?", (int(approved), digest, run_id))
            self.event(run_id, "decision", {"approved": approved, "proposal_hash": digest})

    def order(self, tenant, order_id):
        row = self.db.execute("SELECT remaining,version FROM orders WHERE tenant=? AND id=?", (tenant, order_id)).fetchone()
        if row is None:
            raise ValueError("Commande introuvable")
        return dict(row)

    def refund(self, run_id, tenant, proposal):
        """Effet ET déduplication dans une transaction du même service métier.

        Ce contrat serait à implémenter côté fournisseur si l'effet était distant.
        La transaction ne couvre pas les checkpoints LangGraph.
        """
        encoded = canonical(proposal)
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            previous = self.db.execute("SELECT * FROM refunds WHERE operation_id=?", (run_id,)).fetchone()
            if previous:
                if previous["tenant"] != tenant or previous["proposal"] != encoded:
                    raise Conflict("Identité d'opération réutilisée avec un autre contenu")
                return previous["receipt"]
            run = self.owned(run_id, tenant)
            if run["decision"] != 1 or run["proposal_hash"] != fingerprint(proposal):
                raise Conflict("Action non approuvée")
            if run["status"] == "cancelled" or proposal["expires_at"] <= time.time():
                raise Conflict("Proposition annulée ou expirée")
            order = self.order(tenant, proposal["order_id"])
            amount = proposal["amount_cents"]
            if type(amount) is not int or not 0 < amount <= order["remaining"]:
                raise Conflict("Montant invalide")
            if order["version"] != proposal["order_version"]:
                raise Conflict("Commande modifiée depuis la proposition")
            receipt = "avoir-" + run_id
            self.db.execute("UPDATE orders SET remaining=remaining-?,version=version+1 WHERE tenant=? AND id=?", (amount, tenant, proposal["order_id"]))
            self.db.execute("INSERT INTO refunds VALUES (?,?,?,?)", (run_id, tenant, encoded, receipt))
            self.event(run_id, "effect_committed", {"receipt": receipt, "amount_cents": amount})
            return receipt

    def events(self, run_id, tenant, after=0):
        self.owned(run_id, tenant)
        return [dict(row) for row in self.db.execute("SELECT seq,kind,payload FROM events WHERE run_id=? AND seq>? ORDER BY seq", (run_id, after))]
