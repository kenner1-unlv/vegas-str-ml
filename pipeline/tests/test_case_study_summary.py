"""The site receives a small aggregate-only payload tied to reviewed evidence."""

import json
from pathlib import Path


def test_case_study_payload_is_aggregate_and_reconciled():
    root = Path(__file__).resolve().parents[2]
    path = root / "web/src/lib/research-summary.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert path.stat().st_size < 20_000
    assert data["schema_version"] == 1
    assert data["source_rows"] == sum(market["source_rows"] for market in data["markets"])
    assert data["priced_rows"] == sum(market["priced_rows"] for market in data["markets"])
    assert data["final_n"] == sum(market.get("final_n", 0) for market in data["markets"])
    assert data["public_prediction_release"] == "withheld"
    assert {market["id"] for market in data["markets"]} == {
        "clark-county-nv",
        "new-york-city",
        "los-angeles",
        "nashville",
    }
    assert "listing_id" not in path.read_text(encoding="utf-8")
    assert "reviewer_name" not in path.read_text(encoding="utf-8")
