# Probability & sampling — Flashcards
Tags: #flashcards #ai-engineering #inference #sampling #probabilities #llm
<!-- summary: logits, temperature, greedy, top-k, top-p and min-p, conditional probabilities, logprobs, perplexity, renormalization exercises, sampling and confidence limits, class scores at several tokens, entropy, order of filters. -->


What does a LLM produce at each generation step? <!--anki:7a6f51326e26623f245b-->
?
A **logit vector** (a score by token of the vocabulary), transformed into **probability distribution** by a **softmax**. The following token is **chosen** in this distribution, added to the context, and we start again: it is the generation **autoregressive**.
```text
context → logits → softmax → P(token) → choix → context + token → …
```

Order of magnitude: with a vocabulary of about 128,000 tokens, each step produces 128,000 logs, calculated from the only last hidden state; the previous positions are taken from [[61-kv-cache-attention|KV cache]]. The loop remains sequential: a response of 500 tokens requires 500 model passes, hence the weight of the output length in the latency.

---

Why do two identical calls give different answers? <!--anki:494e50217049554b3f66-->
?
The **Sampling** can choose from tokens different in the same distribution. The prefix then changes and continuations may diverge.

This is not the only cause: review of the model, recovered documents, template, parameters, numerical calculations and batching can vary. Even without sampling, the result depends on the environment. To diagnose, first verify that the full entry and configuration are the same, and then distinguish between random sampling and system variations. "Same user question" does not mean "same problem actually sent to the model".

---

What is the role of temperature? <!--anki:7a675f34445f53796f43-->
?
For **T > 0**, the temperature divides the logits before softmax:
```text
P(i) = exp(z_i / T) / somme_j exp(z_j / T)
```
T < 1 concentrates more mass on high logs; T > 1 spreads it; T = 1 retains distribution before other possible treatments. In limit T → 0, the mass concentrates on the maximum; API often use zero to request greedy.

These effects concern the **diversity of the prints**, not the truth. A concentrated distribution can repeat an error with assurance; evaluate accuracy and repetitions separately.

---

What is Greedy Decoding? <!--anki:6f593a673f4456597d3a-->
?
Take **at every step token The most likely** (temperature 0). Simple and stable, but he can **Turn in Loop** (repeats) and does not **guarantee** the most likely sequence as a whole.

The choice is local: the token preferred now can lead to a globally less likely sequence than another start. Zero temperature also does not ensure a perfect identity between infrastructures, because of rounding and implementation. Evaluate repetitions and accuracy, without assimilating absence of sampling and truth.

---

What is top-k sampling? <!--anki:74476e34764847357059-->
?
Keep only the most likely **k tokens**, **renormalize** their probabilities, and then sample. Limit: k is **fixed**, whether the model is sure of itself (only one good candidate) or whether it hesitates (dozens).

Example: if the model gives 0.90 the First token, k = 40 Canned 39 unlikely candidates who keep together about 10% Chances of being shot. If he hesitates between 200 tokens plausible, k = 40 cut most of them. This is why it is often combined with top-p or min-p, which adapt to the form of distribution. Limit case: k = 1 This is equivalent to Greedy decoding.

---

What is top-p (nucleus sampling)? <!--anki:46793e5f305777615e5f-->
?
Sort the tokens by decreasing probability, keep the **smallest prefix reaching the threshold p**, and then renormalize and draw randomly.

Example: for `0,6 ; 0,25 ; 0,1 ; 0,05`, `top-p=0,8` retains the first two, total mass 0.85. Their draw probabilities become about **0.706 and 0.294**, not 0.6 and 0.25; the others are excluded.

The size of the core adapts to the concentration of the distribution. Temperature and other filters can modify this distribution according to their order of application. The threshold does not measure the truth: a false response can concentrate a high probability.

---

What is min-p? <!--anki:63343a6840684d475a3f-->
?
The **min-p** retains the tokens whose probability is at least `min_p × p_max`, then renormalizes before the draw. With `p_max = 0,5` and `min_p = 0,1`, the threshold is 0.05.

This is a threshold relative to the best-ranked token, while top-p uses a cumulative mass. The support and order of treatments depend on the engine. Better high-temperature performance must be assessed on the task; the threshold follows the concentration of the distribution, not an already calibrated factual confidence.

---

What sampling settings do you use? <!--anki:627032625674675b7b24-->
?
Depart from **settings for the model**, Then compare it to the task. A low temperature or greedy is a candidate for stable extraction; More diversity can help in the search for several solutions.

These choices do not guarantee accuracy or useful creativity. Measure quality, repetitions, format validity and cost; check if the model imposes certain parameters. Modifying one setting at a time helps diagnosis, and then test interactions. Numerical values from another model are not a universal recipe.

---

What are logprobs and what are they used for? <!--anki:4c453a62566a77455729-->
?
**logprobs** are logarithms of probabilities assigned to tokens, for events and treatments defined by API. They are used to calculate a likelihood or to construct a classification score.

Comparing "yes" and "no" implies defining labels, their tokenization, and normalization; some labels use multiple tokens. A weak logprob may simply correspond to a rare noun. Neither its value nor verbal assurance directly constitutes a likelihood of hallucination. Validate the score on annotated examples before turning it into an abstention threshold.

---

How to calculate the probability of a sequence? <!--anki:785f373940723d475669-->
?
By the **string rule**: multiply the probabilities of each token conditional to the prefix; in logarithms, add them.
```text
P(t1,…,tn | context) = produit_i P(ti | context,t1,…,t{i−1})
```
For a complete completed sequence, specify if EOS is entering the event. The average of logprobs per token is used to compare standardized scores, but **is no longer the log-probability of the entire sequence**. Choose the score according to the objective: normalization changes the possible ranking and does not transform the likelihood into business accuracy.

Example: Two conditional probabilities 0.5 and then 0.2 give 0.1, not 0.35.

---

What is Perplexity? <!--anki:447e6435633669525170-->
?
**Perplexity** is the exponential of the mean of the negative log-probabilities of the reference tokens, with natural logarithms:
```text
PPL = exp(− somme_i log P(ti | prefix)/N)
```
It measures the predictability of a text under the model. To compare, keep corpus, tokenization, mask comparable evaluated positions and context policy. A different tokenization can change the scale without useful progress. Perplexity directly evaluates neither actuality, nor respect for instructions, nor quality of an isolated response; complete with task criteria.

A uniform distribution over four tokens has a perplexity of 4. This does not mean that the model has four plausible answers or an accuracy of 25%.

---

Are the probabilities of a LLM reliable (calibration)? <!--anki:454b32677a482d2d2925-->
?
The **calibration depends on the event and the population being evaluated**. The probability of the next token is not directly that an entire answer is correct. A frequent but false sentence may be very likely.

Post-training, prompt and domain can change the calibration; verbalized trust is not a default validated measure. Build a score for a specific task, confront it with independent labels and check its segments. Do not automatically turn a high logprob into a news indicator.

---

Do not confuse: temperature and top-p? <!--anki:70332c3a5d2f2c2b6961-->
?
The **temperature** modifies the relative probabilities via the logits; **top-p** selects, in descending order, the smallest prefix of tokens reaching the cumulated mass p, and then renormalizes.

Modifying both changes both distribution and allowable set. To assign an effect, start with a single variable, and then test a combination if necessary. There is no mathematical prohibition against combining them; check their support and order in the engine. Neither directly regulates the truth or safety of the answers.

---

What happens if we combine a high temperature (1.5) and a top-p to 1? <!--anki:3263666230666563316166313465656538393562646233623835343166666633-->
?
T = 1.5 **flattens the distribution** compared to T = 1; top-p = 1 does not remove any candidates per mass truncation, so the initially less likely tokens can be fired more often, without each output having to become inconsistent.

The effect depends on the model and other treatments. Comparing useful diversity, errors and repetitions on the same tasks. Reducing the temperature or truncating the distribution are candidates to be tested, not a guarantee of quality. An early error can also influence the following continuations.

---

Calculation: four tokens have the probabilities 0.50, 0.30, 0.15 and 0.05. With top-p = 0.75 applied alone, which ones remain and with what probabilities after renormalization? <!--anki:6465663762656366643837343433363162626362623533656132343239356336-->
?
Keep the smallest sorted prefix whose mass reaches **0.75**: the first token is not enough; the first two total 0.80.
```text
P1 after filtering = 0.50 / 0.80 = 0.625
P2 after filtering = 0.30 / 0.80 = 0.375
P₃ = P₄ = 0
```
The threshold is a mass to be reached, not a number of tokens or a minimum probability per token. The retained mass may exceed the threshold. We then draw a token in this distribution; keeping two candidates does not mean producing them both.

---

Calculation: two reference tokens have the conditional probabilities 0.5 then 0.25. Excluding EOS, what is the probability of their sequence and its perplexity on these two tokens? <!--anki:3831613766666264346431313433313261646537653733636530313265303561-->
?
Apply the string rule, then normalize the logarithm for perplexity:
```text
P(sequence) = 0.5 × 0.25 = 0.125
PPL = exp(−(ln 0,5 + ln 0,25)/2) = √8 ≈ 2,83
```
The probabilities are already conditional on the prefixes: their multiplication does not imply independent tokens. The average `(0,5 + 0,25)/2` is not the probability of the sequence. The perplexity describes the average likelihood of the tokens retained for this calculation; it does not measure the veracity of their content.

---

Why don't the probabilities of two labels naively compare if they use different numbers of tokens? <!--anki:6434633333356465383265343439653939643264326162663932313361633839-->
?
The **probability of a sequence** multiplies the conditional probabilities of its tokens. A class written in three tokens does not directly compare to the probability of the first token of another class.

Calculate complete sequences, define the processing of variants and the end token, or choose controlled labels with an evaluated protocol. A length normalization changes the score and does not automatically make it a class probability. Calibrate the decision on representative annotated examples before using this score for abstention.

---

Do not confuse: low entropy of tokens and truth of the answer? <!--anki:3233396432613335333961613464666661333865616339393038343738303032-->
?
A low entropy indicates a **distribution focused on a few possible tokens** in context. The model can be very sure to complete a false sentence or a familiar expression.

The truth requires external verification or empirical calibration of the task. Entropy can help detect some unusual behavior, but does not constitute a factual certificate. A correct answer can also admit several formulations and therefore a strong lexical diversity.

---

Why can the application order of temperature, top-k and top-p change the sampling? <!--anki:3164333733653231663935393461643462396164323033363133356364336434-->
?
The temperature changes the relative probabilities; **top-p chooses a set according to their cumulative mass**. Applying top-p before or after this transformation can therefore retain different tokens.

Renormalizations and penalties add other dependencies to the order. To replicate an experiment, keep the actual engine pipeline, not just the parameter values. Two APIs accepting the same settings names do not guarantee an identical distribution.

---

## Scenarios

Scenario: your extraction of fields from contracts gives different results with each execution on the same document. What settings do you change? <!--anki:67437644407968463477-->
?
1. **Low temperature** (0 to 0.3): extraction does not need creativity
2. **Isolate effects**: change one parameter at a time, then test useful combinations
3. **Constrict output** with a schema, to remove shape variability ([[63-guided-generation|guided generation]])
4. **Measuring residual variability**: Even at 0 temperature, GPU calculations may vary by environment ([[114-reproducibility-variance|Reproducibility]])
5. **Test on properties** (good amount extracted) rather than on an exact string

**Trap**: Believe that `temperature=0` guarantees identical outings from one day to the next.

---

Scenario: your classifier should send the uncertain cases to a human. How do you measure the confidence of the model? <!--anki:634925695a74604d7079-->
?
1. **Logprobs**: ask for the probabilities of the tokens of the answer and compare the candidate classes
2. **Climbing threshold**: below a given probability, the demand goes to a human ([[144-ai-ux-human-in-the-loop|human-in-the-loop]])
3. **Calibrate the threshold** on an annotated game: measure actual accuracy by confidence slice
4. **Beware of verbalized trust** (“I’m sure 90%”), unreliable
5. **Monitoring** the drift of the climbing rate in production ([[93-monitoring-inference|monitoring]])

**Trap**: Use perplexity as the quality score of a response, which it does not measure.

---

## Sources

- [Hugging Face — perplexity and tokenization](https://huggingface.co/docs/transformers/en/perplexity)
- [Hugging Face — generation settings](https://huggingface.co/docs/transformers/en/main_classes/text_generation)

- [vLLM — Speculative Decoding and Digital Reproducibility Limits](https://docs.vllm.ai/en/latest/features/speculative_decoding/index.html)

## Connections
- [[61-kv-cache-attention|KV cache & attention]] — Generation token by token
- [[62-inference-optimizations|Inference optimizations]] — speculative decoding
- [[63-guided-generation|Guided generation]] — hide logs before sampling
- [[11-advanced-prompt-engineering|Prompt engineering]] — self-consistency: multiple samples, majority vote
- [[114-reproducibility-variance|Reproducibility & variance]] — why outputs vary even at temperature 0
- [[92-chainforge-evals-prompts|Evals]] — measure the effect of settings
- [[67-speculative-decoding|Speculative Decoding]] — the acceptance rule that preserves distribution
- [[131-transformer-architecture|Architecture Transformer]] — where the logs come from
- [[143-hallucinations-grounding|Hallucinations]] — calibration and detection
- [[11-llm-inference-servers|Inference Servers]] — vLLM, SGLang, TensorRT-LLM and their setting
- [[52-post-training-alignment|Post-training & Alignment]] — RLHF, DPO, GRPO and RLVR
- [[00-moc-ai-engineering|MOC AI Engineering]]
