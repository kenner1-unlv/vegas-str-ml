# Decisions

Reviewed October 7, 2026.

- **Static site plus offline Python:** sufficient for a public exploratory map. Avoids server/database maintenance and private credentials in CI.
- **Current stable toolchain:** SvelteKit 3.0.1, Svelte 5.57.2, Vite 8.3.3, adapter-static 4.0.0, MapLibre 6.13.0; pnpm and uv lockfiles capture compatible dependencies. Followed the [SvelteKit 3 migration/configuration guidance](https://svelte.dev/docs/kit/migrating-to-sveltekit-3) and [static adapter documentation](https://svelte.dev/docs/kit/adapter-static).
- **OpenFreeMap public Liberty tiles:** appropriate for public/commercial use without keys or per-request limits, with required attribution. Its operator offers no SLA; [policy and attribution](https://openfreemap.org/). Keep style configurable and listing interaction usable during tile failures.
- **Cloudflare Pages production target:** the existing Direct Upload project serves str.housev.dev; only static files are needed. Workers and the Cloudflare server adapter provide no necessary benefit for this milestone. Revisit if server routes or authenticated workflows are introduced.
- **Keep source neighborhood labels:** explicit city and unincorporated labels enable sample comparison, but approximate source positions and boundary provenance do not establish parcel jurisdiction.
- **No model or opportunity score in the UI:** advertised-rate residuals and acquisition-adjusted investment value require different evidence.

- **GitHub Actions to existing Pages:** native Git integration cannot be added to the Direct Upload project. Gate Wrangler upload on both CI jobs and reuse the checked artifact; production only on main pushes. This preserves the existing domain and Pages history. Hosted delivery passed on October 7, 2026 in Verify run 37738181925, attempt 2. Retain the legacy Worker config until its separate Git build trigger is paused; no Worker deletion or DNS migration.

## ZIP-area research and source enrichment — October 8, 2026

Start geographic stratification with Census 2020 ZCTAs after the user selected ZIP areas over bespoke street partitions. ZCTAs offer reproducible categorical geography but can hide variation within an area. Preserve original labels and use a hash-pinned sidecar to avoid changing the base listing schema. Never treat anonymized dots as houses, force nearest assignments or shift coordinates based on anecdotal direction. Show edge sensitivity and withhold sparse ZIP-table medians. The 150 m sensitivity distance and n=20 display threshold are transparent choices, not validated confidence bounds.

Archive all seven supplied Inside Airbnb files privately with hashes. Summary files duplicate detailed observations. Preserve a nonpersonal research feature allowlist separately from deployed data; source coverage is measured before normalization or modeling. Numeric bathrooms and calendar prices are unavailable in this snapshot. More ingestion preserves research options; it is not evidence of model improvement. One-hot encoding, property-cohort mappings and ML evaluation remain future work.
