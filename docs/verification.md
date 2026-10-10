# Verification record

Evidence dated October 7, 2026 Pacific time. The original local checks below are historical; fresh production and local checks are recorded separately. The successful hosted workflow and deployment are recorded below.

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

Vite warns about the dynamically imported MapLibre chunk (~1.04 MB / ~280 KB gzip); its worker is ~508 KB. OpenFreeMap Liberty emits nonfatal null road-shield filter warnings. Tile service offers no SLA. Automated refresh and ML/housing integration remain unimplemented. The optional source-file archive/audit was added on October 8; see the separate record below. Historical local browser checks do not prove current hosted cluster/marker behavior; fresh hosted checks follow.

## Fresh production checks — October 7, 2026 Pacific

- Public DNS-over-HTTPS lookup returned str.housev.dev CNAME vegas-str-ml.pages.dev, TTL 300. housev.dev retains four AWS Route 53 nameservers. No DNS records or nameservers were changed.
- A fresh browser context with ignoreHTTPSErrors=false loaded the custom domain with HTTP 200; certificate subject str.housev.dev, issuer WE1. No certificate warning was bypassed. The Pages dashboard's domain Active label was not available to inspect.
- /data/index.json, listings.json and boundaries.geojson returned HTTP 200. Index snapshot is 2026-09-20; listing/boundary payloads are 2,809,128 / 677,108 bytes. All 17,212 public listing IDs are strings. The Pages index also returned 200; the legacy Worker page remains 200.
- Deployed page exposes X-Content-Type-Options: nosniff, Referrer-Policy: strict-origin-when-cross-origin and Permissions-Policy camera=(), microphone=(), geolocation=(). No CSP is configured.
- Map canvas rendered with basemap, clusters, points, boundary lines and attribution; Loading map notice disappeared. Nonfatal road-shield warnings remain. Fresh cluster-click/marker-click behavior was not repeated; those interactions remain historical local evidence above.
- Default sample: 17,212 listings, median asking $229. Henderson filter: 784, median $200; listing 3955163 selected with $90 asking price. Maximum $100: 2,853 records; maximum $1: empty sample; reset recovered.
- Sixteen-bedroom filter: five records. Selecting listing 654407021180063478 preserved the exact ID (above JavaScript safe-integer range) and showed $3,986 asking price. Private-room filter returned 4,717, matching freshly fetched data.
- At 390×844, no horizontal document overflow. This is a narrow layout check, not a full mobile or accessibility audit.

## Fresh local checks and deployment audit

Exact root: C:/Users/russe/repos/vegas-str-ml; main HEAD 088dfee (preceded by 23cd24c). Origin is kenner1-unlv/vegas-str-ml. Existing untracked .vscode/ was preserved. The GitHub connector confirmed the public repository and main default branch; issue search returned no issues. Original initial-commit README requested a Las Vegas STR interactive map; docs/scope.md is the current roadmap.

The standard shell launcher failed during process setup. Checks used the installed executables through the Node runtime, without installing or downloading dependencies:

- Prettier --check . in web: passed.
- ESLint . in web: passed.
- svelte-kit sync then svelte-check --tsconfig ./tsconfig.json: zero errors/warnings.
- Vite build in web: passed; adapter-static produced web/build. MapLibre large-chunk warning remains (~1,035 KB JS / 280 KB gzip plus ~508 KB worker).
- Python scripts/check_assets.py: 22 files, largest 2,809,128 bytes, passed.
- Pipeline virtualenv pytest pipeline/tests -q: 15 passed; one nonfatal pytest cache-write warning.
- Pipeline virtualenv ruff check pipeline scripts and ruff format --check pipeline scripts: passed.
- Dependency installation / uv sync were not repeated in this session; earlier locked-install evidence remains above.

Wrangler 4.148.0 whoami and pages project list were attempted using the cached CLI. Both failed with restricted filesystem log writes and network fetch errors; current local OAuth/account capabilities were not verified. Credential files were not read or exported. Browser inventory had no linked account tabs; no Cloudflare connector or GitHub secret-management tool was exposed.

CI now contains a main-only Pages upload job gated on web and pipeline success, using the checked build artifact, serialized uploads, superseded-commit skipping and HTTPS endpoint checks. YAML formatting/syntax and git diff whitespace checks are local validation only; Hosted validation subsequently passed; see the delivery record below. Deployment ownership is documented in deployment.md. No Worker build trigger, account token, GitHub secret, AWS resource or DNS record was changed.

## Hosted delivery — October 7, 2026 Pacific

[Commit 739a55a](https://github.com/kenner1-unlv/vegas-str-ml/commit/739a55a) was published directly to main. [Verify run 37738181925](https://github.com/kenner1-unlv/vegas-str-ml/actions/runs/37738181925), attempt 2, passed web locked installation/format/lint/types/build/asset checks, pipeline locked sync/Ruff/tests, and Pages deployment. The initial attempt failed at the explicit missing-account-ID check; the API token was present. After user configuration, the rerun uploaded successfully to [88bf2920.vegas-str-ml.pages.dev](https://88bf2920.vegas-str-ml.pages.dev). str.housev.dev and data/index.json returned 200 after upload, with snapshot 2026-09-20. No fresh post-upload map-interaction run is implied by those HTTP checks.

Retrospective issues #1 and #2 record shipped work; they are not evidence of prior PR review. New changes follow CONTRIBUTING.md. Local .git synchronization was denied, so local HEAD remains 088dfee despite remote main 739a55a; preserved tracked edits must not be blindly recommitted. Untracked .vscode/, .playwright-mcp/ and %SystemDrive%/ were not published or removed.

## Portfolio follow-up — October 7, 2026 Pacific

README/demo navigation and contributor templates address issue #3. Local Markdown link checks resolved 18 relative file targets with zero missing files. Frontend ESLint, svelte-check (zero diagnostics) and static build passed after adding the repository footer link; the existing MapLibre bundle warning remains. The generated HTML includes the repository link. [PR #7](https://github.com/kenner1-unlv/vegas-str-ml/pull/7) subsequently merged after hosted validation. [Main run 37739667370](https://github.com/kenner1-unlv/vegas-str-ml/actions/runs/37739667370) passed and deployed; the production repository footer link was freshly checked.

## ZCTA research layer and complete source audit — October 8, 2026

Fresh local evidence for issues [#8](https://github.com/kenner1-unlv/vegas-str-ml/issues/8) and [#9](https://github.com/kenner1-unlv/vegas-str-ml/issues/9), separate from earlier deployed checks:

- All seven source files downloaded privately; byte sizes, source URLs and SHA-256 recorded. Streaming CSV audits counted 20,651 detailed/summary listings, 7,537,733 calendar rows and 744,753 detailed/summary reviews. Actual calendar header has no price column; numeric bathroom fields are empty throughout.
- Census 2020 query returned 66 valid polygons, matching independent count-only query. Assignment used the unchanged 17,212-listing release: 17,211 assigned, one unmatched, zero ambiguous, 61 represented codes and 3,614 near-edge flags. Full geometry assigns points; simplified geometry is display-only.
- Locked Python environment synchronization passed offline with uv's cache redirected to ignored data/raw/.uv-cache because the default local cache path could not initialize. Fixture suite: **25 passed**, including rejection of incomplete seven-file manifests before replacing private research output. Ruff check/format, frontend Prettier, ESLint, Svelte diagnostics and production build passed. Geographic client contract check verifies IDs, exact listing hash, codes/counts and rejection cases; CI runs it without downloading datasets.
- Local production preview browser: combined ZCTA 89146 / Entire home/apt / four-bedroom filter yielded **58** records and **$350** median asking price; edge exclusion yielded **46**, still $350. A selected listing exposed approximate ZIP membership and sensitivity wording. Filtering to unmatched records retained one listing and withheld its ZIP-table median; out-of-filter selection cleared. Fresh rebuilt-preview summary showed 61 ZIP areas, retaining the unmatched listing separately. ID 497110058117895483 remained exact in selection and the outbound source URL; Census outlines and selected-area highlighting were visually inspected.
- Existing large MapLibre bundle warning remains. Local favicon returned 404; road-shield basemap warnings were nonfatal. Do not interpret them as failed listing/geography data requests.

The local shell helper is unavailable and local CLI internet sockets are restricted. Downloads used the browser's public download capability, then checksums and audits ran locally. Commands for ordinary network-enabled environments are in data-sources.md. Fresh hosted CI, merge and production evidence belongs in [PR #10](https://github.com/kenner1-unlv/vegas-str-ml/pull/10); local browser checks alone do not establish deployment.

Hosted feature verification: [PR run 37831787070](https://github.com/kenner1-unlv/vegas-str-ml/actions/runs/37831787070) and [branch run 37831775980](https://github.com/kenner1-unlv/vegas-str-ml/actions/runs/37831775980) passed for feature commit 976c79a. Main/production promotion is recorded in PR #10 independently of these branch checks.

PR #10 automated review identified a partial-manifest success path in the complete-source audit. The follow-up requires all seven expected files before output/checksumming, tests preservation of previous output and documents the --all prerequisite. Authenticated Wrangler whoami and Pages project list subsequently succeeded through the authorized shell: existing vegas-str-ml Pages project includes str.housev.dev and reports Git Provider No. Credential files were not read or printed. Local Git fetch also succeeded; earlier environment restrictions above describe the original attempts, not an ongoing account failure.

## October 9 private research normalization

Fresh [Phase 1 verification](../specs/001-comparable-price-baseline/verification.md) records Spec Kit setup, 60 fixture tests, all-source/usable reconciliation, deterministic private output and unchanged public artifacts. Comparable selection/model evaluation remain open; this section adds no new browser or model claims.
