# DevSecOps for Agentic AI — Flashcards
Tags: #flashcards #ai-engineering #security #devsecops #agents #llm
Verified on: 25 September 2026 — global date preserved; targeted review of 13 November 2026 detailed in Sources.
<!-- summary: proof modeling (MAESTRO, ATLAS), repositories (OWASP, NIST, ISO 42001), AI-BOM, SBOM or AI-BOM, supply chain models, CI controls, adversarial tests (promptfoo, garak, PyRIT), red teaming, security eval gate, prompts as code, environments, logging, detection, response to incident -->


What is the DevSecOps applied to agentic AI? <!--anki:44494a704c554b4f3d6c-->
?
Integrate security **at each stage of an agent’s life cycle** (design, code, build, testing, deployment, operation) rather than in a final audit. What changes compared to a traditional application:
- **New assets** to protect and release: prompts, tool configurations, MCP servers, skills, models, datasets, memory, eval sets
- **New attack surface**: Any natural language input
- **Non-deterministic behavior**, which is statistically tested ([[114-reproducibility-variance|Reproducibility]])

---

How to do the threat modeling of an agent? <!--anki:5f6043506c24217b64-->
?
1. **Mapping**: assets, data, tools and rights, flows, trust borders, network outputs
2. **List untrusted entries** ([[102-agent-threats|threats]]) and check the **Rule of Two** for each stream
3. **List threats** with STRIDE, the Top 10 OWASP agent, **MAESTRO** (Cloud Security Alliance, model in 7 layers for AI agent) or **MITRE ATLAS**
4. Deduct **controls** and **adversarial tests**

To be redone as soon as a **tool, data source or level of autonomy** is added.

---

Which repositories describe attacks against AI and agents? <!--anki:414b466a5e572f687153-->
?
**OWASP** features the Top 10 LLM **2026**, the Top 10 of the agent applications **2026** released in December 2025, and AI Exchange.**ATLAS MITRE** describes tactics and attack techniques against AI.

Version reference: LLM identifiers have been reordered to 2026, while ASI agent identifiers belong to another list. An old analysis can remain useful if its edition is explicit; it does not become a cover of the new edition by simple change of label. These repositories are used for reasoning on threats. Link each relevant risk to a component, a measurement and a proof of test.

---

What does NIST offer for AI and agent security? <!--anki:705724283e7326467450-->
?
- **AI RMF**: the AI risk management framework, with its generative **AI profile** (AI 600-1)
- **AI Agent Standards Initiative** of CAISI (February 2026): interoperability and security of agents. It prepares **overlays SP 800-53** dedicated to agents: least privilege of tools, containment of actions, logging

A framework organizes controls, it does not automatically certify an application. Translate each retained risk into responsibility, measurement and proof: for example, a test showing that a tool actually refuses an out-of-scope operation.

---

What management and compliance frameworks apply to agentic AI? <!--anki:4c565e4f416e3d577049-->
?
- **ISO/IEC 42001** : AI management system, certifiable
- **CSA MAESTRO** (threat modeling agentic) and **Google SAIF** (AI security framework)
- **AI Act** European Union[[115-agent-platforms-governance|Governance]])

They do not have the same status: management standard, analysis method, safety framework and regulations impose different approaches. Choose the requirements according to the role of the organization and the use of the system. A management certification does not prove that a particular agent resists injections or meets all its legal obligations.

---

What is an AI-BOM? <!--anki:4d585b443b5e6e4c3825-->
?
A **Inventory of AI Components** of a system, on the model of SBOM: models (version, source, license), datasets, Prompt, Tools and Servers MCP, skills, Dependencies. Formats: **CycloneDX ML - BOM** and **SPDX IA Profile 3**.

It serves to **respond quickly to an incident** ("what agents are using the compromised X server?"), audit and compliance. It becomes a **purchasing requirement** in some procurements.

---

How to secure the model supply chain? <!--anki:32397d2c3454654279-->
?
- **Official sources** and internal mirror, review **pinned** by imprint
- Format **safetensors** rather than pickle, which can execute code ([[10-images-models-weights|Weight of models]]); parse remaining pickles (ModelScan, picklescan)
- **Check signatures**: OpenSSF **Model Signing** (v1.0 in 2025, based on Sigstore)
- Beware of third-party **fine-tunes**, which may contain **backdoors** activated by a trigger
- Check the **license**

---

Which conventional security controls remain indispensable in an agent’s IC? <!--anki:635f446973612436423e-->
?
The same as for any application:
- **SAST** on agent code
- **Dependency Analysis** (SCA) and lockfiles
- **Secret detection**
- **Scan of images and IaC**

They detect vulnerabilities in the software that surrounds the model: vulnerable dependency, secrecy, or excessive infrastructure permissions. Completing them with tool tests and context attacks. Passing conventional scans does not demonstrate that a malicious statement retrieved from a document will be properly contained.

---

Which AI-specific security controls to add to an agent’s IC? <!--anki:6b4e737433567a426026-->
?
- Scan of **Configurations MCP and Skills** (e.g. mcp - scan)
- Lint of prompts and configurations: **no secrets**, tool whitelists respected
- **Adversary test suite** used as gate
- Generation of the **AI-BOM** and **Signature** Artifacts
```yaml
jobs:
  securite-ia:
    steps:
      - run: mcp-scan scan .mcp.json                  # Tools and Skills
      - run: python -m lint_prompts prompts/          # secrets, authorized tools
      - run: promptfoo redteam run --config redteam.yaml
      - run: python -m ai_bom generate > aibom.json
      - run: python -m check_asr --max-injection 0.05 --max-exfiltration 0
```
See [[112-model-cicd|CI/CD models]].

This YAML is a **educational scheme**, to be adapted to the commands and modules actually available in the project. Define the attack sets, denominators and thresholds before making a gate. Zero exfiltration observed on some tests does not prove a zero risk; keep the results and versions tested to follow the regressions.

---

How to automate adversarial testing of an agent? <!--anki:516a3b58562466217c52-->
?
- **Tools**: **promptfoo** (open source, acquired by OpenAI in March 2026), **garak** (NVIDIA), **PyrIT** (Microsoft)
- **Benchmarks** : AgentDojo, InjecAgent
- **Test case**: one injection **per untrusted input source**, exfiltration attempts, privilege escalation, jailbreaks, destructive actions
- **Metric** decode work **success rate of attacks** (ASR) by category

Each successful attack becomes a **regression test**. Adaptive attacks remain stronger than these suites: we complete with human red teaming.

---

How to red-team an agentic system? <!--anki:792541572a57546c3a6b-->
?
- Test **the entire system**, not just the model: tools, memory, RAG, interface rendering, agent exchanges
- From **threat model scenarios**: data theft, unauthorized action, cost overrun
- Mobilize the **Human Creativity** In the face of humans, all the tested defenses have fallen ([[102-agent-threats|« The Attacker Moves Second »]])
- **When**: Before launch, with each major change, and continuously (bug bounty)

---

What is a security eval gate for an agent? <!--anki:737e5d52593c53394d46-->
?
A **security threshold that blocks deployment**, such as the [[112-model-cicd|eval gate]] quality:
- Maximum **ASR** per attack category
- **Zero tolerance** for critical scenarios (leakage of secrets, destructive action)

It is replayed at **every change of model, prompt, tool or skill**: a simple version upgrade of the model can change its robustness.

ASR refers to the success rate of attacks on a defined set. Zero violation observed on finished tests does not establish a zero risk; retain scenarios, effectiveness and severity of failures to interpret the threshold.

---

How do I manage agent prompts and configurations securely? <!--anki:497c4871785959714777-->
?
**Like code**:
- **Versioned** in Git and **replayed** in pull request
- **CODEOWNERS** Security on tool lists, policies and rights
- **No secrets**, signed releases
- **Detection of deviations** between declared and running configuration (register, [[115-agent-platforms-governance|Governance]])

A prompt line that adds a tool is **a change of rights**.

Comparing pre-deployment and post-deployment effective rights. A setpoint alone does not grant permission; it is the exposure of a tool and the permission applied by its server that make the action possible.

---

What are the rules for agent dev and test environments? <!--anki:50442e70333969307a7b-->
?
- **Synthetic or anonymized data** in dev and pre-production
- **Separated identifiers**: No production tokens accessible to a dev agent
- **Simulated** or sandboxed tools for testing, especially those that write or send
- **Same policies and guards** as in production, to test what will actually be deployed

Parity is about controls, not about sharing secrets. Test a shipment or payment with a double locale and verify that no real endpoint is accessible. Document preproduction differences that limit the scope of testing.

---

What to log for the security of an agent? <!--anki:755e792c39652e345530-->
?
Log **verified identity, tool, timestamp, policy decision, and result**, with action/correlation ID, version, and approval reference. Hide sensitive arguments before exporting to SIEM.

Example: distinguish between "authorised request", "call sent" and "confirmed effect". After timeout, a status **unknown** avoids falsely declaring success or failure; a reconciliation can complete the log.

Include refusals and errors, not just successful actions. Protect integrity, access and retention; do not save secrets to prove their use. Diagnostic traces can be sampled, but critical audit events must follow an explicit coverage policy ([[93-monitoring-inference|monitoring]]).

---

How to detect a compromised agent at runtime? <!--anki:6c7162372875413e5d40-->
?
Signals to watch:
- **New tools or domains** contacted, **call pics**, loops
- **Political Refusal** on the Rise
- **Sensitive data** in outputs (DLP)
- **Changed description** of a tool
- Activity at **unusual times**

We can also place **honeytokens**: false sensitive data whose use betrays an exfiltration. The platforms propose the detection of anomalies dedicated to agents.

---

How to react to an incident involving an agent? <!--anki:6d2e6a44283a755e6b31-->
?
1. **Contain**: kill switch (disable agent, block tool at gateway), **revoke tokens**, rotate secrets
2. **Investigate** with traces and session log: what input, what actions, what data
3. **Cleaning**: Purge poisoned memory or index finger, correct actions (compensation)
4. **Notify** according to obligations
5. **Post-mortem**: new control and **new regression test**

The Playbook **Exercise in advance**, As with any security incident.

---

How do I manage vulnerabilities in an agent system? <!--anki:48216c502f3d38795f7e-->
?
- Maintain the **Inventory** (AI-BOM) to know what is exposed
- **Follow security notices** of frameworks, MCP SDKs, servers and agent tools: they have already had critical flaws (e.g. CVE-2025-49596 in MCP Inspector, CVE-2025-6514 in mcp-remote)
- **correction time** according to criticality, as for any dependency
- Also monitor the **deprecations of models and API**, which force changes

---

Who is responsible for the security of agents? <!--anki:4b507379584d596b234b-->
?
A **Shared Responsibility** :
- **Platform team**: controls provided by default (gateway, sandbox, identity, traces)
- **Product team**: threat model, least privilege tools, adversarial tests
- **Security team**: standards, red teaming, detection, incident response
- **Owner of each agent**: responsible for their behavior and rights

**security champions** in teams, and training developers on agent-specific risks.

---

Do not confuse: SBOM and AI-BOM? <!--anki:723559332f417224645b-->
?
- **SBOM**: the inventory of **software components** of an application (libraries, versions, licenses), to know who is affected by a vulnerability
- **AI-BOM** : extends the inventory to **AI Components** : models and their versions, data sets, Prompt, Servers MCP, skills, Agents and their tools

The AI-BOM answers the question “Which agents are using this compromised MCP server?” which the SBOM does not cover.

---

Why does a certificate of origin for a model need to be verified on deployment? <!--anki:6166396335633339336130613466373561376565636161326535363436366236-->
?
A **attestation** connects an artifact to a construction and a producer according to a trusted model. Keeping it without checking it does not block any unauthorized artifact.

On deployment, check the identity of the signer, exact digest, source and conditions required by the policy. Apply the check to the weights and load code concerned. Keep the decision for the audit and provide for revocation. A valid signature from an unapproved actor is not enough; nor does a trusted provenance guarantee the absence of vulnerability or bias.

---

Why should an inventory of AI components be linked to active deployments? <!--anki:3932666439636163303636343464323062663833643835323537643532386237-->
?
A theoretical catalog does not tell **where a vulnerable version is still running**. Connect model, tokenizer, tools, dependencies, and configuration to instances and owners.

During an alert, identify exposed paths and check for actual removal after correction. Include scheduled jobs and forgotten environments. A corrected artifact in the registry does not imply that all workers have loaded it.

---

How to turn a prompt injection incident into a useful non-regression control? <!--anki:3137393766646234376266363436613361366330373836383533633164663463-->
?
Extract **the breached border and the forbidden effect**, then create a case reproducing this mechanism with dummy data. Verify that the control blocks the effect, not just a specific sentence.

Add form variants and keep a neighboring legitimate task to measure false positives. Version the case, its expected result and the policy concerned. A filter that memorizes only the historical payload does not demonstrate a general defense.

---

## Scenarios

Scenario: you need to set up the CI/CD of a new agent who reads the CRM and sends emails to customers. What do you put in the pipeline? <!--anki:715f364056525f595273-->
?
1. **Classic controls**: SAST, SCA, secret detection, image and IaC scanning
2. **AI controls**: scan MCP configurations and skills, lint prompts (no secrets, authorized tools), AI-BOM generation
3. **Quality assessments** and **adversarial tests**: injections into emails and CRM topics, exfiltration attempts, sending to unauthorized recipients
4. **Security eval gate**: zero tolerance for exfiltration and unauthorized shipment, ASR threshold for the rest
5. **Progressive deployment**: monitored canary, rollback ready ([[112-model-cicd|CI/CD]])

**Trap**: Only run adversarial tests on the first deployment, not every model, prompt, or tool change.

---

Scenario: an alert signals the use of a honeytoken, a fake API key placed in your HR agent's document database. Unroll your response to an incident. <!--anki:4d344f4e3765742d4069-->
?
1. **Contain**: disable the agent or its outgoing tools, revoke its tokens ([[115-agent-platforms-governance|kill switch]])
2. **Tracer**: which session read the trapped document, which entry triggered the leak, through which channel the key came out
3. **Evaluate**: what real data could have come out by the same way; turn the secrets concerned
4. **Clean**: Remove malicious content from the index or memory
5. **Notify** according to obligations, especially for personal data
6. **Post-mortem**: close the channel (outgoing network, rendering URLs) and add a regression test

**Trap**: Remove the trapped document before saving the tracks.

---

Scenario: your supplier announces that the model used by your agents is moving to a new version next month. What do you expect from the security side? <!--anki:653e3f45697d4c752f34-->
?
1. **Inventory**: AI-BOM indicates which agents are using this model
2. **Replay** the adversarial suite and the evals on the new version: the robustness to injections can change from one version to another
3. **Compare** ASR by category with current version, on the same cases ([[114-reproducibility-variance|Comparison Paired]])
4. **Block** if the security eval gate is not reached: strengthen the architecture controls or stay on the old version as long as it is available
5. **Deploy gradually** by monitoring policy denials and anomalies

**Trap**: Use a model alias that switches to the new version on its own.

---

## Sources

- [NIST — AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- [MITRE ATLAS — attack techniques against AI systems](https://atlas.mitre.org/)

Targeted review of 13 November 2026: affirmations specified in this pass; other content is not fully verified.

- [OWASP — Top 10 LLM, 2026 Edition](https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/) — Official PDF accessed; the historical index `/llm-top-10/` still displays the 2025 edition.
- [OWASP — PDF 2026](https://genai.owasp.org/download/56857/) — numbers, labels and perimeter changes.

- 14 November supplement 2026 — Artifact source: [SLSA v1.2 — Provenance](https://slsa.dev/spec/v1.2/provenance).

## Connections
- [[102-agent-threats|Menaces & incidents]] — what the threat model should cover
- [[103-agent-defenses|Defensive Architecture]] — Checks
- [[104-mcp-skills-security|Security of MCP & Skills]] — scan tools and skills
- [[106-coding-agent-security|Security of Code Agents]] — agents in the CI/CD
- [[112-model-cicd|CI/CD models]] — eval gate and pipeline
- [[111-mlops-llmops-fundamentals|MLOps & LLMOps]] — Version Artifacts
- [[115-agent-platforms-governance|— Agent Platforms Architecture & Governance]] — audit, kill switch, AI Act
- [[93-monitoring-inference|Monitoring of inference]] — Newspapers and Alerts
- [[10-images-models-weights|Images & weights of models]] — safetensors or pickle
- [[101-llm-security-guardrails|LLM Security & Guardrails]] — OWASP LLM and red teaming
- [[155-ai-act|AI Act]] — regulatory obligations
- [[33-mcp|MCP]] — the standard protocol between agents and tools
- [[90-015-agent-skills-format-skills-ref|Agent Skills & skills-ref]] — validate a skills repository in CI
- [[00-moc-ai-engineering|MOC AI Engineering]]
