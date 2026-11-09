# Planning verification and issue map

Planning review: 2026-11-08 Pacific. No new model was trained, scored, published or
deployed in this increment. The existing `.vscode/` folder was pre-existing and untouched.

## Source observations

The four current detailed Inside Airbnb listing URLs returned HTTP 200. Four local
archives were streamed for headers, aggregate row counts, room types and missing target
counts. All have the same 90-column header; [research.md](research.md) records dates,
bytes, hashes and limitations. The three new archives are ignored under `data/raw/`.
The four private cohorts now have verified local source manifests, explicit retrieval
events for the three new archives, typed selected fields, all-column missingness,
geographic support summaries and reconciled row counts in [source-audit.json](source-audit.json).
The tracked aggregate audit contains no raw row or personal field value. Full model-cohort
eligibility and frozen split rules remain pending issue #26.

## Cohort implementation checks (#25)

`pipeline/market_sources.py` verifies bytes, SHA-256 and the detailed header before use;
downloads are explicit and replace a local archive only after verification.
`pipeline/market_normalize.py` writes private normalized rows and an audit under ignored
`data/research/multi-city/`; its selected field allowlist excludes host/reviewer details.
Synthetic tests cover four market paths, string IDs, Hotel room, zero/missing/invalid
values, duplicate IDs, changed headers, hash mismatch and prior-output preservation.
An allowlist test checks that the committed audit contains aggregate counts and provenance
without source rows.
All four actual normalized outputs and private audits matched byte-for-byte on a repeated
run. Ruff passed and the full fixture suite reported **170 passed** locally. Web
formatting/lint/types/build, geography and asset gates also passed. This is
source/cohort evidence only; no price model has been trained or released.

## Frozen partition checks (#26)

The spatial grid, hash assignment, observed-point buffer, minimum support and core feature
allowlist were frozen in [contracts/evaluation.md](contracts/evaluation.md) before any
multi-city model fit. Synthetic fixtures test repeated IDs across snapshots, cross-market
identity, deterministic blocks, near-point exclusion, insufficient support, city exclusion,
and local adaptation that avoids target prices and final rows. Actual private manifests
for all four markets reproduced byte-for-byte on two local runs. The reviewed
[split-support.json](split-support.json) shows zero fitting/final group and block overlap,
per-fold counts and minimum retained observed-coordinate distances above 1 km. Source
coordinate anonymization still limits physical separation claims. No final prices have
been scored.

At this checkpoint, the full Python fixture suite passed **178 tests**, Ruff lint and
format checks passed, and the existing geography and Pages asset checks passed. The web
code has not changed since its previous full passing check.

## Advertised-price evaluation (#27)

The core feature allowlist, fixed Ridge and histogram-boosting configurations, metric
definitions and paired block bootstrap were recorded in
[contracts/evaluation.md](contracts/evaluation.md) before fitting. The development
runner used three frozen geographic folds, selected histogram boosting by pooled USD
MAE and reproduced the complete aggregate result on a second local run. The final CLI
then scored the NYC/LA/Nashville blocks once and wrote
[final-evaluation.json](final-evaluation.json). It refuses a repeat final run.
Training-only preprocessing, unseen categories, median fallback, metrics, serialization,
thin-cell suppression and a synthetic final-protocol smoke test have fixture coverage.
An aggregate-output allowlist test rejects listing-row and identifying fields. The
[model card](../../docs/model-card.md) documents the pooled improvement and hotel-room,
mid-price and cross-city transfer failures. Public predictions remain withheld. No model
binary or source row was added to Git; the current Pages site has not changed.
Complete aggregate diagnostics were copied to ignored local research storage after the
single final pass. `scripts/summarize_market_results.py` produced compact public summaries
linked by SHA-256 to those private complete reports; geographic block labels are reduced
to supported-block error distributions. No model was rescored during this reduction.
The full local gate after this increment passed **188 Python tests**, Ruff lint and
format, web format/lint/typecheck/build, geography contract and Pages asset checks.

## Secondary classification checks (#28)

The market-relative target, per-fold fitting median, majority baseline, fixed logistic
and random-forest configurations, metrics and development-only boundary were frozen in
[secondary-protocol.md](secondary-protocol.md) before fitting. Synthetic tests verify
training-only thresholds, unseen categories, class support and confusion matrices.
NYC, LA and Nashville used only buffered geographic development folds; no outer final
classification score was computed. Two local executions produced identical aggregate
[secondary-results.json](secondary-results.json) content. The model card reports where
the nonlinear hypothesis held and failed. No classifier or source row was published.
The full Python fixture suite now passes **192 tests**; Ruff lint/format and Pages asset
checks also pass. The web application has not changed in this increment.

## Spec Kit consistency analysis

The pinned prerequisite check found the new spec, research, data model, contracts and
tasks. No unresolved clarification marker remains. All 12 functional requirements map
to at least one of 24 unchecked tasks, including synthetic test and publication gates.
The major correction during analysis was to avoid describing any same-snapshot Clark
County row as an untouched new final test; the spec, plan, evaluation contract and task
T017 now reserve new final evidence for NYC, LA and Nashville. No known constitutional
conflict remains. Exact block parameters, full source audit and selected secondary
question are explicit pre-fitting tasks, not unrecorded implementation choices.

## Linked issue sequence

| Issue | Work | Dependency |
| --- | --- | --- |
| [#24](https://github.com/kenner1-unlv/vegas-str-ml/issues/24) | Constitution, source/spec/plan/tasks and planning verification | None |
| [#25](https://github.com/kenner1-unlv/vegas-str-ml/issues/25) | Verified four-market private cohorts | #24 |
| [#26](https://github.com/kenner1-unlv/vegas-str-ml/issues/26) | Frozen grouped geographic/market partitions | #25 |
| [#27](https://github.com/kenner1-unlv/vegas-str-ml/issues/27) | Baseline-first price generalization | #25, #26; related to [#17](https://github.com/kenner1-unlv/vegas-str-ml/issues/17) |
| [#28](https://github.com/kenner1-unlv/vegas-str-ml/issues/28) | One justified secondary question | #25, #26 |
| [#29](https://github.com/kenner1-unlv/vegas-str-ml/issues/29) | Reviewed portfolio case study | #27; #28 where completed |

No issue criteria are checked merely because a plan exists. PR publication, hosted CI,
review, merge and production verification are separate future events.
