# Tasks: Multi-city advertised-price research

Input: [spec](spec.md), [plan](plan.md), [source audit](research.md),
[data model](data-model.md) and [contracts](contracts/). All implementation tasks are
pending. Create checkbox GitHub issues and issue-based branches before T001. Issue numbers
are assigned by GitHub, never inferred from task IDs. Tests are required by FR-012.

## Phase 1: Foundation and issue setup

- [x] T001 Create linked checkbox issues for source/schema, partition/evaluation, baseline experiments, secondary research and portfolio delivery; record dependency order in specs/003-multi-city-research/verification.md.
- [x] T002 Finalize the four-source manifest, UTC retrieval times, policy review and hash checks in specs/003-multi-city-research/source-manifest.json and research.md; confirm local source files against it.
- [x] T003 Audit selected source-field types, all-column missingness, geographic support, price distributions and room/property labels by market; record aggregate evidence and all exclusions in specs/003-multi-city-research/source-audit.json.
- [x] T004 Freeze spatial block origin/size, buffer, minimum support, final membership rules and feature availability before fitting in specs/003-multi-city-research/contracts/evaluation.md.

## Phase 2: User Story 1 - Four-market cohort

Independent test: reprocess each pinned local source; reconcile all rows and source hashes;
reject malformed sources without replacing previous private outputs.

- [x] T005 [US1] Add synthetic source archives for four market labels, `Hotel room`, missing/zero/invalid values, duplicate IDs and changed headers in pipeline/tests/test_market_sources.py and test_market_normalize.py.
- [x] T006 [US1] Implement four-market source registry, opt-in local download, SHA-256/byte/header verification and atomic private retrieval metadata in pipeline/market_sources.py.
- [x] T007 [US1] Add canonical row parser with market/snapshot/string-ID identity, source scrape date, typed values and explicit missing/invalid statuses in pipeline/market_normalize.py.
- [x] T008 [US1] Add input/included/excluded reconciliation, duplicate-ID and failed-output preservation tests in pipeline/tests/test_market_normalize.py.
- [x] T009 [US1] Run pinned local normalization twice; review and publish aggregate cohort/room/missingness evidence in specs/003-multi-city-research/source-audit.json and research.md, keeping private rows in data/research/.

## Phase 3: User Story 2 - Cross-city generalization

Independent test: fixture manifests have zero group overlap and deterministic geographic
membership; compared methods use the same partition and train-only transforms.

- [x] T010 [US2] Write split fixtures for repeated listing IDs, adjacent coordinates, insufficient blocks and city exclusion in pipeline/tests/test_market_splits.py.
- [x] T011 [US2] Implement frozen within-city/pooled/leave-one-city-out/limited-local partition manifests and observed-point buffer in pipeline/market_splits.py.
- [x] T012 [US2] Test median fallbacks, unseen categories, transform fitting boundaries, target back-transform, serialization and metric correctness in pipeline/tests/test_market_experiments.py.
- [x] T013 [US2] Implement shared global/room-median and Ridge evaluation with configuration/source/split hashes in pipeline/market_experiments.py.
- [x] T014 [US2] Add one preregistered scikit-learn boosting candidate on identical partitions in pipeline/market_experiments.py; record configuration before fitting in contracts/evaluation.md.
- [x] T015 [US2] Add room/market/geographic/price-band diagnostics and support-aware spatial-block uncertainty in pipeline/market_experiments.py and pipeline/tests/test_market_experiments.py.
- [x] T016 [US2] Run development-only comparisons twice, verify split and metric repeatability, then record aggregate results and failures in specs/003-multi-city-research/development-results.json.
- [x] T017 [US2] Freeze chosen configuration, score new NYC/LA/Nashville final partitions once, keep same-snapshot Clark County results historical/development, and review release gates in specs/003-multi-city-research/final-evaluation.json and docs/model-card.md.

## Phase 4: User Story 3 - Justified secondary research

Independent test: one question has a target, baseline, validation/stability protocol and
interpretation; unsupported methods are explicitly deferred.

- [ ] T018 [US3] Audit secondary questions against sample support, prediction-time availability and leakage; freeze one selected protocol or an evidence-backed deferral in specs/003-multi-city-research/secondary-protocol.md.
- [ ] T019 [US3] Add synthetic target/baseline/split tests for the selected secondary question in pipeline/tests/test_market_secondary.py.
- [ ] T020 [US3] Implement and evaluate the selected question in pipeline/market_secondary.py; publish only aggregate findings or a documented support failure in specs/003-multi-city-research/secondary-results.json.

## Phase 5: User Story 4 - Portfolio and delivery

Independent test: every public metric traces to a private run and source; no source rows,
identities, review text or binary enter the Git diff or built site.

- [ ] T021 [US4] Review field/granularity allowlist, attribution, thin-cell suppression and asset privacy with fixtures in pipeline/tests/test_market_publication.py and contracts/publication.md.
- [ ] T022 [US4] Write the measured public research narrative, source citations, comparisons, failures and reproduction path in README.md and docs/model-card.md; mark planned work plainly.
- [ ] T023 [US4] Decide whether a listing-level review aggregate or authenticated demo adds value; if selected, specify it as a separately reviewed issue and contract before any web/src/ or Pages change in specs/003-multi-city-research/verification.md.
- [ ] T024 [US4] Run full fixture/web/asset gates, verify public artifact contents and link actual PR/CI evidence in specs/003-multi-city-research/verification.md before checking issue criteria.

## Dependencies and ownership

T001-T004 precede implementation. T005-T009 establish canonical data before T010-T017.
T018 can begin after T009 but T019-T020 depend on a frozen secondary protocol and splits.
T021-T024 follow measured evidence. A source adapter agent may own one market fixture/adapter
only after T003/T004; the shared schema, split and experiment modules have one owner each.
Use separate issue branches/worktrees for independent work and integrate against the
shared contracts. The lead owns contract changes, conflict resolution and final evidence.

**MVP**: T001-T017 plus T021-T022/T024 for a complete four-market baseline and honest
case study. T018-T020 and T023 are conditional on source support and two-week capacity;
their incomplete status remains visible if deferred.
