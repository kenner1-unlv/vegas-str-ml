import copy
import json
import shutil
import sys

import pytest
import select_comps as module
from audit_comps import coverage
from normalize_research import build
from select_comps import select_comps
from test_normalize_research import fixture_inputs


def row(identifier, **overrides):
    result = {
        "id": str(identifier),
        "snapshot_date": "2026-09-20",
        "in_usable_cohort": True,
        "property_group": "house_like",
        "room_type": "entire_home_apt",
        "stay_cohort": "1_27_nights",
        "bedrooms": 3,
        "accommodates": 6,
        "asking_price_usd": 200.0,
        "geography": {"zcta": "89146", "status": "assigned", "near_boundary": False},
    }
    result.update(overrides)
    return result


def test_default_membership_inclusive_bedrooms_and_price_invariance():
    rows = [row("9223372036854775807"), row(2, bedrooms=2), row(3, bedrooms=4), row(4, bedrooms=5)]
    result = select_comps(rows, rows[0]["id"])
    assert result["matched_ids"] == ["2", "3"]
    assert result["exclusions"] == {"subject": 1, "bedrooms_outside_tolerance": 1}
    changed = copy.deepcopy(rows)
    for i, item in enumerate(changed):
        item["asking_price_usd"] = 10000 + i
    assert select_comps(changed, rows[0]["id"])["matched_ids"] == result["matched_ids"]
    assert result["summary"]["median_asking_price_usd"] is None


@pytest.mark.parametrize(
    "field,value,reason",
    [
        ("property_group", "hotel_resort", "different_property_group"),
        ("room_type", "private_room", "different_room_type"),
        ("stay_cohort", "28_plus_nights", "different_stay_cohort"),
        ("property_group", "unknown", "unsupported_property_group"),
        ("property_group", "other", "unsupported_property_group"),
        ("room_type", "unknown", "unknown_room_type"),
        ("stay_cohort", "unknown", "unknown_stay_cohort"),
        ("bedrooms", None, "unknown_bedrooms"),
        ("geography", None, "unknown_geography"),
        (
            "geography",
            {"zcta": "89102", "status": "assigned", "near_boundary": False},
            "different_zcta",
        ),
    ],
)
def test_each_matching_dimension_and_unknown_exclusions(field, value, reason):
    result = select_comps([row(1), row(2, **{field: value})], "1")
    assert result["matched_count"] == 0
    assert result["exclusions"][reason] == 1


def test_capacity_optional_and_exact_zero_tolerances():
    rows = [row(1), row(2, accommodates=None), row(3, accommodates=8), row(4, bedrooms=4)]
    assert select_comps(rows, "1")["matched_count"] == 3
    result = select_comps(rows, "1", bedroom_tolerance=0, capacity_tolerance=2)
    assert result["matched_ids"] == ["3"]
    assert result["exclusions"]["unknown_capacity"] == 1
    assert select_comps(rows, "1", capacity_tolerance=0)["matched_ids"] == ["4"]


def test_support_floor_excludes_subject_and_reports_descriptive_differences():
    rows = [row(1, asking_price_usd=250)] + [row(i, asking_price_usd=200) for i in range(2, 22)]
    supported = select_comps(rows, "1")
    assert supported["matched_count"] == 20
    assert supported["support"] == "supported"
    assert supported["summary"] == {
        "median_asking_price_usd": 200,
        "subject_difference_usd": 50,
        "subject_difference_percent": 25,
    }
    thin = select_comps(rows[:-1], "1")
    assert thin["matched_count"] == 19
    assert thin["support"] == "thin_sample"
    assert all(value is None for value in thin["summary"].values())


def test_boundary_sensitivity_is_explicit_never_changes_geography():
    geo = {"zcta": "89146", "status": "assigned", "near_boundary": True}
    rows = [row(1), row(2, geography=geo), row(3)]
    included = select_comps(rows, "1")
    assert included["matched_near_boundary_count"] == 1
    assert included["matches_without_boundary_sensitive"] == 1
    excluded = select_comps(rows, "1", edge_policy="exclude")
    assert excluded["matched_ids"] == ["3"]
    assert excluded["exclusions"]["near_boundary"] == 1
    rows[0]["geography"] = geo
    assert select_comps(rows, "1", edge_policy="exclude")["support"] == "unsupported_subject"


@pytest.mark.parametrize(
    "overrides,reason",
    [
        ({"bedrooms": None}, "unknown_bedrooms"),
        ({"property_group": "other"}, "unsupported_property_group"),
        ({"geography": None}, "unknown_geography"),
        ({"stay_cohort": "unknown"}, "unknown_stay_cohort"),
        (
            {"in_usable_cohort": False, "asking_price_usd": None, "geography": None},
            "outside_usable_cohort",
        ),
    ],
)
def test_unsupported_subject_has_reasons_not_fallback(overrides, reason):
    result = select_comps([row(1, **overrides), row(2)], "1")
    assert result["support"] == "unsupported_subject"
    assert reason in result["subject_limitations"]
    assert result["matched_ids"] == []
    assert all(value is None for value in result["summary"].values())


def test_exclusion_funnel_counts_once_and_studio_is_not_unknown():
    rows = [
        row(1, bedrooms=0),
        row(2, bedrooms=0),
        row(3, bedrooms=1),
        row(4, property_group="other", bedrooms=None),
        row(5, in_usable_cohort=False, asking_price_usd=None, geography=None),
    ]
    result = select_comps(rows, "1", bedroom_tolerance=0)
    assert result["matched_ids"] == ["2"]
    assert result["input_rows"] == result["matched_count"] + sum(result["exclusions"].values())
    assert "unknown_bedrooms" not in result["exclusions"]


@pytest.mark.parametrize(
    "options",
    [
        {"bedroom_tolerance": -1},
        {"bedroom_tolerance": True},
        {"capacity_tolerance": 1.5},
        {"edge_policy": "widen"},
    ],
)
def test_bad_request_rejected(options):
    with pytest.raises(ValueError):
        select_comps([row(1)], "1", **options)


def test_duplicate_or_unknown_ids_fail():
    with pytest.raises(ValueError):
        select_comps([row(1), row(1)], "1")
    with pytest.raises(ValueError):
        select_comps([row(1)], "2")


def test_subject_capacity_required_only_when_constrained():
    rows = [row(1, accommodates=None), row(2)]
    assert select_comps(rows, "1")["matched_count"] == 1
    assert (
        "unknown_capacity" in select_comps(rows, "1", capacity_tolerance=1)["subject_limitations"]
    )


@pytest.mark.parametrize("change", ["rows", "rules", "hash", "snapshot"])
def test_verified_loader_rejects_tampering(tmp_path, monkeypatch, change):
    raw, public, _ = fixture_inputs(tmp_path)
    snapshot = "2026-09-20"
    raw_target = tmp_path / "data/raw" / snapshot
    public_target = tmp_path / "web/static/data" / snapshot
    shutil.copytree(raw, raw_target)
    shutil.copytree(public, public_target)
    path = tmp_path / "data/research" / snapshot / "normalized.json"
    census = public / "census.geojson"
    build(raw_target, public_target, snapshot, path, census_source=census)
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module, "build", lambda *args: build(*args, census_source=census))
    verified, _ = module.load_verified(snapshot)
    assert len(verified["rows"]) == 2
    modified = copy.deepcopy(verified)
    if change == "rows":
        modified["rows"][0]["bedrooms"] = 999
    elif change == "rules":
        modified["audit"]["rules_version"] = "old"
    elif change == "hash":
        modified["audit"]["provenance"]["geography_sha256"] = "tampered"
    else:
        modified["audit"]["snapshot_date"] = "2020-01-01"
    path.write_text(json.dumps(modified))
    previous = path.read_bytes()
    with pytest.raises(ValueError):
        module.load_verified(snapshot)
    assert path.read_bytes() == previous
    assert not list(path.parent.glob("comps-verify-*"))


@pytest.mark.parametrize(
    "value",
    [
        "web/static/data/result.json",
        "data/raw/result.json",
        "data/research/normalized.json",
        "data/research/Normalized.JSON",
        "data/research/result.csv",
    ],
)
def test_private_output_boundary(tmp_path, monkeypatch, value):
    monkeypatch.setattr(module, "ROOT", tmp_path)
    with pytest.raises(ValueError):
        module.output_path(tmp_path / value)


def test_cli_aggregate_and_failure_preservation(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(module, "ROOT", tmp_path)
    dataset = {"rows": [row(1), row(2)], "audit": {"provenance": {}}}
    monkeypatch.setattr(module, "load_verified", lambda snapshot: (dataset, "validated"))
    target = tmp_path / "data/research/comps.json"
    monkeypatch.setattr(
        sys,
        "argv",
        ["select_comps", "--snapshot", "2026-09-20", "--subject-id", "1", "--output", str(target)],
    )
    module.main()
    printed = json.loads(capsys.readouterr().out)
    assert "subject_id" not in printed and "matched_ids" not in printed
    assert json.loads(target.read_text())["matched_ids"] == ["2"]
    previous = target.read_bytes()

    def failure(snapshot):
        raise ValueError("stale input")

    monkeypatch.setattr(module, "load_verified", failure)
    with pytest.raises(SystemExit):
        module.main()
    assert target.read_bytes() == previous


@pytest.mark.parametrize(
    "overrides",
    [
        {"id": 1},
        {"bedrooms": True},
        {"accommodates": -1},
        {"asking_price_usd": float("nan")},
        {"geography": {"zcta": "bad", "status": "assigned", "near_boundary": False}},
    ],
)
def test_bad_normalized_values_rejected(overrides):
    with pytest.raises(ValueError):
        select_comps([row(1, **overrides)], "1")


def test_ambiguous_geography_and_room_support():
    rows = [row(1), row(2, geography={"zcta": None, "status": "ambiguous", "near_boundary": True})]
    assert select_comps(rows, "1")["exclusions"]["unknown_geography"] == 1
    assert (
        "unknown_room_type"
        in select_comps([row(1, room_type="unknown")], "1")["subject_limitations"]
    )


@pytest.mark.parametrize("policy", ["include", "exclude"])
def test_coverage_index_matches_direct_selector(policy):
    rows = [
        row(
            i,
            bedrooms=i % 4,
            geography={"zcta": "89146", "status": "assigned", "near_boundary": i % 5 == 0},
        )
        for i in range(1, 51)
    ]
    rows += [row(51, property_group="unknown"), row(52, bedrooms=None)]
    expected = {"supported": 0, "thin_sample": 0, "unsupported_subject": 0}
    for subject in rows:
        result = select_comps(rows, subject["id"], edge_policy=policy)
        expected[result["support"]] += 1
    assert coverage(rows, policy) == expected
