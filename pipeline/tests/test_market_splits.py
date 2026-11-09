"""Grouped market and geographic partition contracts."""

import json
from pathlib import Path

import pytest

from market_splits import (
    buffered_fitting,
    grouped_rows,
    local_groups,
    protocols,
    spatial_block,
    split_market,
)


def row(market, identifier, latitude, longitude, snapshot="2026-09-14"):
    return {
        "market_id": market,
        "snapshot_date": snapshot,
        "id": identifier,
        "latitude": latitude,
        "longitude": longitude,
    }


def test_blocks_are_stable_and_market_qualified():
    a = row("new-york-city", "1", 40.72, -73.99)
    assert spatial_block(a) == spatial_block({**a, "id": "2"})
    assert spatial_block(a) != spatial_block(row("los-angeles", "1", 34.05, -118.25))


def test_repeated_id_across_blocks_is_excluded_but_cross_market_id_is_distinct():
    rows = [
        row("new-york-city", "1", 40.70, -73.99),
        row("new-york-city", "1", 40.85, -73.99, "2026-12-01"),
        row("los-angeles", "1", 34.05, -118.25),
    ]
    kept, audit = grouped_rows(rows)
    assert len(kept) == 1 and kept[0]["market_id"] == "los-angeles"
    assert audit["geographic_drift_observations"] == 2


def test_buffer_excludes_nearby_and_repeated_ids():
    held = [row("nashville", "9", 36.10, -86.80)]
    fitting = [
        row("nashville", "9", 36.13, -86.80),
        row("nashville", "10", 36.101, -86.80),
        row("nashville", "11", 36.13, -86.80),
    ]
    kept, audit = buffered_fitting(fitting, held)
    assert [r["id"] for r in kept] == ["11"]
    assert audit["group_excluded"] == 1
    assert audit["buffer_excluded"] == 1


def test_small_unsupported_market_fails_instead_of_random_fallback():
    rows = [row("nashville", str(i), 36.10 + i * 0.00001, -86.80) for i in range(10)]
    with pytest.raises(ValueError, match="Insufficient"):
        split_market(rows, "nashville")


def synthetic_market(market):
    return [row(market, str(i), 35.0 + i * 0.05, -90.0) for i in range(60)]


def test_market_split_is_deterministic_grouped_and_block_disjoint():
    rows = synthetic_market("new-york-city")
    first = split_market(rows, "new-york-city", require_support=False)
    second = split_market(list(reversed(rows)), "new-york-city", require_support=False)
    assert first["audit"]["manifest_sha256"] == second["audit"]["manifest_sha256"]
    assert {r["id"] for r in first["fitting"]}.isdisjoint(r["id"] for r in first["final"])
    assert {spatial_block(r) for r in first["fitting"]}.isdisjoint(
        spatial_block(r) for r in first["final"]
    )
    for inner in first["inner"]:
        assert {r["id"] for r in inner["fitting"]}.isdisjoint(r["id"] for r in inner["validation"])


def test_transfer_and_local_protocols_keep_target_final_out_of_fitting():
    splits = {
        market: split_market(synthetic_market(market), market, require_support=False)
        for market in ("clark-county-nv", "new-york-city", "los-angeles", "nashville")
    }
    designs = protocols(splits)
    for target, design in designs["leave_one_city_out"].items():
        assert all(row["market_id"] != target for row in design["fitting"])
        assert all(row["market_id"] == target for row in design["target"])
    for target, budgets in designs["limited_local"].items():
        final = {(row["market_id"], row["id"]) for row in budgets["0"]["final"]}
        for budget, design in budgets.items():
            fitting = {(row["market_id"], row["id"]) for row in design["fitting"]}
            assert not final & fitting
            assert len(
                {row["id"] for row in design["fitting"] if row["market_id"] == target}
            ) <= int(budget)


def test_local_sample_balances_geographic_blocks_without_using_target():
    rows = synthetic_market("nashville")
    first = local_groups(rows, 5)
    second = local_groups(list(reversed(rows)), 5)
    assert {row["id"] for row in first} == {row["id"] for row in second}
    assert len({spatial_block(row) for row in first}) == 5


def test_public_split_support_has_no_membership_rows():
    root = Path(__file__).resolve().parents[2]
    report = json.loads((root / "specs/003-multi-city-research/split-support.json").read_text())
    assert report["repeatable_local_bytes"] is True
    for audit in report["markets"].values():
        assert "fitting" not in audit and "final" not in audit and "eligible" not in audit
        assert audit["fitting_final_group_overlap"] == 0
        assert audit["fitting_final_block_overlap"] == 0
