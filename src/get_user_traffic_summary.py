from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric
from google.oauth2 import service_account
import os

router = APIRouter()

KEY_PATH = os.getenv("KEY_PATH", "ga_service_key.json")
PROPERTY_ID = os.getenv("PROPERTY_ID", "421376314")

class UserTrafficRequest(BaseModel):
    start_date: str
    end_date: str

@router.post("/get_user_traffic_summary")
def get_user_traffic_summary(req: UserTrafficRequest):
    try:
        credentials = service_account.Credentials.from_service_account_file(KEY_PATH)
        client = BetaAnalyticsDataClient(credentials=credentials)

        request = RunReportRequest(
            property=f"properties/{PROPERTY_ID}",
            metrics=[
                Metric(name="activeUsers"),
                Metric(name="newUsers"),
                Metric(name="sessions"),
            ],
            date_ranges=[DateRange(start_date=req.start_date, end_date=req.end_date)],
        )

        response = client.run_report(request)
        if not response.rows:
            return {
                "summary": f"From {req.start_date} to {req.end_date}: no data.",
                "metrics": {"activeUsers": 0, "newUsers": 0, "sessions": 0},
            }

        vals = response.rows[0].metric_values
        metrics = {
            "activeUsers": int(float(vals[0].value or 0)),
            "newUsers": int(float(vals[1].value or 0)),
            "sessions": int(float(vals[2].value or 0)),
        }
        summary = (
            f"From {req.start_date} to {req.end_date}: "
            f"activeUsers = {metrics['activeUsers']}, "
            f"newUsers = {metrics['newUsers']}, "
            f"sessions = {metrics['sessions']}."
        )
        return {"summary": summary, "metrics": metrics}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
