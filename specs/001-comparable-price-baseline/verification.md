# Phase 1 verification and remaining scope

Date: 2026-10-09 (America/Los_Angeles). Historical Phase 1 evidence below; Phase 2 evidence follows. The full feature is not converged because US3 evaluation remains unimplemented.

## Fresh local evidence

- Exact repository root verified; main matched origin/main at 55826a9 before creating 001-comparable-price-baseline. Existing untracked .vscode/ preserved.
- Official specify-cli 1.1.3 scaffolded Codex skills/PowerShell scripts; constitution/spec template resolvers, setup-plan, setup-tasks and check-prerequisites succeeded. No extension hooks configured. Specification-quality checklist passes; this is distinct from implementation tasks.
- Locked uv sync (offline cached), Ruff check/format and **69 pytest cases passed**. Existing CI runs the same fixture-based pipeline gate without downloads.
- Fresh actual normalization rechecked all seven archive hashes and exact source/cohort/geography joins: **20,651 source / 17,212 usable**. [Aggregate audit](phase1-audit.json) contains complete property/room tables and numeric/stay statuses. No private rows published.
- Two unchanged runs produced identical private normalized SHA-256: `b0fa8d61e43716062361ae044c97fa3ea97abd82a81049f1485487eabe1419ab` (current code/input bytes). Source/code hashes and rules version are in the audit; checkout line-ending differences can change code-provenance bytes.
- Geography contract check passed 17,212 string-ID assignments/hash/count/rejection cases. Pages assets check passed 24 files, largest 2,809,128 bytes. Public web artifacts, frontend code, lockfile and deployment workflow unchanged.
- Tests cover exact hotel/property semantics, unseen/missing labels, zero/missing/invalid numeric values, 27/28 threshold, contradictory stays, amenity quality, deterministic full/usable denominator retention, stale geography/hash, duplicate/missing joins, source checksum/duplicate IDs and prohibited audit-report overwrites. Nine additional regression cases reject missing/changed Census vintage/source URL/hash/retrieval/limitations, tampered Census bytes and incomplete feature coverage.
- Git ignore checks confirm raw inputs, private normalized rows and machine-local Spec Kit feature pointer excluded from publication.

## Requirements coverage

| Requirements | Phase 1 evidence |
| --- | --- |
| FR-001..004 | Explicit source-preserving normalize(), groups, typed status fields, stay/amenity checks |
| FR-005 | Full seven-file validation, schema/snapshot/hash and exact ID-to-record/sidecar reconciliation |
| FR-006 | Ignored atomic private artifact; explicit aggregate-only report; unchanged public data |
| FR-012 (Phase 1) | Offline fixture failure/determinism coverage and pipeline checks |
| FR-007..008 | Phase 2 contract/selector/audit below; #13 / T013..017 |
| FR-009..011, FR-012 evaluation | Future #6 / tasks T018..023; no splits, encoders or fitted model |

## Delivery evidence

[PR #14](https://github.com/kenner1-unlv/vegas-str-ml/pull/14) contains implementation, final-head validation and merge/main-delivery history. Hosted [PR Verify run 38022898222](https://github.com/kenner1-unlv/vegas-str-ml/actions/runs/38022898222) passed web and pipeline on implementation head bd79ef2; push run 38022893899 also passed. Final-head/main evidence is recorded in the PR before issue closure. The separate legacy Workers Builds check failed for bd79ef2; its cause was not inspected and remains issue #4. No fresh browser interaction is required for private normalization; prior map/browser evidence remains in docs/verification.md and is not claimed as repeated here. Main delivery must be confirmed independently of PR checks.

Automated review found that initial geography acceptance did not require pinned boundary provenance. Fixed before merge: require Census 2020 metadata plus exact local raw archive/manifest/hash/byte/feature-count agreement; rerun actual normalization and 69 fixture cases passed.

## Remaining work

[#13](https://github.com/kenner1-unlv/vegas-str-ml/issues/13) records implemented private comparable membership/support rules. [#6](https://github.com/kenner1-unlv/vegas-str-ml/issues/6): freeze splits/features/release criteria, train baselines/candidate and report actual errors. Bathroom/amenity predictors need reviewed semantics. No ML results, temporal generalization, occupancy, acquisition valuation or public capacity fields are delivered. Separate hosting follow-up #4 and housing-cost research #5 remain open.

## Phase 2 fresh verification (2026-10-10)

- Exact root verified, main synchronized at 2c247d2; branch phase2-geographic-comps created. Pre-existing untracked .vscode/ preserved.
- speckit-implement prerequisite resolver passed; requirements checklist 8/8 checked, no extension hooks. Scope limited to T013..017, not future US3.
- Contract tests were run before selector existed and failed import as expected; implementation then passed **113 total pytest cases**, including 44 Phase 2 cases. Fixtures cover membership/price invariance, hotel/room separation, unknowns, zero bedrooms, inclusive/exact tolerances, optional capacity, n=19/20, edge policy, counting funnel, stale/edited normalization, output path/privacy and failure preservation. Fast support audit is checked against direct selection for both edge policies.
- Current ignored normalization rebuilt offline from pinned inputs. Eight actual selector CLI runs across two example profiles and four constraints matched direct function summaries. [Reproducible aggregate audit](phase2-audit.json) records examples and snapshot-wide support; no IDs/private rows included. Existing Phase 1 audit remains historical, not overwritten.
- Public frontend/data/deployment are unchanged; no fresh map/filter/selection interaction claims for this offline increment. Model fitting/encoding remains #6.
- Local locked sync/Ruff/tests, geographic/assets and Markdown checks passed. [PR #15](https://github.com/kenner1-unlv/vegas-str-ml/pull/15) records final-head and main delivery history. Implementation head ca72109 passed [PR Verify 38088211285](https://github.com/kenner1-unlv/vegas-str-ml/actions/runs/38088211285) and push run 38088208546 (web/pipeline). The separate legacy Worker build failed and remains #4; it is not the Pages delivery gate.

Release scope: private research selector for the next evaluation milestone. Public comp UI/schema changes need a separate reviewed contract. n=20 is not confidence, ZCTA boundaries remain approximate, other/unknown categories remain unsupported, and no acquisition/occupancy/earnings claims are produced.
