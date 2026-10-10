# Contributing and reviewing changes

Start with an existing issue or create one describing the concrete problem and checkbox acceptance criteria. Small related changes can share one issue/PR; separate unrelated work. Verify git rev-parse --show-toplevel and read AGENTS.md before editing; preserve existing work.

1. Create a focused branch from current main. Implement the issue's criteria and update affected existing documentation.
2. Open a PR linking its issue with Closes #N only when the full criteria are delivered; use Refs #N for partial work. Explain changed behavior, validation actually run and remaining limitations. Never fabricate tests, model results or historical review.
3. Run appropriate checks below and wait for the PR's hosted Verify checks. PRs do not deploy Pages.
4. Check completed criteria in the issue only with evidence. Leave incomplete criteria unchecked. Review and merge approval are separate from publication; do not merge solely because CI passes.
5. A main update triggers verified Pages deployment. Confirm the upload job and public endpoints before claiming production success. Close completed issues with linked PR/commit and evidence; keep unfinished follow-ups open.

## Checks from repository root

Node 24 and pnpm 12.10.1:

```powershell
npx.cmd --yes pnpm@12.10.1 --dir web install --frozen-lockfile
npx.cmd --yes pnpm@12.10.1 --dir web format:check
npx.cmd --yes pnpm@12.10.1 --dir web lint
npx.cmd --yes pnpm@12.10.1 --dir web check
npx.cmd --yes pnpm@12.10.1 --dir web build
python scripts/check_assets.py
node scripts/check_geography.mjs
uv sync --project pipeline --locked
uv run --project pipeline ruff check pipeline scripts
uv run --project pipeline ruff format --check pipeline scripts
uv run --project pipeline pytest pipeline/tests -q
```

On Linux/macOS use npx instead of npx.cmd. Documentation-only work needs link/content checks; UI changes also need browser verification appropriate to their behavior. CI still runs the full established gates.

Data refreshes are explicit and separate from CI. Never publish raw datasets, host/reviewer data, secrets or model binaries. Preserve string listing IDs. Keep advertised prices, hypothetical revenue and validated observed outcomes distinct. Follow [methodology](docs/methodology.md) for planned ML evaluation and [deployment](docs/deployment.md) for production/recovery commands.

## Substantial research changes

Use the pinned [Spec Kit workflow](.specify/README.md) for data semantics, evaluation or architecture changes. Follow the [project constitution](.specify/memory/constitution.md) and active [spec/plan/tasks](specs/001-comparable-price-baseline/spec.md); implement only the authorized phase and keep later tasks unchecked. Small established-rule fixes retain focused issue/PR checks. Research outputs stay private; publish aggregate evidence after checking the allowlist.
