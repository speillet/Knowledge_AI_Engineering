# Streaming & application integration — Flashcards
Tags: #flashcards #ai-engineering #api #streaming #agents #llm
Verified on: 30 September 2026 — This factsheet lists products, versions or regulatory texts that are evolving quickly.
<!-- summary: streaming interest, SSE or WebSocket, proxy buffers, server-side cancellation, streaming JSON, agent events (AG-UI), long asynchronous tasks, resuming a stream, idempotency key, calculation of open connections, deduplication to SSE reconnection, backpressure, end of stream. -->


Why stream the answers of a LLM? <!--anki:6536416a5043402c2f28-->
?
Streaming makes it possible to display the **useful content gradually**, while the generation continues. For example, 500 tokens produced at 50 tokens/s represent about 10 seconds of decoding, to which is added the expectation of the first content.

The initial delay depends on the context, the model, the queue and the network; it is not always a few hundred milliseconds. At the same generation and pricing, changing the transport does not automatically reduce the cost. However, an effective cancellation or a change in user behavior can change the work consumed.

---

Do not confuse: SSE and WebSocket? <!--anki:4c7763604f434577474d-->
?
**SSE** transports → client server events over HTTP (`text/event-stream`); **WebSocket** maintains a two-way channel, useful especially for interactive [[163-real-time-voice|voice]].

Example: a chat sends a request over HTTP and then receives the tokens over SSE; a voice call continuously exchanges audio and events in both directions.

The automatic reconnection concerns in particular the browser client `EventSource`, not any SSE reading via `fetch`. **Reconnection is not taken back guaranteed**: it is necessary identifiers and policy of replay on the server side to avoid losses or duplicates. Both transports require management of delays, disconnection and proxies; SSE does not neutralize their buffering.

---

Why does an SSE streaming sometimes come from a single block? <!--anki:4e6e354453327c605246-->
?
An intermediary **buffers**: reverse proxy, compression, CDN or framework. The client receives everything at the end.
```nginx
location /api/chat {
    proxy_pass http://backend;
    proxy_buffering off;          # or X-Accel-Buffering header: no
    proxy_read_timeout 300s;      # Long answers exceed 60 s
    gzip off;
}
```
Also check the **timeouts of inactivity** of load balancers: sending a regular SSE comment (`: ping`) avoids them ([[83-gateway-ingress|gateway]]).

Diagnosis: `curl -N` on the direct backend, then through each intermediary; the first layer where the events arrive grouped is the culprit. Server side, send `Content-Type: text/event-stream` and `Cache-Control: no-cache`: some proxies disable their buffer only by recognizing this type.

---

Why manage server-side cancellation? <!--anki:4c74432f2e24316a6b77-->
?
When the user closes the tab or clicks "Stop", the server must **stop the call to the model**: otherwise continuous generation, **consumes tokens billed** and occupies the KV cache of the inference server for nothing.

In practice: detect the disconnection of the client, then cancel the current request (cancel the asynchronous task, close the stream to the provider) ([[121-inference-costs|costs]]).

Closing the stream does not guarantee that the provider has stopped the calculation. Measuring the tokens products after abandonment and using its cancellation mechanism when it exists. An already executed business action requires possible compensation, not just stopping the stream.

---

How to stream a structured output (JSON)? <!--anki:4f736b3c676762595649-->
?
A partial JSON is not valid until it is finished. Two approaches:
- **Partial JSON parser** on the client side, which displays the fields as they complement each other
- **Stream only free text**, and send structured fields in a final event

The API of structured outputs stream fragments, validated against the scheme **at the end** only ([[63-guided-generation|guided generation]]).

---

How to stream an agent response that calls tools? <!--anki:732a6b6543373a467370-->
?
The stream contains several **types of events**, not just text: start and end of step, tool call with its arguments, result, response text, error, end. The client thus displays **what the agent does** ("search in the database..."), which makes the wait acceptable.

This is the object of protocols like **AG-UI**, which standardizes these events between an agent and its interface ([[144-ai-ux-human-in-the-loop|Make the work visible]]).

---

How to expose an agent task that lasts several minutes? <!--anki:6a352641682c7b69602d-->
?
Not in synchronous HTTP request: connections are cut and we lose everything. We pass in **asynchronous**:
1. `POST /tasks` immediately returns an **ID**
2. The agent runs in a **worker**, with its state persisted
3. The client follows the progress by **SSE**, by periodic query, or receives a **webhook** at the end

If the worker restarts, the task resumes thanks to the **Durable Execution** ([[115-agent-platforms-governance|Durable Execution]]).

---

How to resume a cut stream without losing everything? <!--anki:686c3f7c614c49506d52-->
?
- Numbering events: SSE returns the header **`Last-Event-ID`** to reconnection
- **Keep the server-side stream** (Redis, base) for a few minutes, regardless of connection
- On return, return the **missed** events, thcontinuouslye live

Condition: that the generation **continue** on the server side even without a connected client, which opposes automatic cancellation. We choose according to use: chat short (cancel) or long task (continue).

---

What is an Idempotence key and why put it on a API LLM? <!--anki:413e3131404d6351465b-->
?
A unique identifier provided by the client (`Idempotency-Key`): if the same request arrives twice (double click, network retry), the server returns the **same result** instead of retrying. Without it, a retry restarts the agent, **doubles the cost** and can **repeat an action** (ticket created twice) ([[142-llm-reliability-resilience|retries]]).

The header has no effect without a server implementation. Set client scope, retention time, and request footprint; deny the same key with different arguments. For work still in progress, return its status rather than start a second agent.

---

Calculation: at equilibrium, 50 new SSE streams start per second and last on average 12 s. How many streams are opened on average, then if the arrival rate triples durably? <!--anki:725e21745a3f6a415179-->
?
**Little's Law**: Simultaneous connections = arrivals × duration.
```text
50 req/s × 12 s = 600 open SSE streams on average
pic ×3          ≈ 1,800
```
Each stream holds a connection and often an asynchronous task: it takes a server **asynchronous** (not a thread per request) and check the **connection limits** of the proxy and the provider ([[64-inference-metrics-slo|Competition]]).

These figures are **averages**: Little’s law says nothing about spikes per minute or abnormally long flows.Size on a high percentile of the number of observed flows, with a margin, rather than on 600.

---

Why can an SSE reconnection display the same agent event twice? <!--anki:3664656336333734666238333464613538393835396339663233306464303737-->
?
A **reconnection** can replay events already received, especially if the client did not save its last cursor before the cut.

Give events a stable, orderly identifier according to the contract; the client deduplicates and resumes from its cursor. If the history has expired, recover a reference state rather than reconstructing a result from an incomplete stream. Display events should not directly trigger replayable business effects. Distinguish between resuming transport and resuming agent execution.

---

Why limit the buffer of an SSE stream when the client reads slowly? <!--anki:6431313366653233663238383436366161306265343930306263373735643431-->
?
Without a limit, the producer can accumulate **data faster than the network evacuates**, until it saturates the memory.

Set an explicit backpressure, delay or interrupt policy. For replayable events, a durable log can decouple production and delivery. Do not silently delete fragments of text or arguments: the result would become incomplete while appearing valid.

---

Why distinguish between connection closure and success event in an agent stream? <!--anki:6333613839326437333231653433653761333664336633366535326638666462-->
?
A connection can close after **a failure, a timeout or a success**. Closing alone does not give the business status.

Provide an explicit end event with task and result ID, as well as a status endpoint if the connection is lost. The client should not display "completed" on a simple end of transport. Test a break just before and right after the success record.

---

## Scenarios

Scenario: your assistant stream well locally, but in production the answer appears suddenly after 15 seconds, and some long answers are cut to 60 seconds. What do you check? <!--anki:4651427b395e7d5061-->
?
1. **Tracking**: browser, CDN, load balancer, ingress, application, provider
2. **Search for buffer**: `proxy_buffering`, compression, middleware that reads all the answer ([[83-gateway-ingress|ingress]])
3. **Search for 60 s timeout**: load balancer idle timeout or `proxy_read_timeout`
4. **Fix**: disable the buffer on this route, extend delays, send regular `: ping`
5. **Test** with `curl -N` at each layer to see where the flow is blocking

**Trap**: increase the resources of the backend, while the problem is in the proxy.

---

Scenario: an analysis agent takes 3 to 8 minutes to produce a report. Today the interface waits for the HTTP response, and 20% scans are lost. How do you recognize the integration? <!--anki:76523976517d40646353-->
?
1. **Go asynchronous**: Create task with ID, Idempotence key against duplicate submissions
2. **Run in a worker** with durable execution, to survive reboots ([[115-agent-platforms-governance|Durable Execution]])
3. **Publish progress** in events (steps, sources read), searchable by SSE with recovery via `Last-Event-ID`
4. **Notify end** by webhook or notification, so the user can close the tab
5. **Measure**: completion rate, duration, abandonments

**Strap**: Increase timeouts anywhere up to 10 minutes, and keep a fragile architecture.

---

## Sources

- [MDN — using Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events)
- [AG-UI — protocole d’interaction agent-interface](https://docs.ag-ui.com/introduction)

## Connections
- [[81-litellm-api-layer|LiteLLM]] — the gateway that relays the flow
- [[83-gateway-ingress|Ingress & API gateway]] — buffers and timeouts
- [[64-inference-metrics-slo|Metrics & SLO]] — TTFT and concurrency
- [[144-ai-ux-human-in-the-loop|UX & human-in-the-loop]] — what streaming changes for the user
- [[142-llm-reliability-resilience|Reliability & resilience]] — idempotency and recoveries
- [[115-agent-platforms-governance|Platforms of agents]] — Durable execution of long tasks
- [[163-real-time-voice|Voice & Real Time]] — when bidirectional is required
- [[85-agentic-protocols-map|Map of protocols]] — where AG-UI is
- [[141-system-design-llm|System Design LLM]] — design method
- [[61-kv-cache-attention|KV cache]] — memory that limits concurrency
- [[33-mcp|MCP]] — the standard protocol between agents and tools
- [[149-delivery-idempotency-concurrency|Delivery & Idempotence]] — track an operation after timeout or disconnection
- [[90-011-langfuse-instrumentation-production|Langfuse — Production instrumentation]] — observe the flow consumption
- [[140-011-agentic-application-architecture|— Architecture & Life Cycle]] — public contract and reconnections
- [[00-moc-ai-engineering|MOC AI Engineering]]
