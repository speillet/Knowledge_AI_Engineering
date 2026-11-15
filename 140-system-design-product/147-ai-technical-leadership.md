# Technical Leadership in AI Engineering — Flashcards
Tags: #flashcards #ai-engineering #leadership #senior #product
<!-- summary: what makes a senior, choice of use cases, ROI, POC failure, RFC and ADR, build or buy, go/no-go, team standards, mentoring, design review, technical debt, communication and monitoring, conditions for reviewing an architectural decision, stopping a POC, transfer criteria. -->


What distinguishes a senior AI Engineer from a confirmed one? <!--anki:684c3732252364496938-->
?
A senior takes care of one **End-to-end result in uncertainty** : framing, proof of value, technical choices, delivery and operation. He makes the compromises clear. detects a misleading experience and knows how to stop an insufficient approach.

Faced with an evaluation at 94% on a game built by the team, he first asks how the cases were chosen. His contribution is also seen in the autonomy of the others: documented decisions, useful reviews, transmission and truly executable procedures. Knowing the definitions of this value helps to reason; demonstrating these skills requires achievements, analyzed incidents and arbitrations explained with their limits.

---

How to identify a good LLM use case? <!--anki:4b2577697b426f3a4c41-->
?
- **Frequent task**, expensive in human time, with **data available**.
- **Error tolerance** compatible (or low-cost human verification).
- **Measurable success** (time saved, resolution rate, quality).
- Business sponsor and identified **users**.

Avoid: cases where a **simple rule** or a classic ML model is sufficient, and cases where an error is **serious and difficult to detect**.

Example: summarizing 300 support calls per day for an advisor who reads the summary is a good candidate; refusing only a credit is not.

---

How to estimate the ROI of an AI feature? <!--anki:46336235733534795e37-->
?
**Value**: time saved × hourly cost × volume, additional revenue, errors avoided.
**Costs**: development, **recurring inference**, infra, **remaining human review**, maintenance (evals, model migrations), risks.
Include the actual **adoption rate** and the cost of **errors** in the system. An impressive POC is not an ROI.

Example: 2,000 tickets per month, 6 minutes saved on each 40 € of the hour, either 8,000 €. With 60% of actual adoption, he remains 4,800 € ; after 1,200 € Inference and 1,500 € of human review, 2,100 € per month, before maintenance and cost of errors.

---

Why do so many IA POCs never reach production? <!--anki:693a52455b6d31444b43-->
?
- Demonstrated on **some selected examples**, without representative eval.
- Difference between **80% in demo** and **95%+ required** in production.
- Underestimated topics: **Actual data**, access rights, security, compliance, costs at scale, integration into existing tools.
- No **owner** business or metric of success.

The senior asks these questions **from the framing**.

Prior to the POC, define a pass criterion: useful gain, quality per segment, complete cost and operational responsibility. Test a realistic volume and errors; a successful demonstration does not reveal the human correction load.

---

What does an RFC / doc design for an AI feature need to contain specific? <!--anki:4268716c3f7a326a2e6b-->
?
In addition to the classic content (context, objectives, architecture, alternatives):
- the **evaluation strategy** and the production start-up thresholds;
- the **modes of failure** of the model and their mitigations;
- the **risk analysis** (Safety, PII, [[155-ai-act|classification AI Act]]) ;
- the **Cost estimate** inference at scale;
- the **rollout plan** (canary, A/B) and **rollback**.

Example of evaluation criterion: 300 annotated cases, including 40 adversarial; production if accuracy reaches 92%, with no PII leak and with a p95 under 4 s.

---

What is an ADR and why write it for AI choices? <!--anki:66767745303f396a214d-->
?
A **Architecture Decision Record**: a short document that freezes **a decision, its context, the options discarded and its consequences**. AI choices (model, framework, RAG vs fine-tuning) are **often called into question** when the market moves: the ADR allows to know **why** one has chosen and **what condition** one must reconsider.
```text
ADR-014 — Hybrid search for support assistant
Context: 30% questions cite an exact product code.
Dismissed options: vectors only (reminder @10 = 0.71), BM25 only (0.64).
Decision: BM25 + vectors merged by RRF (0.86).
Reconsider whether: a model of embedding alone exceeds 0.85, or if the index cost doubles.
```

Example scores require a comparable protocol and uncertainty to become evidence of decision. Associate a date and a reviewer; ADR explains the choice without preventing its review.

---

Build or buy for an IA brick? <!--anki:623f7e44644d5d2e292c-->
?
**Buy** (SaaS, API Managed when the brick is **not differentiating**, standard and that the supplier is better and cheaper to scale. **Build** when it is **at the heart of value**, when the data or constraints (sovereignty, integration) require it, or when no offer is suitable. Criteria: total cost, **lock-in**, confidentiality, speed, Internal Competences ([[38-agent-platforms|Agent Platforms]]).

Example: buy the OCR of standard invoices; build the claims sorting which exploits fifteen years of internal data and constitutes the business advantage.

---

How to manage an AI project whose feasibility is uncertain? <!--anki:446a36356a5b543a253b-->
?
By **decision steps**: disposable prototype (days) → eval on real data → driver with users → production. At each step, a **digitized go / no-go criteria** defined in advance. We agree to **stop**: a fast no-go is a good result.

Example: extraction of contract clauses. Three-day prototype on 50 documents, go if at least 85% of the fields are correct; otherwise we stop or we reformulate the need. Driver of one month with ten lawyers, go if the processing time drops by 30% without increasing errors. The thresholds come from the business, not from the technical team alone.

---

What development standards does a lead set for the team? <!--anki:77473558776e6c7b3028-->
?
- **Prompt versioned** and reviewed as code.
- **Compulsory evaluations** in CI for any prompt or model changes.
- **Templates** of doc and ADR design.

The standard must make a decision reproducible: for example, any PR that modifies a prompt initiates the review of 150 cases and displays the deviation to the score of `main`. Adapt the depth of the review to the risk; small changes need targeted and fast controls. The lead provides examples and tools for these practices to be effectively used, not only documented.

---

What operating and security standards does a lead set? <!--anki:6c386e6a59785458604f-->
?
- **Single gateway**: Keys, budgets, observability.
- **Safety checklist**: injection, PII, tool permissions.
- **Systematic traces** and regular review of samples.

Name those responsible for alerts, incidents, budgets and model migrations. Test emergency shutdown, access revocation and recovery on a realistic scenario: every quarter, revoke the key of an agent and check that it stops in less than 5 minutes. The traces must be useful for diagnosis and proportionate to the sensitive data; a technical centralization does not replace the responsibility of the teams for the uses they deliver.

---

How to explain the limits of AI to a non-technical decision maker? <!--anki:79794d41516042715354-->
?
By **frequency, consequences and safeguards**, with categories without double counting.

Fateful example on 100 requests: 92 good automatic answers, 5 preventive escalations and 3 errors, including 2 detected then escalated. This represents **7 folders to review and 1 error not detected**, not a reliable service to 99% without human work.

Specify sample, period, uncertainty and detection time; these frequencies do not predict exactly the next 100 cases. Show a concrete failure, its severity, the cost of correction and that can interrupt the service. The decision maker must arbitrate an explicit residual risk, not just a percentage of performance.

---

How to stay up-to-date without chasing after each novelty? <!--anki:732f4a7c70342b334c40-->
?
- Separate **sustainable principles** (evals, security, architecture, costs) and **ephemeral tools**.
- Test the news **on its own evals**, not on ads.
- Reserve a limited **exploration time** and share the results (notes, internal demos).
- Maintain topics like this, **corrected** when reality changes.

Example: a better advertised model first passes the 200 cases of the home trial, with cost and latency, before any migration; the exploration takes two hours a week and returns in a monthly demo.

---

How does a senior develop the autonomy of a colleague on an AI project? <!--anki:3534353366323764333364353439633739313730343038363562616362636436-->
?
Give a **perimeter and a verifiable result**, with explicit constraints, access and success criteria. Explain the evaluation protocol and options before proposing its own solution, and then organize review points proportionate to the risk.

On a first deployment, prepare a runbook together and then let the colleague run it in a controlled exercise. The sign of progression is his ability to diagnose and decide without permanent dependency on the senior. Answering yourself to each problem can accelerate today while blocking this progression.

---

How to conduct an AI design review that results in a decision? <!--anki:3736656232363665373136663466663661366564373835333039623061323936-->
?
From **constraints and evidence**, then compare some realistic options, including baseline. Identify the hypothesis that could reverse the choice: quality on a segment, human review cost, quota or recovery time.

Transform testable disagreements into limited experiences, with responsibility and decision criteria. Document the choice, its limits and the condition of reconsideration in an ADR. A consensus on the framework is not enough if no one has verified the availability of the data or defined what would make the solution unacceptable.

---

How to prioritize an AI technical debt in the face of a new feature? <!--anki:6537306139656166653437613462663961346332663134316535376364653430-->
?
Describe the **measurable consequence** of debt: recurring incidents, migration time, operating cost, undetected errors, or dependence on a person. Compare its maintenance cost and risk to the correction effort and the value of the feature.

An unversioned dependency that invalidates evals can justify immediate action; an imperfect abstraction without impact can wait. Prefer a limited and verifiable correction to a general overhaul. Associate responsible, deadline and proof of improvement to the decision.

---

What does an AI architecture decision need to contain in order to be usefully reviewed? <!--anki:6465623364613265393236623466376661376434376261626335623334336665-->
?
A **architecture decision** records the problem, the options actually compared, the constraints and the evidence that motivate the choice. Add assumptions, responsible and reconsideration conditions.

For example: choose a API as long as the volume, privacy and cost remain in a defined envelope; re-evaluate if it is exceeded. Link benchmarks and experiences instead of stating that a tool is "better". Describe operational consequences and exit cost. Date and triggers avoid treating a contextual decision as a permanent truth.

---

When to stop an IA POC despite a convincing demonstration? <!--anki:3735626339626135336634353466323139653531373535363564636533383036-->
?
When representative tests show **insufficient value or unresolved fundamental constraint**: too costly errors, unavailable data or unsustainable exploitation.

Compare to a simple baseline and pre-POC criteria. Document what has been learned and the conditions that would warrant a recovery. The time already invested should not replace the assessment of future profits.

---

What should be contained in the transfer of an AI prototype to the team that operates it? <!--anki:3433316132303863383863333437303138353737626232313163326462656131-->
?
Transmit **service contract, release manifest, assessments, failure modes and recovery procedures**, with identified managers.

Run an installation and a simulated incident by the receiving team. A presentation of the code does not demonstrate operating autonomy. Keep known limitations, costs and reconsideration conditions; the transfer must allow for decision and action without depending on the original designer.

---

## Scenarios

Scenario: your management wants to "do AI" and asks you to launch six projects in parallel. How do you respond without passing for a brake? <!--anki:67617e3b517835434e71-->
?
1. **Qualify cases**: frequency, current human cost, available data, error tolerance, measurable success
2. **Remove** those that a simple rule or a classic model would treat better, and those where a serious error would go unnoticed
3. **Prioritize two cases** with identified business sponsor and clear success metric
4. **Drive in decision-making stages**: prototype, eval on real data, pilot, production, with numerical criteria
5. **Assume stop**: a fast no-go is better than a project that drags a year

**Trap**: Accept all six projects and deliver six prototypes that no one uses.

---

Scenario: a manager asks you why the assistant is "still wrong", after an impressive demonstration three months ago. How do you explain? <!--anki:7a2a466d215f342b287e-->
?
1. **Talk in probabilities**, not in technology: on 100 requests, so many successes, so many escalations, so many errors, some of which were detected
2. **Show real examples** of chess, not abstract averages
3. **Explaining the demo-production gap**: some examples chosen against real and varied data
4. **Present plan**: evals, measured corrections, safeguards, human verification where risk requires
5. **Encrypt net worth** despite errors: time saved, cost of errors, ROI ([[122-finops-llm|FinOps]])

**Trap**: Promise reliability that the system will not reach, or blame the model.

---

Scenario: You are the only person able to deploy and troubleshoot the assistant, and every delivery awaits your return. What do you put in place? <!--anki:3732376634316264343333373430393962333932396437373037376665336638-->
?
1. **Identify personal dependencies**: implicit access, commands, decisions, and knowledge.
2. **Document a reproducible route**, from eval to rollback, with examples of failure.
3. **Automate repetitive controls** and assign operational responsibilities.
4. **Run the course by a co-worker** and then correct any identified deficiencies.
5. **Measuring the autonomy acquired**: successful delivery and diagnosis without essential intervention.

**Trap**: Write documentation that no one has ever used, and then consider the completed transfer.

---

## Connections
- [[141-system-design-llm|System Design LLM]] — Frame and Referee
- [[146-model-selection|Choice of model]] — decisions to document
- [[94-evals-methodology|Evaluation methodology]] — criteria go / no-go
- [[122-finops-llm|FinOps LLM]] — Costs and Lead Role
- [[111-mlops-llmops-fundamentals|MLOps & LLMOps]] — role of Lead
- [[115-agent-platforms-governance|Agent Platforms — Governance]] — paved road
- [[155-ai-act|AI Act]] — regulatory framing
- [[49-coding-agents|Code Agents]] — Use and Integrate Code Agents
- [[171-ml-model-selection|Choose a model ML]] — justify complexity by business value
- [[116-ai-sre-incidents-capacity|SRE: incidents & capacity of AI services]] — responsibilities and follow-up of corrections
- [[00-moc-ai-engineering|MOC AI Engineering]]
