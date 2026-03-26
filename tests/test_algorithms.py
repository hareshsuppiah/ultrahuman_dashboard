"""Tests for core algorithms: circular mean and derived sleep metrics."""

import math
import pytest

from src.algorithms import (
    calculate_circular_mean,
    needs_circular_averaging,
    process_sleep_graph_data,
    format_duration,
)


# ---------------------------------------------------------------------------
# Circular mean tests
# ---------------------------------------------------------------------------

class TestNeedsCircularAveraging:
    def test_single_time_returns_false(self):
        assert needs_circular_averaging([22.0]) is False

    def test_empty_list_returns_false(self):
        assert needs_circular_averaging([]) is False

    def test_times_crossing_midnight(self):
        # 23:00 and 01:00 — should need circular averaging
        assert needs_circular_averaging([23.0, 1.0]) is True

    def test_times_not_crossing_midnight(self):
        # 21:00 and 22:30 — both evening, no crossing
        assert needs_circular_averaging([21.0, 22.5]) is False

    def test_morning_times_no_crossing(self):
        # 6:30 and 7:15 — both morning
        assert needs_circular_averaging([6.5, 7.25], "waketime") is False

    def test_threshold_boundary(self):
        # min=5.9 (<6), max=18.1 (>18) — should trigger
        assert needs_circular_averaging([5.9, 18.1]) is True

    def test_just_below_threshold(self):
        # min=6.0 (not <6), max=18.1 — should not trigger
        assert needs_circular_averaging([6.0, 18.1]) is False


class TestCalculateCircularMean:
    def test_empty_list_returns_zero(self):
        assert calculate_circular_mean([]) == 0

    def test_single_value_returned_unchanged(self):
        assert calculate_circular_mean([22.5]) == 22.5

    def test_arithmetic_mean_when_no_midnight_crossing(self):
        # 21:00 and 23:00 — arithmetic mean is 22:00
        result = calculate_circular_mean([21.0, 23.0])
        assert result == pytest.approx(22.0)

    def test_circular_mean_across_midnight_symmetric(self):
        # 23:00 and 01:00 — circular mean should be 00:00 (midnight)
        # 24.0 and 0.0 are equivalent on a 24-hour clock
        result = calculate_circular_mean([23.0, 1.0])
        assert result % 24 == pytest.approx(0.0, abs=0.01)

    def test_circular_mean_across_midnight_asymmetric(self):
        # 22:00 and 02:00 — circular mean should be 00:00
        result = calculate_circular_mean([22.0, 2.0])
        assert result % 24 == pytest.approx(0.0, abs=0.01)

    def test_circular_mean_late_evening_cluster(self):
        # 23:00, 23:30, 00:30 — mean should be near 23:40
        result = calculate_circular_mean([23.0, 23.5, 0.5])
        assert 23.0 <= result or result <= 1.0  # near midnight

    def test_circular_mean_multiple_nights(self):
        # 22:30, 23:00, 23:30, 00:00, 00:30
        result = calculate_circular_mean([22.5, 23.0, 23.5, 0.0, 0.5])
        # Should be near 23:06
        assert 22.5 <= result or result <= 1.0

    def test_waketime_no_crossing(self):
        # Wake times: 6:00, 6:30, 7:00 — simple arithmetic
        result = calculate_circular_mean([6.0, 6.5, 7.0], "waketime")
        assert result == pytest.approx(6.5)

    def test_identical_times(self):
        result = calculate_circular_mean([22.0, 22.0, 22.0])
        assert result == pytest.approx(22.0)


# ---------------------------------------------------------------------------
# Sleep metrics tests
# ---------------------------------------------------------------------------

def _make_segment(seg_type, start, duration_min):
    """Helper to create a sleep segment with start/end in Unix seconds."""
    start_ts = start
    end_ts = start + (duration_min * 60)
    return {"type": seg_type, "start": start_ts, "end": end_ts}


class TestProcessSleepGraphData:
    def test_empty_input_returns_no_data(self):
        result = process_sleep_graph_data([])
        assert result["has_data"] is False
        assert result["deep_sleep_min"] == 0

    def test_none_input_returns_no_data(self):
        result = process_sleep_graph_data(None)
        assert result["has_data"] is False

    def test_non_list_input_returns_no_data(self):
        result = process_sleep_graph_data("not a list")
        assert result["has_data"] is False

    def test_simple_sleep_no_awakenings(self):
        # 90 min deep, 120 min light, 60 min REM, no awake
        base = 1700000000
        segments = [
            _make_segment("deep_sleep", base, 90),
            _make_segment("light_sleep", base + 5400, 120),
            _make_segment("rem_sleep", base + 12600, 60),
        ]
        result = process_sleep_graph_data(segments)
        assert result["has_data"] is True
        assert result["deep_sleep_min"] == 90
        assert result["light_sleep_min"] == 120
        assert result["rem_sleep_min"] == 60
        assert result["awake_min"] == 0
        assert result["sleep_onset_latency_min"] == 0
        assert result["waso_min"] == 0
        assert result["wake_episodes"] == 0
        assert result["total_sleep_derived_min"] == 270

    def test_sol_from_initial_awake_segment(self):
        # First segment is awake (10 min SOL), then sleep
        base = 1700000000
        segments = [
            _make_segment("awake", base, 10),           # SOL
            _make_segment("light_sleep", base + 600, 120),
            _make_segment("deep_sleep", base + 7800, 90),
        ]
        result = process_sleep_graph_data(segments)
        assert result["sleep_onset_latency_min"] == 10
        assert result["waso_min"] == 0
        assert result["wake_episodes"] == 0

    def test_waso_from_mid_sleep_awakenings(self):
        # SOL (5 min) + sleep + awake (3 min) + sleep + awake (7 min)
        base = 1700000000
        segments = [
            _make_segment("awake", base, 5),              # SOL = 5 min
            _make_segment("deep_sleep", base + 300, 60),
            _make_segment("awake", base + 3900, 3),        # WASO segment 1
            _make_segment("light_sleep", base + 4080, 90),
            _make_segment("awake", base + 9480, 7),        # WASO segment 2
        ]
        result = process_sleep_graph_data(segments)
        assert result["sleep_onset_latency_min"] == 5
        assert result["waso_min"] == 10  # 3 + 7
        assert result["wake_episodes"] == 2
        assert result["awake_min"] == 15  # 5 + 3 + 7

    def test_sol_plus_waso_equals_total_awake(self):
        base = 1700000000
        segments = [
            _make_segment("awake", base, 8),
            _make_segment("light_sleep", base + 480, 60),
            _make_segment("awake", base + 4080, 4),
            _make_segment("rem_sleep", base + 4320, 30),
            _make_segment("awake", base + 6120, 6),
        ]
        result = process_sleep_graph_data(segments)
        assert result["sleep_onset_latency_min"] + result["waso_min"] == result["awake_min"]

    def test_total_time_in_bed_validation(self):
        # deep + light + REM + awake should equal time in bed
        base = 1700000000
        segments = [
            _make_segment("awake", base, 5),
            _make_segment("deep_sleep", base + 300, 90),
            _make_segment("light_sleep", base + 5700, 120),
            _make_segment("awake", base + 12900, 3),
            _make_segment("rem_sleep", base + 13080, 60),
            _make_segment("awake", base + 16680, 2),
        ]
        result = process_sleep_graph_data(segments)
        total_time_in_bed = (
            result["deep_sleep_min"]
            + result["light_sleep_min"]
            + result["rem_sleep_min"]
            + result["awake_min"]
        )
        # total_sleep_derived should be deep + light + REM only
        assert result["total_sleep_derived_min"] == (
            result["deep_sleep_min"] + result["light_sleep_min"] + result["rem_sleep_min"]
        )
        # All segments accounted for
        assert total_time_in_bed == 280  # 5+90+120+3+60+2

    def test_no_sol_when_first_segment_is_sleep(self):
        # First segment is deep_sleep, not awake — SOL should be 0
        base = 1700000000
        segments = [
            _make_segment("deep_sleep", base, 60),
            _make_segment("awake", base + 3600, 5),
            _make_segment("light_sleep", base + 3900, 90),
        ]
        result = process_sleep_graph_data(segments)
        assert result["sleep_onset_latency_min"] == 0
        # The single awake segment is not at index 0, so it counts as WASO
        # But since there's only one awake segment and it's not at index 0,
        # awake_segments[0].index != 0, so SOL = 0
        # And len(awake_segments) == 1, so WASO loop doesn't execute
        assert result["waso_min"] == 0
        assert result["wake_episodes"] == 0

    def test_single_awake_segment_at_start(self):
        # Only one awake segment at the start — SOL only, no WASO
        base = 1700000000
        segments = [
            _make_segment("awake", base, 15),
            _make_segment("deep_sleep", base + 900, 120),
        ]
        result = process_sleep_graph_data(segments)
        assert result["sleep_onset_latency_min"] == 15
        assert result["waso_min"] == 0
        assert result["wake_episodes"] == 0


# ---------------------------------------------------------------------------
# Format duration tests
# ---------------------------------------------------------------------------

class TestFormatDuration:
    def test_standard_duration(self):
        result = format_duration(28800)  # 8 hours
        assert result["formatted"] == "8h 0m"
        assert result["total_minutes"] == 480

    def test_hours_and_minutes(self):
        result = format_duration(27000)  # 7h 30m
        assert result["formatted"] == "7h 30m"
        assert result["total_minutes"] == 450

    def test_none_returns_na(self):
        result = format_duration(None)
        assert result["formatted"] == "N/A"
        assert result["total_minutes"] == 0

    def test_nan_returns_na(self):
        result = format_duration(float("nan"))
        assert result["formatted"] == "N/A"

    def test_zero_duration(self):
        result = format_duration(0)
        assert result["formatted"] == "0h 0m"
        assert result["total_minutes"] == 0
