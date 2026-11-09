"""The committed source audit contains counts and provenance, never source rows."""

import json
from pathlib import Path


def test_public_source_audit_is_aggregate_allowlisted():
    root = Path(__file__).resolve().parents[2]
    audit = json.loads((root / "specs/003-multi-city-research/source-audit.json").read_text())
    assert set(audit) == {"schema_version", "source_manifest_sha256", "limitations", "markets"}
    allowed = {
        "snapshot_date",
        "source_area",
        "source_sha256",
        "normalized_sha256",
        "normalizer_sha256",
        "normalization_rules_version",
        "source_rows",
        "source_field_missing_counts",
        "included_rows",
        "exclusions",
        "room_types_source",
        "unknown_property_labels",
        "missing_overall_rating",
        "invalid_overall_rating",
        "selected_field_statuses",
        "asking_price_usd_included",
        "source_coordinate_extent",
        "candidate_5km_blocks",
        "candidate_5km_blocks_with_at_least_20_rows",
    }
    assert len(audit["markets"]) == 4
    for market in audit["markets"].values():
        assert set(market) == allowed
        assert all(type(value) is int for value in market["source_field_missing_counts"].values())
        assert all(type(value) is int for value in market["selected_field_statuses"].values())
        assert market["source_rows"] == market["included_rows"] + sum(market["exclusions"].values())
