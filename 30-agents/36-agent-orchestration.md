# Multi-agent orchestration — Flashcards
Tags: #flashcards #ai-engineering #agents #multi-agent #llm
Verified on: 25 September 2026 — This factsheet lists products, versions or regulatory texts that are evolving quickly.
<!-- summary: orchestrator-workers, supervisor, handoffs, evaluator-optimizer, shared state, multi-agent cost, A2A protocol, parallel critical path calculation, branch cancellation, delegation contract. -->


What is a multi-agent system? <!--anki:63233b336f5f4325367c-->
?
Several **Agents LLM Specialized** (role, tools and context) which **Co-operation** on a task, coordinated by an orchestrator or by hand-over rules.

An agent can search for sources while another analysis of the data, and then a coordinator assembles the results. The specialization must correspond to a clear subtask and output contract. Forecasting budgets, conflict management and final verification: multiplying roles guarantees neither diversity of reasoning nor better quality.

---

When to switch to multi-agent? <!--anki:42663463505b794a2840-->
?
When the task is **parallelizable**, **exceeds the context window** of a single agent, or requires very different **tools or expertise**. Otherwise, **a single agent** remains simpler and cheaper.

Measuring the gain on tasks where the sub-problems have few dependencies. A comparison of several markets parallels better than a sequential modification of the same file. Also test a simple separation in calls or contexts: it can be sufficient without introducing autonomous coordination, shared state and additional communication costs.

---

What is the orchestrator-workers pattern? <!--anki:7850547e77347858323c-->
?
A **Orchestrator** Cut out the task, **Delegate** subtasks to workers (often in parallel), then **Synth** their results.
```text
                 ┌── worker : sources FR ──┐
Orchestrator ───┼── worker : sources EN ──┼──→ Synthesis
                 └── worker : brevets ─────┘
```
Each worker works in **his own context** and returns only a **structured result**. This is what protects the context of the orchestrator, but also what multiplies the tokens ([[35-context-engineering|context engineering]]).

Decomposition helps if the subtasks are fairly independent. Each worker must receive an objective, a budget and a result format with sources and uncertainties. The orchestrator then deals with contradictions, duplicates and partial failures. Three workers who repeat the same search can increase the cost without providing three independent proofs.

---

What is the pattern supervisor? <!--anki:68252d3e6e7552793276-->
?
An agent **supervisor** chooses at each stage **which specialized agent** must act, and can stack several levels (supervisors of supervisors).

The supervisor formulates a subtask, transmits the necessary context, examines the result and decides to continue or conclude. For example, he delegates a documentary search to a specialist and then asks for a verification of the figures. To limit the depth and the number of delegations; otherwise the coordination itself becomes a costly loop.

---

What is a handoff? <!--anki:4a76714a787563664645-->
?
The **transfers control of the conversation** from one agent to another (e.g. triage → billing agent), with the necessary context to continue. Technically, it is often a particular **tool call**, which passes the hand instead of returning a result.

After a handoff to billing, it is the receiving agent that continues the exchange; in a subagent call as a tool, the parent usually retrieves the result and remains responsible for the continuation. Transfer only the necessary context and recheck the permissions: changing agent should not automatically expand the user's rights.

---

Do not confuse: subagent and handoff? <!--anki:72473748675961444c44-->
?
- **Sub-agent**: the primary agent **keeps control**. He calls the sub-agent as a tool, receives a **summary** and continues. Context remains compartmentalized
- **Handoff**: the agent **gives control** and does not take over. It is the next one who speaks to the user

Practical choice: sub-agent for **Explore** or parallelize, Handoff for **Router** to a specialty (sorting to billing).

---

Which sequential, parallel or critical patterns make it possible to compose agents? <!--anki:433e64396f3367454834-->
?
- **Sequential** (pipeline): the output of one is the input of the next
- **Parallel**: independent sections or votes
- **Evaluator-optimizer**: one product agent, another review, iterates

Choose according to the structure of the task: strong dependencies for the pipeline, independent sub-problems for the parallel, explicit correction criterion for the critique. The evaluator-optimizer must have a maximum number of iterations and a measurable improvement condition: for a summary, at most three turns, stop as soon as each affirmation is attached to a source. Two agents who exchange opinions do not constitute a reliable validation.

---

What is the cost of the multi-agent? <!--anki:4f3e644c6456264e4e2e-->
?
The total cost includes **calls from all agents**, repeated contexts, tools, and synthesis. Latency depends on the **critical path**: it adds up for sequential steps, but independent branches can run in parallel.

Example: three workers of 2 minutes run in parallel, then a one-minute summary, give 3 minutes of delay against 7 in sequence; the tokens of the four calls add up in both cases. The measured orders of magnitude are in the [[31-agent-fundamentals|Agents]] topic. Measure cost per successful task, delay and quality against a single agent.

---

How do agents in a multi-agent system share information? <!--anki:726a607969306e577a79-->
?
By **messages** (summaries returned to the orchestrator), a **shared state** (status graph, whiteboard) or external **artifacts** (files, base) — which avoids passing everything through the context.

Define who can read and write each piece of information, in which version and in which format. Two agents modifying the same artifact can overwrite their results; use work partitions or concurrency control. Example: each worker writes only `results/<worker>.json`, and the orchestrator is the only one to produce the synthesis. Transmit the proofs and uncertainties with the synthesis, so that a provisional conclusion does not become a given fact.

---

What is the A2A protocol? <!--anki:752355255f5525695870-->
?
**Agent2Agent** standardizes agent-to-agent exchanges: ability discovery via a **Agent Card**, sending requests, and tracking tasks or results. [[33-mcp|MCP]] instead exposes tools and resources to a host; both can be combined.

Example: a procurement agent requests an analysis from a supplier agent without knowing its model or internal orchestration. The protocol describes the exchange, not the reliability of this analysis.

Verify authentication, compatible capabilities, deadlines, and endpoint status of the task. An Agent Card describes a service; it does not constitute an access authorization or a certification of its responses.

---

Calculation: what minimum time for three parallel workers of 2, 5 and 8 seconds followed by a synthesis of 3 seconds? <!--anki:6266316666383433363938613435396238616562343635313338353734333963-->
?
If workers are **independent**, start together, and synthesis waits for all three, the critical path is `max(2, 5, 8) + 3 = 11 secondes`, excluding orchestration and files.

Sequential execution would take `2 + 5 + 8 + 3 = 18 secondes`. Latency gain does not imply a drop in cost: the same work is performed, with possibly more coordination. A worker dependency or a concurrency limit invalidates this ideal calculation.

---

What should a delegation contract between an orchestrator and a sub-agent contain? <!--anki:3165613337626238373133633438623538333331336532376134613064653866-->
?
Specify **objective, authorized entries, verifiable deliverable, budget and stop condition**. The sub-agent must also indicate the evidence and uncertainties relevant to the summary.

"Analyse the file" is less controllable than "extracts the termination clauses with page and quotation". The orchestrator remains responsible for checking the result and resolving the contradictions. Delegate a task does not expand the permissions or erase the overall budget.

---

Why cancel sub-agents that have become useless after a decision? <!--anki:3731393930653865323533383435623662313238633937653835313833383134-->
?
They can continue to consume **tokens, writing tools and capabilities** while their result will no longer be used. Spread the cancellation to tasks, external calls cancelable and the admission of new actions.

Check for transactions that have already occurred: a local cancellation does not prove the absence of an external effect. Keep their credentials for reconciliation. Measure the work actually saved, because some providers complete and charge a request even after disconnecting from the client.

---

## Scenarios

Scenario: a team offers an architecture to seven agents (research, writing, proofreading, SEO, translation, publication, supervision) to produce articles. What do you think? <!--anki:4a3d52637c423274602b-->
?
1. **Question the need**: these steps are **sequential and predictable**, so a workflow with a few LLM calls is often enough ([[41-code-nocode-automation|automation]])
2. **Remind the cost**: each agent has its context. A multi-agent system consumes much more tokens and accumulates latencies
3. **Keep the multi-agent** where it brings something: search, parallelizable on multiple sources
4. **Simplify**: a primary agent, search sub-agents, and code for the web
5. **Compare** both versions on the same task: quality, cost, latency, ease of debugging

**Trap**: a supervisor who coordinates six agents and becomes the real bottleneck, impossible to debug.

---

Scenario: in your orchestrator-workers system, a worker returns a false data that the orchestrator resumes as is in its synthesis. How do you avoid propagation? <!--anki:4e605d5334603c7c3c64-->
?
1. **Treat the output of a worker as unreliable**, even if it is internal ([[103-agent-defenses|Defenses]])
2. **Structured formats**: the worker returns schema-validated fields, with its **sources**, not a free text
3. **Verification**: cross-checking between workers, or deterministic control when possible
4. **Cute-circuit**: beyond a rate of errors, we stop the chain rather than publish
5. **Track** each step, to find the agent causing the error ([[93-monitoring-inference|traces]])

**Trap**: judge quality only on the final result, without ever looking at the intermediate steps.

---

Scenario: a partner wants your booking agent to interact with his/hers, developed with another framework. How do you proceed? <!--anki:49763e756e54515d5d46-->
?
1. **A2A**: Expose a **Agent Card** describing skills, endpoint and authentication, and consume your own
2. **Verify identity**: Signed Agent Cards, mutual authentication, authorized scope of action
3. **Frame the exchanges**: typed tasks, structured formats, deadlines and error recovery
4. **Protect Yourself** : what the partner agent returns is a **Unreliable entry**, Validate before any action
5. **Observe**: traces and metrics from end to end, and a circuit breaker if the partner degrades

**Trap**: Give the partner direct access to your tools instead of going through a controlled agent interface.

---

## Sources

- [Anthropic — multi-agent search system architecture](https://www.anthropic.com/engineering/multi-agent-research-system)
- [A2A — protocol specification](https://a2a-protocol.org/latest/specification/)

## Connections
- [[31-agent-fundamentals|Agents]] — single agent before multi-agent
- [[35-context-engineering|Context engineering]] — isolates contexts
- [[37-agent-frameworks|Frameworks d'agents]] — LangGraph, CrewAI, ADK
- [[38-agent-platforms|Platforms of agents]] — run in production
- [[41-code-nocode-automation|Automation]] — when a workflow is enough
- [[45-langgraph-production|LangGraph in production]] — subagents, handoffs, router in practice
- [[46-crewai-crews|CrewAI]] — sequential or hierarchical process
- [[115-agent-platforms-governance|— Agent Platforms Architecture & Governance]] — govern a fleet of agents
- [[103-agent-defenses|Security agents — Defensive architecture]] — secure exchanges between agents
- [[48-agentic-workflow-patterns|Patterns of workflows]] — chaining, routing, evaluator-optimizer
- [[27-search-agents-deep-research|Research agents]] — the school case of orchestrator and subagents
- [[98-agent-debugging|Debugging agents]] — coordination failures (MAST)
- [[85-agentic-protocols-map|Map of protocols]] — A2A vs MCP and AG-UI
- [[102-agent-threats|Threats to agents]] — real attacks and incidents
- [[145-system-design-cases|Case of system design]] — of commented type architectures
- [[44-langgraph-fundamentals|LangGraph]] — state graphs for agents and workflows
- [[47-crewai-flows|CrewAI — Flows]] — event-driven workflows
- [[49-coding-agents|Code Agents]] — Use and Integrate Code Agents
- [[137-long-context|Long context]] — limits and cost of long windows
- [[34-harness-plugins|Harness & plugins]] — the program that runs the agent
- [[43-langchain-agents|LangChain — Agents]] — agents and middleware LangChain
- [[40-012-crewai-reliable-execution|CrewAI — Reliable Execution & Integration]] — dependencies and delegation
- [[00-moc-ai-engineering|MOC AI Engineering]]
