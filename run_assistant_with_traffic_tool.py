import openai
import requests
import os

openai.api_key = os.getenv("OPENAI_API_KEY")  # or paste your key directly

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_user_traffic_summary",
            "description": "Get user traffic data between two dates.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format"
                    }
                },
                "required": ["start_date", "end_date"]
            }
        }
    }
]

def handle_function_call(name, arguments):
    if name == "get_user_traffic_summary":
        print("Calling FastAPI backend...")
        res = requests.post("http://localhost:8100/get_user_traffic_summary", json=arguments)
        return res.json()
    else:
        return {"error": "Unknown function"}

def run_chat():
    messages = [
        {"role": "user", "content": "How much traffic did we get from July 1 to July 31, 2025?"}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    tool_call = response.choices[0].message.tool_calls[0]
    function_name = tool_call.function.name
    function_args = eval(tool_call.function.arguments)

    result = handle_function_call(function_name, function_args)

    messages.append({
        "role": "assistant",
        "tool_calls": [tool_call]
    })

    messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "name": function_name,
        "content": str(result)
    })

    final_response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=messages
    )

    print("\n💬 Assistant response:")
    print(final_response.choices[0].message.content)

if __name__ == "__main__":
    run_chat()

