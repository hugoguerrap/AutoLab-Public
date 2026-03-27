#!/usr/bin/env python3
"""autolab SessionStart hook — injects lab state into new sessions.
Cross-platform: works on Windows, macOS, and Linux.
"""
import json
import os
from datetime import datetime
from pathlib import Path

PROJECT_DIR = Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")).resolve()
JOURNAL = PROJECT_DIR / "lab" / "journal.md"
SCOREBOARD = PROJECT_DIR / "lab" / "scoreboard.md"
EXPERIMENTS_DIR = PROJECT_DIR / "experiments"

context_parts = []


def tail_lines(filepath: Path, n: int = 15) -> list[str]:
    if not filepath.exists():
        return []
    lines = filepath.read_text(encoding="utf-8").splitlines()
    return [l for l in lines if l.startswith("[")][-n:]


# Experiment status
if EXPERIMENTS_DIR.exists():
    experiments = []
    for exp_dir in sorted(EXPERIMENTS_DIR.iterdir()):
        if not exp_dir.is_dir() or exp_dir.name.startswith("."):
            continue
        results_file = exp_dir / "results.tsv"
        iterations = 0
        if results_file.exists():
            lines = results_file.read_text(encoding="utf-8").splitlines()
            iterations = max(len(lines) - 1, 0)  # subtract header
        status = "complete" if iterations > 0 else "pending"
        experiments.append(f"  {exp_dir.name}: {iterations} iterations ({status})")

    if experiments:
        context_parts.append("## Experiments\n" + "\n".join(experiments))

# Recent journal entries
journal_lines = tail_lines(JOURNAL, 15)
if journal_lines:
    context_parts.append("## Recent Lab Activity\n" + "\n".join(journal_lines))

# Scoreboard
if SCOREBOARD.exists():
    scores = SCOREBOARD.read_text(encoding="utf-8").strip()
    if scores.count("\n") > 2:
        context_parts.append(f"## Scoreboard\n{scores}")

# Log session start
JOURNAL.parent.mkdir(parents=True, exist_ok=True)
with open(JOURNAL, "a", encoding="utf-8") as f:
    f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SESSION_START\n")

# Output for Claude Code
full_context = "\n\n".join(context_parts)
print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": full_context
    }
}))
