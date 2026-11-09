"""Canonical multi-market row and output-failure contracts."""

import csv
import gzip
import json

import pytest

from market_normalize import SOURCE_FIELDS, normalize_archive, normalize_row


def source_row(**changes):
    row = dict.fromkeys(SOURCE_FIELDS, "")
    row.update(
        id="9007199254740993",
        last_scraped="2026-09-15",
        price="$199.00",
        latitude="34.1",
        longitude="-118.2",
        room_type="Hotel room",
        property_type="Room in hotel",
        bedrooms="0",
        beds="1",
        accommodates="2",
        minimum_nights="1",
        maximum_nights="365",
        neighbourhood_cleansed="Area",
        number_of_reviews="0",
    )
    row.update(changes)
    return row


def write_archive(path, rows, fields=SOURCE_FIELDS):
    with gzip.open(path, "wt", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def test_row_preserves_hotel_zero_and_missing_review():
    row, reason = normalize_row(source_row(), "los-angeles", "2026-09-14")
    assert reason is None
    assert row["id"] == "9007199254740993"
    assert row["room_type"] == "hotel_room"
    assert row["property_group"] == "hotel_resort"
    assert row["bedrooms"] == 0 and row["statuses"]["bedrooms"] == "valid"
    assert row["reviews"]["number_of_reviews"] == 0
    assert row["reviews"]["review_scores_rating"] is None
    assert row["statuses"]["review_scores_rating"] == "missing"
    assert not {"host_name", "reviewer_name", "comments"} & row["raw"].keys()


def test_invalid_and_missing_target_remain_distinct():
    assert normalize_row(source_row(price=""), "nashville", "2026-09-19")[1] == "missing_price"
    assert normalize_row(source_row(price="0"), "nashville", "2026-09-19")[1] == "invalid_price"
    assert (
        normalize_row(source_row(latitude="nan"), "nashville", "2026-09-19")[1]
        == "invalid_coordinates"
    )
    assert normalize_row(source_row(id="abc"), "nashville", "2026-09-19") == (None, "invalid_id")


def test_archive_reconciles_and_keeps_prior_output_on_failure(tmp_path):
    path = tmp_path / "listings.csv.gz"
    output = tmp_path / "normalized.jsonl"
    write_archive(
        path,
        [
            source_row(),
            source_row(price="$300"),
            source_row(id="2", price=""),
            source_row(id="3", latitude="999"),
            source_row(id="bad"),
        ],
    )
    audit = normalize_archive(path, "los-angeles", "2026-09-14", output)
    assert audit["source_rows"] == 5
    assert audit["included_rows"] == 1
    assert audit["first_failure_reasons"] == {
        "duplicate_id": 1,
        "invalid_coordinates": 1,
        "invalid_id": 1,
        "missing_price": 1,
    }
    rows = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 1 and rows[0]["id"] == "9007199254740993"
    before = output.read_bytes()
    write_archive(path, [source_row()], fields=["id", "price"])
    with pytest.raises(ValueError, match="header"):
        normalize_archive(path, "los-angeles", "2026-09-14", output)
    assert output.read_bytes() == before
    assert not output.with_suffix(".jsonl.part").exists()


def test_extra_source_columns_are_excluded(tmp_path):
    path = tmp_path / "listings.csv.gz"
    output = tmp_path / "normalized.jsonl"
    write_archive(path, [source_row()])
    with gzip.open(path, "at", encoding="utf-8", newline="") as handle:
        csv.writer(handle).writerow([source_row()[field] for field in SOURCE_FIELDS] + ["extra"])
    audit = normalize_archive(path, "nashville", "2026-09-19", output)
    assert audit["source_rows"] == 2
    assert audit["first_failure_reasons"]["malformed_row"] == 1
