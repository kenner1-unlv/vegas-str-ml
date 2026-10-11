"""Review parsing, private joins and development-only experiment contracts."""

import copy
import csv
import gzip
import hashlib
import json
import subprocess
import sys

import numpy as np
import pytest
from review_features import COUNTS, REVIEWS, SCORES, enrich, parse_review
from test_evaluation import fixture

from evaluate import bucket, features, make_model
from review_experiment import experiment, private_output, selections


@pytest.mark.parametrize(
    "field,text,value,status",
    [
        (SCORES[0], "", None, "missing"),
        (SCORES[0], "  ", None, "missing"),
        (SCORES[0], "4.98", 4.98, "valid"),
        (SCORES[0], "1", 1, "valid"),
        (SCORES[0], "5", 5, "valid"),
        (SCORES[0], "5.05", None, "invalid"),
        (SCORES[0], "0", None, "invalid"),
        (SCORES[0], "nan", None, "invalid"),
        (SCORES[0], "inf", None, "invalid"),
        (COUNTS[0], "0", 0, "valid"),
        (COUNTS[0], "2.5", None, "invalid"),
        (COUNTS[0], "-1", None, "invalid"),
        ("reviews_per_month", "1.25", 1.25, "valid"),
        ("reviews_per_month", "-0.1", None, "invalid"),
    ],
)
def test_parse(field, text, value, status):
    assert parse_review(field, text) == (value, status)


def write_source(tmp_path, rows):
    tmp_path.mkdir(exist_ok=True)
    path = tmp_path / "listings.csv.gz"
    with gzip.open(path, "wt", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["id", "host_name", *REVIEWS])
        writer.writeheader()
        writer.writerows(rows)
    (tmp_path / "manifest.json").write_text(
        json.dumps(
            {
                "snapshot_date": "2026-09-20",
                "files": {
                    "listings.csv.gz": {"sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                },
            }
        )
    )
    return path


def test_private_exact_large_id_join_catalog_and_status(tmp_path):
    identifier = "497110058117895483"
    rows = [{"id": identifier, "snapshot_date": "2026-09-20", "in_usable_cohort": True}]
    source = {f: "1" for f in REVIEWS}
    source.update(id=identifier, host_name="NEVER_OUTPUT", review_scores_communication="5.05")
    write_source(tmp_path, [source])
    enriched, catalog, provenance = enrich(rows, tmp_path, "2026-09-20")
    assert enriched[0]["id"] == identifier
    assert "host_name" not in enriched[0]["review_raw"]
    assert enriched[0]["review_status"]["review_scores_communication"] == "invalid"
    assert enriched[0]["review_scores_communication"] is None
    assert "NEVER_OUTPUT" not in json.dumps(catalog)
    assert catalog["columns"]["host_name"]["role"] == "restricted"
    assert len(catalog["columns"]) == 14
    assert catalog["columns"][SCORES[0]]["present"] == 1
    assert provenance["source_sha256"]
    assert "review_raw" not in rows[0]


@pytest.mark.parametrize("ids", [["1", "1"], ["1"], ["1", "3"], ["1", "x"]])
def test_bad_source_join_rejected(tmp_path, ids):
    base = [{"id": x, "snapshot_date": "2026-09-20"} for x in ("1", "2")]
    write_source(tmp_path, [{"id": x, **{f: "" for f in REVIEWS}} for x in ids])
    with pytest.raises(ValueError):
        enrich(base, tmp_path, "2026-09-20")


def test_stale_hash_and_missing_schema(tmp_path):
    path = write_source(tmp_path, [{"id": "1", **{f: "" for f in REVIEWS}}])
    path.write_bytes(path.read_bytes() + b"stale")
    with pytest.raises(ValueError, match="Checksum"):
        enrich([{"id": "1"}], tmp_path, "2026-09-20")


def test_missing_review_column_and_snapshot_fail(tmp_path):
    path = write_source(tmp_path, [{"id": "1", **{f: "" for f in REVIEWS}}])
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        handle.write("id,review_scores_rating\n1,5\n")
    manifest_path = tmp_path / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["files"][path.name]["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="columns"):
        enrich([{"id": "1", "snapshot_date": "2026-09-20"}], tmp_path, "2026-09-20")
    with pytest.raises(ValueError, match="snapshot"):
        enrich([], tmp_path, "2026-10-01")


def test_numeric_normalized_id_rejected(tmp_path):
    write_source(tmp_path, [{"id": "1", **{f: "" for f in REVIEWS}}])
    with pytest.raises(ValueError, match="strings"):
        enrich([{"id": 1, "snapshot_date": "2026-09-20"}], tmp_path, "2026-09-20")


def test_existing_baseline_output_cannot_be_overwritten(tmp_path, monkeypatch):
    import review_experiment as module

    path = tmp_path / "baseline.json"
    path.write_text('{"report":{"evaluation_rules_version":"1.0.0"}}')
    monkeypatch.setattr(module, "output_path", lambda _: path)
    with pytest.raises(ValueError, match="another experiment"):
        private_output(str(path))


def test_standalone_cli_imports_and_help():
    from evaluate import ROOT

    result = subprocess.run(
        [sys.executable, str(ROOT / "pipeline/review_experiment.py"), "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "--features" in result.stdout


@pytest.mark.parametrize("selection", ["", "host_id", f"{SCORES[0]},{SCORES[0]}", "price"])
def test_selection_rejects_unsupported_or_duplicate(selection):
    with pytest.raises(ValueError):
        selections(selection)


def test_selection_exact_and_canonical():
    assert selections(f"{COUNTS[0]},{SCORES[0]}") == {
        "property_only": (),
        "custom": (SCORES[0], COUNTS[0]),
    }
    assert set(selections(None)) == {
        "property_only",
        "scores_without_value",
        "counts",
        "scores_counts_without_value",
        "all_reviews",
    }


def test_optional_preprocessing_fits_only_training_and_preserves_empty():
    rows = fixture()[:3]
    for i, row in enumerate(rows):
        row[SCORES[0]] = 4 + i / 10
        row[COUNTS[0]] = None
    numeric = ("bedrooms", "beds", "accommodates", SCORES[0], COUNTS[0])
    model = make_model(10, numeric=numeric).fit(features(rows, numeric), np.log1p([100, 110, 120]))
    imputer = model.named_steps["preprocess"].named_transformers_["numeric"].named_steps["impute"]
    assert imputer.statistics_.tolist() == [2, 3, 4, 4.1, 0]
    test = copy.deepcopy(rows[0])
    test[SCORES[0]] = 1
    model.predict(features([test], numeric))
    assert imputer.statistics_[3] == 4.1


def test_development_only_target_independence_and_repeatability():
    rows = fixture()
    for i, r in enumerate(rows):
        for f in SCORES:
            r[f] = None if i % 7 == 0 else 4.5
        for f in COUNTS:
            r[f] = i % 20
        r["reviews_per_month"] = 1.5
    result = experiment(rows, selections(SCORES[0]))
    modified = copy.deepcopy(rows)
    for r in modified:
        if bucket(r["geography"]["zcta"], "outer", 5) == 0:
            r["asking_price_usd"] *= 100
            r[SCORES[0]] = 1
    assert result == experiment(list(reversed(modified)), selections(SCORES[0]))
    report = result["report"]
    assert report["outer_holdout_scored"] is False
    assert report["public_prediction_release"] == "withheld"
    assert "manifest" not in report
    for f in result["manifest"]["folds"]:
        assert not {r["id"] for r in f["train"]} & {r["id"] for r in f["validation"]}
    for f in report["folds"]:
        assert f["id_overlap"] == 0
        assert f["buffer"]["minimum_distance_m"] > 1000
    for variant in report["variants"].values():
        assert variant["metrics"]["n"] == report["development_observations"]
        assert set(variant["subgroups"]) == {"room_type", "property_group", "zcta"}


def test_cli_failure_preserves_output(tmp_path, monkeypatch):
    import review_experiment as module

    path = tmp_path / "previous.json"
    path.write_text("previous")
    monkeypatch.setattr(module, "private_output", lambda _: path)
    monkeypatch.setattr(
        module, "load_verified", lambda _: (_ for _ in ()).throw(ValueError("stale"))
    )
    monkeypatch.setattr("sys.argv", ["review", "--snapshot", "2026-09-20", "--output", str(path)])
    with pytest.raises(SystemExit):
        module.main()
    assert path.read_text() == "previous"
