import os
from fastapi import FastAPI
from dotenv import load_dotenv
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric
from google.oauth2 import service_account

# Load .env if needed
load_dotenv()

# ✅ Your verified config
GA4_PROPERTY_ID = "421376314"
KEY_FILE = "config/secrets/ga_service_key.json"

app = FastAPI()

@app.get("/get_analytics_summary")
def get_analytics_summary():
    credentials = service_account.Credentials.from_service_account_file(KEY_FILE)
    client = BetaAnalyticsDataClient(credentials=credentials)

    request = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        metrics=[
            Metric(name="sessions"),
            Metric(name="activeUsers"),
            Metric(name="eventCount"),
            Metric(name="purchaseRevenue"),
            Metric(name="transactions")
        ],
        date_ranges=[DateRange(start_date="today", end_date="today")]
    )

    response = client.run_report(request)
    row = response.rows[0].metric_values

    return {
        "sessions": row[0].value,
        "active_users": row[1].value,
        "event_count": row[2].value,
        "revenue": f"${row[3].value}",
        "purchases": row[4].value
    }
