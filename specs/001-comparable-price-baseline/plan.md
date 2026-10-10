# Implementation Plan: Comparable listings and advertised-price baseline

**Branch**: `001-comparable-price-baseline` | **Date**: 2026-10-09 | **Spec**: [spec.md](spec.md)

## Summary
Normalize pinned private source data before choosing comps or training. Phases 1 and 2 deliver private normalization and offline comparable research; Phase 3 training remains separate. [Milestone #11](https://github.com/kenner1-unlv/vegas-str-ml/issues/11), [Phase 1 #12](https://github.com/kenner1-unlv/vegas-str-ml/issues/12), [Phase 2 #13](https://github.com/kenner1-unlv/vegas-str-ml/issues/13), [Phase 3 #6](https://github.com/kenner1-unlv/vegas-str-ml/issues/6).

## Technical Context

**Language/Version**: Python 3.12+; CI Python 3.14. Existing TypeScript/Svelte client is unchanged.

**Primary Dependencies**: Standard library plus existing Shapely; pytest/Ruff. Phase 3 will add a pinned scikit-learn dependency through the existing lockfile, not during normalization.

**Storage**: Ignored local raw archives and a single atomically replaced private normalized JSON artifact containing rows plus audit. Aggregate report can be published explicitly.

**Testing**: Offline synthetic pytest fixtures, checksum/join failure preservation, repeat-run determinism, Python lint/format; hosted established web and pipeline checks.

**Target Platform**: Windows local, Linux CI, offline research CLI.

**Project Type**: Existing static frontend and offline pipeline; no server/database added.

**Performance Goals**: Complete the current ~21k-row snapshot on a workstation; no live request latency dependency. Stream source archives; hold only allowlisted listing evidence in memory.

**Constraints**: No raw/research rows, host/reviewer data, model binaries or secrets published. No CI data downloads or live training. No coordinate correction/parcel joins. Public schema unchanged.

**Scale/Scope**: One source snapshot, 20,651 source / 17,212 usable rows. Multiple snapshots, training encoders and model release are subsequent tasks.

## Constitution Check

Pre-research and post-design gates pass: price remains advertised; private rows stay ignored; groups/unknowns explicit; baselines and geographic evaluation planned; issues/checkbox evidence required; no infrastructure changes. No exceptions.

## Project Structure

```text
.specify/memory/constitution.md
.agents/skills/speckit-*/SKILL.md
specs/001-comparable-price-baseline/
  spec.md, plan.md, research.md, data-model.md, quickstart.md, tasks.md
  checklists/requirements.md, phase1-audit.json
scripts/normalize_research.py
pipeline/tests/test_normalize_research.py
scripts/select_comps.py, scripts/audit_comps.py
pipeline/tests/test_comps.py
data/research/<snapshot>/normalized.json  # ignored
```

**Structure Decision**: Extend the existing pipeline, using its base cleaning function to verify cohort alignment. Keep existing deployment/methodology/source docs canonical and link feature contracts rather than copying them.

## Delivery stages

1. **Phase 1 / US1 (#12)**: audit all source/usable values, version explicit mappings and parsers, verify archive hashes and public/geographic joins, atomically publish one private artifact, record aggregate evidence and tests.
2. **Phase 2 / US2 (#13)**: offline comparable selector; matching rules and tolerance tests; count/exclusion/support evidence. Public UI enrichment is a separate contract decision.
3. **Phase 3 / US3 (#6)**: deterministic group/geography splits and training medians; training-only preprocessing and one-hot categorical vocabulary; candidate regularized model; baseline comparison and model card. Decide geographic units/buffers before fitting, based on support audit; log the frozen split strategy and never tune on final holdout. No model binary in Git.

## Complexity Tracking

No constitution deviations. No new production infrastructure. One private file keeps row/audit publication consistent. Detailed split geometry and candidate release thresholds must be frozen in Phase 3 before training, and are explicitly open tasks, not completed decisions.

## Phase 2 implementation decision (2026-10-10)

Branch phase2-geographic-comps implements [comps contract](contracts/comps.md). CLI revalidates the private normalized artifact by rebuilding from pinned local inputs in a temporary ignored directory and comparing parsed data, then selects explicit same-area/group/room/stay matches. Pure selection has no price-dependent membership or area expansion. Fixed support floor 20, optional edge exclusion and capacity tolerance remain explicit. Other/unknown property groups are unsupported rather than bundling unusual lodging as comps. No frontend, public schema or training changes.
