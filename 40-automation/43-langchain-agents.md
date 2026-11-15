# LangChain — Agents & middleware — Flashcards
Tags: #flashcards #ai-engineering #agents #langchain #llm
Verified on: 25 September 2026 — This factsheet lists products, versions or regulatory texts that are evolving quickly.
<!-- summary: `create_agent`, memory by checkpointer and `thread_id`, `response_format`, middleware hooks, middleware provided (human-in-the-loop, summary, fallback, limits), runtime context, Deep Agents, multiple entries between layers, restore budgets, filter results. -->


What is `create_agent`? <!--anki:7a4b2e797a59726e6d3e-->
?
The LangChain v1 function that builds a **out-of-the-box agent**: a model, tools, a system prompt, and the **loop** model → tools → model up to the final answer ([[31-agent-fundamentals|ReAct]]).

```python
from langchain.agents import create_agent

agent = create_agent(
    model="anthropic:claude-sonnet-4-5",
    tools=[get_weather],
    system_prompt="You are a concise weather assistant.",
)
result = agent.invoke({"messages": [{"role": "user", "content": "Weather in Lyon?"}]})
print(result["messages"][-1].content)
```

In this example, `get_weather` must already be defined and model integration configured. The function builds the loop, but it remains to limit calls, validate tools, and handle failures. The last response must be checked according to the task, even if the execution ends normally.

---

What is `create_agent` built on? <!--anki:48725f6e587475697364-->
?
On **[[44-langgraph-fundamentals|LangGraph]]**: `create_agent` builds a compiled graph orchestrating model and tools. It benefits from its streaming, persistence and interruption mechanisms when configured.

Example: After restarting, continuing a conversation requires a durable checkpointer and the same thread ID; recreating the agent object with its own tools does not automatically reload the old exchange.

Separate **graph definition, execution status, and external effects**. Persistence of the state does not make a business write unique: a replayed tool can repeat it. Validate resume and idempotency by a real stop of the process, not just by two successive calls.

---

How do I give an agent a conversation memory? <!--anki:412f743a4b36626b4447-->
?
By passing a **checkpointer** and reusing the same **`thread_id`** from one call to another: the thread history is automatically reloaded.

```python
from langgraph.checkpoint.memory import InMemorySaver

agent = create_agent(model=..., tools=[...], checkpointer=InMemorySaver())
config = {"configurable": {"thread_id": "conv-42"}}
agent.invoke({"messages": [...]}, config=config)
```

`InMemorySaver` is suitable for a demonstration, but loses the history when the process stops. In production, choose a durable backend and verify that the user is allowed to access the requested thread. Reusing a shared identifier between users would mix their conversations and could expose their data.

---

How do I get a structured final response with create_agent from LangChain? <!--anki:6e2d72285b7b3141633b-->
?
With `response_format=MonModelePydantic`: the agent ends with a validated output, available in **`result["structured_response"]`**.

The Pydantic model describes the expected fields, types, and constraints, e.g. `category` and `priorite` for a ticket. The policy used depends on the provider's support. Explicitly deal with impossible validation, refusal, and exhausted budget. Then check the content: a priority allowed by the schema may still be unsuitable for the problem described.

An absence of `structured_response` must not become an object filled with default values. Expose an explicit failure to the consumer and keep the cause for diagnosis.

---

What is a middleware in LangChain? <!--anki:704e5b615d724d26394b-->
?
A component that **inserts itself into the agent's loop** to observe or modify its behavior (context, model calls, tool calls) without rewriting the loop. This is the main extension point of v1, comparable to the hooks of a [[34-harness-plugins|harness]].

A middleware can limit the number of calls, adapt visible tools or intercept an error. Its location and stacking order count: a retry can repeat an operation that another component counts. Test failure paths and keep business rules critical in executable controls, not just in a prompt change.

---

What hooks can a LangChain agent middleware implement? <!--anki:623b496e31414c772f60-->
?
- **Node style**: `before_agent`, `before_model`, `after_model`, `after_agent`
- **Style wrapper**: `wrap_model_call`, `wrap_tool_call` (for retry, fallback, cache...)
Each hook also exists in **decorator** (`@before_model`, `@wrap_tool_call`...), plus `@dynamic_prompt`.

Choose a hook based on where to act: prepare the context before the model, review its output after, or surround a call to handle errors. The order of the middlewares influences the result. Avoid multiple layers of retry silently multiply attempts and exceed the overall budget.

---

How to write a custom before_model middleware for a LangChain agent? <!--anki:62663d2665583f485161-->
?
```python
from langchain.agents.middleware import before_model, AgentState
from langgraph.runtime import Runtime

@before_model
def log_before_model(state: AgentState, runtime: Runtime):
    print(f"{len(state['messages'])} messages sent to the model")
    return None  # or a status update dict
```
A hook can also return **`jump_to`** (`"end"`, `"tools"`, `"model"`) to short-circuit the loop.

This hook observes the state without modifying it. To route with `jump_to`, declare the permitted destinations via the middleware's `can_jump_to` configuration; returning an arbitrary destination is not enough. Logs must remain sober: counting messages can be useful without saving their confidential content.

The hook can be called several times in a loop. Do not place a billing or a notification supposed unique; measure its number of invocations in a test with several turns.

---

Which ready-to-use LangChain middleware to use for human approval, compaction, model toggle or call capping? <!--anki:4a5532617776615f543e-->
?
- **HumanInTheLoopMiddleware**: Human approval before some tools
- **SummarizationMiddleware**: summarizes the near-limit history ([[35-context-engineering|compaction]])
- **ModelFallbackMiddleware**, **ModelRetryMiddleware**, **ToolRetryMiddleware**
- **ModelCallLimitMiddleware**, **ToolCallLimitMiddleware**: cap costs
- **PIIMiddleware**, **ContextEditingMiddleware**, **TodoListMiddleware**

Choose middleware based on the observed problem: loop too long, saturated context, sensitive tool or transient error. Test their order and their interaction on a concrete case. A call limit must cover all execution, while a human approval must precede the external effect that it authorizes.

---

How does human approval work with `create_agent`? <!--anki:494756303d597a3c6960-->
?
The **HumanInTheLoopMiddleware** interrupts the agent before the sensitive tools (e.g. `send_email`); the status is saved by the checkpointer. We then resume with a **`Command(resume=...)`** that contains the decision: approve, modify or reject the call ([[45-langgraph-production|interrupts LangGraph]]).

Introduce the human to the **name of the tool, its arguments and effects**. Resume the same thread with the decision corresponding to the interruption, then revalidate the modified arguments and the current rights. Storage only in memory is not enough to survive the restart of the process; provide a durable checkpointer in production.

---

How to pass the user and hold him to the runtime of a LangChain agent? <!--anki:734e286f38437868654c-->
?
By a **`context_schema`**: we pass `context=...` to `invoke`, and this data is accessible in middleware and tools via the **runtime**, without being put in the messages seen by the model.

The application constructs this context from an authenticated identity. A tool can filter a request by holding without asking the LLM to choose the holding. Do not copy these values into an unnecessary tool output, and apply service-side access controls: being invisible in the prompt is not enough to secure a data.

---

What is Deep Agents? <!--anki:7670636152256a7e7468-->
?
An "**batteries included**" layer built on LangChain agents: **planning** (todo list), **virtual file system**, **subagents** and **automatic context compression**, for long tasks.

This overlay reduces the initial assembly for a task that plans, reads, and produces artifacts. Check which backend stores the files and what isolation surrounds the code tools. Subagents and compression add behaviors to evaluate, including loss of information, tokens consumption, and spreading permissions.

---

When to go from `create_agent` to LangGraph? <!--anki:6c6473235e656b6e5743-->
?
When the flow must be **explicit**: deterministic steps mixed with agentic steps, branches and custom loops, several coordinated agents — is the domain of [[44-langgraph-fundamentals|LangGraph]].

Example: Retrieve documents, request an approval, run a process, and then check its result according to predefined branches. A graph makes the transitions and state inspectable. Keep `create_agent` in nodes where a stand-alone loop is useful; it is not necessary to reimplement each model call.

---

Why is it not enough to limit attempts in every LangChain middleware to limit the entire agent? <!--anki:6534353739633865653136303461376162653232616433636337396133366633-->
?
The **Nested Loops** can multiply attempts: three attempts in the SDK and three in a middleware allow up to nine calls for the same logical request.

Set an overall budget of time, cost and calls, consumed by all layers. Designate the layer responsible for each recovery and propagate the remaining deadline. Instrumentate technical attempt and agent turn separately. Test a provider that consistently fails: Local limits must lead to an explicit end before the overall budget runs out.

---

Why should a LangChain agent’s budget survive a human disruption? <!--anki:3535623031666166333865303431633661393164666634373139633636623362-->
?
Otherwise, a restart can reset the counters and allow **a new budget for each suspension**. The announced limit per task would no longer be real.

Persist the consumption associated with the business execution and check the remainder before each call. Distinguish new user request and continuation of the same task. The estimated tokens counters must be brought closer to the observed usage; an interruption does not refund the calls already made.

---

Where to filter sensitive data from tool results before use by a LangChain agent? <!--anki:3965343565613330336666643439636539646636326261373832663839626532-->
?
At the level of **the tool or its application border**, before insertion in the messages, traces and any summaries. A final response filter intervenes too late if the secret has already been sent to the model.

Define the fields needed for the task, then build a minimal result. Test also exceptions and logs. The middleware can centralize part of the control, but it is necessary to check the effective order of the hooks and all the output paths.

---

## Scenarios

Scenario: your LangChain agent must request a validation before sending any e-mail, cap his calls to the model and summarize the history when it grows. How do you implement it? <!--anki:51313d393b6e7032624a-->
?
1. **Do not rewrite the loop** These needs are **middlewares**, inserted in the existing agent
2. **HumanInTheLoopMiddleware** to interrupt before `send_email`, with recovery by `Command(resume=...)`
3. **ModelCallLimitMiddleware** and **ToolCallLimitMiddleware** to cap cost and loops
4. **SummarizationMiddleware** for near-limit compaction ([[35-context-engineering|context engineering]])
5. **Checkpointer** mandatory: without persistence, an interruption loses the status of the agent

**Trap**: Put "always ask for confirmation" in the system prompt and believe it is a check.

---

Scenario: your tools need the customer ID and subscription level, but you don't want the model to be able to change them. How do you do it? <!--anki:63347e7a64404f595956-->
?
1. **Do not put them in messages**: whatever the model sees, it can reformulate or invent it
2. **`context_schema`**: pass this data via `context=...` to invocation
3. **Read them in the runtime**, tools and middleware side, at run time
4. **Check tool-side rights** from this context, never from an argument provided by the model ([[103-agent-defenses|Defenses]])
5. **Trace** the actual identity used for each call ([[93-monitoring-inference|traces]])

**Trap**: pass the `tenant_id` as a tool parameter. An injection would then be enough to change the client.

---

## Sources

- [LangChain — custom middleware and routing](https://docs.langchain.com/oss/python/langchain/middleware/custom)

- [LangChain — agents and middleware](https://docs.langchain.com/oss/python/langchain/agents)

## Connections
- [[42-langchain-fundamentals|LangChain — Fundamentals]] — models, tools, messages
- [[44-langgraph-fundamentals|LangGraph — Fundamentals]] — the underlying runtime
- [[45-langgraph-production|LangGraph — Production]] — persistence and interrupts
- [[34-harness-plugins|Harness & plugins]] — middleware as harness hook
- [[35-context-engineering|Context engineering]] — context summary and editing
- [[36-agent-orchestration|Orchestration multi-agents]] — subagents, handoffs and A2A
- [[40-010-langchain-tools-middleware-production|LangChain — Contracts, tools & middleware in production]] — middleware composition
- [[00-moc-ai-engineering|MOC AI Engineering]]
