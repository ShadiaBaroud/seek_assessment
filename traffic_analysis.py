#!/usr/bin/env python3
"""
Traffic Analysis Core Logic.

Provides reusable analysis functions for both CLI usage
and FastAPI-based API services.
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, date
from typing import List, Dict
import logging

logger = logging.getLogger("traffic_api")


# -------------------------------------------------------------------
# Data model
# -------------------------------------------------------------------
@dataclass
class HalfHourRecord:
    timestamp: datetime
    count: int


# -------------------------------------------------------------------
# Parsing
# -------------------------------------------------------------------
def parse_records(data: str) -> List[HalfHourRecord]:
    """
    Parse raw traffic data into HalfHourRecord objects.

    Malformed lines, invalid timestamps, and negative counts
    are skipped with warnings logged.
    """
    records: List[HalfHourRecord] = []

    for line_num, line in enumerate(data.splitlines(), 1):
        line = line.strip()
        if not line:
            continue

        try:
            ts_str, count_str = line.split()
            count = int(count_str)

            if count < 0:
                logger.warning("Negative count skipped (line %d): %s", line_num, line)
                continue

            timestamp = datetime.fromisoformat(ts_str)
            records.append(HalfHourRecord(timestamp=timestamp, count=count))

        except Exception as e:
            logger.warning(
                "Malformed line skipped (line %d): %s (%s)",
                line_num,
                line,
                e,
            )

    return records


# -------------------------------------------------------------------
# Core analytics
# -------------------------------------------------------------------
def total_cars(records: List[HalfHourRecord]) -> int:
    """Return total number of cars."""
    return sum(r.count for r in records)


def cars_per_day(records: List[HalfHourRecord]) -> Dict[str, int]:
    """Aggregate total cars per day."""
    per_day: Dict[str, int] = {}

    for r in records:
        day = r.timestamp.date().isoformat()
        per_day[day] = per_day.get(day, 0) + r.count

    return per_day


def top_three_half_hours(records: List[HalfHourRecord]) -> List[Dict[str, int]]:
    """
    Return the top 3 half-hour periods by car count.
    Ties are broken by earliest timestamp.
    """
    top = sorted(
        records,
        key=lambda r: (-r.count, r.timestamp),
    )[:3]

    return [
        {"timestamp": r.timestamp.isoformat(), "count": r.count}
        for r in top
    ]


def min_1_5_hour_window(records: List[HalfHourRecord]) -> Dict[str, int]:
    """
    Return the contiguous 1.5-hour (3-record) window
    with the lowest total traffic.
    """
    if len(records) < 3:
        raise ValueError("At least 3 records are required to compute a 1.5-hour window")

    best_start = 0
    best_sum = sum(r.count for r in records[:3])
    current_sum = best_sum

    for start in range(1, len(records) - 2):
        current_sum -= records[start - 1].count
        current_sum += records[start + 2].count

        if current_sum < best_sum:
            best_sum = current_sum
            best_start = start

    window = records[best_start : best_start + 3]

    return {
        "start": window[0].timestamp.isoformat(),
        "end": window[-1].timestamp.isoformat(),
        "total_count": best_sum,
    }


# -------------------------------------------------------------------
# Public API entry point (used by FastAPI)
# -------------------------------------------------------------------
def analyze_traffic_file(data: str) -> Dict:
    """
    Analyze traffic data and return computed metrics.

    Raises ValueError for invalid or insufficient input.
    """
    records = parse_records(data)

    if not records:
        raise ValueError("No valid records found in input data")

    # Critical for correctness
    records.sort(key=lambda r: r.timestamp)

    return {
        "total_count": total_cars(records),
        "daily_counts": cars_per_day(records),
        "top_periods": top_three_half_hours(records),
        "lowest_window": min_1_5_hour_window(records),
    }
