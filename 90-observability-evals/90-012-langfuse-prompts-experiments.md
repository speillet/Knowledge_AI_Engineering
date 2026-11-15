# Langfuse — Prompts, datasets & experiences — Flashcards
Tags: #flashcards #ai-engineering #agents #production
Verified on: 9 October 2026 — API cited against official documentation; limits spelled out in maps.
<!-- summary: labels and versions, prompt cache, fallback, promotion, evaluation games, comparable runs, missing scores, costs per achievement and feedback, confirmation game independence, absent scores, version cache. -->


Do not confuse: version and label of a Langfuse prompt? <!--anki:6132653866646365356530343433393639353338323563656432313331306364-->
?
A **version** identifies saved content; a **label** selects a version and can be moved, so `production` is a mutable reference, useful for promoting or removing a prompt.

Trace the version actually recovered, not just the requested label:
```python
prompt = langfuse.get_prompt("support-response", label="production")
prompt.version          # for example 14; switch it to generation with prompt=prompt
```
To reproduce an experience, fix the version and the rendered variables. A return of the label to an older version does not guarantee that all processes have already renewed their cache.

---

Why version the variable contract of a Langfuse prompt? <!--anki:3837646234303261363235643437626238616234623763633265363834393930-->
?
The template and the code that fills it share a **contract**: names, types and meanings of variables. Renaming `question` to `request` can break the application even if the prompt text looks better.

Test compilation, missing variables, and pre-promotion content: With the Python SDK, `prompt.compile(request=...)` on a template that waits for `{{question}}` does not throw any errors and sends `{{question}}` as is to the template. Link the change to the expected tool and output schemas. If older versions of the code remain deployed, maintain compatibility or coordinate the toggle.

---

Do not confuse: Langfuse registry cache and model prefix caching? <!--anki:6230643233623462626432323465363938666431663531653366353463666333-->
?
The **cache of the registry** avoids downloading the template on every call; the Python SDK keeps it 60 s by default. The **prefix caching** reuses inference calculations on a compatible prefix on the vendor or model server side.

The former reduces dependency on the registry and can delay an update; the latter can reduce prefill time or input cost. They have different keys, lifetimes, and metrics. A Langfuse hit cache does not prove any GPU compute gain.

---

How to make a quick rollback observable despite Langfuse caches? <!--anki:3231333264666633376632303436326462623938353034303438633465636239-->
?
Follow the **version actually used** by requests after moving the label. The Python SDK serves an expired version while it refreshes it in the background: each replica can respond with the old version beyond its cache time.

Set the acceptable propagation time, preload or invalidate according to the capacities selected and check multiple replicas. For an urgent correction, provide an application deactivation mechanism independent of the registry. A visible change in the interface does not mean an instantaneous toggling of all traffic.

---

What contract should be imposed on a rescue team if Langfuse is unavailable? <!--anki:3863356565376662666561653463373538663138643464646536393436356135-->
?
The fallback must be **prevalidated**, compatible with the expected variables, tools, and schemas, and then identified in the tracks.
```python
prompt = langfuse.get_prompt("support-response", label="production",
                             fallback="Answered only from the sources provided: {{question}}")
prompt.is_fallback      # True if the registry was unreachable and the cache empty
```
Test an empty cache start and unavailability after filling the cache.

For a sensitive task, proper refusal may be preferable to a generic improvised instruction. The fallback protects technical availability; it does not guarantee an equivalent quality. Measure its rate of use and the quality of the results obtained.

---

Why should a Langfuse experience fix more than the prompt? <!--anki:3035313633663562333364343465366338363566343438383064313730313635-->
?
The output also depends on the **model**, the tools, the corpus, the configuration and the initial state. Save their versions with the identity of the dataset and the evaluator, for example in `run_experiment(..., metadata={"model": "model-x", "corpus": "snap-2026-10-20", "tools": "v7"})`.

If two candidates do not have access to the same documents or if the second takes advantage of a memory created by the first, the comparison is biased. Build an independent fixture for each essay, while maintaining comparable conditions. The traces then help to explain the observed deviations.

---

How do I turn a failure record into a useful dataset item? <!--anki:6531633130623330376339383462366661643635333535343161386465366533-->
?
Extract one **Reproducible input**, the necessary data and the expected result or invariant. Remove the secrets, Check reuse rights and document what is missing to replay the tools.
```python
langfuse.create_dataset_item(dataset_name="regressions-support", source_trace_id=trace_id,
    input={"request": sanitized_request},
    expected_output={"invariant": "No having without approval"})
```

A raw conversation is not enough if it depends on a today modified command. Replace the mutable environment with a fix when possible. Keep the origin link in an authorized space, and prevent the expected response from being injected into the candidate's context.

---

Why keep a regression dataset and a representative dataset for agents? <!--anki:3832363764663666373265333438363739373830666361626230343464643937-->
?
The first contains known **significant failures**; the second reflects a target distribution of requests. They answer different questions: do not reintroduce a bug and estimate the expected performance.

Accumulate only the incidents produces a useful but unbalanced game. The representative game is renewed, for example 300 requests drawn each month randomly, stratified by segment, then frozen in a version. Present the results separately. Also reserve cases not used during the optimization to avoid choosing a prompt that memorizes the examples of review.

---

How do I attach a Langfuse score to the right level? <!--anki:3135646161666634343433313438653162656433646461666463323965663337-->
?
Choose the object corresponding to the **measured criterion**: observation for a tool, trace for an execution, session for a complete conversation. For example, `create_score(name="outil_correct", value=0, trace_id=t, observation_id=o)` refers to the faulty call, which an overall score would not allow to identify.

Set name, type, meaning, and version of the scale. A late human fix should reference the original object, not just the user's last request. Prevent duplicates if the score producer returns the same event after a network error.

---

Why distinguish zero score, absent score and reviewer error in Langfuse? <!--anki:6635643430623732393735303461373338316164333231366465313238323931-->
?
**Zero** It can be a verdict of failure. **Absent** means not evaluated; a **Error of Evaluator** This means that the judgment could not be calculated. Conflating them with false comparisons.

Publish evaluation coverage and errors with scores: "Average 0.8 on 150 cases evaluated on 200, i.e. 75% coverage, and 10 judge errors." If a candidate produces answers that fail the judge, silently exclude them may favor him. Set in advance the treatment of invalid executions and analyze their frequency by candidate.

Also follow the scoring delay: too early a comparison mixes temporary absence and permanent failure.

---

How do I change a judge without breaking historical scores? <!--anki:6232656333363865326132613465666539363735653837383336623266623561-->
?
Version **model, prompt, parameters, scale and parsing rules** of the judge, with each score. Make note of the same outputs by the two versions over a period of comparison.

Example: the new scale penalizes missing quotes; a drop from 0.8 to 0.6 can then come from the judge, not from a degradation of the agent. Separate the series and explain the break.

If you recalculate the history, keep the original score and recalculation version rather than overwriting the values. Controlling agreement with human annotations, limit cases, and coverage. An absent score or an evaluator error should not be turned to zero.

---

How to decide to promote a prompt with the Langfuse experiences? <!--anki:6431653166646365363338383431613562316462363535626438383864346566-->
?
Set before comparison of **acceptance criteria**: for example, no decrease by more than one point on a critical segment, zero authorization regression, cost-per-success under 0.10 € and unchanged p95. Compare the same cases, inspect regressions and consider uncertainty.

The best average score can hide a failure on the permissions or an increase in abandonments. After offline validation, gradually deploy and link the measurements in production to the version actually served. The experiment tool brings the data; the decision rule remains to be defined.

---

Calculation: on the same 200 files, candidate A costs 12 € and succeeds 160 files; B costs 15 € and succeeds 180. What are their costs per success, including the cost of failures? <!--anki:3338613335393339663136373438623861653362643533373034396530383136-->
?
**A: 12 / 160 = 0.075 €** by success; **B: 15 / 180 ≈ 0.0833 €**. Success rates are 80% and 90% respectively.

B succeeds more, but its cost per success is higher. The choice depends on the value of the additional files, latency constraints and acceptable errors. Excluding the costs of failures would make candidates appear artificially more economical.

---

How to prevent user feedback from manipulating the scores of an agentic application? <!--anki:6435663531316637316162343438373938336638396566373964393037303862-->
?
Attach feedback to an authenticated user's **execution**, limit the frequency, and set a replacement or deduplication rule. Do not freely accept an external `trace_id` as proof of ownership: `POST /feedback` only records a note if the trace belongs to the token's user, one note per trace, the last one replacing the previous one.

Separate satisfaction, factual correction and business success. Silence is not worth approval, and some users respond more often than others. Keep this feedback as a signal to cross with objective controls and targeted annotations.

---

Why keep a protected test outside of repeated experiments in Langfuse? <!--anki:3562306161366262306531393439376262643566643137613462373036333636-->
?
A **dataset consulted with each experiment** becomes a development tool, even if its name contains "test". The choices of prompts and models eventually adapt to its particularities.

Keep a development set to iterate and an independent evaluation to confirm the final decision. Version the cases, references and protocol, then plot the number of variants compared. Have the failures examined without copying their answers into the training examples. The experimentation tool facilitates comparisons; it does not guarantee their independence.

---

How do I verify that a prompt promotion is actually applied to all workers? <!--anki:6334356461353433336635393465633938333436643930383636363362343834-->
?
Trace **the resolved version for each call**, not just the requested label. Local caches can continue to serve the old version after moving a label.

Measure version distribution, test expiration and restart, and then confirm the toggle. For a controlled experience, resolve and fix an immutable version. A label change in the registry does not constitute proof of immediate change on all instances.

---

## Scenarios

Scenario: after rollback of the production label in Langfuse, some users still receive the old behavior. What do you check? <!--anki:3565393461396130356562623431323739343334636338363262323531636461-->
?
1. Read the version actually attached to the generations, by replica and period.
2. Check for caches, preloads and possible rescue prompts.
3. Check that all code paths use the expected registry.
4. Test the spread and monitor until the target behavior is returned.

**Trap**: Declare the completed rollback based solely on the label displayed.

Set the maximum expected propagation time and a test on each critical path. A label is a mutable reference; only the identifiers of the versions actually consumed can confirm that all instances have changed.

---

Scenario: a candidate wins five points in Langfuse but 20% of his evaluations are absent. Can we conclude an improvement? <!--anki:3137333733343833613539313431383561346636306330353234306435613561-->
?
1. Compare coverage and evaluator errors between candidates.
2. Examine absent cases and their possible association with invalid exits.
3. Apply the rule for non-evaluable executions, without masking them.
4. Restart repairable assessments and then compare the same cases with uncertainty.

**Trap**: Calculate the average only on the answers that the judge was able to read.

---

Scenario: the prompt improves on historical incidents but degrades simple demands in production. How do you rebalance assessments? <!--anki:3137633634643732313339623435376462336238343866396434623436373735-->
?
1. Keep incidents in a dedicated regression game.
2. Build a representative sample of current requests and their segments.
3. Report quality, cost and latency on both games.
4. Require critical guarantees while checking the performance of the usual traffic.

**Trap**: Remove difficult cases to beautify the average or test only them.

Setting the target weight before comparing variants and checking critical segments separately. An average of incidents and current traffic without announced proportions can change simply because the test set has been recomposed.

---

## Sources
- [Langfuse — prompt management](https://langfuse.com/docs/prompt-management/get-started)
- [Langfuse — cache and fallback prompts](https://langfuse.com/docs/prompt-management/features/caching)
- [Langfuse — datasets](https://langfuse.com/docs/evaluation/experiments/datasets)
- [Langfuse — scores via API and SDK](https://langfuse.com/docs/evaluation/evaluation-methods/scores-via-sdk)

## Connections
- [[91-langfuse-observability|Langfuse — Fundamentals]] — connect prompts, traces and scores
- [[90-011-langfuse-instrumentation-production|Langfuse — Instrumentation]] — origin and coverage of observations
- [[13-production-prompts|Prompt in production]] — release and promote contracts
- [[99-statistics-experimental-decisions|Statistics]] — decide from experiences
- [[95-llm-as-judge|LLM-as-judge]] — calibrate reviewers
- [[00-moc-ai-engineering|MOC AI Engineering]]
