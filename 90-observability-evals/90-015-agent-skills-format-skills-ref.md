# Agent Skills: format & validation with skills-ref — Flashcards
Tags: #flashcards #ai-engineering #agents #skills #evals #ci
Verified on: 14 November 2026 — This factsheet lists fast-moving products, versions or regulatory texts.
<!-- summary: open Agent Skills specification, client-specific discovery locations, required and optional fields, name and description rules, progressive disclosure budgets, skills-ref commands, structure and field checks, validator blind spots, unknown fields, Unicode names, catalog token costs, allowed-tools and CI integration. -->


What is the Agent Skills specification? <!--anki:6437336336333664616561303462663162313566383262343633346238653566-->
?
An **open format** defining the contents of a skill directory: a required `SKILL.md` with YAML frontmatter and Markdown instructions, plus optional `scripts/`, `references/` and `assets/` directories. Published on agentskills.io under Apache 2.0, it follows governance adopted on 4 November 2026 that provides for affiliation with LF Projects.

The format allows you to write a skill once and have it loaded by several clients. It does not set the activation decision or the permissions: a portable file does not guarantee the same behavior from one agent to another. The concept of skill itself is defined in [[34-harness-plugins|Harness & plugins]].

---

Does the Agent Skills specification require the location of skills? <!--anki:3334383034623237633038623438346561353665636661643333393565663030-->
?
**No**: it defines the content of a skill folder, not where the client is looking for it. Each client has its native directory; the `.agents/skills/` convention, at the project or user level, has emerged as a way to share skills between clients.

A client discovers a skill by searching for **subfolders containing exactly `SKILL.md`**, ignoring `.git/` or `node_modules/`. A valid skill can therefore remain invisible if it is stored somewhere other than where the agent is looking. Test the discovery in each target client, not just the format.

---

Which SKILL.md frontmatter fields are required? <!--anki:6166303831373335613962613462306339323730316135623036336662303936-->
?
Two: **`name`** and **`description`**. Optional fields are `license`, `compatibility` (environment requirements, at most 500 characters), `metadata` (string keys and values) and the experimental `allowed-tools` field.

```markdown
---
name: analyze-csv
description: Analyzes CSV files and produces charts. Use when the user provides a CSV file or wants to explore a spreadsheet, even without mentioning CSV.
metadata:
  version: "1.2"
---
```

Reserve `compatibility` for actual requirements: system packages, network access or a target product. Team-specific information, such as version or owner, belongs in `metadata`.

---

What rules must the name field of a skill respect? <!--anki:6637373863643732613765323438633339313565306538656537383138386663-->
?
According to the specification: **1 to 64 characters**, lower case, digits and dashes only, without dash at the beginning or end, without double dash, and **identical to folder name**.

`pdf-processing` is valid; `PDF-Processing`, `-pdf`, `pdf--processing` and `pdf_processing` are not. Correspondence with the folder is the easiest rule to break: renaming the folder without changing the frontmatter invalidates the skill. The name serves as an identifier; it is the description that decides when to trigger it.

---

What should the description of a skill according to the Agent Skills specification contain? <!--anki:3465666463643461303735383435326461666263393765663362613165643764-->
?
**What the skill does and when to use it**, with keywords that a user would use. It counts 1 to **1,024 characters**.

"Help with PDFs" is too poor. "Extract text and PDF tables, fill out forms, merge files. Use when the user handles PDFs or talks about forms" gives the agent what to decide. A validator controls the length; the quality of the trigger is judged only by trying queries ([[90-014-agent-skill-evaluation|Trigger Eval]]).

---

What context budget does the Agent Skills specification recommend for each level of a skill? <!--anki:6661313736373864623665323466323838373230336238366266643863396366-->
?
Three levels of [[34-harness-plugins|progressive disclosure]]:
1. **Metadata** (`name`, `description`): about 100 tokens, loaded at startup for every skill.
2. **Instructions**, the `SKILL.md` body: under 5,000 tokens recommended, loaded on activation; keep the file under **500 lines**.
3. **Resources** (`scripts/`, `references/`, `assets/`): loaded only when the instructions reference them.

Use relative paths and keep references **one level deep** from `SKILL.md`. Chains of nested references force the agent to open several files to find an instruction, or stop before reaching it.

---

What is skills-ref? <!--anki:3066306630323336303930633434663738663162363137336438623639393961-->
?
The Agent Skills specification's **reference library**, requiring Python 3.11 or later and licensed under Apache 2.0. It provides an API and CLI:
- `skills-ref validate <directory>`: checks frontmatter and naming;
- `skills-ref read-properties <directory>`: returns properties as JSON;
- `skills-ref to-prompt <directories…>`: generates a prompt's `<available_skills>` block.

Its README describes it as a **demonstration**, not a production implementation. It provides an executable definition of the rules; a publishing pipeline adds its own checks.

---

What structural checks does skills-ref validate perform on a skill directory? <!--anki:3162323035306264336232393433393039613263373031663236613762353664-->
?
Before checking fields, it checks that:
- the path exists and identifies a **directory**; a path to `SKILL.md` is resolved to its parent directory;
- the directory contains `SKILL.md`, or otherwise `skill.md`;
- the file **starts with `---`** and the frontmatter is closed;
- the YAML can be parsed with **strictyaml** and forms a mapping.

The command exits with code **0** for a valid skill or **1** otherwise, listing problems on standard error. This exit code can block a commit or CI run.

---

What frontmatter field checks does skills-ref validate apply? <!--anki:6566656234653837303330643430313362356237313631633039336135626530-->
?
- **Known fields only**: anything outside `name`, `description`, `license`, `allowed-tools`, `metadata` and `compatibility` is an error.
- **`name`** must be present and nonempty; after Unicode NFKC normalization, its length, lowercase letters, hyphens and match with the directory name are checked.
- **`description`** must be present, nonempty and at most 1,024 characters.
- **`compatibility`** must be text of at most 500 characters.

It does not check the contents of `license`, `allowed-tools` or `metadata` values, or the file body.

---

What does skills-ref validate leave unchecked? <!--anki:3436343764643935656537323461636538373438313366396537663661663539-->
?
Anything beyond the frontmatter:
- **Body size**: the recommended 500-line and 5,000-token limits;
- **Links** to `references/` or `scripts/`, which may be broken;
- execution and safety of **scripts**;
- **description quality** and triggering behavior;
- **security**: hidden instructions, exfiltration and dependencies.

A "valid" skill is only **readable** by a compliant client. Triggering and usefulness require trials ([[90-014-agent-skill-evaluation|skill evaluation]]); risks require review ([[104-mcp-skills-security|skill security]]).

---

Why does skills-ref reject a version field placed at the root of the frontmatter? <!--anki:6364336336306366306463613439393062373935366536366136386530303131-->
?
The validator accepts only the specification's **six fields**: placing `version: 1.2` at the root produces "Unexpected fields in frontmatter". Team-specific or client-specific data belongs in `metadata`, a mapping of string keys to string values:

```yaml
metadata:
  version: "1.2"
  owner: data-team
```

The same applies to client extensions: a product-specific root field fails reference validation. Document the divergence or keep the skill portable. Prefixing `metadata` keys reduces collisions between clients.

---

Do not confuse: skills-ref read-properties and skills-ref validate? <!--anki:6436646364333035663566313433383738313436393632613535636431643861-->
?
**`read-properties`** reads frontmatter and returns JSON properties; it only requires readable YAML and nonempty `name` and `description` fields. **`validate`** applies all rules: allowed fields, name format, directory matching and lengths.

A skill named `Analyze-CSV` in an `analyze-csv` directory passes `read-properties` but fails `validate`. Use `read-properties` to extract metadata and `validate` as a quality gate. `to-prompt` uses the same reader as `read-properties`, so it does not perform full validation either.

---

How do Agent Skills and skills-ref diverge on allowed name characters? <!--anki:3062616536643966653031393434393439633666386665623766663166316361-->
?
The specification talks about lowercase alphanumeric characters by quoting `a-z`, `0-9` and the dash. The validator accepts any lowercase **Unicode** letter after NFKC normalization: its tests validate `мой-навык` or `技能`, and reject `НАВЫК`, written in uppercase.

Impact: `café-data` passes `skills-ref validate` but may be rejected by a client that applies the ASCII rule. For a shared skill, stick to the lowercase **ASCII** and add this control in CI. A reference validator does not replace a test in each target client.

---

What does skills-ref to-prompt produce, and what is it used for? <!--anki:3133356439623536316239623430356638303563616331326438363737336134-->
?
An `<available_skills>` XML block giving each skill's `<name>`, `<description>` and `<location>`, the absolute path to its `SKILL.md`:

```xml
<available_skills>
<skill>
<name>analyze-csv</name>
<description>Analyzes CSV files...</description>
<location>/home/u/.agents/skills/analyze-csv/SKILL.md</location>
</skill>
</available_skills>
```

This is the **catalog** a custom harness places in the prompt. The README recommends it for Anthropic models; other clients format it differently. It also helps measure the catalog's token cost and inspect what the model receives at startup without running the client.

---

Calculation: an agent loads 40 skills with descriptions averaging 600 characters. At about 4 characters per token, plus 30 tokens for tags and paths per skill, how many tokens does the catalog use per session? <!--anki:3365623434316532313665303463306261373064323766333430306664663439-->
?
```text
description: 600 / 4 = 150 tokens
per skill: 150 + 30 = 180 tokens
catalog: 40 × 180 = 7,200 tokens
```
About **7,200 tokens** enter every session before any task. Four characters per token is an approximation for English; French and code often cost more, so measure with the model's tokenizer. With 1,024-character descriptions, the catalog would exceed 11,000 tokens. [[35-context-engineering|Prompt caching]] does not remove this context usage.

---

Does the allowed-tools field of a skill restrict what the agent can do? <!--anki:3762333234343435623264653430663039353839616666396639353136353037-->
?
**No**, according to the specification: this is a list of **pre-approved** tools that the skill can use, separated by spaces, e.g. `Bash(git:*) Bash(jq:*) Read`. The field is **experimental** and its support varies by client.

It therefore reduces confirmation requests rather than adding a barrier. A third-party skill that pre-approves an unrestricted shell expands what the agent executes without asking. Restrictions are within the **permissions of the [[34-harness-plugins|harness]]**, and a downloaded skill is read again like code ([[104-mcp-skills-security|Safety of Skills]]).

---

Where should skills-ref validate run in a skill repository's delivery pipeline? <!--anki:3832376530373632613861663430323262633032666539326234316264643235-->
?
Run it in **pre-commit** and **CI** for every skill directory:

```bash
fail=0
for d in skills/*/; do
  skills-ref validate "$d" || fail=1
done
exit $fail
```

The loop checks every skill before failing, reporting all errors together; exit code 1 blocks the merge. Add checks that `validate` lacks: body length, relative links, executable scripts, secrets and ASCII names. Pin skills-ref's version so rule changes cannot break CI without review ([[105-agentic-ai-devsecops|DevSecOps]]).

---

## Scenarios

Scenario: a skill passes `skills-ref validate` in CI, but your team's code agent never loads it, even on obvious requests. How do you look for the cause? <!--anki:3864363162326234383934303462633438643132373831663965663937323532-->
?
1. **Discovery**: is the directory somewhere this client searches, such as `.agents/skills/` or its native project-level or user-level directory?
2. **Catalog**: does the skill appear in the agent's available list? Compare with `to-prompt` output.
3. **Client rules**: a non-ASCII name or another client's root-level field may be rejected.
4. **Description**: does it explain when to use the skill in terms of user intent?
5. **Measurement**: use a trigger test set with near-misses and repeated attempts ([[90-014-agent-skill-evaluation|skill evaluation]]).

**Trap**: assuming the skill works because format validation passes.

---

Scenario: your team maintains 30 skills shared between two coding agents from different providers. What repository and CI rules do you establish? <!--anki:3931656531636238663461653461386462383866333837313664613935393765-->
?
1. **Common format**: only the six specification fields; extensions go into `metadata` with prefixed keys.
2. **Lowercase ASCII names** matching directory names, checked in addition to `skills-ref validate`.
3. **Budget**: bodies under 500 lines, references one level deep and verified links.
4. **Review** scripts and `allowed-tools` as code ([[104-mcp-skills-security|supply-chain security]]).
5. **Test each client**: discovery and triggering in both agents on the same query set.
6. **Versioning**: pin skills-ref and publish a digest for each skill.

**Trap**: testing one client and assuming portability.

---

## Sources

- [Agent Skills — Specification](https://agentskills.io/specification)
- [Agent Skills — Add skills support to an agent](https://agentskills.io/client-implementation/adding-skills-support)
- [skills-ref — source code and tests, commit 83021e2 of November 4, 2026](https://github.com/agentskills/agentskills/tree/83021e2be457a9b6679148719c1f6074f0ad975e/skills-ref)
- [Agent Skills — Governance Adopted on November 4, 2026](https://github.com/agentskills/agentskills/blob/83021e2be457a9b6679148719c1f6074f0ad975e/GOVERNANCE.md)

## Connections
- [[90-014-agent-skill-evaluation|Evaluating Agent Skills]] — After Format: Trigger and Utility
- [[90-016-harbor-agent-evaluation|Harbor]] — Inject Validated Skills into Container Testing
- [[34-harness-plugins|Harness & plugins]] — the notion of skill and the permissions of the harness
- [[104-mcp-skills-security|Security of MCP & Skills]] — what format validation does not cover
- [[35-context-engineering|Context engineering]] — catalog cost and progressive disclosure
- [[105-agentic-ai-devsecops|AI DevSecOps]] — CI checks a skills repository
- [[00-moc-ai-engineering|MOC AI Engineering]]
