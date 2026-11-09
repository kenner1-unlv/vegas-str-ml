# Private multi-city research data model

All row-level artifacts stay in ignored `data/research/` or `data/raw/`. The current public
explorer schema stays unchanged. New public outputs require a separate versioned contract.

## Source snapshot (version 1)

Required: `market_id` (stable string slug), `source_area` (provider label),
`snapshot_date` (catalog date), `source_url`, `retrieved_at_utc`, `sha256`, `bytes`,
`license_name`, `license_url`, `schema_header_sha256`. A downloaded file must match its
manifest before parsing. The local source pathname is recorded but not published as data.

## Canonical observation (version 1)

Identity: (`market_id`, `snapshot_date`, `listing_id`), all strings. A repeated listing
across snapshots retains the same (`market_id`, `listing_id`) group. The source `id` is
never coerced to a number. Duplicate identity within a snapshot is invalid and counted.

Fields and rules:

| Field | Meaning and validation |
| --- | --- |
| `source_last_scraped` | Preserve source date separately from catalog snapshot date; invalid/empty status explicit. |
| `asking_price_usd` | Positive finite parsed nightly advertised price or null with missing/invalid status; target, never a predictor. |
| `latitude`, `longitude` | Finite WGS84 source research coordinates or null with invalid status; anonymized and not parcel identity. |
| `room_type` | Exact known source category, including `Hotel room`; unknown labels remain unknown with original string retained privately. |
| `property_type` | Original label retained; reviewed cross-market grouping may be derived separately. |
| `bedrooms`, `beds`, `accommodates` | Nonnegative integral counts where meaningful; advertised capacity positive; missing distinct from zero and invalid. |
| `minimum_nights`, `maximum_nights` | Optional source values/status; cohort use must be explicitly specified and not treated as bookings. |
| `review_scores_*`, `number_of_reviews*`, `reviews_per_month` | Optional private feature values/status; training use requires an availability decision. No review text or reviewer identity. |
| `source_neighborhood` | Source label and its market-specific meaning; not a universal geographic key. |

Keep raw selected source strings privately for parsing audits, excluding host/reviewer
identities, descriptions and review text. A valid zero remains zero. Unknown, missing and
invalid are distinguishable. Row exclusion uses enumerated, first-failure reasons and
preserves aggregate overlap counts where useful. Do not infer property condition or legal
status from coordinates or reviews.

## Partition and experiment records

- **Partition manifest**: protocol/version, market and snapshot hashes, deterministic seed,
  group key, geographic block definition, buffer, train/development/final memberships and
  checksum. Membership is private; aggregate counts and hash may be published.
- **Experiment configuration**: question/hypothesis, target, feature allowlist and
  availability rationale, cohort, preprocessing, baseline/candidate hyperparameters,
  split version, metric definitions and software lock hash.
- **Result**: configuration and data hashes; training/validation/test counts; MAE, RMSE,
  median absolute error and a suitable relative or log error; subgroup counts, bootstrap
  uncertainty method, exclusions, failure analysis, limitations and release status.

Market-level aggregate results may be public after review. Listing-level aggregate review
scores/counts need a separate publication schema, field review and privacy checks. No raw
source table, host/reviewer details, secrets or model binary is a public artifact.
