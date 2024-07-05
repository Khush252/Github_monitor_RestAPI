# main.py

# Direct Commits: Commits made directly to the main branch will be captured as they have a single parent.
# Squashed Commits: When commits are squashed and merged, they will also appear as single-parent commits and will be included in the analysis.
# Rebase and Merge Commits: After rebase and merge, the rebased commits will appear as if they were made directly on top of the main branch, each having a single parent.
# Merge Commits: Merge commits that integrate changes from one branch into another and have multiple parents will be ignored to avoid double-counting.

# API call for generating report
# With custom date range:      http://localhost:8001/generate_report?start_date_str=01-06-2024&end_date_str=20-06-2024

# Default to the last 7 days:  http://localhost:8001/generate_report
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
from datetime import datetime, timedelta
import os
import signal
import sys
from src.generate_report import generate_report
from config import REPO_OWNER, REPO_NAME, ACCESS_TOKEN
from utils.slack_alert import send_slack_alert
import httpx
import pandas as pd

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
    start_date=None
    end_date=None
    try:
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, date_format)
            end_date = datetime.strptime(end_date_str, date_format)
        else:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=2)
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
        file_path, report_data = await generate_report(
            REPO_OWNER, REPO_NAME, ACCESS_TOKEN, start_date, end_date
        )

        # Creating the table header
        report_table = "USERS                TESTS ADDED    PRs CONTRIBUTED\n"
        report_table += "--------------------------------------------------\n"

        # Adding the data rows
        for row in report_data.itertuples(index=False, name=None):
            report_table += f"{row[0]:<20} {row[1]:<12} {row[2]:<16}\n"

        completion_message = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"✅ Report Generated",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Report Path:* `{file_path}`\n*Duration:* {start_date_str} to {end_date_str}"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"```\n{report_table}\n```"
                }
            }
        ]

        send_slack_alert(completion_message, is_block=True)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 403:
            print("Rate limit exceeded")
            rate_limit_message = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🚫 Rate Limit Exceeded",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Rate limit exceeded while generating the report. Please try again later."
                    }
                }
            ]
            send_slack_alert(rate_limit_message, is_block=True)
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        else:
            print("Error generating report")
            error_message = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "❌ Error Generating Report",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "An error occurred while generating the report. Please check the logs for more details."
                    }
                }
            ]
            send_slack_alert(error_message, is_block=True)
            raise HTTPException(status_code=500, detail="Error generating report")
    
    print(f"Report Generated for {start_date} to {end_date}")
    return JSONResponse(content={"message": "Report generated", "file_path": file_path}, status_code=200)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
