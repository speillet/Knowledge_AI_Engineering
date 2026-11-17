# Agentic Workflow Patterns — Flashcards
Tags: #flashcards #ai-engineering #agents #workflows #patterns #llm
<!-- summary: chaining, workflow routing versus model and tool selection, ambiguous and multi-intent requests, handoffs, parallelization, evaluator-optimizer, plan-and-execute versus ReAct, Reflexion, explicit branch contracts and bounded improvement loops. -->


## Composition and routing

Which basic patterns can compose LLM calls into a workflow? <!--anki:794e6f356a4c61743f5b-->
?
Common patterns include:

1. **Chaining**: fixed stages pass validated outputs onward.
2. **Routing**: select a specialized branch.
3. **Parallelization**: run independent work, then aggregate.
4. **Orchestrator-workers**: dynamically decompose and delegate a task.
5. **Evaluator-optimizer**: assess a candidate and revise it within limits.

These patterns can be combined; they are not a mandatory sequence or a ranking of sophistication. A workflow can contain a bounded agentic step. Choose the structure from dependencies, acceptance criteria and measured outcomes rather than the number of model calls.

---

What is prompt chaining? <!--anki:63754e5a7b244d33377b-->
?
Prompt chaining splits work into **predefined stages**, such as extracting facts, drafting a summary and checking it against the source. Each stage supplies input to the next.

Use explicit gates to reject invalid intermediate output and retain references to the original evidence. Otherwise a small extraction error can propagate through fluent downstream text.

If each of three stages succeeds with probability 0.98 conditional on earlier success, end-to-end success is `0.98³ ≈ 0.941`. Chaining improves controllability, but reliability still depends on stage quality, recovery and the final acceptance check.

---

What does routing mean in a workflow? <!--anki:433c21753f315e2a483c-->
?
A router selects a **specialized processing branch** from the request and relevant state. The decision can come from code rules, a classifier or an LLM.

For support requests, branches might handle order tracking, returns and technical troubleshooting. Each can have its own prompt, tools and acceptance conditions.

Include explicit treatment of ambiguous and unsupported requests. Route selection is a decision about where work goes; it is not proof that the chosen branch completed the task. Evaluate the full outcome after routing, not only the category label.

---

Do not confuse: workflow routing, model routing and tool selection? <!--anki:3530303835336337323534633462643239353437643033396636316231333434-->
?
**Workflow routing** chooses a processing branch. **Model routing** chooses a model or backend for a call. **Tool selection** chooses an operation to request.

One support task can use all three: route a ticket to the delivery branch, choose a model that supports its tool contract, then request `tracking_status`.

These decisions optimize different things and may be implemented in different components. A correct branch can still choose the wrong tool; a strong model can still be placed in an unsuitable workflow. Keep their decision reasons and evaluations separate.

---

How should a workflow router handle ambiguous or unsupported requests? <!--anki:3637326437666138383032613438656439373861306632616235316339333034-->
?
Provide a **defined abstention path** instead of forcing every input into a known branch. Ask a targeted question, use a general handler or escalate according to the task contract.

If “close it” could mean closing a ticket or cancelling an order, a high-similarity route is insufficient. Resolve the intended object and effect before an irreversible step.

Thresholds and score gaps should be validated on realistic confusing examples. Confidence in a category is not authorization to act, and unsupported requests must not silently enter the nearest available specialist.

---

How should routing handle a request containing several intents? <!--anki:6264333035643066663961623431313839383162333864326564633866643637-->
?
Determine whether the intents are **separable, dependent or conflicting**. A single-label classifier can lose part of the request if it routes only the most prominent intent.

“Cancel my order and email confirmation” has a dependency: confirmation should reflect the cancellation result. “Track order A and order B” may permit independent lookups.

Represent required outcomes explicitly, dispatch the necessary work and aggregate their statuses. Report partial completion when only one intent succeeds. Do not mark the entire request complete because one specialist finished its branch.

---

What contract should every routed workflow branch expose? <!--anki:3935323466363432346331643432306439626462363338613265663564613064-->
?
Define its **accepted inputs, required context, permitted effects, output shape and completion conditions**. Also specify how it returns missing information, failure or an unresolved operation.

A refund branch should distinguish a prepared proposal, a submitted refund and a confirmed refund. The parent workflow needs those distinctions to decide whether to continue, wait or stop.

Preserve task identity and relevant evidence across the boundary. Branch-local success is only one part of the parent task's acceptance criteria; delegation does not transfer responsibility for the overall result.

---

Do not confuse: delegating a subtask and handing off control? <!--anki:3033333033613539353331303437356561663864383130326232636535306433-->
?
**Subtask delegation** normally returns a result to a supervising controller. A **handoff** transfers responsibility for the next interaction to another handler; exact semantics vary by framework.

For example, a billing specialist may return an invoice analysis to a support agent, or it may take over the conversation to resolve a billing issue.

Define ownership, return conditions, carried state and remaining budget. A handoff is not task completion. Bound transfers and detect cycles so two handlers cannot repeatedly send the same unresolved request back to each other.

---

Do not confuse: sectioning and voting when parallelizing LLM calls? <!--anki:47335a5b4c435a6f5958-->
?
**Sectioning** runs different independent subtasks, such as summarizing separate documents. **Voting** runs multiple attempts at the same task and combines their outputs under a declared rule.

Sectioning can reduce elapsed time when dependencies and capacity allow it. Voting can improve results only when the candidates and aggregation provide useful complementary information; correlated mistakes can defeat it.

Account for aggregation, incomplete results and total cost. A validator that must inspect a generated draft cannot validate that draft before it exists, even if both calls are technically launched together.

---

How should you choose between a workflow and an agentic step? <!--anki:6f6678437a726b25366f-->
?
Use a **workflow** for known stages and explicit branches. Consider an **agentic step** when the useful next action depends on discoveries that are hard to enumerate in advance.

An invoice process may stay deterministic except for finding missing supporting evidence. Bound that investigation with permitted tools, a budget and a return contract.

Compare against the simpler baseline. Neither an agent nor a workflow is automatically cheaper or more reliable; measure success, recovery, latency and cost for the actual workload. High-impact decisions still need explicit controls regardless of the chosen pattern.

---

## Planning, feedback and stopping

What is the evaluator-optimizer pattern? <!--anki:6f513979335932596924-->
?
A generator produces a candidate, an evaluator checks it against **explicit criteria**, and a revision step uses actionable feedback to improve it.

Stop when acceptance criteria are met, the revision budget is exhausted, or further attempts fail to make useful progress. Keep the best eligible candidate rather than assuming the last is best.

Code tests, factual checks and a calibrated rubric can provide feedback. A model simply declaring its own answer good is weak evidence. The pattern is useful only when evaluation can identify deficiencies and revisions can plausibly correct them.

---

Do not confuse: plan-and-execute and ReAct? <!--anki:446b3f67597d5a3d334d-->
?
**Plan-and-execute** creates an explicit plan before carrying out steps, with defined opportunities to revise it. **ReAct** interleaves decisions, actions and observations as work proceeds.

The distinction concerns how planning and feedback are organized. ReAct does not require a large model for every action, and a plan is not necessarily complete or fixed.

They can coexist: plan major milestones, then use an observation-driven loop within each milestone. Compare adaptation, planning overhead and execution cost empirically; neither pattern is universally cheaper or more reliable.

---

What is the Reflexion pattern described by Shinn et al.? <!--anki:43766a393a407a512d26-->
?
**Reflexion** uses feedback from an attempt to produce a textual reflection that can guide later attempts. It stores lessons in the agent's context or memory rather than updating model weights through gradient training.

For a coding task, a failed test can lead to a concrete note about a mistaken assumption. The next attempt uses that feedback alongside the task.

The reflection itself may be wrong. Keep the underlying evidence, validate subsequent results and bound retries. Repeating self-critique without reliable feedback can reinforce a false explanation rather than correct the task.

---

When should you avoid an evaluator-optimizer loop? <!--anki:70363f3e4a7e4a215d56-->
?
Avoid it when **evaluation cannot distinguish useful improvement**, revision adds unacceptable latency, or a simpler validation-and-escalation path already meets the requirements.

Shared model biases can make a generator and judge agree on the same error; using different models is not an automatic cure. Test the evaluator against independent references or adjudicated examples.

Measure benefit by revision count and include the cost of judging. If another iteration mostly changes wording or exploits the judge, stop and repair the feedback rather than extending the loop.

---

Why should an evaluator-optimizer retain the best eligible candidate? <!--anki:3064373864333466376237613435653438666364303263616337636134613833-->
?
A revision can improve one criterion while **breaking another requirement**. The last candidate is therefore not necessarily the best usable result.

Store candidates with their evidence, scores and hard-constraint checks. First exclude ineligible candidates, then compare the remaining ones under a declared rule.

For a product description, a slightly higher tone score cannot compensate for a prohibited claim. At the stopping limit, return the best acceptable candidate or report that none qualifies. Do not silently label the least-bad invalid result as a success.

---

Why define a minimum improvement in an evaluator-optimizer loop? <!--anki:3534353761626465623131653433613339383738626434636438336364623966-->
?
It prevents **cosmetic revisions and judge noise** from sustaining an unproductive loop. Define meaningful improvement, a finite attempt budget and non-negotiable eligibility checks.

Use a progress measure relevant to the task, such as resolving a factual error, rather than accepting any increase in an arbitrary score. Confirm small gains when evaluator variance is material.

Stagnation is a stopping reason, not evidence of completion. If the best candidate still fails a required condition, return a limited or escalated outcome instead of lowering the acceptance standard.

---

Calculation: a revision loop requires all hard checks, a score of at least 0.90 and at most three revisions. Candidate A passes with 0.87; B scores 0.93 but fails a hard check; C passes with 0.89. What is the result after the limit? <!--anki:6136343539343664643561633438363138373061373262356165356334306530-->
?
**No candidate meets the full acceptance rule.** B is ineligible despite its higher score. Among eligible candidates, C is better than A, but 0.89 remains below the required 0.90.

Stop at the limit and preserve C as the best eligible partial result for review. Report that acceptance was not achieved; do not silently lower the threshold or continue with an unbounded fourth revision.

The thresholds are synthetic. In a real system, justify them against task outcomes and evaluator uncertainty before using them to control completion.

---

## Implementation and numerical reasoning

How can chaining, routing and parallelization be implemented without an agent framework? <!--anki:4867683c232863727074-->
?
Ordinary functions can express the control flow. This illustrative Python sketch assumes the named application functions already exist:

```python
import asyncio

async def respond(ticket):
    route = await classify(ticket)
    if route == "ambiguous":
        return request_clarification(ticket)
    draft, input_risk = await asyncio.gather(
        draft_response(ticket, route), inspect_input_risk(ticket)
    )
    if input_risk.requires_review:
        return escalate(draft, input_risk)
    return await validate_draft(draft, ticket)
```

The parallel calls both consume the ticket; the later validator consumes the completed draft. Add deadlines, bounded recovery and persistent state where required. `gather` itself does not define cancellation, retry or business-completion semantics.

---

Calculation: a chain requires all ten steps to succeed. Each independently succeeds with probability 0.95, with no recovery. What is the task success probability? <!--anki:51284f54214b6a7a7c36-->
?
```text
P(all ten succeed) = 0.95^10 ≈ 0.5987
P(at least one failure) ≈ 0.4013
```

Under these assumptions, roughly 60% of tasks succeed. Improving each step to 0.99 gives `0.99^10 ≈ 0.9044`.

Independence is a mathematical assumption, not a property of agent traces. Shared bad evidence can correlate failures. Shorter paths, better steps and effective recovery may help, but a retry is useful only when it can resolve the cause without duplicating unwanted effects.

---

Calculation: three independent binary classifiers each have an 80% probability of being correct. What is their majority-vote accuracy? <!--anki:3062663931623331356234393437383562663763373630623534653039316233-->
?
A majority is correct when exactly two or all three are correct:

```text
P(correct majority) = 3 × 0.8² × 0.2 + 0.8³
                    = 0.896 = 89.6%
```

The calculation assumes independent correctness events, identical individual accuracy and no abstentions. Three calls sharing a false premise may make the same error and violate those assumptions.

Measure joint errors, aggregation behavior and total cost on representative tasks before treating repeated model calls as a reliability improvement.

---

## Scenarios

Scenario: an autonomous claims agent succeeds on 78% of requests, but the business process always has four fixed stages. What do you propose? <!--anki:6c42675b522672606b61-->
?
1. **Map the stages** and identify any genuinely variable investigation.
2. **Build a workflow baseline** for classification, extraction, eligibility checks and response.
3. **Add explicit branch contracts and gates**, including clarification and escalation.
4. **Keep adaptive investigation bounded** where it shows a measured benefit.
5. **Compare on the same requests**, including cost, completion and failure recovery.

**Trap**: repeatedly prompting an agent to obey a fixed process that would be clearer in code.

---

Scenario: marketing rejects 20% of generated product descriptions for tone, length or prohibited claims. How do you design a revision loop? <!--anki:4c313c6c243e38355869-->
?
1. **Define acceptance criteria**, separating objective restrictions from subjective tone.
2. **Check deterministic conditions in code** and validate any model-based rubric against reviewed examples.
3. **Provide actionable feedback** tied to actual violations.
4. **Set revision and stagnation limits**, retaining the best eligible candidate.
5. **Measure acceptance and cost on held-out descriptions**, escalating when no candidate qualifies.

**Trap**: letting a high tone score override a prohibited claim.

---

Scenario: a support router sends a ticket to billing, billing sends it to technical support, and technical support sends it back. How should the loop stop? <!--anki:3238623561646263626665663466306262616231326466663166656365356134-->
?
1. **Record the transfer history and unresolved requirement** under one task ID.
2. **Check branch responsibilities** and whether required context was lost.
3. **Enforce a shared handoff limit** and detect repeated transfers without new evidence.
4. **Request specific missing information or escalate** to an owner who can resolve the boundary.
5. **Report a waiting or limited outcome**, preserving progress and avoiding a false completion claim.

**Trap**: giving each specialist a fresh budget whenever control changes hands.

---

## Sources

Review of 17 November 2026: pattern distinctions, branch contracts, handoffs and explicit acceptance and stopping rules. Numerical examples and application state conventions are synthetic.

- [Anthropic — Building effective agents](https://www.anthropic.com/research/building-effective-agents).
- [Yao et al. — ReAct](https://arxiv.org/abs/2210.03629).
- [Shinn et al. — Reflexion](https://arxiv.org/abs/2303.11366).
- [Python documentation — asyncio task execution](https://docs.python.org/3/library/asyncio-task.html). The sketch is not a complete recovery implementation.

## Connections
- [[31-agent-fundamentals|Agents]] — workflow or agent, ReAct
- [[32-tool-calling|Tool calling]] — requesting and executing an operation
- [[36-agent-orchestration|Orchestration multi-agents]] — orchestrator-workers and subagents
- [[41-code-nocode-automation|Automation]] — the same patterns in no-code
- [[44-langgraph-fundamentals|LangGraph]] — implement these graphs persistently
- [[82-routing-llm|Routing LLM]] — the routing side models
- [[95-llm-as-judge|LLM-as-a-judge]] — the loop evaluator
- [[98-agent-debugging|Debugging agents]] — know which step fails
- [[49-coding-agents|Code Agents]] — Use and Integrate Code Agents
- [[00-moc-ai-engineering|MOC AI Engineering]]
