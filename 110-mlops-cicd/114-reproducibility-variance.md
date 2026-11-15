# Reproducibility & variance — Flashcards
Tags: #flashcards #ai-engineering #mlops #reproducibility #evals #llm
<!-- summary: non-temperature determinism 0, invariance to batch, seed, A rejoicing call, tests on variable outputs, standard error and confidence intervals, Matching comparison, Pass@K and Pass^k, variance of LLM-as-judge, fine-tuning reproducible, stability per repeated task, selection of seeds, checkpoint or inference artifact, change of dependence isolated, audit without replay possible, order of data, variance between runs. -->


Does a temperature of 0 guarantee identical outputs? <!--anki:6354476e2a6372354e28-->
?
**No.** GPU calculations in **floating semicolon** are not associative: (a + b) + c ≠ a + (b + c). A small deviation on the logits is enough to change the token chosen when two candidates are almost equal, and the rest of the answer diverges.

Batching, kernels, or a review of the backend can change the order of calculations. For a test, distinguish stable business invariants and exact textual equality; repeat sensitive tests and archive the actual configuration.

---

Where does the non-determinism of an inference server come from? <!--anki:42575a626e2f243e7b46-->
?
An important source is the **non-invariance to the batch**: kernels can change their order of reduction according to the form of the calculation. The roundings then slightly change the logits; two nearby tokens can exchange their rank.

With continuous batching, the form also depends on competing requests, so a seed does not set the entire digital environment. Kernels or deterministic modes reduce certain variations, with engine-specific conditions and costs. Also check sampling, hardware, versions, and parallel operations; there is no single dominant cause for all deployments.

---

Which model settings can change its output, at the same speed? <!--anki:7445534225614d64687a-->
?
- Sampling and **seed parameters**
- **Exact version** of the template, tokenizer and chat template
- **Quantization** (FP16, FP8, INT4…)

Trace these values with the query and use the same environment to compare two variants. FP16 is a reference precision here, while FP8 or INT4 further reduce the numerical representation. An identical seed ensures repeatability only under the conditions supported by the engine; it does not freeze all sources of variation.

---

Which infrastructure and application factors can change the output of the same model, to the same prompt? <!--anki:4b5a6e72257228217c42-->
?
- **Inference engine** and its version, type of **GPU**, degree of **tensor parallelism**
- **Server load** (batch size)
- Application side: prompt system, tools, **documents recovered** by the RAG

Distinguish prompt user identical and **full entry of the same model** : a different retrieved document changes the problem posed. Recording the final context makes it possible to separate this application variability from the numerical effects. for a diagnosis, first freeze the sources and tools, then compare the inference configurations.

---

What is the seed parameter? <!--anki:4b30415a706a76365a43-->
?
The **seed** initializes a pseudo-random generator in the perimeter supported by the library or engine. It helps to repeat certain prints in a fixed stack; it does not freeze all operations or the entire system.

Several generators can be involved: data preparation, sampler, model, workers or GPU. Documenting those controlled and the versions used, then testing the repeatability announced by the environment. In comparison, repeat on several seeds planned in advance and keep their results, including unfavorable. Choosing the best seed after the fact is like selecting an experiment, with a risk of overlearning the evaluation.

---

How to make a LLM call replayable? <!--anki:693e60316b3025562574-->
?
Retain, based on permissions and retention, **effective entry, versions, and observed result**: prompt rendering, context, settings, tool contracts, and external observations. Protected references may replace some sensitive copies.

Differentiate between replay of recorded observations and a new call to actual services. The first isolates the orchestration; the second may encounter different data, tools or backend. An inaccessible reference or a removed model sometimes prevents regeneration. For historical proof, the recorded result and its context therefore remain distinct from an identical recalculation promise. Regularly test access to the parts necessary for diagnosis.

---

When is an exact comparison of the LLM output suitable, and when should properties be tested? <!--anki:656d592d3b347921397b-->
?
For a **free answer**, several formulations can satisfy the task: an exact match would penalize correct variants. Check the facts, fields, constraints and useful references.

For a class, identifier, or canonical value, the exact equality may be the correct test, after an explicitly accepted normalization. Test separately the orchestration code with simulated or recorded responses, and the model on representative inputs. A replay makes some tests reproducible; it does not measure the behavior of the actual model again.

---

Why can a score gap between two prompts be nothing but noise? <!--anki:422b296b24785b465177-->
?
A score calculated on a sample has an **uncertainty**. For a proportion of success `p` on `n` independent observations:
```text
SE ≈ √(p × (1 − p) / n)
p = 0.8; n = 100 → SE ≈ 0.04
Normal IC to 95% ≈ 80% ± 7.8 points
```
This interval concerns **a score**, not directly the gap between two prompts. On the same examples, use a matched comparison: the uncertainty depends on the disagreements between variants. Repeat the generations if they vary; do not conclude a robust gain from a few points without analysis.

---

How to rigorously compare two variants (prompt, model)? <!--anki:74766263287b66405325-->
?
- **Same dataset** and analysis **paired** (difference for example): much less variance than when comparing two averages
- **Several runs** for example, to smooth out the sound of sampling
- Report **mean ± confidence interval**, and **expand dataset** when the sought gap is small

Pairing allows you to see which tasks win or lose, instead of hiding the compensations in the average. If several runs come from the same example, take this dependency into account in the uncertainty. Keeping a final test separate: selecting the best prompt after many tries on the same game ends up exploiting its noise.

---

Do not confuse: pass@k and pass^k? <!--anki:4c352d733b676a657961-->
?
**pass@k** means at least one success among k tests; **pass^k** means k success. For a task of constant success probability p and independent tests:
```text
pass@k = 1 − (1 − p)^k ; pass^k = p^k
p = 0.8; k = 3 → 99.2% and 51.2%
```
The first does not ensure that we know how to identify the correct answer; the second describes the repeatability according to this protocol. On heterogeneous tasks, calculate the results per task before averaging. Publish also initial success, cost and types of failures according to the service.

---

How to estimate pass@k without bias? <!--anki:4467264a4f62364f6a33-->
?
Generate **n ≥ k** samples per problem, count **c** achievements, then:
```text
pass@k = 1 − C(n − c, k) / C(n, k)
```
It is the estimator of the Codex paper (2021), more stable than pulling only k tests.

`C(a, b)` is the number of combinations; if `n − c < k`, the failure term is zero. Calculate by problem and then average. The interpretation assumes draws according to a comparable protocol and a reliable checker. Pass@k measures the presence of at least one success, not the ability to identify that success without oracle.

---

Why does a LLM-as-judge add variance? <!--anki:6d765b41246831436431-->
?
The judge is himself an LLM **Non-deterministic** and **Biased** (Order of presentation, length, style). We turn it to **low temperature**, on **Swap the order** of comparative answers, on **Average of several passes**, and caliber it on human annotations.

Repeating the judgment reduces a part of the hazard, but **not a systematic bias** : a judge who always prefers long answers can remain very stable and be wrong. Measure agreement with human references by type of case, retain the judge’s version and inspect disagreements before using his score as a deployment decision.

---

How to make a fine-tuning reproducible? <!--anki:74213c39574676285476-->
?
Freeze **data, sample order, seeds, base, code, libraries, hardware, and distributed configuration**. Enable appropriate deterministic options, e.g. `torch.use_deterministic_algorithms(True)`, respecting their preconditions.

Example: Resuming a workout also requires optimizer states, scheduler, random generators and sampler position. Reloading only the weights with the same seed does not take the same calculation.

Determinism can slow down or deny an operation without a suitable implementation. Hardware changes or distributed reduction can change the results. Distinguish bit-by-bit reproduction in a fixed stack and **reproducibility of conclusions**, evaluated by several runs and comparable metrics.

---

Should we aim for determinism everywhere? <!--anki:4e404d572d6036633c3c-->
?
**No.** It is used where one compares or investigates: **tests, audits, debugging, comparative evals**. In production, one **conceives for variability**: validation of outputs, [[63-guided-generation|outputs contraintes]], retrievals and evals on several runs. A reliable system does not depend on a lucky draw.

Make business rules, authorization and calculations deterministic when possible, then measure the variability of generative parts. For the same request, several formulations may be acceptable while an amount must remain accurate. Defining invariants of result and external effect makes it possible to be reliable without imposing an identical text on each execution.

---

Calculation: two equi-weighted tasks succeed with constant probabilities 1 and 0.5. The repetitions are independent for each. What is their pass^2 average, compared to the square of the average success? <!--anki:3237306434396163383139313463656161383761666134346137363531323363-->
?
First calculate the repeated success **per task**, then average:
```text
Pass Average ^2 = (1² + 0.5²)/2 = 0.625
medium success = (1 + 0.5)/2 = 0.75
medium success square = 0.75² = 0.5625
```
The values differ because the difficulties differ. For this protocol, two tries repeat the same task; they do not resample a task from the mixture at each attempt. An average overall success of 75% is therefore not enough to determine the average ^2 pass. Specify tasks, repetitions and weighting before aggregating.

---

Why repeat each task several times before comparing the stability of two agents? <!--anki:3232383735333832656138383437646639376330653431323964366130323633-->
?
An average **score** mixes difficulty of tasks and variance of executions. One agent can always succeed the same cases, while another succeeds intermittently each case with the same overall average.

Repeat each task with controlled initial status, then report average success and reliability distribution per task. Keep repeats grouped in uncertainty analysis. Choose metric as needed: Unsupervised automation requires a different regularity from a generation where the user selects a candidate. Repeated calls on different tasks do not measure this stability.

---

Why keep unfavourable seeds in a training comparison? <!--anki:6664346537356230386264333462633938613036663063633866326266373665-->
?
Selecting only the **best seed** turns a repetition to measure variance into a candidate search. The reported result becomes favorably selected.

Set the number of runs, metric and aggregation rule before the test; keep scores and failures of each run. If a selection is assumed, count its cost and confirm the candidate on data not used to choose it. A significant variance can indicate an unstable training or a game too small. The dispersion of the results is operational information: it influences the risk of the next automatic execution, not just the quality of a publication.

---

Do not confuse: training checkpoint and exported model for inference? <!--anki:3063626564653532306165333462376562656131386565653235303237353961-->
?
A **training checkpoint** may include weight, optimizer, scheduler, random states, and read position required for recovery. An **inference artifact** contains what the service needs to load to predict, along with its contract and dependencies.

Exporting the weights alone does not ensure a faithful recovery of the calculation; keeping the entire training state does not ensure a light or safe package for the serving. Define two contracts and retention policies, and then test recovery and loading separately. The exact format depends on the framework; a file named `checkpoint` does not by itself prove which states it contains.

---

Why test a new dependency and weight separately? <!--anki:3831393435343162333339393463313962636361376334616639656532313664-->
?
Changing **libraries and model** at the same time makes it difficult to assign a deviation. A difference can come from serialization, numerical calculation, preprocessing or learning.

Compare, when combinations are compatible, old model/old stack, old model/new stack and new model/new stack on the same cases. Measure types, values, decisions and costs with explicit tolerances. An old stack may not load the new format: document this limit rather than fabricate a comparable result. This protocol does not remove any interaction, but reduces the investigation and gives a migration path that is easier to validate.

---

How to explain a historical decision if the vendor model used has been removed? <!--anki:6365646334323839653266313462613362353134396131373965343638393331-->
?
Distinguish between **proof of what happened** and **ability to regenerate it**. Without access to the original model, a new identical execution may be impossible, even with prompt and preserved parameters.

Rely on recorded result, authorized context, vendor reference, application version and proof of external actions, depending on the retention policy. Another version can be used to analyze the behavior, but its result does not replace that observed historically. Providing this limit before choosing the service and testing the recovery of audit parts. Archive sensitive data without purpose or control is not a universal solution.

---

Why is it not enough to fix the seed without fixing the order of the data to reproduce a drive? <!--anki:6233663861326235336162393432636338626661336130616236373134643839-->
?
Updates depend on **grouped examples and their order**. Workers, shuffling, dataloader recovery, and transformations can modify this sequence.

Keep manifests, random states, and read positions necessary for recovery, then distinguish between exact reproducibility and statistical stability. A single seed does not freeze kernels or dependencies. Check metrics on multiple runs when decisions are based on small deviations.

---

Why not present the best run out of ten as the expected performance of a workout? <!--anki:3264313837386665633039353464323938363737353733396133313136646331-->
?
Selection promotes **a lucky achievement** of variance. It overestimates the performance of a future training if this selection is not integrated into the protocol.

Publish distribution, selection rule and independent evaluation of the successful candidate. The cost of the ten runs is part of the method. An average and an appropriate interval are more informative than a single record when one wants to estimate stability.

---

## Scenarios

Scenario: a customer contractually requires that "the same document always gives the same extraction". What do you commit to do, and what do you refuse to commit to? <!--anki:417a783d2b7d663c296b-->
?
1. **Honestly explain**: Even at 0 temperature, GPU calculations do not guarantee an identical output to the nearest bit
2. **Define testable criteria**: schema, field accuracy and error handling; do not promise identical values with each regeneration
3. **Make call replayable**: journal dated model, prompt rendered, parameters, documents, and response
4. **Reduce variance**: low temperature, constrained output, possibly a deterministic mode of the engine, at the price of performance
5. **Hide results**: for the same document already processed, return the saved output rather than regenerate

**Trap**: Promise determinism because `temperature=0` is in the configuration.

---

Scenario: your team is testing a bug-fixing agent. It passes 4 times on 5 in demonstration, and the product wants to announce "80% of success". What do you specify? <!--anki:6376583a3e3362543e7d-->
?
1. **Report observation**: 4 success on 5 trials, i.e. 80% on this small demonstration; the estimate remains very uncertain.
2. **Set protocol**: five different tasks or five repetitions of a single task?
3. **Choose metrics**: pass on first try, pass@k if a checker chooses a solution, pass^k for repeatability.
4. **Expand the evaluation** to independent representative cases, with such useful repetitions.
5. **Report uncertainty and limits**, without presenting the observed rate as a guarantee.

**Trap**: Say that five tests measure “nothing,” or that they are enough to accurately estimate production.

---

## Sources

- [NIST — McNemar test for paired binary observations](https://www.itl.nist.gov/div898/software/dataplot/refman1/auxillar/mcnemar.htm)

- [PyTorch — reproducibility and hazard sources](https://docs.pytorch.org/docs/stable/notes/randomness.html)
- [scikit-learn — persistence and compatibility of environments](https://scikit-learn.org/stable/model_persistence.html)

## Connections
- [[65-probabilities-sampling|Probability & sampling]] — the source of variability
- [[111-mlops-llmops-fundamentals|Basic MLOps]] — versioning and lineage
- [[112-model-cicd|CI/CD models]] — tests and eval gates
- [[113-monitoring-drift-feedback|Monitoring & drift]] — version changes side provider
- [[92-chainforge-evals-prompts|Evals]] — compare prompts on a golden dataset
- [[91-langfuse-observability|Langfuse]] — traces to replay a call
- [[62-inference-optimizations|Inference optimizations]] — continuous batching and quantization
- [[51-fine-tuning-adaptation|Fine-tuning]] — reproducible training
- [[94-evals-methodology|Evaluation methodology]] — game size
- [[95-llm-as-judge|LLM-as-a-judge]] — correct an imperfect judge
- [[11-llm-inference-servers|Inference Servers]] — vLLM, SGLang, TensorRT-LLM and their setting
- [[153-data-flywheel-versioning|Data flywheel & versioning]] — loop on failures, version data
- [[54-distributed-training|Distributed training]] — memory and drive parallelisms
- [[67-speculative-decoding|Speculative Decoding]] — generate multiple tokens per pass
- [[68-quantization|Quantization]] — reduce accuracy to gain memory and speed
- [[96-evals-rag-agents|Evaluation of RAG systems & Agents]] — retrieval, trajectories and passes^k
- [[97-evals-online-ab-testing|Evals online & A/B testing]] — measure in production
- [[98-agent-debugging|Debugging agents]] — find the cause of a failure in a trace
- [[165-computer-use-browser-agents|Computer use & browser agents]] — agents that use interfaces
- [[55-agentic-rl|Agentic RL]] — train a model on agent tasks
- [[118-ml-artifacts-registry-releases|Artifacts, registry and releases ML]] — production contracts and verifications
- [[90-016-harbor-agent-evaluation|Harbor]] — pass@k and repeated tests calculated by an eval harness
- [[00-moc-ai-engineering|MOC AI Engineering]]
