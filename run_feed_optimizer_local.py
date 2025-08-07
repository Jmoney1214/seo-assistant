import requests
import os

API_URL = "http://localhost:8090/optimize_feed/"
INPUT_FILE = "products_feed.csv"
OUTPUT_FILE = "optimized_gmc_feed.csv"

print("\n--- DEBUG: Script starting ---")

# 1. Check if server is up before sending the file
try:
    print(f"Checking if server is up at {API_URL} ...")
    health_check = requests.get(API_URL.replace("/optimize_feed/", "/docs"))
    if health_check.status_code == 200:
        print("Server is reachable. Swagger UI loaded.\n")
    else:
        print(f"WARNING: Server reachable but /docs returned status {health_check.status_code}")
except Exception as e:
    print("ERROR: Server is NOT reachable at", API_URL)
    print("EXCEPTION:", e)
    print("Aborting script.")
    exit(1)

# 2. Check that input file exists
if not os.path.exists(INPUT_FILE):
    print(f"ERROR: Input file '{INPUT_FILE}' does NOT exist in {os.getcwd()}")
    exit(2)
else:
    print(f"Found input file: {INPUT_FILE}")

# 3. Try to POST the file to the server
try:
    print(f"Opening {INPUT_FILE} for reading (as binary)...")
    with open(INPUT_FILE, "rb") as f:
        files = {"file": (INPUT_FILE, f, "text/csv")}
        print("Sending POST request to API endpoint:", API_URL)
        response = requests.post(API_URL, files=files)
        print("Response received from API.")

    print("Response code:", response.status_code)
    # Print the first part of the response for easy debugging
    print("Response content (first 300 chars):", response.content[:300])
except Exception as e:
    print("EXCEPTION during POST:", e)
    exit(3)

# 4. Save output or print error
if response.status_code == 200:
    try:
        with open(OUTPUT_FILE, "wb") as out:
            out.write(response.content)
        print(f"SUCCESS: Optimized feed saved as {OUTPUT_FILE}")
    except Exception as e:
        print("EXCEPTION during file write:", e)
        exit(4)
else:
    print(f"API returned error: Status code {response.status_code}")
    print("Full response text:", response.text)

print("--- DEBUG: Script finished ---\n")
