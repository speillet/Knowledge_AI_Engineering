# Workshop: SQL for reliable data pipelines

Practice joins, null handling, deterministic versions and time-aware features on synthetic data in an in-memory SQLite database. Use Python 3.10 or newer with its standard `sqlite3` module. No packages, API keys or data files are required.

Before starting, read [analytical data modeling](../../150-data-compliance/150-010-analytical-data-modeling.md) and [analytical SQL](../../150-data-compliance/150-011-analytical-sql-transformations.md).

## Run

From the repository root:

```bash
python3 examples/data-engineering/sql_workshop.py
```

Expect **7 cases and 14 verified results**, each prefixed with `OK`. An assertion fails if a query returns a different result. The script creates no external service or data file.

## Predict the result first

Read the schema and queries in [sql_workshop.py](sql_workshop.py). For each case, write the expected rows and the invariant the query should preserve:

1. Join fan-out: compare the naive total of 720 with the order amount of 120; preaggregate at the correct grain.
2. Outer joins: explain why moving a filter from `ON` to `WHERE` drops customers without open tickets.
3. Nulls: compare counts and averages, then `NOT IN` with `NOT EXISTS`.
4. Versions: choose one row per key using a total ordering, including a tie-breaker.
5. Window frames: compare `ROWS` and `RANGE` when dates repeat.
6. Time-aware features: exclude a feature that was not yet available at decision time.
7. Replay and deletion: reject older events and preserve a versioned tombstone.

## Deliverable and completion criteria

Choose two cases. Explain the incorrect query, the violated invariant and the corrected result. Change one input in a working copy, predict its effect, and update the expected result only after checking the reasoning.

For the temporal case, explain why event time alone is insufficient; connect it to [time-aware data and features](../../150-data-compliance/159-temporal-data-features.md).

## Limits

These assertions validate the supplied SQL examples. They do not measure database performance or prove distributed execution, concurrent delivery or production recovery guarantees.

[All workshops](../README.md)
