import os
import uuid
import requests
from dotenv import load_dotenv

# Load environment variables from ~/.zshrc or .env
load_dotenv()

GA_MEASUREMENT_ID = os.getenv("GA4_MEASUREMENT_ID")
GA_API_SECRET = os.getenv("GA4_API_SECRET")

def send_event(event_name, params=None):
    if params is None:
        params = {}

    # Generate a realistic random client ID
    client_id = str(uuid.uuid4())

    # Use the GA4 DEBUG endpoint
    endpoint = (
        f"https://www.google-analytics.com/debug/mp/collect"
        f"?measurement_id={GA_MEASUREMENT_ID}"
        f"&api_secret={GA_API_SECRET}"
    )

    payload = {
        "client_id": client_id,
        "events": [
            {
                "name": event_name,
                "params": params
            }
        ],
        "user_properties": {
            "debug_mode": {
                "value": "true"
            }
        }
    }

    response = requests.post(endpoint, json=payload)
    print(f"Status code: {response.status_code}")
    print(f"Response body: {response.text}")

if __name__ == "__main__":
    send_event("test_event", {
    "source": "backend",
    "triggered_by": "python_script",
    "debug": True
})
