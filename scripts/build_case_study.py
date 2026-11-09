"""Build a small public case-study payload from reviewed aggregate evidence only."""

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "specs/003-multi-city-research"
OUTPUT = ROOT / "web/src/lib/research-summary.json"
MARKET_ORDER = ("clark-county-nv", "new-york-city", "los-angeles", "nashville")


def load(name):
    path = SPEC / name
    value = json.loads(path.read_text(encoding="utf-8"))
    canonical = json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()
    return value, hashlib.sha256(canonical).hexdigest()


def build():
    sources, source_hash = load("source-manifest.json")
    audit, audit_hash = load("source-audit.json")
    development, development_hash = load("development-results.json")
    final, final_hash = load("final-evaluation.json")
    secondary, secondary_hash = load("secondary-results.json")
    if (
        final["public_prediction_release"] != "withheld"
        or secondary["public_classification_release"] != "withheld"
    ):
        raise ValueError(
            "Case study cannot advertise released predictions or classifier"
        )
    if development["selected_candidate_for_final"] != final["selected_candidate"]:
        raise ValueError("Final candidate differs from frozen development selection")
    markets = []
    for market in MARKET_ORDER:
        source = sources["markets"][market]
        cohort = audit["markets"][market]
        item = {
            "id": market,
            "area": source["source_area"],
            "snapshot_date": source["snapshot_date"],
            "source_rows": cohort["source_rows"],
            "priced_rows": cohort["included_rows"],
            "missing_price_rows": cohort["exclusions"].get("missing_price", 0),
            "source_url": source["url"],
            "fresh_final": market in final["within_city"],
        }
        if item["fresh_final"]:
            item["final_n"] = final["within_city"][market]["evaluation_n"]
            item["within_city_mae_usd"] = {
                name: score["mae_usd"]
                for name, score in final["within_city"][market]["metrics"].items()
            }
            item["classification_macro_f1"] = {
                name: score["macro_f1"]
                for name, score in secondary["markets"][market][
                    "pooled_development_metrics"
                ].items()
            }
            item["adaptation_mae_usd"] = {
                budget: result["metrics"][final["selected_candidate"]]["mae_usd"]
                for budget, result in final["limited_local_adaptation"][market].items()
            }
        markets.append(item)
    pooled = final["pooled"]
    hotel = pooled["subgroups"]["room_type"]["supported"]["hotel_room"]
    mid = pooled["subgroups"]["price_band"]["supported"]["250_499"]
    return {
        "schema_version": 1,
        "study_date": "2026-11-08",
        "source_name": "Inside Airbnb",
        "source_page": sources["source_page"],
        "license_url": sources["license_url"],
        "markets": markets,
        "source_rows": sum(market["source_rows"] for market in markets),
        "priced_rows": sum(market["priced_rows"] for market in markets),
        "development_n": development["pooled_development_metrics"]["room_median"]["n"],
        "development_mae_usd": {
            name: score["mae_usd"]
            for name, score in development["pooled_development_metrics"].items()
        },
        "final_n": pooled["evaluation_n"],
        "final_metrics": {
            name: {"mae_usd": score["mae_usd"], "rmse_usd": score["rmse_usd"]}
            for name, score in pooled["metrics"].items()
        },
        "selected_candidate": final["selected_candidate"],
        "pooled_mae_interval_usd": pooled["uncertainty"][final["selected_candidate"]][
            "mae_usd_95pct"
        ],
        "hotel_failure": {
            "n": hotel["n"],
            "candidate_mae_usd": hotel["metrics"][final["selected_candidate"]][
                "mae_usd"
            ],
            "room_median_mae_usd": hotel["metrics"]["room_median"]["mae_usd"],
        },
        "mid_price_failure": {
            "n": mid["n"],
            "candidate_mae_usd": mid["metrics"][final["selected_candidate"]]["mae_usd"],
            "room_median_mae_usd": mid["metrics"]["room_median"]["mae_usd"],
        },
        "loco_mae_usd": {
            market: {
                name: score["mae_usd"]
                for name, score in report["metrics"].items()
                if name in ("room_median", final["selected_candidate"])
            }
            for market, report in final["leave_one_city_out_diagnostic"].items()
        },
        "nashville_loco_ridge_rmse_usd": final["leave_one_city_out_diagnostic"][
            "nashville"
        ]["metrics"]["ridge"]["rmse_usd"],
        "public_prediction_release": "withheld",
        "evidence_sha256": {
            "source_manifest": source_hash,
            "source_audit": audit_hash,
            "development": development_hash,
            "final": final_hash,
            "secondary": secondary_hash,
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    content = json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n"
    if args.check:
        if (
            not OUTPUT.exists()
            or json.loads(OUTPUT.read_text(encoding="utf-8")) != value
        ):
            parser.error(
                "Case-study summary is missing or stale; regenerate and review it"
            )
        print("Case-study summary matches reviewed aggregate evidence")
        return
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    temporary = OUTPUT.with_suffix(".json.part")
    try:
        temporary.write_text(content, encoding="utf-8")
        temporary.replace(OUTPUT)
    finally:
        temporary.unlink(missing_ok=True)
    print(f"Case-study summary: {OUTPUT.stat().st_size} bytes")


if __name__ == "__main__":
    main()
