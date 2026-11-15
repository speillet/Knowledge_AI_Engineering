# Harbor: Evaluating Agents in Containers — Flashcards
Tags: #flashcards #ai-engineering #evals #agents #benchmarks #containers
Verified on: 14 November 2026 — This factsheet lists fast-moving products, versions or regulatory texts.
<!-- summary: Harbor purpose, task components, verifiers and reward files, trials and jobs, oracle and nop agents, shared and separate verifiers, run options, job and task skills, skill provenance, comparisons with and without skills, reward aggregation, trial errors, invalid rewards, pass@k, reward hacking, lint, check and analyze, restricted networks, task versions and re-verification. -->


What is Harbor? <!--anki:6239333066353262363737633431323738373066316330666434613364326133-->
?
An open source framework under the Apache 2.0 license, created by the **Terminal-Bench** team to **evaluate and optimize agents and models** in containers. It runs existing agents, such as Claude Code, Codex CLI or OpenHands, or a custom agent, on isolated tasks whose verifier computes a reward.

This is the official harness of Terminal-Bench 2.0; it integrates third-party benchmarks like SWE-bench and produces reusable trajectories in [[55-agentic-rl|Agentic RL]]. The tests run locally with Docker, or in parallel with sandbox providers like Daytona or Modal.

---

What are the components of a Harbor task? <!--anki:6531363938333430363665383438303938616565346534643432343862363438-->
?
A self-contained directory:
- **`instruction.md`**: instructions given to the agent;
- **`task.toml`**: metadata, timeouts, resources, network settings and verifier mode;
- **`environment/`**: the sandbox definition, often a `Dockerfile`;
- **`tests/test.sh`**: the verifier, which writes the reward;
- **`solution/solve.sh`**, optional: a reference solution.

A task is independent of the framework: it is a versioned package that another compatible tool can run. Treat it as software, with reviews, tests and versions, to avoid mistaking a task defect for an agent failure.

---

How does a Harbor verifier produce a trial reward? <!--anki:3866306466343931396562353462636461626635366566343235656532666566-->
?
`tests/test.sh` runs after the agent and writes a number to **`/logs/verifier/reward.txt`**, or named metrics to **`/logs/verifier/reward.json`**. The JSON file takes precedence if both exist:

```bash
#!/bin/bash
set -euo pipefail
if pytest /tests/test_outputs.py; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
```

Use absolute paths. Harbor clears these files at the start of verification, preventing an agent from leaving its own reward there. The script can also call an [[95-llm-as-judge|LLM judge]], for example through the `harbor-rewardkit` package.

---

Do not confuse: trial and job in Harbor? <!--anki:6464323531366133323364643461353861373831363864656430376666653135-->
?
A **trial** is **one attempt by an agent at a task**: sandbox startup, agent execution, verification, reward and trajectory. A **job** is a **set of trials** launched with `harbor run`: it combines datasets, tasks, agents and models, and runs trials in parallel.

With 30 tasks, two agents and 5 attempts per task, a job contains 300 trials. Statistics such as the mean and pass@k are computed within the job, grouped by agent, model and dataset. Each trial's **trajectory**, in ATIF format, supports debugging.

---

What are the oracle and nop agents for in Harbor? <!--anki:3961323633656464376264363463623262306430376239363734313535383663-->
?
They **test the task before testing an agent**. **`oracle`** runs `solution/solve.sh` and should receive 1; otherwise, the task is unsolvable or the verifier rejects a correct solution. **`nop`** does nothing and should receive 0; otherwise, the verifier accepts the initial state.

```bash
harbor run -p tasks/my-task -a oracle
harbor run -p tasks/my-task -a nop
```

A task can provide several reference solutions, selected through a variable passed with `--ae`. A verifier that accepts only one implementation is **overfit** and penalizes correct agents.

---

Do not confuse: shared and separate verifiers in Harbor? <!--anki:6663336334633962353863663432663739663937633135623836323136666233-->
?
**Shared** (`environment_mode = "shared"`): tests run in the agent's container, where the agent may have read them or modified what they inspect. **Separate**: tests run in a fresh sandbox, to which Harbor copies only the **artifacts** declared in `task.toml`.

```toml
artifacts = ["/app/output"]

[verifier]
environment_mode = "separate"
```

`harbor init` creates tasks with separate verification by default. The limitation is that anything to be checked must exist as **files**: a running process or in-memory state must be materialized, otherwise shared mode is still necessary. Separate mode also supports re-verifying existing trials.

---

How do I launch an evaluation job with Harbor? <!--anki:3833616631323034643530323438363538313230633335343839376438336361-->
?
```bash
harbor run -d terminal-bench@2.0 -a claude-code \
  -m anthropic/claude-opus-5-5 -n 8 -k 5 -r 2
```
- `-d`: a registry dataset; use `-p` for a local directory or `-t` for a task;
- `-a` and `-m`: agent and model;
- `-n`: concurrent trials, default 4;
- `-k`: attempts per task, default 1;
- `-r`: retries after errors, default 0.

`--env daytona` moves sandboxes to a provider to increase parallelism. `--print-config` displays the configuration; version it to make the job reproducible.

---

How does Harbor provide skills to the agent during a trial? <!--anki:6637373038613239323238343433393562323438613530373237303066376230-->
?
Use the repeatable `--skill` option, which accepts a local directory, `org/repo@ref` or a GitHub URL ending in `/tree/<ref>/<path>`:

```bash
harbor run -p tasks/ -a codex -m openai/<model> \
  --skill ./skills/analyze-csv --skill my-org/skills@v1.4
```

For each trial, Harbor copies each skill into the sandbox at `/runtime/skills/<name>`, after the health check and before agent installation. The integration then registers it at the native location: `$HOME/.agents/skills` for Codex or `$CLAUDE_CONFIG_DIR/skills` for Claude Code. If two skills have the same directory name, **the last one wins**.

---

Do not confuse: task skills and job skills in Harbor? <!--anki:3936326531326430653566323430653438646334303034376639323438363734-->
?
**Task skills** are built into the image, for example with `COPY skills/ /skills/` in the `Dockerfile`, and declared through `environment.skills_dir`: all agents receive the same skills. **Job skills** are supplied through `--skill` at launch, so they can change without rebuilding the task.

Job skills are copied into the task's `skills_dir`. A job skill **replaces** a task skill with the same name for that trial. Keep these sources distinct when comparing runs with and without a skill: a skill left in the image contaminates the "without skill" condition.

---

How does Harbor track the version of a skill used in a job? <!--anki:3665666433613337383539383465313939633862393836663061353166386537-->
?
The **job lock file** records each skill's name, source and **SHA-256 digest** of all its files. For a Git skill, it also records the repository URL and **resolved commit**. Git skills are cached by commit in `~/.cache/harbor/skills/`.

A branch can advance after the job runs; the commit and digest identify the exact content that produced the results. Compare digests before attributing a difference between jobs to "the skill": different content may mean that two versions were compared unintentionally.

---

How do you compare an agent with and without a skill in Harbor? <!--anki:3030323739396665306531353435336661663932393430393663313263313731-->
?
Run two jobs that differ only in the skill:

```bash
harbor run -p tasks/ -a claude-code -m anthropic/claude-opus-5-5 \
  -k 5 --job-name without-skill
harbor run -p tasks/ -a claude-code -m anthropic/claude-opus-5-5 \
  -k 5 --job-name with-skill --skill ./skills/schema-migration
```

Keep tasks, agent, model, attempt count and environment fixed; check that the images contain no skills already. Compare results **per task**, then the mean, valid rewards and token use. Trajectories in `harbor view` show whether the skill was loaded: failure to trigger a skill and an ineffective skill require different fixes ([[90-014-agent-skill-evaluation|skill evaluation]]).

---

How does Harbor aggregate the rewards of a job? <!--anki:3737663261373437636231373464396538643235363135303232366338366132-->
?
By default, Harbor computes the **mean** reward. For a multidimensional `reward.json`, it computes a mean **per dimension**, counting a missing dimension as 0. A `metric.py` in the dataset replaces this calculation: it reads a JSONL reward file (`-i`) and writes a JSON metrics object (`-o`).

The overall mean combines tasks with very different difficulty levels. Also compare results **per task** and domain, and the number of valid rewards in each condition ([[94-evals-methodology|evaluation methodology]]).

---

What does Harbor do with a trial that ends in error? <!--anki:6332353832386265663962393434346261643139393166306464373131613136-->
?
Each error type has a policy defining whether to retry, verify and count the reward.
- **Agent timeout or context limit exceeded**: verification runs and the reward is **valid**; this counts as an agent failure.
- **Sandbox startup failure**: retry, no verification, invalid reward.
- **API error or rate limit**: retry and verification, but an **invalid** reward.

Invalid rewards are excluded from **both the numerator and denominator** of the mean. Set retries with `-r`; `override_error_policy` changes the policy for a particular error type.

---

Calculation: a job has 20 trials: 10 successes, 6 valid failures and 4 API-error trials with invalid rewards. What mean does Harbor report, and what would it report if those 4 errors counted as failures? <!--anki:3533313230643162643433613463393161356161393264313232386166623538-->
?
```text
Harbor: 10 / (10 + 6) = 0.625
Errors counted as failures: 10 / 20 = 0.50
```
Harbor reports **62.5%**. Exclusion is fair if errors occur randomly. If errors mostly affect long tasks that make more calls and encounter more rate limits, exclusion removes difficult tasks and inflates the score. Before comparing conditions, check that they have the same number of valid rewards and rerun trials that ended in error.

---

When does Harbor calculate pass@k, and for what values of k? <!--anki:3938313632666236356435363438623239653733323665666530313566393936-->
?
Only when every reward is **binary**, 0 or 1, and has a single dimension. Harbor applies the unbiased [[114-reproducibility-variance|pass@k]] estimator per task, then averages across tasks.

Values of k are powers of 2 starting at 2 and multiples of 5, up to the **smallest number of valid trials** for any task. With `-k 5` and no errors, k ∈ {2, 4, 5}. If a task has only 3 valid rewards, only pass@2 remains. A continuous reward, such as 0.7, disables pass@k.

---

What are the three types of reward hacking distinguished by Harbor? <!--anki:6362363631623462633662303432633362353062393038386462396430336530-->
?
- **Tampering**: the agent interferes with scoring, for example by modifying the verifier or pointing a symbolic link to the solution.
- **Cheating**: it obtains the answer from a prohibited source, such as a benchmark solution published online.
- **Loopholes**: it satisfies the tests without solving the problem, for example by hard-coding the checked cases.

Each type needs a corresponding defense: isolate the verifier, restrict the network and strengthen the tests. The same risk exists during training ([[55-agentic-rl|reward hacking in RL]]).

---

Do not confuse: harbor lint, harbor check and harbor analyze? <!--anki:6163373736353735656531333432376261353733323438386338383065653030-->
?
**`harbor lint`** statically checks task configuration: solutions or tests copied into the agent image, shared verifiers, images not pinned by digest and privileged containers.

**`harbor check`** asks an agent to review task sources against a rubric, using 11 Terminal-Bench-inspired criteria by default.

**`harbor analyze`** runs **after** a job: an agent reads the task, logs and each trial's trajectory, then flags rewards obtained by fooling the verifier and overly vague instructions. The first two run before trials; the third audits the results.

---

How does Harbor limit network access cheating? <!--anki:6236613738303436396239643463646138326461623637353861353431646539-->
?
Set `network_mode` in `task.toml` to `public`, `allowlist` with `allowed_hosts`, or `no-network`. Agent and verifier settings can be configured separately.

```toml
[environment]
network_mode = "allowlist"
allowed_hosts = ["pypi.org"]
```

With a restricted network, Harbor automatically allows the agent-declared inference endpoint or configured `base_url`, and **disables built-in web search** for agents that provide it. Paths and variables visible to the agent use neutral names to limit awareness of being evaluated.

---

What happens when a task version changes in a Harbor dataset? <!--anki:3135623836653661393034393438303461313634643336396264643061346331-->
?
Harbor applies **semantic versioning** to tasks:
- **Patch**: existing trials are reused;
- **Minor**: existing trials are **re-verified** with the new verifier;
- **Major**: trials are **rerun**.

`harbor run -d <dataset>@<new-version> -a <agent> --diff <old-job>` applies these rules. Fixing an overly permissive verifier therefore requires re-verification rather than rerunning agents, provided the task uses a separate verifier and the artifacts were retained.

---

## Scenarios

Scenario: your team wants to know if its internal schema migration skill really improves Claude Code before deploying it to 200 developers. How do you organize the measurement with Harbor? <!--anki:6130353530316336613139653434393762333465643432373764353434623537-->
?
1. **Build 15 to 30 realistic tasks**, including limit cases, with separate checker and reference solution.
2. **Validate tasks**: `harbor lint`, `oracle` to 1, `nop` to 0, and no solution leak in the skill.
3. **Launch two matched jobs**, with and without `--skill`, 5 attempts per task.
4. **Compare by task**: success, valid rewards, tokens, regressions.
5. **Read trajectories**: skill loaded or not, instructions followed or ignored.
6. **Decide** according to a threshold set before, keeping the digest of the skill measured.

**Trap**: Measure the tasks that were used to write the skill.

---

Scenario: an agent jumps from 55% to 94% success on your internal Harbor dataset in one release. What do you check before celebrating? <!--anki:6362666337626132363061343439613962613933383538373665626230636439-->
?
1. **Read successful trajectories** with `harbor view`: does the agent solve the task or bypass the tests?
2. **Run `harbor analyze`** to flag tampering, cheating and loopholes.
3. **Audit tasks** with `harbor lint`: shared verifiers, tests in the agent image and open networks.
4. **Harden the environment**: separate verifier, non-root agent, network allowlist and multiple reference solutions.
5. **Fix and version** tasks, then re-verify with `--diff`.

**Trap**: publishing the score before reading a single trajectory.

---

Scenario: a task verifier accepts an empty output file, but 2,000 trials have already been scored on the dataset. How do you fix this without rerunning everything? <!--anki:3637613938643835316637363433306539623232323262316438313863666433-->
?
1. **Reproduce the defect**: an empty output file must receive 0 from the corrected verifier.
2. **Fix `tests/`** and add a verifier test, excluded from the sandbox through `.harborignore`.
3. **Increment the task's minor version**: existing trials will be re-verified rather than rerun.
4. **Re-verify** the old job with `--diff`, using a separate verifier and retained artifacts.
5. **Publish the before-and-after difference** and identify affected rankings.

**Trap**: fixing the verifier without changing the version, mixing old and new scores.

---

## Sources

- [Harbor — repository and README, version 0.26.0](https://github.com/harbor-framework/harbor)
- [Harbor — concepts](https://docs.harborframework.com/core-concepts)
- [Harbor — task format](https://docs.harborframework.com/tasks/overview), [Verifier](https://docs.harborframework.com/tasks/verifier) and [solution](https://docs.harborframework.com/tasks/solution)
- [Harbor — Launching a Job](https://docs.harborframework.com/jobs/run-a-job), [skills](https://docs.harborframework.com/jobs/skills) and [Task Skills](https://docs.harborframework.com/tasks/skills)
- [Harbor — error classification](https://docs.harborframework.com/jobs/error-classification) and [Metrics](https://docs.harborframework.com/datasets/metrics)
- [Harbor — Cracking down on reward hacking, 28 October 2026](https://docs.harborframework.com/news/reward-hacking)

## Connections
- [[90-014-agent-skill-evaluation|Evaluating Agent Skills]] — protocol with and without skill that Harbor executes
- [[90-015-agent-skills-format-skills-ref|Agent Skills & skills-ref]] — validate the format before injecting a skill
- [[96-evals-rag-agents|Evaluation of RAG systems & Agents]] — eval environments and end state verification
- [[114-reproducibility-variance|Reproducibility & variance]] — pass@k and repeated tests
- [[55-agentic-rl|Agentic RL]] — training environments and reward hacking
- [[49-coding-agents|Code Agents]] — code agent benchmarks and their limits
- [[95-llm-as-judge|LLM-as-a-judge]] — checkers that rate with a model
- [[00-moc-ai-engineering|MOC AI Engineering]]
