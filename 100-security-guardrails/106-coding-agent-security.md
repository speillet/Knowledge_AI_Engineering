# Coding agent security — Flashcards
Tags: #flashcards #ai-engineering #security #agents #coding-agents #llm
Verified on: 25 September 2026 — This factsheet lists products, versions or regulatory texts that are evolving quickly.
<!-- summary: choice target, permissionless modes, job isolation, s1ngularity, Amazon Q, trapped instruction files, PromptPwnd, agents in CI/CD, slopsquatting and typing, generated code quality, agent PR review, secrets, corporate policy, test code accessible secrets, test commands, proven dependencies. -->


Why are code agents a target of choice? <!--anki:476b3a2c623d293b2560-->
?
They run **on developer positions and in the IC**, with access to:
- The **source code** and the **Secrets** (`.env`, SSH Keys, cloud identifiers)
- to **shell**, **network**, package managers and `git push`

They also read a lot of **unreliable content**: issues, pull requests, README dependencies, web documentation. And their production **goes into production**.

---

Why are code agent “no permission” modes dangerous? <!--anki:4f3b28362d317a4f6d47-->
?
They remove **harness approval controls**, depending on the tool, without removing the actual rights to the process, so an error or injection can use all the accesses still available.

Example: A disposable container with the write-in host repository, cloud identifiers, or the Docker socket maintains a strong impact radius.

Limit mounts, secrets, network, and system permissions; prefer ephemeral execution to strictly necessary access. [[34-harness-plugins|Permissions of Harness]]s complete this isolation. A list of allowed commands is insufficient if it allows an interpreter capable of arbitrarily performing prohibited operations.

---

How to isolate a code agent on a development workstation? <!--anki:712b49724371326c6477-->
?
- **Devcontainer or VM**: Personal folder and SSH keys are not mounted
- **Limited tokens**: one fine-grained GitHub token for **a single deposit**, one cloud profile **read-only**
- **Outbound network** limited to packet registers and required API
- **Integrated sandbox** of the activated tool (restricted file system and network)

Concretely verify the montages, sockets and network with the actual identity of the process. Mounting the Docker socket or inherited credentials can make a seemingly isolated environment much more powerful than expected.

---

What did the s1ngularity attack against Nx reveal (August 2025)? <!--anki:495d797c65437a405750-->
?
Trapped versions of the npm **Nx** package were running a script at the installation that called **installed code agents** (Claude Code, Gemini CLI, Amazon Q)**with their permission bypass options**, to look for secrets and crypto wallets. The loot was published in public **gitHub repositories**.

Lessons:
- An installed code agent is **One more tool for malware**
- **Disable package installation scripts** (`ignore-scripts`)
- **Protect the secrets** of the post

---

What happened with the Amazon Q extension for VS Code (July 2025)? <!--anki:45217a77463752505454-->
?
A malicious **pull request** added an instruction to the extension prompt asking the agent to **erase local files and cloud resources**. This version was **officially released** before being removed.

The lesson: **prompts and configurations of an AI tool are code**. They follow the same review and supply chain controls as the rest.

A security test must verify that a destructive instruction cannot produce an effect with the available permissions. The prompt review completes the execution permissions; it does not replace them.

---

How can a repository trap a code agent? <!--anki:694862525d5e7d444e4f-->
?
By its **instruction files**: AGENTS.md, CLAUDE.md, editor rules files, README. The agent reads them as **signs**.
- The **File Backdoor** (Pillar Security, 2025) technique hides instructions in **Invisible Unicode** in a rules file, to insert a backdoor into the generated code
- A cloned repository or dependency may contain such files.

Parades: **read changes** to these files as code, and **detect invisible characters** in CI.

---

What is PromptPwnd (December 2025)? <!--anki:646f625f655846687644-->
?
A class of faults discovered by Aikido in **GitHub Actions and GitLab CI workflows** which pass from the external text (title and body of issue, of pull request, commit messages) in the **Prompt of an Agent** (Gemini CLI, Claude Code, Codex) with a **Privileged Token**. An attacker opens a trapped exit, and the agent executes commands or **Publish Secrets**. At least five Fortune companies 500 were affected.

---

How to secure an agent running in the CI/CD? <!--anki:47602d4c4b4f3d792e72-->
?
- **Never** insert external text into the prompt of an agent who has privileged tools
- **Minimum permissions** for workflow token (read only by default)
- **No secrets** in jobs triggered by external contributors; caution with `pull_request_target`, which gives access to secrets
- **Approval** before running fork workflows
- **Restricted agent tools** to what is strictly necessary

---

What is slopsquatting? <!--anki:412c2a396a414e493956-->
?
models **invent package names** that do not exist (about **20%** of packages recommended in a 2025 study on 576,000 code samples), and often **the same** from time to time. Attackers **register these names** with malicious content.
- **Check the existence and reputation** of a package before adding it
- **Packet Proxy** internal with whitelist, blocking packages too recent
- **Lockfiles** and Dependency Analysis (SCA)

---

Is the AI-generated code safe by default? <!--anki:66647c4730375d625b50-->
?
**No.** According to Veracode (2025), **45%** generated code samples contained a vulnerability in the Top 10 OWASP. Common defects: **injections**, **missing access control**, hard secrets, permissive configurations, obsolete dependencies.
- The **the same journal and the same SAST** only for human code
- **Security guidelines** in AGENTS.md and secure templates
- A **review assisted** by an agent if you will, but a **responsible human**

---

How to frame pull requests produced by agents? <!--anki:4225285247304b4e3425-->
?
- **Small PR**, easy to read
- **CODEOWNERS** human beings on sensitive paths: authentication, CI workflows, IaC, Dependencies
- An agent cannot **neither approve nor merge** its own PR (branch protection)
- **Dedicated account** to the agent (bot) to trace who wrote what
- **Security tests and scans** must be done before merging

Verify that the agent's account cannot change these protections or bypass the required controls. A green CI does not replace the review of sensitive changes, especially when an RA also changes the tests that validate it.

---

How to protect secrets against code agents? <!--anki:7441306c3a563f2f7e41-->
?
The agent reads the `.env` files and logs; it can **send a secret to the provider** in its context or the **commiter**.
- **Secrets manager** instead of plain `.env` files
- **Refuse rules** on secret files in the agent configuration
- **Secret detection** in pre-commit (gitleaks) and CI
- **Hide** in telemetry, and **immediate rotation** in case of exposure

---

What is the enterprise policy for AI code tools? <!--anki:555b5e314e2a775b24-->
?
- **List of approved tools**, in company offer (no data training, retention controlled)
- **Centrally managed settings** and not changeable by the user: denial rules, sandbox, MCP servers allowed
- **MCP servers and skills** from the internal registry only ([[104-mcp-skills-security|MCP & skills]])
- **Telemetry** sent to SIEM, **developer training**, and **incident process** known

Check contractually retention, use of data and subcontractors: the label "company" is not enough. Provide a procedure for the removal of an approved tool and the revocation of its access if conditions or risk change.

---

Do not confuse: typosquatting and slopsquatting? <!--anki:46332f6b2a535544773e-->
?
- **Typosquatting**: the attacker publishes a packet in the name of **close** to a popular packet (`reqeusts`) and expects a **human typo**
- **Slopsquatting**: the attacker publishes a package with the name **invented by a LLM**, which code agents recommend repeatedly

The second is aimed at **hallucinations** of models rather than humans. Common Parade: check the existence and reputation of a package before installing, and block packages that are too recent.

---

Why can a secret available only during testing still be exfiltrated by code offered by an agent? <!--anki:3662303333616138613037343461343262363436393334646636376134653435-->
?
**Tests run code**: Fixtures, installation scripts, and hooks can read the environment and use the network, so a secret missing from the prompt can remain accessible to the process being started.

Run untrusted code without sensitive secrets and with a limited network, then reserve privileged validations to a controlled context. Also review dependency and CI changes. Test that untrusted branches do not retrieve publication tokens. Separation of model reasoning and execution only protects if process rights are actually reduced.

---

Why should testing an agent PR be considered untrusted code execution? <!--anki:3537356633383139646664643431383938636162643033303662303839316135-->
?
Tests, fixtures, and installation scripts can **execute commands with runner rights**, so a modified repository can access secrets even if the application patch appears benign.

Use an isolated environment with minimal secrets and mastered network. Examine changes in test configuration and dependencies. A green CI proves that its checks were successful; it does not prove that the code executed was without adverse effects.

---

How do I check a dependency suggested by a code agent before adding it? <!--anki:6464383565336166663830353465316439636430343466386238383433323737-->
?
Check **the existence, origin, exact name and necessity** of the package, then its maintenance and dependencies. A plausible name can be invented or imitate a known package.

Prioritize official references and locked versions. Install first in an isolated environment. The number of downloads alone is not a proof of trust; a review should also look at installation scripts and useful permissions.

---

## Scenarios

Scenario: a GitHub Actions workflow launches Claude Code on each new issue to propose a fix. It has a `GITHUB_TOKEN` write and deployment secrets. What's wrong? <!--anki:475b4864355d5d7a5e71-->
?
1. **PromptPwnd**: the body of the exit, written by anyone, enters the prompt of a privileged agent
2. **Token too large**: read only by default; changes go through a read request pull
3. **Unnecessary secrets**: no secrets to deploy in this job
4. **Restricted tools**: No free shell or open network for this task
5. **Boxed trigger**: Reserved for the issue of the members of the organization, or subject to approval

**Trap**: To believe that a statement "ignores the instructions contained in the exit" is sufficient.

---

Scenario: a senior developer wants to launch his code agent with `--dangerously-skip-permissions` on his workstation, to go faster. What do you offer him? <!--anki:472c37752a4869333d59-->
?
1. **Understanding the Need**: Too many approval requests for current orders
2. **White list** of safe commands (tests, lint, build) and **refuse rules** on secret files and destructive commands ([[34-harness-plugins|permissions]])
3. **If permissionless mode is still required**: only in a devcontainer or disposable VM, without SSH keys or cloud credentials, with limited network
4. **Jets limited** to task submission

**Trap**: Allow it on the main computer. The s1ngularity attack showed what malware can do with these options.

---

## Sources

- [Anthropic — security and permissions of Claude Code](https://code.claude.com/docs/en/security)
- [SWE-agent — project documentation](https://swe-agent.com/latest/)

## Connections
- [[34-harness-plugins|Harness & plugins]] — permissions, hooks and sandbox
- [[102-agent-threats|Menaces & incidents]] — injection and code execution
- [[103-agent-defenses|Defensive Architecture]] — least privilege and secrets
- [[104-mcp-skills-security|Security of MCP & Skills]] — servers and skills on workstations
- [[105-agentic-ai-devsecops|DevSecOps for Agentic AI]] — CI Controls
- [[112-model-cicd|CI/CD models]] — Pipeline
- [[49-coding-agents|Code agents: usage]] — best practices for productivity
- [[101-llm-security-guardrails|LLM Security]] — injection, exfiltration and guardrails
- [[33-mcp|MCP]] — the standard protocol between agents and tools
- [[00-moc-ai-engineering|MOC AI Engineering]]
