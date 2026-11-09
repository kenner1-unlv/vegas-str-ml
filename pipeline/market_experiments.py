"""Baseline-first private advertised-price experiments on frozen market splits."""

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from market_splits import NEW_FINAL_MARKETS, ROOT, local_groups, spatial_block, split_market

NUMERIC = ("bedrooms", "beds", "accommodates")
CATEGORICAL = ("room_type", "property_group")
MODELS = ("ridge", "hist_gradient_boosting")
SEED = 20261108


def features(rows):
    return np.array(
        [
            [np.nan if row.get(field) is None else row[field] for field in NUMERIC]
            + [row[field] for field in CATEGORICAL]
            for row in rows
        ],
        dtype=object,
    )


def target(rows):
    values = np.array([row["asking_price_usd"] for row in rows], dtype=float)
    if not len(values) or not np.isfinite(values).all() or (values <= 0).any():
        raise ValueError("Invalid advertised-price target")
    return values


def make_model(name):
    if name not in MODELS:
        raise ValueError("Unknown predeclared candidate")
    numeric_steps = [
        ("impute", SimpleImputer(strategy="median", add_indicator=True, keep_empty_features=True))
    ]
    if name == "ridge":
        numeric_steps.append(("scale", StandardScaler()))
    transform = ColumnTransformer(
        [
            ("numeric", Pipeline(numeric_steps), list(range(len(NUMERIC)))),
            (
                "category",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                list(range(len(NUMERIC), len(NUMERIC) + len(CATEGORICAL))),
            ),
        ]
    )
    estimator = (
        Ridge(alpha=10, solver="svd")
        if name == "ridge"
        else HistGradientBoostingRegressor(
            max_iter=120,
            max_leaf_nodes=15,
            learning_rate=0.05,
            min_samples_leaf=40,
            l2_regularization=1.0,
            random_state=SEED,
        )
    )
    return Pipeline([("preprocess", transform), ("estimator", estimator)])


def fit_predict(name, training, evaluation):
    model = make_model(name)
    model.fit(features(training), np.log1p(target(training)))
    with np.errstate(over="raise", invalid="raise"):
        raw = np.expm1(model.predict(features(evaluation)))
    if not np.isfinite(raw).all():
        raise ValueError("Nonfinite model prediction")
    return np.maximum(raw, 0), int(np.sum(raw < 0))


def median_predictions(training, evaluation):
    global_median = float(np.median(target(training)))
    groups = defaultdict(list)
    for row in training:
        groups[row["room_type"]].append(row["asking_price_usd"])
    by_room = {room: float(np.median(prices)) for room, prices in groups.items()}
    return {
        "global_median": np.full(len(evaluation), global_median),
        "room_median": np.array(
            [by_room.get(row["room_type"], global_median) for row in evaluation], dtype=float
        ),
    }


def metrics(actual, prediction):
    actual, prediction = np.asarray(actual, dtype=float), np.asarray(prediction, dtype=float)
    if (
        not len(actual)
        or len(actual) != len(prediction)
        or not np.isfinite(actual).all()
        or not np.isfinite(prediction).all()
        or (actual <= 0).any()
        or (prediction < 0).any()
    ):
        raise ValueError("Invalid metric inputs")
    error = np.abs(actual - prediction)
    return {
        "n": len(actual),
        "mae_usd": float(np.mean(error)),
        "median_absolute_error_usd": float(np.median(error)),
        "rmse_usd": float(np.sqrt(np.mean((actual - prediction) ** 2))),
        "log1p_mae": float(np.mean(np.abs(np.log1p(actual) - np.log1p(prediction)))),
    }


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


def block_bootstrap(rows, actual, candidate, baseline, replicates=500, seed=SEED):
    groups = defaultdict(list)
    for index, row in enumerate(rows):
        groups[spatial_block(row)].append(index)
    if len(groups) < 10:
        return None
    blocks = [np.array(indices, dtype=int) for _, indices in sorted(groups.items())]
    actual = np.asarray(actual, dtype=float)
    candidate = np.asarray(candidate, dtype=float)
    baseline = np.asarray(baseline, dtype=float)
    rng = np.random.default_rng(seed)
    maes, deltas = [], []
    for _ in range(replicates):
        chosen = rng.integers(0, len(blocks), len(blocks))
        indices = np.concatenate([blocks[index] for index in chosen])
        candidate_mae = np.mean(np.abs(actual[indices] - candidate[indices]))
        baseline_mae = np.mean(np.abs(actual[indices] - baseline[indices]))
        maes.append(candidate_mae)
        deltas.append(candidate_mae - baseline_mae)
    return {
        "blocks": len(blocks),
        "replicates": replicates,
        "seed": seed,
        "mae_usd_95pct": np.percentile(maes, [2.5, 97.5]).tolist(),
        "delta_vs_room_median_usd_95pct": np.percentile(deltas, [2.5, 97.5]).tolist(),
    }


def subgroups(rows, actual, predictions):
    result = {}
    for field in ("market_id", "room_type", "property_group", "price_band", "geographic_block"):
        groups = defaultdict(list)
        for index, row in enumerate(rows):
            label = (
                price_band(row["asking_price_usd"])
                if field == "price_band"
                else spatial_block(row)
                if field == "geographic_block"
                else row[field]
            )
            groups[label].append(index)
        result[field] = {
            "supported": {
                label: {
                    "n": len(indices),
                    "metrics": {
                        name: metrics(actual[indices], values[indices])
                        for name, values in predictions.items()
                    },
                }
                for label, indices in sorted(groups.items())
                if len(indices) >= 20
            },
            "suppressed_groups": sum(len(indices) < 20 for indices in groups.values()),
            "suppressed_observations": sum(
                len(indices) for indices in groups.values() if len(indices) < 20
            ),
        }
    return result


def partition_predictions(training, evaluation, candidates=MODELS):
    actual = target(evaluation)
    predictions = median_predictions(training, evaluation)
    clamps = {}
    for name in candidates:
        predictions[name], clamps[name] = fit_predict(name, training, evaluation)
    return actual, predictions, clamps


def evaluate_partition(training, evaluation, candidates=MODELS):
    actual, predictions, clamps = partition_predictions(training, evaluation, candidates)
    return {
        "training_n": len(training),
        "evaluation_n": len(evaluation),
        "metrics": {name: metrics(actual, values) for name, values in predictions.items()},
        "subgroups": subgroups(evaluation, actual, predictions),
        "negative_prediction_clamps": clamps,
        "uncertainty": {
            name: block_bootstrap(evaluation, actual, predictions[name], predictions["room_median"])
            for name in candidates
        },
    }


def load_splits():
    support = json.loads(
        (ROOT / "specs/003-multi-city-research/split-support.json").read_text(encoding="utf-8")
    )
    if (
        support["split_rules_sha256"]
        != hashlib.sha256((ROOT / "pipeline/market_splits.py").read_bytes()).hexdigest()
    ):
        raise ValueError("Frozen split code differs from reviewed support audit")
    if (
        support["private_manifest_sha256"]
        != hashlib.sha256((ROOT / "data/research/multi-city/splits.json").read_bytes()).hexdigest()
    ):
        raise ValueError("Private split membership differs from reviewed support audit")
    sources = json.loads((ROOT / "specs/003-multi-city-research/source-manifest.json").read_text())
    splits = {}
    for market, source in sorted(sources["markets"].items()):
        path = (
            ROOT
            / "data/research/multi-city"
            / market
            / source["snapshot_date"]
            / "normalized.jsonl"
        )
        with path.open(encoding="utf-8") as handle:
            rows = [json.loads(line) for line in handle]
        if support["normalized_sha256"][market] != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError("Normalized rows differ from frozen split input")
        splits[market] = split_market(rows, market)
        if (
            splits[market]["audit"]["manifest_sha256"]
            != support["markets"][market]["manifest_sha256"]
        ):
            raise ValueError("Recomputed split membership differs from frozen support audit")
    return splits


def provenance():
    split_path = ROOT / "data/research/multi-city/splits.json"
    return {
        "split_manifest_sha256": hashlib.sha256(split_path.read_bytes()).hexdigest(),
        "source_manifest_sha256": hashlib.sha256(
            (ROOT / "specs/003-multi-city-research/source-manifest.json").read_bytes()
        ).hexdigest(),
        "evaluation_contract_sha256": hashlib.sha256(
            (ROOT / "specs/003-multi-city-research/contracts/evaluation.md").read_bytes()
        ).hexdigest(),
        "experiment_code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "lockfile_sha256": hashlib.sha256((ROOT / "pipeline/uv.lock").read_bytes()).hexdigest(),
        "sklearn_version": sklearn.__version__,
    }


def development(splits):
    pooled_actual = []
    pooled_predictions = {name: [] for name in ("global_median", "room_median", *MODELS)}
    fold_reports = []
    validation_rows = []
    for index in range(3):
        training = [
            row for market in sorted(splits) for row in splits[market]["inner"][index]["fitting"]
        ]
        validation = [
            row
            for market in NEW_FINAL_MARKETS
            for row in splits[market]["inner"][index]["validation"]
        ]
        actual, predictions, clamps = partition_predictions(training, validation)
        pooled_actual.extend(actual.tolist())
        validation_rows.extend(validation)
        for name, values in predictions.items():
            pooled_predictions[name].extend(values.tolist())
        fold_reports.append(
            {
                "fold": index,
                "training_n": len(training),
                "validation_n": len(validation),
                "metrics": {name: metrics(actual, values) for name, values in predictions.items()},
                "negative_prediction_clamps": clamps,
            }
        )
    actual = np.array(pooled_actual)
    predictions = {name: np.array(values) for name, values in pooled_predictions.items()}
    scores = {name: metrics(actual, values) for name, values in predictions.items()}
    selected = min(MODELS, key=lambda name: (scores[name]["mae_usd"], MODELS.index(name)))
    return {
        "stage": "development",
        "research_question": "Do nonlinear property and room interactions reduce cross-market advertised-price error?",
        "hypothesis": "Fixed histogram boosting improves development MAE over fixed Ridge",
        "feature_allowlist": {"numeric": list(NUMERIC), "categorical": list(CATEGORICAL)},
        "candidate_configurations": {
            "ridge": {"alpha": 10, "solver": "svd", "target": "log1p"},
            "hist_gradient_boosting": {
                "max_iter": 120,
                "max_leaf_nodes": 15,
                "learning_rate": 0.05,
                "min_samples_leaf": 40,
                "l2_regularization": 1.0,
                "random_state": SEED,
                "target": "log1p",
            },
        },
        "folds": fold_reports,
        "pooled_development_metrics": scores,
        "pooled_development_subgroups": subgroups(validation_rows, actual, predictions),
        "selected_candidate_for_final": selected,
        "selection_metric": "pooled geographic development USD MAE, NYC/LA/Nashville only",
        "provenance": provenance(),
        "limitations": [
            "Selected-candidate fold metrics reuse development folds and are not unbiased final estimates",
            "Clark County same-snapshot outcomes are historical, not fresh final evidence",
            "Advertised asking price is not revenue or occupancy",
        ],
    }


def final_evaluation(splits, development_report):
    current = provenance()
    if (
        development_report.get("stage") != "development"
        or development_report.get("provenance") != current
    ):
        raise ValueError("Development selection does not match frozen code, contract or inputs")
    selected = development_report["selected_candidate_for_final"]
    if selected not in MODELS:
        raise ValueError("Unknown frozen candidate")
    pooled_training = [row for market in sorted(splits) for row in splits[market]["fitting"]]
    pooled_final = [row for market in NEW_FINAL_MARKETS for row in splits[market]["final"]]
    within = {
        market: evaluate_partition(splits[market]["fitting"], splits[market]["final"])
        for market in NEW_FINAL_MARKETS
    }
    pooled = evaluate_partition(pooled_training, pooled_final)
    leave_city_out = {}
    for target_market in sorted(splits):
        training = [
            row
            for market in sorted(splits)
            if market != target_market
            for row in splits[market]["fitting"]
        ]
        leave_city_out[target_market] = evaluate_partition(
            training, splits[target_market]["eligible"], MODELS
        )
    adapted = {}
    for target_market in NEW_FINAL_MARKETS:
        other_training = [
            row
            for market in sorted(splits)
            if market != target_market
            for row in splits[market]["fitting"]
        ]
        adapted[target_market] = {
            str(budget): evaluate_partition(
                other_training + local_groups(splits[target_market]["fitting"], budget),
                splits[target_market]["final"],
                (selected,),
            )
            for budget in (0, 100, 500)
        }
    return {
        "stage": "final",
        "selected_candidate": selected,
        "provenance": current,
        "within_city": within,
        "pooled": pooled,
        "leave_one_city_out_diagnostic": leave_city_out,
        "limited_local_adaptation": adapted,
        "public_prediction_release": "withheld",
        "limitations": [
            "Clark County same-snapshot metrics are historical/development, not new independent final evidence",
            "Leave-one-city-out scores compare fixed candidates and are not a selected-model final estimate",
            "Spatial-block bootstrap intervals are not calibrated prediction intervals",
            "No temporal generalization, verified property identity, observed bookings or acquisition costs",
        ],
    }


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    part = path.with_suffix(path.suffix + ".part")
    try:
        part.write_text(
            json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n", encoding="utf-8"
        )
        part.replace(path)
    finally:
        part.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("development", "final"), required=True)
    args = parser.parse_args()
    development_path = ROOT / "specs/003-multi-city-research/development-results.json"
    final_path = ROOT / "specs/003-multi-city-research/final-evaluation.json"
    try:
        splits = load_splits()
        if args.stage == "development":
            if final_path.exists():
                raise ValueError("Final evaluation exists; refuse to replace frozen selection")
            result = development(splits)
            atomic_json(development_path, result)
        else:
            if final_path.exists():
                raise ValueError("Final evaluation already exists; refuse to rescore exposed data")
            result = final_evaluation(
                splits, json.loads(development_path.read_text(encoding="utf-8"))
            )
            atomic_json(final_path, result)
        print(
            json.dumps(
                {
                    "stage": args.stage,
                    "selected": result.get(
                        "selected_candidate_for_final", result.get("selected_candidate")
                    ),
                }
            )
        )
    except (OSError, ValueError, FloatingPointError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
