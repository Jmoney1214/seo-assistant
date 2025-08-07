from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest
from google.oauth2 import service_account
from datetime import date, timedelta

# Path to your service account key file
KEY_PATH = "ga_service_key.json"
PROPERTY_ID = "421376314"  # <-- Your GA4 Property ID

# Calculate last 30 days
today = date.today()
thirty_days_ago = today - timedelta(days=30)
start_date = thirty_days_ago.strftime("%Y-%m-%d")
end_date = today.strftime("%Y-%m-%d")

credentials = service_account.Credentials.from_service_account_file(KEY_PATH)
client = BetaAnalyticsDataClient(credentials=credentials)

request = RunReportRequest(
    property=f"properties/{PROPERTY_ID}",
    dimensions=[{"name": "country"}],
    metrics=[{"name": "activeUsers"}],
    date_ranges=[{"start_date": start_date, "end_date": end_date}],
)

print(f"--- Sending request to GA Data API for {start_date} to {end_date} ---")

try:
    response = client.run_report(request)
    print("Raw API response:", response)
    print("Rows returned:", len(response.rows))
    print(response)
    if not response.rows:
        print("No data returned by the API (empty report). Check your property ID and date range.")
    else:
        print("\nCountry breakdown:")
        for row in response.rows:
            country = row.dimension_values[0].value
            users = row.metric_values[0].value
            print(f"Country: {country}, Active Users: {users}")
except Exception as e:
    print("API ERROR:", e)
