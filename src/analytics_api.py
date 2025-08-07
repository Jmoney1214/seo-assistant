from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import Optional, List, Dict
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric
from google.oauth2 import service_account
from datetime import date, timedelta
from fastapi.middleware.cors import CORSMiddleware
from src.compare_quarterly_metrics_api import router as compare_router
from src.get_user_traffic_summary import router as traffic_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(compare_router)
app.include_router(traffic_router)

KEY_PATH = "ga_service_key.json"
PROPERTY_ID = "421376314"

class EventNightRequest(BaseModel):
    start_date: str
    end_date: str
    metric: str = "activeUsers"
    top_n: int = 5

def get_analytics_report(start_date, end_date, dimensions, metrics):
    credentials = service_account.Credentials.from_service_account_file(KEY_PATH)
    client = BetaAnalyticsDataClient(credentials=credentials)
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[Dimension(name=d) for d in dimensions],
        metrics=[Metric(name=m) for m in metrics],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)]
    )
    return client.run_report(request)

@app.post("/best_event_nights")
def best_event_nights(req: EventNightRequest):
    dimensions = ["dayOfWeek", "hour"]
    metrics = [req.metric]
    response = get_analytics_report(req.start_date, req.end_date, dimensions, metrics)
    event_slots = []
    for row in response.rows:
        day = row.dimension_values[0].value
        hour = row.dimension_values[1].value
        metric_val = int(row.metric_values[0].value)
        event_slots.append({"day": day, "hour": hour, "value": metric_val})
    best_slots = sorted(event_slots, key=lambda x: -x["value"])[:req.top_n]
    return {"best_event_times": best_slots}

@app.get("/country_breakdown")
def country_breakdown(start_date: str = Query(...), end_date: str = Query(...)):
    response = get_analytics_report(start_date, end_date, ["country"], ["activeUsers"])
    return {
        "rows": [
            {
                "country": row.dimension_values[0].value,
                "activeUsers": row.metric_values[0].value
            }
            for row in response.rows
        ]
    }

@app.get("/abandoned_pages")
def abandoned_pages(start_date: str = Query(...), end_date: str = Query(...), top_n: int = Query(5)):
    dimensions = ["pagePath"]
    metrics = ["screenPageViews", "exits"]
    response = get_analytics_report(start_date, end_date, dimensions, metrics)
    rows = []
    for row in response.rows:
        page = row.dimension_values[0].value
        views = int(row.metric_values[0].value)
        exits = int(row.metric_values[1].value)
        abandon_rate = (exits / views) if views > 0 else 0
        rows.append({"page": page, "views": views, "exits": exits, "abandon_rate": abandon_rate})
    sorted_pages = sorted(rows, key=lambda x: -x["abandon_rate"])[:top_n]
    return {"abandoned_pages": sorted_pages}

@app.get("/")
def root():
    return {"status": "OK", "message": "API is running"}

