# AI UX & human-in-the-loop — Flashcards
Tags: #flashcards #ai-engineering #ux #product #human-in-the-loop #llm
<!-- summary: copilot or autopilot, effective human validation, streaming, agent visibility, feedback, expectations, chat or dedicated interface, automation bias, errors and refusal, local correction of results, review capacity, before-after comparison. -->


Why is UX a subject of AI Engineer and not just a designer? <!--anki:473c3c77237b4b533a6b-->
?
Because interface choices **compensate for model limitations** (errors, latency, uncertainty) and **produce improvement data** (feedback, corrections). An average model with good verification UX can beat a better model presented as infallible.

Example: displaying the source next to an amount allows you to verify it in two seconds; without it, the user rechecks everything or makes a blind trust. The AI Engineer knows where the model is wrong, so where the interface must slow down the user. These choices are measured: verification time, correction rate, abandonments.

---

Do not confuse: AI that assists (co-pilot) and AI that acts (autopilot)? <!--anki:7a327b7b494e59375778-->
?
- **Copilot**: AI **proposes**, human **decids** (code suggestion, draft email) — tolerates errors, since human filters.
- **Autopilot**: AI **runs** only — requires much higher reliability and **safeguards**.

We often start as co-pilots. on **Measure** the acceptance rate, Then we automate the cases where it is very high.

The degree of autonomy is defined by action: an assistant can write alone but require validation before sending. Link each level to its permissions, its proof of execution and its possibility of backtracking.

---

How to design an effective human-in-the-loop? <!--anki:6b3241637143484d6449-->
?
- Request a validation **only** for actions **risky or irreversible** (otherwise tired of approval, the human clicks "yes" without reading).
- Show **exactly** what will be done (diff, recipient, amount), not a summary written by the model.
- Allow **modify** before approving, not just accept/refuse.
- **Journal** who approved what ([[103-agent-defenses|approbation humaine fiable]]).

If all proposals are accepted without reading, the presence of a button does not establish effective supervision.

---

Why does streaming change the experience? <!--anki:7a2c4128527e442d467d-->
?
He reduced the **Waiting Without Return** It allows you to start reading before the end. A finished answer in 10 seconds can be better perceived if useful content appears after 500 ms, This does not guarantee its acceptability.

Measure first useful content, fluidity and total delay: an animated indicator is not an answer. Predict incomplete markdown, interruption, late error and distinction between draft and final result.

Content that is already displayed cannot be “dispatched”. For sensitive data or output requiring global validation, buffer before display, even at latency prices. Streaming improves perception, not necessarily duration or reliability.

---

How to make an agent's work visible? <!--anki:5040712a5e662864245e-->
?
Display current **steps** ("Document Search", "Test Execution"), **tools called**, and allow for **interruption** or **redirection**. The user tolerates a long duration if he **sees the progress** and retains control.

Show understandable steps, not the raw reasoning or each technical call. For an agent that modifies data, display before execution what will change, for example "3 closed tickets, 1 email sent", then what has actually changed. This summary also serves as a trace when it is necessary to correct an error.

---

How do I collect useful feedback on an AI assistant's responses? <!--anki:6f52726d5e2c6f7d3d67-->
?
- **Light Explicit**: thumb up/down **at response**, with optional one-click reason.
- **Implicit**: copy, acceptance, modification, regeneration, abandonment.
- **Corrections**: When the user changes the output, the corrected version is a valuable **training data**.

Link each feedback to the complete **trace** ([[91-langfuse-observability|Langfuse]]) to be able to analyze it.

A click or a correction is not automatically a field truth or a retraining authorization. Keep reason and context with a suitable data policy, and then validate the corrections that become references.

---

How do I manage the expectations of AI app users? <!--anki:5165422e7e717c7b467e-->
?
- Announce **what the system knows how to do and does not know how to do** (perimeter, data freshness).
- Suggest **examples of requests** to guide usage.
- Display **sources** and the possibility of error, without generic warning ignored by all.
- Indicate that we are talking to a **IA** ([[155-ai-act|AI Act]] transparency requirement for chatbots).

Distinguish between startup, ongoing processing, and business system-confirmed success. Show a recoverable state after interruption and a way to fix or resume; prevent a progress indicator from simulating an unmeasured progress.

---

For an AI, chat or dedicated interface? <!--anki:642d7846327c23796a26-->
?
**chat** is flexible but requires the user to **know what to ask for** and write. For a **recurring and well-defined** task, a dedicated interface (summarize button, form, action built into the existing tool) is faster, more **valuable** and more reliable. The chat is suitable for **exploration**.

Example: To validate an invoice, displaying fields, documents and corrections side by side reduces the ambiguities of a free exchange. Measure time to correct result and manipulation errors; the number of messages sent is not a value measure.

---

What is Automation Bias? <!--anki:4264612378684778734c-->
?
The tendency of humans to **to trust too much** an automatic suggestion and **Do not check again**, Especially when the system is often right. It makes the human-in-the-loop **Illusory**. Parades: make the verification **Easy** (sources at the click of a button), report cases **Uncertain**, Audit by sampling validated decisions.

Demonstrate evidence, consequence, and actual ability to refuse, not just an "approve" button. Measure errors detected in controlled exercises; a high approval rate can signal justified confidence or superficial replay.

---

How to handle errors and rejections in the interface? <!--anki:67445f4276753a4d3569-->
?
**actionable** messages: say **why** (out of scope, missing information, blocked content) and **what to do** (reformulate, contact a human). Avoid dry refusals without explanation, and plan a **escalation to a human** for blocking cases.

Example: "I can't find this information in 2026 terms and conditions; you can rephrase or open a request" instead of "I can't answer". Also distinguish in security denial, missing information and technical error metrics: their causes differ. A rising refusal rate can signal an empty index rather than an overly cautious model.

---

Why should an AI interface allow to correct an error without starting the whole task again? <!--anki:3365316434666337303934373462653139626332636363386462376661373636-->
?
A **local correction** reduces human effort and avoids regenerating already validated parts. For an extraction, allowing to correct an amount while keeping its source page is often more useful than a global "try again" button.

Identify validated fields and decisions, retain their provenance and show the consequences of a change. Do not reuse an approval if the action changes. Measure correction time and remaining errors with users. Collect the correction as a signal to be checked, with a suitable data policy, before using it to train the system.

---

Why can a human validation queue become a bottleneck despite a fast agent? <!--anki:6639313332613335636339303430656538653038333532663737353339636339-->
?
If proposals arrive faster than humans process them, **wait accumulates**. Automation then shifts latency instead of reducing it.

Measure arrival rate, review time and backlog. Reduce unnecessary proposals, prioritize according to risk and limit admission. A rushed approval to empty the queue can turn human control into a valueless formality.

---

Why show a diff before approving an agent action? <!--anki:3264343336663365616634613437376662383761376636373565616434646132-->
?
The diff makes visible **specific changes and their targets**, rather than vague wording such as "update the record". The human can control the amount, recipient and eventual deletion.

Link approval to this versioned proposal. If the data changes after that, request a new validation or check an explicit compatibility rule. A "Approve" button with no specific purpose encourages attentional errors.

---

## Scenarios

Scenario: your tool requires human validation before each action, and users click “approve” without reading. How do you fix it? <!--anki:6c632d5f7b2e3f5a245e-->
?
1. **Reduce the number of requests**: validation reserved for risky or irreversible actions
2. **Show the concrete**: diff, recipient, amount, calculated by the code and not summarized by the model
3. **Allow to change** before approving, not just accept or decline
4. **Report uncertain cases** to focus attention where it serves
5. **Audit validated decisions by sampling**, because automation bias makes validation illusory

**Trap**: Measure success at the approval rate, which goes up just when people are no longer reading.

---

Scenario: your assistant takes 12 seconds to respond and users abandon it, while the quality is good. What do you change without touching the model? <!--anki:5265462a43554f23484f-->
?
1. **Streamer**: a first token in less than a second makes waiting acceptable
2. **Show the progress** of an agent, step by step, rather than a simple wait indicator
3. **Parallelize** what can be and pre-calculate frequent responses
4. **Allow to interrupt** or reorient along the way
5. **Measure Feeling**: TTFT p95 and dropout rate, not just total duration ([[64-inference-metrics-slo|SLO]])

**Trap**: Display the response of a block at the end, thinking that only the total duration counts.

---

## Connections
- [[31-agent-fundamentals|Agents]] — human-in-the-loop
- [[103-agent-defenses|Defenses of agents]] — approbation humaine fiable
- [[97-evals-online-ab-testing|Evals online]] — feedback and product metrics
- [[143-hallucinations-grounding|Hallucinations & grounding]] — show uncertainty
- [[64-inference-metrics-slo|Metrics & SLO]] — TTFT and perceived latency
- [[83-gateway-ingress|Gateway]] — streaming SSE
- [[163-real-time-voice|Voice & Real-Time Agents]] — the UX when the interface is the voice
- [[84-streaming-application-integration|Streaming & integration]] — the mechanics behind streaming
- [[140-010-transactions-outbox-sagas|Transactions & approbations]] — link consent to parameters actually executed
- [[140-011-agentic-application-architecture|— Architecture & Life Cycle]] — decisions related to proposals
- [[00-moc-ai-engineering|MOC AI Engineering]]
