# Phase 1 verification and remaining scope

Date: 2026-10-09 (America/Los_Angeles). Phase 1 only; the full feature is not converged because US2/US3 remain unimplemented.

## Fresh local evidence

- Exact repository root verified; main matched origin/main at 55826a9 before creating 001-comparable-price-baseline. Existing untracked .vscode/ preserved.
- Official specify-cli 1.1.3 scaffolded Codex skills/PowerShell scripts; constitution/spec template resolvers, setup-plan, setup-tasks and check-prerequisites succeeded. No extension hooks configured. Specification-quality checklist passes; this is distinct from implementation tasks.
- Locked uv sync (offline cached), Ruff check/format and **60 pytest cases passed**. Existing CI runs the same fixture-based pipeline gate without downloads.
- Fresh actual normalization rechecked all seven archive hashes and exact source/cohort/geography joins: **20,651 source / 17,212 usable**. [Aggregate audit](phase1-audit.json) contains complete property/room tables and numeric/stay statuses. No private rows published.
- Two unchanged runs produced identical private normalized SHA-256: `25cb6979931da66f8837b7e792fdea27e8e55fcc5d8f8575604fa29e9b037d4e` (current code/input bytes). Source/code hashes and rules version are in the audit; checkout line-ending differences can change code-provenance bytes.
- Geography contract check passed 17,212 string-ID assignments/hash/count/rejection cases. Pages assets check passed 24 files, largest 2,809,128 bytes. Public web artifacts, frontend code, lockfile and deployment workflow unchanged.
- Tests cover exact hotel/property semantics, unseen/missing labels, zero/missing/invalid numeric values, 27/28 threshold, contradictory stays, amenity quality, deterministic full/usable denominator retention, stale geography/hash, duplicate/missing joins, source checksum/duplicate IDs and prohibited audit-report overwrites.
- Git ignore checks confirm raw inputs, private normalized rows and machine-local Spec Kit feature pointer excluded from publication.

## Requirements coverage

| Requirements | Phase 1 evidence |
| --- | --- |
| FR-001..004 | Explicit source-preserving normalize(), groups, typed status fields, stay/amenity checks |
| FR-005 | Full seven-file validation, schema/snapshot/hash and exact ID-to-record/sidecar reconciliation |
| FR-006 | Ignored atomic private artifact; explicit aggregate-only report; unchanged public data |
| FR-012 (Phase 1) | Offline fixture failure/determinism coverage and pipeline checks |
| FR-007..008 | Future #13 / tasks T013..017; no comp engine |
| FR-009..011, FR-012 evaluation | Future #6 / tasks T018..023; no splits, encoders or fitted model |

## Delivery evidence

[PR #14](https://github.com/kenner1-unlv/vegas-str-ml/pull/14) contains implementation, final-head validation and merge/main-delivery history. Hosted [PR Verify run 38022898222](https://github.com/kenner1-unlv/vegas-str-ml/actions/runs/38022898222) passed web and pipeline on implementation head bd79ef2; push run 38022893899 also passed. Final-head/main evidence is recorded in the PR before issue closure. The separate legacy Workers Builds check failed for bd79ef2; its cause was not inspected and remains issue #4. No fresh browser interaction is required for private normalization; prior map/browser evidence remains in docs/verification.md and is not claimed as repeated here. Main delivery must be confirmed independently of PR checks.

## Remaining work

[#13](https://github.com/kenner1-unlv/vegas-str-ml/issues/13): comparable membership/support rules. [#6](https://github.com/kenner1-unlv/vegas-str-ml/issues/6): freeze splits/features/release criteria, train baselines/candidate and report actual errors. Bathroom/amenity predictors need reviewed semantics. No ML results, temporal generalization, occupancy, acquisition valuation or public capacity fields are delivered. Separate hosting follow-up #4 and housing-cost research #5 remain open.
