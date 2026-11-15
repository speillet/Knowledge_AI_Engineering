# Langfuse — Instrumentation in production — Flashcards
Tags: #flashcards #ai-engineering #agents #production
Verified on: 9 October 2026 — API cited against official documentation; limits spelled out in maps.
<!-- summary: Complete application traces, observations, distributed correlation, async, tokens and costs, streaming, sampling, masking, export, duplicates and diagnostics, spread of traces between workers, failed export, distributed clocks. -->


Why is it not enough to trace only the LLM gateway to observe an agent? <!--anki:6135383431373137353435663462366261663235326663333433313134666563-->
?
The gateway sees the **model calls that pass through it**. It does not necessarily describe the retrieval, business tools, approval decisions, or queue waiting.

Create an application trace that links these steps and attach LLM calls to it. Example: The gateway shows two successful calls for 3,200 tokens; only the application trace reveals that the command read tool has expired after 4 s, hence the fallback response. The actual coverage must be verified on a run with tool, error, and resume.

---

How to choose the perimeter of a Langfuse trace for a conversation? <!--anki:6236366136393265353463663439346539663939653932633433616439396530-->
?
A trace represents an inspectable **work unit**, such as a conversation turn or an agent run. A session groups the traces related to the path.

The same folder can produce several traces during human pauses and repeats, with a common business identifier. Example: the refund proposal forms a trace, the execution approved the next day another; both carry `dossier_id=D-123` in the same session. Avoid artificially keeping an observation open for several days only to keep a single tree. Distinguish between active execution time, human waiting time and total duration of the folder.

---

Do not confuse: thread_id, run_id, and trace_id in an agentic application? <!--anki:3731393534663439613837393430656538383238656463663035353262613730-->
?
The **thread** carries the continuity of the state, the **run** identifies an execution and the **trace** links its technical observations. Their correspondence depends on the architecture: a thread can contain several runs and traces.

Example: The `D-123` thread contains the 1 run, the proposal, and the 2 run, the recovery after approval, each with its trace. Keep these references in metadata; none constitute an access authorization. The idempotency key remains business, like `D-123:refund`: the recovery has produced a new trace for the same operation.

---

How to structure Langfuse observations of an agent loop? <!--anki:3031316337333931316263323431393238636463386531393366376266386632-->
?
Create a parent for execution, then distinguish between **LLM calls, tools, and search or validation steps**. Each model invocation must remain identifiable with its usage and result. With the Python SDK:
```python
with langfuse.start_as_current_observation(name="support-run", as_type="agent"):
    with langfuse.start_as_current_observation(name="read-order", as_type="tool"): ...
    with langfuse.start_as_current_observation(name="propose-refund", as_type="generation",
                                               model="modele-x"): ...
```
Do not wrap the entire loop in a single generation: this hides the call that has magnified the context or requested an incorrect tool. Use stable names and metadata for variable identifiers, in order to keep filters and ratings comparable.

---

How to propagate a trace between a API and a worker? <!--anki:3766396665323336396562643466333661366663303634383533313331373862-->
?
Inject the **tracing context** into the queue message, then extract it into the worker with OpenTelemetry-enabled mechanisms. Depending on duration and causation, create a child or a new trace linked by a link and application identifiers.
```python
# API: attach context to the message
msg["trace"] = {"trace_id": langfuse.get_current_trace_id(),
                "parent_span_id": langfuse.get_current_observation_id()}
# Worker: attaching his work to this trace
with langfuse.start_as_current_observation(name="worker", trace_context=msg["trace"]): ...
```
The context transport must not contain any secrets or proof of authorization. The worker must rebuild his rights from a reliable source. Test the real queue: a spread that works between functions can disappear at the process border.

---

Why do Langfuse observations become orphaned in async or threads? <!--anki:6436326433633838323936373466656439663436636438613435326465346162-->
?
The active **context** may not be passed to the task, thread, or process that is performing the work, so the span is created under a bad parent, or in an independent trace.

In Python, `asyncio.create_task` copies the current context, but `pool.submit(f)` does not transmit the `contextvars` to the pool thread; `pool.submit(contextvars.copy_context().run, f)` takes them away. Add a test that launches two intercalated queries and controls their parent-child relationships. Copying globally "the last trace_id" mixes users.

---

What data is needed to interpret the cost of a Langfuse generation? <!--anki:6531383263633931653631643461383238646633373466653866643863333661-->
?
The **model actually called**, the units of use available and a suitable pricing. Distinguish notably inputs, outputs and tokens cached when the provider exposes them.

An absent value should not silently become a zero cost. Example: the provider returns a dated name, `modele-x-2026-10`, absent from the price table; no cost is inferred and the table that adds up these generations underestimates the expense. Check alias, custom rates and specific counters. Periodically reconcile estimates with billing, keeping scope: some tool or infrastructure fees are excluding LLM cost.

---

How to correctly measure a streamed generation with Langfuse? <!--anki:3165313938623363666230653464303338313733333931653563306539333863-->
?
The observation must cover the actual **consumption of the stream**, not just the creation of the generator. Save first useful content, with `completion_start_time`, end or cancellation, and end use when available. A closed observation as soon as the generator returns displays a few milliseconds for a response of 12 s.

A missed response may have consumed tokens even if no totals were received. Mark usage as incomplete rather than zero. The generation latency and perceived delay by the user differ if a queue, fetch, or proxy delays the display.

---

Do not confuse: trace sampling and generation sampling? <!--anki:3166643861616465623234363466383438313161616663376139653963353934-->
?
The **sampling of traces** chooses which executions are kept for observability. The **sampling of generation** chooses the tokens of the model according to its distribution.

Reducing the former saves storage but can hide incidents; changing the latter changes responses. Documenting the retention probability and filters. A cost table built on 10% traces does not represent the total cost without a suitable estimate or other comprehensive counter.

---

Calculation: among 100,000 daily runs, each has independently 5% chance of being traced. How much average amount of traces is expected, and what probability of not keeping any traces among 10 failed runs? <!--anki:3235333764326665633935393435666461636235303330663738386431353339-->
?
We wait **100,000 × 0.05 = 5,000 traces**. For the ten failures, the probability of keeping none is **0.95¹⁰ ≈ 59.9%**.

The overall average may therefore seem sufficient while leaving a rare incident without evidence. Consider a targeted collection or conservation decided after observation of the result, taking into account the capabilities of the infrastructure and the biases introduced in the dashboards.

---

Where to hide sensitive data before sending to Langfuse? <!--anki:3838316261663163646131663461313762303236646566653364316136616164-->
?
Closer to the **instrument source**, before export, by covering inputs, outputs, tool messages, and metadata. The SDK's masking features help, but their scope needs to be tested.
```python
def masquer(*, data, **kwargs):
    return re.sub(r"\b\d{16}\b", "[CARTE]", data) if isinstance(data, str) else data
langfuse = Langfuse(mask=masquer)
```
`mask` only processes data from the Langfuse SDK; the spans of other OpenTelemetry instrumentation fall under `mask_otel_spans`. Prefer minimal collection and pseudonymous identifiers. Check exported payloads with synthetic secrets, rather than just displaying them in the interface.

---

Why can a short script lose its last traces Langfuse? <!--anki:3361373339386663393233373434383262313231643965373965643534633235-->
?
Observations can be **queued and then exported in the background**. The Python SDK sends them by default in batches of 512 Spans or all 5 s: a script that ends in 2 s may exit before the first shipment.

Provide for a flush or a clean stop of the client at the process life boundary, with a limited delay. A flush triggers or waits for the export according to the SDK; it does not prove on its own that any data has become searchable. Test network errors and abrupt stop.

---

How to avoid counting LLM calls twice in Langfuse? <!--anki:6238373733656630356433613433346261366232346637383366656338363239-->
?
Map active **instruments**: framework callback, vendor SDK, manual wrapper, and gateway. The same call can be observed at multiple borders.

Choose a reference observation for the tokens and cost, or explicitly link the others without adding two identical uses. The Langfuse client can discard the spans of a redundant library with `should_export_span`. A parent trace summarizing a cost should not be counted in addition to all of its children. Check an example for which the number of calls and the tokens are known.

---

What to expect if Langfuse becomes unavailable? <!--anki:3238313361373463646664343466626562646566636237633439353734316466-->
?
Distinguish between **diagnostic telemetry** and business log required to authorize an action. For the first, limit files, retrievals and memory so that an observability failure does not block all requests. The batch processor of OpenTelemetry, on which the Python SDK is based, keeps 2,048 spans in file by default and abandons the following ones.

Measure losses and report the blind period. If a durable audit is required before a sensitive action, save it in the business system with an explicit policy. The observability SDK is not automatically this audit guarantee.

---

How to check the instrumentation coverage of an agent? <!--anki:3339383631663663623762373463656138326632386331663166616332643632-->
?
Set a reference execution with **retrieval, two LLM calls, tool, error, and resume**, and then an explicit list of expected observations and relationships.

Example: Two visible LLM spans do not prove that the business action is instrumented. Verify presence, cardinality, parents, final status and correlation with this action; an assertion on an empty list must not succeed.

Waiting for the asynchronous export with an appropriate time limit, then reporting any missing observations. Controlling undoubled costs, properly closed streaming and absence of synthetic secrets. Replay after change of integration and during a collector failure; partial visibility is not complete coverage.

---

Why should trace context propagation be tested in asynchronous tasks instrumented with Langfuse? <!--anki:3137376338393334323039363436373039356462323831343533376361353036-->
?
A **Asynchronous Border** or a separate worker may lose the context that links the spans to the parent run. Calls remain visible but appear to belong to independent queries.

Transmit correlation identifiers through a documented mechanism, then check for kinship and chronology after passing through the queue. Test also for retries and errors. Do not put secrets in the baggage or propagated metadata. A complete trace allows to assign cost and failure to the right task; it should not depend only on the implicit context of a thread.

---

How to prevent a Langfuse export failure from blocking the application responses? <!--anki:6433626534616566363138643439313739306133333730643230313061313562-->
?
Decouple the export with bounded **buffers, deadlines and explicit policy of loss or recovery**. Observability should not become an infinite queue or indefinitely extend the response.

Monitor non-exported events and test an unavailable collection service. Some audit events require a stronger durability than sampled traces: treat them according to their contract, without assuming that everything can be abandoned.

---

Why can unsynchronized clocks make a distributed trace misleading? <!--anki:6334636130313261303437333435613662386166623634323663653364626532-->
?
Spans on several machines may seem **Overlapping or ending before they start** if the timestamps are compared without taking into account the offset.

Synchronize clocks, retain causal parentage, and locally measure durations with an appropriate clock. Do not conclude negative latency or business order from the time display alone. A correlation identifier connects events without correcting their clocks.

---

## Scenarios

Scenario: Langfuse shows all calls to the model, but no refunds or human wait times. How do you complete the instrumentation? <!--anki:6163366532316136613164383464323439643835326132653139666237653865-->
?
1. Identify off-gateway steps: tools, validation, queue and approval.
2. Add their observations and a stable folder identifier.
3. Connect the covers to the course without keeping a span open during the entire wait.
4. Compare the trace to the business log on a test folder.

**Strap**: assimilate LLM call coverage and application coverage.

Distinguish between active time and human expectation in the delay metrics. A replay two days later connects to the same file, while starting adapted observations; a single open span is not enough to describe this cycle.

---

Scenario: two simultaneous users appear in the same Langfuse tree after passing through threads. How do you fix? <!--anki:3961393232326663653466383464623262376133316338316133663136326436-->
?
1. Check the storage of the trace context and remove the shared global variables.
2. Spread the context specific to each task when crossing the thread.
3. Check session, run, and parent observations in a concurrent test.
4. Also control the masking and access to the traces concerned.

**Trap**: Change only the name of the observations while the parent is wrong.

---

Scenario: the cost displayed in Langfuse has doubled after activating an integration, without increasing traffic. What do you check? <!--anki:3630613334343835343764383431333962333334396537633262393766333334-->
?
1. Compare the number of calls billed and the number of generations exported.
2. Look for dual SDK, framework, or gateway instrumentation.
3. Check tokens, model names, rates, and parent-child aggregation.
4. Replay a known-use scenario before concluding an actual increase.

**Trap**: Arbitraryly divide all costs by two instead of correcting their origin.

Distinguish between estimated cost, supplier usage and reconciled bill. A parent trace can aggregate his children: summing both creates a double counting even if each call has been instrumented once.

---

## Sources
- [Langfuse — Good Trace Practices](https://langfuse.com/docs/observability/best-practices)
- [Langfuse — IDs and distributed tracing](https://langfuse.com/docs/observability/features/trace-ids-and-distributed-tracing)
- [OpenTelemetry — context propagation](https://opentelemetry.io/docs/concepts/context-propagation/)
- [Langfuse — masquage](https://langfuse.com/docs/observability/features/masking)
- [Langfuse — Sampling](https://langfuse.com/docs/observability/features/sampling)
- [Langfuse — Advanced SDK Features](https://langfuse.com/docs/observability/sdk/advanced-features)

- [OpenTelemetry — traces and correlation context](https://opentelemetry.io/docs/concepts/signals/traces/) — targeted deepening of the 12 November 2026; educational examples are built for this review.

## Connections
- [[91-langfuse-observability|Langfuse — Fundamentals]] — trace instrumentation
- [[93-monitoring-inference|Monitoring]] — connect traces and aggregate measurements
- [[84-streaming-application-integration|Streaming]] — observe the flow consumption
- [[152-pii-privacy|Privacy]] — minimize exported data
- [[90-012-langfuse-prompts-experiments|Langfuse — Prompts, datasets & experiences]] — origin and coverage of observations
- [[00-moc-ai-engineering|MOC AI Engineering]]
