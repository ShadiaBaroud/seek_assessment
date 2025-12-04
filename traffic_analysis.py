#!/usr/bin/env python3
"""
Traffic Analysis Program.

This script reads a file of half-hour car counts and performs four analyses:
1. Total cars recorded.
2. Total cars per day.
3. Top 3 half-hour periods with the highest traffic.
4. The 1.5-hour period (3 contiguous records) with the lowest total traffic.

It prioritizes correctness, high performance (O(N) algorithms) and robustness 
by handling file parsing errors gracefully.
"""

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
    """
    Reads the input file, parses lines into HalfHourRecord objects, and handles 
    malformed lines (bad format, non-numeric data) gracefully by logging errors to stderr.
    """
    records: List[HalfHourRecord] = []
    with open(path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            try:
                parts = line.split()
                if len(parts) != 2:
                    print(f"Warning: Line {line_num} has incorrect number of fields (expected 2): '{line}'. Skipping.", file=sys.stderr)
                    continue
                    
                ts_str, count_str = parts
                
                ts = datetime.fromisoformat(ts_str)
                count = int(count_str)
                
                records.append(HalfHourRecord(timestamp=ts, count=count))

            except ValueError as e:
                # Catches bad timestamps (not ISO) or bad counts (not integer)
                print(f"Error: Line {line_num} failed parsing ('{line}'): {e}. Skipping.", file=sys.stderr)
            except Exception as e:
                # Catch any other unexpected error
                print(f"Fatal Error: Line {line_num} failed with unexpected error: {e}. Skipping.", file=sys.stderr)

    return records


def total_cars(records: List[HalfHourRecord]) -> int:
    """Calculates the sum of all car counts across all records."""
    return sum(r.count for r in records)


def cars_per_day(records: List[HalfHourRecord]) -> Dict[date, int]:
    """Aggregates car counts, summing totals for each day."""
    per_day: Dict[date, int] = {}
    for r in records:
        d = r.timestamp.date()
        per_day[d] = per_day.get(d, 0) + r.count
    return per_day


def top_three_half_hours(records: List[HalfHourRecord]) -> List[HalfHourRecord]:
    """
    Returns the top 3 HalfHourRecord objects with the highest car counts.
    Ties are broken by the earliest timestamp.
    """
    return sorted(
        records,
        # Sorts descending by count (-r.count) and ascending by timestamp (r.timestamp) as a tie-breaker.
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
    # Initialize the first window sum
    best_sum = sum(r.count for r in records[0:3])

    current_sum = best_sum
    # Iterate through possible start indices, stopping 2 records before the end
    for start in range(1, len(records) - 2):
        # Slide window by 1: remove previous, add new
        current_sum -= records[start - 1].count # Remove count of the record leaving the window
        current_sum += records[start + 2].count # Add count of the new record entering the window

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

    if not records:
        # No data case: print zeros or a clear message
        #print(0)
        # Optionally: you can print nothing else or a note:
        print("No records found in input file.")
        return 0
    
    # SENIOR FIX: Ensure the list is chronologically sorted for correctness, 
    # which is mandatory for the min_1_5_hour_window contiguous index check.
    # O(N log N) cost is paid once here.
    records.sort(key=lambda r: r.timestamp)


    # 1) Total cars
    #print("--- 1. Total Cars ---", file=sys.stderr)
    #total = total_cars(records)
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
    sys.exit(main(sys.argv))
