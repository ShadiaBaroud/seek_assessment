# api.py
# Run with: uvicorn api:app --reload

from fastapi import FastAPI, UploadFile, HTTPException
from typing import List, Dict
from datetime import date
import shutil
import os

# Import your existing logic!
from traffic_analysis import (
    parse_file, 
    total_cars, 
    cars_per_day, 
    top_three_half_hours, 
    min_1_5_hour_window,
    HalfHourRecord
)

app = FastAPI(title="Traffic Analysis Microservice")

@app.post("/analyze")
async def analyze_traffic_file(file: UploadFile):
    """
    Endpoint to upload a raw traffic file and get full analysis JSON.
    """
    temp_filename = f"temp_{file.filename}"
    
    try:
        # 1. Save uploaded file temporarily
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 2. Reuse core logic from traffic_analysis.py
        records = parse_file(temp_filename)
        
        if not records:
            raise HTTPException(status_code=400, detail="No valid records found in file.")

        # Ensure sorted order (Just like in main!)
        records.sort(key=lambda r: r.timestamp)

        # 3. Perform Analyses
        total = total_cars(records)
        daily_counts = cars_per_day(records)
        top_3 = top_three_half_hours(records)
        min_window = min_1_5_hour_window(records)

        # 4. Return structured JSON
        return {
            "meta": {
                "filename": file.filename,
                "records_processed": len(records)
            },
            "analysis": {
                "total_cars": total,
                "cars_per_day": {d.isoformat(): count for d, count in daily_counts.items()},
                "top_3_periods": [
                    {"timestamp": r.timestamp, "count": r.count} for r in top_3
                ],
                "lowest_1_5_hour_window": [
                    {"timestamp": r.timestamp, "count": r.count} for r in min_window
                ]
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        # Cleanup: Remove the temp file to keep the server clean
        if os.path.exists(temp_filename):
            os.remove(temp_filename)