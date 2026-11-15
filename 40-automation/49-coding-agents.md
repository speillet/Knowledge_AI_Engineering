# Coding agents: usage & integration — Flashcards
Tags: #flashcards #ai-engineering #agents #coding-agents #development #llm
Verified on: 30 September 2026 — This factsheet lists products, versions or regulatory texts that are evolving quickly.
<!-- summary: ACI (SWE-agent), test-driven loop, `CLAUDE.md` and `AGENTS.md`, plan mode, worktrees and subagents, context management, headless mode, SWE-bench and its limits, tasks to delegate, provision measurement, patch independent testing, change location, patch proof. -->


What is a code agent? <!--anki:7773506d63697b387b3d-->
?
An agent who **reads the repository, edits files, issues commands** (tests, build, linter) and iterates on the results until reaching the goal. The difference with autocompletion: it **acts on several files** and **checks its work** by executing code.

Examples of harness: Claude Code, Codex CLI, Cursor, Assist ([[34-harness-plugins|harness]]).

The useful loop links hypothesis, modification and proof: reproduce a defect, apply a correction, then check the test concerned and the close regressions. All successful commands do not prove anything if they do not cover the requested behavior.

---

What is Agent-Computer Interface (ACI)? <!--anki:7a485e43794a50796e35-->
?
The idea, introduced by **SWE-agent** (Princeton, 2024), that an agent's tools must be **designed for a model**, as an interface is for a human:
- Orders **Simple** and few
- Exits **short and informative** (a summary rather than 5,000 lines of log)
- **Failure**: An editor that refuses a change that breaks the syntax

Same model, better ACI: significantly more solved tasks ([[32-tool-calling|Tool design]]).

---

Why are tests the best ally of a code agent? <!--anki:757d45234c6f283c2432-->
?
They give a **verifiable success signal**: the agent can close "edit → to run the → tests" without human. Without tests, it does not know if it has finished, and the reviewer must check everything by hand.

Effective practice: do **write the test first** (which fails), then write the code. Beware of the agent who **changes or deletes the test** to pass it: reread the test diffs.

---

What is a `CLAUDE.md` or `AGENTS.md` file for? <!--anki:676d516323456b606c62-->
?
A file of **project instructions**: build and test commands, conventions, architecture and known traps. Its loading and scope depend on the tool and location; the name alone does not guarantee its application.

Example: specifying "run the tests of the modified module, then typing" gives a verifiable action, unlike "write good code". Keep the commands up-to-date, without secrets, and check their consideration in a simple case.

Stay short; place specialized procedures in [[34-harness-plugins|skills]]s suitable for the host. These instructions guide the agent, but do not replace any permissions or CI controls.

---

Why request a plan before implementation? <!--anki:413f5465585d37213e68-->
?
On a non-trivial task, an agent who codes immediately often goes in a **bad direction** and produces a big diff to throw away. A **plan mode** (read-only) makes him explore the code and propose an approach that the human **corrects in a few lines**, before any change.

This is the plan-and-execute pattern applied to the code ([[48-agentic-workflow-patterns|patterns]]).

The plan must name affected files, invariants to preserve and success tests. For obvious local correction, a long plan can cost more than implementation; adapt its depth to risk and uncertainty.

---

How do I get multiple code agents to work in parallel? <!--anki:4c6c3026414b7b2b5a5f-->
?
- **One worktree Git per agent** (`git worktree add`): each agent has his working copy and branch, without stepping on it
- **Subagents** for exploration: they read a lot of code and only return a summary, which protects the main context ([[36-agent-orchestration|Subagents]])
- **Independent tasks** only: two agents on the same module produce conflicts

The bottleneck becomes the **human review**, not the generation.

---

How does a code agent handle its context over a long session? <!--anki:6f732e74736d4b784e42-->
?
- **Seek rather than read everything**: `grep`, reading targeted passages
- **Compaction**: summarize the history when the context fills up ([[35-context-engineering|context engineering]])
- **Short and targeted sessions**: one task per session, a new context for the next
- **Persistent Notes**: a progress file that the agent updates, to resume after a break

A context saturated with old logs lowers the quality well before the limit.

---

How to use a code agent in headless mode? <!--anki:43616b374770742f4231-->
?
Without interface, from a script or the IC: `claude -p "…"`, `codex exec "…"`. Uses: correct a lint, update dependencies, sort exits, propose a PR from a ticket.

Rules: **explicit and minimal** permissions, **structured** output (JSON) for the calling script, **budget** of turns and cost, and never untrusted data (issue title) processed as instructions ([[106-coding-agent-security|Security of Code Officers]]).

---

What is SWE-bench and what are its limits? <!--anki:6f2b4f5925675d2b363b-->
?
**SWE-bench**: solve real GitHub issues of Python projects, judged by repository tests. **SWE-bench Verified** (2024) in 500, validated by humans.

Limitations: Python only, popular repositories probably seen during training (**contamination**), rather short tasks. Harder variants (SWE-bench Pro, multilingual) exist. On **its own repository**, nothing replaces a trial on real tickets ([[146-model-selection|benchmarks]]).

---

Which tasks to delegate to a code agent? <!--anki:7751504573474253466f-->
?
- **Well adapted**: tasks **well specified and verifiable** (bug with reproduction, mechanical migration, tests to write, refactoring covered by tests)
- **To accompany**: new functionality, with validated plan and careful review
- **Keep**: choice of architecture, sensitive security code, no-test areas where the error is silent

Simple criterion: **Can I check the result faster than writing it?**

---

How to measure the contribution of code agents in a team? <!--anki:656d72496d647c2f4073-->
?
- **Debit**: PR merged, delay between ticket and start of production
- **Quality**: Backward rate, bugs in production, share of agent PRs reviewed
- **Cost**: tokens by merged PR, human review time
- **Perception**: surveys, but to cross with the figures, because the perceived gain may differ from the measured gain

Compare on **comparable tasks**, before and after, rather than prints.

---

Why should tests offered by a code agent include an independent check of the patch? <!--anki:3536636231393239623563373430366361366532323736383736306437333234-->
?
A **test written from the patch** can reproduce its logic and confirm the same error. First define the expected behavior from the need and a case that exposes the defect.

Verify that the test fails before the patch and then passes, then review boundary cases and neighboring effects. For regression, keep the actual entry in an anonymized or synthetic form. Existing tests, diff review, and invariants complete the added tests. An agent that simultaneously modifies code and expectations can make the suite green without repairing the need.

---

Why limit the surface area of a patch produced by a code agent? <!--anki:3462333639613938376133323466303761666636306366356231636161363961-->
?
An extensive change makes **the cause of the result and the review more difficult to establish**. For a local bug, mixing refactoring, updating dependencies and changing behavior increases the risks.

Define the observable fault, fix the affected paths and examine the full diff. A small diff is not a guarantee of quality; it must cover limit cases. Also measure unintentional changes and generated files.

---

How can I prove that a code agent regression test actually detects the initial bug? <!--anki:6263356664383437633933363466303338633364383137353132326562313434-->
?
Verify that it **fails on the defective version and succeeds after correction**, for the expected reason. A test that passes in both versions does not demonstrate repair.

The test must observe the external contract or invariant concerned, without copying the algorithm proposed by the agent. Check its assertion and fixations. When reproducing the initial environment is impossible, document this limit instead of presenting the test as complete proof.

---

## Scenarios

Scenario: your team adopts a code agent, but the PRs produced are huge, mix several topics and the reviewers approve them without reading them. What do you put in place? <!--anki:7451417a4e705a693771-->
?
1. **Cut to source**: one task per session, one plan validated before implementation
2. **Limit size**: short PR rule, the agent proposes a series of PRs rather than a single one
3. **Require verification**: added or modified tests, green CI, description of what was tested
4. **Priority review** test diffs and sensitive areas, indicated by review rules ([[106-coding-agent-security|PR d'agents]])
5. **Follow** the return rate of agent PRs compared to others

**Trap**: judge the tool by the number of rows produced.

---

Scenario: you want the code agent to update every week the dependencies of about twenty repositories, without intervention except in case of problem. How do you organize it? <!--anki:7237445f3a506f336b61-->
?
1. **Job planned in CI**, agent in headless mode, one repository and one branch per execution
2. **Minimum permissions**: reading the repository, writing to a dedicated branch, no production secrets
3. **Criteria of success**: build and green tests, otherwise the agent tries a correction limited to a few turns
4. **Systematic PR** with summary of changes and version notes read, never automatic merging of major updates
5. **Report**: up-to-date filings, open PRs, failures to be handled by a human

**Trap**: Let the agent merge on its own, or install packages it "assumed" to exist ([[106-coding-agent-security|slopsquatting]]).

---

## Sources

- [SWE-agent — project documentation](https://swe-agent.com/latest/)
- [Anthropic — security and permissions of Claude Code](https://code.claude.com/docs/en/security)

## Connections
- [[34-harness-plugins|Harness & plugins]] — the tool that runs the loop
- [[106-coding-agent-security|Security of Code Agents]] — the risks and their parades
- [[35-context-engineering|Context engineering]] — manage a long session
- [[36-agent-orchestration|Orchestration]] — subagents and parallelism
- [[48-agentic-workflow-patterns|Patterns of workflows]] — plan-and-execute applied to code
- [[96-evals-rag-agents|Evaluation of Agents]] — environments and pass^k
- [[147-ai-technical-leadership|Technical Leadership]] — Team Standards for AI Tools
- [[55-agentic-rl|Agentic RL]] — how models learn to code as agents
- [[03-containerd-runc|containerd & runc]] — the runtime that actually runs the containers
- [[102-agent-threats|Threats to agents]] — real attacks and incidents
- [[103-agent-defenses|Defenses of agents]] — isolation, policies and least privilege
- [[143-hallucinations-grounding|Hallucinations & grounding]] — quotes, abstention and verification
- [[145-system-design-cases|Case of system design]] — of commented type architectures
- [[38-agent-platforms|Platforms of agents]] — runtime, sandbox, tool gateway and identity
- [[94-evals-methodology|Evaluation — methodology]] — build a reliable eval set and metrics
- [[90-016-harbor-agent-evaluation|Harbor]] — evaluate a code agent on Terminal-Bench or its own tasks
- [[00-moc-ai-engineering|MOC AI Engineering]]
