# Implementation Plan: Multi-city advertised-price research

**Branch**: Issue-specific branches after planning | **Date**: 2026-11-08 |
**Spec**: [spec.md](spec.md)

## Summary

Extend the offline Las Vegas research to four reproducible Inside Airbnb market cohorts and
test advertised-price transfer across cities. Keep the public explorer stable. Publish
reviewed aggregate evidence and a portfolio case study. Listing-level review aggregates
and a gated reviewer demo are separate release decisions.

## Technical Context

**Language/Version**: Python >=3.12 and the existing Node 24/SvelteKit 3 client.
**Primary Dependencies**: Existing scikit-learn 1.9.1, NumPy/SciPy, Shapely, pytest and Ruff;
standard-library CSV/gzip/hash handling. Add packages only for justified candidates.
**Storage**: Ignored `data/raw/` and `data/research/`; reviewed aggregate artifacts in Git.
**Testing**: Small synthetic fixtures in `pipeline/tests/`, existing web/asset gates;
full dataset runs locally outside CI.
**Target Platform**: Offline Windows development, Linux CI fixtures, static Pages case study.
**Project Type**: Offline research CLIs with optional static portfolio presentation.
**Performance Goals**: Validate 104,483 source listing rows on local development hardware;
record actual time and memory rather than promising a speedup. Keep CI fixture-only.
**Constraints**: No paid services, raw source publication, host/reviewer output, investment
rankings or public prediction release in this increment.
**Scale/Scope**: Four September 2026 snapshots; temporal evaluation requires separately
verified later snapshots. Regression/generalization and one justified secondary question.

## Constitution Check

The [constitution v1.1.0](../../.specify/memory/constitution.md) requires source hashes and
licenses, private rows, baseline-first leakage-safe evaluation, hypotheses, fixture-only CI
and reviewed public fields. The historical Las Vegas Phase 3 holdout is already exposed;
do not reuse it as fresh final evidence. Review scores are optional and cannot stand for
occupancy or future property outcomes. Recheck these gates before public release.

## Phase 0: Research decisions

[research.md](research.md) records four live URLs, matching 90-column headers, row counts,
price missingness and hotel-room support. NYC has substantial missing-price selection risk.
Clark County is broader than Las Vegas city. Current catalog inspection does not establish
later-snapshot access; temporal generalization remains conditional.

## Phase 1: Design and contracts

- [data-model.md](data-model.md) defines source, private row, partition and result records.
- [contracts/ingestion.md](contracts/ingestion.md) defines verification and exclusions.
- [contracts/evaluation.md](contracts/evaluation.md) freezes split/model/metric decisions.
- [contracts/publication.md](contracts/publication.md) defines portfolio review gates.
- [quickstart.md](quickstart.md) describes private/local and fixture-only reproduction.

### Shared interfaces and evaluation

1. A market registry pins area/date/URL/hash. A verified local archive enters one shared
   canonical normalizer; source-specific differences are explicit adapters. Existing
   `pipeline/ingest.py` remains the version-1 public Clark County path.
2. A partition service groups (`market_id`, `listing_id`) across snapshots. Within-city
   tests use deterministic metric spatial blocks and observed-point buffers. A pooled model
   uses comparable development folds. Leave-one-city-out excludes the whole target city;
   limited local adaptation reserves target-city test blocks before selecting local rows.
   New independent final blocks are reserved in NYC, LA and Nashville; this Clark County
   snapshot supplies only historical/development evidence.
3. Fit imputation, scaling and category vocabulary inside each fitting fold. Define unseen
   market/area behavior before comparison. Freeze new-market final membership before fitting;
   use development folds for feature/hyperparameter selection only.
4. Start with global and room-type medians, Ridge and one scikit-learn tree/boosting
   candidate on shared splits. Predeclare log-target/back-transform handling. Report USD
   MAE, RMSE, median absolute error, log or suitable relative error, subgroup counts,
   residuals and block-bootstrap uncertainty where supported. These are not calibrated
   individual prediction intervals.
5. A secondary price-segment classification is a candidate; define fitting-only local
   thresholds and baseline first. Clustering, anomaly detection, PCA/UMAP, explanations
   and neural benchmarks require specific hypotheses and later tasks if core work permits.
6. Publish a cited research report from reviewed aggregate outputs. Audit every new
   public field; an authenticated demo needs a separate access and artifact review.

## Project Structure

### Documentation (this feature)

```text
specs/003-multi-city-research/
  spec.md  plan.md  research.md  data-model.md  quickstart.md  tasks.md
  contracts/ingestion.md  contracts/evaluation.md  contracts/publication.md
  checklists/requirements.md
```

### Source Code (repository root)

```text
pipeline/
  ingest.py                  # existing public Clark County path, retained
  evaluate.py                # existing historical Vegas evaluation, retained
  market_sources.py          # proposed private source registry and verification
  market_normalize.py        # proposed canonical normalization
  market_splits.py           # proposed geographic and market protocols
  market_experiments.py      # proposed baselines and candidate evaluation
  tests/test_market_*.py     # proposed synthetic contract fixtures
scripts/normalize_research.py # existing private Vegas logic, reused where valid
web/                         # existing explorer, unchanged by private research
```

**Structure Decision**: Extend the offline Python project. Keep v1 and 002 scripts as
historical reproducible paths; extract reusable logic only with regression tests. New
module names are proposed ownership boundaries, not implemented files.

## Two-week integration sequence

| Days | Gate and deliverable |
| --- | --- |
| 1–3 | Finish source/contracts, analyze spec, create checkbox issues and branch ownership. |
| 4–6 | Registry, normalization, audit fixtures and grouped geographic splits. |
| 7–9 | Baseline/Ridge/tree development runs and cross-city protocols. |
| 10–11 | Limited local adaptation, uncertainty/error analysis and one secondary protocol. |
| 12–14 | Repeatability/privacy review, report, CI and integration decisions. |

These are targets, not completion claims. Inadequate source/geographic support or compute
moves secondary methods and demo auth to follow-up issues without weakening core evaluation.

## Complexity Tracking

No constitutional exception is requested. A new hosted runtime, paid tool or authenticated
demo would require a separate design and authorization.
