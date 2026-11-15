# LangGraph — Recovery, Concurrency & Evolution — Flashcards
Tags: #flashcards #ai-engineering #agents #production
Verified on: 9 October 2026 — API cited against official documentation; limits spelled out in maps.
<!-- summary: durability sync/async/exit, pending writes, external effects, interruptions, thread concurrency, reducers, subgraphs, migrations and recovery diagnostics, determinism of decisions during replay, leases and fending, retention of checkpoints. -->


Do not confuse: LangGraph checkpoint and business transaction? <!--anki:3363396132633461616334643439346639636339643337353264376462643830-->
?
A **checkpoint** records the progress of the graph. A **business transaction** renders atomic the changes supported by its storage system. Both are usually not validated together.

If a refund succeeds and the process dies before the checkpoint, the node can re-request it. Use a stable operation identity and service-side deduplication, or reconcile its status. Putting the action in a task makes it easier to resume without removing this failure window.

---

How to choose between LangGraph sync, async and exit durability modes? <!--anki:3564343365396664613530663464383961353535313134326463393261386638-->
?
**`sync`** waits for the checkpoint to write before proceeding; **`async`** overlaps persistence and next step; **`exit`** persists at graph output, including error or scheduled interruption.

The compromise concerns the cost of persistence and the work recoverable after crash. Example: `graph.invoke(entree, config, durability="sync")`. In a sequential chain stopped during the step 9, `sync` can resume from the checkpoint following the step 8; `exit` does not guarantee these intermediate backups. No mode makes an external service transactional. Test modes with the backend and envisaged failures.

---

What happens if another branch of the same super-step fails? <!--anki:3532373334353035303231373439306662333336386630643264373162386336-->
?
With appropriate persistence, the **pending writes** keep the results of the super-step's completed nodes. Upon recovery, these nodes do not necessarily have to be restarted: the remaining work can resume.

Example: A, B and C run in the same super-step; A and B succeed, C fails on a network error. After `graph.invoke(None, config)`, only C is restarted. It is necessary to distinguish a recorded result from an external effect whose registration did not succeed. Do not deduce from this mechanism a single universal guarantee of execution.

---

Why should a LangGraph node containing interrupt be able to restart? <!--anki:3331333363616538363435613435666638373731366163643836643062346461-->
?
The resume reruns the node from its beginning before rendering the human response to the corresponding **`interrupt`**, so previous operations can be replayed.

Example: Recalculating a discount from a modified rate while waiting may apply a different amount than the approved one. Persist the exact proposal, version, and unit before the interruption; verify on resuming that the approval is still for that proposal.

Then execute the action in an idempotent step. Do not capture the interrupt signal with general error processing. Test resume in a new process and change the data while waiting.

---

Why not reorder interrupts in an already suspended LangGraph node? <!--anki:6633383838643766396165333437333438346533623933303738663035373638-->
?
Recovery values are associated with interruptions according to their execution order in the node.
```python
def valider(state):
    montant_ok = interrupt("Validate the amount?")   # Answer No. 1
    iban_ok = interrupt("Confirmer l'IBAN ?")        # Answer No. 2
```
If a new version swaps these calls, a folder suspended on the IBAN receives the validation of the amount as an answer to the IBAN question.

Keep the code path compatible for pending executions, or explicitly terminate/migrate them before deploying. Using separate steps and versioned proposals makes tracking easier. Deploying new code does not remove old, persistent states.

---

How to process multiple pending LangGraph interrupts simultaneously? <!--anki:6232346431373435633539363430616561646461396335613536316265343961-->
?
Identify **each interrupt** and attach the response to the correct request; recent APIs accept a match between interrupt identifiers and resume values.
```python
state = graph.get_state(config)
responses = {i.id: decision_humaine(i.value) for i in state.interrupts}
graph.invoke(Command(resume=responses), config)
```
Do not equate a global “yes” to the approval of all branches.

The application checks the owner, rights, version and expiration of each proposal. One approved branch can advance while another waits, depending on the graph. Test disordered approvals, duplicates and partial refusals on the version of the chosen runtime.

---

How do I retrieve a LangGraph graph after an error without submitting a new request? <!--anki:3438303766373064653663643461376439636139633061383439333337306439-->
?
Reload the same **`thread_id`**, inspect its status and then resume the pending work. For error recovery, invocation with `None` can continue the execution; a human interrupt uses `Command(resume=...)`.

```python
config = {"configurable": {"thread_id": dossier_id}}
snapshot = graph.get_state(config)
# After diagnosis of a failure, and with the same storage:
result = graph.invoke(None, config=config)
```

Do not rebuild the initial entries and inject them blindly: this can start a new round or accumulate messages again. Distinguish between error, interruption and completed execution.

Also check the version of the graph and the exclusivity of the recovery on this thread. Two workers with the same state can compete; the checkpointer does not guarantee, on its own, the idempotency of the business system.

---

Why is a LangGraph checkpointer not enough to serialize two queries on the same thread? <!--anki:6330643362343966643762663437366439396439333132306663303537343731-->
?
It keeps checkpoints, but the admission policy of **competing executions** is also runtime and enforcement. Two requests can read an old state and produce incompatible decisions.

Choose an explicit rule: reject, queue or replace the previous request. The agent server of LangGraph exposes it with `multitask_strategy`: `reject`, `enqueue`, `interrupt` or `rollback`. In home hosting, ensure this coordination between replicas; a Python lock protects only one process. The reducers of the graph do not alone regulate this concurrency between invocations.

---

How to design a LangGraph reducer for reliable parallel collection? <!--anki:3964373335323535616462663431326438616439383165323363383139346430-->
?
Set the merge **semantic** before the function: concatenation, set, update by identifier or explicit conflict. If the order should not count, look for an associative and commutative operation; if duplicates are possible, provide a stable identity.

Two results with the same identifier but conflicting content should not be silently overwritten:
```python
def fusion_par_id(a: dict, b: dict) -> dict:
    conflits = {k for k in a.keys() & b.keys() if a[k] != b[k]}
    if conflits:
        raise ValueError(f"conflicting results: {conflicts}")
    return {**a, **b}

class Etat(TypedDict):
    results: Annotated[dict[str, dict], fusion_par_id]
```
Storing by ID and then sorting for display is more robust than a list ordered by the arrival of branches.

---

Why avoid mutations in a LangGraph node? <!--anki:6233323231326532636662313435353939653730633361613239636238356233-->
?
Returning an explicit **update** makes it easier to reason about reducers and snapshots. Editing a list of the status and then returning it with a concatenation reducer can reintroduce elements already present.

```python
# A new contribution, not the entire accumulated list:
def noter(state):
    return {"notes": ["Control completed"]}
```

Test two successive contributions and two parallel branches; check the elements, their identity and their useful order, not just the final length.

---

How to choose the memory of a LangGraph subgraph? <!--anki:3835393364376666643936353436373439656339376532613439323832633066-->
?
Decide whether the delegated agent should **Go back to every call** Or keep your own history. Default (`checkpointer=None`), The subgraph inherits the parent's checkpointer and leaves for each call. `sous_graphe.compile(checkpointer=True)` keeps its history from one call to another in the same thread.

A point sub-agent must not arbitrarily retrieve a previous folder. A persistent specialized assistant requests stable identifiers and namespaces. Test repeated and parallel calls: Sharing a memory can create conflicts or leaks if the perimeter is not explicit.

---

How to change the state scheme of a LangGraph graph in production? <!--anki:3539643263336230323163643437343462623664643464643430396565643030-->
?
Historical checkpoints remain readable by **new code**: provide default values, optional fields, or explicit migrations. A TypedDict annotation does not convert already stored states: declare `canal: NotRequired[str]` and read `state.get("canal", "web")` lets old folders resume.

Adding an application version to the contract, keeping old fixes, and testing for their recovery. Removing a field or renaming a node that is still expected by a broken thread requires a compatibility policy. Also provide the rollback path: the old code may ignore or misinterpret the new state.

---

How do I set up a LangGraph node? <!--anki:3334376465383130656164323437633339386338383332396566636534666534-->
?
Set up a **`RetryPolicy`** for targeted transient errors, in addition to network delays and overall budget. Do not systematically retry a validation or permission error.

```python
from langgraph.types import RetryPolicy
builder.add_node(
    "read_source", read_source,
    retry_policy=RetryPolicy(max_attempts=3, retry_on=ConnectionError),
)
```

The three attempts include the initial. Check the client's internal retrievings and idempotency before treating a write error as a simple unavailability.

The node budget includes sleep between attempts and time of internal clients. Test a persistent failure: the execution must finish in the global deadline and report an external operation still uncertain instead of replaying it blindly.

---

Why does the LangGraph recursion limit not replace an agent budget? <!--anki:6665643733613362383263383463376362303637613430663830326535626436-->
?
It limits **super-steps**, whereas a single step can make a lot of parallel calls, process a long context or wait a long time, so it does not represent an amount or a delay. In LangGraph 1.2.14, version of the support workshop, its default value reaches 10,007 super-steps: setting it, for example `config={"recursion_limit": 40}`, remains useful but is not enough.

Collect ceiling of active branches, deadline and call counters/tokens. Before a delegation, reserve a shared budget rather than give each branch the total budget. At exhaustion, produce an explicit partial result and keep the necessary elements for diagnosis.

---

Calculation: a 24 graph throws independent branches of 2 s each, with at most 6 active branches. Without overhead or retry, what is the minimum time to complete all branches? <!--anki:3165343066383066613030663461646439333838653135376465613664396335-->
?
**⌈24 / 6⌉ × 2 = 8 seconds**, i.e. four waves. Without limit of concurrency and with unlimited capacity, they would take 2 seconds.

The cap protects quotas and resources but increases the wait. In practice, uneven durations, withdrawals and throughput limits can lengthen the total time. Measure active calls and pending tasks separately; reducing parallelism does not automatically reduce the number of tokens consumed.

---

How do I prevent a LangGraph time travel from replaying real effects during debugging? <!--anki:6438313533383466623730363434646561333965393238623330653632316534-->
?
Replay in an environment where **writing tools are simulated** or strictly allowed for testing. Copy only the necessary data and keep a link to the original case.

A checkpoint describes a past state of the graph; it does not restore the balance of an account or the state of a third-party service. Or `graph.invoke(None, old.config)`, with `old` taken from `get_state_history`, reruns the following nodes, tools included. Even if the idempotency keys protect some actions, a new path could generate others.

---

Why should a LangGraph replay stabilize decisions based on time or chance? <!--anki:3832376533396539633534343435666262616534643332626536393538376165-->
?
A **Resumed** can rerun the code from an earlier point. If a condition reads the clock or draws a new random number, it can choose another branch and no longer match the results already persisted.

In the API concerned, isolate non-deterministic operations in tasks whose result is retained. Maintain the order of interruptions and test the resumption of each branch. Idempotence remains necessary for a failure between external effect and persistence: recording a result does not retroactively make these two operations atomic.

---

Why can an expiring lock let two workers take over the same LangGraph thread? <!--anki:6563373234323231626435353436356461633762343335393633303562336639-->
?
A slow worker can **continue after his lease expires**, while a second becomes owner. The lock alone does not prevent the first from writing late.

A fending mechanism assigns a growing generation to the owner; the storage or write service rejects the older generations. This protection must be applied to the relevant border, not just saved in the state of the graph. Test long breaks, network partitions, and late recovery of the old worker.

---

How to choose a LangGraph checkpoint retention policy? <!--anki:6631383164306266656430663437323762373238386463306463373265323630-->
?
Starting from **recovery, debugging, and data retention needs**. Keeping each state forever can accumulate private documents, tool outputs, and old permissions.

Distinguish active, suspended, and terminated threads; preserve dependencies needed for a supported recovery. Test restore and delete with the chosen checkpointer. A deleted checkpoint can render an old recovery identifier unusable: the application must respond explicitly, without silently recreating an empty task.

---

## Scenarios

Scenario: your LangGraph node creates a credit note, then crashes before the checkpoint is saved. After resuming, two credit notes exist. What do you change? <!--anki:3364353231383037663938313437336138383133303632303266383631343462-->
?
1. Identify the window between business validation and graph persistence.
2. Generate the identity of the operation before the effect and keep it on repeats.
3. TB deduplicate the action atomically by the service of the assets.
4. Test a crash precisely after the business validation, then resume from storage.
5. Reconcile duplicates already produced according to business rules.

**Trap**: believing that switching from `async` to `sync` makes the API transactional assets with the checkpoint.

---

Scenario: two messages arrive at the same time in the same LangGraph thread and each changes the basket. How do you avoid a response based on an expired state? <!--anki:6666613261643133616462623462656661653934643566643234363234303239-->
?
1. Set whether the second request waits, is rejected, or replaces the first.
2. Apply coordination to all workers, with a version of the business state.
3. Check this version before actually writing the cart.
4. Test two competing invocations and the expiration of the coordination mechanism.

**Piece**: Add a list reducer while the conflict involves two independent executions.

---

Scenario: a deployment renames the LangGraph trust node while 400 folders wait for a human response. How do you prepare for migration? <!--anki:3566393761616536343764313462643862316339646634383735323031656233-->
?
1. Inventory the pending states and versions before the change.
2. Keep the old path or set a controlled migration to the new one.
3. Test historical checkpoints with approval, refusal and expiration.
4. Provide a compatible rollback and monitor rollbacks after deployment.

**Trap**: Validate only new folders created after the update.

Keep an anonymized sample of checkpoints covering versions already deployed. Test external effects and proposal identifiers after migration; a graph that starts correctly on a new state does not prove this compatibility.

---

## Sources
- [LangGraph — checkpointers, pending writes and durability](https://docs.langchain.com/oss/python/langgraph/checkpointers)
- [LangGraph — interruptions and recovery rules](https://docs.langchain.com/oss/python/langgraph/interrupts)
- [LangGraph — graphs and migrations](https://docs.langchain.com/oss/python/langgraph/graph-api)
- [LangGraph — retry policies](https://docs.langchain.com/oss/python/langgraph/use-graph-api)

- [LangGraph — determinism and replay in the Functional API](https://docs.langchain.com/oss/python/langgraph/functional-api) — targeted deepening of the 12 November 2026; educational examples are built for this review.

- 14 November Supplement 2026 — Checkpoints and Persistent Memory: [LangGraph — persistence](https://docs.langchain.com/oss/python/langgraph/persistence).

## Connections
- [[44-langgraph-fundamentals|LangGraph — Fundamentals]] — reducers and super-steps
- [[45-langgraph-production|LangGraph — Production]] — persistence and interruptions
- [[149-delivery-idempotency-concurrency|Delivery & Idempotence]] — external effects and concurrent runs
- [[140-010-transactions-outbox-sagas|Transactions & sagas]] — transactional borders
- [[140-011-agentic-application-architecture|— Architecture & Life Cycle]] — exploit persistent states
- [[90-013-agent-testing-recovery|Agents — Contracts, failures & recoveries testing]] — inject failures
- [[00-moc-ai-engineering|MOC AI Engineering]]
