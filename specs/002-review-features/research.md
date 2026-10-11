# Research decisions

## Owner choice

Decision: expose all source columns with coverage/role, implement only review scores/counts now. Owner explicitly selected review features first; bathrooms/amenities and operational fields remain candidates. Names/aggregate missingness of restricted host fields are catalog metadata, never host values.

## Parsing

Decision: seven score columns accept finite 1-5, nonnegative integer review counts, nonnegative reviews_per_month. Out-of-range/nonfinite/malformed become null plus invalid status; zero counts remain valid. Preserve raw selected strings privately. Source probe found communication above five; do not cap or silently fix it. Alternatives: dropping affected rows changes comparison populations; clipping invents ratings.

## Experiment

Decision: use existing development pool only and the same three geographic inner folds with 1 km buffers. Compare property_only, scores_without_value, counts, scores_counts_without_value, all_reviews. Score-value included only in the last default variant; all fields selectable. Keep raw count scale with existing StandardScaler (no speculative popularity weighting). Alternatives: reuse outer test to pick features would turn inspected test evidence into tuning data; fitting a new arbitrary final split after reviewing prior outcomes would not establish independent final performance.

## Interpretation

Review scores describe existing comparable operation/guest experience, not a rating promised for a proposed renovation. Correlation with asking price is not causal renovation return. All model inputs come from the same snapshot; no temporal lead, booked-night or income labels.
