"""Committed research evidence contains aggregate metrics and no listing rows."""

import json
from pathlib import Path

FORBIDDEN_ROW_KEYS = {
    "id",
    "listing_id",
    "latitude",
    "longitude",
    "raw",
    "reviews",
    "reviewer_name",
    "host_name",
    "description",
}


def check_keys(value):
    if isinstance(value, dict):
        assert not FORBIDDEN_ROW_KEYS & value.keys()
        for nested in value.values():
            check_keys(nested)
    elif isinstance(value, list):
        for nested in value:
            check_keys(nested)


def test_public_development_and_final_evidence_excludes_source_rows():
    root = Path(__file__).resolve().parents[2] / "specs/003-multi-city-research"
    for filename, stage in (
        ("development-results.json", "development"),
        ("final-evaluation.json", "final"),
    ):
        result = json.loads((root / filename).read_text(encoding="utf-8"))
        assert result["stage"] == stage
        check_keys(result)
    assert result["public_prediction_release"] == "withheld"
