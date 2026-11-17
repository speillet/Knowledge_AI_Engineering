# RAG in production: rights, versions & abstention — Flashcards
Tags: #flashcards #ai-engineering #rag #security #data #retrieval
Verified on: 13 October 2026
<!-- summary: identity and permissions, pre-exposure filtering, recall under filters, time validity, source priority, deletions and caches, versioned citations, abstention and regression tests, revocation of rights during generation, proof of absence, consistency of snapshots. -->


Why is the relevance of a RAG passage not enough to use as proof? <!--anki:3961663861303264376631323462373538363333643236643561653032313563-->
?
A passage must be **relevant, authorized and applicable**. Similarity does not prove the right to read it, its validity on the requested date, or its authority.

Fictive example: a 2024 scale may be the correct proof for an order of 2024, but not for a current order. Conversely, the most recent document is not always the one applicable to the historical case. Verify identity, contractual scope and validity period before exposing the changeover to the model. Then check that it **specifically supports the assertion**, rather than simply dealing with the same subject.

---

Where should the holder and permissions of a RAG request come from? <!--anki:3361633361656338643265623466663462396334613936633231333336376166-->
?
From **authenticated identity context**, verified by the application and its authorization system. The arguments produced by a model or a free field of the request are not proof of belonging to an tenant.

The service infers the accessible perimeter and applies it to searches, document uploads, and citations. Example: The tool exposed to the model is `rechercher(question)`, and the server itself adds `tenant` and groups from the token. A question that names another company remains within the authorized perimeter. Rights must also be rechecked when a conversation resumes after a change of permissions.

---

Why isn't enabling PostgreSQL security per line enough to isolate a RAG? <!--anki:3538636266303636643666323433643238386436373061653731613032333365-->
?
The **Superusers and Roles `BYPASSRLS`** bypass that security; the owner of the table normally bypasses it too, except for appropriate configuration such as `FORCE ROW LEVEL SECURITY`.

Test requests with the **role actually used by the service**, its permissions and policies, rather than with an administrative account. Line security protects access covered by these policies; it does not automatically control copies already present in an external cache or the context of the model.

---

Do not confuse: filter RAG candidates and hide a response after generation? <!--anki:6666646239353432613336333461663662353834383931333463643065646433-->
?
**Filtering candidates** prevents prohibited content from reaching the model, external rerankers and caches exposed to the user. **Hide response** occurs after these components have already received or reused the information: if a third-party hosted reranker has received 50 candidates including six prohibited HR documents, masking the response does not cancel this sending.

An internal search can examine candidates and then filter them within a controlled trust boundary. The safety criterion is that there is no unauthorized exposure; it does not impose a universal physical order on all search engines.

---

Why can a global top-k followed by a filter degrade the RAG recall? <!--anki:3839393638336435303865393435336362646463303064646638373733356163-->
?
Prohibited documents can **occupy the top k places**. Removing them leaves few results while authorized evidence exists further.

Search the eligible subset, increase candidate budget, or use an iterative search by engine. In pgvector with approximate index, the filter is applied after the index scan; from version 0.8, `SET hnsw.iterative_scan = relaxed_order` continues this scan until it gets enough eligible lines **or reaches its course limits**. Measure recall under real filters. Expand search should never expand permissions.

---

Calculation: a RAG ranking places four prohibited documents before two authorized proofs. We take three candidates then filter, or we filter the whole corpus then take three results. Each authorized proof is relevant. How much proof and what reminder do we get? <!--anki:3634616431666432663664303465333738363638383530623566613663656634-->
?
**Top-3 then filter: zero proof**, so `recall = 0/2 = 0 %`. **Filter then top-3: two proof**, so `recall = 2/2 = 100 %`; only two eligible documents exist.

An approximate index may still lack evidence after the restrictions have been applied. It is necessary to measure its recall and cost, rather than infer a guarantee from the presence of a filter.

---

How to represent the temporal validity of a RAG document version? <!--anki:3039303833663566313231323439626439313039383736613930333430613461-->
?
Keep a **business interval**, e.g. `[valid_from, valid_until)`, separate from the date of ingestion. A version is applicable if `valid_from <= date_question < valid_until`; an absent end terminal means that no end is saved.

This choice makes it explicit to switch between two contiguous versions. For a historical question, apply the requested date; for a current question, use a controlled reference date. Permissions remain the user's at the time of access, even if the question is about the past.

---

Do not confuse: date of ingestion and date of effect of a RAG document? <!--anki:3434303262623835663439663465333961623766303764336165653838306362-->
?
The **ingestion date** indicates when the pipeline received the document and the **effective date** indicates when its contents apply to the trade.

A policy published today may come into effect next month. A document received late may describe a rule that is already applicable. Automatically choosing the last ingested file confuses these two temporalities. To replay what the service knew at a past date, also keep the availability of the document in snapshots: business validity alone is not enough.

---

How to resolve two conflicting RAG sources without arbitrarily choosing the most recent one? <!--anki:3964633038636337343033343435373539303231356461316336336535356135-->
?
First check **perimeter, rights, and effective date**, and then apply a documented business rule to the authority of the sources: for example, contract applicable before informative FAQ.

The priority depends on the subject; a similarity score is not an authority. In the `examples/verifiable-rag` workshop, a contract has an authority of 2, the FAQ of 1. If two sources of the same authority remain incompatible, do not merge their values: report the allowed uncertainty or ask for clarification. Keep references for diagnosis, without exposing sources prohibited to the user.

---

What should a RAG citation identify to remain verifiable after an update? <!--anki:6432653264373763633264643439346562343238323064323961656364656538-->
?
The **document, its version and the passage used**. A URL to "the current version" may display tomorrow a text different from the one that supported the answer.

Keeping a chunk identifier linked to a version or fingerprint, and a verifiable location in the source: `politique-retours@v4/chunk-07`, with the SHA-256 fingerprint of its standard text, remains verifiable when v5 appears. The resolution of the citation must control the current rights. A fingerprint identifies content; it does not prove its truth, its applicability, or the permission to disclose it.

---

Why is removing a document from the source not enough to remove it from a RAG? <!--anki:3535316263393961333330303432333761643365633934653262333237646233-->
?
Derived **copies** can remain accessible: chunks, embeddings, summaries, response caches, and conversation context.

Spread a withdrawal or revocation to the affected consumers, immediately block new exposures according to the service contract, and then verify the purge of persistent copies. A withdrawal mark can prohibit reading during the reconstruction of the index: in the case of `withdrawn-source` of the RAG workshop, the chunk remains in the snapshot but is never exposed again. It does not guarantee on its own the physical deletion of all copies or answers already received.

---

How to prevent a RAG response cache from bypassing a rights revocation? <!--anki:3166616632303562663964313438666161623865376138323137313131333934-->
?
Associate entries to the **perimeter of authorization**, source versions, and policy used. Example: The key includes a version number of the user's rights, incremented with each withdrawal, making its old entries untraceable. Alternatively, recheck access to evidence when serving an entry.

A question-only cache can share a response between two users of different rights. A key per user also does not resolve a change in its rights. A lifetime limits exposure over time; it does not provide an immediate revocation.

---

Calculation: a RAG cache retains a private response to 10 h 00 for 15 minutes. A right is removed to 10 h 04; no invalidation or reverification exists. Until when can the cache expose the response and what is the maximum remaining window? <!--anki:3835326532303461366463363435373461343339376432626631643865303266-->
?
The entry expires at **10 h 15**. The remaining window is `15 - 4 = 11 minutes`, for readings served before expiration.

This implies a fixed expiration from insertion, with no extension at each read and no other copy. The TTL does not replace a revocation mechanism. A invalidation or a reverification of the permissions to the response service reduces this window according to its own deadlines and guarantees.

---

How to distinguish between useful abstention and search failure in a RAG? <!--anki:6430613537383432633665653464373338393938393466386538636561623664-->
?
Annotate if an authorized and applicable **evidence exists in the reference corpus**. If it exists but is not retrieved, the abstention protects the response while revealing a failure of the retrieval. If it does not exist or remains contradictory, an asserted response may be unjustified.

Example: on 100 questions, 70 have a proof; refraining on 30 of which 10 answerable reveals 10 failures to diagnose and 20 justified abstentions. If the proof was recovered, look for the error on the generation side rather than retrieval. Follow reminder, success, unjustified answers and abstention. Any refusal can minimize errors while making the service unusable.

---

How to evaluate a partial RAG response without rewarding the omission of difficult questions? <!--anki:3366616362633138393063323464376161306561663063303137613939383530-->
?
Define them in advance **requested items**, then measure their coverage and support of the claims made. Example: the question is about delay, fees and return channel; the answer correctly cites the first two and says "channel: no evidence found", or a cover of 2 on the 3.

For each missing element, distinguish between missing evidence, conflict and unrecovered evidence. In a corpus without evidence for an element, an explicit partial response may respect the contract; in a fully answerable case, the same omission is a failure of completeness. The denominator must not depend solely on what the system chooses to say.

---

What corpus changes should trigger a RAG regression? <!--anki:3437396338373639613439363465333561626538333332383131626532373462-->
?
**Updates, deletions, rights changes, and processing changes.** Check for responses on a replaced version, a date boundary, two ins, two roles, and a removed source.

Add counterfactual tests: pass in a copy of the corpus the contractual delay from 30 to 60 days, then remove this fact. The answer must follow the modification, then become partial or abstain; `tests/test_rag_workshop.py` checks these two variations. Versionner corpus, questions and results to distinguish an expected evolution of a search or generation regression.

---

Why can an authorized proof at the beginning of a RAG task become unusable before its response? <!--anki:6539326538393637363436393436626161393465366239363130613034326534-->
?
**Rights can change during execution**: leaving an employee, changing a group or removing a document. A verified permission to search is not a valid permission indefinitely.

For sensitive data, recheck access before retrieving and before any external effect, according to an explicit policy of freshness. Combine evidence and caches with identity and policy version. Test a revocation for a long generation. A response already displayed cannot be withdrawn retroactively by a simple final check.

---

When can a RAG claim that no document contains information? <!--anki:3133393031306264656362633431303962646166363363336235633935663039-->
?
An empty top-k search only proves that **this search did not find anything**. An absence statement requires an explicit scope and sufficient coverage: authorized corpus, period, versions and complete index.

For "no unpaid invoices", an exhaustive query on a structured registry is better than a semantic search. If the coverage is unknown, formulate "no evidence found in the sources consulted". Distinguish in the metrics actual absence, lack of access and indexation failure.

---

Why should the index, metadata, and texts of a RAG share a consistent version? <!--anki:3637316138303530343961663434653439353535333663316331636338383766-->
?
A vector calculated on version A can point to a text B whose meaning or rights have changed. The engine then finds **a representation that no longer corresponds to the proof displayed**.

Building an identifiable snapshot, validating references and then switching visibility. Maintaining version identity during search and generation. This does not exempt from rechecking common permissions: document consistency and right of access are two distinct conditions.

---

## Scenarios

Scenario: a support assistant answers "refund under 14 days" while the current contract says 30 days; the FAQ to 14 days was re-ingested yesterday. How do you diagnose and correct the problem? <!--anki:3761663539396461613832623464333938306135626664363733656239303366-->
?
1. **Trace the passages actually used**, their versions and their effective dates.
2. **Control the scope** of the contract and FAQ for the question asked.
3. **Apply an explicit business priority**; the last ingestion does not establish authority.
4. **Replay the question** on the current date and on a historical date.
5. **Invalidate assigned responses** and add these cases to regressions.

**Trap**: Increase top-k without changing the selection of applicable evidence.

---

Scenario: an employee loses a financial right, but still receives a private response from the RAG cache. How do you handle the incident and check the correction? <!--anki:3437326663313765376437343464386338303465333066643466316364343732-->
?
1. **Block assigned entries service** and recheck the access perimeter.
2. **Identify the copies concerned**: replies, passages, quotes and preserved context.
3. **Propagate the revocation** according to the contract and withdraw the exposable entries.
4. **Replay with the same user before and after revocation**, then with another role and another hold.
5. **Measuring the revocation period** and verifying direct access to citations.

**Trap**: only correct the search while the cache bypasses this search.

---

Scenario: a RAG abstains from 40% questions and displays 100% valid citations. What measures make it possible to decide if it is useful and reliable? <!--anki:3837386235386632303363653439383061363734613061653639633038326239-->
?
1. **Separate answerable cases from cases without evidence or conflicting** in an annotated game.
2. **Measure recall on answerable cases**, with rights and representative dates.
3. **Check for support for assertions**, beyond the validity of links.
4. **Measure completeness and unwarranted responses**, including abstention.
5. **Compare to a baseline** based on business criteria, latency, and cost.

**Trap**: infer reliability from the mere presence of clickable quotes.

---

## Sources
- [PostgreSQL 18 — security policies by line and privileged role limits](https://www.postgresql.org/docs/18/ddl-rowsecurity.html)
- [pgvector 0.8.1 — filtering and iterative path of approximate indexes](https://github.com/pgvector/pgvector/blob/v0.8.1/README.md#filtering)
- [Liu, Zhang and Liang — citation support and coverage](https://arxiv.org/abs/2304.09848)

- [PostgreSQL — Security by Policy Line and Perimeter](https://www.postgresql.org/docs/current/ddl-rowsecurity.html) — targeted deepening of the 12 November 2026; educational examples are built for this review.

## Connections
- [[22-advanced-rag|Advanced RAG]] — apply filters and selection rules to passages
- [[96-evals-rag-agents|Evals RAG]] — distinguish research, evidence and response quality
- [[150-017-ai-datasets-corpora|Datasets & corpus IA]] — identify documents, versions and transformations
- [[123-aggressive-caching|Caching]] — prevent caches from bypassing freshness and rights
- [[20-011-retrieval-quality-metrics|Retrieval quality metrics]] — AP/MAP, RR/MRR, relevance judgments and evidence coverage
- [[00-moc-ai-engineering|MOC AI Engineering]]
