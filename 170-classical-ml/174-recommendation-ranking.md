# Recommendation & learning to rank — Flashcards
Tags: #flashcards #ai-engineering #classical-ml #recommendation #ranking
<!-- summary: Product objective, candidate generation and ranking, collaborative filtering or content, implicit feedback, two-turn models, ranking objectives, negatives, exposure bias, cold start, nDCG and diversity, recall calculation between candidates and ranking, non-exposed negatives, catalog diversity. -->


Why set the product goal before training a recommendation system? <!--anki:3961363434643038363137653430666262613063613338656334323464636161-->
?
The model needs to optimize a **useful result**, not just reproduce historical clicks. To recommend technical articles, a click, a full reading and a problem resolution represent different objectives.

Define the event, its horizon and the constraints of quality, freshness and latency. Compare a baseline of popularity or contextualized rules. Example: a variant increases the click rate from 4% to 5%, but the share of complete readings from 40% to 30% of clicks, or 1.5% of impressions against 1.6%: it favors also catchy titles.

---

Do not confuse: generation of candidates and ranking in recommendation? <!--anki:6337313536363663346235333430386438653762623733373534623339323536-->
?
The **candidate generation** reduces a large catalogue to a plausible subset, with a tight latency budget. The **candidate ranking** then orders these candidates with possibly more expensive features and calculation.

Example: a vector search reduces 2 million articles to 500 candidates, then the ranker orders them; if the right article is not among the 500, no ranker will show it. Measure separately the recall of candidates and the quality of the ranking, then the complete route after business filters. Compare the rankers on a controlled set helps in diagnosis; measure only this subset does not describe the whole system.

---

Do not confuse: Collaborative filtering and content-based recommendation? <!--anki:3437343438613636656665303462393562326563333639616465316539643433-->
?
**Collaborative filtering** learns from the interactions between users and elements. The recommendation **by content** uses their characteristics: theme, text, category or context attributes.

Example: a tutorial published this morning has no interaction; its text already brings it closer to the Kubernetes articles read by the user, while the collaborative ignores it until the first clicks. However, the collaborative discovers that readers of a GPU article also read a FinOps article. A hybrid approach combines these signals; it does not remove collection biases. Compare by age of users and elements rather than on a popular one.

---

Why is no click not always a reliable negative example? <!--anki:3132393934613263633334663434663738366430396465633432666162643838-->
?
The user may not have **Never seen the element**, or did not notice it in his position. Implicit feedback mixes preference, exposure and context. The absence of interaction throughout the catalog does not mean explicit rejection.

Example: an article placed in 9e position, while the user has only scrolled through the first 4s, has never been seen; treating it as negative learns above all that low positions are not clicked. Log the impressions actually displayed, positions and versions. Even a non-click printing can be ambiguous: tab inactive, recommendation already known or objective not requiring opening.

---

Why does a two-turn model make it easier to find recommendations on a large scale? <!--anki:3065383238373765333138613466613738373362366637323932623433353634-->
?
One tower encodes the **user context**, the other the **element**; a simple function, often a scalar product, compares their representations. The vectors of the elements can be calculated in advance and indexed: for 5 million elements, only the user tower runs at the request, then an index of nearest neighbors returns a few hundred candidates.

This separation limits the fine interactions between context and element during the search. A richer ranker can then exploit them. Version together encoders and indexes, and re-encode elements when necessary: mixing incompatible spaces can degrade the callback without causing a technical error.

---

Do not confuse: pointwise, peerwise and listwise objectives in ranking? <!--anki:6530643030626634366232363461313338303064346635633162353631656635-->
?
A **pointwise** objective learns one score per element; **pairwise** learns preferences between pairs; **listwise** optimizes a property of a list. They differ in the signal used, the cost and their link to the final metric.

A click classifier can provide a baseline pointwise, but its accuracy does not directly measure the order of the top-k. Forming pairs or lists within a comparable context: `LGBMRanker(objective="lambdarank")` receives a `group` parameter that groups the candidates of each query and weights its pairs according to their effect on the nDCG. Choose the objective according to the labels available, then check the result on the ranking actually displayed.

---

How does the choice of negative examples influence a recommender? <!--anki:6565303930643130653632323461646539363931636330666365636534363966-->
?
Negatives **random** often make separation easy; difficult negatives learn finer distinctions but can be false negatives. For a PostgreSQL article reader, a random negative on the kitchen deviates trivially; a negative on MySQL learns a real distinction, but might have interested him.

Document the sample distribution and compare results on candidates representative of the service. Scores learned with artificially rebalanced classes are not automatically calibrated click probabilities. Keep business exclusions and temporality: an element unavailable at the historical moment must not become a plausible candidate at that moment.

---

Why do the journals of a former recommender skew the evaluation of the next one? <!--anki:3737323531313730663962313430373662653664373437316163366533326162-->
?
The old system chose **what was visible and at what position**. The interactions observed reflect this policy, In addition to preferences. A new system offering other elements meets areas where newspapers provide little information.

Exposure probability weights can help under explicit assumptions. An element shown with a probability of 0.05 receives a weight of 20: a few clicks on it dominate the estimate, hence a high variance. These weights do not create observations for an action never proposed. A controlled exploration or a randomised test provides additional evidence, depending on the risk of the product.

---

How to manage a user's or item's cold start? <!--anki:6262373936326638313331343465633862653739303832303765613138346431-->
?
Provide a **path without history**: contextualized popularity, element attributes, session intent, or explicitly provided preferences. For a new element, the description may allow a first representation before interactions.

Measure this segment separately and define the transition to personalization. Example: A new user receives popular articles from their language and product, and then switches to personalization after five reads. Global popularity can be poor for rare uses. Also evaluate the time it takes to expose a new relevant item, not just performance on already very active users.

---

Calculation: which nDCG@3 for binary relevancy [0, 1, 1], with two relevant elements in the evaluated game? <!--anki:3666363231343362656138353430363339303034336237356235313266343833-->
?
With a binary gain and a logarithmic discount by position:
```text
DCG@3  = 0/log2(2) + 1/log2(3) + 1/log2(4) ≈ 1,1309
IDCG@3 = 1/log2(2) + 1/log2(3) + 0/log2(4) ≈ 1,6309
nDCG@3 = DCG/IDCG ≈ 0,6934
```
The ideal order puts the two relevant elements in the lead. Specify relevance, gain and candidate universe to compare scores. The result evaluates this annotated ranking; it does not measure fair exposure or lasting user satisfaction.

For non-binary relevance, also announce the gain function: `r` and `2^r−1` give different values. The ideal denominator must be built on the same universe and with the same conventions.

---

Why add diversity and business constraints after the relevance score? <!--anki:3736356165376333353332633438366561353530353966616166313831636462-->
?
The highest individual scores can produce a **redundant list**, unavailable or poorly adapted to the session: the first five results all come from the same series of posts. The reclassification applies exclusions, caps by category, for example two items per series, diversity or freshness according to an explicit contract.

Measure the trade-off between the relevance and usefulness of the list, as well as the violations of constraints. Access rights and mandatory exclusions must be guaranteed by the application. A constraint of diversity should not be presented as a universal improvement: its value depends on the task and what the user seeks to accomplish.

---

Calculation: a candidate generator finds 80% relevant elements and the canned ranking 75%. What final recall under these assumptions? <!--anki:3733653038643133353032623435336561616566623737366133616435333832-->
?
If the **75%** is the fraction of the recovered relevant items that remain in the final list, the final reminder is `0,80 × 0,75 = 60 %`.

The ranking cannot promote an element that is absent from the candidates. Measure losses separately at each stage to know where to invest. The product here deals with conditional reminders defined on the same population; it does not require an assumption of independence. Averages calculated on users with different weights do not necessarily multiply in this way.

---

Why supplement nDCG with a catalogue coverage measure? <!--anki:3034383265623630386665623430666462636465623362613132333237633365-->
?
A system can classify **a small group of popular items** while making the rest of the catalog invisible. nDCG alone does not describe this concentration.

Measure exposure, diversity and results by segment, with the product objective. More coverage is not automatically better if recommendations become off topic. Evaluate online trade-offs and monitor effects on new items and new users.

---

## Scenarios

Scenario: your new ranker wins in nDCG offline, but the resolution rate drops in production. What do you check? <!--anki:6636323239656663353334623438376261623161383538353862366439313237-->
?
1. **Compare objectives**: annotated relevance, click and effective resolution.
2. **Audit candidates and filters**, with their availability at the historical moment.
3. **Examine exposure biases**, positions, and population changes.
4. **Cut the results** by cold start, theme and seniority.
5. **Test one hypothesis at a time** with product safeguards and adapted online protocol.

**Trap**: To conclude that any progression of a ranking metric necessarily improves the experience.

---

Scenario: new relevant documents are never recommended, despite complete descriptions. How do you diagnose? <!--anki:3330623837396361663832663432653739666635613235343461306532376433-->
?
1. **Follow some documents named**: ingestion, index, rights, language and date of publication. A description available does not prove their eligibility.
2. **Inspect candidates before ranking** on queries where their relevance is checked. If they are absent, correct this step first.
3. **Test cold start**: A click-based score can assign zero to any new document.
4. **Add one path per content or controlled exploration**, with limited quota and same quality constraints.
5. **Compare by age** time to first exposure, recall and satisfaction; log exposure probabilities if bias correction is expected.

**Trap** : to conclude that the novelties are bad because they have few clicks while they are never shown.

---

Scenario: a recommender offers ten almost identical variants of the same tutorial. What correction do you test? <!--anki:6230363266323731313036643465376262343161366438636161383463336231-->
?
1. **Identify duplicates** and define useful diversity: source, difficulty or subject.
2. **Keep the baseline** and measure its relevance and redundancy.
3. **Apply a limited reclassification**, with ceiling per family and explicit exclusions.
4. **Check segments** where multiple variants are really useful.
5. **Assess complete list** on task success, quality, and latency.

**Trap**: Maximize diversity by offering off-topic items.

---

## Sources
- [Google — architecture recommendation systems](https://developers.google.com/machine-learning/recommendation/overview/types)
- [Google — collaborative filtering and feedback](https://developers.google.com/machine-learning/recommendation/collaborative/basics)
- [Covington et al. — Deep Neural Networks for YouTube Recommendations](https://research.google/pubs/deep-neural-networks-for-youtube-recommendations/)
- [Google — reclassification, freshness and diversity](https://developers.google.com/machine-learning/recommendation/dnn/re-ranking)
- [Schnabel et al. — selection bias in recommendation](https://proceedings.mlr.press/v48/schnabel16.html)
- [Burges — From RankNet to LambdaRank to LambdaMART](https://www.microsoft.com/en-us/research/publication/from-ranknet-to-lambdarank-to-lambdamart-an-overview/)

## Connections
- [[133-embeddings-representations|Embeddings]] — representations to search for candidates
- [[96-evals-rag-agents|Evaluation of the Retrieval]] — measure recall and result order
- [[97-evals-online-ab-testing|A/B testing]] — check the exposed list value
- [[178-causal-inference-decisions|Causal inference]] — distinguish exposure and effect of recommendation
- [[117-continuous-training-pipelines|Training pipelines]] — selective labels of a model that decides
- [[00-moc-ai-engineering|MOC AI Engineering]]
