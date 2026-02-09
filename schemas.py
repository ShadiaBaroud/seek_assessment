# schemas.py

from pydantic import BaseModel
from typing import Dict, List


class TopPeriod(BaseModel):
    """Represents a single half-hour period with its traffic count."""
    timestamp: str
    count: int


class LowestWindow(BaseModel):
    """Represents the lowest-traffic 1.5-hour window."""
    start: str
    end: str
    total_count: int


class TrafficMetrics(BaseModel):
    """Response schema returned by the /analyze endpoint."""
    total_count: int
    daily_counts: Dict[str, int]
    top_periods: List[TopPeriod]
    lowest_window: LowestWindow
