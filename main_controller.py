import subprocess
import time
import threading
import os

def run_script(script):
    return subprocess.Popen(["python", script])

def cleanup_task():
    while True:
        # run cleanup once every 24 hours
        os.system("python cleanup_old_files.py")
        time.sleep(24 * 3600)

if __name__ == "__main__":
    print("[INFO] Starting NSE automation container...")

    # Start main scripts
    processes = [
        run_script("nse_event_calendar_scheduler_22.py"),
        run_script("nse_filtered_downloader_memory.py"),
        run_script("gemini_pdf_sentiment_cleanjson.py")
    ]

    # Start cleanup thread
    threading.Thread(target=cleanup_task, daemon=True).start()

    try:
        for p in processes:
            p.wait()
    except KeyboardInterrupt:
        print("\n[INFO] Stopping all processes...")
        for p in processes:
            p.terminate()
