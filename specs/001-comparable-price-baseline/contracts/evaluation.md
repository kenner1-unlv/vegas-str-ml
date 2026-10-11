# Advertised-price evaluation contract v1

Frozen 2026-10-10 before fitting. Implements FR-009..012; issue #6. No public predictions authorized by this contract.

## Cohort and features

Use verified normalized source rows only. Require usable positive priced observation, supported Phase 2 property group, known room/stay and assigned ZCTA; exclude all 150 m near-boundary flags. Bedrooms/beds may be missing: preserve nulls until training-only median imputation with missing indicators. Capacity is advertised. Exclusion funnel counts reconcile all input observations. Repeated (ID,snapshot) pairs fail; repeated IDs across snapshots stay together. IDs assigned different ZCTAs across snapshots are excluded entirely, including otherwise unsupported observations. One current snapshot supports no temporal conclusion.

Numeric predictors: bedrooms, beds, accommodates. Categorical predictors: property_group, room_type, stay_cohort, ZCTA. No ID, target-derived prices, raw labels, coordinates, calendar/review measures, bathroom/amenity guesses or source neighborhood predictors. Raw coordinates serve separation checks only; no parcel inference. Unknown numeric training column uses explicit zero fallback plus missing indicator, not a claim of zero physical capacity.

## Frozen geographic splits and tuning

Whole ZCTAs assigned by SHA-256 of `vegas-str-evaluation-v1:outer:ZCTA`, integer digest modulo 5: bucket 0 is final holdout, others development. Assignment uses no prices or outcome inspection and all areas qualify regardless of support. Reject empty partitions. Within development, SHA-256 of `vegas-str-evaluation-v1:inner:ZCTA` modulo 3 yields three tuning folds. Reject empty folds. Never tune on final holdout. Exclude development observations within 1,000 m great-circle distance of any final-holdout observation; similarly exclude inner training observations within 1,000 m of any validation observation. Also exclude all IDs present in the respective evaluation partition. Spherical Earth radius 6,371,008.8 m; spatial KD-tree on unit vectors and exact chord-to-arc distances. Buffers use anonymized observed points, not complete polygons or true properties: separation of observed points cannot prove actual parcel separation. The pre-existing 150 m edge flag alone is not the 1 km separation buffer.

Private manifest contains string ID/snapshot membership, excluded counts and minimum measured distance. Aggregate report publishes area codes/counts and membership checksum, never rows or IDs. Private manifest remains ignored. Identical inputs, lockfile and code reproduce split and metric JSON (no timestamps/timings).

## Baselines and candidate

First calculate global and room-type medians on training only; unseen room falls back to global. Candidate is Ridge regression on log1p USD price. Pipeline fits numeric median imputation/missing indicators, numeric standardization, and categorical OneHotEncoder(handle_unknown=ignore) on each training fold only. Unseen ZCTA has all-zero area indicators: shared feature/intercept effects, no learned local-area premium. Choose alpha from fixed [1,10,100] using pooled inner-fold USD MAE; ties choose smaller alpha. Each fold is independently fitted; refit chosen alpha on buffered development only. Back-transform with expm1, clamp negative values to zero, report clamp count; nonfinite predictions fail. No target cap or post-hoc retuning. No model binary saved/published.

Report global/room median and candidate USD MAE, median absolute error, RMSE, log1p MAE; observation/unique-ID/area counts; training-only preprocessing statistics/categories; inner metrics and buffer counts; final subgroup metrics by ZCTA, property group, room and target price bands (<100,100-249.99,250-499.99,500+). Price bands are diagnostics only, never split/predictor rules. Groups n<20 flagged thin; all errors remain visible without confidence claims. Report repeat observations explicitly; pooled metrics weight observations, not independent properties.

## Review gates and release decision

Precommitted research gates: at least 200 final observations and 5 final ZCTAs; candidate final MAE at least 10% below each median baseline; candidate RMSE no worse than either baseline; every room/property/ZCTA subgroup n>=20 has candidate MAE no more than 10% above room-median MAE. These are project review criteria, not calibrated confidence. Report every failed gate and do not select another model from final results. Even passing gates does not release UI predictions: intervals, temporal/physical-duplicate checks and a separate public prediction contract/review remain required. No occupancy, financial valuation, investment ranking or regulatory claims.

## CLI and failure handling

`uv run --project pipeline python pipeline/evaluate.py --snapshot 2026-09-20 --output data/research/2026-09-20/evaluation.json`

Rebuild/verify pinned normalization first. Only .json output under ignored data/research allowed; normalized.json protected case-insensitively. Atomically replace one private file containing manifest and aggregate report after all validations/fits finish. Failed input/fitting leaves prior result intact. Stdout is aggregate report only, which may be explicitly captured for model-card evidence after review. CI runs synthetic fixture fits only; no private dataset downloads/training.
