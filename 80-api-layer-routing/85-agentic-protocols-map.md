# Map of — Flashcards
Tags: #flashcards #ai-engineering #agents #protocols #mcp #a2a
Verified on: 30 September 2026 — This factsheet lists products, versions or regulatory texts that are evolving quickly.
<!-- summary: protocols by border, MCP, A2A and AG-UI, Agent Card, A2A task cycle, OpenAI compatible API, OpenTelemetry GenAI conventions, `AGENTS.md` and skills, payments by agents (AP2, ACP), governance of standards, when not to expose an agent in A2A, trust borders, job cancellation and business clearing, negotiation of capabilities, contract evolution. -->


What protocols connect an agent to its environment, and at what level? <!--anki:43777b6e472d742a3e38-->
?
```text
            User Interface
                    │  AG-UI
Other Agents ── A2A ── AGENT ── MCP ── tools, data
                    │  API compatible OpenAI
                  Models
      traces : OpenTelemetry · consignes : AGENTS.md, skills
```
Each protocol solves **a boundary**. Confusing them leads to making everything go through one, for example exposing an agent as a simple MCP tool.

This schema shows integration options, not a mandatory stack. An agent can be exposed as a tool if a simple call/result is enough; a delegation with task cycle and events requires a richer contract. Choose according to the expected interactions, then check versions, authentication and capabilities really common to participants.

---

Do not confuse: MCP, A2A and AG-UI? <!--anki:517e403a342b5e76755a-->
?
- **MCP**: agent ↔ **tools and data**. The agent calls a precise capability and keeps control ([[33-mcp|MCP]])
- **A2A**: agent ↔ **other agent**, often from another publisher. We delegate a **task**, which the other agent leads in his own way ([[36-agent-orchestration|orchestration]])
- **AG-UI**: agent ↔ **user interface**. A flow of events (text, tool calls, status) to the front ([[84-streaming-application-integration|streaming]])

Question to be asked: who decides the next step, the appellant (MCP) or the called (A2A)?

---

What does an Agent Card A2A contain? <!--anki:6d3f5351705879773044-->
?
A **Description of Discovery** : identity, supplier/version, skills and examples, endpoints, expected exchange capabilities and authentication mechanisms.

Example: A document analysis and streaming ad card; the client can check these capabilities before submitting a task, without knowing the internal implementation.

If a signature is provided, verify it with a trusted identity or key, not with an unknown key simply attached to the document. It helps authenticate origin and integrity, **not skill or authorization**. Treat descriptions and endpoints as information to be checked; a copied card can be used for a [[102-agent-threats|usurpation]].

---

How does an A2A task work? <!--anki:4e733b7434655a54504e-->
?
1. The client sends a **message** that creates a **task**
2. The task goes through **states**: submitted, in progress, **pending information** (remote agent requests accuracy), completed, failed, canceled
3. The results come in the form of **artifacts** (documents, structured data)
4. The tracking is done in **streaming SSE**, by query or by **push notification** (webhook) for long tasks

This is a long, negotiated **task** model, not a function call.

---

Why is the API "OpenAI compatible" a de facto standard? <!--anki:6c527d66745e7243642d-->
?
Because almost all servers and gateways expose it: vLLM, SGLang, Ollama, LiteLLM, many vendors. Changing a model often means changing a **URL and a model name** ([[81-litellm-api-layer|LiteLLM]]).

Limit: the functions **advanced diverge** (prompt caching, reasoning, server-side tools, multimodal formats). A code that depends on it is no longer portable: we isolate them behind an abstraction layer ([[146-model-selection|lock-in]]).

---

What do OpenTelemetry GenAI conventions standardize? <!--anki:63383f544e615b586369-->
?
The **attribute and span names** of the LLM application and agent traces: called model, tokens input and output, reason for shutdown, tool and agent call spans. Examples: `gen_ai.request.model`, `gen_ai.usage.input_tokens`.

Interest: the same dashboard or analysis tool reads the traces of **frameworks and different platforms**, without adapter ([[93-monitoring-inference|monitoring]]).

Interoperability requires compatible versions and units. Pin the conventions used and check an exported example; a standard name does not guarantee the presence of the attribute or its good value. Hide sensitive content regardless of format.

---

What is `AGENTS.md` and skills used for in the standards landscape? <!--anki:6c386c4d393f6e2f512f-->
?
They standardize **requirements given to agents**, not network exchanges:
- **`AGENTS.md`**: Project instructions read by code agents, regardless of tool ([[49-coding-agents|Code Agents]])
- **Skills**: instruction and script files loaded **on demand** (`SKILL.md` format), taken over by several harnesses ([[34-harness-plugins|skills]])

They are also **untrusted** entries when they come from a third-party repository or catalog ([[104-mcp-skills-security|Safety of Skills]]).

---

What protocols govern payments made by agents? <!--anki:4f2c2c357e4d60472f7e-->
?
- **AP2** (Agent Payments Protocol, Google, 2025): signed **mandates** prove what the user has authorized (amount, merchant, conditions), so that a payment triggered by an agent is verifiable and questionable
- **ACP** (Agentic Commerce Protocol, OpenAI and Stripe, 2025): the buying journey between a conversational agent and a merchant

Common principle: the agent never handles gross means of payment, and **human authorization is cryptographically proven**.

---

Who governs these standards, and why is it important? <!--anki:7a382370606173486134-->
?
The **Governance** determines who evolves a specification, how decisions are made and how implementations remain compatible. MCP, A2A and `AGENTS.md` are part of initiatives of the Linux Foundation, with separate project structures.

Examine open decisions, versioning, compliance testing, support and depreciation. A neutral foundation can reduce dependency on a vendor, but does not guarantee either the security of an implementation or the durability of a product. Test the useful contract and plan an output; do not confuse governance of the standard and operational guarantees of the chosen tool.

---

When not to expose an agent in A2A? <!--anki:6c7a5b4c793579265f52-->
?
- **Agents in the same application**: a function call or sub-agent is sufficient, without network or serialization ([[36-agent-orchestration|Subagents]])
- **Simple and deterministic capacity**: it is a **tool**, to be exhibited in MCP
- **No external consumers** expected: A2A adds authentication, discovery, and attack surface for nothing

A2A is justified **between teams, between publishers or between organizations**.

Example: Two components deployed and versioned together can share a typed local interface. A network border becomes relevant with deployment autonomy, stable contract and real need for discovery; it also adds timeouts, partial errors and identity management.

---

Which trust boundary does each protocol introduce? <!--anki:7826376228252b703a2b-->
?
- **MCP**: Tool descriptions and results are contextual, so **injection** possible ([[104-mcp-skills-security|MCP Security]])
- **A2A**: A remote agent may be **usurped** or compromised, and its responses are unreliable data
- **AG-UI**: The interface should only display or execute **validated** events
- **`AGENTS.md` and skills**: instructions from a third-party repository or catalog

Each added protocol is a **border to be authenticated, log and filter**.

---

Why is an A2A cancellation request not proof that any business effect has been cancelled? <!--anki:3061326435656534633331383465303238303330643130323939313863373635-->
?
The **Cancellation of Task** is a protocol operation whose success depends on the state of the server. The task may already be completed or have produced an irreversible effect.

Read the returned status, check for external operations, and provide separate compensation if the trade allows it. Test cancellation pending, execution, and confirmation. The protocol normalizes request and tracking; it does not provide a distributed transaction encompassing payment, booking, and messages already sent. Present the user with the confirmed status, including an as-yet-unknown result.

---

Why is it not enough to negotiate an ability to guarantee its semantics between agents? <!--anki:3865346436316138376665353433656438373932346236373136646538663133-->
?
Two participants can recognize **the same capacity name** but differ on limitations, errors, or recovery conditions.

Version contracts and run interoperability tests on useful paths, including denials and cancellations. An optional ability must have explicit fallback behavior. Do not infer from protocol compatibility alone that identities and permissions are equivalent.

---

Why keep a business identifier beyond the MCP, A2A and trace identifiers? <!--anki:3062623362633330353738643461333662613333366166643733373863346264-->
?
Each layer identifies **a different exchange or execution**. The same business operation can go through multiple protocols, calls and times.

A stable business identifier reconciles effects, billing and user result. Technical identifiers remain useful for diagnosis and must be linked to it. Avoid using the trace identifier as an idempotency key if a recovery creates a new trace.

---

## Scenarios

Scenario: your company wants its internal travel agent to reserve through the agent of a partner agency, display its progress in the web application, and consult internal travel policies. What protocols do you use, and where? <!--anki:74765a2e296f595d6542-->
?
1. **Internal policies**: a read-only server **MCP** based on documentation, it is a tool
2. **Partner agency**: **A2A**, because we delegate a negotiated task (availability, details) to an agent of another publisher, via his signed Agent Card
3. **Interface**: **AG-UI** or equivalent event flow to view steps and confirmation requests ([[84-streaming-application-integration|streaming]])
4. **Traces**: OpenTelemetry throughout the chain, to link a reservation to its stages
5. **Payment**: explicit human confirmation, ideally with a verifiable mandate rather than a card entrusted to the agent

**Ship**: Wrap the agency agent in a synchronous MCP tool, and lose the precision exchanges and long task tracking.

---

Scenario: three teams have each built agents with different frameworks, and management wants them to collaborate without rewriting everything. What do you propose? <!--anki:6636733d7065247d4b31-->
?
1. **Inventory** capabilities: which are tools, which are autonomous agents
2. **Expose shared tools in MCP**, behind a common gateway ([[38-agent-platforms|Gateway Tools]])
3. **Expose in A2A** only agents called by other teams, with Agent Cards in an internal register
4. **Unify observability** on OpenTelemetry GenAI conventions
5. **Keep frameworks**: protocols make interoperability independent of each team’s code

**Pip**: impose a single framework on everyone, when the need was an exchange contract.

---

## Sources

- [MCP — Specification 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28)
- [A2A — protocol specification](https://a2a-protocol.org/latest/specification/)
- [AG-UI — protocole d’interaction agent-interface](https://docs.ag-ui.com/introduction)
- [OpenTelemetry — semantic conventions GenAI](https://github.com/open-telemetry/semantic-conventions-genai)

- [A2A — cancellation and task reports](https://a2a-protocol.org/latest/specification/) — targeted deepening of the 12 November 2026; educational examples are built for this review.

## Connections
- [[33-mcp|MCP]] — Protocol Agent ↔ Tools
- [[36-agent-orchestration|Orchestration multi-agents]] — A2A and delegation
- [[84-streaming-application-integration|Streaming & integration]] — AG-UI and events to interface
- [[81-litellm-api-layer|LiteLLM]] — OpenAI compatible API as contract to models
- [[93-monitoring-inference|Monitoring]] — conventions OpenTelemetry GenAI
- [[104-mcp-skills-security|Security of MCP & Skills]] — each protocol is a trusted border
- [[115-agent-platforms-governance|Agent Platforms — Governance]] — standard open against lock
- [[11-llm-inference-servers|Inference Servers]] — vLLM, SGLang, TensorRT-LLM and their setting
- [[123-aggressive-caching|Caching]] — prompt caching and response caches
- [[103-agent-defenses|Defenses of agents]] — insulation, policies and least privilege
- [[37-agent-frameworks|Frameworks d'agents]] — framework panorama
- [[00-moc-ai-engineering|MOC AI Engineering]]
