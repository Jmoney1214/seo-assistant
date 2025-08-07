from fastapi import APIRouter, HTTPException
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest
from google.oauth2 import service_account
import os

router = APIRouter()

KEY_PATH = os.environ.get("KEY_PATH", "/etc/secrets/ga_service_key.json")
PROPERTY_ID = os.environ.get("PROPERTY_ID")

@router.post("/get_user_traffic_summary")
def get_user_traffic_summary(start_date: str, end_date: str):
    try:
        credentials = service_account.Credentials.from_service_account_file(KEY_PATH)
        client = BetaAnalyticsDataClient(credentials=credentials)

        request = RunReportRequest(
            property=f"properties/{PROPERTY_ID}",
            dimensions=[],
            metrics=[
                {"name": "activeUsers"},
                {"name": "newUsers"},
                {"name": "sessions"}
            ],
            date_ranges=[{"start_date": start_date, "end_date": end_date}],
        )

        response = client.run_report(request)
        values = response.rows[0].metric_values

        return {
            "activeUsers": int(values[0].value),
            "newUsers": int(values[1].value),
            "sessions": int(values[2].value),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

