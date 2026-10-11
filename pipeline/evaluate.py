"""Private, reproducible geographic evaluation of advertised USD nightly price."""

import argparse
import hashlib
import json
import math
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

import numpy as np
import sklearn
from scipy.spatial import cKDTree
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from select_comps import SUPPORTED_GROUPS, load_verified, output_path

VERSION = "1.0.0"
EARTH_M = 6371008.8
BUFFER_M = 1000
ALPHAS = (1, 10, 100)
NUMERIC = ("bedrooms", "beds", "accommodates")
CATEGORICAL = ("property_group", "room_type", "stay_cohort", "zcta")


def bucket(zcta, purpose, folds):
    digest = hashlib.sha256(f"vegas-str-evaluation-v1:{purpose}:{zcta}".encode()).hexdigest()
    return int(digest, 16) % folds


def key(row):
    return row["id"], row["snapshot_date"]


def cohort(rows):
    seen, areas = set(), defaultdict(set)
    for row in rows:
        if not isinstance(row.get("id"), str) or not re.fullmatch(r"[0-9]+", row["id"]):
            raise ValueError("IDs must be digit strings")
        date.fromisoformat(row["snapshot_date"])
        if key(row) in seen:
            raise ValueError("Duplicate ID/snapshot")
        seen.add(key(row))
        if type(row.get("in_usable_cohort")) is not bool:
            raise ValueError("Invalid cohort flag")
        geo = row.get("geography")
        if geo and geo.get("status") == "assigned":
            if not isinstance(geo.get("zcta"), str) or not re.fullmatch(r"[0-9]{5}", geo["zcta"]):
                raise ValueError("Invalid ZCTA")
            areas[row["id"]].add(geo["zcta"])
        for field in NUMERIC:
            value = row.get(field)
            if value is not None and (
                type(value) is not int or value < (1 if field == "accommodates" else 0)
            ):
                raise ValueError("Invalid numeric feature")
        if row["in_usable_cohort"]:
            value = row.get("asking_price_usd")
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
                or value <= 0
            ):
                raise ValueError("Invalid asking price")
    kept, excluded = [], Counter()
    for row in sorted(rows, key=key):
        geo = row.get("geography")
        reason = None
        if len(areas[row["id"]]) > 1:
            reason = "geographic_id_drift"
        elif not row["in_usable_cohort"]:
            reason = "outside_usable_cohort"
        elif row["property_group"] not in SUPPORTED_GROUPS:
            reason = "unsupported_property"
        elif row["room_type"] not in {
            "entire_home_apt",
            "private_room",
            "shared_room",
            "hotel_room",
        }:
            reason = "unknown_room"
        elif row["stay_cohort"] not in {"1_27_nights", "28_plus_nights"}:
            reason = "unknown_stay"
        elif not geo or geo["status"] != "assigned":
            reason = "unknown_geography"
        elif type(geo.get("near_boundary")) is not bool:
            raise ValueError("Invalid boundary flag")
        elif geo["near_boundary"]:
            reason = "near_boundary"
        if reason:
            excluded[reason] += 1
        else:
            coordinates(row)
            kept.append(row)
    return kept, dict(sorted(excluded.items()))


def coordinates(row):
    lat, lon = float(row["raw"]["latitude"]), float(row["raw"]["longitude"])
    if not (math.isfinite(lat) and math.isfinite(lon) and -90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError("Invalid separation coordinates")
    return lat, lon


def unit_points(rows):
    radians = np.radians([coordinates(r) for r in rows])
    lat, lon = radians[:, 0], radians[:, 1]
    return np.column_stack((np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)))


def buffer_train(train, held):
    if not train or not held:
        raise ValueError("Empty geographic partition")
    held_ids = {r["id"] for r in held}
    eligible = [r for r in train if r["id"] not in held_ids]
    if not eligible:
        raise ValueError("Empty training partition after ID exclusion")
    chord, _ = cKDTree(unit_points(held)).query(unit_points(eligible))
    distances = 2 * EARTH_M * np.arcsin(np.clip(chord / 2, 0, 1))
    kept = [r for r, d in zip(eligible, distances, strict=True) if d > BUFFER_M]
    if not kept:
        raise ValueError("Empty training partition after spatial buffer")
    return kept, {
        "id_excluded": len(train) - len(eligible),
        "buffer_excluded": len(eligible) - len(kept),
        "minimum_distance_m": float(min(d for d in distances if d > BUFFER_M)),
    }


def split(rows):
    ordered = sorted(rows, key=key)
    held = [r for r in ordered if bucket(r["geography"]["zcta"], "outer", 5) == 0]
    development = [r for r in ordered if bucket(r["geography"]["zcta"], "outer", 5) != 0]
    train, audit = buffer_train(development, held)
    return train, held, audit


def features(rows, numeric=NUMERIC):
    return np.array(
        [
            [np.nan if r.get(f) is None else r[f] for f in numeric]
            + [r[f] for f in CATEGORICAL[:-1]]
            + [r["geography"]["zcta"]]
            for r in rows
        ],
        dtype=object,
    )


def make_model(alpha, numeric=NUMERIC):
    numeric_features = tuple(numeric)
    numeric = Pipeline(
        [
            (
                "impute",
                SimpleImputer(strategy="median", add_indicator=True, keep_empty_features=True),
            ),
            ("scale", StandardScaler()),
        ]
    )
    transform = ColumnTransformer(
        [
            ("numeric", numeric, list(range(len(numeric_features)))),
            (
                "category",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                list(range(len(numeric_features), len(numeric_features) + len(CATEGORICAL))),
            ),
        ]
    )
    return Pipeline([("preprocess", transform), ("ridge", Ridge(alpha=alpha, solver="svd"))])


def target(rows):
    return np.array([r["asking_price_usd"] for r in rows], dtype=float)


def predict(model, rows):
    with np.errstate(over="raise", invalid="raise"):
        result = np.expm1(model.predict(features(rows)))
    if not np.isfinite(result).all():
        raise ValueError("Nonfinite prediction")
    return np.maximum(result, 0), int(np.sum(result < 0))


def metrics(actual, prediction):
    actual, prediction = np.array(actual), np.array(prediction)
    if (
        not len(actual)
        or not np.isfinite(actual).all()
        or not np.isfinite(prediction).all()
        or (prediction < 0).any()
    ):
        raise ValueError("Invalid metric inputs")
    error = np.abs(actual - prediction)
    return {
        "n": len(actual),
        "mae_usd": float(np.mean(error)),
        "median_absolute_error_usd": float(np.median(error)),
        "rmse_usd": float(np.sqrt(np.mean(error**2))),
        "log1p_mae": float(np.mean(np.abs(np.log1p(actual) - np.log1p(prediction)))),
    }


def baselines(train, held):
    global_median = float(np.median(target(train)))
    groups = defaultdict(list)
    for row in train:
        groups[row["room_type"]].append(row["asking_price_usd"])
    medians = {group: float(np.median(prices)) for group, prices in sorted(groups.items())}
    return {
        "global_median": np.full(len(held), global_median),
        "room_median": np.array([medians.get(r["room_type"], global_median) for r in held]),
    }, {
        "global_median_usd": global_median,
        "room_medians_usd": medians,
        "unseen_room_fallback_count": sum(r["room_type"] not in medians for r in held),
    }


def membership(rows):
    return [
        {"id": r["id"], "snapshot_date": r["snapshot_date"], "zcta": r["geography"]["zcta"]}
        for r in rows
    ]


def price_band(price):
    return (
        "lt100"
        if price < 100
        else "100_249"
        if price < 250
        else "250_499"
        if price < 500
        else "500_plus"
    )


def evaluate(rows):
    retained, exclusions = cohort(rows)
    train, held, buffer = split(retained)
    tuning, folds, candidates = [], [], {a: ([], []) for a in ALPHAS}
    for fold in range(3):
        valid = [r for r in train if bucket(r["geography"]["zcta"], "inner", 3) == fold]
        initial = [r for r in train if bucket(r["geography"]["zcta"], "inner", 3) != fold]
        fitting, audit = buffer_train(initial, valid)
        folds.append({"fold": fold, "train": membership(fitting), "validation": membership(valid)})
        record = {
            "fold": fold,
            "train_n": len(fitting),
            "validation_n": len(valid),
            "buffer": audit,
            "validation_zctas": sorted({r["geography"]["zcta"] for r in valid}),
            "candidates": {},
        }
        for alpha in ALPHAS:
            model = make_model(alpha).fit(features(fitting), np.log1p(target(fitting)))
            prediction, clamped = predict(model, valid)
            candidates[alpha][0].extend(target(valid).tolist())
            candidates[alpha][1].extend(prediction.tolist())
            record["candidates"][str(alpha)] = {
                **metrics(target(valid), prediction),
                "negative_clamp_count": clamped,
            }
        tuning.append(record)
    pooled = {str(a): metrics(*candidates[a]) for a in ALPHAS}
    chosen = min(ALPHAS, key=lambda a: (pooled[str(a)]["mae_usd"], a))
    model = make_model(chosen).fit(features(train), np.log1p(target(train)))
    predictions, baseline_audit = baselines(train, held)
    predictions["ridge_log1p"], clamp = predict(model, held)
    scores = {name: metrics(target(held), pred) for name, pred in predictions.items()}
    subgroups = {}
    for dimension in ("zcta", "property_group", "room_type", "price_band"):
        groups = defaultdict(list)
        for index, r in enumerate(held):
            label = (
                r["geography"]["zcta"]
                if dimension == "zcta"
                else price_band(r["asking_price_usd"])
                if dimension == "price_band"
                else r[dimension]
            )
            groups[label].append(index)
        subgroups[dimension] = {
            label: {
                "thin_sample": len(indices) < 20,
                "metrics": {
                    name: metrics(target(held)[indices], pred[indices])
                    for name, pred in predictions.items()
                },
            }
            for label, indices in sorted(groups.items())
        }
    candidate = scores["ridge_log1p"]
    gates = {
        "holdout_support": len(held) >= 200 and len(subgroups["zcta"]) >= 5,
        "mae_improvement": all(
            candidate["mae_usd"] <= 0.9 * scores[b]["mae_usd"]
            for b in ("global_median", "room_median")
        ),
        "rmse_non_regression": all(
            candidate["rmse_usd"] <= scores[b]["rmse_usd"] for b in ("global_median", "room_median")
        ),
    }
    regressions = []
    for dimension in ("zcta", "property_group", "room_type"):
        for label, result in subgroups[dimension].items():
            if (
                not result["thin_sample"]
                and result["metrics"]["ridge_log1p"]["mae_usd"]
                > 1.1 * result["metrics"]["room_median"]["mae_usd"]
            ):
                regressions.append({"dimension": dimension, "group": label})
    gates["supported_subgroup_non_regression"] = not regressions
    manifest = {"train": membership(train), "holdout": membership(held), "inner_folds": folds}
    manifest_hash = hashlib.sha256(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    transform = model.named_steps["preprocess"]
    categories = transform.named_transformers_["category"].categories_
    report = {
        "schema_version": 1,
        "evaluation_rules_version": VERSION,
        "input_observations": len(rows),
        "snapshot_dates": sorted({r["snapshot_date"] for r in rows}),
        "cohort_observations": len(retained),
        "cohort_unique_listings": len({r["id"] for r in retained}),
        "exclusions": exclusions,
        "split": {
            "train_observations": len(train),
            "holdout_observations": len(held),
            "train_unique_listings": len({r["id"] for r in train}),
            "holdout_unique_listings": len({r["id"] for r in held}),
            "train_zctas": sorted({r["geography"]["zcta"] for r in train}),
            "holdout_zctas": sorted(subgroups["zcta"]),
            "id_overlap": len({r["id"] for r in train} & {r["id"] for r in held}),
            "buffer": buffer,
            "manifest_sha256": manifest_hash,
        },
        "feature_allowlist": {"numeric": list(NUMERIC), "categorical": list(CATEGORICAL)},
        "tuning": {
            "alphas": list(ALPHAS),
            "folds": tuning,
            "pooled_metrics": pooled,
            "selected_alpha": chosen,
        },
        "training_preprocessing": {
            "numeric_medians": transform.named_transformers_["numeric"]
            .named_steps["impute"]
            .statistics_.tolist(),
            "categories": {
                field: values.tolist()
                for field, values in zip(CATEGORICAL, categories, strict=True)
            },
            "unseen_holdout_zcta_count": len(held),
        },
        "baseline_training": baseline_audit,
        "metrics": scores,
        "negative_prediction_clamp_count": clamp,
        "subgroups": subgroups,
        "review_gates": gates,
        "subgroup_regressions": regressions,
        "public_prediction_release": "withheld",
        "limitations": [
            "Advertised price, not revenue or occupancy",
            "One snapshot does not establish temporal generalization",
            "Anonymized point buffers cannot guarantee actual property separation",
            "Different IDs may describe related physical units",
            "Unseen areas have no learned area-specific effect",
            "No calibrated prediction intervals or public prediction contract",
        ],
    }
    return {"report": report, "manifest": manifest}


def atomic_write(path, result):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".json.part")
    try:
        temporary.write_text(
            json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n", encoding="utf-8"
        )
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", args.snapshot):
            raise ValueError("Snapshot must be YYYY-MM-DD")
        path = output_path(args.output)
        dataset, digest = load_verified(args.snapshot)
        result = evaluate(dataset["rows"])
        result["report"]["provenance"] = {
            "normalized_sha256": digest,
            "inputs": dataset["audit"]["provenance"],
            "evaluation_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "contract_sha256": hashlib.sha256(
                (ROOT / "specs/001-comparable-price-baseline/contracts/evaluation.md").read_bytes()
            ).hexdigest(),
            "lockfile_sha256": hashlib.sha256((ROOT / "pipeline/uv.lock").read_bytes()).hexdigest(),
            "sklearn_version": sklearn.__version__,
        }
        atomic_write(path, result)
        print(json.dumps(result["report"], sort_keys=True, indent=2, allow_nan=False))
    except (ValueError, OSError, FloatingPointError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
