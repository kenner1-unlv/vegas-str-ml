# Feature Specification: Review-informed comparable research

**Feature Branch**: `research-review-features`
**Created**: 2026-10-10
**Status**: Implemented; development evidence only, public predictions withheld. Delivery evidence is recorded in verification.md.
**Input**: Add review scores to the model and expose the available features so the owner determines what is useful. The purpose is neighborhood pricing support from established comparable rentals, assuming purchase and improvements separately.

## User Scenarios & Testing

### User Story 1 - Choose research features (Priority: P1)

The owner sees the available Airbnb fields, coverage, meaning and current model use before choosing subsequent features.
**Why this priority**: Feature selection must be visible rather than silently decided by the developer.
**Independent Test**: Reconcile the catalog against every source column, with aggregate coverage and an explicit role for each.
**Acceptance Scenarios**:
1. Given the pinned detailed listings, when cataloged, then every column appears exactly once with coverage and current/candidate/restricted/target/provenance status.
2. Given personal or price-derived fields, when cataloged, then their names and limitations are visible but their values never appear in published research evidence.

### User Story 2 - Measure review contributions (Priority: P2)

The owner compares the existing property features with review-score and review-count additions and can specify a subset for a research run.
**Why this priority**: Established rentals' reviews can describe comparable quality without inventing ratings for a subject property.
**Independent Test**: Run reproducible geographic development comparisons and report aggregate errors and subgroup support.
**Acceptance Scenarios**:
1. Given missing scores or a score above five, when prepared, then they remain distinguishable from valid values and do not become invented source zeroes.
2. Given feature selections, when trained, then the recorded selection exactly matches the run and unknown or duplicate names fail.
3. Given the inspected original final holdout, when experimenting, then its targets are not used for model fitting, tuning or new performance metrics.

### Edge Cases

Zero review counts; missing scores; malformed/nonfinite numbers; out-of-scale scores; duplicate or numeric IDs; stale source hashes; incomplete joins; entirely missing training features; unseen areas; thin subgroups; attempts to overwrite the original normalization/evaluation.

## Requirements

### Functional Requirements

- **FR-001**: Catalog every detailed-listing source field with aggregate missingness, research role and interpretation; expose candidate choices without pretending all are implemented predictors.
- **FR-002**: Preserve the original normalization and first evaluation; create a separate private review enrichment with exact string-ID joins and pinned-source verification.
- **FR-003**: Parse seven review scores and five count/rate features with valid/missing/invalid status. Retain original selected source strings privately.
- **FR-004**: Support explicit review-feature selection and property-only, score, count, combined and value-inclusive comparisons with identical development partitions.
- **FR-005**: Fit preprocessing only on fitting partitions; group repeated listing IDs and retain buffered geographic validation. Do not evaluate the already inspected final holdout again as fresh evidence.
- **FR-006**: Publish aggregate coverage, fold/subgroup errors, provenance, feature lists and limitations only. Keep public predictions withheld.
- **FR-007**: Verify parsing, joins, leakage protections, determinism, selection failures and output privacy with synthetic tests; CI downloads no datasets.

### Key Entities

- **Feature catalog entry**: Source name, missing/present counts, model status and interpretation.
- **Private review enrichment**: Listing ID and snapshot, raw selected review strings, typed values and parsing statuses.
- **Development comparison**: Chosen features, fold membership privately, aggregate metrics and subgroup counts publicly.

## Success Criteria

### Measurable Outcomes

- **SC-001**: 100% of detailed-listing columns are classified and coverage counts reconcile to the source row count.
- **SC-002**: All 12 requested review fields have reproducible parsing counts and no lost or additional listing IDs.
- **SC-003**: Five named comparisons report identical validation membership, errors and subgroup counts; a custom selection can be reproduced.
- **SC-004**: Original final-evaluation and public data artifacts remain unchanged; repeated experiment runs yield identical outputs on the checked environment.

## Assumptions

The existing pinned snapshot and geographic cohort remain the research foundation. Scores are 1–5; counts are nonnegative integers; reviews per month is a nonnegative rate. Review features describe established comps, not proven revenue or the achievable score of a renovated subject. All seven scores, including value, are authorized for experiments; value also receives a separate comparison because it relates to perceived price. The catalog supports later owner choices; implementing every candidate or a web feature-selection UI is outside this increment. Fresh final evaluation, temporal evidence and prediction release remain follow-up #17.
