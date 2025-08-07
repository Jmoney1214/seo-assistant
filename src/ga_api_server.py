import os, uuid, time, requests
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

GA_MEASUREMENT_ID = os.getenv("GA4_MEASUREMENT_ID")
GA_API_SECRET = os.getenv("GA4_API_SECRET")

app = FastAPI()

class EventPayload(BaseModel):
    event_name: str
    params: dict

@app.post("/track_event")
def track_event(data: EventPayload):
    client_id = "debug_" + str(uuid.uuid4())
    endpoint = (
        f"https://www.google-analytics.com/debug/mp/collect"
        f"?measurement_id={GA_MEASUREMENT_ID}"
        f"&api_secret={GA_API_SECRET}"
    )
    payload = {
        "client_id": client_id,
        "non_personalized_ads": False,
        "timestamp_micros": int(time.time() * 1_000_000),
        "events": [
            {"name": data.event_name, "params": data.params}
        ],
        "user_properties": {
            "debug_mode": {"value": "true"},
            "triggered_by": {"value": "openai_assistant"}
        }
    }
    response = requests.post(endpoint, json=payload)
    return {
        "status_code": response.status_code,
        "ga_response": response.json()
    }
