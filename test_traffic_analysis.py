from datetime import datetime
import pytest

from traffic_analysis import (
    analyze_traffic_file,
    parse_records,
    total_cars,
    cars_per_day,
    top_three_half_hours,
    min_1_5_hour_window,
    HalfHourRecord,
)


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------
def make_record(ts: str, count: int) -> HalfHourRecord:
    return HalfHourRecord(datetime.fromisoformat(ts), count)


# -------------------------------------------------------------------
# Parsing robustness
# -------------------------------------------------------------------
def test_robust_parsing_skips_malformed_lines():
    data = """
2021-12-01T05:00:00 5
BAD_TIMESTAMP 10
2021-12-01T05:30:00 20
2021-12-01T06:00:00 ABC
2021-12-01T06:30:00 15 extra
2021-12-01T07:00:00 20
"""
    records = parse_records(data)

    assert len(records) == 3
    assert [r.count for r in records] == [5, 20, 20]


def test_negative_counts_are_skipped():
    data = "2025-01-01T10:00 -5\n2025-01-01T10:30 3\n2025-01-01T11:00 2"
    with pytest.raises(ValueError):
        analyze_traffic_file(data)


# -------------------------------------------------------------------
# Core analytics
# -------------------------------------------------------------------
def test_total_cars():
    records = [
        make_record("2021-12-01T05:00:00", 5),
        make_record("2021-12-01T05:30:00", 10),
        make_record("2021-12-02T06:00:00", 3),
    ]
    assert total_cars(records) == 18


def test_cars_per_day():
    records = [
        make_record("2021-12-01T05:00:00", 5),
        make_record("2021-12-01T05:30:00", 10),
        make_record("2021-12-02T06:00:00", 3),
    ]
    per_day = cars_per_day(records)

    assert per_day["2021-12-01"] == 15
    assert per_day["2021-12-02"] == 3


def test_top_three_half_hours_with_tie_breaking():
    records = [
        make_record("2021-12-01T07:00:00", 25),
        make_record("2021-12-01T08:00:00", 15),
        make_record("2021-12-01T06:00:00", 15),
        make_record("2021-12-01T09:00:00", 10),
    ]

    top3 = top_three_half_hours(records)

    assert [r["count"] for r in top3] == [25, 15, 15]
    assert [r["timestamp"] for r in top3] == [
        "2021-12-01T07:00:00",
        "2021-12-01T06:00:00",
        "2021-12-01T08:00:00",
    ]


def test_min_1_5_hour_window_correctness():
    records = [
        make_record("2021-12-01T05:00:00", 5),
        make_record("2021-12-01T05:30:00", 10),
        make_record("2021-12-01T06:00:00", 3),
        make_record("2021-12-01T06:30:00", 20),
    ]

    result = min_1_5_hour_window(records)

    assert result["total_count"] == 18
    assert result["start"] == "2021-12-01T05:00:00"
    assert result["end"] == "2021-12-01T06:00:00"


# -------------------------------------------------------------------
# API-level behavior
# -------------------------------------------------------------------
def test_empty_input_raises_error():
    with pytest.raises(ValueError):
        analyze_traffic_file("")


def test_less_than_three_records_raises_error():
    data = "2021-12-01T05:00:00 5\n2021-12-01T05:30:00 10"
    with pytest.raises(ValueError):
        analyze_traffic_file(data)


def test_malformed_lines_do_not_break_analysis():
    data = "bad_line\n2025-01-01T10:30 3\n2025-01-01T11:00 2\n2025-01-01T11:30 1"
    result = analyze_traffic_file(data)
    assert result["total_count"] == 6
