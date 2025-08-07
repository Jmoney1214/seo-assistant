import os
import pandas as pd
import openai
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import tempfile
import shutil

# === LOAD OPENAI KEY ===
load_dotenv()
client = openai.OpenAI()

app = FastAPI()

# === SEO OPTIMIZER FUNCTION ===
def optimize_seo(title, description):
    prompt = (
        f"Rewrite the following for e-commerce SEO.\n"
        f"1. New product title (70 chars max, compelling, keyword-rich).\n"
        f"2. Meta description (140–160 chars, with brand and call-to-action).\n"
        f"3. Image alt tag.\n\n"
        f"Title: {title}\nDescription: {description}\n"
        f"Format the output as:\n"
        f"Title: ...\nMeta: ...\nAlt: ..."
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an e-commerce SEO expert."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=350,
        temperature=0.4,
    )

    lines = response.choices[0].message.content.strip().split('\n')
    new_title = lines[0].replace("Title:", "").strip() if len(lines) > 0 else ""
    meta = lines[1].replace("Meta:", "").strip() if len(lines) > 1 else ""
    alt = lines[2].replace("Alt:", "").strip() if len(lines) > 2 else ""

    return new_title, meta, alt

# === FEED OPTIMIZATION ENDPOINT ===
@app.post("/optimize_feed/")
async def optimize_feed(file: UploadFile = File(...)):
    print(f"✅ Received file: {file.filename}")

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        df = pd.read_csv(tmp_path, sep=",")
        print("📄 Columns in file:", df.columns.tolist())
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"❌ Failed to parse CSV: {str(e)}")

    required_cols = ["title", "description"]
    if not all(col in df.columns for col in required_cols):
        raise HTTPException(
            status_code=400,
            detail=f"❌ CSV must contain these columns: {required_cols}"
        )

    df = df.head(3)  # Optional: remove or increase later

    try:
        df[["new_title", "meta_description", "image_alt"]] = df.apply(
            lambda row: optimize_seo(row["title"], row["description"]),
            axis=1,
            result_type="expand"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"❌ Optimization failed: {str(e)}"
        )

    output_path = tmp_path + "_optimized.csv"
    df.to_csv(output_path, index=False)
    print(f"✅ File optimized: {output_path}")

    return FileResponse(
        output_path,
        filename="optimized_gmc_feed.csv",
        media_type="text/csv"
    )
