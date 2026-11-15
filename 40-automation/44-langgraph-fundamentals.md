# LangGraph — Fundamentals — Flashcards
Tags: #flashcards #ai-engineering #agents #langgraph #llm
Verified on: 25 September 2026 — This factsheet lists products, versions or regulatory texts that are evolving quickly.
<!-- summary: `StateGraph`, state and reducers, `MessagesState`, nodes and conditional edges, ReAct loop in graph, super-steps, `Send` (map-reduce), `Command`, Functional API, explicit order of parallel aggregations, reducers and duplicates, minimal state. -->


What is LangGraph? <!--anki:6c283f532b7b414f4e78-->
?
A **low-level orchestration framework and a** runtime for **long and stateful** agents. It allows **mixing deterministic steps (code) and agentic steps (LLM)** in the same graph.

The state transports information between steps and the transitions determine the rest of the work. Example: find, analyze, request validation, then act. The graph makes the control explicit; the reliability still depends on the functions performed, the storage of checkpoints and the processing of external effects.

---

What are the three elements of a LangGraph graph? <!--anki:2571304a364929733c-->
?
- **State**: Shared state (TypedDict or Pydantic)
- **Nodes** functions that receive the state and return a **Partial update**
- **Edges**: transitions between nodes (fixed or conditional)

For example, the report contains a ticket, a node calculates its category, and a transition chooses the corresponding processing. Defining clear keys and contracts prevents steps from implicitly depending on the history. For concurrent writes, specify how to merge updates using suitable reducers.

---

What is a reducer in LangGraph? <!--anki:66312c767534457c4079-->
?
The function that says **how to apply the update of a node** to a state key. By default the value is **replaced**; with a reducer it is **combined**:

```python
from typing import Annotated
from operator import add
from typing_extensions import TypedDict

class State(TypedDict):
    notes: Annotated[list[str], add]  # Lists are accumulating
```

With this example, two outputs `['a']` and `['b']` accumulate instead of the second overwriting the first. The choice must respect the business sense: concatenate can create duplicates during a recovery. For identified objects, a merge per identifier is sometimes preferable to a blind addition.

---

What is `MessagesState`? <!--anki:516c586a45296d392342-->
?
A predefined state with a key **`messages`** and the reducer **`add_messages`**, which **adds** new messages (and updates those with the same id): the basis of any conversational agent.

The reducer therefore treats the history as identified messages, and not as a simple list to concatenate. Preserving links between tool calls and responses remains essential. This type of state does not, in itself, add durable storage or common memory to all conversations.

---

How to write a ReAct agent loop with LangGraph? <!--anki:6e7d42476361234b54-->
?
```python
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition

def call_model(state: MessagesState):
    return {"messages": [model_with_tools.invoke(state["messages"])]}

builder = StateGraph(MessagesState)
builder.add_node("llm", call_model)
builder.add_node("tools", ToolNode([get_weather]))
builder.add_edge(START, "llm")
builder.add_conditional_edges("llm", tools_condition)  # → "tools" or end
builder.add_edge("tools", "llm")
graph = builder.compile()
```

The `llm` node adds the model's response; `tools_condition` terminates if no tools are requested, otherwise `ToolNode` executes and returns the model's hand. `get_weather` and `model_with_tools` are prerequisites: the model must be bound to the same tools. Add iteration limits, permissions, and error handling before actual use.

Test three paths with a simulated model: direct response, tool then response, tool in error. Check the order of messages and the association of each result to its call.

---

What is a conditional edge in LangGraph? <!--anki:4335732e4d703f5b4531-->
?
A transition whose destination depends on a **routing function** reading the state: `add_conditional_edges("noeud", route)`. It allows branches and cycles.

Example: after validation, route to `terminer` if the result is valid, `corriger` if there are still attempts, otherwise `escalader`. The counter belongs to the state and must actually increase with each correction.

Test each output, including incomplete state and exhausted budget. The function can be deterministic while reading an uncertain LLM estimate; prefer an independent validator for a verifiable criterion. Avoid an unexpected value silently choosing the path to success.

---

How does LangGraph execute a graph? <!--anki:50592646755542376a7c-->
?
By **super-steps**: Active nodes in a step can run in parallel, and then their updates are applied according to the reducers before the next step.

With a **checkpointer configured**, the runtime can keep the snapshots and writes needed for recovery. The time when they become durable depends on the mode chosen (`sync`, `async`, `exit`) and the backend. A graph compiled without persistence does not automatically save its progress to disk. Check separately the logical parallelism, state fusion and actual durability.

---

What is the API `Send` from LangGraph? <!--anki:6d3b50523a447c7d7e4a-->
?
Au **map-reduce dynamic** : when the number of branches is known only at execution, a conditional edge returns a list of `Send`, one per item to be dealt with.

```python
from langgraph.types import Send

def route(state):
    return [Send("resumer", {"doc": d}) for d in state["docs"]]
```

Each branch receives a report adapted to a document, and then its results must be combined with a reducer. To limit the number of simultaneous tasks to respect the quotas of the model. Also define the behavior when a document fails: limited retry, partial result or stop of the set.

---

What is `Command` in LangGraph? <!--anki:756a654c29346c544574-->
?
To **update the status and choose the next node** from one node, in a single statement: `return Command(update={"status": "ok"}, goto="valider")`. Widely used for **handoffs** between agents.

`update` describes the state changes and `goto` the chosen destination. This is useful when a decision produces both information and a transfer of control. Check the other edges of the node: a static edge can still trigger its path, even if `Command` requests another destination.

---

How to prevent a LangGraph graph from looping to infinity? <!--anki:4341417b4c627b246c37-->
?
With the **`recursion_limit`** (maximum number of super-steps, passed in the config) and explicit **output conditions** in the routing functions.

This limit counts the steps of the graph, not directly the tokens or the duration. Adding a global delay, a budget of calls and a detection of repeated actions without progress. Intercepting the limit error and restoring the partial state; increasing the ceiling without diagnosis can only make the failure more expensive.

For example, three identical searches reporting the same observation indicate a lack of progress; the output should indicate the missing information rather than fabricate a conclusion to complete.

---

Is there an alternative to the explicit graph in LangGraph? <!--anki:4d6557676c3834252436-->
?
**Yes**: The **Functional API** (`@entrypoint` and `@task` decoders) writes the stream in **Classic Python** (if, loops) while taking advantage of the persistence and interruptions of LangGraph.

It is suitable when the existing stream is already readable in Python and we want to add persistence points. Encapsulating the operations concerned in tasks makes it easier to resume. We must always think about the actions that can be replayed: a mandatory syntax does not automatically provide an execution exactly once.

---

Why should a LangGraph parallel aggregation explain the order of the results? <!--anki:3435393033623231663763383434383238386637643133363639396534333563-->
?
The **order of completion** of the branches depends on their duration and may vary between executions. Simply accumulating the results in a list does not give them a reliable business order.

Associate each result with a stable key, check for duplicates, and then explicitly sort before synthesis if the order matters. Test the same branches with reverse timeouts. A reducer must define how to combine competing writes; it must not make the meaning of the result depend on a run between network calls.

---

Why can a LangGraph concatenation reducer accumulate duplicate results? <!--anki:6130373437346434643134303465346138306465383238613339346432356535-->
?
The concatenation is associative, but **not idempotent**: adding the same result twice produces two entries, so a repeated delivery or a rerun branch can swell the list.

If each logical result is to appear only once, use a stable identifier and key merge, with an explicit rule in case of different versions. Do not confuse deduplication and display order. The reducer does not replace the idempotency of external effects.

---

Why keep artifact references rather than large documents in the LangGraph state? <!--anki:6338326563376463616138363439653338366535396563626634623437643161-->
?
A large state increases **serialization, storage, and checkpoint costs**. It can also multiply copies of sensitive data.

Keep a stable reference, version, and fingerprint, then load the details as needed. The artifact must remain accessible for the supported recovery time. A simple temporary path is not enough: after restarting on another worker, it can designate an absent or different file.

---

## Scenarios

Scenario: your graph should summarize a variable number of documents (sometimes 3, sometimes 200) and then produce a summary. How do you build it? <!--anki:6772416528637b63416b-->
?
1. **Dynamic map-reduce**: A conditional edge returns a list of `Send`, one per document, because the number is known only at runtime
2. **Accumulation reducer** on the key that collects the summaries, otherwise each branch overwrites the previous one
3. **Limit parallelism** so as not to saturate supplier quotas ([[81-litellm-api-layer|gateway]])
4. **Manage partial failures**: a document that fails should not bring down the entire synthesis
5. **Monitoring the cost**: 200 documents is 200 calls ([[122-finops-llm|FinOps]])

**Trap**: Forget the reducer and find only one summary on 200 in the final state.

---

Scenario: your team hesitates between the explicit graph and the Functional API for a process with two branches and a loop. How do you choose? <!--anki:6c30363260537e4c5e57-->
?
1. **Explicit Graph**: The stream is visible, inspectable in Studio, and lends itself to numerous branches and subgraphs
2. **Functional API**: the flow is written in classical Python (if, loops), more natural when the logic is mostly sequential
3. **Common point**: Both benefit from persistence, interruptions and recovery
4. **Practical criteria**: who will maintain? An unfamiliar team of graphs will read Python faster
5. **Common crazy guard**: `recursion_limit` and explicit output conditions, to avoid endless loops

**Trap**: Model in graph a purely linear sequence, which adds ceremony without benefit.

---

## Sources

- [LangGraph — Status, Reducers, Transitions and Command](https://docs.langchain.com/oss/python/langgraph/graph-api)

- [LangGraph — concepts and architecture](https://docs.langchain.com/oss/python/langgraph/overview)

- Supplement of the 14 November 2026 — Condition and reducers: [LangGraph — Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api).

## Connections
- [[45-langgraph-production|LangGraph — Production]] — persistance, HITL, multi-agents
- [[43-langchain-agents|LangChain — Agents]] — the high-level agent built on LangGraph
- [[31-agent-fundamentals|Agents]] — the ReAct Pattern
- [[36-agent-orchestration|Orchestration multi-agents]] — the patterns to implement
- [[41-code-nocode-automation|Automation]] — deterministic vs agent workflow
- [[48-agentic-workflow-patterns|Patterns of workflows]] — the patterns to implement in graph
- [[37-agent-frameworks|Frameworks d'agents]] — framework panorama
- [[42-langchain-fundamentals|LangChain]] — the basic building blocks of the framework
- [[47-crewai-flows|CrewAI — Flows]] — event-driven workflows
- [[115-agent-platforms-governance|Agent Platforms — Governance]] — identity, policies, audit and costs of a fleet of agents
- [[34-harness-plugins|Harness & plugins]] — the program that runs the agent
- [[38-agent-platforms|Platforms of agents]] — runtime, sandbox, tool gateway and identity
- [[39-agent-memory|Memorandum of agents]] — what the agent remembers from one session to the next
- [[40-011-langgraph-recovery-concurrency|LangGraph — Recovery, Concurrency & Evolution]] — reducers and super-steps
- [[00-moc-ai-engineering|MOC AI Engineering]]
