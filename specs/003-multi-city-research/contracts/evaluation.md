# Multi-city evaluation contract (draft; freeze before fitting)

**Target**: positive parsed advertised USD nightly price, not bookings, revenue, property
value or investment return. Only observations passing the reviewed cohort audit may enter
supervised training. No price-derived quote, ID, review text or exact address is a predictor.

**Group and geography (frozen 2026-11-08, before fitting)**: Group all snapshots of
(`market_id`, string `listing_id`). If one group appears in multiple spatial blocks,
exclude that group from the evaluated cohort and count geographic drift. For a row at
latitude `lat`, longitude `lon`, compute `x = R*cos(lat0)*radians(lon)` and
`y = R*radians(lat)` with `R=6371.0088 km`; block coordinates are `floor(x/3)` and
`floor(y/3)`. Fixed `lat0` by source market: Clark County 36.2, NYC 40.7, LA 34.1,
Nashville 36.15 degrees. The origin is `(0,0)` km, grid size **3 km**. This local
equirectangular projection defines reproducible blocks, not precise property distances.

Hash the UTF-8 string `vegas-str-multicity-v1:outer:{market_id}:{block_x}:{block_y}`
with SHA-256; integer digest modulo 5 equals 0 for the outer partition. For remaining
blocks, hash the analogous `inner` string and take modulo 3 for development folds.
Whole blocks are assigned together. Exclude fitting observations within **1,000 m**
great-circle distance of any test/validation observed coordinate, and exclude overlapping
listing groups. Apply buffers only within the same source market. Preserve all excluded
counts, membership and a split hash privately; publish counts and hash only.

Minimum support per new-market outer partition: at least 500 rows, 10 populated blocks
and five blocks with at least 20 rows. Each inner validation fold requires at least 200
rows and fitting after buffer at least 1,000 rows. Failure is reported as insufficient
support, never replaced with a random split. Anonymized coordinates and related units
under different IDs remain physical-independence limitations.

**Protocols**:

1. Within city: train and choose hyperparameters on development geography, score the
   new frozen final geography once for NYC, LA and Nashville. Clark County's existing
   snapshot is historical/development evidence only.
2. Pooled: combine development rows from four cities, with fitting-only preprocessing;
   compare on the same frozen final blocks in NYC, LA and Nashville as within-city models.
3. Leave one city out: fit on three cities and score the fourth. The four folds are a
   precommitted transfer diagnostic, with no candidate selection from their outcomes.
4. Limited local adaptation: select a fixed budget of target-city development groups,
   balanced round-robin across development spatial blocks, with block and group order
   determined by SHA-256 and without using target prices for sample selection, and
   evaluate on that city's same frozen final blocks. Compare budgets including zero.

The historical 2026-09-20 Las Vegas Phase 3 outer holdout and development results are
already inspected; no row from this snapshot can be called a fresh independent final test.
Report it separately from the new-market final results. A future, newly acquired Clark
County snapshot may support a new final test with a forward/grouped protocol.
Later-snapshot temporal evaluation needs a new source/version and grouped forward protocol.

**Baselines and candidates**: training global median, training room-type median with
global fallback, log1p Ridge and a predeclared scikit-learn tree/boosting candidate. Core
predictors are `bedrooms`, `beds`, advertised `accommodates`, `room_type` and
`property_group`. IDs, city/neighborhood labels, coordinates, review variables, stay
restrictions, target-derived fields and listing descriptions are excluded from the core
price model. Review variables require a later availability and leakage decision. Use
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
