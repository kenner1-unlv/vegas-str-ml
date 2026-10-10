# Methodology and known limitations

## Initial descriptive explorer

The ingestion requires ID, latitude, longitude, price, room type, bedrooms and neighborhood columns. Price parsing accepts a positive finite USD amount with optional dollar sign and correctly grouped thousands separators; zero, negative, empty, malformed and nonfinite values are excluded. IDs stay strings to avoid JavaScript precision loss. Invalid IDs and later duplicate records are excluded; the first record wins even if it later fails another quality check.

Finite WGS84 coordinates must lie in the explicit Valley bounding box. This excludes valid county listings outside the study area. Missing or invalid bedrooms are retained as unknown. Room type and source neighborhood retain source strings or Unknown. Coordinates are rounded to five decimal places for compactness; this does not improve their accuracy. No price outlier cap is imposed. Very high asking rates may be real or anomalous and remain visible.

Quality summary: 20,651 input rows, zero duplicate/invalid IDs, zero globally invalid coordinates, 3,195 invalid prices (all missing in this snapshot), 258 outside the Valley and 17,212 included. Excluded total is 3,439 because 14 outside-Valley records also have invalid prices. Twelve source rows lack bedrooms. Missingness is measured on all input rows; issue counts may overlap. Boundary geometries must be valid nonempty Polygon/MultiPolygon in WGS84; no silent geometry repair. Full source shapes are retained rather than clipped to the Valley.

The Census ZCTA research layer adds approximate ZIP-area membership and an optional 150 m edge-sensitivity exclusion, preserving original source labels. It does not correct coordinates or identify properties. ZIP-area table medians are withheld below n=20; this display threshold is not statistical confidence. See data-sources.md for assignment, distance and denominator rules.

Every summary and map cluster uses the same filtered sample. Median advertised price is a listing-level statistic, not an area-wide market price or an investment return. Multiple units per owner or duplicated physical properties may remain under distinct IDs. Hotel rooms and long-stay listings are included; minimum nights are not part of the current contract. The name STR Explorer does not certify that every record meets a legal short-term definition. Sample selection, missing prices and platform coverage bias comparisons. No observed fees, taxes, bookings or realized income are available in this explorer.

## Two separate future questions

**Underpriced advertised rental rate:** an asking rate below an appropriately evaluated comparable-listing prediction may identify a rate discrepancy, including differences caused by omitted amenities, stay date, quality or listing errors. It is not evidence of profitability.

**Potentially undervalued investment:** requires acquisition costs and explicit occupancy, fee, expense, tax, financing and regulatory assumptions. Airbnb asking prices alone cannot establish this. Hypothetical revenue must be labeled modeled/scenario revenue, never observed revenue. Unavailable nights include blocked and unavailable dates, not confirmed bookings; never calculate actual occupancy as 365 minus availability.

## Planned ML protocol — not implemented

1. Predict advertised USD nightly rate for comparable listings. Begin with a global training median and room-type medians; report how unknown groups fall back.
2. Freeze feature allowlist and target definition. Exclude price-derived measures, prediction-time-unavailable fields and identifiers. Fit imputers, encoders and transforms inside a training-only pipeline. For ZCTA categories, fit one-hot vocabulary on training folds only and handle unseen/held-out ZCTAs explicitly (for example an unknown-category fallback); report that unseen areas receive no learned area-specific effect. IDs/codes are categories, not ordinal numbers. Geography holdouts and boundary buffers remain required. This encoding is planned, not implemented. Include room/property characteristics and coarse geography where justified; do not imply exact parcel location.
3. Use listing ID groups across snapshots so repeated records cannot leak between train/test. Assess near-duplicate physical listings separately. Reserve spatial blocks (or whole supported areas) as geographic holdouts, with buffers where feasible; do not rely on random splits alone.
4. When suitable historical snapshots exist, train on earlier periods and evaluate on later periods. State whether evaluation targets known versus unseen listings; enforce group exclusion for unseen-listing tests. A single snapshot cannot establish temporal generalization.
5. Tune only in training/grouped validation folds; keep the final geographic/temporal test set untouched. Start with median baselines before regularized linear or tree models.
6. Report USD MAE, median absolute error and RMSE, plus log-scale error if using log target. Report errors by room type, area and price band with sample counts. Avoid MAPE as the sole metric because low-price records dominate. Back-transform predictions correctly.
7. Report holdout-calibrated interval coverage and width, with spatial/temporal coverage diagnostics. Use grouped/bootstrap uncertainty with clear assumptions; geographic distribution shift can invalidate naive intervals. Show small-sample and out-of-distribution flags; do not fabricate certainty.
8. Publish versioned model card, split membership, features, training snapshot hashes, baseline comparisons and failure analysis. No model artifacts in Git. Establish release thresholds before enabling predictions in the UI.

## Implemented research normalization, before ML

[Phase 1](../specs/001-comparable-price-baseline/data-model.md) uses exact versioned property groups separate from room type, typed bedrooms/beds/advertised capacity/stay restrictions, explicit missing/invalid statuses, and analytical 1-27/28+ minimum-stay cohorts. It retains raw bathroom/amenity evidence without deriving unsupported predictors. Records stay private and the explorer sample is unchanged. [Aggregate audit](../specs/001-comparable-price-baseline/phase1-audit.json) reports both full-source and usable denominators. These deterministic domain mappings are not fitted preprocessing. Comp selection, learned encoding, geographic split design and training remain future tasks in the linked spec.
