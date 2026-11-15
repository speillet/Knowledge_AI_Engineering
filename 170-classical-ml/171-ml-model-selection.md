# Classic ML: choose and understand the — Flashcards
Tags: #flashcards #ai-engineering #classical-ml #models #baseline
<!-- summary: rules or ML or LLM, target formulation, baselines, regressions, regularization, trees, random forest and boosting, clustering, preprocessing, missing data and cost of ownership, unknown categories in production, business baseline, capacity and data. -->


How to choose between rules, classic ML and LLM for a business need? <!--anki:6661353466646534356365313436373439663763316530386363633734333530-->
?
From the **Decision expected**, available data and the cost of errors. Rules are appropriate for an explicit and stable policy; A supervised model learns a relationship from labeled examples. a LLM Above all, it brings language processing and generation capabilities.

Example: Decline a refund beyond 500 € is a rule; estimate a risk of fraud on 40 labeled variables, of a supervised model; read the reason written by the customer, of a LLM. Extraction by LLM followed by a tabular model may be relevant. Additional complexity must bring a measurable gain in quality or maintenance.

---

How to set a supervised target before choosing an algorithm? <!--anki:6361663033653337336436613433356639386630636230633635373037396664-->
?
Specifying **the predicted unit, the decision time, the horizon, and the label** is incomplete; "for each active subscription on the first of the month, predict its termination in the 30 days" defines a testable task.

Variables must be available at the time of the decision. Labels require waiting for the end of the horizon: a subscription observed for five days cannot yet be considered a negative to 30 days. This definition conditions the time division and collection.

---

Do not confuse: classification, regression and clustering? <!--anki:3636313061303366326164643436656161633537306134646361623337323035-->
?
**classification** predicts a known category, such as the type of a ticket. **regression** predicts a quantity, such as its resolution time. **clustering** groups observations according to a representation and a notion of proximity, without imposed class labels.

An discovered group is not automatically a useful business category; you need to look at the examples, the stability of the groups and how they are used. Choosing the task according to the decision to be made: creating ten groups does not necessarily help to route to the five existing teams.

---

Which baseline to build before a complex predictive model? <!--anki:6536376232316439373065333461623239383837346531333266383635376438-->
?
Measure one **simple and actionable reference** majority class for a classification, average or median for a regression by loss, existing business rules, or linear model. To provide for a series, A recent or seasonal value may be more relevant than a constant.

Evaluate this reference with exactly the same observations and metrics as the candidate. Example: The keyword routing rule already sends 81% tickets to the right team; it is this score, not chance, that the model must beat. Also keep the cost and latency: a low score gain may not justify a more fragile string.

---

What does a linear regression mean and when is it useful? <!--anki:3230383030383231623732663437363261626131623636656633613031396534-->
?
It represents the prediction by a **weighted sum of the variables**, with an intercept. It is a quick reference when additive effects are a reasonable approximation. Interactions or transformations can enrich the variables while maintaining a linear relationship in the coefficients.

An extrapolation can become absurd: learned about 20 to 120 m², `prix = 50 000 + 4 000 × surface` announces 1.65 million euros for a warehouse of 400 m2. A coefficient describes a conditional association in this model; it does not demonstrate that an intervention on the variable would have this causal effect.

---

Why is logistic regression used to classify? <!--anki:6136336230616464363032353437353638366637663036626532376138633466-->
?
In the binary case, it transforms a linear score by a **sigmoid** to produce an estimated probability of the positive class. A threshold then converts this probability into a decision; despite its name, the final task is a classification.

It provides a compact and fast baseline, especially with textual or tabular variables. The quality of the probabilities must be checked on independent observations. The threshold of 0.5 is not an obligation: in order not to miss the frauds, a team can review any transaction above 0.3, depending on the cost of errors and the ability to review.

---

How does regularization limit overlearning? <!--anki:6538633264316533643265343433613061303939626533343330306465356237-->
?
It penalizes some complex solutions during training. For a linear model, **L2** reduces the coefficients; **L1** can cancel some. We accept a less precise adjustment of the train to better generalize.

The intensity is chosen on validation, with a scale of the variables adapted. Attention to the meaning of the parameter: in `LogisticRegression` of scikit-learn, `C` is the inverse of the force, so `C=0.01` regularizes much more than `C=1`, while the `alpha` of `Ridge` grows with it. A penalty too strong product of the under-learning. It does not yet correct a false data; it can not exploit a false data;

---

How does a decision tree learn from interactions? <!--anki:6538323032383132316466343433376262336232346537663863653066336433-->
?
By successive **tests**: a separation acts only on observations that have reached its node. The effect of a variable thus depends on the previous separations.

Example: a branch tests the seniority, then the activity only in new customers. A low activity can then increase the prediction of departure at home, without changing that of old customers. The sheets estimate their prediction with the examples of training received.

The tree can represent an interaction without being created manually, but learning does not guarantee to find it. Limiting leaf depth and minimum leaf size, then testing stability and generalization; a legible branch is not a causal relationship.

---

Do not confuse: random forest and gradient boosting? <!--anki:3162346437366331633737343461333839316135333262373366323730313763-->
?
A **random forest** aggregates diversified trees by sampling observations and variables; their combination reduces variance in particular. The **gradient boosting** gradually adds trees to improve a loss function, following the signal left by the current set.

Boosting is an important candidate on tabular data, but does not always win. Example: a forest of 500 deep trees is not much adjusted; a boost of 2,000 deep trees 6 at the 0.05 rate requires an early shutdown on validation. Compare the two with an explicit adjustment budget. Depth, number of trees and, for boosting, general learning rate.

---

When to choose a tabular model over a LLM? <!--anki:3365336236643265343633653435366362646136643839623961633036336339-->
?
When we have **Structured variables and labels** for a stable target, a tabular model often offers a compact solution to be tested: operational risk score, deadline, probability of abandonment. It avoids serializing each number in a prompt and can serve at low latency.

Compare on a realistic test rather than assuming its superiority. Free text can justify embeddings or upstream extraction. Include cost of variable preparation, retraining frequency and availability of data in production.

---

Why is preprocessing part of the deployed model? <!--anki:6666613662313664393338303434633039663034653636393630303565646361-->
?
The model learns about a specific **representation**: column order, imputation, normalization, category encoding. These transformations must be recorded and reused with weights. Relearn normalization on each request or change the order of the columns changes the meaning of the entries.

Learn the transformations on the train, then apply them to other games.
```python
pipe = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), LogisticRegression())
pipe.fit(X_train, y_train)               # Median and scales learned on the train alone
joblib.dump(pipe, "model-v3.joblib")    # transformations and weights versioned together
```
A versioned string prevents notebook and service from reconstructing the same variables differently. Also define the behavior in front of a missing column.

---

How to handle numerical and categorical variables without creating a false structure? <!--anki:3533373434353664643636353432376138646464323234366439323236356333-->
?
Adapt the encoding to the method. A **standardization** helps many regularized linear models and distance methods; trees based on thresholds generally need it less. Code Paris = 1, Lyon = 2 and Marseille = 3 would make a linear model believe that Marseille is worth "more" than Paris: an indicator encoding avoids.

`OneHotEncoder(handle_unknown="ignore")` encodes a new city with zeros instead of failing. An encoding using the target must be learned without revealing the label of the encoded observation: `TargetEncoder` of scikit-learn crosses the folds during `fit_transform`.

---

Should a missing value always be replaced by zero? <!--anki:3936623264623266636266373466646339336663393234666161383333616139-->
?
**No: Zero often carries a different business sense from absence.** Unknown income is not zero income. Choose a suitable imputation, learned on the train, and possibly a variable indicating absence; some models process it directly.

Examine why information is missing. A field filled only after investigation can indirectly reveal the target or a process unavailable to prediction. Monitor absence rates in production: a collection failure should not be silently transformed into a customer profile change.

---

When does clustering bring concrete value? <!--anki:6561653439636339666238353439343761643964646366393263323339303934-->
?
To **explore populations**, organize examples to annotate or discover families of errors. The result depends on the variables, their scale, distance and algorithm. For example, k-means favors compact groups around centroids and requires to choose their number.

Check examples, stability, and utility for a business action. A good geometric index does not prove that the groups correspond to real needs. Atypical points can be important rather than just noise to remove.

---

Why is a variable important for a model not necessarily a cause? <!--anki:6334663162333634336263313462653362396264366536313130396661323865-->
?
The model exploits **predictive associations**, which may come from a common factor, a leak, or a proxy variable. A high level of contact to support does not prove that preventing these contacts would reduce terminations.

The significances also depend on the correlated variables and the method of calculation. Measuring them on data held apart and examining errors helps to understand behavior. Estimating the effect of an intervention requires an appropriate causal protocol, not just explaining the prediction.

---

Why should an ML pipeline predict the categories never seen during training? <!--anki:3061306532383633346362333463316338626430386637666535643736336135-->
?
A **new category** appears naturally in production: country, product or channel unreleased. An encoding that fails or assigns an arbitrary meaning to it makes the pipeline fragile.

Define explicit behavior: unknown category, compatible representation, or controlled rejection depending on the task. Learn preprocessing on the workout, then test missing categories and missing values in the contract validation. Monitor their frequency by variable. Treating them without technical exception does not guarantee a good prediction; an increase may require a review of the data or model.

---

Why can a “last known value” baseline beat a complex model? <!--anki:3535336630643661316437323436356162346130316134633462646136303831-->
?
If the phenomenon is **very persistent**, the recent value already contains a large part of the signal. A more flexible model can especially add variance and cost.

Compare on the same horizon and with the same information available. Examine the segments where the baseline fails, then justify the complexity by a gain out of training. A strong baseline also helps to detect leaks when a model seems abnormally efficient.

---

Why isn't increasing model capacity the first response to inconsistent labels? <!--anki:3230656631393938656439643434653839376639373163653837346538643464-->
?
A more flexible model can **memorize contradictions** without learning a useful rule. Validation performance will not necessarily progress.

Analyze disagreements, target definition, and features available at the time of prediction. Correct the annotation process or represent uncertainty when it is real. Model complexity does not replace a measurable and consistent target.

---

## Scenarios

Scenario: you are asked for a LLM agent to predict the delivery time from twenty columns and two years of history. What do you propose? <!--anki:3364313230656333323766333463396362303563626536393361346335383130-->
?
1. **Definite target**: time from which moment, with what information available at that moment.
2. **Build references**: usual time per trip, linear model and trees, evaluated over a future period.
3. **Measure useful errors**: deviations by region, extreme delays, cost of underestimations.
4. **Compare full cost**: collection of variables, serving, maintenance and eventual LLM.
5. **Reserve language** to textual data or explanations if their value is demonstrated.

**Trap**: Integrate the actual date of shipment when the prediction must be made before it is known.

---

Scenario: a tree gets 99% success on the train and 68% on validation. How do you diagnose the problem? <!--anki:6534366630633362326131663436666162306338316336623062643237356230-->
?
1. **Check cutting and labels**: duplicates, groups, dates and even target definition.
2. **Compare a baseline** to see if 68% is progress.
3. **Limit complexity**: depth, minimum number of examples per sheet, suspicious variables.
4. **Examine learning curves** and error segments to distinguish lack of data and inadequacy of variables.
5. **Retest on validation**, keeping the final test independent.

**Trap**: Only look for a more powerful algorithm while the tree already memorizes the train.

---

Scenario: a complex model gains 0.3 quality point but multiplies latency by ten. How do you decide to deploy it? <!--anki:6666386330363161663838353430386438333736373564333237313661386639-->
?
1. **Measuring gain uncertainty** on the same examples and checking for important segments.
2. **Translate the gain** into really improved decisions and avoided error cost.
3. **Check for latency, throughput, memory, and variable availability constraints**.
4. **Encrypt operation**: monitoring, retraining, dependencies and possibility of backtracking.
5. **Choose by net value**, possibly with routing to the complex model for only difficult cases.

**Trap**: choose the best average score without checking that it brings a usable improvement.

---

## Sources
- [scikit-learn — linear models](https://scikit-learn.org/stable/modules/linear_model.html)
- [scikit-learn — sets of trees](https://scikit-learn.org/stable/modules/ensemble.html)
- [scikit-learn — pretreatment](https://scikit-learn.org/stable/modules/preprocessing.html)
- [scikit-learn — clustering](https://scikit-learn.org/stable/modules/clustering.html)

- [scikit-learn — preprocessing and validation errors](https://scikit-learn.org/stable/common_pitfalls.html) — targeted deepening of the 12 November 2026; educational examples are built for this review.

## Connections
- [[172-ml-validation-metrics|Validation & ML metrics]] — compare methods without biasing evaluation
- [[146-model-selection|Choice of LLM models]] — locate a LLM among the technical options
- [[147-ai-technical-leadership|Technical Leadership]] — connect complexity and business value
- [[151-data-curation-annotation|Curation & annotation]] — build supervised examples
- [[175-time-series-forecasting|Prediction of time series]] — build predictive baselines
- [[177-model-explainability|Explanation & diagnosis of models]] — distinguish performance and understanding behavior
- [[00-moc-ai-engineering|MOC AI Engineering]]
