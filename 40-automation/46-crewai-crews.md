# CrewAI — Crews — Flashcards
Tags: #flashcards #ai-engineering #agents #crewai #llm
Verified on: 25 September 2026 — This factsheet lists products, versions or regulatory texts that are evolving quickly.
<!-- summary: agents (role, goal, backstory), tasks, sequential or hierarchical process, delegation, structured outputs, task guards, LLM and tools, unified memory, project structure, independence of validations between agents, task criteria, context contamination. -->


What is CrewAI? <!--anki:773073683f6e7832596e-->
?
A Python framework **multi-agents per role**, written **independently of LangChain**, describes a team (**crew**) of specialized agents and the **tasks** they must accomplish; the **Flows** ([[47-crewai-flows|CrewAI Flows]]) orchestrate the whole.

The role describes a specialization, while the tools determine what the agent can actually do. A crew can perform multi-tasking analysis; a Flow frames its triggers and branches. Measure the value of cooperation over a simpler pipeline before multiplying agents.

---

How to define a CrewAI agent? <!--anki:5064625e6870296b515a-->
?
By three fields in natural language that form its prompt:
- **role**: its function (“AI analyst”)
- **goal**: his goal
- **backstory**: its context and style
Plus its `tools`, its `llm` and settings (`max_iter`, `reasoning`, `verbose`...).

The role describes an expected skill; it does not grant actual permission. An "accounting" agent accesses the entries only by the tools actually exposed. Make its objective verifiable, limit its tool catalog and define a stop condition. A long and flattering backstory does not replace any exit contract or evaluation.

---

How do I set a CrewAI task? <!--anki:412a4645332e30695766-->
?
With a **`description`**, a **`expected_output`** and a **`agent`** responsible; `context` refers to the tasks whose results are needed.

Example: “compare the three quotes attached, excluding taxes, in EUR” is more verifiable than “analyze suppliers”. The expected output specifies supplier, amount, assumptions and reference to the quote; the context transmits the extracted quotes, not all previous exchanges.

`expected_output` remains a **sign**, not a compliance check. If the output feeds code, impose a schema and validate business rules: a well-typed number can still use the wrong currency or come from an outdated quote.

---

How to build and launch a minimum crew with CrewAI? <!--anki:7129717e4e6e464e4c69-->
?
```python
from crewai import Agent, Task, Crew, Process

analyste = Agent(
    role="AI news analyst",
    goal="Find important ads on {topic}",
    backstory="You follow AI news and always verify your sources.",
    tools=[search_tool],
)
veille = Task(
    description="Lists the 5 major announcements of the week on {topic}.",
    expected_output="bulleted list: title, date, source, summary in one sentence.",
    agent=analyste,
)
crew = Crew(agents=[analyste], tasks=[veille], process=Process.sequential)
result = crew.kickoff(inputs={"topic": "agents LLM"})
```
The `{variables}` is replaced by the `inputs` of the kickoff.

The example has an agent and a task: a crew does not require multiple agents. `search_tool` must be defined, and the model and its identifiers configured. The role and the biography guide the generation but do not prove the veracity of the ads; check dates and sources in the result.

If only three verified ads exist, producing five would invent facts to satisfy the format. Provide an explicit partial result and a search budget.

---

What methods of execution (processes) does a CrewAI offer? <!--anki:4f623b5a442b527c2b4d-->
?
- **Sequential**: Tasks run **in order**, each output feeds the next
- **Hierarchical**: a **agent manager** (`manager_llm` or `manager_agent` mandatory) **splits** tasks and **valid** results

Sequential is appropriate when dependencies are known; the hierarchical adds a coordination decision by model. This manager increases calls and can delegate poorly. In both cases, clarify the context needed for tasks and verify the final result with business criteria independent of the role of the agents.

---

What is delegation in CrewAI? <!--anki:67436a665f6224415725-->
?
With `allow_delegation=True` (disabled by default), an agent can **put a subtask or ask a question** to another agent in the crew.

Reserve this ability for tasks that really benefit from requesting additional expertise. Giving a specific question, call limits and a return format avoids circular exchanges. A delegation must not bypass permissions: the agent requested can only act within the authorized perimeter of the system.

---

How do I get a structured output from a CrewAI task? <!--anki:4e2826512a3b38495426-->
?
With **`output_pydantic`** (or `output_json`) on the task: the result is validated against the model. `output_file` also writes the result to a file.

Define a result model, such as a list of findings with source and severity. Explicitly deal with the failure of conversion or validation; do not let a free text pass for a valid object. The product file remains an artifact to control and its destination must be limited to the intended directory.

A valid URL does not establish that it supports the finding. Check the quoted passage separately from the structure validation.

---

What is a task guardrail in CrewAI? <!--anki:6761785230593f39772d-->
?
A **validation of the exit before moving on to the following**:
- **Function** Python that returns `(success, result_or_error)`
- **Text** describing the rule, verified by a LLM
On failure, the agent **restarts** with the error message.

A function is suitable for an exact constraint, such as a mandatory field; a LLM judge can appreciate a more subjective textual quality. Stop new attempts and provide an exploitable error. The guardrail validates the result of the task: it does not retroactively protect against an external writing already performed during its execution.

---

How does CrewAI connect to the LLM? <!--anki:79632352695739716b3a-->
?
By the class **`LLM`** and chains `provider/model` (ex. `"openai/gpt-4o"`, `"ollama/llama3:70b"`). Native SDK for large providers (OpenAI, Anthropic, Gemini, Azure, Bedrock), **LiteLLM** for other — we can also aim for a [[81-litellm-api-layer|proxy LiteLLM]].

The model ID is not enough to ensure compatibility: check authentication, base URL, tool formats and structured outputs. A proxy centralizes some controls, but adds an intermediary to diagnose. Test a simple call then a tool call, and keep track of the model actually served after a possible routing.

---

How do tools work in CrewAI? <!--anki:73416c25474152545177-->
?
The package **`crewai-tools`** provides ready tools (web search, Scraping, reading files, RAG…) ; Create your own with the decorator **`@tool`** Or by inheriting `BaseTool`. The servers [[33-mcp|MCP]] They are also usable.

A tool must expose a clear contract: arguments, result, error cases, and possible effects. Limit account permissions used and network destinations. Test functions separately from agents; a plausible response from the LLM may hide a tool that has never accessed the source or failed.

---

How does memory work in CrewAI? <!--anki:4e7d6e76596a3b63702c-->
?
A class **`Memory` unified** (which replaces the old short-term, long-term and entities memories): `memory=True` on the crew is enough. Memories are found by **combined score** (semantic similarity, recency, importance), stored by default locally (LanceDB).

Enabling memory changes the context of the following executions: a test may depend on previously created memories. Isolate test and production storage, control user perimeter, and schedule deletion. Check on a known sequence that a correction replaces the old memory; a high similarity score does not prove its current validity.

---

How is a CrewAI project organized? <!--anki:432d2c4b733677595a61-->
?
The CLI`crewai create`, `crewai install`, `crewai run`) generates a project. Recent versions describe agents and crew in **JSONC** (`crew.jsonc`, Folder `agents/`) ; many examples still use the old form **YAML** (`agents.yaml`, `tasks.yaml`) with decorators `@CrewBase`, `@agent`, `@task`, `@crew`.

Use the structure generated by the **installed version**, then version configuration, dependencies and business logic. Separate the secrets of the role and task files. During a migration, compare the prompt and the tools actually loaded: a file accepted by the parser can still describe a different crew than expected.

---

What are the limits of CrewAI crews? <!--anki:4b30352368505d537624-->
?
The behavior is based on **role prompts**: less fine control than [[44-langgraph-fundamentals|LangGraph]], execution **less predictable** in hierarchical mode, and **cost in tokens** high. Hence the use of **Flows** to frame crews in production.

A manager can delegate multiple times, rephrase a task, or accept an insufficient result, making cost and duration variable. A Flow sets steps and controls around this autonomy. Measure actual calls, limit attempts, and predict an explicit failure state when the crew does not reach the expected result.

---

Why don't two mutually agreeing CrewAI agents constitute two independent validations? <!--anki:3136336237333066633762393436623539376330326339336662616139373131-->
?
Agents can share **model, context, tools and source errors**. The second can also simply resume the conclusion of the first.

For useful verification, define an observable criterion and provide the verify with the necessary evidence, with deterministic control where it exists. For example, recalculating a total from the invoice lines brings more than a second opinion on the text produced. Measuring common errors and the cost added. Different roles or backstories do not automatically create statistical independence.

---

Why separate the acceptance criteria of a CrewAI task from the personality of the agent? <!--anki:3031373362386464393336633433303762623439346630613163363735383933-->
?
A role as a "rigorous analyst" influences style but does not define **a verifiable result**. The task must specify expected fields, usable sources, and rejection conditions.

An elegant report without evidence can satisfy the role while failing the task. Evaluate outputs with an independent grid and test incomplete entries. The agent description helps with execution; it does not replace either business contract or deliverable control.

---

How to limit the spread of an error between tasks in a crew? <!--anki:3936393663396130636265623461653838333534386134313965376336393466-->
?
Transmit **validated elements with their proofs and uncertainties**, rather than a long narrative presented as certain. A hypothesis of a task should not become a fact for all subsequent ones.

Add a control at the borders where an error changes the final decision. Keep the possibility of returning to the source. A synthesis task must signal the contradictions between outputs; reformulating them fluidly does not solve them.

---

## Scenarios

Scenario: your watch crew produces good results in demonstration, but in production it sometimes invents sources and costs three times the budget. What do you fix? <!--anki:654e6e2d6840715d293c-->
?
1. **Constrict releases**: `output_pydantic` with references and expected dates.
2. **Check evidence**: references actually retrieved, passages that support affirmations and freshness; an accessible URL does not prove the content.
3. **Borse corrections**: guardrails, delegation and iterations, with an overall budget and an explicit outcome in case of failure.
4. **Frame by a Flow**: deterministic steps around open research.
5. **Measure**: Acceptable cost-per-result and properly supported assertion rates, before and after.

**Pip**: enrich the backstories or check only HTTP 200, without checking the link between affirmation and proof.

---

Scenario: a colleague proposes to switch your crew to hierarchical mode to improve the quality. What questions do you ask? <!--anki:4c776f6e2849474f357d-->
?
1. **What problem is solved?** Hierarchical mode adds an agent manager that distributes and validates, so **more calls** and less predictability
2. **Is the sequence really insufficient?** Often, a well-defined `context` between tasks is enough
3. **What model for the manager?** A weak `manager_llm` degrades everything else
4. **How to measure?** Same task set, quality comparison, cost and latency ([[96-evals-rag-agents|evals d'agents]])
5. **How to debug?** In hierarchies, finding the origin of an error is much more difficult

**Trap** : adopt the hierarchical mode because it "looks like a real team", without measure.

---

## Sources

- [CrewAI — crews](https://docs.crewai.com/en/concepts/crews)

- [CrewAI — Crews, documentation v1.15.23](https://docs.crewai.com/v1.15.23/en/concepts/crews)

- 14 November supplement 2026 — Contracts and context of tasks: [CrewAI — Tasks, v1.15.41](https://docs.crewai.com/v1.15.41/en/concepts/tasks).

## Connections
- [[47-crewai-flows|CrewAI — Flows]] — orchestrate crews in production
- [[36-agent-orchestration|Orchestration multi-agents]] — sequential, hierarchical, delegation
- [[37-agent-frameworks|Frameworks d'agents]] — compare with LangGraph and ADK
- [[81-litellm-api-layer|LiteLLM]] — model access layer
- [[101-llm-security-guardrails|LLM Security]] — guardrails and tools
- [[39-agent-memory|Memorandum of agents]] — concepts behind unified memory
- [[40-012-crewai-reliable-execution|CrewAI — Reliable Execution & Integration]] — contracts and task execution
- [[00-moc-ai-engineering|MOC AI Engineering]]
