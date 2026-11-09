"""Source verification and safe replacement contracts, using tiny local fixtures."""

import csv
import gzip
import hashlib
import io

import pytest

from market_sources import (
    archive_path,
    download_archive,
    record_retrieval,
    registry,
    verify_archive,
)


def test_four_pinned_market_paths_keep_provider_areas_distinct(tmp_path):
    sources = registry()["markets"]
    assert set(sources) == {"clark-county-nv", "new-york-city", "los-angeles", "nashville"}
    paths = {market: archive_path(market, source, tmp_path) for market, source in sources.items()}
    assert len(set(paths.values())) == 4
    assert paths["clark-county-nv"].parts[-3:] == ("raw", "2026-09-20", "listings.csv.gz")


def fixture_archive(path, rows):
    text = io.StringIO(newline="")
    writer = csv.DictWriter(
        text,
        fieldnames=[
            "id",
            "last_scraped",
            "price",
            "latitude",
            "longitude",
            "room_type",
            "property_type",
            "bedrooms",
            "beds",
            "accommodates",
            "neighbourhood_cleansed",
        ],
    )
    writer.writeheader()
    writer.writerows(rows)
    with gzip.open(path, "wt", encoding="utf-8", newline="") as handle:
        handle.write(text.getvalue())
    data = path.read_bytes()
    fields = next(csv.reader(io.StringIO(text.getvalue())))
    return (
        {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(), "url": "fixture://test"},
        hashlib.sha256(",".join(fields).encode()).hexdigest(),
    )


def test_verified_fixture_and_hash_tamper(tmp_path):
    path = tmp_path / "listings.csv.gz"
    source, header = fixture_archive(
        path,
        [{"id": "9007199254740993", "room_type": "Hotel room", "price": "$100.00"}],
    )
    assert verify_archive(path, source, header)["sha256"] == source["sha256"]
    with pytest.raises(ValueError, match="header differs"):
        verify_archive(path, source, "0" * 64)
    path.write_bytes(path.read_bytes() + b"extra")
    with pytest.raises(ValueError, match="differ"):
        verify_archive(path, source, header)


def test_failed_download_preserves_previous_verified_archive(tmp_path, monkeypatch):
    path = tmp_path / "listings.csv.gz"
    source, header = fixture_archive(path, [{"id": "1", "room_type": "Hotel room"}])
    original = path.read_bytes()
    monkeypatch.setattr(
        "market_sources.urllib.request.urlopen", lambda *_args, **_kw: io.BytesIO(b"bad")
    )
    with pytest.raises(ValueError, match="differ"):
        download_archive(path, source, header)
    assert path.read_bytes() == original
    assert not path.with_suffix(".gz.part").exists()


def test_retrieval_event_is_recorded_privately_and_atomically(tmp_path):
    path = tmp_path / "listings.csv.gz"
    record_retrieval(path, {"url": "fixture://test", "retrieved_at_utc": "2026-11-09T00:00:00Z"})
    assert (tmp_path / "retrieval.json").read_text(encoding="utf-8").startswith("{")
    assert not (tmp_path / "retrieval.json.part").exists()
