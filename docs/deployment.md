# Deployment preparation

## Current Git-connected Worker setup

The dashboard created a Git-connected Worker named vegas-str-ml. The repository now includes wrangler.jsonc to serve web/build as static assets without an application server. Wrangler 4.148.0 deploy --dry-run passed locally; an authenticated hosted deployment has not been verified.

Open vegas-str-ml > Settings > Build and enter:
- Root directory/path: / (repository root)
- Build command: npx --yes pnpm@12.10.1 --dir web install --frozen-lockfile && npx --yes pnpm@12.10.1 --dir web build
- Deploy command: npx --yes wrangler@4.148.0 deploy
- Preview command: npx --yes wrangler@4.148.0 preview
- Production branch: main
- Build variable: NODE_VERSION=24

Save these settings, then retry the build against the latest main commit. First verify the generated workers.dev URL. No API token belongs in repository files; use the existing dashboard-managed token.

Custom-domain distinction: the Route 53 CNAME instructions below apply to Pages only. Workers Custom Domains require an active Cloudflare zone; a CNAME to workers.dev is not a supported replacement. Keep ops.housev.dev and existing nameservers unchanged. If housev.dev must remain on Route 53, use Pages for the final str.housev.dev address, or deliberately select another hosting/DNS architecture after review. Do not migrate the entire DNS zone merely to resolve this build.

References: https://developers.cloudflare.com/workers/ci-cd/builds/configuration/ and https://developers.cloudflare.com/workers/configuration/routing/custom-domains/.


Recommendation checked October 7, 2026: **Cloudflare Pages static hosting** with adapter-static. The actual app consists of a prerendered shell, JS/CSS/MapLibre worker and compact JSON; it needs no Python service, database, Pages Functions or Worker runtime. See [SvelteKit static adapter](https://svelte.dev/docs/kit/adapter-static).

Cloudflare documents [25 MiB per asset and 20,000 files on Free Pages](https://developers.cloudflare.com/pages/platform/limits/). scripts/check_assets.py enforces these before upload. Real listings are 2,809,128 bytes; boundaries 677,108 bytes. Do not upload data/raw. Future oversized artifacts require deliberate partitioning or a separately authorized storage choice. MapLibre loads dynamically but still has a roughly 1.04 MB JS chunk (about 280 KB gzip) plus its roughly 508 KB worker; the build warning is documented rather than hidden.

## Status and remaining setup

No deployment or DNS modification occurred. No Git remote is configured. Local inspection found neither a wrangler executable nor the usual user-level Wrangler configuration directories; no authenticated Cloudflare project context was available in this repository. Credentials were not inspected or exported. User setup remains: Cloudflare account/project, repository publication or local Direct Upload, and control of housev.dev DNS.

## Recommended first deployment: Git integration

1. Review and publish the repository to the chosen Git host; no commit/push has been performed.
2. In Cloudflare Workers & Pages, create a Pages project using Git integration, repository root directory **web**, build command **pnpm install --frozen-lockfile && pnpm build**, output directory **build**. Select Node 24 and pnpm 12.10.1 (packageManager also pins pnpm). No secrets needed.
3. Deploy first to the generated pages.dev address; check HTTPS, map workers/tiles, JSON source date, all filters, listing detail, mobile layout and visible attribution. Validate the exact deployed artifact, not just local output.
4. In that project, add custom domain **str.housev.dev**. Follow [Cloudflare custom-domain instructions](https://developers.cloudflare.com/pages/configuration/custom-domains/). If housev.dev is external DNS, create only the instructed str CNAME pointing at the assigned pages.dev hostname, after adding the domain in Pages. If managed by Cloudflare, verify its proposed str record and certificate provisioning. Preserve all unrelated records.
5. Confirm HTTPS and data/map interaction at the custom domain. Keep the previous successful deployment for rollback.

## Alternative: Direct Upload

Choose the deployment mode before project creation; [Direct Upload guidance](https://developers.cloudflare.com/pages/get-started/direct-upload/) explains its differences from Git integration. From repository root:

```powershell
pnpm --dir web install --frozen-lockfile
pnpm --dir web build
python scripts/check_assets.py
# Requires account login and explicit project setup
pnpm dlx wrangler login
pnpm dlx wrangler pages project create vegas-str-ml
pnpm dlx wrangler pages deploy web/build --project-name vegas-str-ml
```

These setup/upload commands have not been executed. Free-plan intent does not authorize paid upgrades. Hosting headers are in web/static/_headers; local Vite preview does not exercise Cloudflare header processing. Revisit the hosting decision only if the architecture gains server-side routes.

## Current DNS and account setup

Live public DNS inspection on October 7, 2026 found housev.dev uses AWS Route 53 nameservers. Keep that existing zone; Cloudflare supports an externally managed subdomain with a CNAME. No str CNAME was returned by the public lookup. The local AWS CLI session is expired and requests `aws login`; no DNS write was attempted. A GitHub connector is linked; no Cloudflare connector is exposed in this session.

For Pages build variables set NODE_VERSION=24 and PNPM_VERSION=12.10.1; [build-image documentation](https://developers.cloudflare.com/pages/configuration/build-image/) supports both overrides. Choose framework preset None and enter the static build/output values above explicitly.

After deploying and adding str.housev.dev under Pages Custom domains, sign into [AWS Route 53](https://console.aws.amazon.com/route53/) â†’ Hosted zones â†’ existing public housev.dev zone â†’ Create record. Use record name str, type CNAME, alias Off, value the exact assigned Pages hostname without https://, TTL 300 and Simple routing. Verify no existing str record conflicts before creating; preserve all other records. Follow [AWS record instructions](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resource-record-sets-creating.html). Cloudflare provisions HTTPS after domain verification; confirm the domain becomes Active and test the site.

## Existing GitHub repository

The linked GitHub account confirmed https://github.com/kenner1-unlv/vegas-str-ml exists, is public, and reports size zero with main as its default branch. Local implementation remains uncommitted, with no remote configured. Publish reviewed files to that existing repository before choosing Git integration:

```bash
cd /c/Users/russe/repos/vegas-str-ml
git status --short
git add .
git commit -m "Build initial STR explorer with validated Clark County data"
git branch -M main
git remote add origin https://github.com/kenner1-unlv/vegas-str-ml.git
git push -u origin main
```

These publication commands are instructions and were not executed. If Git requests authentication, use your normal GitHub sign-in or Git Bash `gh auth login` followed by `gh auth setup-git`; do not paste credentials into project files.

Preview configuration includes the required empty previews block. The deploy/preview commands above are Cloudflare dashboard build settings; running wrangler preview in a terminal creates a hosted preview and requires Cloudflare authentication. For a local production preview, use pnpm --dir web build followed by pnpm --dir web preview. A Wrangler deploy dry-run validates packaging but does not verify authenticated preview creation.
