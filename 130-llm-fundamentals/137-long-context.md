# Long context — Flashcards
Tags: #flashcards #ai-engineering #fundamentals #long-context #llm
<!-- summary: RoPE extension, lost in the middle, needle in a haystack and RULER, context rot, long context or RAG, cost, serving techniques, output limit, task test, proof reconciliation assessment, evidence position, useful length. -->


What is the context window? <!--anki:6d7324252c743d7a6c7d-->
?
The **Maximum number of tokens** (input + output) that the model processes into a query. It ranges from tens of thousands to **More than a million** of tokens according to the models. An advertised window is not automatically A guarantee that the model **Operates** All this content.

The budget also includes **instructions, history, and tool diagrams**, not just the document provided. If the input takes up almost all the capacity, it may run out of room for output or an additional tool result. See separate model and service boundaries, and then set a margin for the task.

---

How do I extend the context window of a model? <!--anki:513e6d3c793a695b673c-->
?
Especially by adapting the position encoding **[[131-transformer-architecture|RoPE]]**: **position interpolation**, **NTK-aware scaling**, **YarN** — is "stretching" the rotation angles to cover more positions — then an additional **training on long sequences**. Some models also combine attention **local (slippery window)** and **global**.

Changing the scale of positions is not enough to demonstrate a good use of long sequences. Evaluate information retrieval, reasoning between remote passages and quality on short contexts after extension. A sliding window reduces some costs but restricts direct dependencies; the capabilities obtained depend on the architecture and training associated.

---

What is the phenomenon "lost in the middle"? <!--anki:723c2f282b7629302f5a-->
?
Models make better use of the information placed **at the beginning and end** of the context than the information placed **in the middle**. Recent models mitigate this, but the practical rule remains: **put the instructions and key elements at the ends** and limit noise ([[35-context-engineering|context engineering]]).

The phenomenon depends on the model and the task, especially when it is necessary to find information among distractors. Moving a passage while keeping the same question makes it possible to measure this sensitivity. Do not assume that a repeated instruction at the ends corrects everything: filtering unnecessary passages and testing several positions remains necessary.

---

What is the "needle in a haystack" test and what is its limit? <!--anki:6666417e472b57515f29-->
?
Hide a precise **phrase** in a long text and ask to find it. Most recent models succeed almost perfectly — but it is a task of **simple tracking**. More demanding benchmarks (**RULER**, multi-needles, reasoning on several passages, followed by variables) show an effective **length** often much less than the announced window.

Testing multiple positions and plausible distractors. Finding a contract number does not prove that you know how to combine your clause with an exception located elsewhere. Evaluate recovery and reasoning on evidence separately.

---

Long context or RAG? <!--anki:4f3c556b3e682f4e3b40-->
?
The **long context** is suitable for a limited set of documents when their global relationships count; the **RAG** selects useful passages in a larger or changing corpus.

Example: Comparing all the clauses in two contracts may justify their full loading; finding the applicable record among thousands requires first a selection.

Both approaches require access rights, provenance and citation tests. Holding everything in the window does not guarantee the exploitation of every detail. Measuring omissions, cost and delay; the [[123-aggressive-caching|prompt caching]] reduces certain costs, not errors of attention or selection.

---

What is the cost of a long context to inference? <!--anki:6f402e3c566b7770777e-->
?
- **Prefill**: Dense attention has a quadratic length component; the total cost also depends on the other layers and the cache.
- **KV cache**: Generally linear memory in retained positions → less simultaneous requests.
- **Price**: depends on processed tokens, cache rates and possible milestones ([[121-inference-costs|costs]], [[61-kv-cache-attention|KV cache]]).

Double the context does not necessarily double the delay or the invoice. Measure TTFT, memory and cost with cold prefixes then reused; a large context accepted by the API can remain impractical at the target rate.

---

What techniques reduce the cost of the long context side serving? <!--anki:66435d6f36567a3b6255-->
?
**Prefix caching** (Reuse the KV of a common prefix), **Chunked prefill**, **Quantification of KV Cache**, **Offloading** the Cache to CPU or SSD, Attention to **Sliding Window** or hybrid, and **Parallelism of context** (Cut the sequence between GPU) — see [[66-prefix-caching-radix-attention|prefix caching]].

These techniques do not work on the same workstation: caching avoids a repeated calculation, the prefill chunked better shares the GPU time, and quantization reduces the cache volume. Offloading adds transfers; local attention changes what the model looks at. Check compatibility, quality and latency before combining them.

---

Do not confuse: Input limit (context window) and output limit? <!--anki:6b3d3026794e255e4b21-->
?
The **Maximum output** (max output tokens) is generally **much smaller** the window (a few thousand to a few tens of thousands of tokens), And the generation is **Sequential** So slow. Producing a long document **Cut** generation (plan and sections).

Check if the service imposes a **shared total budget** and a separate output terminal. An accepted input of 100,000 tokens does not necessarily allow an output of the same size. When generating by sections, keep a common plan and references, and then control consistency and omissions; splitting can introduce repetitions and contradictions.

---

How do I test if a model handles its long context on my task? <!--anki:6c59292359433b455432-->
?
Construct an eval where we make **variate the length of the context** and the **position** of the useful information, with realistic **distractors** drawn from his corpus, and plot the quality according to the length. We deduce a **safe working length** to respect in the application ([[94-evals-methodology|evaluation methodology]]).

Maintain the difficulty of the question and the necessary proofs comparable between lengths. Add cases where several passages must be combined, because finding a single sentence does not test all the understanding. Report errors, cost and latency by position and length; the workstation chosen also depends on the business tolerance to failures.

---

Why doesn't finding information in a long context prove that a model can reconcile several? <!--anki:6237333161663733326535383433666562636337363336313634646166616536-->
?
The **recovery of an isolated fact** tests a different ability to reconcile multiple evidence, compute, or resolve contradictions.

Build cases requiring two remote passages, an applicable version and a plausible distractor. Varying their position and the number of documents by keeping a verifiable reference. Measuring the accuracy and coverage of the necessary steps. A model can find each amount separately and produce a false total. Success on a single needle does not justify removing retrieval, structuring or business verification.

---

How to measure the really useful context length for a task? <!--anki:3036633738666338316566353463316661633161356334386430373933663138-->
?
To vary **length, position of evidence, and amount of distractors**, while maintaining a verifiable response. Include multiple pieces of evidence to combine, not just a string to find.

Trace quality, cost and latency according to these axes. The maximum accepted window indicates a technical limit; it does not guarantee a uniform quality. Hold the budget where the task meets its criteria, possibly with retrieval or context selection.

---

Why does high precision on a single needle not prove the ability to sum up a long file? <!--anki:3339643232366631363935643466626139343837356364633236646165613939-->
?
Finding an isolated fact requires less than **covering multiple themes, resolving contradictions and prioritizing evidence**. The summary may omit important elements despite a good one-off search.

Test coverage of decisions, fidelity and exceptions on representative documents. Compare the complete result to a structured grid. A location benchmark remains useful, but its success should not be generalized to all long tasks.

---

## Scenarios

Scenario: a product manager wants to remove the RAG and “put everything in context”, since the model accepts one million tokens. What do you answer? <!--anki:432957427b36502e3f52-->
?
1. **Distinguish window advertised and effective length**: models degrade well before the limit, except on the simple identification of information
2. **Cost**: each call rebills the entire context, with a quadratic prefill and therefore a high TTFT ([[121-inference-costs|costs]])
3. **Functional constraints**: citations, access control per document, freshness of data remain the responsibility of the RAG
4. **Mixed approach**: the RAG selects, the broad context is used to reason on the selection
5. **Measure**: vary the length and position of useful information about your own cases

**Trap**: Validate the idea with a "find this sentence" test, which does not prove the ability to reason on the whole.

---

Scenario: your contract analysis assistant becomes slow and expensive as soon as documents exceed 200 pages. Which levers, application side and serving side? <!--anki:4437756d4641515e533a-->
?
1. **Application side**: do not load everything, recover useful sections, summarize upstream, cut the generation in plan then sections
2. **Prompt caching**: if the same contract is scanned several times, a stable prefix avoids repaying the prefill ([[123-aggressive-caching|caching]])
3. **serving side**: prefix caching, chunked prefill, quantization of the KV cache ([[66-prefix-caching-radix-attention|prefix caching]])
4. **Limit output**: the generation limit is much lower than the window, and the decode is sequential
5. **Fix a safe working length**, deducted from the measurements, and adhere to it in the product

**Trap**: increase the allowed window without measuring the effect on quality and concurrency held by GPU.

---

## Sources

- 14 November 2026 — Position and context selection: [Liu et al. — Lost in the Middle](https://arxiv.org/abs/2307.03172).

## Connections
- [[35-context-engineering|Context engineering]] — manage context budget
- [[61-kv-cache-attention|KV cache & attention]] — memory cost
- [[66-prefix-caching-radix-attention|Prefix caching]] — re-use long prefixes
- [[21-rag-fundamentals|RAG]] — The Long-Context Alternative
- [[131-transformer-architecture|Architecture Transformer]] — RoPE and Attention
- [[13-production-prompts|Prompt in production]] — structure, versioning and portability of prompts
- [[36-agent-orchestration|Orchestration multi-agents]] — subagents, handoffs and A2A
- [[64-inference-metrics-slo|Metrics & SLO]] — TTFT, TPOT, flow rate and percentiles
- [[68-quantization|Quantization]] — reduce accuracy to gain memory and speed
- [[00-moc-ai-engineering|MOC AI Engineering]]
