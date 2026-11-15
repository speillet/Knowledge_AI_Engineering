# Model explainability & diagnostics — Flashcards
Tags: #flashcards #ai-engineering #classical-ml #explainability #shap
Verified on: 8 October 2026
<!-- summary: Local or global explanation, significance by permutation, correlated variables, SHAP contributions, reference population, log-odds, PDP and ICE, actionable counterfactuals, generated justifications and explanation fidelity, stability of explanations, importance and causality, explanation of transformations. -->


Do not confuse: Local explanation and global explanation of a model? <!--anki:3236346461646234333634363465323038633662376664376335303433323061-->
?
A **local** explanation describes a particular prediction; a **global** explanation summarizes the behavior of the model on a population. The dominant variables on average may not explain an atypical case.

Choose the scale according to the question: diagnose a poorly classified ticket or understand the general routing policy. Example: the subscribed offer dominates the routing on average, but this ticket switches because of the word "reimbursement" in its object. Specify model, output and population analyzed. Aggregating local explanations can hide opposing effects between segments; an overall importance is therefore not enough to justify each individual decision.

---

What does the permutation significance of a variable measure? <!--anki:3432346461383838626138373436326338373436336662383962353132656339-->
?
It measures the **degradation of a score** when mixing a variable in a given set, keeping the trained model, and testing its predictive dependence on this information for the chosen metric.

Use a set held apart and repeat permutations to measure variability.
```python
from sklearn.inspection import permutation_importance
r = permutation_importance(model, X_test, y_test, scoring="roc_auc", n_repeats=10, random_state=0)
r.importances_mean, r.importances_std     # average decrease in AUC and dispersion
```
The result depends on the model, population, and score; this is not an absolute property of the variable. Swapping can create unrealistic observations, especially when the variables are highly dependent.

---

Calculation: What is the significance of switching from 0.84 to 0.79 on average? <!--anki:6562656232353633336231383461343639653466363031323031336331313966-->
?
For a score of which **a high value is better**, the importance is worth **0.84 − 0.79 = 0.05**, i.e. five points of accuracy.

With a loss of which a low value is better, interpret the increase in loss with the appropriate convention. The result does not indicate that the variable causes 5% decisions. It describes a particular disturbance of the model; a negative importance may come from noise or an unfavourable dependence on generalization.

---

Why can two correlated variables have low individual importance? <!--anki:6166306366623936656532663437303362393761643035613561366131346262-->
?
They can provide a **substituable information**: when one is mixed, the other still allows to predict well. Example: `revenu_mensuel` and `revenu_annuel` each seem useless, because mixing one leaves the other intact. A small individual importance does not prove that the group of variables is useless.

Examine their dependencies, test a group permutation, or compare retrained models without the group. These experiments answer different questions: dependency on the current model or the ability to learn without this data. They must retain the validation protocol; removing a variable based solely on a ranking of importance can deceive.

---

What is a SHAP contribution? <!--anki:3335653430666264363334303434656138326437633235376333623661376131-->
?
A contribution **SHAP** assigns to a variable a share of the difference between the explained output and a reference value, in a set of defined coalitions. Under the property of additivity, reference and contributions reconstitute this output, to the nearest approximation error.

The result depends on how to represent the absence of a variable and the dependencies taken into account. It explains the model under these conventions, not automatically the causes of the real phenomenon. Check which class and which output unit are actually explained:
```python
sv = shap.TreeExplainer(xgb_binaire)(X_test)    # explained: margin in log-odds
sv.base_values[0] + sv.values[0].sum()           # ≈ predicted margin for line 0
```

---

Why does the choice of reference population change a SHAP explanation? <!--anki:3962326137306130336361383462306139643530626233343761613162363139-->
?
The precise reference **to what** the prediction is explained. Comparing a request to the average customer or to requests from the same service changes the basis and the possible attributions, even if the prediction remains the same. The income of an applicant can thus contribute positively to all customers, and negatively to the only customers in his region, better paid.

Select a representative set of the question asked, version it and document its sampling. Dependent variables require special attention to the masking mechanism. An evolution of the graph may come from a new reference rather than a change of the model; keep the two versions to compare.

---

Calculation: SHAP contributions of +0.8 and +0.4 are added to a base of −1 in log-odds; what probability is obtained? <!--anki:6637363636646338303133393436346661613735356436396562386137613733-->
?
The contributions are added first in **the space explained**, here the log-odds:
```text
z = −1 + 0,8 + 0,4 = 0,2
p = 1 / (1 + exp(−0,2)) ≈ 0,5498
```
The final probability is therefore about 55%. We can not treat +0.8 as an increase of 80 points of probability. Check the unit announced by the explainer: some configurations explain a probability, others a margin or another transformation of output.

The basis is to explain it and its reference population, not necessarily to the gross positive rate. Add all contributions in the space announced before the reverse transformation; transform each contribution separately only with a justified interpretation.

---

Do not confuse: PDP and ICE curves? <!--anki:3565633339626133663835313461366538306264313030633130303766336266-->
?
A **PDP** averages the predictions obtained by varying a feature; **ICE curves** show these variations for each observation. The average can mask opposite behaviors: a flat PDP for discounting, while ICE curves go up for new customers and down for regulars. `PartialDependenceDisplay.from_estimator(model, X, ["discount"], kind="both")` plots both.

Both can evaluate unrealistic combinations when variables are dependent. Examine areas where data exist and supplement with suitable conditional analyses. A rising curve describes a model's reaction to these artificial inputs, not evidence that actual intervention on the variable would increase the target.

---

What makes a counterfactual explanation really actionable? <!--anki:6139353063643962643034313430663939383265333839313630653762626331-->
?
It proposes a **workable change** of entries that modifies the decision of the model, respecting immutable variables, dependencies and the cost of the action. "Reduce the outstanding card of 400 €" may constitute a recourse; "be five years younger" or modify a variable out of reach of the user does not provide any.

Check that the point obtained is plausible and that the recommendation resists small variations. Crossing the boundary of a model does not prove an improvement in the actual situation. An action board requires additional causal assumptions and a validation of its effect.

---

Why is a justification written by a LLM not proof of the decision mechanism? <!--anki:3461363763306332646438373433646162653337623239393239303135656663-->
?
The generated text is an additional **output**, not a guaranteed access to the calculation that produced the decision. A model can give a plausible justification while using other indices. Turpin et al. always place the correct answer in (A) in the examples few-shot: the model chooses (A) more often, without its written reasoning mentioning this index.

For a pipeline, expose the verifiable facts: inputs used, rules applied, sources, and result of the tools. Test the statements of the explanation against these traces. Readability facilitates the use, but does not replace either fidelity to the system or accuracy of the decision.

---

How to check that a model explanation is useful and faithful? <!--anki:3933333337656133383132613434643939616332313439343037383630613132-->
?
Testing for **explained output fidelity**, stability in the relevant context, and usefulness to the human task. Correct additive decomposition is a technical control; it does not guarantee causality or understanding.

Possible test: compare the effect of removing variables deemed important to a random withdrawal, with a plausible replacement rule. Correlations and interactions limit this test; out-of-distribution disturbance can be misleading. Also measure the help to detect an error or choose an action, rather than the only persuasive power. Close predictions may have different reasons: do not impose blind invariance.

---

Why test the stability of an explanation on nearby entries before showing it to a user? <!--anki:3264383963343462373236353463343138316430373663346635663233336533-->
?
A **Unstable explanation** can give very different reasons for two almost identical cases, Even if the prediction varies little. It becomes difficult to use when deciding on a correction.

Apply plausible perturbations that preserve meaning and compare prediction, contributions and recommendations. Control units, reference population and correlated variables. A variation can be legitimate near a border; document it rather than promise absolute stability. Validate model fidelity and user utility separately: a stable explanation may remain false or unactionable.

---

Why should an explanatory counterfactual respect the feasibility constraints between variables? <!--anki:3962633839386534383734373434373161323965303633623037383630303135-->
?
A change can improve the score while describing **an impossible situation**: reduce the age by retaining thirty years of seniority, or change an income without respecting its components.

Constrain immutable variables and their dependencies, then distinguish between mathematical suggestion and actually available intervention. Check the stability of the proposal. A plausible counterfactual for the model is not automatically causal, legal or feasible for the person concerned.

---

Why explain the complete pipeline rather than just the final estimator? <!--anki:6264373666653338663361363435323338626662386334353164306333393436-->
?
The estimator often receives **transformed, imputed, or encoded variables**. A contribution on these columns may be incomprehensible or misleading to the user.

Link transformations to business inputs, verify their consistency and specify the point of reference of the explanation. Test missing values and unknown categories. A faithful explanation to the final model still needs to be translated correctly to explain the decision of the system.

---

## Scenarios

Scenario: two highly correlated variables have almost zero permutation significance, and the team wants to remove them. What do you propose? <!--anki:3837326264343461346663643466633238323939353534373932633863386536-->
?
1. **Check the quality of the model** and the game on which the importance was calculated.
2. **Examine correlation** and possible substitutions between variables.
3. **Switch the group together** to measure the dependency of the current model.
4. **Run without the group** with separate validation to test the deletion decision.
5. **Compare quality, cost and segments**, then document what each test shows.

**Trap**: interpret low individual importance as lack of useful information.

---

Scenario: the business reads a SHAP contribution of +0.7 as "70% risk plus". How do you fix? <!--anki:3431633238323565336661303438336461613865393037363437333965653834-->
?
1. **Identify the space explained**: probability, log-odds or other score, as well as class and reference.
2. **Reconstitute output** with all contributions and check expected additivity.
3. **Show an example in the correct unit**: if the reference is −2 log-odds, this contribution is +0.7 and the others are zero, the total is −1.3. The sigmoid goes from about 11.9% to 21.4%, i.e. **9.5 points**, not 70%.
4. **Fix interface**: display unit and reference; do not transform each contribution separately by the sigmoid, which is nonlinear.
5. **Recall Predictive Range**: This decomposition is not the causal effect of an intervention.

**Trap**: confuse additive contribution to score and additive variation in probability.

---

Scenario: an explanation says that contacting support increases the risk of termination, and the product wants to hide this button. What do you say? <!--anki:3134376664316130383566393433636639346536366465383130633962396365-->
?
1. **Distinguish association and intervention**: prior difficulty may cause contact and termination.
2. **Audit the temporality** of the contacts and the population used to explain.
3. **Formulate the causal question** regarding media access and retention.
4. **Choose a suitable protocol**, with user constraints and quality measures.
5. **Evaluate the actual effect** before turning predictive importance into product policy.

**Trap**: act on the symptom learned by the model by aggravating the user problem.

---

## Sources
- [scikit-learn — importance by permutation and correlations](https://scikit-learn.org/stable/modules/permutation_importance.html)
- [scikit-learn — PDP and ICE](https://scikit-learn.org/stable/modules/partial_dependence.html)
- [Lundberg & Lee — A Unified Approach to Interpreting Model Predictions](https://arxiv.org/abs/1705.07874)
- [SHAP — read a waterfall plot and its units](https://shap.readthedocs.io/en/latest/example_notebooks/api_examples/plots/waterfall.html)
- [SHAP — limits causal interpretations of a predictive model](https://shap.readthedocs.io/en/latest/example_notebooks/overviews/Be%20careful%20when%20interpreting%20predictive%20models%20in%20search%20of%20causal%20insights.html)
- [Karimi et al. — Model-Agnostic Counterfactual Explanations for Consequential Decisions](https://proceedings.mlr.press/v108/karimi20a.html)
- [Turpin et al. — fidelity limits of generated justifications](https://arxiv.org/abs/2305.04388)

## Connections
- [[171-ml-model-selection|Choose a model]] — distinguish performance and understanding behavior
- [[156-responsible-ai|IA responsable]] — analyze the effects and limitations of an explanation
- [[178-causal-inference-decisions|Causal inference]] — validate the effects of proposed actions
- [[00-moc-ai-engineering|MOC AI Engineering]]
