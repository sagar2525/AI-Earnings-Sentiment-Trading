import os
import time
from datetime import datetime, timedelta
from pathlib import Path

DOWNLOAD_DIR = Path("downloads")
RESULT_DIR = Path("parsed_results")
DAYS = 7  # retention period

def delete_old_files(folder: Path):
    if not folder.exists():
        return
    cutoff = time.time() - (DAYS * 86400)
    deleted = 0
    for f in folder.glob("*"):
        if f.is_file() and f.stat().st_mtime < cutoff:
            try:
                f.unlink()
                deleted += 1
            except Exception as e:
                print(f"[WARN] Failed to delete {f.name}: {e}")
    if deleted:
        print(f"[CLEANUP] Deleted {deleted} old files from {folder.name}.")


if __name__ == "__main__":
    print(f"[INFO] Running cleanup for files older than {DAYS} days...")
    delete_old_files(DOWNLOAD_DIR)
    delete_old_files(RESULT_DIR)
