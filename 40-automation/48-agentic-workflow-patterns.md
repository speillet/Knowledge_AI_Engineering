# Agentic Workflow Patterns — Flashcards
Tags: #flashcards #ai-engineering #agents #workflows #patterns #llm
<!-- summary: Prompt chaining, routing, parallelization (sectioning, voting), valuator-optimizer, plan-and-execute or ReAct, Reflexion, chain reliability calculation, workflow or agent, implementation without framework, retention of the best eligible candidate, correlated voting, stop improvements. -->


What are the basic patterns for dialing LLM calls? <!--anki:794e6f356a4c61743f5b-->
?
The taxonomy popularized by Anthropic (“Building effective agents”, 2024), from the simplest to the most autonomous:
1. **Prompt chaining**: a series of fixed steps
2. **Routing**: a referral to a specialized branch
3. **Parallelization**: multiple simultaneous calls, then aggregation
4. **Orchestrator-workers**: a LLM dynamically cuts and delegates ([[36-agent-orchestration|orchestration]])
5. **Evaluator-optimizer**: a product call, another review, iterates

Beyond that, the **Agent** Choose your own steps ([[31-agent-fundamentals|agents]]).

---

What is prompt chaining? <!--anki:63754e5a7b244d33377b-->
?
Split a task into **fixed steps**, each feeding the following: Extract → translate → summarize. A **gate** in code can block an invalid output before propagation ([[11-advanced-prompt-engineering|Decomposition]]).

Each step becomes more targeted and testable, but the string is not automatically more reliable. Example: if each step succeeds with a probability of 98% conditional to previous successful steps, three steps together succeed at about **94.1%**.

Keep references to the initial data to identify deformations, test the final result and predict the failure of a gate. The gain in controllability is paid in calls and latency.

---

What is pattern routing? <!--anki:433c21753f315e2a483c-->
?
A first call (or classifier) **categorizes** the entry and sends it to a **specialized treatment**: prompt, tools or model specific to the category. Example: refund, technical question and claim do not have the same prompt.

It avoids a quick catch-all that degrades all categories, and allows simple cases to be sent to a **small model** ([[82-routing-llm|routing LLM]]).

Predicting an “ambiguous or off-scope” branch: forcing each ticket into a known category masks the router’s errors. Measuring end-to-end success, because an excellent specialist does not compensate for a wrong orientation.

---

What are the two forms of parallelization of LLM calls in a workflow? <!--anki:47335a5b4c435a6f5958-->
?
- **Sectioning**: splitting a task into **independent subtasks** processed in parallel. Example: one call responds, another checks the safeguards at the same time
- **Voting**: run **the same task multiple times** and aggregate responses. Example: three security reviews of a code, alert if at least one finds a problem

The first reduces **latency**, the second increases **reliability** ([[65-probabilities-sampling|self-consistency]]).

---

What is the evaluator–optimizer pattern? <!--anki:6f513979335932596924-->
?
A **loop**: a call **generates**, a second **evaluates** according to explicit criteria and returns a review, the first **corrects**, until validation or maximum number of turns.

It works when two conditions hold: **clear evaluation criteria** and feedback that **improves the answer**, such as translation, writing or code that must pass tests. Without verifiable criteria, the loop goes in circles ([[95-llm-as-judge|judge]]).

---

Do not confuse: plan-and-execute and ReAct? <!--anki:446b3f67597d5a3d334d-->
?
- **ReAct**: the model **decides one action at a time**, observes, then decides the next. Flexible, but each step requires a call to the big model
- **Plan-and-execute**: a scheduler first produces **a complete** plan, which (often smaller) implementers follow, with **replanning** if a step fails

The second is cheaper and repeats before execution, but adapts less quickly to the unexpected ([[31-agent-fundamentals|ReAct]]).

---

What is the Reflexion pattern (Shinn et al.)? <!--anki:43766a393a407a512d26-->
?
After a **failed** test, the agent writes a **natural language review** of what went wrong, and keeps it in memory for the next attempt. Proposed by Shinn et al. (2023), it improves tasks to **verifiable return**: code with tests, puzzles.

Without a reliable failure signal, the model "reflects" on imaginary errors ([[39-agent-memory|Memory]]).

---

Calculation: what probability of success of a chain of 10 steps all necessary, each succeeding with probability 0.95, under independence and without catching up? <!--anki:51284f54214b6a7a7c36-->
?
If the failures are independent and not caught:
```text
0.95^10 ≈ 0.60 → 40% tasks fail somewhere
0.99^10 ≈ 0.90
0.95^20 ≈ 0.36
```
Hence three levers: **fewer steps**, **check gates** that catch up with errors, and more reliable steps. This is also why long agents are difficult to make reliable ([[114-reproducibility-variance|pass^k]]).

Real steps can share a cause of failure, such as a wrong document, so independence is a calculation assumption, not a property of agents. A retry only improves the string if it can correct the error without reproducing its unwanted effects.

---

How to choose between workflow and agent? <!--anki:6f6678437a726b25366f-->
?
- **Steps known in advance**: workflow (chaining, routing). Predictable, testable, cheaper
- **Number of unpredictable steps**, path that depends on the results: agent
- **Expensive error**: workflow, or agent with human approval

Anthropic Rule: Start with **the simplest** option that works, and only add range if it **measures better** ([[94-evals-methodology|evals]]).

Hybrid example: fixed workflow to check an invoice, bounded agent to find a missing part. Autonomy is about the search, not the authorization of payment.

---

When not to use evaluator-optimizer? <!--anki:70363f3e4a7e4a215d56-->
?
- **No verifiable criteria**: the judge validates or rejects randomly, and the loop adds cost without gain
- **Critical Latency**: Each turn adds a generation and evaluation on the critical path
- **First answer already good** in the vast majority of cases: it is better to evaluate only doubtful cases
- **Same model, same context** to generate and criticize: it tends to **validate its own mistakes**

Measure the gain per turn: often, the second round brings the essentials.

---

How to implement chaining, routing and parallelization LLM without a framework? <!--anki:4867683c232863727074-->
?
These are some **functions**: a LLM call, Python code between calls, `asyncio.gather` to parallelize.
```python
async def respond(ticket):
    category = await classer(ticket)                    # routing
    draft, risk = await asyncio.gather(           # Parallelization
        rediger(ticket, category), verifier_risk(ticket))
    if risk.high:
        return escalader(ticket)                         # porte
    return await review(draft)                       # chaining
```
A framework becomes useful for **persistence**, recovery, and human supervision ([[44-langgraph-fundamentals|LangGraph]]).

This extract assumes already defined functions and an import of `asyncio`. The two parallel calls must be independent. Add timeouts, cancellation and exception handling; `gather` does not constitute a recovery policy. Saving the result of each useful step makes it possible to diagnose a failure without restarting the whole task.

---

When should an evaluator-optimizer loop keep the best candidate instead of the last? <!--anki:3064373864333466376237613435653438666364303263616337636134613833-->
?
A **review** can improve a criterion while degrading an already correct answer, so the last candidate is not necessarily the best.

Keep each proposal with its score, its violations and its cost. Accept a review only according to a defined rule: imperative constraints satisfied then measurable improvement. Stop on budget, stagnation or success, and keep the best eligible candidate. If the evaluator is noisy, confirm the useful deviations; multiply the revisions can only over-adapt the text to his judge.

---

Calculation: three independent classifiers each have 80% probability of correct response on a binary task. What reliability for their majority vote without abstention? <!--anki:3062663931623331356234393437383562663763373630623534653039316233-->
?
The majority succeeds if exactly two or all three succeed: **3 × 0.8² × 0.2 + 0.8³ = 0.896**, or **89.6%**.

Three calls to the same model sharing a false premise can produce the same error; their vote then does not follow this calculation. Measure joint errors and cost before deploying a voting strategy.

---

Why fix a minimal improvement in an evaluator-optimizer loop? <!--anki:3534353761626465623131653433613339383738626434636438336364623966-->
?
Without a threshold, the loop can continue **reformulations without useful gain**, guided by the judge's noise. Define a minimum progress, a maximum number of tests and an eligibility condition.

Keep the best eligible candidate according to the grid and then confirm the gains on independent cases. A small increase in the automatic score does not necessarily justify the cost of a new call. An improvement in style should not compensate for a loss of accuracy.

---

## Scenarios

Scenario: your team has built a stand-alone agent to process claims. It succeeds 78% cases, is expensive and its errors are unpredictable. But the business process always has the same four steps. What do you propose? <!--anki:6c42675b522672606b61-->
?
1. **Find out** that the path is known: the autonomy of the agent does not bring anything here, it adds variance
2. **Rewrite in workflow**: categorize request, extract fields, check eligibility by code rules, write response
3. **Add doors**: mandatory fields present, consistent amount, human escalation beyond a threshold
4. **Keep an agent only** for the “atypical case” branch, if it exists
5. **Compare** on the same eval game: pass rate, cost per request and variance ([[96-evals-rag-agents|evals d'agents]])

**Trap**: Add instructions to the agent to follow the four steps, instead of coding them.

---

Scenario: a generator of product descriptions has 20% of rejections by the marketing team (tone, length, forbidden mentions). You are considering an evaluation-optimizer loop. How do you design it? <!--anki:4c313c6c243e38355869-->
?
1. **Write the criteria** of the marketing in verifiable form: length, prohibited mentions (in code), tone (judge)
2. **Check first in code** everything that can be checked, and reserve the judge by tone ([[95-llm-as-judge|judge]])
3. **Calibrate the judge** on 100 descriptions already accepted or rejected by marketing
4. **Limit to 2 or 3 turns**, and climb to a human beyond
5. **Measure** rejection rate and cost per description before and after

**Trap**: Let the same prompt generate and self-assess, then be surprised that it validates everything.

---

## Connections
- [[31-agent-fundamentals|Agents]] — workflow or agent, ReAct
- [[36-agent-orchestration|Orchestration multi-agents]] — orchestrator-workers and subagents
- [[41-code-nocode-automation|Automation]] — the same patterns in no-code
- [[44-langgraph-fundamentals|LangGraph]] — implement these graphs persistently
- [[82-routing-llm|Routing LLM]] — the routing side models
- [[95-llm-as-judge|LLM-as-a-judge]] — the loop evaluator
- [[98-agent-debugging|Debugging agents]] — know which step fails
- [[49-coding-agents|Code Agents]] — Use and Integrate Code Agents
- [[00-moc-ai-engineering|MOC AI Engineering]]
