# Causal Inference & Product Decisions — Flashcards
Tags: #flashcards #ai-engineering #classical-ml #causality #experimentation
<!-- summary: prediction or intervention, ATE and CATE, causal graph, confusion and collision, identification or estimation, hypotheses, positivity, propensity score, differences in differences, uplift and sensitivity analyses, interference between treated units, post-processing adjustment, transport of effects. -->


Why is predicting who will terminate not enough to choose who to help? <!--anki:3631623936393761336133623439396662323464393830633136303130383630-->
?
A termination score predicts a **result under the observed conditions**. To decide on an action, you also need to know who will change behavior through this action. A very high-risk user can leave even after intervention; another can remain unassisted.

Define the intervention, its cost and the desired outcome. A heterogeneous effect model seeks a variation due to the action, under explicit causal assumptions. The best ranking of risk is therefore not necessarily the best ranking of the benefits of an aid policy.

---

Do not confuse: ATE and CATE in causal inference? <!--anki:3139653434363639333361313439363562343430393065346665336635306263-->
?
**ATE** is the mean effect of a treatment on a defined population: `E[Y(1) − Y(0)]`. **CATE** conditions this effect to characteristics: `E[Y(1) − Y(0) | X=x]`.

For the same person, only one of the two potential outcomes is usually observed. Therefore, the CATE is not a direct measure of its individual effect. Specify population, intervention and horizon; a positive average effect can mask poorly helped or injured segments. Their estimation requires sufficient data and independent validation.

A beneficial campaign on average can therefore remain useless for customers who would have bought without it: predicting the purchase is not estimating the effect of the campaign.

---

What is the purpose of a causal graph before choosing the adjustment variables? <!--anki:6464643931623734623766393434666262653865396366616331336531366238-->
?
A **acyclic oriented graph** Explain the assumptions about causes and their order. A common factor can influence both intervention and outcome: the difficulty of a case influences the allocation of aid and its duration of treatment.

Look for an adjustment that blocks relevant confusion paths according to this graph. Adding all variables is not a valid rule: controlling a mediator can remove some of the total effect sought. The graph formalizes business assumptions; it is not a truth automatically deduced from correlations.

---

What is a collision bias in a causal analysis? <!--anki:6364376432626132653264663464316462643930333164613238613738663961-->
?
A **collider** is a common effect of two variables, for example `assistant_usage → open_ticket ← difficulty`. Conditioning on this variable can create an artificial association between its causes, even if they were initially independent.

Analyzing only the open tickets can compare different difficulties depending on the use of the wizard. Identify the selection filters in the graph before adjusting. The correction depends on the causal mechanism and the desired effect; a handy dashboard filter can change the validity of the entire analysis.

---

Do not confuse: identification and estimation of a causal effect? <!--anki:6131313437353335303130313461373461323539373639666261656435386331-->
?
The **Identification** determines whether the desired effect can be expressed from observations under the assumptions used. The **Estimate** Then calculates a value and its uncertainty with finite data and a statistical method.

A highly flexible predictive model can improve some estimates, but does not correct for the lack of identification. If an unmeasured common factor biases the comparison, more lines are not necessarily enough. Document first the hypotheses allowing the effect, and then the calculation protocol, diagnoses and limits of the estimate.

---

What assumptions make a causal adjustment on observational data interpretable? <!--anki:3037616464303166666237313434356138633630393063363766346539666563-->
?
For a standard adjustment, specify in particular **conditional exchangeability**, **positivity** and **consistent treatment**: no confusion not measured after adjustment, possible alternatives in the groups compared, and intervention sufficiently defined to link observed outcome and potential outcome.

The usual framework also requires dealing with interference between units: helping a member can change the outcome of his team. These assumptions are not guaranteed by a library. Business knowledge, the collection plan and sensitivity analyses determine the credibility of the conclusion.

---

Why does the lack of overlap prevent some causal comparisons? <!--anki:6563306633353161373337633466383361393564633737663738636461646438-->
?
If all the difficult folders receive help and no comparable folder remains unaided, there is a missing **alternative observed in this segment**. A regression can extrapolate a difference, without the data alone making it credible.

Examine distributions of characteristics and propensity. Restricting the population to a recovery area may be helpful, but changes the targeted effect. Otherwise, proper collection or experimentation is required. Extreme weights are a symptom to diagnose, not just a numerical problem to hide.

---

What is a propensity score and what is it used for? <!--anki:3435656636636334343831343462363138626630333161643064393130313165-->
?
The **propensity score** is the probability of receiving treatment conditional on the selected variables: `e(X)=P(T=1|X)`. It describes the attribution of the action, not the risk of the outcome.

Pairing or weighting can use it to balance observed characteristics. For a conventional ATE weighting, treatises receive `1/e(X)` and non-treatees `1/(1−e(X))`. Controlling extreme balance and weight. A good attribution predictor does not prove either the absence of unmeasured confusion or the validity of the causal effect.

If `e(X)=0,01`, a treatise weighs 100: some observations may dominate the estimate. Crunching the weights sometimes reduces the variance, but changes the bias or the population actually represented.

---

Calculation: what effect in difference if the equipped group changes from 50 to 65 and the control from 40 to 48? <!--anki:6230303962663832613734353464656439333832383665333266626163616262-->
?
The estimate is **(65 − 50) − (48 − 40) = 7 units**. It removes from the evolution of the equipped group that observed in the control.

The causal interpretation requires that, without treatment, the trends would have been parallel, with no relevant anticipation and differential shock. Consistent prior trends support this hypothesis without proving it. Several dates of adoption or heterogeneous effects require an adapted method; this simple calculation does not validate any progressive deployment.

---

Calculation: what net gain is expected for an aid costing 2 units and increasing by 3 points an issue worth 100 units? <!--anki:6533313463343133666164653437633239646339383732626163623137396132-->
?
Under a properly estimated causal effect and a linear value, the expected net gain per person assisted is **0.03 × 100 − 2 = 1 unit**. The decision must incorporate the uncertainty of this effect and other constraints.

If another segment gains only one point, the expected gain becomes −1 unit. A **uplift** policy targets the useful incremental effect, not just the raw probability of success. Evaluate the full policy on independent data with sufficient support and control for adverse effects.

---

Why don't successful rebuttal tests prove a causal conclusion? <!--anki:6563653334313566386630303430643862663861356166666438623762363364-->
?
They can **reveal a defect**, not rule out all possible defects. A placebo or negative control tests only a particular implication of the hypotheses, with limited power.

Example: No effect detected on an outcome that is supposed to be insensitive to treatment is reassuring; this does not exclude an unobserved factor influencing only the primary outcome.

Choose domain-justified controls, check what they could detect and analyze sensitivity to unobserved confusion. Report remaining assumptions and uncertainty; green diagnoses do not turn an observational study into randomization.

---

Why can the effect of an intervention depend on the treatment of other people? <!--anki:3965653663343938633262343433653362303863373135313337326665353333-->
?
**Interference** occurs when the result of a unit depends on the treatment of other units: mutual aid between colleagues, shared stock or concurrency on the same recommendations.

A comparison that assumes independent units can then measure an effect different from that expected after generalization. Identify the links and choose, if necessary, a randomization by group or a suitable plan. Define the desired effect, including direct or collective. The individual random assignment does not remove this interaction; it must be taken into account in the design and analysis.

---

Why can adjusting on a measured variable after treatment bias a causal estimate? <!--anki:6439316337316234333162383439363461663466656237323237616533303139-->
?
This variable can be **a mediator or a collider**. Controlling it can block some of the desired effect or open a parasitic association.

Define the target effect and a causal graph before choosing the covariates. A highly predictive variable is not automatically a good adjustment variable. Distinguish total effect and direct effect, with their own identification assumptions.

---

Why does a measured causal effect in one population not automatically transfer to another? <!--anki:3965626335353665323439303464613339343638346461383134623239643639-->
?
The effect may vary with **the characteristics, context or implementation of the treatment**. A locally valid experiment does not guarantee the same value elsewhere.

Comparing populations and mechanisms, identifying relevant moderators and verifying data coverage. Reweighting does not resolve the complete absence of certain profiles or a change in mechanism. Documenting transport assumptions and confirming on target where possible.

---

## Scenarios

Scenario: Assistant users close their tickets faster, but it's mostly experienced teams. How do you rate the effect? <!--anki:6532626231303561636330303466323062393935396463616166366533343361-->
?
1. **Definite intervention and outcome**, with population and measurement time.
2. **Represent plausible causes**, including experience and difficulty of tickets.
3. **Privileging appropriate randomised assignment** if feasible.
4. **Otherwise, specify identification**, check recovery and pre-use variables.
5. **Report sensitivity and limits**, without assigning all the observed deviation to the assistant.

**Trap**: Adjust with measured satisfaction after use without defining what effect this allows to estimate.

---

Scenario: all complex files automatically receive assistance and no other files receive it. Can we estimate its effect everywhere? <!--anki:3933666339646137653866353463383961363934343165336631393432663233-->
?
1. **Check attribution rule** and actual support in each segment.
2. **Report the positivity violation** for a standard fit comparison.
3. **Identify a comparable population** if it exists and specify the new target.
4. **Study a collection plan or other design**, with explicit assumptions.
5. **Distinguish extrapolation and evidence**, limiting the scope of recommendations.

**Trap**: Add a more complex model to make the missing information.

---

Scenario: a difference of differences assigns a gain to an assistant launched at the same time as training reserved for the equipped group. What do you conclude? <!--anki:6164373062623661376537393466623439623961643230346463383730306363-->
?
1. **Identify joint change** and its plausibility as a cause of gain.
2. **Review the targeted effect**: assistant alone or assistant program plus training.
3. **Search for a group or an informative calendar** that allows for a credible separation.
4. **Examine trends, composition and shocks**, with appropriate uncertainty.
5. **Report what is identifiable**, or design a new experience to isolate the wizard.

**Trap**: Name "model effect" the effect of a set of inseparable changes.

---

## Sources
- [Hernán & Robins — Causal Inference: What If, Assumptions and Graphs](https://miguelhernan.org/whatifbook)
- [PyWhy — model, identify and estimate an effect](https://www.pywhy.org/dowhy/v0.13/user_guide/causal_tasks/estimating_causal_effects/index.html)
- [PyWhy — Limits and Rebuttal of Estimates](https://www.pywhy.org/dowhy/v0.13/user_guide/refuting_causal_estimates/index.html)
- [SHAP — distinguish prediction and causal decision](https://shap.readthedocs.io/en/latest/example_notebooks/overviews/Be%20careful%20when%20interpreting%20predictive%20models%20in%20search%20of%20causal%20insights.html)
- [Callaway & Sant’Anna — differences and multiple adoptions](https://arxiv.org/abs/1803.09015)

## Connections
- [[99-statistics-experimental-decisions|Experimental statistics]] — distinguish accurate estimate and valid conclusion
- [[97-evals-online-ab-testing|A/B testing]] — Designing a Randomized Intervention
- [[177-model-explainability|Explainability]] — does not transform attribution into causality
- [[174-recommendation-ranking|Recommandation]] — consider exposure in newspapers
- [[00-moc-ai-engineering|MOC AI Engineering]]
