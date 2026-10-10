# Development

Verify `git rev-parse --show-toplevel` before edits. Preserve existing work. This repository is vegas-str-ml.

From repository root:
- `pnpm --dir web install --frozen-lockfile`
- `pnpm --dir web dev`
- `pnpm --dir web format:check`, `pnpm --dir web lint`, `pnpm --dir web check`, `pnpm --dir web build`
- `uv sync --project pipeline --locked`
- `uv run --project pipeline pytest pipeline/tests -q`
- `uv run --project pipeline ruff check pipeline scripts`
- `uv run --project pipeline ruff format --check pipeline scripts`
- `python scripts/check_assets.py`

CI must not download full datasets. Public outputs allow only string listing IDs, approximate coordinates, asking price, room type, bedrooms, and source neighborhood. A separately versioned geography sidecar may publish string listing IDs, derived five-digit Census ZCTA codes or null, and assigned/ambiguous/unassigned status, and a boolean boundary-sensitivity flag, with boundary provenance and limitations. Private research features stay in ignored data/research/. Never publish host/reviewer data, secrets, raw datasets, or model binaries.

Advertised price is not realized revenue. Unavailable calendar nights are not confirmed bookings. Acquisition costs are unresolved. No opportunity score or investment ranking without validated cost data and explicit scenario assumptions. No parcel matching or legal eligibility claims from approximate coordinates. Keep regulatory sources dated and distinct by jurisdiction.

Use baseline-first ML, fit preprocessing only on training data, group listing IDs across snapshots, and use geographic holdouts. Document limitations and checks actually run. Do not claim future milestones complete. Deploy only within explicit project authorization; no paid resources or unrelated DNS changes.

# Deployment

Production is the existing Direct Upload Cloudflare Pages project vegas-str-ml at https://str.housev.dev. .github/workflows/ci.yml deploys the verified web/build artifact on main pushes after web and pipeline checks, using CLOUDFLARE_API_TOKEN / CLOUDFLARE_ACCOUNT_ID. Pull requests do not deploy; CI never ingests full datasets. Root wrangler.jsonc belongs to the separate legacy Git-connected Worker and is retained to preserve it; bare wrangler deploy does not update production Pages. Follow docs/deployment.md for activation, manual recovery and ownership. Preserve the working Worker, Route 53 nameservers, ops.housev.dev and unrelated resources; no paid resources.

Use issue checkbox criteria and focused PRs for new changes; link evidence before checking criteria or closing issues. PR publication, merge approval and production success are distinct. See CONTRIBUTING.md.

# Research development

Use the pinned Spec Kit workflow in .specify/README.md and .specify/memory/constitution.md for substantial research semantics/evaluation changes. Active milestone specs/001-comparable-price-baseline/ defines phased requirements and checkbox tasks. Private normalization in scripts/normalize_research.py does not expand public fields, fit encoders or train a model. Keep source values and explicit unknowns; review aggregate audit evidence before advancing phases.
