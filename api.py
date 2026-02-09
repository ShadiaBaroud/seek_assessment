# api.py
# Run with: uvicorn api:app --reload

from fastapi import FastAPI, UploadFile, File, HTTPException
from schemas import TrafficMetrics
from traffic_analysis import analyze_traffic_file
import logging

# -------------------------------------------------------------------
# Logging configuration
# -------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("traffic_api")

# -------------------------------------------------------------------
# FastAPI application
# -------------------------------------------------------------------
app = FastAPI(title="Traffic Analysis Microservice")


# -------------------------------------------------------------------
# Health check (for Docker / cloud readiness)
# -------------------------------------------------------------------
@app.get("/health")
def health_check():
    return {"status": "ok"}


# -------------------------------------------------------------------
# Analyze endpoint
# -------------------------------------------------------------------
@app.post(
    "/analyze",
    response_model=TrafficMetrics,
    summary="Analyze traffic counter data",
    description="Processes half-hour traffic data and returns aggregated metrics.",
)
async def analyze(file: UploadFile = File(...)) -> TrafficMetrics:
    """
    Analyze half-hour traffic counter data.

    :param file: Uploaded traffic data file
    :return: Computed traffic metrics
    """
    logger.info("Received file: %s", file.filename)

    try:
        contents = (await file.read()).decode("utf-8", errors="ignore")
        return analyze_traffic_file(contents)

    except ValueError as e:
        logger.warning("Validation error: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e))

    except Exception:
        logger.exception("Unexpected server error")
        raise HTTPException(status_code=500, detail="Internal server error")