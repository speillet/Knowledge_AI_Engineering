# SQL for AI pipelines & datasets — Flashcards
Tags: #flashcards #ai-engineering #data #data-engineering
Verified on: 9 October 2026 — technical references and examples of this file.
<!-- summary: joins and filters, null, aggregations, windows, deterministic deduplication, anti-joins, CTE, time SQL, query plans and transformation controls, deterministic deduplication and equalities, ROWS and RANGE windows, join filter. -->


In what logical order to reason on an analytical SQL query? <!--anki:3638393465633964663639633434613639363865613739346437383030623434-->
?
Reason on **FROM and JOIN**, then `WHERE`, aggregations and `HAVING`, then windows and projection, finally sorting and limiting. This conceptual order explains which rows and columns are available at each step; the optimizer can use another equivalent physical order.

A `WHERE` filter removes rows before an average; `HAVING` filters groups after aggregation, so a window function does not see rows already excluded. Breaking the query down into steps helps to understand why a dataset loses observations or changes denominator.

---

Why can a WHERE filter on the right table change the direction of a LEFT JOIN? <!--anki:3264633139653733613066663461666639323533666230303465336132353434-->
?
Unmatched lines receive `NULL`s on the right. `WHERE t.status = 'open'` excludes them, because the comparison is not true for `NULL`.
```sql
SELECT c.id, t.id AS ticket_id
FROM clients c
LEFT JOIN tickets t
  ON t.client_id = c.id AND t.status = 'open';
```
This criterion in `ON` keeps customers without an open ticket. Test a customer without a ticket, one with a closed ticket and one with two open: the result has four lines, two with a zero ticket.

A `WHERE ... OR t.id IS NULL` variant is not enough: the customer with only a closed ticket has a match, then eliminated. Respect the expected grain.

---

Why doesn't a SQL to NULL column compare with = test its absence? <!--anki:3032646563643533396361643461633238393565326466343464363936373637-->
?
SQL uses a **The Logic of Three Values** : true, false and unknown. An ordinary comparison with `NULL` product generally unknown; `WHERE` Keeps only those lines whose condition is true. Use `IS NULL` or `IS NOT NULL` to test the absence.

`COALESCE(x, 0)` replaces an absence with zero, but changes the meaning of the data. Do so only if the contract allows it. For comparisons that must treat two null values as equal, check the operators available in the dialect and the business semantics sought.

---

Calculation: an SQL column contains 10, 20 and NULL. What do COUNT(*), COUNT(value), SUM(value) and AVG(value) give? <!--anki:3363646132636532666232373465326362393333613866303132323732306530-->
?
Common aggregates ignore null values, while `COUNT(*)` counts rows:
```text
COUNT(*) = 3 ; COUNT(value) = 2
SUM(value) = 30 ; AVG(value) = 30 / 2 = 15
```
After replacing `NULL` with zero, the average becomes **10**: the population of the denominator has changed. On an empty set, `COUNT` is zero but `SUM` and `AVG` are generally worth `NULL`.

---

Do not confuse: GROUP BY and SQL window function? <!--anki:6564333466356132356539313430306161646332356562363132346532646539-->
?
`GROUP BY` produces one line per group. A function with **OVER** calculates on a set of related lines while keeping the input lines for this step.

To attach to each sale the total of its customer, a windowed sum may be appropriate; to build one line per customer, an aggregation is adapted. Keeping the lines does not mean keeping their original grain if a join has already multiplied them. Check partition, sorting and window frame before using the result as ML variable.

---

How to select a version by identifier with ROW_NUMBER in a deterministic way? <!--anki:6466356164643736363133303434343562306131343137363238326537643033-->
?
Set a **total order** consistent with the source versions, and then filter after the window. Here `version` is non-zero and `event_id` breaks the equalities stably:
```sql
WITH ranked AS (
  SELECT id, value, ROW_NUMBER() OVER (
    PARTITION BY id ORDER BY version DESC, event_id DESC
  ) AS rn
  FROM changes
)
SELECT id, value FROM ranked WHERE rn = 1;
```
A timestamp alone can leave a gap. Stable separation guarantees reproducibility, not business truth: contradictory events to the same version must also be detected.

If the latest version is a deletion marker, keep it during filing and then filter the deleted objects. Removing deletions before `ROW_NUMBER` would cause an old active version to reappear.

---

Do not confuse: ROWS frame and RANGE frame in a SQL window? <!--anki:3931653737313039383438393439353861626639663739373237303066636532-->
?
**ROWS** delimits the frame by positions; **RANGE** defines it according to the sorting values and its limits, taking into account peers.

Example: two rows of the same date have 10 and 20. For stacking from the beginning, RANGE up to the current value can give 30 to both; ROWS gives 10 and then 30 if an identifier splits the rows in that order.

Declare frame and order explicitly. `ROWS BETWEEN 6 PRECEDING AND CURRENT ROW` means up to seven lines, not seven days. Default syntaxes and values vary by engine; test ex æquo and absent days.

---

How do I search for objects missing from a destination without the NOT IN trap with NULL? <!--anki:6539303461613535613864663437373861316433346263623961373630393133-->
?
A **anti-attachment with NOT EXISTS** directly expresses the absence of correspondence. For non-zero identifiers:
```sql
SELECT s.id
FROM source s
WHERE NOT EXISTS (
  SELECT 1 FROM destination d WHERE d.id = s.id
);
```
With `NOT IN`, a `NULL` among the values compared can make the condition unknown for objects that are absent. `NOT EXISTS` does not regulate the identity of null keys: decide whether they are invalid or comparable. Reconcile also versions and contents, because the presence of an identifier does not prove its freshness.

---

Why are UNION ALL and UNION not interchangeable in a data pipeline? <!--anki:6338343164646530636638343432336361376461353464393761323263343665-->
?
**UNION ALL** keeps all rows; **UNION** eliminates duplicates on all projected columns. Two separate business events can have the same visible values and be mistakenly merged by UNION.

Conversely, UNION ALL also keeps redelivery if no explicit deduplication follows. Choose an event identity and a version rule rather than an implicit deletion based on the columns displayed. Deduplication can also require sorting or network exchange: its cost and semantic effect must be wanted.

---

Why does a SQL CTE improve reading without guaranteeing materialization? <!--anki:3965643134643065383139653461313762626137623263633262383039376162-->
?
A **CTE**, introduced by `WITH`, names a subquery and makes visible the steps of a transformation. Depending on the engine and the query, it can be embedded in the plane or materialized; the keyword alone does not guarantee cache or unique calculation.

Use CTEs to isolate grain, filtering, and aggregation, and then inspect the plan for performance. If a step needs to be persisted, reused, or audited as a dataset, choose an explicit materialization and its refresh policy. Readability and execution cost are two separate criteria.

---

How to check an SQL time join before producing ML examples? <!--anki:6462373436646230616163613433653262306563336562643761666466623861-->
?
For each decision, filter the versions **valid and actually available** at that time, and then select the one that the service would have used. A condition relating only to the business date is not enough if the information arrives late.

Build a small game where an old fix arrives after the decision, where two versions touch each other and where no value is available. Check at most one line for example and an explicit policy of outdated value. Compare to the data actually served when possible; a global `MAX(timestamp)` does not express this join.

---

What to check before a MERGE or an upsert in an incremental transformation? <!--anki:6539303464363062376436653432653162386532623539663739396166613936-->
?
Set **match key, uniqueness, version order, and deletion processing**. Multiple source lines for the same target can cause engine-dependent error or result; null keys and disordered events require explicit policy.

Prepare the source for the expected grain, then apply a script consistent with the version. Test creation, update, duplicate, old event and deletion. An operation named MERGE does not guarantee the idempotency of the entire chain, especially if an extraction has already omitted changes or if external effects follow.

---

What risk does expanding a JSON array online in an AI dataset create? <!--anki:3837303763376465313036343436663561613030633130636664373139336163-->
?
An Operation of **Expansion**, Often called `UNNEST` or `explode`, changes the grain: a document with five elements can produce five lines. The attributes of the document are then repeated, which can multiply labels, sampling amounts or weights.

Define the identity of each element, the possible order and the processing of empty or null lists. Some modes delete them, others keep an empty line. Validate before/after accounts and aggregate to the desired grain. The exact syntax and semantics depend on the dialect; do not deduce them from the function name alone.

---

How to use EXPLAIN to diagnose a slow data preparation query? <!--anki:3339643564313965373735383430666438316432393735633133313665383736-->
?
Compare **estimated and actual** cardinalities, readings, filters, sorting and join strategies. Plan costs are not automatically milliseconds.

Example: A node expected to 100 rows produces a million; a join chosen for a small result can become very expensive. Examine statistics, selectivity, and grain before forcing a policy. Consider the number of loops to interpret a node's measurements.

In PostgreSQL, **`EXPLAIN ANALYZE` actually executes** the query: choose a suitable environment, especially for mutations. Check bytes read, partitions avoided and memory, and then confirm that the optimization retains the expected results.

---

Why test a SQL transformation with small adverse data? <!--anki:6164393634373131383134653463396238373663613033336165333632366462-->
?
A small, explicit set makes the **semantic errors observable**: duplicate keys, null values, no matches, equal timestamps, deletion, and time boundary. Set the expected lines, not just the total number.

Complement by invariants on a representative volume: uniqueness, references, business control sums and stability on replay. A request that compiles can produce false labels or lose a segment. A unit test does not however measure either the large-scale performance or the actual quality of the source.

---

Why does an incomplete ORDER BY make SQL deduplication non-deterministic? <!--anki:3865326234363963663835383432656639383534613735366164313835653233-->
?
A **ROW_NUMBER** ordered only by a timestamp can arbitrarily divide two rows of the same date. The retained row can change depending on the plan or partitioning.

Add a stable criterion that really represents the priority: source version, event sequence or identifier with explicit business rule. If two conflicting values remain equivalent, report the conflict rather than hide it. Test null equalities and timestamps. A deterministic sort guarantees the reproducibility of the choice; it does not prove that the chosen line is the correct business version.

---

## Scenarios

Scenario: a customer table loses 30% of its lines after a LEFT JOIN with their purchases. How do you look for the error? <!--anki:6134623064373962646333373461323062643661393038633437616330643033-->
?
1. **Compare before/after** credentials to identify missing customers.
2. **Inspect WHERE** filters for purchase columns, including dates and statuses.
3. **Clarify the expected population**: all customers or only those who have purchased.
4. **Move criteria to ON if appropriate**, then check for grain and sums.
5. **Add cases without purchase, with excluded purchase and with multiple purchases** to the transformation test.

**Strap**: Replace the join with another without defining what a line represents.

---

Scenario: sometimes chooses another version of the same document, without changing data. What do you check? <!--anki:6565353134626666613133363464653139323636366439626632323131643863-->
?
1. **Search for ex æquo** in the order of the window or selection.
2. **Check for source versions** and possible conflicting events.
3. **Define a stable total order**, compatible with the business rule.
4. **Test input permutations and equalities**, then compare outputs.
5. **Trace the chosen version** for embeddings and derived examples.

**Trap**: assume that the physical order of the files contractually splits the lines.

---

Scenario: an average of satisfaction increases after a SQL migration, but users do not see any progress. How do you survey? <!--anki:6666643433616663663263343461346162663066643236386139303964666339-->
?
1. **Fix the population and period** to compare the two versions.
2. **Compare denominators**, nulls and exclusions by segment.
3. **Inspect COALESCE, joins and aggregations** likely to change weights.
4. **Play on simple cases** whose expected values are known.
5. **Correct and then republish** the measures concerned, with a versioned definition.

**Trap**: Retrain the model while the metric has changed direction.

---

## Sources
- [PostgreSQL — CTE and materialization](https://www.postgresql.org/docs/current/queries-with.html)
- [PostgreSQL — joins, WHERE and aggregations](https://www.postgresql.org/docs/current/queries-table-expressions.html)
- [PostgreSQL — window functions](https://www.postgresql.org/docs/current/tutorial-window.html)
- [PostgreSQL — IN, NOT IN and null values](https://www.postgresql.org/docs/current/functions-comparisons.html)
- [PostgreSQL — read plans EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html)
- [dbt — incremental models and keys](https://docs.getdbt.com/docs/build/incremental-models)

- Supplement to the 14 November 2026 — ROWS/RANGE frames and aggregations: [PostgreSQL 18 — Value Expressions](https://www.postgresql.org/docs/18/sql-expressions.html).

## Connections
- [[150-010-analytical-data-modeling|Analytical modelling]] — preserve grain and cardinality of transformations
- [[26-text-to-sql|Text-to-SQL]] — validate the meaning and results of SQL
- [[159-temporal-data-features|Variables temporelles]] — prevents joints that reveal the future
- [[150-012-columnar-storage-lakehouse|Columnar storage, partitions & lakehouse]] — link SQL filters and data actually read
- [[150-015-distributed-computing-data-performance|Distributed Computing & Data Pipeline Performance]] — review plans and preserve result
- [[150-013-data-pipeline-orchestration|Transformations & orchestration of data pipelines]] — validate transformations before publication
- [[00-moc-ai-engineering|MOC AI Engineering]]
