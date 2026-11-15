# LangChain — Contracts, tools & middleware in production — Flashcards
Tags: #flashcards #ai-engineering #agents #production
Verified on: 9 October 2026 — API cited against official documentation; limits spelled out in maps.
<!-- summary: business contracts, ToolRuntime, ToolMessage, structured outputs, errors, async, middleware, budgets, isolation, testing and upgrades, denial of authorization and fallback, propagated delays, error typing. -->


Why separate a business service from its LangChain tool? <!--anki:3135346462363938313364363461623739393665643963303534346663363931-->
?
The tool is a **model adapter**; the service carries business rules and data access. The same service can be called by a API, an agent, or a test without relying on a message history.

For example, `proposer_remboursement` produces a proposal, while a valid authorized service then executes the refund. Keeping permissions, caps, and Idempotence keys in this service prevents a framework change from changing the business guarantees.

---

How to make a LangChain tool schema useful to model reasoning? <!--anki:6636343636313162646365323462336138326337663230343633653261373632-->
?
Give explicit names, units, bounds, and descriptions that indicate **when to call the tool**. A `amount_cents` field is less ambiguous than `value`. Use enums for closed choices and reject unexpected fields if the contract requires it.

The form validation precedes the business checks: a positive integer can still exceed the refundable balance. Test the schema actually transmitted to the provider, because its subset of JSON Schema can differ from the local validator.

---

Do not confuse: ToolRuntime and tool arguments chosen by the model? <!--anki:6236303864336633656361373438656262393064333731633930333662323362-->
?
**Public arguments** describe what the model can ask for. **`ToolRuntime`** injects application-controlled information: context, state, store, and call ID, without exposing them as arguments to be generated.

An authenticated `tenant_id` must come from the context, and then be checked in the business department. Hiding this field from the model does not guarantee isolation if the SQL function or storage then forgets the hold filter.

---

Why keep the link between Aimessage.tool_calls and ToolMessage in LangChain? <!--anki:3635316236366330613934663436313662633735653136663935396236323736-->
?
Each tool result must reference the **`tool_call_id`** of the corresponding request. This link allows the model to understand which observation responds to which call, especially when several tools are requested together.

When reducing the history, keep the exchanges consistent: deleting the request while keeping its result may invalidate the conversation for some providers. A tool result is a data, not a new system statement.

---

Do not confuse: ProviderStrategy and ToolStrategy for a LangChain release? <!--anki:3930656239613133643064393462663761666439313965613233666134333561-->
?
**`ProviderStrategy`** uses the vendor's structured output mechanism; **`ToolStrategy`** represents the expected response by a structured tool call. Their availability depends on the model and integration.

The same Pydantic schema can lead to different execution paths. Check refusal, absent exit, validation error and coexistence with real tools. Compliance with the schema guarantees a structure, not the correctness of a decision.

Example: `amount: float` accepts 500 while only 50 euros remain refundable. Both policies can produce this valid object; the business control remains the same after extraction.

---

How to manage a structured LangChain output that is correct in form but wrong in business? <!--anki:6230336635653838653961633437336339386363666462376231363935386431-->
?
Add an independent **business validator** after the extraction. For a refund proposal, check order, currency, remaining amount and supporting documents before any writing.

Return an exploitable error for a bounded fix, or escalate if data is missing. A new generation does not resolve a denied access or breached business rule. Measure parsing errors, business breaches, and unproven responses separately.

For example, reject a proposal in USD for an order in EUR, even if both currencies are allowed by the schema. Re-read the business state just before execution if another request can change it.

---

What tool errors can a LangChain agent try to fix? <!--anki:6665393764383133353363663438323161363666666334346131356164376264-->
?
Distinguish between **repairable arguments**, transient unavailability, denial of permission, and negative business result. A malformed identifier can be corrected; a timeout requests a resume policy; a prohibited access must remain prohibited.

Return a stable code and minimal explanation, without secrets or stack trace. Do not silently turn an exception into "no results": this would take a failure for a lack of data.

---

Why does ainvoke not guarantee that a LangChain tool does not block the server? <!--anki:6633376261353139306566373436346162316262393133646533313731663966-->
?
An asynchronous interface does not render all its content non-blocking. A synchronous library can block the event loop; an adapter can deport it to a thread, without being able to stop the work immediately.

Use available async clients, limit simultaneous calls, and configure network-level timeouts. Test with a slow tool and multiple concurrent requests. Cancelling a coroutine does not prove that a remote action has been undone.

---

How to test the order of the middleware of a LangChain agent? <!--anki:6365323332643231303138323430636361666563303035663064356363633135-->
?
Build a case where the order changes the result: an authorization check, a cache and a retry around the same tool. Save input, output and number of invocations of each layer.

The permission must remain applied during a hit cache and recovery. A retry can repeat internal middleware; check their idempotency and total budget. Test the synchronous and asynchronous paths used by the application, rather than assume that their hooks are interchangeable.

---

Calculation: A LangChain tool call can be attempted 3 times by the middleware; each attempt allows 2 HTTP attempts in total. What maximum HTTP calls can cause a single tool call? <!--anki:3439383762663435636466343433386661653335343231643334613832393832-->
?
**3 × 2 = 6 HTTP attempts**, if all attempts fail retriable. The numbers here include the initial attempt of each layer.

A global budget must cover the attempts actually sent, not just the tool request produced by the model. Adding yet another retry at the workflow level can multiply this ceiling. Choose the layer responsible for the retakes and observe the attempts closer to the network call.

---

How to limit the tools available to a LangChain agent according to the step? <!--anki:3533313634613135313432653438306438323666636533383732393732343336-->
?
Expose the necessary **subset** to the current stage: search during the survey, proposal during the analysis, execution after validation. Dynamic selection mechanisms must maintain schemas consistent with the executor.

This reduction helps the model to choose and reduces the context. It complements the controls on the tool side: a forbidden request from an old message or a direct call must also be refused. Test the rights changes between two turns.

---

How to route a LangChain agent to another model without breaking his contracts? <!--anki:6363613966383433393865613430643138363164656632656630663663343139-->
?
Define and test the **minimum capabilities**: tools, output schema, context, modalities and data constraints. The rescue must respect them or produce an explicit failure.

Example: If the useful history exceeds the rescue window, changing only the model name is not enough. Apply a evaluated context reduction, choose another compatible model, or stop; do not silently remove the business constraints.

Trace the actual model and keep the budget consumed, tool results and action status. A fallback does not allow an unannounced degraded format or the replay of an operation already performed.

---

Why separate test data and secrets in LangChain agent fixtures? <!--anki:3037346437653234653636313433393738383731316431313332323366313539-->
?
Fixtures must reproduce messages, tool results, and useful reports with synthetic or minimized **data**. Inject clients and test identities, instead of automatically reading production identifiers.

A unit test must be able to run without a network and verify that a prohibited tool has not been executed. Reserve the real providers to integration tests explicitly configured, whose cost and destination of data are controlled.

---

How to prepare for an upgrade of LangChain and its integrations? <!--anki:3330666137653734373735303436636438623166633238333661616138393439-->
?
Pin a compatible set of versions, then test the **actually used border**: tool schemas, messages, structured outputs, middleware, and streaming. Framework, vendor, and runtime packages may evolve separately.

Compare some benchmarks and business criteria before promotion. Keep a rollback of code and persistence contracts. An installation that resolves dependencies is not a proof of behavioral compatibility.

---

Why shouldn't a permission exception trigger the technical fallback of a LangChain agent? <!--anki:3530376464313436616334623437646361363930616336613065333136366664-->
?
A **refused authorization** is a control decision, not an unavailability to be bypassed. A fallback to another tool or account could execute the action that the first path has successfully denied.

Classify errors before retry and fallback middleware. Reserve recoverable error recoveries, with the same perimeter of identity and a limited budget. Explicitly test that a refusal does not cause any alternative call with more rights. The string must explain the refusal or request the allowed information, without turning resilience into elevation of privileges.

---

Why propagate an absolute deadline through LangChain tools and middleware? <!--anki:3061393739326664653036363431646561616636393065393565343430373765-->
?
Each layer can respect its timeout while exceeding **the total user timeout**. A common deadline allows to calculate the time remaining before each call or resumption.

If the remaining budget is insufficient, stop cleanly or produce a partial expected result. Do not restart a call with a full timeout after almost exhausting the budget. The cancellation must reach the underlying operations when possible; interrupting the local wait does not guarantee their stop.

---

How can I prevent a LangChain tool technical error from being treated as business data? <!--anki:3434633035396431666562653438316161663366376266326234316533623639-->
?
Use a **discriminated result**: success with data, refusal, temporary error or indeterminate result. "503 Error" must not become the text of a document to be summarized.

Preserve the call ID and useful details without exposing secrets. The middleware decides which times are allowed; the model receives a status that allows it to request a correction or report failure. Test a legitimate empty list in the face of an unavailable search.

---

## Scenarios

Scenario: a LangChain tool accepts a tenant_id generated by the model and can view orders from another client. How do you fix the contract? <!--anki:3666643161343134393335643431363339653638623438623365316438346162-->
?
1. Remove the hold of public arguments and construct the context from the authenticated identity.
2. Apply permission and hold filter in the business department.
3. Check caches and shared memories, which must respect the same border.
4. Test a malicious request, direct access to the tool and a change of rights.

**Trap**: Replace only the description of the tool with "do not consult other customers".

---

Scenario: After adding retry middleware, LangChain queries are four times more expensive and some of them exceed their time. How do you investigate? <!--anki:3737336165646364343964373463643738326637316233373065646237306637-->
?
1. Count real calls by model, tool, integration, and HTTP attempt.
2. Identify the layers that start the same operation again.
3. Choose retriable errors and clear recovery responsibility.
4. Enforce a common budget and deadline, and then test an extended outage.

**Trap**: Limit only the number of turns of the agent, while internal attempts remain invisible.

---

Scenario: a LangChain fallback returns free text where the application expects a Pydantic proposal. How do you avoid an incorrect business action? <!--anki:6531336565343837666633373463343161653836626366353933663738343434-->
?
1. Check the compatibility of the backup model with tools and structured output.
2. Deny execution as long as structure and business rules are not validated.
3. Return an explicit failure or help request state.
4. Add this case to the integration test and trace the strategy actually used.

**Trap**: Extract an amount from the text with a regular expression and then execute automatically.

---

## Sources
- [LangChain — Tools and ToolRuntime](https://docs.langchain.com/oss/python/langchain/tools)
- [LangChain — structured outputs](https://docs.langchain.com/oss/python/langchain/structured-output)
- [LangChain — custom middleware](https://docs.langchain.com/oss/python/langchain/middleware/custom)
- [LangChain — tests](https://docs.langchain.com/oss/python/langchain/test)

## Connections
- [[42-langchain-fundamentals|LangChain — Fundamentals]] — component contracts
- [[43-langchain-agents|LangChain — Agents]] — middleware composition
- [[32-tool-calling|Tool calling]] — validate requests and results
- [[103-agent-defenses|Defenses of agents]] — permissions applied by the service
- [[90-013-agent-testing-recovery|Agents — Contracts, failures & recoveries testing]] — test tools and contracts
- [[00-moc-ai-engineering|MOC AI Engineering]]
