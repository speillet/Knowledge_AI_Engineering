# LLM application system design — Flashcards
Tags: #flashcards #ai-engineering #system-design #architecture #llm
<!-- summary: approach, framing, complexity scale, quality-latency-cost triangle, load estimation, components, real or perceived latency, synchronous or asynchronous, multi-tenant, failure modes, arbitration presentation, cost of business errors, amplification of calls, degraded mode. -->


Where does the system design process for a LLM application begin? <!--anki:62787568774b543e5144-->
?
1. **Clarify** the need: users, task, volume, constraints (latency, cost, privacy, language).
2. **Set Success**: Product metrics and [[94-evals-methodology|evals]].
3. Offer **the simplest architecture** that can work.

For example, to distinguish a re-read draft from an automatic processing involving a decision. Give quantified assumptions about traffic, length of requests and acceptable cost, and then a baseline to test the value. The choice of framework or vector base comes after the requirements, not before they are clarified.

---

Once the architecture is sketched, what remains to be done in system design? <!--anki:504079722d576245485a-->
?
4. **Detail** critical components (retrieval, model, tools, guardrails).
5. Process **reliability, security, cost, observability**.
6. Explain the **arbitrations** and how the **system is evolving**.

For each critical component, specify input, output, responsible, and degraded behavior. Justify the choices by the established requirements, and then indicate what actions would trigger an evolution rather than presenting a definitive architecture.

---

What framing questions to ask about product use and constraints? <!--anki:7671295a6b3d2c7d6278-->
?
- **Who** uses, **how much** (queries/day, peaks) and **where** (languages, regions)?
- What **tolerance to error**? (suggestion reread by a human ≠ automatic action)
- What **latency** is acceptable? Interactive, asynchronous, batch?

These answers determine the product contract: a suggestion can be corrected, while an incorrect payment has an immediate cost. Quantify peaks and delays per segment, not just on average. Document unknowns and propose a pilot measure to avoid sizing the architecture on hidden assumptions.

---

What scoping questions to ask about data and the company framework? <!--anki:6e255a234929572f2443-->
?
- What **data**: volume, freshness, sensitivity, access rights?
- **Budget** per request or per user?
- **Contracts**: on-prem, sovereignty, [[155-ai-act|Regulation]]?

Also map who owns the sources, how they change, and who can access them. A residency requirement may exclude some providers; a source updated every hour imposes a synchronization mechanism. Link each constraint to an architectural decision and verifiable control.

---

What are the first bars of the complexity scale of a LLM system? <!--anki:6f3a62406e2a4b7b716b-->
?
We climb a notch **only if the previous one is not enough**, and **we prove it by an eval**:
1. **A very prompt LLM** call.
2. **Workflow**: deterministic call chain, routing.
3. **RAG** or reading tools.

Example: to categorize tickets into twelve categories, a prompt call with a few examples may be enough. We only go to the workflow if the eval shows confusion that a routing or a second step corrects. Each bar adds a component to test, monitor and secure: the operating cost counts as much as the cost of calls.

---

What are the last bars of the complexity scale, and at what price? <!--anki:64486d53634b69783433-->
?
A **agent loop** helps when steps are not known in advance; the **multi-agent** can help truly independent subtasks. They add coordination, status, and calls to diagnose.

The **fine-tuning is another axis**, suitable for repetitive behavior insufficiently obtained by the prompt: it is not necessarily the step after the multi-agent. It costs to train and maintain, but can reduce prompt and latency in service. Add complexity only to solve a measured limit of the baseline ([[31-agent-fundamentals|agents]]).

---

What is the central arbitration triangle of a LLM system? <!--anki:772157213d79352c393c-->
?
**Quality, latency and cost** must be measured together on the target task. A larger model or longer reasoning can improve some cases, but can also add delay, cost or errors without useful gain.

Compare complete configurations with explicit constraints, with their results per segment. [[82-routing-llm|Routage]], [[123-aggressive-caching|caching]] and [[53-synthetic-data-distillation|distillation]] move trade-offs; they themselves have costs and risks. Streaming sometimes reduces perceived waiting without reducing total time.

---

How to make a back-of-the-envelope estimate? <!--anki:4f77243c41575850796f-->
?
Example: 100,000 Users × 10 requests/day = **1 M requests/day ≈ 12 req/s** on average, **Peak ×3 TB ×5**. With 3,000 tokens Entry and 500 Output by request: **3.5 G tokens/day**. We deduce the **Cost API** Price × tokens) or the **Number of GPU** (Debit in tokens/s by GPU), and compare ([[121-inference-costs|break-even API vs self-host]]).

---

What components does a query pass through in a LLM production architecture? <!--anki:74584e6f3d7123525955-->
?
- **Front / API** with auth and rate limiting ([[83-gateway-ingress|gateway]]).
- **Applicative orchestrator** (workflow or agent).
- **Guardrails** in and out.
- **Gateway LLM**: routing, fallbacks, budgets ([[81-litellm-api-layer|LiteLLM]]), then the **models** (API or self-hosted).

Each component adds latency and a point of failure: an input guardrail that calls a model delays the first token of its entire duration. Spread a **query identifier** across all layers, all the way to the models and tools, to link logs, traces and costs. Also decide, component by component, if a failure bypasses it or blocks the request.

---

Which support bricks complete a LLM production architecture? <!--anki:74727b49455b7442742c-->
?
- **Retrieval**: vector and lexical index, ranking.
- **Caches** at all levels and **message file** for asynchronous.
- **Observability** (tracks, evals online) and **feedback loop**.

These bricks meet specific needs and are not all mandatory. A stand-alone extraction does not necessarily require a retrieval; a response dependent on private data requires properly isolated caches. Identify the neck or the risk treated by each component before adding it to the baseline.

---

How to reduce the perceived latency of a LLM application, interface-side? <!--anki:697a3f7d53485e56495f-->
?
- **Streaming** of the tokens: the TTFT counts more than the total duration.
- **Background work** with notification for long tasks, rather than a blocking wait.
- Display the **progression** of an agent rather than a spinner ([[144-ai-ux-human-in-the-loop|UX]]).

Other levers: first display what does not require LLM, such as the status of a command, then the explanation generated; pre-calculate what is predictable, such as the summary of a document when it opens. Measure the effect on usage, such as abandonment before the first read, and not just on server latency.

---

How to reduce the actual latency of a LLM application, on the calculation side? <!--anki:6e49254259305f552c24-->
?
- **Small models** for intermediate steps (routing, rewriting).
- **Prompt caching** of long prefixes ([[123-aggressive-caching|caching]]).
- Answers **pre-calculated** for frequently asked questions.

Measure the critical path first: wait, retrieve, tools, prefill and decode. Small models only help if their quality is sufficient and their call does not create more escalations. Parallel independent steps and limit the output can also reduce the duration; streaming especially improves the perception of waiting time.

---

When to choose synchronous or asynchronous LLM processing? <!--anki:4c506377553d6f47263d-->
?
- **Synchrone** (streaming): human interaction, response in seconds.
- **Asynchronous** (file + workers + notification): long tasks (agents, reports, document processing), load peaks to **smooth**, **batch API** cheaper.

An agent task of several minutes **must not** hold an open HTTP request ([[142-llm-reliability-resilience|Reliability]]).

Separate submission and follow-up: return a durable identifier, then expose status and result. Streaming can show progress without becoming the only job storage; a reconnection must not restart the task.

---

How to isolate customers from a LLM multi-tenant application? <!--anki:45785b5e5036705d493b-->
?
- **Isolation of data** : holding filter **Mandatory** in the retrieval (ideally imposed server side, not by the prompt, and separate indexes.
- **Quotas and budgets** per tenant.
- **Keys and configurations** (model, prompt) per holder.
- **No shared cache** between supporters for private data ([[123-aggressive-caching|Security of the cache]]).

Deduct the holder from the authenticated identity, not from a field offered by the model. Also test downloads, quotes, traces and recovery after revocation: filtering the search does not automatically protect all paths.

---

What failure modes should be anticipated from the design stage? <!--anki:656575326e2975292b3d-->
?
Supplier's failure or **rate limit**, **degraded latency**, **invalid exit** (format), **hallucination**, **prompt injection**, **agent loop**, **cost drift**, **silent model update**, **empty retrieval**. For each: **detection** + **response** (retry, fallback, abstention, human escalation).

Method: a table **mode → signal → response → test**. Example: provider rate limit → rate of 429 and latency p95 → retry bounded then backup model → preproduction exercise. Prioritize according to probability and impact. A mode without detection signal remains an uncovered risk, even if the parade exists.

---

How to present arbitrations in a senior way? <!--anki:4e5d6f754e26452d754d-->
?
Present **options, assumptions, measures, cost of risk and reconsideration condition**, not just name a technology.

Hypothetical example: "B costs 20% more, but meets the required p95 on long documents; A fails on this segment. We retain B and will re-examine A after context reduction, without quality drop."

Specify load, evaluation set, and uncertainty behind the numbers; distinguish measured result from estimate. Include exploitation, vendor lock-in, and migration. A good decision also explains why a simpler option has been ruled out and what signal will trigger a change, with accountability and deadline.

---

Do not confuse: Real latency and perceived latency? <!--anki:6663657646534e482321-->
?
- **Actual latency**: calculation time up to full response, reduced serving side (smaller model, cache, less than tokens output)
- **Perceived latency**: the time the user **waits without seeing anything**, reduced interface side (**streaming**, first token fast, steps displayed, background work)

An agent of 40 seconds that shows its steps may appear faster than a response of 8 seconds on white screen. The **TTFT** drives perception, the total duration drives cost ([[64-inference-metrics-slo|Metric]]).

---

Why quantify the cost of a business error before choosing the AI architecture? <!--anki:6164346231356564623330633437313938373461383063356139633636356164-->
?
The **cost of the error** determines the useful controls: title suggestion and bank transfer do not require the same level of proof, supervision or recovery.

Describe possible errors, estimated frequency, reversibility and people affected. Then compare rules, model, verification and human review on their total cost and time frame. Start with a limited volume when uncertainty is high. A more complex architecture can reduce some errors while creating new failure modes; the arbitration must focus on the complete business result.

---

Calculation: a product receives 12 tasks/s; each task does on average 4 calls LLM, and 10% of these calls require exactly one pick-up. What average call throughput would you expect? <!--anki:3837663937666661313835333434636261353265383138656134333066633363-->
?
The nominal bitrate is **12 × 4 = 48 calls/s**. Repeats add **4.8 calls/s**, or **52.8 calls/s**.

This average calculation ignores bursts and the correlation of failures. Also size tokens, concurrency and tool dependencies. A product QPS does not translate directly into supplier QPS, especially for an agentic loop of variable length.

---

How do I set a useful gradient mode for a LLM application? <!--anki:6538373361373864396336383438646362623465663035623561336131623033-->
?
Preserve **an explicitly bounded value**: search for documents without synthesis, draft without publication or deferred processing. Clearly indicate what has been verified and what remains pending.

Test the mode with the same constraints of rights and confidentiality. A fallback that invents a response to maintain the availability rate degrades the product contract. Measure useful success and delays in this mode separately.

---

## Scenarios

Scenario: we ask you to design an internal assistant for 5,000 employees, on the company documentation. How do you start the first ten minutes? <!--anki:6a643d4d5663212f3323-->
?
1. **Frame before drawing**: volume and peaks, languages, error tolerance, expected latency, document sensitivity, budget
2. **Set success**: what is measured, with what evals and metrics is produced
3. **Posses the simplest architecture**: a LLM call plus a RAG, without an agent
4. **Encrypt**: requests per second, tokens per request, cost per month, then compare API and self-host ([[121-inference-costs|costs]])
5. **Announce critical points**: rights of access to the retrieval, freshness of the index, observability

**Strap**: Start with an eight-component diagram before asking a single question.

---

Scenario: your architecture works at 12 requests per second on average, but falls at peak times. What design choices do you review? <!--anki:4831633d2e7e784a5462-->
?
1. **The peak, not the average**: size on a factor 3 to 5 above the average
2. **Synchron or asynchronous**: long processing queues with notification, instead of holding an open request
3. **Read**: queue, quotas per client, and deferred processing for what is not interactive
4. **Reduce unit cost**: caching, routing to a smaller model on simple cases
5. **Check weak link**: supplier quota, vector base, or inferiority server competition

**Trap**: Add replicas when the limit comes from the model provider quota.

---

Scenario: your technical director asks you why you chose the RAG rather than a fine-tuning. How do you present the arbitration in a senior way? <!--anki:70653f2c445d69663a59-->
?
1. **Say what you earn**: up-to-date knowledge, verifiable quotes, per-document access rights
2. **Say what you lose**: latency of the retrieval, ingestion complexity, quality dependent on the chunking
3. **Say what would change your mind**: if the problem becomes the **style** of the answers or the length of the prompts, a light fine-tuning is justified
4. **Encrypt**: cost per request, latency p95, quality measured on evals
5. **Predict the evolution**: the two approaches combine, the RAG for knowledge, the fine-tuning for behavior

**Pip**: justify a choice of architecture by a technical preference rather than by measures and constraints.

---

## Connections
- [[142-llm-reliability-resilience|Reliability & resilience]] — keep the system in production
- [[145-system-design-cases|Case of system design]] — examples concrets
- [[146-model-selection|Choice of model]] — central component
- [[31-agent-fundamentals|Agents]] — workflow or agent
- [[21-rag-fundamentals|RAG]] — knowledge component
- [[81-litellm-api-layer|LiteLLM]] and [[82-routing-llm|routing]] — the gateway
- [[121-inference-costs|Inference costs]] — Encrypt Design
- [[84-streaming-application-integration|Streaming & integration]] — synchronous, streaming or asynchronous
- [[101-llm-security-guardrails|LLM Security]] — injection, exfiltration and guardrails
- [[147-ai-technical-leadership|Technical Leadership]] — team standards and decisions
- [[148-llm-batch-pipelines|Pipelines batch]] — process millions of items at a lower cost
- [[22-advanced-rag|RAG — Advanced]] — hybrid search, reranking and filters
- [[140-011-agentic-application-architecture|— Architecture & Life Cycle]] — assemble components
- [[00-moc-ai-engineering|MOC AI Engineering]]
