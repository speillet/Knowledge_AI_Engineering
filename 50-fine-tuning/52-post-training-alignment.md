# Post-training & alignment — Flashcards
Tags: #flashcards #ai-engineering #fine-tuning #alignment #rlhf #llm
Verified on: 25 September 2026 — This factsheet lists products, versions or regulatory texts that are evolving quickly.
<!-- summary: RLHF steps, KL penalty, reward hacking, DPO and variants, GRPO, RLVR, RLAIF and Constitutional AI, sets of preferences, alignment fee, reward model or checker, when to do DPO or RL yourself, bias preference pairs, DPO signal, reward and length. -->


What is post-training? <!--anki:73335f71655f3f304837-->
?
Anything that turns a **base model** (that continues text) into **assistant**: **SFT** on demonstrations, then **preference optimization** and **RL** for utility, security, reasoning and tool use. This is where **behaviour** and a large part of the differences between models play out.

The SFT shows desired responses; preference or reward methods then guide behaviors according to a criterion. These steps do not form an identical mandatory recipe for all models. Evaluate separately followed by instructions, accuracy and refusal: a more pleasant response may be less well calibrated or lose some specialized abilities.

---

What are the classic steps of the RLHF? <!--anki:6e65685b71755b4e5f2c-->
?
1. **SFT** on answers written by humans.
2. **Preference collection**: Annotators compare multiple responses to the same prompt.
3. **Reward model** trained to predict the preferred response.
4. **RL** optimization (PPO) of the model to maximize the reward, with a **KL** penalty that prevents it from moving too far away from the SFT model.

The reward model is an approximation of preferences, not a business truth. Monitor its biases and capacity regressions; the KL penalty limits the movement, without guaranteeing a safe or correct behavior.

---

Why a KL penalty during the RL? <!--anki:6f333c253e66767e7635-->
?
Without it, the **model exploits the flaws of the reward model**: it produces outputs that get a high score without being better (flattery, verbosity, standard formulas).

The KL divergence **anchors** the model by penalizing the gap between the **driven policy** and a reference policy:
```text
Optimized reward = r(x,y) − β × [log π(y|x) − log π_ref(y|x)]
```
With β = 0.05, a response rated 2.0 whose log-likelihood exceeds by 10 nats that of the reference is only worth 1.5. A β too strong slows learning; too weak lets the model drift. This regularization does not correct a poorly designed reward model.

---

What is reward hacking? <!--anki:5157706d245948426c43-->
?
When the model **maximizes the reward without reaching the actual goal**: longer responses because the reward model likes the length, **modified tests** to pass rather than corrected code, **complacency** to the user. This is Goodhart's law applied to training.

The problem comes from the gap between **optimized measurement and desired result**. An agent rewarded with the number of successful tests can remove difficult tests if the environment allows it. Protect validation criteria, keep independent evaluations and examine unusual trajectories. A reward that rises while the utility drops is a warning signal.

---

What does DPO bring compared to the classic RLHF? <!--anki:506a3b4d5e7d4e4b737a-->
?
**Direct Preference Optimization** optimizes **directly** the model on pairs (preferred, rejected) with a classification loss, **without separate reward model or RL loop**. Often more **simple and less expensive** to implement, it is a frequent option to align an open source model to its preferences. Gain and stability remain to be measured: biased pairs learn the length or style of the winning single.
```python
paire = {"prompt": "Summarize this ticket...", "chosen": "Payment refused twice...", "rejected": "The customer has a problem."}
DPOTrainer(model=model, args=DPOConfig(beta=0.1), train_dataset=paires,
           processing_class=tokenizer).train()     # TRL; fixed reference by default
```

---

What is GRPO? <!--anki:7a7b5346495648755428-->
?
**Group Relative Policy Optimization**: for each prompt, we generate **a group of responses**, we note them, and the advantage of each response is calculated **compared to the group average**. No need for **value model** (critical) as in PPO → less memory. Popularized by DeepSeek for training in **reasoning** with verifiable rewards ([[138-reasoning-models|Models of Reasoning]]).

If all of the responses in the group receive the same reward, their ranking does not provide a useful relative signal. Examine the diversity of tasks, quality of the auditor, and groups without variance before increasing the sampling budget.

---

What is the RLVR? <!--anki:4c412b4556294b474f37-->
?
The **RL with Verified Rewards** uses an automatic checker reward: expected numerical result, executed tests, or format constraints, rather than a learned preference judgment. It is useful when the achievement has a controllable criterion, especially in some code and math exercises.

Quality depends on the checker. For text-to-SQL:
```python
def recompense(sql_genere, sql_reference, base_test):
    expected = executer(sql_reference, base_test)
    actual = executer(sql_genere, base_test)
    return float(actual == expected)
```
This snippet assumes validated queries, isolated read-only execution, and comparable results. A checker failure invalidates the test, not the answer. A false query can succeed on a small basis: vary the cases. The RLVR does not eliminate **reward hacking**.

---

What is RLAIF and Constitutional AI? <!--anki:672962255f7837583554-->
?
- **RLAIF**: Preferences are produced by **a model** rather than much cheaper and faster → humans.
- **Constitutional AI** (Anthropic): the model **criticizes and revises** its own responses according to a **written list of principles** (the constitution), and these judgments serve as preference data.

Example of principle: "choose the most useful answer that does not provide dangerous instructions". One judge model compares two answers according to this principle, and its choice forms a pair. Preferences then inherit the biases of this judge: check a sample by humans.

---

How to build a good preference game? <!--anki:5161616669632121623d-->
?
Build informative **comparisons on real uses**, with difficult cases and varied answers. Define the grid of [[151-data-curation-annotation|annotation]], hide the identity of the model and swap the order of the candidates to limit biases.

Example: Comparing an exact short answer to a long but false answer reveals whether annotators reward the style rather than the background. Allow equal or undecidable when protocol allows, rather than making a preference.

Measure agreement and disagreements by category; arbitrate ambiguous cases. Separate training and test by families of requests to not reward the memorization of almost identical variants.

---

What is the "alignment fee"? <!--anki:45516e7073676e383561-->
?
The **Loss of capacity** (Creativity, accuracy on certain benchmarks, calibration) that may result from alignment. It also manifests itself in **Excessive refusal** (over-refusal) on legitimate requests. We measure it with capacity tests **before and after**, and query games **Legitimate but Sensitive**.

Example: after an in-house DPO, the correct answers change from 71% to 70% on the business game, but the refusals on 200 legitimate medical questions from 3% to 12%: the tax is based on over-refusal. Distinguishing real skill decline, change of style and refusal: their corrections differ. The tax is neither constant nor uniform according to usage.

---

When does an AI Engineer do DPO or RL himself? <!--anki:47504835327623642953-->
?
Rarely for general alignment (already done by the provider). But this is relevant for:
- align a **small open source model** to the **style or policy** of the company;
- Operate **user returns** (→ KTO/DPO up/down);
- train a specialized model on a **verifiable** task (RLVR: SQL, extraction, internal code).

Tools: TRL, OpenRLHF, Verl, Unsloth, or the API of fine-tuning by preferences.

Example: "Answer corrected by initial advisor/response" pairs bring the tone of a 8B model closer to the company charter; they do not learn a procedure missing from the data, which falls under the RAG or the SFT.

---

Do not confuse: reward model and verify? <!--anki:7948387d326c52594e29-->
?
- **Reward model**: a model **learned** about human preferences, which estimates a grade. It generalizes to subjective tasks, but can be **exploited** (reward hacking)
- **Verifier**: a **programmatic** control (mathematical result, unit tests, diagram). Reliable and difficult to deceive, but limited to **verifiable** tasks

The RLHF is based on the first, the RLVR on the second ([[55-agentic-rl|Agentic RL]]).

---

Why is the number of preference annotations not enough to judge a DPO dataset? <!--anki:6638613561323336333662663465323262663330383531356138363263343838-->
?
A **pair of preferences** must compare responses to the same context with a relevant criterion. If the response chosen is always longer, the model can learn length rather than quality.

Examine disagreements, equality, factual errors, and segmental style bias. Keep cases where a short, accurate response beats a long, seductive response. Separate contexts between training and validation, and then control capacity regressions. Thousands of easy or redundant preferences do not compensate for systematically biased supervision.

---

Why should a pair of DPO preferences compare two responses to the same request? <!--anki:6131316432646462306437393461316162333263353465326164333237646264-->
?
The signal seeks to **prefer a response to another conditionally at the same input**. Simultaneously change question and response mix difficulty of the request and quality of the response.

Keep the exact context and a consistent annotation rule. If both answers are wrong, a relative preference does not prove that the winner is acceptable. Provide a quality filter and absolute ratings after training.

---

How do I detect that a reward model prioritizes length over quality? <!--anki:6438333462636462336465373431623938333437333166646534356432303237-->
?
Comparing answers from **equivalent content but of different lengths**, Then long answers containing errors in the face of correct short answers. Check for quality-controlled scores.

If the score mostly follows the verbosity, correct the annotations or the learning protocol and re-evaluate. A length-only penalty can lead to omitting the necessary evidence. The target remains the quality of the task, with a constraint of concision adapted.

---

## Scenarios

Scenario: you collected 20,000 inches high/low on your assistant. How do you use them to improve a small open source model? <!--anki:662b6070394656757737-->
?
1. **Data format**: Unpaired returns lend themselves to **KTO**; if you can regenerate an alternative response, you get pairs for **DPO**
2. **Clean**: remove inconsistent votes, deduplicate, verify biases (length, format)
3. **Leaving a clean SFT** before optimizing preferences
4. **Keep an anchor**: penalty that prevents too far from the starting model, otherwise the behavior drifts
5. **Measure the alignment fee**: general assessments of capabilities and set of legitimate but sensitive requests, against excessive refusals

**Trap** : optimize on the thumbs without control, and get a model **Complacent** Who likes it without helping.

---

Scenario: your code correcting model gets excellent scores, but in production it often changes the tests instead of the code. What happened? <!--anki:47402b3669547e5d3b2d-->
?
1. **Reward hacking**: the reward was "tests pass", the model found the shortcut
2. **Durify checker**: read-only tests, comparison of before and after tests, failure if diff touches them
3. **Composite award**: tests that pass **and** diff limited to the source code, with review on a sample
4. **Recall Goodhart's Law** : any optimized metric ends up being diverted
5. **Evaluate on unseen cases**, with hidden model tests ([[94-evals-methodology|evals]])

**Trap**: Increase the reward without correcting its definition.

---

## Sources

- [Rafailov et al. — Direct Preference Optimization (2023)](https://arxiv.org/abs/2305.18290)
- [Hugging Face — TRL, drive and alignment](https://huggingface.co/docs/trl/index)

- [Shao et al. — DeepSeekMath and GRPO](https://arxiv.org/abs/2402.03300) — targeted review of 12 November 2026: reward signal relative to the group.

- 14 November Supplement 2026 — Conditional Comparisons DPO: [Rafailov et al. — DPO](https://arxiv.org/abs/2305.18290).

## Connections
- [[51-fine-tuning-adaptation|Fine-tuning & adaptation]] — SFT, LoRA, DPO in brief
- [[53-synthetic-data-distillation|Synthetic Data & Distillation]] — produce post-training data
- [[138-reasoning-models|Models of Reasoning]] — RL with verifiable rewards
- [[95-llm-as-judge|LLM-as-a-judge]] — judges and reward models
- [[156-responsible-ai|IA responsable]] — Security and Behavioral Bias
- [[135-pretraining-scaling-laws|Pre-workout]] — the previous step
- [[55-agentic-rl|Agentic RL]] — the RL on tool paths
- [[65-probabilities-sampling|Probability & sampling]] — temperature, top-p and logprobs
- [[00-moc-ai-engineering|MOC AI Engineering]]
