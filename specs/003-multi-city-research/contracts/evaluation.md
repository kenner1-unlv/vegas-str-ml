# Multi-city evaluation contract (draft; freeze before fitting)

**Target**: positive parsed advertised USD nightly price, not bookings, revenue, property
value or investment return. Only observations passing the reviewed cohort audit may enter
supervised training. No price-derived quote, ID, review text or exact address is a predictor.

**Group and geography**: Group all snapshots of (`market_id`, string `listing_id`). Build
deterministic spatial blocks per market from source approximate coordinates using a fixed
market projection/origin, grid size and hash seed recorded in the split manifest. Reserve
whole blocks for final evaluation before fitting; exclude training points within an
observed-point buffer of final/validation rows and exclude overlapping listing groups.
Use inner geographic folds on development blocks. Record excluded counts, support and
the limitations of anonymized coordinates. If a market lacks enough blocks or observations,
report insufficient support rather than replace with a random split. Exact grid/buffer
values and minimum support are finalized after source geography audit, before model fitting.

**Protocols**:

1. Within city: train and choose hyperparameters on development geography, score the
   new frozen final geography once for NYC, LA and Nashville. Clark County's existing
   snapshot is historical/development evidence only.
2. Pooled: combine development rows from four cities, with fitting-only preprocessing;
   compare on the same frozen final blocks in NYC, LA and Nashville as within-city models.
3. Leave one city out: fit on three cities and score the fourth. The four folds are a
   precommitted transfer diagnostic, with no candidate selection from their outcomes.
4. Limited local adaptation: select a fixed budget of target-city development groups,
   stratified by development geography without using targets for sample selection, and
   evaluate on that city's same frozen final blocks. Compare budgets including zero.

The historical 2026-09-20 Las Vegas Phase 3 outer holdout and development results are
already inspected; no row from this snapshot can be called a fresh independent final test.
Report it separately from the new-market final results. A future, newly acquired Clark
County snapshot may support a new final test with a forward/grouped protocol.
Later-snapshot temporal evaluation needs a new source/version and grouped forward protocol.

**Baselines and candidates**: training global median, training room-type median with
global fallback, log1p Ridge and a predeclared scikit-learn tree/boosting candidate. Use
identical eligible partitions. Fit imputers, encoders, scaling, target transforms and
calibration only on fitting partitions. Unseen city/neighborhood values need explicit
fallback; never encode IDs or price-derived variables. Record configurations and seeds.

**Metrics and interpretation**: USD MAE, RMSE, median absolute error, log1p MAE or a
predeclared suitable relative measure, subgroup counts and residual diagnostics by
market/room/price band/geography. Report a block-bootstrap uncertainty interval when
enough independent blocks exist, with method/replicates/seed; otherwise mark unsupported.
No individual prediction interval or public prediction is implied. Development fold
metrics are selection diagnostics. Final results require a frozen config and one scoring
pass, then a documented failure/release decision. No secondary experiment begins without
its own question, baseline and leakage/stability protocol.
