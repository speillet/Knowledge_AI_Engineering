# LLM application reliability & resilience — Flashcards
Tags: #flashcards #ai-engineering #system-design #reliability #production #llm
<!-- summary: timeouts, recoveries, fallbacks, circuit breaker, retry, fallback or circuit breaker, recoveries multiplied between layers, poorly formed outputs, graceful degradation, spleen limits, long tasks, version pinning, SLO, chaos testing, classification of errors of a circuit breaker, jitter, recovery after 429. -->


Why is a LLM application more fragile than a traditional application? <!--anki:47364949697173294a73-->
?
It depends on a service. **external, Slow, Expensive and non-deterministic** : Latencies from several seconds to several minutes, **rate limits**, failures of the supplier, **ill-formed exits**, and changes in behavior during **updates of the model**. Resilience must be **Designated**, not added after the fact.

Even self-hosted, a model retains outputs to validate and limited resources. Distinguish technical success and business success: HTTP 200 can carry an unusable response. Provide timeouts, validation, recovery budget and explicit degraded mode.

---

Which timeouts to set up on calls to a LLM? <!--anki:455f43415a692f2c7b6f-->
?
Differentiate between **connection**, waiting for the first useful response, **flow inactivity** and **total duration**. These delays protect against different problems: inaccessible network, excessive waiting, blocked stream or task that drags on.

A long TTFT can come from the queue, the prefill, the reasoning or the transport; it does not by itself prove a saturation. Spread a global deadline to the tools and retrieves, then cancel the downstream work if it expires. Test the heartbeats: regular bytes can maintain a live stream without providing useful content to the user.

---

How to correctly retrieve a API LLM? <!--anki:47233729762a372f7c5f-->
?
- Only on **transitional** errors (429, 5xx, timeouts), **never** on 400 (invalid request).
- **Backoff exponential with jitter**, respecting the header **Retry-After**.
- **Limited** Attempts and **Budget of global recoveries** to not amplify a failure.
- Pay attention to the actions **not idempotent** of an agent (payment, e-mail): no blind retry.

Each attempt consumes the remaining time and can already be charged. On timeout of a write, search for its result by ID before replaying; distinguish lost response and operation certainly not executed.

---

What is a fallback chain? <!--anki:4b612e3c3921336d733a-->
?
A limited **suite of fallback solutions**, chosen according to error and contract: another compatible backend, another model evaluated, or explicitly announced degradation ([[81-litellm-api-layer|fallbacks LiteLLM]]).

Example: after unavailability of a region, a second authorized region may be appropriate; after invalid arguments, changing region probably doesn't fix anything. Another model may also miss the required schema or context window.

Keep overall time and budget, avoid failures common to backends and do not replay an already executed effect. Stop the string when no eligible option remains. A static FAQ can inform, without being counted as complete resolution of any request.

---

What is a circuit breaker and why use it? <!--anki:424258362c2624254676-->
?
A component that **stops calls temporarily** after a provider's failure rate exceeds a threshold, switching directly to a fallback. It avoids waiting for repeated timeouts and overloading an already struggling service.

It has three states: **closed**, calls pass; **open**, calls stop for a period such as 30 seconds; **half-open**, a few test requests pass, and successful tests close the circuit. Compute the threshold over a sliding window with a minimum request count, for example 50% failures across at least 20 requests, so two isolated failures do not trigger it.

---

How to manage a poorly formed LLM output in an application? <!--anki:507e476873755e536655-->
?
1. **Warning**: [[63-guided-generation|structured outputs]] / constrained decoding.
2. **Validate**: schema (Pydantic, JSON Schema) + business rules.
3. **Repair**: Re-call with **the validation error** message (1 or 2 times max).
4. **Degrade**: default or explicit error, never an invalid output propagated downstream.

A default value must be explicitly allowable and marked as such. For an invoice, replacing an illegible amount with zero can be syntactically valid but dangerous; prefer an incomplete status and a review.

---

What is the graceful degradation of a LLM service? <!--anki:706e317761743a564431-->
?
Continue to make a **service reduced but compliant with an explicit contract**: evaluated backup model, non-essential functions disabled, limited additional time or human transfer. Each mode defines what it can still promise and how to return to normal.

Answering without RAG is only acceptable if the task allows a non-documentary response; for an internal procedure, it is often better to abstain. A queue must have limited capacity and time limit. Also test permissions, quality and user messages in each degraded mode.

---

How to manage a provider's rate limits? <!--anki:71434b7834454773454e-->
?
Respect the **allowed quotas** of requests, tokens and concurrency, which can be shared by organization, project, model or region. An upstream limiter and bounded queues avoid sending a load already doomed to refusal.

Prioritize the interactive, consider Retry-After, and limit retractions. Request more capacity or allocate to authorized and validated deployments if necessary. Multiplying keys does not necessarily create a quota and should not be used to bypass a common limit. Test the ability of backup before a failure.

---

How to make a long-term agent task reliable? <!--anki:6432522c7d30417a6769-->
?
- Run it **out of HTTP request** (task file, durable workflow).
- **Checkpoint status** at each step to resume after a failure ([[45-langgraph-production|durable execution]], [[41-code-nocode-automation|Temporal]]).
- **Idempotence** of edge effects tools (idempotency key).
- **Limits**: number of steps, tokens budget, duration.

Test a crash after the business effect but before its checkpoint. On resuming, check the persistent operation with the same identity instead of assuming that it did not take place. An "unknown, verification in progress" status is better than a false failure followed by a duplicate.

---

Why pin the model version? <!--anki:5043614c313623677e64-->
?
An alias type "latest" can **change model without warning** → behavior, format or cost modified in production. We pin a **date version**, we **test** the new version on evals, then we voluntarily migrate — and we monitor the **dates of depreciation** of suppliers ([[113-monitoring-drift-feedback|API model Updates]]).

Pinning does not prevent any depreciation or infrastructure change around the model. Keep the combination prompt, tools and validated parameters, then test a replacement before the deadline; provide a review date and a compatible backup route.

---

Which SLO to set for a LLM application? <!--anki:6c773648497256297b71-->
?
- **Availability** (rate of successful queries, including fallbacks).
- **Latency**: TTFT p95, total duration p95 per task type.
- **Quality**: valid exit rate, online eval score above a threshold.
- **Cost** per request under a ceiling.

With a **error budget** that decides when to freeze changes ([[64-inference-metrics-slo|SLO of Inference]]).

Define for each indicator population, window and processing refusals, timeouts and cancellations. An HTTP 200 with a false amount does not count as business success; separate validity of form and useful accuracy.

---

How to test the resilience of a LLM application? <!--anki:68407a3a592331445669-->
?
By **chaos testing**: inject 429, timeouts, cut streams, invalid responses, an empty index, and check that fallbacks, circuit breakers and degraded messages are working. And **load tests** with prompt **realistic** lengths (the load depends on the tokens, not the number of requests).

Fix before the test the expected behavior and business invariants. Cut after an external effect and then resume checks more than a simulated timeout before any call; also check absence of duplicates and effective cancellation.

---

Do not confuse: retry, fallback and circuit breaker? <!--anki:712c79247c783766604f-->
?
- **Retry**: **Replay the same request** on the same provider, for a transient error
- **Fallback**: send the request **elsewhere** (other model, other provider, degraded response) when the first choice fails
- **Circuit breaker**: **Stop calling** a failed provider for a while, so as not to stack timeouts

They are chained: a few retries, then fallback, and the circuit breaker avoids paying these retries when the breakdown is frank ([[82-routing-llm|routing]]).

---

What happens if each layer of a system tries again three times? <!--anki:64766361467b4e364763-->
?
The Retirees **Multiply** Front, orchestrator and client LLM To 3 Attempts are made to each **3³ = 27 Calls** to the provider for a user request. During a partial breakdown, It is a **Storm of Retries** which prevents the service from recovering, and which costs in tokens.

Parades: Retry at **a single layer**, **global withdrawal budget** (e.g. 10% traffic), **jitter** to desynchronize clients, and **circuit breaker** ([[82-routing-llm|fallbacks]]).

---

Calculation: with 99.5% independent availabilities and a perfect toggle, compare three mandatory serial services to two redundant providers. What average downtime on 30 days? <!--anki:3430313231643964333833343465356439306135343731396564333462393436-->
?
Under the assumption of **Independence** and perfect rocking:
```text
3 series mandatory services: 0.995³ ≈ 0.985075
→ about 10.75 hours unavailable on 30 days
2 fournisseurs redondants : 1 − (1 − 0,995)² = 0,999975
→ approximately 1.08 min unavailable on 30 days
```
In series, it is the **availability that multiply**. In redundancy, we multiply the probabilities of simultaneous unavailability. The fallback does not protect a common gateway in failure; correlation, detection delays, backup capacity and failover degrade the real result ([[82-routing-llm|fallbacks]]).

These times represent a theoretical translation of the probabilities into expected duration. They do not describe the frequency or the duration of each incident: the same availability can correspond to a long failure or many micro-cuts.

---

Why should a circuit breaker distinguish between vendor failure and query error? <!--anki:3632643539613639346636623436333061363833336131333665313131373836-->
?
A **circuit breaker** temporarily suspends calls to a failed dependency. If it counts an invalid entry or a business refusal as a global failure, a few requests can block the service for all.

Classify recoverable errors, contract errors and business decisions; choose the range of the circuit by dependency or relevant route. Test the reopening with limited traffic and a budget shared with the entries. A toggle must preserve rights, format and data constraints. The circuit protects the capacity; it does not correct an incorrect request.

---

Why add jitter to the backoff of LLM calls? <!--anki:3736666163636631366537653431623561336232663632636162656237323438-->
?
Customers who fail together can **try again at exactly the same time**, creating repeated waves. The jitter distributes the attempts over time.

The jitter does not create capacity: if the normal load sustainably exceeds the quota, reduce the admission or increase the authorized capacity.

---

Why not automatically resume all 4xx HTTP codes of a API LLM? <!--anki:6465643931316238303865353431633138376339363063323066616264393533-->
?
Many indicate **a persistent issue for this query**, such as an invalid schema or missing permission. Retry the same squanders budget and quota.

Classify according to the contract: correct the request, renew access in a controlled way or wait for some 429. Check the status of an operation if the effect is uncertain. The code alone does not always describe the whole cause; keep the useful details without secrets.

---

## Scenarios

Scenario: during a peak, your application massively returns 429 and your withdrawals worsen the situation. What do you correct in order? <!--anki:64417942635e45495449-->
?
1. **Stop Amplification**: exponential backoff with jitter, compliance with recovery header, global budget of recoveries
2. **Customer-side limiter**: do not send requests that are intended to be rejected, with priorities (interactive before batch)
3. **Circuit breaker**: cut to the supplier in difficulty and switch directly to the fallback
4. **Distribute within allowed limits**: validated regions or suppliers, reserved flow or additional quota requested ([[81-litellm-api-layer|gateway]])
5. **Degradate**: small model, queue, explicit message, rather than an error page

**Trap**: Blindly retry a non-idempotent action, such as sending an email or making a payment.

---

Scenario: your team wants to “test resilience” before a critical start to production. What do you propose concretely? <!--anki:427533363e3e53507373-->
?
1. **Inject failures**: 429, timeouts, stream cut to full streaming, invalid response, empty index
2. **Check each parade**: really functional fallback, circuit breaker that opens, degraded message displayed
3. **Realistic load tests**: Prompt length distribution, not just a number of requests
4. **Check timeouts** at all levels: connection, first token, between tokens, global
5. **Check for restarts**: A missed agent task must start from its last point ([[45-langgraph-production|durable execution]])

**Trap**: Test a fallback that has never been evaluated, and discover that it produces unusable responses.

---

## Sources
- [Google SRE — overload and admission](https://sre.google/sre-book/handling-overload/)

- 14 November Supplement 2026 — Semantic HTTP Errors: [IETF — RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html).

## Connections
- [[141-system-design-llm|System Design LLM]] — the set method
- [[81-litellm-api-layer|LiteLLM]] — retries, fallbacks, load balancing
- [[63-guided-generation|Guided generation]] — outputs valid by construction
- [[45-langgraph-production|LangGraph production]] — durable execution
- [[64-inference-metrics-slo|Metrics & SLO]] — set goals
- [[93-monitoring-inference|Monitoring of inference]] — detect failures
- [[84-streaming-application-integration|Streaming & integration]] — idempotency and long tasks
- [[145-system-design-cases|Case of system design]] — of commented type architectures
- [[149-delivery-idempotency-concurrency|Idempotence & competition]] — secure retries and manage unknown results
- [[116-ai-sre-incidents-capacity|SRE: incidents & capacity of AI services]] — switch mechanisms to their exploitation
- [[00-moc-ai-engineering|MOC AI Engineering]]
