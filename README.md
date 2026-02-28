# Multimodal Invoice Extraction System


### High-Precision Multimodal Invoice Data Extraction using AWS Bedrock + LLM

---

## 📌 Project Overview

The **Invoice Extractor** is an AI-powered intelligent document processing system developed during my 3-month internship at **She-Jobs Tech Company**.

This project leverages:

* AWS Bedrock (Multimodal LLM)
* Computer Vision preprocessing
* High-resolution PDF rendering
* Prompt engineering
* Structured JSON validation
* Data cleaning & transformation
* CSV export pipeline

The system extracts structured pricing and product data from complex invoice/receipt PDFs with high numerical precision — especially focusing on decimal-sensitive pricing columns.

---

## 🧠 Problem Statement

Traditional OCR systems struggle with:

* Decimal precision errors (19.32 → 19.82)
* Digit mixing in pricing columns
* Misreading UPC codes with leading zeros
* Complex tabular extraction
* Low-resolution PDF rendering
* Inconsistent JSON formatting from LLM outputs

This system was built to solve those limitations using **LLM + Computer Vision hybrid architecture**.

---

## 🏗 System Architecture

```
PDF Input
   ↓
High-Resolution Rendering (PyMuPDF 2x Zoom)
   ↓
Image Enhancement (OpenCV + CLAHE)
   ↓
AWS Bedrock Multimodal LLM
   ↓
Strict JSON Extraction
   ↓
Regex Cleanup & Validation
   ↓
DataFrame Processing
   ↓
CSV Output
```

---

## 🔧 Tech Stack

| Category         | Technology           |
| ---------------- | -------------------- |
| Cloud            | AWS Bedrock          |
| LLM Model        | Llama 3 90B Instruct |
| SDK              | boto3                |
| PDF Processing   | PyMuPDF (fitz)       |
| Image Processing | OpenCV               |
| Array Processing | NumPy                |
| Data Handling    | Pandas               |
| Regex Validation | Python re            |

---

## 🤖 LLM & Cloud Integration

### Model Used

`us.meta.llama3-2-90b-instruct-v1:0`

### Region

`us-east-2`

### Why This Model?

* Multimodal (Image + Text support)
* High reasoning capability
* Deterministic output with temperature=0
* Strong structured extraction capabilities

### Bedrock Inference Strategy

* Temperature set to **0.0** (for precision)
* Strict system prompt to prevent hallucination
* Enforced JSON-only output
* Decimal-sensitive instructions
* Column-specific extraction rules

---

## 🖼 Image Processing Optimization

### 🔍 2x Resolution Rendering

Using:

```python
mat = fitz.Matrix(2.0, 2.0)
```

This improves small-text OCR accuracy significantly (approx 300+ DPI equivalent).

### 🧪 CLAHE Contrast Enhancement

Applied:

* Grayscale conversion
* Contrast Limited Adaptive Histogram Equalization (CLAHE)

This prevents:

* Digit bleeding
* Decimal misreading
* Low contrast errors

---

## 📊 Extracted JSON Schema

```json
{
  "header": {"company": "string"},
  "body": [
    {
      "Item No": "string",
      "UPC No": "string",
      "Manufacturer Name": "string",
      "Product Name": "string",
      "Unit": "string",
      "Savings": "string",
      "ADV USD Special": "string",
      "ADV USD Regular": "string",
      "VP2 USD Special": "string",
      "VP2 USD Regular": "string",
      "VP1 USD Special": "string",
      "VP1 USD Regular": "string"
    }
  ]
}
```

---

## 🛡 Precision Control Techniques

### 1️⃣ Decimal Protection

Explicit prompt instruction:

> “Examine every digit after a decimal point with extreme care.”

### 2️⃣ Temperature = 0

Removes randomness and hallucination.

### 3️⃣ Regex-Based JSON Cleaning

* Markdown removal
* Trailing comma fix
* Structured extraction validation

### 4️⃣ UPC Leading Zero Fix

Excel-safe formatting:

```python
final_df['UPC No'] = final_df['UPC No'].apply(lambda x: f"\t{x}")
```

### 5️⃣ Item Number Cleanup

Hyphen normalization for downstream systems.

---

## 📈 Production-Grade Features

✅ Multi-page PDF support (up to 20 pages)
✅ Per-page extraction tracking
✅ Structured DataFrame merging
✅ Fault tolerance (try/except page-level handling)
✅ Credential safety reminder (no hardcoding)
✅ CSV export ready for BI tools

---

## ⚙️ Execution Flow

```bash
python invoice_extractor.py
```

If default path not found:

* Automatically switches to local directory fallback

Output:

```
Extracted_PDF_Data.csv
```

---

## 🎯 Key Achievements During Internship

* Designed a multimodal AI extraction pipeline from scratch
* Integrated AWS Bedrock production inference
* Engineered precision-focused prompts for financial data
* Solved decimal hallucination issues
* Built scalable multi-page extraction logic
* Implemented advanced image enhancement for OCR accuracy
* Delivered structured CSV output usable by finance teams

---

## 🧠 Skills Demonstrated

### AI / LLM Engineering

* Prompt Engineering
* Hallucination Control
* Multimodal Inference
* Deterministic LLM Configuration

### Computer Vision

* DPI scaling
* Image enhancement
* CLAHE application

### Data Engineering

* Structured JSON validation
* Regex sanitation
* Pandas transformation pipeline
* CSV export optimization

### Cloud & Backend

* AWS Bedrock
* boto3 runtime invocation
* Regional inference optimization

---

## 🚀 Real-World Impact

This system enables:

* Automated invoice processing
* Financial price validation
* Bulk catalog extraction
* Supply-chain data digitization
* Reduced manual data entry time

---

## 🔒 Security Considerations

* No credentials hardcoded
* Uses AWS environment authentication
* Safe error handling
* Controlled inference temperature

---

## 🏁 Future Improvements

* Add async page processing for speed
* Add confidence scoring
* Add validation rules for price consistency
* Deploy as API endpoint (FastAPI)
* Integrate database storage
* Add dashboard UI

---

## 👨‍💻 Developed By

**EMMANUEL AI Intern – She-Jobs Tech Company**
Specialization: AI Systems | LLM Engineering | Intelligent Automation

---

# ⭐ Final Summary

This project demonstrates:

* Advanced AI engineering
* Real-world financial data extraction
* Production-aware cloud integration
* Computer vision + LLM hybrid architecture
* Strong debugging and precision mindset


# SCREENSHOTS

# code
<img width="959" height="563" alt="image" src="https://github.com/user-attachments/assets/e12ca4f3-747d-4946-9536-59e9c62d540d" />

## image from the pdf which was used to extraction

<img width="443" height="466" alt="Image" src="https://github.com/user-attachments/assets/41841e02-c3df-4310-ada3-bba5ad69f56b" />

## output csv

<img width="957" height="485" alt="image" src="https://github.com/user-attachments/assets/4b3a3fab-0ae9-4eab-ac83-f4b10c3cb594" />
