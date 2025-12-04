# SEEK AIPS Coding Challenge – Traffic Counter Analysis
Author: Shadia Baroud
Date: 2025-12-03

## Overview

This solution provides four key analytical outputs from the half-hour traffic counter data:
1.  The total number of cars recorded (overall).
2.  The number of cars per day (sorted chronologically).
3.  The top three half-hour periods with the highest traffic.
4.  The 1.5-hour window (three contiguous records) with the lowest total traffic.

The solution is implemented in Python and developed to professional standards, prioritizing **correctness, robustness and performance.**

---

## Key Design Decisions and Performance

### 1. Guaranteed Correctness via Explicit Sorting (O(N log N))

The core challenge for the lowest 1.5-hour window is to find the minimum sum of **three chronologically contiguous** records.
* The `min_1_5_hour_window` function uses the high-performance **Sliding Window Technique** for $O(N)$ complexity.
* **Crucial Fix:** This $O(N)$ algorithm depends entirely on the input list being sorted by time. To guarantee correctness regardless of the input file's original order, the `main` function explicitly enforces a chronological sort on all records once after parsing (`records.sort(key=lambda r: r.timestamp)`). This pays the necessary $O(N \log N)$ cost upfront to ensure the subsequent $O(N)$ analysis is mathematically sound.

### 2. Low-Latency Top 3 Determination
* The `top_three_half_hours` function uses a single sort operation, but implements a composite key for **deterministic tie-breaking**.
* **Tie-Breaker Logic:** Records are sorted descending by `count`, and then ascending by `timestamp`. This ensures that in the event of equal car counts, the **earlier record wins the tie**, providing a stable and predictable output.

---

## Robustness and Professional Standards

### 1. Graceful Error Handling (`parse_file`)
The `parse_file` function is designed to be production-ready and resilient to real-world data issues:
* It uses a robust `try...except` block to catch and handle **malformed lines** (e.g., incorrect field count, non-numeric car count, bad timestamp format).
* **Error Reporting:** Malformed lines are skipped, and detailed warnings/errors are directed to **`sys.stderr`**. This keeps the program's required output (raw data) clean on `stdout` for downstream machine processing.

### 2. Code Quality and Fluency
* **Modern Python:** Leverages `@dataclass` for clear, boilerplate-free data modeling and uses extensive **type hinting** for improved static analysis and maintainability.
* **Documentation:** All core functions include docstrings explaining purpose, input, and output. Critical logic (like the sorting key and the sliding window) is commented to explain the *why* behind the complexity.

---

## Testing

The solution is accompanied by a comprehensive `test_traffic_analysis.py` file using `pytest` that covers:
* Basic correctness for all four analyses.
* **Edge Cases:** Empty files and records lists shorter than 3.
* **Critical Logic Validation:** Dedicated tests to prove the correctness of the **Top 3 tie-breaker** and to validate the failure-mode of the sliding window on unsorted data, justifying the fix in `main`.

---

## Running the Program

The program requires Python 3.9+ and can be run from the command line:

```bash
python traffic_analysis.py sample.txt


Repository Link
This project is also available on GitHub: https://github.com/ShadiaBaroud/seek_assessment
