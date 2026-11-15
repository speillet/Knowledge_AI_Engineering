# Harness & plugins — Flashcards
Tags: #flashcards #ai-engineering #agents #harness #llm
Verified on: 17 October 2026 — behavior of Claude Code hooks confronted with official documentation.
<!-- summary: Harness role, plugins, skills, hooks, permissions, sandbox, memory files, negative policy tests, working directory, ability tests. -->


What is the Harness of an Agent? <!--anki:7976774a57665d6f6958-->
?
The **program that surrounds the model**: it rotates the loop, **runs the tools**, manages the context, applies the permissions and displays the result. The model proposes, **harness has**.

It turns a prediction of the model into a controlled execution: a tool call becomes an authorized operation, traced and limited in time. If the tool fails, it transmits an actionable observation or stops the run. Two applications using the same model can therefore have very different behaviors depending on their harness.

---

What are the responsibilities of a harness? <!--anki:73483b4938322d2e4366-->
?
- **Agent loop** and stop conditions
- **Execution** of [[32-tool-calling|Calling tools]] and return of results
- **Context Management**: system prompt, history, compaction
- **Permissions**, sandboxing, approbations
- **Integrations**: [[33-mcp|MCP]], plugins, hooks

These responsibilities are the **effective control of execution**. For example, a payment tool must be blocked by the program as long as the required authorization is missing, even if the model requests its launch. Traces link decision, arguments, result and error to allow audit and recovery.

---

Why is it said that harness counts as much as the model? <!--anki:4976284543642a78436b-->
?
As an equal model, the **quality of the tools, the context provided and the loop** radically changes the results: a code agent depends as much on its search and editing tools as on the LLM.

A model may know how to fix a bug and fail if the search fails to find the correct file, if the tool truncates the error, or if the edit breaks the format. Harness also decides on the context, times, and limits. To compare two models, fix these items; otherwise, multiple changes are measured at once.

---

Ready-to-use Harness or Harness built with an SDK: when to choose each? <!--anki:6363323232356361663464393438333438616337616636336438343536663533-->
?
- **Ready to use** (Claude Code, Cursor, Codex CLI, Help): to **code** with an agent; we adapt it by memory files, skills, hooks and permissions
- **Built with an SDK** (Claude Agent SDK, OpenAI Agents SDK): for **Integrate** the agent loop in its product, with its own tools and rules

The SDK provides bricks, not the business contract. For customer support, verify that it allows identity by request, budget stop and recovery after failure. A ready-to-use code tool can be enough for an internal task, without becoming the runtime of the product.

---

What is a plugin in a harness? <!--anki:21632f592e76504753-->
?
A **package of extensions** installed in the host: commands, skills, subagents, hooks or MCP servers depending on the product. Not all of these components are required.

Example: A ticket review plugin can combine an input command, a diagnostic procedure, and a connector to the ticket manager. The procedure describes what to do; the connector provides actual access.

Before activation, examine the source, version, and permissions of each component, and then test on a limited scope. **Install does not allow everything**: An update that adds a hook or server can change the possible actions, even if the visible command remains the same.

---

What is a skill for an agent? <!--anki:6f3f3e3a684076505951-->
?
An **instruction and resource folder** (e.g. `SKILL.md` + scripts) that the agent **loads on demand** when the task is suitable: only a short description remains permanently in the context (**progressive disclosure**).

For example, a document export procedure can include layout rules, rendering scripts, and examples. It guides the work without constituting a new training of the model. Its good execution always depends on the available tools and its prerequisites; the loaded instructions must remain compatible with the permissions of the host.

---

What is a hook in an agent harness? <!--anki:4c427a57297048423e58-->
?
A **script executed by the harness** at a specific time in the cycle (before or after a tool call, end of turn...): **deterministic**, it can block an action, format code or log, without depending on the goodwill of the model.
```json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "Bash",
        "hooks": [{ "type": "command", "command": "./scripts/check-command.sh" }] }
    ],
    "PostToolUse": [
      { "matcher": "Edit|Write",
        "hooks": [{ "type": "command", "command": "ruff format" }] }
    ]
  }
}
```
In Claude Code, only the **exit code 2** **Block** the tool call; another non-zero code indicates an error **Non-blocking**, Unless otherwise configured. A political script comes out. 2 or returns a JSON decision of refusal: this is the difference between a directive and a control ([[106-coding-agent-security|Code Agents]]).

---

How does a harness handle permissions? <!--anki:723e704a553f6c796757-->
?
By **modes and rules**: read-only, approve every action, allowlist commands, or full autonomy — with **human confirmation request** for sensitive actions.

The decision is applied **at runtime**, with the user's identity, the target and the actual arguments. An approval to read a file is not worth permission to publish it. Prefer limited and temporary rights; a simple "do nothing dangerous" instruction does not replace this control.

---

Why run an agent in a sandbox? <!--anki:497a51314634782d6450-->
?
For **Limiting the radius of impact** of an error or an [[101-llm-security-guardrails|prompt injection]] Restricted file system, filtered network, disposable container or VM.

For example, allow only a temporary directory, two minutes of calculation and the necessary domains. Test that an out-of-scope write and an unauthorized connection actually fail. The sandbox must also limit memory and CPU. It is not enough if a secret remains accessible or if an external service allows an excessive action: isolation and permissions complement each other.

---

Do not confuse: memory file (e.g. `CLAUDE.md`) and skill? <!--anki:77702e78736c33755528-->
?
The **memory file** is loaded **at each session** (project agreements); the **skill** is loaded **only when it is useful** — is put in the long and specialized procedures.

Put the general conventions, such as the test command, in the project instructions; place a detailed migration procedure in a specialized skill. The precise loading depends on the host and the perimeter of the files. None of these mechanisms is a memory of the weights of the model: these are instructions added to the context.

---

Do not confuse: harness, framework and agent platform? <!--anki:785e4a4b2b72266e5651-->
?
- **Harness**: the **program that runs** the loop at home (Claude Code, Cursor, or your own). It holds the tools, context and permissions
- **Framework**: the **library** with which you write this loop (LangGraph, CrewAI) ([[37-agent-frameworks|frameworks]])
- **Platform**: the **managed service** that hosts and governs it in production ([[38-agent-platforms|Platforms]])

Harness can be written without a framework, and deployed without a platform. The three answer different questions: **who runs**, **what you write**, **where it runs**.

---

How to test that a harness policy actually blocks a prohibited action? <!--anki:3837633964313464636161303430343462333166643163356663636164646463-->
?
Write a negative **run test**: request a prohibited action and verify that no effect has reached the target system. A "declined" message displayed after the call is not enough.

Try the relevant equivalent paths: direct tool, script, subprocess, and delegation. Record policy decision, normalized arguments, and proof of no effect. Repeat after a harness or plugin update. The test checks for a specific perimeter; it does not turn a list of blocked commands into general isolation.

---

Why is the work directory part of the security perimeter of a harness? <!--anki:3364383238343635386333363435623862303662313166633063393730373839-->
?
It determines **read files, discovered configurations, and relative paths** of commands. Running a test from the wrong repository can load a different configuration or write in the wrong place.

Set the project explicitly, resolve sensitive paths, and check for actual sandbox access. An apparent path can cross a symbolic link. Text instructions on the perimeter help the agent, but the necessary restrictions must be applied by the runtime environment.

---

How do I check if a deactivated plugin no longer has agent-usable capabilities? <!--anki:6262313565396236353736343438316262363038636230636338343133643936-->
?
Test **visible inventory and effective execution**: disappearance of tools, invalidation of sessions or concerned permissions and absence of alternative route via a proxy.

Include an agent that is already running, because it can keep an old schema in context. The runtime must refuse the call that has become prohibited even if the model still offers it. An interface that hides the plugin without removing its rights does not constitute a complete revocation.

---

## Scenarios

Scenario: Two teams use the same model for the same code agent, but one gets much better results. Where do you look for the difference? <!--anki:7142566f2e2663332b4c-->
?
1. **In the harness, not in the model**: with equal model, it is the tools, the context and the loop that make the difference
2. **Tools**: quality of code search, editing, test execution; descriptions and error feedback
3. **Context**: project convention file, skills available, compaction well set ([[35-context-engineering|context engineering]])
4. **Boutcle**: stop conditions, automatic check (tests, lint) after each modification
5. **Compare** by running both configurations on the same tasks ([[96-evals-rag-agents|evals d'agents]])

**Trap** To conclude too quickly that "the other team has a better model".

---

Scenario: you want to ensure that no agent on your team can launch `terraform apply` without proofreading, regardless of the instructions given to the model. How do you do it? <!--anki:4c7879576f32706a6e53-->
?
1. **Do not count on the prompt**: a prompt is bypassed, a check is not
2. **Hook** executed by the harness before each tool call: it inspects the command and **blocks** those that match a forbidden pattern
3. **Permissions**: white list of commands, approval mode for everything else
4. **Centrally managed setting**, not modifiable by the user ([[106-coding-agent-security|Code Agents]])
5. **Log** every block, to adjust rules and detect workarounds

**Trap**: Put the rule in the project convention file, which the model can ignore.

---

## Sources

- [Claude Code — hooks and exit codes](https://code.claude.com/docs/en/hooks)

## Connections
- [[31-agent-fundamentals|Agents]] — the loop that the harness executes
- [[32-tool-calling|Tool calling]] — Harness executes calls
- [[33-mcp|MCP]] — the harness is the host MCP
- [[35-context-engineering|Context engineering]] — What Harness Puts in Context
- [[101-llm-security-guardrails|LLM Security]] — permissions and sandbox
- [[38-agent-platforms|Platforms of agents]] — harness across an organization
- [[106-coding-agent-security|Security of Code Agents]] — Code Agent Permission and Isolation Modes
- [[49-coding-agents|Code Agents]] — Daily Use of a Code Harness
- [[103-agent-defenses|Defenses of agents]] — isolation, policies and least privilege
- [[104-mcp-skills-security|Security of MCP & Skills]] — tools and skills as supply chain
- [[24-cognee|Cognee]] — an agent memory in knowledge graph
- [[36-agent-orchestration|Orchestration multi-agents]] — subagents, handoffs and A2A
- [[39-agent-memory|Memorandum of agents]] — what the agent remembers from one session to the next
- [[43-langchain-agents|LangChain — Agents]] — agents and middleware LangChain
- [[44-langgraph-fundamentals|LangGraph]] — state graphs for agents and workflows
- [[90-014-agent-skill-evaluation|Evaluating Agent Skills]] — measure the triggering and utility of a skill
- [[90-015-agent-skills-format-skills-ref|Agent Skills & skills-ref]] — Open Skills Format and Validation
- [[00-moc-ai-engineering|MOC AI Engineering]]
