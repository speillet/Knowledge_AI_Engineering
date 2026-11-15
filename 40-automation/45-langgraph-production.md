# LangGraph — Production (persistance, HITL, multi-agents) — Flashcards
Tags: #flashcards #ai-engineering #agents #langgraph #llm
Verified on: 25 September 2026 — This factsheet lists products, versions or regulatory texts that are evolving quickly.
<!-- summary: checkpointers, threads, `interrupt` and `Command(resume=...)`, time travel, Store long-term, durable execution, streaming, subgraphs, multi-agent patterns, deployment, valid take-back approvals, concurrent approval, take-back and secrets. -->


What is a checkpointer in LangGraph? <!--anki:73715178653d54644d38-->
?
The component that **backs up the state of the graph after each super-step**. It brings conversation memory, error recovery, human-in-the-loop, and time travel.

```python
graph = builder.compile(checkpointer=checkpointer)
```

The backend and durability mode determine when a backup is actually retained. Checkpoints describe the state of the graph; they do not arbitrarily save the entire process memory and do not cancel a remote operation. Test a restart in the middle of a task to verify the actual recovery.

---

What checkpointers does LangGraph offer? <!--anki:4a23792655613437387d-->
?
- **`InMemorySaver`**: process memory, suitable for testing, lost when stopped.
- **`SqliteSaver`**: Persistence on file, useful locally or for limited deployment.
- **`PostgresSaver` / `AsyncPostgresSaver`**: Shared storage suitable for multi-worker services.

Example: Two replicas each with their SQLite file do not share the history of a thread. A common database resolves access to checkpoints, not by itself the concurrent updates of the job.

Choose according to durability, concurrency and exploitation; test restore a backup, retention and deletion. A persistent file in a container remains lost if its storage does not survive the replacement.

---

What is a thread in LangGraph? <!--anki:65266e7a71676c416a5b-->
?
A **set of checkpoints** identified by a **`thread_id`**, passed in the config (`{"configurable": {"thread_id": "..."}}`). Even `thread_id` = is restarted; new `thread_id` = is restarted from scratch.

The thread is a state continuity unit, not a user identity. The application must verify its owner and handle concurrent runs. A new thread can still read a long-term memory shared via a Store; leaving without a history does not mean leaving without any persistent knowledge.

---

How to put a human in the loop of a LangGraph graph? <!--anki:4e2d79524e626742322d-->
?
A node calls **`interrupt(payload)`**: the state is saved and the execution **stops** by returning the payload. We resume with **`Command(resume=value)`** on the same thread; `value` becomes the return of `interrupt()`.

```python
from langgraph.types import interrupt, Command

def approbation(state):
    ok = interrupt("Approve sending this email?")
    return {"approved": ok}

graph.invoke(Command(resume=True), config=config)
```

On resuming, **the node starts over again**: the code preceding `interrupt()` can be executed again. Place the external effect after approval and make it idempotent. Show the human the precise arguments of the action, then verify that its response comes from an authorized identity.

---

Why is a checkpointer required for `interrupt`? <!--anki:52647e3824313c325d47-->
?
The checkpointer keeps the pending state and interrupt in order to resume the **same thread** later, possibly in another process. A RAM backup does not survive a restart: use durable storage for this need.

Recovery does not restore a frozen Python stack: **The interrupted node restarts**, and then `interrupt()` receives the value transmitted by `Command(resume=...)`. Effects before the interruption must therefore be idempotent or moved in a separate step.

---

What is time travel in LangGraph? <!--anki:43524756212128393c4d-->
?
Browse the **History of Checkpoints** a thread (`get_state_history`), **Replay** from a past checkpoint or **amend** (`update_state`) to explore another branch — Very useful for debugging an agent.

A replay can redo LLM calls or tools and produce different results. It does not go back time in external systems: an email already sent remains sent. To debug without duplication of effects, use simulated tools or operations protected by keys of idempotency.

---

Do not confuse: Checkpointer and Store in LangGraph? <!--anki:4b5042685f574b50716d-->
?
- **Checkpointer** : Memory **Short term**, own to **a Thread**
- **Store** (e.g. `InMemoryStore`) : memory **long term, shared between threads**, organized in **Namespaces** (e.g. `("user-123", "preferences")`), with semantic search possible

The former keeps the progress of a conversation; the latter may retain a useful preference in future conversations. "Long term" refers to the perimeter, not a guarantee of durability: `InMemoryStore` remains volatile. For both, define permissions, retention and management of concurrent updates.

---

What is durable execution in LangGraph? <!--anki:6e5a3837745771543752-->
?
The ability of a workflow to **recover from persistent** information after a failure or pause. Work that has been saved can be reused; unsaved portions can be replayed.

Isolating external effects in tasks or nodes facilitates this recovery, but does not guarantee their single execution. If a API accepts an action just before the crash, without saving its result, the recovery can request it again. Provide stable identity of operation, service side idempotency and reconciliation. The durability mode and storage determine the points actually recoverable.

---

What data can be streamed from a LangGraph graph? <!--anki:445e71583c4f4f626c26-->
?
The **Full State** After each step (`values`), on the **Updates** of each node (`updates`), on the **tokens** of the LLM (`messages`) or **Custom Events** (`custom`). Recent versions also add `stream_events(..., version="v3")`.

Choose the flow according to the interface: tokens to display a response gradually, updates to show a completed step, custom events for a business progression. Filter what is exposed: the complete state can contain internal data. Check the modes available in the installed version and manage disconnection or recovery on the client side.

---

What is a subgraph in LangGraph? <!--anki:447762797072732f477e-->
?
A compiled **graph used as a node** of another graph. This breaks up a complex system into modules, often **one subgraph per agent**.

Define the input and output of the module, then translate the keys if its state differs from that of the parent. This separation facilitates reuse and testing. Checking the spread of checkpoints and interruptions according to the configuration; cutting into subgraphs does not automatically create a security isolation.

---

Which LangChain/LangGraph multi-agent patterns do they document? <!--anki:78287e6656626f715b77-->
?
- **Subagents**: a lead agent calls subagents **like tools**
- **Handoffs**: one agent **hands over** to another via a tool call
- **Router**: a step ranks the request and sends it to the right agent
- **Skills**: a single Specialized Context Officer on request
- **Custom workflow**: a custom graph that combines the previous ones

Choose according to the expected control: a sub-agent returns a result to the principal; a handoff changes the active interlocutor. Test who keeps the history and who can act after the transfer, not just the quality of the final text.

---

How to deploy and debug a LangGraph graph? <!--anki:6c6747322662447d7252-->
?
- **LangSmith Deployment** (ex-LangGraph Platform): a **Agent Server** that exposes the graph to API, with persistence, managed task queues and streaming
- **Studio**: Visual IDE to run step-by-step and inspect state
- **Self-hosted**: the graph in its own service (FastAPI, container) with a `PostgresSaver`

The deployment must also cover migrations of checkpoints, thread isolation, cancellation and secrets. Testing a restart during a human wait: finding the state in Studio does not prove that the service knows how to correctly resume the request.

---

Why should a LangGraph human approval expire if the business proposal changes? <!--anki:3666396463386164343636323466306561393138333166636635363339326133-->
?
The **Approval** must be based on specific arguments, an object version and scope of action. After two days of suspension, A price or recipient may have changed.

On resumption, verify identity, rights, expiration and version of the proposal before effect. If a decisive element changes, produce a new proposal and a new validation. Keep the decision and its reference in the audit. A `Command(resume=...)` carries a response; it does not in itself constitute a valid business authorization.

---

How to deal with two competing human responses to a LangGraph interrupt? <!--anki:6236643737646232356561333466396238313861383337613263323466333861-->
?
Associate the decision to **the interrupt identifier and version of the proposal**, and then atomically accept a single transition from the "pending" state.

A late response must receive a status that has already been processed or expired. Do not apply successively "approve" and then "deny" as two new business commands. Test double click, two validators and resume after timeout. The interface and graph must share the same decision status.

---

Why avoid persisting an access token in a LangGraph checkpoint? <!--anki:6664383032383065643938313436613262393838653835633232323061303632-->
?
The token may **expire, be revoked, or become accessible via a backup**. Resume the old checkpoint must not restore an old authorization.

Persist an identity reference and the necessary business data, and then obtain current access through a controlled mechanism. Recheck the rights to action. If a secret has already been stored, deleting the current state is not necessarily enough to erase it from history and backups.

---

## Scenarios

Scenario: your order fulfillment agent stops for human validation which sometimes arrives two days later. It runs today with `InMemorySaver`. What do you change? <!--anki:4d2f6936553058693334-->
?
1. **Persistent Checkpointer**: `PostgresSaver` in production, otherwise a restart loses all pending folders
2. **Thread by folder**: `thread_id` stable, to reload the good state; the start of the interrupted node can be replayed
3. **Recovery** by `Command(resume=...)` with the decision, from a process other than the one that interrupted
4. **Times and reminders**: a file that has been pending for too long must alert or expire
5. **Insulated Edge Effects**: Writes and Shipments must not be replayed after a replay

**Trap**: Keep interruptions in memory and lose ongoing validations on the first deployment.

---

Scenario: an agent produced an outlier yesterday at 14 h, and the user wants to understand why. How do you investigate? <!--anki:432a625f5e245f5a3577-->
?
1. **Find the thread** from the conversation ID, then its checkpoint history
2. **Time travel**: replay from the checkpoint before the error to see the exact status of the time
3. **Isolate the wrong step**: tool that returned false data, unexpected routing, truncated context
4. **Test a fix** by changing the status at this point (`update_state`) and replaying
5. **Fix the case** in a non-regression test, then correct the code or prompt ([[112-model-cicd|CI/CD]])

**Trap**: Replay the query today, with another context and version of the model, and conclude that the problem does not exist.

---

Scenario: your four-agent system becomes impossible to debug, each agent having its own tools and state. How do you restructure it? <!--anki:4b4347547d6645526b3f-->
?
1. **A subgraph per agent**: each one becomes a compiled module, testable only
2. **Choose an explicit pattern**: router input, peer-to-peer handoffs, or subagents called as tools ([[36-agent-orchestration|orchestration]])
3. **Minimum shared status**: what circulates between agents is structured and limited, the rest remains local
4. **Streaming updates** by node, to see who does what live
5. **Wondering if four agents are needed** Sometimes two are enough, with code between them

**Trap** A global state where each agent writes what he wants, and that no one understands anymore.

---

## Sources

- [LangGraph — Interrupts and Reruns the Node on Recovery](https://docs.langchain.com/oss/python/langgraph/interrupts)

- [LangGraph — persistence and threads](https://docs.langchain.com/oss/python/langgraph/persistence)

- [LangGraph — checkpointers and durability](https://docs.langchain.com/oss/python/langgraph/checkpointers)

- [LangGraph — interruptions and recovery](https://docs.langchain.com/oss/python/langgraph/interrupts) — targeted deepening of the 12 November 2026; educational examples are built for this review.

- 14 November Supplement 2026 — Checkpoints and Persistent Memory: [LangGraph — persistence](https://docs.langchain.com/oss/python/langgraph/persistence).

## Connections
- [[44-langgraph-fundamentals|LangGraph — Fundamentals]] — state, nodes, edges
- [[43-langchain-agents|LangChain — Agents]] — HITL and memory via middleware
- [[36-agent-orchestration|Orchestration multi-agents]] — Patterns
- [[35-context-engineering|Context engineering]] — short and long-term memory
- [[41-code-nocode-automation|Automation]] — durable execution (Temporal)
- [[91-langfuse-observability|Langfuse]] — trace executions
- [[39-agent-memory|Memorandum of agents]] — memory types, write and recall
- [[38-agent-platforms|Platforms of agents]] — managed runtimes, double texting
- [[115-agent-platforms-governance|Agent Platforms — Governance]] — identity, policies, audit and costs of a fleet of agents
- [[142-llm-reliability-resilience|Reliability & resilience]] — timeouts, recoveries, fallbacks and degradation
- [[140-010-transactions-outbox-sagas|Transactions & sagas]] — complete checkpoints for external effects
- [[40-011-langgraph-recovery-concurrency|LangGraph — Recovery, Concurrency & Evolution]] — persistence and interruptions
- [[00-moc-ai-engineering|MOC AI Engineering]]
