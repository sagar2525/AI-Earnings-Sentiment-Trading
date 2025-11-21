import os
import json
import time
import random
import requests
from datetime import datetime
from pathlib import Path

# ---------- CONFIG ----------
API_URL = "https://www.nseindia.com/api/corporate-announcements?index=equities&reqXbrl=false&subject=Outcome%20of%20Board%20Meeting"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.nseindia.com/",
}
DOWNLOAD_DIR = "downloads"
TARGET_FILE = "tomorrow_result_list.json"
MEMORY_FILE = "downloaded_memory.json"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


# ---------- UTILITIES ----------
def load_target_list():
    """Load list of Nifty500 companies announcing results today."""
    if not os.path.exists(TARGET_FILE):
        print(f"[ERROR] {TARGET_FILE} not found. Run nifty500_result_today.py first.")
        return set()
    with open(TARGET_FILE, "r", encoding="utf-8") as f:
        return set(json.load(f))


def load_memory():
    """Load previously downloaded symbols memory."""
    if not os.path.exists(MEMORY_FILE):
        return set()
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except Exception:
        return set()


def save_memory(memory):
    """Save updated memory to disk."""
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(list(memory), f, indent=2)


def fetch_latest_filings(limit=5):
    """Fetch only the latest few NSE filings."""
    try:
        resp = requests.get(API_URL, headers=HEADERS, timeout=20)
        if resp.status_code != 200:
            print(f"[WARN] NSE API returned {resp.status_code}")
            return []
        data = resp.json()
        return data[:limit] if isinstance(data, list) else []
    except Exception as e:
        print(f"[ERROR] Failed to fetch NSE API: {e}")
        return []


def download_pdf(url, symbol):
    """Download PDF for given symbol."""
    filename = f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    path = Path(DOWNLOAD_DIR) / filename
    try:
        r = requests.get(url, headers=HEADERS, stream=True, timeout=30)
        if r.status_code == 200 and "application/pdf" in r.headers.get("content-type", "").lower():
            with open(path, "wb") as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
            print(f"[✅ PDF SAVED] {filename}")
            return True
    except Exception as e:
        print(f"[ERROR] PDF download failed for {symbol}: {e}")
    return False


# ---------- MAIN ----------
def main():
    target_symbols = load_target_list()
    if not target_symbols:
        print("[INFO] No target companies loaded. Exiting.")
        return

    memory = load_memory()
    print(f"[INFO] Loaded {len(target_symbols)} target companies for today.")
    print(f"[INFO] Already downloaded companies: {len(memory)}\n")

    while True:
        print(f"[INFO] Checking NSE filings at {datetime.now().strftime('%H:%M:%S')}...")
        filings = fetch_latest_filings(limit=5)

        if filings:
            for item in filings:
                symbol = str(item.get("symbol", "")).upper().strip()
                pdf_url = item.get("attchmntFile")

                if not symbol or symbol not in target_symbols or not pdf_url:
                    continue

                if symbol in memory:
                    # already downloaded, skip silently
                    continue

                print(f"[MATCH] {symbol} → Downloading new result PDF...")
                if download_pdf(pdf_url, symbol):
                    memory.add(symbol)
                    save_memory(memory)
        else:
            print("[WARN] No data received from NSE.")

        sleep_time = random.randint(30, 40)
        print(f"[INFO] Sleeping {sleep_time}s before next check...\n")
        time.sleep(sleep_time)


if __name__ == "__main__":
    main()
