"""
Core algorithms for the Ultrahuman Dashboard.

This module provides Python implementations of the key analytical functions
used by the dashboard. These mirror the JavaScript implementations in the
frontend and are used for testing and potential batch processing workflows.

Functions:
    calculate_circular_mean: Circular mean for time-of-day values crossing midnight.
    needs_circular_averaging: Detect if times cross the midnight boundary.
    process_sleep_graph_data: Derive SOL, WASO, and wake episodes from sleep segments.
    format_duration: Convert seconds to hours and minutes.
"""

import math


def needs_circular_averaging(times, time_type="bedtime"):
    """Detect if times cross the midnight boundary and need circular averaging.

    Args:
        times: List of time values in decimal hours (0-24).
        time_type: 'bedtime' or 'waketime' for context-specific logic.

    Returns:
        True if circular averaging is needed.
    """
    if len(times) < 2:
        return False

    min_time = min(times)
    max_time = max(times)

    if time_type in ("bedtime", "waketime"):
        return min_time < 6 and max_time > 18

    return False


def calculate_circular_mean(times, time_type="bedtime"):
    """Calculate the circular mean for time values that may cross midnight.

    Converts decimal-hour times to angular positions on a 24-hour circle,
    computes the vector mean using sin/cos components, and converts back
    to hours. This correctly handles the midnight boundary problem where
    arithmetic averaging fails (e.g. mean of 23:00 and 01:00 should be
    00:00, not 12:00).

    Args:
        times: List of time values in decimal hours (0-24).
        time_type: 'bedtime' or 'waketime' for context-specific logic.

    Returns:
        Circular mean in decimal hours (0-24).
    """
    if not times:
        return 0
    if len(times) == 1:
        return times[0]

    if not needs_circular_averaging(times, time_type):
        return sum(times) / len(times)

    sin_sum = 0.0
    cos_sum = 0.0

    for time in times:
        angle_rad = (time * 2 * math.pi) / 24
        sin_sum += math.sin(angle_rad)
        cos_sum += math.cos(angle_rad)

    mean_angle_rad = math.atan2(sin_sum, cos_sum)

    mean_time = (mean_angle_rad * 24) / (2 * math.pi)
    if mean_time < 0:
        mean_time += 24

    return mean_time


def process_sleep_graph_data(sleep_graph_data):
    """Derive sleep metrics from raw sleep stage segments.

    Processes the sleep_graph.data array from the Ultrahuman API to calculate:
    - Sleep stage durations (deep, light, REM, awake) in minutes
    - Sleep Onset Latency (SOL): duration of the first awake segment if at index 0
    - Wake After Sleep Onset (WASO): sum of all awake segments after the first
    - Wake episodes: count of awakenings after sleep onset
    - Derived total sleep: deep + light + REM (excludes awake time)

    Validation: SOL + WASO = total awake time, and
    deep + light + REM + awake = time in bed.

    Args:
        sleep_graph_data: List of dicts with 'type', 'start', and 'end' keys.
            type is one of: 'deep_sleep', 'light_sleep', 'rem_sleep', 'awake'.
            start and end are Unix timestamps in seconds.

    Returns:
        Dict with derived sleep metrics.
    """
    empty = {
        "has_data": False,
        "deep_sleep_min": 0,
        "light_sleep_min": 0,
        "rem_sleep_min": 0,
        "awake_min": 0,
        "sleep_onset_latency_min": 0,
        "waso_min": 0,
        "wake_episodes": 0,
        "total_sleep_derived_min": 0,
    }

    if not sleep_graph_data or not isinstance(sleep_graph_data, list) or len(sleep_graph_data) == 0:
        return empty

    deep_sleep_seconds = 0
    light_sleep_seconds = 0
    rem_sleep_seconds = 0
    awake_seconds = 0
    awake_segments = []

    for index, segment in enumerate(sleep_graph_data):
        duration = segment["end"] - segment["start"]
        seg_type = segment["type"]

        if seg_type == "deep_sleep":
            deep_sleep_seconds += duration
        elif seg_type == "light_sleep":
            light_sleep_seconds += duration
        elif seg_type == "rem_sleep":
            rem_sleep_seconds += duration
        elif seg_type == "awake":
            awake_seconds += duration
            awake_segments.append({"index": index, "duration": duration})

    # SOL: first awake segment if it is the very first segment (index 0)
    sol_seconds = 0
    if awake_segments and awake_segments[0]["index"] == 0:
        sol_seconds = awake_segments[0]["duration"]

    # WASO: all awake segments after the first
    waso_seconds = 0
    wake_episodes = 0
    if len(awake_segments) > 1:
        for seg in awake_segments[1:]:
            waso_seconds += seg["duration"]
        wake_episodes = len(awake_segments) - 1

    total_sleep_derived_seconds = deep_sleep_seconds + light_sleep_seconds + rem_sleep_seconds

    return {
        "has_data": True,
        "deep_sleep_min": round(deep_sleep_seconds / 60),
        "light_sleep_min": round(light_sleep_seconds / 60),
        "rem_sleep_min": round(rem_sleep_seconds / 60),
        "awake_min": round(awake_seconds / 60),
        "sleep_onset_latency_min": round(sol_seconds / 60),
        "waso_min": round(waso_seconds / 60),
        "wake_episodes": wake_episodes,
        "total_sleep_derived_min": round(total_sleep_derived_seconds / 60),
    }


def format_duration(seconds):
    """Convert a duration in seconds to hours and minutes.

    Args:
        seconds: Duration in seconds.

    Returns:
        Dict with 'formatted' string ("Xh Ym") and 'total_minutes' int.
    """
    if seconds is None or (isinstance(seconds, float) and math.isnan(seconds)):
        return {"formatted": "N/A", "total_minutes": 0}

    hours = int(seconds // 3600)
    minutes = round((seconds % 3600) / 60)
    return {
        "formatted": f"{hours}h {minutes}m",
        "total_minutes": round(seconds / 60),
    }
