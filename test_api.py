from fastapi.testclient import TestClient
from api import app

client = TestClient(app)


def test_health_check():
    """
    Verifies that the service health endpoint is available.
    Required for container orchestration and readiness checks.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_valid_file():
    """
    Verifies successful analysis of a valid traffic file.
    """
    content = b"""
2025-01-01T10:00:00 5
2025-01-01T10:30:00 3
2025-01-01T11:00:00 2
"""

    response = client.post(
        "/analyze",
        files={"file": ("traffic.txt", content, "text/plain")},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["total_count"] == 10
    assert data["daily_counts"]["2025-01-01"] == 10
    assert len(data["top_periods"]) == 3
    assert "lowest_window" in data


def test_analyze_empty_file_returns_400():
    """
    Empty input should fail with a validation error,
    not an internal server error.
    """
    response = client.post(
        "/analyze",
        files={"file": ("empty.txt", b"", "text/plain")},
    )

    assert response.status_code == 400
    assert "No valid records" in response.json()["detail"]


def test_analyze_insufficient_records_returns_400():
    """
    Less than 3 valid records cannot form a 1.5-hour window.
    """
    content = b"""
2025-01-01T10:00:00 5
2025-01-01T10:30:00 3
"""

    response = client.post(
        "/analyze",
        files={"file": ("short.txt", content, "text/plain")},
    )

    assert response.status_code == 400
    assert "At least 3 records" in response.json()["detail"]


def test_analyze_with_malformed_lines():
    """
    Malformed lines should be skipped, not crash the API.
    """
    content = b"""
bad_line
2025-01-01T10:30:00 3
INVALID 10
2025-01-01T11:00:00 2
2025-01-01T11:30:00 1
"""

    response = client.post(
        "/analyze",
        files={"file": ("mixed.txt", content, "text/plain")},
    )

    assert response.status_code == 200
    assert response.json()["total_count"] == 6
