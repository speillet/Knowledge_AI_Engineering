# Transforming & orchestrating data pipelines — Flashcards
Tags: #flashcards #ai-engineering #data #data-engineering
Verified on: 9 October 2026 — technical references and examples of this file.
<!-- summary: ETL/ELT, data layers, tasks and assets, logical intervals, dependencies, incremental, retrievals, publication, CI, resources and critical path of a DAG, concurrent publication of the same interval, available data, successful task without publication. -->


Do not confuse: ETL and ELT in an AI data pipeline? <!--anki:3335323665353333336238353433396662366239393935376130313139346330-->
?
**ETL** transforms before loading into the analytical destination; **ELT** loads first, then transforms with the resources of that destination. An actual string often combines both: pseudonymize customer emails before the shared warehouse, and then transform raw loaded logs with dbt.

Retaining sources facilitates certain issues, but does not justify unlimited copying of all sensitive data. Choose where to filter, pseudonymize and validate according to the accesses and authorized uses. Compare transfer costs, resources and traceability. The order of the letters does not guarantee either quality or reproducibility: these require contracts, versions and publication rules.

---

What interest do raw, prepared and business layers have in an AI pipeline? <!--anki:3361363930643062353730623430316262613066646566383034613335383837-->
?
They separate **fidelity to the source, common transformations and consumables**. Example: `brut.tickets` keeps the JSON received to explain and replay; `prep.tickets` type dates and duplicates; `metier.tickets_resolus_jour` exposes one line per ticket solved and per day, with its guarantees.

The names bronze, silver and gold are conventions, not automatic quality levels. Each layer must have a contract, owner, retention and access. Avoid multiplying copies without need; a small pipeline can materialize only the borders useful for recovery, sharing or validation.

---

Do not confuse: orchestrator and data processing engine? <!--anki:6130323930663631383436303431366639666666666233323366323134373033-->
?
The **processor** decides which tasks to run, with which dependencies, parameters, and resumes. The **processor** executes transformations: SQL queries, distributed computation, parsing, or batch inference.

Example: An Airflow task initiates a BigQuery query of 40 minutes; the calculation is executed at BigQuery, and the task must follow the job ID. The DAG must know its true end and retrieve its output references, not only find that a submission has succeeded. This separation helps to size each layer, but requires handling cancellation, timeout, and resume when a job continues after losing connection to the orch.

---

Do not confuse: pipeline task and data asset? <!--anki:3065313931373331623363363435363761306339333634383337353461343831-->
?
A **task** represents an executed operation; an **asset** represents an identifiable data result, such as a feature table or a corpus partition. The same task can produce multiple assets, and an asset can be rebuilt during multiple executions.

With Dagster, the asset itself declares dependencies and partitions as follows:
```python
@asset(partitions_def=DailyPartitionsDefinition(start_date="2026-01-01"))
def features_clients(orders):      # depends on the asset "orders"
    ...
```
An asset-oriented orchestration facilitates this reasoning, but does not eliminate content controls or consistency issues between multiple outputs.

---

Why set a job by data interval rather than by the current time? <!--anki:3963323130643034643937613433363438643838663230313734346162646533-->
?
The **logical interval** specify the data to be processed, regardless of the actual launch time. A Monday job can be performed on Tuesday after a breakdown while reconstructing exactly the Monday period.

Use explicit bounds, for example [start, end], with a defined time zone. A filter based on `now()` changes the perimeter during a retry and makes a backfill ambiguous. In Airflow, the interval associated with the run and its logical date do not necessarily mean the execution time. Test boundaries and time changes for local calendars.

---

How do I set the data dependencies of a downstream partition? <!--anki:3436626265303765326638343431653262666638663338373665326264376633-->
?
Describe **which partitions and upstream versions power each downstream partition**, with the rule of completeness, Not just the order of tasks.

For example, a seven-day daily feature `J−6` to `J` depends on these seven entries. Correcting the source of the day `J` also invalidates the outputs already produced for `J+1` to `J+6`, not just `J`.

Save this link to target the recalculation and avoid an unnecessary full backfill. Distinguish between missing entry, valid empty and temporary; publish with a completeness indicator if the job accepts it. A green task does not prove that its dependencies match the correct versions.

---

Why pass dataset references between tasks rather than their full content? <!--anki:3133383036323433646564313462663738323635393731343564353136303961-->
?
Orchestration metadata is suitable for **identifiers, paths, versions, and manifests**, not millions of rows or model weights. Example: A 2 million row DataFrame in XCom fills the Airflow metadata base; `s3://features/v42/_manifest.json` is enough.

Write the results to a suitable storage, then pass a stable reference with access controls and retention time. The next task checks the release version and status. A mutable `latest` path does not offer the same guarantee as an immutable manifest; an expired reference must be detected clearly.

---

How to make a transformation task safe to restart? <!--anki:6566366433353762383064623432353761613363316166613737643433326133-->
?
Define a result identified by **inputs, period, and logical version**, and then publish idempotently or replace a complete partition according to a secure protocol.
```sql
BEGIN;
DELETE FROM daily_sales WHERE day = DATE '2026-10-21';
INSERT INTO daily_sales SELECT ... WHERE day = DATE '2026-10-21';
COMMIT;   -- relaunch returns the same partition, without duplicates
```

Test a crash before writing, after writing and before confirmation to the orchestrator. External calls can be repeated despite a deduplicated downstream output: provide identifiers and appropriate guarantees. A task that resumes must not choose new implicit entries or restart a business effect without control.

---

How to distinguish an error to try again from an error to fix in a pipeline? <!--anki:3666613337666338343033323436343761363536616465326665363333636231-->
?
A **transient** error, such as a brief unavailability or a temporary quota, can justify bounded retries with increasing expectation and dispersion. A schema violation or invalid data often requires correction or quarantine.

Example: HTTP 429 or 503, retry after 1, 2 and then 4 s with dispersion, five times at most; column `amount` missing, quarantined and alerted to owner, without retrying. Retrying immediately at infinity can saturate the dependency and block other partitions. Do not absorb the error and declare the full dataset; make visible

---

Why does an incremental transformation not reduce to filtering the most recent rows? <!--anki:3265616161316137383066363465366662653036333665646236343738636464-->
?
It must process **creations, changes, deletions and late corrections** according to the expected result. A filter on the maximum business date may miss an old line arriving today.

A three-day window does not catch a correction received after a week: provide reconciliation or targeted reconstruction. In dbt, `unique_key` helps some strategies to bring the lines closer together; this parameter does not alone impose uniqueness, absence of nulls or capture deletions.

---

What to check in CI for a data transformation before its publication? <!--anki:3865383533663130663166633466303139653131653239306538663330633062-->
?
Combine **logic tests on small examples**, schema and contract checks, and then compare a result on a representative perimeter. Test keys, time limits, deletions and replays, not just compilation.

Run in an isolated destination with limited rights and costs, e.g. `dbt build --select state:modified+ --defer --state prod/` for only modified models and their dependencies. A dbt test passes when its query returns zero rows: `WHERE amount < 0` on an always-zero column always passes.

---

Why does a fixed-time trigger not prove that the upstream data is ready? <!--anki:6635343033653666346536363463356439386162383961393764383266396333-->
?
A schedule provides for **execution**, not the completion of a source. An export can arrive late, partially or under a new scheme while the downstream cron starts normally.

Waiting for a reliable release signal, checking manifest and contract, and then applying timeout and missing data policy. An event trigger reduces some delays, but a "created file" event can also happen before a full release: an export written in 25 minutes is read truncated, unless one expects a `_SUCCESS` marker or a manifest. Separate arrival, validation and availability for consumption, with an explicit state at each border.

---

How to prevent a backfill from monopolising the resources of common pipelines? <!--anki:6362313636623664393431343438653061666633346632363535303230626162-->
?
Reserve **concurrency and quotas** by work class, limit active runs and split the backfill into repeatable units. In Airflow, for example, `max_active_runs=2` on the backfill DAG and a `backfill` pool of two locations, separate from that of current traffic. Take into account the limits of source, warehouse and API models, not just workers.

Measure current traffic delay and replay progress, and then adjust the priority. Individually light tasks can produce a significant spike when they start together. Schedule pause, cancel, and clean up; a remote job can continue to consume after an orchestrator timeout.

---

Calculation: a DAG has an ingestion of 2 minutes, two independent branches of 10 and 4 minutes, Then a publication of 3 Minutes waiting for both. What is the ideal duration and what is the cumulative work? <!--anki:3166623462333236336535623431383962383636633864643239383130303666-->
?
Without expectation or contention:
```text
critical life = 2 + max(10, 4) + 3 = 15 minutes
cumulative work = 2 + 10 + 4 + 3 = 19 minutes of task
```
Reducing the branch by four minutes does not accelerate this critical path as long as it remains shorter than the other. Parallelism, however, consumes simultaneous resources. Include files, startup, transfers and validation to predict the actual time. These task minutes are not directly minutes charged if the tasks use different resources.

If the two branches share a saturated resource, they are no longer independent in execution time. Measure their simultaneous times rather than reuse their isolated times to promise the fifteen minutes.

---

Why should two orchestrations of the same data interval publish a consistent result? <!--anki:6534393565393834363234353437613639393530393536613330666130653565-->
?
A **retry, backfill, or manual launch** can recalculate the same interval in parallel. If each run writes directly to the final destination, readers can see mixed results.

Defining a logical partition identity, writing in a single version, validating and publishing with a competitive check. Deciding whether a second run finds the existing result or replaces it according to an explicit rule. Testing two simultaneous runs. The success of all tasks in a DAG does not guarantee that their competing release complies with the data contract.

---

Why is a data dependency more accurate than just waiting between job hours? <!--anki:6433643662623338386465643436636438323861623565626433306563623563-->
?
A job launched at 03 h may depend on a producer of 02 h **who has failed or published only part of the data**. The time does not prove availability.

Trigger according to a state of publication validated for the expected interval, with freshness and completeness. Plan timeout and delay policy. A success of the scheduler should not be confused with a data ready for its consumers.

---

What does the success of a pipeline task mean if its results are not yet published? <!--anki:6165666362383962613963343433376339336630383063383666363730346161-->
?
It can only mean **that the calculation has ended**. Consumers need a complete and consistent publication, possibly separate.

Separate calculated, validated and published states, then set which state unlocks downstream. Test a failure between these steps. A recovery must be able to verify artifacts already produced without creating a partially visible batch or overwriting a published version.

---

## Scenarios

Scenario: a January backfill written in today's partition because the script uses the system date. How do you fix it? <!--anki:3264313131623362323035653432356161386437646333366339646566646363-->
?
1. **Identify affected exits** and suspend publication if necessary.
2. **Spread the logical interval explicitly** to read and write.
3. **Pin entries and code version** to make each partition reproducible.
4. **Test two reminders on different dates**, with the same parameters and expected results.
5. **Repair affected partitions** and then validate dependent consumers.

**Trap**: Change only the name of the output file without correcting the input filter.

---

Scenario: a task submits a remote job, loses the connection and then retrys it a second time. What strategy do you propose? <!--anki:6234623531333764653665643433306339363265396331623034386165393065-->
?
1. **Give stable identity to submission** when remote service allows it.
2. **Keep the job ID** and check its status before recreating work.
3. **Definite the cancellation policy** and the treatment of an unknown state.
4. **Make the downstream publication idempotent**, even if the calculation has been executed twice.
5. **Test the loss of connection after acceptance** and observe the residual cost.

**Trap**: Believe that a local timeout proves that remote processing has not started.

---

Scenario: a DAG is green, but the published dataset contains only nine out of ten expected partitions. What do you change? <!--anki:6563343534396332373137623436346162643931616663333738646238303564-->
?
1. **Define a manifest of the expected partitions** for this interval.
2. **Check for success rules** and absorbed errors or skipped tasks.
3. **Add validation before publication**, with volumes and version consistency.
4. **Publish a partial status only if the contract allows it**, otherwise maintain the latest valid version.
5. **Replay the missing partition** and test this failure scenario.

**Trap**: Conflate orchestration success with data product compliance.

---

## Sources
- [Apache Airflow — best practices for tasks and data](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)
- [Apache Airflow — runs and data intervals](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dag-run.html)
- [Apache Airflow — backfill control](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/backfill.html)
- [dbt — incremental and key limits](https://docs.getdbt.com/docs/build/incremental-models)
- [dbt — data testing](https://docs.getdbt.com/docs/build/data-tests)

## Connections
- [[158-ingestion-cdc-backfills|Ingestion & backfills]] — coordinate covers, partitions and publication
- [[150-011-analytical-sql-transformations|Analytical SQL]] — validate transformations before publication
- [[41-code-nocode-automation|Automation]] — separating orchestration and processing
- [[150-015-distributed-computing-data-performance|Distributed calculation]] — sizing resources and critical path
- [[150-014-streaming-event-processing|Streaming & event processing]] — coordinate treatments and recoveries
- [[150-016-data-observability-lineage|Observability, lineage & data exploitation]] — link successful execution and availability of results
- [[117-continuous-training-pipelines|ML Training Pipelines]] — caches immutable steps and snapshots
- [[00-moc-ai-engineering|MOC AI Engineering]]
