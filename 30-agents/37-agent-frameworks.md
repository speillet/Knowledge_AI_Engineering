# Frameworks d'agents — Flashcards
Tags: #flashcards #ai-engineering #agents #frameworks #llm
Verified on: 25 September 2026 — This factsheet lists products, versions or regulatory texts that are evolving quickly.
<!-- summary: LangChain, LangGraph, CrewAI, Google ADK, OpenAI Agents SDK, Claude Agent SDK, LlamaIndex, framework or house code, comparative prototype with failures, state portability, business border. -->


What is an agent framework? <!--anki:7a3f7e4b6f3a367c3e6e-->
?
To provide **ready bricks**: model provider abstraction, tool declaration, agent loop, memory, state persistence, streaming, and observability integrations.

These bricks reduce the integration code and make certain behaviors standardized. They do not automatically define the right tools, permissions or success criteria. Before adoption, verify that we can understand the actual flow, inspect messages and resume a interrupted execution without depending on a hidden state.

A revealing test is to stop the process after a successful tool: does the recovery keep the result or repeat the action? The behavior matters more than the name of the abstraction.

---

What is LangChain? <!--anki:43603633354a63316478-->
?
A library of **Components LLM** (models, Prompt, Retrievers, tools) and **Integrations** with hundreds of suppliers. Since v1, it also provides a high-level agent, `create_agent`, Expandable by **middlewares** and built on LangGraph. Details: [[42-langchain-fundamentals|Basic]] and [[43-langchain-agents|agents]].

For a support wizard, these components link messages, model, and command lookup tool. Their interest is common integration; business validation remains in the application. Inspect the messages actually sent and test tool errors, because a uniform interface does not make vendor behaviors identical.

---

What does LangGraph offer in the LangChain ecosystem? <!--anki:7a6145323a375a645e41-->
?
A framework that models the agent as a **status graph**: nodes (steps), conditional edges, **cycles**, **checkpoints** persisted. It allows error recovery, **human-in-the-loop**, and "time travel" in execution. Details: [[44-langgraph-fundamentals|Basic]] and [[45-langgraph-production|production]].

For example, a graph can search for a folder, request an approval, and then execute an action. The checkpoint keeps the progress; it does not guarantee that an external effect will only be executed once. On a resume, replayed nodes must use idempotent operations or a reconciliation mechanism with the business system.

---

What does CrewAI offer compared to other agent frameworks? <!--anki:6a6e5763326c792b2f67-->
?
A **multi-agent-by-roles** approach: defines agents (role, objective, backstory) and **tasks**, which a crew executes in sequence or hierarchically. Very fast to prototype; the **Flows** frame crews in production. Details: [[46-crewai-crews|crews]] and [[47-crewai-flows|flows]].

A "researcher and then editor" team makes explicit the expected responsibilities and the deliverables exchanged. The roles remain, however, instructions to the model: they do not provide real expertise or access control. Define exit criteria, limit exchanges and compare the crew to a simpler solution on the same tasks.

---

What is Google ADK? <!--anki:7036305b5b3a4f7a6e36-->
?
Google's **Agent Development Kit**: open source framework (Python, Java...) to build agents and agent hierarchies, optimized for Gemini and the Gemini Enterprise Agent Platform (ex-Vertex AI) but multi-model, with support for **[[33-mcp|MCP]]** and the **A2A** protocol.

To judge its interest, make a small flow with a tool, a persistent session and a simulated failure. Check the capacities of the version and language retained, as well as the dependencies on the chosen deployment. **Multi-models** does not mean that each provider exposes exactly the same formats, tools or streaming functions.

---

What do model providers’ SDKs offer? <!--anki:4c6e4c5d762154776353-->
?
Frameworks **light**: **OpenAI Agents SDK** (agents, handoffs, guardrails, tracing) and **Claude Agent SDK** (the harness of Claude Code reusable: tools, sub-agents, hooks, MCP).

They facilitate access to the capabilities of their ecosystem, but do not necessarily offer the same guarantees of portability or persistence. Check on the chosen version the tools available, authentication, approval points and dependencies to the service provider. Evaluate a small complete task before building the entire application around the SDK.

---

Which agent framework for a data-centric agent, for typed outputs, or in the Microsoft ecosystem? <!--anki:3862306337396462366434393466303962653836363662366539636461653035-->
?
- **Data-centered agent** (ingestion, index, query engines, RAG): **LlamaIndex**
- **Typed and validated**: **Pydantic AI**
- **Microsoft Ecosystem** : **Microsoft Agent Framework**, heir to AutoGen and Semantic Kernel

For a state stream with checkpoints and interrupts: [[44-langgraph-fundamentals|LangGraph]].

These connections are **starting points**, because the perimeters overlap. A documentary assistant can also require typed outputs and a durable recovery. Pass through the prototype a parsing error, a refusal of access and a restart; retain the tool whose necessary guarantees are understandable and verifiable by the team.

---

Framework or house code? <!--anki:6d577d2f41337e3d4953-->
?
An agent loop holds in **a few dozen lines**: the house code keeps a **total control** and a simple debugging. A framework is justified for **persistence, multi-agent, human-in-the-loop** or when the team already masters one.

The minimal loop often hides the production work: cancellation, budgets, retrievals, events and message compatibility. Conversely, adopting a framework adds dependencies and migrations. Compare the maintenance cost on a concrete incident and check that we can inspect the state, rather than just count the lines of the prototype.

---

What criteria to use when choosing an agent framework? <!--anki:7350393a5947214d4f25-->
?
**Flow control** (explicit graph or standalone loop), **persistent** and recovery, **multi-model** and MCP support, **observability** native, maturity and stability of the API, team language.

Make a prototype covering a difficult case: tool in error, human interruption, restart and model change. Check traceability and operating cost, not just the brevity of the demonstration code. Prefer the smallest set of features that meets the measured needs of the team.

Set pre-test elimination criteria: no customer isolation or unchecked recovery. Additional integration does not compensate for the failure of a mandatory requirement.

---

Which abstraction trap should be avoided with agent frameworks? <!--anki:692c52522b5d41257d52-->
?
Avoid opaque **abstractions** that hide messages, tool calls and recovers actually executed. The traces [[91-langfuse-observability|Langfuse]] must allow to connect a business request to its calls, with masking of sensitive data.

Example: an application retry of three attempts envelops a client who makes three attempts himself; a request can trigger nine calls. The business code shows only one invocation.

Inspect effective settings, versions, results, and recovery policies, then reproduce a minimal case. Diagnose the offending layer before changing models; a useful abstraction must remain observable and testable.

---

Do not confuse: LangChain, LangGraph and LangSmith? <!--anki:443372515e4c38412956-->
?
```text
LangChain → components: models, tools, retrievers, and create_agent
LangGraph → orchestration engine and runtime (state graph,
              checkpoints, interruptions) that create_agent relies on
LangSmith → platform: traces, evals, datasets, and deployment
              (LangSmith Deployment, ex-LangGraph Platform)
```
In other words: **what** you write with, **what** executes the stream, **where** you observe and deploy it. The three are independent: you can use LangGraph without LangChain, or you can draw a house application in LangSmith.

An application can thus assemble its tools in LangChain, resume its execution thanks to LangGraph and analyze its traces in LangSmith. Do not confuse the presence of a graph with managed hosting, nor instrumentation with automatic quality evaluation. The choice of each layer depends on a separate need: integration, execution or operation.

---

How to compare two agent frameworks with a prototype that reveals their limitations? <!--anki:6536353766656666336530613437393238346666616539336430346463666634-->
?
Implement the **same small representative task** with an identical contract: business tool, typed output, human interruption and outage after external effect.

Compare result, recovery, traces, isolation and maintenance effort, fixing model and data. Include an error case and a change of state version; a demonstration without failure little test the guarantees of execution. Document the specific code of the framework and the export possibilities. The number of lines of the happy scenario is not enough to choose a production dependency.

---

Why isolate the business state model from the internal objects of an agent framework? <!--anki:3835373738346661303839383439653362333061663462666461336566356231-->
?
This limits **coupling to framework formats and lifecycles**. A decision, invoice, or authorization must remain interpretable without loading the entire orchestration library.

Use explicit contracts at the borders and retain the source of the data. Internal messages and checkpoints may remain framework-specific; predict their migration or extinction during a change. A uniform API to call a model does not guarantee the portability of suspended executions.

---

How to check the cost of a framework migration before adopting it? <!--anki:3564623037616165333333633437366239313934303962336233306535613233-->
?
Bring out from the prototype **a trace, a business state and a set of replayable tasks**, then implement a small variant with another orchestration or simple code.

Identify what depends on serializers, interrupts, storage and recovery mechanisms. Measure the effort on these borders rather than counting the lines of the first example. The goal is not to guarantee free migration, but to make costly dependencies explicit before generalization.

---

## Scenarios

Scenario: you start an internal assistant that calls three tools and must resume after a break. Framework or house code? <!--anki:75637d7a236b3c7a536a-->
?
1. **Frame the real need**: the call loop fits in a few dozen lines; what is expensive is the **persistence** and the recovery
2. **What pushes towards a framework**: checkpoints, human-in-the-loop, multi-agent, streaming, recovery after crash ([[44-langgraph-fundamentals|LangGraph]])
3. **What pushes towards the house code**: few steps, need for total control, team that knows no framework
4. **Frequently Compromised**: home loop on the raw API, plus a library for persistence
5. **Non-negotiable condition**: be able to **inspect raw calls** sent to the model ([[91-langfuse-observability|traces]])

**Pip**: choose a framework for its demos, then fight against its abstractions from the first special case.

---

Scenario: your team hesitates between CrewAI and LangGraph for a five-step document analysis process, with human validation at step 3. How do you slice? <!--anki:75723e2a6e663d59214b-->
?
1. **Look at the nature of the flow**: five known steps, with an interruption in the middle, it is an explicit **graph** more than a team of autonomous agents
2. **LangGraph**: explicit state, interruption and recovery, time travel, adapted to human-in-the-loop ([[45-langgraph-production|production]])
3. **CrewAI**: faster to prototype by roles, with **Flows** to frame the execution ([[47-crewai-flows|flows]])
4. **Decide on criteria**: flow control, persistence, observability, language and team skills
5. **Prototype** the same critical step in both, rather than deciding on the documentation

**Field**: Compare frameworks over the time of the first prototype, while the actual cost is in production.

---

## Sources

- [LangChain — documentation Python](https://docs.langchain.com/oss/python/langchain/overview)
- [Google ADK — framework documentation](https://adk.dev/)
- [CrewAI — Crews, documentation v1.15.23](https://docs.crewai.com/v1.15.23/en/concepts/crews)

## Connections
- [[31-agent-fundamentals|Agents]] — what frameworks implement
- [[33-mcp|MCP]] — standardized access to tools
- [[36-agent-orchestration|Orchestration multi-agents]] — patterns implemented by frameworks
- [[38-agent-platforms|Platforms of agents]] — where to deploy them
- [[42-langchain-fundamentals|LangChain]], [[44-langgraph-fundamentals|LangGraph]], [[46-crewai-crews|CrewAI]] — Detailed topics
- [[32-tool-calling|Tool calling]] — call loop on the raw API, often sufficient without a framework
- [[85-agentic-protocols-map|Map of protocols]] — which protocol to which agent boundary
- [[00-moc-ai-engineering|MOC AI Engineering]]
