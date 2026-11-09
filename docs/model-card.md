# Advertised nightly-price research model v1

Evaluated October 10, 2026. Offline research only; **public predictions withheld**. [Issue #6](https://github.com/kenner1-unlv/vegas-str-ml/issues/6) tracks implementation and delivery; [follow-up #17](https://github.com/kenner1-unlv/vegas-str-ml/issues/17) tracks failures, temporal evidence and prediction review. [Frozen evaluation contract](../specs/001-comparable-price-baseline/contracts/evaluation.md), [aggregate results](../specs/001-comparable-price-baseline/phase3-evaluation.json), [implementation](../pipeline/evaluate.py).

## Intended use and data treatment

Estimate an Inside Airbnb listing's advertised USD nightly price for research, not achieved revenue, bookings, occupancy, acquisition value, profit or legal eligibility. This is not yet an address-based estimator or MLS/Zillow integration. One Clark County snapshot dated 2026-09-20; hashes and normalization provenance are in the aggregate results.

20,651 input observations -> 13,288 supported research observations. First-failure exclusions: 3,439 outside the existing usable cohort; 241 unsupported property groups; 116 unknown stay category; one unassigned geography; 3,566 near-boundary observations after earlier exclusions. Missing bedroom/bed counts remain null until training-only imputation. No price cap or coordinate shift. Capacity is advertised, not verified. Bathroom/amenity, lot size, condition and renovation features are absent.

Whole-ZCTA price-independent hash assignment reserves nine areas (89002, 89030, 89052, 89104, 89117, 89123, 89145, 89156, 89179): 1,642 holdout observations. Development starts at 11,646; the 1 km observed-point buffer removes 1,280, leaving 10,366 training observations. Zero train/holdout listing-ID overlap; minimum measured separation 1,000.318 m. All current observations have distinct IDs; this does not guarantee distinct physical properties. ZCTAs and anonymized points are approximate. Buffers do not establish true parcel separation.

## Model and training

Global training median $227; room-type medians fall back to global for unseen room categories. Candidate: scikit-learn 1.9.1 Ridge on log1p price, numeric bedrooms/beds/advertised capacity, categorical property group/room/stay/ZCTA. Numeric median imputation, missing indicators, scaling and categorical vocabulary fit inside each training-only pipeline. Held-out ZCTAs use all-zero area indicators with shared effects; they receive no learned local-area premium. Candidate alpha 10 selected from [1,10,100] by pooled USD MAE in three inner geographic folds, each with its own ID exclusion and 1 km buffer. No tuning on final outcomes, no model binary published. Back-transform expm1; zero negative clamps in the actual holdout.

## Final held-out results

| Method | USD MAE | USD median absolute error | USD RMSE |
| --- | ---: | ---: | ---: |
| Global training median | 177.93 | 115.50 | 438.50 |
| Room-type training median | 170.30 | 105.60 | 435.20 |
| Log1p Ridge | 123.09 | 55.45 | 392.26 |

Candidate MAE is 27.72% below room-type median and 30.82% below global median. These are errors against advertised prices, not expected investment accuracy. [Aggregate evidence](../specs/001-comparable-price-baseline/phase3-evaluation.json) includes log errors, all ZCTA/property/room/price-band subgroup counts, training vocabulary, tuning metrics and split checksum. Two actual CLI runs produced identical private output bytes; no temporal validation is possible from this one snapshot.

## Failures and release decision

Precommitted support, overall MAE improvement and overall RMSE gates pass. **Supported-subgroup non-regression fails**: hotel_room n=28 has candidate MAE $83.31 versus room-median $74.27 (12.17% worse), exceeding the 10% limit. Hotel-room RMSE also increases ($138.30 versus $121.68). No final-set retuning or selective hotel fallback was added after observing this failure.

Price-band diagnostics also expose weaknesses: $250-499 listings have candidate MAE $123.31 versus room-median $114.67; $500+ listings still have candidate MAE $447.09 and RMSE $1,054.37 despite improvement. The log target emphasizes proportional fit and can underrepresent the dollar cost of high-price errors. Uncapped extreme rates, missing property condition/amenities, broad groups and unseen local-area effects limit interpretation. Thin groups are flagged at n<20; this is not a confidence bound.

**Withhold public predictions.** No calibrated intervals, temporal validation, verified-address/property integration or physical-duplicate controls exist. [Issue #17](https://github.com/kenner1-unlv/vegas-str-ml/issues/17) requires development-only investigation and fresh untouched evaluation before a revised release decision. The live explorer remains descriptive. [Address workflow #16](https://github.com/kenner1-unlv/vegas-str-ml/issues/16) first requires permitted property-data access and a separate public contract.

## Reproduction and ownership

### Review-feature development follow-up

The [owner feature menu](features.md) catalogs all 90 detailed-listing columns. The [review experiment contract](../specs/002-review-features/contracts/experiment.md) was frozen in commit d19e835 before actual fitting. It adds seven scores, four review counts and reviews/month as selectable private inputs without changing the first evaluation above. Owner chose review features first; bathrooms, amenities and other candidates await selection and parsing.

On the same three buffered geographic development folds (10,366 validation observations pooled), independently tuned log1p Ridge variants produced:

| Feature set | USD MAE | USD RMSE | Selected alpha |
| --- | ---: | ---: | ---: |
| Property only | 165.53 | 1,093.07 | 10 |
| Scores excluding value | 163.14 | 1,091.89 | 10 |
| Review counts/rate | 161.71 | 1,091.26 | 10 |
| Scores + counts excluding value | 161.44 | 1,090.96 | 10 |
| All reviews including value | 161.33 | 1,090.60 | 1 |

All-review MAE is about 2.53% below the property-only reference in this exploration. Global/room-median development baselines are $217.69/$213.03. Property-only pooled alpha metrics exactly reproduce the original development tuning metrics. **Do not compare this $161.33 with the original $123.09 final MAE as an improvement/regression:** they use different observations. Each alpha is selected on these same folds, so these are selection-biased development diagnostics, not new final-test or unbiased nested-CV estimates. No feature-set winner is promoted.

Development coverage: 7,595 of 10,366 have valid overall/accuracy/cleanliness scores and reviews/month; check-in/location/value have 7,594. Communication has 7,594 valid, 2,771 missing and one invalid (source 5.05 preserved privately, not capped). All four counts are present/valid for all development rows. Missing values are imputed inside fitting partitions with indicators; zero review counts remain distinct from missing ratings.

[Aggregate results](../specs/002-review-features/development-results.json) include every fold/alpha and room/property/ZCTA diagnostics. [Verification](../specs/002-review-features/verification.md) records repeatability and preserved baseline/public artifacts. Ratings describe established comps and may reflect management/service or perceived price; they are not guaranteed subject-property outcomes or causal renovation effects. Counts are not bookings. Large RMSE persists from extreme asking-price errors. No outer-holdout errors were recomputed; fresh final/temporal evidence, calibrated intervals and public prediction release remain [#17](https://github.com/kenner1-unlv/vegas-str-ml/issues/17).

Follow [quickstart](../specs/001-comparable-price-baseline/quickstart.md) with pinned private archives/normalization, then run `uv run --project pipeline python pipeline/evaluate.py --snapshot 2026-09-20 --output data/research/2026-09-20/evaluation.json`. Private output contains split membership; stdout contains aggregates only. CI runs synthetic evaluation fixtures, not private source training or downloads. Research owner explicitly reviews/publishes aggregate results; GitHub Actions deploys only the static frontend artifact after main checks. Lockfile/code/contract/dataset hashes accompany results. Numeric-library/platform differences can affect floating-point last digits; bitwise repeatability was checked on this Windows environment, not promised across platforms.

## Four-market advertised-price research (November 8, 2026)

This separate offline study uses [Inside Airbnb](https://insideairbnb.com/get-the-data/)
detailed listings for Clark County (2026-09-20), New York City (2026-09-14), Los Angeles
(2026-09-14) and Nashville (2026-09-19), under the source's [CC BY 4.0 policy](https://insideairbnb.com/data-policies/).
Source archives remain local. The [source manifest](../specs/003-multi-city-research/source-manifest.json),
[cohort audit](../specs/003-multi-city-research/source-audit.json),
[frozen protocol](../specs/003-multi-city-research/contracts/evaluation.md) and
[split support](../specs/003-multi-city-research/split-support.json) record provenance
and exclusions. The normalization and source-area expansion are our modifications.
Clark County represents the broader source area, not just Las Vegas city.

The four archives contain 104,483 source rows; 82,868 have parsed positive advertised
prices and valid coordinates. All 21,615 exclusions in this initial private cohort have
missing asking prices, including 10,512 of 29,918 NYC rows. Missing target selection may
vary substantially by city. Valid extreme asking prices were retained. Aggregate review
ratings were audited but **not used** as predictors in this core model.

The fixed core inputs are bedrooms, beds, advertised capacity, room type and property
group. Global and room-type training medians are baselines. Ridge (alpha 10) and histogram
gradient boosting (120 iterations, 15 maximum leaf nodes) fit a log1p price target with
training-only numeric imputation and categorical encoding, then back-transform to USD.
Whole 3 km geographic blocks and a 1 km observed-coordinate buffer separate fitting and
evaluation. The existing Clark County snapshot has already informed earlier model work;
its results here are historical/development evidence. New final blocks were frozen in
NYC, LA and Nashville before fitting. Approximate source points cannot guarantee that
different IDs represent different physical properties.

### Development selection and frozen final results

Three geographic development folds across the three new markets contain 48,085 pooled
validation observations. Fixed histogram boosting had $182.86 MAE versus Ridge $193.81,
room median $223.14 and global median $236.92. The preregistered rule selected histogram
boosting by development USD MAE. These folds were also used for selection, so their errors
are not fresh final estimates. A second local development run reproduced the saved
aggregate result exactly.

The single frozen final pass evaluated 8,568 listings across NYC, LA and Nashville:

| Method, pooled training | USD MAE | USD RMSE |
| --- | ---: | ---: |
| Global training median | 197.84 | 480.72 |
| Room-type training median | 176.46 | 473.21 |
| Log1p Ridge | 149.83 | 433.03 |
| Log1p histogram boosting | 144.11 | 413.58 |

For the selected candidate, a 500-resample paired geographic-block bootstrap produced
an MAE interval of $114.52–$177.84 and candidate-minus-room-median MAE interval of
-$42.91 to -$21.66. These describe block-resampling uncertainty under the observed
snapshot, **not** calibrated intervals for an individual listing or future market.

Within-city final boosting MAE was $144.30 on 5,351 LA listings, $125.57 on 1,332
Nashville listings, and $158.09 on 1,885 NYC listings. Fixed-candidate leave-one-city-out
diagnostics gave boosting MAE $194.76 for LA, $157.26 for Nashville and $172.74 for NYC;
Clark County was $206.74 versus its room-median $196.51, a transfer failure. Ridge's
Nashville leave-one-out diagnostic had $423.25 MAE and $14,570.85 RMSE, exposing severe
cross-market tail instability. These leave-one-out scores are diagnostics of predeclared
methods; no method was chosen from them. With geographically balanced local-group budgets
of 0 to 500, selected boosting MAE changed from $147.67 to $146.16 in LA, $155.88 to
$151.93 in Nashville and $166.63 to $166.16 in NYC. Limited adaptation gains were small
in two of three markets; protocols use the same frozen local final blocks per market.

### Failure analysis and release decision

The pooled final **hotel-room** subgroup (n=60) has boosting MAE $229.94 versus
room-median $201.20, a 14.3% regression. The $250–499 asking-price band (n=2,182) has
boosting MAE $110.55 versus room-median $97.43, a 13.5% regression. These failures
matter even though pooled MAE improved. Final subgroup results are descriptive failure
analysis, not instructions to retune on this exposed final set. The full
[development summary](../specs/003-multi-city-research/development-results.json) and
[final aggregate summary](../specs/003-multi-city-research/final-evaluation.json) include
support, other subgroup errors, block-bootstrap methods and source/configuration hashes.
Their hashes point to complete aggregate diagnostics retained locally outside Git.

**Public prediction release remains withheld.** The hotel-room subgroup fails the
existing non-regression threshold; temporal validation, calibrated individual intervals
and physical-duplicate controls are also absent. The live map remains the original
descriptive explorer. The multi-city case study and any reviewed public research view
are separate delivery work, not a deployed model.

### Development-only price-segment classification

A separate [frozen secondary protocol](../specs/003-multi-city-research/secondary-protocol.md)
tests whether the same basic characteristics identify listings at or above **that
market and fold's training-price median**. This is a relative advertised-price label,
not property value, quality, profitability or occupancy. Each threshold is learned only
from fitting rows; buffered geographic development folds are reused. The outer final
blocks were not scored for this experiment.

| Market | Validation rows | Majority macro F1 | Logistic macro F1 | Random forest macro F1 |
| --- | ---: | ---: | ---: | ---: |
| Los Angeles | 26,213 | 0.510 | 0.781 | 0.780 |
| Nashville | 6,658 | 0.404 | 0.732 | 0.734 |
| New York City | 15,214 | 0.466 | 0.721 | 0.773 |

The preregistered hypothesis that the nonlinear classifier would improve on logistic
regression is supported in NYC, nearly tied in Nashville and **not supported in LA**.
Validation class support and confusion matrices are in the
[aggregate results](../specs/003-multi-city-research/secondary-results.json). For example,
Nashville's random forest classified 1,281 above-median listings as below-median versus
488 errors in the other direction; the task is not equally accurate for both classes.
Two local runs produced the same aggregate result. These are exploratory development
metrics with fold-specific thresholds, so do not interpret their pooled values as a
single market-wide threshold's final accuracy. No public classifier was released.
