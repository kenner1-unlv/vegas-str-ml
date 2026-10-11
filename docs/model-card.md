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
