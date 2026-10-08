"""Audit source coverage and build a private, allowlisted research table; no model training."""

import argparse
import csv
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FEATURES = (
    "id",
    "latitude",
    "longitude",
    "price",
    "room_type",
    "property_type",
    "bedrooms",
    "beds",
    "accommodates",
    "bathrooms",
    "bathrooms_text",
    "amenities",
    "minimum_nights",
    "maximum_nights",
    "neighbourhood_cleansed",
)


def audit_file(path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        missing = Counter()
        count = 0
        for row in reader:
            count += 1
            missing.update(key for key in fields if not row.get(key))
    return {
        "rows": count,
        "columns": fields,
        "missing": {key: missing[key] for key in fields},
    }


def build_research(raw, output):
    """Keep source values as strings; missing stays empty. Normalize only in training later."""
    report = {}
    manifest = json.loads((raw / "manifest.json").read_text())
    for name, entry in manifest["files"].items():
        path = raw / name
        with path.open("rb") as handle:
            digest = hashlib.file_digest(handle, "sha256").hexdigest()
        if digest != entry["sha256"]:
            raise ValueError("Checksum mismatch: " + name)
        if ".csv" in name:
            report[name] = audit_file(path)
    output.mkdir(parents=True, exist_ok=True)
    temp = output / "listing-features.csv.part"
    with gzip.open(
        raw / "listings.csv.gz", "rt", encoding="utf-8-sig", newline=""
    ) as handle:
        reader = csv.DictReader(handle)
        if not set(FEATURES).issubset(reader.fieldnames or []):
            raise ValueError("Missing research feature columns")
        with temp.open("w", encoding="utf-8", newline="") as target:
            writer = csv.DictWriter(target, fieldnames=FEATURES)
            writer.writeheader()
            for row in reader:
                writer.writerow({key: row[key] for key in FEATURES})
    temp.replace(output / "listing-features.csv")
    report["notes"] = [
        "Private research only; raw source values are not normalized or model-ready.",
        "Calendar unavailable dates are not bookings. Reviews do not establish occupancy.",
        "Summary listings duplicate detailed listings; never concatenate them as extra observations.",
        "No host or reviewer fields or review text in listing-features.csv.",
    ]
    (output / "coverage.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", required=True)
    args = parser.parse_args()
    raw = ROOT / "data/raw" / args.snapshot
    report = build_research(raw, ROOT / "data/research" / args.snapshot)
    print(
        json.dumps(
            {
                name: value["rows"]
                for name, value in report.items()
                if isinstance(value, dict)
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
