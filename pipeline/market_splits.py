"""Frozen group-aware geographic partitions for private multi-city evaluation."""

import argparse
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
LATITUDE_CENTERS = {
    "clark-county-nv": 36.2,
    "new-york-city": 40.7,
    "los-angeles": 34.1,
    "nashville": 36.15,
}
EARTH_KM = 6371.0088
BLOCK_KM = 3
BUFFER_M = 1000
SEED = "vegas-str-multicity-v1"
NEW_FINAL_MARKETS = ("new-york-city", "los-angeles", "nashville")
LOCAL_BUDGETS = (0, 100, 500)


def spatial_block(row):
    market = row["market_id"]
    center = LATITUDE_CENTERS[market]
    lat, lon = row["latitude"], row["longitude"]
    if not all(math.isfinite(value) for value in (lat, lon)):
        raise ValueError("Nonfinite geographic coordinate")
    x = EARTH_KM * math.cos(math.radians(center)) * math.radians(lon)
    y = EARTH_KM * math.radians(lat)
    return f"{market}:{math.floor(x / BLOCK_KM)}:{math.floor(y / BLOCK_KM)}"


def fold(block, purpose, count):
    value = hashlib.sha256(f"{SEED}:{purpose}:{block}".encode()).hexdigest()
    return int(value, 16) % count


def row_key(row):
    return row["market_id"], row["id"], row["snapshot_date"]


def group_key(row):
    return row["market_id"], row["id"]


def grouped_rows(rows):
    seen = set()
    blocks = defaultdict(set)
    for row in rows:
        key = row_key(row)
        if key in seen:
            raise ValueError("Duplicate market/listing/snapshot observation")
        seen.add(key)
        blocks[group_key(row)].add(spatial_block(row))
    drift = {group for group, values in blocks.items() if len(values) > 1}
    kept = sorted((row for row in rows if group_key(row) not in drift), key=row_key)
    return kept, {
        "geographic_drift_groups": len(drift),
        "geographic_drift_observations": len(rows) - len(kept),
    }


def unit_points(rows):
    angles = np.radians([(row["latitude"], row["longitude"]) for row in rows])
    lat, lon = angles[:, 0], angles[:, 1]
    return np.column_stack((np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)))


def buffered_fitting(fitting, held):
    if not held:
        raise ValueError("Empty geographic validation partition")
    held_groups = {group_key(row) for row in held}
    eligible = [row for row in fitting if group_key(row) not in held_groups]
    by_market = defaultdict(list)
    for row in held:
        by_market[row["market_id"]].append(row)
    kept = []
    buffer_excluded = 0
    minimum_kept_distance = math.inf
    for market in sorted({row["market_id"] for row in eligible}):
        members = [row for row in eligible if row["market_id"] == market]
        if market not in by_market:
            kept.extend(members)
            continue
        chord, _ = cKDTree(unit_points(by_market[market])).query(unit_points(members))
        distance = 2 * EARTH_KM * 1000 * np.arcsin(np.clip(chord / 2, 0, 1))
        for row, meters in zip(members, distance, strict=True):
            if meters > BUFFER_M:
                kept.append(row)
                minimum_kept_distance = min(minimum_kept_distance, meters)
            else:
                buffer_excluded += 1
    kept.sort(key=row_key)
    return kept, {
        "group_excluded": len(fitting) - len(eligible),
        "buffer_excluded": buffer_excluded,
        "minimum_kept_distance_m": (
            None if math.isinf(minimum_kept_distance) else float(minimum_kept_distance)
        ),
    }


def membership(rows):
    return [
        {
            "market_id": row["market_id"],
            "id": row["id"],
            "snapshot_date": row["snapshot_date"],
            "block": spatial_block(row),
        }
        for row in sorted(rows, key=row_key)
    ]


def split_market(rows, market, require_support=True):
    if any(row["market_id"] != market for row in rows):
        raise ValueError("Mixed source markets in one market split")
    eligible, drift = grouped_rows(rows)
    final = [row for row in eligible if fold(spatial_block(row), "outer", 5) == 0]
    development = [row for row in eligible if fold(spatial_block(row), "outer", 5) != 0]
    if not final or not development:
        raise ValueError("Insufficient final or development geography")
    final_blocks = Counter(spatial_block(row) for row in final)
    if (
        require_support
        and market in NEW_FINAL_MARKETS
        and (
            len(final) < 500
            or len(final_blocks) < 10
            or sum(count >= 20 for count in final_blocks.values()) < 5
        )
    ):
        raise ValueError("Insufficient final geographic support")
    fitting, outer_buffer = buffered_fitting(development, final)
    if not fitting:
        raise ValueError("Insufficient fitting geography after final buffer")
    if {group_key(row) for row in fitting} & {group_key(row) for row in final}:
        raise ValueError("Final listing-group overlap")
    if {spatial_block(row) for row in fitting} & set(final_blocks):
        raise ValueError("Final geographic-block overlap")
    inner = []
    for index in range(3):
        validation = [row for row in fitting if fold(spatial_block(row), "inner", 3) == index]
        initial = [row for row in fitting if fold(spatial_block(row), "inner", 3) != index]
        if not validation or not initial:
            raise ValueError("Insufficient inner geographic support")
        inner_fitting, buffer_audit = buffered_fitting(initial, validation)
        if {group_key(row) for row in inner_fitting} & {group_key(row) for row in validation}:
            raise ValueError("Inner listing-group overlap")
        if {spatial_block(row) for row in inner_fitting} & {
            spatial_block(row) for row in validation
        }:
            raise ValueError("Inner geographic-block overlap")
        if require_support and (len(validation) < 200 or len(inner_fitting) < 1000):
            raise ValueError("Insufficient inner geographic support")
        inner.append(
            {
                "fold": index,
                "fitting": inner_fitting,
                "validation": validation,
                "buffer": buffer_audit,
            }
        )
    manifest = {
        "market": market,
        "eligible": membership(eligible),
        "fitting": membership(fitting),
        "final": membership(final),
        "inner": [
            {
                "fold": entry["fold"],
                "fitting": membership(entry["fitting"]),
                "validation": membership(entry["validation"]),
            }
            for entry in inner
        ],
    }
    digest = hashlib.sha256(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return {
        "eligible": eligible,
        "fitting": fitting,
        "final": final,
        "inner": inner,
        "manifest": manifest,
        "audit": {
            **drift,
            "eligible_rows": len(eligible),
            "fitting_rows": len(fitting),
            "final_rows": len(final),
            "final_blocks": len(final_blocks),
            "final_blocks_at_least_20": sum(count >= 20 for count in final_blocks.values()),
            "fitting_final_group_overlap": 0,
            "fitting_final_block_overlap": 0,
            "outer_buffer": outer_buffer,
            "inner": [
                {
                    "fold": entry["fold"],
                    "fitting_rows": len(entry["fitting"]),
                    "validation_rows": len(entry["validation"]),
                    "buffer": entry["buffer"],
                }
                for entry in inner
            ],
            "manifest_sha256": digest,
            "fresh_final_evidence": market in NEW_FINAL_MARKETS,
        },
    }


def local_groups(rows, budget):
    by_block = defaultdict(set)
    for row in rows:
        by_block[spatial_block(row)].add(group_key(row))
    ordered = {
        block: sorted(
            groups,
            key=lambda group: hashlib.sha256(
                f"{SEED}:adapt:{group[0]}:{group[1]}".encode()
            ).hexdigest(),
        )
        for block, groups in by_block.items()
    }
    blocks = sorted(
        ordered,
        key=lambda block: hashlib.sha256(f"{SEED}:adapt:{block}".encode()).hexdigest(),
    )
    selected = set()
    while len(selected) < budget and any(ordered.values()):
        for block in blocks:
            if ordered[block] and len(selected) < budget:
                selected.add(ordered[block].pop(0))
    return [row for row in rows if group_key(row) in selected]


def protocols(splits):
    """Build private membership-only manifests; callers fit models on corresponding rows."""
    markets = sorted(splits)
    pooled_train = [row for market in markets for row in splits[market]["fitting"]]
    pooled_final = [row for market in NEW_FINAL_MARKETS for row in splits[market]["final"]]
    if {group_key(row) for row in pooled_train} & {group_key(row) for row in pooled_final}:
        raise ValueError("Pooled listing-group overlap")
    result = {
        "pooled": {"fitting": membership(pooled_train), "final": membership(pooled_final)},
        "leave_one_city_out": {},
        "limited_local": {},
    }
    for target in markets:
        others = [
            row for market in markets if market != target for row in splits[market]["fitting"]
        ]
        result["leave_one_city_out"][target] = {
            "fitting": membership(others),
            "target": splits[target]["manifest"]["eligible"],
            "fresh_final_evidence": False,
        }
        if target in NEW_FINAL_MARKETS:
            result["limited_local"][target] = {
                str(budget): {
                    "fitting": membership(others + local_groups(splits[target]["fitting"], budget)),
                    "final": splits[target]["manifest"]["final"],
                }
                for budget in LOCAL_BUDGETS
            }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output).resolve()
    expected = (ROOT / "data/research/multi-city/splits.json").resolve()
    if output != expected:
        parser.error("Split output must remain in ignored data/research/multi-city/splits.json")
    sources = json.loads((ROOT / "specs/003-multi-city-research/source-manifest.json").read_text())
    splits = {}
    normalized_hashes = {}
    for market, source in sorted(sources["markets"].items()):
        path = (
            ROOT
            / "data/research/multi-city"
            / market
            / source["snapshot_date"]
            / "normalized.jsonl"
        )
        with path.open(encoding="utf-8") as handle:
            rows = [json.loads(line) for line in handle]
        normalized_hashes[market] = hashlib.sha256(path.read_bytes()).hexdigest()
        splits[market] = split_market(rows, market)
    manifest = {
        "schema_version": 1,
        "source_manifest_sha256": hashlib.sha256(
            (ROOT / "specs/003-multi-city-research/source-manifest.json").read_bytes()
        ).hexdigest(),
        "split_rules_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "normalized_sha256": normalized_hashes,
        "seed": SEED,
        "block_km": BLOCK_KM,
        "buffer_m": BUFFER_M,
        "markets": {market: split["manifest"] for market, split in splits.items()},
        "protocols": protocols(splits),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    part = output.with_suffix(".json.part")
    try:
        part.write_text(
            json.dumps(manifest, sort_keys=True, separators=(",", ":")), encoding="utf-8"
        )
        part.replace(output)
    finally:
        part.unlink(missing_ok=True)
    print(json.dumps({market: split["audit"] for market, split in splits.items()}, sort_keys=True))


if __name__ == "__main__":
    main()
