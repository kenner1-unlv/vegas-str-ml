# Private normalization contract v1

Requirements FR-001..006, FR-012. Implemented by scripts/normalize_research.py; rules version 1.0.0. Phase 2/3 consume this contract privately. No public web contract change.

## Source and usable inputs

All seven filenames from audit_sources.EXPECTED_FILES must exist in manifest.json and match SHA-256; manifest snapshot_date must equal requested snapshot. Detailed listings must contain all 15 FEATURES fields. Source IDs must be nonempty digit strings and unique; invalid/duplicate IDs fail the normalization run instead of silently dropping evidence.

Public listings.json envelope must be schema_version=1, matching snapshot_date, synthetic=false. Exact ID-to-record equality against ingest.clean_rows plus equal count is required, irrespective of ordering. Geographic sidecar schema/snapshot/listing SHA-256 and exact unique ID coverage must match; statuses assigned/ambiguous/unassigned and boolean near_boundary are validated. Assigned code is a five-digit string; other statuses have null code.

## Normalized artifact

`data/research/<snapshot>/normalized.json` is ignored and contains `audit` and `rows`. Rows sort lexicographically by string ID; this is deterministic storage order, not ranking.

| Field | Contract |
| --- | --- |
| id | Digit string, unique within snapshot; never numeric or predictor |
| snapshot_date | Requested source date |
| raw | Exactly audit_sources.FEATURES source strings; no host/reviewer fields or listing descriptions |
| in_usable_cohort | Boolean; matches current cleaned public study cohort |
| asking_price_usd | Positive source asking price for usable cohort only; null outside it; raw price remains preserved |
| property_group | house_like, apartment_condo, hotel_resort, serviced_apartment, guesthouse_suite, other, unknown |
| property_status | known, unspecified, missing, unrecognized; exact mapping, no substring fallback |
| room_type | entire_home_apt, private_room, shared_room, hotel_room, unknown |
| room_status | known, missing, unrecognized |
| bedrooms, beds | Null or nonnegative integer; zero distinct from null |
| accommodates, minimum_nights, maximum_nights | Null or positive integer; capacity advertised, not verified beds |
| numeric_status | Per numeric field: valid, missing, invalid; empty/whitespace missing, malformed/nonfinite/fractional/out-of-range invalid |
| stay_cohort | 1_27_nights, 28_plus_nights, unknown; unknown if minimum missing/invalid or min/max contradictory |
| stay_range_inconsistent | Boolean; valid maximum below valid minimum; no invented correction |
| amenities_status/count | valid list of strings / missing / invalid; count integer only if valid, empty list count zero |
| geography | For usable IDs only: zcta string/null, status, near_boundary; null for excluded source rows |

Raw numeric bathrooms/bathrooms_text/amenities remain unaltered; there are no inferred bathroom or amenity predictors. Exact property mapping lives in the versioned script; unknown/unusual labels never become presumed residential houses.

## Audit

Schema/rules/snapshot, source manifest/seven archive hashes, public/geography/code/base-ingestion hashes, Census vintage; original quality report; all_source and usable_cohort aggregates. Each aggregate includes property-group/status counts, full property_type x room_type count table, numeric statuses, stay cohorts/inconsistencies, amenities quality and bathroom missingness. No IDs, coordinates, personal data or raw rows in the aggregate report.

## Failure and publication

Validate inputs and serialize all rows before writing. Atomically replace the single normalized artifact via sibling .part file; prior output survives validation failure. Aggregate audit is embedded so rows/audit never mismatch. Optional --audit-report writes the identical aggregate to an explicitly named path; it is not used as a runtime row pointer. No timestamp in normalized content: identical inputs and code yield identical bytes. Private output must never be copied to web/static or committed.

## Future interfaces

Phase 2: request has subject characteristics, explicit ZCTA, bedroom tolerance default 1, optional capacity tolerance and edge policy. Result has private member IDs, counts/exclusions/support and descriptive price summaries only for n>=20. No silent geographic fallback. Freeze concrete interface in #13 before implementation.

Phase 3: versioned split manifest, training-only fitted transforms, baseline/candidate metrics and model card. Freeze split and release decisions in #6 before fitting; no numeric IDs or price-derived predictors, no public binaries.
