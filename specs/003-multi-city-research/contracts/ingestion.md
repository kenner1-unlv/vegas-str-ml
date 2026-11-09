# Private source and normalization contract (draft v1)

The four market/date/URL/hash entries in [research.md](../research.md) are pinned inputs.
Before processing, compare local bytes with the pinned digest and record retrieval UTC time,
source page, license/terms and header digest. A mismatch fails without replacing a prior
normalized artifact. Download only on an explicit local command, never in CI.

Identity is (`market_id`, `snapshot_date`, string `id`). Reject malformed or duplicate IDs
within a snapshot with enumerated counts. Across snapshots, use (`market_id`, `id`) as a
listing group. Do not combine the summary listing table with detailed listings.

Process all source rows to an aggregate audit. Parse price as positive finite advertised
USD or missing/invalid. Preserve valid extreme prices; flag tails for diagnostics. Parse
finite WGS84 coordinates and record outside-study-area rules per market before filtering.
Room type retains `Entire home/apt`, `Private room`, `Shared room`, `Hotel room` or explicit
unknown. Keep source property labels, source scrape date and source neighborhood. Numeric
counts distinguish missing, invalid and valid zero; `accommodates` must be positive.
Optional review scores/counts retain missing/invalid status and are not automatically model
inputs. No host/reviewer columns, review text or descriptions enter normalized output.

Use atomic private output writes after all validation. Publish only aggregate audit after
manual review: input/included/excluded counts, first-failure reasons, missingness, room
support, source hashes and limitations. Reconcile `input = included + excluded`; retain
source-row denominators as well as model-cohort denominators. Tests use tiny synthetic
archives for malformed input, duplicate IDs, zero/missing, hotel rooms, hash mismatch,
idempotence and prior-output preservation.
