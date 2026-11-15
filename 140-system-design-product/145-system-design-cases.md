# LLM system design cases — Flashcards
Tags: #flashcards #ai-engineering #system-design #interview #llm
<!-- summary: customer support, document research, code assistant, natural language data analysis, large-scale extraction, acting agent, consumer chatbot, voice assistant, response frame, maintenance errors, human review capacity calculation, storage estimation, hypothesis validation. -->


Case 1 — Customer Support Assistant: What does the request do? <!--anki:765e30282f603b217430-->
?
1. **Intent classification** (small model): question, action on account, claim, out of scope.
2. **RAG** based on knowledge (hybrid + ranking), filtered by product and language.
3. **Reading tools** (order status) via authenticated API **on behalf of the customer**.

The intent classifier in mind reduces cost and latency: simple questions trigger neither tools nor large models, and claims can go directly to a human. The tools remain in **read**: as soon as an action modifies the customer's account, we switch in the case of an agent who acts, with its safeguards.

---

Case 1 — Customer Support Assistant: How do I frame the answer? <!--anki:44453a5b504657536c68-->
?
1. Generation with **quotations** and **abstention**.
2. **Scale** to a human with summary of the conversation.
3. Ratings: rate of **resolution without human**, truthfulness, CSAT.

The wizard must link the affirmations to the applicable policy and avoid promising an unauthorized refund. Escalation conveys the problem, the evidence and the steps already attempted to avoid the user repeating everything. Evaluate the actual resolution and costly errors; a good satisfaction score is not enough to prove the actuality.

---

Case 1 — What are the specific customer support risks? <!--anki:6f2e25642c397d425d38-->
?
- **Invented commitments** (reimbursement falsely promised) → the model has **no right** to promise; actions go through tools with business rules.
- **Prompt injection** by customer message or ticket.
- **Data leak** from another → client identity filter **server side**.
- **Your** unsuitable on an angry customer → detection and escalation.

Test the rights borders with two hostile accounts and attachments. For commercial gestures, check the amount, recipient and history directly in the business system; a reassuring response does not prove a correct refund.

---

Case 2 — Internal document search (“chat with our documents”): the hard points? <!--anki:474f652b735665542c6c-->
?
- **Access rights**: Each chunk carries the **ACL** of the source document, filtered at the retrieval according to the user (never "index everything then ask the model to filter").
- **Heterogeneous ingestion**: PDF, slides, tables, wikis → [[162-document-parsing|Parsing of documents]].
- **Fresh**: Incremental synchronization, deletion propagated.
- **Contradictory or obsolete documents**: date metadata, priority to reference sources.

---

Case 3 — IDE Code Wizard: what constraints? <!--anki:79237278407c2d442c51-->
?
- **Autocomplete**: latency **< 200-300 ms** → small specialized model (fill-in-the-middle), cache, cancellation of obsolete queries.
- **Chat / agent**: strong model, **context** built from the repository (open files, symbol search, code index).
- Security: **secrets** excluded from context, execution in **sandbox**, review of changes ([[106-coding-agent-security|Code Agents]]).
- Key metric: **acceptance rate** and code stored at J+N.

---

Case 4 — Natural Language Data Analysis Wizard: What Design Choices? <!--anki:3136636634613865343265393435373439393461316439346434396237646536-->
?
- **Question business views** or a **semantic layer**, not raw tables: the numbers must coincide with the dashboards ([[26-text-to-sql|text-to-SQL]]).
- **Schema linking**: Provide only useful tables, with → SQL question descriptions and examples validated.
- **Secure execution**: read-only account, line level security, timeouts and budget per request.
- **Verifiable response**: Display the query, filters, and conventions applied.
- **Execution Accuracy** assessments on real business issues, including ambiguity.

---

Case 5 — Agent that performs actions (reservations, tickets, operations): what should be added? <!--anki:68366c3f4f3a5e684940-->
?
- **Tools with minimum permissions**, identity **delegated** of the user.
- **Human confirmation** for irreversible or costly actions.
- **Limits**: steps, budget, maximum amount.
- **Complete audit log** and **kill switch**.
- Environment of **eval in sandbox** before production ([[115-agent-platforms-governance|Governance]], [[103-agent-defenses|Defenses]]).

Orders of magnitude to be set: for example 15 steps, 0.50 € Model and 100 € Reimbursement per task without validation. Confirmation refers to the concrete effect, “ Book AF123 Flight 4 May for 412 € », Not on a vague title. The tool must be idempotent so that a resume does not reserve twice ([[149-delivery-idempotency-concurrency|idempotency]]).

---

Case 6 — High traffic consumer chatbot: cost priorities? <!--anki:757d596e60654e602f71-->
?
Start with the **cost per successful conversation**, then optimize your dominant positions:
- [[82-routing-llm|Routage]] rated to a cheaper model when it meets the criteria.
- Prompt caching of stable prefixes.
- History mastered without losing preferences, constraints or essential context.
- tokens quotas, calls and expenses.

Example: A semantic cache may reuse a public FAQ, not a personal answer on an account balance. Include holding, rights, and freshness in the eligibility, or waive the response cache.

Maintain moderation and critical controls; a drop in cost accompanied by more repeats or human review can be a false gain.

---

Case 7 — Real-time voice assistant: which constraints dominate? <!--anki:74722e2b763c26706a56-->
?
The **end-to-end latency** (< 1 s felt): pipeline **STT → LLM → TTS** Streaming at every stage, or model **speech-to-speech** native; End-of-speech detection and **Management of Interruptions** (barge-in). Replies **Short** and without markdown[[163-real-time-voice|Real Time Voice]]).

This second is an illustrative target to validate. Measure → first useful audio, with network and silence detection. If the user interrupts, also stop the audio already buffered and avoid adding to the context sentences that he did not hear.

---

How to frame the need, architecture and data in a system design response? <!--anki:7525777d58607c31264e-->
?
1. **Clarify** need and constraints, **encrypt** load.
2. **Simple baseline** + measurable success criteria.
3. **Architecture** and **flow** of a query.
4. **Data**: ingestion, freshness, access.

Encrypt, for example, the number of records per day, the length of entries, and the expected time. The feed must show where the information comes from and when permissions are applied. A testable baseline makes assumptions explicit and provides a benchmark for future optimizations.

---

How to cover models, risks and operation in a system design response? <!--anki:62545b3b23662a533b7a-->
?
5. **Models**: choice, routing, fallbacks.
6. **Security and Compliance**.
7. **Evals** offline and online, **observability**.
8. **Costs** and **evolution** (v2, v3).

Explain an incident and its response: allowable fallback, partial restitution, or human escalation. Give a cost per task and metrics that would warrant a more complex version. The conclusion must show a reasoned choice, its limitations, and how to verify that it works on the expected load.

---

What errors should I avoid in LLM system design maintenance? <!--anki:646e3f68777c4f522c4f-->
?
- Offer **directly a multi-agent** or a fine-tuning without justification.
- Forget the **evals** and the measure of success.
- Ignore **access rights, PII and prompt injection**.
- Don’t give **any number** (volume, cost, latency).
- Present the model as **reliable** with no plan for its errors.

Make the hypotheses reviewable: “10 requests/s, point ×3, answer p95 under 5 s” allows to discuss capacity and file. Separate known data, sizing hypotheses and measurements to be made to the prototype.

---

Calculation: 200 daily files require a review of 6 minutes, but two people spend only 4 hours each. What capacity and what daily delay? <!--anki:3265353363323565346531393436326539363135333830636365393034643539-->
?
Available capacity is `2 × 4 × 60 / 6 = 80 dossiers/day`. With **200 daily arrivals**, the delay increases by **120 records/day**, excluding changes and recoveries.

A human review does not stabilize the system in this scenario. Reduce the volume, time per file or increase the capacity; reserve the controls according to the risk without removing an essential validation. Include wait times and peak load in the design. A good precision of the model does not compensate for a structurally saturated human queue.

---

Calculation: a Treating Assistant 40,000 tasks per day and keeps 25 KiB of traces per task during 30 days, without replication or compression. What kind of rough storage to expect? <!--anki:3461646137363162356432333432366561323263306433663165356365633737-->
?
The volume is equal to **40,000 × 25 × 30 = 30,000,000 KiB**, or approximately **28.6 GiB**.

Add index, replication, backups, and margin depending on the architecture. The raw content of the documents can change the order of magnitude significantly. Link this estimate to the retention policy and the actual diagnostic need, rather than keeping everything by default.

---

Why announce the most risky assumptions before drawing a complete AI architecture? <!--anki:3263306334643337343939303466303661623161613538373836306438393564-->
?
They determine **What to Test First** : attainable quality, availability of evidence, right of access or ability to review. A detailed architecture does not compensate for a false business assumption.

Propose a short experiment with success and stop criteria for each major unknown. Then update the sizing and component choices. Distinguish what is measured from what remains an estimate.

---

## Scenarios

Scenario: a candidate proposes, for a support assistant, an architecture with five autonomous agents with a fine-tuned model. How do you react as an evaluator? <!--anki:694f7656574c4e26294b-->
?
1. **Ask for justification**: What would a workflow with RAG not cover?
2. **Point the cost**: five agents multiply tokens, latency and debugging difficulty
3. **Question the fine-tuning**: what data, what behavior, what alternative per prompt?
4. **Search for gaps**: access rights, prompt injection by customer messages, evals, escalation
5. **What is expected of a senior**: start simple and **prove** with an eval the need to climb a notch

**Trap**: judge the proposed architecture on its sophistication rather than on its adequacy.

---

Scenario: you are asked to design a data extraction on 20 millions of documents, with a tight budget and no latency constraints. What architecture do you propose? <!--anki:4e7c3e533470396f7b59-->
?
1. **Batch asynchronous**: Delayed processing, cheaper, GPU kept at full load
2. **Constraint outputs** per schema, with business validation thereafter ([[63-guided-generation|guided generation]])
3. **Small model** fine-tuned or distilled, if the volume justifies the investment ([[53-synthetic-data-distillation|distillation]])
4. **File of exceptions**: low confidence cases go towards a human review
5. **Idempotence and recovery**: an incident must not reprocess the 20 million documents

**Strap**: Sizing this processing as an interactive service, with synchronous calls one by one.

---

## Connections
- [[141-system-design-llm|System Design LLM]] — method
- [[142-llm-reliability-resilience|Reliability & resilience]] — hold in production
- [[22-advanced-rag|Advanced RAG]] — ACL and hybrid search
- [[36-agent-orchestration|Orchestration]] — when several agents are justified
- [[162-document-parsing|Parsing of documents]] — ingestion of real corpus
- [[163-real-time-voice|Real time voice]] — Voice Case
- [[122-finops-llm|FinOps LLM]] — control cost at scale
- [[148-llm-batch-pipelines|Pipelines batch]] — the case 4 in detail
- [[101-llm-security-guardrails|LLM Security]] — injection, exfiltration and guardrails
- [[49-coding-agents|Code Agents]] — Use and Integrate Code Agents
- [[00-moc-ai-engineering|MOC AI Engineering]]
