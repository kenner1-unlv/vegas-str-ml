# Decisions

Reviewed October 7, 2026.

- **Static site plus offline Python:** sufficient for a public exploratory map. Avoids server/database maintenance and private credentials in CI.
- **Current stable toolchain:** SvelteKit 3.0.1, Svelte 5.57.2, Vite 8.3.3, adapter-static 4.0.0, MapLibre 6.13.0; pnpm and uv lockfiles capture compatible dependencies. Followed the [SvelteKit 3 migration/configuration guidance](https://svelte.dev/docs/kit/migrating-to-sveltekit-3) and [static adapter documentation](https://svelte.dev/docs/kit/adapter-static).
- **OpenFreeMap public Liberty tiles:** appropriate for public/commercial use without keys or per-request limits, with required attribution. Its operator offers no SLA; [policy and attribution](https://openfreemap.org/). Keep style configurable and listing interaction usable during tile failures.
- **Cloudflare Pages production target:** the existing Direct Upload project serves str.housev.dev; only static files are needed. Workers and the Cloudflare server adapter provide no necessary benefit for this milestone. Revisit if server routes or authenticated workflows are introduced.
- **Keep source neighborhood labels:** explicit city and unincorporated labels enable sample comparison, but approximate source positions and boundary provenance do not establish parcel jurisdiction.
- **No model or opportunity score in the UI:** advertised-rate residuals and acquisition-adjusted investment value require different evidence.

- **GitHub Actions to existing Pages:** native Git integration cannot be added to the Direct Upload project. Gate Wrangler upload on both CI jobs and reuse the checked artifact; production only on main pushes. This preserves the existing domain and Pages history. The user reported saving the required GitHub secrets; the first hosted run remains the activation check. Retain the legacy Worker config until its separate Git build trigger is paused; no Worker deletion or DNS migration.
