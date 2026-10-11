"""Private review enrichment and aggregate catalog; no personal source values exported."""

import csv
import gzip
import hashlib
import json
import math
import re
from collections import Counter
from datetime import date

SCORES = tuple(
    "review_scores_" + name
    for name in (
        "rating",
        "accuracy",
        "cleanliness",
        "checkin",
        "communication",
        "location",
        "value",
    )
)
COUNTS = (
    "number_of_reviews",
    "number_of_reviews_ltm",
    "number_of_reviews_l30d",
    "number_of_reviews_ly",
)
REVIEWS = (*SCORES, *COUNTS, "reviews_per_month")


def parse_review(field, raw):
    if field not in REVIEWS:
        raise ValueError("Unknown review field")
    if not raw.strip():
        return None, "missing"
    try:
        value = float(raw)
    except ValueError:
        return None, "invalid"
    if not math.isfinite(value):
        return None, "invalid"
    if field in SCORES:
        valid = 1 <= value <= 5
    elif field in COUNTS:
        valid = value >= 0 and value.is_integer()
    else:
        valid = value >= 0
    if not valid:
        return None, "invalid"
    return (int(value) if field in COUNTS else value), "valid"


def field_role(field):
    if field == "price":
        return (
            "target",
            "Advertised price; prediction target, not a predictor or realized revenue.",
        )
    if field in {
        "room_type",
        "property_type",
        "bedrooms",
        "beds",
        "accommodates",
        "minimum_nights",
    }:
        return (
            "current",
            "Existing model input, directly or through property/stay grouping.",
        )
    if field in REVIEWS:
        return (
            "review_experiment",
            "Selectable review experiment input; scores/counts describe established rentals.",
        )
    if field.startswith(("host_", "hosts_", "calculated_host_")):
        return (
            "restricted",
            "Host data excluded from research predictors and public records under current policy.",
        )
    if field in {"estimated_occupancy_l365d", "estimated_revenue_l365d"}:
        return (
            "source_estimate",
            "Provider estimate, not observed bookings/revenue; excluded from model inputs.",
        )
    if field.startswith("price_quote_"):
        return (
            "target_related",
            "Price-derived quote; excluded as a predictor to avoid predicting price from price.",
        )
    if field in {"name", "description", "neighborhood_overview", "picture_url"}:
        return (
            "restricted",
            "Text/images excluded from this experiment; may expose personal or identifying details.",
        )
    if field == "license":
        return (
            "restricted",
            "Reported license is not verified legal eligibility; excluded.",
        )
    if field in {"latitude", "longitude"}:
        return (
            "geographic_input",
            "Approximate coordinates derive ZCTA/buffers; not parcel matching or direct model inputs.",
        )
    if field.startswith("neighbourhood"):
        return (
            "candidate",
            "Source neighborhood context; differs from Census ZCTA and verified legal jurisdiction.",
        )
    if field in {"bathrooms", "bathrooms_text", "amenities"}:
        return (
            "candidate",
            "Physical/amenity feature; parsing and shared/private semantics require owner review.",
        )
    if "nights" in field:
        return (
            "candidate",
            "Stay restriction, not observed occupancy; future feature choice.",
        )
    if field.startswith("availability_") or field == "has_availability":
        return (
            "candidate",
            "Calendar availability, not confirmed bookings; future research only.",
        )
    if field == "instant_bookable":
        return "candidate", "Booking setting; future feature choice."
    if field in {"first_review", "last_review"}:
        return (
            "candidate",
            "Review dates could support age/recency features; not occupancy labels.",
        )
    return "provenance", "Identifier/link/scrape metadata; not a predictor."


def validate_id(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]+", value):
        raise ValueError("Listing IDs must be digit strings")


def enrich(rows, raw, snapshot):
    date.fromisoformat(snapshot)
    manifest = json.loads((raw / "manifest.json").read_text(encoding="utf-8"))
    if manifest["snapshot_date"] != snapshot:
        raise ValueError("Source snapshot mismatch")
    path = raw / "listings.csv.gz"
    with path.open("rb") as handle:
        digest = hashlib.file_digest(handle, "sha256").hexdigest()
    if digest != manifest["files"][path.name]["sha256"]:
        raise ValueError("Checksum mismatch: detailed listings")
    expected = set()
    for row in rows:
        validate_id(row["id"])
        if row["id"] in expected or row.get("snapshot_date") != snapshot:
            raise ValueError("Duplicate or mismatched normalized IDs/snapshot")
        expected.add(row["id"])
    selected, missing = {}, Counter()
    with gzip.open(path, "rt", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        if len(fields) != len(set(fields)) or not {"id", *REVIEWS}.issubset(fields):
            raise ValueError("Missing/duplicate review source columns")
        for source in reader:
            if None in source or any(source.get(f) is None for f in fields):
                raise ValueError("Malformed detailed-listing row")
            identifier = source["id"]
            validate_id(identifier)
            if identifier in selected or identifier not in expected:
                raise ValueError("Duplicate or unexpected source ID")
            missing.update(f for f in fields if not source[f].strip())
            selected[identifier] = {f: source[f] for f in REVIEWS}
    if set(selected) != expected:
        raise ValueError("Incomplete source/normalized ID join")
    enriched = []
    for base in sorted(rows, key=lambda r: r["id"]):
        values = selected[base["id"]]
        row = {**base, "review_raw": values, "review_status": {}}
        for f, raw_value in values.items():
            row[f], row["review_status"][f] = parse_review(f, raw_value)
        enriched.append(row)
    catalog = {
        "source_rows": len(selected),
        "columns": {
            f: {
                "present": len(selected) - missing[f],
                "missing": missing[f],
                "role": field_role(f)[0],
                "interpretation": field_role(f)[1],
            }
            for f in fields
        },
    }
    return enriched, catalog, {"source_sha256": digest, "snapshot_date": snapshot}


def coverage(rows):
    return {
        f: {
            status: sum(r["review_status"][f] == status for r in rows)
            for status in ("valid", "missing", "invalid")
        }
        for f in REVIEWS
    }


def catalog_markdown(catalog, snapshot):
    intro = f"""# Airbnb feature menu

Snapshot **{snapshot}**; **{catalog["source_rows"]:,} source rows**, {len(catalog["columns"])} detailed-listing columns. Generated from hash-verified inputs by scripts/review_features.py. Coverage here is source-wide, not the modeling cohort; typed review coverage and cohort exclusions are in the [experiment results](../specs/002-review-features/development-results.json).

## Choices for neighborhood comparable research

| Group | Available fields | Current use / owner choice |
| --- | --- | --- |
| Property and capacity | Property/room type, bedrooms, beds, accommodates (sleeps) | Current model; distinct property and room groups |
| Geography | Approximate latitude/longitude, source neighborhoods; derived Census ZCTA | ZCTA model category and buffered geographic evaluation |
| Guest ratings | Overall, accuracy, cleanliness, check-in, communication, location, value | Added to selectable review experiment; value also tested separately |
| Review history | Total reviews, last 12 months, last 30 days, previous year, reviews/month | Added to selectable review experiment; not bookings or occupancy |
| Bathrooms | Numeric bathrooms and shared/private bathroom description | Available; deferred by owner pending this audit |
| Amenities | Source amenity list, potential pool/hot-tub/kitchen/parking indicators | Available; not yet encoded; deferred by owner |
| Stay/booking rules | Minimum/maximum nights and forward restrictions, instant booking | Current stay cohort uses minimum nights; additional predictors deferred |
| Availability | 30/60/90/365-day and end-of-year availability | Candidate only; unavailable does not mean booked |
| Review timing | First and last review dates | Candidate recency/establishment measures; not yet encoded |
| Lot size, living area, condition, renovation cost | Not provided as structured fields in this source | Property-source/owner-assumption work remains separate |

The owner chose **review features first**. Candidate means available for consideration, not developer approval or an implemented predictor. Use the [custom feature command](../specs/002-review-features/quickstart.md) to choose review inputs explicitly. Scores characterize existing comps, not guaranteed results from renovation. Review-count weighting and review-based comp filters are not implemented here; counts are ordinary selectable model inputs.

## Complete source catalog

`current` = existing input directly or via a derived group. `review_experiment` = selectable now. `candidate` = available but not implemented. Other roles explain why a field is metadata, target-related, estimated or restricted. Only field names and aggregate coverage are shown; no host/reviewer values, free text or source records are published.

| Source field | Present | Missing | Role | Interpretation |
| --- | ---: | ---: | --- | --- |
"""
    return (
        intro
        + "\n".join(
            f"| `{f}` | {v['present']:,} | {v['missing']:,} | {v['role']} | {v['interpretation']} |"
            for f, v in catalog["columns"].items()
        )
        + "\n"
    )
