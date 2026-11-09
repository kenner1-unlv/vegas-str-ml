# Planning verification and issue map

Planning review: 2026-11-08 Pacific. No new model was trained, scored, published or
deployed in this increment. The existing `.vscode/` folder was pre-existing and untouched.

## Source observations

The four current detailed Inside Airbnb listing URLs returned HTTP 200. Four local
archives were streamed for headers, aggregate row counts, room types and missing target
counts. All have the same 90-column header; [research.md](research.md) records dates,
bytes, hashes and limitations. The three new archives are ignored under `data/raw/`.
Full row/type/geographic audit, explicit retrieval-event manifests and normalized cohorts
are pending issues below. No raw row or personal field was added to version control.

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
