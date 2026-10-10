# Normalization CLI contract

From repository root: `uv run --project pipeline python scripts/normalize_research.py --snapshot YYYY-MM-DD [--audit-report PATH]`.

Inputs are local data/raw/<snapshot>/manifest.json and seven archives, plus web/static/data/<snapshot>/listings.json and geography.json. No network request. Version/schema/value/failure details are in [data-model.md](../data-model.md).

Success writes ignored data/research/<snapshot>/normalized.json atomically and prints source/usable counts and property-group counts. Optional PATH receives aggregate audit only, never listing rows. Report paths cannot overwrite the private normalized artifact, web assets or raw inputs. The command rejects malformed snapshot syntax, missing archives/columns, wrong checksums, snapshot mismatch, invalid/duplicate source IDs, cohort drift and stale/invalid geography. Failure exits nonzero; validation failures preserve prior private artifact. A failure exporting optional report does not roll back the already validated private artifact.

No host/reviewer data, credentials, rows or coordinates printed. No training, learned imputation, model output, public-web mutation or deployment. See [quickstart](../quickstart.md) for reproducible scenarios.
