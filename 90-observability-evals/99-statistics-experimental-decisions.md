# Statistics for AI decisions — Flashcards
Tags: #flashcards #ai-engineering #evals #statistics #experimentation
<!-- summary: Useful effect and significance, p-value, confidence interval, matched comparison, independent unit, zero failure, multiple tests, power, causality, selection bias and sample mismatch ratio, opportunistic stop and sequential tests, Simpson's paradox, observation dependency. -->


Do not confuse: Statistical significance and practical importance? <!--anki:6261623137333138643566323438393961653766356166626633366465653635-->
?
**Significance** indicates incompatibility of observations with a null hypothesis, depending on the test and its assumptions.**Practical importance** depends on the magnitude of the gain, its cost and acceptable risk.

A tiny gain can become significant with a lot of data while not justifying a migration. Set a useful minimal effect before the experiment, and then report estimate and confidence interval. An uncertain result requires a decision explaining this uncertainty, not a binary read "p less than 0.05 so deploy".

---

What does a p-value of 0.03 mean in a model comparison? <!--anki:6561656235626662376234663463343561326563666435336662613531643437-->
?
Under the **Hypothesis null** and the assumptions of the test, a p-value of 0.03 is the probability of a statistic at least as extreme as that observed. It's not 97% Chances are that the model will be better.

Example: testing twenty independent metrics under twenty null assumptions true at the threshold of 5% gives about **64% probability of at least one significant result**: `1 − 0,95^20`.

Pre-specified metric, pairing, stopping and correcting multiple comparisons. Reporting effect, interval and business cost; significance does not mean great effect or automatically favorable decision.

---

How to interpret a frequentist confidence interval at 95%? <!--anki:6330313635323635663539613431626362643534653664386333346364326337-->
?
A valid **procedure** would produce intervals containing the actual parameter in 95% of the sampling plane repeats. After observation, this is not a probability of 95% assigned to the fixed parameter within this particular interval.

The interval reflects the uncertainty due to sampling according to the assumptions chosen. It does not automatically cover collection bias, false labels or new population. A very narrow interval can therefore accurately describe a measurement that does not answer the right question.

---

Why compare two models on the same cases with a paired bootstrap? <!--anki:3561393263656665373738353430323562613063313138353064373863623366-->
?
The **Pairing** exploits the fact that the same question can be difficult for both models. Resample the same indices for their two results and recalculate the difference retains this dependency.

By resampling each model separately, we lose the common information. Choose the relevant independent unit: document, user or client, rather than each token. The bootstrap estimates the uncertainty for the represented protocol; it does not repair a contaminated test or an easy case sample. For the time, preserve dependencies with a suitable method.

---

Why 10,000 messages from 100 Users are not 10,000 Independent observations? <!--anki:3839666662323831373966353433353962363863303232623731316562663464-->
?
A user's messages share preferences, context, and sometimes memory. Treating them as independent can **underestimate uncertainty**, especially if the experience assigns a variant per user.

Choose a metric and analysis that is compatible with the assignment unit: aggregation by user, group-based method or resampling of users. Also specify the weighting: the average user and the average message do not represent the same target. A very active user should not dominate the result by accident.

In a bootstrap per user, pull users and then keep their messages together: resampling messages in isolation would break this dependency.

---

Calculation: Does zero failure on 300 trials allow to announce a lower risk than 0.1%? <!--anki:3137303038393761333632613462623439663963373835316539313636323331-->
?
**No.** For independent, representative and constant risk Bernoulli tests, a one-sided upper bound to 95% after zero failure is:
```text
p_max = 1 − 0,05^(1/n)
For n = 300: p_max ≈ 0.00994 ≈ 1%
Approximation: 3/n; aiming for 0.1% requires about 3,000 safe testing.
```
This calculation does not guarantee anything about a scenario that is absent from the tests; almost identical variants of the same question do not necessarily provide as much information as independent cases.

The protocol must be fixed before the tests: multiplying the observations to obtain a favorable limit changes the inference. For grouped tasks or variable risks, prefer an analysis compatible with these dependencies and this follow-up.

---

What risk does the search for the best result create among 20 tests? <!--anki:3937313162656165326133633434623638303530316139656434323565313036-->
?
Under 20 true null assumptions, with independent tests each at the threshold of 5%, the probability of at least one false positive is **1 − 0.95²⁰ ≈ 64%**.

Define the family of comparisons and the objective before the analysis. For example, Bonferroni uses a threshold of 0.05 / 20 = 0.0025 to control the family risk, without requiring independence. It can be conservative; an exploratory analysis must be distinguished from a confirmation on new data.

---

Do not confuse: no significant difference and equivalence? <!--anki:6232346235343439363038313462316238303165366164336238303435666634-->
?
A non-significant test may simply lack **power**. It does not demonstrate that the systems are equivalent. An equivalence or non-inferiority approach defines an acceptable margin in advance and uses a suitable procedure.

To replace one model with another cheaper, fix the tolerable quality loss and examine the relevant boundary of the difference interval. With an interval from −8 to +3 points, a cost gain does not make it possible to assert that the quality is kept to within one point.

---

How to choose the randomization unit of an AI experiment? <!--anki:6561363937623036623037383435316462343638333131303438633135646137-->
?
Choose the smallest unit limiting the **contamination between variants**: user if history persists, team if responses are shared, sometimes request for a task with no lasting effect. The analysis must respect this grouping.

A stable assignment avoids changing a user's variant during conversation. Interactions between units can still violate assumptions, for example if teams share generated documents. Randomization by user is a common choice, not a sufficient rule in all products.

---

What is a sample mismatch ratio in an A/B test? <!--anki:3461313736393834306564303434356361333635356164373663373737616163-->
?
A **SRM** is a statistically suspect discrepancy between the observed numbers by variant and the expected assignment ratio. A test designed at 50/50 should not be naively interpreted if the collection removes more users from an arm.

Examine randomization, eligibility, exposure, telemetry and filters before comparing business results. A minuscule gross deviation is normal; evaluate it by workforce. Correcting volumes by weighting without understanding their origin may leave a selection bias intact.

Example: If B-arm errors prevent telemetry from being sent, its remaining users appear to be artificially more satisfied.

---

Why does a before/after improvement not prove the causal effect of a new model? <!--anki:6434306138326366303238313434343462316566613436383833616232343231-->
?
Between periods often change **population, season, interface or business procedure**. An increase in the resolution rate may come from simpler requests rather than the deployed model.

A randomized contemporary control group helps to isolate the effect, if the assignment and no-interference assumptions are plausible. Otherwise, documenting competing factors and assumptions of a quasi-experimental method. A correlation between an offline score and the product result provides an index, not evidence that any increase in this score will create value.

---

Why does checking a p-value every day and then stopping as soon as it switches to 0.05 change the risk of error? <!--anki:6564643966326165313463643432613939356636376339393536623230623232-->
?
The **Repeated tests with opportunistic shutdown** There are many opportunities to see a positive result. The threshold of a test intended for a fixed workforce does not automatically control the risk of this sequential protocol.

Set the strength and stop rule before the test, or use a suitable sequential method with guarantees that match the expected follow-up. Report duration, intermediate readings and monitored metrics. Continue until meaningfulness and then show only the last p-value masks the selection process. A product constraint may stop the experiment, but the inference must take this into account.

---

How can a global average reverse the comparison between two better models per segment? <!--anki:6531363461623337326537333466316662313266636335623763336263323165-->
?
If the models are evaluated on **different proportions of easy and difficult cases**, the aggregation can reverse the ranking: this is the Simpson paradox.

Compare to a common population, publish the results by segment and apply a weighting corresponding to the target use. An overall increase may come from a change of mix rather than from the model. Do not choose the segments after the fact only to justify the preferred result.

---

Why aren't a thousand answers from ten documents necessarily worth a thousand independent observations? <!--anki:3365646130306535643339613462363738383366346532393665303539333235-->
?
Errors can be **correlated within each document**: same format, vocabulary, or parsing problem. Treat all responses as independent then underestimate uncertainty.

Separate training and testing by document or source when appropriate, and use an estimate that respects these groups. Increasing the number of questions per document does not provide the same information as increasing the number of independent documents.

---

## Scenarios

Scenario: the variant wins over the messages, but the experiment has been randomized by user. How do you check the result? <!--anki:3163653465626537633336373431626138343030376636393234326235336439-->
?
1. **Identify target unit**: average message or average user.
2. **Check staffing and assignment**, before calculating the gain.
3. **Analyse the dependency** between messages from the same user.
4. **Recalculate uncertainty** at the group level, with explicit weighting.
5. **Report gain, interval, and guardrails**, without selecting the most favorable method.

**Trap**: artificially increase the sample size by counting each message as independent.

---

Scenario: a team announces a reliable agent to 99.9% after 300 tasks without error. What do you answer? <!--anki:6636363934386436346566633437323362363333373236373030636335616566-->
?
1. **Definite failure**: business result, permissions, external effects, and abandoned cases.
2. **Check for representativeness and independence** of the tasks tested.
3. **Calculate the risk limit**: approximately 1% to 95% under binomial assumption.
4. **Dimension the sequence** according to the intended risk, without changing the protocol after each result.
5. **Add targeted scenarios** for rare risks, and then plan for monitoring and retreat.

**Trap**: Turn an observed absence of incident into a universal reliability guarantee.

---

Scenario: among 40 prompts, only one progresses by two points on the historical test. Can it be deployed? <!--anki:3366393030326464393061373466323039333663636239303535653537303661-->
?
1. **Consider this game as selected**: it was used to choose the winner.
2. **Review paired errors** and changes by segment.
3. **Document all tests**, as well as the cost and metrics sought.
4. **Confirm on an independent game** sized for useful gain, or a suitable confirmatory protocol.
5. **Decide according to value and uncertainty**, and then apply the usual deployment controls.

**Pip**: Present the maximum score of a search as an independent measure of generalization.

---

## Sources
- [NIST — interpretation of confidence intervals](https://www.itl.nist.gov/div898/handbook/eda/section3/eda352.htm)
- [NIST — intervals for a proportion](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm)
- [NIST — multiple comparisons and Bonferroni](https://www.itl.nist.gov/div898/handbook/prc/section4/prc473.htm)
- [SciPy — bootstrap and pairing](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html)
- [Microsoft Research — mismatch sample ratio diagnosis](https://www.microsoft.com/en-us/research/articles/diagnosing-sample-ratio-mismatch-in-a-b-testing/)
- [Microsoft Research — inference after selection in A/B testing](https://www.microsoft.com/en-us/research/uploads/prod/2021/06/PostSelectionKDD2021.pdf)

- [ASA — p-value interpretation principles](https://www.amstat.org/asa/files/pdfs/p-valuestatement.pdf)
- [Microsoft Research — protocol, metrics and interference](https://www.microsoft.com/en-us/research/articles/patterns-of-trustworthy-experimentation-pre-experiment-stage/)
- [Microsoft Research — independent unit and A/B test analysis](https://www.microsoft.com/en-us/research/publication/trustworthy-analysis-of-online-a-b-tests-pitfalls-challenges-and-solutions/)
- [Microsoft Research — Experimentation and Causality](https://www.microsoft.com/en-us/research/publication/online-experimentation-at-microsoft/)

## Connections
- [[94-evals-methodology|Evaluation methodology]] — moving from a score to a justified decision
- [[97-evals-online-ab-testing|A/B testing]] — check the validity of the online protocol
- [[172-ml-validation-metrics|Validation ML]] — compare models without selection bias
- [[178-causal-inference-decisions|Causal Inference & Product Decisions]] — distinguish accurate estimate and valid conclusion
- [[60-010-inference-load-benchmarks|LLM Load Benchmarks]] — measure capacity without hiding files and failures
- [[90-012-langfuse-prompts-experiments|Langfuse — Prompts, datasets & experiences]] — decide from experiences
- [[117-continuous-training-pipelines|Training pipelines]] — compare a challenger to the champion
- [[90-014-agent-skill-evaluation|Evaluating Agent Skills]] — decide on a skill eval in few cases
- [[00-moc-ai-engineering|MOC AI Engineering]]
