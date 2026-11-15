# Agent Memory — Flashcards
Tags: #flashcards #ai-engineering #agents #memory #llm
Verified on: 25 September 2026 — This factsheet lists products, versions or regulatory texts that are evolving quickly.
<!-- summary: Working memory, semantics, episodic and procedural, thread or long-term, writing during or after the conversation, consolidation, recall score, reflection, changing facts, storage, Letta, tools, risks, evaluation, agent memory or RAG, when not to give long-term memory, distinction between inferred facts and preferences, correction and logical deletion, provenance of memories. -->


Why does an agent need external memory? <!--anki:4771475b312e6378352c-->
?
A LLM is **stateless**: it only knows what is in its context window, limited and expensive. To remember from one session to another (preferences, facts, lessons learned from errors), one **writes out of context** and then **selectively reinjects** what is used for the current task ([[35-context-engineering|context engineering]]).

Save "prefers the answers in French" with its source and user reach avoids rereading the entire conversation. The memory does not update the weights of the model; an unrecovered memory does not participate in the answer.

---

What types of memory are distinguished for an agent? <!--anki:234b3f24393a6b7661-->
?
- **Work**: data of the current task, such as the current cart.
- **Semantics**: facts, such as a confirmed food preference.
- **Episodic**: Location-based experiences, such as a deployment blocked by a quota on a given date.
- **Procedural**: know-how, such as a diagnostic procedure.

These categories describe usage, not four mandatory bases. A quota incident is an experience, **not proof of a permanent limit**. Turning it into a procedure requires validation and careful generalization. For each durable memory, keep provenance, scope, date and possibility of correction; do not automatically promote any conversation in fact established.

---

Thread memory or long-term memory? <!--anki:4f61472d505b28496777-->
?
- **Thread** The History of **a** conversation, charged at each turn (e.g. [[45-langgraph-production|checkpointer]] LangGraph)
- **Long term**: shared **between conversations**, filed by **namespace** (user, team, organization) and retrieved by search (e.g. Store LangGraph)

The thread state allows you to resume a current folder; a durable preference can be reused in a new folder. A namespace organizes the data but does not alone constitute an authorization. Set read rights, retention period and deletion, in particular to prevent a user's information from being recalled to another.

---

When to write in memory: during the conversation or in the background? <!--anki:514f75377d7373513a29-->
?
Writing **during the conversation** makes a memory immediately available, but adds tool call, validation, and delay to the critical path. Writing **in the background** can consolidate exchanges after the fact, with a delay in availability.

Asynchronousness moves the cost; it does not remove it and can create a concurrency with a user fix. For a useful preference right away, write a validated version; for a less urgent synthesis, consolidate later with provenance. Predict conflicts, expiration and resume writing, and then measure latency and recall quality rather than promise free processing.

---

How to extract and consolidate memories? <!--anki:6f2351266f6a21365b2a-->
?
A LLM extracts the **candidate facts**, then compares each to the close memories already stored and chooses: **add**, **update**, **delete** or **ignore** (the operations ADD, UPDATE, DELETE, NOOP of Mem0). Without this consolidation, the memory accumulates **doubles and contradictions**.

An explicit user correction must be able to override an old preference, while an uncertain deduction remains a candidate. Store source, date, and confidence level, and then make operations auditable. Consolidation must not merge memories belonging to two users or automatically propagate an error from an isolated conversation.

---

How to choose souvenirs to remember? <!--anki:6f7862213e5e592d556b-->
?
By an **Combined Score** (popularized by Generative Agents, 2023) :
- **Relevance**: Similarity to request
- **Receiving**: Decreasing over time
- **Importance**: noted in writing

More **filters** (user, memory type). Better **few well-chosen memories** than all the history.

Apply the **access filters** first, then classify the allowed memories. A recent but off-topic memory should not rule out a stable and important constraint. Check also contradictions and validity dates. Evaluate the recall on issues where the good memory is known, counting the unnecessary information added to the prompt.

---

In agent memory, what is reflection? <!--anki:747d5b5b70284a2c677b-->
?
The Agent **periodically synthesizes** raw memories in higher-level conclusions ("the user prefers short answers with code"), or shoots **Lessons** of his failures. It thus transforms episodic into semantic or procedural.

The resulting conclusion remains a **derived hypothesis**, not a user statement. After a SQL query failure, a useful lesson can be "check the column names before execution", with a link to the incident. Validate this rule on other cases before generalizing it; erroneous reflection can maintain the same errors.

---

How to handle facts that change over time? <!--anki:4e5d6777774e4f2e3b52-->
?
**Invalidate rather than overwrite**: Each fact has a **valid window** (how long, how long) and the history is preserved. Time graphs like Graphiti do this automatically. Otherwise, the agent mixes the old address with the new one, or loses track of what was true on a given date.

Distinguish the date the fact is **valid** from the date the system learned it. An address corrected today may have been valid since last week. Requests must specify whether they relate to the current or past state. Keep a history only within the limits of the retention policy and applicable rights.

---

Where to store the long-term memory of an agent? <!--anki:474e52572d285e445668-->
?
- **Vector base**: text memories + embeddings, search by similarity
- **[[23-knowledge-graphs-ontologies|Knowledge graph]]**: entities and relationships, multi-hop requests, time dimension
- **Structured profile** (key-value document): user preferences and attributes
- **Files**: `CLAUDE.md`, or Anthropic's memory tool that reads and writes to a memory directory

First choose the necessary operations: approximate search, current attribute, or time relationship. Keep an authoritative source and stable identifiers to correct or delete copies; multiple storages require a synchronization policy.

---

How does Letta memory (ex-MemGPT) work? <!--anki:65302b6a764f7b402e40-->
?
An approach inspired by **operating systems**: **core memory blocks** remain in context and the agent itself **modifies them** with tools; the memory of **archives** (vector search) and **reminder** (history) remains out of context and is loaded on demand, like pagination.

Content in core memory costs context to each call; archives require a search to become visible. This separation requires choosing what deserves to remain always present, as a lasting constraint. Control the modifications proposed by the agent and keep their origin to avoid that an incorrect inference becomes a permanent preference.

---

Which agent memory library for a simple extraction layer, self-published memory, changing facts, a graph with ontology? <!--anki:3931613663613465373863633435633661313165373434653566323234346263-->
?
- **Memory layer** that extracts and consolidates the facts of the conversations: **Mem0**
- **Memory self-published** by the agent himself: **Letta**
- **Faits that change over time** (validity, history): **Zep / Graphiti**, a time graph
- **Knowledge graph structured by an ontology**: **[[24-cognee|Cognee]]**

Compare these approaches on the same scenario: learn a preference, correct it, recall it in another session and then delete it. Check provenance, isolation and behavior in the presence of contradictions. The choice depends on the life cycle of the information; a richer graph does not guarantee a better recall for simple preferences.

---

Before building an agent memory, what built-in offers to look at depending on whether a framework is used, theAPI from a provider or a platform? <!--anki:6473553378783f6d733a-->
?
- **Frameworks**: **LangMem** and the **Store** of LangGraph, the memory of [[46-crewai-crews|CrewAI]]
- **Model Providers**: Anthropic's **memory tool** (files)
- **Agent Platforms**: AgentCore Memory, Google's Memory Bank ([[38-agent-platforms|Platforms]])

Distinguishing raw storage from mechanisms that extract, select, and update memories. Out-of-the-box integration does not guarantee relevance or privacy. Check for user isolation, deletion operations, provenance, and conflict management before letting the agent write to memory automatically.

---

What are the risks of persistent memory? <!--anki:7623374a3f4c6c633932-->
?
- **Poisoning**: a registered [[101-llm-security-guardrails|Prompt injection]] reappears at each session
- **Run between users** if namespaces are poorly partitioned
- **Personal data**: GDPR, right to be forgotten, therefore deletion **real**
- **False or outdated memories**

Parades: validate what you write, TTL, and an interface to **see and delete** your memories.

Test a correction and then an old recovery: a false data must not return from a summary or a forgotten index. Treat backups and traces according to their retention; remove the visible text does not delete all its copies.

---

How to evaluate the memory of an agent? <!--anki:6a323337576173662f2e-->
?
Benchmarks of long conversations (**LoCoMo**, **LongMemEval**) and business tests:
- Remind a given fact **several sessions** earlier
- Take into account a fact **who has changed**
- **Refrain** when information has never been given

Also measure the **latency** and **cost** added by writing and research.

Test a sequence: preference A, explicit replacement with B, new session, then deletion. Check for recall of B, absence of A and abstention after withdrawal. Compare to a version without memory to distinguish real gain and already guessable information.

---

When not to give long-term memory to an agent? <!--anki:49407272774774375d5d-->
?
- **Point tasks** without continuity (extraction, classification, one-shot)
- **A structured profile is enough**: preferences and stable facts live better in a table or CRM, read by a tool
- **Sensitive data**: each memory is a personal data to justify, secure and know **delete** ([[154-gdpr-llm|RGPD]])
- **No way to evaluate or purge it**: a false or poisoned memory persists and contaminates the following sessions ([[102-agent-threats|threats]])

Long-term memory is justified by a **measured gain**, not in principle.

---

Do not confuse: agent memory and RAG? <!--anki:4a74332155403f4b7574-->
?
- **RAG**: search in an existing **corpus** (documentation, knowledge base), the same for all users, powered by an ingestion pipeline
- **Agent memory**: information **written by the agent itself** over interactions (preferences, facts, decisions), often **specific to a user**, that evolve and contradict each other

Technically, memory often uses a retrieval; the proper difficulty is **what to write, when to update, and what to forget** ([[21-rag-fundamentals|RAG]]).

---

Why shouldn't a user's silence become a permanent fact in an agent's memory? <!--anki:3363343063626564623963643438386262646466333736623262653833336565-->
?
A **no correction** is not a confirmation. The model may have assumed a preference and the user simply moved on.

Distinguishing between declared, observation and inference; retaining provenance, date and degree of validation. For example, a vegetarian reservation for a guest does not prove that the user is a vegetarian. Providing confirmation for durable preferences, correction and expiration. Upon recovery, presenting an inference as such. Repeating an assumption in multiple summaries does not turn it into evidence.

Test these statuses after consolidation: the summary should not erase the distinction between observation and inference.

---

How do I prevent a corrected memory from reappearing after an agent's memory has been consolidated? <!--anki:6366383263346234346265353435316462646532366634396138353038326364-->
?
The correction should be for **sources and derivatives**, not just the text displayed. Mark the old one as replaced and keep a relationship to the valid version.

Consolidation must respect this status and not rebuild the old value from a historical summary. Test the recall after consolidation, reindexing, and restoration. Logical deletion can help prevent recurrence, but its retention and content must themselves respect the data policy.

---

## Scenarios

Scenario: users complain that your assistant "forgets everything" from one session to another, but also that it sometimes comes out of outdated information. How do you design its memory? <!--anki:69632a4d35613b2e6023-->
?
1. **Separate levels**: thread history for ongoing conversation, long-term memory for lasting facts
2. **Choose what to write**: preferences and stable facts, not all history, with extraction and then **consolidation** (add, update, delete)
3. **Manage time**: Each fact has a valid window, on **invalid** instead of overwriting
4. **Remind little, but well**: score combining relevance, recency and importance, with filters per user
5. **Give the user a hand**: see and erase memories ([[154-gdpr-llm|RGPD]])

**Trap** Memorize everything “just in case.” what produces duplicates, contradictions and potential leaks.

---

Scenario: your agent shares a memory between all the users of the same client company. What safeguards do you pose before putting into production? <!--anki:495a2d323c4446493275-->
?
1. **Closure**: namespace per client and per user, checked for both writing and reading
2. **Control of what enters**: no gross external content, no instructions, write injection analysis ([[103-agent-defenses|Defenses]])
3. **Provenance** attached to each memory, to be able to purge by source
4. **Retention**: lifetime, actual deletion, processing of personal data
5. **Tests**: recall of an ancient fact, taking into account a changed fact, abstention if the information was never given

**Trap**: A memory written by a user that goes back into another user's session.

---

## Sources

- [Letta — agents with state and memory](https://docs.letta.com/v1-sdk/concepts/stateful-agents)
- [LangGraph — persistence and threads](https://docs.langchain.com/oss/python/langgraph/persistence)

## Connections
- [[35-context-engineering|Context engineering]] — Memory as a Context Component
- [[45-langgraph-production|LangGraph in production]] — checkpointer and Store
- [[46-crewai-crews|CrewAI]] — Unified Memory
- [[23-knowledge-graphs-ontologies|Knowledge graphs & ontologies]] — Graph Memory
- [[24-cognee|Cognee]] — a Graph Memory Platform
- [[34-harness-plugins|Harness & plugins]] — Memory Files
- [[101-llm-security-guardrails|LLM Security]] — memory poisoning
- [[38-agent-platforms|Platforms of agents]] — Managed Platform Memory
- [[103-agent-defenses|Security agents — Defensive architecture]] — protect the memory from poisoning
- [[154-gdpr-llm|GDPR applied to LLMs]] — deletion and retention
- [[44-langgraph-fundamentals|LangGraph]] — state graphs for agents and workflows
- [[00-moc-ai-engineering|MOC AI Engineering]]
