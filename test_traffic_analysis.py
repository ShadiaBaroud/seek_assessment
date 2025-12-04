import io
from datetime import datetime, date
from traffic_analysis import (
    HalfHourRecord,
    total_cars,
    cars_per_day,
    top_three_half_hours,
    min_1_5_hour_window,
    parse_file,
)


def make_record(ts: str, count: int) -> HalfHourRecord:
    """Helper function to create a HalfHourRecord from a string timestamp."""
    return HalfHourRecord(datetime.fromisoformat(ts), count)


# --- CRITICAL TEST CASES (VALIDATING ROBUSTNESS & ASSUMPTIONS) ---

def test_robust_parsing(tmp_path):
    """
    Verifies that parse_file can gracefully handle and skip malformed input lines
    (bad timestamp, non-integer count, wrong field count) without crashing, 
    returning only the valid records.
    """
    input_content = """
2021-12-01T05:00:00 5
BAD_TIMESTAMP 10             # Expected to be skipped (bad format)
2021-12-01T05:30:00 20
2021-12-01T06:00:00 ABC      # Expected to be skipped (bad count)
2021-12-01T06:30:00 15 extra # Expected to be skipped (wrong field count)
2021-12-01T07:00:00 20
"""
    # Write content to a temporary file
    test_file = tmp_path / "test_robust.txt"
    test_file.write_text(input_content)

    records = parse_file(str(test_file))
    
    # Assert that only the 3 valid records were returned
    assert len(records) == 3
    assert records[0].count == 5
    assert records[1].count == 20
    assert records[2].count == 20


def test_top_three_half_hours_with_tie():
    """
    Verifies that when counts are equal (a tie), the earlier timestamp is ranked higher.
    This validates the sorting key: (-count, timestamp).
    """
    records_tie = [
        make_record("2021-12-01T07:00:00", 25),  # 1st place
        make_record("2021-12-01T08:00:00", 15),  # Tie for 2nd/3rd, later timestamp (3rd place)
        make_record("2021-12-01T06:00:00", 15),  # Tie for 2nd/3rd, earlier timestamp (2nd place)
        make_record("2021-12-01T09:00:00", 10),  # Not in top 3
    ]
    
    top3 = top_three_half_hours(records_tie)
    
    # Expected order: 25@07:00 (highest), 15@06:00 (earlier time wins tie), 15@08:00 (loses tie)
    expected_timestamps = [
        datetime(2021, 12, 1, 7, 0, 0),
        datetime(2021, 12, 1, 6, 0, 0),
        datetime(2021, 12, 1, 8, 0, 0),
    ]
    
    actual_timestamps = [r.timestamp for r in top3]
    assert actual_timestamps == expected_timestamps


def test_min_1_5_hour_window_unsorted_input():
    """
    VALIDATION OF MAIN FIX: This test confirms that min_1_5_hour_window relies ONLY on 
    the list index order for contiguity. This justifies the necessity of explicitly 
    sorting the list in the main() function before calling this analysis.
    """
    # Real chronological order (by timestamp) is 5, 10, 3, 20
    # Input is deliberately unsorted, forcing the sliding window to use the list index order.
    records = [
        make_record("2021-12-01T06:00:00", 3),  # Index 0
        make_record("2021-12-01T05:00:00", 5),  # Index 1
        make_record("2021-12-01T06:30:00", 20), # Index 2
        make_record("2021-12-01T05:30:00", 10), # Index 3
    ]
    
    window = min_1_5_hour_window(records)
    
    # Expected window based on *index*: [3 + 5 + 20 = 28] -> minimal window by index
    assert [r.count for r in window] == [3, 5, 20]
    # The timestamps here are NOT contiguous in time, which proves the function is index-dependent.
    assert window[0].timestamp == datetime(2021, 12, 1, 6, 0, 0)
    
# --- GENERAL TEST CASES ---

def test_total_cars():
    """Verifies the correct aggregation of all car counts."""
    records = [
        make_record("2021-12-01T05:00:00", 5),
        make_record("2021-12-01T05:30:00", 10),
        make_record("2021-12-02T06:00:00", 3),
    ]
    assert total_cars(records) == 18


def test_cars_per_day():
    """Verifies the correct summation of counts across different days."""
    records = [
        make_record("2021-12-01T05:00:00", 5),
        make_record("2021-12-01T05:30:00", 10),
        make_record("2021-12-02T06:00:00", 3),
    ]
    per_day = cars_per_day(records)
    assert per_day[records[0].timestamp.date()] == 15
    assert per_day[records[2].timestamp.date()] == 3


def test_top_three_half_hours():
    """Verifies the selection of the top 3 highest counts."""
    records = [
        make_record("2021-12-01T05:00:00", 5),
        make_record("2021-12-01T05:30:00", 20),
        make_record("2021-12-01T06:00:00", 15),
        make_record("2021-12-01T06:30:00", 8),
    ]
    top3 = top_three_half_hours(records)
    counts = [r.count for r in top3]
    assert counts == [20, 15, 8]


def test_min_1_5_hour_window():
    """Verifies the O(N) sliding window correctly identifies the minimal sum contiguous window."""
    # counts: [5, 10, 3, 20] -> minimal window is [5, 10, 3] sum=18
    records = [
        make_record("2021-12-01T05:00:00", 5),
        make_record("2021-12-01T05:30:00", 10),
        make_record("2021-12-01T06:00:00", 3),
        make_record("2021-12-01T06:30:00", 20),
    ]
    window = min_1_5_hour_window(records)
    assert [r.count for r in window] == [5, 10, 3]

# --- EDGE CASES ---

def test_empty_records():
    """Tests all functions with an empty input list."""
    records = []
    assert total_cars(records) == 0
    assert cars_per_day(records) == {}
    assert top_three_half_hours(records) == []
    assert min_1_5_hour_window(records) == []

def test_less_than_three_records():
    """Tests functions when the input list size is insufficient for a 3-unit window."""
    records = [
        make_record("2021-12-01T05:00:00", 5),
        make_record("2021-12-01T05:30:00", 10),
    ]

    # top3 returns all records, sorted
    top3 = top_three_half_hours(records)
    assert [r.count for r in top3] == [10, 5]

    # min_1_5_hour_window returns all records since a 3-unit window is impossible
    window = min_1_5_hour_window(records)
    assert [r.count for r in window] == [5, 10]

def test_multiple_days_per_day_aggregation():
    """Tests aggregation across two distinct days."""
    records = [
        make_record("2021-12-01T05:00:00", 5),
        make_record("2021-12-01T05:30:00", 10), # Day 1 total: 15
        make_record("2021-12-02T06:00:00", 3),
        make_record("2021-12-02T06:30:00", 7),  # Day 2 total: 10
    ]
    per_day = cars_per_day(records)
    assert per_day[date(2021, 12, 1)] == 15
    assert per_day[date(2021, 12, 2)] == 10