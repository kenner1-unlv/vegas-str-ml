"""Compare selectable review features privately on development geography only."""

import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import numpy as np
import sklearn
from review_features import COUNTS, REVIEWS, SCORES, coverage, enrich
from select_comps import load_verified, output_path

from evaluate import (
    ALPHAS,
    CATEGORICAL,
    NUMERIC,
    ROOT,
    atomic_write,
    baselines,
    bucket,
    buffer_train,
    cohort,
    features,
    make_model,
    membership,
    metrics,
    split,
    target,
)

VERSION = "1.0.0"


def selections(value):
    if value is None:
        return {
            "property_only": (),
            "scores_without_value": SCORES[:-1],
            "counts": (*COUNTS, "reviews_per_month"),
            "scores_counts_without_value": (*SCORES[:-1], *COUNTS, "reviews_per_month"),
            "all_reviews": REVIEWS,
        }
    names = [s.strip() for s in value.split(",")]
    if len(names) != len(set(names)) or not set(names).issubset(REVIEWS):
        raise ValueError("Review selection must contain unique allowlisted names")
    return {"property_only": (), "custom": tuple(f for f in REVIEWS if f in names)}


def prediction(model, rows, numeric):
    with np.errstate(over="raise", invalid="raise"):
        values = np.expm1(model.predict(features(rows, numeric)))
    if not np.isfinite(values).all():
        raise ValueError("Nonfinite prediction")
    return np.maximum(values, 0), int(np.sum(values < 0))


def subgroup_metrics(rows, actual, predicted):
    result = {}
    for dimension in ("room_type", "property_group", "zcta"):
        labels = [r["geography"]["zcta"] if dimension == "zcta" else r[dimension] for r in rows]
        result[dimension] = {
            label: {
                "thin_sample": labels.count(label) < 20,
                **metrics(
                    np.array(actual)[np.array(labels) == label],
                    np.array(predicted)[np.array(labels) == label],
                ),
            }
            for label in sorted(set(labels))
        }
    return result


def experiment(rows, variants):
    if not variants or variants.get("property_only") != ():
        raise ValueError("Property-only reference required")
    for selected in variants.values():
        if len(selected) != len(set(selected)) or not set(selected).issubset(REVIEWS):
            raise ValueError("Invalid feature selection")
    retained, exclusions = cohort(rows)
    development, held, outer_buffer = split(retained)
    for row in development:
        for field in {f for selected in variants.values() for f in selected}:
            value = row.get(field)
            if value is not None and (
                type(value) not in {int, float}
                or not math.isfinite(value)
                or (field in SCORES and not 1 <= value <= 5)
                or (field in COUNTS and (value < 0 or not float(value).is_integer()))
                or (field == "reviews_per_month" and value < 0)
            ):
                raise ValueError("Invalid typed review value")
    pooled = {name: {a: [] for a in ALPHAS} for name in variants}
    clamps = {name: {a: 0 for a in ALPHAS} for name in variants}
    baseline_predictions = {"global_median": [], "room_median": []}
    actual, validation_rows, folds, fold_manifests = [], [], [], []
    for fold in range(3):
        valid = [r for r in development if bucket(r["geography"]["zcta"], "inner", 3) == fold]
        initial = [r for r in development if bucket(r["geography"]["zcta"], "inner", 3) != fold]
        fitting, buffer = buffer_train(initial, valid)
        base_predictions, _ = baselines(fitting, valid)
        for name, values in base_predictions.items():
            baseline_predictions[name].extend(values.tolist())
        actual.extend(target(valid).tolist())
        validation_rows.extend(valid)
        fold_manifests.append(
            {"fold": fold, "train": membership(fitting), "validation": membership(valid)}
        )
        record = {
            "fold": fold,
            "train_observations": len(fitting),
            "validation_observations": len(valid),
            "train_zctas": sorted({r["geography"]["zcta"] for r in fitting}),
            "validation_zctas": sorted({r["geography"]["zcta"] for r in valid}),
            "id_overlap": len({r["id"] for r in fitting} & {r["id"] for r in valid}),
            "buffer": buffer,
            "baselines": {n: metrics(target(valid), p) for n, p in base_predictions.items()},
            "variants": {},
        }
        for name, selected in variants.items():
            numeric = (*NUMERIC, *selected)
            record["variants"][name] = {}
            for alpha in ALPHAS:
                model = make_model(alpha, numeric).fit(
                    features(fitting, numeric), np.log1p(target(fitting))
                )
                values, clamp = prediction(model, valid, numeric)
                pooled[name][alpha].extend(values.tolist())
                clamps[name][alpha] += clamp
                record["variants"][name][str(alpha)] = {
                    **metrics(target(valid), values),
                    "negative_clamp_count": clamp,
                }
        folds.append(record)
    outcomes = {}
    for name, selected in variants.items():
        scores = {str(a): metrics(actual, pooled[name][a]) for a in ALPHAS}
        chosen = min(ALPHAS, key=lambda a: (scores[str(a)]["mae_usd"], a))
        outcomes[name] = {
            "features": {"numeric": [*NUMERIC, *selected], "categorical": list(CATEGORICAL)},
            "selected_alpha": chosen,
            "pooled_alpha_metrics": scores,
            "metrics": scores[str(chosen)],
            "negative_clamp_count": clamps[name][chosen],
            "subgroups": subgroup_metrics(validation_rows, actual, pooled[name][chosen]),
        }
    manifest = {"development": membership(development), "folds": fold_manifests}
    report = {
        "schema_version": 1,
        "experiment": "review_features_development",
        "rules_version": VERSION,
        "input_observations": len(rows),
        "cohort_observations": len(retained),
        "cohort_exclusions": exclusions,
        "development_observations": len(development),
        "outer_holdout_excluded_observations": len(held),
        "outer_buffer": outer_buffer,
        "outer_holdout_scored": False,
        "manifest_sha256": hashlib.sha256(
            json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "folds": folds,
        "variants": outcomes,
        "baselines": {
            name: {
                "metrics": metrics(actual, p),
                "subgroups": subgroup_metrics(validation_rows, actual, p),
            }
            for name, p in baseline_predictions.items()
        },
        "public_prediction_release": "withheld",
        "limitations": [
            "Selected-alpha metrics reuse tuning folds and are exploratory, not final/unbiased test estimates",
            "No automatic feature-set winner or public promotion",
            "Reviews describe established comps, not guaranteed subject-property ratings",
            "Same-snapshot associations do not establish temporal prediction or causal renovation return",
            "Review counts and unavailable dates are not occupancy or revenue",
            "Value scores may depend on perceived price",
            "Anonymized coordinates cannot guarantee physical-property separation",
            "Fresh untouched final evaluation and temporal evidence remain issue #17",
        ],
    }
    return {"report": report, "manifest": manifest}


def private_output(value):
    path = output_path(value)
    if path.exists():
        current = json.loads(path.read_text(encoding="utf-8"))
        if current.get("report", {}).get("experiment") != "review_features_development":
            raise ValueError("Cannot overwrite output owned by another experiment")
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--features")
    args = parser.parse_args()
    try:
        if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", args.snapshot):
            raise ValueError("Snapshot must be YYYY-MM-DD")
        variants = selections(args.features)
        path = private_output(args.output)
        dataset, digest = load_verified(args.snapshot)
        rows, catalog, source = enrich(
            dataset["rows"], ROOT / "data/raw" / args.snapshot, args.snapshot
        )
        result = experiment(rows, variants)
        development, _, _ = split(cohort(rows)[0])
        result["report"].update(
            catalog=catalog,
            review_coverage={
                "source": coverage(rows),
                "usable": coverage([r for r in rows if r["in_usable_cohort"]]),
                "development": coverage(development),
            },
            provenance={
                **source,
                "normalized_sha256": digest,
                "base_inputs": dataset["audit"]["provenance"],
                "sklearn_version": sklearn.__version__,
                "code_sha256": {
                    name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                    for name in (
                        "pipeline/review_experiment.py",
                        "pipeline/evaluate.py",
                        "scripts/review_features.py",
                        "pipeline/uv.lock",
                        "specs/002-review-features/contracts/experiment.md",
                    )
                },
            },
        )
        result["rows"] = rows
        atomic_write(path, result)
        print(json.dumps(result["report"], sort_keys=True, indent=2, allow_nan=False))
    except (ValueError, OSError, FloatingPointError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
