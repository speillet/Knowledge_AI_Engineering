# — Agent Platforms Architecture & Governance — Flashcards
Tags: #flashcards #ai-engineering #agents #platform #governance #llm
Verified on: 25 September 2026 — global date preserved; targeted review of 13 November 2026 detailed in Sources.
<!-- summary: internal platform (paved road), control plane and execution planee, reference architecture, separation of the brain, hands and session, durable execution, multi-tenant isolation, exchange of tokens for the delegated agent, throws out of context, standards of identity, engine of policies, human-in-the-loop, register and life cycle, Top 10 OWASP agentic, impact radius and kill switch, Audit, SLO, continuous evals, costs, AI Act, lock-in, criteria of choice, revocation of an active delegation, political versions, verified withdrawal, business and operational responsibilities, Temporary derogations, Revocation of cache, exceptional access. -->


Why build an internal agent platform instead of letting each team get by? <!--anki:736971307067364a5850-->
?
Without a platform, each team reimplements runtime, identity, access to tools, observability and controls, each in its own way. The platform team provides a **paved road**: templates, approved tools, memory, authentication, traces and out-of-the-box evals. Product teams focus on business logic.

The platform is useful if it really reduces the delivery time and repeated errors. Start with the common needs observed, with clear contracts and responsibilities, and then measure adoption, incidents and operating costs. Too rigid a base can push the teams to bypass it; provide an extension procedure and exceptions drawn.

---

Why does Gartner plan to cancel many agent projects by the end of 2027, and what to take away from it? <!--anki:6233353432366564333864353439316662376461306137396636323031326531-->
?
**More than 40%**, for three reasons: derailing **costs**, fuzzy **business value** and insufficient **risk control**. These are the topics that an internal platform deals with from the start.

It is a **Forecast published**, not a measure of failures already observed or a probability applicable to each project. The point to remember is to demand a measurable value, a successful cost-per-task and a risk manager. A platform can help these controls, but its presence alone does not guarantee the success of a project.

---

Do not confuse: control plane and execution plane for an agent platform? <!--anki:4b303c326a415821624f-->
?
The **Control Plane** manages inventory, identities, policies, versions, and deployment decisions; the **Execution Plane** handles sessions, model calls, tools, memory, and traces.

These are responsibilities, not necessarily two products: an offer can cover both. At Microsoft, Foundry Agent Service provides execution and Agent 365 organizational governance of embedded or discovered agents. Agent 365 is commercially available from the 1 May 2026, with licensing and integration requirements. Do not infer visibility or automatic control over any unknown agent from the system.

---

What does the reference architecture of an agent platform look like? <!--anki:6a53783776536d3a607e-->
?
```text
Users, Apps, Other Agents (A2A)
        ↓
Agent gateway: authentication, routing, quotas
        ↓
Runtime: isolated sessions, harness (agent loop)
   ├─ Gateway LLM ──────→ models (routing, budgets)
   ├─ Gateway Tools ─→ MCP, API tools   ← Engine of Policies
   ├─ Sandbox ──────────→ code, browser
   └─ Memory ──────────→ session, long term
Transverse: identity, register, observation (OTel), evals
```
Each arrow is a **control point**: this is where you authenticate, filter, trace and limit.

Components can be grouped into a small system, but their responsibilities must remain explicit. Identity accompanies calls to tools and memory. For example, a conversation authorization is not worth authorization of reimbursement: the effective control is also done at the border of the business action.

---

In the architecture of Claude Managed Agents, what are the brain, hands and session? <!--anki:4b67397543574d597878-->
?
- **Brain**: the model and its harness, **without state**
- **Hands**: sandboxes and tools, **provided only when a tool needs them**
- **Session**: a **add-only event log**, stored outside the context window

This separation allows a calculation process to be recreated from a durable history, and to allocate a runtime environment only at the appropriate time. It does not make external effects reversible. If a business writing succeeds before a failure, the recovery must consult a proof of this writing or use an idempotency key.

---

What do you gain by separating an agent's brain, hands and session? <!--anki:422e7d317c6e3e4b662d-->
?
Separate **calculation, tool environment and durable history** allows to allocate and restore these components according to different cycles. A worker can start from a preserved state; a sandbox can be renewed without losing the whole file.

Latency and cost benefits depend on what is actually preheated, transferred, or rebuilt. Separation can make it easier to isolate secrets, but not automatically inaccessible: check mounts, proxies, and tool rights. An outage always requires idempotency or reconciliation. Gains measured by a vendor are not a boon for any architecture that uses these names.

---

How to make an agent that runs for hours reliable? <!--anki:6c415f6f4a3457375e3a-->
?
With the **Durable Execution** ([[41-code-nocode-automation|durable execution]]) :
- **Checkpoint at each stage**, resumed at the last point after a crash ([[45-langgraph-production|LangGraph]], Temporal)
- **Idempotence** of tool calls (idempotency key), so that a replay does not pay twice
- **Timeouts and withdrawals** with backoff
- **Compensation** (pattern saga) to undo an action when a next step fails
- **Long asynchronous operations**, followed by polling (extension **Tasks** of MCP)

---

How to isolate customers and teams on a shared platform? <!--anki:42344a3b424b56677953-->
?
- **Calculation**: one **microVM per session** (Firecracker) or gVisor or Kata, rather than containers that share the kernel
- **Data** : memory, files and indexes **Partitioned** by customer and user
- **Caches**: no sharing of the prefix cache between clients ([[66-prefix-caching-radix-attention|Auxiliary Channel]])
- **Secrets** specific to each client, **Outgoing network** limited to a whitelist
- **Quotas** per customer against noisy neighbor effect

---

How does a delegated agent get its rights without a service account? <!--anki:7859473c4b2c3479314d-->
?
A mechanism of **Exchange of tokens**, as OAuth Token Exchange, can be used to obtain a token for a specific audience and perimeter from an existing identity. The representation of the subject and actor depends on the profile and the authorization server.

The protocol does not automatically grant all user rights, nor does it automatically grant a correct reduction through the mere presence of two identities. Define audience, scopes, duration, and delegation rules; then control each action and keep the requester/agent link in the audit. A stand-alone agent uses a framed service identity, with a manager, with no implicit user mandate.

---

Where do the tokens of an agent live? <!--anki:4630305e382b7b6f4121-->
?
A privileged architecture keeps **credentials in a vault or tool proxy**, which authenticates the action and injects the secret at the last moment. The model receives a business result rather than the raw token.

Use minimal rights, limited time and appropriate revocation. Do not expose the secret in context, logs or files accessible to the agent when the architecture avoids it. This prevents some direct readings, but not the abuse of an authorized tool: an injection may still request a consultation or an improper sending. The proxy must verify identity, arguments and destination.

---

What standards are emerging for agent identity? <!--anki:6c754254776647366b4d-->
?
Distinguish **protocol, extension, draft standard and product**:
- **MCP Enterprise-Managed Authorization**: Stable extension, explicitly enabled; IdP centralizes policies via ID-JAG. Participant support remains required.
- **Customer ID Metadata Documents**, recommended in MCP 2026-07-28; dynamic recording is deprecated but retained for compatibility, with pre-registration possible.
- **SPIFFE**: Workload identity; **AIMS/WIMSE**, including `draft-ietf-wimse-aims-01`, remains an Internet-Draft, not a final RFC.
- **Enter Agent ID**: Agent identities and directory life cycle.

Identify review, support and effective policy. A certified identity does not, alone, allow a business action or a user delegation.

---

Why a deterministic policy engine in addition to prompt instructions? <!--anki:72532c345f666b242154-->
?
A prompt **is not a barrier**: an injection can bypass it. Policies are evaluated **out of the model**, by the gateway, **before each tool call**: what tool, what parameters, under what conditions (maximum amount, role of the user, schedules), with or without human approval. We start from a **default** and **each decision is logged**.

Languages: **Cedar** (AgentCore Policy, available since March 2026) or **OPA/Rego**. Complete content guardrails ([[101-llm-security-guardrails|LLM Security]]).

---

What does a Cedar policy look like for a support agent? <!--anki:4b7c5f4a345a5a6a366a-->
?
Example with **whole amount in cents**, identity and approval provided by a trusted context:
```text
permit (
  principal in Group::"agents-support",
  action == Action::"refund",
  resource is Order
) when {
  resource.owner == context.user &&
  context.amount_cents >= 0 &&
  (context.amount_cents <= 10000 ||
   context.approbation_humaine == true)
};
```
Without `permit` applicable, Cedar refuses; an applicable `forbid` overrides permissions. The schema must define these entities and attributes. Also validate the refundable balance and idempotency in the business department. **The agent does not itself provide its approval**: otherwise the policy would be deprecable.

---

How to organize human-in-the-loop on a large scale? <!--anki:65425e237c397e475a58-->
?
Classify actions according to **consequences, data, and actual reversibility**, then choose automation, deterministic control, and approval. Secret reading can be sensitive; reversible writing may have already disclosed information.

For an approval, show exact arguments and destination, identity, scope and expiration. Link the agreement to the versioned proposal and then recheck rights and preconditions before the effect. Measure load and review errors: multiply requests can reduce attention. Some actions do not become acceptable by a human click; prohibitions and business limits remain applied by the system, regardless of the choice of model.

---

What is in the agent register and what is their life cycle? <!--anki:4a405e614e7c51417737-->
?
**Agent topic**: owner, objective, models, tools and rights, accessible data, **risk level**, version, status.

**Life cycle**: → proposal security and risk review → publication → monitoring → **periodic certification** → withdrawal (identity disabled, tokens revoked).

We also inventory the **ghost agents**, created outside the circuit, and we **pin the versions** of the MCP servers and approved skills, because they are part of the supply chain.

---

Top 10 Agentic OWASP: what are lens hijacking and out-of-control agents? <!--anki:4826364a4d7941746038-->
?
Two risks of the edition **Top 10 for Agentic Applications 2026**, published on 9 December 2025:
- **Objective Misdirection** (ASI01): An injection causes the attacker's goals to continue. Reduce privileges and enforce policies outside of the model.
- **Out-of-control agents** (ASI10): a compromised or deviant agent continues to act. Monitor behaviour, identities, accepted tasks and means of stoppage.

Do not confuse this repository **ASI** with the Top 10 of LLM applications, whose 2026 edition has other identifiers. Associate the version of the repository with the scenarios and controls tested; neither its publication nor a completed checklist demonstrate the safety of the product.

---

Top 10 OWASP agentic: what are the misuse of tools and unexpected code execution? <!--anki:36517a694450415267-->
?
- **Disuse of tools** (ASI02): the agent uses a legitimate tool in a dangerous way (deletion, mass mailing). Parade: validation of arguments, quotas, approval of risky actions
- **Unexpected code execution** (ASI05): the agent generates and launches dangerous code or commands. Parade: isolated sandbox, without secrets, to the filtered network

The separation helps in diagnosis: an authorized API called on the wrong resource is the business authorization; a process launched out of containment is the execution control. Test the two borders, because a sandbox does not validate the arguments of a remote API.

---

Top 10 Agentic OWASP: what is identity abuse and insecure agent-to-agent communication? <!--anki:773b325725532a2d5d67-->
?
- **Identity and Privilege Abuse** (ASI03): The agent uses tokens or inherited rights beyond their need. Parade: User Rights, Short and Limited Tokens, Token Exchange
- **Inter-agent communication not secure** (ASI07): messages between agents spoofed, modified or replayed. Parade: mutual authentication, signed Agent Cards, exits of other agents treated as unreliable

---

Top 10 Agentic OWASP: what is supply chain and context poisoning? <!--anki:44333b24796c634c6648-->
?
- **Supply chain** (ASI04): tools, MCP servers, malicious or compromised plugins or skills. Parade: internal registry, pinned versions, pre-authorization analysis ([[104-mcp-skills-security|MCP & skills]])
- **Context and memory poisoning** (ASI06): falsified data retrieved or stored, which guides the following decisions Parade: provenance, writing policy, partitioning, purge

A pinned version guarantees an artifact identity, not its safety. Provide removal from the registry, revocation of access and search for executions that have consumed a compromised version; traceability makes this response possible.

---

Top 10 OWASP agent: what are cascading failures and human-agent trust abused? <!--anki:704d472e495a65307153-->
?
- **Cascade failures** (ASI08): An error or a false data spreads and is amplified from one agent or system to another. Parade: circuit breakers, validation between steps, limited impact radius
- **Human Trust-Abused Agent** (ASI09): The agent pushes the human to approve of a dangerous action, either by persuasion or misleading description.

See [[102-agent-threats|threats & incidents]].

---

How to limit the impact radius of a derailing agent? <!--anki:482d267241512f7a7832-->
?
Limit **rights, destinations and work allowed**, with call limits, duration, cost and concurrency. A narrow tool and a policy external to the model limit actions even if the instructions are diverted.

Stopping new requests, revoking credentials and blocking a route or tool. A kill switch does not automatically remove a message sent or an operation already accepted elsewhere. Test propagation delays, in-flight tasks and reconciliation after stopping. Counters and anomalies help trigger; the reduction of the impact radius must also be based on actual permissions and technical boundaries.

---

Which traces and which audit for compliance? <!--anki:74515d325a734c793226-->
?
Distinguish between **diagnosis trace** and **audit proof**: link identity, task, versions, policy decisions, approval, action and result, without unnecessarily copying sensitive data ([[93-monitoring-inference|monitoring]]).

Example: a span is called "called tool", but the audit log must be used to find the approved proposal and the identifier of the external operation.

Protecting the log from unauthorized changes, checking its coverage, and setting retention/deletion consistent with obligations. “Immutable” does not mean keeping all data forever. Testing the collector outage and providing a durable buffer or explicit refusal depending on the criticality.

---

Which metrics and which SLO for an agent? <!--anki:4b6c28432b555a68485f-->
?
- **Task Success Rate**, and **pass^k**: pass the k tests, a reliability measure ([[114-reproducibility-variance|Reproducibility]])
- **Steps and duration** per task
- **Cost per successful task**
- **Escalation rate** to a human
- **Policy Refusals** and **Tool Errors**

The SLO on the **End-to-end task** (success and duration) not only on the TTFT ([[64-inference-metrics-slo|Metric & SLO]]).

---

How to evaluate and improve an agent continuously? <!--anki:71255944386074307b6c-->
?
Organize a **controlled change loop**:
- Before deployment: representative cases, simulated tools, regressions and versioned promotion criteria.
- In production: traces, samples evaluated, coverage, returns and sufficiently mature business outputs.
- Optimization: analyze the causes, propose prompt or tool description, then validate the variant independently.

AgentCore documents recommendations, bundles, and A/B tests; Google introduces Agent Optimizer to suggest improvements from failures. Check each feature's availability, region, and prerequisites, rather than deducting its status from that of the entire platform. An automatic recommendation is neither a proof of win nor a promotion authorization.

---

How to control the cost of a fleet of agents? <!--anki:4a5a787e4c6044325e53-->
?
Four levers:
- **Assign** cost per agent, task and team, through identity and tags ([[122-finops-llm|FinOps]])
- **Budgets per run**
- **Stable prefix** for cache ([[123-aggressive-caching|caching]]) and **context compact**
- **Small models** for substeps ([[82-routing-llm|routing]])

The metric that decides: the **cost per successful task**, compared to the cost of the current process.

Include failed attempts and still-in-flight calls in the budget envelope. Segment costs by outcome: A drop in price per call may hide more spins or pick-ups.

---

What to prepare for the AI Act on an agent platform? <!--anki:764d316c7c5548246a50-->
?
- **Inventory** and **risk classification** of each agent: the platform registry serves as the basis
- **Human supervision** effective on risky actions
- **Journals** and **technical documentation**

Useful management framework: **ISO/IEC 42001**; schedule and obligations in the [[155-ai-act|AI Act]].

Qualification depends on the **finality of the system and the role of the organization**, not just the use of an agent. Link each use case to the managers, the available evidence and the obligations actually applicable. A register or a management certification does not alone demonstrate the compliance of each application; have the scope and deadlines validated.

---

How to limit lockout by a provider? <!--anki:754262562e752d547735-->
?
Identify when choosing a platform **what it costs to move**: logic, state, policies, events, data, observability and tool behavior. An open protocol facilitates an interface without making all internal checkpoints or formats portable.

Version contracts and keep a documented export path. Try a representative folder: rebuild its useful state and resume the path on another implementation. Measure work, lost data and necessary revalidation. Predict depreciation and retention of evidence. A gateway alone does not erase differences in models, authentication or functions specific to a service.

---

What criteria to choose your agent platform? <!--anki:7a642525262b4e577b43-->
?
Examine **ecosystem, data, compatibility and operation**:
- Integration with existing data, identities and tools.
- Location and retention of sessions, tracks, files, and model calls.
- Effectively supported agents and protocols.
- Ability of the team to operate and resume service.
- Cost per useful task and cost of output tested.

Example: The **Managed Agents hosted by Anthropic** is not eligible for ZDR, even with self-hosted sandboxes. In the fully self-hosted service, accessible on request, the organization retains sessions; model calls follow their vendor contract. Self-host the sandbox, service, or model represents three different perimeters.

---

Which agent platform architecture is most common? <!--anki:7a6664363e28693c4c29-->
?
Without **Population and Reference Measure**, It is not possible to establish the most frequent architecture here. A combination of managed services and internal controls is an option to evaluate, Not an adoption statistic.

It is possible to entrust computing or sandboxes to a service while keeping identity, policies and metadata under controlled contracts. Test event exchanges, state export, recovery and withdrawal before considering this combination as portable. Compare to the real need: autonomy of teams, data constraints, operational capacity and exit cost. The supposed popularity is neither a proof of compatibility nor a sufficient criterion of choice.

---

Why should an agent platform provide for the revocation of a delegation during an asset run? <!--anki:3535646463323738376438373436303061363636343138396164646562666265-->
?
A **long run** may retain a right that is no longer valid: user disabled, mandate removed, or policy changed.

Associating each effect with an identity and a mandate, using credentials of limited duration and rechecking the authorizations at sensitive borders. Provide suspension or stop of the concerned runs and invalidation of the tokens according to the identity mechanism. Test a revocation between two steps. A kill switch of the worker does not delete the operations already entrusted to an external service.

---

Why associate the policy version with evidence of an agentic release? <!--anki:3064616336353863643238663463323439656438646134643839386565396461-->
?
A **authorization policy** or a ceiling can change behavior without changing pattern or prompt. An evaluation made with free tools does not automatically validate the same task with additional approval or refusal.

Associate policy, execution identity, and environment to test reports. Verify what actions are allowed as prohibited, and then measure their effect on success and delay. An old version approval may need to be renewed depending on the change. The policy remains verified at the time of the action; tracing it does not allow for the indefinite retention of rights that have been revoked since the evaluation.

---

How to check that a retired agent can no longer accept work? <!--anki:3662353336306432303361333466643038663431383833386461393832656233-->
?
The **withdrawal** includes admission, identities, current tasks, and derived resources. Disabling only your page in a catalog can leave an endpoint, cron, or queue active.

Inventory these paths, stop new submissions, apply revocations and decide the fate of existing runs. Test a direct call and resume with old identifiers. Check external effects still uncertain, then keep or delete data according to their contract. Keep the evidence necessary for the audit without keeping the privileges. The administrative end of the project is not the technical proof of its effective stop.

---

Why distinguish between business owner and operating manager of an AI system? <!--anki:6336316664393635303835303435633038346437386638363966303863376666-->
?
The **business owner** sets the objective and the acceptable consequences; the **operating manager** maintains the service and coordinates the operational response. The same people can cumulate the roles, but their obligations must remain explicit.

Define who decides a degradation, authorizes a promotion, funds reliability and responds to a quality alert. Provide a replacement and access to the necessary evidence. A name in the registry is not enough if no one has the ability to stop the dangerous effect or arbitrate the return to service. Test this organization during a representative incident exercise.

---

How to frame a temporary exception to the standards of the AI platform? <!--anki:3539363066646263363437393432623139636438656564663530313131613430-->
?
An **exception** must identify need, perimeter, owner, compensatory controls, deadline and condition of exit. It allows a visible derogation rather than a forgotten parallel service.

Relate the decision to the release and test the guarantees actually retained: rights, data, traces and recovery. Expiry, explicitly reconsider or withdraw the use according to the policy; do not turn the silence into an extension. Measure the recurring exceptions: they can reveal an inappropriate base and motivate a common evolution. Automation can signal or apply the limits provided, without inventing an authorization that the managers have not given.

---

Why should authorization decision caches be part of an agent platform revocation plan? <!--anki:3837613630353336616237353432666561323838643962653331376138643235-->
?
An "authorized" decision held for too long may **survive the withdrawal of a right**. Workers and gateways may continue to accept actions on this basis.

Define the scope, duration and invalidation of the cache according to the risk. For sensitive writing, check the current conditions in the business department. Test a withdrawal during a long task. The correct central policy is not enough if its copies remain out of date.

---

## Scenarios

Scenario: your management wants "50 agents in production within a year". You have three today, each built in its own way. What do you propose? <!--anki:48635f77536c646d5f48-->
?
1. **Clarify expected business results** and measure baseline, beyond the number of agents.
2. **Establish a marked path** for identity, tools, execution, traces and assessments, based on the needs already observed.
3. **Name those responsible** for behaviour, operations and risk decisions.
4. **Deliver gradually** with cost-per-task, effects controls and rework tested.
5. **Review the value** before each extension; a sector forecast does not replace the proof of the project.

**Trap**: Present the Gartner forecast of cancellations by 2027 as an already observed rate or a probability attached to each agent, and then choose a platform on this single figure.

---

Scenario: an internal agent deleted data in a business tool last night. The manager asks what happened and who is responsible. What do you need to be able to produce? <!--anki:71514c53763e61336077-->
?
1. **The complete track**: which user, which agent, which entries, which actions, with which version
2. **Identity used**: delegated agent with user rights, or agent's own identity
3. **Policy decisions**: what has been authorized, by what rule, with or without approval
4. **Agent topic**: responsible owner, declared perimeter, level of risk
5. **Immediate measures**: kill switch, token revocation, correction of actions ([[105-agentic-ai-devsecops|Response to Incident]])

**Trap**: discover that the agent's actions are logged under a common service account, with no connection to the user.

---

Scenario: your agent platform provider announces that a service will be discontinued in six months. How do you assess the impact? <!--anki:432b3b67705d31754a72-->
?
1. **Inventory** what depends on it: agents, tools, memories, tracks, eval games
2. **Separate** what is portable (agent logic in code, MCP tools, OpenTelemetry traces) from what is proprietary
3. **Check the export** of data: memory, session logs, datasets
4. **Encrypt output cost**: rewrite, migration, revalidation by evals
5. **To draw a rule**: estimate this cost **before** to choose a platform, not at the time of the announcement

**Trap**: to have built business logic in a visual builder from which nothing is exported.

---

## Sources

- [Cedar — policy syntax](https://docs.cedarpolicy.com/policies/syntax-policy.html)

- [Anthropic — consumption observed in its multi-agent search system](https://www.anthropic.com/engineering/multi-agent-research-system)

- [AWS — Components in Bedrock AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html)
- [NIST — AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)

- [RFC 8693 — OAuth 2.0 Token Exchange](https://www.rfc-editor.org/rfc/rfc8693.html) — subject, actor and policy of issuing tokens.
- [Gartner, June 25, 2025 — cancellation forecast for end of 2027](https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027) — forecast, not previously observed rate.

Targeted review of 13 November 2026: products, identity, retention and repositories.

- [Microsoft Learn Agent 365, Availability and Prerequisites](https://learn.microsoft.com/en-us/microsoft-agent-365/overview)
- [MCP 2026-07-28 — Customer Registration](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/client-registration) — deprecated dynamic mechanism, retained for compatibility.
- [MCP — extension Enterprise-Managed Authorization](https://modelcontextprotocol.io/extensions/auth/enterprise-managed-authorization) — explicit support and flow ID-JAG.
- [IETF — AIMS, draft-ietf-wimse-aims-01 of 2 November 2026](https://datatracker.ietf.org/doc/html/draft-ietf-wimse-aims-01) — working document, not final RFC.
- [Microsoft Learn — Identities Enter Agent ID](https://learn.microsoft.com/en-us/entra/agent-id/agent-identities)
- [Anthropic — brain, tool and session separation](https://www.anthropic.com/research/managed-agents)
- [Claude Platform — Managed Agents Hosted and Retention](https://platform.claude.com/docs/en/managed-agents/overview)
- [Claude Platform — data and fully self-hosted service access](https://platform.claude.com/docs/en/managed-agents/self-hosted-data-and-access) — on-demand access; separate from only self-hosted sandboxes.
- [AWS — Release Notes AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/release-notes.html) — feature availability, distinguishable from historical preview announcements.
- [AWS — recommendations, bundles and A/B tests](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/optimization.html)
- [Google Cloud — Agent Platform and Agent Optimizer](https://cloud.google.com/blog/products/ai-machine-learning/introducing-gemini-enterprise-agent-platform/)
- [OWASP — Top 10 agentic 2026, published on 9 December 2025](https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/)

## Connections
- [[38-agent-platforms|Agent Platforms — Fundamentals]] — bricks and offers
- [[36-agent-orchestration|Orchestration multi-agents]] — A2A and multi-agent cost
- [[33-mcp|MCP]] — authorization, gateway and tool registry
- [[101-llm-security-guardrails|LLM Security & Guardrails]] — injection, excessive agency, guardrails
- [[112-model-cicd|CI/CD models]] — eval gate, canary, rollback
- [[113-monitoring-drift-feedback|Monitoring, drift & feedback]] — Quality in production
- [[93-monitoring-inference|Monitoring of inference]] — metrics, traces and alerts
- [[122-finops-llm|FinOps LLM]] — attribution and budgets
- [[45-langgraph-production|LangGraph — Production]] — Durable Execution and Interruptions
- [[111-mlops-llmops-fundamentals|MLOps & LLMOps]] — registry, lineage, environments
- [[103-agent-defenses|Security agents — Defensive architecture]] — security checks in detail
- [[105-agentic-ai-devsecops|DevSecOps for Agentic AI]] — incident detection and response
- [[155-ai-act|AI Act]] — risk classification and schedule
- [[85-agentic-protocols-map|Map of protocols]] — Open Platform Standards
- [[147-ai-technical-leadership|Technical Leadership]] — team standards and decisions
- [[35-context-engineering|Context engineering]] — what the agent has in front of his eyes at each turn
- [[44-langgraph-fundamentals|LangGraph]] — state graphs for agents and workflows
- [[84-streaming-application-integration|Streaming & integration]] — SSE, cancellation and long tasks
- [[95-llm-as-judge|LLM-as-a-judge]] — note automatically, and validate the judge
- [[140-010-transactions-outbox-sagas|Transactions, outbox & sagas]] — implement compensation and validation of actions
- [[00-moc-ai-engineering|MOC AI Engineering]]
