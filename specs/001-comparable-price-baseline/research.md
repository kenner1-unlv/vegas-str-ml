# Research decisions and Phase 1 evidence

Date: 2026-10-09. Fresh local analysis of the pinned 2026-09-20 detailed archive and current usable string-ID cohort. Machine-readable aggregate evidence: [phase1-audit.json](phase1-audit.json). Original source provenance/license and coordinate limitations remain in [data sources](../../docs/data-sources.md).

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

**Decision**: Comps use geography and characteristics, with no default price band. Start with medians before a training-only categorical/regularized baseline. Phase 1 contains no fitting.

**Rationale**: Filtering +/-15% of target price first hides candidate discrepancies. ZCTA one-hot supports known areas but cannot learn an unseen area's effect; geographic holdouts must reveal that limitation.

**Alternatives considered**: Random split alone risks geographic/repeated-ID leakage. Buying-value/occupancy targets do not exist in this dataset. Full MLS/scenario-management product remains outside scope.
