# Text-to-SQL & structured data — Flashcards
Tags: #flashcards #ai-engineering #rag #text-to-sql #data #llm
Verified on: 29 September 2026 — This factsheet lists products, versions or regulatory texts that are evolving quickly.
<!-- summary: text-to-SQL or RAG, prompt content, schema linking, semantic layer, execution security, correction loop, exact match or execution compliance, benchmarks (Spider, BIRD, Spider 2.0), ambiguous questions, limits of SQL validation on sample, join fan-out, NULL values. -->


What is text-to-SQL? <!--anki:797b6930743e52773076-->
?
A LLM **translates a natural language question into a SQL query**, which is executed on the basis; the result is then presented or summarized. This is the way to answer the questions **encrypted and aggregated** ("how many", "what evolution", "top 10") on tabular data.

The difficulty is also **semantic**: "turnover" requires definition, period, currency, and cancellation management. A valid SQL query can calculate the wrong indicator. Provide the useful schema, control the rights and execution cost, and then verify the result on cases whose business calculation is known.

---

Do not confuse: text-to-SQL and RAG? <!--anki:49415b3c493c4d7148-->
?
- **RAG**: find relevant **text passages** and let the LLM get the answer. Good for "what does the refund policy say?"
- **Text-to-SQL**: Makes **calculate** the base. Good for "How many refunds in March, by region?"

A RAG does not know **Count** : it goes up k chunks, Never all the lines. Business assistants often combine the two, with a **Routing** according to the question ([[21-rag-fundamentals|when not to do RAG]]).

---

What is in the prompt of a text-to-SQL system? <!--anki:7145587c263171674831-->
?
- The **schema**: tables, columns, types, keys, with **business descriptions** (“`status = 3` means canceled”)
- Some **example values** per categorical column, to write the right filters
- The **Example Question → SQL** validated, close to the question (selected by similarity)
- The **dialect** (PostgreSQL, BigQuery, Snowflake) and rules: read-only, `LIMIT`, time zone

A raw schema without descriptions is a common cause of error.

---

How can a text-to-SQL system handle a schema of 500 tables? <!--anki:744e306277797e296e65-->
?
By **schema linking**: a first step selects the **tables and columns that are useful** to the question (description search, or LLM), then we put only this sub-schema in the generation prompt. Otherwise, the schema saturates the context and the **confound model of the homonymous columns**.

Better yet: expose prepared **business views** rather than raw tables.

For "revenues per customer", selecting `clients` and `lignes_facture` without the `factures` link can make the right query impossible, even with the right amount columns.

---

What is a semantic layer and why does it help? <!--anki:4a75536f372969675526-->
?
A layer that defines **once** the **metrics and dimensions** of the company ("net sales", "active customer") with their official calculation (dbt Semantic Layer, Cube, LookML). The LLM chooses **which metric and which filters**, instead of writing the join and formula.

Gain: the figures **match those of the dashboards**, and the LLM cannot invent its own definition of the turnover.

---

How to secure the execution of generated queries? <!--anki:503f54667a6e2f616d4d-->
?
- Basic account in **read-only**, on a **replica**, with only the allowed schemes
- **Safety at the line level** (row-level security): the user only sees his data, Whatever the request
- **Query analysis** before execution: only one `SELECT` statement, tables allowed
- **Timeouts**, `LIMIT` and budget: preliminary cost estimate (`EXPLAIN`, dry run BigQuery)

The generated request is an unreliable **input**, which can be influenced by injection ([[101-llm-security-guardrails|Security]]).

---

How does a text-to-SQL system fix its errors? <!--anki:493c403f785f2c3e4b37-->
?
By an **Bounded Loop** : analyze the request, use `EXPLAIN` When relevant, then execute under controlled permissions and limits. Returning an exploitable error without secrets helps to correct syntax or unknown columns.

A successful execution does not validate the **sense**. Example: join each command to its lines and then sum the order total counts it several times. Control grain, cardinalities and aggregations, with datasets where the error becomes visible. An empty or negative result deserves consideration, but can be legitimate: do not arbitrarily modify the request until a "reassuring" result is obtained.

---

Do not confuse: Exact Match and Execution Accuracy? <!--anki:4a5e2b332a234d433067-->
?
- **Exact match** : the generated request is **identical** The reference request? too strict, because there are several correct SQL
- **Accuracy**: Do the two queries give the **same result** on the basis? This is the standard metric

Limit of the second: two requests can coincide on the test data by chance. We test on a **realistic** basis and we check the limit cases.

---

Why does a good score on Spider not predict the success of a text-to-SQL on a corporate warehouse? <!--anki:6976465b5b7c3160683e-->
?
- **Spider** (2018): varied but simple bases, now saturated
- **BIRD** (2023): larger and **sales** bases, necessary business knowledge
- **Spider 2.0** (2024): real enterprise workflows (BigQuery, Snowflake), hundreds of column diagrams; success rates remain much lower

The difference between these benchmarks is a reminder that a public score does not predict the result **on its own basis** ([[146-model-selection|choice of model]]).

Build local cases with tax dates, cancellations and one-to-many joins. A query can run without error while doubling the turnover: compare the business result, not just the syntax or the absence of exception.

---

How should a text-to-SQL system handle an ambiguous question? <!--anki:62717d725e7e684b387b-->
?
"March sales": what year, what scope, gross or net turnover? Options:
- **Ask for clarification** when ambiguity strongly changes the result
- **Apply a documented convention** (last full year, net sales) and **display it** in the response
- **Show the query** or its translation into natural language, so that the user can verify what has been calculated

A false figure presented with assurance is worse than a question of clarification ([[143-hallucinations-grounding|abstention]]).

---

Why is LIMIT not a representative sample for validating a text-to-SQL? <!--anki:6337346239313835376561633466663038303239616635643966326461323562-->
?
A **LIMIT** retains a subset whose order may depend on the plan and storage. The first lines can represent a single period or a single client, without covering cases that vary the response.

Validate the query on controlled sets containing limit cases, multiple joins and missing values, and then on the relevant population. If a statistical sample is needed, define its method and its strata. Adding an ORDER BY stabilizes a selection, but does not automatically make it representative or correct for an overall aggregate.

---

Why can a join double a total in a text-to-SQL generated query? <!--anki:3630346365353337613433383466386539333031316637656130373133373162-->
?
A relationship **One-to-many multiplies lines** before aggregation. Attach an order of 100 € three lines produces three occurrences of the amount; `SUM(montant_commande)` returns 300 €.

Define the grain of each table and preaggregate to the expected grain, or aggregate the right measurements. `SUM(DISTINCT amount)` is not a general repair: two different orders can have the same amount. Test with known cardinalities and compare to reference totals.

---

How can NULL values distort an executable text-to-SQL response? <!--anki:3762653638613565366531373465343739363839623732636538326662303862-->
?
**NULL represents an unknown or absent value**, not zero. `COUNT(*)` counts rows; `COUNT(colonne)` ignores NULLs. `AVG(colonne)` also ignores these values, which changes the denominator.

On three invoices of 10, 20 and unknown amount, the average of the known amounts is 15, not 10. The system must specify the calculated population and choose a business policy for absences. Replacing all NULLs with zero would invent information.

---

## Scenarios

Scenario: the sales manager wants to "ask questions at the natural language data warehouse". The warehouse has 300 poorly documented tables. How do you frame the project? <!--anki:48286c646f7b7a5a404e-->
?
1. **Reduce the scope**: one domain (sales), a dozen documented business views, not the 300 tables
2. **Rely on the semantic layer** if it exists, so that the numbers stick to the dashboards
3. **Build the eval game**: 100 real business questions with their expected result, in execution accuracy
4. **Secure**: Read-only, reply, row-level security, timeouts and budget per request
5. **Make it verifiable**: Display the query, applied filters, and selected conventions

**Pip**: plug the LLM into the entire warehouse and let the trade discover false figures in committee.

---

Scenario: your text-to-SQL wizard has 85% execution accurency in test, but users complain about numbers "that don't stick". What are you looking for? <!--anki:76553f3b417169662447-->
?
1. **Collect reported cases** with the question, query and number expected by the user
2. **Sort gaps**: poor business definition (gross or net CA), forgotten implicit filter (test clients, cancellations), ambiguous period, real SQL error
3. **Correct at source**: column descriptions, example question → SQL, metrics in the semantic layer
4. **Add these cases to the eval game**, which did not reflect the real questions ([[153-data-flywheel-versioning|flywheel]])
5. **Display conventions** applied in each response

**Trap**: Change model when the error comes from business definitions missing from the prompt.

---

## Sources

- [Spider 2.0 — author's benchmark](https://spider2-sql.github.io/)

- Supplement of the 14 November 2026 — Joints, cardinalities and aggregations: [PostgreSQL 18 — table expressions](https://www.postgresql.org/docs/18/queries-table-expressions.html).

## Connections
- [[145-system-design-cases|Case of system design]] — Data Analysis Assistant as an Architecture Case
- [[21-rag-fundamentals|RAG — Fundamentals]] — text, when SQL is not suitable
- [[23-knowledge-graphs-ontologies|Knowledge graphs]] — Text2Cypher, the same problem on a graph
- [[32-tool-calling|Tool calling]] — Expose SQL Execution as a Tool
- [[101-llm-security-guardrails|LLM Security]] — generated query is untrusted entry
- [[96-evals-rag-agents|Evaluation of GARs & Agents]] — measure on its own questions
- [[143-hallucinations-grounding|Hallucinations & grounding]] — clarify rather than invent
- [[150-010-analytical-data-modeling|Modeling of analytical data]] — make allowable joins and metrics explicit
- [[150-011-analytical-sql-transformations|SQL for AI Pipelines and Datasets]] — validate the meaning and results of SQL
- [[00-moc-ai-engineering|MOC AI Engineering]]
