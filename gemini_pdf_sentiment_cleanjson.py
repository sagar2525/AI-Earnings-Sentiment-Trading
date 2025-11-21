import os
import json
import re
import time
import requests
from pathlib import Path
from datetime import datetime
import google.generativeai as genai
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ========== CONFIGURATION ==========
DOWNLOAD_DIR = "downloads"
OUTPUT_DIR = "parsed_results"
PROCESSED_FILE = "processed_companies.json"
MODEL_NAME = "gemini-2.5-flash-lite"  # or "gemini-1.5-flash" for faster performance
API_KEY = ""

# 🚀 Flask Order Execution Server Endpoint (change this URL if running remotely)
ORDER_SERVER_URL = "http://127.0.0.1:5000/receive_data"

# ========== SETUP ==========
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel(MODEL_NAME)
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ========== UTILS ==========
def load_processed_companies():
    """Load processed company list from file."""
    if Path(PROCESSED_FILE).exists():
        try:
            with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()


def save_processed_companies(companies):
    """Save processed companies to file."""
    with open(PROCESSED_FILE, "w", encoding="utf-8") as f:
        json.dump(list(companies), f, indent=2)


def extract_json_from_text(text):
    """Clean and extract JSON from Gemini response."""
    cleaned = re.sub(r"```(?:json)?", "", text, flags=re.IGNORECASE).strip()
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    try:
        return json.loads(cleaned)
    except Exception:
        return {"raw_response": text}


# ========== GEMINI FUNCTION ==========
def extract_financial_data_from_pdf(pdf_path):
    print(f"\n[INFO] Sending {pdf_path.name} to Gemini for analysis...")

    prompt = """
    You are a financial analyst AI.
    Read the attached quarterly financial results PDF of an Indian listed company.

    Output ONLY valid JSON — no markdown, text, or explanations.

    Include fields:
      - Company name
      - Ticker (from filename or PDF header)
      - Quarter / Period
      - Revenue/Sales
      - Operating Profit/EBIT
      - EBITDA
      - Net Profit (PAT)
      - Earnings Per Share (EPS)
      - Gross Profit Margin
      - Operating Margin
      - Net Profit Margin
      - Cash Flow from Operations (CFO)
      - Free Cash Flow (FCF)
      - Debt-to-Equity Ratio
      - Working Capital
      - QoQ and YoY % changes for Revenue and PAT
      - Sentiment ("Strong Bullish", "Bullish", "Neutral", "Bearish", "Strong Bearish")

    Return example:
    {
      "Company": "Example Ltd",
      "Ticker": "EXAMPL",
      "Quarter": "Q2 FY2025",
      "Revenue/Sales": 12345.67,
      "EBITDA": 2345.89,
      "Net Profit (PAT)": 678.90,
      "Earnings Per Share (EPS)": 4.23,
      "QoQ_Revenue_Change_%": 5.6,
      "QoQ_PAT_Change_%": 7.8,
      "YoY_Revenue_Change_%": 14.3,
      "YoY_PAT_Change_%": 12.7,
      "Sentiment": "Bullish"
    }
    """

    try:
        file_ref = genai.upload_file(pdf_path)
        response = model.generate_content([prompt, file_ref], request_options={"timeout": 300})
        data = extract_json_from_text(response.text)

        # Add ticker from filename if missing
        ticker = pdf_path.stem.split("_")[0]
        if "Ticker" not in data or not data["Ticker"]:
            data["Ticker"] = ticker

        # Add company name fallback if missing
        if "Company" not in data or not data["Company"]:
            data["Company"] = ticker

        return data

    except Exception as e:
        print(f"[ERROR] Gemini API error: {e}")
        return None


# ========== SEND TO ORDER SERVER ==========
def send_to_order_server(data):
    """Send parsed financial data JSON to Flask order execution server."""
    try:
        response = requests.post(ORDER_SERVER_URL, json=data, timeout=10)
        if response.status_code == 200:
            print(f"[INFO] ✅ Data successfully sent to order server.")
        else:
            print(f"[WARN] ⚠️ Server responded with {response.status_code}: {response.text}")
    except Exception as e:
        print(f"[ERROR] ❌ Failed to send data to order server: {e}")


# ========== SAVE RESULT ==========
def save_result_json(data, pdf_path):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    symbol = pdf_path.stem.split("_")[0]
    json_path = Path(OUTPUT_DIR) / f"{symbol}_{timestamp}.json"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"[INFO] 💾 Saved clean JSON → {json_path}")

    # NEW: Send parsed data to Flask order execution system
    send_to_order_server(data)
    print(f"[INFO] 🚀 Sent parsed data of {symbol} to order execution system.\n")


# ========== WATCHDOG HANDLER ==========
class PDFHandler(FileSystemEventHandler):
    def __init__(self, processed):
        super().__init__()
        self.processed = processed

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".pdf"):
            pdf_path = Path(event.src_path)
            company_name = pdf_path.stem.split("_")[0].upper()

            # Skip duplicate company PDFs
            if company_name in self.processed:
                print(f"[SKIP] Duplicate company detected → {company_name}")
                return

            print(f"\n[NEW FILE DETECTED] {pdf_path.name}")
            time.sleep(3)  # ensure file is fully written

            data = extract_financial_data_from_pdf(pdf_path)
            if data:
                save_result_json(data, pdf_path)
                self.processed.add(company_name)
                save_processed_companies(self.processed)


# ========== MAIN ==========
def main():
    print(f"[INFO] 👀 Watching folder: {DOWNLOAD_DIR}")
    processed = load_processed_companies()
    print(f"[INFO] Loaded {len(processed)} previously processed companies.")

    event_handler = PDFHandler(processed)
    observer = Observer()
    observer.schedule(event_handler, DOWNLOAD_DIR, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        observer.stop()
        print("\n[INFO] 🛑 Stopped watching.")
    observer.join()


if __name__ == "__main__":
    main()

