# Analytical data modeling — Flashcards
Tags: #flashcards #ai-engineering #data #data-engineering
Verified on: 9 October 2026 — technical references and examples of this file.
<!-- summary: grain, OLTP and OLAP, facts and dimensions, keys, standardization, join cardinalities, additive measurements, SCD, business identity and metric definitions, weighted global average calculation, semi-additive measurements, historical dimensions. -->


Why define the grain of a table before building ML variables? <!--anki:3062336464623832353838383439306261643964313533396439623630623261-->
?
The **grain** specifies what a line represents: event, command line, customer on a date, or document in a version. It determines valid keys, joins, and aggregations.

"One line per customer" and "one line per customer per day" are not interchangeable. Mixing the two can repeat a label or overweight active customers. Write the rule of uniqueness, the population covered and the temporality before the columns, then check this contract on the data produced:
```sql
SELECT client_id, decision_date, count(*) FROM examples
GROUP BY client_id, decision_date HAVING count(*) > 1;   -- Must be empty
```

---

Do not confuse: OLTP and OLAP storage for an AI application? <!--anki:6665636261656231373233373430313338343466633637346163383539333564-->
?
A **OLTP** system serves short transactional operations: create an order, read an account or modify a report with guarantees of concurrency. A **OLAP** system prefers scans, joins and aggregations on many lines to analyze or prepare a dataset.

These are load profiles, not two waterproof categories; a small relational base can cover both. Example: PostgreSQL serves the basket in a few milliseconds, but scanning 400 million commands for a dataset returns to a columnar engine or a replica, whose delay is measured. Choose according to access, consistency and volume.

---

How does a star schema organize analytical data? <!--anki:6262656638663766353537633432333261353265353231666639326234376463-->
?
A **fact table** describes events or measurements at a specific grain; **dimensions** bear the attributes used to filter and group. A reference sales line for example product, customer and date.
```text
fact_sales(date_id, product_id, customer_id, quantity, amount) grain: sales line
dim_product(product_id, category, brand)
dim_client(client_id, segment, country)
```
This organization makes reusable joins and definitions explicit. It can feed an ML dataset or SQL wizard, without requiring all AI data to have this format. Nested documents, graphs, and events can retain other representations. Controling unique dimensions and integrity of references before aggregating.

---

Do not confuse: business key, technical key and example ID ML? <!--anki:6537346233616663333137363461626361303231313861643239366132383238-->
?
The **business key** designates an entity in the domain; a **technical key** identifies a row in a storage, possibly a historical version. The **example identifier** distinguishes a model observation, for example `(client, instant_decision)`.

The same client can produce multiple examples and dimension versions. Include the perimeter of the source or holder when the identifiers are not global. A hash sometimes avoids bulky keys, but does not resolve identity ambiguity or business duplicates. Document which keys are used for split, joins and replay.

---

When to normalize tables, and when to denormalize for AI use? <!--anki:3566326338316564373061393434343361303637373961306430633437346266-->
?
**normalization** limits duplication and update inconsistencies; **denormalization** brings data closer together to simplify or speed up recurring access. A table of ML examples is often denormalized from more structured sources.

Retain the provenance and construction logic to be able to reconstruct it. Duplicating a product category in each example may be useful, but it should be clarified whether it is its historical or current value. Measure the cost of joins against the cost of storage, refresh and inconsistency.

---

Why check cardinality before each data join? <!--anki:6139326230373030303334373439633938376338623437343138333730616530-->
?
Joining can **change the grain and weight of observations**. Multiple key matches multiply lines; multiple lines on each side produce their product.

Example: Enriching a "one line per customer" dataset with its address history overwhelms customers who have moved, so the model gets a different distribution, even if no cell is zero.

Check expected unicity (`GROUP BY ... HAVING COUNT(*) > 1`), before/after numbers and sums. Select the address applicable to the date of the example, or aggregate explicitly. A final `DISTINCT` does not necessarily restore grain and may hide inconsistencies rather than resolve them.

---

Calculation: an order for 120 € has three rows and two payments. How many rows does the join of the three tables per order, and what becomes the sum of the order amount? <!--anki:3661643739323837326235653437323061623066663439363932656566313034-->
?
With all connections between lines and payments:
```text
line_items obtenues = 3 × 2 = 6
naive sum of the order amount = 6 × 120 € = 720 €
```
The business total remains **120 €**. Pre-aggregate lines and payments to grain order, or calculate each measure in its fact table before reconciling the results. `SUM(DISTINCT amount)` is not a general repair: two different orders may have the same amount. The correct correction is on grain and keys, not on the repeated value.

---

Do not confuse: Additive, semi-additive and non-additive measurement? <!--anki:3731353934613338643935643436633861386534336664343531373562663436-->
?
A **additive** measure is based on the expected dimensions, such as sales amounts in the same currency. A **semi-additive** measure, such as an instant stock, is based between warehouses but generally not between dates. A **non-additive** measure, such as a rate, requires an adapted calculation.

To aggregate success rates, keep numerators and denominators and then sum them: 90% on 10 cases and 50% on 1,000 cases give 70% on average simple, but (9 + 500) / 1,010 ≈ 50.4% in total. Declare allowed dimensions, units or mixed sales.

---

Do not confuse: SCD slow-moving dimensions type 1 and type 2? <!--anki:3437633137353138666338343436623162633364653431633565646630336634-->
?
The **type 1** replaces a value and essentially retains the current state. The **type 2** adds a dimension version, with validity period and identity to attach the facts to this version.

The choice depends on the question: analyze the customers according to their current segment, or according to the one associated with each sale. The 2 type does not automatically reconstitute the changes never collected. Nor is it enough to guarantee the actual availability of information during an ML decision; this requires an explicit temporality of knowledge.

---

Why use non-overlapping validity intervals in a historical dimension? <!--anki:3735313132333661323836363436356562336331366331383063663264376631-->
?
Intervals such as **[start, end]** make it possible to match a version for a moment at most, if the periods of the same entity do not overlap.

Test overlaps, holes and the number of common versions. A `is_current` is not enough to join an old sale. Also distinguish business validity and date of knowledge: correcting an old period today does not allow to use this correction to simulate what the model knew yesterday.

---

How to manage a dimension that comes after the fact that references it? <!--anki:3530373933313263316365363433363439386363313736396438663730383232-->
?
Keep the fact with a **missing reference status** or provisional dimension line, depending on the contract, then reconcile when the dimension arrives. Measure these cases and define the uses that should wait.

Example: a sale of the 3 March references a client created in the CRM the 5; it is loaded with the key −1, "unknown client", then attached to the correct version the 5. An internal join would silently remove this orphan fact. At repair, recalculate dependent results. An "unknown" member facilitates publication, but does not make information reliable for the drive.

---

Why does the entity resolution need to be evaluated before merging sources for the ML? <!--anki:6635636562646163333564653434383562633138643363613361656165333730-->
?
The **entity resolution** decides whether records refer to the same entity despite different identifiers. An abusive merge mixes people or products; a missed merge fragments their history and can split their data between train and test.

Prefer reliable matches when they exist, then evaluate approximate approximations on annotated references. Keep method, score, version and possibility of separation. An identical name is not a global key. Adapt thresholds to the consequences: bring "Jean Martin, Lyon" and "J. Martin, 69003" with a score of 0.82 may be enough for a campaign, not to merge health histories.

---

What should a business metric reused by models and a SQL wizard specify? <!--anki:6263376435353863343934633463646462653461323563353837366338386530-->
?
Set **population, grain, numerator, denominator, period, and exclusions**. “Active customer” can mean connection, purchase, or subscription not terminated; a valid SQL query does not resolve this ambiguity.

Version the definition and its dependencies, with owner and expected examples:
```yaml
metric: resolution_rate            # version 3, owner: support
population: closed tickets, excluding spam
numerator: tickets resolved without reopening within 7 days
denominator: closed tickets
period: ISO week, Europe/Paris time zone
```
A semantic layer centralizes these rules, but must still respect access rights, freshness and availability of dimensions. Testing a small game including refunds, unknowns and temporal boundaries helps reveal divergences before they become labels or user responses.

---

Calculation: A group of two commands is 10 € on average and a group of eight is worth 20 €. What is the overall average? <!--anki:3637656264373331393639323430333362646136346661343661313165363738-->
?
First reconstitute the sums: `2 × 10 + 8 × 20 = 180 €` for ten orders. The **global average is 18 €**, and not the unweighted average `(10 + 20) / 2 = 15 €`.

Keep effective and sum with an aggregated average to be able to recombine it correctly. Verify that populations are disjoint, units are identical, and missing values are treated according to the same rule. The same trap appears in a dashboard that averages the average scores of clients of very different sizes.

---

Why is a bank balance a semi-additive measure in an analytical model? <!--anki:3330373137376466613965383438343362643032323166623666343937646335-->
?
You can add **account balances at the same time**, but adding the balance of the same account over several days does not give a relevant balance.

Define the time grain and expected aggregation: last state, time average or other business measure. An SQL engine will run `SUM` without knowing if it makes sense. Document the additivity of each measure according to dimensions.

---

Why can joining a historic sale to the current customer dimension change past reporting? <!--anki:3464666634393538623033303466316461373430353432643336363463343165-->
?
The customer may have **changed region or segment** since the sale. Using its current value reallocates the past according to today's situation.

Explicitly choose a historical or current reading. For the history, use the valid dimension version at the chosen time and ensure unambiguous intervals. Both reports may be legitimate, but they answer different questions.

---

## Scenarios

Scenario: After joining with support tickets, customers who often contact support weigh more in the training. How do you fix the dataset? <!--anki:3332373631356464323164393464633238636130313362353064343965343331-->
?
1. **Speak the expected grain**: one observation per customer and moment of decision.
2. **Measure the multiplication** of rows by key before and after joining.
3. **Aggregate tickets available** at this time into explicit variables.
4. **Check uniqueness and labels**, then rebuild splits according to entities and time.
5. **Compare segments** and scores after correction, without reusing the test to adjust the solution.

**Trap**: arbitrarily remove duplicates without understanding what information has been repeated.

---

Scenario: a historical report changes as soon as a customer moves from the SME segment to the large account segment. How do you determine if it is a bug? <!--anki:6161316432656665316465323436313239393866653766623064626432663134-->
?
1. **Clarify business question**: current segmentation or segmentation as of the date of the facts.
2. **Inspect the dimension strategy** and the history actually preserved.
3. **Choose the appropriate join**, with non-overlapping intervals for historical reading.
4. **Test a customer who changes segment**, especially at the validity border.
5. **Verify the definition of the report** and announce any break in series.

**Trap**: impose the 2 type on all uses without defining what the report should represent.

---

Scenario: two sources both use client_id = 42, but for different clients. One model receives their mixed histories. What do you change? <!--anki:3433613438613730613334353433363039326464383964616531363231343631-->
?
1. **Contain incorrect merge** and identify affected datasets and predictions.
2. **Qualify keys** by source or holding before any join.
3. **Build a separate lookup table** for authorized cross-source reconciliations.
4. **Test collisions and separations**, then rebuild variables, labels and splits involved.
5. **Add an identity contract** with owner, rules and cardinality checks.

**Trap**: Change only the column type or hash the `42` value without its perimeter.

---

## Sources
- [Kimball Group — declare grain](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/grain/)
- [Kimball Group — additive and non-additive measurements](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/additive-semi-additive-non-additive-fact/)
- [Kimball Group — techniques SCD](https://www.kimballgroup.com/wp-content/uploads/2013/08/2013.09-Kimball-Dimensional-Modeling-Techniques11.pdf)
- [PostgreSQL — joins and table expressions](https://www.postgresql.org/docs/current/queries-table-expressions.html)

## Connections
- [[157-data-contracts-quality|Contracts & quality]] — define grain, keys and sense of measurement
- [[159-temporal-data-features|Temporal data]] — connect business history and availability for the model
- [[26-text-to-sql|Text-to-SQL]] — make allowable joins and metrics explicit
- [[150-011-analytical-sql-transformations|SQL for AI Pipelines and Datasets]] — preserve grain and cardinality of transformations
- [[00-moc-ai-engineering|MOC AI Engineering]]
