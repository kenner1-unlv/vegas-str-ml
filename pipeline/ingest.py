"""Versioned Clark County source ingestion; no host/reviewer data in public outputs."""

import argparse
import csv
import gzip
import hashlib
import json
import math
import re
import shutil
import tempfile
import urllib.request
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from shapely.geometry import mapping, shape

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PAGE = "https://insideairbnb.com/get-the-data/"
REQUIRED = {
    "id",
    "latitude",
    "longitude",
    "price",
    "room_type",
    "bedrooms",
    "neighbourhood_cleansed",
}
VALLEY = (-115.5, 35.8, -114.8, 36.5)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, separators=(",", ":"), allow_nan=False), encoding="utf-8")


def number(value):
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except (ValueError, TypeError):
        return None


def price(value):
    if not re.fullmatch(r"\$?(?:\d+|\d{1,3}(?:,\d{3})+)(?:\.\d{1,2})?", value or ""):
        return None
    result = number(value.replace("$", "").replace(",", ""))
    return result if result and result > 0 else None


def clean_rows(rows):
    counts = Counter(
        {
            key: 0
            for key in (
                "input_rows",
                "duplicate_ids",
                "invalid_ids",
                "invalid_prices",
                "invalid_coordinates",
                "outside_valley",
                "invalid_bedrooms",
            )
        }
    )
    missing = Counter()
    output = []
    seen = set()
    for row in rows:
        counts["input_rows"] += 1
        for key in REQUIRED:
            if not row.get(key):
                missing[key] += 1
        identifier = row.get("id", "")
        if not re.fullmatch(r"[0-9]+", identifier):
            counts["invalid_ids"] += 1
            continue
        if identifier in seen:
            counts["duplicate_ids"] += 1
            continue
        seen.add(identifier)
        lat, lon = number(row.get("latitude")), number(row.get("longitude"))
        nightly = price(row.get("price", ""))
        if nightly is None:
            counts["invalid_prices"] += 1
        if lat is None or lon is None or not (-90 <= lat <= 90 and -180 <= lon <= 180):
            counts["invalid_coordinates"] += 1
            continue
        if not (VALLEY[0] <= lon <= VALLEY[2] and VALLEY[1] <= lat <= VALLEY[3]):
            counts["outside_valley"] += 1
            continue
        if nightly is None:
            continue
        bedrooms = number(row.get("bedrooms"))
        if bedrooms is not None and (bedrooms < 0 or not bedrooms.is_integer()):
            counts["invalid_bedrooms"] += 1
            bedrooms = None
        output.append(
            {
                "id": identifier,
                "latitude": round(lat, 5),
                "longitude": round(lon, 5),
                "price": nightly,
                "room_type": row.get("room_type") or "Unknown",
                "bedrooms": int(bedrooms) if bedrooms is not None else None,
                "neighborhood": row.get("neighbourhood_cleansed") or "Unknown",
            }
        )
    counts["included_rows"] = len(output)
    counts["excluded_rows"] = counts["input_rows"] - len(output)
    return output, {
        "counts": dict(counts),
        "missingness": {k: missing[k] for k in sorted(REQUIRED)},
    }


def validate_boundaries(collection):
    if collection.get("type") != "FeatureCollection" or not collection.get("features"):
        raise ValueError("Expected nonempty boundary FeatureCollection")
    features = []
    for feature in collection["features"]:
        geometry = shape(feature["geometry"])
        if (
            geometry.geom_type not in ("Polygon", "MultiPolygon")
            or geometry.is_empty
            or not geometry.is_valid
        ):
            raise ValueError("Invalid polygon boundary")
        west, south, east, north = geometry.bounds
        if not (-180 <= west <= east <= 180 and -90 <= south <= north <= 90):
            raise ValueError("Boundary outside WGS84 coordinate ranges")
        # Preserve boundary shapes and only a nonpersonal descriptive field.
        features.append(
            {
                "type": "Feature",
                "geometry": mapping(geometry),
                "properties": {
                    "neighborhood": feature.get("properties", {}).get("neighbourhood", "Unknown")
                },
            }
        )
    return {"type": "FeatureCollection", "features": features}


def discover(snapshot=None):
    request = urllib.request.Request(SOURCE_PAGE, headers={"User-Agent": "vegas-str-ml/0.1"})
    with urllib.request.urlopen(request, timeout=60) as response:
        page = response.read().decode("utf-8")
    urls = re.findall(
        r'https://data.insideairbnb.com/united-states/nv/clark-county-nv/[^"<>\s]+', page
    )
    dates = sorted({url.split("/")[6] for url in urls}, reverse=True)
    if not dates or (snapshot and snapshot not in dates):
        raise ValueError("Requested Clark County snapshot is not listed on the source page")
    chosen = snapshot or dates[0]
    return chosen, {
        (
            url.rsplit("/", 1)[1].replace(".csv", "-summary.csv")
            if "/visualisations/" in url
            and url.rsplit("/", 1)[1] in ("listings.csv", "reviews.csv")
            else url.rsplit("/", 1)[1]
        ): url
        for url in urls
        if f"/{chosen}/" in url
    }


def download(url, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp = destination.with_suffix(destination.suffix + ".part")
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "vegas-str-ml/0.1"})
        with urllib.request.urlopen(request, timeout=120) as response, temp.open("wb") as out:
            shutil.copyfileobj(response, out)
        with temp.open("rb") as handle:
            digest = hashlib.file_digest(handle, "sha256").hexdigest()
        temp.replace(destination)
    finally:
        temp.unlink(missing_ok=True)
    return {
        "url": url,
        "retrieved_at": datetime.now(UTC).isoformat(),
        "sha256": digest,
        "bytes": destination.stat().st_size,
    }


def process(raw, output, snapshot, manifest):
    with gzip.open(raw / "listings.csv.gz", "rt", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not REQUIRED.issubset(reader.fieldnames or []):
            raise ValueError(
                "Missing essential listing columns: " + str(REQUIRED - set(reader.fieldnames or []))
            )
        listings, quality = clean_rows(reader)
    boundaries = validate_boundaries(json.loads((raw / "neighbourhoods.geojson").read_text()))
    if not listings:
        raise ValueError("No usable listings; refusing to publish empty data")
    quality.update(
        {
            "snapshot_date": snapshot,
            "schema_version": 1,
            "boundary_features": len(boundaries["features"]),
            "valley_bbox": VALLEY,
            "filters": "First record per valid ID; positive asking price; finite WGS84 coordinates within Valley bbox. Unknown bedrooms retained. Counts can overlap.",
        }
    )
    dataset = {
        "schema_version": 1,
        "snapshot_date": snapshot,
        "synthetic": False,
        "source": "Inside Airbnb — Clark County, NV",
        "license": "CC BY 4.0",
        "source_url": SOURCE_PAGE,
        "listings": listings,
    }
    # Validate everything before publishing. Versioned snapshot path, small pointer updated last.
    with tempfile.TemporaryDirectory(dir=output.parent) as temporary:
        stage = Path(temporary)
        for name, value in [
            ("listings.json", dataset),
            ("boundaries.geojson", boundaries),
            ("quality.json", quality),
            ("manifest.json", manifest),
        ]:
            write_json(stage / name, value)
        output.mkdir(parents=True, exist_ok=True)
        for artifact in stage.iterdir():
            shutil.copyfile(artifact, output / artifact.name)
    write_json(
        output.parent / "index.json",
        {"schema_version": 1, "snapshot_date": snapshot, "path": snapshot},
    )
    print(json.dumps(quality, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Download all seven supplied source files for private research",
    )
    parser.add_argument("--calendar", action="store_true")
    parser.add_argument("--reviews", action="store_true")
    parser.add_argument(
        "--offline", action="store_true", help="Reprocess existing raw data and manifest"
    )
    args = parser.parse_args()
    if args.offline and not args.snapshot:
        parser.error("--offline requires --snapshot")
    snapshot, urls = (args.snapshot, {}) if args.offline else discover(args.snapshot)
    raw = ROOT / "data" / "raw" / snapshot
    manifest_path = raw / "manifest.json"
    if args.offline:
        manifest = json.loads(manifest_path.read_text())
        for name, entry in manifest["files"].items():
            with (raw / name).open("rb") as handle:
                if hashlib.file_digest(handle, "sha256").hexdigest() != entry["sha256"]:
                    raise ValueError("Checksum mismatch: " + name)
    else:
        manifest = {
            "snapshot_date": snapshot,
            "source_page": SOURCE_PAGE,
            "attribution": "Inside Airbnb",
            "license": "CC BY 4.0",
            "license_url": "https://creativecommons.org/licenses/by/4.0/",
            "files": {},
        }
        names = ["listings.csv.gz", "neighbourhoods.geojson"]
        names += [
            name
            for flag, name in [(args.calendar, "calendar.csv.gz"), (args.reviews, "reviews.csv.gz")]
            if flag
        ]
        if args.all:
            names = [
                "listings.csv.gz",
                "calendar.csv.gz",
                "reviews.csv.gz",
                "listings-summary.csv",
                "reviews-summary.csv",
                "neighbourhoods.csv",
                "neighbourhoods.geojson",
            ]
        for name in names:
            manifest["files"][name] = download(urls[name], raw / name)
            write_json(manifest_path, manifest)
    out = ROOT / "web" / "static" / "data" / snapshot
    out.parent.mkdir(parents=True, exist_ok=True)
    process(raw, out, snapshot, manifest)


if __name__ == "__main__":
    main()
