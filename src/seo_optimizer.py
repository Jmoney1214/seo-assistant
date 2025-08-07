import os
import pandas as pd
import openai
from dotenv import load_dotenv

# Load environment variables from .env file in project root
load_dotenv()

# Create OpenAI client instance using API key from env
client = openai.OpenAI()

# File locations (relative to project root)
INPUT_CSV = "products_feed.csv"  # Place your feed here: ~/Projects/seo-assistant/products_feed.csv
OUTPUT_CSV = "optimized_gmc_feed.csv"  # Output will be saved as ~/Projects/seo-assistant/optimized_gmc_feed.csv

def optimize_seo(title, description):
    prompt = (
        f"Rewrite the following for e-commerce SEO.\n"
        f"1. New product title (70 chars max, compelling, keyword-rich).\n"
        f"2. Meta description (140-160 chars, with brand and call-to-action).\n"
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
    result = response.choices[0].message.content
    lines = result.split('\n')
    new_title = lines[0].replace('Title: ', '').strip() if len(lines) > 0 else ""
    meta = lines[1].replace('Meta: ', '').strip() if len(lines) > 1 else ""
    alt = lines[2].replace('Alt: ', '').strip() if len(lines) > 2 else ""
    print(f"Processed: {title[:60]}...")  # Show first 60 chars of title for progress
    return new_title, meta, alt

if __name__ == "__main__":
    print("Loading product feed…")
    df = pd.read_csv(INPUT_CSV, sep="\t")  # Use sep="," for standard CSV, "\t" for TSV from Merchant Center
    print("Loaded rows:", len(df))
    print("Columns:", df.columns.tolist())

    def debug_func(row):
        print("Processing title:", row['title'])
        return optimize_seo(row['title'], row['description'])

    print("Beginning SEO optimization…")
    df[['new_title', 'meta_description', 'image_alt']] = df.apply(
        debug_func,
        axis=1, result_type='expand'
    )
    print("Writing CSV output…")
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Optimized file saved as {OUTPUT_CSV}")
