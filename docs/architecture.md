# Architecture

Offline processing feeds a static public client:

Inside Airbnb → ignored data/raw/{snapshot} + SHA-256 manifest → validated allowlisted artifacts in web/static/data/{snapshot} → index.json → SvelteKit static build → Cloudflare Pages at str.housev.dev → browser filters and MapLibre clusters.

The uv-managed Python pipeline streams gzip CSV records, validates essential columns and polygon geometry with Shapely, and publishes small JSON files. Outputs contain schema_version=1 and a snapshot date. All IDs are strings. Inputs stay outside Git; lockfiles are included. Calendar/review downloads are optional and never used to infer confirmed bookings.

The client validates its listing contract before rendering. Controls share one filtered sample with the map, medians, neighborhood table and listing browser. Clustering happens after filtering, so counts represent the filtered records. Selection clears when a listing falls outside filters. The listing browser provides a keyboard-accessible alternative to spatial interaction. No map interaction sends data to a Python backend.

The page is prerendered and loads data in the browser. SvelteKit 3 configuration lives in vite.config.ts; MapLibre is loaded dynamically after mount. Its worker URL is explicitly bundled as an asset. Static deployment avoids a Cloudflare runtime adapter and can move to another static host. Hosting headers and deployment procedures are isolated.

A download writes .part then renames; preprocessing completes before public writes and updates the index last. Snapshot folders can be regenerated; publication is not a cross-file atomic transaction. Do not process directly in a live serving directory. Build a complete artifact, validate, then deploy. Future refreshes need immutable release IDs and atomic promotion. Keep old validated releases for rollback.

Public requests go to the app host and OpenFreeMap tile/style/glyph endpoints. No cookies, accounts, or analytics are added by this application. Tile service outages and devices without WebGL retain listing exploration and expose a map status message.

Production delivery: GitHub Actions on main checks web and Python independently, retains the tested static artifact, then uploads it to the existing Direct Upload Pages project after both succeed. Deployment credentials exist only in GitHub secrets; no dataset fetch or Python runtime is part of hosting. Its first hosted run must succeed before automatic delivery is considered verified. The Git-connected Worker and root Wrangler config are a separate legacy path, retained pending build-trigger cleanup. See deployment.md for the single operational procedure.
