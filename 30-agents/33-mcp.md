# MCP — Model Context Protocol — Flashcards
Tags: #flashcards #ai-engineering #agents #mcp #llm
Verified on: 25 September 2026 — This factsheet lists products, versions or regulatory texts that are evolving quickly.
<!-- summary: M×N problem, host, client and server, tools, resources and prompts, stdio and HTTP transport, 2026-07-28 stateless spec, MCP or API REST server, risks, interoperability and historical compatibility tests, protocol and business errors, server identity. -->


What is MCP? <!--anki:516d532139606b765240-->
?
The **Model Context Protocol**: an open **standard** (initiated by Anthropic, hosted since December 2025 by the **Agentic AI Foundation** of the Linux Foundation) to connect AI applications to tools and data sources via a client-server architecture.

For example, multiple wizards can use the same document server without each re-implementing their own business API. MCP normalizes exchanges and ability discovery; the **host** retains the decision to expose and call these capabilities. Protocol compatibility does not guarantee server reliability or permission to access all of its data.

---

What problem does MCP solve? <!--anki:6c3b47315f4c6e566d3b-->
?
Problem **M×N**: Without standard, each app must integrate each tool; with MCP, an app speaks to **any MCP** — server hence the image of "**USB-C of AI** apps".

In particular, the protocol standardizes the discovery and invocation of capabilities, which reduces specific adapters. Interoperability remains subject to transport, versions and functionalities supported on both sides. Authentication, permissions and semantics of tools must be configured: a successful connection does not make all servers interchangeable.

---

What is the architecture of MCP? <!--anki:505935676943515d3e6b-->
?
- **Host** : l'application IA (IDE, chat, agent)
- **Client**: the connection managed by the host, **one per server**
- **MCP server**: exposes tools and data
```text
Host (Claude Code, Cursor, ton agent)
 ├─ client ──→ MCP GitHub server (tools: issues, PR)
 ├─ client ──→ MCP Postgres server (tools: read requests)
 └─ client ──→ internal MCP server (tools: in-house CRM)
```
The **model never speaks directly** to a server: it is the host that lists the tools, presents them to the model, executes the call and returns the result ([[32-tool-calling|tool calling]]).

The host remains responsible for the user agreement and the perimeter of the connections. Connecting two servers does not implicitly allow to transfer data from one to the other.

---

What are the three primitives exposed by a MCP server? <!--anki:7334672d62745828472a-->
?
- **Tools**: Summonable actions **by the model** (he decides)
- **Resources**: searchable data or documents, chosen **by the application or user**
- **Prompts**: Reusable templates, triggered **by the user** (often commands)

The distinction is about **Who decides** to use it: the model, the application, or the human. Recent extensions add **Tasks** (long operations tracked by polling) and the **Apps** (HTML interface rendered in a sandbox).

Example: an internal guide is a resource, "analyze an incident" a prompt template, and check its ticket a tool. This distinction never replaces server-side authorization.

---

What transports does MCP exist? <!--anki:683c4f6b67296425664d-->
?
- **stdio**: local server launched as a subprocess
- **HTTP streamable**: remote server

Since spec **2026-07-28**, the protocol is **no state** (no more session or handshake): a remote server passes behind a simple load balancer. The old HTTP+SSE transport is deprecated.

Transport mainly determines **where the server is running and how to reach it**. With stdio, master the launched binary, its environment and local access; with HTTP, manage identity, network and delays. Set the version of the protocol and check its compatibility on the client and server side: the session guarantees are not deduced from the single word HTTP.

---

Do not confuse: MCP and API REST server? <!--anki:6a476f7b5b3434754e73-->
?
- **API REST**: a contract designed for **developers**, who read the doc and write the call code
- **MCP server**: a contract designed for a **model**, which **discovers** the execution tools, resources and prompts, described in natural language with their JSON Schema

A MCP **server often wraps** a API REST: it chooses which operations to expose, renames and describes them for the model. Exposing them as 200 REST endpoints results in a bad MCP server. The link to the model remains as **[[32-tool-calling|tool calling]]**.

---

Is a MCP server linked to a particular model? <!--anki:6b6f7e2628343e304b4f-->
?
**No.** The server exposes capabilities via MCP; the host makes them accessible to the model and organizes exchanges. Changing the model does not require, in principle, to rewrite the connector.

But **protocol compatibility and quality of use are distinct**. Example: two hosts access the same ticket tool; one exploits its associated resources, the other only its tools. Transport, authentication and supported capabilities must also match. Test discovery, call and error handling with each host; a reachable server does not guarantee all its features or a good choice of tool by the model.

---

What security risks does MCP introduce? <!--anki:6b5735663b3e5b48284d-->
?
**Unaudited third-party servers, [[101-llm-security-guardrails|prompt injection]] via results and tool descriptions, permissions too wide** — from where sandboxing and human validation of sensitive actions. Detail of attacks (tool poisoning, rug pull...): [[104-mcp-skills-security|Security of MCP & Skills]].

A tool description may claim to send a secret to complete the task; it remains a third-party data, not an authorization. Limit network tokens and outputs, filter access per user, and log actions. Human validation must show the actual destination and arguments to allow for useful control.

---

How does a MCP host declare a local server and a remote server? <!--anki:3861633963323633363765663437353461356231323532633438386235333338-->
?
A **local** server is a process initiated by the host; a **distant** server is joined by its URL and authentication mechanism. Illustrative example for a host accepting this convention:
```json
{
  "mcpServers": {
    "crm-local": { "command": "/opt/mcp/crm/1.4.0/bin/mcp-crm", "args": ["--stdio"] },
    "crm-distant": { "url": "https://mcp.example.org/crm" }
  }
}
```
The path is fictitious and versioned; adapt the format to the host and provide the secrets through its secure mechanism. MCP does not universally impose these configuration keys. Check binary origin, local rights, transport and supported version before login; pin a component does not attest to its safety.

---

Why is declaring a MCP capability not enough to prove its interoperability? <!--anki:3566646134346631633966373436396262326430383834633532326234373666-->
?
An announced **capacity** describes what a participant claims to support. It is still necessary to check version, transport, authentication and actual behavior with the selected host.

Build a contract test: discovery, valid call, business error, large result and denial of access. Also test an absent ability to check for expected degradation. In the 2026-07-28 review, version and capabilities accompany queries; historical clients may require an adaptation. Fix the tested review instead of inferring compatibility of the MCP name alone.

---

Do not confuse: MCP protocol error and business failure of a tool? <!--anki:6336323733623162363238613435343161353064646531613531363534333030-->
?
A **protocol error** indicates that the exchange itself is invalid or impossible; a **business failure** may be a correctly received response indicating that the operation was refused or failed.

The host must preserve this distinction in what it shows the model and in its metrics. A successful transport does not prove the success of the action. Define the recoveries according to the nature of the error and check the exact contract of the MCP version used.

---

Why are two MCP servers exposing a tool of the same name not interchangeable? <!--anki:3161383261393963646661373463656161373837353732636534386138353233-->
?
The name does not determine **operator identity, permissions, or semantics** of the action. Two `search` tools can explore different corpora and supports.

Link the selection to an authenticated server, its approved configuration, and its contract. Test the results and effects during a replacement. A dynamically retrieved tool description is data to be examined; it should not grant new permissions to the server that provides it.

---

## Scenarios

Scenario: Each team integrates the internal API into its agents in its own way, and the same Jira connector exists in four versions. What do you propose? <!--anki:436d2a2b63586a323e77-->
?
1. **One MCP server per system**: published once, reusable by all hosts, regardless of model
2. **Internal registry**: discovery, owner, pinned version, approval circuit ([[38-agent-platforms|Platforms]])
3. **Gateway MCP** in front of servers: authentication, whitelist of tools per agent, quotas, audit
4. **Conventions**: naming of tools, carefully written descriptions, strict diagrams
5. **Security**: pre-publication review, pinned versions, change of description monitoring ([[104-mcp-skills-security|MCP Security]])

**Trap**: Let each developer workstation set up its own MCP servers, without inventory or control.

---

Scenario: your internal MCP server, written before spec 2026-07-28, keeps the status of requests in memory per session. Switching to three replicas breaks everything. What do you do? <!--anki:7a3f694b376861363352-->
?
1. **Understanding**: the recent spec renders the protocol **stateless**, precisely to allow multiple replicas behind a load balancer
2. **Exit process memory state**: The server issues an opaque **handle** that the client returns as an argument, and the state lives in shared storage
3. **Link the handle to the authenticated server-side user**: holding it is not enough to access it ([[104-mcp-skills-security|MCP Security]])
4. **Migrate transport**: Abandon old HTTP+SSE, deprecated
5. **Tester** with multiple replicas and a simple load balancer, without session affinity

**Trap**: Bypass the problem with sticky sessions, which push back the debt and break the next reboot.

---

## Sources

- [MCP — Specification 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28)
- [MCP — Best Safety Practices, Edition 2026-07-28](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices)

- [MCP 2026-07-28 — version and compatibility](https://modelcontextprotocol.io/specification/2026-07-28/basic/versioning) — targeted deepening of the 12 November 2026; educational examples are built for this review.

- 14 November 2026 — MCP Identity and Trusted Boundaries: [MCP — Security Practices 2026-07-28](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices).

## Connections
- [[32-tool-calling|Tool calling]] — the underlying mechanism
- [[34-harness-plugins|Harness & plugins]] — the host that integrates MCP
- [[38-agent-platforms|Platforms of agents]] — server registry MCP
- [[37-agent-frameworks|Frameworks d'agents]] — ADK & A2A side interop
- [[115-agent-platforms-governance|— Agent Platforms Architecture & Governance]] — Business Authorization and Tool Gateway
- [[104-mcp-skills-security|Security of MCP & Skills]] — attacks specific to MCP and spec rules
- [[85-agentic-protocols-map|Map of protocols]] — MCP from A2A, AG-UI and others
- [[103-agent-defenses|Defenses of agents]] — insulation, policies and least privilege
- [[165-computer-use-browser-agents|Computer use & browser agents]] — agents that use interfaces
- [[24-cognee|Cognee]] — an agent memory in knowledge graph
- [[84-streaming-application-integration|Streaming & integration]] — SSE, cancellation and long tasks
- [[102-agent-threats|Threats to agents]] — real attacks and incidents
- [[105-agentic-ai-devsecops|DevSecOps IA]] — security checks in the delivery cycle
- [[106-coding-agent-security|Security of Code Agents]] — risks specific to code agents
- [[81-litellm-api-layer|LiteLLM]] — the gateway between applications and models
- [[00-moc-ai-engineering|MOC AI Engineering]]
