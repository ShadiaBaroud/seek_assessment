# SEEK AIPS Coding Challenge – Traffic Counter Analysis
Author: Shadia Baroud  
Date: 03 December 2025

## Overview
This solution processes half-hour traffic counter records and outputs:
1. The total number of cars recorded.
2. The number of cars per day.
3. The top three half-hour periods with the highest traffic.
4. The 1.5-hour window (three contiguous records) with the lowest total traffic.

## Approach
- The input file is parsed line-by-line.
- ISO 8601 timestamps are converted using `datetime.fromisoformat`.
- Day-level aggregation uses a dictionary keyed by date.
- Top 3 half-hours are identified via descending sort by count.
- The lowest 1.5-hour period is calculated using a sliding window over the original record order.
- Code is kept intentionally simple, readable and maintainable.
- Tested with Python 3.9+

## Running the Program
```bash
python traffic_analysis.py sample.txt

## Repository Link

This project is also available on GitHub:  
https://github.com/ShadiaBaroud/seek_assessment
