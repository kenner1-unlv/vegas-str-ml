"""Normalize verified multi-market listings into private rows and aggregate audits."""

import argparse
import csv
import gzip
import hashlib
import json
import math
import re
import statistics
import sys
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from normalize_research import NUMERIC_FIELDS, PROPERTY_MAP, ROOM_MAP, numeric
from review_features import REVIEWS, parse_review

from market_sources import archive_path, registry, verify_archive

SOURCE_FIELDS = (
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
    "minimum_nights",
    "maximum_nights",
    "neighbourhood_cleansed",
    *REVIEWS,
)
PRICE_PATTERN = re.compile(r"\$?(?:\d+|\d{1,3}(?:,\d{3})+)(?:\.\d{1,2})?")
RULES_VERSION = "1.0.0"


def parse_price(raw):
    if not raw.strip():
        return None, "missing"
    if not PRICE_PATTERN.fullmatch(raw):
        return None, "invalid"
    value = float(raw.replace("$", "").replace(",", ""))
    if not math.isfinite(value) or value <= 0:
        return None, "invalid"
    return value, "valid"


def parse_coordinate(raw, low, high):
    if not raw.strip():
        return None, "missing"
    try:
        value = float(raw)
    except ValueError:
        return None, "invalid"
    return (value, "valid") if math.isfinite(value) and low <= value <= high else (None, "invalid")


def parse_date(raw):
    if not raw.strip():
        return None, "missing"
    try:
        return date.fromisoformat(raw).isoformat(), "valid"
    except ValueError:
        return None, "invalid"


def normalize_row(source, market, snapshot):
    raw = {name: source.get(name) or "" for name in SOURCE_FIELDS}
    identifier = raw["id"]
    if not re.fullmatch(r"[0-9]+", identifier):
        return None, "invalid_id"

    price, price_status = parse_price(raw["price"])
    latitude, lat_status = parse_coordinate(raw["latitude"], -90, 90)
    longitude, lon_status = parse_coordinate(raw["longitude"], -180, 180)
    scraped, date_status = parse_date(raw["last_scraped"])
    counts = {field: numeric(raw[field], minimum) for field, minimum in NUMERIC_FIELDS.items()}
    reviews = {field: parse_review(field, raw[field]) for field in REVIEWS}
    room = ROOM_MAP.get(raw["room_type"], "unknown")
    property_group = PROPERTY_MAP.get(raw["property_type"], "unknown")
    statuses = {
        "asking_price_usd": price_status,
        "latitude": lat_status,
        "longitude": lon_status,
        "source_last_scraped": date_status,
        "room_type": "known" if room != "unknown" else "unknown",
        "property_group": "known" if property_group != "unknown" else "unknown",
        **{field: value[1] for field, value in counts.items()},
        **{field: value[1] for field, value in reviews.items()},
    }
    row = {
        "market_id": market,
        "snapshot_date": snapshot,
        "id": identifier,
        "source_last_scraped": scraped,
        "asking_price_usd": price,
        "latitude": latitude,
        "longitude": longitude,
        "room_type": room,
        "property_type": raw["property_type"],
        "property_group": property_group,
        "source_neighborhood": raw["neighbourhood_cleansed"],
        **{field: value[0] for field, value in counts.items()},
        "reviews": {field: value[0] for field, value in reviews.items()},
        "statuses": statuses,
        "raw": raw,
    }
    if price_status != "valid":
        return row, "missing_price" if price_status == "missing" else "invalid_price"
    if lat_status != "valid" or lon_status != "valid":
        return row, "invalid_coordinates"
    return row, None


def quantiles(values):
    if not values:
        return None
    ordered = sorted(values)
    return {
        "min": ordered[0],
        "median": statistics.median(ordered),
        "p99": ordered[int(0.99 * (len(ordered) - 1))],
        "max": ordered[-1],
    }


def normalize_archive(path, market, snapshot, output):
    """Write only included rows, atomically; return source-denominator aggregate audit."""
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    part = output.with_suffix(output.suffix + ".part")
    source_rows = 0
    reasons = Counter()
    statuses = Counter()
    room_types = Counter()
    properties = Counter()
    scraped_dates = Counter()
    prices = []
    seen = set()
    try:
        with (
            gzip.open(path, "rt", encoding="utf-8-sig", newline="") as handle,
            part.open("w", encoding="utf-8", newline="\n") as target,
        ):
            reader = csv.DictReader(handle)
            fields = reader.fieldnames or []
            if len(fields) != len(set(fields)) or not set(SOURCE_FIELDS).issubset(fields):
                raise ValueError("Incomplete or duplicate source header")
            for source in reader:
                source_rows += 1
                if None in source:
                    reasons["malformed_row"] += 1
                    continue
                row, reason = normalize_row(source, market, snapshot)
                if row is None:
                    reasons[reason] += 1
                    continue
                if row["id"] in seen:
                    reasons["duplicate_id"] += 1
                    continue
                seen.add(row["id"])
                room_types[source.get("room_type") or "(missing)"] += 1
                properties[source.get("property_type") or "(missing)"] += 1
                scraped_dates[source.get("last_scraped") or "(missing)"] += 1
                statuses.update(f"{field}:{state}" for field, state in row["statuses"].items())
                if reason:
                    reasons[reason] += 1
                    continue
                prices.append(row["asking_price_usd"])
                target.write(json.dumps(row, sort_keys=True, allow_nan=False) + "\n")
        included = len(prices)
        if source_rows != included + sum(reasons.values()):
            raise ValueError("Source row reconciliation failed")
        part.replace(output)
    finally:
        part.unlink(missing_ok=True)
    return {
        "market_id": market,
        "snapshot_date": snapshot,
        "source_rows": source_rows,
        "included_rows": included,
        "excluded_rows": source_rows - included,
        "first_failure_reasons": dict(sorted(reasons.items())),
        "statuses": dict(sorted(statuses.items())),
        "room_types": dict(sorted(room_types.items())),
        "property_types": dict(sorted(properties.items())),
        "source_last_scraped": dict(sorted(scraped_dates.items())),
        "included_price_usd": quantiles(prices),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--market", choices=sorted(registry()["markets"]), required=True)
    args = parser.parse_args()
    manifest = registry()
    source = manifest["markets"][args.market]
    path = archive_path(args.market, source)
    output = (
        ROOT
        / "data/research/multi-city"
        / args.market
        / source["snapshot_date"]
        / "normalized.jsonl"
    )
    try:
        verified = verify_archive(path, source, manifest["header_sha256"])
        audit = normalize_archive(path, args.market, source["snapshot_date"], output)
        report = {
            **audit,
            "normalization_rules_version": RULES_VERSION,
            "normalizer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "source": {**verified, "retrieved_at_utc": source["retrieved_at_utc"]},
        }
        audit_path = output.with_name("audit.json")
        part = audit_path.with_suffix(".json.part")
        try:
            part.write_text(
                json.dumps(report, sort_keys=True, indent=2, allow_nan=False) + "\n",
                encoding="utf-8",
            )
            part.replace(audit_path)
        finally:
            part.unlink(missing_ok=True)
        print(json.dumps(report, sort_keys=True, allow_nan=False))
    except (OSError, ValueError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
