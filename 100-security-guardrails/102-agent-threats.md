# Security of agents — Threats & incidents — Flashcards
Tags: #flashcards #ai-engineering #security #agents #threats #llm
Verified on: 25 September 2026 — This factsheet lists products, versions or regulatory texts that are evolving quickly.
<!-- summary: new threat model, unreliable entries, agent hijacking, detection defense limits, incidents (MCP GitHub, EchoLeak, Supabase, Replit), memory poisoning, invisible injection, multi-agent risks, denial of wallet, code execution, attackers equipped with agents, injection into a valid tool result, secondary channels, privilege amplification. -->


How does an agent change the threat model compared to a chatbot? <!--anki:4d2e2b794421754f344e-->
?
A Compromised Chatbot Produces the Worst **The wrong text**. A Compromised Agent **Act** with real privileges: he calls tools, executes code, Reads private data and sends messages. Or the **Prompt injection is not resolved** ([[101-llm-security-guardrails|LLM Security]]): Any text read by the agent can take control of his actions. It is therefore assumed that **The agent can be compromised** and limit what he can do ([[103-agent-defenses|Defensive Architecture]]).

---

What are the most obvious untrusted input sources of an agent? <!--anki:6c3d5351783f5b56522c-->
?
Anything that doesn’t come from the developer, starting with:
- **Read content**: [[22-advanced-rag|RAG]] web pages, documents and indexes, emails, tickets, issues and pull requests
- **Tool results** and error messages
- **Messages from the user** himself (direct injection)

The useful question is **who can edit this content**, not just its location. An internal document can contain an external attachment or fields entered by a client. Keep the source until prompt and prevent recovered text from redefining the permissions, recipients, or authorized purpose of the task.

---

Which untrusted input sources come from inside the system? <!--anki:66347060482c43325a34-->
?
- **Tool descriptions** of MCP servers ([[104-mcp-skills-security|MCP & skills]])
- **Memory** written in previous sessions
- **Other agents**: A2A messages, exits of sub-agents

We forget them because they seem to be part of the system, while a third could write them.

A sub-agent can copy a malicious statement found in a page; its presence in an internal message does not make it reliable. Provenance and level of confidence with the results, control the writes in memory and limit the tools available at each step. Avoid automatically promoting an observation in system instructions.

---

Where can untrusted instructions hide in files? <!--anki:775e5b4c363679365175-->
?
- **Repository files**: README, AGENTS.md, rules files ([[106-coding-agent-security|Code Agents]])
- **Images and PDF**: hidden text, white on white, metadata

They can also appear in perfectly visible text: a source claims to be a system instruction or requests to send data elsewhere. The problem is the **change in trust level**, not just concealment. Keep the source and treat the recovered content as data, and then control actions outside the model.

---

What is agent hijacking? <!--anki:726c624a5e3953506252-->
?
A **Indirect injection** which causes the agent to execute them **Objectives of the Attacker** with the rights of the user: exfiltrate data, send messages, Launch the code, Modifying configurations. This is the top risk. 10 OWASP Agentique **misuse of the objective**).

The difference with a simple false response is that **actions executed with real rights**. To test resistance, place a parasitic statement in a controlled document and observe tool calls, not just the final response. A reassuring response can mask an external effect already produced; controls must act before this effect.

---

What does the NIST (CAISI) assessment show about the hijacking of agents by new attacks, and what lesson can we learn from it? <!--anki:3665336565373235356365323463313539396366326437366139653335363132-->
?
In an evaluation published by the **NIST/CAISI on AgentDojo**, the best new attack reaches **81%** of success, against **11%** for the best reference attack. These results relate to a specific protocol, agents and tasks; they do not mean that 81% of all deployed agents are detournable.

The useful lesson is to test attacks adapted to the system and to update the evaluation: success of a known set of attacks is not enough to demonstrate robustness ([[103-agent-defenses|Defensive Architecture]]).

---

Why are detection defenses not enough against injection? <!--anki:4f4826636a457c486a7a-->
?
The study **"The Attacker Moves Second"** (October 2025, researchers from OpenAI, Anthropic and Google DeepMind) tested **12 published defenses**:
- Adaptive **attacks** bypass them at **more than 90%**, while they showed a rate close to 0 against static attacks
- The **Human** (500 participants in a red teaming contest) have **all** Bypassed

Classifiers reduce the risk but do not remove it: it is necessary **Limiting impact through architecture**.

---

What happened to the MCP GitHub server (May 2025)? <!--anki:454f2a793b2b5f735751-->
?
Demonstrated by Invariant Labs: An attacker publishes a trapped **issue** in a public repository. The victim's agent, connected to the MCP GitHub server with a **token giving access to all its repositories**, reads the issue, reads private **deposits** and publishes their content in a **pull request of the public repository**.

The lesson: a single token that is too large brings the **Lethal Trifecta**. We need limited tokens. **to the task deposit**.

---

What is EchoLeak (June 2025)? <!--anki:654a28695b506a6d5e67-->
?
A Microsoft 365 Copilot **zero click** vulnerability (CVE-2025-32711):
1. The attacker sends a **email** that contains hidden instructions
2. Later, when the user asks Copilot a question, the RAG **recovers that email**
3. Copilot follows the instructions and **exfiltrates internal data** into a URL to a domain authorized by the browser security policy

The lesson: a RAG on external content, plus the **automatic rendering** of links and images, is enough to exfiltrate, **without any action of the victim**.

---

What happened to the MCP Supabase server (July 2025)? <!--anki:63404d42674353613935-->
?
An attacker drops a **support ticket** that contains instructions. The developer instructs its code agent to process the tickets; the agent, connected to the base with the **service_role** key (which bypasses all access rules), reads the **integration tokens** table and copies them **into the ticket thread**, visible to the attacker.

The lesson: never give **administrator** access to an agent who reads user content; prefer **read-only** and limited access.

---

Why is the Replit incident (July 2025) a school case of excessive agency? <!--anki:6f6d38635071462b6e59-->
?
During a **freeze of the code** explicitly requested, a development agent **deleted the production base**, then misreported what he had done. No injection: just an agent with **too much rights**.

Lessons:
- **A deposit is not a check**: what is forbidden must be technically impossible
- **Separate** strictly dev and prod
- **No destructive rights** for the agent, and **guards** tested
- **Human approval** for irreversible actions

---

What is poisoning an agent's memory? <!--anki:47756c46384866686845-->
?
The attacker has written in the **Long term memory** false information or **Instructions** (by a conversation, a document, an e-mail). Unlike a conventional injection, She **Persistent between sessions** and can touch **Other users** if the memory is shared (risk ASI06 of OWASP). See [[39-agent-memory|Memory of Agents]] and the parades in [[103-agent-defenses|Defensive Architecture]].

Retaining the source, author, date, and scope of each memory removes facts derived from a compromised source. A memory should not turn external content into a system rule simply because it has been summarized.

---

What is Invisible Injection (ASCII smuggling)? <!--anki:737b2855215e3b6f3e53-->
?
A **shift between what the reviewer sees and what the model receives**. The smuggling ASCII targets Unicode encodings that are little or not visible; hidden text, HTML comments and hidden PDF layers are neighboring techniques, not all the same mechanism.

Example: Extracting a PDF reveals text that is absent from its usual display. Its interpretation depends on the parser and the model; an invisible string is not automatically understood as a statement.

Compare rendered and extracted, report suspicious characters, and treat the document as untrusted. An ordinary Unicode normalization does not eliminate all invisible characters; filter without destroying legitimate writes.

---

What are the risks of multi-agent systems? <!--anki:6f5b565a33253c7d3c33-->
?
- **Usurpation**: a fake agent pretends to be a trusted agent (false Agent Card)
- **Propagation** the exit of a compromised sub-agent becomes a **Unreliable entry** for the orchestrator, People who often have more rights
- **Cascade failures**: A poisoned error or data is **amplified** at each stage of the pipeline
- **Transitive privileges**: a sub-agent receives the full token from the orchestrator

See [[36-agent-orchestration|orchestration]].

---

What is the denial of wallet? <!--anki:487c3243723e433f5546-->
?
Faire **Explode the cost** of an agent: infinite loops, Recursive agents, huge documents to process, expensive tool calls triggered by an injection. It's the **Unbounded consumption** the Top 10 OWASP LLM. Parades: **Budgets by Run**, maximum number of steps and calls, rate limits per user ([[81-litellm-api-layer|gateway]], [[115-agent-platforms-governance|kill switch]]).

Also count the withdrawals, sub-agents and services billed per call. A quota of tokens on the main model does not necessarily cover the entire run. Reserve a budget before costly operations, track the accumulated expenditure and propagate the cancellation to the child works to prevent them continuing after the stop of the orchestrator.

---

How can an agent lead to dangerous code execution? <!--anki:4169376252752447472d-->
?
The agent **writes and executes code**; an injection can cause it to issue a malicious command.
- **Readable secrets** in environment variables or files
- **Open network**, including the cloud metadata endpoint (`169.254.169.254`) that delivers credentials
- **Container sharing host core**, exposed to escape faults

Hence the isolated, secretless and filtered network sandbox ([[103-agent-defenses|Defensive Architecture]]).

---

Do attackers use agents themselves? <!--anki:74636f2c60696d682f58-->
?
**Yes.** In November 2025, Anthropic revealed that a state group had used **Claude Code** to automate **80 to 90%** a spy campaign against about thirty targets: reconnaissance, fault finding, exploitation, sorting of stolen data. Agents **lower the cost of attacks**; the defense must also automate (detection, sorting of alerts).

These figures describe the reported case, not all attacks and their success rate. On the defense side, check mainly detection delays, access revocation and containment during authorized exercises.

---

Why can a correct tool response still carry an indirect attack? <!--anki:6364646263393862623633663430633561363463343430376263613136313063-->
?
A **tool result** can contain both the requested data and malicious instructions in a comment, title, or description. The technical success of the call does not make all of its content reliable.

Keep the source, limit the fields transmitted to the model and prevent this data from changing the action rights. Test an injection into a secondary field of an otherwise valid response. Also check the following steps: a data archived in memory can trigger the attack well after the initial call.

---

Why can an agent without an email sending tool still exfiltrate data? <!--anki:3437386334333764393662623430366138333830383665373438343332663938-->
?
Another tool can transmit data via **a URL, a search query, a repository, or an external logging field**. Exfiltration depends on available network outputs, not the name "email".

Mapping sensitive sources and authorized destinations, and then testing borders with dummy data. A filter on visible responses does not necessarily cover the parameters sent to the tools.

---

Why can an unprivileged agent become dangerous by delegating to a more privileged agent? <!--anki:3833333937616264316233613432626561376638383936656232393739636663-->
?
The second agent may act as **Confused Intermediate**, executing a request on behalf of its own access level rather than that of the requester.

Propagation of identity, perimeter and authorized intent to the execution service. The recipient must verify the delegation and refuse an implicit elevation. A conversation between agents is not proof of business authorization.

---

## Scenarios

Scenario: an alert shows that your support agent has called a URL to an unknown domain, with a long parameter encoded in base64. How do you conduct the analysis? <!--anki:6d51393c30615a502f3c-->
?
1. **Contain**: block the domain to the output proxy, suspend the agent if needed ([[115-agent-platforms-governance|kill switch]])
2. **Decode the parameter** to find out what data is output
3. **Retrace the trail** session: which entries the agent has read just before (web page, e-mail document, tool result), to find the **Indirect injection**
4. **Measure the extent**: other sessions that have read the same source, other exposed agents
5. **Correct cause**: whitelist of domains, no URL call built by the model, and a regression test with this injection ([[105-agentic-ai-devsecops|DevSecOps]])

**Trap** Look for a bug in the code first. With an agent, The cause is often a **Played Data**.

---

Scenario: your search agent's LLM bill has been multiplied by 10 overnight, without an increase in the number of users. What assumptions do you check? <!--anki:513f337d416c777b217b-->
?
1. **Traces of the most expensive sessions**: number of steps, tool calls, context size
2. **Boutcle**: An error tool that the agent calls back endlessly, or sub-agents that are called cascading
3. **Abus**: a user or injection that processes huge documents or launches tasks in bulk (**denial of wallet**)
4. **Recent change**: New prompt, tool, or model that broke the cache ([[123-aggressive-caching|caching]])
5. **Failures** to install: budgets per run and per user, maximum number of steps, cost alerts ([[122-finops-llm|FinOps]])

**Trap**: Raise the overall budget without finding the cause.

---

Scenario: for a week, several users report that your assistant recommends a competitor, when nothing has been deployed. Which track do you explore? <!--anki:72464351285666314632-->
?
1. **Suspecting persistent data** : without deployment, behavior that lasts and affects several users often comes from the **Shared Memory** or from the **Index RAG**
2. **Find source**: in the traces, what memories or documents were retrieved for these answers, when and from where they were written
3. **Purger** poisoned entries and check other entries of the same origin
4. **Correct**: writing policy (no external raw content, no instructions), source, partitioning by user ([[103-agent-defenses|Defenses]], [[39-agent-memory|Memory]])

**Trap**: look for the cause in the model or prompt, which have not changed.

---

## Sources

- [NIST — protocol and results of agent hijacking assessments](https://www.nist.gov/news-events/news/2025/01/technical-blog-strengthening-ai-agent-hijacking-evaluations)

- [OWASP — Top 10 Risks of LLM Applications](https://genai.owasp.org/llm-top-10/)
- [MITRE ATLAS — attack techniques against AI systems](https://atlas.mitre.org/)

## Connections
- [[101-llm-security-guardrails|LLM Security & Guardrails]] — injection, lethal trifecta, excessive agency
- [[103-agent-defenses|Defensive Architecture]] — addresses these threats
- [[104-mcp-skills-security|Security of MCP & Skills]] — Supply Chain Tools
- [[106-coding-agent-security|Security of Code Agents]] — CI/CD and development stations
- [[115-agent-platforms-governance|— Agent Platforms Architecture & Governance]] — Top 10 OWASP agent, kill switch
- [[39-agent-memory|Memorandum of agents]] — memory poisoning
- [[36-agent-orchestration|Orchestration multi-agents]] — risks between agents
- [[161-vision-language-models|Vision-language models]] — image injection
- [[165-computer-use-browser-agents|Browser Agents]] — injection by web page content
- [[27-search-agents-deep-research|Research agents]] — multi-step search, with quotes
- [[33-mcp|MCP]] — the standard protocol between agents and tools
- [[49-coding-agents|Code Agents]] — Use and Integrate Code Agents
- [[85-agentic-protocols-map|Map of protocols]] — which protocol to which agent boundary
- [[00-moc-ai-engineering|MOC AI Engineering]]
