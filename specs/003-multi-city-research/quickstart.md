# Reproduction path (planning-stage)

From the repository root, follow [CONTRIBUTING.md](../../CONTRIBUTING.md) for the existing
web and Python gates. `uv sync --project pipeline --locked` installs the current pipeline.
CI runs fixture tests only: `uv run --project pipeline pytest pipeline/tests -q`.

The four source URLs, dates and hashes are in [research.md](research.md). Download the
detailed files deliberately to ignored `data/raw/`, verify bytes against the manifest,
then run the future normalization and experiment CLIs from an issue branch. Exact commands
will be added when their interfaces and code exist; no multi-city training command is
implemented yet. Keep private normalized rows, split membership and model artifacts in
ignored `data/research/`. Only reviewed aggregate evidence enters `specs/` or the case study.

The existing Clark County public path remains `pipeline/ingest.py`; historical evaluation
is `pipeline/evaluate.py` and review exploration is `pipeline/review_experiment.py`. Do not
interpret their already reported final/development metrics as new cross-city evidence.
