"""Public result reduction keeps useful geography diagnostics without block labels."""

from summarize_market_results import compact_partition


def test_compact_partition_suppresses_geographic_labels():
    metric = {"n": 20, "mae_usd": 10.0, "rmse_usd": 12.0}
    partition = {
        "training_n": 100,
        "evaluation_n": 20,
        "metrics": {"room_median": metric, "ridge": metric},
        "negative_prediction_clamps": {"ridge": 0},
        "uncertainty": {"ridge": None},
        "subgroups": {
            "geographic_block": {
                "supported": {
                    "secret-market:123:456": {
                        "n": 20,
                        "metrics": {"room_median": metric, "ridge": metric},
                    }
                },
                "suppressed_groups": 1,
                "suppressed_observations": 2,
            },
            "market_id": {"supported": {}, "suppressed_groups": 0, "suppressed_observations": 0},
            "room_type": {"supported": {}, "suppressed_groups": 0, "suppressed_observations": 0},
            "property_group": {
                "supported": {},
                "suppressed_groups": 0,
                "suppressed_observations": 0,
            },
            "price_band": {"supported": {}, "suppressed_groups": 0, "suppressed_observations": 0},
        },
    }
    compact = compact_partition(partition, detailed=True)
    assert compact["geography"]["supported_blocks"] == 1
    assert compact["geography"]["suppressed_observations"] == 2
    assert "secret-market:123:456" not in str(compact)
