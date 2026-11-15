# LangChain — Fundamentals — Flashcards
Tags: #flashcards #ai-engineering #agents #langchain #llm
Verified on: 25 September 2026 — This factsheet lists products, versions or regulatory texts that are evolving quickly.
<!-- summary: v1, `init_chat_model` packets, messages, `@tool` and `bind_tools` tools, structured outputs, Runnables and LCEL, RAG bricks, LangSmith, structured message retention, argument streaming, call concurrency. -->


What is LangChain today? <!--anki:6d5e30397b5f6e244140-->
?
An open source framework (Python and JS) that provides **Components LLM Standardized** (models, messages, tools, retrievers) and, since the **v1**, a **Agent Harness** Minimal and configurable: `create_agent` ([[43-langchain-agents|LangChain agents]]).

It connects components via common interfaces, but the capabilities remain those of the underlying provider. Choose the abstractions useful to its application and pin the dependencies. A framework does not exempt from defining validation, authorizations, budget and evaluation; it facilitates their integration into the flow.

---

How are LangChain packages organized? <!--anki:6a7e44294e70317a3d68-->
?
- **`langchain-core`**: Basic abstractions (messages, runnables, tools)
- **`langchain`**: agents and middleware
- **Integrations**: `langchain-openai`, `langchain-anthropic`... (one package per supplier)
- **`langchain-classic`**: the old chains and features of v0, for backward compatibility

Installing only the necessary integrations limits dependencies and makes updates more readable. An import error can result from a mismatch between the main package, the core, and the provider. Pin a compatible package and check for a minimal call before migrating agents; an old example can target another generation of API.

---

How to instantiate a model via LangChain independently of the supplier? <!--anki:4e6c666e705f3a35383f-->
?
With `init_chat_model` and a `provider:model` chain: on **change provider without changing the application code**.

```python
from langchain.chat_models import init_chat_model

model = init_chat_model("anthropic:claude-sonnet-4-5")
reponse = model.invoke("Explain the RAG in one sentence.")
```

Installing vendor integration and configuring credentials is still necessary. The call interface is common, but the models differ on tools, structured outputs, parameters, and context limits. After switching vendor, replay functional tests and evals rather than assuming behavior equivalence.

Include at least one tool call, structured output, and denial: a simple "hello" validates the connection, not application compatibility.

---

What types of messages does LangChain handle? <!--anki:6e25772567323b58302f-->
?
`SystemMessage`, `HumanMessage`, `AIMessage` (which may contain `tool_calls`) and `ToolMessage` (result of a tool) — or simple `{"role": ..., "content": ...}` dicts. v1 adds **content blocks standardized** (text, reasoning, tool calls) common to all providers.

When an `AIMessage` Ask for a tool, on the `ToolMessage` must be associated with the **Identification of this call**. Confusing roles or losing this association breaks the conversation expected by the provider. Standardized blocks facilitate inspection, but their abilities vary: do not assume that each model exposes a reasoning or the same modalities.

---

How do I declare a tool with LangChain? <!--anki:4e2668233f3b707b5663-->
?
With the `@tool` decorator: the **name of the function**, the **docstring** and the **type hints** become the name, description and JSON Schema of the [[32-tool-calling|tool]].

```python
from langchain.tools import tool

@tool
def get_weather(city: str) -> str:
    """Return the current weather for a city."""
    return f"It is beautiful at {city}"
```

This example returns a **fictitious value**: a real weather tool would query a source and handle errors. A precise description helps the model choose when to call the function. Annotations describe the contract; access controls and job validation must be implemented in the application.

---

How does a model use off-agent tools? <!--anki:6873426d3e2d217e434c-->
?
`model.bind_tools([get_weather])` attaches the tool schemas; the response then contains `response.tool_calls` (name + arguments). **It is up to you to run** the tool and return a `ToolMessage` — what `create_agent` automates.

Link each result to the correct call ID, especially if multiple tools are requested. Manage unknown name, invalid arguments, and timeout without hiding the error from the model. Linking a schema does not execute anything and does not give any additional permissions: the application loop remains responsible for the actual effects.

---

How to get a structured output with LangChain? <!--anki:79644644213972374439-->
?
`model.with_structured_output(MonModele)` with a **Pydantic** model (or a JSON Schema): the call directly returns a validated object, relying on the vendor's structured outputs or tool calling ([[63-guided-generation|guided generation]]).

The schema sets fields and types, such as a category and an amount. Predict validation errors, rejections and incomplete outputs depending on the integration. Structural compliance does not prove that the extracted amount is accurate; compare it to the source and apply business rules before use.

---

What is Runnable and LCEL interface? <!--anki:78337d302c763673295f-->
?
All components exhibit the same methods: **`invoke`, `batch`, `stream`** (and their async versions). **LCEL** composes them with the `|` operator:

```python
chain = prompt | model | StrOutputParser()
chain.invoke({"topic": "the KV"})
```

Still available in `langchain-core`, but v1 focuses on agents.

In this extract, the prompt prepares messages, the model generates, and the parser extracts the text. Variables and imports must be defined in the application. This composition is suitable for a fixed pipeline; persistent repeats and complex transitions require more explicit orchestration.

---

What bricks does LangChain supply for the RAG? <!--anki:6d7c557541244b554728-->
?
**loaders**, **splitters**, **embeddings** models, **vector stores** and **retrievers**, with common interfaces to dial the [[21-rag-fundamentals|RAG]].

Example: load a PDF record, cut its pages, index the fragments and then call the retriever from `vector_store.as_retriever()`. Metadata must keep document, page, version and access perimeter until the final citation.

An interchangeable interface does not ensure the same behavior: two retrievers can filter differently or produce non-comparable scores. Test the actually returned passages and their authorization after replacement; the generation does not repair a missing passage or a lost provenance.

---

What is the role of LangSmith? <!--anki:47476469236b7933533b-->
?
The publisher's platform for **tracing, debugging and evaluating** LangChain/LangGraph applications (enabled by environment variables, e.g. `LANGSMITH_TRACING=true`). Open source alternative: [[91-langfuse-observability|Langfuse]].

A trace is used to find calls, tools, durations, and errors in a request, and then make it a case of evaluation. Configure the data actually sent and their retention before activating the collection. Observability does not require storing all the secrets or all the raw content.

For a slow tool, compare its duration to that of the model and the shrinkages. A high total time does not, on its own, indicate which component to optimize.

---

Which review often comes back on LangChain? <!--anki:4f6a534f5b2a36356f23-->
?
Thick **abstracts** that mask the prompt actually sent and **APIs that have changed a lot** between versions. The v1 replied by **simplifying** (only one `create_agent`, old chains moved in `langchain-classic`).

To limit this risk, pin versions, view migration guides, and keep contract tests on messages and outputs. Examine a real trace during unexpected behavior. Simplifying the API does not remove the need to understand the loop and the transformations applied to data.

---

Why can normalizing a LangChain message in plain text lose essential information? <!--anki:3135383764613266326130633439613861313436346434623534366638663263-->
?
A **message** can contain text, tool calls, correlation identifiers, multimodal content, and metadata. Converting everything into a string can remove the link between tool request and result or confuse final text and intermediate content.

Keep structured objects to boundaries that require text, and then explicitly choose which blocks to display. Test a response without text but with tool call and a message containing multiple blocks. Portability depends on the contract retained, not just a common call method.

---

Why wait until the end of a streamed tool call before validating its LangChain arguments? <!--anki:6662636636353065353964633434646161633862653765666138343033376234-->
?
Received fragments can form **an incomplete JSON**, and a started value can still be extended. Do not perform an action on the first fragment that seems plausible.

Assemble fragments by call ID, verify the end, and then parse, validate, and authorize. Test multiple intermingled calls and a disconnection in the middle of the argument. Progressive display may be useful, but validating a complete proposal remains a separate step in its execution.

---

Why don't multiple asynchronous LangChain calls guarantee higher throughput? <!--anki:6562386234363234623234663439393261343064383361623338656565363132-->
?
The concurrency can saturate **quotas provider, connections, CPU or memory**. Errors and recoveries then increase faster than valid results.

Block in-flight calls and measure payload, wait, and 429. Task batches must share the limits of the called dependency. An asynchronous function facilitates concurrent wait; it does not increase either the capacity of the provider or that of a local blocking component.

---

## Scenarios

Scenario: your management wants to be able to change model provider in case of price increase, without rewriting the application. How do you structure the code? <!--anki:6c2447527d2a5d675f62-->
?
1. **Abstract model access**: `init_chat_model("provider:model")`, the name coming from the configuration and not the code
2. **Stick to common interfaces**: standard messages, `@tool`, `with_structured_output`, to avoid vendor peculiarities
3. **Pass through a gateway** for keys, budgets and toggles ([[81-litellm-api-layer|LiteLLM]])
4. **Test the toggle**: replay the evals on the backup model, because the prompts do not always transpose ([[114-reproducibility-variance|Comparison Paired]])
5. **Monitoring**: quality, latency and cost per model, to decide with numbers ([[82-routing-llm|routing]])

**Trap**: Believe that a model change is neutral. Code is portable, behavior is not.

---

Scenario: your data extraction sometimes returns invalid JSON, and you chain the `try/except` to catch up. What do you change? <!--anki:6f787361626c783c4351-->
?
1. **Stop asking for a format**: the **constraint** with `with_structured_output` and a Pydantic model ([[63-guided-generation|guided generation]])
2. **Validate content**, not just syntax: bounds, enumerations, consistency between fields
3. **Provide for failure**: an explicit "not found" field rather than an invented value
4. **Tester** on actual documents, including malformed documents
5. **Measure** the rate of valid outputs as production metric ([[93-monitoring-inference|validations]])

**Trap**: Fix the JSON with regular expressions, which hides the real extraction errors.

---

## Sources

- [LangChain — documentation Python](https://docs.langchain.com/oss/python/langchain/overview)

- 14 November 2026 — Tool call fragments: [LangChain — models and streaming](https://docs.langchain.com/oss/python/langchain/models).

## Connections
- [[43-langchain-agents|LangChain — Agents & middleware]] — `create_agent`
- [[44-langgraph-fundamentals|LangGraph]] — runtime under LangChain agents
- [[37-agent-frameworks|Frameworks d'agents]] — panorama
- [[32-tool-calling|Tool calling]] — what `@tool` and `bind_tools` encapsulate
- [[21-rag-fundamentals|RAG]] — brick loaders, splitters, retrievers
- [[40-010-langchain-tools-middleware-production|LangChain — Contracts, tools & middleware in production]] — component contracts
- [[00-moc-ai-engineering|MOC AI Engineering]]
