# Scope and roadmap

The application will let people inspect Las Vegas Valley rental data, compare neighborhoods and properties, and investigate investment hypotheses with transparent assumptions. Initial geography is the explicit bounding box [-115.5, 35.8, -114.8, 36.5]; this is a reproducible study area, not an official Valley polygon or the whole county.

## Milestones

1. **Descriptive explorer implemented and publicly served:** versioned ingestion, quality and provenance, interactive filtered map, listing detail, sample medians and counts, accessible listing alternative, responsive interface, CI and deployment instructions. Fresh custom-domain checks are recorded in verification.md. Automated main-to-Pages delivery passed run 37738181925, attempt 2.
2. **Acquisition-cost research and integration:** select a legally reusable source, verify Clark County geographic and date coverage, ingest benchmark data with provenance, align property types and dates, report join failures. Regional home values remain benchmarks, not exact property acquisition prices.
3. **Advertised-price baseline:** global/room-type training medians, leakage-safe feature pipeline, grouped geographic evaluation, error analysis and uncertainty. No income predictions.
4. **Improved models and evaluation:** geographic holdouts, repeated listing grouping, temporal holdouts when multiple suitable snapshots exist, explainability and supported neighborhood comparisons with sample-size limits.
5. **Investment scenarios:** user-entered purchase price, occupancy assumptions, expenses, financing, taxes and fees; sensitivity ranges and explicit hypothetical revenue. No automatic legal-eligibility certification.
6. **Refresh operations:** scheduled downloads only after authorization, immutable release IDs, artifact hashes, quality drift checks, rollback, coverage monitoring.

No accounts, database, persistent Python server, paid infrastructure, listing scrape automation, fabricated opportunity scores, or investment rankings in milestone 1.

## Requirements and remaining work

The original repository README (initial commit 4401c16) requested a "Short Term rental interactive map for Las Vegas". The current static explorer implements that map, filters, clustering, listing selection and neighborhood sample comparisons using the validated Clark County snapshot. This checkout contains no separate original requirements specification or task checklist beyond this roadmap; broader milestones must remain distinct from the original map request.

Operational follow-up: [issue #4](https://github.com/kenner1-unlv/vegas-str-ml/issues/4) tracks Pages dashboard status and pausing the separate Worker Git build trigger without deleting the Worker. Product milestones 2–6 above remain future work; no acquisition data, models, occupancy/revenue conclusions, investment rankings or legal eligibility are implemented.

## Issue roadmap

- Completed retrospective records: [#1 explorer foundation](https://github.com/kenner1-unlv/vegas-str-ml/issues/1), [#2 Pages delivery](https://github.com/kenner1-unlv/vegas-str-ml/issues/2).
- [#3 portfolio navigation](https://github.com/kenner1-unlv/vegas-str-ml/issues/3) links [PR #7](https://github.com/kenner1-unlv/vegas-str-ml/pull/7) and its implementation, validation and merge history.
- Open: [#4 hosting follow-up](https://github.com/kenner1-unlv/vegas-str-ml/issues/4), [#5 housing-cost evidence](https://github.com/kenner1-unlv/vegas-str-ml/issues/5), [#6 advertised-price baselines](https://github.com/kenner1-unlv/vegas-str-ml/issues/6).
- Later milestones 4–6 remain roadmap proposals rather than scheduled or completed implementations.

## Research layers before ML

[#8 Census ZCTA comparisons](https://github.com/kenner1-unlv/vegas-str-ml/issues/8) and [#9 complete source audit](https://github.com/kenner1-unlv/vegas-str-ml/issues/9) link [PR #10](https://github.com/kenner1-unlv/vegas-str-ml/pull/10) and its implementation, validation and merge history. The geographic layer uses approximate ZIP areas, preserved source neighborhoods, room/bedroom filters and explicit boundary/small-sample treatment. The source audit retains all seven supplied files privately and prepares a candidate feature table; it does not train a model.

Remaining: reviewed hotel/resort/residential and minimum-stay cohort mappings, bathroom/amenity normalization, more granular street/named-area research if ZIP areas prove too broad, and baseline-first training-only categorical encoding with grouped geographic evaluation (#6). Exact lot size, renovation/horse-property characteristics, MLS alerts, user-saved scenario assumptions and property-management workflows are future product proposals without implemented data integrations. STR asking prices provide comps; occupancy/cost/profit scenarios require explicit user assumptions and separate evidence.
