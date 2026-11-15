# Agent Platforms — Flashcards
Tags: #flashcards #ai-engineering #agents #platform #llm
Verified on: 25 September 2026 — global date preserved; targeted review of 13 November 2026 detailed in Sources.
<!-- summary: Different from a framework, bricks, levels of abstraction (API, runtime, Harness managed, cloud offerings and model providers, open source, runtime and double texting, sandbox and sandbox services, gateway of tools, register, identity, Delegated or autonomous agent, memory, Observability, evals, ProtocolsMCP, A2A), Build or buy. The rest, Senior level, is the topic 115 of the Section 110, work quotas and equity between supporters, control plan unavailable, Isolation of quotas. -->


What is an agent platform compared to a framework? <!--anki:66657538313d7a42737a-->
?
The **[[37-agent-frameworks|framework]]** serves to **Write** the agent (library); the **Platform** to **Execute and govern it in production** Runtime managed, Sandbox, memory, access to tools, identity, access policies, Observability, evals. The senior suite of this file: [[115-agent-platforms-governance|Architecture & Governance]].

A library running on a computer does not become a platform because it knows how to call tools. It also has to organize deployments, identities, resource limits and recovery after failure. Clarify who exploits each brick: adopting a managed offer moves some responsibilities without removing business controls.

---

Which execution bricks provides an agent platform? <!--anki:737d4d4e712a33605833-->
?
A platform can provide four complementary bricks:
- **Runtime**: Run sessions and track their lifecycle.
- **Sandbox**: Isolate code or browser and limit their resources.
- **Memory**: Retain and recall session status and durable information.
- **Tool Gateway**: Expose APIs under control, possibly via [[33-mcp|MCP]].

For example, an agent scans a file in a sandbox and then calls a business tool via the gateway. Isolation reduces the possible effects; it does not make running without risk. Also control network, secrets, mounted volumes and separation between users.

---

What governance bricks does an agent platform provide? <!--anki:5262495061614f2a237c-->
?
- **Register**: catalogue of agents, tools and skills
- **Identity and access policies**: who the agent represents, what they have the right to do
- **Observability, evals, costs**

In 2026, AWS, Google and Microsoft offer all these bricks, often **useable separately**.

The registry allows you to know **which version is allowed**, while policies determine who can run it and with which tools. Associate each deployment with an owner, a budget and a removal procedure. Check the actual integration of the bricks: a catalog without control at the time of the call does not prevent a prohibited action.

---

What levels of abstraction do platforms offer? <!--anki:493c4c5225462a41395a-->
?
From the most flexible to the most turnkey:
1. **API of the model**: we write our own agent loop ([[34-harness-plugins|harness]]) and host it ourselves
2. **Managed runtime**: you bring your agent code, regardless of the framework (LangGraph, ADK, CrewAI...), and the platform executes it (sessions, scaling, isolation)
3. **Harness Managed** A: On **Declares** only the model, The prompt, tools and skills, and the platform provides the loop itself (e.g. **Claude Managed Agents**, **AgentCore Harness**)

---

Which product serves as an agent platform at AWS, Google, and Microsoft? <!--anki:6c2e232f513e5d4f3246-->
?
- **AWS** : **Bedrock AgentCore**
- **Google**: **Gemini Enterprise Agent Platform**, new name for Vertex AI since April 2026
- **Microsoft**: **Foundry Agent Service** to build and run, **Agent 365** to govern
- **Data and SaaS Editors** Databricks, Snowflake, Salesforce Agentforce, ServiceNow

The three clouds cover the same bricks: runtime, memory, gateway tools, identity, observability, evals and policies. Retain the correspondence with its ecosystem, not the list of components, which changes quickly.

---

Beyond their SDKs, what offers from agents offer OpenAI and Anthropic? <!--anki:4824477c257e78733d3a-->
?
- **OpenAI**: Agents SDK, ChatGPT Workspace Agents and **OpenClaw Enterprise**, open source control plan still in **pilot**. Agent Builder has been deprecated since the 3 June 2026, with closure announced on **30 November 2026**; export requires reconfiguration and validation.
- **Anthropic**: Claude Agent SDK and Managed Agents; the hosted service remains in beta, with agent, environment, session and events.

Distinguish **local sandbox and fully self-hosted service**: the latter is accessible on request and modifies storage and operation. None of these names guarantees that the inference is local; check the model provider actually called and the applicable contracts.

---

Are there open source agent platforms, and at what levels? <!--anki:63642e78254937534137-->
?
**Yes**, on two levels:
- **Self-hosting visual builders**: **Dify** (full suite: workflows, knowledge base, app publishing), **Langflow**, **Flowise**, **n8n** (automation with agent nodes)
- **Infrastructure Bricks**: **kagent** (agents declared as Kubernetes resources and deployed in GitOps), **Agent Sandbox** (sandboxes on Kubernetes), **agentgateway** (gateway for MCP, A2A and LLM)

**Self-hosting does not always mean open source**: check the license of each component, including commercial usage restrictions. Also compare features reserved for paid offers and operating effort.

---

What does an agent runtime do compared to a traditional web deployment? <!--anki:423134626b627b623839-->
?
An agent does not look like a short HTTP request:
- **Long sessions**: minutes, hours, even days (e.g. up to 8 h per session on AgentCore Runtime)
- **Insulation per session**, often one microVM per session
- **Asynchronous execution** in the background, triggering by **cron** or by event
- **Recovery after failure** thanks to the saved state ([[45-langgraph-production|checkpoints]])
- **Streaming**,**interruptions** for human-in-the-loop, concurrent message management

---

What is double texting? <!--anki:6d6275635935573e2957-->
?
The user sends a **new message while the agent is still working** on the previous one. The runtime must decide what to do with the current run: finish it, interrupt it or cancel it.

The policy can queue the message, interrupt the work or replace the request depending on the product. It is necessary to preserve a consistent history and avoid two competing entries in the same state. A cancellation does not defeat the external effects already achieved: inform the user of what is still in progress or already accomplished.

---

What strategies does a runtime offer against double texting? <!--anki:42397a604d446b253650-->
?
In the LangSmith Deployment vocabulary:
- **Enqueue**: Put the new message on hold.
- **Reject**: Reject competitor execution.
- **Interrupt**: interrupt the current run while maintaining its state for the future.
- **Rollback**: Drop the current run state changes before the next one.

Choose by trade: a draft fix can interrupt the work; an operation already started requires more coordination. **Rollback does not call back an email or cancel an external payment.** These effects require idempotency or compensation. Test the behavior when the second message arrives before, during and after the action.

---

Why does an agent platform provide a runtime sandbox? <!--anki:74725137757b39403351-->
?
The code, commands, and web navigation generated by the model are **untrusted code**, potentially influenced by a prompt injection. The sandbox executes them in a **isolated and disposable** environment:
- **Strong insulation**: microVM (Firecracker), gVisor or Kata, rather than a conventional container that shares the host's kernel ([[03-containerd-runc|runtime]])
- **Filtered outbound network**, ephemeral file system, CPU limits and memory
- **No secrets** accessible from the sandbox

---

What kind of sandbox service to choose for an agent: offer of its cloud, specialized service or sandbox on its own cluster? <!--anki:493231677a3150776559-->
?
- **Cloud managed**: AgentCore Code Interpreter (AWS), Cloudflare Sandboxes
- **Specialized**: E2B, Daytona, Modal
- **On its cluster**: Agent Sandbox for Kubernetes, with a **pool of preheated sandboxes** to hide boot time

Criteria of choice: isolation technology, **start time**, possible persistence between two calls, network filtering. See also [[34-harness-plugins|harness]].

Test isolation with two simultaneous tasks and a forbidden network output. A quick start does not evaluate boundary resistance or data erasure after destruction; review these guarantees separately.

---

What is a tool gateway (or MCP gateway)? <!--anki:677b3430255e3c483576-->
?
The **single point of passage between agents and tools**:
- It **transforms existing APIs** (OpenAPI, serverless functions) into MCP tools
- She manages the **Authentication** to each tool
- Filters tools **visible by each agent**
- It applies **access policies, quotas and audit** to each call

Examples: AgentCore Gateway, Google's Agent Gateway, open source agentgateway. Not to be confused with the [[81-litellm-api-layer|gateway LLM]], which is between the application and the **models**.

---

Why maintain a centralized register of agent tools? <!--anki:6f2a595b353e4852725a-->
?
A **registry** facilitates discovery, inventory and governance of agents or tools: owner, use, contract, version, risks and approval decision. Publishing an entry does not automatically grant execution rights.

Examples: **AWS Agent Registry**, Google Agent Registry, Agent 365 registry; the public MCP registry targets MCP servers and does not replace an internal review. These perimeters are not the same. Check for actually discovered content, synchronization, consumers, and removal. Pin a trusted reference, and then apply authorization to the call. An agent missing from the inventory or an obsolete entry must be detected.

---

Why is identity a key topic for agents? <!--anki:627564286c41662c6a68-->
?
An agent acts on **real resources**: identify the actor, the user possibly represented and the mandate allows to control each operation and to keep the proof.

Products such as Entra Agent ID or AgentCore Identity provide identity and access mechanisms; their presence does not guarantee that secrets remain out of context or that permissions are minimal. Configure Vault or Proxy, Audiences, Scopes, Duration and Revocation, and then test these borders. Successful authentication does not allow all tools or resources. Link the policy decision and the observed effect to the actual identity.

---

Do not confuse: delegated agent and autonomous agent? <!--anki:41734f3c442839645429-->
?
A **Delegated Agent** acts on behalf of a user in a limited mandate; its rights must remain an authorized subset for this task. A **Self-employed** uses its own identity, with defined permissions and responsible owner.

For example, a support agent can view only the records of its requester, while a nightly processing has a framed service access. In both cases, verify identity, purpose, expiration and rights before the effect. "Autonomous" does not mean without supervision, and "delegated" does not justify copying all the user's tokens.

---

What memory does an agent platform provide? <!--anki:484a632f5562363b4a5d-->
?
- **Short term**: the session or thread history, kept on the server side
- **Long term**: facts, preferences and summaries **automatically extracted** from conversations and found in subsequent sessions (e.g. AgentCore Memory, Google Memory Bank)
- **Stores shared** between agents, **split** by user or customer

See [[39-agent-memory|Memory of Agents]].

Example: A language preference can run through sessions, unlike a temporary access token. Set provenance, retention time, and deletion; test that a client change never recalls memories of the previous one.

---

What role does observability play in a platform? <!--anki:7751412e48372c7b3f42-->
?
**Track each step** of the agent (LLM calls, tools, decisions, approvals), measure costs and latency, and attach quality **scores**. Platforms emit traces **OpenTelemetry** (GenAI agreements), readable in Langfuse, Datadog, CloudWatch... ([[91-langfuse-observability|Langfuse]], [[93-monitoring-inference|monitoring]]).

A useful trace connects user demand to model calls and business effects, with a common identifier. It distinguishes between slow tool, repetitive loop and bad decision. Hide sensitive data and predict retention and sampling; a technically complete trace can be costly or unnecessarily expose the content of conversations.

---

When is an agent evaluated on a platform? <!--anki:4e706774217c234e5623-->
?
- **Before deployment**: task datasets and **simulation** (synthetic users, virtualized tools)
- **Continuous**: **scoring of a sample of production traces** by evaluators (often LLM-as-judge)

The evaluation before deployment is used to block regressions on known cases; the production one detects new uses and drifts. Add controls on the results of tools and business actions. A judge score alone remains insufficient: the human standard, incidents and success metrics must be able to contradict it.

---

What protocols make a platform interoperable? <!--anki:742e4e7131465e7c6163-->
?
- **MCP**: agent ↔ tools and data ([[33-mcp|MCP]]). From the spec **2026-07-28**, it is **stateless**: it passes behind a simple load balancer
- **A2A**: agent ↔ agent, between publishers ([[36-agent-orchestration|orchestration]]). Version **1.0** in March 2026 with signed **Agent Cards**
- **OpenTelemetry**: common trace format
- **AGENTS.md**: instructions for code agents

MCP, A2A, and AGENTS.md are hosted by the **Agentic AI Foundation** (Linux Foundation), which limits lock-in by a single publisher.

---

Build or buy for an agent platform? <!--anki:68367e4b62543e7d4623-->
?
- **Buy** (cloud platform or managed harness): fast production, managed security and scaling, but **lock-in** and products that change quickly
- **Build** (framework + Kubernetes + open source bricks): control and portability, but all the run is at your expense

In practice, often **hybrid**: buy runtime and sandboxes, keep **agent logic in code** and rely on open **standards**. Detailed criteria: [[115-agent-platforms-governance|Architecture & Governance]].

---

Why distinguish between request quota and work quota on an agent platform? <!--anki:6263646439376433336134343437623861306231313036366164383439303561-->
?
Two **requests** can mobilize very different resources: a short classification and a survey of 30 calls. A quota of requests alone therefore protects neither budget nor capacity.

Combine active session limits, tokens, tool calls and time, depending on the service. Reserve an envelope before expensive work and adjust actual consumption. Measure wait and rejects per team to prevent a tenant from monopolising workers. Ceilings must be applied by the platform, even if the model ignores budget guidelines.

---

How should an agent platform react to a failure in its control plan? <!--anki:6263653632663963643566343436646462336332633733383232383933383563-->
?
Separately define the fate of existing **executions and new admissions**. Some tasks may continue with a still valid local policy; others must wait for fresh permission.

Prevent an inaccessible registry from being interpreted as a universal permission. Provide policy validity, revocation, and degraded mode. Test out the failure with active and suspended agents: the availability of the runtime is not enough to ensure proper governance.

---

## Scenarios

Scenario: your agent prototype runs in a container with a API FastAPI. It must now serve 200 users, with tasks of 20 minutes. What breaks first? <!--anki:49552d657c4b4132623a-->
?
1. **The long requests** : one API Classic HTTP does not hold any tasks 20 minutes. We need the **asynchronous execution** and task tracking
2. **Status**: without checkpoints, a redeployment loses all current work ([[45-langgraph-production|checkpoints]])
3. **Insulation**: Sessions share the same process, so the code generated by one can affect the others
4. **Competitive messages**: a user who rewrites during work (double texting)
5. **The decision**: managed runtime, or build runtime, sandbox and recovery yourself ([[115-agent-platforms-governance|Architecture & Governance]])

**Trap**: Put a simple autoscaling in front, while the problem is the execution model.

---

Scenario: your management wants "an agent platform" in three months, and your company is already on Microsoft 365. Where do you start? <!--anki:69692f513c3f55756a61-->
?
1. **Tracking data and identity**: With Entra and Microsoft 365, the short path goes through Foundry to build and Agent 365 to govern
2. **Start with a measurable use case**, not the entire platform
3. **Poss the transverse bricks** from the first agent: identity, registry, tool gateway, traces
4. **Keep agent logic in code** versioned, to remain portable ([[115-agent-platforms-governance|lock-in]])
5. **Provide governance**: owner by agent, review before production, budgets

**Trap**: launch six agents in parallel without a common base, and have to resume everything at the first audit.

---

## Sources

- [AWS — Components in Bedrock AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html)
- [LangGraph — concepts and architecture](https://docs.langchain.com/oss/python/langgraph/overview)

Targeted review of 13 November 2026: affirmations specified in this pass; other content is not fully verified.

- [OpenAI — Agent Builder and Deadline Announced](https://developers.openai.com/api/docs/guides/agent-builder)
- [OpenAI — export and migration from Agent Builder](https://developers.openai.com/api/docs/guides/agent-builder/migrate-from-agent-builder)
- [Claude Platform — Hosted Service and Beta Status](https://platform.claude.com/docs/en/managed-agents/overview)
- [Claude Platform — fully self-hosted service, data and access](https://platform.claude.com/docs/en/managed-agents/self-hosted-data-and-access)
- [AWS — release notes, AWS Agent Registry](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/release-notes.html)

- [OpenAI — OpenClaw Enterprise, pilot phase control plan](https://developers.openai.com/blog/securing-persistent-agents-like-openclaw-at-openai) — the post distinguishes the driver from the 1.0 version lens.

## Connections
- [[37-agent-frameworks|Frameworks d'agents]] — the code that is deployed there
- [[115-agent-platforms-governance|— Agent Platforms Architecture & Governance]] — suite, senior level
- [[34-harness-plugins|Harness & plugins]] — Agent Loop and Sandbox
- [[33-mcp|MCP]] — tool protocol and server registry
- [[36-agent-orchestration|Orchestration multi-agents]] — what the runtime should support, A2A protocol
- [[39-agent-memory|Memorandum of agents]] — Memory Brick
- [[45-langgraph-production|LangGraph — Production]] — checkpoints, interruptions, deployment
- [[91-langfuse-observability|Langfuse]] — the observability brick
- [[93-monitoring-inference|Monitoring of inference]] — metrics and production alerts
- [[101-llm-security-guardrails|LLM Security]] — Identity and Permissions
- [[81-litellm-api-layer|LiteLLM]] — the gateway LLM
- [[83-gateway-ingress|Ingress]] — Network Input
- [[104-mcp-skills-security|Security of MCP & Skills]] — why a gateway and a tool registry
- [[103-agent-defenses|Defenses of agents]] — insulation, policies and least privilege
- [[122-finops-llm|FinOps LLM]] — allocate and drive AI spend
- [[165-computer-use-browser-agents|Computer use & browser agents]] — agents that use interfaces
- [[44-langgraph-fundamentals|LangGraph]] — state graphs for agents and workflows
- [[49-coding-agents|Code Agents]] — Use and Integrate Code Agents
- [[85-agentic-protocols-map|Map of protocols]] — which protocol to which agent boundary
- [[95-llm-as-judge|LLM-as-a-judge]] — note automatically, and validate the judge
- [[00-moc-ai-engineering|MOC AI Engineering]]
