import openai
import requests
import json
import os

# Set your OpenAI API key as an environment variable or here
openai.api_key = os.getenv("OPENAI_API_KEY") or "sk-..."

# Map function names to your FastAPI endpoints
API_BASE = "http://localhost:8100"

def get_best_event_nights(start_date, end_date, metric="activeUsers", top_n=5):
    url = f"{API_BASE}/best_event_nights"
    payload = {
        "start_date": start_date,
        "end_date": end_date,
        "metric": metric,
        "top_n": top_n
    }
    resp = requests.post(url, json=payload)
    return resp.json()

def get_country_breakdown(start_date, end_date):
    url = f"{API_BASE}/country_breakdown?start_date={start_date}&end_date={end_date}"
    resp = requests.get(url)
    return resp.json()

# Define available function schemas for the assistant
functions = [
    {
        "name": "get_best_event_nights",
        "description": "Get the best days and hours for customer events, based on Google Analytics engagement.",
        "parameters": {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "YYYY-MM-DD"},
                "end_date": {"type": "string", "description": "YYYY-MM-DD"},
                "metric": {"type": "string", "description": "Metric to use (default 'activeUsers')", "default": "activeUsers"},
                "top_n": {"type": "integer", "description": "How many top time slots to return", "default": 5}
            },
            "required": ["start_date", "end_date"]
        }
    },
    {
        "name": "get_country_breakdown",
        "description": "Get country-by-country active user report for the given date range.",
        "parameters": {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "YYYY-MM-DD"},
                "end_date": {"type": "string", "description": "YYYY-MM-DD"}
            },
            "required": ["start_date", "end_date"]
        }
    }
]

function_map = {
    "get_best_event_nights": get_best_event_nights,
    "get_country_breakdown": get_country_breakdown
}

# Simple assistant function-calling loop (for CLI or backend)
def run_assistant_query(user_question):
    messages = [
        {"role": "system", "content": "You are a world-class analytics and business intelligence assistant. Always use the available functions to answer with real, live data, and include strategic recommendations for event planning, targeting, and campaign timing."},
        {"role": "user", "content": user_question}
    ]

    response = openai.chat.completions.create(
        model="gpt-4o",  # or gpt-4-turbo
        messages=messages,
        tools=functions,  # This is 'functions' in API 1.x, or 'tools' for backwards compatibility
        tool_choice="auto"
    )

    message = response.choices[0].message
    if message.tool_calls:
        tool_call = message.tool_calls[0]
        fn_name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)
        # Call your local analytics function
        result = function_map[fn_name](**args)
        # Send the result back to the assistant for a final answer
        followup = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages + [
                {"role": "assistant", "content": None, "tool_calls": [tool_call]},
                {"role": "tool", "tool_call_id": tool_call.id, "name": fn_name, "content": json.dumps(result)}
            ]
        )
        print(followup.choices[0].message.content)
    else:
        print(message.content)

if __name__ == "__main__":
    # Example usage
    user_q = input("Ask your analytics assistant: ")
    run_assistant_query(user_q)
