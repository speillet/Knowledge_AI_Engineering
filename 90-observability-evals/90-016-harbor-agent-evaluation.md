# Harbor: Evaluate Container Agents — Flashcards
Tags: #flashcards #ai-engineering #evals #agents #benchmarks #containers
Verified on: 14 November 2026 — This factsheet lists fast-moving products, versions or regulatory texts.
<!-- summary: Harbor role, task components, checker and reward files, trial or job, oracle and nop agents, shared or separate checker, run command and its options, job or task skills, skill provenance, comparison with and without skill, reward aggregation, mis-trials, calculation of invalid rewards, pass@k, reward hacking, lint, check-and-anal. -->


What is Harbor? <!--anki:6239333066353262363737633431323738373066316330666434613364326133-->
?
An open source framework, under the Apache 2.0 license, created by the **Terminal-Bench** team to **evaluate and optimize agents and models** in containers. It runs existing agents, such as Claude Code, Codex CLI or OpenHands, or a home agent, on isolated tasks for which a checker calculates the reward.

This is the official harness of Terminal-Bench 2.0; it integrates third-party benchmarks like SWE-bench and produces reusable trajectories in [[55-agentic-rl|Agentic RL]]. The tests run locally with Docker, or in parallel with sandbox suppliers like Daytona or Modal.

---

What are the components of a Harbor task? <!--anki:6531363938333430363665383438303938616565346534643432343862363438-->
?
An autonomous file:
- **`instruction.md`**: the instructions given to the agent;
- **`task.toml`**: metadata, timelines, resources, network, checker mode;
- **`environment/`**: the definition of sandbox, often a `Dockerfile`;
- **`tests/test.sh`** : the auditor, Who writes the reward;
- **`solution/solve.sh`**, optional: a reference solution.

A task does not depend on the framework: it is a versioned package that another compatible tool can run. Treating it as — software review, testing, — versions prevents a task defect from passing for an agent failure.

---

How Does a Harbor Checker Produce a Trial Reward? <!--anki:3866306466343931396562353462636461626635366566343235656532666566-->
?
`tests/test.sh` runs after the agent and writes a number in **`/logs/verify/reward.txt`**, or metrics named in **`/logs/verify/reward.json`**, priority if both exist:

```bash
#!/bin/bash
set -euo pipefail
if pytest /tests/test_outputs.py; then
  echo 1 > /logs/verify/reward.txt
else
  echo 0 > /logs/verify/reward.txt
fi
```

Use absolute paths. Harbor clears these files at the beginning of the check: an agent cannot deposit its own reward there. The script can also call a [[95-llm-as-judge|juge LLM]], for example with the `harbor-rewardkit` package.

---

Do not confuse: trial and job in Harbor? <!--anki:6464323531366133323364643461353861373831363864656430376666653135-->
?
A **Trial** is **an agent's attempt on a task** Start the sandbox, execution of the agent, verification, reward and trajectory. A **Job** is an **Set of Trials** launched by `harbor run` It combines datasets. tasks, agents and models, and execute the trials in parallel.

With 30 tasks, two agents and 5 attempts per task, a job counts 300 trials. The statistics, like the average or pass@k, are calculated in the job, by agent, model and dataset. The **trajectory** of each trial, in ATIF format, is used for debugging.

---

What are Oracle and Nop Agents for in Harbor? <!--anki:3961323633656464376264363463623262306430376239363734313535383663-->
?
To **test the task before testing an agent**. **`oracle`** executes `solution/solve.sh`: it must get 1, otherwise the task is insoluble or the checker rejects a good solution. **`nop`** does nothing: it must get 0, otherwise the checker accepts the start state.

```bash
harbor run -p taches/ma-tache -a oracle
harbor run -p taches/ma-tache -a nop
```

A task can provide multiple reference solutions, chosen by a variable passed with `--ae`. A checker that accepts only one implementation is **over-adjusted** and will penalize correct agents.

---

Do not confuse: Shared Checker and Separate Checker in Harbor? <!--anki:6663336334633962353863663432663739663937633135623836323136666233-->
?
**Shared** (`environment_mode = "shared"`): Tests run in the agent's container, which has been able to read them or modify what they inspect. **Separate**: A new sandbox, where Harbor copies only the **artifacts** declared in `task.toml`.

```toml
artifacts = ["/app/output"]

[verify]
environment_mode = "separate"
```

`harbor init` creates separate tasks by default. Limit: what needs to be checked must exist as **files**; a current process or a state in memory must be materialized, otherwise the shared mode remains necessary. Separate mode also allows to re-check existing trials.

---

How do I launch an evaluation job with Harbor? <!--anki:3833616631323034643530323438363538313230633335343839376438336361-->
?
```bash
harbor run -d terminal-bench@2.0 -a claude-code \
  -m anthropic/claude-opus-5-5 -n 8 -k 5 -r 2
```
- `-d`: registry dataset, `-p` for a local folder, `-t` for a task
- `-a` and `-m`: agent and model;
- `-n`: concurrent trials, 4 by default;
- `-k`: attempts by task, 1 by default;
- `-r`: Repeated after error, 0 by default.

`--env daytona` moves sandboxes to a vendor to parallelize. `--print-config` displays the configuration: the versioner makes the job replayable.

---

How does Harbor provide skills to the agent during a trial? <!--anki:6637373038613239323238343433393562323438613530373237303066376230-->
?
With the repeatable option `--skill`, which accepts a local folder, `org/repo@ref` or a GitHub URL in `/tree/<ref>/<chemin>`:

```bash
harbor run -p taches/ -a codex -m openai/<modele> \
  --skill ./skills/analyse-csv --skill mon-org/skills@v1.4
```

For each trial, Harbor copies each skill to `/runtime/skills/<nom>` of the sandbox, after the health check and before the agent is installed. The integration then saves it to the native location: `$HOME/.agents/skills` for Codex, `$CLAUDE_CONFIG_DIR/skills` for Claude Code. If two skills have the same folder name, **the last wins**.

---

Do not confuse: Job and task skills in Harbor? <!--anki:3936326531326430653566323430653438646334303034376639323438363734-->
?
The **task skills** are integrated into the image, for example `COPY skills/ /skills/` in the `Dockerfile`, and declared by `environment.skills_dir`: all agents receive the same. The **job skills** come from `--skill` at launch: you change skills without rebuilding the task.

Job skills are copied to the `skills_dir` of the task, and a job skill **replaces** the task skill of the same name for this trial. To compare with and without skill, do not mix the two: a skill remained in the image contaminates the condition "without skill".

---

How does Harbor make it traceable the version of a skill used in a job? <!--anki:3665666433613337383539383465313939633862393836663061353166386537-->
?
The **job lock file** records, for each skill, his name, its source, a **digest SHA-256** of all its files and, for a Git skill, the URL of the repository and the **commit resolved**. Git skills are cached by commit in `~/.cache/harbor/skills/`.

A branch can move forward after the job: the commit and the digest say exactly what content produced the results. Compare the digests of two jobs before assigning a gap to "the skill": if the content differs, we may be comparing two versions without knowing it.

---

How to compare an agent with and without skill in Harbor? <!--anki:3030323739396665306531353435336661663932393430393663313263313731-->
?
Two identical jobs, to the skill limit:

```bash
harbor run -p taches/ -a claude-code -m anthropic/claude-opus-5-5 \
  -k 5 --job-name without-skill
harbor run -p taches/ -a claude-code -m anthropic/claude-opus-5-5 \
  -k 5 --job-name with-skill --skill ./skills/migration-schema
```

Keep tasks, agent, model, attempts, and environment; check that no skills are already in the images. Compare **per task**, then average, valid rewards, and tokens. `harbor view` shows in trajectories whether the skill has been loaded: non-trigger and inefficient skill do not correct in the same way ([[90-014-agent-skill-evaluation|Assessment of Skills]]).

---

How does Harbor aggregate the rewards of a job? <!--anki:3737663261373437636231373464396538643235363135303232366338366132-->
?
By default, it makes the **average** of the rewards; for a multi-dimensional `reward.json`, an average **per dimension**, where an absent dimension counts 0. A `metric.py` placed in the dataset replaces this calculation: it reads a JSONL file of rewards (`-i`) and writes a JSON object of metrics (`-o`).

To compare two conditions, also look at the results **per task** and per domain, as well as the number of valid rewards on each side ([[94-evals-methodology|methodology of evals]]).

---

What does Harbor do with a trial that ends in error? <!--anki:6332353832386265663962393434346261643139393166306464373131613136-->
?
Each type of error has its policy: resume or not, check or not, count or not the reward.
- **Agent time or context exceeded**: verified, reward **valid**; this is an agent failure.
- **Sandbox that does not start**: recovery, no verification, invalid reward.
- **Error ofAPI or flow limit** : recovery and verification, but Reward **Invalid**.

An invalid reward leaves the **numerator and the denominator** of the average. The restarts are set with `-r`, and `override_error_policy` modifies the policy of an error type.

---

Calculation: A 20 trials account job: 10 achievements and 6 valid failures, plus 4 invalid reward API error trials. What average does Harbor earn, and what would be the rate if these 4 trials counted as failures? <!--anki:3533313230643162643433613463393161356161393264313232386166623538-->
?
```text
Harbor : 10 / (10 + 6) = 0,625
errors counted in failure: 10 / 20 = 0.50
```
Harbor reports **62.5%**. Exclusion is fair if errors hit randomly. If they mostly hit long tasks, which make more calls and encounter more throughput limits, they remove difficult tasks and inflate the score. Before comparing two conditions, check that they have as many valid rewards and restart trial errors.

---

When does Harbor calculate pass@k, and for what values of k? <!--anki:3938313632666236356435363438623239653733323665666530313566393936-->
?
Only if each reward is **binary**, 0, or 1, and only one dimension. Harbor applies the [[114-reproducibility-variance|pass@k]] non-biased estimator per task, then averages on tasks.

The values of k are the powers of 2 from 2 and the multiples of 5, until the **smaller number of valid tests** of a task. With `-k 5` and no errors: k ∈ {2, 4, 5}. If a task has only 3 valid rewards, only pass@2 Stay. A reward continues. As 0.7, Delete Pass@k.

---

What are the three types of reward hacking distinguished by Harbor? <!--anki:6362363631623462633662303432633362353062393038386462396430336530-->
?
- **Alteration** (*tampering*): The agent disrupts the notation, for example by modifying the checker or pointing a symbolic link to the solution.
- **Cheat** (*cheating*): It gets the answer from a prohibited source, such as the benchmark solution published online.
- **Failure** (*loophole*): it satisfies the tests without solving the problem, for example by hard-coded the verified cases.

Each type calls its parade: isolate the checker, restrict the network, strengthen the tests. The same risk exists at training ([[55-agentic-rl|reward hacking in RL]]).

---

Do not confuse: harbor lint, harbor check and harbor analyze? <!--anki:6163373736353735656531333432376261353733323438386338383065653030-->
?
**`harbor lint`** statically controls the configuration of a task: solution or tests copied into the agent image, shared checker, image not pinned by digest, privileged container.

**`harbor check`** entrusts an agent with reviewing the sources of the task according to a grid, default 11 criteria inspired by Terminal-Bench.

**`harbor analyze`** intervenes **after** the job: an agent reads the task, the logs and the trajectory of each trial, then reports the rewards obtained by deceiving the checker and the instructions too vague. The first two precede the tests; the third audits the results.

---

How does Harbor limit network access cheating? <!--anki:6236613738303436396239643463646138326461623637353861353431646539-->
?
By `network_mode` in `task.toml`: `public`, `allowlist` with `allowed_hosts`, or `no-network`, separately adjustable for agent and verify.

```toml
[environment]
network_mode = "allowlist"
allowed_hosts = ["pypi.org"]
```

When the network is restricted, Harbor automatically allows the agent-declared inference point, or the configured `base_url`, and **disables built-in web search** of agents that have one. To limit awareness of being evaluated, paths and variables visible to the agent have neutral names.

---

What happens when you change the version of a task in a dataset Harbor? <!--anki:3135623836653661393034393438303461313634643336396264643061346331-->
?
Harbor applies the **semantic versioning** to tasks:
- **Corrective**: Existing trials are reused;
- **minor**: they are **re-verified** with the new checker;
- **major**: they are **relaunched**.

`harbor run -d <dataset>@<new-version> -a <agent> --diff <old-job>` applies these rules. Correcting an overly permissive checker thus costs a re-check, not a new passage of agents, provided you use a separate checker and preserved artifacts.

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

Scenario: on your internal dataset Harbor, a new agent changes from 55% to 94% success in one version. Before celebrating, what do you check? <!--anki:6362666337626132363061343439613962613933383538373665626230636439-->
?
1. **Read successful trajectories** with `harbor view`: Does the agent solve the task or bypass the tests?
2. **Launch `harbor analyze`** on the job to report alterations, cheats and flaws.
3. **Audit tasks** with `harbor lint`: shared checker, in-image testing, open network.
4. **Durcir**: separate checker, non-root agent, network whitelist, multiple reference solutions.
5. **Correct and version** tasks, then re-check with `--diff`.

**Trap**: Publish the score before you have read a single track.

---

Scenario: you discover that the checker of a task accepts an empty output file, whereas 2,000 trials have already been noted on this dataset. How do you fix without restarting everything? <!--anki:3637613938643835316637363433306539623232323262316438313863666433-->
?
1. **Reproduce** the fault: An empty output file must get 0 with the checker fixed.
2. **Correct** `tests/` and add a checker test, excluded from the sandbox by `.harborignore`.
3. **Mount the minor version** of the task: existing trials will be re-checked, not re-launched.
4. **Re-check** with `--diff` on the old job, which assumes a separate checker and preserved artifacts.
5. **Publish** the deviation before and after correction, and report the relevant rankings.

**Strap**: fix without changing version, which mixes old and new notes.

---

## Sources

- [Harbor — repository and README, version 0.26.0](https://github.com/harbor-framework/harbor)
- [Harbor — concepts](https://docs.harborframework.com/core-concepts)
- [Harbor — task format](https://docs.harborframework.com/tasks/overview), [Checker](https://docs.harborframework.com/tasks/verifier) and [solution](https://docs.harborframework.com/tasks/solution)
- [Harbor — Launching a Job](https://docs.harborframework.com/jobs/run-a-job), [skills](https://docs.harborframework.com/jobs/skills) and [Task Skills](https://docs.harborframework.com/tasks/skills)
- [Harbor — error classification](https://docs.harborframework.com/jobs/error-classification) and [Metric](https://docs.harborframework.com/datasets/metrics)
- [Harbor — Cracking down on reward hacking, 28 octobre 2026](https://docs.harborframework.com/news/reward-hacking)

## Connections
- [[90-014-agent-skill-evaluation|Evaluating Agent Skills]] — protocol with and without skill that Harbor executes
- [[90-015-agent-skills-format-skills-ref|Agent Skills & skills-ref]] — validate the format before injecting a skill
- [[96-evals-rag-agents|Evaluation of GARs & Agents]] — eval environments and end state verification
- [[114-reproducibility-variance|Reproducibility & variance]] — pass@k and repeated tests
- [[55-agentic-rl|Agentic RL]] — training environments and reward hacking
- [[49-coding-agents|Code Agents]] — code agent benchmarks and their limits
- [[95-llm-as-judge|LLM-as-a-judge]] — checkers that rate with a model
- [[00-moc-ai-engineering|MOC AI Engineering]]
