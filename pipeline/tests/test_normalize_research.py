import csv
import gzip
import hashlib
import json

import pytest
from audit_sources import FEATURES
from normalize_research import SOURCE_URL, build, normalize, numeric, validate_geography
from test_research_geography import polygon, source_manifest

from ingest import clean_rows


def source_row(**overrides):
    row = dict.fromkeys(FEATURES, "")
    row.update(
        id="9223372036854775807",
        latitude="36.1",
        longitude="-115.2",
        price="$200.00",
        room_type="Private room",
        property_type="Room in hotel",
        bedrooms="0",
        beds="2",
        accommodates="4",
        minimum_nights="2",
        maximum_nights="365",
        amenities='["Wifi"]',
        neighbourhood_cleansed="Area",
    )
    row.update(overrides)
    return row


def provenance():
    return {
        "url": SOURCE_URL,
        "boundary_vintage": "2020-01-01",
        "attribution": "U.S. Census Bureau",
        "sha256": "a" * 64,
        "bytes": 10,
        "expected_features": 1,
        "retrieved_at": "2026-10-08T00:00:00Z",
    }


def fixture_inputs(tmp_path):
    raw, public = tmp_path / "raw", tmp_path / "public"
    raw.mkdir()
    public.mkdir()
    rows = [source_row(), source_row(id="2", price="", bedrooms="", property_type="Entire place")]
    with gzip.open(raw / "listings.csv.gz", "wt", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FEATURES)
        writer.writeheader()
        writer.writerows(rows)
    manifest = source_manifest(raw)
    manifest["snapshot_date"] = "2026-09-20"
    (raw / "manifest.json").write_text(json.dumps(manifest))
    listings, _ = clean_rows(rows)
    listing_path = public / "listings.json"
    listing_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "snapshot_date": "2026-09-20",
                "synthetic": False,
                "listings": listings,
            }
        )
    )
    census = public / "census.geojson"
    census.write_text(json.dumps({"type": "FeatureCollection", "features": [polygon()]}))
    meta = provenance()
    meta.update(sha256=hashlib.sha256(census.read_bytes()).hexdigest(), bytes=census.stat().st_size)
    census.with_suffix(".manifest.json").write_text(json.dumps(meta))
    geo = {
        "boundary_vintage": "2020-01-01",
        "source": meta,
        "limitations": "Approximate anonymized coordinates; no parcel or jurisdiction inference.",
        "schema_version": 1,
        "snapshot_date": "2026-09-20",
        "listing_sha256": hashlib.sha256(listing_path.read_bytes()).hexdigest(),
        "assignments": [
            {"id": rows[0]["id"], "zcta": "89146", "status": "assigned", "near_boundary": False}
        ],
    }
    (public / "geography.json").write_text(json.dumps(geo))
    return raw, public, tmp_path / "research/normalized.json"


def test_hotel_group_does_not_depend_on_room_type_and_raw_evidence_survives():
    row = normalize(source_row())
    assert row["property_group"] == "hotel_resort"
    assert row["room_type"] == "private_room"
    assert row["bedrooms"] == 0
    assert row["raw"]["id"] == "9223372036854775807"
    assert row["raw"]["bathrooms"] == ""
    assert set(row["raw"]) == set(FEATURES)


@pytest.mark.parametrize(
    "label,status",
    [
        ("", "missing"),
        ("Entire place", "unspecified"),
        ("Entire mansion hotel-ish", "unrecognized"),
    ],
)
def test_unknown_properties_do_not_use_substring_guesses(label, status):
    row = normalize(source_row(property_type=label, room_type="new label"))
    assert row["property_group"] == "unknown"
    assert row["property_status"] == status
    assert row["room_type"] == "unknown"


@pytest.mark.parametrize(
    "value,minimum,expected",
    [
        ("", 0, (None, "missing")),
        (" ", 1, (None, "missing")),
        ("NaN", 0, (None, "invalid")),
        ("inf", 0, (None, "invalid")),
        ("-1", 0, (None, "invalid")),
        ("1.5", 0, (None, "invalid")),
        ("0", 1, (None, "invalid")),
        ("0", 0, (0, "valid")),
        ("4.0", 1, (4, "valid")),
    ],
)
def test_numeric_missing_invalid_zero_and_integral_strings(value, minimum, expected):
    assert numeric(value, minimum) == expected


@pytest.mark.parametrize(
    "minimum,maximum,cohort,inconsistent",
    [
        ("27", "365", "1_27_nights", False),
        ("28", "365", "28_plus_nights", False),
        ("", "365", "unknown", False),
        ("30", "2", "unknown", True),
    ],
)
def test_stay_boundaries_and_contradictions(minimum, maximum, cohort, inconsistent):
    row = normalize(source_row(minimum_nights=minimum, maximum_nights=maximum))
    assert row["stay_cohort"] == cohort
    assert row["stay_range_inconsistent"] is inconsistent


@pytest.mark.parametrize(
    "value,status,count",
    [
        ("", "missing", None),
        ("{}", "invalid", None),
        ("[1]", "invalid", None),
        ("[", "invalid", None),
        ("[]", "valid", 0),
        ('["Wifi"]', "valid", 1),
    ],
)
def test_amenities_evidence_not_inferred_features(value, status, count):
    row = normalize(source_row(amenities=value))
    assert row["amenities_status"] == status
    assert row["amenities_count"] == count
    assert row["raw"]["amenities"] == value


def test_build_is_deterministic_retains_source_denominator_and_string_ids(tmp_path):
    raw, public, output = fixture_inputs(tmp_path)
    audit = build(raw, public, "2026-09-20", output, census_source=public / "census.geojson")
    first = output.read_bytes()
    assert (
        build(raw, public, "2026-09-20", output, census_source=public / "census.geojson") == audit
    )
    assert output.read_bytes() == first
    result = json.loads(first)
    assert audit["all_source"]["rows"] == 2
    assert audit["usable_cohort"]["rows"] == 1
    assert all(isinstance(r["id"], str) for r in result["rows"])
    assert result["rows"][0]["geography"] is None
    assert "host_name" not in first.decode()


@pytest.mark.parametrize(
    "damage",
    [
        "hash",
        "snapshot",
        "duplicate_geo",
        "missing_geo",
        "cohort",
        "source_duplicate",
        "source_checksum",
        "vintage",
        "missing_vintage",
        "source_url",
        "source_hash",
        "missing_limitations",
        "census_checksum",
        "missing_retrieval",
        "missing_source",
        "incomplete_census",
    ],
)
def test_invalid_inputs_preserve_successful_output(tmp_path, damage):
    raw, public, output = fixture_inputs(tmp_path)
    build(raw, public, "2026-09-20", output, census_source=public / "census.geojson")
    previous = output.read_bytes()
    geo_path = public / "geography.json"
    geo = json.loads(geo_path.read_text())
    if damage == "vintage":
        geo["boundary_vintage"] = "2022-01-01"
    elif damage == "missing_vintage":
        del geo["boundary_vintage"]
    elif damage == "source_url":
        geo["source"]["url"] = "https://example.invalid/unpinned"
    elif damage == "source_hash":
        geo["source"]["sha256"] = "b" * 64
    elif damage == "missing_limitations":
        del geo["limitations"]
    elif damage == "census_checksum":
        (public / "census.geojson").write_text("{}")
    elif damage == "missing_retrieval":
        del geo["source"]["retrieved_at"]
    elif damage == "missing_source":
        del geo["source"]
    elif damage == "incomplete_census":
        path = public / "census.geojson"
        path.write_text(json.dumps({"type": "FeatureCollection", "features": []}))
        geo["source"]["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        geo["source"]["bytes"] = path.stat().st_size
        path.with_suffix(".manifest.json").write_text(json.dumps(geo["source"]))
    elif damage == "hash":
        geo["listing_sha256"] = "stale"
    elif damage == "snapshot":
        geo["snapshot_date"] = "old"
    elif damage == "duplicate_geo":
        geo["assignments"] *= 2
    elif damage == "missing_geo":
        geo["assignments"] = []
    elif damage == "cohort":
        dataset = json.loads((public / "listings.json").read_text())
        dataset["listings"] = []
        (public / "listings.json").write_text(json.dumps(dataset))
    elif damage == "source_checksum":
        (raw / "listings.csv.gz").write_bytes(b"bad")
    elif damage == "source_duplicate":
        with gzip.open(raw / "listings.csv.gz", "wt", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=FEATURES)
            writer.writeheader()
            writer.writerows([source_row(), source_row()])
        manifest = source_manifest(raw)
        manifest["snapshot_date"] = "2026-09-20"
        (raw / "manifest.json").write_text(json.dumps(manifest))
    geo_path.write_text(json.dumps(geo))
    with pytest.raises(ValueError):
        build(raw, public, "2026-09-20", output, census_source=public / "census.geojson")
    assert output.read_bytes() == previous


def test_geographic_codes_status_and_booleans_are_validated():
    geo = {
        "schema_version": 1,
        "snapshot_date": "d",
        "boundary_vintage": "2020-01-01",
        "source": provenance(),
        "limitations": "Approximate",
        "listing_sha256": "h",
        "assignments": [{"id": "1", "zcta": "89146", "status": "assigned", "near_boundary": 0}],
    }
    with pytest.raises(ValueError):
        validate_geography(geo, "d", "h", [{"id": "1"}])


@pytest.mark.parametrize(
    "target",
    [
        "web/static/data/report.json",
        "data/raw/report.json",
        "data/research/2026-09-20/normalized.json",
    ],
)
def test_cli_rejects_report_overwriting_inputs_or_private_artifact(monkeypatch, target):
    import sys

    from normalize_research import ROOT, main

    monkeypatch.setattr(
        sys,
        "argv",
        ["normalize_research", "--snapshot", "2026-09-20", "--audit-report", str(ROOT / target)],
    )
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 2
