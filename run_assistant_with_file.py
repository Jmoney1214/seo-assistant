import openai
import os
import time
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
assistant_id = "asst_eiRwI4FvzKfCTJ4HKyxpeh7C"

def upload_file(file_path):
    with open(file_path, "rb") as f:
        file_resp = openai.files.create(file=f, purpose="assistants")
        return file_resp.id

if __name__ == "__main__":
    file_id = upload_file("products_feed.csv")
    print("File uploaded. ID:", file_id)

    # 1. Create a thread (NO attachments here)
    thread = openai.beta.threads.create()

    # 2. Send a message with the file attached, and tools as an ARRAY of STRINGS (not objects)
    message = openai.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content="Please optimize this product feed for SEO and compliance.",
        attachments=[{
            "file_id": file_id,
            "tools": ["optimize_feed"]
        }]
    )

    # 3. Start the run
    run = openai.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id
    )

    # 4. Poll for completion
    while True:
        run = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        print("Status:", run.status)
        if run.status in ("completed", "failed", "cancelled", "expired"):
            break
        time.sleep(2)

    # 5. Print all messages
    messages = openai.beta.threads.messages.list(thread_id=thread.id)
    for msg in messages.data:
        print(msg.role + ":", msg.content[0].text.value)
