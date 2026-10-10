# Feature Specification: Comparable listings and advertised-price baseline

**Feature Branch**: `001-comparable-price-baseline`

**Created**: 2026-10-09

**Status**: Phases 1 (normalization) and 2 (offline comps) implemented; Phase 3 evaluation remains planned. Delivery evidence is linked in verification.md.

**Input**: Organize STR data into meaningful geographic/property comparisons before ML; preserve source evidence and evaluate advertised nightly price.

## User Scenarios & Testing

### User Story 1 - Trust the research dataset (Priority: P1)
A researcher can distinguish property groups, room types, stay restrictions and missing characteristics while retaining source evidence.

**Why this priority**: Mixed or silently misclassified accommodation undermines comps and training.

**Independent Test**: Rebuild private normalized data and aggregate audit from pinned inputs; reconcile all source rows and retained IDs. Fixture tests cover malformed numbers, unknown labels, large IDs and stale joins.

**Acceptance Scenarios**:

1. Given a private room in a resort, when normalized, then hotel/resort group and original room/property labels remain distinct.
2. Given missing/invalid numbers, when normalized, then null and separate validation statuses replace invented zeroes.
3. Given stale hashes or duplicate IDs, when processing, then fail before replacing prior successful output.

### User Story 2 - Compare properties in the same area (Priority: P2)
A researcher obtains comps in an explicit approximate ZIP area, matching property group, room type and stay cohort with adjustable bedroom/capacity tolerances.

**Why this priority**: Area-wide prices mix materially different accommodation.

**Independent Test**: Fixtures prove exact membership, exclusions and thin-sample behavior without a model.

**Acceptance Scenarios**:

1. Given known subject characteristics, when selecting default comps, then require same ZCTA, group, room type and stay cohort, with bedrooms +/-1.
2. Given fewer than 20 matching priced records, when reporting, then show counts and thin-sample flag, withhold median/discrepancy conclusion.
3. Given unknown characteristics/geography, when selecting, then disclose limitations without silent expansion or unknown-to-known matches.

### User Story 3 - Assess price predictions (Priority: P3)
A reviewer compares baselines and a candidate on held-out geography and inspects errors before a later public prediction decision.

**Why this priority**: Complexity needs credible out-of-sample evidence.

**Independent Test**: Reproduce deterministic splits/evaluation; fixture tests prove zero ID overlap and training-only preprocessing.

**Acceptance Scenarios**:

1. Given repeated snapshots, when splitting, then a listing never appears in both training and holdout.
2. Given an unseen held-out ZCTA, when encoding, then use documented fallback without fitting categories/imputers on holdout.
3. Given candidate results, when reporting, then include USD MAE, median absolute error, RMSE, baseline/subgroup counts and failures even without improvement.

### Edge Cases

- Studio/zero is distinct from unknown; capacity differs from beds.
- Unrecognized property labels, private hotel rooms, contradictory stay ranges remain explicit.
- Missing prices/outside-area rows remain in source denominators, outside initial priced cohort.
- Ambiguous/unassigned/near-edge ZCTAs remain flagged, never corrected to parcels.
- Distinct IDs may still represent related physical properties; thin/unseen groups confer no confidence.

## Requirements

### Functional Requirements

- **FR-001**: Retain every source row privately with string ID, snapshot, allowlisted raw evidence, parsed characteristics and validation statuses.
- **FR-002**: Use versioned explicit property mapping, distinguishing house-like, apartment/condo, hotel/resort, serviced apartment, guesthouse/suite, known other and unknown; audit property jointly with room type.
- **FR-003**: Validate bedrooms, beds, advertised capacity and minimum/maximum stay, separating missing/invalid from zero. Preserve bathroom/amenity evidence; defer unsupported inference.
- **FR-004**: Separate minimum stays 1-27, 28+ and unknown; flag contradictory maximum stays. These are research categories, not legal definitions.
- **FR-005**: Reconcile exact source IDs/price/location against existing usable cohort and snapshot/hash-bound geography; report both denominators.
- **FR-006**: Keep normalized listing rows private and publish only aggregate audit/provenance. Phase 1 changes no public demo data.
- **FR-007**: Default comps require same ZCTA, property group, room type and stay cohort, exclude subject, and use adjustable bedrooms +/-1; capacity tolerance optional and explicit.
- **FR-008**: No default price band; price is comparison outcome. Report exclusions, boundary sensitivity and counts; withhold median/discrepancy for n<20.
- **FR-009**: Implement global/room-type training medians before a candidate; fit learned preprocessing only on training folds; exclude ID and price-derived predictors.
- **FR-010**: Group IDs across snapshots, hold out geography and document separation/buffer limitations. No temporal generalization from one snapshot.
- **FR-011**: Report metrics, subgroups, failures, reproducible splits and model card; public predictions require separate release review.
- **FR-012**: Fixture-based tests cover contracts, failure preservation and leakage. CI does not download datasets or train on private source rows.

### Key Entities

- Source snapshot: hashes, dates and row counts.
- Normalized listing: raw evidence, derived values, cohort membership and statuses.
- Comparison request/result: explicit scope/tolerances, private membership, exclusions and supported summaries.
- Evaluation release: dataset/rules versions, split membership, fitted baseline/candidate and metrics.

## Success Criteria

### Measurable Outcomes

- **SC-001**: All source rows accounted for; all retained IDs join exactly once without multiplication.
- **SC-002**: Identical inputs produce identical normalized bytes/counts; stale/malformed inputs preserve successful outputs.
- **SC-003**: Every label and invalid/missing field has explicit outcome/count; unseen labels never enter known groups.
- **SC-004**: Comp fixtures reproduce membership and n<20 suppression; price alone never changes default membership.
- **SC-005**: Evaluation reports zero ID overlap, held-out areas and baseline/candidate errors; improvement is a result, not a promise.
- **SC-006**: Reviewers can trace requirements -> issues -> checked tasks -> PR -> evidence, seeing unfinished stages open.

## Assumptions

Initial snapshot 2026-09-20, existing bounding-box cohort and Census ZCTAs. ZCTAs are approximate ZIP areas, not named neighborhoods/jurisdictions. The 28-night cutoff and n=20 support floor are explicit analytical defaults, not legal/confidence guarantees. Preserve original values. Phase 1 does not train, encode, change filters or publish capacity. Occupancy, acquisition valuation, MLS, scenario persistence and property management are excluded; no lot-size/renovation/horse-property inference.
