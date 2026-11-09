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

Review-feature research follows specs/002-review-features/: expose docs/features.md for owner choices, keep scores/counts private, and use development geographic folds only. Do not reuse the inspected Phase 3 final holdout for feature selection or call tuning-fold metrics fresh final evidence. Bathrooms/amenities remain deferred candidates. Review scores are comparable-property characteristics, not promised renovation outcomes; review counts are not occupancy.

# Public research and portfolio outputs

The public field allowlist above describes the existing version-1 explorer, and the private review-feature rule describes the completed 002 experiment. For a new, separately versioned and reviewed research output, the owner authorizes a broader publication contract: market-level and appropriately supported subgroup statistics, charts, model metrics, error analysis, methods, limitations, and selected listing-level aggregate review scores or counts may be published. Define and test the exact output fields, granularity, provenance, missing-value handling, and privacy checks in the relevant specification before release. Do not publish review text, reviewer or host identities, or small-cell examples that reveal them. Keep raw source archives and full source tables out of GitHub and deployed assets; download from the provider for deliberate local research, with recorded source URLs, dates, hashes, and license terms. CI continues to use small fixtures only.

For Inside Airbnb-derived outputs, credit Inside Airbnb, identify each market and snapshot date, link the source and CC BY 4.0 license, and describe modifications. Respect its request not to republish the source dataset. Review any other provider's terms separately; Inside Airbnb's license does not cover third-party material outside its grant. Authentication may limit access to a reviewed demo, but does not replace field review, attribution, or the existing model-release gates. Keep advertised prices separate from realized revenue and review activity separate from bookings or occupancy.
