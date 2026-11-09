"""Private development-only market-relative asking-price classification."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix, f1_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from market_experiments import (
    CATEGORICAL,
    NUMERIC,
    atomic_json,
    features,
    load_splits,
    provenance,
    target,
)
from market_splits import NEW_FINAL_MARKETS, ROOT

SEED = 20261108
METHODS = ("majority", "logistic", "random_forest")


def threshold_labels(fitting, validation):
    threshold = float(np.median(target(fitting)))
    y_fit = (target(fitting) >= threshold).astype(int)
    y_valid = (target(validation) >= threshold).astype(int)
    if len(set(y_fit)) != 2 or len(set(y_valid)) != 2:
        raise ValueError("Insufficient low/high class diversity")
    return threshold, y_fit, y_valid


def make_classifier(name):
    if name not in METHODS:
        raise ValueError("Unknown preregistered classifier")
    numeric = [
        ("impute", SimpleImputer(strategy="median", add_indicator=True, keep_empty_features=True))
    ]
    if name == "logistic":
        numeric.append(("scale", StandardScaler()))
    transform = ColumnTransformer(
        [
            ("numeric", Pipeline(numeric), list(range(len(NUMERIC)))),
            (
                "category",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                list(range(len(NUMERIC), len(NUMERIC) + len(CATEGORICAL))),
            ),
        ]
    )
    estimator = (
        DummyClassifier(strategy="most_frequent")
        if name == "majority"
        else LogisticRegression(max_iter=1000, class_weight="balanced", random_state=SEED)
        if name == "logistic"
        else RandomForestClassifier(
            n_estimators=100,
            max_depth=12,
            min_samples_leaf=20,
            n_jobs=1,
            random_state=SEED,
        )
    )
    return Pipeline([("preprocess", transform), ("classifier", estimator)])


def classification_metrics(actual, prediction):
    actual, prediction = np.asarray(actual), np.asarray(prediction)
    if len(actual) == 0 or len(actual) != len(prediction):
        raise ValueError("Invalid classification metric inputs")
    if not set(actual).issubset({0, 1}) or not set(prediction).issubset({0, 1}):
        raise ValueError("Expected binary low/high labels")
    return {
        "n": len(actual),
        "support": {"low": int(np.sum(actual == 0)), "high": int(np.sum(actual == 1))},
        "accuracy": float(accuracy_score(actual, prediction)),
        "balanced_accuracy": float(balanced_accuracy_score(actual, prediction)),
        "macro_f1": float(
            f1_score(actual, prediction, average="macro", labels=[0, 1], zero_division=0)
        ),
        "confusion_matrix": confusion_matrix(actual, prediction, labels=[0, 1]).tolist(),
    }


def evaluate(splits):
    result = {}
    for market in NEW_FINAL_MARKETS:
        labels, predictions = [], {name: [] for name in METHODS}
        folds = []
        for item in splits[market]["inner"]:
            fitting, validation = item["fitting"], item["validation"]
            threshold, y_fit, y_valid = threshold_labels(fitting, validation)
            fold_predictions = {}
            for name in METHODS:
                model = make_classifier(name).fit(features(fitting), y_fit)
                fold_predictions[name] = model.predict(features(validation))
                predictions[name].extend(fold_predictions[name].tolist())
            labels.extend(y_valid.tolist())
            folds.append(
                {
                    "fold": item["fold"],
                    "training_n": len(fitting),
                    "validation_n": len(validation),
                    "training_median_threshold_usd": threshold,
                    "training_support": {
                        "low": int(np.sum(y_fit == 0)),
                        "high": int(np.sum(y_fit == 1)),
                    },
                    "metrics": {
                        name: classification_metrics(y_valid, predicted)
                        for name, predicted in fold_predictions.items()
                    },
                }
            )
        result[market] = {
            "folds": folds,
            "pooled_development_metrics": {
                name: classification_metrics(labels, values) for name, values in predictions.items()
            },
            "outer_final_scored": False,
        }
    return {
        "stage": "development_only_secondary",
        "question": "Can listing characteristics identify market-relative high asking-price segments on unseen development geography?",
        "target": "Advertised asking price at or above each market/fold training median",
        "feature_allowlist": {"numeric": list(NUMERIC), "categorical": list(CATEGORICAL)},
        "methods": {
            "majority": {"strategy": "most_frequent"},
            "logistic": {"max_iter": 1000, "class_weight": "balanced", "random_state": SEED},
            "random_forest": {
                "n_estimators": 100,
                "max_depth": 12,
                "min_samples_leaf": 20,
                "n_jobs": 1,
                "random_state": SEED,
            },
        },
        "markets": result,
        "provenance": {
            **provenance(),
            "secondary_protocol_sha256": hashlib.sha256(
                (ROOT / "specs/003-multi-city-research/secondary-protocol.md").read_bytes()
            ).hexdigest(),
            "secondary_code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        },
        "public_classification_release": "withheld",
        "limitations": [
            "Development-fold metrics are exploratory and not a fresh final accuracy estimate",
            "Each threshold is a training-derived market asking-price median, not a property-value judgment",
            "Only advertised prices are labeled; unavailable nights and review counts are not bookings",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output).resolve()
    expected = (ROOT / "specs/003-multi-city-research/secondary-results.json").resolve()
    if output != expected:
        parser.error("Secondary output must be the reviewed aggregate results path")
    try:
        result = evaluate(load_splits())
        atomic_json(output, result)
        print(
            json.dumps(
                {
                    market: result["markets"][market]["pooled_development_metrics"]
                    for market in NEW_FINAL_MARKETS
                },
                sort_keys=True,
            )
        )
    except (OSError, ValueError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
