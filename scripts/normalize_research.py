"""Build a private, versioned research dataset and aggregate audit from pinned local inputs."""

import argparse
import csv
import gzip
import hashlib
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

from audit_sources import EXPECTED_FILES, FEATURES
from build_geography import SOURCE_URL

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
from ingest import clean_rows, number

RULES_VERSION = "1.0.0"
PROPERTY_GROUPS = {
    "house_like": (
        "Entire home",
        "Private room in home",
        "Shared room in home",
        "Entire villa",
        "Private room in villa",
        "Entire townhouse",
        "Private room in townhouse",
        "Entire bungalow",
        "Private room in bungalow",
        "Entire cottage",
        "Private room in cottage",
        "Entire cabin",
        "Private room in cabin",
        "Entire vacation home",
        "Private room in vacation home",
    ),
    "apartment_condo": (
        "Entire rental unit",
        "Private room in rental unit",
        "Shared room in rental unit",
        "Entire condo",
        "Private room in condo",
        "Entire loft",
    ),
    "hotel_resort": (
        "Room in hotel",
        "Shared room in hotel",
        "Room in boutique hotel",
        "Room in aparthotel",
        "Private room in resort",
        "Shared room in resort",
        "Room in resort",
        "Entire resort",
        "Entire timeshare",
    ),
    "serviced_apartment": (
        "Entire serviced apartment",
        "Private room in serviced apartment",
        "Room in serviced apartment",
    ),
    "guesthouse_suite": (
        "Entire guesthouse",
        "Private room in guesthouse",
        "Entire guest suite",
        "Private room in guest suite",
    ),
    "other": (
        "Private room in camper/rv",
        "Shared room in camper/rv",
        "Camper/RV",
        "Private room in bed and breakfast",
        "Shared room in bed and breakfast",
        "Tower",
        "Private room in farm stay",
        "Private room in castle",
        "Tiny home",
        "Private room in tiny home",
        "Barn",
        "Casa particular",
        "Private room in casa particular",
        "Holiday park",
        "Tent",
        "Ranch",
        "Shared room in hostel",
        "Dome",
    ),
}
PROPERTY_MAP = {
    label: group for group, labels in PROPERTY_GROUPS.items() for label in labels
}
UNSPECIFIED_PROPERTIES = {"Entire place", "Private room"}
ROOM_MAP = {
    "Entire home/apt": "entire_home_apt",
    "Private room": "private_room",
    "Shared room": "shared_room",
    "Hotel room": "hotel_room",
}
NUMERIC_FIELDS = {
    "bedrooms": 0,
    "beds": 0,
    "accommodates": 1,
    "minimum_nights": 1,
    "maximum_nights": 1,
}


def sha256(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def numeric(value, minimum):
    if value is None or not value.strip():
        return None, "missing"
    parsed = number(value)
    if parsed is None or parsed < minimum or not parsed.is_integer():
        return None, "invalid"
    return int(parsed), "valid"


def normalize(row):
    raw = {field: row[field] for field in FEATURES}
    property_type = raw["property_type"]
    group = PROPERTY_MAP.get(property_type, "unknown")
    property_status = (
        "known"
        if property_type in PROPERTY_MAP
        else "unspecified"
        if property_type in UNSPECIFIED_PROPERTIES
        else "missing"
        if not property_type
        else "unrecognized"
    )
    values, statuses = {}, {}
    for field, minimum in NUMERIC_FIELDS.items():
        values[field], statuses[field] = numeric(raw[field], minimum)
    low, high = values["minimum_nights"], values["maximum_nights"]
    inconsistent = low is not None and high is not None and high < low
    stay = (
        "unknown"
        if low is None or inconsistent
        else "1_27_nights"
        if low < 28
        else "28_plus_nights"
    )
    try:
        amenities = json.loads(raw["amenities"])
        amenity_status = (
            "valid"
            if isinstance(amenities, list)
            and all(isinstance(x, str) for x in amenities)
            else "invalid"
        )
    except (ValueError, TypeError):
        amenities, amenity_status = (
            None,
            "missing" if not raw["amenities"] else "invalid",
        )
    return {
        "raw": raw,
        "property_group": group,
        "property_status": property_status,
        "room_type": ROOM_MAP.get(raw["room_type"], "unknown"),
        "room_status": "known"
        if raw["room_type"] in ROOM_MAP
        else "missing"
        if not raw["room_type"]
        else "unrecognized",
        **values,
        "numeric_status": statuses,
        "stay_cohort": stay,
        "stay_range_inconsistent": inconsistent,
        "amenities_status": amenity_status,
        "amenities_count": len(amenities) if amenity_status == "valid" else None,
    }


def validate_geography(geography, snapshot, listing_hash, public):
    source = geography.get("source", {})
    if not isinstance(source, dict):
        raise TypeError("Missing Census geographic provenance")
    if (
        geography.get("boundary_vintage") != "2020-01-01"
        or source.get("boundary_vintage") != "2020-01-01"
        or source.get("url") != SOURCE_URL
        or source.get("attribution") != "U.S. Census Bureau"
        or not isinstance(source.get("sha256"), str)
        or not re.fullmatch(r"[0-9a-f]{64}", source["sha256"])
        or type(source.get("bytes")) is not int
        or source["bytes"] <= 0
        or type(source.get("expected_features")) is not int
        or source["expected_features"] <= 0
        or not isinstance(geography.get("limitations"), str)
        or not geography["limitations"].strip()
    ):
        raise ValueError("Missing or unpinned Census geographic provenance")
    try:
        retrieved = datetime.fromisoformat(source["retrieved_at"])
        if retrieved.tzinfo is None:
            raise ValueError("Timestamp requires timezone")
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("Invalid Census retrieval provenance") from exc
    if (
        geography.get("schema_version") != 1
        or geography.get("snapshot_date") != snapshot
        or geography.get("listing_sha256") != listing_hash
    ):
        raise ValueError("Stale or unsupported geographic sidecar")
    assignments = geography.get("assignments", [])
    result = {}
    for row in assignments:
        identifier = row.get("id")
        code, status = row.get("zcta"), row.get("status")
        if (
            not isinstance(identifier, str)
            or identifier in result
            or status not in {"assigned", "ambiguous", "unassigned"}
            or not isinstance(row.get("near_boundary"), bool)
            or (
                status == "assigned"
                and (not isinstance(code, str) or not re.fullmatch(r"\d{5}", code))
            )
            or (status != "assigned" and code is not None)
        ):
            raise ValueError("Invalid or duplicate geographic assignment")
        result[identifier] = {
            key: row[key] for key in ("zcta", "status", "near_boundary")
        }
    if set(result) != {row["id"] for row in public}:
        raise ValueError("Geographic ID coverage mismatch")
    return result


def summarize(rows):
    return {
        "rows": len(rows),
        "property_groups": dict(
            sorted(Counter(r["property_group"] for r in rows).items())
        ),
        "property_status": dict(
            sorted(Counter(r["property_status"] for r in rows).items())
        ),
        "room_status": dict(sorted(Counter(r["room_status"] for r in rows).items())),
        "property_room_counts": [
            {"property_type": prop, "room_type": room, "rows": count}
            for (prop, room), count in sorted(
                Counter(
                    (r["raw"]["property_type"], r["raw"]["room_type"]) for r in rows
                ).items()
            )
        ],
        "numeric_status": {
            field: dict(
                sorted(Counter(r["numeric_status"][field] for r in rows).items())
            )
            for field in NUMERIC_FIELDS
        },
        "stay_cohorts": dict(sorted(Counter(r["stay_cohort"] for r in rows).items())),
        "inconsistent_stay_ranges": sum(r["stay_range_inconsistent"] for r in rows),
        "amenities_status": dict(
            sorted(Counter(r["amenities_status"] for r in rows).items())
        ),
        "empty_amenities": sum(r["amenities_count"] == 0 for r in rows),
        "bathrooms_missing": sum(not r["raw"]["bathrooms"] for r in rows),
        "bathrooms_text_missing": sum(not r["raw"]["bathrooms_text"] for r in rows),
    }


def build(raw, public_dir, snapshot, output, census_source=None):
    manifest_path = raw / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("snapshot_date") != snapshot:
        raise ValueError("Source snapshot mismatch")
    if not EXPECTED_FILES.issubset(manifest.get("files", {})):
        raise ValueError("Incomplete source manifest; run ingestion with --all")
    for name in sorted(EXPECTED_FILES):
        if sha256(raw / name) != manifest["files"][name]["sha256"]:
            raise ValueError("Checksum mismatch: " + name)
    with gzip.open(
        raw / "listings.csv.gz", "rt", encoding="utf-8-sig", newline=""
    ) as handle:
        reader = csv.DictReader(handle)
        if not set(FEATURES).issubset(reader.fieldnames or []):
            raise ValueError("Missing research columns")
        source = [{field: row[field] for field in FEATURES} for row in reader]
    identifiers = [r["id"] for r in source]
    if any(not re.fullmatch(r"[0-9]+", x) for x in identifiers) or len(
        set(identifiers)
    ) != len(identifiers):
        raise ValueError("Invalid or duplicate source IDs")
    listing_path = public_dir / "listings.json"
    dataset = json.loads(listing_path.read_text(encoding="utf-8"))
    if (
        dataset.get("schema_version") != 1
        or dataset.get("snapshot_date") != snapshot
        or dataset.get("synthetic") is not False
    ):
        raise ValueError("Unsupported or mismatched usable dataset")
    public = dataset["listings"]
    expected, quality = clean_rows(source)
    if len(public) != len(expected) or {r["id"]: r for r in public} != {
        r["id"]: r for r in expected
    }:
        raise ValueError("Usable cohort differs from source normalization")
    geography_path = public_dir / "geography.json"
    geography = json.loads(geography_path.read_text(encoding="utf-8"))
    assignments = validate_geography(geography, snapshot, sha256(listing_path), public)
    census_source = census_source or ROOT / "data/raw/geography/zcta2020.geojson"
    census_manifest = json.loads(
        census_source.with_suffix(".manifest.json").read_text(encoding="utf-8")
    )
    if (
        geography["source"] != census_manifest
        or sha256(census_source) != census_manifest["sha256"]
        or census_source.stat().st_size != census_manifest["bytes"]
    ):
        raise ValueError(
            "Geographic source differs from pinned local Census provenance"
        )
    census_collection = json.loads(census_source.read_text(encoding="utf-8"))
    if (
        census_collection.get("type") != "FeatureCollection"
        or len(census_collection.get("features", []))
        != census_manifest["expected_features"]
    ):
        raise ValueError("Incomplete pinned Census source")
    included = {r["id"]: r for r in public}
    rows = []
    for source_row in sorted(source, key=lambda r: r["id"]):
        row = normalize(source_row)
        identifier = source_row["id"]
        row.update(
            id=identifier,
            snapshot_date=snapshot,
            in_usable_cohort=identifier in included,
            asking_price_usd=included[identifier]["price"]
            if identifier in included
            else None,
            geography=assignments.get(identifier),
        )
        rows.append(row)
    audit = {
        "schema_version": 1,
        "rules_version": RULES_VERSION,
        "snapshot_date": snapshot,
        "provenance": {
            "source_manifest_sha256": sha256(manifest_path),
            "source_sha256": {
                name: manifest["files"][name]["sha256"]
                for name in sorted(EXPECTED_FILES)
            },
            "usable_listing_sha256": sha256(listing_path),
            "geography_sha256": sha256(geography_path),
            "normalizer_sha256": sha256(Path(__file__)),
            "base_ingest_sha256": sha256(ROOT / "pipeline/ingest.py"),
            "boundary_vintage": geography.get("boundary_vintage"),
            "census_source": census_manifest,
        },
        "quality": quality,
        "all_source": summarize(rows),
        "usable_cohort": summarize([r for r in rows if r["in_usable_cohort"]]),
        "limitations": [
            "Asking price is not realized revenue; capacity is advertised, not verified beds.",
            "28-night cutoff is analytical, not legal. ZCTAs/coordinates do not identify parcels.",
            "Bathroom and amenity evidence is retained; no inferred bathroom/amenity predictors yet.",
            "No fitted preprocessing, comp selection, model, occupancy or acquisition valuation.",
        ],
    }
    # One atomic artifact contains rows and audit so they cannot become mismatched files.
    content = json.dumps(
        {"audit": audit, "rows": rows},
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    temp = output.with_suffix(".json.part")
    try:
        temp.write_text(content + "\n", encoding="utf-8")
        temp.replace(output)
    finally:
        temp.unlink(missing_ok=True)
    return audit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", required=True)
    parser.add_argument(
        "--audit-report",
        type=Path,
        help="Optional aggregate-only report; never contains rows",
    )
    args = parser.parse_args()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.snapshot):
        parser.error("Snapshot must be YYYY-MM-DD")
    output = ROOT / "data/research" / args.snapshot / "normalized.json"
    if args.audit_report:
        report_path = args.audit_report.resolve()
        if (
            report_path == output.resolve()
            or report_path.is_relative_to(ROOT / "web")
            or report_path.is_relative_to(ROOT / "data/raw")
        ):
            parser.error(
                "Audit report must not overwrite normalized data, web assets or raw inputs"
            )
    audit = build(
        ROOT / "data/raw" / args.snapshot,
        ROOT / "web/static/data" / args.snapshot,
        args.snapshot,
        output,
    )
    if args.audit_report:
        args.audit_report.parent.mkdir(parents=True, exist_ok=True)
        args.audit_report.write_text(
            json.dumps(audit, sort_keys=True, indent=2) + "\n", encoding="utf-8"
        )
    print(
        json.dumps(
            {
                "snapshot": args.snapshot,
                "source_rows": audit["all_source"]["rows"],
                "usable_rows": audit["usable_cohort"]["rows"],
                "property_groups": audit["usable_cohort"]["property_groups"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
