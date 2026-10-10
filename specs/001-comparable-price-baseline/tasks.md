# Tasks: Comparable listings and advertised-price baseline

**Input**: spec.md, plan.md, research.md, data-model.md, quickstart.md. Tests required by FR-012.

The user's **Phase 1** means normalization/US1, including the setup and foundational sections below. Spec Kit template phase numbers are organizational; Phase 2/3 product work remains unchecked.

## Setup

- [x] T001 Install pinned Spec Kit 1.1.3 Codex skills and PowerShell scaffolding in .agents/skills/ and .specify/.
- [x] T002 Establish project principles in .specify/memory/constitution.md without replacing AGENTS.md.
- [x] T003 Specify stories/requirements and link milestone issues in specs/001-comparable-price-baseline/spec.md and plan.md.

## Foundation

- [x] T004 Audit exact property/room labels and source/usable denominators in specs/001-comparable-price-baseline/research.md.
- [x] T005 Define private row contract, hashes and null/status rules in specs/001-comparable-price-baseline/data-model.md.

## Phase 1 / User Story 1 - Trust the dataset (#12)

Independent check: pinned normalization reconciles source/usable cohorts, repeated bytes match and malformed input preserves prior output.

- [x] T006 [US1] Add explicit property/room mapping and numeric parsers in scripts/normalize_research.py: exact known groups; unseen labels unknown; bedrooms/beds null or nonnegative integer; capacity/stay null or positive integer.
- [x] T007 [US1] Validate archive hashes, source/dataset snapshots, string IDs and exact geographic coverage in scripts/normalize_research.py.
- [x] T008 [US1] Atomically publish one private row/audit artifact and analytical 1-27/28+/unknown stay cohorts in scripts/normalize_research.py; retain all source rows with raw allowlisted evidence.
- [x] T009 [US1] Exercise unknowns, numeric bounds, malformed amenities, determinism and stale/duplicate failure preservation in pipeline/tests/test_normalize_research.py.
- [x] T010 [US1] Reproduce pinned snapshot and record aggregate evidence in specs/001-comparable-price-baseline/phase1-audit.json and research.md.
- [x] T011 [US1] Document CLI/reproduction and private/public boundaries in specs/001-comparable-price-baseline/quickstart.md and contracts/cli.md; link existing docs.
- [ ] T012 [US1] Record final local/hosted checks and linked Phase 1 PR evidence in specs/001-comparable-price-baseline/verification.md and issue #12 before closure.

## Phase 2 / User Story 2 - Geographic comps (#13)

Independent check: fixture membership/exclusions match expected rules; price alone does not alter membership.

- [ ] T013 [US2] Freeze comparison request/result and missing-subject behavior in specs/001-comparable-price-baseline/contracts/comps.md.
- [ ] T014 [US2] Implement explicit same-ZCTA/group/room/stay matching, exclude subject, bedroom tolerance default 1 and optional capacity tolerance in scripts/select_comps.py.
- [ ] T015 [US2] Report counts/exclusions, boundary sensitivity and n<20 suppression without geographic/price fallback in scripts/select_comps.py.
- [ ] T016 [US2] Test membership invariance to price, unknowns, support threshold and tolerance limits in pipeline/tests/test_comps.py.
- [ ] T017 [US2] Record actual results and release decision in specs/001-comparable-price-baseline/verification.md; public enrichment requires separate contract review.

## Phase 3 / User Story 3 - Advertised-price evaluation (#6)

Independent check: reproducible holdouts, zero ID overlap and no training preprocessing fitted on held-out values.

- [ ] T018 [US3] Freeze supported cohort/feature allowlist, geographic split units/buffers, tuning folds and review thresholds before fitting in specs/001-comparable-price-baseline/contracts/evaluation.md.
- [ ] T019 [US3] Add locked evaluation dependencies in pipeline/pyproject.toml and pipeline/uv.lock; implement deterministic grouped geographic split manifest in pipeline/evaluate.py.
- [ ] T020 [US3] Implement global/room-type training medians and train-only imputation/one-hot vocabulary with explicit unseen-area fallback in pipeline/evaluate.py.
- [ ] T021 [US3] Evaluate a regularized candidate against baselines and report USD MAE/median absolute error/RMSE and subgroup counts in pipeline/evaluate.py.
- [ ] T022 [US3] Verify ID exclusion, train-only transforms, geographic separation and reproducible baseline metrics in pipeline/tests/test_evaluation.py.
- [ ] T023 [US3] Publish measured model card, failure analysis and prediction release decision in docs/model-card.md; keep private splits/binaries ignored.

## Cross-cutting

- [ ] T024 Reconcile remaining requirements, task/issue checkboxes and actual release evidence in specs/001-comparable-price-baseline/verification.md.

## Dependencies and execution strategy

Setup -> foundation -> US1 -> US2 -> US3 -> final convergence. Tests and independent checks apply at each stage. Deliver US1 now; do not train while its inputs remain under review. US2 requires normalized contract; US3 can be evaluated independently of a UI but needs the reviewed cohort semantics. Fixture design and documentation may be prepared in parallel after the respective contract is fixed; mutation of shared scripts/task files is sequential. No parallel implementation agents are required.

There are 24 tasks: 3 setup, 2 foundation, 7 US1, 5 US2, 6 US3, 1 cross-cutting. Checked tasks have local implementation evidence; PR/hosted completion is separate T012. Specification-quality checks are not implementation completion.
