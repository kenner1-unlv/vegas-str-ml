"""Reproduce aggregate-only geographic comp examples and support coverage offline."""

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from select_comps import (
    COMPS_VERSION,
    MINIMUM_SUPPORT,
    load_verified,
    select_comps,
    support_reasons,
)


def coverage(rows, policy):
    counts = Counter()
    subjects = []
    usable = [row for row in rows if row["in_usable_cohort"]]
    for row in usable:
        if support_reasons(row, None, policy):
            continue
        key = (
            row["geography"]["zcta"],
            row["property_group"],
            row["room_type"],
            row["stay_cohort"],
        )
        counts[(key, row["bedrooms"])] += 1
        subjects.append((row, key))
    statuses = Counter(
        {
            "unsupported_subject": len(usable) - len(subjects),
            "supported": 0,
            "thin_sample": 0,
        }
    )
    for row, key in subjects:
        total = (
            sum(
                counts[(key, bedroom)]
                for bedroom in range(max(0, row["bedrooms"] - 1), row["bedrooms"] + 2)
            )
            - 1
        )
        statuses["supported" if total >= MINIMUM_SUPPORT else "thin_sample"] += 1
    return dict(statuses)


def audit(dataset, digest):
    rows = dataset["rows"]
    examples = []
    for code, bedrooms, label in (
        ("89146", 4, "89146_four_bedroom_house"),
        ("89005", None, "89005_small_house_sample"),
    ):
        subjects = [
            row
            for row in rows
            if row["in_usable_cohort"]
            and row["geography"]
            and row["geography"]["status"] == "assigned"
            and row["geography"]["zcta"] == code
            and not row["geography"]["near_boundary"]
            and row["property_group"] == "house_like"
            and row["room_type"] == "entire_home_apt"
            and row["stay_cohort"] == "1_27_nights"
            and row["bedrooms"] is not None
            and (bedrooms is None or row["bedrooms"] == bedrooms)
        ]
        if not subjects:
            examples.append({"profile": label, "support": "no_subject_for_example"})
            continue
        subject = min(subjects, key=lambda row: row["id"])
        for options in (
            {},
            {"bedroom_tolerance": 0},
            {"edge_policy": "exclude"},
            {"capacity_tolerance": 2},
        ):
            result = select_comps(rows, subject["id"], **options)
            examples.append(
                {
                    "profile": label,
                    "options": options,
                    "matched_count": result["matched_count"],
                    "support": result["support"],
                    "median_asking_price_usd": result["summary"][
                        "median_asking_price_usd"
                    ],
                    "near_boundary_count": result["matched_near_boundary_count"],
                    "exclusions": result["exclusions"],
                }
            )
    return {
        "selector_sha256": hashlib.sha256(
            Path(__file__).with_name("select_comps.py").read_bytes()
        ).hexdigest(),
        "audit_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "snapshot_date": dataset["audit"]["snapshot_date"],
        "rules_version": COMPS_VERSION,
        "source_rows": len(rows),
        "usable_rows": sum(row["in_usable_cohort"] for row in rows),
        "normalization_sha256": digest,
        "examples": examples,
        "default_coverage": {
            policy: coverage(rows, policy) for policy in ("include", "exclude")
        },
        "limitations": [
            "Counts are actual snapshot descriptive support, not model quality or confidence.",
            "No IDs, subject prices, individual research rows, or capacity values published.",
            "Examples choose first lexicographic ID meeting the documented profile; not representative valuation.",
            "Capacity tolerance is centered on the selected example's advertised capacity.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", args.snapshot):
        parser.error("Snapshot must be YYYY-MM-DD")
    dataset, digest = load_verified(args.snapshot)
    print(json.dumps(audit(dataset, digest), sort_keys=True, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
