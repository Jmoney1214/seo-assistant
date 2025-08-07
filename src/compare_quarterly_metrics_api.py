from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric
from google.oauth2 import service_account
from datetime import datetime, timedelta

router = APIRouter()

KEY_PATH = "ga_service_key.json"
PROPERTY_ID = "421376314"

default_metrics = [
    "activeUsers", "newUsers", "sessions",
    "engagementRate", "averageSessionDuration", "bounceRate",
    "conversions", "purchaseRevenue", "screenPageViews"
]

METRIC_ALIASES = {
    "revenue": "purchaseRevenue",
    "engagement rate": "engagementRate",
    "bounce rate": "bounceRate",
    "average session duration": "averageSessionDuration",
    "avg session time": "averageSessionDuration",
    "avg session length": "averageSessionDuration",
    "conversions": "conversions",
    "sessions": "sessions",
    "users": "activeUsers",
    "new users": "newUsers",
    "page views": "screenPageViews"
}

class CompareQuarterlyRequest(BaseModel):
    start_year: int
    num_quarters: Optional[int] = 4
    metrics: Optional[List[str]] = None

def get_quarter_date_range(year: int, quarter: int):
    start_month = (quarter - 1) * 3 + 1
    end_month = start_month + 2
    start_date = datetime(year, start_month, 1).strftime("%Y-%m-%d")
    next_quarter_start = datetime(year if end_month < 12 else year + 1, (end_month % 12) + 1, 1)
    end_date = (next_quarter_start - timedelta(days=1)).strftime("%Y-%m-%d")
    return start_date, end_date

def fetch_quarter_data(start_date: str, end_date: str, metrics: List[str]) -> Dict[str, float]:
    credentials = service_account.Credentials.from_service_account_file(KEY_PATH)
    client = BetaAnalyticsDataClient(credentials=credentials)

    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        metrics=[Metric(name=m) for m in metrics],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)]
    )

    response = client.run_report(request)

    if not response.rows:
        return {m: 0.0 for m in metrics}

    row = response.rows[0]
    return {
        metrics[i]: float(row.metric_values[i].value)
        for i in range(len(metrics))
    }

@router.post("/compare_quarterly_metrics")
def compare_quarterly_metrics(req: CompareQuarterlyRequest):
    try:
        raw_metrics = req.metrics if req.metrics else default_metrics
        metrics_to_use = [METRIC_ALIASES.get(m.lower(), m) for m in raw_metrics]

        comparisons: Dict[str, List[Dict[str, float]]] = {}

        for i in range(req.num_quarters):
            year = req.start_year + ((i + 1) // 5)
            quarter = (i % 4) + 1

            start_date, end_date = get_quarter_date_range(year, quarter)
            data = fetch_quarter_data(start_date, end_date, metrics_to_use)

            for metric_name, value in data.items():
                comparisons.setdefault(metric_name, []).append({
                    "year": year,
                    "quarter": quarter,
                    "value": value
                })

        # Generate assistant-friendly summary
        summary_lines = []
        for metric, entries in comparisons.items():
            for entry in entries:
                value = entry['value']
                formatted = int(value) if value == int(value) else round(value, 2)
                summary_lines.append(
                    f"In Q{entry['quarter']} {entry['year']}, {metric} was {formatted}."
                )
        summary_text = " ".join(summary_lines)

        return {
            "success": True,
            "summary": summary_text,
            "data": comparisons
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
