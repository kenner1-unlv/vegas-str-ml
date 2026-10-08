"""Assign approximate listing coordinates to pinned Census 2020 ZCTAs."""

import argparse
import hashlib
import json
import math
import re
import urllib.request
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from shapely.affinity import scale
from shapely.geometry import Point, mapping, shape
from shapely.strtree import STRtree

ROOT = Path(__file__).resolve().parents[1]
SOURCE_URL = (
    "https://tigerweb.geo.census.gov/arcgis/rest/services/Census2020/"
    "PUMA_TAD_TAZ_UGA_ZCTA/MapServer/2/query?where=1%3D1"
    "&geometry=-115.5%2C35.8%2C-114.8%2C36.5&geometryType=esriGeometryEnvelope"
    "&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=ZCTA5&outSR=4326&f=geojson"
)


def download_source(destination):
    request = urllib.request.Request(
        SOURCE_URL, headers={"User-Agent": "vegas-str-ml/0.1"}
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        body = response.read()
    count_url = SOURCE_URL.replace("&f=geojson", "&returnCountOnly=true&f=json")
    with urllib.request.urlopen(count_url, timeout=60) as response:
        expected = json.load(response)["count"]
    collection = json.loads(body)
    assign([], collection)
    if len(collection["features"]) != expected:
        raise ValueError("Incomplete Census boundary response")
    manifest = {
        "url": SOURCE_URL,
        "retrieved_at": datetime.now(UTC).isoformat(),
        "sha256": hashlib.sha256(body).hexdigest(),
        "bytes": len(body),
        "expected_features": expected,
        "attribution": "U.S. Census Bureau",
        "boundary_vintage": "2020-01-01",
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(body)
    destination.with_suffix(".manifest.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )


def assign(listings, collection):
    if collection.get("type") != "FeatureCollection" or not collection.get("features"):
        raise ValueError("Expected nonempty ZCTA FeatureCollection")
    areas, codes, features = [], [], []
    for feature in collection["features"]:
        code = feature.get("properties", {}).get("ZCTA5")
        area = shape(feature["geometry"])
        if (
            not isinstance(code, str)
            or not re.fullmatch(r"[0-9]{5}", code)
            or code in codes
        ):
            raise ValueError("Invalid or duplicate ZCTA code")
        if (
            area.geom_type not in ("Polygon", "MultiPolygon")
            or area.is_empty
            or not area.is_valid
        ):
            raise ValueError("Invalid ZCTA polygon")
        west, south, east, north = area.bounds
        if not (-180 <= west <= east <= 180 and -90 <= south <= north <= 90):
            raise ValueError("ZCTA outside WGS84")
        areas.append(area)
        codes.append(code)
        features.append(
            {
                "type": "Feature",
                "geometry": mapping(area.simplify(0.00001, preserve_topology=True)),
                "properties": {"zcta": code},
            }
        )
    # Regional equirectangular approximation, for sensitivity only, not surveyed distance.
    lon_scale = 111320 * math.cos(math.radians(36.15))

    edges = [
        scale(area.boundary, xfact=lon_scale, yfact=111320, origin=(0, 0))
        for area in areas
    ]
    tree = STRtree(areas)
    assignments = []
    for row in listings:
        point = Point(row["longitude"], row["latitude"])
        matches = [
            int(index) for index in tree.query(point) if areas[int(index)].covers(point)
        ]
        # Shared edges or overlapping polygons stay ambiguous; do not pick an arbitrary area.
        status = (
            "assigned"
            if len(matches) == 1
            else "ambiguous"
            if matches
            else "unassigned"
        )
        assignments.append(
            {
                "id": row["id"],
                "zcta": codes[matches[0]] if len(matches) == 1 else None,
                "status": status,
                "near_boundary": any(
                    edges[index].distance(Point(point.x * lon_scale, point.y * 111320))
                    <= 150
                    for index in matches
                ),
            }
        )
    return assignments, {"type": "FeatureCollection", "features": features}


def build(snapshot, source, source_manifest):
    output = ROOT / "web/static/data" / snapshot
    listing_path = output / "listings.json"
    listing_bytes = listing_path.read_bytes()
    dataset = json.loads(listing_bytes)
    if dataset["snapshot_date"] != snapshot:
        raise ValueError("Snapshot mismatch")
    if source_manifest["boundary_vintage"] != "2020-01-01":
        raise ValueError("Unsupported boundary vintage")
    source_bytes = source.read_bytes()
    if hashlib.sha256(source_bytes).hexdigest() != source_manifest["sha256"]:
        raise ValueError("ZCTA source checksum mismatch")
    collection = json.loads(source_bytes)
    if len(collection["features"]) != source_manifest["expected_features"]:
        raise ValueError("Incomplete Census boundary response")
    assignments, boundaries = assign(dataset["listings"], collection)
    report = {
        "schema_version": 1,
        "snapshot_date": snapshot,
        "boundary_vintage": "2020-01-01",
        "listing_sha256": hashlib.sha256(listing_bytes).hexdigest(),
        "source": source_manifest,
        "counts": dict(Counter(row["status"] for row in assignments)),
        "represented_zctas": len({row["zcta"] for row in assignments if row["zcta"]}),
        "near_boundary_count": sum(row["near_boundary"] for row in assignments),
        "boundary_sensitivity_meters": 150,
        "display_boundary_simplification_degrees": 0.00001,
        "distance_method": "Regional equirectangular approximation at latitude 36.15; sensitivity flag only, not a confidence interval",
        "assignments": assignments,
        "limitations": "ZCTAs approximate ZIP areas, not named neighborhoods or jurisdictions. "
        "Assignments use anonymized listing coordinates, not verified property ZIPs. "
        "Boundary-near assignments may be wrong; no parcel match or legal inference.",
    }
    index_path = output.parent / "index.json"
    index = json.loads(index_path.read_text())
    if index["path"] != snapshot:
        raise ValueError("Build geography only for the active snapshot")
    for name, value in [
        ("geography.json", report),
        ("zcta-boundaries.geojson", boundaries),
    ]:
        (output / name).write_text(
            json.dumps(value, separators=(",", ":"), allow_nan=False), encoding="utf-8"
        )
    index["geography"] = True
    index_path.write_text(json.dumps(index, separators=(",", ":")), encoding="utf-8")
    print(
        json.dumps(
            {
                key: report[key]
                for key in ("counts", "represented_zctas", "near_boundary_count")
            },
            indent=2,
        )
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", required=True)
    parser.add_argument(
        "--source", type=Path, default=ROOT / "data/raw/geography/zcta2020.geojson"
    )
    parser.add_argument(
        "--download",
        action="store_true",
        help="Retrieve pinned Census source and validate complete query response",
    )
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", args.snapshot):
        parser.error("Expected YYYY-MM-DD snapshot")
    if args.download:
        download_source(args.source)
    manifest = json.loads(args.source.with_suffix(".manifest.json").read_text())
    build(args.snapshot, args.source, manifest)


if __name__ == "__main__":
    main()
