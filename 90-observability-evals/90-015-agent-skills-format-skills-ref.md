# Agent Skills: format & validation with skills-ref — Flashcards
Tags: #flashcards #ai-engineering #agents #skills #evals #ci
Verified on: 14 November 2026 — This factsheet lists fast-moving products, versions or regulatory texts.
<!-- summary: Open specification Agent Skills, non-imposed location, mandatory and optional fields, name and description rules, progressive disclosure budget, skills-ref (validate, read-properties, to-prompt), structure and field controls, validator blind spots, unknown fields, Unicode names, catalog and cost in tokens, allowed-tools, CI integration. -->


What is the Agent Skills specification? <!--anki:6437336336333664616561303462663162313566383262343633346238653566-->
?
A **Open Format** which defines the content of a skill folder: a `SKILL.md` compulsory, with a YAML frontmatter and Markdown instructions, and optional cases `scripts/`, `references/` and `assets/`. Published on agentskills.io under Apache license 2.0, it follows a governance adopted on 4 November 2026, which provides for its attachment to LF Projects.

The format allows you to write a skill once and have it loaded by several clients. It does not set the activation decision or the permissions: a portable file does not guarantee the same behavior from one agent to another. The concept of skill itself is defined in [[34-harness-plugins|Harness & plugins]].

---

Does the Agent Skills specification require the location of skills? <!--anki:3334383034623237633038623438346561353665636661643333393565663030-->
?
**No**: it defines the content of a skill folder, not where the client is looking for it. Each client has its native directory; the `.agents/skills/` convention, at the project or user level, has been imposed to share skills between clients.

A client discovers a skill by searching for **subfolders containing exactly `SKILL.md`**, ignoring `.git/` or `node_modules/`. A valid skill can therefore remain invisible if it is stored somewhere other than where the agent is looking. Test the discovery in each target client, not just the format.

---

Which frontmatter fields of a SKILL.md are mandatory? <!--anki:6166303831373335613962613462306339323730316135623036336662303936-->
?
Two: **`name`** and **`description`**. Optional fields are `license`, `compatibility` (environmental requirements, 500 characters at most), `metadata` (keyboard and text values) and `allowed-tools`, experimental.

```markdown
---
name: analyse-csv
Description: Analyzes CSV files and produces graphics. Use when the user provides a CSV or spreadsheet to explore, even without saying CSV.
metadata:
  version: "1.2"
---
```

Reserve `compatibility` for real needs: system packets, network access, targeted product. Team-specific information, such as version or owner, goes into `metadata`.

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
Three levels of [[34-harness-plugins|divulgation progressive]]:
1. **Metadata** (`name`, `description`): about 100 tokens, loaded at startup for all skills.
2. **Instructions**, the body of the `SKILL.md`: less than 5,000 tokens recommended, loaded upon activation; file under **500 lines**.
3. **Resources** (`scripts/`, `references/`, `assets/`): Loaded only if the instructions refer to it.

Returns are made in relative paths, **only one level** since `SKILL.md`. A string of nested returns forces the agent to open multiple files to find a setpoint, or to stop before.

---

What is skills-ref? <!--anki:3066306630323336303930633434663738663162363137336438623639393961-->
?
The **reference library** of the Agent Skills specification, in Python 3.11 or higher, under Apache 2.0 license. It offers a API and a CLI:
- `skills-ref validate <dossier>`: controls the frontmatter and naming;
- `skills-ref read-properties <dossier>`: Displays properties in JSON.
- `skills-ref to-prompt <dossiers…>`: Generates the `<available_skills>` block of a prompt.

Its README is intended for **demonstration**, not production. It serves as an executable definition of rules; a publishing chain adds its own controls.

---

What checks skills-ref validate on the structure of a skill folder? <!--anki:3162323035306264336232393433393039613263373031663236613762353664-->
?
Before the fields, the structure:
- the path exists and designates a **folder**; a path to `SKILL.md` is returned to its folder;
- it contains `SKILL.md`, or otherwise `skill.md`;
- the file **starts with `---`** and the frontmatter is closed;
- The YAML reads with **strictyaml** and forms a table.

The command exits with the code **0** if the skill is valid, **1** if not, and lists the problems on the error output. This code is enough to block a commit or a CI.

---

What skills-ref validate controls does it apply to frontmatter fields? <!--anki:6566656234653837303330643430313362356237313631633039336135626530-->
?
- **Known Fields Only**: Any field outside `name`, `description`, `license`, `allowed-tools`, `metadata` and `compatibility` is an error.
- **`name`** present and not empty, normalized to Unicode NFKC, then controlled: length, lower case, dashes, folder name.
- **`description`** presents, not empty, 1,024 characters at most.
- **`compatibility`**: Text of 500 characters at most.

There is no control over the contents of `license`, `allowed-tools` or `metadata` values, or over the body of the file.

---

What does not check skills-ref validate? <!--anki:3436343764643935656537323461636538373438313366396537663661663539-->
?
Anything beyond the frontmatter:
- **body size**: 500 lines and 5,000 tokens recommended;
- on the **Links** worms `references/` or `scripts/`, which can be broken;
- the execution and security of **scripts**;
- the **quality of the description** and its triggering;
- **security**: hidden instructions, exfiltration, dependencies.

A "valid" skill is only **readable** by a compliant client. Trigger and utility are measured by trials ([[90-014-agent-skill-evaluation|Assessment of Skills]]); risk is handled by review ([[104-mcp-skills-security|Safety of Skills]]).

---

Why does skills-ref reject a version field placed at the root of the frontmatter? <!--anki:6364336336306366306463613439393062373935366536366136386530303131-->
?
Because the validator only accepts the **six fields** of the specification: `version: 1.2` at the product root "Unexpected fields in frontmatter". A team or client-specific data goes into `metadata`, key table and text values:

```yaml
metadata:
  version: "1.2"
  owner: equipe-data
```

The same reasoning applies to the extension of a customer: a product-specific field, placed at the root, fails the reference validator. Either we document this gap or we keep the skill portable. Prefixing the keys of `metadata` limits collisions between customers.

---

Do not confuse: skills-ref read-properties and skills-ref validate? <!--anki:6436646364333035663566313433383738313436393632613535636431643861-->
?
**`read-properties`** reads the frontmatter and returns properties in JSON; it only requires a readable YAML, a non-empty `name` and `description`. **`validate`** applies all rules: allowed fields, name format, folder matching, lengths.

A skill named `Analyse-CSV` in a `analyse-csv` folder passes `read-properties` but fails `validate`. Using `read-properties` to extract metadata into a script, `validate` as the quality gate. `to-prompt` is based on the same read as `read-properties`: it also does not validate.

---

How do Agent Skills and skills-ref diverge on allowed name characters? <!--anki:3062616536643966653031393434393439633666386665623766663166316361-->
?
The specification talks about lowercase alphanumeric characters by quoting `a-z`, `0-9` and the dash. The validator accepts any lowercase **Unicode** letter after NFKC normalization: its tests validate `мой-навык` or `技能`, and reject `НАВЫК`, written in uppercase.

Impact: `café-data` passes `skills-ref validate` but may be rejected by a client that applies the ASCII rule. For a shared skill, stick to the lowercase **ASCII** and add this control in CI. A reference validator does not replace a test in each target client.

---

What is skills-ref to-prompt and what is it used for? <!--anki:3133356439623536316239623430356638303563616331326438363737336134-->
?
A `<available_skills>` XML block that gives, for each skill, `<name>`, `<description>` and `<location>`, the absolute path of the `SKILL.md`:

```xml
<available_skills>
<skill>
<name>analyse-csv</name>
<description>Analysis of CSV files...</description>
<location>/home/u/.agents/skills/analyse-csv/SKILL.md</location>
</skill>
</available_skills>
```

It's the **catalogue** that a home-made harness puts in the prompt; README recommends it for Anthropic models, other customers format it differently, it also allows you to measure the cost of the catalog and see, outside of the customer, what the model reads at startup.

---

Calculation: an agent loads 40 skills whose description averages 600 characters. Counting about 4 characters per token and 30 tokens tags and path per skill, how many tokens costs the catalog each session? <!--anki:3365623434316532313665303463306261373064323766333430306664663439-->
?
```text
description : 600 / 4 = 150 tokens
by skill: 150 + 30 = 180 tokens
catalogue : 40 × 180 = 7 200 tokens
```
About **7,200 tokens** present in each session, before any task. The ratio of 4 characters per token is an approximation for English; French or code often cost more: measure with the model's tokenizer. With descriptions of 1,024 characters, the catalog would exceed 11,000 tokens. The [[35-context-engineering|prompt caching]] does not place the cost in context.

---

Does the allowed-tools field of a skill restrict what the agent can do? <!--anki:3762333234343435623264653430663039353839616666396639353136353037-->
?
**No**, according to the specification: this is a list of **pre-approved** tools that the skill can use, separated by spaces, e.g. `Bash(git:*) Bash(jq:*) Read`. The field is **experimental** and its support varies by client.

It therefore reduces confirmation requests rather than adding a barrier. A third-party skill that pre-approves an unrestricted shell expands what the agent executes without asking. Restrictions are within the **permissions of the [[34-harness-plugins|harness]]**, and a downloaded skill is read again like code ([[104-mcp-skills-security|Safety of Skills]]).

---

Where to place skills-ref validate in the delivery chain of a skills repository? <!--anki:3832376530373632613861663430323262633032666539326234316264643235-->
?
In **pre-commit** and in **CI**, on each skill file:

```bash
fail=0
for d in skills/*/; do
  skills-ref validate "$d" || fail=1
done
exit $fail
```

The loop validates all skills before failing, to display all errors at once; the 1 code blocks the merge. Then add what `validate` does not know: body lines, relative links, executable scripts, secrets, ASCII names. Pin the skills-ref version: a rule change must not break the CI without a review ([[105-agentic-ai-devsecops|DevSecOps]]).

---

## Scenarios

Scenario: a skill passes `skills-ref validate` in CI, but your team's code agent never loads it, even on obvious requests. How do you look for the cause? <!--anki:3864363162326234383934303462633438643132373831663965663937323532-->
?
1. **Discovered**: Is the folder in a directory that this client browses, `.agents/skills/` or native directory, at the project or user level?
2. **Catalogue**: is the skill in the list that the agent exposes? Compare with the output of `to-prompt`.
3. **Customer rules**: A non-ASCII name or root field specific to another client may be denied.
4. **Description**: Does it say when to use skill, in terms of intent?
5. **Measure**: trigger game with near-misses and several attempts ([[90-014-agent-skill-evaluation|Assessment of Skills]]).

**Trap**: conclude that the skill is correct because the validator passes.

---

Scenario: your team maintains 30 skills shared between two code agents from different providers. What deposit and CI rules do you put in place? <!--anki:3931656531636238663461653461386462383866333837313664613935393765-->
?
1. **Common format**: the six fields of the specification only, extensions in `metadata` with prefixed keys.
2. **Tiny ASCII names**, identical to records, controlled in addition to `skills-ref validate`.
3. **Budget**: Body under 500 lines, level references, verified links.
4. **Review** scripts and `allowed-tools` as code ([[104-mcp-skills-security|Supply Chain]]).
5. **Test per client**: discovery and triggering in both agents, on the same query set.
6. **Versioner**: version of skills-ref pinned and digest released for each skill.

**Trap**: Test in a single client and assume portability.

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
- [[105-agentic-ai-devsecops|DevSecOps IA]] — CI checks a skills repository
- [[00-moc-ai-engineering|MOC AI Engineering]]
