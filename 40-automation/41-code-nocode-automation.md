# Automation code & no-code — Flashcards
Tags: #flashcards #ai-engineering #automation #workflow #llm
Verified on: 25 September 2026 — This factsheet lists products, versions or regulatory texts that are evolving quickly.
<!-- summary: n8n, triggers, Zapier and Make, Airflow, Prefect and Temporal, durable execution, no-code limits, duplicates and webhooks mess, time zones, queue failure. -->


What is n8n? <!--anki:5074357b48742c717130-->
?
A Tool of **Automation of workflows** visual, **Self-hostable** (Fair Code License): **Nodes** Related (API, bases, LLM) triggered by **Triggers**, with the ability to insert JavaScript or Python code.

Each node receives data, performs an operation and forwards its output to the following. Example: receiving a form, extracting fields, validating and creating a ticket. Self-hosting gives control of the infrastructure but involves updates, backups, secrets and supervision; check the license conditions for the intended use.

---

What is a trigger in a workflow tool? <!--anki:68544b7e4c744e677a2d-->
?
The **event that starts a workflow**: webhook, scheduled schedule, message, or data change. It usually brings ID, date, and content.

Example: an order webhook is saved permanently, then processed in the background. The acknowledgment confirms its support, **not the delivery of the order**. If the producer returns the same event after a timeout, a stable key must prevent a second business action.

Predicting source authentication, deduplication, and recovery after failure. A scheduled trigger also requires setting time zone and behavior if the previous execution is not completed.

---

How do I integrate a LLM into an n8n workflow? <!--anki:4b76742c3c456f2b2679-->
?
By IA **nodes**: model call, structured extraction, classification, or node **AI Agent** with tools and memory — the agent becomes **a step** of a mastered workflow.

Surround the call with controls: input schema, output validation, timeout, and error branch. To classify a ticket, limit possible categories and then check the value obtained before routing it. The rest of the workflow retains explicit rules; a free response from the model should not decide on its own about an irreversible action.

---

How to choose between n8n, Zapier and Make for a workflow? <!--anki:78707c3f7a57534d4161-->
?
Compare tools on the **integration and operation need**. Zapier and Make offer hosted services with connectors and a visual editor; n8n offers in particular a self-hosting option and code insertion.

Check the connectors that are actually needed, the license conditions, the location of the data, the limits and the cost at the expected volume. Example: health data to keep on its servers are directed to n8n self-hosted; twenty common SaaS integrations without an operating team, to a hosted service. Self-hosting is not free to operate and a large catalog does not guarantee the good coverage of a API.

---

When to switch from no-code to code? <!--anki:4c5a477837435f66672d-->
?
When it is necessary to **version, test, review code**, manage complex logic, large volumes or strict SLA. The no-code excels for **prototype** and for simple integrations.

These capabilities exist to varying degrees in platforms: it is their concrete limitations that drive the transition. For example, keeping the editor to connect services and move a complex business rule into a tested API. Compare maintenance cost and team skills before rewriting the entire workflow.

---

Which “code” orchestrator for planned data pipelines, modern Python orchestration, or long workflows that survive outages? <!--anki:3965646437363366373533343431323962373938366663616639633465636330-->
?
- **Planned Batch Pipelines** (Data Processing DAG): **Airflow**
- **Modern Python orchestration**, focused on tasks or assets: **Prefect**, **Dagster**
- **Long workflows that have to survive breakdowns** (human expectations, agents): **Temporal** and its **durable execution**

Starting from the need for recovery: recalculating a data partition is not the same as resuming an approval wait after three days. Test delays, restarts and external effects with the chosen orchestrator. A durable execution keeps the progress, but replayable activities must always manage the idempotency of business writes.

---

Why is durable execution useful for agents? <!--anki:624b5d7544713e7d2179-->
?
It allows you to **recover a workflow from a durable history**, without redoing the steps whose result has already been saved.
```python
await workflow.execute_activity(propose_refund, case,
                                start_to_close_timeout=timedelta(minutes=5))
await workflow.wait_condition(lambda: self.decision is not None)  # human signal, no time limit
```
After a restart, the worker replays the history: the completed activity is not restarted, its result is reread.

A remote activity accepted just before a crash can, however, be restarted if its result has not been recorded. Provide idempotency keys, status verification, and cancellation policy; an engine does not transform an external API into a transaction. See [[45-langgraph-production|checkpoints]] for comparison of persistence boundaries.

---

Do not confuse: data orchestrator and durable execution? <!--anki:735f63646e702e615826-->
?
**Data orchestration** organizes dependencies, partitions, and results availability. **Sustainable execution** aims to resume workflows based on a persistent history of steps and events.

Example: Dagster recalculates the 21 October partition of an asset when its source changes; Temporal resumes the D-123 folder at the "wait to sign" step after a restart. These capabilities overlap across platforms. Examine the granularity of recovery, delays, cancellation, versioning, and external interactions. Persistence of the workflow does not guarantee that a remote activity is running once:

---

What are the limits of no-code in production? <!--anki:4169365566313b657b25-->
?
**Versioning and diff** difficult, **Automated Testing** limited, management of errors and secrets to monitor, and risk of **Shadow IT workflows** that no one maintains.

Name a manager, document dependencies, and schedule backup, alerts, and recovery. Test connector failure and duplicate notifications. A visually simple workflow can incur significant rights. Example: It uses an employee's personal token that is gone, revoked on a Friday, and fails every night without an alert. Use limited, renewable service identifiers, such as for a code-developed application.

---

Why should a workflow webhook tolerate events delivered multiple times or in a mess? <!--anki:6534373461653763386561313461363339656563643065393662616630623736-->
?
The **delivery of a webhook** can be repeated after an error or delayed by the network, so the arrival order does not guarantee the business order.

Check signature and freshness, save an event ID, and then deduplicate before the effect. For an old event, compare the version of the object or re-read its current state. Respond after a long-lasting support, according to the provider's contract. Test duplicates, delay and failure during writing; a visually linear workflow does not remove these distributed cases.

---

Why does a daily local time trigger require a time change policy? <!--anki:6132663733613562646637663464386438383537643066303064653835363964-->
?
In summer/winter, a local time may **not exist or occur twice**. "Every day at 02 h 30" is therefore not always a sequence of intervals of 24 hours.

Set the time zone and skip or duplicate policy, then identify the execution by its business period. Idempotence protects a duplicate; it does not create the missing execution. Test transitions and raises after the scheduler stops.

---

What should a fail queue do for an automated workflow? <!--anki:6538373535376362333666383432353562373562363362353535353965396433-->
?
It must keep **the event, cause, and history of attempts** in order to diagnose and then play back in a controlled manner. Moving a message in a queue does not solve its problem.

Distinguish correctable error from invalid data, fix the cause and then replay with the same business identifier if the operation should remain idempotent. Monitor age and volume of this queue. A massive replay without limit can recreate the initial failure.

---

## Scenarios

Scenario: the marketing department has set up an n8n workflow that sends customer emails with a LLM, and it is already in production. What are you doing? <!--anki:7773364f507c3d783c70-->
?
1. **Do not forbid it dryly**: it meets a real need and it turns. Removing it would push the subject into the shadows
2. **Inventory** What does he do, what data it touches, What secrets do they use? Who maintains it
3. **Secure the essentials**: keys passed by the [[81-litellm-api-layer|gateway]], budgets, no sensitive data in clear, centralized traces
4. **Framework**: human validation before sending, error management, owner identified
5. **Decide next**: keep it in no-code if it remains simple, or pass it in code if it becomes critical (versioning, testing, review)

**Trap**: Let a shadow IT workflow live without an owner, until the day it sends a thousand wrong emails.

---

Scenario: your customer onboarding process lasts three days, with two human validations and one LLM call per step. Which tooling do you choose? <!--anki:4d30377563394d6f6c5f-->
?
1. **Recognizing the need**: a long process, with human expectations, must **survive restarts**
2. **Durable execution**: Temporal or a checkpoint framework, to resume without replaying calls already made ([[45-langgraph-production|LangGraph in production]])
3. **Idempotence** of each step that writes or sends something
4. **Human waits** modeled as states, with expiration times and raises
5. **Observability**: where are each folder, which steps have failed ([[93-monitoring-inference|monitoring]])

**Trap**: A cron script that reruns everything from the beginning after an incident, and returns emails that have already gone.

---

## Sources

- [n8n — workflow documentation](https://docs.n8n.io/)
- [Temporal — Durable](https://docs.temporal.io/)

## Connections
- [[31-agent-fundamentals|Agents]] — workflow vs agent
- [[36-agent-orchestration|Orchestration multi-agents]] — when workflow is no longer enough
- [[32-tool-calling|Tool calling]] — A workflow can serve as a tool for an agent
- [[44-langgraph-fundamentals|LangGraph]] — workflows and agents in code, as a graph
- [[47-crewai-flows|CrewAI Flows]] — event workflows that orchestrate crews
- [[81-litellm-api-layer|LiteLLM]] — model access point
- [[91-langfuse-observability|Langfuse]] — traces remain centralized
- [[48-agentic-workflow-patterns|Patterns of workflows]] — the patterns behind workflows
- [[150-013-data-pipeline-orchestration|Transformations & orchestration of data pipelines]] — separating orchestration and processing
- [[00-moc-ai-engineering|MOC AI Engineering]]
