# Workshop: verifiable RAG

This workshop diagnoses a documentary system before adding an LLM. A fictional corpus of ten passages and ten annotated cases compares a deliberately incorrect baseline with a policy that respects tenants, groups, effective dates, withdrawals and source authority.

It uses only the standard library of **Python 3.10 or newer**, without API, GPU or installation. The ranking is lexical and deterministic; the facts structured, annotated by hand, replace extraction and generation. The scores are those of this simulation, not performance measured on a model.

## Run from the repository root

```bash
# Predict results before reading solutions.
python3 examples/verifiable-rag/rag_workshop.py --questions

# Compare the two policies on the ten cases.
python3 examples/verifiable-rag/rag_workshop.py

# Inspect each claim and write a report outside the repository.
python3 examples/verifiable-rag/rag_workshop.py --case current --json /tmp/rag-current.json

# Observe a retrieval budget that hides a contradiction.
python3 examples/verifiable-rag/rag_workshop.py --case conflict --k 1

# Run tests for permissions, time validity and evidence changes.
python3 -m unittest discover -s tests -p 'test_rag_workshop.py' -v
```

The commands also work from another directory if the script path is absolute: the data is loaded next to the script. No file is written without `--json`; the report destination directory must already exist.

## Data and policy

- [corpus.json](corpus.json) contains simulated identities, passages, their versions, effective dates, groups, and annotated facts. An identity belongs to a tenant; a document requires the same tenant **and at least one authorized group**.
- [cases.json](cases.json) sets the requested fields, relevant evidence and expected results. These references are only used for evaluation; the resolver only looks at the retrieved passages.
- [rag_workshop.py](rag_workshop.py) applies the policy and produces the trace: passages and versions, affirmations, quotes, reasons for abstention, violations and metrics.

The report also contains SHA-256 fingerprints of the normalized contents of the corpus and of the executed cases, including expected annotations. They change if a fact or a reference changes, even without renaming the snapshot. Keep the input files with the report: a fingerprint makes it possible to recognize the contents, not to reconstruct it.

Validity follows `[valid_from, valid_until)`: on 1 November, the version at 45 days replaces the one at 30 days. The rights are those of the simulated identity at the time of access, even for a historical question. Chunk identifiers are unique in the snapshot; the full identity of a document also includes its tenant.

In this fictitious domain, contracts have an authority of 2 and the FAQ of 1. For each field, the resolver retains the maximum authority among the recovered proofs. Two values incompatible with this authority produce `conflict`. The absence of proof produces `no_evidence`. The answer is `complete`, `partial` or `abstain` depending on the fields solved.

The baseline takes the first passages of the global ranking and the first value found, without filter or conflict management. The `filtered` variant filters the corpus before ranking and applies the business priority. The score is the number of common distinct words after normalization; the equalities are separated by chunk identifier. This choice facilitates reproduction, without simulating BM25 or embeddings.

## Cases to Diagnose

| Case | What it checks |
| --- | --- |
| `current` | Old version, adversarial FAQ and applicable contract |
| `historical` | Business date passed with current permissions |
| `date-boundary` | Excluded terminal and new effective version |
| `authorized-finance` / `unauthorized-finance` | Same question, different permissions |
| `other-tenant` | A generic question finds the proof of the authenticated tenant |
| `conflict` | Two contracts of the same authority contradict each other. |
| `no-evidence` | No source contains the requested fact |
| `partial` | Two resolved fields and an explicitly reported missing element |
| `withdrawn-source` | A chunk still present in the snapshot is blocked after removal |

With the corpus delivered and `k=4`, `filtered` complies with **10 out of 10 contracts**, with zero out-of-scope passages. The baseline complies with **0 out of 10** and exposes 20 out-of-scope passages in total. A contract also requires that **all context** be admissible: the baseline may fail even if its final response appears to be correct.

## Read metrics without confusing their denominators

| Scope of the report | Definition |
| --- | --- |
| `precision_returned` | Relevant evidence retrieved/separate passages actually returned; if less than k results exist, the denominator is not k |
| `recall_at_k` | Relevant evidence retrieved/relevant evidence annotated |
| `reciprocal_rank` | Inverse of the rank of the first relevant evidence, or 0 if none is recovered |
| `citation_support` | Links that support exactly the fact and are allowable/links issued; deduplication within an assertion |
| `claim_support` | Affirmations with at least one supporting link/affirmations made |
| `expected_coverage` | Expected items properly resolved and supported/answerable items expected |
| `requested_coverage` | Expected items correctly resolved and supported / all fields requested |
| `unexpected_claims` | Number of declared fields that are not in expected items |

A null denominator gives **`null` in the JSON and `n/a` in the terminal**. Abstention without citation does not get support from 100%. Cases without evidence have an undefined recall; the adversarial case has two relevant passages even if no single value is expected. The ratio does not arbitrarily average these populations.

The `partial` case reaches 100% from `expected_coverage` but only **2/3 from `requested_coverage`**: the element without proof remains requested. In the case of `conflict`, the baseline obtains 100% from citation support while incorrectly answering "4 hours": the cited document contains this value, but another source of the same authority contradicts it.

## Switch to variations and produce a deliverable

1. **Change the current fact** on a copy of the corpus: the response must change. Without updating the reference, the contract must fail; this reveals the change instead of masking it.
2. **Withdraw all evidence from a field**: the response becomes partial or abstains. Withdraw only the contract can leave the FAQ as proof: decide if the business policy should still accept it.
3. **Reduce `k` to 1 on `conflict`**: the second proof disappears, the system asserts a value and fails the contract. A resolver cannot detect a conflict that it has not recovered.
4. **Withdraw Bruno's finance group** on a copy: the search and access to citations must lose the private proof. The workshop simulates a new request; adding a cache would also require testing its revocation.
5. **Change a validity limit**: check the answers immediately before, at the time and after the change, then check the references that have become inapplicable.

Deliverable: a JSON report, a `question | affirmation | passage/version | verdict | cause | correction` table, and a short decision on priority of sources and abstention. To succeed, explain a search failure, a faithful but unjustified response and a difference between coverage of the responsive elements and coverage of the entire request.

## Limits and extension to a real RAG

Identity is a trusted fixture, **not actual authentication**. The workshop does not model changing permissions during a query, physical purge, caches, response flows, free formulations, historical availability of documents, or an ANN engine. The exact equality of annotated facts does not replace a semantic check on natural texts.

To move to a real pipeline, replace the retriever and generator while retaining cases, references, and trace. Annotate support for free assertions, control missing evidence, and then add load, cost, and revocation during execution. The numerical authority of this example must be replaced by a business rule tailored to the topic.

The effect of filters on an approximate index must be measured with the actual engine; pgvector 0.8.1 document the filtering after index scan and iterative scans. [Documentation pgvector 0.8.1](https://github.com/pgvector/pgvector/blob/v0.8.1/README.md#filtering).

The indicators of support and coverage are a pedagogical adaptation of the distinction studied by Liu, Zhang and Liang they do not reproduce their annotation protocol. [Evaluating Verifiability in Generative Search Engines](https://arxiv.org/abs/2304.09848).

To read: [RAG and rights/versions](../../20-rag/20-010-rag-permissions-versions.md), [RAG Assessment](../../90-observability-evals/96-evals-rag-agents.md), [Construction of Corpus](../../150-data-compliance/150-017-ai-datasets-corpora.md) and [Learning Guide](../../docs/guides/learning-with-flashcards.md).

[All workshops](../README.md)
