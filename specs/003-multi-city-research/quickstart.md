# Reproduction path (planning-stage)

From the repository root, follow [CONTRIBUTING.md](../../CONTRIBUTING.md) for the existing
web and Python gates. `uv sync --project pipeline --locked` installs the current pipeline.
CI runs fixture tests only: `uv run --project pipeline pytest pipeline/tests -q`.

The four source URLs, dates and hashes are in [source-manifest.json](source-manifest.json).
Download explicitly only when needed. The current four local archives were verified against
the pinned manifest; the three new source files and all normalized rows stay ignored.

```powershell
# Example: explicit local acquisition or verification without acquisition.
uv run --project pipeline python pipeline/market_sources.py --market new-york-city --download
uv run --project pipeline python pipeline/market_sources.py --market new-york-city
uv run --project pipeline python pipeline/market_normalize.py --market new-york-city
# Repeat normalization for each market, then review before publishing aggregates.
uv run --project pipeline python scripts/summarize_market_audits.py --output specs/003-multi-city-research/source-audit.json
```

The normalizer writes private `normalized.jsonl` and `audit.json` per market under
`data/research/multi-city/`. The summary command publishes only reviewed aggregate fields.
Private split membership and any future model artifacts stay in ignored `data/research/`.

The frozen split command reads those normalized private rows and writes only private
membership to ignored `data/research/multi-city/splits.json`:

```powershell
uv run --project pipeline python pipeline/market_splits.py --output data/research/multi-city/splits.json
```

Its stdout is aggregate support evidence; the reviewed [split-support.json](split-support.json)
records counts and membership hashes without listing IDs. Re-run from the same pinned
inputs to check byte repeatability before using any results.

The [frozen evaluation contract](contracts/evaluation.md) and current code support two
separate scoring stages. Development may be repeated for reproducibility; the final CLI
refuses a second run once its aggregate output exists:

```powershell
uv run --project pipeline python pipeline/market_experiments.py --stage development
uv run --project pipeline python pipeline/market_experiments.py --stage final
```

The runner first writes complete **aggregate** diagnostics to this specification
directory; no listing prediction or model binary is written there. Before publication,
preserve those complete reports in ignored local research storage and generate the
reviewed compact summaries:

```powershell
Copy-Item specs/003-multi-city-research/development-results.json data/research/multi-city/development-full.json
Copy-Item specs/003-multi-city-research/final-evaluation.json data/research/multi-city/final-full.json
uv run --project pipeline python scripts/summarize_market_results.py
```

The compact summaries retain metrics, supported subgroup results, uncertainty and
provenance, while replacing individual geographic block labels with error distributions.
Their `full_private_sha256` values bind them to the private complete reports. Do not
delete the final result to retune or claim a new final test. Any revised candidate needs
a newly sourced, untouched evaluation protocol. CI exercises synthetic fixtures, not
full-data training.

The existing Clark County public path remains `pipeline/ingest.py`; historical evaluation
is `pipeline/evaluate.py` and review exploration is `pipeline/review_experiment.py`. Do not
interpret their already reported final/development metrics as new cross-city evidence.
