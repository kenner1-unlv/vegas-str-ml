# Scope and roadmap

The application will let people inspect Las Vegas Valley rental data, compare neighborhoods and properties, and investigate investment hypotheses with transparent assumptions. Initial geography is the explicit bounding box [-115.5, 35.8, -114.8, 36.5]; this is a reproducible study area, not an official Valley polygon or the whole county.

## Milestones

1. **Descriptive explorer implemented and publicly served:** versioned ingestion, quality and provenance, interactive filtered map, listing detail, sample medians and counts, accessible listing alternative, responsive interface, CI and deployment instructions. Fresh custom-domain checks are recorded in verification.md. Automated main-to-Pages delivery is configured; its first hosted run remains to verify.
2. **Acquisition-cost research and integration:** select a legally reusable source, verify Clark County geographic and date coverage, ingest benchmark data with provenance, align property types and dates, report join failures. Regional home values remain benchmarks, not exact property acquisition prices.
3. **Advertised-price baseline:** global/room-type training medians, leakage-safe feature pipeline, grouped geographic evaluation, error analysis and uncertainty. No income predictions.
4. **Improved models and evaluation:** geographic holdouts, repeated listing grouping, temporal holdouts when multiple suitable snapshots exist, explainability and supported neighborhood comparisons with sample-size limits.
5. **Investment scenarios:** user-entered purchase price, occupancy assumptions, expenses, financing, taxes and fees; sensitivity ranges and explicit hypothetical revenue. No automatic legal-eligibility certification.
6. **Refresh operations:** scheduled downloads only after authorization, immutable release IDs, artifact hashes, quality drift checks, rollback, coverage monitoring.

No accounts, database, persistent Python server, paid infrastructure, listing scrape automation, fabricated opportunity scores, or investment rankings in milestone 1.

## Requirements and remaining work

The original repository README (initial commit 4401c16) requested a "Short Term rental interactive map for Las Vegas". The current static explorer implements that map, filters, clustering, listing selection and neighborhood sample comparisons using the validated Clark County snapshot. This checkout contains no separate original requirements specification or task checklist beyond this roadmap; broader milestones must remain distinct from the original map request.

Operational follow-up: verify the gated Pages workflow's first hosted deployment, inspect Pages custom-domain dashboard status, then pause the separate Worker Git build trigger without deleting the Worker. Product milestones 2–6 above remain future work; no acquisition data, models, occupancy/revenue conclusions, investment rankings or legal eligibility are implemented.
