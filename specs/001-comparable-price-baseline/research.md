# Research decisions and Phase 1 evidence

Date: 2026-10-09. Fresh local analysis of the pinned 2026-09-20 detailed archive and current usable string-ID cohort. Machine-readable aggregate evidence: [phase1-audit.json](phase1-audit.json). Original source provenance/license and coordinate limitations remain in [data sources](../../docs/data-sources.md).

## How the data was treated

This table shows the treatment directly. Examples are illustrative field values, not published listing rows; counts below are freshly measured from the actual snapshot.

| Source evidence | Derived research representation | Reason |
| --- | --- | --- |
| property_type=Room in hotel; room_type=Private room | property_group=hotel_resort; room_type=private_room; both original labels retained | Avoid treating private hotel rooms as residential rooms |
| Entire home, Entire townhouse, Entire villa | house_like; raw subtype still available | Initial broad research group; not a claim that all are detached houses |
| Entire serviced apartment | serviced_apartment, separate from apartment_condo | Preserve an accommodation distinction rather than collapse it prematurely |
| Entire place / Private room as property type | unknown group, unspecified status | Source label does not identify the underlying property |
| Unseen property label | unknown group, unrecognized status | No substring guessing or automatic residential assignment |
| Bedrooms "0" / "4.0" / empty / "1.5" | 0 / 4 / null missing / null invalid | Integer count, with zero distinct from missing; raw string retained |
| Advertised accommodates "6" | Integer 6 with valid status | Advertised guest capacity; not verified beds or comfortable sleeping |
| minimum_nights "27" / "28" / empty | 1_27_nights / 28_plus_nights / unknown | Transparent analytical stay cohort, not a legal STR determination |
| minimum=30, maximum=2 | unknown stay cohort plus inconsistent flag; original values retained | Do not silently repair a contradictory range |
| Price "$250.00" on a usable row | asking_price_usd=250, raw price retained | Asking rate only; no income or occupancy label |
| Valid price outside study area | Raw price preserved; in_usable_cohort=false, study target/geography null | Keep evidence without silently enlarging the initial study cohort |
| Entirely missing numeric bathrooms | Raw empty value retained; no bathroom-count predictor | No zero fill or unreviewed interpretation of bathroom text |
| Amenities JSON string array / [] | Original string retained; valid status and list count / zero count | No inferred amenity ontology or learned encoding yet |
| Anonymized coordinates | Original strings retained; existing usable points/ZCTA join reused and provenance checked | No east/west shift, address correction, parcel matching or legal inference |
| Listing ID | String throughout, sorted lexicographically only for deterministic file output | No numeric precision loss; storage order is not price/opportunity ranking |

### Row accounting

All **20,651** detailed source rows remain in the private normalized artifact. **17,212** are flagged as the existing usable priced study cohort. The original cleaning excludes 3,195 missing prices and 258 outside-area rows, with 14 overlapping exclusions: **3,439 total excluded**. No extra rows were dropped by Phase 1 normalization. Summary listings are duplicates of detailed observations and were not appended. All seven original archives remain private; only 15 allowlisted source feature strings enter the normalized row evidence.

### What the usable cohort contains

| Research property group | Listings |
| --- | ---: |
| House-like | 6,749 |
| Apartment/condo | 5,538 |
| Hotel/resort | 3,137 |
| Serviced apartment | 885 |
| Guesthouse/suite | 662 |
| Known other | 213 |
| Unknown/unspecified | 28 |
| **Total** | **17,212** |

Minimum stays: **14,069** at 1-27 nights, **3,027** at 28+ nights, **116** unknown. Usable missingness: **9 bedrooms**, **394 beds**, **17,212 numeric bathroom values**, **80 bathroom-text values**. Advertised capacity is valid/populated for all 17,212. Seven amenities arrays are empty; empty does not certify absence of amenities. Price remains uncapped, with no outlier winsorization, scaling, learned imputation, one-hot encoding or model fitting in this phase.

Raw bathroom/amenity evidence is retained for a separately reviewed future transformation. Missing bedrooms/beds are not filled with averages. Full-source and usable counts stay separate in [the aggregate audit](phase1-audit.json), so exclusions cannot disappear from quality reporting.

## Separate property group from room type

**Decision**: Exact-value, versioned property mapping in scripts/normalize_research.py; house-like, apartment/condo, hotel/resort, serviced apartment, guesthouse/suite, known other, unknown. Preserve original labels. Known unspecified labels differ from unseen/missing labels in status.

**Rationale**: 1,965 retained Room in hotel records use Private room; 110 Room in aparthotel records use Entire home/apt. Room type alone cannot isolate residential accommodation. Retained groups: house-like 6,749; apartment/condo 5,538; hotel/resort 3,137; serviced apartment 885; guesthouse/suite 662; known other 213; unknown 28. House-like includes townhouses/villas/cottages and does not mean detached or a particular lot size.

**Alternatives considered**: Room type alone mixes cohorts. Substring/property-name guessing hides unknowns. Collapsing serviced apartments and guest suites into houses loses useful distinctions.

## Preserve capacity and stay semantics

**Decision**: Parse nonnegative integer bedrooms/beds and positive integer advertised capacity/minimum/maximum nights. Null plus missing/invalid status; zero bedrooms remains valid. Minimum 1-27 / 28+ / unknown; contradictory min/max becomes unknown stay cohort with flag.

**Rationale**: Retained 14,069 minimum-stay records below 28 nights, 3,027 at least 28, 116 missing. Capacity is populated for all 17,212, but does not verify physical beds. Bedrooms missing 9; beds missing 394. The 28-night threshold is analytical, not statutory.

**Alternatives considered**: Drop missing records or impute now would hide coverage or leak learned preprocessing. Treat all records as legal STRs would exceed the evidence.

## Defer bathroom and amenity predictors

**Decision**: Retain source strings; validate amenities list-of-strings/count only. Do not derive bathroom or amenity model features yet.

**Rationale**: Numeric bathrooms is wholly missing. Bathroom text includes sharing/half-bath semantics. Amenities arrays are valid, seven usable arrays empty; literal arrays are not a stable amenity ontology.

**Alternatives considered**: Filling bathrooms with zero is false. Unreviewed keyword features introduce opaque semantics. Separate later normalization needs its own documented mapping and fixtures.

## Reuse existing priced cohort and geographic contract

**Decision**: Recompute base clean_rows and compare exact ID-to-record dictionaries with the current public dataset; validate schema/snapshot and geography byte hash/ID coverage. Source rows outside the usable cohort remain private with raw evidence, null study target/geography.

**Rationale**: Keeps current 20,651 / 17,212 denominators aligned and prevents stale joins. No public schema expansion; geography only exists for the current usable cohort. IDs stay strings and cannot be model predictors.

**Alternatives considered**: Build a different priced cohort silently or nearest-ZCTA fallback would invalidate comparisons. Do not ingest summaries as extra observations.

## Keep the next stages explicit

**Decision**: Comps use geography and characteristics, with no default price band. Start with medians before a training-only categorical/regularized baseline. Neither normalization nor the Phase 2 comp selector fits a model.

**Rationale**: Filtering +/-15% of target price first hides candidate discrepancies. ZCTA one-hot supports known areas but cannot learn an unseen area's effect; geographic holdouts must reveal that limitation.

**Alternatives considered**: Random split alone risks geographic/repeated-ID leakage. Buying-value/occupancy targets do not exist in this dataset. Full MLS/scenario-management product remains outside scope.

## How comparable membership is treated (Phase 2, October 10)

[Contract](contracts/comps.md), [selector](../../scripts/select_comps.py) and [aggregate audit](phase2-audit.json) provide the implementation trail. Geography/group/room/stay are exact matches; bedrooms use inclusive +/-1 by default, optional capacity tolerance is explicit. Asking price never filters membership. Subject is excluded. Unknown characteristics and the heterogeneous other group are unsupported; no area expansion. Exclusions count the first failed rule per row, so they reconcile but are not independent/overlapping reason counts.

The 89146 four-bedroom house-like example uses Entire home/apt and 1-27 minimum nights, not the entire ZIP market. Changing one constraint at a time produces:

| Constraint | Comps | Median asking USD/night | Near-edge comps |
| --- | ---: | ---: | ---: |
| Bedrooms +/-1 (default) | 99 | 384.00 | 23 |
| Exact bedrooms | 46 | 371.90 | 12 |
| Default bedrooms, exclude edges | 76 | 416.85 | 0 |
| Default bedrooms, capacity +/-2 around example subject | 44 | 524.95 | 8 |

These are descriptive medians for one deterministic example, not a prediction of that home's rent, a neighborhood valuation or earnings. The 89005 example has two default comps and its median is withheld. Capacity is advertised and not verified beds; the example's capacity/IDs are not published in the aggregate audit.

Of 17,212 usable subjects, default support: 13,503 with at least 20 comps, 3,351 thin samples, 358 unsupported. With strict edge exclusion: 10,114 supported, 3,174 thin, 3,924 unsupported (including boundary-sensitive subjects). The audit computes grouped counts and fixtures check them against direct selector results. The threshold is a research support floor, not statistical confidence. This coverage shows why a model must report unsupported groups rather than promise prices everywhere.
