# Tasks: Review features and owner feature menu

Input: [spec](spec.md), [plan](plan.md), [contract](contracts/experiment.md).

## Setup and foundation

- [x] T001 Freeze scoped research requirements/protocol in specs/002-review-features/spec.md and contracts/experiment.md; link issue #22.
- [x] T002 Add parsing/source/join fixtures before implementation in pipeline/tests/test_review_features.py.

## US1 - Choose features

Independent test: every source column classified once; counts reconcile; no raw values published.

- [x] T003 [US1] Implement hash-verified complete catalog and typed review enrichment in scripts/review_features.py; scores finite 1..5, counts nonnegative integer, rate finite nonnegative; null plus missing/invalid statuses.
- [x] T004 [US1] Generate complete aggregate menu in docs/features.md and expose current/candidate/restricted fields with caveats.

## US2 - Compare review contributions

Independent test: reproducible fitting-only transforms, identical development folds, custom selection and no new outer test errors.

- [x] T005 [US2] Add geographic/selection/privacy fixtures in pipeline/tests/test_review_features.py.
- [x] T006 [US2] Parameterize numeric features in pipeline/evaluate.py with unchanged baseline defaults.
- [x] T007 [US2] Implement five variants and selectable review subset in pipeline/review_experiment.py; keep original final holdout excluded and public predictions withheld.
- [x] T008 [US2] Run actual pinned data comparison twice and record aggregate results in specs/002-review-features/development-results.json.

## Verification and delivery

- [x] T009 Link feature choices/results from README.md and docs/model-card.md; document verification in specs/002-review-features/verification.md.
- [x] T010 Run fixtures/Ruff/assets, preserve baseline/public hashes and publish focused PR with evidence for issue #22.

## Dependencies and implementation strategy

T001 -> T002 -> T003 -> T004 (independent catalog MVP). T005 -> T006 -> T007 requires T003; then T008 -> T009 -> T010. Sequential shared-file edits; no agent delegation needed. Independent existing asset and lint checks may execute in parallel after implementation. Every task uses checkbox/ID/path; US1 two tasks, US2 four tasks, setup two, delivery two.
