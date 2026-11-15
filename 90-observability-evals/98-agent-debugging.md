# Agent debugging & failure analysis — Flashcards
Tags: #flashcards #ai-engineering #agents #evals #observability #debugging
<!-- summary: error analysis (open and axial coding), symptom or cause, failure categories, MAST taxonomy, loop detection, replay reproduction, failure in case of non-regression, production signals, when not to blame the model, controlled ablation, first divergence, debugging without effects. -->


Why is an agent harder to debug than a LLM call? <!--anki:63762b3d6f2b7d677546-->
?
- Failure often appears **away from its cause**: A bad tool result in step 3 produces a false response in step 15
- Behavior is **non-deterministic**: failure does not recur every time ([[114-reproducibility-variance|variance]])
- The trace is **long**: dozens of calls, tools and thousands of tokens

So you need complete **traces** and a method, not just error logs ([[91-langfuse-observability|traces]]).

---

What is error analysis? <!--anki:6c6b3c60573e3c384654-->
?
Examine cases, describe problems freely (**open coding**), then build an exploitable **failure taxonomy** and count their frequency on a suitable sample.

Example: "wrong answer" may cover missing document, ignored passage, or misinterpreted tool result. These categories lead to different fixes; trace and targeted replays help test the cause.

Include successes and contrasting cases, not just spectacular reports. Note frequency, severity and coverage; a biased ticket collection does not measure the overall rate. After correction, turn the cases into non-regression tests without over-adapting the entire [[94-evals-methodology|Evaluation]] to a few incidents.

---

Do not confuse: symptom and cause of agent failure? <!--anki:68364270646b286a3855-->
?
- **Symptom**: what the user sees. "False response", "the agent is running in circles"
- **Cause**: the **first step** where the trace deviates. Poorly formulated search, ambiguous tool description, truncated tool result, contradictory instruction

We correct the **first error** of the trace: the following often result from it.

The first anomaly observed remains a causal hypothesis. Replay with this corrected or simulated step, keeping the rest constant, and then check if the failure disappears. Several independent defects can coexist in the same trace.

---

Which agent failure categories do we encounter most often? <!--anki:727553234b4d6c736937-->
?
- **Specification**: ambiguous or contradictory instruction, absent end criterion
- **Tools**: wrong tool selection, invalid arguments, misinterpreted result ([[32-tool-calling|tool calling]])
- **Context**: missing, drowned or outdated information ([[35-context-engineering|context engineering]])
- **Verification**: the agent declares to have finished without checking
- **Boucles**: repetition of the same action without progress

The ranking indicates **where to act**: prompt, tool, retrieval, guardrails or model.

---

What does the MAST taxonomy say about multi-agent system failures? <!--anki:71372c644f7061407923-->
?
A study by 2025 ("Why Do Multi-Agent LLM Systems Fail?") classified the failures observed into **three families**:
- **Design and specification**: poorly defined roles, instructions not followed
- **Disalignment between agents**: information not transmitted, work ignored or duplicated
- **Verification and termination**: premature termination, absent or superficial verification

Useful conclusion: many failures come from the **system design**, not from the model limits ([[36-agent-orchestration|multi-agents]]).

---

How to detect that an agent is looping? <!--anki:732d7e23564a363e2826-->
?
- **Repetition**: same tool with the same arguments several times in a row
- **No progress**: no new state (file, data) since N steps
- **Overshoot** of planned number of steps or budget

Reaction: interrupt, send a message to the model that **describes the loop**, or escalate. And analyze the cause: often a tool error **misexplained** to the model ([[142-llm-reliability-resilience|resilience]]).

---

How to reproduce an agent failure? <!--anki:71245e54613635634565-->
?
- **Replay track**: Re-inject the same inputs and **results from saved tools**, to isolate the decision from the model
- **Figer** model, prompt and parameters; low temperature for diagnosis
- **Restart N times** the state just before the deviation, to measure the frequency of the error
- **Simulated tools** (mocks) for non-replayable actions: payment, email

A failure seen once out of ten is not corrected until this frequency is measured.

---

What to do with an agent failure once its cause is understood? <!--anki:69374a72434a62663952-->
?
1. **Correct** in the right place: prompt, tool description, retrieval, code guardrail
2. **Add the case** to the non-regression game, with the success criterion ([[153-data-flywheel-versioning|flywheel]])
3. **Check** that the correction does not break others, on the complete game
4. **Monitoring** in production the corresponding failure category

Without the 2 step, the same failure returns to the next model change.

Keep minimal input, initial state, versions, and observed effect without unnecessary sensitive data. The test must fail on the defective version and verify the business need; copying only the expected text can hide a new variant of the defect.

---

Which production signals point to the traces to be read? <!--anki:43695d442f3f3f7d6d33-->
?
- **Negative feedback** and escalation to a human
- **Tool errors** and policy rejection ([[115-agent-platforms-governance|gateway]])
- **Abnormally long** or expensive tracks
- **Reformulations** of the user right after a response
- **Random sample**, to find silent failures

Read every week a batch of tracks remains the most profitable activity to improve an agent ([[93-monitoring-inference|monitoring]]).

Combine selection by risk and random draw: the only slow traces ignore fast and convincing errors. Version the retained cases and limit their sensitive content before turning them into regressions.

---

When should an agent failure not be attributed to the model? <!--anki:7574796a2a7975773c63-->
?
As long as the trace shows a problem **upstream**: the information was not in context, the tool returned an unreadable error, two instructions contradicted each other, or the end criterion did not exist.

We blame the model when it fails **with** a correct context and clear tools, and that other models succeed on the same case ([[146-model-selection|choice of model]]).

---

Why does a component temporarily disable help debug a complex agent? <!--anki:3635373532666164616663643431336438616566303266333030316237333432-->
?
A **controlled ablation** removes or replaces a component to test a hypothesis: memory, ranking, compaction or tool. If the defect disappears, the component or its interaction becomes a track, not an already proven cause.

Replay the same entries with an initial state and controlled external effects. Change one dimension at a time and keep track, versions and results. Repeat if the system is stochastic. An ablation that simultaneously changes the budget and context may explain the improvement by these changes rather than by the removed component.

---

Why look for the first divergence of an agent path rather than correcting its last sentence? <!--anki:6435306363396665373432303462653962333034383330643231633564336262-->
?
The final answer can be **the result of a previous error**: wrong tool, truncated document or incorrect filter. Touching the formulation then hides the cause.

Compare observation, decision and result at each step with an expected trajectory or invariant. Replay the components in isolation and replace a tool result with a controlled reference. Then check the complete path to confirm the correction.

---

How to replay an agent trace without reproducing its external writes? <!--anki:6639316666383162353833303437343262646431383839633230646438383538-->
?
Replace the effect boundaries with **controlled duplicates or an isolated environment**, while maintaining the necessary contracts and responses for diagnosis.

Identify all writing paths, including application logs, messages, and callbacks. A "dry run" flag is only reliable if each border respects it. Test that no production connection is usable during replay.

---

## Scenarios

Scenario: your support agent has a success rate of 72%, and the team offers to move to the higher model, three times more expensive. How do you decide? <!--anki:413a343e41525d3b266a-->
?
1. **Read 50 failed tracks** and write down what is wrong, without pre-established categories
2. **Group and count**: e.g. wrong tool 40%, information 30% missing context, stop 15% without verification
3. **Correct non-model related causes**: tool descriptions, retrieval, verification step
4. **Remeasure**, then test the higher model on the remaining failures only
5. **Decide at cost per successful task** ([[121-inference-costs|costs]])

**Strap**: Pay three times more to hide design flaws.

---

Scenario: a user reports that a multi-agent agent has produced a "completely next to" report. The trace does 140 steps. Where do you start? <!--anki:7734242e6f3b4b567d29-->
?
1. **Review the request and final response** to accurately describe the variance
2. **Go back to orchestrator decisions**: plan and instructions given to each sub-agent
3. **Seeking the first deviation**: mistransmitted instruction, sub-agent who answered another question, summary who lost the essentials
4. **Replay** the offending step with the same inputs, multiple times, to measure the frequency
5. **Fix and add the case** to the non-regression game

**Trap**: Read the trace in order from the beginning, and get lost in it before reaching the offending step.

---

## Connections
- [[91-langfuse-observability|Langfuse & observability]] — traces to read
- [[94-evals-methodology|Evaluation — methodology]] — failures observed at metrics
- [[96-evals-rag-agents|Evaluation of Agents]] — measure after correction
- [[36-agent-orchestration|Orchestration multi-agents]] — coordination failures
- [[48-agentic-workflow-patterns|Patterns of workflows]] — Easy Steps to Diagnose
- [[114-reproducibility-variance|Reproducibility & variance]] — replay and measure frequency
- [[153-data-flywheel-versioning|Data flywheel]] — Turn Failures into Tests
- [[40-012-crewai-reliable-execution|CrewAI — Reliable Execution & Integration]] — attributing errors to steps
- [[00-moc-ai-engineering|MOC AI Engineering]]
