import csv
import gzip
import hashlib
import json

import pytest
from audit_sources import FEATURES, audit_file, build_research
from build_geography import assign


def polygon(code="89146", left=-115.3, right=-115.2):
    return {
        "type": "Feature",
        "properties": {"ZCTA5": code, "discard": "not public"},
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [left, 36],
                    [right, 36],
                    [right, 36.2],
                    [left, 36.2],
                    [left, 36],
                ]
            ],
        },
    }


def test_zcta_assignments_keep_large_ids_and_unmatched_records():
    rows = [
        {"id": "9223372036854775807", "longitude": -115.25, "latitude": 36.1},
        {"id": "2", "longitude": -115.4, "latitude": 36.1},
    ]
    assignments, boundaries = assign(rows, {"type": "FeatureCollection", "features": [polygon()]})
    assert assignments == [
        {
            "id": "9223372036854775807",
            "zcta": "89146",
            "status": "assigned",
            "near_boundary": False,
        },
        {"id": "2", "zcta": None, "status": "unassigned", "near_boundary": False},
    ]
    assert boundaries["features"][0]["properties"] == {"zcta": "89146"}


def test_shared_edge_is_ambiguous_not_arbitrary_assignment():
    assignments, _ = assign(
        [{"id": "1", "longitude": -115.2, "latitude": 36.1}],
        {
            "type": "FeatureCollection",
            "features": [
                polygon(),
                polygon("89102", -115.2, -115.1),
            ],
        },
    )
    assert assignments[0] == {"id": "1", "zcta": None, "status": "ambiguous", "near_boundary": True}


def test_hole_is_not_assigned():
    feature = polygon()
    feature["geometry"]["coordinates"].append(
        [
            [-115.28, 36.05],
            [-115.28, 36.15],
            [-115.22, 36.15],
            [-115.22, 36.05],
            [-115.28, 36.05],
        ]
    )
    assignments, _ = assign(
        [{"id": "1", "longitude": -115.25, "latitude": 36.1}],
        {"type": "FeatureCollection", "features": [feature]},
    )
    assert assignments[0]["status"] == "unassigned"


@pytest.mark.parametrize("features", [[polygon("bad")], [polygon(), polygon()]])
def test_invalid_zcta_codes_fail(features):
    with pytest.raises(ValueError):
        assign([], {"type": "FeatureCollection", "features": features})


def test_private_research_excludes_personal_fields_and_preserves_missing(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    source = raw / "listings.csv.gz"
    row = dict.fromkeys(FEATURES, "")
    row.update(id="9223372036854775807", price="$250.00", host_name="private")
    with gzip.open(source, "wt", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row))
        writer.writeheader()
        writer.writerow(row)
    (raw / "manifest.json").write_text(
        json.dumps(
            {
                "files": {
                    "listings.csv.gz": {"sha256": hashlib.sha256(source.read_bytes()).hexdigest()},
                }
            }
        )
    )
    output = tmp_path / "research"
    report = build_research(raw, output)
    with (output / "listing-features.csv").open(newline="") as handle:
        result = next(iter(csv.DictReader(handle)))
    assert result["id"] == row["id"]
    assert result["beds"] == ""
    assert "host_name" not in result
    assert report["listings.csv.gz"]["rows"] == 1
    assert report["listings.csv.gz"]["missing"]["beds"] == 1
    assert audit_file(source)["rows"] == 1


def test_boundary_sensitivity_flags_only_near_edges():
    rows = [
        {"id": "1", "longitude": -115.299, "latitude": 36.1},
        {"id": "2", "longitude": -115.25, "latitude": 36.1},
    ]
    assignments, _ = assign(rows, {"type": "FeatureCollection", "features": [polygon()]})
    assert assignments[0]["near_boundary"] is True
    assert assignments[1]["near_boundary"] is False


def test_bad_research_checksum_preserves_previous_table(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "listings.csv.gz").write_bytes(b"tampered")
    (raw / "manifest.json").write_text(
        json.dumps({"files": {"listings.csv.gz": {"sha256": "wrong"}}})
    )
    output = tmp_path / "research"
    output.mkdir()
    (output / "listing-features.csv").write_text("previous validated research")
    with pytest.raises(ValueError, match="Checksum mismatch"):
        build_research(raw, output)
    assert (output / "listing-features.csv").read_text() == "previous validated research"
