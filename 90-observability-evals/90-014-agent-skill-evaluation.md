# Evaluate agent skills — Flashcards
Tags: #flashcards #ai-engineering #evals #agents #skills #llm
Verified on: 14 November 2026 — This factsheet lists fast-moving products, versions or regulatory texts.
<!-- summary: Compliance, triggering and utility, role of description, overly simple requests, trigger set and near-misses, trace detection, three-test noise, training and validation, paired executions, reference without skill or older version, assertions and evidence, cost-per-success, SkillsBench (curated and self-generated skills, size, normalized gain), solution leak, skill invoked or useful. -->


What questions do you need to separate to evaluate an agent skill? <!--anki:3537303338616330316165633438636639386134396332626163613831343164-->
?
Three questions, tested by different means:
1. **Compliance**: Does the folder conform to the Agent Skills format? Static control, for example with [[90-015-agent-skills-format-skills-ref|skills-ref]].
2. **Triggering**: does the agent load the skill when it is useful, and only then?
3. **Usefulness**: with the skill, does the task succeed more often than with a reference, and at what cost?

A valid skill may never trigger; a well-triggered skill may degrade the result. A single global score hides the failed step. Content security is handled separately ([[104-mcp-skills-security|Safety of Skills]]).

---

Why does the description of a skill decide to trigger it? <!--anki:3365343534333430616636343462663061376132333737303463666461303636-->
?
Through [[34-harness-plugins|progressive disclosure]]: at startup, the agent sees only each skill's `name` and `description`, about 50 to 100 tokens each. It reads the full `SKILL.md` only after deciding the skill is relevant. The description therefore drives that initial decision.

An effective description says what the skill does **and when to use it**, in terms of intent: "Use when the user wants to explore a spreadsheet, even without saying CSV." The body of the file, as good as it is, does not help a skill that the agent never loads.

---

Why can a relevant skill not trigger on a simple request? <!--anki:3737636464666633316633343465306438333339653837373036326335383530-->
?
Agents mostly consult skills for tasks that go beyond what they can do on their own. "Read this PDF" is treated with the basic tools, even if the description of a PDF skill fits perfectly.

Positive evaluation queries should therefore require knowledge supplied by the skill, such as an internal API, unusual format or business procedure, rather than merely containing its keywords. Otherwise, a low trigger rate wrongly implicates the description. Not loading the skill is a failure only if the result suffers.

---

How to build a query set to test the triggering of a skill? <!--anki:3031636231383437393831613461316362626334663630353333373038336261-->
?
About **20 queries tagged** `should_trigger`, half positive, half negative:
- **Various positives**: formal or familiar tone, named or only described domain, short task or buried in a multi-step flow;
- **Near negatives** (*near-misses*): same keywords, different need;
- **Realistic context**: file paths, column names, typos.

The most useful positives are those where the link to the skill is not obvious: if the query accurately describes the skill, any description triggers it.

---

What is a negative "near-miss" query in a skill trigger eval? <!--anki:6565373337663737303561633432616139393934386365303039383965383333-->
?
A query that **shares keywords or domain** of the skill but asks for something else. For a CSV analysis skill, "write a script that loads every line of a CSV in Postgres" is the ETL, not the analysis.

"What weather tomorrow?" does not test anything: no reasonable description is triggered. Near-misses measure the **precision** of the description, as toolless cases measure false calls in [[96-evals-rag-agents|tool calling]]. A description that gains positives by becoming vague is betrayed on these cases.

---

How do I detect that a skill has been triggered during a trial? <!--anki:3332623937373534623761343433623362316265343966303964663138346633-->
?
In the **agent trace**: look for a skill-loading tool call or a read of `SKILL.md`. The Agent Skills guide gives this example for Claude Code in headless mode:

```bash
claude -p "$QUERY" --output-format json \
  | jq -e --arg s "$SKILL" 'any(.messages[].content[];
      .type == "tool_use" and .name == "Skill" and .input.skill == $s)'
```

`jq -e` returns 0 if a `Skill` call is aimed at the tested skill. The output format depends on the client and its version: validate the detector on a positive case known before the series. We can stop the test as soon as the outcome is clear.

---

Calculation: a positive query triggers a skill in 40% of trials. With 3 independent trials and the rule "observed rate > 0.5", what is the probability that it passes? <!--anki:3438353634313032646332383437663438383430366565643464333736656636-->
?
At least 2 of the 3 trials must trigger:
```text
P(X ≥ 2) = 3 × 0.4² × 0.6 + 0.4³ = 0.288 + 0.064 = 0.352
```
A weak query passes **about one time in three**. With 3 trials, the observed rate has only four possible values (0, 1/3, 2/3, 1). This is a coarse filter useful for detecting clear failures. To distinguish similar descriptions, increase the number of trials or queries and compare on the same queries ([[99-statistics-experimental-decisions|experimental decisions]]).

---

Why separate training and validation when optimizing the description of a skill? <!--anki:6532353735343935346136643462366139383036366366646334353062303065-->
?
Because we can **overfit** the description to the tested formulations, for example by copying the words of failed queries. The Agent Skills guide offers about **60% training and 40% validation**, with the same proportion of positives on each side and a fixed partition.

Training failures guide the changes; validation is only used to choose the **best iteration**, which is not necessarily the last. Five iterations are often enough. Finish by 5 to 10 new requests. Same logic as in [[12-automatic-prompt-optimization|Automatic optimization of prompts]].

---

How do you measure a skill's usefulness on a task? <!--anki:3162636334353065633865393434323039313063356530646665376431313634-->
?
Use **paired runs**: run each test case with the skill and without it, or with the previous version, keeping the prompt, input files and model identical. Each run starts in a fresh **context**, such as a separate session or subagent. Compare success, tokens and duration.

A fresh context ensures the agent follows the `SKILL.md`, without relying on memories of the session where the skill was written. Pairing controls for each case's difficulty: examine what the skill changes case by case before comparing averages.

---

Do not confuse: a no-skill baseline and a previous-version baseline? <!--anki:6332383263363764646161353463346239626134623634343765336638633663-->
?
A **no-skill baseline** measures **absolute added value**: does the skill improve the model's performance? A **previous-version baseline** measures **the effect of a change**: is the new wording better than the deployed version?

For the latter, freeze a copy before editing (`cp -r my-skill/ workspace/skill-snapshot/`) and run the baseline against it. A new version can beat the old one while still being worse than using no skill, if the old version already harmed results.

---

What makes a good assertion for grading a skill's output? <!--anki:3738616236303738306462653465306561633862636234306231363238386165-->
?
A **verifiable** statement about the output: "the output file is valid JSON", "the chart has two labeled axes" or "the report contains at least three recommendations".

Avoid vague assertions ("the output is good") and brittle ones ("contains exactly the phrase Total Revenue") that reject a correct result expressed differently. Write assertions **after an initial trial**, once you have seen what good output looks like. Assign mechanical checks to scripts, criteria requiring interpretation to an [[95-llm-as-judge|LLM judge]], and style to human review.

---

How do you grade skill-test assertions with an LLM judge without accepting unsupported passes? <!--anki:6664636133336662373933333435353238336365653130363032663338303630-->
?
Require **cited evidence** for every PASS: the judge returns `passed` and `evidence` quoting or pointing to the relevant output. A "Summary" heading followed by a vague sentence is a FAIL: the label exists, but the substance does not.

Also review the assertions themselves: are they too easy, impossible or unverifiable from the output? Compare overall qualities through a **blind comparison**, where the judge does not know which version produced each output. Two outputs that pass every assertion can still differ substantially.

---

What assertions should be removed or corrected after a skill eval iteration? <!--anki:6464376138346662613533623463633038643831376265623632343133343030-->
?
Read results **by assertion and configuration**:
- **Passes with and without the skill**: provides no evidence of added value and inflates the score; remove or strengthen it.
- **Fails with and without the skill**: the assertion may be broken, the case too hard or the target inappropriate; investigate first.
- **Passes with the skill, fails without it**: identifies a contribution; find the decisive instruction or script.
- **Varies across trials**: the assertion may be ambiguous or the evaluation stochastic; add an example.

---

Calculation: with the skill, 83% success for 3,800 tokens per test; without, 33% for 2,100 tokens. How many tokens costs a success in each configuration? <!--anki:3764333164633334613337643437626439363831306534386130366263376365-->
?
Tokens spent per successful task:
```text
with skill: 3,800 / 0.83 ≈ 4,580 tokens by success
without skill: 2,100 / 0.33 ≈ 6,360 tokens by success
delta per test: +50 pass points, +1,700 tokens
```
The skill costs more **per try** but less **per success**. The calculation assumes that a failure has no other cost; if it causes a human recovery, the gap widens. Conversely, doubling the tokens for +2 points is only justified if each success is expensive. Supplement by the duration and variance between tries.

---

What does SkillsBench measure, and what does it show about curated skills? <!--anki:3239316636363464646531623430363062333334323765646533656134316266-->
?
**SkillsBench** (version 4, June 2026) compares 87 tasks across 8 domains **without skills** and **with curated skills**, using 18 model–harness pairs, deterministic verifiers and three trials per cell. Mean success rises from **33.9% to 50.5%** (+16.6 percentage points).

All 18 configurations improve, by +4.1 to +25.7 points, but **13 of the 87 tasks** regress: an average gain does not guarantee improvement on every task. Domain-level gains range from +9.7 points for mathematics and operations research to +28.8 for natural sciences. Tasks use the [[90-016-harbor-agent-evaluation|Harbor]] format.

---

Why don't agent-generated skills help in SkillsBench? <!--anki:6337656231656538646634623464663462356562663930626537316661303934-->
?
When agents write their own skills before solving the task, performance falls **below the no-skill baseline** in all three tested configurations, by −8.1 to −11.5 points. Curated skills instead add +18.2 to +24.8 points in those configurations.

Trajectory audits identify skills that are never discovered, time spent writing instead of solving, and **incorrect content stated confidently**. A model cannot teach itself procedural knowledge it does not possess; value comes from external, verified knowledge. Test generated skills before sharing them.

---

What skill size produces the largest gains in SkillsBench? <!--anki:3738393666333335666264653462383938346166373762336163386265626465-->
?
**Focused skills**: one skill adds +18.0 points and two or three add +19.0, compared with +10.1 for four or more. Compact (+19.0) and standard (+21.5) formats outperform detailed ones (+14.5); exhaustive documentation adds almost nothing (+0.7).

These are correlations observed on a task benchmark, not a universal rule: some procedures need length. They align with the Agent Skills guide: keep the skill **concise**, explain why instructions matter and remove steps that trajectories show are unnecessary.

---

Calculation: success rises from 33.9% without a skill to 50.5% with it. What is the normalized gain g = (p_with − p_without) / (1 − p_without)? <!--anki:3566663366313435376536303430343262333236393565646332666339633434-->
?
Normalized gain expresses improvement relative to the remaining room for improvement:
```text
g = (0.505 − 0.339) / (1 − 0.339) = 0.166 / 0.661 ≈ 0.251
```
The skill closes about **25% of the baseline's failures**. Computing this from overall means differs from SkillsBench's reported 25.5%, which computes g **per configuration and then averages**. Aggregation order matters. Normalized gain compares configurations with different baselines, but becomes unstable as baseline success approaches 100%.

---

How do I prevent an evaluated skill from containing the task solution? <!--anki:3161303163616633383030343462323062363439393563623335656363303166-->
?
By treating **leakage** as an acceptance criterion, SkillsBench rejects skills that contain task-specific file names or paths, the exact sequence of commands that resolves the task, constants in the statement, or references to tests.

The skills are written independently of the tasks, and the instruction never names the skill to use. An automatic check looks for leaks from the skill to the solution, before the human review. Without this, we measure the agent's ability to copy a response, not the value of reusable knowledge.

---

Do not confuse: skill invoked and skill useful? <!--anki:6662663365636162383132623434613138313639393762663062346135643438-->
?
**Invoked**: the trajectory shows that the agent has read or called the skill. **Useful**: The verified result improves from the reference.

A skill can be read and then ignored: SkillsBench observes harnesses that acknowledge the content without applying it. It can also be read and harm if its content is false. Measure both: invocation rate, then success **conditional** to invocation. Rare discovery: work the description. Reading without effect: work the body of the skill.

---

## Scenarios

Scenario: traces show that your internal schema-migration skill loads in only 3 of 10 sessions where it would help. How do you improve triggering without loading it everywhere? <!--anki:6131643030396466666235313465353039656130653939336531353262356435-->
?
1. **Build a test set**: 20 realistic queries drawn from traces, including 8 to 10 near-misses such as a simple SQL query or data correction.
2. **Measure**: 3 trials per query, a per-query trigger rate and a fixed 60/40 train/validation split.
3. **Diagnose missed positives**: an intent missing from the description, or a task the agent considers feasible unaided.
4. **Rewrite the description** in the imperative, centered on intent and clear about what the skill does not cover.
5. **Keep the iteration** with the best validation score, then test 5 to 10 new queries.
6. **Check usefulness**: do sessions loading the skill succeed more often?

**Trap**: copying words from failed queries into the description.

---

Scenario: a new version of a report writing skill changes from 72% to 80% success on 25 cases, with only one trial per case. Your team wants to publish it. What do you check? <!--anki:3234373564376632646337303433396661633833373865363836366264336135-->
?
1. **Put the gain in perspective**: 8 points across 25 cases means 2 cases; examine changes in both directions.
2. **Pair results**: compare old and new versions case by case and list regressions.
3. **Repeat**: 3 to 5 trials per case and version to separate the effect from [[114-reproducibility-variance|variance]].
4. **Check cost**: tokens and duration per successful task.
5. **Review outputs blindly** and remove assertions that always pass.
6. **Decide** using a threshold set before testing ([[99-statistics-experimental-decisions|experimental decisions]]).

**Trap**: publishing based on a difference of only two cases.

---

Scenario: your platform wants to let agents write skills themselves from their successful sessions, and then share them with the whole team. What conditions do you pose? <!--anki:3561303130366662306336303433633862656130653761323839336235323264-->
?
1. **Do not assume a win**: in SkillsBench, self-generated skills do less well than the lack of skill.
2. **Validate the format** with `skills-ref validate`, then re-read the content and scripts ([[104-mcp-skills-security|Safety of Skills]]).
3. **Evaluate before sharing**: Executions matched with and without skill, on tasks other than the original session.
4. **Search for leaks**: Paths, constants, or commands specific to a single task.
5. **Publish in quarantine**: version, author, digest, followed by triggering and utility in production.
6. **Remove** skills without measured gain.

**Trap**: Judge the skill on the task that produced it.

---

## Sources

- [Agent Skills — Specification](https://agentskills.io/specification)
- [Agent Skills — Evaluating skill output quality](https://agentskills.io/skill-creation/evaluating-skills)
- [Agent Skills — Optimizing skill descriptions](https://agentskills.io/skill-creation/optimizing-descriptions)
- [SkillsBench — Benchmarking How Well Agent Skills Work Across Various Tasks, arXiv 2602.12670, version 4 June 14, 2026](https://arxiv.org/abs/2602.12670v4)
- [Harbor — Skills](https://docs.harborframework.com/jobs/skills)

## Connections
- [[90-015-agent-skills-format-skills-ref|Agent Skills & skills-ref]] — static format control, before any test
- [[90-016-harbor-agent-evaluation|Harbor]] — run in containers testing with and without skill
- [[34-harness-plugins|Harness & plugins]] — what a skill is and how the harness loads it
- [[104-mcp-skills-security|Security of MCP & Skills]] — Risks of Shared Skill
- [[96-evals-rag-agents|Evaluation of RAG systems & Agents]] — result, trajectory and eval environments
- [[94-evals-methodology|Methodology of evals]] — test sets, references and regressions
- [[95-llm-as-judge|LLM-as-a-judge]] — score assertions that require reading the output
- [[99-statistics-experimental-decisions|Statistics & experimental decisions]] — decide on few matched cases
- [[12-automatic-prompt-optimization|Automatic optimization of prompts]] — the same risk of over-adjustment as the description
- [[35-context-engineering|Context engineering]] — the skills catalog as context budget
- [[00-moc-ai-engineering|MOC AI Engineering]]
