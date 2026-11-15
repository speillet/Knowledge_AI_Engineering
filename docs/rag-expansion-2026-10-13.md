# Deposit Enrichment — 13 October 2026

The repository already largely covers models, agents, inference, data, and their exploitation. The learning path and previous reviews show a need for **reproducible practice**: knowing how to recite a rule is not enough to diagnose a pipeline result.

This pass realizes the RAG workshop proposed in the [The Review of 11 October](relevance-review-2026-10-11.md). It adds a specialized topic and connects the exercise to the existing courses.

## State of departure and perimeter

Observed condition: **138 cards, 2,059 cards**, 326 situationalized and 166 confusion cards. Lint and catalogs were compliant. Local changes were already present, including the answer evaluation sheet and the platform path: they are kept.

The gap research focused on the RAG rights, freshness, and assessments organization, routes, relevance review, workshops, and passages, and is not a comprehensive factual review of the pre-existing 138 topics or a measure of learning.

## Additions made

| Ajout | Competence worked | Evidence available |
| --- | --- | --- |
| [RAG: rights, versions and abstention](../20-rag/20-010-rag-permissions-versions.md) | Authenticated identity, filters, effect dates, source authority, citations, withdrawals, and caches | 19 cards, including two calculations, two distinctions and three situational settings |
| [Verifiable RAG Workshop](../examples/verifiable-rag/README.md) | Diagnose research, applicability of sources and final response | Ten Fictional Passages, Ten Annotated Cases, and the JSON Affirmation/Citation Report |
| [Tests of the workshop](../tests/test_rag_workshop.py) | Detect a leak, an incorrect time marker or a misleading assessment | Two-tenant regressions, revoked rights, modified/withdrawn evidence, and masked conflict |
| Integration with the courses | Switching from cards to a validation deliverable | README, MOC, learning guide, 5 stage of the platform journey and four reciprocal links |

Existing cards receive links; their cards and identifiers remain unchanged. Previous verification dates remain. The new card cites the primary sources consulted for this pass.

The pre-publication review confirms that the fact topic deepens the production rules mentioned in the advanced RAG, while the workshop makes them observable without dependence on a model. It reinforces traceability: each report contains the SHA-256 fingerprints of the corpus and of the executed cases. The tests verify that a modification of a fact or reference changes the corresponding fingerprint, even if the name of the snapshot remains the same.

## Educational Outcomes and Limitations

With the supplied corpus and `k=4`, the filtered policy complies with **10/10 contracts**, against **0/10** for the intentionally incorrect baseline. It places zero out-of-scope passes in the context, against 20 occurrences for the baseline. The contract includes the eligibility of the entire context, even when a prohibited pass is ultimately not cited.

The contradictory case shows a response whose citation is supported at 100%, but which erroneously decides between two contracts of the same authority. The partial case shows 100% of coverage of the answerable elements and only 2/3 of the requested elements. Metrics without denominator remain undefined; they do not automatically become successes.

The workshop uses exact lexical ranking and manually annotated structured facts. It does not implement actual authentication, nor does embeddings, nor does LLM, nor does it cache or purge physical. Current rights are simulated, and dates represent business validity rather than historical availability of data. The results describe these constructed cases; they do not guarantee the behavior of an actual service.

## Primary sources and scope

- [PostgreSQL 18 — Row Security Policies](https://www.postgresql.org/docs/18/ddl-rowsecurity.html): Line policies and roles that can bypass them.
- [pgvector 0.8.1 — Filtering](https://github.com/pgvector/pgvector/blob/v0.8.1/README.md#filtering): filtering after an approximate index scan, recall compromise and iterative scan.
- [Liu, Zhang and Liang — Evaluating Verifiability in Generative Search Engines](https://arxiv.org/abs/2304.09848): distinguish between support for quotes and coverage of claims.

Priority policies, business intervals and invalidation procedures are pedagogical choices explained in the topic and the workshop; these references do not alone validate a particular production architecture.

## Next identified priorities

| Priority | Possible improvement | Criteria for success |
| --- | --- | --- |
| 1 | Workshop on tool effects and recovery | Distinguish timeout before/after writing, unknown result and resume without duplicate mutation |
| 2 | Qualification workshop of a judge | Compare human annotations, style, injections and errors by segment, with magazine cover |
| 3 | Catalogue of workshops and deliverables | Find for each course an exercise, its prerequisites, its order and a verifiable result |

These priorities extend existing topics; they are not implemented in this pass. Adding an actual backend to the RAG will have to keep the cases checked, then extend the annotations to free formulations and measure quality, latency, cost and revocation.

## Validation

Results achieved:

- **139 cards, 2,078 cards**, 329 situationalized and 168 confusion cards; zero error and zero lint warning.
- **51 tests passed** on Python 3.12 with pinned dependencies; the 11 tests of the workshop also pass with the Python system 3.9 and its only standard library.
- Compliant catalogues and **348 controlled local links** in the README, MOC, documents and guide of the new workshop.
- Generated Anki export: **2,078 active cards and 30 suspended removed cards**, SQLite database integrates.
- The questions, answers and identifiers of the pre-existing **2,059 cards are kept**, checked against a copy of the initial state.

The verifications concern the format of the maps, their links and identifiers, the catalogs, the workshop and the Anki export.

```bash
python3 scripts/lint_flashcards.py --stale-months 0
python3 scripts/sync_catalog.py --check
python3 -m unittest discover -s tests -v
python3 scripts/export_anki.py
python3 examples/verifiable-rag/rag_workshop.py --questions
python3 examples/verifiable-rag/rag_workshop.py --json /tmp/rag-validation.json
```

The complete suite and the export require the pinned dependencies of `scripts/requirements.txt`; the workshop alone remains usable with the standard library.
