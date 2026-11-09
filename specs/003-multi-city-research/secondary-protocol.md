# Secondary experiment: market-relative asking-price segment

**Frozen before fitting**: 2026-11-08 Pacific. Issue [#28](https://github.com/kenner1-unlv/vegas-str-ml/issues/28).
This is private exploratory classification, not a user-facing investment label.

## Question and hypothesis

Can basic listing characteristics distinguish advertised prices at or above a market's
training-set median from those below it on unseen development geography? A nonlinear
random forest may capture property/capacity interactions and improve macro F1 over a
linear logistic classifier. This is an empirical hypothesis, not an expected outcome.

## Target and partitions

For each market and each of the three frozen inner geographic folds in
[evaluation.md](contracts/evaluation.md), calculate the **median asking price only from
that fold's fitting rows**. Label fitting and validation rows `high` if advertised price
is greater than or equal to this fixed median, otherwise `low`. Ties may cause class
imbalance; record class counts and threshold per fold. No target price or derived quote
is an input feature. Grouped IDs and 1 km buffers are inherited from the frozen split.
Only NYC, LA and Nashville development folds are evaluated; Clark County is historical
context and all outer final blocks remain unscored in this experiment.

Fit separate market models rather than a pooled model so each threshold has a clear local
meaning. The core inputs are bedrooms, beds, advertised capacity, room type and property
group, with training-only numeric median imputation/missing indicators and categorical
one-hot encoding. The majority-class predictor fitted on each fold is the baseline.

## Fixed candidates and evaluation

- Logistic regression: `max_iter=1000`, `class_weight=balanced`, `random_state=20261108`.
- Random forest classifier: `n_estimators=100`, `max_depth=12`,
  `min_samples_leaf=20`, `n_jobs=1`, `random_state=20261108`.

Record per-fold and pooled-by-market confusion matrices, class support, accuracy,
balanced accuracy and macro F1. Compare candidates with the majority baseline on the
same validation rows. Record repeatability and source/split/config hashes. Class labels
are market-relative asking-price categories, not property quality, investment value,
occupancy or expected revenue. Do not select or publish a classifier as a product from
these development folds. If support or class diversity fails, report insufficient
evidence rather than substituting a random split.

## Deferred alternatives

Clustering, anomaly detection, PCA/UMAP, model explanations and tabular neural networks
remain future questions. Each needs its own hypothesis, defensible inputs, stability or
held-out protocol and a baseline. No result is claimed for them here.
