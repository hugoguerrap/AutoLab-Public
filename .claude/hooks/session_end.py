#!/usr/bin/env python3
"""autolab SessionEnd hook — logs session duration.
Cross-platform: works on Windows, macOS, and Linux.
"""
import os
import re
from datetime import datetime
from pathlib import Path

PROJECT_DIR = Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")).resolve()
JOURNAL = PROJECT_DIR / "lab" / "journal.md"

now = datetime.now()
now_str = now.strftime("%Y-%m-%d %H:%M:%S")

duration_str = ""
if JOURNAL.exists():
    lines = JOURNAL.read_text(encoding="utf-8").splitlines()
    # Find last SESSION_START
    starts = [l for l in lines if "SESSION_START" in l]
    if starts:
        match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", starts[-1])
        if match:
            try:
                start_time = datetime.strptime(match.group(1), "%Y-%m-%d %H:%M:%S")
                minutes = int((now - start_time).total_seconds() / 60)
                duration_str = f" | duration={minutes}m"
            except ValueError:
                pass

JOURNAL.parent.mkdir(parents=True, exist_ok=True)
with open(JOURNAL, "a", encoding="utf-8") as f:
    f.write(f"[{now_str}] SESSION_END{duration_str}\n")
