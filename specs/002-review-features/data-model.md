# Review enrichment and catalog contract

Base normalized.json stays schema/rules v1. New in-memory enriched rows keep base fields and add review numeric fields, review_raw (only 12 selected strings), review_status (valid/missing/invalid). IDs are digit strings, unique per snapshot. All source IDs exactly equal normalized source IDs; duplicate, malformed or incomplete inputs fail.

Scores: review_scores_rating, accuracy, cleanliness, checkin, communication, location, value (all full review_scores_ prefixes), finite float 1..5 inclusive. Counts: number_of_reviews, number_of_reviews_ltm, number_of_reviews_l30d, number_of_reviews_ly, nonnegative integer. reviews_per_month: finite nonnegative float. Empty/whitespace missing; malformed/nonfinite/fractional counts/out-of-range invalid. No automatic 100-point conversion or clipping.

Catalog: each detailed column exactly once, present/missing counts, role, explanation. Coverage considers stripped blanks; no raw examples, text, host/reviewer values or IDs in published evidence. Baseline normalized fields and ZCTA derivations listed separately. Candidate does not mean predictor implementation or owner approval.

Private result: report aggregates, enrichment rows and buffered development manifests. Report includes review parsing by source/cohort/development, feature sets, fold errors, pooled alpha errors, selected-alpha diagnostics, room/property/ZCTA subgroups and provenance. No model binaries. Repeat snapshot grouping is supported in experiment partitions; the source loader deliberately enriches one snapshot per invocation.
