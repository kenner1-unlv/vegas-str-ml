"""Verify or deliberately download pinned Inside Airbnb detailed listings privately."""

import argparse
import csv
import gzip
import hashlib
import json
import shutil
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "specs/003-multi-city-research/source-manifest.json"
REQUIRED = {
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
}


def registry(path=SPEC):
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if value.get("schema_version") != 1 or not value.get("markets"):
        raise ValueError("Invalid market source registry")
    return value


def archive_path(market, source, root=ROOT):
    if market == "clark-county-nv":
        return Path(root) / "data/raw" / source["snapshot_date"] / "listings.csv.gz"
    return Path(root) / "data/raw/multi-city" / market / source["snapshot_date"] / "listings.csv.gz"


def digest(path):
    with Path(path).open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def verify_archive(path, source, header_sha256):
    path = Path(path)
    if path.stat().st_size != source["bytes"] or digest(path) != source["sha256"]:
        raise ValueError("Source bytes or SHA-256 differ from pinned manifest")
    try:
        with gzip.open(path, "rt", encoding="utf-8-sig", newline="") as handle:
            fields = next(csv.reader(handle))
    except (OSError, UnicodeError, StopIteration) as exc:
        raise ValueError("Source is not a readable detailed-listings gzip CSV") from exc
    if len(fields) != len(set(fields)) or not REQUIRED.issubset(fields):
        raise ValueError("Source header is missing or duplicates required fields")
    header_digest = hashlib.sha256(",".join(fields).encode()).hexdigest()
    if header_digest != header_sha256:
        raise ValueError("Source header differs from pinned manifest")
    return {
        "bytes": path.stat().st_size,
        "sha256": source["sha256"],
        "header_sha256": header_digest,
    }


def download_archive(path, source, header_sha256):
    """Replace only after complete download and verification; never called implicitly."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    part = path.with_suffix(".gz.part")
    request = urllib.request.Request(
        source["url"], headers={"User-Agent": "vegas-str-ml-research/0.1"}
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response, part.open("wb") as out:
            shutil.copyfileobj(response, out)
        verified = verify_archive(part, source, header_sha256)
        retrieved_at = datetime.now(UTC).isoformat()
        part.replace(path)
        return {**verified, "retrieved_at_utc": retrieved_at, "url": source["url"]}
    finally:
        part.unlink(missing_ok=True)


def record_retrieval(path, result):
    """Keep acquisition-event metadata beside the ignored local archive."""
    destination = Path(path).with_name("retrieval.json")
    part = destination.with_suffix(".json.part")
    try:
        part.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        part.replace(destination)
    finally:
        part.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--market", choices=sorted(registry()["markets"]), required=True)
    parser.add_argument("--download", action="store_true", help="Explicit source download")
    args = parser.parse_args()
    manifest = registry()
    source = manifest["markets"][args.market]
    path = archive_path(args.market, source)
    try:
        if args.download:
            result = download_archive(path, source, manifest["header_sha256"])
            record_retrieval(path, result)
        else:
            result = verify_archive(path, source, manifest["header_sha256"])
        print(json.dumps({"market": args.market, **result}, sort_keys=True))
    except (OSError, ValueError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
