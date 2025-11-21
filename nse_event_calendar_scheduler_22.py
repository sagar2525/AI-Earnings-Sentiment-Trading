# nse_event_calendar_scheduler_22.py
from curl_cffi import requests
import json
import pandas as pd
import time
import random
from datetime import datetime, timedelta, time as dtime
from zoneinfo import ZoneInfo

# =============================
# CONFIGURATION
# =============================
HOMEPAGE = "https://www.nseindia.com/"
EVENT_API = "https://www.nseindia.com/api/event-calendar?type=equities"
NIFTY500_FILE = "ind_nifty500list.csv"
OUTPUT_FILE = "tomorrow_result_list.json"

# Set scheduler timezone to Asia/Kolkata explicitly
TZ = ZoneInfo("Asia/Kolkata")
SCHEDULE_HOUR = 22  # 10 PM
SCHEDULE_MINUTE = 0

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/119.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
    "Connection": "keep-alive",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}

# =============================
# HELPERS
# =============================
def init_session():
    session = requests.Session(impersonate="chrome124")
    session.headers.update(HEADERS)
    try:
        session.get(HOMEPAGE, timeout=20)
    except Exception:
        # ignore occasional homepage fetch errors, we'll retry when calling API
        pass
    return session


def fetch_event_calendar(session):
    retries = 0
    while True:
        try:
            retries += 1
            resp = session.get(EVENT_API, timeout=30)
            if resp.status_code != 200:
                print(f"[WARN] NSE returned {resp.status_code} (attempt {retries}) — retrying...")
                time.sleep(random.uniform(5, 10))
                continue

            data = resp.json()
            if isinstance(data, dict) and "data" in data:
                data = data["data"]

            if not isinstance(data, list):
                print(f"[WARN] Unexpected JSON format (attempt {retries}) — retrying...")
                time.sleep(random.uniform(5, 10))
                continue

            return data
        except Exception as e:
            print(f"[ERROR] Fetch attempt {retries} failed: {e} — retrying in 5-10s...")
            time.sleep(random.uniform(5, 10))


def load_nifty500_symbols():
    df = pd.read_csv(NIFTY500_FILE)
    sym_col = next((c for c in df.columns if "symbol" in c.lower()), None)
    if not sym_col:
        raise ValueError("Nifty 500 CSV must contain a 'Symbol' column")
    return set(df[sym_col].astype(str).str.strip().str.upper())


def filter_tomorrows_symbols(events):
    tomorrow = (datetime.now(TZ) + timedelta(days=1)).strftime("%d-%b-%Y")
    nifty500 = load_nifty500_symbols()
    result_keywords = ["result", "financial", "quarter", "earning"]

    symbols = set()
    for e in events:
        symbol = str(e.get("symbol", "")).strip().upper()
        event_date = str(e.get("date", "")).strip()
        purpose = str(e.get("purpose", "")).lower()

        if not symbol or not event_date:
            continue
        if event_date.lower() == tomorrow.lower() and symbol in nifty500:
            if any(k in purpose for k in result_keywords):
                symbols.add(symbol)

    return sorted(symbols)


def save_symbols(symbol_list):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(symbol_list, f, indent=2, ensure_ascii=False)


def seconds_until_next_run(hour: int, minute: int, tz: ZoneInfo):
    now = datetime.now(tz)
    today_target = datetime.combine(now.date(), dtime(hour, minute, 0, tzinfo=tz))
    if now < today_target:
        delta = (today_target - now).total_seconds()
    else:
        # schedule for next day
        next_target = today_target + timedelta(days=1)
        delta = (next_target - now).total_seconds()
    return max(0, int(delta))


# =============================
# MAIN SCHEDULE LOOP
# =============================
def run_once_and_save(session=None):
    if session is None:
        session = init_session()
    print(f"[{datetime.now(TZ).strftime('%Y-%m-%d %H:%M:%S %Z')}] Starting fetch...")
    events = fetch_event_calendar(session)
    print(f"[INFO] Received {len(events)} entries from NSE.")
    symbols = filter_tomorrows_symbols(events)
    save_symbols(symbols)
    print(f"[INFO] Found {len(symbols)} symbols for tomorrow — saved to {OUTPUT_FILE}")


def main():
    print("[INFO] Scheduler started — will run daily at {:02d}:{:02d} IST".format(SCHEDULE_HOUR, SCHEDULE_MINUTE))
    session = init_session()

    while True:
        secs = seconds_until_next_run(SCHEDULE_HOUR, SCHEDULE_MINUTE, TZ)
        hrs = secs // 3600
        mins = (secs % 3600) // 60
        print(f"[SLEEP] Sleeping {hrs}h {mins}m until next scheduled run at "
              f"{SCHEDULE_HOUR:02d}:{SCHEDULE_MINUTE:02d} IST")
        time.sleep(secs)

        try:
            run_once_and_save(session=session)
        except Exception as e:
            # if something fails, print and keep the loop; next iteration will attempt again tomorrow
            print(f"[ERROR] Scheduled run failed: {e}")

        # small random delay before calculating next sleep to avoid tight alignment issues
        time.sleep(random.uniform(1, 3))


if __name__ == "__main__":
    main()
