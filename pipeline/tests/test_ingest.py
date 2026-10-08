import pytest

from ingest import clean_rows, price, validate_boundaries


def row(**overrides):
    return {
        "id": "9223372036854775807",
        "latitude": "36.12",
        "longitude": "-115.15",
        "price": "$1,234.50",
        "room_type": "Entire home/apt",
        "bedrooms": "2",
        "neighbourhood_cleansed": "Test",
        **overrides,
    }


@pytest.mark.parametrize(
    "value,expected",
    [
        ("$1,234.50", 1234.5),
        ("25", 25),
        ("", None),
        ("$0.00", None),
        ("NaN", None),
        ("-2", None),
        ("$1,23", None),
        ("inf", None),
    ],
)
def test_prices(value, expected):
    assert price(value) == expected


def test_ids_remain_strings_and_duplicates_excluded():
    records, quality = clean_rows([row(), row()])
    assert records[0]["id"] == "9223372036854775807"
    assert quality["counts"]["duplicate_ids"] == 1
    assert len(records) == 1
    assert "host_id" not in records[0]


def test_coordinate_and_price_exclusions_are_reported():
    records, quality = clean_rows(
        [
            row(id="1", latitude="NaN"),
            row(id="2", longitude="-110"),
            row(id="3", price=""),
            row(id="4", bedrooms=""),
        ]
    )
    assert [r["id"] for r in records] == ["4"]
    assert records[0]["bedrooms"] is None
    assert quality["counts"]["invalid_coordinates"] == 1
    assert quality["counts"]["outside_valley"] == 1
    assert quality["counts"]["invalid_prices"] == 1
    assert quality["missingness"]["bedrooms"] == 1


def test_bad_id_and_fractional_bedrooms():
    records, quality = clean_rows([row(id="1e9"), row(id="2", bedrooms="1.5")])
    assert records[0]["bedrooms"] is None
    assert quality["counts"]["invalid_ids"] == 1
    assert quality["counts"]["invalid_bedrooms"] == 1


def test_invalid_boundary_rejected():
    with pytest.raises(ValueError):
        validate_boundaries(
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [[[0, 0], [1, 1], [1, 0], [0, 1], [0, 0]]],
                        }
                    }
                ],
            }
        )


def test_boundary_geometry_and_privacy():
    polygon = {"type": "Polygon", "coordinates": [[[-115, 36], [-114, 36], [-114, 37], [-115, 36]]]}
    result = validate_boundaries(
        {
            "type": "FeatureCollection",
            "features": [
                {"geometry": polygon, "properties": {"neighbourhood": "Test", "owner": "private"}}
            ],
        }
    )
    assert result["features"][0]["properties"] == {"neighborhood": "Test"}


def test_missing_schema_fails_before_publication(tmp_path):
    import gzip

    from ingest import process

    raw = tmp_path / "raw"
    raw.mkdir()
    with gzip.open(raw / "listings.csv.gz", "wt") as handle:
        handle.write("id,price\n1,20\n")
    output = tmp_path / "published" / "2026-09-20"
    with pytest.raises(ValueError, match="Missing essential"):
        process(raw, output, "2026-09-20", {})
    assert not output.exists()


def test_bad_boundaries_preserve_previous_outputs(tmp_path):
    import csv
    import gzip
    import json

    from ingest import process

    raw = tmp_path / "raw"
    raw.mkdir()
    with gzip.open(raw / "listings.csv.gz", "wt", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row()))
        writer.writeheader()
        writer.writerow(row())
    (raw / "neighbourhoods.geojson").write_text(
        json.dumps({"type": "FeatureCollection", "features": []})
    )
    output = tmp_path / "published" / "2026-09-20"
    output.mkdir(parents=True)
    previous = output / "listings.json"
    previous.write_text("previous validated release")
    with pytest.raises(ValueError, match="nonempty"):
        process(raw, output, "2026-09-20", {})
    assert previous.read_text() == "previous validated release"
