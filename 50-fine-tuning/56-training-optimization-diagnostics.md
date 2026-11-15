# Training optimization & diagnostics — Flashcards
Tags: #flashcards #ai-engineering #fine-tuning #optimization #deep-learning
Verified on: 7 October 2026
<!-- summary: loss and business metric, backpropagation, learning rate, AdamW, learning curves, diagnostic micro-lot, normalized accumulation, clipping, mixed precision, PyTorch modes and label masking, train loss comparability and validation, supervised tokens, order of transformations. -->


Do not confuse: loss of drive and business metric? <!--anki:3036653364613531613036643462383261306238306563643263626633323664-->
?
The **loss** provides an optimized signal to adjust parameters; the **business metric** measures the expected result. Reducing tokens cross-entropy does not guarantee more correctly extracted invoices: the many format tokens can hide errors on amounts.

Follow the two on separate data. Choose the checkpoint according to a validation protocol set in advance, with controls on the abilities to preserve. The final test is not used to choose the time.

---

What does the backpropagation calculate and what does the optimizer do next? <!--anki:6436636137376438303539333461666561613434383366626636363431326131-->
?
The **retropropagation** applies the chain bypass rule to the calculation graph to obtain the gradients of the loss relative to the parameters. The **optimizer** uses these gradients to modify the parameters; therefore, calculating the gradients does not update the weights.

For a simple descent: `θ ← θ − η × gradient`, with `η` the learning rate. Check that a parameter supposed to learn receives a gradient and changes after a step, especially when part of the model is frozen.

---

How to diagnose an inadequate learning rate? <!--anki:6561326133613134343133333432623662343232386638313263303730373138-->
?
Too high a rate can produce oscillations, divergence or unfinished losses; too low a rate can give an almost invisible progression. These symptoms are not enough for diagnosis: invalid data, normalization and gradient errors can imitate them.

Compare a few rates on the same small game, with constant configuration and budget. Observe loss, standard gradients and amplitude of updates. A warmup gradually increases the initial rate; it does not repair an incorrect label set.

---

Do not confuse: L2 penalty and weight decay with AdamW? <!--anki:6336613737626566316436333438373961643331303939363732366366636364-->
?
The **Penalty L2** adds an end to the loss and therefore to the gradients. **AdamW** decouples weight contraction from adaptive gradient transformation. With an adaptive optimizer, The two operations are generally not equivalent.

The coefficient must be selected on validation, along with the other hyperparameters. Documenting which parameters are affected: biases or normalization parameters can be excluded depending on the recipe. Changing the name of the optimizer without controlling these groups changes the experience in an inconspicuous way.

---

What do train loss and validation curves reveal? <!--anki:3166663138303666616463373437656362313930643736663964666163393461-->
?
A falling train loss while the validation goes back suggests **overlearning**. Two high losses can signal underlearning, poor performance, or faulty pipeline. Comparing curves assumes consistent definition and normalization of the loss.

Dropping or increasing can make the train more difficult than validating, so a gap is not automatic proof. Link curves to concrete errors and select a checkpoint on validation before touching the final test.

Compare also by length: an average dominated by many easy tokens can mask the degradation of rare business fields.

---

Why try to overlearn a tiny batch before an expensive workout? <!--anki:3762373161633066643138653434356539613933386633356165346664373135-->
?
It is a **test of the operation of the pipeline**: on a few clean and fixed examples, a sufficiently flexible model should be able to greatly reduce its loss. A failure orients to labels, masks, gradients, frozen or optimizer parameters before accusing the volume of data.

Temporarily disable increases and simplify regularization for this diagnosis. Success proves a local memorization ability, not generalization. Then reset the normal settings and evaluate on independent observations.

Example: Repeat eight instruction-response pairs and verify that the response tokens receives gradients. A constant loss despite this test warrants inspecting the pipeline before adding GPU.

---

Calculation: Which batch is effective with 4 examples by GPU, 8 accumulations and 2 data replicas? <!--anki:3738336431346232313232633463613062383536373334336530323864613530-->
?
The actual batch contains **4 × 8 × 2 = 64 examples** per update, if each replica deals with separate examples and all micro-batches are complete.

Accumulation makes several backpropagations before an optimizer step to limit the memory of activations. It does not necessarily make training identical to a physical batch of 64: BatchNorm, hazards and normalization may differ. Tensor parallelism GPU do not multiply this batch if they work on the same examples.

---

Why normalize the accumulation by the tokens actually supervised? <!--anki:3038623765386562653162313437636638396263653538333563393630396361-->
?
If two micro-batches contain respectively **100 and 900 tokens Supervised**, average their average losses gives them the same weight, Instead of weighing each token as well. For an average goal per token, Accumulate amounts of losses with a coherent total denominator.

Exclude padding and masked labels from this denominator. In distribution, take into account the reduction of gradients and global counts. Divide only by the number of accumulations suitable for micro-batches of the same weight, not for all variable sequences.

---

What does gradient clipping protect and what does it not correct? <!--anki:3863346663646530373037323462646161356639373431323631613365313931-->
?
**clipping by standard** reduces a gradient that exceeds a threshold, preserving its direction when it comes to a global resizing, and limiting the effect of a peak on the update.

Log the standard before clipping and its frequency: a permanent activation prompts to look for excessive rate, outliers or improperly normalized loss. With gradients scaled, remove this scale before clipping. Clipping does not transform NaNs into valid gradients and does not replace diagnosis.

---

Do not confuse: model.eval() and gradient deactivation in PyTorch? <!--anki:6236346430303366383035613432356262323136626233386134303039373262-->
?
**`model.eval()`** changes the behavior of modules like dropout and BatchNorm; **`torch.no_grad()`** disables autograd graph recording in its context. Both are independent.

Example: with `no_grad()` but without `eval()`, a dropout remains active and BatchNorm can still refresh its training statistics. With `eval()` alone, operations can still build a gradient graph and consume memory.

For normal validation, combine the two, then restore the previous mode before continuing training. To calculate a sensitivity to the input, keep the gradients even in evaluation mode: no learning and no derivatives are two different choices.

---

Why can mixed precision produce NaNs during training? <!--anki:3133323837303666366362353464303239643633323432306562306365323231-->
?
Some operations exceed the numerical range of the chosen format, or their gradients become too small to be represented. The **FP16** and the **BF16** do not have the same range of exhibitors; their behavior also depends on the operations kept in FP32.

Locate the first unfinished value and compare a small case in FP32. The gradient scaling helps against the subflow in FP16, but does not correct a division by zero or invalid data. Reducing the rate without identifying the origin can only hide the problem.

---

Why does less validation loss than training loss not prove better generalization? <!--anki:3763653538333863656465343437333961383633366164353439313430313531-->
?
**Measurement conditions** may differ: active dropout during training, regularization included in one loss but not the other, data increase or populations of different difficulty.

Compare the two games with the same definition of loss and a consistent evaluation protocol, without gradient. Then examine the business metrics and representativeness. A curve reversal is neither automatically a bug nor proof of no overlearning. Also check that the displayed training loss does not summarize previous steps with a less trained model.

---

Why track the number of tokens supervised in addition to the number of batches during a fine-tuning? <!--anki:6465353133363566666366653438323262663334386433306630343933613330-->
?
Two batches of the same size can contain **very different amounts of learning signal**, depending on length and masking. An almost entirely masked batch can contribute very little.

Following tokens useful, normalized loss and scheduler progression helps to interpret curves. Comparing experiments with an identical normalization convention. An equal number of steps does not mean equal exposure to data or equal amount of calculation.

---

Why does the order between unscale and gradient clipping count in mixed precision with loss scaling? <!--anki:3136656537643034393662383436323939626635353162346661616239643663-->
?
The clipping must focus on **gradients at their real scale**. Applying the threshold to gradients multiplied by the scaling factor is like using a different effective threshold.

Unscaling before clipping, depending on the API used, and then performing the optimization step. Check for unfinished gradients and skipped steps. This is for workouts that actually use a loss scaler; it does not mean that any BF16 workout requires one.

---

## Scenarios

Scenario: the loss of your fine-tuning decreases, but the extracted amounts become less accurate. What do you check? <!--anki:3266386265386562656466353437306239653631353866313939313538303162-->
?
1. **Check supervised labels**: assistant, uprights, padding and tokens.
2. **Compare the rendering of examples** in the format used inference, including truncation.
3. **Measuring field accuracy** on validation, separate from the average loss per token.
4. **Inspect errors**: units, decimals, contradictory or too repetitive examples.
5. **Compare checkpoints** to baseline and keep the final test independent.

**Trap**: Extend training only because the train curve goes down.

---

Scenario: after activation of gradient accumulation, the loss explodes on long documents. How do you isolate the problem? <!--anki:3765343861363266383932623462343161373831323964613165323166643334-->
?
1. **Fig a reproducible batch** containing short and long documents.
2. **Count supervised tokens** in each micro-batch and check for normalization.
3. **Control steps**: reset at the right time, one step of optimizer after accumulation.
4. **Compare gradients** with an equivalent physical batch if memory allows.
5. **Examine digital accuracy** and clipping only after this comparison.

**Tip**: Change learning rate, batch, and loss simultaneously, then assign the result to a single cause.

---

Scenario: a workout doesn't even remember 16 own examples. Where do you start? <!--anki:6234643731646365363866633431306339643632633665313561616661393664-->
?
1. **Read entries and labels that are really tensorized**, with masks and target offsets.
2. **Check that the loss depends on the predictions**, without accidental detachment of the graph.
3. **Inspect gradients and weights** before and after a step for entrainable parameters.
4. **Simplify calculation**: FP32, no increase, minimum configuration.
5. **Compare a few learning rates**, then re-introduce optimizations one by one.

**Trap**: Launch more GPU before demonstrating that the pipeline is learning.

---

## Sources
- [PyTorch — boucle d'optimization](https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html)
- [PyTorch — autograd and evaluation modes](https://docs.pytorch.org/docs/main/notes/autograd.html)
- [PyTorch — mixed precision and clipping](https://docs.pytorch.org/tutorials/recipes/recipes/amp_recipe.html)
- [PyTorch — CrossEntropyLoss and labels ignored](https://docs.pytorch.org/docs/2.14/generated/torch.nn.CrossEntropyLoss.html)
- [Loshchilov & Hutter — Decoupled Weight Decay Regularization](https://arxiv.org/abs/1711.05101)

- [PyTorch — accumulation of gradients in mixed precision](https://docs.pytorch.org/docs/main/notes/amp_examples.html)

- 14 November 2026 — Unscale before clipping: [PyTorch 2.15 — AMP examples](https://docs.pytorch.org/docs/2.15/notes/amp_examples.html).

## Connections
- [[51-fine-tuning-adaptation|Fine-tuning]] — diagnose an adaptation before making it more complex
- [[54-distributed-training|Distributed training]] — effective batch and gradient reduction
- [[172-ml-validation-metrics|Validation ML]] — separate selection and final estimate
- [[00-moc-ai-engineering|MOC AI Engineering]]
