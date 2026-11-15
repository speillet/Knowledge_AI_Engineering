# Context engineering — Flashcards
Tags: #flashcards #ai-engineering #agents #context-engineering #llm
<!-- summary: context as budget, context rot, compaction, sub-agents, prompt caching, context loaded as needed (just-in-time), compaction invariants, context selection, reserve budget. -->


What is context engineering? <!--anki:6d7964697b53773a6a7e-->
?
The art of **choose, at each call, the minimum set of tokens most useful** in the context window: instructions, tools, history, memory, recovered documents.

It is important to keep what allows the next decision: objective, constraints, evidence and progress. For example, replace a long execution log with a summary of results with links to details. The goal is not to blindly reduce the tokens: removing an important exception can cost more than a slightly longer context.

---

Do not confuse: context engineering and prompt engineering? <!--anki:267e45776566756838-->
?
The **[[11-advanced-prompt-engineering|prompt engineering]]** optimizes the **formulation** of an instruction; the **context engineering** handles **everything that enters the context**, over the duration of a session or agent.

Rewriting “summarize this contract” in precise instructions is a matter of prompt engineering. Selecting the right version of the contract, loading its annexes, keeping the user constraints and summarizing the previous rounds is a matter of context engineering. An excellent instruction does not compensate for a missing or outdated source: it is necessary to work on both levels.

---

Why treat the context window as a budget? <!--anki:6565374d7c3f655b753c-->
?
Each token **costs** (price, latency, VRAM of the [[61-kv-cache-attention|KV cache]]) and **dilutes the attention**: the bigger the context, the less the model exploits each information.
```text
Budget of an agent round (example):
  system prompt              600 tokens   stable → cached
  12 definitions 2,400 tokens stable → cached tools
  Memory and Preferences 300 tokens
  Recovered documents 3,000 tokens variable
  historical (8 turns) 4,500 tokens continuously grows ← to compact
  question                    120 tokens
                           ──────────────
                          ~10,900 tokens per call, including reusable 70%
```
The position that grows on its own is the **Historical** He is the one who is compacted first.

Also reserve space for **response and future tool results**. The part actually hidden depends on a prefix compatible with the mechanism of the provider: "reusable" does not imply "cache hit". Compacting the history by keeping decisions, constraints and references; losing an authorization or a critical result can cost more than saving a few tokens.

---

What is context rot? <!--anki:493a7c686b5f307c324d-->
?
**Performance degradation when the context is extended**: conflicting old information, accumulated noise, [[22-advanced-rag|« lost in the middle »]] effect. A large window is not a well-used context.

Identifying symptoms: forgetting a constraint, repeating a search, or using an old value. Reducing the results of redundant tools, keeping an explicit state, and reloading the source if necessary. Comparing success before and after compaction, because too aggressive a summary can also remove decisive information.

---

What are the components of an agent's context? <!--anki:6b38662a4c5f6b385871-->
?
- **Instructions** (system prompt)
- **Definitions of tools**
- **History** of conversation and tool results
- **Memory** (continued facts)
- **Knowledge Retrieved** ([[21-rag-fundamentals|RAG]])

Each component has a function: define the task, make the actions possible, keep the progress or bring facts. The documents and results of tools remain **data to examine**, not confidence instructions. Also reserve enough space for the model output and for observations of the next round.

---

What is the context compaction of an agent? <!--anki:6e5f505d713a4b7b5677-->
?
**Summarize the history** As we approach the limit, to leave with a shorter context that keeps decisions, status and ongoing tasks. Light variant: **Clear old tool results**.

Two side effects: it **invalidates the cache from the first modified token** and **loses details**. The previously unchanged prefix can remain reusable. Keep critical facts out of context ([[39-agent-memory|Memory]]).

Example of a useful summary: objective, validated decisions, references to evidence, remaining work and unresolved errors. Verify that a hypothesis has not become a fact in passing.

---

Do not confuse: compaction, truncation and memory? <!--anki:7229785e5a41372d3b28-->
?
- **Troncature**: we **cut** the oldest messages. Free, but we lose everything that is cut, including decisions made
- **Compaction**: we **summarize** the history. Costs a LLM call, keeps the essentials, but loses the details and invalidates the cache
- **Memory** A: On **Writing out of context** Durable facts, and we reread them on demand. The only solution that survives the session

The three combine: memory for what must last, compaction to hold the session, truncation as a last resort.

---

How do sub-agents help manage context? <!--anki:4f7d3b7869655a2c734e-->
?
A [[36-agent-orchestration|Sub-agent]] explores in **its own context** and returns a targeted result: the principal does not ingest all its searches.

For example, delegating the boundary identification of a API to a "limit, condition, reference, uncertainty" return, rather than a general summary of the provider.

Separation reduces the bulk of the main context, **not necessarily the total tokens or the delay**. Avoid redundant missions and delegations that require to retransmit all the history; limit question, tools and return format.

---

Why keep a stable prompt prefix? <!--anki:4e48317c44305d665b56-->
?
To take advantage of the **prompt caching**: the provider reuses the calculation (KV cache) of an identical **prefix**. We put the stable content (instructions, tools) **at the beginning** and the variable content **at the end**.

A timestamp or variable identifier placed before the instructions can prevent their reuse. Measure the tokens actually read in cache, because the thresholds, retention periods and rates depend on the provider. The cache speeds up a part of the input calculation; it does not dispense with generating the new response or checking its quality.

---

What is the just-in-time context? <!--anki:6a6c3e4a7c636c713068-->
?
Do not load everything in advance: give the agent light **references** (file paths, queries, search tools) and let him **recover information when he needs it**.

For example, provide the index of a repository and then read only the files concerned. This saves context and avoids working on old copies, provided that the tools allow a reliable search. Keep the exact references and versions consulted; otherwise the agent can search for a long time or re-read a source that has changed.

---

What happens if the context of an agent exceeds the model window? <!--anki:6435353066396565386132663436363262613562303131313639303632356336-->
?
Depending on the API and its configuration, the request is **rejected or truncated**. Not dependent on an implicit deletion that could remove instructions or evidence.

The Harness must **book the exit and compact before the limit**. Example: A total window of 32,000 tokens, with 4,000 reserved for the generation, Leave at most 28,000 for all entrances, Tools included. Add a margin and measure the actual count. Quality can deteriorate before saturation: keep objective, decisions and useful sources, not only to keep the text ([[137-long-context|long context]]).

---

How do I verify that a compaction keeps the necessary information for an agent? <!--anki:6666353138343263643833373438366638616236346465316337373135373131-->
?
Define **invariants to preserve**: common objective, constraints, validated decisions, proof references and operations still uncertain. Compare these elements before and after compaction over long sessions.

Test a recovery that requires an old fact, a user refusal and the identifier of an operation already executed. Keep the authorization rules in the application control and the durable facts in a suitable storage. A good reformulation of the summary is not enough: measure success and absence of repetition of effects after recovery.

---

Why can loading all tool results in context reduce the reliability of an agent? <!--anki:3561363434313836306434663432613262653062303131313334386239633239-->
?
Each result consumes budget and can **dilute useful evidence** or introduce unreliable instructions. The presence of information in the window does not guarantee its correct use.

Keep a faithful summary with references, then load the details on demand. Do not summarize the numbers or constraints whose accuracy is required without access to the original. Evaluate the answers after this selection, including cases where a rare exception changes the decision.

---

Calculation: an agent has a window of 32,000 tokens, 6,000 tokens fixed, 14,000 history and reserve 4,000 for output. What place is left for tool results? <!--anki:6365636234373061643263313435613062356436623936653764386635363161-->
?
There remains **32,000 − 6,000 − 14,000 − 4,000 = 8,000 tokens** in this counting convention.

A result of 12,000 tokens therefore requires pagination, selection or compaction before the next call. Provide a margin for new messages and possible schemas. The calculation assumes that the output shares this ceiling; the input and output limits can be distinct depending on the model and the API.

---

## Scenarios

Scenario: your support agent gives good answers at the beginning of conversations, then degrades and contradicts itself after an hour. What do you do? <!--anki:463a55674e31642c4634-->
?
1. **Recognize context rot**: the context has inflated, old and contradictory information accumulates
2. **Compact**: summarize history by keeping decisions, status, and tasks in progress; remove old tool results
3. **Getting the facts out of the way** to a read-on-demand memory ([[39-agent-memory|Memory]])
4. **Just-in-time**: Give references and let the agent get what he needs, rather than preload everything
5. **Measure**: Context length, quality and cost per turn over the course of the conversation ([[93-monitoring-inference|monitoring]])

**Trap**: switch to a very large window model without changing anything. The problem is the **quality** of the context, not its size.

---

Scenario: your assistant costs twice as much as expected, while the system prompt and tool definitions are the same for each call. Which track? <!--anki:6a563d5e6c7b32533143-->
?
1. **Check for prompt caching**: Is the prefix really stable, or do you insert the date, session ID, or reordered tools?
2. **Reorganize**: stable content (instructions, tools) at the beginning, variable content at the end ([[123-aggressive-caching|caching]])
3. **Measure** the rate of tokens read cached in traces, before and after
4. **Reduce** what is sent in each turn: unnecessary tools, documents recovered too many
5. **Monitor** cost per conversation, not just per call ([[122-finops-llm|FinOps]])

**Trap**: Add the full history to the prompt header, which invalidates the cache on each turn.

---

Scenario: your agent needs to analyze 300 pages of technical documentation to answer a specific question. How do you organize its context? <!--anki:6b6b564f527c422b5958-->
?
1. **Don't load everything**: 300 pages saturate the context, are expensive and dilute attention
2. **Search first**: RAG or search tool to retrieve only useful passages ([[21-rag-fundamentals|RAG]])
3. **Sub-agents**: if several sections need to be explored, each one works in its own context and only goes back to a summary ([[36-agent-orchestration|Subagents]])
4. **References rather than content**: give the table of contents and targeted reading tools
5. **Quote** the passages used, to check the answer

**Strap**: cut mechanically into 10 calls without memory between them, and lose the thread of reasoning.

---

## Sources

- [Anthropic — Context Management and Agent Compaction](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents) — targeted deepening of the 12 November 2026; educational examples are built for this review.

- 14 November 2026 — Position and context selection: [Liu et al. — Lost in the Middle](https://arxiv.org/abs/2307.03172).

## Connections
- [[11-advanced-prompt-engineering|Prompt engineering]] — the prompt in its global budget
- [[22-advanced-rag|Advanced RAG]] — placement of chunks
- [[31-agent-fundamentals|Agents]] — agent working memory
- [[61-kv-cache-attention|KV cache]] — the memory cost of context
- [[36-agent-orchestration|Orchestration multi-agents]] — isolates contexts
- [[34-harness-plugins|Harness]] — that assembles the context
- [[39-agent-memory|Memorandum of agents]] — long-term memory in detail
- [[123-aggressive-caching|Caching agressif]] — design context for cache
- [[137-long-context|Long context]] — lost in the middle, longueur effective
- [[121-inference-costs|Inference costs]] — cost structure and unit economics
- [[13-production-prompts|Prompt in production]] — structure, versioning and portability of prompts
- [[132-tokenization|Tokenisation]] — what a token is and what it costs
- [[43-langchain-agents|LangChain — Agents]] — agents and middleware LangChain
- [[45-langgraph-production|LangGraph — Production]] — persistence, recovery and human supervision
- [[49-coding-agents|Code Agents]] — Use and Integrate Code Agents
- [[115-agent-platforms-governance|Agent Platforms — Governance]] — identity, policies, audit and costs of a fleet of agents
- [[90-014-agent-skill-evaluation|Evaluating Agent Skills]] — check that a skill loaded as needed really serves
- [[90-015-agent-skills-format-skills-ref|Agent Skills & skills-ref]] — the cost of the skills catalog in context
- [[00-moc-ai-engineering|MOC AI Engineering]]
