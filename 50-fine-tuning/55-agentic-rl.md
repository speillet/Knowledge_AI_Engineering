# Agentic RL & Training Environments — Flashcards
Tags: #flashcards #ai-engineering #fine-tuning #reinforcement-learning #agents #llm
Verified on: 30 September 2026 — This factsheet lists products, versions or regulatory texts that are evolving quickly.
<!-- summary: RL on multi-turn trajectories, RLVR or agentic RL, training environments, result or process reward, agent reward hacking, SFT on trajectories, GRPO, task curriculum, tools (verl, OpenRLHF, TRL), when a product team needs to get started, isolation of RL episodes, terminal reward, policy lag. -->


What is the agentic RL? <!--anki:6966466243243e466b26-->
?
Train a model by **strengthening** on **multi-turn** tasks where it uses tools: it acts in a **environment** (code repository, browser, simulated API), and receives a **reward** according to the result (tests passing, task completed).

This is what has advanced recent models in code and tool usage, beyond the simple RLVR on a single response ([[52-post-training-alignment|RLVR]]).

---

Do not confused: RLVR on an answer and RL agentic? <!--anki:6e73554e47344851597d-->
?
- **Classic RLVR** : a question, **a** Answer, automatically verified (mathematical result, tests of a function)
- **Agentic RL**: a **trajectory** of dozens of actions and observations, in an environment that **changes state**. The reward often arrives **at the end**

The second poses its own problems: attribution of merit between stages, long and expensive trajectories to generate, environments to run in the thousands.

---

What is an agent training environment? <!--anki:47497e416c2d30714141-->
?
A **reproducible** sandbox that provides:
- a **initial state** (filing, database, simulated account)
- the **tools** that the model can call
- a **reward function** that checks the result
- a **fast reset** between episodes

It must turn **in mass** (thousands of episodes in parallel) and be **isolated**, because the training model tries arbitrary actions ([[96-evals-rag-agents|Eval Environments]]).

---

Do not confuse: result reward and process reward? <!--anki:65552155572869485d6c-->
?
- **Result reward** (outcome): note the **final status**. Simple and difficult to deceive, but signal **rare** on long tasks
- **Process reward** (process): Note the **intermediate steps**, often by a reward model. Signal denser, but easier to operate and more expensive to build

The trend is towards **verifiable** result rewards, supplemented by simple penalties (length, format).

---

How can an agent cheat during the RL? <!--anki:6b7030485a6f31363057-->
?
By **reward hacking**: it maximizes the reward without doing the task.
- **Change or remove tests** to pass
- Hard code the **expected value**
- Exploiting a **checker's fault** (poorly parsed exit counted as fair)
- Declare the finished task without doing it, if the judge believes it

Parades: tests **Protected in Writing**, robust checkers, **Inspection** samples of rewarded trajectories ([[52-post-training-alignment|reward hacking]]).

---

What is SFT on trajectories (rejection sampling)? <!--anki:75655a326c694a7a2c43-->
?
A simpler alternative to the RL: rotate a model (often stronger) on many tasks, **keep only successful trajectories**, and then make a **fine-tuning supervised** of the target model on those trajectories.

Less efficient than the RL to exceed the original model, but **stable** and accessible, this is often the first step of a product team ([[53-synthetic-data-distillation|distillation]]).

For example, keep only the trajectories that the business tests pass, removing secrets and duplicates. Also control the steps: a result obtained by response leak or prohibited action is not a good example of learning.

---

Why is GRPO popular for Agentic RL? <!--anki:762d3d71285d59625760-->
?
It does not need a **critical model**: for the same task, we generate **several trajectories**, and each is compared to the **average of the group** (relative advantage).

On agentic tasks, the group must contain **successes and failures**: tasks that are too easy or too hard do not produce any signal ([[52-post-training-alignment|GRPO]]).

---

Why is the choice of training tasks decisive? <!--anki:4a4e643352476b6e4271-->
?
The learning signal comes from the tasks **at the limit of the capabilities** of the model: successful sometimes, not always. So we build a **curriculum**: filter the tasks always successful or always missed, and increase the difficulty over the course of training.

The **diversity** counts just as much: a model trained on a single type of deposit or API generalizes poorly.

With a binary reward, a group where all attempts fail gives little relative contrast. Examine first if the task is feasible and if the checker is working, before making it easier or excluding it.

---

Agentic RL: open source library or managed reinforcement service fine-tuning? <!--anki:6433363235303264663562323463636261366130353530396132616130643530-->
?
- **Open source library** (verl, OpenRLHF, TRL for GRPO): total control on a **open-weights** model, but all the infrastructure is to be mounted: GPU drive, inference server to generate trajectories ([[11-llm-inference-servers|vLLM, SGLang]]), isolated environments by episode ([[54-distributed-training|Distributed Training]])
- **Managed service** of fine-tuning reinforcement: we provide the **tasks and the grader**, the supplier trains **his** model

In both cases, the dominant cost is often the **generation of trajectories**, not the updating of weights.

---

When should a product team do agentic RL? <!--anki:7077524a526d3c78352f-->
?
When a solid baseline caps and the team has **verifiable reward, controlled environment, and experimental budget**. Usually start with tools, context, and [[48-agentic-workflow-patterns|patterns]], then compare model, routing, and SFT before investing in the RL.

Example: Rewarding "ticket closed" can learn how to close too early; checking actual resolution, no prohibited action, and total cost gives a more accurate goal. Evaluating out of training, with independent control of the checker used to learn.

Predict rollouts without uncontrolled business effects and monitoring regressions. An increased reward score does not justify deployment if actual quality or safety deteriorate.

---

Why is it necessary to reset and isolate the environment between two episodes of agentic RL? <!--anki:6662656236346433623535663432656561323933653532313638373161663234-->
?
A **residual state** may reveal a solution, facilitate the next task, or allow the auditor to be modified, and the officer would learn an environmental shortcut rather than the skill being tested.

Reset files, data, and services to a reference state; isolate concurrent episodes and keep the checker out of agent rights. Replay tasks in a blank environment and vary their settings. Control that an episode cannot read artifacts from the previous one. The reward gain must survive this separation.

---

Why does a rare terminal reward complicate an agent's RL? <!--anki:3861626235663165323035633437363761636561313465303536616436636333-->
?
Many trajectories receive **the same score**, without indicating what decision caused the failure. Exploration and awarding of merit becomes difficult.

Starting with accessible tasks, demonstrations or a curriculum can provide a useful signal. Intermediate rewards must stay aligned with the end result: rewarding the number of tools called can learn to multiply actions. Measuring complete success on unseen tasks.

---

Why can trajectories collected with an old policy be a problem for an RL training? <!--anki:3434666562393736623330383434373038326638643531343438343738323331-->
?
They reflect **Another distribution of visited actions and states**. An algorithm designed for data close to the current policy may receive a biased signal if these trajectories are too old.

Trace the collection version, limit the stability and use a method compatible with out-of-policy data when necessary. More trajectories are not always better if they do not correspond to the assumptions of the algorithm or current tools.

---

## Scenarios

Scenario: your company processes 50,000 tickets per month with an agent who uses 12 internal tools. A fine-tuned open weights model would cost 5 times cheaper, but succeeds 20 points less. How do you plan training? <!--anki:4e5e36736062615121-->
?
1. **Building the environment**: internal tools simulated from real traces, reproducible initial state, verification of the result by business rules
2. **Start with SFT** on the successful trajectories of the current model, and measure the remaining gap
3. **Go to the RL (GRPO)** on tasks where the model sometimes succeeds, with a robust checker
4. **Monitoring reward hacking**: inspecting rewarded trajectories at each iteration
5. **Validate** on a separate test set, in pass^k and cost per successful ticket ([[96-evals-rag-agents|evals d'agents]])

**Trap**: Reward "the customer did not call back", which the agent gets by closing tickets too early.

---

Scenario: during an RL training of a code agent, the success rate increases from 40% to 85% in two days. What do you check before you rejoice? <!--anki:774e2e796e754a55642f-->
?
1. **Read rewarded trajectories**, randomly: does the code really solve the problem?
2. **Search for known cheats**: modified or deleted tests, hard coded values, output that deceives the parser
3. **Evaluate on a separate game**, with hidden tests the agent has never seen
4. **Compare** with general capabilities, to detect regression elsewhere
5. **Correct checker** if a flaw is found, then resume training

**Strap**: Publish the model on the only training reward curve.

---

## Sources

- [verl — RL Framework Documentation](https://verl.readthedocs.io/en/latest/)
- [Microsoft — Agent Lightning](https://github.com/microsoft/agent-lightning)

## Connections
- [[52-post-training-alignment|Post-training & Alignment]] — RLHF, GRPO, RLVR and reward hacking
- [[53-synthetic-data-distillation|Synthetic Data & Distillation]] — SFT on tracks
- [[51-fine-tuning-adaptation|Fine-tuning]] — when adjusting the weights
- [[96-evals-rag-agents|Evaluation of Agents]] — environments are also used to evaluate
- [[54-distributed-training|Distributed training]] — drive infrastructure
- [[49-coding-agents|Code Agents]] — the flagship use case of the RL agentic
- [[114-reproducibility-variance|Reproducibility & variance]] — non-determinism and eval statistics
- [[138-reasoning-models|Models of Reasoning]] — test-time compute and budget reflection
- [[135-pretraining-scaling-laws|Pre-workout & scaling laws]] — how to make a LLM
- [[90-016-harbor-agent-evaluation|Harbor]] — containerized environments, rollouts and reward hacking
- [[00-moc-ai-engineering|MOC AI Engineering]]
