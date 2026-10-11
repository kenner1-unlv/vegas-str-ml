"""Geographic evaluation leakage and deterministic fit contracts."""

import copy
import math

import numpy as np
import pytest

from evaluate import bucket, buffer_train, cohort, evaluate, features, make_model, metrics, split


def row(identifier, zcta, lat=36.0, lon=-115.0, price=100, snapshot="2026-09-20"):
    return {
        "id": str(identifier),
        "snapshot_date": snapshot,
        "in_usable_cohort": True,
        "asking_price_usd": price,
        "property_group": "house_like",
        "room_type": "entire_home_apt",
        "stay_cohort": "1_27_nights",
        "bedrooms": 2,
        "beds": 3,
        "accommodates": 4,
        "raw": {"latitude": str(lat), "longitude": str(lon)},
        "geography": {"zcta": zcta, "status": "assigned", "near_boundary": False},
    }


def fixture():
    areas = [str(89000 + i) for i in range(100)]
    chosen = []
    for outer in range(5):
        for inner in range(3):
            chosen.append(
                next(
                    z
                    for z in areas
                    if bucket(z, "outer", 5) == outer and bucket(z, "inner", 3) == inner
                )
            )
    return [
        row(i * 30 + j, z, lat=35 + i * 0.03, price=80 + 10 * j)
        for i, z in enumerate(chosen)
        for j in range(25)
    ]


def test_split_deterministic_target_independent():
    rows = fixture()
    a = split(rows)
    edited = copy.deepcopy(rows)
    for r in edited:
        r["asking_price_usd"] *= 100
    b = split(list(reversed(edited)))
    assert [[r["id"] for r in x] for x in a[:2]] == [[r["id"] for r in x] for x in b[:2]]
    assert not {r["id"] for r in a[0]} & {r["id"] for r in a[1]}
    assert not {r["geography"]["zcta"] for r in a[0]} & {r["geography"]["zcta"] for r in a[1]}


def test_buffer_and_id_exclusion():
    held = [row(1, "89101")]
    train = [row(1, "89102", lat=37), row(2, "89102", lat=36.001), row(3, "89102", lat=36.02)]
    kept, audit = buffer_train(train, held)
    assert [r["id"] for r in kept] == ["3"]
    assert audit["id_excluded"] == 1 and audit["buffer_excluded"] == 1
    assert audit["minimum_distance_m"] > 1000


def test_repeated_ids_geographic_drift_and_duplicates():
    rows = [row(1, "89101"), row(1, "89102", snapshot="2026-10-01"), row(2, "89103")]
    kept, excluded = cohort(rows)
    assert [r["id"] for r in kept] == ["2"]
    assert excluded["geographic_id_drift"] == 2
    with pytest.raises(ValueError, match="Duplicate"):
        cohort([rows[0], rows[0]])


@pytest.mark.parametrize(
    "field,value,reason",
    [
        ("property_group", "unknown", "unsupported_property"),
        ("room_type", "unknown", "unknown_room"),
        ("stay_cohort", "unknown", "unknown_stay"),
    ],
)
def test_cohort_exclusions(field, value, reason):
    r = row(1, "89101")
    r[field] = value
    assert cohort([r])[1][reason] == 1


def test_training_only_imputation_vocabulary():
    train = [row(1, "89101"), row(2, "89101", price=120)]
    train[1]["bedrooms"] = None
    model = make_model(10).fit(features(train), np.log1p([100, 120]))
    transform = model.named_steps["preprocess"]
    assert transform.named_transformers_["numeric"].named_steps["impute"].statistics_[0] == 2
    categories = transform.named_transformers_["category"].categories_
    assert list(categories[-1]) == ["89101"]
    held = row(3, "89999")
    held["bedrooms"] = 1000
    assert math.isfinite(float(model.predict(features([held]))[0]))
    assert list(categories[-1]) == ["89101"]
    assert transform.named_transformers_["numeric"].named_steps["impute"].statistics_[0] == 2


def test_metrics_known_values():
    result = metrics([10, 20], [12, 16])
    assert result["mae_usd"] == 3 and result["median_absolute_error_usd"] == 3
    assert result["rmse_usd"] == pytest.approx(math.sqrt(10))


def test_evaluation_reproducible_reconciled_and_no_public_ids():
    rows = fixture()
    first = evaluate(rows)
    second = evaluate(list(reversed(rows)))
    assert first == second
    report = first["report"]
    assert report["input_observations"] == report["cohort_observations"] + sum(
        report["exclusions"].values()
    )
    assert report["split"]["id_overlap"] == 0
    assert set(report["metrics"]) == {"global_median", "room_median", "ridge_log1p"}
    assert "manifest" not in report
    assert not any("id" in entry for entry in report["subgroup_regressions"])
    assert first["manifest"]["train"][0]["id"].isdigit()


def test_invalid_price_and_empty_split():
    bad = row(1, "89101", price=float("nan"))
    with pytest.raises(ValueError):
        cohort([bad])
    with pytest.raises(ValueError, match="Empty"):
        split([row(1, "89101")])


def test_repeated_snapshots_stay_in_same_partition():
    rows = fixture()
    repeated = copy.deepcopy(rows[0])
    repeated["snapshot_date"] = "2026-10-01"
    train, held, _ = split(cohort(rows + [repeated])[0])
    locations = [
        name
        for name, partition in [("train", train), ("held", held)]
        if any(r["id"] == repeated["id"] for r in partition)
    ]
    assert len(locations) == 1
    partition = train if locations[0] == "train" else held
    assert sum(r["id"] == repeated["id"] for r in partition) == 2


def test_baseline_unseen_room_fallback():
    from evaluate import baselines

    train = [row(1, "89101", price=100), row(2, "89101", price=200)]
    held = row(3, "89102")
    held["room_type"] = "hotel_room"
    predictions, audit = baselines(train, [held])
    assert predictions["room_median"].tolist() == [150]
    assert audit["unseen_room_fallback_count"] == 1


def test_inner_folds_disjoint_buffered():
    result = evaluate(fixture())
    for fold in result["manifest"]["inner_folds"]:
        assert not {r["id"] for r in fold["train"]} & {r["id"] for r in fold["validation"]}
        assert not {r["zcta"] for r in fold["train"]} & {r["zcta"] for r in fold["validation"]}
    assert all(
        f["buffer"]["minimum_distance_m"] > 1000 for f in result["report"]["tuning"]["folds"]
    )
    assert result["report"]["public_prediction_release"] == "withheld"


def test_missing_numeric_fallback_and_studio():
    train = [row(1, "89101"), row(2, "89101")]
    for r in train:
        r["beds"] = None
    train[0]["bedrooms"] = 0
    model = make_model(1).fit(features(train), np.log1p([100, 120]))
    assert model.named_steps["preprocess"].named_transformers_["numeric"].named_steps[
        "impute"
    ].statistics_.tolist() == [1, 0, 4]


def test_cli_failure_preserves_previous_output(tmp_path, monkeypatch):
    import evaluate as module

    output = tmp_path / "evaluation.json"
    output.write_text("previous")
    monkeypatch.setattr(module, "output_path", lambda _: output)
    monkeypatch.setattr(
        module, "load_verified", lambda _: (_ for _ in ()).throw(ValueError("stale"))
    )
    monkeypatch.setattr(
        "sys.argv", ["evaluate", "--snapshot", "2026-09-20", "--output", str(output)]
    )
    with pytest.raises(SystemExit):
        module.main()
    assert output.read_text() == "previous"


def test_atomic_private_manifest(tmp_path):
    from evaluate import atomic_write

    path = tmp_path / "evaluation.json"
    atomic_write(path, {"report": {"n": 2}, "manifest": {"train": []}})
    import json

    assert json.loads(path.read_text())["report"]["n"] == 2
    assert not path.with_suffix(".json.part").exists()
