"""Market-relative classification target and development-only protocol checks."""

import numpy as np

from market_secondary import classification_metrics, make_classifier, threshold_labels


def row(identifier, price, room="entire_home_apt", bedrooms=None):
    return {
        "market_id": "nashville",
        "snapshot_date": "2026-09-19",
        "id": str(identifier),
        "asking_price_usd": price,
        "bedrooms": bedrooms,
        "beds": 1,
        "accommodates": 2,
        "room_type": room,
        "property_group": "house_like",
        "latitude": 36.1,
        "longitude": -86.8,
    }


def test_validation_target_uses_only_fitting_market_median():
    fitting = [row("1", 100), row("2", 200), row("3", 300)]
    validation = [row("4", 1000), row("5", 150)]
    threshold, y_fit, y_valid = threshold_labels(fitting, validation)
    assert threshold == 200
    assert y_fit.tolist() == [0, 1, 1]
    assert y_valid.tolist() == [1, 0]


def test_classifiers_handle_missing_numeric_and_unseen_room():
    fitting = [row(i, 100 + i * 10, bedrooms=i % 3) for i in range(60)]
    fitting[0]["bedrooms"] = None
    evaluation = [row("new", 200, room="hotel_room", bedrooms=None)]
    labels = np.array([i % 2 for i in range(60)])
    for name in ("logistic", "random_forest"):
        model = make_classifier(name)
        from market_experiments import features

        model.fit(features(fitting), labels)
        assert model.predict(features(evaluation)).shape == (1,)


def test_classification_metrics_have_explicit_class_support():
    result = classification_metrics([0, 0, 1, 1], [0, 1, 1, 1])
    assert result["accuracy"] == 0.75
    assert result["confusion_matrix"] == [[1, 1], [0, 2]]
    assert result["support"] == {"low": 2, "high": 2}
