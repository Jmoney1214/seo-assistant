import os
from dotenv import load_dotenv

load_dotenv()

print("OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY")[:8], "...")
print("GA4_MEASUREMENT_ID:", os.getenv("GA4_MEASUREMENT_ID"))
print("GA4_API_SECRET:", os.getenv("GA4_API_SECRET")[:8], "...")
