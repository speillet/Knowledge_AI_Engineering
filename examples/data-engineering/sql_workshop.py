#!/usr/bin/env python3
"""Local workshop: python3 examples/data-engineering/sql_workshop.py.

SQLite in memory, standard library only, synthetic data.
Read each hypothesis and then predict the results before starting the workshop.
The assertions check for business results, not engine performance.
"""

import sqlite3


def verify(db, title, query, expected):
    actual = db.execute(query).fetchall()
    if actual != expected:
        raise AssertionError(f"{title}\nexpected: {expected}\nactual: {actual}")
    print(f"OK — {title} : {actual}")


def main():
    db = sqlite3.connect(":memory:")
    try:
        db.executescript("""
            CREATE TABLE orders (id INTEGER PRIMARY KEY, amount INTEGER);
            CREATE TABLE line_items (order_id INTEGER, line_id INTEGER);
            CREATE TABLE payments (order_id INTEGER, amount INTEGER);
            INSERT INTO orders VALUES (1, 120);
            INSERT INTO line_items VALUES (1, 1), (1, 2), (1, 3);
            INSERT INTO payments VALUES (1, 60), (1, 60);

            CREATE TABLE clients (id INTEGER PRIMARY KEY);
            CREATE TABLE tickets (id INTEGER, client_id INTEGER, status TEXT);
            INSERT INTO clients VALUES (1), (2), (3);
            INSERT INTO tickets VALUES (10, 1, 'open'), (20, 2, 'closed');

            CREATE TABLE measurements (value INTEGER);
            INSERT INTO measurements VALUES (10), (20), (NULL);
            CREATE TABLE source (id INTEGER NOT NULL);
            CREATE TABLE destination (id INTEGER);
            INSERT INTO source VALUES (1), (2);
            INSERT INTO destination VALUES (1), (NULL);

            CREATE TABLE changes (
                id INTEGER, value TEXT, version INTEGER NOT NULL,
                event_id INTEGER NOT NULL
            );
            INSERT INTO changes VALUES
                (1, 'old', 1, 1), (1, 'candidate', 2, 2),
                (1, 'selected', 2, 3), (2, 'unique', 1, 4);

            CREATE TABLE sales (id INTEGER, day TEXT, amount INTEGER);
            INSERT INTO sales VALUES
                (1, '2026-01-01', 10), (2, '2026-01-01', 20),
                (3, '2026-01-02', 5);

            CREATE TABLE decisions (
                decision_id INTEGER PRIMARY KEY, client_id INTEGER,
                decision_at TEXT NOT NULL
            );
            CREATE TABLE features (
                client_id INTEGER, version INTEGER,
                event_at TEXT NOT NULL, available_at TEXT NOT NULL,
                value INTEGER
            );
            INSERT INTO decisions VALUES
                (1, 1, '2026-01-01T10:05:00Z'),
                (2, 2, '2026-01-01T10:05:00Z'),
                (3, 1, '2026-01-01T10:12:00Z');
            INSERT INTO features VALUES
                (1, 1, '2026-01-01T09:50:00Z', '2026-01-01T09:51:00Z', 10),
                (1, 2, '2026-01-01T09:58:00Z', '2026-01-01T10:12:00Z', 99);

            CREATE TABLE state (
                id INTEGER PRIMARY KEY, version INTEGER NOT NULL,
                value TEXT, deleted INTEGER NOT NULL
            );
        """)

        # 1. A multiplicative join does not retain the order grain.
        verify(
            db,
            "Naive join: six lines and multiplied amount",
            """
            SELECT COUNT(*), SUM(c.amount)
            FROM orders c
            JOIN line_items l ON l.order_id = c.id
            JOIN payments p ON p.order_id = c.id
        """,
            [(6, 720)],
        )
        verify(
            db,
            "Grain Preaggregation Order",
            """
            WITH l AS (
                SELECT order_id, COUNT(*) AS nb FROM line_items GROUP BY order_id
            ), p AS (
                SELECT order_id, SUM(amount) AS paid
                FROM payments GROUP BY order_id
            )
            SELECT c.id, c.amount, l.nb, p.paid
            FROM orders c JOIN l ON l.order_id = c.id
            JOIN p ON p.order_id = c.id
        """,
            [(1, 120, 3, 120)],
        )

        # 2. The non-corresponding customer must remain present if the contract so requires.
        verify(
            db,
            "Filter in ON: retained customers",
            """
            SELECT c.id, t.id AS ticket_id
            FROM clients c
            LEFT JOIN tickets t
              ON t.client_id = c.id AND t.status = 'open'
            ORDER BY c.id
        """,
            [(1, 10), (2, None), (3, None)],
        )
        verify(
            db,
            "Filter in WHERE: customers without open ticket excluded",
            """
            SELECT c.id, t.id FROM clients c
            LEFT JOIN tickets t ON t.client_id = c.id
            WHERE t.status = 'open' ORDER BY c.id
        """,
            [(1, 10)],
        )

        # 3. NULL changes the denominator and the logic of the comparisons.
        verify(
            db,
            "Aggregates and average with/without imputation",
            """
            SELECT COUNT(*), COUNT(value), SUM(value), AVG(value),
                   AVG(COALESCE(value, 0)) FROM measurements
        """,
            [(3, 2, 30, 15.0, 10.0)],
        )
        verify(
            db,
            "NOT IN with NULL: no absentee raised",
            """
            SELECT id FROM source WHERE id NOT IN (SELECT id FROM destination)
        """,
            [],
        )
        verify(
            db,
            "NOT EXISTS: missing ID found",
            """
            SELECT s.id FROM source s
            WHERE NOT EXISTS (SELECT 1 FROM destination d WHERE d.id = s.id)
            ORDER BY s.id
        """,
            [(2,)],
        )

        # 4. event_id here provides an agreed-upon separation; it does not prove the truth.
        verify(
            db,
            "One version per key with total order",
            """
            WITH ranked AS (
                SELECT id, value, ROW_NUMBER() OVER (
                    PARTITION BY id ORDER BY version DESC, event_id DESC
                ) AS rn FROM changes
            )
            SELECT id, value FROM ranked WHERE rn = 1 ORDER BY id
        """,
            [(1, "selected"), (2, "unique")],
        )

        # 5. ROWS tracks positions; RANGE includes peers of the sort value.
        verify(
            db,
            "Cumuls ROWS and RANGE on equal dates",
            """
            SELECT id,
                SUM(amount) OVER (
                    ORDER BY day, id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ),
                SUM(amount) OVER (
                    ORDER BY day RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                )
            FROM sales ORDER BY id
        """,
            [(1, 10, 30), (2, 30, 30), (3, 35, 35)],
        )

        # 6. Full states, growing versions, without TTL; canonical UTC timestamps.
        # An availability exactly equal to the decision is allowed in this exercise.
        verify(
            db,
            "Time join: actual availability respected",
            """
            WITH candidates AS (
                SELECT d.decision_id, f.value, ROW_NUMBER() OVER (
                    PARTITION BY d.decision_id ORDER BY f.version DESC
                ) AS rn
                FROM decisions d LEFT JOIN features f
                  ON f.client_id = d.client_id
                 AND f.event_at <= d.decision_at
                 AND f.available_at <= d.decision_at
            )
            SELECT decision_id, value FROM candidates WHERE rn = 1 ORDER BY decision_id
        """,
            [(1, 10), (2, None), (3, 99)],
        )
        verify(
            db,
            "Business Date Only: Late Arrival Value Leak",
            """
            SELECT value FROM features
            WHERE client_id = 1 AND event_at <= '2026-01-01T10:05:00Z'
            ORDER BY version DESC LIMIT 1
        """,
            [(99,)],
        )

        # 7. Educational protocol of complete states; it is not a delta log.
        # Contradictory events of equal version must be reported upstream.
        upsert = """
            INSERT INTO state(id, version, value, deleted) VALUES (?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                version = excluded.version, value = excluded.value,
                deleted = excluded.deleted
            WHERE excluded.version > state.version
        """
        for event in [(1, 2, "current", 0), (1, 2, "current", 0), (1, 1, "old", 0)]:
            db.execute(upsert, event)
        verify(
            db,
            "Replay and old event without crushing",
            """
            SELECT id, version, value, deleted FROM state
        """,
            [(1, 2, "current", 0)],
        )
        db.execute(upsert, (1, 3, None, 1))
        db.execute(upsert, (1, 2, "current", 0))
        verify(
            db,
            "Tombstone Versioned: No Resurrection",
            """
            SELECT id, version, value, deleted FROM state
        """,
            [(1, 3, None, 1)],
        )
        verify(
            db,
            "Active view after deletion",
            """
            SELECT id FROM state WHERE deleted = 0
        """,
            [],
        )

        print("\n7 cases, 14 verified results. No external service or data file created.")
        print("This validates these local SQL examples, not a distributed system or its performance.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
