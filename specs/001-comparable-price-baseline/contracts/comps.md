# Geographic comparable selector v1

Scope: FR-007/008 and Phase 2 portions of FR-012, tasks T013..017, issue #13.
Offline research only. Public fields, filters and model fitting remain unchanged.

## Inputs and validation

Use the Phase 1 private `data/research/<snapshot>/normalized.json`. Before selection the CLI
rebuilds a temporary normalized artifact from the pinned local inputs using the Phase 1 builder
and compares parsed contents exactly. This detects edited rows, stale hashes, wrong rules or
changed geography, without replacing the user's existing normalized artifact. Missing/stale
input exits nonzero with instructions to rerun normalization. No dataset downloads.

Request: digit-string subject ID in this snapshot, nonnegative integer bedroom tolerance
(default 1), optional nonnegative integer advertised-capacity tolerance (default disabled),
edge policy `include` (default) or `exclude`. Studio/zero is valid; tolerance is inclusive.
The subject's assigned ZCTA fixes geography; the selector never expands it. Unknown ID or invalid
options fail rather than choosing another subject. IDs remain strings.

## Subject and candidate support

Supported property groups: house_like, apartment_condo, hotel_resort, serviced_apartment,
guesthouse_suite. Known other and unknown are unsupported: the other group bundles materially
different lodging. Required room type, minimum-stay cohort, assigned ZCTA and bedrooms must be
known. A capacity constraint additionally requires known subject/candidate capacity.
The subject must belong to the usable priced cohort. With edge exclusion, an edge-sensitive
subject is unsupported rather than comparing it confidently to another area.

Unsupported subject returns an explicit reason list, zero comparisons and null summaries.
Candidate membership is independent of asking price within the valid priced input cohort.
Require same ZCTA/group/room/stay, bedroom difference <= tolerance, optional capacity difference
<= tolerance; exclude subject and, when requested, near-boundary candidates.

## Exclusions and result

Rows are checked in this order, producing **one first-failing reason per excluded row**:
subject, outside_usable_cohort, unsupported_property_group, unknown_room_type,
unknown_stay_cohort, unknown_geography, unknown_bedrooms, unknown_capacity (if constrained),
different_zcta, different_property_group, different_room_type, different_stay_cohort,
bedrooms_outside_tolerance, capacity_outside_tolerance, near_boundary (if excluded).
Counts reconcile `input_rows = matched_count + sum(exclusions)` for supported subjects.
This is a sequential exclusion funnel, not overlapping reason prevalence.

Private result contains subject ID, matched string IDs sorted lexicographically, request,
provenance hashes/rules versions, support status, first-failure counts, matched near-edge count,
subject edge flag and count remaining without edge-sensitive comparisons. n=20 is fixed for
descriptive support; it is not a confidence guarantee. For n<20, support is thin_sample and
median/difference values are null. Otherwise report median asking USD/night and the subject's
signed difference from that median in USD/percent. These are descriptive asking-rate differences,
not model residuals, earnings or investment conclusions. No price band, caps or ranking.

The CLI prints **only an aggregate view**, omitting subject/matched IDs. Optional full private
JSON is atomically written only to an ignored `data/research/` path, never normalized.json or
another input. Aggregate result is never automatically committed. Stored normalized.json and
private result hashes bind the run; changing asking prices may change summaries but not matches.

## Commands

```powershell
uv run --project pipeline python scripts/select_comps.py --snapshot 2026-09-20 --subject-id LISTING_ID
# Exact bedrooms, optional capacity tolerance, strict edge exclusion:
uv run --project pipeline python scripts/select_comps.py --snapshot 2026-09-20 --subject-id LISTING_ID --bedroom-tolerance 0 --capacity-tolerance 2 --edge-policy exclude --output data/research/2026-09-20/comps.json
```

LISTING_ID is an existing string ID; this command does not geocode a private home or infer a
parcel. Reproduction needs the local licensed source/Census files described in quickstart.md.
CI uses synthetic fixtures. No new public UI, training, one-hot encoding or revenue assumptions.
