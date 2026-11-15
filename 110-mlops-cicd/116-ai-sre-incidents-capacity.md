# SRE — Incidents & capacity for AI services — Flashcards
Tags: #flashcards #ai-engineering #mlops #sre #incidents #capacity
<!-- summary: SLI user, error budgets, burn rate, multi-window alerts, bounded queues, admission, backup capability, time propagation, incident management, rollback, RTO and RPO, postmortem and recovery, RTO and RPO compliance calculation, boot-up dependency, drive-service isolation, backlog resorption calculation, ML impact after restoration, recovery load, recovery exercises. -->


Why is a 200 HTTP status not sufficient as SLI for an AI service? <!--anki:3635323732333063663032383435633261333464373137376137633665346238-->
?
HTTP 200 indicates a protocol success, not necessarily a **useful and timely** response. Set eligible events, success, and user-level window.

Example: on 1,000 eligible requests, 990 arrive in HTTP 200, but 40 of these responses are empty or out of time; the success of this contract is **950/1,000 = 95%**, not 99%.

Separate this SLI from the estimated quality on an annotated sample, with coverage and uncertainty. A fallback only counts as a success if it complies with the product contract; a wait response is not automatically a resolution.

---

Calculation: How many failures does a SLO of 99.9% allow on one million eligible queries? <!--anki:6230353962613665323066613437376261666466363162653333363966316365-->
?
The budget is worth **1,000,000 × (1 − 0.999) = 1,000 failed requests**. With 700 failures already counted in this window, there are still 300 events in the budget.

This SLO is based on requests, not directly on downtime. A breakdown during a peak consumes more than a breakdown during a downtime. Future traffic and window slippage change the budget; a policy must specify how these changes influence delivery decisions.

---

Calculation: what burn rate for 2% of failures with a SLO of 99.9%? <!--anki:6335613061333137663963313432633662356334633964353839656338343339-->
?
The **burn rate** compares the observed failure rate to the allowed rate: **0.02 / 0.001 = 20**. At this constant rate, with consistent traffic and a full initial budget on 30 days, it would be consumed in **30 / 20 = 1.5 day**.

This delay is a projection, not a prediction of failure. It changes with traffic, errors already counted and the window selected. Linking the alert to the consumption of the budget avoids an arbitrary threshold identical for all services.

---

Why combine a short and a long window in a burn rate alert? <!--anki:3838633662346539353238363437356562356630306362623561646335666439-->
?
The **long window** confirms a significant budget consumption; the **short window** checks that the problem is still active. Require both can avoid waking up the on-call for an incident already completed.

Additional rules detect fast failure and slow degradation. Adapt thresholds to traffic and response time, and then test their behavior on known incidents. A small number of requests makes ratios unstable: the service may require probes and a specific alert strategy.

---

Do not confuse: backpressure and load shedding? <!--anki:6361656431366339653033393432613262616164643439326638363131303230-->
?
**backpressure** slows down or limits the output of upstream work when downstream saturates. **load shedding** explicitly refuses or abandons part of the load to protect the remaining service.

An unlimited queue does not solve either: it can accumulate tasks already useless. For an AI service, use bounded queues, tokens quotas, deadlines and priorities. Communicate the refusals and count their user impact; masking them in the statistics would give an artificially favorable SLO.

---

Calculation: a queue receives 30 tasks per second and processes only 20; how much accumulates in two minutes? <!--anki:3831313332343830373134633435306538333532623036316236313938393830-->
?
Under constant throughput and no downtime, the queue increases by **(30 − 20) × 120 = 1,200 tasks**. If the arrivals stop, the server will take **60 seconds** to process this stock at the same throughput.

If the arrivals stay at 30 per second, the queue continues to grow. Adding storage does not solve the capacity deficit. It is necessary to increase the service, reduce the admission or decrease the work per task, with priorities and a time limit accepted by the product.

---

Why should a backup provider be tested under the toggle load? <!--anki:6531346435636635326466663433376339363634623839333639643936336631-->
?
A **help** must support the load transferred with the same useful contracts: identity, formats, tools, deadlines and authorized data. A correct response to a single call does not prove this ability.

Perform failover with representative traffic, available quotas, cold cache and common dependencies. Check what remains if DNS, gateway, registry or identity system also falls; two providers are not independent of the entire application. Plan admission and degraded mode if the backup capacity is less. After return, reconcile uncertain operations and observe user signals, not to mention any backup response as a success.

---

Why propagate a global deadline to the stages of an agent? <!--anki:3530653465313534336237653439306262633736383030316637353661646634-->
?
A **End to end deadline** limits the time still useful for the user. Each step and retry consumes the rest, instead of receiving its maximum timeout again.

If three steps each have 30 seconds, the task can take much longer than the budget produced. Spread the time remaining to the queues, tools and vendors that allow it; before a new attempt, check that it can still serve the decision. Cancel or reconcile the in-flight jobs according to their effects. The client-side expiration does not automatically stop a remote write, and an expired task must not remain billable without follow-up.

---

What to do first during an AI incident affecting users? <!--anki:6439643935393961326330323463653061346263646630613233663730373239-->
?
**Reduce impact and coordinate response**: qualify the scope, appoint an incident manager, apply verifiable mitigation, and keep a time-stamped log. Distribute technical diagnosis and communication to avoid inconsistent competing actions.

A rollback, write tool shutdown, or degraded mode may be preferable to an immediate search for the complete cause. Keep the necessary evidence without releasing sensitive data. The return to normal is seen by user signals, not just by a successful restart.

---

Why does a model rollback not necessarily restore the AI service? <!--anki:3764316166643039643232653431386461316636633031323562616331323933-->
?
The behavior also depends on the **prompt, tokenizer, index, tool schema, configuration, and data**. Returning to previous weights alone may leave an incompatible index or irreversible migration in place.

Version the useful set, document the compatibility and repeat the return procedure. External effects already performed require reconciliation or compensation; undoing them is not a property of the software rollback. Check after toggles the quality, queues pending and the processing of tasks started under the old configuration.

Example: embeddings of the same size but from another model remain incompatible. Returning to generator weights alone does not repair this index.

---

Do not confuse: RTO and RPO for an AI application? <!--anki:3439663163353563633762653465313839343835313836623039336634646539-->
?
**RTO** is the interrupt recovery time target; **RPO** represents tolerable data loss expressed in duration. Resuming in one hour does not mean retrieving all events until failure.

Define objectives by state: corpus, rebuildable index, agent checkpoints, and business effects log. A backup is only useful if restore, keys, permissions, and dependencies work together. Measure actual recovery during an exercise and document deviations from objectives.

Example: An RPO of 15 minutes may allow the loss of recent checkpoints, not necessarily those of payments already accepted. These statements require separate objectives.

---

Calculation: a failure destroys the data of the last 12 minutes and the service returns after 45 minutes. Do we respect RPO 5 min and RTO 1 h? <!--anki:6363373462356533313736353436373662663433343535376638356534363561-->
?
The **RTO** is respected: recovery takes 45 minutes, below the target of one hour. The **RPO** is not: 12 minutes of lost data exceeds the accepted five minutes.

Specify which data and functions are covered: status of agents, business operations, evidence and indexes can have different objectives. A service once again accessible may still be unable to reconcile its actions. Test restoration and business consistency, not just restarting processes.

---

Why don't an already loaded inference and a cold start have the same registry dependencies? <!--anki:3238626562356633316432383463323362396666343938393030333433326133-->
?
A service that has **loaded its model** may continue to predict during a registry failure, if its contract does not require remote resolution on each call. A new replica may remain blocked due to lack of metadata or artifacts.

Test these two states: stable service, restart, scale-out and restore. Provide pinned references, controlled cache and validity rules; do not bypass a revocation or serve an unverified artifact to gain availability. A healthy prediction API does not prove that the ability can be rebuilt after the loss of already hot processes.

---

Why isolate training and inference resources even if they use the same model? <!--anki:3831376531326636343762373432333039306333316461353432343866626331-->
?
The **Training** Can saturate GPU, CPU, network and storage for hours; the inference must meet a user deadline. Sharing without quota can make a normal retraining a production incident.

Defining pools, priorities or resource envelopes, then test the simultaneous peaks. Include data download, checkpoints and weight reading, who sometimes ask for common dependencies despite GPU Separated. Sharing can remain profitable with adapted admission and pre-emption, but the identical model does not make their load profiles interchangeable. Connecting retraining planning, SLO and cost of reserve capacity.

---

Calculation: After an outage, 9,000 tasks wait; 20 new arrive per second and the service completes 30/s. What is the ideal time to clear the queue? <!--anki:6530633837383164306337393462383161353736396132373165616466376537-->
?
The **net catch-up capacity** is `30 − 20 = 10 tasks/s`. The delay therefore requires `9 000/10 = 900 s`, either **15 minutes**, under these assumptions.

Divided by 30 would forget about new arrivals. If service and arrivals equalize, the delay does not decrease; if arrivals dominate, it increases. The calculation assumes comparable tasks, constant throughputs and no expiration or resumption. Also consider age of items, useful delays and priority classes: finding a normal throughput does not mean that all old requests can still produce a valid result.

---

Do not confuse: Technical recovery and end of impact assessment of an ML incident? <!--anki:3437366430366262333834333433356362326232336537386465653239343336-->
?
**Technical recovery** provides the service in its operational contract.**Impact analysis** identifies the decisions, people and systems affected during degradation, and then the necessary corrections.

A model that is available again may have left false scores in a batch table or actions that have already been executed. Use versions, periods, decision IDs, and logs to delineate this perimeter. Provide for appropriate recalculation, reconciliation, or business processing, with separate handlers if necessary. Close the availability alert does not automatically close these actions; keep tracking and verify that a recommissioning does not propagate corrupt results again.

---

Why can disaster recovery cause a second failure of an AI service? <!--anki:3331626336333933363063303465363562336463646439306233323766633239-->
?
The simultaneous return of customers and workers releases **a backlog plus new requests**, while caches are cold and dependencies still fragile.

Gradually reopen the admission, distribute the rework and prioritize the useful tasks. Measure the ability to resorption beyond the current traffic. Replay all expired tasks can consume the reserve without bringing value; apply their expiration and cancellation policy.

---

Why does a successful backup not prove the ability to restore an ML service? <!--anki:3832336262373161353465393431386362343562653862393963393665313136-->
?
Restore depends on **integrity, keys, versions, and external dependencies**. A restored base without its artifacts or tokenizer does not restore the service.

Run an isolated exercise up to validated predictions, measure duration, and compare lost data to objectives. Include registry, configurations, and rights. The presence of backup files is only one step in this proof.

---

## Scenarios

Scenario: The GPU looks small, but users wait for 45 seconds and the queue grows. How do you react? <!--anki:3661656463396430323033363436623439663335636166393363623563623464-->
?
1. **Decompose latency**: Waiting, Retrieval, Provider, Generation and Tools.
2. **Compare arrivals and service**, with age of tasks and distribution of tokens.
3. **Born admission** and remove expired tasks according to their business contract.
4. **Isolate the bottleneck**: external quota, CPU, network or application blocking.
5. **Check user-level recovery** and emptying the queue.

**Pip**: add GPU while flow is limited elsewhere.

---

Scenario: after a failure, the backup model responds, but executes tool calls incorrectly. What do you do? <!--anki:3834643766356132383231313433653839643334663333356137613434323434-->
?
1. **Suspend risky effects** and offer an explicit degraded service.
2. **Identify affected tasks** with runtime versions and logs.
3. **Check the actions already taken**, before any relaunch.
4. **Return to a validated configuration** or limit rescue to playback.
5. **Add a tool compatibility check** and a toggle exercise before reactivation.

**Trap**: count HTTP 200 as recovery while the business result is incorrect.

---

Scenario: the same saturation incident returns every month despite postmortems. What do you change? <!--anki:3032663335626632636236343436366139303663653862643334393962353663-->
?
1. **Review technical and organizational factors**, without reducing the analysis to human error.
2. **Choosing verifiable actions**: Bounded admission, alerting, or removing a fragile dependency.
3. **Assign responsibility and deadline** for each priority action.
4. **Replay the failure scenario** to verify that the action reduces the impact.
5. **Follow the execution of the plan** and arbitrate the reliability work with the product.

**Field**: close the postmortem as soon as the document is written, without checking for corrections.

---

## Sources
- [Google SRE — Define and Implement SLO](https://sre.google/workbook/implementing-slos/)
- [Google SRE — alerts based on SLO](https://sre.google/workbook/alerting-on-slos/)
- [Google SRE — error budget policy](https://sre.google/workbook/error-budget-policy/)
- [Google SRE — Overload Management](https://sre.google/sre-book/handling-overload/)
- [Google SRE — to manage incidents](https://sre.google/sre-book/managing-incidents/)
- [Google SRE — postmortems and corrective actions](https://sre.google/sre-book/postmortem-culture/)

- [AWS Well-Architected — Recovery Goals and Tests](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/plan-for-disaster-recovery-dr.html)

- [MLflow — Metadata, Artifacts and Tracking Server](https://mlflow.org/docs/latest/self-hosting/architecture/overview/) — distinguish boot dependency and service already loaded.

## Connections
- [[142-llm-reliability-resilience|Reliability & resilience]] — switch mechanisms to their exploitation
- [[64-inference-metrics-slo|Metrics & SLO]] — connect capacity and user experience
- [[112-model-cicd|CI/CD models]] — rollback and artifact compatibility
- [[147-ai-technical-leadership|Technical Leadership]] — responsibilities and follow-up of corrections
- [[60-011-inference-capacity-scheduling|Capacity & scheduling]] — connect memory, budgets and payload under load
- [[150-016-data-observability-lineage|Observability, lineage & data exploitation]] — react to warranty breaches and validate trade-ins
- [[118-ml-artifacts-registry-releases|Artifacts, registry and releases ML]] — production contracts and verifications
- [[119-prediction-contracts-features-batch|Prediction contracts, features and batch]] — production contracts and verifications
- [[00-moc-ai-engineering|MOC AI Engineering]]
