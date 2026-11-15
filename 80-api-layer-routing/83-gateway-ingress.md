# Ingress & API gateway — Flashcards
Tags: #flashcards #ai-engineering #kubernetes #ingress #networking
Verified on: 17 October 2026 — removal of ingress-nginx from Kubernetes project announcements.
<!-- summary: Ingress controller, ingress-nginx removal, Ingress, API gateway and gateway LLM, TLS, Gateway API, rate limiting, SSE streaming, controller migration, total timeout and idle timeout, client disconnect, body size. -->


What is an Ingress in Kubernetes? <!--anki:49586e334f397c2c6740-->
?
The **HTTP(S) gateway of the cluster**: it routes external traffic to the Services according to the host and path.

An Ingress object describes rules; an **Ingress controller** must implement them in order for traffic to be effectively routed. The Services then direct to eligible Pods. The Ingress does not automatically decide on the correct LLM model and does not, on its own, constitute an authentication or budget policy.

---

Does an Ingress work alone? <!--anki:45497c54723d663e553e-->
?
**No.** The Ingress declares rules; a compatible **controller** must observe them and configure the effective network path.

Example: `kubectl apply` succeeds but the Ingress targets a class that no controller handles. The object exists, without a working route. Check `ingressClassName`, controller events and logs before modifying the LLM server.

Thcontinuouslye the string: published address, DNS, certificate, Service, and ready endpoints. The status of the object is not an end-to-end test. Choose a maintained controller and check its functionality; not all annotations are portable between implementations.

---

What does an Ingress typically do? <!--anki:46493d40694175445866-->
?
- Routing **per host** (`api.example.com`) and **per path** (`/v1/...`)
- **TLS Termination** (HTTPS)

For example, send `api.example.com/v1` to the Gateway Service while presenting an HTTPS certificate. Some additional functions depend on the controller and its configuration. Check body size, timeouts and streaming over the entire chain; a correct routing rule does not guarantee that a long response arrives intact.

---

What is the Gateway API? <!--anki:4c73712d31366d6b342d-->
?
The **successor of the Ingress** in Kubernetes, with separate roles:
```text
GatewayClass → implementation (chosen by the platform)
Gateway → entry point: ports, TLS (infra team)
HTTPRoute → Routing to Services (application team)
```
Contributions: **team delegation** without proprietary annotations, traffic splitting **by weight** (canary), and support for other protocols (gRPC, TCP). This is the recommended way by Kubernetes to replace ingress-nginx. Gateway projects for agents rely on it ([[38-agent-platforms|agentgateway]]).

The resources describe the intent; a compatible controller must apply it. Verifying the route acceptance and programming conditions: A YAML accepted by the API does not guarantee that a backend is reachable.

---

Do not confuse: Ingress, API gateway and gateway LLM? <!--anki:68587e30382d4f264f2a-->
?
```text
Ingress → HTTP(S) exposure, host, path, TLS
API gateway   → API policies: auth, quotas, transformations
Gateway LLM → models, tokens, budgets, fallbacks, traces LLM
```
These are **Responsibilities**, not necessarily three stacked products. A general-purpose gateway can integrate functions LLM or an extension of the tokens ; a Gateway LLM You can also finish TLS.

Choose the assembly that covers the needs without duplicating the controls, and designate who applies each quota or timeout ([[81-litellm-api-layer|LiteLLM]]).

Example: If the Ingress cuts to 30 s an agent allowed to work for two minutes, the client fails despite a healthy backend. Align delays and spread cancellation.

---

Why rate-limit a LLM endpoint? <!--anki:6b603e5625303c4c4a78-->
?
Because every request consumes **GPU Costly** : without limit, a customer can saturate the service and blow up the costs.

Queries do not all have the same cost: a long generation can monopolize much more resources than a classification. Combine query limits, tokens and concurrency, by identity and globally. Return an explicit error with a suitable retry policy and keep a line bounded to protect the latency of other customers.

---

What does the network string of a LLM stack look like on Kubernetes? <!--anki:482648216e5375467761-->
?
```text
Client → Ingress (TLS, routage) → gateway/LiteLLM (auth, quotas) → Service vLLM → Pods GPU
```

The Ingress exposes the domain; the gateway authenticates and chooses the backend; the Service provides a stable destination to the ready Pods; the Pods run the model. Some components can be merged. Diagnose each hop: DNS resolution, TLS, authorization, routing, readiness, and computation, keeping a common identifier in the logs.

Measure the durations per hop and verify the spread of the cancellation. A closed client connection can let the backend calculate if the break is not transmitted; the GPU cost thcontinuouslyes with no result consumed.

---

Why does streaming (SSE) require special settings? <!--anki:715e606d2e4e6d786140-->
?
The LLM responses are **long and streamed**: it takes extended **timeouts** and disable **buffering**, otherwise the proxy keeps the response and the user waits for all the text at once.
```yaml
annotations:                       # ingress-nginx
  nginx.ingress.kubernetes.io/proxy-buffering: "off"
  nginx.ingress.kubernetes.io/proxy-read-timeout: "600"
  nginx.ingress.kubernetes.io/proxy-send-timeout: "600"
```
Think of them too **Load Balancers Cloud** upstream, with their own inactivity period, and to the **Compression**, Disable on these roads. These annotations are specific to ingress-nginx, which has not been maintained since March 2026 : with another controller or the Gateway API, Look for equivalent settings.

---

What are the configuration cues for a LLM endpoint? <!--anki:6a586e4237583a6c5656-->
?
Set the settings from the **SLO and the query profile**, no universal values:
```text
Total time from end to end budget on the client and server side
Inactivity timeout suitable for pauses between stream events
buffering avoid accumulating tokens before sending
request size capped according to the formats actually accepted
request quotas, tokens and concurrency
```
Differentiate between connection time, read time and total duration. Test a long stream, a period without sending and a customer disconnection. A very high timeout without cancellation can let GPU run unnecessarily ([[142-llm-reliability-resilience|Reliability]]).

Record the chosen values with a validation scenario: prompt long, pause reasoning and slow client. Align the delays of all proxies; the shortest limit can interrupt a flow yet authorized elsewhere.

---

Why should the timeouts of a gateway distinguish between the silence of the flow and the total duration of the request? <!--anki:6562323839386164636138663463356638316234363465383235343735313262-->
?
A **timeout of inactivity** limits the time without data; a **timeout total** limits the duration of the operation. A stream can remain active for ten minutes and exceed a product budget of thirty seconds.

Align these timelines between client, proxy, gateway, and backend, then propagate a global deadline. Test a model that reasons long before the first byte and a stream that regularly sends small data. Check buffering and undo propagation. A network heartbeat does not prove that useful content is progressing.

---

Why limit the size of a request before it arrives at the LLM server? <!--anki:6266363131316433666338313430666239613339353965313334306638643465-->
?
Parsing, decompression and tokenization can consume **memory and CPU before any GPU** admission. A limit in tokens applied late does not protect these steps.

Bound bytes, attachments, and sizes after decompression, and then check the budget for tokens. Send an understandable error. Limits must be consistent between gateway and application to avoid opaque failures at different sizes.

---

Why check the spread of a client disconnection through the gateway? <!--anki:3235313961376639343465383462626161333265613764376362343366366532-->
?
The proxy can continue the query upstream even after the client leaves, leaving **an expensive calculation without a consumer**.

Trace a common identifier and observe the actual shutdown in the inference server. Test network disconnection, timeout proxy and explicit cancellation. Depending on the contract, some tasks must continue in the background; they must then be exposed as tracked asynchronous tasks, rather than silently losing their result.

---

## Scenarios

Scenario: your assistant is exposed by ingress-nginx, which is no longer maintained since March 2026, with annotations that disable buffering and lengthen the streaming times. How do you prepare the migration? <!--anki:6566363336623132396438643438623062396438343933313137363037623561-->
?
1. **Inventory** Ingress objects and their annotations: timeouts, buffering, TLS, query size, rewrites
2. **Choosing the target**: an implementation of the Gateway API or another controller maintained, depending on the functions actually used ([[04-kubernetes-kubelet-cri|Kubernetes]])
3. **Translate each setting**: no substitute accepts these annotations as is, the equivalents are configured differently
4. **Test end-to-end streaming**: long response, pause without broadcast, client disconnection ([[84-streaming-application-integration|streaming]])
5. **Gradually switch**: Two entry points in parallel, traffic moved in stages, back ready

**Trap**: copy the roads without their annotations, and find in production buffered or cut responses.

---

Scenario: a single customer saturates your inference service by running thousands of queries in parallel. Where do you set the limits? <!--anki:42676956437a5a6f296b-->
?
1. **At the entrance**: rate limiting by key or IP on the Ingress or the API gateway
2. **In the LLM gateway**: limits in requests and in **tokens** per minute, plus a budget ([[81-litellm-api-layer|LiteLLM]])
3. **In the inference server**: maximum concurrency, to preserve the SLO from other users
4. **Response cleanly**: 429 code with recovery header, rather than a timeout
5. **Monitoring**: rate of 429 per customer, to distinguish an abuse from a too low limit ([[93-monitoring-inference|monitoring]])

**Trap**: Limit only the number of requests, while a single request to 100,000 tokens costs much more.

---

## Sources

- [Kubernetes — removal from Ingress NGINX](https://kubernetes.io/blog/2025/11/11/ingress-nginx-retirement/)
- [Kubernetes — Gateway API](https://gateway-api.sigs.k8s.io/)

## Connections
- [[04-kubernetes-kubelet-cri|Kubernetes]] — Base
- [[64-inference-metrics-slo|Metrics & SLO]] — rate limiting and timeouts driven by the SLO
- [[12-kubernetes-gpu-inference|Kubernetes GPU]] — the Pods behind the Ingress
- [[81-litellm-api-layer|LiteLLM]] — the application gateway behind the Ingress
- [[84-streaming-application-integration|Streaming & integration]] — buffers and timeouts on SSE streams
- [[11-llm-inference-servers|Inference Servers]] — vLLM, SGLang, TensorRT-LLM and their setting
- [[112-model-cicd|CI/CD models]] — eval gates, canary and rollback
- [[144-ai-ux-human-in-the-loop|UX & human-in-the-loop]] — what the user sees and validates
- [[00-moc-ai-engineering|MOC AI Engineering]]
