# Review-feature verification — October 10, 2026

## Protocol and actual data evidence

Issue [#22](https://github.com/kenner1-unlv/vegas-str-ml/issues/22); protocol frozen before actual fitting in commit d19e835. Specification-quality checklist: 12/12 pass; no hooks configured. Spec Kit setup-plan/setup-tasks/check-prerequisites ran with explicit 002-review-features directory. Owner selected reviews first; other candidates remain deferred.

Pinned local detailed source: 20,651 rows, 90 columns. Exact string-ID join covers all original normalized source rows. [Catalog](../../docs/features.md) and [aggregate report](development-results.json) expose field names/coverage only. No host/reviewer values or raw rows published. Review scores have explicit 1–5 validation; one communication value 5.05 is invalid (raw retained privately), not capped. All four review counts are valid in the 10,366-row development pool.

Five actual Ridge variants use identical three buffered development geographic folds and per-fold fitting-only transforms. Pooled MAE: property-only 165.5262, scores excluding value 163.1381, counts/rate 161.7072, combined excluding value 161.4399, all reviews 161.3342 USD. Aggregate fold/alpha/subgroup counts/errors and provenance are in the report. Selected-alpha diagnostics are tuning-biased exploratory evidence; original final holdout excluded from scoring. Public predictions remain withheld; #17 remains open.

Two actual CLI runs produced identical private bytes on this Windows environment. A separate actual custom run selected cleanliness/location/total reviews, and the recorded numeric feature list exactly matched those plus the three base numeric fields. The full default and custom CLI commands are in quickstart.md.

Original phase3-evaluation.json, private normalized.json/evaluation.json and all seven existing public data files (10 recorded file hashes total) were byte-identical before/after. Property-only pooled alpha metrics exactly equal the original Phase 3 tuning metrics. No new final-holdout metrics or UI interaction verification claimed.

## Checks

- Initial fixture collection failed because implementation modules did not exist; implementation then passed **161 pytest cases**, including 32 new review cases.
- New tests exercise score/count/rate bounds, missing vs zero, exact large-ID joins, personal-value exclusion, stale hashes/schema/snapshot failures, duplicate/unmatched/numeric IDs, invalid selections, baseline overwrite protection, standalone CLI imports, fitting-only preprocessing, identical geographic membership under outer-target edits, buffered/disjoint folds, determinism and CLI output preservation.
- Ruff check and format, asset allowlist/size and geography contract checks passed locally. uv locked environment used existing dependencies; no library added.
- Public build/interaction behavior is unchanged; hosted web/pipeline and delivery evidence belongs to the linked PR/main run. No live browser/map checks repeated for private research changes.

## Requirements traceability

| Requirements | Evidence |
| --- | --- |
| FR-001, SC-001 | Catalog 90 unique source columns with reconciled missing/present counts |
| FR-002/003, SC-002 | Source hash + exact ID join, parsing/status tests and aggregate coverage |
| FR-004/005, SC-003 | Five variants/custom actual run, geographic manifests, outer-target invariance test |
| FR-006/007, SC-004 | Repeated bytes, unchanged original/public hashes, private-only outputs and fixture checks |

## Remaining work

Owner selection/parsing for bathrooms, amenities or other candidates; review-informed comp filters/weighting or web selector; better extreme-price performance, temporal snapshots, fresh untouched final evaluation, uncertainty and release review. This increment establishes correlations with advertised rates, not renovation ROI, bookings or neighborhood earnings.
