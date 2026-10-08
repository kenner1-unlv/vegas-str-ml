# Verification record

Local verification on October 7, 2026 Pacific time. This is local evidence; GitHub-hosted CI and Cloudflare deployment have not run.

## Data

Real listings and boundaries downloaded from the verified September 20, 2026 Clark County source URLs. Source discovery and ingestion succeeded. Offline reprocessing validated SHA-256 against the raw manifest and regenerated 17,212 records from 20,651 source rows. All seven source boundary geometries passed validation. Explicit zero counts are present for duplicates, invalid IDs and globally invalid coordinates. Raw files are ignored by Git. Calendar/reviews links were verified; optional downloads were not run.

## Commands

- pnpm --dir web install --frozen-lockfile: verified lockfile installation.
- pnpm --dir web format:check: passed.
- pnpm --dir web lint: passed.
- pnpm --dir web check: zero errors/warnings.
- pnpm --dir web build: static production output passed.
- python scripts/check_assets.py: all public build files under 25 MiB, fewer than 20,000 files; largest file 2,809,128 bytes.
- uv sync --project pipeline --locked: passed.
- uv run --project pipeline ruff check pipeline scripts: passed.
- uv run --project pipeline ruff format --check pipeline scripts: passed.
- uv run --project pipeline pytest pipeline/tests -q: 15 tests passed (price parsing, string ID precision, duplicates, coordinate exclusions, missingness, unknown bedrooms, invalid geometry, property allowlisting, missing schema and preservation on validation failure).

## Browser

Firefox 156 managed by Playwright, production preview at http://127.0.0.1:4173/. Installed missing managed browser before checking.

- Real data loaded, asking-price label and snapshot visible; 17,212 records and median asking price $229.
- Maximum asking price $100 produced 2,853 records; selection from listing browser populated correct detail.
- Maximum $1 displayed empty state; reset restored sample.
- Henderson source filter yielded 784 listings. Room-type and bedroom filters checked against loaded source records.
- Map rendered OpenFreeMap basemap, source boundaries, clusters and points. Clicking a cluster changed map extent/zoom; marker click populated listing 1411646708410770759 at $136 and preserved its ID exactly.
- At 390×844 the page had no horizontal overflow. Controls and listing selection remained operable.
- Failed listing request showed error and Retry recovered after restoring access; delayed request exposed loading state.
- Initial worker resolution defect was fixed by bundling the MapLibre worker URL explicitly. Final browser run had no application errors or missing map-resource notice.

Desktop/mobile screenshots in evidence/ are actual local browser output. The mobile capture includes the map-loading state during the request-delay test; map-clusters.png records the fully loaded clustered map separately. Native labels, focus styles, keyboard-operable filters/listing controls and readable semantic tables are implemented; this is not a full assistive-technology audit.

## Warnings and unverified work

Vite warns about the dynamically imported MapLibre chunk (~1.04 MB / ~280 KB gzip); its worker is ~508 KB. OpenFreeMap Liberty emits nonfatal null road-shield filter warnings. Tile service offers no SLA. Hosted CI, deployment headers on Cloudflare, custom-domain DNS/TLS, automated refresh, optional large downloads and ML/housing integration remain unverified/not implemented.
