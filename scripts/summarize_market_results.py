"""Publish compact, allowlisted aggregate research evidence from private full run reports."""

import hashlib
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / "data/research/multi-city"
PUBLIC = ROOT / "specs/003-multi-city-research"


def geography_summary(partition):
    geography = partition["subgroups"]["geographic_block"]
    blocks = geography["supported"]
    candidates = list(partition["metrics"])
    distributions = {}
    for candidate in candidates:
        values = sorted(
            block["metrics"][candidate]["mae_usd"] for block in blocks.values()
        )
        distributions[candidate] = (
            {
                "median_block_mae_usd": statistics.median(values),
                "p10_block_mae_usd": values[int(0.1 * (len(values) - 1))],
                "p90_block_mae_usd": values[int(0.9 * (len(values) - 1))],
            }
            if values
            else None
        )
    return {
        "supported_blocks": len(blocks),
        "suppressed_blocks": geography["suppressed_groups"],
        "suppressed_observations": geography["suppressed_observations"],
        "supported_block_error_distribution": distributions,
    }


def compact_partition(partition, detailed=False):
    result = {
        "training_n": partition["training_n"],
        "evaluation_n": partition["evaluation_n"],
        "metrics": partition["metrics"],
        "negative_prediction_clamps": partition["negative_prediction_clamps"],
        "uncertainty": partition["uncertainty"],
        "geography": geography_summary(partition),
    }
    if detailed:
        result["subgroups"] = {
            name: partition["subgroups"][name]
            for name in ("market_id", "room_type", "property_group", "price_band")
        }
    return result


def compact_development(full, digest):
    if full["stage"] != "development":
        raise ValueError("Expected development report")
    geography = full["pooled_development_subgroups"]["geographic_block"]
    return {
        "stage": "development",
        "research_question": full["research_question"],
        "hypothesis": full["hypothesis"],
        "feature_allowlist": full["feature_allowlist"],
        "candidate_configurations": full["candidate_configurations"],
        "folds": full["folds"],
        "pooled_development_metrics": full["pooled_development_metrics"],
        "pooled_development_subgroups": {
            name: full["pooled_development_subgroups"][name]
            for name in ("market_id", "room_type", "property_group", "price_band")
        },
        "geography_support": {
            "supported_blocks": len(geography["supported"]),
            "suppressed_blocks": geography["suppressed_groups"],
            "suppressed_observations": geography["suppressed_observations"],
        },
        "selected_candidate_for_final": full["selected_candidate_for_final"],
        "selection_metric": full["selection_metric"],
        "provenance": full["provenance"],
        "full_private_sha256": digest,
        "limitations": full["limitations"],
    }


def compact_final(full, digest):
    if full["stage"] != "final":
        raise ValueError("Expected final report")
    return {
        "stage": "final",
        "selected_candidate": full["selected_candidate"],
        "provenance": full["provenance"],
        "full_private_sha256": digest,
        "within_city": {
            market: compact_partition(partition, detailed=True)
            for market, partition in full["within_city"].items()
        },
        "pooled": compact_partition(full["pooled"], detailed=True),
        "leave_one_city_out_diagnostic": {
            market: compact_partition(partition)
            for market, partition in full["leave_one_city_out_diagnostic"].items()
        },
        "limited_local_adaptation": {
            market: {
                budget: compact_partition(partition)
                for budget, partition in budgets.items()
            }
            for market, budgets in full["limited_local_adaptation"].items()
        },
        "public_prediction_release": full["public_prediction_release"],
        "limitations": full["limitations"],
    }


def publish(path, result):
    temporary = path.with_suffix(".json.part")
    try:
        temporary.write_text(
            json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def main():
    for stage, full_name, public_name, transform in (
        (
            "development",
            "development-full.json",
            "development-results.json",
            compact_development,
        ),
        ("final", "final-full.json", "final-evaluation.json", compact_final),
    ):
        source = PRIVATE / full_name
        data = source.read_bytes()
        full = json.loads(data)
        result = transform(full, hashlib.sha256(data).hexdigest())
        publish(PUBLIC / public_name, result)
        print(
            f"{stage} aggregate: {len(data)} private bytes -> {(PUBLIC / public_name).stat().st_size} public bytes"
        )


if __name__ == "__main__":
    main()
