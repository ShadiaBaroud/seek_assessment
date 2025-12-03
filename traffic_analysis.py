#!/usr/bin/env python3
from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import datetime, date
from typing import List, Tuple, Dict


@dataclass
class HalfHourRecord:
    timestamp: datetime
    count: int


def parse_file(path: str) -> List[HalfHourRecord]:
    records: List[HalfHourRecord] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            ts_str, count_str = line.split()
            ts = datetime.fromisoformat(ts_str)
            count = int(count_str)
            records.append(HalfHourRecord(timestamp=ts, count=count))
    return records


def total_cars(records: List[HalfHourRecord]) -> int:
    return sum(r.count for r in records)


def cars_per_day(records: List[HalfHourRecord]) -> Dict[date, int]:
    per_day: Dict[date, int] = {}
    for r in records:
        d = r.timestamp.date()
        per_day[d] = per_day.get(d, 0) + r.count
    return per_day


def top_three_half_hours(records: List[HalfHourRecord]) -> List[HalfHourRecord]:
    return sorted(
        records,
        key=lambda r: (-r.count, r.timestamp),
    )[:3]


def min_1_5_hour_window(records: List[HalfHourRecord]) -> List[HalfHourRecord]:
    """
    Returns the 3 contiguous records (by input order) with the smallest sum of counts.
    """
    if len(records) < 3:
        # With fewer than 3 records, just return all of them
        return records[:]

    best_start = 0
    best_sum = sum(r.count for r in records[0:3])

    current_sum = best_sum
    for start in range(1, len(records) - 2):
        # Slide window by 1: remove previous, add new
        current_sum -= records[start - 1].count
        current_sum += records[start + 2].count

        if current_sum < best_sum:
            best_sum = current_sum
            best_start = start

    return records[best_start : best_start + 3]


def format_record(r: HalfHourRecord) -> str:
    return f"{r.timestamp.isoformat()} {r.count}"


def main(argv: List[str]) -> int:
    if len(argv) != 2:
        print(f"Usage: {argv[0]} <input_file>", file=sys.stderr)
        return 1

    input_path = argv[1]
    records = parse_file(input_path)

    # 1) Total cars
    total = total_cars(records)
    print(total)

    # 2) Cars per day (sorted by date)
    per_day = cars_per_day(records)
    for d in sorted(per_day.keys()):
        print(f"{d.isoformat()} {per_day[d]}")

    # 3) Top 3 half-hours
    top3 = top_three_half_hours(records)
    for r in top3:
        print(format_record(r))

    # 4) 1.5 hour period with least cars (3 contiguous records)
    window = min_1_5_hour_window(records)
    for r in window:
        print(format_record(r))

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
