# Distributed Computing & Data Pipeline Performance — Flashcards
Tags: #flashcards #ai-engineering #data #data-engineering
Verified on: 9 October 2026 — technical references and examples of this file.
<!-- summary: Local or distributed choice, lazy execution, partitions, shuffle, skew, broadcast, salting, driver memory, UDF, cache, aggregations, Amdahl’s law and processing cost, unbalanced partition and hot key, preventable shuffle, partial aggregation. -->


When to distribute data processing rather than run it on a machine? <!--anki:6331663030656464613039623434643038353038613564656161386234653837-->
?
When **volume, processing time, concurrency or fault tolerance** exceeds what a suitable machine can provide at an acceptable cost. First compare a vectorized local execution, possibly capable of overflowing on disk, to the distributed solution.

Distributing adds coordination, transfers and exploitation; a small job can become slower. A volume higher than RAM does not always impose a cluster: DuckDB can aggregate 200 GB of Parquet on a 64 GB machine by overflowing on disk. Measure maximum memory, I/O, duration and cost on a representative load, with a reserve adapted to the peak.

---

Do not confuse: lazy transformation and action in an engine like Spark? <!--anki:3132643464323135323838343464623239623664623161333361643831376465-->
?
A lazy **transformation** constructs a plan without necessarily calculating it immediately. An **action** requests a result and triggers its execution. This separation allows the optimizer to combine operations and reduce readings.

Defining a transformation without taking action does not measure the real time of the pipeline.
```python
df = spark.read.parquet("s3://sales/").filter("country = 'FR'")  # Plan only
df.count()                          # action: reading, filter pushed into the scan
df.write.parquet("s3://output/")    # second action: everything is reread without persistence
```
Include execution, writing and validation in the benchmark, and understand if the observed result comes from cold or already cached data.

---

What is a shuffle in a distributed calculation? <!--anki:6438396633363565343235363432656362393432333238363732343062643861-->
?
A **shuffle** redistributes data between partitions, often between machines, to match those needed for a join, sort, or aggregate. It can cost network, serialization, memory, and disk.

Filtering rows, projecting columns, and preaggregating when valid can reduce bytes exchanged. Not all operators with the same name produce the same plane: existing partitioning and engine count. Inspect the physical plane, where Spark displays a shuffle like `Exchange hashpartitioning(client_id, …)`, and exchange metrics; more CPU does not necessarily repair a saturated network.

---

Why is the number of calculation partitions a compromise? <!--anki:3066303161366332373137343463313538373462313766653030303234666436-->
?
Too few partitions limit **parallelism** and increase memory per task; too many small partitions increase scheduling fees and small files produced. Their size can be very uneven despite a seemingly correct number.

Distinguish file partitions, shuffle partitions and table business partitions. Example: with the 200 default shuffle partitions of Spark, 2 TB give tasks of about 10 GB; 4,000 partitions bring each back to 500 MB. Adaptive execution can then merge the too small ones. A `repartition(1)` can simplify output while creating a bottleneck and memory risk.

---

How do I recognize a keystroke in a distributed join or aggregation? <!--anki:6433313061643333336430363438353861646661626632336536306139363332-->
?
The **skew** appears when some keys concentrate much more data or work. Some tasks become very long or overflow in memory while the others are completed.

Compare common partition sizes, durations, and keys, including null or default values: for example, `GROUP BY client_id ORDER BY count(*) DESC LIMIT 10` reveals 30% lines on `client_id` as null. Possible responses include preaggregation, separate hot key processing, or `spark.sql.adaptive.skewJoin.enabled`, which cuts out too large partitions from a join. Adding workers does not automatically share an indivisible key. First, check that a wrong join is not causing the join.

---

When is a broadcast join useful and what memory risk does it introduce? <!--anki:6235666330343764313639633465373061336233346235333331376164386463-->
?
It broadcasts a **small relationship** to workers to avoid redistributing the large one according to the join key. It is suitable if the small relationship and the structure necessary for the join fit in the available memory of the performers.

The compressed size on disk often underestimates the decoded size and hash table. Spark automatically broadcasts an estimated table under `spark.sql.autoBroadcastJoinThreshold`, 10 MB by default, and the hint `broadcast(ref)` forces the broadcast beyond: neither proves that it holds in memory. Compare plans, memory peak and duration; check the semantics and support of the join type.

---

How can salting distribute a hot key without distorting an aggregation? <!--anki:3164653834653139323534353461366639366239333763393434343664333237-->
?
Adding a **distribution suffix** to the hot key allows you to produce several partial aggregates, then combine them by removing this suffix. The function must be combinable correctly.

For an average, keep sum and effective; averaging partial averages without weight is incorrect.
```python
sale = df.withColumn("sel", (F.rand() * 16).cast("int"))
partial = sale.groupBy("client", "sel").agg(F.sum("amount").alias("s"), F.count("amount").alias("n"))
final = partial.groupBy("client").agg(
    F.when(F.sum("n") > 0, F.sum("s") / F.sum("n")).alias("mean")
)
```
A salty join may require replicating matches on the other side, which increases the data. Test accounts and sums after recombination. Salting is not a universal recipe: non-decomposable functions and order requirements limit its use.

---

Why can collecting a distributed result on the driver cause a failure? <!--anki:6566316130313838313136383437616362306331353639376239333963306631-->
?
An operation like **collect** returns the result in the coordinating process. The total memory of the cluster does not protect this process, which may need to receive and materialize all the rows.

To inspect, `df.limit(1000).toPandas()`; to publish, `df.write.parquet(...)` from partitions. In Spark, `spark.driver.maxResultSize`, 1 GB by default, limits the serialized results, **not the peak memory after decoding**. Even 1,000 very wide lines can overflow. Aggregate before repatriating a small result and measure its size. Increasing the driver RAM can postpone the failure without correcting a collection.

---

Why would you prefer native expressions over line-by-line UDFs when they’re enough? <!--anki:6231393762303136383337663438663338666464616135643564383035656235-->
?
Native expressions are often **visible from the optimizer** and executed vectorically. An opaque UDF, especially with a passage between runs, can introduce serialization, allocations and loss of optimizations.

Example: `F.lower(F.col("email"))` stays in the engine; `udf(lambda s: s.lower())` sends each row to Python; a `pandas_udf` handles Arrow batches. A UDF remains useful for logic that cannot be expressed otherwise. Compare results on nulls, types and encodings, and then measure performance. Network calls or LLM in a UDF also add quotas, repeats and repeated effects: their orchestration must be explicit.

---

When to persist an intermediate pipeline result in memory or disk? <!--anki:3866616662333735663632353437373039646431366435386438636665396364-->
?
When its **re-use** saves more than its materialization, storage and management costs. A once-calculated intermediary does not automatically benefit from being cached.

Example: A cleaned feature table feeds three aggregates; `df.persist()` before the three actions avoids three replays, and then `df.unpersist()` frees up memory. Also evaluate decoded size, invalidation, and associated source version. A cache can speed up a benchmark while hiding the cost of a first pass. Persisting to speed up is not the same as publishing a sustainable and audited version of data.

---

How to choose between exact and approximate aggregate on large volumes? <!--anki:6235623966633238616533353430343262313837623937393838613366646162-->
?
An aggregate **approximate** can reduce memory and exchanges to estimate cardinalities or quantiles, with an error depending on the algorithm and parameters. It can be suitable for exploratory monitoring if its accuracy is sufficient for the decision.

Example: `approx_count_distinct("user_id", rsd=0.01)` is for a **relative standard deviation** of 1%, not a guaranteed maximum error of 1%. It does not prove the absence of duplicates. For billing or a contractual threshold, check whether the approximation is acceptable. Document error, population and merge properties. Compare to an exact result on a controlled perimeter, without extrapolating universal accuracy.

---

How to distinguish a pipeline limited by the CPU, memory or I/O? <!--anki:6334336435313262616535313464346261666265646531303733323665633539-->
?
Connect **step times** to CPU usage, network/disk wait, read rate, maximum memory, and spill volumes. Little-busy workers can wait for files, a downstream quota, or an unbalanced task.

Example in the Spark interface: a stage with 40 GB of "Spill (Disk)" lacks memory per task; an internship that reads S3 with CPU To 15% It is limited by I/O. Reducing readings helps an I/O bottleneck; Filtering before a shuffle reduces trade. Limiting batches limits the memory peak. A percentage CPU global can hide a single saturated task.

---

Calculation: 20% of a pipeline remains strictly sequential, and 80% perfectly parallels. What maximum gain with ten workers according to Amdahl’s law? <!--anki:3633663438376530343532313466336661363232373538353763336265633334-->
?
Under these ideal assumptions:
```text
acceleration = 1 / (0.20 + 0.80/10) ≈ 3.57
limit with an infinity of workers = 1 / 0.20 = 5
```
Ten workers therefore do not give a gain of ten. Coordination, network and imbalance can further reduce this result. This formula assumes a fixed load and a sequential fraction unchanged; it does not describe a simultaneous increase in the volume processed. Locate the sequential part may be more useful than multiplying machines.

For example, speeding up only the parallel read leaves the sequential 20% intact. Profile the entire pipeline before purchasing workers; the enhanced component must belong to the path that actually limits execution.

---

Calculation: A uses two workers at 0.80 €/h for 45 minutes; B uses four at the same rate for 30 minutes. What cost per run, excluding storage and other charges? <!--anki:3934646165636233323435323432313562363964633731333233346165653930-->
?
With these fictitious rates and billing proportional to time:
```text
A = 2 × 0,80 × 45/60 = 1,20 €
B = 4 × 0,80 × 30/60 = 1,60 €
```
B finishes fifteen minutes earlier but costs about **33% more**. The choice depends on the time required, the reserve and the value of the time saved. Add orchestration, storage, transfers and failures for the full cost. A shorter duration is not enough to announce a cheaper pipeline.

---

Why can a single very large partition limit an entire distributed calculation? <!--anki:3139343264316439366231383435323161363066616137353463313963613030-->
?
**End time** often depends on the slowest task. A very common key can focus work on a partition while other workers wait.

Measure distribution of sizes and durations per partition before adding workers. Depending on the algorithm, preaggregate, treat hot keys separately or distribute their work with correct recombination. Test the equalities and accuracy of aggregates after change. More parallelism does not accelerate an indivisible key; a misallocation can dominate CPU and network yet available.

---

Why preaggregate before a shuffle can reduce the cost of a distributed calculation? <!--anki:6263653130633862633564333438313838623766336563373131386132323566-->
?
When the operation allows, each partition can **combine its lines locally** and send less data to the global grouping. A sum combines easily; an exact median requires more information.

Check the properties of the aggregate and the cardinality of the keys. If almost each key is unique, the gain is limited. Measure the bytes exchanged and the memory, not just the number of tasks.

---

## Scenarios

Scenario: 99% Spark tasks end in two minutes, but only one lasts forty minutes. What do you look for before adding machines? <!--anki:6434616135663639306366333466626539663666313961316437626235313236-->
?
1. **Compare the slow partition** to others: bytes, lines, keys, and spill.
2. **Look for hot keys or multiplicative joins**, especially on nulls.
3. **Check the plan** and the ability to pre-aggregate or isolate this key.
4. **Test an appropriate strategy**, such as additional allocation or separate processing.
5. **Compare result, duration and cost**, with a case that voluntarily concentrates data.

**Trap**: Increase workers without changing the work of the blocking partition.

---

Scenario: a reference table makes 200 MB on disk but its broadcast causes memory errors. How do you investigate? <!--anki:3364386530333735393135383465386339643765383032353533336131333766-->
?
1. **Measure the decoded size** and join structure created in memory.
2. **Count concurrent copies and tasks** by executing.
3. **Spreading and filtering the reference** before the broadcast if the result remains equivalent.
4. **Compare with another join policy** and suitable partitions.
5. **Check memory peaks** on the actual load before resetting the broadcast.

**Strap**: Use the only compressed size to ensure that a table holds in memory.

---

Scenario: a distributed embeddings job restarts some partitions and the API invoice doubles. How do you make the processing reliable? <!--anki:6330396139353930393939333465616361353466353363326433623236363664-->
?
1. **Trac repeats** by object, text hash, and model version/configuration, including speculative attempts of the distributed engine.
2. **Reuse a durable result** for this key; publish atomically so that two workers do not create two logical results.
3. **Examine the billing border**: If the API offers an idempotency covering the operation, reuse its key. Otherwise, the downstream deduplication does not cancel the calls already invoiced.
4. **Borner concurrency and withdrawals**, with quotas and distinction between permanent error, transient and unknown result.
5. **Inject critical failure** after remote success but before local backup, and then measure invoiced calls and published duplicates separately.

**Trap**: Promise billing exactly once while the API does not provide idempotency or recovery of lost result.

---

## Sources
- [Apache Spark — shuffle, persistence and actions](https://spark.apache.org/docs/latest/rdd-programming-guide.html)
- [Apache Spark — joins, partitions, statistics and skew](https://spark.apache.org/docs/latest/sql-performance-tuning.html)
- [DuckDB — optimization and processing beyond memory](https://duckdb.org/docs/current/guides/performance/how_to_tune_workloads)

## Connections
- [[150-012-columnar-storage-lakehouse|Analytical storage]] — connect data layout and execution cost
- [[150-011-analytical-sql-transformations|Analytical SQL]] — review plans and preserve result
- [[148-llm-batch-pipelines|Pipelines batch LLM]] — limit model calls and make repeats safe
- [[150-013-data-pipeline-orchestration|Transformations & orchestration of data pipelines]] — sizing resources and critical path
- [[00-moc-ai-engineering|MOC AI Engineering]]
