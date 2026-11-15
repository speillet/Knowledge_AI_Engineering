# LiteLLM (API layer) — Flashcards
Tags: #flashcards #ai-engineering #api-layer #litellm #llm
Verified on: 25 September 2026 — This factsheet lists products, versions or regulatory texts that are evolving quickly.
<!-- summary: SDK or proxy, virtual keys, budgets, rate limits, fallbacks, load balancing, observability callbacks, alternatives (self-hosted gateways, cloud services, aggregators), reconciliation with provider billing, streaming and fallback, competing budget. -->


What is a API layer (LLM gateway)? <!--anki:79752c38462d5a6c3765-->
?
A **common interface in front of several backends**, cloud or self-hosted, which centralizes authentication, Routing, Budgets and observation.

Example: An application uses a business alias; the gateway resolves it to an authorized provider for that team and category of data. The model actually chosen must remain traceable.

Unifying API does not make the capabilities identical: check tools, structured outputs, streaming and context limits after routing. This layer also becomes a critical dependency; provide availability, versioned configuration and failure tests. A fallback must not send data to a prohibited provider under the guise of maintaining the service.

---

What is LiteLLM? <!--anki:496b6e43213c2b593774-->
?
An open source project that exposes **more than 100 providers of LLM in the format of the API OpenAI**. It exists in two forms: a **Python SDK** and a **proxy** (gateway server).

The common interface simplifies the client code, but does not erase all vendor differences: parameters, tools, schemas and errors may vary. Check the capabilities of the chosen model and integration. Test the exact path of the application before considering two backends as interchangeable.

---

SDK or LiteLM proxy? <!--anki:7531606c2c72556e5870-->
?
- **SDK**: library in code (`litellm.completion(...)`), ideal for a single service
- **Proxy**: **centralized** server for the entire organization, with shared keys, budgets and observability

The SDK avoids an additional network service but disperses the configuration if several applications use it separately. The proxy facilitates common policies, at the cost of a component to host and supervise. In both cases, the provider's permissions and data processing rules must match usage.

---

How do I configure multiple deployments behind an alias of the LiteLLM proxy? <!--anki:75244e56214c4d524272-->
?
```yaml
model_list:
  - model_name: chat-default
    litellm_params:
      model: hosted_vllm/meta-llama/Llama-3.1-8B-Instruct
      api_base: http://vllm.inference.svc:8000/v1
  - model_name: chat-default
    litellm_params:
      model: anthropic/claude-sonnet-4-5
```
Two deployments under the same name: the proxy **spreads the load** between them.

`model_name` is the alias requested by the client; each entry is a candidate deployment. Add identifiers via secrets and choose the routing policy. Here the models differ: the distribution can change the quality of the responses; for simple replication, use functionally equivalent backends and test the required capabilities.

---

What are LiteLM's virtual keys? <!--anki:685b522c2437213a3750-->
?
The **Key API Issued by Proxy** (by team, project or user): the real keys of the suppliers remain **Secrets**, Every virtual key has its **authorized models, budget and limits**.

The application uses its virtual key and the proxy calls the provider with the appropriate secrecy. This makes it easier to revoke and allocate expenses without distributing master keys. Nevertheless, protect the virtual key: it allows billable calls. Check the actual permissions, rotation and availability of configuration storage.

---

How does LiteLLM control costs? <!--anki:462c433f457b28282c46-->
?
By the **monitoring of expenditure** by key, team or user, of the **Budgets** (a ceiling over a period of time) and **rate limits** in requests and tokens per minute (RPM/TPM).

Budgets limit spending over a period of time, while RPM/TPM limits control the pace. Competing queries and deferred accounting can lead to overrun: test the guarantees of the chosen configuration. Provide alerts, margins and conduct in case of a quota reached, without any delays that would aggravate the saturation.

---

How does LiteLLM improve reliability? <!--anki:6369583735646953616f-->
?
- **Retrievances** on transient errors
- **Fallbacks** to another model or supplier if the first one fails
- **Load balancing** between deployments, with cooldown of deployments in error

Limit the number of attempts and the total time to avoid a retrieving storm. A fallback must meet the same data, capacity and quality constraints as the initial model. After the start of a streaming, silently replace the response is tricky: define the client-side recovery behavior.

---

How to link LiteLLM to observability? <!--anki:4e6e34374d5732535658-->
?
By **callbacks**: each call is sent to [[91-langfuse-observability|Langfuse]] (or OpenTelemetry, Prometheus) with prompt, response, tokens, cost and latency — without instrumenting each application.

The gateway sees model calls, but not necessarily all business steps or external tools; propagate a trace identifier and instrument these steps in the application. Filter sensitive data before export and set retention and access. A complete trace must explain the result without unnecessarily collecting secrets.

---

Where is LiteLLM in the stack? <!--anki:65484f7c36453a766272-->
?
```text
Client → Ingress (TLS) → LiteLLM (auth, quotas, routing) → vLLM / API cloud
```
The[[83-gateway-ingress|Ingress]] manages the network; LiteLM **Logical to the LLM**.

The client receives a common interface while the gateway chooses the backend and applies the cost policies. Each hop adds a possibility of error, delay, or stream buffering. Align timeouts, propagate request identifiers, and verify authentication at each exposed border.

Compare the same direct call to the backend and then via the full channel. If streaming arrives in bulk only via the Ingress, changing the model will not correct this buffering.

---

Which type of LLM gateway to choose: self-hosted, managed cloud service, or SaaS aggregator? <!--anki:3236613063623236323539633436323039303964303466393931623061646136-->
?
- **Self-hosting** (LiteLLM, Portkey, Kong AI Gateway, Envoy AI Gateway, agentgateway which also manages MCP and A2A): when the **data should not come out**, or to keep control over routing and budgets
- **Cloud managed service** (AWS, Azure, Google): when everything is already **in the same cloud** and we don’t want to exploit anything
- **SaaS aggregator** (OpenRouter): to access **many providers** without infrastructure or separate contracts

Common criteria: covered providers, budgets and virtual keys, observability, added latency.

---

What happens when a virtual key LiteLLM reaches its budget? <!--anki:3363626463666234653138353463303961396535356364323734336663613965-->
?
The proxy **refuses** the following requests with an explicit error, until the end of the period (`budget_duration`) or a ceiling raise.

For the application, it is a **breakdown**: you have to manage this error (clear message, degraded mode), and **alert before** the ceiling, for example to 80% ([[122-finops-llm|FinOps]]).

Do not try again in a loop a request refused for budget: without change of ceiling or period, it will remain refused. Test the behavior under concurrency; a logical ceiling does not promise an invoice exactly equal to the cent.

---

Why does the accounting of a LiteLM gateway need to be reconciled with supplier billing? <!--anki:6639383364663265646234383438656239373038373831616361663038656233-->
?
The **gateway** observes its calls, but delays, interrupted responses, tools, or counting differences can create a discrepancy with the invoice. The reported customer cost is not always the final invoice cost.

Correlate call identifiers, effective model, returned usage, and versioned rate. Include failed attempts to bill and distinguish between estimate and reconciled amount. Test an interrupted flow before its end-of-use event. A useful budget allocation retains these uncertainties instead of turning missing data into zero cost.

---

Why is a fallback after the start of a LLM stream tricky? <!--anki:6261316164313439616262373435383739396232623330343864613565336662-->
?
The client has already received **a prefix produced by the first model**. The second can generate a different response; concatenate the two creates an inconsistent result.

Set an explicit recovery or failure protocol, possibly restarting a new identified message. Test the failure after multiple fragments. The technical ability to recall a vendor does not guarantee a transparent recovery at the product level.

---

Why can a verified spending limit only be exceeded after each response? <!--anki:3835323334633563353335353439613139623864393236363935343336333236-->
?
Several competing requests can be accepted with **the same balance remaining**, and then each consume this budget. Post-accounting comes too late for a strict limit.

Reserve an estimate before admission, limit generation and then reconcile with actual use. Set the uncertainty margin and the processing of calls still in flight. Check the exact guarantees of the deployed proxy; an expense table does not necessarily constitute a budget lock.

---

## Scenarios

Scenario: Five teams call API directly from three suppliers, with keys shared by copy and paste. The monthly bill is not attributable to anyone. What do you start from? <!--anki:6a6e56307e5b2b4c726f-->
?
1. **Put a gateway in front**: all applications pass through the proxy, in the format of the API OpenAI
2. **Virtual keys** by team and by project: the real keys of the suppliers become secret again
3. **Budgets and spleen limits** per key, with pass alerts ([[122-finops-llm|FinOps]])
4. **Observability callbacks**: centralized traces, costs, and latencies without instrumenting each application ([[91-langfuse-observability|Langfuse]])
5. **Migrate gradually**: start with a volunteer team, then close direct access

**Trap**: Make the gateway a single point of failure without replicas or supervision.

---

Scenario: your primary provider is experiencing a 40 minutes outage in the middle of the day. How should your architecture have reacted? <!--anki:67297e4a71396d5d5e4f-->
?
1. **Fallback configured** to another provider or a self-hosted model for critical routes
2. **Retries** with backoff on transient errors, and **cooldown** on error deployment
3. **Acceptable degradation**: model less good but available, or explicit wait response ([[142-llm-reliability-resilience|Reliability]])
4. **Check compatibility**: the backup model must have been tested on the same evals
5. **Measure**: error rate and toggles, to know later what happened

**Trap**: declare a fallback that has never been tested, which fails when it is needed.

---

## Sources

- [LiteLLM — proxy and gateway](https://docs.litellm.ai/docs/simple_proxy)

## Connections
- [[83-gateway-ingress|Ingress & API gateway]] — network input in front of LiteLLM
- [[82-routing-llm|Routing LLM]] — choose the right model by query
- [[91-langfuse-observability|Langfuse]] — traces sent by callbacks
- [[64-inference-metrics-slo|Metrics & SLO]] — rate limits and timeouts
- [[11-llm-inference-servers|Inference Servers]] — self-hosted backends
- [[122-finops-llm|FinOps LLM]] — budgets and cost allocation
- [[93-monitoring-inference|Monitoring of inference]] — usage metrics collected at the gateway
- [[142-llm-reliability-resilience|Reliability & resilience]] — retries, fallbacks, circuit breakers
- [[84-streaming-application-integration|Streaming & integration]] — relay and cancel streams
- [[101-llm-security-guardrails|LLM Security]] — injection, exfiltration and guardrails
- [[123-aggressive-caching|Caching]] — prompt caching and response caches
- [[141-system-design-llm|System Design LLM]] — design method
- [[33-mcp|MCP]] — the standard protocol between agents and tools
- [[38-agent-platforms|Platforms of agents]] — runtime, sandbox, tool gateway and identity
- [[41-code-nocode-automation|Automation code & no-code]] — workflows and no-code tools
- [[46-crewai-crews|CrewAI — Crews]] — Role-Based Agent Teams
- [[85-agentic-protocols-map|Map of protocols]] — which protocol to which agent boundary
- [[00-moc-ai-engineering|MOC AI Engineering]]
