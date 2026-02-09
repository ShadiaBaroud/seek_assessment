# SEEK AIPS Coding Challenge – Traffic Counter Analysis

**Author:** Dr. Shadia Yahya Baroud  
**Date:** 2025-12-03  

---

## Overview

This project implements a robust analytical engine for processing **half-hourly traffic counter data**.  
It computes a set of core metrics required for traffic analysis while ensuring **correctness, determinism, and production-readiness**.

The solution is implemented as a small, modular system consisting of:
- a **FastAPI backend** for analysis
- a **Streamlit frontend** for interactive exploration
- a reusable **core analytics module**

---

## Features & Metrics

The system computes the following metrics:

- **Total Car Count**  
  The aggregate number of cars recorded across the entire dataset.

- **Daily Traffic Totals**  
  A chronological breakdown of total car counts per day.

- **Top 3 Half-Hour Periods**  
  The three individual 30-minute intervals with the highest traffic volume.

- **Lowest 1.5-Hour Window**  
  The contiguous 90-minute period (three consecutive records) with the lowest cumulative traffic.

---

## Architecture

```
.
├── api.py                  # FastAPI service
├── dashboard.py            # Streamlit UI
├── traffic_analysis.py     # Core analytical logic
├── test_traffic_analysis.py
├── sample.txt              # Sample dataset
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Components

### FastAPI Backend (`api.py`)
- Exposes an `/analyze` endpoint
- Accepts uploaded traffic data files
- Returns structured JSON results
- Maintains a clear separation between API handling and business logic

### Streamlit Dashboard (`dashboard.py`)
- Interactive web interface
- Supports file uploads
- Displays computed metrics and charts

### Core Analytics Engine (`traffic_analysis.py`)
- Responsible for file parsing and validation
- Performs aggregations and sliding-window calculations
- Implements deterministic tie-breaking logic

---

## Key Design Decisions

### 1. Explicit Sorting for Correctness (O(N log N))

Input files may not be ordered chronologically.  
To guarantee correctness, all records are explicitly sorted by timestamp immediately after parsing:

```python
records.sort(key=lambda r: r.timestamp)
```

This ensures reliable downstream calculations, including sliding-window logic.

---

### 2. Efficient Sliding Window for Lowest Traffic Period

The lowest 1.5-hour window is computed using a **sliding window technique**:
- Linear time complexity after sorting (O(N))
- Avoids redundant summation
- Handles edge cases gracefully

---

### 3. Deterministic Tie-Breaking

For the **Top 3 Half-Hour Periods**:
- Records are sorted by:
  1. Descending car count
  2. Ascending timestamp (tie-breaker)

This guarantees **stable and predictable output**, prioritizing earlier intervals when counts are equal.

---

## Running the Application

### Option 1: Docker (Recommended)

Run the full stack (API + Dashboard):

```bash
docker-compose up --build
```

- Streamlit Dashboard: http://localhost:8501  
- API Documentation (Swagger): http://localhost:8000/docs  

---

### Option 2: Local Execution

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the API:

```bash
uvicorn api:app --reload
```

Start the dashboard:

```bash
streamlit run dashboard.py
```

---

## CLI Usage

The analytics engine can also be run directly:

```bash
python traffic_analysis.py sample.txt
```

---

## Testing

- Automated tests are implemented using **pytest**
- Coverage includes:
  - Core metric calculations
  - Sliding window logic
  - Tie-breaking behavior
  - Edge cases (e.g. empty or minimal datasets)

Run tests:

```bash
pytest
```

---

## Error Handling & Robustness

- Malformed input lines are skipped during parsing
- Parsing errors are logged to `stderr`
- Valid records continue to be processed without failing the entire run
- Output remains clean and structured for downstream usage

---

## Trade-offs & Future Improvements

- Support for **streaming or very large datasets**
- Persistent storage for results (e.g. Redis or PostgreSQL)
- API authentication and rate limiting
- Structured logging and metrics (e.g. Prometheus)
- Deployment to a managed cloud environment (AWS ECS / EKS)

---

## Summary

This solution prioritizes:
- **Correctness over assumptions**
- **Deterministic behavior**
- **Clean separation of concerns**
- **Production-oriented engineering practices**

It is designed to be easy to run, test, and extend, while remaining efficient and predictable.

---

## Repository Link

This project is also available on GitHub: https://github.com/ShadiaBaroud/seek_assessment

