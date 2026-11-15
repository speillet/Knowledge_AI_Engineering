# Evaluate agent skills — Flashcards
Tags: #flashcards #ai-engineering #evals #agents #skills #llm
Verified on: 14 November 2026 — This factsheet lists fast-moving products, versions or regulatory texts.
<!-- summary: Compliance, triggering and utility, role of description, overly simple requests, trigger set and near-misses, trace detection, three-test noise, training and validation, paired executions, reference without skill or older version, assertions and evidence, cost-per-success, SkillsBench (cured, self-generated skills, size, normalized gain), solution leak, skill invoked or useful. -->


What questions do you need to separate to evaluate an agent skill? <!--anki:3537303338616330316165633438636639386134396332626163613831343164-->
?
Three questions, tested by different means:
1. **Compliance**: Does the folder conform to the Agent Skills format? Static control, for example with [[90-015-agent-skills-format-skills-ref|skills-ref]].
2. **Trigger**: Does the agent charge the skill when it is used, and only then?
3. **Useful**: with the skill, does the task succeed more often than with a reference, and at what cost?

A valid skill may never trigger; a well-triggered skill may degrade the result. A single global score hides the failed step. Content security is handled separately ([[104-mcp-skills-security|Safety of Skills]]).

---

Why does the description of a skill decide to trigger it? <!--anki:3365343534333430616636343462663061376132333737303463666461303636-->
?
By [[34-harness-plugins|divulgation progressive]]: On startup, the agent only sees the `name` and `description` of each skill, about 50 to 100 tokens each. He only reads the complete `SKILL.md` after having judged the skill relevant. The description therefore bears the decision alone.

An effective description says what the skill does **and when to use it**, in terms of intent: "Use when the user wants to crawl a spreadsheet, even without saying CSV." The body of the file, as good as it is, does not help a skill that the agent never loads.

---

Why can a relevant skill not trigger on a simple request? <!--anki:3737636464666633316633343465306438333339653837373036326335383530-->
?
Agents mostly consult skills for tasks that go beyond what they can do on their own. "Read this PDF" is treated with the basic tools, even if the description of a PDF skill fits perfectly.

For the eval, positive queries must therefore require the knowledge of the — API internal skill, rare format, — business procedure and not just contain its keywords. Otherwise, a low trigger rate wrongly accuses the description. Do not load the skill is a failure only if the result suffers.

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
In the **agent tag**: call the skill loading tool or read the `SKILL.md`. The Agent Skills guide gives this example for Claude Code in headless mode:

```bash
claude -p "$QUERY" --output-format json \
  | jq -e --arg s "$SKILL" 'any(.messages[].content[];
      .type == "tool_use" and .name == "Skill" and .input.skill == $s)'
```

`jq -e` returns 0 if a `Skill` call is aimed at the tested skill. The output format depends on the client and its version: validate the detector on a positive case known before the series. We can stop the test as soon as the outcome is clear.

---

Calculation: a positive query actually triggers the skill in 40% tests. With 3 independent tests and the rule "observed rate > 0.5", what is the probability of counting it as successful? <!--anki:3438353634313032646332383437663438383430366565643464333736656636-->
?
At least 2 triggers on 3:
```text
P(X ≥ 2) = 3 × 0,4² × 0,6 + 0,4³ = 0,288 + 0,064 = 0,352
```
A weak request goes through **About once out of three**. With 3 tests, the observed rate takes only four values (0, 1/3, 2/3, 1): it is a coarse filter, useful for spotting net failures. To distinguish between two close descriptions, increase trials or queries and compare on the same queries ([[99-statistics-experimental-decisions|Experimental Decisions]]).

---

Why separate training and validation when optimizing the description of a skill? <!--anki:6532353735343935346136643462366139383036366366646334353062303065-->
?
Because we can **over-adjust** the description to the tested formulations, for example by copying the words of failed queries. The Agent Skills guide offers about **60% training and 40% validation**, with the same proportion of positives on each side and a fixed partition.

Training failures guide the changes; validation is only used to choose the **best iteration**, which is not necessarily the last. Five iterations are often enough. Finish by 5 to 10 new requests. Same logic as in [[12-automatic-prompt-optimization|Automatic optimization of prompts]].

---

How to measure the usefulness of a skill on a task? <!--anki:3162636334353065633865393434323039313063356530646665376431313634-->
?
By paired **executions**: each test case runs with the skill and without it, or with the previous version, to prompt, identical input files and model, each in a new **context** (subagent or separate session). We compare success, tokens and duration.

The new context ensures that the agent only follows the `SKILL.md`, not memories of the session where the skill was written. The matching removes from the comparison the specific difficulty of each case: we look at what the skill changes, case by case, before the average.

---

Do not confuse: reference without skill and old version reference to evaluate a skill? <!--anki:6332383263363764646161353463346239626134623634343765336638633663-->
?
The reference **Without skill** the Measure **absolute value** : Does the skill bring something to the naked model? The reference **Old Version** the Measure ’**Effect of a change** : Is the new editorial better than the one that is deployed?

For the second, freeze a copy before editing (`cp -r ma-skill/ workspace/skill-snapshot/`) and run the reference on this copy. A new version can beat the old one while remaining useless in front of the naked model, if the old one already degraded the result.

---

What is a good statement to note the release of a skill? <!--anki:3738616236303738306462653465306561633862636234306231363238386165-->
?
A **verifiable** statement on output: “the output file is a valid JSON”, “the graph has two labeled axes”, “the report contains at least three recommendations”.

To avoid: the wave ("the output is good") and the fragile ("contains exactly the phrase Total Revenue"), which rejects a correct output otherwise formulated. Write the assertions **after a first try**, when we see what a good output looks like. Entrust the mechanical controls to a script, the reading criteria to a [[95-llm-as-judge|juge LLM]] and the style to the human journal.

---

How to rate the assertions of a skill test with a LLM judge without complacency? <!--anki:6664636133336662373933333435353238336365653130363032663338303630-->
?
Require a **quoted proof** for each PASS: the judge provides `passed` and a `evidence` that cites or designates the output. A title "Summary" followed by a vague sentence is a FAIL: the label is there, not the content.

When noting, also judge assertions: too easy, impossible or unverifiable from the output. To compare two versions on global qualities, use a **blind comparison** where the judge does not know which version produced which output. Two outputs that pass all assertions may still differ markedly.

---

What assertions should be removed or corrected after a skill eval iteration? <!--anki:6464376138346662613533623463633038643831376265623632343133343030-->
?
Read the results **by assertion and by configuration**:
- **Successful with and without skill**: Learns nothing and inflates the score with skill; removes or hardens it;
- **Failed with and without skill** The broken assertion, case too hard or bad target; Correct it first;
- **successful with, failed without**: there is the contribution; identify the instruction or the decisive script;
- **unstable from one trial to the next**: ambiguous statement or random eval; add an example.

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

What does SkillsBench measure and what does it show about Cured Skills? <!--anki:3239316636363464646531623430363062333334323765646533656134316266-->
?
**SkillsBench** (4, June 2026) compares 87 tasks from 8 domains **without skill** and **with curated skills**, on 18 model-harness pairs, with deterministic checkers and three tests per cell. The average success goes from **33.9% to 50.5%** (+16.6 points).

The 18 configurations are progressing, de +4.1 to +25.7 points, but **13 Tasks on 87** Average gain does not guarantee a gain per task. By domain, The gain is +9.7 points (mathematics and operational research) to +28.8 (Natural Sciences). Tasks are in format [[90-016-harbor-agent-evaluation|Harbor]].

---

Why don't agent-generated skills help in SkillsBench? <!--anki:6337656231656538646634623464663462356562663930626537316661303934-->
?
When the agent writes his own skills before solving the task, the result passes **below the reference without skill** on the three tested configurations, from −8.1 to −11.5 points, while the skills cures there bring +18.2 to +24.8 points.

The audit of trajectories is about skills never discovered, time spent writing instead of solving, and content **false but affirmed**. A model does not teach itself a procedural knowledge that it does not: the value comes from an external and verified knowledge. Any skill generated is tested before being shared.

---

Which skill size gives the best gain in SkillsBench? <!--anki:3738393666333335666264653462383938346166373762336163386265626465-->
?
Skills **Targeted** A skill brings +18.0 points and two or three +19.0, against +10.1 from four. In terms of length, compact formats (+19.0and standard (+21.5) exceed the detailed (+14.5) ; Exhaustive documentation brings almost nothing (+0.7).

These are correlations observed on a task bank, not a law: a long procedure is sometimes necessary. They join the Agent Skills guide: keep the skill **sobre**, explain the why of the instructions and remove those whose traces show that they make the agent work for nothing.

---

Calculation: without skill, 33.9% success; with, 50.5%. What is the normalized gain g = (p_with − p_sans) / (1 − p_sans)? <!--anki:3566663366313435376536303430343262333236393565646332666339633434-->
?
Normalized gain reports progress to the remaining margin:
```text
g = (0,505 − 0,339) / (1 − 0,339) = 0,166 / 0,661 ≈ 0,251
```
The skill fills about **25% of failures** of the reference. This calculation on the global averages differs from the 25.5% published by SkillsBench, which calculates g **per configuration then averages**: the aggregation order changes the result. The normalized gain compares configurations of different levels, but becomes unstable when the reference approaches 100%.

---

How do I prevent an evaluated skill from containing the task solution? <!--anki:3161303163616633383030343462323062363439393563623335656363303166-->
?
By treating **leakage** as an acceptance criterion, SkillsBench rejects skills that contain task-specific file names or paths, the exact sequence of commands that resolves the task, constants in the statement, or references to tests.

The skills are written independently of the tasks, and the instruction never names the skill to use. An automatic check looks for leaks from the skill to the solution, before the human review. Without this, we measure the agent's ability to copy a response, not the value of reusable knowledge.

---

Do not confuse: skill invoked and skill useful? <!--anki:6662663365636162383132623434613138313639393762663062346135643438-->
?
**Invoked**: The path shows that the agent has read or called the skill. **Useful**: The verified result improves from the reference.

A skill can be read and then ignored: SkillsBench observes harnesses that acknowledge the content without applying it. It can also be read and harm if its content is false. Measure both: invocation rate, then success **conditional** to invocation. Rare discovery: work the description. Reading without effect: work the body of the skill.

---

## Scenarios

Scenario: According to the traces, your team's internal migration-schema skill is only loaded in 3 sessions on 10 where it would have served. How do you improve its triggering without having it load everywhere? <!--anki:6131643030396466666235313465353039656130653939336531353262356435-->
?
1. **Build the game** : 20 realistic requests drawn from the tracks, of which 8 TB 10 near-misses, as a simple SQL query or a data correction.
2. **Measure**: 3 per request, trigger rate per request, fixed partition 60/40.
3. **Diagnose** missed positives: intent not covered, or task that the agent considers feasible alone.
4. **Rewrite** the description to the imperative, centered on intent, specifying what the skill does not cover.
5. **Retain** the iteration at the highest validation score, and then test 5 to 10 new queries.
6. **Checking for usefulness**: Do the sessions that load the skill perform better?

**Trap** : copy the words of failed queries in the description.

---

Scenario: a new version of a report writing skill changes from 72% to 80% success on 25 cases, with only one trial per case. Your team wants to publish it. What do you check? <!--anki:3234373564376632646337303433396661633833373865363836366264336135-->
?
1. **Scale up**: 8 points on 25 cases, this is 2 cases; look at which ones change status, in both directions.
2. **Apparer**: compare old and new version case by case, and list regressions.
3. **Repeat**: 3 to 5 trials per case and version to separate the effect of the [[114-reproducibility-variance|variance]].
4. **Check cost**: tokens and duration by success.
5. **Reread** the outputs in comparison to the blind and remove the assertions always true.
6. **Decide** according to a pre-test threshold ([[99-statistics-experimental-decisions|Experimental Decisions]]).

**Pip**: Publish on a two-case spread.

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
- [[96-evals-rag-agents|Evaluation of GARs & Agents]] — result, trajectory and eval environments
- [[94-evals-methodology|Methodology of evals]] — test sets, references and regressions
- [[95-llm-as-judge|LLM-as-a-judge]] — note assertions that require playback
- [[99-statistics-experimental-decisions|Statistics & experimental decisions]] — decide on few matched cases
- [[12-automatic-prompt-optimization|Automatic optimization of prompts]] — the same risk of over-adjustment as the description
- [[35-context-engineering|Context engineering]] — the skills catalog as context budget
- [[00-moc-ai-engineering|MOC AI Engineering]]
