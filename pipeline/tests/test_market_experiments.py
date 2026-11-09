"""Meaningful price-model preprocessing, baseline, metric and uncertainty checks."""

import math

import joblib
import numpy as np
import pytest

from market_experiments import (
    block_bootstrap,
    features,
    final_evaluation,
    fit_predict,
    make_model,
    median_predictions,
    metrics,
    price_band,
    subgroups,
)
from market_splits import split_market


def row(identifier, price, bedrooms=None, room="entire_home_apt", group="house_like", lat=36.1):
    return {
        "market_id": "clark-county-nv",
        "snapshot_date": "2026-09-20",
        "id": str(identifier),
        "asking_price_usd": price,
        "bedrooms": bedrooms,
        "beds": 1,
        "accommodates": 2,
        "room_type": room,
        "property_group": group,
        "latitude": lat,
        "longitude": -115.2,
    }


def test_training_preprocessing_cannot_learn_held_out_values_or_categories():
    train = [row("1", 100, 1), row("2", 120, None), row("3", 200, 3)]
    held = [row("4", 1000, 999, room="hotel_room", group="hotel_resort")]
    model = make_model("ridge")
    model.fit(features(train), np.log1p([r["asking_price_usd"] for r in train]))
    transform = model.named_steps["preprocess"]
    assert transform.named_transformers_["numeric"].named_steps["impute"].statistics_[0] == 2
    assert "hotel_room" not in transform.named_transformers_["category"].categories_[0]
    assert np.isfinite(model.predict(features(held))).all()


def test_room_median_uses_training_only_and_unseen_fallback():
    train = [row("1", 100, room="private_room"), row("2", 300, room="private_room")]
    held = [row("3", 1000, room="hotel_room")]
    predictions = median_predictions(train, held)
    assert predictions["global_median"].tolist() == [200]
    assert predictions["room_median"].tolist() == [200]


def test_usd_metrics_and_fixed_price_bands():
    result = metrics([100, 300], [120, 260])
    assert result["mae_usd"] == 30
    assert result["rmse_usd"] == pytest.approx(math.sqrt(1000))
    assert result["median_absolute_error_usd"] == 30
    assert [price_band(x) for x in (99, 100, 250, 500)] == [
        "lt100",
        "100_249",
        "250_499",
        "500_plus",
    ]


def test_block_bootstrap_is_paired_deterministic_and_support_gated():
    rows = [row(i, 100, lat=35 + i * 0.05) for i in range(20)]
    actual = np.full(20, 100)
    candidate = np.full(20, 105)
    baseline = np.full(20, 110)
    first = block_bootstrap(rows, actual, candidate, baseline)
    assert first == block_bootstrap(rows, actual, candidate, baseline)
    assert first["mae_usd_95pct"] == [5, 5]
    assert first["delta_vs_room_median_usd_95pct"] == [-5, -5]
    assert block_bootstrap(rows[:2], actual[:2], candidate[:2], baseline[:2]) is None


def test_histogram_candidate_smoke_and_thin_group_suppression():
    train = [row(i, 100 + i, bedrooms=i % 4) for i in range(50)]
    held = [row("held", 200, room="hotel_room")]
    prediction, clamps = fit_predict("hist_gradient_boosting", train, held)
    assert np.isfinite(prediction).all() and prediction[0] >= 0
    assert clamps >= 0
    report = subgroups(held, np.array([200]), {"hist_gradient_boosting": prediction})
    assert report["room_type"]["supported"] == {}
    assert report["room_type"]["suppressed_observations"] == 1


def test_metrics_reject_invalid_predictions():
    with pytest.raises(ValueError, match="Invalid metric"):
        metrics([100], [-1])


def test_private_model_serialization_roundtrip(tmp_path):
    train = [row(i, 100 + i * 5, bedrooms=i % 4) for i in range(50)]
    model = make_model("ridge")
    model.fit(features(train), np.log1p([r["asking_price_usd"] for r in train]))
    candidate = row("new", 200, bedrooms=None, room="hotel_room")
    before = model.predict(features([candidate]))
    path = tmp_path / "private-model.joblib"
    joblib.dump(model, path)
    after = joblib.load(path).predict(features([candidate]))
    assert np.array_equal(before, after)


def test_final_protocol_smoke_keeps_research_predictions_withheld(monkeypatch):
    monkeypatch.setattr("market_experiments.provenance", lambda: {"fixture": True})
    markets = ("clark-county-nv", "new-york-city", "los-angeles", "nashville")
    splits = {
        market: split_market(
            [
                {**row(i, 100 + i, bedrooms=i % 4, lat=35 + i * 0.05), "market_id": market}
                for i in range(60)
            ],
            market,
            require_support=False,
        )
        for market in markets
    }
    result = final_evaluation(
        splits,
        {
            "stage": "development",
            "provenance": {"fixture": True},
            "selected_candidate_for_final": "hist_gradient_boosting",
        },
    )
    assert result["public_prediction_release"] == "withheld"
    assert set(result["within_city"]) == {"new-york-city", "los-angeles", "nashville"}
    assert set(result["leave_one_city_out_diagnostic"]) == set(markets)
