# Production deployment

Production target: **https://str.housev.dev**, backed by the existing Cloudflare Pages project **vegas-str-ml** (https://vegas-str-ml.pages.dev). GitHub repository: https://github.com/kenner1-unlv/vegas-str-ml, production branch main. This is a Direct Upload Pages project, not a native Git-integrated Pages project.

## Ownership and automatic updates

The repository owner maintains GitHub Actions, the allowlisted public artifacts and the Cloudflare Pages project. AWS Route 53 owns housev.dev DNS. Production deploys only the static web/build directory; there is no Python service, database or Pages Function.

.github/workflows/ci.yml verifies web formatting, lint, types, build and asset limits plus Python lint, formatting and tests. On a push to main, it retains the checked build as a seven-day Actions artifact and deploys that exact artifact only after both jobs pass. Pull requests never deploy. Production uploads are serialized; queued commits superseded on main are skipped. The deploy job uses the GitHub production environment (any configured approval rules still apply), pins Wrangler 4.148.0, and checks the HTTPS page and public index after upload. Endpoint checks do not replace a browser acceptance check or verify the deployed commit's contents.

Automatic delivery is active: [Verify run 37738181925](https://github.com/kenner1-unlv/vegas-str-ml/actions/runs/37738181925), attempt 2, passed web, pipeline and Pages upload on October 7, 2026 Pacific. The first attempt stopped safely for a missing account-ID secret; configuration fixed it. Secret values were not inspected. Required repository or production-environment secrets by name only:

- CLOUDFLARE_API_TOKEN: an account-scoped token with Account / Cloudflare Pages / Edit for the existing account; do not grant unrelated DNS or AWS permissions.
- CLOUDFLARE_ACCOUNT_ID: the account containing vegas-str-ml.

Local Wrangler OAuth authentication is not a GitHub Actions secret and must not be copied or exported. Create/store credentials through the provider's secure account UI. For a new setup, configure the secrets before merging deployment changes and verify Verify → Deploy production Pages succeeds. No credentials belong in files, logs or browser transcripts.

Cloudflare documents that [Direct Upload projects cannot switch to native Git integration](https://developers.cloudflare.com/pages/get-started/direct-upload/). [CI-driven Direct Upload](https://developers.cloudflare.com/pages/how-to/use-direct-upload-with-continuous-integration/) preserves this existing project and its domain. Do not create a replacement project merely to obtain native Git integration.

## Existing Worker

https://vegas-str-ml.kenner1.workers.dev remains a separate legacy deployment. Its Cloudflare Git connection currently rebuilds the Worker on pushes; it does **not** update Pages. Root wrangler.jsonc is retained solely for that working Worker (assets at ./web/build, workers_dev enabled, previews enabled). Pages CLI ignores it because it has no pages_build_output_dir. That warning is expected; the Pages job supplies its output directory, project and branch explicitly.

The new Actions job is the intended Pages production owner. No Worker deletion or build-setting change occurred in this session. After Pages automation succeeds, pause/disconnect only the legacy Worker's Git build trigger in that Worker's Settings → Build so pushes have one intended production path. Preserve its deployed assets and workers.dev endpoint. Until then, main may update both deployments independently with the active Pages job; the Worker is not the custom-domain production target. Do not run bare wrangler deploy to update production Pages.

## Manual recovery

From repository root, with Node 24 and Python available:

```powershell
npx.cmd --yes pnpm@12.10.1 --dir web install --frozen-lockfile
npx.cmd --yes pnpm@12.10.1 --dir web format:check
npx.cmd --yes pnpm@12.10.1 --dir web lint
npx.cmd --yes pnpm@12.10.1 --dir web check
npx.cmd --yes pnpm@12.10.1 --dir web build
python scripts/check_assets.py
uv sync --project pipeline --locked
uv run --project pipeline ruff check pipeline scripts
uv run --project pipeline ruff format --check pipeline scripts
uv run --project pipeline pytest pipeline/tests -q
npx.cmd --yes wrangler@4.148.0 whoami
npx.cmd --yes wrangler@4.148.0 pages project list
npx.cmd --yes wrangler@4.148.0 pages deploy web/build --project-name vegas-str-ml --branch main
```

Use the authenticated account containing the existing project. Do not run pages project create. Review git status first; a manual upload includes local build contents and is not proof of a deployed main commit. CI never downloads full datasets: reviewed compact outputs are checked in. Refresh data separately with pinned ingestion, review provenance/quality and publish only allowlisted outputs before deploying.

Retain previous successful Pages deployments. For recovery, use the existing project's production-deployment rollback control, then revert/fix the offending source change before the next main deployment. A rollback does not alter Git; the next upload can replace it. Do not rebuild unknown historical data or upload raw inputs as a rollback shortcut.

## Domain and verification

Fresh public DNS checks October 7, 2026 Pacific time confirm str.housev.dev CNAME → vegas-str-ml.pages.dev, TTL 300, and housev.dev AWS Route 53 nameservers. HTTPS page and data requests return 200. No DNS write is needed. Cloudflare's dashboard Custom domains Active status could not be inspected in this session; successful public HTTPS is separate evidence.

If recovery is ever needed, first check the existing Pages custom-domain association and existing str record. The required Route 53 record is name str, CNAME, Alias off, target vegas-str-ml.pages.dev, TTL 300, Simple routing. Preserve ops.housev.dev, every unrelated record and all nameservers. Do not substitute a CNAME to workers.dev or migrate the zone.

web/static/_headers configures nosniff, referrer/permissions policy and data cache rules; these were observed on the deployed host. scripts/check_assets.py enforces [Pages asset limits](https://developers.cloudflare.com/pages/platform/limits/): 25 MiB/file and 20,000 files. MapLibre remains a large dynamically imported bundle plus a worker; its warning is documented, not suppressed. See [verification](verification.md) for fresh versus historical evidence and [scope](scope.md) for remaining product work.
