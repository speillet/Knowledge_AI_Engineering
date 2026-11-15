# Tool calling — Flashcards
Tags: #flashcards #ai-engineering #agents #tool-calling #llm
<!-- summary: tool definition, controlled parallel calls, tool calling or MCP, validation of arguments, errors and timeouts, operation statuses, pagination and cost of schemas, separation proposal and execution, voluminous results, writing preconditions. -->


What is tool calling (function calling)? <!--anki:4c434c62492628352f4a-->
?
The LLM **proposes a structured call**: tool name and arguments. The application validates and then executes the authorized operation and returns its result to the model, associated with the call ID.

Example: `order_status(id="C42")` requests a read, not a proof that C42 belongs to the user. The backend controls this membership and distinguishes command absent, access denied and technical unavailability. The model can then respond or request another tool.

The schema best guarantees the **form** of the arguments; neither their veracity, nor the authorization, nor the success of the execution derive from the JSON. A proposed call is not an action accomplished.

---

Does the model run the tools itself? <!--anki:672f7363513542412f2f-->
?
**No.** The model only **generates the call intent** (name and arguments); it is the application, the harness, that executes and returns the result.

Essential consequence: it is **in the application** that we control what is really running. Validation of arguments, permissions, human approval and logging are placed between the intent of the model and the execution ([[34-harness-plugins|harness]]).

For example, `refund(order="C7", amount=50)` can be well-formed but exceed the refundable balance. The application must refuse before the business effect, and then transmit this refusal to the model without turning it into success.

---

How do I declare a tool to the model? <!--anki:745d3a6878654160442b-->
?
By a definition including **name, description and schema of parameters**, depending on the format of the provider.
```json
{
  "name": "order_status",
  "description": "Return the order status for the authenticated customer.",
  "input_schema": {
    "type": "object",
    "properties": {
      "order_id": { "type": "string", "pattern": "^CMD-[0-9]{6}$" }
    },
    "required": ["order_id"]
  }
}
```
The supported constraints (types, patterns, enumerations) describe the expected arguments; their application depends on the mode used ([[63-guided-generation|guided generation]]). These definitions occupy context with each call: 40 tools, that is thousands of tokens each turn ([[123-aggressive-caching|caching]]).

The schema describes the **acceptable arguments**, not the rights of the requester. Even with a well-formed identifier, the application must verify that the command belongs to the connected client. The identity comes from the authenticated session, never from a free argument provided by the model. Also test missing values, unexpected fields and validation errors.

---

What does the tool calling loop look like? <!--anki:474750306946343634-->
?
```text
prompt → model emits tool_call(name, args)
→ app runs → result returned to model
→ new tool_call or final answer
```

On each turn, the application **validates the name and arguments**, controls permissions, executes with a timeout, and returns a structured result or error. The model can then correct its request or respond. Keep call identifiers and limit iterations. For an action with external effect, provide idempotency so that a resume does not create duplicates.

With two simultaneous calls, attach each observation to its identifier, not to its order of arrival. Otherwise the model can assign the result of one command to another.

---

What are parallel tool calls? <!--anki:482f5a41654854453b58-->
?
Multiple tool requests issued during the same model response. The application can run them simultaneously **after verifying their independence**: two non-dependency searches can be paralleled; a write followed by a reading of its result must wait.

The model can offer incompatible or competing calls on the same resource. Comply with the protocol of results, permissions and limits of concurrency, and then transmit partial successes and failures with their identifiers. The gain in latency depends on the dependencies and capacity of the services called.

---

Do not confuse: tool calling and MCP? <!--anki:7154542972474730592e-->
?
The **tool calling** is the mechanism by which a model proposes a tool name and its arguments; the application controls and then executes the request. **MCP** organizes the exchanges between clients and servers to expose tools, resources and prompts.

You can use coded tools directly without MCP. Conversely, a client can read a resource or invoke a tool MCP from code or an interface, without a decision of one LLM. MCP does not depend on the native tool calling of a model; The two combine in an agent.

---

What to do when a tool fails? <!--anki:4d4a3b542c376265564f-->
?
Distinguish between **invalid arguments, denial of permission, temporary failure, and unknown result**. Provide a structured and actionable error when the model can correct its request.
```text
INVALID_ARGUMENT: command_id must follow CMD-000000.
Use search_commands if the identifier is unknown.
```
Bound raises; do not expose secrets or internal traces. A timeout after a write can hide a success: check the state or status of the operation before repeating it. A refusal of permission is not bypassed by another tool. The harness must be able to stop or escalate unrecoverable failures.

---

Why is the description of tools critical? <!--anki:457254495d344e7c3357-->
?
The **name, description and schema** guide the choice of the tool and its arguments, with the setpoint, history and observations already available.
- Vague : `search(q)` — « Recherche. »
- Explicit: `rechercher_commandes(email_client)` — "List orders, most recent first; does not provide package tracking."

Specifying use cases, limits and result structure helps the model to choose. Measuring errors on representative tasks; a good description does not grant any rights and does not exempt from validating the call.

---

What is the syntactic reliability of arguments based on? <!--anki:446e47724d4a2d696c7b-->
?
A constrained **decoding** can impose a supported schema during generation. This property depends on the model, mode, and constraints actually supported; declaring a JSON Schema is not enough to enable it.

Verify that the call is complete and actionable: refusal, error or truncation require separate processing. Then validate server-side arguments. Their **semantic validity** remains independent of the format: a well-formed identifier can target another client, an amount exceeding a ceiling. See [[63-guided-generation|guided generation]].

---

Calculation: 40 tool schemas of 300 tokens each are sent with each of an agent’s 25 calls. What volume and cost to 3 €/M as input, and then what cost if all those tokens are read to 10% from the tariff from an already hot cache? <!--anki:3232623534646231383763363464303539666437323536306133333231383237-->
?
Assumptions: 300 tokens by tool scheme, returned on each call, 3 €/M as input.
```text
Diagrams: 40 × 300 = 12,000 tokens for every call
per task: 12,000 × 25 towers = 300,000 tokens ≈ 0.90 €
with prompt caching (≈ 0.1×) ≈ 0.09 €, but the context remains busy
```
Beyond the cost, 12,000 tokens diagrams occupy context and can complicate the choice of tool: we expose only the tools useful to the task, or we load them on demand ([[35-context-engineering|context engineering]]).

The hot scenario excludes the boot cost and assumes all affected tokens eligible for each read. A changed or reordered schema can break the prefix; compare the actual usage counters to the estimated cost.

---

What should the result of a tool expose to avoid a false agent success? <!--anki:6464383461663535363034323436316639313236656439633664643934316637-->
?
A **exploitable status**, the necessary data and their limits: error, partial result, version consulted or operation still in progress.
```json
{"status": "pending", "operation_id": "op-42", "completed": false}
```
An acknowledgement of receipt does not prove that the action is complete. Provide for a status consultation or a business auditor, and associate each result with the correct call. The contract must distinguish "no data", "incomplete search" and "service unavailable", otherwise the model can invent a conclusion.

---

Why does pagination of a tool distort an agent's conclusion? <!--anki:3330393863376537633037333466303339633164323932626139346537333561-->
?
A **page-limited** result does not necessarily represent the entire collection; the agent can conclude "no recent orders" after reading only the first elements of another sort.

Indicate filters, order, limit, presence of a continuation and continuation cursor. Prefer a service-side filter or aggregation for a global question. If the budget does not allow to browse all the pages, announce the perimeter actually consulted. Evaluate the tasks whose proof is after the first page.

---

Why should a proposal tool be separated from a runtime tool? <!--anki:3337613762613866656336363461633538633337313562636234633634396666-->
?
The **proposal** calculates and describes an action; the **execution** applies an authorized effect. This separation allows to validate recipient, amount and consequences before writing.

For example, preparing a refund returns a versioned proposal; execution requires its identifier, a still valid authorization, and an idempotency key. If the settings change, revalidate instead of reusing an old agreement. Separation of tools helps the interface; the server still needs to check the rights and business status when acting.

---

How should a tool return a result that is too large for the context of the model? <!--anki:3963323033653962613033633439663062383330633566363862356238616530-->
?
Return **a bounded summary, a stable identifier, and a way to view details** by page, filter, or range. Explicitly report any truncation and total volume when known.

The model can then request the necessary parts without erroneously concluding that it has seen everything. Keep the original proofs out of the prompt. A silently cut string can remove an error, an exception, or the last lines of an array and reverse the conclusion.

---

Why include an expected version in a tool that modifies a business object? <!--anki:6432393932303366323035303434336639353639306363343762326134333566-->
?
The version allows a **conditional write**: apply the change only if the object has not changed since it was read. For example, updating the folder to version 7 must fail if its current version is 8.

The service must verify this condition atomically. The agent then rereads the file and re-evaluates the proposal. Idempotence avoids repeating the same operation; it does not alone protect against a decision based on an old state.

---

## Scenarios

Scenario: your agent has 40 tools and often gets the wrong tool or invents parameters. How do you improve the situation? <!--anki:45503a33472d5921333f-->
?
1. **Reduce choice**: expose only useful tools to the current task, even if it means filtering them dynamically
2. **Care for descriptions**: Explicit name, use case, which the tool does not. This is prompt engineering
3. **Merge or Separate** : grouping redundant tools, Separate those who do too much
4. **Constrict arguments** by the JSON Schema, with enumerations rather than free text ([[63-guided-generation|guided generation]])
5. **Measure**: valid call rates and good tools chosen, by tool, before and after ([[96-evals-rag-agents|evals d'agents]])

**Trap**: Add an additional tool to fix previous errors.

---

Scenario: a tool call fails in production with a timeout, and your agent tries again in a loop with the same arguments. What do you fix? <!--anki:423c3d21382d71634132-->
?
1. **Qualify operation**: read without effect or write whose result is unknown.
2. **Reconcile status** after writing: check status before repeating.
3. **Borne restarts** retryable, with deadline, backoff and idempotency key if the service manages it.
4. **Transmit a clear** status to the model; invalid denials and settings are not treated as a network outage.
5. **Check the business result**, then stop or escalate if uncertainty persists.

**Tip**: Assume that a timeout means the action did not take place.

---

Scenario: an agent claims that a customer has no outstanding invoices after reading 20 invoices, but the tool also returns a continuation slider. How do you fix it? <!--anki:3339626162663531323736303465376139363334636464656665643732633261-->
?
1. **Check the contract**: filter, sort and meaning of the cursor.
2. **Search service side** for unpaid bills, or browse pages if no targeted query exists.
3. **Distinguish full and partial**, with explicit budget and status.
4. **Check the conclusion** on customers whose unpaid is on a later page.
5. **Restore uncertainty** if verification remains incomplete.

**Trap**: Turn the absence of an element in the page being read into evidence of its overall absence.

---

## Sources

- [MCP 2025-11-25 — tools and invocation by customer](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)
- [MCP 2025-11-25 — application-driven resources](https://modelcontextprotocol.io/specification/2025-11-25/server/resources)
- [Anthropic — define tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools)
- [Anthropic — design results and evaluate tools](https://www.anthropic.com/engineering/writing-tools-for-agents)

## Connections
- [[31-agent-fundamentals|Agents]] — the loop that consumes the tools
- [[63-guided-generation|Guided generation]] — the syntactic guarantee
- [[33-mcp|MCP]] — standardize access to tools
- [[34-harness-plugins|Harness]] — that actually runs
- [[101-llm-security-guardrails|LLM Security]] — validate before running
- [[103-agent-defenses|Security agents — Defensive architecture]] — validate tool calls
- [[165-computer-use-browser-agents|Computer use & browser agents]] — agents that use interfaces
- [[22-advanced-rag|RAG — Advanced]] — hybrid search, reranking and filters
- [[26-text-to-sql|Text-to-SQL]] — answer numerical questions on tables
- [[37-agent-frameworks|Frameworks d'agents]] — framework panorama
- [[41-code-nocode-automation|Automation code & no-code]] — workflows and no-code tools
- [[42-langchain-fundamentals|LangChain]] — the basic building blocks of the framework
- [[40-010-langchain-tools-middleware-production|LangChain — Contracts, tools & middleware in production]] — validate requests and results
- [[00-moc-ai-engineering|MOC AI Engineering]]
