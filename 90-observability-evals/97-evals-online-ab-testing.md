# Evals online & A/B testing — Flashcards
Tags: #flashcards #ai-engineering #evals #ab-testing #production #llm
<!-- summary: Explicit and implicit signals, A/B test, guardrail metrics, shadow testing, canary or A/B, peeking, novelty effect, product metrics, online-offline loop, confidentiality, sample size calculation, intent to process and exposure bias, randomization unit, delayed metrics. -->


Why are offline evals not enough? <!--anki:6b62287a2a6d53773a7b-->
?
The offline game is **fated and incomplete**: it does not capture the actual **distribution** of the queries, nor their **evolution**, nor the effect on the **users** (satisfaction, retention). Only the measure **in production** tells if the change creates value.

Example: A game built before launch does not contain any questions about an offer that appeared the following month; it always displays 92% while this new segment fails. Conversely, a better offline variant can lengthen responses and lower usage. The offline remains the fast and risk-free filter; the online slices on the value.

---

Which quality signals to collect in production? <!--anki:7957626f517230716c-->
?
- **Explicit**: thumbs up/down, notes, comments — rare and biased towards the disgruntled.
- **Implications**: **reformulation** of the question, **copy** of the answer, **acceptance** of a code suggestion, abandonment, escalation to a human.
- **Automatic**: [[95-llm-as-judge|juges]] without reference on a sample, format validations, detectors.

An implicit signal remains ambiguous: copying can mean “useful” or “to be corrected elsewhere”. Crossing multiple signals with annotated traces, and measuring who gives feedback; silencers are not automatically satisfied.

---

What is an A/B test on a LLM application? <!--anki:4c3830253b43347c7138-->
?
A **A/B test** randomly assigns units to a control and variant, and then compares a pre-defined master metric. Randomization helps isolate the effect of changing prompt, pattern, or retrieve.

Choose the unit according to the interactions: user for a persistent history, team for a shared work, sometimes request for an independent task. Keep the assignment stable and analyze at the appropriate level. Control the workforce imbalances and telemetry before interpreting the scores: randomization does not correct the data lost after assignment.

---

What is a guardrail metric in an A/B test? <!--anki:6f6666764a3551592569-->
?
A metric that **should not degrade** even if the main metric progresses: **p95 latency, cost per request, error rate, refusal rate, security reports**. A variant that gains 2% satisfaction but doubles the cost can be **rejected**.

Set a **margin of non-inferiority** for each before the test, for example "latency p95 + 10% at most". The test then concludes twice: gain on the main metric, and no degradation beyond the margin on each guard. Several safeguards multiply the tests: take this into account in the analysis ([[99-statistics-experimental-decisions|tests multiples]]).

---

Do not confuse: canary and A/B test? <!--anki:703c247d5246697c554a-->
?
- **Canary** : expose the new version to **a small percentage of traffic** to detect **Faults** (errors, latency) before expanding — Objective **Security of deployment**.
- **A/B test**: measure **statistically** which versions are **best** — lens **product decision**.

Practical consequences: a canary lasts hours, with stop criteria on errors and latency; an A/B often lasts weeks, with a sample size calculated in advance. A successful canary does not prove that the version is better, and an A/B is not designed to quickly detect a failure: we often chain the two.

---

Why should the sample size and duration be fixed in advance? <!--anki:643c68246355213a393a-->
?
To avoid **peeking**: watch the result every day and **stop as soon as it is significant** greatly inflates the false positive rate. We calculate the necessary size (minimum detectable effect, power) before launching, or we use **sequential tests** designed for continuous monitoring.

Providing for a representative use cycle and safety shutdown rules. Stopping for incident is legitimate, but does not then present the result as that of a fixed test completed without bias.

---

What is the novelty effect in an A/B test? <!--anki:782c3c2e4b3e40457e26-->
?
A **transitional reaction to a change**, different from its lasting effect, positive or negative depending on usage.

Example: A new interface increases clicks on the first day because users explore it, without improving resolution after multiple uses. Compare by time since first exposure and frequency of use, not just by calendar date.

Predict duration and analysis before the test, with relevant business cycles. Control cohort composition, seasonality and interface learning; a temporal evolution is not automatically a novelty effect. Do not delete unfavourable days after the fact or extend until a favorable significance is obtained.

---

Which Product Metrics Link to LLM Metrics? <!--anki:6f4d4b523c2d764c7c4c-->
?
Linking technical scores to the **Really accomplished task** : resolution verified, Net working time, quality of decisions or total cost of treatment. An acceptance or click is just a proxy if no one checks the result.

Evaluating the link by error analysis and experimentation; a correlation alone does not prove a causal effect. Certain criteria such as security or fidelity to sources remain constraints even without immediate gain of conversion. Avoid optimizing an isolated score at the expense of the complete service.

---

How to close between online and offline? <!--anki:4f572f26404b2e515241-->
?
1. Sample **failures** detected online (feedback negative, judge in check).
2. The **Analyzing** and label them.
3. Add them to **golden dataset** ([[94-evals-methodology|Non-regression]]).
4. Correct, validate offline, redeploy in canary then A/B.

This is the [[153-data-flywheel-versioning|data flywheel]] applied to evals.

Set a rhythm, for example 30 failures analyzed per week, and group them by cause before pouring representatives to the game. Adding a hundred variants of the same failure overwhelms a single cause in the score: keep a few examples by category and track the strength of each.

---

What are the privacy precautions for online evals? <!--anki:483c79285a236e7d7a47-->
?
Set the **purpose and appropriate legal basis**, consent of which may be an option depending on the context; collection for the service does not automatically allow any reuse. Limit collected content, [[152-pii-privacy|hide personal data]] and restrict access to annotators.

Establish a retention period and verify subcontractors, transfers and erasure possibilities. Pseudonymization does not necessarily make traces anonymous. Document the protocol before transmitting conversations to an external judge or a proofreading team ([[154-gdpr-llm|RGPD]]).

---

Calculation: under the Lehr rule for two independent balanced arms, bilateral risk 5% and power 80%, how many users per arm to detect +2 points around success 70%? <!--anki:51317d402a63415f794c-->
?
Lehr rule (risk α 5%, power 80%):
```text
n ≈ 16 × p(1 − p) / δ² = 16 × 0.7 × 0.3 / 0.02² ≈ 8,400 per arm
```
Split the effect sought by 2 **multiplied by 4** the sample: detect +1 point request ≈ 34,000 per arm. If traffic does not allow it, aim for a larger effect, a less noisy metric, or rely on offline evals ([[114-reproducibility-variance|variance]]).

An offline evaluation helps to select a candidate, but does not alone identify the causal effect of a deployment. The rule ignores groupings and sequential readings; adapt the sizing to the actual plane.

---

Why distinguish intent to process and analysis from only users actually exposed in an A/B AI test? <!--anki:3034633733303261663164643439653661666532656332373862333265623635-->
?
The **Intention to treat** compare the units according to their initial assignment. Restricting after the fact to exposed users can introduce a bias if the variant precisely influences the exposure or loading errors.

Keep assignment, eligibility and exposure as separate events; define the analysis population before the trial. Report exposure failures and analyze their causes. An analysis of the presentations may answer a specific question with additional assumptions, but does not automatically replace the causal estimate related to randomization.

---

Why randomize one assistant per user rather than per message in some A/B tests? <!--anki:6662623337643438343431383435396662373931666562303831616562363032-->
?
The messages of a conversation are influenced. Changing the variant of each message can create **an inconsistent experience and contamination between treatments**.

Choose the unit according to the mechanism studied: user, conversation or team. Analyze uncertainty at this level, because several messages from the same person are not independent. A larger randomization may require more units to reach the desired power.

---

Why wait for the results to mature before comparing two variants with a delayed metric? <!--anki:6462663733656661653933623438346338303963383330666536323933626139-->
?
Recent applications have not yet had **time to produce their final result**. Comparing an older variant to a newer variant may artificially favor the former.

Define a common maturation window, track label coverage and analyze comparable cohorts. Quick indicators can help with piloting, but do not automatically replace the delayed business metric.

---

## Scenarios

Scenario: a product manager wants to stop an A/B test after two days because the variant wins from 3%. What do you answer? <!--anki:6a62463a447e37326561-->
?
1. **Explain Peeking**: Watching the results continuously and stopping as soon as it’s significant greatly inflates false positives
2. **Recall protocol**: set sample size and duration **before** launch, starting from the minimum effect to be detected
3. **Possible novelty effect**: check use cycles and cohorts; the first few days are not always enough to estimate a lasting effect
4. **Check guardrail metrics**: p95 latency, cost, error rate, and rejection rate must not degrade
5. **Alternative if the emergency is real**: Use a sequential test, designed for continuous monitoring

**Trap**: conclude on a metric chosen after the fact because it is favorable.

---

Scenario: you want to change the model of your assistant without risking degrading the experience. What validation sequence do you put in place? <!--anki:49405a5e697236447a4c-->
?
1. **Offline first**: golden dataset replayed, matched comparison, non-regression thresholds ([[94-evals-methodology|evals]])
2. **Shadow**: Real traffic also goes to the new version, without being shown, to compare the outputs. Isolate the external effects and measure the additional cost
3. **Canary**: a small percentage of users, to detect outages, latency and errors
4. **A/B test**: decide with a pre-defined main metric and guardrail metrics
5. **Bucking**: failures detected online power the golden dataset ([[153-data-flywheel-versioning|flywheel]])

**Pip**: go directly to full deployment because “offline evals are good”.

---

## Sources
- [Microsoft Research — Framework and Validity of Experiments](https://www.microsoft.com/en-us/research/articles/patterns-of-trustworthy-experimentation-pre-experiment-stage/)

## Connections
- [[94-evals-methodology|Evaluation methodology]] — offline vs online
- [[112-model-cicd|CI/CD models]] — canary, shadow, rollback
- [[113-monitoring-drift-feedback|Monitoring & feedback]] — feedback loop
- [[93-monitoring-inference|Monitoring of inference]] — quality signals without field truth
- [[114-reproducibility-variance|Reproducibility & variance]] — tests statistics
- [[144-ai-ux-human-in-the-loop|UX of AI]] — design feedback collection
- [[99-statistics-experimental-decisions|Statistics to decide in AI]] — check the validity of the online protocol
- [[174-recommendation-ranking|Recommandation & learning to rank]] — check the exposed list value
- [[178-causal-inference-decisions|Causal Inference & Product Decisions]] — Designing a Randomized Intervention
- [[00-moc-ai-engineering|MOC AI Engineering]]
