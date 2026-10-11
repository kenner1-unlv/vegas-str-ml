# Reproduce feature audit and review comparison

From repository root, use the existing pinned local snapshot and current Phase 1 normalized artifact; no new dataset download is needed. See [baseline quickstart](../001-comparable-price-baseline/quickstart.md) if normalization needs rebuilding.

```powershell
uv sync --project pipeline --locked
uv run --project pipeline pytest pipeline/tests -q
uv run --project pipeline python pipeline/review_experiment.py --snapshot 2026-09-20 --output data/research/2026-09-20/review-experiment.json
uv run --project pipeline python pipeline/review_experiment.py --snapshot 2026-09-20 --output data/research/2026-09-20/review-custom.json --features review_scores_cleanliness,review_scores_location,number_of_reviews
```

Both commands keep original baseline files/public assets intact. Output JSON contains private rows/manifests; stdout contains aggregate report only. docs/features.md is the readable source catalog; the report contains exact choices and errors. No improvement is assumed. Cached Windows workaround: uv --cache-dir data/raw/.uv-cache run --project pipeline ... . Same commands without cache override on Linux.
