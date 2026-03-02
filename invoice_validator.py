import boto3
import json
import re
import pandas as pd
import cv2
import numpy as np
import fitz  # PyMuPDF
from io import BytesIO

# --- CONFIGURATION ---
# Using the Cross-Region Inference Profile for Claude 3.5 Sonnet v2
MODEL_ID = "us.meta.llama3-2-90b-instruct-v1:0"
REGION = "us-east-2"  # Best for Claude Sonnet v2 profiles
OUTPUT_FILE = "Extracted_PDF_Data.csv"

def get_high_res_image_bytes(page):
    """
    Renders PDF page at 2x zoom (300+ DPI equivalent).
    Standardizes quality to fix decimal and digit-mixing errors.
    """
    # 2.0x Matrix scaling makes tiny text much clearer for the LLM
    mat = fitz.Matrix(2.0, 2.0)
    pix = page.get_pixmap(matrix=mat)

    # Convert PyMuPDF pixmap to OpenCV format
    img_data = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.height, pix.width, 3))
    img = cv2.cvtColor(img_data, cv2.COLOR_RGB2BGR)

    # Image Enhancement: Grayscale and Contrast (CLAHE)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # Encode to PNG bytes
    is_success, buffer = cv2.imencode(".png", enhanced)
    return buffer.tobytes()

def extract_json_payload(text):
    """Cleans the LLM response to extract a valid JSON object."""
    try:
        # Strip markdown and find the first '{' to last '}'
        clean_text = re.sub(r'```(?:json)?', '', text).replace('```', '').strip()
        match = re.search(r'(\{.*\})', clean_text, re.DOTALL)
        if match:
            json_str = match.group(1)
            # Fix trailing commas
            json_str = re.sub(r',\s*([\]}])', r'\1', json_str)
            return json.loads(json_str)
        return None
    except Exception as e:
        print(f"!!! JSON Parsing Error: {e}")
        return None

def run_extraction(pdf_path):
    client = boto3.client("bedrock-runtime", region_name=REGION)
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"❌ Error opening PDF: {e}")
        return

    combined_data = []

    # Iterate through the first 20 pages
    max_pages = min(20, len(doc))
    print(f"🚀 Starting extraction for {max_pages} pages...")

    for i in range(max_pages):
        print(f"📄 Processing Page {i+1} of {max_pages}...")
        try:
            page = doc.load_page(i)
            image_bytes = get_high_res_image_bytes(page)

            system_prompt = (
                "You are a high-precision OCR engine. Output ONLY raw JSON. "
                "Examine every digit after a decimal point with extreme care. "
                "Do not hallucinate or mix digits in the ADV or VP columns."
            )

            prompt = """Extract receipt details into this exact JSON structure:
            {
              "header": {"company": "string"},
              "body": [
                {
                  "Item No": "string", "UPC No": "string", "Manufacturer Name": "string", "Product Name": "string",
                  "Unit": "string", "Savings": "string", 
                  "ADV USD Special": "string", "ADV USD Regular": "string",
                  "VP2 USD Special": "string", "VP2 USD Regular":"string",
                  "VP1 USD Special": "string", "VP1 USD Regular":"string"
                }
              ]
            }
            Extraction Rules:
            1. Manufacturer Name: Look for the Brand/Company Name at the TOP LEFT of the label/block. Ignore 'Mfg:' codes.
            2. Product Name: Extract the full product description/title (e.g., 'HAMMER CURVED CLAW STL 16OZ'). It is usually located immediately BELOW the Manufacturer Name.
            3. Item No: Extract Item Number.
            4. UPC No: Extract EXACT digits including leading zeros.
            5. Pricing Table (Bottom Left):
               - Look for a table/grid with headers "ADV USD", "VP2 USD", "VP1 USD".
               - Under each header, there are two columns: "Special" and "Regular".
               - Extract ALL 6 values if visible.
               - Example Row: | 19.32 | 21.47 | 20.39 | 22.66 | 21.11 | 23.46 |
               - Ensure every price has a decimal point.
            """

            messages = [{
                "role": "user",
                "content": [
                    {"image": {"format": "png", "source": {"bytes": image_bytes}}},
                    {"text": prompt}
                ]
            }]

            response = client.converse(
                modelId=MODEL_ID,
                messages=messages,
                system=[{"text": system_prompt}],
                inferenceConfig={"temperature": 0.0} # Lower temperature = more precision
            )

            raw_text = response["output"]["message"]["content"][0]["text"]
            data = extract_json_payload(raw_text)

            if data and 'body' in data:
                df_page = pd.DataFrame(data['body'])
                df_page['Source_Page'] = i + 1
                combined_data.append(df_page)
        
        except Exception as e:
            print(f"⚠️ Error on page {i+1}: {e}")

    # Save to CSV
    if combined_data:
        final_df = pd.concat(combined_data, ignore_index=True)

        # Final cleanup for UPC column
        if 'UPC No' in final_df.columns:
            final_df['UPC No'] = final_df['UPC No'].astype(str).str.replace(" ", "")
            # Apply leading zero fix for Excel
            final_df['UPC No'] = final_df['UPC No'].apply(lambda x: f"\t{x}" if x and not x.startswith('\t') else x)

        # Cleanup Item No: Remove hyphens
        if 'Item No' in final_df.columns:
            final_df['Item No'] = final_df['Item No'].astype(str).str.replace("-", "")

        final_df.to_csv(OUTPUT_FILE, index=False)
        print(f"\n✅ SUCCESS: {len(final_df)} rows saved to {OUTPUT_FILE}")
    else:
        print("\n❌ No data was extracted. Check your file path or permissions.")

if __name__ == "__main__":
    # Remember to ask Akhilla for credentials and not to hardcode them!
    TARGET_PDF = r"C:\Users\BathulaEmmanuel-Shej\Downloads\input.pdf"
    
    # Check if file exists, if not try local
    import os
    if not os.path.exists(TARGET_PDF):
        local_pdf = "input.pdf"
        if os.path.exists(local_pdf):
             TARGET_PDF = local_pdf
             print(f"⚠️ Default path not found. Using local file: {TARGET_PDF}")

    run_extraction(TARGET_PDF)