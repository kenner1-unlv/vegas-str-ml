# Phase 1 reproducibility and validation

From repository root with Python 3.12+ and uv. Existing public data is checked in; private archive reproduction needs the licensed source download. CI runs fixtures only. Source acquisition is documented in [data sources](../../docs/data-sources.md).

```powershell
uv sync --project pipeline --locked
# Deliberate download of all seven files; omit if already present:
uv run --project pipeline python pipeline/ingest.py --snapshot 2026-09-20 --all
# Base ingestion resets the geography pointer; rebuild existing pinned enrichment:
uv run --project pipeline python scripts/build_geography.py --snapshot 2026-09-20
uv run --project pipeline python scripts/normalize_research.py --snapshot 2026-09-20
# Explicit aggregate-only export, suitable for review after checking contents:
uv run --project pipeline python scripts/normalize_research.py --snapshot 2026-09-20 --audit-report specs/001-comparable-price-baseline/phase1-audit.json
uv run --project pipeline ruff check pipeline scripts
uv run --project pipeline ruff format --check pipeline scripts
uv run --project pipeline pytest pipeline/tests -q
```

Geography needs the pinned Census file already available privately; see existing source instructions for first-time --download. If using existing validated artifacts, run normalization directly; it checks all archive hashes without re-downloading or rebuilding web data.

Expected Phase 1: source 20,651, usable 17,212; private ignored normalized.json; aggregate audit reconciles denominators. Compare hashes from two unchanged runs for determinism. [Contract](data-model.md) specifies values and failure behavior. Fixtures test stale hashes/snapshots, duplicate IDs, numeric edge cases, unknowns, empty/invalid amenities and preserved prior output. No model command or prediction UI is implemented.

On this Windows checkout, default uv cache failed initialization; actual local checks used `uv --cache-dir data/raw/.uv-cache ...`. This ignored cache is a local workaround, not a required production setting.
