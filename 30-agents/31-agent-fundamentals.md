# Basics of — Flashcards
Tags: #flashcards #ai-engineering #agents #llm
<!-- summary: workflow or agent, ReAct pattern, minimal agent components, three forms of human-in-the-loop, risks and parades, cost orders of magnitude, stop conditions, end-of-task proof, environmental observableness, success and trajectory. -->


What is a LLM agent? <!--anki:502c4c3f7a7c7b624a33-->
?
A **LLM with tools and a loop of execution** (perceive → reason → act) that pursues a **objective** by deciding its own steps.

The model chooses an action; the program around it checks the rights, executes the tool and returns the observation. For example, it looks for a command before explaining its status. Its autonomy remains limited by the available tools, the budget and the stop criteria: **the model does not grant itself permissions**.

The distinguishing criterion is not the number of tools: it is the decision on the next step. A script that always calls the same functions remains a workflow.

---

Do not confuse: workflow and agent? <!--anki:712b5a28436a7b683047-->
?
A **workflow** follows steps predefined by the developer; a **agent** dynamically decides on its — distinction actions popularized by Anthropic (“Building effective agents”).

A workflow can contain LLM calls while keeping a fixed path: extract fields, validate, save. An agent chooses the next search according to what he discovers. Both combine: a workflow can delegate an open step to an agent, then validate its result before continuing.

---

What is the ReAct pattern? <!--anki:4e773142733d352f7878-->
?
**ReAct** alternates reasoning, action and observation to adapt the next step to the result obtained.
```text
Need: know the status of an order
Action      : order_status(order_id="CMD-004212")
Observation: {"status": "shipped"}
Next: answer or look for missing information
```
The [[32-tool-calling|tool calling]] provides a call format, but does not build this strategy or its loop on its own. The [[34-harness-plugins|harness]] must execute the authorized operations and re-inject their results. An explanation produced by the model sometimes helps in diagnosis; it does not constitute a faithful proof of its internal reasoning.

If the observation indicates "unknown command", the sequence must ask for precision or otherwise seek, not present the expected status as a fact.

---

What is a minimal agent made of? <!--anki:43784f552a2f34552f69-->
?
- A **model** that proposes the next step.
- From **[[32-tool-calling|Tools]]** to explicit contracts.
- A **control loop** that validates each request, executes the authorized operations and transmits the results.
- A **[[35-context-engineering|context]]**: instructions, history and useful information.
- **Stopping conditions**: verified result, budget achieved, refusal or request for help.

A prototype can be short; reliable execution also requires handling errors, cancellation and effects already produced. A final model response does not replace the verification of the business result.

---

When should I NOT build an agent? <!--anki:7330797b4f57247a213f-->
?
When useful steps are **known and sufficiently stable**, start with an explicit workflow: it facilitates control, measurement and diagnosis. A stand-alone loop must bring a demonstrated gain to justify its complexity.

For an invoice, the LLM can extract fields, code apply rules and a human handle exceptions. A variable path can justify an agent, without making it automatically preferable: compare success, errors, latency and cost to a baseline. The agent is chosen according to the need for adaptation, not according to the number of AI components.

---

What is human-in-the-loop? <!--anki:6e254c244e5b5d6d4e5d-->
?
The **human validation points** inserted into the loop of the agent, where a mistake would be expensive. Three forms:
- **Approval before action**: payment, e-mail, deletion. The agent stops and waits
- **Clarification request**: the agent asks a question rather than guessing
- **Review after the fact**: a human checks a sample of reversible actions

Too many approvals produce **fatigue** and blind validations: they are reserved for risky actions ([[144-ai-ux-human-in-the-loop|UX of human-in-the-loop]]).

---

What are the main risks of an agent? <!--anki:6c23424a5e3f5e732375-->
?
- **Infinite buttons**: same action repeated without progress. Parade: step budget and repetition detection
- **Objective drift**: the agent pursues another goal, sometimes after an injection. Parade: narrow tools, out-of-model policies ([[103-agent-defenses|Defenses]])
- **Destructive actions**: deletion, sending, payment. Parade: minimal permissions and human approval
- **Uncontrolled cost**: history grows with each turn. Parade: ceilings per task ([[121-inference-costs|costs]])
- **Silent failure**: the agent declares that it has finished without checking. Parade: explicit verification of the result

---

What orders of magnitude for the cost of an agent? <!--anki:743745713e294b57476e-->
?
In research workloads reported by Anthropic, an agent alone consumed about **4 times more tokens** than a chat, and a multi-agent system about **15 times more**. These observations are not universal bill multipliers.

Each turn can return the history; each agent adds its own context. Estimate the cost with tokens input, output, cache, models and tools actually used. Then compare the cost **per successful task** to the value produced ([[123-aggressive-caching|caching]], [[122-finops-llm|FinOps]]).

---

How does an agent know when to stop? <!--anki:653272545f6866677138-->
?
The protocol can signal the end when the model responds without tools or emits a dedicated signal; the harness also imposes limits on iterations, time and cost.

Distinguish **completed, successful, blocked and interrupted**. Example: to produce a CSV, the existence of the file is not enough; check required columns, expected number of rows and absence of export error. A phrase "it is done" is not proof.

In case of limit reached, save the useful progress and return partial result, uncertainties and next step. The success criterion must be defined before execution, regardless of the self-evaluation of the model.

---

What proof do I need to ask before an agent announces that a business task is complete? <!--anki:6236373266383337663938303463393462303462663030323039656461663066-->
?
Define a **observable end condition** in the business system: saved command, published document, or actually passed test. A model sentence, a completed plan, or a tool call sent is not enough.

Associate the operation to an identifier and verify its end state with the authoritative source. Distinguish success, failure and result still unknown. If a processing is asynchronous, announce its launch and then follow its confirmation. This distinction prevents an agent from turning an intent or an acknowledgment into user success.

---

Why does an agent sometimes have to look at the environment again before acting? <!--anki:3965376432336139613537373436316138636330643939343863623164313430-->
?
Its internal state can be **timed or incomplete**. Between reading a stock and a reservation, another transaction can consume the last unit.

Re-observe important data and have preconditions checked by the business department at the time of writing. Correct reasoning on an old observation does not guarantee correct action now. Provide an explicit "precondition become false" result that results in a new decision, without a blind loop of repeats.

---

Why evaluate the trajectory of an agent in addition to its final response? <!--anki:3962636638383665376237303433306439633864616433656136373234383330-->
?
A correct answer may have been obtained with **prohibited action, excessive expense, or data leak**. The end result does not reveal these defects.

Evaluate important transitions: permissions, actually executed calls, effects, budget, and proof of termination. Do not impose a single path if several are valid; check properties and results. An agent that abstains correctly after denial of access can better comply with the contract than an agent that "successfully" by bypassing this denial.

---

## Scenarios

Scenario: the profession wants "an AI agent" to process leave requests, which always follow the same rules. What do you answer? <!--anki:6f2d7b747a3e764a7673-->
?
1. **Qualify task**: is the path known in advance? Here yes, so a **workflow** is more reliable, cheaper and easier to debug ([[41-code-nocode-automation|automation]])
2. **Place the LLM where it brings value**: understand the demand in natural language and extract the fields, the rest being deterministic code
3. **Keeping a way out**: out-of-the-way cases go to a human
4. **Measure**: automatic processing rate, errors, cost per request
5. **Reserve the agent** for tasks whose steps really vary from case to case

**Trap**: Add autonomy without demonstrating its value or providing the necessary controls and traces.

---

Scenario: your analysis agent sometimes turns 40 steps, costs expensive and ends up with no useful answer. What limits do you pose? <!--anki:42587c246536282e3159-->
?
1. **Fences**: Maximum number of iterations, budget in tokens and duration per task ([[122-finops-llm|FinOps]])
2. **Clear stop conditions**: Explicit success criteria in the prompt and, if possible, verifiable by code
3. **Detect loops**: same repeated tool calls, no progress between two steps
4. **Cut**: Subtasks with a clean context rather than a long trajectory that saturates the context ([[35-context-engineering|context engineering]])
5. **Clean Failure**: Give back the hand to the human with the state of progress rather than insist

**Trap**: Raise the iteration limit when the agent fails, instead of understanding why they are not moving forward.

---

## Sources

- [Yao et al — ReAct](https://arxiv.org/abs/2210.03629)

- [Anthropic — consumption observed in its multi-agent search system](https://www.anthropic.com/engineering/multi-agent-research-system)

## Connections
- [[32-tool-calling|Tool calling]] — the hands of the agent
- [[34-harness-plugins|Harness]] — Execution Framework
- [[35-context-engineering|Context engineering]] — Working Memory
- [[36-agent-orchestration|Orchestration multi-agents]] — Scale
- [[41-code-nocode-automation|Automation]] — workflow vs agent
- [[96-evals-rag-agents|Evals d'agents]] — trajectory, final state, pass^k
- [[141-system-design-llm|System Design LLM]] — workflow or agent
- [[165-computer-use-browser-agents|Computer use & browser agents]] — when the tool is a GUI
- [[48-agentic-workflow-patterns|Patterns of workflows]] — dial before making autonomous
- [[22-advanced-rag|RAG — Advanced]] — hybrid search, reranking and filters
- [[37-agent-frameworks|Frameworks d'agents]] — framework panorama
- [[44-langgraph-fundamentals|LangGraph]] — state graphs for agents and workflows
- [[47-crewai-flows|CrewAI — Flows]] — event-driven workflows
- [[00-moc-ai-engineering|MOC AI Engineering]]
