# Feature Specification: Multi-city advertised-price research

**Feature Branch**: Pending issue-based branches
**Created**: 2026-11-08
**Status**: Draft; source and evaluation contracts precede implementation
**Input**: Owner-approved portfolio research across Clark County/Las Vegas, New York City,
Los Angeles and Nashville. Publish a public case study and consider a gated reviewer demo.

## User Scenarios & Testing

### User Story 1 - Reproduce a comparable four-market cohort (Priority: P1)

A researcher can obtain each named Inside Airbnb snapshot once, verify its provenance, and
prepare compatible private observations without losing source meaning or silently discarding
invalid or missing values.

**Why this priority**: No cross-city result is credible without a consistent, auditable cohort.
**Independent Test**: Reprocess four pinned archives from local copies and reconcile source,
included, excluded and missing counts by market.

**Acceptance Scenarios**:
1. Given a pinned archive for each market, when it is verified and normalized, then its hash,
   date, original fields, exclusions and canonical fields are recorded, with string IDs and no
   host/reviewer identity or review text in the research table.
2. Given absent or malformed prices, coordinates, room types or property attributes, when the
   cohort is prepared, then each has an explicit status and cannot become a valid zero.
3. Given a source `Hotel room`, when the room type is normalized, then it remains distinct from
   other categories. A separate hotel dataset is not required.

---

### User Story 2 - Test cross-city price generalization (Priority: P1)

A reviewer can reproduce comparisons between within-city, pooled and unseen-city advertised
nightly-price models, understand where they fail, and distinguish development findings from
untouched final evidence.

**Why this priority**: Transfer across markets is the central research contribution.
**Independent Test**: Run frozen split manifests and shared baselines on private local data;
verify disjoint listing groups and reproduce aggregate results.

**Acceptance Scenarios**:
1. Given four reviewed market cohorts, when within-city, pooled and leave-one-city-out runs
   execute, then all compared methods use the same appropriate partitions and training-only
   preprocessing; results include MAE, RMSE, counts and subgroup diagnostics.
2. Given limited target-market examples, when an adaptation experiment runs, then local
   training observations cannot enter its test partition and the local sample budget is explicit.
3. Given the already inspected Las Vegas Phase 3 holdout and development results, when
   new candidates are selected, then no Clark County row from this snapshot is described
   as a fresh independent final test. New final evidence is reserved in other markets.

---

### User Story 3 - Investigate additional ML questions (Priority: P2)

A researcher can evaluate a defined classification, segmentation, anomaly or neural-network
question against an appropriate baseline without presenting algorithm count as a result.

**Why this priority**: A portfolio should show justified method choice and critical evaluation.
**Independent Test**: At least one preregistered secondary question has an executable protocol,
baseline, held-out or stability check, interpretation and failure analysis.

**Acceptance Scenarios**:
1. Given a proposed secondary task, when it is admitted to a research phase, then its target or
   interpretive purpose, usable inputs, split or stability protocol and baseline are documented
   before fitting.
2. Given inadequate support or leakage risk, when audited, then the task is deferred with a
   reason instead of a fabricated performance claim.

---

### User Story 4 - Present an honest portfolio case study (Priority: P2)

A hiring reviewer can inspect sources, research questions, reproducible commands, comparisons,
errors and limitations without receiving a raw dataset. An optional interactive demo may require
reviewer authentication after a separate release review.

**Why this priority**: The project must communicate engineering judgment as well as models.
**Independent Test**: Review the public artifact field by field, reproduce aggregate tables, and
confirm the case study separates observed results from planned work.

**Acceptance Scenarios**:
1. Given a completed experiment, when the case study is prepared, then every reported metric
   maps to a versioned source, cohort, split, configuration and run; unknown results stay marked
   planned.
2. Given a proposed listing-level aggregate rating or count, when public output is prepared,
   then it is included only after a versioned field/privacy review and never includes reviewer
   text, identities or the full source table.
3. Given no approved demo access contract, when the case study is published, then the public
   research narrative remains complete without a login.

### Edge Cases

- A source market disappears, changes license/terms, changes columns or provides an incomplete
  archive. Stop that cohort and document a substitute decision; do not silently change markets.
- Repeated listing IDs across snapshots or markets, near-duplicate physical units, and changed
  locations require explicit group and geography handling.
- Missing target prices, extreme valid asking prices, zero review counts, missing review scores,
  unknown room/property labels and thin hotel-room groups retain distinct statuses.
- A city has too few supported geographic units for a held-out protocol; report insufficient
  support and do not substitute a random split as equivalent evidence.
- A large error or unsupported subgroup blocks a release claim even if overall MAE improves.

## Requirements

### Functional Requirements

- **FR-001**: Pin each selected public source by market, date, URL, retrieval time, byte size,
  SHA-256 and license/terms; retain source values in ignored local archives.
- **FR-002**: Normalize four market archives into a versioned private schema with composite
  market/snapshot/string-ID identity, source values, typed values, and missing/invalid statuses.
- **FR-003**: Reconcile row counts, duplicate IDs, room types including Hotel room, coordinates,
  advertised prices, characteristics and source dates without arbitrary price trimming.
- **FR-004**: Define feature availability and exclude identities, target-derived values,
  unavailable-at-prediction fields and review text from model inputs.
- **FR-005**: Freeze group-aware geographic and, where supported, temporal partitions before
  candidate selection; preserve untouched new final evaluations in markets without an
  inspected historical test and record split membership privately and hashes publicly.
- **FR-006**: Evaluate training-only median and linear baselines before any nonlinear method;
  compare methods on shared partitions with reproducible configurations and seeds where supported.
- **FR-007**: Evaluate within-city, pooled, leave-one-city-out and limited-local-data protocols;
  report USD MAE/RMSE, suitable relative error, uncertainty estimates, support counts and
  market/room/geography error analysis.
- **FR-008**: Require a question, hypothesis, target or interpretive purpose, baseline, split or
  stability check and limitations before each secondary ML experiment; defer unsupported tasks.
- **FR-009**: Publish a source-cited case study with measured results and limitations; version
  and review any new public listing-level fields separately from the current explorer.
- **FR-010**: Keep raw archives, full source tables, host/reviewer data, review text, secrets and
  model binaries out of GitHub and deployed assets; use small synthetic fixtures in CI.
- **FR-011**: Preserve the existing public explorer, deployment route, and historical Phase 3
  holdout interpretation. Public predictions remain withheld until a separate release gate passes.
- **FR-012**: Test schema variation, invalid/missing values, partition leakage, train-only fitting,
  metric correctness, deterministic reruns, source/privacy contracts and existing application gates.

### Key Entities

- **Source snapshot**: Market, geographic coverage, source date, archive URL, retrieval time,
  license, byte size and SHA-256.
- **Canonical observation**: Market/snapshot/listing ID, source and typed characteristics,
  explicit statuses, advertised-price target and provenance; private only.
- **Partition manifest**: Research protocol, split version, listing groups, geographic units,
  temporal ordering and membership checksum; row membership private.
- **Experiment result**: Hypothesis, feature set, baseline/candidate config, source and split
  hashes, metrics, support, uncertainty, failure analysis and limitations.
- **Public research artifact**: Reviewed aggregate evidence, citations, field allowlist,
  suppression rules and release decision.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Four selected snapshots have complete provenance and 100% of input rows
  reconciled to included or explicitly excluded/invalid counts by market.
- **SC-002**: Fixture and actual split audits show zero repeated-listing overlap between
  fitting and evaluation partitions and no fitting of transforms on evaluation observations.
- **SC-003**: All four cross-city protocols produce baseline and candidate metrics with counts,
  subgroup diagnostics and reproducible commands; unsupported cells are marked insufficient
  and same-snapshot Clark County results are labeled historical/development evidence.
- **SC-004**: At least one secondary research question has a complete protocol and measured
  or explicitly deferred outcome; the case study does not claim unexecuted methods.
- **SC-005**: Two local reruns from the same pinned inputs and configuration produce the same
  split hashes and metric values within documented numerical tolerance.
- **SC-006**: The public case study contains no raw source table, identities, review text or
  model binary, and every published result traces to a documented source and run.

## Assumptions

- Initial markets are Clark County/Las Vegas, New York City, Los Angeles and Nashville;
  Austin is a substitute candidate if a selected market fails the source audit. The 2026-09
  detailed listings URLs respond and expose common core columns, but row-level quality and
  historical snapshots have not yet been verified.
- The two-week target prioritizes source contracts and price generalization. Classification,
  clustering, anomaly detection, explanations and neural networks are candidate follow-ups;
  at least one justified secondary experiment is targeted in this increment.
- Inside Airbnb public downloads are currently described as CC BY 4.0; each source and any
  archived-data agreement must be rechecked before use. Full datasets are not republished.
- Public presentation is a research case study. A gated reviewer demo is optional and requires
  a separately reviewed access and public-field contract; no paid resources are assumed.
- Advertised price is the prediction target, not revenue. Availability and review counts are
  not observed bookings. Exact parcel matching, legal eligibility, housing acquisition costs,
  opportunity rankings and public model predictions are outside this increment.
