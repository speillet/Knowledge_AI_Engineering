# Search agents (deep research) — Flashcards
Tags: #flashcards #ai-engineering #rag #agents #deep-research #llm
Verified on: 30 September 2026 — This factsheet lists products, versions or regulatory texts that are evolving quickly.
<!-- summary: RAG or search agent, search loop, parallel subagents, search tools, reliable citations, risks (sources, injection, bias), evaluation (coverage, BrowseComp), calculation of the cost of a report, when not to use it, independence of web evidence, coverage of assertions, search stop criterion. -->


What is a deep research agent? <!--anki:315f783362537c352a-->
?
An agent that **plans and adapts a search**: formulate sub-questions, consult sources, explore gaps and then produce a cited summary. The number of queries and duration depend on the task and budget, not a threshold defining "deep research".

For example, comparing two standards requires finding their texts, dates of application and exceptions, then resolving contradictions. The report must link each conclusion to the evidence and distinguish established facts and uncertainties. Multiplying the pages read does not guarantee independence of sources or coverage; ten times of the same press release remain a single origin.

---

Do not confuse: RAG classic and search agent? <!--anki:6d437d676a3c354d443e-->
?
- **RAG** : **a** research, top-k passages, An answer. Fast and cheap, but limited to what the first request finds ([[21-rag-fundamentals|RAG]])
- **Search Agent**: **loop** of queries that depend on what has already been read, on many sources, with summary. Covers questions **opened or multiple jumps**, but costs 10 to 100 times more

between the two, the **Agentic RAG** : some research decided by the model ([[22-advanced-rag|Advanced RAG]]).

---

How does a search agent's loop work? <!--anki:4c7b53673262534b5173-->
?
1. **Clarify** the question, sometimes by asking the user
2. **Plan**: break down into sub-questions
3. **Search and read**: queries, selection of results, reading of useful pages
4. **Evaluate**: what is missing, what contradicts? Then new requests
5. **Edit** the report, each statement related to its source

The stop is decided on **sufficient coverage** or **exhausted budget**.

Keep a `sous-question → preuve → uncertainty` matrix. Ten pages with the same dispatch do not cover ten independent points. With an exhausted budget, distinguish the substantiated conclusions from the open questions.

---

Why do search agents often use multiple agents? <!--anki:4831403a517c48356826-->
?
Because the search is **parallelized** well: an orchestrator launches **subagents** on independent sub-questions, each with its own context, which return only a **summary**. Anthropic reports a significant gain of its multi-agent system on an agent alone, at the price of about **15 times more tokens** than a chat ([[36-agent-orchestration|orchestration]]).

To reserve for questions **large**: for a narrow question, only one agent is sufficient.

---

What kind of tools to give a search agent? <!--anki:6a416525792b62536b65-->
?
- **API web search** designed for agents (cleaned results, relevant snippets), or model vendor-integrated web search
- **Page recovery** that returns clean text, not plain HTML
- **Internal search**: Document index, SharePoint, tickets, via [[33-mcp|MCP]]
- A **Working Memory** (Notes, list of sources read) to not reread the same page

Results **Short and dense** more than the number of tools ([[49-coding-agents|ACI]]).

---

How to make quotes from a report reliable? <!--anki:77332e51657671396742-->
?
- Attach **every statement** to a specific passage from a read source, not just a URL
- Have the statement verified, by a separate call, that the **passage supports** the claim
- Report conflicting **sources** instead of silently choosing one
- Prefer them **Primary sources** (Study, official text) on the occasions

A quote to a page that doesn't say what it's being loaned is worse than none ([[143-hallucinations-grounding|citations]]).

---

What specific risks does a research officer pose? <!--anki:435a7b2d2f7670487140-->
?
- **Unreliable or AI-generated sources** cited as authorities
- **Prompt injection** by the pages read, which can guide the synthesis or try to exfiltrate ([[102-agent-threats|threats]])
- **Confirmation fields**: the agent looks for what confirms his first hypothesis
- **False completeness**: a long and quoted report gives an impression of complete coverage

Hence authorized or prioritized sources, and a report that says **what hasn't been found**.

---

How to evaluate a search agent? <!--anki:50402c6137552b754438-->
?
- **Accuracy** on questions with verifiable answers, including questions **difficult to find** (benchmarks like BrowseComp)
- **Coverage**: share of expected key points in the report, listed by an expert
- **Citation fidelity**: Is each statement supported by its source?
- **Cost and duration** compared to

A **calibrated judge** rating covers and quotes; accuracy is verified by reference ([[96-evals-rag-agents|evals d'agents]]).

---

Calculation: 5 sub-agents read 15 pages of 4,000 tokens each; assume those tokens sent twice, plus 100,000 tokens orchestration input. At 3 €/M, what is the cost of input versus, excluding tools and outputs? <!--anki:7332246760345a2c3f25-->
?
The invoice volume includes the re-sent pages and the orchestration:
```text
lecture initiale = 5 × 15 × 4 000 = 300 000 tokens
read sent twice = 600,000 tokens
= 600,000 + 100,000 = 700,000 tokens
entry cost = 700,000 / 1,000,000 × 3 € = 2.10 €
```
This rate is **fictive**; the result excludes outputs, tools and possible cache write costs. It does not assume any cache discount. To compare in-depth research and RAG, report the cost to a useful answer: a more expensive report may be relevant if its additional coverage meets the need.

---

When not to use search agent? <!--anki:777e6c2d5123333b7074-->
?
- **Simple factual question**, to which a RAG or a single search responds
- **Latency expected in seconds**: support chat, voice assistant
- **Corpus closed and small**, which fits in the context
- **Commitment decision** without human review of the report

He serves the questions **Open, large and high value** and watch, due diligence, State of the art.

Compare to a simple search on the same questions: the extra cost must buy better coverage or additional verification. Multiplying the sources without solving the contradictions adds time and noise.

---

Why can ten matching web pages represent only one independent proof? <!--anki:3937643765346534316538323465366262303866373765623131346262306332-->
?
Several pages can **copy the same dispatch, study or press release**. Their number then measures the dissemination of an affirmation rather than its independent corroboration.

Go back to the original source, group the reprints and distinguish between declaration of an actor and independent verification. For a controversy, also look for contradictory elements and specify the date of the facts. Keep the chain of provenance in the research notes. A synthesis must not transform ten copies of an unverified assertion into ten confirmations.

---

How to build a proof-affirmations matrix for a research report? <!--anki:3733376164663634363230393435643638633936303530623264386536626234-->
?
Associate each **Important affirmation** from a specific source, A passage, date and status: supported, contradicted or not resolved. This makes conclusions without proof and decorative quotations visible.

Distinguishing fact reported and agent deduction. For a deduction, keep the premises and its limits. The matrix must cover the issues of the warrant, not just the easy-to-find facts; an accessible source can nevertheless be secondary or outdated.

---

When should a search agent stop searching despite unresolved questions? <!--anki:6335353537646438326237343430343862343166316361396639633631313934-->
?
Stop when the **budget is reached** or new searches no longer provide useful evidence, according to a rule defined in advance. Record requests already tried, sources covered and uncertainties remaining.

A successful stoppage can produce a reliable partial report. Repeating the same search with paraphrases is not progress. For a critical decision, forward the unresolved point to a human; lack of budget does not justify supplementing with an assumption.

---

## Scenarios

Scenario: the legal team wants an agent who prepares regulatory watch notes from the web and the internal documentary database. How do you conceive it? <!--anki:6e2c4d595d2f65235548-->
?
1. **Sources**: official texts and institutional sites in priority, internal base via a search tool, list of trusted domains
2. **Architecture**: plan validated by the lawyer, sub-agents by sub-question, final drafting with quotations in passing
3. **Verification**: separate check that each passage supports the assertion, reported contradictions
4. **Security**: web content treated as unreliable, no writing or sending tools ([[103-agent-defenses|Defenses]])
5. **Assessment**: 20 questions already handled by the team, scored on cover and citation fidelity

**Trap**: Present the report as complete, while the agent only read what his queries found.

---

Scenario: your search agent produces good reports, but costs 8 € and 25 minutes per question, and users use it for simple questions. What do you do? <!--anki:45436375787a3d634c5f-->
?
1. **Measure** the distribution of questions: simple, average, really open
2. **Router**: RAG or single search for simple questions, agent only for others ([[82-routing-llm|routing]])
3. **Budget**: Maximum number of sub-agents, pages and tokens per question
4. **Reuse**: caches pages already read and recent reports on the same topic ([[123-aggressive-caching|caching]])
5. **Show** the duration estimate before starting a thorough search

**Trap**: Reduce the budget for everyone, and degrade the issues that justified the agent.

---

## Sources

- [Anthropic — multi-agent search system architecture](https://www.anthropic.com/engineering/multi-agent-research-system)

- [W3C — PROV provenance model](https://www.w3.org/TR/prov-overview/) — targeted deepening of the 12 November 2026; educational examples are built for this review.

## Connections
- [[21-rag-fundamentals|RAG — Fundamentals]] — search in one go
- [[22-advanced-rag|RAG — Advanced]] — agentic RAG and ranking
- [[36-agent-orchestration|Orchestration multi-agents]] — orchestrator and subagents
- [[143-hallucinations-grounding|Hallucinations & grounding]] — citations fiables
- [[102-agent-threats|Threats to agents]] — injection by the pages read
- [[96-evals-rag-agents|Evaluation of RAG systems & Agents]] — measure coverage and fidelity
- [[165-computer-use-browser-agents|Browser Agents]] — when searching requests to browse
- [[00-moc-ai-engineering|MOC AI Engineering]]
