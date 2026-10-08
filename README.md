# Las Vegas STR Explorer

A public Las Vegas Valley map for exploring advertised Airbnb nightly prices and comparing source neighborhoods. Working title; intended domain: str.housev.dev.

Initial milestone implemented locally: SvelteKit/TypeScript/MapLibre explorer, reproducible Python ingestion, source manifest, quality report, tests, CI configuration, and static deployment preparation. No deployed site, housing-cost integration, trained model, occupancy estimate, or investment ranking.

## Quickstart

Requirements: Node 24 LTS, pnpm 12.10.1, Python 3.12+ and uv. Tested locally with Python 3.14.7.

```powershell
cd C:\Users\russe\repos\vegas-str-ml
pnpm --dir web install --frozen-lockfile
uv sync --project pipeline --locked
pnpm --dir web dev
```

Open the Vite URL printed in the terminal. The repository includes the compact real-data outputs, so web development and CI require no dataset download or private credentials. Copy web/.env.example to web/.env only to override the public map style at build time.

```powershell
# Refresh explicitly pinned snapshot; raw files stay ignored
uv run --project pipeline python pipeline/ingest.py --snapshot 2026-09-20
# Reprocess locally with SHA-256 verification and no network
uv run --project pipeline python pipeline/ingest.py --snapshot 2026-09-20 --offline
# Optional large research downloads (not needed for explorer)
uv run --project pipeline python pipeline/ingest.py --snapshot 2026-09-20 --calendar --reviews
```

Without --snapshot, ingestion discovers the newest Clark County snapshot on the source page. Review changes before publishing.

```powershell
pnpm --dir web format:check
pnpm --dir web lint
pnpm --dir web check
pnpm --dir web build
python scripts/check_assets.py
uv run --project pipeline ruff check pipeline scripts
uv run --project pipeline ruff format --check pipeline scripts
uv run --project pipeline pytest pipeline/tests -q
pnpm --dir web preview
```

## Data and limitations

Real [Inside Airbnb Clark County data](https://insideairbnb.com/get-the-data/), snapshot September 20, 2026; retrieved October 7, 2026 Pacific time. 20,651 source rows; 17,212 retained. Seven valid source boundaries. Asking prices are not realized income. Unavailable nights are not bookings. Approximate coordinates do not identify parcels or legal eligibility. Source neighborhood labels distinguish city and unincorporated areas, but are not independently verified jurisdictions.

Public data is attributed to Inside Airbnb under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); basemap attribution is visible in the app. No host names, host IDs, reviews, or reviewer information enter the public outputs. Application code has no selected redistribution license yet.

See [scope and roadmap](docs/scope.md), [architecture](docs/architecture.md), [sources](docs/data-sources.md), [methodology](docs/methodology.md), [decisions](docs/decisions.md), [deployment](docs/deployment.md), and [verification](docs/verification.md).
