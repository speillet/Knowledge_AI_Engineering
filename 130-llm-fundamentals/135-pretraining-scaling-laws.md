# Pretraining & scaling laws — Flashcards
Tags: #flashcards #ai-engineering #fundamentals #pretraining #scaling #llm
<!-- summary: manufacturing steps, pre-workout or post-workout, data, scaling laws, Chinchilla, over-workout for inference, 6ND, MFU, contamination, knowledge cutoff, emerging capabilities, data wall, scaling laws extrapolation limits, lifecycle cost, tokens quality. -->


What are the major manufacturing steps of a LLM? <!--anki:7a3f3d7a4d61366e7263-->
?
1. **Pre-workout**: prediction of the following token on **billions of tokens** → base model (knowledge, language, latent reasoning).
2. **Mid-training** (optional): more targeted data (code, math, long context).
3. **Post-training**: SFT then alignment by preferences and **RL** → model that follows instructions, uses tools and reasons ([[52-post-training-alignment|post-training]]).

Chains vary: not all teams do RL, and SFT data can be human or synthetically validated. Evaluate each step on separate sets to distinguish between targeted progress and general regression.

---

What data does a LLM pre-drive? <!--anki:4124396750642f6d357d-->
?
**filtered web** (Common Crawl cleaned), **code**, **books**, scientific articles, multilingual data and, increasingly, **synthetic data**. Quality prevails: **deduplication**, quality filters (often by classifier), removal of toxic content and PII, **decontamination** of benchmarks ([[151-data-curation-annotation|curation]]).

The **mix** counts as much as the quantity: a long source can dominate the budget of tokens even if it contains few documents. Track languages, domains, licenses and rare cases, then measure the effect of filters by segment. Removing all atypical texts can improve a clean appearance while depleting the sought-after abilities.

---

What Do Scaling Laws Say? <!--anki:6725533c2f733155372f-->
?
These are **empirical regularities**: in a given regime, the loss varies approximately according to power laws with parameters, data and calculation. For a dense Transformer, `C ≈ 6ND` gives an order of magnitude of the training calculation.

They help to divide a budget between size and tokens from small comparable tests. Example: doubling the parameters with fixed calculation requires approximately to divide the tokens by two; the best compromise depends on the adjusted curve.

A predicted drop in loss **does not guarantee** an accurate business gain. Change of data, architecture or recipe may invalidate the extrapolation.

---

What has Chinchilla shown? <!--anki:706f6333723d25753c64-->
?
What To **Fixed calculation budget**, The optimum is to increase **Parameters and tokens in equal parts**, either approximately **20 tokens by Parameter**. Many of the earlier models were **Too big and under-trained**.

It is an empirical optimal allocation of the **pre-workout budget** in the studied diet, not a mandatory rule for each model.

While inference accounts for the bulk of the cost of living, driving a smaller model for longer may be preferable, nor does the empirical ratio guarantee that repeating poor data is equivalent to adding informative tokens.

---

Why are current models trained far beyond Chinchilla? <!--anki:267869342439474772-->
?
Chinchilla Optimizes **cost of training**, not the **Total cost**. One more model **Small** Trained on **much more tokens** (Hundreds, or even thousands of tokens per parameter) costs more to train but is **cheaper to serve** — and inference can dominate the cost over the lifetime of a widely used model.

This arbitrage depends on the future number of calls. A model rarely served may never amortize this extra drive; compare initial cost and economy per request over an explicit horizon, at comparable quality.

---

What is the "6ND" law and what is it for? <!--anki:795034647b6b31645263-->
?
The training compute of a dense Transformer ≈ **6 × Parameters × tokens** FLOPs (2 for the forward pass, 4 for the backward pass). Example: 1 B parameters on 20 B tokens ≈ **1.2·10²⁰ FLOPs**.

Divide by the effective throughput of the cluster gives **seconds**, not GPU-hours. With 8 GPU to 100 TFLOP/s effective each: about 150,000 s, i.e. 41.7 h elapsed and **333 GPU-hours**. If the throughput is theoretical, apply the **MFU**; do not count the long costs

---

What is MFU? <!--anki:42584d7a597735794763-->
?
**Model FLOPs Utilization**: the portion of the computational power **theoretical** of the GPU actually used for training. Typically **30 to 50%** on large clusters; the rest is lost in communications, memory expectations and failures ([[54-distributed-training|Distributed Training]]).

The numerator estimates the FLOPs useful to the model per unit of time; the denominator depends on the **hard peak and the precision chosen**. Specify these conventions before comparing two MFUs. A low value may come from data, memory or communications; it does not alone designate the component to be optimized.

---

What is Benchmark Contamination? <!--anki:79216e4b4d4532747c44-->
?
The presence of **questions (and answers) of a benchmark in the training data**. The model has "seen" them: its score **overestimates** its actual capacity. Hence the **recent or private** benchmarks, tests on reformulated variants, and caution against leaderboards ([[146-model-selection|choice of model]]).

The leak can be accurate or take the form of a paraphrase, a published solution or an almost identical example. A contaminated score then partly measures familiarity with the test. Search for recoveries and renew cases; reformulating only the question does not necessarily remove the knowledge of its answer.

---

What is the knowledge cutoff? <!--anki:67494854747530244668-->
?
The **Knowledge Cut Date** is an announced benchmark for the freshness of the data used by the model, and does not guarantee that the model is aware of all the previous facts or that all of its training steps share a single time boundary.

A model can answer with confidence from old information, even if its wording seems current. For a version of API, a price or a rule likely to evolve, consult a source dated via search or RAG and check its relevance. Separate thus learned knowledge and information actually consulted during the answer.

---

What do we call emerging capabilities, and why are they debated? <!--anki:682b797c26666a40656a-->
?
Abilities that seem **Appear abruptly** beyond a certain size. Part of this effect comes from **Choice of Metric** (Exact match, all or nothing): with a continuous metric, Progress is often **Gradual**. Morality: **Measure your task** rather than assuming a threshold.

A task scored correct only if ten sub-responses are correct may suddenly seem successful when each sub-response gradually improves. This does not rule out the occurrence of new behaviors; it requires a review of the protocol. Varying metrics, difficulties, and model sizes before assigning a score change to a universal threshold of ability.

---

Why are we talking about a “data wall”? <!--anki:443379637077604b2458-->
?
The stock of **quality human text** available on the web is finite and exhausted at the current rate. The answers: **synthetic data**, **multimodal**, training on **several eras** of the best data, and moving the calculation to **post-training by RL** and **test-time compute** ([[138-reasoning-models|Models of Reasoning]]).

This is a constraint on data that is **useful, accessible and actionable**, not the disappearance of any text on the Internet. Repeating data or generating more does not automatically replace diversity and quality. Projections depend on the assumptions of collection and effectiveness; avoid inferring a certain date of end of progress.

---

Do not confuse: pre-workout and post-workout? <!--anki:48683125506a2f714352-->
?
- **Pre-workout**: Predict the following token on **billions of tokens** of plain text. It brings **knowledge** and general capabilities, and costs the bulk of the calculation
- **Post-training**: SFT then preferences or RL (RLHF, DPO, RLVR) on games **much smaller**. It brings the **behavior**: follow instructions, format, refusal, reasoning ([[52-post-training-alignment|post-training]])

Practical consequence: an enterprise fine-tuning is post-training. It changes the **form** of the answers much more easily than it adds **knowledge** ([[51-fine-tuning-adaptation|fine-tuning]]).

---

Calculation: under C ≈ 6ND, what number of GPUhours to drive a dense 8B sur 15,000 billions of tokens To 4 × 10^14 FLOP/s useful by GPU, What is the ideal duration on 1,000 GPU ? <!--anki:6566616464316664376339343436633939366138316165646262353739633461-->
?
```text
C ≈ 6 × N × D = 6 × 8e9 × 15e12   = 7,2e23 FLOP
H100 to 40% from MFU ≈ 4e14 FLOP/s Useful
7,2e23 / 4e14 = 1,8e9 s           ≈ 500 000 GPU-heures
on 1,000 H100 ≈ 3 weeks
```
Meta reported about **1.5 million GPU-hours** for Llama 3.1 8B: the actual MFU, the rework and the experiments are added, so an AI Engineer starts from an existing model ([[51-fine-tuning-adaptation|fine-tuning]]).

The formula is an order of magnitude for a dense model and ignores several additional costs. The three weeks assume an ideal distribution on 1,000 GPU with the announced efficiency. The difference with a published figure does not, on its own, allow to assign the additional time to the times: perimeter of counting and efficiency must be comparable.

---

Calculation: for a 70B model, how many tokens gives the educational benchmark of 20 tokens per parameter, compared to the 15,000 billion announced for Llama 3 70B? <!--anki:6335373737396634343762663437663162353937616338383032353765326435-->
?
```text
Chinchilla: ≈ 20 tokens per parameter → 70e9 × 20 ≈ 1,400 billion tokens
Llama 3 70B: ≈ 15,000 billion tokens → ≈ 200 tokens per parameter, 10 times more
```
Chinchilla minimizes the cost of **training**; we go far beyond to obtain, at equal quality, a smaller model and therefore cheaper to **serve**.

With 15,000/70, the ratio is about **214 tokens per parameter**; "200" is a rounding. More than tokens does not guarantee a proportional gain: quality, diversity and repetitions of the corpus count. The arbitration is done on the complete training cycle then inference, depending on the volume of requests expected.

---

Why extrapolating a scaling law out of its measured domain can lead to a bad investment? <!--anki:3065383665653361623066633437313661313563373633656139633864613534-->
?
A **scaling law** adjusts an empirical relationship under certain data, architecture and computational conditions. It is not a universal guarantee of business gain for any increase in parameters or tokens.

Check measured range, definition of loss, and assumptions before extrapolating. Compare with intermediate experiments and include inference cost, data quality, and product objective. A predicted loss drop may not resolve a rare error or tool defect. Present extrapolation as a quantified hypothesis with uncertainty, and then predict an experimental decision point.

---

Why does not doubling the number of training tokens double the useful information? <!--anki:3439626436636162353930613435383039323762326335303139616664633665-->
?
The new tokens can be **duplicates, noise or very close data**. Their marginal value depends on diversity, quality and suitability for the purpose.

Trace sources, repeats, and contamination of assessments. Repeating data can sometimes help, but should not be presented as adding independent facts. Empirical laws depend on the data regime used to establish them.

---

## Scenarios

Scenario: a model displays 92% on a public reasoning benchmark, but collapses on your business cases. What explanations do you envisage? <!--anki:4b3d69623c34476e7578-->
?
1. **Contamination**: Benchmark questions, or their variants, may have been in the training data
2. **Distribution gap**: the benchmark does not look like your traffic, neither in language, format, nor in difficulty
3. **Metric**: an overall score can hide the failure on the segment you are interested in
4. **The correct answer**: evaluate on **your** data, benchmarks are only used for pre-sorting ([[146-model-selection|choice of model]])
5. **Check the cut-off date** if your cases involve recent information

**Field**: Arbitrate between two models on the basis of a public ranking.

---

Scenario: your management asks how much would it cost to pre-train a "home" model of 8 billion parameters. How do you respond? <!--anki:6b585758734f29685d7e-->
?
1. **Estimate calculation**: Approximately 6 × parameters × tokens. For 8 billion on 15,000 billion of tokens, the order of magnitude is colossal
2. **Convert to GPU-hours**: Divide by the actual cluster throughput, knowing that the actual use of GPU often revolves around 30 to 50%
3. **Add the rest**: data collection and curation, failed tests, post-training, evals
4. **Ask the real question**: what need would not be covered by an existing model, fine-tuned or distilled?
5. **Propose the alternative**: fine-tuning or distillation, for a fraction of the cost ([[53-synthetic-data-distillation|distillation]])

**Tip**: Compare a training cost to a API cost without looking at the lifetime and inference cost.

---

## Connections
- [[131-transformer-architecture|Architecture Transformer]] —
- [[52-post-training-alignment|Post-training & Alignment]] — the next step
- [[53-synthetic-data-distillation|Synthetic Data & Distillation]] — beyond the data wall
- [[54-distributed-training|Distributed training]] — how to parallelize
- [[136-mixture-of-experts|Mixture of Experts]] — more parameters without more calculation
- [[146-model-selection|Choice of model]] — read benchmarks
- [[55-agentic-rl|Agentic RL]] — train a model on agent tasks
- [[69-roofline-prefill-decode|Roofline & Disaggregation]] — which limits each phase of the inference
- [[00-moc-ai-engineering|MOC AI Engineering]]
