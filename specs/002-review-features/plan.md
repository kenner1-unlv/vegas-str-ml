# Implementation Plan: Review-informed comparable research

**Branch**: research-review-features | **Date**: 2026-10-10 | **Spec**: [spec.md](spec.md) | **Issue**: [#22](https://github.com/kenner1-unlv/vegas-str-ml/issues/22)

## Summary

Catalog every detailed-listings column. Independently enrich verified private normalized rows with review values; compare explicitly selectable review sets on existing development geographic folds. Preserve original normalization, final metrics and public assets.

## Technical Context

Python >=3.12, existing locked NumPy/scikit-learn/SciPy; no new dependencies. Offline CLI on Windows/Linux; pytest fixtures and Ruff. Inputs: pinned local gzip CSV, existing normalized JSON and manifests. Private outputs: ignored JSON. Public output: aggregate feature menu and exploratory metrics. Scale: 20,651 source rows. No downloads or model binaries in CI; no deployment architecture change.

## Constitution Check

Before and after design: PASS. Price is only advertised price; reviews are not occupancy. Personal data excluded. Explicit property/geography cohorts retained. Train-only transforms, repeated-ID exclusion and 1 km buffers reused. Original outer holdout targets are not used for new errors or tuning. Issue/PR evidence required. No paid resource or public-data change. No unknown technical choices require research agents.

## Project Structure

- scripts/review_features.py: source hash verification, field roles/catalog and independent typed enrichment.
- pipeline/review_experiment.py: development comparisons and CLI subset selection.
- pipeline/evaluate.py: parameterize existing feature matrix/preprocessor with backward-compatible defaults.
- pipeline/tests/test_review_features.py: parsing, source, partition and selection contracts.
- docs/features.md: generated complete source menu and readable feature groups.
- specs/002-review-features/: contract and measured aggregate evidence.

## Implementation Strategy

US1 catalog is independently useful. US2 uses verified normalized rows and shared transforms; never expands audit_sources.FEATURES, so the original normalization contract remains reproducible. Output destinations cannot overwrite baseline artifacts. Freeze protocol before actual fits; use five fixed variants and optional custom review subset. No public release decision from development comparisons.
