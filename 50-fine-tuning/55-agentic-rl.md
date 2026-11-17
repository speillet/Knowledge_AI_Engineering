# Agentic RL & Training Environments — Flashcards
Tags: #flashcards #ai-engineering #fine-tuning #reinforcement-learning #agents #llm
Verified on: 30 September 2026 — This factsheet lists products, versions or regulatory texts that are evolving quickly.
<!-- summary: RL on multi-turn trajectories, verifiable rewards and agentic interaction, training environments, outcome and process rewards, reward hacking, SFT on accepted trajectories, group-relative advantages, task curricula, library or managed service, product readiness, episode isolation, sparse terminal rewards and policy lag. -->


What is agentic reinforcement learning? <!--anki:6966466243243e466b26-->
?
**Agentic RL** trains a policy on interactions with an environment: the model selects tool calls or other actions, receives observations and earns rewards tied to the task.

The trajectory includes several decisions and may change external state. Training must define resets, allowed actions, termination and how success is checked. A code task might reward a verified repository fix after multiple edits and test runs.

Compared with scoring a single completion, this makes credit assignment, rollout cost and environment isolation especially important. Success on a simulated task still needs validation under realistic deployment conditions.

---

Do not confuse: verifiable rewards and agentic interaction? <!--anki:6e73554e47344851597d-->
?
**RLVR** describes the source of a reward: an automated verifier checks a result. **Agentic RL** describes the interaction structure: multiple actions and observations unfold in an environment.

These categories overlap. A code agent can act over many turns and receive a verifiable reward from trusted tests. A single-response math task can also use RLVR without tool interactions.

The multi-step case adds changing state, delayed feedback and credit assignment. Do not infer that a reward is learned or verifiable merely from whether the policy is called an agent.

---

What is an agent training environment? <!--anki:47497e416c2d30714141-->
?
A training environment defines the **initial state, available actions, state transitions, observations, rewards and termination** for an episode. For a support task, this might include a simulated account, ticket history and tools for reading or updating records.

Use controlled resets and isolate effects between episodes. Record tool and dataset versions so a reward change can be traced to policy behavior or an environment change.

Rollout throughput matters at scale, but thousands of parallel episodes are not a defining requirement. Begin with reproducible small runs and inspect complete trajectories before increasing concurrency.

---

Do not confuse: outcome reward and process reward? <!--anki:65552155572869485d6c-->
?
An **outcome reward** scores a final result or state. A **process reward** scores intermediate decisions or steps. Either can come from learned judgments or explicit checks.

Outcome feedback can be sparse on long tasks; process feedback is denser but adds assumptions about which intermediate behavior is useful. Neither is inherently difficult to exploit.

For example, rewarding resolved tickets requires verifying resolution, not just a closed status. Rewarding the number of investigative tool calls can encourage pointless calls. Test each component against shortcuts and retain independent end-to-end evaluation.

---

How can reward hacking appear in an agent's training environment? <!--anki:6b7030485a6f31363057-->
?
An agent may obtain reward by **changing the evaluator or exploiting its assumptions** instead of completing the intended task. Examples include deleting tests, hard-coding leaked answers or exploiting a parser that interprets malformed output as success.

Keep trusted validation assets outside the agent's write permissions, test the checker with invalid outputs and inspect rewarded trajectories. Verify final external state instead of accepting the agent's claim that a task is complete.

A higher reward is useful only insofar as it tracks the intended outcome. Recheck previously trained checkpoints after discovering an exploit.

---

What is supervised fine-tuning on accepted trajectories? <!--anki:75655a326c694a7a2c43-->
?
Generate candidate trajectories, **retain those meeting a quality criterion**, and train the target model to imitate their actions. This is often called rejection-sampling fine-tuning when acceptance is driven by filtering sampled attempts.

It is a useful baseline before online RL. Performance depends on coverage, the generating policy and the acceptance check; there is no universal guarantee that it matches or stays below the generator on every metric.

Validate intermediate actions as well as final success. A trajectory that succeeds through leaked answers, unauthorized access or a corrupted checker is unsuitable supervision.

---

Why use group-relative advantages for agent trajectories? <!--anki:762d3d71285d59625760-->
?
Comparing several trajectories for the **same task and initial state** can provide a baseline without training a separate critic. It trades critic-related complexity for the cost of collecting several rollouts.

Useful relative signal requires differences in reward. With binary success rewards, mixed success/failure groups provide contrast; continuous quality rewards can differ even when all trajectories succeed.

Control environment resets and versions so reward differences reflect actions rather than different starting conditions. The absence of a critic does not eliminate credit assignment or the need to validate rewards.

---

Why does task selection matter for group-relative agent training? <!--anki:4a4e643352476b6e4271-->
?
With binary rewards, tasks the policy **sometimes solves** can provide within-group contrast. All-pass and all-fail groups have zero centered reward advantages; this observation does not imply that every RL method should discard them.

A curriculum can adjust difficulty as capabilities change. First check feasibility and verifier correctness, then preserve diversity across task families, repositories and tools. Filtering solely for immediate reward variance can neglect important rare tasks.

Evaluate on a fixed representative set, including difficult cases. Otherwise, an improving training curve may reflect easier task selection rather than better generalization.

---

When should agentic RL use an open-source library or a managed training service? <!--anki:6433363235303264663562323463636261366130353530396132616130643530-->
?
An **open-source library** offers control over compatible model weights, optimization and environment integration, while leaving distributed training, rollout infrastructure and maintenance to the team.

A **managed service** can reduce operational work, but its supported models, reward interfaces, tool loops and data constraints must fit the task. Support for single-response reward training does not automatically provide arbitrary multi-step environments.

Prototype one complete training and evaluation cycle before committing. Measure rollout generation, tool execution, reward computation and weight updates separately; the dominant cost depends on the workload.

---

When should a product team do agentic RL? <!--anki:7077524a526d3c78352f-->
?
Consider it when a strong baseline plateaus and the team has **meaningful rewards, controlled environments and an experimental budget**. First improve tools and context, then compare model selection, routing and SFT on accepted trajectories.

For support automation, rewarding closed tickets may encourage premature closure. Validate actual resolution, permitted actions and cost on held-out cases using checks independent of the training reward.

Run exploratory rollouts without uncontrolled production effects. Promote a checkpoint only if task success and regression criteria improve enough to justify training and operating costs.

---

Why must agentic RL environments be reset and isolated between episodes? <!--anki:6662656236346433623535663432656561323933653532313638373161663234-->
?
**Residual state** can leak a previous solution, make a later task easier or leave the evaluator modified. The policy may learn an environmental shortcut instead of the intended skill.

Reset files, databases and services to a declared starting state; isolate concurrent episodes and protect the checker. Verify that one episode cannot read another's private artifacts.

For example, a code task should not inherit an earlier rollout's patch or cached test answers. Replay successful policies in clean environments with varied task instances; the improvement should survive those controls.

---

Why does a sparse terminal reward complicate agentic RL? <!--anki:3861626235663165323035633437363761636561313465303536616436636333-->
?
Many unsuccessful trajectories receive **the same final score**, with little information about which action caused failure. Discovering a successful trajectory and assigning credit across its decisions both become difficult.

Demonstrations, accessible tasks or a curriculum can make useful behavior easier to discover. Intermediate rewards may provide more feedback, but they can introduce shortcuts: rewarding the number of tool calls encourages unnecessary actions.

Track complete task success on unseen cases alongside any shaped reward. Denser feedback is useful only when it helps learn behavior that transfers to the intended outcome.

---

Why can stale trajectories cause problems in RL training? <!--anki:3434666562393736623330383434373038326638643531343438343738323331-->
?
They reflect a **different distribution of actions and visited states**. A method assuming data close to the current policy can receive biased or high-variance estimates when rollouts become stale.

Record collection-policy versions and sampled-action log-probabilities. Bound rollout lag and reuse; apply importance correction only where the algorithm and support assumptions justify it. Clipping alone does not make arbitrary old data valid.

Also version tools and environments: a trajectory collected before an API or reward change may describe a different task, not merely an older policy.

---

## Scenarios

Scenario: your company processes 50,000 tickets per month with an agent using 12 tools. An open-weights model has one-fifth the inference cost but a success rate 20 percentage points lower. How do you plan training? <!--anki:4e5e36736062615121-->
?
1. **Build a reproducible environment** with representative tool behavior and independently checked business outcomes.
2. **Establish an SFT baseline** using validated successful trajectories; measure the remaining gap.
3. **Pilot RL if justified**, with meaningful reward variation and controlled rollout costs.
4. **Inspect rewarded behavior** for premature closure, unauthorized actions and checker exploitation.
5. **Validate on held-out tickets**, measuring success, repeated-run reliability and total cost per successful resolution.

**Trap**: assuming cheaper inference guarantees cheaper service after failures, escalations and training costs.

---

Scenario: a code agent's training success rate rises from 40% to 85% in two days. What do you check before accepting the improvement? <!--anki:774e2e796e754a55642f-->
?
1. **Inspect a sample of rewarded trajectories**: do the patches solve the requested problem?
2. **Look for evaluator exploits**, including deleted tests, leaked answers and malformed outputs accepted as success.
3. **Evaluate on held-out tasks** in fresh environments with protected validation assets.
4. **Compare general capabilities and costs** under the same inference budget.
5. **Repair faulty checks and reassess affected checkpoints** before resuming or promoting training.

**Trap**: deploying on the strength of the training reward curve alone.

---

## Sources

- [verl — RL Framework Documentation](https://verl.readthedocs.io/en/latest/)
- [Microsoft — Agent Lightning](https://github.com/microsoft/agent-lightning)

- Targeted review of 17 November 2026 — reward-source and interaction distinctions, critic-free baselines and policy lag: [DeepSeekMath](https://arxiv.org/abs/2402.03300) and [PPO](https://arxiv.org/abs/1707.06347).

## Connections
- [[52-post-training-alignment|Post-training & Alignment]] — RLHF, GRPO, RLVR and reward hacking
- [[53-synthetic-data-distillation|Synthetic data & distillation]] — SFT on accepted trajectories
- [[51-fine-tuning-adaptation|Fine-tuning]] — when to adapt model weights
- [[96-evals-rag-agents|Agent evaluation]] — independent checks in controlled environments
- [[54-distributed-training|Distributed training]] — training infrastructure
- [[49-coding-agents|Coding agents]] — repository tasks and test-based feedback
- [[114-reproducibility-variance|Reproducibility & variance]] — non-determinism and eval statistics
- [[138-reasoning-models|Reasoning models]] — test-time compute and reasoning budgets
- [[135-pretraining-scaling-laws|Pretraining & scaling laws]] — the initial training stage
- [[90-016-harbor-agent-evaluation|Harbor]] — containerized environments, rollouts and reward hacking
- [[00-moc-ai-engineering|MOC AI Engineering]]
