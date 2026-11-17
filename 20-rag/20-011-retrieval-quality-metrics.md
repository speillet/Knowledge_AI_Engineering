# Retrieval quality metrics — Flashcards
Tags: #flashcards #ai-engineering #rag #retrieval #evaluation #ranking
<!-- summary: evaluation contracts and qrels, precision and recall denominators, reciprocal rank and MRR@k, AP@k and MAP@k conventions, worked ranking comparisons, graded nDCG, missing judgments, duplicates, evidence coverage, ANN versus relevance recall, candidate and reranker diagnosis, paired comparisons, permissions and context budgets. -->


## Define the evaluation contract

What must be fixed before comparing retrieval quality metrics? <!--anki:3466313836326235613034393436653639613861326535366364646163623138-->
?
Define the **query set, corpus snapshot, relevance judgments and cutoff**, then specify the evaluation unit: document, passage or distinct evidence item.

A relevance judgment, or **qrel**, links a query ID to an item ID and a relevance label. Keep IDs stable across runs. Record eligibility rules, deduplication, tie-breaking and the treatment of queries without relevant items.

For example, document-level judgments cannot fairly score two chunkers by counting every overlapping chunk as a different success. A metric becomes interpretable only when its denominator and evaluation population are reproducible.

---

When a retriever returns fewer than k results, what does precision@k divide by? <!--anki:3966353030303966346165663435376439613164626539646330626639353931-->
?
Under a **fixed-cutoff convention**, precision@k divides the number of relevant results by **k**. An alternative, precision over returned results, divides by the number actually returned. Name the convention explicitly.

If k = 5 and only two passages are returned, both relevant, the scores are **2/5 = 0.4** and **2/2 = 1.0**, respectively. The latter measures selection purity; it hides unused capacity.

Report the number returned as well. Neither score tells you whether all evidence needed for the answer was retrieved; assess coverage separately.

---

Why must retrieval recall use an eligible relevance set? <!--anki:6261623830376536373861633430626538663030313965346561353637383433-->
?
For a given query, recall divides relevant retrieved items by the **relevant items that the system is allowed and expected to retrieve**.

Suppose five passages match the topic, but only three are current and authorized for this user. Retrieving those three yields eligible recall **3/3**, not 3/5. Returning a revoked document is a policy failure, even if it improves an unfiltered score.

Keep the evaluation identity, effective date and corpus version with the qrels. Report authorization violations separately so an aggregate relevance score cannot hide them.

---

How should retrieval evaluation handle queries with no relevant evidence in the corpus? <!--anki:3936363764363831303139383465646438396537633332636334383939313337-->
?
When **R = 0**, recall and total-relevant AP involve division by zero. An evaluator may define their score as zero or exclude these queries; neither convention should be hidden.

First distinguish genuinely absent evidence from incomplete annotations. Report answerable and no-evidence queries separately, with their counts. On the latter, assess irrelevant context selection and whether the complete system appropriately abstains.

Keep answerable queries with zero retrieved hits in the retrieval average: they are failures, not undefined cases. Otherwise, a system can appear better simply by failing on difficult questions.

---

## First relevant result

How is reciprocal rank computed for one retrieval query? <!--anki:6565636333653834386365343461303061366537653934353462646632373139-->
?
**Reciprocal rank**, RR, is `1 / rank` of the **first relevant result**, with ranks starting at 1. RR@k is zero if no relevant result appears within the top k.

For relevance labels `[0, 0, 1, 1, 0]`, the first useful passage is third: **RR@5 = 1/3**. The fourth result does not change RR. If the first relevant result were sixth, RR@5 would be zero even though an untruncated ranking finds it.

RR measures how quickly retrieval finds one useful item; it cannot establish complete evidence coverage.

---

Do not confuse: reciprocal rank and mean reciprocal rank? <!--anki:3561616365326662313863643430323538353830636464383465653932373261-->
?
**RR@k** scores one query. **MRR@k** is the arithmetic mean of those scores over the declared query set:

```text
MRR@k = sum(RR@k(q) for q in queries) / number_of_queries
```

Queries with relevant evidence but no retrieved hit contribute **zero**. Removing these failures inflates the result. Queries with no relevant evidence anywhere need a separate, explicit policy because there is no first relevant rank to find.

MRR is useful when finding one authoritative result is the main objective. For questions requiring several sources, pair it with coverage or MAP.

---

Do not confuse: reciprocal rank as a metric and reciprocal rank fusion? <!--anki:3436356633303933313333663433353162303862313962393862616435386161-->
?
**RR/MRR** evaluate rankings using relevance judgments. **Reciprocal Rank Fusion**, RRF, combines ranked lists without requiring those judgments during fusion.

RRF assigns a document contributions such as `1 / (c + rank)` from each input list, where c is a smoothing constant. Its fusion score is neither a relevance probability nor an MRR score.

For example, hybrid retrieval may fuse lexical and vector results with RRF, then use MRR, MAP and recall on held-out qrels to assess whether that fusion helps. Changing c is a retrieval choice, not a change in the definition of MRR.

---

## All relevant results

What does average precision at k reward, and which denominator does this topic use? <!--anki:6239356239353065326433633463303939303166336261626631616433316163-->
?
**AP@k** rewards retrieving relevant items early while accounting for relevant items missed. This topic uses the **total-relevant denominator**, R:

```text
P@r = number of relevant items in ranks 1..r / r
AP@k = sum(rel(r) * P@r for r = 1..k) / R
```

`rel(r)` is 1 for a relevant result, otherwise 0. R counts all judged relevant items in the evaluation universe. Relevant items beyond k contribute zero to the numerator.

Unlike ordinary precision@k, AP considers order. If R exceeds k, AP@k cannot reach 1 under this convention, even with a perfect prefix.

---

Calculation: a query has three relevant passages in total, found at ranks 1, 3 and 5. What is AP@5 using the total-relevant denominator? <!--anki:3036366539646639396330383433383661393433336438356236616231303763-->
?
Only relevant ranks contribute:

```text
P@1 = 1
P@3 = 2/3
P@5 = 3/5
AP@5 = (1 + 2/3 + 3/5) / 3 = 34/45 ≈ 0.756
```

Recall@5 is 1 because all three relevant passages were found, but AP@5 is below 1 because irrelevant results delayed two of them. With the same passages at ranks 1, 2 and 3, AP@5 would be 1.

This comparison assumes distinct passages, binary relevance and complete judgments for the three relevant items.

---

Why can two implementations disagree about AP@k while both follow their documented formula? <!--anki:3233613037616331313564393436323938336166646539383162366164343031-->
?
They may use **different normalizers**. Besides division by total relevant items R, a cutoff-normalized variant divides by `min(R, k)`. A retrieved-only denominator answers a different question again.

For R = 5, k = 3 and labels `[1, 1, 0]`, the numerator is `1 + 1 = 2`. Division by R gives **0.4**; division by `min(R, k)` gives **0.667**.

Publish the formula and a tiny checked example with the score. Do not compare dashboards solely because both say “MAP@k”; also verify duplicate handling and queries without relevant items.

---

What is MAP@k, and why should it not be called an average of precision@k scores? <!--anki:6463363935366236326533643439616238323761333734616136626438306565-->
?
**Mean Average Precision at k** first computes **AP@k for each query**, then averages those AP values:

```text
MAP@k = sum(AP@k(q) for q in queries) / number_of_queries
```

A mean of ordinary precision@k scores does not account for order within each result list, so it is not MAP@k. “MAPs@k” is usually an informal spelling; the standard abbreviation is **MAP@k**.

Each query gets equal weight in the usual macro average. A traffic-weighted mean is possible, but its weights and evaluation population must be reported.

---

Calculation: three queries have AP@5 values of 0.75, 0.25 and 0. The third has relevant evidence but retrieves none. What is MAP@5? <!--anki:3861623632363338663964613463626361313164656334323034363432313366-->
?
Include the failed query:

```text
MAP@5 = (0.75 + 0.25 + 0) / 3 = 1/3 ≈ 0.333
```

Averaging only successful queries gives **0.5**, incorrectly hiding the complete retrieval failure.

This example uses a macro average: every query has equal weight. Pooling retrieved documents across the three queries changes the estimand and can let queries with many relevant documents dominate. Preserve per-query scores so you can examine failures and compare systems on the same queries.

---

Calculation: three documents are relevant. At k = 5, retriever A has labels [1,0,0,0,0] and B has [0,1,1,1,0]. How do RR and AP compare using R = 3? <!--anki:3130626636316163393961383462373539623561343062666664393464326261-->
?
```text
A: RR@5 = 1;   AP@5 = 1/3 ≈ 0.333; recall@5 = 1/3
B: RR@5 = 1/2; AP@5 = (1/2 + 2/3 + 3/4) / 3 ≈ 0.639
   recall@5 = 1
```

A wins on the first useful result. B wins on the distribution and coverage of relevant results. Neither metric contradicts the other: they reward different retrieval behaviors.

For a question requiring all three documents, A's perfect RR is insufficient. Choose the evaluation objective from the information need, not from whichever metric makes a preferred system win.

---

When do AP and reciprocal rank coincide? <!--anki:3365326639306239336634373433636261353932653934643764326131393462-->
?
With **exactly one relevant item**, both equal `1 / rank` if that item is within the cutoff, otherwise zero. Thus MAP@k and MRR@k coincide on a query set with one relevant item per query, under matching conventions.

With several relevant items, AP accounts for additional relevant ranks while RR ignores everything after the first hit. Equality on a one-answer benchmark therefore does not make the metrics interchangeable for multi-document RAG.

Check the number of relevant items and whether the qrels annotate all valid evidence or just one convenient answer location.

---

## Graded relevance and evidence coverage

Why use nDCG when retrieval relevance has several grades? <!--anki:3562343566323133653339613432333738323239663038653830633039383035-->
?
**nDCG@k** compares a ranking's discounted relevance gain with that of an ideal ranking of the same judged items. It can distinguish a directly answering passage from merely useful background.

```text
DCG@k = sum(gain(rel(r)) / log2(r + 1) for r = 1..k)
nDCG@k = DCG@k / IDCG@k
```

State the gain function, such as `2^grade - 1`; linear gains are another convention. IDCG uses descending grades. A zero IDCG needs an explicit handling policy.

A high nDCG does not prove that all required facts are covered or that the generator uses them correctly.

---

Calculation: the judged universe contains three items with grades [3,0,2], retrieved in that order. With gain 2^grade − 1 and discount log2(rank + 1), what is nDCG@3? <!--anki:3664643337333136633239393431313661313166343535333566313833383734-->
?
The ideal order is `[3, 2, 0]`:

```text
DCG@3  = 7/log2(2) + 0/log2(3) + 3/log2(4) = 8.5
IDCG@3 = 7/log2(2) + 3/log2(3) + 0/log2(4) ≈ 8.893
nDCG@3 = 8.5 / 8.893 ≈ 0.956
```

The ranking contains all judged useful results, yet delaying the grade-2 result lowers its score. Different gain functions produce different numerical values; report the chosen convention instead of comparing this result with a dashboard using linear gains.

---

Why can high passage recall still miss the evidence needed for a RAG answer? <!--anki:3961333937646439353139363436613561623966353631666439613133333239-->
?
Passage counts do not express **which facts or combinations of evidence are necessary**. Several relevant passages may repeat the same fact while another required fact is absent.

For a comparison requiring price and cancellation terms for two plans, four retrieved passages about one plan's price are not four independent requirements satisfied. Annotate required evidence groups or subquestions and measure their coverage under the actual context budget.

Also allow alternative valid evidence sets. Requiring one exact passage ID can unfairly penalize another passage that establishes the same fact.

---

How should duplicate or overlapping chunks be treated in retrieval evaluation? <!--anki:3435333533313863633738343464306461656432626437316534656130633237-->
?
Choose a unit and deduplication policy **before** scoring. Repeating one relevant document at several ranks must not count as discovering several distinct relevant documents.

Chunk-level evaluation can still hide redundancy: multiple overlapping chunks may all be relevant but add no new evidence. Report unique-source or evidence-group coverage alongside chunk metrics and context tokens.

If two chunking strategies produce different numbers of chunks, consider document-level judgments or stable evidence spans. Otherwise one strategy can appear better merely by splitting the same answer into more counted items.

---

How do missing relevance judgments distort MAP and MRR? <!--anki:6539633263663363376531633433633838333332303361636539396136646263-->
?
An **unjudged** result is not necessarily irrelevant. Treating every unjudged passage as zero relevance can penalize a retriever that discovers valid evidence outside the annotation pool.

For example, a new retriever puts a valid but unjudged passage first; the reported RR may become zero although a human finds the answer immediately. Record judgment coverage and inspect disagreements between systems.

Expand the judgment pool using diverse retrievers and adjudicate a blinded sample. Keep the evaluation convention fixed; silently discarding unjudged results can also change ranks and make comparisons misleading.

---

Do not confuse: ANN recall and relevance recall in a RAG pipeline? <!--anki:6263626461623032613065353461376162633763636463623636306335373632-->
?
**ANN recall** measures how well an approximate nearest-neighbor index recovers the neighbors produced by an exact search with the same vectors and similarity function. **Relevance recall** measures retrieval against evidence judged useful for the query.

An approximate index can recover every exact neighbor while those neighbors are semantically wrong: ANN recall is 1, but relevance recall is poor. Conversely, a missed exact neighbor may have an equally useful substitute.

Use ANN recall to diagnose index approximation; use qrels, evidence coverage and answer evaluations to judge the application.

---

Why evaluate candidate retrieval, reranking and final context separately? <!--anki:3930383063643438663734643437366139623837646362303131643437303932-->
?
Each stage can lose evidence. Measure **candidate recall** before reranking, **ranking quality** after reranking and **evidence retained** after filtering, deduplication and token-budget packing.

If the required passage never enters the candidate pool, a reranker cannot promote it. If it reaches rank 2 but the context builder drops it, changing embeddings will not fix the immediate problem.

Store IDs and scores at each boundary. Compare the final context under the same token budget; top-10 chunks can represent very different amounts of text across chunkers.

---

How should two retrieval systems be compared beyond their mean score? <!--anki:6666626565643564373937353430643238353332303334663530323062613430-->
?
Use the **same queries and qrels**, inspect per-query score differences and report uncertainty using an appropriate paired procedure. Group related queries or templates when resampling to avoid treating near-duplicates as independent.

Break down results by meaningful slices such as rare terminology, multi-document questions and access restrictions. Freeze the final test set while tuning parameters on development queries.

Include latency, context tokens and failure rates. An increase in mean MAP can hide regressions on critical queries or require an unacceptable retrieval budget.

---

## Scenarios

Scenario: your dashboard reports MRR@10 = 0.98, but comparison answers omit half the requested facts. What should you investigate? <!--anki:3664353864333131343639663434386538633938333663323863343135313234-->
?
1. **Inspect the task**: identify whether answering requires several distinct facts or sources.
2. **Read the qrels**: check whether they mark only one convenient passage per query.
3. **Measure coverage**: add AP/MAP and required-evidence coverage under the actual prompt budget.
4. **Trace context construction**: inspect truncation, deduplication, filters and selected chunks.
5. **Evaluate generation separately**: compare answers using retrieved context and complete reference context.

**Trap**: assuming that finding the first relevant passage proves the whole answer is supported.

---

Scenario: one evaluator reports MAP@3 = 0.4 and another reports 0.667 on the same result list. How do you resolve the discrepancy? <!--anki:3762353133333764616539343432636262616262313039623261653236316663-->
?
1. **Freeze one query**: use five relevant items in total and top-three labels `[1, 1, 0]`.
2. **Recompute the numerator**: relevant ranks contribute `1 + 1 = 2`.
3. **Inspect denominators**: division by five gives 0.4; division by `min(5, 3)` gives approximately 0.667.
4. **Check other conventions**: duplicates, tie-breaking, empty qrels and unjudged results.
5. **Publish a shared metric contract** and rerun both systems before interpreting the difference.

**Trap**: tuning retrieval to reconcile two differently defined metrics.

---

Scenario: a reranker improves MAP@10 but doubles latency and reduces answer completeness. How do you decide whether to deploy it? <!--anki:3433666237313734336663623462303639333035613437396330336231633266-->
?
1. **Confirm comparability**: same queries, corpus, labels, cutoff and eligibility filters.
2. **Trace stage losses**: inspect candidates, reordered passages and the context actually sent to the model.
3. **Check evidence diversity**: high-ranked passages may repeat one fact while crowding out another.
4. **Compare under a fixed token and latency budget**, with paired answer evaluations.
5. **Apply release criteria** for completeness, critical slices and latency; revise or reject the reranker if these fail.

**Trap**: treating a ranking metric as the complete product objective.

---

## Sources

Review of 17 November 2026: metric definitions, normalization conventions and diagnostic examples. Numerical examples are synthetic and independently calculated.

- [Manning, Raghavan and Schütze — evaluation of ranked retrieval](https://nlp.stanford.edu/IR-book/html/htmledition/evaluation-of-ranked-retrieval-results-1.html).
- [ir_measures — AP, RR, nDCG and cutoff parameters](https://ir-measur.es/en/latest/measures.html).
- [NIST trec_eval — implementation of cutoff average precision](https://github.com/usnistgov/trec_eval/blob/main/m_map_cut.c).
- [Apache Spark — ranking metrics implementation, including the min(R, k) AP normalizer](https://github.com/apache/spark/blob/master/mllib/src/main/scala/org/apache/spark/mllib/evaluation/RankingMetrics.scala).
- [Cormack, Clarke and Büttcher — Reciprocal Rank Fusion](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf).
- [Faiss — evaluating approximate search against exact neighbors](https://github.com/facebookresearch/faiss/wiki/Getting-started).

## Connections
- [[21-rag-fundamentals|RAG fundamentals]] — where retrieval fits into the pipeline
- [[22-advanced-rag|Advanced RAG]] — hybrid retrieval, RRF and reranking
- [[96-evals-rag-agents|RAG and agent evaluation]] — generation, faithfulness and end-to-end outcomes
- [[134-vector-search-ann|Vector search and ANN]] — approximation recall versus relevant evidence
- [[20-010-rag-permissions-versions|Permissions and versions]] — eligible evidence and invalidated documents
- [[174-recommendation-ranking|Recommendation and ranking]] — related ranking objectives and exposure bias
- [[00-moc-ai-engineering|MOC AI Engineering]]
