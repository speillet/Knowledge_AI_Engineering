# Time series forecasting — Flashcards
Tags: #flashcards #ai-engineering #classical-ml #forecasting #time-series
<!-- summary: horizon and cadence, seasonal baseline, ETS or ARIMA or ML, backtesting with slippery origins, future variables, direct or recursive forecasts, lags, MAPE and MASE, quantiles, intervals and hierarchical coherence, MAPE limits with zero sales, horizon and leakage, interval validation. -->


What should be defined before predicting a time series? <!--anki:3832313262386130373438663432643761663164383138343564303065376431-->
?
Specify **target, time horizon, timing and timing of decision**. Forecasting the next day's demand each morning differs from a weekly forecast for the next four weeks. The information available and the cost of errors are not the same.

Also define the granularity: item, store or total. Distinguish between actual demand and observed sales when breaks limit sales: an item that breaks three days displays zero sales, not zero demand. The backtest must reproduce these decisions and this historical availability, not just predict a staggered column in a complete table.

---

Why is a naive seasonal forecast an important baseline? <!--anki:6633316437616161323365343434356538646532396431633935303033333461-->
?
It resumes the **last observed value of the same season**: for a weekly daily series, the previous Monday is used to predict the following Monday. It captures a recurring pattern with very few parameters.

On a complete daily chart, `y.shift(7)` is suitable if the offset value is known at the decision date. To predict 28 days at a time, repeat the last week observed: then using the real future sales would create a leak. Compare to the same horizons and dates. Holidays, promotions and breaks can invalidate this repetition, hence the interest of measuring the candidate's gain.

---

Do not confuse: ETS, ARIMA and regression models with delayed variables? <!--anki:6265353436636335316332363465653839303034383762643230656439326230-->
?
**ETS** represents level, trend, and seasonality via exponential smoothing. **ARIMA** describes time dependencies and can use differences to process certain non-stationarities. A **delayed regression** learns a relationship from available lags and other variables.

The choice depends on the structure, volume of series and external information.
```python
ExponentialSmoothing(y, trend="add", seasonal="add", seasonal_periods=7)   # statsmodels
ARIMA(y, order=(1, 1, 1), seasonal_order=(1, 0, 0, 7))
X = pd.concat({"lag1": y.shift(1), "lag7": y.shift(7)}, axis=1)            # Regression
```
A global model, for example a single boost for 5,000 articles, can share learning between series. Compare to the same multi-horizon protocol; more parameters or a pre-trained model does not guarantee a gain on the target population.

---

How to build a backtest with slippery origins? <!--anki:6134643739613434633563343463323562633266383333656563646135366564-->
?
Choose multiple **decision dates**. Each, reconstruct the available data, train or reuse the model according to the expected rate, and then forecast the requested horizons. `TimeSeriesSplit(n_splits=3, test_size=28)` produces three consecutive test blocks of 28 observations: 28 days only on a complete daily schedule, not month beginnings.

Report errors by horizon and period, with explicit aggregation between series. Overlapping windows produce dependent errors. Set hyperparameters to separate validation windows and set an independent final period for conclusion.

---

Why distinguish between known and expected future variables? <!--anki:6439613435346139376561313434386261633631363235643238623938333563-->
?
A future variable can only be used if its **value or forecast was available at the origin of the decision**. Calendar and promotions already decided differ from the weather actually observed later.

Example: to forecast Friday sales on Monday, use the weather forecast published on Monday, not the one revised on Thursday or the temperature measured on Friday. Archive publication date, target date and version to reproduce this choice in backtest.

A promotion can also change: remember the known schedule then. If a variable is to be expected, propagate its uncertainty or compare scenarios; a conditional interval at an assumed exact value does not automatically cover it.

---

Do not confuse: Recursive forecasting and direct forecasting to multiple horizons? <!--anki:3565636464326634363862303463333138313963633531373465646264623232-->
?
The **recursive** method predicts a step and then reuses this prediction to move forward. It can accumulate errors. A **direct** method learns a target for each horizon, possibly with a common model producing multiple outputs. For J+7, the first one chain seven predictions of one step; the second one results in seven models, or a model with seven outputs.

The second avoids some feedbacks but can require more data or produce inconsistent horizons between them. The backtest must reproduce the real strategy: feeding a recursive forecast with the real future intermediate values would give an overly optimistic result.

---

How to avoid a target leak in moving averages used to predict? <!--anki:6162386661656532323330613437376461343133663735326131383838623564-->
?
Construct each aggregate only with **observations available before the decision**. To predict the value of the day before its observation, an average including this value flees the target; a centered window can also incorporate the future.

In a supervised table, shifting before calculating the window is a frequent protection, to be adapted to the horizon and the collection time, series by series:
```python
df["moy7"] = df.groupby("article")["sales"].transform(lambda s: s.shift(1).rolling(7).mean())
```
Check a few lines by hand, including start of series, holes and frequency changes.

---

Calculation: what MASE for a 12 test MAE and a 20 average naive seasonal error on the train? <!--anki:3561323334396265623030333435336162663932656365306662343464343838-->
?
The **MASE** reports the absolute error of the test on a scale calculated on the naive differences of the train: **12 / 20 = 0.6**. The denominator must use the retained seasonality and only the train.

This score facilitates some comparisons between series of different scales. It does not prove that the model beats the baseline during this test period: it is also necessary to evaluate the baseline. If the train is constant, the denominator can be zero. MAPE, on the other hand, poses a problem with real values zero or close to zero.

---

Calculation: what loss pinball to 0.9 quantile for a target of 100 and forecasts of 80 then 120? <!--anki:3663373637343666656130653437386561373266386264313839303930613365-->
?
For `u = target − forecast`, the loss is `max(αu, (α−1)u)`:
```text
20 Subforecast: 0.9 × 20 = 18
20 over-forecast: 0.1 × 20 = 2
```
The high quantile further penalizes the sub-forecast. Choose α according to the decision and the asymmetric cost, and then check the overshoot frequencies. A 0.9 quantile forecast is not an arbitrarily increased average of 10% and does not guarantee identical coverage in each segment.

For the same quantile, average this loss on non-workout forecasts and compare to a baseline. Changing the quantile changes the objective: the losses do not become comparable without specifying the targeted decision.

---

How to evaluate a forecast interval at 90%? <!--anki:3338646162346561396133623437363039336565343761306533316638636330-->
?
Measure your **Empirical Coverage** and sa **Width**, by horizon and segment. A huge interval can cover almost all observations without helping to plan. too narrow an interval masks the uncertainty.

Example: 830 Real values on 1,000 fall in intervals announced at 90%, A sub-coverage of 7 points. Compare over successive periods with enough observations, taking into account their dependence. Examine regime failures and assumptions about future variables. The interval is for future observations, not just uncertainty on an estimated average. An overall rate of 90% does not guarantee the coverage of each store.

---

Why reconcile the predictions of a series hierarchy? <!--anki:6431303330386462666633343464353861633332363433653861363165306631-->
?
Separate store-level and national-level forecasts can yield incompatible **totals**: 100, 120 and 80 for three stores, but 330 for the total. Reconciliation requires consistency with the aggregation structure, taking into account the method and, depending on the approach, historical errors.

Check business constraints, including non-negativity and perimeter changes. Consistency does not guarantee better accuracy at all levels. Quantiles do not usually add up: the 90% quantile of the total also depends on the dependence between the components.

---

Why is the MAPE a problem when actual sales are zero or very low? <!--anki:3837663635373238373463303465653661396663383366656463636532323762-->
?
The **MAPE** divides the absolute error by the actual value. It is undefined at zero and can give extreme importance to a small error on a very low sale.

Choose a metric adapted to the decision, for example MAE or MASE with its hypotheses, and specify weighting between series and horizons. Do not silently delete the days without sale: they can be essential to the management of the stock. Test also the units, intermittents and ruptures. A digital protection by epsilon does not alone solve the problem of interpretation.

---

Why evaluate a forecast separately for each horizon? <!--anki:3262356133353062356330303466383061303666306433643236313361633661-->
?
Uncertainty and useful mechanisms change **between tomorrow and in three months**. An average can mask an excellent model in the short term but unusable for long-range planning.

Build the backtest to actual decision dates and compare baselines by horizon. Future variables must be known or predicted under the same conditions. A realized value available only after the fact would create a leak.

---

## Scenarios

Scenario: your model predicts very well at one day, but fails for the four-week schedule. What do you change? <!--anki:6635623432376633633662643431663362353630316232346361666163333738-->
?
1. **Redefine operational target**: time horizons and aggregation used by the schedule.
2. **Replay a multi-horizon backtest** when decisions were made.
3. **Check future variables**, distinguishing between available forecasts and observations made.
4. **Compare direct and recursive** to a seasonal baseline at the same horizons.
5. **Report errors and intervals** by horizon, then the cost of the decisions obtained.

**Trap**: Present the one-day metric as proof of quality at one month.

---

Scenario: a forecast uses today's sales to calculate its moving average, whereas it must be produced at 8 h. What do you check? <!--anki:3965323464633135383833623438306538663536326537376133656331616332-->
?
1. **Trace the actual time of availability** of each variable and correction.
2. **Recalculate aggregates** excluding sales not yet known to 8 h.
3. **Rebuild the historical backtest** with the data then available.
4. **Compare the score drop** and review the conclusions from the previous experience.
5. **Add a time control** on variables served in production.

**Trap**: Keep the historical score obtained thanks to the leak to announce the expected performance.

---

Scenario: the demand becomes very intermittent and the MAPE explodes despite small errors in units. How do you rate? <!--anki:3562613738616666343763363461386238393462313232393534653830386263-->
?
1. **Examine zeros**, out of stock and collection mechanisms.
2. **Choose defined metrics** on these cases, with MFA and business cost.
3. **Check the MASE denominator** if this metric is used.
4. **Compare appropriate references** to the intermittency and decision horizon.
5. **Assess aggregates and quantiles** based on replenishment needs.

**Trap**: remove periods from the test and then announce an overall gain.

---

## Sources
- [Hyndman & Athanasopoulos — simple forecasts](https://otexts.com/fpp3/simple-methods.html)
- [Hyndman & Athanasopoulos — validation temporelle](https://otexts.com/fpp3/tscv.html)
- [Hyndman & Athanasopoulos — metric and MASE](https://otexts.com/fpp3/accuracy.html)
- [Hyndman & Athanasopoulos — variables futures](https://otexts.com/fpp3/forecasting-regression.html)
- [Hyndman & Athanasopoulos — ARIMA and ETS](https://otexts.com/fpp3/arima-ets.html)
- [Hyndman & Athanasopoulos — forecast intervals](https://otexts.com/fpp3/prediction-intervals.html)
- [Hyndman & Athanasopoulos — reconciliation](https://otexts.com/fpp3/reconciliation.html)
- [scikit-learn — delayed variables and validation](https://scikit-learn.org/stable/auto_examples/applications/plot_time_series_lagged_features.html)
- [scikit-learn — perte pinball](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.mean_pinball_loss.html)

- [Hyndman and Athanasopoulos — Prediction Rating and Percent Errors](https://otexts.com/fpp3/toolbox.html) — targeted deepening of the 12 November 2026; educational examples are built for this review.

- 14 November supplement 2026 — Forecast and horizon evaluation: [Hyndman and Athanasopoulos — Forecasting, Chapter 5](https://otexts.com/fpp3/toolbox.html).

## Connections
- [[171-ml-model-selection|Choose a model]] — build predictive baselines
- [[172-ml-validation-metrics|Validation ML]] — compare without using future
- [[159-temporal-data-features|Temporal data]] — rebuild available information
- [[176-anomaly-detection|Detection of anomalies]] — detect deviations at expected dynamics
- [[00-moc-ai-engineering|MOC AI Engineering]]
