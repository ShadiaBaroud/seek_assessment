import io
from datetime import datetime
from traffic_analysis import (
    HalfHourRecord,
    total_cars,
    cars_per_day,
    top_three_half_hours,
    min_1_5_hour_window,
)


def make_record(ts: str, count: int) -> HalfHourRecord:
    return HalfHourRecord(datetime.fromisoformat(ts), count)


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
    assert per_day[records[0].timestamp.date()] == 15
    assert per_day[records[2].timestamp.date()] == 3


def test_top_three_half_hours():
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
    # counts: [5, 10, 3, 20]
    records = [
        make_record("2021-12-01T05:00:00", 5),
        make_record("2021-12-01T05:30:00", 10),
        make_record("2021-12-01T06:00:00", 3),
        make_record("2021-12-01T06:30:00", 20),
    ]
    window = min_1_5_hour_window(records)
    # possible windows: [5+10+3=18], [10+3+20=33] -> first is minimal
    assert [r.count for r in window] == [5, 10, 3]
