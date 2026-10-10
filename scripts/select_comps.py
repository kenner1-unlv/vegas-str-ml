"""Select geographic asking-price comps privately; no training or revenue inference."""

import argparse
import hashlib
import json
import math
import re
import tempfile
from collections import Counter
from datetime import date
from pathlib import Path
from statistics import median

from normalize_research import ROOM_MAP, ROOT, RULES_VERSION, build

COMPS_VERSION = "1.0.0"
MINIMUM_SUPPORT = 20
SUPPORTED_GROUPS = {
    "house_like",
    "apartment_condo",
    "hotel_resort",
    "serviced_apartment",
    "guesthouse_suite",
}
SUMMARY_FIELDS = (
    "median_asking_price_usd",
    "subject_difference_usd",
    "subject_difference_percent",
)


def validate_rows(rows):
    seen = set()
    snapshots = set()
    for row in rows:
        identifier = row.get("id")
        if (
            not isinstance(identifier, str)
            or not re.fullmatch(r"[0-9]+", identifier)
            or identifier in seen
        ):
            raise ValueError("Invalid or duplicate listing ID")
        seen.add(identifier)
        snapshots.add(row.get("snapshot_date"))
        if type(row.get("in_usable_cohort")) is not bool:
            raise ValueError("Invalid usable-cohort flag")
        for key, minimum in (("bedrooms", 0), ("accommodates", 1)):
            value = row.get(key)
            if value is not None and (type(value) is not int or value < minimum):
                raise ValueError("Invalid comparable characteristic: " + key)
        if (
            row.get("property_group") not in SUPPORTED_GROUPS | {"other", "unknown"}
            or row.get("room_type") not in set(ROOM_MAP.values()) | {"unknown"}
            or row.get("stay_cohort")
            not in {"1_27_nights", "28_plus_nights", "unknown"}
        ):
            raise ValueError("Invalid normalized comparison category")
        price = row.get("asking_price_usd")
        if row["in_usable_cohort"]:
            if (
                type(price) not in {int, float}
                or not math.isfinite(price)
                or price <= 0
            ):
                raise ValueError("Invalid usable asking price")
        elif price is not None:
            raise ValueError("Excluded cohort row has a study target")
        geo = row.get("geography")
        if geo is not None:
            if not isinstance(geo, dict):
                raise TypeError("Invalid geography")
            status, code = geo.get("status"), geo.get("zcta")
            if (
                status not in {"assigned", "unassigned", "ambiguous"}
                or type(geo.get("near_boundary")) is not bool
                or (
                    status == "assigned"
                    and (
                        not isinstance(code, str) or not re.fullmatch(r"[0-9]{5}", code)
                    )
                )
                or (status != "assigned" and code is not None)
            ):
                raise ValueError("Invalid geographic assignment")
    if len(snapshots) != 1:
        raise ValueError("Comparisons require one snapshot")
    try:
        date.fromisoformat(next(iter(snapshots)))
    except (TypeError, ValueError) as exc:
        raise ValueError("Invalid snapshot date") from exc


def support_reasons(row, capacity_tolerance, edge_policy):
    reasons = []
    if not row["in_usable_cohort"]:
        reasons.append("outside_usable_cohort")
    if row["property_group"] not in SUPPORTED_GROUPS:
        reasons.append("unsupported_property_group")
    if row["room_type"] == "unknown":
        reasons.append("unknown_room_type")
    if row["stay_cohort"] == "unknown":
        reasons.append("unknown_stay_cohort")
    geo = row["geography"]
    if geo is None or geo["status"] != "assigned":
        reasons.append("unknown_geography")
    if row["bedrooms"] is None:
        reasons.append("unknown_bedrooms")
    if capacity_tolerance is not None and row["accommodates"] is None:
        reasons.append("unknown_capacity")
    if edge_policy == "exclude" and geo is not None and geo["near_boundary"]:
        reasons.append("near_boundary_subject")
    return reasons


def select_comps(
    rows,
    subject_id,
    bedroom_tolerance=1,
    capacity_tolerance=None,
    edge_policy="include",
):
    if (
        type(bedroom_tolerance) is not int
        or bedroom_tolerance < 0
        or (
            capacity_tolerance is not None
            and (type(capacity_tolerance) is not int or capacity_tolerance < 0)
        )
        or edge_policy not in {"include", "exclude"}
    ):
        raise ValueError("Invalid comparison tolerance or edge policy")
    validate_rows(rows)
    subjects = [row for row in rows if row["id"] == subject_id]
    if len(subjects) != 1:
        raise ValueError("Subject ID not found in this snapshot")
    subject = subjects[0]
    reasons = support_reasons(subject, capacity_tolerance, edge_policy)
    result = {
        "schema_version": 1,
        "comps_version": COMPS_VERSION,
        "snapshot_date": subject["snapshot_date"],
        "subject_id": subject_id,
        "request": {
            "zcta": subject["geography"]["zcta"] if subject["geography"] else None,
            "property_group": subject["property_group"],
            "room_type": subject["room_type"],
            "stay_cohort": subject["stay_cohort"],
            "bedrooms": subject["bedrooms"],
            "bedroom_tolerance": bedroom_tolerance,
            "accommodates": subject["accommodates"],
            "capacity_tolerance": capacity_tolerance,
            "edge_policy": edge_policy,
        },
        "input_rows": len(rows),
        "subject_limitations": reasons,
        "subject_near_boundary": bool(
            subject["geography"] and subject["geography"]["near_boundary"]
        ),
        "minimum_support": MINIMUM_SUPPORT,
        "support": "unsupported_subject",
        "matched_ids": [],
        "matched_count": 0,
        "matched_near_boundary_count": 0,
        "matches_without_boundary_sensitive": 0,
        "exclusions": {},
        "summary": dict.fromkeys(SUMMARY_FIELDS),
        "limitations": [
            "Descriptive asking rates only; no model, occupancy, earnings or investment result.",
            "ZCTAs use anonymized coordinates; no parcel or eligibility inference.",
            "n=20 is a display/support floor, not statistical confidence.",
            "Exclusions count each row's first failure, not overlapping reason prevalence.",
        ],
    }
    if reasons:
        return result
    matched, excluded = [], Counter()
    for row in rows:
        reason = None
        if row["id"] == subject_id:
            reason = "subject"
        else:
            unsupported = support_reasons(row, capacity_tolerance, "include")
            if unsupported:
                reason = unsupported[0]
            elif row["geography"]["zcta"] != subject["geography"]["zcta"]:
                reason = "different_zcta"
            else:
                for key in ("property_group", "room_type", "stay_cohort"):
                    if row[key] != subject[key]:
                        reason = "different_" + key
                        break
                if (
                    reason is None
                    and abs(row["bedrooms"] - subject["bedrooms"]) > bedroom_tolerance
                ):
                    reason = "bedrooms_outside_tolerance"
                if (
                    reason is None
                    and capacity_tolerance is not None
                    and abs(row["accommodates"] - subject["accommodates"])
                    > capacity_tolerance
                ):
                    reason = "capacity_outside_tolerance"
                if (
                    reason is None
                    and edge_policy == "exclude"
                    and row["geography"]["near_boundary"]
                ):
                    reason = "near_boundary"
        if reason:
            excluded[reason] += 1
        else:
            matched.append(row)
    result.update(
        matched_ids=sorted(row["id"] for row in matched),
        matched_count=len(matched),
        exclusions=dict(sorted(excluded.items())),
        matched_near_boundary_count=sum(
            row["geography"]["near_boundary"] for row in matched
        ),
        matches_without_boundary_sensitive=sum(
            not row["geography"]["near_boundary"] for row in matched
        ),
        support="supported" if len(matched) >= MINIMUM_SUPPORT else "thin_sample",
    )
    if len(matched) >= MINIMUM_SUPPORT:
        price = median(row["asking_price_usd"] for row in matched)
        difference = subject["asking_price_usd"] - price
        result["summary"] = {
            "median_asking_price_usd": price,
            "subject_difference_usd": difference,
            "subject_difference_percent": 100 * difference / price,
        }
    return result


def load_verified(snapshot):
    path = ROOT / "data/research" / snapshot / "normalized.json"
    body = path.read_bytes()
    dataset = json.loads(body)
    if (
        dataset.get("audit", {}).get("schema_version") != 1
        or dataset["audit"].get("rules_version") != RULES_VERSION
        or dataset["audit"].get("snapshot_date") != snapshot
    ):
        raise ValueError("Unsupported normalized dataset; rerun normalization")
    with tempfile.TemporaryDirectory(prefix="comps-verify-", dir=path.parent) as folder:
        rebuilt = Path(folder) / "normalized.json"
        build(
            ROOT / "data/raw" / snapshot,
            ROOT / "web/static/data" / snapshot,
            snapshot,
            rebuilt,
        )
        if dataset != json.loads(rebuilt.read_text(encoding="utf-8")):
            raise ValueError("Stale or edited normalized dataset; rerun normalization")
    validate_rows(dataset["rows"])
    return dataset, hashlib.sha256(body).hexdigest()


def aggregate_view(result):
    return {
        key: value
        for key, value in result.items()
        if key not in {"subject_id", "matched_ids"}
    }


def output_path(value):
    path = Path(value).resolve()
    if (
        not path.is_relative_to(ROOT / "data/research")
        or path.suffix != ".json"
        or path.name.casefold() == "normalized.json"
    ):
        raise ValueError(
            "Full comparison outputs must be .json in ignored data/research/, not normalized.json"
        )
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--subject-id", required=True)
    parser.add_argument("--bedroom-tolerance", type=int, default=1)
    parser.add_argument("--capacity-tolerance", type=int)
    parser.add_argument(
        "--edge-policy", choices=("include", "exclude"), default="include"
    )
    parser.add_argument(
        "--output", help="Optional full private JSON inside data/research/"
    )
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", args.snapshot):
        parser.error("Snapshot must be YYYY-MM-DD")
    if not re.fullmatch(r"[0-9]+", args.subject_id):
        parser.error("Subject ID must be a digit string")
    try:
        target = output_path(args.output) if args.output else None
        dataset, digest = load_verified(args.snapshot)
        result = select_comps(
            dataset["rows"],
            args.subject_id,
            args.bedroom_tolerance,
            args.capacity_tolerance,
            args.edge_policy,
        )
        result["provenance"] = {
            "normalized_sha256": digest,
            "normalization_rules_version": RULES_VERSION,
            "selector_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "inputs": dataset["audit"]["provenance"],
        }
        content = json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n"
        if target:
            target.parent.mkdir(parents=True, exist_ok=True)
            temp = target.with_suffix(".json.part")
            try:
                temp.write_text(content, encoding="utf-8")
                temp.replace(target)
            finally:
                temp.unlink(missing_ok=True)
        print(
            json.dumps(
                aggregate_view(result), sort_keys=True, indent=2, allow_nan=False
            )
        )
    except (ValueError, OSError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
