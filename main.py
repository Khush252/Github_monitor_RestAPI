# main.py

# Direct Commits: Commits made directly to the main branch will be captured as they have a single parent.
# Squashed Commits: When commits are squashed and merged, they will also appear as single-parent commits and will be included in the analysis.
# Rebase and Merge Commits: After rebase and merge, the rebased commits will appear as if they were made directly on top of the main branch, each having a single parent.
# Merge Commits: Merge commits that integrate changes from one branch into another and have multiple parents will be ignored to avoid double-counting.

# API call for generating report
# With custom date range:      http://localhost:8000/generate_report?start_date=01-06-24&end_date=20-06-24

# Default to the last 7 days:  http://localhost:8000/generate_report
from fastapi import FastAPI, Query, HTTPException
from typing import Optional
from datetime import datetime, timedelta
import os
import signal
import sys
from src.generate_report import generate_report
from config import REPO_OWNER, REPO_NAME, ACCESS_TOKEN
import httpx

app = FastAPI()

def handle_shutdown(signum, frame):
    print(f"Received signal {signum}, shutting down gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)

@app.get("/generate_report")
async def generate_report_endpoint(
    start_date_str: Optional[str] = Query(None),
    end_date_str: Optional[str] = Query(None),
):
    date_format = "%d-%m-%Y"

    try:
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, date_format)
            end_date = datetime.strptime(end_date_str, date_format)
        else:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
        if start_date > datetime.now() and end_date > datetime.now():
            print("Both Start and End Dates are invalid")
            raise HTTPException(
                status_code=400, detail="Both Start and End Dates are invalid"
            )
        if start_date > datetime.now():
            print("Start Date is invalid")
            raise HTTPException(status_code=400, detail="Start Date is invalid")
        if end_date > datetime.now():
            print("End Date is invalid")
            raise HTTPException(status_code=400, detail="End Date is invalid")
        if end_date < start_date:
            print("End date must be greater than start date.")
            raise HTTPException(
                status_code=400, detail="End date must be greater than start date."
            )

    except ValueError:
        print("Incorrect date format, should be dd-mm-yyyy.")
        raise HTTPException(
            status_code=400, detail="Incorrect date format, should be dd-mm-yyyy."
        )

    print("Generating report...")
    try:
        file_path = await generate_report(
            REPO_OWNER, REPO_NAME, ACCESS_TOKEN, start_date, end_date
        )
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 403:
            print("Rate limit exceeded")
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        else:
            print("Error generating report")
            raise HTTPException(status_code=500, detail="Error generating report")
    
    print(f"Report Generated for {start_date} to {end_date}")
    return {"message": "Report generated", "file_path": file_path}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
